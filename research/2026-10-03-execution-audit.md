# 2026-10-03 期货执行诊断

**结论：截至 2026-10-03（最近已完成行情日 2026-09-30；本周国内期货仅 9/28-9/30 三个交易日，10/1-10/7 国庆休市、10/8 恢复交易），已核研究范围内未形成可执行方案，仍有研究/账户核验缺项；不能据此写"市场没有机会"或"市场建议空仓"。** 本诊断按拟议 **v2.28**（分支 `futures-framework/2026-10-03` 工作区；取代 2026-10-01 关闭未合并的 PR #30 草案）刷新为 `proposed_framework_reassessment`——候选判定与 status 与 v2.27 版相同，仅版本串、日历与状态行引用随新版本刷新，不伪装为历史交易日已生效的规则，数据协议 `FUTURES_DATA_PROTOCOL.md` v2.26。**连续第二周没有新的行情快照**：仓库最新快照仍为 `research/2026-09-19-data-snapshot.txt`（脚本 v1.15、最新行情日 2026-09-18），落后最近已完成交易日**七个交易日**（9/21-9/24、9/28-9/30）→按 0D/协议记 **stale**：全部价差分位、1-5-10td 变化、同期样本验收、ATR 分层/极差、D8 周涨分位、SC2611 结算周涨（9/23→9/30）、MA2701 逐日结算涨跌（#30；媒体口径 9/28 主力日内一度 +5% 为"可能触及"线索）、确认定义 v1 观测值、§5 影子结算均为 **temporary_gap/unknown**，不以媒体收盘推算、不沿用 9/18 读数。公开信息来自 WebSearch，本周部分原文经 WebFetch 核验（TASS/中新网/Mysteel/同花顺/大越/BLS/美联储等），未核项按摘要标注；五条跨年/跨月/口径错误命中（网易焦炭 7 月、ChemNet 伊朗 7 月、西本 2022、24/7 布油 113.96、生意社月均 3,797）已标 invalid。**上周框架更新 PR #30（v2.28 草案）于 2026-10-01 关闭未合并**，canonical 仍为 v2.27（0.0b 日历、交易所风控、AU 卡、负反馈行、MA 卡文本均为已核过期项），本周阶段③重做。实际账户与挂单快照未提供（`actual_position_status=unknown`），全部 `final_lots=null`，总体机会数 `null`。

| 已观察记录 | 本次状态 | 已核否决 / 缺口 |
|---|---|---|
| MA2701−MA2705，A reversion（做空价差，domestic_public） | incomplete | **国内路线论证结案（fail）维持**：本周国内事实（江苏现货 4,575-4,600 升水期货、仓单 5,720 持平、伊朗装置大部分停车摘要）继续指向近月强；复活条件三项（装置复产数值化/到港回升/现货基差走弱）均未被观测（"基差 01+5 走弱"摘要未核不采信、ChemNet 复产为 7 月文章）；**#5(b) 已核反证维持 fail**；确认定义 v1（effective_from 9/28）观测值无快照；港口库存两口径冲突（39.35/-1.85 vs 34.75/+3.51）不入判定；研究筛选/#2/#13 无快照→unknown；计划未形成；账户未核；9/29 起 MA 10%/9%，10/8 回落核 |
| MA2705−MA2709，A（准备对） | incomplete | temporary_gap：连续两周无快照；上一快照样本 24/21/22<33、MA2709 量缺失 |
| RB2701−RB2703，A（黑色唯一结构表达） | incomplete | temporary_gap：无快照（上一实测 56.1 不能沿用）；独立证据已备且已核：Mysteel 9/30 当周总库存 1,462.94（-19.03，去库放缓）、周产量 793.18（+13.50）、消费 -2.8%、建材去库/板材累库；焦炭首轮提降 9/29 落地=负反馈启动确认（背景）；9/23 起 RB 7%/9% |
| RB2703−RB2705，A（准备对） | incomplete | temporary_gap：无快照；RB2705 上一实测 13,672 临界过 #2 |
| MA2701，方向性多头（D 事件冲击） | incomplete | **#16 已核失败**（低敞口继续命中：高密度簇 10/4 OPEC+→10/7 纪要→10/8 复盘多重落地→10/12 WASDE→10/15 CPI→10/16 PPI→10/29 FOMC；交易所公告 ±1（9/29 生效、10/8 回落核）；D12 上一实测）；**新增 geo_quake_day_pm1 已核失败**（俄乌轴 9/30 官宣延期=预设质变形态落地→9/30 与 10/8 能源链方向性单边新开冻结，既有 0.1/2.3 条款机械执行）；周涨护栏/D8/#20/#30/D12 无快照→unknown（#30：9/28 主力日内 +5% 须快照判定）；计划/账户未核 |
| MA2701，方向性空头 | incomplete | **#16、geo_quake_day_pm1、#26 已核失败**（①"中断证真"维持：9/28-10/1 四起袭船多源=要件一再命中；美方 9/30 反提案为谈判 headline、顺序分歧、未官方化→反向要件未出现；要件二 back 方向无快照 unknown；通行量近常态为参考级且口径冲突）；#30/D8/D12 unknown；计划/账户未核 |
| M2701，独立备选 | incomplete（research_only） | 无已许可具体策略（仅观察）；USDA 9/1 大豆库存 3.15 亿蒲（低于预期）、国内豆粕库存 110-111 万吨高位；9/29 起 8%/10%；10/9 WASDE 国内 10/12 响应（前 2 日禁新开按 10/8-10/9 核） |
| SR2701−SR2705，A 远月 | incomplete | temporary_gap：无快照（上一实测 0.0）；SR2701 9/30 早盘 5344、广西现货 5130-5180（-20）；9 月产销未发布；9/29 起 SR 8%/7% |
| SR2701，B 季节做多 | **no_signal** | B-WINDOW SR-summer planned_exit=2026-09-22 已过、window_end=2026-09-30 已到→本窗口结束（直接日历证据；上周已结案，本周为延续记录）；后续门不再评估并明示 |
| CF2701，B 季节做多 | incomplete | B-WINDOW CF-autumn 在窗（planned_exit=10/23；可新开区间 10/8-10/22）；**#5 已核失败**（(b) 供给端反证：新棉集中上市、机采棉收购指数 7.32 元/公斤"稳中回落"、CF 9/29-9/30 连跌 >1%；轮出 9/30 结束仅为供给扰动退出——无独立需求侧支持）；轮储公告 ±3 天条款适用性未定义（轮出已结束，拟按"轮出期外不适用"结案）；B 触发无快照且未组装；9/29 起 CF 9%/8% |

信号席（不进候选 schema）：AU2612——美国 9 月非农 2.9 万/失业率 4.2%→10 月 FOMC 加息概率 17-18%（9/25 71%→一周前约 36%→10/2 17%），但 10Y 10/1 触 5.34%（2002 年来最高）、期限溢价 0.96%、DXY 101.85 年内新高；现货金 10/1 约 4,167→10/2 4,140.19（再创决议后新低）→ fed_state 输入由"加息落地·连续加息指引"转"加息落地·10 月按兵基准×期限溢价紧缩"；D13 复归档条件 A（10/28 按兵）趋近、条件 B（美元连涨中断）反向→不复归档；AU 卡"回吐段"延续但驱动换版；不建仓。SC2611-SC2612——无快照（①要件二 back 方向 unknown）；媒体：9/28 +0.95%、9/29 -3%+、9/30 收 711（-0.82%，日内低 674.70/-5%）、夜盘 705.2；闭市期布油 9/29 96.16→10/2 102.70-103.37（+6-7%）=10/8 向上跳空风险源；SC2611 结算周涨 9/23→9/30 unknown；剩余 16 td。

**上期预备观察项处置（诊断口径）**：①快照补跑（due 9/28）**未完成**，连续第二周缺快照，due 改 10/8；②①反向监测——要件一四次再命中、反提案未官方化→"中断证真"维持，#26 fail 延续；③假期前纪律——9/28-9/30 已过，9/30 俄禁令官宣=俄乌轴质变日（±1 冻结延至 10/8）、9/30 PMI 50.1 已发布、T-1 处置为条件式（账户未知）；④黑色负反馈——首轮提降 9/29 发起/10/1 执行→"启动确认"（RB 背景，无执行动作）；⑤MA 研究记录——v1 观测值 unknown、复活条件均未观测、港口库存由 missing 转 conflicting；⑥利率链——10 月概率坍塌至 17-18%、10Y/DXY 新高、金 4,140（状态行换版，D13 不复归档）；⑦②''——PMI 50.1 回扩张但成交 1.45 万亿、9 月日均 1.83 万亿→未修复维持；⑧SR 9 月产销未发布/CF 轮出 9/30 结束、B 触发组装待快照；⑨多晶硅 9 月排产未减、无第三份文件→③门维持；⑩LC 冻结维持（9/15 仓单 47,164 手）；另：**上周"日历纠错写入 canonical（due 9/26）"因 PR #30 关闭未合并→未落地，本周阶段③重做**。

**证据纠错（EVIDENCE_CORRECTIONS）**：五条无效命中（网易焦炭 2026-07-22、ChemNet 伊朗复产 2026-07-09、西本 2022-09-30、24/7 布油 113.96、生意社月均 3,797）全部只入 diagnostic，不进入任何 pass/fail 依据；canonical 日历错误（inv_canonical_calendar_1009）继续以交易所官方通知替代，#16/SR B 重算后结论不变（recalculation=completed）。三项搜索摘要未核项（钢厂盈利率 6.93%、9 艘甲醇船 SDN、太仓基差 01+5 走弱）标 missing 不采信。

旧输出失效项：上周"9/28 前补跑快照"未完成，9/18 读数现落后 7 个交易日；"俄禁令报道级/11 月 conflicting"由 9/30 官宣解除；"提降准备发起"→"启动确认"；"港口库存三周缺（missing）"→"数值可得但口径冲突（conflicting）"；"10 月 FOMC 国内 T 预计 10/29"→官方日历已核（CPI 10/15、PPI 10/16、FOMC T 10/29、WASDE 10/12、纪要北京 10/8 02:00）；fed_state"71-73%/连续加息定价加深"→"17-18%/期限溢价紧缩"；上上周影子计划有效期已过、预期作废待 §5 确认。

风险容量只引用 canonical Step5 与 `scripts/futures_risk.py`；配置=单笔上限 5,250、常规组合上限 5,250、当前低敞口组合上限 5,000（高密度簇＋交易所公告 ±1＋俄乌轴质变日 ±1＋D12 高波层（上一实测）条款命中）；实际净值、存量风险、挂单预留、保证金未核验，未对任何候选运行真实容量计算。现有材料没有完整历史候选账，不能判断连续空仓与机会成本，也不能把本周结果归因于 5,000 元上限。

**影子计划**：本周**未新登记**——最接近成立的两条候选（MA A 做空价差、MA2701 突破多）均缺 9/30 两腿/单腿结算价（连续两周无快照），按 4.4 不以媒体收盘价登记；上上周 SP-2026-09-19-* 有效期已过，由脚本 §5 在下次快照按"过入场有效期未成交即作废"机械确认（登记不改写）。缺件写入 `unresolved_items`。

## 结构化记录（schema 3）

