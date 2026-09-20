"""Pure deterministic calculators for the ETF track.

No API, credentials, pandas or market-data dependencies. Every rate, weight
and percentile crosses this module's boundary in percent (5.97 = 5.97%,
percentile 0-100) and carries a ``_pct`` suffix or says so in its docstring.
Unknown inputs are never filled: multi-output functions return
status="incomplete" with missing_fields and None values, scalar functions
return None. Caller misuse (bad dates, unsorted series) raises ValueError.
"""

from datetime import date, datetime, timedelta
import math
import statistics

DAYS_PER_YEAR = 365.25
MIN_TRACKING_OBSERVATIONS = 120
FUND_BASES = ("adj_nav", "unit_nav")
INDEX_BASES = ("price", "total_return", "net_total_return")


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


def _day(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and len(value) == 8:
        return datetime.strptime(value, "%Y%m%d").date()
    raise ValueError("date_must_be_date_or_YYYYMMDD")


def _series(observations):
    """(day, value) pairs -> [(date, float|None)], strictly ascending by date."""
    series = [(_day(day), _number(value)) for day, value in observations]
    if any(later[0] <= earlier[0] for earlier, later in zip(series, series[1:])):
        raise ValueError("observations_must_be_strictly_ascending_by_date")
    return series


def _result(**values):
    return dict(status="complete", missing_fields=[], **values)


def _finish(result, value_keys):
    if result["missing_fields"]:
        result["status"] = "incomplete"
        for key in value_keys:
            result[key] = None
    return result


def _annualize(ratio, years):
    return (ratio ** (1 / years) - 1) * 100


def return_decomposition(start, end):
    """Split an annualized price return into earnings growth and valuation change.

    start/end are dict(date, level, pe). Implied EPS = level / PE, so
    (1 + price) = (1 + eps) * (1 + valuation): the parts compound, their plain
    sum differs from the price return by the cross term. Non-positive PE means
    implied EPS is undefined and is reported as a gap.
    """
    start_day, end_day = _day(start["date"]), _day(end["date"])
    if end_day <= start_day:
        raise ValueError("end_date_must_follow_start_date")
    years = (end_day - start_day).days / DAYS_PER_YEAR
    keys = ("price_annual_pct", "eps_annual_pct", "valuation_annual_pct")
    result = _result(start_date=start_day, end_date=end_day, years=years, **dict.fromkeys(keys))
    values = {}
    for label, point in (("start", start), ("end", end)):
        for field in ("level", "pe"):
            values[label, field] = _number(point.get(field), positive=True)
            if values[label, field] is None:
                result["missing_fields"].append(f"{label}_{field}")
    if years < 1:
        result["missing_fields"].append("window_shorter_than_one_year")
    if not result["missing_fields"]:
        level_ratio = values["end", "level"] / values["start", "level"]
        pe_ratio = values["end", "pe"] / values["start", "pe"]
        result.update(price_annual_pct=_annualize(level_ratio, years),
                      eps_annual_pct=_annualize(level_ratio / pe_ratio, years),
                      valuation_annual_pct=_annualize(pe_ratio, years))
    return _finish(result, keys)


def _history_sample(observations, min_years, window_years):
    """Valid history up to the latest observation, or its trailing window_years.

    No conclusion when the latest value is missing, history is shorter than
    min_years, or it does not cover the whole window.
    """
    series = _series(observations)
    result = _result(sample_n=None, current=None, first_date=None, last_date=None, window_years=window_years)
    valid = [(day, value) for day, value in series if value is not None]
    if not series or series[-1][1] is None:
        result["missing_fields"].append("current_value")
        return result, []
    last_day, current = valid[-1]
    first_day = valid[0][0]
    span = (last_day - first_day).days / DAYS_PER_YEAR
    if span < min_years:
        result["missing_fields"].append(f"history_shorter_than_min_years:{span:.2f}/{min_years}")
    sample = valid
    if window_years is not None:
        window_start = last_day - timedelta(days=window_years * DAYS_PER_YEAR)
        if first_day > window_start:
            result["missing_fields"].append(f"window_not_covered:{span:.2f}/{window_years}")
        sample = [(day, value) for day, value in valid if day > window_start]
    result.update(sample_n=len(sample), current=current, first_date=sample[0][0], last_date=last_day)
    return result, [value for _, value in sample]


def expanding_percentile(observations, *, min_years=5, window_years=None):
    """Percentile (0-100) of the latest value within its own history.

    Repo convention: share of the sample strictly below the current value,
    the current value included in the sample.
    """
    result, sample = _history_sample(observations, min_years, window_years)
    result["percentile"] = 100 * sum(value < result["current"] for value in sample) / len(sample) if sample else None
    return _finish(result, ("percentile",))


def history_quantiles(observations, points=(10, 25, 50, 75, 90), *, min_years=5, window_years=None):
    """Levels of the same history at the given percentile points (linear interpolation, inclusive)."""
    if any(type(point) is not int or not 0 < point < 100 for point in points):
        raise ValueError("points_must_be_integers_in_(0,100)")
    result, sample = _history_sample(observations, min_years, window_years)
    cuts = statistics.quantiles(sample, n=100, method="inclusive") if len(sample) > 1 else None
    result["levels"] = {point: cuts[point - 1] for point in points} if cuts else None
    if cuts is None and not result["missing_fields"]:
        result["missing_fields"].append("sample_n:1/2")
    return _finish(result, ("levels",))


def erp_spread(pe, bond_yield_pct):
    """Equity risk premium proxy in percentage points: 100/PE - bond yield (both %)."""
    pe, bond_yield_pct = _number(pe, positive=True), _number(bond_yield_pct)
    if pe is None or bond_yield_pct is None:
        return None
    return 100 / pe - bond_yield_pct


def scenario_annual_return(eps_growth_pct, dividend_yield_pct, current_multiple,
                           terminal_multiple, years, drag_pct):
    """Expected annual return % = EPS growth + dividend yield + valuation change - drag.

    Valuation change = (terminal / current) ** (1 / years) - 1. A base scenario
    passes terminal_multiple == current_multiple, i.e. zero valuation change.
    """
    keys = ("valuation_change_pct", "annual_return_pct")
    result = _result(**dict.fromkeys(keys))
    rates = dict(eps_growth_pct=_number(eps_growth_pct), dividend_yield_pct=_number(dividend_yield_pct),
                 drag_pct=_number(drag_pct))
    positives = dict(current_multiple=_number(current_multiple, positive=True),
                     terminal_multiple=_number(terminal_multiple, positive=True),
                     years=_number(years, positive=True))
    result["missing_fields"] = [name for name, value in {**rates, **positives}.items() if value is None]
    if not result["missing_fields"]:
        change = _annualize(positives["terminal_multiple"] / positives["current_multiple"], positives["years"])
        result.update(valuation_change_pct=change,
                      annual_return_pct=(rates["eps_growth_pct"] + rates["dividend_yield_pct"]
                                         + change - rates["drag_pct"]))
    return _finish(result, keys)


def aggregate_valuation(weights_pct, fundamentals, *, min_coverage_pct=90):
    """Index-level PE, PB and dividend yield from constituent weights and per-stock readings.

    weights_pct {code: % of index}; fundamentals {code: {"pe_ttm", "pb", "dv_ttm"}} (dv_ttm in %).
    PE and PB are weight-harmonic (index earnings over index price) across constituents whose
    multiple is positive; a constituent whose pe_ttm is missing or non-positive is a loss-maker
    (tushare reports no pe_ttm for them) and its weight is reported as loss_weight_pct, so the
    aggregate PE overstates earnings by exactly that omission; a missing or non-positive pb is
    treated the same way (book counted as zero). Constituents absent from
    fundamentals reduce coverage_pct; below min_coverage_pct nothing is concluded.
    """
    keys = ("pe_ttm", "pb", "dividend_yield_pct", "loss_weight_pct", "coverage_pct")
    result = _result(**dict.fromkeys(keys), total_weight_pct=0.0)
    covered = earnings = book = dividends = losses = 0.0
    for code, weight in weights_pct.items():
        weight = _number(weight)
        if weight is None or weight < 0:
            raise ValueError(f"invalid_weight:{code}")
        result["total_weight_pct"] += weight
        row = fundamentals.get(code)
        if row is None:
            continue
        covered += weight
        pe, pb, dividend = (_number(row.get(key)) for key in ("pe_ttm", "pb", "dv_ttm"))
        if pe is not None and pe > 0:
            earnings += weight / pe
        else:
            losses += weight
        if pb is not None and pb > 0:
            book += weight / pb
        dividends += weight * (dividend or 0.0)
    if result["total_weight_pct"] <= 0:
        result["missing_fields"].append("weights")
        return _finish(result, keys)
    result.update(coverage_pct=100 * covered / result["total_weight_pct"], loss_weight_pct=100 * losses / result["total_weight_pct"])
    if result["coverage_pct"] < min_coverage_pct:
        result["missing_fields"].append(f"coverage_pct:{result['coverage_pct']:.1f}/{min_coverage_pct}")
        return _finish(result, ("pe_ttm", "pb", "dividend_yield_pct"))
    result.update(pe_ttm=covered / earnings if earnings > 0 else None, pb=covered / book if book > 0 else None,
                  dividend_yield_pct=dividends / covered)
    return result


def level_at_multiple(current_level, current_multiple, target_multiple):
    """Index level at which the valuation multiple would equal target_multiple, earnings held constant."""
    values = [_number(value, positive=True) for value in (current_level, current_multiple, target_multiple)]
    if None in values:
        return None
    return values[0] * values[2] / values[1]


def _tracking_inputs(fund, index, fund_basis, index_basis, fund_currency, index_currency):
    """Shared basis checks and date alignment for tracking difference / error."""
    result = _result(fund_basis=fund_basis, index_basis=index_basis, currency=fund_currency,
                     window_start=None, window_end=None, observations=0, warnings=[])
    if fund_basis not in FUND_BASES:
        result["missing_fields"].append("fund_basis")
    if index_basis not in INDEX_BASES:
        result["missing_fields"].append("index_basis")
    if not fund_currency or not index_currency:
        result["missing_fields"].append("currency")
    elif fund_currency != index_currency:
        result["missing_fields"].append(f"currency_mismatch:{fund_currency}/{index_currency}")
    if fund_basis == "adj_nav" and index_basis == "price":
        result["warnings"].append("index_price_basis_excludes_dividends")
    if fund_basis == "unit_nav":
        result["warnings"].append("unit_nav_excludes_fund_distributions")
    index_levels = {day: value for day, value in _series(index) if value is not None and value > 0}
    pairs = [(day, value, index_levels[day]) for day, value in _series(fund)
             if value is not None and value > 0 and day in index_levels]
    if len(pairs) < MIN_TRACKING_OBSERVATIONS:
        result["missing_fields"].append(f"aligned_observations:{len(pairs)}/{MIN_TRACKING_OBSERVATIONS}")
    if pairs:
        result.update(window_start=pairs[0][0], window_end=pairs[-1][0], observations=len(pairs))
    return result, pairs


def tracking_difference(fund, index, *, fund_basis, index_basis, fund_currency, index_currency):
    """Fund return minus index return over their common dates, in % points.

    fund/index are (day, level) series. Annualized only when the common window
    is at least one year. Undeclared basis or currency, or differing
    currencies, is a gap: the two returns would not be comparable.
    """
    keys = ("period_td_pct", "annual_td_pct")
    result, pairs = _tracking_inputs(fund, index, fund_basis, index_basis, fund_currency, index_currency)
    result.update(dict.fromkeys(keys))
    if not result["missing_fields"]:
        fund_ratio, index_ratio = pairs[-1][1] / pairs[0][1], pairs[-1][2] / pairs[0][2]
        years = (pairs[-1][0] - pairs[0][0]).days / DAYS_PER_YEAR
        result["period_td_pct"] = (fund_ratio - index_ratio) * 100
        if years >= 1:
            result["annual_td_pct"] = _annualize(fund_ratio, years) - _annualize(index_ratio, years)
    return _finish(result, keys)


def tracking_error(fund, index, *, fund_basis, index_basis, fund_currency, index_currency,
                   periods_per_year=250):
    """Annualized standard deviation of periodic return differences, in %."""
    result, pairs = _tracking_inputs(fund, index, fund_basis, index_basis, fund_currency, index_currency)
    result["annual_te_pct"] = None
    if not result["missing_fields"]:
        gaps = [(later[1] / earlier[1]) - (later[2] / earlier[2]) for earlier, later in zip(pairs, pairs[1:])]
        result["annual_te_pct"] = statistics.stdev(gaps) * math.sqrt(periods_per_year) * 100
    return _finish(result, ("annual_te_pct",))


def premium_pct(price, nav):
    """Exchange price over closing NAV, in %. Same day, same currency is the caller's duty."""
    price, nav = _number(price, positive=True), _number(nav, positive=True)
    if price is None or nav is None:
        return None
    return (price / nav - 1) * 100


def lookthrough_weights(direct_pct, fund_pct, constituents_pct):
    """Portfolio weight per security = direct + sum(fund weight x constituent weight).

    direct_pct {security: % of portfolio}; fund_pct {fund: % of portfolio};
    constituents_pct {fund: {security: % of fund}}. Whatever a fund does not
    disclose (no constituents, or weights summing below 100) stays in
    unresolved_pct instead of being spread over the known names.
    """
    result = _result(weights_pct={}, unresolved_pct=0.0)
    weights = result["weights_pct"]
    for security, weight in direct_pct.items():
        weight = _number(weight)
        if weight is None or weight < 0:
            raise ValueError(f"invalid_direct_weight:{security}")
        weights[security] = weights.get(security, 0.0) + weight
    for fund, fund_weight in fund_pct.items():
        fund_weight = _number(fund_weight)
        if fund_weight is None or fund_weight < 0:
            raise ValueError(f"invalid_fund_weight:{fund}")
        constituents = constituents_pct.get(fund) or {}
        if not constituents:
            result["missing_fields"].append(f"constituents:{fund}")
        disclosed = 0.0
        for security, weight in constituents.items():
            weight = _number(weight)
            if weight is None or weight < 0:
                raise ValueError(f"invalid_constituent_weight:{fund}:{security}")
            disclosed += weight
            weights[security] = weights.get(security, 0.0) + fund_weight * weight / 100
        if disclosed > 100 + 1e-6:
            raise ValueError(f"constituent_weights_exceed_100:{fund}")
        result["unresolved_pct"] += fund_weight * (100 - disclosed) / 100
    if result["missing_fields"]:
        result["status"] = "incomplete"
    return result


def _drawdown_fraction(stress_drawdown_pct):
    drawdown = _number(stress_drawdown_pct)
    if drawdown is None:
        return None
    if not -100 <= drawdown < 0:
        raise ValueError("stress_drawdown_pct_must_be_in_[-100,0)")
    return -drawdown / 100


def loss_budget_cap(loss_budget, stress_drawdown_pct):
    """Largest position whose stress loss stays within the budget: budget / |drawdown|."""
    loss_budget, drawdown = _number(loss_budget, positive=True), _drawdown_fraction(stress_drawdown_pct)
    if loss_budget is None or drawdown is None:
        return None
    return loss_budget / drawdown


def joint_stress_loss(positions):
    """Loss (positive amount) if every (amount, stress_drawdown_pct) position hits its stress at once."""
    result = _result(loss=None)
    total = 0.0
    for position, (amount, stress_drawdown_pct) in enumerate(positions):
        amount, drawdown = _number(amount), _drawdown_fraction(stress_drawdown_pct)
        if amount is None or amount < 0:
            result["missing_fields"].append(f"position_{position}:amount")
        elif drawdown is None:
            result["missing_fields"].append(f"position_{position}:stress_drawdown_pct")
        else:
            total += amount * drawdown
    result["loss"] = total
    return _finish(result, ("loss",))


def month_end_levels(observations):
    """Last observation of each calendar month, ascending. The final month may be unfinished."""
    months = {}
    for day, value in _series(observations):
        months[day.year, day.month] = (day, value)
    return [months[key] for key in sorted(months)]


def sma_state(levels, window):
    """Latest level against its own simple moving average over the last `window` levels."""
    if type(window) is not int or window < 1:
        raise ValueError("window_must_be_positive_integer")
    keys = ("last", "sma", "distance_pct", "state")
    result = _result(window=window, **dict.fromkeys(keys))
    tail = [_number(level, positive=True) for level in levels[-window:]]
    if len(tail) < window:
        result["missing_fields"].append(f"levels:{len(tail)}/{window}")
    elif None in tail:
        result["missing_fields"].append("invalid_level_in_window")
    else:
        sma = sum(tail) / window
        distance = (tail[-1] / sma - 1) * 100
        result.update(last=tail[-1], sma=sma, distance_pct=distance,
                      state="above" if distance > 0 else "below" if distance < 0 else "at")
    return _finish(result, keys)
