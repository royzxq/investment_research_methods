# 2026-10-11 期货元框架变化检测结果

## 0. 上期预备观察项复核

以下逐项核10/03变化报告与审计的下一轮观察，**“触发”只指预设检查点出现，不等于策略开仓信号**。结果按本期可读原文与快照登记；市场新变化、证据修复和未触发条件分开。

| 上期预设/观察 | 本期核验 | 性质与下层处置 |
|---|---|---|
| ①补新行情快照以判MA #30、D8、SC结算周涨、A分位与影子 | **已触发/完成**：10/10完整快照，行情10/09；MA #30两次命中、D8多头否决、SC>5%未>8%；§5旧影子仍not_filled | 数据修复＋当期市场脉冲；更新读数，不能把旧“无快照”延续，也不能据影子算机会成本 |
| ②海峡官方缓和与SC back同向回落 | **未触发**：可读报道显示谈判/政策立场并存，未见官方全面重开；SC固定对10/09仍back +22.9，5td−23.7 | ①既有“中断证真”与#26拦截不因单边收窄解除；geopolitical_fade仍research_only |
| ③10/08恢复交易、提保条件/OPEC+/10/07纪要 | **部分触发**：10/08实际恢复；OPEC+10/04维持11月目标已落地；美联储9月纪要10/07发布。各品种提保实际回落条件及经纪商保证金未齐 | 到期事件状态更新＋交易所条件继续核；OPEC配额不是油流恢复，不能改① |
| ④焦炭第二轮提降与Mysteel同系列库存 | **部分触发**：10/09第二轮仅发起/预期，未核落地；五大材总库存10/07周+85.50，对9/30周−19.03由去库转节后累库，但原站只见AI摘要及假期效应 | 新市场观察；D14对依赖该假设的具体计划成案后才判，不直接开RB单边 |
| ⑤MA domestic_public做空结案复活三项＋冻结v1 | **未触发/结案维持**：国内装置复产数值化、到港回升、太仓/江苏同口径基差走弱未获确证；v1逐日S/H20仍缺。仓单−182与港库转引日冲突不能重启 | 既有路线fail与模型temporary_gap并存；补数只解除数据缺口，不自动解除产业结案 |
| ⑥10月CPI/PPI/FOMC与D13复归档 | **日期已核，事件未发生**：CPI10/14 ET、PPI10/15 ET、FOMC10/28 ET；9月加息仍有效，后续逐会承诺无依据；美元周度承压与FOMC按兵条件尚未共证 | 日历/归因纠错；D13参数不降，AU仍信号席 |
| ⑦②''政策结构与2万亿成交额 | **未证触发**；本期没有能将其升级为池内许可的完整同口径证据 | 池外背景/研究观察，不进本期执行分母 |
| ⑧SR月产销与CF秋季B | SR-summer **已失效（2026窗口结束）**；CF窗口仍在，但B-HISTORY、窗前低点与独立需求支持缺 | SR B no_signal；CF B temporary_gap。旧8月糖读数不当本期事实 |
| ⑨光伏产能政策、⑩LC同系列库存 | **无可触发当前许可的已核新证** | 均research_only/池外扫描，不扩执行池或制造缺口 |
| ⑪旧框架更新PR#38 | **未合并，仍OPEN/CONFLICTING** | 不继承拟议v2.28/v1.17；本期若更新，以独立10/11证据作light提案 |

## 1. 基本信息

- 调研时点：2026-10-11，Asia/Shanghai；最近已完成行情日2026-10-09。
- 对比对象：本期 [`2026-10-11-market-research.md`](2026-10-11-market-research.md) vs 严格轨道上期 `research/futures/weekly/2026-10-03/2026-10-03-market-research.md`，并复核上期同日变化检测、执行审计。
- 生效框架：`framework/futures_framework.md` canonical **v2.27**，主线基线 `379d34ac6e802e7e328cb06775ed1c0a05d0e725`；compact v2.27、数据脚本v1.16。旧PR #38拟议v2.28/v1.17 **OPEN/CONFLICTING、未合并**，不能继承为本期生效规则。本报告仅做变化判定，后续拟议更新须是10/11独立提案。
- 快照：严格路径发现最新有效**已提交** `research/futures/snapshots/2026-10-10-data-snapshot.txt`，头 `AS_OF=20261010`、v2.27/v1.16，末尾有“快照完成”；SHA256 `dd8699ec302663cf63b6c700b96bfb2443942a7d27a8ffd9598082115c82f26a`，行情各锚至10/09，含§2d D8与§5影子结算。快照未给含时区采集时间，`market_captured_at=null`。本阶段未运行行情脚本。§0b零已配置节点不代表官方事件为零。
- 研究范围：MA当前A国内路线与D/E适用性、RB当前A、SR当前A筛选、CF秋季B；MA/RB准备对独立验收。MA缓和因果fade与M无许可独立策略维持`research_only`，AU/SC仅信号席。SR-summer已过2026窗口。账户/全候选账缺失，不能推空仓、零风险或零总体机会。

