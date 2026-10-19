# research_controls 语义修正与载荷精简：隔离实施结果

生成端：Codex。日期：2026-10-19（Asia/Shanghai）。本次依据用户“先修正语义，再压缩载荷”的授权实施，仅在两个隔离 worktree 修改代码和文档；后续按用户 review and commit 授权分别本地提交，未修改生产数据、未部署、未推送。新语义是隔离候选，不建立 adopted handoff；2026-10-18 已采纳的两价方案及免除前瞻影子期的决定保持。

## 1. 结果与范围

两仓同步完成持续限制、运行时判断、观察项的边界修正，以及双读旧载荷、新写紧凑载荷。完整理由不再进入新 CSV 控制单元格；保留可独立重放的执行状态、主张标识和证据绑定。

| 层 | 隔离变更 |
|---|---|
| 框架 | canonical 与 compact §6 明确生命周期、买入研究资格与到价分离、holding-only 未知、接续与解除；候选方法标记 stock-two-price-controls-v2 |
| 调研技能 | stock-research 及估值/一致性参考增加生命周期与解除覆盖；AI 仓录价、监控抽取技能明确列属主和不得自行改控制 |
| 调研脚本 | audit-v2 可记录 lifecycle/clearance.covers；新批次 two-price-controls/v2 强制 lifecycle；提供 claims 内容标识工具 |
| 发布属主 | research_consumer 聚合全部独立主张；先持久化不可变审计，再通过原 CSV 锁/CAS 发布紧凑 v2；calc_weighted_prices 不接受新写厚 v1 |
| 运行时 | 旧 v1 与新 v2 双读；默认只投影执行字段，整个合同缺失仍保守阻断；holding-only 复评未知不扩大 entry/add |
| 下游 | candidate_review 接回有未解事项的 HOLD，沿用配置族、节奏、预算；AH 配对、候选复评与卖出缓存比较业务语义，排除纯发布元数据 |
| 文档 | AI 仓 ADR-20261019、system_boundaries、monitor_strategy_mapping 与 CHANGELOG 同步 |

隔离根目录：

- methods：`/private/tmp/methods-controls-semantics-20261019`，基线 `0ed4d748f20d61059658d26f9cdf7d860011c554`。
- AI：`/private/tmp/ai-controls-semantics-20261019`，基线 `a64a873f606f2d18ac3af04bef86cd70574010b1`。
- 两仓隔离分支均为 `codex/research-controls-semantics`。原工作区的无关改动和文件未覆盖。

## 2. 语义裁决

1. **持续保留**：已触发研究限制和判断对应资格必需的缺证项为 persistent；按 entry/add/holding 的实际范围执行。证据不足不清除。TEMP 缺等价运行时属主时继续保留；取消追加计划、D5 重建、R6 事后逐股复评均不因精简丢失。
2. **运行时判断**：纯现价相对 P1/T1、最低收益等为 runtime，交原价格/收益规则。buy_candidate 是研究资格，现价高于 P1 仍可由运行时给 HOLD。新报告不得把纯价格条件标成当前持续研究阻断；这需要研究者核语义，程序不靠关键词猜测。
3. **仅观察**：未触发经营信号、复评路标为 observation，留完整条件/monitoring，不进入未解研究集合。普通观察不要求伪造 constraint。
4. **持仓未知**：完整合同内仅 holding 复评未知要求补证/复评，不凭空扩大 entry/add；整个合同缺失、确认失效/退出，以及相应 entry/add 缺证仍阻止新增。卖出通路不因研究缺口变成不可达。
5. **历史接续**：旧价格阻断不按 ID、格式升级或跌价自动删除；须核原证据后明确更正。不同 ID 不自动去重；同 ID 不同来源主张全部保留，排序不决定取舍。解除多个独立主张须有证据并完整覆盖其内容标识，缺一保留限制。单主张旧式明确解除保持兼容。
6. **R6 与 D5**：R6 保留“实质暴露且（前 48 小时或相关窗口缺预案）”及事后按结果逐股复评，不按过窗解冻。D5/R21 阶段、合取/合法替代路径和原独立重建路径保持；waiting_review 的证据不能补足 rebuild_review_complete 的解除覆盖。

规则、投资阈值、预算比例和价格公式未调参。P1/T1、首笔 60%/预留 40%、独立止损、真实发布时间和报价 T+1 继续走原路径。

## 3. 紧凑载荷与唯一业务来源

research_contract 仍为 stock-research/v4；研究 JSON 和 audit 版本仍为 v4/audit-v2。CSV 新存储载荷 research-controls/v2 保留各 scope 的 status/refs，以及 id/scope/action/status/claims、必要的解除覆盖和 D5 阶段。它不保存完整来源正文与解除理由。

