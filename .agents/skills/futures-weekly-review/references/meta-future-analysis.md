# 期货品种研究（阶段①）

## 输入与执行

- 输入 AS_OF_DATE、实际框架修订、已采纳前期报告与可用 EXECUTION_EVIDENCE；未提供则明确缺口，不假定行情最新或账户空仓。完整/刷新流程的发现与取数遵循 [刷新和接续](refresh-and-handoff.md)。
- 先读 `framework/FUTURES_DATA_PROTOCOL.md`、compact 导航及 `projects/meta_future_analysis/INSTRUCTIONS.md`，方法和参数回 canonical。
- 先扫描全部已知存量计划/持仓的相关事件、经济反证、止损和期限，再扫描 MA/RB/M/SR/CF 价格信号与最小证据，按品种写“主因—支持—最强反证—本周变化”，重点 M/RB。存量扫描本身用于发现变化，不能等机械刷新先发现新信号才做；账户未知输出条件管理，不推定仓位。
- 仅 T 顺势与 V 经济回归；条件引用 canonical。市场主因变化、相反方向的新信号和研究优先级变化使用现行规则处理，不先改方法。事件与季节只作相关证据及执行边界。
- 按根 AGENTS 使用实际检索和原文。保留完整年份、观测日、发布日、单位与可比口径；先撤回错证据，再比较市场变化。每项缺失指标最多两个公开来源，增强缺失不否决全池，必要专业依赖长期不可得列 research_only 及恢复条件。
- 本阶段形成候选研究依据，最多两个新机会深入由执行审计成案，存量复核不受此限；缺账户不停止公共研究。按 [V 观察锚维护](refresh-and-handoff.md#v-观察锚维护)为有证据基础的组合建立未来适用锚，保留已有锚、失效或续期记录；不以缺锚结束每一轮 V 研究，也不要求每期必须成案。只研究模式到此结束，不自动进入方法适配。

## 输出

按 instruction 保存 `research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-market-research.md` 或不覆盖原稿的修订。返回全文与路径作为 CURRENT_META_RESULT，保留 PRICE_SCREEN、PRODUCT_DRIVERS、DATA_FEASIBILITY、EVIDENCE_CORRECTIONS 以及兼容的结构化摘要字段。MAIN_CONTRADICTION 可为“品种分化，无统一主因”或 null，不是所有品种共同方向门。
