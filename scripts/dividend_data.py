"""Optional A-share dividend evidence add-on; no forecasts, trades or schema rewrites.

Units: daily_basic.dv_ttm and the ChinaBond yield are percent; difference is percentage
points. Raw dividend rows require primary-source reconciliation before aggregation.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
from zoneinfo import ZoneInfo

SCHEMA = 'dividend-data-addon/v1'
SOURCES = {'daily_basic': 'https://tushare.pro/document/2?doc_id=32',
           'dividend': 'https://tushare.pro/document/2?doc_id=103'}
FIELDS = {
 'daily_basic': 'ts_code,trade_date,close,dv_ratio,dv_ttm,pb',
 'dividend': 'ts_code,end_date,ann_date,div_proc,cash_div,cash_div_tax,record_date,ex_date,pay_date,imp_ann_date,base_date,base_share'}
LIMITS = {'daily_basic': 6000, 'dividend': 2000}
SOURCES.update(chinabond_10y='https://yield.chinabond.com.cn/cbweb-pbc-web/pbc/historyQuery',
               hk_cash_ttm='Tushare hk_daily/hk_basic/hk_adjfactor/hk_tradecal + Eastmoney RPT_HKF10_MAIN_DIVBASIC')
FIELDS.update(chinabond_10y='trade_date,yield', hk_cash_ttm='ts_code,trade_date,close,dv_ttm,dividend_events')
LIMITS.update(chinabond_10y=2, hk_cash_ttm=2)


HK_EVIDENCE_GAPS = {
    'dividend_history_unavailable', 'incomplete_dividend_history', 'duplicate_dividend_rows',
    'invalid_disclosure_date', 'wrong_dividend_security', 'missing_ex_date',
    'unverified_disclosure_version', 'unverified_hkd_conversion', 'unrecognized_distribution_terms',
    'ambiguous_cash_amount', 'unverified_hkd_counter', 'missing_raw_close', 'stale_raw_close',
    'missing_calendar_anchor', 'incomplete_twelve_month_history', 'incomplete_factor_sessions',
    'raw_close_disagreement', 'unexplained_corporate_action', 'corporate_action_amount_mismatch',
    'unconfirmed_ex_date', 'missing_explicit_zero_disclosures', 'incomplete_hk_calendar',
}


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{8}', value):
        raise ValueError('date must be YYYYMMDD')
    return datetime.strptime(value, '%Y%m%d').date()


def number(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        value = float(value)
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) else None


def same_day_spread(stock, bond):
    """Strict units/identity/date check, usable for other matched currencies too."""
    if not stock or not bond:
        return None
    if (stock.get('unit') != 'percent' or bond.get('unit') != 'percent'
            or stock.get('currency') != bond.get('currency')
            or stock.get('currency') not in ('CNY', 'HKD', 'USD')
            or stock.get('as_of') != bond.get('as_of')
            or bond.get('tenor_years') != 10 or bond.get('curve_type') != 'government_ytm'):
        return None
    try:
        date.fromisoformat(stock['as_of'])
    except (ValueError, TypeError, KeyError):
        return None
    a, b = number(stock.get('value')), number(bond.get('value'))
    if a is None or b is None or a < 0:
        return None
    return round(a - b, 10)


def request_rows(token, endpoint, params):
    # HTTPS only; do not include remote messages/response body in errors/logs.
    if endpoint in ('hk_cash_ttm', 'chinabond_10y'):
        # Standalone CLI reuses the same public providers as the scheduler.
        import importlib.util
        root = Path(os.environ.get('AI_INVESTMENT_ROOT', Path(__file__).resolve().parents[2] / 'ai_investment'))
        if endpoint == 'hk_cash_ttm':
            import sys
            sys.path.insert(0, str(root))
            try:
                from src.data.adapter import DataAdapter
                return DataAdapter().get_research_dividend_rows(endpoint, params, FIELDS[endpoint])
            finally:
                sys.path.pop(0)
        spec = importlib.util.spec_from_file_location('_public_research_yields', root/'src/data/services/research_yields.py')
        provider = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(provider)
        return [{'trade_date': params['trade_date'], 'yield': provider.bond_value(params['trade_date'])}]
    if not token:
        raise RuntimeError('TUSHARE_TOKEN unavailable')
    import requests
    response = requests.post('https://api.tushare.pro', timeout=(10, 25),
        json={'api_name': endpoint, 'token': token, 'params': params, 'fields': FIELDS[endpoint]})
    response.raise_for_status()
    payload = response.json()
    if payload.get('code') != 0:
        message = str(payload.get('msg', '')).lower()
        if '权限' in message or '积分' in message or 'permission' in message:
            raise PermissionError('provider permission unavailable')
        raise RuntimeError('provider denied request or reported an API error')
    data = payload.get('data') or {}
    fields, items = data.get('fields'), data.get('items')
    if (not isinstance(fields, list) or not isinstance(items, list) or len(set(fields)) != len(fields)
            or not set(FIELDS[endpoint].split(',')) <= set(fields)
            or any(not isinstance(row, list) or len(row) != len(fields) for row in items)):
        raise ValueError('provider response schema mismatch')
    return [dict(zip(fields, row)) for row in items]


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def write_once(path, value):
    """Atomic no-overwrite publication; interrupted writes never look complete."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.dividend-partial-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(canonical(value)); f.flush(); os.fsync(f.fileno())
        os.link(name, path)
    finally:
        os.unlink(name)


