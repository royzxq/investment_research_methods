# 元框架变化检测结果

## 0. 上期预备观察项复核

generator=codex；AS_OF_DATE=2026-10-25，Asia/Shanghai；统一 revision=2。先核采纳、再核事实，不将触发等同研究完成。

| 观察项/规则身份 | 截至本期证据与判定 | 接续及完成凭证 |
|---|---|---|
| D5 深化 / R21 对称退出：已采纳 | 最新同一组10/21–23，成交1.429344/1.528708/1.956258万亿；完整两融日差-12.15/-234.39/null亿。科创50供应商收盘1343.28/1305.87/1345.51，交易所原件缺。前两日量能失败，R21 not_triggered；原>2万亿重建not_triggered。D5深化triggered/延续 | 候选池买入限制及存量加仓暂停继续；市场研究不是逐股完成，账户null |
| UST十年五日>5%：已采纳 | 最新五发布日10/19–23为5.15/5.12/5.13/4.96/5.00%，本窗口not_triggered，等于5.00也不算>5；30年10/23为5.33%，未超过旧5.60锚 | 旧触发未自动关闭；不能据本周未再触发，抹去受暴露公司的历史复评义务 |
| CPI / FOMC出口：已采纳R2/R3/R18/R6 | 9月CPI3.7%、核心环比0.3%，仍命中原观察分支；总同比>4%分支not_triggered。10/27–28 FOMC尚未来临，路径出口unknown | 不以利率水位变化代替“不加且官方路径回撤”；只对实质暴露公司核48h时点，不提前冻结全市场 |
| 内需解除R20：已采纳滚动定义 | 10/19公布9月全口径社零+1.1%，已知未>2%；同月单月贷款同比官方原文仍缺 | 两项合取明确not_triggered，不再把整个合取写unknown；贷款子项仍null，下一已公布同月数据继续滚动 |
| 成本/供给R14/R15/R17：已采纳 | PPI购进6.9/出厂5.0，差1.9pp；EIA新数据是现货，不能作ICE同合约结算 | 油价新升降档unknown；上游85美元与中下游130美元压力场景保留；黄金/美元待补，不用即时边栏触发 |
| 海外AI与A/H盈利链：已采纳R7/R8 | TSMC Q3仍为已核锚；本周Meta资本开支指引下限上调、FCF为负；Tesla最低capex表述下移；A/H订单同步变化未核 | 外部capex分化不等于国内订单全面证伪或全部无风险；只生成适用公司定向复核线索 |
| 政策第二环R19：已采纳 | 10/20科技金融意见、药监AI会议仍为方向/机制；具体上市公司预算/中标/回款未核 | 原9/15、9/18事件的4–8周时钟不重置；新文件按自身事件与暴露记录 |
| S.5548 / BD：已采纳历史触发 | 两家光模块命名风险最新立法行动unknown；恒瑞交割/入账及康方实际权利仍待自身凭证，其他药企新交割不代替 | SZ-300308、SZ-300502、SH-600276、HK-01276、HK-09926 五项pending，completed=0 |

## 1. 基本信息

当前方法为实际已合并的 `stock-two-price-controls-v2`，来自PR #50 merge `6f797ed9223225b68b97db7f7dc9e2cc1c44ab43` 和PR #51 merge `346caada9172b4346c6b9246cb66978b06024ba4`。初始发布基线 `origin/main=c9ce8d8af2f5a61bb0471e1ccfd32b2e1501316f`；入口/helper已在此基线部署，deployment_status=deployed。不夹带主目录本地提交或维护代码。

canonical SHA256 `773677164aee09f006d80afda8e7484f00b05a489061903754b7f76ffec78ed7`，compact `57d9a8e4530e32e53a5d06ab80dc7244d3dc67fd28d95951890dc68c25453ea2`；实际两份正文见[冻结方法](evidence/investment-2026-10-25-handoff-r2-methods/investment_framework.md)。完整元研究为[本期报告](investment-2026-10-25-market-research-r2.md)。[上期研究](../2026-10-18/investment-2026-10-18-market-research-r2.md)及[上期变化](../2026-10-18/investment-2026-10-18-change-decision-r2.md)只作为历史比较，确切哈希在本期handoff；不将不兼容旧handoff当当前采纳来源。

PR #48已合并，只改变事实观测块，不改变当时方法指纹；随后#50/#51实质改变两价与控制生命周期。helper初选null有明确原因；本期按现行方法重新核验，建立新adopted接续，并承接历史pending与撤回。详见[采纳审查](evidence/adoption-review.md)。框架内“未推送/隔离未替换”等文字按其历史日期阅读，不能推翻真实合并凭证。

