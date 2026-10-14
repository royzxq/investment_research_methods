"""Small, offline stock-maintenance provenance checks; not a trading/state engine."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re

SCHEMA = "investment-maintenance/v1"
KINDS = {"market-research", "change-decision", "adaption-report", "handoff"}
CHANGE_KINDS = {"state_refresh", "evidence_correction", "method_change"}
START, END = "<!-- investment-state:start -->", "<!-- investment-state:end -->"


def _date(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError("Expected ISO date")
    return value


def _load_json(text):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result
    def reject_constant(value):
        raise ValueError("Nonfinite JSON constant")
    return json.loads(text, object_pairs_hook=unique_pairs, parse_constant=reject_constant)


def method_fingerprint(raw: bytes) -> str:
    """Exclude only validated observations; mixed rule/state prose stays hashed."""
    text = raw.decode("utf-8")
    if START not in text and END not in text:
        return hashlib.sha256(raw).hexdigest()
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
        raise ValueError("Malformed or repeated investment state markers")
    before, remaining = text.split(START)
    body, after = remaining.split(END)
    match = re.fullmatch(r"\s*```json\s*\n(.*?)\n```\s*", body, re.S)
    if not match:
        raise ValueError("State block must contain one fenced JSON object")
    state = _load_json(match.group(1))
    keys = {"schema", "as_of", "evidence_cutoff", "source_report", "observations"}
    if not isinstance(state, dict) or set(state) != keys or state["schema"] != "investment-state/v1":
        raise ValueError("Unexpected state schema or rule fields")
    _date(state["as_of"])
    _date(state["evidence_cutoff"])
    if state["evidence_cutoff"] > state["as_of"]:
        raise ValueError("Future evidence cutoff")
    if state["source_report"] is not None:
        _relative(state["source_report"])
    if not isinstance(state["observations"], list):
        raise ValueError("Observations must be a list")
    seen = set()
    for obs in state["observations"]:
        if not isinstance(obs, dict) or set(obs) != {"id", "value", "unit", "observed_at", "source", "status"}:
            raise ValueError("Observation contains rule fields or missing provenance")
        if not isinstance(obs["id"], str) or not obs["id"] or obs["id"] in seen:
            raise ValueError("Observation identity must be unique")
        seen.add(obs["id"])
        if isinstance(obs["value"], (dict, list)) or isinstance(obs["value"], bool):
            raise ValueError("Observation value must be a scalar fact")
        if isinstance(obs["value"], float) and not math.isfinite(obs["value"]):
            raise ValueError("Nonfinite observation")
        if obs["observed_at"] is None:
            if obs["status"] == "verified" or obs["value"] is not None:
                raise ValueError("Dated observation required for known value")
        else:
            _date(obs["observed_at"])
            if obs["observed_at"] > state["evidence_cutoff"]:
                raise ValueError("Future observation")
        if obs["status"] not in {"verified", "unknown", "withdrawn"}:
            raise ValueError("Unsupported observation status")
        if not isinstance(obs["unit"], str) or not isinstance(obs["source"], (str, type(None))):
            raise ValueError("Invalid observation provenance")
        if obs["status"] == "verified" and (obs["value"] is None or not obs["source"]):
            raise ValueError("Verified observation requires value and source")
    normalized = (before + START + END + after).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def weekly_path(root, as_of, kind, revision=None):
    _date(as_of)
    if kind not in KINDS:
        raise ValueError("Unknown stock weekly kind")
    if revision is not None and (type(revision) is not int or revision < 2):
        raise ValueError("Revision must be an integer >= 2")
    suffix = "" if revision is None else f"-r{revision}"
    ext = "json" if kind == "handoff" else "md"
    return Path(root) / "research/investment/weekly" / as_of / f"investment-{as_of}-{kind}{suffix}.{ext}"


def discover_reports(root, kind, before=None):
    """Discover exact stock family and revisions; discovery does not imply adoption."""
    if kind not in KINDS:
        raise ValueError("Unknown stock weekly kind")
    if before is not None:
        _date(before)
    ext = "json" if kind == "handoff" else "md"
    pattern = re.compile(rf"investment-(\d{{4}}-\d{{2}}-\d{{2}})-{kind}(?:-r([2-9]|[1-9]\d+))?\.{ext}")
    found = []
    for path in (Path(root) / "research/investment/weekly").glob(f"*/*.{ext}"):
        match = pattern.fullmatch(path.name)
        if not match:
            continue
        try:
            day = _date(match[1])
        except ValueError:
            continue
        if path.parent.name != day or (before is not None and day >= before):
            continue
        found.append((day, int(match[2] or 1), path))
    return [item[2] for item in sorted(found)]


def next_revision(root, as_of):
    """Allocate one shared suffix for an entire weekly package, never overwrite."""
    _date(as_of)
    paths = [p for kind in KINDS for p in discover_reports(root, kind) if p.parent.name == as_of]
    if not paths:
        return None
    return max([int(re.search(r"-r(\d+)\.", p.name)[1]) if re.search(r"-r(\d+)\.", p.name) else 1 for p in paths]) + 1


def _relative(value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
        raise ValueError("References must be repository-relative paths")
    return value


def _path(root, value):
    root = Path(root).resolve()
    path = (root / _relative(value)).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Reference escapes repository")
    return path


def file_ref(root, path, *, as_of=None):
    root = Path(root).resolve()
    path = Path(path)
    if not path.is_absolute():
        path = root / path
    relative = path.resolve().relative_to(root).as_posix()
    result = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if as_of is not None:
        result["as_of"] = _date(as_of)
    return result


def _check_ref(root, ref):
    if not isinstance(ref, dict) or not {"path", "sha256"}.issubset(ref):
        raise ValueError("Reference needs path and sha256")
    if "as_of" in ref:
        _date(ref["as_of"])
    raw = _path(root, ref["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise ValueError(f"Source hash changed: {ref['path']}")
    return raw


def _check_dated_ref(root, ref, cutoff, label):
    """Evidence availability is required for decisions, unlike content identity."""
    if not isinstance(ref, dict) or "as_of" not in ref:
        raise ValueError(f"{label}: decision evidence requires as_of")
    if _date(ref["as_of"]) > cutoff:
        raise ValueError(f"{label}: evidence comes from the future relative to its decision cutoff")
    return _check_ref(root, ref)


def freeze_methods(root, as_of, revision=None):
    """Exclusive immutable copies; user approval/adoption is never inferred here."""
    stem = weekly_path(root, as_of, "handoff", revision).stem
    folder = Path(root) / "research/investment/weekly" / as_of / "evidence" / (stem + "-methods")
    folder.mkdir(parents=True, exist_ok=True)
    refs = {}
    for role, name in (("canonical", "investment_framework.md"), ("compact", "investment_framework_compact.md")):
        raw = (Path(root) / "framework" / name).read_bytes()
        fingerprint = method_fingerprint(raw)
        target = folder / name
        if target.exists():
            if target.read_bytes() != raw:
                raise ValueError("Frozen method destination differs; allocate a new revision")
        else:
            with target.open("xb") as stream:
                stream.write(raw)
        refs[role] = {**file_ref(root, target), "method_sha256": fingerprint}
    return refs


def classify_changes(changes):
    flags = {kind: False for kind in sorted(CHANGE_KINDS)}
    for change in changes:
        kind = change.get("kind")
        if kind not in CHANGE_KINDS:
            raise ValueError("Unknown maintenance change kind")
        flags[kind] = True
        if not change.get("summary"):
            raise ValueError("Change needs a concrete summary")
        if kind == "method_change":
            required = ("definition", "economic_reason", "scope", "positive_case", "negative_case", "boundary_case", "compatibility_impact")
            if any(not change.get(field) for field in required):
                raise ValueError("Method proposal lacks definition, economic reason or boundary cases")
            if change.get("status") not in {"proposed", "adopted"}:
                raise ValueError("Method proposal/adoption must be explicit")
    return {**flags, "update_needed": flags["method_change"]}


def _method_pair(root, methods):
    if not isinstance(methods, dict) or set(methods) != {"canonical", "compact"}:
        raise ValueError("Both canonical and compact are required")
    result = []
    for role in ("canonical", "compact"):
        ref = methods[role]
        fingerprint = method_fingerprint(_check_ref(root, ref))
        if ref.get("method_sha256", fingerprint) != fingerprint:
            raise ValueError("Method fingerprint does not match frozen content")
        result.append(fingerprint)
    return tuple(result)


def validate_handoff(record, root):
    """Validate provenance/shape, not investment semantics or permission to trade."""
    if record.get("schema") != SCHEMA:
        raise ValueError("Unknown maintenance handoff schema")
    as_of = _date(record["as_of"])
    def check_reference_dates(value):
        if isinstance(value, dict):
            if {"path", "sha256", "as_of"}.issubset(value) and _date(value["as_of"]) > as_of:
                raise ValueError("Referenced evidence comes from the future")
            for nested in value.values():
                check_reference_dates(nested)
        elif isinstance(value, list):
            for nested in value:
                check_reference_dates(nested)
    check_reference_dates(record)
    revision = record.get("revision")
    expected = weekly_path(root, as_of, "handoff", revision).stem
    if record.get("id") != expected:
        raise ValueError("Handoff identity/date/revision mismatch")
    if record.get("status") not in {"proposed", "adopted", "withdrawn"}:
        raise ValueError("Explicit lifecycle status required")
    if not record.get("adoption_basis") and record["status"] in {"adopted", "withdrawn"}:
        raise ValueError("Adoption/withdrawal requires explicit evidence or authorization")
    if record.get("method_status") != "adopted":
        raise ValueError("State must be evaluated against an adopted base method")
    _method_pair(root, record["methods"])
    reports = record.get("reports", {})
    if not {"market_research", "change_decision"}.issubset(reports):
        raise ValueError("Missing paired research/decision provenance")
    for ref in reports.values():
        _check_dated_ref(root, ref, as_of, "reports")
    flags = classify_changes(record.get("changes", []))
    if record.get("classification") != flags:
        raise ValueError("Classification conflicts with itemized changes")
    if record["status"] == "proposed" and (record.get("supersedes") or record.get("withdrawn_sources")):
        raise ValueError("A proposal cannot supersede adopted evidence")
    if record["status"] == "withdrawn" and not (record.get("supersedes") or record.get("withdrawn_sources")):
        raise ValueError("Withdrawal needs explicit target handoffs or sources")
    supersedes = record.get("supersedes", [])
    if not isinstance(supersedes, list) or len(set(supersedes)) != len(supersedes) or expected in supersedes:
        raise ValueError("Invalid supersession identities")
    for ref in record.get("evidence", []):
        _check_dated_ref(root, ref, as_of, "evidence")
    # Withdrawal targets identify old content, not new evidence for a decision.
    # The withdrawal is dated by this record; any supplied target date is still checked above.
    for ref in record.get("withdrawn_sources", []):
        _check_ref(root, ref)
    for compatible in record.get("compatibility", []):
        if compatible.get("status") != "adopted" or not compatible.get("reason"):
            raise ValueError("Cross-method compatibility needs an adopted review")
        _method_pair(root, compatible["methods"])
        _check_dated_ref(root, compatible["review"], as_of, "compatibility.review")
    for evaluation in record.get("rule_evaluations", []):
        if _date(evaluation.get("as_of")) > as_of:
            raise ValueError("Rule evaluation is from the future")
        if evaluation.get("rule_status") not in {"adopted", "proposed"} or evaluation.get("result") not in {"triggered", "not_triggered", "unknown", "invalidated"}:
            raise ValueError("Rule identity/adoption/trigger status must be separate")
        if not evaluation.get("rule_id") or not evaluation.get("affected_objects"):
            raise ValueError("Rule evaluation needs identity and affected scope")
        if evaluation["result"] == "triggered" and not evaluation.get("evidence"):
            raise ValueError("Triggered evaluation requires evidence")
        for ref in evaluation.get("evidence", []):
            _check_dated_ref(root, ref, evaluation["as_of"], "rule_evaluations.evidence")
    for review in record.get("reviews", []):
        for field in ("reassessment", "compatibility_review"):
            if field in review:
                _check_dated_ref(root, review[field], as_of, "reviews." + field)
        if review.get("status") not in {"pending", "completed", "cancelled"} or not review.get("company") or not review.get("trigger_id"):
            raise ValueError("Company review needs scope, trigger and research status")
        applicable = [item for item in record.get("rule_evaluations", [])
                      if item["rule_id"] == review["trigger_id"] and item["rule_status"] == "adopted"
                      and item["result"] == "triggered" and any(scope in {
                          review["company"], "all", review["company"].split("-")[0],
                          "A" if review["company"].startswith(("SH-", "SZ-", "BJ-")) else "HK"}
                          for scope in item["affected_objects"])]
        if review["status"] in {"pending", "completed"} and not applicable:
            raise ValueError("Company review must link to an adopted triggered rule with matching scope")
        completion = review.get("completion")
        if review["status"] == "completed":
            if not completion or not {"report", "price_map"}.issubset(completion):
                raise ValueError("Triggered is not completed: paired company artifacts required")
            for ref in completion.values():
                _check_dated_ref(root, ref, as_of, "reviews.completion")
            report = completion["report"]["path"]
            price = completion["price_map"]["path"]
            expected_price = report.replace("-research", "-price-map").removesuffix(".md") + ".json"
            if report == expected_price or not report.endswith(".md") or price != expected_price or f"/{review['company']}/" not in report:
                raise ValueError("Company completion must identify the matching report/JSON pair")
            document = _load_json(_check_ref(root, completion["price_map"]))
            meta = document.get("meta", {})
            try:
                from .research_exchange import _report_sections, _validate_pair
                from .stock_price_map import SUPPORTED_SCHEMAS, validate_price_references
            except ImportError:
                from research_exchange import _report_sections, _validate_pair
                from stock_price_map import SUPPORTED_SCHEMAS, validate_price_references
            if meta.get("schema_version") not in SUPPORTED_SCHEMAS:
                raise ValueError("Company completion requires a stock-research/v3 or v2 pair")
            market, code = review["company"].split("-")
            pair = {key: {field: value[field] for field in ("path", "sha256")} for key, value in completion.items()}
            pair["generator"] = meta.get("generator")
            _validate_pair(pair, {"code": f"{code}.{market}", "name": meta.get("name")},
                           {"valuation_date": meta.get("valuation_date")}, Path(root))
            validate_price_references(document)
            report_input = _report_sections(_check_ref(root, completion["report"]))[0]
            if any(ref["sha256"] not in report_input for ref in review.get("methods", {}).values()):
                raise ValueError("Company report method provenance differs from review methods")
            valuation_date = _date(meta["valuation_date"])
            cutoff = _date(review.get("evidence_cutoff"))
            trigger_date = max([item["as_of"] for item in applicable] +
                               [ref["as_of"] for item in applicable for ref in item.get("evidence", []) if "as_of" in ref])
            if not trigger_date <= cutoff <= as_of or valuation_date > as_of:
                raise ValueError("Company completion does not cover the trigger evidence date")
            if valuation_date < cutoff:
                reassessment = review.get("reassessment")
                if not reassessment or not cutoff <= _date(reassessment.get("as_of")) <= as_of:
                    raise ValueError("Old company report needs a dated targeted reassessment")
                _check_ref(root, reassessment)
            if _method_pair(root, review.get("methods")) != _method_pair(root, record["methods"]):
                compatibility = review.get("compatibility_review")
                if not compatibility:
                    raise ValueError("Company completion needs a method compatibility review")
                _check_ref(root, compatibility)
        elif completion is not None:
            raise ValueError("Pending/cancelled review cannot claim completion")
    return record


def write_handoff(root, record):
    validate_handoff(record, root)
    path = weekly_path(root, record["as_of"], "handoff", record.get("revision"))
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    if path.exists():
        if path.read_text() != raw:
            raise ValueError("Immutable handoff already exists; allocate a new revision")
        return path
    with path.open("x", encoding="utf-8") as stream:
        stream.write(raw)
    return path


def select_adopted(root, as_of, methods):
    """Choose explicit compatible adoption; withdrawal applies across method versions."""
    _date(as_of)
    expected_methods = _method_pair(root, methods)
    records = []
    seen, inactive, withdrawn_sources = set(), set(), set()
    for path in discover_reports(root, "handoff"):
        if path.parent.name > as_of:
            continue
        record = validate_handoff(_load_json(path.read_text()), root)
        if path != weekly_path(root, record["as_of"], "handoff", record.get("revision")):
            raise ValueError("Handoff filename differs from identity")
        if any(item not in seen for item in record.get("supersedes", [])):
            raise ValueError("Supersession target is missing or not earlier")
        seen.add(record["id"])
        if record["status"] in {"adopted", "withdrawn"}:
            inactive.update(record.get("supersedes", []))
            withdrawn_sources.update(ref["sha256"] for ref in record.get("withdrawn_sources", []))
        records.append((path, record))
    for path, record in reversed(records):
        if record["status"] != "adopted" or record["id"] in inactive:
            continue
        sources = _used_sources(record)
        if any(ref["sha256"] in withdrawn_sources for ref in sources):
            continue
        compatible = [_method_pair(root, item["methods"]) for item in record.get("compatibility", [])]
        if expected_methods != _method_pair(root, record["methods"]) and expected_methods not in compatible:
            continue
        return {"path": path.relative_to(Path(root)).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "record": record}
    return None


def _used_sources(record):
    refs = []
    def visit(value):
        if isinstance(value, dict):
            if {"path", "sha256"}.issubset(value):
                refs.append(value)
            else:
                for key, nested in value.items():
                    if key != "withdrawn_sources":
                        visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)
    visit(record)
    return refs


def check_adoption_lifecycle(root, as_of, frozen_record):
    """Recheck explicit withdrawal/supersession, not merely a newer state file."""
    _date(as_of)
    identity = frozen_record["id"]
    source_hashes = {ref["sha256"] for ref in _used_sources(frozen_record)}
    result = {"status": "active", "reason": "No adopted withdrawal or supersession", "evidence": []}
    for path in discover_reports(root, "handoff"):
        if path.parent.name > as_of:
            continue
        record = validate_handoff(_load_json(path.read_text()), root)
        if record["status"] not in {"adopted", "withdrawn"}:
            continue
        withdrawn = source_hashes.intersection(ref["sha256"] for ref in record.get("withdrawn_sources", []))
        if withdrawn or identity in record.get("supersedes", []):
            status = "withdrawn" if withdrawn or record["status"] == "withdrawn" else "superseded"
            if result["status"] != "withdrawn":
                result["status"] = status
            result["reason"] = "Frozen maintenance source explicitly withdrawn or superseded"
            result["evidence"].append(file_ref(root, path, as_of=record["as_of"]))
    return result


def evaluate_repair_exit(observations, trading_days, *, calendar=None):
    """R21 only: three supplied consecutive A-share sessions, complete same-day data."""
    if len(trading_days) != 3 or trading_days != sorted(set(trading_days)):
        raise ValueError("Supply exactly three consecutive authoritative A-share trading days")
    for day in trading_days:
        _date(day)
    if calendar is None:
        raise ValueError("Authoritative trading calendar required to establish consecutiveness")
    if calendar != sorted(set(calendar)):
        raise ValueError("Trading calendar must be sorted and unique")
    for day in calendar:
        _date(day)
    positions = [calendar.index(day) if day in calendar else -1 for day in trading_days]
    if positions[0] < 0 or positions != list(range(positions[0], positions[0] + 3)):
        raise ValueError("R21 window skips or invents a trading session")
    by_day = {}
    for row in observations:
        day = _date(row["date"])
        if day not in trading_days or day in by_day:
            raise ValueError("Observation date is outside the declared window or duplicated")
        if row.get("margin_basis") != "complete_daily_change" or row.get("index_basis") != "official_close":
            raise ValueError("R21 requires full margin change and official index close")
        by_day[day] = row
    results = []
    for day in trading_days:
        row = by_day.get(day, {})
        values = [row.get(key) for key in ("turnover_trillion", "margin_change_yi", "star50_close")]
        if any(value is not None and (type(value) not in {int, float} or not math.isfinite(value)) for value in values):
            raise ValueError("R21 values must be finite numbers or null")
        comparisons = [None if value is None else value > threshold if index < 2 else value >= threshold
                       for index, (value, threshold) in enumerate(zip(values, (1.6, -150, 1516.2)))]
        results.append("not_met" if False in comparisons else "unknown" if None in comparisons else "met")
    return "not_met" if "not_met" in results else "unknown" if "unknown" in results else "met"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command", required=True)
    path_parser = sub.add_parser("path")
    path_parser.add_argument("--date", required=True)
    path_parser.add_argument("--kind", choices=sorted(KINDS), required=True)
    path_parser.add_argument("--revision", type=int)
    path_parser.add_argument("--next", action="store_true")
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("file", type=Path)
    select_parser = sub.add_parser("select")
    select_parser.add_argument("--date", required=True)
    select_parser.add_argument("--canonical", default="framework/investment_framework.md")
    select_parser.add_argument("--compact", default="framework/investment_framework_compact.md")
    args = parser.parse_args()
    if args.command == "path":
        revision = next_revision(args.root, args.date) if args.next else args.revision
        print(weekly_path(args.root, args.date, args.kind, revision))
    elif args.command == "validate":
        validate_handoff(_load_json(args.file.read_text()), args.root)
        print("valid: provenance and structure checked; semantics require review")
    else:
        methods = {role: file_ref(args.root, getattr(args, role)) for role in ("canonical", "compact")}
        print(json.dumps(select_adopted(args.root, args.date, methods), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
