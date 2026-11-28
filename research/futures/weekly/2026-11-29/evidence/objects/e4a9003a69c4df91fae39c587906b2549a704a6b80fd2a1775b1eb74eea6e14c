# 甲醇现有信号重评：当前登记，未来执行

研究日2026-10-11，Asia/Shanghai；generator=codex；行情截至10/09。范围：定向纠正r2的版本时间限制并重评MA2701，其他路线沿用已核筛选，不重跑全市场研究。框架v3.0本地澄清版，`assessment_scope=proposed_framework_reassessment`；旧[r2审计](2026-10-11-execution-audit-r2.md)及[市场研究](2026-10-11-market-research-r2.md)保留。

## 结论：已有多头信号，不必再等突破3402

此前把“不能回填历史建议/成交”扩大成“框架升级前发生的信号不能用于未来决策”，确实过于机械。现已在完整版与精简版澄清：**价格信号日、当前评估/登记时间、未来执行时间分别记录。尚在原有效期的T信号可以当前重评；两日有效期不能重启。** V仍须有信号前冻结的经济锚，不借此允许事后造锚。

MA2701在10/09收3338，高于排除当日的前20日高3200，ATR20=99.1645568，价格条件已经成立。原可入场交易日是10/12、10/13；10/11登记时，归属10/12的周五夜盘已经发生，不能补记交易，本计划最早从**10/12 09:00日盘**评估。

3402是10/12形成另一个新信号时使用的滚动高线，不是10/09现有信号的新增入场门。仍需遵守现有信号对应的3200突破侧及0.5ATR价格偏离限制。

本次将MA从“版本时间资格失败”改为**有信号的多头研究计划**。G2与计划算术可通过，完整合约日期核对和G4执行核验仍有缺项，故总体为incomplete，尚非ready或仅差账户。原8条路线中仍为6条no_signal、2条incomplete，但MA的原因、计划完整度和下一步已经改变；不能仅看状态数量断言没有进展。

## 1. 具体多头计划

| 项目 | 研究计划 |
|---|---|
| 合约 / 方向 | MA2701 / 顺势做多 |
| 原价格信号日 | 2026-10-09；当前登记不修改这个日期 |
| 入场有效期 | 10/12、10/13剩余未来交易时段；最早10/12 09:00，截止10/13日盘收市 |
| 价格允许范围 | **3289–3387元/吨**：3338±0.5×99.1645568，向内取整，且高于3200 |
| 选定研究报价 | 3338元/吨；仅为待未来实际报价确认的计划价，没有假设该价现在可成交 |
| 初始止损 | `floor(实际Entry−2×ATR)`；整数Entry对应Entry−199。参考3338入场，**SL=3139**；3289/3387入场则分别3090/3188 |
| 目标 / 退出 | targets=null；入场日收盘后按最近10个完整日low形成下一时段止损，只收紧，最长20交易日 |
| 时间退出 | 10/12入场最晚11/06；10/13入场最晚11/09；更早合约、事件、逻辑失效或止损退出优先 |
| 成本与每手风险 | 研究预算往返手续费20元、滑点20元（2tick价值）；参考每手价格距离风险1990元、含预算2030元。20元费用是研究假设，未声称用户实收；实际成本更高须重算 |
| 手数 | null；真实账户、保证金、限仓、执行及压力容量齐全后用size-v3取严，不从配置资金推算 |

开盘跳到3387以上，不追这份计划；跌破3289也不直接挂单等回到旧价，而须重新核产业解释、报价、止损和剩余有效期。10/13收市前未成交则此信号失效。新的完整日若产生新信号，可以另登记，但不能把未触发的滚动计算当成旧计划自动续期。

## 2. 产业依据与反证

