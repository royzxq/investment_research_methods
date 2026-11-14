# 隔离算术审计，不是正式投研交付

保留旧折扣作控制变量，算术通过不证明折扣经济独立；未运行完整Gate/来源验收，不可发布。

<!-- research-checks:start -->
研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：

| 情景 | 收入 | 经常净利率 | 利润调整 | 经常归母利润 | PE | 权益价值 | V50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| low | 10500 | 3.5% | 0 | 367.50000000000006 | 12 | 4410.000000000001 | 25.888 |
| base | 11500 | 5% | 0 | 575 | 15 | 8625 | 50.631 |
| high | 12500 | 6.5% | 0 | 812.5 | 18 | 14625 | 85.853 |

| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |
|---|---:|---|---|---|
| d_base | 25% | 25%—25% | d_base | initial |
| r_chip | 0% | 0%—0% | 无额外扣减 | initial |
| r_v5 | 0% | 0%—0% | 无额外扣减 | initial |
| r_gov | 0% | 0%—0% | 无额外扣减 | initial |
| r_terminal | 0% | 0%—0% | 无额外扣减 | initial |

总折扣乘数：0.75；用途：tracking。
明确报价：P1={"base": 37.974}；T1={"price_condition": "接近V50上沿时复核"}。

| 约束 | 作用 | 状态 | 依据 |
|---|---|---|---|
| CAPITAL_UNRESOLVED | entry,add: eligibility | unknown | 现金与投资净归属缺口；隔离实验无正式资格裁决 |
| HOLDING_NOT_REASSESSED | holding: review_holding | unknown | 隔离估值实验未形成新的持仓判断 |

| 范围 | 当前研究状态 | 未解约束ID |
|---|---|---|
| entry | unknown | CAPITAL_UNRESOLVED |
| add | unknown | CAPITAL_UNRESOLVED |
| holding | unknown | HOLDING_NOT_REASSESSED |

恢复前须同时解除全部仍有效约束：{"add": ["CAPITAL_UNRESOLVED"], "entry": ["CAPITAL_UNRESOLVED"], "holding": ["HOLDING_NOT_REASSESSED"]}。
<!-- research-checks:end -->

<details><summary>计算、风险归属与解除条件审计输入</summary>

<!-- research-audit:start -->
```json
{
  "schema_version": "stock-research-audit/v2",
  "identity": {
    "code": "09988.HK",
    "generator": "codex",
    "valuation_date": "2026-10-31",
    "currency": "HKD"
  },
  "valuation": {
    "kind": "profit_pe",
    "currency": "CNY",
    "amount_unit": "100_million",
    "shares": 19901959514,
    "fx_to_quote": 1.1683061896861928,
    "horizon": "same 2026-10-31 forward ordinary profit",
    "profit_basis": "legacy normalized ordinary earnings includes finance/investment returns",
    "scenarios": {
      "low": {
        "revenue": 10500,
        "net_margin": 0.035,
        "adjustments": [],
        "profit": 367.50000000000006,
        "pe": 12,
        "equity_value": 4410.000000000001
      },
      "base": {
        "revenue": 11500,
        "net_margin": 0.05,
        "adjustments": [],
        "profit": 575.0,
        "pe": 15,
        "equity_value": 8625.0
      },
      "high": {
        "revenue": 12500,
        "net_margin": 0.065,
        "adjustments": [],
        "profit": 812.5,
        "pe": 18,
        "equity_value": 14625.0
      }
    }
  },
  "baseline": null,
  "discounts": {
    "d_base": {
      "value": 0.25,
      "range": [
        0.25,
        0.25
      ],
      "risk_ids": [
        "d_base"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_chip": {
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_v5": {
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_gov": {
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_terminal": {
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    }
  },
  "risks": [
    {
      "id": "d_base",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "d_base",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    }
  ],
  "constraints": [
    {
      "id": "CAPITAL_UNRESOLVED",
      "scope": [
        "entry",
        "add"
      ],
      "action": "eligibility",
      "status": "unknown",
      "lifecycle": "persistent",
      "reason": "现金与投资净归属缺口；隔离实验无正式资格裁决",
      "release_conditions": [
        "核实资本桥并完整复评"
      ]
    },
    {
      "id": "HOLDING_NOT_REASSESSED",
      "scope": [
        "holding"
      ],
      "action": "review_holding",
      "status": "unknown",
      "lifecycle": "persistent",
      "reason": "隔离估值实验未形成新的持仓判断",
      "release_conditions": [
        "完成持仓逻辑复评"
      ]
    }
  ],
  "release_all_of": {
    "entry": [
      "CAPITAL_UNRESOLVED"
    ],
    "add": [
      "CAPITAL_UNRESOLVED"
    ],
    "holding": [
      "HOLDING_NOT_REASSESSED"
    ]
  },
  "p1_basis": {
    "base": "base"
  }
}
```
<!-- research-audit:end -->

</details>
