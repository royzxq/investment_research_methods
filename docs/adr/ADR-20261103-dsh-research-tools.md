# DSH 首批研究工具与用量统计

日期：2026-11-03（Asia/Shanghai）。范围：用户授权的首批隔离对照、有效组件接入。股票方法、共享证据、财务定义检查、两价输出及现有验收合同不变。

## 决定

新准备的 DSH 批次选择 `dsh-deepseek-flash-high-tools-v1`：

```json
{
  "search": "deepseek-search-api",
  "fetch": "http",
  "aktools": "aktools-0.1.4-r1"
}
```

Search API 通过安装版本的真实 provider A/B 及 DSH 模型集成测试。12 组配对中两路径各成功 12 次；中位耗时 7,000 → 948.5 ms。11 组来源 URL 集合完全一致，另一组仅同一新浪研报的地址别名不同。这是取证搜索环节的改善，不能外推整篇投研耗时或账单节省。

Fetch API 不作全局替换：10 次调用中有 2 次返回实质汇率正文，两份 PDF 及两类 IEA 页面返回 HTTP 404。复审纠正原来的比较：原 HTTP 的 6 次非空 200 响应均在 100,000 字符处截断，只有页面头部/导航，没有实质正文，不能称原路径更有效。HTTP 本来不解析 PDF，继续原下载/PyMuPDF 核页流程；HTML 也需按需要完整下载或浏览器补充，不能凭 200 解除取证缺口。Fetch API 在汇率页显示了定向补充价值，其他样本不足以支持全局切换，其合成 HTTP 200 也不是目标网站状态证明。本次未安装或测试浏览器，不据此判断浏览器是否必要。

AKTools 通过 stdio 握手、工具发现、描述、A/H 财务取数、完整分页和 DSH 工具调用测试。仅作为第三方结构化补数渠道；原始公告仍是核验来源。样本为比亚迪 A/H 股、洛阳钼业，8 个字段与原公告匹配，不能据此证明全接口、全字段正确。港股财报接口不含币种，须从原公告确认。首次 A 股调用 41.8/43.9 秒，新进程复测比亚迪 25.5 秒；HK 首次约 3 秒，同进程重复为缓存，不能当作独立网络稳定性测量。

## 冻结和兼容

`research-runtime-config/v1` / `research-execution-plan/v1` 增加仅 DSH 可用的可选 `tools` 对象。必需键 `search/fetch` 只接受代码内白名单；可选 `aktools` 只接受 null 或固定 runtime ID。不能填写密钥、URL、命令、环境变量或任意插件名。没有 `tools` 的旧 profile 保持原 patch 和回执元数据布局。

完整 profile 随原 execution plan 冻结，已有批次和重试使用原计划。生产配置保留旧 `dsh-deepseek-flash-high`，回退只须将 `active.dsh` 改回它，影响后续新准备批次。不要修改旧计划、清除失败记录或重新占用同一批任务。

AKTools 在 `output/runtime/aktools-0.1.4` 的独立 Python 3.11 venv，版本为 AKTools 0.1.4、AKShare 1.20.22、MCP 2.3.0。60 项依赖的版本与关键服务源码摘要绑定在 `config/dsh_aktools-0.1.4-r1.lock.json`。新环境按同名 requirements 文件安装；运行期不会联网安装或更新依赖。部署新依赖应使用新 runtime ID 和新锁，不改写这个已评估的 ID。

启用该 runtime 的 profile 在 preflight 和 patch 准备时核锁；缺失或漂移应修复安装或为新批次选择旧 profile，不悄悄加载未测试版本。MCP 服务自身启动失败不终止研究，工具失败继续原有取数路径；单次 MCP 调用上限 90 秒，上游读取超时 20 秒，进程内缓存 60 秒。Python 使用 `-I -B`，不从研究 cwd 或 PYTHONPATH 导入模块。AKTools 的日志 cwd 位于每次尝试的 `dsh-aktools/`，环境沿 DSH 凭据清理逻辑，不传模型密钥。

AKTools 默认最多 100 行、单次上限 1,000 行。完整遍历的终止条件是 `offset + returned_rows >= total_rows`；`truncated` 意为本页不是整张表，尾页仍可能为 true。本轮 2,061 行港股利润表按 1,000/1,000/61 行收齐，无重复。生产提示只解释工具的真实边界，不改变财务或估值口径。

## 日志统计

`scripts/research_dsh_metrics.py` 只读每次尝试的持久化 `session.v4.jsonl`，CLI `events.jsonl` 仅定位主会话，不双计。子代理使用裸 UUID 的目录也纳入；首次失败和 `retry-1` 分别保留。重复事件序号、缺结果、缺 usage、无日志、截断/无效行均留缺口。

Usage 优先取 assistant/message 的实报值，否则读取原生流记录 `record.chunk.usage`，按同 turn/step 的最终样本替换，`llm/retry-started` 开始新的计费尝试。压缩按成功 end 计一次，失败和未结束的尝试另列，不累计 start/summary/end 当作三次压缩。`inputTokens` 为未缓存输入，缓存读/写单独统计。只有已报告的部分可求和；搜索辅助模型和 Search/Fetch 计费记录不完整，费用保持 null，禁止用 0 美元表示未知。

每次 DSH 执行结束写 `runner/dsh-metrics.json`，process 只保存索引/哈希/覆盖情况。统计异常只记录异常类型，不改变任何验收结果，也不输出 prompts、命令正文或工具内容。shell 工具的 `isError=false` 不等于子进程退出成功，另统计 `job/settled` 中非零 exit code。工具耗时之和可重叠，不能当作墙钟时间。

历史回算（只写新的输出，不改历史）：

```sh
python3 scripts/research_dsh_metrics.py \
  --from-date 2026-10-29 --through-date 2026-11-03 \
  --output output/audits/investment/2026-11-03/dsh-metrics-new.json
```

2026-10-29 至 11-03 的 32 次尝试包含 26 成功、6 失败、5 次重试；成功部分的 3,604 个工具调用、148 次搜索、381 次辅助搜索请求、55 次底层命令非零退出，与原审计一致。

## 复现和验收证据

正式评估记录位于 `research/investment/maintenance/2026-11-03/investment-2026-11-03-dsh-plugin-rollout-codex.md`。完整原始输入/响应在本地 `output/dsh-plugin-evaluation/2026-11-03/`，必要摘要、原件及响应哈希保存在同日正式报告的 evidence 中。

- Web A/B：`scripts/research_dsh_web_trial.mjs`，调用安装包导出的真实 provider，密钥仅继承环境。需要显式 package root、manifest 和不存在的输出目录。HTTP 4xx/5xx、空结果不记成功；非空 2xx 仍需另做正文质量审查。驱动冻结输入副本和自身哈希，拒绝越出输出目录的案例 ID。
- AKTools：`scripts/research_aktools_trial.py`，显式 venv Python、manifest 和新输出目录；通过实际 JSON-RPC stdio，不用伪造的工具响应。
- DSH 小样本集成验证不等同完整股票研究 A/B；离线共同验收、共享证据和恢复测试仍按原测试套件验证。
- 日志为观察工具；后续是否扩展 Fetch/浏览器及是否有整篇收益，要以新增实际样本判定，不按本轮单工具速度推定。
