# -*- coding: utf-8 -*-
"""
v2.20 框架数据脚本 — Tushare Pro 版 (v1.8)
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
  §3/§4 股指年化贴水 / 国债30Y-10Y利差 → ★v1.8 已删除: IM/IC、TL/T 退出执行池(框架 v2.20 周度扫描),
                           复活时从 git v1.7 取回代码与配置(输入C/④/D15 与曲线补全门随之停用)

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

v1.5 → v1.6 变更 (对应框架 v2.10→v2.11; 注: v2.10 框架更新(2026-07-15)无脚本侧
                  结构性数据需求, 脚本版本未随动, 属预期而非遗漏):
  ★LC候选块接入(v2.11 CONTRACTS 新增·广期所碳酸锂, 供需拐点单链条·不借道G池):
     LC月差 = LC2609-LC2611 (GFEX, 主力-次主力按 2026-07 活跃月估定,
        【激活前必核】实际主力/次主力与 fut_basic 代码样式);
     kind="候选A"(照打 ≥70/≥85 触发标签 + 补全门注记) —— 框架 v2.11 LC卡触发
        ="期现/月差结构分位沿A式", 月差分位为合法触发输入之一; 但激活仍需
        库存/检修人工双验证(周度社会库存与去化幅度、检修产能追踪=人工项,
        SMM等口径), 补全门未过不建仓, 首期系数0.5;
     EXCH 增 LC→GFEX; INDICATOR_CONTRACTS 增 LC2609(0.2可交易性+激活前置核对;
        限仓/保证金核联动广期所 SI/PS: ×0.8+限仓过滤)。
  ★§0b EVENTS 日历随 v2.11 1.4 换版: 新增 7/20-7/22 长鑫缴款·权益资金面验证窗
     (②'; IM/IC 多头新开冻结 0.3#28)、8/9 LC检修窗口复核点; FOMC 备注改
     D13复活口径(常态×0.5恢复+T-1对冲); 政治局改 7/30 已明确日期; 过期节点
     (7/13-17数据窗、7/17美伊节点)保留在表中仅作留痕, 未来10日清单自然不显示。
  ★锚点簿记: 框架 v2.11 的 precheck 编号已改(①尾部监控门/②'资金面企稳门/
     ②''FOMC·政治局双锚/③/④), D13=复活态; 本脚本注释中未逐处重写的 v2.9 编号
     锚点, 其机制(输入A/B/C、D12判据、0.3#25、④量化门槛)在 v2.11 中未变,
     引用继续有效; 资金面三指标(两融/成交额/跌停家数)为 v2.11 新增**人工输入项**
     (框架 1.1 明示), 按适用边界不脚本化。

v1.6 → v1.7 变更 (对应框架 v2.17→v2.18「合约滚动换代」; 主体是配置区合约腿全表换代
                  + 维护规程重写, 另含换月过程中暴露的两处口径 BUG 修正):
  ★全表换月: 2609/2610 系近腿已全线触及否决#1(距最后交易日<20交易日), 按 2026-08-28
     收盘实测(fut_mapping 主力 + fut_basic 到期日 + 近20交易日均量/持仓)整表回填:
       SPREAD_PAIRS  MA2609-2701→MA2610-2701 | CU2609-2611/2701→CU2610-2611/2701 |
                     SR2609-2701→SR2701-2705 | AL2609-2611→AL2610-2611 |
                     JM2609-2701→JM2701-2705 | J2609-2701→J2701-2705 |
                     RB2610-2701 维持 | IM/IC-roll 2609-2612→2612-2703 |
                     黑色J-RB J2609-RB2610→J2701-RB2701(同月对齐) |
                     国债TL-T 2609→TL2612-T2612 | SC近端 2609-2610→SC2610-2611 |
                     PS 2609-2611→PS2611-2612 | LH 2609-2701→LH2611-2701 |
                     LC 2609-2611→LC2611-2701
       INDICATOR_CONTRACTS 全表同步; BASIS_CONTRACTS IM/IC2609→IM/IC2612(§3口径变更, 见下);
       CURVE_FUT_LEGS TL2609/T2609→TL2612/T2612
  ★§3 口径变更(唯一一处非机械换月的改动): 股指年化贴水的计算腿由「近月主力」改为
     「远季carry腿」—— IM2609/IC2609 剩 15 交易日触否决#1, 而次月腿 IM2610(7,498手)/
     IC2610(5,328手)触否决#2, 框架合规的可持有腿只剩 2612。年化贴水水平因此系统性低于
     近月口径(近月临交割会放大年化值, 见注2), **④门读数不可与换月前序列直接比较**;
     框架 v2.18 1.7④行已同步写入该口径注记。
  ★三处"结构性例外"显式化(写进维护注, 防下次换月被"修正"回主力):
     IM/IC 主力恒为近月直到交割(换月中位剩余交易日=0)且次月腿不过#2 → 指标/贴水/roll
       腿一律用季月, 不用主力; SC 主力存续期≈1个月(换月中位剩余9交易日), 近腿几乎恒在
       #1线附近 → 月差按"主力-次月"读结构(不建仓, 不受#1约束); J 除主力外无第二个上万手
       月份(J2705 仅 325 手) → J 月差对仅采集不执行, 双焦执行腿唯一=JM。
  ★维护规程重写: 原「候选块维护注」中 SC 专属的"<25交易日"阈值删除(对 SC 恒成立,
     换月刚落地即再次触发, 属无效阈值), 统一为「近腿触#1线 或 fut_mapping 主力换月,
     先到为准 → 整对下滚; 目标腿须同时过#2, 过不了退到最近一个能过的月份并在框架 0.2
     表标注降级」; 各品种主力月阶梯与下一次触发日见框架 v2.18「合约滚动阶梯」表。
  ★BUG 修正(一)·合约解析主键: _match_rows 的定位主键由
     「delist_date 年月 == 合约交割年月」改为「ts_code 全等」。INE 原油 SC 的最后
     交易日在**交割月前一月**(SC2610 → 20260930), 旧主键使 resolve("SC2609") 实际
     取到 SC2610、resolve("SC2610") 取到 SC2611 —— 20 个配置品种中仅 SC 命中该错位
     (fut_basic 全表核验: SC 的 27 个在挂合约全错位, 其余 19 品种零错位)。错位被
     年份平移腿同步抵消, 故历史分位数值自洽, 但**合约标签、§0 距到期、§2 单合约
     指标全部张冠李戴**, 且 §0 从未对真正的 SC2609(8/31 到期)报过警。
  ★BUG 修正(二)·交易日口径: _busdays 由「工作日近似」改为 trade_cal 真实交易日
     (已剔节假日), §3 年化贴水的分母同步改用同一份日历(向量化 searchsorted)。
     2026 国庆当口实测差 6 个交易日(CU/AL/RB/AU/AG 的 2610 腿: 近似33 vs 真实27) ——
     旧口径会把否决#1(<20交易日)的 §0 预警从 9/10 推迟到 9/18, 而这段正是该批合约的
     换月窗口; trade_cal 失败自动退回原近似(§0/§0b/§2b/§3 四处调用点口径统一)。
  ★配套护栏(对抗审查后补): (a) 合约解析**不再**保留「交割年月」退化兜底 —— 该分支会
     在合约根本不存在时命中邻月(实测 SC2710/SC2711 未挂牌, resolve("SC2711") 会返回
     SC2712), 等于复活本次要修的错位; 现在一律抛 ValueError。(b) trade_cal 只发布到
     **次年年底**(请求 20280830 实测只返回到 20271231, 静默截断) → 新增 _cal_covers
     覆盖守卫, 盖不到目标日就退回 busday 而不是静默少算(否则 §3 分母变小会把年化贴水
     成倍放大, 有让 ④ 假过门的风险)。(c) 任何一次降级都会在 §0 与注2 显式打印原因,
     兑现注2「取数失败才退回近似并在此注明」的承诺。(d) end_date 改用 shift_year_date
     以处理 2/29。
  ★除上述两处 BUG 外, 取数/计算逻辑零改动: §0/§0b/§1/§2/§2a-2c/§4 的算法函数未动;
     EVENTS 事件日历本次未随动(仍是 v2.16 口径, 属另一条用户维护项, 与换月无关)。

v1.7 → v1.8 变更 (对应框架 v2.19→v2.20「选品重构」; 主体是配置区随执行池收缩 + §2b 两列新增
                  + §3/§4 休眠守卫; 取数/计算算法零改动):
  ★配置区收缩(框架 v2.20 0) CONTRACTS 分层: 核心 MA/JM/RB + 备选 M + 信号席 AU/SC + 周度扫描):
     SPREAD_PAIRS 16 组 → 5 组: MA2610-MA2701(A) | JM2701-JM2705(A) | RB2610-RB2701(A, 9/10→RB2701-RB2703)
                              | 黑色JM-RB JM2701-RB2701(结构监控, 原 J2701-RB2701 的 J 腿随 J 退出改 JM)
                              | SC近端 SC2610-SC2611(kind="信号": 不打候选块建仓注记, 仅①back方向/护栏口径)
       停采: CU 两对存档(空仓无存量)、SR、AL、J、IM/IC-roll、TL-T、PS、LH、LC —— 复活时按原行加回,
             同期分位从零重建(历史平移腿由脚本自动跟随)。
     INDICATOR_CONTRACTS 20 腿 → 7 腿: MA2610(主力·护栏腿) MA2701(执行腿) JM2701 RB2701 M2701
                                    AU2612(信号) SC2610(信号·护栏口径腿)。
     BASIS_CONTRACTS / CURVE_FUT_LEGS 配置随 §3/§4 删除(IM/IC、TL/T 退出执行池; 见下条)。
  ★§2b 新增两列(框架 v2.20 输入A 扩展):
     「周涨%」= px(结算价) 对 5 个交易日前的涨跌幅 —— 框架 1.5 MA 卡「原油周涨幅」护栏(>5%/>8%)的
       口径腿=SC2610(随主力换月), 周五 AS_OF 即「周五对上周五」; 布伦特多源口径降为旁证。
     「一手风险2ATR」「手数」= 2×ATR20×multiplier + 2×tick_value 与 floor(RISK_BUDGET/风险) ——
       框架 0.3#31 一手风险门(2026-09-04 实测: AU 42,117/SC 57,253/IM 77,696 ≈ 净值 28%/38%/52%,
       均 0 手; JM 6,569 临界 0 手; MA 1,682→3 手, RB 656→8 手, M 993→5 手)。
       手数<1 → 「否决检查」列加印「一手风险>预算⚠(#31)」; 品种不在 CONTRACT_SPEC → 加印「合约参数缺⚠」。
     新增配置 RISK_BUDGET(=框架 0) RISK_BUDGET 5,250)与 CONTRACT_SPEC(=框架 Step5 合约参数表, 两处同源)。
  ★§3/§4 删除(奥卡姆: 不留"以后可能用到"的兼容分支): stock_index_basis / bond_curve_30_10 / dv01_ratio_hint /
     _curve_frame_* / yc_term_series / index_spot 与 SPOT_INDEX / BASIS_* / CONV_MIN_PP / YC_* / CURVE_* /
     DV01_REG_WIN 配置, spread_percentile 的 候选A/候选代理/存档/H-roll/国债期货价差 五个死分支, 池内 ATR 极差
     的「剔除挂起腿」副行, 一并删除; 复活时从 git v1.7 取回。
  ★周涨% 口径(二稿修正): 基准=AS_OF 前 7 个日历日内最近一个交易日的结算价(周五 AS_OF 即周五对上周五;
     跨国庆/中秋等休市周同口径), 不再用「5 个交易日前」—— 后者在假期周会把跨假累计涨幅当一周涨幅喂给护栏。
  ★#31 高波层(二稿修正): ATR250 分位>80 的腿按框架 0.3#31 「final_lots=floor(lots×0.5) 后仍须≥1手」——
     「手数」列=×0.5 后的有效手数(高波层)或原手数(其余层), <1 手打「高波层×0.5后<1手⚠(#31)」。
  ★信号腿豁免(二稿修正): SIGNAL_LEGS={AU2612, SC2610} 与 kind="信号" 的价差对不打 #1/#2 否决(框架 0)注c
     「信号席不建仓, 不受#1#2」), §0 改打 ℹ 提示行(SC 随主力换月滚), §2b/§1 否决列改「信号腿·不受#1/#2」。
  ★启动参数校验 spec_check()(二稿新增, 宁抛错不猜): CONTRACT_SPEC 未覆盖池内任一品种 → sys.exit;
     multiplier 与 tushare fut_basic.per_unit(实测 MA 10/JM 60/M 10/RB 10/AU 1000/SC 1000; multiplier 字段
     为 None 不可用)不一致 → sys.exit; per_unit 缺失 → 仅 ⚠。
  ★§1 每组价差加印: 两腿距最后交易日 + 价差腿一手风险(|当前价差-50分位锚|×multiplier+4×tick_value, 0.3#31)
     与手数 —— 框架 0)/0.2 表结构腿的 #31 数值自此由脚本给出, A 对 #31 未过时不打入场标签。
  ★EVENTS 仍为用户维护项(本版未随框架 v2.19 1.4 刷新: 9/10 PPI、9/11 CPI 未登记, 非农已过期),
     受影响品种元组里的池外品种(IM/IC/CU/AL/AG)无指标腿, T-3 打标对其无效, 属预期。

合约滚动(换月)维护注  ★v1.7 重写:
  - 统一滚动判据(不再给单品种设特例阈值): 近腿触及否决#1线(距最后交易日<20交易日)
    或 fut_mapping 主力换月, **先到为准** → 整对下滚; 目标腿必须同时过否决#2
    (20日均量≥1万手), 过不了就退到最近一个能过的月份, 并在框架 0.2 表标注降级。
    各品种主力月阶梯(实测)与下一次触发日: 见框架 v2.18「合约滚动阶梯」表。
    换月后价差同期分位/涨幅分位序列全部作废重建(历史平移腿由脚本自动跟随),
    重建完成前框架侧对应结构腿新开从严。
  - 结构性例外(是结论不是疏漏, 下次换月勿"修正"回主力):
    IM/IC —— 市场换月中位剩余交易日=0(主力恒为近月直到交割), 且次月腿过不了#2
      (IM2610 7,498手/IC2610 5,328手) → 指标腿/§3贴水腿/H-roll 对一律用远季月(2612/2703)。
    SC   —— 主力存续期≈1个月(换月中位剩余9交易日), 近腿几乎恒在#1线附近; 月差序列按
      "主力-次月"读近端结构(候选块不建仓, 不受#1约束), ①门过要进执行层时建仓腿另按#1选。
    J    —— 除主力外无第二个上万手月份(J2705 仅325手/J2610 709手) → J 月差对保留仅作采集,
      双焦月差的执行腿唯一=JM。
  - PS/LH 期现升水本体 = 人工输入项(SMM 多晶硅现货 / 生猪现货与出栏节奏);
    本脚本月差代理仅供结构参考, 补全门核对以期现口径为准(1.5 品种卡)。
  - 交易所风控现值(0.2表, 人工核对): SC 处 INE 风控升级期(2026-06 公告:
    涨跌停14%、保证金16-24%区间; 2026-04 曾单日-13%, gap 纪律从严);
    PS 类比 SI 广期所限仓过滤+保证金×0.8 沿用至公告明确退出。
  - LC【激活前必核】广期所现行合约文本(交易单位1吨/手、tick 50元/吨 待核)、
    保证金/限仓现值; 期现基差与社会库存/检修追踪=人工。

适用边界 (对齐 v2.11 的 1.1 人工输入项):
  - 本脚本覆盖: 输入A(★v1.8 含周涨%与一手风险/手数=否决#31数据)/输入B(池内 5 组序列:
    MA/JM/RB 月差 + JM-RB 价差 + SC 近端信号, 每组含价差腿一手风险与两腿剩余td) + 否决#1#2数据
    + 事件T-3判据 + ATR分层/极差 + ATR重校准核验 + 启动参数校验; 输入C(§3 股指贴水)与 §4 曲线利差
    随 IM/IC、TL/T 退出执行池**已删除**(复活时从 git v1.7 取回)。
  - 仍需手动/另接数据源: precheck①的现货/仓单追认代理与事件链进展、
    ②'权益资金面三指标(两融余额/全A成交额/跌停家数, v2.11新增人工项)与②''窗口判定、
    ③产能性判决硬数据(铁水/社库/盈利率/能繁/调减进度)、PS/LH期现升水与SMM现货、
    LC期现基差与社会库存/检修追踪(★v1.6, SMM等口径)、
    板块分化代理(AI链vs地产链)、D9宏观序列、商品现货基差/库存/开工、
    保证金与限仓现值(交易所公告)、单周涨跌3年分位(D8, v1.7候选)、
    gap_ratio(定义悬空: 框架0.3#7引用但1.1未列, 待框架侧补列或给定义后脚本化)。
  - H250/dist/H20 等为单合约自身历史: 样本<250日时 H250 实为上市以来高点,
    D11 口径偏松(看§2「分位样本N」列), 主力连续拼接版(fut_mapping)列后续候选。
  - ★v1.7: 合约腿本身(SPREAD_PAIRS/INDICATOR_CONTRACTS/SIGNAL_LEGS; ★v1.8 起 BASIS_CONTRACTS/
    CURVE_FUT_LEGS 已删除)是**配置区用户维护项**, 不自动跟随主力换月; 脚本只负责在 §0
    用真实交易日预警陈旧腿。滚动判据与各品种主力月阶梯见上文「合约滚动(换月)维护注」
    与框架 v2.18「合约滚动阶梯」表。

使用方法
  pip install tushare pandas numpy
  设置环境变量 TUSHARE_TOKEN (或在配置区直接填 TOKEN)
  python scripts/future_data.py [--as-of YYYYMMDD]   （已从 ai_investment 仓库迁移至此，随框架同仓维护）
  把控制台输出整体贴回对话, 或上传 ./output/*.csv

权限说明
  fut_basic / fut_daily 需 Tushare Pro 期货档积分(通常2000分)。

诚实声明
  本脚本未经线上实测(沙箱无法访问 api.tushare.pro / 东财数据中心); 以下纯计算
  路径已用合成数据离线自测: 候选代理轴反转(升水分位=价差取负后重算, 非100-x
  近似)、样本充足性警告、事件窗口标记(T-3/±1/进行中)、ATR重校准比值与跨层、
  存档/候选标签分支、ATR分层与池内极差; akshare bond_zh_us_rate 列名已经
  v1.18.64 源码核验。★v1.6 新增的 LC 取数路径同样未经线上实测(本环境无法访问
  tushare/akshare 实网), 且未做合成数据自测(复用既有 kind="候选A" 分支, 无新
  计算逻辑, 仅新增配置行)。接口字段与权限仍请按实际环境核对, 尤其: SC/PS/LH/LC
  在 fut_basic 的代码样式与历史平移腿存在性(PS 仅 25xx 一代; LC 上市于
  2023-07-21, 3年对照样本临界, 样本充足性警告可能触发)、yc_cb 参数、
  CFFEX 代码后缀。任何报错原样贴回, 我来修。
  ★v1.7 更新(本版是第一次**真正线上跑通**的版本, 上面几段"未经线上实测"的历史声明
  自本版起对以下范围失效): 2026-08-30 以真实 TUSHARE_TOKEN 对 api.tushare.pro 完整
  跑通 §0/§0b/§1/§2a-2c/§3/§4: 34 个配置合约腿全部解析成功、§0 自检"全部通过"、
  16 组价差的三年同期平移腿除 PS/LC 上市前年份的固有缺口(已由样本充足性⚠显式标注)
  外全部命中(n=40~41)、§3 两只股指贴水与 ④ 判定、§4 利差分位与 DV01 回归均正常输出;
  换月后的 SC/PS/LH/LC 取数路径(v1.5/v1.6 遗留的"未实测"项)本次一并实测通过。
  (§3/§4 已于 v1.8 删除, 其实测记录随代码一并留在 git v1.7。)
  §2c ATR 重校准仍无实数据可测(当前空仓, POSITIONS 为空)。
  ★v1.8 更新: 2026-09-06 以真实 TUSHARE_TOKEN 按 --as-of 20260904 完整跑通收缩后的配置
  (§0 自检+spec_check 参数校验 / §0b / §1 5 组含价差腿一手风险 / §2a-2c 含新列); 一手风险与周涨%
  的数值与框架 v2.20 0)/0.2 表回填值同源(框架表按本脚本输出回填)。§2c 仍空仓无实测。
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
OUTDIR = "./output"

# ---- §0b 事件日历 (v2.9 0.0b / 1.4 事件轴; ★用户维护, 脚本只打印) ----
# 条目: (起始YYYYMMDD, 结束YYYYMMDD, 标签, 受影响品种tuple 或 "ALL", 处置备注[, 自动打标])
#   第6项「自动打标」省略=True: 按 T-3/±1 规则自动打 D12 事件判据与新开限制提示。
#   置 False 用于**不可排期项的逐周顺延占位窗**(地缘轴): 只在清单里列出来提醒人工盯,
#   不自动打标 —— 真正的触发日是质变 headline 当日, 不是占位窗里的每一天;
#   否则 D12 会对能源链/贵金属长期常开, 与 3.5b「临近离散事件T-3」的定义脱钩。
# ⚠ 日期确定性分三档, 越弱越要在官宣后回来改: (a)已定=8月非农9/4、OPEC+9/6;
#   (b)「按框架1.4多源口径」=9/15-16 FOMC(框架据多源判定, 未见官方日历原文核对);
#   (c)「暂估」=WASDE 9/11、中国8月硬数据 9/15-16。新节点随 1.4 表滚动增删;
#   两个地缘「监控窗」是不可排期项的逐周顺延占位, 到期未质变就整体后移一周。
EVENTS = [   # 2026-08-30 按框架 v2.18 的 1.4 事件轴刷新(1.4 表本身沿用 v2.17 内容; 用户维护项)
    #  归档移除(已落地, 见框架1.4【归档】段): Jackson Hole·Warsh首秀(8/28鹰派)、
    #  黑色旺季终裁(8/29分侧执行)、阿曼-伊朗收入分成协议(8/26, 经济安排层)。
    #  移入下方"滚动/不可排期"注释: 8月底调减进度判决(框架已改"到期无数据·显式挂起",
    #  频率栏=事件级(挂起), 无可登记日期)。
    ("20260831", "20260904", "霍尔木兹僵局质变监控窗(①离散裁决对象, 不可排期; 未质变则逐周顺延)",
     ("MA", "SC", "AU", "AG", "CU", "AL"),
     "本窗是**占位提醒**不是事件日: ±1冻结与双向跳空预案针对真实质变headline当日; "
     "质变三形态: 谈判重启官宣→回签约裁决期(v2.14存档文本复用); 正式立法关闭/再袭船→中断复归侧评估; "
     "持续僵局(现状=名义封锁/经济安排/事实通行三层并存)→①维持未过; "
     "锚已换版'通行恢复·多源证实'(海湾出口15-16百万桶/日≈战前2/3), 后续跟踪爬坡斜率",
     False),
    ("20260831", "20260904", "俄乌轴质变监控窗(能源第二地缘轴, 不可排期; 未质变则逐周顺延)",
     ("MA", "SC", "AU", "AG"),
     "同为占位窗: 质变形态=停火信号(侵蚀逻辑回吐评估)/俄成品油出口禁令或配额(供给冲击升级)/"
     "更大规模打击(炼能损失量级跳变); 任一出现日=双向跳空预案日, 并入0.1低敞口判定; "
     "'俄乌升级=能源新主升'列3.6脆弱叙事(原油端被海湾出口恢复对冲)",
     False),
    ("20260904", "20260904", "8月非农(利率二次裁决链第一站; 框架1.4已定日期)",
     ("AU", "AG", "IM", "IC", "CU", "AL"),
     "Warsh鹰派落地后第一个硬数据裁决: 强劲→加息概率上行、贵金属回吐深化、有色宏观腿承压加重; "
     "走弱→'鹰派表态+弱数据'矛盾组合、贵金属回吐位第一个真实支撑测试; "
     "节点±1按事件窗口纪律, 贵金属gap收紧1.3(1.2表); 随后8月CPI接力"),
    ("20260906", "20260906", "OPEC+会议",
     ("MA", "SC", "AU", "AG"),
     "9月+18.8万桶/日已于8/2落地(年内配额恢复完成); IEA/OPEC月报已下调需求预期——"
     "9/6产量表态在僵局背景下与油价区间联动; 节点±1按事件窗口纪律"),
    ("20260911", "20260911", "WASDE(暂估, 官宣后改)",
     ("M", "CF", "SR"),
     "M: 报告前2日禁新开; ±1日农产品gap收紧1.3(1.2表)"),
    ("20260915", "20260916", "中国8月硬数据窗(工业/社零/固投, 暂估, 官宣后改)",
     ("IM", "IC", "RB", "JM", "J", "CU", "AL"),
     "②''资金二次确认的下一数据裁决(框架1.4); **与FOMC同窗**——横跨持仓按6.9做T-1处置时"
     "两个节点合并考虑, 不要只对其中一个对冲"),
    ("20260915", "20260916", "美联储9月FOMC(下一最大单点; fed_state终裁; 日期按框架1.4多源口径)",
     ("AU", "AG", "IM", "IC", "CU", "AL"),
     "当前定价约34%加息概率——**方向不预设, 加息与按兵两个剧本都入预案**: "
     "加息→贵金属趋势级回吐评估、D13复归档议题冻结、金融属性多头全面重估; "
     "按兵+鹰派指引→平台期延续、回吐位支撑测试; 按兵+转鸽→重定价反弹评估; "
     "**T-3起自动D12(约9/10起)、T-1对冲(6.9)、T-10内(约9/1起)核#29重入条件**"
     "(定价若完全悬于单一利率事件→#29重启评估, 经周度复评); "
     "贵金属gap收紧1.3(1.2表); 事件后T+1复评贵金属与fed_state全部状态行"),
]
# 滚动/不可排期监测(无精确日期可登记, 人工跟踪; 按框架 v2.18 的 1.4 与 6.8 刷新):
#   ①政策资金二次确认(②''完全过门, 裁决对象=8000亿投放进度/**首批项目清单(最后一件)**
#     +主力资金回流持续性+成交2万亿关口; 清单发布日按部委文件日纪律, 周度滚动);
#   ②反内卷双轨(轨一=第三份行业文件→跨行业外推裁决点; 轨二=光伏自律执行证据,
#     实际成交价vs成本线, 周度; ③门判据不变);
#   ③**黑色负反馈检验**(替换已归档的旺季终裁行): 焦炭提涨第二轮落地/钢厂减产或抵制信号/
#     铁水日产/焦煤现货涨势延续性/螺纹社库累库斜率——任一反向→原料存量多头止盈纪律触发;
#   ④焦煤复产风险信号(安监放松/山西复产超预期/西曲矿复产→D14预案);
#   ⑤LC重启条件周度复核(冻结期; 去库同口径连续性+现货企稳+排产收缩, 排产✗维持冻结);
#   ⑥**8月底调减进度判决**(③判决点, 框架v2.17改"到期无数据·显式挂起"): 无数据≠未达标,
#     不预支罚则; 第一补核项, 拿到数据即裁决;
#   ⑦油轮通行量爬坡斜率(①锚已多源证实, 转为跟踪向常态收敛的进度);
#   ⑧交易所风控措施公告(全品种, 尤金银/硅链/PS; 公告±1审慎, 日度核对);
#   ⑨**换月触发点**(非市场事件, 不进本表以免误打D12/±1标记; §0 会按真实交易日预警,
#     完整阶梯见框架 v2.20「合约滚动阶梯」表, ★v1.8 已收缩至池内): RB 2026-09-10(→RB2701-RB2703) /
#     MA 2026-09-16(结构对→MA2701-MA2705, 执行腿维持 MA2701) / SC 信号腿随主力换月(约9月中旬) /
#     AU 信号腿≈11月中旬 / JM·M 2026-12-18; 池外品种不再跟踪。
EVENT_T3_BUSDAYS = 3     # 「临近离散事件T-3」窗口(v2.9 3.5b D12第三判据)
EVENT_HORIZON_BD = 10    # §0b 前瞻清单范围(v2.9 0.0b: 未来10个交易日)

# ---- §2c 持仓登记 (v2.9 0.3#25 ATR重校准; ★方向性单边逐仓登记, 结构持仓豁免) ----
# 条目: (合约, 入场日YYYYMMDD, "多"/"空", 备注)
POSITIONS = [
    # ("AU2610", "20260720", "多", "示例: 建仓当日即登记"),
]   # ★当前空仓(2026-07-12 会话确认) —— 建仓当日起填入, §2c 自动核验

# 价差对: (标签, 近腿, 远腿, kind) —— 历史对照自动按年份平移生成
#   kind(★v1.8 收缩为三种): "A"=策略A触发(打≥70/≥85标签+SL/TP锚+价差腿一手风险#31) |
#         "信号"=信号席(不建仓; 不打触发标签、不受#2; 分位作①back方向/护栏口径输入) |
#         "结构监控"=黑色JM-RB价差(入场门=铁水<230, 手动)
#   候选A/候选代理/存档/H-roll/国债期货价差 五种已随 PS·LH·CU·IM/IC·TL/T 退出删除(git v1.7 可取回)
SPREAD_PAIRS = [   # ★v1.8: 随框架 v2.20 执行池收缩至 5 组(池外序列停采, 复活时按 git 历史行加回)
    ("MA",   "MA2610", "MA2701", "A"),
    #   ★v1.7换月: 近腿→实测主力 MA2610; 远腿 MA2701。★v1.8: MA2705 9/4 实测 20 日均 12,561 已过#2,
    #   触发线 2026-09-16(近腿#1线)或主力换月 → 结构对下滚 MA2701-MA2705(执行日复核#2);
    #   方向性单边执行腿=MA2701(§2 单独取指标), 不随本对滚动
    ("JM",   "JM2701", "JM2705", "A"),      # 黑色月差池(纯分位; 收缩叙事不加分); 双焦唯一结构腿
    #   ★v1.8: 当前价差水平一手风险(§1 打印行)> RISK_BUDGET → 框架 0.3#31 当期 0 手(留痕, 不进执行层)
    ("RB",   "RB2610", "RB2701", "A"),      # RB 月差候选(黑色月差池); 触发线 2026-09-10(或主力换月先到)
    #   → 整对下滚 RB2701-RB2703(RB2703 9/4 实测 22,106 过#2; RB2705 7,717 未过)
    ("黑色JM-RB", "JM2701", "RB2701", "结构监控"),
    #   ★v1.8: 原 J2701-RB2701 的 J 腿随 J 退出执行池(J2705 仅 446 手, 无第二个上万手月份)改用 JM;
    #   两腿同交割月对齐(v1.7 口径), 入场门=铁水<230(手动确认)
    # ---- 信号席 (框架 v2.20: 不建仓, 只作①back方向与护栏口径输入) ----
    ("SC近端", "SC2610", "SC2611", "信号"),
    #   ★v1.8: kind 由「候选A」改「信号」—— 0.3#31 单腿 57,253/价差腿(§1 打印行)均 0 手, 建仓路径关闭;
    #   分位仍照算(①「中断复归侧」待核要件=SC 近端 back 反弹); 主力换月日→SC2611-SC2612(SC2612 未过#2, 信号腿不受)
]

# 指标计算合约 (§2; ★v1.8 按框架 v2.20 执行池: 核心 3 + 备选 1 + 信号 2 = 7 腿)
INDICATOR_CONTRACTS = [
    "MA2610",   # 主力: #30 单日±5% 护栏判定腿 + A 结构近腿(9/16 或主力换月即下滚, 届时从本表移除); 高波层×0.5→1 手
    "MA2701",   # 方向性单边执行腿(剩余 87td ≥ 20+持仓上限; 一手 1,682 → 3 手)
    "JM2701",   # 核心②研究主载体(G 冻结; 一手 6,569 → 0 手@2ATR, #31 临界)
    "RB2701",   # 核心③ JM-RB 价差短腿/RB 月差候选(不开方向性单边; 一手 656 → 8 手); 9/10 起替代 RB2610
    "M2701",    # 独立备选(一手 993 → 5 手, 高波层×0.5→2 手); 12/18 或主力换月 → M2705
    "AU2612",   # 信号席: fed_state/D13 价格锚 + #31 复活核验(一手 42,117 ≈ 净值 28%, 0 手); 直接用 2612 不受 9/10 批次
    "SC2610",   # 信号席: MA 护栏「原油周涨幅」口径腿(周涨%列) + ①输入; 随主力换月滚(SC 不受#1)
]

# ---- ★v1.8 一手风险门 (框架 v2.20 0.3#31; 与框架 0) RISK_BUDGET / Step5 合约参数表同源) ----
RISK_BUDGET = 5250      # 单笔最大亏损 = ACCOUNT_SIZE 150,000 × 3.5%(框架 0) 用户输入)
# 品种 → (multiplier 每手乘数, tick_value 最小变动价值); 新品种入池前先与框架 Step5 合约参数表同步填列
CONTRACT_SPEC = {"MA": (10, 10), "RB": (10, 10), "M": (10, 10), "JM": (60, 30),
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
        print(f"  全部通过: {len(seen)} 个配置合约距最后交易日均 ≥20 交易日")


def _prod(sym):
    return re.match(r"[A-Za-z]+", sym).group().upper()


def _signal_pair_leg(sym):
    """sym 是否属于 kind=\"信号\" 的价差对(两腿均按信号腿处理, 不受#1/#2)。"""
    return any(sym in (n, f) for _l, n, f, k in SPREAD_PAIRS if k == "信号")


