"""Offline B-v2.24 calendar/price arithmetic; no fetching or trading permission.

Input: --input JSON, see framework Step5-B and tests/test_seasonal_plan.py.
Calendars must be complete exchange trading calendars, not weekday calendars.
The caller verifies source truth, contract life and all other execution gates.
"""
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
import json
from pathlib import Path
import re

WINDOWS = {"SR-summer": ("SR", "07-01", "09-30"),
           "CF-spring": ("CF", "03-01", "04-30"),
           "CF-autumn": ("CF", "09-01", "10-31")}


def number(value, name, *, positive=True):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name}: expected finite number")
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name}: expected finite number") from None
    if not n.is_finite() or (positive and n <= 0):
        raise ValueError(f"{name}: expected {'positive ' if positive else ''}finite number")
    return n


def calendar(values):
    days = [date.fromisoformat(v) for v in values]
    if not days or days != sorted(set(days)):
        raise ValueError("calendar: expected unique sorted exchange dates")
    return days


def boundaries(window_id, year, days):
    _, start, end = WINDOWS[window_id]
    lo, hi = date.fromisoformat(f"{year}-{start}"), date.fromisoformat(f"{year}-{end}")
    inside = [d for d in days if lo <= d <= hi]
    if not inside or days[0] >= lo or days[-1] <= hi:
        raise ValueError("calendar: must cover both window boundaries and adjacent dates")
    start_i, end_i = days.index(inside[0]), days.index(inside[-1])
    if start_i < 20 or end_i - 5 <= start_i:
        raise ValueError("calendar: insufficient pre-window or holding dates")
    return dict(window_start=inside[0], window_end=inside[-1],
                research_start=days[start_i - 20], planned_exit=days[end_i - 5])


def calculate(data):
    window_id = data["window_id"]
    product, _, _ = WINDOWS[window_id]
    as_of = date.fromisoformat(data["as_of_date"])
    days = calendar(data["trading_dates"])
    if as_of not in days:
        raise ValueError("as_of_date: expected a completed exchange trading date")
    bounds = boundaries(window_id, as_of.year, days)
    result = {"rule_version": "B-v2.24", "scope": "calendar_and_price_arithmetic_only",
              "execution_permission": "not_evaluated", "window_id": window_id,
              **{k: v.isoformat() for k, v in bounds.items()}}
    screening = bounds["research_start"] <= as_of <= bounds["window_end"]
    result["screening"] = "in_window_or_pre20" if screening else "not_triggered"
    if not screening:
        return result  # No downstream quotes, account or historical returns needed.
    if "plan" not in data:
        result["plan_result"] = "not_evaluated"
        return result
    p = data["plan"]
    entry_date = date.fromisoformat(p["entry_date"])
    contract = re.fullmatch(r"(SR|CF)(\d{2})(\d{2})", p["contract"])
    if not contract or contract[1] != product or not 1 <= int(contract[3]) <= 12:
        raise ValueError("contract: expected matching SR/CF YYMM")
    if (2000 + int(contract[2]), int(contract[3])) < (entry_date.year, entry_date.month):
        raise ValueError("contract: delivery month precedes planned entry")
    if entry_date <= as_of or entry_date not in days:
        raise ValueError("entry_date: must be a future trading date relative to completed as_of_date")
    forced_exit = date.fromisoformat(p["contract_latest_exit"])
    if forced_exit not in days:
        raise ValueError("contract_latest_exit: expected a calendar trading date")
    latest_exit = min(bounds["planned_exit"], forced_exit)
    result["latest_exit_date"] = latest_exit.isoformat()
    if not bounds["window_start"] <= entry_date < latest_exit:
        result["plan_result"] = "fails_time_window"
        return result
    tick = number(p["tick"], "tick")
    expected_tick = Decimal(1 if product == "SR" else 5)
    if tick != expected_tick:
        raise ValueError("tick: differs from current SR/CF contract specification")
    atr = number(p["atr20"], "atr20")
    entry_raw = max(number(p["ma20"], "ma20"), number(p["pre_window_low5"], "pre_window_low5") + atr)
    entry = (entry_raw / tick).to_integral_value(rounding=ROUND_CEILING) * tick
    stop = ((entry - Decimal("1.5") * atr) / tick).to_integral_value(rounding=ROUND_FLOOR) * tick
    if stop <= 0:
        raise ValueError("SL: expected positive price")
    history = p["history"]
    years = [h["year"] for h in history]
    expected_years = set(range(as_of.year - 3, as_of.year))
    if len(years) != 3 or any(type(y) is not int for y in years) or set(years) != expected_years:
        raise ValueError("history: require exactly the preceding three years, including losses")
    returns = []
    for h in history:
        year = h["year"]
        historical_days = calendar(h["trading_dates"])
        b = boundaries(window_id, year, historical_days)
        # Shift the actual contract's delivery year; do not splice main contracts.
        delivery_year = 2000 + int(contract[2]) - as_of.year + year
        expected_contract = f"{product}{delivery_year % 100:02d}{contract[3]}"
        if h["contract"] != expected_contract:
            raise ValueError("history.contract: maturity month/year offset mismatch")
        entry_anchor = entry_date.replace(year=year)
        exit_anchor = latest_exit.replace(year=year)
        eligible_entries = [d for d in historical_days if d >= entry_anchor]
        eligible_exits = [d for d in historical_days if d <= exit_anchor]
        if not eligible_entries or not eligible_exits:
            raise ValueError("history: missing mapped dates")
        e, x = eligible_entries[0], eligible_exits[-1]
        if not b["window_start"] <= e < x <= b["window_end"]:
            raise ValueError("history: mapped holding interval outside window or empty")
        if h["entry_date"] != e.isoformat() or h["exit_date"] != x.isoformat():
            raise ValueError("history: endpoint differs from mapped trading date")
        if not date.fromisoformat(h["listed_on"]) <= e < x <= date.fromisoformat(h["last_trade_date"]):
            raise ValueError("history: endpoints outside contract trading life")
        if h["price_basis"] != "settle" or not isinstance(h["source"], str) or not h["source"].strip():
            raise ValueError("history: settlement prices and source required")
        r = number(h["exit_settle"], "exit_settle") / number(h["entry_settle"], "entry_settle") - 1
        returns.append(r)
    mean = sum(returns) / 3
    target = ((entry * (1 + Decimal("0.7") * mean)) / tick).to_integral_value(rounding=ROUND_FLOOR) * tick
    result.update(entry=float(entry), stop=float(stop), tp1=float(target),
                  mean_return=float(mean), yearly_returns=[float(r) for r in returns],
                  plan_result="fails_nonpositive_target" if mean <= 0 or target <= entry else "prices_calculated",
                  pending_checks=["net_R_and_costs", "confirmation_and_industry", "applicable_gates",
                                  "gap_stress", "account_and_capacity"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        result = calculate(json.loads(Path(args.input).read_text()))
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "input_error", "error": str(exc), "execution_permission": "not_evaluated"}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
