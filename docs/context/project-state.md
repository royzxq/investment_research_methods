# 项目状态与迁移边界

核对日期：2026-10-05。这里记录接续线索，不替代 canonical，也不把历史行情、账户或拟议更新当作当前事实。

## 当前权威

| 轨道 | 方法与状态 | 当前配套 |
|---|---|---|
| 期货 | [canonical](../../framework/futures_framework.md) v2.27；整理 9/20，市场状态 9/19，文中最新行情日 9/18 | [compact](../../framework/futures_framework_compact.md)、[数据协议](../../framework/FUTURES_DATA_PROTOCOL.md) v2.26、[future_data.py](../../scripts/future_data.py) v1.16；版本不同并非当然不兼容 |
| 股票 | [canonical](../../framework/investment_framework.md) 与 [compact](../../framework/investment_framework_compact.md) 整理 9/21，市场状态沿用 9/19 | 原三阶段 `projects/*/INSTRUCTIONS.md`；`stock_data_pack.py` 尚未找到，不声称数据脚本已迁入 |
| ETF | [canonical](../../framework/etf_framework.md) v2.1，八主题、双月评审 | v2.0 格式快照兼容；最近评审为 [10/01 review](../../research/etf/reviews/2026-10-01/etf-2026-10-01-review.md)，正文已于 10/02 修订；旧 monthly-review 不作为现行一期 |

## 待接续事项

- 2026-10-05 个股入口：`stock-research` 与 `deep-research-auto` 现维护于 `.agents/skills/`，`.claude/skills/` 同名文件为兼容入口。个股最终 JSON 使用 `stock-research/v2`，仅 `meta/price_map/monitoring`；计算工具为 `scripts/stock_price_map.py`，旧 v1 只作复评历史输入，不能直接迁移单位混杂的 V50 或示例价格。10/05 的 600066、01952 报告与 JSON 保留原研究内容（目录迁移仅修正引用），尚未按修复版重新研究；原参数空值、P2/换汇及事实冲突须在后续复评中解决，不能视为已修正价格。
- 股票 [9/26 change-decision](../../research/investment/weekly/2026-09-26/investment-2026-09-26-change-decision.md) 与期货 [9/26 change-decision](../../research/futures/weekly/2026-09-26/2026-09-26-change-decision.md) 均记录 `update_needed=yes`、`update_level=light`，尚未见同日期适配报告。它们是待处理决策；本次迁移没有实施适配，期货报告提议的 v2.28 尚未成为当前框架。
- 期货 9/26 报告称最新快照为 9/19；本工作区另有在迁移前 HEAD 已提交的完整 `research/futures/snapshots/2026-09-21-data-snapshot.txt`（v2.27/v1.16）。本地接续按真实文件、完整标记和各行情日期选择，不继承该旧断言；发布/无人值守流程按入口只使用已提交快照。9/21 也不能代表 10/04 行情。
- 工作区的完整 `research/etf/snapshots/etf-2026-10-02-data-snapshot.txt` 在目录迁移前 HEAD 已提交；当前新路径仍属本地待提交迁移。按 10/04 评审日距今两天，格式可通过前置；各指数实际行情锚与公开估值、成分、全收益缺口仍须按正文核对。迁移未运行新的行情脚本或研究。
- [ETF 比较偏差与置换诊断](etf-timing-validation.md)、[恒指全收益代理](hsi-total-return-proxy.md) 保存独有历史发现，均待复现。旧收益、显著性、接口成功率不升级为已核实结论。
- 2026-10-05 核对本机 Codex 自动化：期货与股票周更均 ACTIVE，分别调用本仓对应 skill，并在独立 worktree 按既有授权发布；PR #28 监控 PAUSED。未发现本机 ETF 定时定义，远端 Claude Routine 未核验。本次只改输出契约，未更改调度或发布授权。自动化提示词未硬编码旧报告路径，无需修改；远端运行基线需包含完整迁移后才使用新版契约，不夹带本地迁移发布。

## 历史资产的处理

