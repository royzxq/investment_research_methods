# DSH与CC隔离配对评测 v2：宁德时代

研究截止：2026-10-21；实验日期：2026-10-22（Asia/Shanghai）。

**已完成执行与共享交付修复、两轮同模型冻结输入配对、全仓测试和独立代码审查。现有投资方法、正式自动化、共识规则及历史产物未改。**

第二轮DSH盲评分数略高，但两端仍有重要控制语义缺陷；各自仅1/2轮自然完成。唯一完整费用轮中DSH贵约52.29%，没有本轮成本优势。结果不足以证明DSH可以无劣化替换CC，保持隔离用途。所有失败、未知用量与原始输出保留，没有为评分重跑或事后修好报告。

## 1. 研究质量：分数略高不等于达到替换标准

两位独立上下文的 Codex 代理先匿名评审四包，再锁定原始分数与文件哈希，最后解盲。评审前不提供身份、轮次、费用、耗时、运行日志或旧评分；副本只归一自身路径和显式品牌名，不改变经济数字。原件/匿名副本数值相同，两份完整产物的契约检查结论也相同。不是人工评审或统计非劣性证明。

| 轮次 | CC双评总分 | DSH双评总分 | 研究交付 |
|---|---|---|---|
| 01 | N/A / N/A | N/A / N/A | 两端只有JSON，报告未交付；仅交付分为0，不把缺失报告当0分研究排名 |
| 02 | **77 / 76** | **80 / 79** | 两份九节报告及JSON均通过共同结构/算术契约；语义仍有重大问题 |

| 第二轮分项（评审1 / 评审2） | CC | DSH |
|---|---:|---:|
| 事实 /30 | 26 / 25 | 26 / 25 |
| 覆盖反证 /20 | 17 / 17 | 17 / 17 |
| 估值算术 /25 | 18 / 18 | 20 / 20 |
| 控制 /15 | 7 / 7 | 9 / 8 |
| 交付 /10 | 9 / 9 | 8 / 9 |

核心财务、期间、股数及PE→V50→P1主链大体可核算。DSH本次估值论证得分略高；两端均遗漏已提供的关联铜采购及未来预付承诺，近期回购和两基金覆盖也不完整。不能因为P1高低或接近旧报告程度给分。

**CC的重要问题：** R14以未证明上界的油链成本占比与年度OCF假设宣布压力检验passed，未保留该项必要add缺证；两位均判“必要未知当通过”，root回冻结规则确认。税率方向也错误：原PDF的有效税率约14.23%，低于25%时成本冲击税盾更少，税后损失应更大，报告反称更小。还有独立订单资格缺口被其他freeze掩盖、风险折扣监控方向等问题。这是研究验收错误，不是已证明公司真实油价情景OCF为负。[CC原报告](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/trial-01/runs/research-02/cc/workspace/outputs/report.md:422)

**DSH的重要问题及分歧裁决：** 最终恢复清单一面要求同时满足，一面在第7项写第1–5项“大部分解除”即可继续；与canonical及JSON中全部未解持续约束均须解除冲突。评审1判控制解除硬失败，评审2保留为重大未来语义错误，因为当前JSON仍frozen。root按预定协议回原文裁决：确认**评测层面的解除控制硬失败**；评价的是交付的恢复规则，不要求真实交易发生。当前JSON确实仍blocked，不能据此声称系统已经解冻。两人原分与原分类均不改写。DSH另有Terminal期限/近似量纲、市场代理口径及部分风险分类问题。[DSH原报告](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/trial-01/runs/research-02/dsh/workspace/outputs/report.md:1029)、[冻结解除规则](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/trial-01/frozen/.agents/skills/stock-research/references/research-consistency.md:82)

每位评审均核15组事先冻结事实。额外固定seed引用抽查未达8项：CC分别2/3项，DSH两人均0项。DSH正文多用Q3/H1缩写页引，固定候选筛选仅收2行书目/标题；没有临时换样或把0项解释为全文无引用。该筛选覆盖不足限制了额外引用验证强度。

[评审1](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/blind-review/reviews/reviewer-1.md)、[评审2](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/blind-review/reviews/reviewer-2.md)、[分歧与原文裁决](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/quality-review-resolution.json)、[定向原文/算术核验](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/primary-source-checks.json)。

## 2. 实验条件与执行修复

沿用原估值日2026-10-21、59份冻结输入及现行 canonical，未改投资阈值、共识规则或历史文件。修复仅涉及独立故障/预算门禁、完整上游用量留存、私有 PDF/图像运行环境，以及按原规则明确 R14、Precheck、D5/R21、币种、持有复核、折现方向和报告/JSON一致性的共享交付与离线校验。原输入与新增执行材料分开记录，详见[实验manifest](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/trial-01/manifest.json)。

