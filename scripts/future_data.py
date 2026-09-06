# -*- coding: utf-8 -*-
"""
v2.21 框架数据脚本 — Tushare Pro 版 (v1.9)
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

v1.9 对应框架v2.21：方向/止损/目标闭合校验与统一账户风险预算由
scripts/futures_risk.py提供纯离线函数及JSON CLI。常规单笔/全账户风险上限
均为净值3.5%；低敞口只将全账户上限减半一次。取数脚本不假定账户风险为零。
此次修改只完成离线验证，未以v1.9联网重跑；已有output与1.txt是历史快照。
离线范围覆盖A计划校验、预算/容量计算与模拟数据输出；线上API字段与权限
仍沿用已配置Tushare Pro，本版未重新确认网络可用性或数据权限。

维护：合约近腿触#1或主力换月先到则滚动；执行目标两腿须同时核#2。
历史分位按合约年份平移与±20日窗口计算，换月前后不得当作同一信号；
不足3年或窗口不足会显式标注数据缺失。分位极值不是回归收益证明。
指标250日窗口不足时标记实际样本数。SC信号席不建仓，随主力滚月。
保证金、限仓、事件事实与账户快照仍为人工确认输入。
历代实现与停用品种见git历史；本版不扩展市场取数或策略白名单。
"""

import os
import re
import sys
import time
import argparse
from datetime import datetime
import numpy as np
import pandas as pd

try:
    from .futures_risk import precheck_2atr
