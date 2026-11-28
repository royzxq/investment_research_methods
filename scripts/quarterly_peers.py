"""Freeze one disclosed A-share quarterly cross-section for weekly and company research."""
import argparse
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
from statistics import median
import tempfile
from zlib import error as ZlibError
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / 'research/investment/weekly'
SCHEMA = 'a-quarterly-peers/v1'
BASE = 'ts_code,end_date,ann_date,f_ann_date,report_type,comp_type,update_flag'
FIELDS = {
    'income_vip': BASE + ',total_revenue,n_income_attr_p',
    'balancesheet_vip': BASE + ',total_assets,total_liab',
    'cashflow_vip': BASE + ',n_cashflow_act',
    'disclosure_date': 'ts_code,end_date,actual_date',
    'index_member_all': 'ts_code,name,l3_code,l3_name,in_date,out_date,is_new',
    'fina_mainbz_vip': 'ts_code,end_date,bz_item,bz_sales,curr_type',
}
AMOUNTS = {'total_revenue': '营业总收入', 'n_income_attr_p': '归母净利润',
           'total_assets': '期末总资产', 'total_liab': '期末总负债', 'n_cashflow_act': '经营现金流净额'}
RATIOS = {'parent_margin': '归母净利润/营业总收入', 'liabilities_to_assets': '期末负债/资产',
          'operating_cash_margin': '经营现金流/营业总收入'}
STATEMENTS = {'income_vip': ('total_revenue','n_income_attr_p'),
              'balancesheet_vip': ('total_assets','total_liab'), 'cashflow_vip': ('n_cashflow_act',)}


