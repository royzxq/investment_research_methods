# ADR：冻结研究身份与 DSH 回执编码

日期：2026-11-01（Asia/Shanghai）。状态：用户已授权修复；2026-11-01 已将经离线回归和独立审查的补丁应用到本机实际运行仓库。服务未重载，未触发研究；后续新进程读取此版本。

## 问题与选择

价格地图 writer 原样复制模型输入的 `meta.name`，本地 check 只验证结构，最终 exchange 却严格比较冻结任务名，造成别名／上市后缀漂移在研究结束后才失败。DSH headless 的 `--json` 约束事件流，`final.text` 仍是模型正文；完整 JSON 被一个 Markdown 围栏包裹时，旧接收器拒绝。两者均不是提高超时或增加重试次数能可靠解决的问题。

本机官方 CLI 没有最终回执 schema 参数。只生成回执文件再要求模型复制，仍不能保证 final 不带围栏；改为文件/MCP 交付则需要另一套提交和冻结协议。本次采用确定性身份绑定和受限的传输编码兼容，保留业务接收门禁。

## 身份来源

`stock_price_map.py build/check --execution-folder <本次尝试目录>` 读取并验证现有冻结 request、framework snapshot、input、prompt、targets、receipt schema。目录须对应真实 batch/task/provider；重试仅对应自己的 `retry-1` 暂存目标。上下文与目标路径不接受符号链接；缺 snapshot 拒绝，不在 writer 中迁移历史。

build 先严格核对 code（含市场）、valuation_date、generator、report_path 和完整暂存输出路径，再将 name 取自同一冻结 task。只改变新输出的名称元数据，原始 writer 输入、报告、价格与研究结论不改。check 对名称严格比较、绝不修正；最终 exchange 的 code/name/date/generator/path/hash 门禁原样保留。元数据绑定不证明报告的公司事实或研究语义正确。普通独立运行未指定上下文时保持原有显式名称行为。

runner 的实际交付指令传入该选项，不修改已冻结 prompt/input/hash。现有 writer 的 `--legacy-snapshot` 路由和旧交付版本保持原约束。

## 回执传输与历史边界

实际命令准备时，新建 `research-dsh-runtime/v2`，固定 `receipt_encoding=strict-json-or-single-json-fence/v1`。仍要求模型输出裸 JSON；接收时仅额外允许整个正文（可含外围 ASCII 空白）恰为一个小写 `json` 标记的三反引号围栏，开闭围栏各独占一行，LF/CRLF 均可。只解包一次，内部继续使用原严格 JSON 解析：重复键、NaN/Infinity/溢出、非对象、多个对象、解释文字、多个围栏、不完整或无语言围栏均拒绝。

`_events` 先验证新 session、有序 completed 终态及未截断 final，然后才解包。回执身份、status/reason/path、报告绑定、哈希、审计和发布门禁不变；不根据 exit0、产物存在或围栏替失败回执宣称完成。业务 request/result/sealed 与 price-map schema 均不升级。

编码策略按**尝试的 runtime 文件**冻结：已有 v1 runtime 继续只收裸严格 JSON；新准备的首次尝试或新 retry 使用 v2。旧 request 已 prepare、但尚无 runtime 的尝试，也会在未来 command 阶段得到 v2。未知版本/编码、v1携带编码覆盖均拒绝；既有 runtime 不原地升级、不重解释旧 final、不重跑已启动记录。

父 runner 在启动 CLI 前把 runtime 原始字节留在内存，并在解析回执前、成功发布前核对；审计 `process.json` 只记录其 SHA-256，校验不从可被子进程修改的磁盘 process 字段取信任值。原有 patch/plugin 哈希检查保留。

恢复成功记录的只读复核，在重新解析回执前校验 process 记录的 runtime SHA-256；v2 必须有合法且匹配的哈希，v1 仅历史未记录哈希时允许缺失，已记录则同样核验。这是持久化证据的一致性检查，不代替执行时内存信任根。

## 诊断与验证

严格 JSON 错误包含来源标签及解析行列；非法 UTF-8、重复键和非标准常量使用固定错误分类，不回显正文、重复键值或异常链。通用 JSON 解析器不支持围栏。

离线回归覆盖身份先拒绝后绑定、原名 check 拒绝、首次/retry路径、上下文篡改与符号链接、独立 writer、v1/v2 分界、恶意 JSON/围栏、错误回执身份/路径、有序终态以及 runtime 在解析前和发布前被篡改。使用 fake CLI 走完整 runner 与真实 writer，不调用真实模型或研究 API。

调度额度、并发、冷却和一次重试保持原值。不修改队列、历史失败、正式报告或交易状态。隔离版本经 1225 项全仓离线回归及独立 Astra 审查后应用到本机运行目录；本次不提交、推送、合并、重载或触发研究。
