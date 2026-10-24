# 宁德时代 DSH / CC 共享验收隔离配对（v3）

实际运行：2026-10-23（Asia/Shanghai）；研究证据与估值截止：2026-10-21。本记录评估 harness 的研究交付，不更新公司正式价格地图、自动化配置或共识。

DSH 在本次宁德时代固定输入的两轮中，未观察到整体研究质量劣化：两位独立盲评的合并均分为 **83.75/100**，CC 为 **81.25/100**。第一轮两端同为81.5，第二轮DSH为86、CC为81；这是小样本描述，不能宣称一般性优胜或统计非劣。四臂均自然完成。DSH本样本生成费比CC高44.23%，没有显示省费优势；总耗时几乎相同。

R14缺证不放行与按scope列齐全部当前约束，结构验收均已落实。但**恢复逻辑尚不能宣布全文经济语义通过**：四份正文都存在把add-only或holding-only限制扩大到entry的局部表述。它们没有实际按“只解除部分独立约束”放松当前限制，但仍违反scope一致性，不能因机器验收通过而忽略。

| 有效轮次 / 端 | 盲评员1 | 盲评员2 | 均分 |
|---|---:|---:|---:|
| 1 / CC（匿名A） | 81 | 82 | 81.5 |
| 1 / DSH（匿名C） | 82 | 81 | 81.5 |
| 2 / CC（匿名B） | 80 | 82 | 81.0 |
| 2 / DSH（匿名D） | 86 | 86 | 86.0 |

两人各对四份逐条核15组冻结一手真值，并按seed20261023固定序列核前8条独立额外事实，保留所有实际skip。候选为段落；候选内按原文顺序可取多条事实，不额外加“每段只取一条”。该歧义在锁分前同口径澄清，两位均按此交付。两个原始JSON/MD先锁hash，再解盲；评分差最大2分、hard-failure判断一致，未触发预锁的>10分或hard-failure分歧裁决条件。原始分数、初版匿名化及全部实验结果均保留。

共同优点是主估值算术、报告/JSON价格链和R14 unknown的保留；DSH第二轮的财务对账、压力基数和原始重建路径/R21阶段区分较完整。共同弱点是资本配置/回购细节覆盖、现金可用性边界和控制scope的正文表达。两评审均未认定协议级hard failure，这不等于没有数值或规则问题。根代理又回原始PDF及最终正文独立核查三项：

- **CC第二轮现金少一位**：压力/验收段写369.81亿元，Q3原PDF物理p5为369,813,786千元，即3698.13786亿元；物理p12的现金等价物为3333.97571亿元。报告其他基线和主PE使用正确数，R14仍unknown且没有放行，两评审据传播范围按局部错数扣分，原分未改；该错误仍须纠正，不能称数字全部可靠。
- **DSH第二轮融资来源错配**：把371.03亿元合并“吸收投资收到现金”全称H股配售。Q3原PDF物理p12明确其中16.102亿元来自子公司少数股东投资；其余金额也不能直接冒充已经核准的H股净募资。它没有改变主PE的总股本或合并现金余额，但影响资本配置解释。
- **两端均有scope扩大**：CC第一轮REBUY_UPGRADE把仅add的R14套到entry；CC第二轮最终恢复清单未分scope地混入持仓复评/价格；DSH第一轮以holding-only复评未完成阻止新增暴露；DSH第二轮ENTRY_PRICE又要求add-only的R14/D5。结构化all_of对已声明集合完全匹配，不能替代这些正文语义核验。应按原方法逐scope纠正文义，而不是新增“一律全冻结”的投资规则。本次保留原始报告，不代模型修研报、重打分或选优重跑。

建议继续维持现有正式自动化。DSH作为隔离harness已证明本样本能完成交付，研究质量没有观察到整体下降；下一步如继续验证，优先做scope正文与结构的一致性及资本配置/金额单位的定向验收，再用更多公司检验质量和子代理成本。此建议不改变投研方法，不代表授权切换、提升隔离报告或进入共识。


