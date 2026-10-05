---
name: stock-research
description: 对单只 A 股或港股个股做中长期投资价值调研并输出价格地图与核心天花板监控变量：输入股票名称、代码、估值时点与量价基本面数据包（粘贴文本，必填），依次执行数据包自检、定量映射、自动多代理定性调研（deep-research-auto）、框架运算（Precheck→机制归类→Gate→估值→Terminal→Price Map），落盘调研报告 md 与 price-map JSON（含 P1/P2/T1/T2/cap 与不超过 10 条监控变量）并刷新 latest 别名。用于个股调研与复评请求，如"调研 600066 宇通客车""给 01093 石药做价格地图""复评某只股票"。Use when the user asks for single-stock A-share or Hong Kong stock research, a price map, or a review of a previously covered name.
---

# 个股调研（Price Map 与研究结论）

把用户粘贴的数据包放进本仓个股框架的完整决策链，产出：按框架 §10 的调研报告 + 研究结论 JSON（Price Map + 核心天花板监控变量）。方法、参数与判据全部委托 `framework/investment_framework_compact.md`（执行导航，下文简称 **compact**）与 `framework/investment_framework.md`（canonical，判据冲突时以它为准）；本技能只负责编排、校验、落盘与输出契约。路径均相对仓库根目录。

## 适用与边界

- 只出研究结论与价位（评级/动作/Price Map/T1/T2/监控变量）；不给下单金额、执行时点、分批计划，不执行交易。
- **不自行取数**：本仓不存在个股取数脚本（`stock_data_pack.py` 未迁入）；数据包是唯一数据入口，不得尝试运行或查找脚本；包内值"视为既定输入，直接引用，不重查不重算"（compact §2）。
- **不重估宏观**：D1–D8 一律照 compact §1 当期值引用；配置新鲜度只披露、不自行并入或改写。
- 不改 canonical/compact 及其它框架文件；发现框架问题只记录在报告缺口里。
- 默认只落本地：不 `git add/commit/push`、不开 PR；同日重复运行不覆盖已有产物。
- 运行前先读仓库根 `AGENTS.md` 与 `docs/context/project-state.md`；检索路由遵循根 `AGENTS.md`（`gemini_web_search` 优先，失败按标记回退内置检索）。
- 日期一律 `Asia/Shanghai`；历史时点研究只使用估值时点当日及之前已披露的证据，不混入未来信息。

## 输入

### 必填（缺一即停）

1. **股票名称 + 代码**：规范化为 `600066.SH` / `01093.HK` 形式，确定市场（A股/港股）与币种。
2. **估值时点 VALUATION_DATE**：用户指定；未指定时用北京时间当天并声明。
3. **数据包全文**（粘贴文本，唯一数据入口）。需能识别下列各节，**缺整节即停**（见边界条件①②）：
   - 量价快照：最新收盘、近5/20/60日、52周回撤、量额；A股另含量比、换手率、总/流通市值、股息率（TTM）；
   - 估值分位：PE/PB 近1/3/5年；A股另含 PS、换手率分位；
   - 盈利与现金流：A股为多期盈利兑现质量表（含扣非 ROE）+ 经营现金流表（含应收/存货/合同负债）；港股为 best-effort 原始字段（列名不稳定）；
   - Terminal 输入：市值、K、隐含倍数；
   - 附录「无法 API 化、需人工补充」清单。
4. **运行模式**：首次 / 复评。未说明时按 `research/investment-<代码>-latest.json` 是否存在自动判定并在回执中声明。

### 可选

- 仓位参数：单票硬上限、温度仓位上限、cap 系数、`step_down`——仅本次运行有效；缺省的参数化处理见 4.6。
- 上期产物路径覆盖；历史时点的当时配置来源覆盖。

### 自行读取（顺序）

