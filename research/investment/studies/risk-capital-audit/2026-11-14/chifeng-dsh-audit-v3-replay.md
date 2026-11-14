# 赤峰 dsh 历史输入的 audit-v3 算术重演

本文件由Codex生成，dsh只标明原研究来源；不是该端新研报。原经营/现金条件未被本次算术验收证明，无新正式报价。与原P1/V50/控制逐项相等；资金经济归属见同目录隔离复评。

<!-- research-checks:start -->
研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：

| 情景 | 收入 | 经常净利率 | 利润调整 | 经常归母利润 | PE | 权益调整 | 权益价值 | V50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| low | 116 | 15.7927306% | 0 | 18.3195675 | 12 | 0 | 219.83481 | 9.94 |
| base | 131.075 | 19.57706207% | 0 | 25.6606341 | 15 | 0 | 384.9095116 | 17.41 |
| high | 153 | 23.32253647% | 0 | 35.6834808 | 18 | 0 | 642.3026544 | 29.05 |

| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |
|---|---:|---|---|---|
| d_base | 20% | 15%—20% | R_MODEL_BASE | unchanged |
| r_chip | 2% | 0%—3% | R_CHIP_OVERHANG | unchanged |
| r_v5 | 16% | 12%—18% | R_GOLD_COST_TAIL | unchanged |
| r_gov | 0% | 0%—2% | 无额外扣减 | unchanged |
| r_terminal | 0% | 0%—1% | 无额外扣减 | unchanged |

总折扣乘数：0.65856；用途：frozen。
明确报价：P1={"base": 11.46}；T1={"price_condition": "股价≥29.05元/股"}。

