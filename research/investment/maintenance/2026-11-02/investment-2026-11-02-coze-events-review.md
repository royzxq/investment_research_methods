# Coze封存事件改造审查记录

2026-11-02。当前阶段：隔离实现及独立评审完成，本记录随用户已授权的本地提交保存。实现代理未 stage/commit，提交由父任务完成；未 push、合并、改生产配置/排程、真实调用Coze或补发历史。

## 本轮 Astra/xhigh 直接实现

执行代理 `/root/astra_implementation`，模型/effort 为父任务指定的 `gpt-6-astra/xhigh`。已直接检查并修改实际代码；以下不是对上一版代码重新标记“review通过”。

- 修复目标扫描依赖文件名的问题：合法恢复/重命名封存可能被遗漏，漏掉的新轮也可能让旧轮发送。现按 seal 头部 task_id 筛选，完整验收只针对同证券；两个新回归先复现失败、修改后通过。
- 修复丢失派生 job 后已发送请求被新研究标成 superseded 的恢复缺口。只从同 seal、包哈希、证券、日期与固定目标的唯一原 claim 继承已存在的完整输入审核；已发送/unknown 继续原请求收取，prepared 恢复仍重查最新轮。失败不复活，原绑定台账缺失或审核/目标/包被改则阻断；prepare 后未 bind 的孤儿 claim 可恢复原绑定，不能新增请求。
- 人工 publish 后派生 job 本地收敛 completed；待结果审核的小时唤醒只核对本地状态，不重新取网或自动验收。重建 ready 时保留 marker，避免再等一小时。
- 把远程 preflight 与唯一发送移出主研究 queue.lock。新增 claim_guard，在预检后持非阻塞队列共享锁重查最新轮，并仅在锁内落盘 sending/attempts=1；该占位是发送线性化点。新轮在预检期间到达会拒绝首次发送，占位之后到达则继续原请求回收。抢不到主队列锁的未发送 marker 留待重试，不阻断其他活跃请求收取。
- 增强备份逐字节校验，覆盖 event/job/pending/intent 与原 CLI claim/附件；更新两仓 ADR、操作指南和 CHANGELOG，删除现行操作段中恢复15分钟 heartbeat 的矛盾指令。

本轮最终定向验证：methods `python3 -m unittest discover -s tests -p '*coze*.py'` **75通过**，日志 `/tmp/coze-astra-implementation-methods-tests.log`；AI 使用仓库 myenv Python、设置 RESEARCH_METHODS_TEST_ROOT 指向隔离 methods，运行事件集成/CLI集成/Coze消费/备份四模块 **74通过**，日志 `/tmp/coze-astra-implementation-ai-tests.log`。两仓 `git diff --check` 通过。AI测试运行本地假CLI子进程，账户、文件与写回全部使用临时夹具。先前新增恢复场景5项与文件名边界2项均先观测失败，claim_guard两项先观测缺少API失败后修复通过。

父任务已对首次冻结版本执行methods全量回归并报告1285项通过（1240项首次通过；45项loopback/ps受沙箱阻断后单独获准离线重跑通过），独立Astra/xhigh评审发现下列两项P2，已由本实现代理修复并通过独立复核。全量结果属于P2修复前的基线，不冒充本次小修复后的全量运行。剩余外部验证：真实Coze身份/协议、launchd安装与唤醒、真实公开包和报告语义审核均未执行；没有无人值守语义审批器。主研究短暂的本地证据验证/prepare/claim临界区仍存在，网络不占queue.lock；scheduler原有非阻塞锁冲突语义未修改。T1语义继续按用户要求另项处理，PB矛盾与报告质量仍未标为通过。

## 独立评审P2修复

继续由 `/root/astra_implementation` 按原Astra/xhigh配置实现，未切换模型、未提交或部署。

1. **launchd缺少Node路径**：只读核对本机Coze脚本使用 `#!/usr/bin/env node`，Node安装于 `/usr/local/bin/node`。两份计划显式设置固定、非敏感的PATH（包含 `/usr/local/bin`、`/opt/homebrew/bin` 及系统目录），Python必须为绝对路径；不复制交互环境或shell凭据导出。两个新增回归先因缺少EnvironmentVariables失败，修后通过：plist序列化验证仅有固定PATH、拒绝相对Python，以及仅用计划环境启动Python→临时假Coze JavaScript→Node的完整子进程链。本机该测试实际执行、未skip；未运行真实Coze。
2. **预检期间配置变更未重新验权**：事件submission_guard在queue.lock内、sending占位之前重新读取event/CLI配置，复核三层开关、用原request和哈希验证完成时间计算的新cutoff，以及CLI固定目标/台账目录/可执行文件等配置仍与预检一致。已有sending/unknown路径不进入此提交guard，也不删除或重建占位。新增七项离线场景分别在preflight期间关闭event、dispatch、CLI开关，前移cutoff，修改会话、state_dir和executable；修改前七项全部失败，修后全部证明attempts=0且无session message。

