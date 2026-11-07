# 独立审阅 · 2026-11-08期货周更

审阅时间：2026-11-08T01:18:19.892271+08:00。generator=codex；实际采用基线origin/main949d020af04ba55e68cbeacada91099cc960d104，v3.0 / futures-maintenance/v2。审阅对象为本期明确待采纳的market-research-r2、change-decision-r2、execution-audit-r2、anchors-r2及refresh-r4；原稿和失败记录保留。

结论：下列已核范围无剩余阻断性内容问题。状态刷新yes、证据纠错yes、方法变更no，update_needed仅对应方法变更，现行T/V与核心风控未改。本审阅不证明当前行情、账户、成交或收益已核，也不代替后续origin/main与PR发布验收。

## 内容与边界

- 本进程缺继承TUSHARE_TOKEN，两次采集均认证前失败；partial未当完整快照。五T当前信号均unknown/incomplete，没有把失败或旧10/30 no_signal迁为本期信号。三V缺事前经济锚not_evaluated，当前两腿原料缺失单列。
- 实际用于陈旧拒绝和旧窗核验的冻结原料是10/30，故audit/handoff行情锚使用该历史身份；snapshot.current_market_trade_date/current_market_captured_at及当前价格仍null，每条当前筛选有historical_input_anchor_only/current_screen_not_evaluated依据。未用本期时间冒充原料抓取时刻。
- MA/M/RB三个原机会的opportunity_id、signal_date、registered_at、valid_until逐条与已采纳历史相符。M首稿null登记与显式r2补登记的限定裁决保留19:30:56/10/19，不补数值案、不续窗、不遗漏M。
- 已采纳11/01RB remaining_window标签纠错为expired，原10/23信号、10/25登记、10/27截止和数值计划不变；invalid原证据RB-WINDOW-OLD只作诊断，G3仍fail。MA原expired标签无同类错漏。
- MA10/12真实入场的11/06时间上限已过；10/13真实入场的11/09为另一条件上限，均不覆盖更早SL/逻辑退出。原SL穿越只作条件风险管理，不声称实际成交退出；RB单日high未跨历史参考SL不外推全周未止损。
- 三个V当前有序对精确为MA2701–MA2705、RB2701–RB2703、SR2701–SR2705；准备对单列。没有用单侧仓储成本造对称锚，没有事后冻结或重启旧时钟。anchors/withdrawals空具有无继承有效锚的明确前提。未成案V的exit_rule已为null，未套T跟踪规则。
- M/RB及其余品种底稿的观测日、发布时间、样本、预测和最强反证分开；M10/30库存未写成11/06实时或本周增量。WASDE时区已核，M首次国内场次/T未得保持null；公开公司参数不当用户实收。账户/实际SL/持仓/挂单/收益/最终手数均未知，无伪空仓或收益推论。

## 实测核验

- 独立运行validate_futures_audit.py检查execution-audit-r2，status=valid、errors=[]，仅结构范围。另逐项断言11条记录的unknown/null、原计划时钟、RB纠错、MA两条时间上限、V精确有序对与退出字段，通过。
- refresh-r4与r3逐字段比较：除source_inputs持久路径及revision_note，其余计算/状态/evaluated_at全部相同；4条source_inputs的hash与字节数实际一致。
- 13条共享entry用load_entry逐条核身份/对象并与collect导出字节比较；16组纠错及唯一M原钟冲突均在continuity-reconciliation-r2限定裁决。接续源图264文件无live output依赖。
- M/RB公共manifest36条和其余品种manifest20条原文hash实际核对一致；原绝对path回执不改字节，other-products/source-manifest-r2仅以opaque引用保存。总source-manifest独立遍历438文件通过，初稿、失败refresh、partial和原anchors均opaque保留。
- 读取实际validation.json及两次完整离线日志：首轮1317项45个sandbox socket/ps权限错误保留；第二轮1317项OK/219.131秒。治理30当前锚/277旧ID结构通过。此审阅未重复全套测试，未把离线通过当成真实API成功；实际行情API未通过认证，账户/成交/收益未验证。

## 受审版本

- [2026-11-08-market-research-r2.md](../2026-11-08-market-research-r2.md)：sha256=917022d4a248610496e3d68b3a38be44db243745a150f04c67e8453dff3718b4
- [2026-11-08-change-decision-r2.md](../2026-11-08-change-decision-r2.md)：sha256=30461bf88abd6950a5e824b08f4e56342b5092a5c823923951ebaaba90d8b9d6
- [2026-11-08-execution-audit-r2.md](../2026-11-08-execution-audit-r2.md)：sha256=3a92eda6afdbdacda621c2045bb50ac9629b79f6209c8708fb54dd8082723310

总证据：[source-manifest.json](source-manifest.json)；接续裁决：[continuity-reconciliation-r2.json](continuity-reconciliation-r2.json)；实际验证：[validation.json](validation.json)。最终报告来源图实测记录见下。

最终capture_files实测：503个文件，所有路径/hash引用核验通过，live output依赖0；该结果仅证明受审来源图可持久读取，不证明价格新鲜度或经济有效性。
