# 估值与轻量输出契约

本文件是 `stock-research` 的报价提取与导出接口，不是第二份投资框架。规则、固定数值和强制映射以 canonical 为准。两价方法于2026-10-18明确本地采纳；旧历史仍按版本读取。研究阶段按框架论证 P1/T1 与独立控制，完成报告后再提取最终报价；导出不得重做研究结论。

研究计算及发布门禁见 [研究一致性](research-consistency.md)：报告内保留一份可核算输入与程序生成的可见表，校验利润桥、风险归属、基线折扣变化及冻结/解除合取。新runner批次强制检查，新交付为v4 + audit-v2，忠实报价提取保留；计算检查只拒绝矛盾，不自动更改报价。

## 研究假设如何形成

1. 收入、利润率、估值锚分别列低/中/高情景、证据日期、适用口径和最脆弱假设。利润须区分经常经营、一次性收入与估值收益；不得仅复制卖方目标价。
2. 对 `d_base/r_chip/r_v5/r_gov/r_terminal`，在报告列“已在盈利/倍数中反映的风险→仍需覆盖的风险→本次取值及理由→敏感性”。无额外风险时可论证取 0，不代表缺证据默认无风险。
3. canonical 的标准/上沿/一档未给绝对数值时，先解释本公司可接受的研究区间，再选基准；从严约束选择所论证区间的上侧。所有这些是**本次研究假设**，不是用户账户参数或框架常数。若范围无法论证，补研、换合适模型或给真正不可估结论，不为避免 null 任填折扣。
4. 敏感性至少展示最重要假设变化对 V50/P1 的影响，并核对是否改变结论。敏感性结果不自动成为最终 P1 区间；报告须明确最终采用的 P1 单价或区间及各值含义，不为 JSON 凑齐三档。报告原有 P1 与框架算式冲突时，先回查并在报告内裁决，导出不得静默改价。
5. 不再论证 step_down 或 P2/T2 金额。cap 缺失留在报告参数化，不影响价格计算；首笔/预留60/40以cap_final约束后的计划目标仓位为分母，预留须独立复核且扣已用预算，不因取消追加转给首笔，不生成账户执行计划。

## 导出 v4（四个顶层键；历史 v3/v2 原样读取）

| 对象 | 固定字段 | 语义 |
|---|---|---|
| `meta` | `schema_version, code, name, valuation_date, currency, report_path, generator` | 新交付固定`stock-research/v4`；报告路径相对仓库根；报价币种；实际宿主codex或claude |
| `price_map` | `mode, reason, v50, p1, t1` | P1/T1为仅有的核心价格；无p2/t2占位字段；无仓位或证据副本 |
| `research_controls` | `entry, add, holding` | 每项为`{status,refs}`，只表达当前研究判断 |
| `monitoring[]` | `id, kind, state, variable, current, as_of, trigger, action, source, next_check` | 1–10个重点项目，ID和变量唯一；不替代报告完整条件表 |

### 价格与用途

- `mode=buy_candidate/tracking/observation/frozen/rejected/unavailable`：分别为买入型候选、跟踪、观察、冻结、否决、核心输入不足不可估；不是下单许可。除买入型可为null外，reason必须解释限制。
- 前三种模式须有`v50={low,base,high}`和非空P1对象。单一明确价用`{"base":22.42}`；原报告有明确区间才带正数、有序且成对的low/high，base同时存在须在其内。仅区间用`{"base":null,"low":20,"high":24}`，不补中点或复制三档；不同独立方案不拼区间，先在报告裁决。不得从V50、折扣、敏感性或他端报价重建P1。
- 临时市场/相关事件冻结且事实可靠时完整核算V50/V5、折扣和观察P1，mode仍frozen，能论证的T1也保留；真实硬失败/核心事实不足时不产新P1，旧frozen空值可读。rejected/unavailable不产新P1；V50可保留注明来源和失效边界的已核参考，没有则null。缺价不停止持仓逻辑检查。
- `t1={price_condition}`仅一个完整价格表达式：明确金额`股价≥30.85元/股`（CNY可用元/CNY，HKD可用港元/HKD），或`接近V50上沿时复核`、`接近V50下沿时复核`、`接近V50基准时复核`；相应V50值必须存在。金额为有限正数，CNY最多2位、HKD最多3位有效小数；不由程序暗改精度。
- 无独立T1、按既有V50基准回退时用基准引用，报告说明兜底依据。确实无适用价格条件时只用`当前不适用`或`本轮不提供T1报价`，报告说明原因；冻结/tracking/当前持有不卖不是撤回观察报价。公式、百分比、现价及行情日只写报告，不夹入表达式。多报价未裁决不能任选或改成无报价。
- T1的非价格事件和全部适用旧T2事件按新canonical进入报告完整条件表：加仓约束、逻辑失效、复评/减仓、退出分别保留，逐条有去向，不限10条。重点项进入monitoring，当前生效/未知的控制进入audit-v2；不重新报价P2/T2。

