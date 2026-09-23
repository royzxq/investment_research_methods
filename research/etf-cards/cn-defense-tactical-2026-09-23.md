# 决策卡：国防（中证国防）· 2026-09-23

> 席位：国防（框架 A1 第 10 席）。`card_id` = `cn-defense-tactical`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓金额按用户 2026-09-18 提供的数：鹏华中证国防指数(LOF)A `160630.SZ` 49,024 元，定投中。
> 快照 §0 与本席位相关的缺口：无。研究覆盖率 0%（成分无一在个股研究池内），本卡的行业事实全部来自联网检索，逐条给出处。

## 1. 投资任务

- 任务：`tactical`——押"十五五装备采购进入规模化下单 + 军贸出口扩张，行业盈利修复从中报延续到 2027 年"这一有期限的判断。记账币种人民币；计划持有 24 个月，最迟 2026-11-20 复评。
- 允许亏损：行业单笔亏损预算 7 万（用户 2026-09-23 拍板），按 −70% 压力跌幅反推单笔上限 10 万（`loss_budget_cap`）。
- 现状：持仓 49,024 元，占上限 49%，未超限。定投继续。压力情景（−70%）下亏约 3.4 万，约占全部资产 136 万的 2.5%。
- 不买它时钱放哪（记分基准）：中证货币基金指数 `H11025.CSI`。

## 2. 核心判断

**主判断**：军工行业的盈利修复已经在 2026 年中报出现，但指数权重最大的航空主机厂仍在利润下滑，修复尚未到达指数的主体；在"十五五"规模化订单落地之前，持有并继续定投，不做一次性买入，等阶梯给出的点位。