完整内容由现有发布属主存入 CSV 根目录下 `investment_results/research_writeback/controls-evidence/<sha256>.json`，CSV 保存相对路径与 SHA256。审计先写、fsync、以 create-only 硬链接发布并 fsync 目录；已有同名文件内容不符即拒绝。预览应用前校验哈希及执行语义，之后沿原 CAS 提交 CSV。失败可留下未引用审计，但不会获得执行资格。原本地恢复归档已覆盖该子树。

CSV 是运行时资格唯一业务来源，运行时不查审计文件决定资格。审计丢失不会悄悄改动已经提交的资格，但下一次发布须先恢复完整证据，否则拒绝。已提交事务的归档重试保留原发布时间；控制收紧不依赖报价归档成功才生效。人工修 CSV 不属于本次迁移路径。

候选 AI 仍接收原有 catalyst_and_risk 等文本；本地证据路径不被当成远端模型已读取的理由。复评结果也不能直接清除 CSV 的控制。

## 4. 冻结样本验证

输入为此前语义审查冻结的 998 条 CSV 记录，SHA256：`fccdb7ba35401ce3a1d0d207849bfb9e72a1bfbdf9632f5e45481580b3a71012`。不是 998 家公司。只在隔离副本重编码两条 v4 控制，996 条 legacy 记录逐字节保留；价格和 available_at 原值保持，目的仅是格式等价，不能把该副本当成一次新的实际发布。

| 代码 | 原控制字符 | 新控制字符 | 缩减 | 未解 ID / scope 配对 |
|---|---:|---:|---:|---:|
| 600900 | 6,092 | 2,807 | 53.92% | 12 / 18 |
| 300760 | 4,484 | 2,048 | 54.33% | 9 / 14 |

21 个未解 ID 全部保留；180 组时点、持仓已知/未知、决策门禁结果一致；两仓 34 条主张内容哈希一致；两条新载荷均可按其证据绑定恢复完整内容。

另保存独立语义更正示例：明确说明 PRICE_ABOVE_P1_HIGH 仅为当前价相对 P1 后，只解除 `PRICE_ABOVE_P1_HIGH/entry`；其它未解 ID/scope 不变，entry/add 仍未获资格。该示例不写入格式等价 CSV，更未作用于生产。

生产 CSV 在整个验证前后的 SHA256 均为上述输入哈希。已有 CSV 若历史上已丢失同 ID 的来源差异，单凭重编码不能恢复；正式复评须回原始审计/报告核证，不能声称格式压缩重建了历史结论。

复现与结果：`output/controls-semantics-validation/validate_frozen.py`、`results.json`、`explicit-price-correction-example.json`。该程序固定读取冻结输入，输出固定在本隔离目录，不是生产迁移工具。

## 5. 验证结果

| 检查 | 实际结果 |
|---|---|
| methods 完整离线 unittest | 815 通过 |
| AI 完整 unit/integration + calc_weighted_prices | 4,656 通过，103 按原条件跳过 |
| 最后受影响路径回归 | 813 通过，覆盖候选、sell_agent、monitor 映射、报价、scope 与跨仓路径 |
| 最后对抗修复回归 | 63 通过，包含最终 D5 覆盖、来源顺序、压缩重放、发布和跨仓测试 |
| 跨仓 fake-CLI | 合法 unavailable → seal → control-only → 紧凑 CSV → 时间可见门禁 → 幂等重试通过；未调用真实模型 |
| 旧批次兼容 | v3 report-quotes/v3、v4 two-price/v1，Codex/Claude 四组提示词与基线逐字节一致；旧 prepared prompt/input 保持 |
| 框架治理 | investment_framework_governance --check 通过，仅证明结构 |
| 技能校验 | stock-research、AI 录价、AI 监控抽取的 quick_validate 均通过 |
| diff 检查 | 两仓 git diff --check 通过 |

完整回归后最后新增的 D5/主张标识边界及来源排序修正，另由最后两轮定向回归覆盖；各轮测试不相加冒充唯一测试数量。初次沙箱测试的本地端口/ps/caffeinate 受限已在隔离目录提升权限重跑通过，未放宽断言或跳过有效测试。完整 AI 回归 14 个 warning 为原依赖弃用、零下行波动计算与既有测试返回值提示，非本次新增失败。

日志归档于 `output/controls-semantics-validation/`：`methods-full-final.log`、`ai-full-final.log`、`ai-affected-final.log`、`last-review-regression.log`、`cross-repository-boundaries.log`。没有真实 API/生产调度/交易验证；本次不是收益回测，不证明新增研究门禁的收益有效性，也不要求前瞻影子期。

## 6. 正确性对抗审查与六维检查

由当前 Codex 高强度自行审查全部变更和新增文件，重点检查证据丢失、重复发布、旧未知降级、不同来源冲突、clear 重放、D5 阶段混用和只加仓/持仓 scope。未使用独立代理评审。