| 约束 | 作用 | 状态 | 依据 |
|---|---|---|---|
| MARGIN_COST_QUALITY | entry,add: eligibility | blocking | 2026Q3 单季归母 5.53 亿元(-41.84%)、单季归母净利率 18.0%（上年同期约 28.2%）、自产金 AISC 494.31 元/克(+38.71%)、Q3 单季产量约 2.76 吨、全年目标下调至 12.5–13 吨；利润率趋势与 OCF 匹配度合格线未同时满足，不具买入型资格。 |
| R4-EARNINGS-600988 | entry,add: eligibility | unknown | R4 仅部分成立；正式 Q3 减产和单位成本上升，2027 正常化恢复所需的产量、利润率与现金兑现证据未齐，不能以预测替代资格。 |
| TEMP-600988 | entry,add: eligibility | unknown | 温度代理缺失且未证明已有等价运行时属主接替，不能默认冷档；cap_final 的 min(单票硬上限,温度仓位上限) 中温度项未核。 |
| ADD-PLAN-20261007 | add: eligibility | blocking | 接续 10/7 取消追加的研究决定；R17、供给证据不足、产量/成本恢复和 Terminal 工程约束仍有未决；新两价不使旧取消自动失效。 |
| R17_PRECIOUS_METAL | add: eligibility | blocking | R17 贵金属基准情景（强美元＋加息落地）叠加 D3：估值日 SGE Au99.99 收 851.33 元/克（-2.48%），现货约 3,930–3,950 美元/盎司（低于 4,200），美元指数 11/11 收 102.908（高于 100），r_v5 已上调至 16%，加仓判断从严。 |
| R17-GOLD-600988 | add: eligibility | unknown | R17：保留强美元+加息基准及加仓从严；黄金/ICE DXY 同口径连续序列未齐（本轮仅 11/11、11/12 单点与 WGC 周报），未证明撤销/降级条件；与 R17_PRECIOUS_METAL 为同一规则的不同来源实例，均保留。 |
| R14_OIL_COST_UNKNOWN | add: eligibility | unknown | R14 油价三层暴露：公司未披露燃油/电力等能源成本占比，100→130 美元的成本传导与 OCF 桥仅有情景假设，压力测试无法判定；10 月 PPI 燃料动力购进同比 +18.6% 强化该敞口而非解除。取得分矿山能源成本与传导证据前不追加。 |
| R14-ENERGY-600988 | add: eligibility | unknown | R14：柴油、电力实质暴露存在（2025 年柴油 1.0197 亿升、外购电力 7.25 亿千瓦时），2026 量价成本金额、传导/套保及 100→130、85 美元对应现金流桥仍未知；纯 α 情景不足以判 passed；与 R14_OIL_COST_UNKNOWN 为同一规则的不同来源实例，均保留。 |
| HOLD-Q3-20261024 | holding: review_holding | blocking | 接续正式 Q3 单季归母同比 -41.84%、产销量目标下调及资本回报弱化的持仓减仓复评；11/11 收盘 39.30 元仍高于 V50 上沿 29.05 元（+35.3%），旧纯价格/PB 高分位成因已由本轮重算，但经营恢复未被正式证明，未确认核心盈利/现金流失效。 |
| HOLDING_MARGIN_REVIEW | holding: review_holding | blocking | Q3 单季盈利与 AISC 同步恶化、全年产量指引下调；11/11 收盘 39.30 元高于 V50 上沿 29.05 元，T1 处于减仓评估区间；评估减仓不等于清仓。 |
| D5-REPAIR-600988 | entry,add: eligibility | not_applicable | 本轮为独立财报复研，未提出低位轮动新承接；D5 于 11/08 维持回退深化、R21 未退出，本公司非承接型。D5 深化状态不被本公司研究解除。 |
| DEAL_INTEGRATION | add: eligibility | not_applicable | 紫金入股 2026-10-22 完成，董事会提前换届待 2026-11-16 临时股东会；注册资本变更登记仍在办理（月报注册资本仍 1,900,411,178 元）；整合与关联交易安排未构成当前阻断，仅作观察。 |
| R1-CHASE-600988 | entry,add: eligibility | not_applicable | R1 三项：① 公募分位/板块换手 unknown（个股换手 2.60%，1 年分位 30.4%）；② PE(TTM) 26.26、近 1 年分位 80.8% 命中，但包内 PB 5.88 分子分母时点不一致（备考 PB 3.84，分位不可比）；③ 有当季正式业绩，明确不成立。三项未合取，不构成追高否决。 |
| R9-DIVIDEND-600988 | entry,add: eligibility | not_applicable | 股息率(TTM)0.81%、商品波动及高 capex，本次不作为红利/底仓锚，不把 R9 适用对象扩大。 |
| EXIT-CORE-600988 | entry,add,holding: exit_required | not_applicable | 尚未确认核心盈利/现金流被证伪或 Terminal 不可能；观察单季盈利下滑与价格高估不能宣告清仓。 |
| R6-EGM-20261116 | entry,add: freeze | not_applicable | 2026-11-16 09:00 临时股东会审议注册资本变更与董事会提前换届；会前 48 小时（11/14–16）不新增。估值日 11/12 尚未进入该窗口，且 entry/add 已由持续约束阻断，故当前不单独构成额外阻断；过窗按会议结果复核。 |
| R6-FOMC-20261027 | entry,add: freeze | clear | R6 本次事件已完成公司复评：10/28 正式声明维持 3.75%–4.00%，发布会未承诺路径回撤；已读会后 CMT（11/10 10Y 4.98%、30Y 5.35%）与美元/黄金，按已确认政策重算本公司无降息及对称情景。解除本次窗口义务，不解除 D1、R17 或其它资格限制。 |
| R6-CPI-20261014 | entry,add: freeze | clear | 10/14 CPI 结果已通过冻结 10/25 官方来源接续并纳入无降息与成本模型；3.7%/核心环比 0.3 仍不解除 D1；10 月 CPI 核心环比 0.3 已由 11/10 官方页复核，单个 CPI 窗口复评完成。 |
| UST10Y-20261009-REVIEW | holding: review_holding | clear | 旧五日 CMT>5% 触发已由基线完成公司复评并接续；最新 11/04–11/10 为 4.90/4.84/4.86/4.88/4.98%，不满足新的连续五日>5% 条件。旧义务的解除依据是公司 R3/V5 分析完成，不是水位回落。 |
| PRICE-P1-600988 | entry,add: eligibility | clear | 估值日 11/11 收盘 39.30 元高于 P1 11.46 元（未到买入价格）；纯价格条件由运行时判断，不制造长期研究阻断。 |
| PUBLICATION_PRICE_UNAVAILABLE | entry,add: unavailable | clear | 本轮已形成有效 P1/T1 并完成暂存交付，价格不可得状态解除。 |
| METHOD_COMPATIBILITY | entry,add: freeze | blocking | 发布前方法或采纳证据接续变化，适用性待复核；保留原价格 |

| 范围 | 当前研究状态 | 未解约束ID |
|---|---|---|
| entry | blocked | MARGIN_COST_QUALITY, R4-EARNINGS-600988, TEMP-600988, METHOD_COMPATIBILITY |
| add | blocked | MARGIN_COST_QUALITY, R4-EARNINGS-600988, TEMP-600988, ADD-PLAN-20261007, R17_PRECIOUS_METAL, R17-GOLD-600988, R14_OIL_COST_UNKNOWN, R14-ENERGY-600988, METHOD_COMPATIBILITY |
| holding | review_required | HOLD-Q3-20261024, HOLDING_MARGIN_REVIEW |

恢复前须同时解除全部仍有效约束：{"add": ["MARGIN_COST_QUALITY", "R4-EARNINGS-600988", "TEMP-600988", "ADD-PLAN-20261007", "R17_PRECIOUS_METAL", "R17-GOLD-600988", "R14_OIL_COST_UNKNOWN", "R14-ENERGY-600988", "METHOD_COMPATIBILITY"], "entry": ["MARGIN_COST_QUALITY", "R4-EARNINGS-600988", "TEMP-600988", "METHOD_COMPATIBILITY"], "holding": ["HOLD-Q3-20261024", "HOLDING_MARGIN_REVIEW"]}。
<!-- research-checks:end -->

<details><summary>计算、风险归属与解除条件审计输入</summary>

