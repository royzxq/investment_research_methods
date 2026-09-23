# 决策卡：有色金属 · 2026-09-23

> 席位：有色（框架 A1 行业席位）。`card_id` = `cn-nonferrous-tactical`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓按用户 2026-09-18 提供的数：南方中证申万有色金属ETF联接 E `010990.OF` 11,570 元，定投中。
> 快照 §0 与本席位相关的缺口：无（指数行情、成分、自聚合估值、基金净值与费率齐全）。

## 1. 投资任务

- 任务：`tactical`——押"铜矿端结构性短缺 + 黄金央行购金把有色龙头利润推到高位"这一周期判断，有期限。记账币种人民币；计划持有 18 个月，最迟 2026-11-23 复评。
- 允许亏损：行业单笔亏损预算 7 万（用户 2026-09-23 拍板），按 −70% 压力跌幅反推单笔上限 10 万（`loss_budget_cap`）。
- 现状：持仓 11,570 元，占上限 11.6%，远未触顶；定投继续。
- 不买它时钱放哪（记分基准）：中证货币基金指数 `H11025.CSI`。

## 2. 核心判断

**主判断**：铜、金量价双升把有色指数的盈利推到了周期高位——PE 分位 14.6 看起来便宜、PB 分位 69.6 却在历史高半区，这是周期顶部的典型形状；持有现有仓位、定投照常，但不做一次性追加，等回撤阶梯给点位。

