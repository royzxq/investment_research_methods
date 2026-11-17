# 个股调研框架更新结果：独立红利策略

日期：2026-11-17（Asia/Shanghai）；generator=codex；分支 codex/dividend-research-framework-20261117。用户明确认可拆分方案并要求在单独 worktree 实现，本次授权为本地实现与检查，无Git提交、推送、PR、合并、生产部署或交易。

## 1. 更新结论

method_change：股票轨按主持有目的拆为非红利与红利。红利以现金分配质量、可持续普通股息与压力韧性为主；原框架主要负责成长、修复、周期/事件等非红利主策略。共同估值、证据、资本桥、风险消重、P1/T1与控制抽入共享文件。方法在此独立worktree按用户明确授权本地采纳，生产部署仍pending；旧市场观测、个股结果与账户执行未更新。

本次不是对股票作永久分类；有分红或高股息率不足以路由。每份报告一个主策略、一套最终估值及P1/T1，转换主策略必须审议既有控制。股份分红的估值贡献仍适用于非红利公司。

## 2. 受影响模块

| 文件/模块 | 改动与边界 |
|---|---|
| stock_research_common.md | 接收原§4.1A–D、§5.2A、§6.1–2、§6.6完整规则和三值事实定义；原节号保留链接 |
| investment_framework及compact | 主策略范围、共享入口、R9路由范围、依赖指纹；原R1–R22/D1–D8稳定编号及历史观测保留 |
| dividend_framework及compact | HD1–HD8：子类型、六项质量、分红权利与预测、估值压力、价格、利差、持有/组合、交付 |
| dividend_report_template | 沿0–8九节，增加普通/特别/前瞻/压力、税汇、资本桥、收入贡献和持有复评 |
| skills及AGENTS/README | 新dividend-research及Claude入口；stock-research、deep-research-auto、周更与compact技能按主策略/冻结版本路由 |
| runner/maintenance/governance | 新v2冻结六文件；旧v1仍原两份；维护pair通过依赖SHA传递绑定，冻结/恢复/校验全闭合 |
| dividend_data.py | 复用量价财务包的可选补充，仅A股历史股息/派息/同日10年国债与描述性利差 |

轻量price JSON仍v4，audit-v6/controls-v9不变。分红专项事实进报告与证据，不给严格下游schema加字段。DDM/FCFE等仍属other专项计算，不声称机器已验证其经济假设或全部算术。

## 3. 修改说明与边界案例

原框架把现金分配、拥挤/风格和成长判断混排，导致长持收益来源与短期交易信号容易混用。拆分保留共同风险纪律，把长期现金质量及新资金机会成本置于核心。仅HD6明确改变红利R9“三项读数缺一”机械门槛；其他实质风险、必要资格和旧控制不解除。

| 案例 | 应有研究结果 | 禁止的误判 |
|---|---|---|
| 稳定经营现金、必要投入可覆盖、特别分红到期 | 普通分红正常化，特别派息单列，核债务/特许权寿命 | 把特别分红永久外推，或见总额下降即卖 |
| 银行/保险高息、资本承压 | 用资产质量、拨备、资本/偿付能力约束可派现金 | 套OCF-capex或只看低PB放行 |
| 煤炭等周期高派息 | 中周期盈利为基准、低谷压力并保留周期模块 | 峰值低PE/高TTM股息当稳定永久现金 |
| 分红成长 | 留存×回报、必要投入、分配与增长闭合 | 同一利润既分掉又全额投入增长 |
| 高息但主逻辑为事件修复 | 保留非红利主策略，分红作估值输入 | 根据yield自动路由或换名解除旧freeze |
| 国债或拥挤分位缺失 | 利差/分位null，仍完成可支持的质量与估值，独立核必要资格 | 缺数据=0、利差自动通过，或直接否定全部研究 |
| 港币收益率与人民币国债 | 不计算直接差值，补税/汇率/同币种基准 | 把跨币种差视为无风险套利/完整ERP |
| 已除息但未支付 | 新买入者预测剔除不属于其权益的派息 | 把尚未到账当新投资者可获得 |
| 临时冻结但可估 | 观察P1/T1可保留，entry/add受原控制 | 因价格便宜或切红利自动解除 |

价格沿用B=V50×(1-d_base)×∏(1-r_k)，R22输入充分才min(B,U)，不叠加完整股息现值、不另设r_alpha。用户未给y_min，现金收入底线C未启用；未新设账户参数。T1为复评条件，60/40预算保留原义。

## 4. 不应过度反应

未采用4%硬线、70/30历史分位、±2σ或个人5.5/6.5档位；文章胜率没有可复现底稿，不升级规则。5完整财年/周期、3–5年显式预测与10年/5年历史观察是带适用性及缺口的工作窗口，不是保证收益或统一交易阈值。PB低与股息高的组合需解释，不能单独断定陷阱或便宜。

没有重跑市场研究或个股研究，原5项pending和4项withdrawn原样接续；不声称这些公司已完成复评。未改外部ai_investment build_pack/调度器、账户状态、latest或ETF/期货方法。

## 5. 新版框架与入口

