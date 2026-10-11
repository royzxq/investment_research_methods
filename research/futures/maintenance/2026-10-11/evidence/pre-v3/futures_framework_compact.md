# 期货交易分析框架 v2.29 · 精简版

方法整理：2026-10-11；状态与行情沿用§3的既有证据。本次仅整理研究流程和重复表达，不重做市场判断、不新增交易许可、不调整风险预算。

## 0. 决策链总览

**先筛许可/触发 → 至多两条候选完成证据、确认与计划 → 固定分母评分 → 适用门与账户容量 → 持仓管理、审计及影子归因。** 本次仅改变工作顺序；完整方法见[canonical](futures_framework.md)，取证见[数据协议](FUTURES_DATA_PROTOCOL.md)。本文件自含执行规则，277个稳定ID不重编；同义锚只指向本文唯一判据。

| 日常对象 | 最短阅读路径 |
|---|---|
| MA/RB/SR的A | [当前两腿/样本](#r-dynamic-roll-table)→[≥70筛选](#r-a-screen)→[高价差做空回归](#r-a-reversion)→[确认/计划](#r-conf-definition)→[评分](#r-score-normalize)；MA先核[原复活条件](#r-dynamic-pending) |
| CF/SR的B | [窗口](#r-trigger-b-window)→[价格/历史计划](#r-plan-b)→独立产业证据；前20交易日仅准备，研究区间外no_signal |
| MA的D/E | 已落地事件/已出清叙事→[D](#r-trigger-d)/[E](#r-trigger-e)及专属冻结；缺定义列具体缺口 |
| M、AU/SC与池外 | M无具体许可，只观察；AU不交易、SC只信号；仅取本候选必要输入。C/F/G/H及池外结构见§4，不作日常菜单 |

MA/RB保持核心覆盖，M/SR/CF保留备选覆盖。已核未触发可按[AUDIT-no](#r-audit-no)早停，必要未知与已知否决分列。从已许可路线选最接近成立的至多两条：先给方向、获利机制、独立产业支持/反证，冻结自身价格确认，再给有依据的Entry/SL/TP、成本、期限和净R；不能成案就列具体原因，不凑数量。计划提供D3输入后评分，只核适用门；账户后置，研究通过而仅余账户类未知用[awaiting_account](#r-audit-awaiting)，ready前只给条件方案。

正文先交“品种/策略方向｜证据/反证｜触发｜Entry/SL/TP与净R｜最晚退出｜研究状态/执行缺项”，不适用留空说明；再附唯一schema 3底稿及至多两条事前影子记录。同机会沿用ID/确认版本；重复definition/plan/calculation缺口先完成原动作或说明不能完成的原因及到期处置，不能改称市场风险或加新门。

固定规则在§1，品种差异在§2，既有日期/读数在§3，休眠定义在§4。所有金额为人民币；先核适用性，unknown≠fail，资料可得≠研究完成，参考信息不进门。

**待裁决边界**：A≥4.0、常规隔夜≥4.2、限隔夜≥4.5的优先关系未明确；E有门槛但缺固定权重，轻仓区间也不能自行解释为许可。保留原值，不由AI选较低门槛或另加“从严”门；受影响候选明示定义缺口。其他原有歧义见相应条目。

## 1.1 池许可与路由

<a id="r-pool-core"></a>
**POOL-core**　核心池每周维护品种卡、可交易性、换月阶梯和事件轴；执行须过#1期限、#2流动性、#31真实容量及驱动与月份窗口匹配四门。退出依池规则/用户裁决；信号席不建仓。

<a id="r-pool-backup"></a>
**POOL-backup**　备选只维护可交易性与品种卡；已有许可路线获独立供需证据后升核心，首期系数0.5；不拼故事凑仓位。

<a id="r-pool-signal"></a>
**POOL-signal**　仅提供指标/门输入，不建仓；改变用途须用户另议。

<a id="r-pool-scan"></a>
**POOL-scan**　按所列复活条件周扫；独立驱动＋#1/#2＋2ATR预检有容量→先入备选，#31仍须完整计划；用户排除优先。

<a id="r-pool-sleep"></a>
**POOL-sleep**　池外模块、交易门、乘数及旧“必刷”全部休眠，只保留商品侧背景；日常不展开§4。复活须满足对应条件及池许可，不能仅因数据补齐启用。

<a id="r-route-near"></a>
**ROUTE-near**　近月只承接事件、现货及已出清叙事，不承载远月政策预期；结构除外，重分类须证据。

<a id="r-route-far"></a>
**ROUTE-far**　远月A核价差输入，F核产能性门；政策公告不加权，过对应门后评估。

<a id="r-route-structure"></a>
**ROUTE-structure**　完整两腿结构豁免横跨及单边D12/#16/#30/MA方向性护栏，仍核组合风险、费用和专属门；失配立即撤销豁免，裸腿按单边。

<a id="r-data-authority"></a>
**DATA-authority**　canonical定义规则/评分，协议管取证，schema 3模板管字段（schema 2仅旧报告），脚本只提供输入；change-analysis/adaption读canonical。0D覆盖旧全量必刷、优先级和“一字不改”指令。实测用[DATA-snapshot](#r-data-snapshot)，参考级见[DATA-reference](#r-data-reference)；旧叙事/未完成研究不证明护栏有效；数据错误立即撤回，不受反摇摆拦截。

<a id="r-pool-independent"></a>
**POOL-independent**　P/Y/OI等须独立证据及明确入池许可，不借C白名单；BU/EC不入池，未获许可不计执行候选。

## 1.2 状态与事件日历

<a id="r-cal-lookahead"></a>
**CAL-lookahead**　开/加仓前核未来10交易日真实事件清单，核实后才填“完成”；未完成不得输出开/加仓决策。

<a id="r-cal-cross"></a>
**CAL-cross**　拟持仓横跨未落地事件，写T−1对冲/减仓计划；仅许可工具，落地后复评。

<a id="r-cal-day"></a>
**CAL-day**　按节点±1及专属门核新开限制，窗口结束另核其他门；机械换月亦须核。

<a id="r-reg-trigger"></a>
**REG-trigger**　[REG-set](#r-reg-set)任一当前适用条件命中，按[RISK-regime](#r-risk-regime)封顶组合风险且只应用一次；不进入单笔乘数。池外交易门休眠；全部仍有效触发复评解除后才恢复。

<a id="r-reg-tail"></a>
**REG-tail**　地缘/权益夜盘风险涉及敏感品种，周五前用许可工具对冲/减仓，风险消失后复评。

<a id="r-reg-correlation"></a>
**REG-correlation**　再校准期且组合依赖跨资产对冲，按无相关性保护重核；样本不足不能依赖，验证完成后复评。

<a id="r-reg-exchange"></a>
**REG-exchange**　提保/限仓公告±1日，受影响品种新开门槛+0.3，公告日检视占用；窗口退出后本项解除。

<a id="r-cal-timestamp"></a>
**CAL-timestamp**　官方released_at（带时区）→北京时间→domestic_trade_date→品种首次可交易时刻，再用真实日历算T−n。周五夜盘归下一交易日，已收盘者从下一可交易时刻响应；会议首日非决议T，按品种核时段。

<a id="r-state-density"></a>
**STATE-density**　高密度簇=两周内≥2离散催化；能繁稳定<3750＋仔猪同比降；PPI归因=内生性>60%/混合/输入性>60%。只核相关模型，缺可选精确比例不猜不罚，矩阵未填不等中性/过门。

<a id="r-reg-set"></a>
**REG-set**　15项低敞口触发：①宏观T−1未对冲金融/准金融单边；②#30能源脉冲；③carry双杀；④高密度簇且当周有未落地催化；⑤政策密度高且当周≥2节点未落地；⑥流动性收缩；⑦地缘/权益夜盘跳空；⑧波动升档且T−3；⑨D14收缩证伪；⑩创新高且周涨前10%；⑪提保/限仓公告±1；⑫ATR池内极差>50且未当日重校准；⑬地缘质变当日及次日；⑭相关性再校准且依赖跨资产对冲；⑮#28重新冻结。按各源规则参数及组合封顶执行，休眠项不参与；全部有效触发经状态复评解除才恢复。

<a id="r-reg-geop"></a>
**REG-geop**　霍尔木兹停火/重开官宣、正式关闭、扩大打击、再袭船/布雷；俄乌停火、柴油禁令官方延期/扩汽油/解除、更大打击，任一质变→当日及次日方向性新开冻结并备双向跳空预案，MA结构另核±1。通行量仅参考；旧事件无新证据不续冻，当前俄禁令证据见[DYNAMIC-events](#r-dynamic-events)。窗口退出仍核其他触发，不授新方向许可。

## 1.3 资料、合约与换月

<a id="r-roll-days"></a>
**ROLL-days**　交易腿用真实trade_cal和20日均量核#1/#2；单日放量不可替代，更新时重核。

<a id="r-roll-direction"></a>
**ROLL-direction**　方向腿取阶梯中最近且剩余td≥20＋策略持仓上限的月份（D≥50td）；换月重核，信号/结构用各自规则。

<a id="r-roll-structure"></a>
**ROLL-structure**　近腿剩余<20交易日或主力换月，先到即整对退出/重建并重核全门；不另加旧“换月前15日”规则。

<a id="r-roll-plan"></a>
**ROLL-plan**　public_data优先研究5–20交易日计划，30–60日仅参考；事前固定最短/最长持有期及最晚退出日，须覆盖最短持有期并服从[ROLL-structure](#r-roll-structure)。窗口不足只否决该计划，不无依据否定全部目标或静默缩期。滚动结束原计划，新对全门重建；不加旧“换月前15日”退出条件。

<a id="r-roll-target"></a>
**ROLL-target**　目标两腿须过#2；不合格退最近可过月份并标降级。SC信号豁免#1/#2。

<a id="r-roll-timing"></a>
**ROLL-timing**　按已核阶梯日期或fut_mapping主力换月先到者执行，不等周报；信号按专门节奏。具体触发与选腿依[ROLL-direction](#r-roll-direction)/[ROLL-structure](#r-roll-structure)，不另增提前等待天数。

<a id="r-roll-reset"></a>
**ROLL-reset**　换月用新对原有历史按[INPUT-spread](#r-input-spread)验收，更新滚动阶梯/候选审计并重建方向/SL/TP/许可；不继承旧计划、不把分位设0、不额外等41天，完成计算并过全门才可评估。

<a id="r-roll-sc"></a>
**ROLL-SC**　SC信号按主力−次月滚动；近12月逐月、更远按季挂牌，不存在月取下一实际挂牌月；不建仓，豁免#1/#2。

<a id="r-pre-preview"></a>
**PRE-preview** → [0.3#31](#r-gate-31)（同义锚）。

<a id="r-input-price"></a>
**INPUT-price**　SMA、ATR-Wilder(20)、ADX-Wilder(14)、年化HV(20,60)、ATR近250日分位由行情包计算。一般研究结算缺失可标price_basis后回退close；SC周涨/MA#30指定结算不得回退。指标错误不抹有效结算端点。

<a id="r-input-spread"></a>
**INPUT-spread**　过去3年同月合约对，各年目标日±20交易日，期望41、至少33（80%向上取整）个有效唯一同日两腿样本；40/41仅警示，缺年/不足33/重复/非法日期/口径不可核→incomplete。分位用有效原值，不补值、不缩年/窗口；换月可回溯已有历史，无额外41天等待；验收不证明独立或显著。

<a id="r-input-status"></a>
**INPUT-status**　spread%≥+0.3%为B，≤−0.3%为C，其他为F；只是结构描述，非交易方向，随行情更新。

<a id="r-input-scope"></a>
**INPUT-scope**　脚本价差取MA/RB/SR与SC信号；股指/国债停用。池内采样并交叉核per_unit参数，复活先同步配置。

<a id="r-input-manual"></a>
**INPUT-manual**　最低人工研究=行情合约＋一项合适独立公开产业事实＋相关日历；可计算指标由行情包/同口径终端导出承担。库存/利润/开工/基差是菜单，非全链；强因果模型仍核必要数据，池外不日常补采。交易前另核账户、报价、费用、保证金限仓及压力。

<a id="r-input-state"></a>
**INPUT-state**　密度、能繁及PPI阈值见[STATE-density](#r-state-density)；按当期实际适用证据填值，不预填旧结论，不以缺精确归因猜数或扣分，背景缺项不冻结全池。

<a id="r-data-feasibility"></a>
**DATA-feasibility**　available/temporary_gap/research_only只描述资料/模型可得性，不等status。已有许可新对未计算、模块失败或缺列=temporary_gap；最低研究资料齐即可available，反证/未成案/账户未知不改变。必要专业资料长期不可得的模型research_only，保留排除范围/复活条件及已知阻断，不冻结全池；证据恢复后复评。

<a id="r-data-snapshot"></a>
**DATA-snapshot**　先读最新提交的research/futures/snapshots/<AS_OF>-data-snapshot.txt，记录AS_OF、脚本版和行情日。本地继承TUSHARE_TOKEN运行future_data.py，由脚本保存含stderr全文，末行“快照完成”；云端不运行。无文件/缺完成标记/行情落后应有最近完成日→受影响项temporary_gap并注明日期；已有实测不得以推算/旧值/叙事替代。

<a id="r-data-reference"></a>
**DATA-reference**　Kpler船流/出口/战争险、247家铁水/盈利率等不可持续专业数据只作旁证；不进门、不扣分/乘系数/冻结/收紧，缺失不记unknown/temporary_gap或补核待办。①用[GATE-calm](#r-gate-calm)/[GATE-resume](#r-gate-resume)的官方事实＋SC back；黑色需求用公开周度库存/产销/现货。依赖旧专业门的JM-RB/G需求模型复活前须以公开数据重定义。

<a id="r-data-fields"></a>
**DATA-fields**　缺项须分未计算/计算失败/原始字段缺失。SC结算端点与OHLC/ATR/ADX独立，分别列原字段、计算错误和指标状态；整行NaN/接口失败不证明每个字段缺失，close不能补结算护栏。修复后逐项重算。

<a id="r-data-lineage"></a>
**DATA-lineage**　产业/概率证据列完整年份、观测日、原发布者/转引者、单位及比较期；库存加地域/样本/是否含下游。同对象/时点/口径才判conflicting，异期先作序列；区域库存/仓单不代港库/社会库存，反证不等反向可交易。FedWatch须目标会议、利率区间及采样时刻，旧值不拼当前概率。

<a id="r-data-quality"></a>
**DATA-quality**　必要证据为missing/stale/conflicting/invalid，不能据其判pass/fail；必要未知列unknown_checks，无效行仅诊断引用；可选背景缺失不阻断。取得有效证据后复核。

<a id="r-input-preparation"></a>
**INPUT-preparation**　current/preparation分列，具体腿见[DYNAMIC-roll-table](#r-dynamic-roll-table)；同对去重并列样本、缺项、research_stage。准备取样不提前换腿或授许可，一对失败不抹其他对；日期/主力先到按阶梯换月，同日互换配置。

## 1.4 硬否决（#1–#31）

<a id="r-gate-1"></a>
**0.3#1**　交易腿距最后交易日<20交易日→否决/滚动；信号席豁免，换合格新腿后重核。

<a id="r-gate-2"></a>
**0.3#2**　20日均成交量<1万手→否决；信号席豁免，单日放量不代均量；新腿/新均量达标后重核。

<a id="r-gate-3"></a>
**0.3#3**　先写实际依赖的precheck，再逐项判fail/unknown：fail阻断本模型，必要unknown→incomplete且保留已知阻断。domestic_public不继承①未知，但自身国内论证未完成仍incomplete；实际靠地缘缓和获利须改走geopolitical_fade。补齐并过全部适用门才解除。

<a id="r-gate-4"></a>
**0.3#4**　同品种横跨近/远两层的方向性单边否决；获许可的完整结构对冲/价差豁免。改为合规单层或完整结构后重核。

<a id="r-gate-5"></a>
**0.3#5**　价格/结构确认＋至少一项独立产业事实须同时成立，分两项检查：已核失败=fail，定义/必要观察缺失=unknown，不混值。同价格多指标/同源转载不算独立；专门模型仍核强因果门。public_data不套旧周度≤2/月度≤1项否决；两类及专属验证全过才满足。

<a id="r-gate-6"></a>
**0.3#6**　普通R<2或A的TP1成本后净R<2.5→计划失败、否决；有效计划达到相应R才通过，不用毛R代净R。

<a id="r-gate-7"></a>
**0.3#7**　gap_ratio按[GAP-active](#r-gap-active)/[GAP-latent](#r-gap-latent)及收紧条件核轻仓复评/淘汰；真实输入未知不能放行，信号/休眠按池规则。事件或风险输入更新后重核。

<a id="r-gate-8"></a>
**0.3#8**　结构支持评分=1→否决；结构支持重新验证通过才解除。

<a id="r-gate-9"></a>
**0.3#9**　拟建仓触及限仓额度80%须先降至以内，否则淘汰；每腿扣现仓/挂单后的新增容量取小值，足额后重核。

<a id="r-gate-10"></a>
**0.3#10**　实际受提保/限仓覆盖合约须以×0.8折单笔预算，否则不开仓；同源只一次，组合cap另核。非受影响者不适用，措施退出后重核。

<a id="r-gate-11"></a>
**0.3#11**　④未过不新开H，存量双杀无对冲不得过夜，须减仓/对冲；H/④/D15当前休眠，复活后④及完整风控通过才评估。

<a id="r-gate-12"></a>
**0.3#12**　国债曲线利差精确值/分位未补齐不得执行；当前挂起，补齐且结构池复评纳入后重建。

<a id="r-gate-13"></a>
**0.3#13**　A/结构关键序列按[INPUT-spread](#r-input-spread)验收；缺项/未计算/质量不合格→unknown、incomplete，未计算不入first_blocker；已核模型否决另列fail。A豁免D8，可选专业背景不否决；休眠先复活，补齐且全门过才评估。

<a id="r-gate-14"></a>
**0.3#14**　③产能性未证真禁止G单边多头新开；行为性/安监/deadline/立法/自律/光伏纳入口径均不解锁黑色，须对应行业③证真。

<a id="r-gate-15"></a>
**0.3#15**　山西复产达产/超预期证伪收缩→双焦/RB收缩多头减至×0.5或清仓，RB可转合格结构；铁水<230仅参考，月差依D14检视，休眠价差不能承接。持仓合规或证伪状态更新后复评。

<a id="r-gate-16"></a>
**0.3#16**　低敞口时限隔夜池方向性单边禁止新开；完整配对结构豁免但仍受组合cap，裸腿按单边。全部低敞口触发复评解除后恢复。

<a id="r-gate-17"></a>
**0.3#17**　AU/AG/CU/AL空头入场否决；信号改善不解禁，本次无新增解除路径。

<a id="r-gate-18"></a>
**0.3#18**　事件脉冲品种在政策脉冲日必须日内平仓，不得隔夜；其他日另核其余许可。

<a id="r-gate-19"></a>
**0.3#19**　政策脉冲日限隔夜池禁止新开，次日核③/事件及品种门；常规池另核自己的政策日规则。

<a id="r-gate-20"></a>
**0.3#20**　近250日H且近3年周涨上尾前10%→否决多头新开，已有仓不因本项强平；任一机械要件消失即本项解除。分位口径见[D8-definition](#r-d8-definition)/脚本§2d。

<a id="r-gate-21"></a>
**0.3#21**　金融多头周涨上尾前5%禁止追加，已有仓另按管理规则；分位退出且其余门过才重评。口径见[D8-definition](#r-d8-definition)。

<a id="r-gate-22"></a>
**0.3#22**　跳空敏感品种跨周末未对冲且单仓计划止损风险>RISK_BUDGET×30%→周五前降至该金额内或清仓，与组合cap取严；指风险金额，非保证金/名义价值/配置净值。结构按适用性，降至金额内或有效对冲核验后重评。

<a id="r-gate-23"></a>
**0.3#23**　公告/deadline/制度文件不解锁或加权；调减已核未达标→F新开冻结、叙事扣1.5。截止前缺数pending，截止后无法核验仅光伏F新开中性冻结，无罚分、存量不动；无数据≠未达标。期限见[DYNAMIC-deadline](#r-dynamic-deadline)，数据到即按达标/未达裁决，不静默顺延。

<a id="r-gate-24"></a>
**0.3#24**　§2品种专属否决与本清单同效力；按该品种的适用范围及解除条件执行。

<a id="r-gate-25"></a>
**0.3#25**　方向性单边当日ATR重校准未完成/未通过→不得隔夜，日内了结或对冲；有效核验后重评。结构豁免单腿ATR，仍核自身SL/组合cap。

<a id="r-gate-26"></a>
**0.3#26**　①未缓和证真禁止能源方向空头新开；geopolitical_fade仅在①＋结构确认后评估，中断期不适用。独立domestic_public按[A-reversion](#r-a-reversion)论证；两路线均核质变±1与压力，不改名绕门。①缓和后仍核对应结构确认/其余许可。

<a id="r-gate-27"></a>
**0.3#27**　近月政策多头须基差/库存/现货价至少两项同向，否则否决；远月F另须三重验证＋③，不豁免。独立现货达标后重核。

<a id="r-gate-28"></a>
**0.3#28**　官方两融证实实际未回升→恢复IM/IC新开否决及“企稳验证中”；官方口径和②'重新证真才解除。IM/IC池外时交易门休眠、资金背景保留。

<a id="r-gate-29"></a>
**0.3#29**　仅AU/AG方向性：利率事件T−10复评重入，重入后T−3至T+1双向禁新开，T+1按结果归档或延续；不外推全池D12、不解禁池许可，当前窗口见[DYNAMIC-freezes](#r-dynamic-freezes)。

<a id="r-gate-30"></a>
**0.3#30**　能源判定腿单日结算涨跌幅≥5%后3交易日，禁止顺该方向单边新开；多空对称，完整结构豁免，空头另核#26、MA周涨取严。3日到期仍核其他门。

<a id="r-gate-31"></a>
**0.3#31**　先有方向/真实失效SL/成本，再核全部适用系数、账户及容量；风险或保证金/限仓容量<1→记录对应阻断，必要未知→最终手数null，状态依[AUDIT-incomplete](#r-audit-incomplete)/[AUDIT-awaiting](#r-audit-awaiting)，不伪造本门已过。2ATR只扫描，不代表最终手数；不得倒推窄SL，结构按整组，用户/池排除优先。完整有效计划及全部门/容量通过才可评估。

## 1.5 Precheck 与软前置

<a id="r-soft-d12"></a>
**SOFT-D12** → [D12-trigger](#r-d12-trigger)（同义锚）。

<a id="r-soft-ma"></a>
**SOFT-MA** → [CARD-MA](#r-card-ma)（同义锚）。

<a id="r-soft-chain"></a>
**SOFT-chain**　基差/库存/利润背离的方向性新开→扣分并降系数，不一律×0；完整A不套该单边软前置，SI/PS显著背离仍可作沽空/回归依据。链恢复一致后重核。

<a id="r-soft-lowadx"></a>
**SOFT-lowadx**　ADX<20且无季节窗口、无政策/事件日历→观望；A/D/E/F、已解锁G及结构候选豁免。独立策略触发后复评。

<a id="r-soft-beta"></a>
**SOFT-beta**　相关性再校准期，权益beta方向多头门槛+0.3并优先对冲；结构豁免，相关性恢复后重核。

<a id="r-gate-calm"></a>
**GATE-calm**　地缘fade评估；名义解除/正式重开（官方）+SC近端back回落同向（脚本§1）；缓和证真后结构确认才评估；通航量/战争险为参考旁证不作要件；谈判headline不构成裁决；仅geopolitical_fade等依赖该因果模型必填；收入分成协议不算重开；国内独立回归按[A-reversion](#r-a-reversion)；复核/解除：任一反向质变回中性。

<a id="r-gate-resume"></a>
**GATE-resume**　中断证真评估；正式关闭/再袭船或布雷（官方或多源headline）＋SC近端back反弹（脚本§1）；全过→中断证真、回事件冲击模式；不恢复已存档的建仓许可；通行再受阻/海湾出口下降为参考不作要件；headline不代back方向；复核/解除：反向质变回僵局/缓和。

<a id="r-gate-long"></a>
**GATE-long**　僵局期单边多头逐项核具体护栏，并非永久禁止；冻结到期重核。空头仍#26，结构fade仍①。

<a id="r-gate-capacity"></a>
**GATE-capacity**　产能性评估；不可逆退出/纳入口径+调减达标+公开库存同向；对应品种解锁评估；钢厂盈利率/247家铁水为参考；行为性/政策公告/自律不解锁;池外先备选；复核/解除：数据判决#23。

## 1.6 策略触发与参数

<a id="r-trigger-b"></a>
**TRIGGER-B**　[固定窗口](#r-trigger-b-window)内或前20交易日只作研究筛选；完整开仓须品种证据/许可、[PLAN-B](#r-plan-b)与适用门。窗末结束，新定义只前瞻使用。

<a id="r-trigger-d"></a>
**TRIGGER-D**　已落地事件次日确认后按D评估，不抢跑；日历真空不打分，有新节点再研究。

<a id="r-trigger-e"></a>
**TRIGGER-E**　周涨跌近3年前20%（[D8-definition](#r-d8-definition)取被回归侧）且ADX<22，并有官方落地＋首段价格修正＋现货/微观同向，才按[PLAN-E](#r-plan-e)评估已有许可；未决地缘/政策变量不接飞刀。

各策略按下表参数评估，并叠加全部适用门；“轻仓区间”不能绕过硬门。

| 稳定规则 / 策略 | 开仓门槛 | 轻仓区间 | 金额系数 | R | 默认持仓 / 上限 | 专属条件 |
|---|---|---|---|---|---|---|
| <a id="r-param-d"></a>**PARAM-D** | ≥4.0 | 3.5–4.0 | 0.7 | ≥2 | 5–20日 / 30日 | 专属事件门 |
| <a id="r-param-a"></a>**PARAM-A** | ≥4.0且完整计划有效 | 3.5–4.0 | 0.85 | 净R≥2.5 | public_data优先5–20交易日；30–60日仅旧参考 / 结构退出日 | 滚动退出先到 |
| <a id="r-param-f"></a>**PARAM-F** | ≥4.2 | 3.7–4.2 | 0.6 | ≥2 | 10–30日 / 60日 | ③与现货 |
| <a id="r-param-e"></a>**PARAM-E** | ≥3.5 | 3.0–3.5 | 0.5 | ≥2 | 5–15日 / 30日 | SI为0.4–0.5，逆风另×0.5 |
| <a id="r-param-g"></a>**PARAM-G** | ≥4.7 | 4.2–4.7 | 双焦0.5、RB0.4 | ≥2 | 15–40日 / 60日或证伪 | 当前冻结 |
| <a id="r-param-c"></a>**PARAM-C** | ≥4.8 | 4.3–4.8 | 0.3–0.4 | ≥2 | 30–90日 / 120日 | 事件D12门槛+0.3 |
| <a id="r-param-b"></a>**PARAM-B** | ≥4.2 | 3.7–4.2 | 0.7 | ≥2 | 窗口内 / 窗口结束 | ADX<25另×0.7 |

<a id="r-param-overnight"></a>
**PARAM-overnight**　常规隔夜≥4.2/轻仓3.7–4.2，限隔夜非趋势白名单≥4.5/轻仓4.0–4.5；趋势白名单用专门阈值，许可变化再核。与策略阈值优先关系保留§0歧义。

<a id="r-param-caps"></a>
**PARAM-caps**　受总分上限限制候选；E上限4.0；无③政策deadline近月多头3.0；RB/SI无远月赔率近月出清多头3.0；③未过且judgement未达RB/SI远月多头4.0；②''未实质过IM/IC多头4.0；先限分再判门；池外休眠；复核/解除：前置实质通过。

<a id="r-trigger-b-window"></a>
**TRIGGER-B-window**　SR/CF季节筛选；SR-summer每年07-01至09-30；CF-spring每年03-01至04-30；CF-autumn每年09-01至10-31，均含首尾；真实郑商所日历映射区间首/末交易日；research_start=首日前20交易日；planned_exit=末日前5交易日；research_start≤审计交易日≤window_end才入研究；窗外直接no_signal，不为下游TP/账户维持incomplete；CF两窗独立；季节主题不是期货上涨证据；复核/解除：窗口完毕；不使用普通工作日推算。

## 1.7 评分与金额系数

基础权重按 [SCORE-normalize](#r-score-normalize) 的固定分母计算，不按当周数据可得项重加权。

| 稳定规则 / 策略 | D1 | D2 | D3 | D4 | D5 | D7 | D9 | 特例 |
|---|---|---|---|---|---|---|---|---|
| <a id="r-weight-a"></a>**WEIGHT-A**（A/H） | 12% | 22% | 20% | 18% | 8% | 0% | 10% | D10=0，D8豁免 |
| <a id="r-weight-d"></a>**WEIGHT-D** | 20% | 25% | 15% | 12% | 10% | 5% | 8% | D10属性加分0.5/0.3/0.1/0，池内属性唯一；不放大手数，商品0不等于金额×0 |
| <a id="r-weight-f"></a>**WEIGHT-F** | 18% | 25% | 12% | 15% | 5% | 5% | 10% | D3b仅远月产能性+0～0.3；D10准金融+0.3/混合+0.1/商品+0 |
| <a id="r-weight-g"></a>**WEIGHT-G** | 15% | 30% | 15% | 20% | 5% | — | 10% | 行为性D2=0 |
| <a id="r-weight-c"></a>**WEIGHT-C** | 23% | 12% | 15% | 12% | 7% | 10% | 12% | D10+0.3，D11加倍 |
| <a id="r-weight-b"></a>**WEIGHT-B** | 28% | 20% | 18% | 18% | 7% | — | 9% | D2季节专用 |

“—”表示原固定表未列该维度，不临时追加或据此重算其他权重。

<a id="r-weight-evidence"></a>
**WEIGHT-evidence**　F/G/A微观；F执行级=实施细则＋产能纳入口径＋执行案例＋调减进度；公告/deadline/立法计0；G行为性D2计0；现货门仍是硬前置；光伏价格合规/能耗国标可快评但不代③/#27；A按公开评分卡；复核/解除：有效新证据。

<a id="r-d9-levels"></a>
**D9-levels**　流动性背景；5=社融与M2同比双升＋SOFR下行＋DXY走弱；4=三项中两项扩张；3=中性；2=两项收缩；1=全面收缩；可信公开增量按条件计分；无增量固定3并标default_neutral；默认不是已核宏观中性；D13同源为主，不重复满额扣；三项分组歧义见审计报告，不自行补规则。

<a id="r-d10-score"></a>
**D10-score** → [WEIGHT-D](#r-weight-d)（同义锚）。

<a id="r-d8-definition"></a>
**D8-definition**　D8周涨分位计算（脚本§2d）；fut_mapping锚日主力、同一合约两端结算价算周涨（不拼接复权）；终点=最新已完成行情日，起点=终点前7自然日当日或之前最近交易日；历史样本=终点前3年每个自然周最后交易日、不含本周；有效样本<期望周数80%→D8=unknown（calculation缺口）；多头看上尾（历史样本低于当前值的比例≥100−X即前X%）、空头看下尾、商品双向按拟交易方向取侧、E取被回归侧；任一端缺结算→样本无效，不用收盘补；A结构豁免；只作输入不单独构成信号；复核/解除：每期快照重算。

<a id="r-d8-fin-long"></a>
**D8-fin-long**　金融多头周涨上尾前10%扣0.5、前5%否决；A/F产能性通过型/G验证通过型豁免。分位退出后本项解除，其他门另核。

<a id="r-d8-fin-short"></a>
**D8-fin-short**　金融空头按下尾前30%扣1、前20%否决；#17仍独立禁空。分位退出后本项解除。

<a id="r-d8-commodity"></a>
**D8-commodity**　商品按拟交易方向取尾，前20%扣0.5、前10%否决；A/F产能性通过型/G验证通过型豁免，D14/D15优先。分位退出后本项解除。

<a id="r-d11-bands"></a>
**D11-bands**　单边多头贴顶；dist>5%扣0；3%-5%扣-0.2；1%-3%扣-0.3；0.3%-1%扣-0.5；<0.3%扣-0.8并否决新开；逐档扣分；C惩罚加倍（0.3%-1%为-1.0）；结构不适用；已有仓不强平；边界重复歧义保留待澄清，不自行补端点；复核/解除：dist换档。

<a id="r-d12-trigger"></a>
**D12-trigger**　波动升档；HV20/HV60>1.3或ATR20>80分位或T-3；扣分−0.3且门槛+0.3，未过转观望/合格结构；完整结构豁免；复核/解除：升档触发退出。

<a id="r-d12-bands"></a>
**D12-bands**　ATR250分层；ATR250分位>80 / 40-80 / <40；高波×0.5、当期ATR核SL、gap收紧一档及隔夜重核；其余常规；临近T−3低波至少常规；单一收紧值按淘汰线；结构豁免方向性D12；复核/解除：分层更新。

<a id="r-d12-diverge"></a>
**D12-diverge**　池内ATR分位极差>50→逐品种独立核参；结构豁免单腿重校准，分化解除后更新。

<a id="r-d14-restart"></a>
**D14-restart**　仅对依赖成本/收缩因子的计划：山西复产达产/超预期（~6975万吨）→扣0.5～1，多头减至0.5或清仓，月差检视。独立国内月差不继承未知铁水，但须处理已知相关反证；不自动解锁③。独立证伪解除后复评。

<a id="r-d14-water"></a>
**D14-water**　铁水<230万吨（参考）；不作执行条件；不扣分、不触发处置，仅RB需求侧背景旁证；需求证弱按[D14-stock](#r-d14-stock)（库存转累/现货转贴水）判定。

<a id="r-d14-stock"></a>
**D14-stock**　库存转累或现货转贴水→扣0.5、减50%；适用性/豁免同[D14-restart](#r-d14-restart)，去化与现货恢复后重核。

<a id="r-d14-pass"></a>
**D14-pass**　复产慢于预期且去化/需求延续→不扣；铁水≥230仅参考。适用性/豁免同[D14-restart](#r-d14-restart)，证真不解锁③，反向即重核。

<a id="r-pen-narrative"></a>
**PEN-narrative**　当前适用脆弱叙事每项扣0–3，已证伪归档不计；实际证据变化后重评。

<a id="r-pen-fixed"></a>
**PEN-fixed**　PPI/产能/股指/能源条件；PPI输入性>60%扣1；③未达扣1.5；7-8月PPI收窄兑现远月扣0.5；IM/IC②''未实质过扣1；能源单边①未缓和证真扣1；条件扣减；只当期适用可核事实；精确比例缺失不猜不扣；能源结构豁免；池外不入执行分母；复核/解除：对应门解除。

<a id="r-factor-groups"></a>
**FACTOR-groups**　单笔适用系数0–1，按预算金额相乘；不适用记1及理由，同源只一次，状态改变后重算。

<a id="r-factor-nearhigh"></a>
**FACTOR-nearhigh**　多头距高点5%内×0.6、2%内×0.3；取最严一档不双乘，退出相应档后更新。

<a id="r-factor-correlation"></a>
**FACTOR-correlation**　未对冲权益beta处相关性再校准期→预算×0.5或对冲/观望，不重复D12；相关性重建后复评。

<a id="r-factor-policy"></a>
**FACTOR-policy** → [0.3#10](#r-gate-10)（同义锚）。

<a id="r-score-normalize"></a>
**SCORE-normalize**　基础分=Σ(固定原始权重×维度分)/Σ固定权重，再加减适用项；A分母90、D95、F90，其余按固定表。原权重无需合计100%，不得按可得项重加权；仅D9可固定默认，必要维度未知则总分null，补齐后重算。

<a id="r-conf-definition"></a>
**CONF-definition**　A价格确认；价差指标、方向、阈值、窗口、价格口径、经济理由＋rule_version/带时区defined_at/effective_from；confirmation_definition=undefined/draft/frozen；仅冻结生效规则判对应观察期；草案/必要观察未知→unknown；分位另列screening_evidence；三日/40元/两周示例非默认门槛；复核/解除：按[CONF-owner](#r-conf-owner)由研究方提供具体定义或不能成案原因。

<a id="r-conf-prospective"></a>
**CONF-prospective**　确认定义仅前瞻生效；同机会沿版本，修改须留原定义/理由/生效时间。不回判旧信号、不逐周重开观察窗；以生效后必要观察判定。

以下 SCORE-D1–D5 是 A 公开数据评分的治理锚，未声称收益回测验证；必要输入齐后依冻结规则重算。

<a id="r-score-d1"></a>
**SCORE-D1**　A公开数据D1；5=冻结生效价格确认满足；3=已定义可核未确认；1=已核价格模式反向；未冻结/缺必要观察=null；只价格模式，产业归D2；未确认不满足#5，高分不能抵消。

<a id="r-score-d2"></a>
**SCORE-D2**　A公开数据D2；3=一项当前合适产业支持；5=至少两个独立经济维度同向且无未解释反证；1=已核反证；必要缺失=null；价格多个指标/同源转载不计多项；先处理#5。

<a id="r-score-d3"></a>
**SCORE-D3**　A公开数据D3；净R<2.5先否决；2.5≤R<3给3；3≤R<4给4；R≥4给5；计划/成本未知=null；不倒推SL凑分。

<a id="r-score-d4"></a>
**SCORE-D4**　A公开数据D4；样本合格且分位≥85给5；70≤分位<85给3；<70未达筛选；必要缺失=null；位置不能独自证明方向/回归。

<a id="r-score-d5"></a>
**SCORE-D5**　A公开数据D5；5=期限/流动性满足且不跨适用离散事件；3=满足但跨事件；1=已核期限或流动性失败；必要未知=null；单一档，不填1–3；事件门另核，不由分数代替。

<a id="r-conf-owner"></a>
**CONF-owner**　research为最接近的至多两条MA候选完成方向/经济失效SL/目标期限/净R、确认草拟冻结及前瞻观察；不能成案列事实/计算缺件、负责人、动作/期限。既有许可内不等用户批准，不编阈值/SL或扩许可；用户只补账户/挂单、偏好变更和新权限。首次取冻结后完整观察期，同opportunity_id/版本不重开钟。

## 1.8 交易计划与真实容量

<a id="r-a-definition"></a>
**A-definition**　MA/RB/SR同品种跨月1:1，每组近远各1手；S=近−远，元/吨；多=买近卖远，空相反。跨品种/非1:1须另核模型许可。

<a id="r-a-screen"></a>
**A-screen**　同期分位≥70为研究候选，≥85为高分位候选；非方向、非主仓触发。低分位对称路线未开放；完整信号另核。

<a id="r-a-reversion"></a>
**A-reversion**　高价差回归且已有许可；SL>Entry>TP1≥TP2；空价差；domestic_public须国内变化独立支持收敛，即使海峡未缓和仍有论证，并核反向地缘冲击；获利依赖缓和则geopolitical_fade、必须①；通用价格确认＋独立产业事实不能替代强因果专属门；不开放MA单边空头；复核/解除：经济失效触真实SL；必要专业数据长期不可得的模型research_only。

<a id="r-a-continuation"></a>
**A-continuation**　方向/目标须来自显式许可且已验证的模型；多SL<Entry<TP1≤TP2，空相反。本次只保留协议，不新增许可。

<a id="r-a-fields"></a>
**A-fields**　计划生成；两腿/配比、模式/方向/许可、evidence_basis及支持反证、确认定义、Entry/SL/TP1/TP2、价格单位/乘数、费用滑点、行情日/样本、最短/最长持有期、最晚退出日、双腿限价/滑点/撤单平裸腿/压力预案；研究方形成方案；必要缺项incomplete，不整包交回用户；无证据可写具体不能成案原因；方向/净R错误是已核计划失败；复核/解除：补件/重设计划。

<a id="r-a-median"></a>
**A-median**　50/30/10分位仅参考，50不作SL/风险锚，30/10非强制TP；入场冻结目标数值/样本/依据，分位统计与人民币损益分列，不随样本挪SL/TP，换月重建。

<a id="r-a-stop"></a>
**A-stop**　SL取经济逻辑失效点，不为凑手数反推窄止损或放宽止损；新逻辑须重建计划。

<a id="r-a-cost"></a>
**A-cost**　cost_unit=两腿开平合计滑点＋两腿开平合计手续费；仅滑点默认4×tick_value，实际更大取更大，手续费另加。side=+1多价差/−1空价差；risk_unit=side×(Entry−SL)×multiplier+cost_unit；net_reward_tp1=side×(TP1−Entry)×multiplier−cost_unit；R=net_reward_tp1/risk_unit≥2.5。价格CNY/tonne，一组近远各1手，风险/收益为人民币；真实成交后重核。

<a id="r-a-r"></a>
**A-R** → [0.3#6](#r-gate-6)（同义锚）。

<a id="r-a-fill"></a>
**A-fill**　Entry为信息齐备后下一可成交时点的计划价差，不假设盘后结算可成交；两腿成交后重核真实风险与R。

<a id="r-a-legs"></a>
**A-legs**　事前给双腿限价、最大滑点及未成交撤单/平裸腿预案；裸腿按单边占预算，配对完成前无结构豁免。

<a id="r-a-stress"></a>
**A-stress**　检视价差反向跳变、单腿成交及扩板提保；gap、周末及保证金门分别核，必要输入未知不能ready。

<a id="r-a-expiry"></a>
**A-expiry** → [ROLL-plan](#r-roll-plan)（同义锚）。

<a id="r-a-overrides"></a>
**A-overrides**　MA/黑色结构；按实际因子核D14、①、质变事件与组合cap；MA两证据路线分开；RB国内独立月差不因未知铁水自动失败，相关反证不可忽略；完整A豁免单边#30、MA周涨及D8/D11/D12；裸腿另核；复核/解除：各门释放。

<a id="r-plan-style"></a>
**PLAN-style**　不做日内，只用已许可单边/结构；期权/跨式未开放，扩展须明确许可。

<a id="r-plan-d-time"></a>
**PLAN-D-time**　事件发生；T-3~T-1/T/T+1~T+3;次日开30分钟；观察→确认→入场；不抢跑/股指禁空；复核/解除：事件之后核门。

<a id="r-plan-d-exit"></a>
**PLAN-D-exit**　D有效计划；SL1.5ATR/反向极值;TP1+2R;TP2窗末前2日；止损/移动/强平；双向需有效反向公式；复核/解除：退出。

<a id="r-plan-e"></a>
**PLAN-E**　已出清叙事；Entry±0.3ATR;SL±1ATR;TP30日均值；多/空对应公式；金属反向/权益反弹不经E;能源仍①；复核/解除：计划失效。

<a id="r-plan-b"></a>
**PLAN-B**　许可B做多且窗口筛选通过；Entry_raw=max(MA20,pre_window_low5+1×ATR20)；Entry向上对齐tick；SL向下对齐(Entry−1.5×ATR20)；价格元/吨；按[PLAN-B-history](#r-plan-b-history)算mean_return；TP1向下对齐Entry×(1+0.7×mean_return)，5%=0.05；pre_window_low5为窗口开始前5个交易日最低low，固定不滚动；MA20/ATR20取具体合约最近完整交易日；缺数据unknown，不报定义未核；复核/解除：计划/行情变更须按新剩余期限重算；不抬TP缩SL凑R。

<a id="r-risk-caps"></a>
**RISK-caps** → [RISK-regime](#r-risk-regime)（同义锚）。

<a id="r-risk-regime"></a>
**RISK-regime**　当期15项触发核定normal/low_exposure后计算：normal=实际净值×3.5%，low_exposure=min(normal,固定5000元)；单笔仍净值3.5%。unknown则portfolio_cap/final_lots=null，仅可标情景参考，不能默认normal。低敞口不入factor_product/无regime_factor，净值下降取更低normal、上涨仍封顶5000；计划止损非最大亏损，实际占用另核，全部触发及账户复评后重算。

<a id="r-risk-unit"></a>
**RISK-unit**　逻辑/SL成本确定；risk_unit=abs(Entry−SL)×multiplier+round_trip_cost；单腿滑点预算=2×slippage_tick×tick_value，另加开平手续费；真实一手风险；A用组公式;禁中位数锚；复核/解除：成交变动重核。

<a id="r-risk-factor"></a>
**RISK-factor**　factor_product=strategy_factor×适用场景系数；trade_effective_budget=trade_cap×factor_product，先折金额；D10不是乘数，同源去重，状态变化重算。

<a id="r-risk-used"></a>
**RISK-used**　账户持仓剩余计划风险与挂单/部分成交未入持仓的预留风险逐项≥0后相加；同一部分不重复计，成交/撤单即刷新。

<a id="r-risk-add"></a>
**RISK-add**　新开或加仓；trade_remaining=max(0,trade_effective_budget−existing_trade_risk)；portfolio_remaining=max(0,portfolio_cap−used_open_risk−reserved_order_risk)；candidate_budget=min(trade_remaining,portfolio_remaining)；新交易existing_trade_risk须显式0；本交易原持仓挂单已含在组合占用，不二次加算；复核/解除：新计划。

<a id="r-risk-round"></a>
**RISK-round**　risk_lots=floor(candidate_budget/risk_unit)，只在金额预算折减后取整一次；不先floor再乘系数，数据变化后重算。

<a id="r-risk-final"></a>
**RISK-final**　regime/账户/计划/容量齐后：final_lots=min(risk_lots,margin_capacity_lots,position_limit_capacity_lots)；必要未知为null，已核0容量才阻断。输出normal/current和low_exposure_cash_cap，旧portfolio_risk_cap只是current别名，无regime_factor。输入变化重算，数值容量不代全门许可。

<a id="r-risk-dedup"></a>
**RISK-dedup**　贴顶取最严档；D12高波共振0.3替代0.5；MA>8优先>5；同源仅一次，独立T−1可叠加，状态变化重算。

<a id="r-risk-tool"></a>
**RISK-tool**　数值工具factors；strategy、D11、D12、D13、D14、D15、event_window、exchange_buffer、promotion、driver_weakness、MA_oil_guard、seasonal_adx、policy_adverse、equity_confirmation、correlation_recalibration；factors仅接受所列15组；拒未知组/重复JSON键；同源按最严值先合并；D12含高波/T−3/共振；event_window仅独立T−1；driver_weakness含同源链背离；复核/解除：新增组先同步。

<a id="r-risk-snapshot"></a>
**RISK-snapshot**　账户verified_at须带时区、与测算同一上海日期且不晚于测算；核实完整持仓/挂单，空列表须实核，POSITIONS空/历史空仓不作证明。新成交/撤单即刷新。

<a id="r-risk-net"></a>
**RISK-net**　配对结构风险计一次，裸腿按单边；不同交易保守相加，不因反向、浮盈或未验相关性抵消；另有核定模型才另议。

<a id="r-risk-profit"></a>
**RISK-profit**　盈利持仓仍计“当前估值到有效SL的不利损失＋费用”，逐项≥0；浮盈不自动抵扣，SL变化即重核。

<a id="r-risk-margin"></a>
**RISK-margin**　新增容量须满足全账保证金≤净值60%、提保单品≤20%及经纪商实收/可用资金；未核优惠不抵扣，资金/规则改变重算。

<a id="r-risk-limit"></a>
**RISK-limit**　各腿在限仓80%内扣现仓/挂单，取较小新增配对容量；不复用预算，成交/预留变化重算。

<a id="r-risk-reserve"></a>
**RISK-reserve**　多候选依评分及固定平分顺序逐笔预留后重算，不复用组合余量；撤单释放。

<a id="r-risk-null"></a>
**RISK-null**　必要输入未知用null，不能填0；状态依[AUDIT-incomplete](#r-audit-incomplete)和[AUDIT-awaiting](#r-audit-awaiting)。完整核算为0才认预算/容量阻断，补齐后重算。

<a id="r-risk-recal"></a>
**RISK-recal**　ATR_now/entry>1.3或分位升入>80，每日按原策略SL及当前ATR重算；超额次日先降仓，即时约束优先。不统改2ATR、不放宽止损。

<a id="r-risk-structure-recal"></a>
**RISK-structure-recal**　结构每日核自身有效SL、实际风险、双腿保证金及组合cap；只豁免单腿ATR重校准。

<a id="r-risk-stock-regime"></a>
**RISK-stock-regime**　低敞口多个触发只封顶一次，存量按实际金额减至cap，不每日再减半；更严强平/禁隔夜保留，全部触发复评后解除。

<a id="r-plan-b-time"></a>
**PLAN-B-time**　B拟新开；window_start≤执行交易日<planned_exit；最晚退出=min(planned_exit,合约既有强制退出日)；前20交易日仅准备；期限不够则计划失败；研究筛选到window_end不等可新开；旧榨季/新旧作快照不覆盖日期表；复核/解除：执行/合约日期更新即重核。

<a id="r-plan-b-version"></a>
**PLAN-B-version**　采用新B定义；rule_version=B-v2.24；defined_at/effective_from带时区；生效不早于获准采用后的首个完整交易日；研究方登记后仅前瞻使用；窗口与新公式同版本；日期为未校准的研究治理参数，不回判过去信号/收益；不随当期涨跌迁窗；复核/解除：每个窗口结束复评信号/可得性/成本；修订只用于以后窗口。

<a id="r-plan-b-history"></a>
**PLAN-B-history**　拟入场及最晚退出已定；之前连续3个年份，每年同window_id一个收益率；r_y=P_exit_y/P_entry_y−1；mean_return=(r_y1+r_y2+r_y3)/3；同品种同交割月、交割年与窗口年的差值平移；2026秋CF2701对应2025秋CF2601；入场月日向后找首交易日、退出月日向前找末交易日，均在历史窗口且入场<退出、合约可交易期内；两端settle，逐年列日期/值/来源；含亏损年份，不筛年/拼主力/用close/缩年/扩窗；任何一年未上市或缺端点/口径未知则具体unknown；现有日线或终端导出可用，不需专业季节库；复核/解除：按剩余持有区间重算；持续不可得按0D仅复评B可行性，三年目标样本不证明收益有效。

<a id="r-plan-b-economics"></a>
**PLAN-B-economics**　B价格及期限已算；mean_return≤0或TP1≤Entry或net_R<2或期限不行；已核计划失败；R/成本及金额容量按Step5统一定义，不另造公式；参数未知才unknown；窗口筛选不代产业/#5；D8、原分数、策略0.7和ADX<25再×0.7保留；复核/解除：真实计划改动再验；失败与必要未知并存按AUDIT状态。

<a id="r-plan-b-trail"></a>
**PLAN-B-trail**　TP1触达后跟踪；SL=max(原有效SL,此前5个完整交易日最低low)，只上移；已穿越则按可执行报价处置；TP2按此跟踪，到最晚退出日收盘前清余仓，合约更早强制退出优先；TP1只是跟踪启动线，不新增强制分批比例；6.1通用锁盈/止损和6.3贴顶规则取严；不挂虚假可成交SL；复核/解除：研究方交Entry/SL/TP1、TP2规则、入退日、成本/net_R；seasonal_plan.py仅离线算术、不授许可。

## 1.9 已核实持仓管理与换仓

<a id="r-manage-stop"></a>
**MANAGE-stop**　触及SL立即平仓，超策略持仓上限强平；特例取更严者。

<a id="r-manage-profit"></a>
**MANAGE-profit**　盈利>1R移保本、>2R锁1R、>3R锁2R；AU/AG用[MANAGE-AU](#r-manage-au)，退出后结束。

<a id="r-manage-driver"></a>
**MANAGE-driver**　核心微观1项反向或驱动弱/存疑→减至×0.5或对冲，不依赖事件日历；证据恢复后复评。

<a id="r-manage-f"></a>
**MANAGE-F** → [PLAN-F](#r-plan-f)（同义锚）。

<a id="r-manage-event"></a>
**MANAGE-event**　方向性单边横跨离散事件，T−1减至×0.5或对冲；只用许可工具，完整结构豁免单边纪律；落地后复评。

<a id="r-manage-geop"></a>
**MANAGE-geop**　[双轴质变](#r-reg-geop)当日T0/次日双向检视，减反向风险并持续复核；通行量仅参考，不自动新增交易。

<a id="r-manage-exchange"></a>
**MANAGE-exchange**　提保/限仓公告日按全账保证金60%、提保单品20%、限仓80%主动降至阈值，优先保有效对冲腿；措施退出再核。

<a id="r-manage-top"></a>
**MANAGE-top**　任意多头dist_to_H250%<2%且盈利>2R→锁1.5R；dist<0.5%且盈利>1R→平50%；须实测，dist恢复后重核。

<a id="r-manage-policy"></a>
**MANAGE-policy**　政策脉冲日限隔夜池必检：顺向且未触D8前5%持有不加，反向放量减50%；SI日内强平，禁止新开；次日按③快评。

<a id="r-manage-rb"></a>
**MANAGE-RB** → [CARD-RB-manage](#r-card-rb-manage)（同义锚）。

<a id="r-manage-ma"></a>
**MANAGE-MA** → [CARD-MA](#r-card-ma)（同义锚）。

<a id="r-manage-agri"></a>
**MANAGE-agri** → [CARD-M](#r-card-m)（同义锚）。

<a id="r-swap-same"></a>
**SWAP-same**　同品种远月评分高≥0.5且流动性更优可评估移仓；实际滚动仍按[结构](#r-roll-structure)/[方向腿](#r-roll-direction)规则，换入须过全门，不沿旧<10日规则延后。

<a id="r-swap-cross"></a>
**SWAP-cross**　新候选评分高>1且旧核心驱动弱，完整核验后换仓；休眠品种不得承接。

<a id="r-swap-d8"></a>
**SWAP-D8**　金融多头上尾前10%降权、前5%不加但保底仓不强平；创新高且前10%→转合格A或减50%，分位退出后复评。

<a id="r-manage-no-account"></a>
**MANAGE-no-account**　实际持仓核实后才执行管理动作。账户未知时先做研究，final_lots=null；历史空仓/存量条款不证明当前账户，核验要求见[RISK-snapshot](#r-risk-snapshot)。

<a id="r-manage-tail"></a>
**MANAGE-tail**　敏感品种驱动存疑且未对冲；敞口>30%风险预算；强制降至30%或清仓；不依赖事件日历；结构按单边约束豁免仍核组合和专属门；复核/解除：驱动与有效保护重新核验。

## 1.10 跳空执行风险

<a id="r-gap-active"></a>
**GAP-active**　MA/RB/SR/CF/M执行风险；MA 1.3/1.8；RB/M/SR/CF 1.5/2.0；MA①未缓和证真1.2；RB山西复产公告±2日1.3（铁水为参考不触发）；WASDE±1为1.3；依[GAP-definition](#r-gap-definition)分别减额复评/淘汰；单一收紧值为淘汰线；真实数据缺失不可填默认；复核/解除：收紧事件结束。

<a id="r-gap-definition"></a>
**GAP-definition**　执行压力核算；gap_ratio=stressed_loss/planned_loss；stressed_loss=max(planned_loss,压力退出损失+压力成本)；同手/组、同人民币费用口径；以已列场景下SL穿透可执行估价核报价/历史跳空/涨跌停依据与假设；结构同一时点双腿及裸腿事故；不拼有利异步报价，不以无新闻作零压力；公开行情/交易规则可用；复核/解除：研究可列待核，交易前必要场景/报价缺失incomplete。

<a id="r-gap-action"></a>
**GAP-action**　gap_ratio触及表内约束；超过第一数→具体减额复评；超过第二数→否决；单一收紧值=淘汰线；复核绝对压力金额与可用资金，有金额依据才可完成执行核验；减手数不改变单位gap_ratio，不绕第二线；参数是治理值非已验证最优；复核/解除：明确压力承受方案和执行输入。

## 1.11 审计输入约束

证据有效性见 [DATA-quality](#r-data-quality)，确认版本见 [CONF-definition](#r-conf-definition)，账户时效见 [RISK-snapshot](#r-risk-snapshot)；输出与发布见 §1.12。

## 1.12 每周执行诊断

<a id="r-audit-weekly"></a>
**AUDIT-weekly**　每周均新增execution-audit，无论是否更新框架；市场元研究不能替代。

<a id="r-audit-unit"></a>
**AUDIT-unit**　候选=行情交易日＋合约/价差对＋策略＋方向＋框架版本；未定方向记unknown，明确后关联原记录；同一机会跨周保留ID去重。

<a id="r-audit-coverage"></a>
**AUDIT-coverage**　列已/未覆盖范围；逐门先判适用性及理由，再填pass/fail/unknown/not_applicable；检查完整才声明覆盖完整。

<a id="r-audit-no"></a>
**AUDIT-no**　已核触发未满足→no_signal，仅说明该策略未触发；后续可早停并列未评估项，信号变化后重核。

<a id="r-audit-incomplete"></a>
**AUDIT-incomplete**　必要未知→incomplete，已知阻断仍全部保留；不能写市场无信号。已成案且仅账户类未知须用[AUDIT-awaiting](#r-audit-awaiting)，补齐后重评。

<a id="r-audit-block"></a>
**AUDIT-block**　完整候选已核有否决或零容量→blocked，可同时列预算/交易条件/许可阻断；必要未知仍按incomplete处理，阻断解除后重核。

<a id="r-audit-awaiting"></a>
**AUDIT-awaiting**　schema 3专用：triggered＋available＋至少一项适用检查已评估，Entry/SL/TP数值与ISO最晚退出日齐，无fail且所有适用unknown均为gap.kind=account→awaiting_account、final_lots=null。账户已核、计划不全、其他未知或有fail均不适用；满足却写incomplete亦错。账户核验后转ready/blocked。

<a id="r-audit-ready"></a>
**AUDIT-ready**　完整信号及适用门全过，方向/SL/TP/R/期限/账户预算有效且final_lots≥1→ready；成交前仍刷新报价、账户及事件。

<a id="r-audit-only"></a>
**AUDIT-only**　only_blocker：一fail且其余适用全pass=true，至少两fail=false，一fail兼必要unknown=null；无阻断不声称唯一。first_blocker/all_blockers只收已核fail，未知单列unknown_checks；第一刀非独立因果，补齐后重判。

<a id="r-audit-account"></a>
**AUDIT-account**　verified_flat/verified_positions必须有当期已核完整账户快照；历史空仓/已了结/POSITIONS空不代核验，否则unknown。

<a id="r-audit-wording"></a>
**AUDIT-wording**　覆盖完整且全为no_signal/blocked才可称已核范围无合格新开；有缺项写未形成方案，有awaiting_account列成案计划及待账户核验；不外推“市场不值得交易”。

<a id="r-audit-pending"></a>
**AUDIT-pending**　未完成项列负责人、缺件、期限及到期动作；补齐或到期处置，不静默顺延，不把研究未完成当用户已作选择。

<a id="r-audit-fields"></a>
**AUDIT-fields**　审计输出；schema 3；旧schema 2仅兼容历史版本；signal=triggered/not_triggered/unknown；status见[AUDIT-no](#r-audit-no)/[AUDIT-incomplete](#r-audit-incomplete)/[AUDIT-awaiting](#r-audit-awaiting)/[AUDIT-block](#r-audit-block)/[AUDIT-ready](#r-audit-ready)；shadow_plans字段见[AUDIT-shadow](#r-audit-shadow)；正文与严格JSON同步；运行python3 scripts/validate_futures_audit.py --input research/futures/weekly/<date>/<date>-execution-audit.md，记录命令/退出码/实际结果，失败先修；未运行明示；信号席单列范围；不可自造枚举或fail/unknown混值；校验器不核经济逻辑/来源真伪/收益、不授许可；复核/解除：真实填值。

<a id="r-audit-shadow"></a>
**AUDIT-shadow**　影子计划登记、结算与归因；每周为最接近成立的至多两条候选（不论incomplete/awaiting_account/blocked）在JSON shadow_plans登记：shadow_id、candidate_id、instrument{single/spread，contracts 1/2个}、side、entry_type=limit/stop、entry/stop/target（多头stop<entry<target，空头相反）、entry_expiry、latest_exit_date、multiplier、round_trip_cost、带时区registered_at，上海日期须∈[as_of_date−7天, as_of_date]（事后补登记无效）、最晚退出日晚于登记日；登记后不改，同一shadow_id只认最早（改写由脚本点名忽略）；脚本§5结算规则：只用登记之后才开盘的已完成日线（日线含前一交易日21:00起夜盘）；限价按计划价成交，突破单取计划价与开盘价较差者；成交价已越过目标价→按成交价即时了结（只付成本）；成交当日只认止损（价差按当日结算价出场）；同日触及止损与目标按止损；跳空穿止损按开盘价；价差只用两腿结算价之差；过入场有效期未成交作废；最晚退出日或合约最后交易日先到者按结算价了结；缺价停止评估；已了结影子按登记时已核阻断归集人民币盈亏与R；一笔多阻断各计一次，非独立因果；无登记时避免损失/错过收益=null；一次涨跌/未交易不证明护栏有效；未算真实计划风险前不归因于5,000元上限；复核/解除：回溯重评标proposed_framework_reassessment，不假装当日生效。

<a id="r-audit-rule-review"></a>
**AUDIT-rule-review**　同一专业字段不可持续取得且重复拦截；连续两轮；复评公开替代或将该模型research_only结案，保留原机会/否决记录；错误数据/豁免/定义立即纠正；护栏命中数、连续空仓、一次踏空不证明有效或过严；不为凑手数放宽金额边界；复核/解除：同时比较避免亏损与错失盈利，不预设下周更新级别。

<a id="r-audit-gap-owner"></a>
**AUDIT-gap-owner**　适用检查unknown；gap.kind=definition/plan/calculation/raw_data/acquisition/not_published/account；附owner/next_action/due_at；definition/plan归research，calculation归data_pipeline；acquisition是已存在未取得；not_published须官方发布证据；治理deadline不是发布时间；可选背景不进unknown_checks；SC周settle→原油护栏，MA#30另用MA日settle/pre_settle及涨停；D8由脚本§2d计算、快照缺值归calculation缺口，gap_ratio未算归计划缺口；复核/解除：按具体下一动作补齐；账户归user。

<a id="r-audit-retraction"></a>
**AUDIT-retraction**　发现错年/未来时点/错口径；保留invalid旧行＋纠错记录；新证据另建ID；立即撤回触发并重算门/评分/系数/阻断清单/主状态/容量，列前后差异与仍有效独立冻结；替代未核则unknown；不能只换数留罚分；周度247家日均铁水不新增等下一周才撤错的门；无完整输入只列待办，不声称结果不变；复核/解除：schema 3隔离诊断引用与判定依据；来源年份/观测期/单位仍核原文，校验器不从URL断真伪。

## 2. 活跃品种与信号特例

<a id="r-card-ma"></a>
**CARD-MA**　MA仅已有A/E（已出清）/D路由；具体方向腿、#30腿及A双腿见[DYNAMIC-roll-table](#r-dynamic-roll-table)，方向腿剩余td<50按阶梯换月。驱动须对应月份，近强远弱不等买远月；库存/到港/装置/基差/仓单择合适一项，不要求全链。①未缓和时方向多头门槛+0.3、gap1.2并防追高；周五检视单边护栏，结构按A专属门。对应驱动/①/护栏改变后复评。

<a id="r-card-ma-week"></a>
**CARD-MA-week**　SC指定结算周涨>5%→MA方向多头加仓权×0.5、存量减50%；>8%→冻结清仓，取严不重复。完整结构豁免；周涨条件解除后重核。

<a id="r-card-ma-month"></a>
**CARD-MA-month**　原油月创近250日H→MA方向多头禁开并清仓；完整结构仍按A，高位条件解除后重核。

<a id="r-card-ma-inventory"></a>
**CARD-MA-inventory**　库存不去化/连续回升；港库未去化仅对以去化为依据的多头；连续2周回升；对应新开多头冻结；存量减仓50%；缺值不等未去化；国内结构可选其他真实产业证据，已知相关反证不忽略；复核/解除：库存恢复。

<a id="r-card-ma-price"></a>
**CARD-MA-price**　当前护栏腿见[DYNAMIC-roll-table](#r-dynamic-roll-table)。SC指定结算周涨=最新完成行情日对减7自然日及以前最近交易日（§2b“SC护栏结算周涨%”），不是AS_OF减7日或5交易日前；布伦特/WTI仅旁证。MA #30用指定腿settle/pre_settle，v1.16 §2b.1日/近5日结算列；缺列/端点→unknown，不以主力/SC/周涨替代。主力换月复核合约。

<a id="r-card-rb"></a>
**CARD-RB**　RB候选；A月差；方向性多头评估冻结，空头不在白名单；F/G冻结;禁方向单边；JM-RB休眠；复产只实际依赖才必要；铁水/盈利率为参考，不进必要验证、不记缺口；总库存去化≠旺季证真，需公开库存/现货同向；复核/解除：独立许可复评。

<a id="r-card-rb-manage"></a>
**CARD-RB-manage**　实际依赖的成本验证反向→减50%，月差收敛→了结；D14见[D14-restart](#r-d14-restart)/[D14-stock](#r-d14-stock)，结构仍须自身SL，铁水不触发处置。方向性历史存量周五减50%，需求证弱（公开库存）转已许可结构。提涨落地且同口径库存去化只支持原料主线研究；提涨受阻、钢厂减产/抵制或焦煤现货涨势中断，原料历史多头立即止盈；期货先于现货下跌按现货转弱侧处理。JM/J池外，不开放RB单边；D14仅对成案且依赖收缩假设的计划适用。

<a id="r-card-m"></a>
**CARD-M**　M备选，仅已有许可路线获行情确认＋USDA/作物进度/国内供需一项独立事实后评估；升级首期0.5，WASDE方向同向才考虑轻仓，不自动进入C。WASDE前2日禁新开、±1交易日gap1.3，限隔夜池横跨该事件周末须清仓（常规池不自动套用）；事件结束再核。南美天气/压榨/能繁仅增强，模型实际依赖时另核。

<a id="r-card-sr"></a>
**CARD-SR**　白糖备选；A/B路由＋产销/库存/交割供给等证据＋行情确认，升级首期0.5；B按[TRIGGER-B-window](#r-trigger-b-window)/[PLAN-B](#r-plan-b)；A/B评估；抛储多头降级；榨季初需产销率验证；连续2周回落减50%；月度值不外推周度，进口利润仅增强；复核/解除：证据恢复。

<a id="r-card-cf"></a>
**CARD-CF**　B季节窗＋独立证据后评估，升级首期0.5，计划见[PLAN-B](#r-plan-b)。内外棉价差>3年90分位须额外验证；轮储公告±3天暂停，公告后3日跌幅>1.5×ATR减50%；窗口/证据恢复后重核。

<a id="r-card-au"></a>
**CARD-AU** → [DYNAMIC-pool](#r-dynamic-pool)（同义锚）。

<a id="r-card-sc"></a>
**CARD-SC** → [DYNAMIC-pool](#r-dynamic-pool)（同义锚）。

## 3.1 当期配置（拟议框架状态，非交易许可）

<a id="r-dynamic-version"></a>
**DYNAMIC-version**　截至北京时间2026-10-11，方法整理v2.29（基于v2.28）；行情最后完成日2026-10-09，已提交的2026-10-10快照（AS_OF=20261010、行情脚本v1.16、末行“快照完成”）为行情锚。2026-10-11元研究、变化检测与原版执行审计按当时已生效v2.27完成；拟议框架待合并才生效，原审计不回写。脚本v1.17本期仅同步EVENTS配置与版本元数据，尚无新市场重跑；不得从版本号推导新行情。公开原文、原站AI摘要、交易所表转录与仅搜索结果按各自质量记录，账户/实际持仓/收益未知。

<a id="r-dynamic-caps"></a>
**DYNAMIC-caps**　用户2026-09-06配置参考净值150000元、常规单笔/组合预算5250元、低敞口固定封顶5000元；实际计算见[RISK-regime](#r-risk-regime)。当期15项适用触发及账户未全核，RISK_REGIME=unknown，#16不预判；portfolio_cap/portfolio_remaining/final_lots=null。normal/low_exposure可作标明的参考情景，不能填成实际占用或许可。

<a id="r-dynamic-pool"></a>
**DYNAMIC-pool**　核心MA2701/MA2705、RB2701/RB2703；备选M2701、SR2701/SR2705、CF2701；MA/M限隔夜，RB/SR/CF常规。能源仅MA、黑色仅RB月差；RB单边多头冻结、空头无白名单，M无具体许可策略（research_only）。AU2612/SC2611−SC2612仅信号，不因事件或预检改善建仓；AU用户不交易裁决不变。JM/J、AG、CU/AL、SI/PS、LC/LH、IM/IC、TL/T复活见§4。模型当前信号与缺口见[DYNAMIC-roll-table](#r-dynamic-roll-table)/[DYNAMIC-pending](#r-dynamic-pending)；专业旧子模型可得性依[DATA-feasibility](#r-data-feasibility)，一般地缘fade仍核①。

<a id="r-dynamic-frequency"></a>
**DYNAMIC-frequency**　默认周度；政策/事件密集时半周，已核事件T−3、公告±1及不可排期质变日按0.1/1.4缩至日级。10月可排期CPI/PPI/FOMC已核时区与国内T；交易所保证金恢复、其他未核节点不凭旧9月高密度簇续判低敞口。

<a id="r-dynamic-mult"></a>
**DYNAMIC-mult**　规格不变：MA/SR/RB/M乘数10、tick1、tick_value10；CF为5、5、25；AU为1000、0.02、20；SC为1000桶、0.1、100。价格与止损人民币换算、双腿成本及保证金须执行日核；AU/SC只信号。规格变化先同步正文和工具。

## 3.2 合约阶梯与准备对

<a id="r-dynamic-roll-ma"></a>
**DYNAMIC-roll-MA** → [DYNAMIC-roll-table](#r-dynamic-roll-table)（同义锚）。

<a id="r-dynamic-roll-rb"></a>
**DYNAMIC-roll-RB** → [DYNAMIC-roll-table](#r-dynamic-roll-table)（同义锚）。

<a id="r-dynamic-roll-agri"></a>
**DYNAMIC-roll-agri** → [DYNAMIC-roll-table](#r-dynamic-roll-table)（同义锚）。

<a id="r-dynamic-roll-signal"></a>
**DYNAMIC-roll-signal** → [DYNAMIC-roll-table](#r-dynamic-roll-table)（同义锚）。

<a id="r-dynamic-roll-table"></a>
**DYNAMIC-roll-table**　10/09行情；20日均量/剩余真实交易日按10/10完整快照，具体执行仍核[ROLL-direction](#r-roll-direction)、[ROLL-structure](#r-roll-structure)与[ROLL-target](#r-roll-target)。市场换月中位td不是硬触发。准备对不继承当前分位或计划，MA准备对样本按逐年历史33/31/31，两年31低于最低33且远腿20日量缺，temporary_gap；已完成的当前对A筛选不替代准备对验收。

| 品种 | 当前腿与筛选 | 20日均量 / 剩余td（10/09） | 首次触发#1 / 下一目标 | 执行边界 |
|---|---|---|---|---|
| MA（01/05/09；中位21td） | MA2701−MA2705，S+416、分位100、三年41/41/41；MA2701兼方向/#30/A近腿 | 724225/22566；67/146td | MA2701约12/17触#1或主力换月先到；方向腿<50td按阶梯选腿；准备对MA2705−MA2709 | 准备对33/31/31、MA2709量缺；当前对只是筛选，旧国内做空路线结案未复活 |
| RB（01/05/10；中位25td） | RB2701−RB2703，S+2、分位77.2≥70研究候选，<85高分位 | 706042/26351；68/104td | 近腿约12/18触#1或主力换月先到；准备RB2703−RB2705分位52.0仅取样 | 独立产业因果、前瞻自身确认和计划未齐；方向单边不开放 |
| M（01/05/09；中位25td） | M2701 | 1381405；68td | 约12/18或主力换月后核M2705 | 无具体已许可策略，不因WASDE排期/2ATR开放 |
| SR（01/05/09；中位24td） | SR2701−SR2705，S−77、分位0.0 no_signal | 418492/41396；67/146td | 约12/17或主力换月，下一对另验 | B-summer 9/30结束，日历no_signal |
| CF（01/05/09；中位23td） | CF2701，B-autumn窗口内 | 331489；67td | 约12/17或主力换月先到，核CF2705及备选CF2703 | 两腿20日量执行日复核，旧9/4值不得作当前#2；B历史/窗前低点/需求缺，具体模型temporary_gap |
| AU信号（02/04/06/08/10/12；中位18td） | AU2612 | 117089；46td | 约11月中旬核AU2702 | 用户不交易黄金，2ATR预检36608元/0手 |
| SC信号（逐月；中位9td） | SC2611−SC2612，back+22.9、分位100，5td−23.7 | 160486/35097；14/35td | 下次主力换月核SC2612−SC2701真实挂牌 | 信号腿不受#1/#2，不建仓；SC单合约OHLC/ATR unknown，专用结算周涨available |

## 3.3 状态与证据边界

<a id="r-dynamic-regime"></a>
**DYNAMIC-regime**　沿用既有①“中断证真”，尚无官方全面重开/停火＋SC back同向回落的反向共证；9月袭船不作本期新增事实。能源空头#26、各方向多头护栏与完整A豁免见[DYNAMIC-freezes](#r-dynamic-freezes)；Fed与D13见[DYNAMIC-CPI](#r-dynamic-cpi)，RB证据质量见[DYNAMIC-iron-sample](#r-dynamic-iron-sample)。交易所恢复条件/经纪商实收及RISK_REGIME未知，池外门休眠。

<a id="r-dynamic-cpi"></a>
**DYNAMIC-CPI**　美国10/14 CPI 08:30 ET→北京时间当晚20:30、国内T10/15；10/15 PPI 08:30 ET→T10/16；FOMC决议10/28 14:00 ET→北京时间10/29 02:00、国内T10/29，T−3=10/26、T−1=10/28、T+1=10/30。九月加息25bp至3.75–4.00%是历史已核事实；没有本期带采样时刻的FedWatch概率及同口径DXY/10Y周序列，后续逐会承诺与美元连涨中断均不可填。D13−0.3/×0.5/C门槛4.8及复归档“10/28按兵或转鸽＋美元连涨中断周度确认”原条件保留；AU仅信号，#29仅原适用AU/AG并按T−10核重入，不外推全池。

<a id="r-dynamic-iron-sample"></a>
**DYNAMIC-iron-sample**　Mysteel原站2026-10-07 AI摘要：螺纹产量170.27万吨/周−1.96，**五大材总库存**1548.44万吨/周+85.50（对9/30同系列），底层表未读，假期效应未分解；不是RB单品种库存，也不作D14硬fail。10/09螺纹137厂原文仅搜索线索、不能写已核。焦炭10/09第二轮提降仅发起/预期、落地未核；铁水/盈利率为参考。下一完整周同样本原表、前瞻价格确认及独立因果到位后复评RB A。

## 3.4 事件与当前护栏

<a id="r-dynamic-events"></a>
**DYNAMIC-events**　国庆10/01–10/07休市、10/08首个国内响应日、10/09第二日；9/30长假T−1及9/21、9/29公告±1窗均归档，不能续为本期已命中。10/04 OPEC+七成员维持11月产量目标（已读新华社正文，OPEC原声明未直读），目标配额不等于实际油流或①重开。USDA WASDE排期10/09 12:00 ET＝北京时间10/10 00:00，晚于M周五夜盘，首个可能国内响应日10/12；报告正文/大豆数字未核，拟议脚本仅window_only/auto=False人工提醒，不自动生成D12或新开禁令。俄禁令旧9/30到期报道/拟延期未取得本期官方法令，不作当前官宣质变。未来官方CPI/PPI/FOMC时间及国内T见[DYNAMIC-CPI](#r-dynamic-cpi)；不可排期①双向质变按0.1/1.4日度核。交易所节后保证金回落须实际满足非单边市等条件并核经纪商实收，未核不能自动解除×0.8或宣布仍命中。

<a id="r-dynamic-gap"></a>
**DYNAMIC-gap**　CPI/PPI与FOMC±1、地缘质变±2等按[GAP-active](#r-gap-active)/[GAP-latent](#r-gap-latent)取适用池；M的WASDE±1 gap1.3仍人工核，脚本window_only不自动生成D12/新开禁令；九月提前窗已到期。MA①未缓和期间gap上限1.2，受交易所扩板的历史压力场景不得代替本期实际合约涨跌停参数；AU信号/AG池外仅历史存量适用，SC信号不建仓。

<a id="r-dynamic-freezes"></a>
**DYNAMIC-freezes**　10/09行情已核：MA2701 10/08结算+7.26%、10/09+5.50%，#30顺向单边新开分别冻结3真实交易日；MA主力MA2611周涨+14.86%/上尾99.4，D8方向性多头否决；SC2611两端结算9/30 696.10→10/09 741.30，周涨+6.49332%命中MA多头>5%减50%/加仓权×0.5，未命中>8%冻结清仓。MA ATR分位94.8、M93.1、SR85.0高波；RB55.2常规、CF37.0/AU21.9低波；池内极差72.9>50错位，D12按实测逐品种及事件T−3，不由SC OHLC缺失抹去专用结算证据。#16因regime未知不预判，#26能源方向空头仍因①未缓和否决；完整1:1 A配对豁免单边D8/#30/D12/#16，但不豁免A证据、止损费用、双腿保证金及组合上限。实际账户与历史处置量unknown。

<a id="r-dynamic-deadline"></a>
**DYNAMIC-deadline**　9/12光伏调减数据硬截止后“无法核验”、光伏F腿新开中性冻结（非罚则、无叙事扣减、存量不动）属旧有效条件，SI/PS池外；数据到即按#23原条款裁决，不把旧9/18报价当本期事实。

<a id="r-dynamic-pv-date"></a>
**DYNAMIC-pv-date**　光伏能耗国标2027-01-01实施日期仅旧纳入口径链待核；不替代产能实际退出/调减达标，不授池外品种复活或新开。

## 3.5 待办与模型分层

<a id="r-dynamic-pending"></a>
**DYNAMIC-pending**　沿原审计/重评保留机会身份和gap.kind。MA domestic_public空月差10/03结案，复活须国内装置复产定量／到港回升／太仓或江苏同口径基差走弱至少一项，且冻结v1自身价格确认；两日S/H20未输出，temporary_gap。准备对缺项见[DYNAMIC-roll-table](#r-dynamic-roll-table)。隆众港库30.51万吨/周−8.84仅转引、观测日10/07或10/08冲突、原表未读，属optional_context，不代#5；99期货转录10/09郑商所仓单5316张/日−182，仅可交割供给，原表未读且注销/假期解释未除。RB待同品种同样本原表、自身确认及因果；CF待B-HISTORY、pre_window_low5、Entry_raw、需求和真实planned_exit；SR本轮A/B no_signal，M无许可策略research_only。全候选计划/实际账户持仓挂单/费用/保证金限仓未齐，final_lots=null。9/19两份MA影子均not_filled，不推真实成交或收益，不改事前门。

## 3.6 过度反应与脆弱叙事

<a id="r-dynamic-overreact"></a>
**DYNAMIC-overreact**　下列脆弱叙事不得代替许可。仓单不是港库、五大材不是RB单品种；不得将个人讲话外推委员会承诺。SR/CF/M状态按[DYNAMIC-pending](#r-dynamic-pending)，增强数据缺失不使全池incomplete。旧公告/长假风险窗不续为本期；单项护栏解除不解除其他门，结算命中不等实际账户已处置。

<a id="r-dynamic-narratives"></a>
**DYNAMIC-narratives**　按[PEN-narrative](#r-pen-narrative)对实际适用候选逐项扣0–3；历史/池外不进当前执行分母。证据与解除条件在所引条目，不重复抄录读数：

| 脆弱叙事 | 反证/边界及复评依据 |
|---|---|
| SC back收窄或OPEC+按兵＝官方重开、能源可空 | 目标配额不证油流；①反向要件未共证，见[DYNAMIC-regime](#r-dynamic-regime)/[DYNAMIC-events](#r-dynamic-events)，#26仍有效 |
| 9月加息＝逐会连续加息、贵金属必回吐 | 个人讲话不代委员会承诺；概率/美元同口径序列缺，D13仍待双条件，见[DYNAMIC-CPI](#r-dynamic-cpi)；AU只信号 |
| MA极端分位或仓单下降＝空月差确认 | 分位仅筛选，仓单有注销/假期解释；港库冲突及国内路线复活条件见[DYNAMIC-pending](#r-dynamic-pending) |
| 五大材节后累库＝RB单边空头或D14硬fail | 原站AI摘要非RB同口径原表；D14限成案且实际依赖假设，见[DYNAMIC-iron-sample](#r-dynamic-iron-sample)；RB空头无白名单 |
| 历史单日放量＝权益资金结构已修复 | 9/18成交/两融仅历史，②''不据此升级；IM/IC池外 |
| 池外自律锁价＝产能出清 | 自律不等不可逆退出，③/#23不变；SI/PS/AL/LC池外 |

旧“永久关闭/近月无限强”等仅历史注记，不入本期评分；新证据按原分数与许可范围复评。

## 4. 休眠模块查阅

仅在既有复活条件、明确许可或已核真实历史持仓使其适用时展开；本区保留原定义，查阅不授予交易许可。共用#1–#31及评分/风险定义仍在§1，池外门不纳入当前候选缺项。

### 4.1 休眠策略与计划

<a id="r-trigger-c"></a>
**TRIGGER-C**　仅AU/AG复活后，ADX>30＋MA同向＋dist>3%且全门通过才评估C；当前休眠。

<a id="r-trigger-fg"></a>
**TRIGGER-FG**　F须三重验证＋③＋现货；G须③先解锁，未过不打分，不由叙事档位绕门。

<a id="r-latent-h"></a>
**LATENT-H**　H复活且④全过：SL=贴水重新走阔+5pct或指数破前低；TP=贴水收敛至10%以下或换月。当前休眠，先核新门。

<a id="r-latent-jmrb"></a>
**LATENT-JMRB**　原料强成材弱结构复活；双焦收缩部分三验证＋成材需求证弱（铁水<230为参考，复活前用公开库存/现货基差重定义）；多JM空RB，名义价值配比；成材相对走强/收缩证伪为SL，目标或任一逻辑反向了结；不是A同品种1:1；JM未回池禁止；复核/解除：新池许可。

<a id="r-latent-curve"></a>
**LATENT-curve**　曲线当前挂起；利差精确值＋3年分位补齐且结构池复评纳入后重建计划。

<a id="r-latent-ps"></a>
**LATENT-PS**　PS回归复活；回池许可＋期现基差/月差、SMM库存产量、合约/广期所风控；过剩且现货反向为回归前提；收敛TP/反扩SL；③达标、强制限价/查处、自律实际成交守成本→检视了结；节点±1不新开；涨停或4%+脉冲后3日不建反向结构；未核方向/底线不得执行；复核/解除：许可重建。

<a id="r-latent-lh"></a>
**LATENT-LH**　生猪升水回归恢复；期现升水、能繁/出栏、合约参数齐；收储/疫病±3日暂停；空升水;現货追认SL；能繁加速去化证真须检视；与通用节点±1取适用更严；复核/解除：恢复候选全门。

<a id="r-latent-spread-screen"></a>
**LATENT-spread-screen**　休眠结构复活；分位≥70/≥85仅研究；开仓≥4.0、轻仓3.5-4.0、首期0.5、R≥2.5、30-60日参考；SC/PS/LH复活后另核方向/真实SL/完整计划；SC满配需另议；LC冻结期参数仅存档；复核/解除：完整计划。

<a id="r-plan-f"></a>
**PLAN-F**　③+三重+现货全过；远月收盘突破MA20；SL=Entry−2×ATR20或MA60取近者；TP1=Entry+2R；TP2前3日低点；仅远月；公告/自律/光伏外推不解锁；复核/解除：任一验证连续2周反向清仓；调减未达存量减50%；PPI内生性<40%连续2月或7-8月收窄兑现，相关远月减30%；新验证后复评。

<a id="r-plan-g"></a>
**PLAN-G**　③已解锁；矿端真实执行+三方库存连续2周去化+现货back;复产<~6975+需求门（公开库存；铁水≥230为参考）；收盘MA20/结构确认入；SL=Entry−2×ATR20或MA60取近者；TP1=Entry+2R；TP2前3日低点或现货弱/复产证真（铁水<230为参考）；无行为性替代；复核/解除：D14优先；60日或证伪退出。

<a id="r-plan-c"></a>
**PLAN-C**　AU/AG许可后；多Entry=max(H20+1tick,突破K高+1tick)；dist>3%、ADX>30、MA同向；SL=min(突破K低,Entry−2×ATR20,MA20−0.5×ATR20)；TP1=Entry+2R，TP2移动止损；周涨非前10%；空头#17；C仅AU/AG且当前休眠；复核/解除：模型重新许可。

<a id="r-plan-f-validation"></a>
**PLAN-F-validation**　F“三重验证”独立三项定义缺失，保留前置但不能判pass，必要定义缺失列incomplete；不得借G三项或自加库存周数。当前F冻结，须canonical补定义及许可后再核。

<a id="r-plan-h-params"></a>
**PLAN-H-params**　H恢复许可后；④后≥4.0＋收敛门；系数0.5；R≥2；至换月/收敛、交割周前退出；再按[LATENT-H](#r-latent-h)计划；当前休眠，不借换仓启用；复核/解除：许可与④通过。

<a id="r-plan-au-break"></a>
**PLAN-AU-break**　AU/AG历史管理引用；破位区间<4000；原文仅称纪律待命，未给具体动作；不据此自行发出交易指令；AU不交易/AG休眠，真实历史持仓仍核[MANAGE-AU](#r-manage-au)与[MANAGE-stop](#r-manage-stop)；复核/解除：需要时先明确缺失动作。


### 4.2 休眠专属门与存量管理

<a id="r-gate-equity"></a>
**GATE-equity**　资金面企稳；两融止跌+上市无踩踏+跌停收敛；#28解除；仅商品背景;不等持续流入；复核/解除：官方两融证伪重新冻结。

<a id="r-gate-policy"></a>
**GATE-policy**　政策投放形式/实质；文件+清单+成交2万亿;风格/持续成交/指数；未实质过×0.5+上限4.0；池外休眠；复核/解除：一至两周第二读数。

<a id="r-gate-carry"></a>
**GATE-carry**　H年化贴水≥20%且10日收敛≥3pp才评估，再不满足即停新开；用远季同口径，新旧腿不可直比；当前休眠。

<a id="r-gate-cu"></a>
**GATE-CU**　CU back重入须同口径连续去库＋月份对齐才恢复⑤，不绕池门；仍池外则归档。

<a id="r-d13-cost"></a>
**D13-cost**　宏观压制有效时常态−0.3、C门槛+0.3、升级线−0.5、预算×0.5；独立事件项仍叠加，归档条件全过才解除。

<a id="r-d13-freeze"></a>
**D13-freeze**　加息对半/落地；事件裁决；复归档冻结；不是永久禁多；复核/解除：美元承压/连涨中断周度确认＋FOMC后宏观退出主导；转鸽重启归档评估，加息冻结重写，按兵鹰派延续待裁决。

<a id="r-d15"></a>
**D15**　carry双杀等状态；未过④=0;双杀−0.5~-1;不明−0~-0.3；减半/对冲/清仓/轻仓；当前休眠；复核/解除：④过且指数稳不扣。

<a id="r-manage-d9"></a>
**MANAGE-D9**　流动性扩张转中性/收缩→C减30%/50%，恢复后复评；当前C休眠。

<a id="r-manage-au"></a>
**MANAGE-AU**　经核AU/AG历史仓：盈利>2R不锁1R，>3R锁2R，>4R锁3R，退出结束；当前信号/休眠不授新开。

<a id="r-manage-dormant"></a>
**MANAGE-dormant**　池外模型复活或真实历史持仓核实；CU/AL跨周末对冲或降至30%风险预算；JM/J单边周五降至50%；SC/PS/LH激活首期周五减半；对应适用事件/节点前处置；PS/LH/SC节点±1不新开，LH专属±3取严；不凭旧持仓文字执行；池外模型不自动复活；复核/解除：许可与实际持仓核实。

<a id="r-manage-cu"></a>
**MANAGE-CU**　已核CU back存量到TP分位、⑤整体口径转累库或结构滚动退出日，先到即了结；转累库立即了结。当前休眠，无核实存量不执行。

<a id="r-gap-latent"></a>
**GAP-latent**　休眠板块恢复：IM/IC 1.3/1.8，权益重大事件/美股单日跌>4%/双杀→1.2；TL/T 1.2/1.5；JM/J 1.5/2.0，山西复产公告±2日→1.3（铁水仅参考）；AU/AG 1.5/2.0，地缘±2/D12→1.3；CU/AL 1.5/2.0，地缘/宏观窗口→1.3；SC 1.3/1.8，地缘质变±2→1.2；PS 1.3/1.8，deadline/行业文件±2日→1.2；LH 1.5/2.0，收储/疫病±2日→1.3（与新开暂停±3日分别核）；SI脉冲日必平，无gap表。复活时按[GAP-definition](#r-gap-definition)及当期日历重核；金银窗口见[DYNAMIC-gap](#r-dynamic-gap)，TL/T裸腿受限；SC信号不执行，池外不影响当前候选。


### 4.3 池外复活条件

<a id="r-revive-commod"></a>
**REVIVE-commod**　JM/J/AG/CU/AL恢复；JM：账户/预算变更且ATR回落使一手≤预算后重议；AG：随AU同评估、不作替代；J：远腿量≥1万手且一手≤预算；CU：结构池复评＋⑤复权＋一手≤预算；AL：D13归档＋独立电解铝/氧化铝驱动＋完整计划风险核验；先按[POOL-scan](#r-pool-scan)入备选，不自动开仓；不自动建仓；复核/解除：列明条件齐。

<a id="r-revive-lc"></a>
**REVIVE-LC**　新一轮同口径去库≥4周＋现货企稳＋排产收缩全证后恢复候选、首期从严；需求型不代供给型，冻结期双向不开。

<a id="r-revive-finance"></a>
**REVIVE-finance**　IM/IC/TL/T；IM/IC账户规模或RISK_BUDGET变更后评估；TL/T利差补齐＋结构池复评；先核池许可再重建计划；不以方向清楚或旧2ATR数字证明本期容量；复核/解除：各条件齐。

<a id="r-revive-structures"></a>
**REVIVE-structures**　池外结构复活；SI/PS：第三份文件/调减数据落地、③证真时复查先备选；LH：期现升水补全＋一手≤预算；SC须另行池许可；数据/独立模型/交易性/专属节点全部核验，按A明确计划；原模块数据齐不自动激活；复核/解除：全部门过。

<a id="r-revive-si"></a>
**REVIVE-SI**　SI空头恢复；周涨近3年前20%、ADX<22、利多price-in、基差/库存/利润三链反向；政府或自律完全成本底（自律覆盖90%产能）；触及成本底则沽空逻辑失效、从严并政策逆风×0.5；涨停/4%+脉冲后3日不追空、节点±1不新开；JM/J反弹做空不开放；RB空头不在白名单；旧原料评估冻结解除关注提涨受阻/钢厂减产仍不绕池许可；复核/解除：规则/数据齐。
