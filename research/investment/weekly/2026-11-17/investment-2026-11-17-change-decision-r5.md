# 自动红利路由变化判定 · 2026-11-17

采用依据：用户明确要求在ai_investment每日研究前自动判断红利，并确认“默认改成2个百分点，其他的没有问题，可以开始实现”。这是method_change，不是行情状态刷新；本轮不新增市场元研究。

KEY_VARIABLE_CHANGES：无新的市场状态。UPDATE_FOCUS：共享C0、红利HD1、两轨入口/模板、数据分类、不可变批次与恢复。DO_NOT_OVERREACT_ITEMS：分类不等于质量合格或交易许可，不能解除旧风险、改变估值算法或宣称方法有投资有效性。

{
  "kind": "method_change",
  "status": "adopted",
  "summary": "每日自动研究按冻结股息利差分流，默认严格大于2个百分点",
  "definition": "TTM税前股息率减同日同币种十年政府债YTM；严格>配置阈值（默认2个百分点）进入dividend，否则non_dividend。股票最近观测距估值日0–7自然日；缺失/未来/超龄/币种不符为pending，不发布任务。冻结research_route/v1及规则dividend-spread/v1，恢复不重算。",
  "economic_reason": "先将高历史现金收益候选送入可持续分配质量研究，避免以成长框架替代分红分析；历史利差只是研究分工，不能证明买入价值或未来分红安全。",
  "scope": "ai_investment每日refresh_data_packs新任务与methods接收/提示/技能/报告§0；无元数据的手工及历史任务保持原路由。",
  "positive_case": "股息率4.01%、国债2%、阈值2个百分点：利差2.01，红利补充取数并用独立红利框架。",
  "negative_case": "股息率3.99%、国债2%：利差1.99，沿普通股票研究；股息率未知不归普通。",
  "boundary_case": "4%减2%=2个百分点，等号不进红利；超过7自然日、缺同日利率或港股缺HKD基准为pending；特别分红虚高仍在红利轨识别，不中途换轨或自动买入。",
  "compatibility_impact": "新可选元数据仅对新批次生效；旧prompt/input/hash不改。六文件v2、controls-v10/audit-v7与价格v4保持，旧控制及5 pending/4撤回/25评估原样接续；两仓须共同部署，工作树实现不等于生产上线。"
}