- `.claude/skills/` 和专属项目会话、七份记忆有备份；Codex 使用 `.agents/skills/` 的四个新入口及阶段 references。通用投研、飞书技能与新版吸引子已在 Codex 存在，未再复制。
- Claude 旧“尚未推送”等记忆已落后于当前 Git 历史，不导入为永久规则。`framework/reference.md` 依赖缺失文件，`research/futures/archive/2026-09-13-legacy-output.txt` 为旧期货输出；不替代现行方法。
- 迁移前 HEAD 已提交的五张 9/25 core 卡片属于旧 ETF 方案；现行 v2.1 的八主题边界优先。`research/etf/archive/legacy-cards/v1-archive/` 为首期承接历史，不能从旧卡片推定当前账户。
- `.claude/worktrees/etf-track+day0` 无独有提交且为 main 祖先；原目录仍保留，未删除、合并或当作新入口。`.venv/` 与 `output/` 保留本地环境和缓存，不把它们当作方法权威。

## 私有备份与恢复

仓库根 `.migration-backups/2026-10-04-claude-to-codex/manifest.json` 记录 SHA-256、大小、文件数和原始未提交研究校验值。目录权限为 700，归档/配置备份为 600；整个目录被 Git 忽略。

| 归档 | 内容 |
|---|---|
| `working-assets.tar.gz` | 原 11 个 Claude skill 与迁移前未提交的 11 个研究/草稿文件 |
| `claude-project-history.tar.gz` | 本项目 Claude 会话与七份记忆 |
| `etf-study-2026-09-30.tar.gz` | 原临时 scratchpad 的 38 个回测、预注册、结果和数据文件 |
| `market-data-cache.tar.gz` | `output/` 的行情及原始缓存 |

另保留 `codex-config.before.toml`、`README.before.md`、`gitignore.before`。备份可能含私人会话或账户资料，不作为可共享研究附件。

恢复时先与 manifest 核对归档 SHA-256，用 `tar -tzf` 查看成员，再解压到独立临时目录后选取所需文件；不要直接覆盖当前工作区。Gemini 的注册在本机全局 Codex 配置，回滚该注册时只移除对应 `mcp_servers.gemini-search` 段并保留之后其他配置；完整旧配置仅用于对照，不能覆盖新工作。

## 本次迁移验收

- Codex 本地 app-server `skills/list` 实际发现四个入口，均为 `scope=repo`、`enabled=true`，仓库技能解析错误为零；四项 `quick_validate.py` 通过。
- 离线全量回归 231 项通过，框架结构检查通过。回归曾复现 HEAD 基线的一个 error 和两个子测试失败；仅为两个隔离测试夹具补注入 `daily_settlement_changes` 与 `math` 后通过，未改生产脚本、策略或参数。
- 独立只读场景验收检查单阶段 compare、无更新仍出期货审计、账户/专业资料缺口、ETF 10/04 合格与 10/20 过期前置、缺适配报告时 data-sync 停止，以及精简保真约束。验收为前置检查和任务推演，未执行新的完整投研。
- 四个归档 SHA-256、全部成员可读性、11 个迁移前工作文件原样与私有权限已核验。原 MCP 定义保留；新增配置与文件未出现现有 Gemini/Tushare 凭据字面值。
- Gemini 注册、stdio 握手、工具发现及六项离线回归通过；Codex 本地 `mcpServerStatus/list` 实际加载 `gemini-search` 并发现 `gemini_web_search`。允许联网的真实 API 查询返回 HTTP 400 地区不支持，成功搜索尚未通过；[上期所官网](https://www.shfe.com.cn/) 的内置搜索及正文读取兜底已完成。已有聊天重新载入 MCP 配置与可用地区网络条件仍须在后续环境确认。

## 研究目录迁移（2026-10-05）

输出契约见 [research 导航](../../research/README.md)，逐文件旧新路径与校验值见 [迁移清单](../research-layout-migration.json)。本轮仅改目录、引用和读写接口，不更新市场判断；历史审计 JSON 与 ETF 冻结预注册字节保留。工作区既有未提交技能与个股研究内容继续保留。自动化读取已提交快照的要求不变，新路径未提交时不能冒充已提交输入。
