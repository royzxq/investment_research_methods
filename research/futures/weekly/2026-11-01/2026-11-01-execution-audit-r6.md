# 期货执行审计 · 2026-11-01

generator=codex；public_data；current_framework v3.0。实际main基线72afd743，完整方法/依赖哈希见[基线](evidence/run-baseline.json)。行情10/30、真实API v1.18.1；账户及成交全部未知。先复核存量，再筛五T/三V；本期没有可用新入场案，不能据此推断市场零机会或账户空仓。

## 覆盖、原时钟与条件管理

| 原对象 | 入场用途 | 若有实际持仓的管理 |
|---|---|---|
| MA 20261011-observe-MA2701-trend-long-v3 | 原10/09信号、10/11 18:14:54登记、10/13截止，已到期 | 原参考SL3139在10/19穿越，原带所有初始SL最迟10/20穿越；反弹不能复活。真实退出未知；11/06或11/09原时间上限保留，不覆盖更早止损 |
| M 20261015-observe-M2701-trend-short-v3 | 原10/15信号、19:30:56真实补登记、10/19截止；10/16越带取消 | 无已核数值执行案；3310/3410诊断不当真实成交。若有实仓按真实Entry/有效SL/费用与事件复核 |
| RB 20261025-observe-RB2701-trend-short-v3 | 原10/23信号、10/25 01:06:50.045735登记、10/27截止，已到期 | 原参考3047/SL3103，假设10/26入场，10/26收盘计算下场3099、10/27收盘下场3096，此后至10/30不放宽。参考本周未穿不等于实际未止损；11/20或11/23取真实入场日及更早边界 |

以上不是持仓事实。MA跨周末单仓约束、相关事件/提保后的压力、全部挂单及已有风险仍按canonical；实际Entry、收紧SL、是否触发可成交/已退及盈亏保持null。RB表需回升和继续去库是原空最强反证，不能继续用“表需下降”作本周事实；产量回升/现货弱提供相反支持，当前研究分歧一次market_risk0.5。MA旧G2 pass撤回仍有效，低库与MTO需求退出/国产提升分歧不恢复旧pass。

## 最新筛选与本周监测边界

10/30五T均not_triggered，分别仅对该根no_signal；V无合格事前数值锚，未评估，三当前对原料完整，MA准备对另缺33日远腿，不能写no_signal。见[逐日重算和来源身份](evidence/weekly-mechanical-review.json)、[独立复核](evidence/independent-audit-review.md)。

10/27 MA long、M/SR/CF short四个历史机械触发的原窗10/28–29现expired；没有当日登记证据，不补ID或成交。10/29 M short(close3161<原L203175)，原窗10/30、11/02；诊断原带3138–3174。10/30 close3183虽距信号22小于0.5ATR23.9565，仍失突破侧并越带，取消入场用途，不等回价复活。没有从本周价格表现追认建议/收益，也没有给已取消信号新注册计划。本轮不存在10/26–30共享日频采纳，不声称全周已监测。

## 公开参数、事件与剩余缺口

本期实际读公开经纪商转引表：RB交易所7%/板5%，M7%/板6%，MA2612–2701 9%/板8%；用户实收与动态更高规则未知。MA10/26提保生效后不凭时间自行解除，按真实仓位/实收取严。MA2027最后交易日原API01/14与旧推01/15冲突，官方仅确认交割月第10交易日，未核2027官方日历不选更晚日期。SSE真实日期代理和SHFE年度休市/场次核验分报，[日历说明](evidence/calendar-review.md)。USDA下次WASDE及M相关映射、各品种支持反证见两份产业底稿；RB不自动套M事件窗。事件/实时压力和账户不足均保留unknown。

三V已推进实际仓储/进出库/仓单规则和供给研究，单侧成本不能复制为对称锚，锚维护[正式记录](../../anchors/2026-11-01/2026-11-01-anchors.json)；无现有有效锚待撤，withdrawals为空；11/06补月份费用/交割可实现性及收敛机制。

## 接续、审计与验证

main确切10/25采纳与11条共享来源均冻结；16组纠错含同源重复，作用域逐条复核，[原钟裁决](evidence/continuity-reconciliation-r2.json)保留M冲突，不修改原件。首次当前根共享capture明确失败，后核原件/方法兼容并从冻结源幂等命中原39d1；遗漏可选anchors所成510252重复入口保留且不增加经济证据权重。来源图以不可变blob保存，历史原路径只作溯源，避免历史compact hash被错配到当前文件。

