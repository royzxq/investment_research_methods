# 两价框架实施与影子验收记录

日期：2026-10-18，Asia/Shanghai。生成端：Codex。状态：已完成候选实现与离线影子验收；未采纳生产，未提交或推送。

用户授权依据：按既定两价方案同步框架、调研技能、脚本和下游系统，完成必要测试；策略先影子验证、暂不切生产、不推送。

## 已完成范围

| 层次 | 最终行为 |
|---|---|
| canonical / compact | 核心报价仅 P1/T1；退休 P2/T2 报价与步长；原加仓、逻辑失效、复评、退出条件独立保留；稳定 R/D 编号、门槛、例外、解除条件与 60/40 预算不变；观测块保持 |
| 调研技能 | 默认 stock-research/v4 与 audit-v2；完整条件表承载全部适用条件，monitoring 仍为重点摘录；entry/add/holding 按范围声明；不推导第三价格 |
| methods 脚本 | 估值提取、审计、runner、exchange、latest、Coze 与维护交接引用同步；旧冻结批次按原快照恢复，legacy writer 绑定具体证券、日期、生成端及目标路径 |
| 下游数据 | v4 P1/T1 共识沿用既有席位与权重；不继承或生成 P2；CSV 原子发布报价及控制，控制按实际发布时间生效；仅有完整验收封口的无报价研究可单独收紧控制 |
| 限制接续 | 缺席、遗漏或普通 eligible 不解除旧限制；typed evidence、ID/scope、D5 重建阶段与已确认持仓风险逐项保留；冲突按受影响范围 unknown，发布后回放不丢解除证据 |
| 策略候选 | P1 以下满足原最低收益要求才给至多普通买入；P1/T1 之间观察；T1 以上保留原卖出侧。无 RR/P2 止损距离；缺波动风险尺度不新增敞口；AR 双重时点、协议与滚动分组隔离 |
| 运行下游 | AR 后、保存前及执行前重新校验新增资格；实际有仓用 add、无仓用 entry、未知同时要求两者 eligible；卖出、成本纪律与原移动止损独立保留 |
| 复核与展示 | 卖出智能体、候选复核、快照/缓存、工作台、模型评价适配两价与独立控制；AI 持有/失败不能隐藏已知退出复核事项；不同 A/H 条件不共享复核结论 |

本次没有为下游另设 60/40 自动资金分配；research eligible 也不是执行许可。v4 买入策略须显式影子上下文，状态仅内存；默认生产写回拒绝 v4，影子 CSV 和报价库限定隔离目录。未生成 adopted handoff。

## 实际验证

- methods：`python -m unittest discover -s tests -v`，**805 项通过，104.550 秒**。日志末尾明确 OK；测试后一次 shell 尾部包装因 zsh 的只读变量退出 1，不是测试失败。
- 下游合并工作树：研究合同/真实离线跨仓联调、共识、发布/中断恢复、报价库/备份、评价/工作台、core/risk/Regime、完整 sell_agent/candidate_review、monitor、AR、执行与重定基定向联合回归，**1,335 项通过，43.10 秒**。两个 warnings 来自现有 websockets 弃用提示。
- 股票 governance：通过；canonical/compact method fingerprint 一致于候选记录，结构检查不代表全部语义等价或投资有效。
- stock-research、investment-weekly-review 与下游手工报价 skill：quick_validate 均通过。最初用 methods 解释器校验 skill 缺 PyYAML，改用现有 AI 虚拟环境后通过，没有安装或改依赖。
- 两仓 `git diff --check` 通过。
- 真实代码离线链路：methods runner → completed unavailable → audit-v2 → seal → AI load/prepare/apply；发布 control-only，不复制旧价格到新日，保留 T1 原日期和实际 available_at。采用 fake CLI 与临时目录，不是真实模型或外部 API。
- `scripts/two_price_shadow.py` 在整合工作树真实运行；迁到持久目录后又重放 16 个场景，结果一致。模块导入尝试持久化 Tushare 本地 token 缓存时被沙箱拒绝并跳过；未输出 token、未据此取行情、未修改该缓存。

完整日志、场景输入、输出及文件哈希见 [证据目录](evidence/two-price-implementation/manifest.json)。

