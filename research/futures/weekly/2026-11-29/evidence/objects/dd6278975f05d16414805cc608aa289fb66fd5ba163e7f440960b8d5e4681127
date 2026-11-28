# MA2701 存量计划定向审计 · 2026-10-13

10/13 收盘刷新：原 MA2701 信号日 10/09、登记 10/11、截止 10/13 不变。五个 T 今天均无新机械突破；V 无事前锚未评估。今日 MA2701 日盘高价 3278 低于原入场范围下界 3289，19:30 时日盘已结束；刷新器对截止日仍标 `session_check_required`，夜盘归属与任何场次调整未逐项核，故不声称仍可新入场。10/14 不顺延原机会。

[存量与来源记录](../../refresh/2026-10-13/2026-10-13-stock-plan-check.md)逐项记录产业反证、止损、事件与期限。原参考 SL 3139 未被 10/12–13 日低触及，但真实持仓、成交、收紧后的 SL、盘中执行均未知；若有持仓，核账户与当前风险后按既定退出规则管理，不把入场窗到期等同于平仓。新华财经报告的 MA2611 跌幅不可替代 MA2701 日线。当前 G2、G4 与账户门仍有缺口；今日只作状态重评，不改 v3 参数。

以下 JSON 是定向结构审计；当前机会没有交易许可或最终手数。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-13",
  "research_mode": "public_data",
  "assessment_scope": "state_refresh_existing_plan",
  "generator": "codex",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "origin/main 24e7285",
    "canonical_sha256": "ffa7c08762af97700064854d5cf4c9480ece70c65c0ba54d6b272d75cbd01458"
  },
  "snapshot": {
    "market_trade_date": "2026-10-13",
    "market_captured_at": "2026-10-13T19:28:52.352014+08:00",
    "source_artifacts": [
      "research/futures/refresh/2026-10-13/2026-10-13-signal-refresh.json",
      "research/futures/refresh/2026-10-13/2026-10-13-stock-plan-check.md",
      "research/futures/weekly/2026-10-12/2026-10-12-execution-audit.md"
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
      "10/13 five T mechanical closes",
      "MA2701 original plan current price, counter-evidence, session and conditional holding review"
    ],
    "missing_scope": [
      "non-triggered T routes not given fresh industrial G1-G6 review",
      "current MA2701 exchange margin/limit/quote, exact event window and account not verified"
    ],
    "research_only_scope": [
      "V pairs lack frozen economic anchors"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "MA-1013-RAW",
      "metric": "MA2701 exact-contract daily OHLC and original entry range",
      "value": {
        "close": 3235,
        "high": 3278,
        "low": 3193,
        "previous_close": 3229,
        "previous_high": 3384,
        "previous_low": 3176,
        "returned_ts_code": "MA2701.ZCE",
        "identity_basis": "fut_daily_response_ts_code",
        "original_entry_range": [
          3289,
          3387
        ],
        "original_stop_reference": 3139
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-10-13",
      "published_at": "2026-10-13T19:28:45+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-13/evidence/2026-10-13-signal-refresh/market-inputs.json",
      "original_source": "Tushare Pro fut_daily returned rows",
      "price_basis": "close/high/low",
      "comparison_basis": "exact MA2701, not MA2611",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-1013-REFRESH",
      "metric": "Five T current mechanical signals and original window",
      "value": {
        "MA2701_signal": "not_triggered",
        "original_signal_date": "2026-10-09",
        "original_valid_until": "2026-10-13",
        "window_status": "session_check_required"
      },
      "unit": "status/date",
      "observation_date": "2026-10-13",
      "published_at": "2026-10-13T19:28:52.352014+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-13/2026-10-13-signal-refresh.json",
      "original_source": "current futures_refresh.py",
      "price_basis": "close",
      "comparison_basis": "SSE dated calendar only",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-1013-CNFIN",
      "metric": "Main contract and MTO demand counter-evidence",
      "value": {
        "main_contract": "MA2611",
        "main_decline_pct": 6.73,
        "mto_demand": "shutdowns and negative feedback reported",
        "counterpoint": "port inventory extremely low"
      },
      "unit": "percent/qualitative",
      "observation_date": "2026-10-13",
      "published_at": "2026-10-13",
      "source_url_or_file": "https://www.cnfin.com/yw-lb/detail/20261013/4480148_1.html",
      "original_source": "新华财经商品日报；引用银河期货产业观点",
      "price_basis": "main contract MA2611",
      "comparison_basis": "MA2701 not inferred from main",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-1013-CZCE",
      "metric": "MA session schedule and contract specification",
      "value": {
        "day": "09:00-11:30,13:30-15:00",
        "night": "21:00-23:00",
        "tick": 1,
        "multiplier": 10
      },
      "unit": "Asia/Shanghai; CNY/t; t/lot",
      "observation_date": "2024-02-06",
      "published_at": "2024-02-06",
      "source_url_or_file": "https://www.czce.com.cn/cn/uploadfile/2024/02/07/20240207154824122.pdf",
      "original_source": "郑州商品交易所甲醇业务细则",
      "price_basis": "not_price",
      "comparison_basis": "current temporary announcements still unverified",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-ORIGINAL-PLAN",
      "metric": "Frozen 10/11 MA2701 plan and clock",
      "value": {
        "opportunity_id": "20261011-observe-MA2701-trend-long-v3",
        "signal_date": "2026-10-09",
        "registered_at": "2026-10-11T18:14:54+08:00",
        "valid_until": "2026-10-13",
        "entry_range": [
          3289,
          3387
        ],
        "stop": 3139
      },
      "unit": "CNY/tonne/date",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11T19:11:01+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/2026-10-11-execution-audit-r3.md",
      "original_source": "adopted local/published-compatible audited plan",
      "price_basis": "planned quote",
      "comparison_basis": "historical frozen plan; not actual fill",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "historical"
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
      "data_feasibility": "available",
      "data_feasibility_reason": "10/13 MA2701 verified raw OHLC and SSE dated calendar available; current execution/industrial/account checks remain open",
      "signal": "triggered",
      "signal_evidence_refs": [
        "MA-ORIGINAL-PLAN",
        "MA-1013-REFRESH"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "exact contract data present; current last-day/discretionary early exit, 20-day volume and execution quote not all independently reverified",
          "evidence_refs": [
            "MA-1013-RAW",
            "MA-1013-CZCE"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "verify exact MA2701 current expiry, liquidity and executable quote",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "10/09 price breakout remains historical; today MA2701 close is 3235 without new signal; MTO demand shock continues while low port stocks counter it. Independent same-basis economics not resolved for renewed long entry.",
          "evidence_refs": [
            "MA-1013-RAW",
            "MA-1013-CNFIN",
            "MA-ORIGINAL-PLAN"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "verify comparable port/inland supply, MTO actual demand and basis before any new thesis",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "original plan and 10/13 expiry preserved; 10/13 day session high 3278 below 3289 entry minimum, and day session closed by evaluation time. Current night-session trading-day attribution and any exception not independently verified; no remaining original-window entry asserted.",
          "evidence_refs": [
            "MA-1013-RAW",
            "MA-1013-REFRESH",
            "MA-1013-CZCE",
            "MA-ORIGINAL-PLAN"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "verify current exchange session attribution; after 10/13 date close original entry window and await new signal",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "MTO shock and abrupt price move require current MA2701 exchange board/margin/limit, event-window, stress and executable exit review",
          "evidence_refs": [
            "MA-1013-CNFIN",
            "MA-1013-CZCE"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "verify current CZCE notices, MA2701 quote, event T and stress/exit route",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "current equity, position, pending orders, broker margin/fees and limits unknown",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "obtain current account snapshot and actual fill/position history",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "cannot compute final capacity without G5 and current stress/execution inputs",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "after verified inputs, run size-v3 and constrain by actual execution/stress capacity",
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
        "entry_quote_status": "original_plan_not_current_quote",
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
        "MA-1013-RAW",
        "MA-1013-REFRESH",
        "MA-1013-CNFIN",
        "MA-1013-CZCE",
        "MA-ORIGINAL-PLAN"
      ],
      "price_screening_date": "2026-10-13",
      "historical_price_screen": "2026-10-09 triggered long retained solely as original fact",
      "evaluated_at": "2026-10-13T19:32:21+08:00",
      "registered_at": "2026-10-11T18:14:54+08:00",
      "risk_factors": {
        "strategy": 0.7,
        "market_risk": 0.5,
        "exchange_buffer": null,
        "market_risk_reason": "direct demand shock and economic disagreement; one 0.5 factor only"
      },
      "entry_window_state": "session_check_required; 10/13 day session closed, no range print; do not extend into 10/14",
      "actual_position_status": "unknown"
    }
  ],
  "evidence_corrections": [],
  "shadow_plans": [],
  "performance_status": "not_automated",
  "unresolved_items": [
    {
      "item": "MA2701 current position and any 10/12 fill unknown",
      "owner": "user",
      "due_at": "before_execution"
    },
    {
      "item": "Current MA2701 exchange/position risk and event window unverified",
      "owner": "research",
      "due_at": "before_execution"
    },
    {
      "item": "V economic anchors absent",
      "owner": "research",
      "due_at": "next_report"
    }
  ],
  "risk_context": {
    "regime": "unknown",
    "reason": "current related demand shock and position state not fully verified"
  },
  "evaluated_at": "2026-10-13T19:32:21+08:00",
  "registered_at": null,
  "supersedes": [
    "research/futures/weekly/2026-10-12/2026-10-12-execution-audit.md"
  ]
}
```
