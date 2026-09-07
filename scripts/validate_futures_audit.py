"""Offline structural checks for futures execution audit schema 2.

CLI: python scripts/validate_futures_audit.py report.json
     python scripts/validate_futures_audit.py --input report.md
     python scripts/validate_futures_audit.py --input -

Markdown must contain exactly one fenced ``json`` block. JSON duplicate keys
and non-finite numbers are rejected. No network, credentials, market-data
refresh, risk calculation, automatic freshness cutoff, or trading permission
evaluation occurs. A valid result only means the supplied structure and stated
statuses are consistent; it does not establish source truth or rule coverage.
"""

import argparse
from datetime import date, datetime, timedelta, timezone
import json
import math
from pathlib import Path
import re
import sys


ACCOUNT_FACTS = (
    "equity", "open_positions", "pending_orders", "existing_risk",
    "reserved_order_risk", "margin_available",
)
EVIDENCE_FIELDS = (
    "evidence_id", "metric", "value", "unit", "observation_date", "published_at",
    "source_url_or_file", "original_source", "price_basis", "comparison_basis",
    "role", "quality", "time_scope",
)
CHINA_TIME = timezone(timedelta(hours=8))


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _enum(value, allowed, path, errors):
    if not isinstance(value, str) or value not in allowed:
        errors.append(f"{path}: expected one of {', '.join(sorted(allowed))}")
        return False
    return True


def _object(value, path, errors):
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return None
    return value


def _list(value, path, errors):
    if not isinstance(value, list):
        errors.append(f"{path}: expected array")
        return None
    return value


def _required_fields(value, fields, path, errors):
    for field in fields:
        if field not in value:
            errors.append(f"{path}.{field}: missing field")


def _date(value, path, errors, *, timestamp=False):
    if not _text(value):
        errors.append(f"{path}: expected ISO date" + (" or timestamp" if timestamp else ""))
        return None
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return date.fromisoformat(value)
        if timestamp:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timestamp requires timezone")
            return parsed.astimezone(CHINA_TIME).date()
    except (ValueError, OverflowError):
        pass
    errors.append(f"{path}: invalid ISO date or timezone-qualified timestamp")
    return None


def _dated(value, path, as_of, errors, *, timestamp=False, required=False):
    if value is None and not required:
        return
    observed = _date(value, path, errors, timestamp=timestamp)
    if observed is not None and as_of is not None and observed > as_of:
        errors.append(f"{path}: later than as_of_date (Asia/Shanghai)")


def _ids(value, path, errors):
    items = _list(value, path, errors)
    if items is None:
        return set()
    result = set()
    for index, item in enumerate(items):
        if not _text(item):
            errors.append(f"{path}[{index}]: expected nonempty ID string")
        elif item in result:
            errors.append(f"{path}[{index}]: duplicate ID {item}")
        else:
            result.add(item)
    return result


def _json_values(value, path, errors):
    """Keep direct library calls as strict as parsed JSON, without coercion."""
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            errors.append(f"{path}: non-finite number")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _json_values(item, f"{path}[{index}]", errors)
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                errors.append(f"{path}: object key must be a string")
            _json_values(item, f"{path}.{key}", errors)
    else:
        errors.append(f"{path}: expected JSON-compatible value")


