# 失败 DSH 席位恢复与来源合并实现

2026-10-24，Asia/Shanghai。生成端 Codex。用户明确授权在保留 Codex 与全部失败后，补齐机制、测试审查，再补跑今日失败席位并观察正常晚间消费。

## 交付与规则边界

恢复使用唯一 intent、新 DSH-only request 和私有运行目录，按原封口/请求/方法快照 SHA 绑定；不重生成 Codex，不改原始批次。每席最多2次、每次3600秒，沿用原 DeepSeek Flash/high、同端基线和冻结交付合同 two-price-controls/v4。全部原尝试及两端均须终态、对应进程组已消失；原尝试时间、claim、请求绑定矛盾则拒绝恢复。成功、拒绝、冻结或无报价研究不能借此重跑。

新输入继承原 canonical/compact、维护来源和 DSH 基线，不重新选择模型/方法，也不复制 Codex 答案。正常冷却历史识别已验证恢复，仍归原轮，不重置日额度、冷却或 daily-check。成功必须重新核原生 ordered completed 终态、process/entry/receipt、运行库绑定、全部输入与产物及共享验收，才生成 research-sealed-recovery/v1。失败保留新尝试但不发布成功补充。

正常消费者先处理原封口再处理合法补充，分别验证各自请求。精确复用 Codex 原 record/backup/source/available_at，只登记新 DSH。CSV目标行和同日报价冲突在写入前 held；双来源稳定读锁覆盖提交，支持幂等重放和其它股票变化时的安全重基，不覆盖同证券改动。原共识权重、席位、拒绝/缺席、monitor选择、R14/all-of和旧控制延续不变；条件 Coze 适配有效配对，但现有 Coze 保持 PAUSED。

## 测试与独立审查

- Methods 全量1166项通过，225.221秒；新增恢复定向33项通过，独立最终真实本地合成CLI集成16项通过。原 runner95、runtime21与冻结恢复9项亦通过。全量首次运行发生测试编写期间的暂态失败，原日志保留，定稿后全量通过。
- AI 广回归811通过、2个需要显式methods路径的用例随后opt-in全部通过，共813个唯一用例。33项恢复用例包含2个无mock的冻结执行→真实loader→临时报价库/CSV完整链，最终methods源码定稿后再复验2项通过。
- AI既有一项CSV测试读取未启用skipinitialspace，隔离执行HEAD原测试/原consumer也复现同一失败；只修测试读取方式，未改生产CSV格式。原失败和HEAD复现日志保留。
- 独立审查 PASS，无未解决P1/P2；AI六维检查通过。发现的自然终态复验、全部父尝试结束、影子报价库隔离、真实Coze文件名和同时间跨轮排序、延迟导入问题均已修复并回归。
- 保全清单中402个原批次/报告/封口文件逐字节未变；原4份Codex、8次DSH失败保留。源代码、报告、测试与审查的SHA和日志在审计目录；原canonical/compact原始SHA未改变。

## 本次恢复与后续验证

恢复ID `4d633500a49c4b8197e43914ed7799c5`，依次恢复 HK-02513、HK-09988、SH-601021、SZ-002371 的 DSH。原目标仍为 `8094449450ca4f9686712d08850579ca`，原首次正式生产8次超时结论不被恢复替代。新请求SHA `40b8db6afbaf7f052fbc5b171a1d17dae910b8159a524b5a09c68a80b570ee1d`。

首席于10:23:06.202801实际启动，stdin_transport=frozen_file，已产生原生session/事件；当前在途，不能判自然完成或研究质量通过。运行日志：`output/audits/investment/2026-10-24/dsh-seat-recovery/production-recovery.log`。本报告只记录机制验收与已启动状态；各席最终终态、研究语义、工具、费用及正常消费另由既有一次性跟踪汇报。

用户单独批准空闲重载AI调度器。10:24前核无在途job、无startup catchup、无待恢复重试；仅重载该服务，旧PID5261退出，新PID6255运行，无新增任务start。未手工调用消费者、写CSV/共识或启动Coze；原22:00正常消费保留。

已在 [DeepSeek官方价格页](https://api-docs.deepseek.com/quick_start/pricing/) 核验今日周六全天谷价。Flash按每百万token美元：uncached输入0.15、cache-read0.003、输出0.6。费用以后续实际主/子/辅助/恢复usage计量，未知保持null；全部总额目前null，不把已知下界当账单总额。原8次失败费用单列，不能报0。此次验证未证明投资经济语义或实际账户账单。

审计位置：`output/audits/investment/2026-10-24/dsh-seat-recovery/`。既有 `dsh` heartbeat 继续观察新恢复及今晚正常消费，原目标不替换；不新增监控，完成后才停用。
