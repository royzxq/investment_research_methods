"""Truthful DSH identities and legacy-compatible contracts; no model/network IO."""
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import test_research_exchange as exchange_fixture
import test_research_scheduler as scheduler_fixture
import test_research_runner as runner_fixture
import test_research_dsh as dsh_fixture
import test_research_scheduler_profiles as scheduler_profile_fixture
from scripts import research_exchange as exchange
from scripts import research_coze as coze
from scripts import research_paths as paths
from scripts import research_runner as runner
from scripts import research_runtime as runtime
from scripts import research_scheduler as scheduler


class DSHExchangeTests(unittest.TestCase):
    def setUp(self):
        self.f = exchange_fixture.ResearchExchangeTests('runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def dsh_pair(self):
        f = self.f
        f.request.update(schema_version=exchange.REQUEST_SCHEMA_V2, generators=['codex', 'dsh'])
        f.write_request()
        f.report_relative = f.report_relative.replace('-codex', '-dsh')
        f.price_relative = f.price_relative.replace('-codex', '-dsh')
        old_report = f.report_path.read_bytes()
        f.report_path = f.artifact_root / f.report_relative
        f.price_path = f.artifact_root / f.price_relative
        f.report_path.write_bytes(old_report)
        f.document['meta'].update(generator='dsh', report_path=f.report_relative,
                                  schema_version='stock-research/v4')
        pm = f.document['price_map']
        pm.pop('p2'); pm.pop('t2'); pm['t1'].pop('events')
        f.document['research_controls'] = dict(entry=dict(status='unknown', refs=['GAP']),
            add=dict(status='unknown', refs=['GAP']), holding=dict(status='normal', refs=[]))
        f.document['monitoring'][0].update(id='income', kind='general', state='watching')
        f.price_path.write_text(json.dumps(f.document, ensure_ascii=False))
        entry = f.result['results'][0]
        entry.update(generator='dsh', report=dict(path=f.report_relative, sha256=f.sha(f.report_path)),
                     price_map=dict(path=f.price_relative, sha256=f.sha(f.price_path)))
        f.result.update(schema_version=exchange.RESULT_SCHEMA_V2, request_sha256=f.sha(f.request_path))
        f.write_result()

    def test_v1_request_result_and_bytes_stay_unchanged(self):
        f = self.f
        before = {p: p.read_bytes() for p in f.root.rglob('*') if p.is_file()}
        self.assertEqual(exchange.load_request(f.request_path), f.request)
        self.assertEqual(f.check_result(), f.result)
        self.assertEqual(before, {p: p.read_bytes() for p in f.root.rglob('*') if p.is_file()})
        self.assertEqual(exchange.seal_schema(f.request), 'research-sealed/v1')

    def test_v2_dsh_completed_pair_retains_true_identity_and_original_seat(self):
        self.dsh_pair()
        self.assertEqual(self.f.check_result()['results'][0]['generator'], 'dsh')
        self.assertEqual(exchange.business_seat('dsh'), 'claude')
        self.assertEqual(exchange.business_seat('codex'), 'gemini')
        self.assertEqual(exchange.seal_schema(self.f.request), 'research-sealed/v2')
        self.assertEqual(runner.manifest(self.f.request, self.f.request_path.read_bytes(), [])['schema_version'],
                         exchange.RESULT_SCHEMA_V2)

    def test_v1_cannot_smuggle_dsh_or_unknown_identity(self):
        for generators in (['codex', 'dsh'], ['dsh'], ['unknown'], ['codex', 'coze']):
            with self.subTest(generators=generators):
                self.f.request['generators'] = generators
                self.f.write_request()
                with self.assertRaisesRegex(ValueError, 'unsupported generator'):
                    exchange.load_request(self.f.request_path)

    def test_v2_rejects_duplicate_business_seat_and_arbitrary_mapping(self):
        for generators in (['claude', 'dsh'], ['codex', 'claude', 'dsh'], ['dsh', 'dsh']):
            with self.subTest(generators=generators), self.assertRaises(ValueError):
                exchange.validate_generators(generators, exchange.REQUEST_SCHEMA_V2)
        self.dsh_pair()
        self.f.request['business_seats'] = {'dsh': 'extra-vote'}
        self.f.write_request()
        with self.assertRaises(ValueError):
            exchange.load_request(self.f.request_path)

    def test_result_version_must_match_frozen_request(self):
        for modern in (False, True):
            with self.subTest(modern=modern):
                if modern:
                    self.dsh_pair()
                self.f.result['schema_version'] = (exchange.RESULT_SCHEMA if modern else exchange.RESULT_SCHEMA_V2)
                self.f.write_result()
                with self.assertRaisesRegex(ValueError, 'request version'):
                    self.f.check_result()

    def test_dsh_artifacts_cannot_claim_claude_or_other_paths(self):
        self.dsh_pair()
        self.f.document['meta']['generator'] = 'claude'
        self.f.rewrite_document()
        with self.assertRaisesRegex(ValueError, 'meta.generator'):
            self.f.check_result()

    def test_dsh_missing_or_failed_remains_absent_or_failed(self):
        self.dsh_pair()
        self.f.result['results'] = []
        self.f.write_result()
        self.assertEqual(self.f.check_result()['results'], [])
        self.f.result['results'] = [dict(task_id='SH-600066', generator='dsh', status='failed',
            reason='offline failure', started_at='2026-10-06T08:01:00+08:00',
            completed_at='2026-10-06T09:00:00+08:00', report=None, price_map=None)]
        self.f.write_result()
        self.assertEqual(self.f.check_result()['results'][0]['status'], 'failed')

    def test_dsh_history_and_latest_namespace_never_aliases_claude(self):
        self.dsh_pair()
        f = self.f
        report = paths.company_path('SH', '600066', '2026-10-06', 'research', f.artifact_root, generator='dsh')
        price = paths.company_path('SH', '600066', '2026-10-06', 'price-map', f.artifact_root, generator='dsh')
        report.write_bytes(f.report_path.read_bytes())
        doc = deepcopy(f.document); doc['meta']['report_path'] = report.relative_to(f.artifact_root).as_posix()
        price.write_text(json.dumps(doc))
        self.assertEqual(paths.company_runs('SH', '600066', '2026-10-06', f.artifact_root, generator='dsh'), [price])
        self.assertEqual(paths.company_runs('SH', '600066', '2026-10-06', f.artifact_root, generator='claude'), [])

    def test_base_seal_version_and_dsh_provenance_are_bound(self):
        self.dsh_pair()
        f = self.f
        f.request['tasks'][0]['data_pack_meta']['research_trigger'] = dict(event_key='event')
        f.write_request()
        text = f.report_path.read_text().replace('本节的离线验收内容。',
            f"batch={f.request['batch_id']}; pack={f.request['tasks'][0]['data_pack']['sha256']}", 1)
        f.report_path.write_text(text)
        entry = f.result['results'][0]
        entry['report']['sha256'] = f.sha(f.report_path)
        f.result['results'].append(dict(task_id='SH-600066', generator='codex', status='failed',
            reason='offline failure', started_at=entry['started_at'], completed_at=entry['completed_at'],
            report=None, price_map=None))
        f.result.update(request_sha256=f.sha(f.request_path))
        f.result_path = f.artifact_root / 'output/result.json'
        f.result_path.parent.mkdir(parents=True)
        f.write_result()
        payload = dict(manifest='output/result.json', manifest_sha256=f.sha(f.result_path), actual_model=None)
        queue_entry = dict(task_id='SH-600066', batch_id=f.request['batch_id'], event_key='event',
            request=str(f.request_path), request_sha256=f.sha(f.request_path), budget_date='2026-10-06')
        state_root = f.artifact_root / 'output/research_queue'
        scheduler.seal_entry(queue_entry, state_root, f.request,
            {'codex': ('failed', dict(payload, generator='codex')),
             'dsh': ('completed', dict(payload, generator='dsh'))})
        seal_path = Path(queue_entry['sealed'])
        context = coze.load_base(seal_path, f.artifact_root, f.request_root)
        self.assertEqual(set(context['documents']), {'dsh'})
        self.assertFalse(coze.eligible(context))
        original = seal_path.read_bytes()
        bad = json.loads(original); bad['schema_version'] = 'research-sealed/v1'
        seal_path.write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError, 'version mismatch'):
            coze.load_base(seal_path, f.artifact_root, f.request_root)

    def test_coze_scan_emits_true_pair_keys_and_preserves_base(self):
        self.dsh_pair()
        f = self.f
        f.request['tasks'][0]['data_pack_meta']['research_trigger'] = dict(event_key='event')
        f.write_request()
        source = f.report_path.read_text().replace('本节的离线验收内容。',
            f"batch={f.request['batch_id']}; pack={f.request['tasks'][0]['data_pack']['sha256']}", 1)
        original_entry = f.result['results'][0]
        entries = []
        for producer, price in (('codex', 10), ('dsh', 12)):
            report_relative = f.report_relative.replace('-dsh', '-' + producer)
            price_relative = f.price_relative.replace('-dsh', '-' + producer)
            report_path, price_path = f.artifact_root/report_relative, f.artifact_root/price_relative
            report_path.write_text(source)
            doc = deepcopy(f.document)
            doc['meta'].update(generator=producer, report_path=report_relative)
            doc['price_map']['p1'] = {'base': price}
            price_path.write_text(json.dumps(doc))
            entry = dict(original_entry, generator=producer,
                report=dict(path=report_relative, sha256=f.sha(report_path)),
                price_map=dict(path=price_relative, sha256=f.sha(price_path)))
            entries.append(entry)
        f.result.update(results=entries, request_sha256=f.sha(f.request_path))
        f.result_path = f.artifact_root/'output/result.json'
        f.result_path.parent.mkdir(parents=True)
        f.write_result()
        descriptor = dict(manifest='output/result.json', manifest_sha256=f.sha(f.result_path), actual_model=None)
        queue_entry = dict(task_id='SH-600066', batch_id=f.request['batch_id'], event_key='event',
            request=str(f.request_path), request_sha256=f.sha(f.request_path), budget_date='2026-10-06')
        scheduler.seal_entry(queue_entry, f.artifact_root/'output/research_queue', f.request,
            {g: ('completed', dict(descriptor, generator=g)) for g in f.request['generators']})
        preserved = Path(queue_entry['sealed']).read_bytes()
        result = coze.scan(f.artifact_root, f.request_root, f.root/'mail', '2026-10-01T00:00:00+08:00')
        self.assertFalse(result['errors'])
        intents = list((f.artifact_root/'output/research_queue/coze').glob('*/intent.json'))
        self.assertEqual(len(intents), 1)
        intent = json.loads(intents[0].read_text())
        self.assertEqual(intent['p1'], {'codex': 10, 'dsh': 12})
        self.assertEqual(Path(queue_entry['sealed']).read_bytes(), preserved)
        coze.scan(f.artifact_root, f.request_root, f.root/'mail', '2026-10-01T00:00:00+08:00')
        self.assertEqual(len(list((f.artifact_root/'output/research_queue/coze').glob('*/intent.json'))), 1)


