---
name: dividend-research
description: 按本仓独立红利框架研究或复评 A 股、港股的长期现金分配质量、可持续分红、估值与持有逻辑，复用共享规则及股票交付流程。用于明确红利股投研、长期收息或以可持续分红为主要目标的研究；也用于已冻结research_route=dividend的自动任务，不用于框架维护。
---

# 红利股研究

自动任务以经校验的冻结research_route=dividend为入口，按共享C0执行（默认A股利差严格>2、港股严格>3.5个百分点，均以中国十年国债作筛选基准）；命中不是质量合格，质量不足仍在本轨作结论，不递归回普通轨。报告§0披露冻结规则/阈值/读数/日期/币种/来源，不重算；无该元数据的手工研究在用户明确“红利投研/长期收息”或主持有逻辑为可持续现金分配时进入。每家先写主策略 dividend、持有目的及四类子类型；普通分红不是路由充分条件。无自动路由元数据且企业价值成长/事件/修复为主者回 stock-research。仅手工主策略冲突先用已有用户持有目的裁决，不能为绕开风险换标签。

## 方法与工作流

1. 定位含 framework/research 的仓库，读 AGENTS.md、research/README.md 及当前项目状态；日期 Asia/Shanghai，生成端按真实宿主。读取适用历史，优先增量，不重复整套全量取证。
2. 有 runner 快照优先原合同：v2 读取冻结 stock_research_common.md、dividend_framework.md、dividend_framework_compact.md、dividend_report_template.md，实质适用的基础/行业风险回冻结 investment_framework.md；v1缺本独立框架时仅按旧股票方法完成，不追加新规则。无快照用现行对应文件，说明方法绑定及采纳状态。
早期六文件v2与新版都可能存在；R9迁出以冻结正文范围标记为准，未带标记仍按其旧规则，不套当前技能默认方法。
3. 复用 [stock-research](../stock-research/SKILL.md) 的历史发现、数据校验、deep-research-auto取证、价格审计与落盘步骤；只执行一次共同流程，不递归再路由。把主策略、子类型和HD1–HD8缺口传给后端，基础规则与治理/偿付/事件风险不豁免。
4. 按 [红利数据补充](references/data-and-output.md) 复用原数据包，必要时取专项补充；不是每次全量取数。公告原文核普通/特别、资本缓冲、分配权利和税；不把API现金分红自动当可持续净收入。
5. 用独立九节模板交付，执行[红利估值与交付](references/valuation-and-output.md)，HD1–HD8（含HD4A）与共享规则完整执行，新controls-v10/audit-v7的已给V50按共享§4.1D完成中性校准；当前mode与entry/add/holding分判，历史控制逐条接续。DDM等专项计算可用other但必须保留真实计算证据，自动审计不能证明模型经济有效。
6. 继续原报告路径、investment-前缀、generator隔离、v4价格JSON与适用audit。股息台账/利差/情景放正文和证据，不给最终轻量JSON加字段。监控≤7但完整条件表保留全部。校验命令复用stock-research，不覆盖同日已有结果，不自动提升隔离结果。

## 研究重点

长期现金质量优先于TTM高息；正常年、未来12月有权取得、压力及特别分红分开。金融按资产质量/资本/分配约束，周期按正常化与低谷，分红成长核再投资，有限期不编永续。利差只是定价背景，缺三项拥挤读数不自动失败，但真实风险/必要资格缺证照常控制。净收入底线y_min未提供，不启用新门槛。

框架修订交investment-weekly-review；本技能不改规则、调度器或账户状态，不执行交易或外发。
