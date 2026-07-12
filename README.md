# investment_research_methods

期货投资研究方法论与三段分析流水线（meta future analysis → future change analysis → future adaption）的本地存档。

## 目录结构

- `projects/` — 三个 Claude.ai Project 的原始 instruction（`meta_future_analysis/` / `future_change_analysis/` / `future_adaption/`，各自 `INSTRUCTIONS.md`）
- `framework/futures_framework.md` — 现行「期货投资分析框架」活文档
- `research/` — 每周流水线运行的留痕（调研报告 + 变更判定，按日期命名）
- `.claude/skills/` — 跑这套流水线用的 Claude Code skill：`meta-future-analysis` / `future-change-analysis` / `future-adaption`（三个阶段包装）+ `futures-weekly-review`（编排器）
