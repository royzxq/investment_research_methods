# 两价迁移 PR 审查修复

日期：2026-10-18，Asia/Shanghai。生成端：Codex。用户授权监听两个现有 PR、处理合理审查意见和 CI 问题；允许提交并推送必要修复到 PR head，不自动合并。

## 已确认问题及修复

1. [PR262 报价失效门禁](https://github.com/royzxq/ai_investment/pull/262#discussion_r4307608053)：仅持仓待复评的 control-only 发布可能仍令 entry/add eligible，随后继承旧价格新增敞口。消费者对真实报价缺失、倒挂、共识/权重失败增加自己的 `PUBLICATION_PRICE_UNAVAILABLE` 约束，限制 entry/add；仅非晚到的合法新价格发布以 seal/价格证据解除自身缺口，其他约束保留。合法报价仅因晚到未写入时不自动制造缺口，也不解除旧缺口。原 T1、卖出及 holding 复评语义独立。修复已推送 `3da72dd3b12b1ad903cafaed4af04b9e1c280120` 到该PR head `dev2`。
2. [PR50 约束动作降级](https://github.com/royzxq/investment_research_methods/pull/50#discussion_r4307613882)：旧约束可以同 ID/scope 从 freeze/reject/unavailable 改成 eligibility，绕过原限制的解除证据。新检查保留未解动作的限制强度，使用明确偏序而不任意排列不同经济条件；旧 audit/v1 的 effect 兼容。不可比替换先有证据解除旧ID，再用独立ID记录新条件。已确认否决、失效、退出不能靠 unknown 降级。
3. [PR50 维护完成缺审计](https://github.com/royzxq/investment_research_methods/pull/50#discussion_r4307613883)：外部手动 v4 研究可能只凭九节和报告/JSON配对完成复评。completed 验收现在调用同一 `research_consistency.validate_report`，检查 audit/v2、控制投影、可见计算视图及适用基线。旧 v2/v3 不追补新审计。

两个修复工作树分别为 `/private/tmp/ai-investment-pr262-fixes-20261018` 与 `/private/tmp/methods-pr50-fixes-20261018`，未改实际生产目录和业务数据。PR实际分支按GitHub读取核验，不把本地同名分支当作远端head。

## 验证与审查

AI侧先用7项失败测试复现问题，修复后63项定向、1037项综合回归通过；独立复核另实际执行失败→恢复→再失败三次发布，确认建仓资格 unknown→eligible→unknown，旧加仓限制始终保留。仅修改消费者、测试、现有ADR及CHANGELOG四文件。

methods侧先复现16个约束连续性失败分支及4个维护验收失败分支；定向15＋41项通过，完整unittest **810项通过（98.372秒）**。首次完整运行的两项错误仅为沙箱禁止 ps，授权环境完整重跑通过；未把环境错误当作测试通过。股票治理检查、两项相关skill quick_validate和diff检查通过，框架正文及其指纹未变。

两仓修复代码组合运行 methods runner→审计→封口→正式消费者的离线联调，1项通过。PR262原提交及PR50原提交CI均通过；修复提交必须重新检查其实际head的CI，不能继承旧绿灯。真实外部API与前瞻影子实验未运行，投资有效性限制沿用原回测报告。

六维复核通过：沿用现有职责属主；不恢复删除模块或提交凭据；不保留被替代的新路径；改动仅处理上述可复现缺陷；现有ADR/CHANGELOG与技能引用同步；验证覆盖不合法输入、历史兼容、显式解除、失败重放和真实入口调用顺序。独立代理与主代理交叉核验，未发现剩余阻断问题。

## 持续监听

本聊天已启用每15分钟监听，状态与测试证据保存在本机 `output/pr-monitor-262-50/`，记录意见ID、实际head、修复提交与CI状态。没有可处理的新变化时保持安静；发现合理意见或CI问题继续修复并推送到现有PR，发生权限/语义阻碍时说明。两个PR均关闭或合并后停用监听，不自动合并、不对外发无关消息。
