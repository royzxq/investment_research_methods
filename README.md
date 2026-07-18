# investment_research_methods

两条并行的研究方法论自动化流水线的本地存档，每周分别由 claude.ai 云端 Routine 自动运行。两条轨道共享同一个仓库，文件互不重叠（期货侧文件无前缀，股票侧文件统一带 `investment-` 前缀），互相独立、互不干扰。

## 期货轨道：meta future analysis → future change analysis → future adaption → future data sync

- `projects/{meta_future_analysis,future_change_analysis,future_adaption}/INSTRUCTIONS.md` — 三个 Claude.ai Project 的原始 instruction
- `framework/futures_framework.md` — 现行「期货投资分析框架」活文档，只能通过分支 + PR 更新，不直接改 main
- `scripts/future_data.py` — 框架配套取数脚本（Tushare/akshare），版本随框架结构性变化同步迭代；本身无网络环境无法线上实测，改动需人工在有真实数据源的环境里运行验证
- `research/` — `baseline-market-research.md`（day-0 基线）+ 按日期命名的 `<date>-market-research.md` / `<date>-change-decision.md`（始终直接 push 到 main）/ `<date>-adaption-report.md`（框架需要更新时才有，走分支 + PR）
- `.claude/skills/` — `meta-future-analysis` / `future-change-analysis` / `future-adaption` / `future-data-sync`（四个阶段包装）+ `futures-weekly-review`（编排器，统一开 PR）

## 股票轨道：meta investment analysis → investment change analysis → investment adaption

- `projects/{meta_investment_analysis,investment_change_analysis,investment_adaption}/INSTRUCTIONS.md` — 三个 Claude.ai Project 的原始 instruction；字段口径与期货那套不同（`DOMINANT_RETURN_DRIVERS`/`FRAGILE_NARRATIVE`/`research_meaning`，`investment_adaption` 输入变量名为 `CURRENT_STOCK_RESEARCH_FRAMEWORK`）
- `framework/investment_framework.md` — 现行「个股调研框架」活文档，本质是逐股分析用的参数化模板（含 `{{COMPANY_NAME}}`/`{{TICKER_OR_CODE}}`/`{{VALUATION_DATE}}` 占位符），不是像期货框架那样对所有标的通用的执行规则集；同样只能通过分支 + PR 更新
- 框架 Section 0 提到配套取数脚本 `stock_data_pack.py`（对应期货侧 `future_data.py` 的角色），目前本仓库与 `ai_investment` 均未找到该脚本，暂未设计联动同步阶段
- `research/` — `investment-baseline-market-research.md`（day-0 基线，可为空——为空时首次运行按"无历史基线"处理，不是错误）+ `investment-<date>-market-research.md` / `investment-<date>-change-decision.md`（始终直接 push 到 main）/ `investment-<date>-adaption-report.md`（框架需要更新时才有，走分支 + PR）
- `.claude/skills/` — `meta-investment-analysis` / `investment-change-analysis` / `investment-adaption`（三个阶段包装，`investment-adaption` 自己开 PR，无需编排器额外收尾）+ `investment-weekly-review`（编排器）
