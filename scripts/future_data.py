# -*- coding: utf-8 -*-
"""
v2.9 框架数据脚本 — Tushare Pro 版 (v1.5)
====================================================================
定位: 只负责取数与计算, 按框架 v2.9 的 1.1 输入接口填坑; 不复述框架机制档位,
     框架每周滚动档位/参数时本脚本零改动。输出段与 v2.9 引用锚点对应:
  §0  合约新鲜度自检      → v2.9 否决#1(距到期<20) 前置预警, 防陈旧合约码
  §0b 事件日历核对辅助    → v2.9 0.0b(硬前置)第1/3步提示 + 3.5b「事件T-3」判据源;
                           节点由用户在配置区维护, 脚本只打印(准确性=用户责任)
  §1  价差同期分位        → v2.9 输入B: 策略A触发(≥70/≥85) / 黑色月差(RB候选启用) /
                           候选块(SC近端·PS·LH, 补全门+首期0.5) / CU存档 /
                           H-roll参考 / 国债期货价差代理(仅观察)
  §2  单合约指标          → v2.9 输入A: D12提示(全品种·双向·含事件T-3判据) /
                           ATR分层(3.5b错位分层) / 池内ATR250分位极差(0.1错位子维) /
                           D11位置(H250,dist) / Entry参考 / 否决#1#2
  §2c ATR重校准核验       → v2.9 0.3#25 / Step5: 方向性单边隔夜硬前置(空仓=无项)
  §3  股指年化贴水        → v2.9 输入C: precheck④(量化版) / D15 直判
  §4  国债30Y-10Y真实利差 → 数据补全门 = 曲线挂起态的重启前置之一(数据齐≠可执行);
                           yc_cb 权限不足 → 自动降级 akshare(东财源)

v1.4 → v1.5 变更 (对应框架 v2.8→v2.9; 框架 YAML 所称「当前v1.2 / v1.3 backlog」
                  实为「当前v1.4 → 本次v1.5」, 框架文档版本簿记待同步修正):
  ★候选块接入(v2.9 CONTRACTS 三新品种, 月份按 2026-07-12 主力/次主力核定):
     SC近端月差 = SC2609-SC2610 (INE, 主力-次月; ①近端结构联动; 每月滚动, 见维护注)
     PS 月差代理 = PS2609-PS2611 (GFEX, 主力-活跃远月; 期现升水结构的月差【代理】,
        期现基差/SMM现货维持人工 —— 用户裁决: 现货腿不走脚本)
     LH 月差代理 = LH2609-LH2701 (DCE, 主力-次主力; 远月升水回归腿的月差【代理】,
        期现升水/出栏节奏维持人工)
     EXCH 新增 INE 交易所与 SC/PS/LH 映射; INDICATOR_CONTRACTS 增 SC2609/PS2609/
     LH2609(供 0.2 可交易性与激活前置核对; 补全门未过不建仓)。
  ★价差 kind 分型扩展「候选A」「候选代理」「存档」:
     候选A(SC近端) = 照打 ≥70/≥85 触发标签 + 候选块注记(首期系数0.5, 0.3#13);
     候选代理(PS/LH) = 不打 A 触发标签, 加印远月升水%与升水同期分位(轴反转重算),
        注明「触发以期现升水分位(人工)为准」—— 防代理分位被误读为开闸信号;
     存档(CU两对) = v2.9 CU back 轮出: 仅作存量了结参考(达TP分位/⑤口径事件/
        换月前15日先到为准), 不打触发标签, 不新开不加仓。
  ★RB月差启用: RB2610-RB2701 入黑色月差池候选(v2.9), 本序列即其数据补全项。
  ★同期对照样本充足性警告: 对照不足 YEARS 年 → 显式⚠「实为近N年分位」并按
     0.3#13 审慎(PS 上市于 2024-12-26, 当前仅 1/3 年, 触发本警告属预期而非故障)。
  ★§1 加印两腿20日均成交(≤AS_OF口径): 远腿流动性(否决#2线)不再是盲区
     (v1.4 遗留: MA2701 等远腿成交量需人工另核, 本版闭环)。
  ★§1 对 A/候选A/存档 加印同期池 10/30/50 分位对应价差水平(绝对值+%两口径):
     补齐 Step5-A 的 SL(50分位)/TP1(30)/TP2(10) 锚 与 CU 存档「达TP分位了结」的
     水平参考 —— 即上轮 MA 交易解锁条件(2)「无50分位价位→无SL→R无法验证」的
     脚本侧闭环; 并就地注记 v2.9 Step5-A 的 SL/TP 方向自洽性缺陷待框架侧修复。
  ★新增 §0b 事件日历核对辅助: EVENTS 配置(用户维护) → 未来10交易日节点清单 +
     T-3 / ±1 标记; §2a「D12提示」列并入「事件T-3」判据(v2.9 3.5b 第三触发条),
     并按事件受影响品种逐合约打标; 低波层+事件T-3 → 按常规层处理(防低波陷阱)。
  ★§2 新增「ATR分层」列(高波>80 / 常规40-80 / 低波<40, 3.5b 错位分层), 与
     池内 ATR250 分位极差判定(>50=错位, 0.1 错位子维; 空仓期以监控池代理口径,
     并另给剔除挂起腿 TL/T 的口径)。
  ★新增 §2c ATR重校准核验(0.3#25 / Step5 硬规则): POSITIONS 配置逐仓登记方向性
     单边 → ATR20_now/ATR20_entry 比值(>1.3) 与 ATR250 分位跨层(升入>80) 自动
     核验; 核验失败一律按未过处理(不得隔夜)。当前空仓(2026-07-12确认), 默认为空。
  ★§4 双改: (a) 措辞对齐 v2.9 曲线挂起态 —— 补全门=重启前置之一, 数据齐≠可执行,
     复权还需「上层结构池复评重新纳入」; (b) yc_cb 权限不足 → 自动降级 akshare
     bond_zh_us_rate(东财数据中心源; 已经 akshare v1.18.64 源码核验含
     「中国国债收益率30年/10年」列), 强制按 CURVE_YEARS 回溯取数并计算近3年分位
     (修正外部补丁「当年起算无法出3年分位 + 未算分位」两处缺陷)。
  ★D12 口径注释全面更新: v2.9 扩展为全品种方向性单边·多空对称, 股指/国债的
     D12 列由「仅供参考」转为实际生效(结构表达仍豁免); 全文锚点 v2.8→v2.9,
     precheck 编号按 v2.9 1.7(①美伊×SC结构 ②数据窗+政治局 ③产能性判决
     ④贴水 ⑤归档), D13=归档态。

候选块维护注:
  - SC近端月差按月滚动: 近腿距到期 <25 交易日(§0 会在 <20 时⚠)或主力换月 →
    整对下滚一月(SC2609-SC2610 → SC2610-SC2611), 历史平移腿自动跟随。
  - PS/LH 期现升水本体 = 人工输入项(SMM 多晶硅现货 / 生猪现货与出栏节奏);
    本脚本月差代理仅供结构参考, 补全门核对以期现口径为准(v2.9 1.5 品种卡)。
  - 交易所风控现值(0.2表, 人工核对): SC 处 INE 风控升级期(2026-06 公告:
    涨跌停14%、保证金16-24%区间; 2026-04 曾单日-13%, gap 纪律从严);
    PS 类比 SI 广期所限仓过滤+保证金×0.8 沿用至公告明确退出。

适用边界 (对齐 v2.9 的 1.1 人工输入项):
  - 本脚本覆盖: 输入A/B/C(含RB月差/SC近端月差/PS·LH月差代理) + §4曲线利差 +
    否决#1#2数据 + 事件T-3判据 + ATR分层/极差 + ATR重校准核验。
  - 仍需手动/另接数据源: precheck①的现货/仓单追认代理与事件链进展、②窗口判定、
    ③产能性判决硬数据(铁水/社库/盈利率/能繁/调减进度)、PS/LH期现升水与SMM现货、
    板块分化代理(AI链vs地产链)、D9宏观序列、商品现货基差/库存/开工、
    保证金与限仓现值(交易所公告)、单周涨跌3年分位(D8, v1.6候选)、
    gap_ratio(定义悬空: 框架0.3#7引用但1.1未列, 待框架侧补列或给定义后脚本化)。
  - H250/dist/H20 等为单合约自身历史: 样本<250日时 H250 实为上市以来高点,
    D11 口径偏松(看§2「分位样本N」列), 主力连续拼接版(fut_mapping)列v1.6候选。

使用方法
  pip install tushare pandas numpy        (akshare 为§4降级源可选: pip install akshare)
  设置环境变量 TUSHARE_TOKEN (或在配置区直接填 TOKEN)
  python scripts/future_data.py [--as-of YYYYMMDD]   （已从 ai_investment 仓库迁移至此，随框架同仓维护）
  把控制台输出整体贴回对话, 或上传 ./output/*.csv

权限说明
  fut_basic / fut_daily 需 Tushare Pro 期货档积分(通常2000分)。
  index_daily(现货指数) 需指数权限; 不足→§3退化为 IM/IC 跨月价差代理提示。
  yc_cb(中债收益率曲线) 需债券档权限; 不足→§4自动降级 akshare(东财源);
  两源均失败→数据补全门维持未过(曲线挂起态下本就不进执行层)。

诚实声明
  本脚本未经线上实测(沙箱无法访问 api.tushare.pro / 东财数据中心); 以下纯计算
  路径已用合成数据离线自测: 候选代理轴反转(升水分位=价差取负后重算, 非100-x
  近似)、样本充足性警告、事件窗口标记(T-3/±1/进行中)、ATR重校准比值与跨层、
  存档/候选标签分支、ATR分层与池内极差; akshare bond_zh_us_rate 列名已经
  v1.18.64 源码核验。接口字段与权限仍请按实际环境核对, 尤其: SC/PS/LH 在
  fut_basic 的代码样式与历史平移腿存在性(PS 仅 25xx 一代)、yc_cb 参数、
  CFFEX 代码后缀。任何报错原样贴回, 我来修。
====================================================================
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
BASIS_LOOKBACK = 10     # 股指贴水「方向/收敛幅度」与「指数涨跌」回看交易日数
CONV_MIN_PP = 3.0       # ★precheck④「明显收敛」量化门槛: 回看窗口内年化贴水
#   下降 ≥ 该值(百分点)才算「明显收敛」; 置 0.0 恢复
#   v1.3 纯方向判定。改默认值需与框架 v2.9 1.7④行同步
#   (v2.9 1.7 ④行「明显收敛」注记仍待补: =10日收敛≥3pp)。
OUTDIR = "./output"

# ---- §0b 事件日历 (v2.9 0.0b / 1.4 事件轴; ★用户维护, 脚本只打印) ----
# 条目: (起始YYYYMMDD, 结束YYYYMMDD, 标签, 受影响品种tuple 或 "ALL", 处置备注)
# ⚠「暂估」项(政治局/非农/WASDE)官宣后必须改为准确日期; 新节点随 1.4 表滚动增删。
EVENTS = [
    ("20260713", "20260717", "中美数据窗(②)",
     ("IM", "IC", "JM", "J", "RB", "CU", "AL", "AU", "AG"),
     "超预期脉冲→事件窗口纪律; 横跨持仓T-1处置(6.9); 窗口内限隔夜收紧"),
    ("20260717", "20260717", "美伊事件链节点(①)",
     ("MA", "SC", "AU", "AG", "CU", "AL"),
     "±1日能源链/贵金属方向性单边新开冻结(0.1); 能源链方向性空头否决(0.3#26)"),
    ("20260728", "20260729", "FOMC",
     ("AU", "AG", "CU", "AL", "IM", "IC", "TL", "T"),
     "T-1对冲/减仓(6.9); 事件渠道处置(D13归档, 不作常态扣减)"),
    ("20260730", "20260731", "7月政治局(②·暂估月底, 官宣后改准确日期)",
     ("RB", "SI", "AL", "IM", "IC"),
     "公告级/deadline表述不加权(③); 政策脉冲日纪律(6.4)"),
    ("20260802", "20260802", "美伊事件链节点(①)",
     ("MA", "SC", "AU", "AG", "CU", "AL"),
     "同7/17节点: ±1新开冻结 + 空头否决(0.3#26)"),
    ("20260807", "20260807", "非农(暂估: 8月首个周五)",
     ("AU", "AG", "IM", "IC"),
     "T-1对冲(6.9)"),
    ("20260812", "20260812", "WASDE(暂估, 官宣后改)",
     ("M", "CF", "SR"),
     "M: 报告前2日禁新开; ±1日农产品gap收紧1.3(1.2表)"),
    ("20260831", "20260831", "8月底调减进度判决(③判决点)",
     ("SI", "PS", "RB", "AL", "LH"),
     "未达标→F池新开冻结+存量减50%+脆弱叙事扣减1.5(0.3#23)"),
]
EVENT_T3_BUSDAYS = 3     # 「临近离散事件T-3」窗口(v2.9 3.5b D12第三判据)
EVENT_HORIZON_BD = 10    # §0b 前瞻清单范围(v2.9 0.0b: 未来10个交易日)

# ---- §2c 持仓登记 (v2.9 0.3#25 ATR重校准; ★方向性单边逐仓登记, 结构持仓豁免) ----
# 条目: (合约, 入场日YYYYMMDD, "多"/"空", 备注)
POSITIONS = [
    # ("AU2610", "20260720", "多", "示例: 建仓当日即登记"),
]   # ★当前空仓(2026-07-12 会话确认) —— 建仓当日起填入, §2c 自动核验

# ---- §4 国债30Y-10Y真实利差 (数据补全门; v2.9 曲线=挂起态) ----
YC_CODE = "1001.CB"     # 中债国债收益率曲线(到期); 需债券档权限
YC_TERM_SHORT = 10.0    # 10Y
YC_TERM_LONG = 30.0     # 30Y
CURVE_YEARS = 3         # 利差「近3年分位」回看
CURVE_DIR_LOOKBACK = 10  # 利差方向回看交易日数
DV01_REG_WIN = 120      # DV01经验配比: ΔTL对ΔT 回归窗口(交易日)
CURVE_FUT_LEGS = ("TL2609", "T2609")   # DV01回归所用期货腿(随框架换月同步滚)

# 价差对: (标签, 近腿, 远腿, kind) —— 历史对照自动按年份平移生成
#   kind: "A"=策略A触发(打≥70/≥85标签) | "候选A"=候选块·照打触发+补全门注记 |
#         "候选代理"=候选块·月差代理(不打A触发标签, 期现升水以人工为准) |
#         "存档"=CU轮出·存量了结参考 | "H-roll"=H的roll参考 |
#         "结构监控"=黑色价差 | "国债期货价差"=TL-T代理(补全门以§4为准)
SPREAD_PAIRS = [
    ("MA",   "MA2609", "MA2701", "A"),
    ("CU",   "CU2609", "CU2611", "存档"),   # ★v1.5: v2.9 CU back轮出→存量了结参考
    ("CU",   "CU2609", "CU2701", "存档"),   # ★同上(远腿按实际存量核)
    ("SR",   "SR2609", "SR2701", "A"),
    ("AL",   "AL2609", "AL2611", "A"),
    ("JM",   "JM2609", "JM2701", "A"),      # 黑色月差池(纯分位; v2.9收缩叙事不加分)
    ("J",    "J2609",  "J2701",  "A"),      # 黑色月差池(同上)
    ("RB",   "RB2610", "RB2701", "A"),      # ★v1.5启用: RB月差入黑色月差池候选(v2.9),
    #                                          本序列即其数据补全项
    ("IM-roll", "IM2609", "IM2612", "H-roll"),
    ("IC-roll", "IC2609", "IC2612", "H-roll"),
    ("黑色J-RB", "J2609", "RB2610", "结构监控"),
    ("国债TL-T", "TL2609", "T2609", "国债期货价差"),
    # ---- ★v1.5 候选块 (v2.9 CONTRACTS 新增; 补全门未过不进执行层, 首期系数0.5) ----
    ("SC近端", "SC2609", "SC2610", "候选A"),    # 主力-次月(2026-07核定); ①双模定方向;
    #                                             近腿<25交易日→整对下滚一月(维护注)
    ("PS",    "PS2609", "PS2611", "候选代理"),  # 主力-活跃远月(11-12为市场月差活跃区);
    #                                             期现升水本体=人工(SMM); ⚠上市仅1年多,
    #                                             样本充足性警告会触发(预期内)
    ("LH",    "LH2609", "LH2701", "候选代理"),  # 主力-次主力(2701为升水叙事腿);
    #                                             期现升水/出栏节奏=人工
    # ---- 可选补充, 取消注释即启用 ----
    # ("黑色JM-RB", "JM2609", "RB2610", "结构监控"),  # 原料用焦煤腿版本
]

# 指标计算合约 (§2; 按 v2.9 CONTRACTS)
INDICATOR_CONTRACTS = [
    "IM2609", "IC2609",            # 股指(D事件腿/H④门; v2.9起D12列实际生效·双向)
    "TL2609", "T2609",             # 国债曲线腿(挂起·观察席; D12列对结构豁免)
    "CU2609", "AL2609",            # 有色
    "JM2609", "J2609", "RB2610",   # 黑色
    "MA2609", "SR2609",            # 能化/软商品
    "AU2610", "AG2610",            # 贵金属
    "SI2609",                      # 事件脉冲
    "CF2609", "M2609",             # 季节/观察
    "SC2609",                      # ★v1.5 候选块主力腿(INE): 0.2可交易性+激活前置核对
    "PS2609",                      # ★v1.5 候选块主力腿(GFEX): 同上; 限仓/保证金核联动SI
    "LH2609",                      # ★v1.5 候选块主力腿(DCE): 同上
]

# ★股指现货指数映射 (index_daily; 年化贴水 = 现货 vs 期货)
SPOT_INDEX = {
    "IM": ("000852.SH", "中证1000"),
    "IC": ("000905.SH", "中证500"),
    # "IF": ("000300.SH", "沪深300"),   # 备用
    # "IH": ("000016.SH", "上证50"),    # 备用
}
# 需计算年化贴水的股指期货合约 (§3)
BASIS_CONTRACTS = ["IM2609", "IC2609"]
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
        "IF": "CFFEX", "IH": "CFFEX"}         # 备用

pro = None
_basic_cache, _daily_cache, _index_cache, _yc_cache = {}, {}, {}, {}
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
                             fields="ts_code,symbol,name,list_date,delist_date")
        if df is None or df.empty:
            raise RuntimeError(f"fut_basic({exch}) 返回为空 —— 多为积分不足")
        _basic_cache[exch] = df
        time.sleep(0.4)
    return _basic_cache[exch]


def _match_rows(sym):
    """按「品种前缀正则 + 预期交割年月==delist前缀」在 fut_basic 内定位合约。

    品种前缀用 ^品种+数字 精确匹配, 而非 startswith:
    DCE 上 J/JM/JD、L/LH/LG、M, CFFEX 上 T/TL/TS/TF、IM/IC/IF/IH 等共享首字母,
    startswith 会误匹配; 要求品种码后紧跟数字即可区分(T2609 ≠ TL2609/TS2609,
    LH2609 ≠ L2609/LG2609)。
    交割年月匹配规避郑商所3位代码十年循环重复(如 MA609 在 2016/2026 各一次)。
    """
    prod = re.match(r"[A-Za-z]+", sym).group().upper()
    ym = re.search(r"\d+", sym).group()          # '2609'
    target = "20" + ym                            # '202609'
    b = basic(EXCH[prod])
    cands = b[b["ts_code"].astype(str).str.upper().str.match(rf"{prod}\d")]
    hit = cands[cands["delist_date"].astype(str).str.startswith(target)]
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


def _busdays(from_yyyymmdd, to_yyyymmdd):
    """两日期间工作日数(busday近似, 未剔节假日); to 在 from 之前则为负。"""
    a = np.datetime64(pd.to_datetime(
        str(from_yyyymmdd), format="%Y%m%d").date())
    b = np.datetime64(pd.to_datetime(str(to_yyyymmdd), format="%Y%m%d").date())
    return int(np.busday_count(a, b))


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


def index_spot(ts_code):
    """现货指数日线(收盘); 用于股指年化贴水。需 index 权限。"""
    if ts_code not in _index_cache:
        df = api().index_daily(ts_code=ts_code, fields="trade_date,close")
        time.sleep(0.4)
        if df is None or df.empty:
            raise RuntimeError(f"index_daily({ts_code}) 返回为空 —— 多为指数权限不足")
        df = df.sort_values("trade_date").reset_index(drop=True)
        _index_cache[ts_code] = df
    return _index_cache[ts_code]


def yc_term_series(term):
    """中债国债到期收益率曲线单期限序列(近CURVE_YEARS年)。需债券档权限。"""
    key = (YC_CODE, float(term))
    if key not in _yc_cache:
        df = api().yc_cb(ts_code=YC_CODE, curve_type="0",
                         start_date=shift_year_date(AS_OF, CURVE_YEARS),
                         end_date=AS_OF, curve_term=term,
                         fields="trade_date,curve_term,yield")
        time.sleep(0.4)
        if df is None or df.empty:
            raise RuntimeError(
                f"yc_cb({YC_CODE}, term={term}) 返回为空 —— 多为债券曲线权限不足")
        df = df.sort_values("trade_date").reset_index(drop=True)
        df["yield"] = pd.to_numeric(df["yield"], errors="coerce")
        _yc_cache[key] = df[["trade_date", "yield"]].dropna()
    return _yc_cache[key]


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
    """全部配置合约: 解析 + 距最后交易日检查(否决#1前置预警, busday近似)。"""
    syms, seen = [], set()
    for _label, n, f, _kind in SPREAD_PAIRS:
        syms += [n, f]
    syms += list(INDICATOR_CONTRACTS) + \
        list(BASIS_CONTRACTS) + list(CURVE_FUT_LEGS)
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
            elif days < 20:
                warns.append(
                    f"  ⚠ {s} 距最后交易日仅 {days} 交易日(<20, 触发否决#1) —— 建议滚月"
                    + ("(SC近端对: 整对下滚一月)" if s.upper().startswith("SC") else ""))
        except Exception as e:
            warns.append(f"  ⚠ {s} 解析失败: {e}")
    print("\n---- 0) 合约新鲜度自检 (否决#1 前置预警, busday近似) ----")
    if warns:
        print("\n".join(warns))
    else:
        print(f"  全部通过: {len(seen)} 个配置合约距最后交易日均 ≥20 交易日")


# ---------------- §0b 事件日历核对辅助 (v2.9 0.0b / 3.5b) ----------------
def _event_flags():
    """扫描 EVENTS → (前瞻清单, T-3受影响品种集合)。busday近似。

    定义(与 v2.9 对齐):
      进行中 = AS_OF 落在 [起始, 结束] 内;
      T-3内 = 尚未开始且距起始 ≤ EVENT_T3_BUSDAYS 个工作日(3.5b D12第三判据);
      ±1窗口 = 距起始或结束 ≤1 工作日(0.1 节点±1新开限制核对提示)。
    """
    upcoming, t3_prods = [], set()
    for st, ed, label, prods, note in EVENTS:
        ongoing = (st <= AS_OF <= ed)
        d_start = _busdays(AS_OF, st)
        d_end = _busdays(AS_OF, ed)
        in_t3 = ongoing or (AS_OF < st and d_start <= EVENT_T3_BUSDAYS)
        near_pm1 = ongoing or abs(d_start) <= 1 or abs(d_end) <= 1
        if ongoing or (AS_OF < st and d_start <= EVENT_HORIZON_BD):
            upcoming.append((st, ed, label, prods, note,
                             d_start, ongoing, in_t3, near_pm1))
        if in_t3:
            t3_prods.update(prods if prods != "ALL" else ("ALL",))
    return upcoming, t3_prods


def print_event_calendar():
    print(f"\n---- 0b) 事件日历核对辅助 (v2.9 0.0b; 未来{EVENT_HORIZON_BD}个交易日; "
          f"节点由用户在配置区维护, 脚本只打印) ----")
    upcoming, t3_prods = _event_flags()
    if not upcoming:
        print("  窗口内无已配置节点 —— 请核对框架 1.4 事件轴是否有新增/暂估项待修正")
    for st, ed, label, prods, note, d_start, ongoing, in_t3, near_pm1 in upcoming:
        span = st if st == ed else f"{st}~{ed}"
        stat = "进行中" if ongoing else f"T-{max(d_start, 0)}"
        pl = "全品种" if prods == "ALL" else "/".join(prods)
        marks = []
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
def spread_percentile(label, near, far, kind="A"):
    cur_df = pair_series(near, far)
    cur_df = cur_df[cur_df["trade_date"] <= AS_OF]
    if cur_df.empty:
        raise RuntimeError(f"{near}-{far} 在 {AS_OF} 前无重叠数据")
    cur = cur_df.iloc[-1]

    pool, used = [], []
    for k in range(1, YEARS + 1):
        n_k, f_k = shift_year_sym(near, k), shift_year_sym(far, k)
        try:
            h = pair_series(n_k, f_k)
            sub = window_around(h, shift_year_date(AS_OF, k), WIN)
            if not sub.empty:
                pool.append(sub[["spread", "spread_pct"]])
                used.append(f"{n_k}-{f_k}(n={len(sub)})")
        except Exception as e:
            used.append(f"{n_k}-{f_k}(缺失:{e})")
    if not pool:
        raise RuntimeError("历史对照全部缺失, 无法计算同期分位")

    hist = pd.concat(pool)
    hist_pct = hist["spread_pct"]
    pct_same = float((hist_pct < cur["spread_pct"]).mean() * 100)
    pct_life = float((cur_df["spread_pct"] < cur["spread_pct"]).mean() * 100)
    ok_years = len(pool)

    os.makedirs(OUTDIR, exist_ok=True)
    safe = f"{near}_{far}".replace("/", "")
    cur_df.to_csv(f"{OUTDIR}/spread_{safe}.csv", index=False)

    if kind == "A":
        tag = ("≥85 主仓触发" if pct_same >= 85 else
               "≥70 候选触发" if pct_same >= 70 else "未触发")
    elif kind == "候选A":
        base = ("≥85 主仓触发" if pct_same >= 85 else
                "≥70 候选触发" if pct_same >= 70 else "未触发")
        tag = (base + " —— 候选块(首期系数0.5): 激活前置全过才进执行层(0.3#13); "
               "①双模定方向; 美伊节点±1不新开")
    elif kind == "候选代理":
        tag = ("候选块·月差【代理】 —— 触发(≥70/≥85)以期现升水分位(人工)为准; "
               "补全门未过不进执行层(0.3#13); 首期系数0.5")
    elif kind == "存档":
        tag = ("存档·CU back轮出(v2.9) —— 仅存量了结参考: 达TP分位/⑤口径事件/"
               "换月前15日先到为准; 不新开不加仓")
    elif kind == "H-roll":
        tag = "H-roll参考(carry拉长腿) —— H开闸只看§3的④, 勿以本分位触发"
    elif kind == "结构监控":
        tag = "黑色价差监控 —— 入场门=铁水<230(基本面, 手动确认)"
    elif kind == "国债期货价差":
        tag = "期货价差代理(仅观察) —— 数据补全门以§4真实利差为准; 曲线=挂起态"
    else:
        tag = kind

    print(f"\n[{label}] {near} - {far}  (数据截至 {cur['trade_date']})")
    print(f"  当前价差: {cur['spread']:+.1f}  |  价差%: {cur['spread_pct']:+.3f}%")

    # ★v1.5 两腿20日均成交(≤AS_OF口径): 远腿流动性(否决#2)不再是盲区
    try:
        def _v20(s):
            d = daily(s)
            d = d[d["trade_date"] <= AS_OF]
            return float(pd.to_numeric(d["vol"], errors="coerce").tail(20).mean())
        vn, vf = _v20(near), _v20(far)
        warn = ""
        if not np.isnan(vf) and vf < 10000:
            warn = "  ⚠ 远腿<1万手(否决#2)"
        elif not np.isnan(vn) and vn < 10000:
            warn = "  ⚠ 近腿<1万手(否决#2)"
        print(f"  两腿20日均成交: 近 {vn:,.0f} / 远 {vf:,.0f}{warn}")
    except Exception:
        pass

    print(f"  近{YEARS}年同期分位(±{WIN}交易日): {pct_same:.1f}  → {tag}")

    # ★v1.5 SL/TP锚: 同期池 10/30/50 分位对应的价差水平(绝对值+%两口径)
    #   服务 Step5-A 的 SL(50分位)/TP1(30)/TP2(10) 与 CU 存档的「达TP分位了结」;
    #   注: v2.9 Step5-A 的 SL(50) 与 TP(30/10) 在高分位入场下同侧的方向自洽性
    #   缺陷仍待框架侧修复 —— 本行只给水平, 方向以用户裁决为准。
    if kind in ("A", "候选A", "存档"):
        lv = np.percentile(hist["spread"], [10, 30, 50])
        lp = np.percentile(hist_pct, [10, 30, 50])
        print(f"  同期池分位对应价差水平(SL/TP锚): 10分位={lv[0]:+.1f} / "
              f"30分位={lv[1]:+.1f} / 50分位={lv[2]:+.1f}"
              f"  (%口径: {lp[0]:+.3f}/{lp[1]:+.3f}/{lp[2]:+.3f})")

    # ★v1.5 候选代理: 轴反转重算升水分位(升水=远-近; 直接对取负序列重算, 非100-x近似)
    if kind == "候选代理":
        prem_cur = -float(cur["spread_pct"])
        prem_same = float(((-hist_pct) < prem_cur).mean() * 100)
        prem_life = float(((-cur_df["spread_pct"]) < prem_cur).mean() * 100)
        print(f"  远月升水%(=-价差%): {prem_cur:+.3f}%  |  升水同期分位(轴反转): "
              f"{prem_same:.1f}  |  升水生命周期分位: {prem_life:.1f}")

    # ★v1.5 样本充足性警告(0.3#13 精神: 分位口径降级须显式)
    if ok_years < YEARS:
        print(f"  ⚠ 同期对照仅 {ok_years}/{YEARS} 年 —— 本分位实为「近{ok_years}年"
              f"同期分位」, 口径降级, 按补全门审慎处理(新上市品种如 PS 属预期)")

    print(f"  本对全生命周期分位: {pct_life:.1f}  (参考)")
    print(f"  历史对照: {'; '.join(used)}")


# -------------- §3 股指年化贴水 (precheck④量化版 / D15) --------------
def stock_index_basis(fut_sym):
    """
    现货指数 vs 期货 → 年化贴水率 + 收敛幅度 + 方向 + 指数涨跌。
      年化贴水率(正=贴水) = (现货 - 期货close)/现货 × 252/到期交易日数(busday近似) × 100
      收敛幅度(pp)       = BASIS_LOOKBACK 日前年化贴水 - 当前年化贴水 (正=收敛)
      指数涨跌           = 现货指数同窗口涨跌幅
    直判:
      precheck④ = 年化贴水 ≥ 20% 且 收敛幅度 ≥ CONV_MIN_PP → 策略H可开放
                  (CONV_MIN_PP=0.0 时退化为 v1.3 纯方向判定)
      D15 双杀  = 走阔(方向) 且 指数下跌 → carry 减仓/不新开
    """
    prod = re.match(r"[A-Za-z]+", fut_sym).group().upper()
    if prod not in SPOT_INDEX:
        raise RuntimeError(f"{fut_sym} 无对应现货指数映射")
    idx_code, idx_name = SPOT_INDEX[prod]

    fut = daily(fut_sym)[["trade_date", "close"]
                         ].rename(columns={"close": "fut"})
    spot = index_spot(idx_code).rename(columns={"close": "spot"})
    m = pd.merge(spot, fut, on="trade_date")
    m = m[m["trade_date"] <= AS_OF].reset_index(drop=True)
    if len(m) < BASIS_LOOKBACK + 2:
        raise RuntimeError(f"{fut_sym} 现货/期货重叠样本仅 {len(m)} 日, 不足")

    dl = delist_date(fut_sym)
    dl_d = np.datetime64(pd.to_datetime(dl, format="%Y%m%d").date())
    td = pd.to_datetime(
        m["trade_date"], format="%Y%m%d").values.astype("datetime64[D]")
    busdays = np.busday_count(td, np.full(len(td), dl_d)).astype(float)
    busdays = np.clip(busdays, 1.0, None)   # 避免到期日除零/反号

    m["basis"] = m["fut"] - m["spot"]                         # 负=贴水
    m["disc_pct"] = (m["spot"] - m["fut"]) / m["spot"] * 100  # 正=贴水(未年化)
    m["disc_ann"] = m["disc_pct"] * 252.0 / busdays           # 年化贴水率(正=贴水)

    cur = m.iloc[-1]
    prev = m.iloc[-1 - BASIS_LOOKBACK]
    ann_now, ann_prev = float(cur["disc_ann"]), float(prev["disc_ann"])
    conv_pp = ann_prev - ann_now            # 正=收敛幅度
    direction = "收敛(企稳)" if ann_now < ann_prev else (
        "走阔" if ann_now > ann_prev else "持平")
    idx_chg = (float(cur["spot"]) / float(prev["spot"]) - 1) * 100

    # 年化贴水率在本合约生命周期内的分位
    pct_life = float((m["disc_ann"] < ann_now).mean() * 100)

    precheck4 = (ann_now >= 20.0) and (conv_pp >= CONV_MIN_PP)
    d15_double = (ann_now > ann_prev) and (idx_chg < 0)

    os.makedirs(OUTDIR, exist_ok=True)
    m.to_csv(f"{OUTDIR}/basis_{fut_sym}.csv",
             index=False, encoding="utf-8-sig")

    print(
        f"\n[{fut_sym}] 现货 {idx_name}({idx_code}) vs 期货  (数据截至 {cur['trade_date']})")
    print(f"  现货: {cur['spot']:.1f}  期货: {cur['fut']:.1f}  基差: {cur['basis']:+.1f}  "
          f"(到期约 {int(busdays[-1])} 交易日)")
    print(
        f"  年化贴水率: {ann_now:.1f}%  |  {BASIS_LOOKBACK}日前: {ann_prev:.1f}%  → 方向: {direction}")
    print(f"  {BASIS_LOOKBACK}日收敛幅度: {conv_pp:+.1f}pp  "
          f"(④量化门: 年化贴水≥20% 且 收敛≥{CONV_MIN_PP:.1f}pp)")
    print(f"  同窗口指数涨跌: {idx_chg:+.2f}%  |  年化贴水率本合约生命周期分位: {pct_life:.0f}")
    print(f"  → precheck④ (→ 策略H可开放): {'✓ 满足' if precheck4 else '✗ 未满足'}")
    print(f"  → D15 双杀 (走阔 且 指数下跌 → carry减仓/不新开): "
          f"{'⚠ 触发' if d15_double else '— 未触发'}")


# -------------- §4 国债30Y-10Y真实利差 (数据补全门; v2.9 曲线=挂起态) --------------
def dv01_ratio_hint(tl_sym, t_sym, win=DV01_REG_WIN):
    """ΔTL 对 ΔT 的回归斜率 ≈ 每1手TL需β手T对冲(DV01经验配比 T:TL ≈ β:1)。"""
    m = pd.merge(daily(tl_sym)[["trade_date", "px"]],
                 daily(t_sym)[["trade_date", "px"]],
                 on="trade_date", suffixes=("_tl", "_t"))
    m = m[m["trade_date"] <= AS_OF].tail(win + 1)
    d = m[["px_tl", "px_t"]].diff().dropna()
    if len(d) < 30 or float(d["px_t"].var()) == 0:
        raise RuntimeError(f"Δ价样本不足({len(d)})或方差为零")
    beta = float(d["px_t"].cov(d["px_tl"]) / d["px_t"].var())
    return beta, len(d)


def _curve_frame_tushare():
    """主源: tushare yc_cb 中债国债收益率曲线。"""
    s10 = yc_term_series(YC_TERM_SHORT).rename(columns={"yield": "y10"})
    s30 = yc_term_series(YC_TERM_LONG).rename(columns={"yield": "y30"})
    m = pd.merge(s10, s30, on="trade_date").dropna()
    return m, f"tushare yc_cb {YC_CODE}(中债国债收益率曲线)"


def _curve_frame_akshare():
    """降级源: akshare → 东方财富数据中心 中美国债收益率(需 pip install akshare)。

    ★列名已经 akshare v1.18.64 源码核验: 含「中国国债收益率30年/10年」。
    ★必须按 CURVE_YEARS 回溯取数(勿从当年起算, 否则近3年分位无从计算)且计算分位
      —— 此为对上轮外部补丁两处缺陷(起始日期不足 + 未算分位)的修正。
    ★东财为转载源: 首跑建议与中国债券信息网(中债估值)抽核一次。
    """
    import akshare as ak
    raw = ak.bond_zh_us_rate(start_date=shift_year_date(AS_OF, CURVE_YEARS))
    raw = raw.rename(columns={"日期": "trade_date",
                              "中国国债收益率10年": "y10",
                              "中国国债收益率30年": "y30"})
    m = raw[["trade_date", "y10", "y30"]].copy()
    m["trade_date"] = pd.to_datetime(m["trade_date"]).dt.strftime("%Y%m%d")
    m["y10"] = pd.to_numeric(m["y10"], errors="coerce")
    m["y30"] = pd.to_numeric(m["y30"], errors="coerce")
    m = m.dropna().sort_values("trade_date").reset_index(drop=True)
    return m, "akshare bond_zh_us_rate(东财数据中心, 降级源 —— 首跑请与中国债券信息网抽核)"


def bond_curve_30_10():
    """中债国债 30Y-10Y 利差: bp + 近3年分位 + 方向; yc_cb失败自动降级akshare。"""
    m, src, errs = None, None, []
    for fetch in (_curve_frame_tushare, _curve_frame_akshare):
        try:
            m, src = fetch()
            break
        except Exception as e:
            errs.append(f"{fetch.__name__}: {e}")
    if m is None:
        raise RuntimeError("; ".join(errs) +
                           " —— 若 akshare 未安装可 pip install akshare 后重试")

    m = m[m["trade_date"] <= AS_OF].reset_index(drop=True)
    if len(m) < CURVE_DIR_LOOKBACK + 2:
        raise RuntimeError(f"曲线重叠样本仅 {len(m)} 日, 不足")
    m["spread_bp"] = (m["y30"] - m["y10"]) * 100.0

    cur, prev = m.iloc[-1], m.iloc[-1 - CURVE_DIR_LOOKBACK]
    sp_now, sp_prev = float(cur["spread_bp"]), float(prev["spread_bp"])
    pct3y = float((m["spread_bp"] < sp_now).mean() * 100)
    direction = "走阔" if sp_now > sp_prev else (
        "收窄" if sp_now < sp_prev else "持平")
    trigger = ("≥70 → 利差偏宽: 回归收敛候选(复权后适用)" if pct3y >= 70 else
               "≤30 → 利差偏窄: 回归走阔候选(复权后适用)" if pct3y <= 30 else
               "30-70 中性区: 不触发")

    os.makedirs(OUTDIR, exist_ok=True)
    m.to_csv(f"{OUTDIR}/curve_30y10y_{AS_OF}.csv",
             index=False, encoding="utf-8-sig")

    print(f"\n[国债30Y-10Y] 30Y-10Y 到期收益率利差  (数据截至 {cur['trade_date']})")
    print(f"  数据源: {src}")
    print(f"  10Y: {float(cur['y10']):.3f}%  30Y: {float(cur['y30']):.3f}%  "
          f"利差: {sp_now:.1f}bp")
    print(f"  近{CURVE_YEARS}年分位: {pct3y:.1f}  → {trigger}")
    print(f"  {CURVE_DIR_LOOKBACK}日前利差: {sp_prev:.1f}bp  → 方向: {direction}  "
          f"(样本 {len(m)} 日)")
    print("  → 数据补全门: ✓ 数据侧已齐(利差精确值 + 近3年分位由本节给出)")
    print("    ⚠ v2.9 曲线=挂起态(结构池轮换轮出): 数据齐≠可执行, 本门仅为复权前置之一;")
    print("      复权还需「上层结构池复评重新纳入」(v2.9 1.5 TL/T卡), 复权前本节仅追踪进度")
    try:
        beta, n = dv01_ratio_hint(*CURVE_FUT_LEGS)
        print(f"  DV01经验配比: T:TL ≈ {beta:.1f}:1  "
              f"(近{n}日Δ结算价回归; 框架参考2~3:1, 复权后以此校准)")
    except Exception as e:
        print(f"  DV01经验配比: 计算失败({e}) —— 按框架参考 2~3:1 并以终端久期校准")


# ---------------------- §2 单合约指标 (Wilder口径) ----------------------
def _tr(df):
    pc = df["px"].shift(1)
    return pd.concat([df["high"] - df["low"],
                      (df["high"] - pc).abs(),
                      (df["low"] - pc).abs()], axis=1).max(axis=1)


def indicators(sym):
    df = daily(sym)
    df = df[df["trade_date"] <= AS_OF].reset_index(drop=True)
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
    vol20 = float(pd.to_numeric(df["vol"], errors="coerce").tail(20).mean())

    try:
        dte = _busdays(AS_OF, delist_date(sym))
    except Exception:
        dte = None

    veto = []
    if dte is None:
        veto.append("到期解析失败⚠")
    elif dte < 20:
        veto.append("距到期<20⚠")
    if not np.isnan(vol20) and vol20 < 10000:
        veto.append("均成交<1万⚠")

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
            "否决检查": "|".join(veto) if veto else "-"}


