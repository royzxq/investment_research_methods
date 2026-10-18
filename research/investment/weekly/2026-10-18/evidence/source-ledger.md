# 本期来源核验与事实摘记

generator=codex；研究日/访问日：2026-10-18，Asia/Shanghai；证据访问截止约09:00。以下是研究者整理的事实记录，并非网页原文副本。原始网址、实际读取范围、披露日和数据期分别列明；不把检索摘要算作正文。API 原始回执见同目录 `tushare-inputs.json`，计算见 `calculations.json`。动态网页今后可能变动，本表与原始 API 回执冻结本次实际使用的信息。

|ID|来源及原始网址|披露/数据期|实际读取与可支持事实|
|---|---|---|---|
|S01|[BLS 9月CPI存档](https://www.bls.gov/news.release/archives/cpi_10142026.htm)|10/14 08:30 ET；2026年9月|正文与Table A已读：总CPI同比3.7%、季调环比0.6%，核心环比0.3%、同比2.6%。超过现行观察分支的3.6%/0.3%，总同比未超过4%。|
|S02|[财政部10月CMT](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value_month=202610&type=daily_treasury_yield_curve)|10/16数据，美东披露对应北京时间不晚于10/17|表头和行已读；10年期10/9、13、14、15、16为5.24/5.21/5.19/5.10/5.09%；30年10/16为5.43%。10/12无表行，不补自然日。|
|S03|[Fed 9/16声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm)；[会议日历](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)|9/16；日历更新10/7|声明利率段、2026日历已读：目标3.75%–4.00%，10/27–28会议不附SEP，12/8–9附SEP。10月决定尚未来临。|
|S04|[国家统计局9月PPI](https://www.stats.gov.cn/sj/zxfbhjd/202610/t20261014_1965476.html)|10/14 09:30；2026年9月|正文和表已读：出厂同比5.0%、购进6.9%，两者环比均1.2%；生产资料同比6.5%、生活资料-0.1%。作者计算购进减出厂=1.9个百分点。|
|S05|[国家统计局9月价格解读](https://www.stats.gov.cn/xxgk/jd/sjjd2020/202610/t20261014_1965475.html)|10/14；2026年9月|正文已读：CPI同比0.9%、核心1.0%，服务环比-0.2%；不以价格总涨幅证明消费数量恢复。单独CPI原表页面读取失败，不声称已读原表。|
|S06|[国家统计局9月PMI](https://www.stats.gov.cn/zwfwck/sjfb/202609/t20260930_1965449.html)|9/30；2026年9月|正文/分类表已读：制造业50.1、生产51.7、新订单50.5（环比-0.1），中/小企业49.7/48.9；属于上期已有数据，本周无新PMI。|
|S07|[人民银行前三季度报告](https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2026101415422529740/index.html)；[同花顺转载](https://news.10jqka.com.cn/20261014/c680691268.shtml)|10/14；2026年前三季度/9月末|央行页面只读到标题，正文未返回；转载全文已读，属二级证据：前三季人民币贷款增11.52万亿元、M2同比7.2%、M1同比3.2%。不将累计贷款当9月单月新增贷款，也不声称央行正文已验证。|
|S08|[上海证券报10/16收盘](https://finance.sina.com.cn/roll/2026-10-16/doc-inivmiip8338895.shtml)；[智通收评](https://cn.investing.com/news/stock-market-news/article-3611960)|10/16 16:32、15:53；10/16|两篇正文已读：沪深成交约15554亿元，智通精值15554.14亿；科创50收1358.65，与API1358.647四舍五入一致。只用于行情，不采用智通其它新闻作为已核原始政策。|
|S09|[香港电台收盘](https://gbcode.rthk.hk/TuniS/news.rthk.hk/rthk/ch/component/k2/1874205-20261016.htm?spTabChangeable=0)|10/16 HKT16:36；10/12–16|正文已读：恒指24186、科技4108、主板成交1782亿港元；周变动分别-0.1%/-2.1%。这些是二级行情；南向完整序列未知。|
|S10|[上交所发布转载](https://finance.sina.com.cn/wm/2026-10-16/doc-inivmiin1689005.shtml)|10/16 18:06；10/8–16|转载全文已读，原微信公众号链接读取失败。科创50约1359，89.2倍PE，按上年年报利润且剔亏；指数区间-11.20%是10/8–16口径，不能称10/12–16周跌幅；不当TTM或历史分位。|
|S11|[上证报两融稿转载](https://stock.10jqka.com.cn/20261016/c680762013.shtml)|10/16 09:47；10/15|正文已读：完整A股两融25031.92亿、日减319.00亿，与API沪深北汇总/日差一致；电子融资净卖出113.53亿是融资分项，不能与完整两融混名。|
|S12|[IEA 10月油市报告公开部分](https://www.iea.org/reports/oil-market-report-october-2026)|10/14；9月观察与2026–27预测|公开Highlights、Fragile rebound已读，未购付费PDF：9月供给回升但袭击风险仍在；预测全年需求同比减少260万桶/日；公开叙述期货约107美元、现货Dated约134美元，非带合约与逐日结算的阈值序列。|
|S13|[台积电Q3正式业绩](https://pr.tsmc.com/english/news/3346)|10/15；季度截至9/30|新闻稿正文已读：美元收入467.2亿美元、同比41.2%，毛利率66.4%。这是海外公司自身正式实绩，非A/H公司收入、利润率或订单证明。|
|S14|[新华社全国卫生与健康大会原稿](https://www.xinhuanet.com/20261013/a5fc2cef862c434dbcd5811046d7d642/c.html)|10/13 14:02；会议10/12–13|正文已读：基层医疗、医保支付、药耗集采与科技成果转化方向；所读稿未给本期特定上市公司预算、采购、份额或收入。|
|S15|[GovInfo S.5548档案](https://www.govinfo.gov/app/details/BILLS-119s5548is)；[引入版正文](https://www.govinfo.gov/content/pkg/BILLS-119s5548is/html/BILLS-119s5548is.htm)|档案最后列示行动9/24；访问10/18|档案与正文已打开；仍为IS引入版、转委员会。单一IS档案不证明截至10/18所有立法动作均无变化，最新全行动链未完整获取；不宣称现行禁令或绝对无进展。|
|S16|[恒瑞许可公告](https://www.hengrui.com/media/detail-1041.html)|9/29；预计2026Q4交割|正文已读：3亿美元合同首付，监管/惯例条件，预计Q4交割；本期实际交割、收款、入账均unknown。|
|S17|[AZ完成投资公告](https://www.astrazeneca.com/media-centre/press-releases/2026/astrazeneca-completes-equity-investment-in-summit-therapeutics.html)|10/5|正文已读：20亿美元股权投资交割对象为Summit；本款不能算康方现金收入。后续康方里程碑与报表另核。|
|S18|Tushare `trade_cal/index_daily/margin`，本期真实API调用|10/18约08:50获取；交易/数据日10/8–16|三个接口成功。10/16 margin只SSE一行，SZSE/BSE未返；10/13–15三所齐。科创50与媒体交叉，日历为提供商SSE日历；未取得交易所直接完整指数/日历下载。原始字节及参数冻结，密钥未保存。|

## 保留缺口

9月社零原文与9月单月人民币贷款同口径同比、10/16沪深北完整两融、沪深成交三日完整序列、直接交易所指数原件、ETF同样本涨日净流向、南向连续额、A/H估值历史分位/股息利差/拥挤度、布伦特同一主力结算连续序列、黄金/美元同口径连续收盘、公司三季报/回款与真实账户均缺。相关字段保持unknown/null，不把本期查询成功扩写成全数据/全账户验证。
