# 可持续分红基础估值采纳与兼容审查

2026-11-12，Asia/Shanghai，generator=codex。

用户本轮明确指示“采纳这版修订，检查与现有自动投研流程的兼容性后，同步到生产框架”。该授权承接本日初始适配报告及其§4.1A规则，采用同一规则正文，生产版只更正采纳状态和接续说明。

## 接口与方法

现有stock-research/v4只输出V50、明确P1/T1及按scope的控制。audit-v2允许other模型保存未舍入V50，完整DDM/FCFE专项计算留报告，已定向通过V50→P1和重复风险归属检查。新增估值无需轻量JSON或下游消费者字段。k_e及终值风险若已进估值锚，用multiple归属并说明模型位置，残余才入原折扣。

stock-research入口按实际冻结框架是否含§4.1A判适用，既有Codex/DSH提示词引导读取该技能并绑定两份方法哈希。元研究与变化检测入口补入分配证据接续，仍使用原七变量、重要变化项和分类。周更automation-2读取最新origin/main、canonical/compact及这两个入口，既有提示词可承接本次增补。

本次方法增加基础估值的分红计入和可核算交付要求，新旧方法并非整体语义等价。compatibility留空，旧冻结批次保留原输入、重试和恢复合同，发布前由framework_compatibility判needs_review并走原隔离流程。新批次应核为exact，采用新handoff且生命周期active。接口兼容不等于旧价格已按新法重评。

## 状态与历史接续

接续11/08已采用的市场来源、规则评估、5项pending及原触发时钟。旧reviews.methods保留原方法身份，required_completion_methods指向本轮方法，实际完成仍需报告/JSON及适用兼容凭证。旧withdrawn_sources与supersedes链继续有效。新增§4.1A的逐股状态为unknown，未形成虚假的触发或completed。

两份框架受限观测块逐字保留，不将方法采纳日期作为行情刷新日期。旧adaption-report保持proposed历史，新的change-decision-r2与handoff-r2记录本轮采纳。

## 验证依据与限度

前一轮已完成12项合成算术与接口检查，以及1341项全量离线回归和47项环境失败复验。此次另在最新origin/main隔离基线运行全量回归，并以实际方法文件进行旧/新快照、采纳生命周期和提示词绑定验证，具体回执见生产接续记录与output审计目录。

验证范围为结构、计算接口与流程接续。分红证据、主辅估值经济去重及收益有效性由后续逐股研究核验。没有调用真实证券研究、支付模型费用或发布公司报价。
