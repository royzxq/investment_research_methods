# research_controls 语义审查与最小精简方案

审查日期：2026-10-19，Asia/Shanghai。生成端：Codex。状态：**审查完成，修改方案待采纳；未修改框架、技能、业务代码或生产数据。**

## 1. 结论与范围

保留协议标记、P1/T1 和 entry/add/holding 独立研究判断。当前需要改进的是条件的生命周期、作用范围、来源裁决和执行载荷，并非用一个 `P1=reject` 取代全部控制。建议先修语义，再压缩载荷；不新建通用规则引擎或另一份可变控制状态库。

本轮覆盖：当前生产 CSV 全部有 controls 的记录；四份同日两端报告及其价格地图；canonical/compact 的 R1–R21、D1–D8、价格与持仓条件；stock-research 输出/审计与 runner/验收脚本；发布、monitor、候选复评、sell_agent、回测和执行前门禁。只核已有规则与程序行为，**未联网重评公司或宏观事实，也未重新估值、调整阈值、刷新市场状态或验证投资收益。** 文中公司经营、宏观及日历数字仅转述被审查文件。

输入冻结于 **2026-10-19 08:46:29+08:00**：

| 输入 | 结果 |
|---|---|
| `ai_investment/investment_prediction.csv` | 998 条历史记录：996 条 legacy、2 条 v4；不是 998 只股票 |
| CSV SHA256 | `fccdb7ba35401ce3a1d0d207849bfb9e72a1bfbdf9632f5e45481580b3a71012` |
| 长江电力 600900 | 第998物理行；controls 6,092字符；20条scope投影、13个独立ID |
| 迈瑞医疗 300760 | 第999物理行；controls 4,484字符；14条scope投影、9个独立ID |
| 合计 | 34条scope投影、22个“公司+ID”；15 blocking、6 unknown、1 not_applicable；21个未解项 |
| 当前持仓控制 | 6个独立holding复评ID，均为review_holding；没有已确认invalidated/exit_required |
| 两端源研究 | 4份报告+4份价格地图，共30个源约束；8组跨端同ID，scope/action/status相同，但解除正文不同 |
| 本地版本 | methods HEAD `9a5e70d`；AI HEAD `a64a873`。两边既有用户工作保留 |

methods 工作目录尚未包含 PR50 后续修复提交 `0ed4d74`；本轮另外只读核对修复工作树，确认防降级和 maintenance v4 审计验收已修，不将其重复列为新问题。PR合并、当前工作目录部署、实际生产运行是不同事实；本轮未拉取或切换分支。

当前 CSV 每个scope的状态为：

| 公司 | entry | add | holding |
|---|---|---|---|
| 长江电力 | blocked | blocked | unknown |
| 迈瑞医疗 | blocked | blocked | review_required |

上述是现状，下面分类和方案不会立即改变这些值。

## 2. 三类职责及可持续保留的边界

| 类别 | 应保存什么 | 谁判断与更新 | 不应发生什么 |
|---|---|---|---|
| 持续研究裁决 | 已确认的冻结/否决、必要资格证据缺口、当期追加计划取消、已触发持仓复评、确认失效/退出；写清适用范围和解除证据 | 研究形成裁决，发布端验收、合并和接续，后续证据复评显式解除 | 不能因价格下跌、时间过去、模型缺席或代码回滚消失；也不能无依据新增解除门槛 |
| 运行时动态条件 | 当前价格相对本次有效P1/T1、原最低收益要求、账户/预算/风险尺度等；动态数据带实际可用时点 | 由已有价格、风险和执行属主使用当时可用数据重算 | 不把研究时点的命中状态永久锁存；不另造模型高档P1作为隐藏买价 |
| 观察与研究触发 | 未触发条件、风险提示、一般经营监控、仅参数敏感性、待收集的非必要信息 | 报告完整条件表及monitoring；触发后依原规则创建复评或形成具体限制 | 不因“值得看”就生成blocking/unknown；观察、复评、冻结、失效、退出没有默认自动升级链 |

**混合条件必须拆开理解，但不能因此自动解除。** 例如R6的“是否入48h窗口”可动态计算，但“公司是否实质暴露、预案是否充分、事件结果是否支持解除”仍需证据裁决；D5/R21的市场数值可计算，但退出深化不等于公司研究完成。动态数据由谁提供、时效如何校验、回测是否可得，必须在迁移前有明确属主；没有这些条件时不把旧unknown直接改成eligible。

持仓复评的“blocking”表示**复评事项已经触发**，不表示投资逻辑已被证伪，也不表示已执行卖出。复评待补证应留在holding范围；如确需阻断新增，须由对应规则明确提供entry/add依据。整个v4合同缺失/损坏与完整合同内holding-only缺证须区分，前者仍阻止新增。

## 3. 五项关键发现

### 3.1 纯价格等待进入了无限接续的研究限制

`PRICE_ABOVE_P1_HIGH`以entry/eligibility/blocking进入实际CSV，原因是研究时价格高于某端P1高档。发布合并器对所有blocking/unknown按ID+scope保留，最终门禁只看状态，不读取该文本并重算价格。

内存隔离测试仅保留该项，模拟价从29.38降至20.00，后者低于生产发布P1=21.24，仍将BUY改为HOLD。原文还要求“重新走Gate”，所以不能把该条解释成研究者已经授权仅凭跌价解除；本轮证明的是**职责和生命周期混杂**，不是证明发生了真实漏买。两只股票均另有独立限制，删掉纯价格项也不等于可买。

对应位置：[持续接续](/Users/xinquanzhou/Workspace/ai_investment/src/analysis/research_controls.py:93)、[最终门禁](/Users/xinquanzhou/Workspace/ai_investment/src/decision/research_eligibility.py:166)、[既有P1价格判断](/Users/xinquanzhou/Workspace/ai_investment/src/decision/decision_core.py:716)。当前实际价格核心已经判断“现价≤P1且原最低收益要求满足”，无需再增加一个持久价格闸门。

