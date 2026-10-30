# DSH 首次正式投研、失败席位恢复及正常消费观察

完成日期：2026-10-24（Asia/Shanghai）；审计生成端：Codex。本文记录固定首轮及用户随后明确授权的补充恢复，不新增研究、不修改原稿或评分，不手工写入共识。

DSH 启动投递修复后，四个补充席位全部首尝试自然完成；正常晚间消费者在 22:08:28 完成原批与四份恢复补充，来源、报价、CSV 事务及旧约束保全核验通过。三只股票形成 Codex 与 DSH 两席数值共识，智谱贡献明确拒绝报价及控制、监控。四只的 entry/add 仍全部 blocked。研究经济语义仍有明确缺口，不能将结构验收和发布成功称为完整研究质量通过。

## 固定观察对象与原失败

- 首个正式调度 run_id：`research-bf7380182d2b4c14bb9c782441519a29`，原批：`8094449450ca4f9686712d08850579ca`。
- 标的：HK-02513、HK-09988、SH-601021、SZ-002371；未换批次或选择后续成功样本。
- 原四份 Codex completed；原 DSH 首试与原策略重试共八次全部启动超时，09:08:16 走完原策略。原 DSH 无原生会话/有效 usage，真实模型和费用未知。监督清理后的 exit0 不构成自然完成。
- 原请求 SHA：`de7f70147c4330f63778e2ea4194911f8f61f63a6c93cd52018cf0f09428c0c8`；execution-plan SHA：`ae0760de22ef667df325fa90cb8900573a79b04c5051a24f9a82edc6aed7e167`。
- 唯一恢复：`4d633500a49c4b8197e43914ed7799c5`，新请求 SHA：`40b8db6afbaf7f052fbc5b171a1d17dae910b8159a524b5a09c68a80b570ee1d`。仅补四个失败 DSH 席位，独立冻结原包、方法、同端基线及 DeepSeek Flash/high，不重生成 Codex。

原失败、原 Codex 成果、恢复输出分别保留。晚间终态复核的 402 个保护文件全部原 SHA 不变。

## 修复、回归与部署边界

启动根因是 Python 3.11 的分段 stdin 投递：首轮 `communicate(input=payload, timeout=0.25)` 超时后改传 `input=None`，可能留下未完整写入的输入，DSH 等待 EOF。修复改为冻结文件 stdin 完整投递；原日志与失败结果不改。

启动修复提交 `7b30571db18205f15c589a705c2b3dfd8e525ba5`，当时全量 1135 与实际 Python 3.11 定向 95 通过，独立审查无阻塞。恢复/来源合并机制 Methods 全量 1166、AI 813 个唯一回归通过，另有定向及独立真实冻结输入集成验证，代码独审 PASS。上述为实施阶段实际测试，晚间观察没有额外运行研究或测试生成。

恢复机制已本地提交：Methods `b6f6435f9a97905c3cf5d3b8b582679cddec2110`；AI `ef3704109d74a328e45f83f1f783263ceece4d81`，均未推送。用户另行批准的一次 AI 调度器空闲重载已于上午完成，未触发任务；本观察未再重载。

18 项测试/审查快照中，16 项源码、测试、ADR 等字节仍一致；AI `CHANGELOG.md` 与 `docs/contracts/system_boundaries.md` 因后续独立策略提交 `4267bd1` 改变。实际恢复 consumer、quote store、writeback 源码及共识权重配置与已测版本一致。本观察不评价后续其它策略变更，也不声称整仓无漂移。

## 自然完成与工具稳定性

| DSH 恢复席位 | 首尝试实际运行（北京时间） | 子会话数 | 已知生成下界 USD |
|---|---|---:|---:|
| HK-02513 | 10:23:06–10:37:21 | 0 | 0.139990002 |
| HK-09988 | 10:37:22–10:52:18 | 1 | 0.167022450 |
| SH-601021 | 10:52:20–11:11:11 | 2 | 0.240207810 |
| SZ-002371 | 11:11:13–11:20:13 | 0 | 0.085274094 |

四份 process 均 completed，driver exit0；CLI 均严格有序 session→turn_start→匹配的 completed turn_end→最后唯一 final。四主、三子原生会话均最终 completed turn/end，工具和后台 job 收尾，进程组无剩余，runtime patch/plugin 与冻结输入完整。实际模型仅取原生 header，均为 deepseek-flash。各席至多两次的原策略恢复额度均只使用首尝试，未使用额度不转为新增授权。

真实工具 616 次，call/result 全部配对，384 个 job 注册与收尾闭合。八次 edit/web_fetch/read_image 错误随后恢复并自然完成，应计入工具稳定性，不能误报研究终态失败。三子会话最大同时在途二、深度一。Jev 四次真实 route 均为精确位置跳过，backend=0、fallback=0，不能称已实际使用后端筛选。