COLS_VOLA = ["合约", "数据截至", "px", "ATR20", "ADX14", "HV20%", "HV60%",
             "HV20/HV60", "ATR20分位", "分位样本N", "ATR分层", "D12提示"]
COLS_POS = ["合约", "H250", "dist_H250%", "H20", "L20", "H60", "L60",
            "MA20", "MA60", "20日均成交", "距到期", "否决检查"]


def print_atr_dispersion(tab):
    """★v1.5 池内 ATR250 分位极差(v2.9 0.1 错位子维 / 3.5b 错位分层)。"""
    p = pd.to_numeric(tab["ATR20分位"], errors="coerce")
    ok = p.notna()
    if ok.sum() < 2:
        return
    rng = float(p[ok].max() - p[ok].min())
    hi = tab.loc[p[ok].idxmax(), "合约"]
    lo = tab.loc[p[ok].idxmin(), "合约"]
    mask2 = ok & ~tab["合约"].isin(list(CURVE_FUT_LEGS))
    rng2 = float(p[mask2].max() - p[mask2].min()
                 ) if mask2.sum() >= 2 else np.nan
    verdict = ("⚠ 错位(>50): 禁止跨品种套用统一风险参数, 逐品种独立核参; "
               "方向性单边隔夜须过§2c核验(0.3#25), 极端者未重校准隔夜=0(0.1)"
               if rng > 50 else "未错位")
    print(f"\n  ★池内ATR250分位极差(0.1错位子维): {rng:.1f}  "
          f"({hi} {float(p[ok].max()):.1f} ↔ {lo} {float(p[ok].min()):.1f})")
    if not np.isnan(rng2):
        print(f"    剔除挂起腿{'/'.join(CURVE_FUT_LEGS)}后: {rng2:.1f}")
    print(f"    判定: {verdict}")
    print("    口径注: v2.9 以「持仓/候选池」为准; 空仓期以本监控池代理")


