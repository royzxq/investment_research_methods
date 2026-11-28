# MA2701 存量计划定向审计 · 2026-10-12

北京时间 2026-10-12 收盘刷新。采用 origin/main 24e7285 的 v3.0；仅复核已登记 MA2701 多头研究计划。原机会 ID、10/09 信号、10/11 登记与 10/13 截止不变。10/11 的数值入场范围和参考止损是原条件计划，不代表今日可成交价、现有持仓或动态止损。

[存量检查与来源](../../refresh/2026-10-12/2026-10-12-stock-plan-check.md)记录新华财经今日收盘报道及长安期货分析的确切作用域。MTO 停车、现货转弱及主力 MA2611 下跌使原产业支持需要重评；报道不能替代 MA2701 日线或交易所参数。原 10/08 港口低库存仍是相反支持，故当前 G2 从旧 pass 改为 unknown，不声称已证伪，也不准把旧 pass 沿用为新入场。G1、G4、账户 G5/G6 仍缺项；实际持仓未知时仅有条件管理：若有持仓，先核真实成交、最新行情、收紧止损和事件退出；若未入场，先完成六门新核验。工具两次联网取数失败，五品种 T 无可用 10/12 信号，V 无合格锚。

本次只替代 MA2701 的当前经济适用性结论；旧 r3 对其他路线的 10/09 价格筛查保持历史。以下 JSON 为可校验定向审计，执行许可与最终手数均未评估。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-12",
  "research_mode": "public_data",
  "assessment_scope": "state_refresh_existing_plan",
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
      "research/futures/refresh/2026-10-12/2026-10-12-signal-refresh-r2.json",
      "research/futures/refresh/2026-10-12/2026-10-12-stock-plan-check.md",
      "research/futures/weekly/2026-10-11/2026-10-11-execution-audit-r3.md"
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
      "MA2701 existing plan economic counter-evidence and capture failure"
    ],
    "missing_scope": [
      "10/12 contract OHLC and actual calendar unavailable",
      "other products 10/12 price and economic evidence not reassessed"
    ],
    "research_only_scope": [
      "V anchors absent"
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
    },
    {
      "evidence_id": "MA-1012-CNFIN-CLOSE",
      "metric": "Main-contract methanol close and MTO demand shock, not MA2701 price",
      "value": "MA2611 3536 CNY/tonne, -7.41%; MTO shutdowns reported",
      "unit": "CNY/tonne and percent",
      "observation_date": "2026-10-12",
      "published_at": "2026-10-12",
      "source_url_or_file": "https://www.cnfin.com/yw-lb/detail/20261012/4479614_1.html",
      "original_source": "新华财经收盘日报，记者郭洲洋、左元；报道事实及所引市场观点",
      "price_basis": "MA2611 main contract only; not MA2701 OHLC",
      "comparison_basis": "Compared with prior trading day as reported; exact exchange MA2701 line unavailable",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-1012-ANALYST-SECONDARY",
      "metric": "Methanol spot weakness and MTO shutdown explanation, secondary analyst account",
      "value": "Long-analyzed demand negative feedback and spot decline; underlying Longzhong raw table not directly verified",
      "unit": "qualitative",
      "observation_date": "2026-10-12",
      "published_at": "2026-10-12",
      "source_url_or_file": "https://finance.sina.com.cn/money/future/fmnews/2026-10-12/doc-iniuyari7225751.shtml",
      "original_source": "长安期货张晨署名分析，经新浪转载；所引隆众原始表未直接读取",
      "price_basis": "Spot and MA2611 commentary; not MA2701",
      "comparison_basis": "Indicative counter-evidence only; needs primary same-basis validation",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    }
  ],
  "candidates": [
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
      "data_feasibility_reason": "10/12 Tushare trade_cal/fut_basic connection failure; MA2701 10/12 OHLC and settlement unavailable; independent demand counter-evidence requires fresh G2 review",
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
          "result": "unknown",
          "details": "10/09 price breakout remains historical fact. 10/12 MTO shutdowns, spot weakness and MA2611 selloff affect the independent economic case; MA2701 10/12 OHLC/basis and current same-basis demand evidence unavailable. No current entry judgement.",
          "evidence_refs": [
            "PRICE-MA2701",
            "MA-PORT-CURRENT",
            "MA-1012-CNFIN-CLOSE"
          ],
          "diagnostic_evidence_refs": [
            "MA-1012-ANALYST-SECONDARY"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify MA2701 complete 10/12 bars, basis, same-basis port/inland supply and MTO demand; re-evaluate the original long thesis without extending 10/13 expiry",
            "due_at": "before_execution"
          }
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
          "details": "10/12 direct sector event and sharp main-contract decline raise gap/exit risk. MA2701 current exchange parameters, own quotes, stop/exit and stress applicability remain unverified.",
          "evidence_refs": [
            "GL-1012",
            "MA-RULE-DETAIL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify MA2701 10/12/10/13 exchange notices, board/margin/limit, actual quote, event window and stress/exit path",
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
        "G2",
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
        "GL-1012",
        "MA-1012-CNFIN-CLOSE"
      ],
      "price_screening_date": "2026-10-09",
      "historical_price_screen": "triggered_long_reassessed_now_for_future_execution",
      "evaluated_at": "2026-10-12T19:39:25+08:00",
      "registered_at": "2026-10-11T18:14:54+08:00",
      "risk_factors": {
        "strategy": 0.7,
        "market_risk": 0.5,
        "exchange_buffer": null,
        "market_risk_reason": "非致命产业分歧，只乘一次"
      }
    }
  ],
  "evidence_corrections": [],
  "shadow_plans": [],
  "performance_status": "not_automated",
  "unresolved_items": [
    {
      "item": "Restore verified futures calendar and MA2701 10/12 source-identified OHLC/settlement; failed fetch is not no_signal",
      "owner": "data_pipeline",
      "due_at": "next_refresh"
    },
    {
      "item": "Reassess MTO shutdowns, spot/basis and port tightness against original MA2701 thesis; check event, exchange rules and original 10/13 window",
      "owner": "research",
      "due_at": "before_execution"
    },
    {
      "item": "Actual position, entry, stop, pending orders, account capacities and final lots remain unknown",
      "owner": "user",
      "due_at": "before_execution"
    }
  ],
  "risk_context": {
    "regime": "unknown",
    "reason": "5个T历史HV比未触发高波动不证明账户实际持仓和持续相关事件均无风险；账户及完整候选未形成"
  },
  "evaluated_at": "2026-10-12T19:39:25+08:00",
  "registered_at": "2026-10-12T19:39:25+08:00",
  "supersedes": "Only MA2701 current G2 economic pass from 10/11 audit is withdrawn pending reassessment; prior signal, ID, registered_at, valid_until and other routes stay historical."
}
```
