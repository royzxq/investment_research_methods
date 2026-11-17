# 中性校准方法与验收独立审阅

日期：2026-11-17（Asia/Shanghai）

结论：发现 1 项可复现的期间完整性问题（P2）；未发现本次文本修订强迫提价、为贴近 DSH 调参、自动撤回有界估值，或改变旧 v1–v9 冻结合同的证据。终值 IC 对账和敏感性实际复算仍属人工核验边界，不能把结构检查通过称为经济对账通过。没有发现 P0/P1 问题。本审阅不评价任何公司的报价是否合理。

## 范围与独立性

按 stock-research / deep-research-auto 的独立核验职责，只读当前 canonical §4.1D、compact §7、`research_neutral.py`、`research_consistency.py` 新 schema 路由与相关计算入口、runner v10、对应 reference、测试与指定 pre-change 副本。为确认输入约束按需查阅了 `stock_price_map.py` 的数值范围校验。未读取本轮六个实验的公司新报告、模型或价格，未改变框架、代码、测试、冻结快照及公司产物。唯一落盘文件是本审阅。

## 发现：P2，资本桥可倒序接续并通过验收

- 位置：[research_neutral.py:55](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_neutral.py:55)，特别是 57–68 行；契约对应 [research-consistency.md:40](/Users/xinquanzhou/Workspace/investment_research_methods/.agents/skills/stock-research/references/research-consistency.md:40)。
- 当前实现将 `period` 仅当非空字符串及去重键，随后按列表顺序检查前行 closing 与后行 opening。它没有检查期间的时间顺序。
- 已用现有 `tests/test_valuation_neutral.py` 的 `current()` 合成 fixture 复现：设置 `status=reconciled`，第一行 `period=2028, opening=100, capex=25, da=10, other=0, closing=115`，第二行 `period=2027, opening=115, capex=25, da=10, other=0, closing=130`，相同 scope；`validate_audit` 正常通过。算术在列表中连续，但经济时间倒序，违反现契约“同 scope 按时间顺序”的明确要求。现有测试只覆盖金额断接和单行不平，见 [test_valuation_neutral.py:45](/Users/xinquanzhou/Workspace/investment_research_methods/tests/test_valuation_neutral.py:45)。
- 影响：录入顺序错误可被标记为 `reconciled`，掩盖资产先后关系，尤其在投入期资产增减与终值资产接续时造成误读。这不是直接改写 V50 的程序漏洞，但属于本次新增完整性检查可以且应当发现的错误。
- 最小修复：保持原 `period` 字段，在下一次未冻结版本中明确支持的年度/季度记法，并按 scope 检查严格递增；不要自动排序后声称原记录无误。补倒序、同年季度倒序与正常多 scope 的边界测试即可。不新增金融阈值、估值模型或 schema 字段，不自动将报告判为不可估。当前六个实验已冻结启动，应在实验后的修订中处理，不能改运行中快照或重新解释其输入。

## 人工核验边界，不列为新增阻断问题

**终值 IC 未与资本桥数字绑定。** [research_neutral.py:43](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_neutral.py:43) 只对 `terminal_reconciliation` 检查非空文字；资本桥的数值行只核行内算术和列表接续，不与 DCF 的 CapEx/DA、分部或终值 IC 自动连接。使用现有合成 DCF、终值 IC=150，填写同范围期末资产为 0、并在对账文字声称“0+0+0=150”，完整 `render_report_block → validate_report` 仍可通过。这证明的是当前机器核验边界，不证明真实模型存在该错误。现 reference 本就将资本范围与原始证据留给人工复核，故不将这一点描述为旧合同失效或必须加字段的缺陷。

本轮最小处置是按报告实际模型逐项复核“期末生产性资产 + 期末 NWC + 其他生产性资本 + 明确范围调整 = 所用终值 IC”，并检查 CapEx/DA 的模型口径与桥表差异；不能仅凭 `status=reconciled` 或审计 passed 下结论。以后若实际错误反复出现，再考虑在保留字段的前提下约定可解析对账格式或复用模型底稿计算，不必现在扩建一套资本系统。

