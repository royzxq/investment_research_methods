# 期货执行审计 · 2026-10-25

generator=codex；public_data；current_framework v3.0。实际基线与hash见[evidence/run-baseline.json](evidence/run-baseline.json)。行情10/23，v1.18.1真实API完整；首次沙箱网络失败稿保留，采纳刷新r2。先逐一检查全部已知MA/M存量，再研究本期新RB机会。所有实际持仓、成交、权益与最终手数未知；没有收益验证。

## 覆盖和候选

| 对象 | 当前结论 | 处置 |
|---|---|---|
| 原MA多 20261011-observe-MA2701-trend-long-v3 | 原入场10/13已到期；原示例SL3139在10/19被low3131穿越 | 若真实沿原案持仓且此前未退出，止损边界已触发；不能因10/23回升复活。真实成交/平仓未知 |
| 原M空 20261015-observe-M2701-trend-short-v3 | 10/16原价格越界已取消，10/19到期；10/23当前T未触发 | 保留10/15 19:30:56登记，不能续期或补造持仓 |
| 新RB2701空 | 10/23 close3047<prior20low3051；G1/G2/G3通过，G4/G5/G6 unknown | 唯一新深研计划；状态incomplete，非awaiting_account，手数null |
| 当前M/MA/SR/CF T | 完整价格侧not_triggered | 四条no_signal，仅对本次路线早停 |
| MA/RB/SR V | 当前有序腿原料完整；经济锚缺失 | 三条research_only/未评估，非no_signal；另两准备对仅原料检查 |

## 新计划唯一登记

RB机会`20261025-observe-RB2701-trend-short-v3`，真实登记见[rb-registration](evidence/rb-registration.json)。信号10/23，窗口10/26–27，截止10/27日盘15:00（临时安排/报价仍需拟执行前核）。10/23晚所属10/26的夜盘早于登记，不追记。登记后首个常规连续竞价为10/26 09:00。

参考Entry3047，允许3034–3050，初始SL3103；ATR27.88435，targets=null。开平手续费预算20元/手、滑点20，总成本40，参考风险600元/手；不是经纪商实收。实际Entry改变按2ATR重算SL及风险，不能照抄600；入场失去突破侧、超出0.5ATR、逻辑被证伪或过期即取消。10/26入场最迟11/20，若10/27入场最迟11/23，均入场日算第1天20交易日；按当日期交所/经纪商更早边界取严。每天完整日收盘用最近10完整日最高high作为下一时段空头跟踪SL，只收紧。信号日prior10high3105为历史参考，不放宽3103。

产业支持是同口径螺纹表需201.03万吨周减21.24、产量174.73周增0.84；反证是总库522.16仍去26.30，不能把去库说成累库，也不能把表需当终端实销。evidence_quality=weak、market_risk一次0.5；HV比0.9102未高波。FOMC只背景，无直接相关事实则不自动冻结RB。

公开规格、期限及20日均量已核。公开费率动态表附件失败、当前盘口/限板参数未核，G4保留研究缺口。以prior20high3140作可核不利情景，含同成本压力970/计划600=1.6167，超过RB轻仓复核线1.5、未过通常淘汰线2.0；这不是最坏压力保证，尚须核动态板幅与更严场景/相关事件及账户绝对承受额。未以减手数掩盖单位风险，G4仍unknown。不使用示例空仓调用size-v3。

## 原持仓条件管理与全部历史范围

MA原Entry3338/SL3139不改。10/19 low3131首次穿参考SL；10/20 low3089低于原入场带对应所有初始SL3090–3188，所以若真实按原范围入场、未提前离场，则最迟10/20存在条件退出触发。真实入场低高先后、已收紧SL、能否成交和盈亏均未知，不回填执行。10/23最近10完整日low3016不能把已触发的3139放宽为3016；失效后反弹不是恢复入场。原11/06或11/09时间界保留作历史上限，不取代更早止损。专属逐日日线见[条件轨迹](evidence/ma-conditional-holding-review.json)。

MA本周MTO需求反证与低库支持并存，原G2 pass撤回不恢复。10/26结算起9%/8%公告直接覆盖MA2701，按相关风控事件T10/26复核10/23–27窗口、存量压力/保证金；10/28以后首场次仍核实际CZCE安排。旧6%压力不能沿用到新制度，具体经纪商实收未知。跨周末无有效对冲仍按canonical单仓B×30%上限；缺账户不计算。MA到期API01/14与旧推01/15保留待核，不能静默选较晚。

