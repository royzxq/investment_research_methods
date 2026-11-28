# 期货执行审计 · 2026-11-08

generator=codex；public_data；current_framework v3.0，实际main949d020af04ba55e68cbeacada91099cc960d104。本期先复核MA/M/RB存量，再审五T/三V。缺继承TUSHARE_TOKEN，两次fetch认证前失败；未取得当前61日行情/API返回。历史10/30输入由当前刷新器明确拒绝，不是no_signal。当前行情日/抓取时间和真实账户均null；历史锚独立列10/30。没有新执行计划，没有可复现收益。

## 覆盖与旧时钟

五个当前T价格路线为unknown/incomplete，三组V无事前锚not_evaluated、当前两腿未更新，两类缺口分别列。11条审计记录由五T、全部三个旧机会、三V组成，不代表11个独立新机会；总体机会数null。G1–G6逐项记录，缺当前61日与流动性/报价等研究输入不能用awaiting_account。账户、真实Entry/SL/持仓挂单/实收保证金/成交退出、全部final_lots保持null，不做伪空仓size-v3。当前V未成案退出规则保持null，不套T的跟踪止损。

|存量原机会|原入场状态/计划|条件风险管理|
|---|---|---|
|MA 20261011-observe-MA2701-trend-long-v3|信号10/09、登记10/11 18:14:54、截止10/13，expired；历史3338/SL3139，原带3289–3387|原参考SL10/19条件穿越、原带所有初始SL最迟10/20穿越；若真实未先退则更早退出条件已触发，不能因反弹复活。10/12入场的11/06时间上限已过；10/13入场原11/09是另一条件末限，均不覆盖更早SL|
|M 20261015-observe-M2701-trend-short-v3|信号10/15、登记19:30:56、截止10/19；10/16越带取消，cancelled_and_expired；原无完整数值案|3310/3410仅历史诊断，不当成交。原null/r2登记冲突已裁决，不丢M、不重启。若真有仓按真实Entry/SL和WASDE压力复核|
|RB 20261025-observe-RB2701-trend-short-v3|信号10/23、登记10/25 01:06:50.045735、截止10/27，expired；原3047/SL3103，原带3034–3050|若10/26入场，旧路径收盘后下场SL3099再3096仅历史参考、此后只收紧；本周完整路径缺失不能重算。11/06公开H3059未跨3096只说明单日，不证明全周未穿或真实持仓。11/20或11/23原时间上限取真实入场日及更早退出|

全部原ID、signal_date、registered_at、valid_until与原数值计划逐字保留；上表不是账户事实。旧MA入场过期与是否已经平仓分开；跨周末/提保/事件压力及全部风险要核实际账户。M旧10/29未登记且10/30已取消的机械触发也不复活，旧10/27四根窗口已过，未补历史建议/成交。

## 产业、事件、执行边界

RB本周产185.90、表需残差200.80、总库482.37万吨：供增需降、去库减速但仍去库，原空支持增强，仍有现货修复和去库反证。M现货/成品供给压力有独立公开证据，但10/30库存138.94只是11/06发布的滞后观测；AI摘要的3040报价与提货总数未用。MA11/04港库41.27周+5.89转累、提货一般，对旧多构成反证；旧G2 pass撤回不恢复。SR开榨推进但陈糖清库，CF弱纱需与棉现货上涨相抵。详见[市场研究](2026-11-08-market-research-r2.md)、[M/RB原文底稿](evidence/m-rb/research-note.md)、[MA/SR/CF底稿](evidence/other-products/research-note.md)。

USDA WASDE11/10 12ET=11/11 01北京已核；M首次国内实际场次/国内T两份DCE原件不可读仍null，不能用美国当地日当T或自动冻结RB。若有实仓，报告前按实际事件相关性重做压力，不能承受就减/退，未声称已执行。MA细则常规场次已核但临时安排未穷尽；2027第10交易日规则不解01/14 vs01/15精确到期冲突。公开交易所参数与公司表、不同日期/合约和用户实收区分，动态规则/报价/完整压力及账户缺口仍unknown；不凭公告未找到判没有公告。旧计划日历不依赖本轮T主合约列表，r4原窗计算与价格未刷新分列。

## 纠错、接续与验证

11/01已采纳r6及collected RB计划继承remaining_window标签，与原10/27截止和正文expired不一致。本期保存invalid证据RB-WINDOW-OLD，仅diagnostic引用；当前entry_window_state=expired，G3失败依据为原计划及当前日期，原钟不改。这是状态元数据证据纠错，不改变T/V定义或风险参数。其他16组历史纠错逐项继承；M原登记冲突裁决保留，不能只读导出的MA/RB而漏M。[完整裁决r2](evidence/continuity-reconciliation-r2.json)、[稳定来源图r2](evidence/continuity-catalog-r2.json)。

