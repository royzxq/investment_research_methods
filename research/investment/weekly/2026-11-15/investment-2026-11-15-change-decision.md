# 元框架变化检测结果

## 0. 上期预备观察项复核

所有下列规则均为当前canonical已采纳；未合并本期观测正文不阻断现行方法状态接续。

|项目|上期证据/状态|本期结果（截止）|对象/复评与完成|
|---|---|---|---|
|D5/R21/原重建|11/06官方整数1253，出口未达|11/13整数1280仍低；R21 not_triggered，精确三日helper unknown；深化triggered|仅既定适用对象，未生成研究完成|
|10年美债|末4.86，最新五日未达；历史复评开放|末5.15，仅两条>5；新窗not_triggered，历史triggered|实际融资/估值暴露待公司核，非统一调参|
|R2|9月3.7与核心0.3，路径出口未达|10月同比缺，>4为unknown；核心0.3；无FOMC回撤证据|保留9月特定观察身份/原从严，不造本月硬门槛|
|R20|9月社零1.1、贷款缺，未解除|10月完整同月配对未齐：unknown|不混月，不以新数据待发作事实改善或恶化|
|R14/R17|同口径连续数据缺|unknown|原约束按原范围，禁止现货替期货|
|R7/R19|海外需求、政策至收入链未完成|收入/工具有新增，个股现金或传导仍unknown|状态刷新不代表二链已兑现|
|R22|两上下文有缺口|份额/成交与权重公告新增，实测/前瞻仍unknown|不按身份调P1/T1、不全市场冻结|
|R6日历|11/09及11/10待发布|现已发布转结果复核；11/16入窗，11/18 NVDA尚未入窗|只看实质暴露；到期不自动解冻|
|§4.1A–D|11/12与11/14新方法已采纳|main部署核验通过，取数与未来完成按实际合同|当前报告未运行逐股DCF或分红估值|
|五pending|9/24、9/29、10/05旧触发|继续pending，completed=0|恒瑞A配对存在但触发事项/兼容未完成，见inventory|

## 1. 基本信息

研究日2026-11-15；行情截止11/13；最新资料于本次02时段读取。当前报告：[market-research](investment-2026-11-15-market-research.md)。市场基线11/08（sha256 ebc6283e87acebac9f54187ec0e5752160ebdd88ac227665c69bc3f3e4923ab9）；方法变化比较11/14（sha256 fa097a1023bec9d475672b1151aa9e542ca9d99e25861e767ed63f6eda4891b1）。当前两份正文哈希及已合并采纳见[adoption-review](evidence/adoption-review.md)。main基线a690373cef83d2ff624ad7f74b4c14c7ccca5214，deployment_pending=false。

## 2. 总结论

state_refresh=true；evidence_correction=false（本期无新增错误源，四项历史撤回继续）；method_change=false；update_needed=no，update_level=none。没有新增永久定义/阈值/范围/权重/例外/退出。需要刷新canonical/compact原位受限观测块，仍走单一PR；实际状态采用不等PR。既有11/12–14方法的合并属于本期输入确认，不另开第二套方法提案。

## 3. 新旧七变量比较表

|变量|11/08基线|11/15新证据与变化等级|对框架含义|
|---|---|---|---|
|MAIN_CONTRADICTION|需求/成本与外部利率压力|重要：PPI价差2.2pp、10年5.15；港内需求差异|既有矛盾加强，不改机制权重|
|DOMINANT_RETURN_DRIVERS|现金兑现、AI需求待传导|重要：TSMC月营收、新融资工具/治理事实|拆营收/预算/现金，不改估值方法|
|KEY_CONSTRAINTS|D5、R2、R20未解除|重要：出口仍未达；新CPI同比与10月配对unknown|unknown不等于零或成立|
|PRIORITY_MECHANISMS|六类高/中高/中|无变化，详本期机制表|取证次序不等于加仓|
|FRAGILE_NARRATIVE|反弹/政策/AI等同兑现|轻微扩展至ETF被动调仓及治理连续性|已有规则覆盖|
|TOP_MISTAKE_TO_AVOID|缺口填值、触发当完成|无方法变化；新增同比缺失与批准/执行例证|按三值与唯一计价处理|
|PRECHECK_ITEMS|完整数据、日历、五pending|重要：11/16、11/18与资本/DCF接续|滚动事件，保持168h和原触发日期|

R22补充项与七变量并存：ETF_LIQUIDITY_CONTEXT新增SSE同表周变化及S14渐进权重公告；BENCHMARK_CONTEXT保留原声明窗口，仅增同币种价格诊断；行业相对总收益归因和前瞻输入unknown。无自动定价影响。

