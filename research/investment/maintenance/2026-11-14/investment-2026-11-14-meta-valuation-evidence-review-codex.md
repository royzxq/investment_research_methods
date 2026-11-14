# 元研究估值证据接续评审

- 日期：2026-11-14（Asia/Shanghai）
- 生成端：Codex
- 基线：`3600af12ad898356f83291a8419127639db1f094`，本地 `dev`
- 工作分支：`codex/meta-valuation-evidence`
- 结论：**PASS**。上游补齐证据要求，变化检测及框架适配使用原接口接续；无需改变估值方法身份、运行程序或报价。

## 修改范围

1. [元研究主提示词](../../../../projects/meta_investment_analysis/INSTRUCTIONS.md)：区分经营兑现、估值假设与市场预期；记录经济传导、旧假设、已有吸收及待核残余；对称核验乐观与悲观叙事，保留反向估值的条件组合及模型适用边界。
2. [元研究阶段入口](../../../../.agents/skills/investment-weekly-review/references/meta-investment-analysis.md)：明确读取上述要求，全文传递证据，保留旧报告与冻结合同的适用边界。
3. [周更总入口](../../../../.agents/skills/investment-weekly-review/SKILL.md)：完整模式明确连接元研究、变化检测、框架适配 reference；原单阶段结束边界不变。

这是现有已采纳估值规则的上游证据要求补齐，没有改 canonical/compact、默认参数、审计版本、handoff schema、公司研究调度或正式报价写入链路。原七变量及既有 ETF_LIQUIDITY_CONTEXT、BENCHMARK_CONTEXT 字段不变，不新增必填顶层字段。旧报告缺项表示当期未研究，不补0、不倒填、不失效其余有效证据。

## 链路核对与语义评审

实际读取了[变化检测](../../../../projects/investment_change_analysis/INSTRUCTIONS.md)原则9/10及估值段、[框架适配](../../../../projects/investment_adaption/INSTRUCTIONS.md)第4/5步及估值适配报告要求，并检查各自 skill reference。下游已支持三类变化、原假设/已吸收归属、旧冻结兼容和独立状态接续，本次不重复修改其定义。

以下为合成场景的人工语义走查，不是模型生成实测，也不是公司投资结论：

| 输入场景 | 沿链路应得到的结果与核对结论 |
|---|---|
| 同一需求损失已下调收入，又被换名列作额外风险折扣 | 元研究传原假设、期间和已吸收位置；已采纳唯一计价规则下列 evidence_correction，交公司核对独立残余，不预填新的折扣。 |
| 募资到账并增发股份，未来投入已进入现金流，却按项目用途再扣同笔现金 | 传股本—资金—用途—收益及时间配对证据；变化检测列资本桥纠错。若原依据不全保留unknown，不直接宣布现金全部可加回。 |
| 没有新增经营证据，只有市价与V50差距扩大 | 行情可以 state_refresh，差异交解释/复核；不能因此拟合PE/WACC或自动新增交易阻断。 |
| 现金流改善有公告支持，但持续性仍不确定 | 改善与反证都传递，分开已兑现、暂时改善和预测；不预设市场高估，也不据改善自动消除原买入/持仓约束。 |
| 增长下滑、利润率下降和融资成本上升确有共同证据 | 可保留有依据的悲观基准；禁止的是无共同证据的最悲观假设堆叠，不要求用乐观值机械抵消。 |
| 报告只给一个反推收入数，未说明固定利润率或资本成本 | 缺失条件标unknown，要求补模型、固定条件、变量和业务范围；不把单个解或行业TAM称为唯一公司天花板。金融/有限寿命等不强制换DCF。 |
| 旧报告没有风险归属记录，旧冻结合同也没有新审计版本 | 历史缺项不等于风险未计价；保持原报告/prompt/input/合同，只记录待研究或兼容线索，不按新字段追溯拒收。 |
| 周报提议全行业统一WACC或新增默认倍数 | 变化检测列 method_change，适配需定义/依据/边界并待采纳；既有方法下的独立状态刷新仍继续。 |
| 证据涉及四项以上待核问题 | 前置验证摘要仍至多三项，其余随全文进入重要变化项/下游影响；不能仅传七变量摘要而丢证据。 |

