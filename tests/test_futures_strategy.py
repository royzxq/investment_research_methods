"""v3 boundary regressions using synthetic data; no market/performance claims."""
from contextlib import redirect_stdout
from datetime import date, timedelta
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.futures_strategy import EXIT_RULE, reversion_inputs, trend_inputs, trailing_stop, validate_plan
from scripts.futures_risk import size_position_v3


def calendar():
    start = date(2026, 1, 1)
    # Synthetic exchange calendar deliberately excludes a weekday.
    return [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range(150)
            if (start + timedelta(days=i)).weekday() < 5 and i != 5]


def trend_market(side="long", product="M"):
    days = calendar()
    records = []
    for i, day in enumerate(days[:61]):
        close = 3000 + (i % 7) * 2
        if i == 60:
            close = 3030 if side == "long" else 2970
        records.append(dict(trade_date=day, contract=f"{product}2701", close=close,
                            high=close + 1, low=close - 1, settle=99999))
    return dict(contract=f"{product}2701", records=records, trading_dates=days, as_of_date=days[60])


def reversion_market(side="short"):
    days = calendar()
    values = [200 + (i % 7) * 2 for i in range(58)] + [320, 310, 300]
    if side == "long":
        values = [-v for v in values]
    records = [dict(trade_date=day, near_contract="RB2701", far_contract="RB2705",
                    near_settle=3000 + value, far_settle=3000)
               for day, value in zip(days, values)]
    return dict(near_contract="RB2701", far_contract="RB2705", anchor_low=-100, anchor_high=100,
                records=records, trading_dates=days, as_of_date=days[60])


def plan_request(strategy="trend", side="long"):
    market = trend_market(side) if strategy == "trend" else reversion_market(side)
    days = market["trading_dates"]
    plan = dict(side=side, entry=3030 if side == "long" else 2970,
                entry_date=days[61], latest_exit_date=days[80],
                price_unit="CNY/tonne", multiplier=10, tick_value=10, round_trip_fees=10)
    if strategy == "trend":
        plan.update(targets=None, exit_rule=EXIT_RULE)
    else:
        plan.update(entry=300 if side == "short" else -300,
                    entry_range=[300, 300] if side == "short" else [-300, -300],
                    stop=350 if side == "short" else -350,
                    leg_ratio=[1, 1], convergence_sessions=10,
                    economic_anchor_basis="Synthetic storage/delivery band, not market evidence",
                    convergence_mechanism="Synthetic supply arrival within ten sessions",
                    invalidation_basis="Synthetic delivery restriction strengthens",
                    economic_evidence_refs=["synthetic-evidence"])
    return dict(rule_version="v3.0", strategy=strategy, market=market, plan=plan)


def sizing_request():
    return dict(rule_version="v3.0", equity=150000, risk_unit=1000, regime="normal",
                open_position_risks=[], reserved_order_risks=[], existing_trade_risk=0,
                position_snapshot_verified=True, position_snapshot_as_of="2026-10-11T09:00:00+08:00",
                sizing_as_of="2026-10-11T09:01:00+08:00",
                factors={"strategy": .7, "market_risk": 1, "exchange_buffer": 1},
                factors_complete=True, margin_capacity_lots=50, position_limit_capacity_lots=50,
                execution_capacity_lots=50, stress_capacity_applicable=False, stress_capacity_lots=None,
                weekend_capacity_applicable=False, weekend_capacity_lots=None,
                hard_vetoes=[])