上游还存在诱因：`stock_price_map.py:275–276`要求tracking/observation不得eligible。**最小澄清是buy_candidate代表研究资格，现价未到P1仍由价格核心给HOLD**，不把“当前不买”误写为研究资格被拒。保留真正因研究证据不足而tracking/observation的限制，不必为此完全重做mode枚举。

### 3.2 holding-only unknown 被扩大为全部新增限制

methods审计要求`review_holding`仅作用holding，并允许holding未知而entry/add依然eligible；AI最终门禁却把任何`holding=unknown`作为禁建仓、禁加仓的理由。当前长江的蓄水批准期限缺证经合并将holding变成unknown，而源报告两边holding摘要均是review_required。

内存夹具确认：完整合法合同内仅holding/review_holding/unknown、entry/add eligible，methods投影验收通过，AI却阻买；把同一holding事项改为review_required则不阻买。[methods范围](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_consistency.py:341)、[AI跨范围条件](/Users/xinquanzhou/Workspace/ai_investment/src/decision/research_eligibility.py:179)。现有测试甚至明确锁定该行为，因此不能借“字段压缩”悄悄改掉；应作为范围语义修正，单独列行为差分和回归。

建议：holding-only复评/缺证不自行扩scope；确认invalidated/exit_required和缺失v4合同继续阻新增；已明确声明的entry/add未知照常阻对应暴露。不对含糊历史项一刀切解除，应逐项确认其实际适用范围。

### 3.3 约束身份和多来源解除要求未充分裁决

长江`R4`与`R4_PARTIAL_STANDING`高度重叠，`HYDRO_Q3`与`HOLD_REVIEW_Q3`部分重叠且后者混入价格因素。按字符串ID保留会形成重复未解项；直接按名字相似去重又会丢掉不等价条件。

另有8组跨端相同ID：长江ADD_PLAN_CANCELLED；迈瑞D5/R9/R4/R6_CN/ADD_REPAIR/H_PLEDGE/H_MARGIN。当前CSV在同ID同scope同等级时只选择一份约束正文；本次8组均保留Codex版本，`sources`只留各端状态/refs，不包含另一端完整解除条件。夹具颠倒两来源顺序，状态相同而保留下来的解除正文变化。[来源选择](/Users/xinquanzhou/Workspace/ai_investment/src/analysis/research_controls.py:104)。**完整JSON很长，并不等于完整保留了全部来源含义。** 本轮未证明这些分歧已导致错误解除，但当前载荷不足以自证已完成来源裁决。

最小改法：规范“规则身份+具体事件/计划实例”，跨端别名做显式映射；合并前保留各源证据和分歧，形成一份可追溯的最终裁决。不同R6事件不能误合并，追加计划ID须限定研究期/计划实例。只对除scope外语义完全一致的记录合并scope，禁止自然语言模糊去重。D5现有阶段检查不能因别名绕过。

解除逻辑分两层：scope内**所有独立有效阻断合取**；单个规则内部按canonical允许的AND/OR和复评路径判断。文本数组不是可执行逻辑，非空evidence也不证明全部条件真实满足。不建议开发通用表达式语言，应由研究者写清必要条件/替代路径/仅触发复评，并由发布审查保留裁决。

### 3.4 执行范围与复评恢复入口有断点

monitor明确不掌握真实持仓，传`position_known=False`，于是entry/add都要eligible；回测和执行前门禁按实际持仓分别选择。其保守行为应保留，但必须披露“可评估首笔、不可追加”，不能声称通用monitor已经完整实现两种资格的独立展示。[monitor](/Users/xinquanzhou/Workspace/ai_investment/scripts/investment_monitor.py:933)。

同时候选筛选只收BUY/SELL。即使控制变化被标为forced=True，被禁买后落在HOLD的股票仍可能不进入候选复评；夹具中forced=True而活跃候选数为0。显式`--candidate`、财报事件和陈旧提醒等仍是可用入口，但**不能把forced标记等同于已安排恢复研究**。[筛选](/Users/xinquanzhou/Workspace/ai_investment/src/decision/candidate_review/selection.py:26)、[编排](/Users/xinquanzhou/Workspace/ai_investment/src/decision/candidate_review/orchestrator.py:60)。

建议先把持续限制的补证/复评事项接入现有定向研究待办和事件来源，记录负责入口及完成凭证；保留既有研究冷却和预算，不新增每天重跑全部冻结股票的任务，也不因任务未运行自动解冻。

### 3.5 证据载荷过重，并会触发无意义的下游工作

同条件按scope复制全文；历史sources在每次合并继续累计，正常新封口还会加入新的publication来源。候选复评、A/H配对和sell缓存用整个controls对象比较，纯seal/发布时间变化即可触发额外工作。

已复现：scope状态和constraints完全不变，只改publication元数据，候选forced=True、业务条件相同的A/H分成2组、sell缓存由可复用变为不可复用。[候选比较](/Users/xinquanzhou/Workspace/ai_investment/src/decision/candidate_review/review_gate.py:55)、[A/H键](/Users/xinquanzhou/Workspace/ai_investment/src/decision/candidate_review/pairing.py:50)、[卖出缓存](/Users/xinquanzhou/Workspace/ai_investment/src/decision/sell_agent/cache.py:223)。当前尚无容量瓶颈证据，主要问题是阅读、职责和重复成本。

应统一“控制业务变化”的比较口径，排除纯发布时间、事件ID、累计来源和重复正文。**不能只比较三个状态**：真实action/scope、适用对象、触发事实、参数、解除结果或来源分歧改变，仍须触发相应复评；财报新事实/证据新鲜度继续走既有事件与锚点更新路径，不能为减少调用漏掉实质变化。

## 4. 当前22项逐条分类

分类计数为：8项持续研究裁决，2项动态职责候选，1项当前不适用，9项混合需拆分，2项证据待澄清。**不是8项保留、其余14项删除。** 混合项中的研究限制继续保留，只有明确归属且有完整接替者的动态子项才迁出；TEMP尤其不能立即移除。

