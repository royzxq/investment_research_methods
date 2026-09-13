# 期货周度执行诊断：共享口径与模板

每周由 `future-change-analysis` 生成 `research/<AS_OF_DATE>-execution-audit.md`，不以 `update_needed=yes` 为前提。完整流水线如更新了框架，编排器在数据同步后按最终版本刷新同一诊断，标明版本尚待合并；不得把新规则伪装成历史交易日已生效的规则。单独定向维护只写本次诊断，不重跑或覆盖历史市场调研。

诊断只评估证据、候选与执行完备性，不代替成交记录。风险定义及计算以 `framework/futures_framework.md` 的 Step5 / #31 和 `scripts/futures_risk.py` 为唯一来源；本模板不保存第二套公式。行情脚本的分位或单腿参考手数不能替代真实交易计划、组合预算和保证金核验。风险 helper 只计算数值容量，滑点、跳空压力与完整执行门未核验时仍不能 ready。

## 有限数据模式与发布前检查（v2.24）

先读 `framework/FUTURES_DATA_PROTOCOL.md`。`research_mode=public_data`；逐模型记录 `data_feasibility=available / temporary_gap / research_only`，与交易status分开。强因果模型不可得时退出执行候选但保留历史记录、已知阻断及复活条件；coverage同时列研究范围和排除范围，不能声称全市场覆盖。

逐项先判适用性再判门。增强字段缺失不进unknown_checks；必要数据缺失才影响相应候选。当前值必须有完整年份/观察日/单位/来源，比较值必须同口径；搜索摘要不能替代当期证据，旧资料不回填。对已知错误先撤回触发再重评，不沿用原“保守数字”。

以下错误发布前必须修复：A豁免D8却因其缺失判#13失败；完整结构计#16或单边D12；30–60参考期当固定最低期；未知账户风险填0；同源转载重复验证；SC收盘代结算；高分位代替近期反弹；only_blocker无充分依据。换月33/41样本下限及A固定评分口径只引用canonical，勿另改参数。

机器块使用严格JSON（schema 3；schema 2仅兼容历史版本），便于标准库工具校验。运行 `python3 scripts/validate_futures_audit.py --input research/<date>-execution-audit.md`，失败先修。校验仅检查结构、状态和日期内部一致性，不核查网络内容真实、不覆盖完整交易许可或经济逻辑；通过不等于ready。流水线无本地执行环境时按同一清单检查并明确“未运行校验器”，不能虚构通过。

发布时附校验器命令、退出码/错误摘要和待人工核验事项；不能仅更换JSON代码块标签而保留YAML或旧字段。AU/SC信号席记录在coverage或独立signal_observations，不用signal_only混入执行候选。已有许可但换月对未计算记temporary_gap，不能直接判research_only。

#3逐个precheck说明适用理由；国内路线不自动引用全局①未知项。#5可在details分写价格确认与独立产业证据，检查result仍只取一个值：有充分已核失败依据可fail并同时保留未完成子项；只有缺项则unknown，不能写fail/unknown。第一条否决只来自已知fail；仅一项fail且仍有未知时only_blocker=null。逐项适用性和结果须与all_blockers/unknown_checks对应，不将“其余not_applicable或unknown”当作完成检查。

## 证据与计数口径

- 候选单位为 `交易日 + 具体合约或价差对 + 策略 + 方向 + 框架版本`。未定方向记 `unknown`，只是待定义候选；确定方向后建立具体记录并关联原记录，汇总去重。未定义的策略不能自行从价格走势反推。
- 同一机会跨周延续须关联 `opportunity_id`，保留每日/每周快照但不当作多笔独立交易。策略A的分位只是观测证据，本期仅有高分位研究筛选，未新增低分位对称策略；`reversion` / `continuation`、价差方向及 Entry/SL/TP 由完整计划决定。定义高分位回归的做空价差协议不代表本期触发；continuation 未显式许可不开放。
- 同时保留所有**已核实**的阻断 `all_blockers` 和所有缺口 `unknown_checks`；不能因已发现一条阻断便把余下检查补写为已过。`first_blocker` 是实际检查顺序下第一条已核实否决，附检查顺序，不代表因果贡献最大。
- `only_blocker=true` 仅在其他适用检查全部完成且只有该项否决时填写；至少两项已知阻断可填 `false`；否则填 `null`。删除第一条规则不代表可以交易。
- `final_lots=null` 表示计划、账户或约束尚未补齐，`0` 表示所需输入齐全后计算/核验确实不可执行。不得把未提供的持仓、净值、保证金或风险占用填成零。`POSITIONS={}` / `[]` 是脚本配置，不足以证明账户空仓。实际持仓未知时组合已用风险与最终手数均为 null；挂单、部分成交未入持仓部分的预留风险也计入预算。
- 实际持仓 `actual_position_status` 仅有 `verified_flat` / `verified_positions` / `unknown`：前两者须带时间戳、已核验的当期完整账户快照（可由用户提供），并保留来源与覆盖范围。`verified_at` 必须为带时区的完整时间戳，转换为 Asia/Shanghai 后日期须等于本次 `as_of_date`；仅有日期或旧日快照不能支撑非 null 手数或 ready。报告里的“存量持有/减仓”等管理规则不证明曾持仓或成交。
- 行情记录同时写观测交易日、采集时间/未知、来源与计算版本；账户写核验时间/未知；规则写版本和修订号。旧脚本输出可作为有日期的行情证据，已废弃风险或标签单列为不可沿用。

## 状态判定

