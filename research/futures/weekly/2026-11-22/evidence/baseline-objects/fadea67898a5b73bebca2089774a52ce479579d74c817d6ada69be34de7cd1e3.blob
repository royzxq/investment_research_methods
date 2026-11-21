"""Explicit futures report adoption; no strategy evaluation, data fetch or publication.

Only YYYY-MM-DD-handoff.json is discoverable. Revisions are selected by their
exact report paths at registration, never by the largest -rN suffix. A replace
archives the previous manifest without modifying any adopted report.
Candidate compatibility permits continuity of IDs/evidence and old plans only;
ready/account states, signal validity and execution require fresh evaluation.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

try:
    from .research_paths import artifact_path
except ImportError:
    from research_paths import artifact_path

ROOT = Path(__file__).resolve().parents[1]
CHINA = timezone(timedelta(hours=8))
SCHEMA = "futures-handoff/v2"
LEGACY_SCHEMA = "futures-handoff/v1"
FINGERPRINT_SCHEMA = "futures-effective-rules/v1"
# These are calculation/data dependencies, not the maintenance orchestrators.
METHOD_DEPENDENCIES = ("scripts/futures_strategy.py", "scripts/futures_risk.py")
SOURCE_DEPENDENCIES = METHOD_DEPENDENCIES + ("scripts/future_data.py",)
RULE_ANCHORS = tuple("r-v3-" + name for name in (
    "scope", "pool", "workflow", "data", "calendar", "economics", "quality",
    "signal-t", "plan-t", "signal-v", "plan-v", "expiry", "liquidity", "budget",
    "factors", "account", "margin", "gap", "pair", "event", "stop", "manage", "roll",
    "status", "audit", "shadow", "validation", "tools", "state", "retirement"))
MAINTENANCE_ANCHORS = {"r-v3-tools", "r-v3-state"}
MAINTENANCE_START = "<!-- futures-maintenance-only:start -->"
MAINTENANCE_END = "<!-- futures-maintenance-only:end -->"
# Reviewed orchestration sentences only. New prose is a rule fingerprint input
# until explicitly reviewed here; keywords cannot establish semantic equivalence.
REVIEWED_MAINTENANCE_SENTENCES = (
    "维护分为状态刷新、证据纠错、方法变更，可同时发生：信号触发、事件到期或研究重点变化按已有规则更新状态；"
    "事实/计算/适用性错误撤回并重评；只有规则定义、参数或范围实际改变才作方法修订。",
    "维护分为状态刷新、证据纠错、方法变更，可同时发生。",
    "维护分为状态刷新、证据纠错、方法变更，分别完成。",
    "前两类不升级方法版本、不等待方法适配才研究；若纠错涉及规则本身，同时列方法变更。",
    "采纳版本、取数、刷新与发布按维护入口执行，本文只在末节保留有日期的当期摘要与引用。",
)
CANONICAL = "framework/futures_framework.md"
KINDS = ("market_research", "execution_audit", "change_decision")
SCOPES = {"local", "published"}
STATUSES = {"no_signal", "incomplete", "awaiting_account", "blocked", "ready"}
STATE_START = '<a id="r-v3-state"></a>'
STATE_END = '<a id="r-v3-retirement"></a>'


def digest(content):
    return hashlib.sha256(content).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f"Non-finite JSON value: {value}")


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Non-finite JSON value: {value}")
    return number


def read_json(content):
    return json.loads(content, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_finite_float)


def _day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"Expected ISO date, got {value!r}")
    return date.fromisoformat(value).isoformat()


def _now():
    return datetime.now(CHINA)


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def _sha(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Invalid SHA-256")
    return value


def safe_path(root, relative):
    """Require canonical root-relative POSIX paths, including missing outputs."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("Path must be a nonempty relative POSIX path")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in {"..", "."} for part in relative.split("/")):
        raise ValueError(f"Unsafe path: {relative}")
    if path.as_posix() != relative:
        raise ValueError(f"Noncanonical path: {relative}")
    root = Path(root).resolve()
    result = root / relative
    if not result.resolve().is_relative_to(root):
        raise ValueError(f"Path escapes repository: {relative}")
    return result