| 公司 / CSV行 | ID | scope | action / status | 分类 | 具体语义判断与来源 |
|---|---|---|---|---|---|
| 600900 长江电力 / 998 | ADD_PLAN_CANCELLED | add | eligibility / blocking | 持续研究裁决 | 当期研究层追加计划取消，须新公司研究及计划重新评估；不是随价格进入P1自动复活。 [codex审计:482](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:482)，[claude审计:700](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-claude.md:700) |
| 600900 长江电力 / 998 | D5 | add,entry | freeze / not_applicable | 仅观察 | 当前明确not_applicable，仅保留范围裁决记录，不是未解阻断。与迈瑞D5适用性不同不构成冲突。 [codex审计:530](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:530) |
| 600900 长江电力 / 998 | HOLD_REVIEW_Q3 | holding | review_holding / blocking | 混合需拆分 | Q3电量反证、T1价格位置、蓄水条件混入同一复评；解除路径含经营恢复或价格回落后再复核。应拆经营复评与价格观察，保留OR原文，不让价格单项清除经营事实。 [claude审计:713](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-claude.md:713) |
| 600900 长江电力 / 998 | HYDRO_Q3 | holding | review_holding / blocking | 持续研究裁决 | 已发生电量下降触发的正式公司持仓复评；后续利润/现金证据才能裁决，未确认失效。 [codex审计:494](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:494) |
| 600900 长江电力 / 998 | PB_REVIEW | holding | review_holding / blocking | 混合需拆分 | PB历史分位是动态输入，阈值触发持仓复评；完成复评是研究工作，不等于分位回落即解除全部风险。 [codex审计:518](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:518) |
| 600900 长江电力 / 998 | PRICE_ABOVE_P1_HIGH | entry | eligibility / blocking | 应由运行时动态评估 | 纯价格坐标比较部分应随同版本报价及行情重算；其附带Gate/其它约束引用不能被一起自动清除，24.83为Claude本轮高档而非CSV加权P1 21.24。 [claude审计:688](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-claude.md:688) |
| 600900 长江电力 / 998 | R4 | add,entry | eligibility / blocking | 持续研究裁决 | 公司无降息情景及盈利能否对冲估值压缩，是有证据的持续研究结论；价格变化不能替代重新论证。 [codex审计:456](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:456) |
| 600900 长江电力 / 998 | R4_PARTIAL_STANDING | add,entry | eligibility / blocking | 持续研究裁决 | 与R4高度重叠，但其解除要求含宏观路径与公司盈利组合，须保留来源各自的AND条件再研究归一。 [claude审计:674](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-claude.md:674) |
| 600900 长江电力 / 998 | R6_CN_MACRO | add,entry | freeze / blocking | 混合需拆分 | 事件48h在窗可动态判；公司实质暴露、预案及发布后需求/电价/现金影响要另保留研究裁决，不能日历一过自动放行。 [codex审计:417](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:417) |
| 600900 长江电力 / 998 | R6_COMPANY_DATE | add,entry | eligibility / unknown | 证据不足待澄清 | Codex称正式预约日未知，Claude监控已有10/31；应先核日期来源等级及发布时间，再分离日历事实与结果复评，当前unknown不是确认入窗或失败。 [codex审计:469](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:469) |
| 600900 长江电力 / 998 | R6_DEBT_MATURITY | add,entry | freeze / blocking | 混合需拆分 | 债券到期窗口可动态判，真实兑付/余额/融资与期后现金须证据复核；Codex未判已兑付而Claude监控称已兑付，存在事实声明冲突。 [codex审计:430](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:430) |
| 600900 长江电力 / 998 | R9 | add,entry | eligibility / unknown | 混合需拆分 | 同口径分位/利差可数据刷新，但样本、拥挤和底仓资格仍须研究；缺项保留unknown。Claude监控给全部基金近3年分位0%并承认主动权益/板块口径缺项，不足以推翻Codex缺合格分位结论。 [codex审计:443](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:443) |
| 600900 长江电力 / 998 | RESERVOIR_DEADLINE | holding | review_holding / unknown | 证据不足待澄清 | 缺当年正式批准期限及枯期影响，不能把尚未达175米直接判失败；当前为unknown的持仓复评，待精确条件证据，不升级为逻辑失效。 [codex审计:506](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SH-600900/investment-600900-2026-10-19-research-codex.md:506) |
| 300760 迈瑞医疗 / 999 | ADD_OIL | add | eligibility / unknown | 混合需拆分 | 同一主力结算价/情景可动态判断，实际成本弹性、套保、转嫁和OCF需公司证据研究；unknown不等于已经失效。 [codex审计:554](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:554) |
| 300760 迈瑞医疗 / 999 | ADD_REPAIR | add | eligibility / blocking | 持续研究裁决 | 原取消追加计划的公司盈利、现金、订单、Terminal与全部Gate条件，需正式研究重新安排，不能价格/时间单项解除。 [codex审计:542](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:542)，[claude审计:749](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-claude.md:749) |
| 300760 迈瑞医疗 / 999 | D5 | add,entry | freeze / blocking | 混合需拆分 | 市场深化/退出/重建的逐日数值可动态计算；公司适用性与逐股盈利/OCF/订单/估值复评必须独立保留。R21只退等待复核，原重建路径独立。 [codex审计:467](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:467)，[claude审计:683](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-claude.md:683) |
| 300760 迈瑞医疗 / 999 | H_MARGIN | holding | review_holding / blocking | 持续研究裁决 | 已报利润率下滑是实际经营反证，持续保留复评；Claude另列价格回落后复核OR分支，不能用价格回落清除该经营事实。 [codex审计:578](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:578)，[claude审计:776](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-claude.md:776) |
| 300760 迈瑞医疗 / 999 | H_PLEDGE | holding | review_holding / blocking | 持续研究裁决 | 已披露新增质押的持仓专项复评，须后续履约/平仓/控制权及现金影响证据；尚非invalidated/exit_required。 [codex审计:566](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:566)，[claude审计:763](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-claude.md:763) |
| 300760 迈瑞医疗 / 999 | R4 | add,entry | eligibility / blocking | 持续研究裁决 | 公司紧缩下经营独立性和盈利对冲能力的持续研究裁决，不能改成仅现价跌过压力值即自动解除。 [codex审计:516](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:516)，[claude审计:721](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-claude.md:721) |
| 300760 迈瑞医疗 / 999 | R6_CN | add,entry | freeze / blocking | 混合需拆分 | 宏观窗口动态部分与公司内需传导、R20社零/信贷结果及预案复评混合；事件过窗不解除内需约束和D5等其它Gate。 [codex审计:489](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:489)，[claude审计:735](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-claude.md:735) |
| 300760 迈瑞医疗 / 999 | R9 | add,entry | eligibility / unknown | 混合需拆分 | 多频次分位/利差输入适合按数据期刷新，资格及口径研究需保留；不得用个股换手替板块换手，也不以缺项推定不拥挤。 [codex审计:503](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:503)，[claude审计:706](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-claude.md:706) |
| 300760 迈瑞医疗 / 999 | TEMP | add,entry | eligibility / unknown | 应由运行时动态评估 | China-MM或兼容温度代理、对应cap/账户上限本属当前运行时约束；数据不足维持unknown，不能默认冷档，研究应给适用代理/规则不固化旧温度值。 [codex审计:529](/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/2026-10-19/SZ-300760/investment-300760-2026-10-19-research-codex.md:529) |