## 2. 总结论

- state_refresh=true：刷新行情、完整两融、利率/社零、海外财报、BD进展及事件日历；R21与内需解除均未达。
- evidence_correction=true：纠正上期方法/状态被误当当前有效接续的风险；最近五日>5%现在时改为不满足，旧历史触发保留；社零由unknown补为1.1%，合取结果改为明确不满足。撤回与supersedes不因新方法消失，逐股完成仍须配对。
- method_change=false，update_needed=no，update_level=none：本期没有新增方法提案或新阈值。#50/#51是已单独完成采纳的跨期输入变化，已说明实质影响，不能宣称与旧方法等价；不是本次待审建议，也不重复发布其实现。
- 明确采用本期独立状态/纠错handoff，绑定当前已合并方法；canonical/compact仅同步唯一受限事实JSON，统一一个观测PR待人工审阅。PR未合并不阻断日志/状态采纳；任何新正文哈希不冒充先前已采纳。

## 3. 新旧七变量比较表

| 变量 | 10/18历史证据 | 10/25当前证据/研究含义 | 类型/级别 |
|---|---|---|---|
| MAIN_CONTRADICTION | 分母/成本与缩量、杠杆偿还，外部盈利待传导 | 利率边际缓和与周五反弹并存，但社零不足、承接退出未达；海外capex方向分化须穿透订单 | state_refresh / 重要 |
| DOMINANT_RETURN_DRIVERS | 盈利兑现与供给/政策分化为研究优先，市场实现归因null | 盈利质量仍优先；Meta现金流/支出与Tesla最低支出表述分化，BD分公司交割进度不同；实现归因仍null | state_refresh / 重要 |
| KEY_CONSTRAINTS | 五日CMT全>5%；9月社零/贷款未知；R21失败 | 最新五日不再全>5%；社零1.1%，内需合取失败；10/22完整两融再减234.39亿；R21仍失败 | state_refresh / 重要 |
| PRIORITY_MECHANISMS | 六机制既有高/中高/中 | 六类、权重和验证链不改，按现行两价与scope控制消费 | 输入接续；无新方法 |
| FRAGILE_NARRATIVE | 外部利率回落+海外业绩+政策=承接完成 | 周五放量反弹/海外支出总量/BD总金额直接被当A/H利润和解冻 | state_refresh / 重要 |
| TOP_MISTAKE_TO_AVOID | 触发当完成、代理当真值、旧方法当现行 | 把已合并新方法误作待部署；把不再新增触发当旧风险已解除；把capex下限变化当精确砍单 | evidence_correction / 重要 |
| PRECHECK_ITEMS | FOMC、同月内需、量能两融、逐股凭证 | FOMC合取出口、最新三日完整同口径状态、A/H正式财报和合同/回款与全部独立主张解除证据 | state_refresh / 重要 |

## 4. 重要变化项

| old_value → new_value | change_direction / kind / importance_level | research_meaning / downstream_impact |
|---|---|---|
| 最近五日10年CMT全>5% → 含4.96%及5.00%，五日条件false | 利率水位缓和；state_refresh；重要 | 长久期分母压力有边际改善，未满足FOMC出口；历史复评不自动完成，个股盈利对冲与R3合取照常 |
| 9月社零unknown → +1.1%，贷款子项unknown | 证据补齐且解除失败；state_refresh；重要 | 收入端内需假设从严不变，不能换成非汽车3.9%；贷款缺口不补造，也不把整个AND误写未知 |
| 10/16成交1.5554万亿、完整两融止10/15 → 10/23成交1.9563万亿，完整两融止10/22 | 周五量能改善、连续条件仍失败；state_refresh；重要 | 放量反弹不是R21/原重建通过，买入/加仓受对应scope约束，非清仓全部持仓 |
| 只有上期TSMC外部锚 → Meta与Tesla本周原始披露分化 | 新海外验证；state_refresh；重要 | 资本支出方向、利润特殊项与FCF分层，A/H客户订单/OCF未核前不宣称脱钩已证伪 |
| 上期旧方法handoff → 新合并方法冻结且初选null | 接续身份纠正；evidence_correction；重要 | 两价P1/T1与独立entry/add/holding合同生效；旧P2不再输出，更不能active；不追改旧报告或捏造跨方法完成 |

