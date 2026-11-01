# Coze CLI 条件第三模型传输

2026-11-01，用户授权迁移实现；独立 Astra/xhigh 审查通过后允许本地 commit，未授权 push、合并或部署。

新请求使用已验证的 InvestAuto CLI 会话，完整冻结 data pack 不变。CLI 原生 request message ID、reply_to_message_id、session ID、发送方 claw ID、用户 ID、服务端时间及完整附件构成证据，不构造 Gmail headers。旧 email supplement/v1 只保留历史验证；新交付采用 supplement/v2 和 CLI receipt/v1。

保留沪深 A 股、本轮同包两基础席成功、P1 严格差异 >10%、最新轮次、额度和冷却。旧 intent（含失败）不转换为新请求、不重发；历史邮件继续按原证据读取。CLI 请求由唯一 intent 绑定，文件锁领取，提交前持久化 sending。任何提交响应不确定均先完整查历史，用账户、会话、时间及实际 query 哈希唯一恢复；无唯一证据不得重新发送。

15 分钟从真实已发请求的服务端时间计，未恢复时保守使用 sending_at。先成功完成分页并登记匹配回复，再判无回复超时。只接受期限内的、同 request/session/claw 的结果；明确失败终态不复活。队列提示和进度不是研究结果，附件缺失/截断或未读保持 partial/held。完整原件、全文、原始回复、冻结包、身份及回执选定后不可变，后续消息不改旧交付。

prepare/collect 不发布生产；submit 还须配置 enabled=true 与显式 --allow-submit。默认配置 disabled。review 只核既有身份/日期/价格引句/完整附件契约；T1 语义问题按用户本次指示不扩展为迁移阻塞，也不声称语义通过。报告监控字段仍须原合同，不造值。publish 仍绑定原 seal、生成独立补充；ai 消费者仍先原两席后第三席，07:30/22:00、原本地来源/CSV 事务与保护不变。

不修改既有邮件 heartbeat 或安装目录；提交前只读复核状态为 PAUSED（此前记录曾为ACTIVE），不能因迁移自动恢复。本地配置及切换操作文档为待部署产物；真正切换须独立授权，先冻结在途旧 intent 清单，不将其准备成 CLI 请求。CLI ledger 纳入本地运行备份。OAuth 已有连接可用时使用，不登录、不扩权限，不复制凭据。
