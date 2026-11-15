# 个股调研框架更新结果

## 1. 更新结论

研究日2026-11-15，generator=codex。state_refresh=true，evidence_correction=false（继承四项历史撤回），method_change=false，update_needed=no。canonical/compact仅原位受限观测块更新，本期正文为待审PR内容；当前状态已按main实际方法建立独立adopted接续，绑定发布前真实正文。无新方法提案、自动合并、交易或公司批次。

## 2. 受影响模块

|位置|原因与分类|对象范围|摘要|
|---|---|---|---|
|两框架investment-state JSON|state_refresh|A/H市场事实输入|10月物价、11/13行情/CMT/ETF汇总、香港Q3、TSMC营收及缺口|
|日期报告与handoff|state_refresh|有效方法及待复评事项|11/15状态、R22两上下文、当前已部署方法、5pending/0completed|
|固定规则及混排D段|未改|原适用范围|正文块外字节完全保留，包含原日期及解除定义|

## 3. 修改说明

旧块截至11/08，部分精确行情仍停10/30；本期取得真实API但11/13两融不完整。已知历史值保留真实日期；美国CPI最新同比置null，并单列最后已知9月值，避免被当10月读数。新增latest缺口字段不删除作为比较依据的旧值。官方科创50整数1280与精确官方字段null分列。

经济含义：输入成本与长端利率压力加强，政策/需求旁证和治理变化共存；并无新规则动作。R21的“精确三日helper unknown”与“官方末日必要条件否定退出”分开，不虚构全部三日已取得。状态转移、AND/OR、等号、例外、固定参数及P1/T1契约未改。当前方法继续§1.3、§4.1A–D、§6.6三值/资本/唯一计价/DCF/R22。

正反及边界：三日每项齐备且指数恰1516.2可过R21，只降等待复核；成交恰1.6或两融恰-150不通过；缺一个关键值不能判满足。ETF短期跑赢和政策额度不能自动上调个股价格。新方法旧冻结不声明全局等价；旧pending时钟与历史方法保留，未来完成按适用合同复核。

## 4. 不应过度反应

不把未知当损失成立，不用最新股价拟合PE/WACC/增长或终值，不统一加折扣，不把ETF身份或政策操作当基本面价值。已有吸收的损失按§4.1B去重；分红按基础估值进入一次，机会成本门槛不重复相乘。临时市场/事件限制保留实质适用范围；可估值与买入资格分判，事实足够可给冻结观察价位。无全市场新增冻结、无每日扫描、无168小时冷却重置。

## 5. 新版框架链接

- [canonical](../../../../framework/investment_framework.md)
- [compact](../../../../framework/investment_framework_compact.md)
- [本期元研究](investment-2026-11-15-market-research.md)、[变化检测](investment-2026-11-15-change-decision.md)、[已采用状态handoff](investment-2026-11-15-handoff.json)

仅JSON观测块为本次待审正文；未修改方法头“本地dev”历史采纳文字，当前远端部署事实由adoption-review及新handoff给出。

## 6. 版本变更记录

已采纳方法身份：stock-two-price-controls-v2-etf-relative-v1-dividend-v1-capital-v1-dcf-v1。基线origin/main a690373cef83d2ff624ad7f74b4c14c7ccca5214，PR63/64/65/66已合并，deployment_pending=false。本期handoff状态adopted、首修订，supersedes11/14；本期观测正文仍待审，合并后须另建接续绑定实际正文，不重写本次冻结来源。

|副本|旧正文SHA256|待审正文SHA256|方法指纹（不变）|
|---|---|---|---|
|canonical|61a118fad095da7f028a1a7002e9354e38f3aed7573981db8b2d2c8561012d7f|0a9f32372bc5de6f81ec406655b5c9a7f3f2fef3dbbe3ba5f1d35b8402b4a6b7|6b90ff1a149123e882bb27524629fa7dd2645070871fe7ae94e46e045af3e52b|
|compact|191d73ab2e9d889159b23f64c7a0480fcec3f900f5d556c6cbd87dcf1e35f6ee|5bdfff9838f397aac736919ba8710c4a29f580d1f0ee0351aafa7b4ab1d80ec1|8b75958d5facf48e1e464423b3781191fa800d31b5f02bdbcd28c67346048761|

待复评仍为SZ-300308/SZ-300502（9/24）、SH-600276/HK-01276（9/29）、HK-09926（10/05）。恒瑞A已有11/05配对，不代表Novo事项及当前方法验收已完成。无completed或账户执行。四项withdrawn_sources继承，旧方法回切防复活检查通过。

## 7. 验证

见[validation.md](evidence/validation.md)及[机器检查回执](evidence/verification-results.json)：handoff哈希、日期、选择、生命周期、旧来源防复活通过；篡改/未来证据拒绝通过；R21严格/含等号/缺值边界通过；股票governance通过；142项相关离线回归通过。首次系统解释器3项夹具导入错误已定位为第三方tests包遮蔽，切Conda复跑通过，未改生产/测试。七次真实Tushare调用成功，但缺口仍保留。未运行全仓/账户API/收益有效性验证。

## 8. 精简版同步

使用framework-condense定向保真同步两份同一JSON块，七项自审：

1. 有效内容覆盖：受影响观测42项两份完全相同；固定规则、例外、退出及未改混排D段用块外字节相同比对保护，不声称重新证明所有历史语义。
2. 数值公式：新增值按原始资料/单位换算，原比较符、AND/OR与公式在块外保持；历史9月值不删除，最新10月缺口显式null。
3. 规则引用：R/D稳定ID和章节映射未改，governance无缺失/重复/悬空；新report路径存在。
4. 自包含抽检：仅凭compact的R21判等号及unknown、R22取min(B,U)与无前瞻边界、经济唯一计价不重复折扣三例，均与canonical适用定义一致；例子不是新数值规则。
5. 副本矛盾：两JSON完全一致；真实官方整数与供应商精确值不同字段并存，未静默替换。
6. 决策链：数据契约→Precheck→机制→Gate→估值→Terminal→Price Map全部块外字节保留；没有因观测增加交易许可。
7. 体积范围：下表UTF-8 bytes及splitlines口径。增长来自10项事实/缺口，不设压缩比例；compact未增加canonical之外门槛。完整方法指纹不变，结构通过不等于100%语义/收益证明。

|副本|bytes before→after|lines before→after|
|---|---|---|
|canonical|124671 → 127456|876 → 956|
|compact|83115 → 85900|562 → 642|
