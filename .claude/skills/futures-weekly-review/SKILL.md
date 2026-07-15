---
name: futures-weekly-review
description: 期货研究流水线编排器：meta future analysis → future change analysis →（条件）future adaption → future data sync，每周跑一次；串联四个阶段 skill，处理"上一次调研"查找、框架回写、配套取数脚本联动同步、以及最终统一开 PR。Use when asked to run the weekly futures pipeline end to end, either as a local dry run or from the scheduled cloud routine.
---

# futures weekly review（编排器）

串联四个阶段 skill；不重复各阶段自己的方法论，那些分别在 `meta-future-analysis`、`future-change-analysis`、`future-adaption`、`future-data-sync` 各自的 SKILL.md 里。

## 步骤

1. 开始前先 `git pull`（或确认已是 origin/main 最新），确保能看到其他历史周次已提交的 `research/*.md`——`PREVIOUS_META_RESULT` 的查找依赖这些文件已经在远程仓库里
2. 取今天日期为 `AS_OF_DATE`（`YYYY-MM-DD`）
3. 调用 `meta-future-analysis` skill（输入 `AS_OF_DATE`），得到 `CURRENT_META_RESULT`，已落盘 `research/<AS_OF_DATE>-market-research.md`
4. 按 `future-change-analysis` SKILL.md 里的查找规则确定 `PREVIOUS_META_RESULT`
5. 调用 `future-change-analysis` skill（输入 `AS_OF_DATE`、`CURRENT_META_RESULT`、`PREVIOUS_META_RESULT`），得到 `update_needed`
6. **不论 `update_needed` 是 yes 还是 no**，直接在 `main` 分支上 `git add research/<AS_OF_DATE>-market-research.md research/<AS_OF_DATE>-change-decision.md` 并 commit + push——这两份只是调研/判定的留痕日志，不改动框架本身，不需要人工审阅门；且下一次运行（不论是下周还是任何人重跑）都要靠这次 push 上去的文件才能找到"上一次结果"，本地 commit 不 push 等于对下一次运行不可见

   **commit message 必须按以下结构写，两段结论缺一不可**（这是硬性格式要求，不是"写好点"的建议——即使觉得内容平淡也要按结构填，不能省略某一段）：
   ```
   research: <AS_OF_DATE> 期货元框架调研与变化检测（update_needed=<yes/no>[, update_level=<level>]）

   阶段①调研结论：<MAIN_CONTRADICTION 原句或紧贴原意的一句话概括，不要泛化改写>

   阶段②判定结论：update_needed=<yes/no>[，update_level=<level>]
   理由：<decision_reason 的完整摘要，2-4 句，需要能让人不看原文也理解"为什么这么判">
   [若 update_needed=yes，再加一行：本次更新重点：<UPDATE_FOCUS 各条要点，逗号分隔>]

   完整报告见 research/<AS_OF_DATE>-market-research.md 与 research/<AS_OF_DATE>-change-decision.md
   ```
7. 若 `update_needed: no`：流程到此结束
8. 若 `update_needed: yes`：
   a. 读 `framework/futures_framework.md` 作为 `CURRENT_FUTURES_EXECUTION_FRAMEWORK`，连同阶段②的完整报告一起调用 `future-adaption` skill——它会新建分支 `futures-framework/<AS_OF_DATE>`、写新版框架和报告、在该分支上 commit，但**不会**开 PR，把分支名和报告内容返回给编排器
   b. 在同一个分支上，连同新版框架全文、阶段③报告一起调用 `future-data-sync` skill——它会判断配套取数脚本 `scripts/future_data.py` 是否需要跟着改，改或不改都会在该分支上追加一个 commit（追加"8. 数据脚本同步"小节到报告里），返回是否改了脚本
   c. 两个子步骤都提交完之后，编排器自己在该分支上执行一次 `gh pr create`：标题形如 `期货框架更新 <AS_OF_DATE>：<更新级别>`；正文汇总阶段③的"1. 更新结论"+"2. 受影响模块"，以及阶段④（data-sync）"是否改了取数脚本"的结论——一个 PR 里同时看到"框架改了什么"和"取数脚本要不要跟着改"。**这一步绝对不能直接 push 或 merge 到 main**，必须走 PR，等待人工审阅
9. 输出一行摘要：`AS_OF_DATE` + `update_needed` + （若有）PR 链接，作为本次运行的可见结果

## 运行环境注意

- 本 skill 可能被云端 scheduled routine（无本地 session）调用：调研阶段一律用内置 `WebSearch`，不要依赖 `gemini-search`、`lark-cli` 等本地专属 MCP/工具
- 只有 `framework/futures_framework.md`（和联动的 `scripts/future_data.py`）的改动需要走分支 + PR；阶段①②的研究日志直接 push 到 main（步骤6），不因为"这周没有框架变化"就不提交
- `gh pr create` 只在编排器最后统一执行一次（步骤8c）——`future-adaption` 和 `future-data-sync` 各自只管在同一分支上提交，不要各自开 PR，避免同一次更新开出两个 PR
- 四个阶段各自可被单独手动调用（例如只想重跑调研，或针对两份已有调研结果重跑变化检测，或单独给已有的框架分支补一次数据脚本同步检查），不必每次都走完整编排；单独调用时不必执行步骤6的自动 push
