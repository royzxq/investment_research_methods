# -*- coding: utf-8 -*-
"""
v2.27 框架数据脚本 — Tushare Pro 版 (v1.16)
====================================================================
只负责取数、研究候选和情景预检，不输出完整交易许可。
  §0/§0b: 合约期限、事件日历核对；缺数据不能视为过门。
  §1: S=近腿-远腿，同品种1:1。同期分位≥70/≥85仅为研究候选强度，
      不推导方向、SL、TP或可开手数；10/30/50分位仅参考。
      真实A计划须用 futures_risk.py validate-a 离线验证，再完成全量规则。
  §2: 单合约ATR、趋势与位置。2ATR金额及预算先折减后一次取整的数量
      仅是该止损情景的预检上界，不是最终手数，不独立裁决#31。
      实际策略止损、实际费用、账户已占用/挂单风险、保证金和限仓须另核。
  §2c: 只核已登记方向性持仓；POSITIONS为空不证明账户空仓。
  §2d: D8周涨分位(主力同合约两端结算，近3年周样本)，只是输入。
  §5: 影子账本——执行诊断里事前登记的影子计划按保守日线规则结算，只供规则复评。

v1.16（2026-09-19，对应框架 v2.27 周度状态换版）——配置层随动 + §2b 一列新增，无算法改动：
  ★ §0b EVENTS 日历滚动：归档 9/14 萨拉拉会(推迟无新日期)、9/14 CPI/WASDE 国内响应日、9/15 统计局硬数据、9/17 FOMC(加息 25bp)、
    9/14-9/18 霍尔木兹/俄乌占位窗、调减硬截止条目；新增 9/21、9/29 郑商所国庆前分级提保扩板节点(交易所公告日程, 不自动打 D12,
    仅提示 ±1 日门槛+0.3)、10/1-10/8 国庆长假占位(9/30=T-1 处置日; 不自动打标)、10/27-10/28 FOMC(自动打标 T-3/±1; 官方时间与
    国内 T-n 待下月核)；9/30 俄禁令条目加注 Vedomosti 延期报道级与长假 T-1；10/4 OPEC+ 加注闭市期/10/9 首个响应日。
    FIXED_RISK_WINDOWS 两条 9 月窗已到期(脚本按 AS_OF 自动不再显示), 保留条目作历史口径, 不新增 10 月窗(待官方日历)。
  ★ §2b.1 新增「日结算涨跌%」「近5日结算涨跌%」「#30近3日≥5%」三列：用同一合约 settle/pre_settle 逐日计算(缺任一端或非正数=None),
    供框架 0.3#30(能源链单日结算涨跌≥5%→顺向新开否决 3 交易日)按判定腿(MA2701)人工核验；脚本只算数值, 不判定命中/冷却、不授许可。
    背景：9/19 快照只有周涨列, 2026-09-19 执行诊断把 MA2701 #30 记为 unknown(raw_data)。
  ★ 滚动监测注释 ①/③/⑥/⑦/⑧ 按框架 v2.27 改写(①改判中断证真的反向监测; 第五轮 9/10 已落地纠错; 交易所收紧)。
  ★ 诚实声明: 本版**未经线上实测**(本环境无 tushare/pandas/numpy 与网络); 已做 python3 -m py_compile、配置区离线 ast 检查
    (EVENTS/FIXED_RISK_WINDOWS 元组形状)与仓库单元测试(134 项通过; 10 项脚本集成测试因本环境缺 numpy/pandas 未运行, 与改动前基线相同)。
    新增三列的纯计算路径以合成 records 离线自测(见适配报告第 8 节); 真实环境运行后须核 settle/pre_settle 字段与 MA2701 逐日读数。

v1.15（2026-09-17，对应框架 v2.26）：
  ★ 换月按框架0)阶梯执行：MA2610 9/16 实测剩余 19td(<20，#1 线)→结构对 MA2610-MA2701 整对下滚为 MA2701-MA2705
    (MA2705 9/16 实测 20 日均 18,667 过#2)；MA2701 兼方向性执行腿与#30护栏判定腿，§2 不再取 MA2610；
    MA 准备对顺延为 MA2705-MA2709(仅取样，不授许可)。SC 信号腿 SC2610 实测 9td 且 fut_mapping 主力已为 SC2611
    →SC近端对下滚为 SC2611-SC2612，原油周涨护栏口径腿随之改为 SC2611。RB/M/SR/CF/AU 未到换月条件。
  ★ 框架 v2.26 把 Kpler 通行量/海湾出口/战争险与 247 家铁水/盈利率降为参考：§0b 霍尔木兹占位窗与滚动监测注释同步改写，
    脚本算法不变。

v1.14（2026-09-16 方法修复，框架版本号不变）：
  ★ §2d 实现 D8：fut_mapping 取锚日主力，同一合约两端结算价算周涨(终点前7自然日及以前最近交易日)，
    近3年每自然周最后交易日为历史样本，有效样本<80%为unknown；口径经用户2026-09-16确认，写入canonical 3.4。
  ★ §5 影子账本：扫描 research/*-execution-audit.md 的 shadow_plans，结算规则见 price_evidence.settle_shadow_plan；
    已了结影子按登记时已核阻断归集盈亏，供 AUDIT 规则复评。
  ★ 脚本自行把完整输出(含 stderr)写入 research/<AS_OF>-data-snapshot.txt(末行“快照完成”为完整标记)，提交后流水线据此读取实测值。

v1.13 对应框架v2.25（2026-09-12 周度状态换版, light; 合并 v2.24/v1.12 后重适配）——仅配置层随动，无算法改动：
  ★ §1 SPREAD_PAIRS: RB 当前对按框架 0) 阶梯表 9/10 触发点到期切换 RB2610-RB2701 → RB2701-RB2703
    (RB2610 9/11 推算剩余 18td<20, 旧对退出; 新对分位/样本未计算, 首次运行按 3.1 验收、不继承旧分位);
    PREPARATION_PAIRS 的 RB 项改为下一对 RB2703-RB2705 取样(RB2705 9/4 实测 7,717 未过#2, 仅取样不授许可);
    MA 当前对维持 MA2610-MA2701 至框架写死的 2026-09-16 执行日, 届时与 MA2701-MA2705 准备对互换(用户维护项);
  ★ §0b EVENTS: 归档 9/6 OPEC+、9/11 PPI 国内响应日; 新增 9/14 萨拉拉伊朗-海合会外长会(反向质变候选, 占位不自动打标)、
    10/4 OPEC+; 8 月硬数据窗按统计局日程改为 9/15 已核(自动打标); 霍尔木兹/俄乌占位窗顺延至 9/14-9/18 并按本周实况改写备注
    (Kpler 10 日均 10 艘/日临界、9/8-9/9 质变日冻结已执行、上周 SC 结算周涨 +15.33% 命中>8%、本周 #30 甲醇 9/8 涨停冷却 9/9-9/11);
    调减硬截止条目改为"9/12 已到期无数据→9/14 记录无法核验"; 滚动监测注释 ③/⑦/⑨ 同步;
  ★ 诚实声明: 本版**未经线上实测**(本环境无 tushare/pandas 与网络); 已做 python3 -m py_compile、配置区离线 exec
    (research_pairs() 去重与 EVENTS 元组形状检查)与仓库单元测试; 真实环境运行后须按输出逐字段核验 RB 新对样本与 §0 剩余 td。

v1.12 对应框架v2.24：B季节日历/计划价格由独立离线入口seasonal_plan.py验算；
本主脚本不自动组装B历史输入，未取数须记录具体calculation/acquisition缺口。
新增helper经合成数据测试；本版未重新联网核验API或真实历史样本。

v1.11 对应框架v2.23：价格证据与OHLC指标独立输出；增加MA/RB换月准备，
事件国内交易日与既有提前风险窗分列。公开价格证据保留原始口径和比较日期；SC原油护栏
仅使用两端有效结算价，同对价差提供1/5/10交易日变化，缺样本为null。
方向/止损/目标闭合校验与统一账户风险预算由
scripts/futures_risk.py提供纯离线函数及JSON CLI。常规单笔/全账户风险上限
均为净值3.5%；低敞口按Step5固定金额封顶，且不高于常规组合预算，不再减半。
取数脚本不假定账户风险为零。
此次修改只完成离线验证，未以v1.13联网重跑；已有output与1.txt是历史快照。
离线范围覆盖A计划校验、预算/容量计算与模拟数据输出；线上API字段与权限
仍沿用已配置Tushare Pro，本版未重新确认网络可用性或数据权限。

维护：合约近腿触#1或主力换月先到则滚动；执行目标两腿须同时核#2。
历史分位按合约年份平移与±20日窗口计算，换月前后不得当作同一信号；
固定3年逐年须有至少33/41个有效唯一样本；33–40只警示，低于33/缺年/日期异常为必要缺项。
不填补样本、不临时改年数或窗口；该治理门槛不是统计有效性保证。分位极值不是回归收益证明。
指标250日窗口不足时标记实际样本数。SC信号席不建仓，随主力滚月。
保证金、限仓、事件事实与账户快照仍为人工确认输入。
历代实现与停用品种见git历史；新增取数仅为既定MA/RB下一合约对，不扩展策略白名单。
"""

import os
import re
import sys
import time
import argparse
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

try:
    from .futures_risk import precheck_2atr
    from .price_evidence import select_price, weekly_price_evidence, spread_change_series, completed_day_cutoff
    from .price_evidence import sample_coverage, validate_unique_trade_dates, calendar_window
    from .price_evidence import weekly_anchor_days, d8_weekly_rank, settle_shadow_plan, parse_shadow_plan
    from .validate_futures_audit import load_audit
except ImportError:  # direct script invocation
    from futures_risk import precheck_2atr
    from price_evidence import select_price, weekly_price_evidence, spread_change_series, completed_day_cutoff
    from price_evidence import sample_coverage, validate_unique_trade_dates, calendar_window
    from price_evidence import weekly_anchor_days, d8_weekly_rank, settle_shadow_plan, parse_shadow_plan
    from validate_futures_audit import load_audit

try:
    import tushare as ts
except ImportError:
    sys.exit("缺少依赖: 请先执行  pip install tushare pandas numpy")

# ============================ 配置区 ============================
# 环境变量优先; 也可直接在此粘贴:  TOKEN = "你的tushare_token"
TOKEN = os.getenv("TUSHARE_TOKEN", "")
# 复盘基准日 (框架 AS_OF_DATE): 默认=运行当天, 可用 --as-of YYYYMMDD 覆盖
AS_OF = datetime.now().strftime("%Y%m%d")
YEARS = 3               # 价差同期分位回看年数
WIN = 20                # 同期对齐窗口: 历史各年同日历日 ±20 个交易日
OUTDIR = "./output"

