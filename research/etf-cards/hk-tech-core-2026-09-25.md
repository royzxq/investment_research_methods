# 决策卡：恒生科技（核心席位）· 2026-09-25

> 席位：恒生科技（框架 A1 第 5 席，核心；用户裁定不占行业额度）。`card_id` = `hk-tech-core`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓：天弘恒生科技ETF联接(QDII)C 012349.OF 53,211 元（用户 2026-09-18 提供），定投中。
> 快照 §0 与本席位相关的缺口：港股指数无估值源；恒生科技成分与权重无现成源 `[需人工补充]`。

## 1. 投资任务

- 任务：`core`——中国互联网平台与港股硬科技的长期持有仓，记账币种人民币；计划持有 5 年，最迟 2026-12-25 复评。
- 允许亏损：核心席位上限表（用户 2026-09-19）：上限 5 万、压力跌幅 −75%（2021-02 → 2022-10 实测）、亏损预算 3.75 万。
- **现状：53,211 元，已超上限 3,211 元。** 按用户 2026-09-23 口径，上限不强制减存量——本卡的动作是 **停定投**、持有、等阶梯；减仓侧锚点生效。
- 不买它时钱放哪（记分基准）：`H11025.CSI`。

## 2. 核心判断

**主判断**：恒生科技是押中国互联网平台 + AI 应用与硬科技的高波动篮子，平台回购与 AI 业务给了盈利底，但估值随美元利率与监管起伏；本席位已超上限，停定投、持有等阶梯，不追加。

