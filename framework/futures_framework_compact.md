# 期货交易分析框架 v2.28 · 精简版

## 0. 决策链总览

许可与路由 → 行情快照 → 当前状态/真实事件日历 → 资料及合约验收 → 适用性与硬门 → 策略触发 → 固定分母评分 → 有效计划/真实容量 → 经核实持仓管理 → 执行审计、影子结算与归因。

固定层 §1 按上述次序使用；品种特例仅覆盖差异（§2）；日期、池成员、已定事件安排及旧行情快照单列 §3。执行数据缺失保持 unknown/null，账户核验后置。先核适用性；unknown 不是 fail；数据可得性不等研究完成度；参考级数据不进门、不记缺口。所有金额为人民币，规则中的日期偏移按事件口径与真实交易日历核验。

本文件是[完整版](futures_framework.md)的精简表达，保留全部 277 个稳定规则锚及 #1–#31、①–⑤、D8–D15 标识。条目保留触发、参数、动作、例外与解除条件；箭头表示同一规则的别名，不新增条件。执行判据在本文件内，未定义边界保持缺项；不以压缩为由补造或删去许可、评分、审计、影子结算及休眠复活能力。取证细节见[数据协议](FUTURES_DATA_PROTOCOL.md)。当期状态统一见 §3，后续研究须重新核验。

## 1.1 池许可与路由

<a id="r-pool-core"></a>
**POOL-core**　核心执行品种；#1/#2/#31及驱动窗口；周度全量维护且四门齐备；例外：信号不建仓；解除/更新：退出依用户/池规则。

<a id="r-pool-backup"></a>
**POOL-backup**　独立备选；独立供需证据;首期0.5；升级核心前只维护0.2/卡；例外：不拼故事凑仓位；解除/更新：独立证据齐才升级。

<a id="r-pool-signal"></a>
**POOL-signal**　信号席；不建仓；仅指标/门输入；例外：不按方向触发建仓；解除/更新：用户另议。

<a id="r-pool-scan"></a>
**POOL-scan**　周度扫描；独立驱动+#1/#2+2ATR参考容量；先入备选；例外：#31须完整计划;用户排除优先；解除/更新：所列复活条件。

<a id="r-pool-sleep"></a>
**POOL-sleep**　品种池外；不参与当前判断；模块/门/乘数/必刷休眠；例外：商品侧背景保留；解除/更新：对应品种复活。

<a id="r-route-near"></a>
**ROUTE-near**　近月；事件/现货/已出清叙事；不承载远月政策预期；例外：结构除外；解除/更新：重分类须证据。

<a id="r-route-far"></a>
**ROUTE-far**　远月；A输入/F产能性；政策公告不加权；解除/更新：门通过。

<a id="r-route-structure"></a>
**ROUTE-structure**　完整结构配对；完整两腿；豁免横跨/单边D12/#16/#30/MA方向性护栏；例外：组合风险/费用/专属门不豁免;裸腿按单边；解除/更新：失去配对即撤销豁免。

