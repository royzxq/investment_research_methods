"""Offline quote-provenance regressions; never import the API script module."""

import ast
from datetime import datetime, timezone, timedelta
import io
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.price_evidence import select_price, weekly_price_evidence, spread_change_series, completed_day_cutoff
from scripts.price_evidence import sample_coverage, validate_unique_trade_dates, calendar_window


def quote(day, settle, close=None):
    return {"trade_date": day, "settle": settle, "close": close}


def pair_records():
    dates = ["20260824", "20260825", "20260826", "20260827", "20260828",
             "20260831", "20260901", "20260902", "20260903", "20260904", "20260907"]
    return [dict(trade_date=day, spread=-20 + i * 3,
                 near_contract="MA2610", far_contract="MA2701",
                 price_basis_n="settle", price_basis_f="settle")
            for i, day in enumerate(dates)]


class WeeklyEvidenceTests(unittest.TestCase):
    def test_incomplete_current_day_and_future_days_are_cut_off(self):
        china = timezone(timedelta(hours=8))
        self.assertEqual(completed_day_cutoff(datetime(2026, 9, 7, 9, tzinfo=china)), "20260906")
        self.assertEqual(completed_day_cutoff(datetime(2026, 9, 7, 18, tzinfo=china)), "20260907")

    def test_invalid_settlement_fallback_is_disclosed(self):
        for missing in (None, float("nan"), float("inf"), 0, -1, True, "invalid"):
            with self.subTest(missing=missing):
                self.assertEqual(select_price(missing, 123), (123, "close"))
                self.assertEqual(select_price(missing, None), (None, "unknown"))
        self.assertEqual(select_price(100, 123), (100, "settle"))

    def test_weekend_asof_uses_actual_fridays_and_raw_settlement(self):
        result = weekly_price_evidence([quote("20260828", 100, 110),
                                        quote("20260904", 110, 150)], "20260906")
        self.assertEqual(result["start_date"], "20260828")
        self.assertEqual(result["end_date"], "20260904")
        self.assertEqual(result["start_basis"], "settle")
        self.assertEqual(result["settlement_status"], "available")
        self.assertAlmostEqual(result["settlement_change_pct"], 10)

    def test_monday_research_anchors_to_friday_market_day(self):
        rows = [quote("20260828", 100), quote("20260831", 105), quote("20260904", 110)]
        result = weekly_price_evidence(rows, "20260907")
        self.assertEqual(result["market_trade_date"], "20260904")
        self.assertEqual(result["anchor_date"], "20260828")
        self.assertEqual(result["start_date"], "20260828")
        self.assertEqual(result["settlement_change_pct"], 10)

    def test_explicit_unfinished_day_does_not_shift_anchor(self):
        rows = [quote("20260828", 100), quote("20260831", 105), quote("20260904", 110),
                quote("20260907", 120) | {"is_complete": False}]
        result = weekly_price_evidence(rows, "20260907")
        self.assertEqual(result["market_trade_date"], "20260904")
        self.assertEqual(result["start_date"], "20260828")
        self.assertEqual(result["settlement_change_pct"], 10)

    def test_either_missing_settlement_cannot_trigger_oil_guard_from_close(self):
        for missing_endpoint in (0, 1):
            for value in (None, 0, float("nan"), float("inf"), -5):
                with self.subTest(endpoint=missing_endpoint, value=value):
                    rows = [quote("20260828", 100, 100), quote("20260904", 110, 130)]
                    rows[missing_endpoint]["settle"] = value
                    result = weekly_price_evidence(rows, "20260904")
                    self.assertIsNotNone(result["reference_change_pct"])
                    self.assertIsNone(result["settlement_change_pct"])
                    self.assertEqual(result["settlement_status"], "unknown")
                    self.assertEqual(result["start_basis" if missing_endpoint == 0 else "end_basis"], "close")

    def test_strict_guard_preserves_threshold_precision(self):
        for end, expected in ((108, 8), (108.004, 8.004)):
            result = weekly_price_evidence([quote("20260828", 100), quote("20260904", end)], "20260904")
            self.assertEqual(result["settlement_change_pct"], expected)

    def test_missing_endpoint_is_not_replaced_by_earlier_valid_settlement(self):
        rows = [quote("20260827", 95, 95), quote("20260828", None, 100),
                quote("20260903", 105, 105), quote("20260904", None, 130)]
        result = weekly_price_evidence(rows, "20260904")
        self.assertEqual((result["start_date"], result["end_date"]), ("20260828", "20260904"))
        self.assertIsNone(result["settlement_change_pct"])

    def test_holiday_uses_calendar_week_anchor_not_five_observations(self):
        rows = [quote("20260925", 100), quote("20260928", 102),
                quote("20260929", 103), quote("20260930", 110), quote("20261009", 121)]
        result = weekly_price_evidence(rows, "20261009")
        self.assertEqual(result["anchor_date"], "20261002")
        self.assertEqual(result["start_date"], "20260930")
        self.assertAlmostEqual(result["settlement_change_pct"], 10)

    def test_empty_missing_baseline_or_stale_week_returns_unknown(self):
        for rows in ([], [quote("20260904", 110)], [quote("20260828", 100)]):
            result = weekly_price_evidence(rows, "20260904")
            self.assertIsNone(result["settlement_change_pct"])
            self.assertIsNone(result["reference_change_pct"])

    def test_future_quotes_are_not_used(self):
        result = weekly_price_evidence([quote("20260907", 999), quote("20260904", 110),
                                        quote("20260828", 100)], "20260904")
        self.assertEqual(result["end_date"], "20260904")
        self.assertAlmostEqual(result["settlement_change_pct"], 10)

    def test_duplicate_dates_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_trade_date"):
            weekly_price_evidence([quote("20260904", 100), quote("20260904", 200)], "20260904")


