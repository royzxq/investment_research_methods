# 可持续分红基础估值兼容检查与生产接续

2026-11-12，Asia/Shanghai，generator=codex。用户明确采纳本日修订，并授权检查自动投研兼容性后同步生产。本次为定向方法维护，市场证据截止日保持2026-11-08。

## 生效内容

方法版本为 `stock-two-price-controls-v2-etf-relative-v1-dividend-v1`。canonical §4.1A 与 compact §7 明确分红可持续性、分配权利时点、股利折现及替代模型裁决、现金与留存桥和唯一计价。R22 未量化时，有依据的分红仍通过 V50 进入基础 P1。R22 可量化时共用预测并取更严格的回报约束，完整估值不能再叠加同一股息现值或重复奖励风险改善。

本轮采用的规则正文与初始修订一致，生产版只更新头部采纳状态与接续链接。初始 [adaption-report](../../weekly/2026-11-12/investment-2026-11-12-adaption-report.md) 保留 proposed 历史。本轮采纳见 [change-decision-r2](../../weekly/2026-11-12/investment-2026-11-12-change-decision-r2.md)、[不可变审查来源](../../weekly/2026-11-12/evidence/dividend-adoption-review.md) 与 [handoff-r2](../../weekly/2026-11-12/investment-2026-11-12-handoff-r2.json)。用户本次同步生产授权涵盖此单一 PR 的合并和本机部署，后续自动周更仍按原人工审核权限执行。

## 自动流程兼容

- 个股研究继续使用 stock-research/v4、stock-research-audit/v2 和 two-price-controls/v5，仍只交付 V50、明确 P1/T1 与独立 scope 控制。DDM/FCFE 用既有 `valuation.kind=other`、真实未舍入 V50 和专项计算，折现率或终值风险按既有归属明确吸收位置。无需新增 JSON 字段、迁移历史数据或修改下游消费者。
- stock-research 入口和估值/一致性 reference 依据实际冻结方法判断 §4.1A 是否适用。Codex/DSH 的既有提示词读取该入口、绑定框架哈希和已采用维护来源，Claude 兼容入口也接续同一技能。分红证据按 required_inputs 及既有补证机制取得，未给旧快照追加方法要求。
- 本机 launchd 服务 WorkingDirectory 为生产仓库，每次准备任务读取并冻结该仓框架。每日05:00排期、模型、额度、冷却及启动脚本均不变，文档更新无需重载或立即触发付费研究。
- 周度 automation-2 为 ACTIVE、周日02:00，从最新 origin/main 建工作树并读取 canonical/compact、元研究和变化检测项目入口。两份项目入口已补充分红证据接续及 state/evidence/method 分类边界，现有提示词即可承接，排期和提示词均无需修改。
- 新旧方法并非整体语义等价，compatibility 保持空。实际新快照为 exact、handoff 生命周期 active，旧11/08方法快照为 needs_review、生命周期 superseded。旧快照原字节不变，既有发布流程会保留隔离结果，避免未复核旧价被直接采纳为新方法结论。
- 原5项 pending、触发时钟、历史方法身份和撤回链保留，required_completion_methods 接续本轮方法。未生成公司 completed 凭证或解除 Gate，分红条款的逐股评估保留 unknown。

## 验证

基于最新 origin/main `3a16e84c27341ba17a75df2bd3e728c4f6dfc010` 建独立发布工作树，仅包含本次规则与接续。生产工作区的两个未发布开发提交及另有的启动脚本修改均不夹带。

1. 全量离线回归1317项通过，用已有 conda Python 执行，允许测试使用本机回环端口和进程检查，耗时314.404秒。未修改生产脚本或测试代码。
2. 12项合成算术/接口检查通过，覆盖 R22 缺输入仍传入 P1、减派、贴现率、分期与终值一致、同日派息/留存等值、特别股息资产扣除、有限期、永续参数域、R22只收紧、v4/audit-v2回读及重复风险/错误P1拒绝。
3. 实际两份框架及维护来源冻结、全部来源哈希校验、新旧兼容和生命周期检查通过。Codex、DSH、Claude 三端提示词均绑定新框架哈希、handoff-r2、v4/audit-v2/v5。此为离线提示词检查，未启动模型。首次快照检查漏传 audit 契约，被既有校验正确拒绝，补齐生产准备路径实际使用的 audit/request 参数后通过，失败副本留在审计目录。
4. 股票框架治理、stock-research 技能 quick_validate、handoff 来源校验与 git diff --check 通过。框架方法正文与已接受修订相同，原受限观测块逐字不变。受影响 compact 的适用性、公式域、权利时点、去重、缺口与 R22 衔接已核对，原 Gate/Terminal 等未受影响正文保留。完整保真复核范围见初始适配报告§8。

| 最终方法 | 完整SHA-256 | 方法指纹 | UTF-8字节 / 行数 |
|---|---|---|---|
| investment_framework.md | `b2ac2b44c38156d102f7c9bdb6a0a282819d66754428d2606a093adcc3246972` | `495394639994749dd17724e797e78f06b002c0f47c7b1513cd318549f856c377` | 112260 / 811 |
| investment_framework_compact.md | `ba3ec6af1aa4598db0cf2ed7e4285e1f39ca59f84825285cb886520979ad1062` | `2b2a1bf628e09ededbd2880b5957327bf873015ba8fbae3ead07dcbcbefb9aa4` | 74861 / 534 |

部署前已记录215份生产队列、索引、历史快照、业务CSV、配置、启动脚本及排期文件的哈希。最终 PR、远端合并提交、逐文件部署哈希及部署后不变性核验，以本机 [release receipt](../../../../output/audits/investment/2026-11-12/dividend-production/release-receipt.json) 为准，不以本报告存在推定发布完成。离线日志、算术和快照验证材料也保存在该审计目录。

这些验证覆盖结构、演示算术、输出接口和方法接续。DDM现金流来源、主辅模型的经济去重和未来分红可持续性仍需逐股取证，未验证收益有效性，也未调用真实证券API、付费研究或发布公司报价。

## 部署与恢复边界

发布使用单一框架 PR，合并后只把发布清单内文件同步到生产工作区，并核对其与远端合并版本及不可变方法副本一致。现有开发提交、运行配置、历史报告、队列与持仓数据保留，不对 dev 执行 reset 或整分支覆盖。

恢复时须逐项比对发布清单及部署前备份，不能覆盖后续修改。方法回退仍需新的明确采纳接续，并复核已有新方法产物的兼容性，不重写旧 handoff、冻结输入或业务报价。
