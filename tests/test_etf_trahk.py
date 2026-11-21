"""02800.HK must match the traded HKD close to the manager's published HKD counter."""
import io
import json
import unittest
from datetime import datetime
from types import ModuleType
from unittest.mock import Mock, patch

from openpyxl import Workbook
import pandas as pd

with patch.dict("sys.modules", {"akshare": ModuleType("akshare")}):
    from scripts import etf_data as etf


def workbook(day="20261120", currency="HKD", nav=22.5375, premium=0.01):
    wb = Workbook()
    ws = wb.active
    # Deliberately place the RMB counter first. Its creation-unit NAV is also in HKD.
    for row in [
        ["Name of ETF Manager", "Hang Seng Investment Management Limited"],
        ["Stock Code", None, "82800", None, None, "2800"],
        ["Date (ddmmmyyyy)", None, datetime.strptime(day, "%Y%m%d"), None, None, datetime.strptime(day, "%Y%m%d")],
        ["N.A.V. per Creation Unit (Note 2)", "HKD", 22537500, None, "HKD", 22537500],
        ["N.A.V. per Unit in Trading Currency (Note 1)", "RMB", 19.1977, None, currency, nav],
        ["Premium / Discount (%) (Note 5)", None, -0.04, None, None, premium],
        ["Notes"],
        ["Stock Code", "Stock Name", None, None, "Quantity"],
    ]:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def listing(time="20/11/2026 21:59", suffix="123"):
    return dict(DATE_TIME=time, STOCK_CODE="02800<br/>82800",
                LONG_TEXT="Trading Information of Exchange Traded Funds", TITLE="Summary Information",
                FILE_LINK="/listedco/listconews/sehk/2026/1120/" + suffix + ".xlsx")


class TrackerFundTests(unittest.TestCase):
    def snapshot(self, *, ts_rows=(), sina_rows=(("2026-11-20", 22.54, 100),),
                 reports=None, cutoff="20261121"):
        if reports is None:
            reports = [(listing(), workbook())]
        by_url = {x["FILE_LINK"]: data for x, data in reports}

        def get(url, **kwargs):
            if url.endswith("titleSearchServlet.do"):
                self.assertEqual(kwargs["params"]["toDate"], cutoff)
                return Mock(json=lambda: {"result": json.dumps([x for x, _ in reports]),
                                          "recordCnt": len(reports), "hasNextRow": False})
            return Mock(content=by_url[url.removeprefix("https://www1.hkexnews.hk")])

        fields = ["ts_code", "trade_date", "close", "vol"]
        resp = Mock(status_code=200)
        resp.json.return_value = dict(code=0, data=dict(fields=fields, items=list(ts_rows)))
        with (patch.object(etf, "CUTOFF", cutoff), patch.object(etf, "GAPS", []) as gaps,
              patch.object(etf, "INTERFACES", {}), patch.object(etf, "TOKEN", "unit-test"),
              patch.object(etf.time, "sleep"), patch.object(etf.requests, "post", return_value=resp) as post,
              patch.object(etf.requests, "get", side_effect=get),
              patch.object(etf.ak, "stock_hk_daily", create=True) as sina):
            sina.return_value = pd.DataFrame(sina_rows, columns=["date", "close", "volume"])
            section = "\n".join(etf.section_tools(None, {}, None))
            self.assertEqual(post.call_args.args, ("https://api.tushare.pro",))
            self.assertEqual(post.call_args.kwargs["json"]["params"]["ts_code"], "02800.HK")
            self.assertFalse(post.call_args.kwargs["allow_redirects"])
            if sina.called:
                sina.assert_called_once_with(symbol="02800", adjust="")
            return section, gaps

    def test_weekend_fallback_and_disclosed_rounding(self):
        section, gaps = self.snapshot()
        for value in ("新浪", "22.54 HKD", "22.5375 HKD", "20261120", "+0.0111%", "+0.01%", "21:59"):
            self.assertIn(value, section)
        self.assertFalse(any("02800" in g for g in gaps))

    def test_tushare_priority_and_latest_traded_day(self):
        valid = ("02800.HK", "20261120", 22.54, 100)
        for rows, source in [([valid], "Tushare"), ([("02800.HK", "20261119", 22.94, 300)], "新浪"),
                             ([("82800.HK", "20261120", 19.19, 40)], "新浪"),
                             ([("02800.HK", "20261120", 23.00, 0)], "新浪")]:
            section, _ = self.snapshot(ts_rows=rows)
            self.assertIn(source, next(s for s in section.splitlines() if "收盘价" in s))
            self.assertIn("+0.0111%", section)

    def test_discount_and_latest_visible_revision(self):
        old = listing("20/11/2026 21:40", "122")
        for reports in ([(old, workbook(nav=22.55, premium=-0.04)), (listing(), workbook())],
                        [(listing(), workbook()), (old, workbook(nav=22.55, premium=-0.04))]):
            section, _ = self.snapshot(reports=reports)
            self.assertIn("+0.0111%", section)
        section, _ = self.snapshot(reports=[(old, workbook(nav=22.55, premium=-0.04))])
        self.assertIn("-0.0443%", section)

    def test_later_release_only_visible_from_its_hong_kong_date(self):
        reports = [(listing("21/11/2026 00:01"), workbook())]
        before, _ = self.snapshot(reports=reports, cutoff="20261120")
        after, _ = self.snapshot(reports=reports, cutoff="20261121")
        self.assertNotIn("+0.0111%", before)
        self.assertIn("+0.0111%", after)
        self.assertIn("2026-11-21 00:01", after)

    def test_missing_mismatched_or_unpublished_evidence_stays_a_gap(self):
        for reports in ([], [(listing(), workbook(day="20261119"))], [(listing(), workbook(currency="RMB"))],
                        [(listing(), workbook(nav=0))], [(listing(), workbook(premium=-0.04))],
                        [(listing("21/11/2026 00:01"), workbook())]):
            section, gaps = self.snapshot(reports=reports, cutoff="20261120")
            self.assertNotIn("+0.0111%", section)
            self.assertIn("22.54 HKD", section)
            self.assertTrue(any("02800" in g for g in gaps))
        section, _ = self.snapshot(sina_rows=[("2026-11-23", 22.54, 100)])
        self.assertNotIn("+0.0111%", section)


