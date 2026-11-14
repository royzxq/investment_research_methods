# 赤峰 codex 历史输入的 audit-v3 算术重演

本文件由Codex生成，codex只标明原研究来源；不是该端新研报。原经营/现金条件未被本次算术验收证明，无新正式报价。与原P1/V50/控制逐项相等；资金经济归属见同目录隔离复评。

<!-- research-checks:start -->
研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：

| 情景 | 收入 | 经常净利率 | 利润调整 | 经常归母利润 | PE | 权益调整 | 权益价值 | V50 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| low | 117 | 16.055555555555556% | 0 | 18.785 | 12 | 77.839774 | 303.259774 | 13.71 |
| base | 133.5 | 19.697044943820224% | 0 | 26.295555 | 15 | 77.839774 | 472.273099 | 21.36 |
| high | 165 | 23.973818181818182% | 0 | 39.5568 | 18 | 77.839774 | 789.862174 | 35.72 |

| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |
|---|---:|---|---|---|
| d_base | 20% | 15%—20% | MODEL_RESIDUAL | unchanged |
| r_chip | 3% | 0%—3% | CHIP_RESIDUAL | unchanged |
| r_v5 | 12% | 8%—15% | JOINT_TAIL | unchanged |
| r_gov | 0% | 0%—0% | 无额外扣减 | unchanged |
| r_terminal | 0% | 0%—0% | 无额外扣减 | unchanged |

总折扣乘数：0.68288；用途：frozen。
明确报价：P1={"base": 14.58, "high": 24.39, "low": 9.37}；T1={"price_condition": "股价≥35.72元/股"}。

| 约束 | 作用 | 状态 | 依据 |
|---|---|---|---|
| R6-FOMC-20261027 | entry,add: freeze | clear | R6本次事件已完成公司复评：10/28正式声明维持3.75%–4.00%，发布会未承诺路径回撤；已读会后黄金/美元供应商历史记录和CMT，按已确认政策及会后市场变化重算本公司无降息及对称情景。解除本次窗口义务，不解除D1、R17或其它资格限制。 |
| R4-EARNINGS-600988 | entry,add: eligibility | unknown | R4仅部分成立；正式Q3减产和单位成本上升，2027正常化恢复所需的产量、利润率与现金兑现证据未齐，不能以预测替代资格。 |
| TEMP-600988 | entry,add: eligibility | unknown | 温度代理缺失且未证明已有等价运行时属主接替，不能默认冷档。 |
| ADD-PLAN-20261007 | add: eligibility | blocking | 接续10/7取消追加的研究决定；R17、供给证据不足、产量/成本恢复和Terminal工程约束仍有未决；新两价不使旧取消自动失效。 |
| R17-GOLD-600988 | add: eligibility | unknown | R17：保留强美元+加息基准及加仓从严；黄金/ICE DXY同口径连续序列未齐，未证明撤销/降级条件。 |
| R14-ENERGY-600988 | add: eligibility | unknown | R14：柴油、电力实质暴露存在，2026量价成本金额、传导/套保及100→130、85美元对应现金流桥仍未知；纯α情景不足以判passed。 |
| HOLD-Q3-20261024 | holding: review_holding | blocking | 正式Q3单季归母同比−41.84%、量产恢复与资本回报仍未被新正式经营期证明；本轮39.30高于T1且估值分位重升，持仓继续减仓复评，未确认核心盈利/现金流失效。 |
| R6-CPI-20261014 | entry,add: freeze | clear | 10/14 CPI结果已通过冻结10/25官方来源接续并纳入无降息与成本模型；3.7%/核心环比0.3仍不解除D1，单个CPI窗口复评完成。 |
| UST10Y-20261009-REVIEW | holding: review_holding | clear | 历史五日CMT>5%事件已由冻结本端基线完成公司R3/V5复评；本轮原文11/4、5、6、9、10五值4.90/4.84/4.86/4.88/4.98%未全部>5只作新观测，不作为旧义务解除理由。 |
| D5-REPAIR-600988 | entry,add: eligibility | not_applicable | 本轮为独立财报及控制权复研，未提出低位轮动新承接；冻结基线也未将本股作为D5承接计划。D5深化状态不被本公司研究解除。 |
| R9-DIVIDEND-600988 | entry,add: eligibility | not_applicable | 股息率0.81%、商品波动及高capex；本次不作红利/底仓锚，R9不适用。分红政策不等于现金分配已发生。 |
| R1-CHASE-600988 | entry,add: eligibility | not_applicable | PE近1年80.8%与PB近3/5年90.2%/81.0%命中估值项；公募/板块换手缺失，个股2.60%不能替代；公司仍有当前销售和盈利，三项不合取。 |
| PRICE-P1-600988 | entry,add: eligibility | clear | 11/11包收盘39.30高于本轮P1，纯价格由运行时判断，不产生永久研究阻断。 |
| EXIT-CORE-600988 | entry,add,holding: exit_required | not_applicable | 尚未确认核心盈利/现金流被证伪或Terminal不可能；观察单季盈利下滑不能宣告清仓。 |
| MARGIN_COST_QUALITY | entry,add: eligibility | blocking | 接续上游稳定ID并以Q3原文核实：单季归母率18.024%低于既有研究观察线20%，9M AISC同比38.71%；纠正单季AISC错误，不推断下一期继续恶化。普通损益影响已进margin，此ID仅为恢复资格。 |
| R14_OIL_COST_UNKNOWN | add: eligibility | unknown | 接续上游R14必要缺证ID；分矿能源成本金额、传导/套保及同口径压力OCF桥仍缺，不能用正利润判通过。与R14-ENERGY同属待核主题但来源未提供合法别名映射，分别保留。 |
| R17_PRECIOUS_METAL | add: eligibility | blocking | 接续上游已触发贵金属加仓从严；固定黄金/ICE美元连续序列与正式降级复评尚未闭合，供应商反弹不解除。未证别名关系，独立保留R17-GOLD-600988。 |
| HOLDING_MARGIN_REVIEW | holding: review_holding | blocking | 接续上游利润率/成本持仓复评ID；Q3归母率18.024%、9M单位成本上涨为事实，未披露Q4不是恶化；未证与HOLD-Q3别名关系，分别保留。 |
| R6-US-CPI-20261110 | entry,add: freeze | clear | BLS于11/10发布10月CPI后，本轮按核心环比0.3%及总环比0.4%、同比缺失的真实口径完成本公司黄金/利率双情景复评；未把同比缺失当CPI<4或紧缩解除。 |
| R6-CN-PPI-20261109 | entry,add: freeze | clear | 11/9国内10月PPI购进7.9%/出厂5.7%已核；本轮完成公司能源/材料成本传导复评，保守损益成本区间继续，R14公司现金桥缺口未解除。 |
| DEAL_INTEGRATION | add: eligibility | not_applicable | 交易已完成不再使用交割未知作为限制；本模型也未计协同增利，原上游该ID不适用。资本使用实绩缺口留经营及资金观察。 |
| PUBLICATION_PRICE_UNAVAILABLE | entry,add: unavailable | clear | 上游已clear且本轮报告有可复核价格；未以历史出版缺价冒充当前核心不可估。 |
| METHOD_COMPATIBILITY | entry,add: freeze | blocking | 发布前方法或采纳证据接续变化，适用性待复核；保留原价格 |

