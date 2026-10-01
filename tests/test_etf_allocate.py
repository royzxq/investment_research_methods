"""Synthetic holdings and cards; none of these numbers is market data."""
from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etf_allocate import plan_month

CORE = {"core-a500": 28, "core-star50": 7, "core-hsi": 15, "core-hk-dividend-lowvol": 20}


ON = date(2026, 11, 28)


def run(*args, **kwargs):
    kwargs.setdefault("on", ON)   # card versions in effect on a fixed date, not on the day the tests run
    return plan_month(*args, **kwargs)


def theme_card(seat, target, code, status="active", money="continue", stock="none", as_of="2026-11-06", effective=None):
    """Only the fields plan_month reads; real cards pass scripts/validate_etf_card.py first."""
    return {"card_id": f"theme-{seat}", "as_of_date": as_of, "status": status, "task": "theme",
            "sizing": {"bet_group": seat}, "instruments": {"list": [{"code": code, "role": "primary"}]},
            "decision": {"target_weight_pct": {"value": target, "source": f"user:{as_of}"}, "new_money_action": money,
                         "stock_action": stock, "effective_from": effective or as_of}}


def holdings(values, **extra):
    positions = [{"code": f"{index:06d}.OF", "value_cny": value, "slot": slot} for index, (slot, value) in enumerate(values.items())]
    return {"as_of": "2026-11-28", "cash_cny": 0, "positions": positions, **extra}


