# 项目状态与迁移边界

核对日期：2026-10-11（本次接续股票与期货；ETF沿用原核对日期）。这里记录接续线索，不替代 canonical，也不把历史行情、账户或拟议更新当作当前事实。

## Codex 先行与共享事实（2026-10-29）

用户采纳“先 Codex 完成，再 DSH 基于事实增量研究”。新准备的 Codex + DSH 批次顺序衔接，同股禁止同时启动，其他股票仍可并发；默认与上限均为4个根研究进程。Codex 额外交付带原始来源、摘录与哈希的事实包，DSH 在可追溯复用的基础上独立补证和估值，不接收 Codex 报告及估值结论。旧冻结批次不迁移；失败、重试及 DSH 恢复保持原轮证据绑定。详见[实施与边界](../adr/ADR-20261029-sequential-stock-evidence.md)。本机日频 Codex 及股票周更均已按用户要求配置 Astra / Extra High；DSH 继续原配置。此项改造不更新投资方法或共识计算。

## DSH 接替 CC（2026-10-23）

用户在完成隔离配对后授权正式替换。新批次 Codex + DSH，DSH 真实身份接替既有 Claude 业务席位，同批两者互斥；旧 frozen CC 计划不改。方法、共识、Coze、额度、168小时冷却及历史不变。执行/交接 v2 与旧 v1 并读；本机已于22:34空闲重载生效，原05:00排期与台账保留。结果见[迁移 ADR](../adr/ADR-20261023-dsh-research-seat-migration.md)及[实施记录](../../research/investment/maintenance/2026-10-23/investment-2026-10-23-dsh-production-rollout-codex.md)，不将隔离报告提升为生产研究。

## 执行架构解耦（2026-10-21）

按用户授权完成模型 profile 与本地 CLI harness adapter 的等价抽取，现有Codex/Claude默认、投研方法、参与/共识与Coze规则及历史合同保留；新增显式配置和新批次执行快照，恢复/重试不换读当前配置。定时入口可透传配置但本次未重装服务、未启用新profile、未切换dsh。接口、兼容与后续新增生产身份边界见[ADR](../adr/ADR-20261021-research-runtime-profiles.md)，实际测试/审查见[实施记录](../../research/investment/maintenance/2026-10-21/investment-2026-10-21-research-runtime-decoupling-codex.md)。

## 两价本地采纳（2026-10-18）

用户明确不要求前瞻影子测试，授权根据既有回测判断并完整本地落地。方法标识 `stock-two-price-v1`，新交付 v4/audit-v2，核心 P1/T1 与独立 entry/add/holding 条件；既有60/40预算、阈值及观测块保留。回测中取消区间减仓的效果两市不一致，不宣称收益优势。新正式批次走两价，旧历史与冻结批次保留版本，缺历史条件不补造 eligible；一只股票已发布 v4 后不能由旧共识降级。生产数据不批量重写，下一次研究按新协议自然接续。方法已由用户明确本地采纳；市场证据仍截止原记录，没有伪造新的周度市场研究或状态 handoff。部署与验证见本日 maintenance 的 two-price-production-rollout-codex 报告；后续 review-and-commit 报告记录提交前审查与修复，仍不推送。

## 当前方法与原状态背景

| 轨道 | 方法与状态 | 当前配套 |
|---|---|---|
| 期货 | [canonical](../../framework/futures_framework.md) v3.0；已有T信号可当前重评、在原有效期内向未来登记，不追认旧建议/成交。10/09行情已用v1.18输入重算，MA当前计划见[10/11重评](../../research/futures/weekly/2026-10-11/2026-10-11-execution-audit-r3.md)，实际执行条件与账户未齐 | [compact](../../framework/futures_framework_compact.md) / [数据协议](../../framework/FUTURES_DATA_PROTOCOL.md) v3.0，[future_data.py](../../scripts/future_data.py) v1.18.1及策略helper；新增handoff/refresh/continuity工具，10/11原v1.18真实API刷新通过、行情仍10/09；v1.18.1另修来源身份、未作新API验证；无收益验证 |
| 股票 | [canonical](../../framework/investment_framework.md) 与 [compact](../../framework/investment_framework_compact.md) 本地方法标识 `stock-two-price-v1`；市场证据沿用原记录（正文背景10/11、已有受限观测块10/18），本次未重做行情研究 | 周更三类分流、明确采纳交接与批次正文快照；临时冻结可估但买入受限；R21口径已补齐。股票 PR #45 已合并至 main，当前期货分支接续该方法；`stock_data_pack.py` 尚未找到 |
| ETF | [canonical](../../framework/etf_framework.md) v2.1，八主题、双月评审 | v2.0 格式快照兼容；最近评审为 [10/01 review](../../research/etf/reviews/2026-10-01/etf-2026-10-01-review.md)，正文已于 10/02 修订；旧 monthly-review 不作为现行一期 |

