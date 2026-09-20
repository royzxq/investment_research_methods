"""Pre-registered rule validation for the ETF track.

Protocol: research/etf-2026-09-19-rule-prereg.md. Nothing here may be tuned after results are seen.
The simulation core is pure Python on monthly lists (a fold has at most 72 months), so the unit
tests need no pandas; the data layer at the bottom imports pandas/tushare lazily and is only used by
the CLI:  python3 scripts/etf_backtest.py --as-of 20260918

Conventions: month t's signal is known at month-end t and traded at that close; return[t] is the
asset's return over month t, earned on the position carried out of month t-1. Rates are fractions
here (0.01 = 1%); the report prints percent.
"""

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

try:
    from .etf_calc import expanding_percentile, month_end_levels, sma_state
except ImportError:  # direct script invocation
    from etf_calc import expanding_percentile, month_end_levels, sma_state

BUY_COST = 0.0015
LADDER = ((10, 1.0), (25, 0.5))          # q <= threshold -> buy up to this share of the account
REDUCE_AT, REDUCE_TO = 75, 0.3           # q >= REDUCE_AT -> sell down to REDUCE_TO
FOLDS = (("F1", "200501", "201012"), ("F2", "201101", "201612"), ("F3", "201701", "202212"), ("F4", "202301", "202608"))
MIN_SIGNAL_SHARE = 0.8
CYCLICAL_KEYS = {"000819.SH", "000813.CSI", "399975.SZ", "931151.CSI", "399976.SZ"}   # R1 uses PB for these
ANNUAL_FEE = {"broad": 0.0020, "sector": 0.0060, "gold": 0.0060}


# ------------------------------------------------------------------ simulation core
def ladder_target(quantile, weight):
    """Desired equity share after this month-end's decision; None means leave the position alone."""
    if quantile is None:
        return None
    for threshold, target in LADDER:
        if quantile <= threshold:
            return target if weight < target else None       # buy zone only buys
    if quantile >= REDUCE_AT:
        return REDUCE_TO if weight > REDUCE_TO else None      # reduce zone only sells
    return None


def _trade(equity, cash, target):
    """Move the account to `target` equity share; purchases pay BUY_COST, sales are free."""
    value = equity + cash
    change = target * value - equity
    if change > 0:
        change = min(change, cash)
        return equity + change * (1 - BUY_COST), cash - change
    return equity + change, cash - change


def run_ladder(returns, cash_returns, quantiles, gate=None):
    """Account of 1 unit, all cash at the start. Returns per-month account values and equity shares.

    Index 0 is the fold's opening decision; returns[t] for t >= 1 accrues after decision t-1.
    gate[t] False blocks purchases at t (sales still happen); None means no gate.
    """
    equity, cash, values, weights = 0.0, 1.0, [], []
    for t, quantile in enumerate(quantiles):
        if t:
            equity *= 1 + returns[t]
            cash *= 1 + cash_returns[t]
        weight = equity / (equity + cash)
        target = ladder_target(quantile, weight)
        blocked = target is not None and target > weight and gate is not None and not gate[t]   # the gate stops buys only
        if target is not None and not blocked:
            equity, cash = _trade(equity, cash, target)
        values.append(equity + cash)
        weights.append(equity / (equity + cash))
    return values, weights


def run_constant_mix(returns, cash_returns, weight):
    """Rebalanced to `weight` every month-end: the no-timing way to hold the ladder's average exposure."""
    equity, cash, values = 0.0, 1.0, []
    for t in range(len(returns)):
        if t:
            equity *= 1 + returns[t]
            cash *= 1 + cash_returns[t]
        equity, cash = _trade(equity, cash, weight)
        values.append(equity + cash)
    return values


def run_dca(returns, cash_returns, gate=None):
    """One unit arrives every month-end. Gate closed -> it stays in cash for good. Returns (values, flows)."""
    equity, cash, values = 0.0, 0.0, []
    for t in range(len(returns)):
        if t:
            equity *= 1 + returns[t]
            cash *= 1 + cash_returns[t]
        if gate is None or gate[t]:
            equity += 1 - BUY_COST
        else:
            cash += 1
        values.append(equity + cash)
    return values, [1.0] * len(returns)


