# 期货数据与执行协议 v3.0

日期：2026-10-11（Asia/Shanghai）。方法、阈值与池范围以[canonical](futures_framework.md)为准；本文件只定义取证、输入交接及工具边界。默认`research_mode=public_data`，研究方先完成具体计划，再核账户。旧A–H、分位评分与D系列字段不作为v3必填。

## 1. 取数与频率

周度更新产业假设与最多两份计划；模型定义和参数不随行情自动修改。机械信号在交易日收盘后和拟入场前刷新。实际未运行、失败或数据陈旧时说明监测空窗，不能声称周更覆盖了2交易日内所有信号，也不能延长过期信号。未触发可先列条件观察方案，状态仍no_signal。工具不执行交易。

运行合同为`futures-maintenance/v2`：状态刷新、证据纠错、方法变更分别记录；`update_needed`只指方法变更。完整周更及轻量刷新按用户/定时任务已有授权取数，没有授权时只验已有输入并披露缺口。先读真实行情日、交易日历和脚本版本，后研究；数据不可用不是no_signal。`futures_refresh.py --fetch`在隔离目录调用既有取数脚本，不覆盖同日正式快照，冻结所用原料及哈希。默认复算五品种T；V没有事前冻结的有效经济锚只记未评估，不从历史分位造锚。具体CLI、输出和发布前检查只维护在[刷新与接续](../.agents/skills/futures-weekly-review/references/refresh-and-handoff.md)。

日频先检查全部已知存量计划/持仓的事件、反证、止损与期限，再处理至多两个新机会；没有机械新信号也要完成相关存量检查。研究方在周更维护有公开经济依据的 V 观察锚及未来适用修订，日频核失效证据；没有依据记录研究缺口，不强制造锚。锚只须早于信号形成，同日用独立时序证据核验；有序合约对、底层原料和锚必须一致。旧计划独立核日历及行情覆盖，不因本轮主合约换月丢失，也不以入场到期推断持仓已退出。

按[环境文档](../docs/context/environment.md)使用可用Python，继承`TUSHARE_TOKEN`，不输出密钥：

```sh
/Users/xinquanzhou/miniconda3/bin/python3 scripts/future_data.py --as-of YYYYMMDD
```

正式快照在`research/futures/snapshots/<AS_OF>-data-snapshot.txt`，末行“快照完成”才算写入完整；`.partial`不是完成。默认拒绝覆盖，同日复跑按现有产物和用户授权选择隔离输出，不以文件名证明行情有效。`--no-snapshot`只打印，`--legacy-v2`额外输出历史方法模块，不进入v3准入。

v1.18.1默认输出v3 T行情输入、V两腿结算原料，机器包位于`output/cache/futures/v3_research_inputs_<AS_OF>.json`（实际OUTDIR以脚本为准）；是可重建中间文件，正式报告须保存所用原料、来源引用或可追溯产物，不能只留将来会失效的缓存指针。研究阶段按文件完成标记、行情日及每字段状态读取，发布流程仍遵守入口的已提交快照要求。v1.16快照只作历史原料，不因格式可读就当成v3完整输入。

Tushare 行情来源必须保存从 API 返回行核验的确切 `ts_code`，同时核对请求合约及交易所后缀；不得从外层计划标签补造来源身份。采集器逐行验证响应，在缓存复用时复核响应列与来源字段，核验完成后标注 `identity_basis=fut_daily_response_ts_code`；T 包和 V 两腿分别透传真实代码及该来源标记。刷新器要求来源有此核验声明，拒绝缺失或冲突的身份；行内代码用于一致性核对，不要求每行重复来源标记。旧 T 包缺此字段，须用可核验身份的原始响应重建或重新取数，不能只补一个期望合约名。旧 v1.18 的 V 来源曾以请求码填入 ts_code，其存在不证明返回行身份已核验；历史输出保留，按实际来源重新核对后再作当前价格依据。

`as_of_date`研究日、`market_trade_date`完整行情日、实际`fetched_at`分列；交易所和来源随原料保留。18:00等取数截止只是避免未完成日线的保护，不证明最终结算已正式发布。所有交易日/事件窗口以真实交易所日历与夜盘归属为准，降级的普通工作日日历不能给v3信号或计划有效期。数据商日历保留其实际交易所来源；如采用SSE日历作日线机械筛查，必须明示，不能据此声称已核期交所夜盘、临时休市或真实入场时刻；执行前仍须核具体期交所日历。

## 2. 必要证据与可选背景

| 输入 | v3用途 | 缺项归属 |
|---|---|---|
| T真实合约61根连续完整close/high/low，交易日历 | prior20突破、固定Wilder ATR及波动预算；不读settle回退或旧px | 原始获取/计算，非用户定义 |
| V确切近远腿同日settle与日历 | 3日价格确认、61日价差变动波动；不拼接换月 | 原始获取/计算 |
| 合约最后交易日、各腿20日均量、规格/tick、当前报价 | G1期限/流动性、G3成本、G4执行 | 研究方核有效规则与报价 |
| 当前独立产业事实及最强反证 | G2；只要求实际逻辑依赖的字段 | research取证与论证 |
| V经济锚、计算/假设、来源日、适用月份/截止、收敛与失效 | G2/G3；不是历史分位自动生成 | research，不交给用户猜目标 |
| 事件时区/国内T、公开交易规则、压力情景和双腿方案 | G4；仅实际相关事件 | research |
| 权益、持仓挂单、资金、账户专属保证金/费用/限额 | G5/G6；当日实际快照 | user提供后研究方计算 |

