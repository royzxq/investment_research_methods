# 2026-09-19 期货执行诊断

> **拟议版本重评（proposed_framework_reassessment）**：本文件在分支 `futures-framework/2026-09-19` 上按拟议 canonical **v2.27**（significant：仅状态机层面三项门/状态变更——①评估期→中断证真、D13 冻结→加息落地重写、交易所风控常规→收紧；规则本体、参数、门槛、评分权重、池分层零改动）与脚本 **v1.16**（EVENTS 日历滚动；§2b.1 新增判定腿逐日结算涨跌列，服务既有 #30；未联网实测）刷新。**规则零改动→各候选的适用门判定与 status 与现行 v2.26 诊断完全一致**；状态层变更已体现在：MA2701 空头 #26 details（①改判中断证真）、MA2701 多空 exchange_notice/#16（交易所收紧、低敞口继续）、RB D14 注记（第五轮纠错）。v1.16 的 #30 输入列在本次回填所用 9/19 快照（v1.15）中尚不存在→#30 仍 unknown（raw_data，next_action 改为重跑 v1.16）。这是新版本的重评，不是历史交易日已生效的规则；v2.27 待 PR 合并。首次运行（现行 v2.26）记录保留于"校验记录"第一条。

**结论：截至 2026-09-19（最新已完成行情日 2026-09-18），已核研究范围内未形成可执行方案，仍有研究/账户核验缺项；不能据此写"市场没有机会"或"市场建议空仓"。** 本诊断按现行 `framework/futures_framework.md` v2.26（origin/main `b6069b2`，2026-09-17）与 `FUTURES_DATA_PROTOCOL.md` v2.26 生成；**本周有用户提交的行情快照 `research/2026-09-19-data-snapshot.txt`**（脚本 v1.15、AS_OF=20260919、最新行情日 20260918、末行"快照完成"），价差/分位/样本/周涨/D8/ATR 分层全部取自快照实测；公开信息来自 WebSearch 摘要（本环境原文读取被出口代理封锁，按协议降级：多源同口径官方数据 verified、单源/无日期/摘要冲突项分别标注）；实际账户与挂单快照未提供（`actual_position_status=unknown`），全部 `final_lots=null`，总体机会数 `null`。

| 已观察记录 | 本次状态 | 已核否决 / 缺口 |
|---|---|---|
| MA2701−MA2705，A reversion（做空价差，domestic_public） | incomplete | 研究筛选 pass（快照分位 100.0、价差 +312、样本 41/41/41 complete；5td +30、10td +123）；**#5 已核失败**（(b) 独立产业事实仍指向近月走强：中东约 62% 甲醇装置停车/伊朗在产约 7 套（9/10-9/11 报道，最近可得读数）；港口库存"进一步走低"为无日期定性、装置 9 月中下旬复产为前瞻——均不构成做空价差的独立支持）；确认定义本周给出 draft（未冻结）；国内路线论证未完成；计划/账户未核；9/21 起郑商所提保扩板抬高双腿占用 |
| MA2705−MA2709，A（准备对） | incomplete | temporary_gap：快照同期样本 24/21/22<33、MA2709 20 日均量缺失（#2 缺失）；分位 100 仅参考、不授许可 |
| RB2701−RB2703，A（黑色唯一结构表达） | **no_signal** | 快照分位 56.1（<70 研究筛选线）→ 本策略未触发（直接证据：快照 §1）；后续门未评估并明示；兰格口径总库存 -29.13 去库加速、焦炭第五轮 9/10 落地/钢厂减产计划增多为背景；Mysteel 同口径总库存未取得（不阻断未触发结案） |
| RB2703−RB2705，A（准备对，仅取样） | **no_signal** | 快照分位 61.8（<70）→ 未触发；RB2705 13,672 过 #2 |
| MA2701，方向性多头（D 事件冲击） | incomplete | **#16 已核失败**（0.1 低敞口判定继续命中：高密度簇 9/21、9/29 郑商所提保扩板→9/30 俄禁令→10/1-10/8 长假/10/4 OPEC+→10/27-28 FOMC；交易所公告 ±1 日；D12 高波层 MA2701 ATR250 分位 82.9）；周涨护栏 pass（SC2611 结算周涨 -0.30% 未命中 >5%/>8%；上一读数 +22.56% 的处置到期不续延）；D8 pass（上尾 66.7 无档）；#20 pass（dist_H250 5.61%）；D12 已触发（高波层→×0.5+门槛+0.3，非否决）；**#30 unknown**（MA2701 逐日结算涨跌未取得；SC 信号腿 9/14 +11% 记录不替代）；计划/账户未核 |
| MA2701，方向性空头 | incomplete | **#16、#26 已核失败**（①未证缓和——本周 change-analysis 按 v2.26 新要件改判"中断证真"：再袭船 9/8-9/9 多源✓＋SC 近端 back 9/18 +43.5/分位 100；护航/管道修复非官方重开）；SC 9/17 -6%/9/18 -9% 为信号腿记录；#30 unknown；计划/账户未核 |
| M2701，独立备选 | incomplete（research_only） | 无已许可具体策略（仅观察）；快照 ATR 分位 99.4 高波层；到港/库存为 9/1 口径 stale |
| SR2701−SR2705，A 远月 | **no_signal** | 快照分位 0.0（<70）→ 未触发 |
| SR2701，B 季节做多 | incomplete | B-WINDOW SR-summer（07-01–09-30）在窗（日期筛选 pass）；**品种卡专属否决与 #5 已核失败**（榨季初期多头需产销率验证：广西截至 8 月产销率 80.56%、同比 −8.48pp，工业库存同比 +78.74 万吨——验证反向）；planned_exit≈9/23、剩余持有区间 ≤2 个交易日（期限核验待 seasonal_plan.py）；B-HISTORY/Entry/SL/TP1 未组装；D8 pass（做多看上尾 5.9） |
| CF2701，B 季节做多 | incomplete | B-WINDOW CF-autumn（09-01–10-31）在窗（pass）；**#5 已核失败**（(b) 独立产业事实反证：储备棉 9/18 成交率 96.37%（本轮首见 <100%）、新棉上市提速、籽棉开秤预期下移 7.0-7.5 元/公斤——供给端压力，无独立需求侧支持）；轮储公告 ±3 天条款对滚动轮出周的适用性未定义；B 触发（pre_window_low5/B-HISTORY）未组装；D8 pass（上尾 2.0） |

信号席（不进候选 schema）：AU2612——加息 25bp 落地（12-0、点阵 16/18）、10Y 5.00%、美元 100.2、现货金决议后低点约 4,270→9/18 4,368.60、沪金主力 948.52（+1.41%）：fed_state 输入="加息落地·连续加息指引"，D13 按预设重写、#29 冻结 9/11-9/18 到期归档；SC2611-SC2612——快照 +43.5/分位 100（1td -9.7、10td +17.9）、SC2611 结算周涨 -0.30%（9/11→9/18，两端 settle available）、逐日 +11%/+6%/-1%/-6%/-9%（转引）→ ①"back 反弹"要件有实测读数（反弹侧但 9/17-9/18 收窄）、MA 周涨护栏本周未命中。

旧输出失效项：canonical v2.26 写入的 9/16 快照读数（MA2701-MA2705 +309、RB2701-RB2703 58.5、SC +56.7、SC2611 结算周涨 +22.56%、D8 MA 上尾 80.4、剩余 td 79/80、MA2701 ATR 分位 86.4、极差 79.0）全部由 9/19 快照刷新；上一读数的"周涨 >8%→冻结·清仓"处置已到期（条件式）不续延、本周未命中亦不恢复 MA 多头新开（#16 仍否决）；D12 既有提前窗 9/11-9/17 与 #29 9/11-9/18 到期；上周 9/12 诊断的 "本周无行情包/temporary_gap" 项（MA/RB 对、SC 结算、样本）已由快照解除。

风险容量只引用 canonical Step5 与 `scripts/futures_risk.py`；配置=单笔上限 5,250、常规组合上限 5,250、当前低敞口组合上限 5,000（高密度簇＋交易所公告＋D12 高波层条款命中）；实际净值、存量风险、挂单预留、保证金未核验，未对任何候选运行真实容量计算。现有材料没有完整历史候选账，不能判断连续空仓与机会成本，也不能把本周结果归因于 5,000 元上限。

**影子计划（首批，canonical 4.4）**：为最接近成立的两条候选事前登记假设性计划，供脚本 §5 按保守日线规则结算后归集到登记时的已核阻断（#5 / #16、D12），**只用于规则复评，不是交易信号、不授予任何许可**：(1) `SP-2026-09-19-MA-A-short-spread`——MA2701-MA2705 做空价差，限价 +312（9/18 两腿结算价差）、SL +380（价差在 100 分位基础上再走阔约 22%、超过 9/16-9/17 峰值区 +309/+330=近月挤仓延续、国内回归假设失效的明确价位）、TP +120（本对全生命周期 50 分位附近的部分回归目标；经济理由=国内装置 9 月中下旬复产＋国庆前后到港＋9/21、9/29 提保扩板压缩近月投机溢价）、入场有效期 2026-09-25、最晚退出 2026-10-23（近腿触 #1 前、覆盖 5-20 交易日）、乘数 10、往返成本 48 元/组（两腿开平合计滑点 4×tick_value=40＋手续费约 8）；净 R=(312−120)×10−48 ÷ (380−312)×10+48 = 1,872/728 ≈ 2.57（≥2.5 治理线，仅为假设）；登记时已核阻断=#5（产业反证）。(2) `SP-2026-09-19-MA2701-long-D`——MA2701 单合约突破多头，止损单 3155（H20 3154+1 tick）、SL 3018（Entry−1.5×ATR20 91.14，策略 D 口径）、TP 3429（Entry+2R）、有效期 2026-09-25、最晚退出 2026-10-23、乘数 10、往返成本 30；登记时已核阻断=#16（低敞口）、D12 高波层（非否决）。两条均于 2026-09-19（周六）20:00 上海时间登记；按 4.4 结算规则，周一 9/21 日线含周五夜盘不可用，首个可结算日线为 2026-09-22。

