# DSH 取数前后体检补强：实施与验证

日期：2026-11-08（Asia/Shanghai）｜生成端：Codex。

用户授权先集中补强取数体检。本次已在当前 DSH 实际使用的网页与 AKTools 工具入口增加程序检查，并启用新批次配置。投资方法、模型、调度时间、共享事实流程和价格/控制交付合同不变；没有启动正式公司研究或调用新的付费模型、数据 API。

## 实施结果

新增 [research_data_health.mjs](../../../../scripts/research_data_health.mjs)，通过本机 DSH 0.2.1-rc.2 原生工具执行前后钩子运行，而非只在提示词里增加要求。[适配器](../../../../scripts/research_dsh.py)从冻结回执读取估值日，将插件副本和哈希绑定到本次尝试。

| 环节 | 自动检查 | 处理边界 |
|---|---|---|
| 取数前 | URL 结构、接口参数、证券字符串及已知市场、分页整数和单页上限 | 含混证券身份或非法参数在发起请求前拒绝；支持 AKTools 实际提供的负数 offset 和越界夹取 |
| 网页返回 | HTTP 状态、内容结构、空正文、显式截断、疑似导航/脚本空壳 | 空正文/错误状态拒绝该次返回；截断、短 HTML 等提示核验，不把短公告判为无效 |
| 表格返回 | MCP/JSON 包装、文本与结构化值一致性、接口、列、行数、offset、总数、无进展 | 结构冲突拒绝；正常空表明确不能推断无公告、无风险或业务为零 |
| 分页覆盖 | 同接口同参数的已观察位置、重复页、重叠内容变化、总数漂移 | 真正收齐时记 complete_observed；尾页 truncated=true 不妨碍完成，不将单独尾页视为全表 |
| 已验证的财务接口 | 主体一致性、占位符、核心字段缺失、非有限金额、报告期间/披露日期、单位/币种缺口 | 正常零值、负利润保留；不补0、不自动除以100、不猜币种；晚于估值截止的行明确提示排除 |
| 留痕与反馈 | 保存工具返回的 canonical JSON、SHA-256、请求/调用摘要、时间和问题类别 | 保留原值，检查报告与原始返回分开；不是保存 HTTP 传输层原始字节 |

自动拦截对象为 `web_fetch` 和 `mcp__aktools__get_data`。财务细检限 `stock_profit_sheet_by_report_em` 与 `stock_financial_hk_report_em`；其他 AKTools 接口保留通用结构/分页检查，明确业务语义未检查。没有新增 stock-x 依赖。

每次尝试输出至自己的 `data-health/`，主、子代理共用。PTC 子调用除了保留 canonical value，还将检查提示传回后续模型上下文；大响应被其他策略折叠展示不会跳过检查。已有策略的拒绝保持有效，上游原始错误诊断保留。保存失败/超限显式失败，不截断数据后声称取得完整结果。

## 研究判断的边界

三种结果分别为 `rejected`、`review_required`、`mechanical_checks_only`。它们只描述本次取数的机械问题，不证明事实正确，也不自动判断公司可估值、资格、仓位或交易动作。

部分分页或正文截断不要求整篇研究停止。研究者可以使用已经核验的局部片段，同时明确未覆盖范围；缺口只限制相关输入。单位/币种、会计定义、披露时点和正文相关性继续回原文确认。`complete_observed` 只表示本进程观察到了该响应表的全部行，不证明数据新鲜或完整历史披露。

bash/curl、PDF、其他 MCP 与 stock-x 不在自动拦截范围，继续执行 [原始资料获取与核验](../../../../.agents/skills/stock-research/references/data-acquisition.md)。本次同步补充该 reference，并将其中过时的“最终 v2 JSON”措辞改为现行轻量交付合同，没有变更最终 schema。

## 生效与兼容

[生产配置](../../../../config/research_runtime.production.json)的新 active DSH profile 为 `dsh-deepseek-flash-high-health-v1`，增加 `data_health=data-health-v1`；Search API、HTTP、AKTools 版本、主/子模型继续原配置。原 profiles 字段逐项与修改前 HEAD 对比一致，Codex/Claude 选择不变。

本机 launchd 定义仍指向本仓 `deploy/launchd/run_research.sh` 和该生产配置，保持每日05:00；未重装或重载服务。新准备批次采用新 profile，已冻结/在途批次、重试及历史按原计划处理。回退仅须为未来新批次选择原 `dsh-deepseek-flash-high-tools-v1`。没有修改旧回执、报告、latest 或失败记录。

稳定合同与回退细节见 [ADR](../../../../docs/adr/ADR-20261108-dsh-data-health.md)。

## 实际验证

| 验证 | 结果 | 证明范围 |
|---|---|---|
| 全仓离线回归 | **1324 项通过，224.760 秒** | 原执行、共享证据、回执、恢复等合同回归；不调用真实模型 |
| 末次小修后的专项回归 | **43 项 Python 通过** | DSH 适配、配置冻结、源文件篡改、有效回执及 JS 边界检查 |
| Node 专项与真实运行时离线集成 | **18 项通过，0 跳过** | 当前安装 DSH ToolRuntime 的实际前后置钩子、拒绝/提示、原值保留；含旧 Web 试验驱动回归 |
| 历史原始响应回放 | **31 份**：20 份 Web、11 份 AKTools | 本地旧响应的新检查，不是新的联网实测 |
| 当前生产 profile 本机预检 | 通过 | CLI 能力、现有凭据可用性检查、PDF解释器、固定 AKTools 锁与插件源存在；没有发起模型请求 |
| 股票框架结构检查 | 通过 | 只证明结构；框架不是本次修改对象 |
| bundled skill quick_validate | 通过 | 使用本机已有可导入 YAML 的 Python，未安装依赖；不证明技能语义正确 |
| git diff --check | 通过 | 改动空白检查 |

回放结果：12 次原有工具失败仍保留失败，17 次要求核验，2 次仅通过机械检查；成功定位原来六次非空 HTTP 200 的正文截断。港股 2,061 行以 1,000/1,000/61 行三页收齐后记为已观察完整，保留披露日与币种/单位待核提示；正常末页 `truncated=true` 没有误判。A 股历史表中的空字段只标明缺口，未改写数值或据此判经营恶化。

测试还覆盖代码前导零、主体冲突、空数组、合法零/负值、缺单位、未来披露、分页重放/变化、合法负 offset、短公告、原始返回与检查记录绑定、保存目录符号链接和旧 profile 无新插件。一次初版回放误用了不存在的 URL 字段，该结果已排除；最终回放按原冻结 manifest 映射 URL，并显式检查不存在该输入错误。

源文件/测试日志摘要及验证索引见 [validation.json](evidence/dsh-data-health/validation.json)，逐项回放见 [historical-replay.json](evidence/dsh-data-health/historical-replay.json)。完整日志位于 `output/data-health-validation/2026-11-08/`。完整回归之后的最后小修由43项专项及18项Node检查覆盖，没有把先前全回归结果冒充第二次完整重跑。

本次没有新的整篇 DSH 投研实跑，不能声称误判率、研究耗时或投资效果已经改善。实际后续研究仍需查看体检提示是否被正确处理；自动检查的目标是尽早暴露已知错误，并保留可复核材料。
