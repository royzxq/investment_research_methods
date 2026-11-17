# 个股调研框架更新结果

2026-11-16，Asia/Shanghai，generator=codex。范围为估值可用性与观察结论的方法修订。

## 1. 更新结论

method_change=true，state_refresh=false，evidence_correction=false，update_needed=true。按用户“好的，帮我修改”的明确指示完成本地修改，方法在当前分支本地采纳，配套同日adopted handoff绑定最终正文。分支为codex/valuation-observation，未提交、合并dev/main、推送或远端发布。未改任何公司报告或价格。

预期减少“有普通缺口就直接不可估”的误判。未来参数允许有依据假设，正式报价留空前须评估重要性并尝试边界/代理/替代模型。价格留空也要在正式报告交付可用条件结果、限制和下一证据；确无结果时解释原因。新任务默认controls-v9/audit-v6，价格JSON保持stock-research/v4。

## 2. 受影响模块

| 位置 | 修改与对象 |
|---|---|
| canonical §4.1D、compact §7 | 所有新股票研究的输入状态、留空判断顺序与结论用途，局部同步 |
| stock-research及估值/一致性references | 明示合理代理、有界假设、观察用途及可见条件结果；旧冻结合同优先 |
| research_consistency | audit-v6增加availability_review，留空需尝试/覆盖未决输入及解释，生成报告可见表 |
| research_runner、research_recovery、research_acceptance | 新v9冻结合同、验收与恢复接入；旧提示与验收保留 |
| investment-weekly-review及完成验收 | 新v6完成须lifecycle/acceptance，接续原待复评和撤回证据 |

## 3. 修改说明

经济依据是估值本身依赖预测。未知精确值与无法合理估值之间，需要重要性和区间论证。现有程序对声明unresolved后的留空约束很强，却未要求同等具体的留空依据，容易造成执行倾向差异。依据见[前序审计](../../maintenance/2026-11-16/investment-2026-11-16-valuation-availability-audit-codex.md)和[变化决策](investment-2026-11-16-change-decision.md)。样本支持机制诊断，尚非受控因果检验。

操作定义为“事实/假设分列→论证缺口影响→尝试边界、代理或适用替代→裁决可用范围→给价格或留空”。公司历史、披露计划、资产寿命、同口径可比等可支持合理代理。足以支持中性路径和情景区间即bounded；遇反证或越过边界重新估值及判资格。没有统一新增比例/金额门槛，按能否改变价值区间或资格判断重要性。来源日期继续不得晚于估值日，币种、单位和现金流联动仍按原定义。

任一正式V50/P1=null时，availability_review须有decision_reason、attempts、diagnostic_summary、next_evidence。相关输入合组，每个unresolved被覆盖；尝试包括方法、边界或失败原因、价值影响与裁决。有价时此项可null。全部输入被标resolved也不能跳过留空尝试，除非有blocking的reject/invalidated/exit_required；若仍有unresolved，即使硬失败也须覆盖这些输入。程序核覆盖与非空声明，无法证明模型认真尝试或假设经济合理。

| 场景 | 新方法结果 | 边界 |
|---|---|---|
| 缺精确税务明细，历史与公开结构足以约束区间 | 有界假设可继续V50/观察P1，联动及敏感性披露 | 不把合并亏损当自动免税或退款 |
| 市场/事件暂时freeze，估值可用 | frozen保留观察价格，entry/add限制独立 | 不用tracking隐藏freeze |
| 请求权/担保范围无法约束，替代模型仍不能界定普通股价值 | V50/P1保持null，报告显示已试路径、条件结果限制及下一证据 | 不强造数字或安全垫 |
| V50可估，仅独立折扣仍核心未决 | 保留V50，P1及未知折扣仍null | 不把未知折扣记零 |
| 已确认硬否决且无估值未决 | 可免估值尝试，保留否决及重研条件；无新P1 | 低价不自动解锁 |
| P1实际为low/high区间、base=null | 仍属于有价，不强补中值或留空论证 | 价格提取契约不变 |

可能的副作用是形式完整的假设仍可能不可信，或模型为了出价误标bounded。缓解方式是保留来源、联动、敏感性、风险唯一计价、基线变化及独立控制；不设出价率目标。后续真实双端同包研究需同时考察论证质量、风险遗漏、估值稳定性和适当保留空值的能力。

## 4. 不应过度反应

R/D规则、评分、数值阈值、AND/OR、例外及解除证据未改。风险在现金流、资本桥或独立折扣计价一次，假设区间不承诺统计覆盖或保证安全价格。治理失效、偿付问题、必要资格缺证不随降价自动解除。普通观察不等于具备买入资格，已触发freeze保持frozen。没有触价率校准，没有新增PE/WACC/折扣常数。

旧个股结论、报价、latest及账户执行未改；新方法不自动把上期不可估改为有价，也不取消既有pending。数据不足只限制相应范围；当前方法不能用任意代理把实质不可约束的核心风险写成已解决。

## 5. 新版框架链接

