# 股票研究框架适配（阶段③）

仅在变化报告 `update_needed=yes` 时执行；为 no 时不动 canonical。单独适配到本阶段结束，不自动精简、提交或开 PR。

## 输入与执行

- `AS_OF_DATE`；`CURRENT_STOCK_RESEARCH_FRAMEWORK` 为 `framework/investment_framework.md` 现行全文，跳过顶部维护说明 HTML 注释；`FRAMEWORK_UPDATE_RESULT` 为完整变化报告，含决策、变量变化、更新重点和不应过度反应项。
- 读取 `projects/investment_adaption/INSTRUCTIONS.md`，遵循角色、原则与六步流程。该模板变量是 `{{CURRENT_STOCK_RESEARCH_FRAMEWORK}}`，不用期货变量替代。
- 框架是逐股研究的参数化模板，保留 `{{COMPANY_NAME}}`、`{{TICKER_OR_CODE}}`、`{{VALUATION_DATE}}` 及整体结构；不能改成某只股票的报告。
- 只局部修改真正受影响内容，优先调整权重、判断顺序、阈值、前置验证及风险约束，优先微调，尊重 `DO_NOT_OVERREACT_ITEMS`。当前状态原位替换，不叠旧状态或历代“本次更新”标记；历史放日期报告及 git。

## 输出与交接

1. 在入口指定的框架更新分支或隔离 worktree 写 `research/investment/weekly/<AS_OF_DATE>/investment-<AS_OF_DATE>-adaption-report.md`，按 instruction 格式产出。第 5 节链接完整工作区框架，只列受影响章节和必要片段，不粘全文。
2. 按报告局部更新 `framework/investment_framework.md`，保留有效未受影响内容、维护说明和占位符；完整新版以工作区文件提供，不从报告抽取全文替换。
3. 返回分支／worktree、报告全文与路径、受影响范围。完整流程由入口接着调用共用 `framework-condense`，写「8. 精简版同步」。
4. 默认保留本地结果；已获 `publish` 授权时本阶段只提交 canonical 和适配报告的独立记录，提交摘要取「1. 更新结论」。不自己 push 或开 PR，交回入口统一发布。
