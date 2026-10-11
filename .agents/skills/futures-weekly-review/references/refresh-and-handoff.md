# 行情刷新与版本接续

本协议用于 full/refresh 及修订后的接续。输出位置遵循 research/README，方法与数值只取 canonical；工具提供结构/计算核验，不授予 ready、交易或发布权限。

## 1. 启动与实际版本

- 本地任务记录实际 canonical、脚本修订和输入来源。自动化从最新 origin/main 建隔离 worktree；先核 v3 方法、技能的 `maintenance_contract=futures-maintenance/v2` 及 `scripts/futures_handoff.py`、`scripts/futures_refresh.py`、`scripts/futures_continuity.py`。任一未部署则记 `deployment_missing`，明确缺件并结束依赖步骤；不回退旧流程，不夹带本地未发布修订。
- 读 `docs/context/environment.md` 选择可用解释器，继承 TUSHARE_TOKEN，不输出密钥。方法文件版本名相同仍须核实际修订/hash，不能以 v3.0 字样代替内容一致性。
- 周度自动化按已有 full+publish 授权执行；日频轻量任务仅本地保存，其存在不授予 Git 发布权限。两者必须读取同一本地共享采纳入口，接续计划、纠错和 V 锚；memory 只作提示，不能承担唯一交接。共享的 local 材料不冒充 main 已发布结果，周更仍独立核当前行情。

## 2. 明确采纳，而非猜“最新”

正式交接文件为 `research/futures/weekly/<date>/<date>-handoff.json`。同日修订仅因明确登记而成为采纳输入，不能按最大 -rN、文件时间或旧报告自称“最新”选择。

```sh
python3 scripts/futures_handoff.py resolve --as-of YYYY-MM-DD --kind execution-audit --scope local
python3 scripts/futures_handoff.py resolve --as-of YYYY-MM-DD --before --kind market-research --scope published
```

- 当前候选/纠错与市场比较分别按产物类型解析；`--before` 只用于严格早于本期的市场基线。只有审计的新登记不能遮蔽已采纳市场报告；同类型最新记录损坏也不能为运行而退回旧稿。单阶段用户指定报告时按指定路径读，不偷偷替换成另一份。
- handoff 绑定精确 market-research、execution-audit、可选 change-decision、方法版本/修订、行情日、文件 hash、supersedes 及 correction_scope。市场报告和审计可来自不同修订，纠错范围决定哪些旧说法已被替代；不能把整份 r2 全当作 r3 已核。
- 被登记材料缺失、hash 不符、版本不兼容，明确 `handoff_invalid` 或兼容性缺口，不能静默回退到旧已发布记录。没有 handoff 才按 research_paths.py 严格正式名发现，并显式标注未建立采纳记录；不得自动提升未登记 rN。
- 完整文档 hash 保留溯源；候选兼容性按实际规则与计算依赖核验，文案、链接和状态变化不自动作废旧计划。真实依赖/规则变化或身份缺口须说明受影响项并重新评估，不能靠相同 v3.0 字样或静默补 hash 认兼容。历史不兼容时显式 `--allow-historical` 仅接事实、原 ID/登记/有效期和纠错；不复用执行判断或旧参数，不重启窗口。无实质周环比基线明确不可比较，本期研究仍继续。
- v2 manifest 记录有效规则及 strategy/risk 计算依赖身份，采集器变更另留溯源并重验当前数据。旧 v1 缺计算依赖身份，默认只供历史读取。只有找到登记时 canonical、strategy/risk/future_data 原件、核原 canonical hash 并审阅来源后，才可运行 `migrate <manifest> --baseline-root <原件目录> --baseline-provenance <来源说明> --method-revision <实际修订>`；工具冻结依据并保留旧 manifest，不得把当前文件假作旧原件。
- published 消费核 manifest、引用/迁移证据以及当前 canonical/helper 字节与当前 HEAD 一致；兼容性另比有效规则和计算依赖，不要求当前完整文档 hash 等于旧 manifest。local 采纳提交后可标 publication_verified；这只证明提交一致性，编排器另核实际 origin/main 已采用基线，不能把 PR 分支 HEAD 当作已发布方法。最新同类型 local 采纳未提交时不能为运行跳过它、选择更旧 published。
- 工具始终返回 execution_reuse=false、requires_fresh_evaluation=true；candidate_continuity_compatible 只表示可接续 ID、证据和旧计划，不继承 ready、账户或有效期判断，当前执行重新核验。

### 日频与周更共享采纳

两种任务启动时，先解析实际 main 已发布的按类型 handoff，将需要接续的确切 manifest 幂等收录，再合并共享 local 记录。若 main 尚无相应登记，明确缺口后仍读取已有共享材料。共享工具默认按 git-common-dir 定位主 checkout 的 `research/futures/local-continuity/`，用内容寻址对象冻结来源；该目录虽被 Git 忽略却是持续状态，不得当缓存删除。隔离任务仅可为交接写此共享数据目录，不修改主 checkout 源文件或取得额外 Git 发布权限。