def _file_bytes(root, relative):
    path = safe_path(root, relative)
    if not path.is_file():
        raise ValueError(f"Missing regular file: {relative}")
    data = path.read_bytes()
    if not data.strip():
        raise ValueError(f"Empty file: {relative}")
    return data


def _committed(root, relative, content):
    saved = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=root,
                           capture_output=True, check=False)
    if saved.returncode or saved.stdout != content:
        raise ValueError(f"Published source is not identical to HEAD: {relative}")


def _report_day(relative, kind=None):
    choices = kind.replace("_", "-") if kind else "(?:market-research|execution-audit|change-decision)"
    match = re.fullmatch(
        rf"research/futures/weekly/(\d{{4}}-\d{{2}}-\d{{2}})/\1-{choices}(?:-r([2-9]|[1-9]\d+))?\.md",
        relative,
    )
    if not match:
        raise ValueError(f"Wrong report track, type, date directory or revision: {relative}")
    return _day(match[1])


def _legacy_fingerprint(content):
    """v1 format is retained solely to authenticate explicitly supplied history."""
    text = content.decode("utf-8")
    if text.count(STATE_START) != 1 or text.count(STATE_END) != 1:
        raise ValueError("Canonical must contain exactly one state/retirement anchor pair")
    start, end = text.index(STATE_START), text.index(STATE_END)
    if start >= end:
        raise ValueError("Canonical state anchors are out of order")
    rules = text[:start + len(STATE_START)] + text[end:]
    return digest(rules.encode("utf-8"))


def _rule_text(text):
    """Ignore headings/blank layout, not prose, formulas, tables or code."""
    result, fence = [], None
    for line in text.splitlines():
        stripped = line.strip()
        fence_match = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence_match:
            token = fence_match[1]
            if fence is None:
                fence = token[0]
            elif token[0] == fence:
                fence = None
        elif fence is None and re.match(r"^#{1,6}\s", stripped):
            continue
        if stripped:
            result.append(stripped)
    return "\n".join(result)


def _maintenance_sentence_key(text):
    """Normalize presentation around a reviewed sentence, keeping its wording."""
    text = re.sub(r"\[([^\]]+)\]\([^\n)]*\)", r"\1", text)
    text = re.sub(r"(?m)^\s*(?:[-+*]|\d+\.)\s+", "", text)
    return re.sub(r"\s+|[*_`]", "", text)


def _maintenance_rules(text):
    """Exclude exact reviewed maintenance sentences; preserve all unknown prose.

    Arbitrary prose equivalence is not machine-decidable here. Conservative
    fallback retains a new sentence (including a new gate) in the effective
    fingerprint; a future reviewed maintenance-only wording can be added to the
    explicit list. Display headings and formatting retain their usual meaning.
    """
    approved = {_maintenance_sentence_key(sentence) for sentence in REVIEWED_MAINTENANCE_SENTENCES}
    sentences = re.findall(r"[^。]+。|[^。]+$", _rule_text(text))
    return "\n".join(sentence.strip() for sentence in sentences
                     if _maintenance_sentence_key(sentence) not in approved)


def _rule_sections(text):
    anchors = list(re.finditer(r'<a id="(r-v3-[a-z-]+)"></a>', text))
    names = [item[1] for item in anchors]
    if len(names) != len(set(names)) or set(names) != set(RULE_ANCHORS):
        raise ValueError("Canonical requires the exact unique stable v3 rule anchors")
    if names != list(RULE_ANCHORS):
        raise ValueError("Canonical rule anchors are out of order")
    # The unanchored preamble is provenance/reading navigation. All effective
    # rules must live under the stable anchors; headings are display labels.
    sections = {}
    for index, item in enumerate(anchors):
        name = item[1]
        body = text[item.end():anchors[index + 1].start() if index + 1 < len(anchors) else len(text)]
        if name in MAINTENANCE_ANCHORS:
            continue
        if MAINTENANCE_START in body or MAINTENANCE_END in body:
            if name != "r-v3-workflow" or body.count(MAINTENANCE_START) != 1 or body.count(MAINTENANCE_END) != 1:
                raise ValueError("Maintenance-only markers are allowed once in workflow only")
            start, end = body.index(MAINTENANCE_START), body.index(MAINTENANCE_END)
            if start >= end:
                raise ValueError("Maintenance-only markers are out of order")
            excluded = body[start + len(MAINTENANCE_START):end]
            retained = _maintenance_rules(excluded)
            body = body[:start] + retained + body[end + len(MAINTENANCE_END):]
        normalized = _rule_text(body)
        if not normalized:
            raise ValueError(f"Empty effective rule section: {name}")
        sections[name] = digest(normalized.encode("utf-8"))
    return sections