def _hk_v2_evidence(rows):
    if len(rows) != 1 or not isinstance(rows[0], dict):
        return False
    row = rows[0]
    coverage = row.get('coverage')
    return (row.get('evidence_version') == 2 and row.get('source') == SOURCES['hk_cash_ttm']
            and isinstance(coverage, dict) and isinstance(coverage.get('factor_sessions'), int)
            and coverage['factor_sessions'] > 0 and isinstance(row.get('dividend_events'), list))


def fetch(endpoint, params, cache, call):
    identity = {'endpoint': endpoint, 'params': params, 'fields': FIELDS[endpoint]}
    key = hashlib.sha256(canonical(identity)).hexdigest()
    path = Path(cache) / endpoint / (key + '.json')
    if path.exists():
        doc = json.loads(path.read_text())
        rows = doc.get('rows')
        if (doc.get('identity') != identity or doc.get('status') != 'ok'
                or doc.get('rows_sha256') != hashlib.sha256(canonical(rows)).hexdigest()
                or not isinstance(rows, list) or not rows or len(rows) >= LIMITS[endpoint]
                or any(not isinstance(row, dict) for row in rows)
                or not isinstance(doc.get('retrieved_at'), str)):
            raise ValueError('invalid dividend cache; preserve and use an isolated cache directory')
        if endpoint == 'hk_cash_ttm' and params.get('evidence_version') == 2 and (
                doc.get('source') != SOURCES[endpoint] or not _hk_v2_evidence(rows)):
            raise ValueError('invalid HK provider version in cache')
        return {**doc, 'cache_path': str(path.resolve()), 'cached': True}
    now = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    try:
        if endpoint == 'hk_cash_ttm' and params.get('evidence_version') != 2:
            raise ValueError('legacy HK evidence requires its original snapshot')
        rows = call(endpoint, params)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError('invalid rows')
        if endpoint == 'hk_cash_ttm' and rows and not _hk_v2_evidence(rows):
            raise ValueError('HK source version mismatch')
        # Reject NaN rather than converting unverified quantities to zero.
        digest = hashlib.sha256(canonical(rows)).hexdigest()
        status = 'empty' if not rows else ('possibly_truncated' if len(rows) >= LIMITS[endpoint] else 'ok')
        doc = dict(identity=identity, status=status, retrieved_at=now, rows=rows,
                   rows_sha256=digest, source=SOURCES[endpoint])
    except Exception as exc:
        # Deliberately no str(exc): clients may echo token/body in exceptions.
        failure = dict(identity=identity, status='unavailable', retrieved_at=now,
                       rows=[], source=SOURCES[endpoint], error_type=type(exc).__name__)
        if endpoint == 'hk_cash_ttm':
            from_hint = getattr(exc, 'evidence_gap', None)
            if isinstance(from_hint, str) and from_hint in HK_EVIDENCE_GAPS:
                failure['evidence_gap'] = from_hint
        return failure
    if status == 'ok':
        try:
            write_once(path, doc)
        except FileExistsError:
            return fetch(endpoint, params, cache, call)
    return {**doc, 'cache_path': str(path.resolve()) if status == 'ok' else None, 'cached': False}


