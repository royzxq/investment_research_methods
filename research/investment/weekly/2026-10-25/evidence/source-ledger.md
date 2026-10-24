# 本期证据总账与采纳边界

AS_OF_DATE=2026-10-25，Asia/Shanghai；generator=codex；统一revision=null；普通检索使用内置web搜索并打开原始来源，未用Gemini。

- [宏观、利率与政策原始来源](macro-sources.md)：披露日、数据期、可读正文和访问失败分列；社零全口径1.1%，美国CPI3.7/核心环比0.3，最新CMT五日不再全部>5%，贷款官方原文缺口。
- [产业、海外、监管、油金美元与香港原始来源](industry-sources.md)：Meta/Tesla新披露、HUTCHMED交割/待到账、10/22美国对外投资提案边界、原始合约/指数口径。末尾补核覆盖前文早期概括；不把本周无微软/AMD财报概括成无海外新财报。
- [A/H行情与口径](market-sources.md)及[tushare-inputs.json](tushare-inputs.json)、[tushare-total-turnover.json](tushare-total-turnover.json)、[calculations.json](calculations.json)：真实API共9次成功，完整性另判；不把深证成指成份股成交当全深圳，不把daily_info统计混入指数口径，不把供应商指数冒充直接交易所收盘。
- [实际方法采纳审查](adoption-review.md)：PR48已合并观测，PR50/51已合并方法；两份实际正文冻结在[investment-2026-10-25-handoff-methods](investment-2026-10-25-handoff-methods/investment_framework.md)。旧handoff方法不兼容，仅可作为历史比较；本期新接续按当前规则重评。

证据截止为10/25实际访问，原始事实最新日期：美国利率10/23、A/H行情10/23、完整沪深北两融10/22、美国CPI/国内PPI/社零数据期9月；公司财报数据期Q3且10/21–22公开。所有未来窗口/前瞻指引标明性质，不使用10/25之后信息。

本期state_refresh/evidence_correction采用授权来自automation-2用户完整full+publish提示；新规则无提案。冻结方法证明字节来源，采纳由实际合并凭证支持，不由helper或最新文件名推定。原主目录公司产物只读核对：恒瑞10/9旧v3报告存在但不足以证明覆盖10/18证据及现行方法的复核，其余四项未见完整配对；五pending，completed=0，不称这些公司从未研究。原trigger_date保留9/24、9/29、10/5，不重置七天冷却。

有效撤回继承：10/11旧change-decision SHA256=06b59f529cf18cbfe55c08dffe10ca99ecb8c75ed5fbba6678e43fe681b2187a的当前有效来源身份已撤回，本期继续承接；旧文原件不改、不作为正向决策来源。旧10/18 r2将由本期新handoff显式supersedes，真实历史行情不撤回，也不复活旧P2或以旧正文“已采纳”代替凭证。

模型配置：启动时automation.toml仍为gpt-6.1-sol/ultra，与用户要求不同。本次通过app automation_update原位恢复gpt-6-sol/high并回读，周日02:00/ACTIVE/项目/提示保持。研究子代理显式gpt-6-sol/high；不能追溯宣称本轮控制器已按目标模型运行。

未知：贷款原文、10/23完整两融、直接交易所指数原件、ICE同合约结算、黄金/ICE DXY连续值、港股净流/分位/股息利差/拥挤度、对应A/H公司最新财务及合同传导和账户执行。null不解释为0、未触发或已解除；已知AND失败的合取可判未满足，缺少其它项不逆转此事实。
