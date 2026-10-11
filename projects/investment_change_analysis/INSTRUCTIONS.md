# 股票维护变化检测 — Project Instruction

## 流水线定位与输入

阶段②：读取本次完整元研究 `{{CURRENT_META_RESULT}}`、可选上次已采用研究 `{{PREVIOUS_META_RESULT}}` 及其变化报告、现行已采纳 canonical，在 `{{AS_OF_DATE}}` 判断应刷新什么、纠正什么、审议什么。它不负责执行公司研究、修改框架或采纳方法；完整流程由 `investment-weekly-review` 入口接续，单阶段到输出结束。

七项输入保持：MAIN_CONTRADICTION、DOMINANT_RETURN_DRIVERS、KEY_CONSTRAINTS、PRIORITY_MECHANISMS、FRAGILE_NARRATIVE、TOP_MISTAKE_TO_AVOID、PRECHECK_ITEMS。

## 判定原则

1. 对每项同时做周环比和框架/现实一致性检查。时效失效、错引证据不必等宏观“显著变化”才纠正；单周新闻也不能自动推出新永久门槛。
2. **state_refresh**：在既有规则下更新状态、行情、日历和已知事实。**evidence_correction**：撤回或纠正错误证据与完成断言，并指明受影响结论。**method_change**：改变研究权重、逻辑、阈值、适用对象、动作、例外或解除条件。可同时存在，但不得用 light 名称把方法变化伪装成状态。
3. `update_needed` 仅为是否有 method_change 的兼容字段。没有方法变更，状态/纠错也必须列出并交回完整流程；不以 no 丢弃最新状态。
4. 读取历史报告、适配与必要 Git 采纳事实。上期观察项先辨认属于已采纳规则还是提案，再看 triggered/not_triggered/unknown/invalidated；提案触发仅支持重新审议，不直接升级规则。
5. 触发某个复评条件只创建 pending。completed 必须链接该公司对应日期、生成端的完整报告/JSON 配对，不能把“命中阈值”写成“已经执行一轮”。完成研究不代表账户执行。
6. 状态限制只作用于明确适用对象。临时买入冻结不自动证明公司不可估值；价值可估性、观察价位与买入资格分别判断，不强迫缺数据公司产出数字。
7. 无历史基线时不虚构周环比，仍用当前证据检查已采纳规则与现实。不存在已采用 handoff 不阻止研究，但不能把最新文件默认为已采纳。

## 六步分析

1. **复核旧观察项**：列规则/提案身份、采纳方法及来源、观察截止日、结果、受影响对象、待逐股复评和完成凭证。失效或错误证据明确撤回，不无限“再等等”。
2. **比较七项变量**：区分无变化、轻微、重要、结构性；各项写旧值、新值、证据截止日与变化方向。无基线则标不适用。
3. **解释研究含义**：影响哪些公司/机制，哪些受损、哪些受益；是否改变研究优先级或仅改变当前参数输入；解释经济传导，避免将市场整体风险等同于所有公司的价值损毁。
4. **分类与决策**：逐项标三类变化，分别说明理由。对已有规则有状态结果但正文未及时同步时，仍输出可采用的当前状态；未合并方法提案保留 proposed。
5. **方法审议**：每项方法变化说明 definition（时点、单位、AND/OR、等号、窗口、unknown、退出）、economic_reason、scope、positive_case、negative_case、boundary_case、compatibility_impact。缺定义保留提案，不进有效规则。按影响补历史样本/敏感性验证，不为每条定性规则强加全市场回测。
6. **交付接续**：列本期 state/evidence 输入、withdrawn_sources、需被替代的旧 handoff、待研究公司与有效方法。同日新证据使用整包统一 rN，不覆盖旧决策。

## 输出格式

沿用报告标题「元框架变化检测结果」与以下结构：

0. 上期预备观察项复核（采纳身份、触发证据、待复评/完成凭证）
1. 基本信息（研究日、证据截止、已采纳方法路径/哈希、比较报告路径/哈希）
2. 总结论（三类变化、方法级别、是否需正文修订、独立状态/纠错接续）
3. 新旧七变量比较表
4. 重要变化项（old_value/new_value/change_direction/change_type/importance_level/research_meaning/downstream_impact）
5. 方法变化审议（完整定义与边界案例，或无方法变化）
6. 不应过度反应、待复评、撤回与兼容影响
7. 结构化输出

```yaml
MAINTENANCE_CLASSIFICATION:
  state_refresh: true_or_false
  evidence_correction: true_or_false
  method_change: true_or_false
FRAMEWORK_UPDATE_DECISION:
  update_needed: yes_or_no  # 仅等于 method_change
  update_level: none_or_light_or_significant_or_partial_rebuild
  decision_reason: ""
KEY_VARIABLE_CHANGES: []  # 每项含kind，研究含义用research_meaning
UPDATE_FOCUS: []
DO_NOT_OVERREACT_ITEMS: []
RULE_EVALUATIONS: []
PENDING_COMPANY_REVIEWS: []
COMPLETION_EVIDENCE: []
WITHDRAWN_SOURCES: []
```

完整流程随后按 skill 的 maintenance-handoff 契约采用状态与纠错；单阶段比较只保存这份判断，不修改方法、不自动采用或发布。
