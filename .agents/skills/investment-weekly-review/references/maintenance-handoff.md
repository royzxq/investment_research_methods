# 股票维护接续与来源

本文件用于 full/refresh 的状态采用、同日修订、版本桥接；research/compare 单阶段仅研究，不自动采用结果。helper 为 `scripts/investment_maintenance.py`，标准库实现，只检查结构和来源，不判断金融语义、合并权限或执行交易。

## 三类变化

- `state_refresh`：以既有阈值/对象/动作/例外更新行情、事件日历及状态读数。全局市场约束只影响适用公司与买入资格，不自动阻断证据充分的价值研究。
- `evidence_correction`：更正错误来源、时间或错误“已执行”断言；列撤回证据及受影响结论，将缺乏完成凭证的逐股复评退回 pending。若更正改变方法定义，同时另列 method_change。
- `method_change`：任何权重、阈值、AND/OR、适用对象、动作、例外或解除路径变化。必须列 definition、economic_reason、scope、positive_case、negative_case、boundary_case、compatibility_impact 和 proposed/adopted；一个“light”名称不能豁免定义与验证。

## 日期、修订和基线

`weekly_path(root,date,kind,revision=None)` 的 kind 为 market-research/change-decision/adaption-report/handoff。首份沿用正式名，后续 `-r2` 起；`next_revision(root,date)` 为整包分配同一 suffix。使用一次分配结果写整包，不能每写一份再次分配。同输入复用；新证据默认新 revision，不覆写旧记录。

```sh
python3 scripts/investment_maintenance.py path --date 2026-10-11 --kind handoff --next
python3 scripts/investment_maintenance.py select --date 2026-10-11
python3 scripts/investment_maintenance.py validate research/investment/weekly/2026-10-11/investment-2026-10-11-handoff-r2.json
```

严格发现允许 rN，但**发现不是采纳**。`select_adopted(root,as_of,methods)` 只选明确采用、来源哈希有效且与当前方法兼容的记录，返回 path/sha256/record 或 null；methods 是 canonical/compact 两个 `file_ref(root,path)`。它先应用所有已采用/撤销记录的 supersedes 与 withdrawn_sources，再匹配方法，防止切回旧方法时复活已撤回证据。

历史正式报告首次桥接：读原报告、对应变化/适配与 Git 或用户明确采纳依据；将当时真正有效的两份方法正文保存在 evidence（不能拿今天正文冒充当时原文），明确报告所用版本与哪些结论仍兼容，建立新的 adopted 记录并写 adoption_basis。无凭证时保留 null，按当前已采纳方法重新评估受影响事实；不是永久研究门槛。未合并 PR、较新日期、上期“已采纳”自述均不能单独证明方法生效。

## handoff 最小格式

- `schema: investment-maintenance/v1`；`id` 与文件 stem 一致；`as_of`、`revision`（首份 null，后续 >=2）。
- `status: proposed|adopted|withdrawn`，`adoption_basis` 写明确授权/采纳记录或合并提交；`supersedes` 为被替代 handoff id 列表。proposal 无权 supersede；采用修订不修改旧文件。
- `method_status: adopted`；`methods` 含 canonical/compact 的仓库相对 `path`、完整 `sha256`、`method_sha256`，必须指不可变方法副本。`freeze_methods(root,date,revision)` 从**已核验为已采纳的**工作区方法复制；它本身不证明采纳。先冻结旧方法，再编辑提案。
- `reports` 含 market_research/change_decision 的 path/sha256/as_of，可另加 adaption；`evidence` 为实际使用的其他来源 refs。`withdrawn_sources` 列撤回 refs，撤回记录本身不再作为有效证据。
- `changes` 逐项列 kind/summary；方法项另列完整定义字段与 status。`classification` 使用 `classify_changes(changes)` 生成，其中 update_needed 只代表 method_change。有独立状态和待审方法时，handoff 可 adopted，但其 methods 仍绑定旧的已采纳方法，方法项保持 proposed。
- `rule_evaluations`：rule_id、as_of、rule_status=adopted/proposed、result=triggered/not_triggered/unknown/invalidated、affected_objects、evidence。affected_objects 可用具体公司、SH/SZ/HK/A 或 all，必须覆盖被安排复评的公司；triggered 必须有证据。提案评估仅为研究，不能产生有效交易约束。
- `reviews`：company（例如 HK-06886）、trigger_id、status=pending/completed/cancelled；completed 必须有 completion.report 与 completion.price_map 的完整 ref、evidence_cutoff 和实际使用的 methods；要求完整 stock-research/v3（兼容历史 v2）、证券/日期/生成端匹配、可见的0–8节与价格引用有效，报告第0节需显示这两份方法的完整sha256。evidence_cutoff 必须覆盖已采纳触发与证据日期；旧报告补 dated reassessment ref 可完成受影响部分复核，不强制全文重跑。方法不同还须 compatibility_review ref。没有公司报告就 pending，不能用 meta-only JSON 或“已命中”代替。缺旧方法来源先补核，不复填当前hash冒充历史；完成研究不代表账户交易。