| 范围 | 当前研究状态 | 未解约束ID |
|---|---|---|
| entry | blocked | R4-EARNINGS-600988, TEMP-600988, MARGIN_COST_QUALITY, METHOD_COMPATIBILITY |
| add | blocked | R4-EARNINGS-600988, TEMP-600988, ADD-PLAN-20261007, R17-GOLD-600988, R14-ENERGY-600988, MARGIN_COST_QUALITY, R14_OIL_COST_UNKNOWN, R17_PRECIOUS_METAL, METHOD_COMPATIBILITY |
| holding | review_required | HOLD-Q3-20261024, HOLDING_MARGIN_REVIEW |

恢复前须同时解除全部仍有效约束：{"add": ["R4-EARNINGS-600988", "TEMP-600988", "ADD-PLAN-20261007", "R17-GOLD-600988", "R14-ENERGY-600988", "MARGIN_COST_QUALITY", "R14_OIL_COST_UNKNOWN", "R17_PRECIOUS_METAL", "METHOD_COMPATIBILITY"], "entry": ["R4-EARNINGS-600988", "TEMP-600988", "MARGIN_COST_QUALITY", "METHOD_COMPATIBILITY"], "holding": ["HOLD-Q3-20261024", "HOLDING_MARGIN_REVIEW"]}。
<!-- research-checks:end -->

<details><summary>计算、风险归属与解除条件审计输入</summary>

