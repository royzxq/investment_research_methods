# DSH 股票投研生产运行审计

核验日期：2026-11-03，Asia/Shanghai。只读审计；未启动研究、调用模型/API、安装插件、修改生产配置或改写现有日志。统计底稿：[runtime-audit-stats.json](/Users/xinquanzhou/Workspace/investment_research_methods/output/deep-research/2026-11-03-dsh-stock-research-plugins/runtime-audit-stats.json)。

## 结论

生产股票研究并不是“大量能力完全没用”。在 2026-10-29 至 2026-11-03 的 **26 个验收完成的 DSH 研究尝试**中，38 个主/子 session 合计调用 **16 种工具、3,604 次**。合并工具清单里共出现 29 个模型可调用工具名，13 个未调用；这不是“插件利用率”，因为基础插件还提供权限、日志、模型路由、文件系统、压缩等后台服务，不能按 tool call 数衡量。

最有证据的优化方向：测试已安装但生产未选择的专用 Search/Fetch API；将反复编写的 PDF 下载、按页提取、渲染和来源定位变成可靠的标准入口；改善 Jev manifest 验证反馈。`read_image`、子代理、Jev 和 compaction 组件都不是简单“没安装”。本审计不声称换插件后会提速多少，需同题对照验证。

## 配置与加载事实

- 本机 npm CLI 包 `/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/package.json` 的版本为 **0.2.1-rc.2**。这是本次读取到的安装版本，不代表 npm 最新版，也没有执行升级。
- `config/research_runtime.production.json` 的 DSH profile 为 `dsh-deepseek-flash-high`：主、子模型均 `deepseek-flash`；effort `high`。当前代码使用 `headless --patch <每次私有patch> --json -`，每次重设 `HOME`、`DSH_HOME`、`DSH_AGENTS_HOME` 与 `XDG_*`。证据：[运行隔离与补丁](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_dsh.py:250)、[实际启动命令](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_dsh.py:332)。
- headless 的基础 bundle 是 `@deepseek-ai/dsh-base` + `@deepseek-ai/dsh-headless`；生产运行生成的 `dsh-home/profiles/headless/package.json` 实读符合此结构。官方安装源码 [headless template](/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-app-boot/lib/index.js:554)；headless 声明不挂载 Host/HTTP server/Web runtime/browser plugin，且关闭交互 credentials/authorization/account。证据：[headless bundle](/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-headless/cordis.patch.yml:1)。
- 26 份实际 patch 都插入 `research-data-environment` 和 `research-mcp-jev_research`，主子模型、搜索路由、2 个活跃子代理上限一致。16 份旧 metadata 为 runtime/v1，10 份为 runtime/v2；不能把当前 v2 的 PDF 提示等改进倒推为全部历史都有。
- 当前可见用户目录 `~/.dsh` **不存在**，故 `~/.dsh/profiles/*/package.json` 与用户 cordis patch 枚举为空。当前审计环境 `DSH_HOME`、`DSH_AGENTS_HOME` 均未设置。此结论只覆盖可见路径，不推断其他 App bundle 或自定义目录没有桌面配置。即便桌面另有插件安装，生产每次生成的隔离 headless 也不会自动继承该 profile。
- skill 发现仍包含仓库 `.dsh/skills` 与 `.agents/skills`，所以仓库 `stock-research` 可用；用户级路径来自隔离后的 `DSH_HOME/skills`、`DSH_AGENTS_HOME/skills`。默认发现源码没有 `~/.codex/skills`；不能认为本会话列出的全局投资技能均已给 DSH。证据：[skill roots](/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-skill-filesystem/lib/index.js:150)。

默认 base 已配置 `compaction-basic`、`tool-result-pruner`（8192 字符阈值，4096头/1024尾）、`image-offload`、subagent spawn/fork、workflow PTC、web、MCP resources 等。[base 组件](/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-base/cordis.patch.yml:351)。插件“被组合进 profile”、服务“被模型可见”、能力“在本次调用”是三个不同层次。

## 样本和计数方法

发现边界严格为 `output/runs/investment/<日期>/*/execution/*/dsh/**/events.jsonl`，日期目录从 10-29 到 11-03，包含 retry 子目录。共发现 **32 个尝试**；主样本要求同目录 `process.json.status == completed` 且 `accepted.json` 内对应 DSH task 为 completed，得到 **26 个**。其余 **6 个失败尝试**单列，不混入成功样本的工具错误率。覆盖 27 个日期/公司任务，其中 1 个任务两次尝试均失败；这不是随意抽取少量顺利案例，但主表存在明确的“完成样本”选择边界。这里的 completed/accepted 是运行与产物验收状态，不证明报告中的财务事实、估值或投资结论正确。

