# 研究计算与状态一致性

本页接续2026-10-18两价发布契约；新准备使用价格v4 + audit-v4（two-price-controls/v7）；用户已授权评审后合并本地dev，实际采纳以匹配正文指纹的adopted handoff为准。冻结合同优先：旧controls-v6使用audit-v3，旧两价v1及controls-v2…v5继续audit-v2，使用各自旧字段/公式；更早价格v3/audit-v1使用 [legacy-audit-v1](legacy-audit-v1.md)，不追溯改写。只编码 canonical 已定义的计算与按scope控制，不另加折扣常数或投资阈值。

## 一份可核算底稿

先裁决估值假设，再建立临时 `research-audit.json`，完成报告并提取明确报价后生成核算展示：

```sh
python3 scripts/research_consistency.py render --audit output/<本轮>/research-audit.json --price-map output/<本轮>/price-map.json > output/<本轮>/research-checks.md
python3 scripts/research_consistency.py check --report <本轮报告.md> --price-map <本轮价格.json> --require-lifecycle --require-acceptance --expected-schema stock-research-audit/v4
```

把生成内容完整放入报告§5或§7，保留唯一的可见核算表与可展开JSON审计块。经营假设的数字表以此为准，正文解释依据，不另写一套未经桥接的收入/利润表。九节、原始证据、现金桥、Terminal、敏感性和监控仍按原契约完成。

程序只检查并拒绝矛盾，不重写P1/T1。计算模型先正确，再从报告提取报价；不得通过换成`other`、删除基线、清空报价或改折扣绕过错误。audit-v4受支持的持续经营FCFF使用`dcf_fcff`；其它方法如实选`other`并保留专项计算与未自动覆盖限制；真正不可估选`unavailable`。语义、来源及方法是否适用仍须人工核验。

## 审计输入

顶层字段为 `schema_version, identity, valuation, baseline, discounts, risks, constraints, release_all_of, p1_basis`；仅audit-v4另必填`valuation_review`，旧版本不追补。

- `schema_version`：新合同为 `stock-research-audit/v4`；冻结v6用audit-v3、v1–v5用audit-v2，字段/公式/可见表保留原样。旧价格v3仍配audit-v1。
- `identity`：`code, generator, valuation_date, currency`，与本轮价格JSON一致。
- PE模型 `valuation`：`kind="profit_pe", currency, amount_unit="100_million", shares, fx_to_quote, horizon, profit_basis, scenarios`。shares为实际股数；同币种fx=1，跨币种方向与依据留正文。
- `scenarios`必须有low/base/high，每项为`revenue, net_margin, adjustments, profit, pe, equity_adjustments, equity_value`。利润率用小数，例如11%写0.11。每项强制核验`收入×利润率＋调整=经常归母利润`、`利润×PE＋Σequity_adjustments=股权价值`（旧audit-v2仍核利润×PE），再核股本/币种换算后的V50。
- `adjustments`默认空数组。有合并范围、少数股东或非经营调整时，每项写`id, amount, reason, source`，金额与收入同单位，给来源与桥接理由。不得加一个无来源调整专门凑到旧目标利润。
- `equity_adjustments` 为新audit-v3必填数组，无调整填[]；每项同样为`id, amount, reason, source`，单位为模型币种亿元，现金正值、独立请求权/投入为负值，同情景不与利润调整共用ID。PE保留真实选定倍数，不把现金除利润折进PE、不虚增利润。来源和经济归属须人工核验，算术闭合不证明现金自由可用或项目支出充分。
- 非PE模型的`valuation`为`{"kind":"other","reason":"适用方法与计算位置","unrounded_v50":{"low":20.005,"base":24.005,"high":30.005}}`，明确提供未舍入的报价币种/股值；不可估为`{"kind":"unavailable","reason":"具体阻断输入"}`。非PE的专项计算仍由原估值契约和人工验收负责，不从已舍入JSON倒算未舍入值。
- `p1_basis`只列已明确报价的字段所对应的V50情景，例如单价`{"base":"base"}`，实际区间可为`{"low":"low","base":"base","high":"high"}`；base=null不填对应键。核验公式与明确报价一致，不代为生成缺价。

折扣 `discounts`固定五项 `d_base/r_chip/r_v5/r_gov/r_terminal`，每项包含：

