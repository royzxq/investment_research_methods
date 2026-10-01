---
name: etf-monthly-review
description: ETF 轨道月度编排器（框架 v1.1）：本地出快照 → 到了评审月份就调用 etf-review 出调研报告 → 变化检测（只有五类事实才改框架）→ 提交并开 PR。只维护调研框架与研究结论，不涉及交易。每月跑一次，先在本地跑、不上云端 Routine。Use when asked to run the monthly ETF pipeline end to end.
---

# etf monthly review（月度编排器）

节奏：每月一次；出快照只在本地（云端无 tushare 权限）。产物在分支上，最后统一开 PR，不直接改 main。

## 步骤

1. **分支**：`git checkout -b etf-monthly/<AS_OF_DATE>`（从 main）。
2. **快照**（本地，约 5 分钟）：
   `/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --pool-csv /Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv`
   产物 `research/etf-<日期>-data-snapshot.txt`（末行须有「快照完成」）；§0 接口异常先重跑一次，仍失败的记入缺口，不猜数。
3. **本月要不要出报告**（框架 §7）：1、3、7 月 → `etf-review` `light`；5、9、11 月 → `full`；3、6、9、12 月末另做 `quarterly`（与双月评审同月就合并成一份）；
   6、12 月加半年复核内容，12 月加年度评估。其余月份只留快照。用户给了持仓就一并传给 `etf-review`。
4. **变化检测**：只有五类情况允许改 `framework/etf_framework.md`——结构性事实变了（编制规则、产品、税费、额度）、口径错了（附修复前后数字）、
   年度评估给出证据、上期挂账的观察项到期（逐条复核，不许静默丢弃）、用户改组合基准（写明日期与理由）。市场叙事、涨跌、板块轮动都不是理由。改了就在变更记录里写明属于哪一类。
5. **检查与提交**：`python3 -m unittest tests.test_etf_calc tests.test_etf_backtest`；提交快照、报告与框架改动，开 PR 到 main。**不推送、不合并——由用户决定。**