def _effective_sha(rule_sections, dependencies):
    payload = {"fingerprint_schema": FINGERPRINT_SCHEMA, "rule_sections": rule_sections,
               "dependencies": dependencies}
    return digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _python_semantics(content):
    class StripDocstrings(ast.NodeTransformer):
        def generic_visit(self, node):
            node = super().generic_visit(node)
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = node.body
                if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                    node.body = body[1:]
            return node
    try:
        parsed = StripDocstrings().visit(ast.parse(content.decode("utf-8")))
    except SyntaxError as error:
        raise ValueError("Calculation dependency is not valid Python") from error
    return digest(ast.dump(parsed, annotate_fields=True, include_attributes=False).encode("utf-8"))


def _fingerprint_bytes(content, sources, *, legacy_layout=False):
    text = content.decode("utf-8")
    if legacy_layout and MAINTENANCE_START not in text:
        # One known pre-marker operational paragraph; never hide arbitrary rule
        # prose on the strength of a version string or a numeric-only diff.
        text, count = re.subn(r"(?m)^(维护分为状态刷新、证据纠错、方法变更[^\n]*)$",
                             MAINTENANCE_START + r"\n\1\n" + MAINTENANCE_END, text)
        if count > 1:
            raise ValueError("Ambiguous legacy maintenance paragraph")
    match = re.search(r"^#\s+[^\n]*\b(v\d+(?:\.\d+)+)\b", text, re.MULTILINE)
    if not match:
        raise ValueError("Canonical header has no method version")
    sections = _rule_sections(text)
    dependencies = {path: _python_semantics(sources[path]) for path in METHOD_DEPENDENCIES}
    return {"path": CANONICAL, "version": match[1], "fingerprint_schema": FINGERPRINT_SCHEMA,
            "rule_sections": sections, "dependencies": dependencies,
            "source_dependencies": {path: digest(sources[path]) for path in SOURCE_DEPENDENCIES},
            "sha256": _effective_sha(sections, dependencies), "canonical_full_sha256": digest(content)}


def method_fingerprint(root):
    content = _file_bytes(root, CANONICAL)
    sources = {path: _file_bytes(root, path) for path in SOURCE_DEPENDENCIES}
    return _fingerprint_bytes(content, sources)


def _ref(root, relative):
    return {"path": relative, "sha256": digest(_file_bytes(root, relative))}


def _validate_ref(root, ref, *, published=False):
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise ValueError("File reference requires exactly path and sha256")
    data = _file_bytes(root, ref["path"])
    if digest(data) != _sha(ref["sha256"]):
        raise ValueError(f"Source hash mismatch: {ref['path']}")
    if published:
        _committed(root, ref["path"], data)
    return data


