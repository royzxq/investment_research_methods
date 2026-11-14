# 隔离算术审计，不是正式投研交付

保留旧折扣作控制变量，算术通过不证明折扣经济独立；未运行完整Gate/来源验收，不可发布。

<!-- research-checks:start -->
研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：

| 情景 | 经营价值 | 权益调整 | 权益价值 | V50 |
|---|---:|---:|---:|---:|
| low | 1218.4942746251209207154614275164677192185711984968 | 683.25970046 | 1901.7539750851209207154614275164677192185711984968 | 8.613 |
| base | 3096.4461490491393245616869574586180403794362050742 | 683.25970046 | 3779.7058495091393245616869574586180403794362050742 | 17.118 |
| high | 6668.9831407821045028449400166055747314102308096136 | 683.25970046 | 7352.2428412421045028449400166055747314102308096136 | 33.298 |

| 情景 | 分部 | 年 | NOPAT | FCFF | 现值 |
|---|---|---:|---:|---:|---:|
| low | smartphones_and_other | 1 | 12.000000 | 5.865000 | 5.283784 |
| low | smartphones_and_other | 2 | 12.000000 | 8.955000 | 7.268079 |
| low | smartphones_and_other | 3 | 14.544000 | 10.848000 | 7.931964 |
| low | smartphones_and_other | 4 | 14.688000 | 10.982000 | 7.234184 |
| low | smartphones_and_other | 5 | 18.540000 | 14.783000 | 8.772991 |
| low | smartphones_and_other | 6 | 18.720000 | 14.953000 | 7.994484 |
| low | smartphones_and_other | 7 | 18.900000 | 15.642750 | 7.534462 |
| low | smartphones_and_other | 8 | 19.080000 | 16.371000 | 7.103811 |
| low | smartphones_and_other | 9 | 19.260000 | 17.086500 | 6.679536 |
| low | smartphones_and_other | 10 | 19.440000 | 17.820000 | 6.275927 |
| low | iot | 1 | 24.000000 | 17.000000 | 15.315315 |
| low | iot | 2 | 24.480000 | 18.580000 | 15.079945 |
| low | iot | 3 | 24.960000 | 18.960000 | 13.863389 |
| low | iot | 4 | 27.136000 | 21.036000 | 13.857065 |
| low | iot | 5 | 28.512000 | 22.312000 | 13.241086 |
| low | iot | 6 | 30.800000 | 24.500000 | 13.098700 |
| low | iot | 7 | 31.416000 | 25.894000 | 12.472063 |
| low | iot | 8 | 32.032000 | 27.397333 | 11.888429 |
| low | iot | 9 | 32.676000 | 28.945000 | 11.315318 |
| low | iot | 10 | 33.320000 | 30.543333 | 10.756888 |
| low | internet | 1 | 115.200000 | 112.680000 | 101.513514 |
| low | internet | 2 | 116.480000 | 114.620000 | 93.028163 |
| low | internet | 3 | 117.760000 | 115.880000 | 84.730457 |
| low | internet | 4 | 119.040000 | 117.140000 | 77.163746 |
| low | internet | 5 | 120.320000 | 118.400000 | 70.264637 |
| low | internet | 6 | 121.600000 | 119.660000 | 63.975122 |
| low | internet | 7 | 122.880000 | 119.874000 | 57.738320 |
| low | internet | 8 | 124.160000 | 120.066000 | 52.099819 |
| low | internet | 9 | 125.440000 | 120.236000 | 47.003231 |
| low | internet | 10 | 126.720000 | 120.384000 | 42.397376 |
| low | ev_ai | 1 | -80.000000 | -108.000000 | -97.297297 |
| low | ev_ai | 2 | -67.200000 | -91.400000 | -74.182290 |
| low | ev_ai | 3 | -52.800000 | -78.000000 | -57.032928 |
| low | ev_ai | 4 | -36.800000 | -63.000000 | -41.500051 |
| low | ev_ai | 5 | -19.200000 | -46.400000 | -27.536142 |
| low | ev_ai | 6 | 0.000000 | -28.200000 | -15.076872 |
| low | ev_ai | 7 | 4.160000 | -17.844000 | -8.594713 |
| low | ev_ai | 8 | 8.640000 | -6.892000 | -2.990621 |
| low | ev_ai | 9 | 13.320000 | 4.783500 | 1.869989 |
| low | ev_ai | 10 | 13.560000 | 12.204000 | 4.298059 |
| base | smartphones_and_other | 1 | 26.400000 | 19.656000 | 17.869091 |
| base | smartphones_and_other | 2 | 34.000000 | 28.531000 | 23.579339 |
| base | smartphones_and_other | 3 | 39.200000 | 33.630000 | 25.266717 |
| base | smartphones_and_other | 4 | 43.200000 | 37.529000 | 25.632812 |
| base | smartphones_and_other | 5 | 44.160000 | 38.808000 | 24.096715 |
| base | smartphones_and_other | 6 | 45.120000 | 39.687000 | 22.402277 |
| base | smartphones_and_other | 7 | 46.080000 | 40.408500 | 20.735950 |
| base | smartphones_and_other | 8 | 47.040000 | 41.106500 | 19.176486 |
| base | smartphones_and_other | 9 | 47.976000 | 41.769900 | 17.714515 |
| base | smartphones_and_other | 10 | 48.936000 | 42.411200 | 16.351354 |
| base | iot | 1 | 36.800000 | 28.750000 | 26.136364 |
| base | iot | 2 | 42.312000 | 32.962000 | 27.241322 |
| base | iot | 3 | 47.160000 | 37.410000 | 28.106687 |
| base | iot | 4 | 53.376000 | 43.226000 | 29.523940 |
| base | iot | 5 | 58.400000 | 48.300000 | 29.990500 |
| base | iot | 6 | 61.200000 | 50.750000 | 28.647052 |
| base | iot | 7 | 64.000000 | 53.766667 | 27.590801 |
| base | iot | 8 | 66.400000 | 56.623333 | 26.415203 |
| base | iot | 9 | 68.800000 | 59.170000 | 25.093856 |
| base | iot | 10 | 70.880000 | 61.429333 | 23.683667 |
| base | internet | 1 | 136.800000 | 134.140000 | 121.945455 |
| base | internet | 2 | 144.000000 | 141.800000 | 117.190083 |
| base | internet | 3 | 151.200000 | 148.900000 | 111.870774 |
| base | internet | 4 | 158.400000 | 156.000000 | 106.550099 |
| base | internet | 5 | 165.600000 | 163.100000 | 101.272268 |
| base | internet | 6 | 172.800000 | 170.200000 | 96.073463 |
| base | internet | 7 | 180.000000 | 174.375000 | 89.481947 |
| base | internet | 8 | 187.200000 | 178.312000 | 83.183864 |
| base | internet | 9 | 193.680000 | 181.341700 | 76.906583 |
| base | internet | 10 | 199.440000 | 183.484800 | 70.741333 |
| base | ev_ai | 1 | -60.000000 | -95.000000 | -86.363636 |
| base | ev_ai | 2 | -34.500000 | -75.250000 | -62.190083 |
| base | ev_ai | 3 | 0.000000 | -44.500000 | -33.433509 |
| base | ev_ai | 4 | 23.200000 | -25.050000 | -17.109487 |
| base | ev_ai | 5 | 38.400000 | -13.600000 | -8.444530 |
| base | ev_ai | 6 | 55.360000 | 1.710000 | 0.965250 |
| base | ev_ai | 7 | 66.600000 | 21.937500 | 11.257406 |
| base | ev_ai | 8 | 78.400000 | 42.966667 | 20.044267 |
| base | ev_ai | 9 | 82.000000 | 57.137500 | 24.231878 |
| base | ev_ai | 10 | 84.800000 | 70.666667 | 27.245059 |
| high | smartphones_and_other | 1 | 43.200000 | 35.850000 | 32.889908 |
| high | smartphones_and_other | 2 | 53.200000 | 45.308000 | 38.134837 |
| high | smartphones_and_other | 3 | 64.000000 | 55.906000 | 43.169690 |
| high | smartphones_and_other | 4 | 67.200000 | 58.904000 | 41.729079 |
| high | smartphones_and_other | 5 | 70.400000 | 61.902000 | 40.232053 |
| high | smartphones_and_other | 6 | 73.280000 | 65.000000 | 38.757376 |
| high | smartphones_and_other | 7 | 75.840000 | 67.175167 | 36.747117 |
| high | smartphones_and_other | 8 | 78.080000 | 68.765778 | 34.511225 |
| high | smartphones_and_other | 9 | 80.000000 | 69.790167 | 32.133331 |
| high | smartphones_and_other | 10 | 82.016000 | 70.624889 | 29.832716 |
| high | iot | 1 | 52.000000 | 42.900000 | 39.357798 |
| high | iot | 2 | 62.920000 | 50.570000 | 42.563757 |
| high | iot | 3 | 75.360000 | 61.910000 | 47.805879 |
| high | iot | 4 | 82.560000 | 67.960000 | 48.144577 |
| high | iot | 5 | 89.760000 | 74.410000 | 48.361394 |
| high | iot | 6 | 96.480000 | 80.830000 | 48.196288 |
| high | iot | 7 | 102.720000 | 87.228333 | 47.716885 |
| high | iot | 8 | 108.480000 | 92.896667 | 46.621704 |
| high | iot | 9 | 113.760000 | 97.847500 | 45.051707 |
| high | iot | 10 | 118.320000 | 101.886667 | 43.038029 |
| high | internet | 1 | 157.440000 | 154.570000 | 141.807339 |
| high | internet | 2 | 173.656000 | 171.111000 | 144.020705 |
| high | internet | 3 | 191.200000 | 188.460000 | 145.525699 |
| high | internet | 4 | 206.000000 | 203.055000 | 143.849281 |
| high | internet | 5 | 221.600000 | 218.440000 | 141.971012 |
| high | internet | 6 | 238.000000 | 234.615000 | 139.893259 |
| high | internet | 7 | 254.800000 | 246.787917 | 135.001442 |
| high | internet | 8 | 271.200000 | 258.000000 | 129.481500 |
| high | internet | 9 | 286.400000 | 267.510000 | 123.169035 |
| high | internet | 10 | 300.800000 | 275.733333 | 116.472740 |
| high | ev_ai | 1 | 0.000000 | -42.000000 | -38.532110 |
| high | ev_ai | 2 | 23.040000 | -32.160000 | -27.068429 |
| high | ev_ai | 3 | 54.400000 | -8.900000 | -6.872433 |
| high | ev_ai | 4 | 87.120000 | 15.220000 | 10.782232 |
| high | ev_ai | 5 | 118.560000 | 37.560000 | 24.411423 |
| high | ev_ai | 6 | 143.920000 | 56.470000 | 33.671216 |
| high | ev_ai | 7 | 170.400000 | 93.850000 | 51.339164 |
| high | ev_ai | 8 | 197.760000 | 132.655000 | 66.575071 |
| high | ev_ai | 9 | 211.200000 | 159.975000 | 73.656934 |
| high | ev_ai | 10 | 221.760000 | 184.800000 | 78.061517 |

