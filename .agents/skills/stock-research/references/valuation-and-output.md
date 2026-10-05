# 估值与轻量输出契约

本文件是 `stock-research` 的计算接口，不是第二份投资框架。规则、固定数值和强制映射以 canonical 为准。

## 研究假设如何形成

1. 收入、利润率、估值锚分别列低/中/高情景、证据日期、适用口径和最脆弱假设。利润须区分经常经营、一次性收入与估值收益；不得仅复制卖方目标价。
2. 对 `d_base/r_chip/r_v5/r_gov/r_terminal`，在报告列“已在盈利/倍数中反映的风险→仍需覆盖的风险→本次取值及理由→敏感性”。无额外风险时可论证取 0，不代表缺证据默认无风险。
3. canonical 的标准/上沿/一档未给绝对数值时，先解释本公司可接受的研究区间，再选基准；从严约束选择所论证区间的上侧。所有这些是**本次研究假设**，不是用户账户参数或框架常数。若范围无法论证，补研、换合适模型或给真正不可估结论，不为避免 null 任填折扣。
4. 敏感性至少展示最重要假设变化对 V50/P1 的影响，并核对是否改变结论。情景下沿须为同一估值模型可解释的保守情景；P1 的 low/base/high 使用同一组基准折扣，替代折扣情景放报告，不混成含义不明的上下沿。
5. `step_down` 只能在 canonical 的 5%–10% 内选择并说明理由。仓位上限缺失时 cap 留在报告参数化，不影响价格计算。取消 P2 不把其原 40% 自动转移到 P1。

## 导出 v2（仅三个顶层键）

| 对象 | 固定字段 | 语义 |
|---|---|---|
| `meta` | `schema_version, code, name, valuation_date, currency, report_path` | schema 固定 `stock-research/v2`；报告路径相对仓库根；币种为上市报价币种 |
| `price_map` | `mode, reason, v50, p1, p2, t1, t2` | 全部数值价格统一为报价币种/股；没有仓位、Gate 全树或证据副本 |
| `monitoring[]` | `variable, current, as_of, trigger, action, source, next_check` | 1–10 项，变量不重复；当前值不能与报告底稿矛盾 |

- `mode`：`buy_candidate` 买入型候选、`tracking` 跟踪、`observation` 观察、`frozen` 冻结、`rejected` 否决、`unavailable` 因输入不足不可估。它是研究用途，不是下单许可；除买入型可为 null 外，`reason` 必须解释限制。
- 前三种模式必须有数值 `v50/p1={low,base,high}`，价格为正且有序。后三种不产新的 P1/P2；允许在 `v50` 保留此前已核验参考值，但报告必须说明其来源与失效边界。没有则为 null。
- `p2={status,price,reason}`：`active` 有效参考价；`cancelled` 按规则取消，价格 null；`suspended` 暂停触发，保留已计算参考价格和恢复条件；`unavailable` 不可计算，价格 null。除 active 外均必须理由；冻结/否决/不可估模式只能 cancelled/unavailable。tracking 下 active 仅指跟踪参考有效，不代表可以开仓。
- `t1/t2={price_condition,events}`：前者为可解释的价格条件文字，后者为非空事件条件列表。没有适用价格边界时明确写“当前不适用：原因”，不要捏造数值阈值。接近 V50 上沿/明显高于 V50 如需量化，必须在报告注明研究假设，不能称为框架固定比例。
- `monitoring.current` 为数值、明确带单位的文字或 null；非空必须有 `as_of`，不能晚于估值日。来源写可追溯 URL/公告章节或数据包字段；`trigger` 包含窗口、单位和方向，`action` 指定重算/撤价位/取消 P2 等动作。`next_check` 为日期或明确事件文字。未取得当前值时 current/as_of 可 null，原因及补证路径写报告，不用 0 代替。
- 字段不再重复保存 precheck/rules/valuation 全推导/terminal/qualitative_findings/key_inputs/gaps。折扣、cap、评级、解除条件和其它框架必答仍保留在报告；schema 精简不等于研究删项。

