---
name: investment-adaption
description: 股票研究框架更新（流水线阶段③，仅在阶段②判定 update_needed=yes 时触发）：据变化检测结果起草新版个股调研框架，写入 research/investment-日期-adaption-report.md 并局部更新 framework/investment_framework.md，在新分支上提交等待后续阶段与人工确认，不直接改 main、本阶段自己不开 PR。Use when asked to run the framework-update stage or draft a framework revision from an existing change-decision report.
---

# investment adaption（流水线阶段③）

只在阶段②判定 `update_needed: yes` 时触发；`update_needed: no` 时不要调用本 skill，也不要动 `framework/investment_framework.md`。

本阶段结束后，编排器会接着在同一分支上调用 `framework-condense`（再生成保真精简版 compact）并追加提交，最后才由编排器统一执行 `gh pr create`——**本阶段自己不要开 PR**。

## 输入

- `CURRENT_STOCK_RESEARCH_FRAMEWORK`：`framework/investment_framework.md` 现行全文（跳过文件顶部的 HTML 注释行，那只是本仓库的维护说明，不属于框架正文）——注意 instruction 原文里这个变量叫 `{{CURRENT_STOCK_RESEARCH_FRAMEWORK}}`，不是 `CURRENT_FUTURES_EXECUTION_FRAMEWORK` 那一套命名
- `FRAMEWORK_UPDATE_RESULT`：阶段②产出的完整报告（含 `FRAMEWORK_UPDATE_DECISION` / `KEY_VARIABLE_CHANGES` / `UPDATE_FOCUS` / `DO_NOT_OVERREACT_ITEMS`）

## 执行

1. 读取 `projects/investment_adaption/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则（只改真正受影响的部分、优先改模块权重/判断顺序/阈值松紧/前置验证项/风险约束、优先微调、尊重 DO_NOT_OVERREACT_ITEMS）与六步流程；代入上面两个输入变量
2. `framework/investment_framework.md` 本质是一份**逐股分析用的参数化模板**（含 `{{COMPANY_NAME}}`/`{{TICKER_OR_CODE}}`/`{{VALUATION_DATE}}` 占位符），不是像期货框架那样对所有合约通用的执行规则集——修改时保留这些占位符与模板的整体结构，不要把它误当成某一只具体股票的分析报告去改写
3. 严格按 instruction 第六步给出的格式产出「个股调研框架更新结果」报告；第 5 节链接工作区完整框架，只列受影响章节和必要变更片段，不粘全文。框架只局部修改受影响内容，不新增【本次更新】等历代修订标记；当前状态在原有对应区域替换，历史依据放日期报告和 git。研究范围、判据、模板占位符与各阶段分析要求不因文本精简改变

## 输出与提交（不直接改 main，本阶段不开 PR）

1. 把完整报告写入 `research/investment-<AS_OF_DATE>-adaption-report.md`
2. 按报告列出的变更局部修改 `framework/investment_framework.md`，保留未受影响的有效内容及维护说明；当前状态原位替换，不叠加旧状态。完整新版正文由工作区文件提供，不再从报告提取全文替换
3. 新建分支 `investment-framework/<AS_OF_DATE>`，在该分支上 `git add` + commit 以上两处改动（commit message 用报告"1. 更新结论"摘要即可）
4. 返回值：分支名 + 报告全文，交给编排器传给下一步 `framework-condense`；**到此为止，不要 push、不要 `gh pr create`**——PR 由编排器在 condense 也提交完之后统一打开
