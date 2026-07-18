---
name: investment-adaption
description: 股票研究框架更新（流水线阶段③，仅在阶段②判定 update_needed=yes 时触发）：据变化检测结果起草新版个股调研框架，写入 research/investment-<AS_OF_DATE>-adaption-report.md 并整篇替换 framework/investment_framework.md，在新分支上提交等待人工确认，不直接改 main、本阶段自己不开 PR。Use when asked to run the framework-update stage or draft a framework revision from an existing change-decision report.
---

# investment adaption（流水线阶段③）

只在阶段②判定 `update_needed: yes` 时触发；`update_needed: no` 时不要调用本 skill，也不要动 `framework/investment_framework.md`。

本阶段结束后，编排器会直接在同一分支上执行 `gh pr create`——**本阶段自己不要开 PR**（股票这条轨道没有类似期货 `future-data-sync` 的联动阶段，本阶段提交完就是分支的最后一次提交）。

## 输入

- `CURRENT_STOCK_RESEARCH_FRAMEWORK`：`framework/investment_framework.md` 现行全文（跳过文件顶部的 HTML 注释行，那只是本仓库的维护说明，不属于框架正文）——注意 instruction 原文里这个变量叫 `{{CURRENT_STOCK_RESEARCH_FRAMEWORK}}`，不是 `CURRENT_FUTURES_EXECUTION_FRAMEWORK` 那一套命名
- `FRAMEWORK_UPDATE_RESULT`：阶段②产出的完整报告（含 `FRAMEWORK_UPDATE_DECISION` / `KEY_VARIABLE_CHANGES` / `UPDATE_FOCUS` / `DO_NOT_OVERREACT_ITEMS`）

## 执行

1. 读取 `projects/investment_adaption/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则（只改真正受影响的部分、优先改模块权重/判断顺序/阈值松紧/前置验证项/风险约束、优先微调、尊重 DO_NOT_OVERREACT_ITEMS）与六步流程；代入上面两个输入变量
2. `framework/investment_framework.md` 本质是一份**逐股分析用的参数化模板**（含 `{{COMPANY_NAME}}`/`{{TICKER_OR_CODE}}`/`{{VALUATION_DATE}}` 占位符），不是像期货框架那样对所有合约通用的执行规则集——修改时保留这些占位符与模板的整体结构，不要把它误当成某一只具体股票的分析报告去改写
3. 严格按 instruction 第六步给出的格式，产出完整的「个股调研框架更新结果」报告，其中第 5 节"新版个股调研框架"必须是**完整、自包含**的新版模板正文（沿用现行框架自身的【本次更新】标注惯例，不是只给 diff 片段）

## 输出与提交（不直接改 main，等待人工确认）

1. 把完整报告写入 `research/investment-<AS_OF_DATE>-adaption-report.md`
2. 取报告"5. 新版个股调研框架"的完整正文，替换 `framework/investment_framework.md` 里 HTML 注释行之后的全部内容（注释行本身保留不动）
3. 新建分支 `investment-framework/<AS_OF_DATE>`，在该分支上 `git add` + commit 以上两处改动（commit message 用报告"1. 更新结论"摘要即可）
4. 在该分支上执行一次 `gh pr create`：标题形如 `股票研究框架更新 <AS_OF_DATE>：<更新级别>`；正文用报告"1. 更新结论"+"2. 受影响模块"+"6. 版本变更记录"的摘要，让人一眼看清改了什么、为什么改——**不 push/merge 到 main**
5. 返回值：PR 链接 + 一句话摘要（新旧版本号、更新级别）