### 仅观察的实际项目

四份价格地图各有10条重点monitoring，共40条，其中15条在该来源标为general/watching。这些本身不应追加进controls未解集合；未来真正触发后，再按原规则判断参数调整、复评或具体限制。

| 来源 | 当前标为general/watching的ID | 处置 |
|---|---|---|
| 长江/Codex | DIVIDEND_SPREAD、PRICE_CONTRACT、CAPEX_POLICY | 年度分红/利差、电价长协、抽蓄资本回报与认缴等留监控；未触发不能以“存在风险”生成未知禁买 |
| 长江/Claude | M_TARIFF、M_DEBT、M_DIVIDEND、M_YIELD_SPREAD、M_CROWDING、M_Q3_REPORT | 留电价、债务、分红、利差、拥挤及财报观察；其中债务/窗口/拥挤与另一端active判断有交集，watching不能反向清除另一端已有限制，须按下述来源分歧核对 |
| 迈瑞/Codex | CAPITAL、CASH_ORDER、GLOBAL_GROWTH | H股申请/股本、现金渠道、内外需与终局份额留观察，不提前把申请当融资完成、把阈值条件当已触发 |
| 迈瑞/Claude | CAPITAL、CASH_ORDER、GLOBAL_GROWTH | 同类观察保留各端事实口径；同名监控不等于两端证据完全相同 |

长江D5的not_applicable是适用性审计记录，既不是已激活D5，也无需为没有触发的冻结创建解除任务。以上按**来源项目**计数，包含不同端相同概念，不表示15个独立公司风险。

### 尚需证据裁决的具体分歧

- 长江债券到期：Codex未核实际兑付、认为有现金/滚续暴露；Claude价格地图称已兑付，而报告对日期的表述较弱，且以固定条款/OCF覆盖判为不构成窗口。需要核真实可得时点、正式兑付与实质暴露，不仅刷新日期。见Codex报告119行、Claude报告285/859行及其价格地图116行。
- 长江宏观窗口：Codex认定本日10:00窗口与境内收入传导相关；Claude报告275行称未进入任何48h窗口。缺少同ID不等于已明确解除，要核事件覆盖与公司暴露。
- 长江财报日期：一端未知，一端引用10/31预约；先核正式来源、版本及何时可用，不拿二手日期自动clear。
- R9分位：全部基金/主动权益、公募分位/北向比例、个股换手/板块换手不能互相替代。一个来源给0%不证明必要口径已齐。
- 某端自定义的“两报告期转正”“Terminal份额<30%”“年报利润≥317亿元”等须标公司假设、触发线或充分证据路径，说明论证；canonical未统一要求这些作为所有合法解除的唯一前提。本轮不宣布其全部无效，也不把它们提升为跨公司常量。

以上是被审查文件的声明差异，**本轮未判定谁的投资事实正确，也未形成解除凭证。**

## 5. 最小精简方案

### 5.1 先修语义，再减载荷，分开验收

第一步只修职责和作用范围：纯P1/T1条件交既有价格核心；holding-only缺证不扩scope；规范重复ID、事件实例和来源裁决；未触发项留观察。R1/R3/R6/R21的原AND/OR、例外、证据要求和数值不变。单独记录行为差分，不能与格式等价改造混成“无策略变化”。

第二步压缩执行载荷，并做旧厚对象/新薄对象在同一输入上的资格、解除和卖出等价检查。相同限制压缩前后不应改变决策；来源冲突和未决研究不因格式变化变成允许。

第三步才处理既有2条v4的显式语义迁移清单。本轮只提出清单，不写生产；996条legacy、旧报告/JSON、封口、available_at和历史价格不改。

### 5.2 推荐仍在原CSV两列内保存紧凑执行载荷

保留`research_contract=stock-research/v4`；P1/T1价格协议无需仅因载荷瘦身升级。CSV的`research_controls`改为有明确存储版本的紧凑对象，推荐新执行载荷版本`research-controls/v2`，旧v1双读、新发布单写v2。最终具体字段以实施ADR和兼容测试定稿，不在现有v1含义下静默变更。

最低内容：

