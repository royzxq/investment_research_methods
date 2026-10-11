---
name: investment-weekly-review
description: 维护本仓 A 股与港股研究框架，执行周度元研究、状态刷新、证据纠错和方法审议；支持单阶段及定向维护，接续已采纳报告，不替代普通公司投研。
---

# 股票研究框架维护

从技能目录向上找到含 `framework/`、`projects/`、`research/` 的仓库根，读取 `AGENTS.md`；输出与日期遵循 `research/README.md`。`AS_OF_DATE` 用指定日期或北京时间当天，历史研究不使用未来证据。默认本地保存；只有明确授权 `publish` 才提交、推送或创建 PR，不自动合并。定向维护只处理授权范围，不重跑市场研究。

## 选择范围

| 模式 | 读取与执行 | 结束边界 |
|---|---|---|
| `research` | [元研究](references/meta-investment-analysis.md) | 保存 market-research，不自动采纳状态、比较或修改框架 |
| `compare` | [变化检测](references/investment-change-analysis.md) | 用指定报告分类并保存 change-decision，不自动修改或采纳 |
| `adapt` | [框架适配](references/investment-adaption.md) | 只处理变化报告批准范围，不自动 compact 或发布 |
| `refresh` | [维护接续](references/maintenance-handoff.md) | 按既有方法刷新受影响状态/证据与待复评，不强制全市场重跑 |
| `full` | 元研究 → 变化检测 → 维护接续；有正文变更才适配及共用 `framework-condense` | 本期研究、独立状态/纠错交接；方法提案另列 |

方法、参数及歧义以**已采纳** `framework/investment_framework.md` 为准，compact 是保真导航；待审分支、上期提案和仅日期较新的报告不是有效规则。版本标签只用于识别，不替代两份正文哈希。方法与观测混排的 D 层仍是方法正文；仅唯一受限 observation JSON 块允许独立状态差异，规则阈值、适用对象、动作、AND/OR、例外和解除条件不能写入该块。

## 完整周更

1. 检查工作区与本期既有产物。`local` 不自动 fetch，记录远程新鲜度限制；已授权发布时安全同步 `origin/main`，不夹带其他改动。同日同输入复用，不同输入默认隔离 `-rN`，不覆盖旧报告。
2. 读取[维护接续](references/maintenance-handoff.md)，用 helper 选择截至研究日、与已采纳方法兼容的明确 adopted handoff。未桥接历史只能当历史证据；先核验相关 Git 合并/明确采纳事实，再为历史正式报告建立一次桥接。首次无实质基线不虚构比较，但仍可在既有规则下刷新当前状态。
3. 执行完整元研究，保留全文；变化检测同时比较新证据与当前方法，不仅比较上周文字。逐项分类 `state_refresh` / `evidence_correction` / `method_change`，允许同一期包含多类。
4. **没有方法修改也完成状态/纠错接续**：保存研究、变化报告及采用凭证，更新受影响观察与待逐股复评。`update_needed` 仅保留为 `method_change` 的兼容别名，不再表示“本期无事可做”。状态应按当前证据和既有方法重算，不能继承旧正文“当前”断言；数据缺口保留 unknown。
5. 方法变更另做完整定义、经济理由、正反及边界场景、兼容影响；未采纳提案不影响当前状态计算。需修改 canonical 正文或观测块时在分支/隔离 worktree 局部适配，再同步 compact（读取 `.agents/skills/framework-condense/SKILL.md`），无正文变化不做无效精简。方法 PR 未合并不阻断已采纳方法下的独立状态/纠错 handoff。
6. 运行 helper 结构/来源检查与相关回归；声明它们不证明研究语义、方法有效性或真实交易执行。返回日期、三类判定、方法采纳状态、已采用 handoff、待研究及报告路径。

## 发布与后续复核

- 已授权完整 `publish`：本期研究日志及已核验、明确采用的状态/纠错 handoff 与其冻结来源可独立提交并推送 `main`。canonical/compact 的任何改动（含 observation 块）仍走单一框架 PR；不因“只是状态”扩大直接改 main 的授权。研究日志写清方法提案未采纳，不在日志中把新阈值当有效规则。
- 同期已有分支/PR 时核对后复用，名称默认 `codex/`；方法 PR 正文写问题、行为变化、经济理由、边界验证、兼容影响与未验证事项。创建后附加到当前聊天，等待人工合并。单阶段发布只限明确授权产物。
- 研究日志与框架的采纳是不同动作；合并后核验实际两份正文哈希，再写新的 adopted handoff 接续方法。不得通过重写旧 handoff 把历史 proposed 改成 adopted。
- 保留每周全市场研究；财报、政策、重大风险证据或既有解除条件变化时局部 `refresh`，只重评受影响公司。触发只生成待复评，完成必须有对应公司报告/JSON 凭证。研究完成不等于交易，股票无需每日全市场重跑；不改现有个股研究冷却期。
