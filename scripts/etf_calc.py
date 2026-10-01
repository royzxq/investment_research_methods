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


def drawdown_states(month_end_closes, window=36):
    """State variable of the validated drawdown ladder (prereg R2): each month-end close over the highest
    of the last `window` month-end closes, itself included. 1.0 = at the high; lower = deeper drawdown."""
    closes = [_number(close, positive=True) for close in month_end_closes]
    if None in closes:
        raise ValueError("month_end_closes_must_be_positive_numbers")
    return [close / max(closes[max(0, t - window + 1):t + 1]) for t, close in enumerate(closes)]


def level_at_drawdown_state(rolling_high, state):
    """Index level at which close / rolling_high equals `state` (a quantile of the state's own history, in (0, 1])."""
    rolling_high, state = _number(rolling_high, positive=True), _number(state, positive=True)
    if rolling_high is None or state is None:
        return None
    if state > 1:
        raise ValueError("state_is_close_over_rolling_high_and_cannot_exceed_1")
    return rolling_high * state


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


def _amount(value, label):
    amount = _number(value)
    if amount is None or amount < 0:
        raise ValueError(f"amount_must_be_non_negative:{label}")
    return amount


def dca_gap_allocation(target_weights_pct, holdings, cash, new_money, *, reserved_cash_pct=0.0, paused=()):
    """Monthly new money by effective gaps (framework v1.0 B3).

    target_weights_pct {slot: % of the strategy account}; holdings {slot: market value}; cash: strategy cash before
    this month's inflow; new_money: this month's inflow. With T = sum(holdings) + cash + new_money,
    gap = max(target x T - holding, 0) for every slot not in `paused`. Money available for buying is
    cash + new_money - reserved_cash_pct x T (approved theme cash is kept first), floored at zero. Gaps that fit are
    filled in full, otherwise in proportion to the gaps; the rest stays as cash, nothing is bought beyond a target.
    shares_pct gives each buy as % of everything bought this time: the rule is a ratio, the amount only scales it.
    A held slot without a target is a gap in the inputs, not a zero target.
    """
    keys = ("total", "available", "gaps", "buys", "shares_pct", "cash_after", "unfilled")
    result = _result(**dict.fromkeys(keys))
    targets = {slot: _amount(weight, f"target:{slot}") for slot, weight in target_weights_pct.items()}
    values = {slot: _amount(value, f"holding:{slot}") for slot, value in holdings.items()}
    cash, new_money = _amount(cash, "cash"), _amount(new_money, "new_money")
    reserved_pct = _amount(reserved_cash_pct, "reserved_cash_pct")
    if sum(targets.values()) + reserved_pct > 100 + 1e-9:
        raise ValueError("targets_and_reserve_exceed_100")
    result["missing_fields"] = [f"target:{slot}" for slot in sorted(values) if slot not in targets]
    if result["missing_fields"]:
        return _finish(result, keys)
    total = sum(values.values()) + cash + new_money
    available = max(cash + new_money - reserved_pct * total / 100, 0.0)
    gaps = {slot: max(weight * total / 100 - values.get(slot, 0.0), 0.0)
            for slot, weight in targets.items() if slot not in paused}
    need = sum(gaps.values())
    scale = 1.0 if need <= available else available / need
    buys = {slot: gap * scale for slot, gap in gaps.items()}
    spent = sum(buys.values())
    result.update(total=total, available=available, gaps=gaps, buys=buys,
                  shares_pct={slot: 100 * amount / spent for slot, amount in buys.items()} if spent > 0 else {},
                  cash_after=cash + new_money - spent, unfilled=need - spent)
    return result


def rebalance_trades(target_weights_pct, holdings, cash, new_money, *, reserved_cash_pct=0.0, keep=(), paused=()):
    """Bring holdings back to their targets (framework v1.0 A9, and the first migration).

    Slots above target are sold down to target x T, except those in `keep` (e.g. a holding whose sale would need a
    cross-border transfer); the proceeds plus cash and new money then fill the other slots' gaps by the rule of
    dca_gap_allocation. T is unchanged by trades inside the account. A held slot without a target is a gap.
    """
    keys = ("total", "available", "gaps", "buys", "shares_pct", "cash_after", "unfilled", "sells")
    result = _result(**dict.fromkeys(keys))
    values = {slot: _amount(value, f"holding:{slot}") for slot, value in holdings.items()}
    result["missing_fields"] = [f"target:{slot}" for slot in sorted(values) if slot not in target_weights_pct]
    if result["missing_fields"]:
        return _finish(result, keys)
    total = sum(values.values()) + _amount(cash, "cash") + _amount(new_money, "new_money")
    sells = {slot: max(value - _amount(target_weights_pct[slot], f"target:{slot}") * total / 100, 0.0)
             for slot, value in values.items() if slot not in keep}
    sells = {slot: amount for slot, amount in sells.items() if amount > 0}
    after = {slot: value - sells.get(slot, 0.0) for slot, value in values.items()}
    result.update(dca_gap_allocation(target_weights_pct, after, cash + sum(sells.values()), new_money,
                                     reserved_cash_pct=reserved_cash_pct, paused=paused), sells=sells)
    return result