def spec_check():
    """★v1.8 启动参数校验(宁抛错不猜): CONTRACT_SPEC 必须覆盖全部池内品种, 且 multiplier 与
    tushare fut_basic.per_unit 一致 —— 乘数写错会让一手风险(0.3#31)成倍失真且无任何报错。
    (fut_basic.multiplier 字段实测为 None, per_unit 才是每手乘数: MA 10/JM 60/AU 1000/SC 1000。)"""
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
    print(f"  ★v1.8 参数校验: CONTRACT_SPEC 覆盖 {len(first)} 个池内品种, multiplier 与 fut_basic.per_unit 一致"
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
def spread_percentile(label, near, far, kind="A"):
    """kind: "A"=策略A触发(≥70/≥85 标签 + SL/TP锚 + 价差腿一手风险 0.3#31) |
             "信号"=信号席(不建仓, 不受#2; 分位仅作①back方向/护栏口径输入, 不打触发标签) |
             "结构监控"=黑色JM-RB价差(入场门=铁水<230, 手动确认)。"""
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

    # ★两腿20日均成交(≤AS_OF口径)与距最后交易日: 否决#2/#1 是硬否决, 未过的对**不得**打出
    #   ≥70/≥85 入场标签(PR#16 review P1); 信号对(kind="信号")不建仓故不受, 只留痕。
    def _v20(s_):
        d = daily(s_)
        d = d[d["trade_date"] <= AS_OF]
        return float(pd.to_numeric(d["vol"], errors="coerce").tail(20).mean())
    vn = vf = float("nan")
    try:
        vn, vf = _v20(near), _v20(far)
    except Exception:
        pass
    try:
        dn, df_ = _busdays(AS_OF, delist_date(near)), _busdays(AS_OF, delist_date(far))
    except Exception:
        dn = df_ = None
    thin = [f"{lbl}腿{v:,.0f}手" for lbl, v in (("近", vn), ("远", vf))
            if not np.isnan(v) and v < 10000]
    veto2 = bool(thin) and kind != "信号"

    # ★v1.8 SL/TP 锚 + 价差腿一手风险(0.3#31): |当前价差-50分位锚|×multiplier + 4×tick_value(两腿各2tick)
    lv = np.percentile(hist["spread"], [10, 30, 50])
    lp = np.percentile(hist_pct, [10, 30, 50])
    spec = CONTRACT_SPEC.get(_prod(near))
    risk_sp = lots_sp = None
    if spec:
        risk_sp = abs(float(cur["spread"]) - float(lv[2])) * spec[0] + 4 * spec[1]
        lots_sp = int(RISK_BUDGET // risk_sp) if risk_sp > 0 else 0

    trig = ("≥85 主仓触发" if pct_same >= 85 else
            "≥70 候选触发" if pct_same >= 70 else "未触发")
    if kind == "A":
        if veto2:
            tag = (f"**否决#2 未过({'/'.join(thin)}<1万手)→ 不进执行层、不产生入场信号**; "
                   f"分位 {pct_same:.1f} 仅作序列留痕, 恢复条件=两腿20日均量均回到1万手以上")
        elif lots_sp is not None and lots_sp < 1:
            tag = (f"分位{trig}, 但 **否决#31 未过(价差腿一手风险 {risk_sp:,.0f} > 预算 {RISK_BUDGET:,})"
                   f"→ 不进执行层、不产生入场信号**; 解锁=价差向50分位锚回归至一手≤预算")
        else:
            tag = trig
    elif kind == "信号":
        lvl = ("同期极端高位(≥85)" if pct_same >= 85 else "同期偏高(≥70)" if pct_same >= 70 else
               "同期极端低位(≤15)" if pct_same <= 15 else "同期中性")
        tag = (f"信号腿·不建仓(0.3#31): 近端back {lvl} —— 作①'back反弹/回落'要件输入与护栏口径, "
               f"不打触发标签、不受#2")
    elif kind == "结构监控":
        tag = "黑色价差监控 —— 入场门=铁水<230(基本面, 手动确认)"
    else:
        tag = kind

    print(f"\n[{label}] {near} - {far}  (数据截至 {cur['trade_date']})")
    print(f"  当前价差: {cur['spread']:+.1f}  |  价差%: {cur['spread_pct']:+.3f}%")
    if not (np.isnan(vn) and np.isnan(vf)):
        warn = ""
        if thin and kind == "信号":
            warn = f"  ({'/'.join(thin)}<1万手; 信号腿不受#2)"
        elif not np.isnan(vf) and vf < 10000:
            warn = "  ⚠ 远腿<1万手(否决#2)"
        elif not np.isnan(vn) and vn < 10000:
            warn = "  ⚠ 近腿<1万手(否决#2)"
        td = (f"  |  距最后交易日: 近 {dn} / 远 {df_} td"
              + ("(信号腿不受#1)" if kind == "信号" else "")) if dn is not None else ""
        print(f"  两腿20日均成交: 近 {vn:,.0f} / 远 {vf:,.0f}{warn}{td}")
    print(f"  近{YEARS}年同期分位(±{WIN}交易日): {pct_same:.1f}  → {tag}")
    if kind in ("A", "信号"):
        lbl = ("同期池分位对应价差水平(SL/TP锚)" if kind == "A" and not veto2 and (lots_sp is None or lots_sp >= 1)
               else "同期池分位对应价差水平(不作入场锚, 仅留痕/back极端度参考)")
        print(f"  {lbl}: 10分位={lv[0]:+.1f} / 30分位={lv[1]:+.1f} / 50分位={lv[2]:+.1f}"
              f"  (%口径: {lp[0]:+.3f}/{lp[1]:+.3f}/{lp[2]:+.3f})")
        if spec:
            print(f"  价差腿一手风险(至50分位锚, 0.3#31): {risk_sp:,.0f} → {lots_sp} 手"
                  + ("  (信号腿不建仓, 仅留痕)" if kind == "信号" else ""))
        else:
            print("  价差腿一手风险: 合约参数缺(补 CONTRACT_SPEC 后再核 0.3#31)")
    if ok_years < YEARS:
        print(f"  ⚠ 同期对照仅 {ok_years}/{YEARS} 年 —— 本分位实为「近{ok_years}年"
              f"同期分位」, 口径降级, 按 0.3#13 审慎处理")
    print(f"  本对全生命周期分位: {pct_life:.1f}  (参考)")
    print(f"  历史对照: {'; '.join(used)}")


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
    signal = sym in SIGNAL_LEGS          # ★v1.8 信号席: 不建仓, 不受#1/#2(框架 0)注c)
    if dte is None:
        veto.append("到期解析失败⚠")
    elif dte < 20:
        veto.append("信号腿·不受#1(随主力换月)" if signal else "距到期<20⚠")
    if not np.isnan(vol20) and vol20 < 10000:
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
    # 一手风险 = 2×ATR20×multiplier + 2×tick_value; 手数 = floor(预算/一手风险);
    #   高波层(ATR250分位>80)按框架 0.3#31 再 floor(×0.5) 后仍须 ≥1 手 —— 「手数」列即该有效手数。
    spec = CONTRACT_SPEC.get(prod)
    if spec:
        risk1 = 2 * float(atr20.iloc[-1]) * spec[0] + 2 * spec[1]
        lots_raw = int(RISK_BUDGET // risk1) if risk1 > 0 else 0
        lots1 = lots_raw // 2 if atr_pct > 80 else lots_raw
        if lots_raw < 1:
            veto.append("一手风险>预算⚠(#31)")
        elif lots1 < 1:
            veto.append("高波层×0.5后<1手⚠(#31)")
    else:
        risk1, lots1 = np.nan, np.nan
        veto.append("合约参数缺⚠(#31无法核, 补 CONTRACT_SPEC)")

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
            "一手风险2ATR": int(round(risk1)) if not np.isnan(risk1) else np.nan,
            "手数(高波×0.5后)": lots1,
            "否决检查": "|".join(veto) if veto else "-"}


COLS_VOLA = ["合约", "数据截至", "px", "ATR20", "ADX14", "HV20%", "HV60%",
             "HV20/HV60", "ATR20分位", "分位样本N", "ATR分层", "D12提示"]
COLS_POS = ["合约", "H250", "dist_H250%", "H20", "L20", "H60", "L60",
            "MA20", "MA60", "20日均成交", "距到期", "周涨%", "一手风险2ATR", "手数(高波×0.5后)", "否决检查"]


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
        description="v2.20 框架数据脚本 (Tushare Pro, v1.8)")
    parser.add_argument(
        "--as-of", type=_valid_date, default=AS_OF, metavar="YYYYMMDD",
        help="复盘基准日 (缺省=运行当天, 当前默认 %(default)s)")
    args = parser.parse_args()
    AS_OF = args.as_of

    print(f"== v2.20 框架数据脚本 v1.8 | AS_OF={AS_OF} | 同期窗口±{WIN} | "
          f"单笔预算{RISK_BUDGET:,}(0.3#31) | 事件节点{len(EVENTS)}项(用户维护) ==")

    spec_check()                     # ★v1.8 合约参数校验, 不过直接退出
    contract_freshness_check()

    # §0b: 先算事件窗口 → §2 的 D12「事件T-3」判据依赖本结果
    _T3_PRODS.update(print_event_calendar())

    print("\n---- 1) 价差同期分位 (输入B: A触发·MA/JM/RB月差(含价差腿一手风险#31) / "
          "JM-RB黑色价差监控 / SC近端信号) ----")
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
    print("\n  -- 2b 位置/均线/流动性 (D11 / Entry / 否决#1#2 / ★v1.8 周涨%(7日历日基准)·一手风险#31·手数含高波×0.5) --")
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