class SpreadChangeTests(unittest.TestCase):
    def changes(self, rows, calendar=None):
        if calendar is None:
            calendar = [row["trade_date"] for row in pair_records()]
        return spread_change_series(rows, "MA2610", "MA2701", calendar)

    def test_one_five_ten_sessions_are_same_pair_absolute_changes(self):
        result = self.changes(pair_records())[-1]
        self.assertEqual([result[f"spread_change_{n}td"] for n in (1, 5, 10)], [3, 15, 30])
        self.assertEqual(result["spread_change_5td_from"], "20260831")

    def test_lookback_shortfall_is_null_not_zero(self):
        result = self.changes(pair_records()[-3:])[-1]
        self.assertEqual(result["spread_change_1td"], 3)
        self.assertIsNone(result["spread_change_5td"])
        self.assertIsNone(result["spread_change_10td"])

    def test_missing_internal_session_does_not_compress_window(self):
        rows = pair_records()
        del rows[7]
        result = self.changes(rows)[-1]
        self.assertEqual(result["spread_change_1td"], 3)
        self.assertIsNone(result["spread_change_5td"])
        self.assertEqual(result["spread_change_5td_status"], "missing_pair_sessions")

    def test_calendar_unavailable_does_not_invent_business_days(self):
        result = self.changes(pair_records(), [])[-1]
        self.assertIsNone(result["spread_change_1td"])
        self.assertEqual(result["spread_change_1td_status"], "calendar_unavailable")

    def test_roll_pair_or_missing_identity_is_rejected(self):
        for near, far in (("MA2701", "MA2705"), (None, None)):
            rows = pair_records()
            rows[0].update(near_contract=near, far_contract=far)
            with self.assertRaisesRegex(ValueError, "mixed_or_unidentified_contract_pair"):
                self.changes(rows)

    def test_basis_change_cannot_appear_as_structural_reversal(self):
        rows = pair_records()
        rows[-1]["price_basis_n"] = "close"
        result = self.changes(rows)[-1]
        self.assertIsNone(result["spread_change_1td"])
        self.assertEqual(result["spread_change_1td_status"], "price_basis_changed_or_unknown")

    def test_consistent_close_basis_is_disclosed_and_comparable(self):
        rows = pair_records()
        for row in rows:
            row["price_basis_n"] = "close"
        self.assertEqual(self.changes(rows)[-1]["spread_change_5td"], 15)

    def test_invalid_internal_spread_cannot_be_skipped(self):
        rows = pair_records()
        rows[-2]["spread"] = float("nan")
        result = self.changes(rows)[-1]
        self.assertIsNone(result["spread_change_1td"])
        self.assertEqual(result["spread_change_1td_status"], "invalid_spread")

    def test_falling_high_spread_reports_negative_change(self):
        rows = pair_records()
        for i, row in enumerate(rows):
            row["spread"] = 500 - i * 2
        result = self.changes(rows)[-1]
        self.assertEqual(result["spread_change_1td"], -2)
        self.assertEqual(result["spread_change_10td"], -20)


