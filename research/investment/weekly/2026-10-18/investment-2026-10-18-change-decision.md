# 元框架变化检测结果

## 0. 上期预备观察项复核

generator=codex；日期2026-10-18；当前有效规则为PR #45已合并正文。10/11正式研究/变化/适配已完整读取，初选handoff=null，经[桥接审查](evidence/adoption-bridge.md)核验Git采纳。下表区分既有规则、历史提案、当前观察和逐股完成。

|观察项/有效身份|本期证据与结果|接续|
|---|---|---|
|D5深化，已采纳；R21退出，已采纳且定义已齐|10/16成交1.5554万亿、科创50 1358.65；10/15完整两融日差-319亿。深化triggered；R21及原重建not_triggered。14–16窗口已有量能失败；10/16深北两融缺失|维持冻结/P2暂停；不把单项缺口解释为通过；账户null|
|UST五日复评，已采纳|同一CMT最新五发布日10/9、13–16十年均>5%，triggered；30年降至5.43%只是水位，未再创新高|受暴露高估值公司pending；原报告未提供公司完成配对|
|CPI/FOMC出口，已采纳|9月3.7%、核心环比0.3%触发既有观察分支；>4%分支not_triggered；FOMC未来决定unknown|CPI已过窗立即按实际暴露复核，不能继续机械沿用48h日历冻结；其它Gate独立|
|S.5548，已采纳R6/Precheck#5跟踪|IS正文点名中际/新易盛；档案最后列9/24，最新全行动链未完整获取|命名敞口复评pending，最新进程unknown；不能据IS页宣称绝对无进展或已全面禁采|
|油价/IEA/PPI，已采纳R14|IEA供给恢复且冲突/需求破坏并存；现货/期货仍不齐。PPI购进6.9/出厂5.0，差1.9|PPI state_refresh；期货连续阈值unknown；从严及85情景沿用|
|贵金属，已采纳R17|同口径金/美元连续系列未齐|触发unknown，旧累计两档提案不采纳|
|政策第二环，已采纳R19|健康大会为方向证据；9/15、18规划进入4–8周区间，逐公司第二环证据未知|原事件日期继续，不凭周更/换版重置期限，不假定所有公司都未落地|
|AI与创新药兑现，已采纳验证链|台积电新增海外Q3实绩，A/H自身财务待核；恒瑞首付仍只证实待条件合同，AZ款付Summit|受影响公司pending，均无本handoff可核完整报告/JSON完成凭证|
|猪链旧子映射，历史观察|旧10.3为9月下旬旬价，本期新旬价未取|不复活失效映射，也不把旧价当当前企业售价|
|内需解除，已采纳R20滚动月度|9月PPI已补；同月社零/单月贷款同比原文未齐|unknown，维持既有约束；不以9月锁死后续月份|

## 1. 基本信息

研究/截止日2026-10-18，交易行情10/16、完整两融10/15。发布基线22b1cf1；deployment_status=deployed。canonical完整哈希b26daf1d3cc601e34682effbe46bb88b064190410de94886546fce7a79378a3a；compact 7c588fba94eb81f9629fe22f6266243c31121e44384ec7a1785c330c7231ada8。两份实际来源见[冻结方法](evidence/investment-2026-10-18-handoff-methods/investment_framework.md)及[桥接](evidence/adoption-bridge.md)。本期完整输入为[market-research](investment-2026-10-18-market-research.md)；历史10/11报告的确切哈希在handoff的baseline审计字段中，旧change正文只供纠错，不再作为有效决策来源。

## 2. 总结论

