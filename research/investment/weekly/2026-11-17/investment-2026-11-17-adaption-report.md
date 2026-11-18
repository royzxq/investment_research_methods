# 个股调研框架更新结果

2026-11-17，Asia/Shanghai，generator=codex。

## 1. 更新结论

按用户明确授权完成本地最小方法修订；method_change=true、state_refresh=false、evidence_correction=false。当前分支codex/valuation-observation，本地采纳，未提交、合并、推送、重载调度或提升隔离价格。新增检查约束已采纳V50的论证，不给统一资本成本、增长、折扣或提价幅度。新准备合同two-price-controls/v10 / stock-research-audit/v7，轻量价格仍stock-research/v4。

## 2. 受影响模块

canonical §4.1D、compact §7明确五类中性假设、逐年生产资本与终值IC衔接、逐风险现金流/资本桥/资本成本/P1定位，以及联合路径和单项敏感性。审计新增neutral_review；runner/recovery/acceptance按新合同传递，新技能默认路由同步。无关规则与市场状态不改。

## 3. 操作定义与边界

所有V50非null的报告均需五类假设依据、反证、替代及选择，包括P1仍留空的报告。资本桥reconciled/approximate给逐期数值，检查资产滚动、期际衔接和期间顺序；现金购建/资产增加差异、范围转换与终值资本仍须经济审查。不能可靠精确对账时可说明代理或未覆盖项，不通过新增机械空价惩罚报告。不可估报告继续原留空尝试，不强迫给价。

风险表完整覆盖已计价风险，说明四个位置和独立残余；预期现金损失与系统性溢价不自动等同，也不因改ID证明独立。联合乐观或悲观假设均需支持及反面组合。敏感性绑定本次V50，核差额算术，实际计算和参数联动另由研究者复核；未能量化可明确原因与方向，不编数。

正例：有近期高投入和中长期效率改善的不同证据，保留有界中值及两侧替代。反例：把峰值投入永久化，又因相同现金回收风险提高WACC和P1折扣；或令CapEx长期低于DA却无资本效率衔接。边界：因真实融资尾部未决保留V50、P1留空；金融资产模型可说明生产资产滚动不适用；资本对账不精确不自动撤价。价差缩小并非验收目标。

## 4. 不应过度反应

R1–R22、D1–D8、原阈值、AND/OR、例外和解除条件保持；更低价格不能解除资格约束。正式公司报告、latest、原五项pending与撤回证据不改。此次同包复跑另有独立证据与方法快照，六个新模型均请求Astra/xhigh，不混入截止后事实；单次同配置仍有随机性，不能把输出差视为纯框架因果效应。

## 5. 新版框架

[canonical](../../../../framework/investment_framework.md)与[compact](../../../../framework/investment_framework_compact.md)；方法标识stock-two-price-controls-v2-etf-relative-v1-dividend-v1-capital-v1-dcf-v4。核心方法唯一保留在canonical；表格是检查接口，不另创投资规则。

## 6. 版本与采纳

| 文件 | 前/后完整SHA256 | 前/后方法SHA256 |
|---|---|---|
| investment_framework.md | `2b909852e5afacc1ea832a76540c04469439fb016692dc91c32bd7160e13fb32` → `288c122feebe8fc1fc0ac7016c30ddf6e8b889e410b33f5411d2ac878ef0bb98` | `6303f7f694f21805a2122c2db7a67b8539a00a37e741f214084ab2f602c86e7e` → `329eede537bae7691b14c9a52137002fe93e8ac74e0df50c6b8be8cabdcf731f` |
| investment_framework_compact.md | `2ad08f195bb6729dd8c7aea96ccaf85c1fa5504aa53cfd18beef90f0e0377d1e` → `7c1d26fea0862c49852f4471eb58ebb9ce36803959537e13135f49e57ebe4d6a` | `782ff89d54dab37e9652c8e6a8c11706379773e23fed3cd21176fe83aa24769d` → `7a9a6cb2e90236efb015e8f834f2620632f1a2df969bd85e47c18ff51420e379` |


旧输入来自11/16 adopted handoff；本日新handoff绑定当前两份实际正文，完整接续5项reviews、规则评估及withdrawn_sources，保持原日期。三股实验估值日11/16、方法实际修改日11/17，属于历史反事实复评，不声称当时已用新方法。未登记隔离实验为生产completed。

## 7. 实际验证

最终全量离线回归 **1410 项通过**（260.221秒）。框架治理、技能quick_validate与git diff --check通过。旧v1–v9九种prompt逐字一致，162组历史报告/JSON/计算展示与新增5组audit-v6展示不变。独立审阅发现期间顺序漏洞，已修复并增加边界；完整结果见[验证](evidence/neutral-validation.json)、[独立审阅](evidence/neutral-independent-method-review.md)及[处置](evidence/neutral-review-resolution.md)。第一轮定向测试2项因ps沙箱、2项旧默认版本断言失败，修正预期并经授权全量通过，未掩盖失败。

结构与算术测试不证明来源真实、经济中性或投资有效。终值IC真实组成、实际敏感性、精确盘前证据截止须单独核验。模型试验是实际CLI请求，但不属于离线测试；无新增市场数据API或交易。

## 8. 精简版同步

仅同步本次条款、方法标识与日期说明。两份全文的R/D引用序列、三个模板变量计数与状态JSON原字节保持；新增条款的对象、依据/反证、未知/代理、无新资格门槛、资本桥/折现去重、联合假设/敏感性及旧合同边界在compact均有承载。三项执行抽检覆盖“P1空但V50有价”“可设界资本对账”“核心缺口确实不可估”。不重新证明历史全文100%语义等价。

canonical 974→980行、133468→135527 UTF-8字节；compact 654→656行、89909→91381字节。治理检查只证结构；未改条目逐字保留。