本期先拆分三类变化：**（a）市场事实**：MA连续脉冲、RB五大材节后由去库转累库、SC近端back收窄但仍正；**（b）证据修复**：旧“最新9/19”发现错误、旧日历与“逐会连续加息指引”归因不成立；**（c）可得性**：10/10快照令D8/#30/SC结算护栏可判，但MA冻结v1逐日确认、CF B历史/窗前低点、计划与账户仍缺。三者不得互相计成“市场结构改变”。

## 2. 总结论

- 是否需要更新期货执行框架：**是**。
- 更新级别：**仅需轻微更新（light）**。更新对象是框架中的当期状态、事件日历、证据有效性与脚本EVENTS配置；既有模型许可、阈值、评分权重和风险上限均无新证据支持变更。
- 结论理由：v2.27仍把国庆期写作10/1–10/8并以10/9为首个响应日，且若干状态行停在9/19；本期完整快照已显示MA D8多头否决、#30两次命中、SC结算周涨>5%（未>8%）、RB A首次进入研究筛选、MA准备对仍缺验收。BLS和Fed官方10月日历已确认；[美联储9/16声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm)证实9月加息25bp至3.75–4.00%，[Waller 10/8原文](https://www.federalreserve.gov/newsevents/speech/waller20261008a.htm)明确后续加息不必连续会议。旧“逐会承诺”不能继续挂在fed_state；D13现行扣减与复归档条件仍应保留，未据一场讲话下调护栏。
- 若不更新：事件T与提保复核可能按错误日期执行，MA方向性脉冲护栏和RB新研究筛选仍显示旧读数，未核港库或自动摘要可能被误写为产业硬门；旧PR拟议状态会与main实际方法混淆。

## 3. 新旧对比总览

| 变量 | 10/03上期结果（按原文，不沿用过期事实） | 10/11本期结果（以本期元研究及原始证据为准） | 变化级别 | 是否重要 |
|---|---|---|---|---|
| `MAIN_CONTRADICTION` | 国庆闭市期外盘重定价、10/08复盘多重落地；旧报告因无覆盖9/30的新行情而护栏unknown | MA近端交割供给偏紧迹象与RB节后五大材累库线索并存，持续性及定价因果待核；MA高分位继续走阔且单边结算脉冲已核 | 重要市场变化＋证据修复 | 是，改变筛选与风控输入 |
| `DOMINANT_TRADE_DRIVERS` | 海峡袭船/俄禁令、外盘与利率重估主导；OPEC+及纪要待落地 | 仓单减少与五大材假期累库是不同对象的供需线索；OPEC+维持11月目标已落地，SC back仍+22.9但5td−23.7；Fed后续节奏不固定 | 重要状态变化，部分旧归因纠错 | 是，更新事件与fed_state记录 |
| `KEY_CONSTRAINTS` | 快照滞后，D8/#30/SC结算周涨等unknown；10/08提保/事件复盘 | 快照可核：MA D8上尾99.4、10/08/09 #30+7.26%/+5.50%、SC结算周涨+6.49332%、MA ATR分位94.8；账户与结构计划仍unknown | 重要证据可得性变化 | 是，硬门由unknown转实测，不改门槛 |
| `PRIORITY_MECHANISMS` | 事件与供需拐点高、波动切换防御，期限结构低偏中（无新快照） | 事件与波动仍高（风险纪律），A期限结构为首要结构**研究**：MA100分位但未回归确认，RB77.2入筛选 | 轻微排序变化 | 是，更新研究次序但不增许可 |
| `FRAGILE_TRADE_NARRATIVE` | 美方反提案＝海峡将重开、加息概率下降＝金见底；MA高分位必回归 | 谈判/SC 5td收窄≠官方重开；仓单减少、港库转引日冲突，MA高分位≠做空信号；节日钢材累库≠RB单边空头许可 | 重要表达变化 | 是，防错误因果与绕门 |
| `TOP_MISTAKE_TO_AVOID` | 10/08复盘日用外盘/媒体日内涨幅追方向，或沿用9/18护栏读数 | 10/09结算数据已出：不能把筛选分位直接下单，也不能忽略已核D8/#30/SC>5%或把方向性护栏移植给完整A配对 | 重要执行焦点变化 | 是，硬门适用性及实际数值已变 |
| `PRECHECK_ITEMS` | 补跑快照；核10/08交易所回落、OPEC+/纪要、港库及RB库存 | 快照完成；转为MA冻结v1逐日S/H20计算、RB前瞻确认所需逐日序列/成本、产业原表与假期效应、真实交易所保证金及官方CPI/PPI/FOMC T、账户 | 重要待办状态变化 | 是，不能重复要求已提交快照 |

