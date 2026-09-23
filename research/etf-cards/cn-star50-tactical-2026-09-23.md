# 决策卡：科创50 · 2026-09-23

> 席位：科创50（框架 A1 第 3 席；用户裁定为行业席位，占行业额度）。`card_id` = `cn-star50-tactical`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓金额按用户 2026-09-18 提供的数：工银瑞信上证科创板50成份ETF联接C `011615.OF` 11,774 元，定投中。
> 快照 §0 与本席位相关的缺口：无。但快照 §3 的成分权重日是 2026-08-31，指数 2026-09-14 已生效三季度调样（调入盛合晶微、影石创新、睿创微纳、华丰科技、屹唐股份，调出凯赛生物、中无人机、和辉光电、恒玄科技、惠泰医疗——[21 财经 2026-08-28](https://m.21jingji.com/article/20260828/herald/48c4970dfcb16b90ea57916c074fe1c7.html)），下次快照才反映 `[需人工补充]`。

## 1. 投资任务

- 任务：`tactical`——押"AI 算力需求驱动的国产半导体（芯片设计、设备、代工）盈利兑现"这一有期限的判断。记账币种人民币；计划持有 18 个月，最迟 2026-11-20 复评。
- 允许亏损：行业单笔亏损预算 7 万（用户 2026-09-23 拍板），按 −70% 压力跌幅反推单笔上限 10 万（`loss_budget_cap`）。压力跌幅 −70% 对这只指数不算苛刻：它的成分是池内波动最大的一组，回撤状态历史 P10 为 0.5363（即从 36 月高点跌 46%）。
- 现状：持仓 11,774 元，占上限 12%，未超限。定投继续。压力情景下亏约 0.8 万。
- 不买它时钱放哪（记分基准）：中证货币基金指数 `H11025.CSI`。

## 2. 核心判断

**主判断**：科创50 是一笔 80% 押在半导体上的 AI 算力叙事，盈利预期很高、价格已经计入大半——上半年涨 64% 后回撤 20%，现在在中间区；小仓位持有并继续定投，不做一次性买入，等阶梯点位。

支撑证据：
1. 盈利预期：Wind 一致预期显示科创50 指数 2026 年归母净利润同比增速已超过 170%（[东方财富 财富号 2026-04-27](https://caifuhao.eastmoney.com/news/20260427171229408930100)）。
2. 核心公司兑现中：海光信息、寒武纪 2026 年一季度业绩继续高增；中芯国际 2026 年继续扩产，代工环节业绩确定性强（[东方财富 财富号 2026-04-24](https://caifuhao.eastmoney.com/news/20260424231220798333920)）。
3. 指数纯度上升：2026 年三季度调样 5 进 5 出，调入盛合晶微等半导体/硬科技公司、调出凯赛生物、惠泰医疗等，调整后指数总市值 5.9 万亿元（[新浪科技 2026-08-28](https://finance.sina.com.cn/tech/roll/2026-08-28/doc-inipwtfp5760990.shtml)、[腾讯新闻 2026-08-31](https://news.qq.com/rain/a/20260831A04ZAO00)）。

反证：
1. 价格已计入高增：自聚合 PB 7.76、扩张窗分位 84.0，股息率 0.27%、分位 9.3（快照 §4）；2026 年上半年指数涨 64.25%，7、8 月回撤超过 20 个百分点，市场对拥挤度的担忧已经兑现过一次（[腾讯新闻 2026-08-31](https://news.qq.com/rain/a/20260831A0534900)）。
2. 集中与脆弱：半导体 80.2%、前十大 58.90%、亏损股权重 16.07%（快照 §3、§4）——单一景气周期与单一政策（美国出口管制）能同时打击全部成分；亏损股权重超过 15%，PE 77.17 不可作估值锚（框架 A5）。

## 3. 指数匹配

- 编制（A4 四问）：科创50，上证科创板市值最大、流动性最好的 50 只；50 只成分，前十大 58.90%，最大单一成分寒武纪 8.41%；行业权重半导体 80.2%，其余专用机械 2.7%、医疗保健 2.5%、软件服务 2.5%（快照 §3，权重日 2026-08-31）。市值加权、单一成分设权重上限，季度调样；近 12 个月调入 10 只（现权重合计 18.4%）、调出 10 只（5.5%），换手明显高于其他席位——新进公司权重大，指数在追随市值扩张。
- 观点与持仓的错位：论点是"AI 算力驱动的国产半导体"，指数 80% 就是半导体，错位小；但指数是"科创板市值最大的 50 家"而不是"半导体龙头"，权重随市值追涨，牛市后半段的调入会在高位买入（本次调样即在上半年大涨之后）。
- 历史：指数 2019-12-31 基日、2020-07-23 发布（快照 §6b 状态样本自 2019-12，n=82），没有经历完整周期。

## 4. 预期与估值

- 估值状态（快照 §4 自聚合，指数权重口径）：**PB 7.76，扩张窗分位 84.0**（n=75，自 2020-07）；PE_TTM 77.17、分位 69.3 只作参考——亏损股权重 16.07% 超过框架 A5 的 15% 降级线，PE 不可靠；股息率 0.27%，分位 9.3。三个读数一致：贵。
- 方法：`scenario_only`（PE 不可用，PB 无法做回报分解）。三情景是本卡的判断，标 `ai_estimate`：
  - 熊：AI 资本开支放缓或出口管制扩大到设计与设备主体，估值向 PB P50（5.42）回归，年化 −30%。
  - 基准：盈利如一致预期兑现但估值随之消化，年化 +10%（估值零变化）。
  - 牛：算力需求超预期、国产替代加速，年化 +35%。
- 读法：这是池内向上弹性最大、向下也最深的一笔；小仓位、只用定投、把加仓留给阶梯的买入区是与之匹配的做法。

## 5. 工具比选（同指数比"谁更可靠更便宜"）

| 工具 | 年费 | TD 年化 / TE | 赎回费 | 结论 |
|---|---|---|---|---|
| 工银瑞信科创50联接C `011615.OF`（持 11,774） | 0.45%（含销售服务费 0.10%） | −2.17pp / 2.38%（3 年，total_return 口径） | 7 天内 1.5%、7–30 天 0.10%、30 天后 0 | **首选（现有持仓）**；持有，定投继续 |
| 工银瑞信科创50联接A `011614.OF`（未持有） | 0.35% | — | — | 落选于本卡（不新增一次性资金）；**定投若持有超过一年，A 类更便宜 0.10%/年**，可考虑把定投计划改到 A 类，存量不动 |
| 工银瑞信科创50联接Y `022932.OF`（未持有） | 0.20% | — | — | 落选：Y 份额限个人养老金账户 |
| 工银瑞信科创50联接E `020750.OF`（未持有） | 0.45% | — | — | 落选：与 C 类同价 |

TD 年化 −2.17pp 明显大于年费 0.45%，说明联接基金在指数大涨年份的现金拖累（申购资金到位滞后）显著；这是所有科创50 联接基金的共性，不构成换工具的理由。

## 6. 点位与仓位

- 推导：框架 A9 唯一 validated 的回撤分位阶梯。`000688.SH` 近 36 个月末收盘最高值 2,207.86（快照 §6b），状态历史分位点 P10 0.5363 / P25 0.6325 / P75 0.9405（n=82，自 2019-12）。
- 点位（`level_at_drawdown_state`，按快照打印的状态复算）：`add_below` **1,184.08**（目标 100%）、`buy_below` **1,396.47**（目标 50%）、`reduce_above` **2,076.49**（目标 30%）。当前 1,652.63（状态 0.7485，分位 41.5），在中间区。
- 读法：买入区在当前下方约 16%，减仓区在上方约 26%。本卡 `status=active`、工具 `hold`：不做一次性买入，定投继续；升破 2,076.49 时把这笔押注减到上限的 30%（3 万，现持仓 1.2 万本就在其下，届时只是停止定投）；跌破 1,396.47 时不自动买，转为复评——若盈利兑现路径未变，用额度在买入区加到 50%（5 万）。
- 必须交代的代价：该指数价格史自 2019-12，规则验证里适用折不足，结论沿用主指数恒指（四折回撤全部更优）；阶梯在趋势性上涨段会长期不加仓——上半年 +64% 这种行情里它只会持有存量。历史样本只有 82 个月且含一轮完整的涨跌，分位点的代表性弱于老指数。
- 仓位：`bet_group = cn-star50`，上限 100,000 = 70,000 ÷ 70%。现持仓 11,774（12%）。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 警戒阈值 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 指数相对 200 日均线（自动） | 执行侧日频计算 | 快照 §6：+4.84%，above | < 0 持续 | 告警 | 日 |
| 指数点位跌破买入锚点（自动） | 执行侧日频计算 | 1,652.63 | < 1,396.47 | 复评（不自动买） | 日 |
| 美国对华半导体出口管制/实体清单变化（人工） | 美国商务部 BIS 公告 | 无新增针对成分公司主体的限制 | 寒武纪、海光、中微、中芯任一被新增实质性限制 | 复评 | 事件 |
| 核心成分季报营收增速（人工） | 寒武纪、海光、中芯国际、中微季报 | 2026Q1 高增 | 三家以上单季营收同比增速降到 30% 以下 | 复评 | 季 |
| 指数调样（人工） | 上交所/中证公告（6 月、12 月） | 2026-09-14 已生效 5 进 5 出 | 半导体权重降到 60% 以下或前十大变动 3 只以上 | 复评（论点与指数是否仍匹配） | 事件 |

## 8. 退出与复评

- 失效条件：① 美国将新的实质性限制（实体清单、EDA/设备断供）扩大到寒武纪、海光、中芯、中微等成分主体且业务受实质影响 → `reduce`；② 2026 年报指数归母净利润增速低于 50%（一致预期 170% 落空一半以上）→ `close`。
- 最迟复评日 2026-11-20（三季报后）。
- 记分：基准 `H11025.CSI`，预登记 2026-09-23，置信度 40%，写卡时点位 1,652.63。

```json
{
  "card_schema_version": 1,
  "card_id": "cn-star50-tactical",
  "as_of_date": "2026-09-23",
  "supersedes": null,
  "framework": {
    "path": "framework/etf_framework.md",
    "version": "v0.1"
  },
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "tactical",
  "status": "active",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "000688.SH",
    "index_name": "科创50",
    "asset_type": "sector",
    "currency": "CNY",
    "counts_toward_sector_cap": true,
    "china_equity": true,
    "view_mismatch_note": "指数 80.2% 是半导体，与“AI 算力驱动的国产半导体”论点错位小；但它按市值追涨调样（2026-09-14 调样在上半年大涨之后），不是半导体龙头指数",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {
        "value": 50,
        "source": "snapshot§3"
      },
      "max_constituent_weight_pct": {
        "value": 8.41,
        "source": "snapshot§3"
      },
      "top10_weight_pct": {
        "value": 58.9,
        "source": "snapshot§3"
      },
      "research_coverage_pct": {
        "value": 4.0,
        "source": "snapshot§3"
      },
      "top_constituents": [
        {
          "code": "688256.SH",
          "name": "寒武纪",
          "weight_pct": {
            "value": 8.41,
            "source": "snapshot§3"
          }
        },
        {
          "code": "688012.SH",
          "name": "中微公司",
          "weight_pct": {
            "value": 8.18,
            "source": "snapshot§3"
          }
        },
        {
          "code": "688981.SH",
          "name": "中芯国际",
          "weight_pct": {
            "value": 7.9,
            "source": "snapshot§3"
          }
        }
      ]
    }
  },
  "thesis": {
    "statement": "科创50 是一笔 80% 押在半导体上的 AI 算力叙事，盈利预期很高、价格已计入大半（上半年 +64% 后回撤 20%，处中间区）；小仓位持有并继续定投，不做一次性买入，等阶梯点位",
    "evidence": [
      "Wind 一致预期科创50 指数 2026 年归母净利润同比增速超过 170%",
      "海光信息、寒武纪 2026 一季度业绩继续高增；中芯国际 2026 年继续扩产，代工环节确定性强",
      "2026 三季度调样 5 进 5 出，调入盛合晶微等半导体公司、调出生物与医疗器械公司，指数纯度上升，调整后总市值 5.9 万亿元"
    ],
    "counter_evidence": [
      "自聚合 PB 7.76、分位 84.0，股息率 0.27%、分位 9.3：价格已计入高增；上半年 +64.25% 后 7–8 月回撤超 20 个百分点",
      "半导体 80.2%、前十大 58.90%、亏损股权重 16.07%：单一景气周期与美国出口管制能同时打击全部成分，PE 77.17 不可作估值锚"
    ],
    "horizon_months": 18
  },
  "expectation": {
    "method": "scenario_only",
    "scenarios": {
      "bear": {
        "inputs": null,
        "valuation_change_pct": {
          "value": null,
          "source": null
        },
        "annual_return_pct": {
          "value": -30,
          "source": "ai_estimate",
          "note": "AI 资本开支放缓或出口管制扩大到成分主体，PB 向 P50 回归"
        }
      },
      "base": {
        "inputs": null,
        "valuation_change_pct": {
          "value": 0,
          "source": "framework:A5"
        },
        "annual_return_pct": {
          "value": 10,
          "source": "ai_estimate",
          "note": "盈利如一致预期兑现但估值随之消化"
        }
      },
      "bull": {
        "inputs": null,
        "valuation_change_pct": {
          "value": null,
          "source": null
        },
        "annual_return_pct": {
          "value": 35,
          "source": "ai_estimate",
          "note": "算力需求超预期、国产替代加速"
        }
      }
    },
    "valuation_state": {
      "index_code": "000688.SH",
      "metric": "pb",
      "value": {
        "value": 7.76,
        "source": "snapshot§4",
        "note": "亏损股权重 16.07% 超过 15% 降级线，按框架 A5 用 PB；PE 77.17（分位 69.3）只作参考"
      },
      "percentile_expanding": {
        "value": 84.0,
        "source": "snapshot§4"
      },
      "percentile_10y": {
        "value": null,
        "source": null,
        "note": "估值史自 2020-07，不足 10 年"
      },
      "sample_n": {
        "value": 75,
        "source": "snapshot§4"
      },
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "本席位只有一只持仓，bet_group=cn-star50 与 card_id 一一对应",
    "list": [
      {
        "code": "011615.OF",
        "name": "工银瑞信上证科创板50成份ETF联接-C",
        "instrument_type": "otc_fund",
        "share_class": "C",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "primary",
        "action": "hold",
        "reason": "现有持仓；年费 0.45%，3 年 TD -2.17pp、TE 2.38%（联接基金在大涨年份的现金拖累，同类共性）"
      },
      {
        "code": "011614.OF",
        "name": "工银瑞信上证科创板50成份ETF联接-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "未持有；年费 0.35%，长期定投比 C 类便宜 0.10%/年，可考虑把定投计划改到 A 类，存量不动"
      },
      {
        "code": "022932.OF",
        "name": "工银瑞信上证科创板50成份ETF联接-Y",
        "instrument_type": "otc_fund",
        "share_class": "Y",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "未持有；Y 份额限个人养老金账户"
      }
    ]
  },
  "trade_rules": {
    "min_holding_days": 30,
    "purchase_limit_note": null
  },
  "decision": {
    "rule_refs": [
      "A5",
      "A8",
      "A9",
      "A10",
      "A13"
    ],
    "anchors": {
      "basis": "index_level",
      "index_code": "000688.SH",
      "snapshot_ref": null,
      "add_below": {
        "level": {
          "value": 1184.08,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 100,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 2207.86,
            "source": "snapshot§6"
          },
          "state": {
            "value": 0.5363,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P10"
          }
        },
        "rationale": "回撤状态回到自身历史 P10：从 36 月高点跌 46%，相当于 2022–2024 年的底部区域"
      },
      "buy_below": {
        "level": {
          "value": 1396.47,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 50,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 2207.86,
            "source": "snapshot§6"
          },
          "state": {
            "value": 0.6325,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P25"
          }
        },
        "rationale": "回撤状态回到自身历史 P25；跌破时不自动买而是复评，盈利兑现路径未变则用额度加到 50%"
      },
      "reduce_above": {
        "level": {
          "value": 2076.49,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 30,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 2207.86,
            "source": "snapshot§6"
          },
          "state": {
            "value": 0.9405,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P75"
          }
        },
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 6%）：升破即把这笔押注减到上限的 30%（3 万）；现持仓 1.2 万低于该目标，届时只停定投"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "cn-star50",
    "stress_drawdown_pct": {
      "value": -70,
      "source": "user:2026-09-18"
    },
    "loss_budget_cny": {
      "value": 70000,
      "source": "user:2026-09-23"
    },
    "standalone_cap_cny": {
      "value": 100000,
      "source": "calc:loss_budget_cap"
    }
  },
  "monitor_variables": [
    {
      "name": "指数相对 200 日均线",
      "kind": "auto",
      "metric": "index_vs_sma200_pct",
      "operator": "<",
      "threshold": {
        "value": 0,
        "source": "framework:A11"
      },
      "condition_text": "收盘持续低于 200 日均线",
      "data_source": "执行侧日频计算",
      "current_text": "快照 §6：+4.84%，above",
      "frequency": "daily",
      "action": "alert",
      "action_note": ""
    },
    {
      "name": "指数点位跌破买入锚点",
      "kind": "auto",
      "metric": "index_level",
      "operator": "<",
      "threshold": {
        "value": 1396.47,
        "source": "calc:level_at_drawdown_state"
      },
      "condition_text": "收盘跌破 buy_below（回撤状态 P25）",
      "data_source": "执行侧日频计算",
      "current_text": "快照 §6：1,652.63",
      "frequency": "daily",
      "action": "review",
      "action_note": "不自动买；复评盈利兑现路径后决定是否加到 50%"
    },
    {
      "name": "美国对华半导体出口管制/实体清单变化",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "寒武纪、海光、中微、中芯任一被新增实质性限制",
      "data_source": "美国商务部 BIS 公告",
      "current_text": "无新增针对成分主体的限制",
      "frequency": "event",
      "action": "review",
      "action_note": "命中即触发失效条件①的评估"
    },
    {
      "name": "核心成分季报营收增速",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "寒武纪、海光、中芯国际、中微中三家以上单季营收同比增速降到 30% 以下",
      "data_source": "季报",
      "current_text": "2026Q1 海光、寒武纪继续高增",
      "frequency": "quarterly",
      "action": "review",
      "action_note": ""
    },
    {
      "name": "指数调样",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "半导体权重降到 60% 以下，或前十大变动 3 只以上",
      "data_source": "上交所/中证指数公告（6 月、12 月）",
      "current_text": "2026-09-14 生效 5 进 5 出，快照权重尚未反映",
      "frequency": "event",
      "action": "review",
      "action_note": "论点与指数是否仍匹配"
    }
  ],
  "exit": {
    "invalidation": [
      {
        "name": "出口管制扩大到成分主体",
        "kind": "manual",
        "metric": null,
        "operator": null,
        "threshold": {
          "value": null,
          "source": null
        },
        "condition_text": "美国新的实质性限制（实体清单、EDA/设备断供）扩大到寒武纪、海光、中芯、中微等成分主体且业务受实质影响",
        "data_source": "美国商务部 BIS 公告、公司公告",
        "current_text": "未发生",
        "frequency": "event",
        "action": "reduce",
        "action_note": ""
      },
      {
        "name": "盈利预期落空",
        "kind": "manual",
        "metric": null,
        "operator": null,
        "threshold": {
          "value": null,
          "source": null
        },
        "condition_text": "2026 年报指数归母净利润增速低于 50%（一致预期 170% 落空一半以上）",
        "data_source": "年报汇总（Wind/券商）",
        "current_text": "一致预期 +170%",
        "frequency": "event",
        "action": "close",
        "action_note": ""
      }
    ],
    "latest_review_date": "2026-11-20"
  },
  "scorecard": {
    "benchmark": {
      "code": "H11025.CSI",
      "name": "同一笔钱放在货币基金"
    },
    "preregistered_at": "2026-09-23",
    "confidence_pct": 40,
    "entry_ref_index_level": {
      "value": 1652.63,
      "source": "snapshot§6"
    }
  }
}
```
