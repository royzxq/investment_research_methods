# ETF 研究轨道：任务说明 v0（M1–M4）

> 来源：用户与 ai_investment 会话（`ai-investment-7f`）在 2026-09-18/19 的设计讨论与拍板。本文件是交接文档；由承接会话（investment_research_methods 仓）复制进自己的分支后提交。与用户当面指令冲突时以用户为准。

## 0. 一页摘要

- **目标**：在 investment_research_methods 仓新增第三条轨道（ETF/指数基金），与期货、个股两条轨道并列、文件互不重叠（统一 `etf-` 前缀）。产出一份研究框架活文档、一套数据快照与确定性计算器、一个预注册的规则验证、一套决策卡与月度流水线。
- **两仓分工**：本仓 = 方法论与研究产出；`ai_investment` = 执行（读卡、每日监控、组合穿透与预算检查、台账）。**两仓唯一接口 = 决策卡 Markdown 里唯一的 JSON 块（带 schema 版本）**，互不 import。
- **三个已定的设计决定**
  1. ETF **不进** ai_investment 的 `investment_prediction.csv`（那台"P1/P2/T1 锚点"机器没有目标权重与再平衡，形状不对），走独立的决策卡路径。
  2. **慢变量随卡走，快变量执行侧自己算**：估值状态、情景回报、指数结构（月频）由本仓算好写进卡；指数点位、基金净值、趋势、权重（日频）由 ai_investment 每日计算。
  3. **买卖条件挂在指数点位上**，不挂基金净值/ETF 价格；工具价格只进"交易检查"（场内才有溢价）。
- **本文件范围**：M1–M4（全部在 methods 仓）。ai_investment 侧 P1–P3 不在本任务内，等本仓卡 schema 定稿后再开工。

## 1. 为什么 ETF 研究与个股研究不同（写框架时的立场）

| | 个股 | ETF/指数 |
|---|---|---|
| 研究对象 | 一门生意，内在价值可估 | 一条规则定义的篮子 = 一种风险暴露；问的是"承担这份风险现在给多少补偿" |
| 超额来源 | 信息/分析优势 | 风险溢价、分散、再平衡纪律、期限、成本税收结构；个人没有信息优势 |
| 广度 | 5000 只 | 坍缩成 10–15 个独立因子 → 择时期望 alpha 天然低，**配置是主菜** |
| 主要风险 | 事实判断错 | **被回测骗**（20 年只有约 4 个独立周期）+ 单一市场长期不回本 |
| "基本面" | 财报 | **指数编制规则** |

实测佐证（乐咕乐股月频 PE，as_of 2026-09-18）：沪深300 自 2007-10（PE 47.8）至今 18.9 年，价格年化 −1.22% = 每股盈利 +5.97% + 估值变化 −6.79%；自 2005-04（PE 14.0）至今 21.4 年，价格 +7.65% = 盈利 +8.14% + 估值 −0.46%。起始估值就是宽基的安全边际。

## 2. 要遵守的本仓惯例

- 文件前缀 `etf-`；三个 Project instruction 放 `projects/{meta_etf_analysis,etf_change_analysis,etf_adaption}/INSTRUCTIONS.md`；阶段 skill 放 `.claude/skills/`。
- `framework/etf_framework.md` 是 canonical；改动只走分支 + PR；`framework-condense` 直接复用生成 compact（仅供人读，任何 AI 环节读 canonical）。
- 取数脚本沿用 `future_data.py` 的模式：本地运行 → 写 `research/etf-<AS_OF>-data-snapshot.txt`（头行含框架版本/脚本版本/AS_OF，末行"快照完成"为完整标记）→ 提交；AI 环节只读快照。运行产物（CSV/parquet）落已 gitignore 的 `output/`。
- 确定性计算放纯函数模块 + `python3 -m unittest discover -s tests -v`。
- 机器可读块 = Markdown 内**唯一**严格 JSON 块 + 标准库校验器（仿 `validate_futures_audit.py`）；`null` 表示未知、`0` 表示已核实为零，不得混用。
- 诚实声明：未线上实测的取数路径如实写"未经线上实测"。

## 3. 文件布局（新增）

