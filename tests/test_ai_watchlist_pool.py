import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).resolve().parents[1] / 'scripts' / 'check_ai_watchlist_pool.py'


class WatchlistPoolTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        upstream = self.root / 'scripts'
        upstream.mkdir()
        (upstream / '__init__.py').touch()
        (upstream / 'review_stock_pool.py').write_text(
            "import json\ndef build_inputs(root, holdings):\n"
            "    return json.loads((root / 'pool.json').read_text())\n")
        self.pool = dict(created_at='2026-11-22T09:00:00+08:00',
                         sources={'investment_prediction.csv': '1' * 64, 'paused_stocks.csv': '2' * 64},
                         stocks=[dict(code='002475', name='立讯精密', state='active'),
                                 dict(code='02475', name='立讯精密', state='paused'),
                                 dict(code='688041', name='海光信息', state='expired'),
                                 dict(code='02513', name='智谱', state='active'),
                                 dict(code='688256', name='寒武纪', state='active')])
        self.row = dict(name='立讯精密', business='互联', evidence='已交付', check='核应收回款',
                        source_date='2026-11-21', source_title='业绩公告', source_url='https://example.com/ir')
        self.draft = self.root / 'draft.json'

    def check(self, entries=None):
        (self.root / 'pool.json').write_text(json.dumps(self.pool))
        cmd = [sys.executable, str(CHECKER), '--pool-root', str(self.root)]
        if entries is not None:
            self.draft.write_text(json.dumps(dict(available_at=self.pool['created_at'], entries=entries)))
            cmd.extend(['--release', str(self.draft)])
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_active_listings_and_draft_match_by_market(self):
        listed = self.check()
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(set(json.loads(listed.stdout)['active']), {'002475.SZ', '02513.HK', '688256.SH'})
        checked = self.check({'002475.SZ': self.row})
        self.assertEqual(checked.returncode, 0, checked.stderr)
        result = json.loads(checked.stdout)
        self.assertEqual(result['matched_count'], 1)
        self.assertEqual(result['sources'], self.pool['sources'])
        self.assertEqual(result['release_sha256'], hashlib.sha256(self.draft.read_bytes()).hexdigest())
        excluded = self.check({code: self.row for code in ('02475.HK', '688041.SH', '002475.SH')})
        self.assertNotEqual(excluded.returncode, 0)
        self.assertIn('Outside the active stock pool: 002475.SH, 02475.HK, 688041.SH', excluded.stderr)

    def test_incomplete_sources_block_even_empty_draft(self):
        for name in self.pool['sources']:
            with self.subTest(name=name):
                digest = self.pool['sources'][name]
                self.pool['sources'][name] = None
                result = self.check({})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Missing stock pool source: ' + name, result.stderr)
                self.pool['sources'][name] = digest

    def test_membership_alone_cannot_validate_malformed_evidence(self):
        for row in (None, dict(self.row, source_date='2026-11-23'), dict(self.row, check='')):
            with self.subTest(row=row):
                result = self.check({'002475.SZ': row})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('invalid AI watchlist', result.stderr)
