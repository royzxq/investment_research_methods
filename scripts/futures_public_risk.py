"""Public limits of real listed contracts in the last completed trading week."""
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

SCHEMA = 'futures-public-risk/v1'
FIELDS = {
    'trade_cal': 'exchange,cal_date,is_open',
    'ft_limit': 'ts_code,trade_date,exchange,up_limit,down_limit,m_ratio',
    'fut_daily': 'ts_code,trade_date,pre_settle,settle,high,low,oi',
    'fut_settle': 'ts_code,trade_date,exchange,settle,long_margin_rate,short_margin_rate,b_hedging_margin_rate,s_hedging_margin_rate',
    'fut_trade_param': 'ts_code,trade_date,exchange,tick_size,pre_settle_price,price_limit,position_limit,trade_limit',
    'fut_trade_param_dce': 'ts_code,trade_date,exchange,trade_type,type,spec_buy_rate,hedge_buy_rate,rise_limit_rate,rise_limit,fall_limit,client_buy_posi_quota',
}
EXCHANGES = {'ZCE': 'CZCE', 'SHF': 'SHFE', 'DCE': 'DCE'}
MARGIN_FIELDS = ('long_margin_rate', 'short_margin_rate', 'b_hedging_margin_rate', 's_hedging_margin_rate')
ROOT = Path(__file__).resolve().parents[1]
CHECK_FILE = 'public-risk-exchange-checks.json'


def number(value):
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return n if n.is_finite() and n >= 0 else None


def lots(value):
    n = number(value)
    return int(n) if n is not None and n == n.to_integral_value() else None


def rate(value, scale=1):
    n = number(value)
    if n is not None and 0 < n * scale <= 100:
        return float(n * scale)
    return None


def window(cutoff, exchange, query):
    day = datetime.strptime(cutoff, '%Y%m%d').date()
    friday = day - timedelta(days=(day.weekday() - 4) % 7)
    first = friday - timedelta(days=39)
    rows = query('trade_cal', dict(exchange=exchange, start_date=first.strftime('%Y%m%d'),
                                   end_date=friday.strftime('%Y%m%d')), FIELDS['trade_cal'])
    expected = {(first+timedelta(days=i)).strftime('%Y%m%d') for i in range(40)}
    if (len(rows) != len(expected) or {r['cal_date'] for r in rows} != expected or
            any(r['exchange'] != exchange or str(r['is_open']) not in ('0', '1') for r in rows)):
        raise ValueError('交易所日历不完整')
    opens = sorted(r['cal_date'] for r in rows if str(r['is_open']) == '1')
    for _ in range(5):
        monday = (friday-timedelta(days=4)).strftime('%Y%m%d')
        days = [d for d in opens if monday <= d <= friday.strftime('%Y%m%d')]
        before = [d for d in opens if d < monday]
        if before and days:
            return dict(friday=friday.isoformat(), prior=before[-1], sessions=days)
        friday -= timedelta(days=7)
    raise ValueError('缺完整交易周或前一交易日')


def dated(rows, code, exchange, valid_days):
    out = {}
    for row in rows:
        day = row['trade_date']
        if row['ts_code'] != code or row.get('exchange', exchange) != exchange or day not in valid_days:
            raise ValueError('响应合约、交易所或日期不匹配')
        if day in out:
            raise ValueError('单日参数重复')
        out[day] = row
    return out


