# 基础封存事件触发 Coze

2026-11-02，替代每15分钟候选扫描。本轮由 gpt-6-astra/xhigh 直接补齐实现与离线失败路径验证，独立 Astra/xhigh 评审无剩余代码阻塞；此次范围止于已授权本地提交。未启用、未发送，11月2日三只不补发。

基础双模型或授权恢复 seal 完成后同步写本地持久化事件，事件键为 seal SHA256；不在 provider slot 中验证/取网/等待 Coze。通知异常只记录独立 journal，不使基础研究失败。独立 worker 从封存头部的 task_id 选定同证券，只对该证券完整验证；文件名不作身份依据，合法恢复或重命名文件仍参加最新轮判断。准备/发送检查不每10秒全量验证候选，已发送请求收取无需扫描封存。验证不可变 seal、请求、双席、SH/SZ、明确 P1 严格 >10%、最新轮与完整冻结包；新第三意见仍无 research_controls，不能解除主研究限制。历史邮件与 CLI 证据兼容不变。

`config/coze_events.json` 默认 disabled、dispatch_disabled、not_before=2026-11-03T00:00:00+08:00，CLI 自身也保持关闭。启用必须填明确授权的未来 request.created_at 起点；通知和恢复都检查此边界，不能隐式回补今日或历史。首次准备后等待完整公开包审阅：approve 显式确认后才允许独立 worker 准备、绑定和发送。此人工门禁延续现行完整输入审阅要求，不自动把未读包标为公开。报告/附件完整阅读、价格引句与七字段监控仍走现有 review/publish；worker 不批准报告、不直接生产写回。

状态：new → ineligible/superseded/legacy_or_terminal/awaiting_public_review → ready → watching → failed/awaiting_result_review，人工发布后收敛为 completed。关闭发送开关转 blocked_dispatch。每事件持久化 job，单 worker 锁排除并发；每10秒只推进现有待办和收取已发送的活跃请求，不扫描股票候选。真实消息关联、15分钟接收期限、未知发送只查历史、终态不复活由已有 transport 负责。进度消息不算报告；及时 partial 到期后留待人工阅读。请求准备、绑定或 job 更新间崩溃，复用台账的同 intent 请求；sending/send_unknown 永不 submit。

派生 job 丢失时先验证原 seal/request/有效双席完成时间，再按原 intent、唯一台账 claim、冻结包哈希、证券、日期与账户/会话恢复。只继承原 claim 中已明确记录的 public_input_reviewed=true，不把缺失审阅补成 true。已发送/unknown 继续原请求收取，较新轮不截断；prepared 恢复为 ready，真正发送前仍检查最新轮。原 intent 已绑定但台账或 claim 缺失时拒绝创建新请求；失败终态原样保留。批准后丢 marker 由 reconcile 修复；重建 ready 的 marker 保留到下一步，不等待另一次小时扫描。已人工发布的 intent 由下一次本地步骤/小时修复使 job 收敛 completed，不重新调用远端或自动验收。

并发边界：scheduler 整批持 queue.lock，worker 的最新轮检查以非阻塞共享锁抢占，失败仅暂缓该 marker，继续处理其他已发送任务。CLI preflight 在 queue.lock 外执行；随后 claim_guard 在锁内重验最新轮、重新读取event/CLI配置，并再次核验三层开关、原request与哈希验证双席完成时间的最新cutoff，以及CLI固定目标/台账目录/可执行文件等配置仍与本次预检一致。预检期间关闭开关、前移起点或改变CLI配置均在attempts=0时阻断。验证通过才原子持久化 sending/attempts=1；这个 durable claim 是发送资格的线性化点。释放队列锁后执行唯一远程发送，已落占位不撤销、不重建，后来的新轮不会令它重发或失去收取。网络 auth/history/send 均不持主研究队列锁。prepare/bind、同证券证据验证和 claim 落盘仍有本地临界区，scheduler 现有非阻塞抢锁语义不变；没有宣称所有本地文件操作零耗时。

