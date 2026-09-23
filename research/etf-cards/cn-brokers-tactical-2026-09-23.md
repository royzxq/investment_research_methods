# 决策卡：证券 · 2026-09-23

> 席位：证券（框架 A1 行业席位，用户 2026-09-19 确认的新席位）。`card_id` = `cn-brokers-tactical`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓：无。本卡是候选卡（`watch`），只给点位与首选工具，不产生买入指令。
> 快照 §0 与本席位相关的缺口：快照 §5 不含未持有基金，首选工具的费率、规模、净值为 2026-09-23 tushare / akshare 实测，写在正文、不进 JSON `[需人工补充]`（下次快照把候选工具纳入 §5 后替换）。

## 1. 投资任务

- 任务：`tactical`——押"券商盈利跟随成交与两融的高位，但估值按账面看在历史低位"这一周期判断。记账币种人民币；计划持有 12 个月，最迟 2026-11-23 复评。
- 允许亏损：行业单笔亏损预算 7 万（用户 2026-09-23 拍板），按 −70% 压力跌幅反推单笔上限 10 万（`loss_budget_cap`）。
- 现状：无持仓。行业合计已用 17.6 万 / 21 万，新席位建仓要占剩余 3.4 万的行业额度——这是本卡之外的组合级约束，执行侧按 `portfolio_params` 检查。
- 不买它时钱放哪（记分基准）：中证货币基金指数 `H11025.CSI`。

## 2. 核心判断

**主判断**：券商 2026 上半年净利大增近五成，PB 1.21 处在 11.0 分位，账面上便宜；但盈利靠的是成交与两融的高位，9 月成交已回落到 2 万亿以下，而回撤阶梯的位置离减仓区只差 5%——账面便宜与周期位置互相矛盾时，按已验证的规则：现在不是建仓点，等 `buy_below` 458.91。