支撑证据：
1. 行业层面盈利修复：军工板块 2026 年上半年营收 4,159.95 亿元（同比 +7.93%），归母净利润 253.26 亿元（同比 +20.98%），毛利率回升 0.92 个百分点至 18.85%（[中信建投，腾讯新闻 2026-09-13](https://news.qq.com/rain/a/20260913A06WN400)）。
2. 订单先行指标转正：2026 年一季度板块合同负债较年初增长 15.68%、存货较年初增长 7.08%，行业进入"订单修复—业绩与估值修复"阶段（[中信建投，新浪财经 2026-09-16](https://finance.sina.com.cn/wm/2026-09-16/doc-inirykpk3192440.shtml)）。
3. 需求侧两个催化：随"十五五"装备目录逐步明确，规模化订单下达渐近；9·3 阅兵后多款装备亮相，军贸订单陆续落地，行业形成"内需筑基、外贸扩张、民用反哺"格局（[财联社 2026-09](https://www.cls.cn/detail/1089312)、[新浪财经 2026-09-16](https://finance.sina.com.cn/wm/2026-09-16/doc-inirykpk3192440.shtml)）。

反证：
1. 修复没有到达指数主体：指数 43.2% 权重是航空（快照 §3），而本轮增长主要来自船舶、地面兵装与军贸，航空航天核心赛道利润仍同比下滑（[腾讯新闻 2026-09-13](https://news.qq.com/rain/a/20260913A06WN400)）。第二大成分中航沈飞 2026 年中报营收 61.91 亿元（−57.68%）、归母净利润 4.73 亿元（−58.37%），原因是新型装备配套交付节奏（[腾讯新闻 2026-08-27](https://news.qq.com/rain/a/20260827A09PCD00)）。
2. "订单渐近"是一个日期不确定的叙事，指数 2026 年内已跌约 15%（[腾讯新闻 2026-09-09](https://news.qq.com/rain/a/20260909A04IO600)），估值并不便宜——自聚合 PE 63.49、扩张窗分位 60.9（快照 §4）；规划批复与下单时点若再推迟一两个季度，等待期的机会成本由持仓者承担。

## 3. 指数匹配

- 编制（A4 四问）：中证国防指数，50 只成分，前十大合计 47.70%，最大单一成分睿创微纳 8.28%；行业权重航空 43.2%、元器件 15.1%、通信设备 12.8%、小金属 6.1%（快照 §3，权重日 2026-08-31）。市值加权，半年调样；近 12 个月调入 5 只（合计 3.4%）、调出 5 只（4.9%），换手低。
- 观点与持仓的错位：论点里的增长来源（船舶、兵装、军贸）在指数里权重很小，指数是一笔"航空主机厂 + 航空配套"的押注；沈飞、航发动力、西飞、机载四家合计约 19%（快照 §3 前十大）。军贸受益者（无人机、导弹、雷达）分散在通信设备与元器件里。**买这个指数买到的是"十五五航空装备放量"，不是"军贸"。**
- 历史：指数 2011-06-30 基日、2014-04-15 发布（快照 §6b 状态样本自 2011-06），2014 年前为回溯值。

## 4. 预期与估值

- 估值状态（快照 §4 自聚合，指数权重口径）：PE_TTM 63.49，扩张窗分位 60.9（n=138，自 2014-04），10 年窗分位 71.9；PB 3.19，扩张窗分位 31.9；股息率 0.56%；亏损股权重 5.70%（低于 15%，PE 可用）。PE 中性偏贵、PB 偏便宜——盈利在底部，ROE 压着 PE 抬高。
- 方法：`return_decomposition`，5 年，实施拖累按持仓工具年费 1.20%（快照 §5），股息率 0.56%（§4）。期末倍数只取 §4 分位点：熊 P10 39.58、基准 63.49（估值零变化）、牛 P75 72.96；盈利增速是本卡假设（`ai_estimate`）：熊 5%、基准 15%、牛 25%。
  - 熊：年化 −4.66%（估值年化 −9.02%）；基准：+14.36%；牛：+27.18%。
- 读法：基准情景靠盈利修复就能给两位数回报，这是持有的理由；熊情景里估值压缩会吃掉全部盈利增长，这是不一次性买入的理由。

## 5. 工具比选（同指数比"谁更可靠更便宜"）

| 工具 | 年费 | TD 年化 / TE | 赎回费 | 结论 |
|---|---|---|---|---|
| 鹏华中证国防指数(LOF)A `160630.SZ`（持 49,024） | 1.20% | +1.28pp / 4.00%（3 年，total_return 口径） | 7 天内 1.5%、7–365 天 0.50%、365–730 天 0.25% | **首选（现有持仓）**；持有，定投继续。费率是池内最贵，但 3 年跟踪偏离为正、规模 25.96 亿 |
| 鹏华中证国防指数(LOF)C `012041.OF`（未持有） | 1.30% | — | — | 落选：比 A 类多 0.10% 销售服务费 |
| 鹏华中证国防指数(LOF)I `025140.OF`（未持有） | 1.30% | — | — | 落选：同上 |
| 鹏华中证国防ETF `512670.SH`（未持有，场内） | 0.40%（管理 0.30% + 托管 0.10%；来源 2026-09-19 tushare fund_basic 实测，快照 §5 未覆盖） | — | 场内无赎回费 | 落选于本卡：需券商账户交易；**若日后在本席位新增大额资金，优先它**——年费低 0.80 个百分点 |

处置：LOF A 的赎回费阶梯使换出成本随持有时间递减（满两年 0），现持仓不因费率换出；定投继续走 A 类。

## 6. 点位与仓位

- 推导：框架 A9 唯一 validated 的回撤分位阶梯。`399973.SZ` 近 36 个月末收盘最高值 2,174.45（快照 §6b），状态历史分位点 P10 0.4805 / P25 0.5658 / P75 0.8441（n=184，自 2011-06）。
- 点位（`level_at_drawdown_state`，按快照打印的状态复算）：`add_below` **1,044.82**（目标 100%）、`buy_below` **1,230.30**（目标 50%）、`reduce_above` **1,835.45**（目标 30%）。当前 1,599.31（状态 0.7355，分位 56.0），在中间区。
- 读法：买入区在当前下方约 23%，减仓区在上方约 15%。本卡 `status=active`、工具 `hold`：不做一次性买入，定投继续；升破 1,835.45 时把这笔押注减到上限的 30%（3 万）；跌破 1,230.30 时不自动买，转为复评——若届时"十五五"订单已可见，用剩余额度（约 5 万）在买入区加。
- 必须交代的代价：该指数在规则验证里适用折不足（价格史自 2011-06），结论沿用主指数恒指（四折回撤全部更优、年化平均 +5.1%）；阶梯在趋势性上涨段会长期不加仓，2023 年以来标普的机会成本是例子。
- 仓位：`bet_group = cn-defense`，上限 100,000 = 70,000 ÷ 70%。现持仓 49,024（49%）。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 警戒阈值 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 指数相对 200 日均线（自动） | 执行侧日频计算 | 快照 §6：−10.98%，below | < 0 持续 | 告警 | 日 |
| 指数点位跌破买入锚点（自动） | 执行侧日频计算 | 1,599.31 | < 1,230.30 | 复评（不自动买） | 日 |
| "十五五"规划及装备目录批复、规模化订单公告（人工） | 国务院/军方公告、主机厂公告（合同负债） | 装备目录逐步明确，规模化订单未下达 | 主机厂公告大额订单或合同负债单季环比 +30% 以上 | 复评（考虑用剩余额度加） | 事件 |
| 航空主机厂利润增速（人工） | 中航沈飞、航发动力、中航西飞季报 | 沈飞 2026 中报净利润 −58.37% | 连续两个季报同比转正 → 修复到达指数主体 | 复评 | 季 |

## 8. 退出与复评

- 失效条件：① "十五五"规划批复后一年内，板块合同负债同比转负（订单叙事证伪）→ `close`；② 航空主机厂连续两个年度利润同比下滑（2026、2027 年报）→ `reduce`。
- 最迟复评日 2026-11-20（三季报与规划进展落地后）。
- 记分：基准 `H11025.CSI`，预登记 2026-09-23，置信度 50%，写卡时点位 1,599.31。

```json
{
  "card_schema_version": 1,
  "card_id": "cn-defense-tactical",
  "as_of_date": "2026-09-23",
  "supersedes": null,
  "framework": {"path": "framework/etf_framework.md", "version": "v0.1"},
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "tactical",
  "status": "active",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "399973.SZ",
    "index_name": "中证国防",
    "asset_type": "sector",
    "currency": "CNY",
    "counts_toward_sector_cap": true,
    "china_equity": true,
    "view_mismatch_note": "论点里的增长来源（船舶、兵装、军贸）在指数里权重很小；指数 43.2% 是航空，实际买到的是“十五五航空装备放量”",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {"value": 50, "source": "snapshot§3"},
      "max_constituent_weight_pct": {"value": 8.28, "source": "snapshot§3"},
      "top10_weight_pct": {"value": 47.7, "source": "snapshot§3"},
      "research_coverage_pct": {"value": 0.0, "source": "snapshot§3"},
      "top_constituents": [
        {"code": "688002.SH", "name": "睿创微纳", "weight_pct": {"value": 8.28, "source": "snapshot§3"}},
        {"code": "600760.SH", "name": "中航沈飞", "weight_pct": {"value": 6.33, "source": "snapshot§3"}},
        {"code": "600893.SH", "name": "航发动力", "weight_pct": {"value": 6.13, "source": "snapshot§3"}}
      ]
    }
  },
  "thesis": {
    "statement": "军工盈利修复已在 2026 年中报出现，但指数权重最大的航空主机厂仍在利润下滑；十五五规模化订单落地前持有并继续定投，不做一次性买入，等阶梯点位",
    "evidence": [
      "军工板块 2026 上半年营收 +7.93%、归母净利润 +20.98%，毛利率回升 0.92 个百分点至 18.85%",
      "2026 一季度板块合同负债较年初 +15.68%、存货 +7.08%，订单先行指标转正",
      "十五五装备目录逐步明确、规模化订单渐近；9·3 阅兵后军贸订单陆续落地"
    ],
    "counter_evidence": [
      "修复未到指数主体：指数 43.2% 是航空，而增长来自船舶、兵装与军贸；中航沈飞 2026 中报营收 -57.68%、净利润 -58.37%",
      "订单渐近的日期不确定，指数 2026 年内已跌约 15%，自聚合 PE 63.49、分位 60.9 并不便宜，推迟的等待成本由持仓者承担"
    ],
    "horizon_months": 24
  },
  "expectation": {
    "method": "return_decomposition",
    "scenarios": {
      "bear": {
        "inputs": {
          "eps_growth_pct": {"value": 5, "source": "ai_estimate", "note": "航空主机厂交付节奏持续拖累"},
          "dividend_yield_pct": {"value": 0.56, "source": "snapshot§4"},
          "current_multiple": {"value": 63.49, "source": "snapshot§4"},
          "terminal_multiple": {"value": 39.58, "source": "snapshot§4", "note": "PE 扩张窗 P10"},
          "years": {"value": 5, "source": "ai_estimate"},
          "drag_pct": {"value": 1.2, "source": "snapshot§5", "note": "160630.SZ 年费合计"}
        },
        "valuation_change_pct": {"value": -9.02, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": -4.66, "source": "calc:scenario_annual_return"}
      },
      "base": {
        "inputs": {
          "eps_growth_pct": {"value": 15, "source": "ai_estimate", "note": "中报净利润 +20.98% 的修复趋势打折延续"},
          "dividend_yield_pct": {"value": 0.56, "source": "snapshot§4"},
          "current_multiple": {"value": 63.49, "source": "snapshot§4"},
          "terminal_multiple": {"value": 63.49, "source": "snapshot§4", "note": "估值零变化"},
          "years": {"value": 5, "source": "ai_estimate"},
          "drag_pct": {"value": 1.2, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 0.0, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 14.36, "source": "calc:scenario_annual_return"}
      },
      "bull": {
        "inputs": {
          "eps_growth_pct": {"value": 25, "source": "ai_estimate", "note": "十五五规模化订单 + 军贸"},
          "dividend_yield_pct": {"value": 0.56, "source": "snapshot§4"},
          "current_multiple": {"value": 63.49, "source": "snapshot§4"},
          "terminal_multiple": {"value": 72.96, "source": "snapshot§4", "note": "PE 扩张窗 P75"},
          "years": {"value": 5, "source": "ai_estimate"},
          "drag_pct": {"value": 1.2, "source": "snapshot§5"}
        },
        "valuation_change_pct": {"value": 2.82, "source": "calc:scenario_annual_return"},
        "annual_return_pct": {"value": 27.18, "source": "calc:scenario_annual_return"}
      }
    },
    "valuation_state": {
      "index_code": "399973.SZ",
      "metric": "pe_ttm",
      "value": {"value": 63.49, "source": "snapshot§4", "note": "自聚合、指数权重口径；PB 3.19 分位 31.9 偏便宜，盈利在底部抬高了 PE"},
      "percentile_expanding": {"value": 60.9, "source": "snapshot§4"},
      "percentile_10y": {"value": 71.9, "source": "snapshot§4"},
      "sample_n": {"value": 138, "source": "snapshot§4"},
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "本席位只有一只持仓，bet_group=cn-defense 与 card_id 一一对应",
    "list": [
      {"code": "160630.SZ", "name": "鹏华中证国防指数(LOF)-A", "instrument_type": "otc_fund", "share_class": "A", "currency": "CNY", "platform_account": "支付宝", "role": "primary", "action": "hold", "reason": "现有持仓；年费 1.20% 为池内最贵，但 3 年 TD +1.28pp、规模 25.96 亿；赎回费满两年为 0，不因费率换出"},
      {"code": "012041.OF", "name": "鹏华中证国防指数(LOF)-C", "instrument_type": "otc_fund", "share_class": "C", "currency": "CNY", "platform_account": "支付宝", "role": "rejected", "action": "none", "reason": "未持有；比 A 类多 0.10% 销售服务费"},
      {"code": "512670.SH", "name": "鹏华中证国防ETF", "instrument_type": "exchange_etf", "share_class": null, "currency": "CNY", "platform_account": "券商账户", "role": "rejected", "action": "none", "reason": "未持有；年费 0.40% 比 LOF 低 0.80 个百分点，但需场内账户。日后在本席位新增大额资金时优先它"}
    ]
  },
  "trade_rules": {"min_holding_days": 730, "purchase_limit_note": "LOF A 赎回费阶梯：7 天内 1.5%、7–365 天 0.50%、365–730 天 0.25%、满两年 0"},
  "decision": {
    "rule_refs": ["A8", "A9", "A10", "A13"],
    "anchors": {
      "basis": "index_level",
      "index_code": "399973.SZ",
      "add_below": {
        "level": {"value": 1044.82, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 100, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 2174.45, "source": "snapshot§6"}, "state": {"value": 0.4805, "source": "snapshot§6", "note": "回撤状态扩张窗 P10"}},
        "rationale": "回撤状态回到自身历史 P10：相当于 2018 年与 2022–2024 年的底部区域"
      },
      "buy_below": {
        "level": {"value": 1230.3, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 50, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 2174.45, "source": "snapshot§6"}, "state": {"value": 0.5658, "source": "snapshot§6", "note": "回撤状态扩张窗 P25"}},
        "rationale": "回撤状态回到自身历史 P25；跌破时不自动买而是复评，届时若十五五订单已可见，用剩余额度在买入区加"
      },
      "reduce_above": {
        "level": {"value": 1835.45, "source": "calc:level_at_drawdown_state"},
        "target_ratio_pct": {"value": 30, "source": "framework:A13"},
        "inputs": {"rolling_high": {"value": 2174.45, "source": "snapshot§6"}, "state": {"value": 0.8441, "source": "snapshot§6", "note": "回撤状态扩张窗 P75"}},
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 16%）：升破即把这笔押注减到上限的 30%（3 万）"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "cn-defense",
    "stress_drawdown_pct": {"value": -70, "source": "user:2026-09-18"},
    "loss_budget_cny": {"value": 70000, "source": "user:2026-09-23"},
    "standalone_cap_cny": {"value": 100000, "source": "calc:loss_budget_cap"}
  },
  "monitor_variables": [
    {"name": "指数相对 200 日均线", "kind": "auto", "metric": "index_vs_sma200_pct", "operator": "<", "threshold": {"value": 0, "source": "framework:A11"}, "condition_text": "收盘持续低于 200 日均线", "data_source": "执行侧日频计算", "current_text": "快照 §6：-10.98%，below", "frequency": "daily", "action": "alert", "action_note": ""},
    {"name": "指数点位跌破买入锚点", "kind": "auto", "metric": "index_level", "operator": "<", "threshold": {"value": 1230.3, "source": "calc:level_at_drawdown_state"}, "condition_text": "收盘跌破 buy_below（回撤状态 P25）", "data_source": "执行侧日频计算", "current_text": "快照 §6：1,599.31", "frequency": "daily", "action": "review", "action_note": "不自动买；复评十五五订单进展后决定是否用剩余额度加"},
    {"name": "十五五规划及装备目录批复、规模化订单公告", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "主机厂公告大额订单，或合同负债单季环比增长 30% 以上", "data_source": "国务院/军方公告、主机厂季报合同负债", "current_text": "装备目录逐步明确，规模化订单未下达", "frequency": "event", "action": "review", "action_note": "考虑用剩余额度在买入区加"},
    {"name": "航空主机厂利润增速", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "沈飞、航发动力、西飞连续两个季报归母净利润同比转正", "data_source": "季报", "current_text": "中航沈飞 2026 中报净利润 -58.37%", "frequency": "quarterly", "action": "review", "action_note": "修复到达指数主体的信号"}
  ],
  "exit": {
    "invalidation": [
      {"name": "订单叙事证伪", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "十五五规划批复后一年内，板块合同负债同比转负", "data_source": "板块季报合同负债汇总（券商研报）", "current_text": "2026Q1 合同负债较年初 +15.68%", "frequency": "quarterly", "action": "close", "action_note": ""},
      {"name": "航空主机厂持续下滑", "kind": "manual", "metric": null, "operator": null, "threshold": {"value": null, "source": null}, "condition_text": "航空主机厂 2026、2027 两个年度归母净利润连续同比下滑", "data_source": "年报", "current_text": "2026 中报下滑", "frequency": "event", "action": "reduce", "action_note": ""}
    ],
    "latest_review_date": "2026-11-20"
  },
  "scorecard": {
    "benchmark": {"code": "H11025.CSI", "name": "同一笔钱放在货币基金"},
    "preregistered_at": "2026-09-23",
    "confidence_pct": 50,
    "entry_ref_index_level": {"value": 1599.31, "source": "snapshot§6"}
  }
}
```