class TrackerFeeTests(unittest.TestCase):
    def fees(self, day):
        with (patch.object(etf, "CUTOFF", day), patch.object(etf, "GAPS", []) as gaps,
              patch.object(etf, "fetch", return_value=None)):
            section = etf.section_tools(None, {}, None)
        return {key: next(line for line in section if line.startswith("  " + key))
                for key in ("管理费", "受托人费", "持续收费比率")}, gaps

    def test_each_fee_has_its_own_terms_period_and_issuer_source_without_a_price(self):
        fees, _ = self.fees("20261120")
        for label in ("管理费", "受托人费"):
            for term in ("150亿", "300亿", "450亿", "0.045%", "0.030%", "0.020%", "0.015%",
                         "2022-09-19", "2025-09-19", "0.019%", "取低", "平均每日", "2022091900035.pdf", "2026041700316.pdf"):
                self.assertIn(term, fees[label])
        for term in ("0.060%", "2026-04-17", "2025-01-01", "2025-12-31", "平均净资产",
                     "估算", "已含管理费和受托人费", "2026041700316.pdf"):
            self.assertIn(term, fees["持续收费比率"])
        self.assertFalse(any("02800" in g for g in etf.STATIC_GAPS))

    def test_cap_and_daily_basis_only_appear_after_their_own_effective_dates(self):
        for day, capped, daily in (("20250918", False, False), ("20250919", True, False),
                                   ("20251007", True, False), ("20251008", True, True)):
            with self.subTest(day=day):
                fees, _ = self.fees(day)
                for label in ("管理费", "受托人费"):
                    self.assertEqual("0.019%" in fees[label], capped)
                    self.assertEqual("2025091500355.pdf" in fees[label], capped)
                    self.assertEqual("平均每日" in fees[label], daily)
                    self.assertNotIn("2026041700316.pdf", fees[label])

    def test_ongoing_ratio_switches_by_disclosure_not_by_financial_year(self):
        for day, rate, year, published in (
                ("20220919", "0.08%", 2021, "2022-09-19"),
                ("20230428", "0.08%", 2022, "2023-04-28"),
                ("20240430", "0.07%", 2023, "2024-04-30"),
                ("20250423", "0.066%", 2024, "2025-04-23"),
                ("20251231", "0.066%", 2024, "2025-04-23"),
                ("20260416", "0.066%", 2024, "2025-04-23"),
                ("20260417", "0.060%", 2025, "2026-04-17")):
            with self.subTest(day=day):
                line = self.fees(day)[0]["持续收费比率"]
                for term in (rate, published, f"{year}-12-31", "https://www1.hkexnews.hk/"):
                    self.assertIn(term, line)
                if day < "20260417":
                    self.assertNotIn("2026041700316.pdf", line)

    def test_before_first_disclosure_each_fee_is_missing(self):
        fees, gaps = self.fees("20220918")
        for label, line in fees.items():
            self.assertIn(etf.MARK, line)
            self.assertTrue(any(label in gap for gap in gaps))
            self.assertNotIn("%", line)