class DSHPolicyBoundaryTests(unittest.TestCase):
    def test_implicit_profiles_keep_exact_legacy_pair(self):
        config = runtime.load_config()
        self.assertEqual(set(config['active']), {'codex', 'claude'})
        self.assertEqual(set(p['producer'] for p in config['profiles']), {'codex', 'claude'})
        request = dict(schema_version=exchange.REQUEST_SCHEMA_V2, batch_id='b'*32, generators=['dsh'])
        with self.assertRaisesRegex(ValueError, 'no active profile'):
            runtime.build_plan(request, runtime.canonical_bytes(request))

    def test_execution_plan_cannot_add_same_business_seat_twice(self):
        request = dict(schema_version=exchange.REQUEST_SCHEMA_V2, batch_id='b'*32,
                       generators=['codex', 'claude', 'dsh'])
        with self.assertRaisesRegex(ValueError, 'business seat'):
            runtime.build_plan(request, runtime.canonical_bytes(request))

    def test_v2_plan_cannot_fall_back_to_marker_free_legacy_defaults(self):
        request = dict(schema_version=exchange.REQUEST_SCHEMA_V2, batch_id='b'*32, generators=['dsh'])
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(ValueError, 'v2 request requires'):
            runtime.load_plan(Path(temp), request, runtime.canonical_bytes(request), {})

    def test_three_active_lookup_bindings_only_freeze_the_requested_pair(self):
        config = runtime.load_config()
        dsh = runtime.default_profile('dsh')
        config['profiles'].append(dsh)
        config['active']['dsh'] = dsh['profile_id']
        config = runtime.validate_config(config)
        for version, pair in ((exchange.REQUEST_SCHEMA, ['codex', 'claude']),
                              (exchange.REQUEST_SCHEMA_V2, ['codex', 'dsh'])):
            with self.subTest(version=version):
                request = dict(schema_version=version, batch_id='b'*32, generators=pair)
                plan = runtime.build_plan(request, runtime.canonical_bytes(request), config)
                self.assertEqual(set(plan['profiles']), set(pair))
                self.assertEqual(plan['profiles']['codex'], runtime.default_profile('codex'))
                if 'dsh' in pair:
                    self.assertEqual(plan['profiles']['dsh']['models'], dict(
                        main=dict(model='deepseek-flash', effort='high'), subagent=dict(model='deepseek-flash')))
                else:
                    self.assertIsNone(plan['profiles']['claude']['models']['main']['model'])

    def test_missing_request_does_not_preflight_every_supported_binding(self):
        config = runtime.load_config()
        dsh = runtime.default_profile('dsh')
        config['profiles'].append(dsh); config['active']['dsh'] = dsh['profile_id']
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = dict(valuation_date='2026-10-23', batch_id='a'*32,
                         request=str(root/'missing-request.json'))
            profiles, _ = scheduler.admission_profiles([entry], root, config)
            self.assertEqual(set(p['producer'] for p in profiles), {'codex', 'claude'})

    def test_legacy_claude_start_keeps_dsh_replacement_in_cooldown(self):
        f = scheduler_fixture.CooldownTests('runTest')
        with tempfile.TemporaryDirectory() as temp:
            state = scheduler.new_state()
            f.prior_run(Path(temp), generator='claude')
            scheduler.sync_started(state, Path(temp))
            entry = dict(task_id='SH-600004', generator='dsh')
            boundary = scheduler_fixture.NOW + timedelta(days=7)
            self.assertIsNotNone(scheduler.cooldown_until(state, entry, boundary-timedelta(microseconds=1)))
            self.assertIsNone(scheduler.cooldown_until(state, entry, boundary))

    def test_dsh_actual_launch_counts_as_same_listing_history(self):
        f = scheduler_fixture.CooldownTests('runTest')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run, _ = f.prior_run(root, generator='dsh')
            request = json.loads((run/'request.json').read_text())
            request.update(schema_version=exchange.REQUEST_SCHEMA_V2, generators=['dsh'])
            raw = runtime.canonical_bytes(request); (run/'request.json').write_bytes(raw)
            claim_path = run/'execution/SH-600004/dsh/launched.json'
            claim = json.loads(claim_path.read_text()); claim['request_sha256'] = hashlib.sha256(raw).hexdigest()
            claim_path.write_text(json.dumps(claim))
            state = scheduler.new_state()
            scheduler.sync_started(state, root)
            self.assertEqual(state['last_started']['SH-600004']['batch_id'], request['batch_id'])
            self.assertEqual(state['last_started']['SH-600004']['started_at'], scheduler_fixture.NOW.isoformat())

    def test_coze_uses_original_business_pair_with_true_dsh_key(self):
        doc = lambda base: {'price_map': {'p1': {'base': base}}}
        for producer in ('claude', 'dsh'):
            with self.subTest(producer=producer):
                context = dict(task={'task_id':'SH-600066'}, documents={'codex':doc(10), producer:doc(11)})
                self.assertFalse(coze.eligible(context))
                context['documents'][producer] = doc(11.01)
                self.assertTrue(coze.eligible(context))
                self.assertEqual(coze.pair_generators(context['documents']), ['codex', producer])
                context['documents'][producer] = {'price_map': {'p1': {'base': None, 'low': 10, 'high': 12}}}
                self.assertFalse(coze.eligible(context))
        self.assertIsNone(coze.pair_generators({'claude':doc(10), 'dsh':doc(12)}))
        self.assertIsNone(coze.pair_generators({'codex':doc(10), 'claude':doc(11), 'dsh':doc(12)}))


