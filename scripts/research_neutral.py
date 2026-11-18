"""Validate declared neutral-case review; never select a price or risk appetite.

The review records economic judgment and reproducible sensitivities. Arithmetic
and coverage are checkable; evidence quality and neutrality are not inferred.
"""
from datetime import date
from decimal import Decimal
import re

try:
    from .stock_price_map import fields, number, require, string
except ImportError:
    from stock_price_map import fields, number, require, string

TOPICS = {'investment', 'cash_recovery', 'terminal', 'capital_cost', 'capital_scope'}


def period_key(value):
    """Sort calendar dates or explicit model-period indices, never mix them."""
    index = re.fullmatch(r't([1-9][0-9]*)', value)
    if index:
        return ('model_period', int(index[1]))
    match = re.fullmatch(r'(\d{4})(?:-?Q([1-4]))?', value)
    if match:
        year, quarter = int(match[1]), int(match[2] or 4)
        require(1 <= year <= 9999, 'invalid neutral capital period')
        return ('calendar', date(year, quarter * 3, (31 if quarter in (1, 4) else 30)))
    try:
        day = date.fromisoformat(value)
        require(day.isoformat() == value, 'invalid neutral capital period')
        return ('calendar', day)
    except (ValueError, TypeError) as exc:
        raise ValueError('neutral capital period must be YYYY, YYYYQ1–Q4, YYYY-MM-DD or tN') from exc


def validate(review, risks, document):
    if review is None:
        require(document['price_map']['v50'] is None,
                'neutral_review required for every adopted V50, including null P1')
        return
    fields(review, {'assumptions', 'capital_bridge', 'risk_pricing', 'joint_case', 'sensitivities'}, 'neutral_review')
    rows = review['assumptions']
    require(isinstance(rows, list), 'neutral_review.assumptions must be list')
    topics = []
    cutoff = date.fromisoformat(document['meta']['valuation_date'])
    for row in rows:
        fields(row, {'topic', 'adopted', 'support', 'counterevidence', 'alternative', 'decision', 'evidence'}, 'neutral assumption')
        topics.append(string(row['topic'], 'neutral assumption.topic'))
        for key in ('adopted', 'support', 'counterevidence', 'alternative', 'decision'):
            string(row[key], 'neutral assumption.' + key)
        require(isinstance(row['evidence'], list) and row['evidence'], 'neutral assumption needs evidence')
        for source in row['evidence']:
            fields(source, {'source', 'as_of'}, 'neutral evidence')
            string(source['source'], 'neutral evidence.source')
            try:
                day = date.fromisoformat(source['as_of'])
                require(day.isoformat() == source['as_of'] and day <= cutoff, 'neutral evidence exceeds cutoff')
            except (ValueError, TypeError) as exc:
                raise ValueError('neutral evidence invalid date/cutoff') from exc
    require(len(topics) == len(TOPICS) and set(topics) == TOPICS, 'neutral review must cover five distinct topics')

    bridge = review['capital_bridge']
    fields(bridge, {'status', 'scope', 'explanation', 'rows', 'terminal_reconciliation'}, 'neutral capital_bridge')
    status = string(bridge['status'], 'neutral capital_bridge.status')
    require(status in {'reconciled', 'approximate', 'unavailable', 'not_applicable'}, 'invalid neutral capital bridge status')
    for key in ('scope', 'explanation', 'terminal_reconciliation'):
        string(bridge[key], 'neutral capital_bridge.' + key)
    require(isinstance(bridge['rows'], list), 'neutral capital rows must be list')
    if status in {'reconciled', 'approximate'}:
        require(bool(bridge['rows']), 'reconciled/approximate capital bridge requires numeric rows')
    else:
        require(not bridge['rows'], 'unavailable/not_applicable bridge cannot assert numeric reconciliation')
    seen = set()
    previous = {}
    previous_period = {}
    for row in bridge['rows']:
        fields(row, {'scope', 'period', 'opening', 'capex', 'da', 'other', 'closing', 'other_reason'}, 'neutral capital row')
        for key in ('scope', 'period', 'other_reason'):
            string(row[key], 'neutral capital row.' + key)
        identity = (row['scope'], row['period'])
        require(identity not in seen, 'duplicate neutral capital scope/period')
        seen.add(identity)
        period = period_key(row['period'])
        if row['scope'] in previous_period:
            require(period[0] == previous_period[row['scope']][0], 'neutral capital period bases cannot be mixed')
            require(period > previous_period[row['scope']], 'neutral capital periods must be chronological')
        previous_period[row['scope']] = period
        values = {key: number(row[key], 'neutral capital.' + key) for key in ('opening', 'capex', 'da', 'other', 'closing')}
        require(all(values[key] >= 0 for key in ('opening', 'capex', 'da', 'closing')), 'negative neutral productive asset/capex/da')
        calculated = values['opening'] + values['capex'] - values['da'] + values['other']
        require(abs(calculated - values['closing']) <= Decimal('.005'), 'neutral capital rollforward does not reconcile')
        if row['scope'] in previous:
            require(abs(previous[row['scope']] - values['opening']) <= Decimal('.005'), 'neutral capital periods do not connect')
        previous[row['scope']] = values['closing']

    priced_risks = {row['id'] for row in risks if row['owner'] != 'eligibility'}
    require(isinstance(review['risk_pricing'], list), 'neutral risk_pricing must be list')
    covered = []
    for row in review['risk_pricing']:
        fields(row, {'risk_id', 'cashflow', 'capital_bridge', 'capital_cost', 'p1', 'residual_reason'}, 'neutral risk pricing')
        covered.append(string(row['risk_id'], 'neutral risk pricing.risk_id'))
        for key in ('cashflow', 'capital_bridge', 'capital_cost', 'p1', 'residual_reason'):
            string(row[key], 'neutral risk pricing.' + key)
    require(len(covered) == len(set(covered)) and set(covered) == priced_risks,
            'neutral risk pricing must cover each priced risk exactly once')

    joint = review['joint_case']
    fields(joint, {'support', 'countercase', 'decision'}, 'neutral joint_case')
    for key in joint:
        string(joint[key], 'neutral joint_case.' + key)
    require(isinstance(review['sensitivities'], list) and review['sensitivities'], 'neutral sensitivity or explicit inability required')
    for row in review['sensitivities']:
        fields(row, {'topic', 'change', 'base_v50', 'alternative_v50', 'delta', 'calculation', 'limitation'}, 'neutral sensitivity')
        topic = string(row['topic'], 'neutral sensitivity.topic')
        require(topic in TOPICS | {'joint_case'}, 'invalid neutral sensitivity topic')
        for key in ('change', 'calculation', 'limitation'):
            string(row[key], 'neutral sensitivity.' + key)
        if row['alternative_v50'] is None:
            require(row['delta'] is None, 'unquantified neutral sensitivity cannot have delta')
        else:
            base = number(row['base_v50'], 'neutral sensitivity base')
            alt = number(row['alternative_v50'], 'neutral sensitivity alternative')
            require(abs(number(row['delta'], 'neutral sensitivity delta') - (alt - base)) <= Decimal('.005'),
                    'neutral sensitivity delta mismatch')
        price = document['price_map']['v50']
        if price is not None:
            require(abs(number(row['base_v50'], 'neutral sensitivity base') - number(price['base'], 'adopted base')) <= Decimal('.005'),
                    'neutral sensitivity base differs from adopted V50')