- state_refresh=true：补CPI/PPI、最新利率、A/H行情/两融、外部先进制程实绩、政策与日历；深化及既有买入限制延续。
- evidence_correction=true：撤回10/11旧change-decision的当前有效决策身份，纠正其“仅12月点阵可证出口”和“R21尚待定义”在PR #45之后仍被使用的风险；新证据的披露日、口径和缺项明确记录。
- method_change=false；update_needed=no，update_level=none。没有新阈值、权重、逻辑、适用范围或解除路径提案。CPI达到原观察条件并非新增永久冻结条件，剪刀差轻微收窄不足以调整框架机制权重。
- 明确采用本期状态/纠错handoff，绑定已采纳旧方法副本；框架仅将受限事实观测块同步10/18，仍用单一PR待审。PR未合并不阻断本期日志和handoff发布。混排D正文保留其10/11历史日期，读者按新handoff重算当前状态。

## 3. 新旧七变量比较表

|变量|10/11正式报告（经桥接的历史事实）|10/18当前|级别/分类|
|---|---|---|---|
|MAIN_CONTRADICTION|高长端/成本，节后两日反抽，科创破线|缩量和完整两融偿还继续，外部真实盈利不能替代本地兑现|重要/state_refresh|
|DOMINANT_RETURN_DRIVERS|盈利研究优先+政策(a)，实现归因null|新增台积电实绩；供给与健康政策继续待本地传导，实现归因仍null|边际/state_refresh|
|KEY_CONSTRAINTS|9月美CPI/PPI待核；CMT10年5.24、30年5.60|美CPI3.7/核心环比0.3；国内PPI5.0/购进6.9；CMT5.09/5.43|重要/state_refresh|
|PRIORITY_MECHANISMS|六类框架高/中高/中；元研究漏单列供给型|完整单列六类，权重不改，深化维持|覆盖纠正/evidence_correction|
|FRAGILE_NARRATIVE|节后流入/反弹即解除|利率下降/外部业绩/政策即完成承接|边际/state_refresh|
|TOP_MISTAKE_TO_AVOID|提案当执行、代理当真值、BD归属错|旧接续被误当现行方法、触发被当逐股完成|重要/evidence_correction|
|PRECHECK_ITEMS|10/14CPI、量能/两融、第二环/三季报|CPI已落地按暴露复核；10/27–28FOMC、滚动内需、具体公司完成凭证|重要/state_refresh|

## 4. 重要变化项

1. kind=state_refresh；old_value=美国9月CPI未知、长端5.24/5.60；new_value=CPI3.7/核心环比0.3、长端5.09/5.43；change_direction=价格压力观察条件兑现、长端边际下降但五日仍>5%；change_type=原规则输入；importance_level=重要；research_meaning=继续检验盈利对冲而非单押降息，>4%独立分支未命中；downstream_impact=受暴露成长/港股高息定向pending，无全市场统一过窗冻结。
2. kind=state_refresh；old_value=两日成交和融资代理；new_value=10/16量能<1.6万亿、科创1358.65、10/15沪深北完整两融日差-318.998亿；change_direction=深化维持；change_type=同口径补证；importance_level=重要；research_meaning=不以反弹/ETF成交替代退出三项合取；downstream_impact=R21 not_triggered、原重建not_triggered，缺10/16深北不可补零。
3. kind=state_refresh；old_value=9月PPI未核、8月剪刀差2；new_value=9月出厂5/购进6.9、差1.9；change_direction=小幅收窄且投入上涨仍强；change_type=成本输入；importance_level=边际；research_meaning=分行业转嫁与利润率仍需验证，内需解除不能由PPI替代；downstream_impact=V50收入/利润率及V5原纪律沿用。
4. kind=state_refresh；old_value=美光外部锚/专项规划；new_value=台积电Q3实绩、健康大会方向、IEA恢复与供给脆弱并存；change_direction=增加外部事实并保留传导缺口；importance_level=边际；research_meaning=区分收入归属、供给/需求与政策(a)/(b)；downstream_impact=逐公司在手订单/回款/第二环，不改机制归型默认。
5. kind=evidence_correction；old_value=10/11change仍写当次无SEP则等12月、R21定义待补；new_value=PR #45已合并的完整出口及滚动规则；change_direction=纠正有效性身份；importance_level=重要；research_meaning=避免永久等待与旧证据复活；downstream_impact=withdrawn_sources绑定旧change全文hash，保留审计，只接纳本期重新核验结论。旧报告未单列供给型的输出遗漏本期补足，不当方法新增。

