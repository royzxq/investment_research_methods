**DSH 股票投研插件：当前使用情况、增益候选与接入顺序**

调研截止：2026-11-03，Asia/Shanghai。本报告保留接入前的研究判断；后续实施及正文质量纠错见[接入与复审记录](../../../maintenance/2026-11-03/investment-2026-11-03-dsh-plugin-rollout-codex.md)。生成端：Codex。本次为增量调研，接续本仓 10 月 DSH 迁移研究，但当前判断重新核对了生产适配器、本机安装包、近期完整会话日志及官方／作者原始资料。

**结论：当前 DSH 已经使用了一批核心插件，也真实调用了搜索、图片读取、子代理和 Jev。可以继续扩展，但最值得做的是直接搜索、结构化财务取数和困难网页取证；批量安装插件没有已证实的收益。** 研究质量上的优先项是减少缺证与口径错误；运行效率上的优先项是减少重复取数、临时脚本和不必要的模型往返。

当前自动流程使用每次尝试独立的 headless 配置。桌面端安装、Codex 聊天中可见、磁盘上存在、运行时已加载、实际调用成功，是五种不同状态。本报告将它们分别处理。全部新增候选尚未做真实投研 A/B；本次没有安装插件、修改生产配置或启动新的股票研究。

**当前已经用了什么，有什么证据。**