```json
{
  "audit_schema_version": 3,
  "as_of_date": "2026-10-03",
  "research_mode": "public_data",
  "assessment_scope": "proposed_framework_reassessment",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v2.28",
    "revision": "working_tree (futures-framework/2026-10-03); 基于 main 8f68043 v2.27; 本版吸收并取代 2026-10-01 关闭未合并的 PR #30 草案",
    "data_script_version": "v1.17 (分支 futures-framework/2026-10-03; EVENTS 配置层随动, 无算法改动, 未经线上实测; 本周未运行). 最新快照 research/2026-09-19-data-snapshot.txt (v1.15, 最新行情日 2026-09-18) 落后 2026-09-30 七个交易日 → stale, 仅作对照/diagnostic",
    "rule_changes_affecting_candidates": "规则本体零改动 (canonical v2.27; 上周 v2.28 草案 PR #30 关闭未合并, 其内容为状态行/日历纠错, 不改门/参数). 本周判定差异全部来自证据状态: (1) 连续第二周无快照 → 分位/样本/ATR/D8/周涨/#30/v1 观测/影子结算 unknown (落后 7 td); (2) 俄乌轴 9/30 官宣延期 = 预设质变形态落地 → 新增检查 geo_quake_day_pm1 (0.1/2.3 既有条款机械执行, 9/30 与 10/8 能源链方向性单边新开冻结); (3) ①维持中断证真 (要件一 9/28-10/1 四起袭船; 美方反提案未官方化) → #26 fail 延续; (4) 焦炭首轮提降 9/29 落地 → 1.4 负反馈 '启动确认' (RB 背景); (5) 甲醇港口库存数值可得但两口径冲突 → 仍不作判定依据; MA 国内路线复活条件均未观测 → 结案维持; (6) 10 月官方日历 (CPI 10/15、PPI 10/16、FOMC T 10/29、WASDE 10/12) 已核, 事件簇按此刷新; (7) SR-summer 窗口 9/30 结束 → no_signal 结案延续; CF-autumn 轮出 9/30 结束, 可新开区间 10/8-10/22; (8) 本次为拟议 v2.28 (工作区) 的重评: 候选判定与 status 与 current_framework 版相同, 仅框架/脚本版本串、日历与状态行引用随新版本刷新, 不伪装为历史交易日已生效的规则"
  },
  "snapshot": {
    "market_trade_date": "2026-09-30",
    "market_captured_at": null,
    "source_artifacts": [
      "research/2026-10-03-market-research.md (WebSearch + 部分原文 WebFetch 核验, 2026-10-03)",
      "research/2026-09-19-data-snapshot.txt (stale: 脚本 v1.15, 最新行情日 2026-09-18; 落后 7 个交易日; 仅作对照)",
      "交易所 2026-09-17/18/21 通知 (郑商所/大商所/上期所/上期能源; 多源转引) + 郑商所节后回落条件 (财联社)",
      "framework/futures_framework.md v2.27 / framework/FUTURES_DATA_PROTOCOL.md v2.26 / projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md",
      "GitHub PR #30 (2026-10-01 关闭未合并) 元数据",
      "BLS/美联储/USDA 10 月官方日历 (已核)",
      "scripts/seasonal_plan.py 未运行 (CF B-HISTORY 输入未组装); scripts/futures_risk.py 未运行 (无完整计划与账户); scripts/future_data.py 本周与上周均未运行 (需用户本机 Tushare)"
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
      "source": "canonical 0)/Step5; 低敞口=高密度簇 (10/4 OPEC+ 闭市期/10/7 纪要/10/8 复盘多重落地/10/12 WASDE/10/15 CPI/10/16 PPI/10/29 FOMC) + 交易所公告 ±1 日 (9/29 生效、10/8 回落核) + 俄乌轴质变日 ±1 (9/30、10/8) + D12 高波层 (上一实测 82.9, 连续两周无刷新) 条款命中; 实际净值/占用未核"
    },
    "invalidated_legacy_outputs": [
      "上周 (2026-09-26) 诊断 unresolved_items '日历纠错写入 canonical (due 2026-09-26)' 与 '脚本 EVENTS 同步': PR #30 2026-10-01 关闭未合并 → 未落地, 本周阶段③重做; canonical 0.0b/1.4 仍写 '10/1-10/8、10/9 复盘', 0.1 交易所风控仍 '甲醇单品种/INE 阴性', AU 卡仍 '预期兑现型反弹评估', 1.4 负反馈仍 '临界', MA 卡仍 draft1——全部为已核过期文本",
      "上周 '首要待办: 9/28 前补跑快照 (v1.16)' 未完成 → 连续第二周无快照; 9/18 读数现落后 7 个交易日; 上周 '9/24 口径剩余 td' 由 9/30 口径替代",
      "上周 '俄禁令延至 10/31 报道级 (另有 11 月 conflicting)' → 9/30 官宣延至 10/31 (TASS 原文), conflicting 解除; 预设质变形态落地",
      "上周 '钢厂第一轮提降准备发起 (100-110)' → 9/29 发起/10/1 执行 (湿熄 -100/干熄 -110), 负反馈由 '发起级' 转 '启动确认'",
      "上周 '甲醇港口库存连续第三周两入口阴性 (missing)' → 本周数值可得但两口径冲突 (conflicting); 降级为增强级第二指标维持",
      "上周 '10 月 FOMC 国内 T 预计 10/29' → 官方日历已核 T=10/29 (T-3 10/26, T-1 10/28, T+1 10/30); CPI 10/15、PPI 10/16、WASDE 10/12、纪要北京 10/8 02:00 已核",
      "上周 fed_state 读数 '10 月 71-73%、12 月 95%' → 10/2 17-18%; AU 卡 '连续加息定价加深' 驱动归因换版为 '期限溢价/美元' (价格方向延续: 4,244→4,140)",
      "上周 SR B 'planned_exit 9/22 已过' → 窗口 9/30 结束 (结案延续); CF B 'planned_exit 10/23' 维持, 轮出 9/30 结束",
      "上上周影子计划 SP-2026-09-19-* 有效期 9/25 (实际 9/24) 已过且 §5 未运行 → 预期作废, 待快照 §5 机械确认; 本周仍未新登记 (缺 9/30 结算价)"
    ]
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "MA2701-MA2705 A reversion domestic_public: #1/国内路线论证 (结案 fail 维持)/确认定义 (v1 冻结, 观测 unknown)/#5/交易所公告; 研究筛选/#2/#13 因无快照 unknown",
      "MA2705-MA2709 A 准备对: 缺口登记 (连续两周无快照)",
      "RB2701-RB2703 与 RB2703-RB2705 A: 研究筛选 unknown (无快照); 独立产业证据 (Mysteel 9/30 当周, 已核) 已备",
      "MA2701 方向性多空: #1/#16/geo_quake_day_pm1/#26/交易所公告已核; 周涨护栏/D8/#20/#30/D12 无快照 unknown",
      "SR2701-SR2705 A: 研究筛选 unknown (无快照)",
      "SR2701 B: 窗口 9/30 结束 → no_signal (结案延续)",
      "CF2701 B: B-WINDOW 日历筛选 pass、#5 独立产业事实 fail、轮储条款/B 触发/D8 缺口",
      "M2701: research_only 登记 (无已许可策略)"
    ],
    "missing_scope": [
      "本周行情快照 (scripts/future_data.py v1.16, 需用户本机 TUSHARE_TOKEN; 连续第二周缺): 分位/价差变化/样本验收/ATR 分层与极差/D8/SC2611 结算周涨 (9/23→9/30)/MA2701 9/21-9/30 逐日结算 (#30)/v1 观测值/§5 影子结算",
      "实际账户/持仓/挂单/保证金/费用",
      "甲醇港口库存口径统一 (同花顺 iNews 39.35/-1.85 vs 大越 华东华南 34.75/+3.51)",
      "CF B 的 pre_window_low5 (8/25-8/31)、B-HISTORY 三年同窗、Entry/SL/TP1 (seasonal_plan.py 未运行; 且需快照 MA20/ATR20)",
      "SC 逐日结算 (护栏两端; 9/30 收 711/夜盘 705.2 为收盘口径)",
      "10/4 OPEC+ 结果与 10/7 联储纪要 (闭市期待落地)",
      "9/30 日盘甲醇/螺纹/棉花/豆粕收盘价 (媒体仅早盘/夜盘; 结算须快照)"
    ],
    "research_only_scope": [
      "geopolitical_fade / 中断因果模型 (①中断证真维持; 美方反提案未官方化; 复活须按 v2.26 新要件重定义)",
      "M2701 无已许可具体策略 (仅观察)"
    ],
    "signal_observations": [
      "AU2612: 美国 9 月非农 2.9 万/失业率 4.2% → 10 月 FOMC 加息概率 17-18% (9/25 71% → 一周前约 36% → 10/2 17%), 维持约 81%; 但 10Y 10/1 触 5.34% (2002 年来高)、10/2 5.28%, 期限溢价 0.96% (2011 年来高), DXY 101.85 年内新高; 现货金 10/1 约 4,167 → 10/2 4,140.19 (再创决议后新低); 国内 9/29 沪金跌超 1%; fed_state 输入由 '加息落地·连续加息指引' 转 '加息落地·10 月按兵基准 × 期限溢价紧缩'; D13 复归档条件 A (10/28 按兵) 趋近、条件 B (美元连涨中断) 反向 → 不复归档; AU 卡 '回吐段' 延续但驱动换版; 9/23 起 AU 16%/18%, 10/8 回落核; 不建仓; 剩余 48 td",
      "SC2611-SC2612: 无快照 → ①要件二 back 方向 unknown (上一实测 9/18 +43.5/分位 100); 媒体: 9/28 +0.95% (731.70)、9/29 -3%+、9/30 收 711.00 (-0.82%; 日内低 674.70/-5%)、夜盘 705.2 (-1.63%); 闭市期布油 9/29 96.16 (12 月结算) → 10/2 102.70-103.37 (+6-7%) = 10/8 向上跳空风险来源; SC2611 结算周涨 9/23→9/30 unknown; 9/23 起 SC2611 18%/20%, 10/8 回落核; 剩余 16 td (注 c 不受 #1); 下次主力换月 → SC2612-SC2701"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable"
  },
  "evidence": [
    {
      "evidence_id": "cal_holiday_0921",
      "metric": "交易所 2026 年中秋节/国庆节休市与恢复安排",
      "value": "9/24 晚无夜盘; 9/25-9/27 休市; 9/28-9/30 开市; 9/30 晚无夜盘; 10/1-10/7 休市; 10/8 (周四) 08:55 集合竞价恢复交易、当晚恢复夜盘; 本周实际交易日 9/21-9/24; 本周实际交易日 9/28-9/30 (9/30 晚无夜盘); 10/8 恢复交易后保证金/涨跌停自品种持仓量最大合约未出现单边市的首个交易日结算起回落 (郑商所口径, 其他交易所同类条件)",
      "unit": "日期",
      "observation_date": "2026-09-21",
      "published_at": "2026-09-21",
      "source_url_or_file": "https://www.shfe.com.cn/publicnotice/notice/202609/t20260921_833503.html; https://news.qq.com/rain/a/20260921A0BE7900; https://finance.sina.com.cn/roll/2026-09-22/doc-inissyqx6834436.shtml; https://www.cls.cn/detail/2486403",
      "original_source": "上期所/上期能源/郑商所/大商所 2026-09-21 通知 (多源转引)",
      "price_basis": null,
      "comparison_basis": "canonical v2.27 1.4/0.0b 原写 10/1-10/8、10/9 复盘",
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
      "evidence_id": "ma_confirm_def_v1",
      "metric": "MA2701-MA2705 做空价差 价格确认定义 (冻结版)",
      "value": "rule_version A-MA-2701-2705-v1; S=MA2701-MA2705 两腿 settle 之差; 触发=S 连续 2 个交易日 settle 低于 [前 10 个交易日 S 最高值 − 0.65×MA2701 ATR20 (脚本 §2a 当期值)], 且同期 MA2701 settle 未创近 20 日新高 (H20, 脚本 §2b); defined_at 2026-09-26T21:00:00+08:00; effective_from 2026-09-28; 只作前瞻, 不回判 9/21-9/24; 替换 draft1 (其第二条款引用已退出的 MA2610); 2026-09-28 起生效, 9/28-9/30 三个交易日观测值无快照 → unknown",
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
      "evidence_id": "b_window_calendar_2026",
      "metric": "B-WINDOW 真实交易日映射 (canonical 1.6)",
      "value": "SR-summer: window_end=2026-09-30 (郑商所交易日); planned_exit=window_end 前第 5 个交易日=2026-09-22 (9/29、9/28、9/24、9/23、9/22; 9/25-9/27 休市); 审计交易日 9/30 = window_end, 窗口已结束, 不可新开. CF-autumn: window_end=2026-10-30; planned_exit=2026-10-23 (10/29、10/28、10/27、10/26、10/23); 9/30 < planned_exit → 可新开区间内 (剩余可新开交易日 10/8-10/22)",
      "unit": "日期",
      "observation_date": "2026-09-30",
      "published_at": "2026-10-03",
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
      "evidence_id": "inv_canonical_calendar_1009",
      "metric": "canonical v2.27 长假日历文本 (已撤回)",
      "value": "'国庆长假 10/1-10/8 (9/30=T-1; 10/9 复盘/首个响应日; 低敞口条款 10/9 复评; 10/4 OPEC+ 国内首个响应日 10/9)'; 未列 9/25-9/27 中秋休市; 上周 PR #30 (v2.28 草案) 已纠正但 2026-10-01 关闭未合并 → canonical 文本错误仍在",
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
      "evidence_id": "pr30_closed_unmerged",
      "metric": "canonical 版本状态: 上周框架更新 PR #30 的处置",
      "value": "PR #30 '期货框架更新 2026-09-26：light' (分支 futures-framework/2026-09-26, head 3798726, v2.28 草案: 休市日历纠错/交易所风控全池/负反馈启动/MA 结案+v1/无快照标注/脚本 v1.17/compact v2.28) 于 2026-10-01T07:01Z 关闭、未合并 (main 不含 c2d4105; 框架仍 v2.27, 脚本仍 v1.16); 无关闭说明评论",
      "unit": "状态",
      "observation_date": "2026-10-01",
      "published_at": "2026-10-01",
      "source_url_or_file": "https://github.com/royzxq/investment_research_methods/pull/30; git log main..pr30-futures-2026-09-26",
      "original_source": "GitHub PR 元数据 + 本地 git",
      "price_basis": null,
      "comparison_basis": null,
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "td_calendar_0930",
      "metric": "池内合约剩余交易日 (9/30 口径)",
      "value": "MA2701 69 / MA2705 148 / MA2709 234 / RB2701 70 / RB2703 106 / RB2705 149 / M2701 70 / SR2701 69 / SR2705 148 / CF2701 69 / AU2612 48 / SC2611 16 / SC2612 37",
      "unit": "交易日",
      "observation_date": "2026-09-30",
      "published_at": "2026-10-03",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt §1/§2b (9/18 口径) 减 9/21-9/24、9/28-9/30 七个真实交易日 (cal_holiday_0921)",
      "original_source": "scripts/future_data.py v1.15 trade_cal 剩余 td + 交易所日历 (确定性日历运算, 非行情推算)",
      "price_basis": null,
      "comparison_basis": "0.3#1 (≥20 td; 方向性单边 ≥20+持仓上限)",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "russia_diesel_ban_official_0930",
      "metric": "俄乌轴质变: 俄政府官宣延长生产商柴油/船燃/瓦斯油出口禁令",
      "value": "2026-09-30 俄政府签署法令: 直接生产商的柴油、船用燃料、瓦斯油出口禁令延至 2026-10-31 (理由: 秋收期国内燃料市场稳定); 非生产商/汽油全面禁令至 2027-01-31 不变 → 1.4 俄乌轴行预设 '9-30 延期 (升级)' 质变形态官宣落地, 官宣日 9/30 = 国内 T-1 交易日; ±1 的下一交易日 = 10/8",
      "unit": "政策",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://tass.com/economy/2195135; https://www.themoscowtimes.com/2026/09/30/russia-extends-diesel-export-ban-until-end-of-october-a93823; https://www.aa.com.tr/en/energy/oil/russia-extends-ban-on-diesel-marine-fuel-exports-by-producers-until-oct-31/59955",
      "original_source": "俄罗斯政府 (TASS 原文已核; Moscow Times/AA 多源)",
      "price_basis": null,
      "comparison_basis": "上周 '延至 10/31 报道级 (另有 11 月 conflicting)'; 9/30 到期",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "iran_counterproposal_0930",
      "metric": "①反向要件核对: 美方反提案与谈判状态",
      "value": "9/30 伊外长 Araghchi 经卡塔尔收到美方反提案 (七日 '建立信任期' 回到 6 月谅解备忘录增强版, 含伊核具体步骤; 双方步骤大体一致但顺序分歧: 伊方停火→解封→解制裁→解冻→重开海峡→核谈, 美方要求先核让步); Trump: 'it is not the deal that I want to make' / 'I offered them NOTHING!'; 海峡未官方重开、美方海上封锁未解 → 官方停火/重开或许可-收费机制正式落地未出现",
      "unit": "事件",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://www.yahoo.com/news/politics/articles/iran-considers-us-counterproposal-ceasefire-200020811.html; https://www.cnbc.com/2026/09/30/us-iran-war-trump-hormuz.html; https://fortune.com/2026/09/30/trump-iran-hormuz-strait-talks/",
      "original_source": "彭博 (经 Yahoo, 原文已核) / CNBC / Fortune 多源",
      "price_basis": null,
      "comparison_basis": "1.7① 反向质变要件 = 官方停火/重开或许可-收费机制正式落地 + SC 近端 back 回落",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "hormuz_tankers_hit_0928_1001",
      "metric": "①要件一 '再袭船' 本周读数",
      "value": "9/28 夜一船遭不明射弹起火 (已扑灭); 9/29 三艘油轮遭不明射弹 (VLCC Mersin Prosperity 299,319 dwt、Sinbad 115,949 dwt、Al Funtas/Al Ruwais; AIS 关闭航行); 10/1 科威特旗 VLCC Kazimah III 遭击起火; 伊朗海峡管理局称被击三船 '在其不合规名单上'; IRGC 准将 Mohebbi: 未经许可通行 '将被打击或触雷'; UKMTO 称信息来自已核来源",
      "unit": "事件",
      "observation_date": "2026-10-01",
      "published_at": "2026-10-01",
      "source_url_or_file": "https://tass.com/world/2195113; https://www.seatrade-maritime.com/security/four-vessels-struck-in-hormuz-in-24-hours; https://maritime-executive.com/article/three-vessels-struck-in-strait-of-hormuz-as-iran-s-grip-loosens; https://www.seatrade-maritime.com/security/tanker-catches-fire-after-first-hormuz-attack-in-october",
      "original_source": "UKMTO (TASS/Seatrade/Maritime Executive 多源转引; Maritime Executive 原文已核)",
      "price_basis": null,
      "comparison_basis": "上周 9/21 两船 (多源)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "hormuz_traffic_conflicting_0930",
      "metric": "霍尔木兹通行量 (参考级, 口径冲突)",
      "value": "Windward: 9/29 17 艘、9/28 16 艘 AIS 可见通行; Kpler: 9 月 >16.5 百万桶/日 (含海上过驳); JPMorgan: 海湾日流量 17.5 百万桶 ≈ 战前 98%; LNG 9 月 19-21 船 (≈战前 20%); IMF PortWatch 9/27 1 艘 (多日滞后)",
      "unit": "艘/日, 百万桶/日",
      "observation_date": "2026-09-30",
      "published_at": "2026-10-03",
      "source_url_or_file": "https://maritime-executive.com/article/three-vessels-struck-in-strait-of-hormuz-as-iran-s-grip-loosens; https://rigzone.com/news/wire/getting_oil_through_hormuz_is_a_risky_job-03-oct-2026-184762-article; https://247wallst.com/investing/2026/10/03/lng-shipments-through-hormuz-just-hit-a-7-month-high-why-the-global-energy-crisis-is-far-from-over; https://straits.live/briefs/2026-10-01",
      "original_source": "Windward / Kpler / JPMorgan / IMF PortWatch (多源, 对象与口径不同)",
      "price_basis": null,
      "comparison_basis": "v2.26: 通行量为参考级, 不进①要件",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "brent_0929_1002",
      "metric": "布伦特/WTI (闭市期重定价)",
      "value": "9/29 结算: WTI 11 月 89.38 (-3.5%)、布伦特 12 月 96.16 (-1.7%); 10/1 布油 102.38 (24h +4.81%); 10/2 布油 102.70 (TE) / 103.37 (Fortune 美东 9:15); WTI 10/3 行情条 91.11 → 国内闭市期布油 +6-7%",
      "unit": "美元/桶",
      "observation_date": "2026-10-02",
      "published_at": "2026-10-02",
      "source_url_or_file": "http://news.10jqka.com.cn/20260930/c680386685.shtml; https://tradingeconomics.com/commodity/brent-crude-oil; https://fortune.com/article/price-of-oil-10-02-2026/; https://straits.live/briefs/2026-10-01",
      "original_source": "路透 (经同花顺) / TradingEconomics / Fortune (已核)",
      "price_basis": "结算 (9/29) / 盘中水平 (10/1-10/2)",
      "comparison_basis": "9/25 105.11; 国内 SC 9/30 夜盘 705.2",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sc_daily_media_0928_0930",
      "metric": "SC 主力逐日涨跌 (媒体收盘/日内口径, 非结算)",
      "value": "9/28 日盘 +0.95% 报 731.70; 9/29 跌超 3%; 9/30 日盘收 711.00 (-5.90, -0.82%; 高 716.70 / 低 674.70, 日内一度 -5% 报 681); 9/30 夜盘 -1.63% 报 705.2",
      "unit": "%, 元/桶",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://www.sohu.com/a/1082254511_121157270; http://news.10jqka.com.cn/20260930/c680386685.shtml; https://finance.eastmoney.com/a/202609303887675792.html; https://m.stnn.cc/detail/6abc33f00b05bc6162866ad4.html",
      "original_source": "搜狐/同花顺/东方财富/星岛 收盘转引",
      "price_basis": "close/日内 (非 settle)",
      "comparison_basis": "9/24 收 730; SC2611 结算周涨 9/23→9/30 须两端 settle, 本项不作命中判定",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_daily_media_0928_0930",
      "metric": "甲醇主力逐日涨跌 (媒体收盘/日内口径)",
      "value": "9/28 日盘主力日内 +4% (3,228) → 一度 +5% (3,261); 9/28 夜盘 +3.90%; 9/29 收盘涨超 3%; 9/30 早盘涨超 1% (日盘收盘未取得); 判定腿 MA2701 逐日结算未取得",
      "unit": "%, 元/吨",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://m.stnn.cc/detail/6ab9c4080b05bc61627ffc60.html; https://www.sohu.com/a/1081651305_121400326; https://www.jiemian.com/article/15147418.html; https://24topnews.com/news/market/china-chemical-futures-surge-on-sep-29-key-contracts-up-over-3-af5d77d0; https://finance.eastmoney.com/a/202609303887558762.html",
      "original_source": "星岛/搜狐/界面 (已核)/东方财富 收盘转引",
      "price_basis": "close/日内 (非 settle)",
      "comparison_basis": "#30 须 MA2701 settle/pre_settle; 9/28 日内 +5% 为 '可能触及' 线索, 不作判定",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_spot_0928_0929",
      "metric": "甲醇国内独立产业事实 (现货/升水/仓单)",
      "value": "9/28 江苏 4,575 (+320)、华南 4,500 (+140)、福建 4,475 (+300)、山东 3,800 (0)、内蒙 3,450 (+107.5); 9/29 江苏现货 4,600, 现货升水期货; 郑商所甲醇仓单 9/30 5,720 张 (持平); 大越: 主力持仓净空、空增",
      "unit": "元/吨, 张",
      "observation_date": "2026-09-29",
      "published_at": "2026-09-29",
      "source_url_or_file": "http://news.10jqka.com.cn/20260928/c680323776.shtml; https://www.sohu.com/a/1082065231_121123900; http://news.10jqka.com.cn/20260930/c680412313.shtml",
      "original_source": "同花顺 iFInD (已核) / 大越期货 9/29 早报 (已核) / 郑商所仓单 (同花顺转引)",
      "price_basis": "现货报价",
      "comparison_basis": "9/23 太仓 4,090; 做空价差路线需 '海峡未缓和时仍支持收敛的独立国内变化'",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_port_inventory_conflict_0930",
      "metric": "甲醇港口库存 (两口径冲突)",
      "value": "口径 A (同花顺 iNews, 9/30 当周): 港口库存 39.35 万吨, 周 -1.85 (-4.49%), 月 -25.4 (-39.23%), 2023-10 以来最低; 口径 B (大越 9/29 早报): 华东+华南港口甲醇社会库存 34.75 万吨, 较上周期累库 +3.51 万吨 → 对象/口径不同且方向相反",
      "unit": "万吨",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "http://news.10jqka.com.cn/20260930/c680404979.shtml; https://www.sohu.com/a/1082065231_121123900",
      "original_source": "同花顺 iNews / 大越期货 (均已核; 原始统计机构未在页面标明)",
      "price_basis": null,
      "comparison_basis": "上周连续第三周两入口阴性; 已降为增强级第二指标",
      "role": "optional_context",
      "quality": "conflicting",
      "time_scope": "current"
    },
    {
      "evidence_id": "snap_0919_stale",
      "metric": "上一快照读数 (对照用, 已过期 7 个交易日)",
      "value": "MA2701-MA2705 +312/分位 100/样本 41/41/41; RB2701-RB2703 -8/56.1; SR2701-SR2705 -78/0.0; SC2611-SC2612 +43.5/100 (1td -9.7); MA2705-MA2709 +99/100 但样本 24/21/22 且 MA2709 量缺失; RB2703-RB2705 -8/61.8 (RB2705 13,672); SC2611 结算周涨 9/11→9/18 -0.30%; D8 MA 上尾 66.7/SR 下尾 94.1/CF 下尾 98.0; ATR250 分位 MA 82.9/M 99.4/RB 72.7/SR 70.1/CF 22.0/AU 33.0, 极差 77.4; 20 日均量 MA2701 540,023/MA2705 19,628/RB2701 669,156/RB2703 27,445/M2701 1,600,298/SR2701 470,759/SR2705 40,611/CF2701 347,245/AU2612 80,370",
      "unit": "元/吨, 分位, %, 手",
      "observation_date": "2026-09-18",
      "published_at": "2026-09-19",
      "source_url_or_file": "research/2026-09-19-data-snapshot.txt",
      "original_source": "scripts/future_data.py v1.15 (Tushare)",
      "price_basis": "settle",
      "comparison_basis": "最近已完成交易日 2026-09-30 (落后 7 个交易日: 9/21-9/24、9/28-9/30)",
      "role": "required_model",
      "quality": "stale",
      "time_scope": "historical"
    },
    {
      "evidence_id": "ma2701_daily_settle_missing_1003",
      "metric": "MA2701 逐日 settle/pre_settle 涨跌 (#30 判定腿, 9/21-9/30)",
      "value": null,
      "unit": "%",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "scripts/future_data.py v1.16 §2b.1 (连续两周未运行)",
      "original_source": "未取得",
      "price_basis": "settle/pre_settle",
      "comparison_basis": "≥5% 触发 3 交易日顺向新开冻结; 9/28 主力日内 +5% 为线索",
      "role": "required_model",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "shadow_ledger_missing_1003",
      "metric": "影子账本 §5 结算 (SP-2026-09-19-MA-A-short-spread / SP-2026-09-19-MA2701-long-D)",
      "value": null,
      "unit": "元, R",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "scripts/future_data.py v1.16 §5 (连续两周未运行)",
      "original_source": "未取得",
      "price_basis": "settle",
      "comparison_basis": "登记 2026-09-19; 有效期 2026-09-25 (实际最后可入场日 9/24, 已过 → 预期作废)",
      "role": "optional_context",
      "quality": "missing",
      "time_scope": "current"
    },
    {
      "evidence_id": "us_nfp_fedwatch_1002",
      "metric": "美国 9 月非农 / 10 月 FOMC 加息概率",
      "value": "新增就业 2.9 万 (远低预期), 失业率 4.2%, 7-8 月合计下修 6 万; CME FedWatch 10/27-28 加息概率 17-18% (时间序列: 9/25 71% → 一周前约 36% → 10/2 17%), 维持 3.75-4.00% 约 81%; 9/30 PCE 偏冷先行压低概率",
      "unit": "千人, %",
      "observation_date": "2026-10-02",
      "published_at": "2026-10-02",
      "source_url_or_file": "https://cnbc.com/2026/10/02/fed-rate-hike-odds-decline-after-september-jobs-report.html; https://invezz.com/en-ae/news/2026/10/02/us-jobs-report-payrolls-rise-just-29000-fed-october-hike-bets-fade/; https://babypips.com/news/headline-us-jobs-report-september-2026-payrolls-miss-fed-hike-odds",
      "original_source": "BLS / CME FedWatch (CNBC/Invezz/Babypips 多源同口径; 原文 403 未核)",
      "price_basis": null,
      "comparison_basis": "上周 10 月 71-73%、12 月 95%",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "us_10y_dxy_1002",
      "metric": "10Y 美债 / 美元指数 / 期限溢价",
      "value": "10Y 10/1 触 5.34% (2002 年来最高)、10/2 5.28%; DXY 10/1-10/2 约 101.85 (年内新高); 10Y 期限溢价估计 0.96% (2011-02 以来最高); 国会通过 CR 至 12/11, 10/1 停摆避免",
      "unit": "%, 点",
      "observation_date": "2026-10-02",
      "published_at": "2026-10-02",
      "source_url_or_file": "https://www.investing.com/news/economy-news/10-year-us-treasury-yield-hits-highest-since-2002-4926542; https://qz.com/us-treasury-yield-highest-since-2002-bond-selloff-100126; https://tradingeconomics.com/united-states/government-bond-yield; https://www.fxempire.com/forecasts/article/gold-forecast-the-usd-index-soars-to-new-2026-highs-1634558",
      "original_source": "路透 (经 Investing/Quartz) / TradingEconomics / FXEmpire",
      "price_basis": null,
      "comparison_basis": "上周 10Y 5.23%、DXY 101.4",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "gold_1001_1002",
      "metric": "现货金/银",
      "value": "10/1 金约 4,167 (USAGOLD 标题 '收益率上行压制'); 10/2 4,140.19 (-0.90% d/d), 再创决议后新低 (4,244 → 4,140); 国内 9/29 沪金跌超 1%、沪银/铂跌超 2%; <4000 待命位未触及",
      "unit": "美元/盎司",
      "observation_date": "2026-10-02",
      "published_at": "2026-10-02",
      "source_url_or_file": "https://tradingeconomics.com/commodity/gold; https://www.usagold.com/daily-precious-metals-market-report-october-1-2026/; https://www.sohu.com/a/1082254511_121157270",
      "original_source": "TradingEconomics / USAGOLD (403, 标题读数) / 搜狐 9/29 收盘",
      "price_basis": "spot",
      "comparison_basis": "上周 4,244 低点 / 4,280-4,310",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "cn_pmi_sep_0930",
      "metric": "国家统计局 2026 年 9 月制造业 PMI",
      "value": "制造业 PMI 50.1 (+0.3, 连续两月 <50 后回扩张); 生产 51.7 (+1.3); 新订单 50.5 (-0.1); 新出口订单 50.0 (-0.1); 主要原材料购进价格 60.8 (+4.2); 出厂价格 54.0 (+3.6); 大型 50.6 / 中型 49.7 / 小型 48.9",
      "unit": "%",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://www.chinanews.com.cn/cj/2026/09-30/10706023.shtml; https://www.chinanews.com.cn/cj/2026/09-30/10706141.shtml",
      "original_source": "国家统计局/中采联 (中新网转引, 原文已核)",
      "price_basis": null,
      "comparison_basis": "8 月 49.8",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "a_share_0930",
      "metric": "A 股 9/30 与 9 月 (②'' 背景)",
      "value": "9/30 沪指 3842.19 (+0.31%), 深成/创业板微跌; 两市成交约 1.45 万亿 (+约 300 亿 d/d); 9 月日均成交 1.83 万亿 (6 月 3.13 → 7 月 2.70 → 8 月 2.25 → 9 月 1.83); 三季度科创 50 跌超三成; 两市融资余额 9/29 25,714.7 亿 (-20.48 d/d; 9/28 -259.91)",
      "unit": "点, 亿元",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://finance.sina.cn/2026-09-30/detail-initqzkv6906973.d.html; https://m.21jingji.com/article/20260930/herald/64116cfe58db1e16d77b22fe7b3ac6ed.html; https://www.sohu.com/a/1082534191_121400326",
      "original_source": "新浪 / 21 财经 / 搜狐 (融资余额两市口径, 与上周 '两融 26,550 沪深京' 不同源)",
      "price_basis": "close",
      "comparison_basis": "上周沪指 3888.37, 成交 1.67-1.76 万亿",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "steel_inventory_mysteel_0930",
      "metric": "Mysteel 五大品种周度产量与库存 (9/30 当周)",
      "value": "周产量 793.18 万吨 (+13.50, +1.7%); 厂库 384.54 (+1.73); 社库 1,078.40 (-20.76); 总库存 1,462.94 (-19.03, -1.28%; 建材 -28.98/-4.1%, 板材 +9.95/+1.28%); 表观消费 812.21 (-2.8%); 螺纹产量 +6.88、库存 -1.45、'终端节前备货基本结束'; Mysteel: '供增需降' '行情高度取决于节后预期, 现实端缺乏强驱动'",
      "unit": "万吨",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://gc.mysteel.com/a/26093020/BF8CDFCC49B8BF9F.html; https://gc.mysteel.com/a/26093018/8E46EF36AF237713.html",
      "original_source": "Mysteel (原文已核)",
      "price_basis": null,
      "comparison_basis": "Mysteel 同口径 9/24 当周总库存 1,481.97 (-55.76)",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "coke_cut_landed_0929",
      "metric": "焦炭首轮提降落地 (1.4 负反馈检验行输入)",
      "value": "9/29 唐山/天津焦化厂及部分钢厂 (邢台/石家庄/唐山/天津) 对湿熄焦 -100、干熄焦 -110 元/吨, 自 10/1 零点执行; 市场预期节后再降 2-3 轮; 炼焦煤价格指数 9/8 2,278 → 9/29 2,154 (-5.5%); Mysteel 10/2 月报: 9 月两轮提涨 (9/3、9/10) 累计湿熄 +450/干熄 +490, '大部分钢厂陷入亏损', 247 家铁水 9 月 236-238 万吨/日 (参考级), 焦企库存 9/4 97.38 → 9/25 68.1 万吨",
      "unit": "元/吨",
      "observation_date": "2026-09-29",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://www.sohu.com/a/1082722121_122014422; https://k.sina.cn/article_2299163722_890a744a00102f5je.html",
      "original_source": "光大期货 (搜狐转引, 已核) / Mysteel 10 月月报 (已核)",
      "price_basis": null,
      "comparison_basis": "上周 '第一轮提降 (100-110) 准备发起'",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "opec_1004_pending",
      "metric": "OPEC+ 10/4 会议 (闭市期, 待)",
      "value": "10/4 线上会议预期维持 11 月产量目标不变 (顺延), 未定案; 实际产量仍低于目标; 国内首个响应日 10/8",
      "unit": "事件",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://www.agbi.com/oil-and-gas/2026/09/opec-likely-to-keep-output-targets-steady-at-sunday-meeting/; https://www.tokenpost.com/news/investing/25827",
      "original_source": "AGBI / TokenPost (前瞻, 多源)",
      "price_basis": null,
      "comparison_basis": "9/6 按兵",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "us_calendar_oct_2026",
      "metric": "10 月官方发布日历 (0.0b 输入)",
      "value": "BLS: CPI 10/14 08:30 ET (北京 10/14 20:30 → 国内 T=10/15, 有夜盘者 10/14 夜盘起); PPI 10/15 08:30 ET (→ T=10/16); 美联储: FOMC 10/27-28, 决议 10/28 14:00 ET、记者会 14:30 (北京 10/29 02:00 → 国内 T=10/29, T-3=10/26, T-1=10/28, T+1=10/30); 9 月会议纪要 10/7 14:00 ET (北京 10/8 02:00); USDA WASDE 10/9 12:00 ET (北京 10/10 00:00 周六 → 国内 10/12)",
      "unit": "日期",
      "observation_date": "2026-10-03",
      "published_at": "2026-10-03",
      "source_url_or_file": "https://www.bls.gov/schedule/2026/10_sched.htm; https://www.federalreserve.gov/newsevents/2026-october.htm; https://www.usda.gov/about-usda/general-information/staff-offices/office-chief-economist/commodity-markets/wasde-report",
      "original_source": "BLS / 美联储 / USDA 官方日历 (已核)",
      "price_basis": null,
      "comparison_basis": "上周 '10 月 FOMC 国内 T 待核 (预计 10/29)'",
      "role": "required_execution",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sugar_prices_0930",
      "metric": "SR2701 / 广西现货 (9/29-9/30)",
      "value": "9/29 郑糖继续下跌; 9/30 早盘 SR2701 收 5344 (持平; 高 5345 / 低 5318); 广西集团/贸易商 9/30 报 5130-5180 (较 9/24 -20); '国庆节前购销意愿不高'; 9 月产销未发布 (10 月上旬)",
      "unit": "元/吨",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "https://www.yntw.com/2026/09/39324.html; https://www.yntw.com/2026/09/39312.html",
      "original_source": "糖网",
      "price_basis": "早盘 close / 现货报价",
      "comparison_basis": "9/24 SR2701 5404, 现货 5150-5200",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "cotton_0930",
      "metric": "棉花现货 / 新棉收购 / 储备棉轮出结束",
      "value": "新疆棉花现货 9/30 17,250 (+100); 中储棉按政策自 9/30 起停止 2026 年中央储备棉销售 (轮出结束); 截至 9/15 累计挂牌 33.68 万吨、成交 33.53 万吨、成交率 99.55%; 新疆机采棉收购指数 7.32 元/公斤 (+0.04 d/d, 同比 +1.22; '收购价稳中回落、加工进度偏快'); CF 9/28 夜盘 -0.84%、9/29 收盘跌超 1%、9/30 早盘跌超 1%",
      "unit": "元/吨, 元/公斤, %",
      "observation_date": "2026-09-30",
      "published_at": "2026-09-30",
      "source_url_or_file": "http://news.10jqka.com.cn/20260930/c680397785.shtml; https://www.cnfin.com/dz-lb/detail/20260715/4441019_1.html; https://www.dayaotex.com/chtc/news/44500.html",
      "original_source": "同花顺 / 中储棉政策 (cnfin) / 中国棉花信息网 (领布网转引)",
      "price_basis": null,
      "comparison_basis": "上周第九周 93.1%、9/20 99.51%; 吐絮率近 70%",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "soy_usda_0930",
      "metric": "USDA 季度库存 / 国内豆粕供应 (M 背景)",
      "value": "USDA 9/30: 9/1 美国旧作大豆库存 3.15 亿蒲 (预期 3.24; 上年 3.16, 修正后 3.25); 国内 9 月到港约 1,018 万吨、开机 61.7%、周压榨 227 万吨、豆粕库存约 110-111 万吨、大豆库存 832 万吨 (高位); 豆粕 9/28 夜盘 -2.30%",
      "unit": "亿蒲, 万吨",
      "observation_date": "2026-09-30",
      "published_at": "2026-10-01",
      "source_url_or_file": "https://news.fx678.com/202610010005148812.shtml; https://k.sina.cn/article_5952915720_162d2490806704xblo.html",
      "original_source": "USDA (汇通转引) / 新浪 (Mysteel 口径转引)",
      "price_basis": null,
      "comparison_basis": "9/18 豆粕库存 117.32",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "scan_ps_lc_0928",
      "metric": "池外扫描: 多晶硅 / 碳酸锂",
      "value": "多晶硅成交均价站上 4 万元/吨 (硅业分会 9/23: N 型复投料 4.30 万、颗粒硅 4.03 万); 9 月排产未实质减产 (8 月 11.89 万吨 → 9 月约 12.4 万吨), 全链库存约 50 万吨; 9/29 多晶硅跌超 2%、碳酸锂跌超 1%; LC 9/15 仓单 47,164 手",
      "unit": "元/吨, 吨, 手",
      "observation_date": "2026-09-28",
      "published_at": "2026-09-28",
      "source_url_or_file": "https://news.10jqka.com.cn/20260928/c680289466.shtml; https://www.cnfin.com/dz-lb/detail/20260928/4475328_1.html; https://www.sohu.com/a/1082254511_121157270",
      "original_source": "同花顺 / 中国金融信息网 / 搜狐 (广期所、硅业分会口径转引)",
      "price_basis": null,
      "comparison_basis": "上周 4.30 万/4.00-4.10 万; 减产方案待确认",
      "role": "optional_context",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "inv_coke_netease_july",
      "metric": "检索命中 '焦炭第一轮提降落地 焦化企业外运发运整体通畅' (已撤回)",
      "value": "首轮下调 50-55 元/吨 (河北/山东钢厂)",
      "unit": "元/吨",
      "observation_date": "2026-07-22",
      "published_at": "2026-07-22",
      "source_url_or_file": "https://www.163.com/dy/article/L2FFB73B05198CJN.html",
      "original_source": "财联社经网易 2026-07-22 文章 (非本周事件)",
      "price_basis": null,
      "comparison_basis": "本周首轮提降为 9/29 发起 (coke_cut_landed_0929)",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "inv_chemnet_iran_july",
      "metric": "检索命中 '伊朗甲醇分阶段复产, 开工 60-70%、月产 90 万吨' (已撤回)",
      "value": "开工 60-70%; 月产约 90 万吨; 7 月对华 75-100 万吨预估",
      "unit": "%, 万吨",
      "observation_date": "2026-07-09",
      "published_at": "2026-07-09",
      "source_url_or_file": "https://news.chemnet.com/toutiao/detail-73157.html",
      "original_source": "ChemNet 2026-07-09 (6 月停火期复产叙述, 与当前 '伊朗装置大部分停车' 相反)",
      "price_basis": null,
      "comparison_basis": "MA 复活条件 (ii) 到港回升",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "inv_xiben_2022",
      "metric": "检索命中 '9 月 30 日商品期货日盘综述 (西本)' (已撤回)",
      "value": "螺纹 2301 收 3,799 (-0.91%) 等",
      "unit": "元/吨",
      "observation_date": "2022-09-30",
      "published_at": "2022-09-30",
      "source_url_or_file": "https://m.steelx2.com/news-content.aspx?id=573446",
      "original_source": "西本资讯 2022 年文章 (合约 2301)",
      "price_basis": null,
      "comparison_basis": "本周 9/30 收盘采信同花顺/东方财富/星岛/糖网",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "historical"
    },
    {
      "evidence_id": "inv_brent_247_0929",
      "metric": "检索命中 '布油 9/29 113.96、9/15 峰 130.80、WTI 96.16' (已撤回)",
      "value": "113.96 / 130.80 / 96.16",
      "unit": "美元/桶",
      "observation_date": "2026-09-29",
      "published_at": "2026-10-03",
      "source_url_or_file": "https://247wallst.com/investing/2026/10/03/lng-shipments-through-hormuz-just-hit-a-7-month-high-why-the-global-energy-crisis-is-far-from-over",
      "original_source": "24/7 Wall St (与路透经同花顺 9/29 布伦特 12 月结算 96.16、WTI 89.38 及 TE 10/2 102.70 多源不符)",
      "price_basis": null,
      "comparison_basis": "brent_0929_1002",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "current"
    },
    {
      "evidence_id": "inv_taicang_monthly_avg",
      "metric": "检索命中 '截至 9/28 太仓甲醇均价 3,797, 较上月 +1,063' (口径不同, 不用)",
      "value": "3,797",
      "unit": "元/吨",
      "observation_date": "2026-09-28",
      "published_at": "2026-09-28",
      "source_url_or_file": "搜索摘要 (生意社月度均价/价格指数口径)",
      "original_source": "生意社 (月均口径, 与同花顺 iFInD 日度江苏 4,575 不同对象)",
      "price_basis": "月度均价",
      "comparison_basis": "ma_spot_0928_0929",
      "role": "optional_context",
      "quality": "invalid",
      "time_scope": "current"
    },
    {
      "evidence_id": "unverified_claims_1003",
      "metric": "搜索摘要未核项 (不采信): 钢厂盈利率 6.93% / 9 艘伊朗甲醇船 SDN / 太仓基差 01+5 走弱",
      "value": null,
      "unit": "—",
      "observation_date": null,
      "published_at": null,
      "source_url_or_file": "搜索摘要; OFAC 9/29、10/1 公告原文无甲醇船舶条目; Mysteel 月报只写 '大部分钢厂陷入亏损'; 大越早报只写 '现货升水期货/基差偏多'",
      "original_source": "未核到带日期原文",
      "price_basis": null,
      "comparison_basis": "分别对应 1.4 负反馈行 (参考级)、MA 供应证据、MA 复活条件 (iii)",
      "role": "optional_context",
      "quality": "missing",
      "time_scope": "current"
    }
  ],
  "candidates": [
    {
      "candidate_id": "2026-09-30|MA2701-MA2705|A|short_spread|v2.28",
      "opportunity_id": "MA_A_2701_2705",
      "trade_date": "2026-09-30",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "short_spread",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "连续第二周无行情快照: 价差/分位/1-5-10td/样本验收/确认定义 v1 观测值均无 9/30 实测 (9/18 读数 stale, 落后 7 td); 独立产业事实本周可得 (现货/升水/仓单); 港口库存数值本周可得但两口径方向冲突 (conflicting)",
      "signal": "unknown",
      "signal_basis": "研究筛选无本周实测; 确认定义 A-MA-2701-2705-v1 自 9/28 生效, 9/28-9/30 观测值无快照 → unknown",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "近3年同期分位需 9/30 口径快照 §1; 上一实测 100 (9/18) 已过期不沿用",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "td_calendar_0930"
          ],
          "details": "近腿 MA2701 69 td ≥20 (9/30 口径, 日历运算); 结构退出边界=近腿触 #1 (≈2026-12-17) 或主力换月"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "20 日均量需 9/30 口径快照; 9/18 实测 540,023/19,628 已过期",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "同期样本验收须按 9/30 市场锚重算 (9/18 锚 41/41/41 不自动延续)",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "domestic_model_basis",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ma_spot_0928_0929"
          ],
          "details": "国内路线论证结案 (未成案) 维持: 本周可得的国内事实 (江苏现货 4,575-4,600 升水期货、仓单持平、伊朗装置大部分停车摘要) 继续指向近月强; 复活条件 (i) 装置复产数值化 / (ii) 到港回升 / (iii) 现货基差走弱 本周均未被观测 ('基差 01+5 走弱' 摘要未核不采信; ChemNet 复产为 7 月文章 invalid) → 按协议 4 不能改名放行; 不转 geopolitical_fade 建仓 (research_only)",
          "diagnostic_evidence_refs": [
            "ma_port_inventory_conflict_0930",
            "inv_chemnet_iran_july",
            "unverified_claims_1003"
          ]
        },
        {
          "rule_id": "confirmation_definition",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_confirm_def_v1"
          ],
          "details": "A-MA-2701-2705-v1 已冻结 (effective_from 2026-09-28); 冻结不等于触发, 9/28-9/30 观测值待快照"
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ma_spot_0928_0929"
          ],
          "details": "(b) 独立产业事实已核反证延续: 现货 4,575-4,600 升水、9/28-9/29 主力 +4%/+3% 为近月强形态, 与做空价差反向; (a) 价格确认 v1 观测值无快照 = unknown 子项; 港口库存口径冲突与媒体涨跌只入 diagnostic",
          "diagnostic_evidence_refs": [
            "ma_port_inventory_conflict_0930",
            "ma_daily_media_0928_0930",
            "inv_taicang_monthly_avg"
          ]
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "czce_margin_0917_full"
          ],
          "details": "9/29 结算起甲醇全合约保证金 10%/涨跌停 9% 已生效 → 结构双腿按实际保证金口径计占用, ×0.8 缓冲 (2.3); 10/8 恢复交易后自持仓量最大合约未出现单边市的首个交易日结算起回落 (10/8 核); 非否决"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "国内路线未成案 → 本轮不出计划; 上上周影子计划 SP-2026-09-19-MA-A-short-spread 结算 pending (有效期已过, 预期作废)",
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
      "evaluation_order": [
        "screening",
        "#1",
        "#2",
        "#13",
        "domestic_model_basis",
        "confirmation_definition",
        "#5",
        "exchange_notice",
        "execution_plan",
        "account"
      ],
      "all_blockers": [
        "domestic_model_basis",
        "#5"
      ],
      "unknown_checks": [
        "screening",
        "#2",
        "#13",
        "execution_plan",
        "account"
      ],
      "first_blocker": "domestic_model_basis",
      "only_blocker": false,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [
          "D9=3 default_neutral"
        ],
        "notes": "D4=null (分位无实测); D2=1 (已核反证); D1=null (v1 观测值无快照); D3=null (计划缺失); D5=null; 完整总分 null"
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
          "observed_values": "无 9/28-9/30 快照; 上一实测 2026-09-18 S=+312, MA2701 ATR20 91.14, H20 3154 (stale, 仅对照); 媒体: 主力 9/28 日内 +5%、9/29 +3%+ (非 settle, 非判定输入)"
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
      "evidence_refs": [
        "td_calendar_0930",
        "ma_spot_0928_0929",
        "ma_confirm_def_v1",
        "czce_margin_0917_full"
      ]
    },
    {
      "candidate_id": "2026-09-30|MA2705-MA2709|A|unknown|v2.28",
      "opportunity_id": "MA_A_2705_2709_prep",
      "trade_date": "2026-09-30",
      "contracts": [
        "MA2705",
        "MA2709"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "准备对: 连续两周无快照; 上一快照同期样本 24/21/22<33、MA2709 20 日均量缺失 → 未计算/原始字段缺失, 不授许可",
      "signal": "unknown",
      "signal_basis": "分位无本周实测 (上一实测 100 仅参考); 样本不足",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/30 口径快照",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "MA2709 20 日均量上一快照缺失 (不足 20 个完整有效成交量样本); 连续两周无刷新",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "同期样本上一快照 24/21/22 <33 (incomplete); 连续两周无刷新",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "screening",
        "#2",
        "#13",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "screening",
        "#2",
        "#13",
        "account"
      ],
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
      "evidence_refs": [
        "td_calendar_0930"
      ]
    },
    {
      "candidate_id": "2026-09-30|RB2701-RB2703|A|unknown|v2.28",
      "opportunity_id": "RB_A_2701_2703",
      "trade_date": "2026-09-30",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "连续两周无快照: 分位/价差无 9/30 实测 (上一实测 56.1 不能沿用); Mysteel 同口径 9/30 当周取得 (去库放缓至 -19.03、供增需降)",
      "signal": "unknown",
      "signal_basis": "研究筛选需本周快照 §1; 上周 no_signal 直接证据已过期",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/30 口径快照 §1",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "td_calendar_0930"
          ],
          "details": "RB2701 70 td ≥20; RB2703 106 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "20 日均量需本周快照 (上一实测 669,156/27,445 过期)",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "方向未定 (研究筛选 unknown) → (a)(b) 均不能判; 独立产业证据已备且已核: Mysteel 9/30 当周总库存 1,462.94 (-19.03, 去库放缓)、周产量 793.18 (+13.50)、消费 812.21 (-2.8%)、建材去库/板材累库; 焦炭首轮提降 9/29 落地 = 负反馈启动确认 (背景)",
          "diagnostic_evidence_refs": [
            "steel_inventory_mysteel_0930",
            "coke_cut_landed_0929"
          ],
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
          "details": "独立国内月差不依赖复产/铁水/收缩成本假设; 铁水为参考; 提降落地为背景; '库存转累' 行以总库存判定, 9/30 当周仍去化 (-19.03), 板材累库为分项"
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "shfe_margin_0921"
          ],
          "details": "9/23 结算起 RB 涨跌停 7%/一般保证金 9% 已生效 → ×0.8 缓冲、公告日核占用; 10/8 后按条件回落; 非否决"
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "screening",
        "#1",
        "#2",
        "#5",
        "D14",
        "exchange_notice",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "screening",
        "#2",
        "#5",
        "account"
      ],
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
      "evidence_refs": [
        "td_calendar_0930",
        "steel_inventory_mysteel_0930",
        "shfe_margin_0921"
      ]
    },
    {
      "candidate_id": "2026-09-30|RB2703-RB2705|A|unknown|v2.28",
      "opportunity_id": "RB_A_2703_2705_prep",
      "trade_date": "2026-09-30",
      "contracts": [
        "RB2703",
        "RB2705"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "准备对 (仅取样): 连续两周无快照; 上一实测分位 61.8、RB2705 13,672 临界过 #2",
      "signal": "unknown",
      "signal_basis": "需本周快照",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/30 口径快照",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "RB2705 20 日均量上一实测 13,672 临界; 连续两周无刷新",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "screening",
        "#2",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "screening",
        "#2",
        "account"
      ],
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
      "evidence_refs": [
        "td_calendar_0930"
      ]
    },
    {
      "candidate_id": "2026-09-30|MA2701|directional|long|v2.28",
      "opportunity_id": "MA_D_long_2701",
      "trade_date": "2026-09-30",
      "contracts": [
        "MA2701"
      ],
      "strategy": "D",
      "hypothesis": "event_shock",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "连续两周无快照: SC2611 结算周涨 (9/23→9/30)、D8、ATR 分层/重校准、MA2701 9/21-9/30 逐日结算 (#30) 全部 unknown; 媒体收盘/日内涨跌只作记录 (9/28 主力日内 +5% 为 '可能触及' 线索)",
      "signal": "unknown",
      "signal_basis": "策略 D 触发=事件落地+落地次日方向确认+微观同向; 本周事件 (俄禁令官宣 9/30、OPEC+ 10/4、联储纪要 10/7、美方反提案) 落在 T-1 或闭市期, 落地次日确认须待 10/8 后 → unknown",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "td_calendar_0930"
          ],
          "details": "69 td ≥ 20 + D 池持仓上限 30 日 (≥50 td)"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需本周快照",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "cal_holiday_0921",
            "czce_margin_0917_full",
            "ine_sc_margin_0921",
            "shfe_margin_0921",
            "dce_margin_0918",
            "us_calendar_oct_2026",
            "russia_diesel_ban_official_0930"
          ],
          "details": "0.1 低敞口判定继续命中: 高密度簇 (10/4 OPEC+ 闭市期→10/7 联储纪要→10/8 复盘多重落地→10/12 WASDE→10/15 CPI→10/16 PPI→10/29 FOMC; 两周内 ≥2 离散催化且当周有未落地节点) + 交易所公告 ±1 日 (9/29 第二阶段生效, 10/8 回落核日) + D12 高波层 (上一实测 82.9, 连续两周无刷新, 不单独作依据); 限隔夜池方向性单边新开 → 否决; 结构表达不受本项",
          "diagnostic_evidence_refs": [
            "inv_canonical_calendar_1009",
            "pr30_closed_unmerged"
          ]
        },
        {
          "rule_id": "geo_quake_day_pm1",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "russia_diesel_ban_official_0930"
          ],
          "details": "0.1 低敞口判定/2.3 '地缘双轴质变 headline 日 ±1 能源链方向性单边新开 ×0': 俄乌轴 '9-30 延期 (升级)' 预设质变形态 9/30 官宣落地 (TASS 原文已核), 质变日 9/30 及 ±1 的下一交易日 10/8 → 能源链方向性单边新开冻结、存量 T-0 双向检视; 预设分支机械执行, 非新护栏"
        },
        {
          "rule_id": "MA_oil_guard",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "SC2611 结算周涨 9/23→9/30 (两端 settle) 无快照; 9/29 -3%/9/30 日内 -5% 为收盘/日内口径仅记录; 闭市期布油 +6-7% 为外盘旁证, 不作命中依据",
          "diagnostic_evidence_refs": [
            "sc_daily_media_0928_0930",
            "brent_0929_1002",
            "snap_0919_stale",
            "inv_brent_247_0929"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2b.1 SC 护栏结算周涨列",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "D8 周涨分位需快照 §2d (9/23→9/30); 上一读数上尾 66.7 过期",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2d",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#20",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "创近 250 日 H 与周涨前 10% 分位需快照",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2b/§2d",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#30",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "MA2701 逐日 settle/pre_settle (9/21-9/30) 未取得; 媒体: 主力 9/28 日内 +4%→一度 +5% (3,261)、夜盘 +3.90%、9/29 +3%+ → '9/28 可能触及 ≥5%' 须快照判定, 不预设命中或未命中; 主力≠判定腿、日内≠结算",
          "diagnostic_evidence_refs": [
            "ma2701_daily_settle_missing_1003",
            "ma_daily_media_0928_0930"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "运行 scripts/future_data.py v1.16 (§2b.1 日结算涨跌%/近 5 日/#30 近 3 日≥5% 列) 或终端导出 MA2701 9/28-9/30 settle/pre_settle",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "ATR250 分位/HV20/HV60 与池内极差需快照 §2a; 上一实测 82.9 高波层/极差 77.4 过期; 事件 T-3 依 0.0b (10/26 为 FOMC T-3) 人工核",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2a",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "czce_margin_0917_full"
          ],
          "details": "9/29 结算起甲醇全合约保证金 10%/涨跌停 9% 已生效 → ×0.8 缓冲、公告日核占用; 10/8 回落核; 非否决"
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
          "details": "无事件对象/落地次日确认条件/Entry/SL/TP; 上上周影子计划 SP-2026-09-19-MA2701-long-D 结算 pending (有效期已过, 预期作废)",
          "gap": {
            "kind": "plan",
            "owner": "research",
            "next_action": "#16 与质变日 ±1 解除 (10/8 复评后) 前不出计划; 事件对象候选=10/4 OPEC+ (10/8 响应)、10/29 FOMC",
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "#1",
        "#2",
        "#16",
        "geo_quake_day_pm1",
        "MA_oil_guard",
        "D8",
        "#20",
        "#30",
        "D12",
        "exchange_notice",
        "#25",
        "execution_plan",
        "account"
      ],
      "all_blockers": [
        "#16",
        "geo_quake_day_pm1"
      ],
      "unknown_checks": [
        "#2",
        "MA_oil_guard",
        "D8",
        "#20",
        "#30",
        "D12",
        "execution_plan",
        "account"
      ],
      "first_blocker": "#16",
      "only_blocker": false,
      "score": {
        "canonical_ref": "3.1 事件冲击池",
        "result": null,
        "defaulted_dimensions": [
          "D9=3 default_neutral"
        ],
        "notes": "D12/D8/D11 无实测 → null; 事件对象未指定 → D1/D2/D3/D5 null; ①≠缓和证真期间能源链方向性单边固定 +1 扣减"
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
      "evidence_refs": [
        "td_calendar_0930",
        "cal_holiday_0921",
        "czce_margin_0917_full",
        "russia_diesel_ban_official_0930",
        "us_calendar_oct_2026"
      ]
    },
    {
      "candidate_id": "2026-09-30|MA2701|directional|short|v2.28",
      "opportunity_id": "MA_short_2701",
      "trade_date": "2026-09-30",
      "contracts": [
        "MA2701"
      ],
      "strategy": "D",
      "hypothesis": "event_shock",
      "evidence_basis": "geopolitical_fade",
      "direction": "short",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "同多头记录: 连续两周无快照; ①要件二 back 方向 unknown",
      "signal": "unknown",
      "signal_basis": "空头新开受 #26 (①未证缓和) 与质变日 ±1 否决; 事件落地次日确认无法核 → unknown",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "td_calendar_0930"
          ],
          "details": "69 td ≥50"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需本周快照",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#16",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "cal_holiday_0921",
            "czce_margin_0917_full",
            "ine_sc_margin_0921",
            "us_calendar_oct_2026",
            "russia_diesel_ban_official_0930"
          ],
          "details": "同多头记录: 低敞口继续命中 (高密度簇 + 交易所公告 ±1 日 + D12 上一实测)",
          "diagnostic_evidence_refs": [
            "inv_canonical_calendar_1009"
          ]
        },
        {
          "rule_id": "geo_quake_day_pm1",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "russia_diesel_ban_official_0930"
          ],
          "details": "同多头记录: 俄乌轴 9/30 官宣质变 → 9/30 与 10/8 能源链方向性单边新开冻结 (双向)"
        },
        {
          "rule_id": "#26",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "iran_counterproposal_0930",
            "hormuz_tankers_hit_0928_1001"
          ],
          "details": "①'中断证真' 维持: 要件一 '再袭船' 9/28-10/1 四起 (UKMTO 多源) 再命中; 反向质变要件 (官方停火/重开或伊朗许可-收费机制正式落地 + back 回落) 未出现——美方 9/30 反提案为谈判 headline (顺序分歧、未官方化, 'I offered them NOTHING'); 要件二 back 方向无快照 unknown (不影响 #26: 未证缓和即否决); 通行量近常态为参考级且口径冲突 → 能源链方向性空头新开否决继续",
          "diagnostic_evidence_refs": [
            "hormuz_traffic_conflicting_0930",
            "sc_daily_media_0928_0930",
            "brent_0929_1002"
          ]
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
          "details": "双向对称: MA2701 逐日结算 (9/21-9/30) 未取得; SC 9/30 日内 -5% (收盘 -0.82%) 不替代判定腿",
          "diagnostic_evidence_refs": [
            "ma2701_daily_settle_missing_1003",
            "sc_daily_media_0928_0930"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2b.1",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "空头看下尾; 需快照 §2d",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2d",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "D12",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需快照 §2a",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2a",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "czce_margin_0917_full"
          ],
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "#1",
        "#2",
        "#16",
        "geo_quake_day_pm1",
        "#26",
        "MA_oil_guard",
        "#30",
        "D8",
        "D12",
        "exchange_notice",
        "execution_plan",
        "account"
      ],
      "all_blockers": [
        "#16",
        "geo_quake_day_pm1",
        "#26"
      ],
      "unknown_checks": [
        "#2",
        "#30",
        "D8",
        "D12",
        "execution_plan",
        "account"
      ],
      "first_blocker": "#16",
      "only_blocker": false,
      "score": {
        "canonical_ref": "3.1 事件冲击池",
        "result": null,
        "defaulted_dimensions": [
          "D9=3 default_neutral"
        ],
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
      "evidence_refs": [
        "td_calendar_0930",
        "iran_counterproposal_0930",
        "hormuz_tankers_hit_0928_1001",
        "russia_diesel_ban_official_0930",
        "czce_margin_0917_full"
      ]
    },
    {
      "candidate_id": "2026-09-30|M2701|unknown|unknown|v2.28",
      "opportunity_id": "M_observe_2701",
      "trade_date": "2026-09-30",
      "contracts": [
        "M2701"
      ],
      "strategy": "unknown",
      "hypothesis": "unknown",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "research_only",
      "data_feasibility_reason": "无已许可具体策略 (仅观察); 行情连续两周无快照; USDA 季度库存 (9/30) 与国内豆粕供应读数可得",
      "signal": "unknown",
      "signal_basis": "无已定义信号条件",
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "licensed_route",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "canonical_m_route"
          ],
          "details": "1.5 M 卡: 无已许可具体策略, 不进 C 池; 升核心须已有许可路由 + 独立公开供需证据 + 行情确认; 本周 USDA 9/1 大豆库存 3.15 亿蒲 (低于预期)、国内豆粕库存 110-111 万吨/大豆 832 万吨高位为背景",
          "diagnostic_evidence_refs": [
            "soy_usda_0930"
          ]
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "dce_margin_0918",
            "us_calendar_oct_2026"
          ],
          "details": "9/29 结算起豆粕涨跌停 8%/保证金 10% 已生效; 10/9 WASDE (北京 10/10 00:00) 国内首次响应 10/12, 报告前 2 日禁新开按国内交易日 10/8-10/9 核; 非否决"
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "licensed_route",
        "exchange_notice",
        "account"
      ],
      "all_blockers": [
        "licensed_route"
      ],
      "unknown_checks": [
        "account"
      ],
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
      "evidence_refs": [
        "canonical_m_route",
        "dce_margin_0918",
        "us_calendar_oct_2026"
      ]
    },
    {
      "candidate_id": "2026-09-30|SR2701-SR2705|A|unknown|v2.28",
      "opportunity_id": "SR_A_2701_2705",
      "trade_date": "2026-09-30",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "连续两周无快照 (上一实测分位 0.0 未触发不能沿用)",
      "signal": "unknown",
      "signal_basis": "需本周快照 §1",
      "screening_evidence": "snap_0919_stale",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需 9/30 口径快照",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "td_calendar_0930"
          ],
          "details": "SR2701 69 td / SR2705 148 td"
        },
        {
          "rule_id": "#2",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需本周快照 (上一实测 470,759/40,611 过期)",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机 TUSHARE_TOKEN 运行 scripts/future_data.py v1.16) / data_pipeline",
            "next_action": "10/8 前 (以 9/30 为 AS_OF) 或 10/8 收盘后运行 python3 scripts/future_data.py 并提交 research/<日期>-data-snapshot.txt; 连续两周无快照, 无快照则本项保持 unknown",
            "due_at": "2026-10-08"
          }
        },
        {
          "rule_id": "exchange_notice",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "czce_margin_0917_full"
          ],
          "details": "9/29 结算起白糖保证金 8%/涨跌停 7% 已生效; 10/8 回落核; 非否决"
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "screening",
        "#1",
        "#2",
        "exchange_notice",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "screening",
        "#2",
        "account"
      ],
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
      "evidence_refs": [
        "td_calendar_0930",
        "sugar_prices_0930",
        "czce_margin_0917_full"
      ]
    },
    {
      "candidate_id": "2026-09-30|SR2701|B|long|v2.28",
      "opportunity_id": "SR_B_summer_2026",
      "trade_date": "2026-09-30",
      "contracts": [
        "SR2701"
      ],
      "strategy": "B",
      "hypothesis": "seasonal_long",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "available",
      "data_feasibility_reason": "B-WINDOW 日历可由 canonical 定义与交易所日历确定性计算; 本记录只依赖日历",
      "signal": "not_triggered",
      "signal_basis": "TRIGGER-B 新开须 window_start ≤ 执行交易日 < planned_exit; SR-summer planned_exit=2026-09-22 已过, window_end=2026-09-30 已到 → 本窗口结束, 不可新开, 直接日历证据 (上周已结案, 本周为结案延续记录)",
      "signal_evidence_refs": [
        "b_window_calendar_2026"
      ],
      "screening_evidence": "b_window_calendar_2026",
      "evaluated_checks": [
        {
          "rule_id": "B_new_open_window",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "b_window_calendar_2026"
          ],
          "details": "planned_exit 2026-09-22 已过且窗口 9/30 结束; 本窗口结案; B-HISTORY 组装为 2027 窗口 research 责任"
        }
      ],
      "evaluation_order": [
        "B_new_open_window"
      ],
      "all_blockers": [
        "B_new_open_window"
      ],
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
          "observed_values": "SR2701 9/30 早盘 5344 (媒体); 广西现货 5130-5180"
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
      "not_evaluated_after_no_signal": [
        "card_veto (广西 8 月产销率反向, 已核 fail, 本周不再评估)",
        "#5",
        "D8",
        "B_trigger",
        "execution_plan",
        "account"
      ],
      "evidence_refs": [
        "b_window_calendar_2026",
        "sugar_sales_aug",
        "sugar_prices_0930"
      ]
    },
    {
      "candidate_id": "2026-09-30|CF2701|B|long|v2.28",
      "opportunity_id": "CF_B_autumn_2026",
      "trade_date": "2026-09-30",
      "contracts": [
        "CF2701"
      ],
      "strategy": "B",
      "hypothesis": "seasonal_long",
      "evidence_basis": "domestic_public",
      "direction": "long",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "B 触发 Entry_raw=max(MA20, pre_window_low5+ATR20) 需快照 MA20/ATR20 (连续两周无) 且 B-HISTORY 未组装; 独立产业证据 (现货/新棉收购/轮出结束) 可得",
      "signal": "unknown",
      "signal_basis": "窗口筛选 pass 不是完整开仓信号; Entry 条件未组装且无快照 → unknown",
      "screening_evidence": "b_window_calendar_2026",
      "evaluated_checks": [
        {
          "rule_id": "B_window_screen",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "b_window_calendar_2026"
          ],
          "details": "CF-autumn 09-01–10-31: window_end 2026-10-30, planned_exit 2026-10-23; 9/30 在可新开区间 (剩余可新开交易日 10/8-10/22)"
        },
        {
          "rule_id": "#1",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "td_calendar_0930"
          ],
          "details": "CF2701 69 td"
        },
        {
          "rule_id": "card_veto",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "'国储轮储公告日 ±3 天暂停' 对滚动轮出周的适用性未定义; 轮出已于 9/30 停止 → 本条款自 10/8 起事实上不再触发, 但定义口径仍待写入品种卡",
          "gap": {
            "kind": "definition",
            "owner": "research",
            "next_action": "裁定该条款对滚动轮出的适用口径并写入品种卡 (轮出已结束, 可按 '轮出期外不适用' 结案)",
            "due_at": "next_report"
          }
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "cotton_0930"
          ],
          "details": "(b) 独立产业事实已核反证延续: 新棉集中上市 (机采棉收购指数 7.32 元/公斤 '稳中回落、加工进度偏快')、CF 9/29-9/30 连跌 >1%、轮出结束仅为供给扰动退出——无独立需求侧支持; (a) B Entry 未组装 = unknown 子项"
        },
        {
          "rule_id": "D8",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "需快照 §2d (做多看上尾); 上一读数下尾 98.0 过期",
          "diagnostic_evidence_refs": [
            "snap_0919_stale"
          ],
          "gap": {
            "kind": "raw_data",
            "owner": "user (本机运行脚本) / data_pipeline",
            "next_action": "补跑快照 §2d",
            "due_at": "2026-10-08"
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
          "evidence_refs": [
            "czce_margin_0917_full"
          ],
          "details": "9/29 结算起棉花保证金 9%/涨跌停 8% 已生效; 10/8 回落核; 非否决"
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
            "next_action": "#5 已核 fail (供给端反证) → 本周不出计划; 独立需求侧证据出现且 B 触发组装后再评估; 可新开区间至 10/22",
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
            "next_action": "执行核验阶段提供带时区时间戳的账户/持仓/挂单/费用/保证金快照; 研究阶段不催",
            "due_at": "before_execution"
          }
        }
      ],
      "evaluation_order": [
        "B_window_screen",
        "#1",
        "card_veto",
        "#5",
        "D8",
        "B_trigger",
        "exchange_notice",
        "execution_plan",
        "account"
      ],
      "all_blockers": [
        "#5"
      ],
      "unknown_checks": [
        "card_veto",
        "D8",
        "B_trigger",
        "execution_plan",
        "account"
      ],
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
          "observed_values": "无快照; CF 9/28 夜盘 -0.84%、9/29 跌超 1%、9/30 早盘跌超 1% (媒体); 新疆现货 17,250"
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
      "evidence_refs": [
        "b_window_calendar_2026",
        "td_calendar_0930",
        "cotton_0930",
        "czce_margin_0917_full"
      ]
    }
  ],
  "unresolved_items": [
    {
      "item": "行情快照补跑 (首要, 连续第二周): 用户本机 (TUSHARE_TOKEN) 运行 python3 scripts/future_data.py (v1.16; 含 §2b.1 判定腿逐日结算涨跌、§2d D8、§5 影子结算) 并提交 research/<日期>-data-snapshot.txt (建议 10/8 前以 9/30 为 AS_OF 补一份, 10/8 收盘后再跑一份); 用于 SC2611 结算周涨 (9/23→9/30)、MA2701 9/28-9/30 逐日结算 (#30 是否触及 ≥5%)、SC 近端 back 方向 (①要件二)、A 池分位/价差变化/样本验收、ATR 分层与极差、D8、确认定义 v1 观测值、影子计划结算; 无快照则 10/8 全部方向性新开判定保持 unknown",
      "owner": "账户持有人 (本机运行) / data_pipeline",
      "due_at": "2026-10-08",
      "required_evidence": [
        "snap_0919_stale",
        "ma2701_daily_settle_missing_1003",
        "shadow_ledger_missing_1003"
      ],
      "resolution": "pending"
    },
    {
      "item": "上周框架更新 PR #30 (v2.28 草案) 2026-10-01 关闭未合并 → 其日历纠错 (10/1-10/7、10/8 恢复)、交易所风控全池、负反馈启动、MA 结案/v1、AU 卡换版、脚本 EVENTS 同步均未落地 canonical; 本周阶段③在新分支重做并吸收 (取代 PR #30), 由用户审阅; 若用户有意不采纳, 请在 PR 评论说明原因以便下周按裁决处理",
      "owner": "future-adaption / future-data-sync / 用户审阅",
      "due_at": "2026-10-03",
      "required_evidence": [
        "pr30_closed_unmerged",
        "inv_canonical_calendar_1009",
        "cal_holiday_0921"
      ],
      "resolution": "pending"
    },
    {
      "item": "10/8 复盘日四重核验: (a) 全池提保扩板回落条件逐品种核 ('持仓量最大合约未出现涨跌停单边市的首个交易日结算起恢复'); (b) 俄乌轴 9/30 官宣质变日 ±1 的下一交易日=10/8 → 能源链方向性单边新开冻结、存量 T-0 双向检视; (c) 10/4 OPEC+ 结果 (顺延→延续/增产→回吐触发、MA 存量检视) 与 10/7 联储纪要 (北京 10/8 02:00) 按落地次日确认纪律 (10/9 起); (d) 低敞口条款复评 (10/12 WASDE、10/15 CPI、10/16 PPI、10/29 FOMC 已排期 → 簇仍高密度); 存量按护栏与止盈机械执行 (账户未知→条件式)",
      "owner": "账户持有人 (执行) / 研究方 (核验)",
      "due_at": "2026-10-08",
      "required_evidence": [
        "cal_holiday_0921",
        "russia_diesel_ban_official_0930",
        "opec_1004_pending",
        "us_calendar_oct_2026"
      ],
      "resolution": "pending"
    },
    {
      "item": "10 月官方日历写入 canonical 0.0b (阶段③): CPI 10/14 08:30 ET → 国内 T=10/15 (有夜盘者 10/14 夜盘起); PPI 10/15 → T=10/16; FOMC 决议 10/28 14:00 ET = 北京 10/29 02:00 → T=10/29, T-3=10/26, T-1=10/28, T+1=10/30; 9 月纪要 10/7 14:00 ET = 北京 10/8 02:00; WASDE 10/9 12:00 ET = 北京 10/10 00:00 → 国内 10/12; D12 T-3、#29 T-10 重入、1.2 贵金属窗口按此核",
      "owner": "future-adaption",
      "due_at": "2026-10-03",
      "required_evidence": [
        "us_calendar_oct_2026"
      ],
      "resolution": "pending"
    },
    {
      "item": "① '中断证真' 反向监测 (回改只认官方停火/重开或伊朗许可-收费机制正式落地 + SC 近端 back 回落): 美方 9/30 反提案后续 (伊方正式答复/分阶段方案官方化 = 反向候选, 不预设)、UKMTO 袭船持续性 (9/28-10/1 四起)、通行量口径统一后趋势 (参考级)、俄禁令 10/31 下一节点; back 方向待快照",
      "owner": "下周 change-analysis",
      "due_at": "2026-10-10",
      "required_evidence": [
        "iran_counterproposal_0930",
        "hormuz_tankers_hit_0928_1001",
        "hormuz_traffic_conflicting_0930",
        "russia_diesel_ban_official_0930"
      ],
      "resolution": "pending"
    },
    {
      "item": "黑色负反馈 '启动确认' 后续: 焦炭第二轮提降是否发起 (市场预期再降 2-3 轮); Mysteel 10/9 当周总库存是否转累 (D14 '库存转累' 判定, 9/30 当周 -19.03 仍去化但板材累库、消费 -2.8%); JM/J 池外无仓; RB 多头评估冻结/空头不在白名单不变; RB 月差待快照",
      "owner": "研究方",
      "due_at": "2026-10-10",
      "required_evidence": [
        "coke_cut_landed_0929",
        "steel_inventory_mysteel_0930"
      ],
      "resolution": "pending"
    },
    {
      "item": "MA 国内路线论证结案 (未成案) 的复活条件: 观测到 (i) 国内装置复产的数值化进度, 或 (ii) 到港量回升 (伊朗/非伊朗货源; ChemNet 7 月复产文章不算), 或 (iii) 太仓/江苏现货基差走弱 (需带日期原文, '01+5 走弱' 摘要不算) 三者之一, 且确认定义 A-MA-2701-2705-v1 触发; 之前保持结案记录, 不改名 geopolitical_fade 建仓",
      "owner": "研究方",
      "due_at": "next_report",
      "required_evidence": [
        "ma_spot_0928_0929",
        "ma_confirm_def_v1"
      ],
      "resolution": "pending"
    },
    {
      "item": "甲醇港口库存口径统一: 同花顺 iNews (全港口 39.35/-1.85) 与大越 (华东+华南社会库存 34.75/+3.51) 方向相反 → 下周先确认原始统计机构与对象, 取单一口径的两期读数后再作增强级第二指标输入; 统一前不入 #5(b)/D2",
      "owner": "研究方",
      "due_at": "next_report",
      "required_evidence": [
        "ma_port_inventory_conflict_0930"
      ],
      "resolution": "pending (conflicting 记录)"
    },
    {
      "item": "CF-autumn B 触发组装: 快照到位后按 SEASONAL_PLAN_INPUT.md 组装 pre_window_low5 (8/25-8/31)、B-HISTORY (CF2601/2501/2401 秋窗)、MA20/ATR20 并运行 seasonal_plan.py; 登记 rule_version=B-v2.24 的 defined_at/effective_from; 轮储公告 ±3 天条款: 轮出已于 9/30 停止, 按 '轮出期外不适用' 写入品种卡结案; 可新开区间 10/8-10/22 (planned_exit 10/23)",
      "owner": "研究方 (计算由 data_pipeline 执行)",
      "due_at": "next_report",
      "required_evidence": [
        "b_window_calendar_2026",
        "cotton_0930"
      ],
      "resolution": "pending"
    },
    {
      "item": "影子计划: 本周未新登记 (最接近成立的两条候选 MA A 做空价差 / MA2701 突破多 均缺 9/30 两腿/单腿结算价, 连续两周无快照, 不以媒体收盘价登记); 上上周 SP-2026-09-19-* 有效期已过 → 由脚本 §5 在下次快照按 '过入场有效期未成交即作废' 机械确认 (登记不改写); 结算/作废结果只用于复评 #5/#16、D12",
      "owner": "data_pipeline (脚本 §5)",
      "due_at": "next_report",
      "required_evidence": [
        "shadow_ledger_missing_1003"
      ],
      "resolution": "pending"
    },
    {
      "item": "SR 9 月产销 (广西糖协, 10 月上旬发布) → SR 卡激活条件复核; SR-summer 2027 窗口 B-HISTORY 组装为 research 责任",
      "owner": "研究方",
      "due_at": "next_report",
      "required_evidence": [
        "sugar_sales_aug",
        "sugar_prices_0930"
      ],
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
      "reason": "canonical v2.27 长假日历 '10/1-10/8、10/9 复盘/首个响应日、低敞口 10/9 复评' 与交易所 2026-09-21 官方通知不符 (实际 10/1-10/7 休市、10/8 恢复交易并恢复夜盘); 上周已纠错并写入 PR #30, 该 PR 2026-10-01 关闭未合并 → canonical 文本仍错, 本周继续以 cal_holiday_0921 替代; 属日历纠错, 非市场变化",
      "affected_checks": [
        {
          "candidate_id": "2026-09-30|MA2701|directional|long|v2.28",
          "rule_id": "#16"
        },
        {
          "candidate_id": "2026-09-30|MA2701|directional|short|v2.28",
          "rule_id": "#16"
        },
        {
          "candidate_id": "2026-09-30|SR2701|B|long|v2.28",
          "rule_id": "B_new_open_window"
        }
      ],
      "recalculation": "completed",
      "recalculation_note": "#16: 事件簇按 10/8 复盘 + 10 月已核日历重算, 簇仍高密度且当周有未落地节点 → fail 不变; SR B: 窗口 9/30 结束 → no_signal 不变; 低敞口复评日 10/8"
    },
    {
      "withdrawn_evidence_id": "inv_coke_netease_july",
      "reason": "检索命中 '焦炭第一轮提降落地' (网易) 原文为 2026-07-22 (首轮 -50~55, 河北/山东), 非本周事件; 未用于任何判定; 本周首轮提降 (9/29 发起/10/1 执行, -100/-110) 采信光大 9/30 与 Mysteel 10/2 月报 (原文已核)",
      "affected_checks": [
        {
          "candidate_id": "2026-09-30|RB2701-RB2703|A|unknown|v2.28",
          "rule_id": "#5"
        }
      ],
      "recalculation": "completed",
      "recalculation_note": "RB #5 本周 unknown (方向未定), 负反馈 '启动确认' 依据为 coke_cut_landed_0929; 撤回项未参与"
    },
    {
      "withdrawn_evidence_id": "inv_chemnet_iran_july",
      "reason": "检索命中 '伊朗甲醇分阶段复产 60-70%/90 万吨' 为 2026-07-09 文章 (6 月停火期), 与当前 '伊朗装置大部分停车' 相反; 不能作为 MA 复活条件 (ii) 到港回升的观测",
      "affected_checks": [
        {
          "candidate_id": "2026-09-30|MA2701-MA2705|A|short_spread|v2.28",
          "rule_id": "domestic_model_basis"
        }
      ],
      "recalculation": "completed",
      "recalculation_note": "domestic_model_basis 依据为 ma_spot_0928_0929 (现货升水/近月强), 复活条件三项本周均未观测 → fail 不变"
    },
    {
      "withdrawn_evidence_id": "inv_xiben_2022",
      "reason": "检索命中 '9/30 商品期货日盘综述 (西本)' 为 2022-09-30 文章 (合约 2301); 未用于任何判定",
      "affected_checks": [
        {
          "candidate_id": "2026-09-30|MA2701|directional|long|v2.28",
          "rule_id": "MA_oil_guard"
        }
      ],
      "recalculation": "completed",
      "recalculation_note": "MA_oil_guard 本周 unknown (无快照); 9/30 收盘采信同花顺/东方财富/星岛 (sc_daily_media_0928_0930); 撤回项未参与"
    },
    {
      "withdrawn_evidence_id": "inv_brent_247_0929",
      "reason": "检索命中 '布油 9/29 113.96、峰 130.80' 与路透经同花顺 (9/29 布伦特 12 月结算 96.16)、TE (10/2 102.70)、straits.live (10/1 102.38) 多源不符; 标 invalid 不用",
      "affected_checks": [
        {
          "candidate_id": "2026-09-30|MA2701|directional|long|v2.28",
          "rule_id": "MA_oil_guard"
        },
        {
          "candidate_id": "2026-09-30|MA2701|directional|short|v2.28",
          "rule_id": "#26"
        }
      ],
      "recalculation": "completed",
      "recalculation_note": "布油路径按 brent_0929_1002 (96→102-103) 记录, 仅作旁证; MA_oil_guard unknown、#26 fail 均不依赖该项"
    },
    {
      "withdrawn_evidence_id": "inv_taicang_monthly_avg",
      "reason": "检索命中 '太仓甲醇均价 3,797 (较上月 +1,063)' 为生意社月度均价口径, 与日度现货 (同花顺 iFInD 9/28 江苏 4,575、大越 9/29 4,600) 不同对象; 不作基差/现货输入",
      "affected_checks": [
        {
          "candidate_id": "2026-09-30|MA2701-MA2705|A|short_spread|v2.28",
          "rule_id": "#5"
        }
      ],
      "recalculation": "completed",
      "recalculation_note": "#5(b) 依据为 ma_spot_0928_0929 (日度口径); 撤回项未参与; 结论不变"
    }
  ]
}
```

