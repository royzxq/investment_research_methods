# 估值输入桥：定向变化决策

本地dev已合并 `9c2209d7f73c02a3c227c786460269468211770e`，用户明确授权review通过后本地合并；不推送、不启动全量调研、不更新正式报价。本次为method_change，不生成新的全市场事实，原11/15市场报告和观察块原样复用。

新冻结controls-v8/audit-v5支持显式现金税、生产性资本和时间偏移、五类输入依据及未决折扣；原v1–v7按冻结合同恢复。利润恢复/费用/PE、资本归属及折扣的具体假设仍由个股补证，不能以规则修复自动上调。阿里/小米隔离回归区分等价迁移、税计算纠错和经营假设变化，采纳V50/P1为null。赤峰原未决没有复评或解除。

原5项pending及4项撤回来源继续保留，触发日、证据截止、历史方法和已有状态不变；未来完成用新方法核验，隔离诊断无正式acceptance，不能登记completed。旧方法兼容凭证留在原handoff，不外推为新方法对旧估值等价。

依据：[ADR](../../../../docs/adr/ADR-20261115-valuation-input-bridges.md)、[隔离报告](../../studies/valuation-revisions/2026-11-15-r5/report.md)、[review](../../studies/valuation-revisions/2026-11-15-r5/review.md)。本次部署仅本地dev，未推送远端。
