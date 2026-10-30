"""Recovery preparation preserves the parent research inputs without model calls."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import investment_maintenance as maintenance
from scripts import research_runner as runner
from scripts import research_runtime as runtime


class RecoveryRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for name in runner.FRAMEWORKS:
            path = self.root / 'framework' / name
            path.parent.mkdir(exist_ok=True)
            path.write_text('offline original method ' + name)
        self.exchange = self.root / 'exchange'
        tasks = []
        for ticker in ('600066', '600900'):
            task_id = 'SH-' + ticker
            relative = 'packs/' + task_id + '.md'
            raw = ('# ' + ticker + '.SH 量价与基本面数据包\noriginal pack\n').encode()
            path = self.exchange / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            tasks.append(dict(task_id=task_id, code=ticker + '.SH', name='offline company ' + ticker,
                              sources=['candidate_review'], data_pack=dict(path=relative, sha256=runner.sha(raw)),
                              data_pack_meta={'frozen': True}))
        self.request = dict(schema_version='stock-research-request/v2', batch_id='a' * 32,
                            created_at='2026-10-24T05:00:00+08:00', valuation_date='2026-10-24',
                            generators=['codex', 'dsh'], tasks=tasks)
        self.parent_request = self.exchange / 'request.json'
        self.parent_request.write_bytes(runner.encode(self.request))
        profiles = [runtime.default_profile(g) for g in self.request['generators']]
        profiles[1].update(profile_id='frozen-parent-dsh', revision=7)
        profiles[1]['models']['main']['effort'] = 'low'
        self.config = dict(schema_version=runtime.CONFIG_SCHEMA, profiles=profiles,
                           active={p['producer']: p['profile_id'] for p in profiles})
        self.parent = runner.prepare_request(self.parent_request, self.root, runtime_config=self.config)
        self.child = deepcopy(self.request)
        self.child.update(batch_id='b' * 32, generators=['dsh'], created_at='2026-10-24T10:00:00+08:00')
        self.child['tasks'] = self.child['tasks'][:1]
        self.child_folder = self.root / 'recovery-request'
        self.child_folder.mkdir()
        for task in self.child['tasks']:
            target = self.child_folder / task['data_pack']['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((self.exchange / task['data_pack']['path']).read_bytes())
        self.child_request = self.child_folder / 'request.json'
        self.write_child()

    def write_child(self):
        self.child_request.write_bytes(runner.encode(self.child))

    def prepare(self):
        return runner.prepare_recovery_request(self.child_request, self.parent, self.root)

    @staticmethod
    def tree(path):
        return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in path.rglob('*') if p.is_file()}

    def refresh_parent_prompts(self, snapshot):
        manifest = self.parent / 'framework-snapshot/manifest.json'
        manifest.chmod(0o644)
        manifest.write_bytes(runner.encode(snapshot))
        frameworks, _ = runner.snapshot_hashes(self.parent)
        for task in self.request['tasks']:
            for generator in self.request['generators']:
                folder = self.parent / 'execution' / task['task_id'] / generator
                targets = json.loads((folder / 'targets.json').read_text())
                baseline = snapshot['research_baselines'][task['task_id'] + '/' + generator]
                if baseline is not None:
                    baseline = dict(report_path=(self.parent / 'framework-snapshot' / baseline['path']).relative_to(self.root).as_posix(),
                                    sha256=baseline['sha256'])
                prompt = runner.make_prompt(self.request, task, generator,
                    (self.exchange / task['data_pack']['path']).read_bytes(), self.root, frameworks, targets,
                    maintenance=snapshot['maintenance'], research_validation=snapshot['research_validation'],
                    research_baseline=baseline, delivery=runner.delivery_contract(snapshot),
                    evidence_workflow=snapshot.get('evidence_workflow'))
                (folder / 'prompt.txt').write_bytes(prompt)
                (folder / 'input.json').write_bytes(runner.encode(runner.input_record(
                    self.request, self.parent_request.read_bytes(), task, generator, prompt, frameworks, targets)))

    def test_recovery_inherits_exact_method_pack_profile_and_delivery_without_live_selection(self):
        before = self.tree(self.parent)
        for name in runner.FRAMEWORKS:
            (self.root / 'framework' / name).write_text('changed current method')
        with patch.object(runtime, 'load_config', side_effect=AssertionError('must use parent profile')), \
                patch.object(runner, 'framework_bytes', side_effect=AssertionError('must use frozen method')), \
                patch.object(runner, 'company_runs', side_effect=AssertionError('must use frozen baseline')):
            child = self.prepare()
        self.assertEqual(before, self.tree(self.parent))
        request, raw, packs, verified = runner.verify_prepared(child, self.child_request.read_bytes(), self.root)
        self.assertEqual(request, self.child)
        self.assertEqual(packs['SH-600066'], (self.exchange / 'packs/SH-600066.md').read_bytes())
        self.assertEqual(set(verified), {('SH-600066', 'dsh')})
        _, original = runner.snapshot_hashes(self.parent)
        _, snapshot = runner.snapshot_hashes(child)
        self.assertEqual(snapshot['delivery_contract'], original['delivery_contract'])
        self.assertEqual(snapshot['research_validation'], original['research_validation'])
        self.assertEqual(set(snapshot['research_baselines']), {'SH-600066/dsh'})
        self.assertEqual(verified[('SH-600066', 'dsh')]['execution_profile'], self.config['profiles'][1])
        self.assertNotEqual(snapshot['execution_plan']['sha256'], original['execution_plan']['sha256'])
        self.assertFalse((child / 'execution/SH-600066/codex').exists())
        self.assertFalse((child / 'execution/SH-600900').exists())
        runner.verify_recovery_prepared(child, self.parent, self.root)

    def test_selected_dsh_baseline_is_copied_but_codex_and_unselected_answers_are_not(self):
        _, snapshot = runner.snapshot_hashes(self.parent)
        for task in self.request['tasks']:
            for generator in self.request['generators']:
                key = task['task_id'] + '/' + generator
                relative = 'research-baselines/' + task['task_id'] + '-' + generator + '.md'
                raw = (key + ' ORIGINAL ANSWER').encode()
                target = self.parent / 'framework-snapshot' / relative
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(raw)
                snapshot['research_baselines'][key] = dict(path=relative, sha256=runner.sha(raw), original_path='research/' + key + '.md')
        self.refresh_parent_prompts(snapshot)
        before = self.tree(self.parent)
        child = self.prepare()
        answers = list((child / 'framework-snapshot/research-baselines').glob('*.md'))
        self.assertEqual([p.name for p in answers], ['SH-600066-dsh.md'])
        self.assertEqual(answers[0].read_bytes(), b'SH-600066/dsh ORIGINAL ANSWER')
        self.assertEqual(before, self.tree(self.parent))

    def test_all_frozen_maintenance_sources_survive_removed_live_sources(self):
        day = '2026-10-23'
        reports = {}
        for key, kind in (('market_research', 'market-research'), ('change_decision', 'change-decision')):
            path = maintenance.weekly_path(self.root, day, kind)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('offline adopted evidence ' + kind)
            reports[key] = maintenance.file_ref(self.root, path, as_of=day)
        path = maintenance.weekly_path(self.root, day, 'handoff')
        changes = [dict(kind='state_refresh', summary='offline adopted state')]
        record = dict(schema=maintenance.SCHEMA, id=path.stem, as_of=day, revision=None,
                      status='adopted', adoption_basis='explicit fixture adoption', method_status='adopted',
                      methods=maintenance.freeze_methods(self.root, day), reports=reports, changes=changes,
                      classification=maintenance.classify_changes(changes), supersedes=[], withdrawn_sources=[],
                      evidence=[], compatibility=[], rule_evaluations=[], reviews=[])
        maintenance.write_handoff(self.root, record)
        # A fresh synthetic parent freezes the adopted handoff before live removal.
        self.request['batch_id'] = 'c' * 32
        self.parent_request.write_bytes(runner.encode(self.request))
        self.parent = runner.prepare_request(self.parent_request, self.root, runtime_config=self.config)
        _, original = runner.snapshot_hashes(self.parent)
        self.assertIsNotNone(original['maintenance'])
        for source in original['maintenance']['sources']:
            (self.root / source['original_path']).unlink()
        child = self.prepare()
        _, frozen = runner.snapshot_hashes(child)
        self.assertEqual(original['maintenance'], frozen['maintenance'])
        for source in frozen['maintenance']['sources']:
            self.assertEqual((self.parent / 'framework-snapshot' / source['path']).read_bytes(),
                             (child / 'framework-snapshot' / source['path']).read_bytes())

    def test_occupied_outputs_get_new_revision_and_prepare_is_read_only_idempotent(self):
        task = self.child['tasks'][0]
        targets = runner.targets_for_revision(self.root, self.child, task, 'dsh')
        for relative in targets.values():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'preserved previous output')
        child = self.prepare()
        actual = json.loads((child / 'execution/SH-600066/dsh/targets.json').read_text())
        self.assertTrue(all('-r2.' in p for p in actual.values()))
        before = self.tree(child)
        self.assertEqual(self.prepare(), child)
        self.assertEqual(before, self.tree(child))
        for relative in targets.values():
            self.assertEqual((self.root / relative).read_bytes(), b'preserved previous output')

    def test_changed_task_pack_date_generator_or_batch_is_rejected_before_create(self):
        original = deepcopy(self.child)
        cases = [('name', lambda d: d['tasks'][0].update(name='different company')),
                 ('sources', lambda d: d['tasks'][0].update(sources=['other_signal'])),
                 ('metadata', lambda d: d['tasks'][0]['data_pack_meta'].update(changed=True)),
                 ('date', lambda d: d.update(valuation_date='2026-10-25')),
                 ('generator', lambda d: d.update(generators=['codex'])),
                 ('batch', lambda d: d.update(batch_id=self.request['batch_id']))]
        for label, mutate in cases:
            self.child = deepcopy(original)
            mutate(self.child)
            self.write_child()
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.prepare()
        self.assertFalse((self.root / 'output/runs/investment/2026-10-24' / ('b' * 32)).exists())

    def test_parent_tamper_and_child_freeze_rebinding_are_rejected(self):
        child = self.prepare()
        manifest = child / 'framework-snapshot/manifest.json'
        snapshot = json.loads(manifest.read_text())
        snapshot['captured_at'] = '2026-10-24T11:00:00+08:00'
        manifest.chmod(0o644)
        manifest.write_bytes(runner.encode(snapshot))
        with self.assertRaisesRegex(ValueError, 'recovery.*snapshot'):
            self.prepare()
        parent_method = self.parent / 'framework-snapshot/investment_framework.md'
        parent_method.chmod(0o644)
        parent_method.write_bytes(b'changed frozen parent method')
        with self.assertRaises(ValueError):
            self.prepare()

    def test_extra_child_snapshot_answer_is_not_accepted_on_resume(self):
        child = self.prepare()
        path = child / 'framework-snapshot/research-baselines/SH-600066-codex.md'
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b'copied other seat answer')
        with self.assertRaisesRegex(ValueError, 'recovery.*snapshot'):
            self.prepare()

    def test_older_delivery_contract_is_not_silently_upgraded(self):
        _, snapshot = runner.snapshot_hashes(self.parent)
        snapshot['delivery_contract'] = dict(runner.ACCEPTANCE_CONTROLS_CONTRACT)
        self.refresh_parent_prompts(snapshot)
        child = self.prepare()
        _, inherited = runner.snapshot_hashes(child)
        self.assertEqual(inherited['delivery_contract'], runner.ACCEPTANCE_CONTROLS_CONTRACT)
        prompt = (child / 'execution/SH-600066/dsh/prompt.txt').read_text()
        self.assertNotIn('本批监控摘要two-price-controls/v4', prompt)
        self.assertIn('本批验收语义two-price-controls/v3', prompt)

    def test_partial_child_and_missing_parent_freeze_are_preserved_without_migration(self):
        partial = self.root / 'output/runs/investment/2026-10-24' / ('b' * 32)
        partial.mkdir()
        (partial / 'partial-evidence.txt').write_bytes(b'do not replace')
        before = self.tree(partial)
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            self.prepare()
        self.assertEqual(before, self.tree(partial))
        (self.parent / 'framework-snapshot/manifest.json').unlink()
        parent_before = self.tree(self.parent)
        with patch.object(runner, 'migrate_legacy_prepared', side_effect=AssertionError('no migration')), \
                self.assertRaisesRegex(ValueError, 'frozen parent'):
            self.prepare()
        self.assertEqual(parent_before, self.tree(self.parent))


if __name__ == '__main__':
    unittest.main()
