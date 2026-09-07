---
name: future-change-analysis
description: 期货元框架变化检测（流水线阶段②）：对比本次与上一次调研，判定是否更新框架，并生成当期执行诊断；变化结论与诊断分别写入 research/ 下的日期文件。Use when asked to run the change-detection stage, or to standalone-compare two existing research reports without running the full pipeline.
---

# future change analysis（流水线阶段②）

## 输入

- `AS_OF_DATE`
- `CURRENT_META_RESULT`：本次 meta-future-analysis 产出的调研报告全文
- `PREVIOUS_META_RESULT`：上一次调研报告全文
- `PREVIOUS_CHANGE_DECISION`：上一次的变化检测报告全文（与 `PREVIOUS_META_RESULT` 同日期的 `<该日期>-change-decision.md`；找不到就视为无）
- `CURRENT_FRAMEWORK`：`framework/futures_framework.md` 现行全文（跳过顶部 HTML 注释行）
- `EXECUTION_EVIDENCE`：可用行情输出、账户/挂单快照、逐候选计划和历史诊断的来源清单；单独调用未提供时读取已有材料并明确缺口，不假定账户空仓

由 `futures-weekly-review` 编排器调用时，`PREVIOUS_META_RESULT` 按以下规则查找：
1. 在 `research/` 下找文件名匹配 `*-market-research.md`（**排除 `investment-` 前缀的股票轨道文件**）、日期早于 `AS_OF_DATE` 的文件，取日期最近的一份
2. 找不到任何这样的文件时，退回 `research/baseline-market-research.md`

单独调用本 skill（不经编排器）时，由调用方直接给出这些文本，不必套用上面的查找规则。

## 执行

0. 先读取 `framework/FUTURES_DATA_PROTOCOL.md`、`projects/future_change_analysis/INSTRUCTIONS.md` 与 `projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md`。在任何市场比较前，核对新旧证据的完整年份、观测日、单位与比较口径，并处理 `EVIDENCE_CORRECTIONS`、`DATA_FEASIBILITY`；跨年数据、错误解释的修复不算市场反转。随后基于有效证据、适用规则与豁免生成当期执行诊断：对确有必要缺项的活跃候选按共享模板保留 `incomplete`，长期不可得专业依赖的模型单列 `research_only`，增强缺项不拖累其他模型。无论后续是否更新框架都不可跳过诊断；账户未知不阻止前面的研究/评分，最终风险空值与所有状态严格采用共享模板，不复制风险或评分公式
1. **上期预备观察项复核（证据纠错后、市场比较前）**：读 `PREVIOUS_CHANGE_DECISION`，找出其中带复核条件的遗留项（"预备观察项"、"下周复核"、"若 X 则触发更新"等），逐条判定本周是否已触发，在报告里新增一节「0. 上期预备观察项复核」给出处置（已触发 / 未触发 / 已失效 / 转研究观察），**不许静默丢弃**。旧证据失效须明确撤回并重评；长期无法取得必要专业数据或所属品种已休眠时，可归档为 `research_only` 并保留原因、复活条件，不能每周自动顺延。仅适用、证据有效且原预设确为框架更新条件的条目已触发，才构成 `update_needed: yes` 的依据（级别按预设，未预设从 light 起步）；纯研究待补或数据修复不自动触发改规则
2. 读取 `projects/future_change_analysis/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则与六步分析流程；代入上面的输入变量做周环比对比
3. **框架-现实一致性检查（第二触发轴）**：对照 `CURRENT_FRAMEWORK` 里的 regime 性设定（机制档位、地缘轴定位、precheck 门、当期纪律清单等），判断本周调研结果是否与框架现状假设直接矛盾或错配已明显累积——即使周环比变化不大，框架假设与现实的错配同样构成触发依据（防温水煮青蛙）
4. **反摇摆护栏**：若因新市场证据推翻现行框架在最近 1-2 周内刚做出的方向性设定（档位升降、轴定位变更、precheck 门改造等），必须有与该路线相符、日期/口径有效的价格行为或公开硬数据支持，不能仅凭叙事或单条新闻；且报告中必须专门论证"为什么这不是对上周更新的摇摆式回滚"。达不到这个证据标准 → 保持尚有有效依据的设定，并将可核验项写成带触发条件的观察项。**纠正错误数据、错误规则适用性与不可实施的数据依赖不受此护栏限制**，不得以反摇摆为由保留已证伪的依据；必要专业数据长期不可得的路线按协议转研究观察，不无限延期
5. 只关注会改变交易重点、判断顺序、权重设置、阈值松紧的变化；不把措辞差异或单周噪音误判为框架级变化
6. 严格按 instruction 第六步给出的格式输出完整报告（外加第1步的「0. 上期预备观察项复核」节），末尾必须包含结构化字段 `FRAMEWORK_UPDATE_DECISION`（含 `update_needed: yes/no`、`update_level`、`decision_reason`）、`KEY_VARIABLE_CHANGES`、`UPDATE_FOCUS`、`DO_NOT_OVERREACT_ITEMS`、`DATA_FEASIBILITY`、`EVIDENCE_CORRECTIONS`、`EXECUTION_AUDIT`（路径/框架版本/活跃与研究观察范围/证据结论）；新增“等下周验证”事项必须可实际核验并带明确触发条件，长期不可取得的数据不再列为活跃待办

## 输出

- 把完整报告写入 `research/<AS_OF_DATE>-change-decision.md`
- 将独立诊断写入 `research/<AS_OF_DATE>-execution-audit.md`；历史连续空仓/规则有效性缺乏完整账时不作确定归因
- 返回值：报告全文（完整透传并更新 `DATA_FEASIBILITY`、`EVIDENCE_CORRECTIONS`）+ 解析出的 `update_needed`（yes/no）+ `CURRENT_EXECUTION_AUDIT`（诊断全文和路径），供编排器决定是否触发阶段③
