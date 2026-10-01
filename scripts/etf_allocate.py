"""Monthly run of framework v1.0: where this month's new money goes, and which checks fire.

Reads framework/etf_portfolio_params.json, the current cards under research/etf-cards/ and a holdings file the user
supplies; computes nothing that is not in etf_calc. The output is a buy list and a set of review flags for the user
to confirm, never an order.

CLI: python3 scripts/etf_allocate.py --holdings HOLDINGS.json [--new-money F] [--ledger LEDGER.csv]

HOLDINGS.json (market values in CNY, as of one date):
  {"as_of": "2026-10-31", "cash_cny": 0,
   "positions": [{"code": "022448.OF", "value_cny": 18916},
                 {"code": "02800.HK", "value_cny": 56000, "slot": "core-hsi"}],
   "theme_targets_pct": {"innovative-drug": 10}}
  `slot` is needed only for a holding no current card claims; `theme_targets_pct` overrides the theme cards' targets
  (a what-if, or the first month before the theme cards exist). Gold and other out-of-scope holdings are listed and
  left out of the strategy account.
LEDGER.csv: header `date,value_cny,flow_cny`, one row per month-end: strategy account total after that day's external
  flow, and the flow (deposits positive). Gives the unitized NAV and the drawdown review level.
"""

import argparse
import csv
import json
from pathlib import Path
import sys

try:
    from . import etf_calc
    from . import validate_etf_card as validator
except ImportError:  # direct script invocation
    import etf_calc
    import validate_etf_card as validator

CASH = "cash"


def _theme_targets(documents, override):
    targets = validator.allocation_targets(documents)
    theme = {document["sizing"]["bet_group"]: document["decision"]["target_weight_pct"]["value"]   # watch/no_buy hold 0
             for document in validator.current_cards(documents)
             if document["task"] == "theme" and document["status"] != "closed"}
    if override is not None:
        unknown = sorted(set(override) - set(validator.THEME_POOL))
        steps = validator.THEME_RULES["weight_steps_pct"]
        if unknown:
            raise ValueError(f"theme_targets_pct names seats outside the theme pool: {', '.join(unknown)}")
        if any(weight not in steps for weight in override.values()):
            raise ValueError(f"theme_targets_pct takes the approved steps {steps}")
        theme = dict(override)
    if sum(theme.values()) > validator.MODULES["theme"]["target_pct"]:
        raise ValueError("theme targets add up to more than the theme module")
    return theme, set(targets["paused"])