def build(code, as_of, cache, call, *, include_dividends=True, market_as_of=None, route=None):
    cutoff = day(as_of)
    market_day = day(market_as_of) if market_as_of is not None else cutoff
    if not 0 <= (cutoff - market_day).days <= 7:
        raise ValueError('market date outside evidence window')
    market_date = market_day.strftime('%Y%m%d')
    if cutoff > datetime.now(ZoneInfo('Asia/Shanghai')).date():
        raise ValueError('future cutoff is not allowed')
    if not re.fullmatch(r'(?:[036]\d{5}\.(?:SH|SZ)|\d{5}\.HK)', code):
        raise ValueError('expected A-share or HK TS code')
    result = dict(schema_version=SCHEMA, code=code, as_of=cutoff.isoformat(),
        generated_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(), status='partial',
        scope='supplementary evidence only; no trading or valuation forecast',
        strict_point_in_time=False, history_percentile=None, forward_ordinary_dividend=None,
        forward_net_yield=None, sources={}, gaps=[], trailing_yield=None,
        government_10y=None, trailing_spread_pp=None, dividend_events=[])
    if code.endswith('.HK'):
        if route is None:
            route = classify(code, as_of, cache, call)
            if route['trailing_yield'] and route['trailing_yield']['as_of'] != market_day.isoformat():
                result['gaps'].append('standalone addon requires an exact-date HK observation')
                return result
        result.update(trailing_yield=route['trailing_yield'], screening_government_10y=route['government_10y'],
                      screening_spread_pp=route['spread_pp'], sources=route['sources'].copy())
        result['gaps'] = list(route['gaps']) + ['HK payout originals, investor taxes/FX and matched HKD benchmark required; A-share interfaces not substituted']
        if route['status'] == 'classified':
            validate_route(route, code, cutoff.isoformat())
            if market_as_of is not None and route['trailing_yield']['as_of'] != market_day.isoformat():
                raise ValueError('frozen route and market date differ')
            doc = route['sources']['quote_search']
            quotes = fetch('hk_cash_ttm', doc['identity']['params'], cache, call)
            if quotes.get('rows_sha256') != doc['rows_sha256']:
                raise ValueError('HK payout evidence differs from frozen quote')
            result['dividend_events'] = [{**event, 'ordinary_or_special':'unverified', 'investor_net_cash_verified':False}
                                        for event in quotes['rows'][0]['dividend_events']]
        return result
    requests = {'daily_basic': dict(ts_code=code, trade_date=market_date)}
    if include_dividends:
        requests['dividend'] = dict(ts_code=code)
    if route is not None:
        validate_route(route, code, cutoff.isoformat())
        if route['trailing_yield']['as_of'] != market_day.isoformat():
            raise ValueError('frozen route and market date differ')
    for endpoint, params in requests.items():
        endpoint_cache = Path(cache) / ('dividend-asof-' + as_of) if endpoint == 'dividend' else Path(cache)
        result['sources'][endpoint] = fetch(endpoint, params, endpoint_cache, call)
        if result['sources'][endpoint]['status'] != 'ok':
            result['gaps'].append(endpoint + ': ' + result['sources'][endpoint]['status'])
    def usable(endpoint):
        doc = result['sources'][endpoint]
        return doc['rows'] if doc['status'] == 'ok' else []
    quotes = [r for r in usable('daily_basic') if r.get('ts_code') == code and r.get('trade_date') == market_date]
    if len(quotes) == 1 and number(quotes[0].get('dv_ttm')) is not None and number(quotes[0]['dv_ttm']) >= 0:
        result['trailing_yield'] = dict(value=number(quotes[0]['dv_ttm']), unit='percent', currency='CNY',
            as_of=market_day.isoformat(), basis='Tushare dv_ttm; provider historical gross convention; not sustainable ordinary yield',
            source=SOURCES['daily_basic'])
    else:
        result['gaps'].append('unique same-day dv_ttm unavailable')
    if route is not None:
        if not result['trailing_yield'] or result['trailing_yield']['value'] != route['trailing_yield']['value']:
            raise ValueError('dividend addon and frozen yield differ')
        result['government_10y'] = route['government_10y'].copy()
        bond_source = result['government_10y']['source']
        result['sources'].update({k:v.copy() for k,v in route['sources'].items() if v.get('source') == bond_source})
    else:
        result['government_10y'] = public_bond(market_date, cache, call, result['sources'])
        if not result['government_10y']:
            result['gaps'].append('unique same-day CNY government 10y YTM unavailable')
    result['trailing_spread_pp'] = same_day_spread(result['trailing_yield'], result['government_10y'])
    if not include_dividends:
        result['status'] = 'complete' if result['trailing_spread_pp'] is not None else 'partial'
        for source in result['sources'].values():
            source.pop('rows', None)
        return result
    excluded = 0
    seen = set()
    for row in usable('dividend'):
        if row.get('ts_code') != code:
            excluded += 1; continue
        # Latest state can contain a later implementation than the first announcement.
        dates = [row.get('ann_date')]
        if row.get('imp_ann_date'):
            dates.append(row['imp_ann_date'])
        if row.get('div_proc') == '实施' and not row.get('imp_ann_date'):
            excluded += 1; continue
        try:
            if any(day(d) > cutoff for d in dates):
                excluded += 1; continue
        except (ValueError, TypeError):
            excluded += 1; continue
        key = canonical(row)
        if key in seen:
            continue
        seen.add(key)
        result['dividend_events'].append({**row, 'ordinary_or_special': 'unverified',
             'investor_net_cash_verified': False, 'historical_state_verified': False})
    result['excluded_dividend_rows'] = excluded
    result['gaps'] += ['Reconcile payout versions and ordinary/special classification with company originals; no automatic sums',
        'cash_div is provider net convention, not verified investor-specific after-tax receipt',
        'Current API backfill is not a strict historical PIT archive; verify original disclosure before historical use',
        'Forecast payout, tax/channel/FX and comparable historical percentile require separate research']
    if not result['dividend_events']:
        result['gaps'].append('No usable dividend rows does not establish zero dividends')
    # complete means requested raw retrieval succeeded, not that research is complete.
    result['status'] = ('complete' if all(result['sources'][k]['status'] == 'ok' for k in ('daily_basic', 'dividend'))
                        and result['trailing_spread_pp'] is not None and result['dividend_events'] else 'partial')
    for source in result['sources'].values():
        source.pop('rows', None)  # Raw retrieval stays in cache, never in the research fact list.
    return result