PDF 原页文字通过 PyMuPDF 读取；春秋子会话另读 CAAC PDF 第一页图像，温度长图超限后分片读取成功。五次 read_image 中四次成功，未声称所有 PDF 页或图表均视觉核验。bash exit0 可能仍含 HTTP403/404/空返回，工具成功数不等于所有取证成功。

## 正常晚间消费与真实贡献

正常任务 `research_writeback_evening` 的 run_id 为 `task-research_writeback_evening-20261024-220039-3ff30977`，22:00:39 开始、22:08:28 结束，正常 ledger 为 success、mode=apply、held=0。没有手工触发消费者或 CSV。

早间已消费阿里、春秋、北方三个原 Codex 单席；智谱原封口晚于早间机会，本次先于 22:06:44 完成 base，再于 22:07:14 完成恢复。其余恢复分别于 22:07:38、22:08:02、22:08:28 完成。全部满足 base 先消费、后补充的顺序。

| 标的 | 最终 CSV P1 / T1 | DSH 真实贡献 | entry / add |
|---|---|---|---|
| 智谱 | 空 / 空 | 双端明确拒绝报价；控制与监控，无数值共识 | blocked / blocked |
| 阿里巴巴 | 37.93 / 85.75 | 两席同价参与，原始值 37.928 / 85.751 | blocked / blocked |
| 春秋航空 | 31.38 / 58.19 | 两席等权，原始值 31.38 / 58.185 | blocked / blocked |
| 北方华创 | 260.33 / 547.39 | 两席等权参与 | blocked / blocked |

价格单位按原标的：港股 HKD、A 股 CNY。这是系统已发布值的审计，不构成新的估值或交易许可。P2 按原 retired 政策为空。春秋航空原始研究 mode=observation，资格仍受独立 entry/add 约束阻断。四份监控按现有选择规则均选 DSH；持仓约束保持 unknown 或 review_required，不转换成退出指令。

三份早间 Codex 完整 quote record 逐值等于恢复前基线；智谱今晚 base 创建原记录，恢复精确复用。四份旧 record_id、backup_id、source_id、available_at 均保留，只新增四条 Claude 业务席位记录，真实 generator=dsh。补充记录的双来源 provenance 带本次发布时刻，没有改写独立旧 Gemini 记录的可用时间。每股仅 Gemini 与 Claude 两席，没有 Claude/DSH 双票。

八组 before/after/preview/publication/completion、seal 与 local quote 哈希链一致；每次只追加目标股票一行，原历史及其它行逐值保持。四份恢复组成连续完整 CSV 链，最终 CSV SHA 为 `5e956cd6a05958e1df4ad19849e313cff5e0256b0910b1f944883cac5d98b74f`。22:15 正常报价备份另已确认四个新来源。本实现没有单独 transaction.json，事务证据由上述文件及模型历史/备份回执闭合。

原共识权重配置 SHA `d2809d079335fe9a4e95971ce2a99097f1a0d97e21f5f75d74e788a1d476ae1c` 与已测提交逐字一致，两有效数值席位归一化等权，过滤/缺席/拒绝及监控选择按原规则。Coze 自动化仍 PAUSED，无第三席调用。此次未实际遇到同日报价冲突，不能将回归覆盖的 held 分支描述为本轮生产已命中。

## R14、全部约束与研究质量保留项

四份 report/JSON/acceptance 与原文 SHA、精确引句已分别独审。实际冻结 two-price-controls/v4 增加公开 monitoring 摘要，保留 v3 的 R14/all-of 门禁；不能将切换后 v4 工作区合同冒充切换提交已验证。canonical 与 compact 原 SHA 至终态仍分别为 `773677164aee09f006d80afda8e7484f00b05a489061903754b7f76ffec78ed7`、`57d9a8e4530e32e53a5d06ab80dc7244d3dc67fd28d95951890dc68c25453ea2`。

四份 R14 总体压力结果均 unknown，真实持续 add 约束分别为 R14、R14_COST_BRIDGE、R14_20261024、R14-2026H1。智谱四输入 unknown；阿里、北方仅 exposure supported；春秋虽有 exposure/cost supported 和传导 bounded 声明，但 OCF 桥 unknown，且传导上界有下述语义问题。没有以历史正 OCF、一般假设或无关约束替代 R14 后判 passed。

实际持久化 full controls、compact claims、evidence SHA、CSV 与 preview 逐项一致。原 active claim×scope 为 17/15/6/10，合并后 32/29/10/18；原、新独立主张内容哈希均无丢失，各 scope.refs 覆盖登记的全部 active ID。独立约束合取、单条内合法 OR 及 holding/runtime/observation 边界保留。