## 5. 方法变化审议

无method_change，不制造方法提案。原核心估值、Terminal r/g/N/K、P1/P2比例、R1–R21/D1–D8、R3合取例外、R6实质暴露、R19原事件计时、R20滚动同月、R21三日退出与独立重建均沿用。受限观测块只存事实，正文方法指纹不变；不通过观测块写入新的阈值、动作或解除条件。

## 6. 不应过度反应、待复评、撤回与兼容影响

待复评：SZ-300308中际旭创、SZ-300502新易盛（S.5548命名敞口/海外订单与三季报）；SH-600276及HK-01276恒瑞（合同交割/到账/收入）；HK-09926康方（Summit投资和上市公司收入归属）。这是旧未完成事项的显式桥接队列；触发日为原披露日9/24、9/29、10/5，识别/复核日10/18，不能伪造为公司已研究或重启七天时钟。对本期CPI和利率触发，公司适用范围仍须从实质暴露筛选；没有真实持仓和估值依赖清单，不虚构公司名单。

上述五个证券均pending，completion=null；已有本地公司研究不在本worktree共享历史中，未核配对不声称completed或“从未研究”。本次不自动创建公司批次、不改七天冷却、不执行交易。临时市场/事件冻结且事实可靠时可估V50/V5/冻结P1；P2不得active；必须逐项合取解除所有适用阻断。

withdrawn_sources=[research/investment/weekly/2026-10-11/investment-2026-10-11-change-decision.md 的完整sha256]，目的为停止该旧全文作为当前有效决策输入，历史事实仍可从独立原始资料核验。supersedes=[]（首次无旧handoff），撤回身份持续跟随本期已采纳handoff，今后不得因切方法复活。无整体方法兼容证明；本期观测PR与当前方法仅唯一JSON块不同，方法指纹一致，合并后仍需以实际两份字节新建方法状态接续。

## 7. 结构化输出

```yaml
MAINTENANCE_CLASSIFICATION:
  state_refresh: true
  evidence_correction: true
  method_change: false
FRAMEWORK_UPDATE_DECISION:
  update_needed: no
  update_level: none
  decision_reason: "原规则输入刷新及旧决策有效性纠错；无新增方法。"
KEY_VARIABLE_CHANGES:
  - {kind: state_refresh, variable_name: 海外分母, research_meaning: CPI观察分支兑现而非CPI大于4硬阈值}
  - {kind: state_refresh, variable_name: 负反馈, research_meaning: 深化延续且退出及原重建未达}
  - {kind: state_refresh, variable_name: 成本与兑现, research_meaning: PPI差略收窄而本地盈利及内需解除仍待证}
  - {kind: evidence_correction, variable_name: 旧决策身份, research_meaning: 合并后出口及R21按现行方法重评}
UPDATE_FOCUS: [独立状态交接, 来源撤回, pending接续, 事实观测PR]
DO_NOT_OVERREACT_ITEMS: [不因反弹解冻, 不用代理补完整两融, 不将CPI3.7写成大于4, 不将外部报表算本地盈利, 不按换版等待新信号]
RULE_EVALUATIONS: "见handoff完整对象"
PENDING_COMPANY_REVIEWS: [SZ-300308, SZ-300502, SH-600276, HK-01276, HK-09926]
COMPLETION_EVIDENCE: []
WITHDRAWN_SOURCES: [investment-2026-10-11-change-decision.md]
```

来源及读取范围：[来源账本](evidence/source-ledger.md)。验证另见随包`evidence/validation.json`及适配报告；结构检查/离线回归不证明市场事实、投资有效性或账户交易。