- entry/add/holding各自status与refs；必要的有效`id/scope/action/status`，使历史接续仍能判断对应范围。
- 尚需参与重放的显式clear/not_applicable解除记录及短证据引用；D5的`rebuild_review_complete`阶段保留。不能只保存最新eligible摘要并删除解除记录，否则重放会复活历史冻结。
- 绑定本次不可变完整审计的相对引用、内容SHA256、源报告/封口身份。真实available_at沿用原CSV列。完整理由、替代解除路径、源报告差异与历史来源不再每行全文复制。

同一约束语义一致时可一个scope数组覆盖entry/add；若两个scope状态、动作或解除裁决不同，不能强行合并。执行热路径读CSV直接判资格，不读可变旁文件、不依赖网络或LLM重新判断研究结论。

在当前2个对象上，仅去掉执行未用全文/累计来源、保留scope展开约束与解除字段的内存估算为 **6,092→2,075字符、4,484→1,591字符**，各缩约66%/65%。这还没加入正式证据引用及版本信息，也未做scope合并；只是量级估算，不是已经验收的生产格式。无需为追求某个字节上限牺牲可重放语义。

### 5.3 复用既有不可变审计，CSV仍是资格唯一业务来源

完整内容优先放在现有writeback审计产物/冻结报告中，不另建可独立修改的`controls-latest.json`状态文件。某约束的研究证据在报告audit内权威，发布后的执行资格由已提交CSV权威；审计附件不能绕过CSV更改资格，CSV也不能凭未验收字符串冒充解除证据。

发布顺序：校验冻结来源与完整审计 → 保留各源分歧并形成最终裁决 → 只创建、不可变地落盘审计并校验哈希 → 生成紧凑CSV预览 → 使用原锁/CAS原子提交价格、控制、证据引用和真实发布时间 → 保存回执/完成原有归档。CAS失败则重新准备，不能拼接旧价格与新资格；失败可留下未引用审计，不能留下引用未落盘证据的可见业务状态。[原提交属主](/Users/xinquanzhou/Workspace/ai_investment/src/infrastructure/prediction_transaction.py:21)。

发布前证据缺失/哈希不符拒绝新发布，保留上次已提交状态。已发布后的审计附件损坏应告警/进入修复待办，不从残缺附件推导clear、不重盖时间；执行资格继续按CSV记录，不让审计附件成为第二个资格开关。若未来选择每次运行必须读取侧文件才能判断资格，就必须承认它是组合业务来源并另做一致性设计，已超出本轮最小方案。

### 5.4 动态职责不等于已具备运行时实现

| 条件 | 最小处置 |
|---|---|
| C相对P1/T1、原最低收益要求 | 使用现有decision_core；只用正式发布价格，不把Claude高档24.83另作新闸门 |
| TEMP温度/cap | 应归当前运行时风险/仓位职责，但本轮未找到已经等价接入的China-MM/兼容代理完整门禁；已有固定仓位上限不等价。先明确数据、兼容口径、失效处理和回测注入，再迁出；期间不把unknown直接清掉 |
| PB/基金/换手分位、利差 | 输入按真实数据期更新；样本口径与必要证据缺口仍研究核验，不新增低时效强行日频的取数任务 |
| R6日历/48h | 可动态判具体事件窗口，预案/实质暴露及事后结果保留研究。日期过去只改变窗口事实，不解除研究裁决 |
| D5/R21市场条件 | 逐日同组AND、实际公开时间、完整两融口径保留；R21只回等待复核，原重建路径独立，公司复评不可绕过 |

不建设通用自然语言条件执行器，不让LLM每次行情波动重新决定是否解除，也不新增固定投资阈值或隐藏第二买价。

## 6. 跨仓同步清单

“必须调整”是实施本方案时的范围，本轮未修改这些文件。按独立逻辑分批审查，不要求一次大改全部模块。

| 层 | 必须调整或核对的文件 | 具体要求 |
|---|---|---|
| canonical/compact | `framework/investment_framework.md`、`framework/investment_framework_compact.md` | 价格资格分离、持续/动态/观察归属、holding未知范围、ID实例与解除逻辑；既有阈值、参数及D5/R21出口不变；完成治理与保真核对 |
| 调研技能 | `.agents/skills/stock-research/SKILL.md`、`references/valuation-and-output.md`、`references/research-consistency.md` | 报告完整条件表分三类；只把已触发研究限制/必要资格缺证投影到controls；普通watching不造constraint；buy_candidate不代表现价可以买；公司自定义解除线说明依据与非唯一性 |
| 生成/验收 | `scripts/stock_price_map.py`、`research_consistency.py`、`research_runner.py` | 统一mode/资格语义、明确scope未知、规范ID/来源映射及校验能证明的边界；runner“未知不允许新增”只针对对应新增范围和合同缺失；新prompt模板绑定方法指纹，冻结旧批次不改原prompt/hash |
| 接续完成验收 | `scripts/research_exchange.py`、`research_paths.py`、`investment_maintenance.py` | 检查合同、配对、审计与完成凭证；保留PR50已修防降级/完整v4审计；不因“最新文件”或字段存在证明方法兼容/研究完成。仅在输出结构真正变化时改解析，不机械改无关发现逻辑 |
| 本仓文档/兼容入口 | `research/README.md`、必要的`docs/context/project-state.md`、相关projects引用、`.claude/skills/stock-research`入口 | 同步现行合同、输出与旧批次边界；不维护第二套Claude规则正文。deep-research取证流程本身无需因存储瘦身修改，只核它不误下执行裁决 |
| 发布与控制属主 | AI `src/analysis/research_controls.py`、`research_consumer.py` | v1/v2读取、紧凑投影、稳定身份和来源裁决、证据绑定、clear重放、保留消费者缺价约束；不再累计复制全部sources |
| CSV写入 | AI `scripts/calc_weighted_prices.py`、`prediction_publication.py`、`prediction_transaction.py` | 继续按原列属主和原事务发布。writer接纳新载荷时做版本校验；时间戳、锁/CAS实现无必要不改；catalyst_and_risk另属主仍保留 |
| 最终研究门禁 | AI `src/decision/research_eligibility.py` | 统一holding-only未知范围、保持真实发布时间重放、旧v4不被legacy降级；缺合同/确认失效/退出/entry或add缺证仍限制对应新增 |
| 动态价格/仓位 | AI `decision_core.py`、`src/backtest/execution/position_sizer.py`及现有运行时数据属主 | P1/T1/最低收益原逻辑只回归；TEMP如要迁移需额外证明等价门禁，不能以固定cap代替温度约束；不扩展外部数据访问边界 |
| monitor | AI `scripts/investment_monitor.py` | 最终及保存前均用同一控制语义；无持仓上下文保守处理并展示首笔/追加差异，不把HOLD误称已安排复评 |
| 候选复评 | AI `candidate_review/review_gate.py`、`pairing.py`、`snapshot.py`、`ai.py`、`orchestrator.py`/`selection.py`及`reeval_targets.py` | 统一业务比较、薄载荷与证据定位；真条件变化仍复评，纯seal变化不击穿；把适用HOLD复评需求接到既有待办/定向入口；不放开自动买入或无预算全量重研 |
| 持仓/卖出 | AI `scripts/sell_agent.py`、`sell_agent/cache.py`、`execution_planner.py`、`output_builder.py`、`lark_report.py` | 缓存语义比较；新载荷兼容；完整入口已正确恢复晚到控制，应保留回归。复评/unknown不等于清仓，退出要求不冒充已卖出，不抑制现有止损 |
| 回测/最终执行 | AI `src/backtest/orchestrator.py`、`strategy.py`、`execution/trading_executor.py`及相关adapter | 和实盘共用控制解析、scope与价格判断；按当时实际可用数据及真实持仓门禁，不读今天审计去补历史资格；报价既有T+1语义不变 |
| 文档/备份/测试 | AI相关ADR、`docs/contracts/system_boundaries.md`、`monitor_strategy_mapping.md`、CHANGELOG及下述测试 | 新公共载荷/权威关系先有ADR；备份必须覆盖新增不可变审计引用；模型报价库、权重和飞书报价备份不变成资格来源 |

