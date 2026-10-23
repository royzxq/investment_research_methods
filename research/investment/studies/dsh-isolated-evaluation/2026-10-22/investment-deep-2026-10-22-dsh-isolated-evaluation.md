# DSH / Claude Code 同 DeepSeek 隔离接入评估

实验建立于2026-10-21，完成于2026-10-22（Asia/Shanghai）；共同估值截止为2026-10-21。本文是 harness 工程评估，不是公司正式研报或投资规则更新。正式自动化、生成端身份、共识席位及权重保持现状，实验产物不发布到公司目录、latest、seal或报价消费端。

本机DSH headless/base已能在隔离环境下使用同一DeepSeek型号运行真实工具与投研。**本例保存的研究产物未显示相对CC的质量劣化**：两位匿名评审分别给DSH 86/87分、CC 77/79分。但双方控制合同均存在缺陷，完整研究的自然完成和总费用又被共同安全取消删失，**本轮不足以证明可以无损替代正式CC自动化**。正式自动化和共识保持不切换。

## 1. 比较对象与固定条件

| 项目 | 固定条件或实际边界 |
|---|---|
| 公司与资料 | 宁德时代 A股300750.SZ；同一公开data pack、完整Q3/H1 PDF、股本/基金/回购/关联采购原文及来源索引；59份冻结输入；排除旧分析结论、持仓和评分答案 |
| 方法 | 同一canonical/compact、stock-research/deep-research-auto及适用reference，不修改投资方法或控制规则 |
| 用户任务 | 相同prompt字节，完整0–8九节报告和独立实验JSON；完整研究固定证据且禁止联网，在线工具另测 |
| 交付隔离 | JSON采用harness-research-experiment/v1，保留v4经济语义但无正式generator/meta；不调用正式writer/build/seal |
| CC | 本机Claude Code 2.1.296；默认原生工具，私有HOME、无全局settings/hooks/plugins/MCP |
| DSH | 本机CLI 0.2.1-rc.2的headless/base，私有配置/会话；不是Desktop 0.12.1 GUI Standard实测 |
| 模型 | 主研究与子代理请求deepseek-flash/high（官方当时列为DeepSeek-V4.1-Flash-1017），max output16384；实际所有观测生成请求型号均Flash。对齐服务端型号别名，未取得不可变权重ID |
| 原生差异 | CC主研究adaptive/high、DSH enabled/high；辅助调用保留各宿主原生设置，不能称每个请求推理模式/输出上限完全相同。请求正文不被观察代理改写 |
| 资源与会话 | 工具探针每端3次全新会话、600秒；研究每端1800秒、最多2子代理/深度1。独立workspace、HOME、配置、进程组和会话 |

DSH现成headless入口没有GUI Standard选择参数；Standard还涉及GUI preset的工具和会话行为，不能把本轮结果外推为Desktop Standard结果。[本机入口取证](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/local-entry.md)，[官方headless源码说明](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/bundle/headless/README.md)，[Standard preset](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/bundle/web-app/presets/standard.patch.yml)。

## 2. 研究质量：匿名评审现存产物

研究03在响应流异常触发共同安全取消前，双方均已留下九节报告和严格JSON实验envelope。**这些文件可以评价内容，不能当作已自然完成的完整研究样本。** 未修补原始报告/JSON；结构通过不代表事实、估值或控制语义通过。

两名独立上下文的Codex评审代理，按事实30/覆盖反证20/估值算术25/控制15/交付10评分。评分前不提供harness映射、费用、耗时、工具日志或同行结论；只统一归一自身绝对路径和显式harness名称，不改经济数字。两人逐组检查事先冻结的15组真值，并按固定seed抽查首8条非真值表独立事实；独立source字段仅解释其直接上下文，跳过与不足均记录。评分是代理评审，不是人工评审或统计显著性证明。

揭盲映射为A=DSH、B=CC；映射在两份评分冻结后才用于汇总。

| 质量维度 | DSH（评审1 / 评审2） | CC（评审1 / 评审2） |
|---|---:|---:|
| 事实与证据 /30 | 28.5 / 28 | 27 / 27.5 |
| 覆盖与反证 /20 | 17 / 18 | 13.5 / 15 |
| 估值与算术 /25 | 22.5 / 23 | 21 / 21 |
| 控制与监控 /15 | 9 / 9 | 7.5 / 8 |
| 交付 /10 | 9 / 9 | 8 / 7.5 |
| **总分 /100** | **86 / 87** | **77 / 79** |
| 预定义评测硬失败（不被总分掩盖） | 两人均未确认 | 两人均确认同1项R14检验豁免 |

