# 经济损失去重、融资现金桥与冻结兼容：实施验收

日期：2026-11-14，Asia/Shanghai。用户已授权按 P1–P6 方案修改规则、提示词及审计，并对小米与赤峰隔离复评；不更新正式报价。实现位于 `codex/research-risk-capital-audit` 工作树，基于 `0718623`。本地完成，未提交、推送、建立 PR 或生产 adopted handoff。

工作树：`/Users/xinquanzhou/Workspace/ai_investment/outputs/methods_rules_20261114/worktree`。原 `investment_research_methods` checkout 的既有未提交文件保持不变；本次没有切换生产执行目录。

## 1. 验收结论

规则与程序修改完成，1,347 项全量离线测试通过。新冻结合同为 `two-price-controls/v6` + `stock-research-audit/v3`，对外价格 JSON 仍为 `stock-research/v4`。旧冻结合同、提示词字节、审计及控制语义保留；新合同拒绝误交旧版 audit。

两家公司完成针对问题的增量复评。确定的推理/表示错误得到纠正，但**没有证明一个新的唯一合理报价**：小米残余风险的数值及基金净归属仍有缺口；赤峰未来产量所需、尚未计入估值的投入仍未闭合。新规则要求披露这些缺口，不能以任意折扣或“全部加回/全部归零”遮盖。

| 对象 | 确认并修复 | 尚未得到证据支持 |
|---|---|---|
| 小米 | unknown 不可算 true；同一经营/资金损失不按触发次数重扣；未资本化远景不再额外扣价 | r_v5、r_terminal、d_base 应取的唯一数值；基金现金、请求权与母公司追索的净调整 |
| 赤峰 | 真实 PE 与现金分列；不能把融资用途等同资金耗尽；发行前已支出不再扣新款 | 全部 77.84 亿元应加回或应归零；13/13.5/14.7 吨预测的剩余必要投入 |

两份最终研究记录：

- [小米隔离复评](/Users/xinquanzhou/Workspace/ai_investment/outputs/methods_rules_20261114/worktree/research/investment/studies/risk-capital-audit/2026-11-14/investment-01810-isolated-review.md)
- [赤峰隔离复评](/Users/xinquanzhou/Workspace/ai_investment/outputs/methods_rules_20261114/worktree/research/investment/studies/risk-capital-audit/2026-11-14/investment-600988-isolated-review.md)

## 2. P1–P6 实施映射与 diff 范围

| 提案 | 具体落点 | 保留的边界 |
|---|---|---|
| P1 全局经济去重 | canonical §0、§4.1B、§6.6；compact §3/§7 | 不新增默认折扣；资格、容量、持仓动作独立 |
| P2 三处诱导重复扣价 | canonical §3.4/§5.6/§6.3；compact 对应联动、R14 与映射 | 成本先入经营；尾部须独立；PE 仍含持续性判断 |
| P3 三值逻辑 | canonical §1.3、compact §4 | AND/OR/至少 k 项保留 unknown；必要缺证仍限制原 scope |
| P4 资金与股本同口径 | canonical §4.1C、compact §7 | 净款、股数、投入、收益、基金资产/请求权闭合；未知不当 100% 损失 |
| P5 新研究提示 | stock-research SKILL 及两份 references；runner v6 专属段 | 旧提示词不追加 v6；确定重复计价可 correction，不等新增公司新闻 |
| P6 最小审计接口 | consistency、runner、acceptance、旧 experiment 合同；4 个测试文件 | 外部价格 schema 不变；旧实验 v1 固定 audit/v2 |

修改 13 个既有规则/技能/程序/测试文件，另新增 ADR 和本次研究证据。超过常规 5–10 个文件是因为 canonical/compact、实际 runner、人工技能入口、审计/验收、旧实验兼容和对应测试必须同步；未改价格写入方、调度器或金融数据入口。没有新增运行配置或平行估值模块。接口决策见 [ADR](/Users/xinquanzhou/Workspace/ai_investment/outputs/methods_rules_20261114/worktree/docs/adr/ADR-20261114-economic-risk-capital-audit.md)。

## 3. 程序契约与兼容

profit_pe 新增必填 `equity_adjustments` 数组，无调整为 `[]`；每项 `{id, amount, reason, source}`，金额为模型币种亿元，支持正负。程序分别核：

`profit = revenue×net_margin + Σadjustments`

`equity_value = profit×pe + Σequity_adjustments`

`V50 = equity_value×1e8/shares×fx_to_quote`

同情景利润与权益调整 ID 不得重复；新 owner=`equity_adjustment` 承载已由现金/资产桥吸收的风险，不能再被折扣引用。缺字段、无来源、非有限金额与错配 schema 拒绝。非 PE 模型继续支持 other；不能为了逃过可计算的 PE 桥而改标签。

