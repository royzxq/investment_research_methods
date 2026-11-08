# DSH 长正文与上下文证据接续

日期：2026-11-08（Asia/Shanghai）。用户授权集中适配长正文与上下文管理，验证关键证据裁剪/压缩后仍可定位、重读和引用。沿用投研方法、模型、排期和现有补证闭环。

## 决定

增加 `dsh-deepseek-flash-high-context-v1`，叠加 `evidence_context=evidence-context-v1`；只作用于后续新准备批次。旧 profile 及冻结批次不迁移，回退选择 `dsh-deepseek-flash-high-recovery-v1`。适配器冻结插件源码、哈希、证据目录、估值日及本机 Node 解释器；交付回执检查绑定，runner 使用同份冻结实现检查最终暂存报告。没有修改 DSH 安装包或摘要算法，不增加摘要模型调用。

## 原生接入

- 观察 DSH `tools/result` 的最终结果，拒绝/被策略拦下的网页结果不入库。独立完成的补证文档可以在原生 PDF fetch 失败时入库；只读现有恢复原件，不重新下载。自动体检、补证、上下文三插件的组合经过真实 ToolRuntime 离线测试。
- 在 `systemPrompt.context` 注册 required 短定位簿，`system-prompt/assemble` 等待登记队列并刷新；常规可选上下文抑制不能移除它。其内容是研究者标注，不被提高为可信系统事实。
- 注册 find/open/pin/cite/check 五种原生工具，索引和工具变更串行，防止并发写覆盖。重启重新读取持久记录，来源、摘录、标记修订、引用均以内容摘要命名；原件变化或符号链接不静默降级为摘要。

## 投研信息与预算

原始网页响应与文本保存在 `evidence-context/blobs/`；恢复文档引用 `evidence-recovery/` 的清单、原件和页文本。来源 ID 绑定原件和定位文本，evidence_id 绑定来源、页序/范围和摘录哈希。重读核原件与目标文本哈希；PDF保留从1起页序，文本范围沿 JavaScript UTF-16 代码单元。网页原生 HTML 保留 raw_html 身份，解析与全文完整性仍由研究者判断。

关键标记含主体、期间、币种、单位、披露日及支持/反证/未决/拒绝状态；空值不推断。更正保留修订，拒绝证据不能再生成支持引用。短簿小于3500字符、最多6条，优先提醒未决/拒绝，明确另有多少未显示；完整索引可查。单次读默认2400/最多4000字符；每次尝试最多128个来源、512个读取锚点、32个当前关键标记、512个标记修订和512个引用。单文件上限32 MiB，超限明确报错。这些是工程预算，不是投资规则。

来源列表与锚点列表分别分页：仅传 source_id 列该来源锚点，按 evidence_next_offset 传 evidence_offset 续查；传 source_id+query 搜索原文，并按 next_search 的页/范围继续。显示预算不能使后面的锚点失去查询入口。最终审计的 stdin 使用流式 UTF-8 解码，避免中文字符跨管道块时发生误报。

定位簿按尝试保存于 output，依赖原件目录保留；不承诺清理缓存后还能重读，不把它当永久研究档案。当前不自动纳入任意 bash、本地文件、其他 MCP 或 AKTools 表格；分页原有读取/采用凭证不变。

## 引用验收

生成引用时重新校验原文；quote 可省略，提供时须为已读片段中最多500字符的单行逐字引文。返回原URL、PDF页序/文本范围和隐藏引用ID。runner 对最终暂存 Markdown 检查：

1. 标记存在且对应已登记引用；代码块、行内代码和其他 HTML 注释中的示例不算正文引用。
2. 引文、链接和位置与生成的 Markdown 完全相符；引用文件和读取片段哈希仍一致。
3. 已标为 required_citation 且未拒绝的关键证据实际出现；明确不采用的证据须记录理由并取消必引。

这是新 profile 的局部交付检查，失败阻止该次报告发布；不改价格 JSON、投资条件或旧 profile 验收。无引用也无必引项时为 not_exercised，不能报通过。未登记的关键证据、转述是否受原文支持、图表语义、日期有效性与公司事实真实性仍须原流程核验，不能由机械引用检查背书。

最终结果写 `runner/evidence-citations.json`，绑定报告 SHA-256；已有 `dsh-metrics.json` 追加 `evidence_context`，区分打开、主动重读、自动检查、生成引用和最终检查。指标不输出原文/URL/标注理由，也不宣称重新核验所有原件。原 recovery 统计继续保持“研究者声明用途”口径，不追认成独立事实核验。

## 验证策略

用已安装 DSH 0.2.1-rc.2 的真实 ToolResultPruner、Session、TokenMeter 与 BasicCompactionEngine 进行离线组合；只替换文档化的 summarize 钩子为故意丢失数字与定位的确定性摘要。实际执行原生裁剪及 surface 替换，再从短簿/索引重读和引用。该测试没有模型调用，不验证真实模型摘要质量或自发遵循工具的概率。

另用真实 PyMuPDF 提取合成三页 PDF，覆盖页码、空白页、原件篡改和重启；用共享 runner 检查必引漏项、未知引用、正确引用及未启用情况。实际结果与边界见[实施记录](../../research/investment/maintenance/2026-11-08/investment-2026-11-08-dsh-evidence-context-codex.md)。
