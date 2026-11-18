import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from scripts import stock_framework_bundle as bundle, research_runner as runner
try:
    import test_research_runner as fixtures
except ImportError:
    from tests import test_research_runner as fixtures

ROOT = Path(__file__).resolve().parents[1]


class FrameworkBundleTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ResearchRunnerTests('test_whitespace_pack_refused')
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.methods

    def enable_bundle(self):
        for name in bundle.BUNDLE:
            shutil.copyfile(ROOT/'framework'/name, self.root/'framework'/name)

    def prepare(self):
        return runner.prepare_request(self.fixture.request_path, self.root)

    def test_new_snapshot_binds_all_dependencies_and_exact_prompt(self):
        self.enable_bundle(); run = self.prepare()
        hashes, snapshot = runner.snapshot_hashes(run)
        self.assertEqual(set(hashes), set(bundle.BUNDLE))
        self.assertEqual(snapshot['schema_version'], 'stock-framework-snapshot/v2')
        self.assertEqual(runner.delivery_contract(snapshot), runner.NEW_CONTRACT)
        prompt = (run/'execution/SH-600066/codex/prompt.txt').read_text()
        self.assertIn('dividend_report_template.md', prompt)
        self.assertIn('路由变化逐条审议旧控制', prompt)
        self.assertIn('two-price-controls/v10', prompt)
        self.assertIn('JSON仍v4/audit-v7', prompt)
        self.assertNotIn('stock-research-audit/v6', prompt)
        runner.verify_prepared(run, (run/'request.json').read_bytes(), self.root)

    def route(self, strategy='dividend'):
        return dict(schema_version='stock-research-route/v1', rule='dividend-spread/v1',
            code='600066.SH', valuation_date='2026-10-06', status='classified', strategy=strategy,
            threshold_pp=2, comparison='>', max_age_days=7, spread_pp=3 if strategy=='dividend' else 2,
            trailing_yield=dict(value=5 if strategy=='dividend' else 4, unit='percent', currency='CNY',
                as_of='2026-10-06', basis='gross_ttm', source='https://tushare.pro'),
            government_10y=dict(value=2, unit='percent', currency='CNY', as_of='2026-10-06',
                tenor_years=10, curve_type='government_ytm', source='https://tushare.pro'))

    def test_automatic_dividend_selects_skill_and_recovers_frozen_route(self):
        self.enable_bundle()
        self.fixture.request['tasks'][0]['data_pack_meta']['research_route'] = self.route()
        self.fixture.write_request()
        run = self.prepare()
        prompt = (run/'execution/SH-600066/codex/prompt.txt').read_bytes()
        self.assertIn('使用 dividend-research 技能'.encode(), prompt)
        self.assertNotIn('先按stock_research_common.md的C0和用户持有目的'.encode(), prompt)
        self.assertIn('dividend_report_template.md'.encode(), prompt)
        self.assertIn('"threshold_pp": 2'.encode(), prompt)
        runner.verify_prepared(run, (run/'request.json').read_bytes(), self.root)
        self.assertEqual(prompt, (run/'execution/SH-600066/codex/prompt.txt').read_bytes())

    def test_automatic_non_dividend_and_invalid_routes(self):
        self.enable_bundle()
        route = self.route('non_dividend')
        self.fixture.request['tasks'][0]['data_pack_meta']['research_route'] = route
        self.fixture.write_request()
        run = self.prepare()
        self.assertIn('使用 stock-research 技能', (run/'execution/SH-600066/codex/prompt.txt').read_text())
        route['status'] = 'pending'
        self.fixture.write_request()
        with self.assertRaises(ValueError):
            runner.read_request(self.fixture.request_path)

    def test_automatic_route_refuses_legacy_two_file_bundle(self):
        self.fixture.request['tasks'][0]['data_pack_meta']['research_route'] = self.route()
        self.fixture.write_request()
        with self.assertRaisesRegex(ValueError, 'full strategy framework bundle'):
            self.prepare()

    def test_legacy_pair_snapshot_and_prompt_remain_v1(self):
        run = self.prepare(); hashes, snapshot = runner.snapshot_hashes(run)
        self.assertEqual(set(hashes), set(bundle.CORE))
        self.assertEqual(snapshot['schema_version'], runner.SNAPSHOT_SCHEMA)
        prompt = (run/'execution/SH-600066/codex/prompt.txt').read_text()
        self.assertNotIn('本批采用股票策略拆分依赖包', prompt)

    def test_early_v2_snapshot_keeps_original_rule_bytes_after_scope_migration(self):
        old = ROOT / 'research/investment/weekly/2026-11-17/evidence/investment-2026-11-17-handoff-r2-methods'
        for name in bundle.BUNDLE:
            shutil.copyfile(old/name, self.root/'framework'/name)
        with patch.object(runner, 'NEW_CONTRACT', runner.AVAILABILITY_CONTRACT):
            run = self.prepare()
        hashes, snapshot = runner.snapshot_hashes(run)
        self.assertEqual(snapshot['schema_version'], 'stock-framework-snapshot/v2')
        self.assertEqual(runner.delivery_contract(snapshot), runner.AVAILABILITY_CONTRACT)
        before = (run/'execution/SH-600066/codex/prompt.txt').read_bytes()
        self.assertIn(b'audit-v6', before)
        self.assertNotIn(b'two-price-controls/v10', before)
        self.enable_bundle()
        runner.verify_prepared(run, (run/'request.json').read_bytes(), self.root)
        self.assertEqual(before, (run/'execution/SH-600066/codex/prompt.txt').read_bytes())
        for name in bundle.BUNDLE:
            self.assertEqual((run/'framework-snapshot'/name).read_bytes(), (old/name).read_bytes())
        self.assertEqual(runner.framework_compatibility(run, self.root, hashes,
                         '2026-10-06')['classification'], 'needs_review')

    def test_new_dependencies_are_not_implicitly_read_by_old_resume(self):
        run = self.prepare(); before = (run/'execution/SH-600066/codex/prompt.txt').read_bytes()
        self.enable_bundle()
        runner.verify_prepared(run, (run/'request.json').read_bytes(), self.root)
        self.assertEqual(before, (run/'execution/SH-600066/codex/prompt.txt').read_bytes())
        hashes, _ = runner.snapshot_hashes(run)
        result = runner.framework_compatibility(run, self.root, hashes, '2026-10-06')
        self.assertTrue(result['needs_review'])

    def test_dependency_changed_without_resigning_cannot_prepare(self):
        self.enable_bundle()
        path = self.root/'framework/stock_research_common.md'; path.write_text(path.read_text()+'changed')
        with self.assertRaisesRegex(ValueError, 'dependency hash'): self.prepare()

    def test_missing_dependency_cannot_prepare(self):
        self.enable_bundle(); (self.root/'framework/dividend_report_template.md').unlink()
        with self.assertRaises(OSError): self.prepare()

    def test_tampered_frozen_dependency_or_omission_rejected(self):
        self.enable_bundle(); run = self.prepare()
        path = run/'framework-snapshot/dividend_framework.md'
        path.chmod(0o644); path.write_text('changed')
        with self.assertRaisesRegex(ValueError,'mismatch'): runner.snapshot_hashes(run)
        shutil.copyfile(ROOT/'framework/dividend_framework.md', path)
        manifest = run/'framework-snapshot/manifest.json'; manifest.chmod(0o644)
        doc=json.loads(manifest.read_text()); doc['frameworks'].pop('dividend_framework.md')
        manifest.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'manifest'): runner.snapshot_hashes(run)

    def test_resigned_shared_change_is_method_change_not_state_only(self):
        self.enable_bundle(); run = self.prepare(); hashes, _ = runner.snapshot_hashes(run)
        path = self.root/'framework/stock_research_common.md'; path.write_text(path.read_text()+'\nMethod changed.\n')
        bundle.sync(self.root)
        result = runner.framework_compatibility(run, self.root, hashes, '2026-10-06')
        self.assertEqual(result['classification'], 'needs_review')

    def test_bundle_cannot_downgrade_to_legacy_contract(self):
        self.enable_bundle(); run = self.prepare()
        manifest = run/'framework-snapshot/manifest.json'; manifest.chmod(0o644)
        doc=json.loads(manifest.read_text()); doc['delivery_contract']=runner.OLD_TWO_PRICE_CONTRACT
        doc['research_validation']='stock-research-audit/v2'; manifest.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,'current frozen delivery'): runner.snapshot_hashes(run)

    def test_dependency_markers_must_agree_and_cannot_duplicate(self):
        self.enable_bundle(); contents=bundle.capture(self.root/'framework')
        contents[bundle.CORE[1]] = b'legacy'
        with self.assertRaisesRegex(ValueError,'closure'): bundle.validate(contents)
        raw=(self.root/'framework'/bundle.CORE[0]).read_bytes()
        with self.assertRaisesRegex(ValueError,'one'): bundle.dependency_map(raw+raw)

    def test_maintenance_freeze_and_validation_include_dependency_closure(self):
        from scripts import investment_maintenance as maintenance
        self.enable_bundle()
        methods = maintenance.freeze_methods(self.root, '2026-11-17')
        maintenance._method_pair(self.root, methods)
        folder = (self.root / methods['canonical']['path']).parent
        self.assertEqual({p.name for p in folder.iterdir()}, set(bundle.BUNDLE))
        (folder/'stock_research_common.md').unlink()
        with self.assertRaises(OSError): maintenance._method_pair(self.root, methods)

    def test_recovery_copies_full_bundle_and_never_live_changes(self):
        self.enable_bundle()
        request = self.fixture.request
        request['schema_version'] = 'stock-research-request/v2'
        request['generators'] = ['dsh']
        self.fixture.write_request()
        config = runner.research_runtime.load_config()
        profile = runner.research_runtime.default_profile('dsh')
        config['profiles'].append(profile); config['active']['dsh'] = profile['profile_id']
        run = runner.prepare_request(self.fixture.request_path, self.root, runtime_config=config)
        parent, _, packs = runner.read_request(run/'request.json')
        child = copy.deepcopy(parent); child['batch_id'] = 'b' * 32
        raw = runner.encode(child)
        changed = self.root/'framework/dividend_framework.md'
        changed.write_text('live method must not enter recovery')
        hashes, snapshot, files = runner._recovery_inputs(child, raw, packs, run, self.root)
        self.assertEqual(set(hashes), set(bundle.BUNDLE))
        for name in bundle.BUNDLE:
            self.assertEqual(files[name], (run/'framework-snapshot'/name).read_bytes())

    def test_future_default_does_not_invalidate_frozen_bundle_contract(self):
        self.enable_bundle(); run = self.prepare()
        with patch.object(runner, 'NEW_CONTRACT', dict(prompt_template='future-default')):
            _, snapshot = runner.snapshot_hashes(run)
            self.assertEqual(runner.delivery_contract(snapshot), runner.NEUTRAL_CONTRACT)

    def test_adopted_bundle_mirror_survives_removing_live_maintenance(self):
        self.enable_bundle()
        self.fixture.make_handoff()
        run = self.prepare()
        _, snapshot = runner.snapshot_hashes(run)
        self.assertIsNotNone(snapshot['maintenance'])
        copied = {Path(item['original_path']).name for item in snapshot['maintenance']['sources']}
        self.assertTrue(set(bundle.BUNDLE) <= copied)
        shutil.rmtree(self.root/'research')
        runner.verify_prepared(run, (run/'request.json').read_bytes(), self.root)