本期状态刷新yes；新增证据纠错no（历史撤回继续执行）；方法变更no，update_needed=no。完整审计11条：五条当前no_signal、三条原计划及三条V为incomplete，所有final_lots=null。未做size-v3伪空仓计算；无成交/收益检验。验证回执见[evidence/validation-r2.json](evidence/validation-r2.json)。

本修订r2显式采用M/RB底稿r2，纠正未采纳初稿中short失效比较方向的歧义，并把MA到期冲突只归MA候选；原审计与底稿保留。本期没有对既有已采纳事实新增撤回，不据此改方法。

```json
{
  "audit_schema_version": 3,
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "snapshot": {
    "market_trade_date": "2026-10-30",
    "market_captured_at": "2026-11-01T01:00:46.944347+08:00",
    "source_artifacts": [
      "research/futures/refresh/2026-11-01/2026-11-01-signal-refresh-r3.json",
      "research/futures/refresh/2026-11-01/evidence/2026-11-01-signal-refresh-r2/market-inputs.json",
      "research/futures/weekly/2026-11-01/evidence/shared-sources/catalog-r2.json",
      "research/futures/weekly/2026-11-01/evidence/weekly-mechanical-review.json"
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
      "all known MA/M/RB original plans and conditional holdings",
      "five exact-contract latest T screens and intraweek mechanical reconstruction",
      "M/RB priority current industrial routes",
      "three current V and two preparation pair raw checks"
    ],
    "missing_scope": [
      "actual account/fills/effective stops",
      "venue temporary rules/real-time quotes and exact2027 MA expiry"
    ],
    "research_only_scope": [
      "three month-specific numerical V anchors"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "as_of_date": "2026-11-01",
  "evaluated_at": "2026-11-01T01:06:24.913824+08:00",
  "generator": "codex",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "72afd7430cbb99feb13521740f4929e20a647fd2"
  },
  "evidence": [
    {
      "evidence_id": "PRICE-CF2701",
      "metric": "strict prior20 / fixed61 ATR calculation",
      "value": {
        "signal_close": 15315.0,
        "prior20_high": 16130.0,
        "prior20_low": 15055.0,
        "atr20": 217.73256887000986,
        "volatility_ratio": 1.194606804740876,
        "signal": "not_triggered"
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-10-30",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-01/2026-11-01-signal-refresh-r3.json",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "PRICE-M2701",
      "metric": "strict prior20 / fixed61 ATR calculation",
      "value": {
        "signal_close": 3183.0,
        "prior20_high": 3426.0,
        "prior20_low": 3158.0,
        "atr20": 47.88288083404548,
        "volatility_ratio": 0.9394939397318839,
        "signal": "not_triggered"
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-10-30",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-01/2026-11-01-signal-refresh-r3.json",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "PRICE-MA2701",
      "metric": "strict prior20 / fixed61 ATR calculation",
      "value": {
        "signal_close": 3480.0,
        "prior20_high": 3486.0,
        "prior20_low": 2838.0,
        "atr20": 115.30874715821601,
        "volatility_ratio": 1.1542354500827428,
        "signal": "not_triggered"
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-10-30",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-01/2026-11-01-signal-refresh-r3.json",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "PRICE-RB2701",
      "metric": "strict prior20 / fixed61 ATR calculation",
      "value": {
        "signal_close": 3030.0,
        "prior20_high": 3131.0,
        "prior20_low": 3012.0,
        "atr20": 27.785293318819917,
        "volatility_ratio": 0.9309037336936753,
        "signal": "not_triggered"
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-10-30",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-01/2026-11-01-signal-refresh-r3.json",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "PRICE-SR2701",
      "metric": "strict prior20 / fixed61 ATR calculation",
      "value": {
        "signal_close": 5263.0,
        "prior20_high": 5563.0,
        "prior20_low": 5236.0,
        "atr20": 53.56637860150096,
        "volatility_ratio": 1.2309167468242463,
        "signal": "not_triggered"
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-10-30",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-01/2026-11-01-signal-refresh-r3.json",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "ORIGINAL-SOURCES",
      "metric": "immutable shared source graph and main resolutions",
      "value": "11 entries,16 correction groups; one original clock conflict explicitly reconciled",
      "unit": "provenance",
      "observation_date": "2026-11-01",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-01/evidence/shared-sources/catalog-r2.json",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "HOLDING-REVIEW",
      "metric": "source-backed original clocks, conditional stop paths and intraweek triggers",
      "value": "MA reference stopped conditionally; RB reference not crossed, true position unknown; M cancelled",
      "unit": "conditional paths",
      "observation_date": "2026-11-01",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-01/evidence/independent-audit-review.md",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "M-RB-ECON",
      "metric": "current independent industrial support and strongest counterevidence",
      "value": "See public original/credible transfer ledgers",
      "unit": "source-specific",
      "observation_date": "2026-10-30",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-01/evidence/m-rb-research-r2.md",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "MA-SR-CF-ECON",
      "metric": "current independent industrial support and strongest counterevidence",
      "value": "See public original/credible transfer ledgers; CF unlabeled table not upgraded to national tonnes",
      "unit": "source-specific",
      "observation_date": "2026-10-30",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-01/evidence/ma-sr-cf-research.md",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    },
    {
      "evidence_id": "CURRENT-CALENDAR",
      "metric": "actual dated API with venue annual holiday crosscheck",
      "value": "SSE proxy disclosed; SHFE annual holidays read, temporary venue sessions unknown",
      "unit": "dates",
      "observation_date": "2026-11-01",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-01/evidence/calendar-review.md",
      "original_source": "See cited frozen original and reading ledger; local timestamp is not original publication time",
      "price_basis": "close/high/low or specifically stated economic metric",
      "comparison_basis": "same contract, period and named source; no mixed samples",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence capture timestamp; original publication date separately stated in ledger"
    }
  ],
  "candidates": [
    {
      "candidate_id": "20261030-CF2701-trend-screen-v3",
      "opportunity_id": null,
      "contracts": [
        "CF2701"
      ],
      "trade_date": "2026-10-30",
      "strategy": "trend",
      "direction": "unknown",
      "signal": "not_triggered",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract61-day price inputs; this price early stop is not a full execution review",
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
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "signal_evidence_refs": [
        "PRICE-CF2701"
      ],
      "evidence_refs": [
        "PRICE-CF2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "10/30 close在严格前20完整日通道内。只表示最新一根价格未触发；本周历史触发/原计划另核。",
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
      "execution_permission": "not_evaluated",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00"
    },
    {
      "candidate_id": "20261030-M2701-trend-screen-v3",
      "opportunity_id": null,
      "contracts": [
        "M2701"
      ],
      "trade_date": "2026-10-30",
      "strategy": "trend",
      "direction": "unknown",
      "signal": "not_triggered",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract61-day price inputs; this price early stop is not a full execution review",
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
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "signal_evidence_refs": [
        "PRICE-M2701"
      ],
      "evidence_refs": [
        "PRICE-M2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "10/30 close在严格前20完整日通道内。只表示最新一根价格未触发；本周历史触发/原计划另核。",
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
      "execution_permission": "not_evaluated",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00"
    },
    {
      "candidate_id": "20261030-MA2701-trend-screen-v3",
      "opportunity_id": null,
      "contracts": [
        "MA2701"
      ],
      "trade_date": "2026-10-30",
      "strategy": "trend",
      "direction": "unknown",
      "signal": "not_triggered",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract61-day price inputs; this price early stop is not a full execution review",
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
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "signal_evidence_refs": [
        "PRICE-MA2701"
      ],
      "evidence_refs": [
        "PRICE-MA2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "10/30 close在严格前20完整日通道内。只表示最新一根价格未触发；本周历史触发/原计划另核。",
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
      "execution_permission": "not_evaluated",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00"
    },
    {
      "candidate_id": "20261030-RB2701-trend-screen-v3",
      "opportunity_id": null,
      "contracts": [
        "RB2701"
      ],
      "trade_date": "2026-10-30",
      "strategy": "trend",
      "direction": "unknown",
      "signal": "not_triggered",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract61-day price inputs; this price early stop is not a full execution review",
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
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "signal_evidence_refs": [
        "PRICE-RB2701"
      ],
      "evidence_refs": [
        "PRICE-RB2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "10/30 close在严格前20完整日通道内。只表示最新一根价格未触发；本周历史触发/原计划另核。",
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
      "execution_permission": "not_evaluated",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00"
    },
    {
      "candidate_id": "20261030-SR2701-trend-screen-v3",
      "opportunity_id": null,
      "contracts": [
        "SR2701"
      ],
      "trade_date": "2026-10-30",
      "strategy": "trend",
      "direction": "unknown",
      "signal": "not_triggered",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "Complete exact-contract61-day price inputs; this price early stop is not a full execution review",
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
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "signal_evidence_refs": [
        "PRICE-SR2701"
      ],
      "evidence_refs": [
        "PRICE-SR2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "details": "10/30 close在严格前20完整日通道内。只表示最新一根价格未触发；本周历史触发/原计划另核。",
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
      "execution_permission": "not_evaluated",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00"
    },
    {
      "candidate_id": "20261009-MA2701-trend-long-v3",
      "opportunity_id": "20261011-observe-MA2701-trend-long-v3",
      "trade_date": "2026-10-30",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "long",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "Original entry expired/cancelled; actual holdings/stop/fills/account and executable quote unknown; preserve historical numeric plan only",
      "signal": "triggered",
      "signal_evidence_refs": [
        "ORIGINAL-SOURCES"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "真实合约及原期限定性保留；若真实尚持仓，核当前可交易性/临时规则和更早经纪商边界，MA精确2027到期冲突仍缺官方日历。",
          "evidence_refs": [
            "CURRENT-CALENDAR"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "真实合约及原期限定性保留；若真实尚持仓，核当前可交易性/临时规则和更早经纪商边界，MA精确2027到期冲突仍缺官方日历。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "旧当前产业pass撤回继续有效；低港库支持与MTO全停/国产负荷升反证并存，不能恢复旧机会。",
          "evidence_refs": [
            "MA-SR-CF-ECON"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "旧当前产业pass撤回继续有效；低港库支持与MTO全停/国产负荷升反证并存，不能恢复旧机会。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "details": "原入场10/13到期；10/19穿原参考SL3139，10/20穿原范围所有初始SL；若沿原案未先退，应处理已触发退出。实际退出未知，反弹不复活。",
          "evidence_refs": [
            "ORIGINAL-SOURCES",
            "HOLDING-REVIEW"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "本期公开参数转引与公告已读，不能等同实时盘口/更严扩板跳空压力或用户实收；若有未平先核可成交退出与事件预案。",
          "evidence_refs": [
            "M-RB-ECON",
            "MA-SR-CF-ECON"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "本期公开参数转引与公告已读，不能等同实时盘口/更严扩板跳空压力或用户实收；若有未平先核可成交退出与事件预案。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "提供当日真实权益、全部持仓/挂单、有效SL、风险与实收保证金；未知不是空仓。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、全部持仓/挂单、有效SL、风险与实收保证金；未知不是空仓。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "按同一真实计划、账户、压力/执行/周末适用容量运行size-v3，最终手数未知保持null。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "按同一真实计划、账户、压力/执行/周末适用容量运行size-v3，最终手数未知保持null。",
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
        "arithmetic_ref": "research/futures/weekly/2026-10-18/evidence/shared-sources/objects/ec72726d1dd2d82308f236fc8d3f2724192b1b206f1d9f42606711b83da4b14a"
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "evidence_refs": [
        "ORIGINAL-SOURCES",
        "HOLDING-REVIEW",
        "PRICE-MA2701"
      ],
      "price_screening_date": "2026-10-23",
      "historical_price_screen": "original 2026-10-09 long price signal retained; 2026-10-15 new T signal not_triggered",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00",
      "registered_at": "2026-10-11T18:14:54+08:00",
      "risk_factors": {
        "strategy": 0.7,
        "market_risk": 0.5,
        "exchange_buffer": null,
        "market_risk_reason": "nonfatal economic disagreement/ongoing supply event; one factor only"
      },
      "entry_window_state": "expired",
      "actual_position_status": "unknown",
      "execution_permission": "not_evaluated",
      "not_evaluated_after_no_signal": [],
      "execution_state_inherited": false
    },
    {
      "candidate_id": "20261015-M2701-trend-short-v3",
      "opportunity_id": "20261015-observe-M2701-trend-short-v3",
      "trade_date": "2026-10-30",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "Original entry expired/cancelled; actual holdings/stop/fills/account and executable quote unknown; preserve historical numeric plan only",
      "signal": "triggered",
      "signal_evidence_refs": [
        "ORIGINAL-SOURCES"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "真实合约及原期限定性保留；若真实尚持仓，核当前可交易性/临时规则、公开合约及更早经纪商强制退出边界。",
          "evidence_refs": [
            "CURRENT-CALENDAR"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "真实合约及原期限定性保留；若真实尚持仓，核当前可交易性/临时规则、公开合约及更早经纪商强制退出边界。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "当前压榨/现货弱势与供给收缩/基差反证均须按真实持仓逻辑重评；旧无数值案，不继承旧pass。",
          "evidence_refs": [
            "M-RB-ECON"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "当前压榨/现货弱势与供给收缩/基差反证均须按真实持仓逻辑重评；旧无数值案，不继承旧pass。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "details": "原10/15信号、19:30:56登记、10/19截止保留；10/16原价格越界已取消。3310/3410只是旧诊断，不是成交或可执行计划。",
          "evidence_refs": [
            "ORIGINAL-SOURCES",
            "HOLDING-REVIEW"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "本期公开参数转引与公告已读，不能等同实时盘口/更严扩板跳空压力或用户实收；若有未平先核可成交退出与事件预案。",
          "evidence_refs": [
            "M-RB-ECON",
            "MA-SR-CF-ECON"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "本期公开参数转引与公告已读，不能等同实时盘口/更严扩板跳空压力或用户实收；若有未平先核可成交退出与事件预案。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "提供当日真实权益、全部持仓/挂单、有效SL、风险与实收保证金；未知不是空仓。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、全部持仓/挂单、有效SL、风险与实收保证金；未知不是空仓。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "按同一真实计划、账户、压力/执行/周末适用容量运行size-v3，最终手数未知保持null。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "按同一真实计划、账户、压力/执行/周末适用容量运行size-v3，最终手数未知保持null。",
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
        "ORIGINAL-SOURCES",
        "HOLDING-REVIEW",
        "PRICE-M2701"
      ],
      "price_screening_date": "2026-10-23",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00",
      "registered_at": "2026-10-15T19:30:56+08:00",
      "entry_window_state": "cancelled_and_expired",
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
      },
      "current_disposition": "Original 10/15 entry cancelled after 10/16 price deviation and now expired10/19; no restart. No verified fill or numeric active plan. If actual short exists, reconcile real Entry/stop and daily path; current last10 high3420 applies only next session and can only tighten.",
      "execution_permission": "not_evaluated",
      "execution_state_inherited": false
    },
    {
      "candidate_id": "20261023-RB2701-trend-short-v3",
      "opportunity_id": "20261025-observe-RB2701-trend-short-v3",
      "trade_date": "2026-10-30",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "Original entry expired/cancelled; actual holdings/stop/fills/account and executable quote unknown; preserve historical numeric plan only",
      "signal": "triggered",
      "signal_evidence_refs": [
        "ORIGINAL-SOURCES"
      ],
      "registered_at": "2026-10-25T01:06:50.045735+08:00",
      "entry_window_state": "remaining_window",
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
          "same_signal_valid_until": "2026-10-27"
        },
        "round_trip_fee_budget": 20,
        "round_trip_slippage_budget": 20,
        "cost_basis": "research cost budget, not actual broker fee; revalidate actual fill and costs",
        "arithmetic_ref": "research/futures/weekly/2026-11-01/evidence/shared-sources/objects/5ca506b6db3213a317f866c2bb615cdf95d91b12aad56a6c77752a97584fc297.blob"
      },
      "risk_factors": {
        "strategy": 0.7,
        "market_risk": 0.5,
        "market_risk_reason": "nonfatal conflict: residual demand falls but total rebar stocks still destock; HV20/HV60=.9102 not high",
        "exchange_buffer": null
      },
      "stress_review": {
        "adverse_price": 3140,
        "basis": "observed prior20 high as one adverse scenario, not worst case",
        "planned_loss": 600,
        "stressed_loss": 970,
        "gap_ratio": 1.6166666666666667,
        "light_review_line": 1.5,
        "reject_line": 2,
        "result": "above light line; absolute stress capacity and current limit/quote scenarios required; G4/G5/G6 remain unknown"
      },
      "evidence_refs": [
        "ORIGINAL-SOURCES",
        "HOLDING-REVIEW",
        "PRICE-RB2701"
      ],
      "not_evaluated_after_no_signal": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "真实合约及原期限定性保留；若真实尚持仓，核当前可交易性/临时规则、公开合约及更早经纪商强制退出边界。",
          "evidence_refs": [
            "CURRENT-CALENDAR"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "真实合约及原期限定性保留；若真实尚持仓，核当前可交易性/临时规则、公开合约及更早经纪商强制退出边界。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "pass",
          "details": "原10/23价格触发有源；当前同口径产量回升支持供给压力，而表需回升/继续去库是非致命反证，不能称需求继续下滑。weak仅一次market_risk0.5。",
          "evidence_refs": [
            "ORIGINAL-SOURCES",
            "M-RB-ECON"
          ]
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "details": "原10/23信号/10/25登记/10/27入场截止不变；现入场expired。原3047/SL3103及3034–3050只作历史。假设10/26入场，参考下场SL3099再3096，不放宽；实际成交未知。",
          "evidence_refs": [
            "ORIGINAL-SOURCES",
            "HOLDING-REVIEW"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "本期公开参数转引与公告已读，不能等同实时盘口/更严扩板跳空压力或用户实收；若有未平先核可成交退出与事件预案。",
          "evidence_refs": [
            "M-RB-ECON",
            "MA-SR-CF-ECON"
          ],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "本期公开参数转引与公告已读，不能等同实时盘口/更严扩板跳空压力或用户实收；若有未平先核可成交退出与事件预案。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "提供当日真实权益、全部持仓/挂单、有效SL、风险与实收保证金；未知不是空仓。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、全部持仓/挂单、有效SL、风险与实收保证金；未知不是空仓。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "按同一真实计划、账户、压力/执行/周末适用容量运行size-v3，最终手数未知保持null。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "按同一真实计划、账户、压力/执行/周末适用容量运行size-v3，最终手数未知保持null。",
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
      "final_lots": null,
      "status": "incomplete",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "actual_position_status": "unknown",
      "execution_state_inherited": false
    },
    {
      "candidate_id": "20261030-MA2701-MA2705-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "Missing month-specific numerical economic band and verifiable5–20-session convergence, not raw-data failure or no_signal",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evidence_refs": [
        "M-RB-ECON",
        "MA-SR-CF-ECON"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "有序两腿身份与原料61日完整；可实现仓储/交割、期限和实时流动性仍需按成案核。",
          "evidence_refs": [],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "有序两腿身份与原料61日完整；可实现仓储/交割、期限和实时流动性仍需按成案核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "仓储等单侧成本与产业数量不足以给双侧锚；未有合格事前数值锚及5–20日机制，未评估信号。",
          "evidence_refs": [],
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "仓储等单侧成本与产业数量不足以给双侧锚；未有合格事前数值锚及5–20日机制，未评估信号。",
            "due_at": "2026-11-06"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "须先有经济锚/失效价，再冻结近侧目标、数值SL、全区间净R及原有效期；不后造锚。",
          "evidence_refs": [],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "须先有经济锚/失效价，再冻结近侧目标、数值SL、全区间净R及原有效期；不后造锚。",
            "due_at": "2026-11-06"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "未来成案前核双腿同步限价/滑点/裸腿时限/撤单平腿、扩板提保压力和实时报价。",
          "evidence_refs": [],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "未来成案前核双腿同步限价/滑点/裸腿时限/撤单平腿、扩板提保压力和实时报价。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "当日真实账户和两腿资金/风险未知。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "当日真实账户和两腿资金/风险未知。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "同一计划及适用硬容量未齐，不计算最终整数手数。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "同一计划及适用硬容量未齐，不计算最终整数手数。",
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
      "status": "incomplete",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261030-RB2701-RB2703-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "Missing month-specific numerical economic band and verifiable5–20-session convergence, not raw-data failure or no_signal",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evidence_refs": [
        "M-RB-ECON",
        "MA-SR-CF-ECON"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "有序两腿身份与原料61日完整；可实现仓储/交割、期限和实时流动性仍需按成案核。",
          "evidence_refs": [],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "有序两腿身份与原料61日完整；可实现仓储/交割、期限和实时流动性仍需按成案核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "仓储等单侧成本与产业数量不足以给双侧锚；未有合格事前数值锚及5–20日机制，未评估信号。",
          "evidence_refs": [],
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "仓储等单侧成本与产业数量不足以给双侧锚；未有合格事前数值锚及5–20日机制，未评估信号。",
            "due_at": "2026-11-06"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "须先有经济锚/失效价，再冻结近侧目标、数值SL、全区间净R及原有效期；不后造锚。",
          "evidence_refs": [],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "须先有经济锚/失效价，再冻结近侧目标、数值SL、全区间净R及原有效期；不后造锚。",
            "due_at": "2026-11-06"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "未来成案前核双腿同步限价/滑点/裸腿时限/撤单平腿、扩板提保压力和实时报价。",
          "evidence_refs": [],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "未来成案前核双腿同步限价/滑点/裸腿时限/撤单平腿、扩板提保压力和实时报价。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "当日真实账户和两腿资金/风险未知。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "当日真实账户和两腿资金/风险未知。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "同一计划及适用硬容量未齐，不计算最终整数手数。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "同一计划及适用硬容量未齐，不计算最终整数手数。",
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
      "status": "incomplete",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261030-SR2701-SR2705-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "Missing month-specific numerical economic band and verifiable5–20-session convergence, not raw-data failure or no_signal",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evidence_refs": [
        "M-RB-ECON",
        "MA-SR-CF-ECON"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "details": "有序两腿身份与原料61日完整；可实现仓储/交割、期限和实时流动性仍需按成案核。",
          "evidence_refs": [],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "有序两腿身份与原料61日完整；可实现仓储/交割、期限和实时流动性仍需按成案核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "details": "仓储等单侧成本与产业数量不足以给双侧锚；未有合格事前数值锚及5–20日机制，未评估信号。",
          "evidence_refs": [],
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "仓储等单侧成本与产业数量不足以给双侧锚；未有合格事前数值锚及5–20日机制，未评估信号。",
            "due_at": "2026-11-06"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "details": "须先有经济锚/失效价，再冻结近侧目标、数值SL、全区间净R及原有效期；不后造锚。",
          "evidence_refs": [],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "须先有经济锚/失效价，再冻结近侧目标、数值SL、全区间净R及原有效期；不后造锚。",
            "due_at": "2026-11-06"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "details": "未来成案前核双腿同步限价/滑点/裸腿时限/撤单平腿、扩板提保压力和实时报价。",
          "evidence_refs": [],
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "未来成案前核双腿同步限价/滑点/裸腿时限/撤单平腿、扩板提保压力和实时报价。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "details": "当日真实账户和两腿资金/风险未知。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "当日真实账户和两腿资金/风险未知。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "details": "同一计划及适用硬容量未齐，不计算最终整数手数。",
          "evidence_refs": [],
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "同一计划及适用硬容量未齐，不计算最终整数手数。",
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
      "status": "incomplete",
      "evaluated_at": "2026-11-01T01:06:24.913824+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    }
  ],
  "unresolved_items": [
    {
      "item": "Three current V lack defendable economic intervals; current costs/realizable delivery/5–20day catalysts",
      "owner": "research",
      "next_action": "Progress pair-specific numeric inputs by11/06; no fabricated anchors",
      "due_at": "2026-11-06"
    },
    {
      "item": "Actual account/fills/stop path and venue temporary parameters unknown",
      "owner": "user_and_research",
      "next_action": "If holding exists, reconcile true fills/stops with conditional exit and event review",
      "due_at": "before_execution"
    }
  ],
  "evidence_corrections": [],
  "shadow_plans": [],
  "performance_status": "not_automated",
  "inherited_corrections_preserved": true,
  "classification": {
    "state_refresh_needed": true,
    "evidence_correction_needed": false,
    "method_change_needed": false
  }
}
```

本修订r3仅接续可持久抓取的验证回执r2及精确配套采纳引用；历史原稿和各次失败回执保留，投资判断不变。

本修订r4将历史算术附件指向相同原字节的冻结blob，消除对旧output缓存位置的计算材料依赖；原计划数字、时钟和判断不变。

本修订r5采用刷新r3的证据清单修订：计算、原料hash和原时钟沿用成功r2，登记计划原件以同hash opaque blob持久冻结，避免递归依赖历史cache位置；不改变投资事实或方法。

本修订r6仅采用来源图r2/裁决r2：旧导入失败回执按原字节opaque保存，不将错误信息中的旧路径解析为当前依赖；原稿与全部失败记录保留，判断及原钟不变。
