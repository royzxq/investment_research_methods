# 研究成果导航与输出契约

正式研究、必要证据及持续状态保存在本目录；缓存和中间文件保存在被 Git 忽略的 `output/`。公司研究按日期优先组织，打开一天即可查看当天研究的公司；程序使用 `scripts/research_paths.py`。以下路径均相对仓库根，日期采用 Asia/Shanghai，目录按需创建。公司研究目录目前整体被 Git 忽略，只在本地保留，正式交付不等于自动入库。

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
| 个股研究及复评 | `investment/companies/<估值日>/<市场>-<代码>/investment-<代码>-<估值日>-{research,price-map}-<生成端>.{md,json}` | `output/stock-research-<市场>-<代码>-<日期>-<生成端>[-rN]/` |
| 独立深度研究 | 优先具体公司或行业；未指定归属时 `investment/studies/<slug>/<日期>/investment-deep-<日期>-<slug>.md` | `output/deep-research/<日期>-<slug>/` |

目录日期与原产物日期一致，不按迁移时间或文件修改时间重命名。同一期修订留在该期；隔离版报告和 JSON 保持成对的 `-r2/-r3…` 后缀，不能混成下一期或自动提升为正式最新。公司标识使用 SH/SZ/HK 与证券代码。

公司研究示例：`investment/companies/2026-10-06/SH-601919/`。同一天不同公司并列，同一公司不同日期分别归档；附件跟随当期公司目录。报告索引按日期倒序列出公司名称、代码及报告/价格地图链接；跨日期复评继续由 `latest-company` 查找。

个股新产物按实际生成端区分：Codex 为 `codex`，Claude Code 为 `claude`。例如同一公司同日分别生成 `investment-601919-2026-10-06-price-map-codex.json` 与 `investment-601919-2026-10-06-price-map-claude.json`，报告对应 `-research-codex.md` / `-research-claude.md`；JSON 的 `meta.generator` 同步标注。同端重复运行追加 `-r2/-r3`（如 `-price-map-codex-r2.json`），不同端互不占用版本号；附件使用本期公司目录内的 `evidence/<生成端>/`。

历史无生成端后缀、无 generator 字段的产物继续原样保留，视为“来源未标注”，不自动归类为 Claude。`latest-company --generator codex|claude` 只查本端，缺少结果不会回退到另一端；省略参数或使用 `--generator unattributed` 只查无来源历史。跨端报告可明确作为研究材料引用，不能冒充本端结果。latest 分别为 `output/indexes/investment/<市场>-<代码>/investment-<代码>-latest-codex.json` 和 `-latest-claude.json`；旧无后缀缓存只对应未标注来源的历史。

基线只放各轨 `baselines/`。普通旧报告留在原日期目录；`archive/` 仅存退出现行流程的类型，如 ETF 旧卡片、monthly-review、task-spec。旧 v1 卡片层级保留，不能据旧状态推定当前账户。历史审计 JSON 包含人工核对、豁免和原哈希，不能作为可重建日志批量删除。

## 通用技能映射

调用全局技能时先给定正式位置与临时目录，将工作流里的 `reports/`、默认 `outputs/` 映射到下表，`work/` 映射到 `output/`。不在仓库根另建平行产物树，不修改全局技能默认值。

