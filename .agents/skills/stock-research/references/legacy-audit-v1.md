# 冻结旧批次的 audit-v1 附录

仅冻结快照明确要求 `stock-research-audit/v1` 时作为交付门禁；原 `research_validation=null`/缺省旧批次不追溯增加本门。历史审计读取可使用本附录。
只供已经验证的旧 v3/v2 冻结批次及历史渲染读取；普通新交付使用 audit-v2。审计块、旧 prompt/input/hash 不追溯改写。与 [旧 v3 输出合同](legacy-v3-output.md) 配套，不能用本附录规避新批次按 scope 的控制检查。

# 研究计算与状态一致性

这是发布验收契约，不新增投资方法、折扣常数或买入门槛。最终价格JSON继续使用v3；历史封口不追溯改写。

## 一份可核算底稿

先裁决估值假设，再建立临时 `research-audit.json`，完成报告并提取明确报价后生成核算展示：

```sh
python3 scripts/research_consistency.py render --audit output/<本轮>/research-audit.json --price-map output/<本轮>/price-map.json > output/<本轮>/research-checks.md
python3 scripts/research_consistency.py check --report <本轮报告.md> --price-map <本轮价格.json>
```

把生成内容完整放入报告§5或§7，保留唯一的可见核算表与可展开JSON审计块。经营假设的数字表以此为准，正文解释依据，不另写一套未经桥接的收入/利润表。九节、原始证据、现金桥、Terminal、敏感性和监控仍按原契约完成。

程序只检查并拒绝矛盾，不重写P1/P2。计算模型先正确，再从报告提取报价；不得通过换成`other`、删除基线、清空报价或改折扣绕过错误。非PE方法如实选`other`并保留其完整适用计算；真正不可估选`unavailable`，说明阻断输入。语义与来源仍须人工核验。

## 审计输入

顶层字段固定为 `schema_version, identity, valuation, baseline, discounts, risks, constraints, release_all_of, p1_basis`。

- `schema_version`：`stock-research-audit/v1`。
- `identity`：`code, generator, valuation_date, currency`，与本轮价格JSON一致。
- PE模型 `valuation`：`kind="profit_pe", currency, amount_unit="100_million", shares, fx_to_quote, horizon, profit_basis, scenarios`。shares为实际股数；同币种fx=1，跨币种方向与依据留正文。
- `scenarios`必须有low/base/high，每项为`revenue, net_margin, adjustments, profit, pe, equity_value`。利润率用小数，例如11%写0.11。每项强制核验`收入×利润率＋调整=经常归母利润`、`利润×PE=股权价值`，再核股本/币种换算后的V50。
- `adjustments`默认空数组。有合并范围、少数股东或非经营调整时，每项写`id, amount, reason, source`，金额与收入同单位，给来源与桥接理由。不得加一个无来源调整专门凑到旧目标利润。
- 非PE模型的`valuation`为`{"kind":"other","reason":"适用方法与计算位置","unrounded_v50":{"low":20.005,"base":24.005,"high":30.005}}`，明确提供未舍入的报价币种/股值；不可估为`{"kind":"unavailable","reason":"具体阻断输入"}`。非PE的专项计算仍由原估值契约和人工验收负责，不从已舍入JSON倒算未舍入值。
- `p1_basis`只列已明确报价的字段所对应的V50情景，例如单价`{"base":"base"}`，实际区间可为`{"low":"low","base":"base","high":"high"}`；base=null不填对应键。核验公式与明确报价一致，不代为生成缺价。

折扣 `discounts`固定五项 `d_base/r_chip/r_v5/r_gov/r_terminal`，每项包含：

```json
{
  "value": 0.15,
  "range": [0.10, 0.15],
  "risk_ids": ["MODEL_RESIDUAL"],
  "reason": "本公司、本期论证，示例数字不是默认档位",
  "change": {"kind": "initial", "reason": "无适用基线的首次研究", "evidence": []}
}
```

有基线时，数值和已有论证区间未变用`unchanged`；有变动必须用`new_evidence/correction/model_change/method_change`，写原因和非空`evidence`引用，并在正文给参数隔离敏感性。方法变动引用已采纳方法，未合并提案不生效。不能只重新定义更高的“上沿”而不说明变化。相同事实及模型先沿用同端适用基线，跨端只作有归属参考，不强行统一不同模型。

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

`risks`每项为`id, description, owner, scope, source`。owner只能有一个：`revenue/margin/multiple/eligibility`或五个折扣项之一。

- 已在收入、经常利润率或PE吸收的风险，不能同ID再收费；R9缺项等资格限制不自动成为高拥挤或数值损失。
- 同一大类风险确有不同影响时拆分ID，并在scope说明已吸收部分、残余部分及对应证据。例如普通质保成本已进利润；仅超预提支付与回购的额外联合尾部留给r_v5。不能换名复制同一损失。
- 每个非零折扣必须引用自己独占的风险ID；零折扣列空risk_ids并解释归零原因。没有独立终局溢价、已保守估PE时，不为凑齐五项强设r_terminal。
- 不把当期OCF再加到已经包含它的期末现金；未来普通质保/营运资本支付若已进预测OCF，不再次全额扣现金桥。理财、受限/经营必需现金、认缴/实缴、索赔/判赔分开。

程序能拦截相同ID的跨桶扣减，不能判断两个不同ID是否实为同一经济风险；主代理仍须审查scope、原文和现金桥。

## 冻结与恢复

`constraints`每项为`id, effect, status, reason, release_conditions`：

- effect：`freeze/eligibility/reject/unavailable`；status：`blocking/unknown/clear/not_applicable`。仍有效或未知的适用约束均保留。
- 有效freeze不能输出tracking/observation；确认否决用rejected；核心事实不可估不产新P1。仅R9等资格限制可以继续观察估值，不能据报价非空推定可买。
- D5先解释本轮是低位轮动新承接还是独立财报复评；不可把财报触发自动改写为轮动用途。判定其适用冻结后必须frozen。R21退出仅回等待复核，原重建路径独立可用；完整买入/P2恢复仍须全部适用条件和逐股复评，不把“退出深化”写成完整解冻。
- D5适用时另带`clearance={"stage":"deepening|unknown|waiting_review|rebuild_pending_company_review|rebuild_review_complete","evidence":[]}`。R21退出只填waiting_review，不能把status标clear；只有原重建及公司复评都完成、给非空证据引用时才可用rebuild_review_complete/clear。程序核阶段一致性，不替研究者核验引用中的真实市场数据。
- `release_all_of`必须列齐全部blocking/unknown约束ID；每个约束的release_conditions写其必要解除证据。不同合法路径的择一仅可发生在该规则内部，不能用一个约束的解除覆盖其他约束。

新准备的runner批次在发布前强制执行此门禁，失败进入原有最多一次输出重试，保留旧生产结果。旧prepared批次保留其已冻结输入契约；旧封口继续读取，不伪称已经通过新检查。方法兼容性隔离只在派生版本增加状态约束并重验，原暂存报告和回执不改。