except ImportError:  # direct script invocation
    from futures_risk import precheck_2atr

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
# ⚠ 日期确定性分三档, 越弱越要在官宣后回来改: (a)已定=OPEC+ 9/6、调减判决数据硬截止 9/12(框架0.3#23)、
#   俄柴油出口禁令到期 9/30(框架1.4俄乌轴行);
#   (b)「按框架1.4口径」=9/10 PPI、9/11 CPI(沃勒明示的裁决锚)、9/15-16 FOMC(多源判定, 未见官方日历原文核对);
#   (c)「暂估」=WASDE 9/11、中国8月硬数据 9/15-16。新节点随 1.4 表滚动增删;
#   两个地缘「监控窗」是不可排期项的逐周顺延占位, 到期未质变就整体后移一周。
EVENTS = [   # ★v1.8 2026-09-06 按框架 v2.20 的 1.4 事件轴刷新(1.4 表沿 v2.19 2026-09-05 判定; 用户维护项)
    #  归档移除(已落地, 见框架1.4【归档】段): 8月非农(9/4, 强: +16.2万→加息对半基准)、
    #  8000亿首批投放清单(9/1-9/2)、霍尔木兹质变日(9/1-9/3)、俄柴油禁令延期(8/29)。
    #  受影响品种元组沿框架1.4"暴露品种"原文; 其中池外品种(AG/CU/AL/IM/IC/J/SI/PS/LH/CF/SR)无指标腿,
    #  T-3/±1 打标对其无效(属预期, 见框架 v2.20 0)"池外休眠")。
    ("20260907", "20260911", "霍尔木兹中断复归侧裁决监控窗(①离散裁决对象, 不可排期; 未质变则逐周顺延)",
     ("MA", "SC", "AU", "AG", "CU", "AL"),
     "占位提醒不是事件日: ±1冻结与双向跳空预案针对真实质变headline当日; "
     "现状=中断复归侧评估·通行再受阻(4艘/日≈战前1/5, 锚一周内反转), 前两要件✓(再袭船/布雷、通行受阻), "
     "待核两要件=SC近端back反弹(脚本§1 SC近端分位/方向)+海湾出口实质下降 → 全过=中断证真、回事件冲击模式; "
     "反向质变=通行量回升至10日均以上/停火或重开官宣 → 回僵局/缓和侧评估、MA存量周五检视; "
     "任一方向质变日=能源链/贵金属方向性单边新开冻结(0.1)",
     False),
    ("20260907", "20260911", "俄乌轴质变监控窗(能源第二地缘轴, 不可排期; 未质变则逐周顺延)",
     ("MA", "SC", "AU", "AG"),
     "占位窗: 柴油出口禁令延至9/30已兑现(供给冲击升级评估执行中); 下一质变形态=禁令扩至汽油/9-30再延期(升级)"
     "|禁令解除或停火信号(回吐)|更大规模打击(炼能量级跳变); 任一出现日=双向跳空预案日, 并入0.1低敞口判定; "
     "'两轴同向=能源单边主升、地缘溢价不可逆'=3.6首要脆弱叙事",
     False),
    ("20260906", "20260906", "OPEC+会议(两轴同向背景)",
     ("MA", "SC", "AU", "AG"),
     "9月+18.8万桶/日已于8/2落地; 同向背景下: 按兵→同向延续 / 增产或闲置产能释放表态→回吐触发、MA存量周五检视; "
     "节点±1按事件窗口纪律(9/7为节点+1)"),
    ("20260910", "20260910", "8月PPI(9/11 CPI前哨; 利率裁决链第二站起点; 日期按框架1.4口径)",
     ("AU", "AG", "IM", "IC", "CU", "AL"),
     "事件窗口从T-1(9/10)起: 贵金属gap收紧1.3(1.2表, 9/10-9/17连续)、金融/准金融方向性单边T-1对冲或×0.5; "
     "PPI仅前哨, 裁决以9/11 CPI为准"),
    ("20260911", "20260911", "8月CPI(沃勒明示的裁决锚; 日期按框架1.4口径)",
     ("AU", "AG", "IM", "IC", "CU", "AL"),
     "加息对半基准(55-66%)下CPI一个数据即定方向——热→加息概率>70%、金击穿4404进趋势级回吐评估、D13继续冻结、"
     "有色宏观腿承压加重; 改善→加息<40%、4404成第一个真实支撑、FOMC按兵剧本升为基准; CPI落地即FOMC T-3, D12自动衔接; "
     "AU为信号席(0.3#31)——本节点对其只作fed_state/D13状态行输入, 无开仓动作"),
    ("20260911", "20260911", "WASDE(暂估, 官宣后改)",
     ("M", "CF", "SR"),
     "M(独立备选): 报告前2日(9/9起)禁新开; ±1日农产品gap收紧1.3(1.2表); 方向一致才考虑轻仓"),
    ("20260912", "20260912", "8月底调减进度判决·硬截止(框架0.3#23; 已定日期)",
     ("SI", "PS", "RB", "AL", "LH"),
     "9/12仍无可核数据 → 判决点'无法核验'、光伏端F腿(SI/PS)新开冻结(中性处置: 非罚则、无叙事扣减、存量不动)直至数据出现; "
     "数据到位即裁决(达标→解锁评估/未达→F冻结+叙事扣减+1.5); 挂起不得再静默顺延; 池内仅RB受影响(F远月腿本就冻结)"),
    ("20260915", "20260916", "中国8月硬数据窗(工业/社零/固投, 暂估, 官宣后改)",
     ("IM", "IC", "RB", "JM", "J", "CU", "AL"),
     "②''结构修复裁决的下一数据裁决(框架1.4; 权益端已随IM/IC退出执行池休眠); 池内RB按6.9横跨处置(JM池外); "
     "**与FOMC同窗**——横跨持仓T-1处置时两个节点合并考虑"),
    ("20260915", "20260916", "美联储9月FOMC(最大单点; fed_state终裁; 加息对半基准; 日期按框架1.4多源口径)",
     "ALL",
     "加息55-66%对半基准——**方向不预设, 加息与按兵两个剧本都入预案**: 加息→贵金属趋势级回吐评估、D13压制逻辑按新形态重写、"
     "金融属性多头全面重估; 按兵+鹰派指引→平台期延续、4404支撑测试、D13冻结延续; 按兵+转鸽→重定价反弹评估、D13复归档议题重启; "
     "**T-3(9/11)起自动D12(全品种方向性单边, 3.5b)、T-1(9/15)对冲(6.9)、#29已形式重启(T-3至T+1 AU/AG双向新开冻结)**; "
     "贵金属gap收紧1.3; 事件后T+1复评fed_state/D13/①外全部状态行; 高密度簇低敞口条款(总敞口50%)持续至T+1复评"),
    ("20260930", "20260930", "俄柴油/船用燃料出口禁令到期日(框架1.4俄乌轴行; 已定日期)",
     ("MA", "SC"),
     "到期前后=俄乌轴预设质变节点: 再延期或扩至汽油→供给冲击升级 / 到期解除→侵蚀逻辑回吐评估; "
     "任一方向均为双向跳空预案日, 能源链方向性单边新开冻结(0.1); 实际公告日若提前, 按公告日改本条"),
]
# 滚动/不可排期监测(无精确日期可登记, 人工跟踪; ★v1.8 按框架 v2.20(1.4/6.8 沿 v2.19)刷新):
#   ①政策资金结构修复裁决第二读数(②''形式过门·结构核对未过: 投放后一至两周流入结构是否向成长腿修复
#     +成交守2万亿+指数企稳; IM/IC已退出执行池, 本项仅作商品侧背景/跨资产输入);
#   ②反内卷双轨(轨一=第三份行业文件→跨行业外推裁决点; 轨二=光伏自律执行证据, 周度; ③门判据不变);
#   ③**黑色负反馈检验·第五轮提涨=检验点**(池内RB的背景输入; JM/J池外): 第五轮落地+铁水/总库存去化延续→原料主线延续;
#     受阻/钢厂减产或抵制/铁水回落/焦煤现货涨势中断→负反馈启动、原料存量多头止盈触发(不许"再看一周");
#     247家铁水与盈利率=脚本外正式数据补核项;
#   ④焦煤复产风险信号(安监放松/山西复产超预期/西曲矿复产→D14预案);
#   ⑤LC重启条件(池外·周度扫描; 证伪结案, 计数归零; 复活条件见框架0)扫描行);
#   ⑥油轮通行量持续性(①锚已反转"再受阻": 持续<10艘/日=中断证真侧输入, 回升至10日均以上=回僵局侧输入, 日度);
#   ⑦MA护栏口径(★v1.8): 原油周涨幅=§2b SC2610「周涨%」列(结算价周五对上周五), >5%→加仓权0.5/存量减50%,
#     >8%→多头冻结·清仓; #30=MA2610单日±5%; 9/4历史SC读数+15.33%命中>8%(账户持仓另核);
#   ⑧交易所风控措施公告(能源链/甲醇涨停周概率上升; 公告±1审慎, 日度核对);
#   ⑨**换月触发点**(非市场事件, 不进本表以免误打D12/±1标记; §0 会按真实交易日预警,
#     完整阶梯见框架 v2.20「合约滚动阶梯」表, ★v1.8 已收缩至池内): RB 2026-09-10(→RB2701-RB2703) /
#     MA 2026-09-16(结构对→MA2701-MA2705, 执行腿维持 MA2701) / SC 信号腿随主力换月(约9月中旬) /
#     AU 信号腿≈11月中旬 / SR·CF 2026-12-17 / M 2026-12-18; 池外品种不再跟踪。
EVENT_T3_BUSDAYS = 3     # 「临近离散事件T-3」窗口(v2.9 3.5b D12第三判据)
EVENT_HORIZON_BD = 10    # §0b 前瞻清单范围(v2.9 0.0b: 未来10个交易日)

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
    ("MA",   "MA2610", "MA2701", "A"),
    #   ★v1.7换月: 近腿→实测主力 MA2610; 远腿 MA2701。★v1.8: MA2705 9/4 实测 20 日均 12,561 已过#2,
    #   触发线 2026-09-16(近腿#1线)或主力换月 → 结构对下滚 MA2701-MA2705(执行日复核#2);
    #   方向性单边执行腿=MA2701(§2 单独取指标), 不随本对滚动
    #   2026-09-06 用户裁决: JM退出执行池并停采；历史风险估算不作新计划裁决
    ("RB",   "RB2610", "RB2701", "A"),      # RB 月差候选(黑色月差池); 触发线 2026-09-10(或主力换月先到)
    #   → 整对下滚 RB2701-RB2703(RB2703 9/4 实测 22,106 过#2; RB2705 7,717 未过)
    ("SR",   "SR2701", "SR2705", "A"),      # ★2026-09-06 用户裁决: SR 回归常驻备选, A 远月月差加回;
    #   SR2705 9/4 实测 20 日均 30,222 过#2; 触发线 2026-12-17(或主力换月)→ SR2705-SR2709
    #   黑色 JM-RB 价差(原 J2701-RB2701→JM2701-RB2701)随 JM 退出停采, 复活前提=JM 回池
    # ---- 信号席 (框架 v2.20: 不建仓, 只作①back方向与护栏口径输入) ----
    ("SC近端", "SC2610", "SC2611", "信号"),
    #   SC维持信号席，用户许可未扩展；不由研究分位自动开放建仓路径。
    #   分位仍照算(①「中断复归侧」待核要件=SC 近端 back 反弹); 主力换月日→SC2611-SC2612(SC2612 未过#2, 信号腿不受)
]