def _validate_audit(content, day, market_day, method_version):
    text = content.decode("utf-8")
    blocks = re.findall(r"^```json\s*\n(.*?)^```\s*$", text, re.MULTILINE | re.DOTALL)
    if len(blocks) != 1:
        raise ValueError("Adopted audit must have exactly one JSON block")
    audit = read_json(blocks[0])
    if not isinstance(audit, dict) or audit.get("audit_schema_version") != 3:
        raise ValueError("Current handoff requires execution audit schema 3")
    if audit.get("as_of_date") != day:
        raise ValueError("Audit research date does not match handoff")
    if audit.get("framework", {}).get("version") != method_version:
        raise ValueError("Audit candidate method version does not match handoff")
    if audit.get("snapshot", {}).get("market_trade_date") != market_day:
        raise ValueError("Audit market date does not match handoff")
    candidates = audit.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("Audit candidates must be a list")
    for candidate in candidates:
        if not isinstance(candidate, dict) or candidate.get("strategy") not in {"trend", "economic_reversion"}:
            raise ValueError("Audit contains an incompatible candidate strategy")
        if candidate.get("status") not in STATUSES:
            raise ValueError("Audit contains an unknown candidate status")
        if _day(candidate.get("trade_date")) > market_day:
            raise ValueError("Candidate trade date is later than market date")
        signal_day = (candidate.get("plan") or {}).get("signal_date")
        if signal_day is not None and _day(signal_day) > market_day:
            raise ValueError("Candidate signal is later than market date")


def manifest_relative(day):
    day = _day(day)
    return artifact_path("futures", "handoff", day, ROOT).relative_to(ROOT).as_posix()


def _validate_history(root, ref, as_of, published, seen):
    relative = ref.get("path") if isinstance(ref, dict) else None
    match = re.fullmatch(
        r"research/futures/weekly/(\d{4}-\d{2}-\d{2})/evidence/handoff-history/([0-9a-f]{64})\.json",
        relative or "",
    )
    if not match or _day(match[1]) > as_of or match[2] != ref.get("sha256"):
        raise ValueError("Invalid archived handoff reference")
    if relative in seen:
        raise ValueError("Cyclic handoff history")
    seen.add(relative)
    data = _validate_ref(root, ref, published=published)
    prior = read_json(data)
    if prior.get("as_of_date") != match[1]:
        raise ValueError("Archived handoff date mismatch")
    # Original reports remain immutable even when an adoption changes.
    _validate_payload(root, prior, published=published, historical=True, seen=seen)


