# 红利补充数据与交付

原数据包复用量价、股本、财务、行业与宏观。专项只补缺项，不另建完整重复行情管线。公司披露、渠道税务和研究预测仍由研究者核验。

当本批共享规则含「用业务数据检验持有假设」时，从 `business_supplement` 或正文取主营实绩，核公司披露、可比期间及集团/分部范围。按 HD1–HD4A 连到可持续每股分配。主策略对照的历史风格回报保留原口径，分流利差追溯至同批 research_route；可投资替代回报、同币种估值利差分别按 HD5、HD6 取证。旧包缺项按对应冻结方法定向补证。

| 层次 | 来源/字段 | 用途与边界 |
|---|---|---|
| 历史估值 | Tushare daily_basic dv_ratio/dv_ttm/pb/close | 百分数，沿供应商定义；不是前瞻普通股息率 |
| 派息事件 | dividend，cash_div_tax/ann_date/imp_ann_date/div_proc/record_date/ex_date/pay_date/base_share | 税前元/股；base_share万股。cash_div不能直接当特定投资者净现金；预案/实施去重、普通/特别由原文分类 |
| 利率 | 中债公开历史查询的国债到期收益率曲线 10 年列 | 按股票行情有效日取人民币国债 10 年期到期收益率，单位为百分数 |
| 派生 | 同日同币种 dv_ttm − 国债yield | 单位百分点，仅描述历史收益率相对利率，不代替必要权益回报 |
| 研究输入 | 可持续普通分红/未来12月权益/压力、税渠道/汇率 | 不由API自动推算；未知null，不能由TTM复制 |

已核官方文档与发布页：[每日指标](https://tushare.pro/document/2?doc_id=32)、[分红送股](https://tushare.pro/document/2?doc_id=103)、[中债到期收益率曲线](https://yield.chinabond.com.cn/cbweb-pbc-web/pbc/more?locale=cn_zh)。中债国债曲线由中央结算公司在工作日北京时间 17:30 发布。国债数据取自中债公开页面，缺同日有效观测时保留缺口。

按需要执行，路径在当前worktree，估值日选实际有效交易日；日期不匹配保留null：

```sh
/Users/xinquanzhou/miniconda3/bin/python3 scripts/dividend_data.py --code 600900.SH --as-of 20261116 --cache-dir output/cache/investment/dividend --output output/dividend-600900-20261116.json
```

从环境继承TUSHARE_TOKEN，不输出/落盘密钥。曲线缓存以日期/曲线/期限键共享；派息查询无服务端截止，缓存按检索截止日隔离，不能把旧抓取当新公告已查。输出拒绝覆盖，原始成功缓存带sha/查询/取数时刻，失败/空/疑似截断不当成功且不补0；`.dividend-partial-*`不是完成输出。status=complete仅表示请求原料齐，不等于公司证据、前瞻估值或PIT已通过。

历史数据可能后续回填；脚本排除晚于截止的公告/实施状态，不保证历史版本真实复原。原始缓存可能含以后事件，只作取数审计，研究使用过滤后的dividend_events并回原始公告核可见性。没有公开实施日的已实施记录暂不进入历史可用台账。股份拆分、特别分红、重复预案以及税务由研究裁决后才汇总。没有记录不表示零分红。

港股以报价币种HKD的除息记录和最近完整交易日收盘价计算TTM；缺事件覆盖、拆股口径不清或数据超龄保持pending。筛选用中债公开历史曲线，港元估值比较仍需匹配利率/税/汇率。指数官方股息率与5/10年历史分位本工具不获取/计算，数据不足保持null，不用样本平均或今日成分重建“历史官方值”。

供runner使用时，在发布request前把补充包的截止内事实、来源/哈希和缺口附到原data pack；已冻结request/input不修改。手工研究记录补充文件路径/hash。ai_investment的refresh_data_packs先调用classify，使用中国十年期国债，按市场阈值（A股2、港股3.5个百分点，严格大于）冻结research_route；红利分支调用本脚本build补充dividend_addon，普通分支复用build_pack。默认build_pack作为独立工具保持原接口。部署须同时包含两仓修改；本地代码通过不等于生产已部署。分类取最近≤7自然日的股票观测及同日国债，补充分红公告仍截至任务估值日，两个日期不混淆。权限/缺数据最多即时再取一次，仍pending不派研究；港股缺同日中国十年期国债或可核验的港元TTM股息率时保持pending。轻量JSON仍v4，不添加股息字段，审计按冻结合同；报告使用framework/dividend_report_template.md，完整持有期监控/控制由研究者完成。