# ---- §0b 事件日历 (v2.9 0.0b / 1.4 事件轴; ★用户维护, 脚本只打印) ----
# 条目: (起始YYYYMMDD, 结束YYYYMMDD, 标签, 受影响品种tuple 或 "ALL", 处置备注[, 自动打标])
#   第6项「自动打标」省略=True: 按 T-3/±1 规则自动打 D12 事件判据与新开限制提示。
#   置 False 用于**不可排期项的逐周顺延占位窗**(地缘轴): 只在清单里列出来提醒人工盯,
#   不自动打标 —— 真正的触发日是质变 headline 当日, 不是占位窗里的每一天;
#   否则 D12 会对能源链/贵金属长期常开, 与 3.5b「临近离散事件T-3」的定义脱钩。
# 日期列使用国内影响交易日，官方发布时间/来源留在备注；会议起始日不代决议日。
# 2026-09-09复核：BLS 9/10 PPI、9/11 CPI；USDA 9/11 WASDE；Fed 9/16决议。
# ★v1.13 2026-09-12 按框架 v2.25 1.4 刷新：9/6 OPEC+、9/11 PPI 归档；新增 9/14 萨拉拉会(占位)、10/4 OPEC+；9/15 统计局已核。
# 其余暂估/治理截止/地缘占位仅用于人工核验，不作为已核离散事件自动打标。
EVENTS = [   # ★v1.16 2026-09-19 按框架 v2.27 1.4 事件轴刷新(用户维护项); ★v1.13 2026-09-12 条目已归档/改写
    #  归档移除(已落地, 见框架1.4【归档】段): 9/14 萨拉拉伊朗-海合会外长会(9/13 推迟, 无新日期)、9/14 CPI/WASDE 国内响应日、
    #  9/15 统计局8月硬数据(工业+5.2%/社零+0.4%/固投-7.2%/地产-19.9%)、9/17 FOMC(加息25bp至3.75-4.00%, 12-0, 点阵16/18)、
    #  9/14-9/18 霍尔木兹/俄乌占位窗(①已于 9/19 按 v2.26 新要件改判"中断证真", 反向监测转滚动注释①)、调减硬截止条目(#23 无法核验维持)。
    #  受影响品种元组沿框架1.4"暴露品种"原文; 其中池外品种(AG/CU/AL/IM/IC/J/SI/PS/LH/CF/SR)无指标腿,
    #  T-3/±1 打标对其无效(属预期, 见框架 v2.20 0)"池外休眠")。
    ("20260921", "20260921", "郑商所国庆前分级提保扩板第一节点(9/21结算起: MA2610涨跌停9%, MA2611保证金9%/涨跌停8%; 交易所公告日程, 非发布型事件)",
     ("MA",),
     "★v1.16 框架0.1交易所风控=收紧: 公告±1日(9/18-9/22)受影响品种新开门槛+0.3、公告日检视保证金占用(全账户>60%/单品种>20%主动降仓)、"
     "×0.8缓冲叠乘(2.3); 结构双腿按实际保证金口径计占用; 郑商所9/17公告(多源转引, 原文未核; 另有9/21起PTA/甲醇/PX单独通知未核); "
     "不自动打D12/T-3(非发布型事件), 人工按0.1核验",
     False),
    ("20260929", "20260929", "郑商所国庆前分级提保扩板第二节点(9/29结算起: 甲醇全部合约保证金10%/涨跌停9%; 10/8恢复交易后按条件回落)",
     ("MA",),
     "★v1.16 公告±1日(9/28-9/30)新开门槛+0.3、×0.8缓冲对甲醇全合约适用、公告日核占用; 跨长假存量按扩板后口径核压力场景(1.2 化工链1.2从严); "
     "不自动打D12/T-3, 人工按0.1核验",
     False),
    ("20260930", "20260930", "俄柴油/船用燃料出口禁令到期日(框架1.4俄乌轴行; 已定日期) + 国庆长假T-1处置日",
     ("MA", "SC"),
     "到期前后=俄乌轴预设质变节点: 再延期或扩至汽油→供给冲击升级 / 到期解除→侵蚀逻辑回吐评估; "
     "任一方向均为双向跳空预案日, 能源链方向性单边新开冻结(0.1); 实际公告日若提前, 按公告日改本条; "
     "★v1.16 Vedomosti 9/16报道生产商柴油出口限制拟延至10月底(匿名消息, 政府未官宣)=报道级候选, 官宣日才按质变日执行; "
     "同日=10/1-10/8国庆长假T-1: 全品种方向性单边对冲或减至×0.5(6.1/6.9), #22跨假期敞口>30%风险预算减仓, 低敞口条款10/9复评"),
    ("20261001", "20261008", "国庆长假(交易所闭市; 10/4 OPEC+ 与地缘headline均在闭市期发生; 占位不自动打标)",
     "ALL",
     "★v1.16 占位提醒: 跨长假纪律见9/30条目; 10/9为首个响应日, 按策略D'落地次日确认'纪律与双向跳空预案, 不抢跑; "
     "假期内布油/外盘走势、OPEC+决议、护航/再袭船/沙特管道headline于10/9集中定价",
     False),
    ("20261004", "20261004", "OPEC+会议(9/6按兵已归档; 下一节点; ★v1.16 在国内闭市期, 国内首个响应日=10/9)",
     ("MA", "SC", "AU"),
     "★v1.13 9/6七国维持10月产量水平不变='按兵→同向延续'分支兑现; 10/4: 按兵→延续 / 增产或闲置产能释放表态→回吐触发、MA存量10/9检视; "
     "节点±1按事件窗口纪律(闭市期→10/9按落地次日确认)"),
    ("20261027", "20261028", "美联储10月FOMC(10/27-28; ★v1.16 官方发布时间与国内T-n待下月按0.0b核; 暂按会议日期占位并自动打T-3/±1提示)",
     "ALL",
     "★v1.16 9/17加息25bp后点阵16/18年内再加、10月再加息概率49%(记者会后)→57%(9/18); 三剧本: 再加息→D13压制延续/美元10Y新高评估; "
     "按兵或转鸽→D13复归档议题重启评估前置(需美元连涨中断周度确认); #29 AU/AG按T-10核重入(AU信号席不建仓); "
     "决议映射到国内交易日(美东10/28 14:00=北京10/29 02:00→国内T大概率=10/29)待官方日历核实后改写本条日期"),
]
# 滚动/不可排期监测(无精确日期可登记, 人工跟踪; ★v1.8 按框架 v2.20(1.4/6.8 沿 v2.19)刷新):
#   ①政策资金结构修复裁决第二读数(②''形式过门·结构核对未过: 投放后一至两周流入结构是否向成长腿修复
#     +成交守2万亿+指数企稳; IM/IC已退出执行池, 本项仅作商品侧背景/跨资产输入);
#   ②反内卷双轨(轨一=第三份行业文件→跨行业外推裁决点; 轨二=光伏自律执行证据, 周度; ③门判据不变);
#   ③**黑色负反馈检验·临界裁决**(池内RB的背景输入; JM/J池外): ★v1.16 纠错——第五轮9/8发起、9/10全面落地(100/110), ★v1.13"无记录"为检索遗漏;
#     同源记录钢厂亏损扩大、减产计划增多、第六轮观望→检验点=落地但临界(不执行延续/不执行启动); Mysteel同口径总库存本周缺数(兰格口径-29.13不同源);
#     下一裁决=钢厂减产落地/第六轮是否发起: 第六轮落地+同口径去化延续→延续;
#     受阻/钢厂减产或抵制/铁水回落/焦煤现货涨势中断→负反馈启动、原料存量多头止盈触发(不许"再看一周");
#     247家铁水与盈利率=参考信息(★v1.15 框架v2.26降级, 不作门或扣分依据);
#   ④焦煤复产风险信号(安监放松/山西复产超预期/西曲矿复产→D14预案);
#   ⑤LC重启条件(池外·周度扫描; 证伪结案, 计数归零; 复活条件见框架0)扫描行);
#   ⑥①"中断证真"反向监测(★v1.16 2026-09-19改判; 回改只认官方停火/重开或伊朗许可-收费机制正式落地+§1 SC近端back回落(基准9/18 +43.5/分位100);
#     护航常态化(CENTCOM 40艘/1,800万桶 vs Vortexa 4/Kpler 12 conflicting)、沙特东西管道半恢复、萨拉拉新日期、IRGC 9/17再袭船多源确认均为参考级监测;
#     油轮通行量★v1.15 框架v2.26降为参考: 只作背景, 不再作①要件或质变日触发);
#   ⑦MA护栏口径(★v1.8; ★v1.15 随换月改腿): 原油周涨幅=§2b SC2611「SC护栏结算周涨%」列(最新已完成行情日对减7自然日), >5%→加仓权0.5/存量减50%,
#     >8%→多头冻结·清仓; #30=MA2701单日±5%; 9/4历史SC读数+15.33%命中>8%(账户持仓另核; ★v1.13 已写回框架1.5卡);
#     ★v1.13 本周: 甲醇9/8涨停+6.03%→#30顺向新开否决9/9-9/11(9/14到期≠新开窗口); SC 9/10 +6.44%/9/11早盘+8%(信号腿记录);
#     9/4→9/11 SC结算周涨%本地未取得=unknown(缺结算不解除上周处置), 真实环境运行§2b后核;
#     ★v1.16 9/19快照: SC2611结算周涨9/11→9/18 -0.30%未命中(上一读数+22.56%处置到期不续延); SC信号腿9/14 +11%/9/17 -6%/9/18 -9%(收盘口径);
#     MA2701判定腿逐日结算涨跌此前无输出列→2026-09-19诊断记#30 unknown; 本版§2b.1新增「日结算涨跌%」「近5日结算涨跌%」「#30近3日≥5%」列, 脚本只算数值不判冷却;
#   ⑧交易所风控措施公告(★v1.16 框架0.1=收紧: 郑商所9/17国庆分级提保扩板见EVENTS 9/21、9/29条目; PTA/甲醇/PX单独通知与INE公告原文待核; 10/8后按条件回落);
#   ⑨**换月触发点**(非市场事件, 不进本表以免误打D12/±1标记; §0 会按真实交易日预警,
#     完整阶梯见框架 v2.25「合约滚动阶梯」表, ★v1.8 已收缩至池内): RB 2026-09-10 ★v1.13 已到期切换→RB2701-RB2703(当前对) /
#     ★v1.15 MA 2026-09-16 已执行(结构对→MA2701-MA2705, 下次=2026-12-17 或主力换月→MA2705-MA2709) / SC 9/16 已随主力换月→SC2611-SC2612 /
#     AU 信号腿≈11月中旬 / SR·CF 2026-12-17 / M 2026-12-18; 池外品种不再跟踪。
EVENT_T3_BUSDAYS = 3     # 「临近离散事件T-3」窗口(v2.9 3.5b D12第三判据)
EVENT_HORIZON_BD = 10    # §0b 前瞻清单范围(v2.9 0.0b: 未来10个交易日)

# 既有固定安排与真实事件T-n分别显示；只提供方向性单边的预检提示。
# ★v1.16 以下两条 9 月窗已于 9/17、9/18 到期(脚本按 AS_OF>end 自动不再显示), 保留作历史口径; 10 月 FOMC 提前安排待官方日历核实后再登记。
FIXED_RISK_WINDOWS = [
    ("20260911", "20260917", "ALL", "FOMC既有D12提前风险窗",
     "来源=框架3.5b/6.9及数据协议5.2；9/15预案检查保留；与实际T-3提示不重复折减，后续月份不自动续用", True),
    ("20260911", "20260918", ("AU", "AG"), "#29既有新开冻结窗",
     "来源=框架0.3#29；国内决议T+1=9/18复评，仅所列品种新开限制，不延长全池D12", False),
]

# ---- §2c 持仓登记 (v2.9 0.3#25 ATR重校准; ★方向性单边逐仓登记, 结构持仓豁免) ----
# 条目: (合约, 入场日YYYYMMDD, "多"/"空", 备注)
POSITIONS = [
    # ("AU2610", "20260720", "多", "示例: 建仓当日即登记"),
]   # 仅表示本脚本没有登记；账户是否空仓及挂单风险必须另行核实

