# 最终交付独立一致性复核 r2 · 2026-11-01

generator=codex；复核时间 2026-11-01T01:10:24.152618+08:00。本复核只读三稿、正式锚、两产业底稿、日历说明及本期原料，不修改这些文件。原独立审阅和机械JSON保留。

## 结论

三稿、审计r2及锚记录在原时钟、机械信号、潜在持仓条件管理、三类判定和数据限制方面一致，未发现需要修改方法或核心风控的缺陷。审计r2实际运行 `python3 scripts/validate_futures_audit.py --input research/futures/weekly/2026-11-01/2026-11-01-execution-audit-r2.md` 返回valid、errors=[]；这是结构校验，不证明产业因果、实际API来源真实性、成交或收益。

唯一文字精确性建议已反馈主代理：市场报告输入段“成功刷新r2（JSON）与完整正式快照（TXT）同字节”容易误读成两种不同文件字节相同。实际已独立核验的是刷新r2引用的 `evidence/2026-11-01-signal-refresh-r2/data-snapshot.txt` 与正式 `2026-11-01-data-snapshot.txt` 两份TXT逐字节一致，SHA256=141f69dbf8e57217ee1f6663146959ddf6470fd5c1d146cadd6d1e9234211359。采用稿应写清比较对象。本建议是本期未采纳稿文字精确化，不构成对历史已采纳事实新增撤回或方法变更。

## 已核的一致性

- 五T最新10/30都只标该根no_signal，周内5次历史触发另留；10/27四品种窗口均10/28–29到期，10/29 M窗口原10/30/11/02但10/30已失原突破侧及入场带。未登记旧信号未补新ID或成交。
- MA/M/RB三个存量原ID、signal/registration/deadline均保留；入场过期没有替代持仓退出。MA参考及全原价带初始止损的条件穿越不被反弹复活。RB参考只收紧3099→3096与10/26或27不同入场路径可复核，实际持仓/真实SL未知。
- 最新RB同口径表需201.03→206.07、产174.73→181.18、总库522.16→497.27为真实状态变化；未将上期表需下降判成错误证据。M现货/基差/成交数字明确转引口径，不硬拼库存。MA港库两转引连续性有限，不假称已核同原统计者。
- state_refresh=yes、evidence_correction=no（指未新增撤回已采纳事实；历史M/MA纠错继续）、method_change=no、update_needed=no保持一致。原M/RB初稿方向措辞在本期r2修正并保留原稿，无需因此升级方法或改风险参数。
- 审计共11条候选：5个最新no_signal、3个原计划incomplete、3个V研究incomplete；所有final_lots为null。已知G3 fail与必要unknown同时保留，未误标blocked/awaiting_account；没有示例空账户size-v3计算。
- M/RB的G1不再错误夹带MA2027到期冲突，冲突只归MA。公开交易所参数转引与用户实收保证金、实时行情/扩板/退出能力分列。SSE日期代理、SHFE年度假日/场次与未核全的DCE/CZCE临时安排边界明确。
- 当前三V无数值经济锚，anchors=[]、withdrawals=[]，确无有效旧锚待撤。成本算术仅为单侧组件，未复制对称区间或后造历史锚；MA准备对33个远腿缺口与无锚未评估分开。
- 11条共享来源/16纠错组含39d1与510252同字节重复，三稿没有将其当作独立产业证据。M null/r2登记冲突按明确旧裁决人工接续，requires_*空并未被解读为无需重评。published字节核与实际origin/main远端采用区分。

## 冻结范围与未证明事项

三稿引用的数据覆盖和本复核所读版本如下。本文只记录检查时字节，不另设采纳指针；主任务显式handoff决定最终版本。如市场措辞另修订，以明确采纳修订为准。

- `research/futures/weekly/2026-11-01/2026-11-01-market-research.md`：SHA256 `f6c35b0150e8136074127174351c8a5dcb958179660c6cb8fb355d47d782d3a4`。
- `research/futures/weekly/2026-11-01/2026-11-01-change-decision.md`：SHA256 `401099853c10eb7b6dae822cb7760fbee7c79dee796b7154f85fdcc0de464beb`。
- `research/futures/weekly/2026-11-01/2026-11-01-execution-audit-r2.md`：SHA256 `0f0a0c15338125b89d275175f8c187c7de425091c3d0a584bee51b39bdbe97b3`。
- `research/futures/anchors/2026-11-01/2026-11-01-anchors.json`：SHA256 `52def715004541f4ed1af5d45569d24437bc374804ec9779731221aeb2cad96f`。

未证明事项：全部实际账户/成交/盘中先后与收益；各所临时规则及MA2027精确最后交易日；M同口径库存原表；三V可实现双侧经济区间和5–20日收敛机制。以上作为具体缺口保留，不构成方法缺陷或市场零机会断言。
