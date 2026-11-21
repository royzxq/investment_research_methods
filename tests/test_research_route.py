import copy
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts import dividend_data as dd


class RouteTests(unittest.TestCase):
    def test_methods_candidate_cannot_publish_before_classification(self):
        from scripts.research_candidate_packs import collect
        routing = types.ModuleType('src.analysis.research_strategy')
        routing.build_routed_pack = Mock(side_effect=RuntimeError('classification pending'))
        exchange = types.ModuleType('src.analysis.research_exchange')
        exchange.publish_request = Mock()
        targets = types.ModuleType('src.decision.reeval_targets')
        targets.ReevalTarget = targets.research_trigger = Mock()
        with tempfile.TemporaryDirectory() as temp, patch.dict(sys.modules, {m.__name__:m for m in (routing,exchange,targets)}), patch.object(sys, 'path', sys.path.copy()):
            with self.assertRaisesRegex(RuntimeError, 'classification pending'):
                collect(Path(temp), Path(temp)/'exchange', dict(code='00941.HK',research_on='2026-11-16'))
            routing.build_routed_pack.assert_called_once_with('00941','HK','00941.HK','20261116',Path(temp)/'2026-11-16')
            exchange.publish_request.assert_not_called()
    def test_china_benchmark_market_thresholds_and_separate_valuation(self):
        for value, strategy in [(5.1, 'non_dividend'), (5.11, 'dividend')]:
            def call(ep, params):
                if ep == 'hk_cash_ttm':
                    return [dict(ts_code='00941.HK', trade_date='20261113', dv_ttm=value, dividend_events=[],
                                 evidence_version=2, source=dd.SOURCES['hk_cash_ttm'], coverage={'factor_sessions':249})]
                self.assertEqual(ep, 'chinabond_10y')
                return [{'trade_date':'20261113','yield':1.6}]
            with tempfile.TemporaryDirectory() as tmp:
                route = dd.classify('00941.HK', '20261116', tmp, call)
                self.assertEqual((route['strategy'],route['threshold_pp']), (strategy,3.5))
                addon = dd.build('00941.HK','20261116',tmp,call,route=route)
                self.assertEqual(addon['screening_spread_pp'], route['spread_pp'])
                self.assertIsNone(addon['trailing_spread_pp'])
                with self.assertRaisesRegex(ValueError, 'market date'):
                    dd.build('00941.HK','20261116',tmp,call,route=route,market_as_of='20261114')
                for update in ({'rule':dd.ROUTE_RULE}, {'government_10y':{**route['government_10y'],'currency':'HKD'}}):
                    with self.assertRaises(ValueError):
                        dd.validate_route({**route,**update},'00941.HK','2026-11-16')

    def test_old_provider_cannot_create_tushare_snapshot(self):
        old = dict(ts_code='00941.HK', trade_date='20261113', close=40, dv_ttm=5, dividend_events=[])
        with tempfile.TemporaryDirectory() as tmp:
            route = dd.classify('00941.HK', '20261116', tmp, lambda *args: [old])
            self.assertEqual(route['status'], 'pending')
            self.assertFalse(list(Path(tmp).rglob('*.json')))
            # Restoring an old route can read an old cache, never query a v2 provider on its behalf.
            legacy = dd.fetch('hk_cash_ttm', {'ts_code':'00941.HK'}, tmp, lambda *a: self.fail('queried'))
            self.assertEqual(legacy.get('error_type'), 'ValueError')

    def test_a_route_uses_public_curve_as_only_bond_provider(self):
        def call(endpoint, params):
            if endpoint == 'daily_basic':
                return [dict(ts_code='600900.SH', trade_date='20261113', dv_ttm=4)]
            self.assertEqual(endpoint, 'chinabond_10y')
            self.assertEqual(params, dict(trade_date='20261113'))
            return [{'trade_date': '20261113', 'yield': 1.6}]
        with tempfile.TemporaryDirectory() as tmp:
            route = dd.classify('600900.SH', '20261116', tmp, call)
        self.assertEqual(route['strategy'], 'dividend')
        self.assertEqual(route['government_10y']['source'], dd.SOURCES['chinabond_10y'])
        self.assertEqual(set(route['sources']), {'quote_search', 'daily_basic', 'chinabond_10y'})

    def test_curve_failure_leaves_both_markets_pending_without_another_query(self):
        for code, quote in [('600900.SH', 'daily_basic'), ('00941.HK', 'hk_cash_ttm')]:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                calls = []

                def call(endpoint, params):
                    calls.append(endpoint)
                    if endpoint == quote:
                        row = dict(ts_code=code, trade_date='20261113', dv_ttm=6)
                        if endpoint == 'hk_cash_ttm':
                            row.update(evidence_version=2, source=dd.SOURCES[endpoint],
                                       coverage={'factor_sessions':249}, dividend_events=[])
                        return [row]
                    raise RuntimeError('provider unavailable')

                route = dd.classify(code, '20261116', tmp, call)
                self.assertEqual(route['status'], 'pending')
                self.assertIsNone(route['government_10y'])
                expected = [quote, quote, 'chinabond_10y'] if quote == 'daily_basic' else [quote, 'chinabond_10y']
                self.assertEqual(calls, expected)

    def classify(self, value=4, rate=2, code='600001.SH', **kwargs):
        def call(endpoint, params):
            if endpoint == 'daily_basic':
                return [dict(ts_code=code, trade_date='20261113', dv_ttm=value)]
            if endpoint == 'chinabond_10y':
                return [dict(trade_date='20261113', **{'yield': rate})]
            self.fail('classification must not fetch dividend history')
        with tempfile.TemporaryDirectory() as tmp:
            return dd.classify(code, '20261116', Path(tmp), call, **kwargs)

    def test_threshold_boundary_and_custom(self):
        self.assertEqual(self.classify(4)['strategy'], 'non_dividend')
        self.assertEqual(self.classify(4.01)['strategy'], 'dividend')
        self.assertEqual(self.classify(4.00000000001)['strategy'], 'dividend')
        self.assertEqual(self.classify(3.99)['strategy'], 'non_dividend')
        self.assertEqual(self.classify(4.01, threshold_pp=3)['strategy'], 'non_dividend')
        self.assertEqual(self.classify(0)['strategy'], 'non_dividend')

    def test_missing_is_pending_and_hk_not_substituted(self):
        for value in (None, float('nan'), True, -1):
            self.assertEqual(self.classify(value)['status'], 'pending')
        self.assertEqual(self.classify(code='00700.HK')['status'], 'pending')

    def test_frozen_route_validates_identity_dates_values(self):
        route = self.classify(4.01)
        dd.validate_route(route, '600001.SH', '2026-11-16')
        for field, value in [('strategy', 'non_dividend'), ('spread_pp', 20), ('threshold_pp', True)]:
            bad = {**route, field: value}
            with self.assertRaises(ValueError):
                dd.validate_route(bad, '600001.SH', '2026-11-16')
        for field, value in [('as_of', '2026-11-17'), ('as_of', '2026-11-01'), ('currency', 'HKD'), ('unit', 'ratio')]:
            bad = copy.deepcopy(route)
            bad['trailing_yield'][field] = value
            with self.assertRaises(ValueError):
                dd.validate_route(bad, '600001.SH', '2026-11-16')
        with self.assertRaises(ValueError):
            dd.validate_route(route, '600002.SH', '2026-11-16')

    def test_failures_are_not_cached_and_retry_can_recover(self):
        calls = []
        def call(endpoint, params):
            calls.append(endpoint)
            raise PermissionError('secret must not escape')
        with tempfile.TemporaryDirectory() as tmp:
            for _ in range(2):
                result = dd.classify('600001.SH', '20261116', Path(tmp), call)
                self.assertEqual(result['status'], 'pending')
                self.assertNotIn('secret', str(result))
        self.assertEqual(calls, ['daily_basic', 'daily_basic'])

    def test_recent_quote_selection_refuses_invalid_latest_and_mismatched_bond(self):
        for quotes, bond_day in [
            ([('20261116', None), ('20261113', 5)], '20261113'),
            ([('20261101', 5)], '20261101'),
            ([('20261117', 5)], '20261117'),
            ([('20261113', 5), ('20261113', 6)], '20261113'),
            ([('20261113', 5)], '20261112'),
        ]:
            def call(endpoint, params):
                if endpoint == 'daily_basic':
                    return [dict(ts_code='600001.SH', trade_date=d, dv_ttm=v) for d, v in quotes]
                return [dict(trade_date=bond_day, **{'yield': 2})]
            with tempfile.TemporaryDirectory() as tmp:
                result = dd.classify('600001.SH', '20261116', Path(tmp), call)
                self.assertEqual(result['status'], 'pending')

    def test_addon_uses_market_date_but_preserves_newer_disclosure(self):
        def call(endpoint, params):
            if endpoint == 'daily_basic':
                self.assertEqual(params['trade_date'], '20261113')
                return [dict(ts_code='600001.SH', trade_date='20261113', dv_ttm=5)]
            if endpoint == 'chinabond_10y':
                self.assertEqual(params['trade_date'], '20261113')
                return [dict(trade_date='20261113', **{'yield': 2})]
            return [dict(ts_code='600001.SH', ann_date='20261116', imp_ann_date='20261116', div_proc='实施')]
        with tempfile.TemporaryDirectory() as tmp:
            addon = dd.build('600001.SH', '20261116', Path(tmp), call, market_as_of='20261113')
        self.assertEqual(addon['trailing_yield']['as_of'], '2026-11-13')
        self.assertEqual(len(addon['dividend_events']), 1)
        self.assertEqual(addon['status'], 'complete')

    def test_frozen_addon_reuses_legacy_bond_without_calling_provider(self):
        route = self.classify(5)
        legacy = route['sources'].pop('chinabond_10y')
        legacy_url = 'https://tushare.pro/document/2?doc_id=201'
        route['sources']['yc_cb'] = {**legacy, 'source': legacy_url}
        route['government_10y']['source'] = legacy_url
        calls = []

        def call(endpoint, params):
            calls.append(endpoint)
            return [dict(ts_code='600001.SH', trade_date='20261113', dv_ttm=5)]

        with tempfile.TemporaryDirectory() as tmp:
            addon = dd.build('600001.SH', '20261116', tmp, call, include_dividends=False,
                             market_as_of='20261113', route=route)
        self.assertEqual(calls, ['daily_basic'])
        self.assertEqual(addon['government_10y'], route['government_10y'])
        self.assertEqual(addon['sources']['yc_cb']['source'], legacy_url)