### 研究控制与监控

新交付 audit 显式填写 lifecycle，具体判据及旧冻结批次兼容见[研究一致性](research-consistency.md)。持续研究限制/必要资格缺证才进入未解集合；纯现价与收益条件交运行时，未触发信号仅观察。buy_candidate 不表示现价已满足 P1；holding-only 复评未知不扩大建仓/加仓。有效旧限制、TEMP、R6 事后复评和 D5 重建不能因精简自动清除；多来源独立主张逐项覆盖后才解除。

- entry/add的status为`eligible/blocked/unknown`；holding为`normal/review_required/invalidated/exit_required/unknown`。refs只引用本报告稳定约束/监控ID，条件的具体暂停/取消/从严含义、解除证据仍在完整表和审计中。
- eligible仍需价格、账户、组合与执行核验；entry/add任一eligible必须mode=buy_candidate，tracking/observation/frozen/rejected/unavailable均不得eligible。只加仓受限可entry eligible、add blocked；全局freeze/reject/unavailable必须覆盖entry+add，不使用entry-only freeze。
- entry/add unknown不能增加对应暴露；holding unknown要求补证/复评，不写成已失效/已清仓。确认invalidated/exit_required阻断entry+add，持仓复评不自动等于全局冻结。eligible/normal的refs=[]；blocked/unknown/review_required/invalidated/exit_required必须有可解析依据，refs精确等于audit该scope全部blocking/unknown ID的集合，不遗漏、不混入其它scope或普通经营观察。观察依据仍可留在monitoring。
- monitoring.kind为`general/entry_constraint/add_constraint/thesis_invalidation/exit_condition`；state为`watching/triggered/cleared/unknown`。控制相关项目与同ID审计相符：triggered→blocking，unknown→unknown，cleared→有非空clearance.evidence的clear或not_applicable；watching不进入未解集合。首次不适用可不填clearance，但解除历史阻断即使用not_applicable也须有解除证据。一般经营跟踪无需伪造constraint。
- current为数值、带单位文字或null；非空必须有不晚于估值日的as_of。source定位URL/公告章节/包字段；trigger含窗口、单位、方向，action明确复评、重算、暂停追加或持仓处置。next_check为日期/明确事件；未取得时current/as_of可null，报告写补证路径，不以0冒充。
- 历史有效阻断按稳定ID/scope接续，来源缺席、未再提及、unknown不表示解除；新证据明确解除才清除。方法兼容性待复评时派生版本frozen并阻断entry/add，原报告、JSON、回执与holding风险保留，不自动提升latest。

字段不重复保存完整Gate、折扣、cap、评级、证据及推导；它们继续在报告，schema简化不删除研究。generator来自实际宿主，旧v2缺来源保持缺口，历史重提取宿主不能冒充原作者。

### 旧批次与风险收紧交付

普通build只写v4。旧冻结批次必须按已验证合同读取[legacy-v3-output](legacy-v3-output.md)及[legacy-audit-v1](legacy-audit-v1.md)，显式传`--legacy-snapshot <本批run/framework-snapshot/manifest.json>`，使用原冻结方法和原prompt/input/hash。不能只保留旧prompt却让新版默认技能/writer重解释旧产物；无法恢复原合同则新建批次。历史v3/v2读取不强加v4门禁，不自动批量迁移。

报价与已验收的控制应交同一发布属主处理；报价缺失/歧义/倒挂时不伪造金额或回退旧eligible。已确认阻断/退出可交属主按其control-only事务及时收紧，旧价格及价格日期不变。该路径仍须合法completed v4：本轮报价无法确认时mode=unavailable、p1=null、t1.price_condition="本轮不提供T1报价"；audit按事实记录unavailable约束覆盖entry/add，并保留已确认holding/add约束，报告记录弃用报价及原因，通过完整审计后正常seal。failed或未验收receipt本身不能发布controls；研究者不直接写业务CSV。available_at由真实封口/原子发布属主给出，不能按估值日零点倒填。回滚代码或报价不撤销已确认风险事实。本工作区不执行生产写入。