## 影子结果与解释边界

冻结来源为原 ai_investment 本地 `investment_results_enhanced.csv` 的 52 条记录，数据日期 2026-10-15；只使用各记录保存的现价和价格锚，在同一默认 DecisionConfig 下比较。

| 价格层候选 | 旧三价 | 两价候选 |
|---|---:|---:|
| 持有/观察 | 21 | 49 |
| 减仓 | 31 | 3 |

28 条变化来自 P1 与 T1 之间改为观察。另 16 个冻结合成场景覆盖旧 P2 附近与极低现价、P1/T1 边界、仅加仓受限、有仓/无仓/未知持仓、确认退出、风险缺失及控制缺失。两价最终为买入 6、持有 7、减仓 2、清仓 1；已知退出作为独立持仓处置事实保留，不以缺依据的自动清仓数量替代。

这些结果是价格层与门禁反事实检查，**不是原生产预设的历史复现，也不是收益回测**。监控快照不含完整逐时点行情、历史 v4 控制或持仓；缺项没有补造。尚未验证两价策略的收益、回撤、换手、交易成本与持仓集中度优劣，不能据此切换生产。

## 独立审查闭环

通用正确性审查按 high effort 运行，并由跨模块代理互审。所有已报告实质问题均修复并加失败路径回归：

1. legacy writer 可借另一批有效 manifest：绑定具体交付身份和输出目标。
2. 非文本 clearance、n/a 或缺 D5 重建阶段可解除限制：收紧类型和基线解除条件。
3. 未解 holding freeze 投影消失、已确认退出被降级、多来源释放证据在回放中丢失：按 scope 保留风险与确定性解除证据。
4. CSV 已提交但报价归档失败，随后另一股票更新造成恢复阻断：只恢复本笔归档，保留其他记录和原发布时间。
5. 保存前只看旧 reject，漏掉数值 P1 的新控制：v4 每次独立复核；执行前再用实际持仓。
6. 候选成功复核不保存条件基线，及 A/H cadence/共享结论覆盖强制复核：成功基线持久化、失败保留、强制到期优先、条件不同隔离。
7. AR 差分引入 T+1 不可见报价，滚动统计/分组混合协议：双重可见过滤后差分，窗口与分组隔离。
8. 非影子 v4 被旧 AR 修改卖出：overlay 入口直接隔离；监控旧 AR 历史排除当前 v4。

最终独立闭环复核未发现新增实质问题，定向边界测试通过。

| 项目六维 | 结论 |
|---|---|
| Hard Boundaries | PASS：CSV/报价属主、现有指标与数据入口保持；控制聚合不变成第二业务状态源 |
| Hard Stops | PASS：无已删模块复活、无凭据输出、无真实交易或外发 |
| Dead Code | PASS：legacy 路径仍属当前生产及历史读取，依用户暂不切生产要求保留；新影子入口可真实运行 |
| 范围纪律 | PASS：跨仓联动均属于获批两价迁移，没有无关策略调参或全仓格式化 |
| ADR/文档 | PASS：数据与策略 ADR、三个运行契约、CHANGELOG、技能及方法引用已同步 |
| 测试约定 | PASS：离线契约、真实本地链路、失败路径及高强度只读审查完成，外部依赖与投资验证限度明确 |

## 保存位置与生产边界

- methods 候选分支 `codex/stock-two-price`：`/Users/xinquanzhou/.codex/worktrees/stock-two-price/investment_research_methods`。
- AI 候选分支 `codex/stock-two-price`：`/Users/xinquanzhou/.codex/worktrees/stock-two-price/ai_investment`；已从临时 worktree 移到持久目录。
- 两仓均保留未提交修改。原 methods 的 main 与 AI 的 dev 未切换；原 AI 工作树仍干净，methods 原有未跟踪研究资料保留。
- 未写生产 CSV、模型权重、持仓台账、调度配置或云端提示词；未重载生产服务，未 commit、push、创建 PR、发送邮件/飞书或执行交易。

后续生产采纳仍需有实际发布时间与历史控制的组合影子验证、外部 Coze 提示词/服务契约核对，以及用户明确切换决定。本次完成候选实现与必要软件验证，不将这些未完成的采纳条件冒充已通过。
