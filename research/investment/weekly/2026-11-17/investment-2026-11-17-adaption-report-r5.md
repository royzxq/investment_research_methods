# 个股调研框架更新结果 · 自动红利路由

## 1. 更新结论

method_change=true；state_refresh=false；evidence_correction=false。用户明确采纳2个百分点的默认自动选轨方案，本地实现已应用；尚未合并本轮改动或部署，不推送远端。此前拆分及中性校准的本地dev合并保留。

## 2. 受影响模块

共享C0定义新自动入口，红利HD1/compact和两轨技能同步；报告§0记录分类规则与读数。methods dividend_data提供共用classify/validate_route与分红补充。AI每日refresh_data_packs先分类后调用基础数据包，红利另调用补充脚本；API统一经过DataAdapter。request元数据冻结结果，producer与consumer均校验，Codex/DSH提示选择相应技能与模板。

## 3. 修改说明

默认阈值2个百分点，严格>，等号归普通；截至估值日最近股票观测最长7自然日，利率与其同日同币种。缺值不补0；最多即时再取一次，失败不发任务、不标记财报已消费。每次尝试独占保存，新调用/重试使用独立缓存避免旧缺失快照阻断新数据；红利补充复用成功分类的行情/国债缓存，分红公告仍截至任务估值日。下轮可重新分类，但本批恢复冻结且切换逐条审旧控制。

4.01%-2%=2.01个百分点进红利；3.99%-2%=1.99进普通；4%-2%=2恰好等号进普通。特别分红或周期顶部可令候选误入红利，随后必须在红利研究中否定其可持续性，不以分类替代质量判断。较低股息率的分红成长公司可能落普通轨，此乃所选机械分工的限制，手工长期收息研究仍有独立入口。

## 4. 不应过度反应

不修改价格JSON v4、controls-v10/audit-v7或交易许可；同公司唯一V50/P1/T1。旧冻结的提示/输入/哈希不追补分类，旧限制不因换轨解除。原5项pending、4项撤回和25项规则评估原样接续；本轮无公司完成凭证，不清账。

## 5. 新版框架链接

[共享C0](../../../../framework/stock_research_common.md)、[红利框架](../../../../framework/dividend_framework.md)、[原股票框架](../../../../framework/investment_framework.md)、[红利模板](../../../../framework/dividend_report_template.md)。AI配置为config/research_strategy.json，跨仓定位用INVESTMENT_METHODS_ROOT，默认同级investment_research_methods；两仓版本需同步。

## 6. 版本变更记录

本地方法stock-strategy-split-v3-common-v4-dcf-v4；共享v4、红利v3。新handoff r5接续r4，不改历史来源。旧无自动路由与新路由是不同任务入口，不声称两种选择方法投资语义相同。

- canonical 旧SHA256 `3d84e1ebace78c0c5d86451abbc27ceefc677c34d7dd94bba0c5ef97168289a6` / 方法 `dd58bde52f5e97a9773b5af1ba861452897c2d948f81aad429cb79f21436614c`；新SHA256 `bfef2f8603571d71268c987e38a585d039dbfec55ebbf565c7c13349fbe5fc47` / 方法 `d75d0277eebfb1f87059b231be5da210a7f53f7ca5a067b17182bf2f1274074a`。
- compact 旧SHA256 `8f18a6c7c44a3dd2401f887ec1af2ebb6cc2895120ed2c413de1a5a5dff46bf7` / 方法 `267d8e62707eb2fb251af8223346dd6bf642a84ef1e4bc3fcf586ef29985a46a`；新SHA256 `4dcf624ed7708cfe662c63188b4c84565a480c614ef3d25c14af434ea0e57aed` / 方法 `49f6af6f35afe616bde6f3f4d061a9fca618f4f3a6dbcc4ebccc32d4a230b4a9`。

## 7. 验证与审查

- AI定向80项通过：编排、阈值配置、先分类顺序、红利专属补充、有限重试、逐只失败、财报不消费、旧发布契约与安全错误。
- methods全量1449项运行：1403项通过，46项因沙箱禁止回环监听/ps阻断；提升测试环境后仅重跑这46项全部通过。随后新增两项边界用例，相关36项定向回归通过。完整命令为python3 -m unittest discover -s tests -v；未声称首轮全绿。
- 跨仓隔离演练走实际run→publish_request→prepare_request→verify_prepared，用模拟外部数据验证红利/普通各1只和待补1只，只有红利请求dividend；使用production runtime配置冻结Codex+DSH四份正确技能提示，恢复校验通过。未调用外部模型完成真实公司研报。
- 真实API探针：600900.SH、2026-11-16，dv_ttm=3.2798%，yc_cb不可用、利差null，两次分类均pending，未发布任务。yc_cb单独权限见[官方文档](https://tushare.pro/document/2?doc_id=201)。本轮真实路径不能证明成功分类；港股自动采集尚缺可核验TTM/HKD基准，明确pending，不用A股输入替代。
- 两个修改技能quick_validate、股票治理和git diff --check通过。检查只证结构/边界，不证金融有效性。
- 高强度正确性自审发现原尝试缓存会阻止有效重取，已改逐次隔离缓存并测试；审查日期、单位、未知、冻结恢复与错误隔离。六维检查：数据访问归adapter、无无关改动/秘密/交易、无废弃分支复活、仅同一分流特性、ADR先行且契约同步、真实与模拟验证区分。实际阻碍保留为国债权限/数据与港股数据接入，不能标作生产可用。

## 8. 精简版同步

本轮仅按共享C0与HD1授权范围同步，完整定义/数值2/严格>/7自然日/未知/手工例外/旧控制均保留，原R/D/HD编号及未改段落不重写。抽检正例、等号、缺利率均与canonical同决策；依赖哈希显式sync后治理通过。没有宣称全框架100%语义等价；本次不重新核验历史市场观测。体积变化如下：

- investment_framework.md：100560 → 101204 UTF-8字节。
- investment_framework_compact.md：88528 → 89035 UTF-8字节。
- stock_research_common.md：36151 → 37255 UTF-8字节。
- dividend_framework.md：17895 → 18130 UTF-8字节。
- dividend_framework_compact.md：8357 → 8836 UTF-8字节。
- dividend_report_template.md：3020 → 3320 UTF-8字节。
