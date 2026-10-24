# 2026-10-25 接续独立核对

generator=codex；审阅时区 Asia/Shanghai；独立只读审阅。本文不执行 publish/collect、不修改源文件，不代替本期行情、产业和事件核验。

## 实际采用基线

- 审阅时 worktree HEAD 与 origin/main 均为 `76abde55d73f21310cb263fe448dc5a505e89ade`。canonical v3.0、skill `maintenance_contract=futures-maintenance/v2`、handoff/refresh/continuity 三入口均存在且工作区字节与 HEAD 相同，不存在 deployment_missing。
- canonical SHA-256 `41fd0ab17d6efebd9dc258069fb969228c85ae94138cd3b3a65545b30d38732b`；有效规则及计算依赖身份 `c3b3f87f039c46fda68f8d584f28d9496529a166100526c44c04cb564c879a55`。完整文档状态引用改变没有改变该有效身份。
- Git 本地已取到的 main 历史含 PR #49 merge `1a432425916e4e822a234fe7f1370da3071c4050`，合并时间 2026-10-18 15:31:00+08:00；其父分支提交 `9a52f3c` 为状态引用更新。`git merge-base --is-ancestor 1a43242 origin/main` 返回 0。故上期状态 PR 已实际被 main 采用，不能沿用 memory 或项目状态中的“尚待合并”旧结论。`gh pr view 49` 本次网络连接失败，PR 采用结论依据 Git merge 及祖先关系，不声称 GitHub API 本次验证成功。
- 当前按类型正式采纳的 market/audit 均为 10/18 handoff：market hash `9af05bcbf7982e573f71e5535dd929e51193e332eda08c204ea81ca48c0adeae`，audit hash `d3c5d076008d76e2f56e269f3e5956e942225d6f34ae6440287dec9d7ae47a1c`，读取字节均匹配。10/18 严格早于本期，可作周环比基线；其行情仍是 10/16，不能当作本期行情。

## 共享原件完整性与范围

读取主 checkout `research/futures/local-continuity/index.json` 及所有登记对象，使用现有只读 `load_entry` 完整核每个 entry 的内容身份、所有引用文件 SHA-256 和字节数。审阅时 9 个 entry、90 个唯一对象均通过，且 9 个 entry 的有效方法身份均与当前兼容；无须 v1 迁移或 allow-historical。第九条 `20dd9789…` 是主编排器本次将确切 main 10/18 handoff 收录所得，本文没有写共享存储。

主编排器 collect 结果包含 9 条 review_scope、12 组 corrections、1 项 clock 冲突，requires_plan_reassessment 和 requires_method_reassessment 均为空。plans.json 只导出 MA 数字旧计划；M 被 clock 冲突排除。不能据此漏掉 M 或其潜在实际持仓管理。

已知原 opportunity_id 共 9 个：

| 原 ID | 原时钟与本期用途 |
|---|---|
| `20261011-observe-M2701-trend-short-v3` | 10/09 历史观察，无触发信号、无登记计划；由本期 M 覆盖，不把 10/15 新事实倒填到此 ID |
| `20261011-observe-RB2701-trend-short-v3` | 历史观察，无实际信号/有效期；旧条件阈值和 10/12 条件日期不是当前计划 |
| `20261011-observe-MA2701-trend-long-v3` | 原 signal 10/09，registered `2026-10-11T18:14:54+08:00`，valid_until 10/13；保留原数字计划供条件持仓复核 |
| `20261011-observe-SR2701-trend-unknown-v3` | 历史观察，signal/registered/valid_until 均 null |
| `20261011-observe-CF2701-trend-unknown-v3` | 历史观察，signal/registered/valid_until 均 null |
| `20261011-observe-MA2701-MA2705-economic_reversion-unknown-v3` | 历史 V 研究，未有合格事前经济锚，时钟均 null |
| `20261011-observe-RB2701-RB2703-economic_reversion-unknown-v3` | 历史 V 观察，时钟均 null；旧 no_signal 不作当前 V 完成判断 |
| `20261011-observe-SR2701-SR2705-economic_reversion-unknown-v3` | 历史 V 观察，时钟均 null；旧 no_signal 不作当前 V 完成判断 |
| `20261015-observe-M2701-trend-short-v3` | 原 signal 10/15，registered `2026-10-15T19:30:56+08:00`，valid_until 10/19；原入场用途已取消且本期日期已过期 |

