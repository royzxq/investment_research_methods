---
name: meta-investment-analysis
description: 股票元框架调研（流水线阶段①）：用 WebSearch 主动检索中国 A 股 + 港股公开信息，产出结构化的"元框架调研结果"，写入 research/investment-<AS_OF_DATE>-market-research.md。Use when asked to run the weekly stock market meta-analysis stage, or to do a standalone re-research without running the full pipeline.
---

# meta investment analysis（流水线阶段①）

## 输入

- `AS_OF_DATE`：调用方传入的日期（`investment-weekly-review` 编排器会传今天日期；单独调用时用当天日期）

## 执行

1. 读取 `projects/meta_investment_analysis/INSTRUCTIONS.md`，完整遵循其中的角色、目标、固定范围（市场范围固定为中国 A 股 + 港股）、信息来源要求、分析原则与六步分析流程；将其中的 `{{AS_OF_DATE}}` 替换为上面的输入值
2. 全部调研动作使用内置 `WebSearch`——本 skill 可能在没有本地 MCP 的云端环境（云端 scheduled routine）运行，不要依赖 `gemini-search`、`lark-cli` 等本地专属工具
3. 覆盖 instruction 里列出的宏观流动性、政策监管、中观产业景气、资金行为与风格、估值与风险偏好、海外映射等公开信息来源；区分"阶段性噪音"与"足以影响研究框架的变化"
4. 严格按 instruction 第六步给出的格式输出完整报告（含第 9 节结构化结论字段：`MAIN_CONTRADICTION` / `DOMINANT_RETURN_DRIVERS` / `KEY_CONSTRAINTS` / `PRIORITY_MECHANISMS` / `FRAGILE_NARRATIVE` / `TOP_MISTAKE_TO_AVOID` / `PRECHECK_ITEMS`——注意字段名和期货那套不同，不要写成 `DOMINANT_TRADE_DRIVERS`/`FRAGILE_TRADE_NARRATIVE`）

## 输出

- 把完整报告写入 `research/investment-<AS_OF_DATE>-market-research.md`（同一天重复运行直接覆盖同名文件）
- 返回值：报告全文，供编排器作为下一阶段的 `CURRENT_META_RESULT`