class SampleCoverageTests(unittest.TestCase):
    def test_forty_of_forty_one_passes_with_warning(self):
        result = sample_coverage([40, 41, 40])
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["minimum_per_year"], 33)
        self.assertEqual(result["missing_fields"], [])
        self.assertEqual(len(result["warnings"]), 2)
        self.assertEqual(result["actual_counts"], [40, 41, 40])

    def test_each_year_must_pass_and_cannot_be_rescued_by_other_years(self):
        self.assertEqual(sample_coverage([33, 33, 33])["status"], "complete")
        result = sample_coverage([32, 41, 41])
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("year_1:below_minimum:32/33", result["missing_fields"])

    def test_missing_year_does_not_shorten_fixed_reference_window(self):
        for counts in ([41, 41], [41, None, 41], []):
            with self.subTest(counts=counts):
                self.assertEqual(sample_coverage(counts)["status"], "incomplete")

    def test_invalid_counts_cannot_look_like_valid_sample_coverage(self):
        for bad in (True, False, "40", 40.0, -1, 42, float("nan")):
            with self.subTest(bad=bad):
                result = sample_coverage([41, bad, 41])
                self.assertEqual(result["status"], "incomplete")
                self.assertIn("year_2:invalid_or_unknown_count", result["missing_fields"])

    def test_duplicate_or_malformed_dates_are_not_silently_deduplicated(self):
        for dates in (["20260904", "20260904"], ["20260230"], ["2026-09-04"], [20260904]):
            with self.subTest(dates=dates):
                with self.assertRaises(ValueError):
                    validate_unique_trade_dates(dates)