已复现并修复：多来源解除只保留一方覆盖导致重放误冻结；unknown 摘要重放漂移导致证据语义绑定不符；外置预览目录与审计路径不兼容；D5 非完整阶段证据不能混入完整解除覆盖。补测覆盖不可变审计损坏、路径越界、格式非法、运行时审计缺失、元数据不触发复评和实质条件变化仍触发复评。来源冲突证据也按内容稳定排序。

| 六维 | 结论 |
|---|---|
| Hard Boundaries | PASS：CSV 写入仍由 calc_weighted_prices/发布属主；催化监控只改自身列；无行情/指标/策略参数新属主 |
| Hard Stops | PASS：无删除模块复活、凭据输出、全仓格式化、远端消息/推送/交易 |
| Dead Code | PASS：新投影、哈希、绑定分别有运行时/发布/缓存等实际调用；旧兼容分支因真实历史仍保留 |
| 范围纪律 | PASS：同一控制语义/序列化特性，跨仓及下游必要联动；无新调度器、预算或数据库 |
| ADR/文档 | PASS：schema/API/原子发布边界有 ADR 和 CHANGELOG，框架、技能及现行合同同步；未建立生产 adopted handoff |
| 测试约定 | PASS：行为与失败路径测试、真实入口的离线夹具、冻结样本差分，保留实际未验证边界 |

## 7. 版本与生产边界

框架旧/新全文哈希和指纹、稳定 ID/数字对照见 `framework-fidelity.json`、`framework-governance.json`；两仓代码文件哈希见 `implementation-manifest.json`。本次没有修改市场状态观测、生产 CSV、真实持仓或调度配置，也没有向既有 PR 推送。

未来若另行授权部署，应先让两仓读写合同同步，再用原发布事务逐项处理经过核证的旧记录；不能先批量删除旧控制或直接复制本次格式等价 CSV。旧 prepared 继续旧合同，新批次才用新模板。无需据此新增前瞻影子期。

## 8. 精简版同步与七项自审

canonical 与 compact 同步生命周期和解除边界，除此之外保留旧规则内容；原有 R/D 稳定 ID、数字/公式/阈值未删除。版本及“生产基线”标签调整不改变原采纳事实。尺寸、旧新哈希与精确变更行记录于保真结果。

1. 覆盖：新三分语义、scope、历史接续、完整条件表和执行条件在两份框架均承载；旧规则行保持，未新增第二权威规则表。
2. 数字：原数字 token 无删减；P1 公式、60%/40%、R6 的 48 小时、D5/R21 阈值与且/或关系保留。token 检查本身不证明逻辑等价，另核本次新增表述的作用范围。
3. 引用：R/D 编号无改名重排；新内容回指 canonical §6.1；旧 D5/R21 原独立重建路径保持。
4. 抽检：R6 实质暴露+窗口/预案+事后复评；D5 仅退回等待不能全面解冻；holding-only 未知与整个合同缺失；P1 资格与价格各自独立。均核正反和缺证边界。
5. 例外/解除：TEMP 未有接替仍保留；未知不当作证伪/解除；多主张解除覆盖不齐保留；已有价格误分类需显式证据更正。
6. 动静分离：仅新增方法语义，原日期状态块和市场读数未重算、未改写；不把旧“当前”当作新行情核验。
7. 检查与限制：结构治理、冻结差分和行为测试通过；不是全框架投资有效性证明，也不声称逐项市场事实已重新验证。

## 9. 提交前追加审查

本轮 review 检查两个 worktree 相对各自 HEAD 的全部改动与未跟踪文件，并再次做高强度正确性对抗审查和六维检查。发现并先修复两处问题：

- D5 新研究重新判为 deepening 时，旧 waiting_review/rebuild_pending_company_review 可能因字符串排序保留。现按本轮验收阶段更新；本轮来源阶段冲突记 unknown，仍保留未解限制。新增四组阶段迁移、冲突来源顺序及紧凑重放回归。
- 单主张明确填写错误/空 clearance.covers 时，原单主张兼容分支可能忽略覆盖范围并解除另一项事实。现显式 covers 必须匹配；研究仓验收本端未解基线和 AI 仓消费门禁同步修复，未填写 covers 的旧单主张明确解除继续兼容。新增错配/正确匹配/旧式兼容回归。

修复均先复现失败再通过。完整最终回归与哈希检查在 `output/controls-semantics-validation/review-and-commit/` 归档；不把上节较早回归轮次冒充最终轮次。生产 CSV 未作为提交内容，运行数据、测试日志和内容寻址审计也不入 Git。

最终结果：研究仓完整 unittest 816 项通过；AI 仓完整 unit/integration/calc_weighted_prices 4,664 项通过、103 项按原条件跳过，14 个原有 warning。两仓合约、跨仓 fake-CLI、旧冻结兼容、框架治理、三个技能 quick_validate 与 diff 检查通过。冻结样本仍为 996 条 legacy 字节保留、21 个未解 ID 保留、180 组门禁一致。当前未发现剩余阻断性问题；未运行真实 API 或生产调度。