<!-- research-audit:start -->
```json
{
  "schema_version": "stock-research-audit/v3",
  "identity": {
    "code": "600988.SH",
    "generator": "dsh",
    "valuation_date": "2026-11-12",
    "currency": "CNY"
  },
  "valuation": {
    "kind": "profit_pe",
    "currency": "CNY",
    "amount_unit": "100_million",
    "shares": 2211313909,
    "fx_to_quote": 1,
    "horizon": "2027年正常化年景（估值日2026-11-12）",
    "profit_basis": "经常性归母净利润：自产金销量×实现金价−单位营业成本＋其他业务毛利−税金及附加−期间费用，按34%–35%所得税率与81%–82%归母比例折算；不含一次性项目，不以H股募资投放后的增量收益或利息收入为前提",
    "scenarios": {
      "low": {
        "revenue": 116.0,
        "net_margin": 0.157927306,
        "adjustments": [],
        "profit": 18.3195675,
        "pe": 12,
        "equity_value": 219.83481,
        "equity_adjustments": []
      },
      "base": {
        "revenue": 131.075,
        "net_margin": 0.1957706207,
        "adjustments": [],
        "profit": 25.6606341,
        "pe": 15,
        "equity_value": 384.9095116,
        "equity_adjustments": []
      },
      "high": {
        "revenue": 153.0,
        "net_margin": 0.2332253647,
        "adjustments": [],
        "profit": 35.6834808,
        "pe": 18,
        "equity_value": 642.3026544,
        "equity_adjustments": []
      }
    }
  },
  "baseline": {
    "report_path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/chifeng-baseline-dsh.md",
    "sha256": "fb28c3a2dc0da80065ae6ecba86aabdce7cd835f940c61ab57690e4623179e0b",
    "discounts": {
      "d_base": {
        "value": 0.2,
        "range": [
          0.15,
          0.2
        ],
        "quote": "Precheck 警惕取研究区间上沿；销量/售价/成本/税率四重不确定性，Q3 已证伪“高金价必转化为利润”"
      },
      "r_chip": {
        "value": 0.02,
        "range": [
          0.0,
          0.03
        ],
        "quote": "H 股 3.109 亿股供给已落地但锁定 18 个月；ESOP 处理未决；公募与板块拥挤分位缺失"
      },
      "r_v5": {
        "value": 0.16,
        "range": [
          0.12,
          0.18
        ],
        "quote": "常态 8%＋R17 一档 4pct＝12%；金价 <4,200 且美元 >100 再上调一档至 16%"
      },
      "r_gov": {
        "value": 0.0,
        "range": [
          0.0,
          0.02
        ],
        "quote": "未见治理红线；换届走法定程序；补偿为已批准上限且金额不重大。0 不等于无风险"
      },
      "r_terminal": {
        "value": 0.0,
        "range": [
          0.0,
          0.01
        ],
        "quote": "终局困难已由 12–18 倍 PE、未计 SND 利润与低档利润率体现，避免重复扣减"
      }
    }
  },
  "discounts": {
    "d_base": {
      "value": 0.2,
      "range": [
        0.15,
        0.2
      ],
      "risk_ids": [
        "R_MODEL_BASE"
      ],
      "reason": "沿用同端基线 20%（研究区间 15%–20% 上沿）：2027 年景含销量、实现价、单位成本与税率四重不确定性；Q3 单季归母 -41.84% 已证伪“高金价必转化为利润”的线性假设；估值日金价回落但公司产量与成本事实未更新，不确定性结构与上期同质。",
      "change": {
        "kind": "unchanged",
        "reason": "Q3 报表、产量与成本事实未更新；金价由 11/02 SGE 836.08 至 11/12 851.33 的变动已进入收入情景，不在折扣重复计量；模型不确定性未变，故取值与区间沿用。",
        "evidence": []
      }
    },
    "r_chip": {
      "value": 0.02,
      "range": [
        0.0,
        0.03
      ],
      "risk_ids": [
        "R_CHIP_OVERHANG"
      ],
      "reason": "H 股 3.109 亿股已于 10/22 发行完毕、10 月月报确认总股本 22.11 亿股；ESOP 1,518 万股处理未取得明确公告；公募与板块拥挤分位仍缺。近 5 日 +13.8% 为低量上行（量比 0.70、换手 2.60%），不构成新增筹码供给，故沿用 2%。",
      "change": {
        "kind": "unchanged",
        "reason": "股本、ESOP 与拥挤分位三项事实延续；价格上行属估值/预期变化，已由 P1 与 T1 相对现价表达，不在筹码折扣重复收费。",
        "evidence": []
      }
    },
    "r_v5": {
      "value": 0.16,
      "range": [
        0.12,
        0.18
      ],
      "risk_ids": [
        "R_GOLD_COST_TAIL"
      ],
      "reason": "常态 8%＋R17 贵金属基准情景一档 4pct＝12%；估值日 SGE Au99.99 收 851.33 元/克（现货约 3,930–3,950 美元/盎司，低于 4,200），美元指数 11/11 收 102.908（高于 100），D3“再上调一档”条件持续成立→16%；覆盖金价与成本同向不利、流动性冲击与汇率折算尾部，不重复扣利润。",
      "change": {
        "kind": "unchanged",
        "reason": "R17/D3 的触发条件（金价<4,200、美元>100）在估值日仍成立，触发档位未变；11/12 金价进一步回落属同一已触发主张的范围，未出现需要新增档位的规则证据。",
        "evidence": []
      }
    },
    "r_gov": {
      "value": 0.0,
      "range": [
        0.0,
        0.02
      ],
      "risk_ids": [],
      "reason": "未见治理红线：控制权变更 10/22 完成，董事会提前换届待 11/16 股东会，离任薪酬补偿 7,805 万元为已批准税前上限；11/1–11/12 公告窗口仅见 11/02 月报（11/03 A 股转载），无新增治理事件。0 不等于无风险，保留负面触发。",
      "change": {
        "kind": "unchanged",
        "reason": "治理事实仅有程序推进（月报、11/16 会期），无新增红线证据，故沿用 0 与论证区间。",
        "evidence": []
      }
    },
    "r_terminal": {
      "value": 0.0,
      "range": [
        0.0,
        0.01
      ],
      "risk_ids": [],
      "reason": "终局困难已由 12–18 倍 PE、未计 SND 资源利润与低档利润率体现；估值日隐含终局利润 86.91 亿元、隐含倍数 2.63 倍、隐含全球矿产金份额约 1.08%，不另设终局折扣。",
      "change": {
        "kind": "unchanged",
        "reason": "终局参数与可达性判断未变（隐含份额约 1.08%、可达性困难），故沿用。",
        "evidence": []
      }
    }
  },
  "risks": [
    {
      "id": "R_MODEL_BASE",
      "owner": "d_base",
      "scope": "2027 年景销量/实现价/单位成本/税率的联合不确定性（含技改达产、品位与加纳税制）",
      "description": "正常化年景假设的模型不确定性；2026 年目标 12.5–13 吨且 Q4 目标与全年上限算术不完全吻合；实现价与成本同时波动。",
      "source": "本报告 §5.2；2026 年第三季度报告 PDF7–8；上海黄金交易所 2026-11-12"
    },
    {
      "id": "R_CHIP_OVERHANG",
      "owner": "r_chip",
      "scope": "筹码与股本：H 股新增供给已落地但锁定 18 个月、ESOP 处理未决、公募分位未知",
      "description": "新股供给与尚未完成的 ESOP 处理带来筹码不确定性；公募持仓分位、板块换手分位缺失。",
      "source": "完成公告 2026-10-22 PDF2–4；2026 年 10 月月报 PDF3/8"
    },
    {
      "id": "R_GOLD_COST_TAIL",
      "owner": "r_v5",
      "scope": "金价与成本同向恶化的联合尾部（超出单情景假设的相关性）、流动性冲击与汇率折算的生存尾部",
      "description": "金价跌破 4,200 美元且美元站稳 100 触发 D3 再上调一档；能源与税费上行可能同时发生。",
      "source": "上海黄金交易所 2026-11-12；证券时报e公司 2026-11-12 美元指数；2026 年第三季度报告 PDF7–8"
    },
    {
      "id": "R_PRICE_ABSORBED",
      "owner": "revenue",
      "scope": "已吸收：2027 实现价假设 800/845/900 元/克（约合 3,700/3,900/4,170 美元/盎司，按 6.72 折算）",
      "description": "金价水平本身已进入收入情景，不再另设折扣。",
      "source": "上海黄金交易所 2026-11-12 收 851.33 元/克；WGC Q3 2026 LBMA 季度均价"
    },
    {
      "id": "R_VOLUME_ABSORBED",
      "owner": "revenue",
      "scope": "已吸收：自产金销量假设 12.5/13.5/15.0 吨",
      "description": "9M 产量 -16.78%、Q3 单季约 2.76 吨、全年目标 12.5–13 吨已进入销量假设。",
      "source": "2026 年第三季度报告 PDF7–8"
    },
    {
      "id": "R_COST_ABSORBED",
      "owner": "margin",
      "scope": "已吸收：单位营业成本 385/405/425 元/克与税金及附加 7.2%–8.0%、有效税率 34%–35%",
      "description": "9M 营业成本 403.33 元/克(+23.40%)、AISC 494.31(+38.71%)、加纳阶梯资源税已进入利润率假设。",
      "source": "2026 年第三季度报告 PDF7–8"
    },
    {
      "id": "R_MULTIPLE_ABSORBED",
      "owner": "multiple",
      "scope": "已吸收：PE 12/15/18 倍的选择",
      "description": "Q3 单季归母 -41.84%、金价回落与加息预期已体现在低档倍数与正常化利润下滑。",
      "source": "2026 年第三季度报告 PDF2–4；上海黄金交易所 2026-11-12"
    },
    {
      "id": "R_QUALIFY",
      "owner": "eligibility",
      "scope": "资格：盈利兑现合格线未满足，不进入买入型候选",
      "description": "单季归母净利率逐季下行至 18.0%，AISC 同比 +38.71%，Q3 产量低于 3.5 吨门槛。",
      "source": "2026 年第三季度报告 PDF2–4、7–8"
    },
    {
      "id": "R_ENERGY_GAP",
      "owner": "eligibility",
      "scope": "资格：R14 能源成本占比与传导/OCF 桥缺证",
      "description": "公司披露柴油与电力耗用量及单位成本，但未披露能源成本金额占比与到矿价格，100→130 美元压力无法判定。",
      "source": "2026 年第三季度报告 PDF7–8；2025 年度 ESG 报告 PDF92"
    },
    {
      "id": "R_RECOVERY_GAP",
      "owner": "eligibility",
      "scope": "资格：R4 紧缩下独立成立性所需 2027 产量/利润率/现金恢复证据未齐",
      "description": "Q3 正式减产与单位成本上升；2027 正常化恢复尚无可核指引，不能以预测替代资格。",
      "source": "2026 年第三季度报告 PDF2–4、7–8"
    },
    {
      "id": "R_TEMP_GAP",
      "owner": "eligibility",
      "scope": "资格：温度代理缺失，cap 输入未完成",
      "description": "China-MM/50ETF 波指与沪深300 温度未取得，不能默认冷档或据此放宽。",
      "source": "本报告 §4/§7；框架 compact §6 温度"
    },
    {
      "id": "R_ADD_PLAN",
      "owner": "eligibility",
      "scope": "资格：10/7 取消追加的研究决定仍有效",
      "description": "产销、成本与现金兑现及 Terminal 工程证据未足，旧取消不因两价或价格回落自动失效。",
      "source": "本批 controls-evidence d415382…；本报告 §7.3"
    }
  ],
  "constraints": [
    {
      "id": "MARGIN_COST_QUALITY",
      "scope": [
        "entry",
        "add"
      ],
      "status": "blocking",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "2026Q3 单季归母 5.53 亿元(-41.84%)、单季归母净利率 18.0%（上年同期约 28.2%）、自产金 AISC 494.31 元/克(+38.71%)、Q3 单季产量约 2.76 吨、全年目标下调至 12.5–13 吨；利润率趋势与 OCF 匹配度合格线未同时满足，不具买入型资格。",
      "release_conditions": [
        "连续两个正式报告期归母净利率回升且不低于 20%",
        "同期自产金 AISC 同比不再上升",
        "自产金季度产量恢复到 3.5 吨以上并维持两个季度",
        "OCF/归母不低于 1.0 且无税费或回款异常解释"
      ]
    },
    {
      "id": "R4-EARNINGS-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "R4 仅部分成立；正式 Q3 减产和单位成本上升，2027 正常化恢复所需的产量、利润率与现金兑现证据未齐，不能以预测替代资格。",
      "release_conditions": [
        "正式经营更新或财报证明产量恢复、成本可控、利润/现金兑现与持续销货可见度；按同口径重算并完成逐股买入资格复核。"
      ]
    },
    {
      "id": "TEMP-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "温度代理缺失且未证明已有等价运行时属主接替，不能默认冷档；cap_final 的 min(单票硬上限,温度仓位上限) 中温度项未核。",
      "release_conditions": [
        "取得估值截止兼容的 China-MM/50ETF 波指与沪深300 温度及相应 cap 评估，或明确绑定合法等价运行时接替并逐项核验。"
      ]
    },
    {
      "id": "ADD-PLAN-20261007",
      "scope": [
        "add"
      ],
      "status": "blocking",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "接续 10/7 取消追加的研究决定；R17、供给证据不足、产量/成本恢复和 Terminal 工程约束仍有未决；新两价不使旧取消自动失效。",
      "release_conditions": [
        "重新研究本轮追加计划：产销、成本及现金兑现改善且 Terminal 工程证据足够，R17/R14 适用资格复核完成；仍须解除 add 范围其余全部限制。"
      ]
    },
    {
      "id": "R17_PRECIOUS_METAL",
      "scope": [
        "add"
      ],
      "status": "blocking",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "R17 贵金属基准情景（强美元＋加息落地）叠加 D3：估值日 SGE Au99.99 收 851.33 元/克（-2.48%），现货约 3,930–3,950 美元/盎司（低于 4,200），美元指数 11/11 收 102.908（高于 100），r_v5 已上调至 16%，加仓判断从严。",
      "release_conditions": [
        "黄金收复 4,500 美元/盎司 → 按 D3 撤销上调复核",
        "或黄金连续两周收于 4,300 美元/盎司上方且美元指数在 100 上方 → 按 D3 降级为对称情景复核（两条为规则内部替代路径，不替代其它约束）"
      ]
    },
    {
      "id": "R17-GOLD-600988",
      "scope": [
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "R17：保留强美元+加息基准及加仓从严；黄金/ICE DXY 同口径连续序列未齐（本轮仅 11/11、11/12 单点与 WGC 周报），未证明撤销/降级条件；与 R17_PRECIOUS_METAL 为同一规则的不同来源实例，均保留。",
      "release_conditions": [
        "依 D3 原合法路径核验黄金收复 4500 的撤销复核，或连续两周黄金收于 4300 上且美元 100 上方的降级复核；逐股评估加仓，不凭单日反弹恢复。"
      ]
    },
    {
      "id": "R14_OIL_COST_UNKNOWN",
      "scope": [
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "R14 油价三层暴露：公司未披露燃油/电力等能源成本占比，100→130 美元的成本传导与 OCF 桥仅有情景假设，压力测试无法判定；10 月 PPI 燃料动力购进同比 +18.6% 强化该敞口而非解除。取得分矿山能源成本与传导证据前不追加。",
      "release_conditions": [
        "取得分矿山能源/燃油成本占比、传导系数及对 OCF 的量化影响",
        "按 100→130 美元情景完成压力计算并使 R14 压力结论可判定"
      ]
    },
    {
      "id": "R14-ENERGY-600988",
      "scope": [
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "lifecycle": "persistent",
      "reason": "R14：柴油、电力实质暴露存在（2025 年柴油 1.0197 亿升、外购电力 7.25 亿千瓦时），2026 量价成本金额、传导/套保及 100→130、85 美元对应现金流桥仍未知；纯 α 情景不足以判 passed；与 R14_OIL_COST_UNKNOWN 为同一规则的不同来源实例，均保留。",
      "release_conditions": [
        "取得公司分矿成本金额或有来源保守边界、传导/套保及现金流生存桥，完成 100→130 和 85 美元对称情景、按原规则裁决；未知期间不追加。"
      ]
    },
    {
      "id": "HOLD-Q3-20261024",
      "scope": [
        "holding"
      ],
      "status": "blocking",
      "action": "review_holding",
      "lifecycle": "persistent",
      "reason": "接续正式 Q3 单季归母同比 -41.84%、产销量目标下调及资本回报弱化的持仓减仓复评；11/11 收盘 39.30 元仍高于 V50 上沿 29.05 元（+35.3%），旧纯价格/PB 高分位成因已由本轮重算，但经营恢复未被正式证明，未确认核心盈利/现金流失效。",
      "release_conditions": [
        "完成持仓/成本与风险预算资料下的减仓复评并记录适用处置依据，后续正式经营数据证明恢复或重建持有论点；此为研究要求，无成交推断。"
      ]
    },
    {
      "id": "HOLDING_MARGIN_REVIEW",
      "scope": [
        "holding"
      ],
      "status": "blocking",
      "action": "review_holding",
      "lifecycle": "persistent",
      "reason": "Q3 单季盈利与 AISC 同步恶化、全年产量指引下调；11/11 收盘 39.30 元高于 V50 上沿 29.05 元，T1 处于减仓评估区间；评估减仓不等于清仓。",
      "release_conditions": [
        "下一正式报告期净利率、AISC 与产量三项同时改善并确认",
        "完成减仓评估并按新证据重新研究后另立结论"
      ]
    },
    {
      "id": "D5-REPAIR-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "lifecycle": "observation",
      "reason": "本轮为独立财报复研，未提出低位轮动新承接；D5 于 11/08 维持回退深化、R21 未退出，本公司非承接型。D5 深化状态不被本公司研究解除。",
      "release_conditions": [
        "若改作低位承接用途，须单独满足原重建三条件并逐股复评；R21 仅退出深化回等待，不恢复买入。"
      ]
    },
    {
      "id": "DEAL_INTEGRATION",
      "scope": [
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "lifecycle": "observation",
      "reason": "紫金入股 2026-10-22 完成，董事会提前换届待 2026-11-16 临时股东会；注册资本变更登记仍在办理（月报注册资本仍 1,900,411,178 元）；整合与关联交易安排未构成当前阻断，仅作观察。",
      "release_conditions": [
        "若股东会否决/延期、关联交易或同业竞争安排变化、整合后成本或产量指引调整，则升级为独立约束。"
      ]
    },
    {
      "id": "R1-CHASE-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "lifecycle": "observation",
      "reason": "R1 三项：① 公募分位/板块换手 unknown（个股换手 2.60%，1 年分位 30.4%）；② PE(TTM) 26.26、近 1 年分位 80.8% 命中，但包内 PB 5.88 分子分母时点不一致（备考 PB 3.84，分位不可比）；③ 有当季正式业绩，明确不成立。三项未合取，不构成追高否决。",
      "release_conditions": [
        "三项同时成立且处追高价位时重新评估；不以单项分位触发。"
      ]
    },
    {
      "id": "R9-DIVIDEND-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "lifecycle": "observation",
      "reason": "股息率(TTM)0.81%、商品波动及高 capex，本次不作为红利/底仓锚，不把 R9 适用对象扩大。",
      "release_conditions": [
        "若改以红利底仓逻辑研究，先齐利差/公募分位/换手三项。"
      ]
    },
    {
      "id": "EXIT-CORE-600988",
      "scope": [
        "entry",
        "add",
        "holding"
      ],
      "status": "not_applicable",
      "action": "exit_required",
      "lifecycle": "observation",
      "reason": "尚未确认核心盈利/现金流被证伪或 Terminal 不可能；观察单季盈利下滑与价格高估不能宣告清仓。",
      "release_conditions": [
        "若正式证据确认核心失效/红线/不可能，转持续退出要求并冻结新增；重建完整论点才复核。"
      ]
    },
    {
      "id": "R6-EGM-20261116",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "freeze",
      "lifecycle": "observation",
      "reason": "2026-11-16 09:00 临时股东会审议注册资本变更与董事会提前换届；会前 48 小时（11/14–16）不新增。估值日 11/12 尚未进入该窗口，且 entry/add 已由持续约束阻断，故当前不单独构成额外阻断；过窗按会议结果复核。",
      "release_conditions": [
        "会议结果公布后按议案通过/否决、董事会构成与关联交易安排复核；不以日期过去自动解除。"
      ]
    },
    {
      "id": "R6-FOMC-20261027",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "freeze",
      "lifecycle": "persistent",
      "reason": "R6 本次事件已完成公司复评：10/28 正式声明维持 3.75%–4.00%，发布会未承诺路径回撤；已读会后 CMT（11/10 10Y 4.98%、30Y 5.35%）与美元/黄金，按已确认政策重算本公司无降息及对称情景。解除本次窗口义务，不解除 D1、R17 或其它资格限制。",
      "release_conditions": [
        "本事件已按声明、发布会、市场传导及本公司情景复评解除；后续新窗口按其实质暴露重新核验。"
      ],
      "clearance": {
        "evidence": [
          "本报告 §4.2/§4.3；2026-10-28 FOMC 声明与 11/10 CMT 公开表"
        ],
        "stage": "company_review_complete"
      }
    },
    {
      "id": "R6-CPI-20261014",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "freeze",
      "lifecycle": "persistent",
      "reason": "10/14 CPI 结果已通过冻结 10/25 官方来源接续并纳入无降息与成本模型；3.7%/核心环比 0.3 仍不解除 D1；10 月 CPI 核心环比 0.3 已由 11/10 官方页复核，单个 CPI 窗口复评完成。",
      "release_conditions": [
        "先前逐股复评已完成并由冻结基线接续；新事件独立处理。"
      ],
      "clearance": {
        "evidence": [
          "冻结 10/25 macro-sources；11/10 BLS CPI 页面快照（本批共享事实包 M03）"
        ],
        "stage": "company_review_complete"
      }
    },
    {
      "id": "UST10Y-20261009-REVIEW",
      "scope": [
        "holding"
      ],
      "status": "clear",
      "action": "review_holding",
      "lifecycle": "persistent",
      "reason": "旧五日 CMT>5% 触发已由基线完成公司复评并接续；最新 11/04–11/10 为 4.90/4.84/4.86/4.88/4.98%，不满足新的连续五日>5% 条件。旧义务的解除依据是公司 R3/V5 分析完成，不是水位回落。",
      "release_conditions": [
        "本次分析完成不代表真实账户完成；有新利率跳变再复评。"
      ],
      "clearance": {
        "evidence": [
          "本报告 §5.6；美国财政部 2026-11-10 CMT 公开表"
        ],
        "stage": "company_review_complete"
      }
    },
    {
      "id": "PRICE-P1-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "eligibility",
      "lifecycle": "runtime",
      "reason": "估值日 11/11 收盘 39.30 元高于 P1 11.46 元（未到买入价格）；纯价格条件由运行时判断，不制造长期研究阻断。",
      "release_conditions": [
        "运行时对照有效 P1 与收益、账户条件。"
      ],
      "clearance": {
        "evidence": [
          "本报告 §7.1 最终 P1=11.46 元与 11/11 收盘 39.30 元"
        ],
        "stage": "runtime_owned"
      }
    },
    {
      "id": "PUBLICATION_PRICE_UNAVAILABLE",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "unavailable",
      "lifecycle": "runtime",
      "reason": "本轮已形成有效 P1/T1 并完成暂存交付，价格不可得状态解除。",
      "release_conditions": [
        "发布有效且通过验收的 P1/T1 配对。"
      ],
      "clearance": {
        "evidence": [
          "本报告 §7.1；本轮价格 JSON"
        ],
        "stage": "runtime_owned"
      }
    },
    {
      "id": "METHOD_COMPATIBILITY",
      "status": "blocking",
      "reason": "发布前方法或采纳证据接续变化，适用性待复核；保留原价格",
      "release_conditions": [
        "取得兼容性核验及本公司受影响判断复评凭证"
      ],
      "action": "freeze",
      "scope": [
        "entry",
        "add"
      ],
      "lifecycle": "persistent"
    }
  ],
  "release_all_of": {
    "entry": [
      "MARGIN_COST_QUALITY",
      "R4-EARNINGS-600988",
      "TEMP-600988",
      "METHOD_COMPATIBILITY"
    ],
    "add": [
      "MARGIN_COST_QUALITY",
      "R4-EARNINGS-600988",
      "TEMP-600988",
      "ADD-PLAN-20261007",
      "R17_PRECIOUS_METAL",
      "R17-GOLD-600988",
      "R14_OIL_COST_UNKNOWN",
      "R14-ENERGY-600988",
      "METHOD_COMPATIBILITY"
    ],
    "holding": [
      "HOLD-Q3-20261024",
      "HOLDING_MARGIN_REVIEW"
    ]
  },
  "p1_basis": {
    "base": "base"
  }
}
```
<!-- research-audit:end -->

