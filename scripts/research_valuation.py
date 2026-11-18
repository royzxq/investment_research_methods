"""Recalculate explicit continuing-business FCFF DCF and conditional reverse DCF.

Amounts are in 100 million model-currency units, shares are actual whole shares,
and fx_to_quote converts model currency to quoted currency. Frozen audit-v4
uses tax rates/ROIC and year-end flows; audit-v5 explicitly selects cash taxes,
productive capital and a shared year-end offset. This module checks
arithmetic and disclosed inputs; it does not certify their economic plausibility.
Finite-life businesses and a loss-making terminal state need another model.
"""
from __future__ import annotations

from decimal import Context, Decimal, DecimalException, Underflow, localcontext

try:
    from .stock_price_map import fields, number, require, string
except ImportError:
    from stock_price_map import fields, number, require, string


SCENARIOS = ('low', 'base', 'high')
AMOUNT_SCALE = Decimal(100_000_000)
EQUITY_TOLERANCE = Decimal('.005')
PRICE_TOLERANCE = Decimal('.000001')
PARAMETER_TOLERANCE = Decimal('.0000000001')
_CALCULATION_CONTEXT = Context(prec=50)
_CALCULATION_CONTEXT.traps[Underflow] = True


class ReverseNoSolutionError(ValueError):
    """Valid reverse inputs have no identifiable admissible root in the bounds."""


def _fraction(value, label, *, margin=False):
    result = number(value, label)
    require((-1 if margin else 0) <= result <= 1, label + ': fraction outside allowed range')
    return result


def _nonnegative(value, label):
    result = number(value, label)
    require(result >= 0, label + ': must be nonnegative')
    return result


def _segment(segment, label, *, terminal_margin=None, input_bridges=False, year_end_offset=Decimal(0)):
    fields(segment, {'id', 'source', 'assumptions', 'discount_rate', 'years', 'terminal'}, label)
    ident = string(segment['id'], label + '.id')
    string(segment['source'], label + '.source')
    string(segment['assumptions'], label + '.assumptions')
    rate = number(segment['discount_rate'], label + '.discount_rate', positive=True)
    years = segment['years']
    require(isinstance(years, list) and bool(years), label + '.years: expected nonempty list')
    flows, explicit_pv = [], Decimal(0)
    for year, row in enumerate(years, 1):
        path = f'{label}.years[{year}]'
        fields(row, {'year', 'revenue', 'ebit_margin', 'da', 'capex', 'delta_nwc',
                     'cash_tax' if input_bridges else 'tax_rate'}, path)
        require(type(row['year']) is int and row['year'] == year,
                path + ': years must be continuous integers starting at 1')
        revenue = _nonnegative(row['revenue'], path + '.revenue')
        margin = _fraction(row['ebit_margin'], path + '.ebit_margin', margin=True)
        if input_bridges:
            cash_tax = _nonnegative(row['cash_tax'], path + '.cash_tax')
        else:
            tax = _fraction(row['tax_rate'], path + '.tax_rate')
            require(margin >= 0 or tax == 0, path + ': loss year tax must be zero; model usable losses in later tax years')
        da = _nonnegative(row['da'], path + '.da')
        capex = _nonnegative(row['capex'], path + '.capex')
        delta_nwc = number(row['delta_nwc'], path + '.delta_nwc')
        nopat = revenue * margin - cash_tax if input_bridges else revenue * margin * (1 - tax)
        fcff = nopat + da - capex - delta_nwc
        factor = (1 + rate) ** (year + year_end_offset)
        pv = fcff / factor
        explicit_pv += pv
        flows.append(dict(year=year, nopat=nopat, fcff=fcff,
                          discount_factor=factor, present_value=pv))
    terminal = segment['terminal']
    path = label + '.terminal'
    fields(terminal, {'growth', 'margin', 'tax_rate',
                      'invested_capital' if input_bridges else 'roic'}, path)
    growth = _nonnegative(terminal['growth'], path + '.growth')
    if input_bridges:
        capital = _nonnegative(terminal['invested_capital'], path + '.invested_capital')
    else:
        roic = number(terminal['roic'], path + '.ROIC', positive=True)
    require(rate > growth, label + ': discount_rate must exceed terminal growth')
    if not input_bridges:
        require(growth < roic, path + ': growth must be below ROIC')
    margin = _fraction(terminal['margin'], path + '.margin', margin=True)
    tax = _fraction(terminal['tax_rate'], path + '.tax_rate')
    require(revenue * margin * (1 - tax) > 0 or (margin == 0 and growth == 0),
            path + ': positive terminal NOPAT or explicit zero margin/growth required')
    # Only the solver may evaluate a zero-margin bound or negative total equity.
    if terminal_margin is not None:
        margin = terminal_margin
    terminal_nopat = revenue * (1 + growth) * margin * (1 - tax)
    reinvestment = capital * growth if input_bridges else terminal_nopat * growth / roic
    terminal_fcff = terminal_nopat - reinvestment
    if input_bridges and terminal_margin is None:
        require(terminal_fcff > 0 or (margin == 0 and growth == 0),
                path + ': sustainable positive terminal FCFF required')
    terminal_value = terminal_fcff / (rate - growth)
    terminal_pv = terminal_value / ((1 + rate) ** (len(years) + year_end_offset))
    return dict(id=ident, years=flows, explicit_pv=explicit_pv,
                terminal_nopat=terminal_nopat, terminal_reinvestment=reinvestment,
                terminal_fcff=terminal_fcff, terminal_value=terminal_value,
                terminal_pv=terminal_pv, enterprise_value=explicit_pv + terminal_pv)