上期`DATA_FEASIBILITY`各候选缺快照不再机械延续；10/10快照改变有证据的项，缺口按模型最低输入逐项保留。上期`EVIDENCE_CORRECTIONS`已核历史文件中的年/口径错误继续被排除，不能因新周到来重新作为证据。

## 4. 重要变化项与交易含义

### 变化项1：MA方向性硬门由unknown转为已核命中

- 旧值：10/03报告对MA2701 #30、MA主力D8与SC周结算护栏记unknown；9/28媒体日内涨幅只作线索。
- 新值：10/10快照§2b.1给MA2701 10/08和10/09 `settle/pre_settle` +7.26%、+5.50%，即原框架#30顺向3交易日冷却；§2d给MA2611主力周涨+14.86%、上尾99.4（商品多头D8否决）；SC2611两端结算696.10→741.30、周涨+6.49332%，只命中>5%层而未命中>8%冻结；MA ATR分位94.8使方向性D12升档。[完整快照](../../snapshots/2026-10-10-data-snapshot.txt)
- 变化方向/级别：证据修复＋市场脉冲，重要；不能把“unknown→fail”解释为规则新增。
- 交易含义：MA方向性多头至少D8与#30已核否决，SC>5%按原加仓/存量处置，不夸大到>8%；方向性空头仍须#26两要件与自身D信号。**完整1:1 A配对豁免D8/#30/D12/#16**；意外裸腿另按单边事故管理。低敞口#16是否本期继续命中要按最新事件密度、国内交易日和交易所实际恢复核，不从9/19状态沿用。
- 下层影响：刷新MA卡、0.1/0.2、2.3、D8/D12当期行、6.8；不修改#30/D8/SC阈值。

### 变化项2：RB A进入研究筛选，库存由节前去化转假期累库

