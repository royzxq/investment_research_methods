"""Research arithmetic/state failure paths, independent of model/network calls."""
from copy import deepcopy
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tests'))
from scripts import research_consistency as checks
from research_audit_fixture import audit_for


def example():
    doc = {
        'meta': dict(schema_version='stock-research/v3', code='600066.SH', name='离线样例',
                     valuation_date='2026-10-15', currency='CNY', generator='codex', report_path='research/example.md'),
        'price_map': dict(mode='tracking', reason='offline', v50=dict(low=20, base=24, high=30),
                          p1=dict(base=12), p2=dict(status='cancelled', price=None, reason='offline'),
                          t1=dict(price_condition='接近V50上沿时复核', events=['review']),
                          t2=dict(price_condition='明显高于V50上沿时复核', events=['failure'])),
        'monitoring': [dict(variable='income', current=None, as_of=None, trigger='falls',
                            action='review', source='offline', next_check='next report')],
    }
    return audit_for(doc), doc


class ResearchConsistencyTests(unittest.TestCase):
    def test_full_chain_and_visible_view_round_trip_preserve_quotes(self):
        audit, doc = example()
        before = deepcopy(doc)
        report = checks.render_report_block(audit, doc)
        result = checks.validate_report(report, doc)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['discount_factor'], .5)
        self.assertEqual(doc, before)
        with self.assertRaisesRegex(ValueError, 'visible calculation view'):
            checks.validate_report(report.replace('| base | 100 |', '| base | 405 |'), doc)

    def test_profit_equity_shares_and_quote_mismatches_fail(self):
        for field, value, error in [('profit', 50, 'base.profit'),
                                    ('equity_value', 575, 'base.equity_value'),
                                    ('net_margin', 24, 'fraction')]:
            audit, doc = example()
            audit['valuation']['scenarios']['base'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, error):
                checks.validate_audit(audit, doc)
        audit, doc = example()
        audit['valuation']['shares'] = 10
        with self.assertRaisesRegex(ValueError, 'V50 mismatch'):
            checks.validate_audit(audit, doc)
        audit, doc = example()
        doc['price_map']['p1']['base'] = 13
        with self.assertRaisesRegex(ValueError, 'P1 formula'):
            checks.validate_audit(audit, doc)

    def test_profit_adjustment_requires_sourced_bridge(self):
        audit, doc = example()
        row = audit['valuation']['scenarios']['base']
        row['net_margin'] = .20
        row['adjustments'] = [dict(id='scope', amount=4, reason='explicit scope bridge', source='original note')]
        checks.validate_audit(audit, doc)
        row['adjustments'][0]['source'] = ''
        with self.assertRaisesRegex(ValueError, 'adjustment.source'):
            checks.validate_audit(audit, doc)

    def test_non_pe_uses_unrounded_research_value_without_repricing_quote(self):
        audit, doc = example()
        audit['valuation'] = dict(kind='other', reason='PFCF independently derived in report',
                                  unrounded_v50=dict(low=20, base=24.005, high=30))
        doc['price_map']['v50']['base'] = 24.01
        doc['price_map']['p1']['base'] = 12.00
        # 24.005 * .5 = 12.0025 rounds to 12.00; using 24.01 would give 12.01.
        checks.validate_audit(audit, doc)

    def test_risk_in_profit_or_eligibility_cannot_be_charged_again(self):
        for owner in ('margin', 'multiple', 'eligibility'):
            audit, doc = example()
            audit['risks'][0]['owner'] = owner
            with self.subTest(owner=owner), self.assertRaisesRegex(ValueError, 'already absorbed'):
                checks.validate_audit(audit, doc)
        audit, doc = example()
        audit['discounts']['r_v5'].update(value=.05, range=[.03, .07], risk_ids=['estimation'])
        with self.assertRaisesRegex(ValueError, 'already absorbed'):
            checks.validate_audit(audit, doc)

    def test_freeze_cannot_hide_in_tracking_and_release_requires_every_blocker(self):
        audit, doc = example()
        audit['constraints'] = [dict(id=ident, effect=effect, status='unknown', reason='missing evidence',
                                     release_conditions=['verify evidence'])
                                for ident, effect in (('D5', 'freeze'), ('R9', 'eligibility'))]
        audit['release_all_of'] = ['D5', 'R9']
        audit['constraints'][0]['clearance'] = dict(stage='deepening', evidence=[])
        with self.assertRaisesRegex(ValueError, 'hidden as tracking'):
            checks.validate_audit(audit, doc)
        doc['price_map']['mode'] = 'frozen'
        checks.validate_audit(audit, doc)
        audit['release_all_of'] = ['R9']
        with self.assertRaisesRegex(ValueError, 'ALL unresolved'):
            checks.validate_audit(audit, doc)
        audit['release_all_of'] = {'any_of': ['D5', 'R9']}
        with self.assertRaisesRegex(ValueError, 'expected list'):
            checks.validate_audit(audit, doc)

    def test_r9_only_and_d5_not_applicable_can_keep_observation_price(self):
        audit, doc = example()
        audit['constraints'] = [dict(id='D5', effect='freeze', status='not_applicable',
                                     reason='earnings review, no rotation/new reception use', release_conditions=[]),
                                dict(id='R9', effect='eligibility', status='blocking',
                                     reason='historical percentiles missing', release_conditions=['verify R9'])]
        audit['release_all_of'] = ['R9']
        doc['price_map']['mode'] = 'observation'
        checks.validate_audit(audit, doc)
        doc['price_map']['mode'] = 'buy_candidate'
        with self.assertRaisesRegex(ValueError, 'forbids buy_candidate'):
            checks.validate_audit(audit, doc)

    def test_restrictive_mode_requires_its_actual_declared_constraint(self):
        for mode in ('frozen', 'rejected', 'unavailable'):
            audit, doc = example()
            doc['price_map']['mode'] = mode
            if mode != 'frozen':
                doc['price_map']['p1'] = None
                audit['p1_basis'] = {}
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, mode + ' mode requires'):
                checks.validate_audit(audit, doc)

    def test_r21_waiting_cannot_be_declared_full_d5_clearance(self):
        audit, doc = example()
        audit['constraints'] = [dict(id='D5', effect='eligibility', status='clear',
            reason='market use explicitly applies', release_conditions=[],
            clearance=dict(stage='waiting_review', evidence=['R21 exit evidence']))]
        with self.assertRaisesRegex(ValueError, 'R21 exit/waiting'):
            checks.validate_audit(audit, doc)
        audit['constraints'][0]['clearance'] = dict(stage='rebuild_review_complete', evidence=['original rebuild and company review evidence'])
        checks.validate_audit(audit, doc)

    def test_baseline_changes_require_reason_evidence_and_matching_original(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audit, doc = example()
            report = checks.render_report_block(audit, doc)
            path = root/'prior.md'
            path.write_text(report)
            baseline = dict(report_path='prior.md', sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            discounts={key: dict(value=entry['value'], quote='explicit offline assumption')
                                       for key, entry in audit['discounts'].items()})
            audit['baseline'] = baseline
            for entry in audit['discounts'].values():
                entry['change']['kind'] = 'unchanged'
            checks.validate_audit(audit, doc, root=root)
            audit['discounts']['d_base']['value'] = .4
            with self.assertRaisesRegex(ValueError, 'drift without classified'):
                checks.validate_audit(audit, doc, root=root)
            audit['discounts']['d_base']['change'].update(kind='correction', reason='remove duplicate uncertainty')
            with self.assertRaisesRegex(ValueError, 'requires evidence'):
                checks.validate_audit(audit, doc, root=root)
            audit['discounts']['d_base']['change']['evidence'] = ['identified duplicate in original model']
            doc['price_map']['p1']['base'] = 14.4
            checks.validate_audit(audit, doc, root=root)
            baseline['discounts']['d_base']['value'] = .9
            with self.assertRaisesRegex(ValueError, 'original audit'):
                checks.validate_audit(audit, doc, root=root)

    def test_duplicate_json_blocks_keys_and_nonfinite_values_fail(self):
        audit, doc = example()
        report = checks.render_report_block(audit, doc)
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            checks.validate_report(report + report, doc)
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            checks.extract_audit(report.replace('"schema_version":', '"schema_version":"x", "schema_version":', 1))
        audit['discounts']['d_base']['value'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            checks.validate_audit(audit, doc)

    def test_legacy_rejected_baseline_with_no_discount_values_does_not_invent_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/'prior.md'
            path.write_text('核心事实缺失，本轮不提供估值与折扣参数。')
            audit, doc = example()
            audit['baseline'] = dict(report_path='prior.md', sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                discounts={key: dict(value=None, range=None, quote=path.read_text()) for key in checks.DISCOUNTS})
            checks.validate_audit(audit, doc, root=root)


if __name__ == '__main__':
    unittest.main()