1. 根 `AGENTS.md` → `docs/context/project-state.md`（历史边界与待办，不继承旧报告对"最新"的断言）；
2. compact（执行导航）→ 判据冲突时展开 canonical 对应节；
3. 复评模式：`research/investment-<代码>-latest.json` 及其 `provenance.canonical_file` 指向的上期报告与 JSON。
不读 `projects/*/INSTRUCTIONS.md`（历史阶段方法，非现行入口）。

### 停下问用户的边界条件

① 缺数据包、缺整节、字段无法识别；② 名称-代码-市场不符，或 A+H 两地上市未指明市场与币种；③ **数据包数据日或财报期晚于估值时点（前视）→ 硬停**；④ 数据最新交易日与估值时点相差超过 10 个交易日；⑤ 估值时点早于 compact §1「市场状态截至」日且未提供当时配置来源；⑥ 复评模式找不到上期产物（问是否降级为首次）；⑦ 同日同代码产物已存在且输入指纹与本次不一致（问复用/隔离/覆写）。其余情况（含配置过期）不停。

## 执行

### 1 数据包自检（compact §2 mini-gate）

- **时效一致**：数据最新交易日 vs 估值时点；财报为最新已披露期；不一致记缺口。
- **缺失检测**：`—`/`数据为空` → `[需人工补充]`；**禁止用旧记忆或估算填充**。
- **异常标记**：标「存疑」，不作 Gate/熔断硬依据，二次核对。操作性阈值（本技能补足、非改判据）：OCF/净利 <0.5 或 >2.0 且无口径解释；扣非与归母符号相反或偏离 >50%；PE_TTM ≤0 或 >500；股息率 >15%；分位 =0%/100%。
- **字段识别映射表**：包内列名 → 框架字段 → 用途 → 置信度（直接/推断/缺失）；接口列名不稳定时逐条标「推断」并加 `[口径待核]`，不得把推断值当硬证据。整节识别失败按缺节处理（停下）。
- **一致性抽检**（属校验、不属重算）：市值 ≈ PE_TTM × TTM 归母；PB ≈ PE_TTM × ROE；矛盾处标存疑。
- **配置新鲜度检查**：比较 compact §1「市场状态截至」与 `research/` 下最新 `investment-*-market-research.md`/`-change-decision.md`；存在更新的未适配期次时，在报告 §0 与 JSON `meta.framework.stale_config_warning` 显式披露（**只披露、不暂停、不自行并入**）。
- 产出：报告 §0 素材 + `gaps` 初稿（每条带 severity：阻断/降级/注记；**阻断级缺口 → 不得给完整买入型 Price Map**）。

### 2 定量映射（不重查不重算）

按 compact §2「字段→模块」逐条落位，形成「定量事实底稿」（值/单位/数据日/来源=数据包）；此后各环节只引用底稿。必须显式标注的口径差：

- [R1]① 用**个股**换手率分位近似**板块**换手率分位（近似口径）；港股缺该字段 → [R1]① 记「无法判定」，**不得判"未命中"**。
- 港股无扣非 → Precheck#1「扣非 vs 表观背离」判「不适用」（不判通过）；「逐期改善」按半年度序列核对；[R1]③「当季/次季可见业绩」改看正面盈利预告/经营数据公告。
- 币种一致性：市值/净利/PE_TTM 三者币种一致方可相乘；外币报表 + HKD 报价需换算或标 `[口径待核]`。
- 北向/南向持股变化必须带数据日与披露频率口径，不得当日频"最新"信号解读。
- 检索结果与包内值冲突 → **以包内为准**，差异记入报告 §0。
- 温度：A股用 50ETF 波指+沪深300 代理、港股用 VHSI；包内不含时记 `[需人工补充]`，交定性调研取数（3-⑧）。

### 3 定性调研（deep-research-auto 多代理自动调研）

目的：补齐 compact §2「数据包不替代」清单（订单真实性、海外 capex 联动、政策实锤、Terminal 假设、国家队、紧缩体制输入、指数读数、拥挤度口径）。