# 指标计算合约 (§2; ★v1.8 按框架 v2.20 执行池: 核心 2 + 备选 3 + 信号 2 = 8 腿; 2026-09-06 用户裁决后)
INDICATOR_CONTRACTS = [
    "MA2610",   # 主力#30护栏判定腿及A近腿；9/16或主力换月即滚动
    "MA2701",   # 方向性执行候选，真实策略止损及账户预算另核
    "RB2701",   # 黑色结构表达；不开方向性单边
    "M2701",    # 独立备选；12/18或主力换月→M2705
    "SR2701",   # 常驻备选；12/17或主力换月→SR2705
    "CF2701",   # 常驻备选；12/17或主力换月→CF2705并核#2
    "AU2612",   # 信号席：fed_state/D13价格锚；不建仓
    "SC2610",   # 信号席：MA原油周涨护栏口径腿及①输入；随主力换月滚动
]

# ---- v1.9 2ATR情景预检配置；真实#31计划裁决由futures_risk及完整规则负责 ----
ACCOUNT_EQUITY = 150000  # 预检基准净值；不替代下单时核实的账户净值
RISK_BUDGET = ACCOUNT_EQUITY * 0.035  # 2ATR情景预检的基础预算，不推断账户剩余额度
# 品种 → (multiplier 每手乘数, tick_value 最小变动价值); 新品种入池前先与框架 Step5 合约参数表同步填列
CONTRACT_SPEC = {"MA": (10, 10), "RB": (10, 10), "M": (10, 10), "SR": (10, 10), "CF": (5, 25),
                 "AU": (1000, 20), "SC": (1000, 100)}
