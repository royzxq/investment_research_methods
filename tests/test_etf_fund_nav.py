"""ETF §5 must use the NAV versions published by the snapshot cutoff."""
import unittest
from types import ModuleType
from unittest.mock import patch

import pandas as pd

# NAV tests only need Tushare; the offline CI environment omits AKShare.
with patch.dict("sys.modules", {"akshare": ModuleType("akshare")}):
    from scripts import etf_data


CODE = "022448.OF"


def nav(nav_date, ann_date, value, assets=None):
    return dict(ts_code=CODE, nav_date=nav_date, ann_date=ann_date, unit_nav=value,
                adj_nav=value, net_asset=assets, total_netasset=assets)


class FundNavTests(unittest.TestCase):
    def snapshot(self, cutoff, rows):
        with (patch.object(etf_data, "CUTOFF", cutoff), patch.object(etf_data, "GAPS", []) as gaps,
              patch.object(etf_data, "_pro_rows", return_value=pd.DataFrame(rows)),
              patch.object(etf_data, "fetch", side_effect=lambda label, call: call())):
            result = etf_data.fund_nav(CODE)
            return result, gaps

    def test_nav_and_index_use_official_https_with_and_without_fields(self):
        from unittest.mock import Mock

        row = nav("20261119", "20261120", 1.2)
        def pro_response(url, *, json, **options):
            self.assertEqual(url, "https://api.tushare.pro")
            self.assertIs(options["allow_redirects"], False)
            self.assertEqual(json["token"], "offline-test")
            if json["api_name"] == "fund_nav":
                self.assertEqual(json["params"], {"ts_code": CODE, "end_date": "20261120"})
                columns = json["fields"].split(",")
                self.assertEqual(set(columns), set(row))
                items = [[row[k] for k in columns]]
            else:
                self.assertEqual(json["api_name"], "index_daily")
                self.assertEqual(json["params"], {"ts_code": "000300.SH", "start_date": "20261119", "end_date": "20261120"})
                self.assertEqual(json["fields"], "")
                columns, items = ["trade_date", "close"], [["20261120", 3954.57]]
            response = Mock()
            response.json.return_value = {"code": 0, "data": {"fields": columns, "items": items}}
            return response

        with (patch.object(etf_data, "CUTOFF", "20261120"), patch.object(etf_data, "TOKEN", "offline-test"),
              patch.object(etf_data, "fetch", side_effect=lambda label, call: call()),
              patch.object(etf_data.requests, "post", side_effect=pro_response) as post):
            self.assertEqual(etf_data.fund_nav(CODE).iloc[-1].unit_nav, 1.2)
            self.assertEqual(etf_data.daily_levels("000300.SH", "index_daily", "20261119").iloc[-1].close, 3954.57)
            self.assertEqual(post.call_count, 2)

    def test_publication_on_nontrading_day_becomes_visible_on_that_date(self):
        rows = [nav("20260529", "20260530", 1.2752), nav("20260528", "20260529", 1.2886)]
        before, _ = self.snapshot("20260529", rows)
        after, _ = self.snapshot("20260530", rows)
        self.assertEqual(before["trade_date"].tolist(), ["20260528"])
        self.assertEqual(after["trade_date"].tolist(), ["20260528", "20260529"])
        self.assertEqual(after.iloc[-1]["ann_date"], "20260530")

    def test_revision_selected_after_cutoff_filter_for_all_fields(self):
        original = nav("20260528", "20260529", 1.20, 100)
        correction = nav("20260528", "20260601", 1.25, 105)
        for rows in ([original, correction], [correction, original]):
            for cutoff, expected in [("20260531", original), ("20260601", correction)]:
                frame, _ = self.snapshot(cutoff, rows)
                for key in ("ann_date", "unit_nav", "adj_nav", "net_asset", "total_netasset"):
                    self.assertEqual(frame.iloc[0][key], expected[key])

    def test_bad_dates_and_foreign_code_are_not_observations(self):
        rows = [nav("20260528", date, 9) for date in (None, "", "20260230", "2026052", "20260527")]
        rows += [nav(None, "20260528", 9), nav("20260230", "20260528", 9),
                 {**nav("20260528", "20260528", 9), "ts_code": "123456.OF"},
                 nav("20260601", "20260601", 9), nav("20260527", "20260527", 1.2)]
        frame, _ = self.snapshot("20260529", rows)
        self.assertEqual(frame["unit_nav"].tolist(), [1.2])

    def test_conflicting_latest_versions_cannot_revert_to_an_older_value(self):
        r = nav("20260527", "20260527", 1.3)
        rows = [r, dict(r), nav("20260528", "20260528", 1.1),
                nav("20260528", "20260529", 1.2), nav("20260528", "20260529", 1.25)]
        frame, gaps = self.snapshot("20260529", rows)
        self.assertEqual(frame["trade_date"].tolist(), ["20260527"])
        self.assertTrue(any("20260528" in gap for gap in gaps))

    def test_only_future_announcement_yields_empty_series(self):
        frame, _ = self.snapshot("20260529", [nav("20260529", "20260530", 1.2752)])
        self.assertTrue(frame.empty)
        self.assertIn("trade_date", frame.columns)