def summarize(code, exchange, day, prior, tables):
    def item(key, d=day):
        return tables.get(key, {}).get(d, {})
    errors = []
    board, bar, settle = item('ft_limit'), item('fut_daily'), item('fut_settle')
    low, high = number(board.get('down_limit')), number(board.get('up_limit'))
    minimum, maximum = number(bar.get('low')), number(bar.get('high'))
    if low is None or high is None or not 0 < low < high:
        low = high = None
        errors.append('缺有效板价')
    elif not minimum or not maximum:
        errors.append('缺当日成交高低价，板价未做包络核对')
    elif not low <= minimum <= maximum <= high:
        low = high = None
        errors.append('当日日线与板价冲突')
    minimum_pct = rate(board.get('m_ratio'))
    margins = {k: rate(settle.get(k), 1 if exchange == 'CZCE' else 100) for k in MARGIN_FIELDS}
    closing_settle = number(bar.get('settle'))
    # A percentage/fraction switch at the provider must not silently shrink a reported rate 100-fold.
    if exchange == 'CZCE' and minimum_pct and any(
            number(settle.get(k)) and number(settle[k]) * 100 == number(minimum_pct) for k in MARGIN_FIELDS):
        margins = dict.fromkeys(MARGIN_FIELDS)
        errors.append('郑商所结算保证金单位与盘前字段冲突')
    if not closing_settle or closing_settle != number(settle.get('settle')):
        margins = dict.fromkeys(MARGIN_FIELDS)
        errors.append('结算日期或价格未核')
    if minimum_pct is None or None in margins.values():
        errors.append('保证金字段不全')
    position = opening = after_close = basis_day = None
    if exchange == 'CZCE':
        params = item('fut_trade_param')
        pre = number(params.get('pre_settle_price'))
        if pre is not None and pre > 0 and pre == number(bar.get('pre_settle')):
            position = lots(params.get('position_limit'))
            opening = lots(params.get('trade_limit'))
            basis_day = day
        else:
            errors.append('盘前参数的前结算价不符或缺失')
    elif exchange == 'DCE':
        # DCE's date-labelled table can describe the session after settlement.
        # Admit a prior settlement row only after matching both current board prices.
        previous = item('fut_trade_param_dce', prior)
        current = item('fut_trade_param_dce')
        if current.get('trade_type') == '期货':
            after_close = lots(current.get('client_buy_posi_quota'))
        if (previous.get('trade_type') == '期货' and high is not None and
                high == number(previous.get('rise_limit')) and low == number(previous.get('fall_limit')) and
                number(bar.get('pre_settle')) and
                number(bar['pre_settle']) == number(item('fut_daily', prior).get('settle'))):
            position = lots(previous.get('client_buy_posi_quota'))
            basis_day = prior
        else:
            errors.append('前一结算参数与当日板价未匹配')
    return dict(ts_code=code, trade_date=day, up_limit=float(high) if high else None,
                down_limit=float(low) if low else None, minimum_margin_pct=minimum_pct,
                settlement_margin_pct=margins, session_position_limit_lots=position,
                position_source_date=basis_day, session_open_limit_lots=opening,
                closing_table_position_limit_lots=after_close, issues=errors)