两轮有效配对的四臂均自然结束，并通过强制 stock-research-acceptance/v1。四份最终 R14 均为 applicable/unknown，各有独立 persistent add 限制；没有把缺证压力测试判 passed。结构化 audit/acceptance 声明的当前独立有效约束，按各自实际 scope 匹配对应 all_of 集合；此结论只限这些结构化集合，不覆盖前述正文将 holding-only 或 add-only 项扩大到 entry 的问题。格式验收不能证明经济证据充分、约束识别无遗漏或任意自然语言语义完整，独立原文盲评另行判断。

| 有效轮次 | 端 | 自然完成/共享验收 | 秒 | 生成请求 | 谷价生成费估算（元） |
|---|---|---|---:|---:|---:|
| 1 | CC | 通过/通过 | 1579.260 | 178 | 1.99596864 |
| 1 | DSH | 通过/通过 | 1280.340 | 131 | 1.57642000 |
| 2 | CC | 通过/通过 | 959.190 | 128 | 1.22065636 |
| 2 | DSH | 通过/通过 | 1241.284 | 232 | 3.06285524 |

两轮 CC 合计 2538.450 秒、306 次生成、¥3.21662500；DSH 合计 2521.624 秒、363 次生成、¥4.63927524。总耗时仅差0.66%；DSH本样本生成费高44.23%，第一轮较便宜、第二轮较贵，不能据此称其稳定更省或稳定更快。四臂均在谷价，统一谷价折算与实际时点估计相同。没有固定冷缓存或强制相同子任务选择，保留原生执行差异。

早间原第二轮在用户要求等待谷价后协同取消；其 CC exit143、DSH exit0 均 cancelled=true，不能把DSH退出0当自然完成，也不作为自然失败样本。为保证CC无session持久化与DSH公平，午间用全新目录、干净会话与原冻结输入补齐第二轮，预先声明原因，没有根据品质选优重跑。原第一轮不重跑，原中断轮不覆盖。

中断轮另有已知生成费 CC ¥0.50429828、DSH ¥0.73038308，合计 ¥1.23468136；其中跨峰谷请求按起始时刻估计，已知费用可行上界 ¥1.40040324。CC1个、DSH2个在途生成未取得完整usage，保持未知。全部本次已知生成小计 ¥9.09058160，已知跨窗上界 ¥9.25630348，另加3个未知请求；总费为null，不能报成精确全额。10次count_tokens未公开定价，单列且未擅定0费。此处仅为DeepSeek实验生成，不含Codex评审/设备等费用，非账户账单。全部主、子、原生辅助、恢复以及客户端断开但取得完整usage的请求均计入。费率采用[DeepSeek官方定价](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)并分别在早晨和午间实读核验。

工具层面，CC两轮未开启本地子代理；DSH第一轮无子代理，第二轮两名depth1子代理均有匹配的有序turn/end completed，无max-tokens、未结束turn或额外恢复turn。4次send_message不等于4次成功恢复。两端本地文件读取、写入及计算完成；DSH的命令文本分别出现8、14次PDF相关shell调用（不由提及次数推定提取成功），两端原生图片/PDF图像读取均未发生。本固定证据研究没有重测开放网络检索，调用次数不证明原文或经济理解正确。

工具协议显式错误CC各1次，DSH均0；checker命令文本提及次数不能作为实际执行或失败次数。独立可见结果：第一轮CC明确exit0/exit2/unknown为12/1/16，DSH为32/2/1；第二轮CC为12/0/0，DSH为0/0/14。第一轮已证实的自检错误涉及R14引用绑定、audit与result不一致，均原生修正，最终由外层独立复验通过。第二轮DSH自检退出码不足，保留unknown，不能倒推全部自检成功。

