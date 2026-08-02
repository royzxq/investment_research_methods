---
name: framework-condense
description: 框架精简后处理（两条轨道共享）：从 canonical 框架全文无状态再生成一份去冗余的 compact 衍生文件，供人快速阅读。在 adaption（及期货侧 data-sync）提交之后、编排器开 PR 之前，在同一分支上运行。Use after the adaption stage commits a new framework version, to regenerate the human-readable compact derivative on the same branch; also usable standalone to refresh a stale compact file.
---

# framework condense（框架精简后处理）

## 定位（先读这一段再动手）

- **compact 是给人读的，不是给 AI 用的。** 流水线的所有 AI 环节（change-analysis / adaption / data-sync）与任何后续自动化分析，一律只读 canonical 完整版（`framework/futures_framework.md` / `framework/investment_framework.md`）。不要在任何 skill / prompt / 脚本里把 compact 接进 AI 数据流。
- compact 是**衍生文件**：每次从当期 canonical 全文**无状态重新推导**，不做增量修补。canonical 若被手工改过或某周漏更 compact，下一次生成自动重新对齐，无需追溯历史。
- canonical 上的【本次更新】标注、版本变更记录是 adaption instruction 的硬性要求，服务于人工审 PR 和流水线迭代——它们不动；compact 只是把这些簿记从"给人读的版本"里滤掉。

## 输入

- `CANONICAL_PATH`：轨道的 canonical 框架路径（期货 `framework/futures_framework.md`；股票 `framework/investment_framework.md`）
- `COMPACT_PATH`：对应输出路径（`framework/futures_framework_compact.md` / `framework/investment_framework_compact.md`）

## 只允许三类操作

1. **剥离历史标记**：【本次更新】【本次更新注记/新增/扩展/换版/值/当期值/改版/注记刷新】【vX.Y更新*】【新增】【未改动】【保留】【整表换版】等历史标记——删标记本身，**保留其修饰的内容**
2. **删除纯历史簿记**："(原4.2)"式旧值括注、"版本变更记录"类小节、"原文本=vX.Y全文存档"类存档指针、勘误历史说明（"原X为误，核定影响…"只留核定后的现值）、已过期的日期性注记（如已过去的事件窗口批注，注意：未过期的事件日历是活内容，保留）
3. **重复收敛为交叉引用**：同一要求/做法在多个章节重复陈述时，保留唯一权威出处（沿用框架自身的"唯一权威版/唯一出处/参数一律见X.X"惯例），其余处改为"见X.X"式指向

## 硬性保真边界（任何一条都不许越）

- **章节结构与顺序不动**：compact 的章节标题集合与顺序必须与 canonical 完全一致，不合并、不重排、不删节
- **规则措辞不改写**：保留的内容逐字保留，不做"更精炼的表达"式重写
- **所有数值参数逐字保留**：阈值、乘数、分位、系数、日期、合约代码——一个都不能丢
- **带复活/重启/解锁条件的"归档/冻结/挂起"内容是活逻辑不是簿记**，必须保留（如 D13 归档态及其复活触发、G 冻结及其解锁条件、曲线挂起及其复权条件）
- **核心约束允许保留必要重复**："重要的事情可以说三遍"——一票否决、硬止损、保证金/资金安全、"绝不X"类纪律条款，即使多处重复也保留，不收敛

## 强制自审清单（生成后逐项核对，不过不许提交）

1. 用 grep 类手段抽取 canonical 中的数值参数（百分比、乘数、阈值数字），逐一确认在 compact 中仍然存在；发现丢失 → 返工补回，不许带缺失提交
2. 比对两个文件的章节标题（`#`/`##`/`###`/`####` 行）集合与顺序完全一致
3. 确认 compact 中历史标记（【本次更新*】等）残留为 0
4. 统计压缩效果：行数/字数 before → after

## 输出与提交

1. compact 文件头部写 HTML 注释：`<!-- 衍生文件（仅供人阅读）：由 framework-condense 自 <CANONICAL_PATH> vX.Y 于 <日期> 自动再生；勿手改，任何 AI/流水线环节请使用 canonical 完整版 -->`
2. 把自审清单结果（含压缩统计）作为「精简版同步」小节追加到本次的 adaption-report（期货为「9. 精简版同步」，股票为「8. 精简版同步」）
3. 在当前框架更新分支上 `git add` compact 文件与 report，追加一个独立 commit（不与 adaption/data-sync 的 commit 合并）
4. 返回值：压缩统计一句话（供编排器写进 PR 正文）

单独手动调用（不在框架更新分支上、只想刷新 compact）时：直接在 main 上生成/覆盖 compact 并提交，自审清单照做，「精简版同步」小节省略。