def _validate_payload(root, document, *, published=False, historical=False, seen=None):
    expected = {"schema", "status", "scope", "as_of_date", "registered_at", "market_as_of_date",
                "method", "artifacts", "corrections", "previous_handoff"}
    if isinstance(document, dict) and document.get("schema") == SCHEMA:
        expected.add("legacy_migration")
    if not isinstance(document, dict) or set(document) != expected:
        raise ValueError("Unknown or missing handoff fields")
    if document["schema"] not in {SCHEMA, LEGACY_SCHEMA} or document["status"] != "adopted":
        raise ValueError("Unknown handoff schema or adoption status")
    if document["scope"] not in SCOPES:
        raise ValueError("Unknown handoff scope")
    day, market_day = _day(document["as_of_date"]), _day(document["market_as_of_date"])
    now = _now()
    try:
        registered = datetime.fromisoformat(document["registered_at"])
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid registration timestamp") from error
    if registered.tzinfo is None or registered.utcoffset() != CHINA.utcoffset(None):
        raise ValueError("Registration timestamp must have +08:00 timezone")
    if market_day > day or day > registered.date().isoformat() or registered > now:
        raise ValueError("Future market, research or registration date")
    method = document["method"]
    fields = {"path", "version", "revision", "sha256", "canonical_full_sha256"}
    legacy = document["schema"] == LEGACY_SCHEMA
    if not legacy:
        fields |= {"fingerprint_schema", "rule_sections", "dependencies", "source_dependencies"}
    if not isinstance(method, dict) or set(method) != fields:
        raise ValueError("Invalid method fingerprint fields")
    if method["path"] != CANONICAL:
        raise ValueError("Method must reference the canonical framework")
    for field in ("version", "revision"):
        _text(method[field], f"method.{field}")
    _sha(method["sha256"])
    _sha(method["canonical_full_sha256"])
    if not legacy:
        if method["fingerprint_schema"] != FINGERPRINT_SCHEMA:
            raise ValueError("Unknown effective-rule fingerprint schema")
        sections, dependencies = method["rule_sections"], method["dependencies"]
        if not isinstance(sections, dict) or set(sections) != set(RULE_ANCHORS) - MAINTENANCE_ANCHORS:
            raise ValueError("Invalid effective-rule section fingerprints")
        if not isinstance(dependencies, dict) or set(dependencies) != set(METHOD_DEPENDENCIES):
            raise ValueError("Invalid method dependency fingerprints")
        sources = method["source_dependencies"]
        if not isinstance(sources, dict) or set(sources) != set(SOURCE_DEPENDENCIES):
            raise ValueError("Invalid source dependency provenance")
        for value in list(sections.values()) + list(dependencies.values()) + list(sources.values()):
            _sha(value)
        if method["sha256"] != _effective_sha(sections, dependencies):
            raise ValueError("Method fingerprint integrity mismatch")
    current = method_fingerprint(root)
    compatible = not legacy and method["version"] == current["version"] and method["sha256"] == current["sha256"]
    if not compatible and not historical:
        reason = "Legacy v1 requires explicit reviewed migration" if legacy else "Method is incompatible"
        raise ValueError(reason + "; --allow-historical permits facts/corrections only")
    if published:
        _committed(root, CANONICAL, _file_bytes(root, CANONICAL))
        for relative in SOURCE_DEPENDENCIES:
            _committed(root, relative, _file_bytes(root, relative))
    artifacts = document["artifacts"]
    if not isinstance(artifacts, dict) or set(artifacts) != set(KINDS) or not any(artifacts.values()):
        raise ValueError("Handoff must specify all three artifact slots and adopt at least one")
    for kind, ref in artifacts.items():
        if ref is None:
            continue
        content = _validate_ref(root, ref, published=published)
        content.decode("utf-8")
        if _report_day(ref["path"], kind) != day:
            raise ValueError("Adopted report is not from the handoff period")
        if kind == "execution_audit":
            _validate_audit(content, day, market_day, method["version"])
    corrections = document["corrections"]
    if not isinstance(corrections, dict) or set(corrections) != {"scope", "supersedes"}:
        raise ValueError("Invalid correction fields")
    scopes, originals = corrections["scope"], corrections["supersedes"]
    if not isinstance(scopes, list) or not isinstance(originals, list) or bool(scopes) != bool(originals):
        raise ValueError("Correction scope and superseded originals must both be provided or both be empty")
    for value in scopes:
        _text(value, "correction scope")
    original_paths = set()
    for ref in originals:
        _validate_ref(root, ref, published=published)
        if _report_day(ref["path"]) > day:
            raise ValueError("Superseded original is from a future period")
        if ref["path"] in original_paths:
            raise ValueError("Duplicate superseded original")
        original_paths.add(ref["path"])
    previous = document["previous_handoff"]
    if previous is not None:
        _validate_history(root, previous, day, published, set() if seen is None else seen)
    if not legacy and document["legacy_migration"] is not None:
        _validate_migration(root, document, published=published)
    return compatible


def _validate_migration(root, document, *, published=False):
    proof = document["legacy_migration"]
    expected = {"baseline_provenance", "legacy_manifest_sha256", "baseline_sources"}
    if not isinstance(proof, dict) or set(proof) != expected:
        raise ValueError("Invalid explicit legacy migration proof")
    _text(proof["baseline_provenance"], "baseline provenance")
    previous = document["previous_handoff"]
    if previous is None or previous["sha256"] != _sha(proof["legacy_manifest_sha256"]):
        raise ValueError("Migration must preserve the exact v1 manifest")
    old = read_json(_validate_ref(root, previous, published=published))
    if old.get("schema") != LEGACY_SCHEMA:
        raise ValueError("Migration source must be v1")
    refs = proof["baseline_sources"]
    if not isinstance(refs, dict) or set(refs) != {CANONICAL, *SOURCE_DEPENDENCIES}:
        raise ValueError("Migration requires canonical and all source dependency originals")
    sources = {path: _validate_ref(root, ref, published=published) for path, ref in refs.items()}
    canonical = sources.pop(CANONICAL)
    if digest(canonical) != old["method"]["canonical_full_sha256"] or _legacy_fingerprint(canonical) != old["method"]["sha256"]:
        raise ValueError("Legacy canonical proof does not match v1 source hashes")
    baseline = _fingerprint_bytes(canonical, sources, legacy_layout=True)
    if baseline["version"] != document["method"]["version"] or baseline["sha256"] != document["method"]["sha256"]:
        raise ValueError("Migrated effective rules/dependencies differ from reviewed baseline")
    # A migration may re-express identity, never replace the adopted evidence or
    # quietly change its original signal/registration/expiry fields.
    for key in ("as_of_date", "market_as_of_date", "scope", "artifacts", "corrections"):
        if old[key] != document[key]:
            raise ValueError("Migration changed adopted evidence or scope")


