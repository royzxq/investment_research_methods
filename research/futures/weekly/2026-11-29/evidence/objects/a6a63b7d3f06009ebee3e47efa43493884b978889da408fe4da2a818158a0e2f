# 2026-10-15 期货收盘定向执行审计

覆盖：五个 T 的 10/15 收盘核验，MA2701 原计划的公告/经济反证/止损/事件/期限逐项检查，以及新触发的 M2701；五对 V 因无已冻结经济锚未评估。行情为 Tushare Pro `fut_daily` 返回行，日历为 Tushare `trade_cal(exchange=SSE)`，不代表期交所夜盘/临停已核；18:00 截止不证明最终结算发布。

| 项目 | 事实 | 本期处置 |
|---|---|---|
| MA2701 旧多头 | 原 10/09 信号、10/11 登记、10/13 截止。10/15 high/low/close=3289/3164/3170，原参考 SL=3139，今日未据日线触及 | 入场窗 expired；实际持仓/当前 SL 未知，按[存量检查](../../refresh/2026-10-15/2026-10-15-stock-plan-check.md)条件管理 |
| M2701 新空头 | 10/15 收 3316 < 先前 20 日低 3327，ATR20=49.50；日期级原窗口 10/16、10/19 | 产业链反证与同口径资料未核，G1/G3/G4 也缺；incomplete，无数值计划或许可，见[定向研究](2026-10-15-m-signal-research.md) |
| CF/RB/SR 与 MA 新 T | 10/15 均未机械触发 | 仅价格筛选，非全套执行门结论 |

