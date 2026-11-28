# 期货执行审计 · 2026-11-29

current_framework v3.0，原方法基线 e54d933c1197c0ee2324087defab402df38dc231。依次复核四个原机会、五个当根T和三个当前V。四项旧案入场时钟全部结束，RB旧空条件时间退出已过。RB新多仅为观察，G4压力情景超线，G5/G6未知，因此incomplete；其余四个当根T均no_signal，三个当前V缺经济锚。账户、真实仓位、退出和收益未知。完整存量事件、反证与价格路径见[市场周报](2026-11-29-market-research.md)，压力和两种退出日限制见[研究验算](evidence/rb-observation.json)。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-11-29",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
  "execution_permission": "not_evaluated",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "e54d933c1197c0ee2324087defab402df38dc231"
  },
  "snapshot": {
    "market_trade_date": "2026-11-27",
    "market_captured_at": "2026-11-29T01:05:29.249564+08:00",
    "source_artifacts": [
      "research/futures/refresh/2026-11-29/2026-11-29-signal-refresh.json",
      "research/futures/weekly/2026-11-29/evidence/continuity-review.json",
      "research/futures/weekly/2026-11-29/evidence/ordered-pairs.json",
      "research/futures/weekly/2026-11-29/evidence/rb-contract-calendar.json",
      "research/futures/weekly/2026-11-29/evidence/rb-observation.json",
      "research/futures/weekly/2026-11-29/evidence/venue-checks.json",
      "research/futures/weekly/2026-11-29/evidence/venue-sources.json",
      "research/futures/weekly/2026-11-29/evidence/public-readings.md",
      "research/futures/weekly/2026-11-29/evidence/industry-http.json",
      "research/futures/anchors/2026-11-29/2026-11-29-anchors.json"
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
      "2 roll-preparation pairs raw coverage",
      "50 contract-days public parameters",
      "1 new RB long observation; stress gate failed"
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
      "metric": "SHARED",
      "value": "20条共享采纳、25组纠错、1个M原时钟冲突",
      "unit": "record",
      "observation_date": "2026-11-29",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/continuity-review.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "OLDPATH",
      "metric": "OLDPATH",
      "value": "四案历史路径及11/20前原证据",
      "unit": "record",
      "observation_date": "2026-11-22",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/historical-path-source.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "historical"
    },
    {
      "evidence_id": "CAL",
      "metric": "CAL",
      "value": "上期所日期、RB2701终止及逐日成交量，20日均量762715.25",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/rb-contract-calendar.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "EVENT",
      "metric": "EVENT",
      "value": "市场风控提醒、做市合约和旧糖仓单到期；相应适用范围见摘记",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/public-readings.md",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MRB",
      "metric": "MRB",
      "value": "RB产量189.04、表需191.16、厂库增5.32万吨。M压榨增30.57万吨。",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/public-readings.md",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "OTHER",
      "metric": "OTHER",
      "value": "MA港库52.60万吨；SR旧年度仓单11/30到期；CF注册68张、预报388张",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/public-readings.md",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ANCHORS",
      "metric": "ANCHORS",
      "value": "三当前和两准备对，无冻结经济区间，撤回清单空。",
      "unit": "record",
      "observation_date": "2026-11-29",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/anchors/2026-11-29/2026-11-29-anchors.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "RBPATH",
      "metric": "RBPATH",
      "value": "11/23 H3008 L2980 C3004，早于11/27新信号",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/rb-contract-calendar.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "STRESS",
      "metric": "STRESS",
      "value": "参考3083、SL3020、670元/手；下板2919情景1680元/手，2.507倍。",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-29/evidence/rb-observation.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-CF2701",
      "metric": "PRICE-CF2701",
      "value": "CF2701 收盘15555.0，前20日低高 15030.0 / 15640.0",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-29/2026-11-29-signal-refresh.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-M2701",
      "metric": "PRICE-M2701",
      "value": "M2701 收盘3183.0，前20日低高 3041.0 / 3204.0",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-29/2026-11-29-signal-refresh.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-MA2701",
      "metric": "PRICE-MA2701",
      "value": "MA2701 收盘3126.0，前20日低高 2955.0 / 3615.0",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-29/2026-11-29-signal-refresh.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-RB2701",
      "metric": "PRICE-RB2701",
      "value": "RB2701 收盘3077.0，前20日低高 2955.0 / 3075.0",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-29/2026-11-29-signal-refresh.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
      "price_basis": "exact_contract_close_or_declared_historical_plan",
      "comparison_basis": "same contract/sample/date only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-SR2701",
      "metric": "PRICE-SR2701",
      "value": "SR2701 收盘5217.0，前20日低高 5007.0 / 5285.0",
      "unit": "record",
      "observation_date": "2026-11-27",
      "published_at": "2026-11-29T01:10:52.509006+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-29/2026-11-29-signal-refresh.json",
      "original_source": "来源见冻结文件。published_at为本地证据登记时点；外部观察日与首次发布日期另列。",
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
      "published_at": "2026-11-22T01:06:18.091729+08:00",
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
      "published_at": "2026-11-22T01:06:18.091729+08:00",
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
      "published_at": "2026-11-22T01:06:18.091729+08:00",
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
      "trade_date": "2026-11-27",
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
      "holding_review": "10/13截止。10/13最高3278低于原带下沿3289；若10/12依原案入场，10/20已触及止损边界，11/06及备选11/09时间界均已过。港库续增与需求开工回升方向相反，原G2撤回继续。",
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
          "details": "10/13截止。10/13最高3278低于原带下沿3289；若10/12依原案入场，10/20已触及止损边界，11/06及备选11/09时间界均已过。港库续增与需求开工回升方向相反，原G2撤回继续。",
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
      "trade_date": "2026-11-27",
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
      "holding_review": "10/16跌出3292–3326，取消；原10/19截止。历史空登记与当日晚间登记的冲突见接续底稿。压榨恢复与上期去库并存，旧诊断价不能用作真实Entry或SL。",
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
          "details": "10/16跌出3292–3326，取消；原10/19截止。历史空登记与当日晚间登记的冲突见接续底稿。压榨恢复与上期去库并存，旧诊断价不能用作真实Entry或SL。",
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
      "trade_date": "2026-11-27",
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
        "MRB",
        "RBPATH"
      ],
      "entry_window_state": "expired",
      "holding_review": "10/26假设路径的第20日为11/20。10/27备选入场只有3034–3044可达，第20日11/23：当日高3008低2980收3004，低于上场收盘确定的短仓参考止损3051；即使此前始终未触真实止损，也应在11/23收盘前依时退出。无真实成交回单。",
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
          "details": "10/26假设路径的第20日为11/20。10/27备选入场只有3034–3044可达，第20日11/23：当日高3008低2980收3004，低于上场收盘确定的短仓参考止损3051；即使此前始终未触真实止损，也应在11/23收盘前依时退出。无真实成交回单。",
          "evidence_refs": [
            "SHARED",
            "OLDPATH",
            "RBPATH"
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
      "trade_date": "2026-11-27",
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
      "holding_review": "报价已失去原严格突破，原11/17截止。新糖开榨、陈糖出库与11/30旧年度仓单到期均不能恢复原入场；当时未登记可执行Entry/SL。",
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
          "details": "报价已失去原严格突破，原11/17截止。新糖开榨、陈糖出库与11/30旧年度仓单到期均不能恢复原入场；当时未登记可执行Entry/SL。",
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
      "candidate_id": "20261127-CF2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-27",
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
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
          "details": "15555.0介于前20低15030.0与高15640.0之间；无严格收盘突破。",
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
      "candidate_id": "20261127-M2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-27",
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
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
          "details": "3183.0介于前20低3041.0与高3204.0之间；无严格收盘突破。",
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
      "candidate_id": "20261127-MA2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-27",
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
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
          "details": "3126.0介于前20低2955.0与高3615.0之间；无严格收盘突破。",
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
      "candidate_id": "20261127-RB2701-trend-long-v3",
      "opportunity_id": "20261127-observe-RB2701-trend-long-v3",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "long",
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": "2026-11-27",
        "valid_until": "2026-12-01",
        "latest_exit_date": null,
        "exit_rule": "initial_2atr_and_prior10_channel_tighten_only_max20_sessions",
        "registered_at": "2026-11-29T01:10:52.509006+08:00",
        "registration_scope": "research_observation_only",
        "entry_window_state": "do_not_enter_stress_limit"
      },
      "registered_at": "2026-11-29T01:10:52.509006+08:00",
      "trade_date": "2026-11-27",
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "已冻结公开诊断；压力情景超过淘汰线，账户与未来盘口未知。",
      "signal": "triggered",
      "signal_evidence_refs": [
        "PRICE-RB2701"
      ],
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "CAL",
        "MRB",
        "PRICE-RB2701",
        "STRESS",
        "EVENT"
      ],
      "entry_window_state": "do_not_enter_stress_limit",
      "holding_review": "新信号仅登记研究观察。",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "pass",
          "details": "RB终止日2027/01/15，12/17为距终止日20交易日边界。20日均量762715.25手。盘口深度另归执行门。",
          "evidence_refs": [
            "CAL"
          ]
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "pass",
          "details": "正式收盘突破；表需和去库提供弱支持，增产及厂库增加构成分歧，单一market_risk=0.5。",
          "evidence_refs": [
            "PRICE-RB2701",
            "MRB"
          ]
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "pass",
          "details": "诊断价3083在3076–3092；SL3020、风险670元；若可成案两日的更早退出均12/17。无执行计划。",
          "evidence_refs": [
            "STRESS",
            "CAL"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "fail",
          "details": "采用本次脆弱突破的下板压力价2919，1680/670=2.51超2.0，不新开。夜盘末价仅供诊断，登记时休市，未来盘口/费用未知。",
          "evidence_refs": [
            "STRESS",
            "EVENT"
          ]
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "须核当日真实账户、资金、仓位和挂单。",
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
          "details": "账户与已占风险未知，最终容量和手数null。",
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
        "G4"
      ],
      "unknown_checks": [
        "G5",
        "G6"
      ],
      "first_blocker": "G4",
      "only_blocker": null,
      "final_lots": null,
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "diagnostic_plan_ref": "research/futures/weekly/2026-11-29/evidence/rb-observation.json"
    },
    {
      "candidate_id": "20261127-SR2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-27",
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
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
          "details": "5217.0介于前20低5007.0与高5285.0之间；无严格收盘突破。",
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
      "candidate_id": "20261127-MA2701-MA2705-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-27",
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
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
      "candidate_id": "20261127-RB2701-RB2703-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-27",
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
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
      "candidate_id": "20261127-SR2701-SR2705-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-27",
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
      "evaluated_at": "2026-11-29T01:10:52.509006+08:00",
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
      "item": "如有实际存量，核原始成交、有效SL及退出。RB原两个时间界均已过，本期新方向压力超线。",
      "owner": "research",
      "due_at": "before_execution",
      "required_evidence": [
        "RBPATH",
        "STRESS"
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