#   启动时 spec_check() 会用 fut_basic.per_unit 交叉核对 multiplier, 不一致直接退出(宁抛错不猜)
# 信号席单腿(框架 v2.20 0)注c: 不建仓, 不受 #1/#2; §0/§2b 只打提示不打否决)
SIGNAL_LEGS = {"AU2612", "SC2610"}
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

pro = None
_basic_cache, _daily_cache = {}, {}
_cal_cache = None      # ★v1.7 §0/§0b/§2b 的「交易日数」口径源(trade_cal)
CAL_DEGRADED = []      # ★v1.7 交易日口径降级为 busday 近似的原因(§0 与注3 会打印)
_T3_PRODS = set()   # §0b 计算出的「事件T-3」受影响品种集合(供§2 D12判据)


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
            fields="trade_date,settle,close,high,low,pre_settle,vol,oi")
        time.sleep(0.4)
        if df is None or df.empty:
            raise RuntimeError(f"{sym}({code}) 日线为空")
        df = df.sort_values("trade_date").reset_index(drop=True)
        df["px"] = df["settle"].where(df["settle"].notna() & (df["settle"] > 0),
                                      df["close"])
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
    """合并两腿 → spread / spread_pct(以远腿为基)。"""
    a, b = daily(near), daily(far)
    m = pd.merge(a[["trade_date", "px"]], b[["trade_date", "px"]],
                 on="trade_date", suffixes=("_n", "_f"))
    m["spread"] = m["px_n"] - m["px_f"]
    m["spread_pct"] = m["spread"] / m["px_f"] * 100
    return m