两轮使用相同提示词、全新会话，启动顺序交替。主/子代理统一 Flash/high、输出上限32768、每端总时限2400秒；180秒参数在DSH对应流空闲、在CC对应请求超时，语义不同；独立1000请求/50美元门禁，禁用外网及服务端搜索。671个生成请求均指定 `deepseek-flash`；669个带模型标记的响应均为 Flash，另2个连接失败未观察到返回模型。CC原生辅助调用使用2112上限且不带effort；DSH请求为enabled/high，CC主/子为adaptive/high。这些原生差异及辅助费用保留在对照中。[运行配置与指纹](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/trial-01/runs/research-02/configuration.json)

实际测试的是 CC2.1.296 与 DSH CLI0.2.1-rc.2 的 headless/base，未验证 Desktop GUI Standard。已记录 CC二进制、DSH入口与package.json指纹；没有对DSH完整依赖树作整体指纹，也不能由模型别名证明后端权重版本固定。

## 3. 自然完成、工具与生成费用

| 轮次 | Harness | 自然完成 | 秒 | 生成请求 | CNY生成估计 | USD生成估计 |
|---|---|---|---:|---:|---:|---:|
| 01 | CC | 否，取消 | 917.787 | 94 | 已知1.277998＋未知 | 已知0.191700＋未知 |
| 01 | DSH | 否，取消 | 917.553 | 123 | 已知1.439871＋未知 | 已知0.215981＋未知 |
| 02 | CC | 是 | 1078.655 | 230 | 3.847186 | 0.577078 |
| 02 | DSH | 是 | 1057.446 | 224 | 5.859057 | 0.878859 |

第一轮每端各1个URLError、2个TimeoutError导致3条未知usage，触发各自门禁；时间、请求和预算均未耗尽。故障集中于09:04前后，共同服务、网络或连接层因素的归因未定。随后每端1个ClientDisconnected已收到完整上游usage，仍计费，不是第四条未知。13条无arm的本地404全部未转发，生成费0；元数据不足以辨认具体端点，不归因给任一模型。[失败时间线](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/technical-first-round-failure-timeline.json)

费用按[官方CNY价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)及[官方USD价格](https://api-docs.deepseek.com/quick_start/pricing/)分别计算缓存命中、未命中和输出，包含主/子/辅助/原生重试；不使用订阅展示价或策略预留额。第一轮跨09:00，按请求起始时刻估价；已知费用跨窗范围为 CC¥1.277998–1.370111/$0.191700–0.205517，DSH¥1.439871–1.610751/$0.215981–0.241613。未知请求不填0，第一轮及两轮累计总费均为null；累计已知起始价小计仅为 CC¥5.125184、DSH¥7.298928。CC另有11次count_tokens，费用未披露，DSH0次。第二轮全部峰时且usage完整，DSH比CC贵52.29%、用时短1.97%；缓存未控制为冷缓存，此单轮不代表总体优劣。估计不是账户账单。[完整费用指标](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/metrics-v2.json)

第二轮 DSH两子代理均真正completed，无max-tokens；3次send_message未引发额外子turn，不能称为成功恢复。CC该轮未启动子代理；第一轮启动2个但未收completed通知，DSH第一轮两子代理均aborted。实际图像工具第一轮CC成功1次、DSH成功4次；两轮CC研究均未选择原生PDF Read，另有PDF shell调用。协议工具错误仅CC第一轮1次Bash isError，不据此推断研究判断或harness故障。外层Seatbelt保持读写/网络限制；图片持久化需要双方精确祖先目录自身可读，目录名称可见，不授权兄弟文件正文。四arm均通过9项OS隔离、59输入及4执行文件检查，113私有库文件与5可执行文件的精确集合/哈希完整。[技术观察](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/technical-observation.md)

## 4. 测试、代码审查与原始结果保留

生成结束后仅修纯事件解析器的stale-completed边界并补回归；运行版本仍单独保留。四arm原日志全部离线重放，完成分类不变，未付费重跑或覆盖原process/summary。独立审查确认无未解决P1/P2；全库离线回归1034项通过，223.717秒、exit0。这不等于正式自动化验证或投资方法有效性证明。[最终代码审查](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/final-code-review.md)

交付复核确认687份正式保护文件、4329份旧实验文件、897份本轮原始文件全部未变，四个实验进程组均已退出。[保留与清理凭据](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-22/dsh-isolation-v2/delivery-preservation-check.json) 单公司、固定语料、两轮中仅一轮自然完成，不足以证明生产可靠性或普遍不劣化。


本次结构修复没有把原文真实性与自然语言解除逻辑变成已被程序证明的事项；完整checker通过仍须语义复核。本报告为本地评测研究，不生成正式公司研究身份、latest、seal、报价或共识记录。