| 情景 | 分部 | 显式期现值 | 终值首年NOPAT | 终值再投资 | 终值现值 |
|---|---|---:|---:|---:|---:|
| low | smartphones_and_other | 72.079222 | 19.634400 | 1.636200 | 63.386867 |
| low | iot | 130.888197 | 33.653200 | 2.804433 | 108.644568 |
| low | internet | 689.914386 | 127.987200 | 6.399360 | 428.213501 |
| low | ev_ai | -318.042866 | 13.695600 | 1.369560 | 43.410400 |
| base | smartphones_and_other | 212.825254 | 49.914720 | 6.655296 | 208.479758 |
| base | iot | 272.429392 | 72.297600 | 9.639680 | 301.966757 |
| base | internet | 975.215868 | 203.428800 | 16.274304 | 901.952000 |
| base | ev_ai | -123.797384 | 86.496000 | 14.416000 | 347.374504 |
| high | smartphones_and_other | 368.137332 | 84.066400 | 11.675889 | 470.438988 |
| high | iot | 456.858021 | 121.278000 | 16.844167 | 678.676612 |
| high | internet | 1361.192012 | 308.320000 | 25.693333 | 1836.685513 |
| high | ev_ai | 266.024585 | 227.304000 | 37.884000 | 1230.970078 |

估值假设与市价差异（检查声明及算术，不证明预测正确）：
- base_case：同包条件截面；经营假设见inputs/evidence与assumptions；非概率中位数，资产归属仍未闭合
- method_choice：这是模型实验，不是完整生产研究；本组严格采用valuation.kind所声明的资本化法或分业务FCFF，新增假设分拆披露。
- pe_crosscheck：旧阿里普通股利润PE为12/15/18倍；旧小米是EV/NOPAT资本化16/18/20倍再除1.10，不得标为归母PE。本DCF基准经营EV=3096.4461亿元、Y1 NOPAT=140.0000亿元，隐含EV/NOPAT=22.1175倍；含恢复预期，非同业事实或正当性证明。
- 市价核对：{"as_of": "2026-10-30", "explanation": "独立预测后反解；未闭合资金/投资NAV均条件化，市价不用于拟合基准", "price": 26.48, "source": "冻结2026-10-31原始数据包"}
- 反向DCF条件解：{"cases": [{"lower": 0, "modeled_price": 26.48, "parameter": 0.3475217745902895, "residual": 0.0, "scenario": "base", "segment_id": "ev_ai", "target_price": 26.48, "upper": 0.5, "variable": "terminal_margin"}], "reason": "冻结显式期与其它业务，仅反解指定业务终值利润率；不是唯一业务天花板", "status": "solved"}

| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |
|---|---:|---|---|---|
| d_base | 30% | 30%—30% | d_base | initial |
| r_chip | 3% | 3%—3% | r_chip | initial |
| r_v5 | 10% | 10%—10% | r_v5 | initial |
| r_gov | 3% | 3%—3% | r_gov | initial |
| r_terminal | 8% | 8%—8% | r_terminal | initial |

总折扣乘数：0.54534564；用途：tracking。
明确报价：P1={"base": 9.335}；T1={"price_condition": "接近V50上沿时复核"}。

