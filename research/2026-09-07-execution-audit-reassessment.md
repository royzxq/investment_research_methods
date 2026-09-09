# 2026-09-07 Report A 方法重评（2026-09-09编制）

这是一份用现有9/7材料检查新方法的重评记录，覆盖不完整，不是9/7历史实际决策，也不是9/9交易方案。暂不新开；真实账户未知，final_lots=null。没有计算完整风险，不能把本期结果归因于5,000元上限。

MA旧对通过分位筛选，但按报告所用库存假设存在反证。单日收窄41与近5日走阔134同时保留；确认定义未冻结，所以signal=unknown。#5的产业反证与确认定义缺项分开，不将地缘专业出口缺项自动列入国内路线。国内独立逻辑仍须论证，未因此授予许可。

MA/RB新对属于“已有路线尚未计算”，记temporary_gap。原报告中“三日/40元/两周”没有事前依据，本重评没有把它们升级为硬规则。无足够原始路径和独立国内支持时，不编造Entry/SL/TP或影子收益。

证据日期为9/7及之前；quality=verified仅说明本地输出/公开转引可查，不证明源数据真实无误。库存来源按金联创公开转引更正；报告中的全部地缘新闻、交易所公告及实际账户并未在本重评中逐一核实。

金额配置：常规3.5%；低敞口min(净值×3.5%,5000元)。原先“风险状态low_exposure”作为报告背景留存，当前所有生效触发仍需完整执行核验。

