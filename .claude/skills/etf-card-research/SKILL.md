---
name: etf-card-research
description: ETF 决策卡研究：对候选池里的一个席位，读最新数据快照与 ETF 研究框架，按八节模板写一张决策卡（research/etf-cards/<card_id>-<日期>.md，含唯一 JSON 块），过校验器后导出执行侧读取的 current.json。数字只许引自快照或 etf_calc，不由 AI 估。Use when asked to write, refresh or review an ETF decision card, or to produce the first batch of cards for the ETF candidate pool.
---

# etf card research

## 输入

- `SEAT`：席位名（框架 A1 的 15 席之一）。可一次给多个席位，逐张处理。
- `AS_OF_DATE`：写卡日，缺省当天（北京时间）。
- `HOLDINGS`：该席位下用户现持有的工具及人民币金额（用户给；没给就问，不要猜）。用来判断是否超上限、定投是否继续。
- 自行读取：`framework/etf_framework.md`（全文）、`framework/etf_card_schema.md`、`framework/etf_portfolio_params.json`、
  `framework/etf_index_registry.json`、`research/` 下日期最近的 `etf-*-data-snapshot.txt`、`research/etf-2026-09-18-rule-validation.md`、
  该席位上一版卡（`research/etf-cards/<card_id>-*.md` 里日期最近的一份，没有就是首版）。

## 先决检查（任一不过就停下来告诉用户，不写卡）

1. 快照末行有「快照完成」，且快照日期距 `AS_OF_DATE` 不超过 10 天。过期 → 请用户先跑
   `/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --pool-csv /Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv`。
2. 快照 §0 缺口清单里与本席位相关的每一条，都要在卡正文里照录并标 `[需人工补充]`。
3. 席位的主指数在登记清单里。不在 → 先提议登记（需实测行情代码），不要在卡里写未登记的代码。

## 写卡步骤

1. **定主指数与 `card_id`**。同簇多个指数（例：医药席位的四个指数）按框架 A4 四问比选，只留一个挂点位；`card_id` 小写 slug、不含日期，
   例 `cn-hk-pharma-tactical`；`sizing.bet_group` 与 `card_id` 一一对应。
2. **核心判断**（A3）：1 句主判断 + 3 条证据 + 2 条反证。需要当期事实时用联网搜索核实并在正文给出处；成分已在个股研究池内的，先读现成研究。
3. **指数匹配与估值**（A4、A5）：结构读数取快照 §3；估值状态与情景倍数只取快照 §4 自聚合（指数权重口径；亏损股权重 >15% 的看 PB）——§1 的乐咕月频当月行会随运行日消失，引用它的卡下次校验会失效；
   三情景用 `scenario_annual_return`，期末倍数只取快照分位点，基准情景估值零变化；盈利增长与年数是假设，标 `ai_estimate`。
4. **工具比选**（A6）：首选、备选、落选取自快照 §5（费率、TD/TE、同基金其他份额）。用户已持有的同一笔押注下的其他基金写
   `held_other` 并给处置（`hold` / `stop_dca` / `switch_out`）；`rejected` 只用于未持有的落选工具。
5. **点位**（A9）：只有一种合法推导——快照 §6b 的 `36月高点` 与 `P10状态` / `P25状态` / `P75状态`，经
   `calc:level_at_drawdown_state` 得 `add_below` / `buy_below` / `reduce_above`，目标比例 100 / 50 / 30（来源 `framework:A13`）。
   用脚本算，不要心算：`python3 -c "from scripts.etf_calc import level_at_drawdown_state as f; print(round(f(<高点>, <状态>), 2))"`。
   `inputs` 里照抄快照的两个数，校验器会复算。黄金、无行情源的指数、§6b 给不出分位点的指数：三锚点全空 + `no_anchor_reason`。
   同时在正文写明该席位在验证报告里的逐折结果与空仓期的机会成本（A9「必须一并交代的代价」）。
6. **仓位**（A8）：核心席位的 `sizing` 三个数照抄 `etf_portfolio_params.json` 的 `core_seats`；行业席位为 3.5 万 / −70% / 5 万（`calc:loss_budget_cap`）。
   现持仓超上限 → 所有工具 `stop_dca`，不给 `buy`；`status` 用 `watch` 或 `no_buy(portfolio)`。
7. **监控与退出**（A10–A12）：3–5 个监控变量，自动类只能用三个指数点位指标；战术卡至少一条失效条件；`latest_review_date` 核心卡写一个季度后、战术卡不超过两个月；
   记分基准 `H11025.CSI` 或核心宽基；`entry_ref_index_level` 取快照 §6 的收盘。
8. **正文八节**按框架 Part B；末尾放唯一的 ```json 块。正文里出现的每个数字也必须能在快照里找到。

## 校验与导出

```
python3 scripts/validate_etf_card.py research/etf-cards/<本次写的卡>.md   # 零错误才算完成；报错就改卡，不改校验器
python3 scripts/validate_etf_card.py --export                             # 全部卡零错误后更新 research/etf-cards/current.json
```

校验不过时常见原因：引用快照的数与打印值不完全相等（照抄，不另行取整）；点位没用计算器算；`sizing` 与核心席位表不一致；
同一只基金被两张卡认领；`as_of_date` 晚于今天。

## 输出与交接

- 每张卡一句话结论（买 / 观察 / 不买及原因、三个点位、定投是否继续、现持仓怎么处置）汇总给用户审阅。
- 不提交、不开 PR——由调用方（用户或月度编排器）决定。`current.json` 只有合并进 main 后执行侧才会读到。
- 卡的 schema 有任何疑问以 `scripts/validate_etf_card.py` 为准；需要改 schema 时必须同步通知 ai_investment 侧会话。
