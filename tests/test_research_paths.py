"""Offline output-contract tests: isolation, publication failure and historical provenance."""
from contextlib import redirect_stdout
import argparse
import ast
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import subprocess
import shutil
import tempfile
import sys
import unittest
from unittest.mock import patch

from scripts import research_paths as paths
from scripts import etf_backtest


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, path, text='report'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def snapshot(self, day='2026-10-01', track='futures'):
        stamp = day.replace('-', '')
        return self.write(paths.artifact_path(track, 'data-snapshot', day, self.root),
                          f'== header AS_OF={stamp} ==\n== 快照完成 | AS_OF={stamp} | done ==\n')

    def test_discovery_excludes_other_tracks_archive_revision_and_future(self):
        first = paths.artifact_path('futures', 'execution-audit', '2026-09-19', self.root)
        second = paths.artifact_path('futures', 'execution-audit', '2026-09-26', self.root)
        self.write(first); self.write(second)
        self.write(paths.artifact_path('futures', 'execution-audit', '2026-10-10', self.root))
        self.write(first.with_name('investment-2026-09-19-execution-audit.md'))
        self.write(first.with_name('2026-09-19-execution-audit-r2.md'))
        self.write(first.with_name('2026-09-19-execution-audit.md.partial'))
        self.write(self.root/'research/futures/archive/2026-09-19-execution-audit.md')
        self.write(first.parent/'2026-09-20-execution-audit.md')
        self.assertEqual(paths.discover('futures', 'execution-audit', '2026-09-26', self.root), [first, second])
        self.assertEqual(paths.discover('futures', 'execution-audit', '2026-09-26', self.root, before=True), [first])

    def test_date_and_kind_rejection(self):
        for day in ['2026-02-30', '../2026-10-01', '2026-10-01/extra']:
            with self.assertRaises(ValueError): paths.artifact_path('futures', 'data-snapshot', day, self.root)
        with self.assertRaises(ValueError): paths.artifact_path('investment', 'execution-audit', '20261001', self.root)
        with self.assertRaises(ValueError): paths.company_dir('../HK', '01952', self.root)

    def test_snapshot_discovery_requires_matching_header_and_final_marker(self):
        good = self.snapshot()
        bad = self.snapshot('2026-10-02')
        bad.write_text(bad.read_text()+'interrupted\n')
        wrong = self.snapshot('2026-10-03')
        wrong.write_text(wrong.read_text().replace('20261003', '20261004'))
        self.assertEqual(paths.discover('futures','data-snapshot','2026-10-05',self.root),[good])
        bad.write_bytes(b'\xff')
        self.assertFalse(paths.snapshot_complete(bad, '2026-10-02'))

    def test_committed_selection_excludes_new_staged_and_modified_evidence(self):
        def git(*args):
            return subprocess.run(['git', *args],cwd=self.root,check=True,capture_output=True)
        git('init'); git('config','user.email','test@example.invalid'); git('config','user.name','Test')
        first = self.snapshot()
        git('add','.'); git('commit','-m','fixture')
        second = self.snapshot('2026-10-02'); git('add','.')
        self.assertEqual(paths.discover('futures','data-snapshot','2026-10-05',self.root,committed=True),[first])
        first.write_text(first.read_text().replace('header','edited header'))
        self.assertEqual(paths.discover('futures','data-snapshot','2026-10-05',self.root,committed=True),[])

    def produce(self, day='2026-10-01'):
        stamp = day.replace('-', '')
        print(f'== header AS_OF={stamp} ==')
        print(f'== 快照完成 | AS_OF={stamp} | done ==')

    def test_success_is_atomic_and_does_not_replace_existing_file(self):
        dest=paths.artifact_path('futures','data-snapshot','20261001',self.root)
        with redirect_stdout(io.StringIO()), paths.snapshot_output(dest,'20261001'):
            self.assertFalse(dest.exists()); self.produce()
        original=dest.read_bytes()
        with self.assertRaises(FileExistsError), paths.snapshot_output(dest,'20261001'):
            self.fail('must refuse before producer runs')
        self.assertEqual(dest.read_bytes(),original)
        self.assertEqual(list(dest.parent.glob('*.partial')),[])

    def test_failure_keeps_old_snapshot_and_failed_partial(self):
        dest=self.snapshot(); original=dest.read_bytes()
        with self.assertRaises(RuntimeError), redirect_stdout(io.StringIO()):
            with paths.snapshot_output(dest,'20261001',overwrite=True):
                print('partial run'); raise RuntimeError('network unavailable')
        self.assertEqual(dest.read_bytes(),original)
        self.assertEqual(len(list(dest.parent.glob('*.partial'))),1)

    def test_no_marker_or_wrong_date_never_publishes(self):
        dest=paths.artifact_path('etf','data-snapshot','20261001',self.root)
        for text in ['no marker','== header AS_OF=20261002 ==\n== 快照完成 | AS_OF=20261002 ==']:
            with self.assertRaises(ValueError), redirect_stdout(io.StringIO()):
                with paths.snapshot_output(dest,'20261001'): print(text)
            self.assertFalse(dest.exists())

    def test_concurrent_publisher_is_not_overwritten(self):
        dest=paths.artifact_path('etf','data-snapshot','20261001',self.root)
        with self.assertRaises(FileExistsError), redirect_stdout(io.StringIO()):
            with paths.snapshot_output(dest,'20261001'):
                self.produce(); dest.write_text('other winner')
        self.assertEqual(dest.read_text(),'other winner')

    def company(self, day, report=True, revision=None):
        p=paths.company_path('HK','01952',day,'price-map',self.root,revision=revision)
        self.write(p,json.dumps({'schema_version':'stock-research/v1','valuation_date':day}))
        if report: self.write(paths.company_path('HK','01952',day,'research',self.root,revision=revision))
        return p

    def test_company_discovery_works_without_index_and_skips_incomplete_and_isolated(self):
        first=self.company('2026-10-01')
        self.company('2026-10-02',report=False)
        self.company('2026-10-03',revision=2)
        self.company('2026-10-07')
        malformed=self.company('2026-10-04'); malformed.write_text('[]')
        self.assertEqual(paths.company_runs('HK','01952','2026-10-05',self.root),[first])
        paths.rebuild_indexes('2026-10-05',self.root)
        index=self.root/'output/indexes/investment/HK-01952/investment-01952-latest.json'
        self.assertEqual(json.loads(index.read_text()),json.loads(first.read_text()))
        index.unlink()
        self.assertEqual(paths.company_runs('HK','01952','2026-10-05',self.root),[first])

    def company_v2(self, market, code, day, revision=None):
        from scripts.stock_price_map import build_document
        report = paths.company_path(market, code, day, 'research', self.root, revision=revision)
        price_map = paths.company_path(market, code, day, 'price-map', self.root, revision=revision)
        currency = 'HKD' if market == 'HK' else 'CNY'
        document = build_document({
            'meta': dict(code=f'{code}.{market}', name='Offline fixture', valuation_date=day,
                         currency=currency, report_path=report.relative_to(self.root).as_posix()),
            'mode': 'tracking', 'reason': 'Offline fixture',
            'valuation': dict(kind='per_share', values=dict(low=10, base=20, high=30),
                              currency=currency, unit='per_share', fx_to_quote=1),
            'discounts': dict(d_base=0.1, r_chip=0, r_v5=0, r_gov=0, r_terminal=0),
            'step_down': 0.05, 'p2': dict(status='active', reason=None),
            't1': dict(price_condition='Review valuation', events=['Earnings release']),
            't2': dict(price_condition='Review valuation', events=['Thesis invalidation']),
            'monitoring': [dict(variable='Margin', current=None, as_of=None,
                                trigger='Margin deterioration', action='Revalue',
                                source='Offline fixture', next_check='Next report')],
        })
        self.write(report, 'Offline report')
        self.write(price_map, json.dumps(document))
        return price_map

    def test_v2_builder_outputs_are_discovered_and_indexes_keep_newest_valid_pair(self):
        for market, code in [('SH', '600066'), ('SZ', '000001'), ('HK', '01952')]:
            with self.subTest(market=market):
                first = self.company_v2(market, code, '2026-10-01')
                newest = self.company_v2(market, code, '2026-10-03')
                self.company_v2(market, code, '2026-10-04', revision=2)
                self.company_v2(market, code, '2026-10-07')
                self.assertEqual(paths.company_runs(market, code, '2026-10-05', self.root),
                                 [first, newest])
                paths.rebuild_indexes('2026-10-05', self.root)
                index = self.root / f'output/indexes/investment/{market}-{code}/investment-{code}-latest.json'
                self.assertEqual(json.loads(index.read_text()), json.loads(newest.read_text()))
                index.unlink()
                self.assertEqual(paths.company_runs(market, code, '2026-10-05', self.root)[-1], newest)

    def test_v2_discovery_rejects_wrong_identity_date_path_and_incomplete_pairs(self):
        path = self.company_v2('SH', '600066', '2026-10-03')
        original = path.read_text()
        for field, value in [('code', '600066.SZ'), ('code', '600067.SH'),
                             ('code', '600066'), ('valuation_date', '2026-10-02'),
                             ('report_path', 'research/different-report.md')]:
            with self.subTest(field=field, value=value):
                document = json.loads(original)
                document['meta'][field] = value
                path.write_text(json.dumps(document))
                self.assertEqual(paths.company_runs('SH', '600066', '2026-10-05', self.root), [])
        path.write_text(original)
        report = paths.company_path('SH', '600066', '2026-10-03', 'research', self.root)
        report.write_text(' ')
        self.assertEqual(paths.company_runs('SH', '600066', '2026-10-05', self.root), [])
        report.unlink()
        self.assertEqual(paths.company_runs('SH', '600066', '2026-10-05', self.root), [])

    def test_latest_company_cli_finds_v2_without_latest_cache(self):
        newest = self.company_v2('HK', '01952', '2026-10-03')
        scripts = self.root / 'scripts'
        scripts.mkdir()
        for name in ['research_paths.py', 'stock_price_map.py']:
            shutil.copyfile(paths.ROOT / 'scripts' / name, scripts / name)
        result = subprocess.run([sys.executable, str(scripts / 'research_paths.py'),
                                 'latest-company', '--market', 'HK', '--code', '01952',
                                 '--as-of', '2026-10-05'], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), newest.relative_to(self.root).as_posix())

    def test_etf_index_rebuild_requires_complete_matching_snapshot(self):
        snapshot=self.snapshot(track='etf')
        sidecar=paths.artifact_path('etf','drawdown','20261001',self.root)
        payload={'as_of':'20261001','snapshot':str(snapshot.relative_to(self.root)),'indexes':{}}
        paths.write_json(sidecar,payload)
        self.write(paths.artifact_path('etf','drawdown','20261002',self.root),'not json')
        paths.rebuild_indexes('20261005',self.root)
        index=self.root/'output/indexes/etf/etf-ladder-latest.json'
        self.assertEqual(json.loads(index.read_text()),payload)

    def script_main(self, track, producer):
        """Exercise the real CLI orchestration without importing market-data SDKs."""
        name = 'future_data' if track == 'futures' else 'etf_data'
        tree = ast.parse((paths.ROOT / f'scripts/{name}.py').read_text())
        module = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)
                                  and node.name in {'main', '_valid_date'}], type_ignores=[])
        namespace = dict(argparse=argparse, datetime=datetime, sys=sys, json=json,
                         AS_OF='20261001', CUTOFF='20261001', SCRIPT_VERSION='test', ROOT=self.root,
                         LADDER_ROWS={}, LADDER_SIDECAR=self.root/'output/indexes/etf/etf-ladder-latest.json',
                         artifact_path=lambda t,k,d: paths.artifact_path(t,k,d,self.root),
                         snapshot_output=paths.snapshot_output, write_json=paths.write_json, run=producer)
        exec(compile(module,name,'exec'),namespace)
        return namespace

    def test_both_script_clis_publish_and_refuse_overwrite_before_fetching(self):
        for track in ['futures','etf']:
            calls=[]
            def run(*args):
                calls.append(args); self.produce()
            ns=self.script_main(track,run)
            with patch.object(sys,'argv',['data.py','--as-of','20261001']), redirect_stdout(io.StringIO()):
                ns['main']()
                with self.assertRaises(SystemExit): ns['main']()
            self.assertEqual(len(calls),1)
            self.assertTrue(paths.snapshot_complete(paths.artifact_path(track,'data-snapshot','20261001',self.root),'20261001'))
            if track=='etf':
                self.assertTrue(paths.artifact_path('etf','drawdown','20261001',self.root).is_file())

    def test_both_script_clis_no_snapshot_do_not_publish(self):
        for track in ['futures','etf']:
            calls=[]
            ns=self.script_main(track,lambda *args: calls.append(args))
            with patch.object(sys,'argv',['data.py','--no-snapshot']): ns['main']()
            self.assertIsNone(calls[0][0])
            self.assertFalse((self.root/'research').exists())
            self.assertFalse(ns['LADDER_SIDECAR'].exists())

    def test_etf_failure_does_not_update_sidecar_and_historical_run_does_not_roll_index_back(self):
        def failed(*args):
            print('broken'); raise RuntimeError('provider failed')
        ns=self.script_main('etf',failed)
        with patch.object(sys,'argv',['data.py']), redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError): ns['main']()
        self.assertFalse(ns['LADDER_SIDECAR'].exists())
        self.assertFalse(paths.artifact_path('etf','drawdown','20261001',self.root).exists())
        newer={'as_of':'20261005'}
        paths.write_json(ns['LADDER_SIDECAR'],newer)
        ns=self.script_main('etf',lambda *args: self.produce())
        with patch.object(sys,'argv',['data.py']), redirect_stdout(io.StringIO()): ns['main']()
        self.assertEqual(json.loads(ns['LADDER_SIDECAR'].read_text()),newer)

    def test_preregistration_original_commit_survives_move_and_rejects_changed_content(self):
        from scripts.etf_backtest import ROOT, PREREG
        self.assertIn('dc3ea4a204ec13b40eef3e76658096793b8a348a',etf_backtest.prereg_commit())
        with patch.object(etf_backtest, 'ROOT', self.root):
            self.write(self.root/PREREG,'changed preregistration')
            self.write(self.root/'docs/research-layout-migration.json',
                       (ROOT/'docs/research-layout-migration.json').read_text())
            with patch.object(etf_backtest.subprocess,'run') as run:
                run.return_value.stdout=(ROOT/PREREG).read_bytes()
                with self.assertRaises(SystemExit): etf_backtest.prereg_commit()

    def test_manifest_has_no_lost_files_and_protected_evidence_is_byte_identical(self):
        root=paths.ROOT
        manifest=json.loads((root/'docs/research-layout-migration.json').read_text())
        self.assertEqual(len({r['new'] for r in manifest['files']}),len(manifest['files']))
        for item in manifest['files']:
            # Local indexes may be missing on a fresh clone; all research evidence must exist.
            if item['new'].startswith('output/'): continue
            p=root/item['new']; self.assertTrue(p.is_file(),item['new'])
            if 'compact-audit.json' in p.name or 'compact-numeric-audit.json' in p.name or 'rule-prereg.md' in p.name or p.suffix=='.txt':
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),item['sha256_before'],item['new'])


if __name__ == '__main__': unittest.main()
