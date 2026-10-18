from copy import deepcopy
import unittest
from scripts import stock_price_map as prices, research_consistency as audit
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_audit_fixture import audit_for


def sample():
    return dict(meta=dict(code='600066.SH', name='offline', valuation_date='2026-10-18',
                         currency='CNY', generator='codex', report_path='research/example.md'),
                mode='buy_candidate', reason=None,
                valuation=dict(kind='per_share', values=dict(low=20, base=24, high=30),
                               currency='CNY', unit='per_share', fx_to_quote=1),
                p1=dict(base=12), t1=dict(price_condition='股价≥30元/股'),
                research_controls=dict(entry=dict(status='eligible', refs=[]),
                                       add=dict(status='eligible', refs=[]),
                                       holding=dict(status='normal', refs=[])),
                monitoring=[dict(id='income', kind='general', state='watching', variable='income',
                    current=None, as_of=None, trigger='falls', action='review', source='offline', next_check='next report')])


class TwoPriceContractTests(unittest.TestCase):
    def test_default_writer_only_two_prices_and_no_quote_reconstruction(self):
        value = sample()
        doc = prices.build_document(value)
        self.assertEqual(doc['meta']['schema_version'], 'stock-research/v4')
        self.assertEqual(set(doc['price_map']), {'mode', 'reason', 'v50', 'p1', 't1'})
        self.assertEqual(doc['price_map']['p1'], {'base': 12})
        for key in ('p2', 't2'):
            bad = deepcopy(value); bad[key] = None
            with self.assertRaises(ValueError): prices.build_document(bad)
        bad = deepcopy(value); bad['t1']['events'] = ['must migrate']
        with self.assertRaises(ValueError): prices.build_document(bad)

    def test_unknown_missing_refs_and_unpriced_do_not_grant_eligibility(self):
        for mutation in ('missing', 'unknown', 'frozen', 'holding'):
            value = sample()
            if mutation == 'missing': del value['research_controls']
            elif mutation == 'unknown': value['research_controls']['add']['status'] = 'unknown'
            elif mutation == 'frozen': value.update(mode='frozen', reason='blocked')
            else: value['research_controls']['holding'] = dict(status='invalidated', refs=['failure'])
            with self.assertRaises(ValueError): prices.build_document(value)

    def test_only_add_constraint_preserves_entry_and_must_resolve_audit_refs(self):
        value = sample(); value['research_controls']['add'] = dict(status='blocked', refs=['ADD'])
        doc = prices.build_document(value)
        check = audit_for(doc)
        check['constraints'] = [dict(id='ADD', scope=['add'], status='blocking', action='eligibility',
            reason='additional evidence required', release_conditions=['verified report'])]
        check['release_all_of'] = dict(entry=[], add=['ADD'], holding=[])
        audit.validate_audit(check, doc)
        bad = deepcopy(check); bad['release_all_of']['entry'] = ['ADD']
        with self.assertRaises(ValueError): audit.validate_audit(bad, doc)
        bad = deepcopy(doc); bad['research_controls']['add'] = dict(status='eligible', refs=[])
        with self.assertRaises(ValueError): audit.validate_audit(check, bad)

    def test_unknown_holding_is_review_not_confirmed_failure(self):
        value = sample(); value['research_controls']['holding'] = dict(status='review_required', refs=['H'])
        doc = prices.build_document(value); check = audit_for(doc)
        check['constraints'] = [dict(id='H', scope=['holding'], status='unknown', action='invalidated',
            reason='not established', release_conditions=['evidence'])]
        check['release_all_of'] = dict(entry=[], add=[], holding=['H'])
        audit.validate_audit(check, doc)
        bad = deepcopy(doc); bad['research_controls']['holding']['status'] = 'exit_required'
        with self.assertRaises(ValueError): audit.validate_audit(check, bad)

    def test_cleared_requires_evidence_and_watching_is_not_blocking(self):
        value = sample(); value['monitoring'][0].update(id='A', kind='add_constraint', state='cleared')
        doc = prices.build_document(value); check = audit_for(doc)
        check['constraints'] = [dict(id='A', scope=['add'], status='clear', action='eligibility',
            reason='reviewed', release_conditions=[])]
        with self.assertRaises(ValueError): audit.validate_audit(check, doc)
        check['constraints'][0]['clearance'] = dict(evidence=['report section 3'])
        audit.validate_audit(check, doc)
        bad = deepcopy(doc); bad['monitoring'][0]['state'] = 'triggered'
        with self.assertRaises(ValueError): audit.validate_audit(check, bad)

    def test_missing_or_inverted_prices_never_get_repaired(self):
        value = sample(); value['t1']['price_condition'] = '股价≥10元/股'
        doc = prices.build_document(value)
        self.assertEqual(doc['price_map']['p1']['base'], 12)
        self.assertEqual(doc['price_map']['t1']['price_condition'], '股价≥10元/股')
        # Research quotes survive; downstream stops an invalid buy coordinate.
        value['p1'] = None
        with self.assertRaises(ValueError): prices.build_document(value)