## 待接续事项

- 2026-10-15按用户要求修复自动个股一致性：新准备批次冻结本端报告作折扣基线，发布前核收入/利润率/调整/PE/股本链、风险唯一归属、折扣值/区间变化依据、冻结模式及全部阻断合取解除；D5分等待与重建复评完成，R21退出不直接解冻。新审计嵌在报告，轻量v3及旧prepared/封口兼容，canonical/compact未改；只做本地代码/技能更新，未推送或部署远端。宇通同原包/证据完成Codex隔离r2：V50基准25.64不变，P1 17.78→18.33，仅terminal3%归零；用途由frozen改observation是财报触发不等于轮动承接的纠错，R9/R4仍限制买入，P2取消。原正式结果/latest不覆盖。实现、生效范围、实际验证及限制见[修复与复评记录](../../research/investment/maintenance/2026-10-15/investment-2026-10-15-research-consistency-repair.md)。

- 2026-10-14 Coze 条件第三模型已本机接入：仅沪深A股本轮 Claude/Codex P1.base 按 max/min−1 严格超过10%触发；Coze必须明确P1/T1，原两模型先完成回写。成功补充保留原seal/回执，按原共识及写回消费；报告/JSON以coze独立保存，邮件证据冻结。2026-10-15按用户追加要求，发送15分钟无可归属回复即failed终止，不重试、不发布迟到结果；同批intent/失败历史防重入。招商银行、中国海油、中国神华、宇通客车、金力永磁五个请求已关闭失败，原未匹配报告证据保留，无Coze成功交付。持续heartbeat `coze` ACTIVE，每15分钟仅扫描未来合格新批次。投资调度器已重载。规则见 [Coze契约](coze-research-automation.md)，部署/验证及真实回执见 [接入报告](../../research/investment/maintenance/2026-10-14/investment-2026-10-14-coze-integration-report.md)。

- 2026-10-14 个股报价导出定向修订：新交付采用 `stock-research/v3`，P1/P2 显式提取报告最终报价，不再由导出器从 V50/折扣重新计算；P1 单价仅 base，原报告有区间才保留 low/high，仅区间无基准时 base=null。研究公式与固定参数不变，V50 仍支持原单位换算；latest 与接续兼容 v3/v2 并按估值日期选择。随后按用户明确授权，将本地既有 65 份价格地图逐份对照原报告原位重提取为 v3，不保留旧版 JSON；原报告字节、P1/P2 报价与生成端归属不变。同步重建 latest、重绑 19 份自动研究封口及回执，并通过相邻 ai_investment 仓库既有属主接口校正本地报价和 CSV（中远海控、正泰电器价格行更新，恒瑞医药补入 10/09 行）。65 份结构/价格引用、原文哈希、19 份回执及重复执行校验通过；这次历史重提取不代表重新研究或行情刷新。审计位于 `output/price-map-v3-reextract-2026-10-14/`。

