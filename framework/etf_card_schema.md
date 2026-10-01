# ETF 决策卡 schema v2

> 两仓唯一接口。investment_research_methods（研究侧）写卡，ai_investment（执行侧）读卡，互不 import。
> **规范实现 = `scripts/validate_etf_card.py`**（标准库，`SCHEMA_VERSION = 2`）；本文件是它的说明书，文末示例由单测
> `tests/test_validate_etf_card.py` 对着已提交的快照校验，文档与校验器不会各说各话。
> schema 是封闭的：出现未声明的字段即拒收。任何增删改字段、枚举或规则都升 `card_schema_version`，并在本文件「变更记录」登记。
> v2 对应框架 v1.0（70% 规则配置 + 30% 主题预算）：卡给的是**目标权重与两类动作**，不再给指数点位锚点。

## 1. 文件约定

- 路径与命名：`research/etf-cards/<card_id>-<as_of_date>.md`，例 `research/etf-cards/theme-innovative-drug-2026-11-06.md`。
- `card_id` 是跨版本稳定的身份（小写 slug，不含日期）。约定：核心卡 `core-<席位>`（与 `sizing.bet_group` 相同），主题卡 `theme-<席位>`。
  同一张卡更新 = 新日期的新文件，旧文件留作历史，新文件的 `supersedes` 指向旧文件相对路径。
  现行卡 = 同一 `card_id` 下 `as_of_date` 最大的一份；`as_of_date` 不得晚于当天（未来日期会永久压住此后所有版本）。