```
framework/etf_framework.md                    # canonical：Part A 通用规则 + Part B 决策卡模板
framework/etf_framework_compact.md            # condense 衍生
projects/meta_etf_analysis/INSTRUCTIONS.md
projects/etf_change_analysis/INSTRUCTIONS.md
projects/etf_adaption/INSTRUCTIONS.md
.claude/skills/{meta-etf-analysis,etf-change-analysis,etf-adaption,etf-data-sync,etf-card-research,etf-monthly-review}/SKILL.md
scripts/etf_data.py                           # 快照
scripts/etf_calc.py                           # 纯函数计算器
scripts/etf_backtest.py                       # 预注册规则验证（向量化、权重型）
scripts/validate_etf_card.py                  # 决策卡 JSON 校验器
tests/test_etf_calc.py tests/test_etf_backtest.py tests/test_validate_etf_card.py
research/etf-<date>-data-snapshot.txt
research/etf-<date>-rule-prereg.md            # 先提交，再跑
research/etf-<date>-rule-validation.md
research/etf-<date>-market-research.md / -change-decision.md / -adaption-report.md
research/etf-cards/<index-slug>-<date>.md     # 决策卡
research/etf-scorecard.md                     # 记分卡（追加式）
```

分支建议：`etf-track/day0`，M1–M4 可分多个 commit、一次或分次 PR，由承接会话与用户商定。

## 4. 框架文档大纲（M3 交付物的内容要求）

**硬约束：框架里不写任何市场环境（regime）假设，环境判断只存在于卡里。** 这是压住改版频率的手段——期货框架三周内 v2.16→v2.26 的节奏对 ETF 是有害的（过拟合是头号敌人）。

### Part A 通用规则

- **A0 数据契约**：快照与计算器的数字视为既定输入，AI 的工作是"校验 + 判断"，不采集不计算。三项 mini-gate：时效一致、缺失检测（→ `[需人工补充]`）、异常值标"存疑"。关键数据缺失时降低置信度，必要时暂停给出点位与仓位，不用看似合理的数字填空。
- **A1 任务分流**（先定任务再研究；任务决定卖出规则）

  | 任务 | 核心问题 | 决策形状 |
  |---|---|---|
  | 核心配置 + 分散器 | 长期持有哪些市场与资产；跨资产、跨市场分散是**第一目标**（沪深300 19 年未回 2007 高点；恒指 2000→2024 价格指数近乎走平） | 战略权重 + 再平衡带 + 估值缩放的投入倍率 |
  | 阶段性行业/风格 | 哪个方向的基本面改善尚未被充分定价 | 有期限的投资假设 + 指数点位区间 + 失效条件 + 最迟复评日 |
  | 防御/流动性 | 期限与支出匹配 | 期限匹配 |

  杠杆/反向产品直接排除；主动型产品需额外研究管理人，默认不入池。每张卡开头写清：承担什么任务、记账币种、计划持有多久、最多允许它贡献多少组合损失、不买它时资金放在哪里（= 记分基准）。
- **A2 排除优先（非补偿性）**：任务不匹配 / 关键数据不可靠 / 工具门槛不过 / 预算已满 → 直接结论"不买（原因）"，不许用低费率、高规模加分抵消。不做总分排行。
- **A3 底层资产研究**：写成可验证的因果链（例：下游需求 → 订单与产能利用率 → 价格与利润率 → 成分公司盈利与现金流 → 当前价格是否已反映）；每条链回答两问：能否传导到指数实际持有公司的股东回报？市场是否已提前付钱？按权重与盈利贡献分配研究精力。产出固定为 **1 句主判断 + 3 条支撑证据 + 2 条反证**。
- **A4 指数审查**（名字不是说明书，编制规则才是）：①选什么（样本空间、行业定义、筛选条件；**目标子行业占指数多大权重 = 观点-持仓错位度**）②怎么加权（市值/等权/股息率/因子；单一成分与行业上限；这个规则让我承担什么风险）③何时换仓（频率、缓冲区、历史规则变更、换手）④历史业绩是否可用（区分指数回溯期 / 正式运行期 / 基金成立后）。
- **A5 估值与预期分流**（统一的是决策流程，不是估值公式）

  | 类型 | 方法 | 要防的误判 |
  |---|---|---|
  | 宽基 | 回报分解 + 股债利差（E/P − 10 年国债）为主，PE/PB 分位为辅 | 只看点位不看盈利与结构 |
  | 成长/主题 | 情景 + 反向估值（当前价格要求多高增长） | 把产业空间当股东收益 |
  | 周期 | 中周期利润、不同周期位置压力测试 | 高峰利润使 PE 看起来很低 |
  | 红利/价值 | 可持续股东回报、分红覆盖、行业集中度 | 高股息率 = 低风险 |
  | 债券 | 到期收益率、久期、信用 | 低信用风险 = 低波动 |
  | 黄金/商品 | 只做情景；期货类另算展期 | 现货、期货、资源股混为一谈 |

  回报分解：`预期年化 ≈ 指数口径每股盈利增长 + 股息率 + 估值年化变化 − 实施拖累`，估值年化变化 ≈ `(期末倍数/当前倍数)^(1/年数) − 1`。三情景必出；**基准情景必须假设估值零变化**，看回报是否仍可接受。估值分位只能作证据：必须记录观察窗口、指数规则是否变过、成分口径、PE 算法、亏损公司处理；分位一律用扩张窗且样本不足 5 年不出结论，同时给 10 年窗对照。
