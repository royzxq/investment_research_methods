---
name: futures-weekly-review
description: 维护本仓库期货研究与执行框架：周度元研究、变化检测、每期执行审计、条件适配、数据脚本同步及保真精简；支持单阶段研究、比较、适配和 data-sync。用于期货框架演化，不执行交易。
---

# 期货研究与执行框架维护

输出目录、通用技能映射与发现命令统一见仓库 `research/README.md`；正式产物不写 `research/` 根目录。

## 环境、范围与运行模式

- 从本技能目录向上找到同时包含 `framework/`、`projects/`、`research/` 的仓库根，读取根 `AGENTS.md`。仓库路径相对该根，参考路径相对技能目录；兼容子目录和 worktree，不硬编码用户目录。
- `AS_OF_DATE` 为用户给定日期，否则为 `Asia/Shanghai` 当天。历史研究仅使用当时已披露证据。检索路由遵循根 `AGENTS.md`，使用当前工具检索与读取原文，不假定 `WebSearch` 或技能调用 API 存在。
- 默认 `local`：只在授权范围产生本地结果；canonical 变更在更新分支或隔离 worktree，不直接改 `main`，不自动 commit、push 或开 PR。只有用户明确授权本次 `publish` 才发布；迁移和旧 routine 不授予未来发布权限。
- 选择用户要求的模式，只读取相关参考。单阶段结束就返回，不自动扩成全流程；定向维护不自动新市场调研、覆写历史或发布。

| 模式 | 读取与执行 | 输出 |
|---|---|---|
| `research`／只研究 | [元研究](references/meta-future-analysis.md) | market-research |
| `compare`／比较指定报告 | [变化检测与审计](references/future-change-analysis.md) | change-decision、execution-audit 与 `update_needed` |
| `adapt`／从变化报告适配 | [框架适配](references/future-adaption.md)，仅 `update_needed=yes` | canonical 局部更新、adaption-report |
| `data-sync`／仅同步脚本 | [数据同步](references/future-data-sync.md)，使用已有新版框架和适配报告 | 是否改脚本、同步记录、旧输出失效项 |
| `full`／完整周更 | 元研究 → 变化检测及审计 → 条件适配 → 数据同步 → 诊断重评 → 共用精简 | 研究日志与条件更新包 |

`framework/futures_framework.md` 是方法、参数及歧义裁决权威；compact 仅作保真导航。先读 `framework/FUTURES_DATA_PROTOCOL.md`，执行审计只用 `projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md`；评分与风险口径不在包装层另存。历史读取日期报告及必要 git 变更。

## 完整周更与证据发现

1. 检查工作区与历史。`publish` 确认 `origin/main` 最新并按根约定安全同步；`local` 使用现有材料并注明远程新鲜度限制，不自动拉取或发布。
2. 读数据协议、`framework/futures_framework_compact.md` 和共享审计模板；方法与参数回 canonical。发现本期 `EXECUTION_EVIDENCE`：
   - 期货快照仅匹配 `research/futures/snapshots/YYYY-MM-DD-data-snapshot.txt`，不匹配 `etf-*` 或股票文件；取不晚于 `AS_OF_DATE` 的最近有效一份。发布／无人值守流程读取已提交快照；本地用户明确提供的未提交快照可使用，但标明来源状态。记录文件日期、AS_OF、脚本版本、最新行情日；晚于研究日的不作为历史证据，落后于最近已完成交易日标滞后，不推算补齐。
   - 公告、产业原始来源、当期完整账户与挂单快照、候选计划、成交记录、前期诊断。缺来源记不可用，脚本空 `POSITIONS` 不代表账户空仓。
   - 初分 `DATA_FEASIBILITY`（available／temporary_gap／research_only）和 `EVIDENCE_CORRECTIONS`；专业增强项缺失不拖累其他活跃模型。流程不自动运行行情脚本；用户明确要求取数时才按根数据执行约定运行。
