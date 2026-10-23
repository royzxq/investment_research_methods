"""Read-only delivery checks for isolated harness experiments.

The experiment envelope has no production generator or meta. A transient,
unserialized compatibility projection allows reuse of the existing v4/audit-v2
arithmetic/control validators. It neither publishes a price map nor attributes
an experiment to Codex. No production writer, seal, scheduler, or API is used.

The small review declaration records a researcher's self-check, not a second
investment framework. Source truth, applicability, completeness, and prose
equivalence still require independent review against the frozen canonical.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal
import json
import os
from pathlib import Path
import re
import stat

try:
    from . import research_consistency as consistency
    from .stock_price_map import (fields, json_number, number, require, string,
                                  validate_price_references, validate_t1_delivery)
except ImportError:
    import research_consistency as consistency
    from stock_price_map import (fields, json_number, number, require, string,
                                 validate_price_references, validate_t1_delivery)

SCHEMA = 'harness-research-experiment/v1'
REVIEW_SCHEMA = 'harness-delivery-checks/v1'
START = '<!-- experiment-delivery:start -->'
END = '<!-- experiment-delivery:end -->'
SUMMARY_KEYS = {'price_map', 'research_controls', 'monitoring'}
IDENTITY_KEYS = {'code', 'valuation_date', 'currency'}
RESULT_KEYS = {'schema_version', 'audit'} | IDENTITY_KEYS | SUMMARY_KEYS
REVIEW_KEYS = {'precheck', 'r14', 'd5', 'r9', 'holding'}
MAX_ARTIFACT_BYTES = 4 * 1024 * 1024


def loads_strict(text):
    """Reject duplicates and nonfinite constants rather than repairing JSON."""
    return json.loads(text, parse_float=Decimal,
                      object_pairs_hook=consistency.strict_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                      default=json_number)


def _decimal_json_values(value):
    """Compare JSON numeric spellings without rounding existing Decimals."""
    if isinstance(value, (float, Decimal)):
        numeric = Decimal(str(value))
        require(numeric.is_finite(), 'experiment JSON requires finite numbers')
        return numeric
    if isinstance(value, dict):
        require(all(isinstance(key, str) for key in value), 'experiment JSON requires string keys')
        return {key: _decimal_json_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_decimal_json_values(item) for item in value]
    require(value is None or type(value) in (str, int, bool), 'experiment requires JSON values')
    return value


def _extract_block(report, start, end):
    require(report.count(start) == report.count(end) == 1,
            'experiment delivery: require exactly one complete ' + start)
    match = re.search(re.escape(start) + r'\s*```json\s*\n(.*?)\n```\s*'
                      + re.escape(end), report, re.S)
    require(match is not None, 'experiment delivery: malformed JSON block')
    return loads_strict(match[1])


def validation_projection(result):
    """Return deep copies for pure validators; never serialize this projection.

    ``codex`` is a fixed validator compatibility sentinel, used for both arms.
    Neither the input nor the report acquires this fictitious meta/generator.
    Neutral identity is checked *before* the sentinel is added. Baselines are
    forbidden in this frozen no-history experiment, avoiding filesystem reads.
    """
    fields(result, RESULT_KEYS, 'experiment result')
    require(result['schema_version'] == SCHEMA, 'experiment schema mismatch')
    audit = deepcopy(result['audit'])
    fields(audit, {'schema_version', 'identity', 'valuation', 'baseline', 'discounts',
                   'risks', 'constraints', 'release_all_of', 'p1_basis'}, 'experiment audit')
    require(audit['schema_version'] == consistency.SCHEMA, 'experiment requires audit-v2')
    fields(audit['identity'], IDENTITY_KEYS, 'neutral audit identity')
    require(audit['identity'] == {key: result[key] for key in IDENTITY_KEYS},
            'experiment audit identity mismatch')
    require(audit['baseline'] is None, 'frozen no-history experiment requires baseline=null')
    meta = dict(schema_version='stock-research/v4', name='isolated experiment validation',
                generator='codex', report_path='__experiment_validation_only__.md',
                **{key: result[key] for key in IDENTITY_KEYS})
    document = dict(meta=meta, **{key: deepcopy(result[key]) for key in SUMMARY_KEYS})
    audit['identity']['generator'] = 'codex'
    return audit, document


def _enum(value, choices, label):
    require(isinstance(value, str) and value in choices, label + ': unsupported value')


def _ids(value, label):
    return consistency.text_list(value, label, empty=True)


def _affected_rules(ids, audit, scope, label, *, require_any=True):
    _ids(ids, label)
    if require_any:
        require(bool(ids), label + ': unresolved necessary check requires constraint IDs')
    rules = {row['id']: row for row in audit['constraints']}
    selected = []
    for ident in ids:
        require(ident in rules, label + ': unknown constraint ID ' + ident)
        row = rules[ident]
        require(row['status'] in {'blocking', 'unknown'}
                and row['lifecycle'] == 'persistent',
                label + ': constraint must retain unresolved persistent status')
        if scope in row['scope']:
            selected.append(row)
    require(bool(selected) or not require_any,
            label + ': constraints must retain unresolved ' + scope + ' scope')
    return selected


def validate_review(review, result):
    """Check declared mappings, not the truth of the declarations or sources."""
    fields(review, REVIEW_KEYS, 'delivery review')
    audit = result['audit']
    precheck = review['precheck']
    fields(precheck, {'state', 'd_base_upper_required', 'reason'}, 'review.precheck')
    _enum(precheck['state'], {'normal', 'caution', 'hard_failure', 'unknown'}, 'precheck.state')
    require(type(precheck['d_base_upper_required']) is bool, 'precheck upper flag must be boolean')
    string(precheck['reason'], 'precheck.reason')
    if precheck['state'] == 'caution':
        require(precheck['d_base_upper_required'], 'Precheck caution requires upper mapping')
    if precheck['d_base_upper_required']:
        discount = audit['discounts']['d_base']
        require(number(discount['value'], 'd_base') == number(discount['range'][1], 'd_base upper'),
                'Precheck/from-strict mapping requires declared d_base range upper')

    r14 = review['r14']
    fields(r14, {'applicability', 'stress_test', 'constraint_ids', 'reason'}, 'review.r14')
    _enum(r14['applicability'], {'applicable', 'not_applicable', 'unknown'}, 'r14.applicability')
    _enum(r14['stress_test'], {'passed', 'failed', 'unknown', 'not_applicable'}, 'r14.stress_test')
    string(r14['reason'], 'r14.reason')
    _ids(r14['constraint_ids'], 'r14.constraint_ids')
    if r14['applicability'] == 'not_applicable':
        require(r14['stress_test'] == 'not_applicable', 'R14 not-applicable declaration contradicts stress state')
    else:
        require(r14['stress_test'] != 'not_applicable', 'R14 required/unknown check cannot be exempted')
        if r14['applicability'] == 'unknown':
            require(r14['stress_test'] == 'unknown', 'R14 applicability unknown cannot declare pass/fail')
        if r14['stress_test'] in {'failed', 'unknown'}:
            _affected_rules(r14['constraint_ids'], audit, 'add', 'R14')

    d5 = review['d5']
    fields(d5, {'applicability', 'original_rebuild_independent',
                'r21_exit_is_full_clearance', 'reason'}, 'review.d5')
    _enum(d5['applicability'], {'applicable', 'not_applicable', 'unknown'}, 'd5.applicability')
    require(d5['original_rebuild_independent'] is True,
            'D5 original rebuilding path must remain independent of R21')
    require(d5['r21_exit_is_full_clearance'] is False,
            'R21 exit alone is not D5 full clearance')
    string(d5['reason'], 'd5.reason')

    r9 = review['r9']
    fields(r9, {'applicability', 'benchmark_status', 'benchmark_currency',
                'constraint_ids', 'reason'}, 'review.r9')
    _enum(r9['applicability'], {'applicable', 'not_applicable', 'unknown'}, 'r9.applicability')
    _enum(r9['benchmark_status'], {'verified', 'unknown', 'not_applicable'}, 'r9.benchmark_status')
    string(r9['reason'], 'r9.reason')
    _ids(r9['constraint_ids'], 'r9.constraint_ids')
    if r9['benchmark_status'] == 'verified':
        require(r9['benchmark_currency'] == result['currency'],
                'R9 yield spread requires comparable quote/benchmark currency')
    else:
        require(r9['benchmark_currency'] is None, 'unverified R9 benchmark currency must remain null')
    if r9['applicability'] == 'not_applicable':
        require(r9['benchmark_status'] == 'not_applicable', 'R9 not-applicable declaration contradicts benchmark')
    else:
        require(r9['benchmark_status'] != 'not_applicable', 'R9 necessary benchmark cannot be exempted')
        if r9['applicability'] == 'unknown' or r9['benchmark_status'] == 'unknown':
            for scope in ('entry', 'add'):
                _affected_rules(r9['constraint_ids'], audit, scope, 'R9')

    holding = review['holding']
    fields(holding, {'review_status', 'constraint_ids', 'reason'}, 'review.holding')
    _enum(holding['review_status'], {'not_triggered', 'pending', 'completed', 'unknown'},
          'holding.review_status')
    string(holding['reason'], 'holding.reason')
    _ids(holding['constraint_ids'], 'holding.constraint_ids')
    if holding['review_status'] in {'pending', 'unknown'}:
        rows = _affected_rules(holding['constraint_ids'], audit, 'holding', 'holding review')
        require(all(row['action'] in {'review_holding', 'invalidated', 'exit_required'} for row in rows),
                'triggered holding review requires applicable holding action')
        require(result['research_controls']['holding']['status'] != 'normal',
                'triggered holding review cannot report normal')
    elif holding['review_status'] == 'completed':
        require(bool(holding['constraint_ids']), 'completed holding review requires explicit evidence claim')
        rules = {row['id']: row for row in audit['constraints']}
        for ident in holding['constraint_ids']:
            require(ident in rules, 'completed holding review: unknown constraint ID')
            row = rules[ident]
            require('holding' in row['scope'] and row['status'] in {'clear', 'not_applicable'}
                    and bool((row.get('clearance') or {}).get('evidence')),
                    'completed holding review requires cleared holding claim with evidence')


def validate_experiment(report, result, *, require_acceptance=False, root=None):
    """Validate without mutation or output writes; raise ValueError on failure."""
    require(isinstance(report, str) and bool(report.strip()), 'experiment report is empty')
    # Native callers may supply floats; compare their explicit JSON decimal
    # spellings, not Python's binary-float equality against parsed Decimals.
    result = _decimal_json_values(result)
    audit, document = validation_projection(result)
    for row in audit['constraints']:
        require('lifecycle' in row, 'new experiment controls require explicit lifecycle')
    receipt = consistency.validate_audit(audit, document)
    validate_price_references(document)
    validate_t1_delivery(document)
    # This deliberately checks syntax and declared arithmetic. It does not
    # infer source truth or repair units, risk IDs, scenarios, or output quotes.
    sections = re.findall(r'^##\s+(\d+)\.\s*\S', report, re.M)
    require(sections == [str(index) for index in range(9)],
            'experiment report requires ordered sections 0 through 8 exactly once')
    require(consistency.extract_audit(report) == result['audit'],
            'report audit differs from result.audit')
    require(report.count(consistency.VIEW_START) == report.count(consistency.VIEW_END) == 1,
            'experiment requires one visible calculation view')
    require(consistency.render_checks(audit, document) in report,
            'visible calculation view differs from experiment inputs/quotes')
    try:
        from . import research_acceptance
    except ImportError:
        import research_acceptance
    acceptance = None
    if require_acceptance or research_acceptance.START in report or research_acceptance.END in report:
        acceptance = research_acceptance.validate(report, audit, root=root)
    delivery = _extract_block(report, START, END)
    fields(delivery, {'schema_version', 'review'} | SUMMARY_KEYS, 'experiment delivery block')
    require(delivery['schema_version'] == REVIEW_SCHEMA, 'experiment review schema mismatch')
    for key in SUMMARY_KEYS:
        require(delivery[key] == result[key], 'report delivery differs from result.' + key)
    validate_review(delivery['review'], result)
    if acceptance is not None:
        r14 = research_acceptance.extract(report)['r14']
        for key in ('applicability', 'stress_test', 'constraint_ids'):
            require(delivery['review']['r14'][key] == r14[key], 'R14 experiment/shared acceptance mismatch: ' + key)
    receipt = dict(schema_version='harness-delivery-receipt/v1', status='passed',
                arithmetic_and_controls=receipt, neutral_projection_only=True,
                semantic_source_review_required=True, experiment_only=True, production=False,
                consensus_eligible=False)
    if acceptance is not None:
        receipt['acceptance'] = acceptance
    return receipt


def render_experiment_sections(result, review):
    """Render declared data only; no file writes and no research/quote changes."""
    audit, document = validation_projection(result)
    consistency.validate_audit(audit, document)
    validate_review(review, result)
    summary = dict(schema_version=REVIEW_SCHEMA, review=review,
                   **{key: result[key] for key in SUMMARY_KEYS})
    return (consistency.render_checks(audit, document) + '\n\n'
            + consistency.START + '\n```json\n' + _json(result['audit']) + '\n```\n'
            + consistency.END + '\n\n' + START + '\n```json\n' + _json(summary)
            + '\n```\n' + END + '\n')


def read_regular(path, max_bytes=MAX_ARTIFACT_BYTES):
    """Bounded, nonblocking local read; reject symlink parents and endpoints."""
    path = Path(path).absolute()
    require(not any(part.is_symlink() for part in (path, *path.parents)),
            'experiment artifacts must not be symlinks')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_size <= max_bytes,
                'experiment artifact must be a bounded regular file')
        data = bytearray()
        while len(data) <= max_bytes:
            chunk = os.read(fd, min(65536, max_bytes + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        require(len(data) <= max_bytes, 'experiment artifact grew beyond bound')
        return bytes(data).decode('utf-8')
    finally:
        os.close(fd)


def check_delivery(report_path, result_path, *, require_acceptance=False, root=None):
    return validate_experiment(read_regular(report_path), loads_strict(read_regular(result_path)),
                               require_acceptance=require_acceptance, root=root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'render'))
    parser.add_argument('--result', required=True, type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--review', type=Path, help='researcher review declaration, render only')
    parser.add_argument('--acceptance', type=Path, help='new shared acceptance JSON, render only')
    parser.add_argument('--require-acceptance', action='store_true', help='new shared R14/all-of gate')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        if args.command == 'check':
            require(args.report is not None, 'check requires --report')
            print(_json(check_delivery(args.report, args.result,
                                      require_acceptance=args.require_acceptance, root=args.root)))
        else:
            require(args.review is not None, 'render requires --review')
            result = loads_strict(read_regular(args.result))
            rendered = render_experiment_sections(result, loads_strict(read_regular(args.review)))
            if args.acceptance is not None:
                try:
                    from . import research_acceptance
                except ImportError:
                    import research_acceptance
                audit, _ = validation_projection(result)
                rendered += '\n\n' + research_acceptance.render_block(
                    loads_strict(read_regular(args.acceptance)), audit, root=args.root)
            print(rendered)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        parser.exit(2, 'Experiment delivery failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
