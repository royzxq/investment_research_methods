# 研究成果导航与输出契约

正式研究、必要证据及持续状态保存在本目录；缓存和中间文件保存在被 Git 忽略的 `output/`。公司研究按日期优先组织，打开一天即可查看当天研究的公司；程序使用 `scripts/research_paths.py`。以下路径均相对仓库根，日期采用 Asia/Shanghai，目录按需创建。公司研究目录目前整体被 Git 忽略，只在本地保留，正式交付不等于自动入库。

## 阅读入口

- 期货：[周更](futures/weekly/)、轻量刷新（`futures/refresh/`）、[快照](futures/snapshots/)、[维护](futures/maintenance/)、[基线](futures/baselines/)、[旧输出](futures/archive/)
- 股票：[周更](investment/weekly/)、[公司](investment/companies/)、[维护](investment/maintenance/)、[基线](investment/baselines/)
- ETF：[评审](etf/reviews/)、[快照](etf/snapshots/)、[专项研究](etf/studies/)、[维护](etf/maintenance/)、[历史方案](etf/archive/)
- [按日期生成的共享报告索引](INDEX.md)：不链接仅本地保存的公司产物；公司导航使用 `index --local` 生成到 `output/indexes/INDEX.md`。索引只用于导航，正文的证据完整性、市场日期和版本才决定可用性。新克隆不会包含公司产物，`latest-company` 无结果属于正常情况，不应以共享索引暗示这些报告已入库。

## 当前任务输出

| 任务 | 正式位置（research 下） | 本地产物 |
|---|---|---|
| 期货周更及单阶段 | `futures/weekly/<日期>/<日期>-{market-research,change-decision,execution-audit,adaption-report}.md` | `output/runs/futures/<日期>/<run-id>/` |
| 期货已采纳版本接续 | `futures/weekly/<日期>/<日期>-handoff.json`；旧采纳记录保留在同日 `evidence/handoff-history/` | 接续含独有选择与纠错范围，非可丢弃缓存 |
| 期货轻量行情刷新 | `futures/refresh/<日期>/<日期>-signal-refresh[-rN].{md,json}`，原料在同日 `evidence/` | 隔离取数工作目录 `output/futures-refresh-fetch/` |
| 期货 V 观察锚 | `futures/anchors/<日期>/<日期>-anchors[-rN].json`；来源计算留同日 evidence/研究报告，冻结及撤回不可变 | 共享接续后仍需核本期适用性 |
| 期货跨 worktree 本地接续 | 主 checkout 的 `futures/local-continuity/`：内容寻址来源副本、采纳索引 | Git 忽略的持续状态，非缓存；`scripts/futures_continuity.py location` 定位，不能仅留 memory |
| 股票周更及单阶段 | `investment/weekly/<日期>/investment-<日期>-{market-research,change-decision,adaption-report}[-rN].md` | `output/runs/investment/<日期>/<run-id>/` |
| 股票状态、纠错及方法接续 | `investment/weekly/<日期>/investment-<日期>-handoff[-rN].json`；方法正文快照及必要来源放同日 `evidence/` | 采纳、替代和待复评凭证是持续研究记录，不是可丢弃缓存 |
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

个股新产物按实际生成端区分：Codex 为 `codex`，Claude Code 为 `claude`，DeepSeek Harness 为 `dsh`。例如同一公司同日分别生成 `investment-601919-2026-10-06-price-map-codex.json` 与 `investment-601919-2026-10-06-price-map-claude.json`，报告对应 `-research-codex.md` / `-research-claude.md`；JSON 的 `meta.generator` 同步标注。同端重复运行追加 `-r2/-r3`（如 `-price-map-codex-r2.json`），不同端互不占用版本号；附件使用本期公司目录内的 `evidence/<生成端>/`。