# 价差对: (标签, 近腿, 远腿, kind) —— 历史对照自动按年份平移生成
#   kind: "A"=研究候选强度(≥70/≥85)，分位价差仅参考；计划另行校验 |
#         "信号"=信号席(不建仓; 不打触发标签、不受#2; 分位作①back方向/护栏口径输入)
#         ("结构监控"黑色价差分支随 JM 退出停用; 复活时从 git 取回)
#   候选A/候选代理/存档/H-roll/国债期货价差 五种已随 PS·LH·CU·IM/IC·TL/T 退出删除(git v1.7 可取回)
SPREAD_PAIRS = [   # v2.21维持4组研究序列，计划需独立校验
    ("MA",   "MA2701", "MA2705", "A"),
    #   ★v1.15 2026-09-16 触发线到期(MA2610 实测 19td<20)按框架0)阶梯整对下滚; MA2705 9/16 实测 20 日均 18,667 过#2;
    #   下次触发=MA2701 #1线 2026-12-17 或主力换月 → MA2705-MA2709(届时核#2);
    #   方向性单边执行腿=MA2701(§2 单独取指标), 不随本对滚动
    #   2026-09-06 用户裁决: JM退出执行池并停采；历史风险估算不作新计划裁决
    ("RB",   "RB2701", "RB2703", "A"),      # ★v1.13 2026-09-10 触发线到期(RB2610 9/11 推算剩余 18td<20), 按框架 v2.25 阶梯表
    #   整对下滚为当前对 RB2701-RB2703(RB2703 9/4 实测 22,106 过#2); 新对分位/样本未计算, 首次运行按 3.1 验收(3年各≥33/41),
    #   不继承旧对 RB2610-RB2701 的 9/7 分位 61.5; 旧对停采(git v1.11 可取回)
    ("SR",   "SR2701", "SR2705", "A"),      # ★2026-09-06 用户裁决: SR 回归常驻备选, A 远月月差加回;
    #   SR2705 9/4 实测 20 日均 30,222 过#2; 触发线 2026-12-17(或主力换月)→ SR2705-SR2709
    #   黑色 JM-RB 价差(原 J2701-RB2701→JM2701-RB2701)随 JM 退出停采, 复活前提=JM 回池
    # ---- 信号席 (框架 v2.20: 不建仓, 只作①back方向与护栏口径输入) ----
    ("SC近端", "SC2611", "SC2612", "信号"),   # ★v1.15 9/16 SC2610 剩 9td 且 fut_mapping 主力已为 SC2611 → 整对下滚
    #   SC维持信号席，用户许可未扩展；不由研究分位自动开放建仓路径。
    #   分位仍照算(①门要件之一=SC 近端 back 方向); 下次主力换到 SC2612 时→SC2612-SC2701(信号腿不受#1#2)
]

# 已有路线的下一对提前取样，不替换当前对、不自动换月或授予交易许可。
# 当前对配置完成换月后，重复合约对会自动去重。
PREPARATION_PAIRS = [
    ("MA换月准备", "MA2705", "MA2709", "A"),   # ★v1.15 MA 当前对已下滚为 MA2701-MA2705; 下一对仅取样, MA2709 #2 未核、不授许可
    ("RB换月准备", "RB2703", "RB2705", "A"),   # ★v1.13 RB 当前对已切换为 RB2701-RB2703, 准备对顺延为下一对; RB2705 9/4 实测 7,717 未过#2, 仅取样不授许可
]


def research_pairs():
    seen = set()
    for stage, pairs in (("current", SPREAD_PAIRS), ("roll_preparation", PREPARATION_PAIRS)):
        for label, near, far, kind in pairs:
            if (near, far) not in seen:
                seen.add((near, far))
                yield stage, label, near, far, kind

# 指标计算合约 (§2; ★v1.8 按框架 v2.20 执行池: 核心 2 + 备选 3 + 信号 2 = 8 腿; 2026-09-06 用户裁决后)
INDICATOR_CONTRACTS = [
    "MA2701",   # 方向性执行候选兼#30护栏判定腿与A近腿(★v1.15 9/16下滚)；真实策略止损及账户预算另核
    "RB2701",   # 黑色结构表达；不开方向性单边
    "M2701",    # 独立备选；12/18或主力换月→M2705
    "SR2701",   # 常驻备选；12/17或主力换月→SR2705
    "CF2701",   # 常驻备选；12/17或主力换月→CF2705并核#2
    "AU2612",   # 信号席：fed_state/D13价格锚；不建仓
    "SC2611",   # 信号席：MA原油周涨护栏口径腿及①输入；★v1.15 9/16 随主力换月自SC2610滚入
]

# ---- v1.9 2ATR情景预检配置；真实#31计划裁决由futures_risk及完整规则负责 ----
ACCOUNT_EQUITY = 150000  # 预检基准净值；不替代下单时核实的账户净值
RISK_BUDGET = ACCOUNT_EQUITY * 0.035  # 2ATR情景预检的基础预算，不推断账户剩余额度
# 品种 → (multiplier 每手乘数, tick_value 最小变动价值); 新品种入池前先与框架 Step5 合约参数表同步填列
CONTRACT_SPEC = {"MA": (10, 10), "RB": (10, 10), "M": (10, 10), "SR": (10, 10), "CF": (5, 25),
                 "AU": (1000, 20), "SC": (1000, 100)}
#   启动时 spec_check() 会用 fut_basic.per_unit 交叉核对 multiplier, 不一致直接退出(宁抛错不猜)
# 信号席单腿(框架 v2.20 0)注c: 不建仓, 不受 #1/#2; §0/§2b 只打提示不打否决)
SIGNAL_LEGS = {"AU2612", "SC2611"}
# ---- §2d D8 周涨分位(★v1.14, 口径见 canonical 3.4) / §5 影子账本 ----
# 属性决定 D8 档位: (扣分档前X%, 否决档前X%); 品种取自 INDICATOR_CONTRACTS, 复活品种先补属性
PRODUCT_ATTR = {"MA": "商品", "RB": "商品", "M": "商品", "SR": "商品", "CF": "商品", "SC": "商品", "AU": "金融"}
D8_TIERS = {"商品": {"long": (20, 10), "short": (20, 10)},
            "金融": {"long": (10, 5), "short": (30, 20)}}
RESEARCH_DIR = Path(__file__).resolve().parents[1] / "research"   # 影子计划登记在执行诊断 JSON 的 shadow_plans
# ===============================================================

EXCH = {"MA": "CZCE", "SR": "CZCE", "CF": "CZCE",
        "CU": "SHFE", "AL": "SHFE", "RB": "SHFE", "AU": "SHFE", "AG": "SHFE",
        "SI": "GFEX", "M": "DCE",
        "JM": "DCE", "J": "DCE",
        "IM": "CFFEX", "IC": "CFFEX",
        "TL": "CFFEX", "T": "CFFEX",
        "SC": "INE",                          # ★v1.5 新增: INE原油(候选块)
        "PS": "GFEX",                         # ★v1.5 新增: 多晶硅(候选块)
        "LH": "DCE",                          # ★v1.5 新增: 生猪(候选块)
        "LC": "GFEX",                         # ★v1.6 新增: 碳酸锂(候选块, v2.11)
        "IF": "CFFEX", "IH": "CFFEX"}         # 备用
TS_SUFFIX = {"CZCE": "ZCE", "SHFE": "SHF", "DCE": "DCE", "INE": "INE", "GFEX": "GFE", "CFFEX": "CFX"}   # fut_mapping 连续代码后缀

pro = None
_basic_cache, _daily_cache, _mapping_cache, _settle_cache = {}, {}, {}, {}
_cal_cache = None      # ★v1.7 §0/§0b/§2b 的「交易日数」口径源(trade_cal)
CAL_DEGRADED = []      # ★v1.7 交易日口径降级为 busday 近似的原因(§0 与注3 会打印)
_T3_PRODS = set()   # §0b 计算出的「事件T-3」受影响品种集合(供§2 D12判据)
_EARLY_PRODS = set()  # 已有提前风险窗，不伪装为实际事件T-3


def api():
    global pro
    if pro is None:
        if not TOKEN or "填入" in TOKEN:
            sys.exit("请先设置环境变量 TUSHARE_TOKEN, 或在配置区直接填入 TOKEN")
        pro = ts.pro_api(TOKEN)
    return pro


def basic(exch):
    """交易所合约基础表(含已退市), 用于代码解析与到期日。按交易所缓存。"""
    if exch not in _basic_cache:
        df = api().fut_basic(exchange=exch, fut_type="1",
                             fields="ts_code,symbol,name,list_date,delist_date,per_unit")
        if df is None or df.empty:
            raise RuntimeError(f"fut_basic({exch}) 返回为空 —— 多为积分不足")
        _basic_cache[exch] = df
        time.sleep(0.4)
    return _basic_cache[exch]


def _match_rows(sym):
    """在 fut_basic 内定位合约: 主键=ts_code 去后缀后与 sym 全等。

    品种前缀用 ^品种+数字 精确匹配, 而非 startswith:
    DCE 上 J/JM/JD、L/LH/LG、M, CFFEX 上 T/TL/TS/TF、IM/IC/IF/IH 等共享首字母,
    startswith 会误匹配; 要求品种码后紧跟数字即可区分(T2609 ≠ TL2609/TS2609,
    LH2609 ≠ L2609/LG2609)。

    ★v1.7 修正(换月时暴露): 原主键是「delist_date 年月 == 合约交割年月」, 该假设
    对 INE 原油 SC 系统性错位一个月 —— SC 的最后交易日落在**交割月的前一个月**
    (SC2610 → 20260930), 于是 resolve("SC2609") 实际取到 SC2610、resolve("SC2610")
    取到 SC2611。2026-08-30 用 fut_basic 全表核验: 20 个配置品种里只有 SC 错位,
    且其 27 个在挂合约全部错位, 其余 19 个品种零错位。错位在旧版被年份平移腿同步
    抵消(SC2509 也一并平移成 SC2510), 因此**分位数值自洽、但合约标签/§0 距到期/
    §2 单合约指标全部张冠李戴** —— §0 也因此从未对真正的 SC2609(8/31 到期)报警。
    现改为 ts_code 全等: tushare 各交易所均返回 4 位年月码(已核郑商所亦是
    MA2601.ZCE 而非 MA601.ZCE), 不存在原注释担心的十年循环歧义。
    ★不保留「交割年月匹配」作退化兜底: 该分支会在合约**根本不存在**时命中邻月并
    静默返回错误合约 —— 实测 INE 按「近12个月逐月 + 更远按季」挂牌, SC2710/SC2711
    并不存在, 而 resolve("SC2711") 走退化分支会命中 SC2712(delist 20271130), 即原样
    复活本次要修掉的张冠李戴。宁可抛 ValueError 让配置者看见, 也不要猜。
    """
    prod = re.match(r"[A-Za-z]+", sym).group().upper()
    ym = re.search(r"\d+", sym).group()          # '2610'
    target = "20" + ym                            # '202610'
    b = basic(EXCH[prod])
    cands = b[b["ts_code"].astype(str).str.upper().str.match(rf"{prod}\d")]
    code = cands["ts_code"].astype(str).str.upper().str.split(".").str[0]
    hit = cands[code == sym.upper()]
    return prod, target, cands, hit


def resolve(sym):
    """'MA2609' → tushare ts_code。"""
    prod, target, cands, hit = _match_rows(sym)
    if len(hit) >= 1:
        return hit.iloc[0]["ts_code"]
    sample = ", ".join(cands["ts_code"].astype(str).head(20))
    raise ValueError(f"无法解析 {sym} (预期交割 {target}); 该品种样例: {sample}")


def delist_date(sym):
    """返回合约最后交易日 'YYYYMMDD'。"""
    prod, target, cands, hit = _match_rows(sym)
    if len(hit) >= 1:
        return str(hit.iloc[0]["delist_date"])
    raise ValueError(f"无法取得 {sym} 的 delist_date (预期交割 {target})")


def _trade_cal():
    """交易日历(SSE, 回溯 YEARS+1 年、前瞻 2 年); 取数失败→返回空列表, 调用方退回 busday。

    ★注意 tushare 只发布到**次年年底**: 请求 end_date=20280830 实测只返回到 20271231,
    且是静默截断(不报错)。因此调用方必须自己做覆盖检查, 不能假设日历一定盖到目标日
    —— 见 _busdays 的 _cal_covers 守卫。
    """
    global _cal_cache
    if _cal_cache is None:
        try:
            df = api().trade_cal(exchange="SSE",
                                 start_date=shift_year_date(AS_OF, YEARS + 1),
                                 end_date=shift_year_date(AS_OF, -2),   # 闰日按 shift_year_date 处理
                                 fields="cal_date,is_open")
            time.sleep(0.4)
            _cal_cache = sorted(df[df["is_open"] == 1]["cal_date"].astype(str))
        except Exception as e:
            _cal_cache = []
            _cal_degrade(f"trade_cal 取数失败({type(e).__name__})")
    return _cal_cache