def _account(snapshot, as_of, errors):
    account = _object(snapshot.get("account"), "snapshot.account", errors)
    if account is None:
        return False
    path = "snapshot.account"
    _required_fields(account, ("actual_position_status", "verified_at", "evidence") + ACCOUNT_FACTS,
                     path, errors)
    status = account.get("actual_position_status")
    _enum(status, {"unknown", "verified_flat", "verified_positions"},
          f"{path}.actual_position_status", errors)
    if status == "unknown":
        for field in ACCOUNT_FACTS:
            if account.get(field) is not None:
                errors.append(f"{path}.{field}: must be null when account is unknown")
        return False
    if status not in ("verified_flat", "verified_positions"):
        return False
    start_errors = len(errors)
    _dated(account.get("verified_at"), f"{path}.verified_at", as_of, errors,
           timestamp=True, required=True)
    if not _text(account.get("evidence")):
        errors.append(f"{path}.evidence: verified account requires a source reference")
    for field in ("equity", "existing_risk", "reserved_order_risk", "margin_available"):
        value = account.get(field)
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or (isinstance(value, float) and not math.isfinite(value)) or value < 0):
            errors.append(f"{path}.{field}: verified account requires a finite nonnegative number")
    positions = _list(account.get("open_positions"), f"{path}.open_positions", errors)
    _list(account.get("pending_orders"), f"{path}.pending_orders", errors)
    if positions is not None:
        if status == "verified_flat" and positions:
            errors.append(f"{path}.open_positions: verified_flat requires an empty array")
        if status == "verified_positions" and not positions:
            errors.append(f"{path}.open_positions: verified_positions requires registered positions")
    return len(errors) == start_errors


def _evidence(rows, as_of, errors):
    evidence_ids = set()
    for index, row in enumerate(rows):
        path = f"evidence[{index}]"
        item = _object(row, path, errors)
        if item is None:
            continue
        _required_fields(item, EVIDENCE_FIELDS, path, errors)
        evidence_id = item.get("evidence_id")
        if not _text(evidence_id):
            errors.append(f"{path}.evidence_id: expected nonempty ID string")
        elif evidence_id in evidence_ids:
            errors.append(f"{path}.evidence_id: duplicate ID {evidence_id}")
        else:
            evidence_ids.add(evidence_id)
        if not _text(item.get("metric")):
            errors.append(f"{path}.metric: expected nonempty string")
        _enum(item.get("role"), {"required_execution", "required_model", "optional_context"},
              f"{path}.role", errors)
        _enum(item.get("quality"), {"verified", "missing", "stale", "conflicting", "invalid"},
              f"{path}.quality", errors)
        _enum(item.get("time_scope"), {"current", "historical"}, f"{path}.time_scope", errors)
        required_verified = (item.get("role") in ("required_execution", "required_model")
                             and item.get("quality") == "verified")
        if required_verified:
            for field in ("unit", "source_url_or_file", "original_source"):
                if not _text(item.get(field)):
                    errors.append(f"{path}.{field}: required verified evidence needs a nonempty value")
            if item.get("value") is None:
                errors.append(f"{path}.value: required verified evidence cannot be null")
        _dated(item.get("observation_date"), f"{path}.observation_date", as_of, errors,
               required=required_verified)
        _dated(item.get("published_at"), f"{path}.published_at", as_of, errors,
               timestamp=True, required=required_verified)
    return evidence_ids


