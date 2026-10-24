# 元框架调研结果

## 1. 基本信息

- 调研时点：2026-10-25，Asia/Shanghai；generator=codex；mode=full+publish；本期统一 `revision=2`。公开证据访问截至本次写作时；A 股及港股行情最新已读交易日 10/23，美国财政部利率最新已读 10/23。10/24–25 为 A 股休市日，不以未来公布结果填充。
- 市场范围：中国 A 股 + 港股。本报告仅做元研究；研究机制优先级不等于全市场已实现收益归因，也不等于个股买入、加仓或存量卖出判断。已实现收益的严格横截面归因样本 `null`，真实账户和成交 `null`。
- 生产方法：当前 `origin/main=c9ce8d8af2f5a61bb0471e1ccfd32b2e1501316f` 已合并 PR #50 `6f797ed9223225b68b97db7f7dc9e2cc1c44ab43` 与 PR #51 `346caada9172b4346c6b9246cb66978b06024ba4`，以 `stock-two-price-controls-v2` 两份正文为准；canonical 全文 SHA-256 `773677164aee09f006d80afda8e7484f00b05a489061903754b7f76ffec78ed7`、compact `57d9a8e4530e32e53a5d06ab80dc7244d3dc67fd28d95951890dc68c25453ea2`，见[本期方法冻结副本](evidence/investment-2026-10-25-handoff-r2-methods/investment_framework.md)和[审计](evidence/adoption-review.md)。本期不提议改方法。
- 接续边界：10/18 `handoff-r2` 虽为当时 adopted，但所绑两份方法指纹与 #50/#51 之后主线不同，`compatibility=[]`，本期 helper `select --date 2026-10-25` 返回 `null`。10/18 [正式市场报告](../2026-10-18/investment-2026-10-18-market-research-r2.md)只作有日期的历史比较；本报告在现行方法下重新判读状态。旧 P2/T2、P2 步长及其推价公式已退休，当前只有 P1/T1 两个核心价格与独立的新增、追加、持仓处置控制；不以旧术语呈现 active 指令。
- 证据路径：官方原文核验与披露/数据期见本期 [宏观笔记](evidence/macro-sources.md)、[中观笔记](evidence/industry-sources.md)及已保存的[行情账本](evidence/market-sources.md)。真实 Tushare API 回执在[evidence/tushare-inputs.json](evidence/tushare-inputs.json)与[成交口径回执](evidence/tushare-total-turnover.json)；API 成功不证明所有交易所字段齐全。发布/采用状态截至本报告写作时尚待入口核验，不能预称已推送或本报告已 adopted。

## 2. 当前主要矛盾

