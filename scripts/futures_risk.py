"""Offline plan validation and risk sizing for futures framework v2.21.

No market data or credentials are accessed. ``valid`` means this calculation is
complete; it never grants permission to trade. Fees are the actual round-trip
fees for both legs of one 1:1 spread unit, in account currency.

CLI: python scripts/futures_risk.py validate-a|size --input request.json
Use --input - to read JSON from stdin. Missing facts are not inferred.
JSON duplicate keys are rejected at every nesting level. Sizing factors must
use the canonical group names in FACTOR_GROUPS; aliases are not accepted.
"""

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
import json
import math
import re
import sys

RISK_RATE = Decimal("0.035")
LOW_EXPOSURE_CASH_CAP = Decimal("5000")
MIN_A_REWARD_RISK = Decimal("2.5")
A_PRICE_UNIT = "CNY/tonne"
A_PRODUCTS = frozenset(("MA", "RB", "SR"))

# Each independent risk group appears once. The caller must resolve multiple
# applicable rules within a group to the strictest value before sizing.
FACTOR_GROUPS = {
    "strategy": "Strategy sizing coefficient (framework 2.2)",
    "D11": "One strictest high-price-position tier (3.5)",
    "D12": "One volatility group: high ATR, event T-3, high-volatility resonance (3.5b)",
    "D13": "Macro pressure (3.5c)",
    "D14": "Production restart / hot-metal invalidation (3.5d)",
    "D15": "Equity double-loss risk (3.5e)",
    "event_window": "Independent T-1 holding discipline (6.9), never a D12 T-3 alias",
    "exchange_buffer": "Exchange margin / position-limit buffer (2.3)",
    "promotion": "First-period promotion coefficient (product card / 2.2)",
    "driver_weakness": "Weak driver or basis-inventory-profit divergence (2.3)",
    "MA_oil_guard": "One strictest MA crude-oil guard coefficient (1.5 / 2.3)",
    "seasonal_adx": "Seasonal strategy low-ADX adjustment (2.2)",
    "policy_adverse": "Policy adverse-price adjustment (2.2 / strategy E)",
    "equity_confirmation": "IM/IC policy-flow confirmation adjustment (2.3)",
    "correlation_recalibration": "Unhedged equity-beta correlation recalibration (2.3)",
}


class DuplicateJSONKey(ValueError):
    """Input object contains a duplicate key and must not silently overwrite."""


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKey
        result[key] = value
    return result


def _result():
    return {"status": "incomplete", "issues": [], "missing_fields": [],
            "risk_lots": None, "final_lots": None,
            "execution_permission": "not_evaluated", "scope": "risk_sizing_only"}


def _required(data, key, result):
    if key not in data or data[key] is None:
        result["missing_fields"].append(key)
        return None
    return data[key]


def _number(value, field, result, *, minimum=None, positive=False, integer=False):
    try:
        if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
            raise ValueError
        number = Decimal(str(value))
        if not number.is_finite() or not math.isfinite(float(number)):
            raise ValueError
        if positive and number <= 0:
            raise ValueError
        if minimum is not None and number < minimum:
            raise ValueError
        if integer and number != number.to_integral_value():
            raise ValueError
        return number
    except (InvalidOperation, ValueError, OverflowError):
        result["issues"].append(f"invalid_numeric:{field}")
        return None


def _numeric_field(data, key, result, **kwargs):
    value = _required(data, key, result)
    return None if value is None else _number(value, key, result, **kwargs)


def _finish(result):
    result["status"] = ("incomplete" if result["missing_fields"] else
                        "blocked" if result["issues"] else "valid")
    if result["status"] == "incomplete":
        result["final_lots"] = None
    return result


def _amount(number, result):
    value = float(number)
    if not math.isfinite(value):
        result["issues"].append("nonfinite_calculation")
        return None
    return value