- **A6 工具比选**：不同指数比"谁更准确表达观点"，同指数比"谁更可靠更便宜"，两者不混。输出**首选 + 备选 + 其余落选原因**。用户实际工具是**支付宝场外联接/指数基金**，因此重点 = A/C 份额（C 类每年扣销售服务费，长期定投通常 A 类更便宜，须逐只核）、赎回费阶梯（7 天内 1.5%）、QDII 限购、确认/到账时滞、规模与清盘风险、跟踪偏离度（TD，回报差）与跟踪误差（TE，回报差的波动）——同窗口同基准口径、含分红同币种；用历史 TD 作实施拖累时不要再重复扣管理费。税与账户结构要进比较：基金分红对个人暂免个税（个股持有不足一年 10–20%）；盈立直持港股 ETF 无红利税，港股通 20%。
- **A7 交易检查**：场外基金按净值申赎、无溢价 → 本节对其只查限购、惩罚性赎回期、到账时滞。场内 ETF 才查溢价：用**收盘净值口径**（不用盘中 IOPV），是 QDII 专属规则并含卖出侧（持仓溢价过高本身即卖出/换工具理由）；`市价 = 净值 × (1+溢价率)`，10% 溢价归零即 −9.1%。
- **A8 仓位**：`单笔上限 ≈ 允许贡献的组合损失 ÷ 压力情景跌幅`。压力跌幅按资产类型给默认表并允许卡内覆盖：单一市场宽基 −60%~−72%（沪深300 2007–08 实测 −72%）、行业/主题 −70%、恒生科技取自身历史约 −75%。需合并同方向持仓；**穿透后同一观点的多只基金算一笔**。持有很多股票不等于可以无限放大仓位。
- **A9 决策形状**：每条规则标 `validated | provisional | rejected` 并链接验证报告（见 §7）。未验证的规则可以写进框架但必须标 provisional。
- **A10 卖出三分法**：资产逻辑失效（撤销判断）/ 组合权重超限（再平衡）/ 工具变差（换同指数产品）——三种情况动作不同，卡里必须分开写。
- **A11 监控变量**：每卡 3–5 个，表头沿用 ai_investment 现有结构 `变量｜来源｜当前值｜警戒阈值｜触发动作｜频率`；不许写"关注行业景气"这类空话。
- **A12 记分与复盘**：战术论点不可回测 → 预注册（写卡日期、置信度、可观测失效阈值、最迟复评日）+ 事后记分，对照基准 = "同一笔钱放在核心宽基/货基里的结果"。战术项目整体退出线：累计 N 张已关闭卡的合计超额 ≤ 0 → 暂停战术轨道。同时活跃战术卡 ≤ 5 张。
- **A13 参数总表**：框架内所有数值参数集中一张表，含状态与证据链接。**没有验证报告不许改数字**。

### Part B 决策卡模板（参数化 `{{INDEX}}` / `{{TASK}}` / `{{AS_OF}}`）

