#!/usr/bin/env python3
"""Reproduce conditional T price paths under the adopted 10-day stop rule."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys


def iso(day):
    return f"{day[:4]}-{day[4:6]}-{day[6:]}"


def compact(day):
    return day.replace("-", "")


def read_audit(path):
    text = path.read_text(encoding="utf-8")
    return json.loads(re.search(r"```json\n(.*?)\n```", text, re.S).group(1))


def price_book(trend_row):
    book = trend_row["market_inputs"]
    dates = book["trading_dates"]
    assert len(set(dates)) == len(dates) and sorted(dates) == dates
    rows = {row["trade_date"]: row for row in book["records"]}
    assert len(rows) == len(book["records"])
    assert book["identity_basis"] == "fut_daily_response_ts_code"
    assert all(row["ts_code"] == row["response_ts_code"] == book["ts_code"]
               for row in rows.values())
    return book, dates, rows


def trace(dates, rows, start, end, side, entry, initial_stop, stop_helper):
    start_idx = dates.index(start)
    trial_stop = initial_stop
    day20 = dates[start_idx + 19]
    path = []
    first_full_day_touch = None
    for idx, day in enumerate(dates[start_idx:], start_idx):
        if day > min(end, day20):
            break
        window = [rows[key] for key in dates[idx - 9:idx + 1]]
        row = window[-1]
        high10 = max(item["high"] for item in window)
        low10 = min(item["low"] for item in window)
        next_stop = stop_helper(side, initial_stop, trial_stop, low10, high10)
        price_touched = (row["high"] >= trial_stop if side == "short"
                         else row["low"] <= trial_stop)
        closed_by_time_limit = day == day20
        next_applies = not closed_by_time_limit and not price_touched
        if price_touched and day != start:
            first_full_day_touch = day
        path.append({
            "trade_date": iso(day),
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "reference_stop_in_force": trial_stop,
            "stop_relation": ("entry_session_sequence_unknown" if price_touched and day == start
                              else "full_day_touch" if price_touched else "no_touch"),
            "completed_10_days": [iso(item["trade_date"]) for item in window],
            "high10": high10,
            "low10": low10,
            "next_session_reference_stop_at_close": next_stop if next_applies else None,
        })
        if first_full_day_touch or closed_by_time_limit:
            break
        trial_stop = next_stop
    return {
        "entry": entry,
        "initial_stop": initial_stop,
        "natural_20_day_limit": iso(day20),
        "first_post_entry_day_price_touch": iso(first_full_day_touch) if first_full_day_touch else None,
        "entry_day_stop_ordering_unknown": path[0]["stop_relation"] == "entry_session_sequence_unknown",
        "next_session_reference_stop_from_last_row": path[-1]["next_session_reference_stop_at_close"],
        "days": path,
    }


def audit_plan(candidate, trend_row, stop_helper):
    book, dates, rows = price_book(trend_row)
    plan = candidate["plan"]
    side = candidate["direction"]
    end = trend_row["market_trade_date"]
    alt_entry = plan.get("alternate_entry", {}).get("entry_date")
    scenario_dates = [plan.get("entry_date"), alt_entry]
    diagnostic_only = plan["entry"] is None
    if diagnostic_only:
        # Historical observation recorded in the adopted 11/08 audit only.
        scenario_dates = ["2026-10-16", "2026-10-19"]
    scenarios = []
    for entry_day in scenario_dates:
        start = compact(entry_day)
        row = rows[start]
        anchor_entry = 3310 if diagnostic_only else plan["entry"]
        anchor_stop = 3410 if diagnostic_only else plan["stop"]
        ref = trace(dates, rows, start, end, side, anchor_entry, anchor_stop, stop_helper)
        possible_price_envelope = row["low"] <= anchor_entry <= row["high"]
        details = {
            "research_only_diagnostic": diagnostic_only,
            "scenario_entry_date": entry_day,
            "daily_ohlc_high_low": [row["high"], row["low"]],
            "reference_entry_in_daily_high_low": possible_price_envelope,
            "historical_reference_trace": ref,
        }
        if plan["entry_range"] is not None:
            lo, hi = plan["entry_range"]
            eligible = max(lo, int(row["low"])), min(hi, int(row["high"]))
            traces = []
            for entry in range(eligible[0], eligible[1] + 1):
                entry_stop = anchor_stop + entry - anchor_entry
                traces.append(trace(dates, rows, start, end, side, entry, entry_stop, stop_helper))
            details.update({
                "original_plan_quote_range": [lo, hi],
                "range_overlap_with_daily_high_low": list(eligible) if traces else None,
                "initial_stop_range_for_overlap": [traces[0]["initial_stop"], traces[-1]["initial_stop"]] if traces else None,
                "entry_day_ordering_unknown_count": sum(t["entry_day_stop_ordering_unknown"] for t in traces),
                "first_post_entry_day_touch_counts": dict(Counter(
                    t["first_post_entry_day_price_touch"] or "no_touch_through_latest_evaluated_day"
                    for t in traces)),
                "next_session_reference_stop_counts": dict(Counter(
                    str(t["next_session_reference_stop_from_last_row"]) for t in traces)),
                "entry_range_boundary_traces": [traces[0], traces[-1]] if traces else [],
            })
        scenarios.append(details)
    return {
        "opportunity_id": candidate["opportunity_id"],
        "side": side,
        "original_registered_at": candidate["registered_at"],
        "original_signal_date": plan["signal_date"],
        "original_valid_until": plan["valid_until"],
        "fut_daily_response_ts_code": book["ts_code"],
        "fetched_at": book["fetched_at"],
        "market_trade_date": iso(end),
        "scenarios": scenarios,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "scripts"))
    from futures_strategy import trailing_stop

    market_path = root / ("research/futures/refresh/2026-11-22/evidence/"
                          "2026-11-22-signal-refresh-r2/market-inputs.json")
    audit_path = root / ("research/futures/weekly/2026-11-15/"
                         "2026-11-15-execution-audit.md")
    helper_path = root / "scripts/futures_strategy.py"
    market = json.loads(market_path.read_bytes())
    audit = read_audit(audit_path)
    trend = {row["contract"]: row for row in market["trend"]}
    cases = {"20261011-observe-MA2701-trend-long-v3": "MA2701",
             "20261015-observe-M2701-trend-short-v3": "M2701",
             "20261025-observe-RB2701-trend-short-v3": "RB2701"}
    results = [audit_plan(candidate, trend[cases[candidate["opportunity_id"]]], trailing_stop)
               for candidate in audit["candidates"] if candidate["opportunity_id"] in cases]
    assert len(results) == len(cases)
    data = {
        "as_of_date": "2026-11-22",
        "sources": [{"path": str(path.relative_to(root)), "sha256": sha256(path.read_bytes()).hexdigest()}
                    for path in (market_path, audit_path, helper_path)],
        "session_basis": "Tushare exact-contract daily high/low and the refresh input calendar; no intraday timestamp or temporary venue exception inferred",
        "method": "conditional daily path at original reference and every tick in the intersection of the original entry range and session high-low bounds. Anchored original 2ATR offset remains unchanged at every one-tick fill increment. Last-10 closed extrema checked via actual canonical helper at each close, applied prospectively only. Next-session stop omitted after a full-day price touch or the natural 20th day.",
        "limitations": "Daily high/low only bounds a possible fill, and cannot order same-day entry versus stop, prove an actual account fill, verify actual stop or economic exit, or make a valid prospective observation plan. 20-day dates are mechanical ceilings subject to earlier exits and actual venue constraints. A historical reference trace is labeled separately from the reachable entry range.",
        "actual_execution": None,
        "results": results,
    }
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