校验命令：`python3 scripts/validate_futures_audit.py --input research/2026-10-03-execution-audit.md`。实际结果见下方"校验记录"。结构校验不检查门覆盖、独立经济因果、确认规则有效性或实际交易许可。

## 校验记录

- 人工语义核对：连续两周无快照——所有依赖快照的门记 unknown（gap.kind=raw_data，归本机运行脚本），不以 9/18 读数或媒体收盘/日内代判定，"9/28 主力日内 +5%"只作 #30 的线索不作命中；俄乌轴 9/30 官宣延期按 0.1/2.3 既有"质变日 ±1 ×0"条款机械登记为 geo_quake_day_pm1（非新护栏），9/30 与 10/8 双向冻结；#3 按模型拆分（MA 多头 D 路线不引用①全局未知；空头按 geopolitical_fade 核①→#26 fail，依据为 UKMTO 多源袭船与美方反提案未官方化，通行量近常态为参考级且 conflicting 不入依据）；MA 国内路线结案维持（复活条件三项逐项核均未观测，7 月文章与未核摘要剔除）；#5 子项分列；事件窗口按交易所官方日历与 BLS/美联储 10 月官方日历（已核）；#16 依 0.1 低敞口判定当期命中；SR B 以窗口结束直接证据 no_signal，后续门明示未评估；CF B 轮储条款因轮出 9/30 结束拟结案但定义仍待写入（unknown 保留）；账户 unknown 不推定空仓；invalid 行只出现在 diagnostic_evidence_refs；pass/fail 依据全部为 verified 的 required 证据；本周未登记影子计划（缺结算价），缺件已写明。
- 校验器运行结果见下方代码块（由本次运行回填）。

```text
$ python3 scripts/validate_futures_audit.py --input research/2026-10-03-execution-audit.md
{
  "status": "valid",
  "scope": "structure_validation_only",
  "execution_permission": "not_evaluated",
  "errors": []
}
退出码: 0 （2026-10-03 本次运行，拟议 v2.28 / 分支 futures-framework/2026-10-03 工作区）
```