[canonical](../../../../framework/investment_framework.md)与[compact](../../../../framework/investment_framework_compact.md)的方法身份为stock-two-price-controls-v2-etf-relative-v1-dividend-v1-capital-v1-dcf-v3。新定义位于canonical §4.1D“留空前的可用性复核”“结论与价格用途分判”，compact §7对应三段。没有复制另一份执行权威。

## 6. 版本变更记录

| 文件 | 阶段 | 完整SHA256 | 方法SHA256 |
|---|---|---|---|
| investment_framework.md | before | `14d0bf8641ad63565ae55ca27fea618fe0cbd8b4248f83ea3c6dd1addbce29d6` | `a44efae46a01474f54d4c0af28ef010f712afab310a4f2e4974e3ffd8f2cb9f8` |
| investment_framework.md | after | `2b909852e5afacc1ea832a76540c04469439fb016692dc91c32bd7160e13fb32` | `6303f7f694f21805a2122c2db7a67b8539a00a37e741f214084ab2f602c86e7e` |
| investment_framework_compact.md | before | `2820e1f2ba4843e297a5de2762aa095357ef056dda480643519f1834277a8467` | `e4cd7b99dec7ece11fe96fb0266fb2450d9805d22eeb39e21a396e63c5d2827f` |
| investment_framework_compact.md | after | `2ad08f195bb6729dd8c7aea96ccaf85c1fa5504aa53cfd18beef90f0e0377d1e` | `782ff89d54dab37e9652c8e6a8c11706379773e23fed3cd21176fe83aa24769d` |

旧方法来自[11/15 handoff-r2](../2026-11-15/investment-2026-11-15-handoff-r2.json)。新本地采纳见[11/16 handoff](investment-2026-11-16-handoff.json)，来源是用户本次明确方法修改授权；尚无Git发布。此前5项pending、25项rule_evaluations及4条withdrawn_sources原样接续，原触发/截止日期不移动。未生成任何公司completed凭证。

新旧方法不声明经济等价，不添加跨方法自动兼容许可。旧冻结继续原prompt/input/hash及原审计，发布前仍走既有方法适用性隔离。新研究默认v9/audit-v6；价格JSON保持v4，下游价格字段无需迁移。

## 7. 验证

固定最终代码后，全量离线回归 **1399 项通过**，耗时276.172秒。最终定向100项通过，覆盖新假设/留空边界、v6 DCF与反向估值、P1区间、周更完成门禁和旧合同提示；共享证据组21项复跑通过。首轮全量运行期间我调整了新提示文字，导致3项主/子进程版本不一致，已在代码固定后重跑全量通过。系统Python的初次定向调用遇到tests包路径问题，改用项目记录的conda解释器；技能校验使用具有PyYAML的系统Python。初次沙箱runner测试被ps权限阻断，最终全量经批准运行本地临时服务/进程检查。

框架治理、两个已改技能quick_validate和git diff --check通过。162组历史报告/价格文件及其审计展示SHA256未变，覆盖126份audit-v2、2份v4、34份v5；旧v1–v8八种提示哈希一致。旧冻结恢复的单元回归通过。详见[验证摘要](evidence/valuation-observation-validation.json)、[历史兼容核对](evidence/valuation-observation-compatibility-result.json)与[框架差异证据](evidence/valuation-observation-framework-diff-evidence.json)。原始本地日志路径及SHA256见验证摘要。

未调用真实行情或模型API，未运行新的个股研究、双端A/B或收益回测。上述结果证明结构、算术和兼容链按测试执行，不证明估值假设可信、方法投资有效性或实际拒绝率已下降。

## 8. 精简版同步

本次为局部同步。完整文件差异只落在两份文件的方法身份、日期说明和§4.1D对应段落；其余正文逐字保留。七项核对如下。

| 自审项 | 结果 |
|---|---|
| 有效内容覆盖 | 新增假设允许、重要性/尝试顺序、null范围、硬否决例外、下一证据、触发重新估值及资格独立均在compact承载 |
| 数值与公式 | 既有公式/阈值在改动范围外逐字不变；新增内容不设统一数字门槛 |
| 稳定引用 | 全文件R/D编号出现顺序与占位符计数未变；新内容回指§4.1D，没有重编ID |
| 自包含抽检 | 有界税务假设、已触发freeze、核心请求权不可约束三例仅按compact即可作同样判断 |
| 副本矛盾 | 可估与资格分判、条件诊断与正式报价、硬否决免尝试边界均同义；没有新增另一组折扣 |
| 决策链 | 数据契约→Precheck→机制→Gate→估值→Terminal→Price Map→结论原顺序未改，在估值留空前插入复核 |
| 体积与范围 | canonical 968→974行、130839→133468 UTF-8字节；compact 648→654行、88203→89909字节。状态JSON原字节保持，未新增市场触发或个股评审任务 |

本次核验覆盖修改条款及全文件改动边界，没有重新证明历史整份canonical/compact所有语义等价，不使用“100%保真”结论。结构治理不替代语义与投资有效性审阅。