**调用方式**：用 Skill 工具调用 `deep-research-auto` 技能完成下述主题；传参：调研问题、约束（信息截止=估值时点、来源等级等）、`OUTPUT_DIR=output/stock-research-<代码>-<日期>/`、报告格式=结构化证据条目。若该技能不可用（环境缺失或调用失败）→ 改用本仓通用检索路由（`gemini_web_search` 优先、失败回退内置检索）逐主题直接调研。两路都产出同一「结构化证据条目」格式，结论不因路径而异。（官方 `deep-research` 仅限用户手动调用，不作为本流程的调用路径；用户主动要求时按其要求请用户自行运行。）

**8 组主题**（每组注明映射的框架判据）：

1. 订单与客户：付费客户、合同金额、交付周期、回款周期、客户集中度、公告→转化→回款一致性 → Precheck#2、[R8]；
2. 政策实锤与第二环：文件/试点/财政资金/招标/大基金出资/集采规则，分「规划派生/规则型/产业周期」 → Precheck#6、[R19]；
3. Terminal 假设：行业 TAM、份额上限、稳态净利率 → §8；
4. 盈利兑现与一致预期：近端业绩可见性、卖方 2027 年估值、分红/回购政策 → Precheck#1、[R1]③、[R8]；
5. 在册事件与公司日历：业绩预告/快报、财报披露日、解禁、监管审批、并购 → [R6] 与滚动窗口；
6. 筹码与国家队：中央汇金/证金动向（**须官方披露确认，媒体报道不作既成事实**，[R11]）、港股南向持股、A+H 标的的 AH 溢价；
7. 治理/合规/红线：诉讼、处罚、质押、审计意见 → Gate 第③分支、Non-Price Risk；
8. 指数读数：费城半导体 SOX、港股 VHSI、A股温度代理 → §6 温度、Precheck#4。

**传入约束（写进给 `deep-research-auto` 的任务描述）**：

- 信息截止 = 估值时点，只采该日及之前公开的证据；每条结论附 `[出处, 日期]`，优先一手来源；检索摘要只用于发现，关键事实打开原始来源核验；
- **禁止重复检索包内已给的量价/估值/财务字段**；
- 每主题必须显式给出「未找到/证据不足」结论与对称/反向证据；不给买卖建议与目标价（裁决权在本技能）；
- 输出为结构化证据条目（主题/结论/证据/出处/日期/强度/影响方向），不要叙述性长文；
- 工作目录定为 `output/stock-research-<代码>-<日期>/`（仓库已忽略 `output/`，经 `OUTPUT_DIR` 传入）；其笔记与报告均落在该目录下（不写仓库根 cwd），scratch 产物不得写入 `research/` 命名体系、不提交；最终报告落点由第 6 步统一负责。

每条证据登记为 JSON `qualitative_findings`；未取得项按影响进入 `gaps`。

### 4 框架运算（逐步引用 compact，不抄判据原文）

**4.1 Precheck 10 闸与必答**：逐闸输出「项目/数据来源(已供·部分供·需人工)/结论/核心证据/是否构成约束」；结论用**五态**：通过/警惕/不通过/不适用/无法判定（「缺数据 ≠ 通过」「不适用 ≠ 通过」）。必答三项：主矛盾暴露类别（八选一闭集）、收益逻辑归属、双轴定位（六态；D8 激活时内需端暴露程度与对冲显式标注）。**硬失败清单逐条判**（命中/未命中/无法判定 + 依据），再套判定规则（1 项硬失败→冻结；≥2 项中度风险→上调 r、下调 cap、必要时取消 P2；拥挤高+验证弱→优先冻结；双轴一利一损+验证弱→cap 下调 ≥30%；双轴双损→冻结）。

**4.2 机制归类**：六型之一 + 当期权重（查 compact §1 D4/D5，原样引用并标注状态：负反馈修复状态、供给冲击的贵金属/油气分支、事件驱动的规划型/实锤型、正反馈镜像与外部锚）。正反馈 vs 周期反转鉴别清单 5 项逐项判（≥3 项指向正反馈 → 强制正反馈参数）。[R8] 三条件、[R15] 归型、[R19] 政策链层级按适用性引用。

