"""Synthetic card and ladder; the numbers are not market data."""
import json
from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etf_refresh_cards import end_of_next_month, refresh_card
from scripts.validate_etf_card import load_card, validate_card
from tests.test_validate_etf_card import SNAPSHOT, card, number

NEW_SNAPSHOT = """== ETF 框架 v0.1 数据快照 | AS_OF=20261016 ==
---- §0 自检 ----
---- §6 趋势 ----
  -- 6b 回撤分位阶梯 --
 某指数 931152.CSI 20261016 2,100.00 2,400.00 0.8750 60.0 143 20141231 0.5000 0.6000 0.9000
== 快照完成 ==
"""


def levels_of(document):
    return {k: document["decision"]["anchors"][k]["level"]["value"] for k in ("add_below", "buy_below", "reduce_above")}


def card_text(document):
    old = levels_of(document)
    mention = (f"buy_below {old['buy_below']:,.2f} 与 reduce_above {old['reduce_above']:.2f}" if old["buy_below"] is not None
               else "无锚点")
    return (f"# 决策卡：测试\n\n正文提到 {mention}，以及无关的 1,880.55。\n\n"
            "```json\n" + json.dumps(document, ensure_ascii=False, indent=2) + "\n```\n")


def ladder(high=2400.0, states=(0.5, 0.6, 0.9)):
    return {"931152.CSI": {"rolling_high": high, "states": dict(zip(("P10", "P25", "P75"), states)),
                           "snapshot_ref": "research/etf-2026-10-16-data-snapshot.txt"}}


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.document = card()
        self.document["monitor_variables"][0].update(
            metric="index_level", operator="<", threshold=number(levels_of(self.document)["buy_below"], "calc:level_at_drawdown_state"),
            action="review")

    def test_anchors_monitor_prose_and_lineage_move_together(self):
        text, changes = refresh_card(card_text(self.document), ladder(), "2026-09-24")
        new = load_card(text)
        anchors = new["decision"]["anchors"]
        self.assertEqual(levels_of(new), {"add_below": 1200.0, "buy_below": 1440.0, "reduce_above": 2160.0})
        self.assertEqual(anchors["buy_below"]["inputs"]["rolling_high"]["value"], 2400.0)
        self.assertEqual(anchors["buy_below"]["inputs"]["state"]["value"], 0.6)
        self.assertEqual(anchors["valid_until"], "2026-10-31")
        self.assertEqual(new["monitor_variables"][0]["threshold"]["value"], 1440.0)     # pinned to buy_below, moved with it
        self.assertIsNone(new["monitor_variables"][0]["current_text"])                  # last month's reading cleared
        self.assertEqual((new["as_of_date"], new["supersedes"]), ("2026-09-24", "research/etf-cards/cn-pharma-tactical-2026-09-19.md"))
        self.assertEqual(new["snapshot_ref"], "research/etf-2026-09-18-data-snapshot.txt")   # thesis data stays on its snapshot
        self.assertEqual(anchors["snapshot_ref"], "research/etf-2026-10-16-data-snapshot.txt")
        self.assertIn("机械刷新 @2026-09-24", anchors["buy_below"]["rationale"])           # no stale "current level" claim survives
        self.assertEqual(new["thesis"], self.document["thesis"])                        # thesis untouched
        self.assertEqual(new["monitor_variables"][1], self.document["monitor_variables"][1])   # manual monitors untouched
        # the refreshed card validates with its thesis numbers against the old snapshot and its anchors against the new one
        self.assertEqual(validate_card(new, snapshot_text=SNAPSHOT, anchor_snapshot_text=NEW_SNAPSHOT,
                                       filename="cn-pharma-tactical-2026-09-24.md"), [])
        self.assertTrue(validate_card(new, snapshot_text=SNAPSHOT, filename="cn-pharma-tactical-2026-09-24.md"))   # without it, the anchors fail
        self.assertIn("buy_below 1,440.00 与 reduce_above 2,160.00，以及无关的 1,880.55", text)
        self.assertIn("> **点位机械刷新 @2026-09-24**", text.split("\n")[2])
        self.assertEqual(changes["file"], "research/etf-cards/cn-pharma-tactical-2026-09-24.md")

    def test_monitor_pinning_does_not_chain_and_reports_unpinned_thresholds(self):
        old = levels_of(self.document)
        chain = ladder(2829.12, (0.5, 0.6, 0.9))                 # new add_below == old buy_below exactly
        text, changes = refresh_card(card_text(self.document), chain, "2026-09-24")
        new = load_card(text)
        self.assertEqual(levels_of(new)["add_below"], old["buy_below"])
        self.assertEqual(new["monitor_variables"][0]["threshold"]["value"], levels_of(new)["buy_below"])   # not the new add
        self.assertEqual(changes["stale_monitors"], [])
        self.document["monitor_variables"][0]["threshold"]["value"] = round(old["buy_below"] * 0.95, 2)   # derived, not equal
        text, changes = refresh_card(card_text(self.document), ladder(), "2026-09-24")
        self.assertEqual(changes["stale_monitors"], [self.document["monitor_variables"][0]["name"]])
        self.assertEqual(load_card(text)["monitor_variables"][0]["threshold"]["value"], round(old["buy_below"] * 0.95, 2))

    def test_same_day_version_is_never_overwritten(self):
        self.assertEqual(refresh_card(card_text(self.document), ladder(), "2026-09-19"),
                         (None, "a version dated 2026-09-19 already exists; refresh on another day"))

    def test_nothing_to_refresh(self):
        same = ladder(2202.33, (0.5376, 0.6423, 0.8994))                                 # the fixture's own inputs
        self.assertEqual(refresh_card(card_text(self.document), same, "2026-09-24"), (None, "inputs unchanged"))
        closed = card()
        closed.update(status="closed", close_reason="expired")
        self.assertEqual(refresh_card(card_text(closed), ladder(), "2026-09-24"), (None, "closed"))
        self.assertEqual(refresh_card(card_text(self.document), {}, "2026-09-24")[1], "931152.CSI not in ladder sidecar")
        bare = card()
        for name in ("add_below", "buy_below", "reduce_above"):
            bare["decision"]["anchors"][name] = {"level": number(None), "target_ratio_pct": number(None), "inputs": None, "rationale": None}
        bare["decision"]["anchors"].update(no_anchor_reason="无行情源", valid_until=None)
        self.assertEqual(refresh_card(card_text(bare), ladder(), "2026-09-24"), (None, "no anchors"))

    def test_end_of_next_month(self):
        self.assertEqual(end_of_next_month(date(2026, 9, 23)), date(2026, 10, 31))
        self.assertEqual(end_of_next_month(date(2026, 12, 5)), date(2027, 1, 31))
        self.assertEqual(end_of_next_month(date(2027, 1, 31)), date(2027, 2, 28))


if __name__ == "__main__":
    unittest.main()
