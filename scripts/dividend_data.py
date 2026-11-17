"""Optional A-share dividend evidence add-on; no forecasts, trades or schema rewrites.

Units: daily_basic.dv_ttm and yc_cb.yield are percent; difference is percentage
points. Raw dividend rows require primary-source reconciliation before aggregation.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime
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
           'dividend': 'https://tushare.pro/document/2?doc_id=103',
           'yc_cb': 'https://tushare.pro/document/2?doc_id=201'}
FIELDS = {
 'daily_basic': 'ts_code,trade_date,close,dv_ratio,dv_ttm,pb',
 'dividend': 'ts_code,end_date,ann_date,div_proc,cash_div,cash_div_tax,record_date,ex_date,pay_date,imp_ann_date,base_date,base_share',
 'yc_cb': 'ts_code,trade_date,curve_name,curve_type,curve_term,yield'}
LIMITS = {'daily_basic': 6000, 'dividend': 2000, 'yc_cb': 2000}


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
        return {**doc, 'cache_path': str(path.resolve()), 'cached': True}
    now = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    try:
        rows = call(endpoint, params)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError('invalid rows')
        # Reject NaN rather than converting unverified quantities to zero.
        digest = hashlib.sha256(canonical(rows)).hexdigest()
        status = 'empty' if not rows else ('possibly_truncated' if len(rows) >= LIMITS[endpoint] else 'ok')
        doc = dict(identity=identity, status=status, retrieved_at=now, rows=rows,
                   rows_sha256=digest, source=SOURCES[endpoint])
    except Exception as exc:
        # Deliberately no str(exc): clients may echo token/body in exceptions.
        return dict(identity=identity, status='unavailable', retrieved_at=now,
                    rows=[], source=SOURCES[endpoint], error_type=type(exc).__name__)
    if status == 'ok':
        try:
            write_once(path, doc)
        except FileExistsError:
            return fetch(endpoint, params, cache, call)
    return {**doc, 'cache_path': str(path.resolve()) if status == 'ok' else None, 'cached': False}


def build(code, as_of, cache, call):
    cutoff = day(as_of)
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
        result['gaps'] = ['HK payout originals, investor taxes/FX and matched HKD benchmark required; A-share interfaces not substituted']
        return result
    requests = {'daily_basic': dict(ts_code=code, trade_date=as_of),
                'dividend': dict(ts_code=code),
                'yc_cb': dict(ts_code='1001.CB', curve_type='0', curve_term=10, trade_date=as_of)}
    for endpoint, params in requests.items():
        endpoint_cache = Path(cache) / ('dividend-asof-' + as_of) if endpoint == 'dividend' else Path(cache)
        result['sources'][endpoint] = fetch(endpoint, params, endpoint_cache, call)
        if result['sources'][endpoint]['status'] != 'ok':
            result['gaps'].append(endpoint + ': ' + result['sources'][endpoint]['status'])
    def usable(endpoint):
        doc = result['sources'][endpoint]
        return doc['rows'] if doc['status'] == 'ok' else []
    quotes = [r for r in usable('daily_basic') if r.get('ts_code') == code and r.get('trade_date') == as_of]
    if len(quotes) == 1 and number(quotes[0].get('dv_ttm')) is not None and number(quotes[0]['dv_ttm']) >= 0:
        result['trailing_yield'] = dict(value=number(quotes[0]['dv_ttm']), unit='percent', currency='CNY',
            as_of=cutoff.isoformat(), basis='Tushare dv_ttm; provider historical gross convention; not sustainable ordinary yield',
            source=SOURCES['daily_basic'])
    else:
        result['gaps'].append('unique same-day dv_ttm unavailable')
    # Official docs sample uses legacy curve code 101 for 1001.CB; require name too.
    rates = [r for r in usable('yc_cb') if r.get('ts_code') in ('1001.CB', '101', 101)
        and r.get('curve_name') == '中债国债收益率曲线' and str(r.get('curve_type')) == '0'
        and number(r.get('curve_term')) == 10 and r.get('trade_date') == as_of]
    if len(rates) == 1 and number(rates[0].get('yield')) is not None:
        result['government_10y'] = dict(value=number(rates[0]['yield']), unit='percent', currency='CNY',
            as_of=cutoff.isoformat(), tenor_years=10, curve_type='government_ytm',
            series='ChinaBond 1001.CB / type 0 / 10y', source=SOURCES['yc_cb'])
    else:
        result['gaps'].append('unique same-day CNY government 10y YTM unavailable')
    result['trailing_spread_pp'] = same_day_spread(result['trailing_yield'], result['government_10y'])
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
    result['status'] = ('complete' if all(s['status'] == 'ok' for s in result['sources'].values())
                        and result['trailing_spread_pp'] is not None and result['dividend_events'] else 'partial')
    for source in result['sources'].values():
        source.pop('rows', None)  # Raw retrieval stays in cache, never in the research fact list.
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
        if not token:
            raise RuntimeError('TUSHARE_TOKEN unavailable')
        return request_rows(token, endpoint, params)
    result = build(args.code, args.as_of, args.cache_dir, call)
    write_once(args.output, result)
    print(json.dumps({'status': result['status'], 'output': str(args.output.resolve()),
                      'sources': {k: v['status'] for k, v in result['sources'].items()},
                      'trailing_spread_pp': result['trailing_spread_pp']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
