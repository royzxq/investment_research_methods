---
name: future-change-analysis
description: 期货元框架变化检测（流水线阶段②）：对比本次与上一次 meta future analysis 调研结果，判定是否需要更新期货执行框架，写入 research/<AS_OF_DATE>-change-decision.md。Use when asked to run the change-detection stage, or to standalone-compare two existing research reports without running the full pipeline.
---

# future change analysis（流水线阶段②）

## 输入

- `AS_OF_DATE`
- `CURRENT_META_RESULT`：本次 meta-future-analysis 产出的调研报告全文
- `PREVIOUS_META_RESULT`：上一次调研报告全文

由 `futures-weekly-review` 编排器调用时，`PREVIOUS_META_RESULT` 按以下规则查找：
1. 在 `research/` 下找文件名匹配 `*-market-research.md`、日期早于 `AS_OF_DATE` 的文件，取日期最近的一份
2. 找不到任何这样的文件时，退回 `research/baseline-market-research.md`

单独调用本 skill（不经编排器）时，由调用方直接给出这两份文本，不必套用上面的查找规则。

## 执行

1. 读取 `projects/future_change_analysis/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则与六步分析流程；代入上面三个输入变量
2. 只关注会改变交易重点、判断顺序、权重设置、阈值松紧的变化；不把措辞差异或单周噪音误判为框架级变化
3. 严格按 instruction 第六步给出的格式输出完整报告，末尾必须包含结构化字段 `FRAMEWORK_UPDATE_DECISION`（含 `update_needed: yes/no`、`update_level`、`decision_reason`）、`KEY_VARIABLE_CHANGES`、`UPDATE_FOCUS`、`DO_NOT_OVERREACT_ITEMS`

## 输出

- 把完整报告写入 `research/<AS_OF_DATE>-change-decision.md`
- 返回值：报告全文 + 解析出的 `update_needed`（yes/no），供编排器决定是否触发阶段③