def last_period(day):
    start = date(day.year, 3 * ((day.month - 1) // 3) + 1, 1)
    return (start - timedelta(days=1)).strftime('%Y%m%d')


def path_for(weekly, observed, period):
    iso = datetime.strptime(observed, '%Y%m%d').date().isoformat()
    return weekly / iso / 'evidence' / f'investment-{iso}-a-peers-{period}.json.gz'


def fetch_snapshot(observed, period, call):
    rows, requests = {}, {}
    for endpoint, fields in FIELDS.items():
        if endpoint in STATEMENTS:
            params = dict(period=period, report_type='1')
        elif endpoint == 'index_member_all':
            params = dict(is_new='Y')
        elif endpoint == 'disclosure_date':
            params = dict(end_date=period)
        else:
            params = dict(period=period, type='P')
        pages, seen, result = [], set(), []
        request = requests[endpoint] = dict(params=params, fields=fields, page_sizes=pages)
        try:
            while True:
                offset = len(result)
                page = call(endpoint, dict(params, offset=offset, limit=1000), fields)
                pages.append(len(page))
                if not page:
                    break
                if 'end_date' in fields.split(',') and any(r.get('end_date') != period for r in page):
                    raise ValueError(f'{endpoint}: received another period')
                digest = hashlib.sha256(json.dumps(page, sort_keys=True).encode()).hexdigest()
                if digest in seen:
                    raise ValueError(f'{endpoint}: repeated page at offset {offset}')
                seen.add(digest)
                result.extend(page)
            if not result and endpoint != 'fina_mainbz_vip':
                raise ValueError(f'{endpoint}: empty table')
        except (OSError, RuntimeError, ValueError) as exc:
            if endpoint != 'fina_mainbz_vip':
                raise
            # A partial product table cannot establish coverage for any issuer.
            result = []
            request['error'] = type(exc).__name__
        rows[endpoint] = result
    return dict(schema=SCHEMA, observed=observed, period=period, requests=requests, rows=rows)


def publish(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix='.partial')
    try:
        with os.fdopen(fd, 'wb') as f:
            raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
            f.write(gzip.compress(raw, mtime=0))
        os.link(tmp, path)
    finally:
        os.unlink(tmp)


def valid_day(value, low, high):
    try:
        return bool(value and re.fullmatch(r'[0-9]{8}', value) and low <= value <= high
                    and datetime.strptime(value, '%Y%m%d'))
    except (ValueError, TypeError):
        return False


def amount(v):
    return v if type(v) in (float, int) and math.isfinite(v) else None


def companies(snapshot):
    observed, period, tables = snapshot['observed'], snapshot['period'], snapshot['rows']
    stocks = defaultdict(dict)
    reporting = {r['ts_code'] for table in (*STATEMENTS, 'disclosure_date') for r in tables[table]}
    groups, filings = defaultdict(set), defaultdict(set)
    for r in tables['index_member_all']:
        if (r['ts_code'] in reporting and r['is_new'] == 'Y' and valid_day(r['in_date'], '19000101', observed)
                and (not r['out_date'] or r['out_date'] > observed) and r['l3_code'] and r['l3_name']):
            groups[r['ts_code']].add((r['l3_code'], r['l3_name'], r['name']))
    for code, memberships in groups.items():
        if len(memberships) == 1:
            s = stocks[code]
            s['industry_code'], s['industry'], s['name'] = memberships.pop()
    for r in tables['disclosure_date']:
        if valid_day(r['actual_date'], period, observed):
            filings[r['ts_code']].add(r['actual_date'])
    for code, dates in filings.items():
        if len(dates) == 1:
            stocks[code]['actual_date'] = dates.pop()
    for endpoint, fields in STATEMENTS.items():
        versions = defaultdict(list)
        for r in tables[endpoint]:
            if (str(r['report_type']) == '1' and valid_day(r['f_ann_date'], period, observed)
                    and valid_day(r['ann_date'], period, observed)):
                versions[r['ts_code']].append(r)
        for code, rows in versions.items():
            s = stocks[code]
            if not s.get('actual_date'):
                continue
            d = max(r['f_ann_date'] for r in rows)
            latest = [r for r in rows if r['f_ann_date'] == d]
            s.setdefault('filings', {})[endpoint] = d
            for k in fields:
                values = {amount(r[k]) for r in latest}
                if len(values) == 1:
                    s[k] = next(iter(values))
                else:
                    s[k] = None
                    s.setdefault('gaps', []).append(endpoint + ' 同日合并报表字段冲突 ' + k)
            s.setdefault('types', set()).update(str(r['comp_type']) for r in latest)
    for r in tables['fina_mainbz_vip']:
        s = stocks.get(r['ts_code'])
        if (s and s.get('actual_date') and r['bz_item'] and r['curr_type']
                and amount(r['bz_sales']) is not None):
            s.setdefault('product_rows', set()).add((r['bz_item'], r['bz_sales'], r['curr_type']))
    product_error = snapshot.get('requests', {}).get('fina_mainbz_vip', {}).get('error')
    for s in stocks.values():
        if product_error:
            s.setdefault('gaps', []).append(f'本次分产品取数失败（{product_error}），当期覆盖未知。')
        types = s.pop('types', set())
        if len(types) > 1:
            s.setdefault('gaps', []).append('财报公司类型冲突，同行统计留空')
        s['comp_type'] = next(iter(types)) if len(types) == 1 and types <= {'1','2','3','4'} else None
        ratios = [('parent_margin','n_income_attr_p','total_revenue'),
                  ('liabilities_to_assets','total_liab','total_assets')]
        if s['comp_type'] == '1':
            ratios.append(('operating_cash_margin','n_cashflow_act','total_revenue'))
        for key, numerator, denominator in ratios:
            if s.get(numerator) is not None and (s.get(denominator) or 0) > 0:
                s[key] = 100 * s[numerator] / s[denominator]
    return {code: stocks[code] for code in reporting
            if re.fullmatch(r'(?:6\d{5}\.SH|[03]\d{5}\.SZ|[489]\d{5}\.BJ)', code)}


@lru_cache(maxsize=2)
def load(path):
    raw = path.read_bytes()
    snapshot = json.loads(gzip.decompress(raw))
    if (snapshot['schema'] != SCHEMA or path != path_for(path.parents[2], snapshot['observed'], snapshot['period'])):
        raise ValueError('财报截面日期或身份不匹配')
    return snapshot['period'], snapshot['observed'], hashlib.sha256(raw).hexdigest(), companies(snapshot)


def primary_amount_source(path, result):
    """Use an issuer filing check only when its period, snapshot and five amounts match."""
    check = path.with_name(f"investment-{path.parents[1].name}-peer-validation-{result['period']}.json")
    try:
        data = json.loads(check.read_text())
        if any(data[k] != result[k] for k in ('period', 'observed', 'sha256')):
            return None
        sample = data['samples'][result['code']]
        scale = {'人民币元': 1, '人民币百万元': 1_000_000}[sample['source_unit']]
        if not all(Decimal(str(result['amounts'][k])) == Decimal(sample['reported_amounts'][k]) * scale
                   for k in AMOUNTS):
            return None
        return dict(url=sample['report'], pages=sample['pages'], unit=sample['source_unit'])
    except (OSError, ValueError, KeyError, TypeError, InvalidOperation):
        return None


def for_pack(code, as_of, weekly=WEEKLY):
    period_limit = last_period(datetime.strptime(as_of, '%Y%m%d').date())
    latest_by_period = {}
    for p in weekly.glob('????-??-??/evidence/investment-*-a-peers-????????.json.gz'):
        observed = p.parents[1].name.replace('-', '')
        period = p.name.removesuffix('.json.gz').rsplit('-', 1)[-1]
        if (valid_day(observed, '19900101', as_of) and period <= period_limit
                and p == path_for(weekly, observed, period)):
            if period not in latest_by_period or observed > latest_by_period[period][0]:
                latest_by_period[period] = (observed, p)
    if not latest_by_period:
        return dict(code=code, gap='截至估值日没有已采集的季度同行截面')
    periods = sorted(latest_by_period, reverse=True)
    # During reporting season some issuers still have only the previous period.
    for period in periods:
        observed, path = latest_by_period[period]
        try:
            period, observed, digest, stocks = load(path)
        except (OSError, EOFError, ValueError, KeyError, TypeError, ZlibError) as exc:
            return dict(code=code, period=period, observed=observed, source=path.name,
                        gap=f'季度截面读取失败 {path.name}（{type(exc).__name__}）')
        s = stocks.get(code, {})
        if (s.get('actual_date') and s.get('filings')) or period == periods[-1]:
            break
    result = dict(code=code, period=period, observed=observed, sha256=digest,
                  source=str(path.relative_to(weekly.parent.parent.parent)), actual_date=s.get('actual_date'),
                  filings=s.get('filings', {}), industry=s.get('industry'), industry_code=s.get('industry_code'),
                  gaps=list(s.get('gaps', [])), product_count=len(s.get('product_rows', ())))
    products = defaultdict(set)
    for name, sales, currency in s.get('product_rows', ()):
        products[name].add((sales, currency))
    result['products'] = []
    for name, values in sorted(products.items()):
        if len(values) == 1:
            sales, currency = next(iter(values))
            result['products'].append(dict(name=name, sales=sales, currency=currency))
        else:
            result['gaps'].append(f'主营分项「{name}」存在金额或币种冲突')
    if period < periods[0]:
        result['gaps'].append(f'{periods[0]} 截面缺该公司已核披露日或合并报表，列最近已核期。')
    if not s.get('actual_date') or not s.get('filings'):
        return dict(result, gap='当期实际披露日或可核合并报表缺失')
    group = {c: p for c, p in stocks.items() if c != code and s.get('industry_code')
             and p.get('industry_code') == s['industry_code']}
    peers = {c: p for c, p in group.items() if s.get('comp_type') and p.get('comp_type') == s['comp_type']}
    result.update(group_size=len(group), members={c: peers[c]['name'] for c in sorted(peers)}, metrics={})
    result['amounts'] = {k: s.get(k) for k in AMOUNTS}
    result['primary_amount_source'] = primary_amount_source(path, result)
    result['report_currency'] = 'CNY' if result['primary_amount_source'] else None
    for k, label in RATIOS.items():
        if k == 'operating_cash_margin' and s.get('comp_type') != '1':
            continue
        values = [p[k] for p in peers.values() if p.get(k) is not None]
        own = s.get(k)
        result['metrics'][k] = dict(label=label, unit='%', own=own, n=len(values),
                                    peer_median=median(values) if values else None)
    return result


def render(result):
    lines = ['### A股季度合并财报与同行对照']
    if result.get('gap'):
        return '\n'.join(lines + [f"{result.get('period', '')} {result['gap']}".strip()])
    labels = {'income_vip': '利润表', 'balancesheet_vip': '资产负债表', 'cashflow_vip': '现金流量表'}
    dates = '、'.join(f"{label} {result['filings'].get(key, '缺口')}" for key, label in labels.items())
    members = list(result['members'].items())
    examples = '、'.join(f'{name} {code}' for code, name in members[:8])
    primary = result['primary_amount_source']
    scale = 1e8 if primary else 1
    amounts = '、'.join(f'{label} {result["amounts"][k]/scale:,.2f}' if result['amounts'][k] is not None
                       else f'{label} 缺口' for k, label in AMOUNTS.items())
    own_line = (f"本公司合并报表（亿元人民币）：{amounts}。[公司季报第 {primary['pages']} 页]({primary['url']})"
                if primary else f"本公司接口原数：{amounts}。三表缺逐行币种和金额单位，应用金额时核对原报表。")
    lines += [f"报告期 {result['period']}，收入、利润和经营现金流为年初累计，资产负债为期末数。实际披露 {result['actual_date']}。"
              f"合并表公告日为{dates}。同业取采集日 {result['observed']} 的申万三级{result['industry'] or '（缺行业）'}。"
              f"本期三表或披露日历中同行有 {result['group_size']} 只，剔除本公司。相同报表类型 {len(members)} 只"
              f"（{examples or '缺口'}{'等' if len(members) > 8 else ''}）。n 为各指标有效家数。",
              own_line, "同行比较逐家公司先算比率，再取中位数。跨表现金流比率沿用同公司报表计量一致的假设。", '',
              '| 指标 | 本公司 | 同行中位数 | n |', '|---|---:|---:|---:|']
    for m in result['metrics'].values():
        own, peer = (f'{v:,.2f}' if v is not None else '缺口' for v in (m['own'], m['peer_median']))
        lines.append(f"| {m['label']}（{m['unit']}） | {own} | {peer} | {m['n']} |")
    lines += result['gaps']
    for product in result.get('products', []):
        lines.append(f"- 当期分产品收入 {product['name']} {product['sales']:,.2f} {product['currency']}，按采集日版本。")
    lines += [f"本截面可用主营产品原始行 {result['product_count']} 条。数据源 Tushare，截面 {result['source']}，SHA-256 {result['sha256']}。"]
    return '\n'.join(lines)


if __name__ == '__main__':
    from dividend_data import request_rows
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', required=True, help='北京时间采集日 YYYYMMDD')
    parser.add_argument('--period', help='季末 YYYYMMDD，缺省最近已结束季度')
    args = parser.parse_args()
    today = datetime.now(ZoneInfo('Asia/Shanghai')).date()
    if not valid_day(args.as_of, '19900101', today.strftime('%Y%m%d')):
        parser.error('观察日须为已到达的北京时间日期 YYYYMMDD')
    observed = datetime.strptime(args.as_of, '%Y%m%d').date()
    period = args.period or last_period(observed)
    if period[-4:] not in ('0331','0630','0930','1231') or not valid_day(period, '19900101', args.as_of):
        parser.error('invalid report period')
    path = path_for(WEEKLY, args.as_of, period)
    if not path.exists():
        if observed != today:
            parser.error('缺少该观察日冻结截面，当日行业名单与报表版本不能用于回填')
        snapshot = fetch_snapshot(args.as_of, period, lambda e,p,f: request_rows(
            os.environ.get('TUSHARE_TOKEN'), e, p, fields=f))
        if datetime.now(ZoneInfo('Asia/Shanghai')).date() != today:
            parser.error('采集跨日，请使用新的观测日重跑')
        publish(path, snapshot)
    print(path, len(load(path)[3]), 'companies')
