"""Pure v3.0 futures research arithmetic; no fetching or trade permission.

CLI: trend-inputs|reversion-inputs|validate-plan --input JSON (or - for stdin).
All dates are YYYY-MM-DD or YYYYMMDD exchange trading-day labels. Calendars
must contain actual exchange sessions, including the plan's future dates.
Trend prices use a real contract's unadjusted close/high/low, never ``px`` or
settlement fallback. Reversion uses the same pair's raw settlements. These
forward research parameters have not been validated as a profitable strategy.
"""

import argparse
from datetime import datetime
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import json
import math
from pathlib import Path
import re
import statistics
import sys

try:
    from .futures_risk import _unique_json_object
except ImportError:
    from futures_risk import _unique_json_object

RULE_VERSION = "v3.0"
TREND_PRODUCTS = frozenset(("MA", "RB", "M", "SR", "CF"))
REVERSION_PRODUCTS = frozenset(("MA", "RB", "SR"))
SPECS = {"MA": (10, 1), "RB": (10, 1), "M": (10, 1), "SR": (10, 1), "CF": (5, 5)}
EXIT_RULE = "initial_2atr_and_prior10_channel_tighten_only_max20_sessions"


def _result(strategy, scope="v3_market_inputs_only"):
    return dict(rule_version=RULE_VERSION, strategy=strategy, scope=scope,
                status="incomplete", signal="unknown", side=None,
                missing_fields=[], issues=[], execution_permission="not_evaluated",
                methodology_validation="forward_research_not_performance_validated")


def _day(value):
    if not isinstance(value, str):
        raise ValueError("date_must_be_string")
    fmt = "%Y-%m-%d" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else "%Y%m%d"
    return datetime.strptime(value, fmt).strftime("%Y%m%d")


def _num(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, bool):
        raise ValueError(f"invalid_numeric:{name}")
    try:
        value = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"invalid_numeric:{name}") from None
    if not math.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0):
        raise ValueError(f"invalid_numeric:{name}")
    return value


def _contract(value, allowed):
    match = re.fullmatch(r"([A-Z]+)(\d{2})(0[1-9]|1[0-2])", value) if isinstance(value, str) else None
    if not match or match[1] not in allowed:
        raise ValueError("unsupported_or_invalid_contract")
    return match[1], int(match[2] + match[3])


def _calendar(values):
    if not isinstance(values, list):
        raise ValueError("trading_dates_must_be_array")
    days = [_day(day) for day in values]
    if not days or days != sorted(set(days)):
        raise ValueError("calendar_requires_sorted_unique_exchange_sessions")
    return days


def _rows(data, result):
    days = _calendar(data["trading_dates"])
    as_of = _day(data["as_of_date"])
    if days[-1] < as_of:
        raise ValueError("calendar_ends_before_as_of")
    eligible = [day for day in days if day <= as_of]
    if not eligible:
        raise ValueError("calendar_does_not_cover_as_of")
    current = eligible[-1]
    records = {}
    for row in data["records"]:
        day = _day(row["trade_date"])
        if day in records:
            raise ValueError("duplicate_trade_date")
        records[day] = row
    result.update(market_trade_date=current, as_of_date=as_of)
    if current not in records or records[current].get("is_complete") is False:
        result["missing_fields"].append(f"completed_bar:{current}")
    return days, current, records


def _window(days, current, records, count):
    pos = days.index(current)
    if pos + 1 < count:
        raise ValueError(f"insufficient_calendar_history:{count}")
    window = days[pos - count + 1:pos + 1]
    if any(day not in records or records[day].get("is_complete") is False for day in window):
        raise ValueError(f"missing_complete_sessions:{count}")
    return [records[day] for day in window]


def _finish(result):
    result["status"] = "incomplete" if result["missing_fields"] else "blocked" if result["issues"] else "valid"
    return result