def _scenario(row, label, *, override=None, input_bridges=False, year_end_offset=Decimal(0)):
    fields(row, {'segments', 'equity_adjustments', 'equity_value'}, label)
    require(isinstance(row['segments'], list) and bool(row['segments']), label + '.segments: expected nonempty list')
    segments, segment_ids, lengths = [], set(), set()
    for index, segment in enumerate(row['segments']):
        # Validation belongs to _segment, including rejection of non-object rows.
        changed = override is not None and isinstance(segment, dict) and segment.get('id') == override[0]
        result = _segment(segment, f'{label}.segments[{index}]',
                          terminal_margin=override[1] if changed else None, input_bridges=input_bridges, year_end_offset=year_end_offset)
        require(result['id'] not in segment_ids, label + ': duplicate segment id')
        segment_ids.add(result['id'])
        lengths.add(len(result['years']))
        segments.append(result)
    require(len(lengths) == 1, label + ': segments require same forecast length')
    adjustments = row['equity_adjustments']
    require(isinstance(adjustments, list), label + '.equity_adjustments: expected list')
    adjustment_total, adjustment_ids = Decimal(0), set()
    for item in adjustments:
        fields(item, {'id', 'amount', 'reason', 'source'}, label + '.equity_adjustment')
        ident = string(item['id'], label + '.equity_adjustment.id')
        require(ident not in adjustment_ids, label + ': duplicate equity adjustment id')
        adjustment_ids.add(ident)
        string(item['reason'], label + '.equity_adjustment.reason')
        string(item['source'], label + '.equity_adjustment.source')
        adjustment_total += number(item['amount'], label + '.equity_adjustment.amount')
    enterprise = sum((item['enterprise_value'] for item in segments), Decimal(0))
    return dict(segments=segments, enterprise_value=enterprise,
                equity_adjustments=adjustment_total, equity_value=enterprise + adjustment_total)


def evaluate_dcf(model, *, input_bridges=False):
    """Return unrounded Decimal values/details; verify declared equity within .005.

    The computed equity, rather than its potentially rounded declaration, feeds
    per-share values. Invalid inputs or arithmetic outside precision raise ValueError.
    """
    try:
        with localcontext(_CALCULATION_CONTEXT):
            fields(model, {'kind', 'currency', 'amount_unit', 'shares', 'fx_to_quote', 'scenarios'}
                   | ({'year_end_offset'} if input_bridges else set()), 'dcf')
            offset = number(model['year_end_offset'], 'year_end_offset') if input_bridges else Decimal(0)
            require(-1 < offset < 1, 'year_end_offset must be between -1 and 1')
            require(model['kind'] == 'dcf_fcff', 'dcf.kind: expected dcf_fcff')
            require(model['amount_unit'] == '100_million', 'dcf.amount_unit: expected 100_million')
            string(model['currency'], 'dcf.currency')
            shares = number(model['shares'], 'dcf.shares', positive=True)
            require(shares == shares.to_integral_value(), 'dcf.shares: actual whole shares required')
            fx = number(model['fx_to_quote'], 'dcf.fx_to_quote', positive=True)
            fields(model['scenarios'], set(SCENARIOS), 'dcf.scenarios')
            values, details = {}, {}
            for label in SCENARIOS:
                row = model['scenarios'][label]
                result = _scenario(row, label, input_bridges=input_bridges, year_end_offset=offset)
                equity = result['equity_value']
                require(equity > 0, label + ': positive equity required')
                claimed = number(row['equity_value'], label + '.equity_value')
                require(abs(claimed - equity) <= EQUITY_TOLERANCE,
                        f'{label}.equity_value: {claimed} != calculated {equity}')
                values[label] = equity * AMOUNT_SCALE / shares * fx
                details[label] = result
            require(values['low'] <= values['base'] <= values['high'], 'dcf: unordered scenario values')
            return dict(values=values, details=details)
    except DecimalException as exc:
        raise ValueError('dcf: arithmetic outside calculable precision') from exc


