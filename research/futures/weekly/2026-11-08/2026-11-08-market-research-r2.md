# 期货市场研究 · 2026-11-08

generator=codex；AS_OF_DATE=2026-11-08（Asia/Shanghai）；public_data；full+publish。实际采用 origin/main **949d020af04ba55e68cbeacada91099cc960d104**，v3.0 / maintenance_contract=futures-maintenance/v2。有效规则指纹仍c3b3f87f039c46fda68f8d584f28d9496529a166100526c44c04cb564c879a55，canonical/helper与HEAD逐字节一致。见[基线](evidence/run-baseline.json)。本期有产业状态刷新和RB窗口标签纠错，没有方法变更。

## 1. 输入、采纳及覆盖

按类型resolve实际main采纳：execution-audit接11/01审计r6；market-research --before接严格前期11/01市场r6；decision亦r6。确切handoff hash为8cd99398fc3e9d9294e558cf24c26cf752fe4c017ebec1929d0e2922f52c92ec，published检查通过。已从本期实际main工作区幂等收录该确切handoff与原锚，entry2bff2889f1ae1c9252bda4976464c2eada443b7a0f4778d06c45f042b42a8018；共享收录仍是local，不代替Git发布。随后collect13条、16组纠错、1个M原登记冲突；requires_plan_reassessment/requires_method_reassessment均空。逐项处理review_scope/纠错和冲突，见[裁决r2](evidence/continuity-reconciliation-r2.json)、[来源图r2](evidence/continuity-catalog-r2.json)。相同报告的不同捕获范围不算独立产业证据。本周没有新增日频采纳，不能声称覆盖11/02–06每次信号。

本次进程**没有继承TUSHARE_TOKEN**。授权的两次隔离fetch均在认证前exit1，未取得本期完整快照/API返回，原始失败和partial保留。[失败凭证](evidence/fetch-failures/collector-1.log)。随后显式传collect的plans/anchors及11/01已发布原料复算，入口以source_fetched_before_completed_session_cutoff拒绝当前T评估；[刷新r4](../../refresh/2026-11-08/2026-11-08-signal-refresh-r4.json)仅对r3来源指针作同hash持久化修订，计算与evaluated_at未变。五T unknown/incomplete；V缺事前锚not_evaluated，当前两腿原料未更新另列。**no_signal本期没有被验证**。最后已知完整行情仅10/30，不冒称本期最新，handoff的market_as_of_date沿此历史锚，不表示本周价格覆盖。

## 2. 所有已知存量先复核

|原机会|原时钟与入场处置|若存在真实持仓的条件管理|
|---|---|---|
|20261011-observe-MA2701-trend-long-v3|10/09信号、10/11 18:14:54登记、10/13截止，expired|参考3338/SL3139在10/19条件穿越；原带所有初始SL最迟10/20穿越。10/12真实入场的11/06时间上限已经过；10/13入场的原上限11/09尚余，均以更早SL/证伪优先，反弹不复活。实际成交/退出未知|
|20261015-observe-M2701-trend-short-v3|10/15信号、19:30:56补登记、10/19截止；10/16越带取消，cancelled_and_expired|原无完整数值执行案，3310/3410只历史诊断。M原登记null/r2冲突显式裁决，不能丢M或采用更晚截止；实仓按实际Entry/SL/事件管理|
|20261025-observe-RB2701-trend-short-v3|10/23信号、10/25 01:06:50.045735登记、10/27截止，expired|原3047/SL3103；若10/26入场，旧路径参考下场SL3099再3096只收紧。11/06公开单日high3059低于该历史参考，但不证明全周未穿或真实未退出；新10日路径缺失不能重算。11/20或11/23仅原实际入场日条件上限|

本期发现11/01已采纳r6审计结构化RB entry_window_state仍为remaining_window，与原valid_until10/27及原正文expired矛盾；撤回该标签，当前改expired，G3仍fail，不改原计划/ID/登记/期限。MA标签原已expired，无同类错漏。入场到期不等于持仓已退出；所有账户、实际有效SL、持仓/挂单、退出价格和盈亏null。MA跨周末单仓、提保/事件后的压力仍按canonical，缺当前路径明确不能证明已受保护。

## 3. PRICE_SCREEN与DATA_FEASIBILITY

