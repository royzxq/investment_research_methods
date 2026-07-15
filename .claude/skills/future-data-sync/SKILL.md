---
name: future-data-sync
description: 期货框架配套取数脚本同步（流水线阶段③之后的联动步骤，仅在阶段②判定 update_needed=yes 时触发）：判断本次框架更新是否引入了 scripts/future_data.py 需要跟进的结构性数据需求，需要就起草脚本更新，不需要就明确记录"本次无需变更"。在 future-adaption 已开好的分支上追加提交，不单开分支/PR。Use after future-adaption has drafted the new framework version and created its branch, before the orchestrator opens the PR.
---

# future data sync（框架③之后的联动步骤）

只在阶段②判定 `update_needed: yes` 且阶段③（future-adaption）已经在 `futures-framework/<AS_OF_DATE>` 分支上提交了框架改动之后触发；在同一个分支上追加提交，不新建分支、不自己开 PR（PR 由编排器统一在这一步和框架改动都提交完之后再开）。

## 背景：为什么要"判断"而不是每次都改脚本

`scripts/future_data.py` 的文件头注释里写明了它的定位：**框架每周滚动档位/参数时脚本零改动**——它只覆盖框架"1.1 输入接口"里结构化、可编程取数的部分（合约清单、价差分位、ATR/ADX/HV、股指贴水、国债利差等）；框架里大量内容本来就标注为"仍需手动"（现货基差、库存、产能性判决硬数据、SMM 现货口径等），这些永远不该被脚本化。

所以本阶段的核心判断题是：**这次框架变化，有没有新增/删除脚本本该覆盖、但目前没覆盖或覆盖方式已经过期的结构化数据点？** 不是"框架变了就一定要改脚本"。

## 输入

- `NEW_FRAMEWORK`：`framework/futures_framework.md` 阶段③写入之后的新版全文（工作区里已经是新版）
- `ADAPTION_REPORT`：阶段③产出的 `research/<AS_OF_DATE>-adaption-report.md`，重点看"2. 受影响模块"表的"修改类型"列
- `CURRENT_SCRIPT`：`scripts/future_data.py` 现有全文，重点看文件头注释的版本号（形如"vX.Y 框架数据脚本 — Tushare Pro 版 (vA.B)"）与"适用边界"小节（明确列了脚本覆盖 vs 仍需手动的范围）

## 第一步：判断是否需要改脚本

对照 `ADAPTION_REPORT`"受影响模块"表逐项检查：

- **需要改脚本的信号**（任一命中即需要）：新增/删除合约（0) CONTRACTS 表变化）、"1.1 输入接口"新增了脚本本该覆盖的结构化字段（价差/ATR/ADX/HV/贴水/利差类，不是现货/库存/产能性判决这类天然人工项）、"1.5 品种卡"新增品种且其验证输入里有结构化序列、修改类型标注为"新增字段"或"删除字段"且该字段属于脚本覆盖范围
- **不需要改脚本的信号**：修改类型是"参数调整""阈值收紧""阈值放宽""模块升权""模块降权""模块前置"且没有新增/删除结构化数据字段；新增的检查项本质上落在"适用边界"里已经标注为"仍需手动"的范畴（例如现货追认代理、产能性判决硬数据、SMM 口径——即使框架把这些从定性描述改成了量化门槛，只要数据源本身还是人工，脚本也不需要变）

拿不准时以"适用边界"小节的现有分类为准——脚本自己已经说清楚了什么归它管。

## 第二步A：不需要改脚本时

不要动 `scripts/future_data.py`。在 `research/<AS_OF_DATE>-adaption-report.md` 末尾追加一节：

```markdown
## 8. 数据脚本同步

- 结论：本次无需变更 scripts/future_data.py
- 理由：<逐条说明本次修改类型/受影响模块为何都不落在脚本覆盖范围内，或已被"适用边界"划为人工项>
```

在该分支上 `git add research/<AS_OF_DATE>-adaption-report.md`，追加一个 commit（不要和阶段③的 commit 合并，保留两次独立记录）。

## 第二步B：需要改脚本时

1. 精确定位需要新增/修改的章节（脚本按 §0/§0b/§1/§2/§2c/§3/§4 组织，对应关系写在脚本文件头注释里），只改真正需要的部分，不要顺手重构无关代码
2. 实现新的取数/计算逻辑，风格严格贴合现有代码（同样的 Tushare 调用模式、同样的降级/权限不足处理、同样的中文注释密度）
3. **更新文件头注释**：
   - 版本号升级（如 v2.9/v1.5 → v2.10/v1.6，前者跟随框架版本，后者是脚本自身版本）
   - 按现有格式追加一段"vA.B → vA.(B+1) 变更"changelog block（★ 开头的要点列表，说明改了什么、对应框架哪个变化、对应哪个 precheck/否决/策略编号）
   - **必须保留"诚实声明"小节的精神**：明确写出新增的取数路径是否已线上实测过——大概率没有（本环境同样无法访问 tushare/akshare 实网），如实写"未经线上实测，路径已用合成数据离线自测/或未自测"，不要声称验证过实际没验证的东西
   - 更新"适用边界"小节，把新覆盖的字段从"仍需手动"移到"本脚本覆盖"（如适用）
4. 跑一次语法健全性检查（`python3 -m py_compile scripts/future_data.py`），失败就返回重写，不要带着语法错误提交
5. 在 `research/<AS_OF_DATE>-adaption-report.md` 末尾追加：

```markdown
## 8. 数据脚本同步

- 结论：已更新 scripts/future_data.py（vA.B → vA.(B+1)）
- 改动摘要：<新增/修改了哪些章节，对应框架哪些变化>
- 验证状态：**未经线上实测**（本环境无法访问 tushare/akshare 实网）——纯计算路径已用合成数据自测的部分列出，涉及实际 API 字段/权限的部分请在有网络环境下运行并把报错贴回迭代
```

6. `git add scripts/future_data.py research/<AS_OF_DATE>-adaption-report.md`，在该分支上追加一个 commit

## 输出

- 返回值：是否改动了脚本（yes/no）+ 一句话摘要，供编排器写进最终 PR 描述