# ------------------------------------------------------------------ metrics
def time_weighted(values, flows=None):
    """Chain-linked index of the account, contributions removed: r_t = (V_t - flow_t) / V_{t-1} - 1."""
    index = [1.0]
    for t in range(1, len(values)):
        flow = flows[t] if flows else 0.0
        index.append(index[-1] * (values[t] - flow) / values[t - 1])
    return index


def max_drawdown(index):
    peak, worst = index[0], 0.0
    for level in index:
        peak = max(peak, level)
        worst = min(worst, level / peak - 1)
    return worst


def annualized(index, start=None):
    """Annualized growth over len(index) - 1 months. `start` is the capital before the opening trade:
    pass 1.0 for the lump-sum accounts so that a purchase fee paid at t=0 is charged, not cancelled."""
    months = len(index) - 1
    base = index[0] if start is None else start
    return (index[-1] / base) ** (12 / months) - 1 if months > 0 and index[-1] > 0 else None


def money_weighted(values, flows):
    """Annualized IRR of equal-dated monthly contributions against the terminal value (bisection)."""
    def gap(rate):
        return sum(flow * (1 + rate) ** (len(flows) - 1 - t) for t, flow in enumerate(flows)) - values[-1]
    low, high = -0.5, 0.5
    if gap(low) > 0 or gap(high) < 0:
        return None
    for _ in range(200):
        middle = (low + high) / 2
        low, high = (middle, high) if gap(middle) < 0 else (low, middle)
    return (1 + (low + high) / 2) ** 12 - 1


def downside_capture(strategy_index, baseline_index):
    pairs = [(strategy_index[t] / strategy_index[t - 1] - 1, baseline_index[t] / baseline_index[t - 1] - 1)
             for t in range(1, len(baseline_index))]
    down = [(own, base) for own, base in pairs if base < 0]
    return sum(own for own, _ in down) / sum(base for _, base in down) if down else None


def judge(folds, *, skill=False):
    """Pre-registered verdict for one rule on one index.

    folds: [{"drawdown": (strategy, baseline), "annual": (strategy, baseline)[, "annual_mix": (strategy, mix)]}].
    """
    folds = [fold for fold in folds if None not in fold["annual"] and None not in fold.get("annual_mix", ())]
    if len(folds) < 3:
        return dict(verdict="insufficient_data", folds=len(folds))
    better = sum(1 for fold in folds if fold["drawdown"][0] > fold["drawdown"][1])     # drawdowns are <= 0
    gaps = [fold["annual"][0] - fold["annual"][1] for fold in folds]
    mean, sigma = statistics.mean(gaps), statistics.stdev(gaps)
    cost_ok = mean >= 0 or (sigma > 0 and abs(mean) / sigma < 1)
    result = dict(folds=len(folds), drawdown_better=better, annual_gap_mean=mean, annual_gap_sigma=sigma,
                  risk_ok=better >= 3, cost_ok=cost_ok)
    if skill:
        result["skill_gap_mean"] = statistics.mean(fold["annual_mix"][0] - fold["annual_mix"][1] for fold in folds)
        result["skill_ok"] = result["skill_gap_mean"] >= 0
    passed = result["risk_ok"] and cost_ok and result.get("skill_ok", True)
    result["verdict"] = "pass" if passed else ("no_timing_skill" if skill and result["risk_ok"] and cost_ok else "fail")
    return result


def rule_verdict(primary, others):
    """Combine per-index verdicts; insufficient-data indexes do not vote."""
    voters = [item for item in others if item["verdict"] != "insufficient_data"]
    passed = sum(1 for item in voters if item["verdict"] == "pass")
    if primary["verdict"] == "insufficient_data":
        return "data_insufficient"
    if primary["verdict"] == "no_timing_skill":
        return "rejected(no_timing_skill)"
    if primary["verdict"] != "pass":
        return "rejected"
    return "validated" if voters and passed * 2 > len(voters) else "validated(primary_index_only)"


