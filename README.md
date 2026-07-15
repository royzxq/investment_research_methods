# investment_research_methods

期货投资研究方法论与分析流水线（meta future analysis → future change analysis → future adaption → future data sync）的本地存档，每周由 claude.ai 云端 Routine 自动运行（`futures-weekly-review` skill）。

## 目录结构

- `projects/` — 三个 Claude.ai Project 的原始 instruction（`meta_future_analysis/` / `future_change_analysis/` / `future_adaption/`，各自 `INSTRUCTIONS.md`）
- `framework/futures_framework.md` — 现行「期货投资分析框架」活文档，只能通过分支 + PR 更新，不直接改 main
- `scripts/future_data.py` — 框架配套取数脚本（Tushare/akshare），版本随框架结构性变化同步迭代；本身无网络环境无法线上实测，改动需人工在有真实数据源的环境里运行验证
- `research/` — 每周流水线运行的留痕：`baseline-market-research.md`（day-0 基线）+ 按日期命名的 `<date>-market-research.md` / `<date>-change-decision.md`（始终直接 push 到 main）/ `<date>-adaption-report.md`（框架需要更新时才有，走分支 + PR）
- `.claude/skills/` — 跑这套流水线用的 Claude Code skill：`meta-future-analysis` / `future-change-analysis` / `future-adaption` / `future-data-sync`（四个阶段包装）+ `futures-weekly-review`（编排器，统一开 PR）
