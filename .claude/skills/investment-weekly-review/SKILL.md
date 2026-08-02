---
name: investment-weekly-review
description: 股票研究流水线编排器：meta investment analysis → investment change analysis →（条件）investment adaption，每周跑一次；串联三个阶段 skill，处理"上一次调研"查找（含首次运行无基线的特殊情况）与框架回写。与期货侧的 futures-weekly-review 并列、互不干扰。Use when asked to run the weekly stock research pipeline end to end, either as a local dry run or from the scheduled cloud routine.
---

# investment weekly review（编排器）

串联三段流水线；不重复三个阶段各自的分析方法论，那些分别在 `meta-investment-analysis`、`investment-change-analysis`、`investment-adaption` 各自的 SKILL.md 里。这条轨道和期货的 `futures-weekly-review` 是完全独立的两套流水线，共享同一个仓库但文件互不重叠（`investment-` 前缀 vs 期货的无前缀文件）。

## 步骤

1. 开始前先 `git pull`（或确认已是 origin/main 最新），确保能看到其他历史周次已提交的 `research/investment-*.md`——`PREVIOUS_META_RESULT` 的查找依赖这些文件已经在远程仓库里
2. 取今天日期为 `AS_OF_DATE`（`YYYY-MM-DD`）
3. 调用 `meta-investment-analysis` skill（输入 `AS_OF_DATE`），得到 `CURRENT_META_RESULT`，已落盘 `research/investment-<AS_OF_DATE>-market-research.md`
4. 按 `investment-change-analysis` SKILL.md 里的查找规则确定 `PREVIOUS_META_RESULT`（可能不存在——首次运行没有基线是正常情况，不是错误）及配套的 `PREVIOUS_CHANGE_DECISION`（上一次的变化检测报告，承载上期留下的预备观察项）
5. 调用 `investment-change-analysis` skill（输入 `AS_OF_DATE`、`CURRENT_META_RESULT`、`PREVIOUS_META_RESULT`、`PREVIOUS_CHANGE_DECISION`、`framework/investment_framework.md` 现行全文；若无基线则不传前两者，交由该 skill 走"首次运行特殊路径"），得到 `update_needed`——该 skill 内部有三条触发轴：上期预备观察项复核、周环比变化、框架-现实一致性
6. **不论 `update_needed` 是 yes 还是 no**，直接在 `main` 分支上 `git add research/investment-<AS_OF_DATE>-market-research.md research/investment-<AS_OF_DATE>-change-decision.md` 并 commit + push——这两份只是调研/判定的留痕日志，不改动框架本身，不需要人工审阅门；且下一次运行都要靠这次 push 上去的文件才能找到"上一次结果"，本地 commit 不 push 等于对下一次运行不可见

   **commit message 必须按以下结构写，两段结论缺一不可**：
   ```
   research: <AS_OF_DATE> 股票元框架调研与变化检测（update_needed=<yes/no>[, update_level=<level>]）

   阶段①调研结论：<MAIN_CONTRADICTION 原句或紧贴原意的一句话概括，不要泛化改写>

   阶段②判定结论：update_needed=<yes/no>[，update_level=<level>]
   理由：<decision_reason 的完整摘要，2-4 句，需要能让人不看原文也理解"为什么这么判">
   [若 update_needed=yes，再加一行：本次更新重点：<UPDATE_FOCUS 各条要点，逗号分隔>]
   [若是首次运行无基线，理由直接写"首次运行，建立基线，不做变化判定"]

   完整报告见 research/investment-<AS_OF_DATE>-market-research.md 与 research/investment-<AS_OF_DATE>-change-decision.md
   ```
7. 若 `update_needed: no`：流程到此结束
8. 若 `update_needed: yes`：
   a. 读 `framework/investment_framework.md` 作为 `CURRENT_STOCK_RESEARCH_FRAMEWORK`，连同阶段②的完整报告一起调用 `investment-adaption` skill——它会新建分支 `investment-framework/<AS_OF_DATE>`、写新版框架和报告、在该分支上 commit，但**不会**开 PR
   b. 在同一个分支上调用 `framework-condense` skill（`CANONICAL_PATH=framework/investment_framework.md`，`COMPACT_PATH=framework/investment_framework_compact.md`）——从新版框架全文无状态再生成供人阅读的 compact 衍生文件，过强制自审清单（数值参数无丢失、章节一致、历史标记清零），把「8. 精简版同步」小节追加到报告，在分支上追加一个 commit
   c. 两个子步骤都提交完之后，编排器自己在该分支上执行一次 `gh pr create`：标题形如 `股票研究框架更新 <AS_OF_DATE>：<更新级别>`；正文用报告"1. 更新结论"+"2. 受影响模块"+"6. 版本变更记录"的摘要，外加 condense 的压缩统计一句话。**这一步绝对不能直接 push 或 merge 到 main**，必须走 PR，等待人工审阅
9. 输出一行摘要：`AS_OF_DATE` + `update_needed` + （若有）PR 链接，作为本次运行的可见结果

## 运行环境注意

- 本 skill 可能被云端 scheduled routine（无本地 session）调用：调研阶段一律用内置 `WebSearch`，不要依赖 `gemini-search`、`lark-cli` 等本地专属 MCP/工具
- 只有 `framework/investment_framework.md`（和衍生的 `framework/investment_framework_compact.md`）的改动需要走分支 + PR；阶段①②的研究日志直接 push 到 main（步骤6），不因为"这周没有框架变化"就不提交
- `gh pr create` 只在编排器最后统一执行一次（步骤8c）——`investment-adaption` 和 `framework-condense` 各自只管在同一分支上提交，不要各自开 PR
- **compact 是给人读的衍生文件，任何 AI 环节（含本编排器的各阶段）一律读 canonical 完整版**，不要把 compact 接进任何阶段的输入
- 首次运行（无历史 `research/investment-*-market-research.md` 且 baseline 文件是空占位）不是异常情况，`update_needed` 会自然落在 `no`，流程正常结束于步骤7，不需要特殊报错处理
- 各阶段可被单独手动调用（例如只想重跑调研，或针对两份已有调研结果重跑变化检测，或单独刷一次 compact），不必每次都走完整编排；单独调用时不必执行步骤6的自动 push