class TwoPriceContinuityTests(unittest.TestCase):
    def test_tracking_cannot_grant_add_permission(self):
        for mode in ('tracking', 'observation'):
            value=sample(); value.update(mode=mode, reason='not qualified')
            value['research_controls']['entry']=dict(status='unknown',refs=['MISSING'])
            with self.assertRaises(ValueError): prices.build_document(value)

    def test_baseline_unresolved_constraint_cannot_disappear_or_lose_scope(self):
        import hashlib, json, tempfile
        from pathlib import Path
        value=sample(); value['research_controls']['add']=dict(status='blocked',refs=['ADD'])
        old_doc=prices.build_document(value); prior=audit_for(old_doc)
        prior['constraints']=[dict(id='ADD',scope=['add'],status='blocking',action='eligibility',reason='pending',release_conditions=['evidence'])]
        prior['release_all_of']=dict(entry=[],add=['ADD'],holding=[])
        raw=audit.render_report_block(prior,old_doc).encode()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'baseline.md').write_bytes(raw)
            doc=prices.build_document(sample()); current=audit_for(doc)
            current['baseline']=dict(report_path='baseline.md',sha256=hashlib.sha256(raw).hexdigest(),
                discounts={k:dict(value=v['value'],quote='explicit offline assumption') for k,v in prior['discounts'].items()})
            for row in current['discounts'].values(): row['change']['kind']='unchanged'
            with self.assertRaisesRegex(ValueError,'omitted'): audit.validate_audit(current,doc,root=root)
            current['constraints']=[dict(prior['constraints'][0],status='not_applicable',release_conditions=[])]
            with self.assertRaisesRegex(ValueError,'release requires evidence'): audit.validate_audit(current,doc,root=root)
            current['constraints'][0]['clearance']=dict(evidence=['new evidence section 2'])
            audit.validate_audit(current,doc,root=root)

    def test_confirmed_exit_blocks_both_scopes_but_is_not_execution(self):
        value=sample();value.update(mode='frozen',reason='logic failed')
        value['research_controls']=dict(entry=dict(status='blocked',refs=['EXIT','FREEZE']),add=dict(status='blocked',refs=['EXIT','FREEZE']),holding=dict(status='exit_required',refs=['EXIT']))
        doc=prices.build_document(value);check=audit_for(doc)
        check['constraints']=[dict(id='EXIT',scope=['entry','add','holding'],status='blocking',action='exit_required',reason='confirmed',release_conditions=['new thesis']),
            dict(id='FREEZE',scope=['entry','add'],status='blocking',action='freeze',reason='stop exposure',release_conditions=['review'])]
        check['release_all_of']=dict(entry=['EXIT','FREEZE'],add=['EXIT','FREEZE'],holding=['EXIT'])
        audit.validate_audit(check,doc)
        self.assertNotIn('executed',str(doc))
        bad=deepcopy(check);bad['constraints'][0]['status']='unknown'
        with self.assertRaises(ValueError):audit.validate_audit(bad,doc)

