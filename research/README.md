# 研究成果导航与输出契约

正式研究、必要证据及持续状态保存在本目录；缓存和中间文件保存在被 Git 忽略的 `output/`。目录按领域、对象、一期研究组织；程序使用 `scripts/research_paths.py`。以下路径均相对仓库根，日期采用 Asia/Shanghai，目录按需创建。

## 阅读入口

- 期货：[周更](futures/weekly/)、[快照](futures/snapshots/)、[维护](futures/maintenance/)、[基线](futures/baselines/)、[旧输出](futures/archive/)
- 股票：[周更](investment/weekly/)、[公司](investment/companies/)、[维护](investment/maintenance/)、[基线](investment/baselines/)
- ETF：[评审](etf/reviews/)、[快照](etf/snapshots/)、[专项研究](etf/studies/)、[维护](etf/maintenance/)、[历史方案](etf/archive/)
- [按日期生成的报告索引](INDEX.md)：只用于导航，正文的证据完整性、市场日期和版本才决定可用性。

## 当前任务输出

| 任务 | 正式位置（research 下） | 本地产物 |
|---|---|---|
| 期货周更及单阶段 | `futures/weekly/<日期>/<日期>-{market-research,change-decision,execution-audit,adaption-report}.md` | `output/runs/futures/<日期>/<run-id>/` |
| 股票周更及单阶段 | `investment/weekly/<日期>/investment-<日期>-{market-research,change-decision,adaption-report}.md` | `output/runs/investment/<日期>/<run-id>/` |
| 保真审计、脚本同步 | 随本期报告；必要附件放本期 `evidence/`；data-sync 和 compact 摘要仍写适配报告原章节 | `output/audits/<轨道>/<日期>/<run-id>/` |
| 独立修复、治理、核对 | `<轨道>/maintenance/<日期>/` | 本次运行目录 |
| 期货完整快照 | `futures/snapshots/<日期>-data-snapshot.txt` | `output/cache/futures/` |
| ETF 完整快照 | `etf/snapshots/etf-<日期>-data-snapshot.txt`；日期机器读数 `etf-<日期>-drawdown.json` | `output/cache/etf/` |
| ETF 双月评审 | `etf/reviews/<评审日>/etf-<评审日>-review.md` | `output/runs/etf/<日期>/<run-id>/` |
| ETF 预注册、验证 | `etf/studies/timing-validation/`；冻结原件不重写，重跑隔离为 `-r2/-r3` | ETF 缓存及运行目录 |
| ETF 候选池研究 | `etf/studies/theme-pool/` | 本次运行目录 |
| 个股研究及复评 | `investment/companies/<市场>-<代码>/<估值日>/investment-<代码>-<估值日>-{research.md,price-map.json}` | 沿用 `output/stock-research-<代码>-<日期>[-rN]/` |
| 独立深度研究 | 优先具体公司或行业；未指定归属时 `investment/studies/<slug>/<日期>/investment-deep-<日期>-<slug>.md` | `output/deep-research/<日期>-<slug>/` |

目录日期与原产物日期一致，不按迁移时间或文件修改时间重命名。同一期修订留在该期；隔离版报告和 JSON 保持成对的 `-r2/-r3…` 后缀，不能混成下一期或自动提升为正式最新。公司标识使用 SH/SZ/HK 与证券代码。

基线只放各轨 `baselines/`。普通旧报告留在原日期目录；`archive/` 仅存退出现行流程的类型，如 ETF 旧卡片、monthly-review、task-spec。旧 v1 卡片层级保留，不能据旧状态推定当前账户。历史审计 JSON 包含人工核对、豁免和原哈希，不能作为可重建日志批量删除。

## 通用技能映射

调用全局技能时先给定正式位置与临时目录，将工作流里的 `reports/`、默认 `outputs/` 映射到下表，`work/` 映射到 `output/`。不在仓库根另建平行产物树，不修改全局技能默认值。

