# 个股调研框架更新结果

研究日期为 2026-11-12，时区 Asia/Shanghai，generator=codex。

## 1. 更新结论

本轮按用户要求完善可持续分红在基础估值中的计入及去重。分类为 method_change，state_refresh=false、evidence_correction=false。修改已在本地分支 `codex/sustainable-dividend-valuation-20261112` 完成，方法状态 proposed，生产接续以既有 adopted 方法副本为准。

原框架 R22 在可量化时用持有期分配和期末价值约束 P1，但基础估值仅列 PE/PFCF、PB-ROE/RIM 等方法，缺少分配假设的明确交付要求。新 §4.1A 把可持续分红纳入 V50 的独立计算与主辅模型裁决，ETF 预测缺失时仍能形成有依据的基础 P1。

KEY_VARIABLE_CHANGES 为正常化每股分红、可分配现金、权益必要回报率、分配后的剩余价值及留存增长桥。UPDATE_FOCUS 为估值方法、P1/R22 衔接及研究交付。DO_NOT_OVERREACT_ITEMS 为仅因历史股息率高而加价、重复叠加股息现值、将所有股票强制改用 DDM。范围来自本轮用户请求，未套用历史周更提案。

## 2. 受影响模块

| 位置 | 修改内容及适用对象 |
|---|---|
| canonical §4.1A、compact §7 | 全部研究说明适用性，稳态现金流、红利底仓或分红为重要持有理由者展示计入位置和计算。DDM 主估值或交叉核验，替代方法须说明分配价值如何被计入 |
| canonical §6.1/6.6、compact §9 | 基础 V50 先计分红，原五项折扣形成 B，R22 可量化时用一致预测算 U 并取 min(B,U) |
| 两份框架输出格式 | 补分红可持续性、权益时点、主方法、留存/终值桥、去重裁决及敏感性 |
| stock-research 入口及两份 reference | 按实际冻结方法选适用规则，取证输入补分配证据，用原 other 估值接口接入 audit-v2 |

## 3. 修改说明

股利折现适合派息政策可辨认、与盈利和分配能力匹配的公司。采用分期股息与分配后剩余价值折现，可以直接把股东现金回报放入当前价值。所用稳定增长公式及分阶段公式见 CFA Institute 的公开课程摘要，本轮实际读取了 Introduction 与 Summary。[CFA Institute 股利折现](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/discounted-dividend-valuation)

实际分配与分配能力相差较大时，FCFE 等方法可提供更适合的估值基础，预测需要扣除再投资和融资影响。由此采用主方法裁决及明确计入位置的规则，防止仅因派息少便低估有价值的再投资。[CFA Institute 自由现金流估值](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/free-cash-flow-valuation)

