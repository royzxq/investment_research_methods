---
name: framework-condense
description: 框架精简后处理（两条轨道共享）：以"单一出现不变式"从 canonical 框架全文无状态再生成一份去冗余的 compact 衍生文件，供人快速阅读。在 adaption（及期货侧 data-sync）提交之后、编排器开 PR 之前，在同一分支上运行。Use after the adaption stage commits a new framework version, to regenerate the human-readable compact derivative on the same branch; also usable standalone to refresh a stale compact file.
---

# framework condense（框架精简后处理）

## 定位（先读这一段再动手）

- **compact 是给人读的，不是给 AI 用的。** 流水线的所有 AI 环节（change-analysis / adaption / data-sync）与任何后续自动化分析，一律只读 canonical 完整版（`framework/futures_framework.md` / `framework/investment_framework.md`）。不要在任何 skill / prompt / 脚本里把 compact 接进 AI 数据流。
- compact 是**衍生文件**：每次从当期 canonical 全文**无状态重新推导**，不做增量修补。canonical 若被手工改过或某周漏更 compact，下一次生成自动重新对齐。
- canonical 上的【本次更新】标注、版本变更记录是 adaption instruction 的硬性要求，服务于人工审 PR 和流水线迭代——它们不动；compact 只是把这些从"给人读的版本"里滤掉。

## 输入

- `CANONICAL_PATH`：轨道的 canonical 框架路径（期货 `framework/futures_framework.md`；股票 `framework/investment_framework.md`）
- `COMPACT_PATH`：对应输出路径（`framework/futures_framework_compact.md` / `framework/investment_framework_compact.md`）
- 上一版 compact（如存在）：仅用于 R-ID 连续性（见动作2），不作为内容来源

## 核心原则：单一出现不变式

**任何规则/阈值的全文只允许出现一次（在其权威章节），其余位置只能引用。** 全部压缩收益来自删副本，不删语义、不改写措辞——因此无损，且无损性必须经自审清单验证（构造上无损 ≠ 执行上无损）。

操作判据：**如果修改某处内容时需要同步修改别处的文字，那两处就是副本关系，应该抽取收敛。**

## 四类操作

1. **元数据外移**：版本史的 SSoT 是 git/adaption-report，不是正文。剥离历史标记（【本次更新*】【vX.Y更新*】【新增】【未改动】【保留】【整表换版】等——删标记本身，保留其修饰的内容）；删除纯历史簿记（"(原4.2)"式旧值括注、"版本变更记录"类小节、"原文本=vX.Y全文存档"类存档指针、勘误历史说明只留核定后现值、已过期的日期性批注——未过期的事件日历是活内容，保留）
2. **规则抽取**：同一规则重复 N 处 → 在其权威章节保留唯一全文定义并赋稳定编号（R1、R2、…），其余位置替换为 `[Rn]` 引用（也可沿用框架已有的"见X.X/唯一权威版"惯例，但优先 R-ID——章节号会漂移，R-ID 不会）。**R-ID 跨周连续性**：再生成时先读上一版 compact，未变的规则沿用原编号，新规则续号，**永不重编已有编号**（否则周环比 diff 全是噪音）；无上一版时从 R1 起编
3. **删缓存副本**：原则/总览类章节里"预告"下游规则的摘要副本全删，只保留真正全局的原则（在原则章节安家的内容才留在原则章节）。摘要副本是 desync 的主要来源——本条**取代**旧版"核心约束允许重复"的豁免：一票否决/硬止损类条款同样只在权威章节出现一次，别处用 `[Rn]` 引用
4. **关系归一**：多个章节实为同一张关系表（如「信号 × 动作」）按某一属性切开的不同视图时，可合并回一张规范化表——这是**唯一允许改变章节结构的操作**，且须过两道护栏：①同关系判定：行键空间相同、各视图的列互为互补切片才许合并；语义不同的表（如一张是评分扣减、一张是仓位乘数）不合并，只互相引用；②合并必须在报告里附"旧章节 → 新表"映射清单

## 硬性保真边界（任何一条都不许越）

- 语义零删除、措辞零改写：保留下来的内容逐字保留，压缩只来自删副本
- 所有数值参数逐字保留：阈值、乘数、分位、系数、日期、合约代码——一个都不能丢
- **带复活/重启/解锁条件的"归档/冻结/挂起"内容是活逻辑不是元数据**，必须保留（如 D13 归档态及复活触发、G 冻结及解锁条件、曲线挂起及复权条件）
- 除关系归一外章节结构与顺序不动；canonical 永远不动

## 强制自审清单（生成后逐项核对，不过不许提交）

1. **数值参数**：用 grep 类手段抽取 canonical 中的数值参数（百分比/乘数/阈值/日期），逐一确认在 compact 中仍存在；丢失 → 返工补回
2. **引用完整性**：每个 `[Rn]` / "见X.X" 引用都能解析到唯一定义，无悬空引用、无重复定义
3. **关系归一 cell 级完整性**（如本次做了合并）：合并前各视图的每个 (行, 列, 值) 三元组在合并表中全量存在，给出 cell 数 before→after；映射清单写入报告
4. **副本一致性检测**：收敛 N 处副本时若发现副本之间文本互相矛盾——这是 canonical 已发生漂移的证据，**不许静默择一**：按权威章节版本收敛，并把矛盾原文记录进「精简版同步」小节提请人工修 canonical
5. **历史标记残留 0**（比对以剥标记后的文本为基准；【已过】【待数据】类活状态标签不算历史标记）
6. **章节对照**：未参与关系归一的章节标题集合与顺序和 canonical 一致（剥标记后比对）；参与合并的按第3条列映射
7. **压缩统计**：行数/字数 before → after

## 输出与提交

1. compact 文件头部写 HTML 注释：`<!-- 衍生文件（仅供人阅读）：由 framework-condense 自 <CANONICAL_PATH> vX.Y 于 <日期> 自动再生；勿手改，任何 AI/流水线环节请使用 canonical 完整版 -->`
2. 把自审清单结果（含压缩统计、关系归一映射、副本矛盾发现）作为「精简版同步」小节追加到本次的 adaption-report（期货为「9. 精简版同步」，股票为「8. 精简版同步」）
3. 在当前框架更新分支上 `git add` compact 文件与 report，追加一个独立 commit（不与 adaption/data-sync 的 commit 合并）
4. 返回值：压缩统计一句话 +（如有）副本矛盾提醒（供编排器写进 PR 正文）

单独手动调用（不在框架更新分支上、只想刷新 compact）时：直接在 main 上生成/覆盖 compact 并提交，自审清单照做，「精简版同步」小节省略，副本矛盾如有则写进 commit message。