class DSHPreparedBatchTests(unittest.TestCase):
    def test_old_frozen_and_unprepared_legacy_coexist_with_new_dsh_plan(self):
        f = runner_fixture.ResearchRunnerTests('runTest')
        f.setUp(); self.addCleanup(f.doCleanups)
        config = runtime.load_config()
        dsh = runtime.default_profile('dsh')
        config['profiles'].append(dsh); config['active']['dsh'] = dsh['profile_id']
        requests = []
        for key, version, producers in (('a', exchange.REQUEST_SCHEMA, ['codex', 'claude']),
                                       ('b', exchange.REQUEST_SCHEMA_V2, ['codex', 'dsh']),
                                       ('c', exchange.REQUEST_SCHEMA, ['codex', 'claude'])):
            request = deepcopy(f.request)
            request.update(schema_version=version, batch_id=key*32, generators=producers)
            target = f.root/'inputs'/key/'request.json'
            pack = target.parent/request['tasks'][0]['data_pack']['path']
            pack.parent.mkdir(parents=True); pack.write_bytes(f.pack.read_bytes())
            raw = runtime.canonical_bytes(request); target.write_bytes(raw)
            requests.append((request, target, raw))
        old_run = runner.prepare_request(requests[0][1], f.methods)
        old_plan_path = old_run/'framework-snapshot/execution-plan.json'
        old_plan = old_plan_path.read_bytes()
        # The next live configuration may change legacy options, but not an
        # already frozen old CC batch. Both remain valid alongside new DSH.
        live_cc = next(p for p in config['profiles'] if p['producer'] == 'claude')
        live_cc['profile_id'] = 'claude-current-lookup'
        live_cc['models']['main']['model'] = 'current-model'
        config['active']['claude'] = live_cc['profile_id']
        new_run = runner.prepare_request(requests[1][1], f.methods, runtime_config=config)
        new_plan = json.loads((new_run/'framework-snapshot/execution-plan.json').read_text())
        self.assertEqual(set(new_plan['profiles']), {'codex', 'dsh'})
        entries = [dict(valuation_date=request['valuation_date'], batch_id=request['batch_id'],
            request=str(path), request_sha256=hashlib.sha256(raw).hexdigest())
            for request, path, raw in requests]
        profiles, preparations = scheduler.admission_profiles(entries, f.methods, config)
        self.assertEqual([p['producer'] for p in profiles].count('codex'), 3)
        self.assertEqual([p['producer'] for p in profiles].count('claude'), 2)
        self.assertEqual([p['producer'] for p in profiles].count('dsh'), 1)
        cc_profiles = [p for p in profiles if p['producer'] == 'claude']
        self.assertEqual({p['profile_id'] for p in cc_profiles}, {'claude-inherited', 'claude-current-lookup'})
        self.assertEqual(old_plan_path.read_bytes(), old_plan)
        self.assertEqual(set(preparations), {('2026-10-06', 'c'*32)})
        snapshot = json.loads((new_run/'framework-snapshot/manifest.json').read_text())
        self.assertIsNone(snapshot['research_baselines']['SH-600066/dsh'])
        for request, path, raw in requests:
            self.assertEqual(path.read_bytes(), raw)


class DSHRunnerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f = runner_fixture.ResearchRunnerTests('runTest')
        self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.f.request.update(schema_version=exchange.REQUEST_SCHEMA_V2, generators=['dsh'])
        self.f.write_request()
        self.config = runtime.load_config()
        profile = runtime.default_profile('dsh')
        self.config['profiles'].append(profile)
        self.config['active']['dsh'] = profile['profile_id']
        self.f.fake.write_text(dsh_fixture.build_fake_dsh_cli())
        env = patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'offline-test-placeholder'})
        env.start(); self.addCleanup(env.stop)

    def execute(self):
        return runner.run_batch(self.f.request_path, self.f.methods, generator='dsh',
                                cli=str(self.f.fake), timeout=10, runtime_config=self.config)

    def test_fake_dsh_completes_through_shared_runner_and_v2_result(self):
        raw = self.f.request_path.read_bytes()
        result_path = self.execute()
        result = exchange.load_results(result_path, self.f.request_path, self.f.methods)
        self.assertEqual(result['schema_version'], exchange.RESULT_SCHEMA_V2)
        entry = result['results'][0]
        self.assertEqual(entry['status'], 'completed', entry['reason'])
        self.assertEqual(entry['generator'], 'dsh')
        self.assertIn('-dsh.json', entry['price_map']['path'])
        folder = result_path.parent/'execution/SH-600066/dsh'
        process = json.loads((folder/'process.json').read_text())
        self.assertEqual(process['actual_model'], 'offline-dsh-observed')
        self.assertEqual(process['execution_profile']['producer'], 'dsh')
        self.assertEqual(process['execution_profile']['harness'], 'dsh-cli')
        self.assertEqual(self.f.request_path.read_bytes(), raw)
        self.assertFalse(list((result_path.parent/'execution/SH-600066').glob('claude/*')))
        self.assertEqual(json.loads((self.f.methods/entry['price_map']['path']).read_text())['meta']['generator'], 'dsh')

    def test_exit_zero_with_aborted_native_turn_cannot_publish_artifacts(self):
        self.f.fake.write_text(self.f.fake.read_text().replace(
            "'completed' if success else 'error'", "'aborted' if success else 'error'"))
        result_path = self.execute()
        result = json.loads(result_path.read_text())
        entry = result['results'][0]
        self.assertEqual(entry['status'], 'failed')
        self.assertIn('did not complete successfully', entry['reason'])
        self.assertIsNone(entry['report']); self.assertIsNone(entry['price_map'])
        folder = result_path.parent/'execution/SH-600066/dsh'
        process = json.loads((folder/'process.json').read_text())
        self.assertEqual(process['exit_code'], 0)
        self.assertEqual(process['status'], 'failed')
        self.assertFalse(list((self.f.methods/'research/investment/companies').glob('**/*-dsh.*')))

    def test_scheduler_pair_retries_dsh_from_frozen_profile_and_seals_v2(self):
        f = scheduler_profile_fixture.SchedulerProfileTests('runTest')
        f.setUp(); self.addCleanup(f.doCleanups)
        f.request.update(schema_version=exchange.REQUEST_SCHEMA_V2, generators=['codex', 'dsh'])
        f.request_path.write_bytes(runtime.canonical_bytes(f.request))
        dsh_cli = f.root/'fake-dsh'
        dsh_cli.write_text(dsh_fixture.build_fake_dsh_cli(scheduler_profile_fixture.PROFILE_CLI))
        dsh_cli.chmod(0o700)
        f.config_path.write_bytes(runtime.canonical_bytes(self.config))
        with patch.dict('os.environ', {'MOCK_PROFILE_RETRY': 'dsh'}):
            result = f.run_tick(runtime_config=f.config_path,
                clis={'codex': str(f.fake), 'dsh': str(dsh_cli)})
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['used'], 1)
        captures = f.captured()
        self.assertEqual([c['generator'] for c in captures].count('codex'), 1)
        self.assertEqual([c['generator'] for c in captures].count('dsh'), 2)
        self.assertNotIn('claude', [c['generator'] for c in captures])
        self.assertEqual(f.config_path.read_text(), 'invalid current configuration during retry')
        seals = list((f.methods/'output/research_queue/sealed').glob('*.json'))
        self.assertEqual(len(seals), 1)
        seal = json.loads(seals[0].read_text())
        self.assertEqual(seal['schema_version'], 'research-sealed/v2')
        self.assertEqual([r['generator'] for r in seal['results']], ['codex', 'dsh'])
        endpoint = f.run_root/'execution/SH-600066/dsh'
        first = json.loads((endpoint/'process.json').read_text())
        retried = json.loads((endpoint/'retry-1/process.json').read_text())
        self.assertEqual(first['status'], 'failed')
        self.assertEqual(retried['status'], 'completed')
        self.assertEqual(first['execution_profile'], retried['execution_profile'])
        for descriptor in seal['results']:
            doc = exchange.load_results(f.methods/descriptor['manifest'], f.request_path, f.methods)
            self.assertEqual(doc['schema_version'], exchange.RESULT_SCHEMA_V2)
            self.assertEqual(doc['results'][0]['status'], 'completed')


if __name__ == '__main__':
    unittest.main()