10/18 audit 另有按当期日期写的无 opportunity_id 价格筛选/V 研究对象；它们没有已登记信号计划，不构成隐藏真实持仓。原 9 个 ID 留在 review_scope 与材料中。账户、成交和挂单始终 unknown/null，没有已核真实持仓，也没有已核退出的事实。

## 唯一显式冲突及当前裁决

collect 的 `original_clock_or_identity_changed` 来自 10/15 首稿 `23f2be40…` 把 M registered_at 留 null，与明确采纳 r2 `7cdda2de…` 补入真实 19:30:56 不同。核 10/15 handoff corrections：r2 **仅补研究候选实际登记时间**，没有新数值计划或交易许可，原 signal 10/15、deadline 10/19 不变；原 manifest 已备份在 handoff-history。10/18 main 审计及 reconciliation 已再次明确采用这项来源裁决。

本期应保存原 collect 的冲突，另写本期 reconciliation 复述这一已核补记依据，将 M 纳入当前人工复核；不能删除首稿、更改旧 entry、忽略冲突或把 null 无来源地改成当天时间。当前 M 的 registered_at 仍为 10/15 19:30:56，不能采用 10/18/10/25 的审计时间作新登记。

10/18已核 M 原信号允许 Entry 3292–3326，而 10/16 close 3281 已越出原带，取消原入场用途。该原机会本期又已越过 10/19，保持失效。10/16工具机械下破及其 10/20截止仅留原始价格筛选，不给同一机会延窗；这也不是“连续突破一律禁止”的新规则。真正后续独立机会如需研究，要用新行情和身份依据单独论证。

## MA 原计划和条件持仓管理

MA 原参考 Entry 3338、初始 SL 3139、范围 3289–3387；10/12假定入场最晚退出11/06，10/13假定入场最晚退出11/09。两者是原研究假设，不是成交事实。按真实成交价重算的初始 SL 可不同，真实跟踪 SL 还可能已收紧。需要本期 MA2701 专属 OHLC 和最近 10 个完整交易日通道，而不是本轮 T 主力合约名称是否仍是 MA2701。

原入场10/13截止早已过去；不能因价格回到旧范围恢复入场。若有真实持仓，按真实成交/止损历史复核初始止损、只收紧的跟踪止损、逻辑失效、事件压力和原20日退出，不能把 entry expired 写成已平仓。10/18只有“10/16最低3146未穿参考3139”的有限事实；本期不能继续引用该旧最低价声称当前未触发。无成交先后和真实 SL 只给条件管理，不报收益或统一止损成交。

MA G2 blanket pass 已被10/12纠错撤回，低港库和 MTO 需求负反馈不能互相抵消成自动 pass；本期需当前同口径供需和反证。MA 合约最后日旧冲突为 API 2027-01-14 与早先规则/日历推算01/15，应继续核官方边界并将原计划日历和行情缺口分列；不能以已 expired 省略潜在持仓管理。

## 锚维护与方法判断

10/18正式锚包 anchors=[]、withdrawals=[]、signal_observations=[]。没有待撤回的有效旧锚；不应制造 withdrawals 或把单纯未列出解释为撤回。其 MA2701–MA2705、RB2701–RB2703、SR2701–SR2705 三项 research_gaps 的 next_review 是10/23，已经到期，需本期真实研究更新具体缺口、恢复条件与下一复核事件。旧 V 的 no_signal 结论不能越过当前无锚 unknown；10/18已经以 incomplete/research_only 管理三对。

本次只读审阅没有发现需要改变 T/V 参数、范围、止损或核心风险规则的缺陷。反复暴露的 clock 冲突是历史元数据纠错/人工裁决接续，现有契约要求明确处理；文案/状态日期变化不能让有效方法身份失效。无信号、行情反向、账户未知或仍缺数值锚均不足以提 method_change。建议本期 method_change_needed=no、FRAMEWORK_UPDATE_DECISION.update_needed=no；state_refresh 必须继续，evidence_correction 按本期实际新发现判定，历史纠错持续透传，不把重复透传硬说成新增方法变更。

本期审计应特别核：M/MA全部已知存量线索优先、原 ID/时钟不变；五品种实际行情日与完整快照；旧合约独立日历与价格缺口；三条 V 有序合约对和经济锚研究；只给 null 账户下的条件管理。此独立审阅不证明真实 API 新鲜度、当期经济结论、G1–G6通过、收益可复现或交易许可。
