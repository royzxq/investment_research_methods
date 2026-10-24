# 股票周更方法与接续审计（2026-10-25）

审计范围：只读核验本 worktree 的 `origin/main=c9ce8d8af2f5a61bb0471e1ccfd32b2e1501316f`、现行两份框架、股票维护契约、10/18 adopted handoff-r2；另只读检查原主目录的公司产物。没有联网市场取证、改写框架或 handoff，也没有执行交易。

## 合并及方法身份

| 节点 | canonical 全文 SHA-256 / 方法指纹 | compact 全文 SHA-256 / 方法指纹 | 判定 |
|---|---|---|---|
| PR #45 `f1458994fbf9c7413e7fa8d785cc50a38f6bce45`，handoff-r2 冻结方法 | `b26daf1d3cc601e34682effbe46bb88b064190410de94886546fce7a79378a3a` / `96dd548640117d9de7377a7193c9f3179f8b65cdadb4d2bd68e062f50832b4ca` | `7c588fba94eb81f9629fe22f6266243c31121e44384ec7a1785c330c7231ada8` / `1cf307a6af8168fc0375625a6cc30e96398cd75916402f665cd593d7a260631f` | handoff-r2 所用旧采纳方法 |
| PR #48 merge `88e8d6659d6d9e9c14f57721ce8c1414ecf81221`（2026-10-18） | `496d51dd9fb42f3b56eb064baf1d2fb2a40fffe0e8ef75182636cd40cd24e170` / `96dd548640117d9de7377a7193c9f3179f8b65cdadb4d2bd68e062f50832b4ca` | `cef42ee91e39c8181438d3eb506e1965f380b54e495830c26aa2aaec1791921b` / `1cf307a6af8168fc0375625a6cc30e96398cd75916402f665cd593d7a260631f` | 受限 observation 块更新；方法指纹一致 |
| PR #50 merge `6f797ed9223225b68b97db7f7dc9e2cc1c44ab43`（2026-10-19） | `559d2ab77954743c1e5daed6b0293f2c7e5f039752e628b01a67ef0bdaf602df` / `10d9c1ef0d7a33f1775604e279c2be0f1e8759c0164b219621b06a92c7a25d3c` | `2f6c18003d792708ca019c9302dee446094614af7147f1c57bb13c806485ca2d` / `fc12a8ee74b1a219ebad797795eb23265a01c04b28df789cb74c73423eebf2af` | 两价方法实质变更 |
| PR #51 merge `346caada9172b4346c6b9246cb66978b06024ba4`（2026-10-20），现行 `origin/main` | `773677164aee09f006d80afda8e7484f00b05a489061903754b7f76ffec78ed7` / `1ba69fd41b54c45a3b1109a1532b9a51f9a9e65026723af6439a2267d0747f0f` | `57d9a8e4530e32e53a5d06ab80dc7244d3dc67fd28d95951890dc68c25453ea2` / `e38a4400f41f7991170767d145de4b1501050972a2b3d71ec11590114ce84b5f` | 控制生命周期与风险解除语义也变更 |

`method_fingerprint` 仅排除通过严格结构验证的唯一事实观测块；#48 的相同指纹支持接续旧方法的状态。#50/#51 两份指纹均不同，且正文实际取消 P2/T2 与 P2 步长，买入研究只保留 P1/T1；加仓约束、逻辑失效、减仓复评和退出独立于报价。冻结但事实可靠时可有观察 P1/可论证 T1，真实硬失败或核心估值事实不足不得补造价格。持续限制按 scope 与稳定 ID 接续，未触发信号只是 observation，纯现价门槛是 runtime；缺证不自动解除限制，holding-only 未知不自动扩大到 entry/add。确认失效/退出阻断新增，风险收紧不因报价失败而消失。这些变化超出纯观测兼容范围。

## 旧交接的可继承范围

`investment-2026-10-18-handoff-r2.json` 的 SHA-256 为 `6365b7cd72261aab9d3e8e201a9ff8afcc59e106928073d3c160d477f1e7240a`；`status=adopted`、`method_status=adopted`、`method_change=false`、`supersedes=[investment-2026-10-18-handoff]`。`validate` 通过来源与结构检查，不证明金融语义。它明确撤回 10/11 旧 change-decision 身份：`06b59f529cf18cbfe55c08dffe10ca99ecb8c75ed5fbba6678e43fe681b2187a`，不得在新方法下重新作为有效决策来源。旧报告的历史事实仍可在真实日期内重新核验。

截至本审计，`python3 scripts/investment_maintenance.py select --date 2026-10-25` 返回 `null`。原因是 handoff-r2 冻结的两份方法指纹与现行主线均不相同，且 `compatibility=[]`；不能因其曾被 adopted、#48 已合并或文件较新而将它选作当前 adopted handoff。#48 的合并事实只支持当时状态块与当时方法兼容，不覆盖随后 #50/#51 的方法变化。

保守接续方案：先用 `origin/main` 上 #50/#51 的实质规则，按本期证据重新评估受影响观察、触发及各 scope 控制；将 10/18 的行情/事件仅作带日期的历史证据。若形成本期 adopted handoff，冻结现行 canonical/compact 两份原文并绑定上表现行完整哈希和方法指纹；明确 adoption_basis 为已合并主线方法与本期状态采用依据，显式 supersede 旧 r2，逐项承接五条 pending 和撤回来源哈希。跨方法结论若要直接继承，另写逐项 compatibility review，核阈值、逻辑、对象、动作、例外、解除和两价/风险合同；没有审查即按当前方法重评。不可把旧 handoff 修改成新方法，也不可把旧完成凭证补填为今天的产物。

## 原主目录逐股凭证

只读遍历 `/Users/xinquanzhou/Workspace/investment_research_methods/research/investment/companies/<日期>/<证券>/`：

| 旧 pending | 可见公司产物 | 本次结论 |
|---|---|---|
| `SZ-300308`，`R6/S5548-named-exposure` | 无该证券目录/正式配对 | pending；需实际暴露与立法进度核验 |
| `SZ-300502`，同上 | 无该证券目录/正式配对 | pending；同上 |
| `SH-600276`，`Precheck2/Hengrui-settlement` | 2026-10-09 的 Codex 与 Claude 各一份 v3 报告/JSON 配对 | pending；报告在 `evidence_cutoff=2026-10-18` 之前（原触发日9/29，不将10/18识别日改为触发日），使用旧 P2 语义，不能覆盖本触发；需 10/18 后定向 reassessment 与跨方法审查或新完整报告 |
| `HK-01276`，同上 | 无该证券目录/正式配对 | pending |
| `HK-09926`，`Precheck2/Akeso-income-attribution` | 无该证券目录/正式配对 | pending；需康方实际经济权利/入账核验 |

恒瑞旧 v3 报告确有 Novo 待 Q4 交割等分析，证明曾被研究；其 `meta.valuation_date=2026-10-09`，不证明覆盖10/18接续证据并按现行方法复核完成。五条均无满足 handoff 契约的 completion refs、覆盖触发的 evidence_cutoff、必要时的 compatibility_review。不能将元研究、旧报告存在或触发本身记为 completed；也不推断公司从未研究。维持 pending，不重置个股冷却期、不发起公司批次。
