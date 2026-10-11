# 股票维护变化检测（阶段②）

输入 `AS_OF_DATE`、完整 `CURRENT_META_RESULT`、已采纳 canonical；有基线时使用已采用 handoff 指向的 `PREVIOUS_META_RESULT` 及 `PREVIOUS_CHANGE_DECISION`。单独比较遵从用户指定报告，不偷换基线，也不自动采纳输出。

读取 `projects/investment_change_analysis/INSTRUCTIONS.md`，进行周环比和框架/现实一致性检查。先复核上期观察项的**规则身份、采纳来源、触发证据、受影响对象、待研究与完成凭证**；提案命中不自动升级为方法修改，更不能推断逐股研究已完成。历史不靠 canonical 累积。

逐项分为状态刷新、证据纠错或方法变更，轻重只描述影响，不决定变更类别。没有方法变化仍返回状态/纠错清单与交接所需事实；单阶段比较只保存提案，不改框架，不写 adopted handoff。

没有实质基线：明确首次运行，不虚构周环比；当前事实仍可与已采纳方法核对。`method_change` 不能仅因“首次无对比”跳过明显缺定义/现实冲突，也不能凭单周新闻追加风险门槛。

输出使用本期分配的统一 revision，保留 `FRAMEWORK_UPDATE_DECISION`、`KEY_VARIABLE_CHANGES`（`research_meaning`）、`UPDATE_FOCUS`、`DO_NOT_OVERREACT_ITEMS`，新增 `MAINTENANCE_CLASSIFICATION` 和复评接续清单。`update_needed` 只等于是否提出 `method_change`；完整流程继续到[维护接续](maintenance-handoff.md)，不以 no 提前终止。
