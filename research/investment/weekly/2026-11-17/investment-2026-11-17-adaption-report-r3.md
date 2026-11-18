# 个股调研框架更新结果

日期：2026-11-17，Asia/Shanghai；revision：r2；generator：codex。范围为用户要求的 review 与从原股票框架实际拆出红利专用内容，使用独立 worktree `codex/dividend-research-framework-20261117`。本报告是方法维护，不是公司研究或行情刷新。

## 1. 更新结论

`method_change=true`，`state_refresh=false`，`evidence_correction=false`。用户已明确认可独立红利方案，并要求本轮复审及实际迁出；按授权本地采纳。首版只完成部分分流，仍有两处会把红利要求传给非红利。本轮均已修复，另补快照范围检查：

| 发现 | 影响 | 修复 |
|---|---|---|
| P1：R9仍是原框架有效规则，稳态现金流映射强制利差、持仓和换手三个当期读数 | 非红利稳态公司仍可能因红利专项缺值被限制 | 定义迁到红利HD6；原R9只保留历史编号与迁移链接，删除所有有效[R9]映射 |
| P1：共享§4.1A、原compact、skill及输出§5仍强制分红预测/DDM专题 | 公司仅有分红或现金流稳定就被要求走红利估值流程 | 详细分红模型和全部原公式迁至红利HD4A及其compact/reference；共享只保留实际模型依赖的分配一致性 |
| P2：早期与本次六文件快照都叫snapshot/v2 | 仅据schema可能把新R9适用性套到旧批次 | 冻结正文增加策略scope标记；技能按实际冻结正文执行；治理检查约束迁移索引，回归验证旧v2不变 |

未发现阻止本次本地落地的剩余问题；这不是生产发布或投资方法收益验证。

## 2. 受影响模块

| 原位置 | 现行归属与边界 |
|---|---|
| 原股票稳态现金流类型、参数映射、R9、D5红利底仓描述 | 非红利保留经营现金持续性/资本配置研究；红利类型及专用风险交HD1/HD6 |
| 原R9的88%持仓、95%换手提示 | 红利HD6保留数值和同口径要求，作为拥挤/容量/价格复核信号；适用R1仍三项合取，不凭单值冻结 |
| 共享原§4.1A及原compact分红计算块 | 红利HD4A及红利compact，保留权利时点、正常化、金融例外、DDM、税、去重和P1传导 |
| 原股票输出§5及stock-research估值reference | 资本配置与模型实际涉及的分配/留存；不强制红利台账、股息利差、年度普通股息预测或DDM比较 |
| 共享§4.1A | 两轨通用的分配/回购/留存、权利/币种/税、资产与股本桥及唯一计价 |
| R20与D8的低利率红利豁免示例 | 收入暴露决定适用性；红利标签和低利率不构成豁免。原滚动解除条件不变 |
| skills与模板 | stock/dividend/weekly/condense及对应reference同步；红利九节模板指向HD4A |
| 治理脚本 | 新scope与六份依赖一致、R9不可重新作为compact有效引用、红利HD4A不得丢失；legacy仍可检查 |

## 3. 修改说明

按主持有目的分流：可持续现金分配为主进入红利；成长、修复、周期或事件收益为主继续非红利。经营稳定与是否分红不是自动归类条件。一家公司只裁决一套主策略、基准及P1/T1。

经济理由是把长期收入质量的证据结构与经营成长/修复的证据结构分开，减少不相关红利缺值对非红利研究的干扰。可能增加的遗漏是研究者误将实际依赖的分配输入视为可省略，故共享规则仍要求核真实权益归属、现金/资本桥、税费及期末价值，专项模型数学仍可按适用性引用。

- 正例：有普通分红但主要赚成长/估值修复收益的公司，按非红利经营模型分析，不因缺国债利差或DDM台账阻断可支持的估值。
- 正例：以可持续现金分配为主的公司，红利HD3/HD4A完整预测普通/特别分配、正常与压力现金、分配后剩余价值；即使缺利差，也如实留空而非把企业判为失败。
- 反例：依靠借债或周期峰值派息不能因高股息放行；治理、偿付、资本不足及真实流动性风险继续逐条核查。
- 边界：金融红利使用监管资本与可分配利润，不套工业OCF-capex；有限寿命不无条件永续；非红利若有依据自行选DDM，仅引用数学/时点边界，不导入红利筛选门槛。
- 边界：已知零分红可为0，未知不为0；特别派息减对应资产；已除息而新投资者无权收到的款项不能算新买入收益。R22若实际依赖分配，仍需同期限同税基核算。
- 旧控制：不因路由变更清零。只有在明确的新方法适用性及原scope复核后，才可记录仅由旧红利缺值门槛形成的限制解除；真实风险另核。此轮未对任何公司解除控制。