M按“大豆到港/库存→压榨→粕库存/提货/基差”取最低可解释链；RB按“同口径螺纹产量→厂库社库→表需/成交→相应现货”取证。不能把大豆紧直接等于粕紧、五大材库存当螺纹库存、减产去库当需求改善。月度/旬度统计可作适用背景，不伪造周度或交割地基差。

来源记录原发布者、链接、观察期、发布时间、单位、地域/样本及比较期。搜索摘要不能充作已读原文；可信公开转引标明原源及口径限制，不声称核过未读原表。不同日期不是同一观察值冲突；同对象/日/口径矛盾才列conflicting。预期尚未发布须给官方安排。强因果计划依赖的专业数据长期不可得则research_only；增强背景缺失不进necessary unknown、不扩成全池冻结。

## 3. 数值工具接口

工具状态`valid/blocked/incomplete/input_error`描述该工具范围，**不等于候选的ready**。输出`execution_permission=not_evaluated`；产业因果、来源真实、发布时间、实际成交和G1–G6须另核。工具核可计算边界，规则出处是canonical。

### 3.1 行情与计划：futures_strategy.py

```sh
python3 scripts/futures_strategy.py trend-inputs --input market.json
python3 scripts/futures_strategy.py reversion-inputs --input market.json
python3 scripts/futures_strategy.py validate-plan --input plan-request.json
```

`--input -`可读stdin；不联网。合法日期为YYYY-MM-DD或YYYYMMDD，`trading_dates`必须有序唯一，覆盖原始历史、两日入场窗与拟退出日。

| 入口 | JSON输入 |
|---|---|
| trend-inputs | `contract, as_of_date, trading_dates, records`；每行`trade_date, close, high, low`，可带contract/is_complete，真实合约不能混入其他腿 |
| reversion-inputs | `near_contract, far_contract, anchor_low, anchor_high, as_of_date, trading_dates, records`；每行必须带同对`near_contract,far_contract,trade_date,near_settle,far_settle` |
| validate-plan | `rule_version:"v3.0", strategy:"trend"或"economic_reversion", market:<上面输入>, plan:<下面字段>` |

共同plan字段：`side,entry,entry_date,latest_exit_date,price_unit:"CNY/tonne",multiplier,tick_value,round_trip_fees`；`tick_value`为人民币/手tick，`round_trip_fees`为T一手或V一组两腿开平合计，滑点由`round_trip_slippage`显式输入或使用canonical最低预算。工具内规格匹配只是支持范围，不替代当前交易所核验。

T：显式`targets:null`，`exit_rule:"initial_2atr_and_prior10_channel_tighten_only_max20_sessions"`。helper返回`stop,entry_range,signal_date,valid_until,latest_exit_date,risk_unit`。可提交更窄entry_range和stop供一致性校验；入场仍在突破侧，范围与0.5ATR限制取交集按tick向内，SL向外取整；不得给伪TP。`prior10_channel_stop`是信号日之前的参考通道，不是后续持仓日自动更新的止损；持有时用最近10完整日重新计算，下一时段生效。

V：`leg_ratio:[1,1],stop,entry_range,convergence_sessions`，及`economic_anchor_basis,convergence_mechanism,invalidation_basis,economic_evidence_refs`。范围可单点，整个范围均应满足价位顺序与最差点净R；`convergence_sessions`与可持有窗匹配。helper输出targets、选定Entry的`reward_risk`及全区间最差`entry_range_min_reward_risk`；审计`targets`对应targets，`net_R`必须取全区间最差值（选定Entry另可记selected_entry_net_R），经济锚另记`anchor_band={low,high,source,as_of_date}`、有效截止与假设。非空说明仅证明有文字，不能证明经济锚成立。

工具重算价格信号和计划日期；已提交signal_date/valid_until若与重算矛盾则拒绝。`signal=triggered`只是行情条件，不代表独立产业证据、当前登记时点及剩余有效期已核。当前T重评可使用生效前已完成行情，保留原价格信号日，不能延长窗口；具体时间边界取canonical。T/V手续费、tick、真实Entry、SL与计划版本都须留痕；实际成交变化后重算，不能拿原计划风险继续报手数。

### 3.2 账户容量：futures_risk.py size-v3

```sh
python3 scripts/futures_risk.py size-v3 --input risk-request.json
```

输入：`rule_version:"v3.0",equity,risk_unit,regime`（normal/low_exposure）、`open_position_risks,reserved_order_risks,existing_trade_risk`、`position_snapshot_verified,position_snapshot_as_of,sizing_as_of`、`factors,factors_complete`、`margin_capacity_lots,position_limit_capacity_lots,execution_capacity_lots,hard_vetoes`。

