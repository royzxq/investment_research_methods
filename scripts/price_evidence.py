"""Pure offline price evidence: explicit quote basis and same-pair changes.

No API, credentials, pandas or market-data dependencies. Missing values remain
None; no price fallback is permitted in the settlement-only oil guard.
"""

from bisect import bisect_left
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import math


def _number(value, *, positive=False):
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(result) or (positive and result <= 0):
        return None
    return result


def _date(value):
    if not isinstance(value, str) or len(value) != 8:
        raise ValueError("trade_date_must_be_YYYYMMDD")
    datetime.strptime(value, "%Y%m%d")
    return value


def validate_unique_trade_dates(dates):
    """Reject malformed or duplicate dates instead of silently deduplicating."""
    checked = [_date(day) for day in dates]
    if len(checked) != len(set(checked)):
        raise ValueError("duplicate_trade_date")
    return checked


def calendar_window(trading_dates, anchor, win=20):
    """A fixed +/-win trading-calendar window, independent of quote gaps.

    Match the previous searchsorted convention: use the first trading date
    on or after the target anchor. Do not shorten a window at calendar edges.
    """
    _date(anchor)
    if type(win) is not int or win < 0:
        raise ValueError("window_must_be_nonnegative_integer")
    calendar = sorted(validate_unique_trade_dates(trading_dates))
    pos = bisect_left(calendar, anchor)
    if pos < win or pos + win >= len(calendar):
        raise ValueError("trading_calendar_does_not_cover_fixed_window")
    dates = calendar[pos - win:pos + win + 1]
    return dict(target_anchor=anchor, trading_anchor=calendar[pos],
                window_start=dates[0], window_end=dates[-1], trading_dates=dates)


def sample_coverage(counts, expected_per_year=41, expected_years=3):
    """Fixed 80%-per-year governance check, not proof of statistical validity.

    Counts are valid unique same-pair sessions for each fixed historical year.
    Use None for missing/invalid-date years. Partial years are not pooled to
    rescue an under-covered year; the caller keeps actual observations only.
    """
    if (type(expected_per_year) is not int or expected_per_year < 1 or
            type(expected_years) is not int or expected_years < 1):
        raise ValueError("expected_sample_shape_must_be_positive_integers")
    minimum = (4 * expected_per_year + 4) // 5
    result = dict(status="complete", expected_per_year=expected_per_year,
                  expected_years=expected_years, minimum_per_year=minimum,
                  actual_counts=counts, years=[], warnings=[], missing_fields=[])
    if not isinstance(counts, (list, tuple)):
        result["missing_fields"].append("sample_counts_must_be_sequence")
    else:
        if len(counts) != expected_years:
            result["missing_fields"].append(f"historical_year_count:{len(counts)}/{expected_years}")
        for index, count in enumerate(counts, 1):
            state = "complete"
            if type(count) is not int or count < 0 or count > expected_per_year:
                result["missing_fields"].append(f"year_{index}:invalid_or_unknown_count")
                state = "incomplete"
            elif count < minimum:
                result["missing_fields"].append(f"year_{index}:below_minimum:{count}/{minimum}")
                state = "incomplete"
            elif count < expected_per_year:
                result["warnings"].append(f"year_{index}:partial_window:{count}/{expected_per_year}")
            result["years"].append(dict(year_index=index, count=count, status=state))
    if result["missing_fields"]:
        result["status"] = "incomplete"
    return result


def select_price(settle, close):
    """Select the reference price and disclose its basis, never infer settle."""
    for value, basis in ((settle, "settle"), (close, "close")):
        price = _number(value, positive=True)
        if price is not None:
            return price, basis
    return None, "unknown"


def completed_day_cutoff(now=None):
    """Conservative daily-data cutoff in China time, not a publication claim.

    Without a provider completion flag, today's bars are excluded before
    18:00 China time; future dates are always excluded. Weekends/holidays are
    resolved by selecting an actual available trading-date row afterwards.
    """
    china = timezone(timedelta(hours=8))
    current = now if now is not None else datetime.now(china)
    if current.tzinfo is None:
        raise ValueError("now_requires_timezone")
    current = current.astimezone(china)
    day = current.date() - timedelta(days=1 if current.hour < 18 else 0)
    return day.strftime("%Y%m%d")