# ------------------------------------------------------------------ signals
def percentile_series(days, values):
    """Expanding percentile at every month using only data up to that month (None where not concluded)."""
    result = []
    for t in range(len(days)):
        outcome = expanding_percentile(list(zip(days[:t + 1], values[:t + 1])))
        result.append(outcome["percentile"])
    return result


def drawdown_state(closes, window=36):
    """1 + drawdown from the trailing `window`-month high (incl. the current month); lower = deeper."""
    return [close / max(closes[max(0, t - window + 1):t + 1]) for t, close in enumerate(closes)]


def trend_gate(closes, window=10):
    """True above the average, False at or below it, None while the average does not exist yet (treated as closed)."""
    states = [sma_state(closes[:t + 1], window)["state"] for t in range(len(closes))]
    return [None if state is None else state == "above" for state in states]


def lagged(series):
    return [None] + list(series[:-1])


# ------------------------------------------------------------------ per-index evaluation
def fold_slices(months):
    """months: ['YYYYMM', ...] ascending -> [(fold name, start index, end index inclusive, calendar months in the fold)].

    The calendar length is the denominator of the 80% signal rule: a series that starts mid-fold
    does not get a shorter fold to qualify on.
    """
    slices = []
    for name, first, last in FOLDS:
        inside = [t for t, month in enumerate(months) if first <= month <= last]
        length = (int(last[:4]) - int(first[:4])) * 12 + int(last[4:]) - int(first[4:]) + 1
        if inside:
            slices.append((name, inside[0], inside[-1], length))
    return slices


def evaluate_ladder(months, returns, cash_returns, quantiles, gate=None, baseline="hold"):
    """R1/R2 (baseline='hold': vs buy-and-hold plus the constant-mix skill test) or R3 (baseline='ungated')."""
    rows = []
    for name, start, end, length in fold_slices(months):
        q = quantiles[start:end + 1]
        if sum(value is not None for value in q) < MIN_SIGNAL_SHARE * length:
            continue
        r, c = returns[start:end + 1], cash_returns[start:end + 1]
        g = gate[start:end + 1] if gate is not None else None
        values, weights = run_ladder(r, c, q, g)
        if baseline == "hold":
            reference = run_constant_mix(r, c, 1.0)
            mix = run_constant_mix(r, c, statistics.mean(weights))
        else:
            reference, _ = run_ladder(r, c, q, None)
            mix = None
        row = dict(fold=name, months=len(q), average_weight=statistics.mean(weights),
                   drawdown=(max_drawdown([1.0] + values), max_drawdown([1.0] + reference)),
                   annual=(annualized(values, 1.0), annualized(reference, 1.0)),
                   downside_capture=downside_capture(values, reference))
        if mix is not None:
            row["annual_mix"] = (annualized(values, 1.0), annualized(mix, 1.0))
            row["drawdown_mix"] = max_drawdown([1.0] + mix)
        rows.append(row)
    return rows, judge(rows, skill=baseline == "hold")


def evaluate_dca_pause(months, returns, cash_returns, closes, gate=None):
    """gate: per-month trend state from the full price history; None -> derive it from `closes` (tests)."""
    gate, rows = gate if gate is not None else trend_gate(closes), []
    for name, start, end, length in fold_slices(months):
        if gate[start] is None or end - start + 1 < MIN_SIGNAL_SHARE * length:    # no 10-month average at the fold's start, or too little of the fold covered
            continue
        r, c = returns[start:end + 1], cash_returns[start:end + 1]
        paused, flows = run_dca(r, c, gate[start:end + 1])
        fixed, _ = run_dca(r, c)
        rows.append(dict(fold=name, months=len(r), paused_months=sum(not state for state in gate[start:end + 1]),
                         drawdown=(max_drawdown(time_weighted(paused, flows)), max_drawdown(time_weighted(fixed, flows))),
                         annual=(money_weighted(paused, flows), money_weighted(fixed, flows)),
                         downside_capture=downside_capture(time_weighted(paused, flows), time_weighted(fixed, flows))))
    return rows, judge(rows)