`signal` 为 `triggered` / `not_triggered` / `unknown`，只描述该记录的已定义信号条件，不是“可以下单”。状态依以下顺序确定：

1. `signal=not_triggered` 且未触发有完整直接证据：`status=no_signal`；明确限定策略/方向覆盖范围，并列后续未评估项。不能外推为该品种所有策略均无机会。
2. 必需证据、方向、计划或风险/账户核验有缺口，或 `signal=unknown`：`status=incomplete`，已知否决仍保留在 `all_blockers`。缺口不因另有阻断而消失。
3. 其余适用检查全部完成且存在否决或最终手数为零：`status=blocked`。
4. `signal=triggered`、所有适用检查完成、无否决、完整计划及账户组合核验通过且 `final_lots>=1`：`status=ready`。这仍是研究输出，不是已成交。

缺少完整候选账时，汇总填 `coverage=partial` / `unknown`，总体机会数用 `null`；可以汇总已观察记录但须标样本范围。不得写“市场建议空仓”“市场没有机会”“规则已节省亏损”，也不得以没有 `ready` 记录虚构“0 个机会”。

## 输出模板

下面是无行情/账户的缺项示例，日期和标识由当次运行替换，不代表本期市场结论。`evaluated_checks`统一存对象与证据，`all_blockers`/`unknown_checks`只存对应rule_id；不得混存字符串解释和对象。背景缺失在全局evidence表留痕，不能伪装适用门失败。

证据行字段：evidence_id、metric、value、unit、observation_date、published_at、source_url_or_file、original_source、price_basis、comparison_basis、role、quality、time_scope。role=required_execution/required_model/optional_context；quality=verified/missing/stale/conflicting/invalid；time_scope=current/historical。非价格/非比较指标可将对应basis设null；用户文件以可核快照时间记录，不猜发布日期。

适用检查填 `result=pass/fail` 时，其 `evidence_refs` 作为判定依据必须逐条 `quality=verified`；不可用证据只放 `diagnostic_evidence_refs` 解释撤回/缺项，不能保留为失败依据。optional_context留全局背景，不混入支持门的引用。行情证据允许完整日期及明确的历史观察值，不套用账户的当日时间戳要求。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-09-10",
  "research_mode": "public_data",
  "assessment_scope": "proposed_framework_reassessment",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v2.24",
    "revision": "working_tree"
  },
  "snapshot": {
    "market_trade_date": null,
    "market_captured_at": null,
    "source_artifacts": [],
    "account": {
      "actual_position_status": "unknown",
      "verified_at": null,
      "evidence": null,
      "equity": null,
      "open_positions": null,
      "pending_orders": null,
      "existing_risk": null,
      "reserved_order_risk": null,
      "margin_available": null,
      "configured_equity": 150000
    }
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [],
    "missing_scope": [],
    "research_only_scope": [],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [],
  "candidates": [
    {
      "candidate_id": "example-pending-plan",
      "opportunity_id": null,
      "trade_date": null,
      "contracts": [],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "尚未取得该候选的最小行情与独立产业证据",
      "signal": "unknown",
      "signal_basis": null,
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "model_inputs",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "价格/结构确认与独立产业证据待核",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "取得所选合约报价和一项独立产业事实，完成具体计划",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "实际账户快照未提供",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核验当期账户及挂单",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "model_inputs",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "model_inputs",
        "account"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": []
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": []
    }
  ],
  "unresolved_items": [
    {
      "item": "完成一份基于可得公开证据的具体计划",
      "owner": "research",
      "due_at": "next_report",
      "required_evidence": [],
      "resolution": "pending"
    }
  ],
  "evidence_corrections": []
}
```

confirmation_definition为计划留痕字段：state=undefined/draft/frozen；其语义和事件日期口径按数据协议5.1/5.2人工核验，结构校验器不验证信号规则本身的经济有效性。未冻结的草案不能回填历史signal=triggered。

报告正文用一段结论、候选表及待补事项解释 JSON。对于受阻记录，写清是账户可执行性、策略否决还是研究未完成；缺少历史完整证据时明确不能判断连续空仓和机会成本。规则有效性比较须事前固定进出场/成本、纳入盈利与亏损影子候选，并按独立机会去重；命中数和事后涨幅都不是有效性证明。未固定计划的影子记录仅为假设，不能写已避免损失。

## schema 3的新增约束

- 每条适用unknown检查须有gap对象：kind=definition/plan/calculation/raw_data/acquisition/not_published/account；owner、next_action、due_at为非空字符串。definition/plan→research，calculation→data_pipeline，account→user，not_published→publisher。due_at可用明确日期或next_report/before_execution；不得无限“待裁”。not_published另须expected_release_at（带时区）及release_evidence_refs（已核官方日历证据），治理截止不算。
- `signal=not_triggered`必须给非空signal_evidence_refs，直接引用有效的触发输入（如合约分位或B日历）；不以账户未知代替未触发。字段表达真实性仍由研究方核查。
- 顶层evidence_corrections总是数组，无纠错时[]；每项含withdrawn_evidence_id、reason、affected_checks（candidate_id/rule_id对象数组）、recalculation=completed/pending。原证据必须保留为invalid，新证据另建ID。pending时受影响的适用检查为unknown，已知其他阻断不删除。completed须在正文展示门/评分/系数/状态/风险前后重算差异，不能只填枚举宣称完成。
- candidate_id非空且唯一；撤回证据不能留在candidate evidence_refs/signal_evidence_refs或任何pass/fail依据，只能作diagnostic_evidence_refs。日期/来源年份需人工查看原文，校验器不凭URL猜年份、不证明所有门已评估或完成经济重算。