| 技能 / 业务 | 归属（research 下） |
|---|---|
| investment-research、investment-team、earnings-review、management-deep-dive、news-pulse、单公司 checklist / quality-screen / dyp-ask | `investment/companies/<公司标识>/<日期>/`，不同业务使用不同文件名 |
| thesis-tracker | 公司目录的 `tracking/`；论文是持续状态，日期检查另存或追加 |
| industry-research、industry-funnel | `investment/industries/<行业>/<日期>/` |
| 多公司 checklist、quality-screen | `investment/screens/<日期>/<主题>/` |
| bottleneck-hunter | `investment/bottlenecks/<主题>/`；保留总地图、watchlist、日期扫描和 deep-dive 的关系 |
| portfolio-review | `investment/portfolios/<组合>/<日期>/`；原始账户资料另行本地保存，持续状态不视为缓存 |
| private-company-research | `investment/private-companies/<公司>/<日期>/` |
| deep-company-series、wechat-article、earnings-team 的文章 | `publications/<主题或公司>/<系列或日期>/`；配图放相邻 `assets/`，研究底稿链接公司研究 |
| financial-data、团队证据附件 | 所属报告的 `evidence/`；临时提取和机械扫描放 `output/` |
| 文档、表格、图表导出 | 正式交付跟随所属报告；原始下载与临时转换放 `output/` |

技能要求交付的研究底稿、分角色报告和评审记录不能仅因“子代理生成”就视为可丢弃缓存。独立深研笔记在本地保留；正式报告必须包含关键出处及论证，不依赖被忽略笔记才能复核结论。

## 程序发现与写入

从仓库根运行；路径模块以脚本位置定位根，兼容子目录和 worktree：

```sh
python3 scripts/research_paths.py path --track futures --kind execution-audit --as-of 2026-10-05
python3 scripts/research_paths.py list --track investment --kind market-research --as-of 2026-10-05 --before
python3 scripts/research_paths.py list --track futures --kind data-snapshot --as-of 2026-10-05 --committed
python3 scripts/research_paths.py latest-company --market HK --code 01952 --as-of 2026-10-05
python3 scripts/research_paths.py rebuild-indexes --as-of 2026-10-05
python3 scripts/research_paths.py index --as-of 2026-10-05
```

`list` 按日期升序，严格匹配轨道、类型和目录日期；默认不晚于截止日，`--before` 排除本期。`--committed` 要求路径与内容均和 HEAD 一致，暂存改动不算已提交。快照还核对头尾 AS_OF 与末行完整标记；ETF 的 v2.0 格式、10 天时效、指数覆盖和各市场锚仍由 etf-review 验收，路径检查不能替代业务验收。原框架审计与拟议重评按周更契约保留来源，不让归档和隔离副本进入影子账本扫描。

期货与 ETF 取数默认拒绝覆盖同日快照。失败保留 `.partial`，旧正式文件不变；成功后才原子发布。`--no-snapshot` 不写正式快照及 latest。完整快照与必要日期 JSON 应提交；CSV 缓存、机械扫描、partial 和可重建索引不提交。

`output/indexes/` 的个股 latest 与 ETF latest 是可重建缓存；个股发现从日期报告/JSON 配对开始，旧 v1 只作历史输入，不升级其结论。隔离版须明确授权提升；提升时更新正式配对并保留被替代版本。thesis、watchlist、组合维护文件等含独有状态的文件不适用“latest 可忽略”规则。

新审计可将机械明细放 `output/audits/`，正式记录须保留人工核对、豁免理由、缺项、输入版本/哈希、生成命令和限制。未建立可复现生成器前不能删除旧证据。

## 迁移与运行边界

[逐文件迁移清单](../docs/research-layout-migration.json)记录旧新路径、迁移前跟踪状态及前后哈希。冻结 ETF 预注册保留原文与原提交；文内旧输出路径是当时契约，由本文件映射到现行目录，不能用迁移提交冒充预注册提交。审计 JSON 的历史正文与来源哈希同样保留。

本地备份位于被忽略的 `output/layout-migration/2026-10-05/`。迁移本身不授权 commit/push/PR。两个周更自动化通过根 AGENTS 和 skill 读取本契约；远端基线需包含完整迁移才能使用新规则，未提交新路径不能冒充已提交证据。
