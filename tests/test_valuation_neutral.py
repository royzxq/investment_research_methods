from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts import research_consistency as checks
from test_valuation_availability import example, unresolved, review
from research_audit_fixture import neutral_review_for


def current():
    a,d=example();a['schema_version']=checks.SCHEMA
    a['valuation_review']['neutral_review']=neutral_review_for(a,d)
    return a,d


class NeutralTests(unittest.TestCase):
    def test_priced_and_frozen_quotes_preserved(self):
        a,d=current();before=deepcopy(d)
        checks.validate_report(checks.render_report_block(a,d),d,expected_schema=checks.SCHEMA)
        self.assertEqual(d,before)

    def test_missing_review_rejected_even_with_null_p1(self):
        a,d=unresolved('residual_discount');a['schema_version']=checks.SCHEMA
        a['valuation_review']['availability_review']=review(['residual_discount'])
        a['valuation_review']['neutral_review']=None
        with self.assertRaisesRegex(ValueError,'every adopted V50'): checks.validate_audit(a,d)
        a['valuation_review']['neutral_review']=neutral_review_for(a,d)
        checks.validate_audit(a,d)

    def test_unavailable_price_retains_original_availability_gate(self):
        a,d=unresolved('capital');a['schema_version']=checks.SCHEMA
        a['valuation_review'].update(neutral_review=None,availability_review=review(['capital']))
        checks.validate_audit(a,d)

    def test_future_source_rejected(self):
        a,d=current();a['valuation_review']['neutral_review']['assumptions'][0]['evidence'][0]['as_of']='2099-01-01'
        with self.assertRaisesRegex(ValueError,'date/cutoff'): checks.validate_audit(a,d)

    def test_duplicate_topic_cannot_cover_missing_topic(self):
        a,d=current();rows=a['valuation_review']['neutral_review']['assumptions'];rows[-1]=deepcopy(rows[0])
        with self.assertRaisesRegex(ValueError,'five distinct'): checks.validate_audit(a,d)

    def test_capital_rollforward_and_continuity(self):
        a,d=current();b=a['valuation_review']['neutral_review']['capital_bridge']
        b.update(status='approximate',rows=[dict(scope='group',period='2027',opening=100,capex=25,da=10,other=-5,closing=110,other_reason='disposal'),dict(scope='group',period='2028',opening=110,capex=25,da=10,other=0,closing=125,other_reason='none')])
        checks.validate_audit(a,d)
        b['rows'][1].update(opening=109,closing=124)
        with self.assertRaisesRegex(ValueError,'do not connect'): checks.validate_audit(a,d)
        b['rows'][1].update(opening=110,closing=123)
        with self.assertRaisesRegex(ValueError,'does not reconcile'): checks.validate_audit(a,d)

    def test_missing_risk_coverage_rejected(self):
        a,d=current();a['valuation_review']['neutral_review']['risk_pricing']=[]
        with self.assertRaisesRegex(ValueError,'each priced risk'): checks.validate_audit(a,d)

    def test_malformed_risk_and_neutral_fields_rejected_cleanly(self):
        malformed = (
            (lambda a, r: a.update(risks=None), 'risks: expected list'),
            (lambda a, r: a.update(risks=[None]), 'risk: expected object'),
            (lambda a, r: r['assumptions'][0].update(topic=[]), 'neutral assumption.topic'),
            (lambda a, r: r['capital_bridge'].update(status={}), 'neutral capital_bridge.status'),
            (lambda a, r: r['risk_pricing'][0].update(risk_id=[]), 'neutral risk pricing.risk_id'),
            (lambda a, r: r['sensitivities'][0].update(topic=[]), 'neutral sensitivity.topic'),
        )
        for mutate, message in malformed:
            with self.subTest(field=message):
                audit, document = current()
                mutate(audit, audit['valuation_review']['neutral_review'])
                with self.assertRaisesRegex(ValueError, message):
                    checks.validate_audit(audit, document)

    def test_period_labels_cannot_hide_reversed_or_duplicate_calendar(self):
        a,d=current();b=a['valuation_review']['neutral_review']['capital_bridge']
        b.update(status='approximate',rows=[dict(scope='group',period='2028',opening=100,capex=0,da=0,other=0,closing=100,other_reason='none'),dict(scope='group',period='2027',opening=100,capex=0,da=0,other=0,closing=100,other_reason='none')])
        with self.assertRaisesRegex(ValueError,'chronological'): checks.validate_audit(a,d)
        b['rows'][1]['period']='2028Q4'
        with self.assertRaisesRegex(ValueError,'chronological'): checks.validate_audit(a,d)
        b['rows'][1]['period']='later'
        with self.assertRaisesRegex(ValueError,'period must be'): checks.validate_audit(a,d)
        b['rows'][0]['period']='2026Q4';b['rows'][1]['period']='2027-12-31'
        checks.validate_audit(a,d)
        b['rows'][0]['period']='t1';b['rows'][1]['period']='t2'
        checks.validate_audit(a,d)
        b['rows'][1]['period']='2027'
        with self.assertRaisesRegex(ValueError,'cannot be mixed'): checks.validate_audit(a,d)
        b['rows'][0]['period']='t2';b['rows'][1]['period']='t1'
        with self.assertRaisesRegex(ValueError,'chronological'): checks.validate_audit(a,d)

    def test_sensitivity_is_bound_to_adopted_base_and_delta(self):
        a,d=current();r=a['valuation_review']['neutral_review']['sensitivities'][0]
        b=d['price_map']['v50']['base'];r.update(alternative_v50=b-2,delta=-2)
        checks.validate_audit(a,d)
        r['delta']=-1
        with self.assertRaisesRegex(ValueError,'delta mismatch'): checks.validate_audit(a,d)
        r.update(base_v50=b-1,delta=-1)
        with self.assertRaisesRegex(ValueError,'differs from adopted'): checks.validate_audit(a,d)

    def test_unquantifiable_capital_bridge_does_not_cancel_price(self):
        a,d=current();a['valuation_review']['neutral_review']['capital_bridge'].update(status='unavailable',explanation='bounded valuation uses independent earnings proxy; asset schedule absent')
        checks.validate_audit(a,d);self.assertIsNotNone(d['price_map']['v50'])

    def test_v6_remains_valid_and_does_not_accept_v7_fields(self):
        a,d=example();checks.validate_audit(a,d)
        a['valuation_review']['neutral_review']=neutral_review_for(a,d)
        with self.assertRaises(ValueError): checks.validate_audit(a,d)

if __name__=='__main__': unittest.main()
