# 期货周度变化判定 · 2026-11-15

本期以实际 origin/main `ccc23ebc82357ee4bb91d0df4e2d4b6eb29056ca` 的 v3.0 / 维护 v2 执行，严格前期基线为 11/08 已采纳研究 r2。11/08 真实 API 未认证、行情只接历史 10/30，本期真 API 取到完整 11/13 数据。11/06 对同比价来自本轮同合约日线。 [本期市场研究](2026-11-15-market-research.md) · [本期执行审计](2026-11-15-execution-audit.md) · [共享裁决](evidence/continuity-reconciliation.json)

## 三类处置

|类别|结论|处置|
|---|---|---|
|状态刷新|yes|恢复本期真实行情和三所日期核对，四个 T 未触发，SR2701 空头价格触发。按现行规则核 11/16 夜盘末失去突破侧、撤销原入场用途及 11/17 事件阻断。RB 条件研究止损更新，三 V 的两腿有效原料恢复，均缺合格事前经济锚。|
|证据纠错|yes|新取得的同合约完整价格排除 MA 10/13 原入场带与 RB 10/27 原参考价。保留原稿、原 ID、登记和截止，修订的是既有备选路径的价格可达性。RB 10/27 其他原带报价仍可能，从真实成交或条件价分别复算。|
|方法变更|no|事件与 20 日期限、合约距离、跟踪止损、经济锚已有明确规则。本轮问题来自价格缺口与历史路径假设，现规则可以处理。源码与参数无需改变。|

## 可比变化

M 11/06 库存可比样本去库，但仍高，WASDE 对旧空头反向；另一油厂口径方向不同。旧 M 取消状态不变。RB 11/12 转供需同降、继续去库，11/16 的统计发布只在具体需求传导上纳入复核；旧入场到期，实仓未知。MA 港库再累，厂库微降；旧计划在两完整路径中的备选可达性已重评。SR 产量预测上修和云南开榨为新空经济证据，广西陈糖去库与全球紧供限制强度。CF 国内新棉集中供给，棉现货与纱价分化。当期 V 结算不能直接改变经济判定。 [公开出处](evidence/m-rb-public.md) · [其他品种出处](evidence/ma-sr-cf-public.md)

## 证据撤回

- MA 原 10/13 假设入场衍生的 11/09 是机械日历上限。新取得 MA2701 的 10/13 高 3278，小于全原带下限 3289，撤回该方案作为原计划可实现的候选路径。10/12 尚有日线区间交集，其 11/06 时间界与更早止损仍有效用于诊断。真实退出未知。
- RB 10/27 原参考 3047 高过当日 3044，只撤回这个价格的可达性。原带 3034–3044 的日区间交集按实际假设价重算初始 SL，其后截至 11/13 未触当时条件 SL，11/13 收盘更新下场参考至 3059。其余早期、期限、账户和风险条件分别评估。
- 11/08 已撤的 RB `remaining_window` 继续为 expired，M 同日原登记冲突按 r2，MA 旧产业 G2 通过继续撤回。上期 WASDE 未发布、场次未核属于当时的资料状态，本期补证，不反向修改原稿。 [条件路径与原料](evidence/holding-path-review.json)

## 接续

SR 原信号入场用途已撤。下一次日频只核独立新信号及实际报价，11/17 起按直接事件窗。若存在旧 RB 实仓，按真实 Entry/有效 SL 和更早退出界复核，11/20 与 11/23 是不同原入场日的条件上限。账户、容量、总机会和收益保持 null。

```yaml
CHANGE_CLASSIFICATION:
  state_refresh_needed: yes
  evidence_correction_needed: yes
  method_change_needed: no
FRAMEWORK_UPDATE_DECISION:
  update_needed: no
  update_level: none
  decision_reason: "当前固定规则可正确处理行情恢复、场次、原价可达性与事件"
STATE_REFRESH:
  affected_scope: [MA, RB, M, SR, CF, 有序跨期对, 历史候选]
  completed_actions: [刷新行情至11月13日, 复核交易日与事件, 复算三条旧计划, V锚维护]
  current_report_refs: [2026-11-15-market-research.md, 2026-11-15-execution-audit.md]
KEY_VARIABLE_CHANGES:
  - variable_name: 当前 T 价格覆盖
    old_value: 11月08日当前行情unknown
    new_value: 实测四个no_signal及SR2701空头价格触发
    change_type: state_refresh
    trading_meaning: "SR价格触发成立，夜盘末失去突破侧，原入场用途撤销"
    downstream_impact: "本期仅深入一条新候选"
  - variable_name: 旧计划条件路径
    old_value: "MA 10月13日备选，RB 10月27日参考3047"
    new_value: "MA全带不可达，RB参考价不可达但低价区间仍有日线交集"
    change_type: evidence_correction
    trading_meaning: "需按同合约日线重新计算条件止损"
    downstream_impact: "原登记和有效期不变"
EVIDENCE_CORRECTIONS:
  - original_claim: "MA 10月13日原计划备选价格可达"
    correction_basis: "MA2701 原料最高3278低于3289"
    affected_decisions: [MA原入场备选和条件退出]
    reassessment_result: "该日原带不可达"
  - original_claim: "RB 10月27日用原参考3047模拟可达路径"
    correction_basis: "RB2701 当日最高3044"
    affected_decisions: [RB备选参考路径和条件止损]
    reassessment_result: "仅对3034–3044的报价范围复算"
DATA_FEASIBILITY:
  - scope: 五T行情
    data_feasibility: available
    missing_required_inputs: []
    unavailable_enhancements: [逐场成交与完整盘口]
    scope_change: "11月13日实测"
    recovery_condition: null
  - scope: SR2701执行
    data_feasibility: temporary_gap
    missing_required_inputs: [实时可执行报价, 有依据的执行压力, 真实账户]
    unavailable_enhancements: []
    scope_change: "11月17日已确定事件阻断"
    recovery_condition: "等待独立新信号，再核适用场次与账户"
  - scope: MA/RB/SR V经济模型
    data_feasibility: research_only
    missing_required_inputs: [事前经济区间, 可交割成本, 可核收敛]
    unavailable_enhancements: []
    scope_change: "两腿行情已恢复"
    recovery_condition: "获得分月实物流与有效成本输入后，仅前瞻冻结"
METHOD_CHANGE_EVIDENCE: []
UPDATE_FOCUS: []
DO_NOT_OVERREACT_ITEMS: [价格恢复无需调参, 条件止损不等于实际成交, V月差不视为后见锚]
EXECUTION_AUDIT:
  path: research/futures/weekly/2026-11-15/2026-11-15-execution-audit.md
  framework_version: v3.0
  coverage: partial
  active_scope: [五T, 三V研究, 三条旧案复核]
  research_only_scope: [三个V经济模型, 旧进口高频专用模型]
  summary: "账户及执行未全覆盖，机会总数未知"
```
