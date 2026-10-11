# 期货元框架调研（阶段①）

## 输入与方法

- `AS_OF_DATE`；可选 `EXECUTION_EVIDENCE`（已有行情日期／版本、来源与缺口）、初步 `DATA_FEASIBILITY`、已发现 `EVIDENCE_CORRECTIONS`。没有输入不假定行情最新或账户空仓。
- 先读 `framework/FUTURES_DATA_PROTOCOL.md`、`framework/futures_framework_compact.md` 导航；方法、参数与歧义回 `framework/futures_framework.md`。再读 `projects/meta_future_analysis/INSTRUCTIONS.md`，遵循可行性检查和六步分析，记录框架版本／修订号，绑定 `{{AS_OF_DATE}}`。
- 按根 `AGENTS.md` 使用当前检索路由和原文读取能力。原文不能核验时按数据协议降低用途，搜索摘要不能充当已核实数值。
- 默认 `public_data`：先扫描 MA/RB/M/SR/CF 所需最小数据，重点补全 M/RB 双向研究，SR/CF 常驻次级，再按具体 T / V 逻辑补宏观、海外、政策。旧全量清单不是每周必填包，不要求用户采购专业数据。每个缺失指标最多尝试两个公开来源后分类；增强项缺失不扩成全池缺项，必要专业依赖长期不可得的模型进 `research_only`，列恢复条件。
- 核对完整年份、观测日、单位及比较口径；同源转载不算独立证据。先撤回错误证据的用途，再提炼市场变化，不为数据错误增设市场护栏。独立国内结构与事件因果模型分别评估，不改名绕过专属验证。
- 只研究顺势与有经济依据的回归两类，条件及适用范围引用 canonical；事件、政策、季节只作证据与执行边界，不恢复独立策略、加权评分或隔夜分数。缺账户不阻止研究与计划输入。

## 输出

- 按 instruction 完整模板写 `research/futures/weekly/<AS_OF_DATE>/<AS_OF_DATE>-market-research.md`，保留第 9 节全部结构化字段，特别是 `DATA_FEASIBILITY`、`EVIDENCE_CORRECTIONS`。
- 返回报告全文和路径作为 `CURRENT_META_RESULT`，不只传市场摘要。单阶段到此结束；同日与发布边界沿用入口。
