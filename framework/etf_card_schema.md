# ETF 决策卡 schema v1

> 两仓唯一接口。investment_research_methods（研究侧）写卡，ai_investment（执行侧）读卡，互不 import。
> **规范实现 = `scripts/validate_etf_card.py`**（标准库，`SCHEMA_VERSION = 1`）；本文件是它的说明书，文末示例由单测
> `tests/test_validate_etf_card.py` 对着已提交的快照校验，文档与校验器不会各说各话。
> schema 是封闭的：出现未声明的字段即拒收。任何增删改字段、枚举或规则都升 `card_schema_version`，并在本文件「变更记录」登记。

## 1. 文件约定

- 路径与命名：`research/etf-cards/<card_id>-<as_of_date>.md`，例 `research/etf-cards/cn-hk-pharma-tactical-2026-09-19.md`。
- `card_id` 是跨版本稳定的身份（小写 slug，不含日期）；同一张卡更新 = 新日期的新文件，旧文件留作历史，新文件的 `supersedes` 指向旧文件相对路径。
  现行卡 = 同一 `card_id` 下 `as_of_date` 最大的一份；`as_of_date` 不得晚于当天（未来日期会永久压住此后所有版本）。
- 每个文件**恰好一个** ```` ```json ```` 围栏块；正文其余部分是给人看的论证，执行侧不解析。重复键、`NaN`/`Infinity` 拒收。
- 卡的过期时点只认 `exit.latest_review_date`；提醒提前量与过期后的处置由执行侧定义。`latest_review_date` 按任务如实写：核心卡与持有期相称（季度或更长），战术卡写短。不设固定天数的过期线——给个股锚点用的 45 天搬到持有十年的宽基上没有依据。
- 校验：`python3 scripts/validate_etf_card.py`（缺省校验 `research/etf-cards/` 下全部卡；给了文件参数也仍以整个目录做跨卡检查），零错误才可提交。除单卡规则外还查两条跨卡不变量（只看现行卡，`closed` 的卡既不占 `bet_group` 也不认领工具）：一个 `bet_group` 只属于一张卡；一只工具至多被一张卡认领。已提交的 `current.json` 与卡不一致时也报错——改了卡必须重新 `--export`。
- **执行侧只读一个文件：`research/etf-cards/current.json`**，由 `python3 scripts/validate_etf_card.py --export` 在全部卡零错误时生成（先写 `.partial` 再原子替换）并随卡一起提交；结构为
  `{generated_at, card_schema_version, portfolio_params, index_registry, cards}`——`cards` 是每张现行卡的完整 JSON，`portfolio_params` 取自 `framework/etf_portfolio_params.json`（用户拍板的基数）加两个现算的派生量 `sector_etf_cap_cny`、`single_bet_cap_cny`，`index_registry` 取自 `framework/etf_index_registry.json`。执行侧不扫目录、不自行挑现行卡，只读默认分支上的这一份；文件缺失、解析失败、`cards` 为空或 `generated_at` 过旧一律报错，不静默当作"今天没有卡"。

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
| `index_code` / `index_name` | 跟踪指数。`index_code` 只能取 `framework/etf_index_registry.json` 里登记的 key（该清单写明每个指数走哪个取数接口，两仓共用）。清单里 `source` 为空的指数（无行情源，例：恒生港股通红利低波动 `HSHYLV`）只能出现在 `exposure.index_code`，且卡只能是 `no_buy` + `data`、不带锚点；`valuation_state.index_code` 与 `scorecard.benchmark.code` 必须是有行情源的指数 |
| `asset_type` | `broad_equity` / `dividend_value` / `growth_theme` / `sector` / `cyclical` / `bond` / `gold_commodity` / `cross_border_equity`，决定估值方法 |
| `currency` | 指数计价币种，ISO 4217；登记清单里有币种时必须一致 |
| `counts_toward_sector_cap` | 布尔。是否占「行业合计」额度（用户裁定：恒生科技=否，科创50=是） |
| `china_equity` | 布尔。是否计入「中国权益」上限 |
| `view_mismatch_note` | 观点-持仓错位说明，可为空串 |
| `structure` | `weights_as_of`（日期，可空）、`constituent_count`、`max_constituent_weight_pct`、`top10_weight_pct`、`research_coverage_pct`（带来源的数）、`top_constituents`（`[{code, name, weight_pct}]`，`code` 为 `6 位.(SZ|SH|BJ)` 或 `5 位.HK` 的股票代码；其他市场的成分（例如标普500）不在范围内，留空数组；无源时为空数组；执行侧做穿透时未披露部分记为未解析，不摊到已知成分上） |

`thesis`：`statement`（1 句主判断）、`evidence`（恰好 3 条）、`counter_evidence`（恰好 2 条）、`horizon_months`（整数；`tactical` ≥1）。

`expectation`：

| 字段 | 说明 |
|---|---|
| `method` | `return_decomposition` / `reverse_valuation` / `mid_cycle` / `ytm_duration` / `scenario_only` |
| `scenarios.bear/base/bull` | 每个含 `inputs`（可空；非空则六项齐全：`eps_growth_pct`、`dividend_yield_pct`、`current_multiple`、`terminal_multiple`、`years`、`drag_pct`）、`valuation_change_pct`、`annual_return_pct`。**基准情景估值零变化**：前三种方法要求 `base.valuation_change_pct.value == 0`，后两种为 `0` 或 `null`。三个年化回报齐全时须 bear ≤ base ≤ bull |
| `valuation_state` | `index_code`（估值取自哪个指数，可以是代理指数，同样须在登记清单内）、`metric`（`erp_spread` / `pe_ttm` / `pb`）、`value`、`percentile_expanding`、`percentile_10y`、`sample_n`、`as_of`。无估值源时 `index_code`/`metric`/`value`/`as_of` 同时为 `null` |

`instruments`：`merge_note`（同一观点多只基金是否合并及理由，可为空串）+ `list`，每项：

| 字段 | 说明 |
|---|---|
| `code` / `name` | 带后缀的 ts_code：内地基金 `6 位.(OF|SZ|SH)`，港股 ETF `5 位.HK`，裸码拒收（场外基金与 A 股的 6 位代码空间重叠）。内地基金取 `fund_basic` 返回的 `ts_code` 与全名，不按前缀推断交易所；港股 ETF 不在 `fund_basic` 里，写 `<5 位代码>.HK`（例 `02800.HK`）与基金全称 |
| `instrument_type` | `otc_fund` / `exchange_etf` |
| `share_class` | `A` / `C` / `E` / … ，可空 |
| `platform_account` | `支付宝` / `盈立证券` / … |
| `currency` | 该工具**自身**的计价币种（场外基金 `CNY`，`02800.HK` 为 `HKD`）。持仓市值折人民币用它；`exposure.currency` 是指数币种，**不得**用于持仓折算 |
| `role` | `primary`（至多一个；`active`/`watch` 卡恰好一个）/ `backup` / `held_other`（已持有、属于同一笔押注的其他工具）/ `rejected`（**未持有**的落选工具；已持有而要换出的写 `held_other` + `switch_out`，要停投的写 `held_other` + `stop_dca`） |
| `action` | `buy`（仅 `status=active`，且要求三锚点齐全；可按锚点一次性买入，定投继续）/ `hold`（持有，定投继续）/ `stop_dca`（持有，停定投）/ `switch_out`（换出）/ `none`（`rejected` 必为 `none`）。**定投指令只此一处**，逐只工具给 |
| `reason` | 首选、备选、落选或处置的理由 |

**认领规则**：只有 `status ∈ {active, watch, no_buy}` 的现行卡认领持仓，认领范围 = `list` 里 `role ∈ {primary, backup, held_other}` 的全部代码；`closed` 卡不认领——上一版认领过、本版已 `closed` 而持仓仍在的，执行侧发「卡已关闭但持仓仍在」告警。一只工具在全部现行卡里至多被认领一次，其他卡提到它只能写 `rejected`。不在任何现行卡认领范围内的 ETF 持仓走「无卡」告警。认领了持仓的卡必须至少带 1 条监控变量，且 `sizing.standalone_cap_cny` 非空——持仓从股票纪律切到卡规则后，仓位上限只能由它提供。

`trade_rules`：`min_holding_days`（整数，可空）、`purchase_limit_note`（可空）。不设溢价字段：用户的工具全是按净值申赎的场外基金，唯一的场内 ETF（02800）没有净值源，溢价无从计算。

`decision`（候选池里每只 ETF 的买卖点位判断；形状对齐执行侧个股的"加仓价 / 首次买入价 / 卖出价"三锚点）：

| 字段 | 说明 |
|---|---|
| `rule_refs` | 引用的框架规则编号 |
| `anchors.basis` / `index_code` | 恒为 `index_level`；`index_code` 须等于 `exposure.index_code` |
| `anchors.add_below` / `buy_below` / `reduce_above` | 三个锚点，各含 `level`、`target_ratio_pct`、`inputs`、`rationale`（见下） |
| `anchors.reduce_mode` | `to_target_ratio`（减到 `reduce_above.target_ratio_pct`）/ `exit_all`（清仓，此时该比例必须为 0）。显式枚举，不靠文字 |
| `anchors.no_anchor_reason` | 三个锚点全为空时必填（例：无估值源且无可用推导方法），否则为 `null` |
| `anchors.valid_until` | 点位有效期；有锚点时必填，不得早于 `as_of_date`。**过期之后买入侧锚点失效、不再产生买入指令；减仓侧锚点与 `exit.invalidation` 继续生效**，直到本卡被新版取代或转为 `closed` |

锚点字段：

| 字段 | 说明 |
|---|---|
| `level` | 指数点位。**来源必须是 `calc:<函数名>`，这就是点位的推导方法**；方法日后被证伪时按函数名批量召回。目前唯一通过规则验证的推导是 `calc:level_at_drawdown_state`（入参 `rolling_high`、`state` 取自快照 §6b；框架 A9）。`level_at_multiple`（估值倍数换算）对应的规则已被否，不得用于锚点 |
| `target_ratio_pct` | 指数到达该锚点时，这笔押注（同 `bet_group`）应有的仓位，占 `sizing.standalone_cap_cny` 的百分比。**卡里只写比例不写金额**，金额由执行侧按当期上限换算 |
| `inputs` | 推导函数的入参（键 = `etf_calc` 函数的参数名，值为带来源的数），可空。齐全时校验器用该函数复算 `level`（容差 0.01 或万分之一） |
| `rationale` | 为什么取这个锚 |

锚点是**无状态**的：执行侧只拿当日指数点位 `L` 与三个点位比较，不需要成交历史。**买入区只买不卖，减仓区只卖不买**——

| 位置 | 目标仓位（占单笔上限） | 动作 |
|---|---|---|
| `L ≤ add_below` | `add_below.target_ratio_pct` | 现持仓低于目标 → 买到目标；高于目标 → **不动** |
| `add_below < L ≤ buy_below` | `buy_below.target_ratio_pct` | 同上（从更低一档回升到这一档时，多出来的仓位不卖） |
| `buy_below < L < reduce_above` | — | **不产生任何买卖指令**，保持现状；定投按各工具的 `action` |
| `L ≥ reduce_above` | `reduce_above.target_ratio_pct` | 现持仓高于目标 → 减到目标（`exit_all` 即清仓）；低于目标 → 不动。**本档定投一律暂停**，优先于各工具的 `action`；其余三档定投照常 |

单向的理由：点位在某一档边界附近来回时，双向调整会在买入区制造往返交易，而场外基金持有不满 7 天赎回要付 1.5%。
语义因此是"越跌买得越多的棘轮，贵了才减"。**买入侧锚点只在 `status=active` 且该工具 `action=buy` 时产生买入指令**；`watch` 卡的买入侧锚点只产生「到点提示复评」告警。减仓侧锚点对 `active` 与 `watch` 一律生效。持仓口径 = 该卡 `instruments.list` 里 `role != rejected` 的全部工具的人民币市值合计。

校验器钉死：三个锚点要么齐全要么全空；`add_below.level < buy_below.level < reduce_above.level` 严格成立；
比例满足 `add_below ≥ buy_below > reduce_above`。**`add_below` 是加仓位，不是止损位**——执行侧不得继承个股机器里"加仓价兼作止损距离"的耦合；
宽基不设价格止损，退出走 `exit.invalidation`。

`sizing`：`bet_group`（slug）、`stress_drawdown_pct`（负数）、`loss_budget_cny`、`standalone_cap_cny`。
**一笔押注 = 一张卡**：`bet_group` 与 `card_id` 一一对应，一个 `bet_group` 只有一个上限、一套锚点。穿透后属于同一笔押注的多只基金
（例：四只医药基金）合写成一张卡，锚点挂在主指数上，其余基金列进 `instruments.list`（`held_other` + 处置动作）。
校验器批量校验时，同一 `bet_group` 出现在两个不同 `card_id` 下即报错。行业合计上限、中国权益上限这类组合级参数不进卡，由 `framework/etf_portfolio_params.json` 给出、随 `current.json` 导出，执行侧统一检查；执行侧比对上限以最近一次持仓快照为准，报数须附快照日期。卡带锚点或认领持仓时 `standalone_cap_cny` 必填（`target_ratio_pct` 没有它就没有基数）。**核心席位的上限不逐卡算**：`framework/etf_portfolio_params.json` 的 `core_seats` 表（用户 2026-09-19 拍板：先定块——核心 35 万 / 行业 21 万 / 分散器 14 万——再定席位，压力跌幅取各自历史实测）给出上限、压力跌幅与反推的亏损预算，核心卡的 `sizing` 三个数必须与表一致，校验器强制。行业席位仍按 `loss_budget_cap(3.5 万, −70%)` = 5 万。

`monitor_variables`（`active`/`watch` 卡 3–5 条）与 `exit.invalidation`（`tactical` 且 `active`/`watch` 至少 1 条）共用同一种触发器：

| 字段 | 说明 |
|---|---|
| `name` | 变量名 |
| `kind` | `auto`（执行侧每日可算）/ `manual`（月度人工或 AI 复核） |
| `metric` / `operator` / `threshold` | `auto` 三者必填；`manual` 三者为 `null`。`operator` ∈ `<` `<=` `>` `>=` |
| `condition_text` | 人读的条件；`manual` 的条件只写在这里 |
| `data_source` / `current_text` | 来源；当前状态的文字描述（可空） |
| `frequency` | `daily` / `weekly` / `monthly` / `quarterly` / `event` |
| `action` / `action_note` | 监控变量：`alert` / `review` / `reduce` / `close` / `swap_tool`（没有 `pause_dca`：定投指令只在各工具的 `action` 上，触发器要停定投就 `review` 后出新版卡）；失效条件只能 `close` / `reduce` / `swap_tool`（对应卖出三分法） |

`auto` 的 `metric` 只有三个，全部只依赖指数点位（执行侧每日可算；仓位类、溢价类条件执行侧没有可靠的每日数据，一律写成 `manual`）：

| metric | 定义 |
|---|---|
| `index_level` | `exposure.index_code` 最新日收盘点位 |
| `index_vs_sma200_pct` | (最新收盘 ÷ 近 200 个交易日收盘均值 − 1) × 100 |
| `index_vs_sma10m_pct` | (最近已完成月月末收盘 ÷ 最近 10 个已完成月月末收盘均值 − 1) × 100；当月未完成不参与，月末评估 |

`exit`：`invalidation`、`latest_review_date`（除 `closed` 外必填，且晚于 `as_of_date`）。

`scorecard`：`benchmark`（`{code, name}`：不买它时这笔钱放哪，即记分基准；`code` 取登记清单里的 key，没有合适代码时为 `null`）、`preregistered_at`（不晚于 `as_of_date`）、`confidence_pct`（0–100 的裸数字，主观判断）、`entry_ref_index_level`（写卡时 `exposure.index_code` 的点位，来自快照；**只用于事后记分，不得作为任何触发器的输入**——每次刷卡它都会变）。

## 4. 变更记录

- v1（2026-09-19）：首版。相对任务说明 §6 草案的改动——数字统一为带来源的对象并加 `_pct`/`_cny` 后缀；`instruments` 由 primary/backup/rejected 三槽改为带 `role` 的列表（同一笔押注下的多只已持有基金要能表达）；新增 `supersedes`、`exposure.counts_toward_sector_cap` / `china_equity` / `structure`、`valuation_state.index_code`、情景 `inputs`、结构化触发器；`latest_review_date` 对所有未关闭的卡必填。
- v1 发布前修订（2026-09-19，首批卡尚未写，不升版本号）：用户澄清 ETF 同样要择时选标的——候选池逐只投研、给买卖点位，而不是"战略权重 + 估值缩放定投 + 再平衡"。`decision` 块据此重做：删除 `strategic_weight`、`zones`、`dca_multiplier`，`dca_action` 去掉 `scale`；新增无状态三锚点 `anchors`（`add_below` / `buy_below` / `reduce_above`，各带 `level`、`target_ratio_pct`、`inputs`、`rationale`）、`reduce_mode`、`no_anchor_reason`。锚点形状、只写比例不写金额、推导方法记名、减仓语义显式枚举四条来自执行侧评审。同日按执行侧四视角评审再收紧（仍未发布）：新增导出产物 `current.json`、指数登记清单与组合参数文件；`instruments` 加 `currency`、代码必须带后缀、`rejected` 限未持有；删除 `trade_rules` 的溢价字段与 `decision.dca_action`（定投只由各工具的 `action` 给）；`auto` 指标由 7 个收缩为 3 个；`scorecard.benchmark` 改为 `{code, name}`；新增规则——认领持仓的卡须带监控变量与仓位上限、`action=buy` 须三锚点齐全、无行情源的指数只能 `no_buy/data`、`as_of_date` 不得晚于当天、一只工具至多被一张卡认领；删除固定 30/45 天过期线，只认 `latest_review_date`；写明 `valid_until` 过期后与减仓区的定投语义。第二轮代码审查后再补：`closed` 卡释放 `bet_group`；`valid_until` 不得早于 `as_of_date`；`exposure.currency` 须与登记清单一致；估值与记分基准只能引用有行情源的指数；删除触发器动作 `pause_dca`；缺省校验会比对已提交的 `current.json`。此前同日补的两条语义：`bet_group` 与卡一一对应（同组多卡会对同一个持仓池给出互相冲突的目标仓位）；买入区只买不卖、减仓区只卖不买（避免 7 天惩罚性赎回期内的往返交易）。快照引用核对由"按打印精度取整"收紧为"与打印数字完全相等"（取整比较会让 `10年`、`P75` 这类整数给相邻的小数背书）。

## 5. 示例

示意用途的观察卡，数字全部取自 `research/etf-2026-09-18-data-snapshot.txt`，不构成任何买卖结论。

```json
{
  "card_schema_version": 1,
  "card_id": "example-csi-a500-core",
  "as_of_date": "2026-09-19",
  "supersedes": null,
  "framework": {
    "path": "framework/etf_framework.md",
    "version": "v0.1"
  },
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
    "horizon_months": 120
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
            "value": 12.68,
            "source": "snapshot§1"
          },
          "terminal_multiple": {
            "value": 10.08,
            "source": "snapshot§1",
            "note": "沪深300 PE 扩张窗 P10"
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
          "value": -2.27,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 3.03,
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
            "value": 12.68,
            "source": "snapshot§1"
          },
          "terminal_multiple": {
            "value": 12.68,
            "source": "snapshot§1"
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
          "value": 0,
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
            "value": 12.68,
            "source": "snapshot§1"
          },
          "terminal_multiple": {
            "value": 14.46,
            "source": "snapshot§1",
            "note": "沪深300 PE 扩张窗 P75"
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
          "value": 1.32,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 11.62,
          "source": "calc:scenario_annual_return"
        }
      }
    },
    "valuation_state": {
      "index_code": "000300.SH",
      "metric": "erp_spread",
      "value": {
        "value": 6.2,
        "source": "snapshot§1",
        "note": "中证A500 无估值源，以沪深300 为代理"
      },
      "percentile_expanding": {
        "value": 73.7,
        "source": "snapshot§1"
      },
      "percentile_10y": {
        "value": 71.1,
        "source": "snapshot§1"
      },
      "sample_n": {
        "value": 247,
        "source": "snapshot§1"
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
        "reason": "示例：A 类无销售服务费；hold = 持有且定投继续"
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
      "A8",
      "A9",
      "A13"
    ],
    "anchors": {
      "basis": "index_level",
      "index_code": "000510.SH",
      "add_below": {
        "level": {
          "value": 3928.56,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 100,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 6314.99,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.6221,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P10"
          }
        },
        "rationale": "示例：回撤状态回到自身历史 P10 对应的点位（框架 A9，预注册 R2 validated）"
      },
      "buy_below": {
        "level": {
          "value": 4354.19,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 50,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 6314.99,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.6895,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P25"
          }
        },
        "rationale": "示例：回撤状态回到自身历史 P25 对应的点位（框架 A9，预注册 R2 validated）"
      },
      "reduce_above": {
        "level": {
          "value": 5965.14,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 30,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 6314.99,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.9446,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P75"
          }
        },
        "rationale": "示例：回撤状态回到自身历史 P75 对应的点位（框架 A9，预注册 R2 validated）"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "cn-a-broad",
    "stress_drawdown_pct": {
      "value": -72,
      "source": "user:2026-09-19",
      "note": "核心席位上限表：沪深300 2007–08 实测"
    },
    "loss_budget_cny": {
      "value": 86400,
      "source": "user:2026-09-19",
      "note": "核心席位上限表：上限 × 压力跌幅反推"
    },
    "standalone_cap_cny": {
      "value": 120000,
      "source": "calc:loss_budget_cap"
    }
  },
  "monitor_variables": [
    {
      "name": "指数相对10月均线",
      "kind": "auto",
      "metric": "index_vs_sma10m_pct",
      "operator": "<",
      "threshold": {
        "value": 0,
        "source": "framework:A9"
      },
      "condition_text": "月末收盘低于10月均线",
      "data_source": "ai_investment 日频计算",
      "current_text": null,
      "frequency": "monthly",
      "action": "alert",
      "action_note": ""
    },
    {
      "name": "沪深300 股债利差分位",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "扩张窗分位跌破框架参数总表的低估值线",
      "data_source": "月度快照 §1",
      "current_text": null,
      "frequency": "monthly",
      "action": "review",
      "action_note": ""
    },
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
    }
  ],
  "exit": {
    "invalidation": [],
    "latest_review_date": "2026-12-19"
  },
  "scorecard": {
    "benchmark": {
      "code": "H11025.CSI",
      "name": "同一笔钱放在货币基金"
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
