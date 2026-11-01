# Coze CLI 迁移验证与独立审查

日期：2026-11-01（Asia/Shanghai）。范围：methods 与 ai 两个隔离 worktree 中的原生 CLI 传输、证据封存、消费、备份和切换文档。本次不发送新研究消息、不修改原运行目录/邮件排程、不生产写回、不 push/部署。用户追加授权：Astra extra high review 无阻塞后本地 commit。

## 独立审查

明确使用 `gpt-6-astra` / `xhigh`，独立 agent `/root/astra_review`，只读审查两仓全部相对 HEAD diff、未跟踪文件、AGENTS 与 ai 六维 playbook；未让 reviewer 修改文件或执行外部请求。独立最终判决 **PASS-WITH-ISSUES：修复复核后无剩余实现阻塞**；当时 methods 全套尚待主线程确认，随后已通过。保留的 issues 为未部署、未使用本适配器发送真实新任务、未观察真实终页格式及投研内容质量，均未声称完成。

发现、修复与回归：

| 发现 | 修复与证据 |
|---|---|
| sending 只有文件 fsync，掉电后占位可能丢失 | 原子替换/硬链接后同步父目录，新目录链同步；发送占位同步失败不调用 session message，后续不得重发 |
| 标点/中文紧贴 @ 可被官方 CLI 自动当文件上传 | prepare 与 submit 均拒绝全部 @；冻结包不改字节，保持待处理；中文/括号/标点/反引号/email边界回归 |
| 原件校验失败后第二次轮询可重建哈希基线 | 失败保留原始 digest，连续两次 binary、bin+txt 修改均不能完成；人工全文登记继续核原件与提取文本哈希 |
| 引用式 Markdown 图片或 HTML 媒体误标已读 | 图片/HTML媒体/data媒体转 blocked，需显式人工完整读取；Content-Length 不符拒收 |
| 缺游标被当末页，且分页跨截止可误失败 | 检查游标类型/存在、重复冲突、页内跨页降序、完整发送窗口；超时按查询开始时刻，跨截止后下次查询可恢复及时回复 |

六维：Hard Boundaries PASS（base-first/报价属主/CSV事务不变）；Hard Stops PASS（无凭据/旧模块复活/无关格式化）；Dead Code PASS（邮件v1有历史及在途读取依据）；Scope PASS；ADR/docs PASS；Testing 在 reviewer 结束时为 PASS-WITH-ISSUES（全套待确认），下述主线程已完成确认与最后定向复验。

## 验证记录

- methods 完整离线 `python3 -m unittest discover -s tests -q`：**1,255项通过，301.908秒**。最后新增3项分页/跨截止回归在随后 Coze 定向 **48项通过** 中覆盖；数字有重叠，不相加。全套日志 `/tmp/coze-methods-unittest-final.log`。
- ai 相关历史Coze/CLI集成、写回、恢复、运行备份：**118项通过，58.22秒**，日志 `/tmp/coze-ai-tests-final.log`。最后分页修复另复验原生 CLI 集成：**9项通过，24.86秒**，日志 `/tmp/coze-ai-cli-post-review.log`。真实走通的是隔离假CLI子进程→prepare/submit/collect/review→原生v2 seal→现有本地报价/CSV事务，所有账户/生产writer均被测试隔离，没有真实Coze调用。
- 最初 methods 沙箱完整运行的45项错误均为 localhost监听/ps受限；允许这些离线测试能力后仅一个既有2秒超时夹具未产出trace，所属重试模块17项单独通过，随后完整1,255项通过。未改无关生产逻辑规避测试。
- 旧公开长江电力真实测试本地重放：请求 `12ad8a48-89eb-4374-a9fb-6354420dc35a`，选中回复 `7703172241575674121.1`，2条匹配回复、1个附件，新增远程调用0。真实原件 SHA256 `96125fc3406520b5fe507326480e058b85cbe8542cc128c17b14504bacdaa4bb` 保持；实际协议 files=null 的进度消息已适配。重放仅验证传输，未发布该报告。
- 最后只读核验既有会话分页：前两页各10条，均明确 next_cursor 为非空str，页内及跨页降序、无重复ID，第二页所有消息早于此前请求窗口。仅输出字段、排序和窗口布尔元数据，未保存/输出私人正文或签名URL，未发送消息或创建资源。未看到真正终页，缺失游标一律失败关闭，不猜已查完。
- 两仓 `git diff --check` 通过；未修改技能文件（无新增/安装skill），已检查相关 .agents 入口及本地 memory，未触碰全局邮件技能、OAuth权限或原始未提交用户数据。

## 保留合同与限制

新交付仍 `stock-research-coze/v2`：P1.base和单一T1，无P2/T2、无research_controls、不冒充完整v4/audit验收、不得解除主研究限制。历史v1按旧内容/hash回放。触发保持SH/SZ、同冻结包两席成功、P1严格>10%、最新轮、额度及七天冷却；15分钟和失败终态不变。未知发送只唯一关联核验，不进行真实重复提交来测幂等。完整原件及全文封存独立于可变ledger和OAuth；原件哈希证明下载后完整性，不证明远端独立checksum或研究事实正确。

用户明确此次不因既有T1语义阻塞。公开测试包PB=82.2%却标≥80%未命中，真实新报告仍有T1定义、历史内容混入和七字段监控缺口，未因此被认定研究质量通过，亦未写生产。

## 切换条件

提交前只读复核既有 heartbeat 为 PAUSED（此前记录曾为ACTIVE），每15分钟；本迁移未修改自动化。原 methods 工作区仍clean；原 ai 工作区仅保留用户已有 CSV 与一份历史档案未提交改动。

本地配置 `enabled=false`；这次commit不等于已启用。配对部署两仓提交之前需按 `docs/context/coze-research-automation.md` 停旧 heartbeat、快照旧 intent/未知发送请求、核验固定CLI账户/会话和版本，再经切换授权启用唯一入口。旧 intent 包括未发送/失败均不得转换重发。仅沿用既有 ai07:30/22:00 消费，不新建排程、不由heartbeat写生产。备份默认CLI目录与配置已纳入，修改自定义 state_dir 时须同步验证备份覆盖；分页最多100页，超限不误过期/重发；所有 @ 包、二进制/嵌图及缺字段报告保持人工处理。
