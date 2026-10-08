# 自动个股研究调度

本仓负责研究执行，`ai_investment` 负责信号/量价包及价格写回。默认双端为 Codex 和 Claude Code，遵循现有 stock-research 技能。Codex 的下游业务席位是 gemini，Claude Code 是 claude；本仓 JSON generator 不改名，实际模型从 CLI 日志另存，无可核验值则为 null。沿用 Claude Code 既有后端配置。

在本仓运行（Python 3.10+，只用标准库；示例复用相邻仓虚拟环境）：

```bash
../ai_investment/myenv/bin/python scripts/research_scheduler.py plan
../ai_investment/myenv/bin/python scripts/research_scheduler.py run
```

plan 不写台账、不启动研究。run 会真实使用 CLI 账户；默认每端超时3600秒，串行双端/逐股执行。每天最多4只上市证券，两端合用1个名额；超过4只按超30天、独立AI建仓/清仓、监控/财报/其它、纯止损四档排序，未入选顺延。失败仍占名额，A/H分别计数。不含新触发契约的旧批次不自动领取；手动 research_runner 不能作为绕过额度的自动入口。

台账在 `output/research_queue/state.json`；`sealed/` 是 ai 消费依据，`refresh-needed.json` 提供延期财报重抓线索。已开始的任务恢复时先查原 entry/process/claim；不能确认原进程终止时不重复启动。坏账或初始化后台账消失拒绝运行，不能删除台账重置额度。需要备份整个 queue、相应 `output/runs/investment` 和正式 `research/investment/companies` 文件。

安装前先输出 plist 供核对，传入本机已验证的绝对可执行路径：

```bash
../ai_investment/myenv/bin/python scripts/install_research_service.py \
  --python /绝对路径/ai_investment/myenv/bin/python \
  --codex-cli /绝对路径/codex --claude-cli /绝对路径/claude
```

增加 `--install` 才会安装到当前用户 LaunchAgents，标签为 `com.investment-research-methods.research`；每15分钟检查一次队列，运行中的实例不会重入。默认只展示 plist；本次开发未安装服务。已有服务的替换需先 bootout 并移除原 plist，再执行安装，不通过重复安装开启第二份调度。

启动脚本与 ai 已有 launchd 入口一致，只加载 `~/.zshrc` 的 export 行，不输出凭据；runner 会移除生产应用环境变量。登录状态、模型访问权限、CLI技能/工具能力及睡眠/合盖条件需在部署前实测。服务日志在 `output/research_queue/service*.log`；逐股过程保存在原 runner 目录。没有新候选时不调用 CLI。

暂停研究服务（保留所有台账）：

```bash
launchctl bootout gui/$(id -u)/com.investment-research-methods.research
```

AI 每天08:30/16:15消费已封口结果，`config/research_loop.json` 默认 preview。价格/监控原始报价、派生 P2 和最终 CSV 行分别存入预览；结构通过不能证明事实、估值或监控变量语义正确。只有完成影子质量验收后才考虑生产开关；本仓研究进程不负责飞书或生产CSV写入。