```sh
python3 scripts/futures_continuity.py publish --handoff <确切manifest.json> --producer weekly
python3 scripts/futures_continuity.py collect --as-of YYYY-MM-DD --out-dir output/<本轮隔离目录>/continuity
```

- `publish` 在此仅指本地共享收录，不是 Git push。`collect` 输出 plans.json、anchors.json、continuity.json 与冻结 sources，按原 opportunity_id/evaluated_at 接续兼容候选并累积纠错。旧计划不因本轮无新信号消失；原时钟冲突显式待核，不采用较晚截止或重启窗口。
- `requires_plan_reassessment` 记录同 ID 的最新无计划处置，旧计划暂不导出为当前候选，原时钟保留供复核；`requires_method_reassessment` 记录方法不兼容事实。两者逐项处理，不能只读取 plans.json；更晚重评也不能延长原窗口。明确撤回的经济事实跨方法保留，不因版本升级恢复旧锚。
- 本轮刷新使用 collect 的 plans/anchors，并读取 continuity.json 的 `review_scope`、来源、纠错和撤回范围完成存量复核；历史账户/候选仅是待核线索，不代表当前账户已确认。实际存量范围按最新处置、原期限和持仓证据确定：过期研究候选不自动成为真实持仓，已核退出不重复按未平处理。不能只跑最新一根价格信号。共享结果仍须新鲜度、规则与计算依赖核验，不继承 ready 或账户。
- 完成审计后收录 handoff；可附 `--anchors <正式锚.json>`、可重复的 `--evidence <本地证据>`。仅维护锚时可不传 handoff，单独 publish 锚。工具冻结引用与附件后，即使源 worktree 清理仍可接续；只记绝对路径或 memory 不算完成。
- 日频用 `--producer daily`，周更用 weekly，手动任务用 manual。周更先重评、冻结 materialized 来源和纠错记录，再形成自己的日志/handoff；按已有授权发布自己的完整引用材料，不把共享 local 自动当已发布。

## 3. 取数和轻量刷新

用户或本次自动化已授权取数时可运行：

```sh
<环境文档中的python> scripts/futures_refresh.py --as-of YYYY-MM-DD --fetch --plans <本轮continuity/plans.json> --anchors <本轮continuity/anchors.json>
```

使用既有冻结证据时：

```sh
python3 scripts/futures_refresh.py --as-of YYYY-MM-DD --input <input.json> --snapshot <snapshot.txt> --plans <已采纳审计.md>
```

有兼容且可接续的已采纳审计时必须显式传 `--plans`；只有确无可接续计划材料时才省略并披露缺口，工具不会自动发现计划。历史不兼容材料先按当前规则重评，原 ID/登记/有效期仍保留。`--anchors <anchors.json>` 传已采纳且适用的 V 观察锚；没有合格锚如实未评估，同时按下节维护研究。`--check-only` 用于输入核验；具体字段以工具 `--help` 及 schema 为准，不猜造数据。

- 输出 `research/futures/refresh/<date>/<date>-signal-refresh[-rN].md/.json` 及冻结 evidence，保留真实 generated/evaluated 时间、方法/hash、最新已完成交易日与覆盖；同日不同输入另存修订，不覆盖原结果。
- 默认刷新五品种 T 的价格侧；V 未提供合格事前锚时记未评估，不当作 no_signal。复用现有 helper，不改参数；筛选通过不等于产业证据、事件、账户或 G1–G6 已齐。
- V 计算前核外层组合、来源键、原料两腿与锚的有序合约对一致。冻结只要求在信号形成前；同日锚由 anchors 文件的 `signal_observations` 提供 near_contract、far_contract、signal_date、带时区 signal_completed_at 和 source_refs，核 frozen_at 早于信号完成且完成时刻不晚于两腿取数/评估。时序未知明确缺口，不猜收盘钟点、不加“前一天”门；跨日冻结不额外要求日内时刻。原计划日历独立于本期 T 主合约名单，V 两腿分别核覆盖及一致性；`calendar_checks` 与 `price_refresh_status` 分开读，缺旧行情不能声称价格已刷新。
- 每个实际交易日收盘后检查，拟入场前再核实际报价、公开适用参数及账户。调度日不保证是交易日；以真实交易日历判断最近完成时点，周末/节假日不造新信号。收盘未完成、日历不足、快照陈旧、抓取失败分别标明，不把数据失败写成 no_signal。
- 沿用原 opportunity_id、原 signal_date 和原 valid_until；重跑、周报或版本更新均不延长两日窗口。到期如实 expired，不重命名同一机会。
- 截止有效日当天缺当前场次证据时读 `session_check_required`，当天列在 `entry_session_checks_required_dates`，不猜具体收盘钟点；越过截止日期才按日期级 expired。登记与信号同日但缺形成时刻时 `registration_order_status=unknown_same_day_signal_completion_time`；可用计划的 signal_completed_at、signal_completed_source_refs 或 V 同对同日 observation 补核，日期级时钟检查不代表登记顺序、场次或下单许可已核。
- 日频先逐一检查全部已知存量计划/持仓的相关公告、经济反证、止损/退出、事件窗和期限，再处理新机会。检查是发现变化的入口，不能以机械工具已发现约束变化为前提。入场窗口 expired 不等于持仓已退出；缺账户输出有依据的条件管理和具体缺口，不推断仓位。至多两个只限制新机会深研；无相关存量时可轻量结束，不重写全市场叙事。
- 输出工具结果后，人工作用域复核及共享审计才可形成/更新计划。缺必要账户保持 null；不自动下单、通知他人或报告无法复现的收益。