## 确定性计算工具

从已核验底稿与研究假设组装临时模型文件，放本次 `output/stock-research-.../`。先生成候选 JSON、完成报告和语义验收，再移到未占用的最终日期路径。工具不取行情、不判 Gate、不更新 latest、不覆盖文件。

```sh
python3 scripts/stock_price_map.py build --input output/<本次目录>/model-input.json --output output/<本次目录>/price-map.json
python3 scripts/stock_price_map.py check output/<本次目录>/price-map.json
```

临时输入只有 `meta, mode, reason, valuation, discounts, step_down, p2, t1, t2, monitoring`。除计算相关项外与最终字段同义；meta 可省略 schema_version，工具自动补齐。输入 p2 不带 price。

`valuation` 二选一：

```json
{
  "kind": "equity_value",
  "values": {"low": 486, "base": 630, "high": 792},
  "currency": "CNY",
  "unit": "100_million",
  "shares": 2214000000,
  "fx_to_quote": 1
}
```

上例只是单位接口演示，不代表本期正式研究结论。`equity_value` 是归属于普通股股东的权益价值，不能直接填 EV；unit 仅 `currency/million/100_million`，股份数为实际股数，不是“亿股”。

```json
{
  "kind": "per_share",
  "values": {"low": 19, "base": 31, "high": 50},
  "currency": "HKD",
  "unit": "per_share",
  "fx_to_quote": 1
}
```

每股模式不再传 shares。跨币种必须补 `fx_source`（出处、日期、方向）；`fx_to_quote` 定义为“1 单位输入币种等于多少报价币种”。例如 1 HKD=0.865 CNY，HKD→CNY **乘 0.865**，CNY→HKD **乘 1/0.865**。同币种只能为 1；工具无法判断经济上正确的汇率方向，必须独立用反向等式验算。

`discounts` 五个键全部必填（不得从旧样例自动补值）：

```json
{"d_base": 0.10, "r_chip": 0.03, "r_v5": 0.05, "r_gov": 0.00, "r_terminal": 0.05}
```

以上同样只演示格式。每个折扣用 `[0,1)` 小数；工具不决定其合理性。`step_down` 为 `[0.05,0.10]`。priced 模式缺折扣是未完成研究参数论证，不能假借 cap 缺失直接留空；真正不可估时改 mode 并写具体原因。

冻结/否决/不可估时 `discounts` 和 `step_down` 必须 null，不继续生成进入价位，valuation 可 null。取消的 P2 永远没有数值；暂停 P2 保留参考价格但不得表述为有效执行档。

计算使用十进制、未舍入中间值；P1 每个情景乘五项折扣，P2 只用 P1 低档；最终 CNY 2 位、HKD 3 位。构建拒绝非有限数、布尔伪数值、重复键、错误币种和状态。build 验算算式与状态，check 只校验导出结构/数值范围/状态（最终没有折扣输入，不能完整重算）。报告中汇率桥、Terminal、现金桥与监控基线仍须独立复核。

## 验收后发布到本地

- 正式报告必须含本次模型输入的数值、单位、来源、假设和敏感性；不要求用户翻 scratch 才能复核价格。
- JSON 与报告同一版本、同一隔离后缀；报告 §0 记录数据包和两个框架的指纹及本次证据截止。新增来源、参数或证据状态变化都不能只凭旧文件存在而复用。
- 首次成功运行校验报告与 JSON 后复制到 `output/indexes/investment/<市场>-<代码>/investment-<代码>-latest.json`，内容保持完全相同；删除缓存后仍能通过 `research_paths.py latest-company` 找到日期产物。隔离版不更新 latest；升级须用户已有明确授权。v1 仅用于读取上期事实与变化，不自动转换其单位混杂或示例价位。
