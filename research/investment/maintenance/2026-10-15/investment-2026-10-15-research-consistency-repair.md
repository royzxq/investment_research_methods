# 自动个股研究一致性修复及宇通同证据复评

日期：2026-10-15，Asia/Shanghai。用户明确要求把利润链、冻结一致性和折扣去重问题修复到自动流程，并复评宇通、对比前后价格。本次本地实现和研究，不发布Git、不改账户或执行交易。

## 实现与生效范围

新增 `scripts/research_consistency.py`，审计输入位于报告内，不扩展最终轻量 `stock-research/v3`。程序只核验、拒绝矛盾，不更改明确报价。`stock_price_map.py`继续忠实导出P1/P2，独立保留原结构/状态校验。

`research_runner.py`新准备批次在不可变快照中记录 `research_validation=stock-research-audit/v1`，并复制最近本端正式研究原文为折扣基线，绑定路径与SHA。新提示词要求读取本轮一致性reference。发布前核算一次；方法兼容性待复核隔离后，同步派生报告的状态审计并再次核算，原暂存报告、JSON与回执不改。最终回执绑定实际发布报告/价格SHA。失败进入原有最多一次输出修正机制，未通过不发布，不覆盖既有生产结果。

已准备的旧批次继续其冻结契约；旧封口仍可读取，不谎称通过新门禁。本次实际只读验证原10/15批次16个端点的prepared输入，全部可按原字节接续，新契约没有追溯注入。未来新准备批次必须经过新门禁。

本机已安装plist的WorkingDirectory为本仓，入口指向本仓 `deploy/launchd/run_research.sh`，由其启动新的Python调度进程；现有排期为05:00，RunAtLoad=false。新代码将在该本地入口下一次新准备批次时读取，不需要重装服务；本次没有改排期/模型配置，也没有触发一次真实双端生产研究。未提交代码不代表远端/main已部署。

## 门禁覆盖

| 问题 | 行为变化 | 实际边界 |
|---|---|---|
| 利润断链 | PE情景统一输入收入、经常归母率、有来源调整、利润、PE、权益、实际股数与汇率；逐项校验到V50及明确P1 | 不替代正常盈利/PE的经济论证；调整来源内容仍人工核验 |
| 正文与计算表漂移 | 程序生成唯一可见经营核算表，与报告内JSON审计及价格文件逐字/数值核对 | 不理解报告其他自然语言；禁止另一套经营数字表仍需主代理语义验收 |
| 冻结被改名 | 声明的有效freeze必须对应frozen或更严格状态；frozen/rejected/unavailable反过来须有对应未解约束 | 约束适用性/实际证据真伪由研究者裁决 |
| 任一解冻 | release_all_of必须包含全部仍有效/未知阻断；R9补齐不能替代D5或R4 | 不自行从source字符串抓取市场数据 |
| R21误恢复 | D5适用时声明clearance阶段；waiting_review不能标clear，只有重建及公司复评完成且有引用方可clear | 阶段引用是否真实仍须回原文/市场证据 |
| 自行重定义上沿 | 冻结同端原报告；已有审计参数与区间变化须分类、理由和引用，不能静默标unchanged | 首次研究/旧未提供参数允许initial，不创设通用折扣常数 |
| 重复扣减 | 风险ID只有一个盈利/倍数/资格/折扣owner；非零折扣必须独占风险，已进模型或资格的同ID不得再收费 | 异名实为同一损失，需审查scope和现金桥，程序不夸称自动理解经济同义 |
| 非PE与历史兼容 | other显式提供未舍入V50，避免从已舍入JSON重算导致误拒；旧不可估未给折扣可显式null | 不允许以other伪装PE绕过，方法适用性仍人工；已有审计值不能再丢为null |

同步修改repo `stock-research/SKILL.md`、`valuation-and-output.md`，新增 `research-consistency.md`，并更新research导航与项目状态。canonical/compact未改，没有新增投资阈值或折扣档位，故不将本次技术契约变更冒充方法周更/采纳handoff。

## 宇通复评与前后价格

固定原数据包、框架和原批已用公开证据，价格为2026-10-14收盘27.13元。当前宿主Codex完成增量复评，财务/现金与Gate/折扣两个独立后端任务直接回原文；最终主代理复核并裁决。未新增市场读数，也没有实际调用Claude端重研。正式r2报告完整九节、来源/假设、风险去重、现金桥、Terminal、10项监控及审计输入齐备。

