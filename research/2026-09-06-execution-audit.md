# 2026-09-06 期货执行诊断

**当前只能确认研究未完成且存在已知否决，不能从现有材料得出“市场建议空仓”或“没有机会”。** 本次按待合并的 v2.21 做定向重评，行情来自本地 `1.txt` 的9月4日快照，市场状态沿用9月5日存档；没有重跑市场调研，也没有补造实际账户记录。

实际持仓状态为 `unknown`。旧输出“当前空仓 / 无登记的方向性单边”只反映脚本登记，未提供带时间戳的完整账户与挂单快照。全部记录的最终手数为 `null`，总体机会数也为 `null`；这与经过完整核验后算出的零手含义不同。

| 已观察记录 | 本次状态 | 已有证据与缺口 |
|---|---|---|
| MA2610−MA2701，A、方向未定 | incomplete | 分位100、价差+313只是研究筛选；模式、许可、真实SL/TP及独立证据未齐 |
| RB2610−RB2701，A高分位筛选 | no_signal | 分位61，未触发该筛选；其他策略、方向与后续风险门未完成 |
| SR2701−SR2705，A高分位筛选 | no_signal | 分位0，未触发该筛选；本次未开放低分位对称策略 |
| MA2701，方向性多头、策略待定 | incomplete | SC周涨护栏与#30冷却已有记录，其他门及完整计划/账户核验仍缺 |
| MA2701，方向性空头、策略待定 | incomplete | #26已有否决记录，未据此声称其为唯一阻断 |
| M2701，独立备选、策略/方向待定 | incomplete | 趋势参考指标存在，独立供需、策略、计划及账户输入缺失 |
| SR2701，B季节做多候选 | incomplete | 产销/库存/榨季及专属门缺乏完整证据，不从月差0分位推断方向 |
| CF2701，B季节做多候选 | incomplete | 季节窗口、轮储、独立证据及真实交易计划未齐 |

旧版“MA到50分位风险3,500元、可做1组”失效，RB/SR同口径风险与手数也失效。50分位只是参考，不能充当通用止损。A的 `reversion` 与 `continuation` 必须分别审查；高分位做空回归的协议定义不代表本期触发或解禁，continuation没有显式许可也不能开仓。

风险容量只引用 canonical Step5及 `scripts/futures_risk.py`。当前配置为单笔上限5,250元、常规全账户上限5,250元、低敞口全账户上限2,625元；低敞口只对账户上限作用一次，结构也受该上限。实际净值、存量风险、挂单预留、保证金未核验，故没有对这些候选运行真实最终容量计算。金额预算先应用适用系数、最终一次取整，不能沿用旧输出整数手数再逐层折半。

现有材料没有完整历史候选账/成交账，不能证明连续八周空仓、计算规则省下或错失的收益，也不能把这里的记录数当独立机会数。后续优先补MA完整裁决、账户/挂单快照和农产品独立证据；负责人和截止日尚未指定，下面据实留空。

本地行情来源指纹：`1.txt` 的 SHA-256 为 `9350de5094e1c687a28be99e8eeb552c3301f72fa710eb550e4636c95f07f23e`。原文件为用户本地留存、未纳入本次提交；本报告已摘录所用价差、分位与护栏读数，不能据此声称已独立重取行情。

## 结构化记录

以下 `trade_date` 为行情观测交易日；规则版本为本次拟议版本，不代表在9月4日曾按新规则作出或执行这些决策。MA单边护栏的状态记录来自9月5日存档，保留其不同时间来源。