**敏感性只核基准及差额。** [research_neutral.py:85](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_neutral.py:85) 确认 base 绑定最终 V50.base、delta 等于替代值减 base，不会执行 `calculation` 文本。具体替代路径是否真正复算、是否固定了应固定的假设、现金流/资本成本是否双重收费，须核实际模型。当前契约已明确这一限制；不要求为了格式强造可量化值。

**更早证据截止。** [research_neutral.py:26](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_neutral.py:26) 的日期上限是估值日；reference 39 行另要求遵守更早实际证据截止。本轮固定证据包实验还需人工/既有证据链按其原截止核验，不能只用这项检查替代。此为现接口不持有更早截止的边界，本次未向报告加入新字段或建议改运行中合同。

## 已确认的保留条件

- [canonical:672](/Users/xinquanzhou/Workspace/investment_research_methods/framework/investment_framework.md:672) 与 [compact:561](/Users/xinquanzhou/Workspace/investment_research_methods/framework/investment_framework_compact.md:561) 均明确不以提高报价或贴近另一模型为目标，并对乐观和悲观联合假设对称要求依据；没有固定倍数、统一加价或强制取区间均值。
- capital bridge 的 `unavailable` 本身不取消 V50；有依据但不精确的参数可保留 bounded/观察估值。不能量化的敏感性可保留 null 并解释；没有发现因这两类正常缺口必须撤回价格的新门槛。
- V50 有值而 P1 留空仍须做中性校准；V50 留空仍接续原 availability review。现有公司硬否决、freeze、entry/add/holding 作用范围没有被新复核自动解除。
- 新 v10 强制 audit-v7；旧 audit-v6 不被追补 neutral_review。旧 v1–v9 的已冻结 prompt/input 不被本次默认升级重写。

## 实际验证

全部为离线合成 fixture，没有公司估值，也没有真实 API 验证。

| 验证 | 实际结果 |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_valuation_*.py' -v` | 32 项通过，含 v5/v6/v7、可用性、现金税、终值 IC 与中性校准边界 |
| `python3 -m unittest discover -s tests -p 'test_research_consistency.py' -v` | 23 项通过 |
| `python3 -m unittest discover -s tests -p 'test_research_runner.py' -v` | 104 项中 102 项通过，2 项环境错误；不是全通过 |
| 逐合同比较 pre-change runner 与当前 runner 的 `make_prompt` | two-price/v1、controls/v2–v9 共 9 个合同，在同一合成输入下生成字节完全相同 |
| 上述倒序资本桥反例 | 当前验收接受，确认发现 |
| 上述终值 IC 文本矛盾反例 | 当前验收接受，确认人工复核边界 |

两项 runner 环境错误是 `test_sigterm_to_runner_cleans_children_and_records_failure` 和 `test_timeout_kills_descendant_that_ignores_sigterm`，分别在 [test_research_runner.py:1584](/Users/xinquanzhou/Workspace/investment_research_methods/tests/test_research_runner.py:1584) 和 [test_research_runner.py:1566](/Users/xinquanzhou/Workspace/investment_research_methods/tests/test_research_runner.py:1566) 调用 `ps` 时遇到沙箱 `PermissionError: Operation not permitted`。没有据此推断子进程清理通过或失败，也没有请求扩大权限。`test_v1_to_v9_frozen_recovers_under_new_default_without_rewriting`、新 v10 拒绝 v6 审计及历史 prompt 字节检查实际通过。

未发现其他已证实的兼容性回归或不必要拒绝路径；这不等于穷尽所有输入。经济中性、真实来源、六份实际公司模型的资本衔接与重复计价需交由本轮公司报告验收，不能由上述结构测试替代。未获得可归属本子任务的 token 用量。
