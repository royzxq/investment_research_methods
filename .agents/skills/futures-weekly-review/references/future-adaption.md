# 期货框架适配（阶段③）

周更适配只在 `update_needed=yes` 时执行；no 时不动 canonical。单阶段到此结束，不自动 data-sync、审计重评、精简或发布。用户直接授权的设计审阅、精简或重构使用下方 `direct` 分支，不要求先生成周度变化决策。

## 输入与执行

- `AS_OF_DATE`、`CURRENT_FUTURES_EXECUTION_FRAMEWORK`（`framework/futures_framework.md` 现行全文，跳过顶部维护说明 HTML 注释）、完整 `FRAMEWORK_UPDATE_RESULT`（决策、变化、重点、不应过度反应、可得性及纠错）、`CURRENT_EXECUTION_AUDIT`（本期共享模板审计）。单独维护缺审计时明确不可用，不从管理规则推断持仓。
- 先读 `framework/FUTURES_DATA_PROTOCOL.md`，再读 `projects/future_adaption/INSTRUCTIONS.md`，完整遵循角色、原则及六步；诊断口径只引用 `projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md`。
- 区分市场变化、证据纠错、数据可得性变化；`DO_NOT_OVERREACT_ITEMS` 不阻止纠错。优先保证活跃模型最小公开证据可重复取得，专业路线不可得单列 `research_only` 和恢复条件，不新增全局必填或用户长期裁量项。
- T / V、G1–G6 及风险口径只引用 canonical，不复制阈值或公式，不恢复加权评分及已退休冻结。列清新版使哪些旧信号／风险输出失效，供后续重评。
- 仅更新受影响内容，原位维护当前状态，不附历代“本次更新”标记；compact 同步不另改已经确定的方法。用户明确授权重构时记录规则承接、合并和退休依据。

## direct：定向设计维护

- 以用户请求和明确范围为输入，读取现行 canonical、数据协议及相关设计/诊断证据；无需伪造 `FRAMEWORK_UPDATE_RESULT`、`update_needed` 或新一期市场报告。只审阅时不改方法；已要求实施时完成获授权的重构及必要联动。
- 在入口确定的更新分支／隔离工作区工作，正式记录保存至 `research/futures/maintenance/<AS_OF_DATE>/`，同日已有产物按根约定复用或使用不覆盖的独立文件名。说明设计基线、实际变更、退役规则与新旧输出边界。
- 使用 `projects/future_adaption/INSTRUCTIONS.md` 的影响分析与验证方法。用户要求同步完整版和精简版时，在同一工作区完成 canonical、实际依赖的协议/工具/模板以及 framework-condense；只改用户授权范围，不自动扩成完整周更。
- 需要工具联动时，按数据同步 reference 检查依赖；其输入为本次 maintenance 实施报告和实际新版框架，不要求制造 weekly 适配报告。实施报告记录数据/脚本同步及精简版同步结果，未改的部分说明理由。
- 没有新取证就保留当前信号未评估、账户未知；不把规则变更写成当前可交易，不修改旧报告、旧前瞻登记或旧影子收益。研究参数未经收益验证须明示；旧自动影子结算不自动支持新模型。
- 运行适用结构检查、离线边界测试及修改 skill 的 `quick_validate.py`，记录实测与未验证范围。输出完整本地结果；commit、push、PR、交易和对外消息仍需原有明确授权，不能从设计维护推导。

## 周更适配的输出与交接

1. 在入口确定的更新分支／隔离 worktree 写 `research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-adaption-report.md`，保留可得性、纠错及影响范围。按 instruction 输出，第 5 节链接工作区完整框架，仅列受影响章节及必要片段，不粘全文。
2. 按报告局部更新 `framework/futures_framework.md`，保留未受影响有效内容及维护说明；新版正文由工作区文件提供，不从报告抽取全文替换。
3. 返回分支／worktree、报告全文与路径、旧输出失效项。完整流程由入口接 data-sync，并在同一分支完成审计重评和 compact。
4. 默认本地保存；已获 `publish` 授权时仅提交本阶段 framework 与 report 的独立记录，摘要取「1. 更新结论」，不自己 push 或开 PR。
