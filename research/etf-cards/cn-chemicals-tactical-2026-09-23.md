# 决策卡：化工 · 2026-09-23

> 席位：化工（框架 A1 行业席位）。`card_id` = `cn-chemicals-tactical`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓按用户 2026-09-18 提供的数：嘉实中证细分化工产业主题ETF联接 C `013528.OF` 8,845 元，定投中。
> 快照 §0 与本席位相关的缺口：无。

## 1. 投资任务

- 任务：`tactical`——押"反内卷把化工供给从无序扩张拉回利润优先，龙头利润进入上行段"这一有期限的周期判断。记账币种人民币；计划持有 18 个月，最迟 2026-11-23 复评。
- 允许亏损：行业单笔亏损预算 7 万（用户 2026-09-23 拍板），按 −70% 压力跌幅反推单笔上限 10 万（`loss_budget_cap`）。
- 现状：持仓 8,845 元，占上限 8.8%；定投继续。
- 不买它时钱放哪（记分基准）：中证货币基金指数 `H11025.CSI`。

## 2. 核心判断

**主判断**：反内卷加龙头提价已经把化工利润拉回上行段，但指数盈利里含着钾肥、锂盐、MDI 的周期高位价格，且油价站上 100 美元正在挤压中下游；持有现有仓位、定投照常，不一次性追加，等回撤阶梯给点位。