def validate_a_plan(plan):
    """Validate explicit S=near-far, same-product 1:1 MA/RB/SR A plans.

    Required: near_contract, far_contract, leg_ratio=[1,1], mode, side,
    percentile, entry, stop, tp1, tp2, invalidation_basis, multiplier,
    tick_value, round_trip_fees, price_unit="CNY/tonne". All four spread
    prices must be absolute yuan-per-tonne values, never spread percentages.
    No unit inference or conversion is performed. Missing or incompatible
    units leave all monetary calculations and reward/risk unset. Only the
    framework's MA/RB/SR A products are supported; other contract quote units
    require a separately verified model. Multiplier is tonnes per contract;
    tick_value is CNY per tick per leg, while round-trip costs are CNY per
    paired spread unit.
    Optional round_trip_slippage is an amount:
    use the greater of the supplied amount and the 4*tick_value default.
    Continuation also requires an explicit
    continuation_permitted=True. Negative spread prices are valid.
    """
    result = _result()
    result["scope"] = "a_plan_validation_only"
    result.update(risk_unit=None, cost_unit=None, net_reward_tp1=None, reward_risk=None,
                  candidate_strength=None)
    if not isinstance(plan, dict):
        result["issues"].append("plan_must_be_object")
        return _finish(result)

    contracts = []
    for field in ("near_contract", "far_contract"):
        value = _required(plan, field, result)
        if value is not None:
            match = re.fullmatch(r"([A-Za-z]+)(\d{2})(0[1-9]|1[0-2])", value) if isinstance(value, str) else None
            if not match:
                result["issues"].append(f"invalid_contract:{field}")
            else:
                contracts.append((match[1].upper(), int(match[2] + match[3])))
    contracts_ordered = (len(contracts) == 2 and
                         contracts[0][0] == contracts[1][0] and
                         contracts[0][1] < contracts[1][1])
    if len(contracts) == 2 and not contracts_ordered:
        result["issues"].append("require_same_product_and_near_before_far")
    if any(product not in A_PRODUCTS for product, _ in contracts):
        result["issues"].append("unsupported_a_product")
    contracts_supported = (contracts_ordered and
                           all(product in A_PRODUCTS for product, _ in contracts))
    price_unit = _required(plan, "price_unit", result)
    price_unit_valid = isinstance(price_unit, str) and price_unit == A_PRICE_UNIT
    if price_unit is not None and not price_unit_valid:
        result["issues"].append("invalid_price_unit")
    ratio = _required(plan, "leg_ratio", result)
    if ratio is not None and (not isinstance(ratio, list) or len(ratio) != 2 or
                              any(type(v) is not int or v != 1 for v in ratio)):
        result["issues"].append("require_1_to_1_leg_ratio")
    mode = _required(plan, "mode", result)
    side = _required(plan, "side", result)
    if mode is not None and mode not in ("reversion", "continuation"):
        result["issues"].append("invalid_mode")
    if side is not None and side not in ("long", "short"):
        result["issues"].append("invalid_side")
    basis = _required(plan, "invalidation_basis", result)
    if basis is not None and (not isinstance(basis, str) or not basis.strip()):
        result["issues"].append("invalidation_basis_must_be_nonempty")
    if mode == "continuation":
        permitted = _required(plan, "continuation_permitted", result)
        if permitted is not None and permitted is not True:
            result["issues"].append("continuation_not_explicitly_permitted")
    q = _numeric_field(plan, "percentile", result, minimum=0)
    if q is not None:
        if q > 100:
            result["issues"].append("percentile_out_of_range")
        else:
            result["candidate_strength"] = "high" if q >= 85 else "candidate" if q >= 70 else "none"
        if mode == "reversion" and (q < 70 or side not in (None, "short")):
            result["issues"].append("current_reversion_scope_requires_high_percentile_short")

    prices = {field: _numeric_field(plan, field, result)
              for field in ("entry", "stop", "tp1", "tp2")}
    multiplier = _numeric_field(plan, "multiplier", result, positive=True)
    tick = _numeric_field(plan, "tick_value", result, positive=True)
    fees = _numeric_field(plan, "round_trip_fees", result, minimum=0)
    slippage = None
    if "round_trip_slippage" in plan:
        slippage = _numeric_field(plan, "round_trip_slippage", result, minimum=0)
    if all(value is not None for value in prices.values()) and side in ("long", "short"):
        entry, stop, tp1, tp2 = (prices[k] for k in ("entry", "stop", "tp1", "tp2"))
        ordered = stop < entry < tp1 <= tp2 if side == "long" else stop > entry > tp1 >= tp2
        if not ordered:
            result["issues"].append("invalid_stop_entry_target_order")
        elif (price_unit_valid and contracts_supported and
              all(value is not None for value in (multiplier, tick, fees))):
            direction = Decimal(1 if side == "long" else -1)
            cost = max(4 * tick, slippage) + fees if slippage is not None else 4 * tick + fees
            risk = direction * (entry - stop) * multiplier + cost
            reward = direction * (tp1 - entry) * multiplier - cost
            ratio = reward / risk
            result.update(risk_unit=_amount(risk, result), cost_unit=_amount(cost, result),
                          net_reward_tp1=_amount(reward, result),
                          reward_risk=_amount(ratio, result))
            if ratio < MIN_A_REWARD_RISK:
                result["issues"].append("tp1_net_reward_risk_below_2.5")
    return _finish(result)


