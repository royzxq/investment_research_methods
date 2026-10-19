"""Check a report's explicit research calculations without changing its quotes.

The audit lives in the Markdown, not in the lightweight price-map schema.
This validates declared arithmetic and risk ownership, not economic truth or
the completeness of a model's disclosures. Historical reports remain readable.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, DecimalException, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re

try:
    from .stock_price_map import fields, json_number, load_json, number, require, string, validate_document
except ImportError:
    from stock_price_map import fields, json_number, load_json, number, require, string, validate_document

SCHEMA = 'stock-research-audit/v2'
LEGACY_SCHEMA = 'stock-research-audit/v1'
SUPPORTED_SCHEMAS = {LEGACY_SCHEMA, SCHEMA}
DISCOUNTS = ('d_base', 'r_chip', 'r_v5', 'r_gov', 'r_terminal')
SCENARIOS = ('low', 'base', 'high')
START, END = '<!-- research-audit:start -->', '<!-- research-audit:end -->'
VIEW_START, VIEW_END = '<!-- research-checks:start -->', '<!-- research-checks:end -->'


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'research audit: duplicate JSON key ' + key)
        result[key] = value
    return result


def extract_audit(report):
    require(report.count(START) == report.count(END) == 1,
            'research audit: require exactly one complete audit block')
    pattern = re.escape(START) + r'\s*```json\s*\n(.*?)\n```\s*' + re.escape(END)
    match = re.search(pattern, report, re.S)
    require(match is not None, 'research audit: malformed JSON block')
    try:
        return json.loads(match[1], parse_float=Decimal, object_pairs_hook=strict_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (ValueError, TypeError) as exc:
        raise ValueError('research audit: invalid JSON: ' + str(exc)) from exc


def text_list(value, label, *, empty=False):
    require(isinstance(value, list) and (empty or bool(value)), label + ': expected list')
    for item in value:
        string(item, label)
    require(len(value) == len(set(value)), label + ': duplicate item')
    return value


def decimal_text(value):
    return format(number(value, 'display').normalize(), 'f')


def cell(value):
    # Preserve the JSON source, but prevent multiline/table syntax in its view.
    return str(value).replace('|', '／').replace('\n', ' ').replace('\r', ' ')


def quote_round(value, currency):
    try:
        return value.quantize(Decimal('.001') if currency == 'HKD' else Decimal('.01'),
                              rounding=ROUND_HALF_UP)
    except DecimalException as exc:
        raise ValueError('research audit price outside calculable precision') from exc


def close(actual, expected, label, tolerance=Decimal('.005')):
    require(abs(number(actual, label) - expected) <= tolerance,
            f'research audit {label}: {actual} != calculated {expected}')


def baseline_values(audit, root):
    baseline = audit['baseline']
    if baseline is None:
        return None
    fields(baseline, {'report_path', 'sha256', 'discounts'}, 'baseline')
    require(root is not None, 'research audit baseline requires repository root')
    root = Path(root).resolve()
    relative = Path(string(baseline['report_path'], 'baseline.report_path'))
    require(not relative.is_absolute() and '..' not in relative.parts, 'baseline path escapes root')
    path = (root / relative).resolve()
    require(path.is_relative_to(root), 'baseline path escapes root')
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == baseline['sha256'], 'baseline report hash mismatch')
    report = raw.decode('utf-8')
    fields(baseline['discounts'], set(DISCOUNTS), 'baseline.discounts')
    result = {}
    prior = extract_audit(report) if START in report else None
    if prior is not None:
        require(isinstance(prior, dict), 'baseline audit must be an object')
        fields(prior, {'identity', 'discounts'}, 'baseline audit', optional=set(prior) - {'identity', 'discounts'})
        fields(prior['identity'], {'code', 'generator', 'valuation_date', 'currency'}, 'baseline identity')
        fields(prior['discounts'], set(DISCOUNTS), 'baseline discounts')
        for key in ('code', 'generator'):
            require(prior['identity'][key] == audit['identity'][key], 'baseline identity mismatch')
        require(prior['identity']['valuation_date'] <= audit['identity']['valuation_date'],
                'baseline is later than valuation cutoff')
    for key, entry in baseline['discounts'].items():
        fields(entry, {'value', 'quote'}, 'baseline.' + key, optional={'range'})
        quote = string(entry['quote'], 'baseline quote')
        require(quote in report, 'baseline quote absent from original report: ' + key)
        if entry['value'] is None:
            require(prior is None, 'existing audited baseline value cannot be discarded')
            require(entry.get('range') is None, 'missing historical discount cannot have a numeric range')
            result[key] = dict(value=None, range=None)
            continue
        value = number(entry['value'], 'baseline.' + key)
        require(0 <= value < 1, 'baseline discount outside [0,1)')
        if prior is not None:
            require(isinstance(prior['discounts'][key], dict), 'baseline discount must be an object')
            fields(prior['discounts'][key], {'value', 'range'}, 'baseline discount',
                   optional=set(prior['discounts'][key]) - {'value', 'range'})
            require(value == number(prior['discounts'][key]['value'], key),
                    'baseline value disagrees with original audit: ' + key)
        # Legacy values are human extracted, with their exact original quote.
        # Do not pretend a percentage somewhere in prose proves its semantics.
        bounds = prior['discounts'][key]['range'] if prior is not None else entry.get('range')
        if bounds is not None:
            require(isinstance(bounds, list) and len(bounds) == 2, 'baseline range requires two bounds')
            bounds = [number(item, 'baseline range') for item in bounds]
            require(0 <= bounds[0] <= value <= bounds[1] < 1, 'invalid baseline discount range')
        result[key] = dict(value=value, range=bounds)
    return result


def validate_audit(audit, document, *, root=None):
    validate_document(document)
    require(document['meta'].get('generator') in ('codex', 'claude'), 'research audit requires declared generator')
    fields(audit, {'schema_version', 'identity', 'valuation', 'discounts', 'risks',
                   'constraints', 'release_all_of', 'baseline', 'p1_basis'}, 'research audit')
    require(audit['schema_version'] in SUPPORTED_SCHEMAS, 'research audit schema mismatch')
    require((document['meta']['schema_version'] == 'stock-research/v4') == (audit['schema_version'] == SCHEMA), 'price/audit contract mismatch')
    fields(audit['identity'], {'code', 'generator', 'valuation_date', 'currency'}, 'audit identity')
    for key, value in audit['identity'].items():
        require(value == document['meta'][key], 'research audit identity mismatch: ' + key)
    pm = document['price_map']
    model = audit['valuation']
    require(isinstance(model, dict), 'valuation: expected object')
    kind = model.get('kind')
    values = None
    if kind == 'profit_pe':
        fields(model, {'kind', 'currency', 'amount_unit', 'shares', 'fx_to_quote',
                       'horizon', 'profit_basis', 'scenarios'}, 'valuation')
        require(model['amount_unit'] == '100_million', 'profit_pe uses explicit 100_million units')
        string(model['currency'], 'valuation.currency')
        string(model['horizon'], 'valuation.horizon')
        string(model['profit_basis'], 'valuation.profit_basis')
        shares = number(model['shares'], 'shares', positive=True)
        require(shares == shares.to_integral_value(), 'shares must be actual whole shares')
        fx = number(model['fx_to_quote'], 'fx_to_quote', positive=True)
        if model['currency'] == document['meta']['currency']:
            require(fx == 1, 'same-currency fx must be 1')
        fields(model['scenarios'], set(SCENARIOS), 'scenarios')
        values = {}
        for label, row in model['scenarios'].items():
            fields(row, {'revenue', 'net_margin', 'adjustments', 'profit', 'pe', 'equity_value'}, label)
            revenue = number(row['revenue'], label + '.revenue', positive=True)
            margin = number(row['net_margin'], label + '.net_margin')
            require(-1 <= margin <= 1, 'net_margin uses fraction, not percent points')
            require(isinstance(row['adjustments'], list), label + '.adjustments must be a list')
            adjustment, adjustment_ids = Decimal(0), set()
            for item in row['adjustments']:
                fields(item, {'id', 'amount', 'reason', 'source'}, 'profit adjustment')
                ident = string(item['id'], 'adjustment.id')
                require(ident not in adjustment_ids, 'duplicate profit adjustment')
                adjustment_ids.add(ident)
                string(item['reason'], 'adjustment.reason')
                string(item['source'], 'adjustment.source')
                adjustment += number(item['amount'], 'adjustment.amount')
            profit = revenue * margin + adjustment
            close(row['profit'], profit, label + '.profit')
            pe = number(row['pe'], label + '.pe', positive=True)
            require(profit > 0, 'profit_pe requires positive normalized earnings')
            equity = number(row['profit'], label + '.profit') * pe
            close(row['equity_value'], equity, label + '.equity_value')
            values[label] = number(row['equity_value'], label + '.equity_value') * Decimal(100_000_000) / shares * fx
            require(pm['v50'] is not None, 'profit_pe requires quoted V50')
            require(quote_round(values[label], document['meta']['currency']) == number(pm['v50'][label], label),
                    'research audit V50 mismatch: ' + label)
    else:
        fields(model, {'kind', 'reason'} | ({'unrounded_v50'} if kind == 'other' else set()), 'valuation')
        require(kind in ('other', 'unavailable'), 'unsupported audit valuation kind')
        string(model['reason'], 'valuation.reason')
        if kind == 'unavailable':
            require(pm['p1'] is None, 'unavailable valuation cannot retain new P1')
        else:
            fields(model['unrounded_v50'], set(SCENARIOS), 'unrounded_v50')
            require(pm['v50'] is not None, 'other valuation requires V50')
            values = {key: number(value, 'unrounded_v50', positive=True)
                      for key, value in model['unrounded_v50'].items()}
            for key, value in values.items():
                require(quote_round(value, document['meta']['currency']) == number(pm['v50'][key], 'v50'),
                        'research audit unrounded V50 mismatch: ' + key)

    require(isinstance(audit['risks'], list), 'risks: expected list')
    risks = {}
    for risk in audit['risks']:
        fields(risk, {'id', 'description', 'owner', 'scope', 'source'}, 'risk')
        ident = string(risk['id'], 'risk.id')
        require(ident not in risks, 'duplicate risk ID: ' + ident)
        require(risk['owner'] in (*DISCOUNTS, 'revenue', 'margin', 'multiple', 'eligibility'),
                'risk owner must be a single valuation/eligibility/discount bucket')
        for key in ('description', 'scope', 'source'):
            string(risk[key], 'risk.' + key)
        risks[ident] = risk
    previous = baseline_values(audit, root)
    fields(audit['discounts'], set(DISCOUNTS), 'discounts')
    factor, charged = Decimal(1), set()
    for key, entry in audit['discounts'].items():
        fields(entry, {'value', 'range', 'risk_ids', 'reason', 'change'}, key)
        value = number(entry['value'], key)
        require(0 <= value < 1, key + ' outside [0,1)')
        bounds = entry['range']
        require(isinstance(bounds, list) and len(bounds) == 2, key + ': range requires two bounds')
        low, high = (number(item, key + '.range') for item in bounds)
        require(0 <= low <= value <= high < 1, key + ': value outside justified range')
        string(entry['reason'], key + '.reason')
        ids = text_list(entry['risk_ids'], key + '.risk_ids', empty=value == 0)
        require(value > 0 or not ids, 'zero discount must not charge risk IDs')
        for ident in ids:
            require(ident in risks and risks[ident]['owner'] == key,
                    'risk already absorbed elsewhere or wrong owner: ' + ident)
            require(ident not in charged, 'risk charged more than once: ' + ident)
            charged.add(ident)
        change = entry['change']
        fields(change, {'kind', 'reason', 'evidence'}, key + '.change')
        string(change['reason'], key + '.change.reason')
        text_list(change['evidence'], key + '.change.evidence', empty=True)
        if previous is None or previous[key]['value'] is None:
            require(change['kind'] == 'initial', 'no baseline: mark discount as initial')
        elif value == previous[key]['value'] and (previous[key]['range'] is None or [low, high] == previous[key]['range']):
            require(change['kind'] == 'unchanged', 'unchanged discount requires unchanged classification')
        else:
            require(change['kind'] in ('new_evidence', 'correction', 'model_change', 'method_change'),
                    'discount drift without classified justification: ' + key)
            require(change['evidence'], 'changed discount requires evidence/correction reference: ' + key)
        factor *= 1 - value
    require({ident for ident, risk in risks.items() if risk['owner'] in DISCOUNTS} == charged,
            'residual risk must be charged exactly once, or assigned to its actual non-price owner')
    fields(audit['p1_basis'], set((pm['p1'] or {}).keys()) - ({'base'} if (pm['p1'] or {}).get('base') is None else set()), 'p1_basis')
    for quote, scenario in audit['p1_basis'].items():
        require(values is not None and scenario in SCENARIOS, 'P1 requires an explicit scenario basis')
        require(quote_round(values[scenario] * factor, document['meta']['currency']) == number(pm['p1'][quote], 'P1'),
                'research audit P1 formula disagrees with explicit report quote: ' + quote)

    if audit['schema_version'] == SCHEMA:
        unresolved = validate_scoped_controls(audit, document, root=root)
        return {'schema_version': SCHEMA, 'status': 'passed', 'discount_factor': float(factor),
                'unresolved_constraints': unresolved,
                'scope': 'declared calculations, typed controls and state consistency; not economic truth or execution'}
    require(isinstance(audit['constraints'], list), 'constraints: expected list')
    unresolved, ids, effects = set(), set(), set()
    for constraint in audit['constraints']:
        fields(constraint, {'id', 'effect', 'status', 'reason', 'release_conditions'}, 'constraint', optional={'clearance'})
        ident = string(constraint['id'], 'constraint.id')
        require(ident not in ids, 'duplicate constraint ID')
        ids.add(ident)
        effect, status = constraint['effect'], constraint['status']
        require(effect in ('freeze', 'eligibility', 'reject', 'unavailable'), 'invalid constraint effect')
        require(status in ('blocking', 'unknown', 'clear', 'not_applicable'), 'invalid constraint status')
        string(constraint['reason'], 'constraint.reason')
        blocked = status in ('blocking', 'unknown')
        text_list(constraint['release_conditions'], 'release_conditions', empty=not blocked)
        if not blocked:
            continue
        unresolved.add(ident)
        effects.add(effect if status == 'blocking' else ('freeze' if effect == 'reject' else effect))
        require(pm['mode'] != 'buy_candidate', 'unresolved constraint forbids buy_candidate: ' + ident)
        if effect == 'freeze':
            require(pm['mode'] in ('frozen', 'rejected', 'unavailable'),
                    'freeze constraint cannot be hidden as tracking/observation: ' + ident)
        if effect == 'reject' and status == 'blocking':
            require(pm['mode'] == 'rejected', 'confirmed rejection requires rejected mode')
        if effect == 'unavailable':
            require(pm['p1'] is None, 'core valuation input missing: no new P1')
        if effect == 'reject' and status == 'unknown':
            require(pm['mode'] in ('frozen', 'rejected', 'unavailable'), 'unresolved red-line review requires freeze')
    release = text_list(audit['release_all_of'], 'release_all_of', empty=True)
    require(set(release) == unresolved,
            'release must require ALL unresolved constraints; no any-of or omitted blocker')
    for constraint in audit['constraints']:
        if constraint['id'] != 'D5' or constraint['status'] == 'not_applicable':
            continue
        clearance = constraint.get('clearance')
        fields(clearance, {'stage', 'evidence'}, 'D5.clearance')
        stage = clearance['stage']
        require(stage in ('deepening', 'unknown', 'waiting_review', 'rebuild_pending_company_review',
                          'rebuild_review_complete'), 'D5: invalid clearance stage')
        text_list(clearance['evidence'], 'D5.clearance.evidence', empty=True)
        if constraint['status'] == 'clear':
            require(stage == 'rebuild_review_complete' and bool(clearance['evidence']),
                    'D5: R21 exit/waiting is not full rebuilding and company review clearance')
        else:
            require(stage != 'rebuild_review_complete', 'D5 clearance stage disagrees with unresolved status')
    if pm['mode'] == 'frozen':
        require(bool(effects & {'freeze', 'unavailable'}), 'frozen mode requires an explicit unresolved freeze/core constraint')
    if pm['mode'] == 'rejected':
        require('reject' in effects, 'rejected mode requires a confirmed rejection constraint')
    if pm['mode'] == 'unavailable':
        require('unavailable' in effects, 'unavailable mode requires an explicit core-input constraint')
    return {'schema_version': LEGACY_SCHEMA, 'status': 'passed', 'discount_factor': float(factor),
            'unresolved_constraints': sorted(unresolved),
            'scope': 'declared calculations, risk ownership and state consistency; not source truth or economic validity'}


def preserves_active_action(previous, current):
    """Compare only declared conservative transitions, not an action total order.

    Missing core inputs and confirmed rejection have distinct release evidence;
    a different restriction cannot silently replace either under the same ID.
    Legacy audit/v1 stores the same exposure action as ``effect``.
    """
    old_action = previous.get('action', previous.get('effect'))
    conservative_actions = {
        'eligibility': {'eligibility', 'freeze', 'reject', 'unavailable', 'invalidated', 'exit_required'},
        'freeze': {'freeze', 'reject'},
        'reject': {'reject'},
        'unavailable': {'unavailable'},
        'review_holding': {'review_holding', 'invalidated', 'exit_required'},
        'invalidated': {'invalidated', 'exit_required'},
        'exit_required': {'exit_required'},
    }
    if current['action'] not in conservative_actions.get(old_action, set()):
        return False
    if previous['status'] == 'blocking' and old_action in {'reject', 'invalidated', 'exit_required'}:
        return current['status'] == 'blocking'
    return True


def validate_scoped_controls(audit, document, *, root=None):
    """Audit is authoritative; lightweight controls are a checked projection."""
    scopes = {'entry', 'add', 'holding'}
    actions = {'freeze', 'eligibility', 'reject', 'unavailable', 'review_holding', 'invalidated', 'exit_required'}
    require(isinstance(audit['constraints'], list), 'constraints: expected list')
    rules = {}
    unresolved = {scope: [] for scope in scopes}
    for rule in audit['constraints']:
        fields(rule, {'id', 'scope', 'status', 'action', 'reason', 'release_conditions'}, 'constraint', optional={'clearance', 'lifecycle'})
        ident = string(rule['id'], 'constraint.id')
        require(ident not in rules, 'duplicate constraint ID')
        rules[ident] = rule
        targets = text_list(rule['scope'], 'constraint.scope')
        require(set(targets) <= scopes, 'invalid constraint scope')
        status, action = rule['status'], rule['action']
        require(isinstance(status, str) and status in {'blocking', 'unknown', 'clear', 'not_applicable'}, 'invalid constraint status')
        require(isinstance(action, str) and action in actions, 'invalid constraint action')
        string(rule['reason'], 'constraint.reason')
        active = status in {'blocking', 'unknown'}
        require(rule.get('lifecycle', 'persistent') in {'persistent', 'runtime', 'observation'}, 'invalid constraint lifecycle')
        require(not active or rule.get('lifecycle', 'persistent') == 'persistent',
                'only persistent research restrictions enter unresolved controls')
        text_list(rule['release_conditions'], 'release_conditions', empty=not active)
        if action in {'freeze', 'reject', 'unavailable'}:
            require({'entry', 'add'} <= set(targets), 'global restriction must cover entry and add')
        if action in {'review_holding', 'invalidated', 'exit_required'}:
            require('holding' in targets, 'holding action must include holding scope')
        if action in {'invalidated', 'exit_required'} and status == 'blocking':
            require(scopes <= set(targets), 'confirmed invalidation/exit must block entry and add')
        if action == 'review_holding':
            require(set(targets) == {'holding'}, 'holding review does not silently restrict exposure')
        if action == 'eligibility':
            require(set(targets) <= {'entry', 'add'}, 'eligibility restriction has exposure scope')
        if active:
            for scope in targets:
                unresolved[scope].append(ident)
        clearance = rule.get('clearance')
        if status == 'clear' or clearance is not None:
            fields(clearance, {'evidence'}, 'clearance', optional={'stage', 'covers'})
            text_list(clearance['evidence'], 'clearance.evidence', empty=status != 'clear')
            if 'covers' in clearance:
                coverage = text_list(clearance['covers'], 'clearance.covers', empty=True)
                require(all(re.fullmatch(r'[0-9a-f]{64}', item) for item in coverage), 'invalid clearance claim coverage')
        if ident == 'D5' and status != 'not_applicable':
            fields(clearance, {'stage', 'evidence'}, 'D5.clearance', optional={'covers'})
            require(clearance['stage'] in {'deepening', 'unknown', 'waiting_review', 'rebuild_pending_company_review', 'rebuild_review_complete'}, 'invalid D5 stage')
            if status == 'clear':
                require(clearance['stage'] == 'rebuild_review_complete' and clearance['evidence'], 'D5 waiting is not full clearance')
            else:
                require(clearance['stage'] != 'rebuild_review_complete', 'D5 clearance contradicts unresolved status')
    fields(audit['release_all_of'], scopes, 'release_all_of')
    for scope in scopes:
        text_list(audit['release_all_of'][scope], 'release_all_of.' + scope, empty=True)
        require(set(audit['release_all_of'][scope]) == set(unresolved[scope]), 'release must include ALL scope blockers: ' + scope)
    # A fresh eligible summary cannot erase a previously unresolved restriction.
    if audit['baseline'] is not None:
        prior_text = (Path(root) / audit['baseline']['report_path']).read_text(encoding='utf-8')
        if START in prior_text:
            prior = extract_audit(prior_text)
            for old in prior.get('constraints', []):
                if old.get('status') not in {'blocking', 'unknown'}:
                    continue
                ident = old['id']
                require(ident in rules, 'unresolved baseline constraint omitted: ' + ident)
                row = rules[ident]
                old_scopes = set(old.get('scope', ['entry', 'add']))
                if row['status'] in {'blocking', 'unknown'}:
                    require(old_scopes <= set(row['scope']), 'unresolved baseline scope narrowed: ' + ident)
                    require(preserves_active_action(old, row),
                            'unresolved baseline restriction must be explicitly cleared before downgrade or replacement: ' + ident)
                else:
                    clearance = row.get('clearance')
                    require(isinstance(clearance, dict) and bool(clearance.get('evidence')), 'baseline release requires evidence: ' + ident)
                    if 'covers' in clearance:
                        require(constraint_claim_sha256(old) in clearance['covers'],
                                'baseline release coverage misses unresolved claim: ' + ident)
                    if ident == 'D5':
                        require(clearance.get('stage') == 'rebuild_review_complete',
                                'D5 baseline release requires completed rebuilding and company review')
    pm = document['price_map']
    active_entry = [rules[k] for k in unresolved['entry']]
    if any(r['action'] == 'reject' and r['status'] == 'blocking' for r in active_entry):
        require(pm['mode'] == 'rejected', 'confirmed rejection requires rejected mode')
    if any(r['action'] == 'freeze' or (r['action'] == 'reject' and r['status'] == 'unknown') for r in active_entry):
        require(pm['mode'] in {'frozen', 'rejected', 'unavailable'}, 'freeze cannot hide in observation')
    if any(r['action'] == 'unavailable' for r in active_entry):
        require(pm['p1'] is None, 'core input unavailable cannot retain new P1')
    required = {'frozen': {'freeze', 'unavailable', 'reject'}, 'rejected': {'reject'}, 'unavailable': {'unavailable'}}
    if pm['mode'] in required:
        require(any(r['action'] in required[pm['mode']] for r in active_entry), 'restricted mode needs actual entry constraint')
    controls = document['research_controls']
    for scope in ('entry', 'add'):
        rows = [rules[k] for k in unresolved[scope]]
        expected = 'blocked' if any(r['status'] == 'blocking' for r in rows) else ('unknown' if rows else 'eligible')
        require(controls[scope]['status'] == expected, 'control summary differs from audit: ' + scope)
        require(set(controls[scope]['refs']) == set(unresolved[scope]), 'control refs must cover exact scope blockers: ' + scope)
    hold = [rules[k] for k in unresolved['holding']]
    confirmed = {r['action'] for r in hold if r['status'] == 'blocking'}
    expected = ('exit_required' if 'exit_required' in confirmed else 'invalidated' if 'invalidated' in confirmed
                else 'review_required' if hold else 'normal')
    allowed = {expected, 'unknown'} if hold and all(r['status'] == 'unknown' for r in hold) else {expected}
    require(controls['holding']['status'] in allowed, 'holding summary differs from audit')
    require(set(controls['holding']['refs']) == set(unresolved['holding']), 'holding refs differ from audit')
    for item in document['monitoring']:
        if item['kind'] == 'general':
            continue
        if item['state'] == 'watching' and item['id'] not in rules:
            continue
        require(item['id'] in rules, 'control monitoring requires audit ID: ' + item['id'])
        rule = rules[item['id']]
        allowed_states = {'triggered': {'blocking'}, 'unknown': {'unknown'}, 'cleared': {'clear', 'not_applicable'}, 'watching': {'clear', 'not_applicable'}}
        require(rule['status'] in allowed_states[item['state']], 'monitoring state differs from audit')
        if item['state'] == 'cleared':
            require(bool((rule.get('clearance') or {}).get('evidence')), 'cleared monitoring requires evidence')
        target = {'entry_constraint': 'entry', 'add_constraint': 'add', 'thesis_invalidation': 'holding', 'exit_condition': 'holding'}[item['kind']]
        require(target in rule['scope'], 'monitoring kind differs from audit scope')
    return {scope: sorted(ids) for scope, ids in unresolved.items()}


def render_checks(audit, document):
    """Single human-readable calculation table, bound to the audit inputs."""
    model, pm = audit['valuation'], document['price_map']
    lines = [VIEW_START, '研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：']
    if model['kind'] == 'profit_pe':
        lines += ['', '| 情景 | 收入 | 经常净利率 | 利润调整 | 经常归母利润 | PE | 权益价值 | V50 |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|']
        for key in SCENARIOS:
            row = model['scenarios'][key]
            adjustment = sum((number(item['amount'], 'adjustment') for item in row['adjustments']), Decimal(0))
            entries = [key, row['revenue'], decimal_text(number(row['net_margin'], 'margin') * 100) + '%',
                       adjustment, row['profit'], row['pe'], row['equity_value'], pm['v50'][key]]
            lines.append('| ' + ' | '.join(cell(decimal_text(v) if isinstance(v, (Decimal, float, int)) else v) for v in entries) + ' |')
    else:
        lines += ['', '估值链适用性：' + cell(model['kind'] + '；' + model['reason'])]
    lines += ['', '| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |', '|---|---:|---|---|---|']
    factor = Decimal(1)
    for key in DISCOUNTS:
        entry = audit['discounts'][key]
        value = number(entry['value'], key)
        factor *= 1 - value
        bounds = '—'.join(decimal_text(number(v, key) * 100) + '%' for v in entry['range'])
        lines.append(f"| {key} | {decimal_text(value * 100)}% | {bounds} | {cell(', '.join(entry['risk_ids']) or '无额外扣减')} | {cell(entry['change']['kind'])} |")
    lines += ['', '总折扣乘数：' + decimal_text(factor) + '；用途：' + pm['mode'] + '。',
              '明确报价：P1=' + json.dumps(pm['p1'], ensure_ascii=False, sort_keys=True, default=json_number) +
              ('；T1=' + json.dumps(pm['t1'], ensure_ascii=False, sort_keys=True, default=json_number) if audit['schema_version'] == SCHEMA else '；P2=' + json.dumps(pm['p2'], ensure_ascii=False, sort_keys=True, default=json_number)) + '。',
              '', '| 约束 | 作用 | 状态 | 依据 |', '|---|---|---|---|']
    for row in audit['constraints']:
        values = [row[k] for k in ('id', 'action' if audit['schema_version'] == SCHEMA else 'effect', 'status', 'reason')]
        if audit['schema_version'] == SCHEMA:
            values[1] = ','.join(row['scope']) + ': ' + values[1]
        lines.append('| ' + ' | '.join(cell(v) for v in values) + ' |')
    if audit['schema_version'] == SCHEMA:
        lines += ['', '| 范围 | 当前研究状态 | 未解约束ID |', '|---|---|---|']
        for scope in ('entry', 'add', 'holding'):
            control = document['research_controls'][scope]
            lines.append('| ' + ' | '.join(cell(v) for v in (scope, control['status'], ', '.join(control['refs']) or '无')) + ' |')
    lines += ['', '恢复前须同时解除全部仍有效约束：' + cell(json.dumps(audit['release_all_of'], ensure_ascii=False, sort_keys=True) if audit['schema_version'] == SCHEMA else ('、'.join(audit['release_all_of']) or '无未解约束')) + '。', VIEW_END]
    return '\n'.join(lines)


def constraint_claim_sha256(rule):
    """Shared cross-repository content identity; not proof of evidence truth."""
    content = {k:v for k,v in rule.items() if k not in {
        'scope', 'status', 'clearance', 'variants', 'claims', 'latest_review', 'conflicting_evidence'}}
    if content.get('lifecycle') == 'persistent':
        content.pop('lifecycle')
    raw = json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(',', ':'),
                     allow_nan=False, default=json_number).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_report(report, document, *, root=None, expected_baseline=None, require_lifecycle=False):
    audit = extract_audit(report)
    result = validate_audit(audit, document, root=root)
    if require_lifecycle:
        require(audit['schema_version'] == SCHEMA, 'new controls semantics require audit-v2')
        for rule in audit['constraints']:
            require('lifecycle' in rule, 'new controls require explicit lifecycle')
    if expected_baseline is not None:
        require(audit['baseline'] is not None, 'prepared research baseline must not be dropped')
        for key in ('report_path', 'sha256'):
            require(audit['baseline'][key] == expected_baseline[key], 'prepared research baseline mismatch: ' + key)
    require(report.count(VIEW_START) == report.count(VIEW_END) == 1,
            'research audit: require exactly one rendered calculation view')
    require(render_checks(audit, document) in report,
            'research audit: visible calculation view differs from audited inputs/quotes')
    return result


def isolate_report(report, document, *, root=None):
    """Update only isolation state in a derived report; source bytes stay intact."""
    audit = extract_audit(report)
    require('METHOD_COMPATIBILITY' not in {row['id'] for row in audit['constraints']},
            'method compatibility isolation already recorded')
    rule = dict(id='METHOD_COMPATIBILITY', status='blocking',
        reason='发布前方法或采纳证据接续变化，适用性待复核；保留原价格',
        release_conditions=['取得兼容性核验及本公司受影响判断复评凭证'])
    if audit['schema_version'] == SCHEMA:
        rule.update(action='freeze', scope=['entry', 'add'], lifecycle='persistent')
        for scope in ('entry', 'add'):
            audit['release_all_of'][scope].append('METHOD_COMPATIBILITY')
    else:
        rule['effect'] = 'freeze'
        audit['release_all_of'].append('METHOD_COMPATIBILITY')
    audit['constraints'].append(rule)
    pattern = re.escape(START) + r'.*?' + re.escape(END)
    replacement = START + '\n```json\n' + json.dumps(audit, ensure_ascii=False, indent=2,
        allow_nan=False, default=json_number) + '\n```\n' + END
    report = re.sub(pattern, lambda _: replacement, report, count=1, flags=re.S)
    report = re.sub(re.escape(VIEW_START) + r'.*?' + re.escape(VIEW_END),
                    lambda _: render_checks(audit, document), report, count=1, flags=re.S)
    validate_report(report, document, root=root)
    return report


def render_report_block(audit, document, *, root=None):
    validate_audit(audit, document, root=root)
    return (render_checks(audit, document) + '\n\n<details><summary>计算、风险归属与解除条件审计输入</summary>\n\n'
            + START + '\n```json\n' + json.dumps(audit, ensure_ascii=False, indent=2, allow_nan=False, default=json_number)
            + '\n```\n' + END + '\n\n</details>\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'render', 'claims'))
    parser.add_argument('--price-map', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--audit', type=Path)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--require-lifecycle', action='store_true', help='new controls semantics; legacy check remains readable')
    args = parser.parse_args(argv)
    try:
        if args.command == 'claims':
            require(args.audit is not None, 'claims requires --audit')
            rules = load_json(args.audit)['constraints']
            print(json.dumps({r['id']:constraint_claim_sha256(r) for r in rules}, ensure_ascii=False))
            return
        require(args.price_map is not None, 'check/render requires --price-map')
        document = load_json(args.price_map)
        if args.command == 'check':
            require(args.report is not None, 'check requires --report')
            print(json.dumps(validate_report(args.report.read_text(), document, root=args.root,
                                            require_lifecycle=args.require_lifecycle), ensure_ascii=False))
        else:
            require(args.audit is not None, 'render requires --audit')
            print(render_report_block(load_json(args.audit), document, root=args.root))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, 'Research consistency failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
