"""Repository output paths and conservative artifact discovery (standard library only)."""
from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext, redirect_stderr, redirect_stdout
from datetime import date, datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WEEKLY_KINDS = {"market-research", "change-decision", "adaption-report", "execution-audit"}


def iso_date(value):
    value = str(value)
    if re.fullmatch(r"\d{8}", value):
        value = datetime.strptime(value, "%Y%m%d").date().isoformat()
    return date.fromisoformat(value).isoformat()


def artifact_path(track, kind, as_of, root=ROOT):
    day = iso_date(as_of)
    base = Path(root) / "research" / track
    if track not in {"futures", "investment", "etf"}:
        raise ValueError(f"Unknown track: {track}")
    prefix = {"futures": "", "investment": "investment-", "etf": "etf-"}[track]
    if kind == "data-snapshot" and track in {"futures", "etf"}:
        return base / "snapshots" / f"{prefix}{day}-{kind}.txt"
    if kind == "drawdown" and track == "etf":
        return base / "snapshots" / f"etf-{day}-drawdown.json"
    if kind == "review" and track == "etf":
        return base / "reviews" / day / f"etf-{day}-review.md"
    if kind in WEEKLY_KINDS and track in {"futures", "investment"}:
        if track == "investment" and kind == "execution-audit":
            raise ValueError("Stock weekly reviews do not produce futures execution audits")
        return base / "weekly" / day / f"{prefix}{day}-{kind}.md"
    raise ValueError(f"Unsupported artifact: {track}/{kind}")


def company_dir(market, code, root=ROOT):
    if market not in {"SH", "SZ", "HK"} or not re.fullmatch(r"\d{5,6}", code):
        raise ValueError("Company identity requires SH/SZ/HK and a 5–6 digit code")
    return Path(root) / "research/investment/companies" / f"{market}-{code}"


def company_path(market, code, as_of, kind, root=ROOT, revision=None):
    if kind not in {"research", "price-map"}:
        raise ValueError("Unknown company artifact")
    if revision is not None and (not isinstance(revision, int) or revision < 2):
        raise ValueError("Isolated revision must be >= 2")
    day = iso_date(as_of)
    suffix = f"-r{revision}" if revision is not None else ""
    ext = "md" if kind == "research" else "json"
    return company_dir(market, code, root) / day / f"investment-{code}-{day}-{kind}{suffix}.{ext}"


def committed_paths(root):
    result = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "research"],
                            cwd=root, capture_output=True, text=True, check=True)
    return set(result.stdout.splitlines())


def discover(track, kind, as_of, root=ROOT, before=False, committed=False):
    """Exact family/date matching; no archive, revisions, future dates or partial files."""
    root = Path(root)
    cutoff = iso_date(as_of)
    prototype = artifact_path(track, kind, cutoff, root)
    dated_parent = kind in WEEKLY_KINDS or kind == "review"
    base = prototype.parent.parent if dated_parent else prototype.parent
    prefix = {"futures": "", "investment": "investment-", "etf": "etf-"}[track]
    pattern = re.compile(rf"{prefix}(\d{{4}}-\d{{2}}-\d{{2}})-{kind}{re.escape(prototype.suffix)}")
    tracked = committed_paths(root) if committed else None
    found = []
    for path in base.glob("*/*" if dated_parent else "*"):
        match = pattern.fullmatch(path.name)
        if not path.is_file() or not match:
            continue
        try:
            day = iso_date(match[1])
        except ValueError:
            continue
        if day > cutoff or (before and day == cutoff) or (dated_parent and path.parent.name != day):
            continue
        if tracked is not None:
            relative = path.relative_to(root).as_posix()
            if relative not in tracked:
                continue
            # A tracked path with uncommitted edits is not committed evidence.
            saved = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=root,
                                   capture_output=True, check=True).stdout
            if saved != path.read_bytes():
                continue
        if kind == "data-snapshot" and not snapshot_complete(path, day):
            continue
        found.append((day, path))
    return [path for _, path in sorted(found)]