def _volatility(changes, result):
    if len(changes) < 60 or any(not math.isfinite(change) for change in changes[-60:]):
        result.update(volatility_ratio=None, volatility_status="unknown", high_volatility=None)
        result["missing_fields"].append("volatility_60_finite_changes")
        return
    short, long = statistics.stdev(changes[-20:]), statistics.stdev(changes[-60:])
    # A zero denominator does not establish a low-risk state.
    ratio = short / long if long > 0 and math.isfinite(short) and math.isfinite(long) else None
    result.update(volatility_ratio=ratio, volatility_status="available" if ratio is not None else "unknown",
                  high_volatility=ratio > 1.3 if ratio is not None else None)
    if ratio is None:
        result["missing_fields"].append("finite_nonzero_volatility60")


def trend_inputs(data):
    """Same-contract close vs PRIOR 20 highs/lows; ATR uses 60 true ranges.

    Require 61 consecutive completed bars. ATR20 is seeded with the arithmetic
    mean of the first 20 TRs in this fixed 61-bar window, then Wilder-smoothed
    over the remaining 40. TR uses previous raw close. The fixed initialization
    window makes offline and data-script calculations reproducible.
    """
    result = _result("trend")
    try:
        product, _ = _contract(data["contract"], TREND_PRODUCTS)
        result.update(contract=data["contract"], price_basis="close", product=product)
        days, current, records = _rows(data, result)
        rows = _window(days, current, records, 61)
        prices = []
        for row in rows:
            if row.get("contract", data["contract"]) != data["contract"]:
                raise ValueError("mixed_contract_history")
            close, high, low = (_num(row.get(k), k, positive=True) for k in ("close", "high", "low"))
            if not low <= close <= high:
                raise ValueError("close_outside_daily_high_low")
            prices.append((close, high, low))
        prior = prices[-21:-1]
        high20, low20 = max(p[1] for p in prior), min(p[2] for p in prior)
        close = prices[-1][0]
        tr = [max(p[1] - p[2], abs(p[1] - prev[0]), abs(p[2] - prev[0]))
              for prev, p in zip(prices, prices[1:])]
        atr = sum(tr[:20]) / 20
        for value in tr[20:]:
            atr = (atr * 19 + value) / 20
        if not math.isfinite(atr) or atr <= 0:
            raise ValueError("atr20_must_be_finite_positive")
        side = "long" if close > high20 else "short" if close < low20 else None
        result.update(signal="triggered" if side else "not_triggered", side=side,
                      signal_close=close, prior20_high=high20, prior20_low=low20,
                      prior10_low=min(p[2] for p in prices[-11:-1]),
                      prior10_high=max(p[1] for p in prices[-11:-1]), atr20=atr,
                      atr_initialization="61_bars_first20_TR_mean_then_Wilder",
                      sample_start=days[days.index(current) - 60], targets=None,
                      exit_rule=EXIT_RULE)
        _volatility([math.log(p[0] / prev[0]) for prev, p in zip(prices, prices[1:])], result)
    except KeyError as exc:
        result["missing_fields"].append(str(exc.args[0]))
    except (ValueError, TypeError, IndexError, OverflowError) as exc:
        result["missing_fields"].append(str(exc))
    return _finish(result)


def reversion_inputs(data):
    """Economic-band confirmation; percentile does not determine direction.

    Caller must independently establish and freeze the economic band. Records
    require near_settle and far_settle for the exact named same-product pair.
    The tool cannot establish the band's economics, publication time or truth.
    """
    result = _result("economic_reversion")
    try:
        near, far = data["near_contract"], data["far_contract"]
        pn, mn = _contract(near, REVERSION_PRODUCTS)
        pf, mf = _contract(far, REVERSION_PRODUCTS)
        if pn != pf or mn >= mf:
            raise ValueError("require_same_product_near_before_far")
        low, high = (_num(data[k], k) for k in ("anchor_low", "anchor_high"))
        if low > high:
            raise ValueError("unordered_economic_band")
        result.update(near_contract=near, far_contract=far, product=pn,
                      anchor_low=low, anchor_high=high, price_basis="settle_near_minus_far")
        days, current, records = _rows(data, result)
        rows = _window(days, current, records, 3)

        def spread(row):
            if (row.get("near_contract"), row.get("far_contract")) != (near, far):
                raise ValueError("mixed_or_unidentified_contract_pair")
            return _num(row.get("near_settle"), "near_settle", positive=True) - _num(
                row.get("far_settle"), "far_settle", positive=True)

        values = [spread(row) for row in rows]
        value = values[-1]
        side = ("short" if value > high and value < min(values[:2]) else
                "long" if value < low and value > max(values[:2]) else None)
        result.update(signal="triggered" if side else "not_triggered", side=side,
                      signal_spread=value, prior2_spreads=values[:2],
                      target=high if side == "short" else low if side == "long" else None)
        try:
            history = [spread(row) for row in _window(days, current, records, 61)]
            _volatility([b - a for a, b in zip(history, history[1:])], result)
        except ValueError as exc:
            result.update(volatility_ratio=None, volatility_status="unknown", high_volatility=None)
            result["missing_fields"].append(f"volatility:{exc}")
    except KeyError as exc:
        result["missing_fields"].append(str(exc.args[0]))
    except (ValueError, TypeError, IndexError, OverflowError) as exc:
        result["missing_fields"].append(str(exc))
    return _finish(result)


