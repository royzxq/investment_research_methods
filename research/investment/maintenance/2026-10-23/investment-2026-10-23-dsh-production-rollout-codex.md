# DSH 接替 Claude Code：本机生产切换记录

日期：2026-10-23，Asia/Shanghai。用户明确授权替换；新自动研究已切为 **Codex + DSH**。2026-10-23 22:34 空闲重载 methods 与 AI 两仓服务，保留原每日05:00研究排期；没有立即启动正式投研。DSH 主/子模型为 DeepSeek Flash、high，保持每臂32768输出参数及两名活动子代理上限。

## 身份、合同与历史

DSH 使用真实 `generator=dsh`、`harness=dsh-cli`，独立报告、价格JSON、latest与provenance。固定映射为 codex→gemini、claude/dsh→claude，同批Claude与DSH互斥；仍只有原两个基础业务席位。新请求默认request/v2，结果和封口版本跟随请求；v1严格保持旧身份与旧字节。配置可保留三项查找绑定，每批仅冻结实际请求的生成端。

所有旧v1请求继续使用CC，包括现有待处理请求；已冻结计划、prompt、输入、claims、重试及封口不更换harness。新DSH首份同端估值基线为null，不能把旧Claude报告改名充当本端基线；下游按原稳定ID/scope接续生产限制，null或缺席不清掉旧控制。旧报告可以明确归属地参考。

投资canonical/compact、估值、R14缺证不得判passed、全部独立有效约束解除逻辑、holding/runtime/observation边界、共识权重、Coze条件、每日4只、168小时冷却、并发与一次重试政策保持不变。先前隔离实验没有提升为正式研究或共识输入。

## 执行接入与现场修复

生产配置：[research_runtime.production.json](../../../../config/research_runtime.production.json)。DSH为官方已安装0.2.1-rc.2及其私有Node入口；每次尝试使用独立HOME/状态、workspace-write与approval never。此无人值守策略与CC的auto-review能力不同。模型必须提交严格JSON回执，且原生事件有序完成；exit0、final或产物存在均不能单独证明成功。

DeepSeek凭据仅转交子进程内存，不写入patch、profile或prompt；固定官方provider/search地址。Jev引用既有0600密钥文件，可信工具桥只恢复TUSHARE_TOKEN，不向工具转交模型密钥。实际观察模型来自原生session header，缺失保持null。

发现并修复两项正式环境问题：

1. AI虚拟环境未安装PyMuPDF；改为真实探测已有兼容解释器并冻结选定绝对路径，本机选择miniconda3。独立审查发现先resolve会丢失venv环境，已保留launcher路径并增加回归，不跨Python版本拷库。
2. 旧methods启动脚本的nounset会在导入含未定义PYTHONPATH的export时停止，跳过后面的Tushare变量。先复现失败，再仅在原可信export导入范围关闭nounset，导入后恢复。最小launchd环境复验：DSH/PDF预检与Tushare变量均通过；未新增凭据副本。

## 验证

| 项目 | 结果及边界 |
|---|---|
| Methods离线全量 | 最终完整1122项全部通过，166.42秒；首轮受限沙箱有44项环境errors（42项loopback监听、2项ps），获准运行这些本机操作后全绿，不将受阻记录当作产品通过。 |
| AI受影响回归 | 正式myenv中246项通过；包含真实本地假DSH协议→共享runner→v2封口→原两席消费、旧控制接续、v2 CC回退、错版本/重复席拒绝、Coze严格>10%与原配对先提交、故障/幂等。没有真实生产写回事务。 |
| 结构与skill | 股票治理结构检查、stock-research quick_validate和两仓diff检查通过；结构检查不证明投资语义。 |
| 独立代码审查 | 高强度正确性与六维审查PASS；PDF路径问题已关闭；激活脚本与后续环境修复分别追加审查PASS。 |
| 官方CLI离线 | 原生patch schema、可信插件、Jev MCP配置及无生成启动验证通过，不计为模型调用成功。 |
| 真实DSH工具smoke | 北京时间22:28:34谷价启动，20.37秒自然完成、exit0、有序completed、实际模型deepseek-flash。越界写被拒绝，外部canary保持原字节；Tushare日历真实取到2行；合成PDF读取/渲染通过；Jev真实stdio初始化通过（没有提交Jev模型生成）；工具无模型密钥，产物中传入环境的已知秘密值扫描未命中。 |

真实smoke没有公司证据、九节研报或正式manifest，不进入共识，不能替代下一次定时完整研究的验收。按[官方价格页](https://api-docs.deepseek.com/quick_start/pricing/)当日谷价，原生日志两次主生成记录为8592未缓存输入、8448缓存读取、298输出token，已知估算 **$0.001492944**。另有标题辅助请求记录但用量未披露，全部费用合计保持null；这不是账户账单精确值。

## 部署、保全与回退

Methods原plist只追加配置及DSH独立路径，保留旧CC路径、05:00 calendar及其它字段；AI plist字节不变，调度器PID从3733变为97924，启动日志确认新进程。执行前持queue/consumer锁，确认没有活动任务、启动补跑或网络预检重试，远离下一计划任务；未kickstart、重置daily-check、改变冷却或取消在途研究。方法服务保持已加载且未运行。

切换前后两组业务保全清单合计6216个文件均无内容变化或缺失，包括框架、请求、已冻结执行材料、队列/额度、公司历史、CSV、本地模型报价及写回证据。原v3实验目录本轮未修改，原始试验及评分保留。日志、部署回执与本报告是本次新增记录。

Coze适配代码支持新旧基底，其既有heartbeat原为PAUSED，本次保持暂停、频率与目标聊天不变，仅同步DSH身份与当前两价提取接口，不恢复发送或外发测试邮件。其它自动化状态和排期未改。

回退只对未来新请求显式选择codex+claude/v1；保留对应CC runtime绑定和CLI。已冻结DSH批次继续原DSH配置恢复，不改身份、输入或价格/控制历史。不要回退到不能读取新合同/执行计划的旧代码。

本次仅本机生效，未提交、推送或创建PR。下一次定时研究尚未发生，不能提前宣称其完成或质量达标；正常预算、冷却和验收继续生效，无候选不调用模型。

审计入口：`output/audits/investment/2026-10-23/dsh-production-rollout/`，含activation、部署源码/CLI指纹（deployed-source-manifest-final.json）、回归日志、独立审查、原生smoke完整事件/状态/用量及保全清单。设计见[迁移ADR](../../../../docs/adr/ADR-20261023-dsh-research-seat-migration.md)。
