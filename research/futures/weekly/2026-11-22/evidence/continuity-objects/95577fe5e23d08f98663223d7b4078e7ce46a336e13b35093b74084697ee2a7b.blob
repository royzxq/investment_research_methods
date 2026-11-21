# 本周期货执行诊断：v3.0

研究日2026-10-11（Asia/Shanghai），行情截至10/09；generator=codex，现行框架v3.0、修订6cc3b03。配套[市场研究](2026-10-11-market-research-r2.md)及三份分项证据。保留同日旧审计，本文件是隔离重评；没有交易、持仓或账户空仓假设。

## 本期结论与筛选

**本次记录8条路线：6条机械价格条件未触发，2条研究未完成；ready=0、awaiting_account=0。** 这是已覆盖路线的状态，不是全市场可执行机会总数（保持null）。没有一条仅因账户缺失而停在研究阶段。三条V均未建立合格经济锚；RB/SR因双向反转条件都false可先结束本次价格筛选，不将已知未触发改成未知。

| T合约 | 10/09 close | 用于10/09判断的前20日高/低 | ATR20 | HV20/HV60 | 20日均量/手 | 到期剩余交易日 | 机械结论 |
|---|---:|---:|---:|---:|---:|---:|---|
| M2701 | 3402 | 3502 / 3327 | 49.17175 | 1.20055 | 1381405.65 | 68 | no_signal |
| RB2701 | 3080 | 3183 / 3060 | 30.24375 | 1.07275 | 706042.25 | 68 | no_signal |
| MA2701 | 3338 | 3200 / 2817 | 99.16456 | 1.08457 | 724224.95 | 67 | 历史机械long；当前v3候选incomplete |
| SR2701 | 5491 | 5510 / 5305 | 53.88748 | 1.19907 | 418491.60 | 67 | no_signal |
| CF2701 | 15790 | 16955 / 15490 | 215.75233 | 1.05939 | 331489.95 | 67 | no_signal |

价格及ATR单位元/吨。T使用close、真实high/low；价差使用settle，不混口径。波动比均未达到>1.3，**不能因此宣称公开事件/跳空风险已通过**。当前范围、真实合约、历史日均量及剩余期限已有子项证据；整个G1并未标pass，实际入场日、可持有期和公开提前退出边界仍要重核，账户专属更早限制后置G5。

v3于10/11生效，10/09机械信号不能追认为当时新版建议。MA保留“已知价格突破但时间资格失败”，其他研究条件与账户缺项同时保留，故是incomplete而不是伪造ready或blocked。最早10/12收盘产生生效后新信号。

| V路线，近减远 | 09/30、10/08、10/09结算差，元/吨 | 必要价格反转判断 | 本次状态 / 模型可行性 |
|---|---|---|---|
| MA2701−MA2705 | 279、328、416 | short的416<279不成立；long的416>328成立，但是否低于锚下界未知 | incomplete / research_only |
| RB2701−RB2703 | 2、4、2 | short要求2<2；long要求2>4，均不成立 | no_signal / 经济锚research_only |
| SR2701−SR2705 | −78、−75、−77 | short要求−77<−78；long要求−77>−75，均不成立 | no_signal / 经济锚research_only |

仅有价差日线不证明两腿20日均量均达标。V远腿流动性未核，G1没有标pass。三条经济锚、收敛机制及失效价均未成案，目标与净R为空；MA2705−2709、RB2703−2705仅为移仓准备资料，不重复计作本期候选。

## 两份条件观察计划

以下优先完善M/RB，不是已触发订单。**阈值仅用于10/12收盘；10/13以后须每日滚动，不能整周沿用。** 不提前填写未来signal_date、实际Entry/SL或最终手数。若另一方向先确认，以新的经济解释重新研究，不强行维持偏空观点。

### 观察一：RB2701顺势空头