| 约束 | 作用 | 状态 | 依据 |
|---|---|---|---|
| CAPITAL_UNRESOLVED | entry,add: eligibility | unknown | 现金与投资净归属缺口；隔离实验无正式资格裁决 |
| HOLDING_NOT_REASSESSED | holding: review_holding | unknown | 隔离估值实验未形成新的持仓判断 |

| 范围 | 当前研究状态 | 未解约束ID |
|---|---|---|
| entry | unknown | CAPITAL_UNRESOLVED |
| add | unknown | CAPITAL_UNRESOLVED |
| holding | unknown | HOLDING_NOT_REASSESSED |

恢复前须同时解除全部仍有效约束：{"add": ["CAPITAL_UNRESOLVED"], "entry": ["CAPITAL_UNRESOLVED"], "holding": ["HOLDING_NOT_REASSESSED"]}。
<!-- research-checks:end -->

<details><summary>计算、风险归属与解除条件审计输入</summary>

<!-- research-audit:start -->
```json
{
  "schema_version": "stock-research-audit/v4",
  "identity": {
    "code": "01810.HK",
    "generator": "codex",
    "valuation_date": "2026-10-31",
    "currency": "HKD"
  },
  "valuation": {
    "kind": "dcf_fcff",
    "currency": "CNY",
    "amount_unit": "100_million",
    "shares": 25795986357,
    "fx_to_quote": 1.1683061896861928,
    "scenarios": {
      "low": {
        "segments": [
          {
            "id": "smartphones_and_other",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "手机H1收入863.92014亿元、毛利率9.3%、ASP1330元但出货6500万部；内存成本压毛利，Q3行业/小米量弱。预测收入与经营率独立假设，未把毛利当EBIT；末期保留低单位利润。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 传统其他业务收入/资本投入并入本分部，零EBIT；合并后利润率为加权结果，不能拿该稀释率对比披露手机毛利。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.11,
            "years": [
              {
                "year": 1,
                "revenue": 1545,
                "ebit_margin": 0.009708737864077669,
                "tax_rate": 0.2,
                "da": 22.725,
                "capex": 25.77,
                "delta_nwc": 3.09
              },
              {
                "year": 2,
                "revenue": 1545,
                "ebit_margin": 0.009708737864077669,
                "tax_rate": 0.2,
                "da": 22.725,
                "capex": 25.77,
                "delta_nwc": 0.0
              },
              {
                "year": 3,
                "revenue": 1561,
                "ebit_margin": 0.011646380525304293,
                "tax_rate": 0.2,
                "da": 22.955000000000002,
                "capex": 26.031,
                "delta_nwc": 0.62
              },
              {
                "year": 4,
                "revenue": 1576,
                "ebit_margin": 0.0116497461928934,
                "tax_rate": 0.2,
                "da": 23.18,
                "capex": 26.286,
                "delta_nwc": 0.6
              },
              {
                "year": 5,
                "revenue": 1592,
                "ebit_margin": 0.014557160804020102,
                "tax_rate": 0.2,
                "da": 23.41,
                "capex": 26.547,
                "delta_nwc": 0.62
              },
              {
                "year": 6,
                "revenue": 1607,
                "ebit_margin": 0.014561294337274424,
                "tax_rate": 0.2,
                "da": 23.634999999999998,
                "capex": 26.802,
                "delta_nwc": 0.6
              },
              {
                "year": 7,
                "revenue": 1623,
                "ebit_margin": 0.01455637707948244,
                "tax_rate": 0.2,
                "da": 23.865,
                "capex": 26.50225,
                "delta_nwc": 0.62
              },
              {
                "year": 8,
                "revenue": 1638,
                "ebit_margin": 0.014560439560439559,
                "tax_rate": 0.2,
                "da": 24.09,
                "capex": 26.198999999999998,
                "delta_nwc": 0.6
              },
              {
                "year": 9,
                "revenue": 1654,
                "ebit_margin": 0.014555622732769044,
                "tax_rate": 0.2,
                "da": 24.32,
                "capex": 25.876250000000002,
                "delta_nwc": 0.61725
              },
              {
                "year": 10,
                "revenue": 1669,
                "ebit_margin": 0.014559616536848412,
                "tax_rate": 0.2,
                "da": 24.545,
                "capex": 25.565,
                "delta_nwc": 0.6
              }
            ],
            "terminal": {
              "growth": 0.01,
              "roic": 0.12,
              "margin": 0.014559616536848412,
              "tax_rate": 0.2
            }
          },
          {
            "id": "iot",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "IoT H1收入559.5916亿元、毛利率22.3%，境外渠道有增长但国内耐用品压力；费用分摊后的3%–6%经营率远低于毛利，成熟增长逐步收敛。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.11,
            "years": [
              {
                "year": 1,
                "revenue": 1000,
                "ebit_margin": 0.03,
                "tax_rate": 0.2,
                "da": 20.0,
                "capex": 25.0,
                "delta_nwc": 2.0
              },
              {
                "year": 2,
                "revenue": 1020,
                "ebit_margin": 0.03,
                "tax_rate": 0.2,
                "da": 20.4,
                "capex": 25.5,
                "delta_nwc": 0.8
              },
              {
                "year": 3,
                "revenue": 1040,
                "ebit_margin": 0.03,
                "tax_rate": 0.2,
                "da": 20.8,
                "capex": 26.0,
                "delta_nwc": 0.8
              },
              {
                "year": 4,
                "revenue": 1060,
                "ebit_margin": 0.032,
                "tax_rate": 0.2,
                "da": 21.2,
                "capex": 26.5,
                "delta_nwc": 0.8
              },
              {
                "year": 5,
                "revenue": 1080,
                "ebit_margin": 0.033,
                "tax_rate": 0.2,
                "da": 21.6,
                "capex": 27.0,
                "delta_nwc": 0.8
              },
              {
                "year": 6,
                "revenue": 1100,
                "ebit_margin": 0.035,
                "tax_rate": 0.2,
                "da": 22.0,
                "capex": 27.5,
                "delta_nwc": 0.8
              },
              {
                "year": 7,
                "revenue": 1122,
                "ebit_margin": 0.035,
                "tax_rate": 0.2,
                "da": 22.44,
                "capex": 27.082,
                "delta_nwc": 0.88
              },
              {
                "year": 8,
                "revenue": 1144,
                "ebit_margin": 0.035,
                "tax_rate": 0.2,
                "da": 22.88,
                "capex": 26.63466667,
                "delta_nwc": 0.88
              },
              {
                "year": 9,
                "revenue": 1167,
                "ebit_margin": 0.035,
                "tax_rate": 0.2,
                "da": 23.34,
                "capex": 26.151,
                "delta_nwc": 0.92
              },
              {
                "year": 10,
                "revenue": 1190,
                "ebit_margin": 0.035,
                "tax_rate": 0.2,
                "da": 23.8,
                "capex": 25.65666667,
                "delta_nwc": 0.92
              }
            ],
            "terminal": {
              "growth": 0.01,
              "roic": 0.12,
              "margin": 0.035,
              "tax_rate": 0.2
            }
          },
          {
            "id": "internet",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "互联网H1收入185.12009亿元、同比1.9%、毛利率76.4%；全球MAU增4.8%不能直接当收入增速。40%–50% EBIT为研发、获客和总部费用后假设，不是披露分部EBIT。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.11,
            "years": [
              {
                "year": 1,
                "revenue": 360,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.0,
                "capex": 10.8,
                "delta_nwc": 0.72
              },
              {
                "year": 2,
                "revenue": 364,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.1,
                "capex": 10.92,
                "delta_nwc": 0.04
              },
              {
                "year": 3,
                "revenue": 368,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.2,
                "capex": 11.04,
                "delta_nwc": 0.04
              },
              {
                "year": 4,
                "revenue": 372,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.3,
                "capex": 11.16,
                "delta_nwc": 0.04
              },
              {
                "year": 5,
                "revenue": 376,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.4,
                "capex": 11.28,
                "delta_nwc": 0.04
              },
              {
                "year": 6,
                "revenue": 380,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.5,
                "capex": 11.4,
                "delta_nwc": 0.04
              },
              {
                "year": 7,
                "revenue": 384,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.6,
                "capex": 12.566,
                "delta_nwc": 0.04
              },
              {
                "year": 8,
                "revenue": 388,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.7,
                "capex": 13.754,
                "delta_nwc": 0.04
              },
              {
                "year": 9,
                "revenue": 392,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.8,
                "capex": 14.964,
                "delta_nwc": 0.04
              },
              {
                "year": 10,
                "revenue": 396,
                "ebit_margin": 0.4,
                "tax_rate": 0.2,
                "da": 9.9,
                "capex": 16.196,
                "delta_nwc": 0.04
              }
            ],
            "terminal": {
              "growth": 0.01,
              "roic": 0.2,
              "margin": 0.4,
              "tax_rate": 0.2
            }
          },
          {
            "id": "ev_ai",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "汽车/AI/其他新业务H1收入447.60253亿元、交付185055辆、毛利率19.6%、经营亏损约57亿元；AI已有收入包含在本分部。亏损修复与规模扩张需要再投资，未另加独立AI/机器人许可价值。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.11,
            "years": [
              {
                "year": 1,
                "revenue": 800,
                "ebit_margin": -0.1,
                "tax_rate": 0.0,
                "da": 32.0,
                "capex": 52.0,
                "delta_nwc": 8.0
              },
              {
                "year": 2,
                "revenue": 840,
                "ebit_margin": -0.08,
                "tax_rate": 0.0,
                "da": 33.6,
                "capex": 54.6,
                "delta_nwc": 3.2
              },
              {
                "year": 3,
                "revenue": 880,
                "ebit_margin": -0.06,
                "tax_rate": 0.0,
                "da": 35.2,
                "capex": 57.2,
                "delta_nwc": 3.2
              },
              {
                "year": 4,
                "revenue": 920,
                "ebit_margin": -0.04,
                "tax_rate": 0.0,
                "da": 36.8,
                "capex": 59.8,
                "delta_nwc": 3.2
              },
              {
                "year": 5,
                "revenue": 960,
                "ebit_margin": -0.02,
                "tax_rate": 0.0,
                "da": 38.4,
                "capex": 62.4,
                "delta_nwc": 3.2
              },
              {
                "year": 6,
                "revenue": 1000,
                "ebit_margin": 0,
                "tax_rate": 0.0,
                "da": 40.0,
                "capex": 65.0,
                "delta_nwc": 3.2
              },
              {
                "year": 7,
                "revenue": 1040,
                "ebit_margin": 0.005,
                "tax_rate": 0.2,
                "da": 41.6,
                "capex": 60.404,
                "delta_nwc": 3.2
              },
              {
                "year": 8,
                "revenue": 1080,
                "ebit_margin": 0.01,
                "tax_rate": 0.2,
                "da": 43.2,
                "capex": 55.532,
                "delta_nwc": 3.2
              },
              {
                "year": 9,
                "revenue": 1110,
                "ebit_margin": 0.015,
                "tax_rate": 0.2,
                "da": 44.4,
                "capex": 50.5365,
                "delta_nwc": 2.4
              },
              {
                "year": 10,
                "revenue": 1130,
                "ebit_margin": 0.015,
                "tax_rate": 0.2,
                "da": 45.2,
                "capex": 45.2,
                "delta_nwc": 1.356
              }
            ],
            "terminal": {
              "growth": 0.01,
              "roic": 0.1,
              "margin": 0.015,
              "tax_rate": 0.2
            }
          }
        ],
        "equity_adjustments": [
          {
            "id": "bank_assets",
            "amount": 1654.28714,
            "reason": "6/30现金等价物与两类定存；不含受限现金；仍含未拆分基金现金",
            "source": "S1印59/94"
          },
          {
            "id": "borrowings",
            "amount": -392.76762,
            "reason": "流动及非流动借款合计，含可转债；不另增转股分母",
            "source": "S1印60/100"
          },
          {
            "id": "lease_debt",
            "amount": -50.40762,
            "reason": "租赁融资口径；DCF的capex含未来新增使用权资产，旧租赁偿付不再进FCFF",
            "source": "S1印95–96"
          },
          {
            "id": "lp_liability_legacy_anchor",
            "amount": -142.3216,
            "reason": "只作可复算条件锚；须与基金现金及投资净归属一起替换，非假定基金资产零",
            "source": "S1印110"
          },
          {
            "id": "old_intangible_payables",
            "amount": -50.74695,
            "reason": "6/30已确认无形资产应付；年度capex只计估值后新增资本，排除这一存量结算",
            "source": "S1印110/112"
          },
          {
            "id": "old_construction_payables",
            "amount": -17.80532,
            "reason": "6/30已确认工程应付；从旧笼统储备中拆出，只扣一次",
            "source": "S1印112"
          },
          {
            "id": "minorities",
            "amount": -1.1949,
            "reason": "少数权益账面近似；未取得公允价值，固定跨模型比较",
            "source": "S1印60"
          },
          {
            "id": "post_june_buybacks",
            "amount": -15.78342954,
            "reason": "沿用截至10/28已核回购链合计HKD18.4398784226亿元×0.85594；不是回购授权全额",
            "source": "B1§5.2，S2/S3"
          },
          {
            "id": "minimum_operating_cash",
            "amount": -300.0,
            "reason": "条件假设：持续留存经营现金300亿元；250–400敏感性，不代表现金已损失；不含未来capex或ΔNWC",
            "source": "A-CASH；旧B1基准营运储备300亿元；本研究明确范围"
          },
          {
            "id": "fund_net_adjustment_condition",
            "amount": 0.0,
            "reason": "仅为条件C_f=142.3216、N_f=0、R_parent=0的算术锚；一般必须另加Δfund=-C_f+142.3216+N_f-R_parent；0不是已核事实",
            "source": "G-FUND；S1印89–91/110"
          },
          {
            "id": "unmodeled_nonbank_assets_condition",
            "amount": 0.0,
            "reason": "与旧比较一致的未估值资产占位；不证明投资资产价值为零。所有绝对股权值仅在该附加NAV=0条件下成立；另按净归属补充",
            "source": "G-NAV；S1印59/89–91"
          }
        ],
        "equity_value": 1901.7539750851208
      },
      "base": {
        "segments": [
          {
            "id": "smartphones_and_other",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "手机H1收入863.92014亿元、毛利率9.3%、ASP1330元但出货6500万部；内存成本压毛利，Q3行业/小米量弱。预测收入与经营率独立假设，未把毛利当EBIT；末期保留低单位利润。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 传统其他业务收入/资本投入并入本分部，零EBIT；合并后利润率为加权结果，不能拿该稀释率对比披露手机毛利。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.1,
            "years": [
              {
                "year": 1,
                "revenue": 1698,
                "ebit_margin": 0.019434628975265017,
                "tax_rate": 0.2,
                "da": 24.99,
                "capex": 28.338,
                "delta_nwc": 3.396
              },
              {
                "year": 2,
                "revenue": 1749,
                "ebit_margin": 0.024299599771297885,
                "tax_rate": 0.2,
                "da": 25.745,
                "capex": 29.194,
                "delta_nwc": 2.02
              },
              {
                "year": 3,
                "revenue": 1800,
                "ebit_margin": 0.02722222222222222,
                "tax_rate": 0.2,
                "da": 26.5,
                "capex": 30.05,
                "delta_nwc": 2.02
              },
              {
                "year": 4,
                "revenue": 1851,
                "ebit_margin": 0.029173419773095625,
                "tax_rate": 0.2,
                "da": 27.255,
                "capex": 30.906000000000002,
                "delta_nwc": 2.02
              },
              {
                "year": 5,
                "revenue": 1892,
                "ebit_margin": 0.029175475687103592,
                "tax_rate": 0.2,
                "da": 27.860000000000003,
                "capex": 31.592000000000002,
                "delta_nwc": 1.62
              },
              {
                "year": 6,
                "revenue": 1933,
                "ebit_margin": 0.029177444386963267,
                "tax_rate": 0.2,
                "da": 28.465,
                "capex": 32.278,
                "delta_nwc": 1.62
              },
              {
                "year": 7,
                "revenue": 1974,
                "ebit_margin": 0.02917933130699088,
                "tax_rate": 0.2,
                "da": 29.07,
                "capex": 33.121500000000005,
                "delta_nwc": 1.62
              },
              {
                "year": 8,
                "revenue": 2015,
                "ebit_margin": 0.029181141439205954,
                "tax_rate": 0.2,
                "da": 29.674999999999997,
                "capex": 33.988499999999995,
                "delta_nwc": 1.62
              },
              {
                "year": 9,
                "revenue": 2055,
                "ebit_margin": 0.029182481751824817,
                "tax_rate": 0.2,
                "da": 30.265,
                "capex": 34.8921,
                "delta_nwc": 1.579
              },
              {
                "year": 10,
                "revenue": 2096,
                "ebit_margin": 0.029184160305343508,
                "tax_rate": 0.2,
                "da": 30.87,
                "capex": 35.794799999999995,
                "delta_nwc": 1.6
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.15,
              "margin": 0.029184160305343508,
              "tax_rate": 0.2
            }
          },
          {
            "id": "iot",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "IoT H1收入559.5916亿元、毛利率22.3%，境外渠道有增长但国内耐用品压力；费用分摊后的3%–6%经营率远低于毛利，成熟增长逐步收敛。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.1,
            "years": [
              {
                "year": 1,
                "revenue": 1150,
                "ebit_margin": 0.04,
                "tax_rate": 0.2,
                "da": 23.0,
                "capex": 28.75,
                "delta_nwc": 2.3
              },
              {
                "year": 2,
                "revenue": 1230,
                "ebit_margin": 0.043,
                "tax_rate": 0.2,
                "da": 24.6,
                "capex": 30.75,
                "delta_nwc": 3.2
              },
              {
                "year": 3,
                "revenue": 1310,
                "ebit_margin": 0.045,
                "tax_rate": 0.2,
                "da": 26.2,
                "capex": 32.75,
                "delta_nwc": 3.2
              },
              {
                "year": 4,
                "revenue": 1390,
                "ebit_margin": 0.048,
                "tax_rate": 0.2,
                "da": 27.8,
                "capex": 34.75,
                "delta_nwc": 3.2
              },
              {
                "year": 5,
                "revenue": 1460,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 29.2,
                "capex": 36.5,
                "delta_nwc": 2.8
              },
              {
                "year": 6,
                "revenue": 1530,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 30.6,
                "capex": 38.25,
                "delta_nwc": 2.8
              },
              {
                "year": 7,
                "revenue": 1600,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 32.0,
                "capex": 39.43333333,
                "delta_nwc": 2.8
              },
              {
                "year": 8,
                "revenue": 1660,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 33.2,
                "capex": 40.57666667,
                "delta_nwc": 2.4
              },
              {
                "year": 9,
                "revenue": 1720,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 34.4,
                "capex": 41.63,
                "delta_nwc": 2.4
              },
              {
                "year": 10,
                "revenue": 1772,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 35.44,
                "capex": 42.81066667,
                "delta_nwc": 2.08
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.15,
              "margin": 0.05,
              "tax_rate": 0.2
            }
          },
          {
            "id": "internet",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "互联网H1收入185.12009亿元、同比1.9%、毛利率76.4%；全球MAU增4.8%不能直接当收入增速。40%–50% EBIT为研发、获客和总部费用后假设，不是披露分部EBIT。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.1,
            "years": [
              {
                "year": 1,
                "revenue": 380,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 9.5,
                "capex": 11.4,
                "delta_nwc": 0.76
              },
              {
                "year": 2,
                "revenue": 400,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 10.0,
                "capex": 12.0,
                "delta_nwc": 0.2
              },
              {
                "year": 3,
                "revenue": 420,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 10.5,
                "capex": 12.6,
                "delta_nwc": 0.2
              },
              {
                "year": 4,
                "revenue": 440,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 11.0,
                "capex": 13.2,
                "delta_nwc": 0.2
              },
              {
                "year": 5,
                "revenue": 460,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 11.5,
                "capex": 13.8,
                "delta_nwc": 0.2
              },
              {
                "year": 6,
                "revenue": 480,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 12.0,
                "capex": 14.4,
                "delta_nwc": 0.2
              },
              {
                "year": 7,
                "revenue": 500,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 12.5,
                "capex": 17.925,
                "delta_nwc": 0.2
              },
              {
                "year": 8,
                "revenue": 520,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 13.0,
                "capex": 21.688,
                "delta_nwc": 0.2
              },
              {
                "year": 9,
                "revenue": 538,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 13.45,
                "capex": 25.6083,
                "delta_nwc": 0.18
              },
              {
                "year": 10,
                "revenue": 554,
                "ebit_margin": 0.45,
                "tax_rate": 0.2,
                "da": 13.85,
                "capex": 29.6452,
                "delta_nwc": 0.16
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.25,
              "margin": 0.45,
              "tax_rate": 0.2
            }
          },
          {
            "id": "ev_ai",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "汽车/AI/其他新业务H1收入447.60253亿元、交付185055辆、毛利率19.6%、经营亏损约57亿元；AI已有收入包含在本分部。亏损修复与规模扩张需要再投资，未另加独立AI/机器人许可价值。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.1,
            "years": [
              {
                "year": 1,
                "revenue": 1000,
                "ebit_margin": -0.06,
                "tax_rate": 0.0,
                "da": 40.0,
                "capex": 65.0,
                "delta_nwc": 10.0
              },
              {
                "year": 2,
                "revenue": 1150,
                "ebit_margin": -0.03,
                "tax_rate": 0.0,
                "da": 46.0,
                "capex": 74.75,
                "delta_nwc": 12.0
              },
              {
                "year": 3,
                "revenue": 1300,
                "ebit_margin": 0,
                "tax_rate": 0.0,
                "da": 52.0,
                "capex": 84.5,
                "delta_nwc": 12.0
              },
              {
                "year": 4,
                "revenue": 1450,
                "ebit_margin": 0.02,
                "tax_rate": 0.2,
                "da": 58.0,
                "capex": 94.25,
                "delta_nwc": 12.0
              },
              {
                "year": 5,
                "revenue": 1600,
                "ebit_margin": 0.03,
                "tax_rate": 0.2,
                "da": 64.0,
                "capex": 104.0,
                "delta_nwc": 12.0
              },
              {
                "year": 6,
                "revenue": 1730,
                "ebit_margin": 0.04,
                "tax_rate": 0.2,
                "da": 69.2,
                "capex": 112.45,
                "delta_nwc": 10.4
              },
              {
                "year": 7,
                "revenue": 1850,
                "ebit_margin": 0.045,
                "tax_rate": 0.2,
                "da": 74.0,
                "capex": 109.0625,
                "delta_nwc": 9.6
              },
              {
                "year": 8,
                "revenue": 1960,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 78.4,
                "capex": 105.03333333,
                "delta_nwc": 8.8
              },
              {
                "year": 9,
                "revenue": 2050,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 82.0,
                "capex": 99.6625,
                "delta_nwc": 7.2
              },
              {
                "year": 10,
                "revenue": 2120,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 84.8,
                "capex": 93.33333333,
                "delta_nwc": 5.6
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.12,
              "margin": 0.05,
              "tax_rate": 0.2
            }
          }
        ],
        "equity_adjustments": [
          {
            "id": "bank_assets",
            "amount": 1654.28714,
            "reason": "6/30现金等价物与两类定存；不含受限现金；仍含未拆分基金现金",
            "source": "S1印59/94"
          },
          {
            "id": "borrowings",
            "amount": -392.76762,
            "reason": "流动及非流动借款合计，含可转债；不另增转股分母",
            "source": "S1印60/100"
          },
          {
            "id": "lease_debt",
            "amount": -50.40762,
            "reason": "租赁融资口径；DCF的capex含未来新增使用权资产，旧租赁偿付不再进FCFF",
            "source": "S1印95–96"
          },
          {
            "id": "lp_liability_legacy_anchor",
            "amount": -142.3216,
            "reason": "只作可复算条件锚；须与基金现金及投资净归属一起替换，非假定基金资产零",
            "source": "S1印110"
          },
          {
            "id": "old_intangible_payables",
            "amount": -50.74695,
            "reason": "6/30已确认无形资产应付；年度capex只计估值后新增资本，排除这一存量结算",
            "source": "S1印110/112"
          },
          {
            "id": "old_construction_payables",
            "amount": -17.80532,
            "reason": "6/30已确认工程应付；从旧笼统储备中拆出，只扣一次",
            "source": "S1印112"
          },
          {
            "id": "minorities",
            "amount": -1.1949,
            "reason": "少数权益账面近似；未取得公允价值，固定跨模型比较",
            "source": "S1印60"
          },
          {
            "id": "post_june_buybacks",
            "amount": -15.78342954,
            "reason": "沿用截至10/28已核回购链合计HKD18.4398784226亿元×0.85594；不是回购授权全额",
            "source": "B1§5.2，S2/S3"
          },
          {
            "id": "minimum_operating_cash",
            "amount": -300.0,
            "reason": "条件假设：持续留存经营现金300亿元；250–400敏感性，不代表现金已损失；不含未来capex或ΔNWC",
            "source": "A-CASH；旧B1基准营运储备300亿元；本研究明确范围"
          },
          {
            "id": "fund_net_adjustment_condition",
            "amount": 0.0,
            "reason": "仅为条件C_f=142.3216、N_f=0、R_parent=0的算术锚；一般必须另加Δfund=-C_f+142.3216+N_f-R_parent；0不是已核事实",
            "source": "G-FUND；S1印89–91/110"
          },
          {
            "id": "unmodeled_nonbank_assets_condition",
            "amount": 0.0,
            "reason": "与旧比较一致的未估值资产占位；不证明投资资产价值为零。所有绝对股权值仅在该附加NAV=0条件下成立；另按净归属补充",
            "source": "G-NAV；S1印59/89–91"
          }
        ],
        "equity_value": 3779.705849509139
      },
      "high": {
        "segments": [
          {
            "id": "smartphones_and_other",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "手机H1收入863.92014亿元、毛利率9.3%、ASP1330元但出货6500万部；内存成本压毛利，Q3行业/小米量弱。预测收入与经营率独立假设，未把毛利当EBIT；末期保留低单位利润。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 传统其他业务收入/资本投入并入本分部，零EBIT；合并后利润率为加权结果，不能拿该稀释率对比披露手机毛利。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.09,
            "years": [
              {
                "year": 1,
                "revenue": 1850,
                "ebit_margin": 0.02918918918918919,
                "tax_rate": 0.2,
                "da": 27.25,
                "capex": 30.900000000000002,
                "delta_nwc": 3.7
              },
              {
                "year": 2,
                "revenue": 1952,
                "ebit_margin": 0.03406762295081967,
                "tax_rate": 0.2,
                "da": 28.76,
                "capex": 32.611999999999995,
                "delta_nwc": 4.04
              },
              {
                "year": 3,
                "revenue": 2054,
                "ebit_margin": 0.03894839337877313,
                "tax_rate": 0.2,
                "da": 30.27,
                "capex": 34.324,
                "delta_nwc": 4.04
              },
              {
                "year": 4,
                "revenue": 2156,
                "ebit_margin": 0.03896103896103896,
                "tax_rate": 0.2,
                "da": 31.78,
                "capex": 36.036,
                "delta_nwc": 4.04
              },
              {
                "year": 5,
                "revenue": 2258,
                "ebit_margin": 0.03897254207263064,
                "tax_rate": 0.2,
                "da": 33.29,
                "capex": 37.748,
                "delta_nwc": 4.04
              },
              {
                "year": 6,
                "revenue": 2350,
                "ebit_margin": 0.038978723404255324,
                "tax_rate": 0.2,
                "da": 34.65,
                "capex": 39.29,
                "delta_nwc": 3.64
              },
              {
                "year": 7,
                "revenue": 2432,
                "ebit_margin": 0.03898026315789473,
                "tax_rate": 0.2,
                "da": 35.86,
                "capex": 41.28483333,
                "delta_nwc": 3.24
              },
              {
                "year": 8,
                "revenue": 2504,
                "ebit_margin": 0.038977635782747606,
                "tax_rate": 0.2,
                "da": 36.92,
                "capex": 43.39422222,
                "delta_nwc": 2.84
              },
              {
                "year": 9,
                "revenue": 2566,
                "ebit_margin": 0.03897116134060795,
                "tax_rate": 0.2,
                "da": 37.83,
                "capex": 45.613333329999996,
                "delta_nwc": 2.4265
              },
              {
                "year": 10,
                "revenue": 2631,
                "ebit_margin": 0.03896617255796275,
                "tax_rate": 0.2,
                "da": 38.785000000000004,
                "capex": 47.656111110000005,
                "delta_nwc": 2.52
              }
            ],
            "terminal": {
              "growth": 0.025,
              "roic": 0.18,
              "margin": 0.03896617255796275,
              "tax_rate": 0.2
            }
          },
          {
            "id": "iot",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "IoT H1收入559.5916亿元、毛利率22.3%，境外渠道有增长但国内耐用品压力；费用分摊后的3%–6%经营率远低于毛利，成熟增长逐步收敛。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.09,
            "years": [
              {
                "year": 1,
                "revenue": 1300,
                "ebit_margin": 0.05,
                "tax_rate": 0.2,
                "da": 26.0,
                "capex": 32.5,
                "delta_nwc": 2.6
              },
              {
                "year": 2,
                "revenue": 1430,
                "ebit_margin": 0.055,
                "tax_rate": 0.2,
                "da": 28.6,
                "capex": 35.75,
                "delta_nwc": 5.2
              },
              {
                "year": 3,
                "revenue": 1570,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 31.4,
                "capex": 39.25,
                "delta_nwc": 5.6
              },
              {
                "year": 4,
                "revenue": 1720,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 34.4,
                "capex": 43.0,
                "delta_nwc": 6.0
              },
              {
                "year": 5,
                "revenue": 1870,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 37.4,
                "capex": 46.75,
                "delta_nwc": 6.0
              },
              {
                "year": 6,
                "revenue": 2010,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 40.2,
                "capex": 50.25,
                "delta_nwc": 5.6
              },
              {
                "year": 7,
                "revenue": 2140,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 42.8,
                "capex": 53.09166667,
                "delta_nwc": 5.2
              },
              {
                "year": 8,
                "revenue": 2260,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 45.2,
                "capex": 55.98333333,
                "delta_nwc": 4.8
              },
              {
                "year": 9,
                "revenue": 2370,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 47.4,
                "capex": 58.9125,
                "delta_nwc": 4.4
              },
              {
                "year": 10,
                "revenue": 2465,
                "ebit_margin": 0.06,
                "tax_rate": 0.2,
                "da": 49.3,
                "capex": 61.93333333,
                "delta_nwc": 3.8
              }
            ],
            "terminal": {
              "growth": 0.025,
              "roic": 0.18,
              "margin": 0.06,
              "tax_rate": 0.2
            }
          },
          {
            "id": "internet",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "互联网H1收入185.12009亿元、同比1.9%、毛利率76.4%；全球MAU增4.8%不能直接当收入增速。40%–50% EBIT为研发、获客和总部费用后假设，不是披露分部EBIT。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.09,
            "years": [
              {
                "year": 1,
                "revenue": 410,
                "ebit_margin": 0.48,
                "tax_rate": 0.2,
                "da": 10.25,
                "capex": 12.3,
                "delta_nwc": 0.82
              },
              {
                "year": 2,
                "revenue": 443,
                "ebit_margin": 0.49,
                "tax_rate": 0.2,
                "da": 11.075,
                "capex": 13.29,
                "delta_nwc": 0.33
              },
              {
                "year": 3,
                "revenue": 478,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 11.95,
                "capex": 14.34,
                "delta_nwc": 0.35
              },
              {
                "year": 4,
                "revenue": 515,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 12.875,
                "capex": 15.45,
                "delta_nwc": 0.37
              },
              {
                "year": 5,
                "revenue": 554,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 13.85,
                "capex": 16.62,
                "delta_nwc": 0.39
              },
              {
                "year": 6,
                "revenue": 595,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 14.875,
                "capex": 17.85,
                "delta_nwc": 0.41
              },
              {
                "year": 7,
                "revenue": 637,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 15.925,
                "capex": 23.51708333,
                "delta_nwc": 0.42
              },
              {
                "year": 8,
                "revenue": 678,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 16.95,
                "capex": 29.74,
                "delta_nwc": 0.41
              },
              {
                "year": 9,
                "revenue": 716,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 17.9,
                "capex": 36.41,
                "delta_nwc": 0.38
              },
              {
                "year": 10,
                "revenue": 752,
                "ebit_margin": 0.5,
                "tax_rate": 0.2,
                "da": 18.8,
                "capex": 43.50666667,
                "delta_nwc": 0.36
              }
            ],
            "terminal": {
              "growth": 0.025,
              "roic": 0.3,
              "margin": 0.5,
              "tax_rate": 0.2
            }
          },
          {
            "id": "ev_ai",
            "source": "S1印11–13/78/80/95–96；B1§5.1；A-DCF",
            "assumptions": "汽车/AI/其他新业务H1收入447.60253亿元、交付185055辆、毛利率19.6%、经营亏损约57亿元；AI已有收入包含在本分部。亏损修复与规模扩张需要再投资，未另加独立AI/机器人许可价值。 D&A含使用权折旧；capex含新增使用权/递延付款形成的新资本，不含旧应付结算；正常SBC已在EBIT扣除，无FCFF加回。第7–10年再投资收敛到NOPAT×g/ROIC。 2027预测量只作估值日起首个12个月的代理，非宣称精确自然年度现金流。",
            "discount_rate": 0.09,
            "years": [
              {
                "year": 1,
                "revenue": 1200,
                "ebit_margin": 0,
                "tax_rate": 0.0,
                "da": 48.0,
                "capex": 78.0,
                "delta_nwc": 12.0
              },
              {
                "year": 2,
                "revenue": 1440,
                "ebit_margin": 0.02,
                "tax_rate": 0.2,
                "da": 57.6,
                "capex": 93.6,
                "delta_nwc": 19.2
              },
              {
                "year": 3,
                "revenue": 1700,
                "ebit_margin": 0.04,
                "tax_rate": 0.2,
                "da": 68.0,
                "capex": 110.5,
                "delta_nwc": 20.8
              },
              {
                "year": 4,
                "revenue": 1980,
                "ebit_margin": 0.055,
                "tax_rate": 0.2,
                "da": 79.2,
                "capex": 128.7,
                "delta_nwc": 22.4
              },
              {
                "year": 5,
                "revenue": 2280,
                "ebit_margin": 0.065,
                "tax_rate": 0.2,
                "da": 91.2,
                "capex": 148.2,
                "delta_nwc": 24.0
              },
              {
                "year": 6,
                "revenue": 2570,
                "ebit_margin": 0.07,
                "tax_rate": 0.2,
                "da": 102.8,
                "capex": 167.05,
                "delta_nwc": 23.2
              },
              {
                "year": 7,
                "revenue": 2840,
                "ebit_margin": 0.075,
                "tax_rate": 0.2,
                "da": 113.6,
                "capex": 168.55,
                "delta_nwc": 21.6
              },
              {
                "year": 8,
                "revenue": 3090,
                "ebit_margin": 0.08,
                "tax_rate": 0.2,
                "da": 123.6,
                "capex": 168.705,
                "delta_nwc": 20.0
              },
              {
                "year": 9,
                "revenue": 3300,
                "ebit_margin": 0.08,
                "tax_rate": 0.2,
                "da": 132.0,
                "capex": 166.425,
                "delta_nwc": 16.8
              },
              {
                "year": 10,
                "revenue": 3465,
                "ebit_margin": 0.08,
                "tax_rate": 0.2,
                "da": 138.6,
                "capex": 162.36,
                "delta_nwc": 13.2
              }
            ],
            "terminal": {
              "growth": 0.025,
              "roic": 0.15,
              "margin": 0.08,
              "tax_rate": 0.2
            }
          }
        ],
        "equity_adjustments": [
          {
            "id": "bank_assets",
            "amount": 1654.28714,
            "reason": "6/30现金等价物与两类定存；不含受限现金；仍含未拆分基金现金",
            "source": "S1印59/94"
          },
          {
            "id": "borrowings",
            "amount": -392.76762,
            "reason": "流动及非流动借款合计，含可转债；不另增转股分母",
            "source": "S1印60/100"
          },
          {
            "id": "lease_debt",
            "amount": -50.40762,
            "reason": "租赁融资口径；DCF的capex含未来新增使用权资产，旧租赁偿付不再进FCFF",
            "source": "S1印95–96"
          },
          {
            "id": "lp_liability_legacy_anchor",
            "amount": -142.3216,
            "reason": "只作可复算条件锚；须与基金现金及投资净归属一起替换，非假定基金资产零",
            "source": "S1印110"
          },
          {
            "id": "old_intangible_payables",
            "amount": -50.74695,
            "reason": "6/30已确认无形资产应付；年度capex只计估值后新增资本，排除这一存量结算",
            "source": "S1印110/112"
          },
          {
            "id": "old_construction_payables",
            "amount": -17.80532,
            "reason": "6/30已确认工程应付；从旧笼统储备中拆出，只扣一次",
            "source": "S1印112"
          },
          {
            "id": "minorities",
            "amount": -1.1949,
            "reason": "少数权益账面近似；未取得公允价值，固定跨模型比较",
            "source": "S1印60"
          },
          {
            "id": "post_june_buybacks",
            "amount": -15.78342954,
            "reason": "沿用截至10/28已核回购链合计HKD18.4398784226亿元×0.85594；不是回购授权全额",
            "source": "B1§5.2，S2/S3"
          },
          {
            "id": "minimum_operating_cash",
            "amount": -300.0,
            "reason": "条件假设：持续留存经营现金300亿元；250–400敏感性，不代表现金已损失；不含未来capex或ΔNWC",
            "source": "A-CASH；旧B1基准营运储备300亿元；本研究明确范围"
          },
          {
            "id": "fund_net_adjustment_condition",
            "amount": 0.0,
            "reason": "仅为条件C_f=142.3216、N_f=0、R_parent=0的算术锚；一般必须另加Δfund=-C_f+142.3216+N_f-R_parent；0不是已核事实",
            "source": "G-FUND；S1印89–91/110"
          },
          {
            "id": "unmodeled_nonbank_assets_condition",
            "amount": 0.0,
            "reason": "与旧比较一致的未估值资产占位；不证明投资资产价值为零。所有绝对股权值仅在该附加NAV=0条件下成立；另按净归属补充",
            "source": "G-NAV；S1印59/89–91"
          }
        ],
        "equity_value": 7352.242841242104
      }
    }
  },
  "baseline": null,
  "valuation_review": {
    "base_case": "同包条件截面；经营假设见inputs/evidence与assumptions；非概率中位数，资产归属仍未闭合",
    "method_choice": "这是模型实验，不是完整生产研究；本组严格采用valuation.kind所声明的资本化法或分业务FCFF，新增假设分拆披露。",
    "pe_crosscheck": "旧阿里普通股利润PE为12/15/18倍；旧小米是EV/NOPAT资本化16/18/20倍再除1.10，不得标为归母PE。本DCF基准经营EV=3096.4461亿元、Y1 NOPAT=140.0000亿元，隐含EV/NOPAT=22.1175倍；含恢复预期，非同业事实或正当性证明。",
    "market_check": {
      "price": 26.48,
      "as_of": "2026-10-30",
      "source": "冻结2026-10-31原始数据包",
      "explanation": "独立预测后反解；未闭合资金/投资NAV均条件化，市价不用于拟合基准"
    },
    "reverse_dcf": {
      "status": "solved",
      "reason": "冻结显式期与其它业务，仅反解指定业务终值利润率；不是唯一业务天花板",
      "cases": [
        {
          "scenario": "base",
          "segment_id": "ev_ai",
          "variable": "terminal_margin",
          "target_price": 26.48,
          "lower": 0,
          "upper": 0.5,
          "parameter": 0.3475217745902895,
          "modeled_price": 26.48,
          "residual": 0.0
        }
      ]
    }
  },
  "discounts": {
    "d_base": {
      "value": 0.3,
      "range": [
        0.3,
        0.3
      ],
      "risk_ids": [
        "d_base"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_chip": {
      "value": 0.03,
      "range": [
        0.03,
        0.03
      ],
      "risk_ids": [
        "r_chip"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_v5": {
      "value": 0.1,
      "range": [
        0.1,
        0.1
      ],
      "risk_ids": [
        "r_v5"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_gov": {
      "value": 0.03,
      "range": [
        0.03,
        0.03
      ],
      "risk_ids": [
        "r_gov"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_terminal": {
      "value": 0.08,
      "range": [
        0.08,
        0.08
      ],
      "risk_ids": [
        "r_terminal"
      ],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    }
  },
  "risks": [
    {
      "id": "d_base",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "d_base",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    },
    {
      "id": "r_chip",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_chip",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    },
    {
      "id": "r_v5",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_v5",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    },
    {
      "id": "r_gov",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_gov",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    },
    {
      "id": "r_terminal",
      "description": "固定旧折扣作算术控制；是否与DCF重复须见未决项",
      "owner": "r_terminal",
      "scope": "此审计仅证明算术；旧风险未量化无法声称经济去重完成",
      "source": "同日/最近正式Codex报告§7，inputs/evidence定位"
    }
  ],
  "constraints": [
    {
      "id": "CAPITAL_UNRESOLVED",
      "scope": [
        "entry",
        "add"
      ],
      "action": "eligibility",
      "status": "unknown",
      "lifecycle": "persistent",
      "reason": "现金与投资净归属缺口；隔离实验无正式资格裁决",
      "release_conditions": [
        "核实资本桥并完整复评"
      ]
    },
    {
      "id": "HOLDING_NOT_REASSESSED",
      "scope": [
        "holding"
      ],
      "action": "review_holding",
      "status": "unknown",
      "lifecycle": "persistent",
      "reason": "隔离估值实验未形成新的持仓判断",
      "release_conditions": [
        "完成持仓逻辑复评"
      ]
    }
  ],
  "release_all_of": {
    "entry": [
      "CAPITAL_UNRESOLVED"
    ],
    "add": [
      "CAPITAL_UNRESOLVED"
    ],
    "holding": [
      "HOLDING_NOT_REASSESSED"
    ]
  },
  "p1_basis": {
    "base": "base"
  }
}
```
<!-- research-audit:end -->

</details>