|合约|最后已知完整行情（历史）|本期T结果|必要原料与状态|
|---|---|---|---|
|MA2701|10/30 close3480|unknown / incomplete|当前61日OHLC/日期/来源未取得，temporary_gap|
|RB2701|10/30 close3030|unknown / incomplete|同上；11/06公开O3042/H3059/L3030/C3038仅单日辅助，不代替61日|
|M2701|10/30 close3183|unknown / incomplete|当前61日OHLC/日期/来源未取得，temporary_gap|
|SR2701|10/30 close5263|unknown / incomplete|同上|
|CF2701|10/30 close15315|unknown / incomplete|同上；网页CF701未明close/settle不采用|

上期五T对10/30仅该根no_signal，不能搬到本期。原10/27 MA多、M/SR/CF空的10/28–29窗口已过；10/29 M空原10/30/11/02窗，10/30已失突破侧/越带取消，不等回价复活，本周未补历史ID/成交。

V当前精确有序对为MA2701–MA2705、RB2701–RB2703、SR2701–SR2705；准备对MA2705–MA2709、RB2703–RB2705。逐对当前两腿来源/settle/日历尚未更新，旧61期完整或MA准备远腿缺33日均只是10/30历史状态，不能声称本期完整。无有效事前数值经济锚，所以价格确认not_evaluated；两腿认证缺口temporary_gap与经济模型research_only分别登记。没有反向拼腿、事后建锚或用历史分位充经济区间。

## 4. PRODUCT_DRIVERS与本周可比变化

|品种|主因/周期与支持|最强反证和本周变化|当前用途|
|---|---|---|---|
|M|高压榨/供应与库存压力，Mysteel11/06公开分析正文报告10/30全样本粕库存138.94万吨；11/03大地正文约3120现货、周-50提供偏弱证据，观察期/地区按底稿|库存是10/30观测而非11/06实时；国庆后109.08→138.94是原文阶段比较，不是本周环比，不与旧109.60不明样本硬拼。低价采购/基差及可能压榨下降为反证；11/12月到港预测不当已发生|重点双向T公共研究，最低方向因果为高压榨→供给/库存压力；当前价格未知不能新成案|
|RB|新华社11/05转Mysteel：螺纹产185.90周+4.72、表需残差200.80周-5.27、总库482.37周-14.90万吨|上期181.18/206.07/497.27；本周供增需降、去库减速，厂库147.39周+0.15，社库334.98周-15.05；仍去库是空头反证。表需残差非终端成交|旧空叙事反证较上期缓和但未消失；只核当前经济事实，不推实际仓位/收益|
|MA|11/04隆众原站港口41.27万吨周+5.89，外轮卸入11.23、江苏提货一般，近端需求弱与到货带来累库|上期港库35.38去1，本期转累；宁证11/06生产企业库31.08周-1.42、开工88.45周-0.41pct为反证，样本不同不与旧76.33硬比|旧多G2 pass撤回不恢复；低绝对港库仍是新空反证|
|SR|沐甜11/06云南累计2家实际开榨，较上期准备阶段推进；广西780–810万吨为预测而非实产|广糖11/05陈糖清库、南宁仓库11/06仍5170与10/30持平，削弱单纯陈糖压货解释|新糖交付/清库衔接研究；不能按开榨季节直接给空方向许可|
|CF|隆众11/05公开周评10/30–11/05终端需求未明显改善、纱发货慢/库存压力|11/06 CC3128B16889日+111，而C32S23021日-11，现货/成本支撑是空头反证；完整公检加工新值未得|原弱纺需背景未获解除，但当前T未知，不拿缺少原表的摘要做信号|

完整发布/观测日、单位、地域、样本与支持/反证见[M/RB底稿](evidence/m-rb/research-note.md)和[其余底稿](evidence/other-products/research-note.md)。Mysteel若web411后同网址HTTP200才采公开正文；AI摘要、付费表/打开失败不当已核。每个必要缺指标最多两源，增强缺失不扩大为全池冻结。

## 5. 新机会与V观察锚维护

M/RB完成产业深入，未取得当前完整价格信号，不注册新数值执行案，也不为数量制造第二机会。旧机会风险复核全部完成至现有证据边界；缺本周路径/账户，不声称已经逐日验证止损或平仓。

