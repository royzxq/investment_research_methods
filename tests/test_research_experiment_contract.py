"""Isolated delivery failure paths; fixtures are not investment calibration."""
from copy import deepcopy
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from scripts import research_experiment_contract as contract
from research_audit_fixture import audit_for


def fixture():
    doc = dict(meta=dict(schema_version='stock-research/v4', code='300750.SZ',
                        name='offline fixture', valuation_date='2026-10-21',
                        currency='CNY', generator='codex', report_path='research/example.md'),
               price_map=dict(mode='buy_candidate', reason=None,
                              v50=dict(low=20, base=24, high=30), p1=dict(base=12),
                              t1=dict(price_condition='接近V50上沿时复核')),
               research_controls={scope: dict(status='normal' if scope == 'holding' else 'eligible', refs=[])
                                  for scope in ('entry', 'add', 'holding')},
               monitoring=[dict(id='OPS', kind='general', state='watching', variable='income',
                                current=None, as_of=None, trigger='falls', action='review',
                                source='offline fixture', next_check='next report')])
    audit = audit_for(doc)
    audit['identity'].pop('generator')
    result = dict(schema_version=contract.SCHEMA, code='300750.SZ',
                  valuation_date='2026-10-21', currency='CNY', audit=audit,
                  **{key: doc[key] for key in contract.SUMMARY_KEYS})
    review = dict(precheck=dict(state='normal', d_base_upper_required=False, reason='offline fixture'),
                  r14=dict(applicability='not_applicable', stress_test='not_applicable',
                           constraint_ids=[], reason='offline fixture only, not CATL assessment'),
                  d5=dict(applicability='not_applicable', original_rebuild_independent=True,
                          r21_exit_is_full_clearance=False, reason='offline fixture'),
                  r9=dict(applicability='not_applicable', benchmark_status='not_applicable',
                          benchmark_currency=None, constraint_ids=[], reason='offline fixture'),
                  holding=dict(review_status='not_triggered', constraint_ids=[], reason='offline fixture'))
    return result, review


def report_for(result, review):
    return '\n\n'.join('## ' + str(index) + '. offline section' for index in range(9)) + '\n\n' + contract.render_experiment_sections(result, review)


def add_rule(result, ident, scopes, *, action='eligibility', status='unknown'):
    result['audit']['constraints'].append(dict(id=ident, scope=scopes, action=action,
        status=status, lifecycle='persistent', reason='offline evidence gap', release_conditions=['verify original evidence']))
    for scope in scopes:
        result['audit']['release_all_of'][scope].append(ident)
        control = result['research_controls'][scope]
        control['status'] = 'review_required' if scope == 'holding' else ('blocked' if status == 'blocking' else 'unknown')
        control['refs'].append(ident)
    if any(scope in scopes for scope in ('entry', 'add')):
        for scope in ('entry', 'add'):
            if result['research_controls'][scope]['status'] == 'eligible':
                add_rule(result, 'OTHER_' + scope.upper(), [scope])
        result['price_map'].update(mode='tracking', reason='offline necessary evidence gaps')