- 价格条件：10/12完整日收盘<3060，即按tick=1收于3059或以下；盘中下破、收盘恰好3060均不算。
- 产业条件：当前假期周同口径累库、节后首日现货偏弱提供初步解释。触发时使用最新适用事实；若没有更新，不可隐藏其假期口径。无需等待所有周报到齐，但若正常周成交/去库已明确推翻偏弱逻辑，则G2失败。
- 最强反证：低同比供应、低同比库存；假期表需不是终端成交。取消空头解释的条件是可核需求恢复/减产使库存下降且现货转强，而非仅凭价格上涨写基本面改善。
- 若10/12收盘触发且其余条件通过，有效入场交易日为10/13、10/14；首段通常为10/12 21:00夜盘。已核资料没有与RB直接相关的新重大供给事件窗口，但入场前仍须复核，不能宣称事件全集已排除。

### 观察二：M2701顺势空头

- 价格条件：10/12完整日收盘<3327，即3326或以下；盘中跌破不算。
- 必要产业补件：取得一项当前国内证据解释空头传导，例如压榨恢复带来同样本粕累库、提货走弱或当地基差走弱。不要求三项齐全；USDA温和偏空本身不足以替代这一步。国内已核实际压榨下降是最强反证。
- 取消条件：实际供应下降持续并带来当地基差走强/库存收紧，或新的数据推翻宽松传导。若先向上突破3502，必须另以国内供应减少/需求改善解释多头，不能用国产豆减产标题直接翻多。
- WASDE国内事件T=10/12，10/12和10/13不新开。若10/12收盘触发，10/13、10/14原本是两个有效入场日；只有10/14交易日仍可评估，通常自10/13 21:00夜盘开始。该日错过或条件未齐则信号过期，不顺延至10/15。

### 触发后两份计划共用的计算与退出

将信号日收盘记为C，固定61根日线重算ATR=A，前20日低点L。短仓有效报价区间为 `[向上取tick(C−0.5A), 向下取tick(min(C+0.5A,L−tick))]`；为空则不能入场。实际Entry确定后，SL=`向上取tick(Entry+2A)`。必须仍在突破侧且只限后两个真实交易日；不预设固定止盈，`targets=null`，也不对T设净R门。

只作量级参考：10/09的2ATR为RB约60.49元/吨、M约98.34元/吨，按10吨/手分别约604.87、983.44元的未取整价格距离风险。**这些不是未来信号日止损或最终每手风险**；实际需重新取整并计往返手续费、至少2个tick价值的滑点，以及跳空/涨跌停压力。入场后每个完整日收盘，用最近10个完整日最高high作下一时段短仓跟踪止损，只收紧，最长20个交易日（入场日第1日）；退出不得晚于剩余期限跌破20日和更早适用边界。

当前账户未知，权益E、B=3.5%E及实际剩余预算均未核，最终手数null。成案后用size-v3：单笔与组合上限均以B为基础；实际持仓/待开候选出现相关重大事件持续风险或高波动时，组合再封顶min(B,5000元)。策略因子0.7；高波动/持续相关事件/非致命证据冲突的市场因子取0.5且最多折减一次，exchange_buffer按当日实际规则及经纪商实收取0.8或1。金额预算汇合后只向下取整一次。当前risk_regime仍unknown，不因历史HV比低于1.3自动判normal。风险、60%保证金上限、提保组20%上限、80%限仓及执行/压力容量取严，扣除全部已占及挂单保留风险；不以配置资金代替真实账户。RB/M正常跳空警戒/淘汰比1.5/2.0，事件窗内淘汰线1.3且本就不新开。若其他候选MA跨周末，另核无有效对冲单仓风险≤B×30%，不能默认满足。

## 其余品种下一次机械刷新

| 合约 | 10/12严格收盘突破所需最小价格 | 研究解释 |
|---|---|---|
| MA2701 | 多≥3403；空≤2820 | 10/09最高价3402已进入下一日通道。旧3200不能继续当新触发线；偏多观察，补当前公开执行参数和供给传导 |
| SR2701 | 多≥5511；空≤5304 | 双向观察，不因广西高结转直接开空 |
| CF2701 | 多≥16905；空≤15485 | tick=5，下一日高线为16900，和10/09所用16955不同 |

