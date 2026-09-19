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
  §4 指数口径基本面：第二期，本版不做
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
乐咕乐股月频 PE 与 tushare index_dailybasic 日频 PE 算法不同(同日 12.68 vs 13.43)，不可混用；
两者是否 point-in-time 未验证，作回测输入前须按任务说明 §5 抽 5 个历史日期自算核对。
akshare 费率来自天天基金页面，未与基金公告逐只核对。
"""

import argparse
import csv
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

try:
    from .etf_calc import (erp_spread, expanding_percentile, history_quantiles, month_end_levels,
                           return_decomposition, sma_state, tracking_difference, tracking_error)
    from .price_evidence import completed_day_cutoff
except ImportError:  # direct script invocation
    from etf_calc import (erp_spread, expanding_percentile, history_quantiles, month_end_levels,
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
TRACKING_YEARS = 3
MARK = "[需人工补充]"

# 指数池（第 0 天按实际持仓 + 分散器候选）。source=tushare 接口名；None=无现成源。
# tr_code=全收益指数；weight_code=index_weight 代码；valuation_code=index_dailybasic 代码；
# currency=None 表示指数币种未核，凡需同币种比较的计算一律落缺口。
INDEX_POOL = [
    dict(key="000300.SH", name="沪深300(估值锚)", source="index_daily", code="000300.SH", tr_code="H00300.CSI",
         weight_code="000300.SH", valuation_code="000300.SH", lg_symbol="沪深300", currency="CNY",
         decomposition_anchors=[("自2007-10-31估值高点", "20071031")]),
    dict(key="000510.SH", name="中证A500", source="index_daily", code="000510.SH", tr_code="000510CNY010.CSI",
         weight_code="000510.SH", currency="CNY"),
    dict(key="HKTECH", name="恒生科技", source="index_global", code="HKTECH", currency="HKD"),
    dict(key="HSI", name="恒生指数", source="index_global", code="HSI", currency="HKD"),
    dict(key="HSHYLV", name="恒生港股通红利低波动", source=None, code=None, currency="HKD"),
    dict(key="399973.SZ", name="中证国防", source="index_daily", code="399973.SZ", tr_code="H20321.CSI",
         weight_code="399973.SZ", currency="CNY"),
    dict(key="987018.CNI", name="国证港股通创新药", source="index_daily", code="987018.CNI",
         weight_code="987018.CNI", currency=None,
         note="指数币种未核；2026-09-19 试算折不折汇率 TE 都约 9%，tushare 该序列与基金净值疑似口径或日期不匹配"),
    dict(key="931787.CSI", name="中证香港创新药", source="index_daily", code="931787.CSI",
         weight_code="931787.CSI", currency="HKD"),
    dict(key="931152.CSI", name="中证创新药产业", source="index_daily", code="931152.CSI", tr_code="H21152.CSI",
         weight_code="931152.CSI", currency="CNY"),
    dict(key="399989.SZ", name="中证医疗", source="index_daily", code="399989.SZ", tr_code="H20451.CSI",
         weight_code="399989.SZ", currency="CNY"),
    dict(key="000688.SH", name="科创50", source="index_daily", code="000688.SH", tr_code="000688CNY01.CSI",
         weight_code="000688.SH", valuation_code="000688.SH", currency="CNY"),
    dict(key="000819.SH", name="中证申万有色金属", source="index_daily", code="000819.SH", tr_code="H00819.CSI",
         weight_code="000819.SH", currency="CNY"),
    dict(key="000813.CSI", name="中证细分化工", source="index_daily", code="000813.CSI", tr_code="H00813.CSI",
         weight_code="000813.CSI", currency="CNY"),
    dict(key="Au99.99", name="黄金现货Au99.99", source="sge_daily", code="Au99.99", currency="CNY"),
    dict(key="000012.SH", name="上证国债指数", source="index_daily", code="000012.SH", currency="CNY"),
    dict(key="SPX", name="标普500", source="index_global", code="SPX", currency="USD"),
]

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
    "§1 港股指数(恒生科技/恒指/港股通红利低波/两只港股创新药)与多数行业指数的估值无现成源；指数口径自聚合属 §4 第二期",
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


def valuation_history(code):
    """index_dailybasic 单次上限 3000 行：按日期向前翻页取全。"""
    frames, end, label = [], CUTOFF, f"index_dailybasic:{code}"
    while True:
        df = fetch(label, lambda: api().index_dailybasic(ts_code=code, end_date=end, fields="ts_code,trade_date,pe_ttm,pb"))
        if df is None or df["trade_date"].max() > end:   # 后者=接口忽略了 end_date，再翻页只会死循环
            break
        frames.append(df)
        end = (datetime.strptime(df["trade_date"].min(), "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    if not frames:
        return None
    if INTERFACES[label].startswith("失败"):   # 后续页失败：保留失败状态，分位将基于截断的历史
        gap("§1", f"{code} 估值历史翻页中断于 {end}，分位与分位点基于截断样本")
    else:
        INTERFACES[label] = "通"          # 翻到空页是正常终点
    return pd.concat(frames).drop_duplicates("trade_date").sort_values("trade_date").reset_index(drop=True)


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
    df = fetch("ak.bond_zh_us_rate", lambda: ak.bond_zh_us_rate(start_date="20050101"), pause=0)
    if df is None:
        return None
    df = df.rename(columns={"日期": "trade_date", "中国国债收益率10年": "cn10y", "美国国债收益率10年": "us10y"})
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
    return df[df["trade_date"] <= CUTOFF][["trade_date", "cn10y", "us10y"]].sort_values("trade_date").reset_index(drop=True)


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
        df = asof_join(df, bonds, ["cn10y"])
        df["erp"] = [erp_spread(pe, y) for pe, y in zip(df["pe_ttm"], df["cn10y"])]
    else:
        df["cn10y"] = df["erp"] = None
        gap("§1", f"{title}: 10年国债收益率不可得 → 股债利差不可算")
    last = df.iloc[-1]
    rows = [("PE_TTM (分位高=贵)", "pe_ttm", num(last["pe_ttm"])), ("PB (分位高=贵)", "pb", num(last["pb"])),
            ("股债利差 100/PE−10年国债 (分位高=便宜)", "erp", num(last["erp"], suffix="pp"))]
    for label, column, current in rows:
        lines.append(f"  {label}: 当前 {current} | 扩张窗分位 {percentile_cell(df, column, None)}"
                     f" | 10年窗分位 {percentile_cell(df, column, 10)}")
        levels = history_quantiles(pairs(df, column))["levels"]
        if levels is not None:   # 情景的期末倍数只能取自这里，不由 AI 估
            lines.append("    历史分位点(扩张窗): " + " / ".join(f"P{point} {level:.2f}" for point, level in levels.items()))
    lines.append(f"  10年国债(估值日或之前最近一期): {num(last['cn10y'], 4, '%')}")
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
        for label, column in (("中国10年国债", "cn10y"), ("美国10年国债", "us10y")):
            series = bonds.dropna(subset=[column])
            lines.append(f"  {label}: {num(series[column].iloc[-1], 4, '%')} @{series['trade_date'].iloc[-1]}")
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
    body += ["\n---- §4 指数口径基本面: 第二期，本版不做 ----"]
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
