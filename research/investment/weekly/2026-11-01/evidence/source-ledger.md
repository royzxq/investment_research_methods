# 本期来源账本

generator=codex；研究/实际读取日2026-11-01（Asia/Shanghai）；证据截至本次运行，行情锚10/30。本文为实际阅读后的事实摘录与适用边界，不是原网页全文。原始行情另存tushare-inputs.json；摘要不冒充公司研究。

| ID | 原始来源与披露日/数据期 | 已读事实、口径及限制 |
|---|---|---|
| F1 | [Fed声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm)，10/28 14:00 EDT（北京10/29）；10/27–28会议 | 10比2维持3.75%–4.00%；反对者Cook与Hammack要求加25bp；声明称通胀仍高，继续收集信息。已读正文15–21行。不加息成立；声明未明确宣告紧缩路径回撤。没有读取发布会逐字稿，路径回撤子项unknown；不据此宣称已证伪回撤，亦不放宽。 |
| F2 | [Treasury CMT](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202610&type=daily_treasury_yield_curve)，逐交易日公布；10/26–30 | 十年5.00/4.99/5.05/4.98/4.94%，三十年5.31/5.30/5.37/5.32/5.31%。已读原表567列头及585–589行；最新五日严格>5%不成立，30年未突破历史10/9的5.60锚；不把收益率回落等同政策出口。 |
| C1 | [国家统计局10月PMI](https://www.stats.gov.cn/sj/zxfbhjd/202610/t20261031_1965718.html)，10/31 09:30；2026年10月 | 内置页面读取失败后以requests直读原URL，HTTP200，标题及10月表格核验。制造业49.3（9月50.1），生产49.8，新订单49.4，新出口48.7；原料购进/出厂价格扩散指数56.8/51.7（9月60.8/54.0）；非制造业商务49.7，建筑48.0、服务50.0，综合49.7。扩散指数不能当PPI同比或企业毛利。原表数值冻结于nbs-pmi-values.json，完整响应只留output用于核验。 |
| I1 | [Microsoft FY27Q1](https://www.microsoft.com/en-us/Investor/earnings/FY-2027-Q1/press-release-webcast)，10/28；截至9/30季度 | 收入923亿美元，同比19%；营业利润459亿美元，同比21%；净利GAAP增长32%而剔除OpenAI投资影响后18%；Cloud收入639亿美元、增长30%，Azure增长48%。收入增长支持海外云需求，不能替代A/H订单、毛利与回款；未核财报电话会capex指引，不以销售增长充当capex上修。 |
| I2 | [Amazon Q3](https://www.aboutamazon.com/news/company-news/amazon-earnings-q3-2026-report)，10/29；截至9/30季度及TTM | AWS收入460亿美元、同比约39%；营业利润178亿美元。集团TTM OCF1683亿美元，但FCF流出424亿美元；净购置固定资产同比增加948亿美元，主要反映AI投资。季度经营收入与TTM现金流分开，不能把FCF为负等同核心盈利被证伪，也不能把投入等同国内供应商订单。 |
| H1 | [每日经济新闻](https://www.nbd.com.cn/articles/2026-10-30/4631070.html)，10/30 17:10；10/30收盘 | 已读正文：恒指23294.42、日+1.46%、月-5.36%；恒科3754.90、日+0.29%、月-11.73%；消费股领涨，南向净卖出超过35亿港元。这是媒体行情，非交易所原件；南向精确值/全周连续序列仍null。单日反弹不能证明估值便宜、红利不拥挤或资金持续承接。 |
| P1 | [商务部经贸成果解读](https://english.mofcom.gov.cn/News/SignificantNews/art/2026/art_c7903a2767d5475690e6e8d15839d817.html)，正文标Released September28，索引9/30；9/20–23磋商 | 官方正文第VIII部分说明双方同意将吉隆坡安排延至2027/1/10；第II部分300亿美元互降关税安排尚需各自程序并另行公布。属于补核既有政策背景，非本周新协议；具体税号实施/企业受益仍缺，不能以旧11/10机械冻结全出口链。政策共识不代替公司订单。 |
| P2 | [GovInfo S.5548 IS](https://www.govinfo.gov/app/details/BILLS-119s5548is/related)，9/24提案；11/1读取 | 已读元数据列最后行动9/24、Introduced in Senate、转委员会。仅证明此IS版本；Congress all-actions本次不可读，完整最新立法链unknown。不接受搜索中第三方“Passed Senate”作成法凭证；维持原命名敞口待复评，不认定全面禁令。 |

继承来源：10/25已采用market-research-r2、change-decision-r2及macro-sources/industry-sources、10/18 source-ledger和10/11未撤回market-research。9月美国CPI3.7/核心环比0.3、中国社零1.1、PPI购进6.9/出厂5.0为已采纳历史数据期，未声称本次重新下载这些原件。R20仍因已核社零未>2而不满足；贷款子项null。10月PMI不能代替同月社零和贷款。

截至本次原始数据取得：Tushare六次调用成功（trade_cal、四指数、margin）。指数成交额千元转万亿元除1e9；全深圳用399106.SZ，不能用399001成分样本。完整两融采用SSE+SZSE+BSE的rzrqye，缺一个交易所即null。最新完整余额10/29为23849.60766121亿元；10/30只有SSE。最新窗口10/28、29、30由SSE交易日历校验；官方科创50收盘原件未取得，供应商数值单列，helper输入官方字段null。即使该字段缺口，10/29量能及两融已使AND失败。

缺口：FOMC发布会完整措辞、精确政策实施税号、国内最新货币市场利率/贷款原文、官方指数原件、10/30完整两融、ICE同主力五日结算、黄金/ICE DXY连续序列、港股全周资金/估值分位/股息利差/拥挤度、公司入账与完成配对、真实账户。全部保留unknown/null，不用现货、Fed广义美元、搜索摘要、第三方标题替代阈值输入；对外投资NPRM正式刊登状态本次原页面不可读，仅继承上期拟议属性，不写生效新禁令。

本期未发现须新增撤回的已采纳错误源。上期仍有效的withdrawn_sources原样继承；旧报告当时的未知/未来窗口是历史事实，本期状态替代不把它们追溯判错。未读取的未来材料不纳入。