class TrendInputsTests(unittest.TestCase):
    def test_all_five_products_bidirectional_prior_channel_close_only(self):
        for product in ("MA", "RB", "M", "SR", "CF"):
            for side in ("long", "short"):
                result = trend_inputs(trend_market(side, product))
                self.assertEqual((result["status"], result["signal"], result["side"]),
                                 ("valid", "triggered", side))
                self.assertEqual(result["prior20_high"], 3013)
                self.assertEqual(result["prior20_low"], 2999)
                self.assertNotEqual(result["signal_close"], 99999)
                self.assertIsNone(result["targets"])
                self.assertEqual(result["execution_permission"], "not_evaluated")

    def test_exact_channel_touch_is_not_breakout(self):
        market = trend_market()
        market["records"][-1].update(close=3013, high=3014, low=3012)
        self.assertEqual(trend_inputs(market)["signal"], "not_triggered")

    def test_fixed_wilder_initialization_and_no_future_bar_use(self):
        market = trend_market()
        result = trend_inputs(market)
        closes = [r["close"] for r in market["records"]]
        trs = [max(2, abs(b + 1 - a), abs(b - 1 - a)) for a, b in zip(closes, closes[1:])]
        expected = sum(trs[:20]) / 20
        for tr in trs[20:]: expected = (expected * 19 + tr) / 20
        self.assertAlmostEqual(result["atr20"], expected)
        market["records"].append(dict(trade_date=market["trading_dates"][61], close=1, high=1, low=1))
        self.assertEqual(trend_inputs(market)["atr20"], result["atr20"])

    def test_missing_session_close_contract_switch_or_incomplete_bar_never_fills(self):
        mutations = (lambda d: d["records"].pop(30),
                     lambda d: d["records"][30].update(close=None, px=3000),
                     lambda d: d["records"][30].update(contract="M2609"),
                     lambda d: d["records"][60].update(is_complete=False),
                     lambda d: d["records"].append(d["records"][30]))
        for mutate in mutations:
            market = trend_market(); mutate(market)
            result = trend_inputs(market)
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(result["signal"], "unknown")

    def test_no_percentage_rank_or_adx_gate(self):
        market = trend_market()
        market.update(percentile=100, ADX14=2, H250=1000)
        self.assertEqual(trend_inputs(market)["signal"], "triggered")


class ReversionInputsTests(unittest.TestCase):
    def test_two_sided_confirmation_and_negative_spread_volatility(self):
        for side in ("long", "short"):
            result = reversion_inputs(reversion_market(side))
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["side"], side)
            self.assertEqual(result["target"], -100 if side == "long" else 100)
            self.assertIsNotNone(result["volatility_ratio"])

    def test_band_or_two_day_turn_must_be_strict(self):
        market = reversion_market()
        market["records"][-1]["near_settle"] = 3310
        self.assertEqual(reversion_inputs(market)["signal"], "not_triggered")
        market = reversion_market(); market["anchor_high"] = 300
        self.assertEqual(reversion_inputs(market)["signal"], "not_triggered")

    def test_no_close_fallback_no_cross_pair_or_new_product(self):
        for change in (dict(near_settle=None, near_close=3300), dict(near_contract="RB2610")):
            market = reversion_market(); market["records"][-1].update(change)
            self.assertEqual(reversion_inputs(market)["signal"], "unknown")
        market = reversion_market(); market["near_contract"] = "M2701"; market["far_contract"] = "M2705"
        self.assertEqual(reversion_inputs(market)["status"], "incomplete")

    def test_missing_volatility_history_keeps_signal_but_reports_unknown(self):
        market = reversion_market(); market["records"] = market["records"][-3:]
        result = reversion_inputs(market)
        self.assertEqual(result["signal"], "triggered")
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["high_volatility"])

    def test_overflowed_spread_changes_cannot_escape_as_nan_risk_state(self):
        market = reversion_market()
        for index, row in enumerate(market["records"][:-3]):
            row.update(near_settle=1e308 if index % 2 else 1,
                       far_settle=1 if index % 2 else 1e308)
        result = reversion_inputs(market)
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["volatility_ratio"])
        json.dumps(result, allow_nan=False)