def weekly_price_evidence(records, as_of):
    """Compare the latest completed market day to seven calendar days earlier.

    AS_OF limits information availability; it is not the weekly return anchor.
    The caller must supply completed daily bars (the API script applies a
    conservative current-day cutoff). Explicit is_complete=False rows are
    excluded. A missing endpoint settlement is never replaced by an older
    valid settlement to make the oil guard calculable.
    """
    boundary = _date(as_of)
    indexed = {}
    for record in records:
        day = _date(record["trade_date"])
        if day in indexed:
            raise ValueError("duplicate_trade_date")
        indexed[day] = record
    days = sorted(day for day in indexed if day <= boundary and indexed[day].get("is_complete") is not False)
    end_day = days[-1] if days else None
    anchor = ((datetime.strptime(end_day, "%Y%m%d") - timedelta(days=7)).strftime("%Y%m%d")
              if end_day is not None else None)
    previous = [day for day in days if anchor is not None and day <= anchor]
    result = dict(anchor_date=anchor, market_trade_date=end_day, start_date=None, end_date=None,
                  start_price=None, end_price=None,
                  start_basis="unknown", end_basis="unknown",
                  start_settle=None, end_settle=None,
                  reference_change_pct=None, settlement_change_pct=None,
                  settlement_status="unknown")
    for endpoint, day in (("start", previous[-1] if previous else None),
                          ("end", end_day)):
        if day is None:
            continue
        row = indexed[day]
        px, basis = select_price(row.get("settle"), row.get("close"))
        result.update({f"{endpoint}_date": day, f"{endpoint}_price": px,
                       f"{endpoint}_basis": basis,
                       f"{endpoint}_settle": _number(row.get("settle"), positive=True)})
    has_current_week = result["end_date"] is not None and anchor is not None and result["end_date"] > anchor
    if has_current_week and all(result[k] is not None for k in ("start_price", "end_price")):
        result["reference_change_pct"] = float(
            (Decimal(str(result["end_price"])) / Decimal(str(result["start_price"])) - 1) * 100)
    if has_current_week and all(result[k] is not None for k in ("start_settle", "end_settle")):
        result["settlement_change_pct"] = float(
            (Decimal(str(result["end_settle"])) / Decimal(str(result["start_settle"])) - 1) * 100)
        result["settlement_status"] = "available"
    return result


def spread_change_series(records, near_contract, far_contract, trading_dates, periods=(1, 5, 10)):
    """Return changes in absolute spread units on the supplied trading calendar.

    All rows must identify this exact pair. Every expected session in a window
    must be present with finite spreads and a consistent known price basis for
    each leg. Missing sessions, shorter history, changed basis or an unavailable
    calendar yield None, never a change across roll dates or compressed gaps.
    Calendar dates are trading-day labels, not natural-day timestamps.
    """
    if not near_contract or not far_contract or near_contract == far_contract:
        raise ValueError("invalid_contract_pair")
    if any(type(n) is not int or n < 1 for n in periods):
        raise ValueError("periods_must_be_positive_integers")
    calendar = sorted({_date(day) for day in trading_dates})
    positions = {day: i for i, day in enumerate(calendar)}
    indexed = {}
    for record in records:
        day = _date(record["trade_date"])
        if day in indexed:
            raise ValueError("duplicate_trade_date")
        if (record.get("near_contract"), record.get("far_contract")) != (near_contract, far_contract):
            raise ValueError("mixed_or_unidentified_contract_pair")
        indexed[day] = record
    output = []
    for day in sorted(indexed):
        result = {"trade_date": day}
        for n in periods:
            key = f"spread_change_{n}td"
            result.update({key: None, f"{key}_from": None, f"{key}_status": "insufficient_history"})
            pos = positions.get(day)
            if pos is None:
                result[f"{key}_status"] = "calendar_unavailable"
                continue
            if pos < n:
                continue
            window = calendar[pos - n:pos + 1]
            result[f"{key}_from"] = window[0]
            if any(d not in indexed for d in window):
                result[f"{key}_status"] = "missing_pair_sessions"
                continue
            values = [_number(indexed[d].get("spread")) for d in window]
            if any(value is None for value in values):
                result[f"{key}_status"] = "invalid_spread"
                continue
            bases = {(indexed[d].get("price_basis_n"), indexed[d].get("price_basis_f")) for d in window}
            if len(bases) != 1 or any(b not in ("settle", "close") for pair in bases for b in pair):
                result[f"{key}_status"] = "price_basis_changed_or_unknown"
                continue
            result.update({key: values[-1] - values[0], f"{key}_status": "available"})
        output.append(result)
    return output