## 7. 迁移及验收边界

### 7.1 迁移规则

1. 当前记录先做逐ID映射表：保留持续裁决；混合项拆成动态事实和研究待复评；只针对有批准纠错依据的纯价格子项生成版本化更正。来源分歧未裁决、TEMP接替者未齐不放行。
2. 旧v1、旧v4、旧v3/v2、冻结prepared批次均保留原文件字节、原日期和真实发布时间；新读器兼容，新writer单向写新执行载荷。不通过批量重写历史制造新规则的过去表现。
3. 更正或解除只作用相应公司、实例与scope，不把R4别名归一变成R6/R9等其它限制的解除。D5固定阶段保护和明确退出/失效保护继续有效。
4. 新发布和老程序不兼容时应拒绝新增写入或使用已批准兼容读器；不能让旧writer回写厚载荷或legacy报价覆盖新控制。代码回滚不回滚已确认风险；保留可重放证据。
5. 本轮无生产迁移、无提交/推送、无调度或账户变更。此前只限两条PR修复的推送授权不扩展到本方案。

### 7.2 实施前后必要测试

| 场景 | 应验证的可观察行为 |
|---|---|
| 价格高于P1→进入P1 | 只改变价格信号；其它研究限制仍有效；T1独立；不使用模型高档替代发布P1 |
| 纯holding复评缺证 | 不扩展未声明entry/add范围；合同缺失、确认失效/退出仍阻新增；卖出独立 |
| 首笔允许/追加暂停 | 无仓允许继续评估首笔、有仓阻追加；未知持仓保守；展示与最终执行一致 |
| R6 | 实质暴露 AND（入48h OR 相关窗口缺预案）时按原规则限制；分别验证窗外但相关窗口缺预案、窗外且预案充分并未触发的情形；普通未来watching不自动冻；过窗无结果复核不自动解冻；不同事件不能误去重 |
| D5/R21 | 同一组三日、逐日三项合取；缺日/口径错不通过；R21不恢复；原重建独立路径+公司复评保留 |
| 来源和ID | 输入顺序不改变最终业务裁决；别名经映射无重复解除债；两端有实质分歧不能靠取第一份消失 |
| 厚→薄 | 相同状态/action/scope及clear重放决策等价；D5阶段保留；不删除clear后复活冻结；价格失败→有效→再次失败准确收紧 |
| 复评与缓存 | 纯seal/时间变更不触发无效LLM、不拆A/H；真实风险新事实、scope/action/参数/解除变化仍触发；HOLD复评待办实际可达 |
| 事务与历史 | 审计缺失、CAS冲突、写后归档失败、重试幂等、晚到control-only、旧available_at、legacy兼容与防降级全部覆盖 |
| 回测 | 仅用当时available_at/市场数据；报价T+1、实际持仓、独立止损和退出保留；格式等价与语义更正分开比较 |

本轮无实现变更，因此未跑全部跨仓回归或新的组合回测。未来实际实施应按仓库约定完成定向测试、真实受影响入口的隔离夹具、通用正确性审查、六维检查；框架/skill改动另跑治理、quick_validate及单阶段边界验证。无需恢复用户已免除的前瞻影子期，但不得把小样本离线检查称为投资有效性证明。

## 8. 本轮实际验证与限制