### audit-v4 的 DCF 与估值复核字段

`valuation.kind=dcf_fcff` 的顶层精确字段为 `kind,currency,amount_unit,shares,fx_to_quote,scenarios`。金额单位固定`100_million`；每个low/base/high情景有`segments,equity_adjustments,equity_value`。每个分部精确字段`id,source,assumptions,discount_rate,years,terminal`，id同情景唯一，source定位事实、assumptions解释预测；discount_rate为WACC小数。years非空且year从1连续，同情景分部预测期一致；年行字段`year,revenue,ebit_margin,tax_rate,da,capex,delta_nwc`。收入/DA/capex非负，ΔNWC有符号，利润率小数；亏损年的税率设0，亏损可利用影响以后实际纳税年，不能自动给退款。

terminal字段`growth,roic,margin,tax_rate`，按末年收入×(1+growth)×margin×(1-tax)得终值首年NOPAT；正NOPAT、0≤growth<roic、WACC>growth，再按再投资闭合FCFF和终值。其它终值机制选适用专项模型而非硬塞本计算器。equity_adjustments复用`id,amount,reason,source`，经营EV加合计得声明equity_value，程序从原始输入复算（不从已舍入V50倒推）；分部可负、总权益须正且low≤base≤high。

本次FCFF计算边界补充：残差业务可显式设终值利润率=0且g=0，表示终值价值为0，仍完整计入显式期成本及投入；不能为通过审计编造正利润。非零增长的亏损/零利润终局仍不适用该永续式；反向求解仍要求正终局利润率的可识别条件解。

`valuation_review`精确字段`base_case,method_choice,pe_crosscheck,market_check,reverse_dcf`。前三项为非空解释，分别说明中性联合假设、方法适用与主辅裁决、同口径倍数依据或不适用原因；文字存在不证明论证正确。market_check含`price,as_of,source,explanation`，price为报价币种/股的正数、as_of为不晚于估值日的实际行情日，缺价时两者null并解释来源缺口；explanation说明主要业务分歧与市价在情景外的复核。

reverse_dcf含`status,reason,cases`。status为solved/no_solution/unavailable/not_applicable，后两者cases=[]并说明缺口/替代；FCFF不能填not_applicable。solved的每个case精确字段`scenario,segment_id,variable,target_price,lower,upper,parameter,modeled_price,residual`，variable仅terminal_margin，区间满足0≤lower<upper≤1，target_price须等market_check.price。在同一正向模型固定其余参数反求，parameter为终值利润率，modeled_price/residual重新回代，不是任意复制目标价。no_solution的case只有前六个输入字段，程序验证有效输入确实区间无解，不吞输入错误。各case通过scripts/research_valuation.py计算；如需跨WACC敏感性，另保存实际改变参数的完整模型并分别核算，不把其解填到未变主模型case。无解或一个条件解不能证明整体业务天花板/市场错误。

DCF审计不增加价格档，不改五项折扣，不将现金流、资本桥或模型中的同一损失再折扣。正式研究仍需全部适用验收、来源核验与旧基线接续。旧v6/audit-v3保持原字段和可见表字节。

### 折扣字段示例

```json
{
  "value": 0.15,
  "range": [0.10, 0.15],
  "risk_ids": ["MODEL_RESIDUAL"],
  "reason": "本公司、本期论证，示例数字不是默认档位",
  "change": {"kind": "initial", "reason": "无适用基线的首次研究", "evidence": []}
}
```

有基线时，数值和已有论证区间未变用`unchanged`；有变动必须用`new_evidence/correction/model_change/method_change`，写原因和非空`evidence`引用，并在正文给参数隔离敏感性。生产方法变动须引用已采纳方法；两价方法已按2026-10-18用户授权本地采纳。其他未采纳候选只可按明确授权隔离研究，不冒充生产生效。不能只重新定义更高的“上沿”而不说明变化。相同事实及模型先沿用同端适用基线，跨端只作有归属参考，不强行统一不同模型。

新准备批次将最近本端正式报告冻结到方法快照的 `research-baselines/`，提示词给`研究折扣基线`。非null时必须绑定该副本，不能自行改为无历史。`baseline`为：

