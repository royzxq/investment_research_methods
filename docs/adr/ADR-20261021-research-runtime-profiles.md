# ADR：研究执行配置与 harness 适配器

日期：2026-10-21（Asia/Shanghai）。状态：本地实现；落实[架构提案](../../research/investment/maintenance/2026-10-21/investment-2026-10-21-research-runtime-architecture-proposal-codex.md)第一步。暂不接入或切换 dsh，不安装新定时服务，不修改模型服务连接或凭据。

## 决策与边界

研究方法、参与策略、执行配置、CLI 协议与统一验收分别由原有框架/合同、原有调度/消费政策、`research_runtime.py`、`research_harness.py`、原有 runner 验收发布负责。抽取两端真实 CLI 的差异，保留共享的进程监督、取消/超时、暂存和验收发布。现有参与策略继续由其原属主维护，不新增一份平行策略配置。

| 身份 | 本次含义 |
|---|---|
| `producer` / 旧合同 `generator` | 原真实生成端，当前正式合同仅 codex/claude |
| `profile_id` + `revision` | 非秘密执行配置的标识和正整数版本；实际完整配置同时冻结，标识不能替代内容 |
| `harness` | 可信代码注册的适配器，当前为 codex-cli / claude-code-cli |
| `models.main` / `models.subagent` | 请求模型选项，按能力支持；不表示实际观测到该模型 |
| `process.json.actual_model` | 运行事件中实际披露的主会话模型标识；未披露为 null |
| 下游业务席位 | 沿用原消费端映射与共识算法；增加 profile 不增加投票 |

不改变研究 canonical/compact、九节报告、估值与控制语义、v4/audit-v2、旧合同读取、文件身份、latest、封口、报价和历史 provenance。v1 请求/结果/封口不增加字段；新身份信息只保存在本地执行快照与 process 记录，不回填已冻结历史。

## 配置与使用

[示例配置](../../config/research_runtime.example.json)不是活动配置，不会被自动读取。未提供 `--runtime-config` 时，两个适配器继续继承各 CLI 已有的模型、服务连接和环境；现有 CC + DeepSeek 设置继续生效。

配置只允许 `schema_version / profiles / active`。每个 profile 必须完整包含 `profile_id / revision / producer / harness / models`；`active` 将每个原生产身份绑定到一个 profile，正式请求所需生成端必须都有绑定。可保留多个候选 profile，但每个生产身份每批只选择一个。

| 参数 | Codex CLI | Claude Code CLI |
|---|---|---|
| `models.main.model` | `--model` | `--model` |
| `models.main.effort` | `-c model_reasoning_effort=...` | `--effort` |
| `models.subagent.model` | 当前适配器明确拒绝非 null 值 | 子进程环境 `CLAUDE_CODE_SUBAGENT_MODEL` |

null 表示继承，显式非空值才覆盖；不改变父进程或全局设置。当前不支持独立子代理 effort、压缩模型、任意参数/环境、动态导入、工具/权限策略覆盖或明文 API key。需要新能力时扩展可信适配器、校验器与测试，不能静默忽略。连接与凭据仍由既有 CLI 配置管理，当前配置不声称已冻结其 provider、权限、服务端权重或子调用实际模型。

以下命令是使用说明；执行 run 会实际启动研究，必须给真实的已验收请求：

```sh
python3 scripts/research_runner.py prepare --request /absolute/request.json --runtime-config /absolute/runtime.json
python3 scripts/research_runner.py run --request /absolute/request.json --generator claude --runtime-config /absolute/runtime.json
python3 scripts/research_scheduler.py plan --runtime-config /absolute/runtime.json
python3 scripts/research_scheduler.py run --runtime-config /absolute/runtime.json
```

`plan` 保持只读预览，不加载/验证 runtime 配置、不预留额度。`prepare` 冻结配置但不启动模型；runner 的 prepare/run 都接受显式路径。scheduler 在有待执行工作时，对实际待准入与恢复 profile 预检，通过后才预留额度。仅有已准备批次恢复时不读取当前配置；若同次 tick 还需要准备新批次，无效新配置会使本次整体准入停止，保留旧批次待恢复。