八个模块 + 三个新增字段：投资任务 / 核心判断 / 指数匹配 / 预期与估值 / 工具比选 / 点位与仓位 / 核心监控 / 退出与复评；新增 **对照基准、预注册失效阈值、研究覆盖率**（指数权重里有多少已在 ai_investment 的个股研究池内，可复用现成研究）。末尾是 §6 的 JSON 块。结论可以是"不买"。

### AI 与代码分工（写进 A0 与各阶段 instruction）

代码负责一切确定性计算；AI 负责读编制方案、写因果链、找反证、查观点-持仓错位、提监控变量。**AI 不输出任何价格、点位、估值、权重数字**——这些只能来自快照或计算器，并由校验器强制（§6）。

## 5. 数据快照 `scripts/etf_data.py`（M1）

| 节 | 内容 | 数据源 | 实测状态（2026-09-18，用户 tushare token + akshare 1.18.64） |
|---|---|---|---|
| §0 | 自检：数据日、接口可用性、缺口清单 | — | — |
| §1 估值 | PE/PB、股债利差及分位（扩张窗 + 10 年窗，附样本数） | tushare `index_dailybasic`（日频）；akshare `stock_index_pe_lg` / `stock_index_pb_lg`（月频，2005 起，12 个宽基：上证50/沪深300/中证500/中证1000/中证800/中证100/上证180/上证380/创业板50/深证100/上证红利/深证红利）；akshare `bond_zh_us_rate`（10 年国债，2005-01-04 起 5429 行；tushare `yc_cb` **无权限**） | `index_dailybasic`：000300/000905/000016/399006/399905 通；**000852/000015/000922/科创50/行业指数返回空**。`stock_zh_index_value_csindex` 只给最近 20 个交易日 |
| §2 回报分解 | 价格年化 = 盈利增长 + 估值变化（自起点、滚动 10/5 年） | 同上，隐含 EPS = 点位 ÷ PE | 通 |
| §3 指数结构 | 前十大权重、最大单一成分、行业权重、期间换手、成分数；研究覆盖率（可选参数 `--pool-csv` 指向 ai_investment 的 `investment_prediction.csv`） | tushare `index_weight`（月度、point-in-time） | 通：沪深300、中证红利 000922.CSI、上证红利、创业板指（2015 起）；半导体 H30184.CSI（2015 起 69 行）；白酒 399997.SZ、光伏 931151.CSI、科创50 000688.SH（近年起） |
| §4 指数口径基本面 | 加权 ROE、盈利增长、利润集中度、亏损权重 | `index_weight` × 个股 `daily_basic` / `fina_indicator` 自聚合（天然 point-in-time） | 可行但调用量大 → **第二期**，M1 不做 |
| §5 工具池 | 规模、费率、成立日、净值、TD/TE、（场内才有）溢价分布 | tushare `fund_basic(market='O')`（**须 offset 分页，单页上限 15000，全量 29,886 只**）、`fund_nav`（`.OF` 代码，021457.OF 已到 2026-09-17）；场内用 `fund_basic(market='E')`、`fund_daily`、`fund_adj`；akshare `fund_etf_spot_em`（IOPV/折价率/份额） | 均通。**缺口：销售服务费无字段**（akshare 费率类接口未验证）→ 先标 `[需人工补充]` |
| §6 趋势 | 10 月均线、200 日均线状态 | 指数日线 | — |
| §7 宏观代理 | 10 年国债、美债、汇率、金价 | `bond_zh_us_rate` 等 | 部分通，其余待验 |
| §8 记分结算 | 活跃卡/已关闭卡相对基准的收益 | 净值与指数 | — |

已知缺口（一律落 `[需人工补充]`，不猜）：港股指数（恒指、恒生科技、港股通红利低波、港股创新药）的估值与成分无现成源；QDII 标的成分无源；全收益指数口径待核；指数估值供应商数据是否 point-in-time 未验证——**回填历史前必须抽 5 个历史日期，用 `index_weight` 当期成分 + 当期披露自算对比，偏差 >10% 不得作回测输入**。

代码后缀直接用 `fund_basic` 返回的 `ts_code`，不要按前缀推断交易所（ai_investment 里有 6 处推断实现把 51/56/58 开头判成深市，别复制这个 bug）。

### `scripts/etf_calc.py` 纯函数清单