## V 观察锚维护

- **研究方负责建锚和复核。** 周更在 canonical 的 V 范围内，优先研究有公开、可复算经济证据的组合，形成未来适用的观察锚。记录有序合约对、来源/观测日、数值计算、锚类型、机制和最强反证、适用月份、真实冻结时点、有效截止及复核触发；它不是完整计划，不代替 G1–G6 或数值止损。
- **锚是持续产物。** 保存到 `research/futures/anchors/<date>/<date>-anchors[-rN].json`，原始研究和来源留在日期报告/evidence；不可变修订通过共享 publish/collect 接续。周更检查现有锚及研究缺口，日频传入仍适用锚并扫描相关失效证据。到期、反证或适用月份变化时撤回当前用途；有新证据可另存未来生效修订。续期不改写旧锚、旧计划或原信号窗口，不拿后见区间筛旧行情。
- 明确撤回写入锚文件 `withdrawals[]`：near_contract、far_contract、带时区 invalidated_at、reason、source_refs，经 publish 共享。collect 按同对最新时点过滤失效锚并保留撤回记录；新文件没列某锚不等于撤回，受影响旧计划仍须复核。
- **按证据推进，不设配额。** 没有可辩护区间就保留 T/观察，并写明必要缺口、暂缺或 research_only、下一复核事件/数据及恢复条件。研究记录应让下次知道待补什么；不要求每周出锚，也不把缺锚变成长期无人处理的通用标签。

## 4. 登记本期接续

完成研究/审计及适用校验后，显式登记实际采纳材料：

```sh
python3 scripts/futures_handoff.py register --as-of YYYY-MM-DD --market-as-of YYYY-MM-DD --scope local --method-version v3.0 --method-revision <实际修订> --market-research <确切报告.md> --execution-audit <确切审计.md>
```

- 可加 `--change-decision`、`--correction-scope` 和可重复的 `--supersedes <原路径>`，将明确替代范围写清。不因日期新就默认取代所有历史内容。
- 首次登记拒绝覆盖；修订采纳用 `--replace`，工具先验证旧引用完整并备份旧 manifest。这只是显式修改采纳指针，不覆盖原报告。
- handoff 的 status=adopted 表示明确选用这些报告，不证明方法已发布生效；scope 仅 local/published。拟议审计保留 proposed_framework_reassessment；其 handoff 仅在更新分支作 local 接续，不覆盖 main 的采纳记录。
- 完整 publish 的顺序：在实际已采用、canonical 与 HEAD 一致的干净 origin/main 隔离基线上，先按授权提交新原料和本期原框架日志 → register --scope published → 提交 manifest 及必要历史备份并核 published 消费 → 将仅含授权日志、原料和交接的提交安全推送 origin/main 并核远端包含 → 从该基线创建或复用一个 codex/ 更新分支，再写状态片段或方法变更并开单一 PR。非快进先同步复核，绝不强推；失败保存本地产物并报告。仅状态更新复用本期已登记 handoff，有新采纳修订才显式 --replace。未提交的 canonical 状态修改也会阻止 published 登记，不能先弄脏基线再跳过校验；必要时先形成待写片段。
- 方法 PR 未合并时保留原采用方法与原框架审计；合并采纳后才登记新方法交接。工具的 publication_verified 不能证明远端采用，完成发布后另核实际 main 基线及引用；不为满足接续而跳过 Git 授权。
- 登记后运行 `python3 scripts/futures_handoff.py check research/futures/weekly/YYYY-MM-DD/YYYY-MM-DD-handoff.json --scope local`，发布消费改为 `--scope published` 并在交接文件提交后检查。结构通过仍不证明行情新鲜、策略收益或交易许可。
- 将实际采纳的 handoff/锚交付上述共享入口；状态引用 PR 未合并不阻断日志或共享接续。拟议方法材料不覆盖现行方法记录，真实规则改变须重评后明确采纳。