- 阿里原 ALERT_GOV_202610 holding/unknown 保留；DSH 的无 covers clear 仅存为 conflicting_evidence，未抹掉原治理主张。
- 春秋原 TEMP_RESEARCH 与 DISCLOSURE_20261024 entry/add 均保留；同 ID 的两源 R14/holding 主张亦保留。
- 北方原 SOURCE-RD-2026H1 entry/add 保留；同 ID 新旧 R13/R8/R6/R14/HOLD 独立主张均保留，DSH observation 或 null baseline 未自动解除。

这证明本次真实合并没有因换端、缺席或无充分 covers 的 clear 删除旧约束；本次未发生充分证据实际解除成功样本，不能扩展为该分支已生产实测。登记集合一致也不能证明报告已涵盖全部经济条件。研究质量仍有以下发现，保留原文、不修稿、不改分：

| 标的 | 仍存问题及实际边界 |
|---|---|
| 智谱 | R13 当前独立条件的完整恢复覆盖未证，旧 Codex 也无独立持续 R13 保护；同一可转债本金在净现金后再次扣减，压力测算偏保守但算术错误。 |
| 阿里 | 治理 clear 未精确绑定原告警及持续义务履行证据；TEMP 等价 runtime 接替未证。原治理 unknown 已在真实合并中挡住无证解除。 |
| 春秋 | 0%–17.5% 传导上界由整体收益率增量/整体航油成本增量相除，混合运量、结构和票价，缺可比因果桥；18% 静态压力假设不是核实的未来 OCF 桥。总体 R14 仍 unknown。 |
| 北方 | TEMP 未全量登记且无等价 runtime 证明；研发附注写 p128，实际 p136，两个研发口径差额尚未桥接。旧 SOURCE-RD 仍限制新增。 |

四只 entry/add 仍 blocked，未观察到本轮实际错误放行；上述问题意味着不能宣布完整经济语义或研究质量全面通过。此次仅四个恢复席位，亦不足以推断长期稳定性或与 CC 全面等效。

## 生成费用与未知

七个原生会话按 session+message 去重后，516 条主/子 usage：uncached input 956,270；cache-read 70,602,752；cache-write 0；output 462,076。Anthropic input 为 uncached，不再减缓存；推理已含输出，不重复计数。

官方价格在当日 11:47 已核：[DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)。本轮周六调用均在谷价，Flash USD/百万 token：uncached 0.15、cache-read 0.003、output 0.60。已报告生成下界为 **$0.632494356**，统一同率折算的已知部分相同，不是账单精确值。

116 条辅助搜索请求无 usage，加七个标题的付费请求覆盖未知，共 123 条覆盖缺口记录，不能解释为准确的付费请求次数。服务器 search/fetch 免工具费不证明辅助生成 token 免费。**完整恢复费用=null；原八次失败加恢复费用=null；含原 Codex 总费=null。** 原失败与标题未知不记零；Codex 实际模型/全费用未知，不套 DeepSeek 费率。count_tokens 显式事件观察数为零，但完整实际请求、token 和费用仍 null，未补调用或按字符估算。

## 核验材料与结束边界

审计根目录：`output/audits/investment/2026-10-23/dsh-first-production-followup/`。

- `evening-source-audit-20261024T222041+0800.md/json`：71 份原始证据、逐项发布/来源检查无失败；JSON SHA `6e9d1efb2887df2fe833734eda192845ffc0927fc77e6200c33f7d569ba9235c`。
- `evening-controls-audit-20261024T222015+0800.md/json`：逐 scope、claim、原句、完整 evidence 与实际 CSV；JSON SHA `8b3e7ab84cec9080a10b3b60b1b72b318c681d204e9646b86a4ca1ce04e5f6a5`。
- `tools-usage-recovery-terminal-20261024T115316+0800.md/json`：75 份终态证据及费用覆盖；JSON SHA `1efbf4cc88bfc6f092fcef8a4c85b179ec0c318f83152fb5734271ff227c8369`。
- 四份 `semantic-recovery-<task>-<timestamp>.md/json`：原文定位、精确 source SHA、质量发现及限制。
- `observations/20261024T221823+0800-evening-terminal-preservation.json`：402 原件保全及源码/文档差异；`observations/20261024T221939+0800-evening-service-evidence/` 保存真实 ledger/events/config 哈希副本。
- 原失败工具/费用、原 Codex、早间消费者独审，以及上午修复/回归/代码审查/提交记录全部保留，不由本文或新成功样本替换。

固定原轮、授权恢复及其首个正常可消费结果现均明确，本次观察结束。最终收尾回执记录唯一 dsh heartbeat 的删除结果；其它自动化保持原状态。后续研究只由既有正常调度执行，本文没有启动新的研究、写回或补跑。
