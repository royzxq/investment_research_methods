---
name: future-change-analysis
description: 期货元框架变化检测（流水线阶段②）：对比本次与上一次 meta future analysis 调研结果，判定是否需要更新期货执行框架，写入 research/<AS_OF_DATE>-change-decision.md。Use when asked to run the change-detection stage, or to standalone-compare two existing research reports without running the full pipeline.
---

# future change analysis（流水线阶段②）

## 输入

- `AS_OF_DATE`
- `CURRENT_META_RESULT`：本次 meta-future-analysis 产出的调研报告全文
- `PREVIOUS_META_RESULT`：上一次调研报告全文
- `PREVIOUS_CHANGE_DECISION`：上一次的变化检测报告全文（与 `PREVIOUS_META_RESULT` 同日期的 `<该日期>-change-decision.md`；找不到就视为无）
- `CURRENT_FRAMEWORK`：`framework/futures_framework.md` 现行全文（跳过顶部 HTML 注释行）

由 `futures-weekly-review` 编排器调用时，`PREVIOUS_META_RESULT` 按以下规则查找：
1. 在 `research/` 下找文件名匹配 `*-market-research.md`（**排除 `investment-` 前缀的股票轨道文件**）、日期早于 `AS_OF_DATE` 的文件，取日期最近的一份
2. 找不到任何这样的文件时，退回 `research/baseline-market-research.md`

单独调用本 skill（不经编排器）时，由调用方直接给出这些文本，不必套用上面的查找规则。

## 执行

1. **上期预备观察项复核（先于一切比较）**：读 `PREVIOUS_CHANGE_DECISION`，找出其中带复核条件的遗留项（"预备观察项"、"下周复核"、"若 X 则触发更新"这类被上期显式推迟的判定），逐条判定本周是否已触发，在报告里新增一节「0. 上期预备观察项复核」逐条给出处置（已触发 / 未触发 / 已失效），**不许静默丢弃**。任一已触发 → 其本身即构成 `update_needed: yes` 的充分依据（级别按该条目当时预设，未预设从 light 起步）
2. 读取 `projects/future_change_analysis/INSTRUCTIONS.md`，完整遵循其中的角色、目标、分析原则与六步分析流程；代入上面的输入变量做周环比对比
3. **框架-现实一致性检查（第二触发轴）**：对照 `CURRENT_FRAMEWORK` 里的 regime 性设定（机制档位、地缘轴定位、precheck 门、当期纪律清单等），判断本周调研结果是否与框架现状假设直接矛盾或错配已明显累积——即使周环比变化不大，框架假设与现实的错配同样构成触发依据（防温水煮青蛙）
4. **反摇摆护栏**：若本次判定将推翻现行框架在最近 1-2 周内刚做出的方向性设定（档位升降、轴定位变更、precheck 门改造等），必须有价格行为/硬数据级别的实证支持（如单日行情幅度、库存/通行量实测、利率定价变化），不能仅凭叙事或单条新闻；且报告中必须专门论证"为什么这不是对上周更新的摇摆式回滚"。达不到这个证据标准 → 宁可保持现行设定不动，把该项写成带触发条件的预备观察项留给下周复核
5. 只关注会改变交易重点、判断顺序、权重设置、阈值松紧的变化；不把措辞差异或单周噪音误判为框架级变化
6. 严格按 instruction 第六步给出的格式输出完整报告（外加第1步的「0. 上期预备观察项复核」节），末尾必须包含结构化字段 `FRAMEWORK_UPDATE_DECISION`（含 `update_needed: yes/no`、`update_level`、`decision_reason`）、`KEY_VARIABLE_CHANGES`、`UPDATE_FOCUS`、`DO_NOT_OVERREACT_ITEMS`；若本次又产生了新的"等下周验证"型推迟判定，必须写成带明确触发条件的预备观察项（下周第1步会逐条复核）

## 输出

- 把完整报告写入 `research/<AS_OF_DATE>-change-decision.md`
- 返回值：报告全文 + 解析出的 `update_needed`（yes/no），供编排器决定是否触发阶段③
