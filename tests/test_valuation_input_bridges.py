"""New evidence/DCF contract; historical v4 remains a separate frozen contract."""
from copy import deepcopy
from decimal import Decimal as D
from pathlib import Path
import sys
import unittest
import hashlib
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts import research_valuation as calc, research_consistency as audit
from test_research_valuation import example, flat_scenarios
import test_research_consistency as consistency_tests
from research_audit_fixture import valuation_review_for, input_basis_for


def bridged():
    m = example(); m['year_end_offset'] = 0
    for row in m['scenarios'].values():
        seg = row['segments'][0]
        y = seg['years'][0]
        y['cash_tax'] = D(str(y['revenue'])) * D(str(y['ebit_margin'])) * D(str(y.pop('tax_rate')))
        seg['terminal']['invested_capital'] = 150
        del seg['terminal']['roic']
    return m


def audited():
    a, d = consistency_tests.CapitalAuditTests().example()
    a['schema_version'] = 'stock-research-audit/v5'
    a['valuation_review'] = valuation_review_for(d)
    a['valuation_review']['input_basis'] = input_basis_for(d)
    for r in a['risks']: r['economic_key'] = r['id']
    return a, d


class InputBridgeTests(unittest.TestCase):
    def test_frozen_v4_report_and_dcf_display_bytes_are_preserved(self):
        fixture=consistency_tests.ValuationAuditTests()
        for name,digest in [('example','f24d6266e8e5470db53055d5c15c5f5315880caec10659e39af73b5bf95ea11c'),
                            ('dcf_example','ab2c4ac4cbf2f096dca98d3a73f38d0caefda0ef7dc709f3397bf4d8046eb892')]:
            a,d=getattr(fixture,name)()
            self.assertEqual(hashlib.sha256(audit.render_report_block(a,d).encode()).hexdigest(),digest)

    def test_v5_dcf_full_audit_and_reverse_roundtrip(self):
        a,d=consistency_tests.ValuationAuditTests().dcf_example()
        a['schema_version']='stock-research-audit/v5';a['valuation']=bridged()
        a['valuation_review']['input_basis']=input_basis_for(d)
        for row in a['risks']: row['economic_key']=row['id']
        # g=0 makes old and new conditional reverse identical.
        text=audit.render_report_block(a,d)
        audit.validate_report(text,d,expected_schema='stock-research-audit/v5')

    def test_new_terminal_cannot_hide_unsustainable_reinvestment(self):
        m=bridged()
        m['scenarios']['base']['segments'][0]['terminal'].update(growth=.02,invested_capital=10000)
        with self.assertRaisesRegex(ValueError,'terminal FCFF'):calc.evaluate_dcf(m,input_bridges=True)

    def test_unknown_discount_baseline_remains_unknown_and_cannot_erase_known_value(self):
        a,d=audited();d['price_map'].update(mode='unavailable',p1=None);a['p1_basis']={}
        a['constraints'][0]['action']='unavailable'
        a['valuation_review']['input_basis']['residual_discount'].update(status='unresolved',gaps=['no bound'],affects='p1')
        a['discounts']['d_base'].update(value=None,range=None)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);report=audit.render_report_block(a,d);(root/'prior.md').write_text(report)
            a['baseline']=dict(report_path='prior.md',sha256=hashlib.sha256(report.encode()).hexdigest(),
                discounts={k:dict(value=v['value'],range=v['range'],quote=v['reason']) for k,v in a['discounts'].items()})
            for k,v in a['discounts'].items():v['change']['kind']='initial' if k=='d_base' else 'unchanged'
            audit.validate_audit(a,d,root=root)
            # A previously known audited 0 cannot be represented as missing.
            a['baseline']['discounts']['r_chip'].update(value=None,range=None)
            with self.assertRaisesRegex(ValueError,'cannot be discarded'):audit.validate_audit(a,d,root=root)

    def test_equal_economics_gives_same_price_without_mutating_inputs(self):
        m = bridged(); before = deepcopy(m)
        self.assertEqual(calc.evaluate_dcf(m, input_bridges=True)['values'], calc.evaluate_dcf(example())['values'])
        self.assertEqual(m, before)
        with self.assertRaises(ValueError): calc.evaluate_dcf(m)
        with self.assertRaises(ValueError): calc.evaluate_dcf(example(), input_bridges=True)

    def test_positive_cash_tax_can_coexist_with_consolidated_loss(self):
        m = bridged(); r=m['scenarios']['base']; y=r['segments'][0]['years'][0]
        y.update(ebit_margin=-.1, cash_tax=5)
        r['equity_value'] = D('-15')/D('1.1') + D(150)/D('1.1') + 10
        flat_scenarios(m,r)
        result=calc.evaluate_dcf(m,input_bridges=True)
        self.assertEqual(result['details']['base']['segments'][0]['years'][0]['nopat'], -15)
        y=m['scenarios']['base']['segments'][0]['years'][0]; y['cash_tax']=-1
        with self.assertRaisesRegex(ValueError,'cash_tax'): calc.evaluate_dcf(m,input_bridges=True)

    def test_pure_terminal_tax_change_does_not_change_productive_investment(self):
        results=[]
        for tax in (.15,.25):
            m=bridged(); r=m['scenarios']['base']; s=r['segments'][0]
            s['terminal'].update(growth=.02, tax_rate=tax)
            nopat=D(100)*D('1.02')*D('.2')*(1-D(str(tax)))
            r['equity_value']=(15+(nopat-D(3))/D('.08'))/D('1.1')+10
            flat_scenarios(m,r)
            results.append(calc.evaluate_dcf(m,input_bridges=True)['details']['base']['segments'][0])
        self.assertEqual([r['terminal_reinvestment'] for r in results],[3,3])
        self.assertGreater(results[0]['enterprise_value'],results[1]['enterprise_value'])

    def test_reverse_uses_same_productive_capital_and_cash_tax(self):
        m=bridged()
        result=calc.solve_reverse_dcf(m,scenario='base',segment_id='core',variable='terminal_margin',target_price=160,lower=0,upper=1,input_bridges=True)
        self.assertAlmostEqual(result['parameter'],D('.2'))
        calc.validate_reverse_dcf(m,dict(scenario='base',segment_id='core',variable='terminal_margin',target_price=160,lower=0,upper=1,**result),input_bridges=True)

    def test_fractional_discount_time_is_not_silently_reset(self):
        m=bridged(); m['year_end_offset']=.1452054794520548
        for row in m['scenarios'].values():
            row['equity_value']=(D(str(row['equity_value']))-10)/D('1.1')**D(str(m['year_end_offset']))+10
        result=calc.evaluate_dcf(m,input_bridges=True)
        self.assertAlmostEqual(result['values']['base'], D(150)/D('1.1')**D(str(m['year_end_offset']))+10)
        m['year_end_offset']=-1
        with self.assertRaisesRegex(ValueError, 'year_end_offset'): calc.evaluate_dcf(m,input_bridges=True)

    def test_evidence_cutoff_status_and_duplicate_economic_loss(self):
        a,d=audited(); audit.validate_audit(a,d)
        for mutate, message in [
            (lambda a: a['valuation_review']['input_basis']['tax']['evidence'][0].update(as_of='2099-01-01'),'cutoff'),
            (lambda a: a['valuation_review']['input_basis']['capital'].update(status='unresolved',gaps=['ownership'],affects='v50'),'V50'),
            (lambda a: a['valuation_review']['input_basis']['residual_discount'].update(status='unresolved',gaps=['unbounded'],affects='p1'),'P1'),
            (lambda a: a['risks'].append(dict(a['risks'][0],id='renamed',owner='margin')),'economic_key'),
        ]:
            with self.subTest(message=message):
                a,d=audited(); mutate(a)
                with self.assertRaisesRegex(ValueError,message): audit.validate_audit(a,d)

    def test_unresolved_discount_is_not_zero_and_does_not_generate_quote(self):
        a,d=audited(); d['price_map'].update(p1=None, mode='unavailable'); a['p1_basis']={}
        a['constraints'][0]['action']='unavailable'
        a['valuation_review']['input_basis']['residual_discount'].update(status='unresolved',gaps=['not bounded'],affects='p1')
        a['discounts']['d_base'].update(value=None,range=None)
        result=audit.validate_audit(a,d)
        self.assertIsNone(result['discount_factor'])
        block=audit.render_report_block(a,d)
        audit.validate_report(block,d)
        self.assertIn('未决',block)
        d['price_map'].update(mode='tracking',p1={'base':12}); a['p1_basis']={'base':'base'}
        with self.assertRaisesRegex(ValueError,'P1'): audit.validate_audit(a,d)

if __name__ == '__main__': unittest.main()
