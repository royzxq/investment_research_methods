# 个股调研框架更新结果

2026-11-17，Asia/Shanghai，r4，generator=codex。

## 1. 更新结论

用户授权提交红利拆分、合入本地 dev 并完成兼容检查。合并采用红利分支的策略边界与 dev 的中性估值校准。分类为 method_change，市场证据仍截止原报告所列日期。

## 2. 受影响模块

共享§4.1D承接 dev 的完整中性校准，股票与红利 compact、技能和输出模板同步。原股票只保留 R9 迁出索引，红利估值专用规则仍位于 HD4A/HD6。prepare、运行及恢复同时支持新旧冻结合同。

## 3. 修改说明

以经营成长为主持有目的的公司走非红利，即使有现金分红。以长期现金分配为主的公司执行红利质量及估值专用规则，并用适用模型完成中性校准。金融红利使用监管资本与权益估值，遇模型不适用的生产资产对账须说明原因。已有 V50、P1 留空时仍做中性校准；核心缺口仍按原可用性规则处理。中性校准用于核对假设、已计风险与替代情景。

## 4. 边界与历史

既有市场状态、原持仓限制、5项待复评、4项撤回来源与25项历史评估依原证据和日期接续。两方同日文件名冲突，dev 的首版维持原路径，红利原首版与原复审 r2 分别安置为 r2、r3。仅重新绑定移位的记录与链接，冻结方法正文逐字节保留。原提交保存迁移前文件和路径。

## 5. 新版框架

[非红利 canonical](../../../../framework/investment_framework.md) · [红利 canonical](../../../../framework/dividend_framework.md) · [共享规则](../../../../framework/stock_research_common.md) · [红利报告模板](../../../../framework/dividend_report_template.md)

## 6. 版本与采纳

合并后方法标识为 `stock-strategy-split-v2-common-v3-dcf-v4`。本地采纳绑定六文件及其 SHA-256。[r4 采纳记录](investment-2026-11-17-handoff-r4.json) · [dev 原中性校准记录](investment-2026-11-17-handoff.json) · [红利原复审记录](investment-2026-11-17-handoff-r3.json)

## 7. 验证边界

新六文件快照使用 controls-v10 / audit-v7，价格 JSON 为 v4。历史两文件快照和早期六文件 v2 继续用冻结的各自合同，早期红利批次仍可用 v9 / audit-v6 恢复。方法差异仍交发布前复核。兼容检查覆盖本地冻结、提示、恢复、治理与审计。

## 8. 精简版同步

[非红利 compact](../../../../framework/investment_framework_compact.md)同步 dev 中性校准约束；[红利 compact](../../../../framework/dividend_framework_compact.md)引用同一共享定义并保留 HD4A 分红计算和 HD6 利差的专用边界。
