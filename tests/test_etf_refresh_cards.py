"""Synthetic card and ladder; the numbers are not market data."""
import json
from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etf_refresh_cards import end_of_next_month, refresh_card
from scripts.validate_etf_card import load_card
from tests.test_validate_etf_card import card, number


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
                           "snapshot_as_of": "2026-10-16"}}


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.document = card()
        self.document["monitor_variables"][0].update(
            metric="index_level", operator="<", threshold=number(levels_of(self.document)["buy_below"], "calc:level_at_drawdown_state"),
            action="review")

    def test_anchors_monitor_prose_and_lineage_move_together(self):
        text, changes = refresh_card(card_text(self.document), ladder(), "2026-10-19")
        new = load_card(text)
        anchors = new["decision"]["anchors"]
        self.assertEqual(levels_of(new), {"add_below": 1200.0, "buy_below": 1440.0, "reduce_above": 2160.0})
        self.assertEqual(anchors["buy_below"]["inputs"]["rolling_high"]["value"], 2400.0)
        self.assertEqual(anchors["buy_below"]["inputs"]["state"]["value"], 0.6)
        self.assertEqual(anchors["valid_until"], "2026-11-30")
        self.assertEqual(new["monitor_variables"][0]["threshold"]["value"], 1440.0)     # pinned to buy_below, moved with it
        self.assertEqual((new["as_of_date"], new["supersedes"], new["snapshot_ref"]),
                         ("2026-10-19", "research/etf-cards/cn-pharma-tactical-2026-09-19.md", "research/etf-2026-10-16-data-snapshot.txt"))
        self.assertEqual(new["thesis"], self.document["thesis"])                        # thesis untouched
        self.assertIn("buy_below 1,440.00 与 reduce_above 2,160.00，以及无关的 1,880.55", text)
        self.assertIn("> **点位机械刷新 @2026-10-19**", text.split("\n")[2])
        self.assertEqual(changes["file"], "research/etf-cards/cn-pharma-tactical-2026-10-19.md")

    def test_nothing_to_refresh(self):
        same = ladder(2202.33, (0.5376, 0.6423, 0.8994))                                 # the fixture's own inputs
        self.assertEqual(refresh_card(card_text(self.document), same, "2026-10-19"), (None, "inputs unchanged"))
        closed = card()
        closed.update(status="closed", close_reason="expired")
        self.assertEqual(refresh_card(card_text(closed), ladder(), "2026-10-19"), (None, "closed"))
        self.assertEqual(refresh_card(card_text(self.document), {}, "2026-10-19")[1], "931152.CSI not in ladder sidecar")
        bare = card()
        for name in ("add_below", "buy_below", "reduce_above"):
            bare["decision"]["anchors"][name] = {"level": number(None), "target_ratio_pct": number(None), "inputs": None, "rationale": None}
        bare["decision"]["anchors"].update(no_anchor_reason="无行情源", valid_until=None)
        self.assertEqual(refresh_card(card_text(bare), ladder(), "2026-10-19"), (None, "no anchors"))

    def test_end_of_next_month(self):
        self.assertEqual(end_of_next_month(date(2026, 9, 23)), date(2026, 10, 31))
        self.assertEqual(end_of_next_month(date(2026, 12, 5)), date(2027, 1, 31))
        self.assertEqual(end_of_next_month(date(2027, 1, 31)), date(2027, 2, 28))


if __name__ == "__main__":
    unittest.main()
