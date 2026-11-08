# DSH 取数前后体检

日期：2026-11-08（Asia/Shanghai）。用户授权集中补强取数体检；实施范围是数据工程，不改变投资方法、模型、调度、共享事实和最终交付合同。

## 决定

为新准备的 DSH 研究启用 `dsh-deepseek-flash-high-health-v1`，工具配置沿用 Search API、HTTP 和固定 AKTools，增加 `data_health=data-health-v1`。旧 profile 完整保留；冻结 execution plan 和旧尝试不追补。回退通过选择旧 `dsh-deepseek-flash-high-tools-v1` 影响后续新批次，不修改旧失败记录或重占任务。

`scripts/research_data_health.mjs` 使用本机 DSH 0.2.1-rc.2 的原生 `tools/pre-execute` / `tools/post-execute` 接口，只检查 `web_fetch` 与 `mcp__aktools__get_data`。全局注册覆盖根/子代理调用；PTC 子调用将相同提示作为工具来源上下文送回模型，不改写 canonical value。其他策略的拒绝保持有效，展示折叠不跳过检查；若其他策略替换 canonical value，则保留其裁决，不冒充已检查替换值。

## 检查语义

- 前置：网页 URL 结构；接口/参数类型、证券字符串与已知市场、分页整数及单次上限。按固定 AKTools 实现支持负数 offset 和越界夹取，不创造另一套分页规则。
- 网页返回：HTTP 状态、内容类型、空正文、显式截断；保守检查去除脚本/导航后的可见正文。短 HTML 和疑似空壳只提示核验，不能凭长度证明公告无效或正文完整。
- 表格返回：JSON/MCP 包装、文本与结构化结果一致性、接口身份、列与行数、请求和返回 offset、空结果、无进展、重复页/重叠变化及总数漂移。已取得范围按同接口和同参数汇总，非按 `truncated` 是否为 false 判断；覆盖只限当前进程实际返回的表，不等于全历史或查询条件之外的覆盖。
- 财务细检只覆盖已验证过的 `stock_profit_sheet_by_report_em` 与 `stock_financial_hk_report_em`：证券主体、占位/缺失、金额非有限值、报告期、披露日、单位及币种缺口。其他接口只做通用结构/分页检查并明确语义未检验。缺单位不自动换算，缺值不补0，负利润和零值保留。
- `rejected` 拒绝这次机械错误的返回；`review_required` 提示部分覆盖或待核口径；`mechanical_checks_only` 只表示没发现上述机械异常。任何状态都不是事实核验通过，不直接改变 P1/T1 或 entry/add/holding。已可靠核验的局部片段可以使用，缺口只约束受影响输入。

## 留痕与兼容

每次尝试在 `data-health/` 保存唯一命名的 `.raw.json` 与 `.check.json`，记录实际返回、SHA-256、请求/调用摘要、抓取时刻、估值截止和问题类别。原始请求仍在既有 DSH session；不会把模型密钥、环境变量、认证头或完整提示词加入检查记录。上游错误保留原工具诊断，不当作有效数据存档。

原始返回保持原值；程序不会替模型转换单位、修正股本、裁决会计定义或把“无数据”改成业务结论。单次原始返回保存上限16 MiB，超限/保存失败显式失败，不截断后宣称完整；覆盖跟踪有资源上限，超限返回 unknown。检查文件不是新最终研究 schema，不写入价格地图或既有成功封口。

适配器从已有冻结回执 schema 读取估值日，将插件源复制到尝试目录并写入 runtime 哈希；交付时校验该副本。旧 v1/v2 runtime 无新字段时沿原分支，不能用新策略重新解释旧交付。新代码是运行时配置扩展，不迁移已冻结批次。

本机 launchd 定义仍指向本仓和原生产配置，05:00 排期保留；没有重装或重载服务，没有触发正式研究。新准备批次选择新 profile，已准备/在途批次继续旧配置。

## 验证边界

用合成边界用例、安装版本的真实 ToolRuntime 离线集成和已有原始响应回放验证；完整结果见 [实施记录](../../research/investment/maintenance/2026-11-08/investment-2026-11-08-dsh-data-health-codex.md)。没有调用新的付费模型或数据 API，不把测试通过当作研究质量已得到收益验证。

bash/curl、PDF、其它 MCP、stock-x 仍不在自动拦截范围；继续按 [取证规范](../../.agents/skills/stock-research/references/data-acquisition.md)执行原文、日期、单位及来源核验。HTML 语义、单位定义、公告真实性和报告假设始终需要研究者复核。