**4.3 Gate 与 Non-Price Risk**：Gate 决策树**逐分支判定并记录命中分支号**，不合并成一句结论。Non-Price Risk 8 项逐项（Chip/拥挤度/治理/成本与现金流/紧缩体制/AI 链裂缝/油价 PPI/内需暴露）。**温度缺失 → `[需人工补充]`，不得按"冷"放宽（按从严档）**。**[R6] 逐窗口成行**：对 D6 各在册窗口给「公司暴露 / 前 48h 动作 / 弱情景预案」，含油价一级三层暴露（[R14]），不得漏项。联动规则（两项/三项组合后果）逐条核对。

**4.4 估值 V50/V5 与 [R3]**：方法按 compact §7 选择（稳定盈利 PE/PFCF；金融 PB-ROE/RIM；周期 EV/EBITDA；未盈利高增 EV/Sales；多元 NAV/SOTP）。V50 三假设（收入/利润率/估值锚）显式列出、给区间分档不做伪精确；五条验证链择适用者；高强度结论限制逐条核对。V5 压力项按 compact §7 当期水位（含 D 层紧缩体制）。**[R3] 压测明细三项逐项**：① 隐含降息 bp（属"数据包不替代"项：给推导口径与依据，推不出记「无法判定」）；② 无降息情景压缩幅度；③ 盈利对冲能力——**举证责任在多头方向：只有存在合约级订单可见度或政策映射且报表可验，才判「盈利可对冲」；证据缺失按「盈利无法对冲」处理**（三项合取成立 → 冻结，按无降息情景重估）。不对称性 → cap 系数（低 1.0 / 中 0.7–0.9 / 高 0.5–0.7）。

**4.5 Terminal**：四步按 compact §8。固定参数按市场取（A股 r=8%, g=2%, N=7, K≈0.10；港股 r=10%, g=2%, N=7, K≈0.16；**不得混用**，与数据包「固定参数」行核对）。可达性（不可能/困难/可能/容易）与预期差（正/中性/负）。TAM/份额上限/稳态净利率缺省时列入 `terminal.inputs_needed` 与 `gaps`。

**4.6 Price Map**：`P1 = V50 × (1-d_base) × ∏(1-r_k)`；`P2 = P1_low × (1-step_down)`（step 5%–10%）；P1=60%、P2=40%（取消 P2 的情形见 compact §9 强制映射）。`cap_final = min(单票硬上限, 温度仓位上限) × cap系数`：用户提供了两个仓位参数 → 出数值；未提供 → 报告给参数化公式 + 常用档位示例，JSON `price_map.cap.cap_final` 记 `null` 并列入 `gaps`（降级）——**不得自行假定数值**。**强制映射逐条核对**（compact §9）：[R17] 贵金属、[R14] 油价三层暴露、D5 承接池状态、D8 内需暴露、[R19] 规划型、[R5] 双轴、[R1] 追高、[R3] 压测、[R9] 红利三项（缺一不给完整买入型 Price Map，港股红利/底仓标的常因公募分位缺失降级）、[R6] 窗口前 48h 等，命中即按其后果执行。T1/T2 触发按 compact §9 逐条；复评与熔断条件（含 D 层当期强制复评项）逐条列出。结论类型为「仅跟踪价位/仅观察价位」时，只给价位与触发条件，禁止出现买入型执行建议。

### 5 一致性勾稽（报告 ↔ JSON）

- **JSON 是数值底稿**，报告只引用不重算；百分比转换只发生在渲染层。
- 字段级核对（至少）：评级/动作/结论类型/Gate/机制类型与状态/温度/cap_final/P1/P2/T1/T2/五个折扣 r/monitoring 条数与名称/复评与熔断条数/缺口条数；文件名日期 = `meta.valuation_date` = 报告头部日期。
- 报告 §1 DCS 对照 compact §10 清单，最易漏项自查：[R1] 三项逐项、[R4] 成立性、叙事依赖度、双轴、温度、[R6] 逐窗口成行、[R2][R3][R18] 结果、机制分支/状态标注、内需暴露程度（D8 激活时）。

