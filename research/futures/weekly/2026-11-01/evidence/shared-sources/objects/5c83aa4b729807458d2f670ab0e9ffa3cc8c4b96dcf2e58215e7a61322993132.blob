---
name: futures-weekly-review
description: 完成本仓期货周度研究、行情与候选刷新、证据纠错和方法维护；区分状态刷新与方法变更，接续明确采纳的报告，支持单阶段及定向审阅、重构。不执行交易。
---

# 期货研究与执行框架维护

维护合同：`maintenance_contract=futures-maintenance/v2`。

输出目录与历史发现遵循仓库 `research/README.md`，正式产物不写 research 根目录。

## 范围与模式

- 向上找到同时包含 `framework/`、`projects/`、`research/` 的仓库根，读取根 `AGENTS.md`。以下仓库路径相对该根，reference 相对本技能；兼容子目录与 worktree。
- `AS_OF_DATE` 为用户指定日期，否则为 Asia/Shanghai 当天。历史研究只用当时已披露证据；检索遵循根约定，不假定专用技能调用 API。
- 默认 `local`：本地保存，不自动 commit、push 或开 PR。用户或本次自动化任务已有明确 `publish` 授权时按其范围发布，不重复确认；旧 routine 或迁移不授予未来权限。修改框架用更新分支或隔离 worktree，不直接改 main。
- 只执行请求的模式和必要联动，单阶段不扩成全流程。方法、参数与歧义以 `framework/futures_framework.md` 为准，compact 为导航；数据口径读 `framework/FUTURES_DATA_PROTOCOL.md`，执行审计只用 `projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md`。本技能不复制 T/V 数值或核心风控公式。

| 模式 | 读取与执行 | 输出 |
|---|---|---|
| `research`／只研究 | [品种研究](references/meta-future-analysis.md) | market-research |
| `compare`／比较报告 | [变化检测与审计](references/future-change-analysis.md) | 三类判定、change-decision、execution-audit |
| `refresh`／行情与候选刷新 | [刷新和接续](references/refresh-and-handoff.md) | 轻量刷新记录；必要时修订受影响候选审计与接续 |
| `adapt`／方法适配 | [框架适配](references/future-adaption.md)，仅 method_change_needed=yes | canonical 局部更新、adaption-report |
| `data-sync`／同步工具 | [数据同步](references/future-data-sync.md) | 实际依赖同步、旧输出失效项 |
| `direct`／定向审阅、纠错或重构 | [定向维护](references/future-adaption.md) | maintenance 记录及获授权的必要联动 |
| `full`／完整周更 | 接续与取数 → 筛选和研究 → 三类判定与审计 → 条件方法适配 → 接续交付 | 本期研究、诊断及必要更新包 |

## 三类更新

三类可并存，不能用一个 yes/no 代替它们：

| 类别 | 处理对象 | 对方法的影响 |
|---|---|---|
| `state_refresh` | 行情、品种主因、事件、数据可得性、信号和计划状态 | 按现行规则刷新；不升级方法版本 |
| `evidence_correction` | 错数据、错口径、适用性误读、与既定规则不符的实现 | 撤回错误依据并重算受影响输出；不以纠错放松阈值 |
| `method_change` | 模型定义、范围、信号、有效期、止损或风险规则本身 | 说明缺陷与行为变化，完成方法适配和必要验证 |

`CHANGE_CLASSIFICATION` 输出 `state_refresh_needed / evidence_correction_needed / method_change_needed`。兼容字段 `FRAMEWORK_UPDATE_DECISION.update_needed` **仅等于 method_change_needed**；`update_level` 仅评方法变化，无方法变化为 none。规则定义本身错误可同时属于纠错与方法变更；纯数据修复、行情反向或研究优先级变化不是方法变更。

## 完整周更

