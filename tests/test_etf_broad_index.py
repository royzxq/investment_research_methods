"""Monthly valuations of the two domestic benchmark indexes."""
import unittest
from types import ModuleType
from unittest.mock import patch

import pandas as pd

with patch.dict("sys.modules", {"akshare": ModuleType("akshare")}):
    from scripts import etf_data as etf


class BroadIndexTests(unittest.TestCase):
    def setUp(self):
        self.entry = next(e for e in etf.INDEX_POOL if e.get("key") == "000300.SH")
        dates = pd.bdate_range("2005-04-08", "2026-11-23").strftime("%Y%m%d")
        self.calendar = pd.bdate_range("2005-04-01", "2026-11-30").strftime("%Y%m%d").tolist()
        self.level = pd.DataFrame(dict(trade_date=dates, close=100.0))
        self.daily = self.level.drop(columns="close").assign(pe_ttm=20., pb=2.)
        self.backup = self.level.assign(pe_ttm=10., pb=1.).groupby(dates.str[:6]).tail(1)
        self.backup.loc[self.backup.index[-1], "trade_date"] = "20261120"
        cutoff = patch.object(etf, "CUTOFF", "20261120")
        cutoff.start()
        self.addCleanup(cutoff.stop)

    def test_primary_month_ends_and_current(self):
        frame = etf.broad_valuation(self.entry, self.daily, self.level, lambda _: self.fail("主源完整时不应取备用"), open_days=self.calendar)
        self.assertEqual(frame.iloc[-2:].trade_date.tolist(), ["20261030", "20261120"])
        self.assertEqual(frame.pe_ttm.unique().tolist(), [20.])
        rendered = "\n".join(etf.valuation_block("指数", frame, None))
        self.assertIn(f"n={len(frame)-1},", rendered)
        self.assertIn("20261120", rendered)

    def test_missing_month_end_switches_entire_series(self):
        partial = self.daily[self.daily.trade_date != "20181031"]
        out = etf.broad_valuation(self.entry, partial, self.level, lambda _: self.backup, open_days=self.calendar)
        self.assertEqual(out.pe_ttm.unique().tolist(), [10.])
        self.assertIn("20181031", out.attrs["source"])
        self.assertIsNone(etf.broad_valuation(self.entry, partial, self.level, lambda _: None, open_days=self.calendar))

    def test_outage_uses_backup_even_without_tushare_levels(self):
        out = etf.broad_valuation(self.entry, None, None, lambda _: self.backup)
        with patch.object(etf, "INDEX_POOL", [self.entry]):
            text = "\n".join(etf.section_decomposition({"000300.SH": out}, {}, {}))
            self.assertIn("乐咕", text)
            self.assertIn("20261120", text)
            table = "\n".join(etf.level_table({}, {"000300.SH": out}, {}, {}))
            self.assertIn("20261120", table)

    def test_price_history_can_predate_first_valuation_month(self):
        older = pd.DataFrame({"trade_date": ["20050131"], "close": [90.]})
        frame = etf.broad_valuation(self.entry, self.daily, pd.concat([older, self.level]), lambda _: None,
                                    open_days=self.calendar)
        self.assertIsNotNone(frame)
        self.assertEqual(frame.iloc[0].trade_date, "20050429")

    def test_both_daily_series_missing_last_session(self):
        bad_day = "20181031"
        out = etf.broad_valuation(self.entry, self.daily[self.daily.trade_date != bad_day],
                                  self.level[self.level.trade_date != bad_day], lambda _: self.backup, open_days=self.calendar)
        self.assertIn(bad_day, out.attrs["source"])
        self.assertEqual(out.pe_ttm.unique().tolist(), [10.])

    def test_final_trading_day_of_month_counts_even_before_weekend(self):
        with patch.object(etf, "CUTOFF", "20261030"):
            frame = etf.broad_valuation(self.entry, self.daily, self.level, None,
                                        open_days=[s for s in self.calendar if s <= "20261031"])
        self.assertFalse(frame.attrs["provisional"])

    def test_incomplete_or_invalid_primary_without_backup_is_a_gap(self):
        self.daily.attrs["complete"] = False
        self.assertIsNone(etf.broad_valuation(self.entry, self.daily, self.level, lambda _: None, open_days=self.calendar))
        self.daily.attrs.clear()
        self.daily.loc[self.daily.trade_date == "20261120", "pb"] = None
        self.assertIsNone(etf.broad_valuation(self.entry, self.daily, self.level, lambda _: None, open_days=self.calendar))

    def test_point_table_falls_back_when_aggregation_has_no_same_day_price(self):
        key = self.entry["key"]
        selected = etf.broad_valuation(self.entry, None, None, lambda _: self.backup)
        aggregate = selected.copy()
        with patch.object(etf, "INDEX_POOL", [self.entry]):
            lines = etf.level_table({key: aggregate}, {key: selected}, {}, {})
        self.assertIn("乐咕", lines[-1])

    def test_backup_drops_stale_current_value_without_exchange_calendar(self):
        self.assertIsNone(etf.broad_valuation(self.entry, None, None, lambda _: self.backup.iloc[:-1]))

    def test_calendar_schema_failure_allows_backup(self):
        with patch.object(etf, "fetch", return_value=pd.DataFrame({"cal_date": ["20261120"]})):
            days = etf.valuation_calendar("2026-11", "20261120")
        self.assertIsNone(days)
        out = etf.broad_valuation(self.entry, self.daily, self.level, lambda _: self.backup, open_days=days)
        self.assertIn("交易日历不可用", out.attrs["source"])
