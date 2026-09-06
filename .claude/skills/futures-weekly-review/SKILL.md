---
name: futures-weekly-review
description: 期货研究流水线编排器：meta future analysis → future change analysis →（条件）future adaption → future data sync，每周跑一次；串联四个阶段 skill，处理"上一次调研"查找、框架回写、配套取数脚本联动同步、以及最终统一开 PR。Use when asked to run the weekly futures pipeline end to end, either as a local dry run or from the scheduled cloud routine.
---

# futures weekly review（编排器）

串联四个阶段 skill；不重复各阶段自己的方法论，那些分别在 `meta-future-analysis`、`future-change-analysis`、`future-adaption`、`future-data-sync` 各自的 SKILL.md 里。

## 步骤

1. 开始前先 `git pull`（或确认已是 origin/main 最新），确保能看到其他历史周次已提交的 `research/*.md`——`PREVIOUS_META_RESULT` 的查找依赖这些文件已经在远程仓库里
2. 取今天日期为 `AS_OF_DATE`（`YYYY-MM-DD`）
   收集 `EXECUTION_EVIDENCE` 来源清单：可用行情输出及其交易日/版本、当期完整账户与挂单快照、已有候选计划/成交记录/前期执行诊断。缺少来源就记录不可用，不能用脚本空 `POSITIONS` 推定账户空仓；读 `projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md` 作为唯一诊断口径。
3. 调用 `meta-future-analysis` skill（输入 `AS_OF_DATE`），得到 `CURRENT_META_RESULT`，已落盘 `research/<AS_OF_DATE>-market-research.md`
4. 按 `future-change-analysis` SKILL.md 里的查找规则确定 `PREVIOUS_META_RESULT`（注意排除 `investment-` 前缀的股票轨道文件）及配套的 `PREVIOUS_CHANGE_DECISION`（上一次的变化检测报告，承载上期留下的预备观察项）
5. 调用 `future-change-analysis` skill（输入 `AS_OF_DATE`、`CURRENT_META_RESULT`、`PREVIOUS_META_RESULT`、`PREVIOUS_CHANGE_DECISION`、`CURRENT_FRAMEWORK=framework/futures_framework.md` 现行全文、`EXECUTION_EVIDENCE`），得到 `update_needed` 与 `CURRENT_EXECUTION_AUDIT`——该 skill 先生成执行诊断，再完成三条触发轴（上期预备观察项复核、周环比变化、框架-现实一致性）和反摇摆护栏。检查 `research/<AS_OF_DATE>-execution-audit.md` 已实际生成；缺证据应有 `incomplete` 记录，不能跳过文件。
6. **不论 `update_needed` 是 yes 还是 no**，直接在 `main` 分支上 `git add research/<AS_OF_DATE>-market-research.md research/<AS_OF_DATE>-change-decision.md research/<AS_OF_DATE>-execution-audit.md` 并 commit + push——这三份是调研/判定/执行诊断的留痕日志，不改动框架本身；且下一次运行（不论是下周还是任何人重跑）都要靠这次 push 上去的文件才能找到"上一次结果"，本地 commit 不 push 等于对下一次运行不可见

   **commit message 必须按以下结构写，两段结论缺一不可**（这是硬性格式要求，不是"写好点"的建议——即使觉得内容平淡也要按结构填，不能省略某一段）：
   ```
   research: <AS_OF_DATE> 期货元框架调研与变化检测（update_needed=<yes/no>[, update_level=<level>]）

   阶段①调研结论：<MAIN_CONTRADICTION 原句或紧贴原意的一句话概括，不要泛化改写>

   阶段②判定结论：update_needed=<yes/no>[，update_level=<level>]
   理由：<decision_reason 的完整摘要，2-4 句，需要能让人不看原文也理解"为什么这么判">
   [若 update_needed=yes，再加一行：本次更新重点：<UPDATE_FOCUS 各条要点，逗号分隔>]

   执行诊断：<覆盖范围、各已观察候选状态、证据缺口；无完整账不报总体零机会>

   完整报告见 research/<AS_OF_DATE>-market-research.md、research/<AS_OF_DATE>-change-decision.md 与 research/<AS_OF_DATE>-execution-audit.md
   ```