def trailing_stop(side, initial_stop, prior_stop, prior10_low, prior10_high):
    """Use completed prior10 channel; only tighten an already registered stop."""
    if side not in ("long", "short"):
        raise ValueError("invalid_side")
    values = [_num(v, k, positive=True) for k, v in
              (("initial_stop", initial_stop), ("prior_stop", prior_stop),
               ("prior10_low", prior10_low), ("prior10_high", prior10_high))]
    if values[2] > values[3]:
        raise ValueError("unordered_channel")
    return max(values[:2] + [values[2]]) if side == "long" else min(values[:2] + [values[3]])


def _text(plan, key):
    if not isinstance(plan.get(key), str) or not plan[key].strip():
        raise ValueError(f"required_nonempty:{key}")


def validate_plan(data):
    """Recompute the signal, plan dates, cost and risk; no economic verification.

    Input: rule_version, strategy, market (input to the matching signal helper),
    plan. Plan common fields: side, entry, entry_date, latest_exit_date,
    price_unit='CNY/tonne', multiplier, tick_value, round_trip_fees,
    round_trip_slippage (optional; cannot reduce the 2/4-tick floor).
    Trend: targets=null, exit_rule=EXIT_RULE. Stop is calculated from actual
    entry and the signal ATR, rounded outward to the contract tick.
    Reversion: leg_ratio=[1,1], stop, entry_range=[low,high] (may be [entry,entry]),
    convergence_sessions (integer 5..20),
    economic_anchor_basis, convergence_mechanism, invalidation_basis,
    economic_evidence_refs (nonempty strings). Target is the near band edge.
    Signal timing, frozen evidence, relevance, stress and account checks remain
    necessary outside this numerical helper.
    """
    strategy = data.get("strategy") if isinstance(data, dict) else None
    result = _result(strategy, "v3_plan_arithmetic_only")
    result.update(risk_unit=None, cost_unit=None, net_reward=None, reward_risk=None,
                  targets=None, stop=None, final_lots=None,
                  pending_checks=["frozen_prospective_definition_and_evidence", "economic_causality",
                                  "contract_life_and_forced_exit_dates", "latest_executable_quotes",
                                  "stress_and_events", "account_and_capacity"])
    if not isinstance(data, dict) or data.get("rule_version") != RULE_VERSION:
        result["issues"].append("explicit_v3_rule_version_required")
        return _finish(result)
    if strategy not in ("trend", "economic_reversion"):
        result["issues"].append("unsupported_v3_strategy")
        return _finish(result)
    try:
        market, plan = data["market"], data["plan"]
        signal = trend_inputs(market) if strategy == "trend" else reversion_inputs(market)
        result["signal_inputs"] = signal
        result.update(signal=signal["signal"], side=signal["side"])
        result["missing_fields"].extend(signal["missing_fields"])
        if signal["signal"] != "triggered":
            result["issues"].append("price_signal_not_triggered")
            return _finish(result)
        side = plan["side"]
        if side != signal["side"]:
            raise ValueError("plan_side_disagrees_with_signal")
        sign = 1 if side == "long" else -1
        entry = _num(plan["entry"], "entry", positive=strategy == "trend")
        days = _calendar(market["trading_dates"])
        signal_index = days.index(signal["market_trade_date"])
        if signal_index + 2 >= len(days):
            raise ValueError("calendar_missing_two_entry_sessions")
        entry_date, exit_date = _day(plan["entry_date"]), _day(plan["latest_exit_date"])
        entry_index, exit_index = days.index(entry_date), days.index(exit_date)
        if not signal_index < entry_index <= signal_index + 2:
            raise ValueError("entry_outside_next_two_sessions")
        if not entry_index <= exit_index <= entry_index + 19:
            raise ValueError("exit_outside_20_session_holding_limit")
        if strategy == "trend" and entry_index == exit_index:
            raise ValueError("trend_planned_exit_must_follow_entry_day")
        for key, computed in (("signal_date", signal["market_trade_date"]),
                              ("valid_until", days[signal_index + 2])):
            if key in plan and _day(plan[key]) != computed:
                raise ValueError(f"supplied_{key}_conflicts_with_computed_date")
        result.update(entry_expiry=days[signal_index + 2], entry_date=entry_date,
                      latest_exit_date=exit_date, entry=entry,
                      signal_date=datetime.strptime(signal["market_trade_date"], "%Y%m%d").date().isoformat(),
                      valid_until=datetime.strptime(days[signal_index + 2], "%Y%m%d").date().isoformat())
        if plan["price_unit"] != "CNY/tonne":
            raise ValueError("invalid_price_unit")
        multiplier = _num(plan["multiplier"], "multiplier", positive=True)
        tick_value = _num(plan["tick_value"], "tick_value", positive=True)
        expected_multiplier, tick = SPECS[signal["product"]]
        if multiplier != expected_multiplier or tick_value != multiplier * tick:
            raise ValueError("contract_specification_mismatch")
        if Decimal(str(entry)) % tick != 0:
            raise ValueError("entry_not_on_contract_tick")
        fees = _num(plan["round_trip_fees"], "round_trip_fees", nonnegative=True)
        slip_floor = (2 if strategy == "trend" else 4) * tick_value
        slippage = max(slip_floor, _num(plan.get("round_trip_slippage", slip_floor),
                                        "round_trip_slippage", nonnegative=True))
        cost_decimal = Decimal(str(fees)) + Decimal(str(slippage))
        cost = float(cost_decimal)
        if strategy == "trend":
            if "targets" not in plan or plan["targets"] is not None:
                raise ValueError("trend_targets_must_be_explicit_null")
            if plan["exit_rule"] != EXIT_RULE:
                raise ValueError("trend_exit_rule_mismatch")
            if abs(entry - signal["signal_close"]) > .5 * signal["atr20"] + 1e-10:
                raise ValueError("entry_more_than_half_atr_from_signal_close")
            if ((side == "long" and entry <= signal["prior20_high"])
                    or (side == "short" and entry >= signal["prior20_low"])):
                raise ValueError("trend_entry_has_lost_breakout")
            raw = Decimal(str(entry)) - Decimal(sign) * 2 * Decimal(str(signal["atr20"]))
            stop = float((raw / tick).to_integral_value(
                rounding=ROUND_FLOOR if side == "long" else ROUND_CEILING) * tick)
            if stop <= 0:
                raise ValueError("trend_stop_must_be_positive")
            if "stop" in plan and _num(plan["stop"], "stop", positive=True) != stop:
                raise ValueError("supplied_trend_stop_differs_from_registered_2atr_stop")
            range_low = math.ceil((signal["signal_close"] - .5 * signal["atr20"]) / tick) * tick
            range_high = math.floor((signal["signal_close"] + .5 * signal["atr20"]) / tick) * tick
            if side == "long":
                range_low = max(range_low, (math.floor(signal["prior20_high"] / tick) + 1) * tick)
            else:
                range_high = min(range_high, (math.ceil(signal["prior20_low"] / tick) - 1) * tick)
            result.update(stop=stop, exit_rule=EXIT_RULE,
                          prior10_channel_stop=signal["prior10_low"] if side == "long" else signal["prior10_high"],
                          entry_range=[range_low, range_high])
        else:
            if plan["leg_ratio"] != [1, 1] or any(type(v) is not int for v in plan["leg_ratio"]):
                raise ValueError("reversion_requires_1_to_1")
            for key in ("economic_anchor_basis", "convergence_mechanism", "invalidation_basis"):
                _text(plan, key)
            refs = plan["economic_evidence_refs"]
            if not isinstance(refs, list) or not refs or any(not isinstance(r, str) or not r.strip() for r in refs):
                raise ValueError("economic_evidence_refs_required")
            horizon = plan["convergence_sessions"]
            if type(horizon) is not int or not 5 <= horizon <= 20:
                raise ValueError("convergence_sessions_must_be_5_to_20")
            if exit_index - entry_index + 1 < horizon:
                raise ValueError("holding_window_shorter_than_convergence_mechanism")
            stop, target = _num(plan["stop"], "stop"), signal["target"]
            if any(Decimal(str(value)) % tick != 0 for value in (stop, target)):
                raise ValueError("reversion_stop_or_anchor_target_not_on_tick")
            if not sign * stop < sign * entry < sign * target:
                raise ValueError("invalid_stop_entry_anchor_order")
            result.update(stop=stop, targets=[target])
        if strategy == "economic_reversion" or "entry_range" in plan:
            entry_range = plan["entry_range"]
            if not isinstance(entry_range, list) or len(entry_range) != 2:
                raise ValueError("entry_range_requires_two_prices")
            low, high = (_num(value, "entry_range", positive=strategy == "trend") for value in entry_range)
            if not low <= entry <= high:
                raise ValueError("entry_outside_frozen_entry_range")
            if any(Decimal(str(value)) % tick != 0 for value in (low, high)):
                raise ValueError("entry_range_not_on_contract_tick")
            if strategy == "trend" and (low < result["entry_range"][0] or high > result["entry_range"][1]):
                raise ValueError("trend_entry_range_exceeds_half_atr_or_breakout")
            if strategy == "economic_reversion":
                if ((side == "long" and not stop < low <= high < target)
                        or (side == "short" and not stop > high >= low > target)):
                    raise ValueError("reversion_entry_range_crosses_stop_or_anchor")
            result["entry_range"] = [low, high]
        risk_decimal = Decimal(sign) * (Decimal(str(entry)) - Decimal(str(stop))) * Decimal(str(multiplier)) + cost_decimal
        risk = float(risk_decimal)
        if risk <= 0 or not math.isfinite(risk + cost):
            raise ValueError("invalid_plan_risk")
        result.update(risk_unit=risk, cost_unit=cost)
        if strategy == "economic_reversion":
            reward_decimal = (Decimal(sign) * (Decimal(str(signal["target"])) - Decimal(str(entry)))
                              * Decimal(str(multiplier)) - cost_decimal)
            reward = float(reward_decimal)
            ratio_decimal = reward_decimal / risk_decimal
            ratio = float(ratio_decimal)
            result.update(net_reward=reward, reward_risk=ratio)
            if ratio_decimal < Decimal("2.5"):
                result["issues"].append("net_reward_risk_below_2.5")
            worst_entry = Decimal(str(result["entry_range"][0 if side == "short" else 1]))
            worst_risk = Decimal(sign) * (worst_entry - Decimal(str(stop))) * Decimal(str(multiplier)) + cost_decimal
            worst_reward = (Decimal(sign) * (Decimal(str(target)) - worst_entry) * Decimal(str(multiplier))
                            - cost_decimal)
            worst_ratio = worst_reward / worst_risk
            result["entry_range_min_reward_risk"] = float(worst_ratio)
            if worst_ratio < Decimal("2.5"):
                result["issues"].append("entry_range_net_reward_risk_below_2.5")
    except KeyError as exc:
        result["missing_fields"].append(str(exc.args[0]))
    except (ValueError, TypeError, IndexError, OverflowError) as exc:
        result["issues"].append(str(exc))
    return _finish(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("trend-inputs", "reversion-inputs", "validate-plan"))
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        data = json.loads(source, object_pairs_hook=_unique_json_object)
        result = {"trend-inputs": trend_inputs, "reversion-inputs": reversion_inputs,
                  "validate-plan": validate_plan}[args.operation](data)
    except (OSError, ValueError, TypeError) as exc:
        result = dict(status="input_error", error=type(exc).__name__, execution_permission="not_evaluated")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    return 0 if result["status"] == "valid" else 2


if __name__ == "__main__":
    raise SystemExit(main())
