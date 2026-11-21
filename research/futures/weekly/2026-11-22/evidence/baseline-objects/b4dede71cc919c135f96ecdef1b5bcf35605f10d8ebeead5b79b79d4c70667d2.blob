# 项目运行环境

最后核验：2026-10-04，当前 Mac 本地 Codex 会话。此文件保存环境事实与取数入口，业务规则以 `framework/` 和对应 skill 为准。

## Python

期货与 ETF 取数优先使用 `/Users/xinquanzhou/miniconda3/bin/python3`。迁移时离线确认该解释器可启动，环境为 **arm64、Python 3.11.7、已安装 tushare 1.4.29**。可在仓库根目录以研究日期显式调用：

```sh
/Users/xinquanzhou/miniconda3/bin/python3 scripts/future_data.py --as-of YYYYMMDD
/Users/xinquanzhou/miniconda3/bin/python3 scripts/etf_data.py --as-of YYYYMMDD --pool-csv /absolute/path/investment_prediction.csv
```

旧 Claude 记忆记录过 Rosetta/x86_64 Python 与 arm64 numpy 混装导致导入失败；这是旧运行环境的问题，不能视为当前 Codex 状态。若更换解释器，再核对架构与依赖。现有 `.venv/` 与 miniconda 是不同环境，暂保留；迁移不把 `.venv/` 当作 Codex 配置。

## 环境变量与实际调用验收

本轮仅检查是否存在，确认 `TUSHARE_TOKEN`、`GEMINI_API_KEY` 已由当前会话继承。未读取、输出或复制变量值。期货和 ETF 脚本从 `TUSHARE_TOKEN` 取认证；`GEMINI_API_KEY` 仅供需要 Gemini 的后续工作流使用。

变量存在与解释器可启动不能证明联网调用、账号权限或数据字段可用。首次恢复相应工作流时，以实际接口返回和产物自检验收；本次迁移未运行联网行情或新的研究。

Gemini stdio 服务已注册到 Codex 全局配置并通过握手、工具发现与离线故障测试。2026-10-04 在允许联网的调用中，Google 返回 HTTP 400 `User location is not supported for the API use.`；当前 Gemini 成功搜索仍受地区条件阻断，内置搜索及页面读取兜底已实际完成。已有聊天需重新载入 MCP 配置后确认工具可见，不把本条历史错误当成以后每次调用的结果。

## ETF 外部研究池

ETF 快照的研究覆盖率默认参考 `/Users/xinquanzhou/Workspace/ai_investment/investment_prediction.csv`。迁移后的 skill 可通过 `ETF_POOL_CSV` 覆盖该路径，再把选定值传给脚本的 `--pool-csv` 参数；**脚本自身只接收该命令行参数，不自行读取 `ETF_POOL_CSV`**。单独运行脚本时可直接指定其他文件。

该 CSV 用于研究覆盖率，属于外部数据输入。本次迁移不恢复旧 ETF 决策卡、`current.json` 或跨仓交易接口；当前研究边界见 [ETF 框架 v2.1](../../framework/etf_framework.md)。未提供研究池文件时，快照不计算覆盖率，缺口按脚本输出记录。

## 快照与缓存

取数脚本把完整快照写入 `research/futures/snapshots/` 或 `research/etf/snapshots/`；末行“快照完成”是完整标记。期货协议见 [FUTURES_DATA_PROTOCOL.md](../../framework/FUTURES_DATA_PROTOCOL.md)。ETF v2.1 沿用 v2.0 快照格式，不能仅因头行为 v2.0 判旧；还须按当前 skill 检查日期、完整性和指数覆盖。

`output/` 是 Git 忽略的行情与自聚合原始缓存，已作为迁移资产单独备份。历史快照和缓存只证明各自日期的数据，不证明当前行情、事件状态或账户持仓。

