from copy import deepcopy
from pathlib import Path
import hashlib
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_two_price_contract import sample
from scripts import stock_price_map as prices, research_runner as runner


class PublicMonitoringTests(unittest.TestCase):
    def document(self, count=1):
        value = sample()
        value['monitoring'] = [dict(value['monitoring'][0], id=f'v{i}', variable=f'metric{i}',
            source='Company 2026 interim report, financial statements',
            public_search=f'Company 2026 interim report metric{i}') for i in range(count)]
        return value

    def test_new_build_accepts_zero_and_seven_without_padding(self):
        for count in (0, 1, 7):
            value = self.document(count)
            doc = prices.build_document(value)
            self.assertEqual(doc['monitoring'], value['monitoring'])

    def test_new_build_rejects_eight_but_history_ten_is_still_readable(self):
        with self.assertRaisesRegex(ValueError, '0-7'):
            prices.build_document(self.document(8))
        old = prices.build_document(sample())
        old['monitoring'] = [dict(old['monitoring'][0], id=f'old{i}', variable=f'old{i}') for i in range(10)]
        prices.validate_document(old)

    def test_new_delivery_requires_public_search_and_source_but_not_current(self):
        doc = prices.build_document(self.document())
        prices.validate_monitoring_delivery(doc)
        for key in ('source', 'public_search'):
            for bad in (None, '', '   '):
                copy = deepcopy(doc); copy['monitoring'][0][key] = bad
                with self.assertRaisesRegex(ValueError, 'public|source'):
                    prices.validate_monitoring_delivery(copy)
        prices.validate_monitoring_delivery(prices.build_document(self.document(0)))

    def test_public_search_has_to_be_a_nonempty_string_when_declared(self):
        for bad in (None, '', {}, True):
            value = self.document(); value['monitoring'][0]['public_search'] = bad
            with self.assertRaises(ValueError): prices.build_document(value)

    def test_old_acceptance_prompt_is_frozen_and_new_prompt_adds_public_monitoring(self):
        request = dict(batch_id='a'*32, valuation_date='2026-10-06')
        task = dict(task_id='SH-600066', code='600066.SH', name='宇通客车',
            sources=['candidate_review'], data_pack=dict(path='packs/SH-600066.md', sha256='1'*64),
            data_pack_meta=dict(missing_required=['financial.unit']))
        frameworks = {'investment_framework.md': '2'*64, 'investment_framework_compact.md': '3'*64}
        targets = dict(report_path='research/offline-report.md', price_map_path='research/offline-price.json')
        old_contract = dict(runner.OLD_TWO_PRICE_CONTRACT, prompt_template='two-price-controls/v3')
        with patch.object(runner, 'owned_path', side_effect=lambda root, relative: Path(root)/relative):
            args = (request, task, 'claude', '冻结输入正文不可截断\n'.encode(), Path('/offline/research'), frameworks, targets)
            old = runner.make_prompt(*args, research_validation=runner.research_consistency.SCHEMA, delivery=old_contract)
            self.assertEqual(hashlib.sha256(old).hexdigest(), '9cf8614a93cd36acaa1cd77f21cc392e91d863a059a75b7002f14807399f9ee3')
            current = runner.make_prompt(*args, research_validation=runner.research_consistency.SCHEMA)
        self.assertFalse(current == old)
        self.assertIn(b'public_search', current)
        self.assertEqual(runner.NEW_CONTRACT['prompt_template'], 'two-price-controls/v4')
        frozen = dict(delivery_contract=old_contract, research_validation=runner.research_consistency.SCHEMA)
        self.assertEqual(runner.delivery_contract(frozen), old_contract)