- 一句话概括：海外通胀与贴现压力、国内内需和杠杆承接不足仍在，海外 AI 资本开支呈强投入但回报及公司路径分化、国内政策仍待份额传导，两者必须转化为 A/H 企业可核的订单、利润率和现金流才足以对冲成本及估值压缩。
- 解决者：近端正式报表有利润率与 OCF 支撑、订单真实且能转嫁原料成本的公司；供给冲击受益者须证明可售产量、价格传导和 85 美元回落时现金流；政策受益者须有可归属的财政/招采/规则第二环和盈利锚。海外企业的 capex、创新药 BD 交割或中国部委文件仅构成不同验证链的起点。[台积电 10/15 Q3 法说会逐字稿](https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-10/eba4fac72873bf546b669bd2b5d973df5c93215d/TSMC%203Q26%20Transcript.pdf)、[HUTCHMED 10/21 交割公告](https://www.globenewswire.com/news-release/2026/10/21/3385054/0/en/hutchmed-announces-closing-of-kras-egfr-antibody-conjugate-therapy-license-to-gsk-outside-china.html)、[科技部 10/20 指导意见](https://most.gov.cn/kjbgz/202610/t20261020_197532.html)。
- 被压制者：以隐含降息扩张而缺近端盈利对冲的高估值成长；购进价格涨幅高于出厂端、收入又依赖内需的制造与消费公司；只凭低位置或规划文字做承接/份额传导的候选。10/23 Tushare 科创50指数日线 `000688.SH` 收盘 1345.5146（10/16 为 1358.647，约 -0.97%），仍低于现行 1516.2 深化线及 1577.36 重建线；这是行情供应商数据，直接交易所指数原件未取，不标作 `official_close`。单一指数弱不等于全部持仓经营逻辑失效。[本期 API 回执](evidence/tushare-inputs.json)

## 3. 当前主导收益来源

- 主导项1：**盈利兑现**，作为当前研究筛选与可维持估值的主导分子来源。上期已核的台积电 Q3 与 capex 指引仍提供先进制程外部需求锚；**本周** Meta Q3 收入 646.01 亿美元（+26%）但 GAAP 营业利润 129.88 亿美元（-37%）、公司定义非 GAAP FCF -21.2 亿美元，全年含融资租赁本金 capex 指引由 1300–1450 亿收窄为 1350–1450 亿美元（仅下限提高）；Tesla Q3 经营现金流 62.63 亿、capex 47.32 亿、公司定义 FCF 15.31 亿美元，其 2026 capex 文字由“超过 250 亿”变为“超过 200 亿美元”，是**最低预期表述下移**，非精确预算削减，也不证明 AI 项目统一砍单。Meta 当季 GAAP 利润受 98.9 亿美元诉讼和解费用影响，不可只读利润同比或调整后数字。两个外部样本显示 AI 投入强度与现金承受能力分化，不能机械推出 A/H 订单同步上修或下修。本周 HUTCHMED 与 GSK 的 HMPL-A830 许可协议已交割，首付款 1.10 亿美元为“预计短期收到”，不能记作已到账或全部有条件里程碑已入当期收入；也不能外推为恒瑞、康方或创新药全行业盈利兑现。A/H 具体公司仍需合同→交付→回款→利润率与 OCF 的连续验证。[台积电逐字稿](https://investor.tsmc.com/english/encrypt/files/encrypt_file/reports/2026-10/eba4fac72873bf546b669bd2b5d973df5c93215d/TSMC%203Q26%20Transcript.pdf)、[Meta Q3 公告](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/)、[Tesla Q3 SEC 附件](https://www.sec.gov/Archives/edgar/data/1318605/000162828026066738/exhibit9914.htm)、[Tesla Q3 10-Q](https://ir.tesla.com/_flysystem/s3/sec/000162828026066775/tsla-20260930-gen.pdf)、[Tesla Q2 10-Q](https://ir.tesla.com/_flysystem/s3/sec/000162828026049270/tsla-20260630-gen.pdf)、[HUTCHMED 公告](https://www.globenewswire.com/news-release/2026/10/21/3385054/0/en/hutchmed-announces-closing-of-kras-egfr-antibody-conjugate-therapy-license-to-gsk-outside-china.html)
- 主导项2：**政策重估的条件性候选**，主要是事件驱动重估的研究线索，尚非已兑现的全市场收益归因。10/20 科技部刊载 11 部门 10/19 落款科技金融《指导意见》，提出区域基金、再贷款试点与央地资金保障等路径；10/19 药监会议提出 AI+药品监管专项计划。所读文本均未给被研究 A/H 企业的具体获配、招标中标、到款或收入；规划型政策链目前仍主要停在 (a)，第二环 (b) 须逐公司查证。供给冲击分化亦值得研究：IEA 10/14 同时报 9 月供给回升和海湾安全风险，且预计需求破坏，高油价不能直接固化上游稳态现金流。[科技部原文](https://most.gov.cn/kjbgz/202610/t20261020_197532.html)、[上海药监局转载国家药监会议](https://yjj.sh.gov.cn/zjyw/20261021/d9173c5de29349df90dccef5b68bec9a.html)、[IEA 10 月油市报告](https://www.iea.org/reports/oil-market-report-october-2026)
- 资金与风格：沪深成交用 `000001.SH` 上证综指全市场成交额加 `399106.SZ` 深证综指全市场成交额，而非上证综指加 `399001.SZ` 深证成指成分样本。10/21、22、23 依次 **1.429344、1.528708、1.956258 万亿元**；10/23 放量一天不能替代三天合取。Tushare 沪深北三所完整两融余额 10/21 为 **24791.31277149 亿元**，10/22 为 **24556.91846989 亿元**，日差 **-234.39430160 亿元**，独立命中现行“单日 -150 亿以上偿还”深化线；10/23 仅取得上交所，缺深交所/北交所，完整余额和日差均 `null`，不能补零或用单所代理。科创50 10/21–23 为 1343.2818/1305.8731/1345.5146，三日均低于 1516.2。[API 回执](evidence/tushare-inputs.json)、[成交回执](evidence/tushare-total-turnover.json)
- 港股：10/23 香港中通社当日电讯、10/24 10:38 刊文报恒指 23093.37 点、主板成交 2497.84 亿港元，恒指周跌 4.52%，恒生科技指数报道整数 3871 点、周跌 5.76%。这可表述为当周风险偏好弱与成交活跃并存；报道没有南向净流、估值分位或高息股利差，不能把成交当净流、下跌当“便宜”或推断持续托底。[香港中通社报道](https://www.hkcna.hk/cn/content/s6adc1a0ae4b0e4e6f3d63dcb.html)；HKEX 官方 [9 月月报](https://www.hkex.com.hk/Market-Data/Statistics/Consolidated-Reports/HKEX-Monthly-Market-Highlights?sc_lang=en&select=%7B0313FF24-82C0-4802-A7D5-5E90470EC17D%7D)仅可作较早成交背景，不是本周南向净买入。
- 非主导项说明：**估值修复**受负反馈深化和海外分母压力限制；**风险偏好抬升**未由 10/23 单日反弹证实；**流动性宽松**既不是现行买入条件，也不能由 M2 或成交额推出；**供给出清**不与海湾外生供给冲击同义，PPI 正值不能替代需求；**海外映射**仍缺 A/H 公司合同和现金流；政策文件方向不能直接折现为企业资本回报。故上述两项是本期研究驱动排序，已实现全市场收益归因保留 `null`。

## 4. 当前关键约束

- 约束1：**海外扰动与高估值贴现压力**。美国 BLS 10/14 发布 9 月 CPI 总同比 3.7%、核心环比 0.3%，命中现行“≥3.6% 或 ≥0.3%”前置观察，未达总同比严格 >4% 分支。[BLS 原文](https://www.bls.gov/news.release/archives/cpi_10142026.htm) 美联储 9/16 已加息 25bp 至 3.75%–4.00%，9 月 SEP 年底 4.10%仅是当时参与者预测中值，现行框架用作“无降息、年内可能再加一次”估值压力情景，不能说委员会已承诺下次加息。[FOMC 声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm) 财政部同口径 CMT 10/19–23 十年期 5.15/5.12/5.13/4.96/5.00%、30 年期 5.48/5.42/5.42/5.29/5.33%。10/22 的 4.96%和 10/23 恰 5.00%令最近五日**严格 >5%**不成立；上期确已触发的二次复评历史仍在，不冒充已逐股完成。长端下行不满足现行 FOMC“不加息且官方证据支持紧缩路径回撤”出口；10/27–28 会议尚未来到，全面执行档位不能提前撤。[美国财政部逐日表](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202610&type=daily_treasury_yield_curve)、[美联储日历](https://www.federalreserve.gov/newsevents/2026-october.htm)
- 约束2：**需求不足与投入端价格压力**。国家统计局 10/19 公布三季度实际 GDP 同比 4.5%、前三季 4.6%、前三季固投 -7.2%、地产投资 -20.6%；9 月社零同比 1.1%，较 8 月 0.4%改善但仍低于现行严格 >2% 的内需解除第一项。PPI 出厂同比 5.0%、购进 6.9%，剪刀差 1.9 个百分点，较 8 月 2.0 略收窄；统计局官方解读说明原油、有色、煤推动较多，生活资料出厂 -0.1%。这是一点点成本传导边际改善，不能将总 PPI 涨幅称为内需反转。中国人民银行官网 9 月单月新增人民币贷款及同比可比原文未读，贷款第二项 `unknown`，但社零第一项已失败，故同月两项合取 `not_met`，内需弱约束维持。[国家统计局经济发布](https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202610/t20261019_1965618.html)、[9 月零售明细](https://www.stats.gov.cn/sj/zxfb/202610/t20261019_1965614.html)、[PPI 官方解读](https://www.stats.gov.cn/sj/zxfbhjd/202610/t20261014_1965475.html)
- 约束3：**资金承接不足与第二环证据缺口**。10/23 成交接近但仍低于 2 万亿元，前两日 <1.6 万亿元；科创50供应商三日收盘均 <1516.2，直接交易所原件缺失，10/22 完整两融日差 -234.39 亿。R21 同组三日退出阶梯为 `not_met`（已知两日成交失败已足以判合取不满足；官方指数三日原件和 10/23 完整两融仍 `unknown`），原始 >2 万亿三日 + 完整两融三连净流入 + 科创50收复 1577.36 的重建条件同样 `not_met`。本周 HUTCHMED BD 交割是**该公司的合同进度**，并非政策第二环；10/20 科技金融指导意见和药监会议未给特定企业新增份额。若继续把规划或低位行情当买入理由，会漏掉政策传导与盈利核验。[API 回执](evidence/tushare-inputs.json)、[科技部原文](https://most.gov.cn/kjbgz/202610/t20261020_197532.html)
- 影响方向：海外利率压长久期高估值，真实近端现金流相对更易验证但高股息仍有拥挤风险；原料/能源涨价理论上利部分上游且损转嫁弱下游，同时高价引致需求破坏；内需弱压收入端依赖内需者，不由“是否政策受益”豁免；外需和真实订单链须检验独立性。回退深化对新承接候选池维持规则层冻结、存量追加买入暂停，**不**推出所有存量持仓清仓。两价方法下，若仅市场/事件冻结且估值事实可靠，可得冻结状态的观察 P1 与可论证 T1，仍无新增暴露许可；真实硬失败或核心估值事实不足不产新 P1。新建仓、追加买入、持仓处置须各按作用对象与持续限制分别裁定。账户执行 `null`。

## 5. 当前研究机制优先级

以下“高/中高/中”依当前已采纳 canonical 的覆盖权重，模板的“低”本期无一类须降档；这是**研究关注度**，不是买入资格或已实现收益。六类均保留原参数、适用对象、例外及解除条件。

- **正反馈强化型：中。** 海外先进制程与 AI capex 提供分子端外部起点，但 Meta 10/21 Q3 的 capex 下限上移同时单季 FCF 为负，Tesla 10/22 10-Q 的全年 capex 最低表述下移同时单季 FCF 为正；两者显示海外投资回报、现金与项目组合分化，**不能**机械当作 A/H 同步增单或砍单。A/H 结构阿尔法仍须逐季利润率/OCF、订单可见度和 2027 估值合理；10/23 科创50反弹 3.04%仅一天，仍在深化线下，不能替代三项条件。微软 FY27Q1 财报按 IR 日历在 10/28，AMD Q3 在 11/3，截至本报告不可预填。高估值个股按现行隐含降息三项合取与盈利对冲例外、追高三重过滤，不因利率短暂回落整体解冻。相关光模块公司 S.5548 命名式风险须核官方进程及美国联邦关键系统收入暴露，未核为 `unknown`，不是现行全面禁令。[Meta 原文](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/)、[Tesla SEC 10-Q](https://ir.tesla.com/_flysystem/s3/sec/000162828026066775/tsla-20260930-gen.pdf)、[中观证据笔记](evidence/industry-sources.md)
- **负反馈修复型：中，当前回退深化。** 10/21–23 科创50供应商收盘均低于 1516.2，官方逐日原件 `null`；成交前两日 <1.6 万亿；10/22 完整两融再有 -234.39 亿单日偿还，提供独立深化证据。R21 退出 `not_met` 基于已知成交失败，原重建 `not_met` 基于已知成交不足。新承接候选（含低位价值轮动）整体冻结、存量追加买入暂停是规则层状态；仅存量硬证据持仓可按公司事实防守持有，卖出需业绩/订单/现金流失效证据。三日中 10/23 完整两融缺项不能补零，也不能把研究完成、指数单日反弹或 10/23 放量写成退出。真实账户执行 `null`。[行情回执](evidence/tushare-inputs.json)
- **周期反转型：中高。** 购进—出厂差 1.9 点较 8 月 2.0 点小幅收敛，但 9 月社零仅 1.1%、贷款原文缺、成交三日不达现行 2.3 万亿需求端升格条件；依内需的化工下游、机械、汽车及可选消费仍按收入假设从严，需求右侧分支只观察。外生海湾油价推涨与反内卷供给政策各有不同传导，不装作需求型周期反转。[统计局经济发布](https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202610/t20261019_1965618.html)
- **稳态现金流型：高。** 海外贴现压力、内需弱与市场反复使已实现 OCF/分红核验重要；港股高息须按同币种股息利差、估值、换手、公募拥挤度现验。10/23 恒指周跌不能作为高息便宜证明；油气双属性现金流仍须 85 美元回落情景，不以 EIA 10/20 现货 115.22 美元冒充 ICE 主力期货结算。[香港中通社](https://www.hkcna.hk/cn/content/s6adc1a0ae4b0e4e6f3d63dcb.html)、[EIA Brent 现货日表](https://www.eia.gov/dnav/pet/hist/RBRTED.htm)
- **事件驱动重估型：高。** 科技金融 11 部门《指导意见》、药监 10/19 会议和旧专项规划仍属政策 (a) 及待验证 (b)；从 9/15 电子信息、9/18 医药等原事件日起计 4–8 周，不因 10/20 新文重启。HUTCHMED/GSK 的交割属于明确合同进展，需到账、会计收入和公司估值跟进，不能代替恒瑞 Novo 合同结算、康方与 Summit/AZ 各自收入归属。政策、合同、利润分层，只有对应公司可归属的招采/资金/份额与盈利锚才进入更高结论。[科技部原文](https://most.gov.cn/kjbgz/202610/t20261020_197532.html)、[HUTCHMED 公告](https://www.globenewswire.com/news-release/2026/10/21/3385054/0/en/hutchmed-announces-closing-of-kras-egfr-antibody-conjugate-therapy-license-to-gsk-outside-china.html)
- **供给冲击重估型：高。** IEA 10 月报告披露 9 月全球供应环比增约 250 万桶/日至 1.023 亿桶/日，同时海湾袭击威胁使恢复脆弱、2026 需求预测同比下降约 260 万桶/日；供给、价格、运费及需求破坏须一体核。EIA 10/19、20 欧洲 Brent FOB 现货 118.82/115.22 美元，**不是**现行油价阈值所需同一布伦特主力合约连续结算；本次没有 ICE 连续序列，130/95/85 美元新触发/解除状态 `unknown`。贵金属与美元连续官方序列亦 `unknown`，原有强美元、85 美元与中下游 V5 100→130 情景仍保留。[IEA 原文](https://www.iea.org/reports/oil-market-report-october-2026)、[EIA 日表](https://www.eia.gov/dnav/pet/hist/RBRTED.htm)

- **最易误判机制：负反馈修复与事件驱动重估。** 单日放量反弹、单公司 BD 交割、文件中的“支持资金”会被串成“承接完成—政策第二环—全行业盈利兑现”；现行 R21 同组三日合取、政策份额传导和个股盈利链均未因此完成。供给冲击也易被误写成需求型周期右侧，PPI 正值不能代替社零/贷款与公司利润传导。

- **监管增量（事件机制的适用性核验）**：美国财政部10/22已披露对外投资NPRM，联邦公报public-inspection文本截至本期已可读取，计划10/26刊登、12/7截止征求意见；本期不能把计划刊登写成已经发生，更不能把提案当现行禁令。特定生物技术、超算和高超音速拟按技术及美国人投资结构界定；独立药物许可不是当然受管投资，但附属交易例外排除技术/技术知识转让合同，不能概括为“BD全部豁免”。按具体主体、股权/合资/技术转让与订单暴露定向核实，不对创新药或港股全市场冻结。[财政部原文](https://home.treasury.gov/news/press-releases/sb0667)、[拟议文本](https://public-inspection.federalregister.gov/2026-21786.pdf)。黄金与ICE DXY本周可采连续序列仍缺；Fed H.10广义美元基准不同，不能代入DXY=100阈值，R17维持unknown。

## 6. 当前最脆弱的叙事

“10/23 放量反弹、长端美债跌回 5%附近，叠加科技金融文件和海外 AI 高投入，说明 A/H 承接已修复、政策受益已落到订单，可以恢复新增。”该叙事同时跨越了三个未经证实的环节：最近三日 R21 与原重建均不满足、FOMC 出口尚未来到、文件未给公司份额/回款；Meta 与 Tesla 的投入和 FCF 分化也没有给 A/H 订单同步方向。相反，把 10/22 下跌或利率压力当作全部优质存量公司盈利失效，同样没有公司级证据。大宗涨价的对称风险是供给恢复与高价需求破坏。[行情回执](evidence/tushare-inputs.json)、[财政部 CMT](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202610&type=daily_treasury_yield_curve)、[Meta Q3](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Third-Quarter-2026-Results/)、[IEA](https://www.iea.org/reports/oil-market-report-october-2026)

## 7. 当前最不能犯的错误

把**行情/政策线索、规则触发、逐股复评完成、持仓执行**串成同一个状态。10/23 单日成交 1.956 万亿不替代同组三日门槛；10/23 单交易所融资不替代沪深北完整两融；10 年 CMT 10/23 恰 5.00%不是严格 >5%且其回落不等于 FOMC 路径回撤；PPI 正值和政策 (a) 不是内需复苏与企业 (b) 份额；EIA 现货不触发 ICE 期货阈值；HUTCHMED 交割不是恒瑞或康方复评完成。现行 P1/T1 报价与新建仓/追加/持仓风险控制独立，冻结观察价不等于买入许可，缺报价也不隐去持续风险。[本期方法审计](evidence/adoption-review.md)

## 8. 当前最需要前置验证的事项

1. **同口径市场状态与作用对象**：继续补 10/23 后同组三 A 股交易日沪深成交（上证综指全市场额+深证综指全市场额）、沪深北完整两融净变动、科创50直接交易所收盘原件；分别按 R21 退出与原重建两个路径复核，不能由单项回升解除。补港股南向净流、股息利差、估值与拥挤分位；目前本周这些均 `unknown`。若仅负反馈修复新增资格受限，应保持其 scope，不扩为全部存量卖出。
2. **海外与成本/内需窗口**：10/27–28 FOMC 声明/发布会出炉后按现行“再加 / 不加且官方路径回撤 / 不加但鹰派”出口复核；后续同月最新已公布社零严格 >2% 与单月新增人民币贷款同比不少增同时核验，9 月已知社零未过。补 ICE 同主力合约 130/95/85 条件所需连续结算、美元与金价连续序列，以及高估值公司真实盈利对冲和油价三层暴露，不以代理错判。
3. **企业级分子及 pending 凭证**：将 Meta/Tesla 实际投资、OCF 和 FCF 分化映射到各 A/H 公司**具体**在手订单与毛利，不从海外 capex 指引直接写国内收入；对 A/H 三季报、政策招采/基金出资/付款、创新药 BD 交割—到账—收入逐层核验。此前五条 pending：`SZ-300308`、`SZ-300502` 的 S.5548 命名政策敞口；`SH-600276`、`HK-01276` 的恒瑞结算；`HK-09926` 的康方收入归属。现行方法下这五条完成凭证 **0**，恒瑞原触发日9/29；旧10/9 v3报告早于10/18接续证据截止且缺当前方法定向复核、沿用旧P2，不当新完成；仅受影响公司定向复评，遵守已有冷却期，不自行启动全量公司批次。[接续审计](evidence/adoption-review.md)

## 9. 供下一步使用的结构化结论

- MAIN_CONTRADICTION: 海外贴现与成本压力、国内内需及杠杆承接不足仍在；Meta/Tesla 显示海外 AI 投入和现金回报分化，国内政策线索须穿透到 A/H 公司真实订单、利润率、现金流与可归属份额才可抵消。
- DOMINANT_RETURN_DRIVERS: 研究优先验证盈利兑现，其次跟踪政策重估的公司级第二环；供给冲击按上游利润与下游成本分化检查。此为研究驱动排序，**全市场已实现收益主导归因=`null`**，不以海外财报、政策文件或单日反弹冒充 A/H 收益统计。
- KEY_CONSTRAINTS: 美国 9 月 CPI 3.7%/核心环比 0.3% 命中前置观察、FOMC 10/27–28 未落地，CMT 最近五日严格 >5%已中断但全面执行出口未出现；9 月社零 1.1%使内需解除合取失败、PPI 购进-出厂差 1.9 点；R21 退出及原重建均未过，第二环和公司兑现证据不足。
- PRIORITY_MECHANISMS: 高=稳态现金流/事件驱动重估/供给冲击重估；中高=周期反转；中=负反馈修复/正反馈强化。沿用现行 canonical 六类权重，买入资格与持仓处置另判，负反馈仍为回退深化。
- FRAGILE_NARRATIVE: 单日放量、美债回落、海外 AI 高投入与科技金融方向被连写成承接完成和公司订单、政策份额及盈利兑现。
- TOP_MISTAKE_TO_AVOID: 将未齐的行情或政策代理当成完整合取及逐股完成，或以非空 P1/T1、旧 P2 术语掩盖新建仓/追加/持仓控制及证据缺口。
- PRECHECK_ITEMS: 同组三日 R21/原重建和港股资金估值口径；10/27–28 FOMC 与滚动同月内需、ICE/美元/金价连续证据；Meta/Tesla 到 A/H 订单/毛利映射、受影响公司正式报表/回款、政策第二环和五条 pending 的新方法完成凭证。

## 来源与核验界限

本报告所引官方原文包括 [BLS CPI](https://www.bls.gov/news.release/archives/cpi_10142026.htm)、[美国财政部 CMT](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202610&type=daily_treasury_yield_curve)、[美联储声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm)及[日历](https://www.federalreserve.gov/newsevents/2026-october.htm)、[国家统计局 10/19 经济发布](https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202610/t20261019_1965618.html)、[9 月社零明细](https://www.stats.gov.cn/sj/zxfb/202610/t20261019_1965614.html)、[科技部 10/20 指导意见](https://most.gov.cn/kjbgz/202610/t20261020_197532.html)、[IEA 10 月油市报告](https://www.iea.org/reports/oil-market-report-october-2026)及[公司许可协议交割公告](https://www.globenewswire.com/news-release/2026/10/21/3385054/0/en/hutchmed-announces-closing-of-kras-egfr-antibody-conjugate-therapy-license-to-gsk-outside-china.html)。披露日、数据期、实际读取和不能外推的范围见本期来源账本及工作笔记。A 股行情为 Tushare 真 API、港股本周指数与成交为香港中通社报道；均不伪称交易所原始指数下载。央行官网 9 月单月贷款原文、ICE 同主力连续结算、10/23 完整沪深北两融、港股南向净流/估值及部分公司收入归属未核，保持 `unknown/null`。本报告未触发真实账户、交易或对外消息。

## r2接续说明

本修订只补美债10/9历史触发的直接来源链，引用10/11未撤回市场研究；本期市场事实与方法不变。首份保留，r2为本期正式接续。