- 2026-10-05 个股入口：`stock-research` 与 `deep-research-auto` 现维护于 `.agents/skills/`，`.claude/skills/` 同名文件为兼容入口。个股最终 JSON 使用 `stock-research/v2`，仅 `meta/price_map/monitoring`；计算工具为 `scripts/stock_price_map.py`，旧 v1 只作复评历史输入，不能直接迁移单位混杂的 V50 或示例价格。10/05 的 600066、01952 报告与 JSON 保留原研究内容（目录迁移仅修正引用），尚未按修复版重新研究；原参数空值、P2/换汇及事实冲突须在后续复评中解决，不能视为已修正价格。
- 期货10/11定向重构已替代此前期货框架适配待办，见[实施报告](../../research/futures/maintenance/2026-10-11/2026-10-11-v3-refactor-report.md)。两策略/G1–G6、30个当前锚与277旧ID迁移保留；[当期研究r2](../../research/futures/weekly/2026-10-11/2026-10-11-market-research-r2.md)已完成，MA的版本时间障碍由[当前重评r3](../../research/futures/weekly/2026-10-11/2026-10-11-execution-audit-r3.md)纠正，旧r2留作历史。后续[更新机制改造](../../research/futures/maintenance/2026-10-11/2026-10-11-weekly-update-mechanism-implementation.md)已完成三类分流、精确[采纳交接](../../research/futures/weekly/2026-10-11/2026-10-11-handoff.json)与真实API[轻量刷新](../../research/futures/refresh/2026-10-11/2026-10-11-signal-refresh.md)。旧影子引擎仅历史，v3轨迹暂人工核验；未核真实账户。随后[复审修复](../../research/futures/maintenance/2026-10-11/2026-10-11-weekly-update-mechanism-fixes.md)补齐跨 worktree 共享、v2 兼容迁移、V/原计划刷新及存量研究；维护合同 v2，原候选 ID/时钟不变。用户已授权将本批期货改动提交、推送并创建 PR，不自动合并；发布分支包含尚未进入远端 main 的期货 v3 前置，排除无关股票提交。PR 合并前不视为 main 已部署；本轮保持 T/V 参数和核心风控。
- 股票 [9/26 change-decision](../../research/investment/weekly/2026-09-26/investment-2026-09-26-change-decision.md) 是历史提案，不能整包视为待执行方法；10/11已合并的股票PR #43完成当期适配及R21保护。本地本次维护进一步修复接续、临时冻结估值及未定义出口，见[审阅报告](../../research/investment/maintenance/2026-10-11/investment-2026-10-11-weekly-update-mechanism-review.md)与[改造及验证](../../research/investment/maintenance/2026-10-11/investment-2026-10-11-weekly-update-mechanism-implementation.md)。
- 期货 9/26 报告称最新快照为 9/19；本工作区另有在迁移前 HEAD 已提交的完整 `research/futures/snapshots/2026-09-21-data-snapshot.txt`（v2.27/v1.16）。本地接续按真实文件、完整标记和各行情日期选择，不继承该旧断言；发布历史接续使用精确已提交采纳；10/11起已授权任务可隔离取得本期新数据，完整核验并提交原料后再用于published交接。9/21也不能代表10/04行情。
- 工作区的完整 `research/etf/snapshots/etf-2026-10-02-data-snapshot.txt` 在目录迁移前 HEAD 已提交；当前新路径仍属本地待提交迁移。按 10/04 评审日距今两天，格式可通过前置；各指数实际行情锚与公开估值、成分、全收益缺口仍须按正文核对。迁移未运行新的行情脚本或研究。
- [ETF 比较偏差与置换诊断](etf-timing-validation.md)、[恒指全收益代理](hsi-total-return-proxy.md) 保存独有历史发现，均待复现。旧收益、显著性、接口成功率不升级为已核实结论。
- 2026-10-05 核对本机 Codex 自动化：期货与股票周更均 ACTIVE，分别调用本仓对应 skill，并在独立 worktree 按既有授权发布；PR #28 监控 PAUSED。未发现本机 ETF 定时定义，远端 Claude Routine 未核验。本次只改输出契约，未更改调度或发布授权。自动化提示词未硬编码旧报告路径，无需修改；远端运行基线需包含完整迁移后才使用新版契约，不夹带本地迁移发布。

- 2026-10-11 本机期货自动化已通过工具更新：周更仍为周日01:00、full+publish；新增工作日19:30收盘刷新，仅本地保存。两者ACTIVE、GPT-6 Sol/High，基于Asia/Shanghai。任务先核 origin/main 的实际方法/维护合同与工具；缺部署则deployment_missing，不回退旧流程、不夹带本地改动。当前本地机制已验证，尚无新配置定时运行结果；初次发布阶段已 fetch，当时 origin/main 为 44f3741（尚无期货 v3 与维护 v2），不能把本地验证或 PR 分支视为 main 已部署。此前632项离线测试及真实行情刷新记录见原实施报告。日频与周更现均已更新为 v2 配置；周更初次审批拒绝后，用户已明确授权自动推送研究日志、为框架修改创建 PR 且不自动合并，现有任务已更新并回读确认，任务/项目/调度/模型保持不变。授权后证据及本次验证见复审修复报告。本次最终700项离线回归及治理/审计/skill检查通过，真实材料已离线接续复跑；尚无新版定时跨日运行结果。此条替代10/05关于期货自动化无需修改的当时结论；股票与ETF未改。

2026-10-11股票自动化后续核对：`automation-2` 已通过工具更新并回读，保留周日02:00、ACTIVE、GPT-6 Sol/High及原项目，继续自动推送研究日志、方法修改创建PR、不自动合并。周更区分三类变化，部署未齐时报告 deployment_pending；本次改造按用户授权提交、推送并创建PR；合并前不声称已在main部署，尚无新版定时实跑。此条替代此前“股票未改/无需修改”的当时结论，完整验证记录见股票改造报告。

