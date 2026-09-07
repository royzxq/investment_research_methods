# investment_research_methods

两条并行的研究方法论自动化流水线的本地存档，每周分别由 claude.ai 云端 Routine 自动运行。两条轨道共享同一个仓库，文件互不重叠（期货侧文件无前缀，股票侧文件统一带 `investment-` 前缀），互相独立、互不干扰。

## 期货轨道：meta future analysis → future change analysis → future adaption → future data sync

- **v2.22 默认采用有限数据模式 `public_data`**：先查 MA/RB 的现有行情与合约资料，再为进入研究的候选选择至少一项合适的公开产业证据。专业船流、战争险、装置/利润数据库不再是全池必填项；依赖它们的强因果模型保留原验证要求并可转 `research_only`。详见 `framework/FUTURES_DATA_PROTOCOL.md`，三阶段及报告A都须与 canonical 一起读取。
- 研究输出与执行核验分步：先给具体逻辑、方向、价格计划和期限，再核实际账户、挂单、费用、保证金与执行压力。研究无需付费专业全链，真实交易输入仍不得猜测。新版改动与验证记录见 `research/2026-09-07-data-accessibility-adaption.md`。
- `projects/{meta_future_analysis,future_change_analysis,future_adaption}/INSTRUCTIONS.md` — 三个 Claude.ai Project 的原始 instruction
- `framework/futures_framework.md` — 现行「期货投资分析框架」活文档，只能通过分支 + PR 更新，不直接改 main
- `framework/futures_framework_compact.md` — **仅供人阅读**的去冗余衍生文件（剥离历代【本次更新】标记与版本簿记），由 `framework-condense` 阶段在每次框架更新时从 canonical 全文自动再生，勿手改；**任何 AI/流水线环节一律使用上面的 canonical 完整版**
- `scripts/future_data.py` — 框架配套取数脚本（Tushare/akshare），版本随框架结构性变化同步迭代；本身无网络环境无法线上实测，改动需人工在有真实数据源的环境里运行验证
- `scripts/price_evidence.py` — v1.10取数脚本使用的离线价格证据模块：区分 settle/close、SC专用结算周涨、固定合约对1/5/10交易日价差变化与同期样本验收。周涨按最新已完成行情日减7自然日，不按研究日减7天；没有最终结算则不使用收盘价替代护栏。脚本仍需用户已有Tushare权限，未新增无Token的CSV导入入口；可由研究方读取终端导出作为独立证据，不等于脚本自动支持导入。
- `scripts/futures_risk.py` — v2.21起的离线A计划校验与风险容量计算；JSON CLI为 `python3 scripts/futures_risk.py validate-a --input plan.json` / `python3 scripts/futures_risk.py size --input sizing.json`，字段见函数说明。计算通过只代表计划/容量校验完成，不授予完整交易许可；缺实际账户、止损或容量信息保留 `null`。
- `projects/future_change_analysis/EXECUTION_AUDIT_TEMPLATE.md` — 每周执行诊断的唯一口径；无论框架是否更新，都生成 `research/<date>-execution-audit.md`，分开记录未触发、已知阻断、研究未完成与满足执行条件。
- `scripts/validate_futures_audit.py` — schema 2 JSON或含唯一JSON审计块的Markdown结构校验器：`python3 scripts/validate_futures_audit.py --input research/<date>-execution-audit.md`。检查状态、门适用性、证据日期和未知账户空值；不验证来源真伪、不计算投资收益、不授予交易许可。无本地执行环境时须明确未运行，按模板清单检查。
- `research/` — `baseline-market-research.md`（day-0 基线）+ 按日期命名的 `<date>-market-research.md` / `<date>-change-decision.md`（始终直接 push 到 main）/ `<date>-adaption-report.md`（框架需要更新时才有，走分支 + PR）
- `.claude/skills/` — `meta-future-analysis` / `future-change-analysis` / `future-adaption` / `future-data-sync`（四个阶段包装）+ `framework-condense`（compact 再生，两轨道共享）+ `futures-weekly-review`（编排器，统一开 PR）

期货离线回归验证：`python3 -m unittest discover -s tests -v`。A计划校验器仅支持MA/RB/SR同品种1:1月差，必填 `price_unit="CNY/tonne"`；Entry/SL/TP必须为元/吨的绝对价差，乘数为吨/手。单位缺失或不兼容时不计算风险金额或R，不推断或换算百分比；纯风险计算不访问行情或账户，输出不能当作已成交或账户实仓证明。取数脚本的2ATR数量是预检参考，旧版“距50分位风险”和“主仓触发”标签自v2.21起停用。 低敞口组合上限按用户配置取 `min(净值×3.5%, 5000元)`，含持仓与挂单风险；输出以 `portfolio_risk_cap_normal/current` 区分常规和当前生效上限，不使用低敞口比例乘数。

## 股票轨道：meta investment analysis → investment change analysis → investment adaption

- `projects/{meta_investment_analysis,investment_change_analysis,investment_adaption}/INSTRUCTIONS.md` — 三个 Claude.ai Project 的原始 instruction；字段口径与期货那套不同（`DOMINANT_RETURN_DRIVERS`/`FRAGILE_NARRATIVE`/`research_meaning`，`investment_adaption` 输入变量名为 `CURRENT_STOCK_RESEARCH_FRAMEWORK`）
- `framework/investment_framework.md` — 现行「个股调研框架」活文档，本质是逐股分析用的参数化模板（含 `{{COMPANY_NAME}}`/`{{TICKER_OR_CODE}}`/`{{VALUATION_DATE}}` 占位符），不是像期货框架那样对所有标的通用的执行规则集；同样只能通过分支 + PR 更新
- `framework/investment_framework_compact.md` — **仅供人阅读**的去冗余衍生文件，由 `framework-condense` 阶段自动再生，勿手改；**任何 AI/流水线环节一律使用 canonical 完整版**
- 框架 Section 0 提到配套取数脚本 `stock_data_pack.py`（对应期货侧 `future_data.py` 的角色），目前本仓库与 `ai_investment` 均未找到该脚本，暂未设计联动同步阶段
- `research/` — `investment-baseline-market-research.md`（day-0 基线，可为空——为空时首次运行按"无历史基线"处理，不是错误）+ `investment-<date>-market-research.md` / `investment-<date>-change-decision.md`（始终直接 push 到 main）/ `investment-<date>-adaption-report.md`（框架需要更新时才有，走分支 + PR）
- `.claude/skills/` — `meta-investment-analysis` / `investment-change-analysis` / `investment-adaption`（三个阶段包装）+ `framework-condense`（compact 再生，两轨道共享）+ `investment-weekly-review`（编排器，统一开 PR）
