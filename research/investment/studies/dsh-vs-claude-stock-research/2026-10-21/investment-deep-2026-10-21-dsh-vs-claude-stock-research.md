# 用 DeepSeek Harness 替换 Claude Code 的股票投研可行性

调研截止：2026-10-21（Asia/Shanghai）。生成端：Codex。研究方式：完整调研，无适用的 dsh 同题历史；复用本仓现行契约与历史实验作为背景。本文评估 Codex 保留、Claude Code＋DeepSeek 席位改为 dsh＋同一 DeepSeek 模型。完成文档、源码及本地契约核验，**尚未完成真实模型 A/B，因此效果等效性仍未验证**。

**结论：技术上可行，值得做受控试迁移；当前不能直接替换生产。适配正确后，没有证据支持“必然明显劣化”，也没有证据保证“无损或更强”。** 研究方法已有共享文件，迁移的主要工作在执行器、工具、身份和上下游协议。最值得保留的是现有证据与验收纪律；dsh 的主要潜在价值是运行过程可检查、可定制，实际质量和开销须用投研任务验证。

## 当前基线与比较口径

本机只读确认 Claude Code 为 **2.1.296**；配置主模型为 `deepseek-flash[1m]`，子代理为 `deepseek-flash`，入口为 `https://api.deepseek.com/anthropic`；auto compact window 为 786432；配置及本次 shell 环境未声明 effort。没有捕获真实模型请求，不能据此确定生效 effort、所有子请求配置或服务端实际版本。本轮 PATH 未发现 dsh。[本地白名单核查](/Users/xinquanzhou/Workspace/investment_research_methods/output/deep-research/2026-10-21-dsh-vs-claude-stock-research/local-preflight.json)