1. 核工作区、授权与实际采用的框架/工具修订。publish 安全同步最新 origin/main；local 注明远端新鲜度，不自动拉取。按[刷新和接续](references/refresh-and-handoff.md)分别接续当前候选、已核纠错、V 观察锚和前期市场比较基线；同时读取跨 worktree 的本地共享采纳记录，不能只看 main 或各任务 memory。保留精确路径/hash 和替代范围；没有相应采纳记录才用严格正式名发现，不按 -rN 或修改时间猜版本。
2. 核快照完成标记、行情锚、真实交易日历和脚本版本。用户或自动化已授权取数时按环境文档运行刷新入口；未授权则用已有材料并披露覆盖。旧快照、取数失败与无信号分别记录；脚本空 POSITIONS 不是账户空仓。已授权无人值守取数先形成有效本期证据，再按发布约定提交。
3. 先复核全部已知存量计划/持仓的事件、反证、止损及期限，再做 MA/RB/M/SR/CF 价格与可得性短表，研究各品种主因和本周变化，重点 M/RB。至多两个的资源上限只适用于新机会深研，不截断存量风险复核。研究方按公开证据维护有经济依据的 V 观察锚；没有依据不造锚或凑数量。输出完整 CURRENT_META_RESULT。
4. 比较已采纳的前期报告；市场周环比基线必须严格早于研究日，同日 r2/r3 仅作本期证据/纠错接续。无实质基线明确缺口，仍完成本期执行审计和三类更新判定；透传 DATA_FEASIBILITY、EVIDENCE_CORRECTIONS。完整 publish 在修改 canonical 之前，先按下节保存原框架日志及 published handoff；本期状态可以先形成待写片段。
5. **无论 method_change_needed 是否为 yes，完成本期状态刷新、纠错重评及接续。** 原报告保留，修订另存；框架原有状态分区只维护日期、简短摘要及当前报告/handoff 引用，不因状态而升方法版本。状态引用涉及 canonical 时同步 compact 相应分区，不完整跑方法适配；publish 的状态片段在原框架日志交接完成后才写入更新分支。
6. 仅 method_change_needed=yes 时执行适配、必要 data-sync、同输入审计重评及 framework-condense。保留原框架审计，拟议方法结果标 `proposed_framework_reassessment`；不得将拟议规则写成历史已生效，不能追认旧成交或重启原信号窗口。方法变更须交代缺陷、现有规则为何不足、旧新行为差异、存量影响、固定版本验证及撤回条件，收益不可复现则保留未知。
7. 写明实际版本、行情日、登记时间、引用和失效项，通过适用校验后登记 local handoff，并将日频/周更采纳材料交付同一本地共享入口。完整 publish 且仅刷新状态时复用步骤4已登记的 handoff；有新的采纳修订才显式 --replace 并保留历史。更新分支拟议方法保留 proposed_framework_reassessment，与实际采纳隔离。交接不改变交易许可，也不继承 ready、账户或过期前的有效状态。

## 保存与发布

- 同日期先检查已有结果；匹配则复用，输入变化则另存可追溯修订，只有明确覆盖授权才改原文件。更新 handoff 为显式采纳动作，保留 supersedes 和纠错范围；不覆盖原报告，不按最大修订号自动提升。
- 完整 publish 沿用日志/框架分支边界：在实际已采用且 canonical 与 HEAD 一致的干净 origin/main 隔离基线上，按已有授权先提交本期原框架研究、决策、审计和新原料，再登记、提交并校验 published handoff；将仅含这些授权日志、原料及交接的提交安全推送 origin/main，核远端包含后，才从该基线创建或复用一个 codex/ 更新分支写 canonical/compact 状态引用或方法变更并创建单一 PR。非快进先同步复核，绝不强推；发布失败保留本地产物并报告，不能声称已完成 published 接续。原始日志不替换成拟议方法结果；若规则未变，method_change_needed=no，无需制造适配报告或脚本版本。
- published 检查只证明 manifest/引用/canonical 与当前 HEAD 内容一致，不能证明远端 main 已采用；编排器还须核实际采用的 origin/main 基线和发布结果。不能把 PR 分支已提交视为方法已生效。拟议方法仅在自己的更新分支作 local 接续，合并采纳后才登记新方法交接；不得覆盖 main 采纳。已有分支/PR复用匹配记录，阶段不各自 push/开 PR，创建 PR 后附加当前聊天，等待人工审核，不自行 merge。
- 原框架日志与采纳登记独立于状态引用 PR；状态 PR 未合并不阻断后续日频/周更使用已采纳研究。本地共享记录仍为 local，周更按已授予的发布范围核来源、导入并登记；共享不扩大日频 Git 权限，也不把拟议方法当已生效。
- 发布摘要分别给状态刷新、纠错、方法变更结论，附实际基线、行情覆盖和 handoff；不以 PR 数或 ready 数量衡量研究。缺完整候选账不声称市场零机会，缺成交轨迹不报告收益。
- 单阶段只保存该阶段授权产物，未完成的后续联动如实列出；direct 无须伪造周报或 update_needed。修改 skill 运行 bundled skill-creator 的 quick_validate，验证不等于策略有效。