def _candidate(row, index, evidence_ids, account_verified, errors):
    path = f"candidates[{index}]"
    candidate = _object(row, path, errors)
    if candidate is None:
        return
    _required_fields(candidate, ("data_feasibility", "signal", "status", "evaluated_checks",
                               "all_blockers", "unknown_checks", "first_blocker",
                               "only_blocker", "final_lots"), path, errors)
    feasibility, signal, status = (candidate.get(key) for key in ("data_feasibility", "signal", "status"))
    _enum(feasibility, {"available", "temporary_gap", "research_only"}, f"{path}.data_feasibility", errors)
    _enum(signal, {"triggered", "not_triggered", "unknown"}, f"{path}.signal", errors)
    _enum(status, {"no_signal", "incomplete", "blocked", "ready"}, f"{path}.status", errors)
    checks = _list(candidate.get("evaluated_checks"), f"{path}.evaluated_checks", errors)
    failed, unknown, seen = set(), set(), set()
    check_order = []
    for check_index, row in enumerate(checks or []):
        check_path = f"{path}.evaluated_checks[{check_index}]"
        check = _object(row, check_path, errors)
        if check is None:
            continue
        _required_fields(check, ("rule_id", "applicable", "result", "evidence_refs"), check_path, errors)
        rule = check.get("rule_id")
        if not _text(rule):
            errors.append(f"{check_path}.rule_id: expected nonempty ID string")
            rule = None
        elif rule in seen:
            errors.append(f"{check_path}.rule_id: duplicate rule ID {rule}")
        else:
            seen.add(rule)
            check_order.append(rule)
        applicable, result = check.get("applicable"), check.get("result")
        if type(applicable) is not bool:
            errors.append(f"{check_path}.applicable: expected boolean")
        _enum(result, {"pass", "fail", "unknown", "not_applicable"}, f"{check_path}.result", errors)
        if applicable is False and result != "not_applicable":
            errors.append(f"{check_path}.result: inapplicable check must be not_applicable")
        if applicable is True and result == "not_applicable":
            errors.append(f"{check_path}.result: applicable check cannot be not_applicable")
        if applicable is True and rule is not None:
            if result == "fail":
                failed.add(rule)
            if result == "unknown":
                unknown.add(rule)
        references = _ids(check.get("evidence_refs"), f"{check_path}.evidence_refs", errors)
        for reference in sorted(references - evidence_ids):
            errors.append(f"{check_path}.evidence_refs: unresolved evidence ID {reference}")
    if "evidence_refs" in candidate:
        references = _ids(candidate["evidence_refs"], f"{path}.evidence_refs", errors)
        for reference in sorted(references - evidence_ids):
            errors.append(f"{path}.evidence_refs: unresolved evidence ID {reference}")
    blockers = _ids(candidate.get("all_blockers"), f"{path}.all_blockers", errors)
    unknown_checks = _ids(candidate.get("unknown_checks"), f"{path}.unknown_checks", errors)
    if blockers != failed:
        errors.append(f"{path}.all_blockers: must equal applicable fail rule IDs")
    if unknown_checks != unknown:
        errors.append(f"{path}.unknown_checks: must equal applicable unknown rule IDs")
    if "evaluation_order" in candidate:
        order_ids = _ids(candidate["evaluation_order"], f"{path}.evaluation_order", errors)
        if order_ids != seen:
            errors.append(f"{path}.evaluation_order: must cover evaluated_checks rule IDs exactly")
        if isinstance(candidate["evaluation_order"], list):
            check_order = [rule for rule in candidate["evaluation_order"] if _text(rule)]
    expected_first = next((rule for rule in check_order if rule in failed), None)
    first = candidate.get("first_blocker")
    if first is not None and not _text(first):
        errors.append(f"{path}.first_blocker: expected rule ID string or null")
    elif first is not None and first not in failed:
        errors.append(f"{path}.first_blocker: must reference an applicable fail rule")
    if first != expected_first:
        errors.append(f"{path}.first_blocker: must be the first fail in evaluation order ({expected_first!r})")
    only = candidate.get("only_blocker")
    if only is not None and type(only) is not bool:
        errors.append(f"{path}.only_blocker: expected boolean or null")
    elif only is True and (len(failed) != 1 or unknown):
        errors.append(f"{path}.only_blocker: true requires exactly one fail and no unknown checks")
    elif only is False and len(failed) < 2:
        errors.append(f"{path}.only_blocker: false requires at least two known failures; otherwise use null")
    lots = candidate.get("final_lots")
    if lots is not None and (type(lots) is not int or lots < 0):
        errors.append(f"{path}.final_lots: expected nonnegative integer or null, never boolean")
    if not account_verified and lots is not None:
        errors.append(f"{path}.final_lots: must be null without a verified account snapshot")
    if status == "no_signal" and signal != "not_triggered":
        errors.append(f"{path}.status: no_signal requires signal=not_triggered")
    if signal == "not_triggered" and status != "no_signal":
        errors.append(f"{path}.status: an explicitly untriggered signal requires no_signal")
    if signal == "unknown" and status != "incomplete":
        errors.append(f"{path}.status: unknown signal requires incomplete")
    if status == "blocked" and (unknown or not account_verified):
        errors.append(f"{path}.status: unresolved checks/account require incomplete, retaining known blockers")
    if status == "blocked" and not failed and lots != 0:
        errors.append(f"{path}.status: blocked requires a known failure or verified zero capacity")
    if status == "ready":
        if (signal != "triggered" or feasibility != "available" or failed or unknown
                or not account_verified or type(lots) is not int or lots < 1):
            errors.append(f"{path}.status: ready requires triggered/available, no fail or unknown, verified account, final_lots >= 1")


