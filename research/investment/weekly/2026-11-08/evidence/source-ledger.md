# 本期来源账本

研究日2026-11-08（Asia/Shanghai）；检索/实际读取截至约02:20，数据与披露日期分别列示。普通内置搜索发现后打开正文；未调用Gemini。primary不等于数据完整。外部数字均为公开数据，不是账户执行。

|ID|来源与链接|披露/可得日|数据期|读取层级|采用事实与限制|
|---|---|---|---|---|---|
|S01|[美国财政部CMT日表](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=2026&type=daily_treasury_yield_curve)|2026-11-06|2026-11-02—06|primary;网页及HTTP200原表|10年4.91/4.95/4.90/4.84/4.86%；30年末值5.26%。CMT日度估计，不冒充可成交报价。|
|S02|[Fed声明与发布会](https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20261028.pdf)|2026-10-28|2026-10-28|primary;已读PDF正文及政策问答|声明维持3.75%—4.00%；发布会仍强调通胀过高、政策效果需观察，未提供紧缩路径实质回撤证据。初步逐字稿有修订可能。声明 https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm|
|S03|[BLS就业](https://www.bls.gov/news.release/archives/empsit_11062026.htm)|2026-11-06|2026-10|primary;web正文成功，独立HTTP下载403|非农新增16.5万人，失业率4.1%；就业韧性不是下一次利率决定。|
|S04|[BLS发布日历](https://www.bls.gov/schedule/2026/11_sched.htm)|2026-11-03|2026-11|primary;已读正文，页面最后修改日11/3|10月CPI计划11/10美东08:30，即北京时间21:30；11/8 21:30才进入48小时窗。本次02时段尚未进入。计划可变，未发布值null。|
|S05|[NBS十月PMI](https://www.stats.gov.cn/sj/zxfbhjd/202610/t20261031_1965718.html)|2026-10-31|2026-10|primary;已读正文|制造49.3、新订单49.4、新出口48.7、生产49.8；购进/出厂56.8/51.7为扩散指数。上期已吸收，非本周新数据。|
|S06|[NBS国民经济](https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202610/t20261019_1965618.html)|2026-10-19|2026-09|primary;已读正文|社零同比1.1%；PPI出厂5.0%、购进6.9%，剪刀差1.9pp。不同于PMI扩散口径。|
|S07|[NBS发布日历](https://www.stats.gov.cn/sj/fbrc/bnxxfb/)|2025-12-24|2026-11计划|primary;已读年度表|11/9 09:30计划发布10月CPI/PPI；11/16 10:00月度国民经济。计划不证明未来数值；国内价格发布48小时窗已进入，按公司实质暴露适用R6。|
|S08|[PBOC公开市场211号](http://www.pbc.gov.cn/zhengcehuobisi/125207/125213/125431/125475/2026110208540841613/index.html)|2026-11-02|2026-11-02|primary;HTTP200已读正文|固定利率数量招标隔夜逆回购5410亿元，1.25%，全额满足需求；毛投放非净投放。操作期限改变，不直接与旧7日期限比较为降息。|
|S09|[货币政策操作框架调整公告转载](https://finance.eastmoney.com/a/202610303916569143.html)|2026-10-30|2026-11-02起|secondary;已读全文转载|[2026]13号公告将隔夜作为操作锚、7日改为利率招标。细则仅有全文转载，关键首日执行由S08一手确认，不推断DR007或市场融资成本实际下降。|
|S10|[国务院金融工作情况报告政府转载](https://jrj.sh.gov.cn/ZXYW178/20261106/f143b66dcb244ac2bcf04f28c3d38eda.html)|2026-11-06|报告2026-11-03|政府官方转载;已读全文|汇金类平准、长期资金及资本市场政策工具是制度方向；非已发生增持、具体公司订单或到账凭证。|
|S11|[上交所股票基金周报](https://www.sse.com.cn/aboutus/mediacenter/conference/c/10837029/files/6173403a067e4165b85131e235667847.pdf)|2026-11-06|2026-11-02—06，周五17:00统计|primary;已读7页PDF|上证3649点/周+1.39%，科创50 1253点/周+7.96%，指数为整数展示；PE16.0/84.4按上年盈利且剔亏，非TTM。ETF周成交23381亿元含货币ETF，份额22393亿份、市值36315亿元；非净申赎。|
|S12|[新华财经A股收市](https://www.cnfin.com/gs-lb/detail/20261106/4492047_1.html)|2026-11-06|2026-11-06|secondary;已读正文|沪市7726亿、深市8852亿，合计16578亿为媒体舍入数；上证3649.18、深成11175.78、创业2465.23。不得替代官方完整三日组。|
|S13|[Choice港股收市](https://finance.eastmoney.com/a/202611063924832341.html)|2026-11-06|2026-11-06收市|secondary;已读正文16:10|恒指24481.86，恒科4078.23；日-1.27%/-1.83%。官方指数动态页未返回正文，权威精确值仍null。|
|S14|[KGI转载ETNet收市](https://www.kgi.com.hk/en/market-news-and-analysis/market-news/market-news-feed?id=6094097&iid=bed02497bc854ce5924a8777305e86a8&type=scnews)|2026-11-06|2026-11-06收市|secondary;已读正文17:39|恒指24481整数，主板成交2474.3亿港元；南向净买24.1亿，前日净卖213.3亿。不是周净额，更不等于ETF申赎。|
|S15|[AMD季度业绩](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000188/q32026991.htm)|2026-11-03|2026Q3|primary;已读发行人SEC附件|收入134亿美元、GAAP毛利54%、净利24亿；数据中心收入同比+97%。海外订单需求正证据，不能映射为A/H每家供应商毛利或OCF已兑现。|
|S16|[沪深300事实表](https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/en/000300factsheeten.pdf)|2026-03-31|2026-03-31|primary;已读PDF，但旧期资料|人民币A股大盘宽基300只，2005年发布。只核身份和历史可得性，不使用3月权重冒充11月权重。510300为待核产品候选，当前官网动态页无产品正文。|
|S17|[盈富基金KFS](https://cms.hangsenginvestment.com/cms/ivp/hsvm/document/2800_kfs_e.pdf)|2026-04-17|费用期见文件，跟踪差异2025年度|primary;已读PDF|2800/82800，基础币种HKD，跟踪HSI；ongoing charges 0.060%，2025 NAV对价格指数差+0.1368%，调整后NAV口径-0.1356%；不可将二者当总收益alpha。净值含已计费用，不再重复扣费。|
|S18|[南方东英恒科招募书](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0324/2026032400812.pdf)|2026-03-25|文件版本2026-03|primary;已读附录7|3033，2020/8/28上市；管理费0.99%包含受托/登记服务，但不是全部总费率。当前费率或跟踪差异可能变化，应于个股比较日补核。|
|S19|[恒生科技综合指数简报](https://www.hsi.com.hk/content/dam/wpb/hsil/en_hk/index_flash/content/20261104T000000.pdf)|2026-11-04|截至2026-10-30|primary;已读4页PDF|HSTCI于2026/9推出，271只，含生物科技；HSTCL44/HSTCMS227。三年大小盘差16pp含推出前回溯，不是可交易已实现alpha；总收益口径未确认。行业覆盖不同，不能为更好历史表现替换既有比较。|
|S20|[GovInfo S5548](https://www.govinfo.gov/app/details/BILLS-119s5548is)|2026-09-24|提案版本|primary;已读版本页面|页面最后动作为提出并转委员会；此页面不是穷尽后续立法行动，不能证明全面禁令或截至本周绝无后续进展。历史命名暴露复评保留。|

## 冲突与缺口

- ETNet候选 https://m.etnet.com.hk/www/eng/futures/futures_news_detail.php?newsid=ETE361106190 标题声称收市，却给恒指24533、恒科4081及较低成交，与S13/S14冲突。本轮拒绝作为正式收盘；未核其错误原因，不推断必为午间数据。这是新资料入库排除，未曾采纳，区别于下述历史接续纠错。
- 恒生指数官方动态页面只返回启用JavaScript；510300上交所产品动态页未返回正文、基金官网访问失败。其当期成分/费用/跟踪差异保持unknown。Tushare环境变量缺失，API请求数0；完整沪深成交、两融、交易日历及ETF申赎面板缺口不以搜索摘要填充。
- 11/1、11/6-r2、11/6-r3 handoff的R21结构化window错误沿袭10/21—23，与11/1 calculations的latest_window=10/28—30不一致。本期撤回它们作为可消费的状态包，由新handoff supersede；其不变方法正文和合并采纳事实仍有效。10/11错误change-decision的既有撤回继续，不复活。
- 只记录实际取得的披露。油价同合约结算、黄金/ICE DXY连续同口径、R11正式持仓及全周南向、当前港股估值分位和账户字段unknown/null；没有推断交易或公司研究完成。

## 本地下载审计

下载副本为运行材料，原始链接及摘要随研究发布；下表哈希便于识别本次实际读取字节，不将可变网页当不可变服务。必要方法正文另有正式冻结副本。
- `ust.html` SHA256 `6d338d010cfee8d907a747424ccbcd9dbb61914d14078fbbcaa9b7479d5e968c`；HTTP200。
- `fed-pc.pdf` SHA256 `86147734c39cbc1cbf657bbad2ecc032d8728e298b7f78d3022cf9ea4306e894`；HTTP200。
- `pbc-1102.html` SHA256 `611f6072cffeba10fedd0639bb3aaa48add627dde7f63333b781746faf4b99ec`；HTTP200。
- `sse-week.pdf` SHA256 `d057fd824657b96ee01f2b05e3f6e312c660d6aab3c92e9f5f70a7dd5836f38d`；HTTP200。
- `2800.pdf` SHA256 `a332c7859439a053670d3587e4a264db9a21c30e09c1983511f26c31d08b3244`；HTTP200。
- `hsi-tech.pdf` SHA256 `c71b7ae3f0fb88e4077dfb97cd6e4dd4337e134bf9e1d8b6d9880d486974b607`；HTTP200。
