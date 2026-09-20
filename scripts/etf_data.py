# -*- coding: utf-8 -*-
"""
ETF 轨道数据快照 — Tushare Pro + akshare (etf_data v0.1)
====================================================================
只取数与确定性计算，不输出任何买卖结论。AI 环节只读本脚本写出的快照，
卡里的价格/点位/估值/权重数字只能引用本快照的章节号或 etf_calc 的函数名。
  §0 自检：数据上界、接口可用性、缺口清单（缺口一律 [需人工补充]，不猜）
  §1 估值：PE/PB、股债利差(100/PE − 10年国债) 及分位（扩张窗 + 10年窗，附样本数）
  §2 回报分解：价格年化 = 隐含每股盈利增长 ⊗ 估值变化（复利关系，非简单相加）
  §3 指数结构：前十大、最大单一成分、行业权重、近12个月成分变动、研究覆盖率(--pool-csv)
  §4 指数口径估值自聚合：成分权重 × 个股估值逐月回算 PE/PB/股息率，含沪深300 交叉核对与分位点→点位表
  §5 工具池：持仓基金的代码/费率/净值/规模/跟踪偏离(TD)与跟踪误差(TE)，及同基金其他份额
  §6 趋势：200日均线、10月均线（只用已完成月）
  §7 宏观代理：中美10年国债、汇率中间价、金价
  §8 记分结算：随决策卡上线（M3/M4），本版不做

口径：
  · 分位=样本中严格低于当前值的占比(0-100，当前值计入样本)，历史不足5年不出结论。
  · TD/TE 取基金复权净值对指数，窗口=两者共同日期的近3年；优先全收益指数，
    只有价格指数时照算并标"指数不含分红"；外币指数按外管局中间价折人民币；币种未核=缺口。
  · 基金代码后缀一律取 fund_basic 返回的 ts_code，不按前缀推断交易所。
  · --as-of 只截断行情、净值与估值序列；基金清单、费率、赎回费、股票名称与行业是运行当日口径，
    index_weight 取 AS_OF 前 45 天内最近一期。回放历史日期时这几项不是 point-in-time。

诚实声明(v0.1, 2026-09-19)：各接口于 2026-09-19 本地实测可用(tushare 1.4.29 / akshare 1.18.64)。
乐咕乐股月频 PE 与 tushare index_dailybasic 日频 PE 都是总市值加权口径(同日 12.68 vs 13.43)；§4 自聚合是指数权重口径
(同日 15.86)，三者不可混用。§4a 在 5 个固定历史日 + 当日用同一份成分与个股数据按总市值口径复算，与两个现成源的偏差
均在 4% 以内(2026-09-19 实测)，说明成分与个股估值是当时口径；tushare 个股 pe_ttm 本身是否逐日 point-in-time 无法独立验证。
akshare 费率来自天天基金页面，未与基金公告逐只核对。
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

try:
    from .etf_calc import (aggregate_valuation, erp_spread, expanding_percentile, history_quantiles, month_end_levels,
                           return_decomposition, sma_state, tracking_difference, tracking_error)
    from .price_evidence import completed_day_cutoff
except ImportError:  # direct script invocation
    from etf_calc import (aggregate_valuation, erp_spread, expanding_percentile, history_quantiles, month_end_levels,
                          return_decomposition, sma_state, tracking_difference, tracking_error)
    from price_evidence import completed_day_cutoff

try:
    import akshare as ak
    import requests
    import tushare as ts
except ImportError:
    sys.exit("缺少依赖: 请先执行  pip install tushare akshare pandas")

HTTP_TIMEOUT = 45


_session_request = requests.Session.request


def _request_with_timeout(self, *args, **kwargs):
    """akshare 的 requests 调用不带 timeout，对端挂起即永久阻塞(2026-09-19 实测 bond_zh_us_rate 卡死 >10 分钟)。"""
    if kwargs.get("timeout") is None:
        kwargs["timeout"] = HTTP_TIMEOUT
    return _session_request(self, *args, **kwargs)

# ============================ 配置区 ============================
SCRIPT_VERSION = "v0.1"
FRAMEWORK_VERSION = "v0.1-draft"    # framework/etf_framework.md 发布后同步
TOKEN = os.getenv("TUSHARE_TOKEN", "")
AS_OF = datetime.now().strftime("%Y%m%d")
CUTOFF = AS_OF                       # run() 内按已完成交易日收紧
RESEARCH_DIR = Path(__file__).resolve().parents[1] / "research"
OUTDIR = Path(__file__).resolve().parents[1] / "output"      # 已 gitignore：§4 自聚合的原始取数缓存
AGGREGATION_START = 2005                                     # index_weight / daily_basic 的最早有效年份
PIT_CHECK_DATES = ("20071031", "20081031", "20140630", "20181228", "20210226")   # 与现成估值源交叉核对的固定日
TRACKING_YEARS = 3
MARK = "[需人工补充]"

# 指数池取自 framework/etf_index_registry.json（与卡校验器、执行侧导出产物共用一份清单）。
# source=tushare 接口名，null=无现成源；tr_code=全收益指数；weight_code=index_weight 代码；
# valuation_code=index_dailybasic 代码；currency=null 表示指数币种未核，凡需同币种比较的计算一律落缺口。
INDEX_POOL = json.loads((Path(__file__).resolve().parents[1] / "framework" / "etf_index_registry.json")
                        .read_text(encoding="utf-8"))["indexes"]

# 持仓工具：(fund_basic 的 ts_code, fund_basic 的全名——逐次运行核对, 跟踪指数 key)
HOLDINGS = [
    ("012349.OF", "天弘恒生科技ETF联接(QDII)-C", "HKTECH"),
    ("160630.SZ", "鹏华中证国防指数(LOF)-A", "399973.SZ"),
    ("021457.OF", "易方达恒生港股通红利低波动ETF联接-A", "HSHYLV"),
    ("021031.OF", "汇添富国证港股通创新药ETF联接-C", "987018.CNI"),
    ("012782.OF", "银华中证创新药产业ETF联接-C", "931152.CSI"),
    ("022448.OF", "国泰中证A500ETF联接-A", "000510.SH"),
    ("012323.OF", "华宝中证医疗ETF联接-C", "399989.SZ"),
    ("019670.OF", "广发中证香港创新药ETF联接(QDII)-A", "931787.CSI"),
    ("011615.OF", "工银瑞信上证科创板50成份ETF联接-C", "000688.SH"),
    ("010990.OF", "南方中证申万有色金属ETF联接-E", "000819.SH"),
    ("000307.OF", "易方达黄金ETF联接-A", "Au99.99"),
    ("013528.OF", "嘉实中证细分化工产业主题ETF联接-C", "000813.CSI"),
]
HK_ETF = ("02800", "盈富基金", "HSI")    # 盈立证券直持；akshare 新浪港股日线，无净值源

STATIC_GAPS = [   # 运行时探测不到的缺口；探测得到的由 gap() 逐次登记
    "§1 港股指数(恒生科技/恒指/港股通红利低波/两只港股创新药)无估值源，§4 自聚合也覆盖不了港股成分（个股估值无源）",
    "§3 恒生科技、恒指、恒生港股通红利低波动的成分与权重无现成源；QDII 标的成分无源",
    "§5 港股与跨境指数无全收益序列 → TD 对价格指数计算，含分红差",
    "§5 02800 的费率与净值无源",
]

# ============================ 运行时状态 ============================
pro = None
INTERFACES = {}
GAPS = []


def api():
    global pro
    if pro is None:
        if not TOKEN:
            sys.exit("请先设置环境变量 TUSHARE_TOKEN")
        pro = ts.pro_api(TOKEN)
    return pro


def gap(section, text):
    GAPS.append(f"{section} {text}")
    return MARK


def fetch(label, call, pause=0.35):
    """外部接口调用。失败/空表逐项记入 §0 接口清单并返回 None，其余章节照常输出。

    东财/新浪会间歇性断连或挂起(2026-09-19 实测：首跑失败、数分钟后恢复)，故失败后隔 5 秒重试一次。
    """
    for attempt in (1, 2):
        try:
            df = call()
            break
        except Exception as exc:  # 网络、权限、限频都是真实会发生的失败；不吞，落 §0
            INTERFACES[label] = f"失败 {type(exc).__name__}: {str(exc)[:100]}"
            if attempt == 2:
                return None
            time.sleep(5)
    time.sleep(pause)
    if df is None or df.empty:
        INTERFACES[label] = "空表"
        return None
    INTERFACES[label] = "通"
    return df


def days_ago(days):
    return (datetime.strptime(CUTOFF, "%Y%m%d") - timedelta(days=days)).strftime("%Y%m%d")


def num(value, digits=2, suffix=""):
    return "—" if value is None or pd.isna(value) else f"{value:,.{digits}f}{suffix}"


def iso(day):
    return "—" if day is None else (day if isinstance(day, str) else day.strftime("%Y%m%d"))


def pairs(df, column):
    """DataFrame(trade_date 升序) -> etf_calc 的 (day, value) 序列。"""
    return [(day, None if pd.isna(value) else float(value)) for day, value in zip(df["trade_date"], df[column])]


# ============================ 取数 ============================
def daily_levels(code, source, start):
    """指数/现货日线收盘 -> DataFrame(trade_date, close)，升序、去重、截至 CUTOFF。"""
    df = fetch(f"{source}:{code}", lambda: getattr(api(), source)(ts_code=code, start_date=start, end_date=CUTOFF))
    if df is None:
        return None
    df = df[["trade_date", "close"]].dropna().drop_duplicates("trade_date").sort_values("trade_date")
    return df.reset_index(drop=True)


def paged_history(label, call, pause=0.35):
    """tushare 按行数封顶（index_dailybasic 3000、index_global 4000）：按 end_date 向前翻页取全。call(end) -> DataFrame。
    index_global 另有每分钟 10 次的限频，调用方须把 pause 调到 6.5 秒以上。

    返回 (升序去重后的 DataFrame 或 None, 是否完整)。后续页失败时保留 §0 的失败状态并返回不完整，由调用方决定怎么声明。
    """
    frames, end = [], CUTOFF
    while True:
        df = fetch(label, lambda: call(end), pause)
        if df is None or df["trade_date"].max() > end:   # 后者=接口忽略了 end_date，再翻页只会死循环
            break
        frames.append(df)
        end = (datetime.strptime(df["trade_date"].min(), "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    if not frames:
        return None, False
    complete = not INTERFACES[label].startswith("失败")
    if complete:
        INTERFACES[label] = "通"          # 翻到空页是正常终点
    return pd.concat(frames).drop_duplicates("trade_date").sort_values("trade_date").reset_index(drop=True), complete


def valuation_history(code):
    df, complete = paged_history(f"index_dailybasic:{code}", lambda end: api().index_dailybasic(
        ts_code=code, end_date=end, fields="ts_code,trade_date,pe_ttm,pb"))
    if df is not None and not complete:
        gap("§1", f"{code} 估值历史翻页中断于 {df['trade_date'].iloc[0]} 之前，分位与分位点基于截断样本")
    return df


def fund_universe():
    """场外基金须 offset 分页(单页上限 15000)；场内(LOF/ETF)一页取完。"""
    frames, offset = [], 0
    while True:
        page = fetch(f"fund_basic:O@{offset}", lambda: api().fund_basic(market="O", offset=offset, limit=15000))
        if page is None or (frames and page["ts_code"].iloc[0] == frames[0]["ts_code"].iloc[0]):   # 后者=offset 被忽略
            break
        frames.append(page)
        if len(page) < 15000:
            break
        offset += len(page)
    listed = fetch("fund_basic:E", lambda: api().fund_basic(market="E"))
    if listed is not None:
        frames.append(listed)
    return pd.concat(frames, ignore_index=True) if frames else None


def fund_nav(code):
    df = fetch(f"fund_nav:{code}", lambda: api().fund_nav(
        ts_code=code, fields="ts_code,ann_date,nav_date,unit_nav,adj_nav,net_asset,total_netasset"))
    if df is None:
        return None
    df = df[df["nav_date"] <= CUTOFF].sort_values(["nav_date", "ann_date"])
    return df.drop_duplicates("nav_date", keep="last").rename(columns={"nav_date": "trade_date"}).reset_index(drop=True)


def parse_pct(text):
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", str(text))
    return float(match.group(1)) if match else None


def operating_fees(code6):
    """天天基金运作费用：一行 [管理费率, x, 托管费率, y, 销售服务费率, z]。"""
    df = fetch(f"ak.fund_fee_em:{code6}:运作费用", lambda: ak.fund_fee_em(symbol=code6, indicator="运作费用"), pause=0.2)
    if df is None:
        return {}
    cells = [str(cell) for cell in df.iloc[0].tolist()]
    return {label: parse_pct(value) for label, value in zip(cells[0::2], cells[1::2])}


def redemption_ladder(code6):
    df = fetch(f"ak.fund_fee_em:{code6}:赎回费率", lambda: ak.fund_fee_em(symbol=code6, indicator="赎回费率"), pause=0.2)
    if df is None:
        return None
    return "；".join(f"{row['适用期限']} {row['赎回费率']}" for _, row in df.iterrows())


def fx_rates():
    """外管局人民币中间价(每 100 外币) -> 每 1 外币折人民币。"""
    df = fetch("ak.currency_boc_safe", lambda: ak.currency_boc_safe(), pause=0)
    if df is None:
        return None
    df = df.rename(columns={"日期": "trade_date", "港元": "HKD", "美元": "USD"})[["trade_date", "HKD", "USD"]]
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
    df[["HKD", "USD"]] = df[["HKD", "USD"]] / 100
    return df[df["trade_date"] <= CUTOFF].sort_values("trade_date").reset_index(drop=True)


def bond_yields():
    """中国 10 年国债取中债国债收益率曲线（chinabond，经 akshare，单次最多一年，逐年取并缓存）；
    美国 10 年取东财汇总接口，仅供 §7 展示——该接口时通时断(2026-09-19 多次超时)，失败不影响股债利差。"""
    frames = []
    for year in range(AGGREGATION_START, int(CUTOFF[:4]) + 1):
        end = min(f"{year}1231", CUTOFF)
        df = cached_csv(f"bond_china_yield_{year}.csv", f"ak.bond_china_yield:{year}",
                        lambda y=year, e=end: ak.bond_china_yield(start_date=f"{y}0101", end_date=e), immutable=end < days_ago(10))
        if df is not None:
            frames.append(df[df["曲线名称"] == "中债国债收益率曲线"][["日期", "10年"]])
        elif INTERFACES.get(f"ak.bond_china_yield:{year}", "").startswith("失败"):
            gap("§1", f"中债国债收益率 {year} 年取数失败 → 整条收益率序列弃用，股债利差不可算（已成功的年份已缓存，重跑即可）")
            return None   # 缺一年会把那一年的利差压成一条平线，缺当年则会拿去年底的收益率冒充现值
    if not frames:
        return None
    china = pd.concat(frames).rename(columns={"日期": "trade_date", "10年": "cn10y"})
    china["trade_date"] = pd.to_datetime(china["trade_date"]).dt.strftime("%Y%m%d")
    china["cn10y"] = pd.to_numeric(china["cn10y"], errors="coerce")
    china = china.dropna().drop_duplicates("trade_date")
    china["cn10y_date"] = china["trade_date"]
    us = fetch("ak.bond_zh_us_rate", lambda: ak.bond_zh_us_rate(start_date=days_ago(30)), pause=0)
    if us is not None:
        us = us.rename(columns={"日期": "trade_date", "美国国债收益率10年": "us10y"})[["trade_date", "us10y"]]
        us["trade_date"] = pd.to_datetime(us["trade_date"]).dt.strftime("%Y%m%d")
        china = china.merge(us, how="outer", on="trade_date")
    else:
        china["us10y"] = None
    return china[china["trade_date"] <= CUTOFF].sort_values("trade_date").reset_index(drop=True)


def asof_join(left, right, columns):
    """给 left 的每个 trade_date 配上 right 中当日或之前最近一期的值。"""
    keyed = right[["trade_date"] + columns].dropna().assign(_day=lambda d: pd.to_datetime(d["trade_date"]))
    merged = pd.merge_asof(left.assign(_day=pd.to_datetime(left["trade_date"])).sort_values("_day"),
                           keyed.drop(columns="trade_date").sort_values("_day"), on="_day", direction="backward")
    return merged.drop(columns="_day")


def lg_valuation(symbol):
    """乐咕乐股月频：指数点位、滚动市盈率、市净率。"""
    pe = fetch(f"ak.stock_index_pe_lg:{symbol}", lambda: ak.stock_index_pe_lg(symbol=symbol), pause=0)
    pb = fetch(f"ak.stock_index_pb_lg:{symbol}", lambda: ak.stock_index_pb_lg(symbol=symbol), pause=0)
    if pe is None:
        return None
    df = pe.rename(columns={"日期": "trade_date", "指数": "close", "滚动市盈率": "pe_ttm"})[["trade_date", "close", "pe_ttm"]]
    if pb is not None:
        df = df.merge(pb.rename(columns={"日期": "trade_date", "市净率": "pb"})[["trade_date", "pb"]], how="left")
    else:
        df["pb"] = None
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
    return df[df["trade_date"] <= CUTOFF].sort_values("trade_date").reset_index(drop=True)


# ============================ §1 估值 ============================
def percentile_cell(df, column, window_years):
    result = expanding_percentile(pairs(df, column), window_years=window_years)
    if result["status"] != "complete":
        return f"—({result['missing_fields'][0]})"
    return f"{result['percentile']:.1f} (n={result['sample_n']}, 自{iso(result['first_date'])})"


def valuation_block(title, df, bonds):
    """df: trade_date, pe_ttm, pb。打印当前值与两种窗口的分位。"""
    lines = [f"\n[{title}]  数据 {df['trade_date'].iloc[0]} → {df['trade_date'].iloc[-1]}，共 {len(df)} 期"]
    if bonds is not None:
        df = asof_join(df, bonds, ["cn10y", "cn10y_date"])
        df["erp"] = [erp_spread(pe, y) for pe, y in zip(df["pe_ttm"], df["cn10y"])]
    else:
        df["cn10y"] = df["erp"] = df["cn10y_date"] = None
        if not any("10年国债收益率不可得" in item for item in GAPS):
            gap("§1", "10年国债收益率不可得 → 各指数的股债利差不可算")
    last = df.iloc[-1]
    rows = [("PE_TTM (分位高=贵)", "pe_ttm", num(last["pe_ttm"])), ("PB (分位高=贵)", "pb", num(last["pb"])),
            ("股债利差 100/PE−10年国债 (分位高=便宜)", "erp", num(last["erp"], suffix="pp"))]
    for label, column, current in rows:
        lines.append(f"  {label}: 当前 {current} | 扩张窗分位 {percentile_cell(df, column, None)}"
                     f" | 10年窗分位 {percentile_cell(df, column, 10)}")
        levels = history_quantiles(pairs(df, column))["levels"]
        if levels is not None:   # 情景的期末倍数只能取自这里，不由 AI 估
            lines.append("    历史分位点(扩张窗): " + " / ".join(f"P{point} {level:.2f}" for point, level in levels.items()))
    lines.append(f"  10年国债(估值日或之前最近一期): {num(last['cn10y'], 4, '%')} @{last['cn10y_date'] or '—'}")
    if last["cn10y_date"] and (datetime.strptime(last["trade_date"], "%Y%m%d") - datetime.strptime(last["cn10y_date"], "%Y%m%d")).days > 10:
        lines.append(f"  ⚠ 收益率比估值日早 10 天以上 → {gap('§1', title + ': 国债收益率过旧，当前股债利差存疑')}")
    return lines


def section_valuation(bonds, lg, basics):
    lines = ["\n---- §1 估值 (PE/PB/股债利差及分位；两个来源算法不同，不可混用) ----"]
    for entry in INDEX_POOL:
        if entry.get("lg_symbol") and lg.get(entry["key"]) is not None:
            lines += valuation_block(f"{entry['name']} {entry['key']} | 乐咕乐股月频", lg[entry["key"]], bonds)
        if basics.get(entry["key"]) is not None:
            lines += valuation_block(f"{entry['name']} {entry['key']} | tushare index_dailybasic 日频",
                                     basics[entry["key"]], bonds)
    missing = [entry["name"] for entry in INDEX_POOL if not entry.get("valuation_code") and not entry.get("lg_symbol")]
    lines.append(f"\n  无估值源 {MARK}: " + "、".join(missing))
    return lines


# ============================ §2 回报分解 ============================
def decomposition_rows(df, anchors):
    """df: trade_date, close, pe_ttm。anchors: (标签, 目标起点 YYYYMMDD)；起点取当时及之前最近一期。"""
    end = df.iloc[-1]
    rows = []
    for label, target in anchors:
        history = df[df["trade_date"] <= target]
        if history.empty:
            rows.append(f"  {label}: {gap('§2', f'{label}: 起点 {target} 早于数据起点')}")
            continue
        start = history.iloc[-1]
        result = return_decomposition(dict(date=start["trade_date"], level=start["close"], pe=start["pe_ttm"]),
                                      dict(date=end["trade_date"], level=end["close"], pe=end["pe_ttm"]))
        if result["status"] != "complete":
            rows.append(f"  {label}: {gap('§2', label + ': ' + ','.join(result['missing_fields']))}")
            continue
        rows.append(f"  {label}: {start['trade_date']}(点位 {num(start['close'])}, PE {num(start['pe_ttm'])}) → "
                    f"{end['trade_date']}(点位 {num(end['close'])}, PE {num(end['pe_ttm'])}) {result['years']:.1f}年 | "
                    f"价格年化 {result['price_annual_pct']:+.2f}% = 隐含每股盈利 {result['eps_annual_pct']:+.2f}% ⊗ "
                    f"估值变化 {result['valuation_annual_pct']:+.2f}%")
    return rows


def section_decomposition(lg, basics, levels):
    lines = ["\n---- §2 回报分解 (隐含每股盈利=点位÷PE；三项为复利关系 (1+价格)=(1+盈利)(1+估值)) ----"]
    for entry in INDEX_POOL:
        df = lg.get(entry["key"])
        if df is not None:
            anchors = [("自数据起点", df["trade_date"].iloc[0]), *entry.get("decomposition_anchors", []),
                       ("滚动10年", days_ago(3653)), ("滚动5年", days_ago(1826))]
            lines += [f"\n[{entry['name']} | 乐咕乐股月频]"] + decomposition_rows(df, anchors)
        basic, level = basics.get(entry["key"]), levels.get(entry["key"])
        if basic is not None and level is not None and not entry.get("lg_symbol"):
            df = basic.merge(level, on="trade_date").dropna(subset=["pe_ttm"])
            if not df.empty:
                anchors = [("自估值数据起点", df["trade_date"].iloc[0]), ("滚动5年", days_ago(1826))]
                lines += [f"\n[{entry['name']} | tushare 日频]"] + decomposition_rows(df, anchors)
    return lines


# ============================ §3 指数结构 ============================
def latest_weights(code, start, end):
    df = fetch(f"index_weight:{code}@{end}", lambda: api().index_weight(index_code=code, start_date=start, end_date=end))
    if df is None:
        return None
    return df[df["trade_date"] == df["trade_date"].max()].sort_values("weight", ascending=False).reset_index(drop=True)


def load_pool_codes(path):
    """ai_investment 的 investment_prediction.csv：表头含空格，code 为无后缀代码。"""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return {row["code"].strip() for row in csv.DictReader(handle, skipinitialspace=True) if row.get("code")}


def section_structure(pool_codes):
    lines = ["\n---- §3 指数结构 (tushare index_weight 月度、point-in-time；权重单位 %) ----"]
    stocks = fetch("stock_basic", lambda: api().stock_basic(exchange="", list_status="L", fields="ts_code,name,industry"))
    hk = fetch("hk_basic", lambda: api().hk_basic(list_status="L"))
    names = {}
    industries = {}
    if stocks is not None:
        names.update(zip(stocks["ts_code"], stocks["name"]))
        industries.update(zip(stocks["ts_code"], stocks["industry"]))
    if hk is not None:
        names.update(zip(hk["ts_code"], hk["name"]))
    if pool_codes is None:
        lines.append("  研究覆盖率: 未提供 --pool-csv，本次不计算")
    for entry in INDEX_POOL:
        code = entry.get("weight_code")
        if not code:
            continue
        now = latest_weights(code, days_ago(45), CUTOFF)
        if now is None:
            lines.append(f"\n[{entry['name']} {code}] {gap('§3', f'{code} 成分权重不可得')}")
            continue
        top = now.head(10)
        lines.append(f"\n[{entry['name']} {code}] 权重日 {now['trade_date'].iloc[0]} | 成分数 {len(now)} | "
                     f"最大单一成分 {num(now['weight'].iloc[0])}% | 前十大合计 {num(top['weight'].sum())}% | "
                     f"权重合计 {num(now['weight'].sum())}%")
        lines.append("  前十大: " + "、".join(
            f"{names.get(c, c)}({c}) {w:.2f}" for c, w in zip(top["con_code"], top["weight"])))
        sector = now.assign(industry=now["con_code"].map(industries).fillna(
            now["con_code"].str.endswith(".HK").map({True: "港股(无行业源)", False: "未知"})))
        by_industry = sector.groupby("industry")["weight"].sum().sort_values(ascending=False).head(6)
        lines.append("  行业权重(tushare industry 口径，前6): " + "、".join(f"{k} {v:.1f}" for k, v in by_industry.items()))
        year_ago = datetime.strptime(now["trade_date"].iloc[0], "%Y%m%d") - timedelta(days=365)
        before = latest_weights(code, (year_ago - timedelta(days=45)).strftime("%Y%m%d"), year_ago.strftime("%Y%m%d"))
        if before is None:
            lines.append(f"  近12个月成分变动: {gap('§3', f'{code} 一年前权重不可得')}")
        else:
            entered = now[~now["con_code"].isin(before["con_code"])]
            left = before[~before["con_code"].isin(now["con_code"])]
            lines.append(f"  近12个月成分变动({before['trade_date'].iloc[0]}→{now['trade_date'].iloc[0]}): "
                         f"调入 {len(entered)} 只(现权重合计 {entered['weight'].sum():.1f}%) / "
                         f"调出 {len(left)} 只(原权重合计 {left['weight'].sum():.1f}%)")
        if pool_codes is not None:
            covered = now[now["con_code"].str.split(".").str[0].isin(pool_codes)]
            lines.append(f"  研究覆盖率: {covered['weight'].sum():.1f}% ({len(covered)} 只在个股研究池内)")
    return lines


# ============================ §4 指数口径估值自聚合 ============================
def cached_csv(name, label, call, *, immutable):
    """output/ 下的 CSV 缓存。immutable=True 的历史片段命中即不重取；未完结的当年片段每次重取。

    接口明确返回空表（指数当年尚未发布、当日非交易日）也是不可变事实，缓存成 0 字节文件；
    取数失败不缓存——否则一次断网会被永久记成"无数据"。空表不算接口异常，不进 §0。
    """
    path = OUTDIR / name
    if immutable and path.exists():
        return pd.read_csv(path, dtype=str) if path.stat().st_size else None
    df = fetch(label, call)
    empty = df is None and INTERFACES.get(label) == "空表"
    if empty:
        del INTERFACES[label]
    if immutable and (df is not None or empty):
        OUTDIR.mkdir(exist_ok=True)
        path.touch() if empty else df.to_csv(path, index=False)
    return df


def weight_history(code):
    """index_weight 全历史，按半年取（500 只成分 × 6 个月末 = 3000 行，低于单次 6000 行上限）。"""
    frames = []
    for year in range(AGGREGATION_START, int(CUTOFF[:4]) + 1):
        for half, (start, end) in enumerate(((f"{year}0101", f"{year}0630"), (f"{year}0701", f"{year}1231")), 1):
            if start > CUTOFF:
                break
            df = cached_csv(f"index_weight_{code}_{year}H{half}.csv", f"index_weight:{code}:{year}H{half}",
                            lambda s=start, e=min(end, CUTOFF): api().index_weight(index_code=code, start_date=s, end_date=e),
                            immutable=end < days_ago(45))   # 月末权重发布有滞后：半年结束 45 天后才视为定稿
            if df is not None:
                frames.append(df)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True).drop_duplicates(["trade_date", "con_code"])
    df["weight"] = df["weight"].astype(float)
    return df[df["trade_date"] <= CUTOFF]


def market_fundamentals(day):
    """全市场当日 pe_ttm / pb / dv_ttm（一次调用）。返回 (实际估值日, {代码: 读数}) 或 None。

    接口明确返回空表 = 非交易日，回退到之前最近的交易日（最多 6 天）；取数**失败**不回退——拿前一天的估值配当天的权重是静默错数。
    近 5 天的空表可能只是 tushare 尚未发布，不当作定稿缓存。
    """
    for back in range(7):
        probe = (datetime.strptime(day, "%Y%m%d") - timedelta(days=back)).strftime("%Y%m%d")
        label = f"daily_basic:{probe}"
        df = cached_csv(f"daily_basic_{probe}.csv", label, lambda p=probe: api().daily_basic(
            trade_date=p, fields="ts_code,pe_ttm,pb,dv_ttm"), immutable=probe < days_ago(5))
        if df is not None:
            for column in ("pe_ttm", "pb", "dv_ttm"):
                df[column] = pd.to_numeric(df[column], errors="coerce")
            return probe, df.set_index("ts_code")[["pe_ttm", "pb", "dv_ttm"]].to_dict("index")
        if INTERFACES.get(label, "").startswith("失败"):
            return None
    return None


def aggregate_all(weights_by_key):
    """逐月末：成分权重 × 个股估值 → 各指数的 PE/PB/股息率序列。按日期外层循环，内存里只留一天的全市场表。

    每个指数在最新一期权重之后追加一行「数据上界当日」：最新权重 × 当日个股估值（忽略月内权重漂移），与 §6 点位同日。
    """
    plan = {}
    for key, weights in weights_by_key.items():
        months = [(day, dict(zip(month["con_code"], month["weight"]))) for day, month in weights.groupby("trade_date")]
        if months and months[-1][0] < CUTOFF:
            months.append((CUTOFF, months[-1][1]))
        for day, members in months:
            plan.setdefault(day, []).append((key, members))
    rows = {key: [] for key in weights_by_key}
    for day in sorted(plan):
        found = market_fundamentals(day)
        if found is None:
            gap("§4", f"{day}: 全市场估值不可得，{len(plan[day])} 个指数该期跳过")
            continue
        priced_on, fundamentals = found
        for key, members in plan[day]:
            if rows[key] and priced_on <= rows[key][-1]["trade_date"]:
                continue
            result = aggregate_valuation(members, fundamentals)
            rows[key].append(dict(trade_date=priced_on, pe_ttm=result["pe_ttm"], pb=result["pb"],
                                  dividend_yield_pct=result["dividend_yield_pct"], loss_weight_pct=result["loss_weight_pct"],
                                  coverage_pct=result["coverage_pct"], status=result["status"]))
    return {key: pd.DataFrame(series) for key, series in rows.items() if series}


def section_aggregation(bonds, lg, basics, levels):
    lines = ["\n---- §4 指数口径估值自聚合 (成分权重 × 个股 pe_ttm/pb/dv_ttm；亏损股盈利按 0 计，PE 因此偏低；月末口径) ----",
             "  口径：按**指数权重**（自由流通调整）调和加权 = 持有该指数的组合市盈率，点位换算与它自洽。"
             "乐咕与 tushare index_dailybasic 是**总市值加权**（Σ总市值÷Σ净利润），低估值大盘股占比更高，读数系统性偏低；两种口径不可混用。"]
    weights_by_key, skipped = {}, {}
    for entry in INDEX_POOL:
        code = entry.get("weight_code")
        if not code:
            continue
        latest = latest_weights(code, days_ago(45), CUTOFF)   # 先看最新一期：港股成分为主的指数不必再取 20 年权重史
        hk_share = 0 if latest is None else latest.loc[latest["con_code"].str.endswith(".HK"), "weight"].sum()
        if hk_share > 50:
            skipped[entry["key"]] = f"港股成分权重 {hk_share:.0f}%，个股估值无源 → {gap('§4', f'{code} 港股成分估值无源，未自聚合')}"
            continue
        weights = weight_history(code)
        if weights is None:
            skipped[entry["key"]] = gap("§4", f"{code} 成分权重历史不可得")
            continue
        weights_by_key[entry["key"]] = weights
    series_by_key, aggregated = aggregate_all(weights_by_key), {}
    OUTDIR.mkdir(exist_ok=True)
    for entry in INDEX_POOL:
        key, code = entry["key"], entry.get("weight_code")
        if key in skipped:
            lines.append(f"\n[{entry['name']} {code}] {skipped[key]}")
        if key not in weights_by_key:
            continue
        series = series_by_key.get(key)
        if series is None or series["status"].eq("complete").sum() == 0:
            lines.append(f"\n[{entry['name']} {code}] {gap('§4', f'{code} 自聚合无完整月份')}")
            continue
        usable = series[series["status"] == "complete"].reset_index(drop=True)
        aggregated[key] = usable
        series.to_csv(OUTDIR / f"etf_valuation_{key}.csv", index=False)   # 规则验证(etf_backtest.py)读这一份
        lines += valuation_block(f"{entry['name']} {code} | 自聚合月频", usable[["trade_date", "pe_ttm", "pb"]].copy(), bonds)
        last = usable.iloc[-1]
        lines.append(f"  股息率(权重加权): 当前 {num(last['dividend_yield_pct'], suffix='%')} | 扩张窗分位 "
                     f"{percentile_cell(usable, 'dividend_yield_pct', None)} | 亏损股权重 {num(last['loss_weight_pct'])}% | "
                     f"个股估值覆盖 {num(last['coverage_pct'])}% | 不完整月份 {int((series['status'] != 'complete').sum())} 个")
    lines += pit_cross_check(weights_by_key.get("000300.SH"), aggregated.get("000300.SH"), lg.get("000300.SH"), basics.get("000300.SH"))
    lines += level_table(aggregated, lg, basics, levels)
    return lines


def total_cap_pe(weights, day):
    """现成源的口径：Σ成分总市值 ÷ Σ成分净利润(总市值÷pe_ttm，亏损股不计)。只在核对日取数。"""
    current = weights[weights["trade_date"] <= day]
    if current.empty:
        return None
    members = set(current.loc[current["trade_date"] == current["trade_date"].max(), "con_code"])
    df = cached_csv(f"daily_basic_mv_{day}.csv", f"daily_basic_mv:{day}",
                    lambda: api().daily_basic(trade_date=day, fields="ts_code,pe_ttm,total_mv"), immutable=day < CUTOFF)
    if df is None:
        return None
    df = df[df["ts_code"].isin(members)].assign(pe_ttm=lambda d: pd.to_numeric(d["pe_ttm"], errors="coerce"),
                                                 total_mv=lambda d: pd.to_numeric(d["total_mv"], errors="coerce"))
    profitable = df[df["pe_ttm"] > 0]
    earnings = (profitable["total_mv"] / profitable["pe_ttm"]).sum()
    return df["total_mv"].sum() / earnings if earnings > 0 else None


def pit_cross_check(weights, own, monthly, daily):
    """沪深300：用同一份成分与个股数据按现成源的口径（总市值加权）复算，能复现才说明原始数据与成分是当时口径。"""
    lines = ["\n  -- 4a 沪深300 数据核对：按现成源口径(总市值加权)复算 ÷ 现成源；各核对日 |偏差| ≤ 10% 视为原始数据与成分口径可用 --"]
    if weights is None or own is None:
        return lines + [f"  {gap('§4', '沪深300 未自聚合，数据核对未做')}"]
    rows, deviations = [], []
    for day in PIT_CHECK_DATES + (own["trade_date"].iloc[-1],):
        pick = lambda df: df[df["trade_date"] <= day].iloc[-1]["pe_ttm"] if df is not None and (df["trade_date"] <= day).any() else None
        replica, references = total_cap_pe(weights, day), (pick(monthly), pick(daily))
        ratios = [replica / reference if replica and pd.notna(reference) and reference > 0 else None for reference in references]
        deviations += [abs(ratio - 1) for ratio in ratios if ratio is not None]
        rows.append({"核对日": day, "总市值口径复算": num(replica), "乐咕": num(references[0]), "÷乐咕": num(ratios[0], 3),
                     "tushare": num(references[1]), "÷tushare": num(ratios[1], 3), "指数权重口径(本节)": num(pick(own))})
    lines.append(pd.DataFrame(rows).to_string(index=False))
    checked = sum(1 for row in rows if row["÷乐咕"] != "—" or row["÷tushare"] != "—")
    usable = bool(checked >= 3 and max(deviations) <= 0.10)   # numpy 标量进不了 json
    if checked < 3:
        lines.append(f"  判定: 可核对日 {checked} 个，不足 3 个 → {gap('§4', '沪深300 数据核对样本不足')}")
    else:
        lines.append(f"  判定: 可核对日 {checked} 个，最大偏差 {max(deviations) * 100:.1f}% → 原始数据与成分口径{'可用' if usable else '不可用'}")
    (OUTDIR / "etf_valuation_check.json").write_text(json.dumps(   # 预注册 §1 的前置条件，etf_backtest.py 据此决定 R1 出不出结论
        dict(as_of=AS_OF, cutoff=CUTOFF, checked_days=checked, max_deviation_pct=float(max(deviations)) * 100 if deviations else None,
             usable=usable, rows=rows), ensure_ascii=False, indent=1), encoding="utf-8")
    return lines


def level_table(aggregated, lg, basics, levels):
    """估值分位点 → 指数点位（盈利不变假设：点位 × 目标倍数 ÷ 当前倍数）。卡里仍须引用分位点与当前值经 calc 复算。"""
    lines = ["\n  -- 4b 估值分位点对应的指数点位（PE 扩张窗 P10/P25/P50/P75/P90；来源优先：自聚合 > 乐咕 > tushare） --"]
    rows = []
    for entry in INDEX_POOL:
        key = entry["key"]
        source, df = next(((label, table[key]) for label, table in (("自聚合", aggregated), ("乐咕", lg), ("tushare", basics))
                           if table.get(key) is not None), (None, None))
        level = levels.get(key)
        if df is None or level is None:
            continue
        quantiles = history_quantiles(pairs(df, "pe_ttm"))["levels"]
        priced = level[level["trade_date"] <= df["trade_date"].iloc[-1]]   # 点位取估值日当天：两者不同日则换算出的点位是错的
        current_pe = df["pe_ttm"].iloc[-1]
        if quantiles is None or pd.isna(current_pe) or priced.empty:
            continue
        current_level = priced["close"].iloc[-1]
        rows.append({"指数": entry["name"], "来源": source, "估值日": df["trade_date"].iloc[-1], "当前PE": num(current_pe),
                     "点位日": priced["trade_date"].iloc[-1], "当前点位": num(current_level),
                     **{f"P{p}": num(current_level * q / current_pe) for p, q in quantiles.items()}})
    return lines + ([pd.DataFrame(rows).to_string(index=False)] if rows else ["  （无可用估值序列）"])


# ============================ §5 工具池 ============================
def to_cny(level, currency, fx):
    """外币指数按外管局中间价折人民币；人民币原样；币种未知或无汇率返回 None。"""
    if currency == "CNY":
        return level
    if currency is None or fx is None:
        return None
    merged = asof_join(level, fx, [currency]).dropna(subset=[currency])
    return merged.assign(close=merged["close"] * merged[currency])[["trade_date", "close"]]


def tracking_cells(nav, entry, levels, fx, found_date):
    """基金复权净值对跟踪指数的 TD/TE（近 TRACKING_YEARS 年共同日期）。"""
    basis = "total_return" if entry.get("tr_code") else "price"
    level = levels.get(entry.get("tr_code") or entry["key"])
    if level is None:
        return f"TD/TE {gap('§5', entry['name'] + ' TD/TE: 指数行情不可得')}(指数行情不可得)"
    index_cny = to_cny(level, entry["currency"], fx)
    start = days_ago(int(TRACKING_YEARS * 365.25))
    kwargs = dict(fund_basis="adj_nav", index_basis=basis, fund_currency="CNY",
                  index_currency="CNY" if index_cny is not None else entry["currency"])
    index_series = pairs((index_cny if index_cny is not None else level).query("trade_date >= @start"), "close")
    fund_series = pairs(nav.query("trade_date >= @start"), "adj_nav")
    td = tracking_difference(fund_series, index_series, **kwargs)
    te = tracking_error(fund_series, index_series, **kwargs)
    if td["status"] != "complete":
        reasons = ",".join(td["missing_fields"]) + ("；" + entry["note"] if entry.get("note") else "")
        return f"TD/TE {gap('§5', entry['name'] + ' TD/TE: ' + reasons)}({reasons})"
    converted = "" if entry["currency"] == "CNY" else f"，{entry['currency']}按中间价折人民币"
    build_up = (td["window_start"] - datetime.strptime(found_date, "%Y%m%d").date()).days < 183
    return (f"TD 年化 {num(td['annual_td_pct'], suffix='pp')} / 区间 {num(td['period_td_pct'], suffix='pp')}；"
            f"TE 年化 {num(te['annual_te_pct'], suffix='%')} | 窗口 {iso(td['window_start'])}→{iso(td['window_end'])}"
            f" n={td['observations']} | 基准口径={basis}{converted}"
            + ("（指数不含分红，TD 含分红差）" if td["warnings"] else "")
            + (" ⚠窗口含成立后半年内的建仓期，TD/TE 失真" if build_up else ""))


def fee_cells(code, row):
    """tushare 管理/托管费 + 天天基金销售服务费；两源管理费不一致标存疑。"""
    fees = operating_fees(code.split(".")[0])
    sales = fees.get("销售服务费率")
    total = None if sales is None or pd.isna(row["m_fee"]) or pd.isna(row["c_fee"]) else row["m_fee"] + row["c_fee"] + sales
    text = (f"管理 {num(row['m_fee'])}% + 托管 {num(row['c_fee'])}% + 销售服务 "
            f"{num(sales, suffix='%') if sales is not None else gap('§5', code + ' 销售服务费')} = 年费合计 {num(total, suffix='%')}")
    if fees.get("管理费率") is not None and not pd.isna(row["m_fee"]) and abs(fees["管理费率"] - row["m_fee"]) > 1e-9:
        text += f" ⚠存疑: 天天基金管理费 {fees['管理费率']}% ≠ tushare {row['m_fee']}%"
    return text


def section_tools(universe, levels, fx):
    lines = ["\n---- §5 工具池 (持仓基金；场外基金按净值申赎、无溢价) ----"]
    if universe is None:
        return lines + [f"  {gap('§5', 'fund_basic 不可得，工具池整节缺失')}"]
    universe = universe.assign(stem=universe["name"].str.replace(r"-[A-Z]$", "", regex=True))
    index_by_key = {entry["key"]: entry for entry in INDEX_POOL}
    for code, expected_name, key in HOLDINGS:
        entry = index_by_key[key]
        match = universe[universe["ts_code"] == code]
        if match.empty or match.iloc[0]["name"] != expected_name:
            found = "无此代码" if match.empty else match.iloc[0]["name"]
            lines.append(f"\n[{code}] {gap('§5', f'{code} 名称核对失败: 期望 {expected_name}，fund_basic 为 {found}')}")
            continue
        row = match.iloc[0]
        lines.append(f"\n[{code}] {row['name']} | 跟踪 {entry['name']}({key}) | 成立 {row['found_date']} | "
                     f"状态 {row['status']} | {row['invest_type']}")
        lines.append(f"  费率: {fee_cells(code, row)}")
        lines.append(f"  赎回费: {redemption_ladder(code.split('.')[0]) or gap('§5', code + ' 赎回费阶梯')}")
        nav = fund_nav(code)
        if nav is None or nav.empty:
            lines.append(f"  净值: {gap('§5', code + ' 净值不可得')}")
            continue
        last = nav.iloc[-1]
        size = nav.dropna(subset=["net_asset"]).tail(1)
        size_text = (f"net_asset {num(size['net_asset'].iloc[0] / 1e8)} 亿 / total_netasset "
                     f"{num(size['total_netasset'].iloc[0] / 1e8)} 亿 @{size['trade_date'].iloc[0]}"
                     "（tushare 原字段；A/C 两类 net_asset 同值，是否分份额口径未核）") if not size.empty else gap("§5", code + " 规模")
        lines.append(f"  净值: {num(last['unit_nav'], 4)} @{last['trade_date']} | 复权净值 {num(last['adj_nav'], 4)} | 规模 {size_text}")
        lines.append(f"  {tracking_cells(nav, entry, levels, fx, row['found_date'])}")
        siblings = universe[(universe["stem"] == row["stem"]) & (universe["ts_code"] != code) & (universe["status"] == "L")]
        for _, sibling in siblings.iterrows():
            lines.append(f"  同基金其他份额 {sibling['ts_code']} {sibling['name']}: {fee_cells(sibling['ts_code'], sibling)}")
    code, name, key = HK_ETF
    price = fetch(f"ak.stock_hk_daily:{code}", lambda: ak.stock_hk_daily(symbol=code, adjust=""), pause=0)
    lines.append(f"\n[{code}.HK] {name} | 跟踪 {index_by_key[key]['name']} | 盈立证券直持 | 费率/净值 {MARK}")
    if price is not None:
        price = price.assign(trade_date=pd.to_datetime(price["date"]).dt.strftime("%Y%m%d")).query("trade_date <= @CUTOFF")
        lines.append(f"  收盘价: {num(price['close'].iloc[-1])} HKD @{price['trade_date'].iloc[-1]} (新浪港股日线，未复权)")
    else:
        lines.append(f"  收盘价: {gap('§5', '02800 行情不可得')}")
    return lines


# ============================ §6 趋势 ============================
def section_trend(levels):
    lines = ["\n---- §6 趋势 (200日均线用日收盘；10月均线只用已完成月的月末收盘，当月未完成不参与) ----"]
    rows = []
    for entry in INDEX_POOL:
        level = levels.get(entry["key"])
        if level is None:
            rows.append(dict(指数=entry["name"], 备注=gap("§6", f"{entry['name']} 行情不可得")))
            continue
        closes = level["close"].tolist()
        day200 = sma_state(closes, 200)
        last_day = level["trade_date"].iloc[-1]   # 以序列自身的最新月为"未完成月"：数据滞后时不把半个月当月末
        months = [value for day, value in month_end_levels(pairs(level, "close"))
                  if (day.year, day.month) < (int(last_day[:4]), int(last_day[4:6]))]
        month10 = sma_state(months, 10)
        now_vs_month10 = None if month10["sma"] is None else (closes[-1] / month10["sma"] - 1) * 100
        rows.append({"指数": entry["name"], "代码": entry["code"], "最新日": level["trade_date"].iloc[-1],
                     "收盘": num(closes[-1]), "200日线": num(day200["sma"]), "距200日线%": num(day200["distance_pct"]),
                     "200日状态": day200["state"] or "—", "10月线": num(month10["sma"]),
                     "上月末距10月线%": num(month10["distance_pct"]), "上月末状态": month10["state"] or "—",
                     "最新收盘距10月线%": num(now_vs_month10), "备注": "；".join(day200["missing_fields"] + month10["missing_fields"])})
    return lines + [pd.DataFrame(rows).fillna("").to_string(index=False)]


# ============================ §7 宏观代理 ============================
def section_macro(bonds, fx, levels):
    lines = ["\n---- §7 宏观代理 ----"]
    if bonds is not None:
        for label, column in (("中国10年国债(中债曲线)", "cn10y"), ("美国10年国债", "us10y")):
            series = bonds.dropna(subset=[column])
            lines.append(f"  {label}: {num(series[column].iloc[-1], 4, '%')} @{series['trade_date'].iloc[-1]}" if not series.empty
                         else f"  {label}: {gap('§7', label + ' 不可得')}")
    else:
        lines.append(f"  国债收益率: {gap('§7', '中美10年国债收益率不可得')}")
    if fx is not None:
        last = fx.iloc[-1]
        lines.append(f"  人民币中间价: USD {num(last['USD'], 4)} / HKD {num(last['HKD'], 5)} @{last['trade_date']}")
    else:
        lines.append(f"  汇率: {gap('§7', '外管局中间价不可得')}")
    gold = levels.get("Au99.99")
    lines.append(f"  Au99.99 收盘: {num(gold['close'].iloc[-1])} 元/克 @{gold['trade_date'].iloc[-1]}" if gold is not None
                 else f"  金价: {gap('§7', 'Au99.99 不可得')}")
    return lines


# ============================ 主流程 ============================
def tee_output(path):
    """stdout 同时写入快照文件，末行“快照完成”才算完整。stderr 不入快照：akshare 的进度条走 stderr。"""
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
    original = sys.stdout
    sys.stdout = _Tee(original, sink)

    def restore():
        sys.stdout = original
        sink.close()
    return restore


def _valid_date(text):
    try:
        datetime.strptime(text, "%Y%m%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"日期需为 YYYYMMDD 格式: {text!r}")
    return text


def run(snapshot, pool_csv):
    global CUTOFF
    CUTOFF = min(AS_OF, completed_day_cutoff())
    requests.Session.request = _request_with_timeout   # 只在实跑时生效，import 本模块不改全局行为
    print(f"== ETF 框架 {FRAMEWORK_VERSION} 数据快照 | 脚本 etf_data {SCRIPT_VERSION} | AS_OF={AS_OF} | "
          f"指数池 {len(INDEX_POOL)} | 持仓工具 {len(HOLDINGS) + 1} ==")
    print(f"日线上界={CUTOFF}（北京时间18:00前保守排除当天；各序列实际最新日逐项显示）")

    bonds, fx = bond_yields(), fx_rates()
    history_start = days_ago(int((TRACKING_YEARS + 1) * 365.25))
    levels, lg, basics = {}, {}, {}
    for entry in INDEX_POOL:
        if entry.get("lg_symbol"):
            lg[entry["key"]] = lg_valuation(entry["lg_symbol"])
        if entry.get("valuation_code"):
            basics[entry["key"]] = valuation_history(entry["valuation_code"])
        if entry["source"]:
            basic = basics.get(entry["key"])    # §2 日频分解需要与估值同长的点位史
            start = history_start if basic is None else min(history_start, basic["trade_date"].iloc[0])
            levels[entry["key"]] = daily_levels(entry["code"], entry["source"], start)
        if entry.get("tr_code"):
            levels[entry["tr_code"]] = daily_levels(entry["tr_code"], "index_daily", history_start)

    body = section_valuation(bonds, lg, basics)
    body += section_decomposition(lg, basics, levels)
    body += section_structure(load_pool_codes(pool_csv) if pool_csv else None)
    body += section_aggregation(bonds, lg, basics, levels)
    body += section_tools(fund_universe(), levels, fx)
    body += section_trend(levels)
    body += section_macro(bonds, fx, levels)
    body += ["\n---- §8 记分结算: 随决策卡上线，本版不做 ----"]

    failed = {label: status for label, status in INTERFACES.items() if status != "通"}
    print(f"\n---- §0 自检 ----\n  接口: 通 {len(INTERFACES) - len(failed)} 项 / 异常 {len(failed)} 项")
    for label, status in failed.items():
        print(f"    ✗ {label}: {status}")
    print(f"  缺口清单 {MARK}（固定 {len(STATIC_GAPS)} 项 + 本次运行 {len(GAPS)} 项）:")
    for item in STATIC_GAPS + GAPS:
        print(f"    - {item}")
    print("\n".join(body))
    print(f"\n完成。快照={snapshot or '未写(--no-snapshot)'}")
    print(f"== 快照完成 | AS_OF={AS_OF} | 脚本 etf_data {SCRIPT_VERSION} | 本行存在即输出完整 ==")


def main():
    global AS_OF
    parser = argparse.ArgumentParser(description=f"ETF 轨道数据快照 (etf_data {SCRIPT_VERSION})")
    parser.add_argument("--as-of", type=_valid_date, default=AS_OF, metavar="YYYYMMDD",
                        help="基准日 (缺省=运行当天, 当前默认 %(default)s)")
    parser.add_argument("--no-snapshot", action="store_true", help="只打印，不写 research/etf-<AS_OF>-data-snapshot.txt")
    parser.add_argument("--pool-csv", metavar="PATH", help="ai_investment 的 investment_prediction.csv，用于 §3 研究覆盖率")
    parser.add_argument("--overwrite", action="store_true", help="覆盖同一 AS_OF 的已有快照（引用它的决策卡须重新校验）")
    args = parser.parse_args()
    AS_OF = args.as_of
    snapshot = None if args.no_snapshot else RESEARCH_DIR / f"etf-{AS_OF[:4]}-{AS_OF[4:6]}-{AS_OF[6:]}-data-snapshot.txt"
    if snapshot is None:
        return run(None, args.pool_csv)
    if snapshot.exists() and not args.overwrite:
        sys.exit(f"{snapshot} 已存在；决策卡按章节引用其中的数字，重跑会改数。确需覆盖请加 --overwrite")
    partial = snapshot.with_name(snapshot.name + ".partial")   # 跑完整才替换正式文件，中途失败不毁掉旧快照
    restore = tee_output(partial)
    try:
        run(snapshot, args.pool_csv)
    finally:
        restore()
    partial.replace(snapshot)


if __name__ == "__main__":
    main()
