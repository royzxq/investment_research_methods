# 期货执行诊断：v3.0 两类策略与六个条件

本模板对应 [canonical](../../framework/futures_framework.md#r-v3-audit) 与 [数据协议](../../framework/FUTURES_DATA_PROTOCOL.md)，不另存一套投资规则。每周报告存入 `research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-execution-audit.md`；定向维护按 `research/README.md` 保存隔离产物。方法变更后的重评须标注 `proposed_framework_reassessment` 和最终版本，不能把新规则写成历史已生效；纯状态刷新/证据纠错沿用实际方法并注明修订来源，不假称方法升级。已有T信号可按原有效期为未来执行登记。先复核全部已知存量计划/持仓的事件、反证、止损及期限；至多两条只限制新机会深研，优先 M、RB；证据不足就写具体缺口，不将尚未完成的研究解释为没有机会。

从按类型采纳的 handoff 及跨 worktree 共享记录读取前期事实、原计划和累积纠错，逐条处理适用范围；保留实际canonical修订/哈希、输入行情日与评估时间。新鲜度、真实日历、信号有效期和登记后的可执行时段须在运行中复核，结构校验通过不能代替这些检查。机械refresh结果只有价格筛查含义，不能直接变为ready或替代G1–G6；本期审计采纳后登记精确路径，不按修订文件名自动提升。

## 最小诊断

只用 `strategy=trend / economic_reversion`。顺势研究 M/RB/MA/SR/CF，以单合约价格确认加独立经济证据；经济回归限 MA/RB/SR 同品种近远月 1:1 配对，加可核经济锚与收敛机制。旧 A–H、加权评分、季节硬窗口、D8/D11 高位禁入均不作为新版额外门。`evidence_quality=strong / adequate / weak` 只作排序；关键证据缺失仍是 G2 unknown，其余弱证据的市场风险折减按 canonical，不用分数否决。

| ID | 必要条件 | 归属 |
|---|---|---|
| G1 | 范围、真实合约、期限及流动性 | 研究 |
| G2 | 已冻结的模型信号及独立当前经济证据 | 研究 |
| G3 | 完整数值计划、入场有效区间及退出规则 | 研究 |
| G4 | 公开合约与报价、事件、跳空/配对压力场景及执行方案 | 研究 |
| G5 | 当期真实账户、组合预算、账户实收保证金及资金/账户限额 | 用户账户输入后核验 |
| G6 | 风险、保证金、限仓、执行/压力/周末硬容量取严，最终至少 1 手/组 | 账户输入后计算 |

六门都适用，子条件的适用理由写在 details。`result=pass/fail/unknown`，失败和缺项同时存在时都保留；旧 A/#31/D8 ID 只用于历史 schema 2/3 报告。信号直接证实未触发时可以早停，后续未评估门列在 `not_evaluated_after_no_signal`；除此之外六门必须逐一记录。判断以实际完整门为准，校验器不核证据真实性或经济有效性。

G4 完成公开风险与执行方案，不等待账户实收保证金、可用资金或个人账户限额；这些必要缺项归 G5/G6，避免账户未知阻止研究成案。公开交易所规则仍要在 G4 读取，不能因账户后置而略去事件或制度限制。

## 计划与状态

- 候选单位=`行情日+真实合约/价差对+策略+方向+框架版本`。同一机会跨周保留 `opportunity_id`，不能重复计为新交易。`direction=long/short`；未定方向只可登记 `unknown` 的未完成候选。
- 当前重评记录带时区`evaluated_at/registered_at`，保留原`plan.signal_date`和`valid_until`。只使用登记后的未来可交易时段，不重启两日计时、不回填已发生夜盘；当前产业证据不冒充当时已知。V经济锚的信号前冻结要求不变。
- 两类计划共用 `entry`、`stop`、`entry_range=[low,high]`、`signal_date`、`valid_until`、`latest_exit_date`。日期须为 `YYYY-MM-DD`，有效期和最晚退出须按真实交易日验证；研究方填写，不由用户补写策略。工具的 `entry_expiry` 转为 ISO 日期记入 `valid_until`，选择某日入场时另外保留 `entry_date`。回归的有效报价区间由研究方事前冻结，允许单点 `[Entry,Entry]`，不额外设任意宽度阈值。
- `trend`：一张真实合约，`targets=null`，`exit_rule=initial_2atr_and_prior10_channel_tighten_only_max20_sessions`；止损由真实入场与 ATR 确定，前 10 日通道只收紧，最多 20 个交易日。无固定 TP、无净 R 门，不为评分虚构目标。信号/范围/价格和期限用 `scripts/futures_strategy.py` 的当前入口验证。
- `economic_reversion`：contracts 按近、远顺序列两张同品种真实合约，`leg_ratio=[1,1]`，`anchor_band={low,high,source,as_of_date}`，以及 `economic_anchor_basis`、`convergence_mechanism`、`invalidation_basis`。`targets` 仅含靠近入场一侧的锚边界，整个 entry_range 严格位于 SL 和目标之间，采用经济失效止损；报告 `net_R` 取计算器 `entry_range_min_reward_risk`（整个区间最差净 R），必须≥2.5，选定报价的 `reward_risk` 可另列 `selected_entry_net_R`。计划有效期为信号后 2 个交易日，失效须重新计算，不能沿用旧锚、分位或旧信号。
- `signal=not_triggered` 且有完整直接证据 → `no_signal`。仅说明本路线未触发，不外推全品种无机会。
- 周度研究可预写最多两份尚未触发的条件观察计划，仍标 `no_signal`；在 `observation_plan` 说明触发条件、经济依据及需要刷新什么，不虚构未来 signal_date，不标 ready。T/V 信号只有两个交易日有效，每个交易日机械刷新价格/信号/有效期，触发后补齐六门及实际账户再判断；同一机会保留原登记时间及窗口，刷新失败/缺项单独报告，不借刷新生成历史成交。
- 必要证据、方向、计划、执行或账户存在未完成项 → `incomplete`，已知失败仍列 `all_blockers`。G1–G4 均 pass 且完整计划成立、只余账户相关 G5/G6 unknown → `awaiting_account`、`final_lots=null`，不能藏在 incomplete。
- 没有未知项、账户已核且有已知硬失败或核算容量为零 → `blocked`。G1–G6 全 pass、信号触发、数据可得、完整计划与当日账户均核验且 `final_lots>=1` → `ready`。ready 是研究结论，不代表交易已执行。

## 证据与账户

`research_mode=public_data`。数据可行性 `available / temporary_gap / research_only` 与交易状态分列；必要原料暂缺写可执行补件动作，强因果模型不可持续取得证据则退出执行候选，并保留排除范围与复活条件。增强背景缺失不进 unknown、不影响其他候选。

证据行固定字段：`evidence_id, metric, value, unit, observation_date, published_at, source_url_or_file, original_source, price_basis, comparison_basis, role, quality, time_scope`。role=required_execution/required_model/optional_context；quality=verified/missing/stale/conflicting/invalid；time_scope=current/historical。关键事实须实际阅读来源正文并带完整年份/单位/可比口径，搜索摘要只作线索，旧年资料不补当前值。可信公开转引可用，但须注明原发布者、观察期与口径限制；同源转载不计独立验证。pass/fail 的 `evidence_refs` 只能引用 verified；失效证据只进 `diagnostic_evidence_refs`。

每条 unknown 必须有 `gap={kind,owner,next_action,due_at}`。kind=definition/plan/calculation/raw_data/acquisition/not_published/account；definition/plan→research，calculation→data_pipeline，account→user，not_published→publisher。due_at 可以是日期或 next_report/before_execution；未发布另须官方发布日程证据 `expected_release_at`、`release_evidence_refs`，治理截止不等于官方发布日期。

实际账户 `actual_position_status=verified_flat / verified_positions / unknown`。已核账户须有当天带时区 verified_at、来源、净值、持仓、挂单、已占和预留风险、可用保证金；换算北京时间须等于 as_of_date。脚本配置空仓不能证明真实空仓。unknown 时上述事实和 final_lots 一律 null；0 仅用于输入齐全后已证实零容量。风险数值唯一出处为 canonical 与 `scripts/futures_risk.py size-v3`；计划止损不是跳空情况下的保证最大亏损。

G6 通过时保留 `risk_evaluation.calculator_ref="scripts/futures_risk.py size-v3"` 及原 helper `result`，至少包含 rule_version=v3.0、scope=risk_sizing_only、status=valid、final_lots。候选 final_lots 不得高于 helper 最终容量；该值已经包含 execution_capacity_lots、显式适用的 stress/weekend_capacity_lots，不能只摘出 risk_lots。更低整数可作为额外谨慎选择，仍须不少于 1 才能 ready。压力金额和周末适用性未知归 G5/G6，不能绕过执行/压力上限。

all_blockers/unknown_checks 仅放 rule_id，须与六门实际 fail/unknown 一致。first_blocker 是 evaluation_order 的首个 fail，非最大因果贡献。only_blocker=true 仅当账户已核、全部适用检查完成且恰有一个 fail；两个以上 fail 可填 false；其他情况 null。覆盖不完整时总体机会数为 null，不宣称“市场没有机会”“规则节省亏损”。

## 可校验的缺项示例

下面只示范结构，不是行情或交易建议。日期、合约及 ID 在新报告中替换；全文只保留一个 JSON 机器块。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-11",
  "research_mode": "public_data",
  "assessment_scope": "proposed_framework_reassessment",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
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
    "missing_scope": [
      "M/RB优先路线尚未取得当期数据"
    ],
    "research_only_scope": [],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [],
  "candidates": [
    {
      "candidate_id": "example-M-trend-pending",
      "opportunity_id": null,
      "trade_date": null,
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "示例：所需行情与独立供需事实尚未取得",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核所选真实合约、期限与流动性",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核所选真实合约、期限与流动性",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "计算冻结信号并取得独立当前产业证据",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "计算冻结信号并取得独立当前产业证据",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "形成数值计划、入场有效区间和退出规则",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "形成数值计划、入场有效区间和退出规则",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核公开事件、跳空/配对压力场景、报价及执行方案",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核公开事件、跳空/配对压力场景、报价及执行方案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核验当期净值、持仓、挂单、实收保证金及资金/账户限额",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核验当期净值、持仓、挂单、实收保证金及资金/账户限额",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户齐全后运行size-v3核最终整数容量",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户齐全后运行size-v3核最终整数容量",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
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
      "item": "先完成至多两条真实方案；研究缺口不能长期转嫁给用户",
      "owner": "research",
      "due_at": "next_report",
      "required_evidence": [],
      "resolution": "pending"
    }
  ],
  "shadow_plans": [],
  "evidence_corrections": []
}
```

## 发布与前瞻复核

运行 `python3 scripts/validate_futures_audit.py --input <本次报告.md>`，报告写实际命令、退出码/错误摘要及仍待核内容。该工具只验证 JSON、日期、计划字段与六门状态一致性；它不验证价格/经济因果、全部规则覆盖或执行许可。没有本地运行条件就明确“未运行”，不得虚构通过。

正文只需短结论、候选表、缺口责任：品种/方向、核心事实及反证、入场区间/SL/退出、最晚退出日、研究状态与账户缺项。将研究未完成、已核策略失败和账户待核分开写。

每轮对最接近成立的至多两条候选保存事前完整 plan，后续用 opportunity_id 链接原记录，记录触发、退出/失效、成本假设与未完成项，不事后改原计划。v3 报告的 `shadow_plans=[]`；旧 schema 3 固定目标影子解析器仅为历史兼容，不能给无固定 TP 的趋势塞一个伪目标，不能将其自动结算冒充 v3 绩效。新版前瞻跟踪尚需人工审计，未验证收益不是关闭研究路线的理由。

`evidence_corrections` 始终为数组。撤回时旧 evidence 保留为 invalid，每项含 withdrawn_evidence_id、reason、affected_checks(candidate_id/rule_id)、recalculation=completed/pending；pending 的受影响门必须 unknown。完成时正文解释证据、状态、预算与计划重算，不只更换枚举。历史 schema 2/3 报告按历史框架读取，不改写旧报告或用新规则回填胜率。
