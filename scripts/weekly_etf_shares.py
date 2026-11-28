"""Listed ETF sample for the stock weekly review and the ETF snapshot."""
import argparse
from datetime import date, datetime, timedelta
import json
import math
import os
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
WEEKLY = ROOT / 'research/investment/weekly'
# Fixed listed instruments; exclude their feeder funds and share classes.
BASKET = {'510300.SH': '沪深300ETF华泰柏瑞', '159915.SZ': '创业板ETF易方达',
          '512480.SH': '半导体ETF国联安', '512170.SH': '医疗ETF华宝'}
FIELDS = {'fund_share': 'ts_code,trade_date,fd_share', 'fund_daily': 'ts_code,trade_date,close,amount',
          'fund_nav': 'ts_code,nav_date,ann_date,unit_nav', 'fund_adj': 'ts_code,trade_date,adj_factor'}
SCHEMA = 'listed-etf-week/v1'


def calendar_window(cutoff, call):
    d = datetime.strptime(cutoff, '%Y%m%d').date()
    friday = d - timedelta(days=(d.weekday() - 4) % 7)
    start = friday - timedelta(days=32)
    start_s, end_s = start.strftime('%Y%m%d'), friday.strftime('%Y%m%d')
    rows = call('trade_cal', dict(exchange='SSE', start_date=start_s, end_date=end_s),
                'exchange,cal_date,is_open')
    expected = {(start + timedelta(days=i)).strftime('%Y%m%d') for i in range((friday-start).days+1)}
    if (len(rows) != len(expected) or {r['cal_date'] for r in rows} != expected or
        any(r['exchange'] != 'SSE' or str(r['is_open']) not in ('0','1') for r in rows)):
        raise ValueError('沪深 ETF 交易日在上交所日历中的覆盖不完整')
    opens = sorted(r['cal_date'] for r in rows if str(r['is_open']) == '1')
    for _ in range(4):
        monday = (friday - timedelta(days=4)).strftime('%Y%m%d')
        week = [t for t in opens if monday <= t <= friday.strftime('%Y%m%d')]
        prior = [t for t in opens if t < monday]
        if week and prior:
            return [prior[-1], *week]
        friday -= timedelta(days=7)
    raise ValueError('找不到完整交易周及其前收盘日')


def series(rows, code, sessions, cutoff, endpoint, field):
    values = {}
    for r in rows:
        if r['ts_code'] != code:
            raise ValueError(f'{endpoint} 返回其他基金')
        day = r.get('nav_date') if endpoint == 'fund_nav' else r['trade_date']
        if day not in sessions:
            continue
        ann = r.get('ann_date') if endpoint == 'fund_nav' else day
        if not isinstance(ann, str) or not day <= ann <= cutoff:
            continue
        try:
            datetime.strptime(ann, '%Y%m%d')
        except ValueError:
            continue
        v = r[field]
        if v is not None and (type(v) not in (int, float) or not math.isfinite(v)
                              or v < 0 or (field != 'amount' and v == 0)):
            v = None
        values.setdefault(day, {}).setdefault(ann, set()).add(v)
    result = {}
    for day, versions in values.items():
        candidates = versions[max(versions)]
        if len(candidates) == 1:
            result[day] = next(iter(candidates))
    return [result.get(d) for d in sessions]


def summarize(code, sessions, cutoff, tables):
    shares = series(tables['fund_share'], code, sessions, cutoff, 'fund_share', 'fd_share')
    price = series(tables['fund_daily'], code, sessions, cutoff, 'fund_daily', 'close')
    turnover = series(tables['fund_daily'], code, sessions, cutoff, 'fund_daily', 'amount')
    nav = series(tables['fund_nav'], code, sessions, cutoff, 'fund_nav', 'unit_nav')
    factors = series(tables['fund_adj'], code, sessions, cutoff, 'fund_adj', 'adj_factor')
    change = None if shares[0] is None or shares[-1] is None else (shares[-1]-shares[0])/10000
    price_change = None if not price[0] or not price[-1] else (price[-1]/price[0]-1)*100
    stable = None if None in factors else len(set(factors)) == 1
    valued = valuation_effect = None
    if None not in shares and None not in nav and stable:
        # 万份 × 元 = 万元. Exact split of the NAV-based change in assets.
        valued = sum((shares[i]-shares[i-1])*nav[i] for i in range(1,len(sessions))) / 10000
        valuation_effect = sum(shares[i-1]*(nav[i]-nav[i-1]) for i in range(1,len(sessions))) / 10000
    return dict(sessions=sessions, shares_wan=shares, close_cny=price, unit_nav_cny=nav,
                amount_thousand_cny=turnover, adjustment_factors=factors,
                delta_yi_shares=change, price_change_pct=price_change, factor_stable=stable,
                share_change_at_nav_yi_cny=valued, nav_effect_yi_cny=valuation_effect,
                weekly_turnover_yi_cny=sum(turnover[1:])/100000 if None not in turnover[1:] else None)


