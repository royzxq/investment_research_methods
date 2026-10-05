---
name: investment-weekly-review
description: 维护本仓库 A 股与港股研究框架：执行周度元研究、变化检测、条件适配与保真精简；也支持仅研究、比较指定报告或从变化报告适配。用于研究框架演化，不替代普通公司投研。
---

# 股票研究框架维护

## 环境、范围与运行模式

- 从本技能所在目录向上找到同时包含 `framework/`、`projects/`、`research/` 的仓库根目录，读取根 `AGENTS.md`。本文仓库路径均相对该根目录；参考文件路径相对本技能目录。工作目录可能是子目录或 worktree，不硬编码用户主目录。
- 日期采用 `Asia/Shanghai`；`AS_OF_DATE` 为用户指定日期，否则为北京时间当天。历史时点研究仅使用当时已披露的证据，不混入未来信息。检索路由遵循根 `AGENTS.md`，用当前环境工具检索并读取原文，不假定存在 `WebSearch` 或技能调用 API。
- 默认 `local`：在授权范围写本地报告；需改 canonical 时使用框架更新分支或隔离 worktree，不直接改 `main`，不自动 commit、push、开 PR。只有用户明确授权本次 `publish` 才执行发布步骤；技能迁移、旧 routine 和报告模板不提供未来发布授权。
- 按用户要求选模式，仅读取对应参考：完整周更依次执行下表；单阶段到该阶段结束，不自动补跑其他阶段、compact 或发布。用户要求定向维护时只处理授权文件，不重跑市场研究。

| 模式 | 读取与执行 | 输出 |
|---|---|---|
| `research`／只研究 | [元研究](references/meta-investment-analysis.md) | 本期 market-research |
| `compare`／比较指定报告 | [变化检测](references/investment-change-analysis.md)；使用用户指定的新旧报告及可用的上期决策 | change-decision 与 `update_needed` |
| `adapt`／从变化报告适配 | [框架适配](references/investment-adaption.md)；只在 `update_needed=yes` 时执行 | 局部 canonical 改动与 adaption-report |
| `full`／完整周更 | 元研究 → 变化检测 → 条件适配 → 共用 `framework-condense` | 两份研究日志；有更新时另有框架更新包 |

`framework/investment_framework.md` 是方法、参数和歧义裁决的权威；`framework/investment_framework_compact.md` 仅供保真导航。历史状态来自日期报告及必要 git 变更，不向 canonical 堆积历周记录。共用精简入口位于仓库 `.agents/skills/framework-condense/SKILL.md`，仅在完整更新流程或用户明确要求精简时读取执行。

## 完整周更

1. 检查现有工作区与历史材料。`publish` 时确认 `origin/main` 最新并按根约定安全同步；不覆盖或夹带其他工作。`local` 使用现有历史并说明远程新鲜度限制，不为研究自动拉取或发布。
2. 执行元研究，取得并保存完整 `CURRENT_META_RESULT`。
3. 历史基线只匹配 `research/investment-YYYY-MM-DD-market-research.md`，取日期严格早于 `AS_OF_DATE` 的最近一份；上期决策只取同日期的 `investment-YYYY-MM-DD-change-decision.md`。没有历史时检查 `research/investment-baseline-market-research.md` 是否除说明注释外有实质内容。没有实质基线走首次运行路径。
4. 执行变化检测。始终传 `AS_OF_DATE`、`CURRENT_META_RESULT`、现行完整 canonical；只省略不存在的 `PREVIOUS_META_RESULT`／`PREVIOUS_CHANGE_DECISION`，不能在首次运行省略本期结果。完整 `publish` 在此先按下节保存两份研究日志，再进入更新分支；不等改完框架才回头推 main 日志。
5. `update_needed=no` 时结束分析并输出摘要。`update_needed=yes` 时在同一框架更新分支执行适配，再读取共用 `framework-condense`：`CANONICAL_PATH=framework/investment_framework.md`，`COMPACT_PATH=framework/investment_framework_compact.md`。精简结果写入适配报告「8. 精简版同步」。
6. `local` 返回本地路径、判定、修改范围和未验证事项。`publish` 的日志已在步骤4保存，有更新时按下节统一发布更新分支及 PR。

## 同日幂等与发布

- 同日期报告已存在时先检查输入、日期和框架版本，匹配则复用；不为重复运行覆盖历史。用户明确要求重跑或修订该日期才覆写授权文件，并标明下游哪些结果需重评。输入或版本不匹配而未获覆写授权时，报告差异，不把旧结果当作新运行成功。
- 已有本期分支、提交或 PR 时先检查其内容；复用匹配记录，不重复提交或另开同一期 PR。框架分支名称遵循根 `AGENTS.md`；沿用已存在的本期分支，不因前缀变化另造一份。
- 完整流程的 `publish`：无论是否更新框架，两份 `research/investment-<AS_OF_DATE>-{market-research,change-decision}.md` 都按授权提交并推送到 `main`，供下次找到基线；只包含本次授权文件。有框架更新时先保存日志，再在更新分支分别提交适配和 compact。阶段参考不自行开 PR，入口统一创建或复用一个 PR，等待人工审核，不 merge。
- 单阶段 `publish` 只发布本次明确授权的产物，不扩成完整周更；未完成必要同步时明确列出缺口，不宣称更新包完成。
- 研究日志提交保留两段结论，示例：

```text
research: <AS_OF_DATE> 股票元框架调研与变化检测（update_needed=<yes/no>[, update_level=<level>]）

阶段①调研结论：<MAIN_CONTRADICTION 原句或紧贴原意的概括>

阶段②判定结论：update_needed=<yes/no>[，update_level=<level>]
理由：<decision_reason 的完整摘要，2–4 句；首次运行写“首次运行，建立基线，不做变化判定”>
[update_needed=yes 时：本次更新重点：<UPDATE_FOCUS 摘要>]

完整报告见 research/investment-<AS_OF_DATE>-market-research.md 与 research/investment-<AS_OF_DATE>-change-decision.md
```

- PR 标题：`股票研究框架更新 <AS_OF_DATE>：<更新级别>`；正文汇总适配报告「1. 更新结论」「2. 受影响模块」「6. 版本变更记录」和 compact 尺寸统计、保真限制。创建 PR 后按当前 Codex 工具约定附加 PR artifact。
- 最终摘要包含 `AS_OF_DATE`、模式、`update_needed`、报告路径及（如有）PR 链接。
