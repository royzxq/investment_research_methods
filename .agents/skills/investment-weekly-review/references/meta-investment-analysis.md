# 股票元框架调研（阶段①）

只执行本阶段时，不自动变化检测、适配、提交或发布。环境、检索路由、同日写入和发布边界沿用入口及根 `AGENTS.md`。

## 输入与方法

- `AS_OF_DATE`：入口传入的北京时间日期。
- 读取仓库 `projects/meta_investment_analysis/INSTRUCTIONS.md`，按其中角色、固定范围、来源要求及六步流程执行；将 `{{AS_OF_DATE}}` 作为本次输入绑定，不改写原模板。
- 固定市场为中国 A 股与港股。主动核验宏观与流动性、政策监管、中观产业、资金风格、估值风险偏好及海外映射；区分阶段性噪音和足以改变研究框架的变化，不直接推荐个股。
- 使用当前可用检索及原文读取工具；股票阶段不可误用期货的输出字段。

## 输出

- 严格按 instruction 模板写 `research/investment/weekly/<AS_OF_DATE>/investment-<AS_OF_DATE>-market-research.md`。保留第 9 节的 `MAIN_CONTRADICTION`、`DOMINANT_RETURN_DRIVERS`、`KEY_CONSTRAINTS`、`PRIORITY_MECHANISMS`、`FRAGILE_NARRATIVE`、`TOP_MISTAKE_TO_AVOID`、`PRECHECK_ITEMS`，不用期货的 `DOMINANT_TRADE_DRIVERS`／`FRAGILE_TRADE_NARRATIVE` 替代。
- 返回报告全文与路径，作为 `CURRENT_META_RESULT`；后续不可仅传摘要。已有同日期文件按入口幂等规则处理。