def collect(cutoff, call, *, market_cutoff=None):
    sessions = calendar_window(min(market_cutoff or cutoff, cutoff), call)
    data = {}
    for code, name in BASKET.items():
        tables, errors = {}, {}
        params = dict(ts_code=code, start_date=sessions[0], end_date=sessions[-1])
        for endpoint, fields in FIELDS.items():
            try:
                tables[endpoint] = call(endpoint, params, fields)
            except (PermissionError, RuntimeError, ValueError, OSError) as exc:
                errors[endpoint] = type(exc).__name__
                tables[endpoint] = []
        summary = summarize(code, sessions, cutoff, tables)
        data[code] = dict(name=name, summary=summary, errors=errors, inputs=tables)
    return dict(schema=SCHEMA, cutoff=cutoff, sessions=sessions, funds=data)


def missing_observations(doc):
    fields = ('shares_wan', 'close_cny', 'unit_nav_cny', 'amount_thousand_cny', 'adjustment_factors')
    return {code: [f'{day} {field}' for field in fields
                   for day, value in zip(doc['sessions'], fund['summary'][field]) if value is None]
            for code, fund in doc['funds'].items()}


def render(doc):
    def fmt(v):
        return '缺口' if v is None else f'{v:,.2f}'
    days = doc['sessions']
    lines = [f"场内 ETF 固定样本，前一交易周末收盘 {days[0]} 至 {days[-1]}，本周 {len(days)-1} 个交易日。"
             f"数据来自 Tushare fund_share、fund_nav、fund_daily、fund_adj，观察日 {doc['cutoff']}。", '',
             '| 基金 | 份额变化（亿份） | 收盘涨跌（%） | 份额变化按每日净值折算（亿元） | 净值变化贡献（亿元） | 二级成交（亿元） |',
             '|---|---:|---:|---:|---:|---:|']
    for code, fund in doc['funds'].items():
        s = fund['summary']
        data = [s[k] for k in ('delta_yi_shares','price_change_pct','share_change_at_nav_yi_cny',
                               'nav_effect_yi_cny','weekly_turnover_yi_cny')]
        lines.append(f"| {fund['name']} {code} | " + ' | '.join(map(fmt, data)) + ' |')
    lines.extend(['', '份额为期末减期初。净值折算逐日使用当日单位净值，净值贡献使用前日份额。缺份额、净值、复权因子或因子变化时，两项折算留空。申购与赎回各自总量、实付现金及账户身份仍须另核。'])
    return '\n'.join(lines)


def evidence_path(day):
    iso = datetime.strptime(day, '%Y%m%d').date().isoformat()
    return WEEKLY / iso / 'evidence' / f'investment-{iso}-etf-shares.json'


def snapshot_section(cutoff, weekly=WEEKLY, *, market_cutoff=None):
    """Reuse only a by-cutoff observation for the same completed calendar week."""
    d = datetime.strptime(cutoff, '%Y%m%d').date()
    last_bar = min(cutoff, market_cutoff or cutoff)
    market_day = datetime.strptime(last_bar, '%Y%m%d').date()
    friday = market_day - timedelta(days=(market_day.weekday()-4) % 7)
    for p in sorted(weekly.glob('????-??-??/evidence/investment-*-etf-shares.json'), reverse=True):
        obs = date.fromisoformat(p.parents[1].name)
        if friday <= obs <= d and p.name == f'investment-{obs}-etf-shares.json':
            doc = json.loads(p.read_text())
            if (doc.get('schema') == SCHEMA and doc.get('cutoff') == obs.strftime('%Y%m%d')
                    and doc.get('sessions') and doc['sessions'][-1] <= min(last_bar, friday.strftime('%Y%m%d'))):
                return render(doc)
    return None


if __name__ == '__main__':
    from dividend_data import request_rows
    from research_paths import write_json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', required=True)
    args = parser.parse_args()
    today = datetime.now(ZoneInfo('Asia/Shanghai'))
    try:
        observed = datetime.strptime(args.as_of, '%Y%m%d').date()
    except ValueError:
        parser.error('观察日格式须为 YYYYMMDD')
    if observed.strftime('%Y%m%d') != args.as_of or observed > today.date():
        parser.error('观察日须为已到达的北京时间日期 YYYYMMDD')
    path = evidence_path(args.as_of)
    if not path.exists():
        if observed != today.date() or (today.weekday() == 4 and today.hour < 18):
            parser.error('缺少该日冻结份额，实时采集须为当天，周五须在收盘数据发布后')
        doc = collect(args.as_of, lambda e,p,f: request_rows(os.environ.get('TUSHARE_TOKEN'), e,p,fields=f))
        missing = missing_observations(doc)
        if any(missing.values()):
            parser.exit(1, '本次接口不完整，可重试。\n' + render(doc) + '\n' + str(missing) + '\n')
        if datetime.now(ZoneInfo('Asia/Shanghai')).date() != today.date():
            parser.exit(1, '采集跨日，请使用新的观测日重跑。\n')
        write_json(path, doc)
    print(render(json.loads(path.read_text())))
