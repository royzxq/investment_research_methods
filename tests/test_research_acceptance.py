"""Offline acceptance counterexamples; no model calls or investment calibration."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from scripts import research_acceptance as acceptance
from scripts import research_consistency as consistency
from scripts import stock_price_map as prices
from research_audit_fixture import audit_for


def fixture():
    document = prices.build_document(dict(
        meta=dict(code='600066.SH', name='offline acceptance fixture',
                  valuation_date='2026-10-18', currency='CNY', generator='codex',
                  report_path='research/offline.md'),
        mode='buy_candidate', reason=None,
        valuation=dict(kind='per_share', values=dict(low=20, base=24, high=30),
                       currency='CNY', unit='per_share', fx_to_quote=1),
        p1=dict(base=12), t1=dict(price_condition='股价≥30元/股'),
        research_controls=dict(entry=dict(status='eligible', refs=[]),
                               add=dict(status='eligible', refs=[]),
                               holding=dict(status='normal', refs=[])),
        monitoring=[dict(id='income', kind='general', state='watching', variable='income',
                         current=None, as_of=None, trigger='falls', action='review',
                         source='offline fixture', next_check='next report')]))
    audit = audit_for(document)
    gate = dict(schema_version=acceptance.SCHEMA,
        r14=dict(applicability='not_applicable', stress_test='not_applicable',
                 constraint_ids=[], reason='Offline fixture has no applicable oil-cost exposure.',
                 inputs={key: dict(status='unknown', sources=[], derivation=None)
                         for key in acceptance.INPUTS}, calculation=None),
        recovery=dict(operator='all_of', scopes={scope: [] for scope in acceptance.SCOPES}))
    return document, audit, gate


def sync_controls(document, audit, gate):
    """Build a coherent fixture without making a missing blocker disappear."""
    for scope in acceptance.SCOPES:
        rows = [row for row in audit['constraints'] if scope in row['scope']
                and row['status'] in ('blocking', 'unknown')]
        identifiers = [row['id'] for row in rows]
        audit['release_all_of'][scope] = identifiers
        gate['recovery']['scopes'][scope] = identifiers[:]
        state = ('review_required' if rows else 'normal') if scope == 'holding' else (
            'blocked' if any(row['status'] == 'blocking' for row in rows)
            else 'unknown' if rows else 'eligible')
        document['research_controls'][scope] = dict(status=state, refs=identifiers[:])
    if any(row['status'] in ('blocking', 'unknown') and row['action'] == 'freeze'
           for row in audit['constraints']):
        document['price_map'].update(mode='frozen', reason='Offline independent freeze.')
    elif any(document['research_controls'][scope]['status'] == 'eligible' for scope in ('entry', 'add')):
        document['price_map'].update(mode='buy_candidate', reason=None)
    else:
        document['price_map'].update(mode='tracking', reason='Offline necessary evidence gaps.')


def add_rule(document, audit, gate, ident, scopes, *, status='unknown', reason=None,
             release_conditions=None, lifecycle='persistent', action='eligibility', clearance=None):
    rule = dict(id=ident, scope=list(scopes), status=status, action=action,
                reason=reason or 'Offline necessary evidence gap.',
                release_conditions=release_conditions or ['Verify this claim with original company evidence.'],
                lifecycle=lifecycle)
    if clearance is not None:
        rule['clearance'] = clearance
    audit['constraints'].append(rule)
    sync_controls(document, audit, gate)
    return rule


def report_for(document, audit, gate, *, prose='', untrusted=False, root=None):
    if untrusted:
        # An incoming report must be checked even if its author bypassed render.
        audit_block = consistency.render_checks(audit, document) + '\n' + consistency.START + '\n```json\n' + json.dumps(audit) + '\n```\n' + consistency.END
        gate_block = acceptance.render_view(gate, audit) + '\n' + acceptance.START + '\n```json\n' + json.dumps(gate) + '\n```\n' + acceptance.END
    else:
        audit_block = consistency.render_report_block(audit, document, root=root)
        gate_block = acceptance.render_block(gate, audit, root=root)
    return prose + '\n\n' + audit_block + '\n\n' + gate_block


class ResearchAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source_root = Path(self.temporary.name)
        self.quotes = dict(
            exposure='Company production uses purchased oil-linked inputs.',
            cost_exposure='The disclosed cost schedule bounds oil-linked inputs at ten units.',
            pass_through='Contract terms fix pass-through at zero for the modeled period.',
            ocf_bridge='Company cash-flow bridge: opening operating cash flow 100, incremental stress cost 3, ending 97.')
        self.source = self.source_root / 'evidence' / 'company.txt'
        self.source.parent.mkdir()
        self.source.write_text('\n'.join(self.quotes.values()) + '\n', encoding='utf-8')
        self.source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.calculation_quote = '100→130 美元压力下，同期 OCF 从 100 经成本桥接为 97；仅为离线合同样例。'

    def supported(self):
        document, audit, gate = fixture()
        r14 = gate['r14']
        r14.update(applicability='applicable', stress_test='passed',
                   reason='Offline source-tied company stress exercise.',
                   calculation=dict(scenario='Existing canonical 100→130 美元 pressure scenario.',
                                    report_quote=self.calculation_quote))
        for key in acceptance.INPUTS:
            r14['inputs'][key] = dict(status='supported', derivation=None,
                sources=[dict(path='evidence/company.txt', sha256=self.source_hash,
                              quote=self.quotes[key], as_of='2026-10-17')])
        r14['inputs']['ocf_bridge']['derivation'] = 'Use the same modeled period: source OCF 100 less incremental stress cost 3 equals 97.'
        return document, audit, gate

    def validate(self, document, audit, gate, *, prose=None, untrusted=False):
        if prose is None:
            prose = self.calculation_quote if gate['r14']['calculation'] else ''
        report = report_for(document, audit, gate, prose=prose, untrusted=untrusted, root=self.source_root)
        return consistency.validate_report(report, document, root=self.source_root,
                                           require_lifecycle=True, require_acceptance=True)

    def test_source_bound_pass_and_render_round_trip_do_not_mutate_inputs(self):
        document, audit, gate = self.supported()
        before = deepcopy((document, audit, gate))
        checked = self.validate(document, audit, gate)
        self.assertEqual(checked['acceptance']['status'], 'passed')
        self.assertTrue(checked['acceptance']['semantic_source_review_required'])
        self.assertEqual((document, audit, gate), before)

    def test_company_source_derived_conservative_bound_remains_admissible(self):
        document, audit, gate = self.supported()
        gate['r14']['inputs']['cost_exposure'].update(status='bounded',
            derivation='Sum the company cost schedule without offset; include all potentially oil-linked rows.')
        self.assertEqual(self.validate(document, audit, gate)['acceptance']['status'], 'passed')
        gate['r14']['inputs']['cost_exposure']['derivation'] = None
        with self.assertRaisesRegex(ValueError, 'bound requires bridge'):
            self.validate(document, audit, gate, untrusted=True)

    def test_missing_evidence_or_arbitrary_assumption_cannot_prove_pass(self):
        for key in acceptance.INPUTS:
            for status in ('unknown', 'assumption'):
                with self.subTest(input=key, status=status):
                    document, audit, gate = self.supported()
                    gate['r14']['inputs'][key] = dict(status=status, sources=[],
                        derivation='Arbitrary sensitivity hypothesis; not independently supported.')
                    with self.assertRaisesRegex(ValueError, 'missing evidence / arbitrary assumption'):
                        self.validate(document, audit, gate, untrusted=True)

    def test_claiming_supported_without_a_bound_source_also_fails(self):
        for status in ('supported', 'bounded'):
            document, audit, gate = self.supported()
            gate['r14']['inputs']['ocf_bridge'].update(status=status, sources=[], derivation='Estimated 800.')
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, 'requires source evidence'):
                self.validate(document, audit, gate, untrusted=True)

    def test_source_hash_quote_and_date_are_verified_not_merely_declared(self):
        mutations = (
            ('sha256', '0' * 64, 'hash mismatch'),
            ('quote', 'A sentence absent from the immutable company extract.', 'quote absent'),
            ('as_of', '2026-10-19', 'later than valuation cutoff'),
            ('as_of', '2026-02-30', 'date invalid'),
            ('as_of', '2026-1-2', 'ISO date'))
        for field, value, error in mutations:
            document, audit, gate = self.supported()
            gate['r14']['inputs']['exposure']['sources'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, error):
                self.validate(document, audit, gate, untrusted=True)

    def test_source_change_cannot_reuse_the_previously_bound_hash(self):
        document, audit, gate = self.supported()
        self.source.write_text('Replaced company source.', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.validate(document, audit, gate, untrusted=True)

    def test_sources_cannot_escape_root_or_substitute_symlinks(self):
        for path in ('../company.txt', str(self.source)):
            document, audit, gate = self.supported()
            gate['r14']['inputs']['exposure']['sources'][0]['path'] = path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'repository relative'):
                self.validate(document, audit, gate, untrusted=True)
        link = self.source_root / 'link.txt'
        link.symlink_to(self.source)
        document, audit, gate = self.supported()
        gate['r14']['inputs']['exposure']['sources'][0]['path'] = 'link.txt'
        with self.assertRaisesRegex(ValueError, 'symlinks forbidden'):
            self.validate(document, audit, gate, untrusted=True)

    def test_pdf_bytes_need_an_explicit_utf8_extract_not_a_false_text_quote(self):
        source = self.source_root / 'evidence' / 'binary.pdf'
        source.write_bytes(b'%PDF\xff\x00')
        document, audit, gate = self.supported()
        gate['r14']['inputs']['exposure']['sources'][0].update(path='evidence/binary.pdf',
            sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        with self.assertRaisesRegex(ValueError, 'UTF-8 extract'):
            self.validate(document, audit, gate, untrusted=True)

    def test_pass_requires_a_calculation_in_actual_prose_not_its_json_copy(self):
        document, audit, gate = self.supported()
        with self.assertRaisesRegex(ValueError, 'quote absent from report prose'):
            self.validate(document, audit, gate, prose='', untrusted=True)
        gate['r14']['calculation'] = None
        with self.assertRaisesRegex(ValueError, 'passed requires explicit stress calculation'):
            self.validate(document, audit, gate, untrusted=True)

    def test_generated_acceptance_and_audit_views_are_not_calculation_evidence(self):
        for quote in ('R14：applicable / passed。', '| exposure | supported |',
                      '| entry | eligible | 无 |'):
            with self.subTest(quote=quote):
                document, audit, gate = self.supported()
                gate['r14']['calculation']['report_quote'] = quote
                with self.assertRaisesRegex(ValueError, 'quote absent from report prose'):
                    self.validate(document, audit, gate, prose='', untrusted=True)

    def test_calculation_copied_into_audit_still_requires_independent_report_prose(self):
        document, audit, gate = self.supported()
        audit['valuation'] = dict(kind='other', reason=self.calculation_quote,
                                 unrounded_v50=deepcopy(document['price_map']['v50']))
        with self.assertRaisesRegex(ValueError, 'quote absent from report prose'):
            self.validate(document, audit, gate, prose='', untrusted=True)
        self.assertEqual(self.validate(document, audit, gate)['acceptance']['status'], 'passed')

    def test_an_unexplained_ocf_base_does_not_become_a_source_tied_bridge(self):
        document, audit, gate = self.supported()
        gate['r14']['inputs']['ocf_bridge']['derivation'] = None
        with self.assertRaisesRegex(ValueError, 'cash-flow/survival bridge'):
            self.validate(document, audit, gate, untrusted=True)

    def test_a_hidden_html_comment_is_not_the_actual_prose_calculation(self):
        document, audit, gate = self.supported()
        with self.assertRaisesRegex(ValueError, 'quote absent from report prose'):
            self.validate(document, audit, gate, prose='<!-- ' + self.calculation_quote + ' -->', untrusted=True)

    def test_r14_unknown_retains_only_its_add_scope_without_freezing_entry(self):
        document, audit, gate = fixture()
        rule = add_rule(document, audit, gate, 'COMPANY_COST', ['add'],
                        reason='R14 company cost exposure is unknown.')
        gate['r14'].update(applicability='applicable', stress_test='unknown', constraint_ids=[rule['id']])
        checked = self.validate(document, audit, gate)
        self.assertEqual(checked['unresolved_constraints'], dict(entry=[], add=['COMPANY_COST'], holding=[]))
        self.assertEqual(document['research_controls']['entry'], dict(status='eligible', refs=[]))
        self.assertEqual(document['research_controls']['add'], dict(status='unknown', refs=['COMPANY_COST']))

    def test_unknown_cannot_be_erased_because_an_unrelated_freeze_already_blocks_add(self):
        document, audit, gate = fixture()
        add_rule(document, audit, gate, 'OTHER', ['entry', 'add'], status='blocking', action='freeze',
                 reason='Independent market restriction.')
        gate['r14'].update(applicability='applicable', stress_test='unknown', constraint_ids=[])
        with self.assertRaisesRegex(ValueError, 'requires persistent add constraint'):
            self.validate(document, audit, gate, untrusted=True)
        gate['r14']['constraint_ids'] = ['OTHER']
        with self.assertRaisesRegex(ValueError, 'own R14 claim'):
            self.validate(document, audit, gate, untrusted=True)

    def test_unknown_r14_cannot_bind_runtime_observation_or_holding_only_gap(self):
        for mutation in ('runtime', 'observation', 'holding_only', 'clear'):
            document, audit, gate = fixture()
            rule = add_rule(document, audit, gate, 'R14_GAP', ['add'], reason='R14 necessary evidence missing.')
            gate['r14'].update(applicability='unknown', stress_test='unknown', constraint_ids=['R14_GAP'])
            if mutation in ('runtime', 'observation'):
                rule['lifecycle'] = mutation
            elif mutation == 'holding_only':
                rule.update(scope=['holding'], action='review_holding')
            else:
                rule.update(status='clear', clearance=dict(evidence=['Completed source review.']))
            sync_controls(document, audit, gate)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.validate(document, audit, gate, untrusted=True)

    def test_confirmed_failed_r14_is_blocking_and_does_not_become_eligible(self):
        document, audit, gate = fixture()
        rule = add_rule(document, audit, gate, 'OIL_STRESS', ['add'], status='blocking',
                        reason='R14 verified stress failed; cancel this addition.')
        gate['r14'].update(applicability='applicable', stress_test='failed', constraint_ids=[rule['id']])
        self.validate(document, audit, gate)
        self.assertEqual(document['research_controls']['add']['status'], 'blocked')
        rule['status'] = 'unknown'
        sync_controls(document, audit, gate)
        with self.assertRaisesRegex(ValueError, 'confirmed add restriction'):
            self.validate(document, audit, gate, untrusted=True)

    def test_uncertain_applicability_cannot_claim_pass_or_exemption(self):
        for state in ('passed', 'failed', 'not_applicable'):
            document, audit, gate = self.supported()
            gate['r14'].update(applicability='unknown', stress_test=state)
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.validate(document, audit, gate, untrusted=True)

    def test_first_not_applicable_is_accepted_but_not_as_a_release_of_active_r14(self):
        document, audit, gate = fixture()
        self.validate(document, audit, gate)
        add_rule(document, audit, gate, 'OIL_STRESS', ['add'], reason='R14 existing necessary evidence gap.')
        with self.assertRaisesRegex(ValueError, 'contradicts active R14 evidence gap'):
            self.validate(document, audit, gate, untrusted=True)

    def test_pass_must_not_conceal_an_active_r14_gap_or_clear_it_without_evidence(self):
        document, audit, gate = self.supported()
        rule = add_rule(document, audit, gate, 'OIL_STRESS', ['add'], reason='R14 unresolved company input.')
        with self.assertRaisesRegex(ValueError, 'contradicts active R14 evidence gap'):
            self.validate(document, audit, gate, untrusted=True)
        rule.update(status='clear', clearance=dict(evidence=['Company evidence verified and stress recalculated.']))
        gate['r14']['constraint_ids'] = ['OIL_STRESS']
        sync_controls(document, audit, gate)
        self.validate(document, audit, gate)
        rule['clearance']['evidence'] = []
        with self.assertRaises(ValueError):
            self.validate(document, audit, gate, untrusted=True)

    def test_all_independent_blockers_and_unknowns_are_exactly_scoped(self):
        document, audit, gate = fixture()
        add_rule(document, audit, gate, 'ENTRY', ['entry'], status='blocking')
        add_rule(document, audit, gate, 'SHARED', ['entry', 'add'])
        add_rule(document, audit, gate, 'HOLDING', ['holding'], action='review_holding')
        self.validate(document, audit, gate)
        expected = dict(entry=['ENTRY', 'SHARED'], add=['SHARED'], holding=['HOLDING'])
        self.assertEqual(gate['recovery']['scopes'], expected)
        for scope in acceptance.SCOPES:
            bad = deepcopy(gate)
            bad['recovery']['scopes'][scope].pop()
            with self.subTest(scope=scope), self.assertRaisesRegex(ValueError, 'ALL active constraints'):
                self.validate(document, audit, bad, untrusted=True)

    def test_one_cleared_claim_cannot_release_a_remaining_unknown_claim(self):
        document, audit, gate = fixture()
        add_rule(document, audit, gate, 'FIRST', ['add'], status='clear',
                 clearance=dict(evidence=['First independent condition verified.']))
        add_rule(document, audit, gate, 'SECOND', ['add'])
        self.validate(document, audit, gate)
        self.assertEqual(document['research_controls']['add']['status'], 'unknown')
        gate['recovery']['scopes']['add'] = []
        with self.assertRaisesRegex(ValueError, 'ALL active constraints'):
            self.validate(document, audit, gate, untrusted=True)

    def test_all_independent_evidenced_clearances_allow_recovery(self):
        document, audit, gate = fixture()
        for ident in ('FIRST', 'SECOND'):
            add_rule(document, audit, gate, ident, ['entry', 'add'], status='clear',
                     clearance=dict(evidence=['Offline original evidence for ' + ident]))
        self.validate(document, audit, gate)
        self.assertEqual(gate['recovery']['scopes'], dict(entry=[], add=[], holding=[]))
        for scope in ('entry', 'add'):
            self.assertEqual(document['research_controls'][scope], dict(status='eligible', refs=[]))

    def test_recovery_rejects_any_of_majority_duplicates_and_wrong_scope(self):
        document, audit, gate = fixture()
        add_rule(document, audit, gate, 'A', ['add'])
        for operator in ('any_of', 'majority', 'all'):
            bad = deepcopy(gate)
            bad['recovery']['operator'] = operator
            with self.subTest(operator=operator), self.assertRaisesRegex(ValueError, 'ALL active independent'):
                self.validate(document, audit, bad, untrusted=True)
        for scopes in (dict(entry=['A'], add=['A'], holding=[]),
                       dict(entry=[], add=['A', 'A'], holding=[])):
            bad = deepcopy(gate)
            bad['recovery']['scopes'] = scopes
            with self.subTest(scopes=scopes), self.assertRaises(ValueError):
                self.validate(document, audit, bad, untrusted=True)

    def test_internal_legal_or_is_not_changed_into_all_paths_required(self):
        document, audit, gate = fixture()
        rule = add_rule(document, audit, gate, 'INTERNAL_OR', ['add'],
                        release_conditions=['Company-supported alternative path A OR company-supported alternative path B.'])
        before = deepcopy(rule['release_conditions'])
        self.validate(document, audit, gate,
            prose='同一约束内部任一合法替代条件完成后可解除该项约束，其它独立约束仍须全部解除。')
        acceptance.validate_recovery_prose(
            'D5 的两个合法替代条件中任一条件满足即可解除 D5 约束，全部其它独立约束仍须逐项解除。')
        self.assertEqual(rule['release_conditions'], before)

    def test_holding_unknown_and_watch_conditions_do_not_create_exposure_debt(self):
        document, audit, gate = fixture()
        add_rule(document, audit, gate, 'HOLD', ['holding'], action='review_holding')
        add_rule(document, audit, gate, 'WATCH', ['add'], status='not_applicable', lifecycle='observation')
        add_rule(document, audit, gate, 'PRICE', ['entry'], status='not_applicable', lifecycle='runtime')
        self.validate(document, audit, gate)
        self.assertEqual(gate['recovery']['scopes'], dict(entry=[], add=[], holding=['HOLD']))
        self.assertEqual(document['research_controls']['entry']['status'], 'eligible')
        self.assertEqual(document['research_controls']['add']['status'], 'eligible')

    def test_actual_majority_recovery_counterexample_fails_even_with_correct_json(self):
        document, audit, gate = fixture()
        add_rule(document, audit, gate, 'A', ['add'])
        add_rule(document, audit, gate, 'B', ['add'], status='blocking')
        prose = '价格：现价 ≤ P1，且上述 1-5 项至少大部分解除；价格不是唯一条件，不能单独触发。'
        with self.assertRaisesRegex(ValueError, 'subset/majority clearance'):
            self.validate(document, audit, gate, prose=prose, untrusted=True)

    def test_explicit_prohibitions_are_allowed(self):
        for prose in (
            '不得在约束仅大部分解除后恢复研究资格。',
            '只解除部分条件不足以恢复研究资格，必须解除全部有效独立约束。',
            'Clearing most constraints cannot resume eligibility.',
            '解除任一约束不代表可以恢复资格。'):
            with self.subTest(prose=prose):
                acceptance.validate_recovery_prose(prose)

    def test_negated_prefix_does_not_license_a_later_affirmative_subset_recovery(self):
        for prose in (
            '不得仅靠价格恢复，但上述约束大部分解除即可恢复。',
            '不能冒进，不过多数约束解除后可以恢复。',
            'Never ignore risk, but any one blocker cleared allows resume.',
            '多数约束解除并非不允许恢复研究资格。',
            '各独立约束中任一条件解除即可恢复且 D5 的两个合法替代条件中任一条件满足即可解除 D5 约束。',
            '同一约束内部任一合法替代条件完成后可解除该项约束，但其它约束大部分解除就恢复。'):
            with self.subTest(prose=prose), self.assertRaisesRegex(ValueError, 'subset/majority clearance'):
                acceptance.validate_recovery_prose(prose)

    def test_unrelated_negated_caution_prefix_does_not_negate_subset_permission(self):
        for prose in ('不能冒进：大部分约束解除即可恢复。',
                      'Not rashly: most constraints cleared allow resume.'):
            with self.subTest(prose=prose), self.assertRaisesRegex(ValueError, 'subset/majority clearance'):
                acceptance.validate_recovery_prose(prose)

    def test_markdown_unicode_and_zero_width_characters_cannot_hide_subset_recovery(self):
        for prose in (
            '**上述约束大部分解除即可恢复。**',
            '上述约束大\u200b部分解除即可恢复。',
            'Ｍｏｓｔ constraints cleared allow resume.'):
            with self.subTest(prose=prose), self.assertRaisesRegex(ValueError, 'subset/majority clearance'):
                acceptance.validate_recovery_prose(prose)

    def test_legacy_without_new_block_remains_readable_until_strict_gate_requested(self):
        document, audit, _ = fixture()
        legacy_report = consistency.render_report_block(audit, document) + '\n历史正文：上述约束大部分解除即可恢复。'
        checked = consistency.validate_report(legacy_report, document)
        self.assertEqual(checked['status'], 'passed')
        self.assertNotIn('acceptance', checked)
        with self.assertRaisesRegex(ValueError, 'acceptance block'):
            consistency.validate_report(legacy_report, document, require_acceptance=True)

    def test_legacy_audit_v1_remains_readable_without_rewriting_history(self):
        document, _, _ = fixture()
        document['meta']['schema_version'] = 'stock-research/v3'
        document.pop('research_controls')
        document['price_map']['p2'] = dict(status='cancelled', price=None, reason='Historical no addition quote.')
        document['price_map']['t1']['events'] = ['Historical review.']
        document['price_map']['t2'] = dict(price_condition='历史退出观察条件', events=['Historical failure review.'])
        for row in document['monitoring']:
            for key in ('id', 'kind', 'state'):
                row.pop(key)
        audit = audit_for(document)
        report = consistency.render_report_block(audit, document)
        before = deepcopy((document, audit, report))
        self.assertEqual(consistency.validate_report(report, document)['schema_version'], 'stock-research-audit/v1')
        self.assertEqual((document, audit, report), before)
        with self.assertRaisesRegex(ValueError, 'acceptance block'):
            consistency.validate_report(report, document, require_acceptance=True)

    def test_explicit_new_block_is_not_ignored_by_legacy_default_check(self):
        document, audit, gate = self.supported()
        gate['r14']['inputs']['ocf_bridge'] = dict(status='assumption', sources=[], derivation='Unverified 800.')
        report = report_for(document, audit, gate, prose=self.calculation_quote, untrusted=True)
        with self.assertRaisesRegex(ValueError, 'missing evidence / arbitrary assumption'):
            consistency.validate_report(report, document, root=self.source_root)
        legacy = consistency.render_report_block(audit, document)
        for marker in (acceptance.START, acceptance.END):
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, 'acceptance block'):
                consistency.validate_report(legacy + '\n' + marker, document)

    def test_new_block_and_visible_recovery_view_cannot_be_duplicated_or_changed(self):
        document, audit, gate = fixture()
        report = report_for(document, audit, gate)
        variants = (
            (report + '\n' + acceptance.START + '\n' + acceptance.END, 'one complete acceptance block'),
            (report + '\n' + acceptance.VIEW_START + '\n' + acceptance.VIEW_END, 'one visible acceptance view'),
            (report.replace('各范围全部有效约束解除后才可恢复研究资格', '大部分约束解除后可恢复资格'), 'visible recovery view mismatch'))
        for changed, error in variants:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                consistency.validate_report(changed, document)

    def test_derived_isolation_refreshes_all_scopes_and_preserves_source_report(self):
        document, audit, gate = fixture()
        source = report_for(document, audit, gate)
        source_digest = hashlib.sha256(source.encode()).hexdigest()
        isolated_document = deepcopy(document)
        isolated_document['price_map'].update(mode='frozen', reason='Method compatibility pending.')
        for scope in ('entry', 'add'):
            isolated_document['research_controls'][scope] = dict(status='blocked', refs=['METHOD_COMPATIBILITY'])
        derived = consistency.isolate_report(source, isolated_document)
        checked = consistency.validate_report(derived, isolated_document, require_acceptance=True)
        self.assertEqual(checked['acceptance']['status'], 'passed')
        refreshed = acceptance.extract(derived)
        self.assertEqual(refreshed['recovery']['scopes'],
                         dict(entry=['METHOD_COMPATIBILITY'], add=['METHOD_COMPATIBILITY'], holding=[]))
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), source_digest)
        self.assertNotIn('METHOD_COMPATIBILITY', source)
        self.assertEqual(acceptance.extract(source)['recovery']['scopes'], dict(entry=[], add=[], holding=[]))


if __name__ == '__main__':
    unittest.main()