```json
{
  "report_path": "output/runs/investment/<日>/<批>/framework-snapshot/research-baselines/<证券>-<端>.md",
  "sha256": "实际副本SHA256",
  "discounts": {
    "d_base": {"value": 0.15, "quote": "原报告逐字原句", "range": [0.10, 0.15]}
  }
}
```

上例需补齐五项。已有审计块时程序核对原参数与区间；旧报告无块时由模型逐项抽取原句、值和区间并核验语义，程序仅确认原文和哈希，不谎称已理解原句。旧否决/不可估报告从未给某项参数时，该项value与range可为null，quote引用原报告的不可估/未提供说明，本期该项用initial并解释首次论证；不能补造历史参数，也不能丢弃整个冻结基线。基线的经营模型失效时仍记录它并说明模型变化，不继承其无效利润/报价。确无本端正式基线才使baseline整体为null；不得因旧地图冻结而回退到更早的有价基线。

## 风险唯一归属

新方法先执行 canonical §4.1B 全局经济去重、§4.1C 资本桥及 §1.3 三值条件。按“事实/期间→机制→已吸收→残余→唯一位置→敏感性”复核；同损失多条命中只裁决一次，unknown不补成立数。基金NAV/第三方负债、现金/利息、预测项目/必要投入须成对闭合，不把未知变成100%损失，也不默认全部现金自由。语义复核未能约束参数时交条件情景或阻断相应估值，不能凭算术passed宣告经济问题解决。

### 分红基础估值与既有审计的接入

仅当本轮实际方法含 canonical §4.1A 时适用。DDM/FCFE 等按 `valuation.kind=other` 保留完整专项计算、真实未舍入 V50 和去重说明，现有五项折扣及 P1 公式接续。估值锚中的分配/折现率/终值影响可归既有 `owner=multiple`，scope 明确实际模型位置与已吸收部分，不能伪称使用 PE；直接经营影响按 revenue/margin 归属，独立残余才入既有折扣。此归属仅复用审计接口，分红经济定义以 canonical 为准。

报告须核现金/留存/再投资及股本桥、每笔分配权利、主辅模型重叠，R22 共用预测并按不同期限桥接。保留模型选择和相对同端基线的实际变化原因，不用换模型绕过审计错误。轻量 JSON 无新增分红价格档或字段；专项估值算术、来源和不同ID之间的经济去重仍需人工验收。

### R22 与既有审计的接入

仅当本轮实际方法（自动任务为冻结快照）含 R22 时适用；旧快照不追补。定价定义回 canonical §6.6，不把技能中的例子当参数。

- 报告 §4/5/7 留 ETF/指数身份和实测流动性、预先确定的基准/窗口及归因、前瞻比较或未量化原因。审计仍用原五项折扣和 v4及冻结版本对应audit，不新增 `r_etf/r_alpha` 或 U 报价字段。
- 机会成本收紧时，`discounts.d_base.value` 填 R22 桥接后的最终值，`range/reason/change` 对应最终论证；正文单列基础值、上期可辨认的 R22 残余、本期 B/U/最终 P1、证据及敏感性。相对冻结基线有变动须按真实原因分类并给引用。新增的机会成本残余用独立且稳定的 risk ID、`owner=d_base`，scope 说明它是尚未满足的回报要求，不冒充经营损失；已被原折扣满足则不再收费。原其它风险继续其唯一归属。
- `p1_basis` 与最终明确报价相符。现合同每份报告只有一套折扣，不能将不同情景的 `min(B,U)` 强塞进共享折扣的区间；无法用同一最终折扣准确表达时，只交付本轮明确的基准 P1，其余情景留敏感性分析。不得为了通过审计反推 V50、修改风险折扣或补造区间。T1 按独立价值论证提取。
- 缺少前瞻输入时明确未量化，不能记为零风险/已验证 alpha；纯价格回报门槛不制造 persistent 约束。确有依赖未证优势的研究资格限制才按实际 scope 接续。人工复核仍须检查不同 ID 是否同一经济影响，程序通过不证明去重或预测有效。

`risks`每项为`id, description, owner, scope, source`。owner只能有一个：`revenue/margin/multiple/eligibility`、新audit-v3的`equity_adjustment`或五个折扣项之一。

