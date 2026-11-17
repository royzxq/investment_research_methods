# 红利补充数据与交付

原数据包复用量价、股本、财务、行业与宏观。专项只补缺项，不另建完整重复行情管线。公司披露、渠道税务和研究预测仍由研究者核验。

| 层次 | 来源/字段 | 用途与边界 |
|---|---|---|
| 历史估值 | Tushare daily_basic dv_ratio/dv_ttm/pb/close | 百分数，沿供应商定义；不是前瞻普通股息率 |
| 派息事件 | dividend，cash_div_tax/ann_date/imp_ann_date/div_proc/record_date/ex_date/pay_date/base_share | 税前元/股；base_share万股。cash_div不能直接当特定投资者净现金；预案/实施去重、普通/特别由原文分类 |
| 利率 | yc_cb 1001.CB、curve_type=0、curve_term=10 | 中债国债到期收益率曲线，百分数；非活跃券、非即期曲线；单独权限 |
| 派生 | 同日同币种 dv_ttm − 国债yield | 单位百分点，仅描述历史收益率相对利率，不代替必要权益回报 |
| 研究输入 | 可持续普通分红/未来12月权益/压力、税渠道/汇率 | 不由API自动推算；未知null，不能由TTM复制 |

已核官方文档：[每日指标](https://tushare.pro/document/2?doc_id=32)、[分红送股](https://tushare.pro/document/2?doc_id=103)、[国债曲线](https://tushare.pro/document/2?doc_id=201)（2026-11-17读取）。当前接口权限仍以真实请求为准；无权限不申请付费、不切未声明口径。

按需要执行，路径在当前worktree，估值日选实际有效交易日；日期不匹配保留null：

```sh
/Users/xinquanzhou/miniconda3/bin/python3 scripts/dividend_data.py --code 600900.SH --as-of 20261116 --cache-dir output/cache/investment/dividend --output output/dividend-600900-20261116.json
```

从环境继承TUSHARE_TOKEN，不输出/落盘密钥。曲线缓存以日期/曲线/期限键共享；派息查询无服务端截止，缓存按检索截止日隔离，不能把旧抓取当新公告已查。输出拒绝覆盖，原始成功缓存带sha/查询/取数时刻，失败/空/疑似截断不当成功且不补0；`.dividend-partial-*`不是完成输出。status=complete仅表示请求原料齐，不等于公司证据、前瞻估值或PIT已通过。

历史数据可能后续回填；脚本排除晚于截止的公告/实施状态，不保证历史版本真实复原。原始缓存可能含以后事件，只作取数审计，研究使用过滤后的dividend_events并回原始公告核可见性。没有公开实施日的已实施记录暂不进入历史可用台账。股份拆分、特别分红、重复预案以及税务由研究裁决后才汇总。没有记录不表示零分红。

港股输出显式缺口，不调用A股接口替代；需港币匹配利率/税/汇率。指数官方股息率与5/10年历史分位本工具不获取/计算，数据不足保持null，不用样本平均或今日成分重建“历史官方值”。

供runner使用时，在发布request前把补充包的截止内事实、来源/哈希和缺口附到原data pack；已冻结request/input不修改。手工研究记录补充文件路径/hash。外部ai_investment调度与默认build_pack未改，不能声称补充脚本已自动接入生产。JSON仍v4/audit-v6，不添加股息字段；报告使用framework/dividend_report_template.md，完整持有期监控/控制由研究者完成。
