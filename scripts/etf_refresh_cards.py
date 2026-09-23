"""Mechanical monthly refresh of decision-card anchors (framework A1: 点位每月随快照机械刷新，不改论点).

Reads research/etf-ladder-latest.json (the machine-readable copy of snapshot §6b) and, for every current
card that carries anchors, recomputes the three levels from the new 36-month high and the new state
quantiles. A card whose inputs changed gets a new version file <card_id>-<as_of>.md that supersedes the
old one: JSON anchors, snapshot_ref, valid_until and the auto monitors that cite an anchor are updated,
the prose keeps its thesis and only has the old anchor numbers swapped for the new ones, and a note under
the title says the refresh was mechanical. Nothing else in the card is touched; a thesis review is the
etf-card-research skill's job, not this script's.

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
ANCHOR_QUANTILES = (("add_below", "P10"), ("buy_below", "P25"), ("reduce_above", "P75"))
JSON_BLOCK = re.compile(r"(?ms)^```json[ \t]*\n(.*?)^```[ \t]*$")


def end_of_next_month(day):
    year, month = (day.year + 1, 1) if day.month == 12 else (day.year, day.month + 1)
    return date(year, month, calendar.monthrange(year, month)[1])


def _prose_forms(value):
    """Both spellings a level may take in prose: 2,297.84 and 2297.84."""
    return {f"{value:,.2f}", f"{value:.2f}"}


def refresh_card(text, ladder, as_of):
    """Return (new_text, changes) for one card, or (None, reason) when nothing is to be refreshed.

    text: the card file's full text; ladder: the sidecar's "indexes" mapping; as_of: refresh date (ISO string).
    """
    document = validator.load_card(text)
    anchors = document["decision"]["anchors"]
    if document["status"] == "closed":
        return None, "closed"
    if anchors["add_below"]["level"]["value"] is None:
        return None, "no anchors"
    row = ladder.get(anchors["index_code"])
    if row is None:
        return None, f"{anchors['index_code']} not in ladder sidecar"
    old_levels = {name: anchors[name]["level"]["value"] for name, _ in ANCHOR_QUANTILES}
    new_inputs = {name: (row["rolling_high"], row["states"][quantile]) for name, quantile in ANCHOR_QUANTILES}
    if all((anchors[name]["inputs"]["rolling_high"]["value"], anchors[name]["inputs"]["state"]["value"]) == new_inputs[name]
           for name, _ in ANCHOR_QUANTILES):
        return None, "inputs unchanged"
    new_levels = {name: round(level_at_drawdown_state(high, state), 2) for name, (high, state) in new_inputs.items()}
    for name, quantile in ANCHOR_QUANTILES:
        high, state = new_inputs[name]
        anchors[name]["level"]["value"] = new_levels[name]
        anchors[name]["inputs"]["rolling_high"]["value"] = high
        anchors[name]["inputs"]["state"]["value"] = state
    anchors["valid_until"] = end_of_next_month(date.fromisoformat(as_of)).isoformat()
    for monitor in document["monitor_variables"]:   # auto monitors pinned to an anchor move with it
        threshold = monitor["threshold"]
        if threshold["source"] == "calc:level_at_drawdown_state":
            for name, _ in ANCHOR_QUANTILES:
                if threshold["value"] == old_levels[name]:
                    threshold["value"] = new_levels[name]
    old_file = f"research/etf-cards/{document['card_id']}-{document['as_of_date']}.md"
    document.update(as_of_date=as_of, supersedes=old_file,
                    snapshot_ref=f"research/etf-{row['snapshot_as_of']}-data-snapshot.txt")

    block = JSON_BLOCK.search(text)
    prose = text[:block.start()]
    for name, _ in ANCHOR_QUANTILES:
        for form in _prose_forms(old_levels[name]):
            prose = prose.replace(form, f"{new_levels[name]:,.2f}")
    note = (f"> **点位机械刷新 @{as_of}**（快照 {row['snapshot_as_of']}，36 月高点 {row['rolling_high']:,.2f}）："
            + "、".join(f"{name} {old_levels[name]:,.2f}→{new_levels[name]:,.2f}" for name, _ in ANCHOR_QUANTILES)
            + "。论点、监控与失效条件未复核，上一版见 supersedes。\n")
    title_end = prose.index("\n") + 1
    prose = prose[:title_end] + "\n" + note + prose[title_end:]
    new_text = prose + "```json\n" + json.dumps(document, ensure_ascii=False, indent=2) + "\n```\n" + text[block.end():]
    changes = dict(card_id=document["card_id"], index_code=anchors["index_code"], old=old_levels, new=new_levels,
                   valid_until=anchors["valid_until"], file=f"research/etf-cards/{document['card_id']}-{as_of}.md")
    return new_text, changes


def main(argv=None):
    parser = argparse.ArgumentParser(description="按最新快照机械刷新决策卡的点位")
    parser.add_argument("--as-of", default=datetime.now(timezone(timedelta(hours=8))).date().isoformat(), metavar="YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="只打印会改什么，不写文件")
    args = parser.parse_args(argv)
    if not LADDER.exists():
        sys.exit(f"缺少 {LADDER}：先跑 scripts/etf_data.py 生成快照与 §6b 副本")
    sidecar = json.loads(LADDER.read_text(encoding="utf-8"))
    snapshot_as_of = f"{sidecar['as_of'][:4]}-{sidecar['as_of'][4:6]}-{sidecar['as_of'][6:]}"
    ladder = {key: dict(row, snapshot_as_of=snapshot_as_of) for key, row in sidecar["indexes"].items()}
    snapshot = ROOT / f"research/etf-{snapshot_as_of}-data-snapshot.txt"
    if not snapshot.exists():
        sys.exit(f"缺少 {snapshot}")
    snapshot_text = snapshot.read_text(encoding="utf-8")

    paths = sorted(validator.CARDS_DIR.glob("*.md"))
    documents = {}
    for path in paths:
        try:
            document = validator.load_card(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            print(f"跳过 {path.name}: {exc}")
            continue
        documents[path] = document
    current = {doc["card_id"]: doc for doc in validator.current_cards(list(documents.values()))}
    failed = False
    for path, document in documents.items():
        if current.get(document["card_id"]) is not document:
            continue
        new_text, outcome = refresh_card(path.read_text(encoding="utf-8"), ladder, args.as_of)
        if new_text is None:
            print(f"{document['card_id']}: 不刷新（{outcome}）")
            continue
        errors = validator.validate_card(validator.load_card(new_text), snapshot_text=snapshot_text,
                                         filename=Path(outcome["file"]).name)
        if errors:
            failed = True
            print(f"{document['card_id']}: 刷新结果未通过校验，未写入")
            for error in errors:
                print(f"  - {error}")
            continue
        print(f"{document['card_id']} ({outcome['index_code']}): " + "、".join(
            f"{name} {outcome['old'][name]:,.2f}→{outcome['new'][name]:,.2f}" for name, _ in ANCHOR_QUANTILES)
            + f"，valid_until {outcome['valid_until']}" + ("（dry-run）" if args.dry_run else f" → {outcome['file']}"))
        if not args.dry_run:
            (ROOT / outcome["file"]).write_text(new_text, encoding="utf-8")
    if not args.dry_run:
        print("刷新完成；接着运行 python3 scripts/validate_etf_card.py --export")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
