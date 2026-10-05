# investment_research_methods

研究输出按领域与日期整理，入口见 [研究导航与输出契约](research/README.md)及[报告索引](research/INDEX.md)。正式成果留在 `research/`，缓存、中间文件和可重建索引留在被忽略的 `output/`。

股票、期货、主题 ETF 三条研究轨道的共享仓库。后续工作使用 Codex；原有方法、脚本和日期报告继续原位维护。项目约定见 [AGENTS.md](AGENTS.md)，当前版本、待办与历史边界见 [项目状态](docs/context/project-state.md)。

## 在 Codex 中使用

在本仓库打开 Codex 聊天，直接描述任务，或使用以下 skill 名称。项目入口位于 `.agents/skills/`；原 Claude 的七个阶段包装已成为股票/期货入口的 references，仍支持单阶段请求。

| 入口 | 示例 | 流程与交付 |
|---|---|---|
| [stock-research](.agents/skills/stock-research/SKILL.md) | “调研 600066 宇通客车”；“给 01952 做价格地图” | 自动取证 → 框架判断 → 参数论证与数值校验；完整报告 + 仅含价格地图和监控变量的 v2 JSON |
| [deep-research-auto](.agents/skills/deep-research-auto/SKILL.md) | “深度调研这个问题”，或由个股技能调用 | 多代理取证 → 关键冲突裁决 → 定向补研 → 可追溯报告与笔记 |
| [investment-weekly-review](.agents/skills/investment-weekly-review/SKILL.md) | “执行股票完整周更”；“仅比较指定的新旧股票研究报告” | 元研究 → 变化检测 → 条件适配 → 保真精简；报告带 `investment-` 前缀 |
| [futures-weekly-review](.agents/skills/futures-weekly-review/SKILL.md) | “执行期货完整周更”；“仅同步本次适配的数据脚本” | 元研究 → 变化检测与每期审计 → 条件适配 → 脚本同步 → 诊断重评 → 保真精简；日期报告无前缀 |
| [etf-review](.agents/skills/etf-review/SKILL.md) | “执行本期 ETF 主题评审”，可附持仓 | 每两个月评审定投主题与持有主题目标；报告带 `etf-` 前缀 |
| [framework-condense](.agents/skills/framework-condense/SKILL.md) | “仅同步期货 canonical 与 compact” | 保留五元组、数值、逻辑、例外、稳定编号及当前状态，完成七项自审 |

日期默认北京时间当天，可明确指定 `AS_OF_DATE`。默认本地保存；单阶段请求在该阶段结束，同日已有产物先核对并复用。需要框架更新时使用分支或隔离 worktree；只有已明确授权发布时，才提交、推送并统一创建一个 PR，人工审核后合并。原 routine 的自动推送行为不作为新任务授权。

## 方法与证据

- **期货**：[canonical](framework/futures_framework.md) 当前 v2.27；[compact](framework/futures_framework_compact.md) 为同一框架的执行导航。[数据协议](framework/FUTURES_DATA_PROTOCOL.md) v2.26 默认 `public_data`，先满足活跃模型的最小公开数据，专业增强项按各自模型处理。研究先给逻辑、方向、价格计划与期限，实际账户、挂单、费用、保证金和许可另核。
- **股票**：[canonical](framework/investment_framework.md) 是逐股研究的参数化模板，保留公司、代码、估值日期占位符；[compact](framework/investment_framework_compact.md) 不另设判据。`projects/{meta_investment_analysis,investment_change_analysis,investment_adaption}/INSTRUCTIONS.md` 保留原方法与字段契约。空 day-0 基线按首次运行处理，本期元研究结果始终必传。框架提到的 `stock_data_pack.py` 尚未在本仓及关联 `ai_investment` 找到。
- **ETF**：[canonical](framework/etf_framework.md) 当前 v2.1，在八个主题研究池中回答未来两个月定投哪 2–3 个主题，以及持有主题的目标权重和处理。未提供持仓时只给主题名单；宽基 50% 与红利低波 20% 是用户长期安排，本仓不研究。只交付研究结论，执行由用户处理。

canonical 是方法、参数及歧义裁决的权威；compact 必须保真同步。框架只局部更新受影响条目，规则与动态状态分区维护，历史保留在 Git 与日期报告。适配报告链接完整文件，不粘贴框架全文。

快照生成日、实际行情日、规则整理日与评审日分别记录，不能把旧报告的“最新”声明沿用到新一期。完整快照末行须有“快照完成”；`.partial` 不可引用。ETF v2.1 接受 v2.0 快照格式，另检查不晚于评审日、10天以内和两只指定指数，详见入口。

## 本地取数与校验

解释器、凭据继承和外部研究池配置见 [运行环境](docs/context/environment.md)。脚本读取已有 `TUSHARE_TOKEN`，不把 Token 写入仓库。以下命令从仓库根运行：

```sh
/Users/xinquanzhou/miniconda3/bin/python3 scripts/future_data.py --as-of YYYYMMDD
/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --as-of YYYYMMDD --pool-csv /absolute/path/investment_prediction.csv
```

