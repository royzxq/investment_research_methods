# 2026-10-11 期货执行诊断（原框架 v2.27）

**结论：覆盖部分，当前证据未形成可执行方案；总体可执行机会数、真实持仓风险及最终手数均为 `null`。** 最新有效已提交快照为 10/10 完整输出（实际行情终点 10/09，SHA256 `dd8699ec302663cf63b6c700b96bfb2443942a7d27a8ffd9598082115c82f26a`；快照未给出含时区采集时刻，故 `market_captured_at=null`）。本报告仅按 main 上 v2.27 判定；旧 PR #38 拟议规则不生效。10/03 对“最新9/19快照”的表述遗漏了已提交9/21快照；9/21对当时9/30行情仍旧过期，所以这是历史证据发现纠错，不能当本周市场冲击。

## 1. 证据、适用性与执行状态

| 范围 | 数据可得性与筛选 | 状态 / 关键原因 |
|---|---|---|
| MA2701−MA2705 A 做空价差 | temporary_gap；S +416、同期分位100、三年41/41；1/5/10td +88/+172/+86 | incomplete，既有国内做空路线结案未解除（`domestic_model_basis`已核fail）。分位只作筛选；冻结 v1 两日确认所需逐日S/前10日最高未由快照给出；仓单公开转录10/09总计5316张、当日-182张但只代表可交割供给；隆众港库30.51万吨观测日冲突且原表未读，均不能硬判#5通过/失败；具体Entry/SL/TP/成本/净R未完成。S近五日继续走阔，不能倒推回归止损。 |
| RB2701−RB2703 A | available；S +2、77.2分位，三年41/41 | incomplete。Mysteel原站公开AI摘要：螺纹产量170.27万吨、周-1.96，五大材库存1548.44万吨、周+85.50（非螺纹单品种，含假期效应）。需基于连续日S与成本选定前瞻确认、只有成案且依赖库存/收缩成本时再用原表或下一完整周核D14适用性、完整结构计划。 |
| SR2701−SR2705 A | available；分位0.0 | no_signal（仅当前高分位回归筛选未触发）。 |
| MA2705−MA2709 换月准备 | temporary_gap；分位100，但两年31/41<33/41且MA2709远腿20日均成交缺 | incomplete；逐对验收，非永久 research_only。 |
| RB2703−RB2705 换月准备 | available；分位52.0 | no_signal（高分位筛选未触发）。 |
| MA2701 D 多头 | available；MA D8主力MA2611结算周涨+14.86%、上尾99.4；10/08和10/09同腿结算涨+7.26%/+5.50% | incomplete，已核D8多头否决与#30顺向冷却；D12高波94.8%需升档。SC结算周涨+6.49332%只命中>5%加仓权×0.5/存量减仓50%，未命中>8%冻结。具体事件信号及计划仍缺。 |
| MA2701 D 空头 | available；D8空头无尾部档；SC近端S+22.9但5/10td收窄 | incomplete。截至10/10未见官方缓和/重开、SC back仍+22.9，#26已核拦截；不能只凭5/10td收窄解除；事件信号/计划与账户未齐。 |
| CF2701 B 多头 | temporary_gap；仍处秋季窗口；settle15765<MA20 16132、D8无否决 | incomplete。季节日期不是触发；B-HISTORY、窗前5日低点、Step5-B确认、产业与计划缺。 |
| SR2701 B 多头 | available；夏季窗口9/30已结束 | no_signal。 |
| M2701 独立策略 | research_only；canonical未许可具体路由 | 不计活跃执行候选，需定义并批准策略才恢复。 |

SC2611−SC2612仅信号席：S +22.9、分位100，5/10td -23.7/-30.3；近腿剩14交易日但信号腿免#1。①地缘轴不能由价格单要件改判。完整 A 配对豁免 D8、方向性 D12 与 #16；若执行中出现裸腿须另开事故预案。本期没有将方向性护栏移植到完整配对。 [Mysteel 10/07原站公开摘要](https://gc.mysteel.com/a/26100715/8D43767F25CBE5B3.html)与[MA仓单完整转录](https://www.99qh.com/article/%E9%86%87%E7%B1%BB-1101000)仅在各自统计对象内使用；[隆众港库原始入口](https://www.oilchem.net/26-1008-13-764c0881785292b9.html)未读原表且转引观测日冲突。快照§0b“无已配置节点”只说明配置为空，官方日历仍须人工核对。

## 2. 方案、评分与容量

研究方优先核了 MA A 与 RB A。MA A 的筛选数据可用，但冻结v1的逐日确认输入缺失，故具体执行模型记 `temporary_gap`。上期国内做空路线结案维持：仅国内装置复产数值化、到港回升、太仓/江苏同口径基差走弱之一出现且v1确认成立，才可重评；本期未观测任何复活条件，不能因仓单减少或港库争议隐式重启。MA A的冻结价格定义 `A-MA-2701-2705-v1` 自9/28前瞻生效：S连续两日低于前10日S最高减0.65×MA2701 ATR20，且MA2701不创H20。快照没有逐日S和前10日最高；本期单点S+416及分位100不足以证明触发。RB A尚无前瞻固定确认。预注册草案为先检验固定对连续两日S收窄是否达到交易成本以上的经济幅度，并核同源库存/需求与假期效应；当前只有1/5/10td端点差、没有逐日S分布和双腿成本，不能有据冻结数值阈值。研究/数据侧补序列后才定义版本与生效日，不回判10/09。两者都缺能由实盘成本支持的Entry、结构SL、TP与净R≥2.5，因此本周不登记新的shadow_plan，也不以历史同期10/30/50分位倒推止损。MA A 的A卡 D4=5，RB A D4=3；其余必要维度缺口使总分为 `null`。D9若仅缺增强数据可按原规则 `default_neutral=3`，不能填满所有缺失维度。