def snapshot_complete(path, as_of):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    lines = text.rstrip().splitlines()
    stamp = iso_date(as_of).replace("-", "")
    pattern = rf"\bAS_OF={stamp}(?!\d)"
    return bool(lines and lines[-1].startswith("== 快照完成 |") and re.search(pattern, lines[-1])
                and re.search(pattern, lines[0]))


class _Tee:
    def __init__(self, original, sink):
        self.original, self.sink = original, sink

    def write(self, text):
        self.original.write(text)
        return self.sink.write(text)

    def flush(self):
        self.original.flush()
        self.sink.flush()


def write_json(path, payload, overwrite=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=path.name + ".", suffix=".partial", delete=False) as sink:
        json.dump(payload, sink, ensure_ascii=False, indent=2, allow_nan=False)
        sink.write("\n")
        partial = Path(sink.name)
    if overwrite:
        os.replace(partial, path)
    else:
        os.link(partial, path)
        partial.unlink()


@contextmanager
def snapshot_output(path, as_of, overwrite=False, capture_stderr=True):
    """Keep failed runs as ignored partials; publish only complete output, without clobbering."""
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists; explicit --overwrite required")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=path.name + ".", suffix=".partial", delete=False) as sink:
        partial = Path(sink.name)
        stderr = redirect_stderr(_Tee(sys.stderr, sink)) if capture_stderr else nullcontext()
        with redirect_stdout(_Tee(sys.stdout, sink)), stderr:
            yield partial
    if not snapshot_complete(partial, as_of):
        raise ValueError(f"Missing or mismatched completion marker; retained {partial}")
    if overwrite:
        os.replace(partial, path)
    else:
        # Atomic no-replace publication; a concurrent run cannot overwrite the winner.
        os.link(partial, path)
        partial.unlink()


def company_runs(market, code, as_of, root=ROOT, *, include_legacy=False):
    """Return v2 report/JSON pairs; v1 is opt-in historical input, never a current index."""
    cutoff = iso_date(as_of)
    results = []
    for path in company_dir(market, code, root).glob(f"*/investment-{code}-*-price-map.json"):
        try:
            day = iso_date(path.parent.name)
            if day > cutoff or path != company_path(market, code, day, "price-map", root):
                continue
            report = company_path(market, code, day, "research", root)
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("meta", {}), dict):
                continue
            if not report.is_file() or not report.read_text(encoding="utf-8").strip():
                continue
            if data.get("meta", {}).get("schema_version") == "stock-research/v2":
                try:
                    from .stock_price_map import validate_document
                except ImportError:
                    from stock_price_map import validate_document
                validate_document(data)
                if data["meta"]["valuation_date"] != day or data["meta"]["code"] != f"{code}.{market}":
                    continue
                if (Path(root) / data["meta"]["report_path"]).resolve() != report.resolve():
                    continue
            elif include_legacy and data.get("schema_version") == "stock-research/v1":
                if data.get("valuation_date") != day:
                    continue
            else:
                continue
            results.append((day, path))
        except (ValueError, KeyError, TypeError, UnicodeError):
            continue
    return [path for _, path in sorted(results)]


def rebuild_indexes(as_of, root=ROOT):
    """Optional local copies; no research state is stored only in these indexes."""
    root = Path(root)
    for directory in (root / "research/investment/companies").glob("*"):
        match = re.fullmatch(r"(SH|SZ|HK)-(\d{5,6})", directory.name)
        if not match:
            continue
        runs = company_runs(match[1], match[2], as_of, root)
        target = root / "output/indexes/investment" / directory.name / f"investment-{match[2]}-latest.json"
        if runs:
            write_json(target, json.loads(runs[-1].read_text()), overwrite=True)
        elif target.is_file():
            # A rebuilt current index must not keep a legacy or otherwise ineligible result.
            target.unlink()
    paths = discover("etf", "drawdown", as_of, root)
    for path in reversed(paths):
        try:
            data = json.loads(path.read_text())
            day = iso_date(data["as_of"])
        except (ValueError, KeyError, TypeError):
            continue
        snapshot = artifact_path("etf", "data-snapshot", day, root)
        if path != artifact_path("etf", "drawdown", day, root) or not snapshot.is_file():
            continue
        if data.get("snapshot") != snapshot.relative_to(root).as_posix():
            continue
        if snapshot_complete(snapshot, day):
            write_json(root / "output/indexes/etf/etf-ladder-latest.json", data, overwrite=True)
            break


