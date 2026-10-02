---
name: etf-review
description: ETF 主题双月评审（框架 v2.1）：按 framework/etf_framework.md 回答两个问题——未来两个月定投哪 2–3 个主题 ETF、每个持有主题的目标权重和处理（按实际账户管理），写成 research/etf-<日期>-review.md。只出研究结论，不给金额、点位、时点或分批计划。Use when asked to run the ETF theme review, pick theme ETFs for the next two months, or decide whether to adjust current theme ETF holdings.
---

# etf review

## 输入

- `AS_OF_DATE`：缺省当天（北京时间）。
- 持仓（可选）：用户给的一行——各主题市值、主题待配现金、ETF 账户总值（不含黄金）；个股、私募持仓可选。没给就只出名单。
- 自行读取：
  - `framework/etf_framework.md`；
  - `research/` 下最新的 `etf-*-data-snapshot.txt`；
  - 上一期评审报告。文件名严格为 `research/etf-YYYY-MM-DD-review.md`，日期后直接接 `-review.md`；`etf-2026-09-23-monthly-review.md` 这类 v0.1 月报不算。
  - 没有上期报告就是首期，改读 `research/etf-cards/v1-archive/`。

## 步骤

1. **检查快照**：末行有「快照完成」、距 `AS_OF_DATE` 不超过 10 天、头行为「ETF 框架 v2.0」且含 `H30184.CSI` 与 `931994.CSI`。否则停下，请用户本地运行：
   `/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --pool-csv /Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv`
2. **按框架 §3 做**：
   1. 核对上期失效条件，并记分；
   2. 8 个主题各填一行；
   3. 写深度要点：名单主题和拟新进主题要有 12 个月三情景；
   4. 定名单；
   5. 定每个持有主题的目标和处理，合格不够的部分记为待配现金；
   6. 算组合两项数：港股跨模块合计、压力情景损失。

   其中：
   - 当期事实先查原始资料，联网核实并标 [出处, 日期]；查不到写"未知"。
   - 有持仓时按实际账户算主题合计：高于目标时，给出各主题的目标、偏离和研究上的减持先后。
   - 名单上每个主题写一只定投工具（代码、份额）。多基金主题写清哪只与论点最贴，其余"只持有"或先减。
3. **写报告**：按框架 §6 模板写，第一屏就是本期结论。

不写金额、点位、时点、分批计划。不开 PR，由用户决定。