## 大模型价格提取与裁决（组装交付前）

由执行本轮`stock-research`的大模型阅读最终报告价格节，完成提取、消歧和取值，再核对候选JSON；程序负责结构、数值与状态校验。不把程序报格式错当成模型拒绝报价。先完成下列语义自检，再填 v4 字段：

1. **逐字段确认本轮最终含义**：P1取报告本轮最终明确单价/base；仅明确区间时保留边界、base=null；无明确 low/high 不补造。T1定位明确卖出阈值/复核起点。区分`有效报价`、`明确撤回/拒绝`、`未找到`和`仍有歧义`；现价、日期、百分比、估值上沿及P1只是各自字段，不能混作T1候选。旧值、历史例子、另一端结论不冒充本轮报价。
2. **T1取值优先级**：唯一明确的本轮数值起点且未被撤回→用该起点；仅明确V50上沿/下沿/基准→用对应值；无独立T1且无拒绝、无边界指定而本轮有有效V50→用base并明确标记兜底。真正明确拒绝或价格条件不适用时才交付相应无报价表达式，说明原文依据。冻结/tracking/暂停追加及“当前持有不卖”是执行状态，有明确观察报价就保留。
3. **兜底止点**：P1 多个独立报价未裁决、缺价但未明确拒绝、V50文字/对象真实冲突、只有比例而无明确数值起点、无适用V50的未知缺项，都不能靠base、任选最低值/平均值、重算或清空字段绕过。先在本轮报告内裁决；仍无法确定则用failed回执说明缺项/冲突及所需澄清，保留旧生产数据；若已有可独立验收的风险收紧，按上文合法completed unavailable交付路径完整审计，不能直接消费failed回执。研究端不把P1改成V50或他端报价。
4. **算术与精度**：例如“≥30.85元，等于上沿34.28×90%”→T1=30.85；34.28是计算锚、22.80是现价，二者都不是另一卖出阈值。用确定性十进制工具核对公式、边界与原文精度；程序负责数值一致性，大模型负责解释字段归属。自动交付CNY2/HKD3位有效小数；过精度先核对源报告并明确修订精度和理由，不让程序暗改报价。仅有90%没有明示金额，不将计算结果冒充已提取报价。
5. **清晰交付与回读**：在既有报告价格节记录所选值、状态、原文位置/引句、排除的行情/旧值及引用或兜底理由；P1明确报价写相应字段，T1写上节单一表达式，控制按报告与audit提取，不自行增加契约外审计字段。按“报告→报价提取输入→build/check→回读实际输出”逐值核对一致性。格式错时模型定向提取/消歧后重新交付，不能仅改文字使检查通过而改变经济含义。

首次输出失败后，现有一次重试会提供原错误与本轮同端暂存草稿位置。它们是未验收数据，先核对股票/生成端/日期和本轮冻结输入，只读第一次草稿并写新的retry目录；仅语义/格式问题优先定向修正，不默认重新取证和估值。缺草稿、输入/来源失效或实际研究问题按原研究流程补证，哈希/路径/结构门禁照常。重试后仍失败就保留失败回执，不循环调用模型。人工自由文本录入另按ai仓交易决策skill取值及两位小数约定，不将其三席7天规则用于自动批次。

## 报价导出工具

先完成报告和最终价格裁决，再组装临时报价提取输入，放本次 `output/stock-research-.../`；生成候选 JSON、完成回读和语义验收后，再移到未占用的最终日期路径。工具保留 P1/T1 输入报价，不读取自然语言自动猜价、不取行情、不判 Gate、不更新 latest、不覆盖文件。

```sh
python3 scripts/stock_price_map.py build --generator codex --input output/<本次目录>/quote-input.json --output output/<本次目录>/investment-<代码>-<日期>-price-map-codex.json
python3 scripts/stock_price_map.py check output/<本次目录>/investment-<代码>-<日期>-price-map-codex.json
```

临时输入只有`meta, mode, reason, valuation, p1, t1, research_controls, monitoring`。除valuation单位换算外与最终字段同义。P1/T1均由报告明确提供；旧discounts/step_down/p2/t2输入拒绝，不保留重推价分支。meta可省略schema_version，默认补v4；旧冻结合同只有显式legacy writer可写v3。CLI必须`--generator codex|claude`并与已有meta一致；输出JSON与报告名称按代码、估值日、生成端和rN后缀配对。