- 已在收入、经常利润率或PE吸收的风险，不能对同一经济损失再收费（跨ID也禁止）；R9缺项等资格限制不自动成为高拥挤或数值损失。
- 同一大类风险确有不同影响时拆分ID，并在scope说明已吸收部分、残余部分及对应证据。例如普通质保成本已进利润；仅超预提支付与回购的额外联合尾部留给r_v5。不能换名复制同一损失。
- 每个非零折扣必须引用自己独占的风险ID；零折扣列空risk_ids并解释归零原因。先核倍数已资本化的盈利持续性与终局风险；未资本化的远景不扣终局，低倍数已吸收部分不重扣，独立残余可保留，不因没有单列AI溢价就一概归零。
- 不把当期OCF再加到已经包含它的期末现金；未来普通质保/营运资本支付若已进预测OCF，不再次全额扣现金桥。理财、受限/经营必需现金、认缴/实缴、索赔/判赔分开。

程序能拦截相同ID的跨桶扣减，不能判断两个不同ID是否实为同一经济风险；主代理仍须审查scope、原文和现金桥。

## 按作用范围的控制与恢复

`constraints`每项为`id, scope, status, action, reason, release_conditions, lifecycle`，可带`clearance`；`scope`是非空且不重复的`entry/add/holding`集合，`status=blocking/unknown/clear/not_applicable`。旧 v4 批次/报告允许缺 lifecycle，按既有持续限制兼容；新批次显式填写并强制检查。仍有效/未知的适用约束必须保留，禁止遗漏上轮阻断来制造解除。

- lifecycle=persistent：已触发持续限制或对应研究资格必要缺证，才可 blocking/unknown；runtime：纯现价/P1/T1、最低收益交现有价格/收益规则；observation：未触发经营观察或复评路标。后两类保留完整条件/monitoring，不制造当前未解研究债务。buy_candidate 表示研究资格，未到 P1 仍可由运行时给 HOLD。holding-only 未知按持仓复评 scope 补证，不自行扩大 entry/add；整个合同缺失和确认失效/退出仍限制新增。
- 混合条款先区分当前触发、待证资格、观察和运行时价格；保留原且/或/例外及合法替代路径。TEMP 无等价运行时接替仍保留；R6 不按过窗自动解冻；D5/R21 不跳过原重建和逐股复评。旧纯价格阻断只能核原证据后显式纠正，不能仅凭 ID/格式变化删除。
- ID 绑定规则和事件/计划实例。同 ID 不同来源主张均保留；不同 ID 的同义关系须原证据明确映射，不能自动去重。解除同 ID 多项独立主张时，clearance.covers 列齐被解除主张的内容 SHA256（非来源 hash），同时给必要证据；不完整则继续阻断。用 `python3 scripts/research_consistency.py claims --audit <原research-audit.json>` 获取内容标识；它不证明证据真实。clearance.stage、所有必要合取与合法替代路径仍须保留。
- 基线约束已显式填写 lifecycle 时，即使只有一项主张，解除也必须填写 clearance.covers 并覆盖原主张；本轮删除 lifecycle、改为 runtime/observation 或用 not_applicable 解除都不能绕过。只有原基线未带 lifecycle 的旧格式单主张明确解除，才保留省略 covers 的兼容；一旦显式填写，空集合或其它主张的标识仍拒绝。D5 阶段取当前验收研究，不能因旧阶段字符串排序而保留过时状态；当前来源阶段冲突则记 unknown 并保留限制，阶段变化本身不解除主张。

完整理由和来源继续保存在报告审计及发布属主的不可变证据文件中；研究端 JSON 仍为 v4 摘要。下游 CSV 的 research-controls/v2 只保存执行状态/引用/主张标识/解除阶段和证据绑定，由发布属主先保存完整证据、校验后原子提交；研究者不自行改 CSV 或生成第二份执行权威。旧价格表不批量补造控制。