三V正式[锚维护](../../anchors/2026-11-08/2026-11-08-anchors-r2.json)保留anchors=[]、withdrawals=[]：共享无既有有效锚待撤；空表不等于隐式撤回。MA历史官方2元/吨日及非通用仓单5/11注销，RB0.15元/吨日与90/180日仓单/生产期限，SR经纪商0.5元/吨日及年度仓单规则均重新读，不能证明2027逐库现价/可实现性。假设120日MA240/SR60、RB60日9仅仓储，不含融资税费/库点/真实跨月交割路线；单侧成本不能造对称区间。MA累库、RB供需、SR开榨提供机制研究入口，尚无独立数值转换及5–20日修复证据。11/13按实际到港/提货、交割批次与融资、开榨产销分别复核，新冻结只供未来信号，保留原时钟。

## 6. 公开规则、事件与日历

USDA原官网再次核WASDE11/10 12:00 ET，zoneinfo换算11/11 01:00北京时间。M进口供给/成本路径相关；两份DCE官方场次原件未完整取得，首次国内场次/国内T保持null，11/11 09仅常规条件推算，不能据此宣布实际T±1已核或自动冻结RB。实仓若存在须先做事件压力预案，不能承受则按canonical减/退。见M/RB底稿与时区换算凭证。

海证11/05结算公开表MA2612–2701交易所9%/公司14%，M/RB7%、CF7%、SR6%的交易所列与公司列分开；国联11/06发布的11/09表MA701公司15%等并非用户实收。MA702/703不同日期临时提保不能套MA701或认为冲突；最新逐合约动态板幅和实收仍核。甲醇官方细则已核常规夜盘21–23及日盘，但临时安排未穷尽。郑商2026休市通知可信全文转引未列11月法定休市，不能当成全所全场次已核。旧计划日历与本轮T主合约名单独立；r4原窗计算来自历史真实SSE日期代理，不是普通工作日推算。MA2027第10交易日规则已读，01/14 vs01/15精确到期冲突因2027官方日历未得仍保留，不选更晚值放宽期限。

## 7. 下一复核与结构化CURRENT_META_RESULT

1. 恢复本期运行环境继承凭据后另存修订，核完整快照/实际行情日、五T返回身份、每组V同对两腿和真实日历；当前取数失败、陈旧、未评估和no_signal严格分列。
2. 若存在MA/M/RB实际持仓，优先核有效SL/真实Entry/成交退出/全部挂单与权益；MA11/06已过、11/09条件末限以及更早止损，M相关事件和RB反证逐项管理，final_lots仍null。
3. 11/13推进三V月份可实现交割/费用/收敛及DCE首次场次；不能采购缺口转嫁为全池必填。

PRICE_SCREEN=上表（当前五T unknown）；PRODUCT_DRIVERS=品种表；MAIN_CONTRADICTION=品种分化；DOMINANT_TRADE_DRIVERS=M供应库存压力、RB供增需降仍去库、MA到货累库/低绝对库、SR开榨/清库、CF弱纱需/现货支撑。KEY_CONSTRAINTS=当前原料未得、原窗过期取消、V数值机制、真实报价/账户/场次。PRIORITY_MECHANISMS=M/RB双向T，V未来经济研究。FRAGILE_TRADE_NARRATIVE=减产去库等于需求强、现货涨跌等于完整趋势信号；TOP_MISTAKE_TO_AVOID=旧行情当本期no_signal或重启旧窗口。PRECHECK_ITEMS=上述三项。DATA_FEASIBILITY=五T及本期V原料temporary_gap；三V经济区间research_only；公开产业证据available但各观察期时滞独立。EVIDENCE_CORRECTIONS=RB旧窗口标签remaining_window→expired（原G3/时钟不变），继承全部历史撤回。状态刷新yes、纠错yes、方法变更no；收益/交易许可未验证。

本修订r2仅完善持久来源引用及历史行情身份字段：handoff v2要求ISO行情锚，故snapshot.market_trade_date=2026-10-30、market_captured_at为11/01原包抓取时刻，仅表示实际用来做陈旧拒绝/旧窗核验的历史原料；current_market_trade_date/current_market_captured_at仍null。无当前原料的筛选记录trade_date亦仅历史输入锚，basis明确current_not_evaluated，信号unknown、当前价null；不表示本期最新。原稿保留，产业/原计划/三类结论均不变。

实际公共原文、HTTP回执、失败和partial、全部共享来源及初稿原件由[总证据清单](evidence/source-manifest.json)逐hash冻结，回执原字节opaque保存，不依赖失效缓存；锚r2只修来源引用，经济事实和原冻结时点不变。
