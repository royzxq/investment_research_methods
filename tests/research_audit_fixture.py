"""Explicit offline assumptions for delivery tests; no investment calibration."""


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
    return audit
