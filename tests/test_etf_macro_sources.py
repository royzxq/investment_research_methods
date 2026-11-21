"""Exercise the same series and rendered lines used by ETF snapshots."""
import unittest
from contextlib import ExitStack
from types import ModuleType
from unittest.mock import patch

import pandas as pd

with patch.dict("sys.modules", {"akshare": ModuleType("akshare")}):
    from scripts import etf_data as data


def primary(endpoint, fields, **params):
    if endpoint == "us_tycr":
        return pd.DataFrame({"date": ["20261119", "20261120"], "y10": [5.04, 4.92]})
    code = params["ts_code"]
    return pd.DataFrame({"ts_code": [code], "trade_date": ["20261120"],
                         "mid_rate": [85.618 if code == "CNYHKD" else 671.31]})


class MacroSourceTests(unittest.TestCase):
    def setUp(self):
        patches = ExitStack()
        self.addCleanup(patches.close)
        for name, value in (("CUTOFF", "20261120"), ("INTERFACES", {}), ("GAPS", [])):
            patches.enter_context(patch.object(data, name, value))
        patches.enter_context(patch.object(data.time, "sleep"))
        patches.enter_context(patch.object(data, "_china_yields", return_value=None))
        self.query = patches.enter_context(patch.object(data, "_pro_rows", side_effect=primary))
        self.fx_backup = patches.enter_context(patch.object(data.ak, "currency_boc_safe", create=True,
            return_value=pd.DataFrame({"日期": ["2026-11-20", "2026-11-23"], "美元": [671.31, 900], "港元": [85.618, 100]})))
        self.us_backup = patches.enter_context(patch.object(data.ak, "bond_zh_us_rate", create=True,
            return_value=pd.DataFrame({"日期": ["2026-11-20", "2026-11-23"], "美国国债收益率10年": [4.92, 9.0]})))

    def snapshot(self):
        return "\n".join(data.section_macro(data.bond_yields(), data.fx_rates(), {}))

    def test_primary_values_units_dates_and_sources(self):
        text = self.snapshot()
        for s in ("6.7131", "0.85618", "人民币元", "4.9200%", "20261120", "Tushare.fx_midrate", "Tushare.us_tycr"):
            self.assertIn(s, text)
        self.fx_backup.assert_not_called()
        self.us_backup.assert_not_called()

    def test_empty_primary_uses_real_backup_schema_without_future_rows(self):
        self.query.side_effect = lambda *a, **kw: pd.DataFrame()
        text = self.snapshot()
        for s in ("6.7131", "0.85618", "4.9200%", "AKShare.currency_boc_safe", "AKShare.bond_zh_us_rate", "备用", "空表"):
            self.assertIn(s, text)
        self.assertNotIn("20261123", text)

    def test_one_currency_missing_falls_back_only_for_fx(self):
        self.query.side_effect = lambda ep, f, **p: (pd.DataFrame() if p.get("ts_code") == "CNYUSD"
                                                     else primary(ep, f, **p))
        text = self.snapshot()
        self.assertIn("AKShare.currency_boc_safe", text)
        self.assertIn("Tushare.us_tycr", text)
        self.us_backup.assert_not_called()

    def test_stale_primary_checks_for_a_newer_visible_observation(self):
        def stale(*args, **params):
            return primary(*args, **params).replace("20261120", "20261118")
        self.query.side_effect = stale
        text = self.snapshot()
        self.assertIn("AKShare.currency_boc_safe", text)
        self.assertIn("AKShare.bond_zh_us_rate", text)
        self.assertIn("20261120", text)

    def test_no_valid_source_exposes_missing_data(self):
        self.query.side_effect = ConnectionError("offline")
        self.fx_backup.return_value = self.us_backup.return_value = pd.DataFrame()
        text = self.snapshot()
        self.assertIn(data.MARK, text)
        self.assertNotIn("4.9200%", text)
        self.assertNotIn("6.7131", text)

    def test_cutoff_with_no_new_fixing_keeps_primary_actual_date(self):
        self.query.side_effect = lambda *a, **kw: primary(*a, **kw).iloc[[-1]].replace("20261120", "20261119")
        self.fx_backup.return_value = self.fx_backup.return_value.iloc[[0]].replace("2026-11-20", "2026-11-19")
        self.us_backup.return_value = self.us_backup.return_value.iloc[[0]].replace("2026-11-20", "2026-11-19")
        text = self.snapshot()
        self.assertIn("Tushare.fx_midrate", text)
        self.assertIn("Tushare.us_tycr", text)
        self.assertIn("@20261119", text)
        self.assertNotIn("@20261120", text)

    def test_fx_history_reads_past_full_first_page(self):
        dates = pd.bdate_range(end="2026-11-20", periods=1001).strftime("%Y%m%d")[::-1]
        def pages(ep, fields, **params):
            code = params["ts_code"]
            selected = dates[dates <= params["end_date"]][:params["limit"]]
            return pd.DataFrame({"ts_code": code, "trade_date": selected, "mid_rate": 85 if code == "CNYHKD" else 670})
        self.query.side_effect = pages
        frame = data.fx_rates()
        self.assertEqual((len(frame), frame.trade_date.iloc[0], frame.trade_date.iloc[-1]), (1001, dates[-1], dates[0]))
        self.assertEqual(self.query.call_count, 4)
        self.fx_backup.assert_not_called()
