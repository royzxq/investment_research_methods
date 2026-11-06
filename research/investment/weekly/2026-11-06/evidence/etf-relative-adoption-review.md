# R22 方法采纳与接续审查

2026-11-06，Asia/Shanghai，generator=codex。用户明确授权检查兼容性后同步生产。此为方法接续，非新的市场研究。

已安全 fetch 的 main 为 `bbbb177`。GitHub 实际 PR #51 状态 MERGED，merged_at=`2026-10-20T00:47:57Z`，merge_commit=`346caada9172b4346c6b9246cb66978b06024ba4`，且为当前 main 祖先。11/01 adopted handoff 来源与引用通过 helper 验证；两份基础方法除受限观测外与原工作区一致。因此框架旧“控制语义仍隔离”注记属于过时状态，修正它不扩展投资方法或控制动作。

R22 为明确采用的方法增补，定义、经济理由与正反边界见本日适配报告及 change-decision-r2。其变化包含研究范围与机会成本定价，不与旧方法做全局等价桥接；`compatibility=[]`。旧冻结任务继续原 prompt/input/hash，发布时由既有兼容门禁处理。新批次分别冻结两份实际正文和本 handoff 来源，不能只凭版本标签证明兼容。

已检查价格链：最终 P1 使用现行五项折扣公式，R22 的未满足要求只归 d_base；股价未达 P1 属运行时判断。T1、独立 entry/add/holding、风险唯一归属和解除证据合同不变。现有 audit-v2 是共享折扣模型，不能表达情景各异的 min(B,U) 报价区间；这种情况下交付明确基准 P1，保留情景敏感性，不能通过修改 V50 或其它风险拼出区间。旧方法快照不追补新说明。

自动 Codex/DSH 共用冻结框架；DSH 复用事实不复用另一端估值。元研究读取 projects/meta_investment_analysis/INSTRUCTIONS.md，新增两类上下文与原七变量并存；变化检测读取对应入口分类，不能把资金事实直接变成个股折扣。新方法只在研究准备时生效，不改请求/交付 schema、模型配置、额度、168小时冷却或下游 CSV 消费者。

承接11/01全部 rule_evaluations、五项 pending 及 withdrawn_sources，保留原 as_of/evidence_cutoff，不把11/01状态重新认证为11/06行情。R22当前逐股结论为 unknown；未指定股票、未完成逐股复评，不能生成虚假 completed，也不以新增规则自动给全市场设 persistent 阻断。五 pending 的旧 methods 留作任务来源；实际完成须用新方法及真实报告/JSON 验收。

本次与旧状态接续关系是继承原事实和未完成义务，非确认旧价格满足新方法。旧撤回持续有效，不因切回旧方法复活。验证程序只证明结构、算术和来源绑定，不证明前瞻预测或投资收益有效。