[刷新r4](../../refresh/2026-11-08/2026-11-08-signal-refresh-r4.json)保持原r3拒绝/过期计算、仅同hash登记计划引用持久化。三V[正式维护](../../anchors/2026-11-08/2026-11-08-anchors-r2.json)没有可辩护双侧区间/5–20日机制，anchors/withdrawals空有“无有效继承锚”前提；11/13继续月份交割/费用/融资和真实供需，不事后造锚。失败/陈旧/未评估不当no_signal，入场到期不当持仓已退。

状态刷新yes、证据纠错yes、方法变更no；update_needed=no/none。验证分为审计schema3/治理/来源hash和离线回归，真实行情API未通过认证，账户/成交/收益未验证。实际检查回执见[evidence/validation.json](evidence/validation.json)；独立审阅见[evidence/independent-review.md](evidence/independent-review.md)。Git发布及共享发布结果另行核验，publication_verified不替代远端main包含检查。

本修订r2仅完善持久来源引用及历史行情身份字段：handoff v2要求ISO行情锚，故snapshot.market_trade_date=2026-10-30、market_captured_at为11/01原包抓取时刻，仅表示实际用来做陈旧拒绝/旧窗核验的历史原料；current_market_trade_date/current_market_captured_at仍null。无当前原料的筛选记录trade_date亦仅历史输入锚，basis明确current_not_evaluated，信号unknown、当前价null；不表示本期最新。原稿保留，产业/原计划/三类结论均不变。