P2修复后定向结果：methods全部Coze相关 **77通过**（`/tmp/coze-astra-review-fix-methods-tests.log`）；AI事件和CLI集成 **28通过**（`/tmp/coze-astra-review-fix-ai-tests.log`）。launchd环境单模块先有 **25通过**（`/tmp/coze-astra-launchd-runtime-tests.log`）。这些计数重叠，不能相加。两仓 `git diff --check` 通过；按父任务要求未重复全量长回归。修改范围为methods事件脚本/测试/ADR/本记录，以及AI事件集成测试；开关、起点和生产状态不变。

## 本轮独立最终结论

独立审查代理 `/root/astra_final_review` 由明确的 `model=gpt-6-astra`、`reasoning_effort=xhigh` 配置启动，与实施代理不同。只读审查两仓相对 HEAD 的17个变更文件（含6个未跟踪文件）及原adapter、transport、consumer、恢复和备份调用链；没有参与实现或暂存。最终判决 **PASS-WITH-ISSUES：无剩余代码阻塞，可进入已授权的本地提交**。两项P2均逐行复核修复与运行日志，Hard Boundaries、Hard Stops、Dead Code、范围纪律、ADR/文档、测试约定六维均PASS（测试为离线）。

全量证据为 `/tmp/coze-events-astra-final-methods.log`（1285项，首次1240通过、45个环境错误）和 `/tmp/coze-events-astra-sandbox-recheck.log`（45通过，56.123秒）；脚本已核对首次错误集合与复跑用例集合完全相同。最终P2增量使用上述77/28定向回归验证，未重复全套。此前AI四模块74通过；计数均可能重叠，不相加。

残余运行条件明确保留：未安装或真实验证launchd启动/重启唤醒；未用本事件worker执行真实Coze联调。scheduler整批持队列锁时首次发送须等其释放，已有请求继续收取；短暂本地资格/claim临界区保留现行锁冲突语义。完整公开包及结果需授权审阅者验收，无无人值守语义审批器。三层开关关闭，11月3日生效边界不构成外发授权，11月2日旧批次不补发。T1语义、PB矛盾、历史内容混入和监控质量未宣称通过。

## 上一轮独立评审与历史验证

独立review：gpt-6-astra/xhigh，agent /root/astra_review，最终PASS-WITH-ISSUES，无剩余架构/实现阻塞。六维均通过：边界、Hard Stops、Dead Code、范围、ADR、测试。

审查修复：已发送请求不再受新轮门禁阻止收取；跨截止查询按history_started_at保留watching；恢复席和publication restore接入事件；目标资格仅检查同证券封存；reconcile逐seal隔离历史损坏；未发送过期轮标superseded；job/intent绑定seal事件hash。配套备份加入新config和worker锁，避免活动worker时发布恢复归档。

验证：methods全套1272通过(/tmp/coze-events-full-tests.log)，全套后修改另有最新Coze65、scheduler37、恢复36、publication restore5通过。AI跨仓62通过(/tmp/coze-event-ai-final.log)，最后备份锁边界模块28通过；以上计数重叠不可相加。集成真实运行本机假CLI子进程，走封存事件、公开包审阅、唯一提交、丢marker重启恢复、原report封存/消费，生产账户和数据完全隔离。

原methods与ai工作区用户变动未动。实际CLI false、heartbeat PAUSED、新event配置未安装、无event plist；新代码在两个独立worktree。launchd仅生成计划，未安装验证；公开包和结果审核仍由受授权审阅者执行（包括Codex），无无人值守语义审批器。未来发送须用户明确授权，当前三候选不自动补发。停用时若pending非空，配置关闭虽不外发，QueueDirectories仍会节流唤醒；彻底停用须bootout两个job并保留台账。

## 生效范围补充

用户仅确认北京时间2026-11-03零点起，不等同未来自动发送授权。隔离event配置已填该起点，enabled/dispatch_enabled仍false，生产无event配置/服务安装。cutoff双重验证原request与已核验研究完成事件（双席completed_at最大值）；不以mtime或恢复扫描时间制造新事件，不声称现有seal有独立publication时刻。新增四项边界后Coze69通过，跨仓事件集成1通过。只读检验Nov2真实三个候选seal（SH-600036/SH-600048/SH-688111）均明确research batch predates activation，无事件/请求产生。

本次日期边界增量经同一独立Astra/xhigh只读复核：PASS，无新增阻塞；起点包含零点，时间依据未冒充独立封存时钟，日期确认未扩大发送授权。