## 4. 重要变化项

|old_value → new_value|change_direction|change_type|importance_level|research_meaning|downstream_impact|
|---|---|---|---|---|---|
|中PPI购进/出厂6.9/5.0 → 7.9/5.7|成本价差扩0.3pp|state_refresh|重要|议价与库存/合同分化|合理价值经营预测先吸收；独立残余再审计|
|10年4.86 → 5.15，核心CPI0.3保持|折现/融资压力升|state_refresh|重要|长久期与外币负债实际暴露|不统一PE/WACC或重复收利率风险费|
|日历待发 → 结果已发/新窗|时效迁移|state_refresh|重要|实际影响复评，而非日历永久冻结|公司范围须证据，不自动开批次|
|完整日线缺 → 真实API七次，末日两融仍缺|可验证性改善|state_refresh|重要|最新三日窗口确认为11/11–13|helper unknown与必要条件否定分别记录|
|ETF成交23381 →18202；份额22393→22399|成交降、份额略升|state_refresh|轻微|非净申赎，不作身份因果|容量/执行先核；不预填P1/T1幅度|
|权重公告此前未覆盖 → 公布11/06、生效12/14|补充既有事实|state_refresh|重要|不是本周突然生效或直接15%|具体基金交易与压力样本待核|
|海外AI需求证据 → 营收增与NVIDIA治理变动并存|证据更分化|state_refresh|重要|需求与组织风险独立传导|对同一损失按§4.1B去重，不按新闻数处罚|
|历史方法本地采纳表述 → 当前远端部署核验|部署确认|state_refresh|重要|以main真实正文执行新研究契约|旧冻结按旧版本；不改写历史采纳记录|

## 5. 方法变化审议

无新method_change，无待审新方法提案；因此不捏造新操作定义或进行收益回测。当前规则已经覆盖未知、ETF比较、分红、资本/风险唯一计价与DCF。若未来要加身份折扣、统一回报门槛、WACC/倍数或新冻结边界，必须完整审议定义、经济依据、范围、正反/边界案例及兼容影响，不能借本期状态PR生效。

本期三个边界复核：R21成交恰1.6或两融恰-150均不满足，指数恰1516.2可满足该项但仍须三日AND；ETF份额增长但股价下跌可导致市值减少，二级成交下降无法推出赎回；同一原料损失已进入利润预测则不能再按事件ID压低价格，缺数据保留unknown。这些是现行规则抽检，不是新方法。

## 6. 不应过度反应、待复评、撤回与兼容影响

不把美国同比缺失填9月3.7，不将本周核心0.3复制成新的永久日历门；不以香港GDP增长否认个股现金风险；不以政策预算/合作意向代收入；不以ETF成交、短期跑赢或管理层更换直接调P1/T1。临时冻结限制买入，事实足够可出冻结观察价位；P1/T1和独立研究控制保持。

五pending原触发日/历史方法/证据截止保留；只读盘点不关闭事项，也不宣称无历史研究。没有新增completed或账户成交。完整配对、适用方法、触发日和截止、必要审计/生命周期/验收缺一不能登记。当前方法与旧controls方法不声明全局兼容；新公司完成要求按本期冻结，旧合同不追补新audit字段。

继承withdrawn_sources四项：10/11错误change-decision、11/01 handoff、11/06 handoff-r2/r3；具体路径与哈希见本期handoff。保留11/08纠正的R21旧窗口10/28–30，不重写历史。supersedes选中11/14接续，防后续回落使用过时状态；撤回集合跨方法生效。无新增撤回不等于恢复旧来源。

## 7. 结构化输出

```yaml
MAINTENANCE_CLASSIFICATION:
  state_refresh: true
  evidence_correction: false
  method_change: false
FRAMEWORK_UPDATE_DECISION:
  update_needed: no
  update_level: none
  decision_reason: 现行规则覆盖新增证据，观测正文待审，状态独立采用
KEY_VARIABLE_CHANGES: 见第3至4节及handoff.changes
UPDATE_FOCUS: [原位观测块, 本期adopted状态, R22两上下文, 五pending盘点]
DO_NOT_OVERREACT_ITEMS: [同比补值, 成交当申赎, 身份调价, 单周拟合估值, 触发当完成]
RULE_EVALUATIONS: investment-2026-11-15-handoff.json
PENDING_COMPANY_REVIEWS: [SZ-300308, SZ-300502, SH-600276, HK-01276, HK-09926]
COMPLETION_EVIDENCE: []
WITHDRAWN_SOURCES: 继承四项，路径及哈希见handoff
```