支撑证据：
1. 龙头利润转身：万华化学 2026 上半年归母净利约 100.63 亿元、同比 +64.35%，二季度单季 63.45 亿元同比翻倍，8 月 MDI、TDI 再提价（[腾讯新闻 2026-09-09](https://news.qq.com/rain/a/20260909A09TL100)、[万华 2026 半年报](https://static.cninfo.com.cn/finalpage/2026-08-25/1225497561.PDF)）；万华占指数 9.65%（快照 §3）。
2. 资源型成分量价齐升：盐湖股份 2026 上半年营收 130.52 亿元、同比 +79.88%，归母净利 61.69 亿元、同比 +137.88%，钾肥产销两旺、锂盐放量（[腾讯新闻 2026-08-27](https://news.qq.com/rain/a/20260827A02X2400)）；盐湖 6.03%、藏格 4.14%。
3. 供给纪律在制度化：反内卷通过政策端对无序扩产设边界，叠加协会与龙头在开工率、投放节奏与价格上的自律；反倾销措施落地、全球炼能进入紧平衡（[腾讯新闻 2026-09-08](https://news.qq.com/rain/a/20260908A06M5P00)、[国投证券 2026 年度展望](https://www.sdyanbao.com/detail/940859)）。

反证：
1. 成本端正在挤压：布伦特 9 月 9–11 日结算价连续三日站上 100 美元（101.21 / 107.63 / 104.61），8 月工业购进价格 +5.8% 高于出厂价 +3.8%，剪刀差 2 个百分点（个股轨道参考层 `framework/reference.md` @2026-09-12）。指数 51.0% 是化工原料、15.0% 化纤，正处在被挤的那一段。
2. 高峰价格入账：钾肥、碳酸锂、MDI 都在价格高位，PE 17.86 的 25.8 分位是"景气利润压低 PE"的形状；PB 2.31 在 47.0 分位，按账面看只是中位数，谈不上便宜。

## 3. 指数匹配

- 编制：中证细分化工（`000813.CSI`），50 只成分，前十大 42.65%，最大单一成分万华化学 9.65%；按 tushare 行业口径化工原料 51.0%、农药化肥 23.4%、化纤 15.0%（快照 §3）。
- 错位度：论点是"反内卷下的龙头定价权"，主要落在万华、巨化、宝丰、卫星这类一体化龙头（合计约 20%）；而指数近三成是钾肥与锂盐（盐湖、藏格、多氟多、天赐等），走的是资源价格周期。错位约三成。
- 换手：近 12 个月调入 6 只（现权重合计 6.8%）、调出 6 只（4.0%）。研究覆盖率仅 1.8%（1 只在个股研究池内），没有现成研究可复用。
- 历史：指数 2004-12-31 基日、2012-04 发布，2012 年前为回溯值；自聚合估值史自 2012-05。

## 4. 预期与估值

- 周期席位按 A5 用 **PB**：自聚合 PB 2.31，扩张窗分位 47.0（n=151，自 2012-05），10 年窗分位 42.2；历史分位点 P10 1.86 / P25 2.04 / P50 2.35 / P75 2.93 / P90 3.59。PE 17.86（分位 25.8）只作参考。股息率 1.88%，亏损股权重 2.40%。
- 方法 `mid_cycle`，三情景（`scenario_annual_return`，持有 3 年，股息 1.88%，拖累按 A 类年费 0.20%；净资产增速为本卡假设，标 `ai_estimate`）：
  - 熊：净资产零增长、PB 回到 P25 2.04 → 年化 −2.38%（估值年化 −4.06%）。
  - 基准：净资产 +5%、PB 不变 → 年化 +6.68%。
  - 牛：净资产 +10%、PB 到 P75 2.93 → 年化 +19.93%（估值年化 +8.25%）。
- 相比有色，化工的估值位置居中、两头空间对称，这是它比有色更适合继续定投的地方；但成本端的挤压是当期事实，所以同样不一次性追加。

## 5. 工具比选

| 工具 | 年费 | TD 年化 / TE | 结论 |
|---|---|---|---|
| 嘉实中证细分化工产业主题ETF联接 C `013528.OF`（持 8,845） | 0.30%（含销售服务费 0.10%） | −0.94pp / 1.48% | **首选（现有持仓）**，持有、定投继续 |
| 同基金 A 类 `013527.OF`（未持有） | 0.20% | — | 若日后在本席位新增资金走 A 类；存量不换 |

规模 net_asset 10.98 亿（2026-06-30）；赎回费 7 天内 1.50%、7 天后 0。基准口径全收益，跟踪质量在持仓基金里属于最好的一档。

## 6. 点位与仓位

- 推导：框架 A9 唯一 validated 的回撤分位阶梯。近 36 个月末收盘最高值 4,474.09（快照 §6b），状态历史分位点 P10 0.5222 / P25 0.5956 / P75 0.8842（n=262，自 2004-12）。当前状态 0.7911、分位 63.0，中间区。
- 点位（`level_at_drawdown_state`）：`add_below` **2,336.37**（目标 100%）、`buy_below` **2,664.77**（目标 50%）、`reduce_above` **3,955.99**（目标 30%）。当前 3,539.58。
- 读法：买入区在下方约 25%，减仓区在上方约 12%。`status=active`、工具 `hold`：定投继续，不一次性买；升破 3,955.99 减到上限的 30%（3 万，现持仓 0.88 万在其下，届时不动）；跌破 2,664.77 不自动买，转复评。
- 必须交代的代价：本指数在验证报告里只有 2 个适用折（F3 回撤 −1.5% 对 −37.6%、年化 +3.2% 对 +2.8%；F4 −21.6% 对 −38.6%、+7.4% 对 +0.1%），不足以单独出结论，沿用主指数恒指的结论；F3 平均仓位只有 2.1%——阶梯在这只指数上曾经几乎整整六年空仓，这就是代价。
- 仓位：`bet_group = cn-chemicals`，上限 100,000 = 70,000 ÷ 70%；现持仓 8,845。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 警戒阈值 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 指数相对 200 日均线（自动） | 执行侧日频计算 | 快照 §6：−9.65% | < 0 持续 | 告警 | 日 |
| 指数点位跌破买入锚点（自动） | 执行侧日频计算 | 3,539.58 | < 2,664.77 | 复评（不自动买） | 日 |
| 购进价格与出厂价格剪刀差（人工） | 统计局 PPI 月报 | 8 月 2 个百分点 | 扩大到 3 个百分点以上 | 复评 | 月 |
| 主要化工品价格（MDI、钾肥、碳酸锂）（人工） | 百川 / 卓创 / 公司公告 | MDI、TDI 8 月提价 | 回落至 2025 年低点区域 | 复评 | 月 |

## 8. 退出与复评

- 失效条件：① 主要化工品价格回落至 2025 年低点区域且龙头开工率回升（供给纪律失效）→ `reduce`；② 万华化学季度归母净利同比转负 → `close`。
- 最迟复评日 2026-11-23。
- 记分：基准 `H11025.CSI`，预登记 2026-09-23，置信度 50%，写卡时点位 3,539.58。

```json
{
  "card_schema_version": 1,
  "card_id": "cn-chemicals-tactical",
  "as_of_date": "2026-09-23",
  "supersedes": null,
  "framework": {"path": "framework/etf_framework.md", "version": "v0.1"},
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "tactical",
  "status": "active",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "000813.CSI",
    "index_name": "中证细分化工",
    "asset_type": "cyclical",
    "currency": "CNY",
    "counts_toward_sector_cap": true,
    "china_equity": true,
    "view_mismatch_note": "论点押一体化龙头的定价权（万华、巨化、宝丰、卫星约 20%），指数近三成是钾肥与锂盐资源周期；错位约三成",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {"value": 50, "source": "snapshot§3"},
      "max_constituent_weight_pct": {"value": 9.65, "source": "snapshot§3"},
      "top10_weight_pct": {"value": 42.65, "source": "snapshot§3"},
      "research_coverage_pct": {"value": 1.8, "source": "snapshot§3"},
      "top_constituents": [
        {"code": "600309.SH", "name": "万华化学", "weight_pct": {"value": 9.65, "source": "snapshot§3"}},
        {"code": "000792.SZ", "name": "盐湖股份", "weight_pct": {"value": 6.03, "source": "snapshot§3"}},
        {"code": "000408.SZ", "name": "藏格矿业", "weight_pct": {"value": 4.14, "source": "snapshot§3"}}
      ]
    }
  },
  "thesis": {
    "statement": "反内卷加龙头提价已把化工利润拉回上行段，但指数盈利含钾肥、锂盐、MDI 的周期高位价格，且油价站上 100 美元正在挤压中下游；持有、定投照常，不一次性追加，等回撤阶梯给点位",
    "evidence": [
      "万华化学 2026 上半年归母净利约 100.63 亿元、同比 +64.35%，二季度 63.45 亿元同比翻倍，8 月 MDI、TDI 再提价；万华占指数 9.65%",
      "盐湖股份 2026 上半年营收 130.52 亿元、+79.88%，归母净利 61.69 亿元、+137.88%，钾肥产销两旺、锂盐放量；盐湖 6.03%、藏格 4.14%",
      "反内卷通过政策端对无序扩产设边界、协会与龙头自律开工率与价格；反倾销落地、全球炼能进入紧平衡"
    ],
    "counter_evidence": [
      "布伦特 9 月 9–11 日结算连续三日站上 100 美元，8 月购进价格 +5.8% 高于出厂价 +3.8%（剪刀差 2 个百分点）；指数 51.0% 化工原料、15.0% 化纤正处被挤的一段",
      "钾肥、碳酸锂、MDI 都在价格高位，PE 17.86 的 25.8 分位是景气利润压低 PE 的形状；PB 2.31 在 47.0 分位只是中位数"
    ],
    "horizon_months": 18
  },
  "expectation": {
    "method": "mid_cycle",
    "scenarios": {
      "bear": {
        "inputs": {
          "eps_growth_pct": {"value": 0, "source": "ai_estimate", "note": "净资产零增长"},
          "dividend_yield_pct": {"value": 1.88, "source": "snapshot§4"},
          "current_multiple": {"value": 2.31, "source": "snapshot§4", "note": "自聚合 PB"},
          "terminal_multiple": {"value": 2.04, "source": "snapshot§4", "note": "PB 扩张窗 P25"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.2, "source": "snapshot§5", "note": "A 类年费"}
        },
        "valuation_change_pct": {"value": -4.06, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": -2.38, "source": "calc:scenario_annual_return"}
      },
      "base": {
        "inputs": {
          "eps_growth_pct": {"value": 5, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 1.88, "source": "snapshot§4"},
          "current_multiple": {"value": 2.31, "source": "snapshot§4"},
          "terminal_multiple": {"value": 2.31, "source": "snapshot§4"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.2, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 0, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 6.68, "source": "calc:scenario_annual_return"}
      },
      "bull": {
        "inputs": {
          "eps_growth_pct": {"value": 10, "source": "ai_estimate"},
          "dividend_yield_pct": {"value": 1.88, "source": "snapshot§4"},
          "current_multiple": {"value": 2.31, "source": "snapshot§4"},
          "terminal_multiple": {"value": 2.93, "source": "snapshot§4", "note": "PB 扩张窗 P75"},
          "years": {"value": 3, "source": "ai_estimate"},
          "drag_pct": {"value": 0.2, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 8.25, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 19.93, "source": "calc:scenario_annual_return"}
      }
    },
    "valuation_state": {
      "index_code": "000813.CSI",
      "metric": "pb",
      "value": {"value": 2.31, "source": "snapshot§4", "note": "自聚合、指数权重口径；周期席位按 A5 用 PB，PE 17.86（分位 25.8）只作参考"},
      "percentile_expanding": {"value": 47.0, "source": "snapshot§4"},
      "percentile_10y": {"value": 42.2, "source": "snapshot§4"},
      "sample_n": {"value": 151, "source": "snapshot§4"},
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "本席位只有一只持仓；新增资金走同基金 A 类，存量不换",
    "list": [
      {"code": "013528.OF", "name": "嘉实中证细分化工产业主题ETF联接-C", "instrument_type": "otc_fund", "share_class": "C", "currency": "CNY", "platform_account": "支付宝", "role": "primary", "action": "hold", "reason": "现有持仓，持有、定投继续；年费 0.30%，TD 年化 -0.94pp、TE 1.48%（全收益口径），规模 10.98 亿"},
      {"code": "013527.OF", "name": "嘉实中证细分化工产业主题ETF联接-A", "instrument_type": "otc_fund", "share_class": "A", "currency": "CNY", "platform_account": "支付宝", "role": "rejected", "action": "none", "reason": "未持有；年费 0.20%，若日后新增资金走 A 类，存量不值一次申赎"}
    ]
  },
  "trade_rules": {"min_holding_days": 7, "purchase_limit_note": null},
  "decision": {
    "rule_refs": ["A5", "A8", "A9", "A10", "A13"],
    "anchors": {
      "basis": "index_level",
      "index_code": "000813.CSI",
      "add_below": {
        "level": {"value": 2336.37, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 100, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 4474.09, "source": "snapshot§6"}, "state": {"value": 0.5222, "source": "snapshot§6", "note": "回撤状态扩张窗 P10"}},
        "rationale": "回撤状态回到自身历史 P10：相当于 2015–2016、2018、2024 的周期底部区域"
      },
      "buy_below": {
        "level": {"value": 2664.77, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 50, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 4474.09, "source": "snapshot§6"}, "state": {"value": 0.5956, "source": "snapshot§6", "note": "回撤状态扩张窗 P25"}},
        "rationale": "回撤状态回到自身历史 P25；当前 3,539.58 在其上方约 33%。跌破时不自动买而是复评（见监控）"
      },
      "reduce_above": {
        "level": {"value": 3955.99, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 30, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 4474.09, "source": "snapshot§6"}, "state": {"value": 0.8842, "source": "snapshot§6", "note": "回撤状态扩张窗 P75"}},
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 12%）：升破即把这笔押注减到上限的 30%（3 万）；现持仓在其下，届时不动"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "cn-chemicals",
    "stress_drawdown_pct": {"value": -70, "source": "user:2026-09-18"},
    "loss_budget_cny": {"value": 70000, "source": "user:2026-09-23"},
    "standalone_cap_cny": {"value": 100000, "source": "calc:loss_budget_cap"}
  },
  "monitor_variables": [
    {"name": "指数相对 200 日均线", "kind": "auto", "metric": "index_vs_sma200_pct", "operator": "<", "threshold": {"value": 0, "source": "framework:A11"}, "condition_text": "收盘持续低于 200 日均线", "data_source": "执行侧日频计算", "current_text": "快照 §6：-9.65%，below", "frequency": "daily", "action": "alert", "action_note": ""},
    {"name": "指数点位跌破买入锚点", "kind": "auto", "metric": "index_level", "operator": "<", "threshold": {"value": 2664.77, "source": "calc:level_at_drawdown_state"}, "condition_text": "收盘跌破 buy_below（回撤状态 P25）", "data_source": "执行侧日频计算", "current_text": "快照 §6：3,539.58", "frequency": "daily", "action": "review", "action_note": "不自动买；复评论点后再决定是否用剩余额度加"},
    {"name": "购进价格与出厂价格剪刀差", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "工业购进价格同比高于出厂价格同比 3 个百分点以上", "data_source": "统计局 PPI 月报", "current_text": "8 月：购进 +5.8%、出厂 +3.8%，差 2 个百分点", "frequency": "monthly", "action": "review", "action_note": "成本挤压加深"},
    {"name": "主要化工品价格（MDI、钾肥、碳酸锂）", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "回落至 2025 年低点区域", "data_source": "百川 / 卓创 / 公司公告", "current_text": "MDI、TDI 8 月提价；盐湖钾肥、锂盐量价齐升", "frequency": "monthly", "action": "review", "action_note": "命中即触发失效条件①的评估"}
  ],
  "exit": {
    "invalidation": [
      {"name": "供给纪律失效", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "主要化工品价格回落至 2025 年低点区域且龙头开工率回升", "data_source": "百川 / 卓创 / 公司公告", "current_text": "未发生", "frequency": "monthly", "action": "reduce", "action_note": ""},
      {"name": "龙头利润转负", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "万华化学季度归母净利同比转负", "data_source": "季报", "current_text": "2026 二季度同比翻倍", "frequency": "event", "action": "close", "action_note": ""}
    ],
    "latest_review_date": "2026-11-23"
  },
  "scorecard": {
    "benchmark": {"code": "H11025.CSI", "name": "同一笔钱放在货币基金"},
    "preregistered_at": "2026-09-23",
    "confidence_pct": 50,
    "entry_ref_index_level": {"value": 3539.58, "source": "snapshot§6"}
  }
}
```