def render(review, cell):
    if review is None:
        return []
    lines = ['', '已给价中性校准（结构/算术检查不证明经济中性）：',
             '', '| 假设 | 采用路径 | 依据 | 反证 | 替代及取舍 |', '|---|---|---|---|---|']
    for row in review['assumptions']:
        lines.append('| ' + ' | '.join(cell(row[k]) for k in ('topic', 'adopted', 'support', 'counterevidence')) + ' | ' + cell(row['alternative'] + '；' + row['decision']) + ' |')
    bridge = review['capital_bridge']
    lines += ['', '生产性资本对账：' + cell(bridge['status'] + '；' + bridge['scope'] + '；' + bridge['explanation']),
              '', '| 范围 | 期间 | 期初 | CapEx | DA | 其他变化 | 期末 | 其他变化依据 |', '|---|---|---:|---:|---:|---:|---:|---|']
    for row in bridge['rows']:
        lines.append('| ' + ' | '.join(cell(row[k]) for k in ('scope', 'period', 'opening', 'capex', 'da', 'other', 'closing', 'other_reason')) + ' |')
    lines += ['', '终值 IC 衔接：' + cell(bridge['terminal_reconciliation']),
              '', '| 风险 | 现金流 | 资本桥 | 资本成本 | P1 | 残余依据 |', '|---|---|---|---|---|---|']
    for row in review['risk_pricing']:
        lines.append('| ' + ' | '.join(cell(row[k]) for k in ('risk_id', 'cashflow', 'capital_bridge', 'capital_cost', 'p1', 'residual_reason')) + ' |')
    lines += ['', '联合基准：' + cell('；'.join(review['joint_case'].values())),
              '', '| 项目 | 改变 | 基准 V50 | 替代 V50 | 差额 | 计算及限制 |', '|---|---|---:|---:|---:|---|']
    for row in review['sensitivities']:
        lines.append('| ' + ' | '.join(cell(row[k]) for k in ('topic', 'change', 'base_v50', 'alternative_v50', 'delta')) + ' | ' + cell(row['calculation'] + '；' + row['limitation']) + ' |')
    return lines
