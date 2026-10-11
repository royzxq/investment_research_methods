# 股票研究框架适配（阶段③）

只处理变化报告指定的正文修改范围；没有方法变化仍可能有状态/证据修订，不能仅凭旧 `update_needed=no` 拒绝。无需改正文时直接返回无正文变更，独立 handoff 仍由完整流程完成。单阶段到此结束，不自动精简、提交或开 PR。

- 输入 `AS_OF_DATE`、`CURRENT_STOCK_RESEARCH_FRAMEWORK` 现行已采纳 canonical 全文、完整 `FRAMEWORK_UPDATE_RESULT`，读取 `projects/investment_adaption/INSTRUCTIONS.md`。
- 方法规则仍保留 `{{COMPANY_NAME}}`、`{{TICKER_OR_CODE}}`、`{{VALUATION_DATE}}` 及核心结构。局部修改；不把市场状态刷新偷偷变成权重、阈值、动作或例外调整。
- 新方法必须完成操作定义、经济理由、适用对象、正反/边界案例、兼容影响。缺定义的条目保留 proposal，不写入有效方法；不以删除 unknown 保护来制造出口。
- 当期观测优先写独立 handoff/日期报告；同步原位 observation 块时仅用其严格事实 schema。混排方法正文的纠错先判断是否改变规则，再据实分类。历史留日期报告与 Git，不继续堆叠。
- 在本期统一 revision 的 adaption-report 记录变更分类、旧/新完整哈希及方法指纹、采纳状态和下游影响；链接工作区框架与必要片段，不粘全文。完整流程由入口同步 compact，并补「8. 精简版同步」。
- 默认本地保留。有明确发布授权时只交回入口统一单一 PR；新方法在合并/明确采纳前不能用于本期状态，旧方法下的状态与纠错单独接续。