配置文件在一个 tick 的新批次准入预检中只读取一次，已验证副本用于该 tick 的新准备；已有批次始终使用自己的计划。CLI 参数 `--cli`，以及 scheduler 的 `--codex-cli / --claude-cli` 仍是显式安装路径覆盖；未覆盖则逐个按冻结 profile 的 adapter.executable 解析 PATH。不同批次同一生产身份可用不同的已注册适配器，不把可执行路径按生产身份合并覆盖。

定时安装器支持可选绝对路径 `--runtime-config` 并先校验配置；无该参数的 plist/wrapper 行为不变。只有显式 `--install` 才安装服务；本次未运行它。配置路径作为独立参数安全透传，不作为 shell 代码。已有服务未追加配置，继续原默认。

## 冻结、恢复与失败

新批次首次在 methods 准备时生成 `framework-snapshot/execution-plan.json`，绑定请求原始字节 SHA-256、batch_id 和全部选中 profile；快照 manifest 保存该文件路径与哈希。请求、包、prompt、input 与交付合同仍按原格式冻结。

计划严格校验选中生成端、字段及适配器能力。文件读取逐级使用目录 fd 和 O_NOFOLLOW，并拒绝符号链接、非普通文件与不匹配哈希；FIFO 不会阻塞。计划或声明缺一、无声明却注入计划、未知 adapter 或不支持的角色均明确拒绝。

已准备批次不再读取当前 profile 配置。没有计划声明及文件的旧批次按原默认恢复，不补写新计划，不修改旧请求/提示词/input/哈希；原 pre-snapshot 批次仍仅允许精确正文迁移。删除已声明的计划不会自动转成旧批次。冻结表示保存执行意图：null 仍继承启动时的 CLI 默认，模型别名也可能指向变化的服务端版本，不能据此声称模型权重可复现。

预检在首次/重试的 launched claim 前执行，验证可执行文件和必需 CLI flag；原 Codex 两级能力合同原样保留。启动前对比预检 profile/hash；重试还对比首次 process 记录；发布前再次验输入及 profile/hash。配置改变不触发额外票数、自动新重试或历史重写。预检不验证账号、网络、模型名/effort 值在服务端的有效性；真实执行失败沿用原回执和一次重试规则，不能声称“预检通过即投研成功”。

本地执行快照不是防御同一操作系统用户任意重写全部审计材料的独立安全边界；沿用仓库原有文件与执行权限信任模型。

## 扩展约束

新模型在已有适配器支持范围内，新增 profile 并选择 active 即可，影响新准备批次；旧批次继续原计划。可信新 CLI 适配器实现校验、预检、命令、环境、交付提示、回执及 observed model 接口，通过注册和合同测试后可选择；不能从 JSON 注入 Python 模块或任意命令。

当前扩展口针对本地 CLI 类 harness，共享 Popen/进程组生命周期。异步远程任务、SDK/native agent 和 Coze 不应强行伪装成 CLI；将来应扩展明确的执行生命周期及测试。新增 dsh 的真实生产身份仍需先隔离验证，再按提案推进两仓 request/result/seal/provenance 版本化兼容；不能把 dsh 标作 claude 绕过现有白名单，也不开放任意生产身份或新增共识席位。

回退到默认 profile 只影响新准备批次。旧版代码不能安全执行含 plan 的新批次；恢复必须保留本次执行计划读取及校验代码，不能用“旧代码忽略新字段”作为回退手段。既有成果、首次失败、重试记录和已证实风险事实保留。

验证结果及独立代码审查见[实施记录](../../research/investment/maintenance/2026-10-21/investment-2026-10-21-research-runtime-decoupling-codex.md)。本次只验证离线行为；没有新的真实模型调用、投研效果比较或生产切换结果。

2026-10-23 后续：用户授权 DSH 正式接替 CC。新 v2 身份、固定业务席位与部署边界由 [DSH 迁移 ADR](ADR-20261023-dsh-research-seat-migration.md) 接续；本文原解耦阶段结论和历史记录保持不变。
