# 期货变化检测与执行诊断（阶段②）

## 输入

- `AS_OF_DATE`、`CURRENT_META_RESULT`（始终必有）、`PREVIOUS_META_RESULT`、同日期 `PREVIOUS_CHANGE_DECISION`（可无）。完整流程按入口精确发现；单独比较使用用户指定报告，不换输入或自动补跑市场研究。
- `CURRENT_FRAMEWORK`：`framework/futures_framework.md` 现行全文，跳过顶部维护说明 HTML 注释；参数、方法与歧义以 canonical 为准。
- `EXECUTION_EVIDENCE`：有效期货快照、账户／挂单、候选计划、历史诊断来源清单。单独调用未提供则读取已有材料并明确缺口，不假定账户空仓或行情最新。

## 执行

1. 先读 `framework/FUTURES_DATA_PROTOCOL.md`、`projects/future_change_analysis/INSTRUCTIONS.md` 及 `EXECUTION_AUDIT_TEMPLATE.md`（同项目目录）。在市场比较前核对新旧证据的完整年份、观测日、单位及口径，处理 `EVIDENCE_CORRECTIONS` 和 `DATA_FEASIBILITY`；跨年与错误解释的修复不算市场反转。
2. **每期生成独立执行诊断，即使无框架更新**。采用共享模板中的全部状态及风险空值定义：活跃候选确有必要缺项用 `incomplete`；长期不可得专业依赖用 `research_only` 与恢复条件；增强缺失不拖累其他模型。研究已成案只差账户信息时标 `awaiting_account`，账户未知不阻止前面的研究／评分。不得另存评分或风险公式。
3. 行情、D8 周涨分位及影子结算以有效快照实测值为准，记录快照日期，不用推算替代已有实测。对最接近成立的至多两条候选登记 `shadow_plans`；正文列快照 §5 影子结算与按阻断归集结果。
4. **复核上期观察项**：纠错后、比较前逐条处理预备项，写「0. 上期预备观察项复核」，标已触发／未触发／已失效／转研究观察。旧证据失效明确撤回并重评；休眠路线或专业必要数据长期不可得可归 `research_only`，保留原因和复活条件，不无限顺延。只有适用、证据有效且原预设属于框架更新条件的条目已触发，才支持 `update_needed=yes`；级别按预设，无预设从 light 起步。纯待补数据或数据修复不自动触发改规则。
5. 按 instruction 六步完成周环比。无实质上期基线时明确不可比较，不虚构旧值；仍完成执行诊断及可适用的证据纠错、框架一致性检查，说明判定依据与限制，不把本期结果自身视为变化。
6. **框架与现实一致性轴**：检查机制档位、地缘轴、precheck 门和当期纪律是否直接矛盾或累积错配；周环比小也可能构成更新依据。
7. **反摇摆护栏**：新市场证据要推翻最近 1–2 周方向性设定，必须有适配路线、日期／口径有效的价格行为或公开硬数据，并论证为何不是摇摆回滚。未达标准则保留仍有效设定，列可核验的条件观察项。纠错、错误规则适用性及不可实施依赖不受该护栏限制，不得保留已证伪依据；长期不可得路线转研究观察。
8. 只关注交易重点、判断顺序、权重及阈值，不把措辞或单周噪音当框架变化。新延后事项必须实际可核验且有触发条件，长期不可取得数据不列活跃待办。

## 输出

- 完整变化报告写 `research/<AS_OF_DATE>-change-decision.md`；独立诊断写 `research/<AS_OF_DATE>-execution-audit.md`。缺历史完整账时，不对连续空仓／规则有效性作确定归因。
- 按 instruction 保留 `FRAMEWORK_UPDATE_DECISION`（`update_needed`、级别、理由）、`KEY_VARIABLE_CHANGES`、`UPDATE_FOCUS`、`DO_NOT_OVERREACT_ITEMS`、`DATA_FEASIBILITY`、`EVIDENCE_CORRECTIONS`、`EXECUTION_AUDIT`（路径、框架版本、活跃／研究观察范围及证据结论）。
- 返回变化报告全文与路径、`update_needed`、`CURRENT_EXECUTION_AUDIT` 全文及路径，完整更新并透传可得性和纠错字段。单阶段到此结束，同日与发布边界沿用入口。