# -------------- §2c ATR重校准核验 (v2.9 0.3#25 / Step5 硬规则) --------------
def atr_recheck():
    print("\n---- 2c) ATR重校准核验 (v2.9 0.3#25 / Step5: 方向性单边隔夜硬前置) ----")
    if not POSITIONS:
        print("  当前空仓 / 无登记的方向性单边 —— 无核验项。")
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
        description="v2.9 框架数据脚本 (Tushare Pro, v1.5)")
    parser.add_argument(
        "--as-of", type=_valid_date, default=AS_OF, metavar="YYYYMMDD",
        help="复盘基准日 (缺省=运行当天, 当前默认 %(default)s)")
    args = parser.parse_args()
    AS_OF = args.as_of

    print(f"== v2.9 框架数据脚本 v1.5 | AS_OF={AS_OF} | 同期窗口±{WIN} | "
          f"贴水回看{BASIS_LOOKBACK}日 | ④收敛门槛{CONV_MIN_PP:.1f}pp | "
          f"事件节点{len(EVENTS)}项(用户维护) ==")

    contract_freshness_check()

    # §0b: 先算事件窗口 → §2 的 D12「事件T-3」判据依赖本结果
    _T3_PRODS.update(print_event_calendar())

    print("\n---- 1) 价差同期分位 (输入B: A触发 / 黑色月差含RB / 候选块 / CU存档 / "
          "H-roll参考 / 国债期货价差代理) ----")
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
    print("\n  -- 2b 位置/均线/流动性 (D11 / Entry / 否决#1#2) --")
    print(tab.reindex(columns=COLS_POS).to_string(index=False))

    print_atr_dispersion(tab)

    atr_recheck()

    print("\n---- 3) ★股指年化贴水 (输入C: precheck④量化版 / D15) ----")
    for sym in BASIS_CONTRACTS:
        try:
            stock_index_basis(sym)
        except Exception as e:
            print(f"\n[{sym}] 年化贴水 失败: {e}")
            print("  (若为 index 权限不足: 暂以§1 IM/IC 跨月价差作贴水期限结构代理, "
                  "④按未过处理; 需要免费 akshare 版的现货基差告诉我即加。)")

    print("\n---- 4) ★国债30Y-10Y真实利差 (数据补全门; v2.9 曲线=挂起态) ----")
    try:
        bond_curve_30_10()
    except Exception as e:
        print(f"\n[国债30Y-10Y] 真实利差 失败: {e}")
        print("  → 数据补全门维持未过 + 曲线挂起态(v2.9): 本就不进执行层;")
        print("    §1 的 TL-T 期货价差仅作代理观察。yc_cb权限不足会自动尝试 akshare,")
        print("    两源均失败时请检查网络/依赖(pip install akshare)后重跑。")

    print(f"\n完成。CSV 已写入 {OUTDIR}/ ; 请将上方控制台输出整体贴回对话, 或上传 CSV。")
    print("注1: ATR20分位/H250/dist_H250%/H20等为单合约自身历史近似; 样本N<250时")
    print("     H250实为上市以来高点, D11口径偏松, 以「分位样本N」列酌情解读;")
    print("     PS等新品种同期分位口径降级见§1⚠; 主力连续拼接(fut_mapping)与")
    print("     单周涨跌3年分位(D8)列v1.6候选。")
    print("注2: 到期/距到期与事件T-n用busday(工作日, 未剔节假日)近似; 临近交割年化")
    print("     贴水放大需谨慎; 现货用index_daily收盘、期货用收盘对齐基差;")
    print("     EVENTS暂估项(政治局/非农/WASDE)官宣后请立即修正。")
    print("注3: 本脚本未覆盖(维持人工, 见v2.9 1.1人工输入项): ①现货/仓单追认代理与")
    print("     事件链进展、②窗口与政治局判定、③产能性判决硬数据(铁水/社库/盈利率/")
    print("     能繁/调减进度)、PS/LH期现升水与SMM现货(用户裁决:不走脚本)、板块分化")
    print("     代理(AI链vs地产链)、保证金与限仓现值(交易所公告; SC处INE风控升级期)、")
    print("     商品现货基差、单周涨跌3年分位(D8)、gap_ratio(定义悬空, 待框架补列)。")


if __name__ == "__main__":
    main()