支撑证据：
1. 盈利兑现：43 家上市券商 2026 上半年营收 3,647.1 亿元、同比 +45.87%，归母净利 1,553.7 亿元、同比 +49.01%，仅 3 家下滑；中信证券 233.43 亿元居首（[腾讯新闻 2026-09-01](https://news.qq.com/rain/a/20260901A04VYZ00)、[腾讯新闻 2026-09-03](https://news.qq.com/rain/a/20260903A04WR000)）。中信 14.39%、东财 13.02%、国泰海通 10.75%（快照 §3）。
2. 收入来源仍在高位：截至 9 月 17 日两融余额 26,390.98 亿元、占流通市值 2.69%；年内日均成交同比 +94.78%，两融日均 +47.57%（[界面新闻](https://www.jiemian.com/article/13754482.html)、[财联社](https://www.cls.cn/detail/2407102)）。
3. 估值在账面低位：自聚合 PB 1.21，扩张窗分位 11.0（n=136，自 2015-05）；股息率 2.15% 处于 87.5 分位，股债利差 6.45pp 处于 97.8 分位（快照 §4）。

反证：
1. 盈利驱动在退潮：9 月 7–11 日成交 1.95 / 1.96 / 1.86 / 1.65 / 1.97 万亿，五个交易日都低于 2 万亿，9 月 10 日 1.65 万亿为年内次低；两融 9 月 4 日单日 −188.62 亿（个股轨道参考层 `framework/reference.md` @2026-09-12）。上半年年内曾有 31 天成交破 3 万亿——那才是 +49% 利润的底子。
2. 已验证规则给出的位置：回撤状态分位 69.4，`reduce_above` 769.99 只在当前 734.12 上方 4.9%；PE 12.30 处于 3.7 分位——"PE 极低 + PB 低 + 距减仓区一步之遥"正是 A5 提醒的高峰利润形状。

## 3. 指数匹配

- 编制：中证全指证券公司（`399975.SZ`），49 只成分，前十大 60.33%，最大单一成分中信证券 14.39%；行业口径证券 100%（快照 §3）。
- 错位度：论点押的是经纪与两融的 β，指数前三大里东方财富 13.02% 是互联网平台 + 基金销售，国泰海通 10.75% 是合并后的整合期——两者与"传统券商 β"有差异但方向一致，错位小。
- 换手：近 12 个月调入 0、调出 0，成分极稳。研究覆盖率 14.4%（1 只在个股研究池内）。
- 历史：指数 2007-06-29 基日、2013-07 发布；自聚合估值史自 2015-05（含 2015 年泡沫顶部，所以分位低半区偏"便宜"要打折看）。

## 4. 预期与估值

- 周期席位按 A5 用 **PB**：自聚合 PB 1.21，扩张窗分位 11.0，10 年窗分位 12.5；历史分位点 P10 1.21 / P25 1.28 / P50 1.52 / P75 1.74 / P90 1.96。PE 12.30（分位 3.7）只作参考。股息率 2.15%，亏损股权重 0。
- 方法 `mid_cycle`，三情景（`scenario_annual_return`，持有 3 年，股息 2.15%，拖累按首选工具年费 0.20%，为本卡假设；净资产增速同为假设，标 `ai_estimate`）：
  - 熊：净资产 −5%（自营亏损吃掉利润）、PB 停在 P10 1.21 → 年化 −3.05%。
  - 基准：净资产 +5%、PB 不变 → 年化 +6.95%。
  - 牛：净资产 +12%、PB 到 P75 1.74 → 年化 +26.82%（估值年化 +12.87%）。
- 这张卡的回报分布是右偏的——牛市里券商弹性最大。这正是它入池的理由，也是阶梯要求"等回撤"而不是"现在买"的理由：右偏收益要用左侧价格去换。

## 5. 工具比选（同指数比"谁更可靠更便宜"；以下为 2026-09-23 tushare / akshare 实测，`[需人工补充]` 待下次快照纳入 §5）

| 工具 | 年费（管理 + 托管 + 销售服务） | 赎回费 | 规模（2026-06-30） | 结论 |
|---|---|---|---|---|
| 华夏中证全指证券公司ETF联接 A `007992.OF` | 0.15% + 0.05% + 0 = 0.20% | 7 天内 1.50%，7–30 天 0.50%，30 天后 0 | 13.85 亿 | **首选**：最低费率档里规模最大、成立最早（2020-04） |
| 嘉实中证全指证券公司ETF联接 A `016842.OF` | 0.15% + 0.10% + 0 = 0.25% | 7 天内 1.50%，7–30 天 0.10%，30 天后 0 | 3.30 亿 | 备选：赎回费阶梯更友好，但规模小、贵 5 个基点 |
| 银华中证全指证券公司ETF联接 A `025193.OF` | 0.15% + 0.05% + 0 = 0.20% | 同华夏 | 2.89 亿 | 落选：2025-08 成立，规模小 |
| 鹏华中证全指证券公司指数(LOF) C `012044.OF` | 1.00% + 0.20% + 销售服务费 | — | — | 落选：年费是首选的 6 倍 |

跟踪偏离与跟踪误差：候选工具不在快照 §5，未算 `[需人工补充]`。

## 6. 点位与仓位

- 推导：框架 A9 唯一 validated 的回撤分位阶梯。近 36 个月末收盘最高值 935.02（快照 §6b），状态历史分位点 P10 0.4272 / P25 0.4908 / P75 0.8235（n=232，自 2007-06）。当前状态 0.7851、分位 69.4，中间区偏上。
- 点位（`level_at_drawdown_state`）：`add_below` **399.44**（目标 100%）、`buy_below` **458.91**（目标 50%）、`reduce_above` **769.99**（目标 30%）。当前 734.12。
- 读法：买入区在下方约 37%（相当于 2018 年底、2022 年底那类券商底部），减仓区在上方 4.9%。`status=watch`：买入侧只在跌破 458.91 时告警"到点复评"，不自动买；若届时论点仍成立，改 `active` 并把首选工具的 `action` 写 `buy`，按 50% 目标（5 万）建仓。无持仓，减仓侧无意义。
- 必须交代的代价：本指数在验证报告里只有 2 个适用折（F3 回撤 −14.9% 对 −37.5%、年化 +1.9% 对 −3.8%；F4 阶梯全程空仓，+1.6% 对 +4.0%），沿用主指数恒指的结论；F4 的 0% 仓位说明这套规则在券商这种"涨得快、跌得深"的指数上会错过整段上涨，只吃到下跌后的那一段。
- 仓位：`bet_group = cn-brokers`，上限 100,000 = 70,000 ÷ 70%；现持仓 0。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 警戒阈值 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 指数点位跌破买入锚点（自动） | 执行侧日频计算 | 734.12 | < 458.91 | 复评（改 active 后才买） | 日 |
| 指数相对 200 日均线（自动） | 执行侧日频计算 | 快照 §6：−6.39% | < 0 持续 | 告警 | 日 |
| A 股日均成交额（人工） | 交易所 / 公开统计 | 9 月 7–11 日 1.65–1.97 万亿 | 月均低于 1.5 万亿 | 复评 | 月 |
| 两融余额（人工） | 交易所 | 9 月 17 日 26,390.98 亿 | 跌破 2 万亿 | 复评 | 月 |

## 8. 退出与复评

- 失效条件（本卡无持仓，失效即撤销候选资格）：① A 股日均成交额连续两个月低于 1.5 万亿（盈利底子塌掉）→ `close`；② 两融余额跌破 2 万亿 → `reduce`（有仓时减、无仓时降低目标比例）。
- 最迟复评日 2026-11-23。
- 记分：基准 `H11025.CSI`，预登记 2026-09-23，置信度 40%，写卡时点位 734.12（候选卡记分从建仓起算）。

```json
{
  "card_schema_version": 1,
  "card_id": "cn-brokers-tactical",
  "as_of_date": "2026-09-23",
  "supersedes": null,
  "framework": {"path": "framework/etf_framework.md", "version": "v0.1"},
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "tactical",
  "status": "watch",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "399975.SZ",
    "index_name": "证券公司",
    "asset_type": "cyclical",
    "currency": "CNY",
    "counts_toward_sector_cap": true,
    "china_equity": true,
    "view_mismatch_note": "论点押经纪与两融的 β；前三大里东方财富 13.02% 是互联网平台 + 基金销售、国泰海通 10.75% 处于合并整合期，方向一致、错位小",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {"value": 49, "source": "snapshot§3"},
      "max_constituent_weight_pct": {"value": 14.39, "source": "snapshot§3"},
      "top10_weight_pct": {"value": 60.33, "source": "snapshot§3"},
      "research_coverage_pct": {"value": 14.4, "source": "snapshot§3"},
      "top_constituents": [
        {"code": "600030.SH", "name": "中信证券", "weight_pct": {"value": 14.39, "source": "snapshot§3"}},
        {"code": "300059.SZ", "name": "东方财富", "weight_pct": {"value": 13.02, "source": "snapshot§3"}},
        {"code": "601211.SH", "name": "国泰海通", "weight_pct": {"value": 10.75, "source": "snapshot§3"}}
      ]
    }
  },
  "thesis": {
    "statement": "券商上半年净利大增近五成、PB 1.21 处 11.0 分位账面便宜，但盈利靠成交与两融的高位，9 月成交已回落到 2 万亿以下、回撤阶梯离减仓区只差 5%；按已验证规则现在不是建仓点，等 buy_below 458.91",
    "evidence": [
      "43 家上市券商 2026 上半年营收 3,647.1 亿元、+45.87%，归母净利 1,553.7 亿元、+49.01%，仅 3 家下滑；中信证券 233.43 亿元居首",
      "9 月 17 日两融余额 26,390.98 亿元、占流通市值 2.69%；年内日均成交同比 +94.78%、两融日均 +47.57%",
      "自聚合 PB 1.21 处扩张窗 11.0 分位；股息率 2.15% 处 87.5 分位、股债利差 6.45pp 处 97.8 分位"
    ],
    "counter_evidence": [
      "9 月 7–11 日成交 1.95/1.96/1.86/1.65/1.97 万亿，五日均低于 2 万亿、9/10 为年内次低；两融 9/4 单日 -188.62 亿——上半年 31 天破 3 万亿才是 +49% 利润的底子",
      "回撤状态分位 69.4，reduce_above 769.99 只在当前上方 4.9%；PE 12.30 处 3.7 分位，是高峰利润压低估值的形状"
    ],
    "horizon_months": 12
  },
  "expectation": {
    "method": "mid_cycle",
    "scenarios": {
      "bear": {
        "inputs": {
          "eps_growth_pct": {"value": -5, "source": "ai_estimate", "note": "自营亏损吃掉利润，净资产小幅下降"},
          "dividend_yield_pct": {"value": 2.15, "source": "snapshot§4"},
          "current_multiple": {"value": 1.21, "source": "snapshot§4", "note": "自聚合 PB"},
          "terminal_multiple": {"value": 1.21, "source": "snapshot§4", "note": "PB 扩张窗 P10（与当前值相同）"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.2, "source": "ai_estimate", "note": "首选工具华夏 A 类年费 0.15%+0.05%，2026-09-23 实测，不在快照 §5"}
        },
        "valuation_change_pct": {"value": 0, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": -3.05, "source": "calc:scenario_annual_return"}
      },
      "base": {
        "inputs": {
          "eps_growth_pct": {"value": 5, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 2.15, "source": "snapshot§4"},
          "current_multiple": {"value": 1.21, "source": "snapshot§4"},
          "terminal_multiple": {"value": 1.21, "source": "snapshot§4"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.2, "source": "ai_estimate"}
        },
        "valuation_change_pct": {"value": 0, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 6.95, "source": "calc:scenario_annual_return"}
      },
      "bull": {
        "inputs": {
          "eps_growth_pct": {"value": 12, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 2.15, "source": "snapshot§4"},
          "current_multiple": {"value": 1.21, "source": "snapshot§4"},
          "terminal_multiple": {"value": 1.74, "source": "snapshot§4", "note": "PB 扩张窗 P75"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.2, "source": "ai_estimate"}
        },
        "valuation_change_pct": {"value": 12.87, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 26.82, "source": "calc:scenario_annual_return"}
      }
    },
    "valuation_state": {
      "index_code": "399975.SZ",
      "metric": "pb",
      "value": {"value": 1.21, "source": "snapshot§4", "note": "自聚合、指数权重口径；估值史自 2015-05 含泡沫顶部，低分位要打折看；PE 12.30（分位 3.7）只作参考"},
      "percentile_expanding": {"value": 11.0, "source": "snapshot§4"},
      "percentile_10y": {"value": 12.5, "source": "snapshot§4"},
      "sample_n": {"value": 136, "source": "snapshot§4"},
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "无持仓；首选工具按 2026-09-23 tushare/akshare 实测比选，下次快照纳入 §5 后复核",
    "list": [
      {"code": "007992.OF", "name": "华夏中证全指证券公司ETF联接-A", "instrument_type": "otc_fund", "share_class": "A", "currency": "CNY", "platform_account": "支付宝", "role": "primary", "action": "none", "reason": "未持有的首选：年费 0.20%（0.15%+0.05%+0）为最低档且规模最大（13.85 亿 @2026-06-30）、成立最早（2020-04）；赎回费 7–30 天 0.50%。到 buy_below 复评后改 buy"},
      {"code": "016842.OF", "name": "嘉实中证全指证券公司ETF联接-A", "instrument_type": "otc_fund", "share_class": "A", "currency": "CNY", "platform_account": "支付宝", "role": "backup", "action": "none", "reason": "备选：年费 0.25%，赎回费 7–30 天仅 0.10%，但规模 3.30 亿"},
      {"code": "025193.OF", "name": "银华中证全指证券公司ETF联接-A", "instrument_type": "otc_fund", "share_class": "A", "currency": "CNY", "platform_account": "支付宝", "role": "rejected", "action": "none", "reason": "年费同为 0.20%，但 2025-08 成立、规模 2.89 亿"},
      {"code": "012044.OF", "name": "鹏华中证全指证券公司指数(LOF)-C", "instrument_type": "otc_fund", "share_class": "C", "currency": "CNY", "platform_account": "支付宝", "role": "rejected", "action": "none", "reason": "管理 1.00% + 托管 0.20% 另加销售服务费，是首选的 6 倍"}
    ]
  },
  "trade_rules": {"min_holding_days": 30, "purchase_limit_note": "首选工具 30 天内赎回收 0.50%（7 天内 1.50%）"},
  "decision": {
    "rule_refs": ["A2", "A5", "A8", "A9", "A10", "A13"],
    "anchors": {
      "basis": "index_level",
      "index_code": "399975.SZ",
      "add_below": {
        "level": {"value": 399.44, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 100, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 935.02, "source": "snapshot§6"}, "state": {"value": 0.4272, "source": "snapshot§6", "note": "回撤状态扩张窗 P10"}},
        "rationale": "回撤状态回到自身历史 P10：相当于 2018 年底那类券商底部"
      },
      "buy_below": {
        "level": {"value": 458.91, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 50, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 935.02, "source": "snapshot§6"}, "state": {"value": 0.4908, "source": "snapshot§6", "note": "回撤状态扩张窗 P25"}},
        "rationale": "回撤状态回到自身历史 P25；当前 734.12 在其上方约 60%。watch 卡到点只告警复评，改 active 后才按 50% 目标建仓"
      },
      "reduce_above": {
        "level": {"value": 769.99, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 30, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 935.02, "source": "snapshot§6"}, "state": {"value": 0.8235, "source": "snapshot§6", "note": "回撤状态扩张窗 P75"}},
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 18%），只在当前上方 4.9%；无持仓，减仓侧无动作"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "cn-brokers",
    "stress_drawdown_pct": {"value": -70, "source": "user:2026-09-18"},
    "loss_budget_cny": {"value": 70000, "source": "user:2026-09-23"},
    "standalone_cap_cny": {"value": 100000, "source": "calc:loss_budget_cap"}
  },
  "monitor_variables": [
    {"name": "指数点位跌破买入锚点", "kind": "auto", "metric": "index_level", "operator": "<", "threshold": {"value": 458.91, "source": "calc:level_at_drawdown_state"}, "condition_text": "收盘跌破 buy_below（回撤状态 P25）", "data_source": "执行侧日频计算", "current_text": "快照 §6：734.12", "frequency": "daily", "action": "review", "action_note": "复评论点，成立则改 active、首选工具 action 改 buy"},
    {"name": "指数相对 200 日均线", "kind": "auto", "metric": "index_vs_sma200_pct", "operator": "<", "threshold": {"value": 0, "source": "framework:A11"}, "condition_text": "收盘持续低于 200 日均线", "data_source": "执行侧日频计算", "current_text": "快照 §6：-6.39%，below", "frequency": "daily", "action": "alert", "action_note": ""},
    {"name": "A 股日均成交额", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "月均日成交额低于 1.5 万亿", "data_source": "交易所 / 公开统计", "current_text": "9 月 7–11 日 1.65–1.97 万亿", "frequency": "monthly", "action": "review", "action_note": "命中即触发失效条件①的评估"},
    {"name": "两融余额", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "跌破 2 万亿", "data_source": "交易所", "current_text": "9 月 17 日 26,390.98 亿", "frequency": "monthly", "action": "review", "action_note": ""}
  ],
  "exit": {
    "invalidation": [
      {"name": "盈利底子塌掉", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "A 股日均成交额连续两个月低于 1.5 万亿", "data_source": "交易所 / 公开统计", "current_text": "9 月上旬 1.65–1.97 万亿", "frequency": "monthly", "action": "close", "action_note": "无持仓时撤销候选资格"},
      {"name": "杠杆资金退潮", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "两融余额跌破 2 万亿", "data_source": "交易所", "current_text": "26,390.98 亿", "frequency": "monthly", "action": "reduce", "action_note": "有仓时减，无仓时降低目标比例"}
    ],
    "latest_review_date": "2026-11-23"
  },
  "scorecard": {
    "benchmark": {"code": "H11025.CSI", "name": "同一笔钱放在货币基金"},
    "preregistered_at": "2026-09-23",
    "confidence_pct": 40,
    "entry_ref_index_level": {"value": 734.12, "source": "snapshot§6"}
  }
}
```