这只是池内信号表，不是第三份完整条件计划。未部署逐日监控，后续须在交易日收盘或入场前刷新；本周报告不能证明周内未来两日信号已被持续覆盖。

## 执行来源与未完成项

- RB产品与仓单规则已读[上期所细则](https://www.shfe.com.cn/regulation/exchangerules/productrules/202512/t20251231_829962.html)：10吨/手、tick=1；仓库实物90日有效且45日内入库，厂库仓单180日，不能不核货龄就构造1–3月无风险carry锚。假期恢复另按[上期所公告](https://www.shfe.com.cn/publicnotice/notice/202609/t20260921_833503.html)及实际非单边市条件核。
- M假期风险规则已读[中信完整转大商所通知](https://www.citicsf.com/e-futures/content/000204/825671)：节日期间8%涨跌停、10%交易所保证金；恢复前标准的公告条件为持仓最大合约出现首个非单边市交易日后结算，恢复表M为6%/7%。这不证明实际逐合约恢复已完成，也不是用户经纪商实收。
- MA/SR/CF公开参数已有近期公司公告，见分项证据；MA10/12公司表与10/09临时表已不同，当前交易所适用恢复及全部限仓范围仍待核。此项由研究方补；用户账户专属保证金放G5，不回填G4。
- 10/12收盘是下一次价格/产业复核节点，10/16为节后正常周研究复核截止；均是本报告建议的复核节点，不是已创建任务或来源承诺发布日期。账户仅在G1–G4成案时再请求。
- v3尚无本轮前瞻成交记录；`shadow_plans=[]`、`performance_status=not_automated`。未使用旧固定TP引擎制造v3胜率、收益或“避免亏损”结论。

## 机器审计

下列为唯一schema 3机器块。机械筛选与经济模型可得性分开；no_signal早停不表示其余门通过。校验只证明结构一致，不能证明来源真实性、未来获利或执行许可。

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-11",
  "research_mode": "public_data",
  "assessment_scope": "current_framework_initial_screening",
  "generator": "codex",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v3.0",
    "revision": "6cc3b03"
  },
  "snapshot": {
    "market_trade_date": "2026-10-09",
    "market_captured_at": "2026-10-11T12:03:11.615481+08:00",
    "source_artifacts": [
      "research/futures/snapshots/2026-10-11-data-snapshot.txt",
      "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-market-inputs-codex.json",
      "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-screening-codex.json",
      "research/futures/weekly/2026-10-11/evidence/v3-r2/2026-10-11-supplied-snapshot-codex.txt"
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
      "5个品种T真实合约价格筛选",
      "3条同品种V结算价反转筛选",
      "M/RB重点产业研究及两份条件观察",
      "MA/SR/CF最小产业背景"
    ],
    "missing_scope": [
      "10/11生效后前瞻完整日尚未到来",
      "本期M空头国内传导",
      "全部完整执行参数/报价/压力计划",
      "真实账户"
    ],
    "research_only_scope": [
      "MA/RB/SR V经济锚及5–20日机制"
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
      "metric": "当前方法及前瞻生效边界",
      "value": {
        "version": "v3.0",
        "effective_date": "2026-10-11",
        "revision": "6cc3b03"
      },
      "unit": "版本/日期",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11",
      "source_url_or_file": "framework/futures_framework.md#r-v3-workflow",
      "original_source": "仓库canonical",
      "price_basis": "not_price",
      "comparison_basis": "首次生效后的完整行情日方可登记前瞻信号",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
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
    }
  ],
  "candidates": [
    {
      "candidate_id": "20261009-M2701-trend-short-v3",
      "opportunity_id": "20261011-observe-M2701-trend-short-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "M2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "价格输入齐全且未触发；若出现空头信号，本期国内供应传导仍需一项有效证据",
      "signal": "not_triggered",
      "signal_evidence_refs": [
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
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
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
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-M2701",
        "FRAMEWORK",
        "PRICE-M2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "observation_plan": {
        "registered_at": "2026-10-11",
        "signal_date": null,
        "threshold_trade_date": "2026-10-12",
        "close_strictly_below": 3327,
        "minimum_tick_price_at_or_below": 3326,
        "economic_condition": "本期USDA背景需传至国内：实际压榨/粕库存/提货/当地基差的一条可核供应宽松链；保留假期实际压榨下降反证",
        "refresh_required": [
          "逐日滚动20日通道",
          "固定61根ATR",
          "最新适用产业支持和反证",
          "公开规则/报价/费用/压力场景",
          "实际交易日入场有效期",
          "G1–G4成案后实际账户及size-v3"
        ],
        "conditional_valid_entry_dates": [
          "2026-10-13",
          "2026-10-14"
        ],
        "conditional_event_eligible_dates": [
          "2026-10-14"
        ],
        "event_qualification": "只对10/12真实收盘新触发成立；入场前核新增直接相关事件；日期不是已经成立的计划",
        "targets": null,
        "entry": null,
        "stop": null,
        "latest_exit_date": null
      },
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
    {
      "candidate_id": "20261009-RB2701-trend-short-v3",
      "opportunity_id": "20261011-observe-RB2701-trend-short-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "RB2701"
      ],
      "strategy": "trend",
      "direction": "short",
      "evidence_quality": "weak",
      "data_feasibility": "available",
      "data_feasibility_reason": "本次价格与最低背景可读；无信号早停不表示完整执行输入齐全",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "PRICE-RB2701"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-RB2701"
          ],
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
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
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-RB2701",
        "FRAMEWORK",
        "PRICE-RB2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "observation_plan": {
        "registered_at": "2026-10-11",
        "signal_date": null,
        "threshold_trade_date": "2026-10-12",
        "close_strictly_below": 3060,
        "minimum_tick_price_at_or_below": 3059,
        "economic_condition": "最新适用螺纹累库/现货弱的因果解释仍成立；保留假期残差、低同比供应与库存反证",
        "refresh_required": [
          "逐日滚动20日通道",
          "固定61根ATR",
          "最新适用产业支持和反证",
          "公开规则/报价/费用/压力场景",
          "实际交易日入场有效期",
          "G1–G4成案后实际账户及size-v3"
        ],
        "conditional_valid_entry_dates": [
          "2026-10-13",
          "2026-10-14"
        ],
        "conditional_event_eligible_dates": [
          "2026-10-13",
          "2026-10-14"
        ],
        "event_qualification": "只对10/12真实收盘新触发成立；入场前核新增直接相关事件；日期不是已经成立的计划",
        "targets": null,
        "entry": null,
        "stop": null,
        "latest_exit_date": null
      },
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
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
      "data_feasibility_reason": "10/09机械突破早于方法生效；生效后完整日和当期公开执行参数待核",
      "signal": "unknown",
      "signal_evidence_refs": [
        "PRICE-MA2701",
        "FRAMEWORK"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "LIQ-MA2701",
            "FRAMEWORK"
          ],
          "details": "真实合约、当前日均量和期限子项已核；生效后实际候选的可持有期及公开提前退出边界仍需核，账户专属限制后置G5",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "新信号出现后核完整合约持有/公开提前退出边界；不要求用户代研究补规则",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "PRICE-MA2701",
            "FRAMEWORK"
          ],
          "details": "3338>3200为10/09已知机械突破，但早于10/11生效，不能登记v3前瞻信号；当前有效信号仍unknown"
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "FRAMEWORK"
          ],
          "details": "生效后新完整日触发才冻结实际Entry范围、ATR止损和交易日有效期",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "生效后新完整日触发才冻结实际Entry范围、ATR止损和交易日有效期",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "GL-1012"
          ],
          "details": "核新信号对应当日交易所适用参数、公开报价/费用、相关事件和明确压力场景；10/12公司表不能替代全部核验",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核新信号对应当日交易所适用参数、公开报价/费用、相关事件和明确压力场景；10/12公司表不能替代全部核验",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "G1–G4成案后核当日真实权益、持仓/挂单、实收保证金、费用和账户限额",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "G1–G4成案后核当日真实权益、持仓/挂单、实收保证金、费用和账户限额",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户齐全后用size-v3核风险/保证金/限仓/执行/压力及周末硬容量",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户齐全后用size-v3核风险/保证金/限仓/执行/压力及周末硬容量",
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
        "G2"
      ],
      "unknown_checks": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "first_blocker": "G2",
      "only_blocker": null,
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
      "final_lots": null,
      "status": "incomplete",
      "evidence_refs": [
        "LIQ-MA2701",
        "FRAMEWORK",
        "PRICE-MA2701",
        "GL-1012"
      ],
      "price_screening_date": "2026-10-09",
      "historical_price_screen": "triggered_long_before_v3_effective_date"
    },
    {
      "candidate_id": "20261009-SR2701-trend-unknown-v3",
      "opportunity_id": "20261011-observe-SR2701-trend-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "SR2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "本次价格与最低背景可读；无信号早停不表示完整执行输入齐全",
      "signal": "not_triggered",
      "signal_evidence_refs": [
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
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
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
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-SR2701",
        "FRAMEWORK",
        "PRICE-SR2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
    {
      "candidate_id": "20261009-CF2701-trend-unknown-v3",
      "opportunity_id": "20261011-observe-CF2701-trend-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "CF2701"
      ],
      "strategy": "trend",
      "direction": "unknown",
      "evidence_quality": "adequate",
      "data_feasibility": "available",
      "data_feasibility_reason": "本次价格与最低背景可读；无信号早停不表示完整执行输入齐全",
      "signal": "not_triggered",
      "signal_evidence_refs": [
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
          "details": "当前close在前20完整日通道内，双向价格必要条件均不成立；经济子条件未被宣称通过"
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
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "LIQ-CF2701",
        "FRAMEWORK",
        "PRICE-CF2701"
      ],
      "price_screening_date": "2026-10-09",
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "先筛价格，已知未触发；日均量和剩余期限是子项事实，不将含公开提前退出边界的整个G1宣称通过"
    },
    {
      "candidate_id": "20261009-MA2701-MA2705-economic_reversion-unknown-v3",
      "opportunity_id": "20261011-observe-MA2701-MA2705-economic_reversion-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "未取得可复算经济锚、月份匹配输入和5–20日收敛机制；不将库存数量或历史分位转换为锚",
      "signal": "unknown",
      "signal_evidence_refs": [],
      "evaluated_checks": [
        {
          "rule_id": "G1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "补MA2705近20日成交量及两腿期限；有结算价不证明远腿流动性",
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "补MA2705近20日成交量及两腿期限；有结算价不证明远腿流动性",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "SPREAD-MA2701-MA2705",
            "FRAMEWORK"
          ],
          "details": "长反转416>328仅为价格子条件；独立经济锚上下界、月份传导及5–20日机制未知，须先成模型再看生效后信号",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "长反转416>328仅为价格子条件；独立经济锚上下界、月份传导及5–20日机制未知，须先成模型再看生效后信号",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G3",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "经济锚成立后冻结1:1入场区间、近侧锚目标、失效止损、期限及整个区间净R>=2.5",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "经济锚成立后冻结1:1入场区间、近侧锚目标、失效止损、期限及整个区间净R>=2.5",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "G4",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "GL-1012"
          ],
          "details": "核同一时刻两腿报价、至少4tick滑点与费用、裸腿事故预案及规则/事件/压力场景",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核同一时刻两腿报价、至少4tick滑点与费用、裸腿事故预案及规则/事件/压力场景",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "G1–G4成案后核真实账户、经纪商实收、挂单和资金/限仓",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "G1–G4成案后核真实账户、经纪商实收、挂单和资金/限仓",
            "due_at": "before_execution"
          }
        },
        {
          "rule_id": "G6",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户齐全后运行size-v3并取所有适用硬容量最小值",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "账户齐全后运行size-v3并取所有适用硬容量最小值",
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
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "leg_ratio": [
          1,
          1
        ],
        "anchor_band": null,
        "economic_anchor_basis": null,
        "convergence_mechanism": null,
        "invalidation_basis": null,
        "net_R": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "evidence_refs": [
        "SPREAD-MA2701-MA2705",
        "FRAMEWORK",
        "GL-1012"
      ]
    },
    {
      "candidate_id": "20261009-RB2701-RB2703-economic_reversion-unknown-v3",
      "opportunity_id": "20261011-observe-RB2701-RB2703-economic_reversion-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "未取得可复算经济锚、月份匹配输入和5–20日收敛机制；不将库存数量或历史分位转换为锚",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "SPREAD-RB2701-RB2703"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "SPREAD-RB2701-RB2703"
          ],
          "details": "同对三日结算差的多、空严格反转子条件均false；不依赖未知锚即可排除本次触发"
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
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "leg_ratio": [
          1,
          1
        ],
        "anchor_band": null,
        "economic_anchor_basis": null,
        "convergence_mechanism": null,
        "invalidation_basis": null,
        "net_R": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "SPREAD-RB2701-RB2703"
      ],
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "按canonical先筛价格；G1远腿流动性未知，未标pass；G2经济子条件也未完成"
    },
    {
      "candidate_id": "20261009-SR2701-SR2705-economic_reversion-unknown-v3",
      "opportunity_id": "20261011-observe-SR2701-SR2705-economic_reversion-unknown-v3",
      "trade_date": "2026-10-09",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "economic_reversion",
      "direction": "unknown",
      "evidence_quality": "weak",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "未取得可复算经济锚、月份匹配输入和5–20日收敛机制；不将库存数量或历史分位转换为锚",
      "signal": "not_triggered",
      "signal_evidence_refs": [
        "SPREAD-SR2701-SR2705"
      ],
      "evaluated_checks": [
        {
          "rule_id": "G2",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "SPREAD-SR2701-SR2705"
          ],
          "details": "同对三日结算差的多、空严格反转子条件均false；不依赖未知锚即可排除本次触发"
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
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "entry_range": null,
        "signal_date": null,
        "valid_until": null,
        "latest_exit_date": null,
        "leg_ratio": [
          1,
          1
        ],
        "anchor_band": null,
        "economic_anchor_basis": null,
        "convergence_mechanism": null,
        "invalidation_basis": null,
        "net_R": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md#r-v3-budget",
        "calculator_ref": "scripts/futures_risk.py size-v3",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "evidence_refs": [
        "SPREAD-SR2701-SR2705"
      ],
      "not_evaluated_after_no_signal": [
        "G1",
        "G3",
        "G4",
        "G5",
        "G6"
      ],
      "price_early_stop_note": "按canonical先筛价格；G1远腿流动性未知，未标pass；G2经济子条件也未完成"
    }
  ],
  "evidence_corrections": [],
  "shadow_plans": [],
  "performance_status": "not_automated",
  "unresolved_items": [
    {
      "kind": "raw_data",
      "owner": "data_pipeline",
      "scope": "prospective_prices",
      "next_action": "10/12收盘后刷新真实日线及通道；不回填10/09信号",
      "due_at": "2026-10-12"
    },
    {
      "kind": "acquisition",
      "owner": "research",
      "scope": "M_domestic_transmission",
      "next_action": "取得一条方向相关的国内当前供应/库存/提货/基差链，不要求全链齐备",
      "due_at": "before_execution"
    },
    {
      "kind": "acquisition",
      "owner": "research",
      "scope": "public_execution",
      "next_action": "真正触发后核当日规则、报价、费用、事件和压力场景，区分公司与交易所参数",
      "due_at": "before_execution"
    },
    {
      "kind": "definition",
      "owner": "research",
      "scope": "V_economic_models",
      "next_action": "只有独立可复算锚、月份匹配、失效价和5–20日机制齐全才恢复模型；当前不凑锚",
      "due_at": "next_report"
    },
    {
      "kind": "account",
      "owner": "user",
      "scope": "account_and_capacity",
      "next_action": "仅在G1–G4成案后提供当日真实账户供容量核算",
      "due_at": "before_execution"
    }
  ],
  "risk_context": {
    "regime": "unknown",
    "reason": "5个T历史HV比未触发高波动不证明账户实际持仓和持续相关事件均无风险；账户及完整候选未形成"
  }
}
```
