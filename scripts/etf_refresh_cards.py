"""Mechanical monthly refresh of decision-card anchors (framework A1: 点位每月随快照机械刷新，不改论点).

Reads research/etf-ladder-latest.json (the machine-readable copy of snapshot §6b) and, for every current
card that carries anchors, recomputes the three levels from the new 36-month high and the new state
quantiles. A card whose inputs changed gets a new version file <card_id>-<as_of>.md that supersedes the
old one. What moves: the anchors, `decision.anchors.snapshot_ref` (now the new snapshot), valid_until, the
auto monitors pinned to an anchor level, the anchor rationales (regenerated, so no stale "current level"
claim survives) and the auto monitors' current_text (cleared). What stays: the card's own `snapshot_ref`
(the thesis data), the thesis, the manual monitors, the exit conditions. The prose only has the old anchor
numbers swapped for the new ones plus a note under the title. A thesis review is the etf-card-research
skill's job, not this script's.

CLI: python3 scripts/etf_refresh_cards.py [--as-of YYYY-MM-DD] [--dry-run]
"""

import argparse
import calendar
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    from . import validate_etf_card as validator
    from .etf_calc import level_at_drawdown_state
except ImportError:  # direct script invocation
    import validate_etf_card as validator
    from etf_calc import level_at_drawdown_state

ROOT = Path(__file__).resolve().parents[1]
LADDER = ROOT / "research" / "etf-ladder-latest.json"
ANCHORS = (("add_below", "P10", "自身历史 P10：相当于深熊底部区域"), ("buy_below", "P25", "自身历史 P25"),
           ("reduce_above", "P75", "自身历史 P75：距 36 月高点约 2%–10%"))
JSON_BLOCK = re.compile(r"(?ms)^```json[ \t]*\n(.*?)^```[ \t]*$")


def end_of_next_month(day):
    year, month = (day.year + 1, 1) if day.month == 12 else (day.year, day.month + 1)
    return date(year, month, calendar.monthrange(year, month)[1])


def _prose_forms(value):
    """Both spellings a level may take in prose: 2,297.84 and 2297.84."""
    return {f"{value:,.2f}", f"{value:.2f}"}


def refresh_card(text, ladder, as_of):
    """Return (new_text, changes) for one card, or (None, reason) when nothing is to be refreshed.

    text: the card file's full text; ladder: {index_code: sidecar row + "snapshot_ref"}; as_of: refresh date (ISO).
    """
    document = validator.load_card(text)
    anchors = document["decision"]["anchors"]
    if document["status"] == "closed":
        return None, "closed"
    if anchors["add_below"]["level"]["value"] is None:
        return None, "no anchors"
    if document["as_of_date"] == as_of:
        return None, f"a version dated {as_of} already exists; refresh on another day"
    row = ladder.get(anchors["index_code"])
    if row is None:
        return None, f"{anchors['index_code']} not in ladder sidecar"
    old_levels = {name: anchors[name]["level"]["value"] for name, _, _ in ANCHORS}
    new_inputs = {name: (row["rolling_high"], row["states"][quantile]) for name, quantile, _ in ANCHORS}
    if all((anchors[name]["inputs"]["rolling_high"]["value"], anchors[name]["inputs"]["state"]["value"]) == new_inputs[name]
           for name, _, _ in ANCHORS):
        return None, "inputs unchanged"
    new_levels = {name: round(level_at_drawdown_state(high, state), 2) for name, (high, state) in new_inputs.items()}

    # pin each monitor to an anchor by name first, against the OLD levels, then move it: no chained rewrites
    pinned = {}
    for index, monitor in enumerate(document["monitor_variables"]):
        threshold = monitor["threshold"]
        if threshold["source"] == "calc:level_at_drawdown_state" and threshold["value"] is not None:
            match = [name for name, _, _ in ANCHORS if threshold["value"] == old_levels[name]]
            pinned[index] = match[0] if match else None
    stale_monitors = [document["monitor_variables"][index]["name"] for index, name in pinned.items() if name is None]

    for name, quantile, meaning in ANCHORS:
        high, state = new_inputs[name]
        anchor = anchors[name]
        anchor["level"]["value"] = new_levels[name]
        anchor["inputs"]["rolling_high"]["value"] = high
        anchor["inputs"]["state"]["value"] = state
        anchor["rationale"] = f"回撤状态回到{meaning}对应的点位（机械刷新 @{as_of}，据快照 §6b；写卡时的文字见上一版）"
    anchors["snapshot_ref"] = row["snapshot_ref"]
    anchors["valid_until"] = end_of_next_month(date.fromisoformat(as_of)).isoformat()
    for index, monitor in enumerate(document["monitor_variables"]):
        if pinned.get(index):
            monitor["threshold"]["value"] = new_levels[pinned[index]]
        if monitor["kind"] == "auto":
            monitor["current_text"] = None   # last month's reading; the execution side recomputes daily
    old_file = f"research/etf-cards/{document['card_id']}-{document['as_of_date']}.md"
    document.update(as_of_date=as_of, supersedes=old_file)

    block = JSON_BLOCK.search(text)
    prose = text[:block.start()]
    for name, _, _ in ANCHORS:
        for form in _prose_forms(old_levels[name]):
            prose = prose.replace(form, f"{new_levels[name]:,.2f}")
    note = (f"> **点位机械刷新 @{as_of}**（锚点据快照 {row['snapshot_ref']}，36 月高点 {row['rolling_high']:,.2f}；"
            f"论点数据仍取自 {document['snapshot_ref']}）："
            + "、".join(f"{name} {old_levels[name]:,.2f}→{new_levels[name]:,.2f}" for name, _, _ in ANCHORS)
            + "。论点、监控与失效条件未复核，上一版见 supersedes。\n")
    title_end = prose.index("\n") + 1
    prose = prose[:title_end] + "\n" + note + prose[title_end:]
    new_text = prose + "```json\n" + json.dumps(document, ensure_ascii=False, indent=2) + "\n```\n" + text[block.end():]
    changes = dict(card_id=document["card_id"], index_code=anchors["index_code"], old=old_levels, new=new_levels,
                   valid_until=anchors["valid_until"], file=f"research/etf-cards/{document['card_id']}-{as_of}.md",
                   stale_monitors=stale_monitors)
    return new_text, changes