| 字段 | 原Codex | 本轮Codex r2 | 原Claude端（历史对照） |
|---|---|---|---|
| V50低/基准/高 | 16.26/25.64/35.66 | 16.26/25.64/35.66 | 17.16/25.97/33.47，利润链未闭合 |
| 最终P1 | 17.78，单价 | **18.33，单价** | 13.17/19.92/25.68 |
| P2 | cancelled/null | cancelled/null | suspended/11.85 |
| 用途 | frozen | **observation** | tracking，正文从紧冻结的历史冲突保留为纠错依据 |
| T1/T2价格引用 | 接近/明显高于V50上沿 | 同原，上沿35.66 | 上沿33.47 |
| d/chip/v5/gov/terminal | 20/2/5/4/3% | **20/2/5/4/0%** | 15/5/5/0/0% |

本轮保持47.30亿元正常利润与12倍PE：原Codex430×11%=47.30亿、×12=567.60亿算术正确，仍属可解释的保守假设，不为贴近手工稿而换利润或倍数。删除3%终局项，是因为成熟盈利/保守PE未另资本化高成长终局，未找到该项独立额外损失机制。其余参数沿用并重划独占风险，不将R9未知当高拥挤，不把已含在期末现金中的历史OCF再加一次，不把普通质保在利润/未来OCF/现金桥重复扣。

总折扣乘数0.69355776→0.715008，P1增加0.55元、约3.09%。价格变化来自残余风险去重；frozen→observation则来自用途推断纠错：输入只是财报触发，未证明属于低位价值轮动承接，不能自动套D5。它不是宣布市场承接池解除，也不是买入资格恢复；R9、R4等约束仍未闭合，P2继续取消。未来用于低位轮动须另按D5/R21/原重建与逐股复评。

原Claude405×11%应为44.55亿，另两档也应为35.15/51.60亿；其估值表40/50/57亿没有桥。只修该利润链、保留其PE/折扣所得17.75元为诊断，不是本轮Claude正式新报价。手工22.4—25.6元也只是20%折扣敏感区，并非完整P1；不把三者平均成新推荐价。

保留原四份正式报告/JSON及原latest，实际对照SHA均未变化。新配对使用同日 `-codex-r2`，不自动提升latest或回写生产价格。`before-after.json`直接从实际价格文件回读，含原件哈希及变化归因。

## 验证记录

- 一致性专项当前12项：利润/权益/股本错链、有来源调整、同ID重复收费、冻结隐藏、遗漏阻断、R21等待不等于完成重建、基线值/区间漂移、历史缺参数、非PE未舍入价及重复/非有限JSON边界。
- runner离线真实子进程验证新契约发布前拒绝错误利润、隐藏冻结和缺审计；新基线与方法隔离接续保持原报价和原材料。最终完整离线回归 **785项通过，93.797秒**；本轮 `research-validation.json` 同步记录实际结果。
- 旧prepared原批16端点只读兼容核验通过；公司r2九节结构、原文指纹、`stock_price_map.py check`、新一致性检查通过。skill quick_validate与股票框架结构治理检查通过。
- 独立行为验收28个CLI样例，区分合法通过、机械拒绝及故意语义违例仍可通过，详见forward-validation笔记。之后主代理补上D5阶段机械约束，专项回归覆盖；不把早期独立笔记中的语义绕过一律称为当前都可通过。
- Jev实际提交原始候选后首次超过字符预算，按回退要求直接读原文；再提交精确必要页，程序返回declared_precise_location，后端调用0。两次路由日志与不可变首次summary保留，最终汇总为`routing/jev/final-summary.json`。
- 未执行真实研究CLI双端重跑、真实财务取数API、账户/交易验证；不修改原研究模型标签或模型配置。

实际命令：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/investment_framework_governance.py --check
python3 /Users/xinquanzhou/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/stock-research
python3 scripts/stock_price_map.py check research/investment/companies/2026-10-15/SH-600066/investment-600066-2026-10-15-price-map-codex-r2.json
python3 scripts/research_consistency.py check --report research/investment/companies/2026-10-15/SH-600066/investment-600066-2026-10-15-research-codex-r2.md --price-map research/investment/companies/2026-10-15/SH-600066/investment-600066-2026-10-15-price-map-codex-r2.json
```

## 文件与限制

- [复评报告](../../companies/2026-10-15/SH-600066/investment-600066-2026-10-15-research-codex-r2.md)与[价格JSON](../../companies/2026-10-15/SH-600066/investment-600066-2026-10-15-price-map-codex-r2.json)。
- `output/stock-research-SH-600066-2026-10-15-codex-r2/`：冻结输入、财务与Gate独立证据、forward-validation、研究审计输入/核算展示、验证回执、前后JSON比较和完整run-manifest。来源与核心推导直接在正式报告，不要求读临时材料才能理解估值。
- 最终门禁证明的是已声明算式、风险ID、状态阶段与集合一致，不是原文真实性、全部自然语言一致、假设准确或投资方法有效。仍需主代理检查模型类别、经济同义风险、D5用途、旧参数摘录及真实解除证据。测试数量不代表已验证投资收益。
