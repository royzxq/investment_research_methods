# 股票研究执行架构解耦建议

日期：2026-10-21（Asia/Shanghai）。生成端：Codex。状态：只读架构评估与提案，未改生产代码、配置、历史、调度或共识规则；不代表 dsh 已接入。本提案承接同日 dsh 可行性调研，新增读取了相邻 ai_investment 的研究消费及报价契约。

建议先解耦现有自动研究架构，再接 dsh。目标是新增模型时主要新增执行配置，新增 harness 时实现和验收一个适配器；通用调度、研究方法与结果验收不再反复加入具体产品分支。支持多个执行配置，不等于自动增加投票席位或改变现有投资方法。

## Desktop 与 Standard 的关系

Desktop 是安装的桌面应用，Standard 是同套 DSH 的 Agent preset／工作模式；不需要另外安装“Standard软件”。模型选择又是另一层：同一个 Desktop 可以选择不同工作模式，再使用所配置的模型。

官方模式说明称 Standard 直接使用文件、搜索和终端工具，并包含 skills、计划、子代理和压缩；PTC 改为程序组织工具调用；Minimal 减少内置工具与上下文。Desktop 包含完整 Web 应用与本地运行时。[模式说明源码](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/client/ui-agent-preset/src/client/guide-locales.ts#L10)、[Desktop应用说明](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/apps/desktop/README.md#application-overview)

上次只确认 shell 的 PATH 没有 dsh，不能由此推断 Desktop 未安装。官方文档说明 Desktop 的命令注册是可选项，可通过菜单 Manage dsh Command 管理，所注册的 CLI 使用 Desktop 自带运行时。未来自动化应选择经验证的 headless／SDK 入口及明确的工具组合，不通过模拟桌面点击来批量研究；也不能假定 headless、SDK入门minimal与桌面Standard具有同样能力。[命令注册与运行时](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/apps/desktop/README.md#terminal-command)

未读取本机 Desktop 当前界面、安装版本、会话模式或模型设置，不能断言当前已经选了 Standard。

## 现状：已有部分分层，但尚未贯通

现有架构并非完全把模型和宿主等同。消费端已保留 `generator`、`model_seat`、`actual_model`，并以 `SEATS={'codex':'gemini','claude':'claude','coze':'coze'}` 映射业务席位。这证明“真实宿主”和“业务身份”已有分开的意图；仍用 gemini 标识历史业务席位不代表 Codex 实际在调用 Gemini。

未完成的部分是：执行选择、协议白名单、文件身份和消费策略仍依赖分散的固定集合。

| 已读位置 | 当前事实 | 重构含义 |
|---|---|---|
| methods `scripts/research_runner.py:668–720` | 按claude分支拼命令并解析structured_output；另一分支为Codex协议 | 把宿主命令、事件、结果解析收进adapter，业务层不再知道CLI参数 |
| methods `scripts/research_exchange.py:29,100–103,184–200` | v1仅允许codex/claude，严格字段及同生成端文件配对 | 不向v1随意添profile字段；新增身份合同须版本化 |
| methods `stock_price_map.py:85–89,308`、`research_consistency.py:137`、`research_paths.py:22` | 生成端枚举不同，现行v4只接受codex/claude，路径层另含coze | 新端必须走明确的新身份验收与兼容，不只是任意字符串 |
| methods `research_scheduler.py`、`research_coze.py` | CLI启动及Coze条件绑定当前主参与端 | 用执行计划选择profile；补充触发按已采纳policy，不按命令名称判断 |
| ai `src/analysis/research_consumer.py:24,303–353,401–404` | 有席位映射及provenance；严格封口且动态导入methods验收器 | 配置映射不够，需两仓共同切换版本化请求／结果／seal |
| ai `src/analysis/model_consensus_config.py:11,24–35` | 固定三业务席位及权重约束 | 注册N个profile不等于N个共识参与者 |
| ai `src/analysis/model_quote_store.py` | 报价按证券、业务model、日期标识；来源有严格重放／冲突纪律 | 同席同日的多profile不能互相覆盖或都算独立票；历史provenance不原位补字段 |

上述为源码静态事实，不是新运行验证。应保留具体adapter内部的codex/claude差异；需要移除的是这些差异对通用调度和研究业务的渗透。白名单和严格验证仍然有价值，应改成经注册、可校验的配置，不能改为接受任意命令和任意生成端。

## 建议的边界

| 层 | 负责什么 | 不承担什么 |
|---|---|---|
| Research contract：研究合同 | 框架／材料快照、证据截止、九节报告、估值及控制语义、输出与验收版本 | CLI启动、厂商模型命名 |
| Participation policy：参与策略 | 本轮主研究席、补充席、触发条件、超时／缺席处理、如何进入共识 | 用harness品牌推断模型独立性 |
| Execution profile：执行配置 | adapter、模型绑定、模式／工具、推理设置、权限、预算与并发、版本约束及凭据引用 | 改变投资规则、保存明文密钥 |
| Harness adapter：执行适配器 | 能力预检、启动／轮询／取消、事件与usage解析、结果收集 | 改写估值、放宽交付验收、自动提升latest |
| Common acceptance/publication：统一验收与发布 | 结构／路径／哈希／语义一致性、暂存、幂等发布、独立来源归属 | 把进程退出0或模型声称完成当作交付成功 |

模型身份是profile与运行记录的一部分，必须独立记录 provider、requested model、observed model／checkpoint、角色（主代理／子代理／压缩辅助调用）及推理设置；实际不可观测时保留null。配置中的模型别名可能被服务端升级，冻结别名并不保证冻结底层权重。

参与者示意：

| 业务用途 | profile示例 | adapter | 请求模型示例 |
|---|---|---|---|
| 主研究席A | 当前Codex配置 | codex_cli | 当前明确配置的模型，不能据品牌补造实际值 |
| 主研究席B（当前） | CC＋DeepSeek配置 | claude_code_cli | deepseek-flash及实际effort／上下文设置 |
| 主研究席B（候选） | DSH＋DeepSeek配置 | dsh_headless或经验证的SDK adapter | 同一DeepSeek模型，Standard等效工具组合 |
| 条件补充席 | 当前Coze配置 | 异步外部研究adapter | 外部服务可观测模型，不可得为null |

注册表可同时保留两个B候选，但某批次明确选哪一个参与。CC＋DeepSeek与DSH＋同一DeepSeek模型的并行试验，首先是不同执行路径的验证，不应自动成为两张新的“独立模型”票。是否参与投票、共识权重如何处理，必须由明确policy决定；本次不改变默认双主研究席和条件第三席。

## 最小可复用执行接口

适配器至少提供：`preflight(profile, requirements)`、`start(immutable_job)`、`poll_or_wait(handle)`、`cancel(handle)`、`collect(handle)`。实现可采用普通Python结构，不必先引入复杂框架。

- preflight返回版本、支持能力和实际可用性。合同区分必需、可选、允许的替代路径；缺能力时明确失败或披露既有允许的降级，不悄悄改研究义务。现行skill允许无子代理时由主代理补做，这与缺少原文核验能力不同。
- subprocess adapter可以共享现有进程监督、超时与进程组清理；Coze采用外部异步生命周期，不能强行伪装成CLI，也不能把发出请求当作完成或把取消请求当作已取消。
- collect给出原始事件／持久日志引用、明确成功／失败／未知状态、暂存产物、实际模型信息与usage完整性。DSH的截断stdout投影不能替代持久日志。
- usage同时记录已知值、未知部分及统计范围，包含子代理、摘要、重试、超时。没有计量不能填0，不据工具名称猜费用。
- 所有adapter进入同一验收边界，但按声明的交付合同选择校验器：当前Coze的补充schema与完整v4研究不同，不为统一接口而伪造其缺失内容。
- 原生LLM API只是模型服务；如果以后直接接API，仍需实现或采用具备工具循环、上下文、取证和恢复能力的agent runtime，不能把一次文本生成当成完整研究harness。

## 身份、版本和历史

现有 `generator` 在旧合同中继续表示原真实生成端，不改成slot、provider或模型名，也不为了接续旧历史把dsh标成claude。未来合同应显式区分 `seat_id`、`profile_id`、profile版本／快照哈希、`run_id/attempt_id`、harness／model provenance及交付合同。

一次运行的产物以不可变run／profile身份隔离；业务席位映射决定哪些结果被当前批次消费。latest必须有明确索引范围，不能把不同执行配置的“最新”混为一份。历史研究接续应明确采用哪份报告、方法与来源，不能仅因业务席位相同就继承其全部结论。

请求创建时冻结实际profile、研究合同、框架、材料及policy版本；运行中改全局默认配置不应改变已排队任务。旧冻结批次按原字节、哈希及版本恢复，未知历史模型不补造。新schema可双读旧版本、只写明确启用的新版本；新实现替换旧实现时避免永久平行分叉，但历史数据格式的必要读取兼容应保留。

研究结果与来源历史不原位扩字段。ai侧严格比较来源对象，随意补profile可能导致重放被判冲突；应使用新版本记录或单独绑定manifest，并明确旧新读取规则。

## 实施顺序与验收

**第一步：等价抽取现有两端。** 从runner抽出Codex／Claude adapter与内部profile注册，通用调度改为依据计划选择adapter。维持当前v1请求／回执、v4及其冻结交付合同、真实生成端身份、seal、报价、latest和Coze业务政策；不在此步开放新生产身份。优先证明命令／回执等价、错误分类、取消、超时与幂等，现有批次可继续恢复。这一步形成可回归的小闭环，不做整个系统的大重命名。

**第二步：隔离验证新执行器。** 用独立运行目录接入DSH候选，验证抽象边界、实际工具组合、日志／usage、取消与恢复；只产生隔离产物，不冒充claude进入旧生成端验收，不写正式latest、报价或触发Coze。先用真实接入需要检验接口，避免在跨仓生产协议上设计过度。

**第三步：两仓共同版本化执行身份。** 明确新request/result/seal/provenance合同与profile快照，补兼容／重放／冲突／同席多profile的测试，再由生产者和消费者一致启用。旧产物可读、新运行可追溯、报价归属不混淆；不顺带修改共识算法、权重或放开N票。

**第四步：正式切换profile。** 只有隔离质量比较和跨仓合同通过后，再把席位B从CC profile切到DSH profile，仅影响新批次。Desktop可继续用于手工研究，自动化使用固定版本的非交互入口。回退执行配置不能抹除新研究已经证实的风险事实或撤销既有控制。

完成后的合理目标是：换同一adapter已支持的模型只需新增并冻结profile；换新harness需新增adapter及合同测试；新增投票席位或修改补充触发仍是独立业务变更。接入成本降低，但不会承诺任意工具／模型零适配。

本次没有执行代码改造或模型请求，因此未运行生产路径测试；文档／源码核查不能证明上述架构已经落地。底稿见本轮 `output/deep-research/2026-10-21-dsh-vs-claude-stock-research/architecture-{local,consumers}.md`，不包含账户数据或凭据。