## 历史资产的处理

- `.claude/skills/` 和专属项目会话、七份记忆有备份；Codex 使用 `.agents/skills/` 的四个新入口及阶段 references。通用投研、飞书技能与新版吸引子已在 Codex 存在，未再复制。
- Claude 旧“尚未推送”等记忆已落后于当前 Git 历史，不导入为永久规则。`framework/reference.md` 依赖缺失文件，`research/futures/archive/2026-09-13-legacy-output.txt` 为旧期货输出；不替代现行方法。
- 迁移前 HEAD 已提交的五张 9/25 core 卡片属于旧 ETF 方案；现行 v2.1 的八主题边界优先。`research/etf/archive/legacy-cards/v1-archive/` 为首期承接历史，不能从旧卡片推定当前账户。
- `.claude/worktrees/etf-track+day0` 无独有提交且为 main 祖先；原目录仍保留，未删除、合并或当作新入口。`.venv/` 与 `output/` 保留本地环境和缓存，不把它们当作方法权威。

## 私有备份与恢复

仓库根 `.migration-backups/2026-10-04-claude-to-codex/manifest.json` 记录 SHA-256、大小、文件数和原始未提交研究校验值。目录权限为 700，归档/配置备份为 600；整个目录被 Git 忽略。

| 归档 | 内容 |
|---|---|
| `working-assets.tar.gz` | 原 11 个 Claude skill 与迁移前未提交的 11 个研究/草稿文件 |
| `claude-project-history.tar.gz` | 本项目 Claude 会话与七份记忆 |
| `etf-study-2026-09-30.tar.gz` | 原临时 scratchpad 的 38 个回测、预注册、结果和数据文件 |
| `market-data-cache.tar.gz` | `output/` 的行情及原始缓存 |

另保留 `codex-config.before.toml`、`README.before.md`、`gitignore.before`。备份可能含私人会话或账户资料，不作为可共享研究附件。

恢复时先与 manifest 核对归档 SHA-256，用 `tar -tzf` 查看成员，再解压到独立临时目录后选取所需文件；不要直接覆盖当前工作区。Gemini 的注册在本机全局 Codex 配置，回滚该注册时只移除对应 `mcp_servers.gemini-search` 段并保留之后其他配置；完整旧配置仅用于对照，不能覆盖新工作。

## 本次迁移验收

- Codex 本地 app-server `skills/list` 实际发现四个入口，均为 `scope=repo`、`enabled=true`，仓库技能解析错误为零；四项 `quick_validate.py` 通过。
- 离线全量回归 231 项通过，框架结构检查通过。回归曾复现 HEAD 基线的一个 error 和两个子测试失败；仅为两个隔离测试夹具补注入 `daily_settlement_changes` 与 `math` 后通过，未改生产脚本、策略或参数。
- 独立只读场景验收检查单阶段 compare、无更新仍出期货审计、账户/专业资料缺口、ETF 10/04 合格与 10/20 过期前置、缺适配报告时 data-sync 停止，以及精简保真约束。验收为前置检查和任务推演，未执行新的完整投研。
- 四个归档 SHA-256、全部成员可读性、11 个迁移前工作文件原样与私有权限已核验。原 MCP 定义保留；新增配置与文件未出现现有 Gemini/Tushare 凭据字面值。
- Gemini 注册、stdio 握手、工具发现及六项离线回归通过；Codex 本地 `mcpServerStatus/list` 实际加载 `gemini-search` 并发现 `gemini_web_search`。允许联网的真实 API 查询返回 HTTP 400 地区不支持，成功搜索尚未通过；[上期所官网](https://www.shfe.com.cn/) 的内置搜索及正文读取兜底已完成。2026-10-05 按用户要求回退为内置搜索：全局/项目规则、深度研究技能和本机股票/期货周更任务统一使用默认搜索，Codex Gemini MCP 暂停启用，保留服务与凭据配置供以后恢复。

## 研究目录迁移（2026-10-05）

输出契约见 [research 导航](../../research/README.md)，逐文件旧新路径与校验值见 [迁移清单](../research-layout-migration.json)。本轮仅改目录、引用和读写接口，不更新市场判断；历史审计 JSON 与 ETF 冻结预注册字节保留。工作区既有未提交技能与个股研究内容继续保留。自动化读取已提交快照的要求不变，新路径未提交时不能冒充已提交输入。