# ------------------------------------------------------------------ data layer and report (CLI only)
PREREG = "research/etf-2026-09-19-rule-prereg.md"
ROOT = Path(__file__).resolve().parents[1]
CASH_KEY = "H11025.CSI"
BROAD_KEYS = {"000300.SH", "000510.SH", "000905.SH", "HSI", "H30269.CSI", "000012.SH", "SPX"}
PRIMARY = {"R1": "000300.SH", "R2": "HSI", "R3(R1)": "000300.SH", "R3(R2)": "HSI", "R4": "000300.SH"}


def prereg_commit():
    """The protocol is only worth something if it was frozen first: refuse to run on an uncommitted prereg."""
    run = lambda *args: subprocess.run(["git", *args, "--", PREREG], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    commit = run("log", "-1", "--format=%h %cI")
    if run("status", "--porcelain") or not commit:
        sys.exit(f"{PREREG} 尚未提交或有未提交改动；先提交预注册，再跑验证。")
    return commit


def valuation_check(as_of):
    """Prereg section 1: R1 gets a verdict only if this snapshot's section 4a replication of the vendor PE passed."""
    path = ROOT / "output" / "etf_valuation_check.json"
    if not path.exists():
        return None, f"缺少 {path.name}：先用同一 --as-of 跑 scripts/etf_data.py"
    check = json.loads(path.read_text(encoding="utf-8"))
    if check["as_of"] != as_of:
        return check, f"{path.name} 的 AS_OF={check['as_of']} 与本次 {as_of} 不一致：估值序列不是同一次快照产出的"
    return check, None if check["usable"] else "快照 §4a 判定原始数据与成分口径不可用"


def by_month(days, values):
    """{'YYYYMM': (last day in the month, its value)} from ascending daily observations."""
    return {f"{day.year}{day.month:02d}": (day, value) for day, value in month_end_levels(list(zip(days, values)))}


def consecutive_tail(months):
    """The latest unbroken run of calendar months: a missing month would turn one return into a two-month return."""
    tail = [months[-1]]
    for month in reversed(months[:-1]):
        year, number = int(tail[0][:4]), int(tail[0][4:])
        if month != (f"{year - 1}12" if number == 1 else f"{year}{number - 1:02d}"):
            break
        tail.insert(0, month)
    return tail


def load_series(data, code, source, notes, name):
    df, complete = data.paged_history(f"{source}:{code}", lambda end: getattr(data.api(), source)(ts_code=code, end_date=end),
                                      pause=6.5 if source == "index_global" else 0.35)   # index_global: 10 calls a minute
    if df is None:
        return None
    if not complete:
        notes.append(f"{name} {code}: 历史翻页中断，序列自 {df['trade_date'].iloc[0]} 起（更早的缺失）")
    df = df.dropna(subset=["close"])
    return by_month(list(df["trade_date"]), [float(value) for value in df["close"]])


def index_inputs(data, entry, fx, cash, notes):
    """Signals from the full price history in the index's own currency; returns in CNY net of the fund fee,
    total-return when the registry has one. Everything is keyed by month so nothing is truncated to the cash index."""
    price = load_series(data, entry["code"], entry["source"], notes, entry["name"])
    if price is None:
        return None
    total = load_series(data, entry["tr_code"], "index_daily", notes, entry["name"]) if entry.get("tr_code") else None
    levels = total or price
    if entry["currency"] not in ("CNY", None):
        levels = {month: (day, value * fx[entry["currency"]][month]) for month, (day, value) in levels.items()
                  if month in fx[entry["currency"]]}
    fee = ANNUAL_FEE["gold" if entry["key"] == "Au99.99" else "broad" if entry["key"] in BROAD_KEYS else "sector"]
    months = consecutive_tail(sorted(month for month in levels if month in cash and month in price))
    returns = [0.0] + [levels[months[t]][1] / levels[months[t - 1]][1] * (1 - fee / 12) - 1 for t in range(1, len(months))]
    price_months = sorted(price)
    days, closes = [price[month][0] for month in price_months], [price[month][1] for month in price_months]
    return dict(months=months, returns=returns, cash=[cash[month] for month in months],
                closes=[price[month][1] for month in months],
                drawdown_q=dict(zip(price_months, percentile_series(days, drawdown_state(closes)))),
                gate=dict(zip(price_months, trend_gate(closes))),
                note=f"{entry['name']} {entry['key']}: 回测 {months[0]}→{months[-1]}，信号史自 {price_months[0]}，"
                     f"收益口径 {'total_return' if total else 'price'}，币种 {entry['currency'] or '未核(按人民币)'}，年费 {fee * 100:.2f}%")


def valuation_quantiles(key):
    """Lagged expanding percentile of the self-aggregated multiple (PB for cyclicals), keyed by month; None without a series."""
    import pandas as pd
    path = ROOT / "output" / f"etf_valuation_{key}.csv"
    if not path.exists():
        return None, None
    column = "pb" if key in CYCLICAL_KEYS else "pe_ttm"
    df = pd.read_csv(path, dtype={"trade_date": str})
    df = df[(df["status"] == "complete") & df[column].notna()].sort_values("trade_date")
    monthly = by_month(list(df["trade_date"]), [float(value) for value in df[column]])
    months = sorted(monthly)
    quantiles = percentile_series([monthly[month][0] for month in months], [monthly[month][1] for month in months])
    return dict(zip(months, lagged(quantiles))), column


def fmt(value, pct=True):
    return "—" if value is None else (f"{value * 100:+.1f}%" if pct else f"{value:.2f}")


def fold_table(rows, mix):
    head = "| 折 | 月数 | 平均仓位 | 回撤 策略/对照 | 年化 策略/对照 |" + (" 年化 恒定比例 | 回撤 恒定比例 |" if mix else "") + " 下行捕获 |"
    lines = [head, "|" + "---|" * (head.count("|") - 1)]
    for row in rows:
        cells = [row["fold"], str(row["months"]), fmt(row["average_weight"]) if "average_weight" in row else f"暂停 {row['paused_months']} 月",
                 f"{fmt(row['drawdown'][0])} / {fmt(row['drawdown'][1])}", f"{fmt(row['annual'][0])} / {fmt(row['annual'][1])}"]
        if mix:
            cells += [fmt(row["annual_mix"][1]), fmt(row["drawdown_mix"])]
        lines.append("| " + " | ".join(cells + [fmt(row["downside_capture"], pct=False)]) + " |")
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description="ETF 轨道预注册规则验证（先提交预注册，再跑）")
    parser.add_argument("--as-of", default="20260918", metavar="YYYYMMDD")
    args = parser.parse_args(argv)
    commit = prereg_commit()
    try:
        from . import etf_data as data
    except ImportError:
        import etf_data as data
    data.AS_OF = data.CUTOFF = args.as_of
    data.requests.Session.request = data._request_with_timeout
    check, blocked = valuation_check(args.as_of)
    registry = {entry["key"]: entry for entry in data.INDEX_POOL}
    notes = []
    rates = data.fx_rates()
    if rates is None:
        sys.exit("外管局中间价不可得：外币指数无法折人民币，未运行。")
    fx = {currency: {month: value for month, (_, value) in by_month(list(rates["trade_date"]), list(rates[currency])).items()}
          for currency in ("HKD", "USD")}
    cash_levels = load_series(data, registry[CASH_KEY]["code"], "index_daily", notes, "现金代理")
    if cash_levels is None:
        sys.exit(f"现金代理 {CASH_KEY} 行情不可得，未运行。")
    cash_months = sorted(cash_levels)
    cash = {month: cash_levels[month][1] / cash_levels[previous][1] - 1 for previous, month in zip(cash_months, cash_months[1:])}

    results = {rule: {} for rule in PRIMARY}
    for key, entry in registry.items():
        if not entry["source"] or key == CASH_KEY:
            continue
        inputs = index_inputs(data, entry, fx, cash, notes)
        if inputs is None:
            notes.append(f"{entry['name']} {key}: 行情不可得，未参与")
            continue
        months, returns, cash_returns = inputs["months"], inputs["returns"], inputs["cash"]
        gate = [inputs["gate"].get(month) for month in months]
        drawdown_q = [inputs["drawdown_q"].get(month) for month in months]
        results["R2"][key] = evaluate_ladder(months, returns, cash_returns, drawdown_q)
        results["R3(R2)"][key] = evaluate_ladder(months, returns, cash_returns, drawdown_q, gate, "ungated")
        results["R4"][key] = evaluate_dca_pause(months, returns, cash_returns, inputs["closes"], gate)
        by_key, column = valuation_quantiles(key)
        if by_key is not None and not blocked:
            valuation_q = [by_key.get(month) for month in months]
            results["R1"][key] = evaluate_ladder(months, returns, cash_returns, valuation_q)
            results["R3(R1)"][key] = evaluate_ladder(months, returns, cash_returns, valuation_q, gate, "ungated")
            inputs["note"] += f"，R1 状态变量 {column}"
        notes.append(inputs["note"])

    out = [f"# ETF 轨道规则验证报告（数据截至 {args.as_of}）", "",
           f"> 预注册：`{PREREG}` @ {commit}。本报告由 `scripts/etf_backtest.py` 生成，未经手工改数。", "",
           "## 估值数据核对（预注册 §1 的前置条件）", ""]
    if check:
        out += [f"快照 AS_OF={check['as_of']}：可核对日 {check['checked_days']} 个，最大偏差 "
                f"{fmt(check['max_deviation_pct'] / 100) if check['max_deviation_pct'] is not None else '—'}，"
                f"结论：{'可用' if check['usable'] else '不可用'}。", "",
                "| " + " | ".join(check["rows"][0]) + " |", "|" + "---|" * len(check["rows"][0])]
        out += ["| " + " | ".join(str(value) for value in row.values()) + " |" for row in check["rows"]]
    if blocked:
        out += ["", f"**R1 与 R3(R1) 记「数据不可验证」，不出 validated / rejected 结论**：{blocked}。"]
    out += ["", "## 结论", "", "| 规则 | 主指数 | 主指数结论 | 其余参与指数 通过/有结论 | 规则结论 |", "|---|---|---|---|---|"]
    body = []
    for rule, per_index in results.items():
        if blocked and rule in ("R1", "R3(R1)"):
            out.append(f"| {rule} | {registry[PRIMARY[rule]]['name']} | — | — | **data_unverifiable** |")
            continue
        primary = per_index.get(PRIMARY[rule], ([], dict(verdict="insufficient_data")))[1]
        others = [verdict for key, (_, verdict) in per_index.items() if key != PRIMARY[rule]]
        voters = [item for item in others if item["verdict"] != "insufficient_data"]
        out.append(f"| {rule} | {registry[PRIMARY[rule]]['name']} | {primary['verdict']} | "
                   f"{sum(item['verdict'] == 'pass' for item in voters)}/{len(voters)} | **{rule_verdict(primary, others)}** |")
        body += ["", f"## {rule}", ""]
        for key, (rows, verdict) in per_index.items():
            summary = ", ".join(f"{name}={fmt(value) if isinstance(value, float) else value}" for name, value in verdict.items())
            body += [f"### {registry[key]['name']} {key} — {verdict['verdict']}", "", summary, ""]
            body += fold_table(rows, mix=rule in ("R1", "R2")) if rows else ["（无适用折）"]
            body.append("")
    failed = {label: status for label, status in data.INTERFACES.items() if status != "通"}
    out += body + ["## 数据", ""] + [f"- {note}" for note in notes] + [f"- 接口异常 {label}: {status}" for label, status in failed.items()]
    target = ROOT / "research" / f"etf-{args.as_of[:4]}-{args.as_of[4:6]}-{args.as_of[6:]}-rule-validation.md"
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"written {target}")


if __name__ == "__main__":
    main()
