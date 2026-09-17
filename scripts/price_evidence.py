"""Pure offline price evidence: explicit quote basis and same-pair changes.

No API, credentials, pandas or market-data dependencies. Missing values remain
None; no price fallback is permitted in the settlement-only oil guard. The D8
weekly rank and shadow-plan settlement below follow the same rule.
"""

from bisect import bisect_left, bisect_right
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import math
import re


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
                  settlement_status="unknown", settlement_missing_fields=[])
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
    for endpoint in ("start", "end"):
        if result[f"{endpoint}_date"] is None:
            result["settlement_missing_fields"].append(f"{endpoint}_trade_date")
        elif result[f"{endpoint}_settle"] is None:
            result["settlement_missing_fields"].append(f"{endpoint}_settle")
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


def week_start_day(calendar, end_day):
    """Latest session on or before end_day minus seven calendar days (oil-guard week)."""
    limit = (datetime.strptime(_date(end_day), "%Y%m%d") - timedelta(days=7)).strftime("%Y%m%d")
    pos = bisect_right(calendar, limit)
    return calendar[pos - 1] if pos else None


def weekly_anchor_days(trading_dates, end_day, years=3):
    """Last session of each ISO week after end_day minus `years`, excluding end_day's week.

    The calendar must reach a week before that start: a truncated calendar would
    otherwise shrink the expected sample silently instead of failing.
    """
    end = _date(end_day)
    calendar = sorted(validate_unique_trade_dates(trading_dates))
    month_day = end[4:]
    lower = f"{int(end[:4]) - years:04d}{'0228' if month_day == '0229' else month_day}"
    earliest = (datetime.strptime(lower, "%Y%m%d") - timedelta(days=7)).strftime("%Y%m%d")
    if not calendar or end not in calendar or calendar[0] > earliest:
        raise ValueError("trading_calendar_does_not_cover_d8_lookback")
    current_week = datetime.strptime(end, "%Y%m%d").isocalendar()[:2]
    last_session = {}
    for day in calendar:
        if lower < day < end:
            last_session[datetime.strptime(day, "%Y%m%d").isocalendar()[:2]] = day
    return sorted(day for week, day in last_session.items() if week != current_week)


def d8_weekly_rank(trading_dates, end_day, main_by_day, settles_by_contract, years=3):
    """Rank the latest main-contract weekly settle change against its weekly history.

    Every sample, the current one included, uses the contract mapped as main on its
    end day for both endpoints, so a roll never counts as a move. A missing mapping
    or settle voids that sample rather than borrowing close or another month. Ranks
    stay None when valid samples fall below 80% of the expected weeks.
    """
    end = _date(end_day)
    anchors = weekly_anchor_days(trading_dates, end, years)
    calendar = sorted(validate_unique_trade_dates(trading_dates))

    def change(day):
        start = week_start_day(calendar, day)
        contract = main_by_day.get(day)
        settles = settles_by_contract.get(contract) or {}
        first = _number(settles.get(start), positive=True)
        last = _number(settles.get(day), positive=True)
        if contract is None or start is None or first is None or last is None:
            return None, contract, start
        return float((Decimal(str(last)) / Decimal(str(first)) - 1) * 100), contract, start

    samples, invalid = [], []
    for anchor in anchors:
        value = change(anchor)[0]
        if value is None:
            invalid.append(anchor)
        else:
            samples.append(value)
    current, contract, start = change(end)
    required = (4 * len(anchors) + 4) // 5
    result = dict(start_date=start, end_date=end, main_contract=contract, current_change_pct=current,
                  sample_count=len(samples), expected_samples=len(anchors), required_samples=required,
                  invalid_anchor_dates=invalid, up_rank=None, down_rank=None, status="available")
    if current is None:
        result["status"] = "current_unavailable"
    elif not samples or len(samples) < required:
        result["status"] = "insufficient_samples"
    else:
        result["up_rank"] = 100 * sum(value < current for value in samples) / len(samples)
        result["down_rank"] = 100 * sum(value > current for value in samples) / len(samples)
    return result


SHADOW_SIDES = {"long": 1, "short": -1}
_ISO_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")


def _plan_number(plan, key, *, positive, nonnegative=False):
    value = plan.get(key)
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
            or (positive and value <= 0) or (nonnegative and value < 0)):
        qualifier = "positive " if positive else ("nonnegative " if nonnegative else "")
        raise ValueError(f"{key}: expected finite {qualifier}number")
    return Decimal(str(value))