`return_decomposition` / `expanding_percentile`（含最小样本守卫）/ `erp_spread` / `scenario_annual_return` / `tracking_difference` / `tracking_error` / `premium_pct` / `lookthrough_weights`（直接持仓 + Σ 基金权重×成分权重）/ `loss_budget_cap` / `joint_stress_loss` / `sma_state`。全部带单测，单位与口径缺失时返回缺口而不是数值。

## 6. 决策卡 JSON schema v1（草案——由承接会话定稿）

```json
{
  "card_schema_version": 1,
  "card_id": "hk-innovative-drug-tactical-2026-09",
  "as_of_date": "2026-09-19",
  "framework": {"path": "framework/etf_framework.md", "version": "v0.1"},
  "snapshot_ref": "research/etf-2026-09-19-data-snapshot.txt",
  "task": "core | tactical | defensive",
  "status": "active | watch | no_buy | closed",
  "no_buy_reason": "thesis | price | tool | portfolio | data | null",
  "close_reason": "thesis_realized | thesis_invalidated | budget | tool | expired | null",
  "exposure": {"index_code": "", "index_name": "", "asset_type": "broad_equity | dividend_value | growth_theme | sector | cyclical | bond | gold_commodity | cross_border_equity", "currency": "", "view_mismatch_note": ""},
  "thesis": {"statement": "", "evidence": ["", "", ""], "counter_evidence": ["", ""], "horizon_months": 0},
  "expectation": {
    "method": "return_decomposition | reverse_valuation | mid_cycle | ytm_duration | scenario_only",
    "scenarios": {"bear": {"annual_return": null}, "base": {"annual_return": null, "valuation_change_assumed": 0}, "bull": {"annual_return": null}},
    "valuation_state": {"metric": "erp_spread | pe_ttm | pb", "value": null, "percentile_expanding": null, "percentile_10y": null, "sample_n": null, "as_of": "", "source": "snapshot§1"}
  },
  "instruments": {
    "primary": {"code": "021457.OF", "name": "", "instrument_type": "otc_fund | exchange_etf", "share_class": "A | C | E | null", "platform_account": "支付宝 | 盈立证券 | ...", "reason": ""},
    "backup": {},
    "rejected": [{"code": "", "reason": ""}],
    "merge_note": "同一观点下多只基金是否合并及理由"
  },
  "trade_rules": {"min_holding_days": 7, "purchase_limit_note": null, "max_premium_pct": null, "sell_if_premium_above_pct": null},
  "decision": {
    "strategic_weight": {"target": null, "band": null},
    "rule_refs": ["A9.contrib.v1"],
    "zones": {"basis": "index_level", "index_code": "", "accumulate_below": null, "reduce_above": null, "valid_until": ""},
    "dca_action": "continue | pause | scale"
  },
  "sizing": {"bet_group": "同一笔押注的分组键（穿透后同观点的基金共用）", "stress_drawdown": null, "loss_budget_cny": null, "standalone_cap_cny": null},
  "monitor_variables": [{"name": "", "source": "", "current": null, "threshold": "", "action": "", "frequency": ""}],
  "exit": {"invalidation": [{"variable": "", "condition": "", "action": "close | reduce | swap_tool"}], "latest_review_date": ""},
  "scorecard": {"benchmark": "", "preregistered_at": "", "confidence": null, "entry_ref_index_level": null}
}
```

`validate_etf_card.py` 必须强制：schema 版本；`status`/`no_buy_reason`/`close_reason` 的组合合法性；日期为 ISO；`task=tactical` 必有 `exit.latest_review_date` 与至少一条 `invalidation`；`base.valuation_change_assumed == 0`；**每个数值字段旁带 `source`（`snapshot§x` 或 `calc:<函数名>`），点位、权重、金额类字段出现 `ai_estimate` 即拒收**；`instrument_type=otc_fund` 时溢价字段必须为 null。执行侧按"30 天提醒 / 45 天过期"判断卡的新鲜度，超过 `latest_review_date` 视为待复评。

**定稿后请在产出说明里写明 schema 文件路径与版本号**，ai_investment 侧据此写读卡模块。

## 7. 规则验证（M2）：先提交预注册，再跑

预注册文件 `research/etf-<date>-rule-prereg.md` 必须先于任何回测结果提交，写死：规则定义、参数、基线、折、指标、通过门槛。只验证三条：