历史无生成端后缀、无 generator 字段的产物继续原样保留，视为“来源未标注”，不自动归类为 Claude。`latest-company --generator codex|claude|dsh` 只查本端，缺少结果不会回退到另一端；省略参数或使用 `--generator unattributed` 只查无来源历史。跨端报告可明确作为研究材料引用，不能冒充本端结果。latest 分别为 `output/indexes/investment/<市场>-<代码>/investment-<代码>-latest-codex.json` 、`-latest-claude.json` 和 `-latest-dsh.json`；旧无后缀缓存只对应未标注来源的历史。

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
python3 scripts/research_paths.py index --as-of 2026-10-05 --local
```

`list` 按日期升序，严格匹配轨道、类型和目录日期；默认不晚于截止日，`--before` 排除本期。`--committed` 要求路径与内容均和 HEAD 一致，暂存改动不算已提交。快照还核对头尾 AS_OF 与末行完整标记；ETF 的 v2.0 格式、10 天时效、指数覆盖和各市场锚仍由 etf-review 验收，路径检查不能替代业务验收。原框架审计与拟议重评按周更契约保留来源，不让归档和隔离副本进入影子账本扫描。

期货跨期优先使用 `scripts/futures_handoff.py resolve` 的明确采纳记录：保存确切报告路径、哈希、方法身份和纠错替代范围，允许显式采纳 `-rN`，不改写原始报告。`research_paths.py list` 对handoff/refresh仍只枚举严格正式名，不代表版本已验收。handoff默认只创建；明确更改采纳时用 `register --replace` 保留旧manifest并核原件未被篡改。published消费要求最新采纳记录及引用在HEAD中一致，不因它尚未提交就静默使用更旧结论。方法不兼容仅可显式作为历史事实，不继承执行状态。尚无handoff的历史期才使用原严格发现与基线回退。

轻量刷新只使用现行T/V工具生成价格筛查和原计划有效期检查，不自动完成产业、执行或账户判断。输出MD/JSON与冻结原料一并保存；同日重跑写新修订，失败不覆盖旧成功产物、不将过期信号延期。`--fetch`须有本次用户或自动化已有取数授权，使用环境文档解释器；隔离取数结果经完整性验收即可用于本次本地研究，获授权发布时连同必要原料纳入本期日志，提交后才能成为无人值守的历史交接证据。状态刷新、证据纠错、方法变更的唯一编排定义见期货skill，轻量输出不冒充schema 3完整执行审计。

股票周更用 `scripts/investment_maintenance.py` 区分状态刷新、证据纠错、方法变更。发现报告不代表采纳，`update_needed` 兼容字段只表达方法是否需要修改；无方法修改也可形成新的状态/纠错交接。同日新增证据写整个更新包的配套 `-rN`，明确采纳、替代及受影响结论，不覆盖旧日志。已采纳交接绑定确切方法正文与报告哈希；未合并提案只作研究线索。研究日志和状态交接按既有 publish 授权发布，框架正文及方法修改仍统一 PR，状态消费不等待该 PR。首次接续历史报告须明确证据截止与采用依据，不凭文件名或旧报告的“已执行”声明补造完成事实。

股票方法指纹仅排除通过严格结构验证的原位观测块；阈值、动作及混排 D 段仍在方法比较范围。正文任何其他变化需要明确兼容核对，不以相同版本标签证明规则相同。个股以估值截止内、方法兼容的已采纳交接刷新判断；没有交接时仍可按现行已采纳方法定向补证，不新增等待周更的门槛。触发、待复评、完成分别记录，完成需对应报告凭证；研究完成不等于账户执行。

期货与 ETF 取数默认拒绝覆盖同日快照。失败保留 `.partial`，旧正式文件不变；成功后才原子发布。`--no-snapshot` 不写正式快照及 latest。完整快照与必要日期 JSON 应提交；CSV 缓存、机械扫描、partial 和可重建索引不提交。

`output/indexes/` 的个股 latest 与 ETF latest 是可重建缓存。`latest-company` 默认只选截止日内最近合格的正式 v4/v3/v2 配对；`--include-legacy` 用于另查旧 v1 历史研究，不能将其作为当前价格地图。个股缓存按生成端分别重建且仅使用 v4/v3/v2，无合格配对则清除该公司该生成端的旧缓存；选择按估值日而非修改时间或价格是否非空，较新的冻结/不可估 v4/v3/v2 不能被旧的有价结果替代。较晚日期 v1 与较早日期 v4/v3/v2 并存时命令提示日期差异，不把较早估值升级到请求日期；报告索引保留并标注 v1 历史研究。隔离版须明确授权提升；提升时更新正式配对并保留被替代版本。thesis、watchlist、组合维护文件等含独有状态的文件不适用“latest 可忽略”规则。

新审计可将机械明细放 `output/audits/`，正式记录须保留人工核对、豁免理由、缺项、输入版本/哈希、生成命令和限制。未建立可复现生成器前不能删除旧证据。

## 个股复研批次交接验收

`ai_investment` 新发布默认使用 `stock-research-request/v2` 与真实 `codex/dsh`；结果为 `stock-research-result/v2`，封口为 `research-sealed/v2`。v1 继续严格支持历史 `codex/claude`，结果/封口跟随绑定请求版本，字段与哈希/路径校验不变。Codex 接替原 Gemini 业务席位，DSH 接替原 Claude 业务席位；同批 Claude/DSH 互斥，仍为两个基础席位。历史不改身份，DSH 首份同端基线为 null，旧未解除控制由下游原稳定ID/scope接续。独立结果清单绑定请求原始字节哈希及确切报告/JSON 路径。只消费本轮结果，不使用七天窗口补历史来源；部分端尚无回执即缺席，不能记成拒绝或失败。单端成功可进入后续单席计算并披露。

以下 research_exchange 入口只做验收，不启动模型或调度、不更新 CSV/latest，不判断事实真实性或估值合理性：

```sh
python3 scripts/research_exchange.py check-request /path/to/request.json
python3 scripts/research_exchange.py check-results /path/to/result.json --request /path/to/request.json --artifact-root .
```

请求数据包路径相对请求所在目录，结果报告/JSON 路径相对 `--artifact-root`；均须根内、非空且 SHA-256 匹配。拒绝绝对路径、父目录穿越、逃出根的符号链接、重复 JSON 键和非有限数。请求估值日不得晚于请求创建时刻的北京时间日期；不依赖验收当天，可重放历史。

成功回执只接受日期优先目录内同生成端、同修订后缀的正式 v4/v3/v2 报告/JSON 配对，验证证券身份、名称、估值日、真实 `meta.generator`、`meta.report_path`、九节可见且非空的报告及时间顺序；HTML 注释和代码块内的标题不计章节。冻结/否决/不可估仍可以是成功研究交付，结构验收不增加执行许可。`-rN` 可作为本轮精确交付读取，不因此提升 latest。失败回执必须有理由且产物为 null；任务/端重复、错批次、错请求哈希或跨端配对均拒绝。

## 个股研究 CLI 执行（2026-10-07）

`scripts/research_runner.py` 在本仓准备并执行已验收请求，复用 stock-research 技能。必须使用请求中已计划的真实生成端；不要只给股票代码就启动研究。

```sh
python3 scripts/research_runner.py prepare --request /absolute/path/to/request.json --runtime-config /absolute/path/to/research_runtime.production.json
python3 scripts/research_runner.py run --request /absolute/path/to/request.json --generator dsh --runtime-config /absolute/path/to/research_runtime.production.json --workers 3
python3 scripts/research_runner.py run --request /absolute/path/to/request.json --generator codex --workers 1
```

默认使用 PATH 中对应 CLI；可用 `--cli /absolute/path/to/cli` 指定安装位置。Codex/CC未显式选模型时继承既有配置，DSH使用显式模型配置与workspace-write/approval never，无需人工确认，不宣称与CC自动审批审查等价。运行需要实际凭据/网络；拒绝权限或模型失败会留失败回执，不跳过适配器的沙箱检查。`--timeout-seconds` 默认3600，超时终止本次进程组。该入口不安装定时任务、不写飞书/CSV、不提交Git，也不更新 INDEX/latest；自动扫描、预算和失败恢复由 `research_scheduler.py` 管理。

2026-10-21 执行层已抽取 profile 与 harness adapter；不提供配置仍使用legacy Codex/CC默认。可给 prepare/run 或 scheduler 显式 `--runtime-config /absolute/runtime.json`，按[示例](../config/research_runtime.example.json)选择已有适配器支持的主模型/effort及子模型。新批次在 `framework-snapshot/execution-plan.json` 冻结完整选中配置并绑定原请求；已有批次按自己的计划或旧合同恢复，不受当前配置变化影响。2026-10-23起DSH已正式接入，新v2请求须选择含DSH的显式配置，例如[生产配置](../config/research_runtime.production.json)；旧v1/CC计划及原业务席位、共识与Coze规则保留。能力与继承语义见[执行配置ADR](../docs/adr/ADR-20261021-research-runtime-profiles.md)与[DSH迁移ADR](../docs/adr/ADR-20261023-dsh-research-seat-migration.md)。

Jev 默认 `auto`，Codex/Claude/DSH 均注册可审计的 `jev_research` 路由。可用 `run --jev-mode auto|off|force` 指定，或设置 `RESEARCH_JEV_MODE`（定时调度入口也继承该环境变量）；命令行优先，重试保留首次模式。批量公告/年报候选提交后由程序判断是否达到阈值，已精确定位及小批次记录跳过原因；全部候选保留，失败回退原文核验。触发参数和候选格式见 [Jev 条件路由](../.agents/skills/stock-research/references/jev-routing.md)。每端每次尝试在 `execution/<task_id>/<generator>/jev/` 留 `calls.jsonl`、排序结果和最终 `summary.json`，摘要同时进入 `process.json.jev`；retry-1 使用自己的目录。`not_requested` 表示没有提交候选，不能当作程序已评估后跳过。

Codex 运行要求 CLI 支持顶层 `--no-daemon` 和 `exec --approve-for-me`，以及结构化输出、临时会话等执行参数；本机已核验 `codex-cli 0.160.1`。旧版（例如审查环境的 `0.144.0-alpha.4`）不满足此能力契约，不能直接使用。runner 在领取任务前读取两级 `--help` 检查能力；不兼容、检查失败或超时即拒绝启动，不生成任务失败回执、不消耗本批次启动机会，可通过 `--cli` 选择兼容版本后重试。保留自动审批及独立进程清理语义，不自动降级为跳过权限检查。能力检查及命令解析通过不等于模型登录、联网研究或交付验收通过。

准备前校验请求及包，要求上游发布器标准 `packs/<task_id>.md` 路径和匹配证券的量价包标题；包内财务缺口可以进入研究补证。原始请求、包和两份框架实际正文复制到 `output/runs/investment/<估值日>/<batch_id>/`，框架与可用的已采纳状态交接及其来源保存在 `framework-snapshot/`，请求文件最后发布。每项 prompt 明确主、子研究读取这些冻结材料，不能在执行途中换读工作区最新框架；`input.json` 记录请求/包/提示词及框架哈希，`targets.json` 保存准备时在证券锁内选出的空闲版本。启动和发布前校验冻结材料，不能只要求报告抄写哈希。

发布前核对工作区与冻结方法：精确相同、仅受限观测块变化，或已有明确采纳且绑定双方方法的兼容审查时可正常交付，仍说明状态日期；同时核对冻结来源是否已被明确撤回。其余变化先记兼容性待复评，已完成研究保留为至少 `-r2` 的隔离配对，不冒充当前方法下的正式最新，也不因变化重跑整个批次。由于精确批次结果也可消费隔离版本，派生 JSON 的有价模式改为 frozen；v4阻断entry/add并保留holding风险，旧v3按其冻结协议暂停P2，原始研究与模型回执保留；不能只加一句文字警告却保留机器可读买入资格。旧 prepared 请求只有在工作区正文仍与其原指纹精确一致时才可保留旧材料并迁移出快照；原提示词按冻结的 pre-snapshot v2 模板逐字节核验，不随新版交付模板变化，原记录保持不变，运行提示词另存。无法恢复旧正文或提示词不匹配时报告缺口，要求新建批次，不伪造输入。已完成历史结果仍可按原协议读取，无需追溯重跑。

`process.json` 的 PID/状态证明实际进程启动，`events.jsonl`/`stderr.log` 保存执行原文；`cli-receipt.json` 是模型回执，不能代替正式价格JSON。正式产物仍位于日期优先公司目录；同日同端已有文件写配对隔离版本。模型只写本批 staged/<task_id>/<generator>/ 内的同结构暂存文件，JSON meta.report_path和回执使用确切最终相对路径；runner先读全并验证两份暂存字节，再复制成独立inode、以只创建的原子链接发布，拒绝覆盖旧文件。完成回执reason必须null、结论写summary；失败则reason有说明、两个路径null。报告第0节正文须绑定本批ID、包与框架指纹；输入匹配且九节/该批次冻结交付版本/配对验收通过才产生完成回执，不能把连接成功、文件准备或退出码0等同于完整研究交付。

每端生成独立 `results-<generator>.json`，使用与本轮请求绑定的 `stock-research-result/v1|v2` 协议，不相互覆盖；缺席生成端不记失败。任务失败会留原因和 null 产物，同一批次同任务同端拒绝再次启动；修复后显式发布新批次重试，保留旧尝试。跨批同证券同端使用进程锁，执行前再次检查准备时目标未被占用。超时与SIGTERM/SIGINT统一清理进程组（含忽略SIGTERM的同组后代），清理完成后才释放证券锁；SIGKILL、断电或刻意脱离组的守护进程不作恢复保证。部分准备目录没有 request.json 则不可执行，不自动修补或覆盖。

### 两价正式交付（2026-10-18，已本地采纳）

本工作区普通新交付使用`stock-research/v4`：`meta/price_map/research_controls/monitoring`四顶层，price_map仅`mode/reason/v50/p1/t1`；P1显式单价或原报告实际区间，T1仅价格表达式，无P2/T2占位。报告保留全部加仓、逻辑失效、复评/减仓与退出条件，重点monitoring仍1–10项，不截断完整条件；entry/add/holding摘要与audit-v2按稳定ID/scope一致。V50换算、P1原估值式、首笔/预留60/40及已有自动个股研究七天冷却期保留。新批次正式使用本协议，完成验收后更新本端latest并交原定时下游消费；不批量重写旧历史，调度节奏不变。

新批次冻结delivery_contract、prompt_template及`research_validation=stock-research-audit/v2`，继续冻结本端折扣基线。审计保留收入/利润/PE/股本桥、风险唯一归属、参数变化依据和P1算式，升级constraints的scope/action与按scope精确覆盖的release_all_of。only-add阻断不冻结entry；全局freeze/reject/unavailable同时限制entry+add；holding失效/退出阻断新增但不屏蔽卖出。clear必须有解除证据，来源缺席/遗漏/unknown不解除。具体见[输出契约](../.agents/skills/stock-research/references/valuation-and-output.md)与[研究一致性](../.agents/skills/stock-research/references/research-consistency.md)。

旧v3/v2原文、封口及audit-v1保持可读；格式版本不越过更晚估值日期。旧prepared仅按其原冻结合同恢复，运行器附加[旧v3输出](../.agents/skills/stock-research/references/legacy-v3-output.md)/[旧audit-v1](../.agents/skills/stock-research/references/legacy-audit-v1.md)指引；显式`build --legacy-snapshot <本批framework-snapshot/manifest.json>`通过绑定验证才可用旧writer。原prompt/input/hash不改，合同不可恢复则新建批次，不让活跃默认技能重解释旧研究。失败沿用原最多一次重试，不发布未验收报价。

正常报价与控制交同一属主原子发布；已验收的阻断/退出而报价缺失或歧义，必须先交付合法completed unavailable v4（p1=null、T1无报价、全部适用控制与audit完整验收）并正常seal，再交下游属主按control-only路径收紧，旧价格及日期不变；failed/未验收receipt不能发布controls，不能以报价失败保留旧eligible。研究侧不直接写业务CSV。available_at由真实封口/发布属主记录，不按估值日倒填。回滚代码/报价不撤销新风险事实。完整源码测试和影子对照不等于投资效果、真实API或生产切换验证。

## 迁移与运行边界

[逐文件迁移清单](../docs/research-layout-migration.json)记录旧新路径、迁移前跟踪状态及前后哈希。冻结 ETF 预注册保留原文与原提交；文内旧输出路径是当时契约，由本文件映射到现行目录，不能用迁移提交冒充预注册提交。审计 JSON 的历史正文与来源哈希同样保留。

2026-10-06 公司目录改为日期优先：旧 `investment/companies/<公司标识>/<日期>/` 对应现行 `investment/companies/<日期>/<公司标识>/`。旧迁移清单与报告中的历史运行叙述保留当时路径；当前 JSON 的 `meta.report_path` 与导航使用新路径。本次本地迁移备份及逐文件校验记录位于 `output/layout-migration/2026-10-06-company-date-first/`。

本地备份位于被忽略的 `output/layout-migration/2026-10-05/`。迁移本身不授权 commit/push/PR。两个周更自动化通过根 AGENTS 和 skill 读取本契约；远端基线需包含完整迁移才能使用新规则，未提交新路径不能冒充已提交证据。

## Coze 条件补充（2026-10-14）

仅沪深A股同批Claude/Codex P1.base相对较低值的差异严格超过10%时启用。Coze以 `coze` 单独归档原文和`stock-research-coze/v2` JSON（历史v1仍可读），最低要求明确P1/T1；不同报告章节不套本仓九节，缺其他字段不补造。发送后15分钟无可确认归属的回复即终止失败，不重试，不接受迟到结果发布。原两模型封口及回写继续，成功Coze补充封口由原共识与写回入口消费。完整规则、证据、持续heartbeat见 [Coze接入契约](../docs/context/coze-research-automation.md)。