未完成事项按负责人/截止/到期处置列于 JSON `unresolved_items`。

## 结构化记录（schema 3）

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-09-19",
  "research_mode": "public_data",
  "assessment_scope": "proposed_framework_reassessment",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v2.27",
    "revision": "futures-framework/2026-09-19 branch (proposed, significant, 待合并); 基于 origin/main b6069b2 v2.26 (2026-09-17); 首次诊断按现行 v2.26 生成后于同分支按拟议 v2.27 刷新",
    "data_script_version": "v1.16 (branch; §0b EVENTS 滚动 + §2b.1 新增日结算涨跌列; 未联网实测). 本次回填仍用 v1.15 的 research/2026-09-19-data-snapshot.txt (AS_OF=20260919, 最新行情日 20260918, 快照完成标记存在)",
    "rule_changes_affecting_candidates": "v2.27 相对 v2.26: 规则本体零改动→候选判定与 status 不变; 状态层: ①改判中断证真 (MA 空头 #26 details 已按此; 方向许可不变), 交易所风控收紧 (exchange_notice 已核 9/21、9/29), D13 加息落地重写 (池外无候选), 负反馈行纠错 (RB D14 不适用, 判定不变), 低敞口继续 (#16 fail 维持); v1.16 新增 #30 输入列但本快照 (v1.15) 无该列→#30 仍 unknown. v2.26 相对上周诊断所用 v2.25: (1) 行情快照为唯一行情来源, 已有实测值不得写推算——本周全部价差/分位/样本/周涨/D8/ATR 取自快照; (2) D8 按 3.4 由脚本 §2d 计算 (MA 主力 MA2610 上尾 66.7 无档; SR/CF 空头否决档对 B 做多不适用); (3) 新增 awaiting_account 状态 (本周无候选满足: 无 signal=triggered); (4) shadow_plans 首批登记 2 条 (脚本 §5 结算); (5) 参考级数据: Kpler 通行量/海湾出口/战争险与 247 家铁水/盈利率不进门不记缺口; ① 量化锚=脚本 §1 SC 近端 back 方向; (6) 9/16 换月: MA 结构对 MA2701-MA2705、#30 判定腿与 A 近腿=MA2701、SC 信号对 SC2611-SC2612"
  },
  "snapshot": {
    "market_trade_date": "2026-09-18",
    "market_captured_at": null,
    "source_artifacts": [
      "research/2026-09-19-data-snapshot.txt (scripts/future_data.py v1.15, Tushare; AS_OF=20260919; 最新行情日 20260918; §0/§0b/§1/§2a/§2b/§2b.1/§2d/§5)",
      "research/2026-09-19-market-research.md (WebSearch 摘要转引, 2026-09-19; 原文读取被出口代理封锁)",
      "research/2026-09-16-data-snapshot.txt (上一快照, 仅作对照)",
      "framework/futures_framework.md v2.26 / framework/FUTURES_DATA_PROTOCOL.md v2.26 / projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md",
      "scripts/seasonal_plan.py 未运行 (B-HISTORY 输入未组装); scripts/futures_risk.py 未运行 (无完整计划与账户)"
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
      "portfolio_cap_current": 5000,
      "low_exposure_cash_cap": 5000,
      "source": "canonical 0)/Step5; 低敞口=高密度簇(9/21、9/29 提保扩板/9/30/10/1-10/8 长假/10/4/10/27-28)+交易所公告±1日+D12 高波层(MA2701 82.9)条款命中; 实际净值/占用未核"
    },
    "invalidated_legacy_outputs": [
      "canonical v2.26 写入的 9/16 快照读数: MA2701-MA2705 +309/分位 100, RB2701-RB2703 58.5, SC2611-SC2612 +56.7, SC2611 结算周涨 +22.56%(9/9→9/16), D8 MA 上尾 80.4 扣分档, 剩余 td 79/80/158, MA2701 ATR 分位 86.4, 极差 79.0——全部由 9/19 快照刷新",
      "上一读数 '周涨 >8% → 多头冻结·清仓' 处置已到期执行(条件式), 不续延; 本周 -0.30% 未命中, 不恢复多头新开(#16 仍否决)",
      "D12 既有提前窗 9/11-9/17、#29 AU/AG 冻结 9/11-9/18、0.0b 固定安排 (fixed_risk_window) 到期归档",
      "2026-09-12 诊断的 temporary_gap 项 (MA/RB 对分位与样本、SC 结算周涨、剩余 td 推算) 已由快照解除; 其 MA2610-MA2701 与 RB2610-RB2701 旧对记录随换月结案",
      "v2.27 新增失效项 (拟议): canonical v2.26 的 0.1/1.4/1.5/1.7 状态行 (①'中断复归侧评估'、D13'冻结至 FOMC'、交易所风控'阴性'、负反馈行'第五轮无记录'、fed_state'高概率基准'、AU 卡'趋势级回吐评估期') 已换版; 0.4/3.6/6.9 的 v2.25 定性表已换版; 9/16 快照读数由 9/19 快照替换"
    ]
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "MA2701-MA2705 A reversion domestic_public: 研究筛选/#1/#2/#13/#5/确认定义(draft)/交易所公告",
      "MA2705-MA2709 A 准备对: 样本与 #2 缺口登记",
      "RB2701-RB2703 与 RB2703-RB2705 A: 研究筛选未触发 (快照直接证据)",
      "MA2701 方向性多空: #1/#2/#16/#26/#30/周涨护栏/D8/#20/D12/交易所公告",
      "SR2701-SR2705 A: 研究筛选未触发",
      "SR2701/CF2701 B: B-WINDOW 日期筛选、品种卡专属否决、#5 独立产业事实、D8、B 触发/B-HISTORY 缺口",
      "M2701: research_only 登记"
    ],
    "missing_scope": [
      "MA2701 逐日结算涨跌 (#30 判定腿) 与 SC 逐日结算 (护栏两端仅周度已核)",
      "甲醇港口/华东社会库存同口径周度数值 (两入口阴性)",
      "Mysteel 五大品种同口径钢材总库存 (两入口阴性; 兰格口径不可代)",
      "实际账户/持仓/挂单/保证金/费用",
      "SR/CF B 的 PLAN-B-history 三年同窗样本、pre_window_low5、Entry/SL/TP1、planned_exit 真实交易日映射 (seasonal_plan.py 未运行)",
      "郑商所 9/21 起 PTA/甲醇/PX 单独通知原文; INE 对 SC 公告 (阴性)",
      "MA2705-MA2709 准备对样本 (24/21/22<33) 与 MA2709 20 日均量"
    ],
    "research_only_scope": [
      "geopolitical_fade / 中断因果模型 (①改判中断证真后更不适用; 复活须按 v2.26 新要件重定义)",
      "M2701 无已许可具体策略 (仅观察)"
    ],
    "signal_observations": [
      "AU2612: 加息 25bp 落地 (12-0, 点阵 16/18 年内再加, 2026 末中位 4.1%); 10Y 5.00%; 美元 100.2; 现货金决议后低点约 4,270 → 9/18 4,368.60 (周 -0.4%); 沪金主力 948.52 (+1.41%); fed_state 输入='加息落地·连续加息指引'; #29 9/11-9/18 到期归档; 不建仓",
      "SC2611-SC2612: 快照 +43.5/分位 100 (1td -9.7, 5td -0.8, 10td +17.9); SC2611 结算周涨 -0.30% (9/11→9/18 两端 settle, available); 逐日收盘 +11%/+6%/-1%/-6%/-9% (转引); SC2611 OHLC 无效 → 单合约指标 unknown, 结算端点独立有效; ①'back 反弹' 要件有读数 (反弹侧, 9/17-9/18 收窄)"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "snap_ma_pair",
      "metric": "MA2701-MA2705 价差 / 近3年同期分位 / 样本",
      "value": "+312.0 元/吨 (+11.707%); 分位 100.0; 样本 41/41/41 complete; 1td -18 / 5td +30 / 10td +123",
      "unit": "元/吨, 分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1",
      "original_source": "scripts/future_data.py v1.15 (Tushare 日线; 两腿 settle)",
      "price_basis": "settle/settle",
      "comparison_basis": "近3年同期 ±20 交易日窗口 (MA2601-2605/2501-2505/2401-2405, 各 41/41)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_ma2701_td",
      "metric": "MA2701 / MA2705 剩余交易日与 20 日均成交量",
      "value": "MA2701 76 td, 540,023 手; MA2705 155 td, 19,628 手",
      "unit": "交易日, 手",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1/§2b",
      "original_source": "scripts/future_data.py v1.15 (trade_cal 真实交易日)",
      "price_basis": null,
      "comparison_basis": "0.3#1 (≥20 td) / #2 (20 日均量 ≥1 万手)",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_ma_prep_pair",
      "metric": "MA2705-MA2709 准备对价差 / 分位 / 样本",
      "value": "+99.0 元/吨 (+3.858%); 分位 100.0; 样本 24/41、21/41、22/41 (各年 <33) incomplete; 远腿 20 日均量缺失; 5td/10td 变化 null (missing_pair_sessions)",
      "unit": "元/吨, 分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1 [MA换月准备]",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle/settle",
      "comparison_basis": "3.1 A 同期样本验收 (每年 ≥33/41)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_ma2709_vol",
      "metric": "MA2709 20 日均成交量",
      "value": null,
      "unit": "手",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1 (#2: 远腿成交量缺失, 不足 20 个完整有效样本)",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": null,
      "comparison_basis": "0.3#2",
      "role": "required_execution",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_rb_pair",
      "metric": "RB2701-RB2703 价差 / 分位 / 样本 / 成交与期限",
      "value": "-8.0 元/吨 (-0.257%); 分位 56.1; 样本 41/41/41 complete; RB2701 669,156 手/77 td; RB2703 27,445 手/113 td; 1td +1 / 5td +13 / 10td +11",
      "unit": "元/吨, 分位, 手, 交易日",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1 [RB]",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle/settle",
      "comparison_basis": "研究筛选线 分位 ≥70 (候选) / ≥85 (高分位)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_rb_prep_pair",
      "metric": "RB2703-RB2705 准备对价差 / 分位 / 成交",
      "value": "-8.0 元/吨 (-0.256%); 分位 61.8; 样本 complete; RB2703 27,445 手/113 td; RB2705 13,672 手/156 td",
      "unit": "元/吨, 分位, 手",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1 [RB换月准备]",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle/settle",
      "comparison_basis": "研究筛选线 分位 ≥70",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_sr_pair",
      "metric": "SR2701-SR2705 价差 / 分位 / 成交与期限",
      "value": "-78.0 元/吨 (-1.443%); 分位 0.0; 样本 complete; SR2701 470,759 手/76 td; SR2705 40,611 手/155 td",
      "unit": "元/吨, 分位, 手",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1 [SR]",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle/settle",
      "comparison_basis": "研究筛选线 分位 ≥70",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_sc_pair",
      "metric": "SC2611-SC2612 近端月差 / 分位 (①量化锚)",
      "value": "+43.5 元/桶 (+6.119%); 分位 100.0; 1td -9.7 / 5td -0.8 / 10td +17.9 (9/16 快照 +56.7)",
      "unit": "元/桶, 分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1 [SC近端]",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle/settle",
      "comparison_basis": "近3年同期 ±20 交易日; 1.7 ① 要件 'SC 近端 back 反弹'",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_sc_weekly",
      "metric": "SC2611 结算周涨% (MA 原油周涨护栏口径腿)",
      "value": -0.30,
      "unit": "%",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §2b.1",
      "original_source": "scripts/future_data.py v1.15 (两端 settle 756.70 → 754.40; 状态 available)",
      "price_basis": "settle/settle",
      "comparison_basis": "2026-09-11 → 2026-09-18 (最新行情日减 7 自然日); 护栏 >5%/>8%",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_d8_ma",
      "metric": "D8 周涨分位 MA (主力 MA2610)",
      "value": "+0.93%; 上尾位 66.7 / 下尾位 33.3; 样本 153/153 available; 无档",
      "unit": "%, 分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §2d",
      "original_source": "scripts/future_data.py v1.15 (canonical 3.4 口径)",
      "price_basis": "settle/settle",
      "comparison_basis": "近3年周样本; 商品多头前 20% 扣分/前 10% 否决 (上尾)",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_d8_sr",
      "metric": "D8 周涨分位 SR (主力 SR2701)",
      "value": "-2.22%; 上尾位 5.9 / 下尾位 94.1; 空头否决档 (前 10%); 样本 153/153",
      "unit": "%, 分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §2d",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle/settle",
      "comparison_basis": "B 做多看上尾",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_d8_cf",
      "metric": "D8 周涨分位 CF (主力 CF2701)",
      "value": "-3.98%; 上尾位 2.0 / 下尾位 98.0; 空头否决档 (前 10%); 样本 153/153",
      "unit": "%, 分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §2d",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle/settle",
      "comparison_basis": "B 做多看上尾",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_ma2701_indicators",
      "metric": "MA2701 单合约指标 (§2a/§2b)",
      "value": "settle 2977; 周涨 -2.90% (3066→2977); ATR20 91.14; ADX14 38.3; HV20/HV60 1.22; ATR250 分位 82.9 (高波层, 样本 164); H250 3154 / dist_H250 5.61%; H20 3154 / L20 2604; MA20 2892.9 / MA60 2659.7; 2ATR 情景 1,843 → 预检上界 1 手; 76 td; 540,023 手",
      "unit": "元/吨, %, 分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §2a/§2b/§2b.1",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": "settle",
      "comparison_basis": "3.5b D12 (ATR20 分位 >80 或 HV20/HV60 >1.3); #20 (创 250 日 H); #1/#2",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_atr_gap",
      "metric": "池内 ATR250 分位极差",
      "value": "77.4 (M2701 99.4 ↔ CF2701 22.0); 错位 (>50)",
      "unit": "分位",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §2b",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": null,
      "comparison_basis": "0.1 错位子维 >50",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_events_0919",
      "metric": "快照 §0b 事件节点 (未来 10 个交易日)",
      "value": "2026-09-30 俄柴油禁令到期 [T-6]; 2026-10-04 OPEC+ [T-7]; 13 个配置合约均 ≥20 td",
      "unit": "事件",
      "observation_date": "2026-09-19",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §0/§0b",
      "original_source": "scripts/future_data.py v1.15 (EVENTS 用户配置; trade_cal)",
      "price_basis": null,
      "comparison_basis": "0.0b 事件日历核对",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_shadow_ledger",
      "metric": "快照 §5 影子账本",
      "value": "尚无登记的影子计划",
      "unit": "条",
      "observation_date": "2026-09-19",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §5",
      "original_source": "scripts/future_data.py v1.15",
      "price_basis": null,
      "comparison_basis": null,
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "czce_margin_notice_0917",
      "metric": "郑商所 2026 年中秋/国庆期间甲醇期货保证金与涨跌停板调整",
      "value": "9/21 结算起: MA2610 涨跌停 9%, MA2611 保证金 9%/涨跌停 8%; 9/29 结算起: 甲醇全部合约保证金 10%、涨跌停 9%; 10/8 恢复交易后自持仓量最大合约未出现涨跌停单边市的首个交易日结算起回落",
      "unit": "%",
      "observation_date": "2026-09-17",
      "published_at": "2026-09-17",
      "source_url_or_file": "https://news.qq.com/rain/a/20260917A0F4VY00",
      "original_source": "郑州商品交易所 (新浪/腾讯/凤凰多源转引; 原文未核; 另有 9/21 起 PTA/甲醇/PX 单独通知未核)",
      "price_basis": null,
      "comparison_basis": "0.1 交易所风控 (常规→收紧); 2.3 ×0.8; 0.3 护栏 公告±1日 门槛+0.3",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma2701_daily_settle",
      "metric": "MA2701 逐日结算价对 pre_settle 涨跌幅 (9/14-9/18; #30 判定腿)",
      "value": null,
      "unit": "%",
      "observation_date": "2026-09-18",
      "published_at": null,
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt (仅周涨, 无逐日 pre_settle 列); 公开收评未列 MA2701 逐日",
      "original_source": "未取得",
      "price_basis": "settle vs pre_settle",
      "comparison_basis": "0.3#30 单日 ≥5%",
      "role": "required_execution",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_main_intraday_0916",
      "metric": "甲醇主力 (MA2610) 日内涨幅",
      "value": "+4% 报 3559 (日内); 收盘 +3%",
      "unit": "元/吨, %",
      "observation_date": "2026-09-16",
      "published_at": "2026-09-16",
      "source_url_or_file": "https://news.qq.com/rain/a/20260916A04P0Z00",
      "original_source": "腾讯财经 (郑商所行情转引; 主力=MA2610, 非执行腿 MA2701)",
      "price_basis": "intraday/close vs pre_settle (媒体口径)",
      "comparison_basis": "对前一交易日结算价",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sc_daily_0914_0918",
      "metric": "SC 主力逐日收盘涨跌 (信号腿)",
      "value": "9/14 +11%~12%; 9/15 +6%; 9/16 -1%; 9/17 -6%; 9/18 -9% (早盘 -8%)",
      "unit": "%",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://news.qq.com/rain/a/20260918A06WCO00",
      "original_source": "腾讯/财闻网/搜狐收评 (多源同口径转引; 收盘口径非结算)",
      "price_basis": "close vs pre_settle (媒体口径)",
      "comparison_basis": "0.3#30 能源链单日 ≥5% (信号席仅记录)",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sc_close_762_unverified",
      "metric": "SC2611 收盘 762.5 (-42.5, -5.28%)",
      "value": "762.5",
      "unit": "元/桶",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://news.qq.com/rain/a/20260918A04WPM00",
      "original_source": "腾讯 (日期/时点未核; 与多源 '跌超 9%' 及快照 settle 754.40 不同口径)",
      "price_basis": "close",
      "comparison_basis": "对前结算",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_plant_outage_0911",
      "metric": "中东甲醇装置停车比例 / 伊朗在产装置",
      "value": "约 62% 装置停车; 伊朗在产约 7 套, 日产 2-2.5 万吨",
      "unit": "%, 套, 万吨/日",
      "observation_date": "2026-09-10",
      "published_at": "2026-09-11",
      "source_url_or_file": "https://news.qq.com/rain/a/20260911A06K2O00",
      "original_source": "腾讯 (行业口径转引; 与 9/10 界面报道一致; 本周无更新读数, 为最近可得)",
      "price_basis": null,
      "comparison_basis": "供给端 (近月强) 独立产业事实; 对做空价差为反证",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_port_inventory_qual",
      "metric": "甲醇港口库存 (定性)",
      "value": "港口库存进一步走低 (无日期; 数值未取得)",
      "unit": "定性",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "https://m.cngold.org/futures/lm2526/",
      "original_source": "金投网 (无日期摘要; 隆众/卓创同口径周度数值两入口阴性)",
      "price_basis": null,
      "comparison_basis": "近五年同期",
      "role": "required_model",
      "quality": "stale",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_plant_restart_fwd_0911",
      "metric": "国内甲醇装置检修恢复 (前瞻)",
      "value": "9 月中下旬检修装置陆续恢复 (预期)",
      "unit": "定性",
      "observation_date": "2026-09-10",
      "published_at": "2026-09-11",
      "source_url_or_file": "https://news.qq.com/rain/a/20260911A06K2O00",
      "original_source": "腾讯/界面 (前瞻表述, 非已观测)",
      "price_basis": null,
      "comparison_basis": "供给端反向前瞻 (支持做空价差方向但未观测)",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "salalah_postponed_0913",
      "metric": "萨拉拉伊朗-海合会外长会 (①反向质变候选日)",
      "value": "推迟, 无新日期 (阿曼外交部 9/13)",
      "unit": "事件",
      "observation_date": "2026-09-13",
      "published_at": "2026-09-14",
      "source_url_or_file": "https://www.npr.org/2026/09/14/nx-s1-5968072/talks-between-iran-and-gulf-states-to-discuss-strait-of-hormuz-postponed",
      "original_source": "阿曼新闻社 (CNN/NPR/半岛/RFE/RL 多源转引)",
      "price_basis": null,
      "comparison_basis": "1.7 ① 反向质变要件 (官方停火/重开) 未出现",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "us_iran_tanker_strikes_0908_0909",
      "metric": "美击沉/瘫痪 5 艘伊朗油轮; 伊袭 10 艘船 (①要件 '再袭船/扩大打击')",
      "value": "9/8-9/9 多源命中 (canonical v2.26 已✓)",
      "unit": "事件",
      "observation_date": "2026-09-09",
      "published_at": "2026-09-09",
      "source_url_or_file": "https://www.aljazeera.com/news/2026/9/9/us-destroys-five-iranian-tankers-iran-retaliates-with-attacks-on-jordan-base",
      "original_source": "半岛/CNBC (多源; 上周已核)",
      "price_basis": null,
      "comparison_basis": "1.7 ① 中断证真要件一",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "historical"
    },
    {
      "evidence_id": "irgc_tanker_trend_0917",
      "metric": "IRGC 称再袭油轮 Trend (多哥籍)",
      "value": "9/17 夜被击中起火、被迫停船 (IRGC 单方口径, 无独立确认)",
      "unit": "事件",
      "observation_date": "2026-09-17",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://www.globalsecurity.org/wmd/library/news/iran/2026/09/iran-260918-rferl01.htm",
      "original_source": "IRGC 海军 (RFE/RL 转引; 单源)",
      "price_basis": null,
      "comparison_basis": "① 要件一再命中候选 (待多源确认)",
      "role": "required_model",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "centcom_convoy_0917",
      "metric": "美军护航油轮过霍尔木兹 (参考级)",
      "value": "CENTCOM: 40 艘, 约 1,800 万桶; Vortexa 当日 4 次 / Kpler 12 次原油过境 (不符)",
      "unit": "艘, 万桶",
      "observation_date": "2026-09-17",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://easternherald.com/market/brent-crude-oil-price-september-18-2026-centcom-hormuz-escort/",
      "original_source": "CENTCOM / Vortexa / Kpler (转引; 【v2.26】通行量为参考级)",
      "price_basis": null,
      "comparison_basis": "① 反向监测 (非要件)",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "saudi_pipeline_0910_0918",
      "metric": "沙特东西原油管道遇袭关停→半恢复",
      "value": "9/10-11 伊拉克境内无人机袭击; 9/12 预防性关停 (4-5 百万桶/日); 9/17-18 以约一半产能 (2-2.5 百万桶/日) 重启至延布 + 苏哈尔船对船过驳",
      "unit": "事件, 百万桶/日",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://www.aljazeera.com/news/2026/9/12/saudi-arabia-shuts-critical-oil-pipeline-after-drone-attack-what-happened",
      "original_source": "半岛/CNBC/彭博 (遇袭关停, 多源); Easternherald/CNBC/FX168 (半恢复, 转引)",
      "price_basis": null,
      "comparison_basis": "供给冲击第三形态 '绕行通道袭击/修复' (非①要件)",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "brent_0918",
      "metric": "布伦特结算",
      "value": "103.87 美元/桶 (-0.9%); 周 -0.7%~-1%; 9/14 触 108",
      "unit": "美元/桶",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://www.cnbc.com/2026/09/18/oil-prices-today-brent-wti-saudi-arabia-houthi.html",
      "original_source": "CNBC (转引; tradingeconomics 另读数 103.21 为不同时点)",
      "price_basis": "settle",
      "comparison_basis": "9/11 收 104.61",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "fomc_0916",
      "metric": "FOMC 决议",
      "value": "加息 25bp 至 3.75%-4.00%; 12-0; 声明 '通胀仍然偏高'; 点阵 16/18 预计年内再加一次; 2026 末中位 4.1% (前 3.8%)",
      "unit": "bp, %",
      "observation_date": "2026-09-16",
      "published_at": "2026-09-16",
      "source_url_or_file": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm",
      "original_source": "美联储 (CNBC/Fox/Schwab/AdvisorPerspectives 多源转引; 原文未核)",
      "price_basis": null,
      "comparison_basis": "上期定价 80-90% 加息; 预设三剧本",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "rates_fx_gold_0918",
      "metric": "10Y 美债 / 美元指数 / 现货金 / 沪金 / 10 月加息概率",
      "value": "10Y 5.00%; DXY 100.2 (盘中 100.4, 七周高); 现货金 4,368.60 (+0.6%; 决议后低点约 4,270; 周 -0.4%); 沪金主力 948.52 (+1.41%; 另读数 935 时点不同); 10 月加息概率 49% (记者会后) → 57% (9/18)",
      "unit": "%, 点, 美元/盎司, 元/克",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://www.usagold.com/daily-precious-metals-market-report-september-18-2026/",
      "original_source": "tradingeconomics / Gokhshtein / USAGOLD / 彭博 / 新浪 / CME FedWatch (Schwab 转引)",
      "price_basis": "spot/close",
      "comparison_basis": "上期 10Y 4.96%, DXY 99.1, 金 4,385.61, 沪金 942",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "coke_round5_landed_0910",
      "metric": "焦炭第五轮提涨",
      "value": "9/8 多地焦企发起; 9/10 主流钢厂全面落地 (湿熄 +100 / 干熄 +110); 钢厂亏损扩大、减产计划增多、第六轮观望",
      "unit": "元/吨",
      "observation_date": "2026-09-10",
      "published_at": "2026-09-10",
      "source_url_or_file": "https://news.qq.com/rain/a/20260910A0BHQ800",
      "original_source": "腾讯 9/10、21 经济 9/8 (多源转引)",
      "price_basis": null,
      "comparison_basis": "第四轮 9/3-9/4; 1.4 负反馈检验点",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "coke_round5_norecord_prior",
      "metric": "焦炭第五轮 9/5-9/11 '无公开发起或落地记录' (上周判定)",
      "value": "无记录 (unknown)",
      "unit": "定性",
      "observation_date": "2026-09-11",
      "published_at": "2026-09-12",
      "source_url_or_file": "research/2026-09-12-market-research.md (证据表 '焦炭第五轮提涨' 行)",
      "original_source": "上周两入口检索阴性结论 (检索遗漏)",
      "price_basis": null,
      "comparison_basis": "1.4 负反馈检验点",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "steel_inventory_langge_0916",
      "metric": "兰格&找钢 全国重点钢材品种产量与库存 (与 Mysteel 五大品种口径不同源)",
      "value": "产量 1,140.94 万吨 (-10.92); 总库存 2,101.77 万吨 (-29.13); 建材产量 417.87 (-11.13); 建材总库存 1,061.27 (-31.43); 表需 449.30",
      "unit": "万吨",
      "observation_date": "2026-09-16",
      "published_at": "2026-09-16",
      "source_url_or_file": "https://news.qq.com/rain/a/20260916A0BV8L00",
      "original_source": "兰格钢铁网 & 找钢网 (腾讯转引)",
      "price_basis": null,
      "comparison_basis": "周环比 (同源)",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "steel_inventory_mysteel_thisweek",
      "metric": "Mysteel 五大品种钢材总库存 (9/17 当周)",
      "value": null,
      "unit": "万吨",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "两入口阴性 (mysteel.com / 搜索摘要仅返回 9/3 的 1,572.90)",
      "original_source": "Mysteel (未取得)",
      "price_basis": null,
      "comparison_basis": "9/3 1,572.90 (-18.56)",
      "role": "optional_context",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "nbs_aug_0915",
      "metric": "国家统计局 8 月硬数据",
      "value": "工业增加值 +5.2%; 社零 8 月 +0.4% (1-8 月 +1.1%); 固投 1-8 月 -7.2% (扣除地产 -4.2%); 房地产开发投资 -19.9%",
      "unit": "%",
      "observation_date": "2026-08-31",
      "published_at": "2026-09-15",
      "source_url_or_file": "https://www.stats.gov.cn/sj/zxfbhjd/202609/t20260915_1965307.html",
      "original_source": "国家统计局 (新华社/21 经济/中新网多源转引; 原文未核)",
      "price_basis": null,
      "comparison_basis": "7 月",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ashare_week_0918",
      "metric": "A 股 9/18 与本周",
      "value": "沪指 3911.87 (+0.94%), 周 +0.61%; 创业板周 +1.52%; 9/18 成交 2.09 万亿, 本周日均 1.81 万亿; 两融 26,308 亿 (+74 亿/周)",
      "unit": "点, 亿元",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://news.qq.com/rain/a/20260918A0BBR200",
      "original_source": "新浪/东方财富/21 财经 (多源同口径转引)",
      "price_basis": "close",
      "comparison_basis": "上周沪指 -1.07%, 成交 1.97 万亿",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sugar_sales_aug",
      "metric": "广西 2025/26 榨季截至 8 月底产销率 / 工业库存",
      "value": "产销率 80.56% (同比 -8.48pp); 工业库存 149.61 万吨 (同比 +78.74)",
      "unit": "%, 万吨",
      "observation_date": "2026-08-31",
      "published_at": "2026-09-03",
      "source_url_or_file": "https://www.yntw.com/2026/09/39098.html",
      "original_source": "广西糖业协会 (糖网转引; 月度; 9 月数据未发布)",
      "price_basis": null,
      "comparison_basis": "去年同期",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sugar_prices_0918",
      "metric": "SR2701 / 广西现货 / ICE 原糖",
      "value": "SR2701 9/18 早盘 5315 (-0.71%); 广西现货 5090-5170 (-10~-30); ICE 10 月原糖 17.42 美分/磅 (9/10 18.76)",
      "unit": "元/吨, 美分/磅",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://www.yntw.com/2026/09/39229.html",
      "original_source": "糖网 / Barchart (转引)",
      "price_basis": "intraday/close",
      "comparison_basis": "9/8 5487; 9/10 18.76",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "cotton_reserve_0918",
      "metric": "储备棉轮出成交率 / 累计",
      "value": "9/18 成交率 96.37% (计划 8,256 吨, 成交 7,956 吨; 本轮首见 <100%); 均价 16,596.60; 累计成交 358,199 吨 / 99.15%",
      "unit": "%, 吨, 元/吨",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://k.sina.cn/article_5952915720_162d2490806704uwmq.html",
      "original_source": "中国储备棉管理有限公司 (新浪抛储日报转引)",
      "price_basis": null,
      "comparison_basis": "9/7 成交率 100%",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "cotton_seed_price_0918",
      "metric": "新季籽棉开秤价预期 / 新棉上市",
      "value": "开秤价预期下移至 7.0-7.5 元/公斤; 新棉上市提速与轮出双重施压",
      "unit": "元/公斤",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://k.sina.cn/article_5953740931_162dee08306703zbjg.html",
      "original_source": "上棉棉花日报 (新浪转引; 预期表述)",
      "price_basis": null,
      "comparison_basis": null,
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "russia_diesel_ban_report_0916",
      "metric": "俄柴油出口禁令延期",
      "value": "生产商柴油出口限制拟延至 10 月底 (Vedomosti 两名匿名消息人士; 政府未官宣); 当前禁令 9/30 到期",
      "unit": "政策",
      "observation_date": "2026-09-16",
      "published_at": "2026-09-16",
      "source_url_or_file": "https://www.hydrocarbonprocessing.com/news/2026/09/russia-set-to-extend-diesel-export-ban-until-end-of-october/",
      "original_source": "Vedomosti (路透/HydrocarbonProcessing/OilPrice 转引; 报道级)",
      "price_basis": null,
      "comparison_basis": "1.4 俄乌轴 '9-30 延期 (升级)' 形态",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "iea_omr_sep2026",
      "metric": "IEA 9 月报",
      "value": "2026 需求 -250 万桶/日 (较上月 -94 万); 2027 +260 万; 8 月全球产量 1.001 亿桶/日 (-160 万); 海湾 >1,000 万桶/日仍关停, 恢复推迟至 2027; 开战以来观测库存 -5.07 亿桶 (8 月 -9,500 万)",
      "unit": "万桶/日, 百万桶",
      "observation_date": "2026-08-31",
      "published_at": "2026-09-15",
      "source_url_or_file": "https://www.iea.org/reports/oil-market-report-september-2026",
      "original_source": "IEA (摘要转引; 发布日按月中估计, 原文未核)",
      "price_basis": null,
      "comparison_basis": "8 月报",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "b_window_calendar",
      "metric": "1.6 B-WINDOW 日期表",
      "value": "SR-summer 07-01 至 09-30 (2026-09-18 在窗内; planned_exit=window_end 前第 5 个交易日 ≈ 2026-09-23, 人工推算待 seasonal_plan.py 核); CF-autumn 09-01 至 10-31 (在窗内)",
      "unit": "日期",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-10",
      "source_url_or_file": "framework/futures_framework.md 1.6 B-WINDOW (v2.24 定义)",
      "original_source": "canonical 1.6 (rule_version=B-v2.24)",
      "price_basis": null,
      "comparison_basis": "TRIGGER-B: research_start ≤ 审计交易日 ≤ window_end",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    }
  ],
  "candidates": [
    {
      "candidate_id": "2026-09-18|MA2701-MA2705|A|short_spread|v2.26",
      "opportunity_id": "MA_A_2701_2705",
      "trade_date": "2026-09-18",
      "contracts": ["MA2701", "MA2705"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "short_spread",
      "data_feasibility": "available",
      "data_feasibility_reason": "快照实测价差/分位/样本 complete; 独立产业事实可得 (最近读数 9/10-9/11); 港口库存数值缺为子项, 不改可得性",
      "signal": "unknown",
      "signal_basis": "研究筛选 ≥85 (高分位候选) 不构成信号; 确认定义 draft 未冻结 → signal unknown",
      "screening_evidence": "snap_ma_pair",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma_pair"],
          "details": "近3年同期分位 100.0 ≥85 (高强度研究候选); 价差 +312, 5td +30 / 10td +123 (走阔); 仅筛选, 不给方向"
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_td"],
          "details": "近腿 MA2701 76 td ≥20; 结构退出边界=近腿触 #1 (≈2026-12-17) 或主力换月, 先到为准"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_td"],
          "details": "MA2701 540,023 手 / MA2705 19,628 手, 均 ≥1 万手"
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma_pair"],
          "details": "同期样本 41/41/41 complete (≥33/41 各年); 分位用实际有效原值"
        },
        {
          "rule_id": "domestic_model_basis",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["ma_plant_restart_fwd_0911"],
          "details": "海峡未缓和时支持收敛的独立国内变化: 候选=国内装置 9 月中下旬复产 (前瞻, 未观测) + 国庆前后到港 + 提保扩板压缩近月溢价; 尚未以已观测数据论证; 若获利仍依赖地缘缓和则属 geopolitical_fade",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "按 3.1 MA 研究交付责任: 用港口库存/到港/装置开工的已观测数值论证 '即使海峡状态未缓和, 哪项独立国内变化仍支持收敛'; 论证失败则明确结案",
            "due_at": "2026-09-25"
          }
        },
        {
          "rule_id": "confirmation_definition",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["snap_ma_pair"],
          "details": "本周给出 draft (见 plan.confirmation_definition), state=draft 未冻结; 冻结前只作前瞻, 不回判本周; 观测: 9/18 价差 +312, 9/17 +330 (10 日内峰)",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "研究方复核 draft 的指标/阈值/经济理由后冻结 (state=frozen, effective_from 不早于冻结后首个完整交易日), 或说明不能冻结的原因",
            "due_at": "2026-09-25"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["ma_plant_outage_0911"],
          "details": "(b) 独立产业事实已核反证: 中东约 62% 装置停车/伊朗在产约 7 套 (9/10-9/11 最近可得读数) 支持近月走强, 与做空价差反向; 主力 MA2610 周 +0.93% vs MA2701 -2.90% 为价格结构不计产业; (a) 价格确认 draft 未冻结=unknown 子项单列; 港口库存 '进一步走低' 为无日期定性 (stale) 与装置复产前瞻 (未观测) 只入 diagnostic",
          "diagnostic_evidence_refs": ["ma_port_inventory_qual", "ma_plant_restart_fwd_0911", "ma_main_intraday_0916"]
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_notice_0917"],
          "details": "郑商所 9/17 公告: 9/21 起 MA2610/2611 分级、9/29 起甲醇全合约保证金 10%/涨跌停 9% → 结构双腿按实际保证金口径计占用, ×0.8 缓冲 (0.1/2.3), 公告 ±1 日门槛 +0.3; 非否决"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无冻结的 Entry/真实失效 SL/TP/净 R/期限; 本周登记影子计划 SP-2026-09-19-MA-A-short-spread (+312/+380/+120, 净 R≈2.57) 仅为规则复评假设, 不是候选计划",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "在确认定义冻结与国内路线论证完成后, 按策略 A 协议出具四点包 (方向/经济失效 SL/目标与期限/净 R), 含两腿限价/滑点/裸腿预案与提保扩板期间保证金口径",
            "due_at": "2026-09-25"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无当期经核实账户与挂单快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["screening", "#1", "#2", "#13", "domestic_model_basis", "confirmation_definition", "#5", "exchange_notice", "execution_plan", "account"],
      "all_blockers": ["#5"],
      "unknown_checks": ["domestic_model_basis", "confirmation_definition", "execution_plan", "account"],
      "first_blocker": "#5",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": ["D9=3 default_neutral"],
        "notes": "D4=5 (分位 100, 样本满足); D2=1 (已核反证); D1=null (定义未冻结); D3=null (计划缺失); D5=null (期限满足但持有期与事件跨越待计划); 完整总分 null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "draft",
          "rule_version": "A-MA-2701-2705-draft1",
          "defined_at": "2026-09-19T20:00:00+08:00",
          "effective_from": null,
          "price_basis": "两腿 settle 之差 S=MA2701-MA2705 (元/吨)",
          "economic_rationale": "做空价差的价格确认=近月挤仓溢价开始回吐: S 连续 2 个交易日收于 [前 10 个交易日 S 最高值 − 0.65×MA2701 ATR20(当期 91→约 60 元/吨)] 之下, 且同期主力-执行腿 (MA2610-MA2701) 价差不再走阔 (以 settle 计); 阈值以 ATR 比例而非固定元数设定, 避免 '40 元/三日' 类任意门槛; 与 D1 分工: 仅评价价格模式, 产业支持/反证归 D2/#5(b); 未冻结, 不回判 9/14-9/18",
          "observed_values": "2026-09-18 S=+312; 2026-09-17 S=+330; 前 10 交易日最高 ≥ +330; MA2701 ATR20 91.14"
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": ["snap_ma_pair", "snap_ma2701_td", "ma_plant_outage_0911", "czce_margin_notice_0917"]
    },
    {
      "candidate_id": "2026-09-18|MA2705-MA2709|A|unknown|v2.26",
      "opportunity_id": "MA_A_2705_2709_prep",
      "trade_date": "2026-09-18",
      "contracts": ["MA2705", "MA2709"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "准备对: 同期样本 24/21/22<33 (各年) 且 MA2709 20 日均量缺失 (#2 缺失); 本可取得的必要资料本期不足, 非长期不可得",
      "signal": "unknown",
      "signal_basis": null,
      "screening_evidence": "snap_ma_prep_pair",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["snap_ma_prep_pair"],
          "details": "分位 100 但样本 incomplete, 快照注 '不能视为已过门'",
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "MA2709 上市历史积累至各年 ≥33/41 同期样本后重算; 在此之前仅取样",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["snap_ma2709_vol"],
          "details": "MA2709 20 日均成交量缺失 (不足 20 个完整有效样本); 缺失≠未过",
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "MA2709 完整 20 个有效成交日后由脚本 §1 回填; 过 #2 (≥1 万手) 前不作远腿",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["snap_ma_prep_pair"],
          "details": "关键价差序列/同期样本不足 (24/21/22<33) → incomplete, 不得执行; 不算已证实否决",
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "同 screening; 达标前 temporary_gap",
            "due_at": "next_report"
          }
        }
      ],
      "evaluation_order": ["screening", "#2", "#13"],
      "all_blockers": [],
      "unknown_checks": ["screening", "#2", "#13"],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "样本缺失 → D4=null; 不评分"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": ["snap_ma_prep_pair"]
    },
    {
      "candidate_id": "2026-09-18|RB2701-RB2703|A|unknown|v2.26",
      "opportunity_id": "RB_A_2701_2703",
      "trade_date": "2026-09-18",
      "contracts": ["RB2701", "RB2703"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "available",
      "data_feasibility_reason": "快照实测价差/分位/样本 complete; Mysteel 同口径总库存缺为子项, 不阻断未触发结案",
      "signal": "not_triggered",
      "signal_basis": "近3年同期分位 56.1 < 70 研究筛选线 (快照 §1 直接证据)",
      "signal_evidence_refs": ["snap_rb_pair"],
      "screening_evidence": "snap_rb_pair",
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_rb_pair"],
          "details": "RB2701 77 td ≥20; RB2703 113 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_rb_pair"],
          "details": "RB2701 669,156 手 / RB2703 27,445 手"
        },
        {
          "rule_id": "D14",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "独立国内月差不依赖复产/铁水/收缩成本假设; 【v2.26】铁水为参考; 焦炭第五轮落地 (纠错) 与钢厂减产计划仅为背景, 不构成本对触发或否决"
        }
      ],
      "evaluation_order": ["#1", "#2", "D14"],
      "all_blockers": [],
      "unknown_checks": [],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "未触发, 不评分 (D4 分位 56.1 未达研究筛选)"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": ["domestic_public 独立产业证据 (兰格口径去库加速/第五轮落地仅记录)", "confirmation_definition", "#5", "execution_plan", "account"],
      "evidence_refs": ["snap_rb_pair", "steel_inventory_langge_0916", "coke_round5_landed_0910"]
    },
    {
      "candidate_id": "2026-09-18|RB2703-RB2705|A|unknown|v2.26",
      "opportunity_id": "RB_A_2703_2705_prep",
      "trade_date": "2026-09-18",
      "contracts": ["RB2703", "RB2705"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "available",
      "data_feasibility_reason": "准备对仅取样; 快照实测分位/样本 complete、RB2705 过 #2",
      "signal": "not_triggered",
      "signal_basis": "近3年同期分位 61.8 < 70 (快照 §1 直接证据); 准备对不提前改变当前执行腿",
      "signal_evidence_refs": ["snap_rb_prep_pair"],
      "screening_evidence": "snap_rb_prep_pair",
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_rb_prep_pair"],
          "details": "RB2703 113 td / RB2705 156 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_rb_prep_pair"],
          "details": "RB2703 27,445 手 / RB2705 13,672 手 (过 #2)"
        }
      ],
      "evaluation_order": ["#1", "#2"],
      "all_blockers": [],
      "unknown_checks": [],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "未触发, 不评分"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": ["独立产业证据", "confirmation_definition", "#5", "execution_plan", "account"],
      "evidence_refs": ["snap_rb_prep_pair"]
    },
    {
      "candidate_id": "2026-09-18|MA2701|directional|long|v2.26",
      "opportunity_id": "MA_D_long_2701",
      "trade_date": "2026-09-18",
      "contracts": ["MA2701"],
      "strategy": "D",
      "hypothesis": "event_shock",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "available",
      "data_feasibility_reason": "快照 §2 全字段、SC 护栏结算周涨、D8、ATR 分层实测; MA2701 逐日结算缺为 #30 子项",
      "signal": "unknown",
      "signal_basis": "策略 D 触发=事件落地+落地次日方向确认+微观同向; 本周三事件已落地但方向确认与微观验证未定义为具体计划 → unknown",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_indicators"],
          "details": "76 td ≥ 20 + D 池持仓上限 30 日 (≥50 td)"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_indicators"],
          "details": "540,023 手"
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["czce_margin_notice_0917", "snap_events_0919", "snap_ma2701_indicators"],
          "details": "0.1 低敞口判定继续命中: 高密度簇 (9/21、9/29 提保扩板节点, 9/30 俄禁令到期, 10/1-10/8 长假含 10/4 OPEC+, 10/27-28 FOMC; 两周内 ≥2 离散催化且当周有未落地节点) + 交易所公告 ±1 日 + D12 高波层 (ATR250 分位 82.9); 限隔夜池方向性单边新开 → 否决; 结构表达不受本项"
        },
        {
          "rule_id": "MA_oil_guard",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_sc_weekly"],
          "details": "SC2611 结算周涨 -0.30% (9/11→9/18, 两端 settle) 未命中 >5%/>8%; 上一读数 +22.56% 的 '冻结·清仓' 处置到期 (条件式) 不续延; 本项通过不解除 #16"
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_d8_ma"],
          "details": "主力 MA2610 周涨 +0.93%, 上尾位 66.7 < 80 → 商品多头无扣分档 (9/16 快照 80.4 扣分档已解除)"
        },
        {
          "rule_id": "#20",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_indicators", "snap_d8_ma"],
          "details": "dist_H250 5.61% 非创新高; 周涨上尾 66.7 非前 10% → 未命中"
        },
        {
          "rule_id": "#30",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["ma2701_daily_settle"],
          "details": "MA2701 结算价对 pre_settle 逐日涨跌 (9/14-9/18) 未取得; 周涨 -2.90% 不能推断单日; 主力 MA2610 9/16 +4% 与 SC 信号腿 9/14 +11% 均不替代判定腿",
          "diagnostic_evidence_refs": ["ma_main_intraday_0916", "sc_daily_0914_0918"],
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "在有 Tushare 环境重跑 scripts/future_data.py v1.16 (§2b.1 新增 日结算涨跌%/近5日结算涨跌%/#30近3日≥5% 列) 或用户终端导出 MA2701 逐日 settle/pre_settle (9/14-9/18 及后续), 核 ≥5% 命中与冷却期",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_indicators", "snap_atr_gap"],
          "details": "已触发 (ATR250 分位 82.9 > 80 → 高波层; HV20/HV60 1.22 < 1.3): 方向性单边 ×0.5 + 门槛 +0.3 + SL 用重校准 ATR + gap 收紧一档 + 隔夜须过 #25; 池内极差 77.4 错位 → 逐品种独立核参; 非否决 (pass=已评估并适用处置)"
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_notice_0917"],
          "details": "9/21 起 MA2610/2611 分级、9/29 起甲醇全合约保证金 10%/涨跌停 9% → ×0.8 缓冲 (2.3), 公告 ±1 日 (9/18-9/22, 9/28-9/30) 新开门槛 +0.3; 非否决"
        },
        {
          "rule_id": "#25",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "当日 ATR 重校准核验仅对隔夜持仓适用; 账户未知且无已核持仓 → 本次不适用 (若开仓则须过)"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无具体事件对象/落地次日确认条件/Entry/SL/TP/期限; 本周登记影子计划 SP-2026-09-19-MA2701-long-D (突破 3155/SL 3018/TP 3429) 仅为规则复评假设",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "策略 D 计划须指定事件对象 (下一可排期=10/4 OPEC+ 闭市期/10/9 复盘, 10/27-28 FOMC) 与落地次日确认条件; #16 解除前不出计划",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无当期经核实账户与挂单快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["#1", "#2", "#16", "MA_oil_guard", "D8", "#20", "#30", "D12", "exchange_notice", "#25", "execution_plan", "account"],
      "all_blockers": ["#16"],
      "unknown_checks": ["#30", "execution_plan", "account"],
      "first_blocker": "#16",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 事件冲击池",
        "result": null,
        "defaulted_dimensions": ["D9=3 default_neutral"],
        "notes": "D12 扣 -0.3 适用; D8 0; D11 dist 5.61% → 0; 事件对象未指定 → D1/D2/D3/D5 null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": ["snap_ma2701_indicators", "snap_sc_weekly", "snap_d8_ma", "czce_margin_notice_0917"]
    },
    {
      "candidate_id": "2026-09-18|MA2701|directional|short|v2.26",
      "opportunity_id": "MA_short_2701",
      "trade_date": "2026-09-18",
      "contracts": ["MA2701"],
      "strategy": "D",
      "hypothesis": "event_shock",
      "evidence_basis": "geopolitical_fade",
      "direction": "short",
      "data_feasibility": "available",
      "data_feasibility_reason": "快照 §2 全字段与 ① 量化锚 (SC 近端 back) 实测; 方向性空头受 #26 规则许可限制, 非数据不可得",
      "signal": "unknown",
      "signal_basis": "能源链方向性空头在 ① 未证缓和期间无许可路由; 触发条件未定义 → unknown",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_indicators"],
          "details": "76 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_indicators"],
          "details": "540,023 手"
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["czce_margin_notice_0917", "snap_events_0919", "snap_ma2701_indicators"],
          "details": "同多头: 低敞口判定命中, 限隔夜池方向性单边新开否决"
        },
        {
          "rule_id": "#26",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["salalah_postponed_0913", "snap_sc_pair", "us_iran_tanker_strikes_0908_0909"],
          "details": "① 未证缓和 (反向要件 '官方停火/重开 + back 回落' 未出现: 萨拉拉会推迟无新日期; SC 近端 back +43.5/分位 100 仍在反弹侧); 本周 change-analysis 按 v2.26 新要件改判 '中断证真' (再袭船 9/8-9/9 多源✓ + back 反弹); 护航/管道修复非官方重开; 能源链方向性空头新开否决; fade 仅限结构且 research_only",
          "diagnostic_evidence_refs": ["irgc_tanker_trend_0917", "centcom_convoy_0917", "saudi_pipeline_0910_0918"]
        },
        {
          "rule_id": "#30",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["ma2701_daily_settle"],
          "details": "MA2701 逐日结算涨跌未取得 (若 9/17-9/18 有 ≤-5% 日则空向 3 日冷却); SC 信号腿 9/17 -6%/9/18 -9% 不替代",
          "diagnostic_evidence_refs": ["sc_daily_0914_0918"],
          "gap": {
            "kind": "raw_data",
            "owner": "data_pipeline",
            "next_action": "同多头记录: 重跑 v1.16 §2b.1 或终端导出 MA2701 逐日 settle/pre_settle",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_ma2701_indicators"],
          "details": "已触发 (高波层 82.9), 双向对称处置; 非否决"
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_notice_0917"],
          "details": "同多头"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无许可路由下不出计划",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "#26 解除 (① 缓和证真: 官方解除/重开 + back 回落) 前不出计划; 仅记录",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无当期经核实账户与挂单快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["#1", "#2", "#16", "#26", "#30", "D12", "exchange_notice", "execution_plan", "account"],
      "all_blockers": ["#16", "#26"],
      "unknown_checks": ["#30", "execution_plan", "account"],
      "first_blocker": "#16",
      "only_blocker": false,
      "score": {
        "canonical_ref": "3.1 事件冲击池",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "规则许可阻断, 不评分"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": ["snap_ma2701_indicators", "snap_sc_pair", "salalah_postponed_0913"]
    },
    {
      "candidate_id": "2026-09-18|M2701|unknown|unknown|v2.26",
      "opportunity_id": "M_observe_2701",
      "trade_date": "2026-09-18",
      "contracts": ["M2701"],
      "strategy": "unknown",
      "hypothesis": "unknown",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "无已许可具体策略/路由 (仅观察, 不自动进 C 池); 行情可得 (快照 §2: settle 3429, ATR250 分位 99.4 高波层) 但无许可路由 → 按协议 research_only",
      "signal": "unknown",
      "signal_basis": null,
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "licensed_route",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "升核心条件=已有许可路由 + 独立公开供需证据 (USDA/作物进度/国内供需) + 行情确认; 本周无新供需读数 (到港/库存为 9/1 口径 stale)",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "仅当出现独立公开供需证据且提出具体许可路由时再评估; 否则维持观察",
            "due_at": "next_report"
          }
        }
      ],
      "evaluation_order": ["licensed_route"],
      "all_blockers": [],
      "unknown_checks": ["licensed_route"],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": null,
        "result": null,
        "defaulted_dimensions": [],
        "notes": "无许可路由, 不评分"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
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
    },
    {
      "candidate_id": "2026-09-18|SR2701-SR2705|A|unknown|v2.26",
      "opportunity_id": "SR_A_2701_2705",
      "trade_date": "2026-09-18",
      "contracts": ["SR2701", "SR2705"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "available",
      "data_feasibility_reason": "快照实测分位/样本 complete",
      "signal": "not_triggered",
      "signal_basis": "近3年同期分位 0.0 < 70 (快照 §1 直接证据)",
      "signal_evidence_refs": ["snap_sr_pair"],
      "screening_evidence": "snap_sr_pair",
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_sr_pair"],
          "details": "SR2701 76 td / SR2705 155 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_sr_pair"],
          "details": "470,759 / 40,611 手"
        }
      ],
      "evaluation_order": ["#1", "#2"],
      "all_blockers": [],
      "unknown_checks": [],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "未触发, 不评分 (低分位对称策略本次未新增)"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": ["独立产业证据", "confirmation_definition", "#5", "execution_plan", "account"],
      "evidence_refs": ["snap_sr_pair"]
    },
    {
      "candidate_id": "2026-09-18|SR2701|B|long|v2.26",
      "opportunity_id": "SR_B_summer_2026",
      "trade_date": "2026-09-18",
      "contracts": ["SR2701"],
      "strategy": "B",
      "hypothesis": "seasonal_long",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "available",
      "data_feasibility_reason": "产销率/工业库存/原糖/期价公开可得; B-HISTORY 为 calculation 缺口非数据不可得",
      "signal": "unknown",
      "signal_basis": "B 窗口筛选 pass 不是完整开仓信号; Entry 条件 (Step5-B) 未组装 → unknown",
      "screening_evidence": "b_window_calendar",
      "evaluated_checks": [
        {
          "rule_id": "B_window_screen",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["b_window_calendar"],
          "details": "SR-summer 07-01–09-30: 2026-09-18 ≤ window_end → 研究窗口内 (日期筛选)"
        },
        {
          "rule_id": "card_veto",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["sugar_sales_aug"],
          "details": "品种卡专属否决: 榨季初期多头需产销率验证 — 广西截至 8 月产销率 80.56% (同比 -8.48pp)、工业库存同比 +78.74 万吨 → 验证反向 (9 月数据未发布, 最近可得)"
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["sugar_sales_aug"],
          "details": "(b) 独立产业事实已核反证 (同上); (a) B Entry 条件未组装 = unknown 子项; ICE 原糖较 9/10 高位回落 7% 为外盘背景 (diagnostic)",
          "diagnostic_evidence_refs": ["sugar_prices_0918"]
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_d8_sr"],
          "details": "B 做多看上尾: 5.9 → 无扣减 (下尾 94.1 空头否决档不适用于做多)"
        },
        {
          "rule_id": "B_plan_horizon",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["b_window_calendar"],
          "details": "planned_exit=window_end 前第 5 个交易日 ≈ 2026-09-23 (人工推算); 剩余持有区间 ≤2 个交易日, 5-20 日计划期限大概率不可行; 真实交易日映射待 seasonal_plan.py",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "运行 scripts/seasonal_plan.py 映射 SR-summer planned_exit 真实交易日并判期限可行性; 不可行则本窗口结案 (no_signal 转 blocked 由完整检查决定)",
            "due_at": "2026-09-23"
          }
        },
        {
          "rule_id": "B_trigger",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Entry_raw=max(MA20, pre_window_low5+ATR20) 与 B-HISTORY 三年同窗 (SR2601/2501/2401) 未组装; rule_version=B-v2.24 未登记 defined_at/effective_from",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "按 scripts/SEASONAL_PLAN_INPUT.md 组装输入并运行 seasonal_plan.py (即使本窗口到期, 也为 2027 窗口建立流程)",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无 Entry/SL/TP1/期限/成本",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "card_veto 与 #5 已核 fail, 本窗口不出计划; 记录结案理由",
            "due_at": "2026-09-23"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无当期经核实账户与挂单快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["B_window_screen", "card_veto", "#5", "D8", "B_plan_horizon", "B_trigger", "execution_plan", "account"],
      "all_blockers": ["card_veto", "#5"],
      "unknown_checks": ["B_plan_horizon", "B_trigger", "execution_plan", "account"],
      "first_blocker": "card_veto",
      "only_blocker": false,
      "score": {
        "canonical_ref": "3.1 季节性池",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "D2'=1 (产销率反证); Entry 未组装 → D1/D3 null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": "B-v2.24",
          "defined_at": null,
          "effective_from": null,
          "price_basis": "元/吨 settle (Step5-B)",
          "economic_rationale": "夏季消费与节前备货 (1.6 B-WINDOW); 本窗口尾段且产销率验证反向",
          "observed_values": "SR2701 settle 5326 (9/18); 周涨 -2.22%; ATR20 53.31; MA20 5399.8"
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": ["b_window_calendar", "sugar_sales_aug", "snap_d8_sr"]
    },
    {
      "candidate_id": "2026-09-18|CF2701|B|long|v2.26",
      "opportunity_id": "CF_B_autumn_2026",
      "trade_date": "2026-09-18",
      "contracts": ["CF2701"],
      "strategy": "B",
      "hypothesis": "seasonal_long",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "available",
      "data_feasibility_reason": "轮出/新棉/期价公开可得; B-HISTORY 与 pre_window_low5 为 calculation 缺口",
      "signal": "unknown",
      "signal_basis": "B 窗口筛选 pass 不是完整开仓信号; Entry 条件未组装 → unknown",
      "screening_evidence": "b_window_calendar",
      "evaluated_checks": [
        {
          "rule_id": "B_window_screen",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["b_window_calendar"],
          "details": "CF-autumn 09-01–10-31: 2026-09-18 在窗内; 新开区间 window_start ≤ 执行日 < planned_exit (10/31 前第 5 个交易日)"
        },
        {
          "rule_id": "card_veto",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": ["cotton_reserve_0918"],
          "details": "品种卡 '国储轮储公告日 ±3 天暂停' 对逐日滚动轮出周的适用性未定义 (轮出为持续日度挂牌, 非单次公告)",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "明确 ±3 天条款以 '轮出启动/结束/规则变更公告日' 为锚还是逐日挂牌日为锚; 未定义前不据此否决也不据此放行",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["cotton_reserve_0918"],
          "details": "(b) 独立产业事实已核反证 (供给端): 储备棉 9/18 成交率 96.37% (本轮首见 <100%)、累计成交 358,199 吨持续供给; 新棉上市提速与籽棉开秤预期下移 (diagnostic) 同向; 无独立需求侧支持做多; (a) Entry 条件未组装 = unknown 子项",
          "diagnostic_evidence_refs": ["cotton_seed_price_0918"]
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["snap_d8_cf"],
          "details": "B 做多看上尾: 2.0 → 无扣减 (下尾 98.0 空头否决档不适用于做多)"
        },
        {
          "rule_id": "B_trigger",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Entry_raw=max(MA20 16672, pre_window_low5 + ATR20 219.42): pre_window_low5 (8/25-8/31 五日最低 low) 未取得; B-HISTORY (CF2601/2501/2401 秋窗) 未组装; rule_version=B-v2.24 未登记",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "组装 SEASONAL_PLAN_INPUT.md 输入 (含 8/25-8/31 日线 low 与三年同窗结算) 并运行 scripts/seasonal_plan.py",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无 Entry/SL/TP1/期限/成本; #5 已核 fail 下不出计划",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "待独立需求侧证据出现且 B_trigger 计算完成后再拟计划; 否则窗口内每周只更新反证记录",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无当期经核实账户与挂单快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["B_window_screen", "card_veto", "#5", "D8", "B_trigger", "execution_plan", "account"],
      "all_blockers": ["#5"],
      "unknown_checks": ["card_veto", "B_trigger", "execution_plan", "account"],
      "first_blocker": "#5",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 季节性池",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "D2'=1 (供给端反证, 无需求侧支持); Entry 未组装 → D1/D3 null; ADX 30.1 (>25, 不再 ×0.7)"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": "B-v2.24",
          "defined_at": null,
          "effective_from": null,
          "price_basis": "元/吨 settle (Step5-B)",
          "economic_rationale": "秋季订单与新棉供给净影响 (1.6 B-WINDOW); 当前供给端反证",
          "observed_values": "CF2701 settle 15795 (9/18); 周涨 -3.98%; ATR20 219.42; MA20 16672; H20 17345 / L20 15715"
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": ["b_window_calendar", "cotton_reserve_0918", "snap_d8_cf"]
    }
  ],
  "unresolved_items": [
    {
      "item": "MA 国内路线论证与确认定义冻结: 用已观测的港口库存/到港/装置开工数值论证 '海峡未缓和时仍支持收敛的独立国内变化'; 复核 draft A-MA-2701-2705-draft1 后冻结或说明不能冻结的原因; 不能成案则明确结案",
      "owner": "研究方",
      "due_at": "2026-09-25",
      "required_evidence": ["ma_port_inventory_qual", "ma_plant_restart_fwd_0911"],
      "resolution": "pending"
    },
    {
      "item": "补核 MA2701 逐日 settle/pre_settle (9/14-9/18 及后续; #30 判定腿) 与 SC 逐日结算 (护栏两端); 脚本 v1.16 §2b.1 已增列 (拟议, 未实测), 在有 Tushare 环境重跑或用户终端导出",
      "owner": "data_pipeline / 研究方",
      "due_at": "2026-09-25",
      "required_evidence": ["ma2701_daily_settle"],
      "resolution": "pending"
    },
    {
      "item": "补核甲醇港口/华东社会库存同口径周度数值与国内装置复产进度; Mysteel 五大品种同口径钢材总库存 (各最多两个公开入口; 本周均阴性)",
      "owner": "研究方",
      "due_at": "2026-09-25",
      "required_evidence": ["ma_port_inventory_qual", "steel_inventory_mysteel_thisweek"],
      "resolution": "pending; 到期仍缺 → 下周诊断继续 temporary_gap 子项, 不转 research_only"
    },
    {
      "item": "运行 scripts/seasonal_plan.py: SR-summer planned_exit 真实交易日映射与期限可行性 (≈9/23); CF-autumn pre_window_low5 (8/25-8/31)、B-HISTORY 三年同窗、Entry/SL/TP1 与净 R; 登记 rule_version=B-v2.24 的 defined_at/effective_from",
      "owner": "研究方 (计算由 data_pipeline 执行)",
      "due_at": "2026-09-23",
      "required_evidence": ["b_window_calendar"],
      "resolution": "pending"
    },
    {
      "item": "核对郑商所 9/21 起 PTA/甲醇/PX 单独通知原文与 INE 对 SC 的公告 (阴性结论待原文); 9/21、9/29 公告 ±1 日门槛 +0.3 与 ×0.8 缓冲进入适用; 9/30 长假 T-1 处置",
      "owner": "研究方",
      "due_at": "2026-09-21",
      "required_evidence": ["czce_margin_notice_0917"],
      "resolution": "pending"
    },
    {
      "item": "① '中断证真' 改判后的反向监测: IRGC 9/17 再袭油轮多源确认; SC 近端 back 方向 (脚本 §1, 基准 9/18 +43.5/分位 100); 官方停火/重开或伊朗许可-收费机制正式落地; 沙特东西管道全量恢复; 俄柴油禁令 9/30 前官方公告",
      "owner": "下周 change-analysis",
      "due_at": "2026-09-26",
      "required_evidence": ["snap_sc_pair", "irgc_tanker_trend_0917", "russia_diesel_ban_report_0916"],
      "resolution": "pending"
    },
    {
      "item": "影子计划 SP-2026-09-19-MA-A-short-spread 与 SP-2026-09-19-MA2701-long-D 由脚本 §5 在下次快照结算 (首个可用日线 2026-09-22); 结算结果只用于复评 #5 / #16、D12, 不作交易依据",
      "owner": "data_pipeline (脚本 §5)",
      "due_at": "next_report",
      "required_evidence": ["snap_shadow_ledger"],
      "resolution": "pending"
    },
    {
      "item": "仅在执行核验阶段提供当期账户、持仓、挂单及实际费用/保证金 (带时区时间戳)",
      "owner": "账户持有人",
      "due_at": null,
      "required_evidence": [],
      "resolution": "pending"
    }
  ],
  "shadow_plans": [
    {
      "shadow_id": "SP-2026-09-19-MA-A-short-spread",
      "candidate_id": "2026-09-18|MA2701-MA2705|A|short_spread|v2.26",
      "registered_at": "2026-09-19T20:00:00+08:00",
      "instrument": {"type": "spread", "contracts": ["MA2701", "MA2705"]},
      "side": "short",
      "entry_type": "limit",
      "entry": 312,
      "stop": 380,
      "target": 120,
      "entry_expiry": "2026-09-25",
      "latest_exit_date": "2026-10-23",
      "multiplier": 10,
      "round_trip_cost": 48,
      "blockers_at_registration": ["#5"],
      "rationale": "规则复评假设 (非交易信号): 做空价差 +312 (9/18 两腿 settle 之差); SL +380=100 分位基础上再走阔约 22%、超过 9/16-9/17 峰值区 (+309/+330), 近月挤仓延续=国内回归假设失效; TP +120≈本对全生命周期 50 分位附近的部分回归 (国内装置 9 月中下旬复产 + 国庆前后到港 + 9/21、9/29 提保扩板压缩近月投机溢价); 净 R=(312-120)×10-48 ÷ (380-312)×10+48 ≈ 2.57; 最晚退出 10/23 在近腿触 #1 (≈12/17) 前且覆盖 5-20 交易日"
    },
    {
      "shadow_id": "SP-2026-09-19-MA2701-long-D",
      "candidate_id": "2026-09-18|MA2701|directional|long|v2.26",
      "registered_at": "2026-09-19T20:00:00+08:00",
      "instrument": {"type": "single", "contracts": ["MA2701"]},
      "side": "long",
      "entry_type": "stop",
      "entry": 3155,
      "stop": 3018,
      "target": 3429,
      "entry_expiry": "2026-09-25",
      "latest_exit_date": "2026-10-23",
      "multiplier": 10,
      "round_trip_cost": 30,
      "blockers_at_registration": ["#16", "D12(高波层, 非否决)"],
      "rationale": "规则复评假设 (非交易信号): 突破 H20 3154 + 1 tick 的止损单入场; SL=Entry − 1.5×ATR20 (91.14) ≈ 3018 (策略 D 口径); TP=Entry + 2R = 3429; 用于复评 #16 低敞口否决与 D12 高波层处置在本周形态下的避免亏损/错过收益; 成本=单腿开平滑点 2×tick_value + 手续费约 10"
    }
  ],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "coke_round5_norecord_prior",
      "reason": "上周 (2026-09-12) '焦炭第五轮 9/5-9/11 无公开发起或落地记录' 为检索遗漏: 腾讯 9/10、21 经济 9/8 (多源) 记录第五轮 9/8 发起、9/10 主流钢厂全面落地 (湿熄 +100/干熄 +110); 按 4.4 审计纠错闭环保留 invalid 行并撤回, 以 coke_round5_landed_0910 替代; 属证据修复, 非市场反转",
      "affected_checks": [
        {
          "candidate_id": "2026-09-18|RB2701-RB2703|A|unknown|v2.26",
          "rule_id": "D14"
        }
      ],
      "recalculation": "completed",
      "recalculation_note": "D14 对独立国内月差不适用 (applicable=false), 撤回前后判定不变; 1.4 负反馈检验点由 'unknown' 重评为 '落地→负反馈临界' (同源记录钢厂亏损扩大、减产计划增多、第六轮观望), 不执行 '原料主线延续' 亦不执行 '负反馈启动'; RB 多头评估冻结不变; RB2701-RB2703 本周因分位 56.1 未触发, 纠错不产生新的 pass/fail"
    }
  ]
}
```

校验命令：`python3 scripts/validate_futures_audit.py --input research/2026-09-19-execution-audit.md`。实际结果见下方"校验记录"。结构校验不检查门覆盖、独立经济因果、确认规则有效性或实际交易许可。

## 校验记录

- 人工语义核对：#3 按模型拆分（MA 多头 D 路线不引用①全局未知；空头按 geopolitical_fade 核①→#26 fail）；#5 子项分列（产业反证 fail / 价格确认 unknown）；D1/D2/D5 分工按 3.1；事件窗口按 0.0b（FOMC T+1=9/18 已过、#29 与提前窗归档；下一簇 9/21、9/29、9/30、10/1-10/8、10/27-28）；#16 依 0.1 低敞口判定当期命中（高密度簇＋交易所公告＋D12 高波层）；账户 unknown 不推定空仓；no_signal 记录的 signal_evidence_refs 均为快照实测；影子计划登记日（周六）落在 as_of 当日，首个可结算日线 9/22；evidence_corrections 引用的 invalid 行未进入任何 pass/fail 依据。
- 校验器运行结果见下方代码块（由本次运行回填）。

```text
$ python3 scripts/validate_futures_audit.py --input research/2026-09-19-execution-audit.md
{"status": "valid", "scope": "structure_validation_only", "execution_permission": "not_evaluated", "errors": []}
退出码: 0 （2026-09-19 本次运行，现行 v2.26 / origin/main b6069b2）
```

```text
$ python3 scripts/validate_futures_audit.py --input research/2026-09-19-execution-audit.md   # 拟议版本 v2.27 / 脚本 v1.16 重评后再次运行（分支 futures-framework/2026-09-19）
{ "status": "valid", "scope": "structure_validation_only", "execution_permission": "not_evaluated", "errors": []}
退出码: 0 （2026-09-19 本次运行，拟议 v2.27 / v1.16）
```