def parse_shadow_plan(plan):
    """Validate one shadow plan and return (parsed, errors); the audit validator and the settler share it.

    Errors are `field: message` strings. Levels come back as Decimal, dates as YYYYMMDD strings and the
    registration day is the Asia/Shanghai date. The latest exit must fall strictly after registration,
    otherwise no session could ever be settled.
    """
    if not isinstance(plan, dict):
        return None, ["plan: expected object"]
    china = timezone(timedelta(hours=8))
    errors, parsed = [], {}
    for key in ("shadow_id", "candidate_id"):
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            errors.append(f"{key}: expected nonempty ID string")
    side = SHADOW_SIDES.get(plan.get("side"))
    if side is None:
        errors.append("side: expected long or short")
    instrument = plan.get("instrument")
    kind = instrument.get("type") if isinstance(instrument, dict) else None
    settle_only = None
    if kind not in ("single", "spread"):
        errors.append("instrument.type: expected single or spread")
    else:
        settle_only = kind == "spread"
        contracts, wanted = instrument.get("contracts"), 2 if settle_only else 1
        if (not isinstance(contracts, list) or len(contracts) != wanted or len(set(contracts)) != wanted
                or not all(isinstance(c, str) and c.strip() for c in contracts)):
            errors.append(f"instrument.contracts: {kind} requires {wanted} distinct contracts")
        else:
            parsed["contracts"] = list(contracts)
    if plan.get("entry_type") not in ("limit", "stop"):
        errors.append("entry_type: expected limit or stop")
    levels = {}
    for key, kwargs in (("entry", dict(positive=settle_only is False)), ("stop", dict(positive=settle_only is False)),
                        ("target", dict(positive=settle_only is False)), ("multiplier", dict(positive=True)),
                        ("round_trip_cost", dict(positive=False, nonnegative=True))):
        try:
            levels[key] = _plan_number(plan, key, **kwargs)
        except ValueError as exc:
            errors.append(str(exc))
    if side is not None and all(key in levels for key in ("entry", "stop", "target")):
        if not side * levels["stop"] < side * levels["entry"] < side * levels["target"]:
            errors.append(f"levels: {plan['side']} requires stop and target on opposite sides of entry")
    registered = None
    try:
        registered = datetime.fromisoformat(str(plan.get("registered_at")).replace("Z", "+00:00"))
        if registered.tzinfo is None:
            raise ValueError("naive")
    except ValueError:
        registered = None
        errors.append("registered_at: expected timezone-qualified timestamp")
    days = {}
    for key in ("entry_expiry", "latest_exit_date"):
        value = plan.get(key)
        try:
            if not isinstance(value, str) or not _ISO_DAY.fullmatch(value):
                raise ValueError("format")
            days[key] = date.fromisoformat(value).strftime("%Y%m%d")
        except ValueError:
            errors.append(f"{key}: expected ISO date YYYY-MM-DD")
    if registered is not None and len(days) == 2:
        registered_day = registered.astimezone(china).strftime("%Y%m%d")
        if days["entry_expiry"] < registered_day:
            errors.append("entry_expiry: cannot precede registration day (Asia/Shanghai)")
        if days["latest_exit_date"] <= registered_day:
            errors.append("latest_exit_date: must fall after registration day (Asia/Shanghai)")
        if days["latest_exit_date"] < days["entry_expiry"]:
            errors.append("latest_exit_date: cannot precede entry_expiry")
        parsed.update(registered=registered, registered_day=registered_day,
                      expiry=days["entry_expiry"], latest_exit=days["latest_exit_date"])
    if errors:
        return None, errors
    parsed.update(side=side, settle_only=settle_only, entry_type=plan["entry_type"],
                  entry=levels["entry"], stop=levels["stop"], target=levels["target"],
                  multiplier=levels["multiplier"], cost=levels["round_trip_cost"])
    return parsed, []


