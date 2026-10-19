import json
from pathlib import Path
import tempfile
import unittest

from scripts import research_consistency as audit, stock_price_map as prices
from test_two_price_contract import sample
from research_audit_fixture import audit_for


class ControlsSemanticsTests(unittest.TestCase):
    def test_explicit_release_coverage_must_match_the_unresolved_baseline_claim(self):
        value=sample();value['research_controls']['add']=dict(status='blocked',refs=['X'])
        old_doc=prices.build_document(value);old=audit_for(old_doc)
        rule=dict(id='X',scope=['add'],status='blocking',action='eligibility',reason='baseline fact',
                  release_conditions=['company review'],lifecycle='persistent')
        old['constraints']=[rule];old['release_all_of']['add']=['X']
        current_doc=prices.build_document(sample());current=audit_for(current_doc)
        release=dict(rule,status='clear',clearance=dict(evidence=['reviewed'],covers=['0'*64]))
        current['constraints']=[release]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'baseline.md').write_text(audit.render_report_block(old,old_doc))
            current['baseline']=dict(report_path='baseline.md')
            with self.assertRaisesRegex(ValueError,'coverage'):
                audit.validate_scoped_controls(current,current_doc,root=root)
            release['clearance']['covers']=[audit.constraint_claim_sha256(rule)]
            audit.validate_scoped_controls(current,current_doc,root=root)
            del release['clearance']['covers']  # Legacy explicit evidence remains compatible.
            audit.validate_scoped_controls(current,current_doc,root=root)

    def test_runtime_and_observation_do_not_enter_unresolved_research_set(self):
        for lifecycle in ('runtime', 'observation'):
            value = sample()
            value['research_controls']['add'] = dict(status='blocked', refs=['X'])
            doc = prices.build_document(value)
            check = audit_for(doc)
            check['constraints'] = [dict(id='X', scope=['add'], action='eligibility', status='blocking',
                reason='not a persistent research restriction', release_conditions=['price changes'], lifecycle=lifecycle)]
            check['release_all_of']['add'] = ['X']
            with self.assertRaisesRegex(ValueError, 'persistent'):
                audit.validate_audit(check, doc)

    def test_persistent_restriction_and_holding_unknown_are_scoped(self):
        value = sample()
        value['research_controls']['holding'] = dict(status='unknown', refs=['H'])
        doc = prices.build_document(value)
        check = audit_for(doc)
        check['constraints'] = [dict(id='H', scope=['holding'], action='review_holding', status='unknown',
            reason='approved deadline unknown', release_conditions=['official evidence and review'], lifecycle='persistent')]
        check['release_all_of']['holding'] = ['H']
        audit.validate_audit(check, doc)
        self.assertEqual(doc['research_controls']['entry']['status'], 'eligible')

    def test_watch_condition_has_no_unresolved_research_debt(self):
        doc = prices.build_document(sample())
        check = audit_for(doc)
        doc['monitoring'][0].update(id='FUTURE',kind='thesis_invalidation',state='watching')
        self.assertEqual(audit.validate_audit(check,doc)['unresolved_constraints'],dict(entry=[],add=[],holding=[]))

    def test_new_report_requires_lifecycle_but_legacy_v4_remains_readable(self):
        value=sample(); value['research_controls']['add']=dict(status='blocked',refs=['X'])
        doc=prices.build_document(value); check=audit_for(doc)
        rule=dict(id='X',scope=['add'],action='eligibility',status='blocking',
                  reason='required evidence missing',release_conditions=['company review'])
        check['constraints']=[rule]; check['release_all_of']['add']=['X']
        def report():
            return audit.render_checks(check,doc)+'\n'+audit.START+'\n```json\n'+json.dumps(check)+'\n```\n'+audit.END
        audit.validate_report(report(),doc)
        with self.assertRaisesRegex(ValueError,'explicit lifecycle'):
            audit.validate_report(report(),doc,require_lifecycle=True)
        rule['lifecycle']='persistent'
        audit.validate_report(report(),doc,require_lifecycle=True)