class PlanTests(unittest.TestCase):
    def test_trend_has_no_invented_target_or_r_gate_and_actual_entry_stop(self):
        for side in ("long", "short"):
            request = plan_request(side=side)
            result = validate_plan(request)
            self.assertEqual(result["status"], "valid")
            self.assertIsNone(result["targets"])
            self.assertIsNone(result["reward_risk"])
            self.assertEqual(result["cost_unit"], 30)
            delta = abs(result["entry"] - result["stop"])
            self.assertGreaterEqual(delta, 2 * result["signal_inputs"]["atr20"])
            self.assertLess(delta, 2 * result["signal_inputs"]["atr20"] + 1)

    def test_trailing_stop_only_tightens_both_sides(self):
        self.assertEqual(trailing_stop("long", 100, 105, 90, 110), 105)
        self.assertEqual(trailing_stop("long", 100, 105, 108, 120), 108)
        self.assertEqual(trailing_stop("short", 120, 115, 110, 130), 115)
        self.assertEqual(trailing_stop("short", 120, 115, 90, 108), 108)

    def test_entry_second_session_allowed_third_or_signal_day_rejected(self):
        for offset, expected in ((60, "blocked"), (61, "valid"), (62, "valid"), (63, "blocked")):
            request = plan_request(); request["plan"]["entry_date"] = request["market"]["trading_dates"][offset]
            self.assertEqual(validate_plan(request)["status"], expected)

    def test_holding_limit_counts_entry_as_day_one(self):
        request = plan_request(); request["plan"]["latest_exit_date"] = request["market"]["trading_dates"][81]
        self.assertIn("exit_outside_20_session_holding_limit", validate_plan(request)["issues"])

    def test_trend_planned_exit_cannot_be_entry_day(self):
        request = plan_request(); request["plan"]["latest_exit_date"] = request["plan"]["entry_date"]
        self.assertIn("trend_planned_exit_must_follow_entry_day", validate_plan(request)["issues"])

    def test_explicit_signal_and_valid_until_conflicts_are_not_silently_rewritten(self):
        for change in (dict(signal_date="2020-01-01"), dict(valid_until="2030-01-01")):
            request = plan_request(); request["plan"].update(change)
            self.assertEqual(validate_plan(request)["status"], "blocked")
        request = plan_request()
        result = validate_plan(request)
        request["plan"].update(signal_date=result["signal_date"], valid_until=result["valid_until"])
        self.assertEqual(validate_plan(request)["status"], "valid")

    def test_retreat_inside_channel_cancels_trend_and_range_intersects_breakout(self):
        request = plan_request()
        for row in request["market"]["records"]:
            row.update(high=3010, low=2900, close=3000)
        request["market"]["records"][-1].update(high=3012, low=2990, close=3011)
        request["plan"]["entry"] = 3005
        self.assertIn("trend_entry_has_lost_breakout", validate_plan(request)["issues"])
        request["plan"]["entry"] = 3011
        result = validate_plan(request)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["entry_range"][0], 3011)
        request["plan"]["entry_range"] = [3009, 3011]
        self.assertIn("trend_entry_range_exceeds_half_atr_or_breakout", validate_plan(request)["issues"])

    def test_trend_rejects_chase_fixed_target_wrong_spec_nonfinite(self):
        for change in (dict(entry=3040), dict(targets=[3200]), dict(exit_rule="take_profit"),
                       dict(multiplier=100), dict(round_trip_fees=float("nan")), dict(stop=3000)):
            request = plan_request(); request["plan"].update(change)
            self.assertEqual(validate_plan(request)["status"], "blocked")

    def test_reversion_costs_economic_near_edge_and_bidirectional_r(self):
        for side in ("long", "short"):
            request = plan_request("economic_reversion", side)
            result = validate_plan(request)
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["risk_unit"], 550)
            self.assertEqual(result["cost_unit"], 50)
            self.assertAlmostEqual(result["reward_risk"], 1950 / 550)
            request["plan"]["round_trip_slippage"] = 100
            self.assertEqual(validate_plan(request)["cost_unit"], 110)

    def test_reversion_failure_r_missing_economics_and_short_convergence(self):
        for change in (dict(stop=400), dict(economic_anchor_basis=""), dict(economic_evidence_refs=[]),
                       dict(convergence_sessions=4), dict(leg_ratio=[True, 1])):
            request = plan_request("economic_reversion", "short"); request["plan"].update(change)
            self.assertEqual(validate_plan(request)["status"], "blocked")
        request = plan_request("economic_reversion", "short")
        request["plan"]["latest_exit_date"] = request["market"]["trading_dates"][65]
        self.assertEqual(validate_plan(request)["status"], "blocked")

    def test_reversion_exact_net_r_boundary_and_lower_slippage_floor(self):
        request = plan_request("economic_reversion", "short")
        # (2000 - cost) / (500 + cost) = 2.5 at cost=750/3.5.
        # Use integer tick-compatible geometry with exact cost=50 instead:
        # reward=1500, risk=600 -> target=145, entry=300, stop=355.
        request["market"]["anchor_high"] = 145
        request["plan"].update(stop=355, round_trip_slippage=0)
        result = validate_plan(request)
        self.assertEqual(result["reward_risk"], 2.5)
        self.assertEqual(result["status"], "valid")
        request["plan"]["round_trip_fees"] = 10.01
        self.assertEqual(validate_plan(request)["status"], "blocked")

    def test_whole_reversion_range_stays_between_stop_and_near_anchor(self):
        for side, bad_range in (("short", [100, 400]), ("long", [-400, -100])):
            request = plan_request("economic_reversion", side)
            request["plan"]["entry_range"] = bad_range
            self.assertIn("reversion_entry_range_crosses_stop_or_anchor", validate_plan(request)["issues"])

    def test_worst_reversion_range_price_must_satisfy_net_r(self):
        for side, bad_range in (("short", [200, 300]), ("long", [-300, -200])):
            request = plan_request("economic_reversion", side)
            request["plan"]["entry_range"] = bad_range
            result = validate_plan(request)
            self.assertGreater(result["reward_risk"], 2.5)
            self.assertLess(result["entry_range_min_reward_risk"], 2.5)
            self.assertIn("entry_range_net_reward_risk_below_2.5", result["issues"])

    def test_old_a_b_not_relabelled_and_nulls_stay_missing(self):
        request = plan_request(); request["rule_version"] = "B-v2.24"
        self.assertEqual(validate_plan(request)["status"], "blocked")
        request = plan_request(); del request["plan"]["round_trip_fees"]
        result = validate_plan(request)
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["risk_unit"])

    def test_cli_rejects_duplicate_keys(self):
        process = subprocess.run([sys.executable, str(ROOT / "scripts/futures_strategy.py"),
                                  "validate-plan", "--input", "-"], input='{"strategy": "trend", "strategy": "A"}',
                                 text=True, capture_output=True)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(json.loads(process.stdout)["status"], "input_error")