日期分母：10-29=4、10-30=4、10-31=4、11-01=4、11-02=5、11-03=5。取完整 `dsh-sessions/**/session.v4.jsonl`（26 主 session、12 子 session），按 `tool/call.data.callId` 与 `tool/result.data.message.toolCallId` 一对一配对；不再加计外层 events.jsonl，避免双计。38 个 session 的 3,604 次调用均匹配结果。每份 session 的路径、SHA256、事件计数与调用/结果行号已保存在 JSON。

工具错误按 `message.isError` 计；bash 额外用 `job/settled.detail` 的退出码复核。工具延迟为同一 session 的结果时间减调用时间；**各工具延迟可能重叠，累计值不代表总墙钟，更不能直接当成可节省的时间**。单次完整研究墙钟取 process.json 的 started_at/completed_at，中位 **13.21 分钟**，范围 **3.70–19.74 分钟**，仅包含成功尝试自身，不含失败重试、等待前序 Codex 或批次排队。

| 工具 | 调用 | isError | 涉及完成尝试 / 26 | 中位延迟秒 | 累计工具秒 |
|---|---:|---:|---:|---:|---:|
| `bash` | 2494 | 0 | 26 | 0.076 | 1964.170 |
| `read` | 480 | 0 | 26 | 0.022 | 11.205 |
| `web_fetch` | 189 | 11 | 22 | 1.315 | 434.101 |
| `web_search` | 148 | 0 | 24 | 5.912 | 889.040 |
| `edit` | 78 | 9 | 11 | 0.026 | 1.939 |
| `write` | 46 | 0 | 21 | 0.029 | 1.345 |
| `list_agents` | 33 | 0 | 7 | 0.017 | 0.633 |
| `mcp__jev_research__research_jev_route` | 33 | 5 | 25 | 0.038 | 16.576 |
| `skill` | 28 | 0 | 26 | 0.021 | 0.564 |
| `read_image` | 26 | 0 | 4 | 0.062 | 1.863 |
| `todo_write` | 16 | 0 | 13 | 0.016 | 0.255 |
| `subagent` | 13 | 1 | 8 | 0.063 | 0.830 |
| `send_message` | 12 | 0 | 7 | 0.015 | 0.363 |
| `grep` | 4 | 0 | 2 | 0.054 | 0.277 |
| `job_output` | 3 | 0 | 2 | 0.014 | 0.036 |
| `interrupt_agent` | 1 | 0 | 1 | 0.015 | 0.015 |

29 个暴露过的工具名中，未观察到调用的是 `create_goal`、`get_goal`、`update_goal`、`exit_plan_mode`、`glob`、`job_kill`、`job_list`、`list_mcp_resources`、`list_mcp_resource_templates`、`read_mcp_resource`、`subagent_fork`、`workflow`、`working_directory`。其中许多不适用于一次性股票报告，未调用不等于缺陷。

bash 表中的 0 仅代表工具包装层 `isError`；底层 **55/2,494 个进程非零退出**，分布为 code 1=47、code 2=4、code 6=2、code 127=2。包括可恢复的查询无结果、环境探测、命令缺失和脚本失败，不能一律视为投资证据失败，也不能报“bash 零错误”。

## 搜索与抓取

148 次 `web_search` 内部记录 **381 次辅助 Messages 请求**，全部 endpoint 为 `https://api.deepseek.com/anthropic/v1/messages`，工具为 `web_search_20250305`，`max_uses=5`。示例 [原始 request 事件](/Users/xinquanzhou/Workspace/investment_research_methods/output/runs/investment/2026-11-03/c09461267e264fbf874a7b280931d1ec/execution/SH-601919/dsh/dsh-sessions/--Users-xinquanzhou-Workspace-investment_research_methods--/session-c72f70fc-34b2-40a4-8700-d9a38cd11187/session.v4.jsonl:306)。这是实际调用证据，不只是配置推测。

安装的 base 同时包含 `dsh-web-deepseek-api`，但默认 `web.searchProvider=deepseek-official`、`fetchProvider=http`；生产 patch 只配置旧 Messages 搜索 provider，未把选择改成 `deepseek-search-api` / `deepseek-fetch-api`。证据：[默认选择及两个 provider](/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-base/cordis.patch.yml:465)。

`maxUses=5` 的含义是**一次辅助 Messages 请求内部最多 5 次服务端 web_search**，不是整个研究、单个 session 或外层批次共只能搜索 5 次。源码在每次 `search(request)` 构造独立请求，并把该值写入 `tools[0].max_uses`：[search实现](/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-web-search-deepseek/lib/index.js:103)。381 是实际外发请求事件数，不能再假定每次都用满 5 次而报 1,905 次实际原生检索。