```json
{
  "audit_schema_version": 2,
  "as_of_date": "2026-09-07",
  "research_mode": "public_data",
  "assessment_scope": "retrospective_method_reassessment_not_historical_execution",
  "framework": {
    "path": "framework/futures_framework.md",
    "version": "v2.23",
    "revision": "v2.23-2026-09-09-working-tree"
  },
  "snapshot": {
    "market_trade_date": "2026-09-07",
    "market_captured_at": null,
    "source_artifacts": [
      "1.txt"
    ],
    "account": {
      "actual_position_status": "unknown",
      "verified_at": null,
      "evidence": null,
      "equity": null,
      "open_positions": null,
      "pending_orders": null,
      "existing_risk": null,
      "reserved_order_risk": null,
      "margin_available": null,
      "configured_equity": 150000
    }
  },
  "coverage": {
    "completeness": "partial",
    "covered_scope": [
      "MA2610-MA2701 A国内回归研究",
      "RB2610-RB2701 A筛选",
      "SR2701-SR2705 A筛选"
    ],
    "missing_scope": [
      "MA2701-MA2705新对取样",
      "RB2701-RB2703新对取样",
      "CF具体模型证据",
      "适用执行门与真实账户"
    ],
    "research_only_scope": [
      "M无已许可具体策略",
      "geopolitical_fade必要专业证据不可持续取得"
    ],
    "total_executable_opportunities": null,
    "historical_trade_performance": "unavailable",
    "signal_only_scope": [
      "AU",
      "SC"
    ]
  },
  "evidence": [
    {
      "evidence_id": "ma_pct",
      "metric": "MA2610-MA2701同期分位",
      "value": 100,
      "unit": "percentile",
      "observation_date": "2026-09-07",
      "published_at": "2026-09-07",
      "source_url_or_file": "1.txt",
      "original_source": "用户已有脚本v1.10输出，未重拉API",
      "price_basis": "settle",
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_spread",
      "metric": "MA2610-MA2701绝对价差",
      "value": 272,
      "unit": "CNY/tonne",
      "observation_date": "2026-09-07",
      "published_at": "2026-09-07",
      "source_url_or_file": "1.txt",
      "original_source": "用户已有脚本v1.10输出，未重拉API",
      "price_basis": "settle",
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_change_1td",
      "metric": "MA2610-MA2701近1交易日变化",
      "value": -41,
      "unit": "CNY/tonne",
      "observation_date": "2026-09-07",
      "published_at": "2026-09-07",
      "source_url_or_file": "1.txt",
      "original_source": "2026-09-04至2026-09-07同对变化",
      "price_basis": "settle",
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_change_5td",
      "metric": "MA2610-MA2701近5交易日变化",
      "value": 134,
      "unit": "CNY/tonne",
      "observation_date": "2026-09-07",
      "published_at": "2026-09-07",
      "source_url_or_file": "1.txt",
      "original_source": "2026-08-31至2026-09-07同对变化",
      "price_basis": "settle",
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_inventory",
      "metric": "华东甲醇社会库存，不含华东下游工厂",
      "value": 34.47,
      "unit": "万吨",
      "observation_date": "2026-09-03",
      "published_at": "2026-09-04",
      "source_url_or_file": "https://qhweb.eastmoney.com/news/202609043865239986.html",
      "original_source": "金联创，东方财富公开转引，未核付费原库",
      "price_basis": null,
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "ma_inventory_change",
      "metric": "同口径华东甲醇社会库存周变化",
      "value": -3.68,
      "unit": "万吨",
      "observation_date": "2026-09-03",
      "published_at": "2026-09-04",
      "source_url_or_file": "https://qhweb.eastmoney.com/news/202609043865239986.html",
      "original_source": "金联创，东方财富公开转引，未核付费原库",
      "price_basis": null,
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "rb_pct",
      "metric": "RB2610-RB2701同期分位",
      "value": 61.5,
      "unit": "percentile",
      "observation_date": "2026-09-07",
      "published_at": "2026-09-07",
      "source_url_or_file": "1.txt",
      "original_source": "用户已有脚本v1.10输出，未重拉API",
      "price_basis": "settle",
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    },
    {
      "evidence_id": "sr_pct",
      "metric": "SR2701-SR2705同期分位",
      "value": 0,
      "unit": "percentile",
      "observation_date": "2026-09-07",
      "published_at": "2026-09-07",
      "source_url_or_file": "1.txt",
      "original_source": "用户已有脚本v1.10输出，未重拉API",
      "price_basis": "settle",
      "comparison_basis": "所列具体合约对/原文样本口径",
      "role": "required_model",
      "quality": "verified",
      "time_scope": "current"
    }
  ],
  "candidates": [
    {
      "candidate_id": "MA_A_2610_2701",
      "opportunity_id": "MA_A_2610_2701",
      "trade_date": "2026-09-08",
      "contracts": [
        "MA2610",
        "MA2701"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "short_spread",
      "data_feasibility": "available",
      "data_feasibility_reason": "按该模型研究资料单独评估，账户和计划缺项另列",
      "signal": "unknown",
      "signal_basis": null,
      "screening_evidence": "ma_pct",
      "evaluated_checks": [
        {
          "rule_id": "screening",
          "applicable": true,
          "result": "pass",
          "evidence_refs": [
            "ma_pct"
          ],
          "details": "分位100仅通过研究筛选，不代表完整信号"
        },
        {
          "rule_id": "domestic_model_basis",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "尚需论证海峡不缓和时支持收敛的独立国内变化，不能通过改名绕①"
        },
        {
          "rule_id": "confirmation_definition",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [
            "ma_spread",
            "ma_change_1td",
            "ma_change_5td"
          ],
          "details": "确认规则未事前冻结；单日收窄与5日走阔均保留，不倒推条件"
        },
        {
          "rule_id": "#5",
          "applicable": true,
          "result": "fail",
          "evidence_refs": [
            "ma_inventory",
            "ma_inventory_change"
          ],
          "details": "本记录沿用库存支持收敛假设；当前采用的产业事实为去库，方向反向，未有独立同向支持；价格确认仍未知单列"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "方向假设为做空价差，但Entry/真实失效SL/TP/净R/期限和压力预案未完成"
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无当期经核实账户与挂单快照"
        }
      ],
      "evaluation_order": [
        "screening",
        "domestic_model_basis",
        "confirmation_definition",
        "#5",
        "execution_plan",
        "account"
      ],
      "all_blockers": [
        "#5"
      ],
      "unknown_checks": [
        "domestic_model_basis",
        "confirmation_definition",
        "execution_plan",
        "account"
      ],
      "first_blocker": "#5",
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": [
          "D9=3 default_neutral"
        ]
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": "仅保留国内回归假设；未形成可冻结的数值确认定义，不能将临时3日/40元示例回填为历史标准",
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": [],
      "remaining_execution_review": "未声称完成31条全门覆盖；#3须按具体模型precheck拆分，不能把全局海湾出口未知自动带入国内路线"
    },
    {
      "candidate_id": "RB_A_2610_2701",
      "opportunity_id": "RB_A_2610_2701",
      "trade_date": "2026-09-08",
      "contracts": [
        "RB2610",
        "RB2701"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "available",
      "data_feasibility_reason": "按该模型研究资料单独评估，账户和计划缺项另列",
      "signal": "not_triggered",
      "signal_basis": null,
      "screening_evidence": "rb_pct",
      "evaluated_checks": [],
      "evaluation_order": [],
      "all_blockers": [],
      "unknown_checks": [],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": []
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": [
        "方向/确认/完整计划/适用执行门/账户容量"
      ],
      "evidence_refs": [
        "rb_pct"
      ]
    },
    {
      "candidate_id": "SR_A_2701_2705",
      "opportunity_id": "SR_A_2701_2705",
      "trade_date": "2026-09-08",
      "contracts": [
        "SR2701",
        "SR2705"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "available",
      "data_feasibility_reason": "按该模型研究资料单独评估，账户和计划缺项另列",
      "signal": "not_triggered",
      "signal_basis": null,
      "screening_evidence": "sr_pct",
      "evaluated_checks": [],
      "evaluation_order": [],
      "all_blockers": [],
      "unknown_checks": [],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": []
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "no_signal",
      "not_evaluated_after_no_signal": [
        "方向/确认/完整计划/适用执行门/账户容量"
      ],
      "evidence_refs": [
        "sr_pct"
      ]
    },
    {
      "candidate_id": "MA_A_2701_2705",
      "opportunity_id": "MA_A_2701_2705",
      "trade_date": "2026-09-08",
      "contracts": [
        "MA2701",
        "MA2705"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "未计算，不等于模型最低研究资料长期不可得",
      "signal": "unknown",
      "signal_basis": null,
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "本次已有输出未计算该对；v1.11已增加准备取样，尚未联网生成结果"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "新对方向与计划须另核，不能继承旧分位"
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照"
        }
      ],
      "evaluation_order": [
        "#13",
        "execution_plan",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "#13",
        "execution_plan",
        "account"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": []
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": []
    },
    {
      "candidate_id": "RB_A_2701_2703",
      "opportunity_id": "RB_A_2701_2703",
      "trade_date": "2026-09-08",
      "contracts": [
        "RB2701",
        "RB2703"
      ],
      "strategy": "A",
      "hypothesis": "reversion",
      "evidence_basis": "domestic_public",
      "direction": "unknown",
      "data_feasibility": "temporary_gap",
      "data_feasibility_reason": "未计算，不等于模型最低研究资料长期不可得",
      "signal": "unknown",
      "signal_basis": null,
      "screening_evidence": null,
      "evaluated_checks": [
        {
          "rule_id": "#13",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "本次已有输出未计算该对；v1.11已增加准备取样，尚未联网生成结果"
        },
        {
          "rule_id": "execution_plan",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "新对方向与计划须另核，不能继承旧分位"
        },
        {
          "rule_id": "account",
          "applicable": true,
          "result": "unknown",
          "evidence_refs": [],
          "details": "无账户快照"
        }
      ],
      "evaluation_order": [
        "#13",
        "execution_plan",
        "account"
      ],
      "all_blockers": [],
      "unknown_checks": [
        "#13",
        "execution_plan",
        "account"
      ],
      "first_blocker": null,
      "only_blocker": null,
      "score": {
        "canonical_ref": "3.1 A公开数据评分卡",
        "result": null,
        "defaulted_dimensions": []
      },
      "plan": {
        "entry": null,
        "stop": null,
        "targets": null,
        "confirmation_rule": null,
        "confirmation_definition": {
          "state": "undefined",
          "rule_version": null,
          "defined_at": null,
          "effective_from": null,
          "price_basis": null,
          "economic_rationale": null,
          "observed_values": null
        },
        "holding_period": null,
        "latest_exit_date": null
      },
      "risk_evaluation": {
        "canonical_ref": "framework/futures_framework.md Step5 / #31",
        "calculator_ref": "scripts/futures_risk.py",
        "result": null
      },
      "final_lots": null,
      "status": "incomplete",
      "not_evaluated_after_no_signal": [],
      "evidence_refs": []
    }
  ],
  "unresolved_items": [
    {
      "item": "运行v1.11取得新对样本和SC字段级证据，再按实际输出复评",
      "owner": "研究方/已有行情环境",
      "due_at": null,
      "required_evidence": [],
      "resolution": "pending"
    },
    {
      "item": "基于原始同对序列及独立国内逻辑定义可留痕的前瞻确认方案；若不支持则明确结案",
      "owner": "研究方",
      "due_at": null,
      "required_evidence": [],
      "resolution": "pending"
    },
    {
      "item": "仅在执行核验阶段提供当期账户、持仓、挂单及实际费用/保证金",
      "owner": "账户持有人",
      "due_at": null,
      "required_evidence": [],
      "resolution": "pending"
    }
  ]
}
```

校验命令：`python3 scripts/validate_futures_audit.py --input research/2026-09-07-execution-audit-reassessment.md`。本次实际结果：valid、退出码0、errors=[]，execution_permission=not_evaluated。结构校验不检查门覆盖、独立经济因果、确认规则的有效性或实际交易许可。
