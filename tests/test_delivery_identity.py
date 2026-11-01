"""Frozen execution identity is a writer input, not a fuzzy acceptance rule."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import test_research_runner as fixture
from test_stock_price_map import v4_example
from scripts import research_runner as runner, stock_price_map as price
from scripts.research_exchange import _strict_json


class DeliveryIdentityTests(unittest.TestCase):
    def setUp(self):
        self.f = fixture.ResearchRunnerTests('runTest')
        self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.run = runner.prepare_request(self.f.request_path, self.f.methods)
        self.folder = self.run / 'execution/SH-600066/claude'
        self.targets = json.loads((self.folder / 'targets.json').read_text())
        self.output = runner.staging_root(self.f.methods, self.f.request,
            self.f.request['tasks'][0], 'claude') / self.targets['price_map_path']
        self.output.parent.mkdir(parents=True)
        self.data = v4_example()
        self.data['meta'].update(valuation_date='2026-10-06', generator='claude',
            name='宇通客车（别名）', report_path=self.targets['report_path'])
        self.input = self.f.root / 'writer-input.json'

    def build(self, data=None, output=None, folder=None):
        self.input.write_text(json.dumps(data or self.data))
        return price.main(['build', '--input', str(self.input), '--output', str(output or self.output),
            '--generator', 'claude', '--execution-folder', str(folder or self.folder)])

    def test_build_binds_name_and_check_matches_final_acceptance_identity(self):
        original = deepcopy(self.data)
        self.assertEqual(self.build(), 0)
        document = json.loads(self.output.read_text())
        self.assertEqual(document['meta']['name'], '宇通客车')
        self.assertEqual(json.loads(self.input.read_text()), original)
        self.assertEqual(price.main(['check', str(self.output), '--execution-folder', str(self.folder)]), 0)
        document['meta']['name'] = '宇通客车（别名）'
        self.output.write_text(json.dumps(document))
        self.assertEqual(price.main(['check', str(self.output), '--execution-folder', str(self.folder)]), 1)

    def test_wrong_identity_is_rejected_before_name_binding_or_write(self):
        for field, value in [('code', '600066.SZ'), ('code', '00001.HK'),
                             ('valuation_date', '2026-10-05'), ('generator', 'codex'),
                             ('report_path', 'research/other.md')]:
            data = deepcopy(self.data); data['meta'][field] = value
            with self.subTest(field=field, value=value):
                self.assertEqual(self.build(data), 1)
                self.assertFalse(self.output.exists())
        self.assertEqual(self.build(output=self.output.with_name('wrong.json')), 1)
        self.assertFalse(self.output.exists())

    def test_changed_frozen_inputs_and_symlinks_are_rejected(self):
        for path in (self.folder/'input.json', self.folder/'targets.json', self.run/'request.json'):
            original = path.read_bytes()
            try:
                value = json.loads(original)
                if path.name == 'request.json': value['tasks'][0]['name'] = 'changed'
                else: value['extra'] = 'changed'
                path.write_text(json.dumps(value))
                with self.subTest(path=path.name):
                    self.assertEqual(self.build(), 1)
                    self.assertFalse(self.output.exists())
            finally: path.write_bytes(original)
            outside = self.f.root / ('linked-' + path.name)
            outside.write_bytes(original)
            path.unlink(); path.symlink_to(outside)
            try:
                self.assertEqual(self.build(), 1)
            finally:
                path.unlink(); path.write_bytes(original)

    def test_retry_cannot_write_first_attempt_target(self):
        retry = self.folder / 'retry-1'; retry.mkdir()
        for name in ('prompt.txt', 'targets.json', 'receipt-schema.json', 'input.json'):
            (retry/name).write_bytes((self.folder/name).read_bytes())
        retry_output = runner.staging_root(self.f.methods, self.f.request,
            self.f.request['tasks'][0], 'claude', 2) / self.targets['price_map_path']
        retry_output.parent.mkdir(parents=True)
        self.assertEqual(self.build(output=retry_output, folder=retry), 0)
        self.assertEqual(self.build(folder=retry), 1)
        self.assertFalse(self.output.exists())

    def test_standalone_build_retains_explicit_name(self):
        self.input.write_text(json.dumps(self.data))
        self.assertEqual(price.main(['build', '--input', str(self.input), '--output', str(self.output),
                                    '--generator', 'claude']), 0)
        self.assertEqual(json.loads(self.output.read_text())['meta']['name'], self.data['meta']['name'])

    def test_json_diagnostic_names_source_without_echoing_content(self):
        for raw in (b'not-json-sensitive', b'\xff', b'{"sensitive":1,"sensitive":2}', b'{"x":NaN}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError) as error:
                _strict_json(raw, 'DSH final research receipt')
            self.assertIn('DSH final research receipt', str(error.exception))
            self.assertNotIn('not-json-sensitive', str(error.exception))
            self.assertNotIn('sensitive', str(error.exception))

    def test_attempt_directory_and_output_symlinks_are_rejected(self):
        alias = self.folder.parent/'linked'
        alias.symlink_to(self.folder, target_is_directory=True)
        self.assertEqual(self.build(folder=alias), 1)
        target = self.f.root/'outside.json'; target.write_text('preserve')
        self.output.symlink_to(target)
        self.assertEqual(self.build(), 1)
        self.assertEqual(target.read_text(), 'preserve')


if __name__ == '__main__':
    unittest.main()
