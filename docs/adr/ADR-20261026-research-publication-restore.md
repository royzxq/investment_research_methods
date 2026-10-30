# 研究自检文件与发布验收隔离

2026-10-26，用户授权修复洛阳钼业 Codex 交付的文件冲突，并重新验收、恢复已有产物，不重做调研。

原公司/日期/生成端路径没有冲突。原提示词同时允许代理在整个 `execution/<task>/<generator>/` 保存临时材料；代理的自检记录与运行器的独立验收均选用了 `research-validation.json`。运行器在正式发布前以 create-only 写同名文件，失败后保留了暂存报告、原生完成回执和 completed candidate，最终封口记录为 failed。代理提前持久化 Jev 摘要也会使运行器遥测遇到同类冲突。

执行目录根保留进程、冻结输入与原生回执。运行器的独立研究验收、方法兼容性及 Jev 摘要存于 `runner/`；代理的取证/自检仅写 `agent/`、既有 stock-research scratch 或 Jev 的 `materials/`。运行时追加明确的写入边界，原冻结 prompt/input/hash 不变。运行器从实际产物重新验收，绝不采用或覆盖代理自检作为通过证据。

已有 Codex 完成产物只可通过显式 `restore-publication` 恢复。检查原失败封口、停止且 exit=0 的进程、原生回执、candidate 与暂存字节哈希、完整冻结输入/执行 profile、报价和原批次研究验收，再核当前方法兼容性。原报告、JSON、失败记录、原封口及 DSH 产物不改；正式目标有不同内容时拒绝恢复。不启动 CLI、不生成新研究、不重置预算或冷却。

恢复授权使用 `research-publication-restore/v1` intent，绑定原封口和执行证据；私有恢复封口沿用原 request，仅替换原失败 Codex 的 manifest 描述符。面向消费者复用 `research-sealed-recovery/v1`，`recovered_generators=["codex"]`，保留原封口全部字段及原失败来源。与原 DSH 重跑恢复的 intent 严格区分。消费者复用原 DSH 的报价 record/backup/source/available_at，仅补登记 Codex；CSV 行发生外部修改时继续 held。两价条件合并、共识、Coze 配对和外发权限保持原契约。

恢复重复执行应幂等；输入/原文篡改、活进程、非零退出、方法待复核、占用目标、原成功模型变更都必须拒绝。原失败历史不由恢复成功抹除。