本机 npm DSH 是 `0.2.1-rc.2`，主模型和子模型均配置为 `deepseek-flash`、high。官方发布页本日已有 `0.2.1-rc.5`（10 月 30 日）与 `0.2.2-alpha.2`（10 月 28 日）；下文判断当前运行能力以已安装 rc.2 为准，社区插件的 main/master 版本只代表本日读取状态。直接 Search/Fetch 组件在当前版本中就已存在。[官方版本记录](https://github.com/deepseek-ai/deepseek-harness/releases)

本轮扫描 `output/runs/investment/2026-10-29` 至 `2026-11-03` 的 32 个 DSH 尝试；工具统计纳入其中 **26 个 process.completed 且存在 accepted.json 的尝试**，另列 6 个失败尝试，不混入成功样本。纳入样本含 26 个主会话、12 个子会话，按完整 session JSONL 统计，不用有截断的 headless stdout 重建完整过程。这里的“验收”是运行器交付验收，不表示本次重新审查了 26 份报告的投资结论。

| 能力 | 26 个已完成尝试中的实际记录 | 判断 |
|---|---|---|
| 官方网页搜索 | 24 次研究调用，148 次工具调用；381 条辅助搜索模型请求事件 | 已经在用，仍是 Messages 搜索路线 |
| 网页读取 | 22 次研究调用，189 次工具调用，其中 11 次工具错误 | 已在用；失败取页仍有补充空间，错误率不等于最终证据缺失率 |
| 原生图片读取 `read_image` | 4 次研究、26 次调用，结果均含 text＋image 且无工具错误 | 已能把图片送入研究上下文；不证明每个财务数字识别正确 |
| 原生子代理 | 8 次研究、13 次启动调用，成功产生 12 个子会话；1 次碰到活跃数量上限 | 已在用；当前并发上限 2、深度上限 1 |
| Jev 条件路由 | 25 次研究提交路由，33 次 MCP 调用＋3 次 shell 路由；6 个后端批次成功 ranked | 已有真实后端调用；无需再装一套 Jev |
| shell / Python | 26 次研究、2,494 次 bash 调用；底层作业中 55 次非零退出 | 是重要执行通道；不能因 bash 工具外层未报错就称全部命令成功 |
| 技能、压缩、计量和持久化 | 每次研究均有 skill 调用；base 已含压缩与 token-meter，样本无 compaction 事件 | 已有基础能力；“没触发压缩”不等于“没有压缩插件” |

Jev 每次研究最终状态为 18 skipped、6 invoked、1 fallback、1 not_requested。skipped 有程序决定依据；not_requested 只表示没有提交候选，不能解释为程序已判断不需要。以上来自完整运行日志和 Jev calls，主代理独立复查了旧搜索请求、图片结果、取页失败及一次 Jev 成功记录。可复核证据、文件哈希和统计口径见[运行审计](evidence/runtime-audit.md)、[统计数据](../../../../../output/deep-research/2026-11-03-dsh-stock-research-plugins/runtime-audit-stats.json)、[独立核验](evidence/primary-verification.md)。

**额外插件没有自动进入投研，原因在运行配置。**

`scripts/research_dsh.py` 每轮重设 HOME、DSH_HOME、DSH_AGENTS_HOME 和 XDG 目录，使用 `base + headless` 并叠加本批 patch；注入现有 Jev stdio MCP 和 Tushare 环境桥。项目 `.agents/skills` 可被发现，用户其他宿主的插件、技能和登录态不能据此视为可用。检查默认 `~/.dsh` 未发现目录；这不等于穷尽了所有可能的桌面自定义安装位置，但生产隔离机制已有代码与实际 profile 支持。[本地适配器](../../../../../scripts/research_dsh.py)；[官方 profile 组合规则](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/apps/cli/reference/README.md)；[技能发现规则](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/skill/skill-filesystem/README.md)

因此，后续接入应由投研运行配置明确加载、固定依赖并记录版本，而不是只在桌面勾选。DSH 原生插件、通用 MCP 服务和 SKILL.md 研究方法也不能混称：前两者提供运行能力，后者提供使用方法；接入数据服务不会自动获得更高账户权限或更可靠的会计口径。

**建议优先评估以下能力，先小范围接入。**

| 顺序 | 准确名称／类型 | 对当前投研的增量 | 当前判断与条件 |
|---|---|---|---|
| 先做 | `@deepseek-ai/dsh-token-meter`＋完整 session 日志，官方内置 | 找出主／子代理、重试、取数失败和上下文开销发生在哪 | 已具备；完善本地汇总即可，不必另接观测平台 |
| 第一批 | `@deepseek-ai/dsh-web-deepseek-api`，官方原生插件 | 直接 Search/Fetch，搜索免去辅助模型请求，正文可转 Markdown | 当前已挂载但未选用；配置解析已验证，网络与效果待测 |
| 第一批 | AKTools：`aktools-mcp`，AKShare 作者维护的通用 MCP | 发现接口、查参数、取结构化数据，补 Tushare 缺口和交叉核对 | stdio 适配方向吻合；需固定 Python 环境与包版本，验证 A/H 数据和分页 |
| 第一批按需 | `@deepseek-ai/dsh-experimental-browser-use-playwright-mcp`，官方实验适配器 | 处理 JS 公告列表、筛选器、下载入口及普通 HTTP 失败页面 | 需要 Chromium、会话隔离与退出清理；仅困难页面触发 |
| 第二批按需 | `@deepseek-ai/dsh-web-search-exa`，官方原生插件 | 增加一个搜索索引，帮助查海外行业／竞争者或遗漏来源 | 需 Exa key；中国公告召回收益未测，不能当自动故障切换 |
| 第二批按需 | `@anionex/dsh-vision-toolkit`，社区插件＋skill＋Python runtime | 长图分块 OCR、定位和裁剪 | 普通读图已经有；只在复杂扫描表上比较增量 |
| 暂作专门实验 | `@openviking/dsh-memory-plugin` 或其检索 MCP | 跨轮年报、公告原件的定位和找回 | 先建立事实档案边界；默认自动记忆不适合直接进入双席研究 |

这是根据当前能力和缺口作出的优先级判断，不是插件性能排行榜。各候选还需满足以下具体条件。

**直接 Search/Fetch 是最容易形成可比试验的一项。**

当前 `web` 选择 `deepseek-official / http`，`web-search-deepseek` 会为搜索发起辅助 Messages 请求。日志中 381 个事件都指向 `/anthropic/v1/messages`。配置里的 `maxUses=5` 是**每个辅助请求内部服务端搜索次数上限**，不是一份研究最多搜五次。[旧搜索官方说明](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web-search-deepseek/README.md)

新组件选择 `deepseek-search-api / deepseek-fetch-api`，沿用 DeepSeek 凭据。本轮在空凭据、独立临时目录中，两次运行 `--dump-config` 均成功，候选组合也确实切到新 provider。它只证明配置可以解析，没有执行 API 或证明研究更快。[候选 patch 与解析记录](../../../../../output/deep-research/2026-11-03-dsh-stock-research-plugins/config-probe.json)

当前 rc.2 的直接搜索适配器只使用短 snippet，尚未利用 API 的长 summary；后续源码已有相关改进。因此试验必须同时检查来源命中与后续读取成本。Fetch 也不返回目标网站真实状态／最终重定向 URL；不要把它映射出的 HTTP 200 当成下载原文件的凭证。新 provider 没有自动重试或自动换厂商，PDF 原件、页码和哈希仍应保留现有下载路线。[rc.2 新组件说明](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web-deepseek-api/README.md)

2026-11-03 官方定价为 Search、Fetch **各 0.75 美元／1,000 个成功请求**；例如 20 次搜索＋20 次抓取的接口费为 0.03 美元，另计模型处理结果的 token。页面明确 11 月 1 日开始计费，不能沿用其残留“currently free”字样。旧服务端搜索也在计费范围，比较时需核真实用量。[官方计费](https://api-docs.deepseek.com/guides/search/)

样本单次研究耗时中位数 **13.21 分钟**；搜索工具调用中位数 5.91 秒，所有搜索工具计时合计约 889 秒，摊到 26 次研究约 34.2 秒／次。工具可能并发，这些计时不能直接换算为墙钟节省比例，但足以说明：单换搜索插件不支持“大幅缩短整份研究”的承诺。下一步应同时减少重复脚本、无效取数和不必要的上下文传输。

**财务数据方面，AKTools 的增量比再包一层现有 Tushare 更明确。**

AKTools 真正提供 `search_interfaces`、`describe_interface`、`get_data` 三个 MCP 工具，支持 stdio；可先查接口说明再取数，降低猜函数和参数的次数。默认只返回有限行数，应消费 `total_rows / offset / truncated`，完整取得所需区间。其 A/H 财务入口仍有东方财富等聚合来源，核关键会计字段要回公告；两家聚合平台数字相同也未必是独立证据。[AKTools 作者仓库](https://github.com/akfamily/aktools)；[MCP 源码](https://github.com/akfamily/aktools/blob/main/aktools/mcp_server.py)；[AKShare 财务接口](https://akshare.akfamily.xyz/data/stock/stock_finance.html)

Tushare 已有**官方远程 MCP**和官方 skill，不能说市面上全是社区封装。但现行 DSH adapter 固定构造 stdio，不能原样接其 URL 配置；且已有 Tushare 数据桥，切换协议本身不增加覆盖或权限。官方示例将凭据嵌入连接 URL，接入时须避免落入 patch／日志。港股财报有独立权限要求，应保留未取得字段。建议先补现有接口参考与有限取数封装，把官方远程 MCP 留作有明确收益时的选项。[Tushare 官方 MCP](https://tushare.pro/document/2?doc_id=463)；[港股利润表权限](https://tushare.pro/document/2?doc_id=389)

更贴合本仓的长期工具形态，是把“公告主体识别→日期窗口→完整分页→原文下载→哈希／页码→字段口径”封装成少量可审计操作。已有 `data-acquisition.md` 可以作为契约。这里是工程建议，尚未找到并验证一个能完整替代此流程的现成 DSH 插件。[本仓取证契约](../../../../../.agents/skills/stock-research/references/data-acquisition.md)

**浏览器和备用检索应处理具体缺口。**

官方 Playwright 适配器明确支持 `mode: launch, headless: true`，需与 `@deepseek-ai/dsh-browser-use` 配合；另一条路线是现有 MCP bridge 接微软 `@playwright/mcp`。两者择一即可。私有 HOME 会影响浏览器发现和缓存，需固定可运行 Chromium 路径并验证进程清理。其价值是取得动态网页资料，不保证跨过登录、验证码、访问政策，也不会解析所有 PDF 表格。[DSH 官方适配器](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/experimental/browser-use-playwright-mcp/README.md)；[微软 Playwright MCP](https://github.com/microsoft/playwright-mcp)

备用搜索优先挑一个。Exa 官方适配器结构简单，但会丢弃没有 highlight 的结果，也没有封装 Exa 全部产品能力。若已有 Tavily／Brave 需求，可再考虑社区 `dsh-web-search-plugin`；它默认配置和 bundle 会修改搜索路线，安装不等于自动获得备用搜索。多个 provider 共存也不会自动按优先级尝试，需显式选择或实现可审计回退。[Exa 适配器](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web-search-exa/README.md)；[社区多搜索插件](https://github.com/X-C1811/dsh-web-search-plugin)；[provider 选择规则](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web/README.md)

**PDF/OCR 要以当前原生视觉为基线，避免重复购买能力。**

当前 `deepseek-flash` 已支持图片；本机模型声明、官方文档和 26 次真实 `read_image` 结果相互吻合。已有 PyMuPDF 渲染原页再读图的路线，可用于普通图表核验。扫描表、多栏和跨页续表仍可能误读，应检查期间、单位、负号、列归属、合计及附注。[官方视觉说明](https://api-docs.deepseek.com/guides/vision/)；[原生 read_image 条件](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/fs/tool-fs/README.md)

`@anionex/dsh-vision-toolkit` 有明确 headless 路线，分块 OCR 和裁剪可作复杂材料备选；它另需 Python runtime 和视觉供应商配置，中文财报精度尚未验证。`@huanlin/dsh-plugin-mineru` 则存在具体兼容疑点：作者源码硬依赖 `connection`，标准 headless 不挂浏览器 Connection。根据这两项事实，目前不能把它列为可直接安装使用；即使适配成功，也仍需独立 MinerU 服务。Web 附件上传插件同样不能视为自动投研的文件读取能力。[Vision Toolkit](https://github.com/Anionex/dsh-vision-toolkit)；[MinerU 插件依赖源码](https://github.com/HuanLinOTO/dsh-plugin-mineru/blob/master/src/index.ts)；[headless 运行边界](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/apps/cli/reference/README.md)

**记忆、团队和上下文插件应后置。**

OpenViking 的 DSH bundle 能自动召回、捕获会话并挂 MCP；但默认会写入会话、跨 peer 召回，按仓库派生的 peer 也不会自然区分公司、生成端和估值截止。当前合同要求 DSH 独立估值，不读取 Codex 结论；默认全量记忆可能把另一席估值、旧假设或截止后材料带回来。若未来档案规模确实成为瓶颈，先做显式原件检索，限定公司／披露日／生成端，验证服务端过滤和权限，不直接启用自动会话记忆。单设 `syncTurns:false` 不会停止召回，也不能清除历史待写队列。[OpenViking 插件原文](https://github.com/volcengine/OpenViking/tree/main/examples/dsh-memory-plugin)；[本仓共享事实边界](../../../../../docs/adr/ADR-20261029-sequential-stock-evidence.md)

`dsh-context` 有真实 host 统计代码，可供人工诊断，其主要呈现依赖 Web；仅安装到私有 headless 并不会自动得到可查看的仪表板。优先利用已有 token-meter 与完整日志。启发式上下文大小、供应商实报 token 和费用估计必须分开，失败／辅助搜索请求未报告的用量保持 null。[dsh-context](https://github.com/bowenliang123/dsh-context)；[官方 token-meter](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/llm/token-meter)

PTC runtime 和 workflow 基础组件已在本机，但研究仍采用 native 工具模式。PTC 可以实验批量元数据、哈希和表格验算；它改变工具呈现和执行路径，不能假定一定省 token。现有子代理足以先做窄任务分工；另加 Agent Teams 会带来任务板、消息和结束／恢复路径，尚无本项目收益依据。样本未出现 compaction 事件，也没有依据把新的压缩插件列为首要瓶颈。[本机对应工具模式文档](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/core/tools/README.md)；[官方实验 Agent Teams](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/experimental/agent-team)；[内置压缩](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/compaction/compaction-basic/README.md)

**落地建议是“一个基线、三类小试验”。**

先把现有日志汇总到每次尝试：模型与插件版本、主／子代理及重试用量、工具调用／失败、原文取得情况、最终验收结果。再分别验证直接 Search/Fetch、AKTools、困难页面浏览器；每次只改一个因素，使用相同证券、截止日、冻结框架和事实包。优先复用已有 A/H 样本，加入扫描表、跨页附注、分页截断、错误主体、接口失败等边界。

| 验收维度 | 应比较的结果 |
|---|---|
| 证据覆盖 | 必需公告／附注取得率，主体、披露日、原文版本是否正确；空结果和失败能否保持缺口 |
| 财务质量 | 币种、单位、期间、合并口径、股本、调整后利润及勾稽关系，是否漏反证或重述 |
| 研究交付 | 现有报告／JSON、控制条件、事实包哈希和独立估值边界继续通过 |
| 效率 | 完整任务墙钟、主＋子＋重试实际用量、检索费、重复取数和人工修复次数 |
| 运行稳定性 | 私有 HOME 下依赖可解析、分页完整、超时／取消清理、旧冻结批次保持原配置 |

首批不需要同时安装额外记忆、Agent Teams、UI 美化或多套视觉插件。若第一轮证明插件提高了原文取得率或减少了数据错误，再进入新准备批次；已经冻结的研究按原合同恢复。只有工具返回更快、报告更长、调用更多、或格式验收通过，都不足以证明投资判断更好。

本次已完成代码／配置／日志审计、官方及作者原文核查、空凭据配置解析。**未完成新增组件的真实 API、浏览器启动、OCR 质量、整份投研 A/B 或收益验证**，因此不报预期节省百分比。正式研究与证据笔记已本地保存；完整来源账本见[来源索引](evidence/sources.md)，细项见[检索与文档笔记](../../../../../output/deep-research/2026-11-03-dsh-stock-research-plugins/search-documents.md)和[数据与记忆笔记](../../../../../output/deep-research/2026-11-03-dsh-stock-research-plugins/data-memory.md)。本轮采用主代理＋3 个独立取证任务，实际 token 用量不可得。
