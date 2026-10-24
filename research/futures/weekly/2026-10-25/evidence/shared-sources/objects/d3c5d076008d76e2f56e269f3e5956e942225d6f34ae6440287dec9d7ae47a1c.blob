# 期货执行审计 · 2026-10-18

generator=codex；public_data；assessment_scope=current_framework；方法v3.0，实际origin/main基线 `22b1cf1ac21df07b3434aca1fbd41dde67635f47`；行情10/16、真实取数10/18。本期按原方法逐项复核，不继承ready或账户。结构校验结果见验证记录。

| 对象 | 信号与当前处置 | 研究状态与缺口 |
|---|---|---|
| MA原机会 | 保留10/09信号、10/11 18:14:54登记、10/13截止；入场已过期 | incomplete；G3 fail，G1/G2/G4及账户unknown |
| M原机会 | 保留10/15信号、10/15 19:30:56登记、10/19截止；价格偏离取消原入场用途 | incomplete；G2当前弱证据可解释，G3 fail，执行/账户未齐 |
| RB/MA/SR/CF本期T | 10/16价格均未突破 | no_signal；后续门未评估 |
| MA/RB/SR V | 有序对、两腿身份与最近结算核验；无合格经济锚 | incomplete / research_only；不是no_signal |

## 计划与原时钟

M原信号日close3316、prior20 low3327、ATR20=49.5023300954。固定helper给原允许区间3292–3326；以3310作诊断报价，SL3410、预算手续费10+滑点20、每手风险1030元，20日退出11/13，targets=null。**这份算术是取消原因的诊断，未作为当前入场计划登记**：10/16收3281已超出原允许区间，不等待回价重启。10/16机械再次下破的ATR/截止由工具照实保留；本期把它视为同一连续空头观察，不自动新建ID或延至10/20。若以后重新研究独立新信号，须单独交代机会身份和来源，不修改原记录。

该处理是本期机会身份裁决，未增加“连续突破一律禁入”的方法规则。M10/15登记冲突来自首稿缺字段、r2显式补入实际时间；本期采用有来源的r2时间，无向后延长。

RB价格仍在通道内。本期完成同口径产销存与现货研究，未触发条件下不强造SL/未来signal_date。没有两份当前完整新计划；已深入M并完成RB条件研究。V三条锚维护见[正式锚研究记录](../../anchors/2026-10-18/2026-10-18-anchors.json)，不设配额。

## 已持仓的条件管理

共享中只有MA数字旧计划、M研究候选；未有已核真实持仓，账户未知。所有10/11无信号观察已在本期五品种与V研究中复核。不能把研究候选自动当持仓，也不能把窗口取消当平仓。

MA参考3338入场/3139初始SL；10/16最低3146，日线未穿该参考SL。原允许Entry不同会有不同SL，实际有效止损可更高；某些实际Entry对应的SL可能已被本周价格触及。日线不能判入场先后或真实成交，故不报统一止损结果。最近10完整日低点低于参考初始SL，未据此放宽止损。若确有持仓，先按真实成交和只收紧的有效SL核触发，触发则按实际可成交退出；经济逻辑被证伪或压力不能承受须减仓/退出，不等待原入场截止。原时间退出10/12入场11/06、10/13入场11/09保留，更早合约/事件边界优先；跨周末继续受原MA金额上限约束。

M若实际已持有，按真实成交价与10/15信号ATR确定有效SL，只收紧，最长20交易日及更早事件/逻辑边界取严。无成交史不以3310假定建仓，不报告收益。对旧MA与M均复核了公告、国内需求/供给反证、停止入场、条件止损/时间退出、事件窗和期限；原料及完整来源见[来源目录](evidence/shared-sources/catalog.json)、[本期来源摘记](evidence/source-notes.md)。

## 下一次触发与责任

