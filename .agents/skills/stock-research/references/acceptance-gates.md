# 共享证据与恢复验收（stock-research-acceptance/v1）

本契约落实现行 canonical 的 R14 必要证据和独立约束合取要求，不改变投资方法、阈值、价格、共识或执行许可。`stock-research/v4`、`stock-research-audit/v2` 保持原 schema；报告新增唯一共享验收块及程序生成的可见表。新冻结合同为 `two-price-controls/v3`；已冻结的 `two-price-controls/v2`、`two-price/v1` 和旧 v3 仍按各自合同验收，不改写历史与原始实验。

## R14：缺证不能判通过

先按 canonical 判断适用性、三层暴露、同口径油价情景与具体处置。100→130、升降档及资源受益者 85 美元对称情景等仍以冻结 canonical 为准，本契约不另造统一成本比例、OCF 期限、折扣或硬失败判据。

在报告的 R14 分析中，逐项说明公司暴露、成本敏感度、传导/套保及现金流预测桥接。敏感性算得为正，不能代替必要公司依据。特别是成本占比、传导区间或 OCF 基数仍不可约束时，不能以自设 5%–12%、0%–40%、OCF≈800 一类任意假设，证明公司的强制测试已通过。假设情景仍可用于研究，必须标明其证据边界。

共享块字段：

- `schema_version="stock-research-acceptance/v1"`。
- `r14={applicability,stress_test,constraint_ids,reason,inputs,calculation}`。适用性为 `applicable/unknown/not_applicable`，压力结论为 `passed/failed/unknown/not_applicable`。适用性未知只能交付 unknown；确有理由不适用时填写理由，不能借此解除历史 R14 主张。
- `inputs` 精确含 `exposure,cost_exposure,pass_through,ocf_bridge`；每项为 `{status,sources,derivation}`。`status=supported/bounded/assumption/unknown`，分别表示有依据的输入、有来源约束的估算区间、纯情景假设、未知。直接披露不是唯一合法输入：可使用公司事实支持且可复现的保守边界或预测桥接；`bounded` 必须写推导。现金流桥可为有依据的定性生存性/融资检验，不强制新的数值预测或 OCF 必须为正的统一门槛。不能把任意假设改标签冒充有依据。
- `sources` 为原文或原文 UTF-8 摘录的定位列表，每项 `{path,sha256,quote,as_of}`，路径相对本次校验根目录、hash 对应完整文件、quote 为精确原句、as_of 不晚于估值截止。PDF 保留原件并保存可回查页码/出处的文本摘录；报告说明摘录与原件的映射。程序核字节/hash/引句与日期，不证明摘录来自真实公告或该句足以支持推论。网络 URL 可在原文底稿中保留，单独 URL 不能替代已读取证据。
- `calculation=null` 或 `{scenario,report_quote}`。非 null 时，quote 必须精确定位报告正文的压力计算，不能只在验收 JSON 中自我引用；scenario 写本公司适用的现行 canonical 情景。计算口径、期间、币种、税盾和对冲效果继续由研究者核验。
- `passed` 只允许全部必要输入为 `supported/bounded`、均有可读取来源且存在压力计算时声明；这只是完备性与绑定验收，仍须核原文、推导和经济含义。`failed/unknown` 必须以 `constraint_ids` 绑定本次实际 R14 的持续 add 限制，约束 reason 明写 `R14`，不用无关 D5 限制代替；unknown 不自动升级为硬失败。scope 按规则判断，不因仅加仓缺证机械冻结首笔。失败处置继续执行 canonical，不由检查器代定折扣。

## 恢复：按 scope 解除全部有效独立约束

`recovery={operator:"all_of",scopes:{entry:[],add:[],holding:[]}}`。每个列表须精确列齐 audit 中该 scope 全部 `blocking/unknown` ID，并与 `release_all_of`、`research_controls.refs` 一致；不能按多数、部分、至少若干项或任一独立约束已解除就恢复。只解除部分时，剩余限制继续有效；旧主张的 evidence/covers 解除检查继续生效。

单条规则内部原有的且/或、例外、合法替代路径完整保留，例如 D5 的路径选择不能被改写成全部路径都须同时完成；它也不能替代其它独立限制。holding-only 复评、未触发观察和纯运行时价格条件不自行扩大为 entry/add 持续债务。没有未解研究约束，也不表示已满足价格、账户或执行条件。

正文和完整条件表必须与上述恢复逻辑一致。程序拒绝“大部分约束解除即可恢复”“上述 1–5 项至少大部分解除”等明确子集放宽；模糊表述先改为逐 scope 的完整条件。自然语言检查属于保守反例拦截，不能证明任意措辞的语义完整；研究者仍须审查正文、来源和规则内部逻辑。不要把错误旧例整段留在当前恢复指令内；如须说明纠错，明确写“不得/不能”，并保留原始报告在独立历史文件。

## 生成、回读与兼容

先保存报告、audit JSON、验收 JSON 和相对根目录的证据，再生成可见表和块；将输出插入同一报告。不能改价来满足门禁。

```sh
python3 scripts/research_consistency.py render --root <校验根目录> --price-map <本次价格JSON> --audit <audit.json> --acceptance <acceptance.json>
python3 scripts/research_consistency.py check --root <校验根目录> --price-map <本次价格JSON> --report <本次报告> --require-lifecycle --require-acceptance
```

新 runner 在正式发布前两次检查均按冻结 v3 合同强制新块，失败沿用原有最多一次输出重试，保留失败草稿与回执。即使未传强制参数，显式带新块的报告也必须校验该块，不能悄悄忽略。方法隔离派生版按新 audit 同步恢复列表，保留原始报告。

隔离评测复用同一模块：`research_experiment_contract.py render` 可带 `--acceptance`；`check --require-acceptance --root <隔离工作区>` 强制新门禁。旧实验按原冻结合同和原脚本读取；严格复验另存新回执，不覆盖旧报告、分数、费用或结论。门禁通过不使实验进入正式自动化或共识。