<!-- research-audit:start -->
```json
{
  "schema_version": "stock-research-audit/v3",
  "identity": {
    "code": "600988.SH",
    "generator": "codex",
    "valuation_date": "2026-11-12",
    "currency": "CNY"
  },
  "valuation": {
    "kind": "profit_pe",
    "currency": "CNY",
    "amount_unit": "100_million",
    "shares": 2211313909,
    "fx_to_quote": 1,
    "horizon": "2027原情景固定，仅重编码；不是新的正式估值",
    "profit_basis": "保持原经常归母利润，不含新增现金利息；现金独立单列。净款为估计，K=0等条件未独立证实。",
    "scenarios": {
      "low": {
        "revenue": 117.0,
        "net_margin": 0.16055555555555556,
        "adjustments": [],
        "profit": 18.785,
        "pe": 12,
        "equity_value": 303.259774,
        "equity_adjustments": [
          {
            "id": "NET_PROCEEDS",
            "amount": 78.620274,
            "reason": "91.8亿HKD×0.85643；仅重演旧假设，非11/12银行余额证明",
            "source": "HKEX2026102201421_c.pdf PDF3；旧报告§5"
          },
          {
            "id": "COMPENSATION",
            "amount": -0.7805,
            "reason": "已批准补偿上限；与预测经常利润分开，未擅计税盾",
            "source": "HKEX2026102201506_c.pdf PDF4–5；旧报告§5"
          }
        ]
      },
      "base": {
        "revenue": 133.5,
        "net_margin": 0.19697044943820224,
        "adjustments": [],
        "profit": 26.295555,
        "pe": 15,
        "equity_value": 472.273099,
        "equity_adjustments": [
          {
            "id": "NET_PROCEEDS",
            "amount": 78.620274,
            "reason": "91.8亿HKD×0.85643；仅重演旧假设，非11/12银行余额证明",
            "source": "HKEX2026102201421_c.pdf PDF3；旧报告§5"
          },
          {
            "id": "COMPENSATION",
            "amount": -0.7805,
            "reason": "已批准补偿上限；与预测经常利润分开，未擅计税盾",
            "source": "HKEX2026102201506_c.pdf PDF4–5；旧报告§5"
          }
        ]
      },
      "high": {
        "revenue": 165.0,
        "net_margin": 0.23973818181818182,
        "adjustments": [],
        "profit": 39.5568,
        "pe": 18,
        "equity_value": 789.862174,
        "equity_adjustments": [
          {
            "id": "NET_PROCEEDS",
            "amount": 78.620274,
            "reason": "91.8亿HKD×0.85643；仅重演旧假设，非11/12银行余额证明",
            "source": "HKEX2026102201421_c.pdf PDF3；旧报告§5"
          },
          {
            "id": "COMPENSATION",
            "amount": -0.7805,
            "reason": "已批准补偿上限；与预测经常利润分开，未擅计税盾",
            "source": "HKEX2026102201506_c.pdf PDF4–5；旧报告§5"
          }
        ]
      }
    }
  },
  "baseline": {
    "report_path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/chifeng-baseline-codex.md",
    "sha256": "115069b954d20579ed1d070dc9bf10b1d13f968a0b1ba723557e7da363ad6aa5",
    "discounts": {
      "d_base": {
        "value": 0.2,
        "range": [
          0.15,
          0.2
        ],
        "quote": "最终折扣：d_base20%（原区间15%–20%）、r_chip3%（0%–3%）、r_v5 12%（8%–15%）、r_gov0（0–0）、r_terminal0（0–0）。各数值和区间绑定冻结基线原句，不重新定义上沿。普通产量损失归revenue、常态成本税费归margin、耗竭接续归multiple；安全边际只覆盖剩余模型误差、筹码只覆盖交接/ESOP交易扰动、联合尾部只覆盖模型范围外停产或被迫融资。R14/TEMP等资格缺证只归eligibility；澄清旧基线“温度未明安全边际”的文字不再对同一缺口双收费，数值不变。零治理/终局折扣不是无风险，是已由现金/利润/PE处理。"
      },
      "r_chip": {
        "value": 0.03,
        "range": [
          0,
          0.03
        ],
        "quote": "最终折扣：d_base20%（原区间15%–20%）、r_chip3%（0%–3%）、r_v5 12%（8%–15%）、r_gov0（0–0）、r_terminal0（0–0）。各数值和区间绑定冻结基线原句，不重新定义上沿。普通产量损失归revenue、常态成本税费归margin、耗竭接续归multiple；安全边际只覆盖剩余模型误差、筹码只覆盖交接/ESOP交易扰动、联合尾部只覆盖模型范围外停产或被迫融资。R14/TEMP等资格缺证只归eligibility；澄清旧基线“温度未明安全边际”的文字不再对同一缺口双收费，数值不变。零治理/终局折扣不是无风险，是已由现金/利润/PE处理。"
      },
      "r_v5": {
        "value": 0.12,
        "range": [
          0.08,
          0.15
        ],
        "quote": "最终折扣：d_base20%（原区间15%–20%）、r_chip3%（0%–3%）、r_v5 12%（8%–15%）、r_gov0（0–0）、r_terminal0（0–0）。各数值和区间绑定冻结基线原句，不重新定义上沿。普通产量损失归revenue、常态成本税费归margin、耗竭接续归multiple；安全边际只覆盖剩余模型误差、筹码只覆盖交接/ESOP交易扰动、联合尾部只覆盖模型范围外停产或被迫融资。R14/TEMP等资格缺证只归eligibility；澄清旧基线“温度未明安全边际”的文字不再对同一缺口双收费，数值不变。零治理/终局折扣不是无风险，是已由现金/利润/PE处理。"
      },
      "r_gov": {
        "value": 0,
        "range": [
          0,
          0
        ],
        "quote": "最终折扣：d_base20%（原区间15%–20%）、r_chip3%（0%–3%）、r_v5 12%（8%–15%）、r_gov0（0–0）、r_terminal0（0–0）。各数值和区间绑定冻结基线原句，不重新定义上沿。普通产量损失归revenue、常态成本税费归margin、耗竭接续归multiple；安全边际只覆盖剩余模型误差、筹码只覆盖交接/ESOP交易扰动、联合尾部只覆盖模型范围外停产或被迫融资。R14/TEMP等资格缺证只归eligibility；澄清旧基线“温度未明安全边际”的文字不再对同一缺口双收费，数值不变。零治理/终局折扣不是无风险，是已由现金/利润/PE处理。"
      },
      "r_terminal": {
        "value": 0,
        "range": [
          0,
          0
        ],
        "quote": "最终折扣：d_base20%（原区间15%–20%）、r_chip3%（0%–3%）、r_v5 12%（8%–15%）、r_gov0（0–0）、r_terminal0（0–0）。各数值和区间绑定冻结基线原句，不重新定义上沿。普通产量损失归revenue、常态成本税费归margin、耗竭接续归multiple；安全边际只覆盖剩余模型误差、筹码只覆盖交接/ESOP交易扰动、联合尾部只覆盖模型范围外停产或被迫融资。R14/TEMP等资格缺证只归eligibility；澄清旧基线“温度未明安全边际”的文字不再对同一缺口双收费，数值不变。零治理/终局折扣不是无风险，是已由现金/利润/PE处理。"
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
        "MODEL_RESIDUAL"
      ],
      "reason": "20%、15%–20%沿用；覆盖正常化模型估计误差，不对已识别产量/成本损失重复扣减，温度必要缺证仅归资格。",
      "change": {
        "kind": "unchanged",
        "reason": "沿用2026-11-03冻结本端数值与论证区间；新核事实未证明残余风险解除，不重新定义上沿。",
        "evidence": []
      }
    },
    "r_chip": {
      "value": 0.03,
      "range": [
        0,
        0.03
      ],
      "risk_ids": [
        "CHIP_RESIDUAL"
      ],
      "reason": "沿用3%与0%–3%区间；交割不确定已解除，但ESOP尚列1518.26万股、换届过渡期的残余筹码扰动仍未闭合。公募分位缺失只留拥挤未知，不单独扣价或造永久阻断。",
      "change": {
        "kind": "unchanged",
        "reason": "沿用2026-11-03冻结本端数值与论证区间；新核事实未证明残余风险解除，不重新定义上沿。",
        "evidence": []
      }
    },
    "r_v5": {
      "value": 0.12,
      "range": [
        0.08,
        0.15
      ],
      "risk_ids": [
        "JOINT_TAIL"
      ],
      "reason": "沿用12%与8%–15%区间及R17从8%上调一档的历史论证；保留金价与矿山现金需求同时恶化的联合尾部，仅覆盖正常利润与PE未刻画的停产/被迫融资。",
      "change": {
        "kind": "unchanged",
        "reason": "沿用2026-11-03冻结本端数值与论证区间；新核事实未证明残余风险解除，不重新定义上沿。",
        "evidence": []
      }
    },
    "r_gov": {
      "value": 0,
      "range": [
        0,
        0
      ],
      "risk_ids": [],
      "reason": "沿用0；已知税费进利润，已批准离任补偿进现金桥。未确认治理红线，不因缺资料再罚。",
      "change": {
        "kind": "unchanged",
        "reason": "沿用2026-11-03冻结本端数值与论证区间；新核事实未证明残余风险解除，不重新定义上沿。",
        "evidence": []
      }
    },
    "r_terminal": {
      "value": 0,
      "range": [
        0,
        0
      ],
      "risk_ids": [],
      "reason": "沿用0；资源接续与SND未兑现已进入核心12/15/18倍PE及不计项目利润，不再重复扣减。",
      "change": {
        "kind": "unchanged",
        "reason": "沿用2026-11-03冻结本端数值与论证区间；新核事实未证明残余风险解除，不重新定义上沿。",
        "evidence": []
      }
    }
  },
  "risks": [
    {
      "id": "MODEL_RESIDUAL",
      "description": "正常化模型的剩余估计误差与安全边际",
      "owner": "d_base",
      "scope": "不含已识别产量、成本、储量接续损失或温度资格缺口；旧表述澄清，不改变折扣。",
      "source": "基线§7；本报告§2/§5"
    },
    {
      "id": "CHIP_RESIDUAL",
      "description": "ESOP处置与控制权交接期残余流动性波动",
      "owner": "r_chip",
      "scope": "只计经营利润/现金补偿外的市场交易扰动；不再计已完成协议转让",
      "source": "Q3正文p4；10/22董事会公告；基线§7"
    },
    {
      "id": "JOINT_TAIL",
      "description": "黄金售价及生产现金需求共同不利导致被迫融资的非线性尾部",
      "owner": "r_v5",
      "scope": "正常化成本税费已入margin，PE矿山耗竭已入multiple；此处只含超出模型幅度的联合尾部；不对R14缺证收费",
      "source": "Q3正文p6–7；基线V5/R17"
    },
    {
      "id": "OUTPUT_RESET",
      "description": "技改检修和安全自查导致产销恢复不足",
      "owner": "revenue",
      "scope": "12/13/14.7吨收入情景吸收",
      "source": "Q3正文p6–7"
    },
    {
      "id": "COST_TAX",
      "description": "常态单位成本及阶梯资源税",
      "owner": "margin",
      "scope": "430/420/400元、税金7.5/7.5/8%、所得税与少数股东吸收",
      "source": "Q3正文p6–7、10–11"
    },
    {
      "id": "MINE_LIFE",
      "description": "矿山有限寿命与资源转储量/扩产未兑现",
      "owner": "multiple",
      "scope": "经营PE12/15/18吸收，不再r_terminal",
      "source": "基线§5–6及2025年报原始来源"
    },
    {
      "id": "RESEARCH_EVIDENCE",
      "description": "事件、R14、R17、温度与盈利恢复的资格缺证",
      "owner": "eligibility",
      "scope": "只按scope限制研究资格，不虚构数值折价",
      "source": "本报告§4/§7"
    }
  ],
  "constraints": [
    {
      "id": "R6-FOMC-20261027",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "freeze",
      "reason": "R6本次事件已完成公司复评：10/28正式声明维持3.75%–4.00%，发布会未承诺路径回撤；已读会后黄金/美元供应商历史记录和CMT，按已确认政策及会后市场变化重算本公司无降息及对称情景。解除本次窗口义务，不解除D1、R17或其它资格限制。",
      "release_conditions": [
        "本事件已按声明、发布会、市场传导及本公司情景复评解除；后续新窗口按其实质暴露重新核验。"
      ],
      "lifecycle": "persistent",
      "clearance": {
        "stage": "company_review_complete",
        "covers": [
          "7afc3658fcdf86a307bf13ba0f45f9c87316d6d846df81dfd3e0aa863400b51f"
        ],
        "evidence": [
          "output/runs/investment/2026-11-03/c09461267e264fbf874a7b280931d1ec/execution/SH-600988/codex/agent/macro/raw/fed_transcript.pdf：PDF第2、6、13–16页；output/runs/investment/2026-11-03/c09461267e264fbf874a7b280931d1ec/execution/SH-600988/codex/agent/macro/excerpts/fed_transcript.txt",
          "output/runs/investment/2026-11-03/c09461267e264fbf874a7b280931d1ec/execution/SH-600988/codex/agent/macro/raw/fed_statement.html：2026-10-28正式政策决定；output/runs/investment/2026-11-03/c09461267e264fbf874a7b280931d1ec/execution/SH-600988/codex/agent/macro/excerpts/fed_statement.txt",
          "output/runs/investment/2026-11-03/c09461267e264fbf874a7b280931d1ec/execution/SH-600988/codex/agent/macro/excerpts/market-web-read.txt：10/23–10/30供应商黄金与美元历史表；冻结maintenance 11/1 source-ledger及calculations的10/26–30 CMT；本报告§4/§5的实际传导与公司双情景复评。"
        ]
      }
    },
    {
      "id": "R4-EARNINGS-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "reason": "R4仅部分成立；正式Q3减产和单位成本上升，2027正常化恢复所需的产量、利润率与现金兑现证据未齐，不能以预测替代资格。",
      "release_conditions": [
        "正式经营更新或财报证明产量恢复、成本可控、利润/现金兑现与持续销货可见度；按同口径重算并完成逐股买入资格复核。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "TEMP-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "reason": "温度代理缺失且未证明已有等价运行时属主接替，不能默认冷档。",
      "release_conditions": [
        "取得估值截止兼容的China-MM/50ETF波指与沪深300温度及相应cap评估，或明确绑定合法等价运行时接替并逐项核验。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "ADD-PLAN-20261007",
      "scope": [
        "add"
      ],
      "status": "blocking",
      "action": "eligibility",
      "reason": "接续10/7取消追加的研究决定；R17、供给证据不足、产量/成本恢复和Terminal工程约束仍有未决；新两价不使旧取消自动失效。",
      "release_conditions": [
        "重新研究本轮追加计划：产销、成本及现金兑现改善且Terminal工程证据足够，R17/R14适用资格复核完成；仍须解除add范围其余全部限制。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R17-GOLD-600988",
      "scope": [
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "reason": "R17：保留强美元+加息基准及加仓从严；黄金/ICE DXY同口径连续序列未齐，未证明撤销/降级条件。",
      "release_conditions": [
        "依D3原合法路径核验黄金收复4500的撤销复核，或连续两周黄金收于4300上且美元100上方的降级复核；逐股评估加仓，不凭单日反弹恢复。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R14-ENERGY-600988",
      "scope": [
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "reason": "R14：柴油、电力实质暴露存在，2026量价成本金额、传导/套保及100→130、85美元对应现金流桥仍未知；纯α情景不足以判passed。",
      "release_conditions": [
        "取得公司分矿成本金额或有来源保守边界、传导/套保及现金流生存桥，完成100→130和85美元对称情景、按原规则裁决；未知期间不追加。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "HOLD-Q3-20261024",
      "scope": [
        "holding"
      ],
      "status": "blocking",
      "action": "review_holding",
      "reason": "正式Q3单季归母同比−41.84%、量产恢复与资本回报仍未被新正式经营期证明；本轮39.30高于T1且估值分位重升，持仓继续减仓复评，未确认核心盈利/现金流失效。",
      "release_conditions": [
        "完成持仓/成本与风险预算资料下的减仓复评并记录适用处置依据，后续正式经营数据证明恢复或重建持有论点；此为研究要求，无成交推断。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R6-CPI-20261014",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "freeze",
      "reason": "10/14 CPI结果已通过冻结10/25官方来源接续并纳入无降息与成本模型；3.7%/核心环比0.3仍不解除D1，单个CPI窗口复评完成。",
      "release_conditions": [
        "先前逐股复评已完成并由冻结基线接续；新事件独立处理。"
      ],
      "lifecycle": "persistent",
      "clearance": {
        "evidence": [
          "冻结macro-sources.md M1–M4；本报告§4–5无降息模型及Q3成本现金核验"
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
      "reason": "历史五日CMT>5%事件已由冻结本端基线完成公司R3/V5复评；本轮原文11/4、5、6、9、10五值4.90/4.84/4.86/4.88/4.98%未全部>5只作新观测，不作为旧义务解除理由。",
      "release_conditions": [
        "本次分析完成不代表真实账户完成；有新利率跳变再复评。"
      ],
      "lifecycle": "persistent",
      "clearance": {
        "evidence": [
          "冻结10/11 market-research历史触发与10/25 macro-sources逐日行；本报告§5基准/对称/压力及现金桥"
        ],
        "stage": "company_review_complete"
      }
    },
    {
      "id": "D5-REPAIR-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "reason": "本轮为独立财报及控制权复研，未提出低位轮动新承接；冻结基线也未将本股作为D5承接计划。D5深化状态不被本公司研究解除。",
      "release_conditions": [
        "若改作低位承接用途，须单独满足原重建三条件并逐股复评；R21仅退出深化回等待，不恢复买入。"
      ],
      "lifecycle": "observation"
    },
    {
      "id": "R9-DIVIDEND-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "reason": "股息率0.81%、商品波动及高capex；本次不作红利/底仓锚，R9不适用。分红政策不等于现金分配已发生。",
      "release_conditions": [
        "若改以红利底仓逻辑研究，先齐利差/公募分位/换手三项。"
      ],
      "lifecycle": "observation"
    },
    {
      "id": "R1-CHASE-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "reason": "PE近1年80.8%与PB近3/5年90.2%/81.0%命中估值项；公募/板块换手缺失，个股2.60%不能替代；公司仍有当前销售和盈利，三项不合取。",
      "release_conditions": [
        "仅完整三项及追高条件证实后按原规则重评；现价/P1属运行时。"
      ],
      "lifecycle": "observation"
    },
    {
      "id": "PRICE-P1-600988",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "eligibility",
      "reason": "11/11包收盘39.30高于本轮P1，纯价格由运行时判断，不产生永久研究阻断。",
      "release_conditions": [
        "运行时对照有效P1与收益、账户条件。"
      ],
      "lifecycle": "runtime",
      "clearance": {
        "evidence": [
          "本报告§7本轮P1与11/11包内收盘39.30；原冻结基线已明确runtime接替。"
        ],
        "stage": "runtime_owned"
      }
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
      "reason": "尚未确认核心盈利/现金流被证伪或Terminal不可能；观察单季盈利下滑不能宣告清仓。",
      "release_conditions": [
        "若正式证据确认核心失效/红线/不可能，转持续退出要求并冻结新增；重建完整论点才复核。"
      ],
      "lifecycle": "observation"
    },
    {
      "id": "MARGIN_COST_QUALITY",
      "scope": [
        "entry",
        "add"
      ],
      "status": "blocking",
      "action": "eligibility",
      "reason": "接续上游稳定ID并以Q3原文核实：单季归母率18.024%低于既有研究观察线20%，9M AISC同比38.71%；纠正单季AISC错误，不推断下一期继续恶化。普通损益影响已进margin，此ID仅为恢复资格。",
      "release_conditions": [
        "取得下一正式可比期间产量/归母净利率/单位成本及现金流，证明20%观察线对应的利润率恢复、成本同比上行原因消退或以原文足够重建盈利论点，完成资格复评；其它独立约束仍须全部解除。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R14_OIL_COST_UNKNOWN",
      "scope": [
        "add"
      ],
      "status": "unknown",
      "action": "eligibility",
      "reason": "接续上游R14必要缺证ID；分矿能源成本金额、传导/套保及同口径压力OCF桥仍缺，不能用正利润判通过。与R14-ENERGY同属待核主题但来源未提供合法别名映射，分别保留。",
      "release_conditions": [
        "以公司原文或有来源保守边界齐备能源暴露金额、传导和现金流生存桥，按100→130及85美元对称场景复评，并核全部原主张后解除。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R17_PRECIOUS_METAL",
      "scope": [
        "add"
      ],
      "status": "blocking",
      "action": "eligibility",
      "reason": "接续上游已触发贵金属加仓从严；固定黄金/ICE美元连续序列与正式降级复评尚未闭合，供应商反弹不解除。未证别名关系，独立保留R17-GOLD-600988。",
      "release_conditions": [
        "按D3黄金4500撤销复核或连续两周4300以上且美元100以上的合法降级路径取得同口径证据，完成本公司强美元双情景及加仓复评；触发只生成复评，不能跳过其它限制。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "HOLDING_MARGIN_REVIEW",
      "scope": [
        "holding"
      ],
      "status": "blocking",
      "action": "review_holding",
      "reason": "接续上游利润率/成本持仓复评ID；Q3归母率18.024%、9M单位成本上涨为事实，未披露Q4不是恶化；未证与HOLD-Q3别名关系，分别保留。",
      "release_conditions": [
        "以正式新经营期核产量、同口径成本和归母盈利趋势，完成适用持仓风险预算下的减仓/继续持有论证闭合；复评并非成交或已失效。"
      ],
      "lifecycle": "persistent"
    },
    {
      "id": "R6-US-CPI-20261110",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "freeze",
      "reason": "BLS于11/10发布10月CPI后，本轮按核心环比0.3%及总环比0.4%、同比缺失的真实口径完成本公司黄金/利率双情景复评；未把同比缺失当CPI<4或紧缩解除。",
      "release_conditions": [
        "本次特定事件已按原文与§4/5公司传导完成事后复评；未来新窗口独立判。"
      ],
      "lifecycle": "persistent",
      "clearance": {
        "stage": "company_review_complete",
        "evidence": [
          "本轮macro BLS10月CPI原文及本报告§4/5双情景，保留D1/R17与同比缺口。"
        ]
      }
    },
    {
      "id": "R6-CN-PPI-20261109",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "freeze",
      "reason": "11/9国内10月PPI购进7.9%/出厂5.7%已核；本轮完成公司能源/材料成本传导复评，保守损益成本区间继续，R14公司现金桥缺口未解除。",
      "release_conditions": [
        "本次价格数据窗口复评完成；未来新窗口与公司新增成本证据独立复核。"
      ],
      "lifecycle": "persistent",
      "clearance": {
        "stage": "company_review_complete",
        "evidence": [
          "本轮macro国家统计局11/9 PPI原文；本报告§4/5利润成本敏感性及未通过的R14证据验收。"
        ]
      }
    },
    {
      "id": "DEAL_INTEGRATION",
      "scope": [
        "add"
      ],
      "status": "not_applicable",
      "action": "eligibility",
      "reason": "交易已完成不再使用交割未知作为限制；本模型也未计协同增利，原上游该ID不适用。资本使用实绩缺口留经营及资金观察。",
      "release_conditions": [
        "若依赖新协同/新收购增利，须重新验证交割、投入和归母回报。"
      ],
      "lifecycle": "observation"
    },
    {
      "id": "PUBLICATION_PRICE_UNAVAILABLE",
      "scope": [
        "entry",
        "add"
      ],
      "status": "clear",
      "action": "unavailable",
      "reason": "上游已clear且本轮报告有可复核价格；未以历史出版缺价冒充当前核心不可估。",
      "release_conditions": [
        "本轮报价仍需runner完整验收，结构检查不代替经济论证。"
      ],
      "lifecycle": "runtime",
      "clearance": {
        "evidence": [
          "本报告§5/7明确模型与唯一P1/T1；本批构建及回读文件。"
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
      "R4-EARNINGS-600988",
      "TEMP-600988",
      "MARGIN_COST_QUALITY",
      "METHOD_COMPATIBILITY"
    ],
    "add": [
      "R4-EARNINGS-600988",
      "TEMP-600988",
      "ADD-PLAN-20261007",
      "R17-GOLD-600988",
      "R14-ENERGY-600988",
      "MARGIN_COST_QUALITY",
      "R14_OIL_COST_UNKNOWN",
      "R17_PRECIOUS_METAL",
      "METHOD_COMPATIBILITY"
    ],
    "holding": [
      "HOLD-Q3-20261024",
      "HOLDING_MARGIN_REVIEW"
    ]
  },
  "p1_basis": {
    "low": "low",
    "base": "base",
    "high": "high"
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
| entry | R4-EARNINGS-600988, TEMP-600988, MARGIN_COST_QUALITY, METHOD_COMPATIBILITY |
| add | R4-EARNINGS-600988, TEMP-600988, ADD-PLAN-20261007, R17-GOLD-600988, R14-ENERGY-600988, MARGIN_COST_QUALITY, R14_OIL_COST_UNKNOWN, R17_PRECIOUS_METAL, METHOD_COMPATIBILITY |
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
      "R14-ENERGY-600988",
      "R14_OIL_COST_UNKNOWN"
    ],
    "reason": "R14柴油、电力直接成本与通胀分母暴露存在；2025实物投入不能替代2026采购金额/传导/套保和现金流生存桥。未知不等于通过，也未证实油涨30%使OCF转负且无对冲。",
    "inputs": {
      "exposure": {
        "status": "supported",
        "sources": [
          {
            "path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/r14-codex-4c1efaf91a1a.txt",
            "sha256": "f82c123aaa17c89352835a0782640914b105e0ac98aece92b2ed5069f273065e",
            "quote": "101,974,038.22",
            "as_of": "2026-03-20"
          }
        ],
        "derivation": "2025ESG PDF92/印刷177–178脚注17为境内外合计，柴油1.01974亿升、外购电7.25260亿kWh证明直接能源暴露。原PDF保留于financial/originals/2025ESG.pdf及共享sources。"
      },
      "cost_exposure": {
        "status": "unknown",
        "sources": [
          {
            "path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/r14-codex-4c1efaf91a1a.txt",
            "sha256": "f82c123aaa17c89352835a0782640914b105e0ac98aece92b2ed5069f273065e",
            "quote": "101,974,038.22",
            "as_of": "2026-03-20"
          }
        ],
        "derivation": "只有2025用量；2026分矿用量、柴油采购单价和能源现金成本金额缺失，不以任意比例乘AISC。"
      },
      "pass_through": {
        "status": "unknown",
        "sources": [],
        "derivation": "未取得2026采购传导、套保或可约束区间；国际金价变动不证明成本足额转嫁。"
      },
      "ocf_bridge": {
        "status": "unknown",
        "sources": [
          {
            "path": "research/investment/studies/risk-capital-audit/2026-11-14/evidence/r14-codex-86d5ef8c7eff.txt",
            "sha256": "0d9513bfb360c0852044e7ca1e5de5462f1a5e4ddcfdab781753275c5701d37e",
            "quote": "3,116,535,861.77",
            "as_of": "2026-10-23"
          }
        ],
        "derivation": "Q3报告历史9M OCF31.1654亿元是合并实际值，不是油价情景预测；未来营运资本、维持/增长投资、税盾和归母融资承接未齐。§5.4纯情景计算不视为有依据生存桥。"
      }
    },
    "calculation": null
  },
  "recovery": {
    "operator": "all_of",
    "scopes": {
      "entry": [
        "R4-EARNINGS-600988",
        "TEMP-600988",
        "MARGIN_COST_QUALITY",
        "METHOD_COMPATIBILITY"
      ],
      "add": [
        "R4-EARNINGS-600988",
        "TEMP-600988",
        "ADD-PLAN-20261007",
        "R17-GOLD-600988",
        "R14-ENERGY-600988",
        "MARGIN_COST_QUALITY",
        "R14_OIL_COST_UNKNOWN",
        "R17_PRECIOUS_METAL",
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