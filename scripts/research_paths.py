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
GENERATORS = ("codex", "claude")


def generator_suffix(generator):
    if generator is not None and generator not in GENERATORS:
        raise ValueError("Generator must be codex or claude; None is unattributed history")
    return f"-{generator}" if generator else ""


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


def company_dir(market, code, as_of, root=ROOT):
    if market not in {"SH", "SZ", "HK"} or not re.fullmatch(r"\d{5,6}", code):
        raise ValueError("Company identity requires SH/SZ/HK and a 5–6 digit code")
    return Path(root) / "research/investment/companies" / iso_date(as_of) / f"{market}-{code}"


def company_path(market, code, as_of, kind, root=ROOT, revision=None, *, generator=None):
    if kind not in {"research", "price-map"}:
        raise ValueError("Unknown company artifact")
    if revision is not None and (not isinstance(revision, int) or revision < 2):
        raise ValueError("Isolated revision must be >= 2")
    day = iso_date(as_of)
    suffix = generator_suffix(generator) + (f"-r{revision}" if revision is not None else "")
    ext = "md" if kind == "research" else "json"
    return company_dir(market, code, day, root) / f"investment-{code}-{day}-{kind}{suffix}.{ext}"


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


def company_runs(market, code, as_of, root=ROOT, *, include_legacy=False, generator=None):
    """Return one generator's formal pairs; None selects unattributed history only."""
    cutoff = iso_date(as_of)
    results = []
    identity = company_dir(market, code, cutoff, root).name
    base = Path(root) / "research/investment/companies"
    suffix = generator_suffix(generator)
    for path in base.glob(f"*/{identity}/investment-{code}-*-price-map{suffix}.json"):
        try:
            day = iso_date(path.parent.parent.name)
            if day > cutoff or path != company_path(market, code, day, "price-map", root, generator=generator):
                continue
            report = company_path(market, code, day, "research", root, generator=generator)
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
                if data["meta"].get("generator") != generator:
                    continue
                if data["meta"]["valuation_date"] != day or data["meta"]["code"] != f"{code}.{market}":
                    continue
                if (Path(root) / data["meta"]["report_path"]).resolve() != report.resolve():
                    continue
            elif generator is None and include_legacy and data.get("schema_version") == "stock-research/v1":
                if data.get("valuation_date") != day:
                    continue
            else:
                continue
            results.append((day, path))
        except (ValueError, KeyError, TypeError, UnicodeError):
            continue
    return [path for _, path in sorted(results)]


def company_identities(root=ROOT):
    """Unique market/code identities across date directories, excluding other layouts."""
    identities = set()
    for directory in (Path(root) / "research/investment/companies").glob("*/*"):
        match = re.fullmatch(r"(SH|SZ|HK)-(\d{5,6})", directory.name)
        if not directory.is_dir() or not match:
            continue
        try:
            if directory == company_dir(match[1], match[2], directory.parent.name, root):
                identities.add((match[1], match[2]))
        except ValueError:
            continue
    return sorted(identities)


def rebuild_indexes(as_of, root=ROOT):
    """Optional local copies; no research state is stored only in these indexes."""
    root = Path(root)
    for market, code in company_identities(root):
        for generator in (None, *GENERATORS):
            runs = company_runs(market, code, as_of, root, generator=generator)
            suffix = generator_suffix(generator)
            target = root / "output/indexes/investment" / f"{market}-{code}" / f"investment-{code}-latest{suffix}.json"
            if runs:
                target.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=target.parent, suffix=".partial", delete=False) as sink:
                    sink.write(runs[-1].read_bytes())
                    partial = Path(sink.name)
                os.replace(partial, target)
            elif target.is_file():
                # Never substitute another generator or legacy schema for a missing pair.
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