```yaml
audit_schema_version: 1
as_of_date: "2026-09-06"
assessment_scope: "proposed_framework_reassessment"
framework:
  path: "framework/futures_framework.md"
  version: "v2.21"
  revision: "working_tree on codex/futures-execution-consistency; 尚未合并；不是9/4实际决策版本"
snapshot:
  market_trade_date: "2026-09-04"
  market_captured_at: null
  source_artifacts:
    -
      path: "1.txt"
      reported_as_of: "2026-09-06"
      version: "框架v2.20 / 数据脚本v1.8"
      sha256: "9350de5094e1c687a28be99e8eeb552c3301f72fa710eb550e4636c95f07f23e"
      scope: "本地原始控制台输出；本次未重拉线上行情"
    -
      path: "research/2026-09-05-adaption-report.md"
      scope: "仅沿用既有市场/护栏状态，本次未作新的市场调研"
    -
      path: "scripts/futures_risk.py"
      scope: "v2.21数值校验入口；无完整当期交易/账户输入，未生成真实候选容量"
  invalidated_legacy_outputs:
    - "A分位≥85的主仓触发标签"
    - "A到50分位锚的风险/手数：MA3500/1、RB140/37、SR1180/4"
    - "旧单腿手数不是v2.21最终手数"
    - "当前空仓/无登记方向性单边不是账户核验"
  account:
    actual_position_status: "unknown"
    verified_at: null
    evidence: null
    equity: null
    open_positions: null
    pending_orders: null
    existing_risk: null
    reserved_order_risk: null
    margin_available: null
    configured_equity: 150000
  configured_risk_limits:
    single_trade_cap: 5250
    portfolio_cap_normal: 5250
    portfolio_cap_current: 2625
    source: "framework/futures_framework.md 0)与Step5；只是当前配置，实际净值/占用待核"
coverage:
  completeness: "partial"
  covered_scope:
    - "3组A高分位筛选"
    - "MA2701方向性多空的部分门"
    - "M2701独立备选缺口"
    - "SR2701/CF2701 B季节候选缺口"
  missing_scope:
    - "全部适用策略/方向的完整逐候选账"
    - "账户/挂单与部分成交预留风险"
    - "人工现货/库存/供需及执行门数据"
    - "历史逐周实际决策、成交与净收益"
  total_executable_opportunities: null
  historical_trade_performance: "unavailable"
candidates:
  -
    candidate_id: "2026-09-04|MA2610-MA2701|A|unknown|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "MA2610"
      - "MA2701"
    strategy: "A"
    hypothesis: null
    direction: "unknown"
    signal: "unknown"
    signal_basis: null
    screening_evidence: "同期分位100.0%，价差+313元/吨；只是高分位研究候选"
    evaluated_checks:
      - "读取旧输出的合约、交易日、价差、分位及两腿20日均量"
    evaluation_order:
      - "行情快照"
      - "模式/方向/计划"
    all_blockers: []
    unknown_checks:
      - "reversion或continuation及本期许可/方向尚未裁决"
      - "真实SL/TP缺失；不能用50分位锚计风险"
      - "独立微观证据及MA适用①门"
      - "最晚退出日/持有期与近腿滚动边界"
      - "双腿执行和一腿未成交预案"
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: null
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "incomplete"
    not_evaluated_after_no_signal: []
    evidence_refs:
      - "1.txt:31-38"
      - "framework/futures_framework.md Step5 策略A"
  -
    candidate_id: "2026-09-04|RB2610-RB2701|A|unknown|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "RB2610"
      - "RB2701"
    strategy: "A"
    hypothesis: null
    direction: "unknown"
    signal: "not_triggered"
    signal_basis: "仅高分位A筛选：同期分位61，未达研究筛选门槛；不评估未开放的低分位对称策略"
    screening_evidence: "同期分位61"
    evaluated_checks:
      - "高分位A筛选"
    evaluation_order:
      - "高分位A筛选"
    all_blockers: []
    unknown_checks:
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: null
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "no_signal"
    not_evaluated_after_no_signal:
      - "方向/模式与完整计划"
      - "独立微观证据/品种门"
      - "账户及最终风险容量"
      - "该品种其他策略与方向"
    evidence_refs:
      - "1.txt:40-47"
      - "framework/futures_framework.md Step5 策略A"
  -
    candidate_id: "2026-09-04|SR2701-SR2705|A|unknown|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "SR2701"
      - "SR2705"
    strategy: "A"
    hypothesis: null
    direction: "unknown"
    signal: "not_triggered"
    signal_basis: "仅高分位A筛选：同期分位0，未达研究筛选门槛；不评估未开放的低分位对称策略"
    screening_evidence: "同期分位0"
    evaluated_checks:
      - "高分位A筛选"
    evaluation_order:
      - "高分位A筛选"
    all_blockers: []
    unknown_checks:
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: null
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "no_signal"
    not_evaluated_after_no_signal:
      - "方向/模式与完整计划"
      - "独立微观证据/品种门"
      - "账户及最终风险容量"
      - "该品种其他策略与方向"
    evidence_refs:
      - "1.txt:49-56"
      - "framework/futures_framework.md Step5 策略A"
  -
    candidate_id: "2026-09-04|MA2701|unknown|long|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "MA2701"
    strategy: null
    hypothesis: null
    direction: "long"
    signal: "unknown"
    signal_basis: null
    screening_evidence: "MA2701周涨8.56%；SC2610结算价周涨15.33%。未据此判定完整做多信号"
    evaluated_checks:
      - "SC周涨方向性多头护栏"
      - "#30既有涨停冷却记录"
    evaluation_order:
      - "SC周涨方向性多头护栏"
      - "#30既有涨停冷却记录"
    all_blockers:
      -
        rule_id: "MA原油周涨>8%护栏"
        basis: "1.txt显示SC2610周涨15.33%，仅适用于MA方向性多头"
        data_date: "2026-09-04"
      -
        rule_id: "#30"
        basis: "9/5存档记录甲醇9/2涨停、顺向新开冷却至9/7；本次沿用该记录，未重拉逐日行情"
        data_date: "2026-09-05"
    unknown_checks:
      - "具体已许可策略路由、信号、独立证据"
      - "#16限隔夜/低敞口及#20/#21等其余适用门完整核验"
      - "当日ATR重校准与事件窗口最新状态"
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: "MA原油周涨>8%护栏"
    only_blocker: false
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "incomplete"
    not_evaluated_after_no_signal: []
    evidence_refs:
      - "1.txt:83"
      - "1.txt:89"
      - "research/2026-09-05-adaption-report.md:297"
  -
    candidate_id: "2026-09-04|MA2701|unknown|short|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "MA2701"
    strategy: null
    hypothesis: null
    direction: "short"
    signal: "unknown"
    signal_basis: null
    screening_evidence: null
    evaluated_checks:
      - "#26能源方向性空头门"
    evaluation_order:
      - "#26能源方向性空头门"
    all_blockers:
      -
        rule_id: "#26"
        basis: "沿用9/5市场状态：①非缓和证真，能源链方向性空头新开否决"
        data_date: "2026-09-05"
    unknown_checks:
      - "具体策略/信号与近远路由"
      - "缓和门最新完整证据和结构确认"
      - "当日ATR重校准、最新事件及其余执行门"
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: "#26"
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "incomplete"
    not_evaluated_after_no_signal: []
    evidence_refs:
      - "research/2026-09-05-adaption-report.md:293"
      - "framework/futures_framework.md #26"
  -
    candidate_id: "2026-09-04|M2701|unknown|unknown|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "M2701"
    strategy: null
    hypothesis: null
    direction: "unknown"
    signal: "unknown"
    signal_basis: null
    screening_evidence: "ADX14=36.7、距离单合约近似H250为0.99%；单合约样本154，不足以证明完整趋势/独立供需信号"
    evaluated_checks:
      - "行情趋势参考指标"
    evaluation_order:
      - "行情趋势参考指标"
      - "独立备选路由证据"
    all_blockers: []
    unknown_checks:
      - "明确策略/方向"
      - "美豆/南美天气/国内压榨利润等独立供需证据"
      - "WASDE官宣日及实际前后窗口核验"
      - "高波与升核心首期系数适用依据"
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: null
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "incomplete"
    not_evaluated_after_no_signal: []
    evidence_refs:
      - "1.txt:74"
      - "1.txt:85"
      - "1.txt:102-105"
      - "framework/futures_framework.md 1.5 M2701"
  -
    candidate_id: "2026-09-04|SR2701|B|long|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "SR2701"
    strategy: "B"
    hypothesis: null
    direction: "long"
    signal: "unknown"
    signal_basis: null
    screening_evidence: null
    evaluated_checks:
      - "常驻备选B路由"
    evaluation_order:
      - "B路由"
      - "季节与独立证据"
    all_blockers: []
    unknown_checks:
      - "榨季窗口、产销率/库存与进口利润独立证据"
      - "国储抛储与品种专属门"
      - "完整季节策略触发与首期系数"
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: null
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "incomplete"
    not_evaluated_after_no_signal: []
    evidence_refs:
      - "framework/futures_framework.md 1.5 SR2701"
      - "1.txt:75"
      - "1.txt:86"
  -
    candidate_id: "2026-09-04|CF2701|B|long|v2.21"
    opportunity_id: null
    trade_date: "2026-09-04"
    contracts:
      - "CF2701"
    strategy: "B"
    hypothesis: null
    direction: "long"
    signal: "unknown"
    signal_basis: null
    screening_evidence: null
    evaluated_checks:
      - "常驻备选B路由"
    evaluation_order:
      - "B路由"
      - "季节与独立证据"
    all_blockers: []
    unknown_checks:
      - "新旧作季节窗口及独立证据"
      - "国储轮储公告及内外棉价差核验"
      - "完整季节策略触发与首期系数"
      - "当期完整账户/持仓/挂单及部分成交预留风险快照"
      - "真实Entry/SL/TP与费用、滑点、压力情景"
      - "保证金/限仓、gap及全部适用执行门"
    first_blocker: null
    only_blocker: null
    plan:
      entry: null
      stop: null
      targets: null
    risk_evaluation:
      canonical_ref: "framework/futures_framework.md Step5 / #31"
      calculator_ref: "scripts/futures_risk.py"
      result: null
    final_lots: null
    status: "incomplete"
    not_evaluated_after_no_signal: []
    evidence_refs:
      - "framework/futures_framework.md 1.5 CF2701"
      - "1.txt:76"
      - "1.txt:87"
unresolved_items:
  -
    item: "MA A模式/方向和完整计划裁决"
    owner: null
    due_at: null
    required_evidence:
      - "reversion许可与①缓和门；continuation须显式许可"
      - "真实Entry/SL/TP、独立微观证据、费用/滑点、压力情景、最晚退出日"
      - "双腿执行预案"
    resolution: "pending"
  -
    item: "账户状态及风险预算占用核验"
    owner: null
    due_at: null
    required_evidence:
      - "带时间戳完整净值/持仓/挂单及部分成交快照"
      - "存量止损风险、预留风险与可用保证金"
    resolution: "pending"
  -
    item: "农产品独立证据及季节策略计划"
    owner: null
    due_at: null
    required_evidence:
      - "M独立供需链"
      - "SR产销/库存/榨季"
      - "CF季节及轮储信息"
      - "实际策略触发、计划与全部适用门"
    resolution: "pending"
```
