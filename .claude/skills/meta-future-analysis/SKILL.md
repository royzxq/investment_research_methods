---
name: meta-future-analysis
description: 期货元框架调研（流水线阶段①）：用 WebSearch 主动检索国内期货市场公开信息，产出结构化的"期货元框架调研结果"，写入 research/<AS_OF_DATE>-market-research.md。Use when asked to run the weekly futures market meta-analysis stage, or to do a standalone re-research without running the full pipeline.
---

# meta future analysis（流水线阶段①）

## 输入

- `AS_OF_DATE`：调用方传入的日期（`futures-weekly-review` 编排器会传今天日期；单独调用时用当天日期）

## 执行

1. 读取 `projects/meta_future_analysis/INSTRUCTIONS.md`，完整遵循其中的角色、目标、固定范围、信息来源要求、分析原则与六步分析流程；将其中的 `{{AS_OF_DATE}}` 替换为上面的输入值
2. 全部调研动作使用内置 `WebSearch`——本 skill 可能在没有本地 MCP 的云端环境（云端 scheduled routine）运行，不要依赖 `gemini-search`、`lark-cli` 等本地专属工具
3. 覆盖 instruction 里列出的宏观流动性、政策监管、供需链条（库存/利润/开工/现货）、基差与期限结构、市场风险偏好、海外映射等公开信息来源；区分"短期噪音"与"会影响交易方法的环境变化"
4. 严格按 instruction 第六步给出的格式输出完整报告（含第 9 节结构化结论字段）

## 输出

- 把完整报告写入 `research/<AS_OF_DATE>-market-research.md`（同一天重复运行直接覆盖同名文件）
- 返回值：报告全文，供编排器作为下一阶段的 `CURRENT_META_RESULT`
