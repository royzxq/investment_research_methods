# 期货执行审计 · 2026-11-15

v3.0 / 维护 v2，current_framework，public_data，真实行情截至 11/13，账户未知。基线为实际 origin/main ccc23eb。前期按类型采纳 11/08 r2 及本地共享，交接冲突逐组核。 [市场研究](2026-11-15-market-research.md) · [变更判定](2026-11-15-change-decision.md) · [连续性裁决](evidence/continuity-reconciliation.json)

## 三条存量先复核

- MA 原 10/09 信号、10/11 18:14:54 登记、10/13 截止。10/13 H3278 低于原带 3289，撤回这一天按原计划入场的假设，11/09 只留作历史算术。10/12 日线覆盖 3289–3384，96 个可触报价最迟 10/20 触条件 SL，参考 3338/3139 的路径 10/19 L3131 首触。11/06 的条件时间界也已过。后续核实际退出，港库再累与厂库微降均不能恢复旧多。
- M 原 10/15 信号、同日 19:30:56 真实登记、10/19 截止，10/16 收 3281 越带已取消。原 3310/3410 只作诊断，未假设成案。WASDE 的首次报告后国内交易段为 11/11 日盘，T±1 为 11/10–12。美豆出口上调与期末库存下降对旧空头不利，实际仓位若有需按真实成本和退出复核。
- RB 原 10/23 信号、10/25 01:06:50.045735 登记、10/27 截止。原先参考 3047/3103 保留原档。10/27 H3044 使 3047 不可达，但 3034–3044 有日线交集。10/26 全带 17 档、10/27 11 档按原固定 ATR 距离各自重算。11/06 H3059 对当时条件 SL3072，不能把后续 SL3059 回填到 11/06。到 11/13 每条条件路径无价触，11/13 收盘下场条件值均 3059。原 11/20 或 11/23 时间界保留，与真实更早退出界取严格值。11/16 房地产数据与邯郸限产持续程度复核需求和压力。

完整日线仅证明日期级价格路径，实际到账、下单和盘中时序仍未知。不能用日线包络证明在登记以后成交。 [价格路径](evidence/holding-path-review.json) · [事件及交易场次](evidence/exchange-and-event-review.md)

## 本期五 T 与三 V

M/RB/MA/CF 当根双向未过前20日通道，各以 G2 早停。SR 的最后结算 5155 不是 T 取数口径，11/13 收盘 5146 跌破 5154。三 V 两腿最近 61 日齐、来源相符，因缺合格事前锚而未评估，继续留作经济研究。没有本期行情故障。没有完整账户和周内独立机会登记，市场可执行机会数及损益未知。 [机械刷新](../../refresh/2026-11-15/2026-11-15-signal-refresh.md) · [月差锚维护](../../anchors/2026-11-15/2026-11-15-anchors.json)

## SR2701 空头条件诊断

- G1 20 日均量 362440.65 手。API 末日 1/14，与按官方第十个交易日推算的 1/15 有差异；按保守 1/14 算，12/11 仍距末日 23 个交易日。最新盘口及更早适用边界须再核。
- G2 价格与最低独立经济链均成立。年度产量上修及云南实际开榨支持供给增量，广西陈糖清库、进口倒挂和可能的全球供给下修构成反证。按这一分歧，若进入实际 sizing 市场风险折减只计一次，账户状态/整体暴露档位未知。
- G3 仅登记研究观察，原信号日 11/13、原截止 11/17。参考价 5146，允许 5121–5153（严格低于 5154），参考初始 SL 5248，实际 Entry 每 +1 对应初始 SL +1。乘数 10、tick 1，示意费用 12 元往返、滑点 20 元起，参考纸面每手风险 1052 元。收盘后依据过去 10 日只收紧，若 11/16 实际入场第 20 日为 12/11，取更早止损、经济证伪或约束。实际入场价、可执行计划和手数保持空。冻结的是信号研究登记及取消处置。
- G4 11/13 夜盘属于 11/16，已过且该夜最后报价 5154 已离开严格突破侧。据此撤销原信号入场用途，11/16 不等待回价；当前实时盘口仍未知。USDA FAS 全球报告为直接事件，11/17–19 交易日禁新开，原窗口不延到 11/20。11/16 发布前可查的 5% 板幅按正式 5155 结算对应约 5413 上限。若锁板直跳该价且费用预算暂同，压力损失 2702 元/手，约为参考纸面风险 2.57 倍，超过常规 2.0；若此场景经真实盘口/事件证据判适用，则不得新开。它是尾部压力敏感性，不凭板幅证明当前可成交或场景概率。至少另核可执行压力价、实际报价/点差、订单出场方案与动态限仓。
- G5/G6 当前真实权益、全部持仓挂单、止损、实收保证金、限仓、绝对压力金额均未知。未评估真实容量，不能发布手数。旧影子回放不支持该版本收益归因。