决策来源的日期是必填项，不能因 `file_ref(root,path)` 默认只保存内容身份而省略：reports、evidence、compatibility.review、reviews.reassessment / compatibility_review、completion.report / price_map 的 ref 必须有真实可知日期 `as_of`，且不晚于该 handoff 的 as_of；rule_evaluations.evidence 还不得晚于所属规则评估的 as_of。`withdrawn_sources` 是被撤回旧内容的身份引用，可以只有 path/sha256，不要求补造旧来源未知的可用日；撤回决定日期由 handoff.as_of 表示，支持这次纠错的 reports/evidence 仍必须带真实日期。若撤回目标显式提供 as_of，也不得晚于决定日；不能以未来正向材料回写旧日纠错决定。`as_of` 表示这份证据/审查当时已经可用的日期，不是可随意填回的财报期末日。旧公司报告的定向 reassessment 仍须覆盖 reviews.evidence_cutoff，并在 handoff 日期内可知。纯 methods/content 身份引用可无日期。completion.report / price_map 的 ref.as_of 表示实际产物已可用日期，必须不晚于 handoff；v2 配对的 meta.valuation_date 另用于估值及触发覆盖，不能拿回溯估值日冒充报告完成日。不额外要求产物日期等于估值日；旧报告仍可用当日定向 reassessment 复核受影响部分。所有引用若显式声明 as_of，均必须为标准 ISO 日期且不晚于 handoff。程序检查声明的日期链，不会自动证明源文档真实披露日；研究者仍须读原文核验，缺日期保持待补证，不捏造时间。

`write_handoff(root,record)` 校验后独占创建，完全相同可幂等返回，不同内容必须新 revision。报告、冻结来源和 handoff 一起保存/按授权发布，不能仅推一个含失效本地路径的 JSON。个股批次消费时将已采用 handoff 与来源正文一同冻结；无记录不会禁止研究，应按当前方法取证。新 adopted/supersedes 记录承接仍 pending 的复评与有效撤回，不能因换周或换方法遗漏而默认关闭；关闭必须给 cancelled 理由或 completed 凭证。发布公司结果前用 `check_adoption_lifecycle(root,as_of,frozen_record)` 核对显式撤回/替代，普通无关新状态不自动阻断发布。

## 版本兼容和局部刷新

完整正文哈希用作来源锁定。`method_fingerprint(raw)` 只排除唯一 `investment-state:start/end` 内严格 JSON 事实块：schema/as_of/evidence_cutoff/source_report/observations，观测仅 id/value/unit/observed_at/source/status。坏标记、重复键、非有限值、规则键都不能判为纯状态。旧无标记文本按全文 hash；混排 D 段、方法版本标签、阈值、例外都继续参与比较。

两个方法指纹均相同时，可接续不同状态字节版本；只凭版本标签相同不够。正文其他差异默认需审查，受影响判断重评。确属兼容澄清时可新增 compatibility 项，包含 status=adopted、reason、对方两份不可变 methods、review 报告 ref；审查说明阈值/逻辑/适用对象/动作/例外/解除条件是否改变。helper 只验证该凭证完整，不证明语义等价。

事件触发或按需 refresh 只补有关证据，不强制每日全市场研究。新证据更新受影响观察和复评队列，不凭状态变化重置公司研究历史。R21 辅助 `evaluate_repair_exit(observations,trading_days,calendar=...)` 只计算已定义的深化退出：提供权威完整交易日历并校验连续三个 A 股交易日；研究流程另核实所选窗口截至 AS_OF 是最新可用的完整三日，helper 不把全年日历末尾当当前窗口。三个交易日中各日成交>1.6万亿元、完整两融日变动>-150亿元、科创50官方收盘>=1516.2。缺口 unknown；融资代理、盘中指数、混日数据拒绝。输出 met 仅可回等待复核，旧独立重建路径及逐股买入检查照常，不由 helper 代替。