`valuation` 二选一：

```json
{
  "kind": "equity_value",
  "values": {"low": 486, "base": 630, "high": 792},
  "currency": "CNY",
  "unit": "100_million",
  "shares": 2214000000,
  "fx_to_quote": 1
}
```

上例只是单位接口演示，不代表本期正式研究结论。`equity_value` 是归属于普通股股东的权益价值，不能直接填 EV；unit 仅 `currency/million/100_million`，股份数为实际股数，不是“亿股”。

```json
{
  "kind": "per_share",
  "values": {"low": 19, "base": 31, "high": 50},
  "currency": "HKD",
  "unit": "per_share",
  "fx_to_quote": 1
}
```

每股模式不再传 shares。跨币种必须补 `fx_source`（出处、日期、方向）；`fx_to_quote` 定义为“1 单位输入币种等于多少报价币种”。例如 1 HKD=0.865 CNY，HKD→CNY **乘 0.865**，CNY→HKD **乘 1/0.865**。同币种只能为 1；工具无法判断经济上正确的汇率方向，必须独立用反向等式验算。

以下仅演示buy_candidate下首笔可评估、仅加仓受限的片段；ADD_PLAN_CANCELLED必须在报告audit中真实存在并有取消原因/复核条件，实际报价与状态逐项提取原报告：

```json
{
  "p1": {"base": 22.42},
  "t1": {"price_condition": "接近V50上沿时复核"},
  "research_controls": {
    "entry": {"status": "eligible", "refs": []},
    "add": {"status": "blocked", "refs": ["ADD_PLAN_CANCELLED"]},
    "holding": {"status": "normal", "refs": []}
  }
}
```

只有原文另给区间时，P1 才可为 `{"base":22.42,"low":17.29,"high":28.18}`；原文仅给 17.29–28.18 时用 `{"base":null,"low":17.29,"high":28.18}`。单价不复制成三个相同值，区间不求平均。原报告多报价、公式与明示金额不一致时先裁决，不能为了通过校验改数字。

临时冻结且可估仍论证valuation/折扣并导出观察P1/T1，entry/add均不得eligible；rejected/unavailable或事实不足的frozen不产新P1。历史v3/v2不自动转v4；明确要求重提取时逐份读原报告，保留实际空值、来源和日期，新控制缺乏证据不能补造eligible。

P1/T1统一为报价币种/股，CNY最多2位、HKD最多3位有效小数；超精度先在报告明确修订，导出不静默舍入。V50仍可十进制换算单位/股本/汇率后舍入，不参与P1导出计算。build/check拒绝非有限数、布尔伪数、重复键、错误币种/状态及退役字段；检查P1结构、T1表达式/V50显式引用和控制摘要。完整scope/refs/解除关系另由research_consistency验证。程序不能证明原文提取、事实、模型合理性或全报告一致性。

## 验收后发布到本地

- 正式报告必须含本次研究的数值、单位、来源、假设和敏感性，以及明确最终 P1/T1 与独立控制/完整条件表；不要求用户翻 scratch 才能复核价格。
- JSON 与报告同一生成端、同一版本、同一隔离后缀（如 `-price-map-codex-r2.json` 与 `-research-codex-r2.md`）；报告 §0 记录数据包和两个框架的指纹及本次证据截止。新增来源、参数或证据状态变化都不能只凭旧文件存在而复用。
- `output/indexes/investment/<市场>-<代码>/investment-<代码>-latest-<生成端>.json` 只缓存同一生成端截止日内最近合格的正式 v4/v3/v2 配对，保持与日期 JSON 完全相同；`research_paths.py latest-company --generator <生成端>` 同口径；省略生成端或指定 `unattributed` 只查旧的未标注文件，`rebuild-indexes --as-of <日期>` 按该截止日重建，找不到合格配对时清除该公司的旧缓存。选择按估值日期而非格式版本、修改时间或价格是否非空：较新的 frozen/rejected/unavailable v4/v3/v2 仍优先，禁止回退到旧的有价结果。
- v1 只可经 `latest-company --generator unattributed --include-legacy` 作为历史研究读取，不参与当前价格缓存。若日期更晚的文件仍是 v1，明确告知“最近合格价格地图估值日”和“较晚 v1 历史日”，不能把旧空值误当本次结果，或把较早 v4/v3/v2 重新标成后日期估值。隔离版不更新 latest；升级须用户已有明确授权。