评审中补齐了完整模式到框架适配 reference 的显式链接，并将“不得拼接最悲观假设”限定为缺少共同证据的拼接，避免提示词排斥有依据的共同恶化。修订后未发现未解决的阻断问题。

## 实际验证

- `quick_validate.py .agents/skills/investment-weekly-review`：通过；检查了本次新增的阶段链接目标存在。
- `scripts/investment_framework_governance.py --check`：通过，方法身份及状态日期（2026-11-08）不变。该检查仅证明结构与指纹约束，不证明投资方法有效。
- 定向回归：**50 tests，7.817s，OK**。44项维护接续测试及6项 runner 测试；其中一个测试逐一恢复v1–v6冻结合同并比对原始字节。另含旧v3 writer、旧v4准备输入、无活跃框架的旧completed、状态独立冻结及带日期的公司完成凭证。
- 首次模块式调用因 `research_audit_fixture` 不在导入路径出现5个错误；补上测试辅助目录 `PYTHONPATH=tests` 后相同50项全部通过，没有为此修改业务代码或测试。
- 实际运行 `select_adopted` → `freeze_maintenance`：选中原11月14日handoff，在隔离临时目录冻结并逐字节核验34份来源，5项pending保留。未生成新批次或运行真实模型。
- 比较新旧元研究输出字段列表：原七变量和两个既有证据字段完全一致。
- 对本次开工前记录的**6,488个文件**核验SHA-256一致，覆盖历史研究、已有冻结输入/快照、canonical/compact及1,291个生产保护文件（正式报价与公司产物等）。
- `git diff --check`：通过。

本轮回归命令（在仓库根执行，Python使用ai_investment仓库myenv）：

```sh
PYTHONPATH=tests /Users/xinquanzhou/Workspace/ai_investment/myenv/bin/python -m unittest \
  tests.test_investment_maintenance \
  tests.test_research_runner.ResearchRunnerTests.test_v1_to_v6_frozen_recovers_under_new_default_without_rewriting \
  tests.test_research_runner.ResearchRunnerTests.test_v3_frozen_snapshot_and_legacy_writer_remain_bound \
  tests.test_research_runner.ResearchRunnerTests.test_old_v4_prepared_contract_keeps_its_frozen_prompts_and_inputs \
  tests.test_research_runner.ResearchRunnerTests.test_completed_legacy_archive_remains_readable_without_live_framework \
  tests.test_research_runner.ResearchRunnerTests.test_adopted_state_is_frozen_independently_of_framework_pr \
  tests.test_research_runner.ResearchRunnerTests.test_frozen_completed_pair_validates_with_dated_availability_and_no_live_files -v
```

接续身份保持：

- handoff：`research/investment/weekly/2026-11-14/investment-2026-11-14-handoff.json`
- handoff SHA-256：`23048b133151087e09249cd2d7d6f8a8ede148e1968e487f3ac696c9273169ba`
- canonical method fingerprint：`6b90ff1a149123e882bb27524629fa7dd2645070871fe7ae94e46e045af3e52b`
- compact method fingerprint：`8b75958d5facf48e1e464423b3781191fa800d31b5f02bdbcd28c67346048761`

由于两份方法正文及身份未变，本次不创建重复的adopted handoff，也不把旧pending标为completed。本次没有重跑全部离线套件或真实市场元研究；人工场景走查不能证明模型每次遵循提示词，更不能证明预测准确率提高。

## 六维检查与交付边界

| 维度 | 结论 |
|---|---|
| Hard Boundaries | PASS；研究证据在元研究整理，个股模型/参数仍由逐股论证，正式报价写入属主不变。 |
| Hard Stops | PASS；无凭据、无全仓格式化/重命名，无旧模块复活。 |
| Dead Code | PASS；未新增代码或平行规则版本，无需删除兼容路径。 |
| 范围纪律 | PASS；3份提示词/入口及本评审记录，不修改无关产物或未跟踪研究。 |
| ADR/文档 | PASS；未改变API、schema或架构不变量，适用现行canonical与冻结合同，不另立估值算法。 |
| 测试约定 | PASS；使用现有行为回归、真实接续helper和人工边界走查；不新增仅匹配提示词措辞的测试。 |

用户授权评审后合并本地dev。本次不推送远端，不采纳新的市场状态，不更新正式P1/T1、模型报价、CSV或公司latest。回退应只撤销本次三份入口/提示词改动，历史报告和冻结方法仍保留原字节。