def size_position(request):
    """Size once after all monetary risk reductions, then apply capacities.

    Explicit inputs: equity, risk_unit, regime=normal|low_exposure,
    open_position_risks and reserved_order_risks (nonnegative amounts; [] only
    after account review), position_snapshot_verified=True, timezone-aware ISO
    position_snapshot_as_of and sizing_as_of (same China calendar day; snapshot
    no later than sizing),
    existing_trade_risk (this trade's open plus reserved risk, already included
    in the account lists; explicit zero for a new trade),
    factors (only FACTOR_GROUPS keys, including strategy), factors_complete=True,
    margin_capacity_lots, position_limit_capacity_lots, hard_vetoes.
    Normal portfolio and single-trade caps remain equity * 0.035. Low exposure
    sets the current portfolio cap to min(normal cap, 5000 account-currency
    units), once; it is a fixed cash cap, never a per-trade multiplier.
    Read portfolio_risk_cap_normal and portfolio_risk_cap_current explicitly.
    portfolio_risk_cap now aliases the CURRENT cap (previously the normal cap;
    this is a schema correction, not a backward-compatibility guarantee).
    portfolio_regime_factor has been removed; low_exposure_cash_cap records
    the fixed configured ceiling, including when the normal regime is active.
    ``final_lots`` is a capacity calculation, not full-rule trade permission.
    Each intact structure is one combined risk amount; count uncovered partial
    fills as directional risk. Do not count the same fill in both lists and do
    not credit unverified correlation offsets. Score bonuses (including D10)
    are not sizing factors.
    Each canonical group can occur only once. D12 high volatility, event T-3
    and resonance are resolved to the strictest single D12 value by the caller;
    unknown aliases such as D12_high_volatility or D12_event are rejected.
    event_window is only independent T-1 holding discipline, not D12 event T-3.
    Direct Python dict callers must likewise reject duplicate keys before dict
    construction; the CLI enforces this for all JSON objects.
    """
    result = _result()
    if not isinstance(request, dict):
        result["issues"].append("request_must_be_object")
        return _finish(result)
    equity = _numeric_field(request, "equity", result, positive=True)
    risk = _numeric_field(request, "risk_unit", result, positive=True)
    existing = _numeric_field(request, "existing_trade_risk", result, minimum=0)
    regime = _required(request, "regime", result)
    if regime is not None and regime not in ("normal", "low_exposure"):
        result["issues"].append("invalid_regime")
    verified = _required(request, "position_snapshot_verified", result)
    if verified is False:
        result["missing_fields"].append("verified_position_snapshot")
    elif verified is not None and verified is not True:
        result["issues"].append("position_snapshot_verified_must_be_boolean")
    timestamps = {}
    for field in ("position_snapshot_as_of", "sizing_as_of"):
        value = _required(request, field, result)
        if value is not None:
            try:
                stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if stamp.tzinfo is None:
                    raise ValueError
                timestamps[field] = stamp.astimezone(timezone(timedelta(hours=8)))
            except (ValueError, TypeError, AttributeError, OverflowError):
                result["issues"].append(f"invalid_timestamp:{field}")
    if len(timestamps) == 2:
        snapshot, sizing = (timestamps[f] for f in ("position_snapshot_as_of", "sizing_as_of"))
        if snapshot > sizing or snapshot.date() != sizing.date():
            result["missing_fields"].append("position_snapshot_for_sizing_day")
    used_amounts = {}
    for field in ("open_position_risks", "reserved_order_risks"):
        positions = _required(request, field, result)
        if positions is not None:
            if not isinstance(positions, list):
                result["issues"].append(f"{field}_must_be_list")
            else:
                amounts = [_number(v, f"{field}[{i}]", result, minimum=0)
                           for i, v in enumerate(positions)]
                if all(v is not None for v in amounts):
                    used_amounts[field] = sum(amounts, Decimal(0))
    if len(used_amounts) == 2 and existing is not None:
        if existing > sum(used_amounts.values(), Decimal(0)):
            result["issues"].append("existing_trade_risk_exceeds_account_used_risk")
    factors = _required(request, "factors", result)
    complete = _required(request, "factors_complete", result)
    if complete is not None and complete is not True:
        if complete is False:
            result["missing_fields"].append("complete_applicable_factors")
        else:
            result["issues"].append("factors_complete_must_be_boolean")
    factor_product = None
    if factors is not None:
        if not isinstance(factors, dict):
            result["issues"].append("factors_must_be_object")
        else:
            if "strategy" not in factors:
                result["missing_fields"].append("factors.strategy")
            product = Decimal(1)
            for name, value in factors.items():
                if not isinstance(name, str) or not name.strip():
                    result["issues"].append("factor_name_must_be_nonempty")
                elif any(s in name.lower() for s in ("low_exposure", "regime", "低敞口")):
                    result["issues"].append("portfolio_regime_factor_must_not_be_repeated_per_trade")
                elif name not in FACTOR_GROUPS:
                    result["issues"].append(f"unknown_factor_group:{name}")
                number = _number(value, f"factors.{name}", result, minimum=0)
                if number is not None:
                    if number > 1:
                        result["issues"].append(f"risk_reduction_factor_above_one:{name}")
                    product *= number
            factor_product = product
    vetoes = _required(request, "hard_vetoes", result)
    if vetoes is not None:
        if not isinstance(vetoes, list) or any(not isinstance(v, str) or not v.strip() for v in vetoes):
            result["issues"].append("hard_vetoes_must_be_nonempty_strings")
        elif vetoes:
            result["issues"].extend(f"hard_veto:{v}" for v in vetoes)
    # Capacity facts may be missing while the risk-only quantity is calculable.
    risk_missing = list(result["missing_fields"])
    capacities = [_numeric_field(request, field, result, minimum=0, integer=True)
                  for field in ("margin_capacity_lots", "position_limit_capacity_lots")]
    non_veto_issues = [issue for issue in result["issues"] if not issue.startswith("hard_veto:")]
    if not non_veto_issues and not risk_missing:
        trade_cap = equity * RISK_RATE
        portfolio_cap_normal = equity * RISK_RATE
        portfolio_cap_current = (min(portfolio_cap_normal, LOW_EXPOSURE_CASH_CAP)
                                 if regime == "low_exposure" else portfolio_cap_normal)
        effective = trade_cap * factor_product
        used = used_amounts["open_position_risks"] + used_amounts["reserved_order_risks"]
        remaining = max(Decimal(0), portfolio_cap_current - used)
        trade_remaining = max(Decimal(0), effective - existing)
        available = min(trade_remaining, remaining)
        quantity = int((available / risk).to_integral_value(rounding=ROUND_FLOOR))
        result.update(trade_risk_cap=_amount(trade_cap, result),
                      portfolio_risk_cap_normal=_amount(portfolio_cap_normal, result),
                      portfolio_risk_cap_current=_amount(portfolio_cap_current, result),
                      portfolio_risk_cap=_amount(portfolio_cap_current, result),
                      low_exposure_cash_cap=_amount(LOW_EXPOSURE_CASH_CAP, result),
                      used_open_risk=_amount(used_amounts["open_position_risks"], result),
                      reserved_order_risk=_amount(used_amounts["reserved_order_risks"], result),
                      used_total_risk=_amount(used, result),
                      trade_effective_risk=_amount(effective, result),
                      existing_trade_risk=_amount(existing, result),
                      remaining_trade_risk=_amount(trade_remaining, result),
                      remaining_portfolio_risk=_amount(remaining, result),
                      available_risk=_amount(available, result), risk_lots=quantity)
        calculation_issues = [issue for issue in result["issues"] if not issue.startswith("hard_veto:")]
        if not calculation_issues and all(cap is not None for cap in capacities):
            result["capacity_lots"] = min(quantity, *(int(cap) for cap in capacities))
            result["final_lots"] = 0 if vetoes else result["capacity_lots"]
            if result["final_lots"] == 0:
                if not vetoes:
                    result["issues"].append("no_capacity_within_verified_limits")
        elif quantity == 0:
            result["issues"].append("no_capacity_within_verified_risk_budget")
    return _finish(result)