账户实际净值、持仓、挂单、已用风险、保证金、真实手续费未知（`actual_position_status=unknown`），预算配置150,000元不是账户事实。单笔配置上限5,250元、低敞口金额帽5,000元只是规则参数；实际可用组合预算、手数和机会总量均为 `null`。脚本2ATR情景金额不是实际SL风险，未运行 `futures_risk.py`，也未宣称空仓或零风险。

## 3. 独立规则反馈与后续触发

10/10快照解决上期缺行情问题：MA D8、#30、D12、SC结算周涨以及A当前对/准备对均能按原规则重新判定。高分位MA A仍非回归信号；RB库存若同一Mysteel序列由去库转累库，必须对具体RB表达核D14，不自动造单。MA2705−MA2709的缺口是逐年同期样本和远腿成交，不应被当作“数据永久不可得”。§5两条9/19影子都 `not_filled`，没有成交、P&L或已了结样本，不能估计护栏收益或机会成本。

下一轮由研究/数据侧补 MA v1 的两日逐点确认、RB前瞻确认和同源产业证据、CF B完整历史与窗前低点、当前官方事件日历；只有形成真实价格计划与成本后，才用账户/挂单快照核剩余额度。若本期建议新增确认定义，只能从定义后生效，10/09数据只能作设计背景。