如已有 MA2701 持仓，先取得真实成交、持仓、动态止损及保证金/压力容量；止损或逻辑失效按可成交退出规则执行，不推定已平仓。下一复核先补 M 国内大豆到港→压榨→豆粕库存/提货/基差同口径证据与大商所参数；V 建锚研究交周更。工具不授予 ready；账户/最终手数 null，收益未验证。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-15",
  "research_mode": "public_data",
  "assessment_scope": "state_refresh_existing_plan_and_new_signal",
  "generator": "codex",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "origin/main 24e7285d0288076704bc1fafc9398a8537ff5c33",
    "canonical_sha256": "ffa7c08762af97700064854d5cf4c9480ece70c65c0ba54d6b272d75cbd01458"
  },
  "snapshot": {
    "market_trade_date": "2026-10-15",
    "market_captured_at": "2026-10-15T19:27:24.598032+08:00",
    "source_artifacts": [
      "research/futures/refresh/2026-10-15/2026-10-15-signal-refresh.json",
      "research/futures/refresh/2026-10-15/evidence/2026-10-15-signal-refresh/market-inputs.json",
      "research/futures/refresh/2026-10-15/2026-10-15-stock-plan-check.md",
      "research/futures/weekly/2026-10-15/2026-10-15-m-signal-research.md"
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
      "five T exact-contract mechanical price screens through 2026-10-15",
      "all one known carried MA2701 plan risk check",
      "M2701 triggered price candidate"
    ],
    "missing_scope": [
      "M2701 current domestic causal chain, exchange/event and account checks",
      "CZCE MA2701 current notices and actual position"
    ],
    "research_only_scope": [
      "five V pairs lack frozen economic anchors"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "MA-1015-RAW",
      "metric": "MA2701 daily OHLC 10/14-15",
      "value": [
        {
          "ts_code": "MA2701.ZCE",
          "trade_date": "20261014",
          "close": 3262.0,
          "high": 3320.0,
          "low": 3220.0,
          "response_ts_code": "MA2701.ZCE"
        },
        {
          "ts_code": "MA2701.ZCE",
          "trade_date": "20261015",
          "close": 3170.0,
          "high": 3289.0,
          "low": 3164.0,
          "response_ts_code": "MA2701.ZCE"
        }
      ],
      "unit": "CNY/tonne",
      "observation_date": "2026-10-15",
      "published_at": "2026-10-15T19:27:18.215564+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-15/evidence/2026-10-15-signal-refresh/market-inputs.json",
      "original_source": "Tushare Pro fut_daily response MA2701.ZCE",
      "price_basis": "close",
      "comparison_basis": "same_contract",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-1015-RAW",
      "metric": "M2701 price signal",
      "value": {
        "close": 3316.0,
        "prior20_low": 3327.0,
        "atr20": 49.50233009542106,
        "valid_until": "2026-10-19",
        "returned_ts_code": "M2701.DCE"
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-10-15",
      "published_at": "2026-10-15T19:27:19.282475+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-15/evidence/2026-10-15-signal-refresh/market-inputs.json",
      "original_source": "Tushare Pro fut_daily response M2701.DCE",
      "price_basis": "close",
      "comparison_basis": "same_contract",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "M-1009-CJFCO",
      "metric": "M chain and counter evidence",
      "value": {
        "soymeal_inventory_10k_tonnes": 130.11,
        "week_change_10k_tonnes": 0.47,
        "soybean_inventory_10k_tonnes": 821.76,
        "demand": "Q4 feed demand expected strong"
      },
      "unit": "mixed",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-09T18:41:05+08:00",
      "source_url_or_file": "https://www.cjfco.com.cn/main/a/20261009/83286.shtml",
      "original_source": "Changjiang Futures",
      "price_basis": "none",
      "comparison_basis": "different_date",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "historical"
    },
    {
      "evidence_id": "M-1014-GRAIN-REPRINT",
      "metric": "Soymeal inventory/basis counter",
      "value": "inventory down and basis firmer; precise quote date inconsistent",
      "unit": "qualitative",
      "observation_date": "2026-10-14",
      "published_at": "2026-10-14T10:29:00+08:00",
      "source_url_or_file": "https://qhweb.eastmoney.com/news/202610143895207636.html",
      "original_source": "National Food and Strategic Reserves Administration attributed via Eastmoney",
      "price_basis": "none",
      "comparison_basis": "different_date",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-1015-INDUSTRY",
      "metric": "MTO and inventory opposing evidence",
      "value": "MTO weakness vs low absolute port inventory and rising arrivals",
      "unit": "qualitative",
      "observation_date": "2026-10-15",
      "published_at": "2026-10-15T11:14:00+08:00",
      "source_url_or_file": "https://www.quheqihuo.com/news/202610154496302.html",
      "original_source": "Quhe composite citing industry figures",
      "price_basis": "none",
      "comparison_basis": "different_contract_and_basis",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-ORIGINAL-PLAN",
      "metric": "frozen MA2701 original plan",
      "value": {
        "opportunity_id": "20261011-observe-MA2701-trend-long-v3",
        "signal_date": "2026-10-09",
        "registered_at": "2026-10-11T18:14:54+08:00",
        "valid_until": "2026-10-13",
        "stop": 3139
      },
      "unit": "plan",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11T18:14:54+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-11/2026-10-11-execution-audit-r3.md",
      "original_source": "adopted v3 audit",
      "price_basis": "none",
      "comparison_basis": "original",
      "role": "required_model",
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
      "data_feasibility_reason": "MA2701 verified 10/15 OHLC and dated SSE calendar; execution and account remain unknown",
      "signal": "triggered",
      "signal_evidence_refs": [
        "MA-ORIGINAL-PLAN",
        "MA-1015-RAW"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Exact MA2701 daily OHLC present; current expiry, current public contract limits, 20-day volume and executable quote not independently reverified",
          "evidence_refs": [
            "MA-1015-RAW"
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
          "details": "Original 10/09 price signal is historical. 10/15 new price signal not triggered; MTO negative demand evidence and low port stocks/rising arrivals remain conflicting and different-basis.",
          "evidence_refs": [
            "MA-1015-INDUSTRY",
            "MA-ORIGINAL-PLAN",
            "MA-1015-RAW"
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
          "result": "fail",
          "details": "Original entry window expired on 10/13. 10/15 high 3289 touching old range does not reopen it. Holding exits require separate position evidence.",
          "evidence_refs": [
            "MA-ORIGINAL-PLAN",
            "MA-1015-RAW"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "MTO shock and nearby original stop require current CZCE notice, event window, stress and executable exit review",
          "evidence_refs": [
            "MA-1015-INDUSTRY"
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
        "MA-1015-RAW",
        "MA-1015-INDUSTRY",
        "MA-ORIGINAL-PLAN"
      ],
      "price_screening_date": "2026-10-15",
      "historical_price_screen": "original 2026-10-09 long price signal retained; 2026-10-15 new T signal not_triggered",
      "evaluated_at": "2026-10-15T19:30:56+08:00",
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
        "M-1015-RAW"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Exact M2701 OHLC present; last trade date, 20-day volume, public limits and executable quote unverified",
          "evidence_refs": [
            "M-1015-RAW"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "verify M2701 contract/volume/current quote",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Close 3316 < prior20 low 3327 confirms price side; USDA upstream supply change lacks current domestic transmission. Prior soymeal high inventory conflicts with reported fresh inventory decline and firmer basis; exact same-basis arrivals/crush/inventory/pickup/basis missing",
          "evidence_refs": [
            "M-1015-RAW",
            "M-1009-CJFCO",
            "M-1014-GRAIN-REPRINT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "read original same-period arrivals, crush, meal inventory, pickup and basis",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "No frozen executable short entry range/stop/cost and earliest applicable session; do not infer a plan from signal close",
          "evidence_refs": [
            "M-1015-RAW"
          ],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "form and helper-validate complete prospective T plan only if G2 resolves",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "DCE current notices, directly relevant event timing, stress loss, exit liquidity and night session attribution unverified",
          "evidence_refs": [
            "M-1015-RAW"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "verify DCE rules/notices, events, stress and executable quote",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Current account equity, actual positions/orders, broker margin, fees and limits unknown",
          "evidence_refs": [
            "M-1015-RAW"
          ],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "obtain same-day account snapshot before execution",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "No valid risk sizing without G5 and execution/stress capacities",
          "evidence_refs": [
            "M-1015-RAW"
          ],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "after complete inputs run size-v3 and validate capacity",
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
        "signal_date": "2026-10-15",
        "valid_until": "2026-10-19",
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions"
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
        "M-1015-RAW",
        "M-1009-CJFCO",
        "M-1014-GRAIN-REPRINT"
      ],
      "price_screening_date": "2026-10-15",
      "evaluated_at": "2026-10-15T19:30:56+08:00",
      "registered_at": null,
      "entry_window_state": "session_check_required; date-level valid entry 10/16 and 10/19 only if fully reverified",
      "actual_position_status": "unknown"
    }
  ],
  "evidence_corrections": [],
  "shadow_plans": [],
  "performance_status": "not_automated",
  "unresolved_items": [
    {
      "item": "M2701 same-basis domestic chain, public DCE event/contract rules and prospective plan missing",
      "owner": "research",
      "due_at": "before_original_2026-10-19_expiry",
      "required_evidence": [
        "M-1015-RAW",
        "M-1009-CJFCO",
        "M-1014-GRAIN-REPRINT"
      ],
      "resolution": "pending"
    },
    {
      "item": "MA2701 actual position and current valid stop/exit risk unknown",
      "owner": "user",
      "due_at": "before_next_tradable_session",
      "required_evidence": [
        "MA-ORIGINAL-PLAN",
        "MA-1015-RAW"
      ],
      "resolution": "pending"
    },
    {
      "item": "V five ordered pairs lack defensible frozen economic anchors",
      "owner": "research",
      "due_at": "next_weekly_review",
      "required_evidence": [],
      "resolution": "pending"
    }
  ],
  "risk_context": {
    "regime": "unknown",
    "reason": "no verified account and all relevant event/pressure conditions not resolved"
  },
  "evaluated_at": "2026-10-15T19:30:56+08:00",
  "registered_at": null,
  "supersedes": [
    {
      "path": "research/futures/weekly/2026-10-13/2026-10-13-execution-audit.md",
      "sha256": "dd6278975f05d16414805cc608aa289fb66fd5ba163e7f440960b8d5e4681127"
    }
  ]
}
```
