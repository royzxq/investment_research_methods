# 决策卡：恒生港股通红利低波动（核心席位）· 2026-09-25

> 席位：港股红利低波（框架 A1 第 6 席，核心）。`card_id` = `hk-dividend-lowvol-core`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 持仓：易方达恒生港股通红利低波动ETF联接 A 021457.OF 39,873 元（用户 2026-09-18 提供），定投中。
> 快照 §0 与本席位相关的缺口：**指数无行情源**（登记清单 `source: null`），估值、成分、TD/TE、回撤位置全部给不出 `[需人工补充]`；候选代理中证港股通高股息 `930914.CSI` 能否代理待与基金净值核相关。

## 1. 投资任务

- 任务：`core`——组合里最像类债的权益仓：赚港股高息股的股息（Carry），不押估值修复；记账币种人民币；计划持有 10 年，最迟 2026-12-25 复评。
- 允许亏损：核心席位上限表（用户 2026-09-19）：上限 8 万、压力跌幅 −50%（**估计值**，该指数无历史序列，取低波类同类资产的保守估计）、亏损预算 4 万。
- **现状：39,873 元，占上限 50%。** 持有，定投继续。
- 不买它时钱放哪（记分基准）：`H11025.CSI`。

## 2. 核心判断

**主判断**：港股高息低波是本组合里最像类债的权益仓，约 6% 的税前股息率加低波动筛选，靠 Carry 而非估值修复；本席位持有、定投继续，但指数无行情源，暂不设点位。