189 次 `web_fetch` 有 11 次工具错误（5 次 fetch failed、2 次 application/javascript 内容类型不支持、3 次跨域重定向不自动跟随、1 次 30秒超时）；示例 [fetch错误全文](/Users/xinquanzhou/Workspace/investment_research_methods/output/runs/investment/2026-10-29/c28c8a6b46eb496695bc90c2045e6af6/execution/HK-00700/dsh/dsh-sessions/--Users-xinquanzhou-Workspace-investment_research_methods--/24eab0c4-0f3f-40c9-a8b2-8d5ce45703a3/session.v4.jsonl:197)。搜索成功也不意味着正文取得成功，更不证明财务事实已原页核验。

专用 Search/Fetch API 是有针对性的候选实验：搜索可绕开辅助模型生成开销，Fetch 可测试对现有失败类型的覆盖。但本审计没有运行真实 API 对照，不能承诺解决所有重定向、反爬或 PDF 问题。

## PDF 与图片

本期完成样本中，bash 参数包含 `pymupdf/fitz/pdftotext/pdfinfo/pdfplumber/pypdf` 的候选调用 **230 次**，只是字符串筛查上限（包括环境探测或脚本读取），不直接当成 230 次有效 PDF 提取。4 次该候选命令非零退出：一次 `which` 工具探测、一次 pdftotext 缺失、一次 shell `timeout` 不存在、一次网络/JSON链失败；不能都归因于 PDF 解析器。

可复核的具体瓶颈是中创智领 10-31：[pdftotext 调用失败](/Users/xinquanzhou/Workspace/investment_research_methods/output/runs/investment/2026-10-31/40e52fb7faa844aa97f9b63e6794ff03/execution/SH-601717/dsh/dsh-sessions/--Users-xinquanzhou-Workspace-investment_research_methods--/session-c42dd52c-18f5-423e-9d88-bcf5eede70ce/session.v4.jsonl:602) 全文为 `pdftotext: command not found` 及目标文本不存在；随后 [PyMuPDF sort=True 成功取表](/Users/xinquanzhou/Workspace/investment_research_methods/output/runs/investment/2026-10-31/40e52fb7faa844aa97f9b63e6794ff03/execution/SH-601717/dsh/dsh-sessions/--Users-xinquanzhou-Workspace-investment_research_methods--/session-c42dd52c-18f5-423e-9d88-bcf5eede70ce/session.v4.jsonl:610) 返回原年度报告第24页成本分析表。其后来源摘录继续成功。当前代码已经把验证过的 miniconda PyMuPDF fallback 写入投研提示：[PDF fallback提示](/Users/xinquanzhou/Workspace/investment_research_methods/scripts/research_dsh.py:276)。应优先减少探测、临时脚本和布局提取的重复成本，不能把已恢复的历史架构报错当作今天仍普遍存在的故障。

`read_image` **26 次、4 个完成研究，均 isError=false，结果同时包含 text 与 image**。示例 [PDF渲染页读图返回](/Users/xinquanzhou/Workspace/investment_research_methods/output/runs/investment/2026-10-29/c28c8a6b46eb496695bc90c2045e6af6/execution/SH-600406/dsh/dsh-sessions/--Users-xinquanzhou-Workspace-investment_research_methods--/ec825369-df1e-451d-851c-7594abc57a6d/session.v4.jsonl:549)。因此“DSH 根本读不了图”与“图片插件没用过”不成立；本统计只证实图像载入，不证明每张图的财务解读正确。原生工具清单没有专门的 PDF 页码/表格工具，PDF 仍靠 shell/PyMuPDF 提取或渲染后 `read_image`。

两条匹配“incompatible architecture”的候选结果经全文核对都是读取旧报告的历史转述，不计为本期真实执行错误；统计 JSON 已给候选标注，避免关键词误判。

## 子代理、Jev 与压缩

13 次 `subagent` 调用涉及 8/26 个研究，形成 12 个子 session；1 次被 `maxActiveSubagents=2` 拒绝。12 个子 session 的日志跨度中位 **6.73 分钟**，不是表内 0.063 秒的 spawn 返回时间。`subagent_fork` 与 `workflow` 未调用；这只表明可用协作方式未全部使用，不能据此要求为已有充分证据强行增派。

Jev 分三层：33 次 MCP 路由工具调用、36 次路线请求（另 3 次经 bash 直接运行 `research_jev.py route`）、6 次实际后端批次。6 批均有 `backend_tool_submitted` 和 `call_finished(status=ranked)`；示例 [Jev后端成功日志](/Users/xinquanzhou/Workspace/investment_research_methods/output/runs/investment/2026-10-30/fda9f737c3f748a3a3fdacde6c13d2e1/execution/SH-601985/dsh/retry-1/jev/calls.jsonl:6)。36 次路由中记录 7 次 `validation_or_io_failure`、28 个决策、1 次缓存返回；7 次失败不是后端模型失败。各 run 总结为 18 skipped、6 invoked、1 fallback、1 not_requested。

