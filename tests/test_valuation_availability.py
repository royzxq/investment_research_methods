"""Availability review keeps supported quotes and makes abstention reviewable."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts import research_consistency as checks
from test_valuation_input_bridges import audited, bridged
from research_audit_fixture import input_basis_for
import test_research_consistency as consistency_tests


def example():
    audit, document = audited()
    audit['schema_version'] = checks.AVAILABILITY_SCHEMA
    audit['valuation_review']['availability_review'] = None
    return audit, document


def unresolved(*keys):
    audit, document = example()
    core = any(key != 'residual_discount' for key in keys)
    document['price_map'].update(mode='unavailable', p1=None)
    audit['p1_basis'] = {}
    audit['constraints'][0]['action'] = 'unavailable'
    if core:
        document['price_map']['v50'] = None
        audit['valuation'] = dict(kind='unavailable', reason='ordinary equity exposure cannot be bounded')
        document['price_map']['t1'] = dict(price_condition='本轮不提供T1报价')
    for key in keys:
        audit['valuation_review']['input_basis'][key].update(status='unresolved', gaps=['missing claim perimeter'])
    if 'residual_discount' in keys:
        audit['discounts']['d_base'].update(value=None, range=None)
    return audit, document


def review(keys):
    return dict(decision_reason='claim perimeter can change ordinary equity materially',
        attempts=[dict(inputs=list(keys), method='issuer liability cap and net asset alternative reviewed',
            bounds_or_failure='available disclosure does not bound parent recourse or attached assets',
            impact='parent liability can exceed the modeled net assets; no supportable finite floor',
            conclusion='keep material inputs unresolved')],
        diagnostic_summary='operating scenarios alone exclude the missing claims and cannot establish equity or P1',
        next_evidence='issuer disclosure of parent guarantees and corresponding collateral')


class AvailabilityTests(unittest.TestCase):
    def test_v6_dcf_and_reverse_keep_cash_tax_and_productive_capital(self):
        audit, document = consistency_tests.ValuationAuditTests().dcf_example()
        audit['schema_version'] = checks.AVAILABILITY_SCHEMA
        audit['valuation'] = bridged()
        audit['valuation_review'].update(input_basis=input_basis_for(document), availability_review=None)
        for risk in audit['risks']:
            risk['economic_key'] = risk['id']
        checks.validate_report(checks.render_report_block(audit, document), document, expected_schema=checks.AVAILABILITY_SCHEMA)

    def test_actual_price_interval_does_not_require_a_base_or_null_review(self):
        audit, document = example()
        document['price_map']['p1'] = dict(base=None, low=10, high=15)
        audit['p1_basis'] = dict(low='low', high='high')
        checks.validate_audit(audit, document)

    def test_bounded_assumptions_keep_prices_and_independent_qualification(self):
        audit, document = example()
        audit['valuation_review']['input_basis']['tax'].update(status='bounded', gaps=['entity detail absent'],
            explanation='disclosed effective tax history supports a 20–30% range, with investment fixed')
        before = deepcopy(document)
        checks.validate_report(checks.render_report_block(audit, document), document, expected_schema=checks.AVAILABILITY_SCHEMA)
        self.assertEqual(document, before)
        self.assertEqual(document['research_controls']['entry']['status'], 'unknown')
        self.assertIsNotNone(document['price_map']['p1'])

    def test_temporary_freeze_keeps_observation_quotes(self):
        audit, document = example()
        document['price_map']['mode'] = 'frozen'
        audit['constraints'][0].update(action='freeze', status='blocking')
        for scope in ('entry', 'add'):
            document['research_controls'][scope]['status'] = 'blocked'
        checks.validate_audit(audit, document)
        self.assertIsNotNone(document['price_map']['p1'])

    def test_null_without_bounding_attempt_is_rejected(self):
        audit, document = unresolved('capital')
        with self.assertRaisesRegex(ValueError, 'availability_review required'):
            checks.validate_audit(audit, document)
        audit['valuation_review']['availability_review'] = review(['capital'])
        audit['valuation_review']['availability_review']['attempts'] = []
        with self.assertRaisesRegex(ValueError, 'null quotes need an attempt'):
            checks.validate_audit(audit, document)

    def test_declaring_every_input_resolved_cannot_bypass_null_review(self):
        audit, document = unresolved('capital')
        audit['valuation_review']['input_basis']['capital'].update(status='resolved', gaps=[])
        audit['valuation_review']['availability_review'] = review(['capital'])
        audit['valuation_review']['availability_review']['attempts'] = []
        with self.assertRaisesRegex(ValueError, 'confirmed hard failure'):
            checks.validate_audit(audit, document)

    def test_unbounded_claims_can_remain_null_with_visible_reasons(self):
        audit, document = unresolved('capital', 'investment')
        audit['valuation_review']['availability_review'] = review(['capital', 'investment'])
        block = checks.render_report_block(audit, document)
        checks.validate_report(block, document, expected_schema=checks.AVAILABILITY_SCHEMA)
        visible = block.split(checks.START)[0]
        self.assertIn('parent liability can exceed', visible)
        self.assertIn('下一项有效证据', visible)
        self.assertIsNone(document['price_map']['v50'])
        self.assertIsNone(document['price_map']['p1'])
        # An attempted review does not authorize adopting unresolved prices.
        document['price_map']['v50'] = dict(low=20, base=24, high=30)
        with self.assertRaisesRegex(ValueError, 'unresolved V50 input'):
            checks.validate_audit(audit, document)

    def test_p1_only_gap_preserves_v50_and_unknown_discount(self):
        audit, document = unresolved('residual_discount')
        audit['valuation_review']['availability_review'] = review(['residual_discount'])
        checks.validate_audit(audit, document)
        self.assertIsNotNone(document['price_map']['v50'])
        self.assertIsNone(audit['discounts']['d_base']['value'])

    def test_hard_rejection_needs_reason_but_no_fabricated_input_gap(self):
        audit, document = example()
        document['price_map'].update(mode='rejected', p1=None)
        audit['p1_basis'] = {}
        audit['constraints'][0].update(action='reject', status='blocking', reason='confirmed thesis failure')
        for scope in ('entry', 'add'):
            document['research_controls'][scope]['status'] = 'blocked'
        audit['valuation_review']['availability_review'] = dict(decision_reason='confirmed thesis failure',
            attempts=[], diagnostic_summary='V50 retained as reference; thesis failure prevents P1',
            next_evidence='new thesis review with original evidence')
        checks.validate_audit(audit, document)

    def test_review_cannot_omit_inputs_or_hide_empty_assessment(self):
        audit, document = unresolved('capital', 'tax')
        for change, message in (
            (lambda r: r['attempts'][0].update(inputs=['capital']), 'every unresolved'),
            (lambda r: r['attempts'].append(deepcopy(r['attempts'][0])), 'duplicate input'),
            (lambda r: r['attempts'][0].update(inputs=['unknown']), 'unknown input'),
            (lambda r: r['attempts'][0].update(impact=''), 'impact'),
            (lambda r: r.update(diagnostic_summary=''), 'diagnostic_summary'),
            (lambda r: r.update(next_evidence=''), 'next_evidence'),
        ):
            with self.subTest(message=message):
                availability = review(['capital', 'tax'])
                change(availability)
                audit['valuation_review']['availability_review'] = availability
                with self.assertRaisesRegex(ValueError, message):
                    checks.validate_audit(audit, document)

    def test_frozen_v5_null_report_keeps_original_contract(self):
        audit, document = unresolved('capital')
        audit['schema_version'] = checks.INPUT_BRIDGES_SCHEMA
        del audit['valuation_review']['availability_review']
        checks.validate_report(checks.render_report_block(audit, document), document,
                               expected_schema=checks.INPUT_BRIDGES_SCHEMA)


if __name__ == '__main__':
    unittest.main()
