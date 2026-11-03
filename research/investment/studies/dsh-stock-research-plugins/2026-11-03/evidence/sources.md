# 单一来源索引

读取截止与日期：2026-11-03 Asia/Shanghai。主代理是本索引唯一写入者。未标发布日期的网页不推测发布日期；动态 main/master 为本日读取状态，不冒称固定提交。固定 rc.2 原文与本机 rc.2 判断当前运行，master 用于候选能力。

L 为本地规则/源码；P 为主代理打开的官方原文；SD/DM 为对应子代理笔记的原始来源编号，主代理回读关键候选及冲突。所有来源用于技术能力核验，未经真实 API 测试不能标为已接通。运行日志的逐文件哈希和实际行号见 runtime-audit-stats.json，主代理复查位置见 primary-verification.md。

| 编号 | 原始来源 | 日期／版本、实际读取位置与状态 |
|---|---|---|
| L1 | [scripts/research_dsh.py](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_dsh.py) | 已读现行原文；本地 SHA256 `7ae2aee618111e2729490dfa8b77bf1c5593f26baa54903732116a522b13b5e9` |
| L2 | [config/research_runtime.production.json](/Users/xinquanzhou/Workspace/investment_research_methods/config/research_runtime.production.json) | 已读现行原文；本地 SHA256 `f13c7ad3566af11e074808cb05a14071fb07fdd0220ec951996a4ae75562d0f3` |
| L3 | [docs/adr/ADR-20261029-sequential-stock-evidence.md](/Users/xinquanzhou/Workspace/investment_research_methods/docs/adr/ADR-20261029-sequential-stock-evidence.md) | 已读现行原文；本地 SHA256 `c14c5b42cf1839e44e54ea4bc0a4c7f35973238636093702d9699d5cac4f9abc` |
| L4 | [.agents/skills/stock-research/references/data-acquisition.md](/Users/xinquanzhou/Workspace/investment_research_methods/.agents/skills/stock-research/references/data-acquisition.md) | 已读现行原文；本地 SHA256 `6c3feadf9e9960460ca5b500fe0214730480ace02421363561529b44006205a6` |
| L5 | [.agents/skills/stock-research/references/jev-routing.md](/Users/xinquanzhou/Workspace/investment_research_methods/.agents/skills/stock-research/references/jev-routing.md) | 已读现行原文；本地 SHA256 `54691c19f57f9b5a1e69820e0365887a214dbd688dca814340f8dd5c90f2c8ef` |
| L6 | [research/README.md](/Users/xinquanzhou/Workspace/investment_research_methods/research/README.md) | 已读现行原文；本地 SHA256 `3c3ad25161258228952f142fbbc37935a48fecf3ad9d9c280392295774b7c945` |
| P1 | [官方发布](https://github.com/deepseek-ai/deepseek-harness/releases) | 已读发布列表；rc.5 2026-10-30、alpha.2 2026-10-28 |
| P2 | [官方 Search 计费与接口](https://api-docs.deepseek.com/guides/search/) | 已读接口、费用、生效日；服务状态未实测 |
| P3 | [官方 Vision](https://api-docs.deepseek.com/guides/vision/) | 已读图片能力与 Anthropic 接口 |
| P4 | [官方模型与价格](https://api-docs.deepseek.com/quick_start/pricing/) | 已读路由、Vision、Search/Fetch 计费 |
| P5 | [headless](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/bundle/headless/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P6 | [MCP client](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/mcp/mcp-client/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P7 | [CLI profiles](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/apps/cli/reference/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P8 | [旧搜索](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web-search-deepseek/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P9 | [独立API](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web-deepseek-api/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P10 | [provider选择](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P11 | [Exa](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/web/web-search-exa/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P12 | [read_image](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/fs/tool-fs/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P13 | [Playwright适配器](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/experimental/browser-use-playwright-mcp/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P14 | [技能发现](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/skill/skill-filesystem/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P15 | [压缩](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/compaction/compaction-basic/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| P16 | [原生spawn](https://github.com/deepseek-ai/deepseek-harness/blob/dsh-v0.2.1-rc.2/packages/subagent/subagent-spawn-in-process/README.md) | 主代理已打开固定 rc.2 原始 README 对应章节；与现行本机包对照 |
| SD-S1 | [官方独立 Search/Fetch README](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/web/web-deepseek-api/README.md)：Summary、Use this package、配置表、Authentication、Results and failures；约 8–51 行 |
| SD-S2 | [独立 API src/index.ts](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/web/web-deepseek-api/src/index.ts)：插件名、inject、Config、apply，约 27–80 行；[package.json](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/web/web-deepseek-api/package.json)：name/version |
| SD-S3 | [base/cordis.patch.yml](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/bundle/base/cordis.patch.yml)：attachment-local 131–135 行；web、旧/新 provider 和 tool-web 413–448 行 |
| SD-S4 | [官方 CLI reference](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/apps/cli/reference/README.md)：Profile boot 6–20 行、headless 38–39 行、dump 40–47 行 |
| SD-S5 | [独立 API src/fetch.ts](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/web/web-deepseek-api/src/fetch.ts)：20–40 行；[旧搜索 README](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/web/web-search-deepseek/README.md)：Summary、Use this package |
| SD-S6 | [DeepSeek 官方 Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/)：Model Details、Vision、Search & Fetch Pricing，页面 29–75 行 |
| SD-S7 | [官方 Exa README](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/web/web-search-exa/README.md)：Summary、Use this package、What a search returns、Failures，8–51 行 |
| SD-S8 | [Exa package.json](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/web/web-search-exa/package.json)：name/version/peerDependencies |
| SD-S9 | [X-C1811 作者仓库 README](https://github.com/X-C1811/dsh-web-search-plugin)：Why use、Supported providers，页面 195–213 行；[package.json](https://raw.githubusercontent.com/X-C1811/dsh-web-search-plugin/main/package.json)：name/version/peerDependencies |
| SD-S10 | [多供应商 lib/index.js](https://raw.githubusercontent.com/X-C1811/dsh-web-search-plugin/main/lib/index.js)：inject 31–37 行、Tavily/Brave schema 75–99 行、provider 注册及可选 webServer 353–382 行 |
| SD-S11 | [Tavily 实现](https://raw.githubusercontent.com/X-C1811/dsh-web-search-plugin/main/lib/tavily.js)：默认 endpoint/credential、mapTavilyResponse、request body，9–75 行 |
| SD-S12 | [多供应商 bundle patch](https://raw.githubusercontent.com/X-C1811/dsh-web-search-plugin/main/cordis.patch.yml)：全 30 行，默认替换 web 与禁用旧 provider |
| SD-S13 | [官方 Playwright MCP 适配器 README](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/experimental/browser-use-playwright-mcp/README.md)：Use this package、生命周期 23–52 行、模型工具及限制 70–88 行 |
| SD-S14 | [官方 Playwright 适配器 package.json](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/experimental/browser-use-playwright-mcp/package.json)：version、dependency @playwright/mcp 0.0.80 |
| SD-S15 | [Microsoft playwright-mcp README](https://github.com/microsoft/playwright-mcp)：headless/isolated 等参数约 526–552 行、Standalone MCP server、programmatic usage |
| SD-S16 | [官方 dsh-mcp-client README](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/mcp/mcp-client/README.md)：Use this package、configuration、工具名、image result 投射，23–78 行 |
| SD-S17 | [官方 tool-fs README](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/fs/tool-fs/README.md)：read_image gate 23–58 行、image cost 184–190 行、PDF/attachment limitations 264–268 行 |
| SD-S18 | [Vision Toolkit README](https://raw.githubusercontent.com/Anionex/dsh-vision-toolkit/main/README.md)：headless 安装 131–156 行、Toolbox 166–181 行；[package.json](https://raw.githubusercontent.com/Anionex/dsh-vision-toolkit/main/package.json)：name/version/runtime |
| SD-S19 | [Vision Toolkit src/index.ts](https://raw.githubusercontent.com/Anionex/dsh-vision-toolkit/main/src/index.ts)：生命周期声明、inject/apply，1–50 行 |
| SD-S20 | [Vision Toolkit bundle patch](https://raw.githubusercontent.com/Anionex/dsh-vision-toolkit/main/cordis.patch.yml)：全 6 行 |
| SD-S21 | [Vision Toolkit config.ts](https://raw.githubusercontent.com/Anionex/dsh-vision-toolkit/main/src/config.ts)：credential/provider schema、resolveConfig、built-in free provider 判别，1–60、133–139、339–364、494–500 行 |
| SD-S22 | [MinerU 插件 README](https://raw.githubusercontent.com/HuanLinOTO/dsh-plugin-mineru/master/README.md)：配置 25–38 行、五工具 39–59 行、自行部署 84–86 行 |
| SD-S23 | [MinerU 插件 package.json](https://raw.githubusercontent.com/HuanLinOTO/dsh-plugin-mineru/master/package.json)：name/version/peer dependencies；[tools.ts](https://raw.githubusercontent.com/HuanLinOTO/dsh-plugin-mineru/master/src/tools.ts)：开头 HTTP 操作映射 |
| SD-S24 | [MinerU 插件 src/index.ts](https://raw.githubusercontent.com/HuanLinOTO/dsh-plugin-mineru/master/src/index.ts)：host/client 架构注释与硬 inject，1–36 行 |
| SD-S25 | [dsh-attachment-formats README](https://raw.githubusercontent.com/linkingoscar/dsh-attachment-formats/main/README.md)：Web GUI 定位与格式表 0–35 行、external document server/cache 115–138 行 |
| DM-S1 | https://raw.githubusercontent.com/akfamily/aktools/main/README.md | 在 AI 助手中使用、安装、调用规则；Python/stdio/HTTP、缓存；发布日期未标。 |
| DM-S2 | https://raw.githubusercontent.com/akfamily/aktools/main/aktools/mcp_server.py | L3 日期 2026/10/29；L29–42、L63–138、L167–184 三工具/分页/stdio 源码。 |
| DM-S3 | https://raw.githubusercontent.com/akfamily/aktools/main/pyproject.toml | L4–8、46–62 项目依赖与 CLI entrypoints。 |
| DM-S4 | https://akshare.akfamily.xyz/data/stock/stock_finance.html | A 股利润表 L1583–1608；港股三表 L2207–2243；文档当前 1.20.22；目标源东方财富。 |
| DM-S5 | https://github.com/akfamily/akshare | README AI Assistants / Statement；仅学术研究、接口可移除。官网 stock 总索引显示更新 2026-11-02。 |
| DM-S6 | https://tushare.pro/document/1?doc_id=463 | L61–111 官方 MCP 文档、个人中心 key、远程 URL；未标发布日期。 |
| DM-S7 | https://tushare.pro/document/1?doc_id=450 | L76–113 官方 skill 安装及作者 GitHub 链；未标发布日期。 |
| DM-S8 | https://raw.githubusercontent.com/waditu-tushare/skills/master/tushare/SKILL.md | frontmatter 1.1.12；环境、接口文档、分段/重试、output contract 章节；未执行 skill。 |
| DM-S9 | https://tushare.pro/document/1?doc_id=108 | L61–104 积分权限与 A 股财务门槛。 |
| DM-S10 | https://tushare.pro/document/2?doc_id=389 | 港股利润表接口、单独权限、最大行数、字段；已打开原页。 |
| DM-S11 | https://raw.githubusercontent.com/lijinly/tushare-mcp-server/main/src/tushare_mcp_server/server.py 及 https://github.com/lijinly/tushare-mcp-server | env credential/stdin server/import、工具列表与财务调用实现；社区例，非推荐。 |
| DM-S12 | https://github.com/volcengine/OpenViking | README What/Why/Quick start；资源树、分层摘要、服务/模型依赖。 |
| DM-S13 | https://raw.githubusercontent.com/volcengine/OpenViking/main/examples/dsh-memory-plugin/README.md | Requirements/Compatibility、L146–211 预注入/proxy/skills、L212–300 configuration/behavior/tool scope；作者版本兼容声明。 |
| DM-S14 | https://raw.githubusercontent.com/volcengine/OpenViking/main/examples/dsh-memory-plugin/package.json | 0.5.32；peer range、Node、包文件与入口。 |
| DM-S15 | https://raw.githubusercontent.com/volcengine/OpenViking/main/examples/dsh-memory-plugin/mcp.mjs | L0–12 真正挂载 MCP client。 |
| DM-S16 | https://docs.openviking.ai/en/agent-integrations/16-capability-reference 及 https://docs.openviking.ai/en/agent-integrations/06-mcp-clients | 自动生命周期和纯 MCP 工具的差别；server/tools 和鉴权/stdio proxy；DSH 子代理处理。与 S13 更细版本默认冲突时以作者当前代码/README 的明确设置为准。 |
| DM-S17 | https://github.com/bowenliang123/dsh-context | README L209–274 五入口、web 安装、费用估计与官方 token projection。 |
| DM-S18 | https://raw.githubusercontent.com/bowenliang123/dsh-context/main/package.json | 0.80.2；L15–18 engines，L55–75 web client/compatibility。 |
| DM-S19 | https://raw.githubusercontent.com/bowenliang123/dsh-context/main/src/host/index.ts | L23–48 sessionProjections、统计/watchers、prompt injection；真实 host 能力。 |
| DM-S20 | https://raw.githubusercontent.com/bowenliang123/dsh-context/main/src/host/config.ts | L47–48 prompt prefix/suffix 默认空。 |
| DM-S21 | https://raw.githubusercontent.com/bowenliang123/dsh-context/main/src/host/promptInjection.ts | L31–48 注册 system prompt sections；可配置影响模型。 |
| DM-S22 | https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/llm/token-meter/README.md | Summary、measurement、session projections；与本机 0.2.1-rc.2 README 共同核验。 |
| DM-S23 | https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/core/tools/README.md 及 https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/core/tool-executor-ptc/README.md | PTC 的 SDK/run_code、并行与只输出选定结果；上游拆 executor，不能据此认定已安装版配置相同。 |
| DM-S24 | https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/development.md 及 https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/ptc-runtime/ptc-runtime-node/README.md | headless PTC demo、Node runtime 依赖与限制。 |
| DM-S25 | https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/workflow/workflow-ptc/README.md | 最小配置、concurrency/total 默认、没有总体 deadline、caller cancellation、协作 cap 非安全预算；也读本机同包 README。 |
| DM-S26 | https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/experimental/agent-team/README.md | 最小配置、maxMembers、任务板和跨进程/目录限制；也读本机 README。 |
| DM-S27 | https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/experimental/tool-agent-team/README.md | nine tools、legacy controls 冲突、experimental 无稳定保证。 |
| DM-S28 | https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/experimental/client-ui-agent-team/README.md | Web roster/task board；host export inert；UI 与 domain/tool 分离。 |
