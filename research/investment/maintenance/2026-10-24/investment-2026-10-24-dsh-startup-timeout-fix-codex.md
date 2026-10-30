# DSH 启动超时修复与回归审查

完成时间：2026-10-24T09:22:33.218562+08:00（Asia/Shanghai）。本报告只结项启动投递修复；首个正式批次的晚间消费观察仍继续。

## 结论与本轮保全

按用户要求等待固定调度轮自然走完原策略，未主动取消。run `research-bf7380182d2b4c14bb9c782441519a29` / batch `8094449450ca4f9686712d08850579ca` 于2026-10-24 09:08:16 finished：四股 DSH 各首次及一次自动重试，共8次均超时；Codex四端completed。原12个进程组已用只读元数据检查确认退出，之后才开展离线复现/代码修复。`finished.failures=[]`或子进程清理后的exit0均不改变DSH失败结论。

已确认并修复共享 stdin 投递的可复现缺陷。没有重跑、补跑本轮，没有手工写共识、改队列/额度/调度或重启服务。对原批次、报告、seal、历史隔离实验、canonical/compact、AI CSV及本地模型库共2395个保护文件在全部测试后复核：0变更、0缺失。原8次失败及费用缺口均保留。

## 缺陷、复现与修复

旧启动器首次调用 `communicate(input=payload, timeout=0.25)`，超时后改为 `input=None`。实际Python3.11在后续调用中不再为stdin注册写事件；若冷启动的CLI尚未读完大输入，剩余字节与EOF就无法送达。DSH headless在读到完整stdin/EOF之后才创建session，因此该缺陷能解释本轮18,551–28,777字节输入对应的空events/stderr、无session和最终超时。隔离trial具有同一投递模式。

离线回归使用延迟0.6秒读取、超过2MiB的多字节/CRLF输入：旧生产入口的CC/Codex两端均在4秒后超时；修复后原场景通过，完整实际runtime输入字节一致。trial也完成红→绿，CC/DSH fake CLI均收到2,100,007字节并核长度/SHA/EOF。没有调用真实模型或重做公司研究。

生产入口改用最终`jev-runtime-prompt.txt`的只读文件作为stdin，包含原retry上下文、legacy附录和Jev指令；在同一已打开文件描述符上核正规文件及完整字节，定位到开头后交给子进程。独立隔离trial只创建0600输入快照，并核inode/字节、拒绝已有文件及符号链接。两端均改为`wait()`轮询，保留0.25秒取消响应、原总超时、进程组清理、失败归档、自然终态、共享验收和发布门禁。

修复只涉及4个源码/测试文件：`scripts/research_runner.py`、`scripts/research_harness_trial.py`及对应两个测试文件。没有更改投研方法、R14/all-of规则、历史合同、正式报告或共识算法。正常launchd每次按既有排期启动新的Python进程，后续正常调用会读取新代码，无需手工重启或触发研究。

## 验证与独立审查

| 验证 | 实际结果 |
|---|---|
| 全量离线回归，默认Python | 1135项通过，199.170秒 |
| 生产启动器，实际Python3.11环境 | 95项通过，57.534秒 |
| trial与benchmark定向回归 | 66项通过；原执行回执摘取注明并非事后伪造原始日志 |
| 安装中的DSH私有Node v22.22.0 | 延迟600ms，完整读取2,115,589字节，SHA/EOF/只读fd通过 |
| 独立代码审查 | 未发现P1/P2阻塞问题 |
| diff空白检查 | 通过 |
| 原始记录保全 | 2395个文件0变更/0缺失 |

最初受限沙箱的全量尝试有44个PermissionError（42个本地回环代理权限、2个只读ps权限），生产定向也有两项ps权限错误。保留原失败日志，并在允许本地离线测试能力后按相同代码完整复验通过；未将权限错误冒充产品故障。新增边界覆盖慢读大输入/完整EOF、只读stdin、异常/提前退出、取消/超时/进程组回收、输入篡改、FIFO/符号链接和历史拒绝覆盖。既有验收/失败路径由完整回归覆盖。

原现场没有保存父进程输入偏移/栈，不能声称排除了所有其它loader阻塞。离线复现确认的是一个真实、确定的投递缺陷；Node验证是安装运行时的stdin机制测试，不能替代修复后的完整DSH模型研究验证。遵守用户不补跑要求，未新增真实DSH研究来获取成功样本。

## 晚间正常消费仍待观察

前三股已在正常07:30消费者自行完成，独立审计确认仅Codex→gemini贡献，DSH均列failed_sources，无DSH/Claude票；已登记R14 unknown及scope合取限制保留。两份Codex报告的TEMP完整覆盖仍保留语义边界，本轮也没有旧active主张实际解除/covers分支的样本，不能笼统称全部语义已被实证。

第四股HK-02513于09:08:16才封口，首次正常消费机会是今天22:00；当前尚无completion，不能提前结论。仍由同一`dsh` heartbeat继续只读跟踪，完成正常消费审计后汇报并停用该一次性跟踪，不新增监控。

8次DSH均无原生session/usage，实际模型、请求数量和总费用保持null；费用下界0仅表示无可计价已报告记录，绝非零账单。Codex有可见终态tokens但实际模型及子/辅助覆盖边界未知，整轮费用同样null。详见保全的工具费用审计。

审计入口：[startup-timeout-repair](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-23/dsh-first-production-followup/startup-timeout-repair)；[完成检查](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-23/dsh-first-production-followup/startup-timeout-repair/completion-checks.json)、[缺陷分析](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-23/dsh-first-production-followup/startup-timeout-repair/failure-analysis.json)、[独立审查](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-23/dsh-first-production-followup/startup-timeout-repair/independent-code-review.json)、[源diff](/Users/xinquanzhou/Workspace/investment_research_methods/output/audits/investment/2026-10-23/dsh-first-production-followup/startup-timeout-repair/source-diff.patch)。正常消费者与工具/费用终态审计保存在其父目录，本报告不覆盖它们或任何旧实验结果。
