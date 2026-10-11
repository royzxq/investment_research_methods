"""v3 framework plans use two models and six gates without breaking old audits."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_futures_audit_v3 import current
from test_validate_futures_audit import validate_audit, verified_account


def proposal(strategy='trend'):
    doc = current()
    doc['framework']['version'] = 'v3.0'
    c = doc['candidates'][0]
    c.update(strategy=strategy, contracts=['M2701'], direction='long', evidence_quality='adequate',
             signal='triggered', status='awaiting_account', all_blockers=[], unknown_checks=['G5', 'G6'],
             evaluated_checks=[dict(rule_id=f'G{i}', applicable=True, result='pass' if i<=4 else 'unknown',
                                     evidence_refs=['inventory'] if i<=4 else [],
                                     **({} if i<=4 else dict(gap=dict(kind='account', owner='user', next_action='核当日账户', due_at='before_execution'))))
                               for i in range(1,7)],
             plan=dict(entry=3000, stop=2900, targets=None, entry_range=[3000,3020],
                       signal_date='2026-09-07', valid_until='2026-09-09', latest_exit_date='2026-10-09',
                       exit_rule='initial_2atr_and_prior10_channel_tighten_only_max20_sessions'))
    if strategy == 'economic_reversion':
        c.update(contracts=['RB2701','RB2705'])
        c['plan'].update(entry=-50, stop=-70, targets=[10], entry_range=[-50,-45],
                         anchor_band=dict(low=10,high=20,source='economics.csv',as_of_date='2026-09-07'),
                         net_R=2.5, leg_ratio=[1,1], economic_anchor_basis='可核仓储与持有成本',
                         convergence_mechanism='两月供需与持有成本收敛', invalidation_basis='近端供给超预期')
    return doc


class FrameworkV3AuditTests(unittest.TestCase):
    def assert_error(self, doc, fragment):
        errors=validate_audit(doc)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_trend_without_fixed_target_is_research_complete(self):
        doc=proposal()
        self.assertEqual(validate_audit(doc), [])
        doc['candidates'][0]['status']='incomplete'
        self.assert_error(doc,'requires awaiting_account')

    def test_v3_ready_requires_all_six_gates_and_real_account(self):
        doc=proposal(); verified_account(doc)
        c=doc['candidates'][0]
        c.update(status='ready', final_lots=1, unknown_checks=[])
        c['risk_evaluation']=dict(calculator_ref='scripts/futures_risk.py size-v3',result=dict(
            rule_version='v3.0',scope='risk_sizing_only',status='valid',final_lots=1))
        for check in c['evaluated_checks']:
            check.update(result='pass', evidence_refs=['inventory'])
            check.pop('gap',None)
        self.assertEqual(validate_audit(doc), [])
        del c['evaluated_checks'][-1]
        self.assert_error(doc,'ready requires G1 through G6 all pass')

    def test_g6_cannot_exceed_helper_capacity_or_use_the_legacy_sizer(self):
        doc=proposal(); verified_account(doc); c=doc['candidates'][0]
        c.update(status='ready',final_lots=2,unknown_checks=[])
        for check in c['evaluated_checks']:
            check.update(result='pass',evidence_refs=['inventory']);check.pop('gap',None)
        c['risk_evaluation']=dict(calculator_ref='scripts/futures_risk.py size-v3',result=dict(
            rule_version='v3.0',scope='risk_sizing_only',status='valid',final_lots=1))
        self.assert_error(doc,'cannot exceed size-v3 final_lots')
        c['final_lots']=1
        self.assertEqual(validate_audit(doc),[])
        c['risk_evaluation']['calculator_ref']='scripts/futures_risk.py size'
        self.assert_error(doc,'requires scripts/futures_risk.py size-v3')
        c['risk_evaluation']['calculator_ref']='scripts/futures_risk.py size-v3'
        c['risk_evaluation']['result']['status']='incomplete'
        self.assert_error(doc,'G6 pass requires a valid size-v3 result')

    def test_v3_legacy_check_and_strategy_names_do_not_grant_permission(self):
        doc=proposal(); c=doc['candidates'][0]
        c['strategy']='C'
        self.assert_error(doc,'.strategy: expected')
        c['strategy']='trend'; c['evaluated_checks'][0]['rule_id']='#1'
        self.assert_error(doc,'not legacy rule IDs')

    def test_no_signal_may_stop_early_with_real_contract_and_direct_evidence(self):
        doc=proposal(); c=doc['candidates'][0]
        c.update(signal='not_triggered', status='no_signal', evaluated_checks=c['evaluated_checks'][:2],
                 unknown_checks=[], signal_evidence_refs=['inventory'], plan={}, all_blockers=['G2'], first_blocker='G2')
        c['evaluated_checks'][1]['result']='fail'
        self.assertEqual(validate_audit(doc), [])
        c['contracts']=['M主力']
        self.assert_error(doc,'distinct real contract IDs')

    def test_unknown_evidence_cannot_be_hidden_in_awaiting_account(self):
        doc=proposal(); c=doc['candidates'][0]
        c['evaluated_checks'][1].update(result='unknown',gap=dict(kind='acquisition',owner='research',next_action='补产业证据',due_at='next_report'))
        c['unknown_checks'].append('G2')
        self.assert_error(doc,'awaiting_account requires')
        c['status']='incomplete'
        self.assertEqual(validate_audit(doc), [])

    def test_numeric_plan_dates_range_trailing_rule_and_stop_are_checked(self):
        changes=[('entry_range',[2990,2995]),('stop',3100),('valid_until','2026-09-06'),
                 ('exit_rule','invented'),('targets',[3200]),('entry',True)]
        for field,value in changes:
            with self.subTest(field=field):
                doc=proposal(); doc['candidates'][0]['plan'][field]=value
                self.assertTrue(validate_audit(doc))

    def test_reversion_requires_economic_anchor_real_pair_and_net_r(self):
        doc=proposal('economic_reversion')
        self.assertEqual(validate_audit(doc), [])
        for field,value,fragment in [('net_R',2.49,'net_R'),('economic_anchor_basis','','economic_anchor_basis'),
                                     ('targets',[20],'near edge'),('leg_ratio',[True,True],'leg_ratio')]:
            with self.subTest(field=field):
                changed=copy.deepcopy(doc);changed['candidates'][0]['plan'][field]=value
                self.assert_error(changed,fragment)
        for contracts in (['M2705','M2701'],['M2701','RB2705']):
            changed=copy.deepcopy(doc);changed['candidates'][0]['contracts']=contracts
            self.assert_error(changed,'same product, near before far')

    def test_reversion_anchor_after_signal_cannot_validate_a_plan(self):
        doc=proposal('economic_reversion')
        doc['candidates'][0]['plan']['anchor_band']['as_of_date']='2026-09-08'
        self.assert_error(doc,'later than signal_date')

    def test_reversion_validity_covers_whole_range_not_only_selected_entry(self):
        doc=proposal('economic_reversion')
        doc['candidates'][0]['plan']['entry_range']=[-75,-45]
        self.assert_error(doc,'whole range must remain strictly between stop and near anchor edge')
        doc['candidates'][0]['plan']['entry_range']=[-55,10]
        self.assert_error(doc,'whole range must remain strictly between stop and near anchor edge')

    def test_selected_entry_day_cannot_equal_exit_or_precede_signal(self):
        for entry_day in ('2026-09-07','2026-10-09'):
            doc=proposal();doc['candidates'][0]['plan']['entry_date']=entry_day
            self.assert_error(doc,'.plan.entry_date: must follow signal_date')
        doc=proposal();doc['candidates'][0]['plan']['entry_date']='2026-09-08'
        self.assertEqual(validate_audit(doc),[])

    def test_new_signal_cannot_be_after_report_date(self):
        doc=proposal();doc['candidates'][0]['plan']['signal_date']='2026-09-08'
        self.assert_error(doc,'later than as_of_date')

    def test_product_permission_and_month_are_not_inferred_from_four_digits(self):
        for contract in ('AU2701','M2799'):
            doc=proposal();doc['candidates'][0]['contracts']=[contract]
            self.assertTrue(validate_audit(doc))
        doc=proposal('economic_reversion');doc['candidates'][0]['contracts']=['M2701','M2705']
        self.assert_error(doc,'outside the v3 strategy research pool')

    def test_unknown_account_cannot_pass_capacity_gates(self):
        doc=proposal(); c=doc['candidates'][0]
        for check in c['evaluated_checks'][4:]:check.update(result='pass',evidence_refs=['inventory'])
        c['unknown_checks']=[]
        self.assert_error(doc,'G5/G6 cannot pass without a verified account')

    def test_historical_schema3_is_unchanged(self):
        doc=current()
        self.assertEqual(validate_audit(doc), [])

    def test_malformed_v3_plan_values_report_errors_without_crashing(self):
        for field in ('plan','contracts','strategy','direction','evidence_quality'):
            for value in (None,[],{},True):
                with self.subTest(field=field,value=value):
                    doc=proposal();doc['candidates'][0][field]=value
                    self.assertTrue(validate_audit(doc))
        for field in ('entry_range','anchor_band','leg_ratio','targets'):
            for value in (None,{},True):
                doc=proposal('economic_reversion');doc['candidates'][0]['plan'][field]=value
                self.assertTrue(validate_audit(doc))


if __name__ == '__main__': unittest.main()