实际公共原文、HTTP回执、失败和partial、全部共享来源及初稿原件由[总证据清单](evidence/source-manifest.json)逐hash冻结，回执原字节opaque保存，不依赖失效缓存；锚r2只修来源引用，经济事实和原冻结时点不变。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-11-08",
  "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
  "generator": "codex",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "949d020af04ba55e68cbeacada91099cc960d104"
  },
  "snapshot": {
    "market_trade_date": "2026-10-30",
    "market_captured_at": "2026-11-01T01:00:46.944347+08:00",
    "historical_market_trade_date": "2026-10-30",
    "historical_source_captured_at": "2026-11-01T01:00:46.944347+08:00",
    "current_raw_status": "acquisition_failed_missing_inherited_credential",
    "source_artifacts": [
      "research/futures/refresh/2026-11-08/2026-11-08-signal-refresh-r4.json",
      "research/futures/weekly/2026-11-08/evidence/continuity-catalog-r2.json",
      "research/futures/weekly/2026-11-01/2026-11-01-execution-audit-r6.md",
      "research/futures/weekly/2026-11-08/evidence/source-manifest.json"
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
    },
    "current_market_trade_date": null,
    "current_market_captured_at": null,
    "snapshot_basis": "historical_input_package_identity_only;current61sessiondata_not_acquired"
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "all known MA/M/RB original plans and conditional holdings; original clocks and accumulated corrections",
      "five T acquisition/status audit and three V economic research routes",
      "M/RB priority current public industrial evidence;MA/SR/CF and public rules"
    ],
    "missing_scope": [
      "current61-session exact-contract T OHLC and V two-leg inputs",
      "11/02–06 full stop/trailing path and actual venue temporary arrangements",
      "actual account/fills/effective stops/real-time quotes;MA2027 exact expiry"
    ],
    "research_only_scope": [
      "three month-specific numerical V anchor routes"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "FETCH-FAILURE",
      "metric": "Two real collector attempts stopped before authentication",
      "value": {
        "TUSHARE_TOKEN_present": false,
        "api_authenticated": false,
        "new_complete_snapshot": false
      },
      "unit": "status",
      "observation_date": "2026-11-08",
      "published_at": "2026-11-08T01:12:44.436504+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-08/evidence/fetch-failures/collector-1.log",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "REFRESH-REJECT",
      "metric": "Historical10/30 input rejected for current price evaluation; original windows retained",
      "value": {
        "trend": "unknown",
        "reason": "source_fetched_before_completed_session_cutoff",
        "MA_window": "expired",
        "RB_window": "expired"
      },
      "unit": "status",
      "observation_date": "2026-11-08",
      "published_at": "2026-11-08T01:12:44.436504+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-08/2026-11-08-signal-refresh-r4.json",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "ORIGINAL-PLANS",
      "metric": "Adopted original MA/M/RB identities, signal, registration, validity and numeric plans",
      "value": {
        "source_audit": "11/01 r6",
        "current_account": null
      },
      "unit": "status",
      "observation_date": "2026-11-01",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-01/2026-11-01-execution-audit-r6.md",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "historical",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "CLOCK",
      "metric": "As-of date is later than original MA10/13 M10/19 RB10/27 entry expiry",
      "value": "2026-11-08",
      "unit": "status",
      "observation_date": "2026-11-08",
      "published_at": "2026-11-08T01:12:44.436504+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-08/evidence/run-baseline.json",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "CONTINUITY",
      "metric": "13 consumed entries;16 correction groups;1 M original registration conflict;no requires_* items",
      "value": {
        "current_readiness_inherited": false
      },
      "unit": "status",
      "observation_date": "2026-11-08",
      "published_at": "2026-11-08T01:12:44.436504+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-08/evidence/continuity-reconciliation-r2.json",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "RB-WINDOW-OLD",
      "metric": "Inherited erroneous entry_window_state",
      "value": {
        "value": "remaining_window",
        "original_valid_until": "2026-10-27"
      },
      "unit": "status",
      "observation_date": "2026-11-01",
      "published_at": "2026-11-01T01:06:24.913824+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-01/2026-11-01-execution-audit-r6.md",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_execution",
      "quality": "invalid",
      "time_scope": "historical",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "PUBLIC-M-RB",
      "metric": "Current independent industrial evidence, counterevidence, event and quote reading limits",
      "value": "See source ledger; public one-day RB OHLC does not supply61-day series",
      "unit": "status",
      "observation_date": "2026-11-08",
      "published_at": "2026-11-08T01:12:44.436504+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-08/evidence/m-rb/research-note.md",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "PUBLIC-OTHER",
      "metric": "MA/SR/CF drivers, public rules and V month-specific economics",
      "value": "See source ledger; no numerical V anchor established",
      "unit": "status",
      "observation_date": "2026-11-08",
      "published_at": "2026-11-08T01:12:44.436504+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-08/evidence/other-products/research-note.md",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    },
    {
      "evidence_id": "CURRENT-RAW-MISSING",
      "metric": "Current61-session exact-contract OHLC and V legs",
      "value": "unavailable",
      "unit": "status",
      "observation_date": "2026-11-08",
      "published_at": "2026-11-08T01:12:44.436504+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-08/evidence/refresh-attempt-2.log",
      "original_source": "Exact frozen source; original publisher/time/reading limits stated in cited ledger",
      "price_basis": "not an executable quote; see explicit metric",
      "comparison_basis": "same identity, original clock and stated sample only",
      "role": "required_model",
      "quality": "missing",
      "time_scope": "current",
      "published_at_basis": "local verification timestamp unless original publication timestamp specified"
    }
  ],
  "candidates": [
    {
      "candidate_id": "20261108-MA2701-trend-unassessed-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本期进程缺TUSHARE_TOKEN，61根当前完整OHLC与信号未取得；公开单日报道不足替代",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
    },
    {
      "candidate_id": "20261108-RB2701-trend-unassessed-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本期进程缺TUSHARE_TOKEN，61根当前完整OHLC与信号未取得；公开单日报道不足替代",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
    },
    {
      "candidate_id": "20261108-M2701-trend-unassessed-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本期进程缺TUSHARE_TOKEN，61根当前完整OHLC与信号未取得；公开单日报道不足替代",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
    },
    {
      "candidate_id": "20261108-SR2701-trend-unassessed-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本期进程缺TUSHARE_TOKEN，61根当前完整OHLC与信号未取得；公开单日报道不足替代",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
    },
    {
      "candidate_id": "20261108-CF2701-trend-unassessed-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-30",
      "contracts": [
        "CF2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本期进程缺TUSHARE_TOKEN，61根当前完整OHLC与信号未取得；公开单日报道不足替代",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
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
      "data_feasibility_reason": "当前路径/账户未知；保留原计划作历史条件管理，不是当前可入场案",
      "signal": "triggered",
      "signal_evidence_refs": [
        "ORIGINAL-PLANS"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ORIGINAL-PLANS",
            "CLOCK",
            "REFRESH-REJECT"
          ],
          "details": "原信号入场窗已到期/取消；不能用本次登记延长两日"
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
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
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "price_screening_date": "2026-10-23",
      "historical_price_screen": "original 2026-10-09 long price signal retained; 2026-10-15 new T signal not_triggered",
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
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
      "execution_state_inherited": false,
      "performance_status": "not_automated"
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
      "data_feasibility_reason": "当前路径/账户未知；保留原计划作历史条件管理，不是当前可入场案",
      "signal": "triggered",
      "signal_evidence_refs": [
        "ORIGINAL-PLANS"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ORIGINAL-PLANS",
            "CLOCK",
            "REFRESH-REJECT"
          ],
          "details": "原信号入场窗已到期/取消；不能用本次登记延长两日"
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
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
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "price_screening_date": "2026-10-23",
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
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
      "execution_state_inherited": false,
      "performance_status": "not_automated"
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
      "data_feasibility_reason": "当前路径/账户未知；保留原计划作历史条件管理，不是当前可入场案",
      "signal": "triggered",
      "signal_evidence_refs": [
        "ORIGINAL-PLANS"
      ],
      "registered_at": "2026-10-25T01:06:50.045735+08:00",
      "entry_window_state": "expired",
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
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "not_evaluated_after_no_signal": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补本期同合约61日完整OHLC和严格T信号；原信号仅历史，当前产业按底稿重评",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ORIGINAL-PLANS",
            "CLOCK",
            "REFRESH-REJECT"
          ],
          "details": "原信号入场窗已到期/取消；不能用本次登记延长两日",
          "diagnostic_evidence_refs": [
            "RB-WINDOW-OLD"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
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
      "status": "incomplete",
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "actual_position_status": "unknown",
      "execution_state_inherited": false,
      "performance_status": "not_automated",
      "diagnostic_evidence_refs": [
        "RB-WINDOW-OLD"
      ]
    },
    {
      "candidate_id": "20261108-MA2701-MA2705-economic-reversion-research-v3",
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
      "data_feasibility_reason": "月份适用的可实现双侧经济区间与5–20日机制尚缺；本期两腿价格另因认证不可得",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补适用有序对两腿原料、事前数值经济锚和5–20日收敛机制，未来冻结不得筛旧行情",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补适用有序对两腿原料、事前数值经济锚和5–20日收敛机制，未来冻结不得筛旧行情",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
    },
    {
      "candidate_id": "20261108-RB2701-RB2703-economic-reversion-research-v3",
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
      "data_feasibility_reason": "月份适用的可实现双侧经济区间与5–20日机制尚缺；本期两腿价格另因认证不可得",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补适用有序对两腿原料、事前数值经济锚和5–20日收敛机制，未来冻结不得筛旧行情",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补适用有序对两腿原料、事前数值经济锚和5–20日收敛机制，未来冻结不得筛旧行情",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
    },
    {
      "candidate_id": "20261108-SR2701-SR2705-economic-reversion-research-v3",
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
      "data_feasibility_reason": "月份适用的可实现双侧经济区间与5–20日机制尚缺；本期两腿价格另因认证不可得",
      "signal": "unknown",
      "signal_evidence_refs": [],
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
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核本期真实合约20日流动性、当前最后交易日/更早退出规则；范围已知不能替代必要当前字段",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "补适用有序对两腿原料、事前数值经济锚和5–20日收敛机制，未来冻结不得筛旧行情",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "补适用有序对两腿原料、事前数值经济锚和5–20日收敛机制，未来冻结不得筛旧行情",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "当前信号未知，尚不能给合法Entry/SL/有效期；补齐价格后按原规则成案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "PUBLIC-M-RB",
            "PUBLIC-OTHER"
          ],
          "details": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核执行时动态公开规则、真实报价、相关事件场次、完整跳空/退出预案；11/06公开表不冒充用户实收",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核当日净值、全部持仓挂单、实际SL/风险、实收保证金费用、可用资金及限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户及执行输入齐后用size-v3核最终整数容量；缺口不能以0或无限替代",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluated_at": "2026-11-08T01:12:44.436504+08:00",
      "evaluation_order": [
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "evidence_refs": [
        "CONTINUITY",
        "PUBLIC-M-RB",
        "PUBLIC-OTHER"
      ],
      "performance_status": "not_automated",
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
      "trade_date_basis": "historical_input_anchor_only;current_screen_not_evaluated",
      "current_market_trade_date": null
    }
  ],
  "unresolved_items": [
    {
      "item": "恢复运行环境继承的TUSHARE_TOKEN后另存本期修订刷新；不在聊天或仓库保存凭据",
      "owner": "research",
      "due_at": "before_execution",
      "required_evidence": [
        "current complete authenticated raw series and actual calendars"
      ],
      "resolution": "pending"
    },
    {
      "item": "实际MA/M/RB账户与有效SL/成交退出仍未知，先执行条件风险管理",
      "owner": "user",
      "due_at": "before_execution",
      "required_evidence": [
        "dated account/order/fill/effective stop records"
      ],
      "resolution": "pending"
    }
  ],
  "shadow_plans": [],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "RB-WINDOW-OLD",
      "reason": "11/01已采纳审计r6及collect继承remaining_window标签与原10/27截止、正文expired不一致；本期改expired，不重启原时钟",
      "affected_checks": [
        {
          "candidate_id": "20261023-RB2701-trend-short-v3",
          "rule_id": "G3"
        }
      ],
      "recalculation": "completed"
    }
  ],
  "metadata_revision": "r2 keeps historical10/30 input identity in handoff-required date fields; current_market_* remain null, no current price or signal manufactured; complete stable source manifest explicitly referenced."
}
```