## 4. 结构化记录（schema 3）

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-11",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v2.27",
    "revision": "origin/main 379d34ac6e802e7e328cb06775ed1c0a05d0e725；本期仅原框架判断，旧PR #38 v2.28草案OPEN/CONFLICTING且未合并",
    "data_script_version": "v1.16；快照2026-10-10 AS_OF=20261010完整、行情终点2026-10-09；本审计未运行行情脚本",
    "rule_changes_affecting_candidates": "框架本体零变动；本期新实测替换旧stale读数；新规则若提出须在未来定义后前瞻生效，10/09不能回判"
  },
  "snapshot": {
    "market_trade_date": "2026-10-09",
    "market_captured_at": null,
    "source_artifacts": [
      "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "research/futures/weekly/2026-10-03/2026-10-03-market-research.md",
      "research/futures/weekly/2026-10-03/2026-10-03-change-decision.md",
      "research/futures/weekly/2026-10-03/2026-10-03-execution-audit.md",
      "framework/futures_framework.md v2.27",
      "framework/FUTURES_DATA_PROTOCOL.md",
      "projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md"
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
      "configured_equity": 150000
    },
    "configured_risk_limits": {
      "single_trade_cap": 5250,
      "portfolio_cap_normal": 5250,
      "portfolio_cap_current": null,
      "low_exposure_cash_cap": 5000,
      "source": "canonical Step5; 实际净值及本期低敞口时段未完成核证，因此可用组合上限null"
    },
    "invalidated_legacy_outputs": [
      "10/03报告误称9/19为最新已提交快照；严格发现显示当时已有9/21，当前新增10/10完整快照。9/21在10/03仍不足以覆盖9/30，故只纠正证据发现不反转旧市场判定",
      "旧PR #38拟议v2.28/v1.17未合并，不能当现行"
    ]
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "MA/RB/SR当前A与MA/RB准备对 §1筛选、期限和样本",
      "MA方向性D8/#30/SC结算周涨/D12价格侧",
      "CF/SR季节B窗口筛选",
      "§5影子结算",
      "MA仓单经公开完整表转录、隆众港库观测日冲突限制",
      "Mysteel原站公开AI摘要螺纹产量与五大材总库存，尚未取得原表"
    ],
    "missing_scope": [
      "完整账户/持仓/挂单/保证金/真实费用和全候选账",
      "MA A冻结v1逐日S/前10日S高点当前观测",
      "RB A前瞻确认与方向一致的产业因果支持/原表核验、CF B历史及窗前低点、各候选Entry/SL/TP净R",
      "0.0b官方发布时间/国内交易日与交易所实际保证金复核",
      "隆众港库原表及统一观测日；Mysteel底层同系列库存/螺纹需求表"
    ],
    "research_only_scope": [
      "M2701无许可路由",
      "geopolitical_fade未恢复官方缓和双要件；SC仅信号席不建仓"
    ],
    "signal_observations": [
      "SC2611-SC2612 +22.9、分位100、5td -23.7/10td -30.3：①价格侧观察，单独不重判官方地缘轴",
      "MA A +416、分位100，但1/5/10td仍+88/+172/+86，非做空确认",
      "快照§5两条旧影子not_filled、无成交及了结收益"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable: 无真实交易记录、完整候选账，§5影子均not_filled"
  },
  "evidence": [
    {
      "evidence_id": "snapshot_complete",
      "metric": "快照完整性",
      "value": "AS_OF=20261010, v1.16, 完整结束标记, SHA256 dd8699ec302663cf63b6c700b96bfb2443942a7d27a8ffd9598082115c82f26a",
      "unit": "校验记录",
      "observation_date": "2026-10-10",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_a",
      "metric": "MA2701-MA2705 固定对筛选",
      "value": "S=+416元/吨; 同期分位100.0; 1/5/10交易日变化+88/+172/+86; 3年各41/41; 近远腿20日均量724225/22566,剩余67/146td",
      "unit": "元/吨、分位%、手、交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "两腿settle之差",
      "comparison_basis": "固定对同期±20交易日",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "rb_a",
      "metric": "RB2701-RB2703 固定对筛选",
      "value": "S=+2元/吨; 同期分位77.2; 1/5/10交易日变化-2/+11/+11; 3年各41/41; 双腿20日均量706042/26351,剩余68/104td",
      "unit": "元/吨、分位%、手、交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "两腿settle之差",
      "comparison_basis": "固定对同期±20交易日",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sr_a",
      "metric": "SR2701-SR2705 固定对筛选",
      "value": "S=-77元/吨; 同期分位0.0; 3年各41/41",
      "unit": "元/吨、分位%",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "两腿settle之差",
      "comparison_basis": "A高分位研究阈值70%",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_roll",
      "metric": "MA2705-MA2709 换月准备对",
      "value": "S=+169; 同期分位100.0; 逐年33/41、31/41、31/41; 后两年不足33/41; 远腿20日均量缺失(<20有效样本)",
      "unit": "元/吨、样本、手",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "两腿settle之差",
      "comparison_basis": "逐对至少3年各33/41; #2远腿成交",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "rb_roll",
      "metric": "RB2703-RB2705 换月准备对",
      "value": "S=-19; 同期分位52.0; 3年各41/41; 双腿20日均量26351/18238",
      "unit": "元/吨、分位%、手",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "两腿settle之差",
      "comparison_basis": "A高分位研究阈值70%",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_atr",
      "metric": "MA2701方向性指标",
      "value": "settle3321; ATR20=105.60; ATR分位94.8; HV20/HV60=1.16; H250代理3402、距离2.38%; 样本173/250",
      "unit": "元/吨、%、倍",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "settle；H250仅上市以来代理",
      "comparison_basis": "D12>80; D11距离<3%",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_daily",
      "metric": "MA2701近期逐日结算脉冲",
      "value": "10/08 settle/pre_settle +7.26%; 10/09 +5.50%; #30近3交易日命中",
      "unit": "%",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "同合约settle/pre_settle",
      "comparison_basis": "#30顺向方向性单边3交易日禁新开",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "d8_ma",
      "metric": "MA商品主力周涨分位",
      "value": "MA2611 9/30→10/09同合约结算周涨+14.86%; 有效周样本154/154; 上尾99.4%; 多头否决档",
      "unit": "%",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "fut_mapping主力同合约两端settle",
      "comparison_basis": "D8商品多头上尾前10%；完整A结构豁免",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "d8_rb_cf",
      "metric": "RB/CF商品主力周涨分位",
      "value": "RB -1.16%、上尾31.2%; CF +0.93%、上尾74.7%; 各154/154",
      "unit": "%",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "fut_mapping主力同合约两端settle",
      "comparison_basis": "D8拟交易方向尾部",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sc_guard",
      "metric": "SC2611原油周涨护栏",
      "value": "9/30结算696.10→10/09结算741.30，+6.49332%; >5%且未>8%",
      "unit": "元/桶、%",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "SC2611两端settle",
      "comparison_basis": "MA方向性多头加仓权×0.5/存量减仓50%；>8%冻结",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sc_back",
      "metric": "SC2611-SC2612近端信号席",
      "value": "S=+22.9元/桶、分位100.0，1/5/10交易日变化+0.4/-23.7/-30.3；SC2611剩余14td，信号腿豁免#1",
      "unit": "元/桶、分位%、交易日",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "两腿settle之差",
      "comparison_basis": "①裁决双要件的价格侧；本腿不建仓",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "cf_b",
      "metric": "CF2701 B价格筛查",
      "value": "settle15765; MA20=16132; ATR20=229.02; ADX14=33.9; 10/09单日-0.03%; D8上尾74.7",
      "unit": "元/吨、%、点",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "settle",
      "comparison_basis": "B Step5触发仍需pre_window_low5、三年同窗历史和成本计划",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "shadow_ledger",
      "metric": "既有影子结算",
      "value": "两条9/19登记影子均 incomplete/not_filled，fill/P&L/R空；已了结影子为零",
      "unit": "状态",
      "observation_date": "2026-10-10",
      "published_at": "2026-10-10",
      "source_url_or_file": "research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": "§5按事前登记保守结算",
      "comparison_basis": null,
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "calendar_sr_cf",
      "metric": "B-WINDOW固定研究窗口",
      "value": "SR-summer窗口9/30已结束；CF-autumn为9/1-10/31，window_end为10/30，按第五个交易日前退出约10/23，精确交易日按trade_cal复核",
      "unit": "日期",
      "observation_date": "2026-10-11",
      "published_at": "2026-10-11",
      "source_url_or_file": "framework/futures_framework.md §1.6; research/futures/weekly/2026-10-03/2026-10-03-execution-audit.md",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_confirmation",
      "metric": "既有MA A空价差确认冻结定义",
      "value": "A-MA-2701-2705-v1; 2026-09-26T21:00+08定义、2026-09-28前瞻生效；S连续两交易日settle低于前10日S最高减0.65×MA2701 ATR20，且MA2701未创H20；当前快照不打印逐日S与前10日最高",
      "unit": "规则",
      "observation_date": "2026-09-26",
      "published_at": "2026-09-26",
      "source_url_or_file": "research/futures/weekly/2026-09-26/2026-09-26-execution-audit.md",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "old_latest_invalid",
      "metric": "旧10/03“仓库最新9/19快照”断言",
      "value": "不成立；已提交9/21快照，当前还已有10/10完整快照；10/03市场日9/30仍需新行情，故更正发现过程不把旧市场结论自动反转",
      "unit": "源发现",
      "observation_date": "2026-10-03",
      "published_at": "2026-10-03",
      "source_url_or_file": "research/futures/weekly/2026-10-03/2026-10-03-execution-audit.md; scripts/research_paths.py",
      "original_source": "已提交 v1.16 完整快照 / 原框架 v2.27",
      "price_basis": null,
      "comparison_basis": null,
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_warrant",
      "metric": "甲醇注册仓单公开全表转录",
      "value": "5316张、当日-182张、有效预报0；可交割供给，不等于港口库存",
      "unit": "张",
      "observation_date": "2026-10-09",
      "published_at": "2026-10-09T15:48:49+08:00",
      "source_url_or_file": "https://www.99qh.com/article/%E9%86%87%E7%B1%BB-1101000",
      "original_source": "郑商所表经99期货公开转录；原交易所页未核",
      "price_basis": null,
      "comparison_basis": "同表前交易日5498张；注销/交割原因未核",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_port_conflict",
      "metric": "隆众甲醇港口样本库存转引",
      "value": "30.51万吨、周-8.84；机构转载观测日10/07与10/08冲突且原表未读",
      "unit": "万吨",
      "observation_date": null,
      "published_at": "2026-10-09",
      "source_url_or_file": "https://www.oilchem.net/26-1008-13-764c0881785292b9.html; https://www.cnfin.com/yw-lb/detail/20261009/4478761_1.html",
      "original_source": "隆众资讯，机构转引",
      "price_basis": null,
      "comparison_basis": "仅同隆众序列；与注册仓单不可互换",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "rb_mysteel",
      "metric": "Mysteel螺纹产量公开摘要",
      "value": "170.27万吨、周-1.96；原站公开AI摘要，底层表未读",
      "unit": "万吨",
      "observation_date": "2026-10-07",
      "published_at": "2026-10-07T17:30:00+08:00",
      "source_url_or_file": "https://gc.mysteel.com/a/26100715/8D43767F25CBE5B3.html",
      "original_source": "Mysteel原站公开AI摘要",
      "price_basis": null,
      "comparison_basis": "上期172.23万吨仅据周变化反算",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "rb_total_stock",
      "metric": "Mysteel五大材库存公开摘要",
      "value": "1548.44万吨、周+85.50；五大材非RB单品种，国庆假期季节性扰动",
      "unit": "万吨",
      "observation_date": "2026-10-07",
      "published_at": "2026-10-07T17:30:00+08:00",
      "source_url_or_file": "https://gc.mysteel.com/a/26100715/8D43767F25CBE5B3.html",
      "original_source": "Mysteel原站公开AI摘要",
      "price_basis": null,
      "comparison_basis": "同系列前周1462.94万吨；原表未读",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "cf_association",
      "metric": "中国棉花协会10/01-10/07新棉周报公开转引",
      "value": "全国籽棉均收购价7.4元/公斤；公证检验21.46万吨累计量；未给需求改善证据",
      "unit": "元/公斤、万吨",
      "observation_date": "2026-10-07",
      "published_at": "2026-10-08T21:38:41+08:00",
      "source_url_or_file": "https://m.sinotex.cn/news/read.asp?id=267101",
      "original_source": "中国棉花协会经中国纺织网具名转载；原协会页未读",
      "price_basis": null,
      "comparison_basis": "本期无同口径前期价；不可计算环比",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "geo_current",
      "metric": "海峡官方缓和要件本期查核",
      "value": "截至10/10多方谈判/政策立场并存，未见官方全面重开/解除；SC近端仍back +22.9但5td收窄",
      "unit": "事件状态",
      "observation_date": "2026-10-10",
      "published_at": "2026-10-10",
      "source_url_or_file": "https://apnews.com/article/trump-iran-midterms-strikes-sanctions-f5481939341ce51a5a3841498b030260; research/futures/snapshots/2026-10-10-data-snapshot.txt",
      "original_source": "AP已读报道加本期已提交快照；不把未见等同永久不存在",
      "price_basis": null,
      "comparison_basis": "①缓和双要件：官方事实+SC近端back同向回落",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_domestic_prior_closure",
      "metric": "MA domestic_public做空价差既有结案与复活条件",
      "value": "10/03正式审计沿用9/26国内路线结案：只有国内装置复产数值化、到港回升、太仓/江苏同口径基差走弱至少一项被观测，且冻结v1价格确认成立，方可重评；本期公开仓单日-182、隆众港库观测日冲突未给出上述复活条件",
      "unit": "规则状态",
      "observation_date": "2026-10-03",
      "published_at": "2026-10-03",
      "source_url_or_file": "research/futures/weekly/2026-10-03/2026-10-03-execution-audit.md; research/futures/weekly/2026-10-03/2026-10-03-change-decision.md",
      "original_source": "上期按canonical v2.27的正式执行审计及变化报告",
      "price_basis": null,
      "comparison_basis": "本期是否达到既有解除条件",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "historical"
    }
  ],
  "candidates": [
    {
      "candidate_id": "2026-10-09|MA2701-MA2705|A|short_spread|v2.27",
      "opportunity_id": "MA2701-MA2705|A|short_spread",
      "trade_date": "2026-10-09",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "A-reversion",
      "hypothesis": "上期domestic_public做空回归路线已结案；本期100分位只给研究筛选，复活条件未见、冻结v1逐日确认缺。仓单减少与港库争议均不重启路线。",
      "evidence_basis": "domestic_public",
      "direction": "short_spread",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "筛选价差/样本/量可用；但冻结v1最低必要的逐日S、前10日S最高与两日H20未在快照输出，具体确认模型暂缺计算输入。",
      "signal": "unknown",
      "signal_basis": "上期domestic_public做空回归路线已结案；本期100分位只给研究筛选，复活条件未见、冻结v1逐日确认缺。仓单减少与港库争议均不重启路线。",
      "screening_evidence": "ma_a",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_a"
          ],
          "details": "3年各41/41、分位100，仅研究筛选"
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_a"
          ],
          "details": "两腿期限67/146td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_a"
          ],
          "details": "双腿20日均量已显示，须执行时复核阈值"
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_a"
          ],
          "details": "三年逐年完整"
        },
        {
          "rule_id": "domestic_model_basis",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ma_domestic_prior_closure",
            "ma_warrant"
          ],
          "details": "上期国内做空回归路线已结案；本期未观测到国内复产数值化、到港回升或太仓/江苏同口径基差走弱任一既定复活条件。仓单减少及观测日冲突港库不能重新激活路线；冻结v1观测仍缺。"
        },
        {
          "rule_id": "confirmation_v1",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ma_confirmation"
          ],
          "details": "须逐日固定对settle、前10交易日S最高和同期H20，不用单点分位代替",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "从已提交原始行情补算逐日固定对S、前10日S最高、两日近腿H20；只按9/28已生效v1前瞻判，不用10/09设计新阈值回判",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ma_warrant"
          ],
          "details": "公开仓单-182张限制为可交割供给，不能证明做空回归所需国内宽松；隆众港库观测日冲突且原表未读，不得用于硬fail/pass；尚缺复产/到港/基差同口径改善。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "复核同口径港库/仓单/基差和装置状态，分开交割仓单与港口库存",
            "due_at": "2026-10-12"
          },
          "diagnostic_evidence_refs": [
            "ma_port_conflict"
          ]
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "未有经确认后的Entry、真实结构SL、TP、费用、净R≥2.5、期限",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "确认及独立产业事实过门后按结构风险生成具体计划，不倒推止损",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "账户/挂单/保证金未知",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当期账户、持仓、挂单和适用保证金快照",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "D8",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "#30",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "D12",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "#16",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        }
      ],
      "evaluation_order": [
        "screening",
        "#1",
        "#2",
        "#13",
        "domestic_model_basis",
        "confirmation_v1",
        "#5",
        "execution_plan",
        "account",
        "D8",
        "#30",
        "D12",
        "#16"
      ],
      "all_blockers": [
        "domestic_model_basis"
      ],
      "unknown_checks": [
        "confirmation_v1",
        "#5",
        "execution_plan",
        "account"
      ],
      "first_blocker": "domestic_model_basis",
      "only_blocker": null,
      "score": {
        "canonical_ref": "§3.1 A六维/90",
        "result": null,
        "defaulted_dimensions": [
          "D9=3 default_neutral（无独立增强值时）"
        ],
        "notes": "D4=5（分位≥85）；D1确认未知、D2产业验证待本期同口径复核、D3净R未知，其余不凑总分"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": "A-MA-2701-2705-v1",
        "confirmation_definition": {
          "state": "frozen",
          "rule_version": "A-MA-2701-2705-v1",
          "defined_at": "2026-09-26T21:00:00+08:00",
          "effective_from": "2026-09-28",
          "price_basis": "两腿settle之差S",
          "economic_rationale": "两日回吐且近腿不创新高",
          "observed_values": "快照仅有10/09 S+416和1/5/10td变化，不能计算完整v1"
        }
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "ma_a",
        "ma_confirmation",
        "ma_warrant",
        "ma_domestic_prior_closure"
      ]
    },
    {
      "candidate_id": "2026-10-09|RB2701-RB2703|A|undetermined|v2.27",
      "opportunity_id": "RB2701-RB2703|A|undetermined",
      "trade_date": "2026-10-09",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "A-reversion",
      "hypothesis": "77.2分位与完整样本形成研究候选；独立库存/产量证据仅作供需背景，尚无前瞻固定价格确认与入场结构计划。",
      "evidence_basis": "domestic_public",
      "direction": "undetermined",
      "data_feasibility": "available",
      "data_feasibility_reason": "快照A筛选/样本/量与一项独立产业事实可得；价格确认定义及结构方向未形成，不属行情原始数据永久不可得。",
      "signal": "unknown",
      "signal_basis": "77.2分位与完整样本形成研究候选；独立库存/产量证据仅作供需背景，尚无前瞻固定价格确认与入场结构计划。",
      "screening_evidence": "rb_a",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "rb_a"
          ],
          "details": "77.2≥70"
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "rb_a"
          ],
          "details": "68/104td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "rb_a"
          ],
          "details": "量706042/26351"
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "rb_a"
          ],
          "details": "3×41/41"
        },
        {
          "rule_id": "price_confirmation",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "已给预注册草案，但仅有端点变化、产业机制未定与成本缺，无法选定可复评数值阈值；不让用户猜。",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "预注册研究草案：比较固定RB2701-RB2703连续两日S收窄及成本可覆盖幅度，并与同口径产业转累验证；现仅有当日S和1/5/10td变化、无连续日S分布与结构成本，无法有据冻结数值阈值。由research/data_pipeline取日序列与成本后定义版本和生效日，不回判10/09。",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "rb_mysteel"
          ],
          "details": "螺纹产量-1.96万吨为独立当期事实，但单项产量不能证明拟交易方向；五大材库存是假期相关摘要，不能充当螺纹需求硬门。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "以同一Mysteel序列核库存与产量、焦炭/利润，判定对应方向而非直接从分位推断",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "D14",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [
            "rb_total_stock"
          ],
          "details": "当前没有方向/依赖假设/具体计划；D14只对依赖复产、收缩成本或库存的具体计划核。五大材库存周+85.50为候选设计背景，成案后重评适用。"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无Entry/SL/TP/费用/净R",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "在确认定义前瞻生效后组装结构方案",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当期账户/挂单/保证金",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "D8",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "#30",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "D12",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "#16",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        }
      ],
      "evaluation_order": [
        "screening",
        "#1",
        "#2",
        "#13",
        "price_confirmation",
        "#5",
        "D14",
        "execution_plan",
        "account",
        "D8",
        "#30",
        "D12",
        "#16"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "price_confirmation",
        "#5",
        "execution_plan",
        "account"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "§3.1 A六维/90",
        "result": null,
        "defaulted_dimensions": [
          "D9=3 default_neutral（仅增强数据不可得时）"
        ],
        "notes": "D4=3（分位70-85）；其余必要维度待核，不合成总分"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "rb_a",
        "rb_mysteel",
        "rb_total_stock"
      ]
    },
    {
      "candidate_id": "2026-10-09|SR2701-SR2705|A|high_spread|v2.27",
      "opportunity_id": "SR2701-SR2705|A|high_spread",
      "trade_date": "2026-10-09",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "A-reversion",
      "hypothesis": "同期高分位A筛选阈值70%；实测0.0%，本方向未触发。",
      "evidence_basis": "domestic_public",
      "direction": "short_spread",
      "data_feasibility": "available",
      "data_feasibility_reason": "同期高分位A筛选阈值70%；实测0.0%，本方向未触发。",
      "signal": "not_triggered",
      "signal_basis": "同期高分位A筛选阈值70%；实测0.0%，本方向未触发。",
      "screening_evidence": "sr_a",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "sr_a"
          ],
          "details": "0.0<70，后续模型门不评估"
        }
      ],
      "evaluation_order": [
        "screening"
      ],
      "all_blockers": [
        "screening"
      ],
      "unknown_checks": [],
      "first_blocker": "screening",
      "only_blocker": null,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "sr_a"
      ],
      "signal_evidence_refs": [
        "sr_a"
      ]
    },
    {
      "candidate_id": "2026-10-09|MA2705-MA2709|A|roll|v2.27",
      "opportunity_id": "MA2705-MA2709|A|roll",
      "trade_date": "2026-10-09",
      "contracts": [
        "MA2705",
        "MA2709"
      ],
      "strategy": "A-roll-preparation",
      "hypothesis": "换月准备对独立验收：虽分位100，但后两年31/41低于33/41，远腿20日均成交缺；不得继承旧对通过状态或判永久research_only。",
      "evidence_basis": "domestic_public",
      "direction": "undetermined",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "换月准备对独立验收：虽分位100，但后两年31/41低于33/41，远腿20日均成交缺；不得继承旧对通过状态或判永久research_only。",
      "signal": "unknown",
      "signal_basis": "换月准备对独立验收：虽分位100，但后两年31/41低于33/41，远腿20日均成交缺；不得继承旧对通过状态或判永久research_only。",
      "screening_evidence": "ma_roll",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_roll"
          ],
          "details": "分位100只为初筛"
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ma_roll"
          ],
          "details": "两年31/41低于33/41",
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "下次窗口独立重算并检查缺日根因，未达33/41不发布结构信号",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ma_roll"
          ],
          "details": "MA2709远腿成交缺(<20有效日)",
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "追加有效日后重算远腿20日量并逐对验收",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "样本/成交门完整后才定义结构确认与真实风险",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当期账户/挂单/保证金",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "D8",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "#30",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "D12",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        },
        {
          "rule_id": "#16",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "完整双腿A结构豁免方向性护栏；意外裸腿另评"
        }
      ],
      "evaluation_order": [
        "screening",
        "#13",
        "#2",
        "execution_plan",
        "account",
        "D8",
        "#30",
        "D12",
        "#16"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "#13",
        "#2",
        "execution_plan",
        "account"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "ma_roll"
      ]
    },
    {
      "candidate_id": "2026-10-09|RB2703-RB2705|A|roll|v2.27",
      "opportunity_id": "RB2703-RB2705|A|roll",
      "trade_date": "2026-10-09",
      "contracts": [
        "RB2703",
        "RB2705"
      ],
      "strategy": "A-roll-preparation",
      "hypothesis": "准备对同期高分位筛选52.0<70，直接未触发。",
      "evidence_basis": "domestic_public",
      "direction": "undetermined",
      "data_feasibility": "available",
      "data_feasibility_reason": "准备对同期高分位筛选52.0<70，直接未触发。",
      "signal": "not_triggered",
      "signal_basis": "准备对同期高分位筛选52.0<70，直接未触发。",
      "screening_evidence": "rb_roll",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "rb_roll"
          ],
          "details": "52.0<70；后续不评估"
        }
      ],
      "evaluation_order": [
        "screening"
      ],
      "all_blockers": [
        "screening"
      ],
      "unknown_checks": [],
      "first_blocker": "screening",
      "only_blocker": null,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "rb_roll"
      ],
      "signal_evidence_refs": [
        "rb_roll"
      ]
    },
    {
      "candidate_id": "2026-10-09|MA2701|D|long|v2.27",
      "opportunity_id": "MA2701|D|long",
      "trade_date": "2026-10-09",
      "contracts": [
        "MA2701"
      ],
      "strategy": "D-event",
      "hypothesis": "事件方向信号尚未形成具体可成交计划；#30顺向3日禁新开与D8多头尾部否决已知，SC结算周涨仅>5%命中加仓/持有护栏。",
      "evidence_basis": "public_data",
      "direction": "long",
      "data_feasibility": "available",
      "data_feasibility_reason": "事件方向信号尚未形成具体可成交计划；#30顺向3日禁新开与D8多头尾部否决已知，SC结算周涨仅>5%命中加仓/持有护栏。",
      "signal": "unknown",
      "signal_basis": "事件方向信号尚未形成具体可成交计划；#30顺向3日禁新开与D8多头尾部否决已知，SC结算周涨仅>5%命中加仓/持有护栏。",
      "screening_evidence": "ma_atr",
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_a"
          ],
          "details": "67td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_atr"
          ],
          "details": "20日均量724224"
        },
        {
          "rule_id": "directional_event_signal",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需当期事件已落地及次日确认",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "结合本期官方事件时间与价格确认定义方向性D信号",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "d8_ma"
          ],
          "details": "商品多头上尾99.4在前10%否决档"
        },
        {
          "rule_id": "#30",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ma_daily"
          ],
          "details": "10/08与10/09两次顺向结算涨幅≥5%，冷却跨下周实际交易日"
        },
        {
          "rule_id": "MA_oil_guard",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "sc_guard"
          ],
          "details": "SC +6.49332%：多头加仓权×0.5/持有条件减仓50%；未达>8%冻结"
        },
        {
          "rule_id": "D11",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_atr"
          ],
          "details": "距H250代理2.38%：多头扣0.3，未到新高不构成#20"
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_atr"
          ],
          "details": "ATR分位94.8高波；须×0.5、门槛+0.3、重校准ATR，不是已执行完"
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "低敞口方向性新开窗口需当前事件密度/实际交易日核定",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "对10/12起未来10交易日官方节点按0.0b计算并判低敞口与#16",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "确认许可后补Entry/SL/TP/成本/退出",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当期账户/挂单/保证金",
            "due_at": "2026-10-12"
          }
        }
      ],
      "evaluation_order": [
        "#1",
        "#2",
        "directional_event_signal",
        "D8",
        "#30",
        "MA_oil_guard",
        "D11",
        "D12",
        "#16",
        "execution_plan",
        "account"
      ],
      "all_blockers": [
        "D8",
        "#30"
      ],
      "unknown_checks": [
        "directional_event_signal",
        "#16",
        "execution_plan",
        "account"
      ],
      "first_blocker": "D8",
      "only_blocker": false,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "ma_atr",
        "ma_daily",
        "d8_ma",
        "sc_guard"
      ]
    },
    {
      "candidate_id": "2026-10-09|MA2701|D|short|v2.27",
      "opportunity_id": "MA2701|D|short",
      "trade_date": "2026-10-09",
      "contracts": [
        "MA2701"
      ],
      "strategy": "D-event",
      "hypothesis": "①反向官方要件与SC back同向回落须同时核；近端S仍正22.9但5/10日显著收窄，不能只凭收窄解#26。",
      "evidence_basis": "public_data",
      "direction": "short",
      "data_feasibility": "available",
      "data_feasibility_reason": "①反向官方要件与SC back同向回落须同时核；近端S仍正22.9但5/10日显著收窄，不能只凭收窄解#26。",
      "signal": "unknown",
      "signal_basis": "①反向官方要件与SC back同向回落须同时核；近端S仍正22.9但5/10日显著收窄，不能只凭收窄解#26。",
      "screening_evidence": "ma_atr",
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_a"
          ],
          "details": ""
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_atr"
          ],
          "details": ""
        },
        {
          "rule_id": "directional_event_signal",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "本期官方事实和前瞻价格确认共同定义事件落地次日空头信号",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "#26",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "geo_current",
            "sc_back"
          ],
          "details": "截至10/10未见官方全面缓和/重开，虽SC 5/10td收窄但仍back +22.9；①缓和双要件未共证，原框架#26空头拦截维持。"
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "d8_ma"
          ],
          "details": "MA本周上涨，空头非下跌尾部否决"
        },
        {
          "rule_id": "#30",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": ""
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_atr"
          ],
          "details": "高波层处置同上，空头亦适用"
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "核10/12起事件密度与低敞口新开窗",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "确认方向许可后补具体方案",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当期账户/挂单/保证金",
            "due_at": "2026-10-12"
          }
        }
      ],
      "evaluation_order": [
        "#1",
        "#2",
        "directional_event_signal",
        "#26",
        "D8",
        "#30",
        "D12",
        "#16",
        "execution_plan",
        "account"
      ],
      "all_blockers": [
        "#26"
      ],
      "unknown_checks": [
        "directional_event_signal",
        "#16",
        "execution_plan",
        "account"
      ],
      "first_blocker": "#26",
      "only_blocker": null,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "ma_atr",
        "sc_back",
        "d8_ma",
        "geo_current"
      ]
    },
    {
      "candidate_id": "2026-10-09|CF2701|B|long|v2.27",
      "opportunity_id": "CF2701|B|long",
      "trade_date": "2026-10-09",
      "contracts": [
        "CF2701"
      ],
      "strategy": "B-seasonal",
      "hypothesis": "秋季B窗口仍在，但Step5-B的三年同窗历史、窗前五日低点、Entry/SL/TP/费用未组装；settle低于MA20不是B信号。",
      "evidence_basis": "public_data",
      "direction": "long",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "秋季B窗口仍在，但Step5-B的三年同窗历史、窗前五日低点、Entry/SL/TP/费用未组装；settle低于MA20不是B信号。",
      "signal": "unknown",
      "signal_basis": "秋季B窗口仍在，但Step5-B的三年同窗历史、窗前五日低点、Entry/SL/TP/费用未组装；settle低于MA20不是B信号。",
      "screening_evidence": "calendar_sr_cf",
      "evaluated_checks": [
        {
          "rule_id": "B_window",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "calendar_sr_cf"
          ],
          "details": "10/09在窗口且早于计划退出"
        },
        {
          "rule_id": "B_HISTORY",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "按canonical组装三年同窗历史与统一口径，运行seasonal_plan.py",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "B_trigger",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "cf_b"
          ],
          "details": "缺pre_window_low5等必要输入",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "从原始价格组装窗前五日低点、MA20/ATR20和Step5-B完整条件",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "d8_rb_cf"
          ],
          "details": "上尾74.7不在前10%"
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "cf_association"
          ],
          "details": "当期新棉供应上市事实可核；未给独立需求改善或同口径前值，做多产业支持未成立。",
          "gap": {
            "kind": "acquisition",
            "owner": "research",
            "next_action": "核同年度同口径棉花供需原始发布和价格确认",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "历史和触发齐后生成入场/止损/目标/成本/退出",
            "due_at": "2026-10-12"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "提供当期账户/挂单/保证金",
            "due_at": "2026-10-12"
          }
        }
      ],
      "evaluation_order": [
        "B_window",
        "B_HISTORY",
        "B_trigger",
        "D8",
        "#5",
        "execution_plan",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "B_HISTORY",
        "B_trigger",
        "#5",
        "execution_plan",
        "account"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "calendar_sr_cf",
        "cf_b",
        "d8_rb_cf",
        "cf_association"
      ]
    },
    {
      "candidate_id": "2026-10-09|SR2701|B|long|v2.27",
      "opportunity_id": "SR2701|B|long",
      "trade_date": "2026-10-09",
      "contracts": [
        "SR2701"
      ],
      "strategy": "B-seasonal",
      "hypothesis": "SR-summer窗口9/30结束，本窗口本期无新开信号。",
      "evidence_basis": "public_data",
      "direction": "long",
      "data_feasibility": "available",
      "data_feasibility_reason": "SR-summer窗口9/30结束，本窗口本期无新开信号。",
      "signal": "not_triggered",
      "signal_basis": "SR-summer窗口9/30结束，本窗口本期无新开信号。",
      "screening_evidence": "calendar_sr_cf",
      "evaluated_checks": [
        {
          "rule_id": "B_window",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "calendar_sr_cf"
          ],
          "details": "窗口结束"
        }
      ],
      "evaluation_order": [
        "B_window"
      ],
      "all_blockers": [
        "B_window"
      ],
      "unknown_checks": [],
      "first_blocker": "B_window",
      "only_blocker": null,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [
        "calendar_sr_cf"
      ],
      "signal_evidence_refs": [
        "calendar_sr_cf"
      ]
    },
    {
      "candidate_id": "2026-10-09|M2701|unspecified|v2.27",
      "opportunity_id": "M2701|unspecified",
      "trade_date": "2026-10-09",
      "contracts": [
        "M2701"
      ],
      "strategy": "unlicensed-observation",
      "hypothesis": "仅观察，无已许可具体策略，不计活跃执行候选；恢复需明确策略路由、独立供需证据与信号定义。",
      "evidence_basis": "public_data",
      "direction": "undetermined",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "仅观察，无已许可具体策略，不计活跃执行候选；恢复需明确策略路由、独立供需证据与信号定义。",
      "signal": "unknown",
      "signal_basis": "仅观察，无已许可具体策略，不计活跃执行候选；恢复需明确策略路由、独立供需证据与信号定义。",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "licensed_route",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [],
          "details": "canonical未许可本期M独立策略"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "先定义并批准模型路由，再进入可执行研究范围",
            "due_at": "2026-10-12"
          }
        }
      ],
      "evaluation_order": [
        "licensed_route",
        "execution_plan"
      ],
      "all_blockers": [
        "licensed_route"
      ],
      "unknown_checks": [
        "execution_plan"
      ],
      "first_blocker": "licensed_route",
      "only_blocker": null,
      "score": {
        "canonical_ref": "framework/futures_framework.md §3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "必要维度或计划输入未完成，完整总分null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "latest_exit_date": null,
        "holding_period": null,
        "confirmation_rule": null,
        "confirmation_definition": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": []
    }
  ],
  "unresolved_items": [
    {
      "item": "补足MA v1观测与国内独立证据；完成RB A前瞻确认；完整价格计划与成本之后才可算净R及手数",
      "owner": "research / data_pipeline",
      "due_at": "2026-10-12",
      "required_evidence": [
        "ma_a",
        "ma_confirmation",
        "rb_a"
      ],
      "resolution": "pending"
    },
    {
      "item": "CF B组装pre_window_low5和三年同窗历史，运行seasonal_plan；不能把季节日期当开仓信号",
      "owner": "research / data_pipeline",
      "due_at": "2026-10-12",
      "required_evidence": [
        "cf_b",
        "calendar_sr_cf"
      ],
      "resolution": "pending"
    },
    {
      "item": "实核官方10月事件时间、国内交易日及交易所实际保证金；本快照§0b只反映配置空白",
      "owner": "research",
      "due_at": "2026-10-12",
      "required_evidence": [
        "snapshot_complete"
      ],
      "resolution": "pending"
    },
    {
      "item": "完整账户、持仓、挂单、保证金和费用；缺失时风险总量及最终手数继续null",
      "owner": "account_holder",
      "due_at": "next_execution_review",
      "required_evidence": [],
      "resolution": "pending"
    }
  ],
  "shadow_plans": [],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "old_latest_invalid",
      "reason": "10/03文字断言忽略已提交9/21快照；严格路径发现更正，10/10完整快照用于本期重评。9/21仍不覆盖10/03所需9/30行情，所以纠错不等于新市场冲击。",
      "affected_checks": [
        {
          "candidate_id": "2026-10-09|MA2701-MA2705|A|short_spread|v2.27",
          "rule_id": "screening"
        }
      ],
      "recalculation": "completed"
    }
  ]
}
```