研究方：核MA日期冲突、当前交易所临时公告/报价与适用压力；补同口径MA港库/MTO；后续M/RB新日线与产业事实、V交割和资金成本。账户方只需在真实方案成案/持仓核验时提供当日权益、持仓挂单、成交/止损和实收参数；final_lots一直为null。当前没有可据此下达的交易许可。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-18",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "22b1cf1ac21df07b3434aca1fbd41dde67635f47",
    "canonical_sha256": "ffa7c08762af97700064854d5cf4c9480ece70c65c0ba54d6b272d75cbd01458"
  },
  "snapshot": {
    "market_trade_date": "2026-10-16",
    "market_captured_at": "2026-10-18T08:49:13.866894+08:00",
    "source_artifacts": [
      "research/futures/refresh/2026-10-18/2026-10-18-signal-refresh.json",
      "research/futures/refresh/2026-10-18/evidence/2026-10-18-signal-refresh/market-inputs.json",
      "research/futures/weekly/2026-10-18/evidence/shared-sources/catalog.json",
      "research/futures/weekly/2026-10-18/evidence/continuity-reconciliation.json",
      "research/futures/weekly/2026-10-18/evidence/source-notes.md",
      "research/futures/weekly/2026-10-18/evidence/contract-and-volume-api.json",
      "research/futures/weekly/2026-10-18/evidence/v-ordered-pair-checks.json",
      "research/futures/anchors/2026-10-18/2026-10-18-anchors.json",
      "research/futures/refresh/2026-10-18/2026-10-18-signal-refresh-r2.json"
    ],
    "account": {
      "verified_at": null,
      "evidence": null,
      "equity": null,
      "open_positions": null,
      "pending_orders": null,
      "existing_risk": null,
      "reserved_order_risk": null,
      "margin_available": null,
      "configured_equity": null,
      "actual_position_status": "unknown"
    }
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "all known registered MA/M opportunities and historical observations",
      "five exact-contract T price screens through 10/16",
      "all three V ordered-pair sources and anchor research",
      "M/RB current domestic causal chain; MA/SR/CF drivers"
    ],
    "missing_scope": [
      "current actual holdings/fills/stops and orders",
      "exact MA contract-date conflict and full execution rule coverage",
      "current quotes, applied stress and full account capacities",
      "V numeric economic anchors and both-leg execution data"
    ],
    "research_only_scope": [
      "MA/RB/SR V numerical anchor models"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "PRICE-CF2701",
      "metric": "same-contract prior20/ATR fixed-helper screen",
      "value": {
        "rule_version": "v3.0",
        "strategy": "trend",
        "scope": "v3_market_inputs_only",
        "status": "valid",
        "signal": "not_triggered",
        "side": null,
        "missing_fields": [],
        "issues": [],
        "execution_permission": "not_evaluated",
        "methodology_validation": "forward_research_not_performance_validated",
        "contract": "CF2701",
        "price_basis": "close",
        "product": "CF",
        "market_trade_date": "20261016",
        "as_of_date": "20261016",
        "signal_close": 15850.0,
        "prior20_high": 16770.0,
        "prior20_low": 15490.0,
        "prior10_low": 15490.0,
        "prior10_high": 16130.0,
        "atr20": 204.27142174656345,
        "atr_initialization": "61_bars_first20_TR_mean_then_Wilder",
        "sample_start": "20260716",
        "targets": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "volatility_ratio": 1.0886909316897833,
        "volatility_status": "available",
        "high_volatility": false,
        "freshness": "fresh",
        "expected_market_trade_date": "20261016"
      },
      "unit": "CNY/tonne; ratio",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-18T08:49:13.866894+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-18/2026-10-18-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily returned identity verified",
      "price_basis": "close/high/low",
      "comparison_basis": "strictly exclude signal day; fixed 61 bars",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-M2701",
      "metric": "same-contract prior20/ATR fixed-helper screen",
      "value": {
        "rule_version": "v3.0",
        "strategy": "trend",
        "scope": "v3_market_inputs_only",
        "status": "valid",
        "signal": "triggered",
        "side": "short",
        "missing_fields": [],
        "issues": [],
        "execution_permission": "not_evaluated",
        "methodology_validation": "forward_research_not_performance_validated",
        "contract": "M2701",
        "price_basis": "close",
        "product": "M",
        "market_trade_date": "20261016",
        "as_of_date": "20261016",
        "signal_close": 3281.0,
        "prior20_high": 3502.0,
        "prior20_low": 3315.0,
        "prior10_low": 3315.0,
        "prior10_high": 3426.0,
        "atr20": 49.73139023573838,
        "atr_initialization": "61_bars_first20_TR_mean_then_Wilder",
        "sample_start": "20260716",
        "targets": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "volatility_ratio": 1.1886886635529748,
        "volatility_status": "available",
        "high_volatility": false,
        "freshness": "fresh",
        "expected_market_trade_date": "20261016",
        "signal_date": "2026-10-16",
        "valid_entry_dates": [
          "2026-10-19",
          "2026-10-20"
        ],
        "valid_until": "2026-10-20",
        "registered_at": null
      },
      "unit": "CNY/tonne; ratio",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-18T08:49:13.866894+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-18/2026-10-18-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily returned identity verified",
      "price_basis": "close/high/low",
      "comparison_basis": "strictly exclude signal day; fixed 61 bars",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-MA2701",
      "metric": "same-contract prior20/ATR fixed-helper screen",
      "value": {
        "rule_version": "v3.0",
        "strategy": "trend",
        "scope": "v3_market_inputs_only",
        "status": "valid",
        "signal": "not_triggered",
        "side": null,
        "missing_fields": [],
        "issues": [],
        "execution_permission": "not_evaluated",
        "methodology_validation": "forward_research_not_performance_validated",
        "contract": "MA2701",
        "price_basis": "close",
        "product": "MA",
        "market_trade_date": "20261016",
        "as_of_date": "20261016",
        "signal_close": 3192.0,
        "prior20_high": 3402.0,
        "prior20_low": 2821.0,
        "prior10_low": 2838.0,
        "prior10_high": 3402.0,
        "atr20": 103.33286502449582,
        "atr_initialization": "61_bars_first20_TR_mean_then_Wilder",
        "sample_start": "20260716",
        "targets": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "volatility_ratio": 1.1480271888206832,
        "volatility_status": "available",
        "high_volatility": false,
        "freshness": "fresh",
        "expected_market_trade_date": "20261016"
      },
      "unit": "CNY/tonne; ratio",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-18T08:49:13.866894+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-18/2026-10-18-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily returned identity verified",
      "price_basis": "close/high/low",
      "comparison_basis": "strictly exclude signal day; fixed 61 bars",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-RB2701",
      "metric": "same-contract prior20/ATR fixed-helper screen",
      "value": {
        "rule_version": "v3.0",
        "strategy": "trend",
        "scope": "v3_market_inputs_only",
        "status": "valid",
        "signal": "not_triggered",
        "side": null,
        "missing_fields": [],
        "issues": [],
        "execution_permission": "not_evaluated",
        "methodology_validation": "forward_research_not_performance_validated",
        "contract": "RB2701",
        "price_basis": "close",
        "product": "RB",
        "market_trade_date": "20261016",
        "as_of_date": "20261016",
        "signal_close": 3074.0,
        "prior20_high": 3167.0,
        "prior20_low": 3053.0,
        "prior10_low": 3053.0,
        "prior10_high": 3131.0,
        "atr20": 29.025345704918738,
        "atr_initialization": "61_bars_first20_TR_mean_then_Wilder",
        "sample_start": "20260716",
        "targets": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "volatility_ratio": 1.0263531122937424,
        "volatility_status": "available",
        "high_volatility": false,
        "freshness": "fresh",
        "expected_market_trade_date": "20261016"
      },
      "unit": "CNY/tonne; ratio",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-18T08:49:13.866894+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-18/2026-10-18-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily returned identity verified",
      "price_basis": "close/high/low",
      "comparison_basis": "strictly exclude signal day; fixed 61 bars",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-SR2701",
      "metric": "same-contract prior20/ATR fixed-helper screen",
      "value": {
        "rule_version": "v3.0",
        "strategy": "trend",
        "scope": "v3_market_inputs_only",
        "status": "valid",
        "signal": "not_triggered",
        "side": null,
        "missing_fields": [],
        "issues": [],
        "execution_permission": "not_evaluated",
        "methodology_validation": "forward_research_not_performance_validated",
        "contract": "SR2701",
        "price_basis": "close",
        "product": "SR",
        "market_trade_date": "20261016",
        "as_of_date": "20261016",
        "signal_close": 5408.0,
        "prior20_high": 5563.0,
        "prior20_low": 5305.0,
        "prior10_low": 5318.0,
        "prior10_high": 5563.0,
        "atr20": 56.922700307900925,
        "atr_initialization": "61_bars_first20_TR_mean_then_Wilder",
        "sample_start": "20260716",
        "targets": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "volatility_ratio": 1.2683633342087492,
        "volatility_status": "available",
        "high_volatility": false,
        "freshness": "fresh",
        "expected_market_trade_date": "20261016"
      },
      "unit": "CNY/tonne; ratio",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-18T08:49:13.866894+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-18/2026-10-18-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily returned identity verified",
      "price_basis": "close/high/low",
      "comparison_basis": "strictly exclude signal day; fixed 61 bars",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-INDUSTRY",
      "metric": "domestic crush/sales/physical basis",
      "value": {
        "plant_rate_pct": 67.91,
        "daily_change_percentage_points": 2.95,
        "sales_10kt": 9.2,
        "sales_daily_change_10kt": -15.6,
        "jiangsu_spot": 3270,
        "spot_daily_change": -40,
        "basis": -46,
        "basis_daily_change": 17
      },
      "unit": "percent; 10kt; CNY/tonne",
      "observation_date": "2026-10-15",
      "published_at": "2026-10-16T08:56:14+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/source-notes.md",
      "original_source": "Nanhua Futures full attributed repost",
      "price_basis": "spot and same-region reported basis",
      "comparison_basis": "day over day; orders are not actual pickup",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-COUNTER",
      "metric": "same-sample inventory declined; forward arrival forecast is counterevidence",
      "value": {
        "inventory_20260925": 129.64,
        "inventory_20261009": 109.08,
        "october_arrival_forecast": 854
      },
      "unit": "10kt",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-16T14:26:00+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/source-notes.md",
      "original_source": "Mysteel full original analysis",
      "price_basis": "not_price",
      "comparison_basis": "same full-sample history; forecast not actual",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-INDUSTRY",
      "metric": "reported port rebound and MTO demand weakness",
      "value": {
        "reported_port_stock_10kt": 36.72,
        "reported_change_10kt": 6.21,
        "observation_date_exact": null,
        "mto": "loss and closures reported"
      },
      "unit": "10kt; qualitative",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-16",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/source-notes.md",
      "original_source": "Anliang Futures attributed Plasway digest; observation date/sample unverified",
      "price_basis": "not_price",
      "comparison_basis": "dated digest only; no comparison with mismatched old sample",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PUBLIC-RULES",
      "metric": "10/19 published ordinary M/MA plate width; broker margins differ",
      "value": {
        "M_limit_pct": 6,
        "MA2701_limit_pct": 6,
        "broker_margin_is_not_account_margin": true,
        "effective_for_trade_date": "2026-10-19"
      },
      "unit": "percent",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-16",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/source-notes.md",
      "original_source": "Sinolink and Maike own customer notices",
      "price_basis": "not_price",
      "comparison_basis": "ordinary months; exact exchange original/temporary notices remain pending",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "EXACT-CONTRACT",
      "metric": "API contract identities, dates and last 20 volumes",
      "value": {
        "fetched_at": "2026-10-18T08:52:13.784680+08:00",
        "source": "Tushare Pro original API response; no execution permission",
        "contracts": [
          {
            "ts_code": "M2701.DCE",
            "symbol": "M2701",
            "name": "豆粕2701",
            "list_date": "20260119",
            "delist_date": "20270115",
            "per_unit": 10.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "symbol": "MA701",
            "name": "甲醇2701",
            "list_date": "20260119",
            "delist_date": "20270114",
            "per_unit": 10.0
          }
        ],
        "M2701.DCE": [
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20261016",
            "open": 3322.0,
            "high": 3330.0,
            "low": 3276.0,
            "close": 3281.0,
            "settle": 3299.0,
            "pre_settle": 3340.0,
            "vol": 1234349.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20261015",
            "open": 3371.0,
            "high": 3376.0,
            "low": 3315.0,
            "close": 3316.0,
            "settle": 3340.0,
            "pre_settle": 3373.0,
            "vol": 1216140.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20261014",
            "open": 3375.0,
            "high": 3390.0,
            "low": 3355.0,
            "close": 3373.0,
            "settle": 3373.0,
            "pre_settle": 3373.0,
            "vol": 1116938.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20261013",
            "open": 3390.0,
            "high": 3395.0,
            "low": 3356.0,
            "close": 3361.0,
            "settle": 3373.0,
            "pre_settle": 3383.0,
            "vol": 973868.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20261012",
            "open": 3402.0,
            "high": 3420.0,
            "low": 3355.0,
            "close": 3383.0,
            "settle": 3383.0,
            "pre_settle": 3389.0,
            "vol": 1299134.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20261009",
            "open": 3372.0,
            "high": 3408.0,
            "low": 3370.0,
            "close": 3402.0,
            "settle": 3389.0,
            "pre_settle": 3388.0,
            "vol": 940245.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20261008",
            "open": 3372.0,
            "high": 3416.0,
            "low": 3360.0,
            "close": 3366.0,
            "settle": 3388.0,
            "pre_settle": 3369.0,
            "vol": 967353.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260930",
            "open": 3366.0,
            "high": 3390.0,
            "low": 3350.0,
            "close": 3372.0,
            "settle": 3369.0,
            "pre_settle": 3347.0,
            "vol": 845761.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260929",
            "open": 3359.0,
            "high": 3371.0,
            "low": 3327.0,
            "close": 3359.0,
            "settle": 3347.0,
            "pre_settle": 3386.0,
            "vol": 1202408.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260928",
            "open": 3412.0,
            "high": 3412.0,
            "low": 3362.0,
            "close": 3363.0,
            "settle": 3386.0,
            "pre_settle": 3405.0,
            "vol": 1162962.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260924",
            "open": 3404.0,
            "high": 3426.0,
            "low": 3385.0,
            "close": 3426.0,
            "settle": 3405.0,
            "pre_settle": 3414.0,
            "vol": 1112326.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260923",
            "open": 3415.0,
            "high": 3431.0,
            "low": 3402.0,
            "close": 3404.0,
            "settle": 3414.0,
            "pre_settle": 3410.0,
            "vol": 1060443.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260922",
            "open": 3399.0,
            "high": 3425.0,
            "low": 3395.0,
            "close": 3416.0,
            "settle": 3410.0,
            "pre_settle": 3391.0,
            "vol": 1320817.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260921",
            "open": 3393.0,
            "high": 3406.0,
            "low": 3374.0,
            "close": 3386.0,
            "settle": 3391.0,
            "pre_settle": 3429.0,
            "vol": 1226414.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260918",
            "open": 3465.0,
            "high": 3477.0,
            "low": 3387.0,
            "close": 3397.0,
            "settle": 3429.0,
            "pre_settle": 3480.0,
            "vol": 2046376.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260917",
            "open": 3479.0,
            "high": 3502.0,
            "low": 3456.0,
            "close": 3477.0,
            "settle": 3480.0,
            "pre_settle": 3434.0,
            "vol": 1597249.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260916",
            "open": 3385.0,
            "high": 3479.0,
            "low": 3382.0,
            "close": 3479.0,
            "settle": 3434.0,
            "pre_settle": 3374.0,
            "vol": 1714351.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260915",
            "open": 3366.0,
            "high": 3390.0,
            "low": 3357.0,
            "close": 3385.0,
            "settle": 3374.0,
            "pre_settle": 3384.0,
            "vol": 1184016.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260914",
            "open": 3402.0,
            "high": 3416.0,
            "low": 3357.0,
            "close": 3361.0,
            "settle": 3384.0,
            "pre_settle": 3422.0,
            "vol": 1706690.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260911",
            "open": 3421.0,
            "high": 3460.0,
            "low": 3400.0,
            "close": 3402.0,
            "settle": 3422.0,
            "pre_settle": 3399.0,
            "vol": 1937075.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260910",
            "open": 3420.0,
            "high": 3432.0,
            "low": 3375.0,
            "close": 3402.0,
            "settle": 3399.0,
            "pre_settle": 3397.0,
            "vol": 1484855.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260909",
            "open": 3403.0,
            "high": 3429.0,
            "low": 3382.0,
            "close": 3425.0,
            "settle": 3397.0,
            "pre_settle": 3415.0,
            "vol": 1469587.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260908",
            "open": 3407.0,
            "high": 3437.0,
            "low": 3395.0,
            "close": 3415.0,
            "settle": 3415.0,
            "pre_settle": 3404.0,
            "vol": 1451945.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260907",
            "open": 3417.0,
            "high": 3428.0,
            "low": 3384.0,
            "close": 3408.0,
            "settle": 3404.0,
            "pre_settle": 3402.0,
            "vol": 1415266.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260904",
            "open": 3361.0,
            "high": 3436.0,
            "low": 3355.0,
            "close": 3423.0,
            "settle": 3402.0,
            "pre_settle": 3386.0,
            "vol": 1781974.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260903",
            "open": 3360.0,
            "high": 3422.0,
            "low": 3352.0,
            "close": 3382.0,
            "settle": 3386.0,
            "pre_settle": 3376.0,
            "vol": 1921252.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260902",
            "open": 3385.0,
            "high": 3415.0,
            "low": 3346.0,
            "close": 3361.0,
            "settle": 3376.0,
            "pre_settle": 3357.0,
            "vol": 1742143.0
          },
          {
            "ts_code": "M2701.DCE",
            "trade_date": "20260901",
            "open": 3338.0,
            "high": 3395.0,
            "low": 3310.0,
            "close": 3377.0,
            "settle": 3357.0,
            "pre_settle": 3353.0,
            "vol": 1830938.0
          }
        ],
        "MA2701.ZCE": [
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20261016",
            "open": 3172.0,
            "high": 3223.0,
            "low": 3146.0,
            "close": 3192.0,
            "settle": 3187.0,
            "pre_settle": 3231.0,
            "vol": 1561960.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20261015",
            "open": 3282.0,
            "high": 3289.0,
            "low": 3164.0,
            "close": 3170.0,
            "settle": 3231.0,
            "pre_settle": 3275.0,
            "vol": 1452554.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20261014",
            "open": 3220.0,
            "high": 3320.0,
            "low": 3220.0,
            "close": 3262.0,
            "settle": 3275.0,
            "pre_settle": 3233.0,
            "vol": 1378408.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20261013",
            "open": 3255.0,
            "high": 3278.0,
            "low": 3193.0,
            "close": 3235.0,
            "settle": 3233.0,
            "pre_settle": 3257.0,
            "vol": 1305281.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20261012",
            "open": 3327.0,
            "high": 3384.0,
            "low": 3176.0,
            "close": 3229.0,
            "settle": 3257.0,
            "pre_settle": 3321.0,
            "vol": 1740113.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20261009",
            "open": 3300.0,
            "high": 3402.0,
            "low": 3259.0,
            "close": 3338.0,
            "settle": 3321.0,
            "pre_settle": 3148.0,
            "vol": 1493099.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20261008",
            "open": 3029.0,
            "high": 3200.0,
            "low": 3012.0,
            "close": 3200.0,
            "settle": 3148.0,
            "pre_settle": 2935.0,
            "vol": 633499.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260930",
            "open": 2913.0,
            "high": 2974.0,
            "low": 2902.0,
            "close": 2972.0,
            "settle": 2935.0,
            "pre_settle": 2947.0,
            "vol": 617789.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260929",
            "open": 2941.0,
            "high": 2977.0,
            "low": 2923.0,
            "close": 2953.0,
            "settle": 2947.0,
            "pre_settle": 2934.0,
            "vol": 824100.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260928",
            "open": 2965.0,
            "high": 2967.0,
            "low": 2907.0,
            "close": 2941.0,
            "settle": 2934.0,
            "pre_settle": 2892.0,
            "vol": 604302.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260924",
            "open": 2850.0,
            "high": 2963.0,
            "low": 2838.0,
            "close": 2960.0,
            "settle": 2892.0,
            "pre_settle": 2867.0,
            "vol": 994519.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260923",
            "open": 2882.0,
            "high": 2914.0,
            "low": 2821.0,
            "close": 2833.0,
            "settle": 2867.0,
            "pre_settle": 2929.0,
            "vol": 865565.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260922",
            "open": 2950.0,
            "high": 2956.0,
            "low": 2895.0,
            "close": 2944.0,
            "settle": 2929.0,
            "pre_settle": 2951.0,
            "vol": 683656.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260921",
            "open": 2977.0,
            "high": 3005.0,
            "low": 2905.0,
            "close": 2942.0,
            "settle": 2951.0,
            "pre_settle": 2977.0,
            "vol": 771528.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260918",
            "open": 2970.0,
            "high": 3019.0,
            "low": 2941.0,
            "close": 2952.0,
            "settle": 2977.0,
            "pre_settle": 3025.0,
            "vol": 713009.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260917",
            "open": 3062.0,
            "high": 3068.0,
            "low": 2989.0,
            "close": 2995.0,
            "settle": 3025.0,
            "pre_settle": 3036.0,
            "vol": 610236.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260916",
            "open": 2980.0,
            "high": 3077.0,
            "low": 2980.0,
            "close": 3052.0,
            "settle": 3036.0,
            "pre_settle": 3024.0,
            "vol": 807779.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260915",
            "open": 3050.0,
            "high": 3069.0,
            "low": 2985.0,
            "close": 3016.0,
            "settle": 3024.0,
            "pre_settle": 3043.0,
            "vol": 688297.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260914",
            "open": 3000.0,
            "high": 3108.0,
            "low": 2995.0,
            "close": 3016.0,
            "settle": 3043.0,
            "pre_settle": 3066.0,
            "vol": 648274.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260911",
            "open": 3130.0,
            "high": 3154.0,
            "low": 2978.0,
            "close": 3016.0,
            "settle": 3066.0,
            "pre_settle": 3054.0,
            "vol": 835215.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260910",
            "open": 3030.0,
            "high": 3137.0,
            "low": 3014.0,
            "close": 3043.0,
            "settle": 3054.0,
            "pre_settle": 2980.0,
            "vol": 733035.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260909",
            "open": 2967.0,
            "high": 3009.0,
            "low": 2945.0,
            "close": 2999.0,
            "settle": 2980.0,
            "pre_settle": 2951.0,
            "vol": 557514.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260908",
            "open": 2933.0,
            "high": 3004.0,
            "low": 2908.0,
            "close": 2985.0,
            "settle": 2951.0,
            "pre_settle": 2896.0,
            "vol": 505330.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260907",
            "open": 2877.0,
            "high": 2931.0,
            "low": 2853.0,
            "close": 2929.0,
            "settle": 2896.0,
            "pre_settle": 2893.0,
            "vol": 473715.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260904",
            "open": 2873.0,
            "high": 2923.0,
            "low": 2856.0,
            "close": 2900.0,
            "settle": 2893.0,
            "pre_settle": 2884.0,
            "vol": 424038.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260903",
            "open": 2904.0,
            "high": 2935.0,
            "low": 2817.0,
            "close": 2840.0,
            "settle": 2884.0,
            "pre_settle": 2946.0,
            "vol": 539483.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260902",
            "open": 2880.0,
            "high": 3024.0,
            "low": 2857.0,
            "close": 2921.0,
            "settle": 2946.0,
            "pre_settle": 2857.0,
            "vol": 547178.0
          },
          {
            "ts_code": "MA2701.ZCE",
            "trade_date": "20260901",
            "open": 2839.0,
            "high": 2893.0,
            "low": 2819.0,
            "close": 2855.0,
            "settle": 2857.0,
            "pre_settle": 2773.0,
            "vol": 492383.0
          }
        ]
      },
      "unit": "dates; tons/lot; lots",
      "observation_date": "2026-10-16",
      "published_at": "2026-10-18T08:52:13.784680+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/contract-and-volume-api.json",
      "original_source": "Tushare Pro fut_basic/fut_daily returned rows",
      "price_basis": "OHLC/volume",
      "comparison_basis": "MA last date conflict not silently resolved",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ORIGINAL-CLOCK",
      "metric": "immutable shared plan identity and registration correction",
      "value": {
        "MA": {
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
          "entry_quote_status": "expired_original_plan_not_current_quote",
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
        "M": {
          "entry": null,
          "stop": null,
          "targets": null,
          "entry_range": null,
          "signal_date": "2026-10-15",
          "valid_until": "2026-10-19",
          "latest_exit_date": null,
          "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
          "registered_at": "2026-10-15T19:30:56+08:00"
        },
        "M_registered_at": "2026-10-15T19:30:56+08:00"
      },
      "unit": "ISO dates; CNY/tonne",
      "observation_date": "2026-10-15",
      "published_at": "2026-10-15T19:30:56+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/shared-sources/catalog.json",
      "original_source": "hash-validated shared entries; explicitly adopted 10/15 r2",
      "price_basis": "historical plan",
      "comparison_basis": "original clocks retained",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "historical"
    },
    {
      "evidence_id": "CONTINUITY",
      "metric": "explicit M registration reconciliation",
      "value": [
        {
          "opportunity_id": "20261015-observe-M2701-trend-short-v3",
          "conflict": "initial registration null versus explicitly adopted r2 registration",
          "basis": "The 10/15 r2 handoff explicitly supersedes the first audit only to add the actual 19:30:56 registration. Its frozen evaluated_at equals that time. No new signal day or later deadline was introduced.",
          "registered_at": "2026-10-15T19:30:56+08:00",
          "signal_date": "2026-10-15",
          "valid_until": "2026-10-19",
          "execution_state_inherited": false,
          "current_disposition": "cancel original entry use: 10/16 close 3281 is outside the original signal band [3292,3326]. Do not revive by waiting for a return or extend to 10/20 using the consecutive 10/16 price screen."
        }
      ],
      "unit": "identity and ISO timestamps",
      "observation_date": "2026-10-18",
      "published_at": "2026-10-18T08:58:00.453554+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/continuity-reconciliation.json",
      "original_source": "this weekly review of immutable source records",
      "price_basis": "not_price",
      "comparison_basis": "metadata correction only; no ready/account reuse",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-PLAN-CHECK",
      "metric": "original M 10/15 signal-band diagnostic",
      "value": {
        "rule_version": "v3.0",
        "strategy": "trend",
        "scope": "v3_plan_arithmetic_only",
        "status": "valid",
        "signal": "triggered",
        "side": "short",
        "missing_fields": [],
        "issues": [],
        "execution_permission": "not_evaluated",
        "methodology_validation": "forward_research_not_performance_validated",
        "risk_unit": 1030.0,
        "cost_unit": 30.0,
        "net_reward": null,
        "reward_risk": null,
        "targets": null,
        "stop": 3410.0,
        "final_lots": null,
        "pending_checks": [
          "frozen_prospective_definition_and_evidence",
          "economic_causality",
          "contract_life_and_forced_exit_dates",
          "latest_executable_quotes",
          "stress_and_events",
          "account_and_capacity"
        ],
        "signal_inputs": {
          "rule_version": "v3.0",
          "strategy": "trend",
          "scope": "v3_market_inputs_only",
          "status": "valid",
          "signal": "triggered",
          "side": "short",
          "missing_fields": [],
          "issues": [],
          "execution_permission": "not_evaluated",
          "methodology_validation": "forward_research_not_performance_validated",
          "contract": "M2701",
          "price_basis": "close",
          "product": "M",
          "market_trade_date": "20261015",
          "as_of_date": "20261015",
          "signal_close": 3316.0,
          "prior20_high": 3502.0,
          "prior20_low": 3327.0,
          "prior10_low": 3327.0,
          "prior10_high": 3431.0,
          "atr20": 49.50233009542106,
          "atr_initialization": "61_bars_first20_TR_mean_then_Wilder",
          "sample_start": "20260715",
          "targets": null,
          "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
          "volatility_ratio": 1.1900326654701945,
          "volatility_status": "available",
          "high_volatility": false
        },
        "entry_expiry": "20261019",
        "entry_date": "20261019",
        "latest_exit_date": "20261113",
        "entry": 3310.0,
        "signal_date": "2026-10-15",
        "valid_until": "2026-10-19",
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "prior10_channel_stop": 3431.0,
        "entry_range": [
          3292,
          3326
        ]
      },
      "unit": "CNY/tonne; CNY/lot",
      "observation_date": "2026-10-15",
      "published_at": "2026-10-18T08:58:00.453554+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-18/evidence/m-original-signal-plan-result.json",
      "original_source": "fixed current futures_strategy helper; same actual contract",
      "price_basis": "close/high/low",
      "comparison_basis": "counterfactual arithmetic only; original entry use is now cancelled",
      "role": "required_execution",
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
      "data_feasibility_reason": "current price available; economic/contract-date/execution and account gaps",
      "signal": "triggered",
      "signal_evidence_refs": [
        "ORIGINAL-CLOCK"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EXACT-CONTRACT"
          ],
          "details": "Exact MA2701 API delist=2027-01-14 conflicts with earlier rule/calendar derivation 01/15; volume and broad maturity sufficient, precise forced boundary pending.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Exact MA2701 API delist=2027-01-14 conflicts with earlier rule/calendar derivation 01/15; volume and broad maturity sufficient, precise forced boundary pending.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "MA-INDUSTRY"
          ],
          "details": "Previous blanket pass remains withdrawn; nearby demand destruction and reported port refill require same-basis current reassessment.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Previous blanket pass remains withdrawn; nearby demand destruction and reported port refill require same-basis current reassessment.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ORIGINAL-CLOCK"
          ],
          "details": "Original 10/09 signal expires 10/13; no future entry use. Holding exit must be checked separately."
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-RULES",
            "PRICE-MA2701"
          ],
          "details": "Current 6% ordinary MA plate is publicly corroborated; effective stop, current executable quotes, exchange temporary notices, demand-event chronology and stress applicability remain unverified.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Current 6% ordinary MA plate is publicly corroborated; effective stop, current executable quotes, exchange temporary notices, demand-event chronology and stress applicability remain unverified.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
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
      "all_blockers": [
        "G3"
      ],
      "unknown_checks": [
        "G1",
        "G2",
        "G4",
        "G5",
        "G6"
      ],
      "first_blocker": "G3",
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
        "entry_quote_status": "expired_original_plan_not_current_quote",
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
        "EXACT-CONTRACT",
        "MA-INDUSTRY",
        "ORIGINAL-CLOCK",
        "PUBLIC-RULES",
        "PRICE-MA2701"
      ],
      "price_screening_date": "2026-10-16",
      "historical_price_screen": "original 2026-10-09 long price signal retained; 2026-10-15 new T signal not_triggered",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
      "registered_at": "2026-10-11T18:14:54+08:00",
      "risk_factors": {
        "strategy": 0.7,
        "market_risk": 0.5,
        "exchange_buffer": null,
        "market_risk_reason": "direct demand shock and economic disagreement; one 0.5 factor only"
      },
      "entry_window_state": "expired",
      "actual_position_status": "unknown"
    },
    {
      "candidate_id": "20261015-M2701-trend-short-v3",
      "opportunity_id": "20261015-observe-M2701-trend-short-v3",
      "trade_date": "2026-10-15",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "exact-contract price valid; current same-basis soybean-to-soymeal industrial chain and execution data missing",
      "signal": "triggered",
      "signal_evidence_refs": [
        "M-PLAN-CHECK"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EXACT-CONTRACT"
          ],
          "details": "M2701 returned last trade date 2027-01-15 and 20-day volume 1293245.75; full natural-person/broker boundary and current executable quote pending.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "M2701 returned last trade date 2027-01-15 and 20-day volume 1293245.75; full natural-person/broker boundary and current executable quote pending.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "M-PLAN-CHECK",
            "M-INDUSTRY",
            "M-COUNTER"
          ],
          "details": "Original 10/15 price break verified. Current 10/15 plant recovery and weak sales/physical prices support near-term short thesis; inventory decline, basis strengthening and future arrival reduction are nonfatal counterevidence; evidence weak, one market_risk=0.5 only."
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-M2701",
            "M-PLAN-CHECK",
            "CONTINUITY"
          ],
          "details": "10/16 close 3281 is below original allowed band low3292. Cancel original entry use, preserve 10/15 signal, 19:30:56 registration and 10/19 deadline. Consecutive 10/16 screen does not silently extend this opportunity."
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-RULES"
          ],
          "details": "6% ordinary plate corroborated and regular sessions read; exact current quote, exchange notice coverage, execution/pressure scenarios and any directly relevant new policy/supply event require pre-execution review. Old WASDE window has ended.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "6% ordinary plate corroborated and regular sessions read; exact current quote, exchange notice coverage, execution/pressure scenarios and any directly relevant new policy/supply event require pre-execution review. Old WASDE window has ended.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
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
      "all_blockers": [
        "G3"
      ],
      "unknown_checks": [
        "G1",
        "G4",
        "G5",
        "G6"
      ],
      "first_blocker": "G3",
      "only_blocker": null,
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": "2026-10-15",
        "valid_until": "2026-10-19",
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "registered_at": "2026-10-15T19:30:56+08:00"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "EXACT-CONTRACT",
        "M-PLAN-CHECK",
        "M-INDUSTRY",
        "M-COUNTER",
        "PRICE-M2701",
        "CONTINUITY",
        "PUBLIC-RULES"
      ],
      "price_screening_date": "2026-10-16",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
      "registered_at": "2026-10-15T19:30:56+08:00",
      "entry_window_state": "cancelled_price_deviation; original date deadline 2026-10-19 retained",
      "actual_position_status": "unknown",
      "current_price_signal": {
        "signal_date": "2026-10-16",
        "side": "short",
        "signal_close": 3281,
        "mechanical_valid_until": "2026-10-20",
        "not_adopted_as_extension_of_original_opportunity": true
      },
      "diagnostic_plan_arithmetic": {
        "reference_entry": 3310,
        "stop": 3410,
        "allowed_original_band": [
          3292,
          3326
        ],
        "risk_unit_budget": 1030,
        "purpose": "arithmetic diagnostic, cancelled original entry use; not a current plan"
      }
    },
    {
      "candidate_id": "20261016-RB2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-16",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh exact-contract price early screen complete; later execution gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-RB2701"
      ],
      "status": "no_signal",
      "price_screening_date": "2026-10-16",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-RB2701"
          ],
          "details": "Both directional strict prior20 breakouts are false; independent economics and later gates not declared passed."
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "only_blocker": null,
      "final_lots": null,
      "first_blocker": "G2",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "PRICE-RB2701"
      ]
    },
    {
      "candidate_id": "20261016-MA2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-16",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh exact-contract price early screen complete; later execution gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-MA2701"
      ],
      "status": "no_signal",
      "price_screening_date": "2026-10-16",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-MA2701"
          ],
          "details": "Both directional strict prior20 breakouts are false; independent economics and later gates not declared passed."
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "only_blocker": null,
      "final_lots": null,
      "first_blocker": "G2",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "PRICE-MA2701"
      ]
    },
    {
      "candidate_id": "20261016-SR2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-16",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh exact-contract price early screen complete; later execution gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-SR2701"
      ],
      "status": "no_signal",
      "price_screening_date": "2026-10-16",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-SR2701"
          ],
          "details": "Both directional strict prior20 breakouts are false; independent economics and later gates not declared passed."
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "only_blocker": null,
      "final_lots": null,
      "first_blocker": "G2",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "PRICE-SR2701"
      ]
    },
    {
      "candidate_id": "20261016-CF2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-16",
      "contracts": [
        "CF2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh exact-contract price early screen complete; later execution gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-CF2701"
      ],
      "status": "no_signal",
      "price_screening_date": "2026-10-16",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-CF2701"
          ],
          "details": "Both directional strict prior20 breakouts are false; independent economics and later gates not declared passed."
        }
      ],
      "evaluation_order": [
        "G2"
      ],
      "all_blockers": [
        "G2"
      ],
      "unknown_checks": [],
      "only_blocker": null,
      "final_lots": null,
      "first_blocker": "G2",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "PRICE-CF2701"
      ]
    },
    {
      "candidate_id": "20261016-MA2701-MA2705-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-16",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "month-specific numeric economic band and 5-20-session mechanism absent; not a price no_signal",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "status": "incomplete",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null
      },
      "not_evaluated_after_no_signal": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Ordered pair/API identities and dated calendars checked; both-leg volume, exact expiry and executable pair quotes pending.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Ordered pair/API identities and dated calendars checked; both-leg volume, exact expiry and executable pair quotes pending.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Research reviewed economic mechanism, but no defensible numeric anchor or verified pre-signal freeze; do not infer fair band from spread history.",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "Research reviewed economic mechanism, but no defensible numeric anchor or verified pre-signal freeze; do not infer fair band from spread history.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "No economic stop, near anchor target, full-range net R or numerical convergence plan.",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "No economic stop, near anchor target, full-range net R or numerical convergence plan.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "No executable two-leg quote/limit/slippage, naked-leg contingency or adverse-pair stress plan.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "No executable two-leg quote/limit/slippage, naked-leg contingency or adverse-pair stress plan.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
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
      "only_blocker": null,
      "final_lots": null,
      "first_blocker": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": []
    },
    {
      "candidate_id": "20261016-RB2701-RB2703-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-16",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "month-specific numeric economic band and 5-20-session mechanism absent; not a price no_signal",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "status": "incomplete",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null
      },
      "not_evaluated_after_no_signal": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Ordered pair/API identities and dated calendars checked; both-leg volume, exact expiry and executable pair quotes pending.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Ordered pair/API identities and dated calendars checked; both-leg volume, exact expiry and executable pair quotes pending.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Research reviewed economic mechanism, but no defensible numeric anchor or verified pre-signal freeze; do not infer fair band from spread history.",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "Research reviewed economic mechanism, but no defensible numeric anchor or verified pre-signal freeze; do not infer fair band from spread history.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "No economic stop, near anchor target, full-range net R or numerical convergence plan.",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "No economic stop, near anchor target, full-range net R or numerical convergence plan.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "No executable two-leg quote/limit/slippage, naked-leg contingency or adverse-pair stress plan.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "No executable two-leg quote/limit/slippage, naked-leg contingency or adverse-pair stress plan.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
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
      "only_blocker": null,
      "final_lots": null,
      "first_blocker": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": []
    },
    {
      "candidate_id": "20261016-SR2701-SR2705-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-16",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "month-specific numeric economic band and 5-20-session mechanism absent; not a price no_signal",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "status": "incomplete",
      "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null
      },
      "not_evaluated_after_no_signal": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Ordered pair/API identities and dated calendars checked; both-leg volume, exact expiry and executable pair quotes pending.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Ordered pair/API identities and dated calendars checked; both-leg volume, exact expiry and executable pair quotes pending.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Research reviewed economic mechanism, but no defensible numeric anchor or verified pre-signal freeze; do not infer fair band from spread history.",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "Research reviewed economic mechanism, but no defensible numeric anchor or verified pre-signal freeze; do not infer fair band from spread history.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "No economic stop, near anchor target, full-range net R or numerical convergence plan.",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "No economic stop, near anchor target, full-range net R or numerical convergence plan.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "No executable two-leg quote/limit/slippage, naked-leg contingency or adverse-pair stress plan.",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "No executable two-leg quote/limit/slippage, naked-leg contingency or adverse-pair stress plan.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Same-day actual equity, positions, orders, broker fees/margin, account limits and absolute stress/execution capacities are unavailable.",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Supply current account and fill/stop history, then run size-v3 with all applicable capacities.",
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
      "only_blocker": null,
      "final_lots": null,
      "first_blocker": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": []
    }
  ],
  "unresolved_items": [
    {
      "item": "Verify same-basis MA supply/MTO and precise forced-exit date conflict",
      "owner": "research",
      "due_at": "next_report",
      "required_evidence": [],
      "resolution": "pending"
    },
    {
      "item": "Review next M/RB current industrial release, new signal and original opportunity disposition",
      "owner": "research",
      "due_at": "next_report",
      "required_evidence": [],
      "resolution": "pending"
    },
    {
      "item": "Continue month-specific V anchor cost/supply study without inventing bands",
      "owner": "research",
      "due_at": "next_report",
      "required_evidence": [],
      "resolution": "pending"
    }
  ],
  "shadow_plans": [],
  "evidence_corrections": [],
  "generator": "codex",
  "evaluated_at": "2026-10-18T08:58:00.453554+08:00",
  "registered_at": "2026-10-18T08:58:00.453554+08:00",
  "continuity_corrections": {
    "inherited_count": 10,
    "new_metadata_reconciliation": [
      {
        "opportunity_id": "20261015-observe-M2701-trend-short-v3",
        "conflict": "initial registration null versus explicitly adopted r2 registration",
        "basis": "The 10/15 r2 handoff explicitly supersedes the first audit only to add the actual 19:30:56 registration. Its frozen evaluated_at equals that time. No new signal day or later deadline was introduced.",
        "registered_at": "2026-10-15T19:30:56+08:00",
        "signal_date": "2026-10-15",
        "valid_until": "2026-10-19",
        "execution_state_inherited": false,
        "current_disposition": "cancel original entry use: 10/16 close 3281 is outside the original signal band [3292,3326]. Do not revive by waiting for a return or extend to 10/20 using the consecutive 10/16 price screen."
      }
    ],
    "main_prior_market_original_path": "research/futures/weekly/2026-10-11/2026-10-11-market-research-r2.md",
    "main_prior_market_sha256": "ae63fea433500f8ad07db75371f4e47b7b555c1d5012faa1487e8071c1454eaa"
  },
  "risk_regime": "unknown",
  "performance_status": "not_automated"
}
```
