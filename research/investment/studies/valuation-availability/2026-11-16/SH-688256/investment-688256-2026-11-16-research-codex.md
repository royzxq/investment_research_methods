# 寒武纪（688256.SH）｜新版框架隔离复评

## 0. 数据自检与研究范围

估值日 **2026-11-16**（北京时间），资料上限按原 Codex 回执 2026-11-16T05:34:23.588242+08:00。批次 372adfd34a82424299b6024f5f3baa11，任务 SH-688256。原配额内独立 CLI 中断后，由当前 Codex 会话完成隔离增量复评，运行配置与原批次不同。只使用原数据包、原版公开事实资料及截止前可核披露。无更早同端冻结折扣基线；原同日报告用于接续事实与控制。优先复用已验收公开原件及精确定位，未重复跑公告候选排序。研究用的证据副本及摘要均保存在专用本地工作区。

数据包 output/audits/investment/2026-11-16/valuation-v9-rerun-0f06a665/workspace/output/runs/investment/2026-11-16/372adfd34a82424299b6024f5f3baa11/packs/SH-688256.md，SHA-256 ff944d9478b569fb9774b04538dccd2f012b8cf3033a1c5126e260befc906215。包抓取 2026-11-16 05:00；行情为 2026-11-13 收盘，978.88 元，160,646 手，换手率 2.55%。框架快照 output/audits/investment/2026-11-16/valuation-v9-rerun-0f06a665/workspace/output/runs/investment/2026-11-16/372adfd34a82424299b6024f5f3baa11/framework-snapshot，canonical SHA-256 2b909852e5afacc1ea832a76540c04469439fb016692dc91c32bd7160e13fb32，compact SHA-256 2ad08f195bb6729dd8c7aea96ccaf85c1fa5504aa53cfd18beef90f0e0377d1e。事实 bundle SHA-256 146d750f6a210fddcf1da71a18bc46750d6c8dae94a56b88305bbdb541d96d1c。后续披露及更近行情不进入估值。

## 1. DCS 与研究结论

**V50 留空，P1 留空，T1 本轮不提供报价。** 远期订单、库存回收与利润率缺少可共同验证的中性路径。公开诉请的尺度为 44.26 元/股，足额即付可使压力组权益余额转负，实际支付和权利归属仍无法确定。条件估值可用，但暂不采纳普通股中性 V50 或 P1。 原事件窗口和资格证据在当时仍有效，用途为 frozen，entry/add 为 blocked，持仓须复评。

## 2. Precheck

云端芯片交付放量，研发费用开始摊薄。2025 年收入 64.97 亿元，2026 年前三季度 95.26 亿元，扣非归母 35.23 亿元。按三季报拆分并纳入普通减值后的经营利润约 33.97 亿元，经营利润率约 35.66%，剔除投资收益等非经营项，保留股份支付成本。同期 OCF 2.28 亿元，购建付现 7.88 亿元，净库存加预付 147.09 亿元。通常的技术迭代减值反映到利润率，采购资金占用计入 ΔNWC。

| 核验项 | 截止时点判断 |
|---|---|
| 盈利兑现 | 报表支持近端收益，稳态仍须按周期、产品与归属拆分。 |
| 订单/回款 | 交付或销售事实有支持；远期合同量价不足以验证。 |
| 经营现金流 | 报表范围、货款与工程支出须分辨，保留持有逻辑复评。 |
| 紧缩 | 按冻结政策记录做无降息条件；精确隐含量未定。 |
| AI 联动 | 近端经营显化，未来订单强度与下游预算传导待核。 |
| 政策 | 只作适用判断，不把计划变成经营利润。 |
| 供给和成本 | 买卖双方传导及成本冲击现金桥未闭合，R14 保留仅加仓限制。 |
| CapEx | 已有实际支出和已批计划为情景所用，投用/产出待核。 |
| 拥挤 | 个股换手使用冻结包，不能替代板块温度或压力容量。 |
| R6 时间窗口 | 使用原估值证据时点，原有效窗口及复评要求仍适用。 |

## 3. 机制与经营验证

实际收益和行业量价具正反馈特征，但份额、利润率与兑现时间仍有不确定性。压力情景检验需求转弱、客户占款、库存与投资回收，改善情景需要可验证交付和收入持续性。费用、减值和资金占用各在相应现金流位置计入。

## 4. Gate 与非价格风险

原切点已进入 NVIDIA 定期业绩前 48 小时窗口，保留 R6 冻结、R8 订单可见度、R14 仅加仓限制、取消追加及现金质量和诉讼持仓复评。D5 本轮为独立财报复研，非低位承接。R22 比较以科创芯片 588200/科创50 作为辅助，没有同窗含分红前瞻机会成本估计。 R14 成本传导和现金流必要依据不足，原公司压力结论仍为 unknown。无新增证据足以确认核心经营失效或结束持有逻辑复评。

## 5. 估值与可用性复核

核阅年报 pp102–107、中报 pp94、109、123–126、142–143、三季报 pp5、7–12、诉讼公告 pp1–2、7 月募投结构调整与 8 月激励授予公告。募投结构调配不等于总预算增加；新授予预计费用约 20.20 亿元，为条件会计测算。2025 D&A 2.85 亿元、2026H1 1.77 亿元，后三季完整折旧数字未直接披露。

用前三季度收入 95.26 亿元、单季 35.31 亿元定位 2026 年约 130 亿元收入尺度。2027 年收入 145/180/215 亿元分别表示增速回落、延续扩张、供给释放，增速随后逐年下降。2027 年 EBIT 率 29%/34%/37%，以历史经营利润率、研发和减值为参照，终值为 25%/31%/34%。2026 年末营运资本假设 92–94 亿元，锚于三季末简化 NWC 87.20 亿元。2027 年资本支出 13–17 亿元，考虑前三季购建 7.88 亿元和设备/IP增长投入，折旧随投用增至 2033 年 11–23 亿元。营运资本占收入随采购、票据及回收改善保持或逐步趋近 48%–68%。联合路径受远期订单、价格及库存周转支撑程度影响，暂用于情景。

显式期 2027–2033 年，现金流近似年末折现。折算至 11 月 16 日的年分数增加 45/365，未单计估值日起 2026 年末的现金流增量。币种人民币。集团 FCFF = EBIT−现金税＋折旧−资本开支−ΔNWC。滚动长期生产资产 = 初值＋资本开支−折旧，期末 IC 再加营运资本。稳态从 NOPAT 扣 IC×g。折现率和增速为情景参数。母公司获利年度两免三减半及其他主体 15%/25% 锚定情景。显式期用 EBIT 的 7%–22%，终值用 18%–23%，只用于利润主体构成和优惠期限敏感性。亏损年度不计现金退税，集团亏损不跨主体抵扣。

Q3 现金及交易金融资产 43.66 亿元提供现金池上界，条件表不额外加回未核清用途的余额。经营扩张的 CapEx、营运资本已进现金流。实际 628,854,008 股，经营利润保留股份支付经济成本，同时对新增股本与认购资金成对核对。租赁及一年内相关负债近似扣除 0.19 亿元。公开劳动争议诉请 278.31946 亿元，条件上按足额即付的单项尺度为 44.26 元/股。法院受理及公司聘请律师的意见不足以估计支付概率、时点或期望金额。上市公司赔付与既有持股平台内部转让需区分，避免再扣一笔稀释。

