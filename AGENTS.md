# 项目执行约定

本仓维护股票、期货与 ETF 三条研究轨道。现有 `framework/`、`projects/`、`scripts/` 和 `research/` 继续原位使用；迁移不改变投资方法或执行交易。日期、评审周期与报告名使用 `Asia/Shanghai`。

## 入口与权威

| 请求 | Codex 入口 |
|---|---|
| 股票市场元研究、变化比较、框架更新或完整周更 | `.agents/skills/investment-weekly-review/SKILL.md` |
| 期货元研究、执行诊断、框架/脚本同步或完整周更 | `.agents/skills/futures-weekly-review/SKILL.md` |
| 主题 ETF 双月研究与持仓目标复核 | `.agents/skills/etf-review/SKILL.md` |
| 股票/期货 canonical 与 compact 保真同步 | `.agents/skills/framework-condense/SKILL.md` |

按请求读取对应入口及需要的阶段 reference；用户只要求单阶段时仅执行该阶段。阶段方法继续使用 `projects/*/INSTRUCTIONS.md`，不假定存在专用 skill 调用 API。

- 方法、参数及歧义裁决以现行 canonical 为准：`framework/investment_framework.md`、`framework/futures_framework.md`、`framework/etf_framework.md`。compact 是同一框架的执行导航，保留数值、逻辑、例外与解除条件。
- 股票文件以 `investment-` 开头，ETF 文件以 `etf-` 开头，期货日期报告无前缀；发现历史时严格匹配本轨文件类型。实际读取完整标记、数据日期和行情锚，不继承旧报告对“最新”的断言。
- ETF 框架 v2.1 接受 v2.0 快照；旧卡片、旧 schema、旧预算和已删除的分配工具仅属历史。
- 当前待办与历史边界见 `docs/context/project-state.md`；运行数据脚本或排查环境时读 `docs/context/environment.md`。
- 涉及回测判据时读 `docs/context/etf-timing-validation.md`；涉及恒指含分红序列时读 `docs/context/hsi-total-return-proxy.md`。两者是待复现研究发现，不能自行升级为有效投资规则。
- `.claude/` 保留为历史来源，不是 Codex 技能发现位置。`framework/reference.md` 依赖缺失文件，是未采用草稿，不作为第三份权威框架。

## 搜索与证据

- 普通联网检索优先发现并使用 `gemini-search` MCP 的 `gemini_web_search`。缺少该工具，或返回 `[SEARCH_FAILED]` / `[gemini_web_search]` 失败标记时，使用当前会话内置网页搜索与页面读取；完成兜底后无需再重试 Gemini。
- Gemini 输出和检索摘要用于发现资料；关键事实继续打开原始来源核验并记录日期，不能声称未读的正文已验证。OpenAI 产品问题遵循 `openai-docs` 的官方来源顺序。
- Gemini 密钥只从 `GEMINI_API_KEY` 环境变量读取；不输出变量值，不将密钥写入仓库。服务实现为 `.codex/mcp/gemini_search_mcp.py`。

## 输出、更新与协作

- 研究报告写入原 `research/` 命名体系；复用已有通用投研 skills 的证据与计算方法时，保留本仓输出契约、参数及用户裁决。
- 默认本地保存。运行研究或更新框架的请求本身不授权 Git 推送、创建/合并 PR、对外发消息或交易；用户已有明确授权时按授权完成，不重复确认。
- 框架发布使用分支与单一 PR；子阶段不各自开 PR。已授权的发布按原流水线处理研究日志与框架分支；创建 PR 后附加到当前 Codex 聊天。分支默认 `codex/` 前缀。
- 同日重复运行先检查已有产物；默认复用或写隔离输出，覆盖须有用户明确指示。取数脚本仍以正式完成标记区分 `.partial`，不以已有文件名证明完成。
- 多个聊天要同时写同一批文件时使用独立 worktree 或分配互不重叠的文件；不要移除仍由活动会话持有的锁。Claude 的 `EnterWorktree`、旧分类器限制和写锁实现不自动适用于 Codex。
- 项目规则与动态市场状态保持在原文件内分区；历史留在日期报告及 Git，不新增平行规则副本或重写未受影响条目。

## 验证

- 数据脚本优先用环境文档中的可用解释器，继承 `TUSHARE_TOKEN`；缺数据或账户字段保持缺口和 `null`，不推断真实成交或执行许可。
- 框架保真结构检查：`python3 scripts/futures_framework_governance.py --check`；它不证明全部语义等价。
- 离线回归：`python3 -m unittest discover -s tests -v`。新增/更新 skill 运行 bundled `skill-creator/scripts/quick_validate.py`，另检查单阶段边界及领域契约。
- 汇报实际运行结果，区分结构检查、离线测试、真实 API 验证与未验证内容；非平凡修改优先检验边界和失败路径。
