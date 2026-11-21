# 期货变化检测与执行诊断（阶段②）

## 输入

AS_OF_DATE、CURRENT_META_RESULT（必有）、已采纳 PREVIOUS_META_RESULT/同日期 PREVIOUS_CHANGE_DECISION（可无）、当前 canonical、EXECUTION_EVIDENCE。单独比较使用用户指定报告，不自动补跑研究；完整流程按 [刷新和接续](refresh-and-handoff.md)核确切路径和纠错范围。

## 执行

1. 读数据协议、`projects/future_change_analysis/INSTRUCTIONS.md` 与同目录 EXECUTION_AUDIT_TEMPLATE.md。先核日期、单位、适用性和新旧版本，撤回错误依据并重评，纠错不计作市场反转。
2. 每期均生成独立审计。五品种筛选、最多两份新计划，T/V 与 G1–G6 只引用 canonical；账户未知继续公共研究，专业增强缺失不使全池 incomplete，长期不可得必要依赖列 research_only。
3. 逐一复核已知存量计划/持仓的相关事件、反证、止损和期限，不受新机会数量上限限制。入场窗口到期与已知持仓退出分开；缺账户输出条件管理和具体缺口，不能假设平仓。观察状态按已触发／未触发／已失效／转研究观察登记，沿用 opportunity_id 和原有效期；T/V 新反向信号按现行规则研究。旧影子引擎未支持 T/V 时保留人工轨迹边界，不冒充收益验证。
4. 分别判定 state_refresh、evidence_correction、method_change，可并存。update_needed 只映射 method_change_needed，级别只描述方法变更；市场主因、研究排序和常规触发/退出不构成方法变化。
5. 方法变更必须说明定义缺陷或新证据、为什么现有状态/风险规则无法处理，以及旧新同输入的信号、计划、容量或退出差异、存量影响、固定版本验证与撤回条件。不能从单周输赢、踏空或 ready 数直接改参数。
6. 无前期实质基线时明确不可比较，仍完成本期审计、纠错和框架一致性检查。数据抓取失败、长期不可得模型依赖及方法缺陷分别处理，不以缺数据无限增门。
7. 按 instruction 输出三类处置。无方法变化仍刷新当期状态引用和 handoff，需修改规则定义的纠错同时进入方法适配；单阶段到此结束，后续由入口承接。

## 输出

保存 change-decision 与独立 execution-audit，原稿不覆盖。返回全文和路径、CHANGE_CLASSIFICATION、FRAMEWORK_UPDATE_DECISION、KEY_VARIABLE_CHANGES、STATE_REFRESH、EVIDENCE_CORRECTIONS、DATA_FEASIBILITY、UPDATE_FOCUS、DO_NOT_OVERREACT_ITEMS、EXECUTION_AUDIT。only_blocker/unknown/status/null 全沿共享模板，不另造风险契约。