现金能否另加取决于原模型是否已覆盖现金及其收益。仅在税费、经营现金流与资本配置等条件相同时，调整派息形式应保持股息加除息剩余价值合计一致。本轮将这两项原则转成逐项去重和等值场景核验。[Damodaran 每股权益价值](https://pages.stern.nyu.edu/adamodar/New_Home_Page/littlebook/valuepershare.htm) · [Damodaran 分红政策的等值条件](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/invfables/dividirrelevance.htm)

具体实现把股息权利、正常化盈利与可分配现金、资本约束、留存增长、终值、税务和风险归属接起来。金融企业用其资本/偿付能力约束，有限资源或到期经营按寿命和回收价值，特别股息逐笔减少对应现金/资产。k_e 和 g_D 由本次研究论证，g_D 为稳态每股股息年增长率，永续式适用条件为 k_e>g_D>-1 且 k_e>0。等号时停止该永续计算，换有依据的模型或记录缺口。

本次设计采用普通股股东税前分配作为通常 V50 口径，特定税后估值须整套假设匹配。R22 按实际投资渠道计算税后净回报。此口径避免因未取得用户税务信息而阻断所有基础估值，也要求税费比较时显式桥接。

下表均为合成场景，百分比属于演示输入。

| 场景 | 预期行为与核对 |
|---|---|
| 每股可持续分红 5 元、k_e=10%、g_D=2%，基础折扣10%、其他折扣0，R22缺数据 | V50=62.50，基础P1=56.25。分红直接进入基础估值 |
| 可持续现金流下降，下一期分红降至4元，其余假设匹配 | V50=50，基础P1=45。减派对应的现金流恶化传入价格 |
| k_e升至12%，其余与第一行相同 | V50=50，基础P1=45。高股息仍受权益必要回报变化影响 |
| 第一行的五年逐期股息加第五年除息终值 | 折现合计62.50，与直接稳态公式一致，预测期/终值分界无重复 |
| 同年末留存105元，或分5元后剩100元 | 按10%折现均为95.454545，转为派息本身未增加总价值 |
| 100元资产中支付10元特别股息 | 剩余资产90元，合计仍100元，只处理一笔分配，不能额外保留原100元资产 |
| 两年有限期各派5元，清算剩余0 | 按10%折现为8.677686，使用有限期现值，终值0有明确清算假设 |
| k_e=g_D、k_e<g_D 或 g_D=-1 | 永续公式域检查拒绝，定向改模型或留缺口 |
| 第一行一致的五年预测，R22净回报要求14%，假设无税费 | U=53.613020，最终P1=53.61。较低门槛对应U≥B时，P1最高为B |
| PE完整估值与DDM均覆盖同一盈利 | 以适用性裁决主方法和差异，股息现值只用于核验或替代，不能相加两个完整权益价值 |
| 股息已除息但未付 | 新买入者不享有该笔股息，现金流清单剔除，仍可计未来有权取得的分配 |
| 无分红、政策不稳定、金融资本约束或DDM输入不全 | 说明适用性及缺口，有可靠替代方法继续估值。核心价值无法约束才走原不可估规则 |

预期减少的误判包括遗漏持续现金分配、把特别股息永久化、分红与留存双算、用完整 PE 价值再加股息现值，以及分红风险已入贴现率后又重复扣折扣。新增的工作量主要在派息时点和现金/资本桥，适用性筛选及原始证据复用控制其范围。DDM 对增长与贴现率敏感，跨模型差异仍须分析师裁决。

## 4. 规则边界

P1 按原公式生成，R22继续取更严格的回报约束。基础估值可以因新的分配证据重算，旧B不作为新V50的固定上限。R9拥挤核验、各scope资格和独立持仓规则按自身证据执行。分红数据缺口只影响依赖它的论证，可靠替代估值仍可继续。

股息率较高本身没有统一奖励。研究中进入V50的现金流、倍数或资本成本改善与折扣变化逐项消重。既有生效限制按原ID/scope接续，纯价格变化按原运行时处理。

## 5. 新版框架与研究入口

- [canonical §4.1A](../../../../framework/investment_framework.md)
- [compact §7](../../../../framework/investment_framework_compact.md)
- [stock-research 入口](../../../../.agents/skills/stock-research/SKILL.md)
- [估值交付](../../../../.agents/skills/stock-research/references/valuation-and-output.md)
- [审计接入](../../../../.agents/skills/stock-research/references/research-consistency.md)

## 6. 版本、兼容与接续

本轮基线为本地 dev 的 `021aea1`，新工作树位于 `/private/tmp/investment-dividend-20261112`。用户授权范围为框架完善与配套同步，已在该工作树形成可审阅修改。proposed 方法标识为 `stock-two-price-controls-v2-etf-relative-v1-dividend-v1`，基线为 `stock-two-price-controls-v2-etf-relative-v1`。

旧冻结批次保留其原方法，只有实际冻结方法含§4.1A才执行本增补。JSON v4/audit-v2 的字段接口兼容，方法语义有变化，不能只凭schema相同就宣布历史结论兼容。DDM/FCFE及带独立权益调整的模型用原other接口，纯利润×PE继续走profit_pe。未来采纳时，应复核以分红为主要持有理由、原估值未明确分配归属的公司。当前未生成逐股新报告或采纳handoff。

| 文件与版本 | 完整 SHA-256 | 方法指纹 |
|---|---|---|
| investment_framework.md 基线 | `4e8c0e7e4df1027a5affaad3c7c18263a8cc83bc9448f9a969851729bf154782` | `09a175947d764b73e4822d6be2af80020a392330b5ff1e5af845cd42359a50d4` |
| investment_framework.md 修订 | `d552e85ab0b2a8339e7e082619ecfcc01107194bdf459ff7210ae7cb51577572` | `57044646b3678e2ace6baa720952a5003886e218236673ad8df1a1fd1b68727a` |
| investment_framework_compact.md 基线 | `434a1c84337dc916fbdac23c9b3b02e40e790cf59424c83bd93699548bac0eef` | `f78fc877aa3e3093727dc7b31786ffdcb6d61d6aacd5d5d02286a3ce16c740e8` |
| investment_framework_compact.md 修订 | `4d83254d767c772db6c54ab51777ac972cf2bd1a9db5f2f1b8c5a0873c540c8e` | `0d28afde4034c4ddde25d226101dc22429a09b13d946fc526d09b5430c50ea7a` |

## 7. 验证

- `python3 scripts/investment_framework_governance.py --check` 通过，两份方法身份一致，R/D结构与引用检查通过，受限观测块逐字保留。
- bundled `skill-creator/scripts/quick_validate.py .agents/skills/stock-research` 通过，新增入口依据实际冻结方法执行，单阶段与领域边界核对通过。
- `python3 -m unittest discover -s tests -v` 实际运行1341项，首次1294项通过，47项因环境失败。其中44项回环HTTP用例和2项进程检查受沙箱限制，1项系统Python在隔离模式下缺PyMuPDF。以已有 `/Users/xinquanzhou/miniconda3/bin/python3` 并允许本机端口/进程检查，定向重跑全部47项，47/47通过。测试代码与生产脚本均无修改。该结果为完整首轮加失败项复验，通过项未另做全量重复运行。
- 12项独立合成检查通过，覆盖稳态与五年分解一致、R22未量化传导、减派、贴现率上升、留存/派息等值、特别分配的资产减少、有限期终值、永续域边界、R22更严约束、v4/audit-v2的other模型回读、重复风险归属拒绝及错误P1拒绝。采用Decimal计算，等值现值比较容差为1e-20元以容纳运算舍入。
- `git diff --check` 通过，文档相对链接可解析。canonical的Gate/机制段与Terminal段、compact的R/D/Gate段与Terminal段逐字匹配基线。本次独立复核涵盖新增语义及与原条款的衔接。

机械结果位于 `output/dividend-valuation-20261112/`，其中 `unittest.log`、`failed-tests.json`、`retry-tests.log` 保留首轮及复验，`check_dividend.py`、`dividend-checks.json` 和合成报告/JSON保留算术与接口复现材料。

上述检查证明结构、演示算术及现有接口衔接。DDM现金流来源、模型选择、不同风险ID的经济去重和未来分红可持续性仍由逐股研究核验。本次没有真实证券API、实盘或收益有效性测试，外部方法依据仅使用已读的一手公开页面。


## 8. 精简版同步

逐项核对了新增条款的适用对象、证据要求、公式、参数域、时点、税务、主辅模型裁决、去重、R22衔接、缺口及复评动作。两份框架的受限观测块与各自基线逐字一致，状态日期仍为2026-11-08。原R1–R22、D1–D8定义和引用保留，新增规则放估值章节，保持原全局编号。

三项自包含抽检覆盖R22缺输入但分红可估、同日留存与派息等值、k_e≤g_D的永续失效。compact均能给出与canonical相同的路径。数值/公式检验与章节引用检查通过，决策链继续由估值进入P1和R22。新增§4.1A与现行R22的唯一计价要求一致，未发现本次增补内的口径冲突。

| 文件 | UTF-8字节 before→after | 行数 before→after |
|---|---|---|
| investment_framework.md | 105401 → 112104 | 784 → 811 |
| investment_framework_compact.md | 69695 → 74667 | 522 → 534 |

本次保真结论限于新增条款及其衔接，并通过差异检查保留其余原文。既有历史市场事实和整套投资方法有效性未在本轮重新验证。