- **H1 估值缩放投入**：每月预算 B；倍率按股债利差的扩张窗分位（最少 5 年样本）取 ≥0.7→2×、0.3–0.7→1×、<0.3→0.5×；未花完的预算留在现金（货基收益代理）并可在高倍率月动用，保证两边**总投入资金相同**。对照 = 固定每月 B。
- **H2 趋势过滤**：指数月收盘 vs 10 月均线。H2a 仅暂停新增投入；H2b 连同存量一起转现金。对照 = 无过滤。
- **H3 再平衡**：四类资产（中国权益 / 海外权益 / 长债 / 黄金）两组预注册权重——贴近用户约束的 85/5/5/5 与均衡参照 60/15/15/10；比较"偏离带再平衡（绝对 5pp 或相对 25%）/ 年度再平衡 / 不再平衡"。

协议：基线 = 买入持有与固定定投；**4 个不相交周期折**（2005–10 / 2011–16 / 2017–22 / 2023–）；指标只认最大回撤、下行捕获、资金加权年化；通过门槛沿用 ai_investment 的标准——回撤在 ≥3/4 折更优，且年化劣势不超出折间噪声（|均/σ| < 1）；参数先验固定、不调参、不加规则；嵌套窗口不算敏感性；实施拖累按费率与 TD 扣除。海外权益、长债、黄金的长历史总回报序列数据源**尚未验证**，M2 第一步先核数据，取不到的资产如实缩减 H3 范围，不用合成序列硬凑。不通过的规则在 A13 标 `rejected` 并从框架删除。M2 的结论直接决定用户剩余约 34.5 万怎么投入。

`scripts/etf_backtest.py` 是向量化、权重型回测器（几百行 pandas 即可），只服务预注册规则验证；开放式策略挖掘不在本仓范围。

## 8. 月度流水线（M4）

**节奏：月度；先在本地跑，不上云端 Routine**（云端无 tushare 权限）。编排器 `etf-monthly-review`：

1. `etf_data.py` 出快照（本地）。
2. **① meta-etf-analysis**：不重做宏观调研，直接读个股轨道最新的 `research/investment-*-market-research.md`。输出变量：`ASSET_CLASS_STATE`（取自快照）、`STRUCTURAL_CHANGES`（编制规则/产品/税/额度等事实）、`TACTICAL_CANDIDATES`、`CARD_REVIEW_QUEUE`（到期或触发的卡）、`DATA_GAPS`。
3. **② etf-change-analysis**：只有四类情况允许触发改框架——结构性事实变化、口径错误、记分卡证据（年度或累计 N 张已关闭卡）、上期预备观察项。**市场叙事/环境变化明确不触发**，改输出 `CARD_ACTIONS`（更新哪些卡）。沿用个股轨道"上期预备观察项逐条复核、不许静默丢弃"的机制，但**不设**"框架-现实一致性"那条触发轴（框架里本来就没有环境假设）。
4. **③ etf-adaption**（罕见）：分支 + PR；新增硬规则——改 A13 的数字必须链接一份规则验证报告。随后 `etf-data-sync`、`framework-condense`，编排器统一开 PR。
5. `etf-card-research`（按需或由 `CARD_REVIEW_QUEUE` 触发）：输入指数 + 任务 + 快照 → 按 Part B 出卡 → 过校验器。

## 9. 交付物与验收

| 步 | 交付物 | 验收 |
|---|---|---|
| **M1** | `etf_data.py`（§0–§3、§5–§7）、`etf_calc.py`、单测、第一份快照 | 单测全过；以 as_of=2026-09-18、同一月频 PE 源、"当时及之前最近一期"规则，沪深300 分解复现 −1.22% / +5.97% / −6.79%（2007-10-31 起）与 +7.65% / +8.14% / −0.46%（2005-04-29 起），允许末位舍入差；12 只持仓基金的代码、费率、最新净值全部解析出来（含待核的两只） |
| **M2** | 预注册文件（先提交）、`etf_backtest.py`、验证报告 | H1/H2a/H2b/H3 各得出 validated 或 rejected，附逐折表；数据缺口如实写 |
| **M3** | `etf_framework.md` v0.1、`validate_etf_card.py`、`etf-card-research` skill、首批卡 | 校验器零错误；首批至少 3 张：医药/创新药簇（tactical）、一张核心卡（建议港股通红利低波或 02800）、黄金或一张分散器候选 |
| **M4** | 三份 instruction、阶段 skill、编排器 | 本地完整跑通一次，产出当月 market-research 与 change-decision |