def theme_cash_reserve_pct(theme_module_pct, theme_stock_target_pct, theme_held_pct):
    """Approved theme cash to keep, in % of the account (framework v1.0 A2, A8).

    Theme stock plus theme cash make the theme module together, so the reserve is the module's cash target
    (module - theme stock targets) but never more than what tops the theme stock already held up to the module;
    themes held above the module leave nothing to reserve.
    """
    module = _amount(theme_module_pct, "theme_module_pct")
    stock_target = _amount(theme_stock_target_pct, "theme_stock_target_pct")
    held = _amount(theme_held_pct, "theme_held_pct")
    if stock_target > module + 1e-9:
        raise ValueError("theme_stock_target_exceeds_module")
    return max(0.0, min(module - stock_target, module - held))


def drift_threshold_pp(target_weight_pct, relative_pct=25, cap_pp=5):
    """Review threshold for a sub-item's drift: min(target x relative%, cap), in percentage points."""
    target = _amount(target_weight_pct, "target_weight_pct")
    return min(target * _amount(relative_pct, "relative_pct") / 100, _amount(cap_pp, "cap_pp"))


def allocation_check(values, module_of, module_bands_pct, *, drift_targets_pct=None, drift_relative_pct=25,
                     drift_cap_pp=5, ceilings_pct=None):
    """Quarterly band check (framework v1.0 B4): module weights against their bands, drift of named sub-items
    against min(target x relative%, cap), and items above a review ceiling (e.g. a single theme above 15%).

    values {slot: amount, cash slots included}; module_of {slot: module}; module_bands_pct {module: (low, high)}.
    Flags call for a review, not automatically for a trade.
    """
    keys = ("total", "weights_pct", "module_weights_pct", "modules_out_of_band", "drifted", "above_ceiling")
    result = _result(**dict.fromkeys(keys))
    amounts = {slot: _amount(value, f"value:{slot}") for slot, value in values.items()}
    result["missing_fields"] = [f"module:{slot}" for slot in sorted(amounts) if slot not in module_of]
    result["missing_fields"] += [f"band:{module}" for module in sorted(set(module_of.values()) - set(module_bands_pct))]
    total = sum(amounts.values())
    if total <= 0:
        result["missing_fields"].append("total")
    if result["missing_fields"]:
        return _finish(result, keys)
    weights = {slot: 100 * amount / total for slot, amount in amounts.items()}
    modules = {module: 0.0 for module in module_bands_pct}
    for slot, weight in weights.items():
        modules[module_of[slot]] += weight
    drifted = []
    for slot, target in (drift_targets_pct or {}).items():
        threshold = drift_threshold_pp(target, drift_relative_pct, drift_cap_pp)
        weight = weights.get(slot, 0.0)
        if abs(weight - target) > threshold + 1e-9:
            drifted.append(dict(slot=slot, weight_pct=weight, target_pct=target, threshold_pp=threshold))
    result.update(total=total, weights_pct=weights, module_weights_pct=modules,
                  modules_out_of_band=[module for module, weight in modules.items()
                                       if not module_bands_pct[module][0] - 1e-9 <= weight <= module_bands_pct[module][1] + 1e-9],
                  drifted=drifted,
                  above_ceiling=[dict(slot=slot, weight_pct=weights[slot], ceiling_pct=ceiling)
                                 for slot, ceiling in (ceilings_pct or {}).items() if weights.get(slot, 0.0) > ceiling + 1e-9])
    return result


def unit_nav(observations):
    """Unitized NAV of an account with external money flows, so deposits never count as gains (framework v1.0 B9).

    observations: (day, value_after_flow, external_flow) ascending; flow > 0 is money in, < 0 money out.
    The first value seeds the units at NAV 1. On each later day NAV = (value - flow) / units, then the flow buys
    (or redeems) units at that NAV.
    """
    rows = [(_day(day), _number(value), _number(flow) if flow is not None else 0.0) for day, value, flow in observations]
    if any(later[0] <= earlier[0] for earlier, later in zip(rows, rows[1:])):
        raise ValueError("observations_must_be_strictly_ascending_by_date")
    navs, units = [], None
    for day, value, flow in rows:
        if value is None or flow is None or value < 0:
            raise ValueError(f"value_and_flow_must_be_numbers:{day}")
        if units is None:
            if value <= 0:
                raise ValueError("first_value_must_be_positive")
            units, nav = value, 1.0
        else:
            if value - flow <= 0:
                raise ValueError(f"value_before_flow_must_be_positive:{day}")
            nav = (value - flow) / units
            units += flow / nav
        navs.append((day, nav))
    return navs


def drawdown_summary(levels):
    """Current and maximum drawdown of a level series, in % (0 at a high, negative below it)."""
    keys = ("current_drawdown_pct", "max_drawdown_pct")
    result = _result(**dict.fromkeys(keys))
    series = [_number(level, positive=True) for level in levels]
    if not series:
        result["missing_fields"].append("levels")
    elif None in series:
        result["missing_fields"].append("invalid_level")
    if result["missing_fields"]:
        return _finish(result, keys)
    peak, worst = series[0], 0.0
    for level in series:
        peak = max(peak, level)
        worst = min(worst, (level / peak - 1) * 100)
    result.update(current_drawdown_pct=(series[-1] / peak - 1) * 100, max_drawdown_pct=worst)
    return result
