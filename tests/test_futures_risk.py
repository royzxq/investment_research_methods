"""Offline regression tests: no market data request and no credential access."""

import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.futures_risk import precheck_2atr, size_position, validate_a_plan


def a_plan():
    return dict(near_contract="MA2610", far_contract="MA2701", leg_ratio=[1, 1],
                mode="reversion", side="short", percentile=100, entry=313,
                stop=350, tp1=100, tp2=-33, invalidation_basis="供给冲击证据强化且价差突破350",
                price_unit="CNY/tonne", multiplier=10, tick_value=10, round_trip_fees=10)


def sizing():
    return dict(equity=150000, risk_unit=3500, regime="normal",
                open_position_risks=[], reserved_order_risks=[], existing_trade_risk=0,
                position_snapshot_verified=True,
                position_snapshot_as_of="2026-09-04T15:00:00+08:00",
                sizing_as_of="2026-09-04T15:10:00+08:00",
                factors={"strategy": 0.85}, factors_complete=True,
                margin_capacity_lots=10, position_limit_capacity_lots=10, hard_vetoes=[])


class APlanTests(unittest.TestCase):
    def assert_no_plan_amounts(self, result):
        for field in ("risk_unit", "cost_unit", "net_reward_tp1", "reward_risk"):
            self.assertIsNone(result[field], field)

    def test_short_plan_uses_real_stop_and_net_tp1(self):
        result = validate_a_plan(a_plan())
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["risk_unit"], 420)
        self.assertEqual(result["cost_unit"], 50)
        self.assertEqual(result["net_reward_tp1"], 2080)
        self.assertAlmostEqual(result["reward_risk"], 2080 / 420)
        self.assertIsNone(result["final_lots"])
        self.assertEqual(result["execution_permission"], "not_evaluated")

    def test_missing_or_null_price_unit_cannot_produce_money_from_unitless_prices(self):
        for absent in (True, False):
            with self.subTest(absent=absent):
                plan = a_plan()
                # This unitless example previously passed with R exactly 2.5.
                plan.update(entry=20, stop=21, tp1=0, tp2=-1)
                if absent:
                    del plan["price_unit"]
                else:
                    plan["price_unit"] = None
                result = validate_a_plan(plan)
                self.assertEqual(result["status"], "incomplete")
                self.assertIn("price_unit", result["missing_fields"])
                self.assert_no_plan_amounts(result)

    def test_wrong_price_units_and_types_are_rejected_without_conversion(self):
        for unit in ("spread_pct", "%", "USD/tonne", "CNY/barrel", "",
                     "CNY/t", "元/吨", "cny/tonne", " CNY/tonne ",
                     17, True, {}, ["CNY/tonne"]):
            with self.subTest(unit=unit):
                plan = a_plan()
                plan["price_unit"] = unit
                result = validate_a_plan(plan)
                self.assertEqual(result["status"], "blocked")
                self.assertIn("invalid_price_unit", result["issues"])
                self.assert_no_plan_amounts(result)

    def test_canonical_products_keep_negative_price_spreads_in_cny_per_tonne(self):
        for near, far in (("MA2610", "MA2701"), ("RB2610", "RB2701"),
                          ("SR2701", "SR2705")):
            with self.subTest(near=near, far=far):
                plan = a_plan()
                plan.update(near_contract=near, far_contract=far, entry=-100,
                            stop=-80, tp1=-250, tp2=-300)
                result = validate_a_plan(plan)
                self.assertEqual(result["status"], "valid")
                self.assertEqual(result["risk_unit"], 250)
                self.assertEqual(result["cost_unit"], 50)
                self.assertEqual(result["net_reward_tp1"], 1450)
                self.assertAlmostEqual(result["reward_risk"], 5.8)

    def test_tonne_unit_does_not_authorize_non_a_products(self):
        for near, far in (("SC2610", "SC2611"), ("ZZ2610", "ZZ2611"),
                          ("M2701", "M2705"), ("AU2610", "AU2612"),
                          ("CF2701", "CF2705")):
            with self.subTest(near=near, far=far):
                plan = a_plan()
                plan.update(near_contract=near, far_contract=far)
                result = validate_a_plan(plan)
                self.assertEqual(result["status"], "blocked")
                self.assertIn("unsupported_a_product", result["issues"])
                self.assert_no_plan_amounts(result)

    def test_validate_a_cli_enforces_price_unit_and_product_contract(self):
        command = [sys.executable, str(ROOT / "scripts/futures_risk.py"),
                   "validate-a", "--input", "-"]
        for change, expected_status, expected_reason in (
                ({}, "incomplete", "price_unit"),
                ({"price_unit": None}, "incomplete", "price_unit"),
                ({"price_unit": "spread_pct"}, "blocked", "invalid_price_unit"),
                ({"price_unit": "USD/tonne"}, "blocked", "invalid_price_unit"),
                ({"price_unit": "CNY/tonne", "near_contract": "SC2610",
                  "far_contract": "SC2611"}, "blocked", "unsupported_a_product")):
            with self.subTest(change=change):
                plan = a_plan()
                del plan["price_unit"]
                plan.update(change)
                process = subprocess.run(command, input=json.dumps(plan), text=True,
                                         capture_output=True)
                self.assertEqual(process.returncode, 2, process.stderr)
                result = json.loads(process.stdout)
                self.assertEqual(result["status"], expected_status)
                field = "missing_fields" if expected_status == "incomplete" else "issues"
                self.assertIn(expected_reason, result[field])
                self.assert_no_plan_amounts(result)
        process = subprocess.run(command, input=json.dumps(a_plan()), text=True,
                                 capture_output=True, check=True)
        result = json.loads(process.stdout)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["risk_unit"], 420)

    def test_old_median_stop_is_invalid(self):
        plan = a_plan()
        plan.update(stop=-33, tp1=-67, tp2=-95)
        self.assertIn("invalid_stop_entry_target_order", validate_a_plan(plan)["issues"])

    def test_fees_can_invalidate_otherwise_adequate_ratio(self):
        plan = a_plan()
        plan.update(entry=100, stop=110, tp1=60, tp2=50, round_trip_fees=20)
        result = validate_a_plan(plan)
        self.assertEqual(result["risk_unit"], 160)
        self.assertEqual(result["net_reward_tp1"], 340)
        self.assertEqual(result["status"], "blocked")

    def test_higher_actual_slippage_reduces_net_reward_and_increases_risk(self):
        plan = a_plan()
        plan["round_trip_slippage"] = 400
        result = validate_a_plan(plan)
        self.assertEqual(result["cost_unit"], 410)
        self.assertEqual(result["risk_unit"], 780)
        self.assertEqual(result["net_reward_tp1"], 1720)
        self.assertEqual(result["status"], "blocked")
        plan["round_trip_slippage"] = 1
        self.assertEqual(validate_a_plan(plan)["cost_unit"], 50)

    def test_missing_fields_are_incomplete(self):
        plan = a_plan()
        del plan["stop"]
        del plan["round_trip_fees"]
        result = validate_a_plan(plan)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(set(result["missing_fields"]), {"stop", "round_trip_fees"})
        self.assertIsNone(result["risk_unit"])

    def test_continuation_needs_explicit_permission(self):
        plan = a_plan()
        plan.update(mode="continuation", side="long", entry=-100, stop=-120, tp1=0, tp2=30)
        self.assertEqual(validate_a_plan(plan)["status"], "incomplete")
        plan["continuation_permitted"] = False
        self.assertEqual(validate_a_plan(plan)["status"], "blocked")
        plan["continuation_permitted"] = True
        self.assertEqual(validate_a_plan(plan)["status"], "valid")

    def test_reversion_scope_and_contracts(self):
        for change in ({"percentile": 0}, {"side": "long"}, {"leg_ratio": [1, 2]},
                       {"far_contract": "RB2701"}, {"near_contract": "MA2705"}):
            with self.subTest(change=change):
                plan = a_plan()
                plan.update(change)
                self.assertEqual(validate_a_plan(plan)["status"], "blocked")

    def test_numeric_input_rejection(self):
        for field, value in (("entry", float("nan")), ("stop", float("inf")),
                             ("tick_value", -1), ("round_trip_fees", -1),
                             ("multiplier", True), ("percentile", 101)):
            with self.subTest(field=field, value=value):
                plan = a_plan()
                plan[field] = value
                self.assertEqual(validate_a_plan(plan)["status"], "blocked")