def _cal_degrade(reason):
    """记录一次"交易日口径降级为 busday 近似"; §0 与注3 会把它打印出来。"""
    global CAL_DEGRADED
    if reason not in CAL_DEGRADED:
        CAL_DEGRADED.append(reason)


def _cal_covers(cal, lo, hi):
    """日历是否完整覆盖 [lo, hi]; 不覆盖→调用方必须退回 busday, 否则会静默少算天数。"""
    return bool(cal) and cal[0] <= lo and hi <= cal[-1]


def _busdays(from_yyyymmdd, to_yyyymmdd):
    """两日期间交易日数(左闭右开, 与 np.busday_count 同口径); to 在 from 之前则为负。

    ★v1.7: 主口径由「工作日近似」改为 trade_cal **真实交易日**(已剔节假日)。
    近似口径在长假前后系统性高估剩余天数 —— 2026 国庆当口实测: CU2610/AL2610/
    RB2610/AU2610/AG2610 的 busday 读数(33)比真实交易日(27)多 6 天, 会让否决#1
    (<20交易日)的 §0 预警整整晚一周触发, 而这一周恰好是这批合约的换月窗口。
    trade_cal 取数失败(权限/网络)→ 自动退回 busday 近似, 按原注2口径解读。
    """
    cal = _trade_cal()
    a, b = str(from_yyyymmdd), str(to_yyyymmdd)
    sign = 1 if a <= b else -1
    lo, hi = (a, b) if sign > 0 else (b, a)
    if _cal_covers(cal, lo, hi):
        return sign * len([d for d in cal if lo <= d < hi])
    if cal:                                       # 有日历但盖不到目标日(多为次年年底截断)
        _cal_degrade(f"交易日历未覆盖 {lo}~{hi}(日历止于 {cal[-1]})")
    x = np.datetime64(pd.to_datetime(a, format="%Y%m%d").date())
    y = np.datetime64(pd.to_datetime(b, format="%Y%m%d").date())
    return int(np.busday_count(x, y))


def daily(sym):
    """单合约全生命周期日线; 价格口径: 结算价, 缺失用收盘价(close 另保留供基差)。"""
    if sym not in _daily_cache:
        code = resolve(sym)
        df = api().fut_daily(
            ts_code=code,
            fields="trade_date,settle,close,open,high,low,pre_settle,vol,oi")
        time.sleep(0.4)
        if df is None or df.empty:
            raise RuntimeError(f"{sym}({code}) 日线为空")
        cutoff = min(AS_OF, completed_day_cutoff())
        df = df[df["trade_date"].astype(str) <= cutoff].copy()
        if "is_complete" in df:
            df = df[df["is_complete"] != False].copy()
        if df.empty:
            raise RuntimeError(f"{sym} 在已完成日线上界 {cutoff} 前无可用数据")
        validate_unique_trade_dates(df["trade_date"].tolist())
        df = df.sort_values("trade_date").reset_index(drop=True)
        prices = [select_price(row.get("settle"), row.get("close"))
                  for row in df.to_dict("records")]
        df["px"] = [price for price, _ in prices]
        df["price_basis"] = [basis for _, basis in prices]
        _daily_cache[sym] = df
    return _daily_cache[sym]


def shift_year_sym(sym, k):
    """合约代码按年平移: MA2609, k=1 → MA2509。"""
    prod = re.match(r"[A-Za-z]+", sym).group()
    ym = re.search(r"\d+", sym).group()
    return f"{prod}{int(ym[:2]) - k:02d}{ym[2:]}"


def shift_year_date(d, k):
    """'20260609' 平移 k 年, 处理 2/29。"""
    y, md = int(d[:4]) - k, d[4:]
    if md == "0229":
        md = "0228"
    return f"{y}{md}"


def pair_series(near, far):
    """合并同一对两腿，保留原价/口径 → spread / spread_pct(以远腿为基)。"""
    a, b = daily(near), daily(far)
    validate_unique_trade_dates(a["trade_date"].tolist())
    validate_unique_trade_dates(b["trade_date"].tolist())
    columns = ["trade_date", "px", "price_basis", "settle", "pre_settle", "close", "open", "high", "low"]
    m = pd.merge(a.reindex(columns=columns), b.reindex(columns=columns),
                 on="trade_date", suffixes=("_n", "_f"))
    m["near_contract"], m["far_contract"] = near, far
    m["spread"] = m["px_n"] - m["px_f"]
    m["spread_pct"] = m["spread"] / m["px_f"] * 100
    return m


def window_around(df, anchor, win):
    """真实交易日历固定±win日期范围；缺行情不向窗口外补行。"""
    cal = _trade_cal()
    if CAL_DEGRADED:
        raise ValueError("同期样本交易日历已降级，不能验收固定窗口")
    window = calendar_window(cal, anchor, win)
    validate_unique_trade_dates(df["trade_date"].tolist())
    in_bounds = df["trade_date"].between(window["window_start"], window["window_end"])
    expected_date = df["trade_date"].isin(window["trading_dates"])
    if (in_bounds & ~expected_date).any():
        raise ValueError("同期窗口出现非交易日行情日期")
    selected = df.loc[expected_date].copy()
    selected.attrs["sample_window"] = {key: value for key, value in window.items() if key != "trading_dates"}
    return selected


# ---------------------- §0 合约新鲜度自检 ----------------------
def contract_freshness_check():
    """全部配置合约: 解析 + 距最后交易日检查(否决#1前置预警, trade_cal真实交易日)。"""
    syms, seen = [], set()
    for _stage, _label, n, f, _kind in research_pairs():
        syms += [n, f]
    syms += list(INDICATOR_CONTRACTS)
    for _sym, _d, _side, _n in POSITIONS:
        syms.append(_sym)
    warns = []
    for s in syms:
        if s in seen:
            continue
        seen.add(s)
        try:
            dl = delist_date(s)
            days = _busdays(AS_OF, dl)
            if days <= 0:
                warns.append(f"  ⚠ {s} 已到期(最后交易日 {dl}) —— 陈旧合约码, 需滚月")
            elif days < 20 and (s in SIGNAL_LEGS or _signal_pair_leg(s)):
                # ★v1.8 信号腿(框架 0)注c): 不建仓故不受#1, 只提示随主力换月滚
                warns.append(
                    f"  ℹ {s} 信号腿(不建仓, 不受否决#1): 距最后交易日 {days} 交易日 —— 随主力换月整对下滚"
                    + ("(⚠INE 按'近12个月逐月+更远按季'挂牌, 下一月未挂牌时 resolve 会抛错, "
                       "按阶梯表退到下一个实际挂牌月)" if s.upper().startswith("SC") else ""))
            elif days < 20:
                warns.append(
                    f"  ⚠ {s} 距最后交易日仅 {days} 交易日(<20, 触发否决#1) —— 建议滚月")
        except Exception as e:
            warns.append(f"  ⚠ {s} 解析失败: {e}")
    _busdays(AS_OF, AS_OF)          # 触发日历加载, 使降级状态在本节即可判定
    print(f"\n---- 0) 合约新鲜度自检 (否决#1 前置预警, "
          f"{'trade_cal真实交易日' if not CAL_DEGRADED else '⚠busday近似·口径已降级'}) ----")
    for r in CAL_DEGRADED:
        print(f"  ⚠ 交易日口径降级: {r} —— 本次全部「距到期/事件T-n」"
              f"改用工作日近似(未剔节假日), 长假前后会**高估**剩余天数(2026国庆当口实测高估6个交易日),"
              f"否决#1 预警会偏晚, 请按此从严解读")
    if warns:
        print("\n".join(warns))
    else:
        if CAL_DEGRADED:
            print("  #1数据未完成: 近似日历未提示临期，但不能认定真实交易日门已过")
        else:
            print(f"  #1数据检查: {len(seen)} 个配置合约距最后交易日均 ≥20 交易日；不代表完整交易许可")


def _prod(sym):
    return re.match(r"[A-Za-z]+", sym).group().upper()


def _signal_pair_leg(sym):
    """sym 是否属于 kind=\"信号\" 的价差对(两腿均按信号腿处理, 不受#1/#2)。"""
    return any(sym in (n, f) for _l, n, f, k in SPREAD_PAIRS if k == "信号")


def spec_check():
    """★v1.8 启动参数校验(宁抛错不猜): CONTRACT_SPEC 必须覆盖全部池内品种, 且 multiplier 与
    tushare fut_basic.per_unit 一致 —— 乘数写错会让一手风险(0.3#31)成倍失真且无任何报错。
    (fut_basic.multiplier 字段实测为 None, per_unit 才是每手乘数: MA 10/SR 10/CF 5/AU 1000/SC 1000。)"""
    legs = list(INDICATOR_CONTRACTS) + [s for _stage, _l, n, f, _k in research_pairs() for s in (n, f)]
    first = {}
    for sym in legs:
        first.setdefault(_prod(sym), sym)
    missing = sorted(set(first) - set(CONTRACT_SPEC))
    if missing:
        sys.exit(f"CONTRACT_SPEC 缺品种 {missing}: 一手风险(0.3#31)无法核算 —— "
                 f"先与框架 Step5 合约参数表同步填列后再跑")
    bad, unknown = [], []
    for prod, sym in sorted(first.items()):
        try:
            _p, _t, _c, hit = _match_rows(sym)
            pu = pd.to_numeric(hit.iloc[0]["per_unit"], errors="coerce") if len(hit) else np.nan
        except Exception as e:
            pu, unknown = np.nan, unknown + [f"{prod}({e})"]
            continue
        if pd.isna(pu):
            unknown.append(prod)
        elif float(pu) != float(CONTRACT_SPEC[prod][0]):
            bad.append(f"{prod}: CONTRACT_SPEC={CONTRACT_SPEC[prod][0]} vs fut_basic.per_unit={pu:g}")
    if bad:
        sys.exit("CONTRACT_SPEC multiplier 与交易所合约乘数不一致: " + "; ".join(bad)
                 + " —— 修正后再跑(否则 0.3#31 一手风险失真)")
    print(f"  v1.13 参数校验: CONTRACT_SPEC 覆盖 {len(first)} 个池内品种, multiplier 与 fut_basic.per_unit 一致"
          + (f"; ⚠ per_unit 缺失未能核对: {unknown}" if unknown else ""))


# ---------------- §0b 事件日历核对辅助 (v2.9 0.0b / 3.5b) ----------------
def _event_flags():
    """扫描 EVENTS → (前瞻清单, T-3受影响品种集合)。trade_cal真实交易日。

    定义(与 v2.9 对齐):
      进行中 = AS_OF 落在 [起始, 结束] 内;
      T-3内 = 尚未开始且距起始 ≤ EVENT_T3_BUSDAYS 个交易日(3.5b D12第三判据);
      ±1窗口 = 距起始或结束 ≤1 交易日(0.1 节点±1新开限制核对提示)。

    ★占位窗(条目第6项=False)只列清单、不打标: 地缘轴质变不可排期, 用占位窗代替真实
    事件日会让 in_t3/near_pm1 在整个窗口内恒真, D12 对能源链/贵金属长期常开 ——
    与 3.5b「临近离散事件T-3」的定义脱钩(PR#16 review P1)。
    """
    upcoming, t3_prods = [], set()
    for ev in EVENTS:
        st, ed, label, prods, note = ev[:5]
        auto = ev[5] if len(ev) > 5 else True
        ongoing = (st <= AS_OF <= ed)
        d_start = _busdays(AS_OF, st)
        d_end = _busdays(AS_OF, ed)
        in_t3 = auto and (ongoing or (AS_OF < st and d_start <= EVENT_T3_BUSDAYS))
        near_pm1 = auto and (ongoing or abs(d_start) <= 1 or abs(d_end) <= 1)
        if ongoing or near_pm1 or (AS_OF < st and d_start <= EVENT_HORIZON_BD):
            upcoming.append((st, ed, label, prods, note,
                             d_start, ongoing, in_t3, near_pm1, auto))
        if in_t3:
            t3_prods.update(prods if prods != "ALL" else ("ALL",))
    return upcoming, t3_prods


