# Coze 条件第三模型：CLI 迁移与切换

2026-11-01：本分支已实现原生 CLI 传输，`config/coze_cli.json` 的 `enabled=false`，尚未部署到原运行目录。当前只读复核 `coze` heartbeat 为 PAUSED、每15分钟，既有 prompt 仍属邮件链路（此前记录曾为ACTIVE）；本次不修改它、不新增定时任务、不发送新 Coze 请求、不生产写回。原 05:00 研究检查及 ai 07:30/22:00 消费保持原样。切换时使用下述流程，不能把“代码完成”表述成“已启用”。

2026-10-14 起的既有条件授权继续适用：仅沪深 A 股，同批同冻结包两个基础席成功（当前 Codex+DSH；旧批 Codex+Claude），显式正数 P1.base 的 `max/min - 1 > 0.10` 才请求第三意见；恰好10%不触发。拒绝、失败、缺 base、仅区间不触发，不推中值；只处理每证券最新轮，较新在途轮抑制旧轮。不另占每日证券名额、不重置七天冷却。原两席 seal 不变，第三意见 pending/held/failed 不阻断基础消费。

## 传输与证据

官方 `@coze/cli` 已真实验证版本0.3.11，会话7669294798322467118、claw 7669290905110790410、授权用户2100524352023411。配置固定这些非凭据信息；不读取、复制或提交 token，不运行 login、安装 skill 或升级。`session status` 仅本地状态，不能证明会话归属；发送前以 auth status 和目标历史中的真实 claw/session 核验。自动升级已在本机关闭，迁移不改变 OAuth 权限。

实际提交形式：`coze session message --session-id SID --format json`，完整 query 经 stdin，仅提交一次，不使用 --wait。原生 accepted 回执给出 message_id。收取使用 `coze agent message list --project-id SID --size 10 --format json [--cursor ...]`；该 CLI 的 project-id 在此实际映射为 session_id。验证页内/跨页时间降序、游标明确存在且合法，再分页覆盖完整发送窗口（整页均早于发送时点前60秒才止步，不扫描全部陈年历史）。完整窗口成功才可判无回复；游标缺失/循环、顺序异常、分页上限或失败均保持待核验。超时依据本次历史查询开始时刻；查询跨过截止时点时不会冒充截止后的完整检查。结果匹配实际 user ID、session ID、claw ID、reply_to_message_id、请求 query SHA256 和服务端时间。仅候选摘要或 progress/stream=false 都不代表研究完成，必须人工读全及显式 review。

`coze-intent/v2` 绑定原 seal/hash、证券、估值日、冻结包/hash 和固定账户/会话。`prepare` 需逐项读取完整包并确认仅含公开资料，不允许持仓/资产/凭据；完整包原字节保留在 query 中。脚本保守拒绝任何 @ 字符（含中文或标点紧贴场景），避免触发 CLI 文件/agent 解析；含 @ 的包不改字节、保持待人工处理。每 intent 只准一个 request，提交前持锁把 sending/attempts=1 落盘；崩溃、超时或不合法回执均为 send_unknown，之后只能查历史，禁止重发。完整 query 哈希、用户及时间唯一匹配才恢复真实 message ID；零或多个匹配保持未知，到期无匹配则失败，不能新建请求规避。

15分钟从真实 request 服务端时间起，未知时保守用 sending_at。先成功查全历史并登记匹配回复，再判断无回复超时。恰好15分钟创建的回复可用，晚于15分钟的报告不能发布。期限内 partial 可保留等待完整读取，选中的报告本身仍须期限内；明确执行失败使用 fail 终止，不重试、不催办。失败历史或 retry_allowed=false 均不可复活。未来合格新批次不受旧失败阻塞。

原始 reply/files 库存完整保存；同名附件按索引保留不同原件。附件 URL 仅取实际 CLI 消息；下载器 HTTPS 精确域名白名单，检查每次跳转、25MiB上限，保留原字节与 SHA256。为了控制跳转和大小，使用标准库下载器读取 CLI 给出的 URL；这不是虚构 CLI 下载回执。URL、原始消息和附件留本地私有状态，不打印签名 URL。UTF-8 Markdown/txt/json/csv/tsv 自动全文读取；二进制、图像或嵌图需人工完整读取和验证全文提取，失败/空文件/缺 URL 保持 blocked。`extract-attachment` 绑定原件 hash 后登记全文，不能把摘要当全文。附件完整性指下载后哈希与封存/回放一致，不声称服务器独立 checksum 已验证。仍需读报告判断截断、矛盾和来源质量。