- 旧值：10/03因无新快照，沿用9/18 RB2701−RB2703分位56.1仅为旧背景；Mysteel9/30五大材总库存1462.94万吨、周−19.03。
- 新值：10/09固定对S+2元/吨、同期分位77.2、1td−2/5td+11、三年各41/41，双腿量通过已打印的初筛；[Mysteel10/07原站公开AI摘要](https://gc.mysteel.com/a/26100715/8D43767F25CBE5B3.html)列五大材总库存1548.44万吨、周+85.50与螺纹产量170.27万吨、周−1.96。该总库存不是螺纹单品种，底层表未读，且跨国庆假期；10/09“137家螺纹库存596.84”仅搜索摘要、未读正文，不入硬判。
- 变化方向/级别：A筛选由未触发旧读数转入候选，重要；五大材周库存由负转正为新观察期市场变化，节日效应限制外推。
- 交易含义：RB A优先完成独立国内逻辑与前瞻价格确认；分位不是触发。D14只在明确依赖库存/复产/收缩成本的**具体计划**中评估，当前未成案不预扣−0.5或写已核失败；RB方向性空头没有由库存数据新获许可。
- 下层影响：RB卡、1.4黑色周度行、6.8研究清单；若提出确认版本，只能在定义时间后生效。

### 变化项3：快照、日历与Fed归因纠错

- 旧值：10/03报告称“最新已提交快照9/19、连续第二周无新快照”；canonical仍写国庆10/1–10/8、10/9首个响应日，脚本§0b配置空；canonical D13等把“9月加息落地＋连续加息指引”连写。
- 新值：严格已提交路径发现10/03时还有9/21快照（但其行情仍不足以覆盖当时9/30），本期最新为10/10完整快照；真实国庆10/1–10/7休市、10/08恢复，10/09为第二交易日。BLS官方日历：[CPI 10/14 08:30 ET、PPI 10/15 08:30 ET](https://www.bls.gov/schedule/2026/home.htm)，有夜盘品种的国内T分别为10/15、10/16；[Fed官方10月日历](https://www.federalreserve.gov/newsevents/2026-october.htm)给10/28 14:00 ET决议、北京时间10/29 02:00，国内T=10/29。美联储9/16声明确认已加息；10/08 Waller个人讲话反对把后续加息写成逐会固定承诺。10/09 WASDE为美国当地发布日，国内首个可能响应10/12，未核报告正文数字不入M模型。
- 变化方向/级别：历史证据纠错与日历到期，重要执行输入；Fed当前路径不确定属状态更新。旧PR #38未合并，拟议改写不视为已落地。
- 交易含义：0.0b按官方发布时间与实际国内交易日重新排T−n；D13的9月已加息事实与现行扣减、复归档硬条件保留，撤回“委员会承诺连续会议加息”的归因，也不凭一位官员讲话预判10月最终决议。AU仅信号席；不降交易门。
- 下层影响：0.0b/1.4/0.1、fed_state/D13状态与AU卡、脚本EVENTS、6.1/6.8；主要为当期事实修复。

### 变化项4：MA A/准备对的数据分层与产业证据边界

- 旧值：MA当前对上期因无覆盖9/30行情而全部筛选与冻结v1观测unknown；国内路线已做空论证结案，上期港库不同统计对象相互冲突；准备对历史样本不足。
- 新值：当前MA2701−MA2705价差+416、分位100、1/5/10td+88/+172/+86、三年各41/41，双腿量可核；但现有§1输出未给冻结v1所需连续两日S、前10日S最高与两日H20，**具体执行模型`temporary_gap`**。上期domestic_public做空路线结案继续有效：复活须国内装置复产数值化、到港回升、太仓/江苏同口径基差走弱至少一项被观测，并有冻结v1价格确认；本期上述条件未被证实。10/09郑商所MA仓单[公开完整转录](https://www.99qh.com/article/%E9%86%87%E7%B1%BB-1101000)总5316张、当日−182，只代表可交割供给，注销/交割机制未排除。[隆众港库原始页](https://www.oilchem.net/26-1008-13-764c0881785292b9.html)未读到正文，机构转引30.51万吨/周−8.84但观测日10/07或10/08冲突，`conflicting/optional_context`，不得作#5已核pass/fail。准备对MA2705−MA2709虽分位100，两年31/41低于33/41、MA2709远腿20日量缺，仍`temporary_gap`。
- 变化方向/级别：当前对筛选数据可得但确认仍缺；准备对缺口由旧背景转为本期精确实测；产业转引质量受限。重要的是**不能把100分位直接做空**，不是新增禁令。
- 下层影响：MA卡分清研究筛选/既有国内路线结案/冻结确认/产业支持/计划；准备对逐对验收，不继承当前对分位；补数后按旧v1前瞻评价，不重置机会时钟。

## 5. 是否触发执行框架更新

- 判断：**yes / light**。旧PR未合并，main的过期日历和状态卡需要以本期已核事实重新整理；研究排序及候选状态换版，但不新增普遍交易门槛。
- 依据：上面4项；阶段②独立审计 [`2026-10-11-execution-audit.md`](2026-10-11-execution-audit.md) 的覆盖为`partial`，它已按v2.27单独校验。审计没有完整账户/候选账，故机会成本无法估算，不能用护栏命中次数或空仓推收益结论。
- 主要限制：MA港库观测日冲突、Mysteel底层表未读、RB价格确认阈值不能仅由端点数据设定、CF B历史/窗前低点未组装、账户未知。这些是模型/执行缺口，不构成放松风险上限的理由。

## 6. 本次执行框架更新重点

1. **修正过期日历与事实状态**：10/08首个响应/交易所条件回落，CPI/PPI/FOMC的ET发布时间和国内T；OPEC+目标按兵已落地；脚本EVENTS同步。保留“官方事件时点与国内可交易日分别记录”原逻辑。
2. **更新现行卡片读数和适用性**：MA D8/#30/SC>5%/D12新实测、①反向要件及MA A筛选与冻结v1缺口；RB A77.2筛选、同源库存由去库转假期累库但D14只对成案计划适用；MA准备对独立样本/成交缺。A完整配对的D8/#30/D12/#16豁免、#5独立产业证据与真实双腿风险均保持。
3. **清除无依据的宏观与产业归因**：9月加息事实保留，连续会议加息承诺撤回，D13参数与复归档硬条件保持；港库转引冲突和Mysteel AI摘要质量显式标注；旧PR #38内容只作为未合并历史，不复制为本期生效版本。

不因SC 5td收窄开放fade/能源空头，不因MA高分位开放逆势A；不因五大材累库开放RB单边空头，不因Waller讲话复归档D13，不因账户缺失写0风险。

## 7. 输出给下一步使用的结构化结果

```yaml
FRAMEWORK_UPDATE_DECISION:
  update_needed: yes
  update_level: light
  decision_reason: "本期实测令MA D8/#30/SC结算护栏与RB A筛选可判；main v2.27日历和状态行过期，Fed逐会加息归因无官方依据。仅更新当期证据、适用性及事件配置，不改阈值/许可/预算。"

KEY_VARIABLE_CHANGES:
  - variable_name: "MA方向性结算护栏"
    old_value: "10/03判定腿#30、D8和SC结算周涨unknown（无覆盖9/30行情的快照）"
    new_value: "10/09快照：MA2701 10/08+7.26%、10/09+5.50%；MA2611 D8上尾99.4；SC2611两端settle周涨+6.49332%；MA ATR分位94.8"
    change_direction: "unknown转实测命中；>5%命中而>8%未命中"
    change_type: "行情变化与证据可得性，非规则新增"
    importance_level: "高"
    trading_meaning: "MA方向性多头D8/#30拦截；SC>5%加仓/存量护栏；D12方向性升档；完整A配对豁免"
    downstream_impact: "MA卡、D8/D12/2.3当期行、0.1/0.2、6.8"
  - variable_name: "RB A研究筛选及五大材库存"
    old_value: "上期仅有9/18分位56.1的过期背景；9/30五大材总库存1462.94万吨、周−19.03"
    new_value: "10/09固定对分位77.2、S+2；Mysteel10/07公开AI摘要五大材总库存1548.44万吨、周+85.50，螺纹产量170.27万吨、周−1.96"
    change_direction: "进入A研究候选；总库存转为假期累库"
    change_type: "新观察期市场变化，底层表及季节性待核"
    importance_level: "中高"
    trading_meaning: "研究结构确认和国内独立逻辑；D14成案后按依赖假设判，不开放RB单边"
    downstream_impact: "RB卡、1.4黑色状态、6.8"
  - variable_name: "日历、Fed归因及证据版本"
    old_value: "main写10/1–10/8休市、10/9首响应；10/03误称最新9/19；D13连写‘连续加息指引’；旧PR#38拟议未合并"
    new_value: "10/1–10/7休市、10/08首响应；最新10/10完整快照；9月+25bp有效但Waller10/08明确后续加息可非连续；官方CPI/PPI/FOMC日历已核"
    change_direction: "纠错和到期换版"
    change_type: "证据修复/日历重核，单独于市场变化"
    importance_level: "高"
    trading_meaning: "重排0.0b T−n，防旧读数与未合并拟议版本污染决策；D13参数不变"
    downstream_impact: "0.0b/1.4/0.1、fed_state/D13/AU卡、脚本EVENTS"
  - variable_name: "MA A冻结v1与准备对数据可得性"
    old_value: "上期当前对因行情滞后temporary_gap；准备对旧样本/成交缺"
    new_value: "当前对筛选100分位/3年完整，但既有国内做空路线结案未解除、v1逐日确认观测仍缺；准备对两年31/41且远腿量缺；港库转引观测日冲突"
    change_direction: "筛选数据恢复，既有国内路线结案未解除，具体模型与准备对仍temporary_gap"
    change_type: "数据可得性边界细化"
    importance_level: "中"
    trading_meaning: "只在研究层观察，不从极端分位逆推确认/SL/TP"
    downstream_impact: "MA卡、0D缺口、6.8"

EVIDENCE_CORRECTIONS:
  - original_claim: "10/03：最新已提交快照9/19，连续第二周无新快照"
    correction_basis: "严格路径发现10/03时已有9/21已提交快照；本期新增10/10完整快照（SHA256见§1），行情到10/09"
    affected_decisions: ["本期A筛选", "MA D8/#30/SC周结算/D12", "§5影子结算", "旧数据待办"]
    reassessment_result: "旧发现断言撤回；9/21在10/03仍不能覆盖9/30行情，不自动反转旧市场判定；本期硬门按10/10快照重评，影子仍not_filled。"
  - original_claim: "canonical：国庆10/1–10/8休市、10/9复盘/首个响应"
    correction_basis: "上期已核交易所安排为10/1–10/7休市、10/08恢复；本期10/08、10/09快照实际行情再次印证；旧PR#38未合并"
    affected_decisions: ["0.0b事件T与±1", "1.4假期/提保", "低敞口复核日", "脚本EVENTS"]
    reassessment_result: "按10/08首交易日、10/09第二交易日重排；交易所实际提保恢复仍须满足各自条件，不宣称自动回落。"
  - original_claim: "canonical D13/fed_state的‘9月加息落地＋连续加息指引’被读成委员会承诺逐会加息"
    correction_basis: "Fed 9/16声明确认+25bp至3.75–4.00%，但未承诺后续逐会节奏；Waller 10/08个人原文明确加息不必连续会议"
    affected_decisions: ["fed_state标签", "D13状态解释", "AU信号卡", "10月情景"]
    reassessment_result: "保留9月加息历史事实，撤回逐会承诺归因；当前后续次数/节奏不确定。D13扣减、×0.5、复归档硬条件与AU信号席维持，10月结果未发生。"
  - original_claim: "旧港库不同对象冲突或本期30.51万吨转引可直接作MA #5已核门"
    correction_basis: "隆众原表不可读，机构转引观测日分别10/07/10/08；郑商所仓单5316张属不同可交割对象，不能与港库互换"
    affected_decisions: ["MA A #5/D2", "国内路线复活条件", "MA卡库存行"]
    reassessment_result: "港库标conflicting/optional_context；仓单仅限可交割供给事实。MA A #5仍unknown，不能用该争议读数判pass/fail。"

DATA_FEASIBILITY:
  - scope: "MA2701-MA2705 A domestic_public当前对"
    data_feasibility: temporary_gap
    missing_required_inputs: ["冻结A-MA-2701-2705-v1的逐日S、前10日S最高与两日近腿H20观测", "方向性独立国内论证及真实Entry/SL/TP/成本"]
    unavailable_enhancements: ["隆众港库原表/统一观测日；船流/战争险非普遍必填"]
    scope_change: "研究筛选/流动性/历史样本恢复available；既有国内做空路线结案未解除，具体冻结确认模型仍temporary_gap"
    recovery_condition: "从原始行情补算已冻结v1，并核国内复产数值化/到港回升/太仓江苏同口径基差走弱至少一项；两条件满足才重评旧结案，不改旧定义生效日"
  - scope: "MA2705-MA2709 A准备对"
    data_feasibility: temporary_gap
    missing_required_inputs: ["后两年同期样本31/41<33/41", "MA2709远腿20日均成交缺(<20有效样本)"]
    unavailable_enhancements: []
    scope_change: "继续独立验收，不继承当前对"
    recovery_condition: "逐年样本≥33/41×3且远腿量达到#2可核"
  - scope: "RB2701-RB2703 A domestic_public"
    data_feasibility: available
    missing_required_inputs: ["完整连续日S与交易成本供前瞻确认数值选取", "具体方向/价格确认/Entry/SL/TP/净R"]
    unavailable_enhancements: ["Mysteel底层螺纹原表或下一完整周同系列；铁水/盈利率参考级"]
    scope_change: "分位77.2进入研究筛选；未到交易信号"
    recovery_condition: "research/data_pipeline以连续日序列和独立事实成案后冻结确认版本与生效时间"
  - scope: "SR2701-SR2705 A、RB2703-RB2705准备对、SR-summer B"
    data_feasibility: available
    missing_required_inputs: []
    unavailable_enhancements: []
    scope_change: "分别因分位0.0、52.0和季节窗口已结束，当前直接no_signal"
    recovery_condition: "新观察期重新筛选；SR-summer到2027窗口按真实日历再评"
  - scope: "MA2701 D/E方向性"
    data_feasibility: available
    missing_required_inputs: ["自身事件/价格信号及实际可执行计划", "账户/挂单/经纪商参数"]
    unavailable_enhancements: ["精确船流/战争险参考级"]
    scope_change: "D8/#30/SC结算周涨/D12由unknown转已核；空头#26按官方缓和与SC back双要件维持拦截"
    recovery_condition: "各方向独立通过现行门、事件确认、计划与账户；不能只待冷却到期"
  - scope: "CF2701 B-autumn"
    data_feasibility: temporary_gap
    missing_required_inputs: ["B-HISTORY三年同窗", "pre_window_low5与Step5-B触发", "具体Entry/SL/TP/费用/退出"]
    unavailable_enhancements: ["协会原站/原检验表；非必要专业数据不扩为全池门"]
    scope_change: "窗口仍在，不把日期当入场信号"
    recovery_condition: "研究/数据侧组装既有公式并运行seasonal_plan核验后，独立产业事实支持再成案"
  - scope: "M独立策略、MA geopolitical_fade"
    data_feasibility: research_only
    missing_required_inputs: ["M已许可策略路由", "fade官方缓和要件与SC back共证"]
    unavailable_enhancements: []
    scope_change: "维持研究观察，不进入可执行分母"
    recovery_condition: "仅按canonical既有许可与专属因果要件恢复，不用价格代理"
  - scope: "AU/SC信号席（用途限定）"
    data_feasibility: available
    missing_required_inputs: []
    unavailable_enhancements: ["SC单合约OHLC/ATR模块unknown，仅影响依赖该模块的分析；SC结算周涨与back已available"]
    scope_change: "维持信号用途，不建仓；SC2611剩14td为信号腿豁免#1"
    recovery_condition: "下次主力换月按实际挂牌合约重建SC信号对"
  - scope: "账户/挂单/经纪商参数与全候选账"
    data_feasibility: temporary_gap
    missing_required_inputs: ["当期账户净值、持仓、挂单、已用风险、适用保证金、费用与全候选记录"]
    unavailable_enhancements: []
    scope_change: "只影响执行容量与总体机会评估，不传染已取得的价格研究证据"
    recovery_condition: "当期账户来源及完整候选账核验；此前实际风险、总机会、final_lots均null"

UPDATE_FOCUS:
  - "0.0b/1.4与脚本EVENTS校正官方日期、时区、国内T及提保条件；旧PR不继承。"
  - "MA/RB卡与D8/#30/SC>5%/D12/D14本期状态、A适用豁免和数据缺口换版；新确认定义仅前瞻。"
  - "fed_state/D13/AU卡撤回逐会加息承诺归因，保留现行扣减与复归档条件。"

DO_NOT_OVERREACT_ITEMS:
  - "一次MA100分位、RB77.2或五大材假期累库不构成可执行信号，不改评分权重/模型许可/风险帽。"
  - "SC back收窄、美伊对话与港库转引不构成官方缓和证真，#26及fade路由不提前解除。"
  - "9月加息事实保留；Waller个人讲话不等于FOMC10月决定，不据此降低D13。"
  - "没有账户及完整候选账，不能用零手数、空仓或机会成本假设评估护栏收益。"

EXECUTION_AUDIT:
  path: "research/futures/weekly/2026-10-11/2026-10-11-execution-audit.md"
  framework_version: "v2.27 current_framework"
  coverage: partial
  active_scope: ["MA/RB/SR A当前对与MA/RB准备对", "MA2701 D多空", "CF/SR B窗口"]
  research_only_scope: ["M独立策略", "MA geopolitical_fade；AU/SC仅信号"]
  summary: "按原框架schema3：MA多头D8/#30实测拦截、A当前对确认缺、RB新入研究筛选、准备对缺样本与成交、CF B缺历史/计划、账户及总体机会数null；未形成新shadow。"
```