- 每个文件**恰好一个** ```` ```json ```` 围栏块；正文其余部分是给人看的论证，执行侧不解析。重复键、`NaN`/`Infinity` 拒收。
- schema v1 的卡（带点位锚点）已归档到 `research/etf-cards/v1-archive/`，校验器只扫 `research/etf-cards/` 这一层，不再校验它们。
- 卡的过期时点只认 `exit.latest_review_date`：主题卡写到下一次双月评审，核心卡写到下一次半年复核。
- 校验：`python3 scripts/validate_etf_card.py`（缺省校验 `research/etf-cards/` 下全部卡；给了文件参数也仍以整个目录做跨卡检查），零错误才可提交。跨卡不变量（只看现行卡，`closed` 的卡不占席位也不认领工具）：一个 `bet_group` 只属于一张卡；一只工具至多被一张卡认领；现行主题卡的目标权重合计不超过主题模块的 30%。已提交的 `current.json` 与卡不一致时也报错——改了卡必须重新 `--export`。
- **执行侧只读一个文件：`research/etf-cards/current.json`**，由 `python3 scripts/validate_etf_card.py --export` 在全部卡零错误时生成（先写 `.partial` 再原子替换）并随卡一起提交；结构为
  `{generated_at, card_schema_version, portfolio_params, index_registry, allocation, cards}`：
  - `portfolio_params` 取自 `framework/etf_portfolio_params.json`，另加现算的 `stress_loss_pct`（`plan` / `historical` 两套压力情景下按目标权重的账户损失百分比，`calc:joint_stress_loss`）；
  - `allocation` 是执行侧补缺口用的目标：`targets_pct`（核心席位取参数表，主题取 `active` 主题卡）、`theme_stock_pct`、`theme_cash_pct`（主题模块 30% 减去主题目标合计 = 批准的主题待配现金）、`paused`（`new_money_action = pause` 的席位）；
  - `cards` 是每张现行卡的完整 JSON；`index_registry` 取自 `framework/etf_index_registry.json`。
  执行侧不扫目录、不自行挑现行卡，只读默认分支上的这一份；文件缺失、解析失败、`cards` 为空或 `generated_at` 过旧一律报错，不静默当作"今天没有卡"。

## 2. 通用约定

| 约定 | 内容 |
|---|---|
| 单位 | 比率、权重、分位一律百分数，字段名以 `_pct` 结尾（`5.97` = 5.97%，分位 0–100，跌幅为负数）；人民币金额以 `_cny` 结尾；倍数（PE/PB）与指数点位无后缀。**权重一律是占策略账户总资产的百分比**（框架 A1 的分母） |
| 日期 | ISO `YYYY-MM-DD` |
| 未知与零 | `null` = 未知/不适用；`0` = 已核实为零。不得混用 |
| 数字 | 除四个结构性字段（`card_schema_version`、`thesis.horizon_months`、`trade_rules.min_holding_days`、`scorecard.confidence_pct`）外，**所有数字都写成带来源的数** `{"value": 数字或null, "source": 来源或null, "note": 可选说明}`；裸数字拒收 |
| 来源 | `snapshot§N`（N=0–8，`snapshot_ref` 所指快照的章节）、`calc:<函数名>`（`scripts/etf_calc.py` 的公开函数）、`framework:A<n>`（框架条目）、`user:<ISO日期>`（用户拍板的参数或目标权重）、`ai_estimate` |
| `ai_estimate` | 只允许出现在情景假设上：`scenarios.*.inputs` 的 `eps_growth_pct` / `dividend_yield_pct` / `years` / `drag_pct`，以及 `method=scenario_only` 时的 `annual_return_pct`。权重、金额、估值（含期末倍数）、点位出现即拒收 |
| 快照引用核对 | 来源为 `snapshot§N` 的数，必须与该快照第 N 节里打印的某个数字**完全相等**——照抄，不再另行取整（`12.68` 不能写成 `12.7`）。快照文件不存在或没有「快照完成」行即报错 |
| 计算器复算 | 情景 `inputs` 齐全时用 `scenario_annual_return` 复算 `valuation_change_pct` 与 `annual_return_pct`（容差 0.01）；`sizing.stress_loss_contribution_pct` 用 `joint_stress_loss([(目标权重, 压力跌幅)])` 复算（容差 0.01） |
| 参数核对 | 核心卡的目标权重、模块、席位与压力跌幅必须等于 `framework/etf_portfolio_params.json` 的 `core_seats`；主题卡的席位必须在 `theme_pool` 里，主指数必须是该席位登记的 `index_candidates` 之一，目标权重只能取 `theme_rules.weight_steps_pct`，压力跌幅等于 `theme_rules.stress_plan_pct`，情景窗口等于 `theme_rules.scenario_years` |

慢变量随卡走（估值状态、情景回报、指数结构、目标权重，来自快照与评审）；快变量执行侧自算（持仓市值与权重、缺口分配、指数点位、基金净值、账户单位净值）。
**指数点位的取数口径**：A 股与中证/国证系指数走 tushare `index_daily`；恒生指数 `HSI`、恒生科技 `HKTECH` 走 tushare `index_global`
（`index_daily` 对它们返回 0 行且不报错）；黄金走 `sge_daily` 的 `Au99.99` 收盘。**不得用 ETF 价格代理指数点位**
（02800 约 25 港元对恒指约 24750 点，量级差近千倍且不会报错），执行侧读卡应加量级守卫。

## 3. 字段

顶层（全部必填，可空的标「可空」）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `card_schema_version` | 整数 | 恒为 `2` |
| `card_id` | slug | 稳定身份 |
| `as_of_date` | 日期 | 本版写卡日 |
| `supersedes` | 字符串，可空 | 上一版文件相对路径 |
| `framework` | `{path, version}` | `path` 恒为 `framework/etf_framework.md`；`version` 形如 `v1.0` |
| `snapshot_ref` | 字符串 | `research/etf-YYYY-MM-DD-data-snapshot.txt` |
| `task` | 枚举 | `core`（固定 70%：A500、科创50、恒指、红利低波）/ `theme`（动态 30% 的主题席位） |
| `status` | 枚举 | `active` / `watch` / `no_buy` / `closed`。主题卡：`active` ⇔ 目标权重 > 0；`watch`（研究中）与 `no_buy`（结论 0%）目标为 0。核心卡只能 `active`、`watch`（目标已定、工具待核实或暂不成交）或 `closed`（席位被从参数表移除）——战略权重是规则，不是研究结论，没有 `no_buy` |
| `no_buy_reason` | 枚举，可空 | `thesis` / `price` / `tool` / `portfolio` / `data`；当且仅当 `status=no_buy` 时非空 |
| `close_reason` | 枚举，可空 | `thesis_realized` / `thesis_invalidated` / `budget` / `tool` / `expired`；当且仅当 `status=closed` 时非空 |

`exposure`：

| 字段 | 说明 |
|---|---|
| `index_code` / `index_name` | 跟踪指数。`index_code` 只能取 `framework/etf_index_registry.json` 里登记的 key。清单里 `source` 为空的指数（无行情源，例：恒生港股通红利低波动 `HSHYLV`）可以作为持仓口径，但卡上不得有 `auto` 监控、`entry_ref_index_level` 必须为空；`valuation_state.index_code` 与基准成分必须是有行情源的指数 |
| `asset_type` | `broad_equity` / `dividend_value` / `growth_theme` / `sector` / `cyclical` / `bond` / `gold_commodity` / `cross_border_equity`，决定估值方法 |
| `currency` | 指数计价币种，ISO 4217；登记清单里有币种时必须一致 |
| `view_mismatch_note` | 观点-持仓错位说明（"买到什么"），可为空串 |
| `structure` | `weights_as_of`（日期，可空）、`constituent_count`、`max_constituent_weight_pct`、`top10_weight_pct`、`research_coverage_pct`（带来源的数）、`top_constituents`（`[{code, name, weight_pct}]`，`code` 为 `6 位.(SZ|SH|BJ)` 或 `5 位.HK`；其他市场的成分不在范围内，留空数组；无源时为空数组） |

`thesis`：

| 字段 | 说明 |
|---|---|
| `statement` | 1 句主判断（"为什么能赚钱"） |
| `evidence` / `counter_evidence` | 恰好 3 条 / 恰好 2 条 |
| `horizon_months` | 整数；主题卡 ≥ 1 |
| `key_variables` | 文字数组：下次评审要验证的变量。`active`/`watch` 主题卡 2–3 条；核心卡可为空数组 |
| `why_now` | 相比上次新增了什么证据、预计何时兑现。`active`/`watch` 主题卡必填；其余可空 |

`expectation`：

| 字段 | 说明 |
|---|---|
| `method` | `return_decomposition` / `reverse_valuation` / `mid_cycle` / `ytm_duration` / `scenario_only` |
| `scenarios.bear/base/bull` | 每个含 `inputs`（可空；非空则六项齐全：`eps_growth_pct`、`dividend_yield_pct`、`current_multiple`、`terminal_multiple`、`years`、`drag_pct`）、`valuation_change_pct`、`annual_return_pct`。**基准情景估值零变化**：前三种方法要求 `base.valuation_change_pct.value == 0`，后两种为 `0` 或 `null`。三个年化回报齐全时须 bear ≤ base ≤ bull。**主题卡的 `years` 恒为 `theme_rules.scenario_years`（1 年）**，让各主题在同一窗口里比较 |
| `valuation_state` | `index_code`（估值取自哪个指数，可以是代理指数，须在登记清单内且有行情源）、`metric`（`erp_spread` / `pe_ttm` / `pb`）、`value`、`percentile_expanding`、`percentile_10y`、`sample_n`、`as_of`。无估值源时 `index_code`/`metric`/`value`/`as_of` 同时为 `null` |

`instruments`：`merge_note`（同一席位多只基金是否合并及理由，可为空串）+ `list`，每项：

| 字段 | 说明 |
|---|---|
| `code` / `name` | 带后缀的 ts_code：内地基金 `6 位.(OF|SZ|SH)`，港股 ETF `5 位.HK`，裸码拒收。内地基金取 `fund_basic` 返回的 `ts_code` 与全名，不按前缀推断交易所 |
| `instrument_type` | `otc_fund` / `exchange_etf` |
| `share_class` | `A` / `C` / `E` / … ，可空 |
| `platform_account` | `支付宝` / `盈立证券` / … |
| `currency` | 该工具**自身**的计价币种（场外基金 `CNY`，`02800.HK` 为 `HKD`）。持仓市值折人民币用它 |
| `role` | `primary`（至多一个；`active`/`watch` 卡恰好一个）/ `backup` / `held_other`（已持有、属于同一席位的其他工具）/ `rejected`（**未持有**的落选工具） |
| `action` | `hold`（持有）/ `switch_out`（换出到 primary）/ `none`（`rejected` 必为 `none`）。**primary 必须 `hold`：本席位分到的新增资金全部买 primary**；其他已持有工具不接收新增资金 |
| `reason` | 首选、备选、落选或处置的理由 |

**认领规则**：只有 `status ∈ {active, watch, no_buy}` 的现行卡认领持仓，认领范围 = `list` 里 `role ∈ {primary, backup, held_other}` 的全部代码；`closed` 卡不认领。一只工具在全部现行卡里至多被认领一次。不在任何现行卡认领范围内、也不在参数 `out_of_scope_holdings`（黄金）里的 ETF 持仓走「无卡」告警。认领了持仓的卡必须至少带 1 条监控变量。

`trade_rules`：`min_holding_days`（整数，可空）、`purchase_limit_note`（可空）。

`decision`（双月评审行动表的一行；框架 A7、A14）：

| 字段 | 说明 |
|---|---|
| `rule_refs` | 引用的框架条目 |
| `target_weight_pct` | 本席位的目标权重（占策略账户），必填。来源 `user:<日期>`（用户确认的评审结论或战略比例）或 `framework:A<n>`。核心卡必须等于参数表；主题卡只能取 0/5/10/15 |
| `previous_target_weight_pct` | 上一版的目标权重，可空（首版为空）。行动表必须同时给出旧目标与新目标 |
| `new_money_action` | `continue`（参与每月补缺口）/ `pause`（本期不接收新增资金：逻辑待核实、价格或参考净值不可靠、产品异常、回撤复核暂停主题新增等）。只有 `active` 卡可以 `continue` |
| `stock_action` | 存量动作：`none`（不动存量）/ `build`（用迁移或再平衡腾出的资金建仓到目标附近，仅 `active`）/ `reduce`（减到目标，目标须 > 0，仅 `active`）/ `exit`（全部退出，目标须为 0）。`closed` 卡为 `none` |
| `exception_note` | 主题目标超过 10%（即 15%）时必填：估值、把握与下行风险的书面说明；其余为 `null` |
| `trigger_basis` | 触发依据：新证据与估值变化，或"维持不变"的理由 |
| `effective_from` | 生效日，不早于 `as_of_date` |

执行侧语义：`target_weight_pct` × 本月入金后的账户总资产 − 当前持仓 = 缺口；`continue` 的席位按缺口分配新增资金（`calc:dca_gap_allocation`，先留足主题待配现金，缺口超过可用资金时按比例，补足后的余额留现金）。
当月实际留存的主题现金 = `calc:theme_cash_reserve_pct(30, 主题目标合计, 主题持仓占比)`：只把主题股票补到 30%，主题已超配时为 0。`stock_action` 不由执行侧自动下单，进月度交易清单由用户确认。

`sizing`：

| 字段 | 说明 |
|---|---|
| `module` | `broad_core` / `dividend_core` / `theme`；核心卡必须等于参数表里该席位的模块 |
| `bet_group` | 核心卡 = 参数表里该席位的 `bet_group`（如 `core-a500`）；主题卡 = `theme_pool` 的席位 slug（如 `innovative-drug`）。**一席一卡**：A 股、港股创新药共用 `innovative-drug` 一个预算，写在一张卡里 |
| `stress_drawdown_pct` | 方案压力情景下本席位的假设跌幅，必填，等于参数表（核心席位逐个给，主题统一 −50%）。历史情景只在组合层面算 |
| `stress_loss_contribution_pct` | 目标权重 × 压力跌幅 = 本席位对账户压力损失的贡献（占账户百分比），`calc:joint_stress_loss` 复算 |
| `overlap_note` | "对组合有何影响"：与固定仓、其他主题、个股的重叠（引用参数 `risk_overlaps` 的相关系数）。主题卡必填非空；核心卡可为空串 |

`monitor_variables`（`active`/`watch` 卡 3–5 条）与 `exit.invalidation`（`theme` 且 `active`/`watch` 至少 1 条）共用同一种触发器：

| 字段 | 说明 |
|---|---|
| `name` | 变量名 |
| `kind` | `auto`（执行侧每日可算）/ `manual`（月度或评审时人工、AI 复核） |
| `metric` / `operator` / `threshold` | `auto` 三者必填；`manual` 三者为 `null`。`operator` ∈ `<` `<=` `>` `>=` |
| `condition_text` | 人读的条件；`manual` 的条件只写在这里 |
| `data_source` / `current_text` | 来源；当前状态的文字描述（可空） |
| `frequency` | `daily` / `weekly` / `monthly` / `quarterly` / `event` |
| `action` / `action_note` | 监控变量：`alert` / `review` / `reduce` / `close` / `swap_tool`；失效条件只能 `close` / `reduce` / `swap_tool`（卖出三分法）。**监控只产生告警与复核，不产生自动买卖**——框架不设均线、估值分位或点位触发的自动交易 |

`auto` 的 `metric` 只有三个，全部只依赖指数点位：`index_level`、`index_vs_sma200_pct`（最新收盘 ÷ 近 200 个交易日收盘均值 − 1，×100）、`index_vs_sma10m_pct`（最近已完成月月末收盘 ÷ 最近 10 个已完成月月末收盘均值 − 1，×100）。

`exit`：`invalidation`、`latest_review_date`（除 `closed` 外必填，且晚于 `as_of_date`）。

`scorecard`：

| 字段 | 说明 |
|---|---|
| `benchmark` | `{name, components: [{code, weight_pct}]}`：不配这个席位时钱放在哪。**主题卡必须等于参数 `benchmark.theme_replacement_pct`（A500 : 恒指 = 70 : 30）**——主题替代的就是比较基准里的这部分；核心卡在组合层面记分，`components` 可为空数组。非空时权重合计 100，成分须是有行情源的登记指数 |
| `preregistered_at` | 预登记日，不晚于 `as_of_date` |
| `confidence_pct` | 0–100 的裸数字，主观判断 |
| `entry_ref_index_level` | 写卡时 `exposure.index_code` 的点位，来自快照 §6；**只用于事后记分，不得作为任何触发器的输入**；无行情源的指数为空 |

## 4. 变更记录

- v2（2026-10-01）：随框架 v1.0（70% 规则配置 + 30% 主题预算）重做决策形状。删除 `decision.anchors`（三锚点、`reduce_mode`、`valid_until`、锚点快照）与配套的机械刷新脚本——回撤阶梯不再决定投钱时机；删除 `sizing.loss_budget_cny` / `standalone_cap_cny`（逐笔亏损预算上限）与 `exposure.counts_toward_sector_cap` / `china_equity`（行业块与中国权益 90% 上限停用）；工具动作删除 `buy`、`stop_dca`（新增资金只买 primary）。新增 `decision.target_weight_pct` / `previous_target_weight_pct` / `new_money_action` / `stock_action` / `exception_note` / `trigger_basis` / `effective_from`，`sizing.module` / `stress_drawdown_pct` / `stress_loss_contribution_pct` / `overlap_note`，`thesis.key_variables` / `why_now`，`scorecard.benchmark.components`；`task` 改为 `core` / `theme`。无行情源的指数不再强制 `no_buy/data`（权重按基金市值算，只禁止点位类监控与记分点位）。导出新增 `allocation` 与 `portfolio_params.stress_loss_pct`。v1 的 8 张卡归档到 `research/etf-cards/v1-archive/`。
- v1（2026-09-19）：首版，带无状态三锚点（回撤分位阶梯）与逐笔亏损预算上限；修订史见 git 与 v1 归档卡。

## 5. 示例

示意用途的核心卡，数字取自 `research/etf-2026-09-18-data-snapshot.txt` 与参数表，不构成任何买卖结论。

```json
{
  "card_schema_version": 2,
  "card_id": "example-core-a500",
  "as_of_date": "2026-09-19",
  "supersedes": null,
  "framework": {
    "path": "framework/etf_framework.md",
    "version": "v1.0"
  },
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "core",
  "status": "active",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "000510.SH",
    "index_name": "中证A500",
    "asset_type": "broad_equity",
    "currency": "CNY",
    "view_mismatch_note": "",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {
        "value": 500,
        "source": "snapshot§3"
      },
      "max_constituent_weight_pct": {
        "value": 3.2,
        "source": "snapshot§3"
      },
      "top10_weight_pct": {
        "value": 20.25,
        "source": "snapshot§3"
      },
      "research_coverage_pct": {
        "value": 28.5,
        "source": "snapshot§3"
      },
      "top_constituents": [
        {
          "code": "300750.SZ",
          "name": "宁德时代",
          "weight_pct": {
            "value": 3.2,
            "source": "snapshot§3"
          }
        },
        {
          "code": "300308.SZ",
          "name": "中际旭创",
          "weight_pct": {
            "value": 3.16,
            "source": "snapshot§3"
          }
        },
        {
          "code": "600519.SH",
          "name": "贵州茅台",
          "weight_pct": {
            "value": 2.7,
            "source": "snapshot§3"
          }
        }
      ]
    }
  },
  "thesis": {
    "statement": "示例：以当前股债利差持有 A 股宽基，长期回报主要来自盈利增长而非估值修复",
    "evidence": [
      "示例证据一",
      "示例证据二",
      "示例证据三"
    ],
    "counter_evidence": [
      "示例反证一",
      "示例反证二"
    ],
    "horizon_months": 120,
    "key_variables": [],
    "why_now": null
  },
  "expectation": {
    "method": "return_decomposition",
    "scenarios": {
      "bear": {
        "inputs": {
          "eps_growth_pct": {
            "value": 3,
            "source": "ai_estimate"
          },
          "dividend_yield_pct": {
            "value": 2.5,
            "source": "ai_estimate"
          },
          "current_multiple": {
            "value": 15.86,
            "source": "snapshot§4",
            "note": "沪深300 自聚合 PE_TTM（指数权重口径），A500 无估值源以之代理"
          },
          "terminal_multiple": {
            "value": 11.72,
            "source": "snapshot§4",
            "note": "沪深300 自聚合 PE 扩张窗 P10"
          },
          "years": {
            "value": 10,
            "source": "ai_estimate"
          },
          "drag_pct": {
            "value": 0.2,
            "source": "snapshot§5"
          }
        },
        "valuation_change_pct": {
          "value": -2.98,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 2.32,
          "source": "calc:scenario_annual_return"
        }
      },
      "base": {
        "inputs": {
          "eps_growth_pct": {
            "value": 6,
            "source": "ai_estimate"
          },
          "dividend_yield_pct": {
            "value": 2.5,
            "source": "ai_estimate"
          },
          "current_multiple": {
            "value": 15.86,
            "source": "snapshot§4",
            "note": "沪深300 自聚合 PE_TTM（指数权重口径），A500 无估值源以之代理"
          },
          "terminal_multiple": {
            "value": 15.86,
            "source": "snapshot§4"
          },
          "years": {
            "value": 10,
            "source": "ai_estimate"
          },
          "drag_pct": {
            "value": 0.2,
            "source": "snapshot§5"
          }
        },
        "valuation_change_pct": {
          "value": 0.0,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 8.3,
          "source": "calc:scenario_annual_return"
        }
      },
      "bull": {
        "inputs": {
          "eps_growth_pct": {
            "value": 8,
            "source": "ai_estimate"
          },
          "dividend_yield_pct": {
            "value": 2.5,
            "source": "ai_estimate"
          },
          "current_multiple": {
            "value": 15.86,
            "source": "snapshot§4",
            "note": "沪深300 自聚合 PE_TTM（指数权重口径），A500 无估值源以之代理"
          },
          "terminal_multiple": {
            "value": 17.69,
            "source": "snapshot§4",
            "note": "沪深300 自聚合 PE 扩张窗 P75"
          },
          "years": {
            "value": 10,
            "source": "ai_estimate"
          },
          "drag_pct": {
            "value": 0.2,
            "source": "snapshot§5"
          }
        },
        "valuation_change_pct": {
          "value": 1.1,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 11.4,
          "source": "calc:scenario_annual_return"
        }
      }
    },
    "valuation_state": {
      "index_code": "000300.SH",
      "metric": "pe_ttm",
      "value": {
        "value": 15.86,
        "source": "snapshot§4",
        "note": "中证A500 无估值源，以沪深300 自聚合（指数权重口径）为代理"
      },
      "percentile_expanding": {
        "value": 57.9,
        "source": "snapshot§4"
      },
      "percentile_10y": {
        "value": 64.5,
        "source": "snapshot§4"
      },
      "sample_n": {
        "value": 247,
        "source": "snapshot§4"
      },
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "",
    "list": [
      {
        "code": "022448.OF",
        "name": "国泰中证A500ETF联接-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "primary",
        "action": "hold",
        "reason": "示例：A 类无销售服务费；primary 接收新增资金"
      },
      {
        "code": "022449.OF",
        "name": "国泰中证A500ETF联接-C",
        "instrument_type": "otc_fund",
        "share_class": "C",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "示例：未持有的落选工具——长期持有 C 类年费更高"
      }
    ]
  },
  "trade_rules": {
    "min_holding_days": 7,
    "purchase_limit_note": null
  },
  "decision": {
    "rule_refs": [
      "A2",
      "A8",
      "A9"
    ],
    "target_weight_pct": {
      "value": 28,
      "source": "user:2026-09-30",
      "note": "战略配置：A500 占策略账户 28%"
    },
    "previous_target_weight_pct": {
      "value": null,
      "source": null
    },
    "new_money_action": "continue",
    "stock_action": "none",
    "exception_note": null,
    "trigger_basis": "示例：方案 v1.0 的固定配置；固定仓不参与双月轮动，只随半年与年度复核调整",
    "effective_from": "2026-09-19"
  },
  "sizing": {
    "module": "broad_core",
    "bet_group": "core-a500",
    "stress_drawdown_pct": {
      "value": -35,
      "source": "user:2026-09-30",
      "note": "方案设定的压力情景；历史情景 -72% 见组合参数"
    },
    "stress_loss_contribution_pct": {
      "value": 9.8,
      "source": "calc:joint_stress_loss",
      "note": "占策略账户的百分比"
    },
    "overlap_note": ""
  },
  "monitor_variables": [
    {
      "name": "中证A500 编制规则",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "指数公司公告修订编制方案",
      "data_source": "中证指数公司公告",
      "current_text": null,
      "frequency": "event",
      "action": "review",
      "action_note": ""
    },
    {
      "name": "首选工具的跟踪质量与费用",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "近 3 年跟踪差异年化劣于 -0.5 个百分点，或同指数出现明显更便宜的 A 类工具",
      "data_source": "月度快照 §5",
      "current_text": null,
      "frequency": "quarterly",
      "action": "swap_tool",
      "action_note": ""
    },
    {
      "name": "沪深300 估值分位（只作背景，不生成交易）",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "扩张窗分位进入极端区间时在半年复核里讨论长期回报假设",
      "data_source": "月度快照 §4",
      "current_text": null,
      "frequency": "monthly",
      "action": "review",
      "action_note": ""
    }
  ],
  "exit": {
    "invalidation": [],
    "latest_review_date": "2027-03-19"
  },
  "scorecard": {
    "benchmark": {
      "name": "核心席位在组合层面记分：它本身就是比较基准的一部分",
      "components": []
    },
    "preregistered_at": "2026-09-19",
    "confidence_pct": 50,
    "entry_ref_index_level": {
      "value": 5586.09,
      "source": "snapshot§6"
    }
  }
}
```