支撑证据：
1. 股息率：恒生港股通高股息低波动指数股息率 5.96%（2026-01-21，[知乎 · 恒生系指数股息率盘点](https://zhuanlan.zhihu.com/p/1997769669529056800)、[乐咕乐股 HSHYLV](https://legulegu.com/stockdata/hsi-theme-index?indexCode=HSHYLV)），扣港股通 20% 红利税后约 4.8%，高于快照 §7 的 10 年国债 1.6820% 逾 3 个百分点。
2. 编制规则自带纪律：先取净股息率最高的 75 只，再按过去 12 个月年化波动率筛选；股息率超 7% 要复核并剔除一次性分红（[恒生指数公司编算细则](https://www.hsi.com.hk/static/uploads/contents/zh_cn/dl_centre/methodologies/IM_hshylvc.pdf)）。高息陷阱被规则挡在外面。
3. 工具最便宜：021457.OF 年费 0.20%，规模 29.90 亿（快照 §5）。

反证：
1. 无行情源：tushare/akshare 都不覆盖该指数，跟踪偏离、回撤位置、点位都给不出——本卡只能靠基金净值与人工监控管理，是全池唯一"看不见指数"的持仓。
2. 利率与信用的两头：美联储 2026-09 加息后美元资产收益率抬升，港股高息股相对吸引力下降；成分以内地银行为主，净息差与不良率是隐含的信用风险，低波动不等于低风险（框架 A5）。

## 3. 指数匹配

- 编制：港股通范围内按净股息率取前 75 只，再按 12 个月波动率筛选，股息率加权（细则见上）；成分以内地银行、能源、电信、公用事业为主。快照无成分数据，结构读数 `[需人工补充]`。
- 观点与持仓错位：低。要提醒的是它与 A 股红利低波席位（`H30269.CSI`，同样银行为主）的成分公司高度重叠——两个红利席位加起来是同一批银行的 A、H 两端。
- 代理：中证港股通高股息 `930914.CSI` 在快照 §6b 的位置是状态 0.9440、分位 72.0（接近减仓区），仅供参考，本卡不据此写锚点。

## 4. 预期与估值

- 无指数口径估值源 `[需人工补充]`。方法 `scenario_only`（`ai_estimate`）：熊 −20%（内地银行资产质量恶化 + 红利税不变）；基准 +5%（税后股息约 4.8% + 盈利持平，估值零变化）；牛 +12%（港股通红利税减免落地或降息周期）。
- 基准情景的回报几乎全部来自股息——这是 Carry 资产的形状。

## 5. 工具比选

| 工具 | 年费 | TD / TE | 结论 |
|---|---|---|---|
| 易方达恒生港股通红利低波动ETF联接 A `021457.OF`（持 39,873） | 0.20% | 不可算（指数无行情源） | **首选（现有持仓）**；持有，定投继续 |
| 易方达恒生港股通红利低波动ETF联接 C `021458.OF` | 0.50% | — | 落选：长期持有比 A 类贵 0.30 个百分点 |

港股通渠道红利税 20%（H 股；红筹 28%），已含在基金净值里；盈立证券直持同类港股 ETF 可免红利税，但用户该席位的持仓在支付宝，本卡不建议为此换渠道。

## 6. 点位与仓位

- **本卡不设三锚点**（按 schema 契约 `status=no_buy` + `no_buy_reason=data`）：指数无行情源，不产生点位信号；补上行情源后再评估。执行侧日报按 `no_anchor_reason` 原文输出。
- 仓位：`bet_group = hk-dividend-lowvol-core`，上限 80,000 = 40,000 ÷ 50%；现持仓 39,873（50%）。定投继续，触及上限时由执行侧告警停投。
- 规则验证对本指数不适用（无序列）；若将来用 `930914.CSI` 代理，须先与基金净值核相关，再进登记清单。

## 7. 核心监控

| 变量 | 来源 | 当前值 | 触发条件 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 行情源可得性（人工） | 登记清单、快照 §0 | 无源 | tushare/akshare 或恒生官方能取到 HSHYLV 日线 | 复评（重写本卡：补点位、改 status） | 月 |
| 港股通红利税（人工） | 财政部/税务总局 | H 股 20%（红筹 28%） | 税率调整 | 复评 | 事件 |
| 指数股息率（人工） | 恒生 factsheet / 乐咕乐股 | 5.96%（2026-01-21） | 跌破 4%（税前） | 复评 | 月 |
| 基金规模（人工） | 基金定期报告 | 29.90 亿（2026-06-30） | 跌破 5 亿 | 复评（清盘风险） | 季 |

## 8. 退出与复评

- 失效条件（工具层）：基金规模跌破 2 亿或跟踪指数变更 → `swap_tool`。资产逻辑层不设固定跌幅止损（A9）。
- 最迟复评日 2026-12-25。
- 记分：基准 `H11025.CSI`，预登记 2026-09-25，置信度 50%；写卡时点位无源（`entry_ref_index_level` 为空），记分改用基金复权净值 1.2551（快照 §5）作参照。

```json
{
  "card_schema_version": 1,
  "card_id": "hk-dividend-lowvol-core",
  "as_of_date": "2026-09-25",
  "supersedes": null,
  "framework": {
    "path": "framework/etf_framework.md",
    "version": "v0.1"
  },
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "core",
  "status": "no_buy",
  "no_buy_reason": "data",
  "close_reason": null,
  "exposure": {
    "index_code": "HSHYLV",
    "index_name": "恒生港股通红利低波动",
    "asset_type": "dividend_value",
    "currency": "HKD",
    "counts_toward_sector_cap": false,
    "china_equity": true,
    "view_mismatch_note": "指数按净股息率选 75 只、再按 12 个月波动率筛选，成分以内地银行、能源、电信等港股通高息股为主；表达的是“港股高息 + 低波”，不是任何行业观点",
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
    "statement": "港股高息低波是本组合里最像类债的权益仓：约 6% 的税前股息率（港股通渠道扣 20% 红利税后约 4.8%）加低波动筛选，靠 Carry 而非估值修复；本席位持有、定投继续，但指数无行情源，暂不设点位",
    "evidence": [
      "股息率：恒生港股通高股息低波动指数股息率 5.96%（2026-01-21，恒生系高息指数中最高的一档），扣除港股通 20% 红利税后仍约 4.8%，高于 10 年国债 1.68% 逾 3 个百分点",
      "编制规则自带纪律：先取净股息率最高的 75 只，再按过去 12 个月年化波动率筛选，单次股息率超 7% 要复核并剔除一次性分红——高息陷阱被规则挡在外面（恒生指数公司编算细则）",
      "工具是同席位里最便宜的：021457.OF 年费 0.20%（A 类，无销售服务费），规模 29.90 亿（快照 §5）"
    ],
    "counter_evidence": [
      "无行情源：tushare/akshare 都不覆盖该指数，快照 §5/§6 对它全部缺口，跟踪偏离、回撤位置、点位都给不出——本卡只能靠基金净值与人工监控管理",
      "利率与汇率的两头：美联储 2026-09 加息后美元资产收益率抬升，港股高息股相对吸引力下降；成分以内地银行为主，净息差与不良率是隐含的信用风险，低波动不等于低风险（框架 A5）"
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
          "value": -20,
          "source": "ai_estimate",
          "note": "内地银行资产质量恶化 + 港股通红利税不变，价格跌、股息降"
        }
      },
      "base": {
        "inputs": null,
        "valuation_change_pct": {
          "value": 0,
          "source": "framework:A5"
        },
        "annual_return_pct": {
          "value": 5,
          "source": "ai_estimate",
          "note": "股息约 4.8%（税后）+ 盈利持平，估值零变化"
        }
      },
      "bull": {
        "inputs": null,
        "valuation_change_pct": {
          "value": null,
          "source": null
        },
        "annual_return_pct": {
          "value": 12,
          "source": "ai_estimate",
          "note": "港股通红利税减免落地或降息周期，估值修复"
        }
      }
    },
    "valuation_state": {
      "index_code": null,
      "metric": null,
      "value": {
        "value": null,
        "source": null,
        "note": "指数无估值源；恒生官方指数股息率 5.96%（乐咕乐股 2026-01-21）可手工录，未进卡"
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
    "merge_note": "本席位一只工具",
    "list": [
      {
        "code": "021457.OF",
        "name": "易方达恒生港股通红利低波动ETF联接-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "primary",
        "action": "hold",
        "reason": "持 39,873 元，占上限 50%；年费 0.20%，规模 29.90 亿；TD/TE 因指数无行情源不可算（快照 §5）；持有、定投继续"
      },
      {
        "code": "021458.OF",
        "name": "易方达恒生港股通红利低波动ETF联接-C",
        "instrument_type": "otc_fund",
        "share_class": "C",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "未持有；同基金 C 类年费 0.50%，长期持有比 A 类贵 0.30 个百分点"
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
      "index_code": "HSHYLV",
      "snapshot_ref": null,
      "add_below": {
        "level": {
          "value": null,
          "source": null
        },
        "target_ratio_pct": {
          "value": null,
          "source": null
        },
        "inputs": null,
        "rationale": null
      },
      "buy_below": {
        "level": {
          "value": null,
          "source": null
        },
        "target_ratio_pct": {
          "value": null,
          "source": null
        },
        "inputs": null,
        "rationale": null
      },
      "reduce_above": {
        "level": {
          "value": null,
          "source": null
        },
        "target_ratio_pct": {
          "value": null,
          "source": null
        },
        "inputs": null,
        "rationale": null
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": "指数无行情源（tushare/akshare 均不覆盖），不产生点位信号；补上行情源后再评估",
      "valid_until": null
    }
  },
  "sizing": {
    "bet_group": "hk-dividend-lowvol-core",
    "stress_drawdown_pct": {
      "value": -50,
      "source": "user:2026-09-19",
      "note": "核心席位上限表"
    },
    "loss_budget_cny": {
      "value": 40000,
      "source": "user:2026-09-19",
      "note": "核心席位上限表：上限 × 压力跌幅反推"
    },
    "standalone_cap_cny": {
      "value": 80000,
      "source": "calc:loss_budget_cap"
    }
  },
  "monitor_variables": [
    {
      "name": "行情源可得性",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "tushare/akshare 或恒生官方数据服务能取到 HSHYLV 日线",
      "data_source": "登记清单 framework/etf_index_registry.json、快照 §0",
      "current_text": "无源（登记清单 source=null）",
      "frequency": "monthly",
      "action": "review",
      "action_note": "命中即重写本卡：补 §6b 位置与三锚点、改 status"
    },
    {
      "name": "港股通红利税",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "港股通红利税由 20% 调整（减免或加征）",
      "data_source": "财政部/税务总局公告",
      "current_text": "H 股 20%（红筹 28%）",
      "frequency": "event",
      "action": "review",
      "action_note": "税率直接改变税后 Carry"
    },
    {
      "name": "指数股息率",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "恒生官方指数股息率跌破 4%（税前）",
      "data_source": "恒生指数公司 factsheet / 乐咕乐股",
      "current_text": "5.96%（2026-01-21）",
      "frequency": "monthly",
      "action": "review",
      "action_note": "跌破意味着价格已把 Carry 买薄"
    },
    {
      "name": "基金规模",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "021457.OF 规模跌破 5 亿",
      "data_source": "基金定期报告",
      "current_text": "29.90 亿（2026-06-30）",
      "frequency": "quarterly",
      "action": "review",
      "action_note": "清盘风险"
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
        "condition_text": "基金规模跌破 2 亿或跟踪指数变更",
        "data_source": "基金公告",
        "current_text": "未发生",
        "frequency": "event",
        "action": "swap_tool",
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
    "confidence_pct": 50,
    "entry_ref_index_level": {
      "value": null,
      "source": null
    }
  }
}
```
