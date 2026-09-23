---
name: etf-monthly-review
description: ETF 轨道月度流水线编排器：本地出快照 → 机械刷新全部现行卡的点位 → 列出到期/触发的复评队列并按需重写卡 → 变化检测（只有四类事实才改框架）→ 校验、导出 current.json、提交并开 PR。每月跑一次，先在本地跑、不上云端 Routine。Use when asked to run the monthly ETF pipeline end to end, or to refresh the ETF decision cards after a new snapshot.
---

# etf monthly review（月度流水线编排器）

节奏：每月第一个交易日之后跑一次；写卡与刷新只在本地（云端无 tushare 权限）。整条流水线的产物都在分支上，最后统一开 PR，不直接改 main。

## 输入

- `AS_OF_DATE`：缺省当天（北京时间）。
- `HOLDINGS`：用户本月的持仓金额（13 只工具）。没给就沿用上一版卡里的数并在报告里写明"持仓沿用 <日期>"。

## 步骤

### 0. 分支

`git checkout -b etf-monthly/<AS_OF_DATE>`（从 main）。主工作区若被写锁占用，按 memory 里的约定用 worktree。

### 1. 快照（本地，约 5 分钟）

```
/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --pool-csv /Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv
```

产物：`research/etf-<日期>-data-snapshot.txt`（末行须有「快照完成」）与 `research/etf-ladder-latest.json`。
§0 有接口异常时先重跑一次（东财/新浪接口间歇性断连）；仍失败的项记入本月报告的缺口清单，不猜数。

### 2. 机械刷新点位（代码，不动论点）

```
python3 scripts/etf_refresh_cards.py --dry-run     # 先看会改什么
python3 scripts/etf_refresh_cards.py               # 每张输入有变化的现行卡出新版 <card_id>-<日期>.md，supersedes 指向旧版
```

只改锚点及其 `decision.anchors.snapshot_ref`、valid_until、挂在锚点上的自动监控；卡的 `snapshot_ref`（论点数据）不动。正文只替换旧点位数字并加一行"机械刷新"注记。同一天已有版本的卡不刷新（脚本拒绝覆盖）。

### 3. 复评队列（AI 判断，只对进队列的卡重写）

进队列的四种情况，逐张列出并处理：

| 情况 | 判定依据 | 处理 |
|---|---|---|
| 到期 | 现行卡 `exit.latest_review_date` ≤ AS_OF_DATE + 30 天 | 用 `etf-card-research` 重写该席位的卡（论点、证据、反证、监控、失效条件全部重核） |
| 失效条件或监控触发 | 执行侧日报 / 用户告知 / 本月事实核对命中卡里的 `exit.invalidation` 或 manual 监控 | 同上；命中失效条件的卡按其 action 转 `reduce` / `close`，closed 卡写 `close_reason` |
| 进入减仓区或跌破买入锚点 | 快照 §6b 的当前状态分位 ≥ 75 或 ≤ 25（对应卡的 `reduce_above` / `buy_below` 已被穿越） | 重核论点后决定：维持阶梯动作、或改 status |
| 持仓变化 | `HOLDINGS` 显示某席位超上限、或新增/清出了工具 | 更新 instruments 的 role/action 与 sizing 说明；超上限 → 相关工具 `stop_dca` |
| 论点数据过旧 | 现行卡的 `snapshot_ref`（论点数据所用快照，机械刷新不动它）比 AS_OF_DATE 早 100 天以上 | 用 `etf-card-research` 重写，让论点重新对着当期快照 |

不在队列里的卡只做步骤 2 的机械刷新，不重写。

### 4. 变化检测（决定要不要动框架）

只有四类情况允许改 `framework/etf_framework.md`，其余一律不改（市场叙事、行情涨跌、板块轮动都不是理由）：

1. 结构性事实变了：指数编制规则修订、基金清盘/合并/费率变更、税费与 QDII 额度变化、平台规则变化。
2. 口径错了：快照或计算器发现算法缺陷（已修的写进本月报告，附修复前后数字）。
3. 记分卡证据：`research/etf-scorecard.md` 里累计关闭的战术卡达到 A12 的退出线，或某条 validated 规则在新一折数据上明显失效（须重跑 `scripts/etf_backtest.py` 并附报告）。
4. 上期挂账的观察项到期：上月报告"预备观察项"逐条复核，不许静默丢弃。

要改框架 → 走 A13 规则：改数字必须链接验证报告；改文字在变更记录里写明触发的是上面哪一类。改完运行 `framework-condense` 重生成 compact。

### 5. 校验、导出、提交

```
python3 scripts/validate_etf_card.py            # 全部卡零错误，含跨卡不变量
python3 scripts/validate_etf_card.py --export   # 更新 research/etf-cards/current.json
python3 -m unittest discover -s tests
```

提交：快照 + 副本 + 新版卡 + current.json + 本月报告 `research/etf-<日期>-monthly-review.md`（模板见下）。开 PR 到 main；合并后执行侧下一跑读到新卡。**不推送、不合并——由用户决定。**

### 本月报告模板

```markdown
# ETF 月度复评 <AS_OF_DATE>

## 1. 快照
- 文件、接口通/异常、缺口清单里与持仓相关的项

## 2. 点位刷新
- 逐卡：旧→新三锚点、valid_until；未刷新的卡与原因

## 3. 复评队列
- 逐卡：进队列的原因、处理结果（重写/转 reduce/转 close/维持）

## 4. 持仓与预算
- 各席位现持仓 vs 上限；行业合计 vs `etf_portfolio_params.json` 的行业块上限（现为 50 万）；中国权益 vs 90%（分母=全部资产）；已知敞口（A8）重述

## 5. 变化检测
- 四类触发逐条：命中/未命中；预备观察项（下月必复核）

## 6. 记分卡
- 本月关闭的卡及其相对基准的超额；累计
```

## 与其他 skill 的关系

- `etf-card-research`：写/重写单张卡。本编排器只在步骤 3 调用它。
- `framework-condense`：仅在步骤 4 改了框架后调用。
- 期货、个股两条轨道的周度流水线与本流水线互不干扰；本流水线不做宏观调研，需要当期宏观事实时读个股轨道最新的 `research/investment-*-market-research.md`。