ETF 研究池可由技能读取 `ETF_POOL_CSV` 并转为 `--pool-csv`；脚本自身不读取这个环境变量。不默认覆盖同日快照。联网、账户权限和字段可用性以实际调用验收，不能将离线测试或 Token 存在当作线上验证。

- [future_data.py](scripts/future_data.py) 当前 v1.16，负责取数、研究候选和情景预检。`POSITIONS` 为空不证明账户空仓；2ATR 数量与月差分位不等于最终手数或交易许可。
- [stock_price_map.py](scripts/stock_price_map.py) 负责个股价格地图的离线计算与 `stock-research/v2` 导出：`build --input <临时模型> --output <新JSON>` / `check <JSON>`。固定币种/股本口径，P2 从 P1 下沿计算；校验不代表证据或估值合理性已获确认，完整论证留在报告。
- [price_evidence.py](scripts/price_evidence.py) 区分 settle/close、SC 结算周涨和固定合约对的同期样本。周涨以最新完成行情日减七个自然日；不使用收盘替代结算护栏。快照还准备合约对研究 CSV 与 `output/cache/futures/spread_research_<AS_OF>.json`，不自动替换当前合约或授予许可。
- [futures_risk.py](scripts/futures_risk.py) 提供离线 A 计划校验与风险容量计算：`validate-a --input plan.json` / `size --input sizing.json`。A 校验仅支持 MA/RB/SR 同品种 1:1 月差，必填 `price_unit="CNY/tonne"`，Entry/SL/TP 为绝对价差。单位不兼容不换算，缺实际账户、止损或容量保留 `null`。低敞口上限按用户配置取 `min(净值×3.5%, 5000元)`，含持仓与挂单风险，常规和当前上限分列。
- [执行审计模板](projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md) 是每期诊断唯一口径。无论框架是否更新都生成执行审计；[validate_futures_audit.py](scripts/validate_futures_audit.py) 校验 schema 3（schema 2 仅兼容历史），不验证来源真伪、收益或交易许可。
- [etf_index_registry.json](framework/etf_index_registry.json) 为指数清单；[etf_calc.py](scripts/etf_calc.py) 为纯函数计算器。旧回测只按其记录的判据解释；新增历史发现见 [ETF 验证记录](docs/context/etf-timing-validation.md) 和 [恒指全收益代理](docs/context/hsi-total-return-proxy.md)，两者均待复现。

```sh
/Users/xinquanzhou/miniconda3/bin/python3 -m unittest discover -s tests -v
python3 scripts/futures_framework_governance.py --check
python3 scripts/validate_futures_audit.py --input research/futures/weekly/YYYY-MM-DD/YYYY-MM-DD-execution-audit.md
```

结构校验不证明语义等价或投资有效性；汇报实际结果和未验证范围。

## 默认搜索与 Gemini 暂停

服务代码已迁入 [.codex/mcp/gemini_search_mcp.py](.codex/mcp/gemini_search_mcp.py)，只使用 Python 标准库。当前机器已在 `~/.codex/config.toml` 注册 `gemini-search`，通过 `env_vars` 继承 `GEMINI_API_KEY`；可选 `GEMINI_SEARCH_MODEL` 和 `GEMINI_SEARCH_API_TIMEOUT`。密钥值不写入配置或仓库。

2026-10-05 起，普通联网检索默认使用会话内置网页搜索和页面读取，暂不调用或先尝试 `gemini_web_search`。全局规则、项目规则、深度研究技能和本机股票/期货周更任务采用同一路由；Codex 的 Gemini MCP 注册保留，设置 `enabled = false`。关键事实读取原始来源后引用；OpenAI 产品问题遵循 `openai-docs`。

2026-10-04 验收：注册、stdio 握手与工具发现通过；真实 Google API 调用返回 HTTP 400 `User location is not supported for the API use.`，目前无法验证成功搜索。内置搜索与页面读取兜底已实测通过。地区限制属于待解决的外部运行条件，注册成功不等于 Gemini 搜索已可用。

服务代码和环境变量配置保留，便于以后明确要求时恢复。命令 `codex mcp get gemini-search --json` 可检查注册及启用状态；已有聊天可能仍保留旧工具或指令，新会话载入更新后的配置。

## 迁移边界与备份

Codex 已有的通用投研、飞书技能和新版吸引子继续复用，避免平行副本。独有项目约定写入 `AGENTS.md`，环境与研究发现写入 `docs/context/`；没有手工填充 Codex 原生自动记忆库。`.claude/` 的 `stock-research`、`deep-research-auto` 为共用技能的兼容入口，其余原文件保留为历史来源。

迁移前项目会话、七份记忆、独有 skills、未提交研究、临时回测和行情缓存已保存到本机私有 `.migration-backups/2026-10-04-claude-to-codex/`，带 SHA-256 清单并被 Git 忽略。恢复步骤见项目状态文档。`.venv/` 与旧 Claude worktree 保留并忽略，未删除或合并。股票/期货周度、ETF 双月的研究节奏保留；本次未创建定时任务，原云端 Routine 的运行时间与授权需单独衔接。