def plan_month(documents, holdings, new_money, ledger_rows=None):
    """Pure core of the CLI: documents are current cards that passed validation; returns a report dict."""
    params = validator._PARAMS
    claims = {row["code"]: document["sizing"]["bet_group"]
              for document in validator.current_cards(documents) if document["status"] != "closed"
              for row in document["instruments"]["list"] if row["role"] in validator.CLAIMING_ROLES}
    core = {seat["bet_group"]: seat for seat in validator.CORE_SEATS.values()}
    values, skipped, unmapped = {}, [], []
    for row in holdings["positions"]:
        code, value = row["code"], row["value_cny"]
        if code in params["out_of_scope_holdings"]:
            skipped.append(code)
            continue
        slot = row.get("slot") or claims.get(code)
        if row.get("slot") and claims.get(code) not in (None, row["slot"]):
            raise ValueError(f"{code}: holdings say {row['slot']}, the current cards say {claims[code]}")
        if slot is None:
            unmapped.append(code)
            continue
        if slot not in core and slot not in validator.THEME_POOL:
            raise ValueError(f"{code}: {slot} is neither a core seat nor a theme pool seat")
        values[slot] = values.get(slot, 0.0) + value
    if unmapped:
        raise ValueError("held but claimed by no current card and given no slot: " + ", ".join(unmapped))

    theme, paused = _theme_targets(documents, holdings.get("theme_targets_pct"))
    undecided = sorted(slot for slot in values if slot in validator.THEME_POOL and slot not in theme)
    if undecided:
        raise ValueError("theme seats held without a target (finish the theme review or write 0 in theme_targets_pct): "
                         + ", ".join(undecided))
    targets = {slot: seat["target_weight_pct"] for slot, seat in core.items()}
    targets.update({slot: weight for slot, weight in theme.items() if weight > 0})
    theme_cash_pct = validator.MODULES["theme"]["target_pct"] - sum(theme.values())

    drawdown, review = None, None
    if ledger_rows:
        navs = etf_calc.unit_nav(ledger_rows)
        drawdown = etf_calc.drawdown_summary([nav for _, nav in navs])
        rules = params["drawdown_review"]
        level = drawdown["current_drawdown_pct"]
        review = ("reapprove_risk_budget" if level <= rules["reapprove_risk_budget_pct"]
                  else "pause_new_theme_risk" if level <= rules["pause_new_theme_risk_pct"]
                  else "special_review" if level <= rules["special_review_pct"] else None)
        if review in ("reapprove_risk_budget", "pause_new_theme_risk"):
            paused |= set(theme)   # core DCA continues by default during the review (framework A10)
    held_zero = {slot: 0 for slot in values if slot not in targets}   # a theme at 0: held, being exited, takes nothing
    total = sum(values.values()) + holdings.get("cash_cny", 0) + new_money
    theme_held_pct = 100 * sum(value for slot, value in values.items() if slot in validator.THEME_POOL) / total if total else 0.0
    reserve_pct = etf_calc.theme_cash_reserve_pct(validator.MODULES["theme"]["target_pct"], sum(theme.values()), theme_held_pct)
    allocation = etf_calc.dca_gap_allocation({**targets, **held_zero}, values, holdings.get("cash_cny", 0), new_money,
                                             reserved_cash_pct=reserve_pct, paused=paused)

    def check(slot_values, cash):
        reserve = min(cash, reserve_pct * allocation["total"] / 100)
        amounts = {**slot_values, "theme_cash": reserve, CASH: cash - reserve}
        modules = {slot: core[slot]["module"] if slot in core else "theme" for slot in slot_values}
        modules.update(theme_cash="theme", **{CASH: "unassigned"})
        bands = {name: tuple(module["band_pct"]) for name, module in validator.MODULES.items()}
        bands["unassigned"] = (0, 100)
        drift_slots = (validator.CORE_SEATS[key]["bet_group"] for key in params["rebalance"]["drift_items"])
        return etf_calc.allocation_check(
            amounts, modules, bands, drift_targets_pct={slot: targets[slot] for slot in drift_slots},
            drift_relative_pct=params["rebalance"]["drift_relative_pct"], drift_cap_pp=params["rebalance"]["drift_cap_pp"],
            ceilings_pct={slot: validator.THEME_RULES["review_above_pct"] for slot in sorted(slot_values) if slot in validator.THEME_POOL})

    after_values = {slot: values.get(slot, 0.0) + allocation["buys"].get(slot, 0.0)
                    for slot in sorted(set(values) | set(allocation["buys"]))}
    stress = {scenario: etf_calc.joint_stress_loss(
        [(amount, core[slot][f"stress_{scenario}_pct"] if slot in core else validator.THEME_RULES[f"stress_{scenario}_pct"])
         for slot, amount in after_values.items()])["loss"] / allocation["total"] * 100 for scenario in ("plan", "historical")}
    before = check(values, holdings.get("cash_cny", 0) + new_money)
    after = check(after_values, allocation["cash_after"])
    return dict(as_of=holdings.get("as_of"), skipped=skipped, targets_pct=targets, theme_cash_pct=theme_cash_pct,
                theme_cash_reserve_pct=reserve_pct, paused=sorted(paused), allocation=allocation, check_before=before, check_after=after,
                stress_loss_pct=stress, drawdown=drawdown, drawdown_review=review)