两份核心收入→利润→股权价值→A+H股数换算→五折扣→P1，以及V5，均可按各自声明参数复算闭合。没有因为报价不同扣分，也没有把不同定义的净现金代理强行匹配成一个答案。DSH对两项基金、回购、未来预付款与现金桥的覆盖更完整；CC对已采纳CPI观测、R9中国国债缺口的处理较好。未覆盖算覆盖不足，诚实unknown或明确研究假设不当作伪造。

**CC的关键问题有独立方法影响。** 它以“间接成本、非直接油价敏感”为由排除油价+30%检验，却已确认购进价格和利润率成本暴露。冻结R14明确把购进价格暴露的中下游制造纳入100→130美元V5强制范围；其audit缺少相应独立add约束/解除。两位评审将此判为未决强制检验被不当豁免，root已回冻结canonical/compact和原JSON确认；不是认定公司在130美元下OCF已经为负，也不是声称本轮已买入。当前其他原因仍使entry/add blocked，不抵消独立控制遗漏。[冻结R14](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/trial-01/frozen/framework/investment_framework.md:324)、[CC表述](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/trial-01/runs/research-03/cc/workspace/outputs/report.md:214)。

CC另在Precheck警惕下，对自行声明的d_base 10%—20%区间取15%，未执行原规则的上沿映射；只改成其自述20%上沿、保持其它数不变，算术诊断的P1约低5.9%，不是重新发布报价。其audit.scenarios为数组，而冻结audit-v2要求low/base/high具名对象；主报价算对不等于内部审计契约有效。另有R3压力情景文字把7200×11%与704混写，以及局部GWh十倍笔误；后者未传播到主要TWh/报价，不另升级为关键单位硬失败。

**DSH同样没有达到完整控制合同可用状态。** CNY红利利差错用美国CMT而非同市场基准；R1三项合取中②③已不命中，却把①unknown单独扩大为entry资格债务；需求/份额恶化时JSON写“下调r_terminal”，与正文提高风险折扣的方向相反。两端还共同把D5原本独立可用的重建路径误串成必须先过R21，且现金流背离的当前持仓复核与holding=normal摘要不闭合。这些是具体控制缺陷，不能用DSH较高总分掩盖；它们也不授权交易或机械退出。

实际额外抽查：评审1为DSH6条/CC7条，评审2为DSH6条/CC8条。候选顺序相同，对同一source上下文里哪些是新增独立事实存在判读差异；没有从未入选正文补样，不声称每人都核足8条或样本统计独立。两位对每份总分只差1/2分，硬失败分类一致，未触发预定的大分歧裁决。root仍独立复算并核实上述重要控制问题；DSH一个压力情景报价有分币级舍入误差，基准P1不受影响。原始评分和产物全部保留。

[评审1](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/blind-review/reviews/reviewer-1.md)、[评审2](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/blind-review/reviews/reviewer-2.md)、[root复核与映射后汇总](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/quality-review-resolution.json)、[事前真值及原页](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/ground-truth.json)。

## 3. 工具调用与故障恢复

| 实际核验项目 | CC | DSH |
|---|---:|---:|
| 三轮进程/文件envelope完成 | 3/3 | 3/3 |
| CSV计算与预期单个null字段严格一致 | 3/3 | 2/3 |
| 原生独立子代理真实完成且父收到结果 | 3/3 | 3/3 |
| 受控exit42后重试exit0 | 3/3 | 3/3 |
| 原生搜索返回结果 | 3/3 | 3/3 |
| 原生WebFetch直接返回可读PDF正文 | 0/3 | 0/3 |
| 官方URL下载、实算SHA、PDF提取并读取正文fallback | 3/3 | 3/3 |

DSH第三轮把汇总debt写成[null,null]而非预期单个null；没有补成0，收入/利润/利润率均正确。这是业务字段归一/契约信号，不是Python没运行，也不能夸为3次字段全对。下载得到的官方Q3 PDF均为同一588939字节、SHA256 476611fe240b90088319c852de4e89d8ab1537b858d2ffbca573af5f8c5419b3、13页；搜索摘要、下载二进制和读到正文分别核验。