def migrate(root, relative, *, baseline_root, baseline_provenance, method_revision):
    root, baseline_root = Path(root).resolve(), Path(baseline_root).resolve()
    original = check(root, relative, allow_historical=True)
    document = original["handoff"]
    if document["schema"] != LEGACY_SCHEMA:
        raise ValueError("Only legacy v1 manifests need explicit migration")
    _text(baseline_provenance, "baseline provenance")
    content = _file_bytes(baseline_root, CANONICAL)
    if digest(content) != document["method"]["canonical_full_sha256"] or _legacy_fingerprint(content) != document["method"]["sha256"]:
        raise ValueError("Legacy canonical proof does not match v1 source hashes")
    sources = {path: _file_bytes(baseline_root, path) for path in SOURCE_DEPENDENCIES}
    baseline = _fingerprint_bytes(content, sources, legacy_layout=True)
    current = method_fingerprint(root)
    if baseline["version"] != current["version"] or baseline["sha256"] != current["sha256"]:
        raise ValueError("Legacy migration cannot approve changed effective rules/dependencies")
    # v1 did not record dependency identity. The supplied original sources and
    # explicit provenance are the reviewer's attestation, not an inferred fact.
    sources[CANONICAL] = content
    baseline_id = digest(json.dumps({path: digest(data) for path, data in sources.items()}, sort_keys=True).encode())
    refs = {}
    directory = f"research/futures/weekly/{document['as_of_date']}/evidence/handoff-history/method-baseline-{baseline_id}"
    for path, data in sources.items():
        target = f"{directory}/{path}"
        absolute = safe_path(root, target)
        if absolute.exists():
            if absolute.read_bytes() != data:
                raise ValueError("Frozen migration baseline has changed")
        else:
            _atomic_write(absolute, data)
        refs[path] = {"path": target, "sha256": digest(data)}
    proof = {"baseline_provenance": baseline_provenance,
             "legacy_manifest_sha256": original["manifest_sha256"], "baseline_sources": refs}
    return register(root, document["as_of_date"], document["market_as_of_date"],
                    scope=document["scope"], method_version=current["version"], method_revision=method_revision,
                    artifacts={kind: ref["path"] for kind, ref in document["artifacts"].items() if ref},
                    correction_scope=document["corrections"]["scope"],
                    supersedes=[ref["path"] for ref in document["corrections"]["supersedes"]],
                    replace=True, legacy_migration=proof)


def check(root, relative, *, scope="local", allow_historical=False):
    if scope not in SCOPES:
        raise ValueError("Unknown requested scope")
    data = _file_bytes(root, relative)
    document = read_json(data)
    if not isinstance(document, dict) or relative != manifest_relative(document.get("as_of_date")):
        raise ValueError("Only the formal dated handoff may be consumed")
    compatible = _validate_payload(root, document, published=scope == "published", historical=allow_historical)
    if scope == "published":
        _committed(root, relative, data)
    return {"status": "resolved", "manifest": relative, "manifest_sha256": digest(data),
            "method_compatible": compatible,
            "execution_reuse": False,
            "candidate_continuity_compatible": compatible and document["artifacts"]["execution_audit"] is not None,
            "requires_fresh_evaluation": True,
            "stored_scope": document["scope"], "consumption_scope": scope,
            "publication_verified": scope == "published",
            "legacy_fallback_allowed": False, "handoff": document}


