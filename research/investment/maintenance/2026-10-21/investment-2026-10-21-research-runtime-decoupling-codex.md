# 股票投研执行架构解耦实施记录

日期：2026-10-21（Asia/Shanghai）。生成端：Codex。按用户授权完成[提案](investment-2026-10-21-research-runtime-architecture-proposal-codex.md)第一步：等价抽取现有两端、加入执行配置和冻结计划、接通调度及服务参数入口，并完成离线回归与独立代码审查。保持现有 Codex/Claude 默认及 CC 的既有模型连接；暂不切换 dsh。

## 结果与实际范围

- 新增 `scripts/research_runtime.py`，严格校验非秘密 profile，支持多个候选及每生产身份一个活动配置。主模型/effort 和 Claude 子模型可显式配置，未指定仍继承 CLI 原设置。
- 新增 `scripts/research_harness.py`，集中 Codex CLI 与 Claude Code CLI 的能力检查、命令、环境、交付提示、回执和模型事件解析，可信代码注册适配器。通用执行仍负责进程监督、超时/取消、验收、暂存及发布。
- runner 与 scheduler 按选中 profile 路由；新批次在框架快照中保存完整 execution plan，绑定原请求字节和哈希。当前配置改变不影响已准备批次或重试，同 tick 新配置只读一次。不同批次同生产身份不同 harness 分别解析 executable。
- prepare/run/scheduler 与定时服务安装器支持显式 `--runtime-config`；示例文件不自动启用。活动服务未重装，现有模型、权限、调度周期及预算配置未切换。

研究方法、参与策略与统一验收仍由原属主维护，没有复制成另一套规则。没有改动 canonical/compact、skills、共识代码、Coze 条件或相邻消费仓源码。当前 v1 请求/结果/seal、v4/audit-v2、报价来源与历史 provenance 字段不变；新追踪信息只进入新批次本地执行快照和 process 记录，不原位补写旧产物。

旧 prepared 批次继续按原冻结合同恢复，无执行计划的旧批次保留原默认；原请求、prompt、input 及哈希保持。历史 pre-snapshot 迁移仍要求精确原正文。真实模型只取运行事件披露，未知保留 null，不把 requested model 写成 actual model。

## 审查与修复

实现前进行了冻结/失败边界预审，适配器集成及最终六维审查由独立代理只读完成。主要修复已落地并复测：

1. 重试核对首次实际 profile 与计划哈希；同时改写计划与 manifest 哈希，也不能使已执行的批次重试换模型。
2. 预检到启动、运行到发布分别复核 profile/hash，阻断执行期间漂移和正式发布。保留原最后一次完整验证后的内存包快照语义，原数据变更回归继续通过。
3. scheduler 延迟到实际 profile 才解析默认可执行，避免 CLI 默认过早绑定，以及同生产身份混合新旧 harness 的路径覆盖。
4. 计划读取逐级使用目录 fd/O_NOFOLLOW，拒绝符号链接与非普通文件，FIFO 不阻塞；注册时明确校验交付提示能力声明。

默认两端 argv 与旧实现逐项相同；独立探针比较默认提示词字节、make_prompt/input_record/receipt_schema/accepted_entry/communicate 的 AST，均保持等价。最终源码六文件 SHA 与独立审查对象一致；随后文档及示例另经只读复核，没有超出实现的承诺。最终审查未发现未解决的阻断问题。

审查底稿：

- `output/audits/investment/2026-10-21/runtime-architecture/preflight-review.md`
- `output/audits/investment/2026-10-21/runtime-architecture/adapter-integration-review.md`
- `output/audits/investment/2026-10-21/runtime-architecture/final-code-review.md`

## 实际测试

| 验证 | 实际结果与范围 |
|---|---|
| 本仓全量离线回归 | `python3 -m unittest discover -s tests -v`：**906 项全部通过，140.070 秒**。含新增 88 项，覆盖配置、适配器、实际假 CLI 参数/环境、旧批次、冻结/篡改、重试、并发、取消、进程组清理、预算、封口及 Coze 等原有回归 |
| 相邻消费仓兼容 | `METHODS_CONTRACT_ROOT` 显式指定本工作区，Python 3.11.7 pytest 执行 two_price_methods_integration / research_writeback / model_quote_store / model_consensus_config：**103 项全部通过，2.88 秒**；包含本仓假 CLI → seal → consumer → 临时 CSV/控制事件与幂等回放，全部临时路径，无生产写入 |
| 股票结构治理 | `python3 scripts/investment_framework_governance.py --check` 通过；canonical/compact 字节同时与 HEAD 核对一致 |
| 期货结构治理 | `python3 scripts/futures_framework_governance.py --check` 通过 |
| 编译、shell 与差异 | 五个生产 Python 模块 py_compile、`zsh -n deploy/launchd/run_research.sh`、`git diff --check` 全部通过 |
| 配置/文档 | 示例经共享严格校验器通过，全部模型覆盖为 null；新文档本地引用存在 |

全量测试日志：`output/audits/investment/2026-10-21/runtime-architecture/final-unittest.log`；消费兼容日志：同目录 `consumer-compatibility-pytest.log`。基线 818 项在沙箱内仅有两项因禁止 ps 检查而报错；最终测试在获准只读进程检查的执行环境重跑，全量通过，没有弱化或跳过这些测试。

上述均为离线代码及合同验证，不是实际账号/服务端模型/effort 有效性、联网投研质量或收益验证。测试没有发出真实模型请求、安装/重载服务、修改全局模型配置或生产数据。结构治理不证明投资方法有效性或完整语义等价。

## 使用与后续边界

配置字段、命令、能力矩阵、恢复与回退边界见[ADR](../../../../docs/adr/ADR-20261021-research-runtime-profiles.md)，起点为[示例配置](../../../../config/research_runtime.example.json)。不传配置保持现有默认；要换已有 adapter 支持的模型，创建显式 profile 并用于新批次。null 仍继承启动时的外部 CLI 设置；冻结别名不保证底层权重固定。

本轮提供本地 CLI 类型 harness 的真实扩展口，不承诺任意 SDK/异步服务零适配。新增 harness 要实现及验收可信 adapter；新增 dsh 真实生产身份仍需按提案先做隔离验证，再协调两仓版本化 request/result/seal/provenance，不能标作 claude 进入旧合同。多个 profile 不自动增加投票或修改权重，本次没有推进正式切换。

本次改动保存在工作区，没有提交、推送或创建 PR；已有无关未提交产物保留。