完整研究中两端均实际读到Q3全文及H1关键部分。CC通过PDF渲染PNG再原生Read，真实返回图像block；原生直接PDF看页仍遇pdftoppm环境错误。DSH在研究02渲染后read_image被隔离profile共享父路径EPERM拦住，后用原PDF/PyMuPDF文本恢复；研究03没有read_image调用，因此不能声称已完成视觉复核，也不能据此断言DSH一般视觉能力差。两端现有x86 Poppler在arm64不可执行、here-doc临时目录限制均是残余环境干扰。

长研究子任务也有截断：研究03 DSH两个子代理均以单次输出16384的max-tokens结束，只有settled、没有正常completed交接；主代理收到后继续。CC一个正常completed并回到父代理，另一个在共同取消前未完成。DSH主turn1曾max-tokens，但收到子任务后自然进入turn2；共同取消时turn2仍活动，不能把旧turn1理由当最终自然失败。详见[逐项工具证据](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/tool-observations.md)。

## 4. 稳定性：保留全部尝试并区分原因

| 运行 | 发生了什么 | 可支持的结论 |
|---|---|---|
| 连接预热及probe01 | 修正本地计量器、DSH reason协议/配置、CC临时目录及嵌套sandbox等接入问题；全部原始失败和费用保留 | 不计正式可靠率，也不把本地429/拒绝说成provider限流 |
| 有效probe04/05/06 | 每端3次均正常完成；保留真实工具失败/恢复与DSH一次字段类型偏差 | 通过短任务重复初筛，不证明生产可靠率 |
| research01 | 实验代理缺少实际受支持的count_tokens端点，产生本地501；在没有最终文件、未读质量前取消并修仪器 | 仪器无效轮，不评研究质量 |
| research02 | 共享全输入按miss峰价估算达到10.0388643USD安全上界；约1021秒时两端均无最终文件 | 资源删失；缓存调价只有已知费用部分，总额仍null。事前条件仅允许补充一轮扩大资源 |
| research03 | 只把共同上界提高至50USD/1600请求，其余源、输入、profile和1800秒不变；产物已存在后出现响应IncompleteRead | 内容可评；自然完成、完成耗时、完整总费用被共同安全策略删失，不排名 |

研究03最先在00:48:36.805由CC的一条HTTP200响应出现IncompleteRead，日志只能定位到响应读取/传输边界，不能唯一归因DeepSeek服务、网络或实验代理。未知用量保护触发共同取消，随后DSH/CC原已在途请求各出现ClientDisconnected，是取消后果，不能算另两次独立provider故障。总408请求（397生成+11计数），已知保守上界13.7338USD<50、408<1600、约1062秒<1800，均未触及这些上限。DSH stdout虽有final包装，durable turn2仍未结束；exit0同样不能证明研究完成。

研究03之后不再实跑或按质量择优。扩大资源的条件在研究02最终文件不存在、任何质量未读时冻结，保留首轮删失及费用。[资源条件](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/resource-contingency-plan.json)、[客观触发](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/resource-contingency-trigger.json)、[研究03停止分类](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/research-03-stop-classification.json)。

## 5. 成本：模型token费估计，不是账单或完整TCO