def print_event_calendar():
    print(f"\n---- 0b) 事件日历核对辅助 (v2.9 0.0b; 未来{EVENT_HORIZON_BD}个交易日; "
          f"节点由用户在配置区维护, 脚本只打印) ----")
    upcoming, t3_prods = _event_flags()
    if not upcoming:
        print("  窗口内无已配置节点 —— 请核对框架 1.4 事件轴是否有新增/暂估项待修正")
    for st, ed, label, prods, note, d_start, ongoing, in_t3, near_pm1, auto in upcoming:
        span = st if st == ed else f"{st}~{ed}"
        stat = ("人工核验项·不自动打标" if not auto else
                "进行中" if ongoing else f"T-{max(d_start, 0)}")
        pl = "全品种" if prods == "ALL" else "/".join(prods)
        marks = []
        if not auto:
            marks.append("占位/暂估/治理截止不自动打标，待真实事件及适用性核验")
        if in_t3:
            marks.append("T-3内→D12事件判据生效(§2)")
        if near_pm1:
            marks.append("±1窗口→新开限制核对(0.1)")
        print(f"  ⭐{span} {label} [{stat}]  品种: {pl}")
        print(f"     处置: {note}" +
              (f"   ⚠ {'; '.join(marks)}" if marks else ""))
    print("  → 0.0b四步覆盖范围: 本节=第1步(节点清单)与第3步(±1限制)的提示;")
    print("    第2步(横跨判定+T-1对冲预案入6.9)与第4步(4.3模板必填字段)仍需人工完成")
    return t3_prods


def print_fixed_risk_windows():
    affected = set()
    for start, end, prods, label, note, affects_d12 in FIXED_RISK_WINDOWS:
        if AS_OF <= end:
            active = start <= AS_OF <= end
            print(f"  固定安排 {start}~{end} {label} [{'生效中' if active else '待到期'}]：{note}")
            if active and affects_d12:
                affected.update(prods if prods != "ALL" else ("ALL",))
    return affected


# ---------------------- §1 价差同期分位 ----------------------
def _volume20(sym):
    """A full, finite, nonnegative 20-observation volume window is required."""
    data = daily(sym)
    window = data[data["trade_date"] <= AS_OF].tail(20)
    values = pd.to_numeric(window["vol"], errors="coerce")
    if window["trade_date"].nunique() != 20 or len(values) != 20 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("#2缺失: 不足20个完整有效成交量样本")
    return float(values.mean())


def spread_percentile(label, near, far, kind="A"):
    """Research-only S=near-far; no implied direction, stop or tradable size."""
    cur_df = pair_series(near, far)
    cur_df = cur_df[cur_df["trade_date"] <= AS_OF]
    if cur_df.empty:
        raise RuntimeError(f"数据缺失: {near}-{far} 在 {AS_OF} 前无重叠数据")
    cur = cur_df.iloc[-1]
    if not np.isfinite(cur[["px_n", "px_f", "spread", "spread_pct"]].astype(float)).all() or min(cur["px_n"], cur["px_f"]) <= 0:
        raise RuntimeError("数据缺失: 当前两腿价格无效，不计算分位")
    market_trade_date = str(cur["trade_date"])
    pool, used, missing, blocked, quality_warnings, year_counts = [], [], [], [], [], []
    historical_windows, basis_pairs = [], set()
    current_basis = (str(cur.get("price_basis_n", "unknown")), str(cur.get("price_basis_f", "unknown")))
    for k in range(1, YEARS + 1):
        n_k, f_k = shift_year_sym(near, k), shift_year_sym(far, k)
        try:
            hist_pair = pair_series(n_k, f_k)
            validate_unique_trade_dates(hist_pair["trade_date"].tolist())
            sub = window_around(hist_pair, shift_year_date(market_trade_date, k), WIN)
            window = sub.attrs["sample_window"]
            valid = np.isfinite(sub[["px_n", "px_f", "spread", "spread_pct"]]).all(axis=1)
            valid &= (sub["px_n"] > 0) & (sub["px_f"] > 0)
            sub = sub.loc[valid]
            for row in sub.to_dict("records"):
                basis_pairs.add((str(row.get("price_basis_n", "unknown")), str(row.get("price_basis_f", "unknown"))))
            if not sub.empty:
                pool.append(sub[["spread", "spread_pct"]])
            year_counts.append(len(sub))
            historical_windows.append(dict(near_contract=n_k, far_contract=f_k, count=len(sub), **window))
            used.append(f"{n_k}-{f_k}(n={len(sub)}/{2 * WIN + 1};"
                        f"目标锚={window['target_anchor']},交易日锚={window['trading_anchor']};"
                        f"窗口={window['window_start']}~{window['window_end']})")
        except Exception as exc:
            year_counts.append(None)
            historical_windows.append(dict(near_contract=n_k, far_contract=f_k, count=None,
                                           target_anchor=shift_year_date(market_trade_date, k), issue=str(exc)))
            used.append(f"{n_k}-{f_k}(n=unknown/{2 * WIN + 1};缺失或日期异常:{exc})")
    coverage = sample_coverage(year_counts, expected_per_year=2 * WIN + 1, expected_years=YEARS)
    missing.extend(f"同期样本:{issue}" for issue in coverage["missing_fields"])
    quality_warnings.extend(f"同期样本:{issue}" for issue in coverage["warnings"])
    known_basis = all(basis in ("settle", "close") for pair in basis_pairs | {current_basis} for basis in pair)
    basis_quality = ("unknown" if not known_basis or not basis_pairs else
                     "consistent" if basis_pairs == {current_basis} else "basis_mixed")
    if basis_quality != "consistent":
        missing.append(f"分位价格口径={basis_quality}:当前{current_basis},历史{sorted(basis_pairs)}；"
                       "分位仅供参考，不能确认#13/D4已过；须用完整同口径数据重跑，不填补/改写原价")
    hist = pd.concat(pool) if pool else pd.DataFrame(columns=["spread", "spread_pct"])
    pct_same = float((hist["spread_pct"] < cur["spread_pct"]).mean() * 100) if len(hist) else None
    life = cur_df.loc[np.isfinite(cur_df["spread_pct"]), "spread_pct"]
    pct_life = float((life < cur["spread_pct"]).mean() * 100)

    volumes, days = {}, {}
    for name, sym in (("近", near), ("远", far)):
        try:
            volumes[name] = _volume20(sym)
            if volumes[name] < 10000 and kind != "信号":
                blocked.append(f"#2:{name}腿20日均成交<1万")
        except Exception as exc:
            volumes[name] = None
            missing.append(f"#2:{name}腿成交量缺失({exc})")
        try:
            days[name] = _busdays(AS_OF, delist_date(sym))
            if CAL_DEGRADED:
                missing.append(f"#1:{name}腿交易日历已降级，需复核")
            if days[name] < 20 and kind != "信号":
                blocked.append(f"#1:{name}腿距最后交易日<20")
        except Exception as exc:
            days[name] = None
            missing.append(f"#1:{name}腿到期数据缺失({exc})")
    # The change series belongs only to this pair, never to the historical
    # percentile pool or an old pair before a roll. Missing sessions remain
    # unknown instead of compressing the observed rows into "trading days".
    cur_df = cur_df.copy()
    for field, value in (("near_contract", near), ("far_contract", far),
                         ("price_basis_n", "unknown"), ("price_basis_f", "unknown")):
        if field not in cur_df:
            cur_df[field] = value
    changes = spread_change_series(cur_df.to_dict("records"), near, far, _trade_cal())
    cur_df = cur_df.merge(pd.DataFrame(changes), on="trade_date", how="left")
    cur = cur_df.iloc[-1]
    os.makedirs(OUTDIR, exist_ok=True)
    safe = f"{near}_{far}".replace("/", "")
    cur_df.to_csv(f"{OUTDIR}/spread_{safe}.csv", index=False)
    print(f"\n[{label}] {near} - {far}  (数据截至 {cur['trade_date']})")
    print(f"  同期重算市场锚: {market_trade_date}（研究AS_OF={AS_OF}不改变同一行情日的历史窗口）")
    print(f"  当前价差: {cur['spread']:+.1f}  |  价差%: {cur['spread_pct']:+.3f}%")
    print(f"  当前两腿价格口径: {near}={cur['price_basis_n']} / {far}={cur['price_basis_f']}")
    for n in (1, 5, 10):
        key = f"spread_change_{n}td"
        value = cur[key]
        change_text = f"{value:+.2f}" if pd.notna(value) else "null"
        unit = "元/桶" if near.startswith("SC") else "元/吨"
        print(f"  同对价差近{n}交易日变化: {change_text} {unit} | "
              f"{cur[f'{key}_from']} → {cur['trade_date']} | {cur[f'{key}_status']}")
    print("  正负变化仅说明固定合约对走阔/收窄；分位高不代表本期反弹，非供需证真。")
    for name in ("近", "远"):
        volume_text = f"{volumes[name]:,.0f}" if volumes[name] is not None else "缺失"
        day_text = str(days[name]) if days[name] is not None else "缺失"
        print(f"  {name}腿20日均成交: {volume_text} | 距最后交易日: {day_text} td")
    if pct_same is None:
        tag = "数据缺失，不能评价研究候选强度"
        if kind == "A":
            tag += "；计划未完成，方向/真实SL/TP/R/预算及完整规则另核"
    elif kind == "信号":
        tag = "信号席仅供back极端度参考，不建仓"
    else:
        strength = "高强度研究候选(≥85)" if pct_same >= 85 else "研究候选(≥70)" if pct_same >= 70 else "未达研究候选阈值"
        tag = strength + "；计划未完成，方向/真实SL/TP/R/预算及完整规则另核"
    qtext = f"{pct_same:.1f}" if pct_same is not None else "缺失"
    print(f"  近{YEARS}年同期分位(±{WIN}交易日): {qtext} → {tag}")
    if len(hist):
        lv = np.percentile(hist["spread"], [10, 30, 50])
        lp = np.percentile(hist["spread_pct"], [10, 30, 50])
        print(f"  同期池价差水平(仅参考，不自动生成SL/TP): 10分位={lv[0]:+.1f} / 30分位={lv[1]:+.1f} / 50分位={lv[2]:+.1f}"
              f" (%口径: {lp[0]:+.3f}/{lp[1]:+.3f}/{lp[2]:+.3f})")
    print(f"  本对全生命周期分位: {pct_life:.1f} (参考，非收益预测)")
    print(f"  历史对照: {'; '.join(used)}")
    print(f"  同期样本验收: 每个固定历史年至少{coverage['minimum_per_year']}/{coverage['expected_per_year']}，"
          f"共{YEARS}年 | {coverage['status']}；仅为治理最低线，非统计有效性保证")
    for issue in quality_warnings:
        print(f"  ⚠ 质量警示: {issue}；警示与必要缺项分别记录，不填补样本")
    for issue in blocked:
        print(f"  ⚠ 明确否决: {issue}")
    for issue in missing:
        print(f"  ⚠ 数据缺失/不足: {issue}；不能视为已过门")
    return {"scope": "research_inputs", "percentile": pct_same,
            "data_status": "incomplete" if missing else "blocked" if blocked else "complete",
            "missing_fields": missing, "hard_vetoes": blocked,
            "quality_warnings": quality_warnings, "sample_coverage": coverage,
            "market_trade_date": market_trade_date, "historical_windows": historical_windows,
            "percentile_price_basis_quality": basis_quality,
            "price_basis": {near: cur["price_basis_n"], far: cur["price_basis_f"]},
            "spread_changes": changes[-1],
            "plan_status": "incomplete" if kind == "A" else "not_applicable",
            "final_lots": None}