美国财政部10/22对外投资NPRM只作定向暴露线索，public-inspection文本拟10/26刊登、12/7意见截止，未成为本期生效新禁令；不能把独立许可当然判禁止或一概豁免。黄金/DXY同口径连续输入未取得，Fed广义美元不代入DXY阈值。详见[中观原始来源](evidence/industry-sources.md)。

## 5. 方法变化审议

没有本期新增方法提案；无需新增definition/economic_reason/scope/positive_case/negative_case/boundary_case/compatibility_impact七字段的proposed项目。已合并两价与控制生命周期的差异审查在采纳审查中，不能用“方法不变”掩盖其相对上期的实质变化；本期“无方法变化”仅指本次无新增规则修改。未改60/40预算、估值参数、机制权重、R1–R21及核心风险约束。

局部适配只更换受限JSON事实观测；混排D正文及旧日期均保留其历史身份。若将来调整阈值/动作/解除路径，仍需完整定义与单一方法PR，不在状态块塞规则。

## 6. 不应过度反应、待复评、撤回与兼容影响

1. 不把美债水位下降、周五A/H反弹、政策方向、ETF成交或海外收入代替公司盈利/现金流与对应Gate；未取得同样本南向净流、A/H估值分位、股息利差/拥挤度，不声称便宜或资金托底。
2. 事件按实质暴露和真实时点适用48h，不凭10/25日期全市场冻结；过窗按结果复核，缺预案/残余风险继续受限。公司事实足够时可估V50/V5并给冻结观察P1/T1；报价非空不解除entry/add限制。
3. 五个pending的原trigger_date分别为9/24、9/29、10/5，保留原时钟。恒瑞10/9旧v3配对早于本次触发覆盖/两价控制方法，不能据存在即记完成；其余未发现完整可接受凭证。不自动启动公司批次，不重置168小时冷却，不执行交易。
4. `supersedes=investment-2026-10-18-handoff-r2`；继续承接其对10/11旧change-decision SHA256 `06b59f529cf18cbfe55c08dffe10ca99ecb8c75ed5fbba6678e43fe681b2187a`的withdrawn_sources，防止切回旧方法复活。该旧报告只留审计字符串，不作正向当前来源。10/18当时真实行情不撤回，只不沿用其现在时/旧方法的买入语义。
5. 贷款、官方指数原件、完整10/23两融、ICE同合约结算、金/美元连续序列、公司财务/账户缺项保留unknown/null。未核资料不以其他同事或最新文件名补成事实。

## 7. 结构化输出

```yaml
MAINTENANCE_CLASSIFICATION:
  state_refresh: true
  evidence_correction: true
  method_change: false
FRAMEWORK_UPDATE_DECISION:
  update_needed: no
  update_level: none
  decision_reason: "按已合并两价与控制方法重评状态；本期无新规则提案"
KEY_VARIABLE_CHANGES:
  - {kind: state_refresh, variable: UST10Y, research_meaning: "最新五日严格>5%不成立；历史复评不自动关闭"}
  - {kind: state_refresh, variable: domestic_release, research_meaning: "社零1.1%使同月合取失败，贷款仍缺"}
  - {kind: state_refresh, variable: R21, research_meaning: "最新三日已有量能失败，周五反弹未解除"}
  - {kind: evidence_correction, variable: method_continuity, research_meaning: "旧handoff不兼容；新接续绑定已合并正文"}
UPDATE_FOCUS: [事实观测JSON, 明确状态采纳, 撤回继承, pending凭证]
DO_NOT_OVERREACT_ITEMS: [利率回落, 单日反弹, 海外capex, 政策方向, 其他药企BD]
RULE_EVALUATIONS: "见本期handoff，读取身份/截止/triggered/unknown分列"
PENDING_COMPANY_REVIEWS: [SZ-300308, SZ-300502, SH-600276, HK-01276, HK-09926]
COMPLETION_EVIDENCE: []
WITHDRAWN_SOURCES: ["10/11旧change-decision的当前有效身份，原内容保留"]
```

来源与日期：[宏观](evidence/macro-sources.md)、[中观及海外](evidence/industry-sources.md)、[行情与口径](evidence/market-sources.md)、[计算](evidence/calculations.json)。验证与发布结果由本期适配报告和冻结回执分别记录，不以本文件预先宣称推送成功。

## r2来源链补录

首份handoff的10/9美债历史触发未直接链接完整10/5–9序列；r2补入未撤回10/11 market-research（SHA256 4906a6f05f50fe4db622b39c7f82e5d59ab3f1661275341eed95ccdb81ce7dee），仅继承历史事实，不复活已撤回的10/11 change-decision。整包显式supersedes首份，原文不改，市场读数/方法/五pending不变。