class ExperimentContractTests(unittest.TestCase):
    def shared_acceptance(self, result):
        return dict(schema_version='stock-research-acceptance/v1',
            r14=dict(applicability='not_applicable', stress_test='not_applicable',
                constraint_ids=[], reason='offline fixture only',
                inputs={key: dict(status='unknown', sources=[], derivation=None)
                        for key in ('exposure', 'cost_exposure', 'pass_through', 'ocf_bridge')},
                calculation=None),
            recovery=dict(operator='all_of', scopes=deepcopy(result['audit']['release_all_of'])))

    def test_new_shared_gate_is_required_only_for_new_contract_and_never_ignored(self):
        from scripts import research_acceptance
        result, review = fixture()
        report = report_for(result, review)
        self.assertNotIn('acceptance', contract.validate_experiment(report, result))
        with self.assertRaisesRegex(ValueError, 'acceptance block'):
            contract.validate_experiment(report, result, require_acceptance=True)
        block = research_acceptance.render_block(self.shared_acceptance(result), result['audit'])
        receipt = contract.validate_experiment(report + '\n' + block, result, require_acceptance=True)
        self.assertEqual(receipt['acceptance']['status'], 'passed')
        self.assertFalse(receipt['production'])
        self.assertFalse(receipt['consensus_eligible'])
        # Default historical checks must still reject an explicitly supplied
        # new block when it declares weaker recovery semantics.
        bad = (report + '\n' + block).replace('"operator": "all_of"', '"operator": "any_of"')
        with self.assertRaisesRegex(ValueError, 'ALL active'):
            contract.validate_experiment(bad, result)

    def test_experiment_review_cannot_disagree_with_new_shared_r14_gate(self):
        from scripts import research_acceptance
        result, review = fixture()
        review['r14'].update(applicability='applicable', stress_test='passed')
        block = research_acceptance.render_block(self.shared_acceptance(result), result['audit'])
        with self.assertRaisesRegex(ValueError, 'experiment/shared acceptance mismatch'):
            contract.validate_experiment(report_for(result, review) + '\n' + block, result)

    def test_shared_gate_rejects_actual_majority_recovery_wording_without_rewriting_it(self):
        from scripts import research_acceptance
        result, review = fixture()
        report = (report_for(result, review) + '\n'
                  + research_acceptance.render_block(self.shared_acceptance(result), result['audit'])
                  + '\n现价≤P1，且上述1-5项至少大部分解除；价格不是唯一条件。')
        original = report
        with self.assertRaisesRegex(ValueError, 'subset/majority'):
            contract.validate_experiment(report, result, require_acceptance=True)
        self.assertEqual(report, original)

    def test_neutral_roundtrip_reuses_arithmetic_without_mutation(self):
        result, review = fixture()
        original = deepcopy((result, review))
        receipt = contract.validate_experiment(report_for(result, review), result)
        self.assertEqual(receipt['status'], 'passed')
        self.assertTrue(receipt['semantic_source_review_required'])
        self.assertFalse(receipt['production'])
        self.assertFalse(receipt['consensus_eligible'])
        self.assertEqual((result, review), original)
        self.assertNotIn('generator', result['audit']['identity'])
        self.assertNotIn('meta', result)

    def test_legacy_outer_and_hidden_generator_fail(self):
        for mutate in (lambda result: result.update(schema_version='stock-research/v4'),
                       lambda result: result.update(generator='dsh'),
                       lambda result: result['audit']['identity'].update(generator='codex')):
            result, _ = fixture()
            mutate(result)
            with self.subTest(result=result.keys()), self.assertRaises(ValueError):
                contract.validation_projection(result)

    def test_baseline_forbidden_prevents_untrusted_filesystem_read(self):
        result, _ = fixture()
        result['audit']['baseline'] = dict(report_path='/private/secret', sha256='0' * 64, discounts={})
        with self.assertRaisesRegex(ValueError, 'baseline=null'):
            contract.validation_projection(result)

    def test_identity_currency_and_future_monitoring_reuse_formal_guards(self):
        for key, value in [('code', '00700.HK'), ('currency', 'USD'), ('valuation_date', 'not-date')]:
            result, review = fixture()
            result[key] = value
            result['audit']['identity'][key] = value
            with self.subTest(key=key), self.assertRaises((ValueError, TypeError)):
                report_for(result, review)
        result, review = fixture()
        result['monitoring'][0].update(current=1, as_of='2026-10-22')
        with self.assertRaisesRegex(ValueError, 'future observation'):
            report_for(result, review)

    def test_named_scenarios_and_profit_unit_arithmetic_are_not_waived(self):
        for mutate in (lambda result: result['audit']['valuation'].update(scenarios=[]),
                       lambda result: result['audit']['valuation'].update(amount_unit='thousand'),
                       lambda result: result['audit']['valuation']['scenarios']['base'].update(profit=25)):
            result, review = fixture()
            mutate(result)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):
                report_for(result, review)

    def test_quote_and_risk_ownership_are_not_recomputed_or_repaired(self):
        result, review = fixture()
        result['price_map']['p1']['base'] = 13
        with self.assertRaisesRegex(ValueError, 'P1 formula'):
            report_for(result, review)
        self.assertEqual(result['price_map']['p1']['base'], 13)
        result, review = fixture()
        result['audit']['risks'][0]['owner'] = 'margin'
        with self.assertRaisesRegex(ValueError, 'already absorbed'):
            report_for(result, review)

    def test_report_audit_and_delivery_summary_must_match_exactly(self):
        result, review = fixture()
        report = report_for(result, review)
        report = report.replace('"action": "review"', '"action": "raise discount"')
        with self.assertRaisesRegex(ValueError, 'result.monitoring'):
            contract.validate_experiment(report, result)
        report = report_for(result, review).replace('"profit_basis": "offline recurring', '"profit_basis": "changed recurring')
        with self.assertRaisesRegex(ValueError, 'audit differs'):
            contract.validate_experiment(report, result)

    def test_visible_calculations_must_match_and_sections_must_be_unique(self):
        result, review = fixture()
        report = report_for(result, review)
        with self.assertRaisesRegex(ValueError, 'visible calculation view differs'):
            contract.validate_experiment(report.replace('| base | 100 |', '| base | 405 |'), result)
        with self.assertRaisesRegex(ValueError, 'ordered sections'):
            contract.validate_experiment(report + '\n## 8. duplicate', result)
        with self.assertRaisesRegex(ValueError, 'ordered sections'):
            contract.validate_experiment(report.replace('## 0. offline section', '## 9. missing'), result)
        with self.assertRaisesRegex(ValueError, 'ordered sections'):
            contract.validate_experiment(report + '\n## 9. extra', result)

    def test_precheck_caution_requires_the_declared_upper_without_new_constant(self):
        result, review = fixture()
        review['precheck'].update(state='caution', d_base_upper_required=False)
        with self.assertRaisesRegex(ValueError, 'caution requires upper'):
            report_for(result, review)
        review['precheck']['d_base_upper_required'] = True
        # The actual existing offline range [.4,.5] controls the assertion.
        contract.validate_experiment(report_for(result, review), result)
        result['audit']['discounts']['d_base'].update(range=[.4, .6])
        with self.assertRaisesRegex(ValueError, 'declared d_base range upper'):
            report_for(result, review)

    def test_r14_unknown_required_stress_cannot_be_exempted_or_clear_add(self):
        result, review = fixture()
        review['r14'].update(applicability='applicable', stress_test='unknown')
        with self.assertRaisesRegex(ValueError, 'requires constraint IDs'):
            report_for(result, review)
        add_rule(result, 'R14_STRESS', ['add'])
        review['r14']['constraint_ids'] = ['R14_STRESS']
        contract.validate_experiment(report_for(result, review), result)
        review['r14']['stress_test'] = 'not_applicable'
        with self.assertRaisesRegex(ValueError, 'cannot be exempted'):
            report_for(result, review)

    def test_r14_uncertain_applicability_cannot_claim_pass(self):
        result, review = fixture()
        review['r14'].update(applicability='unknown', stress_test='passed')
        with self.assertRaisesRegex(ValueError, 'cannot declare pass/fail'):
            report_for(result, review)

    def test_r14_failure_and_holding_review_keep_separate_scopes(self):
        result, review = fixture()
        add_rule(result, 'R14_STRESS', ['add'], status='blocking')
        add_rule(result, 'CASH_REVIEW', ['holding'], action='review_holding', status='blocking')
        review['r14'].update(applicability='applicable', stress_test='failed', constraint_ids=['R14_STRESS'])
        review['holding'].update(review_status='pending', constraint_ids=['CASH_REVIEW'])
        contract.validate_experiment(report_for(result, review), result)
        self.assertNotIn('CASH_REVIEW', result['research_controls']['entry']['refs'])

    def test_original_d5_path_independent_and_r21_not_full_release(self):
        for field, value, error in [('original_rebuild_independent', False, 'remain independent'),
                                    ('r21_exit_is_full_clearance', True, 'not D5 full clearance')]:
            result, review = fixture()
            review['d5'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, error):
                report_for(result, review)

    def test_r9_verified_yield_benchmark_must_use_comparable_currency(self):
        result, review = fixture()
        review['r9'].update(applicability='applicable', benchmark_status='verified', benchmark_currency='USD')
        with self.assertRaisesRegex(ValueError, 'comparable quote/benchmark currency'):
            report_for(result, review)
        review['r9']['benchmark_currency'] = 'CNY'
        contract.validate_experiment(report_for(result, review), result)

    def test_r9_missing_benchmark_preserves_both_scopes_with_separate_ids(self):
        result, review = fixture()
        add_rule(result, 'R9_ENTRY', ['entry'])
        # add_rule inserted OTHER_ADD to keep tracking coherent; retain it as
        # a distinct frozen-input qualifier, then add a separate R9 add claim.
        add_rule(result, 'R9_ADD', ['add'])
        review['r9'].update(applicability='applicable', benchmark_status='unknown',
                            constraint_ids=['R9_ENTRY', 'R9_ADD'])
        contract.validate_experiment(report_for(result, review), result)
        review['r9']['constraint_ids'] = ['R9_ADD']
        with self.assertRaisesRegex(ValueError, 'unresolved entry scope'):
            report_for(result, review)

    def test_holding_triggered_requires_current_persistent_review_not_observation(self):
        result, review = fixture()
        review['holding'].update(review_status='pending')
        with self.assertRaisesRegex(ValueError, 'requires constraint IDs'):
            report_for(result, review)
        add_rule(result, 'CASH_REVIEW', ['holding'], action='review_holding', status='blocking')
        review['holding']['constraint_ids'] = ['CASH_REVIEW']
        contract.validate_experiment(report_for(result, review), result)
        result['audit']['constraints'][0]['lifecycle'] = 'observation'
        with self.assertRaises(ValueError):
            report_for(result, review)

    def test_current_holding_review_may_complete_with_evidence_without_perpetual_debt(self):
        result, review = fixture()
        review['holding'].update(review_status='completed', constraint_ids=['CASH_REVIEW'])
        result['audit']['constraints'].append(dict(id='CASH_REVIEW', scope=['holding'],
            action='review_holding', status='clear', lifecycle='persistent',
            reason='offline completed review', release_conditions=['verify evidence'],
            clearance=dict(evidence=['offline original source and current review'])))
        contract.validate_experiment(report_for(result, review), result)
        self.assertEqual(result['research_controls']['holding']['status'], 'normal')
        result['audit']['constraints'][0]['clearance']['evidence'] = []
        with self.assertRaises(ValueError):
            report_for(result, review)

    def test_new_constraints_require_explicit_lifecycle(self):
        result, review = fixture()
        add_rule(result, 'CASH_REVIEW', ['holding'], action='review_holding')
        report = report_for(result, review)
        result['audit']['constraints'][0].pop('lifecycle')
        with self.assertRaisesRegex(ValueError, 'explicit lifecycle'):
            contract.validate_experiment(report, result)

    def test_duplicate_nonfinite_and_malformed_blocks_fail(self):
        for text in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                contract.loads_strict(text)
        result, review = fixture()
        report = report_for(result, review)
        for bad in [report.replace(contract.END, ''), report + '\n' + contract.START,
                    report.replace('```json\n', '```text\n')]:
            with self.subTest(report=bad[-80:]), self.assertRaises(ValueError):
                contract.validate_experiment(bad, result)

    def test_native_float_normalization_never_rounds_existing_decimal_input(self):
        value = Decimal('0.1234567890123456789012345')
        self.assertEqual(contract._decimal_json_values({'x': value})['x'], value)
        self.assertEqual(contract._decimal_json_values({'x': .4})['x'], Decimal('.4'))
        for value in (float('nan'), Decimal('Infinity')):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'finite'):
                contract._decimal_json_values({'x': value})

    def test_read_only_files_bound_and_symlinks_fifo_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result, review = fixture()
            report_path, result_path = root / 'report.md', root / 'result.json'
            report_path.write_text(report_for(result, review))
            result_path.write_text(json.dumps(result))
            before = {path.name: path.read_bytes() for path in (report_path, result_path)}
            self.assertEqual(contract.check_delivery(report_path, result_path)['status'], 'passed')
            self.assertEqual(before, {path.name: path.read_bytes() for path in (report_path, result_path)})
            link = root / 'alias'
            link.symlink_to(report_path)
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                contract.read_regular(link)
            parent_link = root / 'parent'
            parent_link.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                contract.read_regular(parent_link / 'report.md')
            fifo = root / 'fifo'
            os.mkfifo(fifo)
            with self.assertRaisesRegex(ValueError, 'bounded regular'):
                contract.read_regular(fifo)
            with self.assertRaisesRegex(ValueError, 'bounded regular'):
                contract.read_regular(report_path, max_bytes=1)

    def test_cli_check_is_offline_and_does_not_create_production_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            result, review = fixture()
            (root / 'report.md').write_text(report_for(result, review))
            (root / 'result.json').write_text(json.dumps(result))
            process = subprocess.run([sys.executable, str(ROOT / 'scripts/research_experiment_contract.py'),
                'check', '--report', str(root / 'report.md'), '--result', str(root / 'result.json')],
                text=True, capture_output=True, timeout=10)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout)['status'], 'passed')
            self.assertEqual({path.name for path in root.iterdir()}, {'report.md', 'result.json'})


if __name__ == '__main__':
    unittest.main()
