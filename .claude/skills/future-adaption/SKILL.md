---
name: future-adaption
description: 期货执行框架更新（流水线阶段③，仅在阶段②判定 update_needed=yes 时触发）：据变化检测结果起草新版期货执行框架，写入 research/<AS_OF_DATE>-adaption-report.md 并整篇替换 framework/futures_framework.md，在新分支上提交等待后续阶段与人工确认，不直接改 main、本阶段自己不开 PR。Use when asked to run the framework-update stage or draft a framework revision from an existing change-decision report.
---

# future adaption（流水线阶段③）

只在阶段②判定 `update_needed: yes` 时触发；`update_needed: no` 时不要调用本 skill，也不要动 `framework/futures_framework.md`。

本阶段结束后，编排器会接着调用 `future-data-sync`（判断配套取数脚本 `scripts/future_data.py` 是否要跟着改）在同一分支上追加提交，最后才由编排器统一开 PR——**本阶段自己不要执行 `gh pr create`**。

## 输入

- `CURRENT_FUTURES_EXECUTION_FRAMEWORK`：`framework/futures_framework.md` 现行全文（跳过文件顶部的 HTML 注释行，那只是本仓库的维护说明，不属于框架正文）
- `FRAMEWORK_UPDATE_RESULT`：阶段②产出的完整报告（含 `FRAMEWORK_UPDATE_DECISION` / `KEY_VARIABLE_CHANGES` / `UPDATE_FOCUS` / `DO_NOT_OVERREACT_ITEMS`）

## 执行

1. 读取 `projects/future_adaption/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则（只改真正受影响的部分、优先微调、尊重 DO_NOT_OVERREACT_ITEMS）与六步流程；代入上面两个输入变量
2. 严格按 instruction 第六步给出的格式，产出完整的「期货执行框架更新结果」报告，其中第 5 节"新版期货执行框架全文"必须是**完整、自包含**的新版框架正文（沿用现行框架自身的版本号+【本次更新】标注惯例，不是只给 diff 片段）

## 输出与提交（不直接改 main，本阶段不开 PR）

1. 把完整报告写入 `research/<AS_OF_DATE>-adaption-report.md`
2. 取报告"5. 新版期货执行框架全文"的完整正文，替换 `framework/futures_framework.md` 里 HTML 注释行之后的全部内容（注释行本身保留不动）
3. 新建分支 `futures-framework/<AS_OF_DATE>`，在该分支上 `git add` + commit 以上两处改动（commit message 用报告"1. 更新结论"摘要即可）
4. 返回值：分支名 + 报告全文，交给编排器传给下一步 `future-data-sync`；**到此为止，不要 push、不要 `gh pr create`**——PR 由编排器在 `future-data-sync` 也提交完之后统一打开