ROUTE_SCHEMA = 'stock-research-route/v1'
ROUTE_RULE = 'dividend-spread/v1'
CN_RULE = 'dividend-spread/cn10y-v2'
MAX_ROUTE_AGE_DAYS = 7


def public_bond(effective, cache, call, sources):
    doc = fetch('chinabond_10y', dict(trade_date=effective), cache, call)
    sources['chinabond_10y'] = {k:v for k,v in doc.items() if k != 'rows'}
    if doc['status'] != 'ok' or len(doc['rows']) != 1:
        return None
    row = doc['rows'][0]
    if row.get('trade_date') != effective or number(row.get('yield')) is None:
        return None
    return dict(value=number(row['yield']), unit='percent', currency='CNY', as_of=day(effective).isoformat(),
                tenor_years=10, curve_type='government_ytm', series='ChinaBond 1001.CB / type 0 / 10y',
                source=SOURCES['chinabond_10y'])


def screening_spread(stock, bond):
    # Common RMB opportunity-cost benchmark for routing ONLY. HD5 still calls same_day_spread.
    if not stock or not bond or stock.get('currency') not in ('CNY','HKD') or bond.get('currency') != 'CNY' or bond.get('series') != 'ChinaBond 1001.CB / type 0 / 10y':
        return None
    if stock.get('as_of') != bond.get('as_of') or stock.get('unit') != 'percent' or bond.get('unit') != 'percent' or bond.get('tenor_years') != 10 or bond.get('curve_type') != 'government_ytm':
        return None
    a, b = number(stock.get('value')), number(bond.get('value'))
    return float(Decimal(str(a)) - Decimal(str(b))) if a is not None and a >= 0 and b is not None else None


def validate_route(route, code, valuation_date):
    """Admission contract shared by producer and consumer; never recompute from live data."""
    if not isinstance(route, dict):
        raise ValueError('research_route must be an object')
    threshold = number(route.get('threshold_pp'))
    if (route.get('schema_version') != ROUTE_SCHEMA or route.get('rule') not in (ROUTE_RULE, CN_RULE)
            or route.get('code') != code or route.get('valuation_date') != valuation_date
            or route.get('status') != 'classified' or route.get('comparison') != '>'
            or threshold is None or threshold < 0
            or route.get('max_age_days') != MAX_ROUTE_AGE_DAYS):
        raise ValueError('invalid or pending research_route')
    stock, bond = route.get('trailing_yield'), route.get('government_10y')
    if not isinstance(stock, dict) or not isinstance(bond, dict):
        raise ValueError('research_route observations required')
    expected_currency = 'HKD' if code.endswith('.HK') else 'CNY'
    if (stock.get('currency') != expected_currency or stock.get('basis') != 'gross_ttm'
            or any(not isinstance(o.get('source'), str) or not o['source'].strip() for o in (stock, bond))):
        raise ValueError('research_route currency/basis/source mismatch')
    spread = (screening_spread if route['rule'] == CN_RULE else same_day_spread)(stock, bond)
    if (spread is None or number(route.get('spread_pp')) != spread
            or not 0 <= (date.fromisoformat(valuation_date) - date.fromisoformat(stock['as_of'])).days <= MAX_ROUTE_AGE_DAYS
            or route.get('strategy') != ('dividend' if spread > threshold else 'non_dividend')):
        raise ValueError('research_route inconsistent observations or decision')
    return route


