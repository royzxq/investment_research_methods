# 元框架变化检测结果

## 0. 上期预备观察项复核

以下按原规则核对；triggered表示规则触发/待复评，不表示完成或已交易。沿用旧日的历史触发明确保留原日期，本周没有重造触发日。R22是已合并方法，原七变量与新增两上下文并存。

|规则（均已采纳）|本期/沿用日期|结果|证据与边界|
|---|---|---|---|
|D5/deepening|2026-11-08|triggered|11/6官方周报科创50整数1253远低于1516.2，深化维持；原10/29量能/两融历史触发亦未被合格出口解除。仅作用适用修复承接候选。|
|R21/repair-exit|2026-11-08|not_triggered|最后日官方整数1253已否定每一天>=1516.2必要条件；完整日历/成交/两融缺，未运行真实三日helper；不再沿袭错误window。|
|D5/original-rebuild|2026-11-08|not_triggered|11/6官方科创50整数1253低于1577.36，原重建合取失败；不能因反弹或R21缺项解除。|
|UST10Y/latest-five-gt5|2026-11-08|not_triggered|11/2—6十年CMT=4.91/4.95/4.90/4.84/4.86，最新五日未全>5%；历史复评开放。|
|UST10Y/historical-review-open|2026-10-25|triggered|10/18接续确认历史五日>5%强制复评；未取得受暴露公司完成凭证，保留开放事项，不等于全市场自动冻结。 10/9首次触发的10/5–9序列见10/11未撤回市场研究，仅作历史事实。|
|R2/CPI-observation|2026-10-25|triggered|9月3.7/核心环比0.3命中原观察分支；只适用受暴露高估值成长。|
|R2/CPI-gt4|2026-10-25|not_triggered|总同比3.7不满足严格>4%。|
|R2/FOMC-release|2026-11-08|not_triggered|已补读10/28官方发布会初步逐字稿，未支持紧缩路径实质回撤；不加息单项不足，维持从严；没有固定等12月。|
|R20/domestic-release|2026-11-08|not_triggered|9月社零1.1仍未>2，同月贷款原文缺；10月社零未取得，不混期。|
|R14/new-threshold|2026-11-08|unknown|本周未取得规则需要的同合约/同口径连续数据；旧压力情景与实质暴露控制继续，不伪造新阈值触发。|
|R17/gold-dollar|2026-11-08|unknown|本周未取得规则需要的同合约/同口径连续数据；旧压力情景与实质暴露控制继续，不伪造新阈值触发。|
|R7/capex-and-orders|2026-11-08|unknown|AMD Q3收入/数据中心增长为海外正证据；A/H对应订单与OCF未核，既有R7证伪合取未被本周证实。|
|R19/policy-second-link|2026-11-08|unknown|金融工作报告及操作框架方向不证明公司采购、份额、回款或实际汇金增持；旧事件时钟不重启。|
|R6/S5548-named-exposure|2026-10-25|triggered|历史已触发复评事项仍开放；原触发日保留，最新进程/公司入账缺完成凭证。9/24原始提案命名式风险接续pending；最新全立法行动链及实际收入敞口仍unknown，无全面禁令判断。|
|Precheck2/Hengrui-settlement|2026-10-25|triggered|历史已触发复评事项仍开放；原触发日保留，最新进程/公司入账缺完成凭证。原合同预期Q4，未核交割/到账/收入，延续受影响部分核验pending。|
|Precheck2/Akeso-income-attribution|2026-10-25|triggered|历史已触发复评事项仍开放；原触发日保留，最新进程/公司入账缺完成凭证。AZ20亿美元交割对象为Summit；康方实际权益/里程碑/入账另核，原核验事项pending。|
|R6/FOMC-post-event|2026-11-01|triggered|会议已结束，对存在实质估值/融资暴露公司按实际结果复核；all是筛查范围，不是所有公司一律冻结。公司清单待定向核验，无新增批次授权。|
|R22|2026-11-08|unknown|R22已采纳且两项元研究上下文已交付；实际净申赎/匹配流动性/共同日总收益/前瞻桥未齐，未量化，不自动改P1/T1或冻结全市场。|
|R6/CN-price-calendar|2026-11-08|triggered|NBS计划11/9 09:30价格数据，11/8研究时点处48小时窗；仅实质利润/估值/融资暴露对象适用，非全市场冻结，未启动批次。|
|R6/US-CPI-calendar|2026-11-08|not_triggered|BLS计划北京时间11/10 21:30发布；11/8 21:30进入48小时窗，本次02时段尚未到。既有CPI/紧缩约束不因日历读数解除。|