class TrackerFeeNoticeTests(unittest.TestCase):
    @staticmethod
    def filing(day, title, number, category="Announcements and Notices - [Matters relating to Collective Investment Schemes]"):
        result = listing(day + " 16:31", number)
        result.update(TITLE=title, LONG_TEXT=category, FILE_LINK=result["FILE_LINK"].replace(".xlsx", ".pdf"))
        return result

    def snapshot(self, cutoff, items, *, body="", count=None, more=False):
        if count is None:
            count = len(items)
        result = Mock()
        result.json.return_value = dict(result=json.dumps(items), recordCnt=count, hasNextRow=more)
        with (patch.object(etf, "CUTOFF", cutoff), patch.object(etf, "GAPS", []) as gaps,
              patch.object(etf, "INTERFACES", {}), patch.object(etf, "fetch", return_value=None),
              patch.object(etf, "TRAHK_FEE_REVIEW_DAYS", ("20261119",)),
              patch.object(etf.requests, "get", return_value=result) as get,
              patch.object(etf, "trahk_notice_text", side_effect=body if isinstance(body, Exception) else None,
                           return_value=body) as pdf):
            lines = etf.section_tools(None, {}, None)
            for call in get.call_args_list:
                self.assertLessEqual(call.kwargs["params"]["toDate"], cutoff)
            return "\n".join(lines), gaps, pdf.call_count

    def test_same_day_new_versions_filtered_by_issuer_and_repeated_until_review(self):
        kfs = self.filing("20/11/2026", "Revised Product Key Facts Statement", "123")
        change = self.filing("20/11/2026", "Reduction of Management Fee", "124")
        later = self.filing("23/11/2026", "New Product Key Facts Statement", "125")
        foreign = dict(change, STOCK_CODE="82800", FILE_LINK=change["FILE_LINK"].replace("124", "126"))
        rows = [later, kfs, change, kfs, foreign]
        before, _, _ = self.snapshot("20261119", rows)
        self.assertNotIn("待复核", before)
        for cutoff in ("20261120", "20261121"):
            report, gaps, pdfs = self.snapshot(cutoff, rows)
            self.assertIn("0.060%", report)
            self.assertIn("待复核", report)
            self.assertIn("2026-11-20 16:31", report)
            for doc in ("123", "124"):
                self.assertEqual(report.count("/" + doc + ".pdf"), 1)
            for doc in ("125", "126"):
                self.assertNotIn("/" + doc + ".pdf", report)
            self.assertEqual(pdfs, 0)

    def test_generic_notice_body_and_unrelated_disclosures(self):
        notice = self.filing("20/11/2026", "Notice to Unitholders", "100")
        dividend = self.filing("20/11/2026", "Announcement", "101", "Announcements and Notices - [Dividend or Distribution]")
        report, _, pdfs = self.snapshot("20261120", [notice, dividend], body="Each management fee will be subject to a cap.")
        self.assertIn("/100.pdf", report)
        self.assertNotIn("/101.pdf", report)
        self.assertEqual(pdfs, 1)
        report, _, _ = self.snapshot("20261120", [notice], body="A new director has been appointed. The change has no impact on management fees.")
        self.assertIn("未发现", report)
        self.assertNotIn("待复核", report)

    def test_partial_or_unreadable_results_do_not_hide_alerts_or_change_fees(self):
        kfs = self.filing("20/11/2026", "Product Key Facts Statement", "950")
        generic = self.filing("20/11/2026", "Notice to Unitholders", "951")
        for count, more, body in ((3, True, ""), (2, False, ValueError("unreadable"))):
            report, gaps, _ = self.snapshot("20261120", [kfs, generic], body=body, count=count, more=more)
            self.assertIn("检查不完整", report)
            self.assertNotIn("未发现", report)
            self.assertTrue(any("检查不完整" in g for g in gaps))
            self.assertIn("/950.pdf", report)
            self.assertIn("0.060%", report)

    def test_complete_empty_is_different_from_failed_index(self):
        report, _, _ = self.snapshot("20261120", [])
        self.assertIn("未发现", report)
        report, _, _ = self.snapshot("20261120", [], count=1)
        self.assertIn("检查不完整", report)
        self.assertNotIn("未发现", report)

    def test_malformed_page_or_lost_second_page_keeps_confirmed_hits(self):
        kfs = self.filing("20/11/2026", "Product Key Facts Statement", "777")
        first = dict(result=json.dumps([kfs]), recordCnt=2, hasNextRow=True)
        for payloads, expected in (([dict(result="null", recordCnt=0, hasNextRow=False)], False),
                                   ([first, etf.requests.Timeout()], True)):
            with (patch.object(etf, "CUTOFF", "20261120"), patch.object(etf, "GAPS", []),
                  patch.object(etf, "INTERFACES", {}), patch.object(etf, "TRAHK_FEE_REVIEW_DAYS", ("20261119",)),
                  patch.object(etf, "trahk_filing_index", side_effect=payloads)):
                lines = "\n".join(etf.trahk_fee_notice_lines())
                self.assertIn("检查不完整", lines)
                self.assertEqual("/777.pdf" in lines, expected)
                self.assertNotIn("未发现", lines)
