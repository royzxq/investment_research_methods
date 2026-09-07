---
name: meta-future-analysis
description: 期货元框架调研（流水线阶段①）：用 WebSearch 主动检索国内期货市场公开信息，产出结构化的"期货元框架调研结果"，写入 research/<AS_OF_DATE>-market-research.md。Use when asked to run the weekly futures market meta-analysis stage, or to do a standalone re-research without running the full pipeline.
---

# meta future analysis（流水线阶段①）

## 输入

- `AS_OF_DATE`：调用方传入的日期（`futures-weekly-review` 编排器会传今天日期；单独调用时用当天日期）
- `EXECUTION_EVIDENCE`：现有行情输出及其日期/版本、公开来源与已知缺口（可无；不假定已有最新行情）
- `DATA_FEASIBILITY`：编排器的初步品种/模型可得性分类（可无；本阶段按证据完善）
- `EVIDENCE_CORRECTIONS`：编排器已发现的旧证据错误及影响范围（可无；本阶段核验并补充，不遗漏已撤回项）

## 执行

1. 先读取 `framework/FUTURES_DATA_PROTOCOL.md`、canonical `framework/futures_framework.md`，再读取 `projects/meta_future_analysis/INSTRUCTIONS.md`，完整遵循其数据可行性检查与六步分析流程；记录框架版本/修订号，将 `{{AS_OF_DATE}}` 替换为输入值
2. 公开信息检索使用内置 `WebSearch`，并用当前环境可用的原文读取能力核对证据；本 skill 可能在没有本地 MCP 的云端环境运行，不要依赖 `gemini-search`、`lark-cli` 等本地专属工具。原文无法核验时按数据协议降低用途，不能把搜索摘要直接写成已核实数值
3. 默认 `public_data`，先覆盖 MA/RB 与符合激活条件的 M/SR/CF 所需最小数据，再按其交易逻辑补充相关宏观、海外、政策信息；旧全量清单不是每周必填包。利用现有日线、公开公告/日历与当前独立产业指标，不要求用户采购专业数据。每个缺失指标最多尝试两个公开来源后分类；专业增强项缺失不扩成全池缺项，必要专业依赖长期不可得的模型进入 `research_only` 并列恢复条件
4. 逐项核对完整年份、观测日、单位与比较口径，同源转载不算独立证据。先列 `EVIDENCE_CORRECTIONS` 并撤回错误证据的用途，再提炼市场变化；不要为数据错误增设市场护栏。独立国内结构与依赖事件因果的模型分别评估，不改名绕过专属验证
5. 严格按 instruction 第六步给出的格式输出完整报告（含第 9 节全部结构化字段，尤其 `DATA_FEASIBILITY`、`EVIDENCE_CORRECTIONS`）；公共数据模式评分只引用 canonical 当前规定，不另存权重/中性值或用缺账户阻止研究评分

## 输出

- 把完整报告写入 `research/<AS_OF_DATE>-market-research.md`（同一天重复运行直接覆盖同名文件）
- 返回值：报告全文，供编排器作为下一阶段的 `CURRENT_META_RESULT`；完整保留 `DATA_FEASIBILITY` 与 `EVIDENCE_CORRECTIONS`，不只传市场摘要
