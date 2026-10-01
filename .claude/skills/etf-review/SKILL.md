---
name: etf-review
description: ETF 主题双月评审（框架 v2.0）：按 framework/etf_framework.md 回答两个问题——未来两个月定投哪 2–3 个主题 ETF、现有主题持仓怎么处理，写成 research/etf-<日期>-review.md。只出研究结论，不给金额、点位或时点。Use when asked to run the ETF theme review, pick theme ETFs for the next two months, or decide whether to adjust current theme ETF holdings.
---

# etf review

## 输入

- `AS_OF_DATE`：缺省当天（北京时间）。
- 持仓（可选）：用户给的一行各主题市值与 ETF 账户总值（不含黄金）。没给就只出名单。
- 自行读取：`framework/etf_framework.md`、`research/` 下最新的 `etf-*-data-snapshot.txt`、上一期 `research/etf-*-review.md`（首期读 `research/etf-cards/v1-archive/`）。

## 步骤

1. 快照末行有「快照完成」且距 `AS_OF_DATE` 不超过 10 天；否则停下，请用户本地运行
   `/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --pool-csv /Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv`。
2. 按框架 §3 做：核对上期失效条件 → 8 个主题各填一行 → 只给有变化 / 拟新进 / 拟退出的主题写要点 → 定名单 → 定现有持仓处理。
   当期事实联网核实并标 [出处, 日期]；查不到写"未知"。有持仓时先算主题实际合计，超过 30% 就写"主题定投暂停"。
3. 按框架 §6 模板写报告，第一屏就是本期结论。

不写金额、点位、时点、分批计划；不提交、不开 PR，由用户决定。
