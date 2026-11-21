# 期货执行审计 · 2026-11-22

实际 origin/main 98c260f、v3.0，current_framework；generator=codex，public_data。先复核MA/M/RB/SR四项原信号，再审五T和三V，共12条记录，不能当12个新机会。五T当根no_signal，三V缺锚未评估；无新触发成案，最多两条新深研上限未消耗。四旧案G3已知失效与账户/执行未知并存，保持incomplete。全部final_lots和真实收益null。

RB原10/26入场上限11/20已过；10/27可达报价3034–3044的备选原上限11/23，条件路径至11/20未触其参考止损、下一场3051，仅供核真实仓位，不能据日线推成交或统一SL。MA原计划条件止损和时间界已过；M越带取消与10/19截止；SR取消及11/17截止均保留。没有延长或复活任何原窗口。全部公告、产业反证、止损与期限见[原路径](evidence/holding-path-review.json)、[场次与规则](evidence/exchange-and-event-review.md)及[接续裁决](evidence/continuity-reconciliation.json)。

当前缺口：真实账户/Entry/有效SL/退出（user提供后研究核）；精确MA/SR最后日及临时场次、当前报价与公开压力场景（research）；V双侧经济区间与收敛（research）。signal早停不代替后续研究，不能声称全市场零机会。既有撤回在JSON保留，本期无新增已采纳证据错误。证据行published_at为本地冻结时间，外部实际发布日期/观察日见原文件。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-11-22",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
  "execution_permission": "not_evaluated",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "98c260f71ff725240b3024c46e0bda1250829643"
  },
  "snapshot": {
    "market_trade_date": "2026-11-20",
    "market_captured_at": "2026-11-22T01:00:20.252654+08:00",
    "source_artifacts": [
      "research/futures/refresh/2026-11-22/2026-11-22-signal-refresh-r2.json",
      "research/futures/weekly/2026-11-22/evidence/price-and-plan-calculation.json",
      "research/futures/weekly/2026-11-22/evidence/source-manifest.json"
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
      "5 exact-contract T screens",
      "4 original-signal dispositions/conditional holding reviews",
      "3 current V research pairs",
      "2 roll-preparation pairs raw coverage"
    ],
    "missing_scope": [
      "current account/fills/effective stops",
      "venue temporary sessions and precise MA/SR contract expiry conflict",
      "V frozen economic bands and 5–20 day mechanisms"
    ],
    "research_only_scope": [
      "MA/RB/SR V economic-anchor routes without defensible bands",
      "specialized import shipment/stock causal submodels with unavailable verified samples"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "SHARED",
      "metric": "explicit adoption, original clocks and inherited withdrawals",
      "value": "17 entries / 22 groups / one reconciled M conflict",
      "unit": "record",
      "observation_date": "2026-11-22",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/continuity-reconciliation.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "OLDPATH",
      "metric": "conditional original plan path, not fills",
      "value": null,
      "unit": "record",
      "observation_date": "2026-11-20",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/holding-path-review.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "CAL",
      "metric": "venue dated calendars and contract rows",
      "value": null,
      "unit": "record",
      "observation_date": "2026-11-22",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/tushare-supplement.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "EVENT",
      "metric": "public current rules/parameters, venue events and limitations",
      "value": null,
      "unit": "record",
      "observation_date": "2026-11-22",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/exchange-and-event-review.md",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MRB",
      "metric": "M/RB independent public industry chain and counterevidence",
      "value": null,
      "unit": "record",
      "observation_date": "2026-11-22",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/m-rb-public.md",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "OTHER",
      "metric": "MA/SR/CF public evidence and limitations",
      "value": null,
      "unit": "record",
      "observation_date": "2026-11-22",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/ma-sr-cf-public.md",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ANCHORS",
      "metric": "current V research gaps, no adopted valid anchor",
      "value": null,
      "unit": "record",
      "observation_date": "2026-11-22",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/anchors/2026-11-22/2026-11-22-anchors.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-MA2701",
      "metric": "61 dated exact-contract bars and strict prior20 signal",
      "value": {
        "contract": "MA2701",
        "ts_code": "MA2701.ZCE",
        "fetched_at": "2026-11-22T01:00:18.126214+08:00",
        "prior_week_close": 3266.0,
        "close": 3073.0,
        "continuous_61_start": "20260820",
        "continuous_61_end": "20261120",
        "prior20_high": 3615.0,
        "prior20_low": 3014.0,
        "atr20": 123.83738949941885,
        "high_volatility": false,
        "signal": "not_triggered"
      },
      "unit": "record",
      "observation_date": "2026-11-20",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-22/2026-11-22-signal-refresh-r2.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-RB2701",
      "metric": "61 dated exact-contract bars and strict prior20 signal",
      "value": {
        "contract": "RB2701",
        "ts_code": "RB2701.SHF",
        "fetched_at": "2026-11-22T01:00:18.672562+08:00",
        "prior_week_close": 3035.0,
        "close": 2999.0,
        "continuous_61_start": "20260820",
        "continuous_61_end": "20261120",
        "prior20_high": 3072.0,
        "prior20_low": 2955.0,
        "atr20": 29.436207051888356,
        "high_volatility": false,
        "signal": "not_triggered"
      },
      "unit": "record",
      "observation_date": "2026-11-20",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-22/2026-11-22-signal-refresh-r2.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-M2701",
      "metric": "61 dated exact-contract bars and strict prior20 signal",
      "value": {
        "contract": "M2701",
        "ts_code": "M2701.DCE",
        "fetched_at": "2026-11-22T01:00:19.213934+08:00",
        "prior_week_close": 3147.0,
        "close": 3071.0,
        "continuous_61_start": "20260820",
        "continuous_61_end": "20261120",
        "prior20_high": 3286.0,
        "prior20_low": 3041.0,
        "atr20": 50.71443637302063,
        "high_volatility": false,
        "signal": "not_triggered"
      },
      "unit": "record",
      "observation_date": "2026-11-20",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-22/2026-11-22-signal-refresh-r2.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-SR2701",
      "metric": "61 dated exact-contract bars and strict prior20 signal",
      "value": {
        "contract": "SR2701",
        "ts_code": "SR2701.ZCE",
        "fetched_at": "2026-11-22T01:00:19.726383+08:00",
        "prior_week_close": 5146.0,
        "close": 5056.0,
        "continuous_61_start": "20260820",
        "continuous_61_end": "20261120",
        "prior20_high": 5400.0,
        "prior20_low": 5015.0,
        "atr20": 54.61907214974101,
        "high_volatility": false,
        "signal": "not_triggered"
      },
      "unit": "record",
      "observation_date": "2026-11-20",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-22/2026-11-22-signal-refresh-r2.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-CF2701",
      "metric": "61 dated exact-contract bars and strict prior20 signal",
      "value": {
        "contract": "CF2701",
        "ts_code": "CF2701.ZCE",
        "fetched_at": "2026-11-22T01:00:20.252654+08:00",
        "prior_week_close": 15555.0,
        "close": 15455.0,
        "continuous_61_start": "20260820",
        "continuous_61_end": "20261120",
        "prior20_high": 15885.0,
        "prior20_low": 15030.0,
        "atr20": 201.5651294282018,
        "high_volatility": false,
        "signal": "not_triggered"
      },
      "unit": "record",
      "observation_date": "2026-11-20",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-22/2026-11-22-signal-refresh-r2.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-ALT-OLD",
      "metric": "inherited invalid applicability",
      "value": "10/13 original band unavailable; already withdrawn 11/15",
      "unit": "record",
      "observation_date": "2026-11-15",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/continuity-reconciliation.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "RB-ALT-OLD",
      "metric": "inherited invalid applicability",
      "value": "10/27 original reference3047 unreachable; already withdrawn 11/15",
      "unit": "record",
      "observation_date": "2026-11-15",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/continuity-reconciliation.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "RB-WINDOW-OLD",
      "metric": "inherited invalid applicability",
      "value": "remaining_window despite10/27 expiry; already withdrawn11/08",
      "unit": "record",
      "observation_date": "2026-11-15",
      "published_at": "2026-11-22T01:06:05.803438+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-22/evidence/continuity-reconciliation.json",
      "original_source": "dated original API or read public source; local published_at is freeze time, original publication dates in cited file",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "invalid",
      "time_scope": "historical"
    }
  ],
  "candidates": [
    {
      "candidate_id": "20261009-MA2701-trend-long-v3",
      "opportunity_id": "20261011-observe-MA2701-trend-long-v3",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "long",
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
        "entry_quote_status": "historical_only",
        "round_trip_fee_budget": 20,
        "round_trip_slippage_budget": 20,
        "cost_basis": "研究预算，非用户实收；实际费用/滑点变化后必须重算",
        "alternate_entry": {
          "entry_date": "2026-10-13",
          "latest_exit_date": "2026-11-09",
          "same_signal_valid_until": "2026-10-13",
          "availability": "outside_original_entry_range"
        },
        "arithmetic_ref": "research/futures/weekly/2026-10-18/evidence/shared-sources/objects/ec72726d1dd2d82308f236fc8d3f2724192b1b206f1d9f42606711b83da4b14a",
        "entry_window_state": "expired"
      },
      "registered_at": "2026-10-11T18:14:54+08:00",
      "trade_date": "2026-11-20",
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "Original entry disposition is settled; actual holding/fill/effective stop unknown, current public gaps remain.",
      "signal": "triggered",
      "signal_evidence_refs": [
        "SHARED"
      ],
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "SHARED",
        "OLDPATH",
        "CAL",
        "EVENT",
        "OTHER"
      ],
      "entry_window_state": "expired",
      "holding_review": "Original10/13 deadline expired;10/13 H3278 below3289. Original reachable10/12 conditional fills touch initial/tightened SL by10/20;20-day ceiling elapsed. No revival.",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
          "evidence_refs": [
            "CAL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
          "evidence_refs": [
            "OTHER"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "research",
            "next_action": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "details": "Original10/13 deadline expired;10/13 H3278 below3289. Original reachable10/12 conditional fills touch initial/tightened SL by10/20;20-day ceiling elapsed. No revival.",
          "evidence_refs": [
            "SHARED",
            "OLDPATH"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
          "evidence_refs": [
            "EVENT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261015-M2701-trend-short-v3",
      "opportunity_id": "20261015-observe-M2701-trend-short-v3",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": "2026-10-15",
        "valid_until": "2026-10-19",
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "registered_at": "2026-10-15T19:30:56+08:00",
        "entry_window_state": "cancelled_and_expired",
        "entry_quote_status": "historical_only"
      },
      "registered_at": "2026-10-15T19:30:56+08:00",
      "trade_date": "2026-11-20",
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "Original entry disposition is settled; actual holding/fill/effective stop unknown, current public gaps remain.",
      "signal": "triggered",
      "signal_evidence_refs": [
        "SHARED"
      ],
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "SHARED",
        "OLDPATH",
        "CAL",
        "EVENT",
        "MRB"
      ],
      "entry_window_state": "cancelled_and_expired",
      "holding_review": "Original10/15 19:30:56 clock retained;10/16 quote moved outside3292–3326 and entry cancelled;10/19 expired.3310/3410 only historical diagnostic.",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
          "evidence_refs": [
            "CAL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
          "evidence_refs": [
            "MRB"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "research",
            "next_action": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "details": "Original10/15 19:30:56 clock retained;10/16 quote moved outside3292–3326 and entry cancelled;10/19 expired.3310/3410 only historical diagnostic.",
          "evidence_refs": [
            "SHARED",
            "OLDPATH"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
          "evidence_refs": [
            "EVENT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-RB2701-trend-short-v3",
      "opportunity_id": "20261025-observe-RB2701-trend-short-v3",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "plan": {
        "entry": 3047,
        "stop": 3103,
        "targets": null,
        "entry_range": [
          3034,
          3050
        ],
        "signal_date": "2026-10-23",
        "valid_until": "2026-10-27",
        "entry_date": "2026-10-26",
        "latest_exit_date": "2026-11-20",
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "registered_at": "2026-10-25T01:06:50.045735+08:00",
        "earliest_future_execution_at": "2026-10-26T09:00:00+08:00",
        "alternate_entry": {
          "entry_date": "2026-10-27",
          "latest_exit_date": "2026-11-23",
          "same_signal_valid_until": "2026-10-27",
          "original_reference_quote_reachable": false,
          "daily_range_intersection": [
            3034,
            3044
          ]
        },
        "round_trip_fee_budget": 20,
        "round_trip_slippage_budget": 20,
        "cost_basis": "research cost budget, not actual broker fee; revalidate actual fill and costs",
        "arithmetic_ref": "research/futures/weekly/2026-11-01/evidence/shared-sources/objects/5ca506b6db3213a317f866c2bb615cdf95d91b12aad56a6c77752a97584fc297.blob",
        "entry_window_state": "expired",
        "entry_quote_status": "historical_only"
      },
      "registered_at": "2026-10-25T01:06:50.045735+08:00",
      "trade_date": "2026-11-20",
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "Original entry disposition is settled; actual holding/fill/effective stop unknown, current public gaps remain.",
      "signal": "triggered",
      "signal_evidence_refs": [
        "SHARED"
      ],
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "SHARED",
        "OLDPATH",
        "CAL",
        "EVENT",
        "MRB"
      ],
      "entry_window_state": "expired",
      "holding_review": "Original10/27 deadline expired.10/26 path20th day11/20 elapsed;10/27 reachable3034–3044 alternative20th day11/23. Through11/20 no conditional price-stop touch, next-session reference3051 only for surviving10/27 path, actual fill/SL/exit unknown.",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
          "evidence_refs": [
            "CAL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
          "evidence_refs": [
            "MRB"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "research",
            "next_action": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "details": "Original10/27 deadline expired.10/26 path20th day11/20 elapsed;10/27 reachable3034–3044 alternative20th day11/23. Through11/20 no conditional price-stop touch, next-session reference3051 only for surviving10/27 path, actual fill/SL/exit unknown.",
          "evidence_refs": [
            "SHARED",
            "OLDPATH"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
          "evidence_refs": [
            "EVENT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261113-SR2701-trend-short-v3",
      "opportunity_id": "20261113-observe-SR2701-trend-short-v3",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": "2026-11-13",
        "valid_until": "2026-11-17",
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "registered_at": "2026-11-15T01:17:47.773776+08:00",
        "registration_scope": "research_observation_and_entry_disposition_only_no_execution_plan",
        "entry_window_state": "cancelled_quote_lost_breakout_and_expired"
      },
      "registered_at": "2026-11-15T01:17:47.773776+08:00",
      "trade_date": "2026-11-20",
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "Original entry disposition is settled; actual holding/fill/effective stop unknown, current public gaps remain.",
      "signal": "triggered",
      "signal_evidence_refs": [
        "SHARED"
      ],
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "SHARED",
        "OLDPATH",
        "CAL",
        "EVENT",
        "OTHER"
      ],
      "entry_window_state": "cancelled_quote_lost_breakout_and_expired",
      "holding_review": "Original11/13 signal cancelled_quote_lost_breakout on11/15; original11/17 deadline elapsed. Null entry/stop remain null; no re-registration or extension.",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
          "evidence_refs": [
            "CAL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify precise applicable venue/account exit boundary; MA/SR API1/14 versus rule-derived1/15 unresolved. Current dated calendar known, no actual position inferred.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
          "evidence_refs": [
            "OTHER"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "research",
            "next_action": "Review any actual holding thesis and current independent evidence; historical trigger cannot create new entry permission.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "details": "Original11/13 signal cancelled_quote_lost_breakout on11/15; original11/17 deadline elapsed. Null entry/stop remain null; no re-registration or extension.",
          "evidence_refs": [
            "SHARED",
            "OLDPATH"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
          "evidence_refs": [
            "EVENT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Current applicable risk notices read; obtain actual live quote/effective exit order and adverse gap scenario, temporary sessions and stricter rules before any management execution.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Verify today account equity, positions/orders, real Entry/SL, broker margin/fees and limits.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "With verified account run size-v3 and all applicable hard capacities; final_lots remains null.",
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-CF2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "CF2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract 61-bar price screen; later gates not evaluated after no signal.",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-CF2701"
      ],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "no_signal",
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
      "evidence_refs": [
        "PRICE-CF2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "close15455.0 inside [15030.0,15885.0], neither strict direction triggers. Independent economic subcondition not claimed passed.",
          "evidence_refs": [
            "PRICE-CF2701"
          ]
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-M2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract 61-bar price screen; later gates not evaluated after no signal.",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-M2701"
      ],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "no_signal",
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
      "evidence_refs": [
        "PRICE-M2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "close3071.0 inside [3041.0,3286.0], neither strict direction triggers. Independent economic subcondition not claimed passed.",
          "evidence_refs": [
            "PRICE-M2701"
          ]
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-MA2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract 61-bar price screen; later gates not evaluated after no signal.",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-MA2701"
      ],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "no_signal",
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
      "evidence_refs": [
        "PRICE-MA2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "close3073.0 inside [3014.0,3615.0], neither strict direction triggers. Independent economic subcondition not claimed passed.",
          "evidence_refs": [
            "PRICE-MA2701"
          ]
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-RB2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract 61-bar price screen; later gates not evaluated after no signal.",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-RB2701"
      ],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "no_signal",
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
      "evidence_refs": [
        "PRICE-RB2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "close2999.0 inside [2955.0,3072.0], neither strict direction triggers. Independent economic subcondition not claimed passed.",
          "evidence_refs": [
            "PRICE-RB2701"
          ]
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-SR2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract 61-bar price screen; later gates not evaluated after no signal.",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-SR2701"
      ],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "no_signal",
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
      "evidence_refs": [
        "PRICE-SR2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "close5056.0 inside [5015.0,5400.0], neither strict direction triggers. Independent economic subcondition not claimed passed.",
          "evidence_refs": [
            "PRICE-SR2701"
          ]
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-MA2701-MA2705-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "Exact ordered pair settlement raw material available; defensible frozen economic band/5–20 day convergence missing.",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "incomplete",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": null
      },
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "ANCHORS",
        "CAL",
        "EVENT"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Verify both leg liquidity and exact delivery/exit restrictions.",
          "evidence_refs": [
            "CAL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify both leg liquidity and exact delivery/exit restrictions.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Freeze defensible ordered-pair economic band, independent mechanism and original timing before a future signal.",
          "evidence_refs": [
            "ANCHORS"
          ],
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "Freeze defensible ordered-pair economic band, independent mechanism and original timing before a future signal.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "After anchor form entire-range netR>=2.5 plan, economic stop, costs and dated exit.",
          "evidence_refs": [
            "ANCHORS"
          ],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "After anchor form entire-range netR>=2.5 plan, economic stop, costs and dated exit.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "Verify synchronous leg quotes, total slippage, naked-leg incident and gap/event scenarios.",
          "evidence_refs": [
            "EVENT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify synchronous leg quotes, total slippage, naked-leg incident and gap/event scenarios.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Verify current account and all hard capacities.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Verify current account and all hard capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "With verified account run size-v3 including applicable stress capacities.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "With verified account run size-v3 including applicable stress capacities.",
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-RB2701-RB2703-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "Exact ordered pair settlement raw material available; defensible frozen economic band/5–20 day convergence missing.",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "incomplete",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": null
      },
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "ANCHORS",
        "CAL",
        "EVENT"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Verify both leg liquidity and exact delivery/exit restrictions.",
          "evidence_refs": [
            "CAL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify both leg liquidity and exact delivery/exit restrictions.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Freeze defensible ordered-pair economic band, independent mechanism and original timing before a future signal.",
          "evidence_refs": [
            "ANCHORS"
          ],
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "Freeze defensible ordered-pair economic band, independent mechanism and original timing before a future signal.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "After anchor form entire-range netR>=2.5 plan, economic stop, costs and dated exit.",
          "evidence_refs": [
            "ANCHORS"
          ],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "After anchor form entire-range netR>=2.5 plan, economic stop, costs and dated exit.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "Verify synchronous leg quotes, total slippage, naked-leg incident and gap/event scenarios.",
          "evidence_refs": [
            "EVENT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify synchronous leg quotes, total slippage, naked-leg incident and gap/event scenarios.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Verify current account and all hard capacities.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Verify current account and all hard capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "With verified account run size-v3 including applicable stress capacities.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "With verified account run size-v3 including applicable stress capacities.",
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261120-SR2701-SR2705-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-20",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "Exact ordered pair settlement raw material available; defensible frozen economic band/5–20 day convergence missing.",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-22T01:06:05.803438+08:00",
      "status": "incomplete",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "exit_rule": null
      },
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "ANCHORS",
        "CAL",
        "EVENT"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "Verify both leg liquidity and exact delivery/exit restrictions.",
          "evidence_refs": [
            "CAL"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify both leg liquidity and exact delivery/exit restrictions.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "Freeze defensible ordered-pair economic band, independent mechanism and original timing before a future signal.",
          "evidence_refs": [
            "ANCHORS"
          ],
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "Freeze defensible ordered-pair economic band, independent mechanism and original timing before a future signal.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "After anchor form entire-range netR>=2.5 plan, economic stop, costs and dated exit.",
          "evidence_refs": [
            "ANCHORS"
          ],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "After anchor form entire-range netR>=2.5 plan, economic stop, costs and dated exit.",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "Verify synchronous leg quotes, total slippage, naked-leg incident and gap/event scenarios.",
          "evidence_refs": [
            "EVENT"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "Verify synchronous leg quotes, total slippage, naked-leg incident and gap/event scenarios.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "Verify current account and all hard capacities.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "Verify current account and all hard capacities.",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "With verified account run size-v3 including applicable stress capacities.",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "With verified account run size-v3 including applicable stress capacities.",
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
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    }
  ],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "MA-ALT-OLD",
      "reason": "Inherited11/15 withdrawal retained; original alternate10/13 not reachable, no widening.",
      "recalculation": "completed",
      "affected_checks": [
        {
          "candidate_id": "20261009-MA2701-trend-long-v3",
          "rule_id": "G3"
        }
      ],
      "classification": "inherited_reassessment_no_new_error"
    },
    {
      "withdrawn_evidence_id": "RB-ALT-OLD",
      "reason": "Inherited11/15 withdrawal retained;10/27 3047 unavailable, only3034–3044 conditional prices.",
      "recalculation": "completed",
      "affected_checks": [
        {
          "candidate_id": "20261023-RB2701-trend-short-v3",
          "rule_id": "G3"
        }
      ],
      "classification": "inherited_reassessment_no_new_error"
    },
    {
      "withdrawn_evidence_id": "RB-WINDOW-OLD",
      "reason": "Inherited11/08 withdrawal retained; original entry deadline10/27 stays expired.",
      "recalculation": "completed",
      "affected_checks": [
        {
          "candidate_id": "20261023-RB2701-trend-short-v3",
          "rule_id": "G3"
        }
      ],
      "classification": "inherited_reassessment_no_new_error"
    }
  ],
  "unresolved_items": [
    {
      "item": "If actual RB original alternative position exists, verify real10/27 fill/effectiveSL and exit no later11/23, earlier stop/logic/rule prevails.10/26 time limit already elapsed.",
      "owner": "research",
      "due_at": "before_execution",
      "required_evidence": [
        "OLDPATH",
        "EVENT"
      ],
      "resolution": "conditional_account_unknown"
    },
    {
      "item": "Maintain MA/RB/SR future-applicable V anchors only after economic bands and mechanism evidence; no synthetic historical anchor.",
      "owner": "research",
      "due_at": "next_report",
      "required_evidence": [
        "ANCHORS"
      ],
      "resolution": "pending"
    }
  ],
  "shadow_plans": []
}
```
