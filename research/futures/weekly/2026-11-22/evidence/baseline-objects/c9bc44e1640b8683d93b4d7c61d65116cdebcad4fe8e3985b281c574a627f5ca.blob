"""Share immutable local futures research across worktrees, without Git publication.

publish freezes explicitly adopted reports and their local evidence. collect merges
opportunities by their original ID and clock, never carrying ready/account approval.
The store is persistent local research, not disposable output/cache.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

try:
    from . import futures_handoff as handoff
    from .futures_strategy import _contract, REVERSION_PRODUCTS
except ImportError:
    import futures_handoff as handoff
    from futures_strategy import _contract, REVERSION_PRODUCTS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "futures-local-continuity/v1"


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return handoff.read_json(Path(path).read_bytes())


def default_store(root):
    result = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root,
                            capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError("Shared store requires a Git checkout or explicit --store")
    common = Path(result.stdout.strip())
    common = (Path(root) / common).resolve() if not common.is_absolute() else common.resolve()
    if common.name != ".git":
        raise ValueError("Nonstandard Git common directory; specify the shared --store explicitly")
    return common.parent / "research/futures/local-continuity"


def store_file(store, relative):
    return handoff.safe_path(store, relative)


@contextmanager
def locked(store):
    store.mkdir(parents=True, exist_ok=True)
    with (store / ".lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def atomic(path, data, *, replace=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".partial", delete=False) as f:
        temp = Path(f.name)
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    try:
        if replace:
            os.replace(temp, path)
        else:
            try:
                os.link(temp, path)
            except FileExistsError:
                if path.read_bytes() != data:
                    raise ValueError(f"Immutable object conflict: {path}")
    finally:
        temp.unlink(missing_ok=True)


def index_read(store):
    path = store / "index.json"
    if not path.exists():
        return {"schema": SCHEMA, "entries": []}
    data = read_json(path)
    if not isinstance(data, dict) or set(data) != {"schema", "entries"} or data["schema"] != SCHEMA:
        raise ValueError("Invalid continuity index")
    if not isinstance(data["entries"], list) or any(not isinstance(x, str) or not re.fullmatch(r"[0-9a-f]{64}", x) for x in data["entries"]):
        raise ValueError("Invalid continuity entry hash")
    if len(set(data["entries"])) != len(data["entries"]):
        raise ValueError("Duplicate continuity entry IDs")
    return data


def timestamp(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("Continuity timestamps require timezone")
    return parsed.astimezone(handoff.CHINA)


def audit_json(content):
    blocks = re.findall(r"^```json\s*\n(.*?)^```\s*$", content.decode(), re.M | re.S)
    if len(blocks) != 1:
        raise ValueError("Adopted audit requires exactly one JSON block")
    result = handoff.read_json(blocks[0])
    if not isinstance(result, dict) or result.get("audit_schema_version") != 3:
        raise ValueError("Shared audit requires schema 3")
    return result


def capture_files(root, initial):
    """Freeze referenced research evidence, including exact hashes from handoff.

    Local report/JSON references are followed; external URLs are retained as text.
    Source scripts/canonical are added explicitly for provenance, not executed.
    """
    found = {}
    queue = list(initial)
    while queue:
        relative, expected = queue.pop()
        if relative in found:
            if expected and digest(found[relative]) != expected:
                raise ValueError(f"Source hash mismatch: {relative}")
            continue
        path = handoff.safe_path(root, relative)
        raw = path.read_bytes()
        if expected and digest(raw) != expected:
            raise ValueError(f"Source hash mismatch: {relative}")
        found[relative] = raw
        # Canonical and source files are provenance snapshots, not research
        # dependencies. Raw text snapshots may print their old cache location;
        # their bytes are frozen data, not an additional dependency manifest.
        if (not relative.startswith(("research/futures/", "output/")) or
                path.suffix not in {".md", ".json"} or "framework" in path.name):
            continue
        text = raw.decode("utf-8")
        # Follow frozen path/hash references even when they carry role/size
        # metadata. Original cache locations are provenance, not dependencies.
        def refs(value):
            if isinstance(value, dict):
                if "source_inputs" in value:
                    inputs = value["source_inputs"]
                    if not isinstance(inputs, list) or any(not isinstance(row, dict) or
                            "path" not in row or "sha256" not in row for row in inputs):
                        raise ValueError("Frozen source_inputs require explicit path and sha256")
                if "path" in value and "sha256" in value and "canonical_full_sha256" not in value:
                    handoff._sha(value["sha256"])
                    queue.append((value["path"], value["sha256"]))
                for key, child in value.items():
                    if key not in {"original_path", "input_selection"}:
                        refs(child)
            elif isinstance(value, list):
                for child in value:
                    refs(child)
        def strings(value):
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for key, child in value.items():
                    if key not in {"original_path", "input_selection"}:
                        yield from strings(child)
            elif isinstance(value, list):
                for child in value:
                    yield from strings(child)
        scan = []
        if path.suffix == ".json":
            parsed = handoff.read_json(text)
            refs(parsed)
            scan.extend(strings(parsed))
        else:
            json_blocks = re.compile(r"^```json\s*\n(.*?)^```\s*$", re.M | re.S)
            for block in json_blocks.findall(text):
                parsed = handoff.read_json(block)
                refs(parsed)
                scan.extend(strings(parsed))
            prose = json_blocks.sub("", text)
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}-signal-refresh(?:-r\d+)?", path.stem):
                # The renderer's input_selection line names the original raw
                # cache. Its paired JSON declares the durable source_inputs.
                prose = "\n".join(line for line in prose.splitlines() if "input_selection" not in line)
            scan.append(prose)
        reference_text = "\n".join(scan)
        for match in re.findall(r"(?:research/futures/|output/)[A-Za-z0-9_./+-]+\.(?:json|md|txt|csv)", reference_text):
            candidate = handoff.safe_path(root, match)
            if candidate.is_file():
                queue.append((match, None))
            else:
                raise ValueError(f"Referenced local evidence is missing: {match}")
        for link in re.findall(r"\]\(([^)]+)\)", reference_text):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                continue
            link = link.split("#")[0].strip("<>")
            resolved = (path.parent / link).resolve()
            if not resolved.is_relative_to(Path(root).resolve()):
                raise ValueError("Evidence link escapes source checkout")
            rel = resolved.relative_to(Path(root).resolve()).as_posix()
            if rel.startswith(("research/futures/", "output/")) and resolved.suffix in {".md", ".json", ".txt", ".csv"}:
                if not resolved.is_file():
                    raise ValueError(f"Referenced local evidence is missing: {rel}")
                queue.append((rel, None))
    return found


def validate_anchors(package, now):
    if not isinstance(package, dict) or not isinstance(package.get("anchors"), list):
        raise ValueError("Frozen anchors require anchors[]")
    for rows, time_key in [(package["anchors"], "frozen_at"), (package.get("withdrawals", []), "invalidated_at")]:
        if not isinstance(rows, list):
            raise ValueError("Anchor and withdrawal rows must be lists")
        for row in rows:
            if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip() for k in ("near_contract", "far_contract", time_key)):
                raise ValueError("Anchor identity/time missing")
            near_product, near_month = _contract(row["near_contract"], REVERSION_PRODUCTS)
            far_product, far_month = _contract(row["far_contract"], REVERSION_PRODUCTS)
            if near_product != far_product or near_month >= far_month or timestamp(row[time_key]) > now:
                raise ValueError("Invalid pair or future anchor event")
            if time_key == "invalidated_at":
                if not isinstance(row.get("reason"), str) or not row["reason"].strip() or not isinstance(row.get("source_refs"), list) or not row["source_refs"] or any(not isinstance(x, str) or not x.strip() for x in row["source_refs"]):
                    raise ValueError("Anchor withdrawal requires reason and source_refs")
    if not isinstance(package.get("signal_observations", []), list):
        raise ValueError("signal_observations must be a list")
    for row in package.get("signal_observations", []):
        if not isinstance(row, dict):
            raise ValueError("Invalid signal observation")
        for key in ("near_contract", "far_contract", "signal_date", "signal_completed_at"):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError("Signal observation identity/time missing")
        if timestamp(row["signal_completed_at"]) > now:
            raise ValueError("Future signal observation")


def publish(root, store, *, manifest=None, anchors=None, evidence=(), producer="manual", allow_historical=False):
    root, store = Path(root).resolve(), Path(store).resolve()
    if producer not in {"daily", "weekly", "manual"}:
        raise ValueError("Unknown continuity producer")
    if not manifest and not anchors:
        raise ValueError("Explicit adopted handoff or frozen anchors required")
    now = datetime.now(handoff.CHINA)
    adopted = handoff.check(root, manifest, allow_historical=allow_historical) if manifest else None
    method = handoff.method_fingerprint(root)
    files = [(x, None) for x in evidence]
    if adopted:
        files.append((manifest, adopted["manifest_sha256"]))
        document = adopted["handoff"]
        # Historical imports keep their original method identity. They can
        # never acquire current-rule compatibility merely by being copied.
        method = document["method"]
        as_of = document["as_of_date"]
        effective_at = document["registered_at"]
        for ref in document["artifacts"].values():
            if ref:
                files.append((ref["path"], ref["sha256"]))
    else:
        document = None
        as_of, effective_at = now.date().isoformat(), now.isoformat()
    if anchors:
        raw = handoff.safe_path(root, anchors).read_bytes()
        package = handoff.read_json(raw)
        validate_anchors(package, now)
        if not adopted:
            times = [timestamp(x["frozen_at"]) for x in package["anchors"]]
            times += [timestamp(x["invalidated_at"]) for x in package.get("withdrawals", [])]
            times += [timestamp(x["signal_completed_at"]) for x in package.get("signal_observations", [])]
            if not times:
                raise ValueError("Anchor-only publication needs a dated anchor event")
            effective_at = max(times).isoformat()
            as_of = max(times).date().isoformat()
        files.append((anchors, digest(raw)))
    for rel in [handoff.CANONICAL, "scripts/futures_strategy.py", "scripts/futures_risk.py", "scripts/future_data.py"]:
        if (root / rel).is_file():
            files.append((rel, None))
    captured = capture_files(root, files)
    refs = {rel: {"sha256": digest(data), "object": f"objects/{digest(data)}", "bytes": len(data)}
            for rel, data in captured.items()}
    identity = dict(schema=SCHEMA, as_of_date=as_of, effective_at=effective_at,
                    method=method, handoff=manifest, anchors=anchors, files=refs)
    # Capture time and originating checkout do not create duplicate adoption events.
    entry_id = digest(encoded(identity))
    entry = dict(identity, entry_id=entry_id, captured_at=now.isoformat(),
                 source_root=str(root), producer=producer)
    with locked(store):
        index = index_read(store)
        for relative, data in captured.items():
            if handoff.safe_path(root, relative).read_bytes() != data:
                raise ValueError(f"Source changed during capture: {relative}")
            atomic(store_file(store, refs[relative]["object"]), data)
        entry_path = store_file(store, f"entries/{entry_id}.json")
        if not entry_path.exists():
            atomic(entry_path, encoded(entry))
        else:
            load_entry(store, entry_id)
        if entry_id not in index["entries"]:
            index["entries"].append(entry_id)
            atomic(store / "index.json", encoded(index), replace=True)
    return dict(status="stored", store=str(store), entry_id=entry_id,
                scope="local", publication_verified=False, execution_reuse=False)


def load_entry(store, entry_id):
    entry = read_json(store_file(store, f"entries/{entry_id}.json"))
    keys = {"schema", "as_of_date", "effective_at", "method", "handoff", "anchors", "files"}
    identity = {key: entry[key] for key in keys}
    if entry.get("schema") != SCHEMA or entry.get("entry_id") != entry_id or digest(encoded(identity)) != entry_id:
        raise ValueError("Continuity entry integrity failure")
    timestamp(entry["effective_at"])
    handoff._day(entry["as_of_date"])
    if not isinstance(entry["files"], dict):
        raise ValueError("Invalid continuity files")
    blobs = {}
    for relative, ref in entry["files"].items():
        if ref["object"] != f"objects/{ref['sha256']}" or not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]):
            raise ValueError("Invalid continuity object identity")
        data = store_file(store, ref["object"]).read_bytes()
        if digest(data) != ref["sha256"] or len(data) != ref["bytes"]:
            raise ValueError(f"Continuity object hash mismatch: {relative}")
        # Check materialization safety even before a consumer requests export.
        handoff.safe_path(store / "unused", relative)
        blobs[relative] = data
    return entry, blobs


def collect(root, store, as_of, out_dir):
    root, store, out_dir = Path(root).resolve(), Path(store).resolve(), Path(out_dir).resolve()
    day = handoff._day(as_of)
    if day > datetime.now(handoff.CHINA).date().isoformat():
        raise ValueError("Future continuity date")
    if not out_dir.is_relative_to(root) or out_dir == root:
        raise ValueError("Materialize inside the consuming checkout")
    if out_dir.exists():
        raise ValueError("Use a fresh output directory; old continuity exports are immutable")
    current = handoff.method_fingerprint(root)
    with locked(store):
        entries = [load_entry(store, x) for x in index_read(store)["entries"]]
    entries = [(entry, files) for entry, files in entries if entry["as_of_date"] <= day]
    entries.sort(key=lambda pair: (pair[0]["as_of_date"], timestamp(pair[0]["effective_at"]), pair[0]["entry_id"]))
    candidates, corrections, anchor_rows, observations, withdrawals = {}, [], {}, {}, {}
    conflicts, reassessment, consumed, review_scope = [], [], [], []
    dispositions = {}
    identity_ids = {}
    (root / "output").mkdir(exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="continuity-", suffix=".partial", dir=root / "output"))
    try:
        for entry, blobs in entries:
            compatible = (entry["method"]["version"] == current["version"]
                          and entry["method"]["sha256"] == current["sha256"])
            source = dict(entry_id=entry["entry_id"], producer=entry["producer"],
                          as_of_date=entry["as_of_date"], method_compatible=compatible,
                          source_root=entry["source_root"], scope="local", execution_reuse=False)
            source["materialized_root"] = f"sources/{entry['entry_id']}"
            consumed.append(source)
            for rel, raw in blobs.items():
                target = handoff.safe_path(staging / "sources" / entry["entry_id"], rel)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            document = handoff.read_json(blobs[entry["handoff"]]) if entry["handoff"] else None
            if document:
                if document["corrections"]["scope"]:
                    corrections.append(dict(source=source, corrections=document["corrections"]))
                audit_ref = document["artifacts"]["execution_audit"]
                if audit_ref:
                    audit = audit_json(blobs[audit_ref["path"]])
                    review_scope.append(dict(source=source, audit=audit_ref["path"],
                                             candidates=audit.get("candidates", []),
                                             account_history=audit.get("account", audit.get("account_snapshot", audit.get("snapshot", {}).get("account"))),
                                             current_account_verified=False))
                    if audit.get("evidence_corrections"):
                        corrections.append(dict(source=source, evidence_corrections=audit["evidence_corrections"]))
                    for original in audit.get("candidates", []):
                        plan = original.get("plan") or {}
                        key = original.get("opportunity_id")
                        if not key:
                            if plan.get("signal_date"):
                                conflicts.append(dict(reason="original_opportunity_id_missing", source=source))
                            continue
                        if not compatible:
                            reassessment.append(dict(opportunity_id=key, source=source, original=original))
                            continue
                        evaluated_at = timestamp(original.get("evaluated_at") or plan.get("evaluated_at") or
                                                 audit.get("evaluated_at") or entry["effective_at"])
                        if evaluated_at > datetime.now(handoff.CHINA) or evaluated_at.date().isoformat() > day:
                            conflicts.append(dict(reason="future_evaluation", opportunity_id=key, source=source))
                            candidates.pop(key, None)
                            continue
                        if not plan.get("signal_date"):
                            previous_disposition = dispositions.get(key)
                            if previous_disposition is None or evaluated_at >= previous_disposition["evaluated_at"]:
                                dispositions[key] = dict(evaluated_at=evaluated_at, source=source, original=original)
                            continue
                        identity = (original.get("strategy"), tuple(original.get("contracts", [])),
                                    original.get("direction"), plan["signal_date"])
                        previous_id = identity_ids.setdefault(identity, key)
                        if previous_id != key:
                            conflicts.append(dict(reason="same_opportunity_different_ids", opportunity_ids=[previous_id, key]))
                            candidates.pop(previous_id, None)
                            continue
                        clock = (plan["signal_date"], plan.get("valid_until"),
                                 plan.get("registered_at", original.get("registered_at")))
                        previous = candidates.get(key)
                        if previous and (previous["original_clock"] != clock or previous["identity"] != identity):
                            conflicts.append(dict(reason="original_clock_or_identity_changed", opportunity_id=key,
                                                  sources=[previous["source"], source]))
                            candidates.pop(key)
                            continue
                        if previous and evaluated_at < previous["evaluated_at"]:
                            continue
                        if previous and evaluated_at == previous["evaluated_at"] and plan != previous["candidate"].get("plan"):
                            conflicts.append(dict(reason="same_evaluation_different_plans", opportunity_id=key,
                                                  sources=[previous["source"], source]))
                            candidates.pop(key)
                            continue
                        copied = json.loads(json.dumps(original))
                        for field in ("risk_evaluation", "account", "account_snapshot", "evaluated_checks"):
                            copied.pop(field, None)
                        copied.update(source_status=copied.get("status"), status="incomplete", final_lots=None,
                                      execution_permission="not_evaluated", continuity_source=source)
                        candidates[key] = dict(candidate=copied, original_clock=clock, identity=identity, source=source,
                                               evaluated_at=evaluated_at)
            if entry["anchors"]:
                package = handoff.read_json(blobs[entry["anchors"]])
                validate_anchors(package, datetime.now(handoff.CHINA))
                for anchor in package["anchors"] if compatible else []:
                    if timestamp(anchor["frozen_at"]).date().isoformat() > day:
                        continue
                    pair = (anchor.get("near_contract"), anchor.get("far_contract"))
                    before = anchor_rows.get(pair)
                    if before is None or timestamp(anchor["frozen_at"]) > timestamp(before["frozen_at"]):
                        anchor_rows[pair] = anchor
                    elif timestamp(anchor["frozen_at"]) == timestamp(before["frozen_at"]) and anchor != before:
                        conflicts.append(dict(reason="same_frozen_anchor_changed", pair=pair))
                        anchor_rows.pop(pair, None)
                for observation in package.get("signal_observations", []) if compatible else []:
                    if timestamp(observation["signal_completed_at"]).date().isoformat() > day:
                        continue
                    key = (observation.get("near_contract"), observation.get("far_contract"), observation.get("signal_date"))
                    if key in observations and observations[key] != observation:
                        conflicts.append(dict(reason="signal_time_evidence_conflict", pair_date=key))
                        observations.pop(key)
                    else:
                        observations[key] = observation
                for row in package.get("withdrawals", []):
                    if timestamp(row["invalidated_at"]).date().isoformat() > day:
                        continue
                    pair = (row["near_contract"], row["far_contract"])
                    if pair not in withdrawals or timestamp(row["invalidated_at"]) >= timestamp(withdrawals[pair]["invalidated_at"]):
                        withdrawals[pair] = dict(row, continuity_source=source)
        bad_ids = {x.get("opportunity_id") for x in conflicts}
        bad_ids.update(x for item in conflicts for x in item.get("opportunity_ids", []))
        plan_reassessment = []
        for key, disposition in dispositions.items():
            previous = candidates.get(key)
            if previous and disposition["evaluated_at"] >= previous["evaluated_at"]:
                bad_ids.add(key)
                plan_reassessment.append(dict(opportunity_id=key, reason="latest_observation_has_no_plan",
                    evaluated_at=disposition["evaluated_at"].isoformat(), source=disposition["source"],
                    latest_observation=disposition["original"],
                    original_plan=previous["candidate"]["plan"], original_plan_source=previous["source"],
                    execution_permission="not_evaluated"))
        plans = dict(schema=SCHEMA, as_of_date=day, scope="candidate_continuity_only",
                     candidates=[v["candidate"] for k, v in sorted(candidates.items()) if k not in bad_ids],
                     execution_permission="not_evaluated", final_lots=None)
        bad_pairs = {tuple(x["pair"]) for x in conflicts if "pair" in x}
        bad_observations = {tuple(x["pair_date"]) for x in conflicts if "pair_date" in x}
        anchors_out = dict(anchors=[v for k, v in anchor_rows.items() if k not in bad_pairs and
                                   (k not in withdrawals or timestamp(v["frozen_at"]) > timestamp(withdrawals[k]["invalidated_at"]))],
                           signal_observations=[v for k, v in observations.items() if k not in bad_observations],
                           withdrawals=list(withdrawals.values()))
        result = dict(schema=SCHEMA, as_of_date=day,
                      status="needs_reconciliation" if conflicts else "needs_reassessment" if plan_reassessment else "collected",
                      store=str(store), scope="local", execution_reuse=False, publication_verified=False,
                      requires_fresh_evaluation=True, consumed=consumed, corrections=corrections,
                      review_scope=review_scope,
                      conflicts=conflicts, requires_method_reassessment=reassessment,
                      requires_plan_reassessment=plan_reassessment,
                      plans="plans.json", anchors="anchors.json", original_sources="sources/")
        for name, value in [("plans.json", plans), ("anchors.json", anchors_out), ("continuity.json", result)]:
            (staging / name).write_bytes(encoded(value))
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        # Serialize final exports through the shared lock; never replace even
        # an empty directory created by another collect call.
        with locked(store):
            if out_dir.exists():
                raise ValueError("Continuity output appeared during collection")
            os.rename(staging, out_dir)
    except Exception:
        # Keep failed staging isolated for diagnosis; never replace a formal export.
        raise
    return dict(status=result["status"], output=str(out_dir), candidates=len(plans["candidates"]),
                corrections=len(corrections), execution_reuse=False, scope="local")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--store", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    put = commands.add_parser("publish")
    put.add_argument("--handoff")
    put.add_argument("--anchors")
    put.add_argument("--evidence", action="append", default=[])
    put.add_argument("--producer", choices=["daily", "weekly", "manual"], default="manual")
    put.add_argument("--allow-historical", action="store_true", help="Import incompatible facts/IDs/corrections for reassessment only")
    get = commands.add_parser("collect")
    get.add_argument("--as-of", required=True)
    get.add_argument("--out-dir", type=Path, required=True)
    where = commands.add_parser("location")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        store = args.store.resolve() if args.store else default_store(root)
        if args.command == "location":
            result = dict(store=str(store), persistent=True, scope="local")
        elif args.command == "publish":
            result = publish(root, store, manifest=args.handoff, anchors=args.anchors,
                             evidence=args.evidence, producer=args.producer, allow_historical=args.allow_historical)
        else:
            (root / "output").mkdir(exist_ok=True)
            output = args.out_dir if args.out_dir.is_absolute() else root / args.out_dir
            result = collect(root, store, args.as_of, output)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, UnicodeError) as error:
        print(json.dumps(dict(status="error", error=str(error), execution_reuse=False), ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
