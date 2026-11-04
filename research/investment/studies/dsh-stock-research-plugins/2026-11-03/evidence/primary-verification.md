# 主代理独立核验

读取日期：2026-11-03，Asia/Shanghai。

- 本机 `~/.local/lib/node_modules/@deepseek-ai/dsh/package.json`：`@deepseek-ai/dsh` 版本 `0.2.1-rc.2`；本机已安装包是判断现行能力的依据。
- `scripts/research_dsh.py:254–263`：每次尝试设置独立 HOME、DSH_HOME、DSH_AGENTS_HOME 和 XDG 目录；`287–318` 设置模型、spawn/fork、并发2/深度1、旧式搜索和 stdio MCP；`332` 使用 headless --patch --json。本轮不改这些配置。
- 本机 `dsh-base/cordis.patch.yml:467–481`：web 默认 `searchProvider=deepseek-official`、`fetchProvider=http`；`web-deepseek-api` 已挂载。
- 本机 `dsh-llm-deepseek/lib/index.js:43–46`：`deepseek-flash` 声明 `inputModalities=[text,image]`；配合官方当前 Vision 文档核验，不沿用“DeepSeek只能读文本”。
- 原始 session `output/runs/investment/2026-10-29/c28c8a6b46eb496695bc90c2045e6af6/execution/HK-00700/dsh/dsh-sessions/--Users-xinquanzhou-Workspace-investment_research_methods--/24eab0c4-0f3f-40c9-a8b2-8d5ce45703a3/session.v4.jsonl:97`：已直接读取 `web/deepseek-search-llm-request`，endpoint `/anthropic/v1/messages`，独立搜索请求，max_uses=5。
- 同 session 第197行：已直接读取 web_fetch 的 WEB_PROVIDER_ERROR，`TypeError: fetch failed`。只证明该调用失败，不证明具体站点封禁、插件根因或研究失败。
- `output/runs/investment/2026-10-29/c28c8a6b46eb496695bc90c2045e6af6/execution/SH-600406/dsh/dsh-sessions/--Users-xinquanzhou-Workspace-investment_research_methods--/ec825369-df1e-451d-851c-7594abc57a6d/session.v4.jsonl:549`：读取原始 tool/result，图片内容块存在；不据此宣称图表数字识别无误。
- `output/runs/investment/2026-10-30/fda9f737c3f748a3a3fdacde6c13d2e1/execution/SH-601985/dsh/retry-1/jev/calls.jsonl:6`：直接读取 call_finished，ranked、successful_items=10、errors={}、backend_tool_submitted=true。确认 Jev 后端真有成功调用。
- 从完整统计重新计算26个已完成尝试：耗时中位数13.21分钟、范围3.70–19.74分钟；search tool 调用148次，总计时889.04秒，即每研究约34.2秒（包含未调用研究）。工具可并发、统计不涵盖全部provider成本，不能将其换算为可节省墙钟比例。
- 独立无凭据临时 HOME 中运行两次 CLI `--dump-config`：基线及候选直连 Search/Fetch patch 均 exit0、stderr空；实际组合分别选择旧路由和 `deepseek-search-api/deepseek-fetch-api`。脚本、配置、dump、结果见本目录 `probe_config.py`、`candidate-search.patch.json`、`*-composition.txt`、`config-probe.json`。仅配置解析，不代表插件启动、网络请求或投研效果通过。

关键网页已由主代理打开：官方仓库与release、rc.2 headless/MCP/skill-filesystem/web/web-search-deepseek/web-deepseek-api/web-search-exa/tool-fs/experimental-browser-use-playwright-mcp README；DeepSeek API pricing/search/vision；Tushare doc_id=463；AKTools作者仓库MCP章节。子代理对额外候选的证据另见独占笔记。
