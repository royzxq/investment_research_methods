# 隔离算术审计，不是正式投研交付

保留旧折扣作控制变量，算术通过不证明折扣经济独立；未运行完整Gate/来源验收，不可发布。

<!-- research-checks:start -->
研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：

估值链适用性：other；legacy EV/NOPAT capitalization /1.10 plus raw capital bridge; original arithmetic in inputs, not FCFF

| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |
|---|---:|---|---|---|
| d_base | 30% | 30%—30% | d_base | initial |
| r_chip | 3% | 3%—3% | r_chip | initial |
| r_v5 | 10% | 10%—10% | r_v5 | initial |
| r_gov | 3% | 3%—3% | r_gov | initial |
| r_terminal | 8% | 8%—8% | r_terminal | initial |

总折扣乘数：0.54534564；用途：tracking。
明确报价：P1={"base": 9.261}；T1={"price_condition": "接近V50上沿时复核"}。

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
    "code": "01810.HK",
    "generator": "codex",
    "valuation_date": "2026-10-31",
    "currency": "HKD"
  },
  "valuation": {
    "kind": "other",
    "reason": "legacy EV/NOPAT capitalization /1.10 plus raw capital bridge; original arithmetic in inputs, not FCFF",
    "unrounded_v50": {
      "low": 9.991057866424894,
      "base": 16.982222667423745,
      "high": 26.501405835803805
    }
  },
  "baseline": null,
  "discounts": {
    "d_base": {
      "value": 0.3,
      "range": [
        0.3,
        0.3
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
      "value": 0.03,
      "range": [
        0.03,
        0.03
      ],
      "risk_ids": [
        "r_chip"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_v5": {
      "value": 0.1,
      "range": [
        0.1,
        0.1
      ],
      "risk_ids": [
        "r_v5"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_gov": {
      "value": 0.03,
      "range": [
        0.03,
        0.03
      ],
      "risk_ids": [
        "r_gov"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_terminal": {
      "value": 0.08,
      "range": [
        0.08,
        0.08
      ],
      "risk_ids": [
        "r_terminal"
      ],
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
    },
    {
      "id": "r_chip",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_chip",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    },
    {
      "id": "r_v5",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_v5",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    },
    {
      "id": "r_gov",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_gov",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    },
    {
      "id": "r_terminal",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_terminal",
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