def _read_ledger(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return [(row["date"].replace("-", ""), float(row["value_cny"]), float(row["flow_cny"] or 0))
                for row in csv.DictReader(handle)]


def _print(report):
    allocation = report["allocation"]
    print(f"== ETF 月度分配 | 持仓日 {report['as_of']} | 入金后策略账户 {allocation['total']:,.0f} 元 ==")
    if report["skipped"]:
        print("不计入策略账户（单列管理）: " + ", ".join(report["skipped"]))
    print(f"主题待配现金目标 {report['theme_cash_pct']}%，本月实际留存 {report['theme_cash_reserve_pct']:.1f}%"
          f"（主题股票已占的部分不再重复留现金）；暂停接收新增资金: {', '.join(report['paused']) or '无'}")
    print(f"可用于补缺口 {allocation['available']:,.0f} 元（先留足主题待配现金）")
    for slot in sorted(allocation["buys"]):
        if allocation["gaps"][slot] > 0.5:
            print(f"  {slot:<26} 目标 {report['targets_pct'].get(slot, 0):>4}%  缺口 {allocation['gaps'][slot]:>10,.0f}"
                  f"  本月买入 {allocation['buys'][slot]:>10,.0f}")
    print(f"本月后现金 {allocation['cash_after']:,.0f} 元；未补足缺口 {allocation['unfilled']:,.0f} 元")
    for label, check in (("本月前", report["check_before"]), ("本月后", report["check_after"])):
        modules = "、".join(f"{name} {weight:.1f}%" for name, weight in check["module_weights_pct"].items())
        print(f"{label}模块权重: {modules}")
        for module in check["modules_out_of_band"]:
            print(f"  ⚠ {module} 超出区间 {validator.MODULES.get(module, {}).get('band_pct')}")
        for row in check["drifted"]:
            print(f"  ⚠ {row['slot']} {row['weight_pct']:.1f}% 偏离目标 {row['target_pct']}% 超过 {row['threshold_pp']:.2f}pp：复核")
        for row in check["above_ceiling"]:
            print(f"  ⚠ 主题 {row['slot']} {row['weight_pct']:.1f}% 超过 {row['ceiling_pct']}%：提前复核")
    print(f"买入后压力损失（占账户）: 方案情景 {report['stress_loss_pct']['plan']:.1f}% / 历史情景 {report['stress_loss_pct']['historical']:.1f}%")
    if report["drawdown"] is not None:
        print(f"单位净值回撤: 当前 {report['drawdown']['current_drawdown_pct']:.1f}% / 最大 {report['drawdown']['max_drawdown_pct']:.1f}%"
              + (f" → {report['drawdown_review']}（框架 A10）" if report["drawdown_review"] else ""))
    print("以上是建议清单，交易由用户确认。")


def main(argv=None):
    parser = argparse.ArgumentParser(description="ETF 月度新增资金分配与检查（框架 v1.0）")
    parser.add_argument("--holdings", required=True, help="持仓 JSON（格式见脚本说明）")
    parser.add_argument("--new-money", type=float, default=None, help="本月入金；缺省取组合参数 new_money.monthly_amount_cny")
    parser.add_argument("--ledger", default=None, help="策略账户月末市值与外部资金流 CSV（date,value_cny,flow_cny）")
    args = parser.parse_args(argv)
    new_money = args.new_money if args.new_money is not None else validator._PARAMS["new_money"]["monthly_amount_cny"]
    if new_money is None:
        parser.error("每月入金 F 还没写进组合参数：用 --new-money 给出")
    documents = []
    for path in sorted(validator.CARDS_DIR.glob("*.md")):
        errors, document = validator._checked(path)
        if errors:
            sys.exit(f"{path.name} 未通过校验，先修卡：python3 scripts/validate_etf_card.py")
        documents.append(document)
    conflicts = validator.cross_card_errors(documents)
    if conflicts:
        sys.exit("现行卡之间有冲突，先修卡：\n  - " + "\n  - ".join(conflicts))
    holdings = json.loads(Path(args.holdings).read_text(encoding="utf-8"))
    try:
        report = plan_month(documents, holdings, new_money, _read_ledger(args.ledger) if args.ledger else None)
    except ValueError as exc:
        sys.exit(str(exc))
    _print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