- `action=freeze/eligibility/reject/unavailable/review_holding/invalidated/exit_required`。全局freeze/reject/unavailable包含entry+add；仅加仓限制用`scope=["add"],action="eligibility"`，不能通过全局mode或解除清单再次冻结entry。holding动作包含holding；已确认invalidated/exit_required同时覆盖entry+add+holding。
- 有效freeze输出frozen，不用tracking/observation隐藏；确认否决用rejected，核心不可估用unavailable且无新P1。资格限制可继续观察估值；价格非空不推定eligible。entry/add任一eligible必须buy_candidate；tracking/observation/frozen/rejected/unavailable均不得eligible。only-add阻断仍允许已经满足条件的entry为eligible。
- `release_all_of={"entry":[],"add":[],"holding":[]}`：各集合精确列齐其scope全部blocking/unknown ID。规则内部合法择一路径保留，不能用一个约束解除覆盖其它约束。每条`release_conditions`写必要解除证据；clear必须有非空`clearance.evidence`；首次not_applicable可无clearance，但解除历史阻断或对应monitoring cleared时即使用not_applicable也须有解除证据。不以日期过去、来源缺席或unknown清除。
- D5先说明本轮是低位轮动新承接还是独立财报复评，不自动互换用途。D5 `clearance.stage`继续为`deepening/unknown/waiting_review/rebuild_pending_company_review/rebuild_review_complete`。R21只退出深化时填waiting_review，不能clear；原重建和逐股复评均完成、证据非空才可rebuild_review_complete/clear。原重建路径独立可用，不把R21出口写成全面解冻。首次D5不适用可无clearance；若基线仍有D5阻断或未知，本轮即使用not_applicable解除，也须rebuild_review_complete及非空证据，不能用不适用绕过重建与逐股复评。
- `research_controls`每个scope的`refs`精确等于该scope全部blocking/unknown ID的集合，不遗漏、不混入其它scope或普通经营观察。eligible/normal的refs=[]；holding=normal时无已触发持仓要求，review_required/invalidated/exit_required/unknown均须可解析refs。已确认失效/退出不能与entry/add eligible并存，持仓未知不自动清仓。
- 控制相关monitoring与同ID审计一致：triggered对应blocking，unknown对应unknown，cleared对应有解除证据的clear或not_applicable，watching不进入未解集合。普通general经营观察不要求伪造constraint；未触发的完整条件仍在报告，不能被7项公开监控摘要上限或公开性筛选截掉。
- 本端适用基线中的未解约束按稳定ID、scope和限制动作接续；旧audit/v1的effect按同义action兼容。仍blocking/unknown时不能仅保留ID和scope却把freeze/reject/unavailable改为eligibility；已有unavailable须保留自身动作，freeze/reject也不能仅改为unavailable来替代原限制。资格限制可收紧为全局限制，freeze可收紧为reject，持仓复核可收紧为失效/退出；已确认reject/invalidated/exit_required不能改unknown。其它降级或不可比动作替换，先用clear/not_applicable及非空clearance.evidence明确解除原ID，再用独立ID记录新限制，不以unknown或附带空解除说明绕过。取消/暂停/从严的具体条件不合并成无原因布尔值。新证据明确解除才清除，并核每个scope；缺席、遗漏与代码回滚都不是解除理由。

程序核结构、算术、scope与声明的一致性，不替研究者核原始证据。新批次发布前强制此门禁，失败进入原有最多一次输出重试，原暂存报告和回执不改。旧prepared按已验证旧合同/附录运行，不让活跃默认writer改变旧产物。方法不兼容时派生隔离版本的entry/add都阻断，holding风险继续，不建立adopted handoff。已确认风险收紧而报价无法确认时，交付mode=unavailable、p1=null、T1无报价的合法completed v4；audit保留entry/add unavailable及全部适用holding/add约束，完整门禁通过后正常seal，再由发布属主处理control-only。failed/未验收receipt不能直接发布controls；不得用报价失败保留旧eligible。

新冻结 `two-price-controls/v3` 合同另按 [共享证据与恢复验收](acceptance-gates.md) 强制 `stock-research-acceptance/v1`：R14 必要输入仍为任意假设或未知时不能标 passed；有来源约束的保守估算允许，unknown 保留实际 R14 的 add 持续限制。各 scope 的恢复清单须精确覆盖全部有效约束，正文不得以“大部分解除”放宽。单条规则内部原且/或和合法替代路径不变。旧 v2/v1 冻结批次不追补新块；原始实验结果不变，严格复验另存回执。新块存在时即使默认历史 check 也不得忽略。