class ConfirmedHoldingContinuityTests(unittest.TestCase):
    def test_confirmed_exit_cannot_become_unknown_without_explicit_clearance(self):
        import hashlib,tempfile
        value=sample();value.update(mode='frozen',reason='confirmed risk')
        value['research_controls']=dict(entry=dict(status='blocked',refs=['F','X']),add=dict(status='blocked',refs=['F','X']),holding=dict(status='exit_required',refs=['X']))
        doc=prices.build_document(value);prior=audit_for(doc)
        prior['constraints']=[dict(id='F',scope=['entry','add'],status='blocking',action='freeze',reason='stop exposure',release_conditions=['review']),
            dict(id='X',scope=['entry','add','holding'],status='blocking',action='exit_required',reason='confirmed risk',release_conditions=['new evidence'])]
        prior['release_all_of']=dict(entry=['F','X'],add=['F','X'],holding=['X'])
        raw=audit.render_report_block(prior,doc).encode()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'prior.md').write_bytes(raw)
            current=deepcopy(prior)
            current['baseline']=dict(report_path='prior.md',sha256=hashlib.sha256(raw).hexdigest(),discounts={k:dict(value=v['value'],quote='explicit offline assumption') for k,v in prior['discounts'].items()})
            for row in current['discounts'].values():row['change']['kind']='unchanged'
            current['constraints'][1]['status']='unknown'
            doc['research_controls']['holding']['status']='review_required'
            with self.assertRaisesRegex(ValueError,'explicitly cleared before downgrade'):
                audit.validate_audit(current,doc,root=root)

class D5ContinuityTests(unittest.TestCase):
    def test_not_applicable_cannot_bypass_prior_d5_rebuilding_review(self):
        import hashlib, tempfile
        value=sample(); value.update(mode='frozen',reason='D5 pending')
        value['research_controls']['entry']=dict(status='blocked',refs=['D5'])
        value['research_controls']['add']=dict(status='blocked',refs=['D5'])
        old_doc=prices.build_document(value); prior=audit_for(old_doc)
        prior['constraints']=[dict(id='D5',scope=['entry','add'],status='blocking',action='freeze',
            reason='waiting review',release_conditions=['rebuild and company review'],
            clearance=dict(stage='waiting_review',evidence=['R21 exit observed']))]
        prior['release_all_of']=dict(entry=['D5'],add=['D5'],holding=[])
        raw=audit.render_report_block(prior,old_doc).encode()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'prior.md').write_bytes(raw)
            doc=prices.build_document(sample()); current=audit_for(doc)
            current['baseline']=dict(report_path='prior.md',sha256=hashlib.sha256(raw).hexdigest(),
                discounts={k:dict(value=v['value'],quote='explicit offline assumption') for k,v in prior['discounts'].items()})
            for row in current['discounts'].values(): row['change']['kind']='unchanged'
            current['constraints']=[dict(prior['constraints'][0],status='not_applicable',release_conditions=[])]
            with self.assertRaisesRegex(ValueError,'D5.*rebuilding'):
                audit.validate_audit(current,doc,root=root)
            current['constraints'][0]['clearance']=dict(stage='rebuild_review_complete',evidence=['completed rebuilding and company review'])
            audit.validate_audit(current,doc,root=root)