def window_around(df, anchor, win):
    """取 anchor 日历日附近 ±win 个交易日的切片。"""
    dates = df["trade_date"].values
    pos = int(np.searchsorted(dates, anchor))
    pos = min(max(pos, 0), len(df) - 1)
    return df.iloc[max(0, pos - win): pos + win + 1]


# ---------------------- §0 合约新鲜度自检 ----------------------
def contract_freshness_check():
    """全部配置合约: 解析 + 距最后交易日检查(否决#1前置预警, trade_cal真实交易日)。"""
    syms, seen = [], set()
    for _label, n, f, _kind in SPREAD_PAIRS:
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
    legs = list(INDICATOR_CONTRACTS) + [n for _l, n, _f, _k in SPREAD_PAIRS]
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
    print(f"  v1.9 参数校验: CONTRACT_SPEC 覆盖 {len(first)} 个池内品种, multiplier 与 fut_basic.per_unit 一致"
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
        if ongoing or (AS_OF < st and d_start <= EVENT_HORIZON_BD):
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
        stat = ("占位窗·滚动" if not auto else
                "进行中" if ongoing else f"T-{max(d_start, 0)}")
        pl = "全品种" if prods == "ALL" else "/".join(prods)
        marks = []
        if not auto:
            marks.append("占位窗**不自动打标**: 真正的D12/±1触发日=质变headline当日, "
                         "由人工按0.0b第2-3步判定")
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
    pool, used, missing, blocked = [], [], [], []
    for k in range(1, YEARS + 1):
        n_k, f_k = shift_year_sym(near, k), shift_year_sym(far, k)
        try:
            hist_pair = pair_series(n_k, f_k)
            sub = window_around(hist_pair, shift_year_date(AS_OF, k), WIN)
            valid = np.isfinite(sub[["px_n", "px_f", "spread", "spread_pct"]]).all(axis=1)
            valid &= (sub["px_n"] > 0) & (sub["px_f"] > 0)
            sub = sub.loc[valid]
            if not sub.empty:
                pool.append(sub[["spread", "spread_pct"]])
            used.append(f"{n_k}-{f_k}(n={len(sub)})")
            if len(sub) < 2 * WIN + 1:
                missing.append(f"同期窗口{n_k}-{f_k}仅{len(sub)}/{2 * WIN + 1}个有效样本")
        except Exception as exc:
            used.append(f"{n_k}-{f_k}(缺失:{exc})")
            missing.append(f"历史对照{n_k}-{f_k}缺失")
    hist = pd.concat(pool) if pool else pd.DataFrame(columns=["spread", "spread_pct"])
    pct_same = float((hist["spread_pct"] < cur["spread_pct"]).mean() * 100) if len(hist) else None
    if len(pool) < YEARS:
        missing.append(f"历史年份不足{len(pool)}/{YEARS}")
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
    os.makedirs(OUTDIR, exist_ok=True)
    safe = f"{near}_{far}".replace("/", "")
    cur_df.to_csv(f"{OUTDIR}/spread_{safe}.csv", index=False)
    print(f"\n[{label}] {near} - {far}  (数据截至 {cur['trade_date']})")
    print(f"  当前价差: {cur['spread']:+.1f}  |  价差%: {cur['spread_pct']:+.3f}%")
    for name in ("近", "远"):
        volume_text = f"{volumes[name]:,.0f}" if volumes[name] is not None else "缺失"
        day_text = str(days[name]) if days[name] is not None else "缺失"
        print(f"  {name}腿20日均成交: {volume_text} | 距最后交易日: {day_text} td")
    if pct_same is None:
        tag = "数据缺失，不能评价研究候选强度"
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
    for issue in blocked:
        print(f"  ⚠ 明确否决: {issue}")
    for issue in missing:
        print(f"  ⚠ 数据缺失/不足: {issue}；不能视为已过门")
    return {"scope": "research_only", "percentile": pct_same,
            "data_status": "incomplete" if missing else "blocked" if blocked else "complete",
            "missing_fields": missing, "hard_vetoes": blocked,
            "plan_status": "incomplete" if kind == "A" else "not_applicable",
            "final_lots": None}


# ---------------------- §2 单合约指标 (Wilder口径) ----------------------
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
    reasons = []
    if hv60.iloc[-1] and (hv20.iloc[-1] / hv60.iloc[-1] > 1.3):
        reasons.append("HV")
    if atr_pct > 80:
        reasons.append("ATR分位")
    if ev_t3:
        reasons.append("事件T-3")
    d12_tag = ("切换升档(" + "+".join(reasons) + ")") if reasons else "-"
    layer = ("高波>80" if atr_pct > 80 else
             ("低波<40" if atr_pct < 40 else "常规40-80"))
    if atr_pct < 40 and ev_t3:
        layer = "低波→按常规(事件T-3)"

    # ---- ★v1.8 周涨%(护栏口径) 与 一手风险(框架 0.3#31) ----
    # 周涨% 基准 = AS_OF 前 7 个日历日内最近一个交易日的结算价(周五对上周五; 跨假期同口径),
    #   不用「5 个交易日前」—— 假期周会把跨假累计涨幅当一周涨幅喂给 MA 护栏(>5%/>8%)。
    anchor = (pd.to_datetime(AS_OF, format="%Y%m%d") - pd.Timedelta(days=7)).strftime("%Y%m%d")
    prev = df[df["trade_date"] <= anchor]
    wk_chg = ((px_now / float(prev["px"].iloc[-1]) - 1) * 100
              if len(prev) and float(prev["px"].iloc[-1]) > 0 else np.nan)
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
            "周涨%": round(wk_chg, 2) if not np.isnan(wk_chg) else np.nan,
            "2ATR情景金额(非真实SL风险)": int(round(risk1)) if not np.isnan(risk1) else np.nan,
            "2ATR预检数量上界(非最终手数)": lots1,
            "否决检查": "|".join(veto) if veto else "#1/#2数据未见否决；其余规则与账户预算未核"}