# ---------------------- §2 单合约指标 (Wilder口径) ----------------------
def daily_settlement_changes(records, days=5, guard_days=3, guard_pct=5.0):
    """★v1.16 Per-session settle/pre_settle change for the latest ``days`` sessions (0.3#30 input).

    Returns (latest_pct, series_text, guard_text). A session is valid only when both settle and
    pre_settle are finite positives; otherwise it is reported as None. The script only computes the
    numbers: whether #30 is hit, which direction is frozen and when the cooling window ends are
    judged by the framework reader against the designated leg (MA2701 since 9/16).
    """
    rows = []
    for rec in list(records)[-days:]:
        try:
            settle = float(rec.get("settle")) if rec.get("settle") is not None else float("nan")
            pre = float(rec.get("pre_settle")) if rec.get("pre_settle") is not None else float("nan")
        except (TypeError, ValueError):
            settle, pre = float("nan"), float("nan")
        ok = settle == settle and pre == pre and settle > 0 and pre > 0
        pct = round((settle / pre - 1) * 100, 2) if ok else None
        rows.append((str(rec.get("trade_date")), pct))
    if not rows:
        return None, "", "unknown"
    latest = rows[-1][1]
    series = "|".join(f"{d}:{p if p is not None else 'null'}" for d, p in rows)
    recent = rows[-guard_days:]
    if any(p is None for _, p in recent):
        guard = "unknown(近%d日结算端点缺失)" % guard_days
    else:
        hits = [f"{d}({'+' if p > 0 else ''}{p}%)" for d, p in recent if abs(p) >= guard_pct]
        guard = ("≥5%命中:" + ",".join(hits)) if hits else "近%d日无≥5%%" % guard_days
    return latest, series, guard


def contract_price_evidence(sym):
    """Endpoint settlement evidence is independent of historical OHLC/ATR."""
    df = daily(sym)
    records = df.to_dict("records")
    week = weekly_price_evidence(records, AS_OF)
    is_oil = sym.startswith("SC")
    day_pct, day_series, day_guard = daily_settlement_changes(records)
    return {"合约": sym, "数据截至": week["market_trade_date"],
            "日结算涨跌%": day_pct, "近5日结算涨跌%": day_series, "#30近3日≥5%": day_guard,
            "px": week["end_price"], "price_basis": week["end_basis"],
            "周涨锚日": week["anchor_date"],
            "周涨起日": week["start_date"], "周涨止日": week["end_date"],
            "周涨起价": week["start_price"], "周涨止价": week["end_price"],
            "周涨起口径": week["start_basis"], "周涨止口径": week["end_basis"],
            "周涨%": week["reference_change_pct"],
            "周涨起结算": week["start_settle"], "周涨止结算": week["end_settle"],
            "SC护栏结算周涨%": week["settlement_change_pct"] if is_oil else None,
            "SC护栏数据状态": week["settlement_status"] if is_oil else "not_applicable",
            "结算证据缺项": "|".join(week["settlement_missing_fields"]),
            "价格证据错误": None}


def collect_contract_data(sym):
    """Preserve each independent result; a calculation failure is not a veto."""
    result = {"合约": sym, "数据截至": None,
              "SC护栏数据状态": "unknown" if sym.startswith("SC") else "not_applicable"}
    try:
        result.update(contract_price_evidence(sym))
    except Exception as exc:
        result.update(价格证据错误=str(exc), 结算证据缺项="price_evidence_unavailable")
    try:
        result.update(indicators(sym))
        result.update(指标状态="available", 指标错误=None)
    except Exception as exc:
        result.update(指标状态="unknown", 指标错误=str(exc),
                      否决检查="指标计算未完成；不是已核策略否决，价格证据见独立列")
    return result


def _tr(df):
    pc = df["px"].shift(1)
    return pd.concat([df["high"] - df["low"],
                      (df["high"] - pc).abs(),
                      (df["low"] - pc).abs()], axis=1).max(axis=1)


def indicators(sym):
    df = daily(sym)
    df = df[df["trade_date"] <= AS_OF].reset_index(drop=True)
    price_data = df[["px", "high", "low"]].apply(pd.to_numeric, errors="coerce")
    if (not np.isfinite(price_data).all().all() or (price_data <= 0).any().any()
            or (price_data["high"] < price_data["low"]).any()):
        raise RuntimeError("数据缺失: OHLC/结算价无效，不计算指标")
    if len(df) < 70:
        raise RuntimeError(f"样本仅{len(df)}日, 不足以计算")

    tr = _tr(df)
    atr20 = tr.ewm(alpha=1 / 20, adjust=False).mean()

    up, dn = df["high"].diff(), -df["low"].diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0))
    ndm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0))
    atr14 = tr.ewm(alpha=1 / 14, adjust=False).mean()
    pdi = 100 * pdm.ewm(alpha=1 / 14, adjust=False).mean() / atr14
    ndi = 100 * ndm.ewm(alpha=1 / 14, adjust=False).mean() / atr14
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi).replace(0, np.nan)
    adx14 = dx.ewm(alpha=1 / 14, adjust=False).mean()

    r = np.log(df["px"]).diff()
    hv20 = r.rolling(20).std() * np.sqrt(252) * 100
    hv60 = r.rolling(60).std() * np.sqrt(252) * 100

    tail = atr20.tail(250)
    atr_pct = float((tail < atr20.iloc[-1]).mean() * 100)

    # ---- 位置/均线/流动性/否决检查 ----
    px_now = float(df["px"].iloc[-1])
    h250 = float(df["high"].tail(250).max())
    dist_h250 = (h250 - px_now) / h250 * 100 if h250 > 0 else np.nan
    h20 = float(df["high"].tail(20).max())
    l20 = float(df["low"].tail(20).min())
    h60 = float(df["high"].tail(60).max())
    l60 = float(df["low"].tail(60).min())
    ma20 = float(df["px"].tail(20).mean())
    ma60 = float(df["px"].tail(60).mean())
    try:
        vol20 = _volume20(sym)
    except (ValueError, KeyError, TypeError):
        vol20 = np.nan

    try:
        dte = _busdays(AS_OF, delist_date(sym))
    except Exception:
        dte = None

    veto = []
    signal = sym in SIGNAL_LEGS          # ★v1.8 信号席: 不建仓, 不受#1/#2(框架 0)注c)
    if dte is None:
        veto.append("#1数据缺失·到期解析失败⚠")
    elif dte < 20:
        veto.append("信号腿·不受#1(随主力换月)" if signal else "距到期<20⚠")
    if CAL_DEGRADED:
        veto.append("#1数据缺失·交易日历降级需复核⚠")
    if not np.isfinite(vol20):
        veto.append("#2数据缺失·20日成交量不足或无效⚠")
    elif vol20 < 10000:
        veto.append("信号腿·不受#2" if signal else "均成交<1万⚠")

    # ---- ★v1.5 D12 判据与 ATR 分层 (v2.9 3.5b) ----
    # D12 触发 = HV20/HV60>1.3 或 ATR20分位>80 或 事件T-3(§0b配置, 按受影响品种打标)。
    # 适用 = 全部方向性单边(多空对称·全品种, v2.9扩展 —— 股指/国债列由「仅参考」
    #        转为实际生效); 结构表达(月差/升水结构/价差/carry)豁免; 中性/低不扣。
    # 错位分层: 高波>80 → 方向性单边系数×0.5 + SL用当期重校准ATR + gap收紧一档 +
    #           隔夜须过§2c核验(0.3#25); 低波<40 + 事件T-3 → 按常规层处理(防低波陷阱)。
    prod = re.match(r"[A-Za-z]+", sym).group().upper()
    ev_t3 = ("ALL" in _T3_PRODS) or (prod in _T3_PRODS)
    early_window = ("ALL" in _EARLY_PRODS) or (prod in _EARLY_PRODS)
    reasons = []
    if hv60.iloc[-1] and (hv20.iloc[-1] / hv60.iloc[-1] > 1.3):
        reasons.append("HV")
    if atr_pct > 80:
        reasons.append("ATR分位")
    if ev_t3:
        reasons.append("事件T-3")
    if early_window:
        reasons.append("既有提前风险窗")
    d12_tag = ("切换升档(" + "+".join(reasons) + ")") if reasons else "-"
    layer = ("高波>80" if atr_pct > 80 else
             ("低波<40" if atr_pct < 40 else "常规40-80"))
    if atr_pct < 40 and (ev_t3 or early_window):
        layer = "低波→按常规(事件T-3或既有提前风险窗)"

    # The weekly anchor is the latest completed market date minus 7 calendar
    # days, not the research AS_OF date. Reference returns may use close fallback;
    # the SC oil guard
    # requires valid raw settlement at BOTH actual calendar-week endpoints.
    week = weekly_price_evidence(df.to_dict("records"), AS_OF)
    wk_chg = week["reference_change_pct"]
    oil_change = week["settlement_change_pct"] if prod == "SC" else None
    oil_status = week["settlement_status"] if prod == "SC" else "not_applicable"
    if oil_status == "unknown":
        veto.append("SC原油护栏数据unknown·两端有效结算价未齐，不据收盘/混合周涨判命中")
    # 仅2ATR情景上界：预算先折减后一次取整，不提供最终#31裁决。
    spec = CONTRACT_SPEC.get(prod)
    risk1, lots1 = np.nan, None
    if spec:
        check = precheck_2atr(float(atr20.iloc[-1]), spec[0], spec[1],
                             equity=ACCOUNT_EQUITY, high_volatility=bool(atr_pct > 80))
        if check["status"] == "valid":
            risk1 = check["precheck_risk_unit"]
            lots1 = check["precheck_lots_upper_bound"]
        else:
            veto.append("2ATR预检数据无效⚠")
    else:
        veto.append("2ATR预检缺合约参数⚠")
    if len(tail) < 250:
        veto.append(f"250日窗口样本不足({len(tail)})·指标仅代理")

    return {"合约": sym, "数据截至": df["trade_date"].iloc[-1],
            "px": round(px_now, 2),
            "price_basis": week["end_basis"],
            "settle": df["settle"].iloc[-1] if "settle" in df else None,
            "pre_settle": df["pre_settle"].iloc[-1] if "pre_settle" in df else None,
            "close": df["close"].iloc[-1] if "close" in df else None,
            "open": df["open"].iloc[-1] if "open" in df else None,
            "ATR20": round(float(atr20.iloc[-1]), 2),
            "ADX14": round(float(adx14.iloc[-1]), 1),
            "HV20%": round(float(hv20.iloc[-1]), 1),
            "HV60%": round(float(hv60.iloc[-1]), 1),
            "HV20/HV60": round(float(hv20.iloc[-1] / hv60.iloc[-1]), 2)
            if hv60.iloc[-1] else np.nan,
            "ATR20分位": round(atr_pct, 1),
            "分位样本N": int(len(tail)),
            "ATR分层": layer,
            "D12提示": d12_tag,
            "H250": round(h250, 2),
            "dist_H250%": round(dist_h250, 2),
            "H20": round(h20, 2), "L20": round(l20, 2),
            "H60": round(h60, 2), "L60": round(l60, 2),
            "MA20": round(ma20, 2), "MA60": round(ma60, 2),
            "20日均成交": int(vol20) if not np.isnan(vol20) else np.nan,
            "距到期": dte if dte is not None else np.nan,
            "周涨%": round(wk_chg, 2) if wk_chg is not None else None,
            "周涨锚日": week["anchor_date"],
            "周涨起日": week["start_date"], "周涨止日": week["end_date"],
            "周涨起价": week["start_price"], "周涨止价": week["end_price"],
            "周涨起口径": week["start_basis"], "周涨止口径": week["end_basis"],
            "周涨起结算": week["start_settle"], "周涨止结算": week["end_settle"],
            "SC护栏结算周涨%": oil_change,
            "SC护栏数据状态": oil_status,
            "2ATR情景金额(非真实SL风险)": int(round(risk1)) if not np.isnan(risk1) else np.nan,
            "2ATR预检数量上界(非最终手数)": lots1,
            "否决检查": "|".join(veto) if veto else "#1/#2数据未见否决；其余规则与账户预算未核"}