### 6 落盘与幂等

- 写入（UTF-8）：
  - `research/investment-<代码>-<估值日>-research.md`（报告，compact §10 九节 0–8）；
  - `research/investment-<代码>-<估值日>-price-map.json`（本次运行生成，勿手抄）；
  - 刷新 `research/investment-<代码>-latest.json`（与日期文件同内容；`provenance.canonical_file` 记录来源）。
- **幂等**：先查同日同代码产物。幂等键 = 代码 + 估值时点 + 数据最新交易日 + 框架版本 + 包内关键字段指纹。命中 → 复用并只作差异说明；不匹配 → 隔离输出（文件名后缀 `-r2`），**隔离运行不刷新 latest**；覆写须用户明确指示。
- 收尾不提交、不推送；如需入库由用户另行指示。

## 输出

### 报告（严格按 compact §10 的 0–8 九节，不得删节）

0 数据自检；1 DCS（约 20 行必填）；2 Precheck Gate 表；3 机制归类；4 Gate & Non-Price Risk；5 Valuation（含 [R3] 压测明细）；6 Terminal（四步 + 监控表：变量-假设-信号-动作）；7 Price Map（d_base/r_chip/r_v5/r_gov/r_terminal、P1/P2/T1/T2、复评/熔断、窗口期与临时规则）；8 最终结论（含解除冻结/升评级信号）。缺数据节标注 `[需人工补充]` 而非留空。

### JSON（schema v1；实际输出不含注释、不省略键）

```json
{
  "schema_version": "stock-research/v1",
  "meta": {
    "run_at": "ISO8601+08:00", "run_mode": "首次|复评",
    "supersedes": "上期 canonical_file 或 null",
    "provenance": {"canonical_file": "日期文件路径（latest 副本时填写）", "isolation_note": null},
    "source_dates": {"price": "YYYY-MM-DD", "financial_period": null, "percentile_window_end": null, "northbound": null},
    "framework": {"canonical_date": "2026-09-21", "compact_as_of": "2026-09-19", "stale_config_warning": null}
  },
  "company": {"name": "", "code": "600066.SH", "market": "A股|港股", "currency": "CNY|HKD", "data_source": ""},
  "valuation_date": "YYYY-MM-DD",
  "conclusion": {
    "conclusion_type": "完整买入型Price Map|仅跟踪价位|仅观察价位|冻结|否决",
    "rating": "", "action": "买入|观望|回避", "portfolio_tilt": "增配|降配|观察",
    "mechanism": {"type": "", "weight": "", "subtype": null, "state_note": "", "discriminator": ""},
    "dual_axis": "", "temperature": {"value": "冷|中|热|无法判定", "source": "", "effect": ""},
    "r4_validity": "成立|部分成立|不成立", "narrative_dependency": "高|中|低",
    "reasons": ["", "", ""]
  },
  "mandatory_answers": {"main_contradiction": "", "return_logic": "", "axes": {"mainline": "", "inner_demand": {"exposure": null, "hedge": null}}},
  "gate": {"verdict": "通过|冻结|否决", "branches_hit": [], "hard_failures_hit": [], "freeze": {"status": "", "basis": "", "release_conditions": []}},
  "precheck": [{"id": 1, "name": "", "source": "", "verdict": "通过|警惕|不通过|不适用|无法判定", "constraint": "", "evidence": ""}],
  "rules": {
    "R1": {"item1": null, "item2": null, "item3": null, "verdict": ""},
    "R3": {"implied_cut_bp": null, "no_cut_compression": null, "hedge": "", "conjunct": "", "verdict": ""},
    "R9": {"dividend_yield": null, "benchmark_10y": null, "spread": null, "crowding_pct": null, "turnover_pct": null, "complete": null},
    "R18": "", "R20": {"exposure": null, "hedge": null}
  },
  "valuation": {"method": "", "v50": {"low": null, "base": null, "high": null}, "v50_assumptions": [], "chains": [], "asymmetry": "", "v5_scenarios": []},
  "terminal": {"market_cap": null, "k": null, "implied_profit": null, "implied_multiple": null, "reachability": "", "expectation_gap": "", "inputs_needed": []},
  "price_map": {
    "formula": "P1 = V50 × (1-d_base) × (1-r_chip)(1-r_v5)(1-r_gov)(1-r_terminal)",
    "d_base": null, "r_chip": null, "r_v5": null, "r_gov": null, "r_terminal": null,
    "p1": null, "p2": null, "p1_share": 0.6, "p2_share": 0.4, "step_down": null,
    "cap": {"cap_final": null, "temp_cap": null, "single_cap": null, "coefficient": null},
    "t1_triggers": [], "t2_triggers": []
  },
  "monitoring": [{"id": 1, "variable": "", "assumption": "", "signal": "", "threshold": "", "action": "", "linked_rule": "", "source": "", "next_check": ""}],
  "review_triggers": [{"condition": "", "rule_ref": "", "action": ""}],
  "circuit_breakers": [{"condition": "", "rule_ref": "", "action": ""}],
  "qualitative_findings": [{"topic": "", "conclusion": "", "evidence": "", "source": "", "as_of": "", "used_in": ""}],
  "key_inputs": [{"name": "pe_ttm", "value": null, "unit": "", "as_of": "", "source": "pack"}],
  "gaps": [{"field": "", "impact_module": "", "severity": "阻断|降级|注记", "handling": "", "resolution": ""}]
}
```

