# 个股调研框架更新结果

## 1. 更新结论

2026-10-18，generator=codex，full+publish，整包正式修订r2。state_refresh=true、evidence_correction=true、method_change=false，update_needed=no。仅在canonical和compact唯一受限JSON事实块写入11项带日期观测；本期当前状态/纠错已按已采纳方法独立采用，观测正文同步为PR待审，未合并不宣称main已更新。无新方法提案。

## 2. 受影响模块

两份框架的investment-state块：as_of/evidence_cutoff=2026-10-18，source_report指本期market-research-r2。内容为美中价格、CMT、科创50提供商收盘、沪深成交和完整两融。10/16完整两融因深北未返记unknown/null。月度数据observed_at为数据期末，实际10/14披露时间记录在来源账本，不能倒推9/30即可使用。旧D1–D8、文件头和正文中的10/11日期仍指旧文字快照；当前采用事实在本期handoff，不将旧文字当最新读数。

## 3. 修改说明

状态采用依据：PR #45合并方法的实际两份正文冻结；市场研究与变化报告r2通过来源校验。CPI3.7/核心0.3命中既有观察分支但未超过4；PPI出厂5/购进6.9，差1.9；CMT仍五发布日>5；成交/指数与完整两融支持深化维持，R21及原重建未达。方法阈值、逻辑、范围、动作、例外和解除均未编辑。

首次桥接绑定10/11原报告真实旧方法63b3df1，并核查#43/#45合并。旧change-decision的过时有效决策身份被撤回，不能因换方法复活。首份handoff自审有撤回来源正向ref，已留档并由r2显式替代；r2选择和active生命周期检查通过，r1被撤回。五个证券仅pending，无公司研究完成凭证，未发公司批次，不重置七天冷却。

## 4. 不应过度反应

海外业绩不代A/H利润；单日板块上涨/ETF成交不代表承接或净申购；利率回落不是FOMC合取出口；R21退出也不能直接买入。R6按实质暴露和实际过窗结果，R20按最新已公布可核同月滚动，R19按原事件日计时。冻结可估值但P2不能active，所有适用阻断必须逐项解除。真实账户与交易未知。

## 5. 新版框架链接

[canonical](../../../../framework/investment_framework.md)、[compact](../../../../framework/investment_framework_compact.md)。本PR中只有受限观测块变化，未粘贴或重写其它正文。两份状态JSON完全一致。

## 6. 版本变更记录

已采纳输入方法stock-maintenance-v1，合并凭证f1458994fbf9c7413e7fa8d785cc50a38f6bce45。待审观测同步完整哈希如下，方法指纹逐份保持不变：

|文件|旧完整SHA256|待审完整SHA256|方法指纹|
|---|---|---|---|
|investment_framework.md|b26daf1d3cc601e34682effbe46bb88b064190410de94886546fce7a79378a3a|496d51dd9fb42f3b56eb064baf1d2fb2a40fffe0e8ef75182636cd40cd24e170|96dd548640117d9de7377a7193c9f3179f8b65cdadb4d2bd68e062f50832b4ca|
|investment_framework_compact.md|7c588fba94eb81f9629fe22f6266243c31121e44384ec7a1785c330c7231ada8|cef42ee91e39c8181438d3eb506e1965f380b54e495830c26aa2aaec1791921b|1cf307a6af8168fc0375625a6cc30e96398cd75916402f665cd593d7a260631f|

已采用[handoff-r2](investment-2026-10-18-handoff-r2.json)绑定旧已合并方法，而非待审分支；supersedes首份且携带withdrawn_sources。合并后应另建接续绑定实际两份文件正文，不重写本次旧记录冒充已合并。方法指纹相同可继续使用已有状态；无整体旧63b3df1到PR45的方法等价声明。

## 7. 验证

股票governance通过；handoff两版来源哈希校验、r2选择/active生命周期、r1撤回、未来日期拒绝及R21等号/缺口边界通过。787项离线全量运行111.784秒：785项通过、2项因沙箱禁止ps而error；这两项以相同代码在允许进程检查环境定向复跑，2项12.191秒均通过。不能称一次全量无错。详细结果见[evidence/validation.json](evidence/validation.json)。

真实API只调用Tushare交易日历、科创50与margin，三接口成功但10/16margin不完整。公开原始网页已按账本核验；央行正文、完整官方指数、贵金属/美元与期货结算、A/H公司三季报和账户仍有缺口。结构/离线检查不证明金融事实全部正确或投资有效性。

## 8. 精简版同步

按framework-condense七项自审：①块外字节逐字不变，固定五元组覆盖沿用当前完整正文；②所有阈值/公式/逻辑/固定参数均在未改块外；③R1–R21/D1–D8唯一、引用和三个占位符通过治理检查；④三例自包含抽检：R21指数=1516.2且其余严格通过仅回等待，不恢复P2；R3盈利可对冲则三项合取不成立但全面执行参数仍从严；R6无实质暴露不作统一日历冻结，相关过窗需实际影响与其它Gate复核；⑤新JSON相同，旧D文字明确日期，当前状态按最新已采纳handoff；⑥决策链块外原样，未增闸；⑦UTF-8字节/行数如下。

- investment_framework.md: 79996→82653 bytes；463→552行。
- investment_framework_compact.md: 49234→51891 bytes；238→327行。

体积增加来自事实JSON，没有压缩目标。自审确认本次局部同步范围保真，不宣称所有历史方法100%语义等价。没有修改技能/代码，无需新增技能校验或维护实现发布。
