"""Verify a weekly candidate pack against exchange files and the selected rule editions."""
import argparse
import csv
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
import requests

try:
    from .futures_public_risk import evidence_key, EXCHANGES, MARGIN_FIELDS, summarize
    from .research_paths import write_json
except ImportError:  # direct script invocation
    from futures_public_risk import evidence_key, EXCHANGES, MARGIN_FIELDS, summarize
    from research_paths import write_json

URLS = {
    'cz': 'https://www.czce.com.cn/cn/DFSStaticFiles/Future/{year}/{day}/FutureDataClearParams.txt',
    'settle': 'https://www.shfe.com.cn/data/tradedata/future/dailydata/js{day}.dat',
    'bars': 'https://www.shfe.com.cn/data/tradedata/future/dailydata/kx{day}.dat',
    'param': 'https://www.shfe.com.cn/data/busiparamdata/future/ContractDailyTradeArgument{day}.dat',
}
WEEK_20261120 = {
    'rb': 'https://www.shfe.com.cn/regulation/exchangerules/productrules/202512/t20251231_829962.html',
    'dce': 'https://www.hongtaqh.com/tzzjy/zcfg/zlgz/202511/20251117_11189.html',
    'guodu': 'https://www.guodu.cc/yjts/show-835.html',
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def decimal(value):
    return Decimal(str(value).strip().replace(',', ''))


def delivery_month_distance(symbol, day):
    delivery = datetime.strptime(symbol[-4:], '%y%m')
    session = datetime.strptime(day, '%Y%m%d')
    return (delivery.year - session.year) * 12 + delivery.month - session.month


def rebar_position_rule(distance, previous_oi, closing_oi):
    require(distance >= 0, 'expired rebar contract')
    if distance >= 2 and (previous_oi < 900000) != (closing_oi < 900000):
        return dict(description='单向持仓跨90万手档位，盘中适用基数待核', fixed_branch_lots=None, fraction=None)
    if distance >= 2 and closing_oi >= 900000:
        return dict(description='单向持仓量×10%（规则档）', fixed_branch_lots=None, fraction=0.1)
    fixed = 900 if distance == 0 else 4500 if distance == 1 else 90000
    return dict(description=f'{fixed:,}手（规则档）', fixed_branch_lots=fixed, fraction=None)


def grid_check(row, pre, up, down, tick):
    for field, theoretical in [('up_limit', pre * (1 + up)), ('down_limit', pre * (1 - down))]:
        reported = decimal(row[field])
        require(reported % tick == 0 and abs(theoretical - reported) < tick,
                (row['ts_code'], row['trade_date'], field, theoretical, reported))
    return 'provider_absolute_vs_exchange_band_within_one_tick'


def verify(pack, candidate_pack, cache, output, rb_rule_url=None, dce_rule_url=None):
    doc = json.loads(pack.read_bytes())
    doc = doc.get('public_risk', doc)
    adopted_bytes = candidate_pack.read_bytes()
    adopted = json.loads(adopted_bytes)
    candidates = {r['market_inputs']['ts_code'] for r in adopted['trend']}
    for pair in adopted['economic_reversion']:
        candidates.update(x['ts_code'] for x in pair['market_inputs']['sources'].values())
    require(set(doc['codes']) == candidates, 'adopted candidate identity')
    windows = {tuple([cal['prior'], *cal['sessions']]) for cal in doc['calendars'].values()}
    require(len(windows) == 1, 'expected a shared dated session window')
    days = sorted(windows.pop())
    last = days[-1]
    expected = {(code, day) for code in candidates for day in days[1:]}
    actual = [(row['ts_code'], row['trade_date']) for row in doc['rows']]
    require(doc['input_sha256'] == evidence_key(doc) and len(actual) == len(expected)
            and set(actual) == expected, 'incomplete input')
    for row in doc['rows']:
        code, day = row['ts_code'], row['trade_date']
        exchange = EXCHANGES[code.split('.')[1]]
        prior = days[days.index(day)-1]
        derived = summarize(code, exchange, day, prior, doc['raw'][code])
        # This one field comes from the CZCE exchange attachment when replaying an enriched pack.
        if exchange == 'CZCE':
            derived.pop('closing_table_position_limit_lots')
        require(all(row.get(k) == v for k, v in derived.items()), f'{code} {day} differs from raw response')
    # The archived editions were reviewed for this week. Later weeks supply their applicable editions.
    static = WEEK_20261120.copy() if last == '20261120' else {}
    if rb_rule_url:
        static['rb'] = rb_rule_url
    if dce_rule_url:
        static['dce'] = dce_rule_url
    require(all(static.get(k, '').startswith('https://') for k in ('rb', 'dce')),
            'supply the effective --rb-rule-url and --dce-rule-url for this week')
    static['xml'] = f'https://www.czce.com.cn/cn/DFSStaticFiles/Future/{last[:4]}/{last}/FutureDataReferenceData.xml'
    cache.mkdir(parents=True, exist_ok=True)
    urls = {kind+day: url.format(year=day[:4], day=day) for kind, url in URLS.items() for day in days}
    source_index, data = {}, {}
    for key, url in {**urls, **static}.items():
        # Pin undated rule pages and reference XML to their source URL in the cache.
        path = cache/(key if key in urls else key+'-'+hashlib.sha256(url.encode()).hexdigest()[:16])
        if not path.exists():
            response = requests.get(url, timeout=(7, 25))
            response.raise_for_status()
            path.write_bytes(response.content)
        content = path.read_bytes()
        source_index[key] = dict(url=url, sha256=hashlib.sha256(content).hexdigest())
        if key.startswith('cz'):
            lines = content.decode('utf-8-sig').splitlines()
            day = datetime.strptime(key[2:], '%Y%m%d').date().isoformat()
            require(day in lines[0] and '郑州商品交易所' in lines[0], key)
            data[key] = {row['合约代码'].strip(): row for row in csv.DictReader(lines[1:], delimiter='|')}
        elif key == 'xml':
            data[key] = {r.findtext('CtrCd'): r for r in ET.fromstring(content).iter('Contract')}
        elif key in static:
            page = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
            data[key] = ''.join(page.stripped_strings).replace(' ', '')
        else:
            table = json.loads(content)
            require(str(table['report_date']) == key[-8:], key)
            data[key] = table
    require('≥90万手101045004500900900＜90万手9000090000' in data['rb'], 'SHFE article 47')
    require('该日前一交易日结算时的持仓量' in data['dce']
            and '豆粕单边持仓量≤400,00020,00020,000单边持仓量＞400,000单边持仓量×5%单边持仓量×5%' in data['dce'], 'DCE articles 28–29')
    if 'guodu' in data:
        require('2026年11月20日' in data['guodu'] and '豆粕m7106' in data['guodu'], 'dated broker bulletin')

    contracts = {}
    for row in doc['rows']:
        code, day = row['ts_code'], row['trade_date']
        prior = days[days.index(day)-1]
        symbol = code.split('.')[0]
        raw = doc['raw'][code]
        bar = raw['fut_daily'][day]
        checked = contracts.setdefault(code, {})[day] = {}
        if code.endswith('.ZCE'):
            local = symbol[:-4] + symbol[-3:]
            ref = data['xml'][local]
            require(ref.findtext('ExchCd') == 'XZCE' and ref.findtext('PrdCd') + ref.findtext('YrCd')[-2:] +
                    ref.findtext('MnthCd') == symbol, code)
            before, after = data['cz'+prior][local], data['cz'+day][local]
            pre = decimal(before['当日结算价'])
            band = decimal(before['涨跌停板(%)'].strip().lstrip('±'))
            tick = decimal(ref.findtext('TckSz').split('元')[0])
            position = int(before['日持仓限额'])
            opening = before['交易限额'].strip()
            require(pre == decimal(bar['pre_settle']) and decimal(
                after['当日结算价']) == decimal(bar['settle']), code)
            require(band == decimal(raw['fut_trade_param'][day]['price_limit']), code)
            require(position == row['session_position_limit_lots'] and (
                int(opening) if opening else None) == row['session_open_limit_lots'], code)
            require(decimal(before['交易保证金率(%)']) == decimal(row['minimum_margin_pct']) and
                    all(decimal(v) == decimal(after['交易保证金率(%)']) for v in row['settlement_margin_pct'].values()), code)
            checked.update(status='CZCE逐日结算原表与合约参考数据',
                           board=grid_check(row, pre, band/100, band/100, tick),
                           sources=['cz'+prior, 'cz'+day, 'xml'], settlement_basis_day=prior, prior_settle=float(pre),
                           band_pct=float(band), tick=float(tick), general_settlement_margin_pct=float(decimal(after['交易保证金率(%)'])),
                           session_position_limit_lots=position, closing_table_position_limit_lots=int(
                               after['日持仓限额']),
                           session_open_limit_lots=int(opening) if opening else None)
        elif code.endswith('.SHF'):
            require(symbol[:-4] == 'RB', 'no reviewed position rule for '+code)

            def shbar(d):
                return next(r for r in data['bars'+d]['o_curinstrument'] if r['PRODUCTID'].strip() == 'rb_f'
                            and r['DELIVERYMONTH'].strip() == symbol[-4:])
            a, b = shbar(prior), shbar(day)
            params = next(r for r in data['param'+day]['ContractDailyTradeArgument']
                          if r['INSTRUMENTID'].strip() == symbol.lower())
            settle = next(r for r in data['settle'+day]['o_cursor']
                          if r['INSTRUMENTID'].strip() == symbol.lower())
            require(params['TRADINGDAY'] == day and all(decimal(b[k]) == decimal(bar[f]) for k, f in
                                                        [('PRESETTLEMENTPRICE', 'pre_settle'), ('SETTLEMENTPRICE', 'settle'), ('OPENINTEREST', 'oi'),
                                                         ('HIGHESTPRICE', 'high'), ('LOWESTPRICE', 'low')]), code)
            require(decimal(settle['SETTLEMENTPRICE']) == decimal(bar['settle']), code)
            rates = [float(100*decimal(settle[k])) for k in
                     ('SPECLONGMARGINRATIO', 'SPECSHORTMARGINRATIO', 'HEDGLONGMARGINRATIO', 'HEDGSHORTMARGINRATIO')]
            require(rates == [row['settlement_margin_pct'][k] for k in MARGIN_FIELDS] and
                    decimal(params['SPEC_LONGMARGINRATIO'])*100 == decimal(row['minimum_margin_pct']), code)
            oi = [int(a['OPENINTEREST']), int(b['OPENINTEREST'])]
            distance = delivery_month_distance(symbol, day)
            checked.update(status='SHFE交易参数、结算参数、日行情及螺纹钢细则第四十七条',
                           board=grid_check(row, decimal(bar['pre_settle']), decimal(
                               params['UPPER_VALUE']), decimal(params['LOWER_VALUE']), Decimal(1)),
                           sources=['param'+day, 'settle'+day, 'bars'+prior, 'bars'+day, 'rb'], observed_single_side_oi=oi,
                           band_pct=[float(100*decimal(params[k])) for k in ('LOWER_VALUE', 'UPPER_VALUE')],
                           settlement_margin_pct=dict(zip(MARGIN_FIELDS, rates)),
                           position_rule=rebar_position_rule(distance, *oi))
        else:
            require(code.endswith('.DCE') and symbol[:-4] == 'M', 'no reviewed position rule for '+code)
            previous, current = raw['fut_trade_param_dce'][prior], raw['fut_trade_param_dce'][day]
            previous_oi, oi = int(raw['fut_daily'][prior]['oi']), int(bar['oi'])
            distance = delivery_month_distance(symbol, day)
            require(distance >= 0 and row['position_source_date'] == prior, code)
            prior_quota = row['session_position_limit_lots']
            close_quota = row['closing_table_position_limit_lots']
            require(prior_quota is not None and close_quota is not None, code)
            if distance >= 2:
                require(prior_quota == (previous_oi//20 if previous_oi > 400000 else 20000) and
                        close_quota == (oi//20 if oi > 400000 else 20000), code)
                limit_status = 'Tushare相邻日参数与限仓规则复算；未取得大商所逐日原表'
            else:
                limit_status = 'Tushare相邻日参数；临近交割的客户类别和限仓档位另核'
            require(previous['rise_limit'] == row['up_limit']
                    and previous['fall_limit'] == row['down_limit'], code)
            require(decimal(previous['spec_buy_rate'])*100 == decimal(row['minimum_margin_pct']), code)
            require(all(decimal(current[key])*100 == decimal(row['settlement_margin_pct'][col]) for key, col in
                        [('spec_buy_rate', 'long_margin_rate'), ('hedge_buy_rate', 'b_hedging_margin_rate')]), code)
            checked.update(status=limit_status,
                           sources=['dce'] + (['guodu'] if day == last and 'guodu' in data else []), board='both_prices_match_prior_dce_parameter_row',
                           settlement_basis_day=prior, prior_oi=previous_oi, close_oi=oi,
                           session_position_limit_lots=prior_quota, closing_table_position_limit_lots=close_quota)
    verification = dict(week_ending=last, observed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                        input_sha256=doc['input_sha256'], adopted_inputs_sha256=hashlib.sha256(
                            adopted_bytes).hexdigest(),
                        sources=source_index, contracts=contracts)
    write_json(output, verification)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', type=Path)
    parser.add_argument('source_cache', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--candidate-pack', type=Path,
                        help='Original adopted v3 futures pack; defaults to the full input pack')
    parser.add_argument('--rb-rule-url', help='Effective SHFE rebar product rule, article 47')
    parser.add_argument('--dce-rule-url', help='Effective DCE position rules for soybean meal')
    args = parser.parse_args()
    verify(args.pack, args.candidate_pack or args.pack, args.source_cache,
           args.output, args.rb_rule_url, args.dce_rule_url)
