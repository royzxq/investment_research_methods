"""Versioned evidence/recovery gates shared by formal and isolated deliveries.

This checks evidence availability/binding and explicit control contradictions.
It cannot establish that a cited sentence supports an economic conclusion.
Old audit/price schemas and frozen delivery contracts are unchanged.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import unicodedata

try:
    from .stock_price_map import fields, require, string, json_number
except ImportError:
    from stock_price_map import fields, require, string, json_number

SCHEMA = 'stock-research-acceptance/v1'
START, END = '<!-- research-acceptance:start -->', '<!-- research-acceptance:end -->'
VIEW_START, VIEW_END = '<!-- research-acceptance-view:start -->', '<!-- research-acceptance-view:end -->'
INPUTS = ('exposure', 'cost_exposure', 'pass_through', 'ocf_bridge')
SCOPES = ('entry', 'add', 'holding')
MAX_SOURCE_BYTES = 4_000_000


def _object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'acceptance: duplicate JSON key ' + key)
        result[key] = value
    return result


def extract(report):
    require(report.count(START) == report.count(END) == 1,
            'acceptance: require exactly one complete acceptance block')
    match = re.search(re.escape(START) + r'\s*```json\s*\n(.*?)\n```\s*' + re.escape(END), report, re.S)
    require(match is not None, 'acceptance: malformed JSON block')
    try:
        return json.loads(match[1], object_pairs_hook=_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (ValueError, TypeError) as exc:
        raise ValueError('acceptance: invalid JSON: ' + str(exc)) from exc


def _ids(value, label):
    require(isinstance(value, list), label + ': expected list')
    for ident in value:
        string(ident, label)
    require(len(set(value)) == len(value), label + ': duplicate ID')
    return value


def _source(source, *, root, cutoff):
    fields(source, {'path', 'sha256', 'quote', 'as_of'}, 'R14 evidence source')
    relative = Path(string(source['path'], 'R14 source path'))
    require(not relative.is_absolute() and '..' not in relative.parts,
            'R14 evidence path must be repository relative')
    require(re.fullmatch(r'[0-9a-f]{64}', string(source['sha256'], 'R14 source hash')) is not None,
            'R14 evidence requires SHA256')
    string(source['quote'], 'R14 source quote')
    as_of = string(source['as_of'], 'R14 source as_of')
    require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', as_of) is not None,
            'R14 evidence date must be ISO date')
    try:
        date.fromisoformat(as_of)
    except ValueError as exc:
        raise ValueError('R14 evidence date invalid') from exc
    require(as_of <= cutoff, 'R14 evidence later than valuation cutoff')
    require(root is not None, 'R14 evidence verification requires root')
    root = Path(root).resolve()
    path = root / relative
    require(not any(p.is_symlink() for p in (path, *path.parents) if p != root and p.is_relative_to(root)),
            'R14 evidence symlinks forbidden')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_size <= MAX_SOURCE_BYTES,
                'R14 evidence must be a bounded regular UTF-8 source/extract')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(MAX_SOURCE_BYTES + 1)
        require(len(raw) <= MAX_SOURCE_BYTES, 'R14 evidence grew beyond bound')
    finally:
        os.close(fd)
    require(hashlib.sha256(raw).hexdigest() == source['sha256'], 'R14 evidence hash mismatch')
    try:
        text = raw.decode('utf-8')
    except UnicodeError as exc:
        raise ValueError('R14 evidence requires UTF-8 extract; retain original source separately') from exc
    require(source['quote'] in text, 'R14 evidence quote absent from bound source')


def validate_claims(acceptance, audit, *, root=None):
    fields(acceptance, {'schema_version', 'r14', 'recovery'}, 'research acceptance')
    require(acceptance['schema_version'] == SCHEMA, 'acceptance schema mismatch')
    require(audit['schema_version'] == 'stock-research-audit/v2', 'acceptance requires audit-v2')
    r14 = acceptance['r14']
    fields(r14, {'applicability', 'stress_test', 'constraint_ids', 'reason', 'inputs', 'calculation'}, 'R14 acceptance')
    require(r14['applicability'] in ('applicable', 'unknown', 'not_applicable'), 'R14 invalid applicability')
    require(r14['stress_test'] in ('passed', 'failed', 'unknown', 'not_applicable'), 'R14 invalid stress state')
    string(r14['reason'], 'R14 applicability/research reason')
    ids = _ids(r14['constraint_ids'], 'R14 constraint_ids')
    fields(r14['inputs'], set(INPUTS), 'R14 required inputs')
    for key, item in r14['inputs'].items():
        fields(item, {'status', 'sources', 'derivation'}, 'R14 input ' + key)
        require(item['status'] in ('supported', 'bounded', 'assumption', 'unknown'), 'R14 invalid input status')
        require(isinstance(item['sources'], list), 'R14 sources must be list')
        if item['derivation'] is not None:
            string(item['derivation'], 'R14 derivation')
        if item['status'] in ('supported', 'bounded'):
            require(bool(item['sources']), 'R14 supported/bounded input requires source evidence: ' + key)
        if item['status'] == 'bounded':
            require(item['derivation'] is not None, 'R14 source-derived bound requires bridge: ' + key)
        for source in item['sources']:
            _source(source, root=root, cutoff=audit['identity']['valuation_date'])
    if r14['calculation'] is not None:
        fields(r14['calculation'], {'scenario', 'report_quote'}, 'R14 calculation')
        string(r14['calculation']['scenario'], 'R14 scenario (existing canonical)')
        string(r14['calculation']['report_quote'], 'R14 calculation report quote')
    if r14['applicability'] == 'not_applicable':
        require(r14['stress_test'] == 'not_applicable' and not ids,
                'R14 not-applicable must not claim stress pass/fail or release a constraint')
    else:
        require(r14['stress_test'] != 'not_applicable', 'R14 required stress cannot be exempted')
        if r14['applicability'] == 'unknown':
            require(r14['stress_test'] == 'unknown', 'R14 uncertain applicability cannot pass/fail')
        if r14['stress_test'] == 'passed':
            require(all(item['status'] in ('supported', 'bounded') for item in r14['inputs'].values()),
                    'R14 missing evidence / arbitrary assumption cannot establish passed')
            require(r14['inputs']['ocf_bridge']['derivation'] is not None,
                    'R14 passed requires cash-flow/survival bridge, not an unexplained OCF base')
            require(r14['calculation'] is not None, 'R14 passed requires explicit stress calculation')
    rules = {row['id']: row for row in audit['constraints']}
    if r14['stress_test'] in ('failed', 'unknown'):
        require(bool(ids), 'R14 failed/unknown requires persistent add constraint')
        for ident in ids:
            require(ident in rules, 'R14 unknown constraint ID')
            row = rules[ident]
            require('add' in row['scope'] and row.get('lifecycle') == 'persistent'
                    and row['status'] in ('blocking', 'unknown'),
                    'R14 failed/unknown requires active persistent add constraint')
            require('R14' in row['reason'], 'R14 gap must bind its own R14 claim, not an unrelated blocker')
            if r14['stress_test'] == 'failed':
                require(row['status'] == 'blocking', 'R14 failed must retain confirmed add restriction')
    elif ids:
        require(all(ident in rules and rules[ident]['status'] in ('clear', 'not_applicable')
                    and (rules[ident].get('clearance') or {}).get('evidence') for ident in ids),
                'R14 passed constraint references require explicit evidenced clearance')
    # A declared pass/N/A cannot conceal a simultaneously unresolved R14 claim.
    if r14['stress_test'] in ('passed', 'not_applicable'):
        require(not any(row['status'] in ('blocking', 'unknown') and 'R14' in row['reason']
                        and 'add' in row['scope'] for row in rules.values()),
                'R14 pass/N/A contradicts active R14 evidence gap')
    recovery = acceptance['recovery']
    fields(recovery, {'operator', 'scopes'}, 'acceptance recovery')
    require(recovery['operator'] == 'all_of', 'recovery requires ALL active independent constraints')
    fields(recovery['scopes'], set(SCOPES), 'recovery scopes')
    for scope in SCOPES:
        actual = _ids(recovery['scopes'][scope], 'recovery.' + scope)
        expected = [row['id'] for row in audit['constraints']
                    if scope in row['scope'] and row['status'] in ('blocking', 'unknown')]
        require(set(actual) == set(expected) == set(audit['release_all_of'][scope]),
                'recovery must cover ALL active constraints for ' + scope)


def render_view(acceptance, audit):
    # Data is escaped for Markdown, never interpreted as a permission to trade.
    def cell(value):
        return str(value).replace('|', '／').replace('\n', ' ').replace('\r', ' ')
    r14 = acceptance['r14']
    lines = [VIEW_START, '共享验收：R14 缺证不能判通过；各范围全部有效约束解除后才可恢复研究资格。',
             'R14：' + cell(r14['applicability']) + ' / ' + cell(r14['stress_test']) + '。',
             '| R14 必要输入 | 证据状态 |', '|---|---|']
    for key in INPUTS:
        lines.append('| ' + key + ' | ' + cell(r14['inputs'][key]['status']) + ' |')
    lines += ['| 恢复范围 | 必须全部解除的当前约束 |', '|---|---|']
    for scope in SCOPES:
        lines.append('| ' + scope + ' | ' + cell(', '.join(acceptance['recovery']['scopes'][scope]) or '无未解研究约束') + ' |')
    lines += ['规则内部合法替代路径保留；不同独立约束之间不能相互替代。运行时价格和账户条件仍须另行核验。', VIEW_END]
    return '\n'.join(lines)


def render_block(acceptance, audit, *, root=None):
    validate_claims(acceptance, audit, root=root)
    return (render_view(acceptance, audit) + '\n\n' + START + '\n```json\n'
            + json.dumps(acceptance, ensure_ascii=False, indent=2, allow_nan=False, default=json_number)
            + '\n```\n' + END)


def validate_recovery_prose(report):
    """Reject explicit subset clearance language, including the observed failure.

    This conservative lint is not a natural-language proof. Ambiguous subset
    wording must be rewritten; legal alternatives *inside one rule* remain OR.
    """
    text = re.sub(r'```.*?```', '', report, flags=re.S)
    text = re.sub(r'<[^>]*>', '', text)
    text = unicodedata.normalize('NFKC', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Cf')
    text = text.replace('**', '').replace('__', '').replace('`', '')
    # A named rule can have legal alternative conditions. Exempt only its
    # local "任一条件" token when clearance targets that *same* named rule;
    # other subset permissions in the sentence remain subject to the lint.
    for local in re.findall(r'[^，,。；;\n]+', text):
        named = re.search(r'\b([A-Z][A-Z0-9_-]*)\b.{0,24}?合法替代(?:条件|路径).{0,8}?(?P<alternative>任一条件)', local)
        if named and re.search(r'解除\s*' + re.escape(named[1]) + r'(?:\b|\s|约束)', local[named.end():]):
            safe = local[:named.start('alternative')] + '合法路径之一' + local[named.end('alternative'):]
            text = text.replace(local, safe, 1)
    # "任一路径" inside one rule is legal OR; "任一独立约束" as a
    # substitute for all claims is not. Do not impose AND on D5's alternatives.
    subset = (r'(?:大部分|多数|部分|任(?:意)?一(?:个|项|条)?(?:独立)?(?:约束|阻断|条件)|'
              r'至少\s*[一二三四五六七八九\d]+\s*[项条个]|majority|most|some|'
              r'any\s+one\s+(?:independent\s+)?(?:constraint|blocker|condition)|at\s+least\s+\d+)')
    for clause in re.split(r'[。；;！!？?\n]', text):
        if not re.search(subset, clause, re.I):
            continue
        if not (re.search(r'解除|解冻|恢复|放行|eligible|clear|resume|unblock', clause, re.I)
                and re.search(r'约束|阻断|条件|上述|前述|第.{0,8}项|constraint|blocker|condition', clause, re.I)):
            continue
        # Permit explicit prohibitions, but do not let a negated prefix excuse
        # a later affirmative instruction in the same sentence.
        chunks = re.split(r'但是|然而|不过|但|[，,：:]|\bbut\b|\bhowever\b', clause, flags=re.I)
        for chunk in chunks:
            quantified = re.search(subset, chunk, re.I)
            if quantified is None:
                continue
            negated = re.search(r'不能|不得|不可|禁止|不允许|不应|不代表|不足以|不是|并非|not\b|cannot\b|never\b', chunk, re.I)
            # Negation must govern the subset permission, rather than an
            # unrelated statement later in the sentence ("can resume and must
            # not lose the evidence"). Unclear wording fails closed.
            permission = re.search(r'(?:即可|就可|可以|可|允许|足以|能)?(?:恢复|解冻|放行)|'
                                   r'\b(?:resume|unblock|eligible)\b', chunk[quantified.end():], re.I)
            permission_at = quantified.end() + permission.start() if permission else len(chunk)
            before = (negated is not None and negated.end() <= quantified.start()
                      and re.fullmatch(r'(?:(?:仅|只|因为|因|以|凭|在|把|将|认为|说|约束|条件|阻断|有效|独立)|\s|[“\"\']|just\b|only\b)*',
                                       chunk[negated.end():quantified.start()], re.I) is not None)
            after = negated is not None and quantified.end() <= negated.start() <= permission_at
            double_negative = re.search(r'(?:并非|不是|不代表|not)\s*(?:不能|不得|不允许|不可|cannot|not)', chunk, re.I)
            governs = (before or after) and double_negative is None
            require(governs,
                    'recovery prose permits subset/majority clearance; ALL active independent constraints required')


def validate(report, audit, *, root=None):
    acceptance = extract(report)
    validate_claims(acceptance, audit, root=root)
    require(report.count(VIEW_START) == report.count(VIEW_END) == 1,
            'acceptance requires exactly one visible acceptance view')
    require(render_view(acceptance, audit) in report, 'acceptance visible recovery view mismatch')
    calculation = acceptance['r14']['calculation']
    if calculation is not None:
        try:
            from .research_consistency import VIEW_START as AUDIT_VIEW_START, VIEW_END as AUDIT_VIEW_END
        except ImportError:
            from research_consistency import VIEW_START as AUDIT_VIEW_START, VIEW_END as AUDIT_VIEW_END
        # Generated views echo declarations; neither they nor JSON establish
        # an independent stress calculation in the report's own prose.
        prose = report
        for start, end in ((VIEW_START, VIEW_END), (AUDIT_VIEW_START, AUDIT_VIEW_END)):
            prose = re.sub(re.escape(start) + r'.*?' + re.escape(end), '', prose, flags=re.S)
        prose = re.sub(r'```.*?```', '', prose, flags=re.S)
        prose = re.sub(r'<!--.*?-->', '', prose, flags=re.S)
        require(calculation['report_quote'] in prose, 'R14 calculation quote absent from report prose')
    validate_recovery_prose(report)
    return {'schema_version': SCHEMA, 'status': 'passed', 'semantic_source_review_required': True,
            'scope': 'evidence availability/binding, declared R14 state, all-of recovery and explicit prose contradictions'}


def refresh_recovery(report, audit):
    """Derived compatibility isolation only; never rewrite the source report."""
    acceptance = extract(report)
    acceptance['recovery'] = {'operator': 'all_of', 'scopes': audit['release_all_of']}
    view = render_view(acceptance, audit)
    report = re.sub(re.escape(VIEW_START) + r'.*?' + re.escape(VIEW_END), lambda _: view, report, flags=re.S)
    block = START + '\n```json\n' + json.dumps(acceptance, ensure_ascii=False, indent=2,
                allow_nan=False, default=json_number) + '\n```\n' + END
    return re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: block, report, flags=re.S)