COLS_VOLA = ["合约", "数据截至", "指标状态", "指标错误", "px", "ATR20", "ADX14", "HV20%", "HV60%",
             "HV20/HV60", "ATR20分位", "分位样本N", "ATR分层", "D12提示"]
COLS_POS = ["合约", "H250", "dist_H250%", "H20", "L20", "H60", "L60",
            "MA20", "MA60", "20日均成交", "距到期", "周涨%", "2ATR情景金额(非真实SL风险)", "2ATR预检数量上界(非最终手数)", "否决检查"]
COLS_PRICE_EVIDENCE = ["合约", "数据截至", "px", "price_basis", "周涨锚日", "周涨起日", "周涨止日",
                      "周涨起价", "周涨止价", "周涨起口径", "周涨止口径", "周涨%",
                      "周涨起结算", "周涨止结算", "SC护栏结算周涨%", "SC护栏数据状态",
                      "日结算涨跌%", "近5日结算涨跌%", "#30近3日≥5%", "结算证据缺项", "价格证据错误"]


def collect_spread_research():
    results = []
    for stage, label, near, far, kind in research_pairs():
        print(f"\n研究阶段={stage}；当前对与换月准备分别验收，均不代表交易许可")
        try:
            result = spread_percentile(label, near, far, kind)
        except Exception as exc:
            result = dict(scope="research_inputs", data_status="incomplete",
                          missing_fields=[str(exc)], hard_vetoes=[], final_lots=None)
            print(f"[{label}] {near}-{far} 数据/计算未完成: {exc}；先记temporary_gap，不自动归为research_only")
        result.update(research_stage=stage, label=label, near_contract=near, far_contract=far,
                      execution_permission="not_evaluated")
        results.append(result)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(f"{OUTDIR}/spread_research_{AS_OF}.json", "w", encoding="utf-8") as output:
        json.dump(dict(as_of_date=AS_OF, scope="research_inputs", pairs=results),
                  output, ensure_ascii=False, indent=2, allow_nan=False)
    return results


def print_atr_dispersion(tab):
    """★v1.5 池内 ATR250 分位极差(v2.9 0.1 错位子维 / 3.5b 错位分层)。"""
    p = pd.to_numeric(tab["ATR20分位"], errors="coerce")
    ok = p.notna()
    if ok.sum() < 2:
        return
    rng = float(p[ok].max() - p[ok].min())
    hi = tab.loc[p[ok].idxmax(), "合约"]
    lo = tab.loc[p[ok].idxmin(), "合约"]
    verdict = ("⚠ 错位(>50): 禁止跨品种套用统一风险参数, 逐品种独立核参; "
               "方向性单边隔夜须过§2c核验(0.3#25), 极端者未重校准隔夜=0(0.1)"
               if rng > 50 else "未错位")
    print(f"\n  ★池内ATR250分位极差(0.1错位子维): {rng:.1f}  "
          f"({hi} {float(p[ok].max()):.1f} ↔ {lo} {float(p[ok].min()):.1f})")
    print(f"    判定: {verdict}")
    print("    口径注: 此处仅以监控池代理，不代表真实账户持仓或账户风险")


# -------------- §2c ATR重校准核验 (v2.9 0.3#25 / Step5 硬规则) --------------
def atr_recheck():
    print("\n---- 2c) ATR重校准核验 (v2.9 0.3#25 / Step5: 方向性单边隔夜硬前置) ----")
    if not POSITIONS:
        print("  本脚本未登记方向性持仓 —— 账户持仓与挂单风险未知，不能据此确认空仓。")
        print("  (建仓当日在配置区 POSITIONS 登记; 结构持仓豁免本节, 按各自分位/价差止损管理)")
        return
    for sym, entry_date, side, note in POSITIONS:
        try:
            df = daily(sym)
            df = df[df["trade_date"] <= AS_OF].reset_index(drop=True)
            atr = _tr(df).ewm(alpha=1 / 20, adjust=False).mean()
            m = df["trade_date"] <= str(entry_date)
            if not m.any():
                raise RuntimeError("入场日早于数据起点或格式错(YYYYMMDD)")
            i0 = int(np.where(m.values)[0][-1])
            a0, a1 = float(atr.iloc[i0]), float(atr.iloc[-1])
            p0 = float((atr.iloc[:i0 + 1].tail(250) < a0).mean() * 100)
            p1 = float((atr.tail(250) < a1).mean() * 100)
            ratio = (a1 / a0) if a0 else float("nan")
            cross = (p1 > 80) and (p0 <= 80)
            trig = (ratio > 1.3) or cross
            print(
                f"  [{sym}] {side} 入场{entry_date}{('·' + note) if note else ''}")
            print(f"     ATR20_entry={a0:.2f}(分位{p0:.0f}) → ATR20_now={a1:.2f}"
                  f"(分位{p1:.0f})  比值={ratio:.2f}  跨层升入>80: {'是' if cross else '否'}")
            msg = ("⚠ 触发重校准: 以ATR20_now重算risk_per_lot, "
                   "超出单笔上限部分次日开盘先行降仓" if trig
                   else "核验通过(比值≤1.3 且 未跨层)")
            print(f"     → {msg}")
        except Exception as e:
            print(f"  [{sym}] 核验失败: {e}")
            print("     → 按核验未完成处理: 该方向性单边不得隔夜(0.3#25: 日内了结或对冲)")
    print("  注: 结构持仓(月差/升水/价差/carry)豁免本节; 本核验为收盘例行项, 未跑=未过")


# -------------- §2d D8 周涨分位 (★v1.14, canonical 3.4) --------------
def main_mapping(prod):
    """fut_mapping 主力映射 {trade_date: ts_code}; 回看覆盖 D8 所需年份。"""
    if prod not in _mapping_cache:
        df = api().fut_mapping(ts_code=f"{prod}.{TS_SUFFIX[EXCH[prod]]}",
                               start_date=shift_year_date(AS_OF, YEARS + 1), end_date=AS_OF)
        time.sleep(0.4)
        if df is None or df.empty:
            raise RuntimeError(f"fut_mapping({prod}) 返回为空")
        _mapping_cache[prod] = dict(zip(df["trade_date"].astype(str), df["mapping_ts_code"].astype(str)))
    return _mapping_cache[prod]


def _settle_series(code, start, end):
    """历史主力的 {trade_date: settle}：已取过全生命周期日线的腿直接复用，其余只取窗口内 settle 列。"""
    sym = code.split(".")[0]
    if sym in _daily_cache:
        df = _daily_cache[sym]
        return dict(zip(df["trade_date"].astype(str), df["settle"]))
    if code not in _settle_cache:
        df = api().fut_daily(ts_code=code, start_date=start, end_date=end, fields="trade_date,settle")
        time.sleep(0.4)
        if df is None or df.empty:
            raise RuntimeError(f"{code} 在 {start}~{end} 无结算价")
        validate_unique_trade_dates(df["trade_date"].astype(str).tolist())
        _settle_cache[code] = dict(zip(df["trade_date"].astype(str), df["settle"]))
    return _settle_cache[code]


def d8_weekly_research(prod):
    """最新已完成行情日的主力结算周涨及其在近 YEARS 年周样本中的上/下尾位置。"""
    attribute = PRODUCT_ATTR[prod]   # 品种未登记属性→本行计算失败，不静默降为 unknown 档
    cal = _trade_cal()
    if not cal:
        raise ValueError("交易日历不可用，D8 不计算")
    cutoff = min(AS_OF, completed_day_cutoff())
    end_day = max(day for day in cal if day <= cutoff)
    mapping = main_mapping(prod)
    anchors = weekly_anchor_days(cal, end_day, YEARS)
    contracts = {mapping[day] for day in anchors + [end_day] if day in mapping}
    window_start = shift_year_date(end_day, YEARS + 1)
    settles, errors = {}, []
    for code in sorted(contracts):
        try:
            settles[code] = _settle_series(code, window_start, end_day)
        except Exception as e:   # 单合约取数失败只令其样本无效，不补值
            errors.append(f"{code}:{type(e).__name__}")
    result = d8_weekly_rank(cal, end_day, mapping, settles, YEARS)
    result.update(product=prod, attribute=attribute, fetch_errors=errors)
    return result


def _d8_tier(rank, cutoffs):
    """按 (扣分档, 否决档) 的前X%提示；适用性与A结构豁免另核。"""
    if rank is None or cutoffs is None:
        return "unknown"
    deduct, veto = cutoffs
    if rank >= 100 - veto:
        return f"否决档(前{veto}%)"
    if rank >= 100 - deduct:
        return f"扣分档(前{deduct}%)"
    return "—"


def print_d8_ranks():
    print("\n---- 2d) D8 周涨分位 (canonical 3.4: fut_mapping主力·同合约两端结算·终点前7自然日·"
          f"近{YEARS}年周样本; A结构豁免) ----")
    rows = []
    for prod in dict.fromkeys(_prod(sym) for sym in INDICATOR_CONTRACTS):
        try:
            r = d8_weekly_research(prod)
        except Exception as e:
            rows.append({"品种": prod, "状态": f"计算失败: {type(e).__name__}: {e}"})
            continue
        tiers = D8_TIERS.get(r["attribute"], {})
        rows.append({
            "品种": prod, "属性": r["attribute"], "主力": r["main_contract"],
            "周涨起日": r["start_date"], "周涨止日": r["end_date"],
            "结算周涨%": None if r["current_change_pct"] is None else round(r["current_change_pct"], 2),
            "样本": f"{r['sample_count']}/{r['expected_samples']}(需≥{r['required_samples']})",
            "上尾位": None if r["up_rank"] is None else round(r["up_rank"], 1),
            "下尾位": None if r["down_rank"] is None else round(r["down_rank"], 1),
            "多头档": _d8_tier(r["up_rank"], tiers.get("long")),
            "空头档": _d8_tier(r["down_rank"], tiers.get("short")),
            "状态": r["status"] + (f"·取数失败{len(r['fetch_errors'])}合约" if r["fetch_errors"] else "")})
    tab = pd.DataFrame(rows)
    os.makedirs(OUTDIR, exist_ok=True)
    tab.to_csv(f"{OUTDIR}/d8_weekly_{AS_OF}.csv", index=False, encoding="utf-8-sig")
    print(tab.to_string(index=False))
    print("  读法: 上尾位=近3年周样本中低于本周涨幅的比例; 多头看上尾、空头看下尾; #20=上尾前10%且创近250日H;")
    print("        #21=金融属性多头上尾前5%; E触发=被回归一侧前20%; 状态非available时D8=unknown, 不能当已过门。")
    return rows


# -------------- §5 影子账本 (★v1.14, canonical 4.4) --------------
def shadow_bars(plan):
    """单合约取OHLC与结算；价差只用两腿同日结算差，任一腿缺失保留为缺口。"""
    kind, contracts = plan["instrument"]["type"], plan["instrument"]["contracts"]
    if kind == "spread":
        near, far = (daily(sym).reindex(columns=["trade_date", "settle"]) for sym in contracts)
        merged = pd.merge(near, far, on="trade_date", how="outer", suffixes=("_n", "_f"))
        merged["settle"] = (pd.to_numeric(merged["settle_n"], errors="coerce")
                            - pd.to_numeric(merged["settle_f"], errors="coerce"))
        return merged.reindex(columns=["trade_date", "settle"]).to_dict("records")
    return daily(contracts[0]).reindex(columns=["trade_date", "open", "high", "low", "settle"]).to_dict("records")