def render_index(as_of, root=ROOT):
    root = Path(root)
    lines = ["# 报告索引", "", f"生成截止：{iso_date(as_of)}。仅导航，不代表证据新鲜或已通过研究验收。",
             "由 `python3 scripts/research_paths.py index --as-of YYYY-MM-DD` 重建。", ""]
    for track, label in [("futures", "期货"), ("investment", "股票框架"), ("etf", "ETF")]:
        lines += [f"## {label}", "", "| 日期 | 已保存报告 |", "|---|---|"]
        families = ["review"] if track == "etf" else sorted(WEEKLY_KINDS - ({"execution-audit"} if track == "investment" else set()))
        dates = {}
        for kind in families:
            for path in discover(track, kind, as_of, root):
                dates.setdefault(path.parent.name, []).append(f"[{kind}]({path.relative_to(root / 'research').as_posix()})")
        for day, links in sorted(dates.items(), reverse=True):
            lines.append(f"| {day} | {' · '.join(links)} |")
        lines.append("")
    lines += ["## 公司研究", ""]
    for directory in sorted((root / "research/investment/companies").glob("*")):
        match = re.fullmatch(r"(SH|SZ|HK)-(\d{5,6})", directory.name)
        if match:
            for path in reversed(company_runs(match[1], match[2], as_of, root, include_legacy=True)):
                report = company_path(match[1], match[2], path.parent.name, "research", root)
                legacy = json.loads(path.read_text()).get("schema_version") == "stock-research/v1"
                label = " · v1 历史研究" if legacy else " · v2"
                lines.append(f"- [{directory.name} · {path.parent.name}{label}]({report.relative_to(root / 'research').as_posix()})")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("path", "list"):
        p = sub.add_parser(command)
        p.add_argument("--track", required=True, choices=["futures", "investment", "etf"])
        p.add_argument("--kind", required=True)
        p.add_argument("--as-of", required=True)
        if command == "list":
            p.add_argument("--before", action="store_true")
            p.add_argument("--committed", action="store_true")
    p = sub.add_parser("latest-company")
    p.add_argument("--market", required=True)
    p.add_argument("--code", required=True)
    p.add_argument("--as-of", required=True)
    p.add_argument("--include-legacy", action="store_true",
                   help="Include v1 reports for historical research only; default selects v2")
    p = sub.add_parser("rebuild-indexes")
    p.add_argument("--as-of", required=True)
    p = sub.add_parser("index")
    p.add_argument("--as-of", required=True)
    args = parser.parse_args()
    if args.command == "path":
        print(artifact_path(args.track, args.kind, args.as_of).relative_to(ROOT))
    elif args.command == "list":
        for path in discover(args.track, args.kind, args.as_of, before=args.before, committed=args.committed):
            print(path.relative_to(ROOT))
    elif args.command == "rebuild-indexes":
        rebuild_indexes(args.as_of)
    elif args.command == "index":
        (ROOT / "research/INDEX.md").write_text(render_index(args.as_of), encoding="utf-8")
    else:
        paths = company_runs(args.market, args.code, args.as_of, include_legacy=args.include_legacy)
        if paths:
            print(paths[-1].relative_to(ROOT))
            history = company_runs(args.market, args.code, args.as_of, include_legacy=True)
            if json.loads(paths[-1].read_text()).get("schema_version") == "stock-research/v1":
                print("历史输入：v1 不代表当前 v2 价格地图，不可直接转换旧参数或价位。", file=sys.stderr)
            elif history and history[-1].parent.name > paths[-1].parent.name:
                print(f"存在更晚的 v1 历史研究（{history[-1].parent.name}）；"
                      f"返回的 v2 估值日仍为 {paths[-1].parent.name}，不代表已复评至 {args.as_of}。",
                      file=sys.stderr)
        else:
            print("未找到截止日内合格的 v2 报告/JSON 配对；旧 v1 仅可用 --include-legacy 查找历史输入。"
                  if not args.include_legacy else "未找到截止日内完整的研究配对。", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