def validate_audit(doc):
    """Return structural error strings; an empty list never grants permission.

    Only the supplied checks are reconciled. This function does not determine
    whether every required trading rule was included or evidence is authentic.
    ``configured_equity`` is configuration, not a verified account balance.
    Missing optional context remains a valid evidence record and does not by
    itself change a candidate's status. Historical ages are not auto-classified.
    """
    errors = []
    document = _object(doc, "$", errors)
    if document is None:
        return errors
    try:
        _json_values(document, "$", errors)
    except RecursionError:
        return ["$: structure is cyclic or exceeds supported nesting depth"]
    _required_fields(document, ("audit_schema_version", "as_of_date", "research_mode", "framework",
                                "snapshot", "coverage", "candidates", "evidence", "unresolved_items"),
                     "$", errors)
    if type(document.get("audit_schema_version")) is not int or document["audit_schema_version"] != 2:
        errors.append("audit_schema_version: expected integer 2")
    _enum(document.get("research_mode"), {"public_data"}, "research_mode", errors)
    as_of = _date(document.get("as_of_date"), "as_of_date", errors)
    _object(document.get("framework"), "framework", errors)
    _object(document.get("coverage"), "coverage", errors)
    snapshot = _object(document.get("snapshot"), "snapshot", errors)
    account_verified = False
    if snapshot is not None:
        account_verified = _account(snapshot, as_of, errors)
        for field, timestamp in (("market_trade_date", False), ("market_captured_at", True)):
            _dated(snapshot.get(field), f"snapshot.{field}", as_of, errors, timestamp=timestamp)
    evidence = _list(document.get("evidence"), "evidence", errors)
    evidence_ids = _evidence(evidence or [], as_of, errors)
    candidates = _list(document.get("candidates"), "candidates", errors)
    for index, candidate in enumerate(candidates or []):
        _candidate(candidate, index, evidence_ids, account_verified, errors)
    unresolved = _list(document.get("unresolved_items"), "unresolved_items", errors)
    for index, item in enumerate(unresolved or []):
        _object(item, f"unresolved_items[{index}]", errors)
    return errors


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def load_audit(source, *, markdown=False):
    """Parse JSON or the unique JSON fence of Markdown, rejecting ambiguity."""
    looks_like_json = source.lstrip().startswith(("{", "["))
    if markdown or (not looks_like_json and (source.lstrip().startswith("#") or "```json" in source)):
        blocks = re.findall(r"(?ms)^[ \t]*```json[ \t]*\r?\n(.*?)^[ \t]*```[ \t]*$", source)
        if len(blocks) != 1:
            raise ValueError("Markdown must contain exactly one fenced json audit block")
        source = blocks[0]
    return json.loads(source, object_pairs_hook=_unique_object, parse_constant=_reject_constant)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="JSON or Markdown report path")
    parser.add_argument("--input", dest="input_path", help="JSON/Markdown path, or - for stdin")
    args = parser.parse_args(argv)
    try:
        if bool(args.path) == bool(args.input_path):
            raise ValueError("provide exactly one positional path or --input")
        input_path = args.input_path or args.path
        source = sys.stdin.read() if input_path == "-" else Path(input_path).read_text(encoding="utf-8")
        document = load_audit(source, markdown=Path(input_path).suffix.lower() in (".md", ".markdown"))
        errors = validate_audit(document)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        errors = [f"input: {exc}"]
    output = {"status": "invalid" if errors else "valid", "scope": "structure_validation_only",
              "execution_permission": "not_evaluated", "errors": errors}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
