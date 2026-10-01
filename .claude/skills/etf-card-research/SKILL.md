---
name: etf-card-research
description: ETF 决策卡研究（框架 v1.0，卡 schema v2）：对一个核心席位或主题席位，读最新数据快照、ETF 研究框架与组合参数，按八节模板写一张决策卡（research/etf-cards/<card_id>-<日期>.md，含唯一 JSON 块），给出目标权重、新增资金动作与存量动作，过校验器后导出执行侧读取的 current.json。数字只许引自快照或 etf_calc，目标权重由用户确认。Use when asked to write, refresh or review an ETF decision card, the four core seat cards, or a theme card during a theme review.
---

# etf card research

## 输入

- `SEAT`：核心席位（`core-a500` / `core-star50` / `core-hsi` / `core-hk-dividend-lowvol`）或主题席位（`framework/etf_portfolio_params.json` 的 `theme_pool` key，如 `innovative-drug`）。可一次给多个，逐张处理。
- `AS_OF_DATE`：写卡日，缺省当天（北京时间）。
- `HOLDINGS`：该席位下用户现持有的工具及人民币市值（用户给；没给就问，不要猜）。
- `TARGET`（主题卡）：本次评审的目标权重与两类动作。通常由 `etf-theme-review` 的行动表给出并经用户确认；单独调用时没有用户确认的目标，就只写 `watch`（目标 0）。
- 自行读取：`framework/etf_framework.md`（全文）、`framework/etf_card_schema.md`、`framework/etf_portfolio_params.json`、`framework/etf_index_registry.json`、
  `research/` 下日期最近的 `etf-*-data-snapshot.txt`、该席位上一版卡（`research/etf-cards/<card_id>-*.md` 里日期最近的一份）；首版主题卡另读 `research/etf-cards/v1-archive/` 里对应的 v0.1 卡作论点输入（数据按当期快照重核）。

## 先决检查（任一不过就停下来告诉用户，不写卡）

1. 快照末行有「快照完成」，且快照日期距 `AS_OF_DATE` 不超过 10 天。过期 → 请用户先跑
   `/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --pool-csv /Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv`。
2. 快照 §0 缺口清单里与本席位相关的每一条，都要在卡正文里照录并标 `[需人工补充]`。
3. 主指数在登记清单里；主题卡的主指数还必须在该席位的 `index_candidates` 里（校验器强制）。半导体、电网设备等尚无登记主指数的席位 → 先提议登记（实测行情与全收益代码，改登记清单与 `theme_pool`），不要在卡里写未登记的代码。

## 写卡步骤

1. **定主指数与 `card_id`**：核心卡 `card_id` = `sizing.bet_group` = 参数表里的席位名（如 `core-a500`）；主题卡 `card_id` = `theme-<席位>`，`bet_group` = 席位 key。同一席位多个指数按框架 A6 四问比选，只留一个主指数。
2. **核心判断**（A5、A6）：1 句主判断 + 3 条证据 + 2 条反证；主题卡另写 `why_now`（相比上次新增了什么证据、预计何时兑现）与 2–3 个 `key_variables`。需要当期事实时联网核实并在正文给出处，区分已披露事实、第三方预测、自己的假设。
3. **指数匹配与估值**（A6）：结构读数取快照 §3；估值状态与情景倍数只取快照 §4 自聚合（亏损股权重 >15% 的看 PB）；三情景用 `scenario_annual_return`，期末倍数只取快照分位点，基准情景估值零变化。
   **主题卡 `years` = 1（12 个月窗口，校验器强制）**；核心卡用与持有期相称的年数。盈利增长、股息率、年数标 `ai_estimate`。
4. **工具比选**（A11）：首选、备选、落选取自快照 §5（费率、A/C 份额、TD/TE）。首选 `role=primary`、`action=hold`（本席位的新增资金只买它）；用户已持有的同席位其他基金写 `held_other` + `hold` 或 `switch_out`；`rejected` 只用于未持有的落选工具。红利低波须比较港股通渠道与直持港股 ETF 的股息税差。
5. **目标与动作**（A2、A7）：
   - 核心卡：`target_weight_pct` 照抄参数表（来源 `user:2026-09-30`），`status` 用 `active`（工具待核实或暂不成交时 `watch` + `new_money_action=pause`），`exception_note` 为 null。
   - 主题卡：`target_weight_pct` 只能 0/5/10/15，来源 `user:<确认日>`；`previous_target_weight_pct` 抄上一版（首版 null）；`active` ⇔ 目标 > 0；15% 必须写 `exception_note`。
   - `new_money_action`：`continue` / `pause`（逻辑待核实、价格或参考净值不可靠、产品异常、回撤复核暂停主题新增）；`stock_action`：`none` / `build` / `reduce` / `exit`（退出时目标为 0、状态 `no_buy`）。
   - `sizing.stress_drawdown_pct` 照抄参数表（核心逐席位，主题 −50），`stress_loss_contribution_pct` 用脚本算：
     `python3 -c "from scripts.etf_calc import joint_stress_loss as f; print(f([(<目标>, <压力跌幅>)])['loss'])"`；
     主题卡的 `overlap_note` 写与固定仓、其他主题、个股的重叠（引用参数 `risk_overlaps`；恒生科技之于恒指、半导体之于科创50 要写合并后的簇权重）。
6. **监控与退出**（A12、A13）：3–5 个监控变量，自动类只能用三个指数点位指标且只告警或复核；无行情源的指数（`HSHYLV`）不得有自动监控、`entry_ref_index_level` 为空。
   主题卡至少一条失效条件，`latest_review_date` 写到下一次双月评审；核心卡写到下一次半年复核。记分基准：主题卡 `components` = A500 70 / 恒指 30（参数 `benchmark.theme_replacement_pct`，来源 `user:2026-09-30`）；核心卡 `components` 为空数组。
7. **正文八节**按框架 Part B；末尾放唯一的 ```json 块。正文里出现的每个数字也必须能在快照或计算器里找到。

## 校验与导出

```
python3 scripts/validate_etf_card.py research/etf-cards/<本次写的卡>.md   # 零错误才算完成；报错就改卡，不改校验器
python3 scripts/validate_etf_card.py --export                             # 全部卡零错误后更新 research/etf-cards/current.json
```

常见报错：引用快照的数与打印值不完全相等（照抄，不另行取整）；核心卡目标、模块、席位或压力跌幅与参数表不一致；主题目标不是 0/5/10/15 或 15 没写例外说明；
主指数不在该席位的 `index_candidates`；主题情景 `years` 不是 1；主题目标合计超过 30%；同一只基金被两张卡认领；`as_of_date` 晚于今天。

## 输出与交接

- 每张卡一句话结论（目标权重旧 → 新、新增资金动作、存量动作及理由、现持仓怎么处置）汇总给用户审阅。
- 不提交、不开 PR——由调用方（用户、`etf-theme-review` 或月度编排器）决定。`current.json` 只有合并进 main 后执行侧才会读到。
- 卡的 schema 有任何疑问以 `scripts/validate_etf_card.py` 为准；需要改 schema 时必须同步通知 ai_investment 侧会话。