def resolve(root, as_of, *, before=False, scope="local", allow_historical=False, kind=None):
    root = Path(root).resolve()
    day = _day(as_of)
    if day > _now().date().isoformat():
        raise ValueError("Resolution date may not be in the future")
    if scope not in SCOPES:
        raise ValueError("Unknown requested scope")
    if kind is not None:
        kind = kind.replace("-", "_")
        if kind not in KINDS:
            raise ValueError("Unknown requested artifact kind")
    base = safe_path(root, "research/futures/weekly")
    candidates = []
    for path in base.glob("*/*-handoff.json"):
        relative = path.relative_to(Path(root).resolve()).as_posix()
        match = re.fullmatch(r"research/futures/weekly/(\d{4}-\d{2}-\d{2})/\1-handoff\.json", relative)
        if not match:
            continue
        record_day = _day(match[1])
        if record_day <= day and not (before and record_day == day):
            candidates.append((record_day, relative))
    for _, relative in sorted(candidates, reverse=True):
        # Never skip a malformed newest record to produce a comforting older result.
        document = read_json(_file_bytes(root, relative))
        if not isinstance(document, dict) or document.get("scope") not in SCOPES or document.get("status") != "adopted":
            raise ValueError(f"Invalid adoption scope or status: {relative}")
        if kind is not None:
            # Validate even an empty-type record before looking past it; corrupted
            # manifests/references cannot be hidden by requesting another type.
            inspected = check(root, relative, scope="local", allow_historical=True)
            if inspected["handoff"]["artifacts"][kind] is None:
                continue
        result = check(root, relative, scope=scope, allow_historical=allow_historical)
        if kind is not None:
            result["requested_kind"] = kind
            result["artifact"] = result["handoff"]["artifacts"][kind]
        return result
    return {"status": "missing", "scope": scope, "as_of_date": day, "requested_kind": kind,
            "legacy_fallback_allowed": True, "execution_reuse": False,
            "candidate_continuity_compatible": False, "requires_fresh_evaluation": True,
            "reason": "No eligible formal adoption; explicitly inspect legacy reports, never auto-select revisions"}


