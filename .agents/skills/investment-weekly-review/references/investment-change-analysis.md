# 股票元框架变化检测（阶段②）

## 输入

- `AS_OF_DATE`、`CURRENT_META_RESULT`（必须有）；`PREVIOUS_META_RESULT`、配套 `PREVIOUS_CHANGE_DECISION`（可无）。完整周更按入口精确发现历史；单独比较使用用户给定的报告，不擅自换成自动发现结果。
- `CURRENT_FRAMEWORK`：`framework/investment_framework.md` 现行全文，跳过顶部维护说明 HTML 注释；方法、参数与歧义仍以该 canonical 为准。

## 首次运行

不存在实质 `PREVIOUS_META_RESULT` 时，不虚构上期、对比表或变化。保留 `CURRENT_META_RESULT`，用其建立基线，写一份精简的「元框架变化检测结果」：基本信息明确无基线；总结论为首次运行、建立基线、不做变化判定；末尾包含：

```yaml
FRAMEWORK_UPDATE_DECISION:
  update_needed: no
  update_level: none
  decision_reason: "首次运行，无历史基线可比，本次调研结果仅作为后续基线"
KEY_VARIABLE_CHANGES: []
UPDATE_FOCUS: []
DO_NOT_OVERREACT_ITEMS: []
```

## 有基线时

1. 先读已有日期研究、变化报告，必要时读适配报告及相关 git 变更。历史不靠 canonical 堆积。
2. **先复核上期观察项**：逐条处理上期「预备观察项」「下周复核」「若 X 则触发 light/significant」等延后判定，在报告「0. 上期预备观察项复核」标已触发／未触发／已失效。带明确框架更新条件的条目已触发，本身即可支持 `update_needed=yes`，无需周环比再过门；级别依原预设，没有预设从 light 起步。不得静默丢弃或无限“再等等”。
3. 读取 `projects/investment_change_analysis/INSTRUCTIONS.md`，遵循角色、原则、六步流程及输出模板，完成周环比。
4. **框架与现实一致性轴**：检查 regime 性假设、紧缩体制判定、机制权重、在册事件窗口、主线叙事与现实是否直接矛盾或累计错配。即使周环比不显著，也能构成更新依据；总结论明确这条轴的结果。
5. 只关注研究重点、顺序、权重、阈值的实质变化，不把措辞或单周噪音当框架变化。新延后事项必须带明确触发条件，供下期复核。

## 输出

- 写 `research/investment/weekly/<AS_OF_DATE>/investment-<AS_OF_DATE>-change-decision.md`，保留观察项节及 instruction 的完整模板。
- 末尾保留 `FRAMEWORK_UPDATE_DECISION`（`update_needed`、`update_level`、`decision_reason`）、`KEY_VARIABLE_CHANGES`（用 `research_meaning`，不是期货 `trading_meaning`）、`UPDATE_FOCUS`、`DO_NOT_OVERREACT_ITEMS`。
- 返回报告全文、路径及解析出的 `update_needed`。单阶段到此结束；无更新不动 canonical。同日写入与发布按入口规则。
