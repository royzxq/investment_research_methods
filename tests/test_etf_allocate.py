"""Synthetic holdings and cards; none of these numbers is market data."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etf_allocate import plan_month

CORE = {"core-a500": 28, "core-star50": 7, "core-hsi": 15, "core-hk-dividend-lowvol": 20}


def theme_card(seat, target, code, status="active", money="continue"):
    """Only the fields plan_month reads; real cards pass scripts/validate_etf_card.py first."""
    return {"card_id": f"theme-{seat}", "as_of_date": "2026-11-06", "status": status, "task": "theme",
            "sizing": {"bet_group": seat}, "instruments": {"list": [{"code": code, "role": "primary"}]},
            "decision": {"target_weight_pct": {"value": target, "source": "user:2026-11-06"}, "new_money_action": money}}


def holdings(values, **extra):
    positions = [{"code": f"{index:06d}.OF", "value_cny": value, "slot": slot} for index, (slot, value) in enumerate(values.items())]
    return {"as_of": "2026-11-28", "cash_cny": 0, "positions": positions, **extra}


class PlanMonthTests(unittest.TestCase):
    def test_on_target_account_buys_in_proportion_and_keeps_theme_cash(self):
        cards = [theme_card("defense", 10, "160630.SZ"), theme_card("chemicals", 10, "013528.OF")]
        values = {**{slot: weight * 1000 for slot, weight in CORE.items()}, "defense": 10000, "chemicals": 10000}
        report = plan_month(cards, holdings(values, cash_cny=10000), 10000)
        self.assertEqual(report["theme_cash_pct"], 10)
        buys = {slot: round(amount, 6) for slot, amount in report["allocation"]["buys"].items()}
        self.assertEqual(buys, {"core-a500": 2800, "core-star50": 700, "core-hsi": 1500, "core-hk-dividend-lowvol": 2000,
                                "defense": 1000, "chemicals": 1000})
        self.assertAlmostEqual(report["allocation"]["cash_after"], 11000)   # 10% of the 110,000 account stays theme cash
        self.assertEqual(report["check_after"]["modules_out_of_band"], [])

    def test_themes_above_the_module_hold_back_no_cash_from_the_core(self):
        cards = [theme_card("innovative-drug", 10, "021031.OF"), theme_card("defense", 0, "160630.SZ", status="no_buy", money="pause")]
        report = plan_month(cards, holdings({"core-a500": 100000, "innovative-drug": 180000, "defense": 40000}), 10000)
        self.assertEqual((report["theme_cash_pct"], report["theme_cash_reserve_pct"]), (20, 0))
        self.assertAlmostEqual(sum(report["allocation"]["buys"].values()), 10000)
        self.assertEqual(report["allocation"]["buys"].get("innovative-drug"), 0)   # 10% target is far below its holding
        self.assertAlmostEqual(report["allocation"]["cash_after"], 0)

    def test_a_claimed_code_needs_no_slot_and_gold_stays_outside(self):
        cards = [theme_card("defense", 10, "160630.SZ")]
        report = plan_month(cards, {"as_of": "2026-11-28", "cash_cny": 0, "positions": [
            {"code": "160630.SZ", "value_cny": 5000}, {"code": "000307.OF", "value_cny": 9999}]}, 1000)
        self.assertEqual(report["skipped"], ["000307.OF"])
        self.assertAlmostEqual(report["allocation"]["total"], 6000)

    def test_unknowns_stop_the_run_instead_of_becoming_zeros(self):
        with self.assertRaisesRegex(ValueError, "claimed by no current card"):
            plan_month([], {"positions": [{"code": "012349.OF", "value_cny": 1}]}, 1000)
        with self.assertRaisesRegex(ValueError, "theme seats held without a target"):
            plan_month([], holdings({"hk-tech": 5000}), 1000)
        with self.assertRaisesRegex(ValueError, "the current cards say defense"):
            plan_month([theme_card("defense", 10, "160630.SZ")],
                       {"positions": [{"code": "160630.SZ", "value_cny": 1, "slot": "chemicals"}]}, 1000)
        with self.assertRaisesRegex(ValueError, "approved steps"):
            plan_month([], holdings({"hk-tech": 5000}, theme_targets_pct={"hk-tech": 7}), 1000)

    def test_a_theme_being_exited_takes_no_new_money(self):
        cards = [theme_card("hk-tech", 0, "012349.OF", status="no_buy", money="pause")]
        report = plan_month(cards, holdings({"hk-tech": 50000}), 10000)
        self.assertNotIn("hk-tech", report["allocation"]["buys"])
        self.assertIn("hk-tech", report["paused"])
        self.assertEqual([row["slot"] for row in report["check_before"]["above_ceiling"]], ["hk-tech"])

    def test_deep_drawdown_pauses_themes_but_core_dca_continues(self):
        cards = [theme_card("defense", 10, "160630.SZ")]
        ledger = [("20260131", 100000, 0), ("20260228", 74000, 0)]
        report = plan_month(cards, holdings({"core-a500": 1000, "defense": 1000}), 10000, ledger)
        self.assertEqual(report["drawdown_review"], "pause_new_theme_risk")
        self.assertEqual(report["allocation"]["buys"].get("defense"), None)
        self.assertGreater(report["allocation"]["buys"]["core-a500"], 0)
        self.assertEqual(plan_month(cards, holdings({"core-a500": 1000}), 0, [("20260131", 100, 0), ("20260228", 69, 0)])
                         ["drawdown_review"], "reapprove_risk_budget")


if __name__ == "__main__":
    unittest.main()