def evidence_key(doc):
    fields = ('schema', 'calendars', 'codes', 'raw')
    data = json.dumps({k: doc[k] for k in fields}, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def week_directory(friday, root=ROOT):
    return root/'research/futures/weekly'/(date.fromisoformat(friday)+timedelta(days=2)).isoformat()


def attach_checks(doc, root):
    fridays = {c['friday'] for c in doc['calendars'].values()}
    if len(fridays) != 1:
        return
    path = week_directory(fridays.pop(), root)/'evidence'/CHECK_FILE
    if not path.is_file():
        return
    try:
        check = json.loads(path.read_text())
        checked_at = datetime.fromisoformat(check['observed_at'])
        if (check['input_sha256'] != doc['input_sha256'] or checked_at.tzinfo is None or
                checked_at > datetime.fromisoformat(doc['observed_at']) or
                checked_at.astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d') > doc['as_of_date']):
            return
        verified_rows = []
        for row in doc['rows']:
            record = check['contracts'][row['ts_code']][row['trade_date']]
            additions = {'exchange_check': record['status'], 'board_check': record['board']}
            if record.get('position_rule'):
                additions['position_rule'] = record['position_rule']
            if 'closing_table_position_limit_lots' in record:
                additions['closing_table_position_limit_lots'] = record['closing_table_position_limit_lots']
            verified_rows.append(additions)
    except (KeyError, TypeError, ValueError, OSError):
        doc['issues'].append('交易所核对附件无法完整读取')
        return
    for row, additions in zip(doc['rows'], verified_rows):
        row.update(additions)
    doc['exchange_checks'] = str(path.relative_to(root))


def collect(as_of, cutoff, codes, query, root=ROOT):
    observed = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    doc = dict(schema=SCHEMA, as_of_date=as_of, cutoff=cutoff, observed_at=observed,
               codes=sorted(set(codes)), calendars={}, raw={}, rows=[], issues=[],
               account_margin_rate=None, remaining_position_capacity=None,
               final_lots=None, execution_permission='not_evaluated')
    for code in doc['codes']:
        if not re.fullmatch(r'[A-Z]+\d{2}(?:0[1-9]|1[0-2])\.(?:ZCE|DCE|SHF)', code):
            raise ValueError(f'须提供有交易所后缀的真实月份合约 {code}')
    for exchange in sorted({EXCHANGES[c.split('.')[1]] for c in doc['codes']}):
        try:
            doc['calendars'][exchange] = window(cutoff, exchange, query)
        except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
            doc['issues'].append(f'{exchange} 交易日历缺口 {type(exc).__name__}')
    for code in doc['codes']:
        exchange = EXCHANGES[code.split('.')[1]]
        cal = doc['calendars'].get(exchange)
        if not cal:
            continue
        days = [cal['prior'], *cal['sessions']]
        endpoints = ['ft_limit', 'fut_settle', 'fut_daily']
        if exchange in ('CZCE', 'DCE'):
            endpoints.append('fut_trade_param' if exchange == 'CZCE' else 'fut_trade_param_dce')
        tables = doc['raw'][code] = {}
        for ep in endpoints:
            try:
                rows = query(ep, dict(ts_code=code, start_date=days[0], end_date=days[-1]), FIELDS[ep])
                tables[ep] = dated(rows, code, exchange, days)
            except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
                tables[ep] = {}
                doc['issues'].append(f'{code} {ep} 数据缺口 {type(exc).__name__}')
        for prior, day in zip(days, days[1:]):
            doc['rows'].append(summarize(code, exchange, day, prior, tables))
    doc['input_sha256'] = evidence_key(doc)
    attach_checks(doc, root)
    return doc


def render(doc):
    lines = ['---- 最近完整交易周 · 真实月份合约公开风控参数 ----']
    for exchange, cal in doc['calendars'].items():
        lines.append(f"{exchange} {cal['sessions'][0]}–{cal['sessions'][-1]}，前一结算日 {cal['prior']}。")
    lines += ['单位：板价为元/吨，保证金为百分数，限仓为单边手数。逐日输入见数据包 public_risk。',
              '合约 | 日期 | 跌停/涨停 | 板价表保证金 | 结算投机买/卖 | 结算套保买/卖 | 当日客户限仓 | 盘后表客户限仓 | 日内开仓限额']

    def show(value):
        return '缺口' if value is None else f'{value:g}' if isinstance(value, float) else str(value)
    for row in doc['rows']:
        m = row['settlement_margin_pct']
        cap = row['session_position_limit_lots']
        if cap is None and row.get('position_rule'):
            cap = row['position_rule']['description']
        lines.append(' | '.join([row['ts_code'], row['trade_date'],
                     '/'.join(map(show, (row['down_limit'], row['up_limit']))
                              ), show(row['minimum_margin_pct']),
                     '/'.join(map(show, (m['long_margin_rate'], m['short_margin_rate']))),
                     '/'.join(map(show, (m['b_hedging_margin_rate'], m['s_hedging_margin_rate']))), show(cap),
                     show(row['closing_table_position_limit_lots']), show(row['session_open_limit_lots'])]))
        if row['issues']:
            lines.append('  ' + '，'.join(row['issues']))
    if doc.get('exchange_checks'):
        lines.append('逐字段核验及来源 '+doc['exchange_checks'])
    lines.extend(doc['issues'])
    lines += ['公开参数仅覆盖上述交易周。客户持仓限额、日内开仓限额和账户剩余额度分别记录。'
              '经纪商实收、已有持仓和挂单需另核。', '采集时间 '+doc['observed_at']]
    return '\n'.join(lines)