### 单位与取值约定

- 比率/折扣（d_base、r_chip/r_v5/r_gov/r_terminal、step_down、p1_share、cap 系数、增速、利润率）用 **0–1 小数**，键名不带 %。
- 分位类（估值分位、换手分位、公募持仓分位）用 **0–100**（与 `research/etf-ladder-latest.json` 惯例一致）。
- 价格用交易币种原值（A股 2 位、港股至多 3 位小数）；金额统一「亿」；日期一律 `YYYY-MM-DD`。
- 空值一律 `null`；「无法判定」用枚举字符串——二者语义不同，不可混。

### monitoring 选取原则（≤10 条，硬上限）

1. 只选触发后能改变**结论类型/Gate/评级/取消买入型 Price Map** 的变量；只能改注记的写入报告注记或 `gaps`（次级监控），不占名额。
2. 必含该标的**最脆弱的 2 个假设**：V50 三假设中最敏感的，及 [R3]③ 证据链最弱一环。
3. 至少 1 条来自 compact §8 触发动作的**首要项**（紧缩体制+压测 [R2][R3][R18]）；标的完全不敏感须写明理由。
4. 至少 1 条**筹码/拥挤类**（[R1]/[R9]/[R11]）或**现金流质量类**（Precheck#3、[R14]③）。
5. 命中 [R6] 窗口的标的含最近的 1–2 个在册窗口，`next_check` 填窗口日。
6. 每条齐备：可观测信号 + 阈值/判据 + 触发动作 + 关联条款 + 数据来源；禁止「关注/留意」类不可证伪表述。
7. 同一驱动因素合并去重；按严重度排序；第 11 条起转 `gaps`（field = 次级监控）。

### 回执（对话内一屏）

结论类型 + 评级/动作 + P1/P2（及 cap_final 或参数化说明）+ 两份文件路径（含 latest）+ 缺口统计（阻断/降级各几）+ 下一步（复评触发日/待补字段）。

### 不做的事

不交易建议/金额/分批；不跑取数脚本；不重估宏观；不改框架文件；不提交 Git；不把检索摘要当已验证事实（关键事实须打开原始来源并记日期）。
