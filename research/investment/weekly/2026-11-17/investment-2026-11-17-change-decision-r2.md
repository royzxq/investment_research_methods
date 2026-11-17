# 股票框架变化裁决（r2）

日期：2026-11-17，Asia/Shanghai；generator=codex。

- 分类：method_change=true；state_refresh=false；evidence_correction=false；update_needed=true。
- 采纳：用户先认可独立红利方案，继而要求review并将原股票框架红利部分实际拆出。该请求授权本独立worktree的修订与兼容性验证；只作本地adopted，不授权推送、合并、生产部署或交易。
- KEY_VARIABLE_CHANGES：没有新增市场变量。变化是主策略适用范围、红利专题归属、R9迁出索引及旧快照识别；完整方法由六文件哈希绑定。
- UPDATE_FOCUS：移除原框架的红利三值门槛/底仓映射/强制分红预测DDM；将专用公式移入HD4A，将拥挤和利差定位移入HD6；共同资本分配一致性保留。
- DO_NOT_OVERREACT_ITEMS：公司分红不代表自动走红利；缺国债不等于公司失败；不自动解除旧scope控制；不改变现有行情或5项待复评；不采用文章固定交易阈值。

定义、经济理由、正反/边界案例、作用范围及兼容影响见[适配报告](investment-2026-11-17-adaption-report-r2.md)。旧六文件v2没有新范围标记时照旧执行，代码可恢复不代表新旧方法等价。原JSON/审计/控制合同不变。r2接续首版及其所有pending、withdrawn与历史日期，不新增公司完成断言。

本轮1430项离线回归、治理、4项skill结构、迁移保真与既有实际快照检查通过；首次沙箱端口/ps错误及获准复跑情况见验证记录。无真实市场API重取、无生产发布，无收益有效性结论。
