"""Response-derived futures identity, cache corruption and export regressions."""
from contextlib import ExitStack, redirect_stdout
from copy import deepcopy
from datetime import datetime
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pandas as pd

from scripts import future_data as data


class DailyResponseIdentityTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(data, "_daily_cache", {}))
        self.stack.enter_context(patch.object(data, "AS_OF", "20261009"))
        self.stack.enter_context(patch.object(data, "completed_day_cutoff", return_value="20261009"))
        self.stack.enter_context(patch.object(data.time, "sleep"))

    def response(self, codes=("M2701.DCE", "M2701.DCE")):
        return pd.DataFrame([dict(ts_code=code, trade_date=day, open=2990, close=3000,
                                  settle=3001, high=3010, low=2980, pre_settle=2990, vol=20000, oi=10000)
                             for code, day in zip(codes, ("20261008", "20261009"))])

    def run_daily(self, response, *, sym="M2701", resolved="M2701.DCE"):
        called = {}

        def endpoint(**kwargs):
            called.update(kwargs)
            return response.copy(deep=True)

        with patch.object(data, "resolve", return_value=resolved), \
                patch.object(data, "api", return_value=SimpleNamespace(fut_daily=endpoint)):
            result = data.daily(sym)
        return result, called

    def test_response_identity_is_requested_preserved_and_exportable(self):
        frame, request = self.run_daily(self.response())
        self.assertIn("ts_code", request["fields"].split(","))
        self.assertEqual(frame["ts_code"].tolist(), ["M2701.DCE", "M2701.DCE"])
        self.assertEqual(frame.attrs["provenance"]["ts_code"], "M2701.DCE")
        self.assertEqual(frame.attrs["provenance"]["contract"], "M2701")
        self.assertEqual(frame.attrs["provenance"]["exchange"], "DCE")
        self.assertEqual(frame.attrs["provenance"]["requested_ts_code"], request["ts_code"])
        self.assertEqual(frame.attrs["provenance"]["identity_basis"], "fut_daily_response_ts_code")

    def test_missing_response_column_never_becomes_requested_identity(self):
        with self.assertRaisesRegex(ValueError, "response_ts_code_missing"):
            self.run_daily(self.response().drop(columns="ts_code"))
        self.assertNotIn("M2701", data._daily_cache)

    def test_blank_null_numeric_or_nan_response_identity_fails(self):
        for bad in (None, "", " ", 2701, float("nan")):
            with self.subTest(value=bad), self.assertRaisesRegex(ValueError, "response_ts_code_missing"):
                self.run_daily(self.response(("M2701.DCE", bad)))
            self.assertNotIn("M2701", data._daily_cache)

    def test_wrong_month_product_exchange_and_malformed_response_fail(self):
        for wrong in ("M2705.DCE", "RB2701.SHF", "M2701.ZCE", "M2713.DCE", "M2701", "M701.DCE"):
            with self.subTest(code=wrong), self.assertRaisesRegex(ValueError, "response_ts_code_(mismatch|invalid)"):
                self.run_daily(self.response((wrong, wrong)))
            self.assertNotIn("M2701", data._daily_cache)

    def test_mixed_rows_fail_including_one_correct_latest_row(self):
        for wrong in ("M2705.DCE", "M2701.ZCE", "RB2701.SHF"):
            with self.subTest(code=wrong), self.assertRaisesRegex(ValueError, "response_ts_code_mixed"):
                self.run_daily(self.response((wrong, "M2701.DCE")))
            self.assertNotIn("M2701", data._daily_cache)

    def test_bad_resolve_and_matching_bad_api_response_cannot_masquerade_as_requested_symbol(self):
        for wrong in ("M2705.DCE", "M2701.ZCE"):
            with self.subTest(code=wrong), self.assertRaisesRegex(ValueError, "response_ts_code_mismatch"):
                self.run_daily(self.response((wrong, wrong)), resolved=wrong)
            self.assertNotIn("M2701", data._daily_cache)

    def test_bad_resolve_and_correct_response_still_reports_request_conflict(self):
        with self.assertRaisesRegex(ValueError, "requested_response_ts_code_mismatch"):
            self.run_daily(self.response(), resolved="M2705.DCE")
        self.assertNotIn("M2701", data._daily_cache)

    def test_cached_frame_keeps_real_fetch_time_without_api_or_resolve(self):
        frame, _ = self.run_daily(self.response())
        before = deepcopy(frame.attrs["provenance"])
        with patch.object(data, "api", side_effect=AssertionError("cache must not refetch")), \
                patch.object(data, "resolve", side_effect=AssertionError("cache key cannot prove response")):
            again = data.daily("M2701")
        self.assertIs(frame, again)
        self.assertEqual(again.attrs["provenance"], before)

    def test_cache_wrong_response_cannot_be_repaired_by_expected_key_or_attrs(self):
        frame, _ = self.run_daily(self.response())
        for mutate in (lambda f: f.drop(columns="ts_code", inplace=True),
                       lambda f: f.__setitem__("ts_code", ["M2705.DCE", "M2705.DCE"]),
                       lambda f: f.__setitem__("ts_code", ["M2701.DCE", "M2701.ZCE"]),
                       lambda f: f.__setitem__("ts_code", [None, "M2701.DCE"])):
            cached = frame.copy(deep=True)
            cached.attrs = deepcopy(frame.attrs)
            mutate(cached)
            data._daily_cache["M2701"] = cached
            with self.subTest(mutate=mutate), patch.object(data, "api", side_effect=AssertionError("must expose gap")), \
                    self.assertRaisesRegex(ValueError, "response_ts_code"):
                data.daily("M2701")

    def test_cache_provenance_conflict_or_unproven_old_attrs_are_rejected(self):
        frame, _ = self.run_daily(self.response())
        mutations = [{"ts_code": "M2705.DCE"}, {"contract": "M2705"}, {"exchange": "CZCE"},
                     {"requested_ts_code": "M2705.DCE"}, {"identity_basis": None}, {"fetched_at": None}]
        for mutation in mutations:
            cached = frame.copy(deep=True)
            cached.attrs = deepcopy(frame.attrs)
            cached.attrs["provenance"].update(mutation)
            data._daily_cache["M2701"] = cached
            with self.subTest(change=mutation), self.assertRaises(ValueError):
                data.daily("M2701")


