"""R22 delivery compatibility; synthetic inputs, not return calibration."""
from copy import deepcopy
from decimal import Decimal
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts import research_consistency as audit, stock_price_map as prices
from research_audit_fixture import audit_for
from test_two_price_contract import sample


def quote(base_discount, ceiling, *, chip=0):
    value = sample()
    value['valuation']['values'] = dict(low=80, base=100, high=120)
    value['t1']['price_condition'] = '股价≥120元/股'
    a = Decimal(100) * (1 - Decimal(str(chip)))
    discount = max(Decimal(str(base_discount)), 1 - Decimal(str(ceiling)) / a)
    value['p1'] = dict(base=float(audit.quote_round(a * (1 - discount), 'CNY')))
    doc = prices.build_document(value)
    block = audit_for(doc)
    block['valuation'] = dict(kind='other', reason='independent synthetic valuation',
                              unrounded_v50=dict(low=80, base=100, high=120))
    block['discounts']['d_base'].update(value=float(discount), range=[float(discount)] * 2,
        risk_ids=['model_residual', 'R22_OPPORTUNITY'] if discount > Decimal(str(base_discount)) else ['model_residual'])
    block['discounts']['r_chip'].update(value=chip, range=[chip] * 2,
                                       risk_ids=['liquidity'] if chip else [])
    block['risks'] = [dict(id=ident, owner=owner, description=ident,
        scope='independent residual; operating valuation excludes this effect', source='synthetic evidence')
        for ident, owner in [('model_residual', 'd_base')]
        + ([('R22_OPPORTUNITY', 'd_base')] if discount > Decimal(str(base_discount)) else [])
        + ([('liquidity', 'r_chip')] if chip else [])]
    return block, doc


class EtfPriceMapCompatibilityTests(unittest.TestCase):
    def test_tighten_or_retain_price_without_changing_t1_or_controls(self):
        for base, ceiling, chip, expected in ((.15, 80, 0, 80), (.28, 80, 0, 72),
                                              (.2, 76, .05, 76), (.2, 70, .05, 70)):
            with self.subTest(base=base, ceiling=ceiling, chip=chip):
                block, doc = quote(base, ceiling, chip=chip)
                before = deepcopy(doc)
                report = audit.render_report_block(block, doc)
                self.assertEqual(audit.validate_report(report, doc)['status'], 'passed')
                self.assertEqual(doc, before)
                self.assertEqual(doc['price_map']['p1'], {'base': expected})
                self.assertEqual(doc['price_map']['t1']['price_condition'], '股价≥120元/股')
                self.assertEqual(doc['research_controls']['entry']['status'], 'eligible')
                self.assertEqual(set(block['discounts']), set(audit.DISCOUNTS))

    def test_residual_cannot_be_billed_again_as_liquidity(self):
        block, doc = quote(.15, 80)
        block['discounts']['r_chip'].update(value=.05, range=[.05, .05], risk_ids=['R22_OPPORTUNITY'])
        with self.assertRaisesRegex(ValueError, 'already absorbed'):
            audit.validate_audit(block, doc)

    def test_incompatible_scenario_interval_is_rejected(self):
        block, doc = quote(.15, 80)
        # Common final discount is 20%; a separately capped high quote cannot
        # masquerade as this same discount's valuation scenario.
        doc['price_map']['p1']['high'] = 90
        doc['price_map']['p1']['low'] = 64
        block['p1_basis']['high'] = 'high'
        block['p1_basis']['low'] = 'low'
        with self.assertRaisesRegex(ValueError, 'P1 formula'):
            audit.validate_audit(block, doc)

    def test_repeat_and_evidence_based_release_preserve_frozen_baseline(self):
        previous, old_doc = quote(.15, 80)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            baseline = audit.render_report_block(previous, old_doc).encode()
            (root / 'baseline.md').write_bytes(baseline)
            for ceiling, kind, expected in ((80, 'unchanged', 80), (90, 'new_evidence', 85)):
                current, doc = quote(.15, ceiling)
                current['baseline'] = dict(report_path='baseline.md', sha256=hashlib.sha256(baseline).hexdigest(),
                    discounts={key: dict(value=item['value'], range=item['range'], quote=item['reason'])
                               for key, item in previous['discounts'].items()})
                for item in current['discounts'].values():
                    item['change']['kind'] = 'unchanged'
                current['discounts']['d_base']['change'] = dict(kind=kind,
                    reason='same residual or evidenced replacement of prior R22 assumptions',
                    evidence=[] if kind == 'unchanged' else ['new forward cash-flow evidence'])
                report = audit.render_report_block(current, doc, root=root)
                self.assertEqual(audit.validate_report(report, doc, root=root)['status'], 'passed')
                self.assertEqual(doc['price_map']['p1']['base'], expected)
                self.assertEqual((root / 'baseline.md').read_bytes(), baseline)
                if kind == 'new_evidence':
                    current['discounts']['d_base']['change']['evidence'] = []
                    with self.assertRaisesRegex(ValueError, 'requires evidence'):
                        audit.validate_audit(current, doc, root=root)