class V3RiskTests(unittest.TestCase):
    def test_all_additional_capacities_are_applied_not_silently_ignored(self):
        for kind in ("execution", "stress", "weekend"):
            request = sizing_request()
            request[f"{kind}_capacity_lots"] = 0
            if kind != "execution": request[f"{kind}_capacity_applicable"] = True
            result = size_position_v3(request)
            self.assertEqual((result["status"], result["final_lots"]), ("blocked", 0))
        request = sizing_request()
        request.update(stress_capacity_applicable=True, stress_capacity_lots=2,
                       weekend_capacity_applicable=True, weekend_capacity_lots=1)
        result = size_position_v3(request)
        self.assertEqual(result["final_lots"], 1)
        self.assertEqual(result["capacity_lots_before_additional"], 3)

    def test_additional_applicability_unknown_or_missing_capacity_keeps_null_final(self):
        for change in (dict(execution_capacity_lots=None), dict(stress_capacity_applicable=None),
                       dict(weekend_capacity_applicable=True), dict(weekend_capacity_applicable=None)):
            request = sizing_request(); request.update(change)
            result = size_position_v3(request)
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(result["risk_lots"], 3)
            self.assertIsNone(result["final_lots"])
        for change in (dict(stress_capacity_lots=999), dict(weekend_capacity_applicable="false"),
                       dict(execution_capacity_lots=-1), dict(execution_capacity_lots=True)):
            request = sizing_request(); request.update(change)
            result = size_position_v3(request)
            self.assertEqual(result["status"], "blocked")
            self.assertIsNone(result["final_lots"])

    def test_existing_zero_budget_stays_zero_after_additional_checks(self):
        request = sizing_request(); request["open_position_risks"] = [6000]
        result = size_position_v3(request)
        self.assertEqual((result["status"], result["final_lots"]), ("blocked", 0))

    def test_core_caps_and_single_floor_after_three_factors(self):
        request = sizing_request()
        self.assertEqual(size_position_v3(request)["final_lots"], 3)
        request["factors"].update(market_risk=.5, exchange_buffer=.8)
        result = size_position_v3(request)
        self.assertEqual(result["final_lots"], 1)
        self.assertEqual(result["available_risk"], 1470)
        self.assertEqual(result["portfolio_risk_cap_current"], 5250)
        self.assertEqual(result["compatibility"], "v3_only")

    def test_reserved_orders_low_cap_same_day_and_unknown_preserved(self):
        request = sizing_request(); request.update(regime="low_exposure", reserved_order_risks=[4000])
        result = size_position_v3(request)
        self.assertEqual(result["final_lots"], 1)
        self.assertEqual(result["portfolio_risk_cap_current"], 5000)
        for change in (dict(position_snapshot_verified=False), dict(factors_complete=False),
                       dict(position_snapshot_as_of="2026-10-10T09:00:00+08:00")):
            request = sizing_request(); request.update(change)
            result = size_position_v3(request)
            self.assertEqual(result["status"], "incomplete")
            self.assertIsNone(result["final_lots"])

    def test_old_factors_and_wrong_fixed_coefficients_rejected(self):
        for change in (dict(D12=.5), dict(strategy=.85), dict(market_risk=.25), dict(exchange_buffer=.5)):
            request = sizing_request(); request["factors"].update(change)
            result = size_position_v3(request)
            self.assertEqual(result["status"], "blocked")
            self.assertIsNone(result["final_lots"])
        request = sizing_request(); del request["factors"]["market_risk"]
        self.assertEqual(size_position_v3(request)["status"], "incomplete")