| 联合情景 | WACC | g | 终值IC（亿元） | 显式现值（亿元） | 终值现值（亿元） | 集团EV（亿元） | 条件权益残值（元/股） |
|---|---|---|---|---|---|---|---|
| 压力 | 12.5% | 1.5% | 184.20 | 109.84 | 134.99 | 244.82 | -5.36 至 38.90 |
| 中间 | 11.0% | 2.5% | 258.36 | 231.42 | 451.62 | 683.04 | 64.33 至 108.59 |
| 改善 | 9.5% | 3.0% | 370.56 | 362.92 | 1118.57 | 1481.49 | 191.30 至 235.56 |

中间经营固定，若诉请不支付或按当前公开额一次支付，每股残值 108.59 或 64.33 元。压力组足额支付后每股经济残值 -5.36 元，代表权益耗尽情景。 三组联合假设的数值、逐年现金流和权益桥见[测算明细](conditional-dcf.json)。情景数字仅用于复核输入对价值的影响，正式报价字段留空。当期扣非归母直接乘倍数会混淆暂时税惠、经营占款和诉请。前三季 OCF/归母约 6.1%，因此即使核对了经常利润，仍缺足够证据把其变成可持续股东现金；分红法也缺可持续分配基础。

来源：[2025年年度报告](https://static.cninfo.com.cn/finalpage/2026-03-13/1225007336.PDF)、[2026年半年度报告](https://static.cninfo.com.cn/finalpage/2026-08-08/1225464969.PDF)、[2026年第三季度报告](https://static.cninfo.com.cn/finalpage/2026-10-24/1225620944.PDF)、[调整募集资金投资项目内部投资结构](https://static.cninfo.com.cn/finalpage/2026-07-25/1225441715.PDF)、[向激励对象首次授予限制性股票公告](https://static.cninfo.com.cn/finalpage/2026-08-18/1225478704.PDF)、[关于离职高管诉讼进展的公告](https://static.cninfo.com.cn/finalpage/2026-10-01/1225592148.PDF)、[中信证券关于使用部分闲置募集资金临时补充流动资金的核查意见](https://static.cninfo.com.cn/finalpage/2026-10-24/1225620955.PDF)、[关于公司近期生产经营情况的公告](https://static.cninfo.com.cn/finalpage/2026-10-24/1225621664.PDF)。

## 6. Terminal 与预期

978.88 元行情锚高于本轮条件结果。更快放量、更持续的高利润率或更轻的客户占款可以缩小差距。激励考核、云端市场规模和实际产品口径不能直接互换。 由于尚未采纳独立普通股基准，不做正式反向 DCF。判断市价隐含的持续期和可达性需要先限定需求、税负、资本效率与权利边界。行情偏离诊断情景并不触发结论升级。

## 7. Price Map、监控与恢复条件

最终提取 V50=null、P1=null、T1“本轮不提供T1报价”。模式为 frozen，entry 和 add 均 blocked，holding 为 review_required。后续按作用范围合取独立条件。仓位参数与实际账户信息缺失。

| 条件 | 作用范围 | 状态 | 依据 | 解除证据 |
|---|---|---|---|---|
| VAL_INPUT_V8_20261116 | entry/add | blocking | 核心V50输入未决：未来经营利润/必要投入/主体现金税/资本请求权无法构成中性联合路径；年中财报、Q3、募投、诉讼和完整路演已补证，见§5。 | 五类input_basis全部由未决转为有证据支持或有来源边界；利润、投入、税务、资本配对闭合。；形成独立中性主模型及适用压力/反解，解释市价差异并通过audit-v5和验收，不用任意折扣替缺口。 |
| R8_ORDER_2026Q3 | entry/add | unknown | R8逐季现金兑现、当前订单可见度及2027估值合理未全部验成；路演未披露当前在手金额/备货覆盖，不等于无订单。 | 利润率趋势与OCF匹配、真实订单交付回款可见、2027估值合理三项必要条件全部证成后逐股复评。 |
| R6_NVDA_20261118 | entry/add | blocking | R6：英伟达财报北京2026-11-18约05:20；直接竞争产品/供需和估值锚有实质传导；封口已进入11月16日05:20开始的48h窗口。 | 事件结果正式公开，并按§4预案核竞争供给、价格、国内客户预算和本公司订单/估值实际传导，完成逐股复评。；时间过去或结果偏强本身均不解除；其余独立entry/add约束仍须全部解除。 |
| R14_COST_2026Q3 | add | unknown | R14油价一级约束：办公室能源数据不覆盖委外制造；采购暴露、转嫁和100→130美元压力下现金桥未有可靠边界，适用性和测试均unknown。 | 合法替代路径一：取得公司证据确认本轮成本压力不适用，并解释委外边界。；合法替代路径二：补齐暴露、成本、转嫁/对冲与现金流桥，完成公司适用100→130压力测试及加仓复核；不能由任意假设宣告通过。 |
| ADD_PLAN_20261116 | add | blocking | 正反馈经营利润已有兑现但OCF显著不匹配，按机制纪律取消本轮追加计划；非永久禁持、非卖出结论。 | 后续新一轮研究取得现金转化及订单兑现改善，重建追加论证，且其他add约束全部解除；本轮跌价、触价或预留预算不恢复。 |
| HOLD_OCF_2026Q3 | holding | blocking | 前三季OCF/归母仅6.13%，单Q3经营现金为负、存货预付扩张，已触发核心现金持仓复评，尚未确认造假或逻辑失效。 | 查明库存预付回收、票据到期、必要投入及融资现金来源，并形成核心现金逻辑仍成立的持仓复评结论；确认证伪则升级退出研究要求。 |
| HOLD_LITIGATION_20261001 | holding | blocking | 最新劳动索赔278.319亿元仍未开庭，赔付金额概率时点未能约束；其它6案胜诉不关闭该请求权。 | 生效裁判/撤诉/和解关闭本劳动请求，或获得可约束的赔付金额概率时点及普通股承受性证据并完成持仓复评；律师转述和预计负债空列不自动解除。 |
| D5_USE_20261116 | entry/add | not_applicable | 首次独立财报/候选复评，不是低位轮动新承接，无本端D5基线待解除。 | 将来改低位承接用途须核D5原三项重建及逐股复评；R21仅退出深化到等待。 |
| R9_USE_20261116 | entry/add | not_applicable | 非红利底仓，历史分红不使主营变稳态；无本端R9历史阻断。 | 将来以红利为重要论据须补三项拥挤护栏。 |

| 监测变量 | 披露日 | 复核触发 | 动作 | 来源 |
|---|---|---|---|---|
| 利润现金转化及库存预付占用 | 2026-09-30 | 现金弱已触发复评；下一正式报表若库存预付继续吸资、减值/票据偿付压力扩大，复核核心现金假设。 | 持仓复评；查明资金回收与偿付并形成有证据结论才解除，确认核心现金流证伪则升级退出要求。 | 寒武纪2026第三季度报告pp1、6–12；https://static.cninfo.com.cn/finalpage/2026-10-24/1225620944.PDF |
| 梁军劳动争议程序和请求权 | 2026-10-01 | 下次程序/裁判/和解或诉请变化；当前未决状态已触发持仓复评。 | 核赔付概率金额时点及普通股承受性；生效解决或有据边界并完成复评才解除，不按诉请全额扣债务。 | 寒武纪2026-036诉讼公告pp1–2；https://static.cninfo.com.cn/finalpage/2026-10-01/1225592148.PDF |
| 募集资金实际使用与用途余额 | 2026-10-24 | 后续实际使用/投资结构/临补用途变更，或现金管理与必要投入配对出现差异。 | 重建同日资金—用途桥；公开余额本身不关闭自由现金缺口，核用途与实际付款后才可更新估值输入。 | 中信证券10/24临补核查意见pp1–3、寒武纪归还公告；https://static.cninfo.com.cn/finalpage/2026-10-24/1225620955.PDF |
| 未归属激励与实际归属股数资金 | 2026-08-18 | 新归属/作废/预留授予或费用估计修订。 | 同步更新实际股本、到账款与SBC权利桥；不能只计稀释或把认购款预先加现金，相关控制仍待输入闭合。 | 寒武纪8/18首次授予公告pp8–9及归属公告pp4–5；https://static.cninfo.com.cn/finalpage/2026-08-18/1225478704.PDF |
| 客户和供应商集中披露 | 2025-12-31 | 下一年报同口径集中度/新老客户结构及供应中断披露，若集中加深且现金质量未改善则复核。 | 重评收入持续性与供应成本；匿名客户不自动判假，旧集中度不冒充当前。R8仍需独立订单证据。 | 寒武纪2025年报p30、2026中报风险章节；https://static.cninfo.com.cn/finalpage/2026-03-13/1225007336.PDF |
| 英伟达财报窗口与竞争供需信息 | 2026-10-28 | 财报与指引实际披露后核产品供给、价格/需求及国内客户传导；当前为窗口触发非业绩下修。 | 冻结新增、暂停追加；结果后逐股复评及全部其它scope约束解除，不按过窗自动恢复。 | NVIDIA Investor Relations，10/28财报日程新闻；https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Sets-Conference-Call-for-Third-Quarter-Financial-Results/ |

<!-- research-checks:start -->
研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：

估值链适用性：unavailable；远期订单、库存回收与利润率缺少可共同验证的中性路径。公开诉请的尺度为 44.26 元/股，足额即付可使压力组权益余额转负，实际支付和权利归属仍无法确定。条件估值可用，但暂不采纳普通股中性 V50 或 P1。

估值假设与市价差异（检查声明及算术，不证明预测正确）：
- base_case：远期订单、库存回收与利润率缺少可共同验证的中性路径。公开诉请的尺度为 44.26 元/股，足额即付可使压力组权益余额转负，实际支付和权利归属仍无法确定。条件估值可用，但暂不采纳普通股中性 V50 或 P1。
- method_choice：集团 FCFF 条件情景及归母 PE 或分红替代法检验，估值数字未获正式采纳。
- pe_crosscheck：当期扣非归母直接乘倍数会混淆暂时税惠、经营占款和诉请。前三季 OCF/归母约 6.1%，因此即使核对了经常利润，仍缺足够证据把其变成可持续股东现金；分红法也缺可持续分配基础。
- 市价核对：{"as_of": "2026-11-13", "explanation": "978.88 元行情锚高于本轮条件结果。更快放量、更持续的高利润率或更轻的客户占款可以缩小差距。激励考核、云端市场规模和实际产品口径不能直接互换。", "price": 978.88, "source": "output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/packs/SH-688256.md §1"}
- 反向DCF条件解：{"cases": [], "reason": "没有可采纳的正向普通股估值模型。", "status": "unavailable"}

输入依据与未决缺口：{"capital": {"affects": "v50", "evidence": [{"as_of": "2026-08-18", "source": "https://static.cninfo.com.cn/finalpage/2026-08-18/1225478704.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S6-2026-08-18-incentive-grant.excerpt.txt"}, {"as_of": "2026-08-18", "source": "https://static.cninfo.com.cn/finalpage/2026-08-18/1225478611.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S7-2026-08-18-vesting.excerpt.txt"}, {"as_of": "2026-10-01", "source": "https://static.cninfo.com.cn/finalpage/2026-10-01/1225592148.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S8-2026-10-01-litigation.excerpt.txt"}, {"as_of": "2026-10-24", "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620955.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S9-2026-10-24-temp-capital-sponsor.excerpt.txt"}], "explanation": "Q3 现金及交易金融资产 43.66 亿元提供现金池上界，条件表不额外加回未核清用途的余额。经营扩张的 CapEx、营运资本已进现金流。实际 628,854,008 股，经营利润保留股份支付经济成本，同时对新增股本与认购资金成对核对。租赁及一年内相关负债近似扣除 0.19 亿元。公开劳动争议诉请 278.31946 亿元，条件上按足额即付的单项尺度为 44.26 元/股。法院受理及公司聘请律师的意见不足以估计支付概率、时点或期望金额。上市公司赔付与既有持股平台内部转让需区分，避免再扣一笔稀释。", "gaps": ["同日同币种募集/自有理财和必要经营资本匹配", "现存激励经济请求权与SBC服务成本配对", "劳动赔付概率金额时点及基金剩余请求权"], "status": "unresolved"}, "investment": {"affects": "v50", "evidence": [{"as_of": "2026-08-08", "source": "https://static.cninfo.com.cn/finalpage/2026-08-08/1225464969.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S2-2026-half.excerpt.txt"}, {"as_of": "2026-10-24", "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620944.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S3-2026-q3.excerpt.txt"}, {"as_of": "2026-07-25", "source": "https://static.cninfo.com.cn/finalpage/2026-07-25/1225441715.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S5-2026-07-25-funds-reallocation.excerpt.txt"}, {"as_of": "2026-10-24", "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620955.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S9-2026-10-24-temp-capital-sponsor.excerpt.txt"}], "explanation": "用前三季度收入 95.26 亿元、单季 35.31 亿元定位 2026 年约 130 亿元收入尺度。2027 年收入 145/180/215 亿元分别表示增速回落、延续扩张、供给释放，增速随后逐年下降。2027 年 EBIT 率 29%/34%/37%，以历史经营利润率、研发和减值为参照，终值为 25%/31%/34%。2026 年末营运资本假设 92–94 亿元，锚于三季末简化 NWC 87.20 亿元。2027 年资本支出 13–17 亿元，考虑前三季购建 7.88 亿元和设备/IP增长投入，折旧随投用增至 2033 年 11–23 亿元。营运资本占收入随采购、票据及回收改善保持或逐步趋近 48%–68%。联合路径受远期订单、价格及库存周转支撑程度影响，暂用于情景。", "gaps": ["订单消化和采购/票据付款条件", "必要CapEx、投用/寿命/DA与终值生产性资本"], "status": "unresolved"}, "profit": {"affects": "v50", "evidence": [{"as_of": "2026-03-13", "source": "https://static.cninfo.com.cn/finalpage/2026-03-13/1225007336.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S1-2025-annual.excerpt.txt"}, {"as_of": "2026-08-08", "source": "https://static.cninfo.com.cn/finalpage/2026-08-08/1225464969.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S2-2026-half.excerpt.txt"}, {"as_of": "2026-10-24", "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225621664.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S10-I01-operation-20261024.excerpt.txt"}, {"as_of": "2026-10-26", "source": "https://roadshow.sseinfo.com/stayTuned/41966；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S11-roadshow-excerpt.txt"}], "explanation": "用前三季度收入 95.26 亿元、单季 35.31 亿元定位 2026 年约 130 亿元收入尺度。2027 年收入 145/180/215 亿元分别表示增速回落、延续扩张、供给释放，增速随后逐年下降。2027 年 EBIT 率 29%/34%/37%，以历史经营利润率、研发和减值为参照，终值为 25%/31%/34%。2026 年末营运资本假设 92–94 亿元，锚于三季末简化 NWC 87.20 亿元。2027 年资本支出 13–17 亿元，考虑前三季购建 7.88 亿元和设备/IP增长投入，折旧随投用增至 2033 年 11–23 亿元。营运资本占收入随采购、票据及回收改善保持或逐步趋近 48%–68%。联合路径受远期订单、价格及库存周转支撑程度影响，暂用于情景。", "gaps": ["产品销量售价和订单覆盖", "独立毛利与含SBC研发/人员费用的持续路径"], "status": "unresolved"}, "residual_discount": {"affects": "p1", "evidence": [{"as_of": "2026-10-24", "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620944.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S3-2026-q3.excerpt.txt"}, {"as_of": "2026-10-01", "source": "https://static.cninfo.com.cn/finalpage/2026-10-01/1225592148.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S8-2026-10-01-litigation.excerpt.txt"}], "explanation": "基础价值和已吸收损失尚未采纳，不能定合理残余折扣。", "gaps": ["已吸收经营/资本损失后的独立残余范围及有据区间"], "status": "unresolved"}, "tax": {"affects": "v50", "evidence": [{"as_of": "2026-08-08", "source": "2026年半年度报告 PDF pp94、123–124、138、143，原证据 S2"}], "explanation": "母公司获利年度两免三减半及其他主体 15%/25% 锚定情景。显式期用 EBIT 的 7%–22%，终值用 18%–23%，只用于利润主体构成和优惠期限敏感性。亏损年度不计现金退税，集团亏损不跨主体抵扣。", "gaps": ["各主体未来利润和优惠实际使用有待核验，区间适用于明确情景。"], "status": "bounded"}}

估值可用性复核：远期订单、库存回收与利润率缺少可共同验证的中性路径。公开诉请的尺度为 44.26 元/股，足额即付可使压力组权益余额转负，实际支付和权利归属仍无法确定。条件估值可用，但暂不采纳普通股中性 V50 或 P1。

| 输入 | 已尝试的方法 | 边界依据或失败原因 | 价值影响 | 裁决 |
|---|---|---|---|---|
| profit, investment | 原财报和投资计划锚定三个FCFF情景，另检验归母PE和分红法 | 用前三季度收入 95.26 亿元、单季 35.31 亿元定位 2026 年约 130 亿元收入尺度。2027 年收入 145/180/215 亿元分别表示增速回落、延续扩张、供给释放，增速随后逐年下降。2027 年 EBIT 率 29%/34%/37%，以历史经营利润率、研发和减值为参照，终值为 25%/31%/34%。2026 年末营运资本假设 92–94 亿元，锚于三季末简化 NWC 87.20 亿元。2027 年资本支出 13–17 亿元，考虑前三季购建 7.88 亿元和设备/IP增长投入，折旧随投用增至 2033 年 11–23 亿元。营运资本占收入随采购、票据及回收改善保持或逐步趋近 48%–68%。联合路径受远期订单、价格及库存周转支撑程度影响，暂用于情景。 | 集团经营价值及终值可逐年复算，完整结果见§5。 | 可形成条件模型；需要经营、现金与归属证据收敛后裁决中性基准。 |
| capital | 固定经营现金流，单列请求权和经济归属情景 | Q3 现金及交易金融资产 43.66 亿元提供现金池上界，条件表不额外加回未核清用途的余额。经营扩张的 CapEx、营运资本已进现金流。实际 628,854,008 股，经营利润保留股份支付经济成本，同时对新增股本与认购资金成对核对。租赁及一年内相关负债近似扣除 0.19 亿元。公开劳动争议诉请 278.31946 亿元，条件上按足额即付的单项尺度为 44.26 元/股。法院受理及公司聘请律师的意见不足以估计支付概率、时点或期望金额。上市公司赔付与既有持股平台内部转让需区分，避免再扣一笔稀释。 | 中间经营固定，若诉请不支付或按当前公开额一次支付，每股残值 108.59 或 64.33 元。压力组足额支付后每股经济残值 -5.36 元，代表权益耗尽情景。 | 仍无充分依据采纳普通股 V50。 |
| residual_discount | 逐项分清经营、权益与资格风险后检查剩余折扣 | 当期扣非归母直接乘倍数会混淆暂时税惠、经营占款和诉请。前三季 OCF/归母约 6.1%，因此即使核对了经常利润，仍缺足够证据把其变成可持续股东现金；分红法也缺可持续分配基础。 | 残余折扣仅影响P1；基础价值未采纳，该折扣无法有效论证。 | P1 保持空值。 |

条件结果及适用限制：中间经营固定，若诉请不支付或按当前公开额一次支付，每股残值 108.59 或 64.33 元。压力组足额支付后每股经济残值 -5.36 元，代表权益耗尽情景。
下一项有效证据：取得劳动案公开法院程序或处分结果并核对请求权主体、金额、时间。检查之后公开的财报中库存消化、收入回款和设备投用，重建中性现金流路径。

| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |
|---|---:|---|---|---|
| d_base | 未决 | 未决 |  | initial |
| r_chip | 未决 | 未决 |  | initial |
| r_v5 | 未决 | 未决 |  | initial |
| r_gov | 未决 | 未决 |  | initial |
| r_terminal | 未决 | 未决 |  | initial |

总折扣乘数：未决；用途：frozen。
明确报价：P1=null；T1={"price_condition": "本轮不提供T1报价"}。

| 约束 | 作用 | 状态 | 依据 |
|---|---|---|---|
| VAL_INPUT_V8_20261116 | entry,add: unavailable | blocking | 核心V50输入未决：未来经营利润/必要投入/主体现金税/资本请求权无法构成中性联合路径；年中财报、Q3、募投、诉讼和完整路演已补证，见§5。 |
| R8_ORDER_2026Q3 | entry,add: eligibility | unknown | R8逐季现金兑现、当前订单可见度及2027估值合理未全部验成；路演未披露当前在手金额/备货覆盖，不等于无订单。 |
| R6_NVDA_20261118 | entry,add: freeze | blocking | R6：英伟达财报北京2026-11-18约05:20；直接竞争产品/供需和估值锚有实质传导；封口已进入11月16日05:20开始的48h窗口。 |
| R14_COST_2026Q3 | add: eligibility | unknown | R14油价一级约束：办公室能源数据不覆盖委外制造；采购暴露、转嫁和100→130美元压力下现金桥未有可靠边界，适用性和测试均unknown。 |
| ADD_PLAN_20261116 | add: eligibility | blocking | 正反馈经营利润已有兑现但OCF显著不匹配，按机制纪律取消本轮追加计划；非永久禁持、非卖出结论。 |
| HOLD_OCF_2026Q3 | holding: review_holding | blocking | 前三季OCF/归母仅6.13%，单Q3经营现金为负、存货预付扩张，已触发核心现金持仓复评，尚未确认造假或逻辑失效。 |
| HOLD_LITIGATION_20261001 | holding: review_holding | blocking | 最新劳动索赔278.319亿元仍未开庭，赔付金额概率时点未能约束；其它6案胜诉不关闭该请求权。 |
| D5_USE_20261116 | entry,add: eligibility | not_applicable | 首次独立财报/候选复评，不是低位轮动新承接，无本端D5基线待解除。 |
| R9_USE_20261116 | entry,add: eligibility | not_applicable | 非红利底仓，历史分红不使主营变稳态；无本端R9历史阻断。 |

| 范围 | 当前研究状态 | 未解约束ID |
|---|---|---|
| entry | blocked | VAL_INPUT_V8_20261116, R8_ORDER_2026Q3, R6_NVDA_20261118 |
| add | blocked | VAL_INPUT_V8_20261116, R8_ORDER_2026Q3, R6_NVDA_20261118, R14_COST_2026Q3, ADD_PLAN_20261116 |
| holding | review_required | HOLD_OCF_2026Q3, HOLD_LITIGATION_20261001 |

恢复前须同时解除全部仍有效约束：{"add": ["VAL_INPUT_V8_20261116", "R8_ORDER_2026Q3", "R6_NVDA_20261118", "R14_COST_2026Q3", "ADD_PLAN_20261116"], "entry": ["VAL_INPUT_V8_20261116", "R8_ORDER_2026Q3", "R6_NVDA_20261118"], "holding": ["HOLD_OCF_2026Q3", "HOLD_LITIGATION_20261001"]}。
<!-- research-checks:end -->

<details><summary>计算、风险归属与解除条件审计输入</summary>

<!-- research-audit:start -->
```json
{
  "schema_version": "stock-research-audit/v6",
  "identity": {
    "code": "688256.SH",
    "generator": "codex",
    "valuation_date": "2026-11-16",
    "currency": "CNY"
  },
  "valuation": {
    "kind": "unavailable",
    "reason": "远期订单、库存回收与利润率缺少可共同验证的中性路径。公开诉请的尺度为 44.26 元/股，足额即付可使压力组权益余额转负，实际支付和权利归属仍无法确定。条件估值可用，但暂不采纳普通股中性 V50 或 P1。"
  },
  "baseline": null,
  "discounts": {
    "d_base": {
      "value": null,
      "range": null,
      "risk_ids": [],
      "reason": "合理价值后的独立估计误差/回报要求未定，多个从严标签不叠罚。",
      "change": {
        "kind": "initial",
        "reason": "无同端正式基线；尚未完成合理价值和残余损失边界，未知不按0处理。",
        "evidence": []
      }
    },
    "r_chip": {
      "value": null,
      "range": null,
      "risk_ids": [],
      "reason": "拥挤和压力流动性缺证，不因ETF身份加减。",
      "change": {
        "kind": "initial",
        "reason": "无同端正式基线；尚未完成合理价值和残余损失边界，未知不按0处理。",
        "evidence": []
      }
    },
    "r_v5": {
      "value": null,
      "range": null,
      "risk_ids": [],
      "reason": "未来普通经营损失归模型；独立融资尾部未形成可靠边界。",
      "change": {
        "kind": "initial",
        "reason": "无同端正式基线；尚未完成合理价值和残余损失边界，未知不按0处理。",
        "evidence": []
      }
    },
    "r_gov": {
      "value": null,
      "range": null,
      "risk_ids": [],
      "reason": "未证治理红线；劳动请求权归资本桥而非重复治理折扣。",
      "change": {
        "kind": "initial",
        "reason": "无同端正式基线；尚未完成合理价值和残余损失边界，未知不按0处理。",
        "evidence": []
      }
    },
    "r_terminal": {
      "value": null,
      "range": null,
      "risk_ids": [],
      "reason": "未完成资本化期限和终局检验，不能对未计远景默认收费。",
      "change": {
        "kind": "initial",
        "reason": "无同端正式基线；尚未完成合理价值和残余损失边界，未知不按0处理。",
        "evidence": []
      }
    }
  },
  "risks": [
    {
      "id": "INVENTORY_MARGIN",
      "owner": "margin",
      "economic_key": "2027plus-inventory-obsolescence-operating-loss",
      "description": "未来代际/库龄风险。2026已计减值不再重复扣净资产。",
      "scope": "未来经营利润中的普通减值/售价损失，非当前净库存全额再扣；尚未形成可采纳模型",
      "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620959.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S4-2026-q3-impairment.excerpt.txt"
    },
    {
      "id": "CUSTOMER_REVENUE",
      "owner": "revenue",
      "economic_key": "2027plus-domestic-demand-and-substitution-sales",
      "description": "客户集中、预算、自研及替代影响未来销量。",
      "scope": "未来收入一次体现；与资格缺证的经济损失区分",
      "source": "https://static.cninfo.com.cn/finalpage/2026-03-13/1225007336.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S1-2025-annual.excerpt.txt"
    },
    {
      "id": "CAPITAL_USES",
      "owner": "equity_adjustment",
      "economic_key": "20260930-assets-uses-ordinary-share-attribution",
      "description": "资金来源、用途和未来必要投入的配对未闭合。",
      "scope": "只对未进入经营FCFF的独立资产/请求权作资本桥调整；投入已进FCFF不再扣预留",
      "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620955.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S9-2026-10-24-temp-capital-sponsor.excerpt.txt"
    },
    {
      "id": "TAX_ENTITY",
      "owner": "margin",
      "economic_key": "2027plus-entity-income-cash-tax",
      "description": "优惠到期、亏损无法跨主体利用。",
      "scope": "未来现金税一次体现，不重复税务折扣，不自动现金退款",
      "source": "https://static.cninfo.com.cn/finalpage/2026-08-08/1225464969.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S2-2026-half.excerpt.txt"
    },
    {
      "id": "AWARDS_RIGHT",
      "owner": "equity_adjustment",
      "economic_key": "20260817-existing-unvested-employee-claims",
      "description": "未归属权益与相应认购款配对。",
      "scope": "现存经济请求权；与未来服务费匹配，不对同一权利既全扣SBC又扣完整权利价值",
      "source": "https://static.cninfo.com.cn/finalpage/2026-08-18/1225478704.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S6-2026-08-18-incentive-grant.excerpt.txt"
    },
    {
      "id": "LABOR_CLAIM",
      "owner": "equity_adjustment",
      "economic_key": "20261001-liangjun-labor-compensation-claim",
      "description": "未决劳动赔偿请求。",
      "scope": "本劳动案赔付请求一次计入；不把旧平台已存股票再新增摊薄，不另r_gov/r_v5扣同损失",
      "source": "https://static.cninfo.com.cn/finalpage/2026-10-01/1225592148.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S8-2026-10-01-litigation.excerpt.txt"
    },
    {
      "id": "CAPITAL_COST",
      "owner": "multiple",
      "economic_key": "20261116-tightening-capitalization-duration",
      "description": "紧缩对资本化成本/期限的影响。",
      "scope": "仅未来WACC或真实倍数一次，不重复在d_base收同损失",
      "source": "冻结maintenance/2026-11-15/handoff-r2及source-ledger，报告§4"
    },
    {
      "id": "ELIGIBILITY_ONLY",
      "owner": "eligibility",
      "economic_key": "20261116-research-qualification-evidence",
      "description": "R8、R14及窗口资格未满足不是已发生的数值损失。",
      "scope": "entry/add按scope控制；非扣价项",
      "source": "报告§4、§7；公开原文S2/S3/S11及英伟达官方事件日程"
    }
  ],
  "constraints": [
    {
      "id": "VAL_INPUT_V8_20261116",
      "scope": [
        "entry",
        "add"
      ],
      "status": "blocking",
      "action": "unavailable",
      "reason": "核心V50输入未决：未来经营利润/必要投入/主体现金税/资本请求权无法构成中性联合路径；年中财报、Q3、募投、诉讼和完整路演已补证，见§5。",
      "release_conditions": [
        "五类input_basis全部由未决转为有证据支持或有来源边界；利润、投入、税务、资本配对闭合。",
        "形成独立中性主模型及适用压力/反解，解释市价差异并通过audit-v5和验收，不用任意折扣替缺口。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R8_ORDER_2026Q3",
      "scope": [
        "entry",
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "reason": "R8逐季现金兑现、当前订单可见度及2027估值合理未全部验成；路演未披露当前在手金额/备货覆盖，不等于无订单。",
      "release_conditions": [
        "利润率趋势与OCF匹配、真实订单交付回款可见、2027估值合理三项必要条件全部证成后逐股复评。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R6_NVDA_20261118",
      "scope": [
        "entry",
        "add"
      ],
      "status": "blocking",
      "action": "freeze",
      "reason": "R6：英伟达财报北京2026-11-18约05:20；直接竞争产品/供需和估值锚有实质传导；封口已进入11月16日05:20开始的48h窗口。",
      "release_conditions": [
        "事件结果正式公开，并按§4预案核竞争供给、价格、国内客户预算和本公司订单/估值实际传导，完成逐股复评。",
        "时间过去或结果偏强本身均不解除；其余独立entry/add约束仍须全部解除。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R14_COST_2026Q3",
      "scope": [
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "reason": "R14油价一级约束：办公室能源数据不覆盖委外制造；采购暴露、转嫁和100→130美元压力下现金桥未有可靠边界，适用性和测试均unknown。",
      "release_conditions": [
        "合法替代路径一：取得公司证据确认本轮成本压力不适用，并解释委外边界。",
        "合法替代路径二：补齐暴露、成本、转嫁/对冲与现金流桥，完成公司适用100→130压力测试及加仓复核；不能由任意假设宣告通过。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "ADD_PLAN_20261116",
      "scope": [
        "add"
      ],
      "status": "blocking",
      "action": "eligibility",
      "reason": "正反馈经营利润已有兑现但OCF显著不匹配，按机制纪律取消本轮追加计划；非永久禁持、非卖出结论。",
      "release_conditions": [
        "后续新一轮研究取得现金转化及订单兑现改善，重建追加论证，且其他add约束全部解除；本轮跌价、触价或预留预算不恢复。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "HOLD_OCF_2026Q3",
      "scope": [
        "holding"
      ],
      "status": "blocking",
      "action": "review_holding",
      "reason": "前三季OCF/归母仅6.13%，单Q3经营现金为负、存货预付扩张，已触发核心现金持仓复评，尚未确认造假或逻辑失效。",
      "release_conditions": [
        "查明库存预付回收、票据到期、必要投入及融资现金来源，并形成核心现金逻辑仍成立的持仓复评结论；确认证伪则升级退出研究要求。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "HOLD_LITIGATION_20261001",
      "scope": [
        "holding"
      ],
      "status": "blocking",
      "action": "review_holding",
      "reason": "最新劳动索赔278.319亿元仍未开庭，赔付金额概率时点未能约束；其它6案胜诉不关闭该请求权。",
      "release_conditions": [
        "生效裁判/撤诉/和解关闭本劳动请求，或获得可约束的赔付金额概率时点及普通股承受性证据并完成持仓复评；律师转述和预计负债空列不自动解除。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "D5_USE_20261116",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "reason": "首次独立财报/候选复评，不是低位轮动新承接，无本端D5基线待解除。",
      "release_conditions": [
        "将来改低位承接用途须核D5原三项重建及逐股复评；R21仅退出深化到等待。"
      ],
      "lifecycle": "observation"
    },
    {
      "id": "R9_USE_20261116",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "reason": "非红利底仓，历史分红不使主营变稳态；无本端R9历史阻断。",
      "release_conditions": [
        "将来以红利为重要论据须补三项拥挤护栏。"
      ],
      "lifecycle": "observation"
    }
  ],
  "release_all_of": {
    "entry": [
      "VAL_INPUT_V8_20261116",
      "R8_ORDER_2026Q3",
      "R6_NVDA_20261118"
    ],
    "add": [
      "VAL_INPUT_V8_20261116",
      "R8_ORDER_2026Q3",
      "R6_NVDA_20261118",
      "R14_COST_2026Q3",
      "ADD_PLAN_20261116"
    ],
    "holding": [
      "HOLD_OCF_2026Q3",
      "HOLD_LITIGATION_20261001"
    ]
  },
  "p1_basis": {},
  "valuation_review": {
    "base_case": "远期订单、库存回收与利润率缺少可共同验证的中性路径。公开诉请的尺度为 44.26 元/股，足额即付可使压力组权益余额转负，实际支付和权利归属仍无法确定。条件估值可用，但暂不采纳普通股中性 V50 或 P1。",
    "method_choice": "集团 FCFF 条件情景及归母 PE 或分红替代法检验，估值数字未获正式采纳。",
    "pe_crosscheck": "当期扣非归母直接乘倍数会混淆暂时税惠、经营占款和诉请。前三季 OCF/归母约 6.1%，因此即使核对了经常利润，仍缺足够证据把其变成可持续股东现金；分红法也缺可持续分配基础。",
    "market_check": {
      "price": 978.88,
      "as_of": "2026-11-13",
      "source": "output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/packs/SH-688256.md §1",
      "explanation": "978.88 元行情锚高于本轮条件结果。更快放量、更持续的高利润率或更轻的客户占款可以缩小差距。激励考核、云端市场规模和实际产品口径不能直接互换。"
    },
    "reverse_dcf": {
      "status": "unavailable",
      "reason": "没有可采纳的正向普通股估值模型。",
      "cases": []
    },
    "input_basis": {
      "profit": {
        "status": "unresolved",
        "affects": "v50",
        "evidence": [
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-03-13/1225007336.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S1-2025-annual.excerpt.txt",
            "as_of": "2026-03-13"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-08-08/1225464969.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S2-2026-half.excerpt.txt",
            "as_of": "2026-08-08"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225621664.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S10-I01-operation-20261024.excerpt.txt",
            "as_of": "2026-10-24"
          },
          {
            "source": "https://roadshow.sseinfo.com/stayTuned/41966；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S11-roadshow-excerpt.txt",
            "as_of": "2026-10-26"
          }
        ],
        "explanation": "用前三季度收入 95.26 亿元、单季 35.31 亿元定位 2026 年约 130 亿元收入尺度。2027 年收入 145/180/215 亿元分别表示增速回落、延续扩张、供给释放，增速随后逐年下降。2027 年 EBIT 率 29%/34%/37%，以历史经营利润率、研发和减值为参照，终值为 25%/31%/34%。2026 年末营运资本假设 92–94 亿元，锚于三季末简化 NWC 87.20 亿元。2027 年资本支出 13–17 亿元，考虑前三季购建 7.88 亿元和设备/IP增长投入，折旧随投用增至 2033 年 11–23 亿元。营运资本占收入随采购、票据及回收改善保持或逐步趋近 48%–68%。联合路径受远期订单、价格及库存周转支撑程度影响，暂用于情景。",
        "gaps": [
          "产品销量售价和订单覆盖",
          "独立毛利与含SBC研发/人员费用的持续路径"
        ]
      },
      "investment": {
        "status": "unresolved",
        "affects": "v50",
        "evidence": [
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-08-08/1225464969.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S2-2026-half.excerpt.txt",
            "as_of": "2026-08-08"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620944.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S3-2026-q3.excerpt.txt",
            "as_of": "2026-10-24"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-07-25/1225441715.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S5-2026-07-25-funds-reallocation.excerpt.txt",
            "as_of": "2026-07-25"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620955.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S9-2026-10-24-temp-capital-sponsor.excerpt.txt",
            "as_of": "2026-10-24"
          }
        ],
        "explanation": "用前三季度收入 95.26 亿元、单季 35.31 亿元定位 2026 年约 130 亿元收入尺度。2027 年收入 145/180/215 亿元分别表示增速回落、延续扩张、供给释放，增速随后逐年下降。2027 年 EBIT 率 29%/34%/37%，以历史经营利润率、研发和减值为参照，终值为 25%/31%/34%。2026 年末营运资本假设 92–94 亿元，锚于三季末简化 NWC 87.20 亿元。2027 年资本支出 13–17 亿元，考虑前三季购建 7.88 亿元和设备/IP增长投入，折旧随投用增至 2033 年 11–23 亿元。营运资本占收入随采购、票据及回收改善保持或逐步趋近 48%–68%。联合路径受远期订单、价格及库存周转支撑程度影响，暂用于情景。",
        "gaps": [
          "订单消化和采购/票据付款条件",
          "必要CapEx、投用/寿命/DA与终值生产性资本"
        ]
      },
      "tax": {
        "status": "bounded",
        "affects": "v50",
        "evidence": [
          {
            "source": "2026年半年度报告 PDF pp94、123–124、138、143，原证据 S2",
            "as_of": "2026-08-08"
          }
        ],
        "explanation": "母公司获利年度两免三减半及其他主体 15%/25% 锚定情景。显式期用 EBIT 的 7%–22%，终值用 18%–23%，只用于利润主体构成和优惠期限敏感性。亏损年度不计现金退税，集团亏损不跨主体抵扣。",
        "gaps": [
          "各主体未来利润和优惠实际使用有待核验，区间适用于明确情景。"
        ]
      },
      "capital": {
        "status": "unresolved",
        "affects": "v50",
        "evidence": [
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-08-18/1225478704.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S6-2026-08-18-incentive-grant.excerpt.txt",
            "as_of": "2026-08-18"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-08-18/1225478611.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S7-2026-08-18-vesting.excerpt.txt",
            "as_of": "2026-08-18"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-10-01/1225592148.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S8-2026-10-01-litigation.excerpt.txt",
            "as_of": "2026-10-01"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620955.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S9-2026-10-24-temp-capital-sponsor.excerpt.txt",
            "as_of": "2026-10-24"
          }
        ],
        "explanation": "Q3 现金及交易金融资产 43.66 亿元提供现金池上界，条件表不额外加回未核清用途的余额。经营扩张的 CapEx、营运资本已进现金流。实际 628,854,008 股，经营利润保留股份支付经济成本，同时对新增股本与认购资金成对核对。租赁及一年内相关负债近似扣除 0.19 亿元。公开劳动争议诉请 278.31946 亿元，条件上按足额即付的单项尺度为 44.26 元/股。法院受理及公司聘请律师的意见不足以估计支付概率、时点或期望金额。上市公司赔付与既有持股平台内部转让需区分，避免再扣一笔稀释。",
        "gaps": [
          "同日同币种募集/自有理财和必要经营资本匹配",
          "现存激励经济请求权与SBC服务成本配对",
          "劳动赔付概率金额时点及基金剩余请求权"
        ]
      },
      "residual_discount": {
        "status": "unresolved",
        "affects": "p1",
        "evidence": [
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-10-24/1225620944.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S3-2026-q3.excerpt.txt",
            "as_of": "2026-10-24"
          },
          {
            "source": "https://static.cninfo.com.cn/finalpage/2026-10-01/1225592148.PDF；本地 output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S8-2026-10-01-litigation.excerpt.txt",
            "as_of": "2026-10-01"
          }
        ],
        "explanation": "基础价值和已吸收损失尚未采纳，不能定合理残余折扣。",
        "gaps": [
          "已吸收经营/资本损失后的独立残余范围及有据区间"
        ]
      }
    },
    "availability_review": {
      "decision_reason": "远期订单、库存回收与利润率缺少可共同验证的中性路径。公开诉请的尺度为 44.26 元/股，足额即付可使压力组权益余额转负，实际支付和权利归属仍无法确定。条件估值可用，但暂不采纳普通股中性 V50 或 P1。",
      "diagnostic_summary": "中间经营固定，若诉请不支付或按当前公开额一次支付，每股残值 108.59 或 64.33 元。压力组足额支付后每股经济残值 -5.36 元，代表权益耗尽情景。",
      "next_evidence": "取得劳动案公开法院程序或处分结果并核对请求权主体、金额、时间。检查之后公开的财报中库存消化、收入回款和设备投用，重建中性现金流路径。",
      "attempts": [
        {
          "inputs": [
            "profit",
            "investment"
          ],
          "method": "原财报和投资计划锚定三个FCFF情景，另检验归母PE和分红法",
          "bounds_or_failure": "用前三季度收入 95.26 亿元、单季 35.31 亿元定位 2026 年约 130 亿元收入尺度。2027 年收入 145/180/215 亿元分别表示增速回落、延续扩张、供给释放，增速随后逐年下降。2027 年 EBIT 率 29%/34%/37%，以历史经营利润率、研发和减值为参照，终值为 25%/31%/34%。2026 年末营运资本假设 92–94 亿元，锚于三季末简化 NWC 87.20 亿元。2027 年资本支出 13–17 亿元，考虑前三季购建 7.88 亿元和设备/IP增长投入，折旧随投用增至 2033 年 11–23 亿元。营运资本占收入随采购、票据及回收改善保持或逐步趋近 48%–68%。联合路径受远期订单、价格及库存周转支撑程度影响，暂用于情景。",
          "impact": "集团经营价值及终值可逐年复算，完整结果见§5。",
          "conclusion": "可形成条件模型；需要经营、现金与归属证据收敛后裁决中性基准。"
        },
        {
          "inputs": [
            "capital"
          ],
          "method": "固定经营现金流，单列请求权和经济归属情景",
          "bounds_or_failure": "Q3 现金及交易金融资产 43.66 亿元提供现金池上界，条件表不额外加回未核清用途的余额。经营扩张的 CapEx、营运资本已进现金流。实际 628,854,008 股，经营利润保留股份支付经济成本，同时对新增股本与认购资金成对核对。租赁及一年内相关负债近似扣除 0.19 亿元。公开劳动争议诉请 278.31946 亿元，条件上按足额即付的单项尺度为 44.26 元/股。法院受理及公司聘请律师的意见不足以估计支付概率、时点或期望金额。上市公司赔付与既有持股平台内部转让需区分，避免再扣一笔稀释。",
          "impact": "中间经营固定，若诉请不支付或按当前公开额一次支付，每股残值 108.59 或 64.33 元。压力组足额支付后每股经济残值 -5.36 元，代表权益耗尽情景。",
          "conclusion": "仍无充分依据采纳普通股 V50。"
        },
        {
          "inputs": [
            "residual_discount"
          ],
          "method": "逐项分清经营、权益与资格风险后检查剩余折扣",
          "bounds_or_failure": "当期扣非归母直接乘倍数会混淆暂时税惠、经营占款和诉请。前三季 OCF/归母约 6.1%，因此即使核对了经常利润，仍缺足够证据把其变成可持续股东现金；分红法也缺可持续分配基础。",
          "impact": "残余折扣仅影响P1；基础价值未采纳，该折扣无法有效论证。",
          "conclusion": "P1 保持空值。"
        }
      ]
    }
  }
}
```
<!-- research-audit:end -->

</details>


<!-- research-acceptance-view:start -->
共享验收：R14 缺证不能判通过；各范围全部有效约束解除后才可恢复研究资格。
R14：unknown / unknown。
| R14 必要输入 | 证据状态 |
|---|---|
| exposure | supported |
| cost_exposure | unknown |
| pass_through | unknown |
| ocf_bridge | unknown |
| 恢复范围 | 必须全部解除的当前约束 |
|---|---|
| entry | VAL_INPUT_V8_20261116, R8_ORDER_2026Q3, R6_NVDA_20261118 |
| add | VAL_INPUT_V8_20261116, R8_ORDER_2026Q3, R6_NVDA_20261118, R14_COST_2026Q3, ADD_PLAN_20261116 |
| holding | HOLD_OCF_2026Q3, HOLD_LITIGATION_20261001 |
规则内部合法替代路径保留；不同独立约束之间不能相互替代。运行时价格和账户条件仍须另行核验。
<!-- research-acceptance-view:end -->

<!-- research-acceptance:start -->
```json
{
  "schema_version": "stock-research-acceptance/v1",
  "r14": {
    "applicability": "unknown",
    "stress_test": "unknown",
    "constraint_ids": [
      "R14_COST_2026Q3"
    ],
    "reason": "Fabless办公室低油耗不能排除外包制造/材料能源成本和客户算力成本。公司采购暴露、转嫁与压力现金桥缺证，不以假设正数通过。",
    "inputs": {
      "exposure": {
        "status": "supported",
        "sources": [
          {
            "path": "output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S12-I02-esg-2025.excerpt.txt",
            "sha256": "679f734ca3e3d70b22aca860ff7199b2608627d218f9a4c4eb574e5e3f6753d5",
            "quote": "运营主要使用外购电力和市政用水",
            "as_of": "2026-03-13"
          }
        ],
        "derivation": "此句只支持办公运营边界，不包含委外生产；结合S2原材料/封测风险，适用性仍需补证。"
      },
      "cost_exposure": {
        "status": "unknown",
        "sources": [
          {
            "path": "output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S2-2026-half.excerpt.txt",
            "sha256": "71565b4663ae13d3f8d22c9836120c9c515545b9e04f489042cc809561127f68",
            "quote": "原材料及\n封装测试成本",
            "as_of": "2026-08-08"
          }
        ],
        "derivation": "成本类别可核，能源占比、采购价格的油价弹性未披露，不能设固定比例。"
      },
      "pass_through": {
        "status": "unknown",
        "sources": [],
        "derivation": "完整财报和路演未给售价传导/锁价/套保条款，未知不等于没有对冲。"
      },
      "ocf_bridge": {
        "status": "unknown",
        "sources": [
          {
            "path": "output/runs/investment/2026-11-16/6ccd42d0f235450f862c98283220576f/execution/SH-688256/codex/agent/shared-evidence/sources/S3-2026-q3.excerpt.txt",
            "sha256": "583514c37efbbbf2e74010535a63b42a197dd8036a17e76a7beb680fde8cbfb4",
            "quote": "227,636,767.50",
            "as_of": "2026-10-24"
          }
        ],
        "derivation": "实际OCF可核但未有油价情景与公司采购/付款/收入和融资的有据桥；历史负单季OCF不证明油价导致硬失败。"
      }
    },
    "calculation": null
  },
  "recovery": {
    "operator": "all_of",
    "scopes": {
      "entry": [
        "VAL_INPUT_V8_20261116",
        "R8_ORDER_2026Q3",
        "R6_NVDA_20261118"
      ],
      "add": [
        "VAL_INPUT_V8_20261116",
        "R8_ORDER_2026Q3",
        "R6_NVDA_20261118",
        "R14_COST_2026Q3",
        "ADD_PLAN_20261116"
      ],
      "holding": [
        "HOLD_OCF_2026Q3",
        "HOLD_LITIGATION_20261001"
      ]
    }
  }
}
```
<!-- research-acceptance:end -->

## 8. 最终复评与待证

同日原 Codex 报告的两项报价仍未恢复。新版报告新增可逐年复算的集团经营现金流、普通股条件桥、留空原因及可改变判断的证据。取得劳动案公开法院程序或处分结果并核对请求权主体、金额、时间。检查之后公开的财报中库存消化、收入回款和设备投用，重建中性现金流路径。