正式封存为 `research-sealed-coze/v2` 和 `coze-cli-receipt/v1`，独立存 request/message/完整冻结包/query/原始附件/全文/result，逐文件绑定 SHA256，不制造 Gmail headers。选定后不可变，后续历史消息和可变台账不改变旧交付；回放无需 OAuth/可变台账。旧 `research-sealed-coze/v1` 继续严格按真实邮件证据读取，旧 intent（包括未发送、失败）不转换/重发。旧 mail helper 只为历史与既有在途核验保留，新 CLI 入口不会发送邮件。

## 操作顺序（仓库根）

配置默认禁止发送。以下 prepare 仅生成本地输入；submit 需要部署后的 enabled=true 和显式 --allow-submit，两道门禁均满足才可能外发。首次发送前核对 pinned 账户、会话及 CLI 版本、原完整包是否公共，并检查旧 intent 清单和已有请求。

```sh
python3 scripts/research_coze.py scan --not-before 2026-10-14T00:00:00+08:00
python3 scripts/research_coze.py prepare --intent /absolute/intent.json --public-input-reviewed
python3 scripts/research_coze.py submit --intent /absolute/intent.json --allow-submit
python3 scripts/research_coze.py collect --intent /absolute/intent.json
python3 scripts/research_coze.py review --intent /absolute/intent.json --reply-id ACTUAL_REPLY_ID --extraction /absolute/extraction.json --verified-result
python3 scripts/research_coze.py publish --intent /absolute/intent.json --extraction /absolute/extraction.json
```

人工二进制/图像全文登记：

```sh
python3 scripts/research_coze.py extract-attachment --intent /absolute/intent.json --reply-id ACTUAL_REPLY_ID --key 0 --text-file /absolute/fulltext.txt --raw-sha256 ORIGINAL_SHA256 --verified-fulltext
python3 scripts/research_coze.py hold --intent /absolute/intent.json --reason '缺价或附件尚未读全'
python3 scripts/research_coze.py fail --intent /absolute/intent.json --reason '已确认执行失败'
```

`review`前读全 body 和所有附件，核对证券、CNY、估值日、P1.base、单一T1和原句证据，再检查 monitoring 是否漏提。extraction 仍为 `{"p1":{"base":报价},"t1":报价,"monitoring":[],"evidence":{"p1":"含P1与币种的精确原句","t1":"含T1与币种的精确原句"}}`。只提取实际报告，不从另一模型、V50或区间端点补价。非空 monitoring 必须真实七字段 variable/current/as_of/trigger/action/source/next_check，不能将报告已有监控静默丢成空数组或编造缺字段。缺证据保持held。原文不满足现行合同，不因 CLI 可用就自动验收。

新交付 `stock-research-coze/v2` 不要求本仓九节，也不冒充 v4/audit-v2认证；P2已退役、V50无则null、无research_controls。价格数字/引句门禁继续，T1语义问题按用户此次指示留待另项解决，本迁移不声称语义质量通过。冻结公开测试包本身包含 PB=82.2% 但≥80%预计算“未命中”的矛盾，新报告仍有T1、历史会话内容及监控字段问题；不要把传输测试等同投研结论通过。

## 待部署切换与回滚

1. 完成独立 Astra/xhigh review、修复和离线回归后本地 commit；不自动 push/部署。当前 worktree 中的模拟端到端只能证明协议适配和消费门禁，尚未用本适配器发新真实任务。
2. 经切换授权后，先确认原邮件 heartbeat 保持暂停，快照所有旧 intent/mail 请求及未知发送状态；不得重置它们或把同一原 seal 改投 CLI。安装两个仓库配对提交，确保 CLI版本/账户/目标会话、依赖和证据目录权限正常；旧邮件 skill 不再作为新请求入口。
3. 在真实运行配置显式启用 CLI，使用本页规则替换既有 heartbeat prompt，仍每15分钟、目标聊天不变。不要另建重复任务。一次只提交 eligible 的新CLI intent；每次先收取已有请求，再扫描；未知发送只核验，不重发。每次通知按 request_id+错误/终态保存 monitor.json 的 notified 去重，通知成功后记录；无变化保持安静。失败检查不充当超时证据。
4. heartbeat 只 prepare/submit/collect/人工验收/publish，不直接生产写回。既有 ai07:30/22:00 消费 supplement，保留 base-first、最新轮、人工改价保护、报价唯一属主和 CSV 事务。备份已加入可选 CLI 台账目录及配置（首次启用前不存在不算错误；一经收录后消失按原规则失败）。
5. 如需回滚，关闭CLI发送并暂停 heartbeat，保留全部台账和不可变证据，不删除发送占位；先核验未知状态，再恢复历史消费者或经授权的邮件入口。不能将已提交 CLI intent 自动转换为邮件重新请求。

CLI运行状态在 methods `output/research_queue/coze/` 与 ai `investment_rawdata/coze_cli/`；正式证据仍在公司目录 `evidence/coze/<request_id>/`，已有备份覆盖正式报告。旧邮件历史在 `investment_rawdata/coze_email/`；本次未触碰。
