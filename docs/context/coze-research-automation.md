# Coze 条件第三模型

**2026-10-18两价已本地采纳**：报价适配器已部署到本机实际运行目录；以下邮件触发、15分钟期限及原授权保持不变。本次未外发邮件、修改外部模型提示词或更新自动化，外部真实调用未验证。历史部署记录按当时版本解释。

本裁决来自用户明确授权：仅沪深A股，同批同包Claude/Codex最终P1.base的 `max/min - 1 > 0.10` 才请求Coze；恰好10%不触发。一端失败、拒绝或仅区间无base不触发，不补中值。不消费前一批模型价，不另计每日证券额度，不重置七天冷却。自动处理2026-10-14及以后创建的每证券最新原始封口；较新批次在途时不为旧批次发邮件。

当前Gmail发送账户由profile核验为 `royzxq@gmail.com`。邮件传输和对应使用 `/Users/xinquanzhou/.codex/skills/coze-stock-research-email/SKILL.md` 与其helper；完整冻结data pack作为query，固定主题，claim后仅发送一次，未知发送先恢复回执，禁止自动重发。持续heartbeat每15分钟扫描合格封口并收取已绑定请求；空闲保持安静。它是持续条件调研入口，因此不因当前请求全部完成而删除；只在用户停止时停用。授权仅发送命中条件的Coze query，不延伸为其他对外消息、Git发布或交易。

原两模型seal与完成回执不可变。Coze pending/held不改变原生产流程。成功后生成 `research-sealed-coze/v1` 补充seal绑定原seal及独立原文/JSON，原写回入口先完成原配对，再尝试第三模型事务；失败单独挂起。有效第三模型加入coze业务席位，Codex仍对应gemini、Claude对应claude；沿用等权/配置权重、过滤、离群及原CSV列属主。晚到且已有更新批次或人工目标改价时保持原保护，不历史补写。仅按原07:30/22:00排期消费，不在heartbeat直接写生产CSV。

Coze报告不要求本仓九节。归档仍用`investment-<代码>-<估值日>-research-coze.md`及`-price-map-coze.json`，同日冲突隔离-rN。新交付为`stock-research-coze/v2`：四顶层meta/price_map/monitoring/extraction；price_map删p2，t1仅price_condition；无research_controls，不冒充本仓完整v4/audit-v2认证。最低要求明确P1.base、单一T1、代码/CNY/日期及可定位原句。缺价或歧义held，不从V50/区间端点/另一模型补价；V50缺失为null。monitoring未提供用空数组，非空仍原7字段，不伪造本仓控制状态。Coze补充两价不构成拒绝票，也不能解除主研究限制；明确新风险进入复核。历史v1保留原p2及t1.events读取，冻结selected-reply按其原交付schema恢复，哈希不改。

原文、冻结包、envelope、此次邮件台账快照与所有附件全文冻结在本期 `evidence/coze/<request_id>/`，supplement绑定哈希。后续回复修改邮件helper台账不改变旧交付。完整附件读取与对应核验仍必需；Gmail账号不符、附件不可读与价格缺失通知一次，无状态变化保持安静。

用户2026-10-15追加裁决：发送后15分钟内没有可确认归属的回复即终止为failed，不重试、不催办、不继续等待该请求，不接受迟到报告发布；不影响原两模型回写或未来其他合格新批次。优先使用完整已发邮件的Gmail internal_date记录sent_at，缺真实回执时以sending_at保守计时并保留发送不确定证据。每次先成功翻完收件搜索/读取相关线程，登记15分钟内匹配回复，随后运行expire；依据received_at而非检查时刻判断，恰好15分钟到达仍属期限内。独立unmatched邮件保留证据，不猜配对、不延长等待。期限内已匹配的partial回复仍须完整读取与价格验收，缺价维持held；明确执行失败为终态。failed请求和intent及monitor保持终态，后续回复仅归档，不重新激活、bind、hold或publish。同一intent不会重新prepare；持续heartbeat继续扫描未来新批次。邮箱检查失败不得冒充无回复；下一次成功检查仍按原15分钟接收时间门禁处理。

入口示例（仓库根）：

```sh
python3 scripts/research_coze.py scan --not-before 2026-10-14T00:00:00+08:00
python3 scripts/research_coze.py expire
python3 scripts/research_coze.py bind --intent /absolute/intent.json --request-id coze-email-...
python3 scripts/research_coze.py hold --intent /absolute/intent.json --reason 'Coze缺少明确P1或T1'
python3 scripts/research_coze.py publish --intent /absolute/intent.json --extraction /absolute/extraction.json
```

v2 extraction仅忠实提取：`{"p1":{"base":报价},"t1":报价,"monitoring":[],"evidence":{"p1":"含P1与币种的精确原句","t1":"含T1与币种的精确原句"}}`。不带p2；原文明确P1区间且明确base才带low/high。原文quote不完整、T1歧义或缺必需报价应hold，不猜金额。旧冻结v1仍按旧extraction恢复，不用新协议改写证据。程序结构/引句校验不证明估值有效，仍须读完整报告核提取语义。

运行状态在 `output/research_queue/coze/`，邮件helper状态在 `ai_investment/investment_rawdata/coze_email/`；完整正式证据位于已纳入现有运行备份的公司目录。部署和验证记录见当期maintenance报告；本文件不声称已收取真实Coze报告。

终态恢复同时检查mail ledger的failed状态、history中的失败转移与retry_allowed=false；共享邮件helper将status误覆写为complete/partial也不能复活请求。未正式发布的late complete同样按接收期限失败，已发布completed intent不降级。超时处理仅涵盖条件intent绑定请求或monitor.automation_id=coze的既有请求，避免关闭其他自动化。发布与重放的冻结邮件均检查15分钟接收窗口。
