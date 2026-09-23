# 决策卡：消费（中证主要消费）· 2026-09-24

> 席位：消费（框架 A1 第 13 席，新席位，**无持仓**）。`card_id` = `cn-consumer-tactical`，首版。数据：`research/etf-2026-09-18-data-snapshot.txt`（AS_OF 2026-09-18）。
> 快照 §0 缺口清单与本席位无直接相关项。工具费率与规模来自 tushare `fund_basic` / `fund_nav` 与 akshare `fund_fee_em` 2026-09-23 实测，不在快照内，只写正文。

## 1. 投资任务

- 任务：`tactical`——押"必选消费（白酒 + 生猪 + 乳品 + 食品）经三年去估值后，估值与股息率到了历史极端，白酒去库存与猪周期都在底部区域"这一有期限的均值回归判断。记账币种人民币；计划持有 24 个月，最迟 2026-11-20 复评。
- 允许亏损：行业单笔亏损预算 7 万（用户 2026-09-23 拍板），按 −70% 压力跌幅反推单笔上限 10 万（`loss_budget_cap`）。
- 现状：无持仓。本卡 `status=watch`——买入侧只告警不出指令，由用户决定是否启用；启用前先看第 6 节的位置。
- 不买它时钱放哪（记分基准）：中证货币基金指数 `H11025.CSI`。

## 2. 核心判断

**主判断**：主要消费指数的 PB 处于 2010 年以来第 1.1 分位、股息率 4.17% 处于第 98.9 分位，白酒渠道库存已到低位、生猪产能去化进入第四个季度——这是一笔"买极端估值、等周期与情绪均值回归"的押注，不是买景气；当前点位已落在阶梯的买入区。