def render_index(as_of, root=ROOT, *, local=False):
    root = Path(root)
    index_dir = root / ('output/indexes' if local else 'research')
    def link(path):
        return Path(os.path.relpath(path, index_dir)).as_posix()
    command = 'python3 scripts/research_paths.py index --as-of YYYY-MM-DD' + (' --local' if local else '')
    lines = ["# 报告索引", "", f"生成截止：{iso_date(as_of)}。仅导航，不代表证据新鲜或已通过研究验收。",
             f"由 `{command}` 重建。", ""]
    for track, label in [("futures", "期货"), ("investment", "股票框架"), ("etf", "ETF")]:
        lines += [f"## {label}", "", "| 日期 | 已保存报告 |", "|---|---|"]
        families = ["review"] if track == "etf" else sorted(WEEKLY_KINDS - ({"execution-audit"} if track == "investment" else set()))
        dates = {}
        for kind in families:
            for path in discover(track, kind, as_of, root):
                dates.setdefault(path.parent.name, []).append(f"[{kind}]({link(path)})")
        for day, links in sorted(dates.items(), reverse=True):
            lines.append(f"| {day} | {' · '.join(links)} |")
        lines.append("")
    lines += ["## 公司研究", ""]
    if not local:
        lines += ["公司报告按仓库约定仅本地保存，共享索引不链接未入库文件。",
                  "运行 `python3 scripts/research_paths.py index --as-of YYYY-MM-DD --local`，",
                  "在 `output/indexes/INDEX.md` 查看本机公司报告及价格地图；新克隆没有这些本地产物，`latest-company` 无结果属正常。"]
        return "\n".join(lines).rstrip() + "\n"
    dates = {}
    identities_by_day = {}
    for market, code in company_identities(root):
        runs = [path for generator in (None, *GENERATORS)
                for path in company_runs(market, code, as_of, root, include_legacy=True, generator=generator)]
        for path in sorted(runs):
            day = path.parent.parent.name
            data = json.loads(path.read_text())
            generator = data.get("meta", {}).get("generator")
            report = company_path(market, code, day, "research", root, generator=generator)
            legacy = data.get("schema_version") == "stock-research/v1"
            name = data.get("meta", {}).get("name") or f"{market}-{code}"
            name = re.sub(r"[\[\]\r\n]", " ", str(name))
            label = ("v1 历史研究" if legacy else "v2") + f" · {generator or '来源未标注'}"
            identities_by_day.setdefault(day, set()).add((market, code))
            dates.setdefault(day, []).append(
                f"- [{name}（{market}-{code}）]({link(report)})"
                f" · {label} · [价格地图]({link(path)})")
    for day, entries in sorted(dates.items(), reverse=True):
        lines += [f"### {day}（{len(identities_by_day[day])} 家公司）", "", *entries, ""]
    return "\n".join(lines).rstrip() + "\n"


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
    p.add_argument("--generator", choices=[*GENERATORS, "unattributed"], default="unattributed",
                   help="Select only this producer; default is old unattributed files, never mixed")
    p.add_argument("--include-legacy", action="store_true",
                   help="Include v1 reports for historical research only; default selects v2")
    p = sub.add_parser("company-path")
    p.add_argument("--market", required=True)
    p.add_argument("--code", required=True)
    p.add_argument("--as-of", required=True)
    p.add_argument("--kind", required=True, choices=["research", "price-map"])
    p.add_argument("--generator", required=True, choices=GENERATORS)
    p.add_argument("--revision", type=int)
    p = sub.add_parser("rebuild-indexes")
    p.add_argument("--as-of", required=True)
    p = sub.add_parser("index")
    p.add_argument("--as-of", required=True)
    p.add_argument("--local", action="store_true",
                   help="Include local company reports and write output/indexes/INDEX.md instead of the shared index")
    args = parser.parse_args()
    if args.command == "path":
        print(artifact_path(args.track, args.kind, args.as_of).relative_to(ROOT))
    elif args.command == "company-path":
        print(company_path(args.market, args.code, args.as_of, args.kind,
                           revision=args.revision, generator=args.generator).relative_to(ROOT))
    elif args.command == "list":
        for path in discover(args.track, args.kind, args.as_of, before=args.before, committed=args.committed):
            print(path.relative_to(ROOT))
    elif args.command == "rebuild-indexes":
        rebuild_indexes(args.as_of)
    elif args.command == "index":
        target = ROOT / ("output/indexes/INDEX.md" if args.local else "research/INDEX.md")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_index(args.as_of, ROOT, local=args.local), encoding="utf-8")
    else:
        generator = None if args.generator == "unattributed" else args.generator
        paths = company_runs(args.market, args.code, args.as_of, include_legacy=args.include_legacy, generator=generator)
        if paths:
            print(paths[-1].relative_to(ROOT))
            history = company_runs(args.market, args.code, args.as_of, include_legacy=True, generator=generator)
            if json.loads(paths[-1].read_text()).get("schema_version") == "stock-research/v1":
                print("历史输入：v1 不代表当前 v2 价格地图，不可直接转换旧参数或价位。", file=sys.stderr)
            elif history and history[-1].parent.parent.name > paths[-1].parent.parent.name:
                print(f"存在更晚的 v1 历史研究（{history[-1].parent.parent.name}）；"
                      f"返回的 v2 估值日仍为 {paths[-1].parent.parent.name}，不代表已复评至 {args.as_of}。",
                      file=sys.stderr)
        else:
            print("未找到截止日内合格的 v2 报告/JSON 配对；旧 v1 仅可用 --include-legacy 查找历史输入。"
                  if not args.include_legacy else "未找到截止日内完整的研究配对。", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