已重新读取[同花顺正文的隆众周度转引](https://goodsfu.10jqka.com.cn/20261008/c680471840.shtml)：截至10/08港口样本库存30.51万吨，较上期减少8.84万吨；同文国产甲醇产量208.19万吨、周增6.02万吨。窄范围的偏多解释是港口供给偏紧仍可支撑价格；国产复产和需求承接弱是反证，不能宣称全国供需都紧。

[10/09仓单日报转录](https://www.99qh.com/article/%E9%86%87%E7%B1%BB-1101000)为5316张、日减182。重新核得[甲醇业务细则](https://www.futureslaw.org.cn/czcepzxz/1436.htm)存在11月集中注销边界，故这一变化不能独立证明1月可交割供给短缺。原表访问和月份传导限制保留，证据质量weak、market_risk=0.5只折一次；没有把关键执行缺项用weak替代为通过。

若随后同口径港库回补、国产复产/到港增长能解释供给宽松，并且实际现货或基差转弱推翻偏紧逻辑，应取消该多头计划。单个反向读数不机械等于长期看空，也不再套旧创新高禁入或永久方向冻结。完整取证见[MA本轮证据](evidence/v3-r3/ma-current-rules-codex.md)。

## 3. 仍需解决的执行条件

G1已核真实合约范围、10吨/手、tick1和日均量724224.95手。具体最后交易日仍需冻结基础表：产品规则为交割月第10交易日，按已有日历推得2027-01-15、从10/11左闭右开计68日，而源快照只给67日、未保留对应delist_date，差异未裁决。两者都明显超过本计划最长持有期，但不能把精确日期写成已交叉核实，G1保留unknown。自然人交割月限仓0；经纪商更早退出属于G5。

G4当前缺项是10/12实际适用板幅、交易所保证金/临时限仓，以及未来可成交报价和压力场景的最终选择。上轮读到的国联13%是**公司保证金**；10/09东海12%板幅是过去时点，不自动延用；细则静态±4%也不是当期证明。不能选最低比例凑过门。

以参考Entry=3338、SL=3139、计划成本40元/手为例，以下是**压力敏感性假设，非当前涨跌停报价**。以10/09 settle=3321为起点，不利压力价向下取整数，压力退出成本假设60元/手：

| 假设情景 | 压力退出价 | 压力损失/手 | gap_ratio | 若被核定为适用场景 |
|---|---:|---:|---:|---|
| 单次下跌7% | 3088 | 2560元 | 1.261 | 低于正常1.3复核线；不代表整体执行通过 |
| 单次下跌9% | 3022 | 3220元 | 1.586 | 超过1.3，须具体减额并核绝对压力承受额 |
| 再次出现12%扩板级别下跌 | 2922 | 4220元 | 2.079 | 超过1.8，不新开；减少手数不能解决单位比值 |
| 连续两次7%且首日无法退出 | 2872 | 4720元 | 2.325 | 事故情景；若适用于当前持仓退出条件，则不新开 |

本轮不把最轻情景冒充最终压力，也不把未核适用性的极端情景直接写成已发生或永久禁令。公开参数与退出可行性补齐后按有依据的适用场景裁决；多情景适用时取最不利者。所有金额均须按实际Entry和成本重算。

10/08已发生的扩板事件若作为T，其T±1窗止于10/09，不能无限冻结到下一周；规则实际恢复仍须另核，新的直接相关事件会重新判定。WASDE不自动冻结MA。

单笔/组合B=真实权益3.5%；相关持续事件风险或实际候选高波动时组合再封顶min(B,5000)。strategy=0.7、已知非致命分歧对应market_risk=0.5；exchange_buffer和risk_regime尚未核定，不默认normal。最终取风险、保证金、限仓、执行/压力与MA跨周末容量最小值；无有效对冲跨周末单仓计划风险≤B×30%。账户仍未知。

## 4. 其他路线与接续

M/RB/SR/CF的10/09价格仍未触发；RB/SR价差反转双向false；MA价差仍缺经济锚。它们不因MA重评变成通过或失败。本轮最多深入MA现有计划和RB条件观察两条；M保留筛选及产业待核记录，不把旧两份观察再加MA凑成三条当前计划。

已有持仓未核，不能给出已经加仓/减仓的结论。下一步是在10/12可交易时段前补当期规则、合约日期并检查实际报价；若G1–G4齐全才请求真实账户核G5/G6。当前没有创建监控任务。算法、两日有效期、0.5ATR、2ATR和核心风险阈值均未变；本轮修改的是错误的版本启动门，不是为甲醇降低价格或风险标准。

## 机器审计

价格日仍为10/09，评估/登记时间见JSON；plan.entry为研究报价。风险计算结果不等于执行许可，final_lots仍null。原r2不覆写，下面保留8条路线的一致状态，并用单独证据更正旧版本时间裁决。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-11",
  "research_mode": "public_data",
  "assessment_scope": "proposed_framework_reassessment",
  "generator": "codex",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "6cc3b03+working_tree:codex/futures-current-signal-reassessment",
    "canonical_sha256": "1b5a7c54df401b5fb5a0f10f28fe7059a1b9138a8d7e59dfce6d5093e0b3c65a"
  },
  "snapshot": {
    "market_trade_date": "2026-10-09",
    "market_captured_at": "2026-10-11T12:03:11.615481+08:00",
    "source_artifacts": [
      "research/futures/snapshots/2026-10-11-data-snapshot.txt",
      "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-market-inputs-codex.json",
      "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-screening-codex.json",
      "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-supplied-snapshot-codex.txt"
    ],
    "account": {
      "actual_position_status": "unknown",
      "verified_at": null,
      "evidence": null,
      "equity": null,
      "open_positions": null,
      "pending_orders": null,
      "existing_risk": null,
      "reserved_order_risk": null,
      "margin_available": null,
      "configured_equity": null
    }
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "5个品种T真实合约价格筛选",
      "3条同品种V结算价反转筛选",
      "沿用M/RB产业研究；当前MA计划与RB条件观察",
      "MA/SR/CF最小产业背景",
      "MA现有信号当前重评及未来价格/时间/压力计划"
    ],
    "missing_scope": [
      "MA基础表最后日与源快照期限计数核对",
      "MA当日公开动态参数/报价及压力场景适用性",
      "本期M国内传导",
      "V经济锚",
      "真实账户与最终容量"
    ],
    "research_only_scope": [
      "MA/RB/SR V经济锚及5–20日机制"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "PRICE-MA2701",
      "metric": "真实合约价格机械筛选（生效前行情，不是历史交易建议）",
      "value": {
        "contract": "MA2701",
        "market_trade_date": "20261009",
        "close": 3338.0,
        "signal_1009": "triggered",
        "direction_1009": "long",
        "channel_high_1009": 3200.0,
        "channel_low_1009": 2817.0,
        "atr20_1009": 99.16455680366184,
        "volatility_ratio": 1.0845672171896683,
        "high_volatility": false,
        "channel_high_for_1012": 3402.0,
        "channel_low_for_1012": 2821.0,
        "fetched_at": "2026-10-11T12:03:09.552791+08:00",
        "recomputed_match": true
      },
      "unit": "价格/ATR:元每吨;波动比:倍",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:09.552791+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-screening-codex.json",
      "original_source": "Tushare Pro既有fut_daily输入；本轮当前helper重算",
      "price_basis": "close及high/low；不使用settle",
      "comparison_basis": "当前close对排除当日的前20日极值；固定61根ATR",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "LIQ-MA2701",
      "metric": "近20完整日日均成交量及真实日历期限",
      "value": {
        "average_volume": 724224.95,
        "remaining_trading_days": 67
      },
      "unit": "手;交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:09.552791+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-supplied-snapshot-codex.txt",
      "original_source": "已有v1.18完成快照，Tushare Pro单合约及交易日历",
      "price_basis": "not_price",
      "comparison_basis": "每腿日均>=10000手、当前剩余>=20交易日",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-RB2701",
      "metric": "真实合约价格机械筛选（生效前行情，不是历史交易建议）",
      "value": {
        "contract": "RB2701",
        "market_trade_date": "20261009",
        "close": 3080.0,
        "signal_1009": "not_triggered",
        "direction_1009": null,
        "channel_high_1009": 3183.0,
        "channel_low_1009": 3060.0,
        "atr20_1009": 30.243745503269064,
        "volatility_ratio": 1.0727455184709542,
        "high_volatility": false,
        "channel_high_for_1012": 3183.0,
        "channel_low_for_1012": 3060.0,
        "fetched_at": "2026-10-11T12:03:10.073328+08:00",
        "recomputed_match": true
      },
      "unit": "价格/ATR:元每吨;波动比:倍",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:10.073328+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-screening-codex.json",
      "original_source": "Tushare Pro既有fut_daily输入；本轮当前helper重算",
      "price_basis": "close及high/low；不使用settle",
      "comparison_basis": "当前close对排除当日的前20日极值；固定61根ATR",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "LIQ-RB2701",
      "metric": "近20完整日日均成交量及真实日历期限",
      "value": {
        "average_volume": 706042.25,
        "remaining_trading_days": 68
      },
      "unit": "手;交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:10.073328+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-supplied-snapshot-codex.txt",
      "original_source": "已有v1.18完成快照，Tushare Pro单合约及交易日历",
      "price_basis": "not_price",
      "comparison_basis": "每腿日均>=10000手、当前剩余>=20交易日",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-M2701",
      "metric": "真实合约价格机械筛选（生效前行情，不是历史交易建议）",
      "value": {
        "contract": "M2701",
        "market_trade_date": "20261009",
        "close": 3402.0,
        "signal_1009": "not_triggered",
        "direction_1009": null,
        "channel_high_1009": 3502.0,
        "channel_low_1009": 3327.0,
        "atr20_1009": 49.17175218276189,
        "volatility_ratio": 1.2005507089872431,
        "high_volatility": false,
        "channel_high_for_1012": 3502.0,
        "channel_low_for_1012": 3327.0,
        "fetched_at": "2026-10-11T12:03:10.577333+08:00",
        "recomputed_match": true
      },
      "unit": "价格/ATR:元每吨;波动比:倍",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:10.577333+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-screening-codex.json",
      "original_source": "Tushare Pro既有fut_daily输入；本轮当前helper重算",
      "price_basis": "close及high/low；不使用settle",
      "comparison_basis": "当前close对排除当日的前20日极值；固定61根ATR",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "LIQ-M2701",
      "metric": "近20完整日日均成交量及真实日历期限",
      "value": {
        "average_volume": 1381405.65,
        "remaining_trading_days": 68
      },
      "unit": "手;交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:10.577333+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-supplied-snapshot-codex.txt",
      "original_source": "已有v1.18完成快照，Tushare Pro单合约及交易日历",
      "price_basis": "not_price",
      "comparison_basis": "每腿日均>=10000手、当前剩余>=20交易日",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-SR2701",
      "metric": "真实合约价格机械筛选（生效前行情，不是历史交易建议）",
      "value": {
        "contract": "SR2701",
        "market_trade_date": "20261009",
        "close": 5491.0,
        "signal_1009": "not_triggered",
        "direction_1009": null,
        "channel_high_1009": 5510.0,
        "channel_low_1009": 5305.0,
        "atr20_1009": 53.88747990017016,
        "volatility_ratio": 1.1990705069685412,
        "high_volatility": false,
        "channel_high_for_1012": 5510.0,
        "channel_low_for_1012": 5305.0,
        "fetched_at": "2026-10-11T12:03:11.080891+08:00",
        "recomputed_match": true
      },
      "unit": "价格/ATR:元每吨;波动比:倍",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:11.080891+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-screening-codex.json",
      "original_source": "Tushare Pro既有fut_daily输入；本轮当前helper重算",
      "price_basis": "close及high/low；不使用settle",
      "comparison_basis": "当前close对排除当日的前20日极值；固定61根ATR",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "LIQ-SR2701",
      "metric": "近20完整日日均成交量及真实日历期限",
      "value": {
        "average_volume": 418491.6,
        "remaining_trading_days": 67
      },
      "unit": "手;交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:11.080891+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-supplied-snapshot-codex.txt",
      "original_source": "已有v1.18完成快照，Tushare Pro单合约及交易日历",
      "price_basis": "not_price",
      "comparison_basis": "每腿日均>=10000手、当前剩余>=20交易日",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-CF2701",
      "metric": "真实合约价格机械筛选（生效前行情，不是历史交易建议）",
      "value": {
        "contract": "CF2701",
        "market_trade_date": "20261009",
        "close": 15790.0,
        "signal_1009": "not_triggered",
        "direction_1009": null,
        "channel_high_1009": 16955.0,
        "channel_low_1009": 15490.0,
        "atr20_1009": 215.75232860511124,
        "volatility_ratio": 1.0593901273988675,
        "high_volatility": false,
        "channel_high_for_1012": 16900.0,
        "channel_low_for_1012": 15490.0,
        "fetched_at": "2026-10-11T12:03:11.615481+08:00",
        "recomputed_match": true
      },
      "unit": "价格/ATR:元每吨;波动比:倍",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:11.615481+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-screening-codex.json",
      "original_source": "Tushare Pro既有fut_daily输入；本轮当前helper重算",
      "price_basis": "close及high/low；不使用settle",
      "comparison_basis": "当前close对排除当日的前20日极值；固定61根ATR",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "LIQ-CF2701",
      "metric": "近20完整日日均成交量及真实日历期限",
      "value": {
        "average_volume": 331489.95,
        "remaining_trading_days": 67
      },
      "unit": "手;交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11T12:03:11.615481+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-supplied-snapshot-codex.txt",
      "original_source": "已有v1.18完成快照，Tushare Pro单合约及交易日历",
      "price_basis": "not_price",
      "comparison_basis": "每腿日均>=10000手、当前剩余>=20交易日",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "SPREAD-MA2701-MA2705",
      "metric": "同对结算价差及严格反转子条件输入",
      "value": [
        [
          "20260928",
          277.0
        ],
        [
          "20260929",
          284.0
        ],
        [
          "20260930",
          279.0
        ],
        [
          "20261008",
          328.0
        ],
        [
          "20261009",
          416.0
        ]
      ],
      "unit": "元/吨",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-market-inputs-codex.json",
      "original_source": "Tushare Pro既有同日真实合约结算价；本轮近减远验算",
      "price_basis": "near_settle-far_settle",
      "comparison_basis": "short S(t)<前2日min；long S(t)>前2日max；等号不触发",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "SPREAD-RB2701-RB2703",
      "metric": "同对结算价差及严格反转子条件输入",
      "value": [
        [
          "20260928",
          -4.0
        ],
        [
          "20260929",
          -2.0
        ],
        [
          "20260930",
          2.0
        ],
        [
          "20261008",
          4.0
        ],
        [
          "20261009",
          2.0
        ]
      ],
      "unit": "元/吨",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-market-inputs-codex.json",
      "original_source": "Tushare Pro既有同日真实合约结算价；本轮近减远验算",
      "price_basis": "near_settle-far_settle",
      "comparison_basis": "short S(t)<前2日min；long S(t)>前2日max；等号不触发",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "SPREAD-SR2701-SR2705",
      "metric": "同对结算价差及严格反转子条件输入",
      "value": [
        [
          "20260928",
          -72.0
        ],
        [
          "20260929",
          -76.0
        ],
        [
          "20260930",
          -78.0
        ],
        [
          "20261008",
          -75.0
        ],
        [
          "20261009",
          -77.0
        ]
      ],
      "unit": "元/吨",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-11",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-market-inputs-codex.json",
      "original_source": "Tushare Pro既有同日真实合约结算价；本轮近减远验算",
      "price_basis": "near_settle-far_settle",
      "comparison_basis": "short S(t)<前2日min；long S(t)>前2日max；等号不触发",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "FRAMEWORK",
      "metric": "被撤回的额外版本启动门；旧规则历史留存，非市场原始数据错误",
      "value": {
        "version": "v3.0",
        "effective_date": "2026-10-11",
        "revision": "6cc3b03"
      },
      "unit": "版本/日期",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r3/2026-10-11-framework-before-current-reassessment.md",
      "original_source": "仓库canonical",
      "price_basis": "not_price",
      "comparison_basis": "首次生效后的完整行情日方可登记前瞻信号",
      "role": "required_model",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "M-USDA",
      "metric": "2026/27美豆供应十月预测",
      "value": {
        "yield": 53.1,
        "production": 4562,
        "ending_stocks": 315,
        "crush": 2780
      },
      "unit": "单产蒲/英亩；其他百万蒲",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-09T12:00:00-04:00",
      "source_url_or_file": "https://www.usda.gov/oce/commodity/wasde/wasde1026.pdf",
      "original_source": "USDA/WAOB",
      "price_basis": "not_price",
      "comparison_basis": "9月52.8/4535/310/2780；年度预测，不是国内周度实际",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-CRUSH",
      "metric": "国内实际大豆压榨及空头反证",
      "value": {
        "crush": 185.69,
        "weekly_change": -66.26,
        "utilization_pct": 50.4
      },
      "unit": "万吨;百分比",
      "observation_date": "2026-10-02",
      "published_at": "2026-10-08T20:25:00+08:00",
      "source_url_or_file": "https://qhweb.eastmoney.com/news/202610083889840147.html",
      "original_source": "Mysteel全国动态全样本；东方财富署名转引正文",
      "price_basis": "not_price",
      "comparison_basis": "9/26-10/2实际对前周；125.36为下一周预估不采用",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-EVENT",
      "metric": "WASDE实际发布时间及国内首次响应映射",
      "value": {
        "published_beijing": "2026-10-10T00:00:00+08:00",
        "domestic_first_response": "2026-10-12T09:00:00+08:00",
        "domestic_T": "2026-10-12",
        "window_trading_dates": [
          "2026-10-09",
          "2026-10-12",
          "2026-10-13"
        ],
        "first_postwindow_trading_date": "2026-10-14"
      },
      "unit": "时间/交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-09T12:00:00-04:00",
      "source_url_or_file": "https://www.usda.gov/about-usda/general-information/staff-offices/office-chief-economist/commodity-markets/wasde-report",
      "original_source": "USDA官方日程；国内映射为本研究推算",
      "price_basis": "not_price",
      "comparison_basis": "美东夏令时UTC-4；配合M-HOURS及真实交易日历",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-HOURS",
      "metric": "M交易时段",
      "value": {
        "night": [
          "21:00",
          "23:00"
        ],
        "day_start": "09:00"
      },
      "unit": "北京时间",
      "observation_date": "2026-02-25",
      "published_at": "2026-02-25",
      "source_url_or_file": "https://www.ddqh.com/bocupload/2026/02/26/1772101558264ywp7n.pdf",
      "original_source": "东鼎期货正式时间表；文内更新日2/25，路径2/26；DCE原时段公告未读取",
      "price_basis": "not_price",
      "comparison_basis": "not_applicable",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "RB-SUPPLY",
      "metric": "螺纹假期周同口径产销存",
      "value": {
        "production": 170.27,
        "factory_inventory": 169.59,
        "social_inventory": 427.25,
        "inventory_weekly_change": 30.69,
        "apparent_consumption": 139.58,
        "production_yoy_change": -33.13,
        "total_inventory_yoy_change": -62.81
      },
      "unit": "万吨",
      "observation_date": "2026-10-07",
      "published_at": "2026-10-09T10:53:00+08:00",
      "source_url_or_file": "https://finance.sina.cn/futuremarket/qsyw/2026-10-09/detail-iniuquqi4053692.d.html?cid=76578&node_id=76578&oid=3815550373158897&vt=4&wm=4007",
      "original_source": "Mysteel调查；光大日报新浪完整转引，原样本定义未核",
      "price_basis": "not_price",
      "comparison_basis": "同篇周环比与同比；表需为产量减库存增量，不是终端成交",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-WARRANT",
      "metric": "甲醇注册仓单",
      "value": {
        "tax_paid_receipts": 5316,
        "daily_change": -182,
        "bonded_receipts": 0
      },
      "unit": "张（10吨/张）",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-09T15:48:00+08:00",
      "source_url_or_file": "https://www.99qh.com/article/%E9%86%87%E7%B1%BB-1101000",
      "original_source": "郑商所日报；99期货全文转录",
      "price_basis": "not_price",
      "comparison_basis": "当日对前日；只代表注册供给，注销原因未知",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-PRODUCTION",
      "metric": "甲醇国产供应恢复反证",
      "value": {
        "production": 208.19,
        "weekly_change": 6.02,
        "utilization_pct": 92.15
      },
      "unit": "万吨;百分比",
      "observation_date": "2026-10-08",
      "published_at": "2026-10-08",
      "source_url_or_file": "https://goodsfu.10jqka.com.cn/20261008/c680471840.shtml",
      "original_source": "隆众周度数据；同花顺正文完整转引，原表访问失败",
      "price_basis": "not_price",
      "comparison_basis": "同口径周环比；不等于港口到货",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-PORT-DATE",
      "metric": "甲醇港库原表日期冲突仍未完全消除",
      "value": {
        "reported_stock": 30.51,
        "reported_change": -8.84,
        "possible_observation_dates": [
          "2026-10-08",
          "2026-10-09"
        ]
      },
      "unit": "万吨",
      "observation_date": "2026-10-08",
      "published_at": "2026-10-09",
      "source_url_or_file": "https://finance.sina.cn/2026-10-09/detail-iniurruc2835532.d.html",
      "original_source": "隆众；同花顺/盛达同源转引日期不一致，原表未读",
      "price_basis": "not_price",
      "comparison_basis": "只作限制说明，不用于门的pass/fail",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "SR-INVENTORY",
      "metric": "广西榨季结转库存及销量",
      "value": {
        "inventory": 83.34,
        "inventory_yoy_change": 39.13,
        "sales_yoy_change": 84.11
      },
      "unit": "万吨",
      "observation_date": "2026-09-30",
      "published_at": "2026-10-10",
      "source_url_or_file": "https://www.hisugar.com/home/articleContent?id=2026101011322520459072",
      "original_source": "广西糖业协会；泛糖完整转载",
      "price_basis": "not_price",
      "comparison_basis": "广西2025/26榨季累计同比，非全国周频",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "CF-DEMAND",
      "metric": "棉花协会9月需求/上市调查",
      "value": "新棉提前约一周上市；订单增量有限；部分高支纱/新疆订单较好",
      "unit": "定性调查",
      "observation_date": "2026-09-30",
      "published_at": "2026-10-10",
      "source_url_or_file": "https://www.sinotex.cn/News/View.asp?id=267144",
      "original_source": "中国棉花协会；锦桥转载正文",
      "price_basis": "not_price",
      "comparison_basis": "18省100家棉纺企业月度监测，非本周期货方向信号",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "DCE-HOLIDAY",
      "metric": "M假期调整与条件恢复规则",
      "value": {
        "holiday_limit_pct": 8,
        "holiday_margin_pct": 10,
        "normal_limit_pct": 6,
        "normal_exchange_margin_pct": 7
      },
      "unit": "百分比",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://www.citicsf.com/e-futures/content/000204/825671",
      "original_source": "大商所通知；中信期货全文转发",
      "price_basis": "not_price",
      "comparison_basis": "恢复须满足最大持仓合约首个非单边市后结算，实际状态另核",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "RB-RULE",
      "metric": "RB规格与仓单有效期",
      "value": {
        "multiplier": 10,
        "tick": 1,
        "warehouse_valid_days": 90,
        "factory_receipt_days": 180
      },
      "unit": "吨/手;元/吨;自然日",
      "observation_date": "2026-01-01",
      "published_at": "2026-01-01",
      "source_url_or_file": "https://www.shfe.com.cn/regulation/exchangerules/productrules/202512/t20251231_829962.html",
      "original_source": "上海期货交易所官方细则",
      "price_basis": "not_price",
      "comparison_basis": "仓库货物生产后45日内入库；仓单类型不同不可套同一carry锚",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "GL-1012",
      "metric": "10/12公司保证金表的提前公告",
      "value": {
        "MA_pct": 13,
        "M_pct": 11,
        "RB_pct": 12,
        "CF_pct": 11,
        "SR_pct": 13
      },
      "unit": "公司投机保证金百分比",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-09",
      "source_url_or_file": "https://www.glqh.com/u/cms/www/202610/09162414y3jc.pdf",
      "original_source": "国联期货公司原始表；10/09发布适用于10/12的表",
      "price_basis": "not_price",
      "comparison_basis": "MA特殊2610/2611不套本次2701；非用户账户实收，非交易所最低",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "FRAMEWORK-CURRENT",
      "metric": "当前重评、原信号原期限、未来执行的澄清",
      "value": {
        "current_registration_allowed": true,
        "original_signal_date_retained": true,
        "validity_not_restarted": true,
        "V_anchor_must_predate_signal": true
      },
      "unit": "规则",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11",
      "source_url_or_file": "framework/futures_framework.md#r-v3-scope",
      "original_source": "用户10/11定向请求后本地canonical澄清",
      "price_basis": "not_price",
      "comparison_basis": "not_applicable",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-PORT-CURRENT",
      "metric": "本轮读正文的有限港口供应支持",
      "value": {
        "port_inventory": 30.51,
        "weekly_change": -8.84
      },
      "unit": "万吨",
      "observation_date": "2026-10-08",
      "published_at": "2026-10-08T15:15:07+08:00",
      "source_url_or_file": "https://goodsfu.10jqka.com.cn/20261008/c680471840.shtml",
      "original_source": "隆众；同花顺正文日内消息完整转引，原表访问限制保留",
      "price_basis": "not_price",
      "comparison_basis": "对9/30同口径读数；不是全国社会库存，其他转引日期分歧仍保留",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-RULE-DETAIL",
      "metric": "甲醇规则基准与仓单注销期限",
      "value": {
        "multiplier": 10,
        "tick": 1,
        "last_trading_day_rule": "交割月第10交易日",
        "natural_person_delivery_month_limit": 0,
        "ordinary_customer_limit": "单边OI<300000时30000，达到时OI×10%",
        "warehouse_cancellation": "5/11月第15交易日前；保税顺延5交易日"
      },
      "unit": "吨/手;元/吨;手;日期规则",
      "observation_date": "2024-02-06",
      "published_at": "2024-02-06",
      "source_url_or_file": "https://www.futureslaw.org.cn/czcepzxz/1436.htm",
      "original_source": "郑商所业务细则；期货和衍生品法律网完整转录",
      "price_basis": "not_price",
      "comparison_basis": "静态规格与限仓基准，不证明10/12临时调整已核",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-PLAN-CALC",
      "metric": "已验证的计划算术；费用输入为研究假设",
      "value": {
        "signal_date": "2026-10-09",
        "entry": 3338,
        "stop": 3139,
        "entry_range": [
          3289,
          3387
        ],
        "valid_until": "2026-10-13",
        "round_trip_fee_budget": 20,
        "slippage_budget": 20,
        "risk_unit_under_assumptions": 2030,
        "entry_1012_exit": "2026-11-06",
        "entry_1013_exit": "2026-11-09"
      },
      "unit": "元/吨;人民币每手;交易日",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11T18:14:54+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r3/2026-10-11-ma-plan-arithmetic-codex.json",
      "original_source": "scripts/futures_strategy.py validate-plan，既有冻结行情和显式研究预算",
      "price_basis": "close信号，未来Entry为研究报价",
      "comparison_basis": "not_applicable",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-EXPIRY-DIAG",
      "metric": "规则日历推算与源快照期限计数差异",
      "value": {
        "rule_calendar_inferred_last_day": "2027-01-15",
        "remaining_from_1011_left_closed_right_open": 68,
        "snapshot_remaining": 67,
        "original_delist_date_not_frozen": true
      },
      "unit": "交易日;日期",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11",
      "source_url_or_file": "research/futures/weekly/2026-10-11/evidence/v3-r3/ma-current-rules-codex.md",
      "original_source": "已读产品规则、冻结日历和已有快照比较；尚未裁决差异",
      "price_basis": "not_price",
      "comparison_basis": "只证明差异存在，不用于G1 pass",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    }
  ],
  "candidates": [
    {
      "candidate_id": "20261009-M2701-trend-short-v3",
      "opportunity_id": "20261011-observe-M2701-trend-short-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "价格输入齐全且未触发；若出现空头信号，本期国内供应传导仍需一项有效证据",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-M2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-M2701"
          ],
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "first_blocker": "G2",
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-M2701",
        "FRAMEWORK-CURRENT",
        "PRICE-M2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
    {
      "candidate_id": "20261009-RB2701-trend-short-v3",
      "opportunity_id": "20261011-observe-RB2701-trend-short-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "本次价格与最低背景可读；无信号早停不表示完整执行输入齐全",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-RB2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-RB2701"
          ],
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "first_blocker": "G2",
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-RB2701",
        "FRAMEWORK-CURRENT",
        "PRICE-RB2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "observation_plan": {
        "registered_at": "2026-10-11",
        "signal_date": null,
        "threshold_trade_date": "2026-10-12",
        "close_strictly_below": 3060,
        "minimum_tick_price_at_or_below": 3059,
        "economic_condition": "最新适用螺纹累库/现货弱的因果解释仍成立；保留假期残差、低同比供应与库存反证",
        "refresh_required": [
          "逐日滚动20日通道",
          "固定61根ATR",
          "最新适用产业支持和反证",
          "公开规则/报价/费用/压力场景",
          "实际交易日入场有效期",
          "G1–G4成案后实际账户及size-v3"
        ],
        "conditional_valid_entry_dates": [
          "2026-10-13",
          "2026-10-14"
        ],
        "conditional_event_eligible_dates": [
          "2026-10-13",
          "2026-10-14"
        ],
        "event_qualification": "只对10/12真实收盘新触发成立；入场前核新增直接相关事件；日期不是已经成立的计划",
        "targets": null,
        "entry": null,
        "stop": null,
        "latest_exit_date": null
      },
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
    {
      "candidate_id": "20261009-MA2701-trend-long-v3",
      "opportunity_id": "20261011-observe-MA2701-trend-long-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "long",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "价格和最低产业论证成立、数值计划已形成；合约日期口径与当前执行参数/报价尚待核",
      "signal": "triggered",
      "signal_evidence_refs": [
        "PRICE-MA2701",
        "FRAMEWORK-CURRENT"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "范围、规格和日均量已核；核基础表最后日与快照67/日历68计数差异，记录公开退出边界；账户专属更早限制后置G5",
          "evidence_refs": [
            "LIQ-MA2701",
            "MA-RULE-DETAIL",
            "MA-EXPIRY-DIAG"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "范围、规格和日均量已核；核基础表最后日与快照67/日历68计数差异，记录公开退出边界；账户专属更早限制后置G5",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "pass",
          "details": "10/09 close3338>prior20 high3200；原有效期仍有未来时段，港库去化提供有限产业支持；国产复产和仓单注销限制为反证，weak不掩盖执行缺项",
          "evidence_refs": [
            "PRICE-MA2701",
            "FRAMEWORK-CURRENT",
            "MA-PORT-CURRENT",
            "MA-PRODUCTION",
            "MA-WARRANT",
            "MA-RULE-DETAIL"
          ],
          "diagnostic_evidence_refs": [
            "FRAMEWORK"
          ]
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "pass",
          "details": "当前登记完整数值计划：3289–3387、参考3338/SL3139、10/13截止，10/12入场11/06最晚退出；费用20+滑点20为显式研究预算，实际成本及报价另核",
          "evidence_refs": [
            "MA-PLAN-CALC",
            "FRAMEWORK-CURRENT"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "核10/12实际板幅/交易所保证金/临时限仓及未来盘口，按有依据的适用压力场景取最不利；不挑最低敏感性情景强行过门",
          "evidence_refs": [
            "GL-1012",
            "MA-RULE-DETAIL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核10/12实际板幅/交易所保证金/临时限仓及未来盘口，按有依据的适用压力场景取最不利；不挑最低敏感性情景强行过门",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "研究成案后核当日权益、持仓/挂单、实收保证金、实际费用、限额和绝对压力承受金额",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "研究成案后核当日权益、持仓/挂单、实收保证金、实际费用、限额和绝对压力承受金额",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "用size-v3按同一真实计划取风险/保证金/限仓/执行/压力及适用MA周末容量最小值",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "用size-v3按同一真实计划取风险/保证金/限仓/执行/压力及适用MA周末容量最小值",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "G1",
        "G4",
        "G5",
        "G6"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "plan": {
        "entry": 3338,
        "entry_date": "2026-10-12",
        "stop": 3139,
        "targets": null,
        "entry_range": [
          3289,
          3387
        ],
        "signal_date": "2026-10-09",
        "valid_until": "2026-10-13",
        "latest_exit_date": "2026-11-06",
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "evaluated_at": "2026-10-11T18:14:54+08:00",
        "registered_at": "2026-10-11T18:14:54+08:00",
        "earliest_future_execution_at": "2026-10-12T09:00:00+08:00",
        "entry_quote_status": "planned_not_observed_executable",
        "round_trip_fee_budget": 20,
        "round_trip_slippage_budget": 20,
        "cost_basis": "研究预算，非用户实收；实际费用/滑点变化后必须重算",
        "alternate_entry": {
          "entry_date": "2026-10-13",
          "latest_exit_date": "2026-11-09",
          "same_signal_valid_until": "2026-10-13"
        },
        "arithmetic_ref": "research/futures/weekly/2026-10-11/evidence/v3-r3/2026-10-11-ma-plan-arithmetic-codex.json"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "evidence_refs": [
        "LIQ-MA2701",
        "MA-RULE-DETAIL",
        "MA-EXPIRY-DIAG",
        "PRICE-MA2701",
        "FRAMEWORK-CURRENT",
        "MA-PORT-CURRENT",
        "MA-PRODUCTION",
        "MA-WARRANT",
        "MA-PLAN-CALC",
        "GL-1012"
      ],
      "price_screening_date": "2026-10-09",
      "historical_price_screen": "triggered_long_reassessed_now_for_future_execution",
      "evaluated_at": "2026-10-11T18:14:54+08:00",
      "registered_at": "2026-10-11T18:14:54+08:00",
      "risk_factors": {
        "strategy": 0.7,
        "market_risk": 0.5,
        "exchange_buffer": null,
        "market_risk_reason": "非致命产业分歧，只乘一次"
      }
    },
    {
      "candidate_id": "20261009-SR2701-trend-unknown-v3",
      "opportunity_id": "20261011-observe-SR2701-trend-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "本次价格与最低背景可读；无信号早停不表示完整执行输入齐全",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-SR2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-SR2701"
          ],
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "first_blocker": "G2",
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-SR2701",
        "FRAMEWORK-CURRENT",
        "PRICE-SR2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
    {
      "candidate_id": "20261009-CF2701-trend-unknown-v3",
      "opportunity_id": "20261011-observe-CF2701-trend-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "CF2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "本次价格与最低背景可读；无信号早停不表示完整执行输入齐全",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-CF2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-CF2701"
          ],
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "first_blocker": "G2",
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-CF2701",
        "FRAMEWORK-CURRENT",
        "PRICE-CF2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
    {
      "candidate_id": "20261009-MA2701-MA2705-economic_reversion-unknown-v3",
      "opportunity_id": "20261011-observe-MA2701-MA2705-economic_reversion-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "未取得可复算经济锚、月份匹配输入和5–20日收敛机制；不将库存数量或历史分位转换为锚",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "补MA2705近20日成交量及两腿期限；有结算价不证明远腿流动性",
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "补MA2705近20日成交量及两腿期限；有结算价不证明远腿流动性",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "SPREAD-MA2701-MA2705",
            "FRAMEWORK-CURRENT"
          ],
          "details": "价格反转子条件已知，但信号前冻结的独立经济锚和5–20日收敛机制缺失；禁止按旧价差事后造锚",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "先冻结独立经济锚与机制，再等待适用的新价格确认；不事后选择旧信号",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "经济锚成立后冻结1:1入场区间、近侧锚目标、失效止损、期限及整个区间净R>=2.5",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "经济锚成立后冻结1:1入场区间、近侧锚目标、失效止损、期限及整个区间净R>=2.5",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "GL-1012"
          ],
          "details": "核同一时刻两腿报价、至少4tick滑点与费用、裸腿事故预案及规则/事件/压力场景",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核同一时刻两腿报价、至少4tick滑点与费用、裸腿事故预案及规则/事件/压力场景",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "G1–G4成案后核真实账户、经纪商实收、挂单和资金/限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "G1–G4成案后核真实账户、经纪商实收、挂单和资金/限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户齐全后运行size-v3并取所有适用硬容量最小值",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户齐全后运行size-v3并取所有适用硬容量最小值",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "leg_ratio": [
          1,
          1
        ],
        "anchor_band": null,
        "economic_anchor_basis": null,
        "convergence_mechanism": null,
        "invalidation_basis": null,
        "net_R": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "evidence_refs": [
        "SPREAD-MA2701-MA2705",
        "FRAMEWORK-CURRENT",
        "GL-1012"
      ]
    },
    {
      "candidate_id": "20261009-RB2701-RB2703-economic_reversion-unknown-v3",
      "opportunity_id": "20261011-observe-RB2701-RB2703-economic_reversion-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "未取得可复算经济锚、月份匹配输入和5–20日收敛机制；不将库存数量或历史分位转换为锚",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "SPREAD-RB2701-RB2703"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "SPREAD-RB2701-RB2703"
          ],
          "details": "同对三日结算差的多、空严格反转子条件均false；不依赖未知锚即可排除本次触发"
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "first_blocker": "G2",
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "leg_ratio": [
          1,
          1
        ],
        "anchor_band": null,
        "economic_anchor_basis": null,
        "convergence_mechanism": null,
        "invalidation_basis": null,
        "net_R": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "SPREAD-RB2701-RB2703"
      ],
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "按canonical先筛价格；G1远腿流动性未知，未标pass；G2经济子条件也未完成"
    },
    {
      "candidate_id": "20261009-SR2701-SR2705-economic_reversion-unknown-v3",
      "opportunity_id": "20261011-observe-SR2701-SR2705-economic_reversion-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "未取得可复算经济锚、月份匹配输入和5–20日收敛机制；不将库存数量或历史分位转换为锚",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "SPREAD-SR2701-SR2705"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "SPREAD-SR2701-SR2705"
          ],
          "details": "同对三日结算差的多、空严格反转子条件均false；不依赖未知锚即可排除本次触发"
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "first_blocker": "G2",
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "leg_ratio": [
          1,
          1
        ],
        "anchor_band": null,
        "economic_anchor_basis": null,
        "convergence_mechanism": null,
        "invalidation_basis": null,
        "net_R": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "SPREAD-SR2701-SR2705"
      ],
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "按canonical先筛价格；G1远腿流动性未知，未标pass；G2经济子条件也未完成"
    }
  ],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "FRAMEWORK",
      "reason": "撤回信号必须晚于版本生效的额外门；当前重评与历史回填不同，价格原始证据未变",
      "affected_checks": [
        {
          "candidate_id": "20261009-MA2701-trend-long-v3",
          "rule_id": "G2"
        }
      ],
      "recalculation": "completed"
    }
  ],
  "shadow_plans": [],
  "performance_status": "not_automated",
  "unresolved_items": [
    {
      "kind": "acquisition",
      "owner": "research",
      "scope": "M_domestic_transmission",
      "next_action": "取得一条方向相关的国内当前供应/库存/提货/基差链，不要求全链齐备",
      "due_at": "before_execution"
    },
    {
      "kind": "acquisition",
      "owner": "research",
      "scope": "public_execution",
      "next_action": "真正触发后核当日规则、报价、费用、事件和压力场景，区分公司与交易所参数",
      "due_at": "before_execution"
    },
    {
      "kind": "definition",
      "owner": "research",
      "scope": "V_economic_models",
      "next_action": "只有独立可复算锚、月份匹配、失效价和5–20日机制齐全才恢复模型；当前不凑锚",
      "due_at": "next_report"
    },
    {
      "kind": "account",
      "owner": "user",
      "scope": "account_and_capacity",
      "next_action": "仅在G1–G4成案后提供当日真实账户供容量核算",
      "due_at": "before_execution"
    },
    {
      "kind": "raw_data",
      "owner": "data_pipeline",
      "scope": "MA_contract_date",
      "next_action": "冻结MA2701基础表及交易日历，裁决剩余67/68口径；不从模糊旧字段推断精确最后日",
      "due_at": "before_execution"
    }
  ],
  "risk_context": {
    "regime": "unknown",
    "reason": "5个T历史HV比未触发高波动不证明账户实际持仓和持续相关事件均无风险；账户及完整候选未形成"
  },
  "evaluated_at": "2026-10-11T18:14:54+08:00",
  "registered_at": "2026-10-11T18:14:54+08:00",
  "supersedes": "MA版本时间裁决及当前计划选择替代r2；旧r2不覆盖，其他路线已核价格结论沿用"
}
```
