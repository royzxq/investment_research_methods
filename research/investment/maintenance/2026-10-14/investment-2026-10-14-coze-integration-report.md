# Coze 条件第三模型接入与验证

日期：2026-10-14，Asia/Shanghai。generator=codex。此报告为软件接入维护记录，不是新的证券研究或交易许可。

## 结果

用户确认的规则已实现并部署到本机两仓：仅沪深A股，同批同冻结data pack的Claude/Codex均成功且明确P1.base时，按 `max(P1)/min(P1)-1 > 0.10` 请求Coze；恰好10%、港股/北交所、缺base及一端失败不触发。Coze必须明确P1与T1，缺失报错并独立held；原两模型先完成写回，Coze等待/错误/下游冲突不阻塞该配对。

Coze成功后以coze业务席位参与原共识，Codex仍映射gemini、Claude映射claude。权重、价格过滤/离群、P2派生、列属主与07:30/22:00写回及后续飞书备份时刻均保持原流程。晚到第三模型生成绑定原seal的不可变补充seal，原两模型seal和完成回执不改写；较新批次/人工目标改价/本地同键冲突仍受原门禁保护。

报告按原公司日期目录独立保存research-coze.md/price-map-coze.json。Coze不套固定九节，JSON使用stock-research-coze/v1保留明确价格及原句证据；不补造缺失V50/P2/监控，也不冒充完整本仓v3研究认证。冻结包、邮件全文、envelope、请求快照、显式人工对应及完整附件提取正文在本期evidence/coze下，已选发布事务重试不依赖可变邮箱台账。首次读邮件证据与helper共用邮箱锁，避免选择混合两次回复。

## 验证

- 实际部署文件运行AI定向回归102项通过，包含13项新增Coze跨仓集成测试；使用本地真实离线CLI子进程、冻结request→manifest→报告/JSON与原CSV事务，Gmail证据采用隔离envelope，不发送测试邮件、不修改生产CSV。
- 覆盖严格10%边界、无效数值、缺P1/T1、P2状态矩阵、附件未读完、晚到三模型/重复提交、坏补充不替代配对、监控/本地Coze同键冲突、人工目标改价、后续回复更新、冻结后中断恢复、校验失败后更正、人工关联及邮箱并发锁恢复。
- methods全量离线768项：766项通过，2项因沙箱禁止ps而报PermissionError；两项在允许的环境下定向重跑通过。后续Coze修改另经上述102项及4项阈值/提取单测通过；不声称对最终状态重跑全部768项。
- 股票框架结构治理检查通过；git diff --check通过。结构检查不证明投资方法有效性。独立high正确性对抗审查及六维静态复审最终PASS，发现的失败回退/可变邮件/状态语义/中断恢复/人工关联/并发问题均修复并补测。
- 本机文件哈希与staged验证版本一致，原文件副本及部署清单保留在output/coze-integration/；生产报价与算法未由本次维护直接改写。用户既有跨日调度授权保持，Git未提交/推送。

## 实际自动化与邮件

`Coze 条件股票调研与回复` heartbeat已创建，automation_id=coze，ACTIVE，每15分钟。旧请求monitor里的coze id存在但实际任务已不存在，经工具确认后重新创建；新任务也接续原未完成请求的只读回复检查，不重复创建其他监听。该任务持续扫描未来条件，因此当前请求结束后不按一次性监听规则自删。

首次自动审批曾拒绝持续外发，认为完整包可能包含内部敏感研究；逐字读取两份实际包，确认仅公开行情/财务/机构公开持股及通用框架缺口提示后补充证据重试，创建与两封Gmail发送成功。未来发送前仍核验完整包，若含个人持仓/成交/余额/凭据或非公开信息则held，不发送或删减。发送使用用户明确调用的coze-stock-research-email技能，仅发往investauto@coze.email，发送账户get_profile实际核验为royzxq@gmail.com。

本次真实符合条件并发送：

| 证券 | Codex P1 | Claude P1 | 差异相对低价 | 请求ID | Gmail ID |
|---|---:|---:|---:|---|---|
| 中国海油600938.SH | 19.67 | 25.79 | 31.11% | coze-email-21127fc2fb3e4e0db8a5251b6ce62eab | 1a13adf9faa1aceb |
| 中国神华601088.SH | 20.32 | 25.42 | 25.10% | coze-email-03e9339001794bac9e2a404968861365 | 1a13ae0a76c1090c |

估值日2026-10-14，数据最新交易日2026-10-13。邮件主题严格股票调研，text/plain完整query；发送领取/回执及实际RFC Message-ID已登记，正文全文与原send.json一致。首次完整线程读取只有自己的发出邮件；from:investauto搜索完整页没有这两次新回复。请求为pending，未生成Coze成功报告/价格JSON或生产第三模型共识，不把邮件发送等同完整研究交付。原两模型完成回执保持有效。

真实发送回执、完整MIME、首次查询与monitor.json在对应邮件请求目录；本次证据摘要在output/coze-integration/evidence/。当前未验证真实Coze报告内容与附件完成门禁，待匹配回复到达后由heartbeat实际处理。

## 调度加载

备份完成、核验当日无在途任务后，于2026-10-14T22:50:20.226802+08:00重载既有投资调度器，返回码0且服务/PID/进程核验通过。原plist、任务定义和时刻不变；未强停在途备份。回执在output/coze-integration/evidence/scheduler-reload.json。

## 契约与代码

- docs/context/coze-research-automation.md：当前行为、技能、状态与失败恢复。
- scripts/research_coze.py：候选、防重绑定、提取/邮件证据、独立原文/JSON及补充seal校验。
- scripts/research_paths.py、research/README.md：coze独立路径/导航。
- ai_investment/src/analysis/research_consumer.py、scripts/research_writeback.py：第三席、原配对先完成与原事务消费。
- ai_investment/docs/adr/ADR-20261014-coze-conditional-opinion.md、CHANGELOG.md：领域裁决与变更记录。

## 2026-10-15 超时裁决与提交前复核

按用户追加授权改为发送后15分钟无可确认归属回复即终止failed，不重试、不继续等待、不发布迟到结果。五个当前请求均已关闭，未匹配原报告证据保留，未生成Coze有效价格交付；持续自动化仅接续未来合格新批次。deadline优先使用已发邮件真实Gmail internal_date。

提交前补强失败历史终态保护：共享helper后续将状态改成complete也不能重新绑定或发布；expire在崩溃恢复时按失败历史收敛，迟到complete不能无限held。已发布完成结果保护、其他自动化范围隔离不变。新增回归覆盖同批连续scan/拒绝bind与publish/两模型实际writeback及幂等、真实helper.record改状态、迟到报告、邮箱台账先失败后崩溃恢复、独立监听不被关闭。独立high正确性及六维复审PASS。methods全量离线回归772项通过；最终期限校验收拢后，8项Coze单测与AI侧107项定向回归再次全部通过。股票框架结构检查与两仓git diff --check通过。本段不把隔离回归当成真实Coze成功研究验证。
