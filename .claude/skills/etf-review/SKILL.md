---
name: etf-review
description: ETF 调研（框架 v1.1）：按 framework/etf_framework.md 对 ETF 组合做一期调研，给出每个方向的调仓方向（增配/维持/降配/退出/观察）、建议目标权重、12 个月预期、理由、失效与复评条件，写成 research/etf-<日期>-review.md。只产出研究结论，不给交易指令、金额、点位或时点。Use when asked to run an ETF review, the bi-monthly theme review, the first 8-theme comparison, or for ETF rebalancing direction and expectations.
---

# etf review

## 输入

- `AS_OF_DATE`：缺省当天（北京时间）。
- `MODE`：`full`（8 主题全量比较 + 固定仓）、`light`（只更新已持有与被触发的主题）、`quarterly`（组合层面检查）。缺省按月份：5、9、11 月 `full`，1、3、7 月 `light`；首期一律 `full`。
- `HOLDINGS`（可缺）：用户给的各基金当前市值。给了才写组合现状与固定仓方向；没给就只出主题结论，组合部分写"持仓未提供"。不要沿用旧数当现状。
- 自行读取：`framework/etf_framework.md`（全文）、`research/` 下日期最近的 `etf-*-data-snapshot.txt`、上一期 `research/etf-*-review.md`（有的话）、
  个股轨道最新的 `research/investment-*-market-research.md`（只取当期事实，不重做宏观调研）；首期另读 `research/etf-cards/v1-archive/` 的 v0.1 卡作论点输入。

## 步骤

1. **先决检查**：快照末行有「快照完成」且距 `AS_OF_DATE` 不超过 10 天，否则停下请用户本地重跑
   `/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --pool-csv /Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv`。
   快照 §0 缺口里与本期有关的项照录、标 `[需人工补充]`。没有登记主指数的主题（半导体、电网设备）先提议登记（要实测行情代码），本期结论写"数据不足，0%"。
2. **组合现状**（有持仓时）：按框架 §1 算各方向当前权重（港币按快照 §7 中间价），对照目标与区间，给出固定仓方向（§4）、主题合计、港股合计、同簇敞口。
3. **主题六问**（框架 §3.3–§3.5）：逐席回答；当期事实联网核实并给出处，区分已披露事实、第三方预测、自己的假设。估值只引快照 §4；
   12 个月三情景用 `python3 -c "from scripts.etf_calc import scenario_annual_return as f; print(f(...))"` 计算，`years=1`，基准情景估值零变化，期末倍数只取快照分位点。
4. **方向与目标**（框架 §4）：三条件筛选，不打分；单主题 0/5/10（例外 15，写明理由），合计 ≤ 30%；每席写上次目标 → 建议目标；常规评审最多变动一个主题（首期、逻辑证伪、超限除外）。
5. **压力**：按建议目标用 `etf_calc.joint_stress_loss` 算方案与历史两套情景，与调整前对比。
6. **写报告** `research/etf-<AS_OF_DATE>-review.md`，结构严格按框架 §8。报告里每个数字都要能在快照或计算器输出里找到。

## 不做的事

不写买卖金额、交易清单、下单时点、指数点位锚点、分批计划，不维护持仓或净值文件——这些是用户的交易决策。不提交、不开 PR，由用户或 `etf-monthly-review` 决定。

## 输出

报告文件，以及给用户的一段摘要：每个方向一句话（方向、上次 → 建议目标、基准预期、关键理由），主题目标合计与待配现金，两套压力的变化。
