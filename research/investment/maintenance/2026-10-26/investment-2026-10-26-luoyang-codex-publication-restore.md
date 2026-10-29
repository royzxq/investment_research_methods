# 洛阳钼业 Codex 发布冲突修复与原产物恢复

- 日期：2026-10-26，Asia/Shanghai；generator=codex。
- 用户授权：修复文件冲突，重新验收并恢复今天洛阳钼业已有 Codex 调研结果，不重做调研。仅本地维护和恢复，未提交/推送 Git。

## 原因与修复

批次 `91b123b1e7f844b9bb6731c173471f11`、任务 `SH-603993`，Codex 05:26:36 启动、05:42:55 在发布前失败。CLI exit=0，原生回执和 candidate 均为 completed。公司/日期/生成端路径隔离正常，冲突来自同一执行目录的两个写入角色：原提示词允许代理在整个 execution 根存临时材料，代理写了 `research-validation.json`；运行器独立验收后再以 create-only 创建同名文件，触发 Errno 17。原暂存报告、JSON 和完成回执保留，正式目录没有发布。Jev 摘要也曾被代理提前持久化，使运行器遥测遇到同类冲突。

现将运行器研究验收、兼容性及 Jev 摘要隔离到 `runner/`，运行时明确代理取证/自检只写 `agent/`、既有 scratch 或 `jev/materials/`。冻结 prompt/input/hash 保持原字节。运行器继续独立读取并验收实际产物，不采纳或覆盖代理自检。新增回归先复现 Errno 17，再验证旧位置同名文件存在时仍可发布，且原代理文件保留。

## 恢复与核验

通过 `research_recovery.py restore-publication` 核对原失败封口、停止且 exit=0 的进程、原生完成回执、candidate、原始完整输入/执行profile及产物哈希，并按原冻结合同执行报价、一致性、lifecycle、acceptance 与方法兼容性复验。检查全部通过，方法兼容性为 exact。未启动新的研究 CLI、未重新取数或改变研究假设。

正式报告：`research/investment/companies/2026-10-26/SH-603993/investment-603993-2026-10-26-research-codex.md`。

正式价格：`research/investment/companies/2026-10-26/SH-603993/investment-603993-2026-10-26-price-map-codex.json`。

原报告 SHA256 `d3ae34f5e726eae6e4568c16bcb6e9b415d5618181cbdbf8820fcfbbc69bc20f`；价格 JSON SHA256 `3f44bae2bd61c57dd66ce3f49ad0422421c29a0f788f03d99df6c394f89df699`。正式文件与暂存原字节一致，Codex latest 与本地索引已更新。P1=8.90、T1=股价≥18.23元/股，仍为 frozen；entry/add blocked、holding review_required，R14必要证据仍 unknown。程序通过不表示经济风险通过或授予执行许可。

原失败 process/entry/queue-result 与原 seal 保留不变；新增 `research-publication-restore/v1` intent、独立复验记录、结果 manifest 和 `research-sealed-recovery/v1` 补充封口，沿用原请求、日期和研究完成时间。DSH 原 manifest、报告、JSON 不变。

相邻 ai_investment 消费者及报价属主补齐了对称恢复路径：只登记 Codex/gemini，复用 DSH/claude 的原 record、backup、source 和 available_at。通过原属主接口单股预演后应用本地 CSV，原 DSH 记录整体相等，其原 available_at 为 2026-10-26T07:39:32.637079+08:00；其他股票原始 CSV 记录保持不变。两模型共识 P1=8.795、T1=17.02（CSV按现行精度显示），原独立控制继续合并。重复验收和应用无新增报价、CSV不变。未调用外发或交易接口。

## 验证与边界

- 完整离线回归：`python3 -m unittest discover -s tests -v`，1177项通过。最初受限沙箱中的回环端口/ps检查被环境阻止，随后获得自动审批以可用权限重跑完整回归并通过；未改测试规避权限。
- 恢复定向回归4项通过，覆盖不重启研究、完整历史/原字节保全、幂等、PID重用、原文/运行输入篡改、占用目标、活进程及非零退出拒绝。
- ai_investment消费端定向回归77项通过，含原DSH完整来源保全、同日/手工修改冲突、恢复重放及原DSH/Coze路径。
- 股票框架结构治理、正式JSON检查、research_consistency的lifecycle/acceptance检查通过；框架方法未改。
- 本次没有新的市场API或研究有效性验证，使用并恢复原研究材料；原证据和投资限制仍按原报告解释。

契约见 `docs/adr/ADR-20261026-research-publication-restore.md`；完整恢复和属主证据见 `output/audits/investment/2026-10-26/luoyang-publication-restore/`。正确性对抗审查及项目六维核对覆盖：不重跑/改价、来源身份、create-only目标、冻结输入、活进程、幂等、原失败保全、原成功模型保全、CSV并发修改、同日冲突与恢复发布时间。审查未发现剩余阻断问题；已有其他聊天改动未纳入本次修复。