def _atomic_write(path, data, *, replace=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", suffix=".partial", delete=False) as sink:
        temporary = Path(sink.name)
        sink.write(data)
        sink.flush()
        os.fsync(sink.fileno())
    try:
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def _registration_lock(root, day):
    lock = safe_path(root, f"output/locks/futures-handoff/{day}.lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def register(root, as_of, market_as_of, *, scope, method_version, method_revision,
             artifacts=None, correction_scope=None, supersedes=None, replace=False, legacy_migration=None):
    root = Path(root).resolve()
    day, market_day = _day(as_of), _day(market_as_of)
    relative = manifest_relative(day)
    path = safe_path(root, relative)
    with _registration_lock(root, day):
        if path.exists() and not replace:
            raise ValueError("Same-day adoption exists; explicit --replace is required")
        previous_data = path.read_bytes() if path.exists() else None
        previous_result = None
        if previous_data is not None:
            # An explicit replacement cannot launder changed original sources.
            previous_result = check(root, relative, allow_historical=True)
        method = method_fingerprint(root)
        if method_version != method["version"]:
            raise ValueError("Requested method version does not match canonical")
        method["revision"] = _text(method_revision, "method revision")
        provided = artifacts or {}
        if set(provided) - set(KINDS):
            raise ValueError("Unknown artifact type")
        references = {kind: _ref(root, provided[kind]) if provided.get(kind) else None for kind in KINDS}
        if previous_result and not previous_result["method_compatible"] and legacy_migration is None:
            old_audit = previous_result["handoff"]["artifacts"]["execution_audit"]
            if old_audit is not None and references["execution_audit"] == old_audit:
                raise ValueError("Cannot re-adopt an incompatible old audit; use explicit legacy migration or a freshly reviewed audit")
        document = {"schema": SCHEMA, "status": "adopted", "scope": scope,
                    "as_of_date": day, "registered_at": _now().isoformat(),
                    "market_as_of_date": market_day, "method": method, "artifacts": references,
                    "corrections": {"scope": correction_scope or [],
                                    "supersedes": [_ref(root, item) for item in supersedes or []]},
                    "previous_handoff": None, "legacy_migration": None}
        _validate_payload(root, document, published=scope == "published")
        if previous_data is not None:
            previous_hash = digest(previous_data)
            archived = f"research/futures/weekly/{day}/evidence/handoff-history/{previous_hash}.json"
            archived_path = safe_path(root, archived)
            if archived_path.exists():
                if archived_path.read_bytes() != previous_data:
                    raise ValueError("Previous handoff archive has changed")
            else:
                _atomic_write(archived_path, previous_data)
            document["previous_handoff"] = {"path": archived, "sha256": previous_hash}
        document["legacy_migration"] = legacy_migration
        # A second pass catches source changes during registration. The manifest
        # is always published last; temporary writes never become discoverable.
        _validate_payload(root, document, published=False)
        if scope == "published":
            # The newly-created history and manifest can only become published
            # after commit; adopted report bytes and canonical must already match.
            for ref in references.values():
                if ref:
                    _validate_ref(root, ref, published=True)
            for ref in document["corrections"]["supersedes"]:
                _validate_ref(root, ref, published=True)
            _committed(root, CANONICAL, _file_bytes(root, CANONICAL))
        if previous_data is not None and path.read_bytes() != previous_data:
            raise ValueError("Formal handoff changed during registration")
        payload = (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
        _atomic_write(path, payload, replace=previous_data is not None)
    return {"status": "registered", "manifest": relative, "manifest_sha256": digest(payload),
            "scope": scope, "published_consumable": False if scope == "published" else None,
            "handoff": document}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("register", help="Explicitly adopt exact report paths")
    make.add_argument("--as-of", required=True)
    make.add_argument("--market-as-of", required=True)
    make.add_argument("--scope", choices=sorted(SCOPES), default="local")
    make.add_argument("--method-version", required=True)
    make.add_argument("--method-revision", required=True)
    for kind in KINDS:
        make.add_argument("--" + kind.replace("_", "-"))
    make.add_argument("--correction-scope", action="append", default=[])
    make.add_argument("--supersedes", action="append", default=[])
    make.add_argument("--replace", action="store_true")
    migrate_parser = commands.add_parser("migrate", help="Explicitly migrate v1 using reviewed historical originals")
    migrate_parser.add_argument("manifest")
    migrate_parser.add_argument("--baseline-root", type=Path, required=True)
    migrate_parser.add_argument("--baseline-provenance", required=True)
    migrate_parser.add_argument("--method-revision", required=True)
    discover = commands.add_parser("resolve")
    discover.add_argument("--as-of", required=True)
    discover.add_argument("--before", action="store_true")
    discover.add_argument("--kind", choices=[kind.replace("_", "-") for kind in KINDS])
    inspect = commands.add_parser("check")
    inspect.add_argument("manifest")
    for command in (discover, inspect):
        command.add_argument("--scope", choices=sorted(SCOPES), default="local")
        command.add_argument("--allow-historical", action="store_true",
                             help="Allow incompatible methods only for facts/corrections, never candidate reuse")
    args = parser.parse_args(argv)
    try:
        if args.command == "register":
            result = register(args.root, args.as_of, args.market_as_of, scope=args.scope,
                              method_version=args.method_version, method_revision=args.method_revision,
                              artifacts={kind: getattr(args, kind) for kind in KINDS},
                              correction_scope=args.correction_scope, supersedes=args.supersedes,
                              replace=args.replace)
        elif args.command == "migrate":
            result = migrate(args.root, args.manifest, baseline_root=args.baseline_root,
                             baseline_provenance=args.baseline_provenance, method_revision=args.method_revision)
        elif args.command == "resolve":
            result = resolve(args.root.resolve(), args.as_of, before=args.before, scope=args.scope,
                             allow_historical=args.allow_historical, kind=args.kind)
        else:
            result = check(args.root, args.manifest, scope=args.scope, allow_historical=args.allow_historical)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if result["status"] == "missing" else 0
    except (ValueError, OSError, UnicodeError, TypeError, AttributeError) as error:
        print(json.dumps({"status": "error", "legacy_fallback_allowed": False, "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