支撑证据：
1. 铜的供给约束在兑现：伦铜 9 月 10 日触及 14,875 美元/吨历史新高，年内涨幅超 27%；全球铜矿或迎近 10 年首次减产（[新浪财经 2026-09-09](https://finance.sina.com.cn/jjxw/2026-09-09/doc-inirfivw3774806.shtml)、[FX168](https://www.fx168news.com/article/1095633)）。
2. 龙头利润创纪录：紫金矿业 2026 年半年度归母净利预计约 391 亿元、同比 +68%；洛阳钼业 155–165 亿元、同比 +79%～+90%，铜产品量价齐升（[新浪财经 2026-07-14](https://finance.sina.com.cn/wm/2026-07-14/doc-inihunse1257841.shtml)）。两者合计占指数权重 18.57%（快照 §3）。
3. 黄金分支有独立支撑：高盛、摩根大通、美银均预期 2026 年金价挑战 5,000 美元/盎司，央行购金是最重要支撑（[中国基金报](https://www.chnfund.com/article/AR20251220011506764)）；指数含黄金股 13.4%（快照 §3 行业权重）。

反证：
1. 利率与美元的压力是当下的事实：美联储 9 月 16 日加息 25bp，市场在定价年内再加一次；黄金 9 月 11 日跌破 4,300 美元、连续两周未收复 4,500，美元指数站稳 99 上方（个股轨道参考层 `framework/reference.md` @2026-09-12）。伦铜 9 月中旬也曾跌破 14,000（[新浪财经 2026-09-17](https://finance.sina.com.cn/jjxw/2026-09-17/doc-inisayan9387669.shtml)）。
2. 高峰利润不可外推：自聚合 PE 16.84 处于 14.6 分位，正是 A5 说的"景气顶部利润使 PE 看起来很低"；高盛预测铝价到 2026 年底较当前下降 18%（[中国基金报](https://www.chnfund.com/article/AR20251220011506764)），指数含铝 12.0%。

## 3. 指数匹配

- 编制：中证申万有色金属（`000819.SH`），50 只成分，前十大 44.73%，最大单一成分紫金矿业 11.18%；按 tushare 行业口径小金属 38.8%、铜 24.5%、黄金 13.4%、铝 12.0%、铅锌 6.2%（快照 §3）。
- 错位度：论点押的是铜与黄金（合计约 38%），而指数最大一块是"小金属"（稀土、锂等）38.8%——北方稀土 4.56%、赣锋锂业 2.70%、藏格矿业 2.73% 走的是另一条周期。错位约四成，写进监控。
- 换手：近 12 个月调入 10 只（现权重合计 7.7%）、调出 10 只（5.5%），中等。研究覆盖率 26.3%（5 只在个股研究池内），紫金、洛钼等可复用现成研究。
- 历史：指数 2004-12-31 基日、2012-05 发布，2012 年前为回溯值；自聚合估值史自 2012-05。

## 4. 预期与估值

- 周期席位按 A5 用 **PB**：自聚合 PB 3.06，扩张窗分位 69.6（n=158，自 2012-05），10 年窗分位 70.7；历史分位点 P10 1.99 / P25 2.14 / P50 2.68 / P75 3.15 / P90 3.51。PE 16.84（分位 14.6）只作参考。股息率 1.73%，亏损股权重 0.90%。
- 方法 `mid_cycle`，三情景（`scenario_annual_return`，持有 3 年，股息 1.73%，拖累按 A 类年费 0.60%；净资产增速为本卡假设，标 `ai_estimate`）：
  - 熊：净资产零增长、PB 回到 P25 2.14 → 年化 −10.11%（估值年化 −11.24%）。
  - 基准：净资产 +6%、PB 不变 → 年化 +7.13%。
  - 牛：净资产 +10%、PB 到 P75 3.15 → 年化 +12.10%（估值只贡献 +0.97%）。
- 不对称性：向上的估值空间只剩到 P75 的 3%，向下到 P25 有 30%。这就是"不追加"的量化理由。

## 5. 工具比选

| 工具 | 年费 | TD 年化 / TE | 结论 |
|---|---|---|---|
| 南方中证申万有色金属ETF联接 E `010990.OF`（持 11,570） | 0.70%（含销售服务费 0.10%） | −2.28pp / 1.72% | **首选（现有持仓）**，持有、定投继续 |
| 同基金 A 类 `004432.OF`（未持有） | 0.60% | — | 若日后在本席位新增资金走 A 类；存量不换（10 个基点的差异在 1.2 万元上一年 12 元，不值一次申赎） |
| 同基金 C 类 `004433.OF` | 1.00% | — | 落选 |

规模 net_asset 90.71 亿（2026-06-30），无清盘风险；赎回费 7 天内 1.50%、7 天后 0。

## 6. 点位与仓位

- 推导：框架 A9 唯一 validated 的回撤分位阶梯。近 36 个月末收盘最高值 11,703.19（快照 §6b），状态历史分位点 P10 0.4580 / P25 0.5720 / P75 0.8250（n=262，自 2004-12）。当前状态 0.7426、分位 61.5，中间区。
- 点位（`level_at_drawdown_state`）：`add_below` **5,360.06**（目标 100%）、`buy_below` **6,694.22**（目标 50%）、`reduce_above` **9,655.13**（目标 30%）。当前 8,690.98。
- 读法：买入区在下方约 23%，减仓区在上方约 11%——离减仓区比离买入区近。`status=active`、工具 `hold`：定投继续，不一次性买；升破 9,655.13 减到上限的 30%（3 万，现持仓 1.16 万在其下，届时不动）；跌破 6,694.22 不自动买，转复评。
- 必须交代的代价：本指数在验证报告里只有 2 个适用折（F3 回撤 −9.8% 对 −47.4%，F4 −7.6% 对 −31.2%；F4 年化 +9.2% 对 +14.5%），不足以单独出结论，沿用主指数恒指的 validated 结论；阶梯在趋势上涨段会长期低仓位——F4 平均仓位 34%、少赚 5.3 个点，就是代价的样子。
- 仓位：`bet_group = cn-nonferrous`，上限 100,000 = 70,000 ÷ 70%；现持仓 11,570。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 警戒阈值 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 指数相对 200 日均线（自动） | 执行侧日频计算 | 快照 §6：−10.01% | < 0 持续 | 告警 | 日 |
| 指数点位跌破买入锚点（自动） | 执行侧日频计算 | 8,690.98 | < 6,694.22 | 复评（不自动买） | 日 |
| 伦铜价格（人工） | LME / 新浪期货 | 9 月 18 日 14,515 美元/吨 | 跌破 11,000 美元/吨且持续一个月 | 复评 | 月 |
| 美元指数与金价（人工） | 公开行情 | 美元 99 上方、金价 4,300 下方（9/11） | 美元站稳 105 且金价跌破 4,000 | 复评 | 月 |

## 8. 退出与复评

- 失效条件：① 伦铜跌破 11,000 美元/吨且持续一个月（矿端短缺叙事被证伪）→ `reduce`；② 紫金矿业与洛阳钼业 2026 年报归母净利同比转负（价格拐点进入报表）→ `close`。
- 最迟复评日 2026-11-23。
- 记分：基准 `H11025.CSI`，预登记 2026-09-23，置信度 50%，写卡时点位 8,690.98。

```json
{
  "card_schema_version": 1,
  "card_id": "cn-nonferrous-tactical",
  "as_of_date": "2026-09-23",
  "supersedes": null,
  "framework": {"path": "framework/etf_framework.md", "version": "v0.1"},
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "tactical",
  "status": "active",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "000819.SH",
    "index_name": "中证申万有色金属",
    "asset_type": "cyclical",
    "currency": "CNY",
    "counts_toward_sector_cap": true,
    "china_equity": true,
    "view_mismatch_note": "论点押铜与黄金（合计约 38%），指数最大一块是小金属 38.8%（稀土、锂），走另一条周期；错位约四成",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {"value": 50, "source": "snapshot§3"},
      "max_constituent_weight_pct": {"value": 11.18, "source": "snapshot§3"},
      "top10_weight_pct": {"value": 44.73, "source": "snapshot§3"},
      "research_coverage_pct": {"value": 26.3, "source": "snapshot§3"},
      "top_constituents": [
        {"code": "601899.SH", "name": "紫金矿业", "weight_pct": {"value": 11.18, "source": "snapshot§3"}},
        {"code": "603993.SH", "name": "洛阳钼业", "weight_pct": {"value": 7.39, "source": "snapshot§3"}},
        {"code": "600111.SH", "name": "北方稀土", "weight_pct": {"value": 4.56, "source": "snapshot§3"}}
      ]
    }
  },
  "thesis": {
    "statement": "铜、金量价双升把有色指数盈利推到周期高位；PE 分位 14.6 与 PB 分位 69.6 的组合是周期顶部形状，持有、定投照常，不一次性追加，等回撤阶梯给点位",
    "evidence": [
      "伦铜 9 月 10 日触及 14,875 美元/吨历史新高、年内 +27%，全球铜矿或迎近 10 年首次减产",
      "紫金矿业 2026 上半年归母净利约 391 亿元、同比 +68%；洛阳钼业 155–165 亿元、同比 +79%～+90%，两者占指数 18.57%",
      "高盛、摩根大通、美银均预期 2026 年金价挑战 5,000 美元，央行购金为主要支撑；指数含黄金股 13.4%"
    ],
    "counter_evidence": [
      "美联储 9 月 16 日加息并定价年内再加，黄金 9 月 11 日跌破 4,300、美元站稳 99 上方，伦铜 9 月中旬曾跌破 14,000",
      "高峰利润不可外推：PE 16.84 处于 14.6 分位正是景气顶部形状；高盛预测铝价到 2026 年底较当前降 18%，指数含铝 12.0%"
    ],
    "horizon_months": 18
  },
  "expectation": {
    "method": "mid_cycle",
    "scenarios": {
      "bear": {
        "inputs": {
          "eps_growth_pct": {"value": 0, "source": "ai_estimate", "note": "净资产零增长（周期下行、利润回落）"},
          "dividend_yield_pct": {"value": 1.73, "source": "snapshot§4"},
          "current_multiple": {"value": 3.06, "source": "snapshot§4", "note": "自聚合 PB"},
          "terminal_multiple": {"value": 2.14, "source": "snapshot§4", "note": "PB 扩张窗 P25"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.6, "source": "snapshot§5", "note": "A 类年费"}
        },
        "valuation_change_pct": {"value": -11.24, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": -10.11, "source": "calc:scenario_annual_return"}
      },
      "base": {
        "inputs": {
          "eps_growth_pct": {"value": 6, "source": "ai_estimate", "note": "净资产增速"},
          "dividend_yield_pct": {"value": 1.73, "source": "snapshot§4"},
          "current_multiple": {"value": 3.06, "source": "snapshot§4"},
          "terminal_multiple": {"value": 3.06, "source": "snapshot§4"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.6, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 0, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 7.13, "source": "calc:scenario_annual_return"}
      },
      "bull": {
        "inputs": {
          "eps_growth_pct": {"value": 10, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 1.73, "source": "snapshot§4"},
          "current_multiple": {"value": 3.06, "source": "snapshot§4"},
          "terminal_multiple": {"value": 3.15, "source": "snapshot§4", "note": "PB 扩张窗 P75"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.6, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 0.97, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 12.1, "source": "calc:scenario_annual_return"}
      }
    },
    "valuation_state": {
      "index_code": "000819.SH",
      "metric": "pb",
      "value": {"value": 3.06, "source": "snapshot§4", "note": "自聚合、指数权重口径；周期席位按 A5 用 PB，PE 16.84（分位 14.6）只作参考"},
      "percentile_expanding": {"value": 69.6, "source": "snapshot§4"},
      "percentile_10y": {"value": 70.7, "source": "snapshot§4"},
      "sample_n": {"value": 158, "source": "snapshot§4"},
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "本席位只有一只持仓；新增资金走同基金 A 类，存量不换",
    "list": [
      {"code": "010990.OF", "name": "南方中证申万有色金属ETF联接-E", "instrument_type": "otc_fund", "share_class": "E", "currency": "CNY", "platform_account": "支付宝", "role": "primary", "action": "hold", "reason": "现有持仓，持有、定投继续；年费 0.70%，TD 年化 -2.28pp、TE 1.72%，规模 90.71 亿"},
      {"code": "004432.OF", "name": "南方中证申万有色金属ETF联接-A", "instrument_type": "otc_fund", "share_class": "A", "currency": "CNY", "platform_account": "支付宝", "role": "rejected", "action": "none", "reason": "未持有；年费 0.60% 优于 E 类 0.10 个百分点，若日后新增资金走 A 类，存量不值一次申赎"},
      {"code": "004433.OF", "name": "南方中证申万有色金属ETF联接-C", "instrument_type": "otc_fund", "share_class": "C", "currency": "CNY", "platform_account": "支付宝", "role": "rejected", "action": "none", "reason": "未持有；年费 1.00%，同基金最贵份额"}
    ]
  },
  "trade_rules": {"min_holding_days": 7, "purchase_limit_note": null},
  "decision": {
    "rule_refs": ["A5", "A8", "A9", "A10", "A13"],
    "anchors": {
      "basis": "index_level",
      "index_code": "000819.SH",
      "add_below": {
        "level": {"value": 5360.06, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 100, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 11703.19, "source": "snapshot§6"}, "state": {"value": 0.458, "source": "snapshot§6", "note": "回撤状态扩张窗 P10"}},
        "rationale": "回撤状态回到自身历史 P10：相当于 2015–2016、2018 那几轮周期底部"
      },
      "buy_below": {
        "level": {"value": 6694.22, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 50, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 11703.19, "source": "snapshot§6"}, "state": {"value": 0.572, "source": "snapshot§6", "note": "回撤状态扩张窗 P25"}},
        "rationale": "回撤状态回到自身历史 P25；当前 8,690.98 在其上方约 30%。跌破时不自动买而是复评（见监控）"
      },
      "reduce_above": {
        "level": {"value": 9655.13, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 30, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 11703.19, "source": "snapshot§6"}, "state": {"value": 0.825, "source": "snapshot§6", "note": "回撤状态扩张窗 P75"}},
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 17%）：升破即把这笔押注减到上限的 30%（3 万）；现持仓在其下，届时不动"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "cn-nonferrous",
    "stress_drawdown_pct": {"value": -70, "source": "user:2026-09-18"},
    "loss_budget_cny": {"value": 70000, "source": "user:2026-09-23"},
    "standalone_cap_cny": {"value": 100000, "source": "calc:loss_budget_cap"}
  },
  "monitor_variables": [
    {"name": "指数相对 200 日均线", "kind": "auto", "metric": "index_vs_sma200_pct", "operator": "<", "threshold": {"value": 0, "source": "framework:A11"}, "condition_text": "收盘持续低于 200 日均线", "data_source": "执行侧日频计算", "current_text": "快照 §6：-10.01%，below", "frequency": "daily", "action": "alert", "action_note": ""},
    {"name": "指数点位跌破买入锚点", "kind": "auto", "metric": "index_level", "operator": "<", "threshold": {"value": 6694.22, "source": "calc:level_at_drawdown_state"}, "condition_text": "收盘跌破 buy_below（回撤状态 P25）", "data_source": "执行侧日频计算", "current_text": "快照 §6：8,690.98", "frequency": "daily", "action": "review", "action_note": "不自动买；复评论点后再决定是否用剩余额度加"},
    {"name": "伦铜价格", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "跌破 11,000 美元/吨且持续一个月", "data_source": "LME / 新浪期货", "current_text": "2026-09-18 收 14,515 美元/吨", "frequency": "monthly", "action": "review", "action_note": "命中即触发失效条件①的评估"},
    {"name": "美元指数与金价", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "美元指数站稳 105 且金价跌破 4,000 美元", "data_source": "公开行情", "current_text": "美元 99 上方、金价 9/11 跌破 4,300", "frequency": "monthly", "action": "review", "action_note": ""}
  ],
  "exit": {
    "invalidation": [
      {"name": "矿端短缺叙事被证伪", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "伦铜跌破 11,000 美元/吨且持续一个月", "data_source": "LME", "current_text": "14,515 美元/吨", "frequency": "monthly", "action": "reduce", "action_note": ""},
      {"name": "价格拐点进入报表", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "紫金矿业与洛阳钼业 2026 年报归母净利同比转负", "data_source": "年报", "current_text": "2026 上半年分别 +68%、+79%～+90%", "frequency": "event", "action": "close", "action_note": ""}
    ],
    "latest_review_date": "2026-11-23"
  },
  "scorecard": {
    "benchmark": {"code": "H11025.CSI", "name": "同一笔钱放在货币基金"},
    "preregistered_at": "2026-09-23",
    "confidence_pct": 50,
    "entry_ref_index_level": {"value": 8690.98, "source": "snapshot§6"}
  }
}
```