按实际provider usage汇总全部主/子/辅助/重试生成请求。已通过真实计量验证Anthropic兼容的input_tokens是不含缓存读的未缓存输入，缓存不能重复加价。实验时段属官方离峰；官方人民币离峰每百万token为未缓存1元/缓存0.02元/输出4元，峰价为2/0.04/8元。美元表独立计算，不做汇率换算。DeepSeek服务端Search/Fetch当前免费政策止于2026-11-01零时，北京时间。[人民币价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)、[美元价格](https://api-docs.deepseek.com/quick_start/pricing/)。

| 范围 | CC | DSH | 如何解释 |
|---|---:|---:|---|
| 3轮有效工具探针，离峰估计 | ¥0.69793 / $0.10469 | ¥0.25098 / $0.03765 | 此任务模型token费DSH少64.0%，包含字段未合预期那次；不能外推完整研究 |
| 同上按峰价重算 | ¥1.39586 | ¥0.50196 | 价格敏感性，不是第二笔支出 |
| 工具探针耗时中位数 | 184.015秒 | 129.798秒 | 本机隔离环境下描述值；不推断生产速度 |
| 研究03已知完整响应费用部分 | 已知部分¥2.11221 / $0.31683 | 已知部分¥1.56306 / $0.23446 | CC2笔、DSH1笔不完整用量；完整总费为null，不据下界排名 |

探针未缓存/缓存/输出token，CC为503647/2446848/36336，DSH为82233/827904/38047。共享账户缓存未做严格冷启动；将全部输入按miss离峰重算，探针分别为$0.46438/$0.15935，仍只说明该小任务的请求与上下文开销。

不隐藏调试成本：预热/无效仪器轮已知模型token费约¥1.06596，资源删失research02已知部分约¥3.16699；连同探针和research03，所有观察到的完整生成响应合计已知部分约¥8.85712，另有8笔不完整生成响应未知，不能当总账单。count_tokens是非生成请求，费用未披露，不假定为0、不把返回计数当消耗；Codex评审、人工、本机资源及其它未核实收费不在本表。

[全部请求计量汇总](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/metrics.json)、[确定性比较结果](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/comparison.json)。

## 6. 隔离、测试和代码审查

实验入口只有三个独立模块：[benchmark](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_harness_benchmark.py)、[私有CLI封装](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_harness_trial.py)、[观察代理](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_experiment_proxy.py)。生产runner/scheduler/runtime/service/config没有新增实验导入或DSH注册。运行时真实key仅由父进程观察代理读取/持有，未复制给CLI或新文件；CLI只拿dummy key；上游固定DeepSeek，不记录认证头/提示词/thinking正文。原生CLI的完整会话日志可能含模型推理，留在权限受限审计目录，未将其作为公开结论或盲评输入。

完整研究两端均通过7项OS正/负检查（在线探针为5项文件边界检查，网络按探针任务开放）：本目录写、外部写拒绝、真实项目/另一端/私人HOME读拒绝、模型代理可连、其它端口拒绝。研究阶段同时禁止provider服务端搜索工具，防止仅靠本机网络限制漏掉服务端外部取证；两端未观测外网取证调用。外层Seatbelt持续覆盖全部后代，DSH仅关闭会冲突的内层重复sandbox；这不是虚拟机级全系统隔离声明。

原59输入每端逐项哈希匹配；研究03原113运行库和严格集合均匹配。research02 CC只新增12个pycache文件，原113未改，但原始严格集合门禁仍保留false；没有为通过而忽略可执行缓存。[验证凭证](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/validation-receipt.json)。正式公司产物/索引/队列及消费端报价CSV的652个基线文件无修改或删除；另检出基线漏记的0字节queue.lock，出生/修改均为10月8日，不当作本轮新增、也未删除。记录的24个CLI进程组已无存活成员。[污染检查及旧锁说明](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/protected-final-interpreted.json)、[进程清理核验](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/process-cleanup-check.json)。

全仓离线回归实际运行 python3 -m unittest discover -s tests -v：**989项全部通过，169.782秒，exit0**。新增实验模块对应83项测试覆盖严格/畸形输入、FIFO/软链、私有HOME与网络边界、当前终态协议、进程组清理、流式不完整用量、在途关闭/去重、非生成CountTokens及门禁。全部回归为fake CLI/本机fake upstream等离线验证，真实DeepSeek调用只来自上述独立实验。独立审查发现的私有目录、费用未知处理、关闭边界和协议问题均在相应后续有效矩阵冻结前修复并复核；最终三个源哈希与研究03冻结配置完全相同，未放宽运行库门禁，**无遗留阻断代码问题**。[测试日志](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/full-unittest.log)、[独立代码审查](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-21/dsh-isolation/code-review.md)。这些结果不等于生产质量、稳定性或费用已经验收。

## 7. 可用范围与后续门槛

本轮只覆盖一个公司便利样本、一次留有研究产物的固定证据任务、每端3次短工具探针。未验证完整在线研究、公告范围穷尽、多公司/长时间生产可靠率、GUI Standard、真实账户账单或投资有效性。共同安全取消和残余图片/PDF环境问题应放在质量解释旁，不能藏到总体成功率里。

下一项隔离验证应优先解决图片工具的父路径依赖、长子任务输出上限与完成交接、流异常下的独立续跑及完整计费可观测性，再扩大到多家公司在线配对。任何后续接入仍须保留harness/model/runtime与实际生成身份、业务席位、共识规则的区分；本轮没有实施正式迁移。
