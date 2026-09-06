# 期货周度执行诊断：共享口径与模板

每周由 `future-change-analysis` 生成 `research/<AS_OF_DATE>-execution-audit.md`，不以 `update_needed=yes` 为前提。完整流水线如更新了框架，编排器在数据同步后按最终版本刷新同一诊断，标明版本尚待合并；不得把新规则伪装成历史交易日已生效的规则。单独定向维护只写本次诊断，不重跑或覆盖历史市场调研。

诊断只评估证据、候选与执行完备性，不代替成交记录。风险定义及计算以 `framework/futures_framework.md` 的 Step5 / #31 和 `scripts/futures_risk.py` 为唯一来源；本模板不保存第二套公式。行情脚本的分位或单腿参考手数不能替代真实交易计划、组合预算和保证金核验。风险 helper 只计算数值容量，滑点、跳空压力与完整执行门未核验时仍不能 ready。

## 证据与计数口径

- 候选单位为 `交易日 + 具体合约或价差对 + 策略 + 方向 + 框架版本`。未定方向记 `unknown`，只是待定义候选；确定方向后建立具体记录并关联原记录，汇总去重。未定义的策略不能自行从价格走势反推。
- 同一机会跨周延续须关联 `opportunity_id`，保留每日/每周快照但不当作多笔独立交易。策略A的分位只是观测证据，本期仅有高分位研究筛选，未新增低分位对称策略；`reversion` / `continuation`、价差方向及 Entry/SL/TP 由完整计划决定。定义高分位回归的做空价差协议不代表本期触发；continuation 未显式许可不开放。
- 同时保留所有**已核实**的阻断 `all_blockers` 和所有缺口 `unknown_checks`；不能因已发现一条阻断便把余下检查补写为已过。`first_blocker` 是实际检查顺序下第一条已核实否决，附检查顺序，不代表因果贡献最大。
- `only_blocker=true` 仅在其他适用检查全部完成且只有该项否决时填写；至少两项已知阻断可填 `false`；否则填 `null`。删除第一条规则不代表可以交易。
- `final_lots=null` 表示计划、账户或约束尚未补齐，`0` 表示所需输入齐全后计算/核验确实不可执行。不得把未提供的持仓、净值、保证金或风险占用填成零。`POSITIONS={}` / `[]` 是脚本配置，不足以证明账户空仓。实际持仓未知时组合已用风险与最终手数均为 null；挂单、部分成交未入持仓部分的预留风险也计入预算。
- 实际持仓 `actual_position_status` 仅有 `verified_flat` / `verified_positions` / `unknown`：前两者须带时间戳、已核验的当期完整账户快照（可由用户提供），并保留来源与覆盖范围。报告里的“存量持有/减仓”等管理规则不证明曾持仓或成交。
- 行情记录同时写观测交易日、采集时间/未知、来源与计算版本；账户写核验时间/未知；规则写版本和修订号。旧脚本输出可作为有日期的行情证据，已废弃风险或标签单列为不可沿用。

## 状态判定

`signal` 为 `triggered` / `not_triggered` / `unknown`，只描述该记录的已定义信号条件，不是“可以下单”。状态依以下顺序确定：

1. `signal=not_triggered` 且未触发有完整直接证据：`status=no_signal`；明确限定策略/方向覆盖范围，并列后续未评估项。不能外推为该品种所有策略均无机会。
2. 必需证据、方向、计划或风险/账户核验有缺口，或 `signal=unknown`：`status=incomplete`，已知否决仍保留在 `all_blockers`。缺口不因另有阻断而消失。
3. 其余适用检查全部完成且存在否决或最终手数为零：`status=blocked`。
4. `signal=triggered`、所有适用检查完成、无否决、完整计划及账户组合核验通过且 `final_lots>=1`：`status=ready`。这仍是研究输出，不是已成交。

缺少完整候选账时，汇总填 `coverage=partial` / `unknown`，总体机会数用 `null`；可以汇总已观察记录但须标样本范围。不得写“市场建议空仓”“市场没有机会”“规则已节省亏损”，也不得以没有 `ready` 记录虚构“0 个机会”。

## 输出模板

```yaml
audit_schema_version: 1
as_of_date: YYYY-MM-DD
assessment_scope: active_framework  # active_framework / proposed_framework_reassessment
framework:
  path: framework/futures_framework.md
  version: null
  revision: null  # commit 或明确 working_tree；未合并版本须说明
snapshot:
  market_trade_date: null
  market_captured_at: null
  source_artifacts: []  # 文件/URL、版本、观测日期、核验范围、不能沿用的旧计算
  account:
    actual_position_status: unknown
    verified_at: null
    evidence: null
    equity: null
    open_positions: null
    pending_orders: null
    existing_risk: null
    reserved_order_risk: null
    margin_available: null
    configured_equity: null  # 框架配置不是核验净值
coverage:
  completeness: partial  # complete / partial / unknown
  covered_scope: []
  missing_scope: []
  total_executable_opportunities: null
  historical_trade_performance: unavailable
candidates:
  - candidate_id: YYYY-MM-DD|contracts|strategy|direction|version
    opportunity_id: null
    trade_date: YYYY-MM-DD
    contracts: []
    strategy: null
    hypothesis: null  # A 必填 reversion / continuation；未决定填 null
    direction: unknown  # long / short / long_spread / short_spread / unknown
    signal: unknown
    signal_basis: null
    screening_evidence: null  # 仅分位极端时放此处，不能代写完整信号
    evaluated_checks: []
    evaluation_order: []
    all_blockers: []  # rule_id + 判定依据 + 数据日期
    unknown_checks: []
    first_blocker: null
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: framework/futures_framework.md Step5 / #31
      calculator_ref: scripts/futures_risk.py
      result: null  # 完整输入与 helper 输出的可追溯引用；不另算一套公式
    final_lots: null
    status: incomplete
    not_evaluated_after_no_signal: []
    evidence_refs: []
unresolved_items:
  - item: null
    owner: null  # 未指定就填 null，不虚构已分配
    due_at: null  # 未指定就填 null；到期以显式裁决收尾，不静默顺延
    required_evidence: []
    resolution: pending
```

报告正文用一段结论、候选表及待补事项解释 YAML。对于受阻记录，写清是账户可执行性、策略否决还是研究未完成；缺少历史完整证据时明确不能判断连续空仓和机会成本。规则有效性比较须事前固定进出场/成本、纳入盈利与亏损影子候选，并按独立机会去重；命中数和事后涨幅都不是有效性证明。