五项公司pending及原触发日期保持，completed=0。恒瑞11/5 Codex配对已实际只读核查，交割仍未决、当前R22兼容验收未获，不能关闭特定事项。详情见[完成凭证清单](evidence/completion-inventory.json)；其余四证券本次未找到合格配对，不声称从未研究。

## 1. 基本信息

研究日2026-11-08（Asia/Shanghai），generator=codex；行情截至11/6，证据截至本次运行。使用已采纳stock-two-price-controls-v2-etf-relative-v1，PR61真实合并；[采纳核验](evidence/adoption-review.md)列两份全文哈希、方法指纹及上期完整市场/变化报告哈希。发布基线含新入口/helper/R22，deployment_pending=false。比较市场基线11/1及方法采纳11/6-r3，不以期货、ETF或公司报告替代市场基线。

## 2. 总结论

**state_refresh=true；evidence_correction=true；method_change=false；update_needed=no；update_level=none。** 状态与纠错按用户本次授权采用并发布main；canonical/compact仅拟同步受限观测JSON，仍走一个PR人工审核。没有新方法提案，也没有把既已采纳R22再报成本周新增方法。

重要纠错：11/1、11/6-r2/r3 handoff的R21.window=10/21—23与11/1计算/摘要的10/28—30不一致。本期撤回错误状态包并supersede，新包更新11/6证据且明确未有完整三日组；历史not_triggered结论不变。旧文件不覆盖，旧方法真实采纳凭证及来源正文不抹除，10/11既有撤回继续传播。

## 3. 新旧七变量比较表

|变量|上期已采用市场证据（11/1，行情10/30）|本期（行情11/6）|程度与方向|
|---|---|---|---|
|MAIN_CONTRADICTION|海外云与分母改善未穿透国内订单/杠杆|AMD需求继续、利率下降与政策操作改变；内需与现金回报验证仍不足|轻微，正证据增加，核心矛盾不变|
|DOMINANT_RETURN_DRIVERS|盈利兑现、具有第二环的政策重估|同；新增AMD与政策操作事实，无全市场实现归因|轻微，非新权重|
|KEY_CONSTRAINTS|内需弱、紧缩出口证据未齐、承接未达|Fed发布会已核但不支持回撤；官方指数仍低于出口|重要，缺口收窄，约束未解除|
|PRIORITY_MECHANISMS|高三类、中高周期、中两类|六类及权重不变|无变化|
|FRAGILE_NARRATIVE|不加息/海外云/港股反弹等同解除|ETF成交/科技反弹/政策方向等同净流入与价值提升|轻微，错误表现更新|
|TOP_MISTAKE_TO_AVOID|观察/触发/可估/完成/执行混判|保留，增加R22身份/历史/前瞻及经济影响去重|重要，已采纳规则进入取证|
|PRECHECK_ITEMS|完整三日、Fed/内需出口、大宗、五pending|同，补R22匹配流动性/总收益/前瞻桥和当前事件窗|重要，补证任务更具体|
|ETF_LIQUIDITY_CONTEXT|当期未研究，不能补0|SSE汇总成交与规模已核；申赎、配对样本unknown|首次按R22交付；非资金方向翻转|
|BENCHMARK_CONTEXT|当期未研究，不能补0|A/H宽基与科技候选、币种/费用/窗口/回溯边界；前瞻未量化|首次按R22交付；非个股收益预测|

## 4. 重要变化项

