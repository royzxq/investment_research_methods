# B-v2.24 离线验算输入

运行 `python3 scripts/seasonal_plan.py --input /绝对路径/plan.json`。依据为canonical 1.6和Step5-B。工具只算日历和计划价格，不取数、不计算完整信号或最终手数。

顶层字段：

| 字段 | 内容 |
|---|---|
| window_id | SR-summer / CF-spring / CF-autumn |
| as_of_date | 最近完整行情交易日，YYYY-MM-DD |
| trading_dates | 覆盖当年窗口前20交易日、窗口及两端相邻日期的完整交易所交易日数组，升序且无重复；不可用普通工作日代替 |
| plan | 可省略：先筛选窗口。提供时字段见下表 |

plan字段：

| 字段 | 内容 |
|---|---|
| contract | 具体SR/CF合约，YYMM，如CF2701 |
| entry_date | 晚于as_of_date的拟入场交易日；下单前行情改变需更新计划 |
| contract_latest_exit | 依既有合约规则核定的最晚退出交易日 |
| ma20 / atr20 | 该合约截至as_of_date的既有指标，元/吨 |
| pre_window_low5 | 窗口开始前5个交易日最低low，元/吨；固定窗口，不能换成最近5日 |
| tick | 当前SR=1、CF=5，元/吨；交易所规格改变先更新规则和工具 |
| history | 前三年各一个对象，必须含亏损年份，内容见下文 |

每个history对象包含year（整数）、contract、trading_dates、entry_date、exit_date、entry_settle、exit_settle、listed_on、last_trade_date、price_basis（必须settle）、source（非空出处）。日历要求同上；两端日期按当前拟入场/最晚退出的月日映射至历史年份：入场向后找交易日，退出向前找交易日。合约保持交割月和相对年份差。工具核日期映射、上市期限声明和正负收益均值；不能认证来源、日历完整性或报价真实，研究记录仍需原始证据。

输出screening只表示研究窗口；prices_calculated只表示价格已算出，仍须计算含成本net_R并核其他门。fails_time_window / fails_nonpositive_target是已算出的计划失败，不等于候选主状态blocked（账户或其他必要项未知时仍incomplete）。输入错误退出码2，不回填数字。

合成输入的完整构造见tests/test_seasonal_plan.py；它只验证算术，不能作为真实市场数据使用。主行情脚本暂不自动组装B历史输入，已有接口或终端导出由研究方按上述字段整理。TP1启动跟踪及移动止损按canonical执行，不由本工具下单。