7. 若 `update_needed: no`：不改框架；确认当期执行诊断已产出并留痕后，转步骤9输出摘要
8. 若 `update_needed: yes`：
   a. 读 `framework/futures_framework.md` 作为 `CURRENT_FUTURES_EXECUTION_FRAMEWORK`，连同阶段②的完整报告和 `CURRENT_EXECUTION_AUDIT` 一起调用 `future-adaption` skill——它会新建分支 `futures-framework/<AS_OF_DATE>`、写新版框架和报告、在该分支上 commit，但**不会**开 PR，把分支名和报告内容返回给编排器
   b. 在同一个分支上，连同新版框架全文、阶段③报告一起调用 `future-data-sync` skill——它会判断配套取数脚本 `scripts/future_data.py` 是否需要跟着改，改或不改都会在该分支上追加一个 commit（追加"8. 数据脚本同步"小节到报告里），返回是否改了脚本
      数据同步完成后，由编排器按共享模板及同一 `EXECUTION_EVIDENCE` 刷新 `research/<AS_OF_DATE>-execution-audit.md`，注明 `proposed_framework_reassessment`、最终框架/脚本版本及旧输出失效项；不伪造新行情/人工核验，也不把新版本当作历史当日生效版本。在同一分支提交诊断，并在适配报告引用该文件。风险计算引用 canonical Step5 与 `scripts/futures_risk.py`，完整输入不足就保留 null / incomplete。
   c. 在同一个分支上调用 `framework-condense` skill（`CANONICAL_PATH=framework/futures_framework.md`，`COMPACT_PATH=framework/futures_framework_compact.md`）——从新版框架全文无状态再生成供人阅读的 compact 衍生文件，过强制自审清单（数值参数无丢失、章节一致、历史标记清零），把「9. 精简版同步」小节追加到报告，在分支上追加一个 commit
   d. 三个子步骤都提交完之后，编排器自己在该分支上执行一次 `gh pr create`：标题形如 `期货框架更新 <AS_OF_DATE>：<更新级别>`；正文汇总阶段③的"1. 更新结论"+"2. 受影响模块"、阶段④（data-sync）"是否改了取数脚本"的结论、以及 condense 的压缩统计一句话。**这一步绝对不能直接 push 或 merge 到 main**，必须走 PR，等待人工审阅
9. 输出摘要：`AS_OF_DATE` + `update_needed` + 执行诊断路径/覆盖范围/主要缺口 + （若有）PR 链接。缺完整候选账时不得把没有 ready 记录写成“市场建议空仓”或“0 个机会”。

## 运行环境注意

- 本 skill 可能被云端 scheduled routine（无本地 session）调用：调研阶段一律用内置 `WebSearch`，不要依赖 `gemini-search`、`lark-cli` 等本地专属 MCP/工具
- `framework/futures_framework.md`（和联动的 `scripts/future_data.py` / `scripts/futures_risk.py`、衍生的 `framework/futures_framework_compact.md`）改动走分支 + PR；阶段①②的研究与执行诊断日志直接 push 到 main（步骤6），不因为"这周没有框架变化"就不提交。新版本的诊断重评与框架一起提交到同一 PR
- `gh pr create` 只在编排器最后统一执行一次（步骤8d）——`future-adaption`、`future-data-sync`、`framework-condense` 各自只管在同一分支上提交，不要各自开 PR，避免同一次更新开出多个 PR
- **compact 是给人读的衍生文件，任何 AI 环节（含本编排器的各阶段）一律读 canonical 完整版**，不要把 compact 接进任何阶段的输入
- 各阶段可被单独手动调用（例如只想重跑调研，或针对两份已有调研结果重跑变化检测，或单独刷一次 compact），不必每次都走完整编排；单独调用时不必执行步骤6的自动 push
- 用户要求定向维护框架/诊断而非运行本周研究时，只处理授权文件，不执行上述新市场调研、历史同日期报告覆盖或自动 push；诊断仍采用共享模板。