def shadow_ledger():
    print("\n---- 5) 影子账本 (canonical 4.4: 事前登记计划的保守日线结算; 只供规则复评, 不是成交或账户记录) ----")
    plans, rewritten, missing_id, skipped = {}, [], 0, []
    for path in sorted(RESEARCH_DIR.glob("*-execution-audit.md")):
        text = path.read_text(encoding="utf-8")
        if '"shadow_plans"' not in text:
            continue
        try:
            document = load_audit(text, markdown=True)
        except ValueError as e:
            skipped.append(f"{path.name}: {e}")
            continue
        if not isinstance(document, dict):
            skipped.append(f"{path.name}: 顶层不是对象")
            continue
        candidates = {c.get("candidate_id"): c for c in (document.get("candidates") or []) if isinstance(c, dict)}
        for plan in document.get("shadow_plans") or []:
            if not isinstance(plan, dict) or not isinstance(plan.get("shadow_id"), str) or not plan["shadow_id"].strip():
                missing_id += 1
                continue
            sid = plan["shadow_id"]
            if sid in plans:
                if plans[sid][1] != plan:   # 同一 shadow_id 只认最早登记，事后改写不生效——但要点名
                    rewritten.append(f"{sid}@{path.name}")
                continue
            plans[sid] = (path.name, plan, candidates.get(plan.get("candidate_id")) or {})
    for item in skipped:
        print(f"  ⚠ 无法读取, 跳过: {item}")
    if missing_id:
        print(f"  ⚠ {missing_id} 条无 shadow_id 的计划已忽略(校验器应已拒绝)")
    if rewritten:
        print(f"  ⚠ 事后改写已忽略(只认最早登记): {', '.join(rewritten)}")
    if not plans:
        print("  尚无登记的影子计划(执行诊断 JSON 的 shadow_plans 为空或缺失)。")
        return []
    rows, gates = [], {}
    for sid, (source, plan, candidate) in plans.items():
        parsed, errors = parse_shadow_plan(plan)   # 先核计划结构：坏计划记 invalid，不去取数
        if errors:
            outcome = dict(shadow_id=sid, status="invalid", error="; ".join(errors))
        else:
            try:   # 取数失败(接口/合约解析)记数据缺口，不推断结果；结算本身在 try 之外，逻辑错误不被吞
                last_days = [str(delist_date(sym)) for sym in parsed["contracts"]]
                bars = shadow_bars(plan)
            except Exception as e:
                outcome = dict(shadow_id=sid, status="data_gap", error=f"{type(e).__name__}: {e}")
            else:
                if all(re.fullmatch(r"\d{8}", day) for day in last_days):
                    outcome = settle_shadow_plan(plan, bars, last_trading_day=min(last_days))
                else:
                    outcome = dict(shadow_id=sid, status="data_gap", error=f"delist_date 无效: {last_days}")
        blockers = [b for b in (candidate.get("all_blockers") or []) if isinstance(b, str)] \
            if isinstance(candidate.get("all_blockers"), list) else []
        rows.append(dict(outcome, source=source, candidate_status=candidate.get("status"),
                         blockers=",".join(blockers) or "—"))
        if outcome["status"] == "closed":
            for gate in blockers or ["(无已核阻断)"]:
                stat = gates.setdefault(gate, dict(count=0, pnl=0.0, r=0.0))
                stat["count"] += 1
                stat["pnl"] += outcome["pnl_cny"]
                stat["r"] += outcome["r_multiple"]
    tab = pd.DataFrame(rows).reindex(columns=[
        "shadow_id", "source", "candidate_status", "blockers", "status", "fill_date", "fill_price",
        "exit_date", "exit_price", "exit_reason", "pnl_cny", "r_multiple", "unrealized_pnl_cny", "last_date", "error"])
    os.makedirs(OUTDIR, exist_ok=True)
    tab.to_csv(f"{OUTDIR}/shadow_ledger_{AS_OF}.csv", index=False, encoding="utf-8-sig")
    print(tab.to_string(index=False))
    print("  已了结影子按登记时的已核阻断归集(一笔多条阻断各计一次, 非独立因果):")
    for gate, stat in sorted(gates.items()):
        print(f"    {gate}: {stat['count']} 笔, 合计 {stat['pnl']:+,.0f} 元, 平均 {stat['r'] / stat['count']:+.2f}R")
    if not gates:
        print("    暂无已了结影子计划。")
    return rows


def tee_output(path):
    """把 stdout+stderr 同时写入快照文件；返回 restore()。sys.exit 的报错也会落进文件，末行“快照完成”才算完整。"""
    class _Tee:
        def __init__(self, stream, sink):
            self.stream, self.sink = stream, sink

        def write(self, data):
            self.stream.write(data)
            self.sink.write(data)

        def flush(self):
            self.stream.flush()
            self.sink.flush()

    sink = open(path, "w", encoding="utf-8")
    originals = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = _Tee(originals[0], sink), _Tee(originals[1], sink)

    def restore():
        sys.stdout, sys.stderr = originals
        sink.close()
    return restore


def _valid_date(s):
    try:
        datetime.strptime(s, "%Y%m%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"日期需为 YYYYMMDD 格式: {s!r}")
    return s


def main():
    global AS_OF
    parser = argparse.ArgumentParser(
        description="v2.26 框架数据脚本 (Tushare Pro, v1.15)")
    parser.add_argument(
        "--as-of", type=_valid_date, default=AS_OF, metavar="YYYYMMDD",
        help="复盘基准日 (缺省=运行当天, 当前默认 %(default)s)")
    parser.add_argument("--no-snapshot", action="store_true",
                        help="只打印，不写 research/<AS_OF>-data-snapshot.txt(框架0D行情快照)")
    args = parser.parse_args()
    AS_OF = args.as_of
    snapshot = None if args.no_snapshot else RESEARCH_DIR / f"{AS_OF[:4]}-{AS_OF[4:6]}-{AS_OF[6:]}-data-snapshot.txt"
    restore = tee_output(snapshot) if snapshot else None
    try:
        run(snapshot)
    finally:
        if restore:
            restore()


def run(snapshot):

    print(f"== v2.26 框架数据脚本 v1.15 | AS_OF={AS_OF} | 同期窗口±{WIN} | "
          f"2ATR预检预算{RISK_BUDGET:,.0f}(非账户剩余额度) | 事件节点{len(EVENTS)}项(用户维护) ==")
    print(f"日线上界={min(AS_OF, completed_day_cutoff())}（北京时间18:00前保守排除当天；"
          "实际最新行情日逐腿显示；本时刻规则不宣称数据源已发布最终结算）")

    spec_check()                     # ★v1.8 合约参数校验, 不过直接退出
    contract_freshness_check()

    # §0b: 先算事件窗口 → §2 的 D12「事件T-3」判据依赖本结果
    _T3_PRODS.clear()
    _EARLY_PRODS.clear()
    _T3_PRODS.update(print_event_calendar())
    _EARLY_PRODS.update(print_fixed_risk_windows())

    print("\n---- 1) 价差同期分位 (输入B: MA/RB/SR研究候选·计划未完成 / SC近端信号) ----")
    collect_spread_research()

    print("\n---- 2) 单合约指标 (输入A: D12全品种·双向 / ATR分层与极差 / D11位置 / "
          "Entry参考 / 否决#1#2) ----")
    rows = [collect_contract_data(sym) for sym in INDICATOR_CONTRACTS]
    tab = pd.DataFrame(rows)
    os.makedirs(OUTDIR, exist_ok=True)
    tab.to_csv(f"{OUTDIR}/indicators_{AS_OF}.csv",
               index=False, encoding="utf-8-sig")
    print("\n  -- 2a 波动率/趋势 (D12·含事件T-3判据 / ATR分层) --")
    print(tab.reindex(columns=COLS_VOLA).to_string(index=False))
    print("\n  -- 2b 位置/均线/流动性 (D11 / Entry / 否决#1#2 / v1.11 参考周涨%·2ATR情景金额/预检上界，非最终手数) --")
    print(tab.reindex(columns=COLS_POS).to_string(index=False))
    print("\n  -- 2b.1 价格证据与原油护栏 (参考周涨可含close；SC护栏只读两端settle专用列；★v1.16 日结算涨跌%=settle/pre_settle, #30列仅数值提示; unknown不等于触发或解除) --")
    print(tab.reindex(columns=COLS_PRICE_EVIDENCE).to_string(index=False))

    print_atr_dispersion(tab)

    atr_recheck()

    print_d8_ranks()

    print("\n---- 3)/4) 股指年化贴水 / 国债30Y-10Y利差: ★v1.8 已随 IM/IC、TL/T 退出执行池删除"
          "(框架 v2.20 周度扫描; 复活时从 git v1.7 取回 §3/§4 代码与配置) ----")

    shadow_ledger()

    print(f"\n完成。CSV 已写入 {OUTDIR}/ ; 快照={snapshot or '未写(--no-snapshot)'}，提交后即为框架0D行情快照。")
    print("注1: ATR20分位/H250/dist_H250%/H20等为单合约自身历史近似; 样本N<250时")
    print("     H250实为上市以来高点, D11口径偏松, 以「分位样本N」列酌情解读;")
    print("     A同期样本按固定3年逐年至少33/41验收，33–40只警示；分位不证明回归收益。")
    print("     D8按fut_mapping主力逐周取同一合约两端结算(不拼接复权)，有效周样本<80%为unknown；A结构豁免D8。")
    print("     B窗口/价格验算：python3 scripts/seasonal_plan.py --input <JSON>；输入需按SEASONAL_PLAN_INPUT.md组装，不因本表缺列报告定义缺失。")
    print("注2: 到期/距到期与事件T-n用trade_cal真实交易日(已剔节假日; ★v1.7);")
    print("     " + ("本次口径正常, 无降级。" if not CAL_DEGRADED else
                     "⚠本次已降级为busday近似, 原因: " + "; ".join(CAL_DEGRADED)))
    print("     周涨%终点=最新已完成实际行情日，起点=该日-7自然日及之前最近交易日；显示两端日期/口径；")
    print("     SC原油护栏仅用专用结算周涨列，两端任一结算价缺失或非正数则unknown，不用close填充；")
    print("     同对价差1/5/10交易日变化须固定合约对、完整日历窗口和一致价格口径，缺项为null；")
    print("     EVENTS为既有人工配置，含WASDE/硬数据暂估项；输出不代表当期已官宣核实。")
    print("     执行前必须核官方日期、时区、交易日归属和实际适用窗口；旧事件备注不是当前事实。")
    print("注3: 默认public_data；人工项按framework/futures_framework.md的0D与")
    print("     framework/FUTURES_DATA_PROTOCOL.md区分必要项和增强项，不再要求专业数据全套。")
    print("     必要执行人工项：具体方向/SL/TP与期限、真实费用、账户持仓/挂单、保证金/限仓、")
    print("     最新可执行报价及压力场景；gap_ratio=压力止损损失/计划止损损失，本脚本未计算。")
    print("     默认验证：已定义价格/结构确认＋至少一项独立当前产业事实；研究评分不等账户核验。")
    print("     港口库存全链、铁水/利润、战争险/通行量/出口等按模型可选；缺失只影响依赖该证据的路线。")
    print("     政策/地缘/供给强因果模型仍须自身专属证据；不可得则research_only，不以价格代理证真。")
    print("     池外休眠品种不追加例行采集，不把背景缺项扩大为全池冻结。")
    print(f"== 快照完成 | AS_OF={AS_OF} | 脚本 v1.15 | 本行存在即输出完整 ==")


if __name__ == "__main__":
    main()