`skipped` 多数原因是 `declared_precise_location`，另有候选数低于阈值的决策；示例 [已提交但程序判跳过](/Users/xinquanzhou/Workspace/investment_research_methods/output/runs/investment/2026-10-29/c28c8a6b46eb496695bc90c2045e6af6/execution/HK-00700/dsh/jev/calls.jsonl:3)。这不能归为“插件没用”。唯一 `not_requested` 是 10-30 SH-605499：`jev/calls.jsonl` 仅有 registered，后台可用，所有主/子工具调用未观察到 Jev 路由；所以在该次运行的已记录路由边界内，它确实没有提交候选批次，不代表全局没有使用 Jev。7 次验证失败说明完善 manifest 生成/路径诊断比单纯装更多 Jev 工具更有依据。

已完成样本 **没有任何 `compaction/*` 日志事件**，包含 prune、summary、start/end 均为0；所有 session 的 request/context 声明 contextWindow=1,000,000。基础组件已配置，不应把“没触发”写成“没装”。源码正常 prune 会显式追加 `compaction/prune`（[pruner事件](/Users/xinquanzhou/.local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-compaction-tool-result-pruner/lib/index.js:159)）；basic summary也显式追加 start/end/summary。本样本不支持“上下文压缩失败是主要瓶颈”的结论。

## 失败尝试边界

下列6个尝试已从主表剔除。它们主要是产物验收问题，不能归到搜索插件失败；当前 v2 与历史 v1 有变更，不把旧问题直接当作本日未修复状态。

| 日期 | task | attempt | 失败原因 |
|---|---|---:|---|
| 2026-10-30 | SH-601985 | 1 | report: requires sections 0-8 in order |
| 2026-10-31 | SZ-002594 | 1 | price_map.meta.name: inconsistent with request/result |
| 2026-11-01 | HK-02513 | 1 | price_map.meta.name: inconsistent with request/result |
| 2026-11-01 | HK-02513 | 2 | Expecting value: line 1 column 1 (char 0) |
| 2026-11-01 | SH-601318 | 1 | price_map.meta.name: inconsistent with request/result |
| 2026-11-02 | SH-601021 | 1 | report section 0 missing batch/input/framework binding |

## 可复算最小脚本

以下只读脚本重建主分母、session数量、工具调用/错误/延迟及底层搜索次数。完整逐调用路径与行号见旁边 stats JSON；该文件仅保存白名单配置、路径、计数与短错误，无凭据、完整环境或金融账户内容。

```python
from pathlib import Path
from collections import Counter, defaultdict
import json, statistics

root = Path("/Users/xinquanzhou/Workspace/investment_research_methods")
days = ["2026-10-29", "2026-10-30", "2026-10-31",
        "2026-11-01", "2026-11-02", "2026-11-03"]
runs = sessions = searches = 0
calls, errors, event_types = Counter(), Counter(), Counter()
latencies = defaultdict(list)
for day in days:
    for outer in sorted((root / "output/runs/investment" / day).glob(
            "*/execution/*/dsh/**/events.jsonl")):
        folder = outer.parent
        process = json.loads((folder / "process.json").read_text())
        if process["status"] != "completed" or not (folder / "accepted.json").exists():
            continue
        accepted = json.loads((folder / "accepted.json").read_text())
        assert any(x.get("generator") == "dsh" and x.get("status") == "completed"
                   and x.get("task_id") == process["task_id"]
                   for x in accepted["results"])
        runs += 1
        for source in sorted((folder / "dsh-sessions").rglob("session.v4.jsonl")):
            sessions += 1
            pending = {}
            for line_no, line in enumerate(source.open(), 1):
                event = json.loads(line)
                kind, data = event["type"], event.get("data", {})
                event_types[kind] += 1
                if kind == "web/deepseek-search-llm-request":
                    searches += 1
                elif kind == "tool/call":
                    pending[data["callId"]] = (data["name"], event["time"])
                    calls[data["name"]] += 1
                elif kind == "tool/result":
                    msg = data["message"]
                    name, start = pending[msg["toolCallId"]]
                    errors[name] += bool(msg.get("isError"))
                    latencies[name].append((event["time"] - start) / 1000)
print(runs, sessions, searches)  # 26, 38, 381
for name in sorted(calls):
    print(name, calls[name], errors[name], statistics.median(latencies[name]))
print({k: v for k, v in event_types.items() if "compaction" in k})  # {}
```

这是日志与本地安装源码审计。没有执行新的股票事实核验、真实搜索API验收、投资回测或生产配置修改。
