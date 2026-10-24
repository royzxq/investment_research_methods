"""Recovery supplements preserve the original conditional Coze pair and identity."""
from copy import deepcopy
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import test_research_exchange as fixture
from scripts import research_coze as coze


class RecoveryCozeTests(unittest.TestCase):
    def setUp(self):
        self.f = fixture.ResearchExchangeTests('runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        f = self.f
        for name in ('root', 'request_root', 'artifact_root', 'request_path', 'result_path',
                     'pack', 'report_path', 'price_path'):
            setattr(f, name, getattr(f, name).resolve())
        f.request.update(schema_version='stock-research-request/v2', generators=['codex', 'dsh'])
        f.request['tasks'][0]['data_pack_meta']['research_trigger'] = {'event_key': 'original-event'}
        f.write_request()
        old_text = f.report_path.read_text().replace('本节的离线验收内容。',
            f"batch={f.request['batch_id']}; pack={f.sha(f.pack)}", 1)
        f.report_path.write_text(old_text)
        f.result.update(schema_version='stock-research-result/v2', request_sha256=f.sha(f.request_path))
        f.result['results'][0]['report']['sha256'] = f.sha(f.report_path)
        f.result['results'].append(dict(task_id='SH-600066', generator='dsh', status='failed',
            reason='timeout', started_at='2026-10-06T08:01:00+08:00',
            completed_at='2026-10-06T09:00:00+08:00', report=None, price_map=None))
        self.base = self.write_seal(f.artifact_root/'output/research_queue/sealed/original.json',
            f.request_path, f.request, f.result, 'output/base-result.json')
        self.base_document = deepcopy(f.document)

        request = deepcopy(f.request)
        request.update(batch_id='2'*32, created_at='2026-10-06T10:00:00+08:00', generators=['dsh'])
        self.recovery_request = f.request_root/'recovery-request.json'
        coze.atomic(self.recovery_request, request)
        relative = f.report_relative.replace('-codex', '-dsh')
        price_relative = f.price_relative.replace('-codex', '-dsh')
        report = f.artifact_root/relative
        report.write_text(old_text.replace(f.request['batch_id'], request['batch_id']))
        doc = deepcopy(f.document)
        doc['meta'].update(generator='dsh', report_path=relative, schema_version='stock-research/v4')
        doc['price_map']['p1'] = {'base': 15}
        doc['price_map'].pop('p2'); doc['price_map'].pop('t2'); doc['price_map']['t1'].pop('events')
        doc['research_controls'] = dict(entry=dict(status='unknown', refs=['R14']),
            add=dict(status='unknown', refs=['R14']), holding=dict(status='normal', refs=[]))
        doc['monitoring'][0].update(id='income', kind='general', state='watching')
        price = f.artifact_root/price_relative
        coze.atomic(price, doc)
        result = dict(schema_version='stock-research-result/v2', batch_id=request['batch_id'],
            request_sha256=f.sha(self.recovery_request), created_at='2026-10-06T11:00:00+08:00',
            results=[dict(task_id='SH-600066', generator='dsh', status='completed', reason=None,
                started_at='2026-10-06T10:01:00+08:00', completed_at='2026-10-06T10:50:00+08:00',
                report=dict(path=relative, sha256=f.sha(report)),
                price_map=dict(path=price_relative, sha256=f.sha(price)))])
        self.recovery = self.write_seal(f.artifact_root/'output/research_recovery/test/seals/SH-600066.json',
            self.recovery_request, request, result, 'output/research_recovery/test/result.json')
        self.wrapper = f.artifact_root/'output/research_queue/sealed/original-recovery-test.json'
        self.wrapper_doc = dict(coze.read(self.base), schema_version='research-sealed-recovery/v1',
            base_seal=dict(path=str(self.base.relative_to(f.artifact_root)), sha256=f.sha(self.base)),
            recovery_seal=dict(path=str(self.recovery.relative_to(f.artifact_root)), sha256=f.sha(self.recovery)),
            recovered_generators=['dsh'], recovery_intent=dict(path='output/research_recovery/test/intent.json', sha256='a'*64))
        coze.atomic(self.wrapper, self.wrapper_doc)
        module = ModuleType('scripts.research_recovery')
        self.loader = unittest.mock.Mock(return_value=(self.base, self.recovery, self.wrapper_doc))
        module.load_supplement = self.loader
        self.mock_module = patch.dict(sys.modules, {'scripts.research_recovery': module})
        self.mock_module.start()
        self.addCleanup(self.mock_module.stop)

    def write_seal(self, path, request_path, request, result, relative):
        manifest = self.f.artifact_root/relative
        coze.atomic(manifest, result)
        value = dict(schema_version='research-sealed/v2', task_id='SH-600066',
            batch_id=request['batch_id'], event_key='original-event', request=str(request_path),
            request_sha256=self.f.sha(request_path), budget_date='2026-10-06', results=[dict(
                generator=g, manifest=relative, manifest_sha256=self.f.sha(manifest), actual_model=None)
                for g in request['generators']])
        coze.atomic(path, value)
        return path

    def test_recovery_pair_binds_each_report_to_own_request_and_keeps_codex(self):
        before = {p: p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        context = coze.load_base(self.wrapper, self.f.artifact_root, self.f.request_root)
        self.loader.assert_called_once_with(self.wrapper, self.f.artifact_root, self.f.request_root)
        self.assertEqual(context['request'], self.f.request)
        self.assertEqual(context['request_path'], self.f.request_path)
        self.assertEqual(context['documents']['codex'], self.base_document)
        self.assertEqual(context['documents']['dsh']['meta']['generator'], 'dsh')
        self.assertEqual(context['entries']['dsh']['status'], 'completed')
        self.assertEqual(context['round_path'], self.base)
        self.assertTrue(coze.eligible(context))
        self.assertEqual(before, {p: p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()})

    def test_private_recovery_seal_cannot_be_used_as_original_pair(self):
        with self.assertRaisesRegex(ValueError, 'outside research queue'):
            coze.load_base(self.recovery, self.f.artifact_root, self.f.request_root)

    def test_invalid_recovery_never_hides_original_or_resets_existing_failure(self):
        self.loader.side_effect = ValueError('invalid recovery binding')
        result = coze.scan(self.f.artifact_root, self.f.request_root, self.f.root/'mail',
                           '2026-10-01T00:00:00+08:00')
        self.assertEqual(result['intents'], [])
        self.assertIn('invalid recovery binding', result['errors'][0]['reason'])
        self.loader.side_effect = None
        result = coze.scan(self.f.artifact_root, self.f.request_root, self.f.root/'mail',
                           '2026-10-01T00:00:00+08:00')
        intent_path = Path(result['intents'][0]['intent'])
        intent = coze.read(intent_path)
        self.assertEqual(intent['base_seal'], str(self.wrapper))
        self.assertEqual(intent['p1'], {'codex': 12, 'dsh': 15})
        intent.update(status='failed', reason='original Coze timeout', retry_allowed=False)
        coze.atomic(intent_path, intent)
        preserved = intent_path.read_bytes()
        coze.scan(self.f.artifact_root, self.f.request_root, self.f.root/'mail',
                  '2026-10-01T00:00:00+08:00')
        self.assertEqual(intent_path.read_bytes(), preserved)

    def test_scan_prefers_latest_original_round_over_old_recovery(self):
        original_load = coze.load_base
        newer = self.f.artifact_root/'output/research_queue/sealed/newer-round.json'
        coze.atomic(newer, dict(coze.read(self.base), batch_id='3'*32))
        def contexts(path, methods, exchange):
            if Path(path) == newer:
                value = original_load(self.base, methods, exchange)
                value['request'] = dict(value['request'], created_at='2026-10-06T11:00:00+08:00')
                value['path'] = newer
                return value
            return original_load(path, methods, exchange)
        with patch.object(coze, 'load_base', side_effect=contexts):
            result = coze.scan(self.f.artifact_root, self.f.request_root, self.f.root/'mail',
                               '2026-10-01T00:00:00+08:00')
        self.assertEqual(result['intents'], [])
        self.assertEqual(result['errors'], [])

    def test_existing_changed_intent_is_held_without_replacing_terminal_history(self):
        folder = self.f.artifact_root/'output/research_queue/coze'/('1'*32+'-SH-600066')
        prior = dict(schema_version='coze-intent/v1', status='failed', retry_allowed=False,
                     base_seal=str(self.base), base_sha256=self.f.sha(self.base), reason='timeout')
        coze.atomic(folder/'intent.json', prior)
        raw = (folder/'intent.json').read_bytes()
        result = coze.scan(self.f.artifact_root, self.f.request_root, self.f.root/'mail',
                           '2026-10-01T00:00:00+08:00')
        self.assertEqual(result['intents'], [])
        self.assertIn('intent input changed', result['errors'][0]['reason'])
        self.assertEqual((folder/'intent.json').read_bytes(), raw)

    def test_coze_publish_filters_recovery_fields_and_roundtrips_recursive_parent(self):
        result = coze.scan(self.f.artifact_root, self.f.request_root, self.f.root/'mail',
                           '2026-10-01T00:00:00+08:00')
        intent_path = Path(result['intents'][0]['intent'])
        intent = coze.read(intent_path)
        intent.update(status='pending', request_id='mail-1')
        coze.atomic(intent_path, intent)
        text = 'P1：11.00元/股；T1：18.00元/股。'
        extracted = dict(p1={'base':11}, t1=18, monitoring=[],
                         evidence=dict(p1='P1：11.00元/股', t1='T1：18.00元/股'))
        selected = dict(raw_path=str(self.f.root/'raw.txt'), text=text, extraction=extracted,
            request=dict(request_id='mail-1', status='complete', history=[], sent_at='2026-10-06T11:00:00+08:00'),
            message=dict(received_at='2026-10-06T11:01:00+08:00'), base_sha256=self.f.sha(self.wrapper))
        with patch.object(coze, 'capture_email', return_value=selected), \
             patch.object(coze, 'freeze_email', return_value=({'path':'email.txt','sha256':'c'*64}, {'path':'receipt.json','sha256':'d'*64})):
            published = coze.publish(intent_path, self.f.root/'not-read.json', self.f.artifact_root, self.f.request_root)
        sealed = coze.read(published['sealed'])
        self.assertEqual(set(sealed), coze.BASE_KEYS | {'base_seal', 'coze'})
        self.assertEqual(sealed['base_seal']['path'], str(self.wrapper.relative_to(self.f.artifact_root)))
        self.assertEqual(sealed['results'], coze.read(self.base)['results'])
        with patch.object(coze, 'archived_email', return_value=text):
            parent, doc, _ = coze.load_supplement(published['sealed'], self.f.artifact_root, self.f.request_root)
        self.assertEqual(parent, self.wrapper)
        self.assertEqual(doc['meta']['generator'], 'coze')


if __name__ == '__main__':
    unittest.main()