`[1m]` 是 Claude Code 的上下文窗口标记，官方文档说明发送 provider 请求前会剥离；不能把它当成另一个更强的 DeepSeek 模型。DeepSeek 当日官方 API 文档将 `deepseek-flash` 指向 **DeepSeek-V4.1-Flash-1017**；这只确认公开路由说明，没有证明本机已经执行该模型。[Claude Code 模型配置](https://code.claude.com/docs/en/model-config)、[DeepSeek 当前模型](https://api-docs.deepseek.com/quick_start/pricing/)

官方 dsh 仓库是 `deepseek-ai/deepseek-harness`。本轮 GitHub release API 和发布页显示最新发布为 **0.2.1-rc.2，2026-10-17**，仍标为 pre-release；源码核查固定该 tag／commit `687f282e8625c6b8d11ff58211a90524be2e4317`。README 明确处于 developer preview 并可能破坏兼容。[官方项目](https://github.com/deepseek-ai/deepseek-harness)、[本轮版本](https://github.com/deepseek-ai/deepseek-harness/releases/tag/dsh-v0.2.1-rc.2)

## 能否承接现有研究

| 本仓需求 | 核验结果与迁移判断 |
|---|---|
| canonical／compact、研究技能与 references | 方法在普通 Markdown，已有共享 `.agents/skills`；可以复用，无需重写投资方法。dsh 的 Standard 模式可发现该技能目录，仍须实测触发、引用路径和冻结框架读取。 |
| 搜索、网页正文与官方公告 | dsh rc.2 已接入 DeepSeek Search／Fetch；需要启用并验证具体 profile 中的可用性。现有 CC＋DeepSeek 同样支持 WebSearch，联网不是 dsh 独有增益。 |
| PDF、财务表格与 Python 验算 | 下载、按页提取、文件哈希及 Python 校验可复用；图片回看、扫描页、错列表格和工具返回截断须真实验收。 |
| 最小上下文多代理、反证与独立核验 | dsh 有原生子代理；需验证实际上下文继承、工具权限、任务交接与异常状态。Agent Team 属实验性能力，不能代替跨进程锁和文件隔离。 |
| 长报告、压缩与中断恢复 | dsh 有会话持久化及压缩／恢复机制；具备功能不证明会保留估值假设、反证、阻断条件和来源定位。 |
| 九节报告、P1／T1、v4／audit-v2 | 现有 Python 验收逻辑可以复用，但生成端枚举、回执解析和启动协议尚未支持 dsh。 |
| 调度、双端共识及 Coze 条件补充 | 当前多处明确绑定 codex／claude；整套替换需要协调本仓与 `ai_investment`，仅换一个 CLI 无法完成。 |

功能事实来自固定版本的官方文档／源码；本仓事实来自实际文件读取。详细定位见[本仓契约核查](/Users/xinquanzhou/Workspace/investment_research_methods/output/deep-research/2026-10-21-dsh-vs-claude-stock-research/local-contract.md)及[官方功能笔记](/Users/xinquanzhou/Workspace/investment_research_methods/output/deep-research/2026-10-21-dsh-vs-claude-stock-research/dsh-capabilities.md)。本轮没有把“文档有该功能”升级成“本机已跑通”。

兼容仍有具体边界：默认技能根包含 `.agents/skills`，没有自动扫描 `.claude/skills`；项目可读 AGENTS／CLAUDE 文件，但不解释 `.claude/rules` 或 `@path` imports，且指令注入有字节预算。个人 CC 扩展不能假定全部自动迁移。[技能发现](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/skill/skill-filesystem/README.md)、[规则加载](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/context/agent-instructions/README.md)

rc.2 的独立 Search／Fetch API 需要切换启用，默认组合仍为辅助模型 Messages 搜索与本地 HTTP Fetch；启用前后费用和取页路径不同。fresh 子代理支持独立空上下文，但共享服务／工作目录；压缩后旧历史由摘要替代，完整日志仍在，不能把日志持久化当成模型始终保留全部原文。[检索配置](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web-deepseek-api/README.md)、[fresh 子代理](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/subagent/subagent-spawn-in-process/README.md)、[压缩策略](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/compaction/compaction-basic/README.md)

首次投研适配建议采用 **Standard**。它与本仓依赖的技能、计划和子代理较接近。PTC 可以进一步尝试批量取数、过滤工具结果与并发，但会改变工具接口，应在 Standard 基线通过后单独比较。Minimal 缺少现成的技能发现等流程支持，不能因为某些编程基准分数较高就直接作为默认投研模式。

## 效果是否会劣化：已有证据支持什么

**同模型不等于同效果。** 工具描述、文件／网页返回方式、上下文保留、错误反馈和结束判据都会改变最终产物。已经找到同 DeepSeek 模型的公开比较，结果支持“依赖任务和模式”，不支持单向结论。

DeepSeek 官方 V4.1 Flash model card 的同模型 scaffold 表如下。它属于早前 V4.1 Flash 的厂商自评，不能当作当前 1017 版本或本仓投研实测：

| 基准 | Claude Code | dsh Minimal | dsh Standard | dsh PTC |
|---|---:|---:|---:|---:|
| DeepSWE v1.1 | 69.8 | 72.6 | 70.5 | 67.6 |
| Terminal-Bench 2.1 | 88.0 | 90.6 | 85.8 | 85.8 |

官方说明使用 max effort、1M 上下文、Linux 环境及相同采样设置；DeepSWE 每题 N=8，Terminal-Bench 每题 N=3且无网络。Standard 相对 CC 一项略高、一项略低；PTC 也没有普遍优势。表中未提供足以判断统计显著性的置信区间，任务更不包含本仓的中文财报取证、投资框架与价格地图。[官方同模型比较表](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash#evaluation-results)

Composio 自行执行的 30 项真实 SaaS 工具任务中，同名 V4 Pro 0813 下，CC 通过 19 项，dsh 0.1.0-rc.7 通过 20 项。作者同时披露：dsh 走 DeepSeek 直连，其他组经 OpenRouter；dsh 晚五天运行；CC 两次超时没有 usage。因此这只能作为 dsh 可以完成复杂工具任务的早期旁证，不能把成本差或一题差异纯归因为 harness，更不能承诺本机节省七倍 token。[实验及作者披露的限制](https://composio.dev/content/deepseek-harness-vs-claude-code#3-the-benchmark-same-model-different-harness)

另有 2026-10-01 的跨 harness 论文，但其 **Claude Code 只测 Claude，未测 CC＋DeepSeek**，dsh 用的还是 0.1.1-rc.2 与 V4 Pro。它支持“模型、harness、任务须联合评估”这一一般结论，无法裁决你的具体替换。[论文 §3.1、表1及附录A](https://arxiv.org/html/2610.00917v1)

对本仓的判断须分层：

| 层面 | 本轮判断 | 最可能的劣化来源 |
|---|---|---|
| 已取得材料上的分析、估值推理 | 未发现必须大幅下降的证据；无损仍未证实 | effort／系统指令／可见材料不同，证据不充分时过早收敛 |
| 复杂取证与长程综合 | 未验证，是研究质量的主要风险 | 把搜索摘要当原文、表格截断、压缩丢掉附注／反证、子代理交接遗漏 |
| 结构化交付和自动批次 | 当前直接替换不兼容；适配后再验收 | 错端身份、回执缺失、状态提前完成、失败被当成功、进程未清理 |
| 费用与耗时 | 方向未知 | cache／输出／子代理／摘要／重试／失败恢复的总量变化 |
| 定制与诊断 | 源码和插件可检查，具备潜在优势 | 预览版升级和自定义组件增加维护工作；可检查不等于结果更正确 |

上表的风险是源码与流程推导，不是本轮观察到的 dsh 投研失败率。

## 两项会误导替换判断的假设

**“dsh 消除了 Anthropic 兼容协议，所以天然更强”不成立。** rc.2 的官方 DeepSeek 适配器默认 base URL 仍是 `https://api.deepseek.com/anthropic`，调用 `/v1/messages`，将工具转换为 `input_schema`，将推理档位转换为 `thinking` 与 `output_config.effort`。变化是宿主及其上下文／工具编排，不是必然移除这套线协议。[默认入口](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/llm/llm-deepseek/src/config.ts#L113)、[请求与参数](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/llm/llm-deepseek/src/serialize.ts#L147)

DeepSeek 的 Anthropic 兼容接口确实不完全等同于 Anthropic：例如忽略 `budget_tokens`，`output_config` 仅支持 effort；不能将这件事直接解释成 CC 本地 MCP 失效或 CC 的 CLI schema 交付必然失效。客户端 MCP、自定义工具和服务端 MCP 字段是不同层。DeepSeek 官方提供 CC 配置与 WebSearch 说明，10/17 的模型更新还明确以 CC 测试 Terminal-Bench 4.0，并说明针对 dsh 等平台作了优化。这些事实都没有提供“换宿主必然提升”的保证。[接口兼容表](https://api-docs.deepseek.com/guides/anthropic_api/)、[CC 接入](https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/)、[10/17 更新](https://api-docs.deepseek.com/updates/)

**“换 dsh 会自动降低模型单价”也不成立。** 当前基线已经调用 DeepSeek API，不能拿 Anthropic 模型价格与 dsh＋DeepSeek 比较。费用差来自实际用量与执行过程；缓存标记被忽略也不等于 DeepSeek 的自动前缀缓存没有命中。官方当日定价还说明，相关服务端 Search／Fetch 调用将于北京时间 **2026-11-01 00:00** 起按请求收费，检索摘要的模型用量也应计入；两端都要计量。[当前计费口径](https://api-docs.deepseek.com/quick_start/pricing/)

## 本仓替换需要完成的工程

个人在 dsh 中手动调用共享方法，工作相对集中；替换整个自动研究席位则涉及跨文件、跨仓的兼容迁移。至少需要以下四组工作：

1. **建立真正的 dsh adapter。** 当前 `research_runner.py:668–720` 硬编码两端启动参数与回执。`--cli` 只是可执行路径，不能用 `--generator claude --cli dsh` 代替适配。需选择 headless 或 SDK，接入冻结 prompt／框架／数据包、工作目录、权限、工具、事件与成功／失败回执，保留超时取消和子进程清理。网页保存的凭据也不代表 headless 会使用相同凭据。
2. **增加真实宿主身份。** 建议新值为 `dsh`，模型另记。`research_paths.py`、`research_exchange.py`、`stock_price_map.py`、`research_consistency.py`、runner及文档都需同步；保留历史 `claude`，不将旧报告改名。现有路径层含 Coze，不代表所有层都支持第三个任意 CLI。
3. **延续研究与交付验收。** 继续九节报告、P1／T1、v4／audit-v2、entry／add／holding控制及估值链检查；保留原文定位、披露日、反证、关键事实复核和 Jev 候选审计。复用暂存、哈希、严格校验与原子发布，不以模型总结或进程退出0认定完成。新端无本端历史时，显式引用旧 Claude 研究作材料，不能冒充 dsh 历史。
4. **同步调度与消费。** `research_scheduler.py`、`research_coze.py` 的双端集合，以及相邻 `ai_investment` 发布器、共识／seal／报价回写均有依赖。可以维持“Codex＋第二研究席”的业务结构，但必须把业务席位与真实宿主身份分开；本轮未检查外仓全部消费者，完整实施清单仍需跨仓核验。

批量入口尤其要核实 profile 的实际工具组合；Python SDK 教程默认使用 sdk-minimal，不能自动等同网页 Standard。headless 虽提供 `--json`，该流是可能截断的事件投影，不能作为完整工具原文与全部尝试的唯一审计依据；还应保存持久日志和可取得的 provider 用量。网页保存的登录／密钥默认不会被 headless 使用。[Python SDK 配置](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/docs/user/guide/python-sdk.md)、[headless 的输入、事件与凭据](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/bundle/headless/README.md)

这些是应用契约变更，不应借机修改投资方法、折扣、阈值或历史报告。本轮未实施上述修改。

## 如何判定可以正式替换

建议先完成隔离适配与小样本验证，再迁移自动化。以下是**后续评测建议，尚未执行，也不是新投资规则**。

先用冻结材料测六类任务：财报附注及条件限定；现金流与一次性项目；港股币种／股本／每股口径；更正公告与增量接续；有估值但买入受限的控制语义；长任务压缩、中断、失败恢复与 JSON 交付。已有恒瑞材料可作为其中一个抽取样本，但其 10/12 旧实验没有 dsh，且早于 10/17 模型路由更新，不能直接作当前基线成绩。

冻结相同框架、资料哈希、公开截止、模型提供方／服务端版本、推理档位、上下文及预算；主代理、子代理、压缩摘要都核实际配置。dsh 适配器未覆写时默认 high，不能自动假定等于 max；当前 CC 生效档位也需捕获。先比较日常现状系统，再做同参数归因比较，两种结果分开报告。两端使用各自真实工具，保留全部失败尝试；联网比较如无法冻结资料，就明确这是整体系统效果比较。

材料测试通过后，再选一只业务较稳定的 A 股、一只附注／事件复杂的 A 股、一只港股，做同日同资料的成对全流程研究，每端每只至少两次，交替运行顺序。这个小样本适合发现问题和决定试运行，不能证明统计意义上的长期等效。

验收先看关键事实、原文支持、反证覆盖、估值口径及控制语义，再看完整报告交付率、需要人工修正的次数、压缩前后遗漏、失败恢复和费用。不能以报价更接近 Codex 或两端更容易达成共识作为正确性标准。任何伪造原文、漏掉影响判断的反证、混错币种／单位、错误解除阻断、假成功回执，都应暂停扩大试用。

费用按**所有尝试累计开销／通过语义与交付验收的报告数**统计，覆盖输入、输出、cache、摘要、子代理、搜索、重试、超时与修复；缺少失败 usage 保持未知或下限，不补0。已有本仓 CC 组内试验证明减少原文和工具调用也可能被复核与恢复开销抵消，不能以更少 token 字样替代实际账单。

通过后先将新端结果隔离保存，再接入正式双端共识；保留可回退的 CC adapter 与历史，分别固定版本。**当前推荐方向是“Codex＋dsh（Standard）作为候选组合”，采用依据应是本仓实际验收，而不是原生品牌或编程排行榜。**

## 证据范围与交付

已完成：三个独立子任务、主代理对关键官方源码／同模型表格／实验限制的直接复查、本地配置白名单与 CLI 版本核对、迁移依赖核查。研究笔记和来源索引保存在[本次底稿目录](/Users/xinquanzhou/Workspace/investment_research_methods/output/deep-research/2026-10-21-dsh-vs-claude-stock-research/)。

未完成：dsh 安装运行、实际搜索／PDF工具验收、真实同模型投研 A/B、token／费用对账、自动化迁移与外仓消费者完整检查。因此可以确认技术路径与适配边界，不能报告劣化率、无损保证或确定节省比例。本轮只新增研究材料，没有修改生产脚本、技能或配置；没有运行无关的全仓测试。模型与子代理 token 总用量不可得。