class V3IdentityExportTests(unittest.TestCase):
    def frame(self, contract="M2701", suffix="DCE"):
        days = pd.bdate_range(end="2026-10-09", periods=65).strftime("%Y%m%d").tolist()
        frame = pd.DataFrame([dict(ts_code=f"{contract}.{suffix}", trade_date=day,
                                  close=3000 + i, settle=3001 + i, high=3002 + i, low=2998 + i)
                              for i, day in enumerate(days)])
        exchange = {"DCE": "DCE", "ZCE": "CZCE", "SHF": "SHFE"}[suffix]
        frame.attrs["provenance"] = dict(source="synthetic fut_daily response", contract=contract,
            ts_code=f"{contract}.{suffix}", exchange=exchange, requested_ts_code=f"{contract}.{suffix}",
            identity_basis="fut_daily_response_ts_code", fetched_at="2026-10-11T19:00:00+08:00")
        return frame, days

    def collect(self, frames, *, contracts=("M2701",), pairs=()):
        _, days = self.frame()
        with tempfile.TemporaryDirectory() as directory, patch.object(data, "OUTDIR", directory), \
                patch.object(data, "AS_OF", "20261011"), patch.object(data, "completed_day_cutoff", return_value="20261009"), \
                patch.object(data, "_trade_cal", return_value=days), patch.object(data, "CAL_DEGRADED", []), \
                patch.object(data, "INDICATOR_CONTRACTS", list(contracts)), \
                patch.object(data, "research_pairs", return_value=list(pairs)), \
                patch.object(data, "daily", side_effect=lambda sym: frames[sym]), \
                patch.object(data, "api", side_effect=AssertionError("offline fixture only")), redirect_stdout(io.StringIO()):
            result = data.collect_v3_research()
            saved = json.loads((Path(directory) / "v3_research_inputs_20261011.json").read_text())
        self.assertEqual(result, saved)
        return saved

    def test_trend_exports_actual_response_provenance_and_raw_row_identity(self):
        frame, _ = self.frame()
        result = self.collect({"M2701": frame})
        row = result["trend"][0]
        self.assertEqual(result["script_version"], "v1.18.1")
        self.assertEqual(row["status"], "valid")
        market = row["market_inputs"]
        for key, value in frame.attrs["provenance"].items():
            self.assertEqual(market[key], value)
        self.assertTrue(all(record["ts_code"] == "M2701.DCE" for record in market["records"]))

    def test_noncanonical_provider_spelling_normalizes_from_response_through_refresh(self):
        from scripts import futures_refresh as refresh
        frame, days = self.frame()
        frame["ts_code"] = " m2701.dce "
        # Exercise the actual API/caching path before export, not just the label
        # serializer: both request and provider strings carry noncanonical case.
        with patch.object(data, "_daily_cache", {}), patch.object(data, "AS_OF", "20261011"), \
                patch.object(data, "completed_day_cutoff", return_value="20261009"), \
                patch.object(data, "resolve", return_value=" m2701.dce "), \
                patch.object(data, "api", return_value=SimpleNamespace(fut_daily=lambda **kwargs: frame)), \
                patch.object(data.time, "sleep"):
            verified = data.daily("M2701")
        payload = self.collect({"M2701": verified})
        market = payload["trend"][0]["market_inputs"]
        market["trading_dates"] = days + ["20261012", "20261013"]
        self.assertEqual(market["ts_code"], "M2701.DCE")
        self.assertEqual(market["requested_ts_code"], "M2701.DCE")
        self.assertEqual(market["requested_ts_code_raw"], " m2701.dce ")
        self.assertEqual(market["response_ts_code_values"], [" m2701.dce "])
        self.assertTrue(all(x["ts_code"] == "M2701.DCE" and x["response_ts_code"] == " m2701.dce " for x in market["records"]))
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / "snapshot.txt"
            original = payload["trend"][0]
            snapshot.write_text("== v3.0 框架数据脚本 v1.18.1 | AS_OF=20261011 |\n"
                                f"T M2701: {original['status']} / {original['signal']} / {original['side']}\n"
                                "== 快照完成 | AS_OF=20261011 | 脚本 v1.18.1 | 本行存在即输出完整 ==\n")
            now = max(datetime.fromisoformat(market["fetched_at"]), datetime.fromisoformat("2026-10-11T23:00:00+08:00"))
            result = refresh.evaluate(payload, snapshot, "20261011", now)
        row = next(x for x in result["trend"] if x["contract"] == "M2701")
        self.assertEqual(row["status"], "valid", row)
        self.assertEqual(row["execution_permission"], "not_evaluated")

    def test_trend_missing_or_wrong_frame_identity_stays_incomplete(self):
        valid, _ = self.frame()
        absent = valid.drop(columns="ts_code")
        wrong, _ = self.frame("RB2701", "SHF")
        for frame in (absent, wrong):
            with self.subTest(columns=frame.columns.tolist()):
                result = self.collect({"M2701": frame})["trend"][0]
                self.assertEqual(result["status"], "incomplete")
                self.assertEqual(result["signal"], "unknown")
                self.assertNotIn("market_inputs", result)
                self.assertIn("response_ts_code", result["missing_fields"][0])

    def test_v_two_sources_are_response_derived(self):
        near, _ = self.frame("MA2701", "ZCE")
        far, _ = self.frame("MA2705", "ZCE")
        result = self.collect({"MA2701": near, "MA2705": far}, contracts=(),
                              pairs=[("current", "MA", "MA2701", "MA2705", "结构")])
        market = result["economic_reversion"][0]["market_inputs"]
        self.assertEqual(market["sources"]["MA2701"]["ts_code"], "MA2701.ZCE")
        self.assertEqual(market["sources"]["MA2705"]["ts_code"], "MA2705.ZCE")
        self.assertEqual(market["sources"]["MA2701"]["identity_basis"], "fut_daily_response_ts_code")

    def test_v_wrong_far_cache_never_gets_expected_far_source_label(self):
        near, _ = self.frame("MA2701", "ZCE")
        wrong, _ = self.frame("MA2709", "ZCE")
        result = self.collect({"MA2701": near, "MA2705": wrong}, contracts=(),
                              pairs=[("current", "MA", "MA2701", "MA2705", "结构")])["economic_reversion"][0]
        self.assertNotIn("market_inputs", result)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("response_ts_code_mismatch", result["missing_fields"][0])


if __name__ == "__main__":
    unittest.main()
