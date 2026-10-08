# 自动个股研究调度

本仓负责研究执行，`ai_investment` 负责信号/量价包及价格写回。默认双端为 Codex 和 Claude Code，遵循现有 stock-research 技能。Codex 的下游业务席位是 gemini，Claude Code 是 claude；本仓 JSON generator 不改名，实际模型从 CLI 日志另存，无可核验值则为 null。沿用 Claude Code 既有后端配置。

在本仓运行（Python 3.10+，只用标准库；示例复用相邻仓虚拟环境）：

```bash
../ai_investment/myenv/bin/python scripts/research_scheduler.py plan
../ai_investment/myenv/bin/python scripts/research_scheduler.py run
```

plan 不写台账、不启动研究。run 会真实使用 CLI 账户；默认每端超时3600秒，串行双端/逐股执行。定时入口每日北京时间05:00只检查一次（`run --scheduled`），即使没有输入也保存daily-check.json，当天不再自动检查；重启服务不启动研究。每天最多4只上市证券，两端合用1个名额；超过4只按超30天、独立AI建仓/清仓、监控/财报/其它、纯止损四档排序，未入选顺延。失败仍占名额，A/H分别计数。不含新触发契约的旧批次不自动领取；手动 research_runner 不能作为绕过额度的自动入口。

台账在 `output/research_queue/state.json`；`sealed/` 是 ai 消费依据，`refresh-needed.json` 提供延期财报重抓线索。已开始的任务恢复时先查原 entry/process/claim；不能确认原进程终止时不重复启动。坏账或初始化后台账消失拒绝运行，不能删除台账重置额度。需要备份整个 queue、相应 `output/runs/investment` 和正式 `research/investment/companies` 文件。

用户确认已手动接手的股票，可在同一 queue 中保存 `manual_holds.json`（`research-manual-holds/v1`）。顶层为 `schema_version` 和 `tasks`；后者按 task_id 映射 `event_key`、`reason`、带时区的 `created_at`。plan/run 均跳过这些证券的同轮信号，包括中断恢复和次日重新抓包；触发证据改变产生新事件后可正常入队。这是人工声明，不代表研究完成，不复用人工报告或伪造封口。格式损坏时停止调度。

增加或清除人工接手记录前先暂停本服务，确认本服务在途子进程已结束，在 `queue.lock` 下备份并原子写入记录。接手条目结束自动恢复状态：已启动并取消的记 failed，未启动的改回 pending。已实际启动的名额仍保留；确认两端均没有 claim/进程记录的预留才可释放。保留旧 entry/process/claim 和输入，不修改用户手动任务。人工研究已完成且需重新允许同轮信号时，显式删除对应记录；不得自动把“已接手”标成“已完成”。

安装前先输出 plist 供核对，传入本机已验证的绝对可执行路径：

```bash
../ai_investment/myenv/bin/python scripts/install_research_service.py \
  --python /绝对路径/ai_investment/myenv/bin/python \
  --codex-cli /绝对路径/codex --claude-cli /绝对路径/claude
```

增加 `--install` 才会安装到当前用户 LaunchAgents，标签为 `com.investment-research-methods.research`；StartCalendarInterval每日05:00，无StartInterval或RunAtLoad，运行中的实例不会重入。默认只展示plist。已安装服务可加 `--replace-when-idle` 等在途研究结束后自动备份旧plist、替换并重载；不得为更改排期取消研究。

启动脚本与 ai 已有 launchd 入口一致，只加载 `~/.zshrc` 的 export 行，不输出凭据；runner 会移除生产应用环境变量。登录状态、模型访问权限、CLI技能/工具能力及睡眠/合盖条件需在部署前实测。服务日志在 `output/research_queue/service*.log`；逐股过程保存在原 runner 目录。没有新候选时不调用 CLI。

暂停研究服务（保留所有台账）：

```bash
launchctl bootout gui/$(id -u)/com.investment-research-methods.research
```

AI 每天07:30/22:00消费已封口结果；用户2026-10-08已明确授权真实飞书/CSV写回，取代原影子期门禁，接纳当天起的自动批次。价格/监控原始报价、派生P2和最终CSV行仍保存预览和事务回执；结构通过不能证明事实或语义正确。本仓研究进程不负责生产写入。

统一日志：相邻ai仓的 `logs/research_loop/events.jsonl`，采用该仓的唯一标准库日志实现。定时检查记录空检查、候选/人工接手、名额、各端结果与实际模型、封口路径；ai记录触发、飞书确认及CSV前后指纹/行值。保持原service/events/完整回执，用batch_id与task_id串联；不记录环境凭据或CLI全文。该统一日志由ai每日22:45备份，23:00日终审计。周末08:00数据包晚于每日研究检查，供人工使用，不在当天再自动领取。