class PlanMonthTests(unittest.TestCase):
    def test_on_target_account_buys_in_proportion_and_keeps_theme_cash(self):
        cards = [theme_card("defense", 10, "160630.SZ"), theme_card("chemicals", 10, "013528.OF")]
        values = {**{slot: weight * 1000 for slot, weight in CORE.items()}, "defense": 10000, "chemicals": 10000}
        report = run(cards, holdings(values, cash_cny=10000), 10000)
        self.assertEqual(report["theme_cash_pct"], 10)
        buys = {slot: round(amount, 6) for slot, amount in report["allocation"]["buys"].items()}
        self.assertEqual(buys, {"core-a500": 2800, "core-star50": 700, "core-hsi": 1500, "core-hk-dividend-lowvol": 2000,
                                "defense": 1000, "chemicals": 1000})
        self.assertAlmostEqual(report["allocation"]["cash_after"], 11000)   # 10% of the 110,000 account stays theme cash
        self.assertEqual(report["check_after"]["modules_out_of_band"], [])

    def test_themes_above_the_module_hold_back_no_cash_from_the_core(self):
        cards = [theme_card("innovative-drug", 10, "021031.OF"), theme_card("defense", 0, "160630.SZ", status="no_buy", money="pause")]
        report = run(cards, holdings({"core-a500": 100000, "innovative-drug": 180000, "defense": 40000}), 10000)
        self.assertEqual((report["theme_cash_pct"], report["theme_cash_reserve_pct"]), (20, 0))
        self.assertAlmostEqual(sum(report["allocation"]["buys"].values()), 10000)
        self.assertEqual(report["allocation"]["buys"].get("innovative-drug"), 0)   # 10% target is far below its holding
        self.assertAlmostEqual(report["allocation"]["cash_after"], 0)

    def test_a_claimed_code_needs_no_slot_and_gold_stays_outside(self):
        cards = [theme_card("defense", 10, "160630.SZ")]
        report = run(cards, {"as_of": "2026-11-28", "cash_cny": 0, "positions": [
            {"code": "160630.SZ", "value_cny": 5000}, {"code": "000307.OF", "value_cny": 9999}]}, 1000)
        self.assertEqual(report["skipped"], ["000307.OF"])
        self.assertAlmostEqual(report["allocation"]["total"], 6000)

    def test_unknowns_stop_the_run_instead_of_becoming_zeros(self):
        with self.assertRaisesRegex(ValueError, "claimed by no current card"):
            run([], {"positions": [{"code": "012349.OF", "value_cny": 1}]}, 1000)
        with self.assertRaisesRegex(ValueError, "a rebalance needs every held theme's target"):
            run([], holdings({"hk-tech": 5000}), 1000, rebalance=True)
        with self.assertRaisesRegex(ValueError, "fx_to_cny"):
            run([], {"positions": [{"code": "02800.HK", "value": 75000, "currency": "HKD", "slot": "core-hsi"}]}, 1000)
        with self.assertRaisesRegex(ValueError, "the current cards say defense"):
            run([theme_card("defense", 10, "160630.SZ")],
                       {"positions": [{"code": "160630.SZ", "value_cny": 1, "slot": "chemicals"}]}, 1000)
        with self.assertRaisesRegex(ValueError, "approved steps"):
            run([], holdings({"hk-tech": 5000}, theme_targets_pct={"hk-tech": 7}), 1000)

    def test_before_the_first_theme_review_new_money_goes_to_the_core_gaps(self):
        values = {"core-a500": 20000, "core-star50": 10000, "core-hk-dividend-lowvol": 40000, "hk-tech": 50000,
                  "innovative-drug": 95000}
        report = run([], holdings(values), 10000)
        self.assertEqual(report["undecided"], ["hk-tech", "innovative-drug"])
        self.assertEqual(report["theme_cash_reserve_pct"], 0)   # themes already hold far more than the module
        shares = {slot: round(share, 1) for slot, share in report["allocation"]["shares_pct"].items() if share > 0}
        self.assertEqual(set(shares), {"core-a500", "core-star50", "core-hsi", "core-hk-dividend-lowvol"})
        self.assertAlmostEqual(sum(shares.values()), 100, places=0)

    def test_hkd_rows_convert_at_the_stated_rate(self):
        report = run([], {"as_of": "2026-10-01", "cash_cny": 0, "fx_to_cny": {"HKD": {"rate": 0.86062, "source": "snapshot§7"}},
                                 "positions": [{"code": "02800.HK", "value": 75000, "currency": "HKD", "slot": "core-hsi"}]}, 0)
        self.assertAlmostEqual(report["allocation"]["total"], 64546.5)

    def test_rebalance_keeps_the_cross_border_seat_and_moves_theme_excess_to_the_core(self):
        values = {"core-a500": 20000, "core-star50": 10000, "core-hsi": 65000, "core-hk-dividend-lowvol": 40000,
                  "hk-tech": 50000, "innovative-drug": 95000, "defense": 50000, "chemicals": 9000}
        targets = {"hk-tech": 10, "innovative-drug": 10, "defense": 10, "chemicals": 0}
        report = run([], holdings(values, theme_targets_pct=targets), 10000, rebalance=True, keep=["core-hsi"])
        sells = report["allocation"]["sells"]
        self.assertNotIn("core-hsi", sells)
        self.assertEqual(sorted(sells), ["chemicals", "defense", "hk-tech", "innovative-drug"])
        self.assertAlmostEqual(sells["chemicals"], 9000)                                        # target 0: sold out
        self.assertAlmostEqual(sells["innovative-drug"], 95000 - 0.10 * report["allocation"]["total"])
        self.assertAlmostEqual(report["check_after"]["module_weights_pct"]["theme"], 30)
        self.assertEqual(report["theme_cash_reserve_pct"], 0)
        with self.assertRaisesRegex(ValueError, "--keep names seats that are not held"):
            run([], holdings(values, theme_targets_pct=targets), 0, rebalance=True, keep=["core-a50"])

    def test_a_cards_exit_is_sold_this_month_without_a_rebalance_run(self):
        cards = [theme_card("hk-tech", 0, "012349.OF", status="no_buy", money="pause", stock="exit"),
                 theme_card("defense", 10, "160630.SZ")]
        report = run(cards, holdings=holdings({"core-a500": 20000, "hk-tech": 50000, "defense": 10000}),
                            new_money=10000)
        self.assertEqual(report["directed"], {"hk-tech": "exit"})
        self.assertEqual(report["allocation"]["sells"], {"hk-tech": 50000})
        self.assertNotIn("defense", report["allocation"]["sells"])          # no card action, no rebalance: not sold
        self.assertAlmostEqual(sum(report["allocation"]["buys"].values()) + report["allocation"]["cash_after"], 60000)
        self.assertAlmostEqual(report["check_after"]["weights_pct"]["hk-tech"], 0)   # weights and stress reflect the sale

    def test_a_reduce_sells_down_to_target_and_a_future_version_waits_for_its_date(self):
        old = theme_card("defense", 10, "160630.SZ", as_of="2026-11-06")
        new = theme_card("defense", 5, "160630.SZ", stock="reduce", as_of="2026-11-20", effective="2026-12-01")
        values = holdings({"core-a500": 50000, "defense": 30000})
        before = run([old, new], holdings=values, new_money=0)
        self.assertEqual((before["targets_pct"]["defense"], before["allocation"]["sells"]), (10, {}))
        after = plan_month(on=date(2026, 12, 1), documents=[old, new], holdings=values, new_money=0)
        self.assertAlmostEqual(after["allocation"]["sells"]["defense"], 30000 - 0.05 * 80000)

    def test_a_theme_being_exited_takes_no_new_money(self):
        cards = [theme_card("hk-tech", 0, "012349.OF", status="no_buy", money="pause")]
        report = run(cards, holdings({"hk-tech": 50000}), 10000)
        self.assertNotIn("hk-tech", report["allocation"]["buys"])
        self.assertIn("hk-tech", report["paused"])
        self.assertEqual([row["slot"] for row in report["check_before"]["above_ceiling"]], ["hk-tech"])

    def test_deep_drawdown_pauses_themes_but_core_dca_continues(self):
        cards = [theme_card("defense", 10, "160630.SZ")]
        ledger = [("20260131", 100000, 0), ("20260228", 74000, 0)]
        report = run(cards, holdings({"core-a500": 1000, "defense": 1000}), 10000, ledger)
        self.assertEqual(report["drawdown_review"], "pause_new_theme_risk")
        self.assertEqual(report["allocation"]["buys"].get("defense"), None)
        self.assertGreater(report["allocation"]["buys"]["core-a500"], 0)
        self.assertEqual(run(cards, holdings({"core-a500": 1000}), 0, [("20260131", 100, 0), ("20260228", 69, 0)])
                         ["drawdown_review"], "reapprove_risk_budget")


if __name__ == "__main__":
    unittest.main()
