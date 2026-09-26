# 2026-09-26 期货执行诊断

**结论：截至 2026-09-26（最近已完成行情日 2026-09-24；本周国内期货仅 9/21-9/24 四个交易日，9/25-9/27 中秋休市），已核研究范围内未形成可执行方案，仍有研究/账户核验缺项；不能据此写"市场没有机会"或"市场建议空仓"。** 本诊断按现行 `framework/futures_framework.md` **v2.27**（origin/main `192b793`；方法/状态日期 2026-09-19，2026-09-20 治理整理）与 `FUTURES_DATA_PROTOCOL.md` v2.26 生成。**本周没有新的行情快照**：仓库最新快照仍为 `research/2026-09-19-data-snapshot.txt`（脚本 v1.15、最新行情日 2026-09-18），落后最近已完成交易日四个交易日→按 0D/协议记 **stale**：全部价差分位、1-5-10td 变化、同期样本验收、ATR 分层/极差、D8 周涨分位、SC2611 结算周涨（9/17→9/24）、MA2701 逐日结算涨跌（#30）、§5 影子结算均为 **temporary_gap/unknown**，不以媒体收盘涨跌推算、不沿用 9/18 读数作本周判定。公开信息来自 WebSearch 摘要（调研阶段只用 WebSearch；多源同口径官方数据 verified，单源/冲突项分别标注；三条跨年/往年命中已标 invalid）。实际账户与挂单快照未提供（`actual_position_status=unknown`），全部 `final_lots=null`，总体机会数 `null`。

| 已观察记录 | 本次状态 | 已核否决 / 缺口 |
|---|---|---|
| MA2701−MA2705，A reversion（做空价差，domestic_public） | incomplete | **国内路线论证结案（fail）**：本周可得的国内独立事实（太仓现货 4,090、西北 3,400 近历史高、检修装置复产偏慢、伊朗供应低位→到港低）全部指向近月强，"即使海峡未缓和仍支持收敛的独立国内变化"未被观测到→按协议不能改名为 domestic_public 放行；**#5(b) 已核反证维持 fail**；确认定义 **draft1→v1 冻结**（effective_from 2026-09-28，只作前瞻）；研究筛选/#2/#13 无本周快照→unknown；港口库存数值第三周缺（改为增强级第二指标，不再阻断）；计划未形成；账户未核；9/29 起 MA 保证金 10%/涨跌停 9% |
| MA2705−MA2709，A（准备对） | incomplete | temporary_gap：无快照；上一快照样本 24/21/22<33、MA2709 量缺失 |
| RB2701−RB2703，A（黑色唯一结构表达） | incomplete | temporary_gap：无快照（上一实测 56.1 未触发不能沿用为本周判定）；独立证据已备：Mysteel 同口径总库存 1,481.97（-55.76）、中钢协旬度 -2.8%（上周缺数子项解除）；钢厂第一轮提降准备=负反馈启动候选（背景）；9/23 起 RB 涨跌停 7%/保证金 9% |
| RB2703−RB2705，A（准备对） | incomplete | temporary_gap：无快照；RB2705 上一实测 13,672 临界过 #2 |
| MA2701，方向性多头（D 事件冲击） | incomplete | **#16 已核失败**（0.1 低敞口判定继续命中：高密度簇 9/28 周末 headline 首个交易日→9/29 第二阶段提保→9/30 俄禁令/PMI/长假 T-1→10/1-10/7 闭市含 10/4 OPEC+→10/8 复盘→10/27-28 FOMC；交易所公告 ±1 日（9/28-9/30 全在 9/29 ±1 内）；D12 高波层为上一实测）；周涨护栏/D8/#20/#30/D12 分层无快照→unknown（SC2611 9/24 收盘 +5.02% 仅记录，非结算）；计划/账户未核 |
| MA2701，方向性空头 | incomplete | **#16、#26 已核失败**（①"中断证真"维持：9/21 两船遇袭多源=要件一再命中；伊朗七日方案 9/25 被美方 9/26 拒绝＋"经济 D 日"→反向要件（官方停火/重开或许可-收费机制落地）未出现；要件二 back 方向无快照 unknown）；#30/D8/D12 unknown；计划/账户未核 |
| M2701，独立备选 | incomplete（research_only） | 无已许可具体策略（仅观察）；豆粕库存 117.32（9/18）供应宽松；9/29 起 8%/10%；10/9 WASDE 国内 10/12 响应 |
| SR2701−SR2705，A 远月 | incomplete | temporary_gap：无快照（上一实测 0.0）；9/29 起 SR 8%/7% |
| SR2701，B 季节做多 | **no_signal** | B-WINDOW SR-summer planned_exit=**2026-09-22**（window_end 9/30 前第 5 个交易日，按真实交易日历 9/29、9/28、9/24、9/23、9/22 重算；上周人工推算 9/23 未计 9/25 休市）已过→"新开须 window_start≤执行交易日<planned_exit"不满足→本窗口结案（直接日历证据）；品种卡产销率否决等后续门不再评估并明示 |
| CF2701，B 季节做多 | incomplete | B-WINDOW CF-autumn 在窗（planned_exit=10/23）；**#5 已核失败**（(b) 供给端反证：储备棉第九周成交率 93.1%、9/20 99.51%、吐絮率近 70%、新棉零星开秤、内外棉价承压——无独立需求侧支持）；轮储公告 ±3 天条款适用性未定义；B 触发（MA20/ATR20/pre_window_low5/B-HISTORY）无快照且未组装；9/29 起 CF 9%/8% |

信号席（不进候选 schema）：AU2612——美国 9 月闪值 PMI 58.4、Barr"还需加息"、10 月 FOMC 加息概率 73%→71%、12 月 95%、10Y 5.23%（2007 年来最高）、DXY 101.4；现货金 9/24 触 4,244（跌破决议后低点约 4,270）、9/25 4,280-4,310、周 -1%~-2%以上；黄金 T+D 926.5 元/克（截至 9/24 当周 -2.12%）→ fed_state 输入="加息落地·连续加息定价加深"，AU 卡"预期兑现型反弹评估"证伪→回吐段；9/23 起 AU 涨跌停 16%/保证金 18%；不建仓。SC2611-SC2612——无快照（①要件二 back 方向 unknown，上一实测 9/18 +43.5/分位 100）；SC2611 逐日（媒体收盘）9/22 夜 -2.3%、9/23 -4%、**9/24 收 730 元/桶（+5.02%）**=能源链单日 ≥5% 记录一次（多向，非结算）；SC2611 结算周涨 9/17→9/24 unknown；9/23 起 SC2611 涨跌停 18%/保证金 20%；剩余 19 td（注 c 不受 #1）。

**上期预备观察项处置（诊断口径）**：④"MA 国内路线论证与确认定义冻结（9/25 前）"——论证按可得证据**结案为未成案**（复活条件见 unresolved_items），确认定义冻结为 v1（前瞻）；港口库存数值连续第三周两入口阴性→按协议 6 复评可得性：MA 国内月差的独立产业证据改以"装置公告/现货基差"这一协议已列公开来源承担，港口库存数值降为增强级第二指标，不再计入必要缺项、不转 research_only；"#30 逐日结算/SC 逐日结算"因无快照继续 pending（脚本 v1.16 §2b.1 已在 main，待用户本机运行）；"seasonal_plan.py"未运行→SR-summer 按日历直接结案、CF-autumn 继续 calculation 缺口；"PTA/甲醇/PX 单独通知"经原文清单核对为同一通知第一阶段（结案）、INE 已于 9/21 发布 SC 公告（"阴性"结论更新）；影子计划 SP-2026-09-19-*（有效期 9/25，实际最后可入场日 9/24）因脚本 §5 未运行→结算 pending，本周登记不改写。

**日历纠错（EVIDENCE_CORRECTIONS）**：canonical v2.27 的"10/1-10/8 长假、10/9 复盘/首个响应日、低敞口条款 10/9 复评"与交易所 9/21 通知不符——实际 10/1-10/7 休市、**10/8（周四）集合竞价恢复交易并恢复夜盘**；中秋 9/25-9/27 休市未入日历；9/24 与 9/30 无夜盘。受影响：#16 的事件簇日期、D 池"落地次日确认"日、OPEC+ 10/4 首个响应日、上周 unresolved_items 的 9/25 截止日。纠错后 #16 判定不变（簇仍高密度）。

旧输出失效项：上周诊断的 no_signal 直接证据（RB2701-RB2703 分位 56.1、RB2703-RB2705 61.8、SR2701-SR2705 0.0）随快照过期失效——本周对应记录回到 incomplete/temporary_gap，不是"重新触发"；上周 MA 卡"D8 66.7 无档""SC 结算周涨 -0.30% 未命中""ATR 分位 82.9/极差 77.4"读数过期，本周全部 unknown；上周 SR B"planned_exit≈9/23"改 9/22；上周"INE 阴性""PTA/甲醇/PX 单独通知未核"结案；上周 MA 确认定义 draft1（含已退出的 MA2610 腿）由 v1 替换。

风险容量只引用 canonical Step5 与 `scripts/futures_risk.py`；配置=单笔上限 5,250、常规组合上限 5,250、当前低敞口组合上限 5,000（高密度簇＋交易所公告 ±1＋D12 高波层（上一实测）条款命中）；实际净值、存量风险、挂单预留、保证金未核验，未对任何候选运行真实容量计算。现有材料没有完整历史候选账，不能判断连续空仓与机会成本，也不能把本周结果归因于 5,000 元上限。

**影子计划**：本周**未新登记**——最接近成立的两条候选（MA A 做空价差、MA2701 突破多）均缺 9/24 两腿/单腿结算价（无快照），按 4.4 不以媒体收盘价登记；上周登记的 SP-2026-09-19-MA-A-short-spread / SP-2026-09-19-MA2701-long-D 继续由脚本 §5 在下次快照结算（登记不改写）。缺件写入 `unresolved_items`。

