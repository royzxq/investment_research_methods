---
name: investment-change-analysis
description: 股票元框架变化检测（流水线阶段②）：对比本次与上一次 meta investment analysis 调研结果，判定是否需要更新股票投资分析框架，写入 research/investment-<AS_OF_DATE>-change-decision.md。Use when asked to run the change-detection stage, or to standalone-compare two existing research reports without running the full pipeline.
---

# investment change analysis（流水线阶段②）

## 输入

- `AS_OF_DATE`
- `CURRENT_META_RESULT`：本次 meta-investment-analysis 产出的调研报告全文
- `PREVIOUS_META_RESULT`：上一次调研报告全文（**可能不存在，见下方查找规则**）

由 `investment-weekly-review` 编排器调用时，`PREVIOUS_META_RESULT` 按以下规则查找：
1. 在 `research/` 下找文件名匹配 `investment-*-market-research.md`、日期早于 `AS_OF_DATE` 的文件，取日期最近的一份
2. 找不到时，检查 `research/investment-baseline-market-research.md`——若该文件除了顶部说明注释外还有实质内容，用它作为 `PREVIOUS_META_RESULT`
3. 上述两者都没有（`research/` 下没有任何历史 `investment-*-market-research.md`，且 baseline 文件仍是空的占位说明）：**这是真正的首次运行，没有基线可比**。此时不要虚构一个"上次结果"，也不要强行给出对比表；直接按下方"首次运行特殊路径"处理，不走正常的六步比较流程

单独调用本 skill（不经编排器）时，由调用方直接给出这两份文本，不必套用上面的查找规则。

## 首次运行特殊路径（无 `PREVIOUS_META_RESULT` 时）

不套用 instruction 的六步比较流程（没有"上次"可比），改为输出一份精简报告：

```markdown
# 元框架变化检测结果

## 1. 基本信息
- 调研时点：<AS_OF_DATE>
- 对比对象：无——本次是流水线首次运行，没有历史调研结果可比

## 2. 总结论
- 是否需要更新投资调研框架：否（首次运行，建立基线，不做变化判定）
- 更新级别：none
- 结论理由：本次 CURRENT_META_RESULT 将作为后续每周对比的基线起点，本身不构成"变化"，无需触发框架更新

## 7. 输出给下一步使用的结构化结果

FRAMEWORK_UPDATE_DECISION:
  update_needed: no
  update_level: none
  decision_reason: "首次运行，无历史基线可比，本次调研结果仅作为后续基线"

KEY_VARIABLE_CHANGES: []
UPDATE_FOCUS: []
DO_NOT_OVERREACT_ITEMS: []
```

## 执行（有 `PREVIOUS_META_RESULT` 时的正常路径）

1. 读取 `projects/investment_change_analysis/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则与六步分析流程；代入上面三个输入变量
2. 只关注会改变研究重点、判断顺序、模块权重、阈值设置的变化；不把措辞差异或单周噪音误判为框架级变化
3. 严格按 instruction 第六步给出的格式输出完整报告，末尾必须包含结构化字段 `FRAMEWORK_UPDATE_DECISION`（含 `update_needed: yes/no`、`update_level`、`decision_reason`）、`KEY_VARIABLE_CHANGES`（每项含 `research_meaning`——注意字段名是 `research_meaning` 不是期货那套的 `trading_meaning`）、`UPDATE_FOCUS`、`DO_NOT_OVERREACT_ITEMS`

## 输出

- 把完整报告写入 `research/investment-<AS_OF_DATE>-change-decision.md`
- 返回值：报告全文 + 解析出的 `update_needed`（yes/no），供编排器决定是否触发阶段③