class RestrictionActionContinuityTests(unittest.TestCase):
    def restricted_pair(self, action, status='blocking', *, legacy=False):
        value = sample()
        value['research_controls']['entry'] = dict(status='blocked' if status == 'blocking' else 'unknown', refs=['RISK'])
        value['research_controls']['add'] = deepcopy(value['research_controls']['entry'])
        if action in {'freeze', 'reject', 'unavailable'}:
            value.update(mode={'freeze': 'frozen', 'reject': 'rejected' if status == 'blocking' else 'frozen',
                               'unavailable': 'unavailable'}[action], reason='unresolved risk')
        if value['mode'] in {'rejected', 'unavailable'}:
            value['p1'] = None
        doc = prices.build_document(value)
        check = audit_for(doc)
        check['constraints'] = [dict(id='RISK', scope=['entry', 'add'], status=status, action=action,
                                    reason='unresolved risk', release_conditions=['new original evidence'])]
        check['release_all_of'] = dict(entry=['RISK'], add=['RISK'], holding=[])
        if legacy:
            doc.pop('research_controls')
            doc['meta']['schema_version'] = 'stock-research/v3'
            doc['price_map']['p2'] = dict(status='cancelled', reason='offline', price=None)
            doc['price_map']['t1']['events'] = ['review']
            doc['price_map']['t2'] = dict(price_condition='待核', events=['review'])
            doc['monitoring'] = [{k: v for k, v in row.items() if k not in {'id', 'kind', 'state'}}
                                 for row in doc['monitoring']]
            check['schema_version'] = 'stock-research-audit/v1'
            check['constraints'][0]['effect'] = check['constraints'][0].pop('action')
            check['constraints'][0].pop('scope')
            check['release_all_of'] = ['RISK']
        audit.validate_audit(check, doc)
        return check, doc

    def with_baseline(self, prior, old_doc, current, callback):
        import hashlib, tempfile
        raw = audit.render_report_block(prior, old_doc).encode()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'prior.md').write_bytes(raw)
            current['baseline'] = dict(report_path='prior.md', sha256=hashlib.sha256(raw).hexdigest(),
                discounts={k: dict(value=v['value'], quote='explicit offline assumption')
                           for k, v in prior['discounts'].items()})
            for row in current['discounts'].values():
                row['change']['kind'] = 'unchanged'
            callback(root)

    def test_unresolved_global_actions_cannot_become_eligibility_under_same_id(self):
        for legacy in (False, True):
            for action in ('freeze', 'reject', 'unavailable'):
                for status in ('blocking', 'unknown'):
                    with self.subTest(legacy=legacy, action=action, status=status):
                        prior, old_doc = self.restricted_pair(action, status, legacy=legacy)
                        current, doc = self.restricted_pair('eligibility', status)
                        def check(root):
                            with self.assertRaisesRegex(ValueError, 'explicitly cleared before'):
                                audit.validate_audit(current, doc, root=root)
                        self.with_baseline(prior, old_doc, current, check)

    def test_confirmed_reject_cannot_become_unknown(self):
        prior, old_doc = self.restricted_pair('reject')
        current, doc = self.restricted_pair('reject', 'unknown')
        def check(root):
            with self.assertRaisesRegex(ValueError, 'explicitly cleared before'):
                audit.validate_audit(current, doc, root=root)
        self.with_baseline(prior, old_doc, current, check)

    def test_incomparable_restrictions_require_clearance_before_replacement(self):
        for old_action, new_action in (('unavailable', 'freeze'), ('freeze', 'unavailable'), ('reject', 'unavailable')):
            with self.subTest(old_action=old_action, new_action=new_action):
                prior, old_doc = self.restricted_pair(old_action)
                current, doc = self.restricted_pair(new_action)
                def check(root):
                    with self.assertRaisesRegex(ValueError, 'explicitly cleared before'):
                        audit.validate_audit(current, doc, root=root)
                self.with_baseline(prior, old_doc, current, check)

    def test_retention_tightening_and_explicit_release_remain_valid(self):
        for old_action, new_action in (('freeze', 'freeze'), ('freeze', 'reject'), ('eligibility', 'freeze'),
                                       ('unavailable', 'unavailable'), ('reject', 'reject')):
            with self.subTest(old_action=old_action, new_action=new_action):
                prior, old_doc = self.restricted_pair(old_action)
                current, doc = self.restricted_pair(new_action)
                self.with_baseline(prior, old_doc, current,
                                   lambda root: audit.validate_audit(current, doc, root=root))
        for action in ('freeze', 'reject', 'unavailable'):
            with self.subTest(legacy=True, action=action):
                prior, old_doc = self.restricted_pair(action, legacy=True)
                current, doc = self.restricted_pair(action)
                self.with_baseline(prior, old_doc, current,
                                   lambda root: audit.validate_audit(current, doc, root=root))
        prior, old_doc = self.restricted_pair('unavailable', 'unknown')
        doc = prices.build_document(sample())
        current = audit_for(doc)
        current['constraints'] = [dict(prior['constraints'][0], status='clear', release_conditions=[],
                                       clearance=dict(evidence=['new original evidence, section 2']))]
        self.with_baseline(prior, old_doc, current,
                           lambda root: audit.validate_audit(current, doc, root=root))


if __name__ == '__main__': unittest.main()