COLS_VOLA = ["合约", "数据截至", "px", "ATR20", "ADX14", "HV20%", "HV60%",
             "HV20/HV60", "ATR20分位", "分位样本N", "ATR分层", "D12提示"]
COLS_POS = ["合约", "H250", "dist_H250%", "H20", "L20", "H60", "L60",
            "MA20", "MA60", "20日均成交", "距到期", "周涨%", "2ATR情景金额(非真实SL风险)", "2ATR预检数量上界(非最终手数)", "否决检查"]


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


def _valid_date(s):
    try:
        datetime.strptime(s, "%Y%m%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"日期需为 YYYYMMDD 格式: {s!r}")
    return s


def main():
    global AS_OF
    parser = argparse.ArgumentParser(
        description="v2.21 框架数据脚本 (Tushare Pro, v1.9)")
    parser.add_argument(
        "--as-of", type=_valid_date, default=AS_OF, metavar="YYYYMMDD",
        help="复盘基准日 (缺省=运行当天, 当前默认 %(default)s)")
    args = parser.parse_args()
    AS_OF = args.as_of

    print(f"== v2.21 框架数据脚本 v1.9 | AS_OF={AS_OF} | 同期窗口±{WIN} | "
          f"2ATR预检预算{RISK_BUDGET:,.0f}(非账户剩余额度) | 事件节点{len(EVENTS)}项(用户维护) ==")

    spec_check()                     # ★v1.8 合约参数校验, 不过直接退出
    contract_freshness_check()

    # §0b: 先算事件窗口 → §2 的 D12「事件T-3」判据依赖本结果
    _T3_PRODS.update(print_event_calendar())

    print("\n---- 1) 价差同期分位 (输入B: MA/RB/SR研究候选·计划未完成 / SC近端信号) ----")
    for label, near, far, kind in SPREAD_PAIRS:
        try:
            spread_percentile(label, near, far, kind)
        except Exception as e:
            print(f"\n[{label}] {near}-{far}  失败: {e}")

    print("\n---- 2) 单合约指标 (输入A: D12全品种·双向 / ATR分层与极差 / D11位置 / "
          "Entry参考 / 否决#1#2) ----")
    rows = []
    for sym in INDICATOR_CONTRACTS:
        try:
            rows.append(indicators(sym))
        except Exception as e:
            rows.append({"合约": sym, "数据截至": f"失败: {e}"})
    tab = pd.DataFrame(rows)
    os.makedirs(OUTDIR, exist_ok=True)
    tab.to_csv(f"{OUTDIR}/indicators_{AS_OF}.csv",
               index=False, encoding="utf-8-sig")
    print("\n  -- 2a 波动率/趋势 (D12·含事件T-3判据 / ATR分层) --")
    print(tab.reindex(columns=COLS_VOLA).to_string(index=False))
    print("\n  -- 2b 位置/均线/流动性 (D11 / Entry / 否决#1#2 / v1.9 周涨%(7日历日基准)·2ATR情景金额/预检上界，非最终手数) --")
    print(tab.reindex(columns=COLS_POS).to_string(index=False))

    print_atr_dispersion(tab)

    atr_recheck()

    print("\n---- 3)/4) 股指年化贴水 / 国债30Y-10Y利差: ★v1.8 已随 IM/IC、TL/T 退出执行池删除"
          "(框架 v2.20 周度扫描; 复活时从 git v1.7 取回 §3/§4 代码与配置) ----")

    print(f"\n完成。CSV 已写入 {OUTDIR}/ ; 请将上方控制台输出整体贴回对话, 或上传 CSV。")
    print("注1: ATR20分位/H250/dist_H250%/H20等为单合约自身历史近似; 样本N<250时")
    print("     H250实为上市以来高点, D11口径偏松, 以「分位样本N」列酌情解读;")
    print("     PS等新品种同期分位口径降级见§1⚠; 主力连续拼接(fut_mapping)与")
    print("     单周涨跌3年分位(D8)列v1.6候选。")
    print("注2: 到期/距到期与事件T-n用trade_cal真实交易日(已剔节假日; ★v1.7);")
    print("     " + ("本次口径正常, 无降级。" if not CAL_DEGRADED else
                     "⚠本次已降级为busday近似, 原因: " + "; ".join(CAL_DEGRADED)))
    print("     周涨%基准=AS_OF前7日历日内最近交易日结算价(周五对上周五, 跨假期同口径);")
    print("     EVENTS暂估项(WASDE/8月硬数据)官宣后请立即修正。")
    print("注3: 本脚本未覆盖(维持人工, 见v2.9 1.1人工输入项): ①现货/仓单追认代理与")
    print("     事件链进展、②窗口与政治局判定、③产能性判决硬数据(铁水/社库/盈利率/")
    print("     能繁/调减进度)、PS/LH期现升水与SMM现货(用户裁决:不走脚本)、板块分化")
    print("     代理(AI链vs地产链)、保证金与限仓现值(交易所公告; SC处INE风控升级期)、")
    print("     商品现货基差、单周涨跌3年分位(D8)、gap_ratio(定义悬空, 待框架补列)。")


if __name__ == "__main__":
    main()
