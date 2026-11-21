import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import research_runner as runner, stock_ai_watchlist as watch, stock_framework_bundle as bundle

try:
    import test_research_runner as fixtures
except ImportError:
    from tests import test_research_runner as fixtures


class WatchlistTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.row = dict(name='样本', business='订阅', evidence='公司披露独立收费产品。',
                        check='核付费续订、客单价及推理成本。', source_date='2026-10-01',
                        source_title='业绩公告', source_url='https://example.com/results')

    def runner_fixture(self):
        fixture = fixtures.ResearchRunnerTests('test_whitespace_pack_refused')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root = fixture.methods
        for filename in bundle.BUNDLE:
            shutil.copyfile(watch.ROOT/'framework'/filename, self.root/'framework'/filename)
        return fixture

    def release(self, stamp, entries, suffix=''):
        folder = self.root / watch.AI_WATCHLIST_DIR
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f'investment-{stamp[:10]}-ai-watchlist{suffix}.json'
        path.write_text(json.dumps(dict(available_at=stamp, entries=entries), ensure_ascii=False))
        return path

    def test_point_in_time_revisions_membership_and_per_task_cutoff(self):
        code = '00700.HK'
        original = self.release('2026-10-06T07:00:00+08:00', {code: self.row})
        self.release('2026-10-06T09:30:00+08:00', {}, '-r2')
        request = dict(valuation_date='2026-10-06', created_at='2026-10-06T02:00:00Z', tasks=[
            dict(task_id='HK-00700', code=code, data_pack_meta={}),
            dict(task_id='SH-688111', code='688111.SH', data_pack_meta=dict(evidence_cutoff='2026-10-05'))])
        current = watch.freeze(self.root, request)
        self.assertIsNone(current['HK-00700']['entry'])
        self.assertNotIn('SH-688111', current)
        task = request['tasks'][0]
        task['data_pack_meta']['historical_valuation_revision'] = dict(evidence_cutoff='2026-10-06T09:00:00+08:00')
        hit = watch.freeze(self.root, request)['HK-00700']
        self.assertEqual((hit['version'], hit['entry']), (original.name, self.row))
        request['created_at'] = '2026-10-06T06:59:59+08:00'
        self.assertEqual(watch.freeze(self.root, request), {})
        request['created_at'] = '2026-10-07T06:00:00+08:00'
        request['valuation_date'] = '2026-10-05'
        self.assertEqual(watch.freeze(self.root, request), {})

    def test_listed_and_unlisted_decisions(self):
        record = dict(version='release', sha256='a'*64, code='00700.HK', entry=self.row)
        for decision in ('启用', '跳过'):
            watch.validate_decision(f'AI专项：{decision}｜理由：见中报，已确认订阅收费。', record, 'non_dividend')
        for line in ('', 'AI专项：启用｜理由：  ', 'AI专项：跳过｜理由：本次收息\nAI专项：启用｜理由：另有收费'):
            with self.assertRaisesRegex(ValueError, 'decision'):
                watch.validate_decision(line, record, 'non_dividend')
        with self.assertRaisesRegex(ValueError, 'decision'):
            watch.validate_decision('AI专项：启用｜理由：模型业务收入。', record, 'dividend')
        watch.validate_decision('AI专项：跳过｜理由：收息研究已扣算力投入。', record, 'dividend')
        watch.validate_decision('- **AI专项**：跳过｜**理由**：AI 试点的投入很小。', record, 'non_dividend')
        unlisted = dict(record, entry=None)
        self.assertIn('仍可启用', watch.instructions(unlisted, 'non_dividend'))
        watch.validate_decision('无专项段落', unlisted, 'non_dividend')

    def test_recovery_inherits_parent_membership_after_revision(self):
        fixture = self.runner_fixture()
        self.release('2026-10-06T07:00:00+08:00', {'600066.SH': self.row})
        request = fixture.request
        request.update(schema_version='stock-research-request/v2', generators=['codex', 'dsh'])
        fixture.write_request()
        runtime = runner.research_runtime
        profiles = [runtime.default_profile(g) for g in request['generators']]
        config = dict(schema_version=runtime.CONFIG_SCHEMA, profiles=profiles,
                      active={p['producer']: p['profile_id'] for p in profiles})
        parent = runner.prepare_request(fixture.request_path, self.root, runtime_config=config)
        self.release('2026-10-06T09:00:00+08:00', {}, '-r2')
        request.update(batch_id='b'*32, generators=['dsh'], created_at='2026-10-06T10:00:00+08:00')
        fixture.write_request()
        child = runner.prepare_recovery_request(fixture.request_path, parent, self.root)
        _, _, packs, inputs = runner.verify_recovery_prepared(child, parent, self.root)
        task = request['tasks'][0]
        frozen = inputs[task['task_id'], 'dsh']
        self.assertEqual(frozen['ai_watchlist']['entry'], self.row)
        retry = runner.make_prompt(request, task, 'dsh', packs[task['task_id']], self.root,
                                   frozen['frameworks'], frozen['targets'], attempt=2,
                                   delivery=frozen['delivery'], ai_watchlist=frozen['ai_watchlist'])
        self.assertIn(self.row['check'].encode(), retry)

    def test_invalid_sources_and_duplicate_keys(self):
        path = self.release('2026-10-06T07:00:00+08:00', {'00700.HK': dict(self.row, source_date='2026-10-07')})
        with self.assertRaisesRegex(ValueError, 'source'):
            watch.releases(self.root, watch.cutoff('2026-10-06'))
        path.write_text(path.read_text().replace('"entries":', '"entries": {}, "entries":'))
        with self.assertRaises(ValueError):
            watch.releases(self.root, watch.cutoff('2026-10-06'))

    def test_prepare_verify_and_accept_without_live_watchlist(self):
        fixture = self.runner_fixture()
        source = self.release('2026-10-06T07:00:00+08:00', {'600066.SH': self.row, '00700.HK': self.row})
        run = runner.prepare_request(fixture.request_path, self.root)
        source.unlink()
        request, _, _, inputs = runner.verify_prepared(run, (run/'request.json').read_bytes(), self.root)
        task = request['tasks'][0]
        frozen = inputs[task['task_id'], 'codex']
        self.assertIn(self.row['check'].encode(), frozen['prompt'])
        self.assertNotIn(b'00700.HK', frozen['prompt'])
        targets = frozen['targets']
        receipt = {k: v['enum'][0] for k, v in runner.receipt_schema(request, task, 'codex', targets)['properties'].items()
                   if 'enum' in v}
        receipt.update(status='completed', reason=None, summary='fixture', **targets)
        report = self.root / targets['report_path']
        report.parent.mkdir(parents=True, exist_ok=True)
        (self.root / targets['price_map_path']).write_text('{}')
        bindings = ' '.join([request['batch_id'], task['data_pack']['sha256'], *frozen['frameworks'].values()])
        sections = ''.join(f'\n## {i}\n正文' for i in range(1, 9))
        args = (receipt, request, task, 'codex', request['created_at'], request['created_at'],
                self.root, frozen['frameworks'], targets, frozen['ai_watchlist'])
        report.write_text('## 0\n' + bindings + sections)
        with self.assertRaisesRegex(ValueError, 'decision'):
            runner.accepted_entry(*args)
        report.write_text('## 0\n' + bindings + '\nAI专项：启用｜理由：订阅收费影响估值。' + sections)
        self.assertEqual(runner.accepted_entry(*args)['status'], 'completed')