M原候选没有已核数值执行计划，3310/3410是旧诊断，不证明真实开仓。若实际持有空头，提供Entry、有效SL和逐日成交路径；下一时段最近10日high3420只可收紧，不能放宽真实旧SL。新鲜现货反弹/国内供应链口径必须重评，原10/15方向不永久继承。USDA作物进度是未来观察，是否构重大事件按实际传导评估。

10/11其余M/RB/SR/CF及V观察均无登记数值计划，不当真实持仓；已在本期五T/三V重新覆盖。共享review_scope9条、纠错12项和1条M元数据冲突逐项读取；M按已明确采纳r2原时间裁决，原件冲突仍留。旧V历史no_signal不继承为当前结论。[接续裁决](evidence/continuity-reconciliation.json)、[冻结来源](evidence/shared-sources/catalog.json)。

## 下次复核与验证边界

10/26拟入场前先核RB报价/参数/更严压力，再核实际账户；每个交易日刷新，不延10/27窗口。MA/M若有真实持仓，先核已触发退出与未平风险。三V10/30研究补件不延任何信号。真实行情/合约API与离线验证分报，具体回执见[evidence/validation.json](evidence/validation.json)。结构通过不能证明产业因果、交易许可或收益。

初稿结构核验发现本地证据行缺published_at，原稿保留；本修订将其明确为本地证据冻结时间，原始发布日按来源账读取，不伪造原始发布时间。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-25",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "76abde55d73f21310cb263fe448dc5a505e89ade"
  },
  "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
  "snapshot": {
    "market_trade_date": "2026-10-23",
    "market_captured_at": "2026-10-25T01:03:13.867920+08:00",
    "source_artifacts": [
      "research/futures/refresh/2026-10-25/2026-10-25-signal-refresh-r2.json",
      "research/futures/refresh/2026-10-25/evidence/2026-10-25-signal-refresh-r2/market-inputs.json",
      "research/futures/snapshots/2026-10-25-data-snapshot.txt",
      "research/futures/weekly/2026-10-25/evidence/shared-sources/catalog.json"
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
      "all known MA/M original plans and conditional holdings",
      "five exact-contract T price screens",
      "one new RB numerical plan",
      "three current V economic routes plus two preparation pair raw checks"
    ],
    "missing_scope": [
      "actual account/fills and daily execution stops",
      "RB current quotes/dynamic public parameters and absolute stress capacity",
      "MA official exact2027 expiry reconciliation"
    ],
    "research_only_scope": [
      "MA/RB/SR month-specific V economic anchors"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "PRICE-CF2701",
      "metric": "exact-contract T price calculation",
      "value": {
        "signal_close": 15855.0,
        "prior20_high": 16130.0,
        "prior20_low": 15490.0,
        "atr20": 202.1982001645694,
        "signal": "not_triggered",
        "volatility_ratio": 1.0235383654402215
      },
      "unit": "CNY/tonne and ratio",
      "observation_date": "2026-10-23",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-25/2026-10-25-signal-refresh-r2.json",
      "original_source": "Tushare Pro fut_daily, response ts_code verified",
      "price_basis": "close/high/low",
      "comparison_basis": "same named object and observation period",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "PRICE-M2701",
      "metric": "exact-contract T price calculation",
      "value": {
        "signal_close": 3276.0,
        "prior20_high": 3502.0,
        "prior20_low": 3217.0,
        "atr20": 47.81304281789677,
        "signal": "not_triggered",
        "volatility_ratio": 0.9783910298939896
      },
      "unit": "CNY/tonne and ratio",
      "observation_date": "2026-10-23",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-25/2026-10-25-signal-refresh-r2.json",
      "original_source": "Tushare Pro fut_daily, response ts_code verified",
      "price_basis": "close/high/low",
      "comparison_basis": "same named object and observation period",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "PRICE-MA2701",
      "metric": "exact-contract T price calculation",
      "value": {
        "signal_close": 3219.0,
        "prior20_high": 3402.0,
        "prior20_low": 2821.0,
        "atr20": 107.80845506008174,
        "signal": "not_triggered",
        "volatility_ratio": 1.2054379372457986
      },
      "unit": "CNY/tonne and ratio",
      "observation_date": "2026-10-23",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-25/2026-10-25-signal-refresh-r2.json",
      "original_source": "Tushare Pro fut_daily, response ts_code verified",
      "price_basis": "close/high/low",
      "comparison_basis": "same named object and observation period",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "PRICE-RB2701",
      "metric": "exact-contract T price calculation",
      "value": {
        "signal_close": 3047.0,
        "prior20_high": 3140.0,
        "prior20_low": 3051.0,
        "atr20": 27.884349934393008,
        "signal": "triggered",
        "volatility_ratio": 0.9102285306987645
      },
      "unit": "CNY/tonne and ratio",
      "observation_date": "2026-10-23",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-25/2026-10-25-signal-refresh-r2.json",
      "original_source": "Tushare Pro fut_daily, response ts_code verified",
      "price_basis": "close/high/low",
      "comparison_basis": "same named object and observation period",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "PRICE-SR2701",
      "metric": "exact-contract T price calculation",
      "value": {
        "signal_close": 5357.0,
        "prior20_high": 5563.0,
        "prior20_low": 5305.0,
        "atr20": 53.95278561392978,
        "signal": "not_triggered",
        "volatility_ratio": 1.2182005828177391
      },
      "unit": "CNY/tonne and ratio",
      "observation_date": "2026-10-23",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/refresh/2026-10-25/2026-10-25-signal-refresh-r2.json",
      "original_source": "Tushare Pro fut_daily, response ts_code verified",
      "price_basis": "close/high/low",
      "comparison_basis": "same named object and observation period",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "CLOCKS",
      "metric": "explicit original registrations and deadlines",
      "value": "MA10/09–10/13; M10/15–10/19, actual M registration19:30:56",
      "unit": "identity/time",
      "observation_date": "2026-10-15",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/continuity-reconciliation.json",
      "original_source": "frozen actual source",
      "price_basis": "source stated basis",
      "comparison_basis": "same named object and observation period",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "historical",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "RB-INDUSTRY",
      "metric": "rebar output/stock/residual consumption",
      "value": [
        174.73,
        152.34,
        369.82,
        201.03
      ],
      "unit": "10,000 tonnes",
      "observation_date": "2026-10-22",
      "published_at": "2026-10-22T14:24:00+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/industry-m-rb.md",
      "original_source": "Xinhua Finance full public report, Sina republication",
      "price_basis": "source stated basis",
      "comparison_basis": "same rebar sample; consumption is residual, not transaction demand",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-INDUSTRY",
      "metric": "MTO closures and regional port inventory",
      "value": "reported coastal MTO shutdowns; port36.38, weekly-0.34, regional divergence",
      "unit": "10,000 tonnes",
      "observation_date": "2026-10-21",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/industry-ma-sr-cf.md",
      "original_source": "Longzhong author article and CLS via CITIC; original plant table unavailable",
      "price_basis": "source stated basis",
      "comparison_basis": "not asserted same sample as previous report",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "PUBLIC-RULES",
      "metric": "RB specs/expiry/session and remaining dynamic parameter gap",
      "value": "10tonne/lot;1CNY/tonne tick; Jan15 expiry;09:00 first future day session",
      "unit": "spec/date",
      "observation_date": "2026-10-25",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/execution-source-notes.md",
      "original_source": "SHFE official rules and hours",
      "price_basis": "source stated basis",
      "comparison_basis": "same named object and observation period",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "CONTRACT-API",
      "metric": "RB/M/MA contract metadata and twenty-session average volume",
      "value": {
        "RB2701.SHF": {
          "basic": [
            {
              "ts_code": "RB2701.SHF",
              "symbol": "RB2701",
              "name": "螺纹钢2701",
              "list_date": "20260116",
              "delist_date": "20270115",
              "last_ddate": "20270119",
              "per_unit": 10.0,
              "trade_unit": "吨"
            }
          ],
          "mean_volume20": 659726.95
        },
        "M2701.DCE": {
          "basic": [
            {
              "ts_code": "M2701.DCE",
              "symbol": "M2701",
              "name": "豆粕2701",
              "list_date": "20260119",
              "delist_date": "20270115",
              "last_ddate": "20270120",
              "per_unit": 10.0,
              "trade_unit": "吨"
            }
          ],
          "mean_volume20": 1144190.35
        },
        "MA2701.ZCE": {
          "basic": [
            {
              "ts_code": "MA2701.ZCE",
              "symbol": "MA701",
              "name": "甲醇2701",
              "list_date": "20260119",
              "delist_date": "20270114",
              "last_ddate": "20270119",
              "per_unit": 10.0,
              "trade_unit": "吨"
            }
          ],
          "mean_volume20": 1402579.55
        }
      },
      "unit": "lots/spec/date",
      "observation_date": "2026-10-23",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/contract-and-volume-api.json",
      "original_source": "actual Tushare Pro fut_basic/fut_daily response",
      "price_basis": "source stated basis",
      "comparison_basis": "same named object and observation period",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "RB-PLAN",
      "metric": "fixed-v3 arithmetic result",
      "value": {
        "entry": 3047,
        "range": [
          3034,
          3050
        ],
        "stop": 3103,
        "risk": 600
      },
      "unit": "CNY/tonne;CNY/lot",
      "observation_date": "2026-10-23",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/rb-plan-result.json",
      "original_source": "scripts/futures_strategy.py validate-plan current fixed helper",
      "price_basis": "source stated basis",
      "comparison_basis": "same named object and observation period",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "MA-STOP",
      "metric": "conditional reference stop crossed",
      "value": "10/19 low3131<3139; 10/20 low3089 below all original-band initial stops",
      "unit": "CNY/tonne",
      "observation_date": "2026-10-20",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/ma-conditional-holding-review.json",
      "original_source": "exact-contract returned-identity daily OHLC",
      "price_basis": "source stated basis",
      "comparison_basis": "same named object and observation period",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
    },
    {
      "evidence_id": "MA-RULE-1026",
      "metric": "announced MA2701 future parameters",
      "value": {
        "exchange_margin": 0.09,
        "limit": 0.08,
        "effective": "2026-10-26 settlement"
      },
      "unit": "ratio/date",
      "observation_date": "2026-10-22",
      "published_at": "2026-10-23",
      "source_url_or_file": "https://www.citicsf.com/e-futures/content/000204/826335",
      "original_source": "CZCE notice full republication by member CITIC",
      "price_basis": "source stated basis",
      "comparison_basis": "same named object and observation period",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "WITHDRAWN-MA-G2",
      "metric": "historical G2 pass withdrawn",
      "value": "No restoration of old current-use industry pass",
      "unit": "n/a",
      "observation_date": "2026-10-12",
      "published_at": "2026-10-25T01:10:57.364586+08:00",
      "source_url_or_file": "research/futures/weekly/2026-10-25/evidence/shared-sources/catalog.json",
      "original_source": "frozen actual source",
      "price_basis": "source stated basis",
      "comparison_basis": "same named object and observation period",
      "role": "required_model",
      "quality": "invalid",
      "time_scope": "historical",
      "published_at_basis": "local evidence artifact frozen_at; underlying original release date is stated in source ledger, not inferred from this time"
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
        "CLOCKS"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "MA2701API01/14与旧规则推01/15冲突仍待官方2027日期；本期均量1402579.55已核，原11月时间退出更早。",
          "gap": {
            "kind": "raw_data",
            "owner": "research",
            "next_action": "MA2701API01/14与旧规则推01/15冲突仍待官方2027日期；本期均量1402579.55已核，原11月时间退出更早。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "原多当前G2 pass撤回不恢复；MTO需求反证强化、低库进口为反证，核同口径装置/港库以判定真实持仓逻辑。",
          "gap": {
            "kind": "raw_data",
            "owner": "research",
            "next_action": "原多当前G2 pass撤回不恢复；MTO需求反证强化、低库进口为反证，核同口径装置/港库以判定真实持仓逻辑。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "CLOCKS",
            "MA-STOP"
          ],
          "details": "原10/13入场到期；若实际按原范围入场且未退出，最迟10/20已穿所有原初始SL，不能因反弹复活；实际Entry/收紧SL/退出另核。"
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "10/26结算MA9%/板8%公告已核；按真实持仓重做事件压力/保证金与周末上限，缺盘口/事故可执行价保持unknown。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "10/26结算MA9%/板8%公告已核；按真实持仓重做事件压力/保证金与周末上限，缺盘口/事故可执行价保持unknown。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
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
        "CLOCKS",
        "MA-STOP",
        "MA-INDUSTRY",
        "MA-RULE-1026",
        "PRICE-MA2701"
      ],
      "price_screening_date": "2026-10-23",
      "historical_price_screen": "original 2026-10-09 long price signal retained; 2026-10-15 new T signal not_triggered",
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "registered_at": "2026-10-11T18:14:54+08:00",
      "risk_factors": {
        "strategy": 0.7,
        "market_risk": 0.5,
        "exchange_buffer": null,
        "market_risk_reason": "nonfatal economic disagreement/ongoing supply event; one factor only"
      },
      "entry_window_state": "expired",
      "actual_position_status": "unknown",
      "conditional_holding_review": {
        "as_of_date": "2026-10-25",
        "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
        "contract": "MA2701",
        "source_inputs": [
          {
            "path": "research/futures/refresh/2026-10-25/evidence/2026-10-25-signal-refresh-r2/market-inputs.json",
            "sha256": "4dfe9acbe8728ce651b5d68222271dcf4c72c711501fa86056d481b20ff95799"
          }
        ],
        "original_reference_entry": 3338,
        "original_reference_initial_stop": 3139,
        "first_daily_low_crossing_reference_stop": {
          "ts_code": "MA2701.ZCE",
          "trade_date": "20261019",
          "close": 3143.0,
          "high": 3243.0,
          "low": 3131.0,
          "response_ts_code": "MA2701.ZCE"
        },
        "reference_stop_initial_range_for_original_entry_band": [
          3090,
          3188
        ],
        "all_band_initial_stops_crossed_by": "2026-10-20",
        "basis": "Original entry band 3289..3387 and original signal ATR, 2ATR outward-rounded initial stops 3090..3188. 10/20 low3089 is below even the minimum; this establishes a conditional stop-boundary breach, not a fill or exit execution. Tightened stops could trigger earlier.",
        "current_recent10_completed_low": 3016.0,
        "current_recent10_completed_high": 3384.0,
        "next_session_effective_only": true,
        "holding_verified": false,
        "actual_entry": null,
        "actual_effective_stop": null,
        "actual_exit": null,
        "pnl": null,
        "dates": [
          {
            "trade_date": "20261012",
            "low": 3176.0,
            "high": 3384.0,
            "close": 3229.0
          },
          {
            "trade_date": "20261013",
            "low": 3193.0,
            "high": 3278.0,
            "close": 3235.0
          },
          {
            "trade_date": "20261014",
            "low": 3220.0,
            "high": 3320.0,
            "close": 3262.0
          },
          {
            "trade_date": "20261015",
            "low": 3164.0,
            "high": 3289.0,
            "close": 3170.0
          },
          {
            "trade_date": "20261016",
            "low": 3146.0,
            "high": 3223.0,
            "close": 3192.0
          },
          {
            "trade_date": "20261019",
            "low": 3131.0,
            "high": 3243.0,
            "close": 3143.0
          },
          {
            "trade_date": "20261020",
            "low": 3089.0,
            "high": 3180.0,
            "close": 3157.0
          },
          {
            "trade_date": "20261021",
            "low": 3016.0,
            "high": 3193.0,
            "close": 3130.0
          },
          {
            "trade_date": "20261022",
            "low": 3081.0,
            "high": 3239.0,
            "close": 3191.0
          },
          {
            "trade_date": "20261023",
            "low": 3160.0,
            "high": 3243.0,
            "close": 3219.0
          }
        ]
      },
      "execution_permission": "not_evaluated"
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
        "CLOCKS"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "M2701 API到期01/15、20日均量1144190.35已核；实际经纪商更早强退和现有持仓期限仍需核。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "M2701 API到期01/15、20日均量1144190.35已核；实际经纪商更早强退和现有持仓期限仍需核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "保留10/15历史触发；本期10/23未触发。库存原表未读且现货反弹，不把旧弱势证据当现行持仓充分证明。",
          "gap": {
            "kind": "raw_data",
            "owner": "research",
            "next_action": "保留10/15历史触发；本期10/23未触发。库存原表未读且现货反弹，不把旧弱势证据当现行持仓充分证明。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "CLOCKS"
          ],
          "details": "原机会已取消且10/19到期；旧3310/3410仅诊断，不是可执行计划或实际成交。"
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "对真实M持仓核进口/美作物进展事件传导、报价和跳空压力；未确认真实账户或止损，不能推定已平。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "对真实M持仓核进口/美作物进展事件传导、报价和跳空压力；未确认真实账户或止损，不能推定已平。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
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
        "CLOCKS",
        "PRICE-M2701"
      ],
      "price_screening_date": "2026-10-23",
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
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
      "execution_permission": "not_evaluated"
    },
    {
      "candidate_id": "20261023-RB2701-trend-short-v3",
      "opportunity_id": "20261025-observe-RB2701-trend-short-v3",
      "trade_date": "2026-10-23",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "fresh prices and independent rebar economics plus numeric plan complete; current quotes and dynamic public execution parameters pending",
      "signal": "triggered",
      "signal_evidence_refs": [
        "PRICE-RB2701"
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
        "arithmetic_ref": "research/futures/weekly/2026-10-25/evidence/rb-plan-result.json"
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
        "PRICE-RB2701",
        "RB-INDUSTRY",
        "RB-PLAN",
        "PUBLIC-RULES",
        "CONTRACT-API"
      ],
      "not_evaluated_after_no_signal": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "PUBLIC-RULES",
            "CONTRACT-API"
          ],
          "details": "许可RB2701真实合约，官方到期月15日与API01/15一致；均量659726.95≥10000。11月时间退出早于交割临近；实际更早经纪商边界仍拟执行时核。"
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "PRICE-RB2701",
            "RB-INDUSTRY"
          ],
          "details": "10/23close3047<prior20low3051；同口径螺纹表需下降21.24、产量+0.84支持弱势，仍去库26.30为最强非致命反证，只作一次0.5。"
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "RB-PLAN",
            "PUBLIC-RULES"
          ],
          "details": "按固定61根ATR27.88435计算3034–3050、参考3047/3103、成本40、风险600；10/26–27有效；10/26入场最迟11/20，10/27则11/23。只用登记后时段，成交变化重算。"
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "已核公开规格/场次和3140压力情景gap1.6167>轻仓线1.5；动态RB2701板幅/交易所费用/保证金与可成交报价仍须补核，基于当前规则重做限板/滑点和绝对压力预算，未达研究执行完整。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "已核公开规格/场次和3140压力情景gap1.6167>轻仓线1.5；动态RB2701板幅/交易所费用/保证金与可成交报价仍须补核，基于当前规则重做限板/滑点和绝对压力预算，未达研究执行完整。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
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
        "G4",
        "G5",
        "G6"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "final_lots": null,
      "status": "incomplete",
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-CF2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-23",
      "contracts": [
        "CF2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh direct price early screen completed; later gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-CF2701"
      ],
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
          "evidence_refs": [
            "PRICE-CF2701"
          ],
          "details": "完整真实合约prior20严格双向条件均未触发；只早停当前价格路线，不裁定全品种零机会。"
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
      "status": "no_signal",
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-M2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-23",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh direct price early screen completed; later gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-M2701"
      ],
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
          "evidence_refs": [
            "PRICE-M2701"
          ],
          "details": "完整真实合约prior20严格双向条件均未触发；只早停当前价格路线，不裁定全品种零机会。"
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
      "status": "no_signal",
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-MA2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-23",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh direct price early screen completed; later gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-MA2701"
      ],
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
          "evidence_refs": [
            "PRICE-MA2701"
          ],
          "details": "完整真实合约prior20严格双向条件均未触发；只早停当前价格路线，不裁定全品种零机会。"
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
      "status": "no_signal",
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-SR2701-trend-current-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-23",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "fresh direct price early screen completed; later gates not evaluated",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-SR2701"
      ],
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
          "evidence_refs": [
            "PRICE-SR2701"
          ],
          "details": "完整真实合约prior20严格双向条件均未触发；只早停当前价格路线，不裁定全品种零机会。"
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
      "status": "no_signal",
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-MA2701-MA2705-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-23",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "month-specific numeric economic interval and5-20-session mechanism absent; not no_signal",
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
      "evidence_refs": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "有序两腿来源身份和日历原料已核；精确到期、双腿20日量和可执行配对报价待核。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "有序两腿来源身份和日历原料已核；精确到期、双腿20日量和可执行配对报价待核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "本期已推进经济成本与供需取证，单侧成本不等于双侧锚；未有可辩护数值区间/信号前冻结。",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "本期已推进经济成本与供需取证，单侧成本不等于双侧锚；未有可辩护数值区间/信号前冻结。",
            "due_at": "2026-10-30"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "锚未成立，缺经济失效SL、近侧目标、全区间净R和收敛期计划；不事后造锚。",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "锚未成立，缺经济失效SL、近侧目标、全区间净R和收敛期计划；不事后造锚。",
            "due_at": "2026-10-30"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "未来成案前冻结双腿报价/最大滑点/裸腿时限/撤单平腿及扩板提保压力。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "未来成案前冻结双腿报价/最大滑点/裸腿时限/撤单平腿及扩板提保压力。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
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
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-RB2701-RB2703-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-23",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "month-specific numeric economic interval and5-20-session mechanism absent; not no_signal",
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
      "evidence_refs": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "有序两腿来源身份和日历原料已核；精确到期、双腿20日量和可执行配对报价待核。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "有序两腿来源身份和日历原料已核；精确到期、双腿20日量和可执行配对报价待核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "本期已推进经济成本与供需取证，单侧成本不等于双侧锚；未有可辩护数值区间/信号前冻结。",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "本期已推进经济成本与供需取证，单侧成本不等于双侧锚；未有可辩护数值区间/信号前冻结。",
            "due_at": "2026-10-30"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "锚未成立，缺经济失效SL、近侧目标、全区间净R和收敛期计划；不事后造锚。",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "锚未成立，缺经济失效SL、近侧目标、全区间净R和收敛期计划；不事后造锚。",
            "due_at": "2026-10-30"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "未来成案前冻结双腿报价/最大滑点/裸腿时限/撤单平腿及扩板提保压力。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "未来成案前冻结双腿报价/最大滑点/裸腿时限/撤单平腿及扩板提保压力。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
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
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
      "execution_permission": "not_evaluated",
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      }
    },
    {
      "candidate_id": "20261023-SR2701-SR2705-economic-reversion-research-v3",
      "opportunity_id": null,
      "trade_date": "2026-10-23",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "month-specific numeric economic interval and5-20-session mechanism absent; not no_signal",
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
      "evidence_refs": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "有序两腿来源身份和日历原料已核；精确到期、双腿20日量和可执行配对报价待核。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "有序两腿来源身份和日历原料已核；精确到期、双腿20日量和可执行配对报价待核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "本期已推进经济成本与供需取证，单侧成本不等于双侧锚；未有可辩护数值区间/信号前冻结。",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "本期已推进经济成本与供需取证，单侧成本不等于双侧锚；未有可辩护数值区间/信号前冻结。",
            "due_at": "2026-10-30"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "锚未成立，缺经济失效SL、近侧目标、全区间净R和收敛期计划；不事后造锚。",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "锚未成立，缺经济失效SL、近侧目标、全区间净R和收敛期计划；不事后造锚。",
            "due_at": "2026-10-30"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "未来成案前冻结双腿报价/最大滑点/裸腿时限/撤单平腿及扩板提保压力。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "未来成案前冻结双腿报价/最大滑点/裸腿时限/撤单平腿及扩板提保压力。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当日真实权益、持仓/挂单、已用与预留风险、实收保证金/费用及压力执行限额；齐全后按同一计划运行size-v3。",
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
      "evaluated_at": "2026-10-25T01:10:57.364586+08:00",
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
      "item": "完成RB当前公开参数/报价和压力评估，保持原10/27截止；不等周更延窗",
      "owner": "research",
      "due_at": "before_execution",
      "required_evidence": [],
      "resolution": "pending"
    },
    {
      "item": "提供真实MA/M成交与止损/退出轨迹、当日账户；条件管理不推定成交",
      "owner": "user",
      "due_at": "before_execution",
      "required_evidence": [],
      "resolution": "pending"
    },
    {
      "item": "三V月份数值锚补件，不得用历史分位/单侧成本制造双侧锚",
      "owner": "research",
      "due_at": "2026-10-30",
      "required_evidence": [],
      "resolution": "pending"
    }
  ],
  "shadow_plans": [],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "WITHDRAWN-MA-G2",
      "reason": "继承10/12已采纳的当前产业pass撤回；本期MTO/低库分歧重评仍unknown，不恢复旧pass。",
      "affected_checks": [
        {
          "candidate_id": "20261009-MA2701-trend-long-v3",
          "rule_id": "G2"
        }
      ],
      "recalculation": "completed"
    }
  ],
  "continuity": {
    "catalog": "research/futures/weekly/2026-10-25/evidence/shared-sources/catalog.json",
    "reconciliation": "research/futures/weekly/2026-10-25/evidence/continuity-reconciliation.json",
    "reviewed_all_known_opportunities": true,
    "execution_reuse": false,
    "M_original_conflict_retained": true,
    "requires_plan_reassessment": [],
    "requires_method_reassessment": []
  },
  "risk_regime": "unknown",
  "performance_status": "not_automated"
}
```