class V3DataIntegrationTests(unittest.TestCase):
    def test_daily_preserves_actual_fetch_time_across_cache_reads(self):
        import pandas as pd
        from scripts import future_data as module
        from types import SimpleNamespace
        market = trend_market()
        frame = pd.DataFrame(market["records"])
        with patch.object(module, "_daily_cache", {}), patch.object(module, "AS_OF", market["as_of_date"]), \
                patch.object(module, "completed_day_cutoff", return_value=market["as_of_date"]), \
                patch.object(module, "resolve", return_value="M2701.DCE"), \
                patch.object(module, "api", return_value=SimpleNamespace(fut_daily=lambda **kwargs: frame)), \
                patch.object(module.time, "sleep"):
            first = module.daily("M2701")
            with patch.object(module, "api", side_effect=AssertionError("cache must preserve original timestamp")):
                second = module.daily("M2701")
        self.assertEqual(first.attrs["provenance"], second.attrs["provenance"])
        self.assertEqual(first.attrs["provenance"]["source"], "Tushare Pro fut_daily")
        self.assertTrue(first.attrs["provenance"]["fetched_at"].endswith("+08:00"))
        self.assertNotEqual(first.attrs["provenance"]["fetched_at"][:10].replace("-", ""), market["as_of_date"])

    def test_v3_shadow_plan_never_reaches_v2_fixed_target_settler(self):
        from scripts import future_data as module
        document = dict(candidates=[dict(candidate_id="new", strategy="trend")],
                        shadow_plans=[dict(shadow_id="s-new", candidate_id="new")])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.md"
            path.write_text(json.dumps(document))
            with patch.object(module, "discover", return_value=[path]), \
                    patch.object(module, "load_audit", return_value=document), \
                    patch.object(module, "parse_shadow_plan", side_effect=AssertionError("legacy settlement forbidden")), \
                    redirect_stdout(io.StringIO()) as output:
                rows = module.shadow_ledger()
        self.assertEqual(rows, [])
        self.assertIn("v3计划不由v2固定目标结算器统计", output.getvalue())

    def test_default_snapshot_exports_separate_v3_inputs_without_legacy_signal_reuse(self):
        import pandas as pd
        from scripts import future_data as module
        market = trend_market()
        frame = pd.DataFrame(market["records"])
        with tempfile.TemporaryDirectory() as directory, patch.object(module, "OUTDIR", directory), \
                patch.object(module, "AS_OF", market["as_of_date"]), \
                patch.object(module, "completed_day_cutoff", return_value=market["as_of_date"]), \
                patch.object(module, "_trade_cal", return_value=market["trading_dates"]), \
                patch.object(module, "CAL_DEGRADED", []), patch.object(module, "INDICATOR_CONTRACTS", ["M2701"]), \
                patch.object(module, "daily", return_value=frame), patch.object(module, "research_pairs", return_value=[]), \
                patch.object(module, "api", side_effect=AssertionError("network forbidden")), redirect_stdout(io.StringIO()):
            result = module.collect_v3_research()
            saved = json.loads((Path(directory) / f"v3_research_inputs_{market['as_of_date']}.json").read_text())
        self.assertEqual(result["trend"][0]["signal_close"], 3030)
        self.assertEqual(saved["trend"][0]["market_inputs"]["exchange"], "DCE")
        self.assertIsNone(saved["trend"][0]["market_inputs"]["fetched_at"])  # Synthetic frame was not fetched.
        self.assertEqual(saved["rule_version"], "v3.0")
        self.assertEqual(saved["execution_permission"], "not_evaluated")


if __name__ == "__main__": unittest.main()
