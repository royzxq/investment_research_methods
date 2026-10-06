"""Read-only acceptance of batch requests and stock-research/v2 artifact pairs.

Acceptance checks identity, paths, hashes, structure and chronology. It does not
run research, validate investment evidence, change latest caches or write files.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from zoneinfo import ZoneInfo

try:
    from .research_paths import company_path
    from .stock_price_map import fields, iso_date, no_duplicates, reject_constant, require, string, validate_document
except ImportError:
    from research_paths import company_path
    from stock_price_map import fields, iso_date, no_duplicates, reject_constant, require, string, validate_document


REQUEST_SCHEMA = "stock-research-request/v1"
RESULT_SCHEMA = "stock-research-result/v1"
GENERATORS = {"codex", "claude"}
SHA256 = re.compile(r"[0-9a-f]{64}")
REQUEST_KEYS = {"schema_version", "batch_id", "created_at", "valuation_date", "generators", "tasks"}
TASK_KEYS = {"task_id", "code", "name", "sources", "data_pack", "data_pack_meta"}
RESULT_KEYS = {"schema_version", "batch_id", "request_sha256", "created_at", "results"}
ENTRY_KEYS = {"task_id", "generator", "status", "reason", "started_at", "completed_at", "report", "price_map"}


def _strict_json(raw, label):
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates, parse_constant=reject_constant)

    def finite(item):
        if isinstance(item, float):
            require(math.isfinite(item), f"{label}: nonfinite JSON number")
        elif isinstance(item, dict):
            for nested in item.values():
                finite(nested)
        elif isinstance(item, list):
            for nested in item:
                finite(nested)

    finite(value)
    return value


def _timestamp(value, label):
    string(value, label)
    require(re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T", value), f"{label}: expected ISO timestamp")
    moment = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    require(moment.tzinfo is not None and moment.utcoffset() is not None, f"{label}: timezone required")
    return moment


def _batch_id(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{32}", value), "batch_id: expected lowercase UUID hex")


def _sha(value, label):
    require(isinstance(value, str) and SHA256.fullmatch(value), f"{label}: expected lowercase SHA-256")


def _contained_path(root, relative, label):
    string(relative, label)
    path = PurePosixPath(relative)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in relative,
            f"{label}: expected relative path without parent traversal")
    resolved_root = Path(root).resolve(strict=True)
    resolved = (resolved_root / path).resolve(strict=True)
    require(resolved.is_relative_to(resolved_root), f"{label}: path escapes root")
    require(resolved.is_file(), f"{label}: expected file")
    return resolved


def _artifact(descriptor, root, label):
    fields(descriptor, {"path", "sha256"}, label)
    _sha(descriptor["sha256"], f"{label}.sha256")
    path = _contained_path(root, descriptor["path"], f"{label}.path")
    raw = path.read_bytes()
    require(bool(raw), f"{label}: empty file")
    require(hashlib.sha256(raw).hexdigest() == descriptor["sha256"], f"{label}.sha256: file mismatch")
    return path, raw


def _validate_request(request, request_root):
    fields(request, REQUEST_KEYS, "request")
    require(request["schema_version"] == REQUEST_SCHEMA, "request.schema_version: unsupported version")
    _batch_id(request["batch_id"])
    created = _timestamp(request["created_at"], "request.created_at")
    valuation = iso_date(request["valuation_date"], "request.valuation_date")
    require(valuation <= created.astimezone(ZoneInfo("Asia/Shanghai")).date(),
            "request.valuation_date: later than request creation date")
    generators = request["generators"]
    require(isinstance(generators, list) and generators, "request.generators: expected nonempty list")
    require(all(isinstance(g, str) and g in GENERATORS for g in generators), "request.generators: unsupported generator")
    require(len(set(generators)) == len(generators), "request.generators: duplicates")
    require(isinstance(request["tasks"], list) and request["tasks"], "request.tasks: expected nonempty list")
    seen = set()
    for i, task in enumerate(request["tasks"]):
        label = f"request.tasks[{i}]"
        fields(task, TASK_KEYS, label)
        string(task["code"], f"{label}.code")
        match = re.fullmatch(r"([0-9]{6})\.(SH|SZ)|([0-9]{5})\.(HK)", task["code"])
        require(match is not None, f"{label}.code: expected SH/SZ/HK listing")
        code, market = task["code"].split(".")
        require(task["task_id"] == f"{market}-{code}", f"{label}.task_id: inconsistent with code")
        require(task["task_id"] not in seen, f"{label}.task_id: duplicate security")
        seen.add(task["task_id"])
        string(task["name"], f"{label}.name")
        sources = task["sources"]
        require(isinstance(sources, list) and sources, f"{label}.sources: expected nonempty list")
        for source in sources:
            string(source, f"{label}.sources")
        require(len(set(sources)) == len(sources), f"{label}.sources: duplicates")
        require(isinstance(task["data_pack_meta"], dict), f"{label}.data_pack_meta: expected object")
        _artifact(task["data_pack"], request_root, f"{label}.data_pack")
    return request


def load_request(path):
    """Return a validated request; data packs resolve relative to its directory."""
    path = Path(path)
    return _validate_request(_strict_json(path.read_bytes(), "request"), path.parent)


def _report_sections(raw):
    text = raw.decode("utf-8")
    require(bool(text.strip()), "report: empty text")
    visible = []
    fence = None
    comment = False
    for line in text.splitlines():
        if fence is not None:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line):
                fence = None
            continue
        # HTML comments do not create sections or bodies. Code blocks handle
        # their own contents first, so a literal <!-- there is not a comment.
        fragments = []
        remaining = line
        while remaining:
            if comment:
                end = remaining.find("-->")
                if end == -1:
                    break
                remaining = remaining[end + 3:]
                comment = False
            else:
                start = remaining.find("<!--")
                if start == -1:
                    fragments.append(remaining)
                    break
                fragments.append(remaining[:start])
                remaining = remaining[start + 4:]
                comment = True
        line = "".join(fragments)
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            fence = marker[1]
            continue
        visible.append(line)
    section_pattern = re.compile(r"^#{1,6}[ \t]+(?:\*\*)?([0-8])(?:[.．、:：)）|｜—–-](?![0-9])|\s|$)")
    headings = [(i, int(match[1])) for i, line in enumerate(visible) if (match := section_pattern.match(line))]
    require([number for _, number in headings] == list(range(9)), "report: requires sections 0-8 in order")
    for index, (start, number) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(visible)
        require(any(line.strip() and not re.match(r"^#{1,6}\s", line) for line in visible[start + 1:end]),
                f"report.section {number}: empty body")


def _validate_pair(entry, task, request, artifact_root):
    report_path, report_raw = _artifact(entry["report"], artifact_root, "result.report")
    _, price_raw = _artifact(entry["price_map"], artifact_root, "result.price_map")
    code, market = task["code"].split(".")
    day = request["valuation_date"]
    generator = entry["generator"]
    match = re.fullmatch(rf"investment-{code}-{day}-price-map-{generator}(?:-r([0-9]+))?\.json",
                         PurePosixPath(entry["price_map"]["path"]).name)
    require(match is not None, "result.price_map.path: incorrect date/code/generator filename")
    revision = int(match[1]) if match[1] is not None else None
    require(revision is None or (revision >= 2 and str(revision) == match[1]), "result.price_map.path: invalid revision")
    for kind, descriptor in (("research", entry["report"]), ("price-map", entry["price_map"])):
        expected = company_path(market, code, day, kind, artifact_root, revision=revision, generator=generator)
        require(descriptor["path"] == expected.relative_to(artifact_root).as_posix(),
                f"result.{kind}.path: not the paired formal artifact path")
    document = _strict_json(price_raw, "price_map")
    validate_document(document)
    meta = document["meta"]
    for key, expected in (("code", task["code"]), ("name", task["name"]), ("valuation_date", day), ("generator", generator)):
        require(meta.get(key) == expected, f"price_map.meta.{key}: inconsistent with request/result")
    require(meta["report_path"] == entry["report"]["path"], "price_map.meta.report_path: inconsistent with paired report")
    require(_contained_path(artifact_root, meta["report_path"], "price_map.meta.report_path") == report_path,
            "price_map.meta.report_path: inconsistent report target")
    _report_sections(report_raw)


def load_results(result_path, request_path, artifact_root):
    """Return a validated manifest; omitted providers remain absent, never failed."""
    request_path = Path(request_path)
    request_raw = request_path.read_bytes()
    request = _validate_request(_strict_json(request_raw, "request"), request_path.parent)
    result = _strict_json(Path(result_path).read_bytes(), "results")
    fields(result, RESULT_KEYS, "results")
    require(result["schema_version"] == RESULT_SCHEMA, "results.schema_version: unsupported version")
    _batch_id(result["batch_id"])
    require(result["batch_id"] == request["batch_id"], "results.batch_id: inconsistent with request")
    _sha(result["request_sha256"], "results.request_sha256")
    require(result["request_sha256"] == hashlib.sha256(request_raw).hexdigest(), "results.request_sha256: request bytes mismatch")
    created = _timestamp(result["created_at"], "results.created_at")
    requested = _timestamp(request["created_at"], "request.created_at")
    require(created >= requested, "results.created_at: before request")
    require(isinstance(result["results"], list), "results.results: expected list")
    tasks = {task["task_id"]: task for task in request["tasks"]}
    seen = set()
    for i, entry in enumerate(result["results"]):
        label = f"results.results[{i}]"
        fields(entry, ENTRY_KEYS, label)
        string(entry["task_id"], f"{label}.task_id")
        require(entry["task_id"] in tasks, f"{label}.task_id: not in request")
        require(isinstance(entry["generator"], str) and entry["generator"] in request["generators"],
                f"{label}.generator: not planned in request")
        identity = (entry["task_id"], entry["generator"])
        require(identity not in seen, f"{label}: duplicate task/generator")
        seen.add(identity)
        started = _timestamp(entry["started_at"], f"{label}.started_at")
        completed = _timestamp(entry["completed_at"], f"{label}.completed_at")
        require(requested <= started <= completed <= created, f"{label}: invalid time order")
        require(entry["status"] in ("completed", "failed"), f"{label}.status: unsupported state")
        if entry["status"] == "failed":
            string(entry["reason"], f"{label}.reason")
            require(entry["report"] is None and entry["price_map"] is None, f"{label}: failed result must have null artifacts")
        else:
            require(entry["reason"] is None, f"{label}: completed result must have null reason")
            _validate_pair(entry, tasks[entry["task_id"]], request, Path(artifact_root))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    request_parser = sub.add_parser("check-request")
    request_parser.add_argument("path")
    result_parser = sub.add_parser("check-results")
    result_parser.add_argument("path")
    result_parser.add_argument("--request", required=True)
    result_parser.add_argument("--artifact-root", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "check-request":
            manifest = load_request(args.path)
            summary = {"batch_id": manifest["batch_id"], "tasks": len(manifest["tasks"]), "generators": len(manifest["generators"])}
        else:
            manifest = load_results(args.path, args.request, args.artifact_root)
            summary = {"batch_id": manifest["batch_id"], "results": len(manifest["results"]),
                       "completed": sum(entry["status"] == "completed" for entry in manifest["results"]),
                       "failed": sum(entry["status"] == "failed" for entry in manifest["results"])}
        print(json.dumps(summary, ensure_ascii=False, allow_nan=False))
    except (ValueError, OSError) as exc:
        print(f"research exchange rejected: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