| 技能 / 业务 | 归属（research 下） |
|---|---|
| investment-research、investment-team、earnings-review、management-deep-dive、news-pulse、单公司 checklist / quality-screen / dyp-ask | `investment/companies/<日期>/<公司标识>/`，不同业务使用不同文件名 |
| thesis-tracker | `investment/tracking/<公司标识>/`；投资逻辑是持续状态，日期检查另存或追加，不随某一期报告复制 |
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
python3 scripts/research_paths.py company-path --market HK --code 01952 --as-of 2026-10-06 --kind price-map --generator codex
python3 scripts/research_paths.py latest-company --market HK --code 01952 --as-of 2026-10-06 --generator codex
python3 scripts/research_paths.py latest-company --market HK --code 01952 --as-of 2026-10-05 --include-legacy
python3 scripts/research_paths.py rebuild-indexes --as-of 2026-10-05
python3 scripts/research_paths.py index --as-of 2026-10-05
```

`list` 按日期升序，严格匹配轨道、类型和目录日期；默认不晚于截止日，`--before` 排除本期。`--committed` 要求路径与内容均和 HEAD 一致，暂存改动不算已提交。快照还核对头尾 AS_OF 与末行完整标记；ETF 的 v2.0 格式、10 天时效、指数覆盖和各市场锚仍由 etf-review 验收，路径检查不能替代业务验收。原框架审计与拟议重评按周更契约保留来源，不让归档和隔离副本进入影子账本扫描。

期货与 ETF 取数默认拒绝覆盖同日快照。失败保留 `.partial`，旧正式文件不变；成功后才原子发布。`--no-snapshot` 不写正式快照及 latest。完整快照与必要日期 JSON 应提交；CSV 缓存、机械扫描、partial 和可重建索引不提交。

`output/indexes/` 的个股 latest 与 ETF latest 是可重建缓存。`latest-company` 默认只选截止日内最近合格的正式 v2 配对；`--include-legacy` 用于另查旧 v1 历史研究，不能将其作为当前价格地图。个股缓存按生成端分别重建且仅使用 v2，无合格配对则清除该公司该生成端的旧缓存；选择按估值日而非修改时间或价格是否非空，较新的冻结/不可估 v2 不能被旧的有价结果替代。较晚日期 v1 与较早日期 v2 并存时命令提示日期差异，不把较早估值升级到请求日期；报告索引保留并标注 v1 历史研究。隔离版须明确授权提升；提升时更新正式配对并保留被替代版本。thesis、watchlist、组合维护文件等含独有状态的文件不适用“latest 可忽略”规则。

新审计可将机械明细放 `output/audits/`，正式记录须保留人工核对、豁免理由、缺项、输入版本/哈希、生成命令和限制。未建立可复现生成器前不能删除旧证据。

## 个股复研批次交接验收

`ai_investment` 发布本轮 `stock-research-request/v1` 请求与量价数据包，本仓使用真实生成端 `codex/claude` 研究；独立 `stock-research-result/v1` 清单绑定请求原始字节哈希及确切报告/JSON 路径。Codex 接替原 Gemini 业务席位，历史 Gemini 不改身份。只消费本轮结果，不使用七天窗口补历史来源；部分端尚无回执即缺席，不能记成拒绝或失败。单端成功可进入后续单席计算并披露。

以下 research_exchange 入口只做验收，不启动模型或调度、不更新 CSV/latest，不判断事实真实性或估值合理性：

```sh
python3 scripts/research_exchange.py check-request /path/to/request.json
python3 scripts/research_exchange.py check-results /path/to/result.json --request /path/to/request.json --artifact-root .
```

请求数据包路径相对请求所在目录，结果报告/JSON 路径相对 `--artifact-root`；均须根内、非空且 SHA-256 匹配。拒绝绝对路径、父目录穿越、逃出根的符号链接、重复 JSON 键和非有限数。请求估值日不得晚于请求创建时刻的北京时间日期；不依赖验收当天，可重放历史。

成功回执只接受日期优先目录内同生成端、同修订后缀的正式 v2 报告/JSON 配对，验证证券身份、名称、估值日、真实 `meta.generator`、`meta.report_path`、九节可见且非空的报告及时间顺序；HTML 注释和代码块内的标题不计章节。冻结/否决/不可估仍可以是成功研究交付，结构验收不增加执行许可。`-rN` 可作为本轮精确交付读取，不因此提升 latest。失败回执必须有理由且产物为 null；任务/端重复、错批次、错请求哈希或跨端配对均拒绝。

## 个股研究 CLI 执行（2026-10-07）

`scripts/research_runner.py` 在本仓准备并执行已验收请求，复用 stock-research 技能。必须使用请求中已计划的真实生成端；不要只给股票代码就启动研究。

```sh
python3 scripts/research_runner.py prepare --request /absolute/path/to/request.json
python3 scripts/research_runner.py run --request /absolute/path/to/request.json --generator claude --workers 3
python3 scripts/research_runner.py run --request /absolute/path/to/request.json --generator codex --workers 1
```

默认使用 PATH 中对应 CLI 和它已有的模型配置；可用 `--cli /absolute/path/to/cli` 指定安装位置。运行需要实际登录/网络，使用正常自动审批；拒绝权限或模型失败会留失败回执，不跳过权限检查。`--timeout-seconds` 默认3600，超时终止本次进程组。该入口不安装定时任务、不写飞书/CSV、不提交Git，也不更新 INDEX/latest；自动扫描、预算和失败自动恢复仍未接入。

准备前校验请求及包，要求上游发布器标准 `packs/<task_id>.md` 路径和匹配证券的量价包标题；包内财务缺口可以进入研究补证。原始请求和包字节复制到 `output/runs/investment/<估值日>/<batch_id>/`，请求文件最后发布。每项 `execution/<task_id>/<generator>/prompt.txt` 直接包含完整包正文、触发元数据、框架指纹及确切配对目标；`input.json` 记录请求/包/提示词哈希、标准输入字节数和目标，`targets.json` 保存准备时在证券锁内选出的空闲版本。启动前重验全部准备材料；标准输入直接使用校验返回的冻结字节，验收使用同一份框架指纹，研究期间框架变化单独记录。不能在交付时再次构造输入或换用后来更新的指纹。

`process.json` 的 PID/状态证明实际进程启动，`events.jsonl`/`stderr.log` 保存执行原文；`cli-receipt.json` 是模型回执，不能代替正式价格JSON。正式产物仍位于日期优先公司目录；同日同端已有文件写配对隔离版本。模型只写本批 staged/<task_id>/<generator>/ 内的同结构暂存文件，JSON meta.report_path和回执使用确切最终相对路径；runner先读全并验证两份暂存字节，再复制成独立inode、以只创建的原子链接发布，拒绝覆盖旧文件。完成回执reason必须null、结论写summary；失败则reason有说明、两个路径null。报告第0节正文须绑定本批ID、包与框架指纹；输入匹配且原九节/v2/配对验收通过才产生完成回执，不能把连接成功、文件准备或退出码0等同于完整研究交付。

每端生成独立 `results-claude.json` / `results-codex.json`，使用原 `stock-research-result/v1` 协议，不相互覆盖；缺席生成端不记失败。任务失败会留原因和 null 产物，同一批次同任务同端拒绝再次启动；修复后显式发布新批次重试，保留旧尝试。跨批同证券同端使用进程锁，执行前再次检查准备时目标未被占用。超时与SIGTERM/SIGINT统一清理进程组（含忽略SIGTERM的同组后代），清理完成后才释放证券锁；SIGKILL、断电或刻意脱离组的守护进程不作恢复保证。部分准备目录没有 request.json 则不可执行，不自动修补或覆盖。

## 迁移与运行边界

[逐文件迁移清单](../docs/research-layout-migration.json)记录旧新路径、迁移前跟踪状态及前后哈希。冻结 ETF 预注册保留原文与原提交；文内旧输出路径是当时契约，由本文件映射到现行目录，不能用迁移提交冒充预注册提交。审计 JSON 的历史正文与来源哈希同样保留。

2026-10-06 公司目录改为日期优先：旧 `investment/companies/<公司标识>/<日期>/` 对应现行 `investment/companies/<日期>/<公司标识>/`。旧迁移清单与报告中的历史运行叙述保留当时路径；当前 JSON 的 `meta.report_path` 与导航使用新路径。本次本地迁移备份及逐文件校验记录位于 `output/layout-migration/2026-10-06-company-date-first/`。

本地备份位于被忽略的 `output/layout-migration/2026-10-05/`。迁移本身不授权 commit/push/PR。两个周更自动化通过根 AGENTS 和 skill 读取本契约；远端基线需包含完整迁移才能使用新规则，未提交新路径不能冒充已提交证据。
