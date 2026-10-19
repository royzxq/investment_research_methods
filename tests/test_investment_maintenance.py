import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import investment_maintenance as maintenance


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'framework').mkdir()
        for name in ('investment_framework.md', 'investment_framework_compact.md'):
            (self.root / 'framework' / name).write_text('adopted rules: threshold > 3\n')

    def state_doc(self, value=10):
        state = {'schema': 'investment-state/v1', 'as_of': '2026-10-11',
                 'evidence_cutoff': '2026-10-11', 'source_report': None,
                 'observations': [{'id': 'turnover', 'value': value, 'unit': 'trillion',
                                   'observed_at': '2026-10-10', 'source': 'official', 'status': 'verified'}]}
        return ('rule threshold > 3\n' + maintenance.START + '\n```json\n' + json.dumps(state) + '\n```\n' + maintenance.END).encode()

    def package(self, day='2026-10-11', revision=None, status='adopted', supersedes=None):
        methods = maintenance.freeze_methods(self.root, day, revision)
        reports = {}
        for key, kind in [('market_research', 'market-research'), ('change_decision', 'change-decision')]:
            path = maintenance.weekly_path(self.root, day, kind, revision)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'{kind} {day} {revision}')
            reports[key] = maintenance.file_ref(self.root, path, as_of=day)
        changes = [{'kind': 'state_refresh', 'summary': 'Latest turnover observation'}]
        return {'schema': maintenance.SCHEMA, 'id': maintenance.weekly_path(self.root, day, 'handoff', revision).stem,
                'as_of': day, 'revision': revision, 'status': status, 'adoption_basis': 'explicit local review',
                'method_status': 'adopted', 'methods': methods, 'reports': reports,
                'classification': maintenance.classify_changes(changes), 'changes': changes,
                'supersedes': supersedes or [], 'reviews': [], 'rule_evaluations': []}

    def live_methods(self):
        return {key: maintenance.file_ref(self.root, 'framework/' + name) for key, name in
                [('canonical', 'investment_framework.md'), ('compact', 'investment_framework_compact.md')]}

    def test_state_changes_do_not_require_method_update(self):
        record = self.package()
        self.assertFalse(record['classification']['update_needed'])
        maintenance.write_handoff(self.root, record)
        self.assertEqual(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods())['record']['id'], record['id'])

    def test_correction_replaces_same_day_baseline(self):
        first = self.package()
        maintenance.write_handoff(self.root, first)
        correction = self.package(revision=2, supersedes=[first['id']])
        correction['changes'] = [{'kind': 'evidence_correction', 'summary': 'Correct false execution claim'}]
        correction['classification'] = maintenance.classify_changes(correction['changes'])
        maintenance.write_handoff(self.root, correction)
        self.assertFalse(correction['classification']['update_needed'])
        self.assertEqual(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods())['record']['revision'], 2)
        self.assertEqual(maintenance.next_revision(self.root, '2026-10-11'), 3)

    def test_proposed_latest_does_not_become_adopted(self):
        first = self.package('2026-10-10')
        maintenance.write_handoff(self.root, first)
        newer = self.package(status='proposed')
        maintenance.write_handoff(self.root, newer)
        result = maintenance.select_adopted(self.root, '2026-10-11', self.live_methods())
        self.assertEqual(result['record']['id'], first['id'])

    def test_proposal_cannot_supersede(self):
        proposal = self.package(status='proposed', supersedes=['historical'])
        with self.assertRaisesRegex(ValueError, 'proposal'):
            maintenance.validate_handoff(proposal, self.root)

    def test_legacy_report_requires_explicit_bridge(self):
        record = self.package()
        self.assertIsNone(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods()))
        maintenance.write_handoff(self.root, record)
        self.assertIsNotNone(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods()))

    def test_withdrawal_prevents_old_method_resurrection(self):
        first = self.package('2026-10-09')
        maintenance.write_handoff(self.root, first)
        old_methods = first['methods']
        (self.root / 'framework/investment_framework.md').write_text('changed threshold > 5')
        newer = self.package('2026-10-10', supersedes=[first['id']])
        maintenance.write_handoff(self.root, newer)
        self.assertIsNone(maintenance.select_adopted(self.root, '2026-10-11', old_methods))

    def test_withdrawn_evidence_cannot_reenter_new_package(self):
        first = self.package('2026-10-09')
        maintenance.write_handoff(self.root, first)
        withdrawn = self.package('2026-10-10', status='withdrawn', supersedes=[first['id']])
        withdrawn['withdrawn_sources'] = [first['reports']['market_research']]
        maintenance.write_handoff(self.root, withdrawn)
        mistaken = self.package()
        mistaken['evidence'] = [first['reports']['market_research']]
        maintenance.write_handoff(self.root, mistaken)
        self.assertIsNone(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods()))

    def test_future_nested_evidence_cannot_claim_asof(self):
        record = self.package()
        record['evidence'] = [dict(record['reports']['market_research'], as_of='2026-10-12')]
        with self.assertRaisesRegex(ValueError, 'future'):
            maintenance.validate_handoff(record, self.root)

    def test_future_compatibility_review_cannot_be_selected(self):
        record = self.package()
        future = dict(record['reports']['change_decision'], as_of='2026-10-12')
        record['compatibility'] = [{'status': 'adopted', 'reason': 'Claimed compatible',
                                    'methods': record['methods'], 'review': future}]
        path = maintenance.weekly_path(self.root, '2026-10-11', 'handoff')
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'future'):
            maintenance.select_adopted(self.root, '2026-10-11', self.live_methods())

    def test_future_or_non_iso_rule_evidence_cannot_be_adopted(self):
        for ref_date in ('2026-10-12', '20261011'):
            record = self.package()
            record['rule_evaluations'] = [{'rule_id': 'D5', 'rule_status': 'adopted',
                'as_of': '2026-10-11', 'result': 'triggered', 'affected_objects': ['HK-06886'],
                'evidence': [dict(record['reports']['market_research'], as_of=ref_date)]}]
            with self.subTest(as_of=ref_date), self.assertRaises(ValueError):
                maintenance.write_handoff(self.root, record)

    def test_decision_references_require_dates_in_every_supported_field(self):
        placements = ('evidence', 'withdrawn_sources', 'compatibility.review',
                      'rule_evaluations.evidence', 'reviews.reassessment', 'reviews.compatibility_review')
        for placement in placements:
            for date_kind in ('missing', 'future', 'invalid'):
                with self.subTest(placement=placement, date_kind=date_kind):
                    record = self.complete_record()
                    ref = dict(record['reports']['market_research'])
                    if date_kind == 'missing':
                        ref.pop('as_of')
                    else:
                        ref['as_of'] = '2026-10-12' if date_kind == 'future' else '20261011'
                    if placement in ('evidence', 'withdrawn_sources'):
                        record[placement] = [ref]
                    elif placement == 'compatibility.review':
                        record['compatibility'] = [{'status': 'adopted', 'reason': 'Reviewed clarification',
                                                    'methods': record['methods'], 'review': ref}]
                    elif placement == 'rule_evaluations.evidence':
                        record['rule_evaluations'][0]['evidence'] = [ref]
                    else:
                        record['reviews'][0][placement.split('.')[1]] = ref
                    if placement == 'withdrawn_sources' and date_kind == 'missing':
                        maintenance.validate_handoff(record, self.root)
                    else:
                        with self.assertRaises(ValueError):
                            maintenance.validate_handoff(record, self.root)

    def test_undated_legacy_source_can_be_withdrawn_without_inventing_its_date(self):
        first = self.package('2026-10-09')
        maintenance.write_handoff(self.root, first)
        correction = self.package(status='withdrawn')
        original = first['reports']['market_research']
        correction['withdrawn_sources'] = [{key: original[key] for key in ('path', 'sha256')}]
        maintenance.write_handoff(self.root, correction)
        self.assertEqual(maintenance.check_adoption_lifecycle(self.root, '2026-10-11', first)['status'], 'withdrawn')
        self.assertIsNone(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods()))

    def test_rule_evidence_must_precede_its_own_evaluation_cutoff(self):
        record = self.complete_record()
        record['rule_evaluations'][0]['as_of'] = '2026-10-10'
        with self.assertRaisesRegex(ValueError, 'rule_evaluations.evidence.*decision cutoff'):
            maintenance.validate_handoff(record, self.root)

    def test_method_content_refs_can_remain_undated(self):
        record = self.complete_record()
        self.assertTrue(all('as_of' not in ref for ref in record['methods'].values()))
        maintenance.validate_handoff(record, self.root)

    def test_completion_availability_is_distinct_from_valuation_date(self):
        for artifact in ('report', 'price_map'):
            for availability in ('missing', '2026-10-12'):
                with self.subTest(artifact=artifact, availability=availability):
                    record = self.complete_record()
                    # A valid valuation date does not prove that the finished artifact existed then.
                    ref = record['reviews'][0]['completion'][artifact]
                    if availability == 'missing':
                        ref.pop('as_of')
                    else:
                        ref['as_of'] = availability
                    with self.assertRaises(ValueError):
                        maintenance.validate_handoff(record, self.root)
        record = self.complete_record()
        maintenance.validate_handoff(record, self.root)

    def test_old_company_report_accepts_dated_targeted_reassessment(self):
        record = self.complete_record(valuation_date='2026-10-09')
        review = record['reviews'][0]
        with self.assertRaisesRegex(ValueError, 'dated targeted reassessment'):
            maintenance.validate_handoff(record, self.root)
        targeted = self.root / 'targeted-reassessment.md'
        targeted.write_text('2026-10-11: reviewed the adopted trigger and current company evidence.')
        review['reassessment'] = maintenance.file_ref(self.root, targeted, as_of='2026-10-11')
        maintenance.validate_handoff(record, self.root)
        review['reassessment']['as_of'] = '2026-10-10'
        with self.assertRaisesRegex(ValueError, 'dated targeted reassessment'):
            maintenance.validate_handoff(record, self.root)

    def test_immutable_handoff_and_frozen_sources(self):
        record = self.package()
        maintenance.write_handoff(self.root, record)
        maintenance.write_handoff(self.root, record)
        changed = copy.deepcopy(record)
        changed['adoption_basis'] = 'different'
        with self.assertRaisesRegex(ValueError, 'Immutable'):
            maintenance.write_handoff(self.root, changed)
        (self.root / record['reports']['market_research']['path']).write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'hash changed'):
            maintenance.select_adopted(self.root, '2026-10-11', self.live_methods())

    def test_method_label_cannot_waive_changed_rules(self):
        record = self.package()
        maintenance.write_handoff(self.root, record)
        (self.root / 'framework/investment_framework.md').write_text('adopted rules: threshold > 4\n')
        self.assertIsNone(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods()))

    def test_reviewed_compatibility_is_explicit(self):
        record = self.package()
        old = record['methods']
        (self.root / 'framework/investment_framework.md').write_text('wording clarified threshold > 3\n')
        new = maintenance.freeze_methods(self.root, '2026-10-11', 2)
        review = self.root / 'review.md'
        review.write_text('Reviewed definitions, thresholds, actions, exceptions: unchanged')
        record['compatibility'] = [{'status': 'adopted', 'reason': 'Audited pure clarification',
                                    'methods': new, 'review': maintenance.file_ref(self.root, review, as_of='2026-10-11')}]
        maintenance.write_handoff(self.root, record)
        self.assertIsNotNone(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods()))
        self.assertIsNotNone(maintenance.select_adopted(self.root, '2026-10-11', old))

    def test_only_restricted_observation_block_ignored(self):
        self.assertEqual(maintenance.method_fingerprint(self.state_doc(10)), maintenance.method_fingerprint(self.state_doc(11)))
        self.assertNotEqual(maintenance.method_fingerprint(self.state_doc()), maintenance.method_fingerprint(self.state_doc().replace(b'threshold > 3', b'threshold > 4')))
        legacy = b'rules and old mixed state'
        self.assertEqual(maintenance.method_fingerprint(legacy), hashlib.sha256(legacy).hexdigest())

    def test_bad_state_blocks_cannot_claim_compatibility(self):
        examples = [self.state_doc() + maintenance.END.encode(),
                    self.state_doc().replace(b'"unit": "trillion"', b'"threshold": 4'),
                    self.state_doc().replace(b'"value": 10', b'"value": {"action": "buy"}'),
                    self.state_doc().replace(b'2026-10-10', b'2026-10-12'),
                    self.state_doc().replace(b'"source_report": null', b'"source_report": "../escape"')]
        for example in examples:
            with self.subTest(example=example), self.assertRaises(ValueError):
                maintenance.method_fingerprint(example)

    def test_duplicate_keys_nan_and_unknown_undated_state(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            maintenance.method_fingerprint(self.state_doc().replace(b'"value": 10', b'"value": 10, "value": 11'))
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            maintenance.method_fingerprint(self.state_doc().replace(b'"value": 10', b'"value": NaN'))
        undated = self.state_doc().replace(b'"value": 10', b'"value": null').replace(b'"observed_at": "2026-10-10"', b'"observed_at": null').replace(b'"status": "verified"', b'"status": "unknown"')
        self.assertEqual(maintenance.method_fingerprint(undated), maintenance.method_fingerprint(self.state_doc()))

    def test_state_only_current_method_compatible_with_frozen_source(self):
        for path in (self.root / 'framework').glob('*.md'):
            path.write_bytes(self.state_doc(10))
        record = self.package()
        maintenance.write_handoff(self.root, record)
        for path in (self.root / 'framework').glob('*.md'):
            path.write_bytes(self.state_doc(11))
        self.assertIsNotNone(maintenance.select_adopted(self.root, '2026-10-11', self.live_methods()))

    def test_method_proposal_needs_operational_definition_and_cases(self):
        with self.assertRaisesRegex(ValueError, 'lacks'):
            maintenance.classify_changes([{'kind': 'method_change', 'summary': 'Add exit', 'status': 'proposed'}])
        change = {'kind': 'method_change', 'summary': 'Add exit', 'status': 'proposed'}
        change.update({key: 'documented' for key in ('definition', 'economic_reason', 'scope', 'positive_case', 'negative_case', 'boundary_case', 'compatibility_impact')})
        self.assertTrue(maintenance.classify_changes([change])['update_needed'])

    def test_trigger_is_not_completed_without_company_pair(self):
        record = self.package()
        record['rule_evaluations'] = [{'rule_id': 'D5', 'rule_status': 'adopted', 'as_of': '2026-10-11', 'result': 'triggered', 'affected_objects': ['HK-06886'], 'evidence': [record['reports']['market_research']]}]
        record['reviews'] = [{'company': 'HK-06886', 'trigger_id': 'D5', 'status': 'completed'}]
        with self.assertRaisesRegex(ValueError, 'Triggered is not completed'):
            maintenance.validate_handoff(record, self.root)
        record['reviews'][0]['status'] = 'pending'
        maintenance.validate_handoff(record, self.root)

    def test_proposed_rule_cannot_become_a_research_completion(self):
        record = self.package()
        record['rule_evaluations'] = [{'rule_id': 'new-exit', 'rule_status': 'proposed', 'as_of': '2026-10-11', 'result': 'triggered', 'affected_objects': ['HK-06886'], 'evidence': [record['reports']['market_research']]}]
        record['reviews'] = [{'company': 'HK-06886', 'trigger_id': 'new-exit', 'status': 'pending'}]
        with self.assertRaisesRegex(ValueError, 'adopted triggered'):
            maintenance.validate_handoff(record, self.root)

    def complete_record(self, valuation_date='2026-10-11'):
        record = self.package()
        folder = self.root / f'research/investment/companies/{valuation_date}/HK-06886'
        folder.mkdir(parents=True, exist_ok=True)
        report = folder / f'investment-06886-{valuation_date}-research-codex.md'
        price = folder / f'investment-06886-{valuation_date}-price-map-codex.json'
        report.write_text('\n'.join(f'## {number}. 研究章节\n可见的研究内容。' + ('\n' + ' '.join(ref['sha256'] for ref in record['methods'].values()) if number == 0 else '') for number in range(9)))
        price.write_text(json.dumps({
            'meta': {'code': '06886.HK', 'name': '离线样例', 'currency': 'HKD', 'generator': 'codex',
                     'report_path': str(report.relative_to(self.root)), 'schema_version': 'stock-research/v2',
                     'valuation_date': valuation_date},
            'price_map': {'mode': 'frozen', 'reason': '离线测试临时买入限制', 'v50': None, 'p1': None,
                          'p2': {'status': 'cancelled', 'reason': '证据缺口', 'price': None},
                          't1': {'price_condition': '待核', 'events': ['事件复核']},
                          't2': {'price_condition': '待核', 'events': ['逻辑复核']}},
            'monitoring': [{'variable': '经营证据', 'current': '待核', 'as_of': valuation_date,
                            'trigger': '新披露', 'action': '复评', 'source': '离线样例', 'next_check': '待披露'}]
        }))
        completion = {'report': maintenance.file_ref(self.root, report, as_of=valuation_date), 'price_map': maintenance.file_ref(self.root, price, as_of=valuation_date)}
        record['rule_evaluations'] = [{'rule_id': 'D5', 'rule_status': 'adopted', 'as_of': '2026-10-11', 'result': 'triggered', 'affected_objects': ['HK-06886'], 'evidence': [record['reports']['market_research']]}]
        record['reviews'] = [{'company': 'HK-06886', 'trigger_id': 'D5', 'status': 'completed', 'completion': completion, 'evidence_cutoff': '2026-10-11', 'methods': record['methods']}]
        return record

    def test_company_completion_requires_matching_pair(self):
        record = self.complete_record()
        maintenance.validate_handoff(record, self.root)
        record['reviews'][0]['company'] = 'HK-00001'
        with self.assertRaisesRegex(ValueError, 'matching scope'):
            maintenance.validate_handoff(record, self.root)

    def test_company_completion_accepts_v3_point_and_interval_without_reconstruction(self):
        record = self.complete_record()
        completion = record['reviews'][0]['completion']
        price = self.root / completion['price_map']['path']
        document = json.loads(price.read_text())
        document['meta']['schema_version'] = 'stock-research/v3'
        document['price_map']['v50'] = dict(low=10, base=20, high=30)
        for quote in ({'base': 15}, {'base': None, 'low': 10, 'high': 16}):
            with self.subTest(quote=quote):
                document['price_map']['p1'] = quote
                price.write_text(json.dumps(document))
                completion['price_map'] = maintenance.file_ref(self.root, price, as_of='2026-10-11')
                original = price.read_bytes()
                maintenance.validate_handoff(record, self.root)
                self.assertEqual(price.read_bytes(), original)

    def complete_v4_record(self):
        from scripts import research_consistency as checks
        from research_audit_fixture import audit_for
        record = self.complete_record()
        completion = record['reviews'][0]['completion']
        price = self.root / completion['price_map']['path']
        report = self.root / completion['report']['path']
        document = json.loads(price.read_text())
        document['meta']['schema_version'] = 'stock-research/v4'
        document['price_map'].pop('p2')
        document['price_map'].pop('t2')
        document['price_map']['t1'] = dict(price_condition='本轮不提供T1报价')
        document['research_controls'] = dict(entry=dict(status='blocked', refs=['offline_gate']),
                                             add=dict(status='blocked', refs=['offline_gate']),
                                             holding=dict(status='normal', refs=[]))
        document['monitoring'][0].update(id='evidence', kind='general', state='watching')
        audit = audit_for(document)
        audit['valuation'] = dict(kind='unavailable', reason='offline evidence unavailable')
        report.write_text(report.read_text() + '\n' + checks.render_report_block(audit, document))
        price.write_text(json.dumps(document))
        for key, path in (('report', report), ('price_map', price)):
            completion[key] = maintenance.file_ref(self.root, path, as_of='2026-10-11')
        return record

    def test_company_completion_v4_requires_complete_valid_audit_and_visible_view(self):
        from scripts import research_consistency as checks
        for mistake in ('missing', 'legacy_audit', 'wrong_controls', 'visible_view'):
            with self.subTest(mistake=mistake):
                record = self.complete_v4_record()
                completion = record['reviews'][0]['completion']
                report = self.root / completion['report']['path']
                text = report.read_text()
                if mistake == 'missing':
                    text = text[:text.index(checks.START)]
                elif mistake == 'legacy_audit':
                    text = text.replace('stock-research-audit/v2', 'stock-research-audit/v1')
                elif mistake == 'wrong_controls':
                    text = text.replace('"status": "blocking"', '"status": "unknown"')
                else:
                    text = text.replace('| entry | blocked |', '| entry | eligible |')
                report.write_text(text)
                completion['report'] = maintenance.file_ref(self.root, report, as_of='2026-10-11')
                with self.assertRaisesRegex(ValueError, 'audit|contract mismatch|control summary|calculation view'):
                    maintenance.validate_handoff(record, self.root)
        record = self.complete_v4_record()
        report = self.root / record['reviews'][0]['completion']['report']['path']
        original = report.read_bytes()
        maintenance.validate_handoff(record, self.root)
        self.assertEqual(report.read_bytes(), original)

    def test_completion_rejects_meta_only_wrong_identity_and_invisible_sections(self):
        for mistake in ('meta_only', 'wrong_code', 'wrong_generator', 'commented', 'empty_sections'):
            with self.subTest(mistake=mistake):
                record = self.complete_record()
                completion = record['reviews'][0]['completion']
                price = self.root / completion['price_map']['path']
                report = self.root / completion['report']['path']
                document = json.loads(price.read_text())
                if mistake == 'meta_only':
                    document = {'meta': document['meta']}
                elif mistake == 'wrong_code':
                    document['meta']['code'] = '00001.HK'
                elif mistake == 'wrong_generator':
                    document['meta']['generator'] = 'claude'
                elif mistake == 'commented':
                    report.write_text('<!--' + report.read_text() + '-->')
                else:
                    report.write_text('\n'.join(f'## {i}. 空章' for i in range(9)))
                price.write_text(json.dumps(document))
                completion['price_map'] = maintenance.file_ref(self.root, price, as_of='2026-10-11')
                completion['report'] = maintenance.file_ref(self.root, report, as_of='2026-10-11')
                with self.assertRaises(ValueError):
                    maintenance.validate_handoff(record, self.root)

    def test_completed_report_must_cover_trigger_and_method(self):
        record = self.complete_record()
        record['reviews'][0]['evidence_cutoff'] = '2026-10-09'
        with self.assertRaisesRegex(ValueError, 'trigger evidence'):
            maintenance.validate_handoff(record, self.root)
        record['reviews'][0]['evidence_cutoff'] = '2026-10-11'
        (self.root / 'framework/investment_framework.md').write_text('new method')
        record['reviews'][0]['methods'] = maintenance.freeze_methods(self.root, '2026-10-11', 2)
        with self.assertRaisesRegex(ValueError, 'method provenance|method compatibility'):
            maintenance.validate_handoff(record, self.root)

    def test_report_method_hash_cannot_be_relabelled_in_handoff(self):
        record = self.complete_record()
        review = record['reviews'][0]
        report = self.root / review['completion']['report']['path']
        report.write_text(report.read_text().replace(record['methods']['canonical']['sha256'], '0' * 64))
        review['completion']['report'] = maintenance.file_ref(self.root, report, as_of='2026-10-11')
        with self.assertRaisesRegex(ValueError, 'method provenance'):
            maintenance.validate_handoff(record, self.root)

    def test_empty_withdrawal_is_not_a_successful_revocation(self):
        with self.assertRaisesRegex(ValueError, 'explicit target'):
            maintenance.validate_handoff(self.package(status='withdrawn'), self.root)

    def test_explicit_withdrawal_rechecked_during_research(self):
        first = self.package('2026-10-09')
        maintenance.write_handoff(self.root, first)
        unrelated = self.package('2026-10-10')
        maintenance.write_handoff(self.root, unrelated)
        self.assertEqual(maintenance.check_adoption_lifecycle(self.root, '2026-10-11', first)['status'], 'active')
        correction = self.package(supersedes=[first['id']])
        maintenance.write_handoff(self.root, correction)
        self.assertEqual(maintenance.check_adoption_lifecycle(self.root, '2026-10-11', first)['status'], 'superseded')
        withdrawn = self.package(revision=2, status='withdrawn')
        withdrawn['withdrawn_sources'] = [first['reports']['market_research']]
        maintenance.write_handoff(self.root, withdrawn)
        self.assertEqual(maintenance.check_adoption_lifecycle(self.root, '2026-10-11', first)['status'], 'withdrawn')
        self.assertEqual(maintenance.check_adoption_lifecycle(self.root, '2026-10-09', first)['status'], 'active')

    def test_discovery_strict_track_dates_and_revision(self):
        official = maintenance.weekly_path(self.root, '2026-10-11', 'market-research')
        official.parent.mkdir(parents=True)
        for name in (official.name, 'investment-2026-10-11-market-research-r2.md',
                     'investment-2026-10-11-market-research-r10.md', '2026-10-11-market-research.md',
                     'investment-2026-10-11-market-research-r1.md', 'investment-2026-10-12-market-research.md',
                     'investment-2026-10-11-market-research.md.partial'):
            (official.parent / name).write_text('report')
        found = maintenance.discover_reports(self.root, 'market-research')
        self.assertEqual([p.name for p in found], [official.name, 'investment-2026-10-11-market-research-r2.md', 'investment-2026-10-11-market-research-r10.md'])
        self.assertEqual(maintenance.discover_reports(self.root, 'market-research', before='2026-10-11'), [])
        self.assertEqual(maintenance.next_revision(self.root, '2026-10-11'), 11)

    def test_supersession_cannot_point_to_unknown_record(self):
        record = self.package(supersedes=['missing'])
        maintenance.write_handoff(self.root, record)
        with self.assertRaisesRegex(ValueError, 'missing'):
            maintenance.select_adopted(self.root, '2026-10-11', self.live_methods())


class RepairExitTests(unittest.TestCase):
    days = ['2026-10-09', '2026-10-12', '2026-10-13']

    def rows(self):
        return [{'date': day, 'turnover_trillion': 1.7, 'margin_change_yi': -149,
                 'star50_close': 1516.2, 'margin_basis': 'complete_daily_change',
                 'index_basis': 'official_close'} for day in self.days]

    def test_positive_and_inclusive_index_boundary(self):
        self.assertEqual(maintenance.evaluate_repair_exit(self.rows(), self.days, calendar=self.days), 'met')

    def test_strict_volume_and_margin_boundaries(self):
        for key, value in [('turnover_trillion', 1.6), ('margin_change_yi', -150), ('star50_close', 1516.19)]:
            rows = self.rows()
            rows[0][key] = value
            with self.subTest(key=key):
                self.assertEqual(maintenance.evaluate_repair_exit(rows, self.days, calendar=self.days), 'not_met')

    def test_missing_and_known_failure_do_not_become_pass(self):
        rows = self.rows()
        rows[0]['margin_change_yi'] = None
        self.assertEqual(maintenance.evaluate_repair_exit(rows, self.days, calendar=self.days), 'unknown')
        rows[1]['turnover_trillion'] = 1.5
        self.assertEqual(maintenance.evaluate_repair_exit(rows, self.days, calendar=self.days), 'not_met')
        self.assertEqual(maintenance.evaluate_repair_exit(self.rows()[:2], self.days, calendar=self.days), 'unknown')

    def test_calendar_rejects_skipped_session_and_missing_calendar(self):
        with self.assertRaisesRegex(ValueError, 'calendar required'):
            maintenance.evaluate_repair_exit(self.rows(), self.days)
        days = ['2026-10-09', '2026-10-13', '2026-10-14']
        with self.assertRaisesRegex(ValueError, 'skips'):
            maintenance.evaluate_repair_exit([], days, calendar=['2026-10-09', '2026-10-12', '2026-10-13', '2026-10-14'])

    def test_reject_proxy_intraday_wrong_date_duplicate_nonfinite(self):
        for key, value in [('margin_basis', 'financing_proxy'), ('index_basis', 'intraday'),
                           ('date', '2026-10-08'), ('turnover_trillion', float('nan'))]:
            rows = self.rows()
            rows[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                maintenance.evaluate_repair_exit(rows, self.days, calendar=self.days)
        with self.assertRaises(ValueError):
            maintenance.evaluate_repair_exit(self.rows() + self.rows()[:1], self.days, calendar=self.days)


if __name__ == '__main__':
    unittest.main()