目录迁移后缓存分到 `output/cache/futures/` 与 `output/cache/etf/`；两脚本均以仓库根定位，不依赖 shell 当前目录。正式快照默认拒绝覆盖，成功且标记一致才原子发布；失败保留被忽略的 `.partial`，旧正式快照不变。显式 `--overwrite` 仍须符合任务授权。ETF 日期机器读数保存在 snapshots，latest 只在 `output/indexes/`。

## DSH 首批工具运行时（2026-11-03）

DSH 0.2.1-rc.2 已隔离实测官方 `deepseek-search-api` 和 AKTools stdio。生产选择与冻结/回退说明见 [DSH 工具 ADR](../adr/ADR-20261103-dsh-research-tools.md)。Fetch API 样本未通过，默认仍为 `http`；原 PDF 下载/PyMuPDF 核页路径保留。

AKTools 使用本仓独立 `output/runtime/aktools-0.1.4/bin/python`，不依赖系统 Python 或投研脚本的 conda 包。已核验 Python 3.11、AKTools 0.1.4、AKShare 1.20.22、MCP 2.3.0，完整依赖固定在 `config/dsh_aktools-0.1.4-r1.requirements.txt`，运行前对照同名 lock JSON。新 checkout 需要显式重建环境；自动投研不会执行 pip 或自行升级：

```sh
/Users/xinquanzhou/miniconda3/bin/python3 -m venv output/runtime/aktools-0.1.4
output/runtime/aktools-0.1.4/bin/python -m pip install -r config/dsh_aktools-0.1.4-r1.requirements.txt
```

API 的网络、币种、字段口径仍按每次实际返回核验；安装/预检成功不代表任意接口可用。日志按尝试保存在 `dsh-aktools/`，DSH 的汇总统计在 `runner/dsh-metrics.json`；密钥、提示词和命令正文不进入汇总。

## DSH 取数体检（2026-11-08）

新准备批次最初启用 `dsh-deepseek-flash-high-health-v1`，保留原工具与模型，增加 `data_health=data-health-v1`。原生网页取数与 AKTools get_data 前后自动检查，并将原响应和体检记录保存在每次尝试的 `data-health/`；财务语义细检限已验证的两类接口，其他接口只做通用结构与分页检查。bash/curl、PDF 等路径仍按技能人工/模型核验。旧冻结计划不变，不用新体检追认历史。实施、回退和未覆盖范围见 [体检 ADR](../adr/ADR-20261108-dsh-data-health.md)。

## DSH 有界补证（2026-11-08 后续）

按用户后续授权，当时新准备批次进一步选择 `dsh-deepseek-flash-high-recovery-v1`，叠加 `evidence_recovery=evidence-recovery-v1`。原生体检提示的网页截断/空壳、PDF不支持和分页不足会进入有界补证；新增工具支持公开文档下载、按页/范围读取、原页渲染及绑定读取凭证的采用记录。自动补证与原工具返回分开，效果记录进入每次尝试的 `evidence-recovery/` 和 `runner/dsh-metrics.json`。本机继续复用已验证的 PyMuPDF 解释器，不安装新依赖。原 health profile 留作回退，旧冻结计划不变。范围、预算、取消及事实核验边界见 [补证 ADR](../adr/ADR-20261108-dsh-evidence-recovery.md)。


## DSH 长正文与上下文接续（2026-11-08 后续）

当前新准备批次使用 `dsh-deepseek-flash-high-context-v1`，在体检及补证上叠加 `evidence-context-v1`。原生网页和恢复文档进入每次尝试的 `evidence-context/`，通过短定位簿、稳定 evidence_id 和原件哈希跨裁剪/压缩接续。关键输入与反证标记保留口径和未决状态；新 runner 对最终暂存报告核引用文字、链接、位置和已标记的必引项。无登记引用时为 not_exercised，不视为已核事实。需要本机 Node.js 20+（本次22.14.0），复用现有DSH/PyMuPDF，不安装依赖。旧冻结批次不变；回退选择 recovery-v1。范围、原件保留要求、验证和语义边界见[上下文 ADR](../adr/ADR-20261108-dsh-evidence-context.md)。
