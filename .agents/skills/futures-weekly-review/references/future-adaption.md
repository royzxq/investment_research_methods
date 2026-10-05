# 期货框架适配（阶段③）

只在 `update_needed=yes` 时执行；no 时不动 canonical。单阶段到此结束，不自动 data-sync、审计重评、精简或发布。

## 输入与执行

- `AS_OF_DATE`、`CURRENT_FUTURES_EXECUTION_FRAMEWORK`（`framework/futures_framework.md` 现行全文，跳过顶部维护说明 HTML 注释）、完整 `FRAMEWORK_UPDATE_RESULT`（决策、变化、重点、不应过度反应、可得性及纠错）、`CURRENT_EXECUTION_AUDIT`（本期共享模板审计）。单独维护缺审计时明确不可用，不从管理规则推断持仓。
- 先读 `framework/FUTURES_DATA_PROTOCOL.md`，再读 `projects/future_adaption/INSTRUCTIONS.md`，完整遵循角色、原则及六步；诊断口径只引用 `projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md`。
- 区分市场变化、证据纠错、数据可得性变化；`DO_NOT_OVERREACT_ITEMS` 不阻止纠错。优先保证活跃模型最小公开证据可重复取得，专业路线不可得单列 `research_only` 和恢复条件，不新增全局必填或用户长期裁量项。
- 公共数据 A 评分、归一化、D9 中性值等只引用 canonical，不复制公式。列清新版使哪些旧信号／风险输出失效，供后续重评。
- 仅局部更新受影响内容，原位更新当前状态，不附历代“本次更新”标记；评分、策略及审计要求不因精简改变。

## 输出与交接

1. 在入口确定的更新分支／隔离 worktree 写 `research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-adaption-report.md`，保留可得性、纠错及影响范围。按 instruction 输出，第 5 节链接工作区完整框架，仅列受影响章节及必要片段，不粘全文。
2. 按报告局部更新 `framework/futures_framework.md`，保留未受影响有效内容及维护说明；新版正文由工作区文件提供，不从报告抽取全文替换。
3. 返回分支／worktree、报告全文与路径、旧输出失效项。完整流程由入口接 data-sync，并在同一分支完成审计重评和 compact。
4. 默认本地保存；已获 `publish` 授权时仅提交本阶段 framework 与 report 的独立记录，摘要取「1. 更新结论」，不自己 push 或开 PR。
