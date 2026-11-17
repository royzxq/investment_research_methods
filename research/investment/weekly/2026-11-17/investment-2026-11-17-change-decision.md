# 个股调研框架变化决策

2026-11-17，Asia/Shanghai，generator=codex。用户明确授权“先做最小框架修订，再用立讯、中芯和海光原来的数据包、估值日和证据截止日，固定模型配置复跑”，结果独立保存且不以缩小价差调高估值。

classification：method_change=true，state_refresh=false，evidence_correction=false；update_needed=true。本次方法在本地分支明确采纳，未提交、推送或部署调度服务。

KEY_VARIABLE_CHANGES：新增的是已给价的论证/完整性检查，不改变WACC、增长、折扣、阈值或公司权利的取值规则。UPDATE_FOCUS：canonical §4.1D及compact §7、audit-v7、controls-v10、技能路由与恢复验收。DO_NOT_OVERREACT_ITEMS：DSH并非正确答案；报价可以上调、不变或下调；有界假设不因无法精确拆解而失去观察价值；资格限制、R/D状态、原触发日期与pending保留。

前置依据：[V50驱动审阅](../../studies/valuation-availability/2026-11-16/investment-2026-11-16-v50-driver-review-codex.md)。原审阅指出资本成本、资本效率、长期增长期限和归母范围差异，未证明所有低估值均是偏差。

{
  "kind": "method_change",
  "status": "adopted",
  "summary": "所有已采纳V50完成中性校准；新controls-v10/audit-v7，价格v4不变",
  "definition": "canonical §4.1D：投入/现金回收/终值/资本成本/归属的依据反证替代；逐年生产资本衔接，逐风险计价定位，联合依据和敏感性；不新增价格或资格否决",
  "economic_reason": "使已给价报告也承担中性取值论证，避免多项悲观或乐观假设无依据叠加，以及现金流与资本成本重复补偿；不以接近外部估值为目标",
  "scope": "新股票研究及其提示、审计、恢复和维护完成登记；旧冻结与正式报价不重写",
  "positive_case": "短期高投入有事实锚、远期效率存在合理区间：保留有界估值，量化替代路径而非一律压力化",
  "negative_case": "未来CapEx低于折旧却不能解释资产/产能与终值IC，或现金损失已扣又无残余依据提高WACC：补证/纠错，不自动提价",
  "boundary_case": "V50有价但P1未决仍做neutral_review；真正不可估保留原availability_review；资本对账只能近似可说明代理，不新造空价门槛",
  "compatibility_impact": "新v10/audit-v7增加neutral_review；旧v1-v9提示字节、原审计/输出不变；不声明新旧方法经济等价或自动完成pending"
}