主触发拟用 launchd QueueDirectories 监视 pending。`plan-launchd` 仅输出两个 plist，不安装或运行。没有采用原15分钟 heartbeat；旧入口应继续暂停。worker 之外需要每小时或更低频 reconcile：seal→outbox 不是同一事务，磁盘/进程故障可能丢通知；pending 文件可能在批准后尚未写入；机器重启或停机也可能漏一次唤醒。现有05:00每天一次不能及时修复这些窗口。reconcile 仅修复授权起点后的 seal 事件和既有待办唤醒；awaiting_result_review 的唤醒只核对本地人工发布/失败状态，不恢复远程收取。不重置旧请求或失败，不改变每日额度/七天冷却。它是故障修复而非主触发；启动恢复用 RunAtLoad，同样受 disabled 与起点门禁。

切换须另行获得未来公开数据发送授权：确认旧邮箱/heartbeat停用；核对当前两仓版本与 CLI 身份；明确起点且保持今日三只排除；安装经审阅的 worker/recovery plist；启用事件和 CLI 两层开关；由输入审阅者批准事件，再一次真实受控验证。先保持旧入口暂停，避免双发。不得修改已有失败 intent 重试；出现不确定发送先核验真实回执。备份已有 methods output/research_queue 和 CLI 台账覆盖新增事件/任务；配套 ai 改动已把新增事件配置纳入备份。

## 操作界面与待启用条件

隔离代码入口（以下为将来获授权后的操作说明，本次未运行worker/恢复命令）：

```sh
python3 scripts/coze_events.py plan-launchd
python3 scripts/coze_events.py worker
python3 scripts/coze_events.py reconcile
python3 scripts/coze_events.py approve --key <seal_sha256> --public-input-reviewed
```

plan-launchd 只打印两份plist，不安装；切换时使用真实运行目录与明确Python解释器生成计划，写入LaunchAgents并bootstrap必须另行执行。两份计划均固定Python绝对路径，并显式写入非敏感 `PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`。本机 `/usr/local/bin/coze` 使用 `#!/usr/bin/env node`，Node 位于 `/usr/local/bin/node`，因此不能沿用launchd仅含系统目录的默认PATH；同时覆盖标准Apple Silicon Homebrew目录。事件worker仅用Python标准库，不依赖主研究的shell导出引导，不读取或复制 `.zshrc`、token等交互环境。非标准Node安装目录须部署前明确调整并重做精简环境验证。事件config enabled控制本地事件接入，dispatch_enabled与coze_cli.enabled共同控制远程工作；not_before须填写明确授权起点。三层开关本次全部关闭，隔离配置起点已按用户要求填写为北京时间2026-11-03零点，无任何今日候选入队。

worker自动把合格事件转为awaiting_public_review；需已有受授权审阅者（包括Codex）读完整冻结包并执行approve。结果阶段awaiting_result_review需读完body及全部附件，再用原research_coze review/publish。没有增加自动模型审批器，也没有把审核标志伪造成已读取，因此本版本不声称无人值守的语义审核已实现。已发送请求不受后续新批次阻止，只继续只读收取；未发送的确定过期轮标superseded。reconcile逐seal隔离坏历史记录，错误清单持久化，不阻断后续正确事件。

## 用户确认的起点（尚未授权发送）

用户确认从北京时间2026-11-03T00:00:00+08:00起生效（等于UTC2026-11-02T16:00:00Z），不补11月2日三只候选。只在隔离配置填写此时间，enabled/dispatch_enabled/CLI仍关闭，不安装服务。日期范围确认不视为未来自动发送授权。

采用双重边界：原研究request.created_at与哈希验证的研究完成事件均不得早于起点。研究完成事件取有效双席completed_at的最大值，持久化为research_event_at、time_basis=latest_verified_provider_completion。既有seal并未记录独立的publication/sealed_at，不能宣称知道精确落盘时间，也不使用mtime、重启、reconcile执行时间冒充研究新事件。新批次完成后才能封存，故此完成凭证加原批次起点足以排除旧批跨日、重封存和恢复回捞。

保守排除：11月2日创建的批次，即使11月3日才完成/恢复/重新写入文件，也不自动触发；旧pending/ready/人工批准状态不能越过新epoch。11月3日创建且完成事件达界的研究仍须资格和公开包审核、显式发送授权。