3. 执行元研究，取得完整 `CURRENT_META_RESULT`，确认活跃池最小数据先于扩展研究，并保留可得性与纠错字段。
4. 历史研究仅匹配 `research/futures/weekly/YYYY-MM-DD/YYYY-MM-DD-market-research.md`，取严格早于 `AS_OF_DATE` 的最近一份；上期决策只取同日期 `YYYY-MM-DD-change-decision.md`。无历史时回退 `research/futures/baselines/baseline-market-research.md`；无实质基线则明确缺口，不虚构上期。本期结果始终必传。
5. 执行变化检测及独立执行审计，取得 `update_needed`、`CURRENT_EXECUTION_AUDIT`。无论是否更新都要生成审计；完整透传 `DATA_FEASIBILITY`、`EVIDENCE_CORRECTIONS`，不只传市场摘要。账户未知不阻止研究，专业依赖不可得不使整个池自动 incomplete。完整 `publish` 在此先按下节保存三份原框架日志，再进入更新分支，不能把重评后的诊断推作 main 原始日志。
6. 无更新时保留当期三份日志并结束分析；有更新时在同一更新分支执行适配、数据同步。随后使用同一证据按共享模板刷新本期审计，注明 `proposed_framework_reassessment`、最终框架／脚本版本与旧输出失效项，适配报告引用该审计。`local` 更新也须在隔离工作区或本地审阅产物中保留原框架审计完整副本及来源，供后来获授权发布时分别处理。不能伪造新行情或把拟议版本写成历史当日已生效；风险输入不足保留 null／incomplete。
7. 读取共用仓库 `.agents/skills/framework-condense/SKILL.md`：`CANONICAL_PATH=framework/futures_framework.md`，`COMPACT_PATH=framework/futures_framework_compact.md`。写适配报告「9. 精简版同步」。单阶段模式不自动推进到这一步。
8. `local` 返回本地结果；`publish` 的原框架日志已在步骤5保存，有更新时按下节统一发布更新分支与 PR。

## 同日幂等与发布

- 同日期报告先核日期、输入与版本，匹配则复用；用户明确重跑或修订该日期才覆写授权文件，并列下游需重评的结果。输入不匹配且未获覆写授权时说明差异，不将旧产物当新运行成功。已有本期分支、提交、PR 时先检查并复用匹配记录，不重复发布。
- 完整 `publish`：不论是否更新，将本期 market-research、change-decision、旧框架下 execution-audit 三份日志按授权提交并推送到 `main`。有更新时再在框架更新分支分别提交适配、data-sync、拟议版本审计重评、compact；只包含授权文件。分支名遵循根 `AGENTS.md`，复用已有本期分支。入口统一创建或复用一个 PR，等待人工审核，不 merge；阶段参考不自己 push 或开 PR。
- 单阶段发布只处理明确授权产物，不扩成全流程；必要同步尚缺时明确说明，不宣称完整更新包已完成。
- 日志提交保留两段结论及执行诊断，示例：

```text
research: <AS_OF_DATE> 期货元框架调研与变化检测（update_needed=<yes/no>[, update_level=<level>]）

阶段①调研结论：<MAIN_CONTRADICTION 原句或紧贴原意的概括>

阶段②判定结论：update_needed=<yes/no>[，update_level=<level>]
理由：<decision_reason 完整摘要，2–4 句>
[update_needed=yes 时：本次更新重点：<UPDATE_FOCUS 摘要>]

执行诊断：<覆盖范围、候选状态、证据缺口；缺完整账不报总体零机会>

完整报告见 research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-market-research.md、research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-change-decision.md 与 research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-execution-audit.md
```

- PR 标题：`期货框架更新 <AS_OF_DATE>：<更新级别>`；正文汇总适配结论和模块、是否改脚本、诊断重评、compact 统计与验证限制。创建后按当前 Codex 工具约定附加 PR artifact。
- 最终摘要包含日期、模式、`update_needed`、诊断路径、活跃覆盖及必要缺口、research_only 范围及复活条件、证据修复和（如有）PR。缺完整候选账时，不能把没有 ready 记录写成“市场建议空仓”或“0 个机会”。
