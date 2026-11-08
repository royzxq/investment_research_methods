# 个股调研框架更新结果

## 1. 更新结论

2026-11-08（Asia/Shanghai），generator=codex，full+publish。state_refresh=true、evidence_correction=true、method_change=false、update_needed=no。R22及维护入口已经部署；实际方法stock-two-price-controls-v2-etf-relative-v1来自PR61合并及11/6明确采纳。本文不新增方法。

当前市场研究、变化判定、纠错及adopted handoff按授权发布main；两份canonical/compact观测正文只在本期一个PR中等待人工审核。即使update_needed=no也完成状态/纠错。PR不自动合并、不交易，不夹带维护实现代码或原项目dev提交。

## 2. 受影响模块

|位置|分类|原因与范围|
|---|---|---|
|canonical/compact唯一investment-state JSON|state_refresh|日期/来源换11/8；美债利率、港股二手事实更新，新增官方科创整数、SSE ETF汇总及PBOC隔夜/BLS读数。旧历史数据保留真实日期，精确官方/账户缺口仍null|
|市场与变化报告、handoff|state_refresh|按R22提供两上下文，保留七变量及六机制，不以身份/成交/短期回报改P1/T1|
|R21窗口来源接续|evidence_correction|11/1及11/6-r2/r3误写10/21—23，实际当期10/28—30；撤回错误状态包且supersede，不改旧文、不改当时退出未满足结论|
|公司复评队列|接续，无完成升级|五pending及原触发日保留，恒瑞11/5配对存在但特定事项/方法兼容未验收；不重置168小时冷却|

## 3. 修改说明

经济依据：利率下降改善分母背景，政策操作期限改变影响流动性传导，算力需求增加公司取证线索；这些都不是买入资格的替代。科创周涨后官方整数1253仍低于既有退出线，R21必要条件失败。ETF汇总成交含货币基金，规模未拆价量，申赎及因果流动性unknown；前瞻机会成本未量化。

阈值/动作/例外/解除定义完全沿用已采纳canonical。R21缺完整日历/三日数据未跑真实helper；末日远低于阈值可以否定合取，不能由数据缺口推满足。R2发布会已读但未支持路径回撤，不锁下一次会议；R20滚动同月条件不混月。R6仅实质暴露且原窗口/预案条件满足者受限。

三条compact自包含抽检（假想案例，非行情）：

1. R21：连续三A股交易日各成交1.7万亿、完整两融-149亿元、科创50=1516.2，可退出深化到等待复核；将任一成交改为1.6或两融=-150则失败，缺官方指数unknown。即使退出也不直接恢复买入，原重建路径独立保留。
2. R22：证据充分且同口径原约束B=85、机会成本上限U=80，则最终P1=80；B=72、U=80则P1仍72，不能再连乘U/B。没有可支持的前瞻输入就未量化，T1不随短期跑输机械下调。示例数不是新参数。
3. 控制/R6：无实质事件暴露的公司不因日历冻结；有暴露且处前48小时或缺预案者依原scope受限。事件结束仍须按结果复评；holding-only未知不自动扩展entry/add，真实买入缺证仍限制相应scope。

## 4. 不应过度反应

保留有效估值参数、五折扣、两价、原核心风险约束和独立scope。临时冻结不自动阻止证据充分的价值研究；前瞻缺口不冻结全市场，ETF身份不加价，净值已扣费不再扣，已在利润/倍数/风险计入的影响不重复。没有新增每日全市场研究、公司批次或账户行为。

## 5. 新版框架链接

待审：[canonical](../../../../framework/investment_framework.md)、[compact](../../../../framework/investment_framework_compact.md)。变更限定唯一受限JSON；混排D段、历史方法日期、规则/公式与例外均逐字保留。D段历史事实不作为本周行情，当前有效观察按日期报告与明确采纳handoff。

## 6. 版本变更记录

|正文|旧完整SHA256|拟更新完整SHA256|不变method_sha256|
|---|---|---|---|
|investment_framework.md|`10a8cb94f5288b7340589a469d1f57c71bdf0fc07346a4d2b2ab0185227edab0`|`4e8c0e7e4df1027a5affaad3c7c18263a8cc83bc9448f9a969851729bf154782`|`09a175947d764b73e4822d6be2af80020a392330b5ff1e5af845cd42359a50d4`|
|investment_framework_compact.md|`071ab7d37d6d11b073cdbb0b5de3f6be9445af2ede5519a7264e1b7378831040`|`434a1c84337dc916fbdac23c9b3b02e40e790cf59424c83bd93699548bac0eef`|`f78fc877aa3e3093727dc7b31786ffdcb6d61d6aacd5d5d02286a3ce16c740e8`|


[本期adopted handoff](investment-2026-11-08-handoff.json)绑定的是实际已采纳main两份旧完整正文及其不可变副本，并承接状态纠错。待审观测字节不冒充已合并；仅观测变化方法指纹不变，可兼容接续。未来若有方法实质变化并合并，另建adopted记录绑定实际正文，不改旧proposed记录。

旧状态包撤回不撤回方法正文及其真实合并凭证；supersedes与withdrawn_sources传递，切回旧方法也不能复活错误窗口或10/11错误变化报告。完成验收必须报告/JSON/触发及方法凭证匹配，本期0项升级completed。

## 7. 验证

[完整验证记录](evidence/validation.md)：handoff来源/日期校验及选择通过，错误hash/未来日期按预期拒绝，旧方法选择不复活撤回记录；股票governance通过。离线47项investment测试与12项research_consistency测试全部通过。真实API请求0（缺TUSHARE_TOKEN），网页原文读取另列账本；未做账户/交易验证，未把离线测试当真实行情完整性证明。

## 8. 精简版同步

使用framework-condense及fidelity七项自审，仅同步受影响观测块，不重写其它条目。

1. 有效内容覆盖：固定方法块逐字相同，canonical/compact观测同步；本轮受影响数值/日期/来源字段逐项比对，不声称重证全框架经济有效性。
2. 数值与公式：已有全部方法数字/单位/比较符/AND-OR逐字保留；新观测明确币种、期限、毛额、整数或二手口径，null未填造值。
3. 规则引用：R1—R22与D1—D8无改名/重编，governance检查通过；新增观测来源均指本期账本，非平行方法副本。
4. 自包含执行：本报告§3三例覆盖R21等号与缺口、R22较严约束与缺证、R6实质暴露/scope，未为抽检制造新规则。
5. 副本矛盾：两观测块一致；历史D段按原日期保留，不把其旧“本期”当11/8状态。本次窗口元数据冲突通过撤回和新handoff解决，未静默择一改旧记录。
6. 决策链：数据→Precheck→机制→Gate→估值→Terminal→Price Map→结论对应正文均保留，无新增必办门或断链；本次没有变更顺序。
7. 体积与范围（UTF-8字节与splitlines行数）：
   - investment_framework.md：103231→105401字节，720→784行；增加为8项有来源观测及单位边界，非规则膨胀。
   - investment_framework_compact.md：67525→69695字节，458→522行；增加为8项有来源观测及单位边界，非规则膨胀。

固定方法两指纹不变，观测块外逐字一致。结构检查与三例抽检有明确范围，不等于全部语义/投资有效性证明。