- [红利canonical](../../../../framework/dividend_framework.md)、[红利compact](../../../../framework/dividend_framework_compact.md)、[九节模板](../../../../framework/dividend_report_template.md)
- [共享基础规则](../../../../framework/stock_research_common.md)、[非红利canonical](../../../../framework/investment_framework.md)、[compact](../../../../framework/investment_framework_compact.md)
- [红利skill](../../../../.agents/skills/dividend-research/SKILL.md)、[数据说明及调用](../../../../.agents/skills/dividend-research/references/data-and-output.md)

## 6. 版本、接续与兼容范围

基线为本地eb77f77及迁入清单中的已批准估值可用性修复（v9/audit-v6），31个基线文件保存于output/dividend-framework-2026-11-17/baseline。未迁入config/research_candidates等无关改动。完整SHA及method_fingerprint如下：

| 文件 | 旧完整SHA256 | 新完整SHA256 |
|---|---|---|
| investment_framework.md | 2b909852e5afacc1ea832a76540c04469439fb016692dc91c32bd7160e13fb32 | affccca432c3dda6218ed785517708b7a69effbca585c762d534d1ce9a29f7c5 |
| investment_framework_compact.md | 2ad08f195bb6729dd8c7aea96ccaf85c1fa5504aa53cfd18beef90f0e0377d1e | 8e5c2abf2d09a96ba157921d584a331382ae74971a954c67280e838a0d83da6a |

| 文件 | 旧方法指纹 | 新方法指纹 |
|---|---|---|
| investment_framework.md | 6303f7f694f21805a2122c2db7a67b8539a00a37e741f214084ab2f602c86e7e | abda2f87612433cbb648692c78958cd2ec0c618dcf8d91248c9239992fbaadb3 |
| investment_framework_compact.md | 782ff89d54dab37e9652c8e6a8c11706379773e23fed3cd21176fe83aa24769d | f2e70172b8b2e70e72fae23bb80866f0e5244af55036109a57e9f7d14377b501 |

新共同/红利文件的实际哈希嵌入两份原框架头部；任一依赖变化必须显式sync、审查并重新冻结，不能在check或prepare自动重签。版本名不代表兼容；R9语义调整与策略范围变化属于method_change，旧价不自动视为兼容，无兼容审议时隔离。

实现期间原工作区仍有并行估值修改，已观察到controls-v10/audit后续方法；本分支未自动合入、未覆盖。本次兼容结论覆盖所冻结基线及更早合同，不声称与该并行未完成版本已合并验证。后续整合需保留其新增审计/提示条款，并把六文件依赖冻结带入新NEW_CONTRACT；并行状态见独立证据摘要。

## 7. 验证与数据实际可用性

最终离线回归 **1,425项通过**（项目指定miniconda Python）；本次新增数据13项、框架/冻结13项。修复维护引用字段边界后运行器104项、恢复9项定向检查通过，随后完整回归通过。股票及期货结构检查、git diff --check通过，5个Codex技能及1个Claude兼容入口均通过bundled quick_validate。

十种历史提示合同与迁入前渲染器逐字节一致。新/旧快照、缺失/篡改依赖、未来默认合同升级、恢复完整依赖和删除现场维护文件后的冻结镜像均覆盖。最初普通Python回归存在tests包解析与PDF依赖环境问题；项目指定解释器已解决。过程中发现的维护引用字段错误已修复并回归，不掩盖为环境问题。

结构检查只证明依赖/编号/状态/模板契约；离线回归不证明投资收益、预测准确或来源真实。没有执行真实个股自动研究或策略回测。

真实Tushare小规模检查：daily_basic与dividend成功；yc_cb返回PermissionError（该接口需要单独权限），利率/利差null，补充包status=partial。未购买权限、未以其他口径静默代替。缓存同日曲线可跨股票复用，分红快照按截止日隔离；空/截断/错误不当零。普通/特别、税后收入和前瞻分红仍须公司原文与研究判断，当前回填不声称严格PIT。

已读官方接口：[daily_basic](https://tushare.pro/document/2?doc_id=32)、[dividend](https://tushare.pro/document/2?doc_id=103)、[yc_cb](https://tushare.pro/document/2?doc_id=201)（2026-11-17）。工具仅作补充；指数官方股息率、10/5年可比历史和港币利率本次未接入，保持缺口，不能据此产生分位或买卖指令。

本地新批次prepare/verify与维护镜像检查另存[准备检查](evidence/dividend-prepare-check.json)，只准备隔离离线输入，不运行研究CLI或交易。

## 8. 精简版同步

原compact只同步路由/权威入口/依赖身份与R9适用性，不重新编号。红利HD1–HD8逐节映射，同步例外、未知值、税汇/时点、金融/周期边界、y_min未启用、预算与旧控制解除要求；共享完整规则仍为必读依赖，不能仅凭红利compact省略。

程序逐段比对原迁移块：§4.1A–D（仅经批准R9适用范围一句调整）、§5.2A、§6.1–2、§6.6和三值事实定义保真；原观测JSON及未受影响R/D定义行保持一致。结构统计与证据见[验证摘要](evidence/dividend-validation.json)。未宣称全语义自动等价或投资方法经实证有效。