59份原始冻结文件、3份提示、6份独立执行文件、7份实现源以及主/子Flash/high/32768计划保持一致，启动顺序两轮反转（CC→DSH、DSH→CC，逐臂并行）。有效两轮中，CC原生另有104次（66+38）2112输出上限辅助生成；中断轮另有5次同类辅助生成，未显式high；均为Flash并纳费用，不将其冒称主研究high请求。单臂2400秒、stream参数180、最多两名子代理与原生至多两次恢复、1000请求/$50后续请求守卫、3未知usage门禁不变；180在CC请求超时与DSH流空闲超时语义有差别。CC2.1.296、DSH0.2.1-rc.2的实际入口、DSH bin.js/private Node前后hash一致；不据此宣称整个npm树逐文件绑定。

自然完成逐臂核process.success、无error/监督取消、exit0、独立有序主终态、runtime完整、真实固定9项OS canary精确集合及全部59/6输入完整性；原窄observer保留，以另立v2强复核补足，任意9个假键不再通过。主终态、子代理完成和产物/共享门禁分别统计，文件存在或settled不等于完成。

验证：续办前172项定向离线测试与全仓1082项回归通过，另有时段边界、盲包保真/泄漏、费用/中断选择与强自然完成反例测试。独立执行、匿名化与技术分析代码审查已闭环；匿名化修复小写cc漏项，按统一规则排除过程回执，保留初版及逐文件私有排除清单，原始研究不动。历史旧验收/旧报告不升级或追写。

保护复核：6255份旧实验及882份原第一轮/中断轮文件hash均相同；原701项业务保护基线有4项外部工作区文件hash不同，所记录mtime在08:26:58–08:27:00、早于本次首次付费config08:30:29，但mtime不能独立证明写入来源。没有回滚它们或声称701项从最初全不变。12:08:56（晚于午间12:05启动）另捕获701项更新基线，后段复核全字节相同；该收据不冒称付费启动前快照。本实验不导入生产dispatcher，真实OS探针验证工作区/另一臂/私有HOME读写隔离，没有正式writer/seal/latest/共识交付。

本轮共同baseline=null且当前限制并未全部解除，真实样本验证的是缺证时持续受限及当前all_of覆盖，没有演示真实历史限制跨期全部解除后的生产恢复；部分解除、合法OR及scope边界另有离线反例回归。

本样本仅一家公司、两轮，不能证明普遍稳定性、统计非劣效或完整开放网络工具能力；验证对象为当前DSH CLI的隔离headless执行，不覆盖Desktop交互或长期批量调度；保留原始方法、历史和正式自动化，继续按用户要求不切换、不进共识。

审计入口：[本轮审计](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/STATE.md)；有效第二轮位于offpeak-continuation/，原中断轮仍在parent trial-01/runs/research-02。技术最终指标见observer/metrics-v3-continuation-v2-final.json；费用/状态独立复核、匿名评审与源hash收据均随审计保留。

关键留档：

- [两位原始盲评锁定](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/reviews/both-reviewers-locked.json)、[盲评1](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/reviews/reviewer-1/review.md)、[盲评2](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/reviews/reviewer-2/review.md)
- [质量解盲汇总](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/quality-summary-unblinded.json)、[根代理原文抽核](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/quality-source-crosscheck.json)
- [技术与费用指标](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/observer/metrics-v3-continuation-v2-final.json)、[独立费用复算](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/observer/independent-accounting-final.json)
- [1082项回归](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/full-regression-receipt.json)、[执行前审查](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/continuation-preflight-review.md)、[技术分析审查](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/continuation-technical-code-review-v2.md)、[报告技术审查](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/final-report-technical-review.md)
- [原始结果与保护复核](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/final-preservation-receipt.json)、[保护边界澄清](../../../../../output/audits/investment/2026-10-23/dsh-isolation-v3/offpeak-continuation/preservation-boundary-clarification.json)