预估 M1 2 人日、M2 2–3、M3 1.5–2、M4 1。M2 排在 M3 前是有意的：先知道择时规则值不值得存在，再决定 A9 留多少内容。

## 10. 用户拍板的参数与现状（2026-09-18/19）

- ETF 计划总仓 ≈70 万；已投 ≈35.5 万（12 只场外基金 ≈29.9 万 + 02800 ≈5.6 万）；待投 ≈34.5 万。全部资产 ≈136 万（个股 ≈66 万 + ETF 70 万）。
- 行业合计 ≤ 30% × 70 万 = **21 万**；单笔最坏亏 **3.5 万**（压力跌幅 −70%）→ 单笔最多 **5 万**，约 4 笔打满。
- 中国权益 ≤ **90%**（分母 = 全部资产）→ 非中国权益至少 ≈13.6 万，现仅黄金 1.2 万（中国权益 ≈99%）；待投资金里至少 ≈12.4 万应投向黄金/债券/美股。
- 归类（用户裁定）：**恒生科技 = 宽基（核心仓，不占行业额度）；科创50 = 行业**。恒生科技卡里的压力跌幅仍取自身历史值。
- 无决策卡的持仓：保留 ai_investment 现有股票纪律 + 告警。

| 基金 | 金额 | 代码 | 管理+托管费 | 桶 |
|---|---|---|---|---|
| 天弘恒生科技ETF联接(QDII)C | 53,211 | 012349.OF | 0.60% | 核心·宽基 |
| 鹏华中证国防指数(LOF)A | 49,024 | 待核 | — | 行业 |
| 易方达恒生港股通红利低波动ETF联接A | 39,873 | 021457.OF | 0.20% | 核心·红利 |
| 汇添富国证港股通创新药ETF联接C | 33,641 | 021031.OF | 0.60% | 行业·医药 |
| 银华中证创新药产业ETF联接C | 25,749 | 012782.OF | 0.55% | 行业·医药 |
| 国泰中证A500ETF联接A | 18,916 | 022448.OF | 0.20% | 核心·宽基 |
| 华宝中证医疗ETF联接C | 18,354 | 012323.OF | 0.60% | 行业·医药 |
| 广发中证香港创新药ETF联接(QDII)A | 16,605 | 019670.OF | 0.60% | 行业·医药 |
| 工银科创50联接C | 11,774 | 待核 | — | 行业 |
| 南方中证申万有色金属ETF联接E | 11,570 | 010990.OF | 0.60% | 行业 |
| 易方达黄金ETF联接A | 11,562 | 000307.OF | 0.60% | 分散器 |
| 嘉实中证细分化工产业主题ETF联接C | 8,845 | 013528.OF | 0.20% | 行业 |
| 盈富基金 02800（盈立证券，HKD） | ≈56,000 | 02800 | — | 核心·宽基 |

现状对规则：医药/创新药 4 只合计 ≈9.4 万，穿透后是同一笔押注，**超单笔上限 4.4 万**；国防 ≈4.9 万顶格；行业合计 ≈17.6 万（占 21 万的 84%，余 ≈3.4 万）；行业联合压力（全部 −70%）≈ −12.3 万；12 只基金全部开着定投，超限的几只按规则应暂停定投（待卡出来落实）。6 只是 C 类份额（恒生科技、港股通创新药、创新药产业、医疗、科创50、化工），须逐只核销售服务费与换 A 类的得失。

第 0 天指数池：恒生科技、中证国防、恒生港股通红利低波、国证港股通创新药、中证香港创新药、中证创新药产业、中证医疗、中证A500、科创50、中证申万有色、中证细分化工、黄金，外加恒生指数（02800）、国债与美股宽基（承接待投资金的分散器候选）。

## 11. 不在本任务范围

- ai_investment 侧的 `src/etf/`（登记表、读卡、每日监控、穿透与预算、纪律分流、基金快照台账）。
- 开放式策略挖掘、产品总分排行、超过复评能力的指数池。
- 让 AI 输出任何数字。