- 只读盘点全部2条v4、22个公司+ID，并对照30个源约束；核四份报告和价格地图哈希。
- `semantic_probes.py`退出0：复现价格锁存、holding-only未知扩scope、持仓上下文差异、同ID来源顺序、sources累计、mode资格耦合；确认clear重放/实际发布时间边界；在两实际对象上对买入/持有/卖出及持仓状态组合做载荷投影比较。通过表示行为被复现，不代表上述设计正确。
- `downstream_probes.py`退出0：复现元数据引起额外复评/AH拆分/缓存失效、HOLD恢复筛选断点；**完整sell CLI恢复辅助路径正确保留晚到exit_required**。早期只看latest DataFrame的怀疑已核销，不列缺陷。
- 现有离线定向测试：`test_two_price_controls.py`、`test_research_eligibility.py`，**39 passed in 0.34s**。其中一项现有测试明确要求holding未知禁新增，恰说明需先裁决语义再改测试；不能把39通过当作语义审查无问题。
- 未调用真实API、LLM生产调研、飞书、交易或生产发布命令；未验证当前公司证据、阈值有效性或策略收益优势。
- 本轮不生成adopted handoff，不覆盖现行框架/报告，不从本报告生成自动解除许可。
- 独立设计复核发现验收表曾漏写R6“相关窗口缺预案”这一OR分支，已在本报告补齐；未据此修改生产规则。其余指定的TEMP接替、混合项、D5/R21、解除重放、证据权威及实质新事实触发边界未发现剩余设计矛盾。

六维设计检查：责任边界需按方案收敛；Hard Stops无违反；无代码删除/死代码判断；范围限本问题；新schema/权威关系待实施ADR；验证为只读夹具和定向回归。审查结论为**现设计有需修正项，方案可进入实施审议**，不是“生产已验收”。

## 9. 全框架条款生命周期核对

| 条款及定位 |逻辑与动作 | 分类与解除边界 |
|---|---|---|
| P1/T1，C426–433、473–479；K294–296、314 | P1是估值参考，T1为价格型减仓/卖出评估起点；触价不等于执行；新建/追加/存量分别裁决 | 相对现价属于运行时动态。纯“当前高于P1”不应成为持续研究禁买；到T1不自动清仓。真实研究冻结另列并继续生效 |
| R1，C187、308；K160 | `(公募>=88% OR 板块换手>=95%) AND PE/PB>=80% AND 无近端可见业绩`，且处追高价位时追高否决/限制新开；不冻结合理持仓 | 混合条件：最新估值/拥挤+研究证据复核。不得以“高于P1”代替三项合取；回撤后重新逐项判，不永久沿用旧命中。不是单一价格自动放行 |
| R2，C183、186；K161 | CPI>4% AND 降息归零/转加息 AND 估值依赖降息扩张，适用于高估值成长；与R3是独立条件 | 持续研究体制与逐股资格；不能把任一宏观观测或D1激活本身改成全票冻结，按本规则复评 |
| R3，C186、236、330；K164–166 | 隐含降息bp>0 AND 降息归零/加息 AND 盈利无法对冲压缩；合约级订单现验 OR 政策映射且报表可验可使第③项不成立 | 持续研究资格，但解除是重新核验合取，不必三项分别“恢复理想值”；不冻结仍保留折扣/cap从严。R18引用不应重复造同一阻断 |
| R4，C191、420；K167 | 不成立→冻结；部分成立→不给激进仓位和完整买入型Price Map | 持续研究资格。需证据复评独立成立性；原文未规定必须连续两个财报期转正、必须等指定FOMC日期；新增这类门槛须标公司研究假设，不能冒充框架必要解除条件 |
| R5，C192、311；K168 | 双轴双损→冻结；内需受损要显式回答暴露与对冲 | 持续研究判断；用同一公司、同一双轴证据复评，非价格回升自动解除 |
| R6，C193、313、333、470；K169 | 实质暴露 AND `(相关窗口前48h OR 相关窗口缺预案)`→冻结新开/暂停追加；无暴露有依据可不适用，未知只保留受影响限制 | 混合：日历/入窗可动态核验；过窗须实际结果、公司暴露及其它Gate即时复评，不自动清除、不等周更。必须区分具体事件实例；未来窗口watching不提前冻结 |
| R7，C312、409、486、505；K170、318 | capex指引转弱 AND 在手订单同步转弱→冻结并重算/复评；大幅下修且高度依赖、确认脱钩证伪才进入退出 | 持续研究限制；单独capex边际转弱只观察/复评，不提前套用AND已成立或退出 |
| R8，K171；C278 | 逐季兑现 AND 订单可见度 AND 2027估值合理→可保留买入候选，仍须R1/R3；否则跟踪 | 持续研究资格；核当期合同/正式报表，不把一个外部行业锚当三项全过 |
| R9，K172；C273 | 利差/公募分位/换手三项现值必查，缺一无完整买入资格；公募>=88% OR 换手>=95% OR 利差显著收窄→按拥挤处理 | 缺口资格可持续至补证；数值随最新口径复核；拥挤回吐不等于逻辑破坏，不因此清仓。不是缺项直接等价于已确认拥挤或永久拒绝 |
| R10，C334、416；K173 | 已验证近端业绩龙头单日/单周回调不自动减仓，先核capex和订单 | 防误动作原则/观察，不创建禁买条件或解除债务 |
| R11，C317、414；K174 | 国家队变化只是跟踪信号，官方确认才作事实；确认连续减持可调整r_chip/cap | 观察/证据规则；仅提及减持或媒体报道不能变持久冻结，联动条件另判 |
| R12，C181；K175 | 低位本身不是买入理由；须盈利兑现链，有业绩真实承接；卖出同样依证据 | 研究资格原则；不能生成“价格低所以解除”或“跌价所以退出” |
| R13，C184；K176 | D2激活且长久期高估值资产，30年美债趋势逆转前不左侧；外生分母冲击不等于盈利证伪 | 条件性研究/执行限制，适用对象必须核实；趋势变化触发复评；硬证据存量不机械退出 |
| R14，C323、239、452；K177–179 | 油价敏感成本端V5不过→r_v5上调、取消追加；剪刀差扩大 AND 无转嫁证据→利润率从严；受益端回落情景不过→追加从严；油价+30%下OCF负 AND 无对冲→硬失败 | 参数调整与研究限制分开。不是油价触值统一禁买。动态油价触发复评，追加取消持续至论证重新批准；同一主力结算与现货不可混 |
| R15，K180；C276 | 供给冲击归型，供给证据/利润传导、回落对称情景必答；贵金属/能源分判 | 研究方法/证据要求；只有具体资格或硬失败成立才生成控制，不把归型本身当冻结 |
| R16，C185；K181 | 基准情景站得住为必要条件，尾部情景只是对称提醒；不是“两情景都必须站得住” | 研究分析要求；失败后按对应规则判scope，不自造统一禁买/清仓 |
| R17，K182、D3；C276/451 | 贵金属强美元基准→r_v5上调、追加从严；撤销/再上调/降级按D3 | 参数/研究判断；“从严”不等于自动add blocked，更不等于entry blocked。需逐股事实裁决 |
| R18，C185–186；K183–187 | D1全面执行→d_base上沿、cap下调；冻结仍仅R3三项合取及例外；反弹不撤销体制 | 参数状态及R3别名引用，不应以R18另造与R3相同的第二未解冻结 |
| R19，C413；K188 | 规划(a)不够，4–8周内须第二环(b)证据且盈利锚；无第二环只观察，到期无证据撤候选 | 持续研究资格+时间驱动复评；到期不是自动恢复，也不是只要到期就确认政策失败；第二环出现仍需盈利核验 |
| R20，C324、412；K189–191 | 依赖内需 AND 暴露高且无对冲→从严收入重算V50、cap下调；政策受益不豁免；不依赖内需不适用 | 参数/研究约束，原文不是全局freeze。D8两项合取触发复核；不把“内需弱”直接变成所有股票禁买 |
| R21/D5，C274；K135–137、192 | 深化触发为成交<1.6万亿 OR 指数<1516.2 OR 两融净偿还超150亿；退出须同3个交易日每天成交>1.6万亿 AND 完整两融>-150亿 AND 官方收盘>=1516.2 | 持续状态机。退出仅回等待复核，不能恢复买入；原重建>2万亿连续3日 AND 两融3日净流入 AND 收复1577.36，再逐股复评。原重建路径独立可用，不强制先走R21 |
| Precheck/联动，C244–247、328–332；K221、256–258 | 硬失败1项→冻结/红线否决；中度>=2项→参数/cap，必要时取消追加；成本/capex/现金任2项不等于必冻结；机构集中/验证不足/高估任2项调参数、3项限制完整候选 | 保留“必要时/原则上”的逐股裁决；不能把所有风险提示映射blocking。内部合取与合法择一不能扁平化为每一子项均需单独clear |
| 持仓复评/失效/退出，C477–493、497–508；K316–320 | 边际弱化→复评；确认核心盈利/现金流被证伪或终局不可能→失效/退出且禁止新增；非价格触发不等待T1；研究退出不等于成交 | 持续holding事实需保留；纯review_holding不扩大entry/add，未知不得冒充失效；确认风险不能被AI持有/失败抹掉 |

