# 个股调研框架更新结果

## 1. 更新结论

2026-10-25，Asia/Shanghai；generator=codex；full+publish；revision=2。state_refresh=true、evidence_correction=true、method_change=false、update_needed=no。当前已采纳方法为PR #50/#51合并后的 `stock-two-price-controls-v2`；本期没有新增方法提案。

本次仅更新canonical与compact各自唯一 `investment-state:start/end` JSON事实块，观测截止10/25、行情10/23、完整两融10/22。块外逐字不变。方法正文和本报告只在本期统一PR待人工合并，不自动合并；日期研究与独立adopted状态/纠错handoff按原授权另行发布main。待审观测版本不替代已冻结的采纳方法来源。

## 2. 受影响模块

| 位置 | 原因/分类 | 对象与摘要 |
|---|---|---|
| 两份框架唯一观测块 | state_refresh | 更新9月社零、10/23利率/指数/成交、10/22完整两融；缺10/23两融、官方指数原件、贷款、油金美元等保留null |
| 日期研究/新handoff | evidence_correction | 旧方法handoff在#50/#51之后不兼容；新接续按合并正文重评，承接五pending与原撤回，不改旧记录 |
| R/D、估值、Gate、Price Map、控制生命周期 | 无正文变更 | 全部保持已采纳规则；P1/T1、entry/add/holding、60/40及168h冷却不变 |

## 3. 修改说明

经济依据：美债最新五日不再全部严格>5%，但FOMC合取出口未发生；社零1.1%未过内需解除线；周五放量不足以替代连续三日与完整两融/官方指数条件。海外资本支出与现金回报分化，必须分别核A/H订单和盈利。这里只更新事实，不因行情单周变化改永久门槛。

动作与例外仍由现行canonical裁定：市场/事件临时冻结但估值事实可靠，可有冻结观察P1/T1；报价非空不是买入许可；only-add限制不擅自扩成entry冻结，holding-only未知不扩大新增；确认失效/退出及对应缺证按原scope接续。原P2只在历史中，不输出active。事件按实质暴露及时间窗，不凭周更日期冻结全市场；缺证不解除独立持续主张。R21退出只回等待复核，原>2万亿独立重建及逐股条件不变。

正例：同组三个A股交易日，成交1.61万亿、完整两融日差-149亿、官方指数1516.2，R21 helper=met，但仍只允许等待复核，不直接买入。反例：本期10/21、22成交<1.6即not_met，10/23放量不补前两日。边界：成交=1.6或两融=-150不通过，指数=1516.2通过；缺任一关键值且无已知失败为unknown，融资代理与非官方指数不得冒充完整输入。UST=5.00不满足>5；社零1.1%与贷款unknown的AND结果为未满足。上述案例检查现行规则，没有引入新定义。

兼容影响：本次新旧方法指纹分别相等，状态可消费；旧10/18 handoff方法在#50/#51之后不等价，不伪造兼容。新handoff显式supersedes旧r2，承接原撤回与五pending，完成仍需新方法下完整配对/定向重评凭证。没有研究批次或交易执行。

## 4. 不应过度反应

利率回落、周五反弹、海外capex、政策方向和其他公司BD都不单独解冻。PPI正值不替代需求，现货不触发期货结算阈值，ETF成交不代替净申购，旧报告存在不等于本轮复评完成。缺账户填null。

## 5. 新版框架链接

[canonical](../../../../framework/investment_framework.md)；[compact](../../../../framework/investment_framework_compact.md)。完整证据及状态见[本期元研究](investment-2026-10-25-market-research-r2.md)、[变化报告](investment-2026-10-25-change-decision-r2.md)、[handoff](investment-2026-10-25-handoff-r2.json)。不粘贴方法全文。

## 6. 版本变更记录

| 文件 | 旧完整SHA256 → 待审新完整SHA256 | 方法指纹 |
|---|---|---|
| canonical | 773677164aee09f006d80afda8e7484f00b05a489061903754b7f76ffec78ed7 → c570475a042643df8ecad64a92b50ee86d4816a983430ce805d76f17a88c3378 | 1ba69fd41b54c45a3b1109a1532b9a51f9a9e65026723af6439a2267d0747f0f（不变） |
| compact | 57d9a8e4530e32e53a5d06ab80dc7244d3dc67fd28d95951890dc68c25453ea2 → 7abbcae54201ae58765abac70e7b50ae35fb2764b9133d41da23e2863d38c673 | e38a4400f41f7991170767d145de4b1501050972a2b3d71ec11590114ce84b5f（不变） |

采纳方法源为#50 merge `6f797ed9223225b68b97db7f7dc9e2cc1c44ab43` 与#51 merge `346caada9172b4346c6b9246cb66978b06024ba4`；当前冻结方法是本期编辑前主线实际字节。本期新观测两份正文仍待审；未来合并后若需绑定完整新字节，应新建接续，不重写旧记录。

## 7. 验证

- 股票governance在编辑前、后均通过；块外字节、两份method_fingerprint和新观测JSON相等检查通过。完整指纹/尺寸见[evidence/observation-sync-r2.json](evidence/observation-sync-r2.json)。
- 全量离线1125项，158.189秒：1080通过，45项因沙箱禁止127.0.0.1绑定或ps报error；同45项在允许该环境能力下定向复跑54.659秒全部通过；股票maintenance定向41项另在0.289秒通过。不是一次全量无错；没有因测试失败修改本次无关实现。原始日志保留worktree output/runs/investment/2026-10-25/automation-2/。
- 真实API：Tushare两轮共9次trade_cal/index_daily/margin/daily_info均成功，返回字段完整性另判；10/23缺深北两融保留null。官方网页与二级行情口径分别见来源账本。未调用账户/交易API。
- handoff来源、选择、生命周期、未来日期/撤回及R21等号/缺口/跳日边界验收见[evidence/validation-r2.json](evidence/validation-r2.json)。这些结构和离线测试不证明所有金融语义、研究方法收益或交易有效性。

## 8. 精简版同步

按 `framework-condense` 及fidelity reference进行受影响范围同步。canonical/compact的观测JSON完全一致；块外均逐字保留。compact UTF-8字节/行数57051/340 → 59202/412；canonical89996/581 → 92147/653，增量来自新增带来源的事实/null，不为压缩而删有效规则。

七项自审：①受影响观测全覆盖，未改规则保持原载体；②数值、单位、比较符及公式均在块外字节保留；③R1–R21、D1–D8编号和引用结构检查通过；④R21正反/等号、R3合取与盈利例外、scope控制三类自包含抽检未见新增规则；⑤无副本新增矛盾，两块相同；⑥决策链块外不变；⑦尺寸及范围如上。未宣称对历史全框架100%语义等价或投资方法有效性。

## r2交接补录

整包r2补齐10/9美债历史触发的直接证据，首份保留但不作为最终接续。观测块source_report同步指向market-research-r2，方法指纹不变；本PR当前应审r2报告。
