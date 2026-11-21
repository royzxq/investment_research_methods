import copy
import json
from pathlib import Path
import tempfile
import unittest
from scripts import dividend_data as data


class DividendDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name)
        self.calls = []
        self.rows = {
            'daily_basic': [dict(ts_code='600900.SH', trade_date='20261116', dv_ttm=4.4)],
            'chinabond_10y': [dict(trade_date='20261116', **{'yield': 1.6285})],
            'dividend': [dict(ts_code='600900.SH', ann_date='20260301', imp_ann_date='20260501',
                             div_proc='实施', cash_div_tax=1, ex_date='20260601', pay_date='20260602')]}

    def call(self, endpoint, params):
        self.calls.append((endpoint, params)); return copy.deepcopy(self.rows[endpoint])

    def build(self, code='600900.SH', as_of='20261116'):
        return data.build(code, as_of, self.cache, self.call)

    def test_percent_points_no_forecast_and_shared_curve_cache(self):
        a = self.build()
        self.assertAlmostEqual(a['trailing_spread_pp'], 2.7715)
        self.assertEqual(a['status'], 'complete')
        for key in ('forward_ordinary_dividend', 'forward_net_yield', 'history_percentile'):
            self.assertIsNone(a[key])
        self.assertFalse(a['strict_point_in_time'])
        self.assertNotIn('rows', a['sources']['dividend'])
        self.rows['daily_basic'][0]['ts_code'] = '600066.SH'
        self.rows['dividend'][0]['ts_code'] = '600066.SH'
        self.build('600066.SH')
        self.assertEqual(sum(name == 'chinabond_10y' for name, _ in self.calls), 1)

    def test_dividend_cache_does_not_hide_next_day_disclosures(self):
        self.build(); self.build(as_of='20261117')
        self.assertEqual(sum(name == 'dividend' for name, _ in self.calls), 2)

    def test_old_announcement_with_future_implementation_not_used(self):
        row = self.rows['dividend'][0]
        row.update(imp_ann_date='20261201')
        a = self.build()
        self.assertEqual(a['dividend_events'], [])
        self.assertEqual(a['excluded_dividend_rows'], 1)
        self.assertEqual(a['status'], 'partial')
        self.assertNotIn('20261201', json.dumps(a))

    def test_missing_known_date_or_wrong_security_not_assumed_visible(self):
        self.rows['dividend'] += [dict(self.rows['dividend'][0], ts_code='600066.SH')]
        self.rows['dividend'][0]['imp_ann_date'] = None
        self.assertEqual(self.build()['excluded_dividend_rows'], 2)

    def test_unknown_special_and_investor_tax_never_automatic(self):
        a = self.build()['dividend_events'][0]
        self.assertEqual(a['ordinary_or_special'], 'unverified')
        self.assertFalse(a['investor_net_cash_verified'])

    def test_exact_duplicate_not_doubled_but_versions_preserved_for_review(self):
        row = self.rows['dividend'][0]
        self.rows['dividend'] += [dict(row), dict(row, cash_div_tax=2)]
        self.assertEqual(len(self.build()['dividend_events']), 2)

    def test_units_currency_date_term_and_missing_are_not_spreads(self):
        s = dict(value=4.4, unit='percent', currency='CNY', as_of='2026-11-16')
        b = dict(value=1.6, unit='percent', currency='CNY', as_of='2026-11-16', tenor_years=10, curve_type='government_ytm')
        for patch in ({'currency':'HKD'}, {'unit':'decimal'}, {'as_of':'2026-11-15'},
                      {'value':None}, {'value':float('nan')}, {'tenor_years':5}, {'curve_type':'spot'}):
            with self.subTest(patch=patch):
                self.assertIsNone(data.same_day_spread(s, dict(b, **patch)))
        self.assertEqual(data.same_day_spread(dict(s,value=0),b), -1.6)

    def test_duplicate_rate_returns_gap(self):
        self.rows['chinabond_10y'] *= 2
        self.assertIsNone(self.build()['trailing_spread_pp'])

    def test_date_mismatch_never_forward_filled(self):
        self.rows['chinabond_10y'][0]['trade_date'] = '20261113'
        self.assertIsNone(self.build()['trailing_spread_pp'])

    def test_permission_failure_does_not_echo_secret_or_cache_failure(self):
        def denied(*args): raise RuntimeError('TOKEN-secret-secret')
        a = data.build('600900.SH', '20261116', self.cache, denied)
        self.assertEqual(a['status'], 'partial')
        self.assertIsNone(a['trailing_spread_pp'])
        self.assertNotIn('secret', json.dumps(a))
        self.assertFalse(list(self.cache.rglob('*.json')))

    def test_empty_is_unknown_and_limit_is_possible_truncation(self):
        self.rows['dividend'] = []
        a = self.build(); self.assertEqual(a['sources']['dividend']['status'], 'empty')
        self.rows['dividend'] = [dict(ts_code='600900.SH')] * 2000
        a = self.build(); self.assertEqual(a['sources']['dividend']['status'], 'possibly_truncated')
        self.assertEqual(a['dividend_events'], [])

    def test_hk_no_a_share_calls(self):
        self.assertEqual(self.build('00941.HK')['status'], 'partial')
        self.assertEqual([ep for ep, params in self.calls], ['hk_cash_ttm'])

    def test_tampered_cache_rejected_and_output_not_overwritten(self):
        a = self.build()
        p = Path(a['sources']['chinabond_10y']['cache_path'])
        d = json.loads(p.read_text()); d['rows'][0]['yield'] = 0; p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError,'cache'): self.build()
        out = self.cache/'output.json'; data.write_once(out, a)
        with self.assertRaises(FileExistsError): data.write_once(out, {})
        self.assertEqual(json.loads(out.read_text()), a)