## 结构化记录（schema 3）

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-09-26",
  "research_mode": "public_data",
  "assessment_scope": "current_framework",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v2.27",
    "revision": "origin/main 192b793 (2026-09-20 治理整理; 方法/状态日期 2026-09-19)",
    "data_script_version": "v1.16 (main; §2b.1 判定腿逐日结算涨跌列已实现, 本周未运行). 本周无新快照; 最新快照 research/2026-09-19-data-snapshot.txt (v1.15, 最新行情日 2026-09-18) 为 stale, 仅作对照/diagnostic",
    "rule_changes_affecting_candidates": "v2.27 相对上周诊断所用 v2.26: 规则本体零改动 (①改判中断证真、D13 加息落地重写、交易所风控收紧为状态层). 本周判定差异全部来自证据状态: (1) 无快照→分位/样本/ATR/D8/周涨/#30/影子结算 unknown, 上周 no_signal 记录回到 incomplete; (2) 日历纠错 (10/8 恢复交易而非 10/9; 9/25-9/27 休市) → SR-summer planned_exit 9/22 已过 → no_signal (直接日历证据); (3) 交易所风控扩至全池 (INE/SHFE 9/23, DCE/CZCE 9/29); (4) MA 国内路线论证按可得证据结案为未成案 (fail), 确认定义冻结 v1 (前瞻); (5) 港口库存数值按协议 6 降为增强级第二指标"
  },
  "snapshot": {
    "market_trade_date": "2026-09-24",
    "market_captured_at": null,
    "source_artifacts": [
      "research/2026-09-26-market-research.md (WebSearch 摘要转引, 2026-09-26)",
      "research/2026-09-19-data-snapshot.txt (stale: 脚本 v1.15, 最新行情日 2026-09-18; 落后 4 个交易日; 仅作对照)",
      "交易所 2026-09-17/18/21 通知 (郑商所/大商所/上期所/上期能源; 多源转引)",
      "framework/futures_framework.md v2.27 / framework/FUTURES_DATA_PROTOCOL.md v2.26 / projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md",
      "scripts/seasonal_plan.py 未运行 (CF B-HISTORY 输入未组装; SR-summer 由日历直接结案); scripts/futures_risk.py 未运行 (无完整计划与账户); scripts/future_data.py v1.16 本周未运行 (需用户本机 Tushare)"
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
      "source": "canonical 0)/Step5; 低敞口=高密度簇 (9/28 headline 首个交易日/9/29 提保/9/30 俄禁令·PMI·T-1/10/1-10/7 闭市含 10/4 OPEC+/10/8 复盘/10/27-28 FOMC) + 交易所公告±1日 (9/28-9/30) + D12 高波层 (上一实测 82.9, 本周无刷新) 条款命中; 实际净值/占用未核"
    },
    "invalidated_legacy_outputs": [
      "上周 (2026-09-19) 诊断的 no_signal 直接证据 (RB2701-RB2703 56.1 / RB2703-RB2705 61.8 / SR2701-SR2705 0.0) 与 MA 卡读数 (D8 66.7 无档、SC 结算周涨 -0.30%、ATR 分位 82.9、极差 77.4、剩余 td) 随快照过期失效; 本周对应项 unknown/temporary_gap, 不是重新触发",
      "canonical v2.27 日历 '10/1-10/8 长假、10/9 复盘/首个响应日、低敞口 10/9 复评' 由交易所 9/21 通知纠正为 10/1-10/7 休市、10/8 恢复交易; 中秋 9/25-9/27 休市补入; 上周 unresolved_items 的 9/25 截止日实为休市日",
      "上周 SR B 'planned_exit≈9/23' 改为 9/22 (真实交易日历); 本窗口结案",
      "上周 '#30 判定腿逐日结算 next_action=重跑 v1.16': v1.16 已在 main, 本周仍未运行 → 缺口性质由 calculation 转为 raw_data (需用户本机 Tushare 运行)",
      "上周 'INE 对 SC 公告阴性' 与 '9/21 起 PTA/甲醇/PX 单独通知未核' 结案: INE 9/21 已发布 (9/23 起 SC 16-18%/18-20%); 单独通知即郑商所主通知第一阶段",
      "上周 MA 确认定义 draft1 (含已退出的 MA2610 腿条款) 由 A-MA-2701-2705-v1 (frozen, effective_from 2026-09-28) 替换; draft1 不回判",
      "上周影子计划 entry_expiry 2026-09-25 为休市日, 实际最后可入场日 9/24; 登记不改写, 由脚本 §5 机械处理"
    ]
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "MA2701-MA2705 A reversion domestic_public: #1/国内路线论证(结案 fail)/确认定义(v1 冻结)/#5/交易所公告; 研究筛选/#2/#13 因无快照 unknown",
      "MA2705-MA2709 A 准备对: 缺口登记 (无快照)",
      "RB2701-RB2703 与 RB2703-RB2705 A: 研究筛选 unknown (无快照); 独立产业证据 (Mysteel 同口径) 已备",
      "MA2701 方向性多空: #1/#16/#26/交易所公告已核; 周涨护栏/D8/#20/#30/D12 无快照 unknown",
      "SR2701-SR2705 A: 研究筛选 unknown (无快照)",
      "SR2701 B: B-WINDOW 日历筛选 → planned_exit 9/22 已过 → no_signal",
      "CF2701 B: B-WINDOW 日历筛选 pass、#5 独立产业事实 fail、轮储条款/B 触发/D8 缺口",
      "M2701: research_only 登记 (无已许可策略)"
    ],
    "missing_scope": [
      "本周行情快照 (scripts/future_data.py v1.16, 需用户本机 TUSHARE_TOKEN): 分位/价差变化/样本验收/ATR 分层与极差/D8/SC2611 结算周涨 (9/17→9/24)/MA2701 逐日结算 (#30)/§5 影子结算",
      "实际账户/持仓/挂单/保证金/费用",
      "甲醇港口/华东社会库存同口径周度数值 (连续第三周两入口阴性; 已降为增强级第二指标)",
      "CF B 的 pre_window_low5 (8/25-8/31)、B-HISTORY 三年同窗、Entry/SL/TP1 (seasonal_plan.py 未运行; 且需快照 MA20/ATR20)",
      "SC 逐日结算 (护栏两端; 9/24 +5.02% 为收盘口径)",
      "国家统计局 9 月 PMI (9/30 发布, 未发布)"
    ],
    "research_only_scope": [
      "geopolitical_fade / 中断因果模型 (①中断证真维持; 七日方案被拒; 复活须按 v2.26 新要件重定义)",
      "M2701 无已许可具体策略 (仅观察)"
    ],
    "signal_observations": [
      "AU2612: PMI 58.4 / Barr '还需加息' / 10 月 FOMC 加息概率 73%→71%、12 月 95% / 10Y 5.23% (2007 年来最高) / DXY 101.4; 现货金 9/24 触 4,244 (跌破决议后低点约 4,270), 9/25 4,280-4,310, 周 -1%~-2%以上; 黄金 T+D 926.5 (截至 9/24 当周 -2.12%); fed_state 输入='加息落地·连续加息定价加深'; AU 卡 '预期兑现型反弹评估' 证伪→回吐段; 9/23 起 AU 涨跌停 16%/保证金 18%; 不建仓; 剩余 51 td (按日历推算)",
      "SC2611-SC2612: 无快照 → ①要件二 back 方向 unknown (上一实测 9/18 +43.5/分位 100, 10td +17.9); 媒体收盘: 9/22 夜 -2.3%、9/23 -4%、9/24 SC2611 收 730 元/桶 (+5.02%) = 能源链单日 ≥5% 记录一次 (多向; 非结算); SC2611 结算周涨 9/17→9/24 unknown; 9/23 起 SC2611 涨跌停 18%/保证金 20%; 剩余 19 td (注 c 不受 #1); 下次主力换月→SC2612-SC2701"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "cal_holiday_0921",
      "metric": "交易所 2026 年中秋节/国庆节休市与恢复安排",
      "value": "9/24 晚无夜盘; 9/25-9/27 休市; 9/28-9/30 开市; 9/30 晚无夜盘; 10/1-10/7 休市; 10/8 (周四) 08:55 集合竞价恢复交易、当晚恢复夜盘; 本周实际交易日 9/21-9/24",
      "unit": "日期",
      "observation_date": "2026-09-21",
      "published_at": "2026-09-21",
      "source_url_or_file": "https://www.shfe.com.cn/publicnotice/notice/202609/t20260921_833503.html; https://news.qq.com/rain/a/20260921A0BE7900; https://finance.sina.com.cn/roll/2026-09-22/doc-inissyqx6834436.shtml",
      "original_source": "上期所/上期能源/郑商所/大商所 2026-09-21 通知 (多源转引)",
      "price_basis": null,
      "comparison_basis": "canonical v2.27 1.4/0.0b 原写 10/1-10/8、10/9 复盘",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "td_calendar_0924",
      "metric": "池内合约剩余交易日 (9/24 口径)",
      "value": "MA2701 72 / MA2705 151 / MA2709 237 / RB2701 73 / RB2703 109 / RB2705 152 / M2701 73 / SR2701 72 / SR2705 151 / CF2701 72 / AU2612 51 / SC2611 19 / SC2612 40",
      "unit": "交易日",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-26",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1/§2b (9/18 口径) 减 9/21-9/24 四个真实交易日 (cal_holiday_0921)",
      "original_source": "scripts/future_data.py v1.15 trade_cal 剩余 td + 交易所日历 (确定性日历运算, 非行情推算)",
      "price_basis": null,
      "comparison_basis": "0.3#1 (≥20 td; 方向性单边 ≥20+持仓上限)",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "czce_margin_0917_full",
      "metric": "郑商所中秋/国庆提保扩板 (两阶段完整清单)",
      "value": "9/21 结算起: PTA/甲醇/PX 2610 涨跌停 9%, 2611 保证金 9%/涨跌停 8% (即上周所谓 '单独通知', 无额外条款); 9/29 结算起: PTA/甲醇/玻璃/苹果/纯碱/短纤/PX/烧碱/瓶片/丙烯 保证金 10%、涨跌停 9%; 棉花/菜油/菜粕/菜籽/硅铁/锰硅/红枣/尿素/花生 9%/8%; 白糖 8%/7%; 棉纱 7%/6%; 10/8 恢复交易后按条件回落",
      "unit": "%",
      "observation_date": "2026-09-17",
      "published_at": "2026-09-17",
      "source_url_or_file": "https://www.stcn.com/article/detail/4189549.html; https://k.sina.cn/article_6192937794_17120bb4202002ugnm.html; https://news.fx678.com/202609171937192465.shtml",
      "original_source": "郑商所 2026-09-17 通知 (多源转引)",
      "price_basis": null,
      "comparison_basis": "canonical 0.1 交易所风控行 (甲醇单品种)",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ine_sc_margin_0921",
      "metric": "上期能源中秋/国庆提保扩板 (原油)",
      "value": "9/23 结算起: 原油/低硫燃料油涨跌停 16%、套保保证金 17%、一般 18%; SC2610/SC2611 (及 LU2610/2611) 涨跌停 18%、套保 19%、一般 20%; 10/8 后自首个未出现单边市交易日结算起恢复",
      "unit": "%",
      "observation_date": "2026-09-21",
      "published_at": "2026-09-21",
      "source_url_or_file": "https://news.fx678.com/202609211743069087.shtml; https://k.sina.cn/article_5182171545_134e1a99902002jsz8.html; https://news.qq.com/rain/a/20260921A0BE7900",
      "original_source": "上海国际能源交易中心 2026-09-21 通知 (多源转引)",
      "price_basis": null,
      "comparison_basis": "上周 'INE 对 SC 公告未检索到 (阴性)'",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "shfe_margin_0921",
      "metric": "上期所中秋/国庆提保扩板 (螺纹钢/黄金)",
      "value": "9/23 结算起: 螺纹钢/热卷/不锈钢/纸浆/胶版纸涨跌停 7%、套保保证金 8%、一般 9%; 黄金/白银涨跌停 16%、套保 17%、一般 18%; 10/8 后条件恢复",
      "unit": "%",
      "observation_date": "2026-09-21",
      "published_at": "2026-09-21",
      "source_url_or_file": "https://www.shfe.com.cn/publicnotice/notice/202609/t20260921_833503.html; https://www.yicai.com/news/103372548.html",
      "original_source": "上海期货交易所 2026-09-21 通知",
      "price_basis": null,
      "comparison_basis": "上周仅郑商所甲醇",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "dce_margin_0918",
      "metric": "大商所中秋/国庆提保扩板 (豆粕等)",
      "value": "9/23 结算起 EG2610/2611 8%/10%、8%/9%; 9/29 结算起: 铁矿石/豆一/豆二/豆粕/豆油/鸡蛋/生猪/LLDPE/PP/PVC 涨跌停 8%、保证金 10%; 棕榈油/EG/纯苯/苯乙烯/LPG 9%/11%",
      "unit": "%",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-18",
      "source_url_or_file": "https://news.qq.com/rain/a/20260918A086NZ00; https://finance.sina.com.cn/money/future/2026-09-18/doc-inisftxc0308802.shtml",
      "original_source": "大连商品交易所 2026-09-18 通知 (多源转引)",
      "price_basis": null,
      "comparison_basis": "—",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "iran_7day_plan_rejected_0926",
      "metric": "①反向要件核对: 伊朗七日重开方案与美方回应",
      "value": "9/25 伊外长 Araghchi (联大): 条件满足则 7 日内重开海峡, 方案经卡塔尔转交美方, '选择权在美国'; 9/26 Trump: 'I rejected their deal', 宣布对伊 '经济 D 日' (Operation Economic Outcast; 财长称周三起关停所有伊朗航空公司), '不在任何谈判中'; 路透 9/24: 美伊代表在纽约探讨分阶段方案 (消息人士) → 官方停火/重开或许可-收费机制正式落地未出现",
      "unit": "事件",
      "observation_date": "2026-09-26",
      "published_at": "2026-09-26",
      "source_url_or_file": "https://edition.cnn.com/2026/09/25/middleeast/iran-unga-us-hormuz-intl; https://www.nbcnews.com/world/iran/iran-says-choice-reopening-hormuz-rests-united-states-offer-rcna599956; https://www.cbsnews.com/live-updates/us-iran-war-deal-strait-of-hormuz/; https://www.usnews.com/news/us/articles/2026-09-26/where-things-stand-after-irans-new-pitch-for-a-deal-to-open-the-strait-of-hormuz",
      "original_source": "伊朗外交部 (联大记者会) / 美国总统与财政部表态 (CNN/NBC/CBS/US News 多源转引)",
      "price_basis": null,
      "comparison_basis": "1.7① 反向质变要件 = 官方停火/重开或许可-收费机制正式落地 + SC 近端 back 回落",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "hormuz_tankers_hit_0921",
      "metric": "①要件一 '再袭船' 本周读数",
      "value": "9/21 英旗油轮 La Stephanie 进入海峡时遭不明射弹击中 (2 名船员受伤); 同日一艘 LPG 船遭不明射弹碎片击中 (无伤亡); 两船继续航行 (UKMTO); IMF PortWatch 9/20 通行 1 艘/日 (战前 85)",
      "unit": "事件",
      "observation_date": "2026-09-21",
      "published_at": "2026-09-21",
      "source_url_or_file": "https://www.france24.com/en/middle-east/20260921-projectile-hits-tanker-as-it-enters-the-strait-of-hormuz; https://gcaptain.com/two-more-tankers-hit-in-strait-of-hormuz-as-attacks-mount/; https://www.marineinsight.com/two-tankers-hit-by-unknown-projectiles-in-strait-of-hormuz-2-injured/",
      "original_source": "UKMTO (France24/gCaptain/MarineInsight 多源转引)",
      "price_basis": null,
      "comparison_basis": "上周 IRGC 9/17 再袭 Trend (单源)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "houthi_yanbu_0924",
      "metric": "绕行通道再袭 (胡塞导弹/无人机袭利雅得与延布)",
      "value": "沙特联军称拦截 6 枚弹道导弹 (目标塔伊夫与延布地区); 胡塞称袭击利雅得 '敏感目标' 与延布 Aramco 设施; 无损失/伤亡确认; 布油 9/24 结算 106.60 (+3.4%, 盘中 +5%)",
      "unit": "事件",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-24",
      "source_url_or_file": "https://www.aljazeera.com/news/2026/9/24/saudi-led-coalition-says-shot-down-6-ballistic-missiles-launched-by-houthis; https://www.bloomberg.com/news/articles/2026-09-24/saudi-arabia-intercepts-houthi-missiles-fired-at-cities; https://money.usnews.com/investing/news/articles/2026-09-24/oil-prices-jump-4-as-houthis-fire-missiles-at-saudi-arabia",
      "original_source": "沙特联军/胡塞声明 (半岛/彭博/路透多源转引)",
      "price_basis": null,
      "comparison_basis": "沙特东西管道 9/10-11 遇袭 (第三形态)",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "saudi_pipeline_restart_0922",
      "metric": "沙特东西管道复运状态",
      "value": "9/22 重启但低速运行, Aramco 力争回到 4 百万桶/日, 全量恢复需数周; 延布出口拟恢复; 布油 9/22 跌向 97 (9/8 以来最低)",
      "unit": "百万桶/日",
      "observation_date": "2026-09-22",
      "published_at": "2026-09-22",
      "source_url_or_file": "https://www.usnews.com/news/world/articles/2026-09-22/saudi-arabia-restarts-east-west-oil-pipeline-to-resume-exports-from-yanbu-sources-say; https://www.hydrocarbonprocessing.com/news/2026/09/saudi-arabia-restarts-east-west-oil-pipeline/",
      "original_source": "路透 (消息人士; 多源转引)",
      "price_basis": null,
      "comparison_basis": "上周 '半恢复 2-2.5 百万桶/日'",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sc_daily_media_0921_0924",
      "metric": "SC 主力逐日涨跌 (媒体收盘口径, 非结算)",
      "value": "9/22 夜盘 -2.3%; 9/23 -4%; 9/24 SC2611 收 730 元/桶 (+34.9, +5.02%; 另一源 '收盘大涨近 7%' 口径不同); 布油 9/25 105.11 (-1.4%), 周 +1.2%~2%",
      "unit": "%, 元/桶",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-24",
      "source_url_or_file": "https://finance.jrj.com.cn/2026/09/24152858529792.shtml; https://finance.jrj.com.cn/2026/09/23152858523090.shtml; http://news.10jqka.com.cn/20260923/c680203451.shtml; https://www.21jingji.com/article/20260924/herald/929d8d78497628ecf33575e317403422.html",
      "original_source": "金融界/同花顺/21 经济/光大期货收盘转引",
      "price_basis": "close (非 settle)",
      "comparison_basis": "前收盘; MA 原油周涨护栏须两端 settle (9/17→9/24), 本项不作命中判定",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_daily_media_0921_0924",
      "metric": "甲醇主力逐日涨跌 (媒体收盘口径)",
      "value": "9/18 夜盘 (9/21 报) +2.05%; 9/23 跌逾 3%; 9/24 +3.26% (主力口径; 执行腿/判定腿 MA2701 逐日结算未取得)",
      "unit": "%",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-24",
      "source_url_or_file": "https://finance.jrj.com.cn/2026/09/21080858496240.shtml; https://finance.jrj.com.cn/2026/09/24152858529792.shtml",
      "original_source": "金融界收盘表 (转引)",
      "price_basis": "close (非 settle)",
      "comparison_basis": "#30 须 MA2701 settle/pre_settle; 本项仅记录",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_supply_tight_0923",
      "metric": "甲醇国内独立产业事实 (现货/装置/进口)",
      "value": "太仓现货 4,090 元/吨 (9/23); 内蒙北线 3,335; CFR 中国 470-474 美元/吨; 西北 3,400 (9/26, 仅次于 2021-10 的近历史高); 国内检修装置复产偏慢 (月供应约 2,620 万吨 vs 1-5 月 2,890); 伊朗供应持续低位→到港低; 江浙 MTO 开工极低但内地 MTO 季节性恢复",
      "unit": "元/吨, 美元/吨, 万吨/月",
      "observation_date": "2026-09-23",
      "published_at": "2026-09-24",
      "source_url_or_file": "https://www.sohu.com/a/1080246210_122014455; https://www.sohu.com/a/1079996778_122014422",
      "original_source": "光大期货 2026-09-24 能源化工日报 / 甲醇周评 2026-09-26 (搜狐转引; 两份独立来源同向)",
      "price_basis": "现货报价",
      "comparison_basis": "9/18 MA2701 settle 2977 (上一快照); 做空价差路线需 '海峡未缓和时仍支持收敛的独立国内变化'",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_plant_outage_0911",
      "metric": "中东甲醇装置停车比例 / 伊朗在产套数",
      "value": "中东约 62% 装置停车, 伊朗在产约 7 套, 日产压缩至 2-2.5 万吨",
      "unit": "%, 套",
      "observation_date": "2026-09-11",
      "published_at": "2026-09-11",
      "source_url_or_file": "https://news.qq.com/rain/a/20260911A06K2O00",
      "original_source": "腾讯/界面/FX168 (多源转引, 中信期货口径)",
      "price_basis": null,
      "comparison_basis": "两周无更新读数",
      "role": "optional_context",
      "quality": "stale",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_port_inventory_missing_0926",
      "metric": "甲醇港口/华东社会库存同口径周度数值",
      "value": null,
      "unit": "万吨",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "隆众/金联创入口 (两入口阴性, 连续第三周)",
      "original_source": "未取得",
      "price_basis": null,
      "comparison_basis": null,
      "role": "optional_context",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_confirm_def_v1",
      "metric": "MA2701-MA2705 做空价差 价格确认定义 (冻结版)",
      "value": "rule_version A-MA-2701-2705-v1; S=MA2701-MA2705 两腿 settle 之差; 触发=S 连续 2 个交易日 settle 低于 [前 10 个交易日 S 最高值 − 0.65×MA2701 ATR20 (脚本 §2a 当期值)], 且同期 MA2701 settle 未创近 20 日新高 (H20, 脚本 §2b); defined_at 2026-09-26T21:00:00+08:00; effective_from 2026-09-28; 只作前瞻, 不回判 9/21-9/24; 替换 draft1 (其第二条款引用已退出的 MA2610)",
      "unit": "元/吨",
      "observation_date": "2026-09-26",
      "published_at": "2026-09-26",
      "source_url_or_file": "research/2026-09-26-execution-audit.md (本文件 plan.confirmation_definition)",
      "original_source": "研究方按数据协议 5.1 冻结",
      "price_basis": "settle/settle",
      "comparison_basis": "前 10 交易日 S 最高值; MA2701 H20",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_0919_stale",
      "metric": "上一快照读数 (对照用, 已过期)",
      "value": "MA2701-MA2705 +312/分位 100/样本 41/41/41; RB2701-RB2703 -8/56.1; SR2701-SR2705 -78/0.0; SC2611-SC2612 +43.5/100 (1td -9.7); MA2705-MA2709 +99/100 但样本 24/21/22 且 MA2709 量缺失; RB2703-RB2705 -8/61.8 (RB2705 13,672); SC2611 结算周涨 9/11→9/18 -0.30%; D8 MA 上尾 66.7/SR 下尾 94.1/CF 下尾 98.0; ATR250 分位 MA 82.9/M 99.4/RB 72.7/SR 70.1/CF 22.0/AU 33.0, 极差 77.4; 20 日均量 MA2701 540,023/MA2705 19,628/RB2701 669,156/RB2703 27,445/M2701 1,600,298/SR2701 470,759/SR2705 40,611/CF2701 347,245/AU2612 80,370",
      "unit": "元/吨, 分位, %, 手",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt",
      "original_source": "scripts/future_data.py v1.15 (Tushare)",
      "price_basis": "settle",
      "comparison_basis": "最近已完成交易日 2026-09-24 (落后 4 个交易日)",
      "role": "required_model",
      "quality": "stale",
      "time_scope": "historical"
    },
    {
      "evidence_id": "ma2701_daily_settle_missing_0926",
      "metric": "MA2701 逐日 settle/pre_settle 涨跌 (#30 判定腿, 9/21-9/24)",
      "value": null,
      "unit": "%",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "scripts/future_data.py v1.16 §2b.1 (本周未运行)",
      "original_source": "未取得",
      "price_basis": "settle/pre_settle",
      "comparison_basis": "≥5% 触发 3 交易日顺向新开冻结",
      "role": "required_model",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "shadow_ledger_missing_0926",
      "metric": "影子账本 §5 结算 (SP-2026-09-19-MA-A-short-spread / SP-2026-09-19-MA2701-long-D)",
      "value": null,
      "unit": "元, R",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "scripts/future_data.py v1.16 §5 (本周未运行)",
      "original_source": "未取得",
      "price_basis": "settle",
      "comparison_basis": "登记 2026-09-19; 有效期 2026-09-25 (实际最后可入场日 9/24)",
      "role": "optional_context",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "us_pmi_barr_fedwatch_0925",
      "metric": "美国 9 月闪值 PMI / Fed Barr / 10 月加息概率 / 10Y / DXY",
      "value": "综合 PMI 58.4 (62 个月高; 预期 55.2), 服务业 58.7, 制造业 56.7; Barr 9/23 '进一步加息很可能是必要的'; FedWatch 10 月 (10/27-28) 加息概率 9/23 73%、9/25 71%, 12 月 95%; 10Y 9/24 峰 5.22%、9/25 5.23% (2007 年来最高); DXY 9/24 高 101.40, 9/25 约 101",
      "unit": "指数, %, 点",
      "observation_date": "2026-09-25",
      "published_at": "2026-09-25",
      "source_url_or_file": "https://www.cnbc.com/2026/09/23/market-sees-next-fed-hike-in-october-following-barr-comments-hot-inflation.html; https://www.fxstreet.com/news/gold-gains-as-us-dollar-and-yields-pause-but-weekly-loss-remains-in-sight-202609251106; https://www.cnbc.com/2026/09/26/10-year-treasury-yield-is-at-its-highest-in-19-years-how-we-got-here.html",
      "original_source": "S&P Global / 美联储 / CME FedWatch / 市场数据 (CNBC/FXStreet/CNN 多源转引)",
      "price_basis": null,
      "comparison_basis": "上周 10 月 49-57%、10Y 5.00%、DXY 100.2",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "gold_0924_0925",
      "metric": "现货金/银与黄金 T+D",
      "value": "现货金 9/24 触一周低 4,244 (跌破决议后低点约 4,270); 9/25 4,280-4,310; 周 -1%~-2%以上 (口径不同); 银 64.04, 周约 -4%; 黄金 T+D 926.5 元/克 (截至 9/24 当周 -2.12%), 沪金主力同步走弱",
      "unit": "美元/盎司, 元/克",
      "observation_date": "2026-09-25",
      "published_at": "2026-09-25",
      "source_url_or_file": "https://www.usagold.com/daily-precious-metals-market-report-september-25-2026/; https://k.sina.com.cn/article_7857201856_1d45362c001908osdy.html",
      "original_source": "USAGOLD / FXStreet / 新浪黄金 (转引)",
      "price_basis": "spot / T+D 收盘",
      "comparison_basis": "上周 4,368.60 / 沪金 948.52; 4404 观察位未回收",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "steel_inventory_mysteel_0924",
      "metric": "Mysteel 五大品种周度产量与库存 (9/24 当周) + 中钢协旬度社库",
      "value": "周产量 779.68 万吨 (-14.46); 厂库 382.81 (-8.65); 社库 1,099.16 (-47.11); 总库存 1,481.97 (-55.76, 去库加速); 中钢协 9 月中旬 21 城社库 932 万吨 (-27, -2.8%)",
      "unit": "万吨",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-24",
      "source_url_or_file": "https://www.sohu.com/a/1080407327_114984; https://www.21jingji.com/article/20260923/herald/79ade5b0884b03e164145fadc3d00b32.html",
      "original_source": "Mysteel (搜狐转引) / 中国钢铁工业协会 (21 经济转引); 两个独立公开来源同向",
      "price_basis": null,
      "comparison_basis": "Mysteel 同口径 9/3 总库存 1,572.90",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "coke_cut_prep_0921",
      "metric": "焦炭提涨/提降与钢厂盈利 (负反馈检验行输入)",
      "value": "焦炭第六轮提涨未发起; 钢厂第一轮提降 (100-110 元/吨) 准备发起, '中秋后实施则国庆前落地'; 钢厂盈利率 <10%, 绝大多数亏损, 减产预期升温; 落地与否 9/24 前未确认",
      "unit": "元/吨, %",
      "observation_date": "2026-09-23",
      "published_at": "2026-09-23",
      "source_url_or_file": "https://news.qq.com/rain/a/20260921A0A2NB00; https://news.qq.com/rain/a/20260920A0B9NP00; https://www.sohu.com/a/1079786288_122014422",
      "original_source": "腾讯头条 9/21、9/20 / 光大期货 9/23 矿钢煤焦日报 (转引)",
      "price_basis": null,
      "comparison_basis": "上周 '第五轮落地、第六轮观望→负反馈临界'",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "b_window_calendar_2026",
      "metric": "B-WINDOW 真实交易日映射 (canonical 1.6)",
      "value": "SR-summer: window_end=2026-09-30 (郑商所交易日); planned_exit=window_end 前第 5 个交易日=2026-09-22 (9/29、9/28、9/24、9/23、9/22; 9/25-9/27 休市); 审计交易日 9/24 ≥ planned_exit → 不可新开. CF-autumn: window_end=2026-10-30; planned_exit=2026-10-23 (10/29、10/28、10/27、10/26、10/23); 9/24 < planned_exit → 可新开区间内",
      "unit": "日期",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-26",
      "source_url_or_file": "framework/futures_framework.md 1.6 B-WINDOW + cal_holiday_0921 (郑商所休市安排)",
      "original_source": "canonical 定义 + 交易所日历 (确定性日历运算)",
      "price_basis": null,
      "comparison_basis": "上周人工推算 planned_exit≈9/23 (未计 9/25 休市)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sugar_sales_aug",
      "metric": "广西 8 月产销率 / 工业库存 (最近可得)",
      "value": "截至 8 月底广西累计销糖 620.13 万吨 (+44.50); 产销率 80.56% (同比 -8.48pp); 工业库存 149.61 万吨 (同比 +78.74); 9 月产销预计 10 月初发布",
      "unit": "万吨, %",
      "observation_date": "2026-08-31",
      "published_at": "2026-09-08",
      "source_url_or_file": "https://www.yntw.com/2026/09/39137.html",
      "original_source": "广西糖业协会 (糖网转引)",
      "price_basis": null,
      "comparison_basis": "同比",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sugar_prices_0924",
      "metric": "SR2701 / 广西现货 (9/24)",
      "value": "SR2701 9/24 收 5404 (+34 vs 结算; 高 5419/低 5373); 广西制糖企业报价 5150-5200 (+20)",
      "unit": "元/吨",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-24",
      "source_url_or_file": "https://www.yntw.com/2026/09/39272.html; https://ncp.mysteel.com/a/26092415/1ED644170FFB7402.html",
      "original_source": "糖网 / Mysteel 农产品",
      "price_basis": "close / 现货报价",
      "comparison_basis": "9/18 settle 5326",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "cotton_reserve_0920",
      "metric": "储备棉轮出成交率 / 新棉上市进度",
      "value": "第九周 (9/14-9/18) 挂牌 4.05 万吨、成交 3.77 万吨、成交率 93.1% (均价 16,816); 9/20 成交率 99.51% (均价 16,457.23, 较 9/18 低 139.37); 累计成交率 99.15%; 全疆吐絮率近 70%、北疆零星机采、新棉零星开秤; '新棉临近集中上市, 内外棉价承压下跌'",
      "unit": "%, 元/吨",
      "observation_date": "2026-09-20",
      "published_at": "2026-09-20",
      "source_url_or_file": "https://k.sina.cn/article_5953740931_162dee08306703zkxy.html; https://k.sina.cn/article_5953189932_162d6782c06704ysly.html",
      "original_source": "中储棉抛储日报 / 中国棉花每周快报 (新浪转引; 两份独立来源)",
      "price_basis": null,
      "comparison_basis": "上周 9/18 96.37% (本轮首见 <100%)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "soymeal_inv_0918",
      "metric": "豆粕库存 / 大豆到港 / 巴西出口",
      "value": "油厂压榨 233.43 万吨, 豆粕库存 117.32 万吨 (9/18; 9/1 口径 110.98); 大豆到港 (截至 9/11) 247 万吨; ANEC 巴西 9 月出口预估 832 万吨 (+19.4%); M2701 9/24 +0.35% (媒体)",
      "unit": "万吨",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-22",
      "source_url_or_file": "https://finance.sina.com.cn/money/future/2026-09-22/doc-inissyqz8839747.shtml",
      "original_source": "新浪 (Mysteel/ANEC 口径转引, 单源)",
      "price_basis": null,
      "comparison_basis": "9/1 口径",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "canonical_m_route",
      "metric": "M 备选卡: 已许可具体策略",
      "value": "无已许可具体策略 (仅观察; 升核心须已有许可路由 + 独立公开供需证据 + 行情确认; 不进 C 池)",
      "unit": "规则",
      "observation_date": "2026-09-20",
      "published_at": "2026-09-20",
      "source_url_or_file": "framework/futures_framework.md 1.5 M2701 卡 / 0) 备选行",
      "original_source": "canonical v2.27",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "a_share_0924",
      "metric": "A 股 9/24 与本周 (②'' 背景)",
      "value": "9/24 沪指 3888.37 (-1.22%, 失守 3900), 深成 -2.34%, 创业板 -2.68%; 本周 (9/21-9/24) 沪指 -0.60%、深成 -2.37%、创业板 -2.48%; 成交 9/23 1.76 万亿、9/24 1.669 万亿; 两融 9/23 沪深京 26,550.08 亿 (-13 亿 d/d)",
      "unit": "点, 亿元",
      "observation_date": "2026-09-24",
      "published_at": "2026-09-24",
      "source_url_or_file": "https://finance.sina.com.cn/tech/roll/2026-09-24/doc-inisxxkx0219872.shtml; https://finance.sina.cn/2026-09-24/detail-iniswrrf5482763.d.html",
      "original_source": "新浪/FX168/格隆汇 (同口径转引)",
      "price_basis": "close",
      "comparison_basis": "上周沪指 3911.87, 9/18 成交 2.09 万亿",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "russia_diesel_ban_report_0921",
      "metric": "俄柴油出口禁令 (生产商) 延期状态",
      "value": "报道: 延至 10/31 (Vedomosti/HP/Roic) 或 '延至 11 月' (Caliber); 官方 government.ru 最新为 8/29 延至 9/30; 9/30 到期节点维持, 官宣前不作已落地",
      "unit": "政策",
      "observation_date": "2026-09-21",
      "published_at": "2026-09-21",
      "source_url_or_file": "https://www.hydrocarbonprocessing.com/news/2026/09/russia-set-to-extend-diesel-export-ban-until-end-of-october/; https://www.roic.ai/news/russia-set-to-extend-diesel-export-ban-through-october-as-refinery-strikes-bite-09-21-2026; http://government.ru/en/news/59723/",
      "original_source": "Vedomosti (匿名消息) / 俄政府网",
      "price_basis": null,
      "comparison_basis": "9/30 到期",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "scan_ps_lc_0923",
      "metric": "池外扫描: 多晶硅 / 碳酸锂",
      "value": "PS2611 9/22 收 37,705 (+2.39%); N 型复投料 4.30 万、颗粒硅 4.00-4.10 万元/吨成交; 减产方案 '待最终确认与实施'; LC 仓单 9/16 45,515 吨 (-1,649 d/d), Mysteel 总库存 121,810 吨 (-4,890 w/w)",
      "unit": "元/吨, 吨",
      "observation_date": "2026-09-23",
      "published_at": "2026-09-23",
      "source_url_or_file": "https://finance.eastmoney.com/a/202609233882660457.html; https://k.sina.cn/article_5953466437_162dab0450670bco80.html",
      "original_source": "东方财富 / 新浪 (广期所、Mysteel 口径转引)",
      "price_basis": "close / 现货",
      "comparison_basis": "上周",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "inv_canonical_calendar_1009",
      "metric": "canonical v2.27 长假日历文本 (已撤回)",
      "value": "'国庆长假 10/1-10/8 (9/30=T-1; 10/9 复盘/首个响应日; 低敞口条款 10/9 复评; 10/4 OPEC+ 国内首个响应日 10/9)'; 未列 9/25-9/27 中秋休市",
      "unit": "日期",
      "observation_date": "2026-09-19",
      "published_at": "2026-09-20",
      "source_url_or_file": "framework/futures_framework.md v2.27 1.4/0.0b/6.1/0.1",
      "original_source": "canonical (上周状态换版时按推测写入)",
      "price_basis": null,
      "comparison_basis": "cal_holiday_0921",
      "role": "required_execution",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "inv_taicang_2024",
      "metric": "检索命中 '9 月 25 日太仓甲醇 2440-2460、基差 +25~+50' (已撤回)",
      "value": "2440-2460 元/吨",
      "unit": "元/吨",
      "observation_date": "2024-09-25",
      "published_at": "2024-09-25",
      "source_url_or_file": "https://nenghua.m.mysteel.com/a/24092512/0C177EE285D7D817_abc.html",
      "original_source": "Mysteel 2024 年报价 (URL 编号 24092512=2024-09-25; 2026-09-25 为休市日)",
      "price_basis": "现货",
      "comparison_basis": "跨年; 与 9/23 太仓 4,090 不符",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "inv_sc_0926",
      "metric": "检索命中 '9/26 燃料油 -6% 至 2,666、SC 主力 -5% 至 624.3' (已撤回)",
      "value": "624.3 元/桶",
      "unit": "元/桶",
      "observation_date": "2026-09-26",
      "published_at": "2026-09-26",
      "source_url_or_file": "WebSearch 摘要 (往年读数, 无有效 URL)",
      "original_source": "未知年份收评摘要",
      "price_basis": "close",
      "comparison_basis": "2026-09-26 为周六且 9/25-9/27 休市; 与 9/24 收 730 不符",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "inv_pmi_prior_year",
      "metric": "检索命中 '9 月制造业 PMI 为 49.8% (连续回升)' (已撤回)",
      "value": "49.8%",
      "unit": "%",
      "observation_date": "2025-09-30",
      "published_at": "2025-09-30",
      "source_url_or_file": "https://www.stcn.com/article/detail/3369277.html",
      "original_source": "证券时报往年文章 (编号早于 2026-09 文章); 2026 年 9 月 PMI 定于 2026-09-30 发布",
      "price_basis": null,
      "comparison_basis": "往年",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "historical"
    }
  ],
  "candidates": [
    {
      "candidate_id": "2026-09-24|MA2701-MA2705|A|short_spread|v2.27",
      "opportunity_id": "MA_A_2701_2705",
      "trade_date": "2026-09-24",
      "contracts": ["MA2701", "MA2705"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "short_spread",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本周无行情快照: 价差/分位/1-5-10td/样本验收无 9/24 实测 (9/18 读数 stale); 独立产业事实本周可得 (现货/装置/进口); 港口库存数值按协议 6 降为增强级第二指标",
      "signal": "unknown",
      "signal_basis": "研究筛选无本周实测; 确认定义 v1 自 2026-09-28 生效, 本周不回判 → unknown",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "近3年同期分位需 9/24 口径快照 §1; 上一实测 100 (9/18) 已过期不沿用",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "9/28 前运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 无快照则本项保持 unknown",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["td_calendar_0924"],
          "details": "近腿 MA2701 72 td ≥20 (9/24 口径, 日历运算); 结构退出边界=近腿触 #1 (≈2026-12-17) 或主力换月"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "20 日均量需 9/24 口径快照; 9/18 实测 540,023/19,628 已过期不沿用",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "同 screening: 补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "同期样本验收须按 9/24 市场锚重算 (9/18 锚 41/41/41 complete 不自动延续)",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §1 样本验收",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "domestic_model_basis",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["ma_supply_tight_0923"],
          "details": "国内路线论证结案 (未成案): '即使海峡未缓和, 哪项独立国内变化仍支持收敛' — 本周可得的国内事实 (太仓 4,090/西北 3,400 近历史高、检修装置复产偏慢、伊朗供应低位→到港低、内地 MTO 恢复) 全部指向近月强; 上周候选驱动 (装置复产/国庆前后到港) 未被观测到, 提保扩板为规则事实非产业变化 → 按协议 4 不能改名放行; 复活条件见 unresolved_items; 不转 geopolitical_fade 建仓 (research_only)",
          "diagnostic_evidence_refs": ["ma_plant_outage_0911", "ma_port_inventory_missing_0926"]
        },
        {
          "rule_id": "confirmation_definition",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["ma_confirm_def_v1"],
          "details": "A-MA-2701-2705-v1 已冻结 (defined_at 2026-09-26T21:00+08:00, effective_from 2026-09-28); 替换 draft1 (第二条款引用已退出的 MA2610); 冻结不等于触发, 观测值待快照"
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["ma_supply_tight_0923"],
          "details": "(b) 独立产业事实已核反证延续: 现货 4,090/复产慢/进口低位支持近月强, 与做空价差反向; (a) 价格确认 v1 生效前无观测=unknown 子项; 港口库存数值 (missing) 与 9/11 装置停车比例 (stale) 只入 diagnostic",
          "diagnostic_evidence_refs": ["ma_port_inventory_missing_0926", "ma_plant_outage_0911", "ma_daily_media_0921_0924"]
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_0917_full"],
          "details": "9/21 起 MA2610/2611 分级 (对本对无直接影响), 9/29 结算起甲醇全合约保证金 10%/涨跌停 9% → 结构双腿按实际保证金口径计占用, ×0.8 缓冲 (2.3), 公告 ±1 日 (9/28-9/30) 门槛 +0.3; 非否决"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "国内路线未成案 → 本轮不出计划; 上周影子计划 SP-2026-09-19-MA-A-short-spread 仅为规则复评假设, 结算 pending",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "复活条件之一被观测 (装置复产数值/到港回升/现货基差走弱) 且确认定义 v1 触发后, 再按策略 A 协议出具四点包; 否则保持结案记录",
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["screening", "#1", "#2", "#13", "domestic_model_basis", "confirmation_definition", "#5", "exchange_notice", "execution_plan", "account"],
      "all_blockers": ["domestic_model_basis", "#5"],
      "unknown_checks": ["screening", "#2", "#13", "execution_plan", "account"],
      "first_blocker": "domestic_model_basis",
      "only_blocker": false,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": ["D9=3 default_neutral"],
        "notes": "D4=null (分位无本周实测); D2=1 (已核反证); D1=null (v1 生效前无观测); D3=null (计划缺失); D5=null; 完整总分 null"
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": "A-MA-2701-2705-v1",
        "confirmation_definition": {
          "state": "frozen",
          "rule_version": "A-MA-2701-2705-v1",
          "defined_at": "2026-09-26T21:00:00+08:00",
          "effective_from": "2026-09-28",
          "price_basis": "两腿 settle 之差 S=MA2701-MA2705 (元/吨)",
          "economic_rationale": "做空价差的价格确认=近月挤仓溢价开始回吐: S 连续 2 个交易日 settle 低于 [前 10 个交易日 S 最高值 − 0.65×MA2701 ATR20 (脚本 §2a 当期值)], 且同期 MA2701 settle 未创近 20 日新高 (H20, 脚本 §2b; 近月不再由现货追认推升); 阈值以 ATR 比例设定, 避免任意元数/天数门槛; 与 D1 分工: 仅评价价格模式, 产业支持/反证归 D2/#5(b); 前瞻生效 2026-09-28, 不回判 9/21-9/24; 替换 draft1 (其 'MA2610-MA2701 不再走阔' 条款引用已退出腿)",
          "observed_values": "无本周快照; 上一实测 2026-09-18 S=+312, 2026-09-17 S=+330, MA2701 ATR20 91.14, H20 3154 (stale, 仅对照)"
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
      "evidence_refs": ["td_calendar_0924", "ma_supply_tight_0923", "ma_confirm_def_v1", "czce_margin_0917_full"]
    },
    {
      "candidate_id": "2026-09-24|MA2705-MA2709|A|unknown|v2.27",
      "opportunity_id": "MA_A_2705_2709_prep",
      "trade_date": "2026-09-24",
      "contracts": ["MA2705", "MA2709"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "准备对: 本周无快照; 上一快照同期样本 24/21/22<33、MA2709 20 日均量缺失 (#2 缺失) → 未计算/原始字段缺失, 不授许可",
      "signal": "unknown",
      "signal_basis": "分位无本周实测 (上一实测 100 仅参考); 样本不足",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/24 口径快照",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §1 (roll_preparation)",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "MA2709 20 日均量上一快照缺失 (不足 20 个完整有效成交量样本); 本周无刷新",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照; MA2709 放量过 #2 前不授许可",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "同期样本上一快照 24/21/22 <33 (incomplete); 本周无刷新",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照; 样本达 33/41 各年前列具体缺口",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["screening", "#2", "#13", "account"],
      "all_blockers": [],
      "unknown_checks": ["screening", "#2", "#13", "account"],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "准备对不评分"
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
      "evidence_refs": ["td_calendar_0924"]
    },
    {
      "candidate_id": "2026-09-24|RB2701-RB2703|A|unknown|v2.27",
      "opportunity_id": "RB_A_2701_2703",
      "trade_date": "2026-09-24",
      "contracts": ["RB2701", "RB2703"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本周无快照: 分位/价差无 9/24 实测 (上一实测 56.1 未触发不能沿用); Mysteel 同口径总库存本周取得 (上周缺数子项解除)",
      "signal": "unknown",
      "signal_basis": "研究筛选需本周快照 §1; 上周 no_signal 直接证据已过期",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/24 口径快照 §1",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["td_calendar_0924"],
          "details": "RB2701 73 td ≥20; RB2703 109 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "20 日均量需本周快照 (上一实测 669,156/27,445 过期)",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "方向未定 (研究筛选 unknown) → (a)(b) 均不能判; 独立产业证据已备: Mysteel 同口径总库存 -55.76 去库加速、中钢协旬度 -2.8% (节前补库); 钢厂第一轮提降准备=负反馈启动候选 (背景)",
          "diagnostic_evidence_refs": ["steel_inventory_mysteel_0924", "coke_cut_prep_0921"],
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "快照到位且分位 ≥70 时按 3.1 定方向与确认定义, 再核 (a)(b); 未触发则结案 no_signal",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "D14",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "独立国内月差不依赖复产/铁水/收缩成本假设; 铁水为参考; 提降准备为背景"
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["shfe_margin_0921"],
          "details": "9/23 结算起 RB 涨跌停 7%/一般保证金 9% → ×0.8 缓冲、公告 ±1 日门槛 +0.3、公告日核占用; 非否决"
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["screening", "#1", "#2", "#5", "D14", "exchange_notice", "account"],
      "all_blockers": [],
      "unknown_checks": ["screening", "#2", "#5", "account"],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "筛选未定, 不评分"
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
      "evidence_refs": ["td_calendar_0924", "steel_inventory_mysteel_0924", "shfe_margin_0921"]
    },
    {
      "candidate_id": "2026-09-24|RB2703-RB2705|A|unknown|v2.27",
      "opportunity_id": "RB_A_2703_2705_prep",
      "trade_date": "2026-09-24",
      "contracts": ["RB2703", "RB2705"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "准备对 (仅取样): 本周无快照; 上一实测分位 61.8、RB2705 13,672 临界过 #2",
      "signal": "unknown",
      "signal_basis": "需本周快照",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/24 口径快照",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "RB2705 20 日均量上一实测 13,672 临界; 本周无刷新",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["screening", "#2", "account"],
      "all_blockers": [],
      "unknown_checks": ["screening", "#2", "account"],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "准备对不评分"
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
      "evidence_refs": ["td_calendar_0924"]
    },
    {
      "candidate_id": "2026-09-24|MA2701|directional|long|v2.27",
      "opportunity_id": "MA_D_long_2701",
      "trade_date": "2026-09-24",
      "contracts": ["MA2701"],
      "strategy": "D",
      "hypothesis": "event_shock",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本周无快照: SC2611 结算周涨 (9/17→9/24)、D8、ATR 分层/重校准、MA2701 逐日结算 (#30) 全部 unknown; 媒体收盘涨跌只作记录",
      "signal": "unknown",
      "signal_basis": "策略 D 触发=事件落地+落地次日方向确认+微观同向; 本周事件 (七日方案被拒/胡塞袭延布) 落在 9/24 后或闭市期, 落地次日确认无法核; → unknown",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["td_calendar_0924"],
          "details": "72 td ≥ 20 + D 池持仓上限 30 日 (≥50 td)"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需本周快照",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["cal_holiday_0921", "czce_margin_0917_full", "ine_sc_margin_0921", "shfe_margin_0921", "dce_margin_0918", "iran_7day_plan_rejected_0926"],
          "details": "0.1 低敞口判定继续命中: 高密度簇 (9/28 周末 headline 首个交易日 [七日方案被拒/经济 D 日]、9/29 郑商所/大商所第二阶段提保、9/30 俄禁令到期/9 月 PMI/长假 T-1、10/1-10/7 闭市含 10/4 OPEC+、10/8 复盘、10/9 WASDE、10/27-28 FOMC; 两周内 ≥2 离散催化且当周有未落地节点) + 交易所公告 ±1 日 (9/28-9/30 全在 9/29 节点 ±1 内) + D12 高波层 (上一实测 82.9, 本周无刷新, 不单独作依据); 限隔夜池方向性单边新开 → 否决; 结构表达不受本项",
          "diagnostic_evidence_refs": ["inv_canonical_calendar_1009"]
        },
        {
          "rule_id": "MA_oil_guard",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "SC2611 结算周涨 9/17→9/24 (两端 settle) 无快照; 9/24 收盘 +5.02% 为收盘口径仅记录, 不作 >5%/>8% 命中判定; 上一读数 -0.30% 已过期",
          "diagnostic_evidence_refs": ["sc_daily_media_0921_0924", "snap_0919_stale", "inv_sc_0926"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2b.1 SC 护栏结算周涨列",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "D8 周涨分位需快照 §2d (9/17→9/24); 上一读数上尾 66.7 过期",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2d",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#20",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "创近 250 日 H 与周涨前 10% 分位需快照",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2b/§2d",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#30",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "MA2701 逐日 settle/pre_settle (9/21-9/24) 未取得; 主力 9/24 +3.26% (媒体) 与 SC 9/24 +5.02% 不替代判定腿",
          "diagnostic_evidence_refs": ["ma2701_daily_settle_missing_0926", "ma_daily_media_0921_0924", "sc_daily_media_0921_0924"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "运行 scripts/future_data.py v1.16 (§2b.1 日结算涨跌%/近 5 日/#30 近 3 日≥5% 列) 或终端导出 MA2701 逐日 settle/pre_settle",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "ATR250 分位/HV20/HV60 与池内极差需快照 §2a; 上一实测 82.9 高波层/极差 77.4 过期; 事件 T-3 依 0.0b (9/30、10/8 节点) 人工核",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2a",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_0917_full"],
          "details": "9/29 结算起甲醇全合约保证金 10%/涨跌停 9% → ×0.8 缓冲、公告 ±1 日 (9/28-9/30) 门槛 +0.3、公告日核占用; 非否决"
        },
        {
          "rule_id": "#25",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "当日 ATR 重校准核验仅对隔夜持仓适用; 账户未知且无已核持仓"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无事件对象/落地次日确认条件/Entry/SL/TP; 上周影子计划 SP-2026-09-19-MA2701-long-D 结算 pending",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "#16 解除 (10/8 复评) 前不出计划; 事件对象候选=10/4 OPEC+ (10/8 响应)、10/27-28 FOMC",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["#1", "#2", "#16", "MA_oil_guard", "D8", "#20", "#30", "D12", "exchange_notice", "#25", "execution_plan", "account"],
      "all_blockers": ["#16"],
      "unknown_checks": ["#2", "MA_oil_guard", "D8", "#20", "#30", "D12", "execution_plan", "account"],
      "first_blocker": "#16",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 事件冲击池",
        "result": null,
        "defaulted_dimensions": ["D9=3 default_neutral"],
        "notes": "D12/D8/D11 无本周实测 → null; 事件对象未指定 → D1/D2/D3/D5 null"
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
      "evidence_refs": ["td_calendar_0924", "cal_holiday_0921", "czce_margin_0917_full", "ine_sc_margin_0921"]
    },
    {
      "candidate_id": "2026-09-24|MA2701|directional|short|v2.27",
      "opportunity_id": "MA_short_2701",
      "trade_date": "2026-09-24",
      "contracts": ["MA2701"],
      "strategy": "D",
      "hypothesis": "event_shock",
      "evidence_basis": "geopolitical_fade",
      "direction": "short",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "同多头记录: 无快照; ①要件二 back 方向 unknown",
      "signal": "unknown",
      "signal_basis": "空头新开受 #26 (①未证缓和) 否决; 事件落地次日确认无法核 → unknown",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["td_calendar_0924"],
          "details": "72 td ≥50"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需本周快照",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["cal_holiday_0921", "czce_margin_0917_full", "ine_sc_margin_0921", "iran_7day_plan_rejected_0926"],
          "details": "同多头记录: 低敞口继续命中 (高密度簇 + 交易所公告 ±1 日)",
          "diagnostic_evidence_refs": ["inv_canonical_calendar_1009"]
        },
        {
          "rule_id": "#26",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["iran_7day_plan_rejected_0926", "hormuz_tankers_hit_0921"],
          "details": "①'中断证真' 维持: 要件一 '再袭船' 9/21 两船遇袭 (UKMTO, 多源) 再命中; 反向质变要件 (官方停火/重开或伊朗许可-收费机制正式落地 + back 回落) 未出现——伊朗七日方案 9/25 为 '方案提出', 美方 9/26 拒绝并启动 '经济 D 日'、'不在任何谈判中'; 要件二 back 方向无快照 unknown (不影响 #26: 未证缓和即否决); 9/22-9/23 回落由管道复运/停战希望驱动, 非官方重开 → 能源链方向性空头新开否决继续",
          "diagnostic_evidence_refs": ["saudi_pipeline_restart_0922", "houthi_yanbu_0924", "sc_daily_media_0921_0924"]
        },
        {
          "rule_id": "MA_oil_guard",
          "applicable": false,
          "result": "not_applicable",
          "evidence_refs": [],
          "details": "SC 结算周涨 >5%/8% 护栏只作用于指定方向性多头"
        },
        {
          "rule_id": "#30",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "双向对称: MA2701 逐日结算 (9/21-9/24) 未取得; SC 9/23 -4% (媒体) 不替代判定腿",
          "diagnostic_evidence_refs": ["ma2701_daily_settle_missing_0926", "sc_daily_media_0921_0924"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2b.1",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "空头看下尾; 需快照 §2d",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2d",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需快照 §2a",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2a",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_0917_full"],
          "details": "同多头记录; 非否决"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "#26 解除前不出计划",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "①缓和证真 (官方重开 + back 回落) 后再评估; 之前只做存量双向跳空预案",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["#1", "#2", "#16", "#26", "MA_oil_guard", "#30", "D8", "D12", "exchange_notice", "execution_plan", "account"],
      "all_blockers": ["#16", "#26"],
      "unknown_checks": ["#2", "#30", "D8", "D12", "execution_plan", "account"],
      "first_blocker": "#16",
      "only_blocker": false,
      "score": {
        "canonical_ref": "3.1 事件冲击池",
        "result": null,
        "defaulted_dimensions": ["D9=3 default_neutral"],
        "notes": "①≠缓和证真期间能源链方向性单边固定 +1 扣减; 其余维度 null"
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
      "evidence_refs": ["td_calendar_0924", "iran_7day_plan_rejected_0926", "hormuz_tankers_hit_0921", "czce_margin_0917_full"]
    },
    {
      "candidate_id": "2026-09-24|M2701|unknown|unknown|v2.27",
      "opportunity_id": "M_observe_2701",
      "trade_date": "2026-09-24",
      "contracts": ["M2701"],
      "strategy": "unknown",
      "hypothesis": "unknown",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "无已许可具体策略 (仅观察); 行情无本周快照; 供需读数 9/18 口径可得",
      "signal": "unknown",
      "signal_basis": "无已定义信号条件",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "licensed_route",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["canonical_m_route"],
          "details": "1.5 M 卡: 无已许可具体策略, 不进 C 池; 升核心须已有许可路由 + 独立公开供需证据 + 行情确认; 本周豆粕库存 117.32 (+6.34 vs 9/1) 供应宽松为背景",
          "diagnostic_evidence_refs": ["soymeal_inv_0918"]
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["dce_margin_0918"],
          "details": "9/29 结算起豆粕涨跌停 8%/保证金 10%; 10/9 WASDE (北京 10/10 00:00) 国内首次响应 10/12, 报告前 2 日禁新开按 0.0b 核; 非否决"
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["licensed_route", "exchange_notice", "account"],
      "all_blockers": ["licensed_route"],
      "unknown_checks": ["account"],
      "first_blocker": "licensed_route",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "research_only 不评分"
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
      "evidence_refs": ["canonical_m_route", "dce_margin_0918"]
    },
    {
      "candidate_id": "2026-09-24|SR2701-SR2705|A|unknown|v2.27",
      "opportunity_id": "SR_A_2701_2705",
      "trade_date": "2026-09-24",
      "contracts": ["SR2701", "SR2705"],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "本周无快照 (上一实测分位 0.0 未触发不能沿用)",
      "signal": "unknown",
      "signal_basis": "需本周快照 §1",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/24 口径快照",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["td_calendar_0924"],
          "details": "SR2701 72 td / SR2705 151 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需本周快照 (上一实测 470,759/40,611 过期)",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_0917_full"],
          "details": "9/29 结算起白糖保证金 8%/涨跌停 7%; 非否决"
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["screening", "#1", "#2", "exchange_notice", "account"],
      "all_blockers": [],
      "unknown_checks": ["screening", "#2", "account"],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "筛选未定, 不评分"
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
      "evidence_refs": ["td_calendar_0924", "sugar_prices_0924", "czce_margin_0917_full"]
    },
    {
      "candidate_id": "2026-09-24|SR2701|B|long|v2.27",
      "opportunity_id": "SR_B_summer_2026",
      "trade_date": "2026-09-24",
      "contracts": ["SR2701"],
      "strategy": "B",
      "hypothesis": "seasonal_long",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "available",
      "data_feasibility_reason": "B-WINDOW 日历可由 canonical 定义与交易所日历确定性计算; 本记录只依赖日历",
      "signal": "not_triggered",
      "signal_basis": "TRIGGER-B 新开须 window_start ≤ 执行交易日 < planned_exit; SR-summer planned_exit=2026-09-22 (真实交易日历), 审计交易日 9/24 ≥ planned_exit → 本窗口不可新开, 直接日历证据",
      "signal_evidence_refs": ["b_window_calendar_2026"],
      "screening_evidence": "b_window_calendar_2026",
      "evaluated_checks": [
        {
          "rule_id": "B_new_open_window",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["b_window_calendar_2026"],
          "details": "planned_exit 2026-09-22 已过 (上周人工推算 9/23 未计 9/25 休市, 已纠正); 窗口 9/30 结束; 本窗口结案, 不为尚未需要的 TP 样本/账户维持 incomplete; B-HISTORY 组装为 2027 窗口 research 责任"
        }
      ],
      "evaluation_order": ["B_new_open_window"],
      "all_blockers": ["B_new_open_window"],
      "unknown_checks": [],
      "first_blocker": "B_new_open_window",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 季节性池",
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
          "rule_version": "B-v2.24",
          "defined_at": null,
          "effective_from": null,
          "price_basis": "元/吨 settle (Step5-B)",
          "economic_rationale": "夏季消费与节前备货 (1.6 B-WINDOW); 本窗口新开区间已过",
          "observed_values": "SR2701 9/24 收 5404 (媒体); 广西现货 5150-5200"
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
      "not_evaluated_after_no_signal": ["card_veto (广西 8 月产销率反向, 上周已核 fail, 本周不再评估)", "#5", "D8", "B_trigger", "execution_plan", "account"],
      "evidence_refs": ["b_window_calendar_2026", "sugar_sales_aug", "sugar_prices_0924"]
    },
    {
      "candidate_id": "2026-09-24|CF2701|B|long|v2.27",
      "opportunity_id": "CF_B_autumn_2026",
      "trade_date": "2026-09-24",
      "contracts": ["CF2701"],
      "strategy": "B",
      "hypothesis": "seasonal_long",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "B 触发 Entry_raw=max(MA20, pre_window_low5+ATR20) 需本周快照 MA20/ATR20 (无) 且 B-HISTORY 未组装; 独立产业证据 (储备棉/新棉) 可得",
      "signal": "unknown",
      "signal_basis": "窗口筛选 pass 不是完整开仓信号; Entry 条件未组装且无快照 → unknown",
      "screening_evidence": "b_window_calendar_2026",
      "evaluated_checks": [
        {
          "rule_id": "B_window_screen",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["b_window_calendar_2026"],
          "details": "CF-autumn 09-01–10-31: window_end 2026-10-30, planned_exit 2026-10-23; 9/24 在可新开区间"
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["td_calendar_0924"],
          "details": "CF2701 72 td"
        },
        {
          "rule_id": "card_veto",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "'国储轮储公告日 ±3 天暂停' 对逐日滚动轮出周的适用性仍未定义 (轮出自 7/20 起每日进行)",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "裁定该条款对滚动轮出的适用口径 (按轮出周计划公告日或不适用) 并写入品种卡; 本周不裁量",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": ["cotton_reserve_0920"],
          "details": "(b) 独立产业事实已核反证延续: 储备棉第九周成交率 93.1%、9/20 99.51% (均价走低)、吐絮率近 70%、新棉零星开秤、新棉临近集中上市内外棉价承压 — 供给端压力, 无独立需求侧支持; (a) B Entry 未组装 = unknown 子项"
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需快照 §2d (做多看上尾); 上一读数下尾 98.0 (空头档, 做多不适用) 过期",
          "diagnostic_evidence_refs": ["snap_0919_stale"],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2d",
            "due_at": "2026-09-28"
          }
        },
        {
          "rule_id": "B_trigger",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "Entry_raw=max(MA20, pre_window_low5+ATR20): MA20/ATR20 需快照; pre_window_low5 (8/25-8/31) 与 B-HISTORY (CF2601/2501/2401 秋窗) 未组装; rule_version=B-v2.24 未登记 defined_at/effective_from",
          "gap": {
            "kind": "calculation",
            "owner": "data_pipeline",
            "next_action": "快照到位后按 scripts/SEASONAL_PLAN_INPUT.md 组装输入并运行 seasonal_plan.py",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": ["czce_margin_0917_full"],
          "details": "9/29 结算起棉花保证金 9%/涨跌停 8%; 非否决"
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
            "next_action": "#5 已核 fail (供给端反证) → 本周不出计划; 独立需求侧证据出现且 B 触发组装后再评估",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照",
          "gap": {
            "kind": "account",
            "owner": "user",
            "next_action": "执行核验阶段提供账户快照",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": ["B_window_screen", "#1", "card_veto", "#5", "D8", "B_trigger", "exchange_notice", "execution_plan", "account"],
      "all_blockers": ["#5"],
      "unknown_checks": ["card_veto", "D8", "B_trigger", "execution_plan", "account"],
      "first_blocker": "#5",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 季节性池",
        "result": null,
        "defaulted_dimensions": [],
        "notes": "D2'=1 (供给端反证); Entry 未组装 → D1/D3 null"
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
          "economic_rationale": "秋季订单与新棉供给的净影响 (1.6 B-WINDOW); 当前供给端反证",
          "observed_values": "无本周快照; CF2701 9/18 收 15,750 (上周), 9/24 +0.25% (媒体)"
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
      "evidence_refs": ["b_window_calendar_2026", "td_calendar_0924", "cotton_reserve_0920", "czce_margin_0917_full"]
    }
  ],
  "unresolved_items": [
    {
      "item": "行情快照补跑 (首要): 用户本机 (TUSHARE_TOKEN) 运行 python3 scripts/future_data.py (v1.16; 含 §2b.1 判定腿逐日结算涨跌与 §5 影子结算) 并提交 research/<日期>-data-snapshot.txt; 用于 SC2611 结算周涨 (9/17→9/24)、MA2701 #30、SC 近端 back 方向 (①要件二)、A 池分位/价差变化/样本验收、ATR 分层与极差、D8、影子计划结算; 无快照则 9/28-9/30 全部方向性新开判定保持 unknown",
      "owner": "账户持有人 (本机运行) / data_pipeline",
      "due_at": "2026-09-28",
      "required_evidence": ["snap_0919_stale", "ma2701_daily_settle_missing_0926", "shadow_ledger_missing_0926"],
      "resolution": "pending"
    },
    {
      "item": "MA 国内路线论证结案 (未成案) 的复活条件: 观测到 (i) 国内装置复产的数值化进度 (开工率/周产量回升), 或 (ii) 到港量回升 (伊朗/非伊朗货源), 或 (iii) 太仓现货基差走弱 (现货相对近月期货回落) 三者之一, 且确认定义 A-MA-2701-2705-v1 触发; 之前保持结案记录, 不改名 geopolitical_fade 建仓",
      "owner": "研究方",
      "due_at": "next_report",
      "required_evidence": ["ma_supply_tight_0923", "ma_confirm_def_v1"],
      "resolution": "pending"
    },
    {
      "item": "甲醇港口/华东社会库存同口径周度数值: 连续第三周两入口阴性 → 按协议 6 降为增强级第二指标 (MA 国内月差的必要独立产业证据改由装置公告/现货基差承担); 仍每周尝试两入口, 取得即记录, 不再作为必要缺项",
      "owner": "研究方",
      "due_at": "next_report",
      "required_evidence": ["ma_port_inventory_missing_0926"],
      "resolution": "pending (降级记录)"
    },
    {
      "item": "日历纠错写入 canonical (阶段③): 10/1-10/7 休市、10/8 恢复交易 (首个响应日/复盘日/低敞口复评日 10/9→10/8); 9/25-9/27 中秋休市; 9/24 与 9/30 无夜盘; 10/9 WASDE 国内 10/12 响应; 10/27-28 FOMC 国内 T 待官方时间核 (预计 10/29); 脚本 EVENTS 同步",
      "owner": "future-adaption / future-data-sync",
      "due_at": "2026-09-26",
      "required_evidence": ["cal_holiday_0921", "inv_canonical_calendar_1009"],
      "resolution": "pending"
    },
    {
      "item": "9/28-9/30 假期前纪律: 9/28 周末 headline (七日方案被拒/经济 D 日/9/21 再袭船/胡塞袭延布) 首个交易日双向跳空预案; 9/29 郑商所/大商所第二阶段生效 (公告 ±1 日门槛 +0.3、×0.8、公告日核占用); 9/30 长假 T-1 处置 (方向性单边对冲或 ×0.5、#22 跨假期敞口 >30% 减仓) + 俄禁令到期官宣核 + 9 月 PMI; 存量按护栏与止盈机械执行 (账户未知→条件式)",
      "owner": "账户持有人 (执行) / 研究方 (核验)",
      "due_at": "2026-09-30",
      "required_evidence": ["cal_holiday_0921", "czce_margin_0917_full", "russia_diesel_ban_report_0921"],
      "resolution": "pending"
    },
    {
      "item": "① '中断证真' 反向监测 (回改只认官方停火/重开或伊朗许可-收费机制正式落地 + SC 近端 back 回落): 七日方案后续 (美方拒绝后是否重启谈判/分阶段方案官方化)、9/21 两船 (多源✓)、胡塞延布损失核实、沙特管道流量、俄禁令 9/30 官宣; back 方向待快照",
      "owner": "下周 change-analysis",
      "due_at": "2026-10-03",
      "required_evidence": ["iran_7day_plan_rejected_0926", "hormuz_tankers_hit_0921", "houthi_yanbu_0924"],
      "resolution": "pending"
    },
    {
      "item": "黑色负反馈启动裁决: 钢厂第一轮提降 (100-110) 是否于 9/28-9/30 落地 (公开落地记录); 落地→'负反馈启动' 记录 (JM/J 池外无仓; RB 多头评估冻结不变; RB 月差待快照); 未落地→维持 '启动候选'",
      "owner": "研究方",
      "due_at": "2026-10-03",
      "required_evidence": ["coke_cut_prep_0921", "steel_inventory_mysteel_0924"],
      "resolution": "pending"
    },
    {
      "item": "CF-autumn B 触发组装: 快照到位后按 SEASONAL_PLAN_INPUT.md 组装 pre_window_low5 (8/25-8/31)、B-HISTORY (CF2601/2501/2401 秋窗)、MA20/ATR20 并运行 seasonal_plan.py; 登记 rule_version=B-v2.24 的 defined_at/effective_from; 裁定轮储公告 ±3 天条款对滚动轮出的适用口径",
      "owner": "研究方 (计算由 data_pipeline 执行)",
      "due_at": "next_report",
      "required_evidence": ["b_window_calendar_2026", "cotton_reserve_0920"],
      "resolution": "pending"
    },
    {
      "item": "影子计划: 本周未新登记 (最接近成立的两条候选缺 9/24 两腿/单腿结算价, 不以媒体收盘价登记); 上周 SP-2026-09-19-MA-A-short-spread / SP-2026-09-19-MA2701-long-D 由脚本 §5 在下次快照结算 (登记不改写; 有效期 9/25 为休市日, 按 '过入场有效期未成交即作废' 机械处理); 结算结果只用于复评 #5 / #16、D12",
      "owner": "data_pipeline (脚本 §5)",
      "due_at": "next_report",
      "required_evidence": ["shadow_ledger_missing_0926"],
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
  "shadow_plans": [],
  "evidence_corrections": [
    {
      "withdrawn_evidence_id": "inv_canonical_calendar_1009",
      "reason": "canonical v2.27 长假日历 '10/1-10/8、10/9 复盘/首个响应日、低敞口 10/9 复评' 与交易所 2026-09-21 官方通知不符 (实际 10/1-10/7 休市、10/8 恢复交易并恢复夜盘; 另 9/25-9/27 中秋休市、9/24/9/30 无夜盘未入日历); 撤回并以 cal_holiday_0921 替代; 属日历纠错, 非市场变化",
      "affected_checks": [
        {"candidate_id": "2026-09-24|MA2701|directional|long|v2.27", "rule_id": "#16"},
        {"candidate_id": "2026-09-24|MA2701|directional|short|v2.27", "rule_id": "#16"},
        {"candidate_id": "2026-09-24|SR2701|B|long|v2.27", "rule_id": "B_new_open_window"}
      ],
      "recalculation": "completed",
      "recalculation_note": "#16: 事件簇日期改为 10/8 复盘/10/9 WASDE, 簇仍高密度且当周有未落地节点 → fail 不变; SR B: planned_exit 由 9/23 改 9/22 (计入 9/25 休市), 结论同为已过 → no_signal; 低敞口复评日 10/9→10/8"
    },
    {
      "withdrawn_evidence_id": "inv_taicang_2024",
      "reason": "检索命中 '9/25 太仓甲醇 2440-2460、基差 +25~+50' 为 2024-09-25 报价 (URL 编号 24092512); 2026-09-25 为休市日; 与 9/23 太仓 4,090 不符; 未用于任何判定",
      "affected_checks": [
        {"candidate_id": "2026-09-24|MA2701-MA2705|A|short_spread|v2.27", "rule_id": "#5"}
      ],
      "recalculation": "completed",
      "recalculation_note": "#5 依据为 ma_supply_tight_0923 (9/23 太仓 4,090), 撤回项未参与; 结论不变"
    },
    {
      "withdrawn_evidence_id": "inv_sc_0926",
      "reason": "检索命中 '9/26 燃料油 -6% 至 2,666、SC -5% 至 624.3' 为往年读数 (2026-09-26 周六且 9/25-9/27 休市; 与 9/24 收 730 不符); 未用于任何判定",
      "affected_checks": [
        {"candidate_id": "2026-09-24|MA2701|directional|long|v2.27", "rule_id": "MA_oil_guard"}
      ],
      "recalculation": "completed",
      "recalculation_note": "MA_oil_guard 本周 unknown (无快照), 撤回项未参与"
    },
    {
      "withdrawn_evidence_id": "inv_pmi_prior_year",
      "reason": "检索命中 '9 月制造业 PMI 49.8%' 为往年文章; 2026 年 9 月 PMI 定于 2026-09-30 发布, 本周未发布; 未用于任何判定",
      "affected_checks": [
        {"candidate_id": "2026-09-24|RB2701-RB2703|A|unknown|v2.27", "rule_id": "#5"}
      ],
      "recalculation": "completed",
      "recalculation_note": "RB #5 本周 unknown (方向未定), 撤回项未参与"
    }
  ]
}
```

校验命令：`python3 scripts/validate_futures_audit.py --input research/2026-09-26-execution-audit.md`。实际结果见下方"校验记录"。结构校验不检查门覆盖、独立经济因果、确认规则有效性或实际交易许可。

## 校验记录

- 人工语义核对：无快照周的处理——所有依赖快照的门记 unknown（gap.kind=raw_data，归本机运行脚本），不以 9/18 读数或媒体收盘代判定，上周 no_signal 记录不沿用；#3 按模型拆分（MA 多头 D 路线不引用①全局未知；空头按 geopolitical_fade 核①→#26 fail，依据为多源官方/UKMTO 事件而非叙事）；MA 国内路线按协议 4"答不出即不放行"结案为 fail，复活条件写入 unresolved_items；确认定义 v1 冻结仅前瞻（effective_from 2026-09-28 为版本获准采用后首个完整交易日），不回判；#5 子项分列；事件窗口按交易所 9/21 通知纠正的真实日历（10/8 复盘）；#16 依 0.1 低敞口判定当期命中（高密度簇＋交易所公告 ±1）；SR B 以 B-WINDOW 日历直接证据 no_signal，后续门明示未评估；账户 unknown 不推定空仓；invalid 行只出现在 diagnostic_evidence_refs，不进入任何 pass/fail 依据；本周未登记影子计划（缺结算价），缺件已写明。
- 校验器运行结果见下方代码块（由本次运行回填）。

```text
$ python3 scripts/validate_futures_audit.py --input research/2026-09-26-execution-audit.md
{"status": "valid", "scope": "structure_validation_only", "execution_permission": "not_evaluated", "errors": []}
退出码: 0 （2026-09-26 本次运行，现行 v2.27 / origin/main 192b793）
```