|old_value → new_value|change_direction / change_type / importance_level|research_meaning / downstream_impact|
|---|---|---|
|科创50官方值缺 → 周报整数1253|数据层级改善；state_refresh；重要|反弹仍低于1516.2与1577.36，维持适用候选深化；不造精确收盘或完整三日helper结果|
|十年4.94/30年5.31 → 4.86/5.26|边际下降；state_refresh；轻微|最新五日未触发>5，但历史复评保留，非从严路径自动退出|
|Fed发布会未核 → 已核未见回撤依据|unknown收窄为出口未触发；state_refresh；重要|证据不足的子项已实际阅读，既有从严继续，不增加新日历锁|
|旧操作锚 → 11/2隔夜1.25%操作5410亿元|期限/机制背景改变；state_refresh；重要|不同期限不作简单降息比较，净投放/市场融资成本未核；合理价值不自动提高|
|海外云背景 → 新增AMD季度证据|外需正证据增加；state_refresh；轻微|保留订单—交付—毛利—OCF桥；不证明国内同链每家公司已兑现|
|两R22字段缺 → 身份/成交/产品/窗口与unknown完整交接|研究覆盖改善；state_refresh；重要|成交不算申购、旧费率不当当前确定值；同一经济影响按合理价值/未吸收风险/执行容量/机会成本去重，由公司审计裁定|
|R21.window错写10/21—23 → 明确历史10/28—30及本期末日否定证据|结构化证据纠错；evidence_correction；重要|防止后续模型用错窗口；不改阈值/AND逻辑，不把纠错当新增方法|
|上期事件日历 → 11/9中国价格、11/10美国CPI|state_refresh；重要|以真实时间与暴露适用R6，未来值null，非全市场同冻|

R22经济影响去向：政策/盈利事实如已进入正常化利润或倍数，不再通过ETF/alpha标签重复奖罚；价差/深度如已进风险折扣或执行容量亦不重复；ETF净值已扣费用不再双扣。现有事实无法量化任何公司剩余机会成本，P1/T1均不由元研究改价。

## 5. 方法变化审议

本期无方法变化、无待审新规则。无新增权重、阈值、比较符、AND/OR、适用对象、例外或退出路径。R22既有方法完整定义仍以canonical §6.6为准；不引入ETF身份奖罚、统一alpha门槛、固定全市场回报底线或新基准挑选规则。当前诊断窗口是本次研究声明，不替代个股既有窗口。若未来提出永久修订，须补齐definition/economic_reason/scope/positive_case/negative_case/boundary_case/compatibility_impact后走方法PR；本次不制造空提案。

## 6. 不应过度反应、待复评、撤回与兼容影响

- 不由周涨/ETF成交推断申购、因果流动性、风险调整alpha或前瞻回报；unknown不是0，也不自动冻结全市场。行业与ETF表现只能提供复评线索。
- 不由Fed暂停、收益率下降或操作期限改变解除既有从严；不由资料缺口断言公司不可估。事实足够仍可估并给冻结观察P1/T1，entry/add/holding按独立scope保留，账户null。
- pending：SZ-300308、SZ-300502、SH-600276、HK-01276、HK-09926。原触发日、历史方法来源与168小时冷却保持；完成需完整同证券/日期/生成端报告与JSON、覆盖触发的证据截止及方法接续/兼容验收。没有新增公司批次授权，未启动。
- 撤回三个有误状态包（11/1、11/6-r2、11/6-r3）供消费使用；历史方法采纳/源文档不撤回。继续撤回10/11错误变化报告。新handoff逐项承接未决事项与旧撤回，避免切回旧方法时错误证据复活。两份正文只有观测块拟变，方法指纹须验证相同；当前状态/纠错不等框架PR合并。

## 7. 结构化输出

```yaml
MAINTENANCE_CLASSIFICATION:
  state_refresh: true
  evidence_correction: true
  method_change: false
FRAMEWORK_UPDATE_DECISION:
  update_needed: no
  update_level: none
  decision_reason: 既有规则足以处理新证据；纠正窗口元数据，不改规则
KEY_VARIABLE_CHANGES:
  - kind: state_refresh
    research_meaning: 科创反弹仍未达出口、Fed发布会不支持路径回撤、政策操作及日历更新
  - kind: state_refresh
    research_meaning: R22两上下文进入市场交接，前瞻缺口保持未量化
  - kind: evidence_correction
    research_meaning: 撤回R21窗口错误状态包，原判断不变
UPDATE_FOCUS: [采用状态和纠错接续, 原位观测块PR, R22按经济含义去重]
DO_NOT_OVERREACT_ITEMS: [不以ETF身份改价, 不以历史回报作预测, 不因缺口全市场冻结, 不把触发当完成]
RULE_EVALUATIONS: 本文第0节及同日handoff的完整数组
PENDING_COMPANY_REVIEWS: [SZ-300308, SZ-300502, SH-600276, HK-01276, HK-09926]
COMPLETION_EVIDENCE: []
WITHDRAWN_SOURCES: 同日handoff中带内容哈希的四项，旧10/11撤回继续
```