class SizingTests(unittest.TestCase):
    def test_ma_single_floor_retains_one_under_normal_cap(self):
        result = size_position(sizing())
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["trade_risk_cap"], 5250)
        self.assertEqual(result["portfolio_risk_cap"], 5250)
        self.assertEqual(result["portfolio_risk_cap_normal"], 5250)
        self.assertEqual(result["portfolio_risk_cap_current"], 5250)
        self.assertEqual(result["trade_effective_risk"], 4462.5)
        self.assertEqual(result["risk_lots"], 1)
        self.assertEqual(result["final_lots"], 1)
        self.assertEqual(result["scope"], "risk_sizing_only")

    def test_low_exposure_uses_fixed_cash_cap_only_on_portfolio(self):
        request = sizing()
        request.update(regime="low_exposure", risk_unit=1000)
        result = size_position(request)
        self.assertEqual(result["trade_effective_risk"], 4462.5)
        self.assertEqual(result["portfolio_risk_cap_normal"], 5250)
        self.assertEqual(result["portfolio_risk_cap_current"], 5000)
        self.assertEqual(result["portfolio_risk_cap"], 5000)
        self.assertEqual(result["remaining_portfolio_risk"], 5000)
        self.assertEqual(result["low_exposure_cash_cap"], 5000)
        self.assertNotIn("portfolio_regime_factor", result)
        self.assertEqual(result["risk_lots"], 4)
        request["risk_unit"] = 3500
        self.assertEqual(size_position(request)["final_lots"], 1)

    def test_fixed_low_exposure_cap_is_not_an_equity_scaled_ratio(self):
        for equity, normal_cap, current_cap, quantity in (
                (150000, 5250, 5000, 5), (200000, 7000, 5000, 5),
                (100000, 3500, 3500, 3)):
            with self.subTest(equity=equity):
                request = sizing()
                request.update(equity=equity, regime="low_exposure", risk_unit=1000,
                               factors={"strategy": 1})
                result = size_position(request)
                self.assertEqual(result["trade_risk_cap"], normal_cap)
                self.assertEqual(result["portfolio_risk_cap_normal"], normal_cap)
                self.assertEqual(result["portfolio_risk_cap_current"], current_cap)
                self.assertEqual(result["risk_lots"], quantity)
                request["regime"] = "normal"
                self.assertEqual(size_position(request)["portfolio_risk_cap_current"], normal_cap)

    def test_low_exposure_subtracts_positions_orders_and_trade_usage_once(self):
        request = sizing()
        request.update(regime="low_exposure", risk_unit=1000,
                       open_position_risks=[1000, 500], reserved_order_risks=[500],
                       existing_trade_risk=1000)
        result = size_position(request)
        self.assertEqual(result["portfolio_risk_cap_current"], 5000)
        self.assertEqual(result["used_total_risk"], 2000)
        self.assertEqual(result["remaining_portfolio_risk"], 3000)
        self.assertEqual(result["remaining_trade_risk"], 3462.5)
        self.assertEqual(result["risk_lots"], 3)

    def test_low_exposure_exact_budget_boundary_and_overuse(self):
        request = sizing()
        request.update(regime="low_exposure", risk_unit=5000, factors={"strategy": 1})
        self.assertEqual(size_position(request)["final_lots"], 1)
        request["reserved_order_risks"] = ["0.01"]
        result = size_position(request)
        self.assertEqual(result["remaining_portfolio_risk"], 4999.99)
        self.assertEqual(result["final_lots"], 0)
        request.update(risk_unit="0.01", reserved_order_risks=["4999.99"])
        result = size_position(request)
        self.assertEqual(result["remaining_portfolio_risk"], .01)
        self.assertEqual(result["final_lots"], 1)
        request["reserved_order_risks"] = ["5000.01"]
        result = size_position(request)
        self.assertEqual(result["remaining_portfolio_risk"], 0)
        self.assertEqual(result["final_lots"], 0)

    def test_low_exposure_still_requires_account_and_capacity_facts(self):
        for missing in ("reserved_order_risks", "position_snapshot_verified", "margin_capacity_lots"):
            with self.subTest(missing=missing):
                request = sizing()
                request["regime"] = "low_exposure"
                del request[missing]
                result = size_position(request)
                self.assertEqual(result["status"], "incomplete")
                self.assertIsNone(result["final_lots"])

    def test_positions_and_unfilled_orders_both_use_budget(self):
        request = sizing()
        request.update(risk_unit=1000, open_position_risks=[1000, 500], reserved_order_risks=[1000])
        result = size_position(request)
        self.assertEqual(result["used_total_risk"], 2500)
        self.assertEqual(result["remaining_portfolio_risk"], 2750)
        self.assertEqual(result["risk_lots"], 2)

    def test_addition_uses_remaining_trade_budget_without_double_deduction(self):
        request = sizing()
        request.update(risk_unit=1000, open_position_risks=[2000], reserved_order_risks=[500], existing_trade_risk=2500)
        result = size_position(request)
        self.assertEqual(result["remaining_trade_risk"], 1962.5)
        self.assertEqual(result["remaining_portfolio_risk"], 2750)
        self.assertEqual(result["risk_lots"], 1)
        request["existing_trade_risk"] = 2600
        self.assertEqual(size_position(request)["status"], "blocked")

    def test_unknown_account_and_incomplete_factors_never_imply_zero_risk(self):
        for field in ("open_position_risks", "reserved_order_risks", "existing_trade_risk",
                      "position_snapshot_verified", "factors_complete", "hard_vetoes"):
            with self.subTest(field=field):
                request = sizing()
                del request[field]
                result = size_position(request)
                self.assertEqual(result["status"], "incomplete")
                self.assertIsNone(result["final_lots"])
                self.assertIsNone(result["risk_lots"])

    def test_snapshot_must_be_verified_and_same_day(self):
        for change in ({"position_snapshot_verified": False},
                       {"position_snapshot_as_of": "2026-09-03T15:00:00+08:00"},
                       {"position_snapshot_as_of": "2026-09-04T16:00:00+08:00"}):
            request = sizing()
            request.update(change)
            self.assertEqual(size_position(request)["status"], "incomplete")

    def test_missing_capacities_preserve_only_risk_quantity(self):
        request = sizing()
        del request["margin_capacity_lots"]
        result = size_position(request)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["risk_lots"], 1)
        self.assertIsNone(result["final_lots"])

    def test_capacity_then_explicit_hard_veto(self):
        request = sizing()
        request.update(risk_unit=100, margin_capacity_lots=3, position_limit_capacity_lots=2)
        self.assertEqual(size_position(request)["final_lots"], 2)
        request["hard_vetoes"] = ["direction_not_permitted"]
        self.assertEqual(size_position(request)["status"], "blocked")
        self.assertEqual(size_position(request)["final_lots"], 0)

    def test_known_veto_does_not_hide_missing_account_or_capacity(self):
        request = sizing()
        request["hard_vetoes"] = ["direction_not_permitted"]
        del request["margin_capacity_lots"]
        result = size_position(request)
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["final_lots"])
        self.assertEqual(result["risk_lots"], 1)
        self.assertIn("hard_veto:direction_not_permitted", result["issues"])
        del request["open_position_risks"]
        result = size_position(request)
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["risk_lots"])
        self.assertIsNone(result["final_lots"])

    def test_rejects_negative_nonfinite_and_fractional_capacity(self):
        for field, value in (("equity", -1), ("risk_unit", 0), ("risk_unit", "Infinity"),
                             ("margin_capacity_lots", 1.5), ("open_position_risks", [-1]),
                             ("reserved_order_risks", [float("nan")]),
                             ("position_snapshot_as_of", "2026-09-04T15:00:00")):
            request = sizing()
            request[field] = value
            self.assertEqual(size_position(request)["status"], "blocked")

    def test_no_score_multiplier_or_repeated_low_exposure(self):
        for factors in ({"strategy": .85, "D10": 1.3},
                        {"strategy": .85, "low_exposure": .5}):
            request = sizing()
            request["factors"] = factors
            self.assertEqual(size_position(request)["status"], "blocked")

    def test_d12_aliases_are_rejected_instead_of_double_discounted(self):
        request = sizing()
        request.update(risk_unit=1500,
                       factors={"strategy": .85, "D12_high_volatility": .5, "D12_event": .5})
        result = size_position(request)
        self.assertEqual(result["status"], "blocked")
        self.assertIsNone(result["risk_lots"])
        self.assertIn("unknown_factor_group:D12_high_volatility", result["issues"])
        self.assertIn("unknown_factor_group:D12_event", result["issues"])
        request["factors"] = {"strategy": .85, "D12": .5}
        result = size_position(request)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["trade_effective_risk"], 2231.25)
        self.assertEqual(result["risk_lots"], 1)

    def test_independent_t1_event_group_can_apply_alongside_d12(self):
        request = sizing()
        request.update(risk_unit=1500,
                       factors={"strategy": .85, "D12": .5, "event_window": .5})
        result = size_position(request)
        self.assertEqual(result["trade_effective_risk"], 1115.625)
        self.assertEqual(result["risk_lots"], 0)

    def test_2atr_is_only_precheck(self):
        result = precheck_2atr(83.1, 10, 10, equity=150000, high_volatility=True)
        self.assertEqual(result["precheck_risk_unit"], 1682)
        self.assertEqual(result["precheck_lots_upper_bound"], 1)
        self.assertIsNone(result["final_lots"])

    def test_cli_json_stdin(self):
        command = [sys.executable, str(ROOT / "scripts/futures_risk.py"), "size", "--input", "-"]
        result = subprocess.run(command, input=json.dumps(sizing()), text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)["final_lots"], 1)
        result = subprocess.run(command, input="{}", text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "incomplete")

    def test_cli_rejects_duplicate_json_keys_at_any_depth(self):
        command = [sys.executable, str(ROOT / "scripts/futures_risk.py"), "size", "--input", "-"]
        for source in ('{"equity":150000,"equity":300000}',
                       '{"factors":{"strategy":0.85,"D12":0.5,"D12":0.3}}'):
            with self.subTest(source=source):
                result = subprocess.run(command, input=source, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2)
                output = json.loads(result.stdout)
                self.assertEqual(output["status"], "blocked")
                self.assertIsNone(output["final_lots"])
                self.assertIn("duplicate_json_key", output["issues"])


class DataOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Importing the data module constructs no API client. All data access
        # below is mocked and api() is patched to fail on accidental use.
        cls.module = importlib.import_module("scripts.future_data")

    def test_empty_registry_does_not_assert_flat_account(self):
        out = io.StringIO()
        with patch.object(self.module, "POSITIONS", []), redirect_stdout(out):
            self.module.atr_recheck()
        self.assertIn("账户持仓与挂单风险未知", out.getvalue())
        self.assertNotIn("当前空仓", out.getvalue())

    def test_missing_leg_data_cannot_pass_research_checks(self):
        import pandas as pd
        m = self.module
        dates = [f"202608{i:02d}" for i in range(1, 22)]
        pair = pd.DataFrame(dict(trade_date=dates, px_n=[3206] * 21, px_f=[2893] * 21,
                                 spread=[313] * 21, spread_pct=[10.8] * 21))
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as temp, patch.object(m, "OUTDIR", temp), \
                patch.object(m, "AS_OF", "20260904"), patch.object(m, "pair_series", return_value=pair), \
                patch.object(m, "_volume20", side_effect=ValueError("missing")), \
                patch.object(m, "delist_date", side_effect=ValueError("missing")), \
                patch.object(m, "api", side_effect=AssertionError("network forbidden")), redirect_stdout(out):
            result = m.spread_percentile("MA", "MA2610", "MA2701")
        self.assertEqual(result["data_status"], "incomplete")
        self.assertIsNone(result["final_lots"])
        self.assertIn("#1", str(result["missing_fields"]))
        self.assertIn("#2", str(result["missing_fields"]))
        self.assertIn("计划未完成", out.getvalue())
        self.assertNotIn("主仓触发", out.getvalue())
        self.assertNotIn("价差腿一手风险", out.getvalue())

    def test_volume_window_requires_twenty_finite_observations(self):
        import pandas as pd
        m = self.module
        for values in ([10000] * 19, [10000] * 19 + [float("nan")], [10000] * 19 + [-1]):
            data = pd.DataFrame(dict(trade_date=["20260904"] * len(values), vol=values))
            with patch.object(m, "AS_OF", "20260904"), patch.object(m, "daily", return_value=data):
                with self.assertRaises(ValueError):
                    m._volume20("MA2701")

    def test_indicator_precheck_zero_is_not_a_31_veto(self):
        import numpy as np
        import pandas as pd
        m = self.module
        dates = pd.bdate_range(end="2026-09-04", periods=80).strftime("%Y%m%d")
        prices = np.linspace(3000, 3100, 80)
        data = pd.DataFrame(dict(trade_date=dates, px=prices, high=prices + 300,
                                 low=prices - 300, vol=[20000] * 80))
        with patch.object(m, "AS_OF", "20260904"), patch.object(m, "daily", return_value=data), \
                patch.object(m, "delist_date", return_value="20270115"), \
                patch.object(m, "_busdays", return_value=80), patch.object(m, "CAL_DEGRADED", []), \
                patch.object(m, "api", side_effect=AssertionError("network forbidden")):
            result = m.indicators("MA2701")
        self.assertEqual(result["2ATR预检数量上界(非最终手数)"], 0)
        self.assertNotIn("#31", result["否决检查"])
        self.assertIn("250日窗口样本不足", result["否决检查"])
        self.assertNotIn("手数(高波×0.5后)", result)


if __name__ == "__main__":
    unittest.main()