| 冻结合同 | 价格 / audit | 处理 |
|---|---|---|
| 老 report-quotes/v3 | v3 / 原 audit-v1 或原无审计 | 原冻结行为 |
| two-price/v1、controls/v2…v5 | v4 / audit-v2 | 保持旧 PE 公式、渲染、各代门禁和提示词 |
| controls/v6 | v4 / audit-v3 | 新权益调整；继承 v5 监控质量、v3 acceptance、v2 lifecycle |
| harness-research-experiment/v1 | 原实验投影 / audit-v2 | 明确固定旧合同，不随默认常量升级 |

prepare 冻结 audit 版本；正常验收及方法不兼容后的隔离验收都要求与冻结版本相等。重试和恢复继承原输入/合同。基线可读取 v1/v2，未解除 entry/add/holding 约束继续接续；升级不等于解除。旧两价 v1 至 controls v5 的五个 prompt SHA-256 已固定回归，历史提示词构造结果不变。

## 4. 实际验证与反例

- TDD：新增审计测试先得到失败（缺 equity_adjustments / 新版本不支持），实现后通过；未为纯文案改动添加镜像测试。
- 全量：`myenv/bin/python -m unittest discover -s tests -v`，**1,347 tests，271.706s，OK**。解释器来自 ai_investment/myenv。初次沙箱不允许本地 socket/ps；最终在获准的环境中跑完同一离线套件，未调用生产投研或写回。离线模型替身覆盖 prepare、run、retry、isolate、seal、recovery、control-only。
- 最后审阅恢复了 controls-v2 测试中“不得出现 v3 acceptance 提示”的较强断言；该单项再跑 **1 test，OK**。之后仅文档与证据整理，不再改生产逻辑。
- 新增边界覆盖真实 PE＋有来源现金正项/投入负项、利润/权益跨项 ID 重复、已吸收风险再折扣、合法版本配对、v2 基线到 v3、other 与隔离控制接续、新合同拒收旧 audit。
- 两份赤峰原 audit/v2 原文验收通过；两份 audit/v3 诊断重演通过算术、scope/lifecycle、acceptance 及监控质量检查。数值和所有未解限制与原模型相同。现金漏项、重复进 PE、同 ID 现金重复三种反例全部被拒。
- 股票 framework governance、stock-research skill quick_validate、`git diff --check` 通过。前两者仅证明结构/引用合规，不证明投资方法有效性。

结果数据与原始日志位置见 [validation-summary.json](/Users/xinquanzhou/Workspace/ai_investment/outputs/methods_rules_20261114/worktree/research/investment/studies/risk-capital-audit/2026-11-14/validation-summary.json)；算术与反例在 [verification.json](/Users/xinquanzhou/Workspace/ai_investment/outputs/methods_rules_20261114/worktree/research/investment/studies/risk-capital-audit/2026-11-14/verification.json)。`replay.py` 是本研究的可重复诊断脚本，只读原 methods 报告并写隔离材料；无需运行任何发布或报价脚本。新 v3 文件的基线及 R14 摘录已复制进 evidence，验收不依赖生产 output 路径。

## 5. 隔离复评方法与局限

本次是两名独立取证核验者分别核小米/赤峰，再由主代理复核、计算和裁决的增量研究。使用既有官方原件并重读关键页，同时按技能进行必要原文检索；不是整套生产 Codex/DSH CLI 研究重新跑一遍。未把另一端目标价作为独立估值答案。原始核验笔记和主代理复评均落盘；子任务只写各自证据文件，没有并行改代码。

小米事实截止 2026-10-15，赤峰截止 2026-11-12；执行日 11/14 的新规则作用于固定旧事实，属于反事实诊断，不是可用于无前视回测的历史预测。没有据此判断哪种模型的市场预测准确率提高。

确定例：小米 Claude 的 true/unknown/false 三取二不能说“两项成立”。正例：成本弱与现金流差均 true 时，第三项 unknown 不妨碍三取二成立，但价格动作仍先核已吸收损失。反例：未计 AI 增量不证明 18 倍现有利润没有终局风险；必要经营现金未加回不证明所有尾部都已承担。

赤峰基准 V50 差约 3.950755 元，其中现金处理约 3.520069 元、利润差约 0.430686 元。真实 PE 分列纠错本身零经济影响。新程序不会自动发现“不同 ID 实为同一损失”，也不会证明本身就错误但自洽的数字正确；真实现金余额、归属、投入和概率仍须语义/原文核验。

## 6. 正确性与仓库边界审查

