from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import stock_disclosure_evidence as evidence


class StockEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.filing = dict(title='三季度报告', date='2026-10-30',
                           pdf_url='https://static.cninfo.com.cn/finalpage/2026-10-30/report.PDF')
        self.raw = dict(symbol='002594', market='A', source='cninfo', requested_category='all',
                        start_date='2026-08-03', end_date='2026-10-31', total=1, truncated=False,
                        announcements=[self.filing])
        self.positions = [dict(code='603986', name='兆易创新', weight_pct=7.82)]
        self.coverage = 'all received source-table equity rows; completeness is not independently verified'
        self.fund = dict(symbol='512480', market='A', disclosed_equity_report=dict(
            as_of='2026-06-30', position_count=1, equity_positions=self.positions, coverage=self.coverage))
        self.proof = dict(period='2026-06-30', published='2026-08-31', original='https://example.org/fund.pdf')

    def filings(self, **changes):
        with patch.object(evidence, 'query', return_value=dict(self.raw, **changes)) as query:
            result = evidence.filings(Path('.'), '002594.SZ', '2026-10-31')
        args = query.call_args.args[1]
        self.assertEqual(args[args.index('--category') + 1], 'all')
        return result

    def test_distinct_corrections_and_inclusive_dates(self):
        correction = dict(self.filing, title='更正公告', pdf_url=self.filing['pdf_url'] + '2')
        report = self.filings(total=3, announcements=[self.filing, self.filing, correction])
        self.assertEqual((report['status'], len(report['filings'])), ('indexed', 2))
        self.assertEqual(report['start_date'], self.raw['start_date'])

    def test_identity_range_truncation_and_empty(self):
        self.assertEqual(self.filings(symbol='000001')['status'], 'unavailable')
        self.assertEqual(self.filings(source='other')['status'], 'unavailable')
        self.assertEqual(self.filings(truncated=True)['status'], 'partial')
        self.assertEqual(self.filings(total=2)['status'], 'partial')
        result = self.filings(announcements=[dict(self.filing, date='2026-11-01')])
        self.assertEqual((result['status'], result['filings']), ('partial', []))
        self.assertEqual(self.filings(total=0, announcements=[])['status'], 'empty_unconfirmed')

    def holdings(self, *, stock='603986.SH', day='2026-11-24', data=None, **proof):
        with patch.object(evidence, 'query', return_value=self.fund if data is None else data):
            return evidence.etf_holdings(Path('.'), '512480.SH', day, stock, **proof)

    def test_publication_cutoff_and_full_table(self):
        cases = [(self.holdings(), 'verify_original_publication'),
                 (self.holdings(day='2026-08-30', **self.proof), 'unavailable_at_cutoff'),
                 (self.holdings(day='2026-06-01'), 'unavailable_at_cutoff'),
                 (self.holdings(**dict(self.proof, period='2025-12-31')), 'different_report_period')]
        for result, status in cases:
            self.assertEqual(result['status'], status)
            self.assertIsNone(result['weight_pct'])
            self.assertNotIn('positions', result)
        self.assertEqual(self.holdings(day='2026-08-31', **self.proof)['weight_pct'], 7.82)
        table = self.holdings(stock=None, original_position_count=1, **self.proof)
        self.assertEqual(table['positions'], self.positions)
        self.assertEqual(table['coverage'], self.coverage)
        self.assertEqual(table['coverage_status'], 'verified_against_original')

    def test_overlap_rejects_position_count_based_only_on_received_rows(self):
        data = deepcopy(self.fund)
        data['disclosed_equity_report'].update(
            position_count=10,
            equity_positions=[dict(code=f'{600000 + i}', name=f'证券{i}', weight_pct=1) for i in range(10)])
        verified = self.holdings(stock=None, original_position_count=1, **self.proof)
        for count, status in [(None, 'unverified'), (120, 'count_mismatch')]:
            with self.subTest(count=count):
                table = self.holdings(stock=None, data=data, original_position_count=count, **self.proof)
                self.assertEqual(table['coverage_status'], status)
                self.assertEqual(table['coverage'], self.coverage)
                self.assertEqual(table['position_count'], 10)
                self.assertEqual(len(table['positions']), 10)
                with self.assertRaisesRegex(ValueError, 'verified_against_original_reports'):
                    evidence.compare_funds(verified, dict(table, fund='159995.SZ'))

    def test_original_position_count_requires_dated_report_and_positive_integer(self):
        with self.assertRaisesRegex(ValueError, 'original_position_count_requires_dated_report'):
            self.holdings(original_position_count=1)
        for count in (0, -1, True, '1'):
            with self.subTest(count=count), self.assertRaisesRegex(ValueError, 'positive_count'):
                self.holdings(original_position_count=count, **self.proof)

    def test_unknown_security_wrong_table_or_duplicate(self):
        self.assertEqual(self.holdings(stock='000001.SZ', **self.proof)['status'], 'stock_exposure_unknown')
        self.assertEqual(self.holdings(data={'holdings': self.positions}, **self.proof)['status'], 'unavailable')
        data = deepcopy(self.fund)
        data['disclosed_equity_report']['equity_positions'] *= 2
        self.assertEqual(self.holdings(data=data, **self.proof)['status'], 'unavailable')
        data['disclosed_equity_report']['position_count'] = 2
        self.assertEqual(self.holdings(data=data, **self.proof)['status'], 'stock_exposure_unknown')

    def test_common_weights_use_minimum_and_exclude_ambiguous_or_misaligned_rows(self):
        left = self.holdings(stock=None, original_position_count=1, **self.proof)
        second = dict(left, fund='159995.SZ', positions=[dict(self.positions[0], weight_pct=5)])
        self.assertEqual(evidence.compare_funds(left, second)['observed_common_nav_pct'], 5)
        double = dict(second, position_count=2, original_position_count=2, positions=second['positions'] * 2)
        result = evidence.compare_funds(left, double)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['unresolved_common_codes'], ['603986'])
        self.assertEqual(result['common_positions'], [])
        for other in (left, dict(second, stock='603986.SH'), dict(second, original_position_count=2),
                      dict(second, cutoff='2026-11-01'),
                      dict(second, report_period='2025-12-31'), dict(second, status='unavailable_at_cutoff')):
            with self.assertRaises(ValueError):
                evidence.compare_funds(left, other)

    def test_provider_failure_falls_back_but_cancellation_propagates(self):
        for error, status in [(ValueError('provider_timeout'), 'unavailable'), (OSError(), 'unavailable')]:
            with patch.object(evidence, 'query', side_effect=error):
                self.assertEqual(evidence.filings(Path('.'), '01211.HK', '2026-10-31')['status'], status)
        with patch.object(evidence, 'query', side_effect=InterruptedError()), self.assertRaises(InterruptedError):
            evidence.filings(Path('.'), '01211.HK', '2026-10-31')