[SR 算术](evidence/price-and-plan-calculation.json) · [产业与规则](evidence/ma-sr-cf-public.md) · [事件与参考报价](evidence/exchange-and-event-review.md)

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-11-15",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
  "execution_permission": "not_evaluated",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "ccc23ebc82357ee4bb91d0df4e2d4b6eb29056ca",
    "canonical_full_sha256": "93a945850259452f3d8f036c4c95a84486f953c8ed4b9c210ab723188bfdd9b4"
  },
  "snapshot": {
    "market_trade_date": "2026-11-13",
    "market_captured_at": "2026-11-15T01:02:50.365123+08:00",
    "source_artifacts": [
      {
        "path": "research/futures/refresh/2026-11-15/2026-11-15-signal-refresh.json",
        "sha256": "c85982209e8fa36436702adbb86e7c806d33cadbc2a46e6635f134cf785d4a43"
      },
      {
        "path": "research/futures/refresh/2026-11-15/evidence/2026-11-15-signal-refresh/market-inputs.json",
        "sha256": "42c1654d8d13c7afa8d25f0a14da1537fe2488b0aed3f2ee1953f68274811ea4"
      },
      {
        "path": "research/futures/weekly/2026-11-15/evidence/tushare-supplement.json",
        "sha256": "44da0309b7ded5886cf458dfd7fd565066556460e41326f1ccfff4cc41839413"
      }
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
      "五T最新收盘",
      "五组V两腿原料",
      "三条已知旧计划条件路径"
    ],
    "missing_scope": [
      "实际临场报价和执行压力",
      "真实账户及成交",
      "11/09–12逐日正式机会审计"
    ],
    "research_only_scope": [
      "MA/RB/SR分月份有序V对",
      "M高频进口强因果子线路"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "SHARED",
      "metric": "采纳冲突和逐组裁决",
      "value": "15条、20组、1个M原钟冲突",
      "unit": "带单位的分项事实或日期（见值和底稿）",
      "observation_date": "2026-11-15",
      "published_at": "2026-11-15T01:17:47.773776+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/continuity-reconciliation.json",
      "original_source": "futures_continuity / 当期复核",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "OLD-MA-PATH",
      "metric": "原窗价格与条件止损",
      "value": "10/13 H3278，原带下限3289；10/12条件路径最迟10/20触发；参考10/19",
      "unit": "CNY/tonne",
      "observation_date": "2026-10-20",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/holding-path-review.json",
      "original_source": "Tushare Pro与现行策略",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "historical"
    },
    {
      "evidence_id": "OLD-M-PATH",
      "metric": "原观察处置",
      "value": "10/16 close3281越原研究带，旧入场取消，原10/19截止",
      "unit": "CNY/tonne",
      "observation_date": "2026-10-16",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/holding-path-review.json",
      "original_source": "Tushare Pro与同日采纳",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "historical"
    },
    {
      "evidence_id": "OLD-RB-PATH",
      "metric": "原窗价格与条件止损",
      "value": "10/27 H3044；11/13收盘推下场参考3059",
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/holding-path-review.json",
      "original_source": "Tushare Pro与现行策略",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "MA-ALT-OLD",
      "metric": "撤回原计划10/13入场的可达性假设",
      "value": "10/13可作为实际原计划入场日且可用11/09条件上限",
      "unit": null,
      "observation_date": "2026-10-13",
      "published_at": null,
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/continuity-objects/3a92eda6afdbdacda621c2045bb50ac9629b79f6209c8708fb54dd8082723310.blob",
      "original_source": "旧采纳的备选路径",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "RB-ALT-OLD",
      "metric": "撤回10/27原参考3047可达性",
      "value": "用3047参考报价外推10/27原带可达路径",
      "unit": "CNY/tonne",
      "observation_date": "2026-10-27",
      "published_at": null,
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/continuity-objects/3a92eda6afdbdacda621c2045bb50ac9629b79f6209c8708fb54dd8082723310.blob",
      "original_source": "旧计划跨备选日期的报价假设",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "CAL",
      "metric": "三所按所别开市日期与精确基础合约",
      "value": "10/09至2027/01/31三所日期与原包一致；1/14、1/15到期口径保留",
      "unit": "带单位的分项事实或日期（见值和底稿）",
      "observation_date": "2026-11-15",
      "published_at": "2026-11-15T01:05:31.173371+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/tushare-supplement.json",
      "original_source": "Tushare Pro",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "EVENT",
      "metric": "相关重大事项及场次",
      "value": "M WASDE T=11/11；RB 邯郸执行与11/16统计排期；SR FAS T=11/18",
      "unit": "带单位的分项事实或日期（见值和底稿）",
      "observation_date": "2026-11-15",
      "published_at": "2026-11-15",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/exchange-and-event-review.md",
      "original_source": "USDA / 交易所 / 统计局 / 调研",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "SUPPLY-SR",
      "metric": "中国食糖供给上修与国内开榨",
      "value": "26/27产量1360万，云南11/12开榨5家，昆明5130–5150；国内缺口230万与陈糖去库限制",
      "unit": "带单位的分项事实或日期（见值和底稿）",
      "observation_date": "2026-11-12",
      "published_at": "2026-11-13T11:37:00+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/ma-sr-cf-public.md",
      "original_source": "农业农村部、糖网、沐甜与泛糖",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PLAN-SR",
      "metric": "固定信号和条件算术",
      "value": "5121–5153，参考5146，SL5248，条件20日最晚12/11",
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-15T01:17:47.773776+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/price-and-plan-calculation.json",
      "original_source": "futures_strategy.py validate-plan",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PUBLIC-MRB",
      "metric": "供需证据与反证",
      "value": "M 11/06可比库存下降，RB 11/12产需同降且去库",
      "unit": "带单位的分项事实或日期（见值和底稿）",
      "observation_date": "2026-11-12",
      "published_at": "2026-11-13",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/m-rb-public.md",
      "original_source": "原研究机构及公开产销存",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ANCHORS",
      "metric": "本期有序对原料及经济锚待补",
      "value": "MA/RB/SR无合格事前经济锚",
      "unit": "带单位的分项事实或日期（见值和底稿）",
      "observation_date": "2026-11-15",
      "published_at": "2026-11-15",
      "source_url_or_file": "research/futures/anchors/2026-11-15/2026-11-15-anchors.json",
      "original_source": "周度研究",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "QUOTE-SR-OLD",
      "metric": "周五夜盘最后价旁证",
      "value": 5154,
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-13T22:59:59+08:00",
      "source_url_or_file": "research/futures/weekly/2026-11-15/evidence/exchange-and-event-review.md",
      "original_source": "第三方冻结快照",
      "price_basis": "11/16交易日未完成时的夜盘最后快照",
      "comparison_basis": "自然日记录时刻；交易日归属11/16，记录为未完成交易日夜盘末报价",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-CF2701",
      "metric": "合约收盘及前20日通道",
      "value": {
        "close": 15555.0,
        "prior20_low": 15030.0,
        "prior20_high": 15945.0,
        "atr20": 200.16366185908458
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-15/2026-11-15-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily / futures_strategy",
      "price_basis": "close; prior20 excludes signal date",
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-M2701",
      "metric": "合约收盘及前20日通道",
      "value": {
        "close": 3147.0,
        "prior20_low": 3053.0,
        "prior20_high": 3330.0,
        "atr20": 51.130368919143635
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-15/2026-11-15-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily / futures_strategy",
      "price_basis": "close; prior20 excludes signal date",
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-MA2701",
      "metric": "合约收盘及前20日通道",
      "value": {
        "close": 3266.0,
        "prior20_low": 3016.0,
        "prior20_high": 3615.0,
        "atr20": 127.93401332502098
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-15/2026-11-15-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily / futures_strategy",
      "price_basis": "close; prior20 excludes signal date",
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-RB2701",
      "metric": "合约收盘及前20日通道",
      "value": {
        "close": 3035.0,
        "prior20_low": 2988.0,
        "prior20_high": 3096.0,
        "atr20": 27.15170813162726
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-15/2026-11-15-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily / futures_strategy",
      "price_basis": "close; prior20 excludes signal date",
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "PRICE-SR2701",
      "metric": "合约收盘及前20日通道",
      "value": {
        "close": 5146.0,
        "prior20_low": 5154.0,
        "prior20_high": 5430.0,
        "atr20": 50.879444253502236
      },
      "unit": "CNY/tonne",
      "observation_date": "2026-11-13",
      "published_at": "2026-11-15T01:02:50.365123+08:00",
      "source_url_or_file": "research/futures/refresh/2026-11-15/2026-11-15-signal-refresh.json",
      "original_source": "Tushare Pro fut_daily / futures_strategy",
      "price_basis": "close; prior20 excludes signal date",
      "comparison_basis": null,
      "role": "required_model",
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
      "data_feasibility_reason": "缺执行或必要经济输入",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "CAL"
          ],
          "details": "旧合约身份已核，若有真实持仓须核最新交割和真实盘口限制。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "旧合约身份已核，若有真实持仓须核最新交割和真实盘口限制。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "OLD-MA-PATH"
          ],
          "details": "仍累库而生产企业去库，旧G2当前适用性不恢复。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "仍累库而生产企业去库，旧G2当前适用性不恢复。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "OLD-MA-PATH",
            "SHARED"
          ],
          "details": "原10/13截止；全天H3278低于原带，撤回备选路径；10/12条件最晚10/20触止损，11/06时间界已过。",
          "diagnostic_evidence_refs": [
            "MA-ALT-OLD"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EVENT"
          ],
          "details": "事件和条件日历已复核；若账上仍有仓，按实际报价、有效止损、动态参数和事件压力复核。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "事件和条件日历已复核；若账上仍有仓，按实际报价、有效止损、动态参数和事件压力复核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
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
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "incomplete",
      "evidence_refs": [
        "OLD-MA-PATH",
        "SHARED",
        "EVENT"
      ],
      "entry_window_state": "expired",
      "position_status": "unknown",
      "registered_at": "2026-10-11T18:14:54+08:00",
      "performance_status": "not_automated"
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
      "data_feasibility_reason": "缺执行或必要经济输入",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "CAL"
          ],
          "details": "旧合约身份已核，若有真实持仓须核最新交割和真实盘口限制。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "旧合约身份已核，若有真实持仓须核最新交割和真实盘口限制。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "OLD-M-PATH",
            "PUBLIC-MRB"
          ],
          "details": "国内去库和WASDE偏强反证，旧方向不得以新产业证据重新开启。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "国内去库和WASDE偏强反证，旧方向不得以新产业证据重新开启。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "OLD-M-PATH",
            "SHARED"
          ],
          "details": "10/16越带取消，原10/19截止已过；3310/3410只作诊断。"
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EVENT"
          ],
          "details": "事件和条件日历已复核；若账上仍有仓，按实际报价、有效止损、动态参数和事件压力复核。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "事件和条件日历已复核；若账上仍有仓，按实际报价、有效止损、动态参数和事件压力复核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
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
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "incomplete",
      "evidence_refs": [
        "OLD-M-PATH",
        "SHARED",
        "EVENT"
      ],
      "entry_window_state": "cancelled_and_expired",
      "position_status": "unknown",
      "registered_at": "2026-10-15T19:30:56+08:00",
      "performance_status": "not_automated"
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
      "data_feasibility_reason": "缺执行或必要经济输入",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "CAL"
          ],
          "details": "旧合约身份已核，若有真实持仓须核最新交割和真实盘口限制。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "旧合约身份已核，若有真实持仓须核最新交割和真实盘口限制。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "OLD-RB-PATH",
            "PUBLIC-MRB"
          ],
          "details": "需求走弱但减产低库与环保限制反证空头，实际退出仍未知。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "需求走弱但减产低库与环保限制反证空头，实际退出仍未知。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "OLD-RB-PATH",
            "SHARED"
          ],
          "details": "10/27截止；当日3047不可达，重算3034–3044，下场参考3059，保留11/20或11/23条件上限。",
          "diagnostic_evidence_refs": [
            "RB-ALT-OLD"
          ]
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EVENT"
          ],
          "details": "事件和条件日历已复核；若账上仍有仓，按实际报价、有效止损、动态参数和事件压力复核。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "事件和条件日历已复核；若账上仍有仓，按实际报价、有效止损、动态参数和事件压力复核。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
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
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "incomplete",
      "evidence_refs": [
        "OLD-RB-PATH",
        "SHARED",
        "EVENT"
      ],
      "entry_window_state": "expired",
      "position_status": "unknown",
      "registered_at": "2026-10-25T01:06:50.045735+08:00",
      "performance_status": "not_automated"
    },
    {
      "candidate_id": "20261113-CF2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-13",
      "contracts": [
        "CF2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "当前价格直接确认无需进入执行，产业/盘口未全面判定",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-CF2701"
      ],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-CF2701"
          ],
          "details": "完整同合约日线证实收盘未向任一方向越过前20日通道。"
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "no_signal",
      "evidence_refs": [
        "PRICE-CF2701"
      ]
    },
    {
      "candidate_id": "20261113-M2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-13",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "当前价格直接确认无需进入执行，产业/盘口未全面判定",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-M2701"
      ],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-M2701"
          ],
          "details": "完整同合约日线证实收盘未向任一方向越过前20日通道。"
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "no_signal",
      "evidence_refs": [
        "PRICE-M2701"
      ]
    },
    {
      "candidate_id": "20261113-MA2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-13",
      "contracts": [
        "MA2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "当前价格直接确认无需进入执行，产业/盘口未全面判定",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-MA2701"
      ],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-MA2701"
          ],
          "details": "完整同合约日线证实收盘未向任一方向越过前20日通道。"
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "no_signal",
      "evidence_refs": [
        "PRICE-MA2701"
      ]
    },
    {
      "candidate_id": "20261113-RB2701-trend-screen-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-13",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "当前价格直接确认无需进入执行，产业/盘口未全面判定",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-RB2701"
      ],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-RB2701"
          ],
          "details": "完整同合约日线证实收盘未向任一方向越过前20日通道。"
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
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "no_signal",
      "evidence_refs": [
        "PRICE-RB2701"
      ]
    },
    {
      "candidate_id": "20261113-SR2701-trend-short-v3",
      "opportunity_id": "20261113-observe-SR2701-trend-short-v3",
      "trade_date": "2026-11-13",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "价格确认与最低经济依据已具备，已观察日夜盘末价失去严格突破侧，第二日另被事件阻止；真实账户和报价未知。",
      "signal": "triggered",
      "signal_evidence_refs": [
        "PRICE-SR2701"
      ],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "CAL",
            "PLAN-SR"
          ],
          "details": "20日均量362440.65，12/11距较早到期23日。精确到期口径有冲突，需核实际报价、容量和适用提前界。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "20日均量362440.65，12/11距较早到期23日。精确到期口径有冲突，需核实际报价、容量和适用提前界。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "PRICE-SR2701",
            "SUPPLY-SR"
          ],
          "details": "5146低于前20日低5154。产量预期上修与云南开榨支持最低因果，陈糖去库、进口倒挂和全球糖报告构成非致命分歧。"
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PLAN-SR",
            "QUOTE-SR-OLD"
          ],
          "details": "可追溯的11/16交易日周五夜盘最后报价5154不再严格低于5154。采用该已观测报价撤销原信号的入场用途；不得等待回价或延长11/17截止。"
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EVENT",
            "QUOTE-SR-OLD"
          ],
          "details": "11/17已证实事件窗内禁止新开。11/16实际可执行报价、压力价与动态限制仍未知，不为已撤入场用途制作许可。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "后续独立新信号才核报价、执行压力和退出预案；11/17已证实禁新开。",
            "due_at": "2026-11-16"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
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
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
        "registration_scope": "research_observation_and_entry_disposition_only_no_execution_plan"
      },
      "status": "incomplete",
      "evidence_refs": [
        "PRICE-SR2701",
        "SUPPLY-SR",
        "PLAN-SR",
        "EVENT"
      ],
      "entry_window_state": "cancelled_quote_lost_breakout",
      "registered_at": "2026-11-15T01:17:47.773776+08:00",
      "eligible_session_condition": [],
      "explicitly_excluded_sessions": [
        "2026-11-13 21:00–23:00 prior to registration",
        "2026-11-16 day session: cancelled after latest observed quote 5154 lost the strict breakout",
        "2026-11-17 trading date, event prohibition"
      ],
      "indicative_calculation_ref": "research/futures/weekly/2026-11-15/evidence/price-and-plan-calculation.json",
      "holding_position_management_if_any": "相关报告前重做压力且不能承担则减退；原T止损及条件12/11最晚界独立核。"
    },
    {
      "candidate_id": "20261113-MA2701-MA2705-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-13",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "各腿原料已恢复，经济锚和机制尚缺",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "CAL",
            "ANCHORS"
          ],
          "details": "两腿身份和日期一致；还须核具体交付月份的流动性、期限与报价。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "两腿身份和日期一致；还须核具体交付月份的流动性、期限与报价。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ANCHORS"
          ],
          "details": "本时点缺信号前冻结经济锚和可辩护的双侧区间，价格确认未评估。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "本时点缺信号前冻结经济锚和可辩护的双侧区间，价格确认未评估。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "先实际研究适用经济失效、滑点、最终目标和可成交区间，再建计划。",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "先实际研究适用经济失效、滑点、最终目标和可成交区间，再建计划。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EVENT"
          ],
          "details": "待有候选再核适用事件、配对压力及裸腿处置。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "待有候选再核适用事件、配对压力及裸腿处置。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
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
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "incomplete",
      "evidence_refs": [
        "ANCHORS",
        "CAL"
      ]
    },
    {
      "candidate_id": "20261113-RB2701-RB2703-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-13",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "各腿原料已恢复，经济锚和机制尚缺",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "CAL",
            "ANCHORS"
          ],
          "details": "两腿身份和日期一致；还须核具体交付月份的流动性、期限与报价。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "两腿身份和日期一致；还须核具体交付月份的流动性、期限与报价。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ANCHORS"
          ],
          "details": "本时点缺信号前冻结经济锚和可辩护的双侧区间，价格确认未评估。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "本时点缺信号前冻结经济锚和可辩护的双侧区间，价格确认未评估。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "先实际研究适用经济失效、滑点、最终目标和可成交区间，再建计划。",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "先实际研究适用经济失效、滑点、最终目标和可成交区间，再建计划。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EVENT"
          ],
          "details": "待有候选再核适用事件、配对压力及裸腿处置。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "待有候选再核适用事件、配对压力及裸腿处置。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
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
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "incomplete",
      "evidence_refs": [
        "ANCHORS",
        "CAL"
      ]
    },
    {
      "candidate_id": "20261113-SR2701-SR2705-V-v3",
      "opportunity_id": null,
      "trade_date": "2026-11-13",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "各腿原料已恢复，经济锚和机制尚缺",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_at": "2026-11-15T01:17:47.773776+08:00",
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "CAL",
            "ANCHORS"
          ],
          "details": "两腿身份和日期一致；还须核具体交付月份的流动性、期限与报价。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "两腿身份和日期一致；还须核具体交付月份的流动性、期限与报价。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ANCHORS"
          ],
          "details": "本时点缺信号前冻结经济锚和可辩护的双侧区间，价格确认未评估。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "本时点缺信号前冻结经济锚和可辩护的双侧区间，价格确认未评估。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "先实际研究适用经济失效、滑点、最终目标和可成交区间，再建计划。",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "先实际研究适用经济失效、滑点、最终目标和可成交区间，再建计划。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "EVENT"
          ],
          "details": "待有候选再核适用事件、配对压力及裸腿处置。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "待有候选再核适用事件、配对压力及裸腿处置。",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "核实际账户权益、净值、持仓、挂单、实收、限仓及可用资金。",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "真实入场成本、压力金额及账户齐备后按size-v3取风险、保证金、限仓和执行容量最严。",
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
      "not_evaluated_after_no_signal": [],
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
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
      "status": "incomplete",
      "evidence_refs": [
        "ANCHORS",
        "CAL"
      ]
    }
  ],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "MA-ALT-OLD",
      "reason": "原10/13截止；全天H3278低于原带，撤回备选路径；10/12条件最晚10/20触止损，11/06时间界已过。",
      "recalculation": "completed",
      "affected_checks": [
        {
          "candidate_id": "20261009-MA2701-trend-long-v3",
          "rule_id": "G3"
        }
      ]
    },
    {
      "withdrawn_evidence_id": "RB-ALT-OLD",
      "reason": "10/27截止；当日3047不可达，重算3034–3044，下场参考3059，保留11/20或11/23条件上限。",
      "recalculation": "completed",
      "affected_checks": [
        {
          "candidate_id": "20261023-RB2701-trend-short-v3",
          "rule_id": "G3"
        }
      ]
    }
  ],
  "unresolved_items": [
    {
      "item": "SR原入场用途已撤；下个独立信号需核真实报价、报告适用、执行压力和强制边界",
      "owner": "research",
      "due_at": "next_report",
      "required_evidence": [
        "EVENT",
        "PLAN-SR"
      ],
      "resolution": "pending"
    },
    {
      "item": "确认旧仓与当日账户、有效止损和实际退出；实际收益未知",
      "owner": "user",
      "due_at": "before_execution",
      "required_evidence": [],
      "resolution": "pending"
    },
    {
      "item": "按明确月份的可交割成本和5–20日机制推进三V",
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