主代理完成独立于实现步骤的反向审阅；未声称额外有第三位代码审查者。重点攻击默认 SCHEMA 变化传播、旧提示词重建、旧实验隐式升级、隔离后绕过审计、同 ID 双扣、来源缺失与非有限金额。审阅修正了旧实验版本引用、旧合同测试夹具、mock legacy schema 分支、三值 unknown 被简称“不成立”的歧义及较弱旧断言，均已验证。没有静默保留已知实现缺陷。

六维检查：

1. Hard Boundaries：没有修改 ai_investment 报价、持仓、行情或写回入口；新字段仅研究内部 audit，价格 JSON v4 不变。
2. Hard Stops：无全库格式化、历史模块重建或凭据读取/输出；没有发信、发布或交易。
3. Dead Code：无新增无人使用的运行抽象；旧合同分支由真实冻结恢复使用，不能删除；旧实验固定其旧版本。
4. 范围：单一“经济去重与资本桥审计”改动；独立工作树避免夹带原 checkout 修改。
5. ADR：新增内部审计接口已先记录版本与兼容矩阵；无 adopted handoff，不误称生产生效。
6. 测试：先失败再实现，定向、完整离线 runner 路径和全套回归通过；语义判断与真实模型 API 未被单元测试替代。

## 7. 正式来源与生产边界

先前两份只读审计的 source_manifest 共 **22 条、42 条记录均哈希未变**（记录间可有重合）。其中：

- `investment_prediction.csv`：`f5c67e227600e92ee2a37a22b42362f294559043937f1ad30280feafd6fca18a`。
- `data/model_quotes/current_quotes.csv`：`d2ead6df7fe0985c6d0b9d00c91a7568880b05963ec02afceb32d029f49cdbd4`。

原 methods 规则、程序与被核报告也与先前清单一致。没有运行 latest 重建、正式研究封口、生产报价写回或采纳命令。工作树产物不在生产 companies/ 或 exchange/，不会成为正式报价来源。生产 checkout 保持原状；新方法今后进入生产需要独立发布/采纳步骤，本任务没有执行它。

## 8. 精简版同步：七项自审

本次是获准的方法优先级修订，不声称新旧方法完全语义等价。canonical 为唯一经济定义；compact 只同步其执行条件，未另设阈值。

| 核对项 | 实际检查和结果 |
|---|---|
| 有效内容覆盖 | 受影响 §1.3/§3.4/§4.1B/C/§5.6/§6.3/§6.6 的触发、动作、例外、解除逐条对照；未改原 Gate/cap/持仓限制，增添价格动作优先级 |
| 数值与公式 | 对照 diff 保留既有 ≥3pp、仓位下降、油价压力及其它阈值；新增 T/U 三值解释、资金桥与审计公式。旧剪刀差行的 2026-09-12 是条款修订尾注，被本次修订记录承接，不是删掉有效比较窗口 |
| 稳定引用 | R1–R22、D1–D8 各定义一次，无重编；canonical §4.1B/C 与 compact §7 对应，governance 通过 |
| 三条自包含抽检 | ① true/unknown/false 三取二为 unknown，不能加已触发罚分，缺证资格仍在；② 成本弱/现金流差 true，第三项 unknown，联动成立，已入利润的同损失不得再折扣，cap 保留；③ 经营价值 100、未含融资现金 20、为已预测经营利润所必需且未扣的投入 5，则合计 115，股数同步发行后，不能给 120 或因用途未知直接给 100。三例仅演示逻辑，不设投资参数 |
| 副本矛盾 | 全文“上调/取上沿”以全局去重优先；叙事不再无条件双扣；unknown 不被改写为 false。原有历史状态按日期保留，未以新日期冒充新市场观测 |
| 决策链 | 数据契约→Precheck→机制→Gate→估值→Terminal→Price Map→结论仍完整；新桥放在估值阶段、风险归属传入 Price Map，资格与持仓链独立 |
| 体积与范围 | UTF-8 计量见下表；增长来自获准的新规则，未扩大交易/市场范围；观测 JSON 块与 HEAD 原字节相等，当前观测仍截至 2026-11-08 |

| 文件 | 字节 before→after | 行数 before→after |
|---|---:|---:|
| canonical | 112,260 → 118,773 | 811 → 854 |
| compact | 74,861 → 79,075 | 534 → 548 |

最终文件 SHA-256、方法指纹和 before/after 记录在 validation-summary。结构自审与定向语义抽检不证明所有投资规则有效，也不解决两家公司缺失的经济参数。两家公司后续有补证时，应重新裁决受影响参数和资格；不得自动提取本报告敏感性数字为报价。