def isolated_functions(names, namespace):
    """Compile function definitions only, skipping script imports/config/token."""
    tree = ast.parse((ROOT / "scripts" / "future_data.py").read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    module = ast.Module(body=nodes, type_ignores=[])
    exec(compile(module, "future_data.py:isolated", "exec"), namespace)
    return namespace


class ScriptIntegrationTests(unittest.TestCase):
    def test_missing_nine_calendar_sessions_cannot_be_filled_from_outside_window(self):
        import pandas as pd

        calendar = pd.bdate_range("20250101", "20251231").strftime("%Y%m%d").tolist()
        expected = calendar_window(calendar, "20250904")
        absent = set(expected["trading_dates"][2:11])
        # Plenty of prices outside the fixed window must not repair the gap.
        frame = pd.DataFrame({"trade_date": [day for day in calendar if day not in absent]})
        ns = isolated_functions({"window_around"}, dict(
            _trade_cal=lambda: calendar, CAL_DEGRADED=[], calendar_window=calendar_window,
            validate_unique_trade_dates=validate_unique_trade_dates))
        result = ns["window_around"](frame, "20250904", 20)
        self.assertEqual(len(result), 32)
        self.assertEqual(sample_coverage([len(result), 41, 41])["status"], "incomplete")
        self.assertTrue(set(result["trade_date"]) <= set(expected["trading_dates"]))
        self.assertEqual(result.attrs["sample_window"]["window_start"], expected["window_start"])

    def test_degraded_calendar_cannot_validate_a_fixed_historical_window(self):
        import pandas as pd

        calendar = pd.bdate_range("20250101", "20251231").strftime("%Y%m%d").tolist()
        ns = isolated_functions({"window_around"}, dict(
            _trade_cal=lambda: calendar, CAL_DEGRADED=["calendar_unverified"],
            calendar_window=calendar_window, validate_unique_trade_dates=validate_unique_trade_dates))
        with self.assertRaisesRegex(ValueError, "交易日历已降级"):
            ns["window_around"](pd.DataFrame({"trade_date": calendar}), "20250904", 20)

    def test_daily_preserves_open_and_price_basis_without_an_api_import(self):
        import pandas as pd
        received = {}

        def fake_daily(**kwargs):
            received.update(kwargs)
            return pd.DataFrame([quote("20260904", None, 130) | {"open": 125}])

        ns = isolated_functions({"daily"}, dict(
            select_price=select_price, _daily_cache={}, resolve=lambda sym: sym,
            AS_OF="20260907", completed_day_cutoff=lambda: "20260906",
            validate_unique_trade_dates=validate_unique_trade_dates,
            api=lambda: SimpleNamespace(fut_daily=fake_daily),
            time=SimpleNamespace(sleep=lambda n: None)))
        result = ns["daily"]("SC2610")
        self.assertIn("open", received["fields"].split(","))
        self.assertEqual(result.iloc[0]["open"], 125)
        self.assertEqual(result.iloc[0]["price_basis"], "close")
        self.assertEqual(result.iloc[0]["px"], 130)

    def test_sc_indicator_separates_mixed_reference_return_from_oil_guard(self):
        import numpy as np
        import pandas as pd
        import re

        dates = pd.bdate_range(end="2026-09-04", periods=80).strftime("%Y%m%d")
        px = np.linspace(500, 600, 80)
        data = pd.DataFrame(dict(trade_date=dates, px=px, settle=px, close=px,
                                 high=px + 5, low=px - 5, open=px - 1, vol=20000))
        data.loc[79, "settle"] = np.nan
        ns = isolated_functions({"_tr", "indicators"}, dict(
            np=np, pd=pd, re=re, AS_OF="20260904", daily=lambda sym: data,
            _volume20=lambda sym: 20000, _busdays=lambda start, end: 80,
            delist_date=lambda sym: "20270115", CAL_DEGRADED=[], SIGNAL_LEGS={"SC2610"},
            _T3_PRODS=set(), CONTRACT_SPEC={}, weekly_price_evidence=weekly_price_evidence))
        result = ns["indicators"]("SC2610")
        self.assertEqual(result["price_basis"], "close")
        self.assertIsNotNone(result["周涨%"])
        self.assertIsNone(result["SC护栏结算周涨%"])
        self.assertEqual(result["SC护栏数据状态"], "unknown")
        self.assertEqual(result["周涨起日"], "20260828")
        self.assertEqual(result["周涨止口径"], "close")

    def test_partial_historical_windows_warn_without_becoming_required_missing(self):
        import numpy as np
        import pandas as pd

        historical_basis = {"near": "settle"}

        def fake_pair(near, far):
            year = 2000 + int(near[2:4])
            dates = pd.bdate_range(f"{year}0807", periods=40).strftime("%Y%m%d")
            if year == 2026:
                dates = pd.bdate_range(end="20260904", periods=40).strftime("%Y%m%d")
            return pd.DataFrame(dict(trade_date=dates, px_n=3200, px_f=2900,
                                     spread=300, spread_pct=300 / 2900 * 100,
                                     near_contract=near, far_contract=far,
                                     price_basis_n=historical_basis["near"] if year < 2026 else "settle",
                                     price_basis_f="settle"))

        with tempfile.TemporaryDirectory() as temp, redirect_stdout(io.StringIO()):
            ns = isolated_functions({"spread_percentile", "window_around"}, dict(
                pd=pd, np=np, os=os, OUTDIR=temp, AS_OF="20260904", YEARS=3, WIN=20,
                pair_series=fake_pair,
                shift_year_sym=lambda sym, k: sym[:2] + f"{int(sym[2:4]) - k:02d}" + sym[4:],
                shift_year_date=lambda day, k: str(int(day[:4]) - k) + day[4:],
                validate_unique_trade_dates=validate_unique_trade_dates,
                sample_coverage=sample_coverage, spread_change_series=spread_change_series,
                calendar_window=calendar_window,
                _volume20=lambda sym: 20000, _busdays=lambda a, b: 50,
                delist_date=lambda sym: "20270115", CAL_DEGRADED=[],
                _trade_cal=lambda: pd.bdate_range("20220101", "20261231").strftime("%Y%m%d").tolist()))
            result = ns["spread_percentile"]("MA", "MA2610", "MA2701")
            ns["AS_OF"] = "20260907"
            monday_result = ns["spread_percentile"]("MA", "MA2610", "MA2701")
            historical_basis["near"] = "close"
            mixed_result = ns["spread_percentile"]("MA", "MA2610", "MA2701")
            historical_basis["near"] = "unknown"
            unknown_result = ns["spread_percentile"]("MA", "MA2610", "MA2701")
        self.assertEqual(result["sample_coverage"]["status"], "complete")
        self.assertEqual(result["data_status"], "complete")
        self.assertEqual(result["missing_fields"], [])
        self.assertTrue(result["quality_warnings"])
        self.assertEqual(result["plan_status"], "incomplete")
        self.assertEqual(result["market_trade_date"], "20260904")
        self.assertEqual(monday_result["historical_windows"], result["historical_windows"])
        self.assertEqual(monday_result["percentile"], result["percentile"])
        self.assertEqual(result["percentile_price_basis_quality"], "consistent")
        self.assertEqual(result["scope"], "research_inputs")
        for item, expected in ((mixed_result, "basis_mixed"), (unknown_result, "unknown")):
            self.assertEqual(item["sample_coverage"]["status"], "complete")
            self.assertEqual(item["data_status"], "incomplete")
            self.assertEqual(item["percentile_price_basis_quality"], expected)
            self.assertIsNotNone(item["percentile"])
            self.assertTrue(any("不能确认#13/D4已过" in missing for missing in item["missing_fields"]))


if __name__ == "__main__":
    unittest.main()