支撑证据：
1. 回购托底：年内 9 家成分股回购合计 417 亿港元，腾讯累计 244 亿港元、小米 110 亿港元（[新浪财经 2026-07-02](https://finance.sina.com.cn/wm/2026-07-02/doc-inifmvzs4005366.shtml)）。
2. AI 与云业务在报表里兑现：小米 2026 年二季度营收 1,089.22 亿元、AI 等创新业务收入 248.96 亿元同比 +17.08%；美团一季度收入 910 亿元 +5.6%，加大 AI Agent 投入（[中新网 2026-08-19](https://www.chinanews.com.cn/cj/2026/08-19/10680101.shtml)）。
3. 指数向 AI 纯度演进：6 月季检首次纳入智谱、MiniMax，8 月季检纳入天数智芯、剔除同程旅行，被动资金双向流量超 72 亿美元（[腾讯新闻 2026-09-04](https://news.qq.com/rain/a/20260904A05YJ100)、[EBC 2026 调整名单](https://www.ebc.com/zh/jinrong/295293.html)）。

反证：
1. 集中度与风险形状：30 只成分、单一 8% 上限下前十大仍占约 69.43%（2026-05-30，[jetsohk101](https://jetsohk101.com/hk-tech-stocks-tracker/)）；2021–2022 回撤约 −75%，全池最深。用户虽归为宽基，风险预算按行业级给。
2. 分母端与外部约束：美联储 2026-09 加息至 3.75%–4.00%；美国对华 AI 芯片与算力限制随时可扩大到中芯、寒武纪类成分——两条都不在公司基本面里，却决定估值。

## 3. 指数匹配

- 编制（恒生指数公司 factsheet）：30 只与科技主题高度相关的最大港股，自由流通市值加权、单一 8% 上限，季度检讨。快照对港股成分无源，结构读数 `[需人工补充]`。
- 观点与持仓错位：指数已把纯 AI 大模型公司纳入，但主体仍是腾讯、阿里、美团、小米、百度、比亚迪、京东、中芯、快手、理想——"AI 应用 + 电商 + 汽车"的混合，不是纯算力。
- 历史：2014-12-31 基日、2020-07 发布，2020 年前是回溯值；快照 §6b 回撤状态样本 142 个月。

## 4. 预期与估值

- 无指数口径估值源 `[需人工补充]`。方法 `scenario_only`（`ai_estimate`）：熊 −30%（美元利率维持高位 + 监管或对华限制升级，回到 2024 年初区域）；基准 +8%（平台盈利中个位数增长 + 回购，估值零变化）；牛 +30%（AI 应用商业化超预期 + 降息）。
- 位置：快照 §6b 36 月高点 6,465.66，当前 4,405.50，状态 0.6814、分位 33.1，中间区，距买入档 −8.7%；快照 §6 显示指数在 200 日线下方 12.25%。

## 5. 工具比选

| 工具 | 年费 | TD 年化 / TE | 结论 |
|---|---|---|---|
| 天弘恒生科技ETF联接(QDII) C `012349.OF`（持 53,211） | 0.80%（含销售服务费 0.20%） | −0.61pp / 1.82%（快照 §5，港元折人民币，指数不含分红） | **首选（现有持仓）**；停定投，存量不动 |
| 天弘恒生科技ETF联接(QDII) A `012348.OF` | 0.60% | — | 落选：本席位已超上限不新增；日后腾出额度再加走 A 类 |

## 6. 点位与仓位

- 推导：框架 A9 回撤分位阶梯。36 月高点 6,465.66，状态分位点 P10 0.4417 / P25 0.6219 / P75 0.9272（n=142，自 2014-12）。
- 点位：`add_below` **2,855.88**（100%）、`buy_below` **4,020.99**（50%）、`reduce_above` **5,994.96**（30%）。当前 4,405.50，中间区。
- `status=active`、primary `stop_dca`：不买；升破 5,994.96 减到上限 30%（1.5 万）；跌破 4,020.99 不自动买（已超上限），转复评。
- 仓位：`bet_group = hk-tech-core`，上限 50,000 = 37,500 ÷ 75%；现持仓 53,211（106%）。
- 规则验证：恒生科技历史自 2014-12，回撤分位阶梯对它"数据不足"（只有 F4 一折），点位沿用主指数恒指的 validated 结论；恒指在横盘折里长期空仓的代价同样适用于此。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 触发条件 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 指数相对 200 日均线（自动） | 执行侧日频计算 | 快照 §6：−12.25% | < 0 持续 | 告警 | 日 |
| 指数点位跌破买入锚点（自动） | 执行侧日频计算 | 4,405.50 | < 4,020.99 | 复评（不自动买） | 日 |
| 指数集中度与季检（人工） | 恒生指数公司季检、factsheet | 前十大约 69.43%（2026-05-30） | 前十大升破 75%，或纯 AI 公司权重合计 >15% | 复评 | 季 |
| 平台回购与中报（人工） | 公司公告、中报 | 回购合计 417 亿港元；小米 Q2 经调整净利 62.19 亿元 | 任两家回购同比腰斩，或经调整净利同比转负 | 复评 | 季 |
| 美国对华科技限制（人工） | BIS 公告、公司公告 | 未发生新一轮扩大 | 限制扩大到中芯、寒武纪、天数智芯等成分且业务受实质影响 | 复评 | 事件 |

## 8. 退出与复评

- 失效条件：① 美国新一轮限制覆盖前十大权重中至少 5 家且收入受实质影响 → `reduce`（减到上限 30%）；② 腾讯、阿里、美团三家连续两个季度经调整净利润同比下滑 → `reduce`。
- 最迟复评日 2026-12-25。
- 记分：基准 `H11025.CSI`，预登记 2026-09-25，置信度 45%，写卡时点位 4,405.50。

```json
{
  "card_schema_version": 1,
  "card_id": "hk-tech-core",
  "as_of_date": "2026-09-25",
  "supersedes": null,
  "framework": {
    "path": "framework/etf_framework.md",
    "version": "v0.1"
  },
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "core",
  "status": "active",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "HKTECH",
    "index_name": "恒生科技",
    "asset_type": "growth_theme",
    "currency": "HKD",
    "counts_toward_sector_cap": false,
    "china_equity": true,
    "view_mismatch_note": "用户裁定恒生科技为核心宽基、不占行业额度，但它只有 30 只成分、前十大约 69%、压力跌幅 −75%，风险形状是行业而非宽基；本卡按核心席位管理，但仓位上限（5 万）已按行业级风险给足",
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
    "statement": "恒生科技是押中国互联网平台 + AI 应用与硬科技的高波动篮子：平台回购与 AI 业务给了盈利底，但估值随美元利率与监管起伏；本席位已超上限，停定投、持有等阶梯，不追加",
    "evidence": [
      "回购托底：年内 9 家恒生科技成分股回购合计 417 亿港元，腾讯累计回购 244 亿港元、小米 110 亿港元（新浪财经 2026-07-02）",
      "AI 与云业务在报表里兑现：小米 2026 年二季度营收 1,089.22 亿元、AI 等创新业务收入 248.96 亿元同比 +17.08%；美团一季度收入 910 亿元 +5.6% 并加大 AI Agent 投入（中新网 2026-08-19）",
      "指数在向 AI 纯度演进：2026 年 6 月季检首次纳入智谱、MiniMax 两家大模型公司，8 月季检纳入天数智芯，被动资金双向流量超 72 亿美元（腾讯新闻 2026-09-04）"
    ],
    "counter_evidence": [
      "集中度与风险形状：30 只成分、单一 8% 上限下前十大仍占约 69.43%（2026-05-30）；2021-02 至 2022-10 实测回撤约 −75%，是全池最深，用户虽归为宽基，风险预算按行业级给",
      "分母端与外部约束：美联储 2026-09 加息至 3.75%–4.00%，港元利率跟随；美国对华 AI 芯片与算力限制随时可扩大到中芯、寒武纪类成分——两条都不在公司基本面里，却决定估值"
    ],
    "horizon_months": 60
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
          "note": "美元利率维持 4% 以上 + 平台监管或对华科技限制升级，回到 2024 年初区域"
        }
      },
      "base": {
        "inputs": null,
        "valuation_change_pct": {
          "value": 0,
          "source": "framework:A5"
        },
        "annual_return_pct": {
          "value": 8,
          "source": "ai_estimate",
          "note": "平台盈利中个位数增长 + 回购，估值零变化"
        }
      },
      "bull": {
        "inputs": null,
        "valuation_change_pct": {
          "value": null,
          "source": null
        },
        "annual_return_pct": {
          "value": 30,
          "source": "ai_estimate",
          "note": "AI 应用商业化超预期 + 降息，估值修复"
        }
      }
    },
    "valuation_state": {
      "index_code": null,
      "metric": null,
      "value": {
        "value": null,
        "source": null,
        "note": "港股指数无估值源（快照 §0 缺口）；恒生官方月报的恒生科技 PE 可手工录，未进卡"
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
    "merge_note": "本席位一只工具；C 类存量不换，定投停止",
    "list": [
      {
        "code": "012349.OF",
        "name": "天弘恒生科技ETF联接(QDII)-C",
        "instrument_type": "otc_fund",
        "share_class": "C",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "primary",
        "action": "stop_dca",
        "reason": "持 53,211 元，已超核心席位上限 50,000（超 3,211）→ 停定投、存量不强制减（用户 2026-09-23 口径）；年费 0.80%，TD 年化 -0.61pp、TE 1.82%（快照 §5）"
      },
      {
        "code": "012348.OF",
        "name": "天弘恒生科技ETF联接(QDII)-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "未持有；同基金 A 类年费 0.60%。本席位已超上限不新增，若日后腾出额度再加钱走 A 类"
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
      "index_code": "HKTECH",
      "snapshot_ref": null,
      "add_below": {
        "level": {
          "value": 2855.88,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 100,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 6465.66,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.4417,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P10"
          }
        },
        "rationale": "回撤状态回到自身历史 P10：相当于 2022 年 10 月那轮 −75% 深跌的底部区域"
      },
      "buy_below": {
        "level": {
          "value": 4020.99,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 50,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 6465.66,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.6219,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P25"
          }
        },
        "rationale": "回撤状态回到自身历史 P25；当前 4,405.50 在其上方约 9.6%。持仓已超上限，跌破时不自动买，转复评"
      },
      "reduce_above": {
        "level": {
          "value": 5994.96,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 30,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 6465.66,
            "source": "snapshot§6",
            "note": "近 36 个月末收盘最高值"
          },
          "state": {
            "value": 0.9272,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P75"
          }
        },
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 7%）：升破即把本席位减到上限的 30%（1.5 万）"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "hk-tech-core",
    "stress_drawdown_pct": {
      "value": -75,
      "source": "user:2026-09-19",
      "note": "核心席位上限表"
    },
    "loss_budget_cny": {
      "value": 37500,
      "source": "user:2026-09-19",
      "note": "核心席位上限表：上限 × 压力跌幅反推"
    },
    "standalone_cap_cny": {
      "value": 50000,
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
      "current_text": "快照 §6：-12.25%，below",
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
        "value": 4020.99,
        "source": "calc:level_at_drawdown_state"
      },
      "condition_text": "收盘跌破 buy_below（回撤状态 P25）",
      "data_source": "执行侧日频计算",
      "current_text": "快照 §6：4,405.50",
      "frequency": "daily",
      "action": "review",
      "action_note": "持仓已超上限，不自动买；复评论点与额度后再定"
    },
    {
      "name": "指数集中度与季检",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "前十大权重合计升破 75%，或季检把纯 AI 公司权重合计推到 15% 以上",
      "data_source": "恒生指数公司季检公告、指数 factsheet",
      "current_text": "前十大约 69.43%（2026-05-30）；6 月纳入智谱、MiniMax，8 月纳入天数智芯",
      "frequency": "quarterly",
      "action": "review",
      "action_note": ""
    },
    {
      "name": "平台回购与中报",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "腾讯、阿里、美团、小米任两家回购规模同比腰斩，或中报经调整净利润同比转负",
      "data_source": "公司公告、中报",
      "current_text": "年内成分股回购合计 417 亿港元；小米 Q2 经调整净利 62.19 亿元",
      "frequency": "quarterly",
      "action": "review",
      "action_note": ""
    },
    {
      "name": "美国对华科技限制",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "实体清单或 AI 芯片/算力出口限制扩大到中芯国际、寒武纪、天数智芯等成分且业务受实质影响",
      "data_source": "BIS 公告、公司公告",
      "current_text": "未发生新一轮扩大",
      "frequency": "event",
      "action": "review",
      "action_note": ""
    }
  ],
  "exit": {
    "invalidation": [
      {
        "name": "对华科技限制扩大到前十大权重过半",
        "kind": "manual",
        "metric": null,
        "operator": null,
        "threshold": {
          "value": null,
          "source": null
        },
        "condition_text": "美国新一轮限制覆盖前十大权重中至少 5 家且其收入受实质影响",
        "data_source": "BIS 公告、公司公告",
        "current_text": "未发生",
        "frequency": "event",
        "action": "reduce",
        "action_note": "减到上限 30%"
      },
      {
        "name": "平台盈利证伪",
        "kind": "manual",
        "metric": null,
        "operator": null,
        "threshold": {
          "value": null,
          "source": null
        },
        "condition_text": "腾讯、阿里、美团三家连续两个季度经调整净利润同比下滑",
        "data_source": "季报",
        "current_text": "未发生",
        "frequency": "event",
        "action": "reduce",
        "action_note": ""
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
    "confidence_pct": 45,
    "entry_ref_index_level": {
      "value": 4405.5,
      "source": "snapshot§6"
    }
  }
}
```
