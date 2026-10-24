# ADR：DSH 接替 CC 的研究业务席位

日期：2026-10-23（Asia/Shanghai）。状态：用户已授权正式替换；本机2026-10-23 22:34空闲重载生效，后续补齐启动环境修复并验证。结果见[实施记录](../../research/investment/maintenance/2026-10-23/investment-2026-10-23-dsh-production-rollout-codex.md)。

## 决策

新自动研究默认采用 Codex + DSH。DSH 使用真实 `generator=dsh`、`harness=dsh-cli` 和独立文件路径；不能冒称 Claude。下游固定映射 Codex→gemini、Claude/DSH→claude，DSH 接替已有席位而不新增票数；同批 Claude 与 DSH 互斥。条件 Coze 第三席、权重、拒绝/缺席处理、监控同完整度优先原 claude 业务席位等原规则不变。

`stock-research-request/v2`、`stock-research-result/v2`、`research-sealed/v2` 沿用原字段与哈希/路径/时间/九节门禁，只增加真实 DSH 身份与受控席位单射。新请求默认 codex+dsh/v2；显式 legacy codex+claude 可发布 v1 供回退。v1 严格只允许旧身份，原字节继续读取；result/seal 版本须跟随绑定 request，不得让 v1 隐式接收 DSH。不得从 JSON 任意配置业务席位或把 Claude+DSH 当两票。

研究 v4/audit-v2 与 R14 缺证不得 passed、scope 全部独立约束解除、holding/runtime/observation 边界保持现行方法。DSH 首份同端 baseline 为 null；旧 Claude 报告可以明确归属地参考，不能改名或冒充 DSH 自身基线。消费者按原 ID/scope/claim 合并 previous controls，旧未解除限制不会因换 harness、缺席或新端 null baseline 消失。

旧已冻结请求、计划、提示、回执、报告、队列、启动时间与额度保持原样；旧 Claude 批次仍用 CC 完成。新 profile 只影响新准备批次；回退也只影响新批，不能把已冻结 DSH 批改成 CC。保留历史 CC adapter 与 v1 是仍在使用的恢复路径，不是死代码。

## 执行与安全边界

DSH 使用已安装官方 CLI 的 headless 协议、每尝试独立状态、workspace-write 文件沙箱和明确无人机审批策略；不宣称具备 CC auto-review 等价能力。必须校验有序 completed 终态和严格正式回执，exit0/产物存在/settled 不能替代自然完成。主/子请求模型固定为已验证 DeepSeek Flash/high；凭据只在内存子环境提供，不写入仓库、patch、prompt、日志或模型回执。必要数据工具保留已有 Tushare/Jev 能力，按可信最小桥接提供；不恢复无关应用密钥。

每日05:00起一次、每日最多4只、168小时冷却、每端一次重试、实际启动后额度与原并发上限均不变。Coze仍仅同轮两基础席 P1.base 差异严格超过10%时触发，先提交原配对再补第三席，不重置已超时/失败请求。本迁移不发送测试邮件、飞书消息、不交易，也不把先前隔离实验提升入生产。

## 验收与回退

覆盖 v1 历史恢复、v2 端到端封口/消费、重复席位/错版本/错路径拒绝、Coze新旧基底与先后事务、跨日DSH启动额度、旧未解控制接续、DSH错误/取消/max-tokens/无终态、无密钥落盘、Jev/data工具。代码与离线测试通过并经独立对抗审查后才重载空闲服务；不取消在途研究、不重置 daily-check/队列或凭空启动新正式研究。小额真实 API 验证与离线合同测试分别报告；下一次定时完整研究结果不能提前宣称成功。

回退选择旧 publisher/profile 仅作用未来新批次，现有成果、风险事实与真实来源保留；禁止重写历史 CSV、报价或来源来掩盖切换。