def classify(code, as_of, cache, call, *, threshold_pp=None):
    """Lightweight preflight; missing evidence is pending, never non-dividend."""
    cutoff = day(as_of)
    threshold = number((3.5 if code.endswith('.HK') else 2.0) if threshold_pp is None else threshold_pp)
    if threshold is None or threshold < 0:
        raise ValueError('threshold_pp must be a finite nonnegative number')
    if cutoff > datetime.now(ZoneInfo('Asia/Shanghai')).date():
        raise ValueError('future cutoff is not allowed')
    if not re.fullmatch(r'(?:[036]\d{5}\.(?:SH|SZ)|\d{5}\.HK)', code):
        raise ValueError('expected A-share or HK TS code')
    result = dict(schema_version=ROUTE_SCHEMA, rule=CN_RULE, code=code,
        valuation_date=cutoff.isoformat(), threshold_pp=threshold, comparison='>',
        max_age_days=MAX_ROUTE_AGE_DAYS, status='pending', strategy=None,
        trailing_yield=None, government_10y=None, spread_pp=None, sources={}, gaps=[])
    start = cutoff - timedelta(days=MAX_ROUTE_AGE_DAYS)
    hk = code.endswith('.HK')
    endpoint = 'hk_cash_ttm' if hk else 'daily_basic'
    params = dict(ts_code=code, start_date=start.strftime('%Y%m%d'), end_date=as_of)
    if hk:
        params['evidence_version'] = 2  # old frozen snapshots retain their original cache identity
    quotes = fetch(endpoint, params, cache, call)
    result['sources']['quote_search'] = {k: v for k, v in quotes.items() if k != 'rows'}
    valid = []
    if quotes['status'] == 'ok':
        for row in quotes['rows']:
            try:
                if row.get('ts_code') == code and start <= day(row.get('trade_date')) <= cutoff:
                    valid.append(row)
            except (ValueError, TypeError):
                continue
    if not valid:
        result['gaps'] = ['recent ' + endpoint + ' unavailable: ' + quotes.get('evidence_gap', quotes['status'])]
        return result
    effective = max(row['trade_date'] for row in valid)
    latest = [row for row in valid if row['trade_date'] == effective]
    if len(latest) != 1 or number(latest[0].get('dv_ttm')) is None or number(latest[0]['dv_ttm']) < 0:
        result['gaps'] = ['latest observation lacks unique valid dv_ttm; older yield not substituted']
        return result
    if hk:
        result['trailing_yield'] = dict(value=number(latest[0]['dv_ttm']), unit='percent', currency='HKD',
            as_of=day(effective).isoformat(), source=quotes['source'])
        result['government_10y'] = public_bond(effective, cache, call, result['sources'])
        if not result['government_10y']:
            result['gaps'].append('missing same-day ChinaBond CNY 10Y')
    else:
        evidence = build(code, effective, cache, call, include_dividends=False)
        result.update(trailing_yield=evidence['trailing_yield'], government_10y=evidence['government_10y'], gaps=evidence['gaps'])
        result['sources'].update(evidence['sources'])
    result['spread_pp'] = screening_spread(result['trailing_yield'], result['government_10y'])
    if result['trailing_yield']:
        result['trailing_yield']['basis'] = 'gross_ttm'
    if result['spread_pp'] is not None:
        result.update(status='classified', strategy='dividend' if result['spread_pp'] > threshold else 'non_dividend')
        validate_route(result, code, cutoff.isoformat())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code', required=True)
    parser.add_argument('--as-of', required=True, help='YYYYMMDD; exact effective date, no automatic prior-day substitution')
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output already exists; use an isolated filename')
    token = os.environ.get('TUSHARE_TOKEN')
    def call(endpoint, params):
        return request_rows(token, endpoint, params)
    result = build(args.code, args.as_of, args.cache_dir, call)
    write_once(args.output, result)
    print(json.dumps({'status': result['status'], 'output': str(args.output.resolve()),
                      'sources': {k: v['status'] for k, v in result['sources'].items()},
                      'trailing_spread_pp': result['trailing_spread_pp']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