`factors`只接受`strategy,market_risk,exchange_buffer`及canonical固定取值；不得混旧D系列，不能把该字段齐全当作其事实已核。各风险列表是人民币金额，来自真实持仓/未撤单；没有账户时不要调用示例空列表伪造空仓。

`stress_capacity_applicable,weekend_capacity_applicable`为显式布尔；适用时对应`stress_capacity_lots,weekend_capacity_lots`须为可新增整数≥0，不适用则容量显式null。执行容量必填整数。未知或未核适用性保留final_lots=null，已核0为阻断；所有硬容量与风险手数取最小，不能只报告risk_lots。容量须保留金额/规则/报价依据，不能随意填一个大数。预算与取整只由helper计算，不在报告另抄一套实现。

本工具只核输入数值与当日时间关系，不连接真实账户，也不能验证保证金/限仓来源、压力场景或挂单是否真的已撤。账户更新、报价/事件变化后重算；G1–G4已齐且仅账户未知为awaiting_account，其他必要未知仍incomplete。

## 4. 审计、前瞻轨迹及历史兼容

输出使用[共享schema 3模板](../projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md)。当前v3仍是schema 3，历史schema 2/3按其当时框架解释；不因schema相同沿用旧A–H许可。候选使用trend/economic_reversion、G1–G6和五种状态，数据可行性分列。

跨期先用`futures_handoff.py`按市场报告/执行审计类型读取明确采纳的路径、哈希、纠错范围与方法版本；审计单独更新不遮蔽前期市场基线，不按最大`-rN`或修改时间选稿。v2 兼容性核有效规则与 strategy/risk 计算依赖，完整文件哈希另留溯源；纯标题/维护说明不自动重置计划。v1 缺依赖身份，须核登记时原件并显式留档迁移，否则仅供历史事实重评。published 消费核当前 HEAD 已提交内容，编排器另核实际 origin/main；损坏不静默回退。

日频与周更都通过`futures_continuity.py`读写同一本地持续采纳存储，冻结引用材料并接续原 ID、原登记/期限、累积纠错及 V 锚/撤回。源 worktree 删除不应丢失这些独有材料；共享存储不作为可丢弃缓存，也不算 Git 发布。候选兼容仍须当前行情、事件与账户重评；历史不兼容记录只作为待重评事实。周更将实际使用的共享材料冻结到正式证据后按已有授权发布，状态引用 PR 未合并不阻断已采纳日志接续。没有对应采纳记录才按严格正式名发现并披露缺口。

每个necessary unknown写`gap.kind/owner/next_action/due_at`：definition/plan归research，calculation归data_pipeline，account归user，not_published归publisher并附正式发布时间证据。已知fail与unknown同时保留；only_blocker须完整核验。无账户必须null而不是0，不推断实际成交/减仓。

v3计划保存在candidate.plan，按opportunity_id前瞻冻结并逐次追加路径。`signal_date`是原价格日，`evaluated_at/registered_at`为当前真实带时区时间，允许执行时段须晚于登记且仍在原有效期；三者不混用，V锚仍须信号前冻结。`shadow_plans=[]`、`performance_status=not_automated`；旧price_evidence固定目标引擎只结算v2历史，不支持v3 T跟踪退出，不能用旧输出当新策略绩效。没有冻结计划/后续路径、或日线无法还原盘中/双腿成交时，收益/避免亏损/错失盈利保持null。

`seasonal_plan.py`、`futures_risk.py validate-a/size`、旧precheck_2atr与D8属于legacy_v2_only；只为历史复现保留。当前趋势不能用含当日H20、旧settle→close回退、旧B窗口或旧评分变相过门。重构前报告/快照不改写；方法、事件和账户不从旧文本续成当前事实。

## 5. 检查与来源入口

```sh
python3 scripts/futures_framework_governance.py --check
python3 scripts/validate_futures_audit.py --input <审计报告.md>
python3 -m unittest discover -s tests -v
```

检查结果须区分结构、离线合成样本、真实API与收益检验。治理脚本核30个当前锚和277个旧ID迁移覆盖，不证明全部语义；单元测试不证明策略可盈利或行情可获取。10/11 v1.18 已有真实 API 取数记录，具体覆盖见[实施报告](../research/futures/maintenance/2026-10-11/2026-10-11-weekly-update-mechanism-implementation.md)；此前维护修复另用冻结原料复跑；v1.18.1 的来源身份修复单独验证，不将旧 API 记录或离线样本写成新版本联网验证。遇数据缺项保留错误与可执行补件动作。

[大商所](https://www.dce.com.cn/)、[郑商所](https://www.czce.com.cn/)、[上期所](https://www.shfe.com.cn/)提供交易与合约规则入口；[USDA WASDE](https://www.usda.gov/about-usda/general-information/staff-offices/office-chief-economist/commodity-markets/wasde-report)、农业农村部CASDE、统计局等提供适用产业背景。入口存在不证明本期已取到数据；不得把宏观统计直接代替具体交割品级现货。
