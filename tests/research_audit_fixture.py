"""Explicit offline assumptions for delivery tests; no investment calibration."""


def valuation_review_for(document):
    return dict(base_case='offline neutral operating path, not a probability quantile',
                method_choice='offline PE applicable to stable recurring earnings',
                pe_crosscheck='offline earnings basis and cash distribution, not market calibration',
                market_check=dict(price=25, as_of=document['meta']['valuation_date'],
                    source='offline close', explanation='offline difference in earnings assumptions'),
                reverse_dcf=dict(status='not_applicable', reason='offline stable PE case; no FCFF model', cases=[]))


def audit_for(document):
    audit = {
        'schema_version': 'stock-research-audit/v1',
        'identity': {key: document['meta'][key] for key in ('code', 'generator', 'valuation_date', 'currency')},
        'valuation': {
            'kind': 'profit_pe', 'currency': 'CNY', 'amount_unit': '100_million',
            'shares': 1_000_000_000, 'fx_to_quote': 1, 'horizon': 'offline normal year',
            'profit_basis': 'offline recurring attributable profit',
            'scenarios': {
                'low': dict(revenue=100, net_margin=.20, adjustments=[], profit=20, pe=10, equity_value=200),
                'base': dict(revenue=100, net_margin=.24, adjustments=[], profit=24, pe=10, equity_value=240),
                'high': dict(revenue=100, net_margin=.30, adjustments=[], profit=30, pe=10, equity_value=300),
            },
        },
        'baseline': None,
        'discounts': {
            key: dict(value=.5 if key == 'd_base' else 0,
                      range=[.4, .5] if key == 'd_base' else [0, 0],
                      risk_ids=['estimation'] if key == 'd_base' else [],
                      reason='explicit offline assumption',
                      change=dict(kind='initial', reason='offline initial study', evidence=[]))
            for key in ('d_base', 'r_chip', 'r_v5', 'r_gov', 'r_terminal')
        },
        'risks': [dict(id='estimation', description='offline model uncertainty', owner='d_base',
                       scope='not in operating assumptions', source='offline fixture')],
        'constraints': [], 'release_all_of': [],
        'p1_basis': {key: key for key, value in (document['price_map']['p1'] or {}).items() if value is not None},
    }
    mode = document['price_map']['mode']
    if mode in ('frozen', 'rejected', 'unavailable'):
        audit['constraints'] = [dict(id='offline_gate', effect={'frozen':'freeze', 'rejected':'reject', 'unavailable':'unavailable'}[mode],
                                    status='blocking', reason='explicit offline gate', release_conditions=['offline review'])]
        audit['release_all_of'] = ['offline_gate']
    if document['meta']['schema_version'] == 'stock-research/v4':
        audit['schema_version'] = 'stock-research-audit/v2'
        old_ids = audit['release_all_of']
        audit['release_all_of'] = dict(entry=old_ids[:], add=old_ids[:], holding=[])
        if mode in ('tracking', 'observation'):
            audit['constraints'] = [dict(id='RESEARCH_ELIGIBILITY', effect='eligibility', status='unknown',
                reason='offline missing qualification', release_conditions=['offline qualification review'])]
            audit['release_all_of'] = dict(entry=['RESEARCH_ELIGIBILITY'], add=['RESEARCH_ELIGIBILITY'], holding=[])
        for rule in audit['constraints']:
            rule['scope'] = ['entry', 'add']
            rule['action'] = rule.pop('effect')
            rule['lifecycle'] = 'persistent'
    return audit


def input_basis_for(document):
    return {key: dict(status='resolved', affects='p1' if key == 'residual_discount' else 'v50',
                     explanation='offline explicit evidence and reconciled assumptions', gaps=[],
                     evidence=[dict(source='offline fixture', as_of=document['meta']['valuation_date'])])
            for key in ('profit', 'investment', 'tax', 'capital', 'residual_discount')}


def neutral_review_for(audit, document):
    """Explicitly synthetic declarations for structural tests, never valuations."""
    if document['price_map']['v50'] is None:
        return None
    return dict(
        assumptions=[dict(topic=topic, adopted='offline bounded path', support='offline operating evidence',
            counterevidence='offline slower/faster recovery alternative', alternative='offline same-scope countercase',
            decision='offline selected path with limits', evidence=[dict(source='offline fixture', as_of=document['meta']['valuation_date'])])
            for topic in ('investment','cash_recovery','terminal','capital_cost','capital_scope')],
        capital_bridge=dict(status='not_applicable',scope='offline PE fixture',explanation='no explicit asset schedule in this synthetic test',rows=[],terminal_reconciliation='offline earnings/capital crosscheck only'),
        risk_pricing=[dict(risk_id=r['id'],cashflow='none',capital_bridge='none',capital_cost='none',p1='offline residual',residual_reason='offline independent residual') for r in audit['risks'] if r['owner']!='eligibility'],
        joint_case=dict(support='offline evidence',countercase='offline alternative combination',decision='offline no automatic worst-case stacking'),
        sensitivities=[dict(topic='joint_case',change='offline inability example',base_v50=document['price_map']['v50']['base'],alternative_v50=None,delta=None,calculation='synthetic fixture has no countermodel',limitation='no claim of investment validity')])
