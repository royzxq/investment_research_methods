# 决策卡：恒生指数（核心席位）· 2026-09-25

> 席位：恒生指数（框架 A1 第 4 席，核心）。`card_id` = `hk-hsi-core`，首版。数据：`research/etf/snapshots/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓：盈富基金 02800.HK 2,500 股（盈立证券直持），按快照 §5 收盘 25.38 港元与 §7 人民币中间价 0.86062 折算约 54,606 元（用户 9/18 给的约数为 56,000）。不在支付宝定投范围内。
> 快照 §0 与本席位相关的缺口：港股指数无估值源；恒指成分与权重无现成源；02800 的费率与净值无源 `[需人工补充]`。

## 1. 投资任务

- 任务：`core`——港股整体 beta 的长期持有仓，记账币种人民币（工具以港元计价，折算按中间价）；计划持有 10 年，最迟 2026-12-25 复评。
- 允许亏损：核心席位上限表（用户 2026-09-19）：上限 10 万、压力跌幅 −66%（恒指 2007-10 高点 31,958 → 2008-10 低点 10,676）、亏损预算 6.6 万。
- **现状：约 54,606 元，占上限 55%。** 持有，不一次性追加；本席位没有定投。
- 不买它时钱放哪（记分基准）：`H11025.CSI`。

## 2. 核心判断

**主判断**：港股宽基的长期回报靠估值均值回归加股息，不靠盈利高增；恒指现在处于阶梯中间区、估值中位，本席位持有不追加，把买入留给阶梯给出的深跌档。

支撑证据：
1. 资金面：南向资金 2026-09-16 已连续 8 个交易日逆势净流入，9/14 单日净流入 44.71 亿港元（[腾讯新闻 2026-09-16](https://news.qq.com/rain/a/20260916A09D1N00)、[FX168 2026-09-14](https://www.fx168news.com/article/%E4%BA%9A%E5%A4%AA%E8%82%A1%E5%B8%82-1092125)）。港股是内地资金唯一能大规模配置的离岸中国资产。
2. 供给与生态：2026 年前 7 个月港股 IPO 融资 3,259.93 亿港元、101 家上市，时隔五年重回 3,000 亿以上（[21 财经 2026-08-05](https://m.21jingji.com/article/20260805/6ecaf56aa67ff4935be914cea3786f32.html)）。A+H 扩容使恒指的科技与新经济占比继续上升。
3. 规则验证：回撤分位阶梯以恒指为主指数、四折全部通过——F1 回撤 −18.3% 对满仓 −62.7%，F3 −12.0% 对 −50.1%，四折年化平均高 5.1 个点，对同均仓位恒定比例仍有 3.2 个点的择时技能（`research/etf/studies/timing-validation/etf-2026-09-18-rule-validation.md`）。

反证：
1. 利率面：美联储 2026 年 9 月把联邦基金利率上调至 3.75%–4.00%（[edigest 2026 议息](https://www.edigest.hk/%E7%90%86%E8%B2%A1/%E7%BE%8E%E5%9C%8B%E5%8A%A0%E6%81%AF%E5%BD%B1%E9%9F%BF-2019788/)），港元联系汇率下 HIBOR 跟随，港股估值分母端承压。
2. 阶梯的代价：验证报告里恒指 F2（2011–2016）阶梯全程空仓、年化 +3.7% 全是现金收益；F3 平均仓位只有 6.3%。本规则在横盘市里长期空仓，不是"持有港股"的替代——所以本卡是持有 + 阶梯，不是只按阶梯。

## 3. 指数匹配

- 编制（恒生指数公司）：港股市值最大、流动性筛选后的成分股，自由流通市值加权、单一成分 8% 上限；成分数已扩至 80 余只并向 100 只推进。快照对港股成分无源，结构读数 `[需人工补充]`；金融与互联网平台合计占比高于 A 股宽基，行业均衡度不如 A500。
- 历史：1964 年基日，快照 §6b 的回撤状态样本 730 个月，是池内最长的序列，也是规则验证的主指数。
- 观点与持仓错位：本卡不押行业观点，错位度低；需要提醒的是"港股 beta"里约三成是同时在 A 股上市的公司，与 A500 席位有重叠。

## 4. 预期与估值

- 无指数口径估值源。恒生官方月报 PE 约 14.16 倍（乐咕乐股 2026-08-31 口径 `[需人工补充]`，未进卡的 JSON）；历史上恒指 PE 8–20 倍区间，14 倍居中。
- 方法 `scenario_only`，三情景为本卡判断（`ai_estimate`）：熊 −15%（美元利率 4% 以上维持 + 盈利下修，回到 2022 年低点区域）；基准 +6%（盈利低个位数 + 约 3.5% 股息，估值零变化）；牛 +18%（南向持续流入 + 降息周期，估值向 18 倍修复）。
- 位置：快照 §6b 恒指 36 月高点 27,387.11，当前 24,750.78，状态 0.9037、分位 57.4，中间区。

## 5. 工具比选

| 工具 | 渠道 | 年费 | 结论 |
|---|---|---|---|
| 盈富基金 `02800.HK`（持 2,500 股） | 盈立证券直持 | 管理费极低（公开资料约 0.019%，未核 `[需人工补充]`），无红利税 | **首选（现有持仓）**，持有 |
| 华夏沪港通恒生ETF联接 A `000948.OF` | 支付宝 | 0.60%，规模 14.88 亿（tushare/akshare 2026-09-25 实测） | 备选：非 QDII、无额度限制；本卡不动作 |
| 华夏恒生ETF联接(QDII) A `000071.OF` | 支付宝 | 0.75%，规模 36.57 亿（2026-09-25 实测） | 落选：QDII 限购且更贵 |
| 汇添富恒生指数(QDII-LOF) C `010789.OF` | 支付宝 | 1.10%，规模 3.48 亿（2026-09-25 实测） | 落选：贵且小 |

直持港股 ETF 无红利税（港股通渠道 20%），这是 02800 相对支付宝联接基金的结构性优势；代价是币种为港元、不在定投体系内。

## 6. 点位与仓位

- 推导：框架 A9 回撤分位阶梯。36 月高点 27,387.11，状态分位点 P10 0.5579 / P25 0.6888 / P75 0.9769（n=730，自 1964-07）。
- 点位（`level_at_drawdown_state`）：`add_below` **15,279.27**（目标 100%）、`buy_below` **18,864.24**（目标 50%）、`reduce_above` **26,754.47**（目标 30%）。当前 24,750.78，中间区，距减仓档 +8.1%、距买入档 −23.8%。
- 本卡 `status=active`、工具 `hold`：不一次性买入；减仓侧生效——升破 26,754.47 减到上限的 30%（3 万）；跌破 18,864.24 不自动买而是复评（届时论点若成立，再把 primary 改为 buy）。
- 仓位：`bet_group = hk-hsi-core`，上限 100,000 = 66,000 ÷ 66%；现持仓约 54,606（55%）。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 触发条件 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 指数相对 200 日均线（自动） | 执行侧日频计算 | 快照 §6：−3.32% | < 0 持续 | 告警 | 日 |
| 指数点位跌破买入锚点（自动） | 执行侧日频计算 | 24,750.78 | < 18,864.24 | 复评（不自动买） | 日 |
| 美元利率与 HIBOR（人工） | 美联储决议、金管局 | 2026-09 联邦基金利率 3.75%–4.00% | 再加息一次以上，或 1 个月 HIBOR 站上 5% | 复评 | 月 |
| 南向资金（人工） | 港交所港股通统计 | 9 月中旬连续 8 日净流入 | 月度净买入连续两个月为负 | 复评 | 月 |
| 恒指官方估值（人工） | 恒生指数公司月报 / 乐咕乐股 | PE 约 14.16（2026-08-31） | 站上 18 倍 | 复评（与减仓锚点互证） | 月 |

## 8. 退出与复评

- 失效条件（工具层）：盈富基金管理人/费率变更导致跟踪偏离明显恶化，或盈立证券无法继续交易港股 ETF → `swap_tool`（换到 000948.OF）。资产逻辑层核心卡不设固定跌幅止损（A9）。
- 最迟复评日 2026-12-25。
- 记分：基准 `H11025.CSI`，预登记 2026-09-25，置信度 50%，写卡时点位 24,750.78。

```json
{
  "card_schema_version": 1,
  "card_id": "hk-hsi-core",
  "as_of_date": "2026-09-25",
  "supersedes": null,
  "framework": {
    "path": "framework/etf_framework.md",
    "version": "v0.1"
  },
  "snapshot_ref": "research/etf/snapshots/etf-2026-09-18-data-snapshot.txt",
  "task": "core",
  "status": "active",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "HSI",
    "index_name": "恒生指数",
    "asset_type": "broad_equity",
    "currency": "HKD",
    "counts_toward_sector_cap": false,
    "china_equity": true,
    "view_mismatch_note": "恒指是港股大盘宽基，但金融（汇丰、友邦、建行等）与互联网平台合计占大头，行业均衡度不如 A500；对用户而言它承担的是“港股整体 beta”而非任何行业观点",
    "structure": {
      "weights_as_of": null,
      "constituent_count": {
        "value": null,
        "source": null
      },
      "max_constituent_weight_pct": {
        "value": null,
        "source": null
      },
      "top10_weight_pct": {
        "value": null,
        "source": null
      },
      "research_coverage_pct": {
        "value": null,
        "source": null
      },
      "top_constituents": []
    }
  },
  "thesis": {
    "statement": "港股宽基的长期回报靠估值均值回归加股息，不靠盈利高增；恒指现在处于阶梯中间区、估值中位（官方 PE 约 14 倍），本席位持有不追加，把买入留给阶梯给出的深跌档",
    "evidence": [
      "资金面：南向资金 2026 年 9 月 16 日已连续 8 个交易日逆势净流入，9 月 14 日单日净流入 44.71 亿港元；港股是内地资金唯一能大规模配置的离岸中国资产",
      "供给与生态：2026 年前 7 个月港股 IPO 融资 3,259.93 亿港元、101 家上市，时隔五年重回 3,000 亿港元以上；A+H 扩容使恒指成分的科技与新经济占比继续上升",
      "规则验证：回撤分位阶梯在恒指上四折全部通过——回撤 −18.3% 对满仓 −62.7%（2005–2010）、年化平均高 5.1 个点、对同均仓位的恒定比例仍有 3.2 个点的择时技能（验证报告 @26e3adc）"
    ],
    "counter_evidence": [
      "利率面：美联储 2026 年 9 月把联邦基金利率上调至 3.75%–4.00%，港元联系汇率下 HIBOR 跟随，港股估值分母端承压；恒指与美元流动性的相关在加息周期里更强",
      "阶梯的代价：验证报告里恒指 2011–2016 那一折阶梯全程空仓（年化 +3.7% 全是现金收益），2017–2022 平均仓位只有 6.3%——本规则在横盘市里长期空仓，并不是“持有港股”的替代"
    ],
    "horizon_months": 120
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
          "value": -15,
          "source": "ai_estimate",
          "note": "估值分母端（美元利率 4% 以上维持）+ 盈利下修，回到 2022 年低点区域"
        }
      },
      "base": {
        "inputs": null,
        "valuation_change_pct": {
          "value": 0,
          "source": "framework:A5"
        },
        "annual_return_pct": {
          "value": 6,
          "source": "ai_estimate",
          "note": "盈利低个位数增长 + 3.5% 左右股息，估值零变化"
        }
      },
      "bull": {
        "inputs": null,
        "valuation_change_pct": {
          "value": null,
          "source": null
        },
        "annual_return_pct": {
          "value": 18,
          "source": "ai_estimate",
          "note": "南向资金持续流入 + 降息周期开启，估值向 PE 18 倍修复"
        }
      }
    },
    "valuation_state": {
      "index_code": null,
      "metric": null,
      "value": {
        "value": null,
        "source": null,
        "note": "港股指数无估值源（快照 §0 缺口）；恒生官方月报 PE 约 14.16（乐咕乐股 2026-08-31）可手工录，未进卡"
      },
      "percentile_expanding": {
        "value": null,
        "source": null
      },
      "percentile_10y": {
        "value": null,
        "source": null
      },
      "sample_n": {
        "value": null,
        "source": null
      },
      "as_of": null
    }
  },
  "instruments": {
    "merge_note": "盈富基金是本席位唯一持仓；支付宝端的恒指联接基金只作备选，不与 02800 并持（同一席位一个工具）",
    "list": [
      {
        "code": "02800.HK",
        "name": "盈富基金",
        "instrument_type": "exchange_etf",
        "share_class": null,
        "currency": "HKD",
        "platform_account": "盈立证券",
        "role": "primary",
        "action": "hold",
        "reason": "2,500 股，按快照 §5 收盘 25.38 港元 × §7 中间价 0.86062 折约 54,606 元；港交所直持无红利税、管理费极低（公开资料约 0.019%，未核）；持有，不追加"
      },
      {
        "code": "000948.OF",
        "name": "华夏沪港通恒生ETF联接-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "backup",
        "action": "none",
        "reason": "支付宝可买、非 QDII 无额度限制，年费 0.60%（tushare/akshare 2026-09-25 实测），规模 14.88 亿；若日后要在支付宝端加恒指仓位用它，不在本卡内动作"
      },
      {
        "code": "000071.OF",
        "name": "华夏恒生ETF联接(QDII)-A-CNY",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "未持有；QDII 有限购，年费 0.75%（2026-09-25 实测）高于沪港通版本"
      },
      {
        "code": "010789.OF",
        "name": "汇添富恒生指数(QDII-LOF)-C",
        "instrument_type": "otc_fund",
        "share_class": "C",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "未持有；年费 1.10%、规模 3.48 亿（2026-09-25 实测），贵且小"
      }
    ]
  },
  "trade_rules": {
    "min_holding_days": 7,
    "purchase_limit_note": null
  },
  "decision": {
    "rule_refs": [
      "A8",
      "A9",
      "A10",
      "A13"
    ],
    "anchors": {
      "basis": "index_level",
      "index_code": "HSI",
      "snapshot_ref": null,
      "add_below": {
        "level": {
          "value": 15279.27,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 100,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 27387.11,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.5579,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P10"
          }
        },
        "rationale": "回撤状态回到自身历史 P10（1964 年以来 730 个月样本）：相当于 2008、2022 那种级别的深跌"
      },
      "buy_below": {
        "level": {
          "value": 18864.24,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 50,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 27387.11,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.6888,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P25"
          }
        },
        "rationale": "回撤状态回到自身历史 P25；当前 24,750.78 在其上方约 31%。跌破时不自动买（本卡工具为 hold），转复评"
      },
      "reduce_above": {
        "level": {
          "value": 26754.47,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 30,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 27387.11,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.9769,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P75"
          }
        },
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 2%）：升破即把本席位减到上限的 30%（3 万）"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "hk-hsi-core",
    "stress_drawdown_pct": {
      "value": -66,
      "source": "user:2026-09-19",
      "note": "核心席位上限表"
    },
    "loss_budget_cny": {
      "value": 66000,
      "source": "user:2026-09-19",
      "note": "核心席位上限表：上限 × 压力跌幅反推"
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
      "current_text": "快照 §6：-3.32%，below",
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
        "value": 18864.24,
        "source": "calc:level_at_drawdown_state"
      },
      "condition_text": "收盘跌破 buy_below（回撤状态 P25）",
      "data_source": "执行侧日频计算",
      "current_text": "快照 §6：24,750.78",
      "frequency": "daily",
      "action": "review",
      "action_note": "本卡工具为 hold，不自动买；跌破即复评是否改 primary 为 buy"
    },
    {
      "name": "美元利率与 HIBOR",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "美联储再加息一次以上，或 1 个月 HIBOR 站上 5%",
      "data_source": "美联储决议、香港金管局",
      "current_text": "2026-09 联邦基金利率 3.75%–4.00%（本轮首次加息）",
      "frequency": "monthly",
      "action": "review",
      "action_note": "港元联系汇率下估值分母端直接受压"
    },
    {
      "name": "南向资金",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "月度净买入连续两个月为负",
      "data_source": "港交所港股通统计",
      "current_text": "9 月中旬连续 8 日净流入；9/14 单日 +44.71 亿港元",
      "frequency": "monthly",
      "action": "review",
      "action_note": ""
    },
    {
      "name": "恒指官方估值",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "恒生官方 PE 站上 18 倍（历史高位区）",
      "data_source": "恒生指数公司月报 / 乐咕乐股",
      "current_text": "PE 约 14.16（乐咕乐股 2026-08-31）",
      "frequency": "monthly",
      "action": "review",
      "action_note": "高于 18 倍时与减仓锚点互证"
    }
  ],
  "exit": {
    "invalidation": [
      {
        "name": "工具变差",
        "kind": "manual",
        "metric": null,
        "operator": null,
        "threshold": {
          "value": null,
          "source": null
        },
        "condition_text": "盈富基金管理人/费率变更导致跟踪偏离明显恶化，或盈立证券无法继续交易港股 ETF",
        "data_source": "基金公告、券商通知",
        "current_text": "未发生",
        "frequency": "event",
        "action": "swap_tool",
        "action_note": "换到支付宝端的沪港通恒生联接"
      }
    ],
    "latest_review_date": "2026-12-25"
  },
  "scorecard": {
    "benchmark": {
      "code": "H11025.CSI",
      "name": "同一笔钱放在货币基金"
    },
    "preregistered_at": "2026-09-25",
    "confidence_pct": 50,
    "entry_ref_index_level": {
      "value": 24750.78,
      "source": "snapshot§6"
    }
  }
}
```
