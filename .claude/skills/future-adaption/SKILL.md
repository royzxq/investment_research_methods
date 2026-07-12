---
name: future-adaption
description: 期货执行框架更新（流水线阶段③，仅在阶段②判定 update_needed=yes 时触发）：据变化检测结果起草新版期货执行框架，写入 research/<AS_OF_DATE>-adaption-report.md 并整篇替换 framework/futures_framework.md，以分支+PR 形式提交等待人工确认，不直接改 main。Use when asked to run the framework-update stage or draft a framework revision from an existing change-decision report.
---

# future adaption（流水线阶段③）

只在阶段②判定 `update_needed: yes` 时触发；`update_needed: no` 时不要调用本 skill，也不要动 `framework/futures_framework.md`。

## 输入

- `CURRENT_FUTURES_EXECUTION_FRAMEWORK`：`framework/futures_framework.md` 现行全文（跳过文件顶部的 HTML 注释行，那只是本仓库的维护说明，不属于框架正文）
- `FRAMEWORK_UPDATE_RESULT`：阶段②产出的完整报告（含 `FRAMEWORK_UPDATE_DECISION` / `KEY_VARIABLE_CHANGES` / `UPDATE_FOCUS` / `DO_NOT_OVERREACT_ITEMS`）

## 执行

1. 读取 `projects/future_adaption/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则（只改真正受影响的部分、优先微调、尊重 DO_NOT_OVERREACT_ITEMS）与六步流程；代入上面两个输入变量
2. 严格按 instruction 第六步给出的格式，产出完整的「期货执行框架更新结果」报告，其中第 5 节"新版期货执行框架全文"必须是**完整、自包含**的新版框架正文（沿用现行框架自身的版本号+【本次更新】标注惯例，不是只给 diff 片段）

## 输出与提交（不直接改 main，等待人工确认）

1. 把完整报告写入 `research/<AS_OF_DATE>-adaption-report.md`
2. 取报告"5. 新版期货执行框架全文"的完整正文，替换 `framework/futures_framework.md` 里 HTML 注释行之后的全部内容（注释行本身保留不动）
3. 新建分支 `futures-framework/<AS_OF_DATE>`，在该分支上提交以上两处改动
4. `gh pr create`：标题形如 `期货框架更新 <AS_OF_DATE>：<更新级别>`；正文用报告"1. 更新结论"+"2. 受影响模块"+"6. 版本变更记录"的摘要，让人一眼看清改了什么、为什么改——**不 push/merge 到 main**
5. 返回值：PR 链接 + 一句话摘要（新旧版本号、更新级别）