</details>

<!-- research-acceptance-view:start -->
共享验收：R14 缺证不能判通过；各范围全部有效约束解除后才可恢复研究资格。
R14：applicable / unknown。
| R14 必要输入 | 证据状态 |
|---|---|
| exposure | supported |
| cost_exposure | unknown |
| pass_through | unknown |
| ocf_bridge | unknown |
| 恢复范围 | 必须全部解除的当前约束 |
|---|---|
| entry | MARGIN_COST_QUALITY, R4-EARNINGS-600988, TEMP-600988, METHOD_COMPATIBILITY |
| add | MARGIN_COST_QUALITY, R4-EARNINGS-600988, TEMP-600988, ADD-PLAN-20261007, R17_PRECIOUS_METAL, R17-GOLD-600988, R14_OIL_COST_UNKNOWN, R14-ENERGY-600988, METHOD_COMPATIBILITY |
| holding | HOLD-Q3-20261024, HOLDING_MARGIN_REVIEW |
规则内部合法替代路径保留；不同独立约束之间不能相互替代。运行时价格和账户条件仍须另行核验。
<!-- research-acceptance-view:end -->

<!-- research-acceptance:start -->
```json
{
  "schema_version": "stock-research-acceptance/v1",
  "r14": {
    "applicability": "applicable",
    "stress_test": "unknown",
    "constraint_ids": [
      "R14_OIL_COST_UNKNOWN",
      "R14-ENERGY-600988"
    ],
    "reason": "本公司为黄金上游资源商：油价不直接定价产品，但经①通胀→加息预期→实际利率→金价（分母端）与③柴油、电力、药剂、物流（成本端）两层暴露；②上游油气利润不适用。公司仅披露能源耗用量与单位成本，未披露能源成本金额占比或到矿价格，100→130美元的成本传导与OCF桥无法量化，压力结论记unknown并保留add持续约束。10月PPI燃料动力购进同比+18.6%强化而非解除该敞口。",
    "inputs": {
      "exposure": {
        "status": "supported",
        "sources": [
          {
            "path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/r14-dsh-5ec7298f0e26.txt",
            "sha256": "41892dae694945a496d3a3ed70e2ab7763309a04a87bb5e0562983a3590cba0a",
            "quote": "9,065.20\n974.44",
            "as_of": "2026-10-23"
          },
          {
            "path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/r14-dsh-5ec7298f0e26.txt",
            "sha256": "41892dae694945a496d3a3ed70e2ab7763309a04a87bb5e0562983a3590cba0a",
            "quote": "10,086,817,612.67",
            "as_of": "2026-10-23"
          },
          {
            "path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/r14-dsh-51764e25e01d.txt",
            "sha256": "b48089acb1dd22e2ccd5d769e5adec20aacee71a494d29ff0fb56b5c6c01dfb6",
            "quote": "柴油消耗总量\n升\n101,974,038.22",
            "as_of": "2026-03-20"
          }
        ],
        "derivation": "2026年1-9月自产金销售9,065.20千克×974.44元/克≈88.33亿元，占营业收入100.87亿元的87.6%，收入与估值对金价高度敏感；生产端2025年柴油消耗1.0197亿升、外购电力7.25亿千瓦时，能源是实际投入，故存在成本端暴露。"
      },
      "cost_exposure": {
        "status": "unknown",
        "sources": [],
        "derivation": "三季报仅披露自产金营业成本403.33元/克与AISC 494.31元/克，未拆分燃油、电力、药剂等能源项金额及其到矿价格；ESG仅披露耗用量，不能据此推导成本占比。"
      },
      "pass_through": {
        "status": "unknown",
        "sources": [],
        "derivation": "黄金为全球定价、公司为价格接受者，未见成本转嫁或套保安排的量化披露；缺少能源成本—利润弹性，不能标bounded。"
      },
      "ocf_bridge": {
        "status": "unknown",
        "sources": [],
        "derivation": "未建立100→130美元情景的OCF桥：9M OCF 31.17亿元、购建支出23.78亿元、支付税费23.31亿元(+72.3%)，能源成本上行会压缩单位毛利，但缺能源占比无法量化。"
      }
    },
    "calculation": null
  },
  "recovery": {
    "operator": "all_of",
    "scopes": {
      "entry": [
        "MARGIN_COST_QUALITY",
        "R4-EARNINGS-600988",
        "TEMP-600988",
        "METHOD_COMPATIBILITY"
      ],
      "add": [
        "MARGIN_COST_QUALITY",
        "R4-EARNINGS-600988",
        "TEMP-600988",
        "ADD-PLAN-20261007",
        "R17_PRECIOUS_METAL",
        "R17-GOLD-600988",
        "R14_OIL_COST_UNKNOWN",
        "R14-ENERGY-600988",
        "METHOD_COMPATIBILITY"
      ],
      "holding": [
        "HOLD-Q3-20261024",
        "HOLDING_MARGIN_REVIEW"
      ]
    }
  }
}
```
<!-- research-acceptance:end -->