D层不应作为额外的八个全局禁买位：D1为体制及参数档位，D2为情景与适用限制，D3为分支情景/复评触发，D4为覆盖权重，D5为机制状态机，D6为具体事件清单，D7为防过度反应原则，D8为内需参数约束。D1出口为不加息 AND 官方路径回撤证据；D3黄金跌破4200 AND 美元站稳100才再上调，另一分支连续两周黄金>4300 AND 美元>100触发降级复核；D8同一最新可核月社零>2% AND 新增贷款同比不少增触发复核。上述数值只是转述当前文件，不刷新其市场状态。

## 10. 复核材料

- [输入及源码指纹](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/input-manifest.json)
- [全部逐条原reason/解除条件、两端来源与分歧](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/inventory-notes.md)
- [机读盘点及4份报告/4份价格地图哈希](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/inventory.json)
- [根代理行为夹具](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/semantic_probes.py)、[结果](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/semantic-probe-results.json)
- [下游夹具](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/downstream_probes.py)、[结果](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/downstream-probes.json)
- [定向回归日志](/Users/xinquanzhou/Workspace/investment_research_methods/output/research-controls-semantic-audit-20261019/existing-targeted-tests.log)

| 公司/生成端 | 报告 SHA256 | 价格地图 SHA256 |
|---|---|---|
| 600900/codex | `13a47a7ebda4795fdf1ddc9da13e141fd436987a944d0184d2254f8744f9bc7e` | `e832e7d9c6db72488a95b4b2a32dc3303373d31de9cc062464485e2f5d486496` |
| 600900/claude | `0743bb5e6f0396adcbdd007926e747a47ba3ee6bd1dfa5d0bd8e97c1af809fba` | `727699295b4c8d264a72f58015dea68de87be0dc6bdf9f54d770796499bca815` |
| 300760/codex | `c1217fcefddd9a974f5ea64c2158542a87922174967f180dc5bca44cecff9799` | `ef204d2dc42b67f12d0370763e97eb90cb43873e561fd143cacaca9a73d2a364` |
| 300760/claude | `c3b54b912b90a87ee7a0313473e3b2bd1b4a40ca2f86efc21dea2578ed7cc8c2` | `10d546bdb95d44641ccf0a34ba4b87169e164945b2f5ab4c6b878daed26ec010` |

```yaml
MAINTENANCE_CLASSIFICATION:
  state_refresh: false
  evidence_correction: true
  method_change: true
FRAMEWORK_UPDATE_DECISION:
  update_needed: yes
  update_level: light_semantics_and_cross_repo_contract
  decision_reason: 明确持续研究、动态执行与观察归属，修正scope和来源裁决；既有投资数值不变
METHOD_ADOPTION: not_adopted_this_run
PRODUCTION_DATA_CHANGED: false
PENDING_COMPANY_REVIEWS:
  - 600900事件暴露/兑付/披露日期与分位口径来源差异
  - 600900跨端R4和Q3复评别名及公司自定义解除条件
  - 300760温度门禁属主与完整替代条件、同ID跨端解除要求
COMPLETION_EVIDENCE:
  - 当前2条v4全量盘点与只读行为复现
WITHDRAWN_SOURCES: []
```