def solve_reverse_dcf(model, *, scenario, segment_id, variable, target_price, lower, upper, input_bridges=False):
    """Solve one terminal margin while freezing every other disclosed input.

    Terminal value is affine in this margin, so exact linear interpolation is
    sufficient. Bounds lie in [0, 1]; a zero-margin bound is allowed, but an
    admissible final solution needs positive terminal NOPAT. A valid model with
    no admissible root raises ReverseNoSolutionError, never a fabricated estimate.
    """
    evaluate_dcf(model, input_bridges=input_bridges)
    require(isinstance(scenario, str) and scenario in SCENARIOS, 'reverse.scenario: unknown scenario')
    string(segment_id, 'reverse.segment_id')
    require(variable == 'terminal_margin', 'reverse.variable: only terminal_margin is supported')
    row = model['scenarios'][scenario]
    require(segment_id in {item['id'] for item in row['segments']}, 'reverse.segment_id: unknown segment')
    target = number(target_price, 'reverse.target_price', positive=True)
    low, high = number(lower, 'reverse.lower'), number(upper, 'reverse.upper')
    require(0 <= low < high <= 1, 'reverse.bounds: require 0 <= lower < upper <= 1')
    try:
        with localcontext(_CALCULATION_CONTEXT):
            scale = AMOUNT_SCALE / number(model['shares'], 'shares') * number(model['fx_to_quote'], 'fx_to_quote')

            def price_at(margin):
                return _scenario(row, scenario, override=(segment_id, margin), input_bridges=input_bridges,
                                 year_end_offset=number(model['year_end_offset'], 'year_end_offset') if input_bridges else Decimal(0))['equity_value'] * scale

            low_price, high_price = price_at(low), price_at(high)
            if high_price == low_price:
                raise ReverseNoSolutionError('reverse: no identifiable root; terminal margin sensitivity is zero')
            if not min(low_price, high_price) <= target <= max(low_price, high_price):
                raise ReverseNoSolutionError('reverse: no root within supplied bounds')
            parameter = low + (target - low_price) * (high - low) / (high_price - low_price)
            if parameter <= 0:
                raise ReverseNoSolutionError('reverse: no admissible root with positive terminal NOPAT')
            if input_bridges:
                segment = next(s for s in row['segments'] if s['id'] == segment_id)
                terminal = segment['terminal']
                nopat = number(segment['years'][-1]['revenue'], 'revenue') * (1 + number(terminal['growth'], 'growth')) * parameter * (1 - number(terminal['tax_rate'], 'tax_rate'))
                if nopat <= number(terminal['invested_capital'], 'capital') * number(terminal['growth'], 'growth'):
                    raise ReverseNoSolutionError('reverse: no admissible root with positive terminal FCFF')
            price = price_at(parameter)
            residual = price - target
            require(abs(residual) <= PRICE_TOLERANCE, 'reverse: computed residual exceeds precision tolerance')
            return dict(parameter=parameter, modeled_price=price, residual=residual)
    except DecimalException as exc:
        raise ValueError('reverse: arithmetic outside calculable precision') from exc


def validate_reverse_dcf(model, reverse, *, input_bridges=False):
    """Re-solve and check a declared root, its actual price and signed residual.

    Parameters must agree within 1e-10; quoted price/residual within 1e-6. These
    tolerances audit calculation precision and are not a valuation confidence band.
    """
    arguments = {'scenario', 'segment_id', 'variable', 'target_price', 'lower', 'upper'}
    fields(reverse, arguments | {'parameter', 'modeled_price', 'residual'}, 'reverse')
    result = solve_reverse_dcf(model, input_bridges=input_bridges, **{key: reverse[key] for key in arguments})
    try:
        with localcontext(_CALCULATION_CONTEXT):
            parameter = number(reverse['parameter'], 'reverse.parameter')
            require(number(reverse['lower'], 'reverse.lower') <= parameter <= number(reverse['upper'], 'reverse.upper')
                    and parameter > 0, 'reverse.parameter: outside admissible bounds')
            require(abs(parameter - result['parameter']) <= PARAMETER_TOLERANCE,
                    'reverse.parameter: differs from recomputed solution')
            equity = _scenario(model['scenarios'][reverse['scenario']], reverse['scenario'],
                               override=(reverse['segment_id'], parameter), input_bridges=input_bridges,
                               year_end_offset=number(model['year_end_offset'], 'year_end_offset') if input_bridges else Decimal(0))['equity_value']
            price = equity * AMOUNT_SCALE / number(model['shares'], 'shares') * number(model['fx_to_quote'], 'fx_to_quote')
            residual = price - number(reverse['target_price'], 'reverse.target_price')
            for key, expected in [('modeled_price', price), ('residual', residual)]:
                claimed = number(reverse[key], 'reverse.' + key)
                require(abs(claimed - expected) <= PRICE_TOLERANCE, 'reverse.' + key + ': differs from recalculation')
            require(abs(residual) <= PRICE_TOLERANCE, 'reverse.residual: declared parameter does not reach target')
            return result
    except DecimalException as exc:
        raise ValueError('reverse: arithmetic outside calculable precision') from exc