支撑证据：
1. 白酒渠道出清接近尾段：广发对五省经销商的调研显示渠道库存处于低位、头部品牌库存均在下降；飞天茅台批价回升至 1750 元左右并企稳；酒协与毕马威中期报告显示 56.6% 经销商反映价格倒挂同比加剧、61.9% 终端门店规模收缩——出清的痛感本身是周期后段的特征（[腾讯新闻 2026-09-21](https://news.qq.com/rain/a/20260921A04QEQ00)、[新浪财经 2026-09-21](https://finance.sina.com.cn/tech/roll/2026-09-21/doc-inisqvrw5704901.shtml)）。
2. 猪周期在底部：2026 年 9 月第一周生猪收购价 12.14 元/公斤，同比 −18.4%，行业每头深亏约 226 元；牧原上半年亏损 60.78 亿元但完全成本已降到 11.5 元/公斤，能繁母猪自 2025 年初的 362 万头降至 313 万头，去化已持续四个季度（[凤凰网](https://original.ifeng.com/c/8wPYjLOyuNG)、[中证网 2026-08-21](https://www.cs.com.cn/ssgs/01/2026/08/21/detail_2026082110032905.html)）。
3. 非周期部分仍在增长：伊利上半年营收 644.9 亿元、核心经营利润 83.8 亿元同比 +10%，并拟最高 20 亿元回购注销；1–8 月粮油食品零售额 +6.8%，基本生活类消费增势好于社零总体（[腾讯新闻 2026-08-26](https://news.qq.com/rain/a/20260826A0D9CM00)、[国家统计局 2026-09-15](https://www.stats.gov.cn/sj/zxfb/202609/t20260915_1965311.html)）。

反证：
1. 需求端没有回暖信号：8 月社零同比仅 +0.4%，1–8 月 +1.1%；白酒中秋动销同比持平到小幅下滑，300–800 元价格带承压，政商务需求偏弱。极端估值可以维持很久，均值回归没有时间表。
2. 指数三成以上是白酒（35.1%）、两成是养殖（20.0%，牧原 10.33%、温氏 6.79%）——两个都是深周期行业；亏损股权重 20.94% 使指数 PE 失真，PB 的"极端便宜"有一部分是盈利能力下台阶而不是错杀。猪价若在 2026 年全年低于成本，养殖部分的账面价值会继续被侵蚀。

## 3. 指数匹配

席位内两个候选，按 A4 四问比选：

| 指数 | 成分 | 前十大 | 最大单一 | 行业构成 | 观点错位 | 研究覆盖率 |
|---|---|---|---|---|---|---|
| 中证主要消费 `000932.SH` | 36 | 67.88% | 牧原股份 10.33% | 白酒 35.1、农业综合 20.0、食品 16.0、乳制品 10.3、软饮料 4.8、啤酒 4.3 | 论点是"必选消费整体极端估值"，与指数一致；白酒只占三分之一 | 37.2%（6 只在个股池） |
| 中证白酒 `399997.SZ` | 17 | 88.15% | 贵州茅台 15.95% | 白酒 100 | 只表达白酒去库存这一条线；单一行业、17 只成分、前四大 59% | 38.4% |

**主指数 = `000932.SH`**：① 论点是一篮子必选消费的极端估值，不是单押白酒；② 规则验证里主要消费三折全部通过（回撤更优 3/3、对恒定比例有择时技能），白酒只有两折、记"数据不足"；③ 集中度低一档；④ 可选工具年费 0.60%，白酒 LOF 年费 1.20%。
但要如实交代白酒这一支的位置：白酒指数距近 36 个月高点回撤 55%（状态 0.4452），回撤状态分位 2.8，**已低于自身 P10——若以白酒为主指数并启用，阶梯今天就会给出目标 100% 的买入**；主要消费则在 P10–P25 之间（目标 50%）。白酒 PB 分位 0.8、股息率 4.91%（分位 99.2）比主要消费更极端。用户若想押更纯的白酒周期，改主指数即可，本卡把两种选法的后果都列在这里。
编制：36 只成分，近 12 个月调入 1 只（2.0%）、调出 5 只（5.1%），换手低；指数 2004-12-31 基日，历史可用。

## 4. 预期与估值

- 估值状态（快照 §4 自聚合，指数权重口径）：**PB 2.78，扩张窗分位 1.1（n=183，自 2010-12），10 年窗分位 1.7**；股息率 4.17%（分位 98.9）。PE_TTM 23.70（分位 32.2）只作参考——亏损股权重 20.94%（生猪养殖）超过框架 15% 的降级线，按 A5 改看 PB。
- 方法：`mid_cycle`（周期底部的压力测试）。以 PB 为倍数做三情景，五年期，实施拖累按首选工具年费 0.60%：
  - 熊：估值不回归（期末 PB 仍 2.78），账面价值年 −3%（猪价全年低于成本、白酒继续去化），股息率 4.17% → 年化 +0.57%。
  - 基准：估值零变化，账面价值年 +3%，股息率 4.17% → 年化 +6.57%。**基准情景下回报几乎全部来自股息，可以接受但不厚。**
  - 牛：PB 回到自身 P25（3.51，年化 +4.77%），账面价值年 +5% → 年化 +13.34%。
- 结论：下行由股息托底，上行靠估值回归；这是典型的"极端估值 + 时间换空间"，与 `tactical` 24 个月期限匹配。

## 5. 工具比选

| 工具 | 跟踪 | 年费（管理+托管+销售服务） | 规模 @2026-06-30 | 成立 | 结论 |
|---|---|---|---|---|---|
| 汇添富中证主要消费ETF联接 A `000248.OF` | 000932.SH | 0.50%+0.10%+0 = 0.60% | 43.9 亿 | 2015-03 | **首选**：同类里规模最大、成立最早 |
| 嘉实中证主要消费ETF联接 A `009179.OF` | 000932.SH | 0.50%+0.10%+0 = 0.60% | 未核 | 2020-04 | 备选：费率相同 |
| 招商中证白酒指数 LOF A `161725.SZ` | 399997.SZ | 1.00%+0.20%+0 = 1.20% | 313 亿 | — | 落选：跟踪的是席位内另一指数，年费高一倍 |

以上数字为 tushare `fund_basic` / `fund_nav` 与 akshare `fund_fee_em` 2026-09-23 实测，未与基金公告逐只核对 `[需人工补充]`。首选工具的 TD/TE 快照 §5 未覆盖（未持有）`[需人工补充]`：启用前先跑快照把它加进 HOLDINGS。赎回费：持有不满 7 天 1.5%。

## 6. 点位与仓位

- 推导：框架 A9 唯一 validated 的回撤分位阶梯。`000932.SH` 近 36 个月末收盘最高值 18,429.13（快照 §6b），状态历史分位点 P10 0.6518 / P25 0.7265 / P75 0.9515（n=262，自 2004-12）。
- 点位（`level_at_drawdown_state`）：`add_below` **12,012.11**（目标 100%）、`buy_below` **13,388.76**（目标 50%）、`reduce_above` **17,535.32**（目标 30%）。当前 12,214.41，状态 0.6628、分位 12.2——**在买入区第一档（目标 50% = 5 万），距加仓档只差 1.7%**。
- 本卡 `status=watch`：执行侧对买入侧只发"到点提示复评"告警，不出买入指令。若用户启用（改 `active`、首选工具 `action=buy`），阶梯语义是：跌破 13,388.76 买到 5 万，跌破 12,012.11 买到 10 万，回升不减；升破 17,535.32 减到 3 万。
- 必须交代的代价：规则验证里主要消费三折通过，但年化对满仓平均 −1.1%（第 3 折 +10.9% 对 +18.8%，趋势上涨段空仓的机会成本）；第 4 折阶梯平均仓位 92% 时回撤仍 −38.6%——阶梯只在"回撤之后"才减轻损失，买入区不是底部的保证。
- 仓位：`bet_group = cn-consumer-tactical`，上限 100,000 = 70,000 ÷ 70%。无持仓。

## 7. 核心监控（启用条件 = 阶梯买入档 + 至少一根宏观路标翻面）

用户 2026-09-24 定的口径：宏观上"还不急"。本卡因此把启用条件写成两层——价格层由阶梯给（当前已在买入区第一档），路标层由下面五个人工监控给；
路标一个都没翻之前，卡维持 `watch`，买入侧只出"到点提示"。读数依据：吸引子宏观数据服务 2026-09-24 拉取（内需 −1.0、总需求 −1.0、服务业景气 −1.0、财政政策力度 −0.95，均为下降·维持；企业利润 +0.55、就业 +0.68）；
统计局 8 月社零 +0.4%、核心 CPI +1.0%。这组读数的含义：企业利润与就业没有传导成社零，公共的钱没往居民端走——便宜是价格给的，回归要靠这根传动轴焊上。

| 变量 | 来源 | 当前值 | 触发条件 | 触发动作 | 频率 |
|---|---|---|---|---|---|
| 宏观传动轴：财政力度与内需读数（人工） | 吸引子宏观数据服务 | 财政力度 −0.95、内需 −1.0、总需求 −1.0 | 财政力度向 0 回升且资金去收入端；内需/总需求置信度松动到 −0.5 一带 | 复评（启用条件之一） | 月 |
| 居民中长期贷款（人工） | 人民银行 | 7 月同比多减 | 当月同比转正 | 复评 | 月 |
| 核心 CPI（人工） | 国家统计局 | 8 月 +1.0% | 站上 1.5% | 复评 | 月 |
| 白酒量价齐动（人工） | 华创食饮等渠道调研 / 今日酒价 | 批价约 1730 元坚挺，动销持平到小幅下滑 | 中秋或春节动销同比转正且批价不跌破 1600 元 | 复评 | 月 |
| 生猪收购价（人工） | 农业农村部周报 | 12.14 元/公斤（9 月第一周） | 连续 4 周高于 15 元/公斤 | 复评（养殖部分估值逻辑改变） | 月 |

## 8. 退出与复评

- 失效条件：① 白酒渠道重新累库——批价跌破 1600 元且经销商库存回升 → `close`（去库存后段的判断错了）；② 能繁母猪存栏连续 3 个月回升 → `close`（猪周期底部判断错了）。
- 最迟复评日 2026-11-20（三季报与双节动销数据落地后）。
- 记分：基准 `H11025.CSI`，预登记 2026-09-23，置信度 50%，写卡时点位 12,214.41。

```json
{
  "card_schema_version": 1,
  "card_id": "cn-consumer-tactical",
  "as_of_date": "2026-09-24",
  "supersedes": null,
  "framework": {
    "path": "framework/etf_framework.md",
    "version": "v0.1"
  },
  "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
  "task": "tactical",
  "status": "watch",
  "no_buy_reason": null,
  "close_reason": null,
  "exposure": {
    "index_code": "000932.SH",
    "index_name": "中证主要消费",
    "asset_type": "sector",
    "currency": "CNY",
    "counts_toward_sector_cap": true,
    "china_equity": true,
    "view_mismatch_note": "论点是必选消费整体的极端估值，与指数一致；白酒只占 35.1%、养殖 20.0%——押的不是单一子行业。席位内另一候选中证白酒已低于自身 P10（状态分位 2.8），若改用它，启用后阶梯今天就给出目标 100% 的买入",
    "structure": {
      "weights_as_of": "2026-08-31",
      "constituent_count": {
        "value": 36,
        "source": "snapshot§3"
      },
      "max_constituent_weight_pct": {
        "value": 10.33,
        "source": "snapshot§3"
      },
      "top10_weight_pct": {
        "value": 67.88,
        "source": "snapshot§3"
      },
      "research_coverage_pct": {
        "value": 37.2,
        "source": "snapshot§3"
      },
      "top_constituents": [
        {
          "code": "002714.SZ",
          "name": "牧原股份",
          "weight_pct": {
            "value": 10.33,
            "source": "snapshot§3"
          }
        },
        {
          "code": "600887.SH",
          "name": "伊利股份",
          "weight_pct": {
            "value": 10.31,
            "source": "snapshot§3"
          }
        },
        {
          "code": "600519.SH",
          "name": "贵州茅台",
          "weight_pct": {
            "value": 10.16,
            "source": "snapshot§3"
          }
        }
      ]
    }
  },
  "thesis": {
    "statement": "主要消费指数 PB 处于 2010 年以来第 1.1 分位、股息率 4.17% 处于第 98.9 分位，白酒渠道库存到低位、生猪去化进入第四个季度——这是买极端估值等均值回归的押注，不是买景气；当前点位已在阶梯买入区",
    "evidence": [
      "白酒渠道库存处于低位、头部品牌库存下降，飞天茅台批价回升至约 1750 元并企稳；56.6% 经销商反映价格倒挂加剧、61.9% 终端门店收缩，出清痛感是周期后段特征",
      "生猪收购价 12.14 元/公斤同比 -18.4%、每头深亏约 226 元；牧原上半年亏 60.78 亿但完全成本降至 11.5 元/公斤，能繁母猪自 362 万头降至 313 万头，去化持续四个季度",
      "伊利上半年核心经营利润 83.8 亿同比 +10% 并拟最高 20 亿回购注销；1–8 月粮油食品零售额 +6.8%，基本生活类消费好于社零总体"
    ],
    "counter_evidence": [
      "需求无回暖信号：8 月社零同比仅 +0.4%、1–8 月 +1.1%；白酒中秋动销持平到小幅下滑，300–800 元价格带承压。极端估值可以维持很久",
      "指数 35.1% 白酒 + 20.0% 养殖都是深周期；亏损股权重 20.94% 使 PE 失真，PB 极端便宜有一部分是盈利能力下台阶而非错杀"
    ],
    "horizon_months": 24
  },
  "expectation": {
    "method": "mid_cycle",
    "scenarios": {
      "bear": {
        "inputs": {
          "eps_growth_pct": {
            "value": -3,
            "source": "ai_estimate",
            "note": "以 PB 为倍数，此处为账面价值增速：猪价全年低于成本、白酒继续去化"
          },
          "dividend_yield_pct": {
            "value": 4.17,
            "source": "snapshot§4"
          },
          "current_multiple": {
            "value": 2.78,
            "source": "snapshot§4",
            "note": "PB，指数权重口径"
          },
          "terminal_multiple": {
            "value": 2.78,
            "source": "snapshot§4",
            "note": "估值不回归"
          },
          "years": {
            "value": 5,
            "source": "ai_estimate"
          },
          "drag_pct": {
            "value": 0.6,
            "source": "ai_estimate",
            "note": "首选工具年费 0.60%（tushare/akshare 2026-09-23 实测）"
          }
        },
        "valuation_change_pct": {
          "value": 0,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 0.57,
          "source": "calc:scenario_annual_return"
        }
      },
      "base": {
        "inputs": {
          "eps_growth_pct": {
            "value": 3,
            "source": "ai_estimate",
            "note": "账面价值增速"
          },
          "dividend_yield_pct": {
            "value": 4.17,
            "source": "snapshot§4"
          },
          "current_multiple": {
            "value": 2.78,
            "source": "snapshot§4"
          },
          "terminal_multiple": {
            "value": 2.78,
            "source": "snapshot§4"
          },
          "years": {
            "value": 5,
            "source": "ai_estimate"
          },
          "drag_pct": {
            "value": 0.6,
            "source": "ai_estimate"
          }
        },
        "valuation_change_pct": {
          "value": 0,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 6.57,
          "source": "calc:scenario_annual_return"
        }
      },
      "bull": {
        "inputs": {
          "eps_growth_pct": {
            "value": 5,
            "source": "ai_estimate",
            "note": "账面价值增速"
          },
          "dividend_yield_pct": {
            "value": 4.17,
            "source": "snapshot§4"
          },
          "current_multiple": {
            "value": 2.78,
            "source": "snapshot§4"
          },
          "terminal_multiple": {
            "value": 3.51,
            "source": "snapshot§4",
            "note": "PB 扩张窗 P25"
          },
          "years": {
            "value": 5,
            "source": "ai_estimate"
          },
          "drag_pct": {
            "value": 0.6,
            "source": "ai_estimate"
          }
        },
        "valuation_change_pct": {
          "value": 4.77,
          "source": "calc:scenario_annual_return"
        },
        "annual_return_pct": {
          "value": 13.34,
          "source": "calc:scenario_annual_return"
        }
      }
    },
    "valuation_state": {
      "index_code": "000932.SH",
      "metric": "pb",
      "value": {
        "value": 2.78,
        "source": "snapshot§4",
        "note": "亏损股权重 20.94% 超过 15% 降级线，PE 23.70（分位 32.2）只作参考"
      },
      "percentile_expanding": {
        "value": 1.1,
        "source": "snapshot§4"
      },
      "percentile_10y": {
        "value": 1.7,
        "source": "snapshot§4"
      },
      "sample_n": {
        "value": 183,
        "source": "snapshot§4"
      },
      "as_of": "2026-09-18"
    }
  },
  "instruments": {
    "merge_note": "新席位，无持仓；首选与备选跟踪同一指数，只比可靠与便宜",
    "list": [
      {
        "code": "000248.OF",
        "name": "汇添富中证主要消费ETF联接-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "primary",
        "action": "none",
        "reason": "未持有；同类里规模最大（43.9 亿）、成立最早（2015-03），年费 0.60%。启用时改 action=buy"
      },
      {
        "code": "009179.OF",
        "name": "嘉实中证主要消费ETF联接-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "backup",
        "action": "none",
        "reason": "未持有；费率相同，规模未核"
      },
      {
        "code": "161725.SZ",
        "name": "招商中证白酒指数(LOF)-A",
        "instrument_type": "otc_fund",
        "share_class": "A",
        "currency": "CNY",
        "platform_account": "支付宝",
        "role": "rejected",
        "action": "none",
        "reason": "跟踪席位内另一指数（中证白酒），年费 1.20% 为首选两倍；若用户改主指数为白酒则它成为首选"
      }
    ]
  },
  "trade_rules": {
    "min_holding_days": 7,
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
      "index_code": "000932.SH",
      "add_below": {
        "level": {
          "value": 12012.11,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 100,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 18429.13,
            "source": "snapshot§6"
          },
          "state": {
            "value": 0.6518,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P10"
          }
        },
        "rationale": "回撤状态回到自身历史 P10；当前 12,214.41 只在其上方 1.7%"
      },
      "buy_below": {
        "level": {
          "value": 13388.76,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 50,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 18429.13,
            "source": "snapshot§6"
          },
          "state": {
            "value": 0.7265,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P25"
          }
        },
        "rationale": "回撤状态回到自身历史 P25；当前已在其下方（买入区第一档），status=watch 只告警"
      },
      "reduce_above": {
        "level": {
          "value": 17535.32,
          "source": "calc:level_at_drawdown_state"
        },
        "target_ratio_pct": {
          "value": 30,
          "source": "framework:A13"
        },
        "inputs": {
          "rolling_high": {
            "value": 18429.13,
            "source": "snapshot§6"
          },
          "state": {
            "value": 0.9515,
            "source": "snapshot§6",
            "note": "回撤状态扩张窗 P75"
          }
        },
        "rationale": "回撤状态回到自身历史 P75（距 36 月高点约 5%）：升破即减到上限的 30%"
      },
      "reduce_mode": "to_target_ratio",
      "no_anchor_reason": null,
      "valid_until": "2026-10-31"
    }
  },
  "sizing": {
    "bet_group": "cn-consumer-tactical",
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
      "name": "宏观传动轴：财政力度与内需读数",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "财政政策力度读数从 −0.95 向 0 回升且资金去向为收入端（社保、生育、消费补贴），同时内需/总需求读数的置信度从 −1.0 松动到 −0.5 一带",
      "data_source": "吸引子宏观数据服务（macro_latest.py：中国-财政政策力度、中国-内需、中国-总需求）",
      "current_text": "2026-09-24：财政力度 −0.95、内需 −1.0、总需求 −1.0，均为下降·维持",
      "frequency": "monthly",
      "action": "review",
      "action_note": "启用条件之一：便宜是价格给的，回归要靠这根传动轴焊上"
    },
    {
      "name": "居民中长期贷款",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "当月新增居民中长期贷款同比转正",
      "data_source": "人民银行金融统计数据",
      "current_text": "2026 年 7 月居民中长贷同比多减；8 月数据待核",
      "frequency": "monthly",
      "action": "review",
      "action_note": "私人信用派生重启的唯一硬证据"
    },
    {
      "name": "核心 CPI",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "核心 CPI 同比站上 1.5%（而非上游涨价推着 CPI 走）",
      "data_source": "国家统计局",
      "current_text": "2026 年 8 月核心 CPI +1.0%，CPI +0.8%",
      "frequency": "monthly",
      "action": "review",
      "action_note": ""
    },
    {
      "name": "白酒量价齐动",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "中秋、春节任一节点白酒动销同比转正，且飞天批价不跌破 1600 元/瓶；只有批价涨、进货量降仍算清淤未回暖",
      "data_source": "华创食饮等渠道调研 / 今日酒价",
      "current_text": "2026 年中秋：批价约 1730 元坚挺，动销同比持平到小幅下滑，渠道库存低位",
      "frequency": "monthly",
      "action": "review",
      "action_note": "跌破 1600 且经销商累库 → 走失效条件①"
    },
    {
      "name": "生猪收购价",
      "kind": "manual",
      "metric": null,
      "operator": null,
      "threshold": {
        "value": null,
        "source": null
      },
      "condition_text": "连续 4 周高于 15 元/公斤（周期反转）",
      "data_source": "农业农村部周报",
      "current_text": "12.14 元/公斤（2026 年 9 月第一周）",
      "frequency": "monthly",
      "action": "review",
      "action_note": "养殖部分的估值逻辑改变"
    }
  ],
  "exit": {
    "invalidation": [
      {
        "name": "白酒渠道重新累库",
        "kind": "manual",
        "metric": null,
        "operator": null,
        "threshold": {
          "value": null,
          "source": null
        },
        "condition_text": "飞天茅台批价跌破 1600 元且经销商库存回升",
        "data_source": "券商渠道调研、酒协报告",
        "current_text": "库存低位、批价约 1750",
        "frequency": "monthly",
        "action": "close",
        "action_note": "去库存后段的判断错了"
      },
      {
        "name": "猪周期底部判断错",
        "kind": "manual",
        "metric": null,
        "operator": null,
        "threshold": {
          "value": null,
          "source": null
        },
        "condition_text": "能繁母猪存栏连续 3 个月回升",
        "data_source": "农业农村部月度数据",
        "current_text": "牧原能繁母猪 313 万头，仍在去化",
        "frequency": "monthly",
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
    "confidence_pct": 50,
    "entry_ref_index_level": {
      "value": 12214.41,
      "source": "snapshot§6"
    }
  }
}
```