def main(argv=None):
    parser = argparse.ArgumentParser(description="按最新快照机械刷新决策卡的点位")
    parser.add_argument("--as-of", default=datetime.now(timezone(timedelta(hours=8))).date().isoformat(), metavar="YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="只打印会改什么，不写文件")
    args = parser.parse_args(argv)
    if not LADDER.exists():
        sys.exit(f"缺少 {LADDER}：先跑 scripts/etf_data.py 生成快照与 §6b 副本")
    sidecar = json.loads(LADDER.read_text(encoding="utf-8"))
    snapshot_ref = sidecar.get("snapshot") or f"research/etf-{sidecar['as_of'][:4]}-{sidecar['as_of'][4:6]}-{sidecar['as_of'][6:]}-data-snapshot.txt"
    snapshot = ROOT / snapshot_ref
    if not snapshot.exists():
        sys.exit(f"缺少 {snapshot}（副本指向的快照不存在）")
    snapshot_text = snapshot.read_text(encoding="utf-8")
    if "快照完成" not in snapshot_text:
        sys.exit(f"{snapshot} 不完整（无「快照完成」行）")
    ladder = {key: dict(row, snapshot_ref=snapshot_ref) for key, row in sidecar["indexes"].items()}

    documents = {}
    for path in sorted(validator.CARDS_DIR.glob("*.md")):
        try:
            documents[path] = validator.load_card(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            print(f"跳过 {path.name}: {exc}")
    current = {doc["card_id"]: doc for doc in validator.current_cards(list(documents.values()))}
    failed = False
    for path, document in documents.items():
        if current.get(document["card_id"]) is not document:
            continue
        new_text, outcome = refresh_card(path.read_text(encoding="utf-8"), ladder, args.as_of)
        if new_text is None:
            print(f"{document['card_id']}: 不刷新（{outcome}）")
            continue
        thesis_text = (ROOT / document["snapshot_ref"]).read_text(encoding="utf-8") if (ROOT / document["snapshot_ref"]).exists() else None
        errors = validator.validate_card(validator.load_card(new_text), snapshot_text=thesis_text, anchor_snapshot_text=snapshot_text,
                                         filename=Path(outcome["file"]).name)
        if thesis_text is None:
            errors.append(f"snapshot_ref: {document['snapshot_ref']} not found")
        if errors:
            failed = True
            print(f"{document['card_id']}: 刷新结果未通过校验，未写入")
            for error in errors:
                print(f"  - {error}")
            continue
        print(f"{document['card_id']} ({outcome['index_code']}): " + "、".join(
            f"{name} {outcome['old'][name]:,.2f}→{outcome['new'][name]:,.2f}" for name, _, _ in ANCHORS)
            + f"，valid_until {outcome['valid_until']}" + ("（dry-run）" if args.dry_run else f" → {outcome['file']}"))
        for name in outcome["stale_monitors"]:
            print(f"  ⚠ 监控「{name}」的阈值引用了锚点计算器但不等于任一锚点，未随刷新移动，请人工核")
        if not args.dry_run:
            (ROOT / outcome["file"]).write_text(new_text, encoding="utf-8")
    if not args.dry_run:
        print("刷新完成；接着运行 python3 scripts/validate_etf_card.py --export")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
