# ETF 决策卡 schema v1

> 两仓唯一接口。investment_research_methods（研究侧）写卡，ai_investment（执行侧）读卡，互不 import。
> **规范实现 = `scripts/validate_etf_card.py`**（标准库，`SCHEMA_VERSION = 1`）；本文件是它的说明书，文末示例由单测
> `tests/test_validate_etf_card.py` 对着已提交的快照校验，文档与校验器不会各说各话。
> schema 是封闭的：出现未声明的字段即拒收。任何增删改字段、枚举或规则都升 `card_schema_version`，并在本文件「变更记录」登记。

## 1. 文件约定

- 路径与命名：`research/etf-cards/<card_id>-<as_of_date>.md`，例 `research/etf-cards/cn-hk-pharma-tactical-2026-09-19.md`。
- `card_id` 是跨版本稳定的身份（小写 slug，不含日期）；同一张卡更新 = 新日期的新文件，旧文件留作历史，新文件的 `supersedes` 指向旧文件相对路径。
  **执行侧按 `card_id` 分组、取 `as_of_date` 最大的一份为现行卡。**
- 每个文件**恰好一个** ```` ```json ```` 围栏块；正文其余部分是给人看的论证，执行侧不解析。重复键、`NaN`/`Infinity` 拒收。
- 新鲜度由执行侧判断：`as_of_date` 起 30 天提醒、45 天过期；超过 `exit.latest_review_date` 视为待复评。校验器只查结构，不查新鲜度。
- 校验：`python3 scripts/validate_etf_card.py research/etf-cards/*.md`，零错误才可提交。

## 2. 通用约定

| 约定 | 内容 |
|---|---|
| 单位 | 比率、权重、分位一律百分数，字段名以 `_pct` 结尾（`5.97` = 5.97%，分位 0–100，回撤为负数）；人民币金额以 `_cny` 结尾；倍数（PE/PB）与指数点位无后缀 |
| 日期 | ISO `YYYY-MM-DD` |
| 未知与零 | `null` = 未知/不适用；`0` = 已核实为零。不得混用 |
| 数字 | 除四个结构性字段（`card_schema_version`、`thesis.horizon_months`、`trade_rules.min_holding_days`、`scorecard.confidence_pct`）外，**所有数字都写成带来源的数** `{"value": 数字或null, "source": 来源或null, "note": 可选说明}`；裸数字拒收 |
| 来源 | `snapshot§N`（N=0–8，`snapshot_ref` 所指快照的章节）、`calc:<函数名>`（`scripts/etf_calc.py` 的公开函数）、`framework:A<n>`（框架参数总表条目）、`user:<ISO日期>`（用户拍板的参数）、`ai_estimate` |
| `ai_estimate` | 只允许出现在情景假设上：`scenarios.*.inputs` 的 `eps_growth_pct` / `dividend_yield_pct` / `years` / `drag_pct`，以及 `method=scenario_only` 时的 `annual_return_pct`。点位、权重、金额、估值（含期末倍数）出现即拒收 |
| 快照引用核对 | 来源为 `snapshot§N` 的数，必须与该快照第 N 节里打印的某个数字**完全相等**——照抄，不再另行取整（`12.68` 不能写成 `12.7`）。快照文件不存在或没有「快照完成」行即报错 |
| 计算器复算 | `sizing.standalone_cap_cny` 用 `loss_budget_cap(loss_budget_cny, stress_drawdown_pct)` 复算（容差 1 元）；情景 `inputs` 齐全时用 `scenario_annual_return` 复算 `valuation_change_pct` 与 `annual_return_pct`（容差 0.01）；锚点 `inputs` 齐全时用其 `level.source` 所指函数复算点位 |

慢变量随卡走（估值状态、情景回报、指数结构，月频，来自快照）；快变量执行侧每日自算（指数点位、基金净值、趋势、持仓权重）。
买卖条件只挂指数点位：`decision.anchors.basis` 恒为 `index_level`。
**指数点位的取数口径**：A 股与中证/国证系指数走 tushare `index_daily`；恒生指数 `HSI`、恒生科技 `HKTECH` 走 tushare `index_global`
（`index_daily` 对它们返回 0 行且不报错）；黄金走 `sge_daily` 的 `Au99.99` 收盘。**不得用 ETF 价格代理指数点位**
（02800 约 25 港元对恒指约 24750 点，量级差近千倍且不会报错），执行侧读卡应加量级守卫。

## 3. 字段

顶层（全部必填，可空的标「可空」）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `card_schema_version` | 整数 | 恒为 `1` |
| `card_id` | slug | 稳定身份 |
| `as_of_date` | 日期 | 本版写卡日 |
| `supersedes` | 字符串，可空 | 上一版文件相对路径 |
| `framework` | `{path, version}` | `path` 恒为 `framework/etf_framework.md`；`version` 形如 `v0.1` |
| `snapshot_ref` | 字符串 | `research/etf-YYYY-MM-DD-data-snapshot.txt` |
| `task` | 枚举 | `core` / `tactical` / `defensive` |
| `status` | 枚举 | `active` / `watch` / `no_buy` / `closed` |
| `no_buy_reason` | 枚举，可空 | `thesis` / `price` / `tool` / `portfolio` / `data`；当且仅当 `status=no_buy` 时非空 |
| `close_reason` | 枚举，可空 | `thesis_realized` / `thesis_invalidated` / `budget` / `tool` / `expired`；当且仅当 `status=closed` 时非空 |

`exposure`：

| 字段 | 说明 |
|---|---|
| `index_code` / `index_name` | 跟踪指数（tushare 代码） |
| `asset_type` | `broad_equity` / `dividend_value` / `growth_theme` / `sector` / `cyclical` / `bond` / `gold_commodity` / `cross_border_equity`，决定估值方法 |
| `currency` | 指数计价币种，ISO 4217 |
| `counts_toward_sector_cap` | 布尔。是否占「行业合计」额度（用户裁定：恒生科技=否，科创50=是） |
| `china_equity` | 布尔。是否计入「中国权益」上限 |
| `view_mismatch_note` | 观点-持仓错位说明，可为空串 |
| `structure` | `weights_as_of`（日期，可空）、`constituent_count`、`max_constituent_weight_pct`、`top10_weight_pct`、`research_coverage_pct`（带来源的数）、`top_constituents`（`[{code, name, weight_pct}]`，无源时为空数组；执行侧做穿透时未披露部分记为未解析，不摊到已知成分上） |

`thesis`：`statement`（1 句主判断）、`evidence`（恰好 3 条）、`counter_evidence`（恰好 2 条）、`horizon_months`（整数；`tactical` ≥1）。

`expectation`：

| 字段 | 说明 |
|---|---|
| `method` | `return_decomposition` / `reverse_valuation` / `mid_cycle` / `ytm_duration` / `scenario_only` |
| `scenarios.bear/base/bull` | 每个含 `inputs`（可空；非空则六项齐全：`eps_growth_pct`、`dividend_yield_pct`、`current_multiple`、`terminal_multiple`、`years`、`drag_pct`）、`valuation_change_pct`、`annual_return_pct`。**基准情景估值零变化**：前三种方法要求 `base.valuation_change_pct.value == 0`，后两种为 `0` 或 `null`。三个年化回报齐全时须 bear ≤ base ≤ bull |
| `valuation_state` | `index_code`（估值取自哪个指数，可以是代理指数）、`metric`（`erp_spread` / `pe_ttm` / `pb`）、`value`、`percentile_expanding`、`percentile_10y`、`sample_n`、`as_of`。无估值源时 `index_code`/`metric`/`value`/`as_of` 同时为 `null` |

`instruments`：`merge_note`（同一观点多只基金是否合并及理由，可为空串）+ `list`，每项：

| 字段 | 说明 |
|---|---|
| `code` / `name` | `fund_basic` 返回的 `ts_code` 与全名（不按前缀推断交易所）；港股 ETF 用 `02800.HK` |
| `instrument_type` | `otc_fund` / `exchange_etf` |
| `share_class` | `A` / `C` / `E` / … ，可空 |
| `platform_account` | `支付宝` / `盈立证券` / … |
| `role` | `primary`（至多一个；`active`/`watch` 卡恰好一个）/ `backup` / `held_other`（已持有、属于同一笔押注的其他工具）/ `rejected` |
| `action` | `buy`（仅 `status=active`）/ `hold` / `stop_dca` / `switch_out` / `none`（`rejected` 必为 `none`） |
| `reason` | 首选、备选、落选或处置的理由 |

**执行侧据 `list` 里 `role != rejected` 的全部代码认领持仓；不在任何现行卡里的 ETF 持仓走「无卡」告警。**

`trade_rules`：`min_holding_days`（整数，可空）、`purchase_limit_note`（可空）、`max_premium_pct`、`sell_if_premium_above_pct`。首选工具是 `otc_fund` 时两个溢价字段的 `value` 必须为 `null`（场外按净值申赎）。

`decision`（候选池里每只 ETF 的买卖点位判断；形状对齐执行侧个股的"加仓价 / 首次买入价 / 卖出价"三锚点）：

| 字段 | 说明 |
|---|---|
| `rule_refs` | 引用的框架规则编号 |
| `dca_action` | `continue` / `pause`。用户默认保留小额定投，卡判断需要停时写 `pause` |
| `anchors.basis` / `index_code` | 恒为 `index_level`；`index_code` 须等于 `exposure.index_code` |
| `anchors.add_below` / `buy_below` / `reduce_above` | 三个锚点，各含 `level`、`target_ratio_pct`、`inputs`、`rationale`（见下） |
| `anchors.reduce_mode` | `to_target_ratio`（减到 `reduce_above.target_ratio_pct`）/ `exit_all`（清仓，此时该比例必须为 0）。显式枚举，不靠文字 |
| `anchors.no_anchor_reason` | 三个锚点全为空时必填（例：无估值源且无可用推导方法），否则为 `null` |
| `anchors.valid_until` | 点位有效期；有锚点时必填 |

锚点字段：

| 字段 | 说明 |
|---|---|
| `level` | 指数点位。**来源必须是 `calc:<函数名>`，这就是点位的推导方法**（估值分位换算、回撤分位、趋势带……各有其函数）；方法日后被证伪时按函数名批量召回 |
| `target_ratio_pct` | 指数到达该锚点时，这笔押注（同 `bet_group`）应有的仓位，占 `sizing.standalone_cap_cny` 的百分比。**卡里只写比例不写金额**，金额由执行侧按当期上限换算 |
| `inputs` | 推导函数的入参（键 = `etf_calc` 函数的参数名，值为带来源的数），可空。齐全时校验器用该函数复算 `level`（容差 0.01 或万分之一） |
| `rationale` | 为什么取这个锚 |

锚点是**无状态**的：执行侧只拿当日指数点位 `L` 与三个点位比较，不需要成交历史。**买入区只买不卖，减仓区只卖不买**——

| 位置 | 目标仓位（占单笔上限） | 动作 |
|---|---|---|
| `L ≤ add_below` | `add_below.target_ratio_pct` | 现持仓低于目标 → 买到目标；高于目标 → **不动** |
| `add_below < L ≤ buy_below` | `buy_below.target_ratio_pct` | 同上（从更低一档回升到这一档时，多出来的仓位不卖） |
| `buy_below < L < reduce_above` | — | **不产生任何买卖指令**，保持现状；定投按 `dca_action` |
| `L ≥ reduce_above` | `reduce_above.target_ratio_pct` | 现持仓高于目标 → 减到目标（`exit_all` 即清仓）；低于目标 → 不动 |

单向的理由：点位在某一档边界附近来回时，双向调整会在买入区制造往返交易，而场外基金持有不满 7 天赎回要付 1.5%。
语义因此是"越跌买得越多的棘轮，贵了才减"。持仓口径 = 该卡 `instruments.list` 里 `role != rejected` 的全部工具的人民币市值合计。

校验器钉死：三个锚点要么齐全要么全空；`add_below.level < buy_below.level < reduce_above.level` 严格成立；
比例满足 `add_below ≥ buy_below > reduce_above`。**`add_below` 是加仓位，不是止损位**——执行侧不得继承个股机器里"加仓价兼作止损距离"的耦合；
宽基不设价格止损，退出走 `exit.invalidation`。

`sizing`：`bet_group`（slug）、`stress_drawdown_pct`（负数）、`loss_budget_cny`、`standalone_cap_cny`。
**一笔押注 = 一张卡**：`bet_group` 与 `card_id` 一一对应，一个 `bet_group` 只有一个上限、一套锚点。穿透后属于同一笔押注的多只基金
（例：四只医药基金）合写成一张卡，锚点挂在主指数上，其余基金列进 `instruments.list`（`held_other` + 处置动作）。
校验器批量校验时，同一 `bet_group` 出现在两个不同 `card_id` 下即报错。行业合计上限、中国权益上限这类组合级参数不进卡，由框架参数总表给出、执行侧统一检查。

`monitor_variables`（`active`/`watch` 卡 3–5 条）与 `exit.invalidation`（`tactical` 且 `active`/`watch` 至少 1 条）共用同一种触发器：

| 字段 | 说明 |
|---|---|
| `name` | 变量名 |
| `kind` | `auto`（执行侧每日可算）/ `manual`（月度人工或 AI 复核） |
| `metric` / `operator` / `threshold` | `auto` 三者必填；`manual` 三者为 `null`。`operator` ∈ `<` `<=` `>` `>=` |
| `condition_text` | 人读的条件；`manual` 的条件只写在这里 |
| `data_source` / `current_text` | 来源；当前状态的文字描述（可空） |
| `frequency` | `daily` / `weekly` / `monthly` / `quarterly` / `event` |
| `action` / `action_note` | 监控变量：`alert` / `review` / `pause_dca` / `reduce` / `close` / `swap_tool`；失效条件只能 `close` / `reduce` / `swap_tool`（对应卖出三分法） |

`auto` 的 `metric` 定义（执行侧实现）：

| metric | 定义 |
|---|---|
| `index_level` | `exposure.index_code` 最新日收盘点位 |
| `index_vs_sma200_pct` | (最新收盘 ÷ 近 200 个交易日收盘均值 − 1) × 100 |
| `index_vs_sma10m_pct` | (最近已完成月月末收盘 ÷ 最近 10 个已完成月月末收盘均值 − 1) × 100；当月未完成不参与，月末评估 |
| `index_drawdown_from_ref_pct` | (最新收盘 ÷ `scorecard.entry_ref_index_level` − 1) × 100 |
| `instrument_premium_pct` | 首选工具收盘价 ÷ 当日收盘净值 − 1，× 100；仅 `exchange_etf` |
| `bet_group_value_cny` | 同 `bet_group` 全部认领持仓的人民币市值合计 |
| `bet_group_weight_pct` | 上者 ÷ 全部资产（个股 + ETF）× 100 |

`exit`：`invalidation`、`latest_review_date`（除 `closed` 外必填，且晚于 `as_of_date`）。

`scorecard`：`benchmark`（不买它时这笔钱放哪，即记分基准）、`preregistered_at`（不晚于 `as_of_date`）、`confidence_pct`（0–100 的裸数字，主观判断）、`entry_ref_index_level`（写卡时的指数点位，来自快照）。

## 4. 变更记录

- v1（2026-09-19）：首版。相对任务说明 §6 草案的改动——数字统一为带来源的对象并加 `_pct`/`_cny` 后缀；`instruments` 由 primary/backup/rejected 三槽改为带 `role` 的列表（同一笔押注下的多只已持有基金要能表达）；新增 `supersedes`、`exposure.counts_toward_sector_cap` / `china_equity` / `structure`、`valuation_state.index_code`、情景 `inputs`、结构化触发器；`latest_review_date` 对所有未关闭的卡必填。
- v1 发布前修订（2026-09-19，首批卡尚未写，不升版本号）：用户澄清 ETF 同样要择时选标的——候选池逐只投研、给买卖点位，而不是"战略权重 + 估值缩放定投 + 再平衡"。`decision` 块据此重做：删除 `strategic_weight`、`zones`、`dca_multiplier`，`dca_action` 去掉 `scale`；新增无状态三锚点 `anchors`（`add_below` / `buy_below` / `reduce_above`，各带 `level`、`target_ratio_pct`、`inputs`、`rationale`）、`reduce_mode`、`no_anchor_reason`。锚点形状、只写比例不写金额、推导方法记名、减仓语义显式枚举四条来自执行侧评审。同日再按执行侧评审补两条语义：`bet_group` 与卡一一对应（同组多卡会对同一个持仓池给出互相冲突的目标仓位）；买入区只买不卖、减仓区只卖不买（避免 7 天惩罚性赎回期内的往返交易）。快照引用核对由"按打印精度取整"收紧为"与打印数字完全相等"（取整比较会让 `10年`、`P75` 这类整数给相邻的小数背书）。

## 5. 示例

示意用途的观察卡，数字全部取自 `research/etf-2026-09-18-data-snapshot.txt`，不构成任何买卖结论。

```json
{
  "card_schema_version": 1,
  "card_id": "example-csi-a500-core",
  "as_of_date": "2026-09-19",
  "supersedes": null,
  "framework": {"path": "framework/etf_framework.md", "version": "v0.1"},
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "core",
  "status": "watch",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "000510.SH",
    "index_name": "中证A500",
    "asset_type": "broad_equity",
    "currency": "CNY",
    "counts_toward_sector_cap": false,
    "china_equity": true,
    "view_mismatch_note": "",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {"value": 500, "source": "snapshot§3"},
      "max_constituent_weight_pct": {"value": 3.20, "source": "snapshot§3"},
      "top10_weight_pct": {"value": 20.25, "source": "snapshot§3"},
      "research_coverage_pct": {"value": 28.5, "source": "snapshot§3"},
      "top_constituents": [
        {"code": "300750.SZ", "name": "宁德时代", "weight_pct": {"value": 3.20, "source": "snapshot§3"}},
        {"code": "300308.SZ", "name": "中际旭创", "weight_pct": {"value": 3.16, "source": "snapshot§3"}},
        {"code": "600519.SH", "name": "贵州茅台", "weight_pct": {"value": 2.70, "source": "snapshot§3"}}
      ]
    }
  },
  "thesis": {
    "statement": "示例：以当前股债利差持有 A 股宽基，长期回报主要来自盈利增长而非估值修复",
    "evidence": ["示例证据一", "示例证据二", "示例证据三"],
    "counter_evidence": ["示例反证一", "示例反证二"],
    "horizon_months": 120
  },
  "expectation": {
    "method": "return_decomposition",
    "scenarios": {
      "bear": {
        "inputs": {
          "eps_growth_pct": {"value": 3, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 2.5, "source": "ai_estimate"},
          "current_multiple": {"value": 12.68, "source": "snapshot§1"},
          "terminal_multiple": {"value": 10.08, "source": "snapshot§1", "note": "沪深300 PE 扩张窗 P10"},
          "years": {"value": 10, "source": "ai_estimate"},
          "drag_pct": {"value": 0.20, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": -2.27, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 3.03, "source": "calc:scenario_annual_return"}
      },
      "base": {
        "inputs": {
          "eps_growth_pct": {"value": 6, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 2.5, "source": "ai_estimate"},
          "current_multiple": {"value": 12.68, "source": "snapshot§1"},
          "terminal_multiple": {"value": 12.68, "source": "snapshot§1"},
          "years": {"value": 10, "source": "ai_estimate"},
          "drag_pct": {"value": 0.20, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 0, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 8.30, "source": "calc:scenario_annual_return"}
      },
      "bull": {
        "inputs": {
          "eps_growth_pct": {"value": 8, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 2.5, "source": "ai_estimate"},
          "current_multiple": {"value": 12.68, "source": "snapshot§1"},
          "terminal_multiple": {"value": 14.46, "source": "snapshot§1", "note": "沪深300 PE 扩张窗 P75"},
          "years": {"value": 10, "source": "ai_estimate"},
          "drag_pct": {"value": 0.20, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 1.32, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 11.62, "source": "calc:scenario_annual_return"}
      }
    },
    "valuation_state": {
      "index_code": "000300.SH",
      "metric": "erp_spread",
      "value": {"value": 6.20, "source": "snapshot§1", "note": "中证A500 无估值源，以沪深300 为代理"},
      "percentile_expanding": {"value": 74.8, "source": "snapshot§1"},
      "percentile_10y": {"value": 71.1, "source": "snapshot§1"},
      "sample_n": {"value": 258, "source": "snapshot§1"},
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "",
    "list": [
      {"code": "022448.OF", "name": "国泰中证A500ETF联接-A", "instrument_type": "otc_fund", "share_class": "A",
       "platform_account": "支付宝", "role": "primary", "action": "hold", "reason": "示例：A 类无销售服务费"},
      {"code": "022449.OF", "name": "国泰中证A500ETF联接-C", "instrument_type": "otc_fund", "share_class": "C",
       "platform_account": "支付宝", "role": "rejected", "action": "none", "reason": "示例：长期持有 C 类年费更高"}
    ]
  },
  "trade_rules": {
    "min_holding_days": 7,
    "purchase_limit_note": null,
    "max_premium_pct": {"value": null, "source": null},
    "sell_if_premium_above_pct": {"value": null, "source": null}
  },
  "decision": {
    "rule_refs": ["A8", "A9"],
    "dca_action": "continue",
    "anchors": {
      "basis": "index_level",
      "index_code": "000510.SH",
      "add_below": {
        "level": {"value": 4440.68, "source": "calc:level_at_multiple"},
        "target_ratio_pct": {"value": 100, "source": "framework:A9"},
        "inputs": {
          "current_level": {"value": 5586.09, "source": "snapshot§6"},
          "current_multiple": {"value": 12.68, "source": "snapshot§1"},
          "target_multiple": {"value": 10.08, "source": "snapshot§1", "note": "沪深300 PE 扩张窗 P10"}
        },
        "rationale": "示例：代理指数 PE 回到历史 P10 对应的点位"
      },
      "buy_below": {
        "level": {"value": 4951.71, "source": "calc:level_at_multiple"},
        "target_ratio_pct": {"value": 50, "source": "framework:A9"},
        "inputs": {
          "current_level": {"value": 5586.09, "source": "snapshot§6"},
          "current_multiple": {"value": 12.68, "source": "snapshot§1"},
          "target_multiple": {"value": 11.24, "source": "snapshot§1", "note": "沪深300 PE 扩张窗 P25"}
        },
        "rationale": "示例：代理指数 PE 回到历史 P25 对应的点位"
      },
      "reduce_above": {
        "level": {"value": 6370.26, "source": "calc:level_at_multiple"},
        "target_ratio_pct": {"value": 30, "source": "framework:A9"},
        "inputs": {
          "current_level": {"value": 5586.09, "source": "snapshot§6"},
          "current_multiple": {"value": 12.68, "source": "snapshot§1"},
          "target_multiple": {"value": 14.46, "source": "snapshot§1", "note": "沪深300 PE 扩张窗 P75"}
        },
        "rationale": "示例：代理指数 PE 升到历史 P75 对应的点位"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-19"
    }
  },
  "sizing": {
    "bet_group": "cn-a-broad",
    "stress_drawdown_pct": {"value": -72, "source": "framework:A8"},
    "loss_budget_cny": {"value": null, "source": null},
    "standalone_cap_cny": {"value": null, "source": null}
  },
  "monitor_variables": [
    {"name": "指数相对10月均线", "kind": "auto", "metric": "index_vs_sma10m_pct", "operator": "<",
     "threshold": {"value": 0, "source": "framework:A9"}, "condition_text": "月末收盘低于10月均线",
     "data_source": "ai_investment 日频计算", "current_text": null, "frequency": "monthly", "action": "alert", "action_note": ""},
    {"name": "沪深300 股债利差分位", "kind": "manual", "metric": null, "operator": null,
     "threshold": {"value": null, "source": null}, "condition_text": "扩张窗分位跌破框架参数总表的低估值线",
     "data_source": "月度快照 §1", "current_text": null, "frequency": "monthly", "action": "review", "action_note": ""},
    {"name": "中证A500 编制规则", "kind": "manual", "metric": null, "operator": null,
     "threshold": {"value": null, "source": null}, "condition_text": "指数公司公告修订编制方案",
     "data_source": "中证指数公司公告", "current_text": null, "frequency": "event", "action": "review", "action_note": ""}
  ],
  "exit": {"invalidation": [], "latest_review_date": "2026-10-19"},
  "scorecard": {
    "benchmark": "同一笔钱放在货币基金",
    "preregistered_at": "2026-09-19",
    "confidence_pct": 50,
    "entry_ref_index_level": {"value": 5586.09, "source": "snapshot§6"}
  }
}
```