<a id="r-data-authority"></a>
**DATA-authority**　执行及调研使用；canonical规则/评分；协议取证；模板schema 3（schema 2仅旧版历史）；脚本仅输入，行情实测读[DATA-snapshot](#r-data-snapshot)，参考级数据见[DATA-reference](#r-data-reference)；0D覆盖旧全量必刷/条款一字不改/旧优先级；change-analysis与adaption只读canonical；例外：不以旧市场叙事或未完成研究证明护栏有效；解除/更新：已确认错误立即撤回对应触发，不受反摇摆拦截。

<a id="r-pool-independent"></a>
**POOL-independent**　P/Y/OI等未入池独立候选；另行走候选纪律；不借C池白名单入池；例外：BU/EC不入池；未获池许可不计算成执行候选；解除/更新：独立证据及明确入池许可。

## 1.2 状态与事件日历

<a id="r-cal-lookahead"></a>
**CAL-lookahead**　拟开/加仓；未来10交易日；核事件清单并填写完成；例外：未完成不可填完成；解除/更新：完成真实核验。

<a id="r-cal-cross"></a>
**CAL-cross**　横跨未落地事件；T-1；计划对冲/减仓；例外：只用许可工具；解除/更新：落地后复评。

<a id="r-cal-day"></a>
**CAL-day**　事件新开限制；节点±1；核专属门；例外：换月为机械节点仍须核；解除/更新：各事件窗口退出。

<a id="r-reg-trigger"></a>
**REG-trigger**　15类低敞口适用触发任一命中；[REG-set](#r-reg-set)任一当前适用触发；组合cap见[RISK-regime](#r-risk-regime)；只应用一次金额封顶；逐项记录有效触发；例外：池外交易门休眠；不将低敞口塞入单笔乘数；解除/更新：全部有效触发复评解除。

<a id="r-reg-tail"></a>
**REG-tail**　地缘/权益夜盘风险；周五前；敏感品种对冲/减仓；例外：许可工具限制；解除/更新：风险消失并复评。

<a id="r-reg-correlation"></a>
**REG-correlation**　再校准且依赖跨资产对冲；无相关性保护；重新核对冲有效性；例外：不以不足样本依赖；解除/更新：完成相关性验证。

<a id="r-reg-exchange"></a>
**REG-exchange**　提保/限仓公告；±1日;门槛+0.3；当日检视占用；例外：仅受影响品种；解除/更新：公告退出。

<a id="r-cal-timestamp"></a>
**CAL-timestamp**　事件窗口计算；released_at带时区→北京时间→domestic_trade_date→首个可交易时刻；按真实交易日算T−n；周五夜盘归下一交易日，收盘后发布从下一可交易时刻响应；例外：会议起始日非决议T；不同品种时段分开；解除/更新：官方日历/交易时段核实。

<a id="r-state-density"></a>
**STATE-density**　状态枚举判定；高密度簇=两周内≥2离散催化；能繁稳定<3750＋仔猪同比降；ppi_attribution内生性>60%/混合/输入性>60%；仅实际相关模型核对；缺可选精确比例不猜不罚；例外：不把矩阵未填当中性或已过门；解除/更新：当期证据。

<a id="r-reg-set"></a>
**REG-set**　低敞口触发清点；15项：①宏观T−1未对冲金融/准金融单边；②能源结算脉冲#30；③carry双杀；④高密度簇且当周有未落地催化；⑤政策密度高且当周≥2节点未落地；⑥流动性收缩；⑦地缘/权益夜盘跳空风险；⑧波动升档且T−3；⑨收缩证伪D14；⑩创新高且周涨前10%；⑪提保/限仓公告±1；⑫ATR池内极差>50且未当日重校准；⑬地缘质变日及次日；⑭相关性再校准且依赖跨资产对冲；⑮#28重新冻结监控；分别执行对应门及组合封顶；解除须复核全部仍有效触发；例外：触发源本身的参数定义只见#30/D12/D14等；休眠项不参与当期；解除/更新：全部有效触发经状态复评解除。

<a id="r-reg-geop"></a>
**REG-geop**　地缘双轴任一质变；霍尔木兹停火或正式重开官宣、正式关闭、扩大打击或再袭船·布雷；俄乌停火、柴油禁令官方延期/扩至汽油或解除、更大规模打击；当日及次日方向性单边新开冻结，双向跳空预案；MA结构依专属±1另核；例外：通行量实测为参考，不构成质变形态；旧9/30拟延期报道未核本期官宣，不是新增方向许可；已执行旧事件不无新证据续冻；解除/更新：当前质变窗口退出并复核其他触发。

## 1.3 资料、合约与换月

<a id="r-roll-days"></a>
**ROLL-days**　所有交易腿；真实trade_cal;20日均量；按真实交易日核#1/#2；例外：单日量不代均量；解除/更新：每次更新。

<a id="r-roll-direction"></a>
**ROLL-direction**　方向性执行腿；剩余td≥20+持仓上限;D≥50td；选阶梯最近符合月份；例外：信号/结构有各自规则；解除/更新：换月再核。

<a id="r-roll-structure"></a>
**ROLL-structure**　结构近腿触红线或主力换月；<20交易日或换月先到；整对退出/重建；例外：取消旧换月前15日重复规则；解除/更新：新对全部门重核。

<a id="r-roll-plan"></a>
**ROLL-plan**　计划开仓；public_data优先5–20交易日；30–60日仅旧参考；写最短/最长持有期和最晚退出具体日期；预计退出须覆盖最短持有期；例外：不满足仅否决该具体计划；不得静默缩期或声称全部目标不可达；解除/更新：窗口足够的新计划。 近腿红线或主力换月；近腿触#1或主力换月，先到为准；按[ROLL-plan](#r-roll-plan)核期限，结束原计划并全套重建；例外：不增加旧“换月前15日”重复退出，不继承旧许可；解除/更新：新对合格。

<a id="r-roll-target"></a>
**ROLL-target**　更换目标腿；两腿#2；未过退最近可过月份并降级标注；例外：SC信号#1/#2豁免；解除/更新：均量过门。

<a id="r-roll-timing"></a>
**ROLL-timing**　写死日期或fut_mapping主力换月；先到;触发前3交易日；生效不等周报;旧单边新开从严；例外：信号有专门节奏；解除/更新：执行换月。

<a id="r-roll-reset"></a>
**ROLL-reset**　换月；新合约对原有历史按[INPUT-spread](#r-input-spread)验收；回填0.2并重建样本、方向、SL/TP与许可；不把分位设0，不设额外观察期；例外：不继承旧计划；不要求换月后再等41天；解除/更新：新对完成计算且全门通过。

<a id="r-roll-sc"></a>
**ROLL-SC**　SC信号滚动；近12月逐月;更远按季；主力-次月;不存在月取下一实际挂牌月；例外：不建仓故#1/#2豁免；解除/更新：维持信号定位。

<a id="r-pre-preview"></a>
**PRE-preview** → [0.3#31](#r-gate-31)（同义锚）。

<a id="r-input-price"></a>
**INPUT-price**　行情输入；SMA；ATR-Wilder(20)；ADX-Wilder(14)；HV年化(20,60)；ATR近250日分位；一般研究结算缺失可标price_basis后回退close；例外：SC周涨/MA#30指定结算不得回退；指标错误不抹去有效结算端点；解除/更新：真实数据。

<a id="r-input-spread"></a>
**INPUT-spread**　输入B；过去3年同月合约对，各年目标日±20交易日，期望41、至少33（80%向上取整）个有效唯一同日两腿样本；按实际有效原值算分位；40/41仅警示；不足33/缺年/重复/非法日期/不可核同对→incomplete；例外：不补值、不缩年数/窗口；换月可回溯已有历史，不自动等41天；不保证独立或显著；解除/更新：原标准样本验收完成。

<a id="r-input-status"></a>
**INPUT-status**　spread状态；≥+0.3/≤−0.3%/其他；B/C/F结构描述；例外：非交易方向；解除/更新：行情变更。

<a id="r-input-scope"></a>
**INPUT-scope**　脚本范围；MA/RB/SR+SC;股指国债停用；池内采样；例外：参数per_unit交叉核；解除/更新：复活先加配置。

<a id="r-input-manual"></a>
**INPUT-manual**　人工必需项；行情合约＋每候选一项合适独立公开产业事实＋公告日历；已有行情负责可计算指标；终端同口径导出可替代；交易前另核账户、价格、费用、保证金限仓与压力；例外：库存/利润/开工/基差是菜单非全链；专属因果模型仍核自己的必要数据；池外停日常补采；解除/更新：字段核实。

<a id="r-input-state"></a>
**INPUT-state**　状态填写；密度≥2/2周;能繁<3750;PPI>60%；按实际适用证据填状态，不预填旧结论；例外：能繁<3750＋仔猪同比降只相关模型；PPI精确归因缺失不猜；背景不传染全池；解除/更新：证据更新。

<a id="r-data-feasibility"></a>
**DATA-feasibility**　判断资料是否持续可得；available / temporary_gap / research_only；与候选status独立；专业数据长期不可持续的模型research_only，列排除范围/复活条件；例外：已有许可新对未计算/模块失败/导出缺列=temporary_gap；最低研究资料齐备可available，即使反证/未成案/账户未知；解除/更新：专业模型所需证据恢复后复评；不传染全池。

<a id="r-data-snapshot"></a>
**DATA-snapshot**　行情/D8/影子结算输入；最新提交的 research/futures/snapshots/<AS_OF>-data-snapshot.txt（本地已配 TUSHARE_TOKEN 运行 scripts/future_data.py，脚本自行写入含 stderr 的完整输出，末行“快照完成”为完整标记；云端流水线不跑脚本）；各阶段先读快照并记录其 AS_OF、脚本版本与最新行情日；例外：快照已有实测值不得用推算、旧快照或叙事替代；解除/更新：无快照、缺完整标记或快照最新行情日落后于应有最近已完成交易日→受影响项 temporary_gap 并写快照日期。

<a id="r-data-reference"></a>
**DATA-reference**　参考级数据；Kpler 油轮通行量/海湾出口量/战争险费率、247 家钢厂日均铁水/钢厂盈利率等流水线不可持续取得的专业数据；只作参考旁证；例外：不进任何门、不触发扣分/系数/冻结/收紧，缺失不记 unknown/temporary_gap、不列补核必办；①门量化锚=脚本§1 SC 近端 back 方向（[GATE-calm](#r-gate-calm)/[GATE-resume](#r-gate-resume)），黑色需求侧证据=公开周度库存/产销/现货；解除/更新：依赖它们的休眠模型（[LATENT-JMRB](#r-latent-jmrb)、[PLAN-G](#r-plan-g)需求门）复活前须用公开数据重定义触发。

<a id="r-data-fields"></a>
**DATA-fields**　输入有缺失或模块失败；未计算/计算失败/原始字段缺失分别记录；SC结算端点独立于OHLC/ATR/ADX；分别输出缺失字段、计算错误与指标状态；例外：整行NaN或接口失败不证明所有字段缺失；close不得满足结算护栏；解除/更新：原字段或计算链修复。

<a id="r-data-lineage"></a>
**DATA-lineage**　采用产业/概率证据；完整年份、观测日、原发布者/转引者、单位、比较期；库存另列地域/样本/是否含下游工厂；同一对象时点口径才判conflicting；不同日期先作序列；例外：区域库存/仓单不代港库/社会库存；反证某假设不证明反向可交易；解除/更新：FedWatch补目标会议、利率区间、采样时刻；旧读数不拼当前概率。

<a id="r-data-quality"></a>
**DATA-quality**　适用门拟判pass/fail；必要证据missing/stale/conflicting/invalid；必要证据不可用不能作已核依据；必要未知分列unknown_checks，无效行仅诊断引用；例外：可选背景缺失不阻断；解除/更新：有效证据齐后复核。

<a id="r-input-preparation"></a>
**INPUT-preparation**　换月准备；current与preparation分列，具体当前对/准备对见[DYNAMIC-roll-table](#r-dynamic-roll-table)；同对去重；逐对输出样本/缺项/research_stage；例外：取样不提前更改执行腿，也不授许可；失败不抹去其他对结果；解除/更新：日期或主力先到依阶梯生效并同日互换配置。

## 1.4 硬否决（#1–#31）

<a id="r-gate-1"></a>
**0.3#1**　距最后交易日不足；<20交易日；本交易腿否决/滚动；例外：不建仓信号席不受#1；解除/更新：换月至满足期限的新腿。

<a id="r-gate-2"></a>
**0.3#2**　20日均成交量不足；<1万手；交易腿否决；例外：不建仓信号席不受#2;单日放量不代20日均量；解除/更新：新腿/新均量达到门槛。

<a id="r-gate-3"></a>
**0.3#3**　先判断各precheck是否为本模型实际依赖；适用门fail/unknown分别记录；已核失败阻断该模型；必要未知incomplete，并保留其他已知阻断；例外：domestic_public不继承①未知；自身国内论证未知仍incomplete；实际依赖地缘改走geopolitical_fade；解除/更新：缺项补齐且全部适用门通过。

<a id="r-gate-4"></a>
**0.3#4**　同品种横跨近远月的方向性单边；同一品种近/远两层；否决横跨；例外：结构对冲/价差除外；解除/更新：改为合规单层或获许可的完整结构。

<a id="r-gate-5"></a>
**0.3#5**　许可模型的最低验证；价格/结构确认＋至少一项独立产业事实，两类同时成立；价格与产业拆成两项检查；已核失败列fail，定义/必要观察未知列unknown，不能混值；例外：同价格多个指标/同源转载不算独立；专门模型仍保留强因果验证，旧周度≤2项/月度≤1项不作public_data通用门；解除/更新：两类均过且专属验证满足。

<a id="r-gate-6"></a>
**0.3#6**　交易赔率不足；普通R<2或A的TP1净R<2.5则计划失败、否决；A按真实成本后净R而非毛R；解除/更新：有效计划达到相应R。

<a id="r-gate-7"></a>
**0.3#7**　gap_ratio超过板块阈值；1.2板块表及收紧值；按轻仓/淘汰阈值处理；例外：信号/休眠范围见池规则;数据未知不可臆填；解除/更新：风险输入与事件窗口重新核验。

<a id="r-gate-8"></a>
**0.3#8**　结构支持评分最低；结构支持=1；否决；解除/更新：结构支持重新验证通过。

<a id="r-gate-9"></a>
**0.3#9**　拟建仓触及交易所限仓未降；限仓额度80%；降至以内;无法满足淘汰；例外：两腿容量分别扣现仓/挂单后取小值；解除/更新：足够新增限仓容量。

<a id="r-gate-10"></a>
**0.3#10**　受提保/限仓覆盖而未折减；缓冲系数×0.8折预算金额，未折减不予开仓；例外：非受影响品种不适用，同源只一次，组合上限另核；解除/更新：按实际措施折减或公告退出。

<a id="r-gate-11"></a>
**0.3#11**　④未过新开H或存量双杀无对冲过夜；④未过/双杀；禁止新开或减仓/不新开；例外：H及④/D15当前池外休眠；解除/更新：复活后④过且完整风控满足。

<a id="r-gate-12"></a>
**0.3#12**　国债曲线利差未补全进入执行；利差精确值及分位缺失；禁止执行；例外：曲线当前挂起;复活前置保留；解除/更新：数据补齐且结构池复评纳入。

<a id="r-gate-13"></a>
**0.3#13**　A/结构两腿关键价格序列及同期样本核验；[INPUT-spread](#r-input-spread)样本标准；缺项/未计算/质量不合格为incomplete、unknown；新对未计算不是first_blocker；已核其他模型否决标准失败另列fail；例外：A豁免D8；可选专业背景缺失不否决；休眠模型先复活；解除/更新：序列补齐并过全部候选门。

<a id="r-gate-14"></a>
**0.3#14**　G单边多头产能性判决未证真；③未通过；禁止G新开；例外：行为性/安监/deadline/制度立法/自律/光伏纳入口径均不解锁黑色；解除/更新：③对应行业产能性证真。

<a id="r-gate-15"></a>
**0.3#15**　收缩证伪时双焦/RB多头未减；山西复产达产/超预期；减至×0.5或清仓;RB转合格结构；例外：铁水<230为参考不触发本条；结构另按D14检视;休眠价差不能承接；解除/更新：持仓降至合规或证伪状态更新。

<a id="r-gate-16"></a>
**0.3#16**　低敞口限隔夜方向性单边新开；regime低敞口；否决；例外：完整配对结构豁免本项但不豁免组合cap;裸腿按单边；解除/更新：低敞口全部触发复评解除。

<a id="r-gate-17"></a>
**0.3#17**　AU/AG/CU/AL空头入场；四个明确品种；否决；例外：当前信号/休眠不借信号改善开空；解除/更新：本次未新增解禁路径。

<a id="r-gate-18"></a>
**0.3#18**　事件脉冲品种政策脉冲日隔夜；政策脉冲日；日内必平不得隔夜；例外：其他日按其余规则；解除/更新：脉冲日结束后另核许可。

<a id="r-gate-19"></a>
**0.3#19**　政策脉冲日限隔夜池新开；政策脉冲日；否决新开；例外：常规隔夜池仍核自身政策日规则；解除/更新：次日核③/事件与品种门。

<a id="r-gate-20"></a>
**0.3#20**　创新高且单周涨幅极端的多头新开；近250日H且近3年周涨上尾前10%（[D8-definition](#r-d8-definition)，脚本§2d）；否决新开；例外：已有持仓不因本项强平；解除/更新：任一机械要件消失即本项解除。

<a id="r-gate-21"></a>
**0.3#21**　金融属性多头极端周涨再追加；周涨上尾前5%分位（[D8-definition](#r-d8-definition)）；禁止追加；例外：已有持仓按管理规则；解除/更新：分位退出且其余门通过。

<a id="r-gate-22"></a>
**0.3#22**　跳空敏感品种跨周末未对冲且单仓风险超额；单仓计划止损风险>RISK_BUDGET×30%；周五前降至金额以内或清仓；例外：金额非保证金/名义价值；与组合cap取严；结构按适用性；账户配置非实际净值；解除/更新：持仓降至金额内/有效对冲核验。

<a id="r-gate-23"></a>
**0.3#23**　政策调减判决前/未达标/到期缺数；未达标叙事扣1.5；到期安排见[DYNAMIC-deadline](#r-dynamic-deadline)；公告/deadline/制度文件不解锁或加权；已核未达标冻结F新开并扣分；截止前缺数据pending，截止后无法核验仅光伏F新开中性冻结；例外：无数据不等未达标；中性处置无罚分、存量不动；解除/更新：可核数据到位即按原达标/未达判决;不得静默顺延。

<a id="r-gate-24"></a>
**0.3#24**　品种专属否决命中；1.5品种卡专属条件；与0.3同效力否决；例外：各品种特定适用范围；解除/更新：依品种卡解除。

<a id="r-gate-25"></a>
**0.3#25**　方向性单边未过当日ATR重校准；当日核验未完成/未通过；不得隔夜;日内了结或对冲；例外：结构豁免单腿ATR但保留自身SL/组合cap；解除/更新：完成当日有效核验。

<a id="r-gate-26"></a>
**0.3#26**　能源方向性空头或依赖地缘缓和的结构；①≠缓和证真;fade还须结构确认；①未缓和证真禁止方向性空头新开；geopolitical_fade必须①与结构确认，中断评估期不适用；例外：domestic_public独立国内回归按[A-reversion](#r-a-reversion)论证；两路线均保留质变±1和压力门，不借改名绕门；解除/更新：①缓和证真后解除评估并核结构确认。

<a id="r-gate-27"></a>
**0.3#27**　近月政策多头现货门未过；基差/库存/现货价至少两项同向未达；否决；例外：远月F仍三重验证+③而非豁免；解除/更新：独立现货验证达标。

<a id="r-gate-28"></a>
**0.3#28**　官方两融证实未实际回升；已解除后的重新冻结条件；恢复IM/IC新开否决及企稳验证中状态；例外：IM/IC当前池外本交易门休眠;资金背景保留；解除/更新：官方口径及②'门重新证真。

<a id="r-gate-29"></a>
**0.3#29**　利率事件二元状态经复评重入；T−10复评重入；T−3至T+1冻结；AU/AG方向性双向新开冻结；例外：只作用AU/AG方向性；本期提前窗见[DYNAMIC-freezes](#r-dynamic-freezes)，不得扩为全池D12或解除池许可；解除/更新：T+1按结果归档或延续。

<a id="r-gate-30"></a>
**0.3#30**　能源主力单日脉冲后顺向单边新开；结算涨跌幅≥5%;后3交易日；否决顺该方向新开；例外：双向对称;完整结构不受;空头另#26;MA周涨取严；解除/更新：3日窗口结束且其他门通过。

<a id="r-gate-31"></a>
**0.3#31**　真实计划/成本/账户/系数/容量核验；风险容量<1或保证金/限仓容量<1;缺项null；完整零容量记录阻断;必要未知incomplete；例外：2ATR仅扫描;结构用真实失效SL;不为手数窄SL;池排除优先；解除/更新：完整有效计划且全部适用门/容量通过；脚本2ATR参考量不是最终手数。

## 1.5 Precheck 与软前置

<a id="r-soft-d12"></a>
**SOFT-D12** → [D12-trigger](#r-d12-trigger)（同义锚）。

<a id="r-soft-ma"></a>
**SOFT-MA** → [CARD-MA](#r-card-ma)（同义锚）。

<a id="r-soft-chain"></a>
**SOFT-chain**　基差库存利润背离；软前置；扣分并降系数；例外：不一律×0；解除/更新：链一致恢复。

<a id="r-soft-lowadx"></a>
**SOFT-lowadx**　低ADX且无窗口事件；ADX<20；观望；例外：A/D/E/F/G解锁/结构候选除外；解除/更新：触发独立策略。

<a id="r-soft-beta"></a>
**SOFT-beta**　再校准权益beta方向多头；门槛+0.3；优先对冲；例外：结构豁免；解除/更新：相关性恢复。

<a id="r-gate-calm"></a>
**GATE-calm**　地缘fade评估；名义解除/正式重开（官方）+SC近端back回落同向（脚本§1）；缓和证真后结构确认才评估；例外：通航量/战争险为参考旁证不作要件；谈判headline不构成裁决；仅geopolitical_fade等依赖该因果模型必填；收入分成协议不算重开；国内独立回归按[A-reversion](#r-a-reversion)；解除/更新：任一反向质变回中性。

<a id="r-gate-resume"></a>
**GATE-resume**　中断证真评估；正式关闭/再袭船或布雷（官方或多源headline）＋SC近端back反弹（脚本§1）；全过→中断证真、回事件冲击模式；不恢复已存档的建仓许可；例外：通行再受阻/海湾出口下降为参考不作要件；headline不代back方向；解除/更新：反向质变回僵局/缓和。

<a id="r-gate-long"></a>
**GATE-long**　僵局单边多头；仅具体护栏生效范围；逐项核而非永久禁止；例外：空头#26;结构fade仍①；解除/更新：冻结期过后重核。

<a id="r-gate-equity"></a>
**GATE-equity**　资金面企稳；两融止跌+上市无踩踏+跌停收敛；#28解除；例外：仅商品背景;不等持续流入；解除/更新：官方两融证伪重新冻结。

<a id="r-gate-policy"></a>
**GATE-policy**　政策投放形式/实质；文件+清单+成交2万亿;风格/持续成交/指数；未实质过×0.5+上限4.0；例外：池外休眠；解除/更新：一至两周第二读数。

<a id="r-gate-capacity"></a>
**GATE-capacity**　产能性评估；不可逆退出/纳入口径+调减达标+公开库存同向；对应品种解锁评估；例外：钢厂盈利率/247家铁水为参考；行为性/政策公告/自律不解锁;池外先备选；解除/更新：数据判决#23。

<a id="r-gate-carry"></a>
**GATE-carry**　H重启评估；年化≥20%;10日≥3pp收敛；H评估；例外：远季口径;新旧不可直比;当前休眠；解除/更新：再度未过停止新开。

<a id="r-gate-cu"></a>
**GATE-CU**　CU back重入；同口径连续去库+月份对齐；恢复⑤；例外：不能绕池门；解除/更新：CU仍池外则归档。

## 1.6 策略触发与参数

<a id="r-trigger-b"></a>
**TRIGGER-B**　季节策略；[TRIGGER-B-window](#r-trigger-b-window)定义的窗口内或前20交易日；仅研究筛选；完整开仓另核[PLAN-B](#r-plan-b)与各适用门；例外：须品种证据与许可；解除/更新：窗口结束；新定义仅前瞻。

<a id="r-trigger-c"></a>
**TRIGGER-C**　趋势策略；ADX>30+MA同向+dist>3%；按C评估；例外：只AU/AG;当前休眠；解除/更新：池复活及全门。

<a id="r-trigger-d"></a>
**TRIGGER-D**　事件策略；落地次日确认；按D评估；例外：真空不打分;不抢跑；解除/更新：日历新节点。

<a id="r-trigger-e"></a>
**TRIGGER-E**　已出清叙事回归；周涨跌近3年前20%（[D8-definition](#r-d8-definition)取被回归侧）且ADX<22；触发事件已官方落地＋价格完成首段方向修正＋现货/微观同向；按PLAN-E已有许可评估，未决地缘/政策变量不接飞刀；例外：未决变量禁止；解除/更新：完整三项证据。

<a id="r-trigger-fg"></a>
**TRIGGER-FG**　F/G拟评估；F三重+③+现货;G③先解锁；未过不打分；例外：不能由叙事档位绕过；解除/更新：全门过。

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
**PARAM-overnight**　隔夜池；常规隔夜≥4.2、轻仓3.7-4.2；限隔夜非趋势白名单≥4.5、轻仓4.0-4.5；按对应轻仓区间；例外：趋势白名单有专门阈值；解除/更新：许可改变。

<a id="r-param-caps"></a>
**PARAM-caps**　受总分上限限制候选；E上限4.0；无③政策deadline近月多头3.0；RB/SI无远月赔率近月出清多头3.0；③未过且judgement未达RB/SI远月多头4.0；②''未实质过IM/IC多头4.0；先限分再判门；例外：池外休眠；解除/更新：前置实质通过。

<a id="r-trigger-b-window"></a>
**TRIGGER-B-window**　SR/CF季节筛选；SR-summer每年07-01至09-30；CF-spring每年03-01至04-30；CF-autumn每年09-01至10-31，均含首尾；真实郑商所日历映射区间首/末交易日；research_start=首日前20交易日；planned_exit=末日前5交易日；research_start≤审计交易日≤window_end才入研究；例外：窗外直接no_signal，不为下游TP/账户维持incomplete；CF两窗独立；季节主题不是期货上涨证据；解除/更新：窗口完毕；不使用普通工作日推算。

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
**WEIGHT-evidence**　F/G/A微观；F执行级=实施细则＋产能纳入口径＋执行案例＋调减进度；公告/deadline/立法计0；G行为性D2计0；现货门仍是硬前置；例外：光伏价格合规/能耗国标可快评但不代③/#27；A按公开评分卡；解除/更新：有效新证据。

<a id="r-d9-levels"></a>
**D9-levels**　流动性背景；5=社融与M2同比双升＋SOFR下行＋DXY走弱；4=三项中两项扩张；3=中性；2=两项收缩；1=全面收缩；可信公开增量按条件计分；无增量固定3并标default_neutral；例外：默认不是已核宏观中性；D13同源为主，不重复满额扣；三项分组歧义见审计报告，不自行补规则。

<a id="r-d10-score"></a>
**D10-score** → [WEIGHT-D](#r-weight-d)（同义锚）。

<a id="r-d8-definition"></a>
**D8-definition**　D8周涨分位计算（脚本§2d）；fut_mapping锚日主力、同一合约两端结算价算周涨（不拼接复权）；终点=最新已完成行情日，起点=终点前7自然日当日或之前最近交易日；历史样本=终点前3年每个自然周最后交易日、不含本周；有效样本<期望周数80%→D8=unknown（calculation缺口）；多头看上尾（历史样本低于当前值的比例≥100−X即前X%）、空头看下尾、商品双向按拟交易方向取侧、E取被回归侧；例外：任一端缺结算→样本无效，不用收盘补；A结构豁免；只作输入不单独构成信号；解除/更新：每期快照重算。

<a id="r-d8-fin-long"></a>
**D8-fin-long**　金融多头涨幅极端；前10%−0.5;前5%否决；扣分/否决；例外：A/F产能通过/G验证豁免；解除/更新：分位解除。

<a id="r-d8-fin-short"></a>
**D8-fin-short**　金融空头极端；前30%−1;前20%否决；扣分/否决；例外：#17仍禁；解除/更新：分位解除。

<a id="r-d8-commodity"></a>
**D8-commodity**　商品双向极端；前20%−0.5;前10%否决；扣分/否决；例外：A/F/G特定豁免;D14/15优先；解除/更新：分位解除。

<a id="r-d11-bands"></a>
**D11-bands**　单边多头贴顶；dist>5%扣0；3%-5%扣-0.2；1%-3%扣-0.3；0.3%-1%扣-0.5；<0.3%扣-0.8并否决新开；逐档扣分；C惩罚加倍（0.3%-1%为-1.0）；例外：结构不适用；已有仓不强平；边界重复歧义保留待澄清，不自行补端点；解除/更新：dist换档。

<a id="r-d12-trigger"></a>
**D12-trigger**　波动升档；HV20/HV60>1.3或ATR20>80分位或T-3；扣分−0.3且门槛+0.3，未过转观望/合格结构；例外：完整结构豁免；解除/更新：升档触发退出。

<a id="r-d12-bands"></a>
**D12-bands**　ATR250分层；ATR250分位>80 / 40-80 / <40；高波×0.5、当期ATR核SL、gap收紧一档及隔夜重核；其余常规；例外：临近T−3低波至少常规；单一收紧值按淘汰线；结构豁免方向性D12；解除/更新：分层更新。

<a id="r-d12-diverge"></a>
**D12-diverge**　池内分位分化；极差>50；逐品种独立核参；例外：结构单边重校准豁免；解除/更新：分化解除。

<a id="r-d13-cost"></a>
**D13-cost**　宏观压制有效；−0.3;C门槛+0.3;升级线−0.5;×0.5；扣分/减金额；例外：独立事件项仍叠加；解除/更新：归档条件全过。

<a id="r-d13-freeze"></a>
**D13-freeze**　加息对半/落地；事件裁决；复归档冻结；例外：不是永久禁多；解除/更新：美元承压/连涨中断周度确认＋FOMC后宏观退出主导；转鸽重启归档评估，加息冻结重写，按兵鹰派延续待裁决。

<a id="r-d14-restart"></a>
**D14-restart**　复产达产/超预期；~6975万吨;−0.5~-1；多头减0.5/清仓;月差检视；例外：仅实际依赖对应成本/收缩因子的计划；独立国内月差不继承未知铁水，已知相关反证仍处理；不自动解锁③；解除/更新：独立证伪解除。

<a id="r-d14-water"></a>
**D14-water**　铁水<230万吨（参考）；不作执行条件；不扣分、不触发处置，仅RB需求侧背景旁证；例外：需求证弱按[D14-stock](#r-d14-stock)（库存转累/现货转贴水）判定。

<a id="r-d14-stock"></a>
**D14-stock**　累库或转贴水；−0.5;减50%；减仓；例外：仅实际依赖对应成本/收缩因子的计划；独立国内月差不继承未知铁水，已知相关反证仍处理；不自动解锁③；解除/更新：去化+现货恢复。

<a id="r-d14-pass"></a>
**D14-pass**　复产慢且去化且需求在；铁水≥230为参考；不扣；例外：仅实际依赖对应成本/收缩因子的计划；独立国内月差不继承未知铁水，已知相关反证仍处理；不自动解锁③；解除/更新：反向重核。

<a id="r-d15"></a>
**D15**　carry双杀等状态；未过④=0;双杀−0.5~-1;不明−0~-0.3；减半/对冲/清仓/轻仓；例外：当前休眠；解除/更新：④过且指数稳不扣。

<a id="r-pen-narrative"></a>
**PEN-narrative**　脆弱叙事适用；每条0–3；负向评分；例外：已证伪归档不评分；解除/更新：实际证据改变。

<a id="r-pen-fixed"></a>
**PEN-fixed**　PPI/产能/股指/能源条件；PPI输入性>60%扣1；③未达扣1.5；7-8月PPI收窄兑现远月扣0.5；IM/IC②''未实质过扣1；能源单边①未缓和证真扣1；条件扣减；例外：只当期适用可核事实；精确比例缺失不猜不扣；能源结构豁免；池外不入执行分母；解除/更新：对应门解除。

<a id="r-factor-groups"></a>
**FACTOR-groups**　适用风险场景；0–1;同源一次；预算金额相乘；例外：不适用=1且写理由；解除/更新：状态改变。

<a id="r-factor-nearhigh"></a>
**FACTOR-nearhigh**　多头贴顶；5%内0.6;2%内0.3；最严一档；例外：不双乘；解除/更新：退出贴顶。

<a id="r-factor-correlation"></a>
**FACTOR-correlation**　未对冲权益beta再校准；×0.5；折金额/对冲/观望；例外：不重复D12；解除/更新：相关性重建。

<a id="r-factor-policy"></a>
**FACTOR-policy** → [0.3#10](#r-gate-10)（同义锚）。

<a id="r-score-normalize"></a>
**SCORE-normalize**　基础分计算；Σ(固定原始权重×维度分)/Σ固定原始权重；A分母90、D95、F90；再叠适用扣减加成，其他池按完整固定表求和；例外：原始权重不必合计100%；不依当周可得项重加权；仅D9可固定默认；必要维度未知完整总分null；解除/更新：补齐必要评分。

<a id="r-conf-definition"></a>
**CONF-definition**　A价格确认；价差指标、方向、阈值、窗口、价格口径、经济理由＋rule_version/带时区defined_at/effective_from；confirmation_definition=undefined/draft/frozen；仅冻结生效规则判对应观察期；草案/必要观察未知→unknown；例外：分位另列screening_evidence；三日/40元/两周示例非默认门槛；解除/更新：按[CONF-owner](#r-conf-owner)由研究方提供具体定义或不能成案原因。

<a id="r-conf-prospective"></a>
**CONF-prospective**　确认定义创建或变更；仅前瞻生效；同机会保留版本，变更留原定义/理由/生效时间；例外：不回判定义前信号，不逐周重置窗口追随既成走势；解除/更新：生效后的必要观察齐备。

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
**CONF-owner**　MA四点包及确认未完成；至多两条最近候选；方向/经济失效SL/目标期限/净R；research负责具体计划、确认草拟冻结和前瞻观察；不能成案逐字段给事实/计算缺项、负责人、下一动作/期限；例外：既有许可内不另等用户批准；不编阈值或SL、不扩大许可；用户仅真实账户/挂单、偏好变更及新权限；解除/更新：首次用冻结后完整观察期；同opportunity_id/版本不逐周重开钟。

## 1.8 交易计划与真实容量

<a id="r-latent-h"></a>
**LATENT-H**　H复活许可；④全过；SL=贴水重新走阔+5pct或指数破前低；TP=贴水收敛至10%以下或换月；按H管理；例外：当前休眠；解除/更新：新门通过。

<a id="r-latent-jmrb"></a>
**LATENT-JMRB**　原料强成材弱结构复活；双焦收缩部分三验证＋成材需求证弱（铁水<230为参考，复活前用公开库存/现货基差重定义）；多JM空RB，名义价值配比；成材相对走强/收缩证伪为SL，目标或任一逻辑反向了结；例外：不是A同品种1:1；JM未回池禁止；解除/更新：新池许可。

<a id="r-latent-curve"></a>
**LATENT-curve**　国债曲线恢复；利差精确值+3年分位+结构池复评；重建计划；例外：当前挂起；解除/更新：补齐复评。

<a id="r-latent-ps"></a>
**LATENT-PS**　PS回归复活；回池许可＋期现基差/月差、SMM库存产量、合约/广期所风控；过剩且现货反向为回归前提；收敛TP/反扩SL；③达标、强制限价/查处、自律实际成交守成本→检视了结；例外：节点±1不新开；涨停或4%+脉冲后3日不建反向结构；未核方向/底线不得执行；解除/更新：许可重建。

<a id="r-latent-lh"></a>
**LATENT-LH**　生猪升水回归恢复；期现升水、能繁/出栏、合约参数齐；收储/疫病±3日暂停；空升水;現货追认SL；例外：能繁加速去化证真须检视；与通用节点±1取适用更严；解除/更新：恢复候选全门。

<a id="r-latent-spread-screen"></a>
**LATENT-spread-screen**　休眠结构复活；分位≥70/≥85仅研究；开仓≥4.0、轻仓3.5-4.0、首期0.5、R≥2.5、30-60日参考；SC/PS/LH复活后另核方向/真实SL/完整计划；例外：SC满配需另议；LC冻结期参数仅存档；解除/更新：完整计划。

<a id="r-a-definition"></a>
**A-definition**　池内MA/RB/SR跨月；S近−远;元/吨;1:1；多=买近卖远/空相反；例外：跨品种/非1:1另核模型；解除/更新：新模型许可。

<a id="r-a-screen"></a>
**A-screen**　价差同期高分位；≥70/≥85；研究候选/高分位候选；例外：非主仓非方向;未开低分位对称；解除/更新：完整信号另核。

<a id="r-a-reversion"></a>
**A-reversion**　高价差回归且已有许可；SL>Entry>TP1≥TP2；空价差；domestic_public须国内变化独立支持收敛，即使海峡未缓和仍有论证，并核反向地缘冲击；获利依赖缓和则geopolitical_fade、必须①；例外：通用价格确认＋独立产业事实不能替代强因果专属门；不开放MA单边空头；解除/更新：经济失效触真实SL；必要专业数据长期不可得的模型research_only。

<a id="r-a-continuation"></a>
**A-continuation**　结构延续模型；多SL<Entry<TP1≤TP2;空反向；方向/目标由批准模型；例外：本次不新增许可；解除/更新：显式许可和验证。

<a id="r-a-fields"></a>
**A-fields**　计划生成；两腿/配比、模式/方向/许可、evidence_basis及支持反证、确认定义、Entry/SL/TP1/TP2、价格单位/乘数、费用滑点、行情日/样本、最短/最长持有期、最晚退出日、双腿限价/滑点/撤单平裸腿/压力预案；研究方形成方案；必要缺项incomplete，不整包交回用户；例外：无证据可写具体不能成案原因；方向/净R错误是已核计划失败；解除/更新：补件/重设计划。

<a id="r-a-median"></a>
**A-median**　分位参考；50/30/10分位仅参考；入场冻结目标数值、样本和依据；统计分位与人民币损益分列；例外：50不作SL或风险锚；30/10非强制TP，不随样本更新静默移动SL/TP；解除/更新：换月重建。

<a id="r-a-stop"></a>
**A-stop**　失效SL；不可反推/放宽；按逻辑定SL；例外：不凑手数；解除/更新：新逻辑需重建。

<a id="r-a-cost"></a>
**A-cost**　风险与净收益；cost_unit=两腿开平滑点+手续费；默认4×tick_value，实际更大取更大；side=+1多价差/−1空价差；risk_unit=side×(Entry−SL)×multiplier+cost_unit；net_reward_tp1=side×(TP1−Entry)×multiplier−cost_unit；R=net_reward_tp1/risk_unit≥2.5；例外：价格统一CNY/tonne；一组近远各1手，人民币风险/收益；解除/更新：真实成交重核。

<a id="r-a-r"></a>
**A-R** → [0.3#6](#r-gate-6)（同义锚）。

<a id="r-a-fill"></a>
**A-fill**　Entry信息齐备；下一可成交时点；重核真实成交风险与R；例外：不得假设盘后结算能成交；解除/更新：成交后重核。

<a id="r-a-legs"></a>
**A-legs**　两腿下单；限价/滑点/撤单平裸腿预案；一腿未成按单边占预算；例外：无结构豁免；解除/更新：完整配对。

<a id="r-a-stress"></a>
**A-stress**　压力情景；价差反跳/单腿/扩板提保；独立核gap/周末/保证金；例外：未知不能ready；解除/更新：数据齐。

<a id="r-a-expiry"></a>
**A-expiry** → [ROLL-plan](#r-roll-plan)（同义锚）。

<a id="r-a-overrides"></a>
**A-overrides**　MA/黑色结构；按实际因子核D14、①、质变事件与组合cap；MA两证据路线分开；RB国内独立月差不因未知铁水自动失败，相关反证不可忽略；例外：完整A豁免单边#30、MA周涨及D8/D11/D12；裸腿另核；解除/更新：各门释放。

<a id="r-plan-style"></a>
**PLAN-style**　交易工具；不做日内;单边+结构；只用许可表达；例外：不开放期权/跨式；解除/更新：另行明确许可。

<a id="r-plan-d-time"></a>
**PLAN-D-time**　事件发生；T-3~T-1/T/T+1~T+3;次日开30分钟；观察→确认→入场；例外：不抢跑/股指禁空；解除/更新：事件之后核门。

<a id="r-plan-d-exit"></a>
**PLAN-D-exit**　D有效计划；SL1.5ATR/反向极值;TP1+2R;TP2窗末前2日；止损/移动/强平；例外：双向需有效反向公式；解除/更新：退出。

<a id="r-plan-e"></a>
**PLAN-E**　已出清叙事；Entry±0.3ATR;SL±1ATR;TP30日均值；多/空对应公式；例外：金属反向/权益反弹不经E;能源仍①；解除/更新：计划失效。

<a id="r-plan-f"></a>
**PLAN-F**　③+三重+现货全过；远月收盘突破MA20；SL=Entry−2×ATR20或MA60取近者；TP1=Entry+2R；TP2前3日低点；仅远月；例外：公告/自律/光伏外推不解锁；解除/更新：任一验证连续2周反向清仓；调减未达存量减50%；PPI内生性<40%连续2月或7-8月收窄兑现，相关远月减30%；新验证后复评。

<a id="r-plan-g"></a>
**PLAN-G**　③已解锁；矿端真实执行+三方库存连续2周去化+现货back;复产<~6975+需求门（公开库存；铁水≥230为参考）；收盘MA20/结构确认入；SL=Entry−2×ATR20或MA60取近者；TP1=Entry+2R；TP2前3日低点或现货弱/复产证真（铁水<230为参考）；例外：无行为性替代；解除/更新：D14优先；60日或证伪退出。

<a id="r-plan-c"></a>
**PLAN-C**　AU/AG许可后；多Entry=max(H20+1tick,突破K高+1tick)；dist>3%、ADX>30、MA同向；SL=min(突破K低,Entry−2×ATR20,MA20−0.5×ATR20)；TP1=Entry+2R，TP2移动止损；例外：周涨非前10%；空头#17；C仅AU/AG且当前休眠；解除/更新：模型重新许可。

<a id="r-plan-b"></a>
**PLAN-B**　许可B做多且窗口筛选通过；Entry_raw=max(MA20,pre_window_low5+1×ATR20)；Entry向上对齐tick；SL向下对齐(Entry−1.5×ATR20)；价格元/吨；按[PLAN-B-history](#r-plan-b-history)算mean_return；TP1向下对齐Entry×(1+0.7×mean_return)，5%=0.05；例外：pre_window_low5为窗口开始前5个交易日最低low，固定不滚动；MA20/ATR20取具体合约最近完整交易日；缺数据unknown，不报定义未核；解除/更新：计划/行情变更须按新剩余期限重算；不抬TP缩SL凑R。

<a id="r-risk-caps"></a>
**RISK-caps** → [RISK-regime](#r-risk-regime)（同义锚）。

<a id="r-risk-regime"></a>
**RISK-regime**　经当期15项适用触发核定normal或low_exposure后才计算组合上限：normal=实际净值×3.5%，low_exposure=min(normal,固定5000元)；当前unknown时portfolio_cap/final_lots=null，只能明确标情景参考，不能由else分支当作normal。单笔预算仍为净值3.5%，低敞口不加入单笔factor_product、无regime_factor；例外：净值降低不得超normal，净值增加低敞口仍封顶5000；计划止损不是最大可能亏损，账户真实占用另核；解除/更新：逐项复评全部触发及账户后重算。

<a id="r-risk-unit"></a>
**RISK-unit**　逻辑/SL成本确定；risk_unit=abs(Entry−SL)×multiplier+round_trip_cost；单腿滑点预算=2×slippage_tick×tick_value，另加开平手续费；真实一手风险；例外：A用组公式;禁中位数锚；解除/更新：成交变动重核。

<a id="r-risk-factor"></a>
**RISK-factor**　系数适用；factor_product=strategy_factor×各适用场景系数；trade_effective_budget=trade_cap×factor_product；先金额折减；例外：D10非乘数;同源去重；解除/更新：规则状态改变。

<a id="r-risk-used"></a>
**RISK-used**　账户持仓挂单；每项风险≥0；持仓+预留相加；例外：同一部分不重复记；解除/更新：成交/撤单刷新。

<a id="r-risk-add"></a>
**RISK-add**　新开或加仓；trade_remaining=max(0,trade_effective_budget−existing_trade_risk)；portfolio_remaining=max(0,portfolio_cap−used_open_risk−reserved_order_risk)；candidate_budget=min(trade_remaining,portfolio_remaining)；新交易existing_trade_risk须显式0；例外：本交易原持仓挂单已含在组合占用，不二次加算；解除/更新：新计划。

<a id="r-risk-round"></a>
**RISK-round**　预算及风险齐备；risk_lots=floor(candidate_budget/risk_unit)，仅此一次取整；risk_lots；例外：不先floor再乘；解除/更新：数据变动重算。

<a id="r-risk-final"></a>
**RISK-final**　可核整数交易容量；仅在regime/账户/计划/保证金与限仓均可核后，final_lots=min(risk_lots,margin_capacity_lots,position_limit_capacity_lots)；输出normal/current及low_exposure_cash_cap，旧portfolio_risk_cap为current别名，无regime_factor输出；例外：任一必要容量或当期regime未知则final_lots=null，已核容量0才阻断；数值输出不代替全规则许可；解除/更新：完整输入到位重算。

<a id="r-risk-dedup"></a>
**RISK-dedup**　重复场景；贴顶最严;D12共振0.3代0.5;MA>8优先>5；同源一次；例外：独立T−1可叠；解除/更新：适用状态改变。

<a id="r-risk-tool"></a>
**RISK-tool**　数值工具factors；strategy、D11、D12、D13、D14、D15、event_window、exchange_buffer、promotion、driver_weakness、MA_oil_guard、seasonal_adx、policy_adverse、equity_confirmation、correlation_recalibration；factors仅接受所列15组；拒未知组/重复JSON键；同源按最严值先合并；例外：D12含高波/T−3/共振；event_window仅独立T−1；driver_weakness含同源链背离；解除/更新：新增组先同步。

<a id="r-risk-snapshot"></a>
**RISK-snapshot**　账户核验；verified_at带时区，与测算同一上海日期，且不晚于测算；核实账户/持仓/挂单；新成交撤单须刷新；例外：空列表须实核；脚本POSITIONS空或历史空仓不作证明；解除/更新：新成交撤单刷新。

<a id="r-risk-net"></a>
**RISK-net**　结构与多笔风险；组合结构一次;裸腿单边；不同笔保守相加；例外：不因相反/浮盈/未验相关抵消；解除/更新：核定模型另议。

<a id="r-risk-profit"></a>
**RISK-profit**　盈利持仓；当前估值到SL不利损失+费≥0；不负风险；例外：浮盈非自动抵扣；解除/更新：SL变动重核。

<a id="r-risk-margin"></a>
**RISK-margin**　保证金容量；全账≤60%;提保单品≤20%；按实际经纪商费/可用资金算新增容量；例外：未经核验无抵扣优惠；解除/更新：资金规则变化。

<a id="r-risk-limit"></a>
**RISK-limit**　限仓容量；每腿80%扣现仓挂单；双腿取小可配对容量；例外：不得复用同一预算；解除/更新：成交预留更新。

<a id="r-risk-reserve"></a>
**RISK-reserve**　多候选；评分及固定平分序；逐笔预留后重算；例外：不多次复用组合余量；解除/更新：撤单释放。

<a id="r-risk-null"></a>
**RISK-null**　必要输入未知；null而非0；incomplete；例外：所有已核为零才预算阻断；解除/更新：补齐。

<a id="r-risk-recal"></a>
**RISK-recal**　ATR上涨/升层；now/entry>1.3或升入>80；按既定SL公式重算超额次日先降；例外：不统改2ATR/不放宽;即时规则优先；解除/更新：每日核验。

<a id="r-risk-structure-recal"></a>
**RISK-structure-recal**　结构存量；每日核SL/实际风险/保证金/组合cap；保留组合风险复核；例外：豁免单腿ATR不豁免总cap。

<a id="r-risk-stock-regime"></a>
**RISK-stock-regime**　低敞口持续；多个触发只应用一次固定金额上限；存量按实际金额降至当前cap；例外：不每天再减半;保留更严的强平/禁隔夜纪律；解除/更新：全部触发复评。

<a id="r-plan-f-validation"></a>
**PLAN-F-validation**　F远月拟执行；原文仅称“三重验证全部通过”，未给独立三项完整定义；保留前置且不能判pass；先核既有许可，必要定义缺失列incomplete；例外：不得借G的三项或新增库存周数补齐F；当前F仍冻结；解除/更新：canonical明确F三重验证定义后再核。

<a id="r-plan-h-params"></a>
**PLAN-H-params**　H恢复许可后；④后≥4.0＋收敛门；系数0.5；R≥2；至换月/收敛、交割周前退出；再按[LATENT-H](#r-latent-h)计划；例外：当前休眠，不借换仓启用；解除/更新：许可与④通过。

<a id="r-plan-au-break"></a>
**PLAN-AU-break**　AU/AG历史管理引用；破位区间<4000；原文仅称纪律待命，未给具体动作；不据此自行发出交易指令；例外：AU不交易/AG休眠，真实历史持仓仍核[MANAGE-AU](#r-manage-au)与[MANAGE-stop](#r-manage-stop)；解除/更新：需要时先明确缺失动作。

<a id="r-plan-b-time"></a>
**PLAN-B-time**　B拟新开；window_start≤执行交易日<planned_exit；最晚退出=min(planned_exit,合约既有强制退出日)；前20交易日仅准备；期限不够则计划失败；例外：研究筛选到window_end不等可新开；旧榨季/新旧作快照不覆盖日期表；解除/更新：执行/合约日期更新即重核。

<a id="r-plan-b-version"></a>
**PLAN-B-version**　采用新B定义；rule_version=B-v2.24；defined_at/effective_from带时区；生效不早于获准采用后的首个完整交易日；研究方登记后仅前瞻使用；窗口与新公式同版本；例外：日期为未校准的研究治理参数，不回判过去信号/收益；不随当期涨跌迁窗；解除/更新：每个窗口结束复评信号/可得性/成本；修订只用于以后窗口。

<a id="r-plan-b-history"></a>
**PLAN-B-history**　拟入场及最晚退出已定；之前连续3个年份，每年同window_id一个收益率；r_y=P_exit_y/P_entry_y−1；mean_return=(r_y1+r_y2+r_y3)/3；同品种同交割月、交割年与窗口年的差值平移；2026秋CF2701对应2025秋CF2601；入场月日向后找首交易日、退出月日向前找末交易日，均在历史窗口且入场<退出、合约可交易期内；两端settle，逐年列日期/值/来源；例外：含亏损年份，不筛年/拼主力/用close/缩年/扩窗；任何一年未上市或缺端点/口径未知则具体unknown；现有日线或终端导出可用，不需专业季节库；解除/更新：按剩余持有区间重算；持续不可得按0D仅复评B可行性，三年目标样本不证明收益有效。

<a id="r-plan-b-economics"></a>
**PLAN-B-economics**　B价格及期限已算；mean_return≤0或TP1≤Entry或net_R<2或期限不行；已核计划失败；R/成本及金额容量按Step5统一定义，不另造公式；例外：参数未知才unknown；窗口筛选不代产业/#5；D8、原分数、策略0.7和ADX<25再×0.7保留；解除/更新：真实计划改动再验；失败与必要未知并存按AUDIT状态。

<a id="r-plan-b-trail"></a>
**PLAN-B-trail**　TP1触达后跟踪；SL=max(原有效SL,此前5个完整交易日最低low)，只上移；已穿越则按可执行报价处置；TP2按此跟踪，到最晚退出日收盘前清余仓，合约更早强制退出优先；例外：TP1只是跟踪启动线，不新增强制分批比例；6.1通用锁盈/止损和6.3贴顶规则取严；不挂虚假可成交SL；解除/更新：研究方交Entry/SL/TP1、TP2规则、入退日、成本/net_R；seasonal_plan.py仅离线算术、不授许可。

## 1.9 已核实持仓管理与换仓

<a id="r-manage-stop"></a>
**MANAGE-stop**　SL触及/超周期；立即/上限；平仓；例外：特例更严；解除/更新：成交退出。

<a id="r-manage-profit"></a>
**MANAGE-profit**　盈利增长；>1R/>2R/>3R；保本/锁1R/锁2R；例外：金银专门规则；解除/更新：退出。

<a id="r-manage-driver"></a>
**MANAGE-driver**　微观1项反向/驱动弱；×0.5；减半或对冲；例外：不依赖事件日历；解除/更新：证据恢复。

<a id="r-manage-f"></a>
**MANAGE-F** → [PLAN-F](#r-plan-f)（同义锚）。

<a id="r-manage-d9"></a>
**MANAGE-D9**　流动性扩张转中性/收缩；减30%/50%；趋势降仓；例外：当前C休眠；解除/更新：流动性恢复。

<a id="r-manage-event"></a>
**MANAGE-event**　横跨离散事件；T−1×0.5或对冲；提前处置；例外：只许可工具;结构单边豁免；解除/更新：事件落地。

<a id="r-manage-geop"></a>
**MANAGE-geop**　双轴质变；T0/次日（形态见[REG-geop](#r-reg-geop)；通行量为参考）；双向检视/反向风险减仓；例外：不自动新增交易；解除/更新：事件持续核。

<a id="r-manage-exchange"></a>
**MANAGE-exchange**　提保限仓公告；60/20/80%；主动减至阈值；例外：保有效对冲腿优先；解除/更新：公告退出。

<a id="r-manage-au"></a>
**MANAGE-AU**　AU/AG盈利；>2R不锁1R;>3R锁2R;>4R锁3R；特殊止盈；例外：当前信号/休眠;核实历史仓才管；解除/更新：退出。

<a id="r-manage-top"></a>
**MANAGE-top**　任意多头贴顶；dist_to_H250%<2%且盈利>2R→锁1.5R；dist_to_H250%<0.5%且盈利>1R→平50%；加速止盈；例外：不凭近似值；解除/更新：dist恢复。

<a id="r-manage-policy"></a>
**MANAGE-policy**　政策脉冲日；D8前5%;反向量放减50%；限隔夜检视;SI强平;禁新开；例外：顺向未触前5持有不加；解除/更新：次日③快评。

<a id="r-manage-rb"></a>
**MANAGE-RB** → [CARD-RB-manage](#r-card-rb-manage)（同义锚）。

<a id="r-manage-ma"></a>
**MANAGE-MA** → [CARD-MA](#r-card-ma)（同义锚）。

<a id="r-manage-agri"></a>
**MANAGE-agri** → [CARD-M](#r-card-m)（同义锚）。

<a id="r-swap-same"></a>
**SWAP-same**　同品种远近；遠月评分高≥0.5且流动性更优；实际滚动按[ROLL-structure](#r-roll-structure)/[ROLL-direction](#r-roll-direction)；换入前重核全门；例外：旧距交割<10日触发被0)滚动唯一判据覆盖，不能延后到10日内；解除/更新：换入全门过。

<a id="r-swap-cross"></a>
**SWAP-cross**　不同品种；新评分高>1且旧核心弱；换仓；例外：禁休眠承接；解除/更新：新候选完整。

<a id="r-swap-d8"></a>
**SWAP-D8**　金融多头分位极端；前10降权;前5不加;创新高+前10；合格A或减50%；例外：保底仓非强平；解除/更新：分位解除。

<a id="r-manage-no-account"></a>
**MANAGE-no-account**　输出持仓管理动作；必须经核实实际持仓；账户未知不等零仓，先做研究，final_lots=null；例外：历史空仓/存量条款均非当前账户证据；无核实不执行管理动作；解除/更新：取得[RISK-snapshot](#r-risk-snapshot)。

<a id="r-manage-tail"></a>
**MANAGE-tail**　敏感品种驱动存疑且未对冲；敞口>30%风险预算；强制降至30%或清仓；例外：不依赖事件日历；结构按单边约束豁免仍核组合和专属门；解除/更新：驱动与有效保护重新核验。

<a id="r-manage-dormant"></a>
**MANAGE-dormant**　池外模型复活或真实历史持仓核实；CU/AL跨周末对冲或降至30%风险预算；JM/J单边周五降至50%；SC/PS/LH激活首期周五减半；对应适用事件/节点前处置；PS/LH/SC节点±1不新开，LH专属±3取严；例外：不凭旧持仓文字执行；池外模型不自动复活；解除/更新：许可与实际持仓核实。

<a id="r-manage-cu"></a>
**MANAGE-CU**　核实CU back历史存量；TP分位/⑤整体口径转累库/结构滚动退出日，先到为准；到期了结，整体转累库立即了结；例外：CU当前休眠、无核实存量不执行；解除/更新：真实退出。

## 1.10 跳空执行风险

<a id="r-gap-active"></a>
**GAP-active**　MA/RB/SR/CF/M执行风险；MA 1.3/1.8；RB/M/SR/CF 1.5/2.0；MA①未缓和证真1.2；RB山西复产公告±2日1.3（铁水为参考不触发）；WASDE±1为1.3；依[GAP-definition](#r-gap-definition)分别减额复评/淘汰；单一收紧值为淘汰线；例外：真实数据缺失不可填默认；解除/更新：收紧事件结束。

<a id="r-gap-latent"></a>
**GAP-latent**　休眠板块恢复；IM/IC 1.3/1.8，权益重大事件/美股单日跌>4%/双杀→1.2；TL/T 1.2/1.5；JM/J 1.5/2.0，山西复产公告±2日→1.3（铁水为参考）；AU/AG 1.5/2.0，地缘±2/D12→1.3；CU/AL 1.5/2.0，地缘/宏观窗口→1.3；SC 1.3/1.8，地缘质变±2→1.2；SI脉冲日必平、无gap表；复活后按[GAP-definition](#r-gap-definition)及当期日历核；金银固定窗口见[DYNAMIC-gap](#r-dynamic-gap)；例外：池外不影响当前候选；TL/T裸腿受限；SC信号不执行；解除/更新：恢复品种时重核。

<a id="r-gap-definition"></a>
**GAP-definition**　执行压力核算；gap_ratio=stressed_loss/planned_loss；stressed_loss=max(planned_loss,压力退出损失+压力成本)；同手/组、同人民币费用口径；以已列场景下SL穿透可执行估价核报价/历史跳空/涨跌停依据与假设；例外：结构同一时点双腿及裸腿事故；不拼有利异步报价，不以无新闻作零压力；公开行情/交易规则可用；解除/更新：研究可列待核，交易前必要场景/报价缺失incomplete。

<a id="r-gap-action"></a>
**GAP-action**　gap_ratio触及表内约束；超过第一数→具体减额复评；超过第二数→否决；单一收紧值=淘汰线；复核绝对压力金额与可用资金，有金额依据才可完成执行核验；例外：减手数不改变单位gap_ratio，不绕第二线；参数是治理值非已验证最优；解除/更新：明确压力承受方案和执行输入。

## 1.11 审计输入约束

证据有效性见 [DATA-quality](#r-data-quality)，确认版本见 [CONF-definition](#r-conf-definition)，账户时效见 [RISK-snapshot](#r-risk-snapshot)；输出与发布见 §1.12。

## 1.12 每周执行诊断

<a id="r-audit-weekly"></a>
**AUDIT-weekly**　每周；无论是否更新；独立execution-audit；例外：市场元研究不代；解除/更新：每周新增审计。

<a id="r-audit-unit"></a>
**AUDIT-unit**　候选身份；交易日+合约/对+策略+方向+版本；跨周关联ID；例外：未定方向unknown；解除/更新：明确定义。

<a id="r-audit-coverage"></a>
**AUDIT-coverage**　全规则核验；pass/fail/unknown/not_applicable；标已/未覆盖；例外：非适用需理由；解除/更新：全覆盖才完整声明。

<a id="r-audit-no"></a>
**AUDIT-no**　触发已核未满足；no_signal；仅本策略未触发；例外：后续门可未评估明示；解除/更新：信号变化。

<a id="r-audit-incomplete"></a>
**AUDIT-incomplete**　存在必要未知；incomplete；保留已知全部阻断；例外：研究已成案且只剩账户类未知→[AUDIT-awaiting](#r-audit-awaiting)，不得写incomplete；不能市场无信号；解除/更新：补件完成。

<a id="r-audit-block"></a>
**AUDIT-block**　完整候选已核有否决或0容量；blocked；列预算/交易/许可多原因；例外：未知优先incomplete；解除/更新：阻断解除。

<a id="r-audit-awaiting"></a>
**AUDIT-awaiting**　研究成案、待账户核验；signal=triggered、data_feasibility=available、至少一条适用检查已评估、plan的Entry/SL/TP（数值）与最晚退出日（ISO日期）已填、无已核否决，且除账户类（gap.kind=account）外没有其他适用unknown→status=awaiting_account，final_lots=null；例外：账户已核验、有fail、计划未填完或任一非account类unknown→不得使用；schema 3专用；满足条件仍写incomplete为错误；解除/更新：账户核验后转ready/blocked。

<a id="r-audit-ready"></a>
**AUDIT-ready**　完整信号门全过；有效方向SL/TP/R/期限/预算容量≥1；ready评估条件；例外：成交前仍刷新；解除/更新：实际更新再核。

<a id="r-audit-only"></a>
**AUDIT-only**　唯一阻断声明；一已知fail且其他适用全pass→true；至少两已知fail→false；一已知fail且必要unknown→null；first_blocker与all_blockers只收已核fail；unknown_checks分列；例外：第一刀统计非独立因果；无阻断不声称唯一阻断；解除/更新：补齐所有门。

<a id="r-audit-account"></a>
**AUDIT-account**　账户状态声明；经核实快照；verified_flat/positions；例外：历史空仓/已了结/POSITIONS空不代；解除/更新：账户实核。

<a id="r-audit-wording"></a>
**AUDIT-wording**　全部候选结论；全范围no_signal/blocked才无合格新开；缺项须写未形成方案；含awaiting_account须列出已成案计划并写“待账户核验”；例外：不能写市场不值得；解除/更新：完成缺项。

<a id="r-audit-pending"></a>
**AUDIT-pending**　未完成事项；负责人/缺件/期限/到期动作；不静默顺延；例外：未决不算用户选择；解除/更新：补齐或到期处置。

<a id="r-audit-fields"></a>
**AUDIT-fields**　审计输出；schema 3；旧schema 2仅兼容历史版本；signal=triggered/not_triggered/unknown；status见[AUDIT-no](#r-audit-no)/[AUDIT-incomplete](#r-audit-incomplete)/[AUDIT-awaiting](#r-audit-awaiting)/[AUDIT-block](#r-audit-block)/[AUDIT-ready](#r-audit-ready)；shadow_plans字段见[AUDIT-shadow](#r-audit-shadow)；正文与严格JSON同步；运行python3 scripts/validate_futures_audit.py --input research/futures/weekly/<date>/<date>-execution-audit.md，记录命令/退出码/实际结果，失败先修；例外：未运行明示；信号席单列范围；不可自造枚举或fail/unknown混值；校验器不核经济逻辑/来源真伪/收益、不授许可；解除/更新：真实填值。

<a id="r-audit-shadow"></a>
**AUDIT-shadow**　影子计划登记、结算与归因；每周为最接近成立的至多两条候选（不论incomplete/awaiting_account/blocked）在JSON shadow_plans登记：shadow_id、candidate_id、instrument{single/spread，contracts 1/2个}、side、entry_type=limit/stop、entry/stop/target（多头stop<entry<target，空头相反）、entry_expiry、latest_exit_date、multiplier、round_trip_cost、带时区registered_at（上海日期≤as_of_date）；登记须在报告周内（registered_at上海日期∈[as_of_date−7天, as_of_date]，事后补登记无效）、最晚退出日晚于登记日；登记后不改，同一shadow_id只认最早（改写由脚本点名忽略）；脚本§5结算规则：只用登记之后才开盘的已完成日线（日线含前一交易日21:00起夜盘）；限价按计划价成交，突破单取计划价与开盘价较差者；成交价已越过目标价→按成交价即时了结（只付成本）；成交当日只认止损（价差按当日结算价出场）；同日触及止损与目标按止损；跳空穿止损按开盘价；价差只用两腿结算价之差；过入场有效期未成交作废；最晚退出日或合约最后交易日先到者按结算价了结；缺价停止评估；已了结影子按登记时已核阻断归集人民币盈亏与R；例外：一笔多阻断各计一次，非独立因果；无登记时避免损失/错过收益=null；一次涨跌/未交易不证明护栏有效；未算真实计划风险前不归因于5,000元上限；解除/更新：回溯重评标proposed_framework_reassessment，不假装当日生效。

<a id="r-audit-rule-review"></a>
**AUDIT-rule-review**　同一专业字段不可持续取得且重复拦截；连续两轮；复评公开替代或将该模型research_only结案，保留原机会/否决记录；错误数据/豁免/定义立即纠正；例外：护栏命中数、连续空仓、一次踏空不证明有效或过严；不为凑手数放宽金额边界；解除/更新：同时比较避免亏损与错失盈利，不预设下周更新级别。

<a id="r-audit-gap-owner"></a>
**AUDIT-gap-owner**　适用检查unknown；gap.kind=definition/plan/calculation/raw_data/acquisition/not_published/account；附owner/next_action/due_at；definition/plan归research，calculation归data_pipeline；acquisition是已存在未取得；not_published须官方发布证据；例外：治理deadline不是发布时间；可选背景不进unknown_checks；SC周settle→原油护栏，MA#30另用MA日settle/pre_settle及涨停；D8由脚本§2d计算、快照缺值归calculation缺口，gap_ratio未算归计划缺口；解除/更新：按具体下一动作补齐；账户归user。

<a id="r-audit-retraction"></a>
**AUDIT-retraction**　发现错年/未来时点/错口径；保留invalid旧行＋纠错记录；新证据另建ID；立即撤回触发并重算门/评分/系数/阻断清单/主状态/容量，列前后差异与仍有效独立冻结；替代未核则unknown；例外：不能只换数留罚分；周度247家日均铁水不新增等下一周才撤错的门；无完整输入只列待办，不声称结果不变；解除/更新：schema 3隔离诊断引用与判定依据；来源年份/观测期/单位仍核原文，校验器不从URL断真伪。

## 2. 品种特例与休眠复活

<a id="r-card-ma"></a>
**CARD-MA**　MA独立路由；A/E（已出清）/D；MA2701=方向性执行腿·#30护栏判定腿·A近腿，MA2705=A远腿（9/16起；当前腿见[DYNAMIC-roll-table](#r-dynamic-roll-table)）；方向性执行腿在其剩余td<50时换到阶梯最近月份；例外：近强远弱不等买远月；库存/到港/装置/基差/仓单择合适一项，不要求全链；解除/更新：驱动对应月份。 ①未过MA多头；门槛+0.3;gap1.2；防追高持续；例外：结构按专属；解除/更新：①相关门变化。 MA周末；周五检视；按MA单边护栏；例外：结构按A专属；解除/更新：护栏解除。

<a id="r-card-ma-week"></a>
**CARD-MA-week**　油价上涨；周>5%×0.5/减50;>8%冻结清仓；取严不重复；例外：完整结构豁免单边护栏；解除/更新：周涨条件解除。

<a id="r-card-ma-month"></a>
**CARD-MA-month**　油价月创新高；近250日H；多头禁开且清仓；例外：结构仍A；解除/更新：高位条件解除。

<a id="r-card-ma-inventory"></a>
**CARD-MA-inventory**　库存不去化/连续回升；港库未去化仅对以去化为依据的多头；连续2周回升；对应新开多头冻结；存量减仓50%；例外：缺值不等未去化；国内结构可选其他真实产业证据，已知相关反证不忽略；解除/更新：库存恢复。

<a id="r-card-ma-price"></a>
**CARD-MA-price**　护栏数据；SC信号腿（随主力换月，9/16起SC2611）结算：最新已完成行情日对其减7自然日及以前最近交易日（脚本§2b“SC护栏结算周涨%”）；MA护栏判定腿（9/16起MA2701）结算/pre_settle单日涨跌（脚本 v1.16 §2b.1「日结算涨跌%」「近5日结算涨跌%」列；列缺失或端点缺失→#30 unknown，不以主力/信号腿或周涨推断）；唯一命中依据；例外：非AS_OF减7日、非5交易日前；布伦特/WTI仅旁证；换月核定合同，端点缺失unknown；解除/更新：主力换月更新。

<a id="r-card-rb"></a>
**CARD-RB**　RB候选；A月差；方向性多头评估冻结，空头不在白名单；F/G冻结;禁方向单边；例外：JM-RB休眠；复产只实际依赖才必要；铁水/盈利率为参考，不进必要验证、不记缺口；总库存去化≠旺季证真，需公开库存/现货同向；解除/更新：独立许可复评。

<a id="r-card-rb-manage"></a>
**CARD-RB-manage**　成本端验证反向/月差收敛；减50%/了结；D14适用（[D14-restart](#r-d14-restart)/[D14-stock](#r-d14-stock)）；按品种管理；例外：铁水创新高、铁水<230为参考不触发；结构需自身SL；解除/更新：证据变化。 RB周末；周五50%；减仓;需求证弱（公开库存）转结构；例外：须结构许可；解除/更新：周末过后。 黑色负反馈检验：提涨落地且同口径库存去化延续→仅评估原料主线延续，不开放RB方向单边；提涨受阻、钢厂减产/抵制或焦煤现货涨势中断→原料历史存量多头立即止盈，不许“再看一周”；期货先于现货回落按现货回落侧处理。JM/J池外仅历史存量适用，RB的D14只对成案且依赖收缩假设的计划判，不传成RB空头许可。

<a id="r-card-m"></a>
**CARD-M**　豆粕备选；已有许可路由的行情确认＋USDA/作物进度/国内公开供需中一项合适独立事实；独立证据升级首期0.5；WASDE方向同向才考虑轻仓；例外：WASDE前2日禁新开、±1交易日gap1.3；南美/压榨/能繁仅相关增强，实际依赖仍核，不自动入C；解除/更新：独立证据升级。 WASDE跨周末；限隔夜池；清仓；例外：常规不自动套限隔夜；解除/更新：事件结束。

<a id="r-card-sr"></a>
**CARD-SR**　白糖备选；A/B路由＋产销/库存/交割供给等证据＋行情确认，升级首期0.5；B按[TRIGGER-B-window](#r-trigger-b-window)/[PLAN-B](#r-plan-b)；A/B评估；例外：抛储多头降级；榨季初需产销率验证；连续2周回落减50%；月度值不外推周度，进口利润仅增强；解除/更新：证据恢复。

<a id="r-card-cf"></a>
**CARD-CF**　棉花备选；季节窗＋独立证据，首期0.5；内外棉价差>3年90分位需额外验证；B按[TRIGGER-B-window](#r-trigger-b-window)/[PLAN-B](#r-plan-b)；B评估；例外：轮储公告±3天暂停；公告后3日跌幅>1.5×ATR减50%；解除/更新：窗口/证据恢复。

<a id="r-card-au"></a>
**CARD-AU** → [DYNAMIC-pool](#r-dynamic-pool)（同义锚）。

<a id="r-card-sc"></a>
**CARD-SC** → [DYNAMIC-pool](#r-dynamic-pool)（同义锚）。

<a id="r-revive-commod"></a>
**REVIVE-commod**　JM/J/AG/CU/AL恢复；JM：账户/预算变更且ATR回落使一手≤预算后重议；AG：随AU同评估、不作替代；J：远腿量≥1万手且一手≤预算；CU：结构池复评＋⑤复权＋一手≤预算；AL：D13归档＋独立电解铝/氧化铝驱动＋完整计划风险核验；先按[POOL-scan](#r-pool-scan)入备选，不自动开仓；例外：不自动建仓；解除/更新：列明条件齐。

<a id="r-revive-lc"></a>
**REVIVE-LC**　LC拟恢复；同口径量化去库≥4周+企稳+排产收缩；恢复候选并首期从严；例外：需求型不代供给;冻结双向不开；解除/更新：新一轮证据齐。

<a id="r-revive-finance"></a>
**REVIVE-finance**　IM/IC/TL/T；IM/IC账户规模或RISK_BUDGET变更后评估；TL/T利差补齐＋结构池复评；先核池许可再重建计划；例外：不以方向清楚或旧2ATR数字证明本期容量；解除/更新：各条件齐。

<a id="r-revive-structures"></a>
**REVIVE-structures**　池外结构复活；SI/PS：第三份文件/调减数据落地、③证真时复查先备选；LH：期现升水补全＋一手≤预算；SC须另行池许可；数据/独立模型/交易性/专属节点全部核验，按A明确计划；例外：原模块数据齐不自动激活；解除/更新：全部门过。

<a id="r-revive-si"></a>
**REVIVE-SI**　SI空头恢复；周涨近3年前20%、ADX<22、利多price-in、基差/库存/利润三链反向；政府或自律完全成本底（自律覆盖90%产能）；触及成本底则沽空逻辑失效、从严并政策逆风×0.5；涨停/4%+脉冲后3日不追空、节点±1不新开；例外：JM/J反弹做空不开放；RB空头不在白名单；旧原料评估冻结解除关注提涨受阻/钢厂减产仍不绕池许可；解除/更新：规则/数据齐。

## 3.1 当期配置（拟议框架状态，非交易许可）

<a id="r-dynamic-version"></a>
**DYNAMIC-version**　截至北京时间2026-10-11，拟议方法v2.28；行情最后完成日2026-10-09，已提交的2026-10-10快照（AS_OF=20261010、行情脚本v1.16、末行“快照完成”）为行情锚。2026-10-11元研究、变化检测与原版执行审计按当时已生效v2.27完成；拟议框架待合并才生效，原审计不回写。脚本v1.17本期仅同步EVENTS配置与版本元数据，尚无新市场重跑；不得从版本号推导新行情。公开原文、原站AI摘要、交易所表转录与仅搜索结果按各自质量记录，账户/实际持仓/收益未知。

<a id="r-dynamic-caps"></a>
**DYNAMIC-caps**　用户2026-09-06配置：参考ACCOUNT_SIZE=150000元；单笔及常规组合上限=净值3.5%（参考5250元）；LOW_EXPOSURE_RISK_CAP=5000元，低敞口组合上限取min(常规,5000)，不设低敞口单笔比例乘数。**RISK_REGIME=unknown**：当期15项适用触发及账户未全核，#16不可预判；portfolio_cap、portfolio_remaining、final_lots=null。可明确标normal/low_exposure两种参考情景，不能作许可或填实际占用；已核触发后才按[RISK-regime](#r-risk-regime)计算。

<a id="r-dynamic-pool"></a>
**DYNAMIC-pool**　核心MA2701/MA2705与RB2701/RB2703；备选M2701、SR2701/SR2705、CF2701；AU2612与SC2611/SC2612仅信号、不建仓。MA/M限隔夜，RB/SR/CF常规。能源仅MA，黑色仅RB月差；RB方向多头冻结、空头不在白名单。M无已许可具体执行策略research_only；SR A分位0及夏窗结束均no_signal；CF秋窗开放但具体B计算temporary_gap。一般geopolitical_fade仍按①官方/多源事实＋SC back及自身结构；仅明确依赖专业船流/出口/战争险的旧子模型在公开替代触发定义前research_only。AU不因事件或预检容量复活，SC不因信号数据复活；JM/J、AG、CU/AL、SI/PS、LC/LH、IM/IC、TL/T仍按§2休眠或扫描复活条件。

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
**DYNAMIC-regime**　①沿用“中断证真”，本期10/09 SC近端back+22.9、5td−23.7但仍正，未见官方全面重开/停火；一次收窄不足反向两要件，9月袭船仅历史，不能冒充本期新事实。能源方向空头#26仍否决，方向多头按自身D8/#30/SC周涨/D12与#16适用性分别判，完整A配对按自身模型与风险。Fed9月加息已核，但10/08讲话不构成委员会逐会承诺；D13参数不变，复归档双条件未共证。RB五大材AI摘要仅节后线索，③/D14不据此硬判。交易所恢复条件/经纪商实收与RISK_REGIME均unknown。所有池外门按休眠适用性。

<a id="r-dynamic-cpi"></a>
**DYNAMIC-CPI**　美国10/14 CPI 08:30 ET→北京时间当晚20:30、国内T10/15；10/15 PPI 08:30 ET→T10/16；FOMC决议10/28 14:00 ET→北京时间10/29 02:00、国内T10/29，T−3=10/26、T−1=10/28、T+1=10/30。九月加息25bp至3.75–4.00%是历史已核事实；没有本期带采样时刻的FedWatch概率及同口径DXY/10Y周序列，后续逐会承诺与美元连涨中断均不可填。D13−0.3/×0.5/C门槛4.8及复归档“10/28按兵或转鸽＋美元连涨中断周度确认”原条件保留；AU仅信号，#29仅原适用AU/AG并按T−10核重入，不外推全池。

<a id="r-dynamic-iron-sample"></a>
**DYNAMIC-iron-sample**　Mysteel原站2026-10-07 AI摘要：螺纹产量170.27万吨/周−1.96，**五大材总库存**1548.44万吨/周+85.50（对9/30同系列），底层表未读，假期效应未分解；不是RB单品种库存，也不作D14硬fail。10/09螺纹137厂原文仅搜索线索、不能写已核。焦炭10/09第二轮提降仅发起/预期、落地未核；铁水/盈利率为参考。下一完整周同样本原表、前瞻价格确认及独立因果到位后复评RB A。

## 3.4 事件与当前护栏

<a id="r-dynamic-events"></a>
**DYNAMIC-events**　国庆10/01–10/07休市、10/08首个国内响应日、10/09第二日；9/30长假T−1及9/21、9/29公告±1窗均归档，不能续为本期已命中。10/04 OPEC+七成员维持11月产量目标（已读新华社正文，OPEC原声明未直读），目标配额不等于实际油流或①重开。USDA WASDE排期10/09 12:00 ET＝北京时间10/10 00:00，晚于M周五夜盘，首个可能国内响应日10/12；报告正文/大豆数字未核，拟议脚本仅window_only/auto=False人工提醒，不自动生成D12或新开禁令。俄禁令旧9/30到期报道/拟延期未取得本期官方法令，不作当前官宣质变。未来官方CPI/PPI/FOMC时间及国内T见[DYNAMIC-CPI](#r-dynamic-cpi)；不可排期①双向质变按0.1/1.4日度核。交易所节后保证金回落须实际满足非单边市等条件并核经纪商实收，未核不能自动解除×0.8或宣布仍命中。

<a id="r-dynamic-gap"></a>
**DYNAMIC-gap**　CPI/PPI与FOMC±1、地缘质变±2等按canonical 1.3各品种规则取适用池；M的WASDE±1 gap1.3仍人工核，脚本window_only不自动生成D12/新开禁令；九月提前窗已到期。MA①未缓和期间gap上限1.2，受交易所扩板的历史压力场景不得代替本期实际合约涨跌停参数；AU信号/AG池外仅历史存量适用，SC信号不建仓。

<a id="r-dynamic-freezes"></a>
**DYNAMIC-freezes**　10/09行情已核：MA2701 10/08结算+7.26%、10/09+5.50%，#30顺向单边新开分别冻结3真实交易日；MA主力MA2611周涨+14.86%/上尾99.4，D8方向性多头否决；SC2611两端结算9/30 696.10→10/09 741.30，周涨+6.49332%命中MA多头>5%减50%/加仓权×0.5，未命中>8%冻结清仓。MA ATR分位94.8、M93.1、SR85.0高波；RB55.2常规、CF37.0/AU21.9低波；池内极差72.9>50错位，D12按实测逐品种及事件T−3，不由SC OHLC缺失抹去专用结算证据。#16因regime未知不预判，#26能源方向空头仍因①未缓和否决；完整1:1 A配对豁免单边D8/#30/D12/#16，但不豁免A证据、止损费用、双腿保证金及组合上限。实际账户与历史处置量unknown。

<a id="r-dynamic-deadline"></a>
**DYNAMIC-deadline**　9/12光伏调减数据硬截止后“无法核验”、光伏F腿新开中性冻结（非罚则、无叙事扣减、存量不动）属旧有效条件，SI/PS池外；数据到即按#23原条款裁决，不把旧9/18报价当本期事实。

<a id="r-dynamic-pv-date"></a>
**DYNAMIC-pv-date**　光伏能耗国标2027-01-01实施日期仅旧纳入口径链待核；不替代产能实际退出/调减达标，不授池外品种复活或新开。

## 3.5 待办与模型分层

<a id="r-dynamic-pending"></a>
**DYNAMIC-pending**　按本期原版执行审计与拟议重评逐候选保留身份和gap.kind：MA domestic_public做空路线10/03结案，须**国内装置复产定量／到港回升／太仓或江苏同口径基差走弱至少一项，且冻结v1自身价格确认**方可复活；当前对S/H20逐日两日确认未输出，具体模型temporary_gap。MA准备对33/31/31、远腿量缺；隆众港库30.51万吨/周−8.84仅转引、观测日10/07或10/08冲突、原表未读，optional_context，不能代#5；99期货所载10/09郑商所仓单表公开转录5316张/日−182仅可交割供给，交易所原表未读且注销/假期机械原因未除。RB补同品种同样本原表、前瞻价格确认及独立产业因果；CF-autumn B须三年同窗B-HISTORY、pre_window_low5、Entry_raw、独立需求和真实planned_exit；SR本轮A/B no_signal，M无许可策略research_only。全候选计划、账户净值、真实持仓/挂单、费用、保证金及限仓未知，final_lots=null。9/19两份MA影子均not_filled，不推真实成交/收益；审计记录更新不得改其机会身份或事前门。

## 3.6 过度反应与脆弱叙事

<a id="r-dynamic-overreact"></a>
**DYNAMIC-overreact**　MA分位100、仓单−182或SC back 5td收窄不等于domestic_public做空价差/地缘fade许可；仓单不是港库总量。RB五大材节后累库不等于RB单品种方向、D14硬fail或空头许可。9月加息不等于今后逐会承诺；D13双条件不据个人讲话解除。SR夏窗结束为no_signal，CF窗内但模型temporary_gap，M无具体策略research_only，勿把增强数据缺失扩成全池incomplete。旧PR#38未合并，旧9月公告/长假风险窗不能延至本期。任何单边护栏解除均独立核其他门；结算命中和账户实际处置分开。

<a id="r-dynamic-narratives"></a>
**DYNAMIC-narratives**　按[PEN-narrative](#r-pen-narrative)仅对实际适用候选评分，每项0–3负向；历史与池外不进当前执行分母：

- “SC back收窄或OPEC+目标按兵＝官方重开、能源空头可做”：10/09 back仍+22.9、5td−23.7，目标配额不证实际油流；官方事实＋back反向两要件未共证，#26继续。
- “9月加息＝委员会逐会连续加息、贵金属必持续回吐”：9月已加息与10/08 Waller个人讲话不能合成委员会未来承诺；当前FedWatch/DXY同口径周线缺，D13旧参数及双条件保留，AU只信号。
- “MA分位100或仓单−182＝做空价差已确认”：分位仅筛选，仓单仅可交割供给、注销/假期机械原因未除；港库转引观测日冲突，domestic_public 10/03结案，三项国内复活证据择一且冻结v1自身价格确认未共证。
- “五大材节后累库＝RB方向性空头或D14硬fail”：Mysteel原站AI摘要属多品种/假期线索、原表未读；RB A77.2仅筛选，D14限已成案且实际依赖该假设的计划，空头不在白名单。
- 【9月历史、未本期重核】“单日放量＝权益资金结构已修复”：9/18成交/两融仅历史，②''未据此升级；IM/IC池外。
- 【池外历史、未本期重核】“自律锁价＝产能出清”：自律不等于不可逆退出，③与#23原门不变；SI/PS/AL/LC池外。
- 旧“永久关闭/近月无限强”等历史案例仅注记，不入本期评分；证据到位后按原评分和许可范围复评。
