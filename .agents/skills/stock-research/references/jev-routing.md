# Jev 条件路由

适用于批量公开公告的优先级排序、年报候选章节定位。普通程序先做目录、页码、字面定位；已确定的原文直接核验。Jev 不做现金收付、主体关系、Gate 或估值裁决，不替代关键事实独立原文复查。

## runner 入口与模式

`scripts/research_runner.py run --request <请求> --generator codex|claude` 默认注册 `jev_research`，暴露 `research_jev_route`。底层使用已安装的 Jev MCP，认证由它从环境或标准密钥文件加载；不把密钥写进配置、参数或日志。Codex 原始 `jev` server 在这个子进程内关闭，调用统一走可审计路由；CC strict MCP 配置包含该路由。

用 `--jev-mode auto|off|force` 或 `RESEARCH_JEV_MODE` 选择；命令行优先，重试默认保留首次模式。`off` 不注册工具；`force` 用于明确要求及接通验证，也受大小限制。

| auto 条件 | 结果 |
|---|---|
| 公告至少8候选，或年报至少6候选，且合计至少12000字符 | 调 Jev 排序定位 |
| 研究者/程序已确定全部必要范围：`selection_complete=true` | 记录 declared_precise_location，普通程序读取 |
| 候选少或正文小 | 记录具体阈值原因，普通程序读取 |
| 单次超过50候选、500000字符，或某段超过200000字符 | 明确回退/拆完整批次，禁止硬截断 |
| 认证、工具或网络失败 | 保留全部候选，回退普通程序；认证不重试，临时错误至多额外一次 |

这些是待校准的传输/开销参数，不是投资规则，也未证明达到阈值就一定省 token。

## 每个候选批次的执行

1. 使用启动输入给出的本次 `jev/materials/`，保存公开原文提取文本 `.txt/.md`。不要送账户、私有持仓、凭据、配置或不相关文件。
2. 普通程序生成位于本执行目录的 manifest，实际计算 SHA 和字符范围，不让主模型转抄原文。格式：

```json
{"schema_version":"research-jev-candidates/v1","purpose":"announcements","query":"许可、资金义务及治理事件","selection_complete":false,"candidates":[{"id":"A001","path":"<本次jev/materials/公告.txt>","sha256":"<实际SHA256>","start":0,"end":1234,"public_url":"<公开资料URL>","title":"公告标题"}]}
```

年报使用 `purpose=annual_sections`，每候选为已定位的完整章节/页范围。字符从0开始，`[start,end)`；源变化要重新定位。公开 URL 是来源声明，不等于真实性或证据已核验。

3. 调 `research_jev_route(manifest_path=<路径>)`，包括小批次和精确定位批次，以便留下真正的未调用原因。程序读取候选并直接转交 Jev；当前宿主主模型仅收到 ID、位置、分数和不确定/失败项。
4. 返回 `next_offset` 时继续翻页，续页复用同一结果，不重发 API。排序结果不排除任何候选；低相关度不是事项不存在，表头、定义、续页和反证义务也不因分数改变。原文核验仍按既有证据契约。
5. MCP 不可用时等价执行 `python3 scripts/research_jev.py route --config <本次jev/config.json> --manifest <路径>`，不得直接绕过日志调用原始 Jev。

## 调用记录

每次研究检查本次 `jev/calls.jsonl` 和结束后的 `jev/summary.json`（摘要也在 `process.json.jev`）：模式、阈值决定、候选数量/字符数、源哈希、缓存复用、请求/结果、失败及回退、模型、已报告 token 与耗时。记录区分收到路由请求、启动后端、提交 `jev_triage` 和返回结果；后端启动失败的提交次数为0。每页返回字节和耗时单列，不能冒充宿主精确 token。二元相关度概率保存为 `jev/result-*.json`，主模型不接收第二份正文。

`not_requested/no_candidate_batch_submitted` 表示本次没有提交批次，不能改称“程序判断无需 Jev”。`skipped` 有具体原因；`fallback` 可以是输入校验或后端启动失败。`invoked` 表示提交过后端工具请求，仍须检查响应是否确认实际 API 成功、是否全部失败。Jev usage只涵盖它已报告的成功项，失败/在途费用未知；SDK内部重试次数不可得，费用字段保留 null，不虚报0。主模型用量另由宿主统计，不与 Jev相加冒充主模型省量。

执行中可用 `python3 scripts/research_jev.py summary --config <本次jev/config.json>` 只读查看最新记录；最终摘要由 runner 在进程收尾后保存，提前查看不会冻结旧摘要。