def precheck_2atr(atr20, multiplier, tick_value, *, equity, high_volatility):
    """2ATR scenario upper-bound quantity only; excludes actual fees and caps.

    This is not a strategy stop, final sizing, account-risk check or #31 veto.
    It reduces the budget before the only floor operation.
    """
    result = _result()
    result["scope"] = "2atr_scenario_precheck"
    nums = [_number(value, name, result, positive=True)
            for value, name in ((atr20, "atr20"), (multiplier, "multiplier"),
                                (tick_value, "tick_value"), (equity, "equity"))]
    if type(high_volatility) is not bool:
        result["issues"].append("high_volatility_must_be_boolean")
    if not result["issues"]:
        atr, multiplier, tick, equity = nums
        unit = 2 * atr * multiplier + 2 * tick
        budget = equity * RISK_RATE * (Decimal("0.5") if high_volatility else Decimal(1))
        result.update(precheck_risk_unit=_amount(unit, result),
                      precheck_lots_upper_bound=int((budget / unit).to_integral_value(rounding=ROUND_FLOOR)))
    return _finish(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("validate-a", "size"))
    parser.add_argument("--input", required=True, help="JSON file, or - for stdin")
    args = parser.parse_args()
    try:
        if args.input == "-":
            request = json.load(sys.stdin, object_pairs_hook=_unique_json_object)
        else:
            with open(args.input, encoding="utf-8") as handle:
                request = json.load(handle, object_pairs_hook=_unique_json_object)
        output = validate_a_plan(request) if args.operation == "validate-a" else size_position(request)
    except DuplicateJSONKey:
        output = _result()
        output["issues"].append("duplicate_json_key")
        _finish(output)
    except (OSError, ValueError) as exc:
        output = _result()
        output["issues"].append(f"invalid_input:{type(exc).__name__}")
        _finish(output)
    print(json.dumps(output, ensure_ascii=False, allow_nan=False, indent=2))
    return 0 if output["status"] == "valid" else 2


if __name__ == "__main__":
    raise SystemExit(main())