def settle_shadow_plan(plan, bars, last_trading_day=None):
    """Settle one pre-registered shadow plan on sessions opened after its registration.

    A daily bar starts with the previous session's 21:00 night trading, so a bar counts
    only when the plan was registered before that evening. Conservative rules: a limit
    entry fills at its price and a stop entry at the worse of its price and the open; a
    fill that already lies beyond the target exits at once at the fill price (the target
    order would execute immediately, so the plan only pays its cost); on the fill session a
    stop touch exits (at the stop, or at settlement for spreads) while the target is
    ignored, because intraday order is unknown; afterwards a gap through the stop exits at
    the open and a session touching both levels exits at the stop. Settle-only bars
    (spreads) trigger on settlement, fill and stop out at the worse of level and
    settlement, and take profit at the target. An unfilled plan lapses after entry_expiry;
    a filled one exits on settlement of the last session not after latest_exit_date or the
    contract's last trading day, whichever is earlier. A missing price stops evaluation
    instead of being inferred. Plan validation is shared with the audit validator
    (parse_shadow_plan); a plan that fails it is reported as invalid.
    """
    result = dict(shadow_id=plan.get("shadow_id") if isinstance(plan, dict) else None,
                  status="invalid", fill_date=None, fill_price=None, exit_date=None, exit_price=None,
                  exit_reason=None, pnl_cny=None, r_multiple=None, unrealized_pnl_cny=None,
                  last_date=None, error=None)
    parsed, errors = parse_shadow_plan(plan)
    if errors:
        result["error"] = "; ".join(errors)
        return result
    side, settle_only = parsed["side"], parsed["settle_only"]
    entry, stop, target, multiplier, cost = (parsed[key] for key in ("entry", "stop", "target", "multiplier", "cost"))
    registered, registered_day, expiry, latest_exit = (parsed[key] for key in ("registered", "registered_day", "expiry", "latest_exit"))
    china = timezone(timedelta(hours=8))
    try:
        exit_day = latest_exit if last_trading_day is None else min(latest_exit, _date(last_trading_day))
        if exit_day <= registered_day:
            raise ValueError("contract_ends_before_registration")
        ordered = sorted(bars, key=lambda bar: _date(bar["trade_date"]))
        validate_unique_trade_dates([bar["trade_date"] for bar in ordered])
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result
    sessions = [bar for previous, bar in zip(ordered, ordered[1:])
                if registered < datetime.strptime(previous["trade_date"] + "21", "%Y%m%d%H").replace(tzinfo=china)]

    risk = abs(entry - stop) * multiplier + cost
    within = [bar for bar in sessions if bar["trade_date"] <= exit_day]
    exit_reached = any(bar["trade_date"] >= exit_day for bar in sessions)
    worse = max if side > 0 else min
    fill = settle = None

    def finish(day, price, reason):
        pnl = side * (price - fill) * multiplier - cost
        result.update(status="closed", exit_date=day, exit_price=float(price), exit_reason=reason,
                      pnl_cny=float(pnl), r_multiple=float(pnl / risk))
        return result

    for index, bar in enumerate(within):
        day = bar["trade_date"]
        if fill is None and day > expiry:
            break
        prices = {}
        for key in ("settle",) if settle_only else ("open", "high", "low", "settle"):
            value = _number(bar.get(key), positive=not settle_only)
            if value is None:
                result.update(status="data_gap", last_date=day, error=f"missing_{key}:{day}")
                return result
            prices[key] = Decimal(str(value))
        result["last_date"] = day
        settle = prices["settle"]
        # Extremes relative to the planned position: a long is hurt by the low.
        adverse = settle if settle_only else prices["low" if side > 0 else "high"]
        favorable = settle if settle_only else prices["high" if side > 0 else "low"]
        if fill is None:
            if plan["entry_type"] == "limit":
                touched = side * (adverse - entry) <= 0
                price = worse(entry, settle) if settle_only else entry
            else:
                touched = side * (favorable - entry) >= 0
                price = worse(entry, settle if settle_only else prices["open"])
            if not touched:
                continue
            fill = price
            result.update(fill_date=day, fill_price=float(fill))
            if side * (adverse - stop) <= 0:
                return finish(day, settle if settle_only else stop, "stop")
            if side * (fill - target) >= 0:   # gapped beyond the target: the target order executes at once
                return finish(day, fill, "target")
        elif settle_only:
            if side * (settle - stop) <= 0:
                return finish(day, settle, "stop")
            if side * (settle - target) >= 0:
                return finish(day, target, "target")
        else:
            if side * (prices["open"] - stop) <= 0:
                return finish(day, prices["open"], "stop")
            if side * (adverse - stop) <= 0:
                return finish(day, stop, "stop")
            if side * (favorable - target) >= 0:
                return finish(day, target, "target")
        if index == len(within) - 1 and exit_reached:
            return finish(day, settle, "time")
    if fill is None:
        deadline = min(expiry, exit_day)
        result["status"] = ("not_filled" if any(bar["trade_date"] >= deadline for bar in sessions)
                            else "pending_entry")
        return result
    result.update(status="open", unrealized_pnl_cny=float(side * (settle - fill) * multiplier - cost))
    return result