## 4. 不应过度反应

没有新增4%股息率、70/30分位、±2σ等买卖阈值；不将文章中的胜率或行情数值作为已验证规则。股息利差继续是红利定价背景。必要回报、总回报比较、普通股权利、资本配置与分配去重仍服务两类股票，不能随红利专题一起删除。

共享§4.1B/C/D、§5.2A、§6.2和§6.6与复审前逐字节相同。§6.1仅将一处强制“可持续分红”措辞改为实际模型涉及的分配，一套B/min(B,U)、两价、60/40及既有控制不变。所有市场观测块逐字节相同，日期不冒充今天。

## 5. 新版框架链接

- [非红利canonical](../../../../framework/investment_framework.md) / [compact](../../../../framework/investment_framework_compact.md)
- [红利canonical：HD4A与HD6](../../../../framework/dividend_framework.md) / [compact](../../../../framework/dividend_framework_compact.md)
- [共享基础](../../../../framework/stock_research_common.md) / [红利九节模板](../../../../framework/dividend_report_template.md)
- [红利技能](../../../../.agents/skills/dividend-research/SKILL.md) / [非红利技能](../../../../.agents/skills/stock-research/SKILL.md)

关键范围标记：`stock-strategy-scope: non_dividend; migrated-rules: R9=dividend-HD6`。未带标记的旧冻结批次，包括早期六文件v2，照其原R9与分红条款执行，不根据当前技能补套本版方法。

## 6. 版本变更记录

本地方法由`stock-strategy-split-v1-common-v1-dcf-v3`改为`stock-strategy-split-v2-common-v2-dcf-v3`；共享`stock-common-v2`，红利`dividend-quality-v2`。快照schema仍v2，六文件依赖按审后正文显式sync；轻量JSON v4、audit-v6及controls-v9未变。原工作区并行controls-v10未合入。

[保真与指纹清单](evidence/dividend-scope-review-fidelity.json)保存六文件旧/新完整SHA-256及method_fingerprint；复审前14文件备份位于`output/dividend-framework-review-2026-11-17/before/`。新旧完整六文件分别存于本目录evidence下的首版与r2 handoff-methods。

[r2采纳交接](investment-2026-11-17-handoff-r3.json)仅在本worktree supersede首版，不重写旧交接、报告或冻结文件。原5项pending、4项withdrawn_sources及25项历史rule_evaluations原样接续，保留各自证据日期；没有新的公司完成凭证。兼容性列表保持空，不声称新旧投资判断等价；仅验证旧合同可恢复、新合同正确绑定。

## 7. 验证

- 股票结构/依赖治理通过；10项治理及14项bundle定向回归通过。新增5项覆盖R9再激活、scope缺失、迁移模型丢失、早期六文件版本及原提示字节不变。
- 全量离线回归1430项通过。首次沙箱运行1430项有46个权限错误（44个本机端口、2个ps），获准沙箱外复跑后全部通过；不把首轮称为通过。
- 本轮4个修改skill的quick_validate通过；71处本地Markdown文件引用无缺失。skill验证仅验证结构，不证明全部语义。
- [保真核查](evidence/dividend-scope-review-fidelity.json)14项断言通过：含迁移计算段保真、共享未受影响段相同、市场观测相同、runner相同；已对适用范围变更人工复核。
- [原实际prepare目录检查](evidence/dividend-scope-legacy-prepare-check.json)通过，旧六文件snapshot/v2仍可校验；没有启动研究provider或生成报价。
- [验证明细](evidence/dividend-scope-review-validation.json)含命令、日志哈希及限制。本轮未运行真实Tushare/API、公司投研、调度或账户执行；此前yc_cb缺权限为历史取数结果。未验证投资收益或生产部署。

## 8. 精简版同步

非红利compact将R9改迁出索引，移除D5/类型映射的有效R9依赖、红利底仓和自动低利率假设；§7分红计算块整体移至红利compact HD4A，§10改为通用资本分配字段。D8同步收入暴露边界，其他有效规则不重编号。

迁移模型仅改适用范围、跨文件引用和HD6控制引用，原n正整数、ke>0、ke>g_D>-1、有限期例外、现金权利、税、终值和P1消重完整保留。原R9的88/95信号现于红利HD6，两份同义；信号动作从原强制三值门槛转为补充风险复核是显式方法变更，不声称完全语义等价。共享正文仍是完整权威，compact不能取代其数值、AND/OR及解除条件。结构/字节检查与人工边界审阅共同支持这次范围拆分，不证明所有未来执行结果或投资效果。
