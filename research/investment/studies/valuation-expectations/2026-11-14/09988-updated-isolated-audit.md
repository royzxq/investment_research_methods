# 隔离算术审计，不是正式投研交付

保留旧折扣作控制变量，算术通过不证明折扣经济独立；未运行完整Gate/来源验收，不可发布。

<!-- research-checks:start -->
研究一致性核算（金额为模型币种亿元，价格为报价币种/股）：

| 情景 | 经营价值 | 权益调整 | 权益价值 | V50 |
|---|---:|---:|---:|---:|
| low | 3918.6380104196340580122448385060720371390071225599 | 2318.79718 | 6237.4351904196340580122448385060720371390071225599 | 36.616 |
| base | 12385.555292890081297167683959072009238638993759311 | 3631.43118 | 16016.986472890081297167683959072009238638993759311 | 94.025 |
| high | 25689.28804013709163464029871142101810298549681483 | 4944.06518 | 30633.35322013709163464029871142101810298549681483 | 179.827 |

| 情景 | 分部 | 年 | NOPAT | FCFF | 现值 |
|---|---|---:|---:|---:|---:|
| low | ecommerce | 1 | 922.500000 | 865.789600 | 779.990631 |
| low | ecommerce | 2 | 940.950000 | 854.030000 | 693.149907 |
| low | ecommerce | 3 | 991.761300 | 886.040340 | 647.865060 |
| low | ecommerce | 4 | 1044.228672 | 927.691387 | 611.099051 |
| low | ecommerce | 5 | 1098.398034 | 970.654060 | 576.035941 |
| low | ecommerce | 6 | 1154.316480 | 1024.017627 | 547.481640 |
| low | ecommerce | 7 | 1171.631227 | 1040.265484 | 501.052620 |
| low | ecommerce | 8 | 1189.205695 | 1055.869467 | 458.169739 |
| low | ecommerce | 9 | 1207.043781 | 1071.707510 | 418.957013 |
| low | ecommerce | 10 | 1225.149437 | 1102.634494 | 388.330755 |
| low | ai_cloud_labs | 1 | -497.040000 | -2294.668000 | -2030.679646 |
| low | ai_cloud_labs | 2 | -514.436400 | -1979.461800 | -1550.208944 |
| low | ai_cloud_labs | 3 | -448.131264 | -1415.271696 | -980.854279 |
| low | ai_cloud_labs | 4 | -352.103136 | -957.080342 | -586.995298 |
| low | ai_cloud_labs | 5 | -228.162832 | -499.986453 | -271.372615 |
| low | ai_cloud_labs | 6 | -80.617534 | -206.107092 | -98.997055 |
| low | ai_cloud_labs | 7 | 31.440838 | -13.704980 | -5.825448 |
| low | ai_cloud_labs | 8 | 80.960159 | 35.266140 | 13.265706 |
| low | ai_cloud_labs | 9 | 115.611106 | 69.841629 | 23.249219 |
| low | ai_cloud_labs | 10 | 133.448249 | 116.767217 | 34.398261 |
| low | other_corporate_eliminations | 1 | -202.500000 | -204.697200 | -181.147965 |
| low | other_corporate_eliminations | 2 | -189.000000 | -191.250000 | -149.776803 |
| low | other_corporate_eliminations | 3 | -171.000000 | -173.250000 | -120.070941 |
| low | other_corporate_eliminations | 4 | -144.000000 | -146.250000 | -89.697864 |
| low | other_corporate_eliminations | 5 | -112.500000 | -114.750000 | -62.281703 |
| low | other_corporate_eliminations | 6 | -81.000000 | -83.250000 | -39.986517 |
| low | other_corporate_eliminations | 7 | -54.000000 | -56.250000 | -23.909661 |
| low | other_corporate_eliminations | 8 | -36.000000 | -38.250000 | -14.388115 |
| low | other_corporate_eliminations | 9 | -18.000000 | -20.250000 | -6.740918 |
| low | other_corporate_eliminations | 10 | 0.000000 | 0.000000 | 0.000000 |
| base | ecommerce | 1 | 1083.750000 | 1018.939600 | 926.308727 |
| base | ecommerce | 2 | 1160.250000 | 1065.050000 | 880.206612 |
| base | ecommerce | 3 | 1241.136000 | 1123.740800 | 844.283095 |
| base | ecommerce | 4 | 1320.258420 | 1190.123012 | 812.870031 |
| base | ecommerce | 5 | 1396.619312 | 1253.698364 | 778.448047 |
| base | ecommerce | 6 | 1438.517892 | 1291.309316 | 728.910444 |
| base | ecommerce | 7 | 1474.480839 | 1324.572132 | 679.714943 |
| base | ecommerce | 8 | 1503.970456 | 1352.073061 | 630.752061 |
| base | ecommerce | 9 | 1534.049865 | 1379.114523 | 584.879185 |
| base | ecommerce | 10 | 1564.730862 | 1408.257775 | 542.944335 |
| base | ai_cloud_labs | 1 | -403.845000 | -2112.420000 | -1886.089286 |
| base | ai_cloud_labs | 2 | -336.537500 | -1763.456500 | -1405.816725 |
| base | ai_cloud_labs | 3 | -161.538000 | -1063.458500 | -756.948755 |
| base | ai_cloud_labs | 4 | 70.269030 | -411.114210 | -261.270513 |
| base | ai_cloud_labs | 5 | 236.103941 | 67.458269 | 38.277633 |
| base | ai_cloud_labs | 6 | 386.029943 | 376.585785 | 190.790079 |
| base | ai_cloud_labs | 7 | 504.841381 | 558.027729 | 252.423405 |
| base | ai_cloud_labs | 8 | 578.272855 | 572.153566 | 231.083229 |
| base | ai_cloud_labs | 9 | 598.512405 | 527.513349 | 190.226602 |
| base | ai_cloud_labs | 10 | 610.482653 | 508.735544 | 163.799230 |
| base | other_corporate_eliminations | 1 | -161.000000 | -163.447200 | -145.935000 |
| base | other_corporate_eliminations | 2 | -140.760000 | -143.290000 | -114.229911 |
| base | other_corporate_eliminations | 3 | -114.860160 | -117.440760 | -83.592013 |
| base | other_corporate_eliminations | 4 | -87.868022 | -90.500235 | -57.514536 |
| base | other_corporate_eliminations | 5 | -59.750255 | -62.435111 | -35.427359 |
| base | other_corporate_eliminations | 6 | -30.472630 | -33.211184 | -16.825819 |
| base | other_corporate_eliminations | 7 | 0.000000 | -2.793325 | -1.263558 |
| base | other_corporate_eliminations | 8 | 11.888897 | 9.039706 | 3.650986 |
| base | other_corporate_eliminations | 9 | 20.211124 | 17.304949 | 6.240338 |
| base | other_corporate_eliminations | 10 | 24.738416 | 19.790733 | 6.372086 |
| high | ecommerce | 1 | 1254.000000 | 1181.089600 | 1083.568440 |
| high | ecommerce | 2 | 1364.220000 | 1260.380000 | 1060.836630 |
| high | ecommerce | 3 | 1483.152000 | 1353.306240 | 1045.000722 |
| high | ecommerce | 4 | 1596.242340 | 1451.387828 | 1028.199728 |
| high | ecommerce | 5 | 1708.757959 | 1547.524505 | 1005.784747 |
| high | ecommerce | 6 | 1819.420379 | 1652.775793 | 985.496204 |
| high | ecommerce | 7 | 1926.893117 | 1755.500897 | 960.319108 |
| high | ecommerce | 8 | 1984.699911 | 1809.294247 | 908.023773 |
| high | ecommerce | 9 | 2034.317409 | 1855.694417 | 854.413260 |
| high | ecommerce | 10 | 2085.175344 | 1876.657810 | 792.720540 |
| high | ai_cloud_labs | 1 | -289.940000 | -2017.154000 | -1817.255856 |
| high | ai_cloud_labs | 2 | -113.076600 | -1600.468800 | -1298.976382 |
| high | ai_cloud_labs | 3 | 176.682188 | -925.814662 | -676.947702 |
| high | ai_cloud_labs | 4 | 424.037250 | -216.730150 | -142.766863 |
| high | ai_cloud_labs | 5 | 688.636494 | 342.622098 | 203.329539 |
| high | ai_cloud_labs | 6 | 936.545632 | 700.441691 | 374.484731 |
| high | ai_cloud_labs | 7 | 1140.932943 | 967.580182 | 466.043133 |
| high | ai_cloud_labs | 8 | 1273.040968 | 1093.694317 | 474.582943 |
| high | ai_cloud_labs | 9 | 1323.962607 | 1140.644707 | 445.906271 |
| high | ai_cloud_labs | 10 | 1357.061672 | 1168.580883 | 411.556049 |
| high | other_corporate_eliminations | 1 | -117.500000 | -120.197200 | -108.285766 |
| high | other_corporate_eliminations | 2 | -73.320000 | -76.140000 | -61.796932 |
| high | other_corporate_eliminations | 3 | -25.417600 | -28.350400 | -20.729568 |
| high | other_corporate_eliminations | 4 | 7.930291 | 4.880178 | 3.214725 |
| high | other_corporate_eliminations | 5 | 24.623554 | 21.517524 | 12.769603 |
| high | other_corporate_eliminations | 6 | 33.816348 | 30.670005 | 16.397437 |
| high | other_corporate_eliminations | 7 | 43.327196 | 40.156912 | 19.341915 |
| high | other_corporate_eliminations | 8 | 44.193739 | 41.016412 | 17.798108 |
| high | other_corporate_eliminations | 9 | 45.077614 | 41.836740 | 16.355018 |
| high | other_corporate_eliminations | 10 | 45.979167 | 38.315973 | 13.494291 |

| 情景 | 分部 | 显式期现值 | 终值首年NOPAT | 终值再投资 | 终值现值 |
|---|---|---:|---:|---:|---:|
| low | ecommerce | 5622.132356 | 1243.526679 | 124.352668 | 4149.007534 |
| low | ai_cloud_labs | -5454.020097 | 134.782731 | 16.847841 | 289.518703 |
| low | other_corporate_eliminations | -688.000486 | 0.000000 | 0.000000 | 0.000000 |
| base | ecommerce | 7409.317480 | 1596.025479 | 159.602548 | 6922.540275 |
| base | ai_cloud_labs | -3243.525100 | 622.692306 | 103.782051 | 1670.752143 |
| base | other_corporate_eliminations | -438.524786 | 25.233185 | 5.046637 | 64.995281 |
| high | ecommerce | 9724.363151 | 2137.304728 | 213.730473 | 12500.593125 |
| high | ai_cloud_labs | -1560.044135 | 1390.988214 | 193.192807 | 4962.881775 |
| high | other_corporate_eliminations | -91.441169 | 46.898750 | 7.816458 | 152.935294 |

估值假设与市价差异（检查声明及算术，不证明预测正确）：
- base_case：同包条件截面；经营假设见inputs/evidence与assumptions；非概率中位数，资产归属仍未闭合
- method_choice：这是模型实验，不是完整生产研究；本组严格采用valuation.kind所声明的资本化法或分业务FCFF，新增假设分拆披露。
- pe_crosscheck：旧阿里普通股利润PE为12/15/18倍；旧小米是EV/NOPAT资本化16/18/20倍再除1.10，不得标为归母PE。本DCF基准经营EV=12385.5553亿元、Y1 NOPAT=518.9050亿元，隐含EV/NOPAT=23.8686倍；含恢复预期，非同业事实或正当性证明。
- 市价核对：{"as_of": "2026-10-30", "explanation": "独立预测后反解；未闭合资金/投资NAV均条件化，市价不用于拟合基准", "price": 97.05, "source": "冻结2026-10-31原始数据包"}
- 反向DCF条件解：{"cases": [{"lower": 0, "modeled_price": 97.05, "parameter": 0.1570157381282522, "residual": 2e-48, "scenario": "base", "segment_id": "ai_cloud_labs", "target_price": 97.05, "upper": 0.5, "variable": "terminal_margin"}], "reason": "冻结显式期与其它业务，仅反解指定业务终值利润率；不是唯一业务天花板", "status": "solved"}

| 折扣 | 取值 | 论证区间 | 独占风险ID | 变化分类 |
|---|---:|---|---|---|
| d_base | 25% | 25%—25% | d_base | initial |
| r_chip | 0% | 0%—0% | 无额外扣减 | initial |
| r_v5 | 0% | 0%—0% | 无额外扣减 | initial |
| r_gov | 0% | 0%—0% | 无额外扣减 | initial |
| r_terminal | 0% | 0%—0% | 无额外扣减 | initial |

总折扣乘数：0.75；用途：tracking。
明确报价：P1={"base": 70.518}；T1={"price_condition": "接近V50上沿时复核"}。

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
    "code": "09988.HK",
    "generator": "codex",
    "valuation_date": "2026-10-31",
    "currency": "HKD"
  },
  "valuation": {
    "kind": "dcf_fcff",
    "currency": "CNY",
    "amount_unit": "100_million",
    "shares": 19901959514,
    "fx_to_quote": 1.1683061896861928,
    "scenarios": {
      "low": {
        "segments": [
          {
            "id": "ecommerce",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-10. E-commerce combines domestic, quick commerce, international and wholesale; Q1 annualized revenue 8234.48. Year1 sales 8200/8500/8800 are assumptions around this run-rate, not an annual forecast from management. EBIT margins include economic SBC, ordinary intangible amortization and lease expense; later margin/growth changes are research forecasts. DA 1.8% revenue and capex 2.5%-3.4% are allocation assumptions; no segment capex disclosure.",
            "discount_rate": 0.11,
            "years": [
              {
                "year": 1,
                "revenue": 8200,
                "ebit_margin": 0.15,
                "tax_rate": 0.25,
                "da": 147.6,
                "capex": 205.0,
                "delta_nwc": -0.6896
              },
              {
                "year": 2,
                "revenue": 8364.0,
                "ebit_margin": 0.15,
                "tax_rate": 0.25,
                "da": 150.552,
                "capex": 234.192,
                "delta_nwc": 3.28
              },
              {
                "year": 3,
                "revenue": 8531.28,
                "ebit_margin": 0.155,
                "tax_rate": 0.25,
                "da": 153.56304,
                "capex": 255.9384,
                "delta_nwc": 3.3456
              },
              {
                "year": 4,
                "revenue": 8701.9056,
                "ebit_margin": 0.16,
                "tax_rate": 0.25,
                "da": 156.634301,
                "capex": 269.759074,
                "delta_nwc": 3.412512
              },
              {
                "year": 5,
                "revenue": 8875.943712,
                "ebit_margin": 0.165,
                "tax_rate": 0.25,
                "da": 159.766987,
                "capex": 284.030199,
                "delta_nwc": 3.480762
              },
              {
                "year": 6,
                "revenue": 9053.462586,
                "ebit_margin": 0.17,
                "tax_rate": 0.25,
                "da": 162.962327,
                "capex": 289.710803,
                "delta_nwc": 3.550377
              },
              {
                "year": 7,
                "revenue": 9189.264525,
                "ebit_margin": 0.17,
                "tax_rate": 0.25,
                "da": 165.406761,
                "capex": 294.056465,
                "delta_nwc": 2.716039
              },
              {
                "year": 8,
                "revenue": 9327.103493,
                "ebit_margin": 0.17,
                "tax_rate": 0.25,
                "da": 167.887863,
                "capex": 298.467312,
                "delta_nwc": 2.756779
              },
              {
                "year": 9,
                "revenue": 9467.010045,
                "ebit_margin": 0.17,
                "tax_rate": 0.25,
                "da": 170.406181,
                "capex": 302.944321,
                "delta_nwc": 2.798131
              },
              {
                "year": 10,
                "revenue": 9609.015196,
                "ebit_margin": 0.17,
                "tax_rate": 0.25,
                "da": 172.962274,
                "capex": 292.637114,
                "delta_nwc": 2.840103
              }
            ],
            "terminal": {
              "growth": 0.015,
              "roic": 0.15,
              "margin": 0.17,
              "tax_rate": 0.25
            }
          },
          {
            "id": "ai_cloud_labs",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-10. Cloud plus AI Labs eliminates an unsupported separation between AI infrastructure benefit and model/app cost. Q1 combined revenue 517.75 and EBITA -82.33; annualized revenue 2071.00. Year1 +20/30/40% and decelerating growth are below or near the latest 45% cloud growth; recovery margins require utilization/pricing and Labs cost absorption. DA and capex are explicit allocation assumptions constrained by S1 group capex and S5 computer lives 3-5 years; no company ten-year plan is claimed.",
            "discount_rate": 0.13,
            "years": [
              {
                "year": 1,
                "revenue": 2485.2,
                "ebit_margin": -0.2,
                "tax_rate": 0.0,
                "da": 447.336,
                "capex": 2236.68,
                "delta_nwc": 8.284
              },
              {
                "year": 2,
                "revenue": 2857.98,
                "ebit_margin": -0.18,
                "tax_rate": 0.0,
                "da": 685.9152,
                "capex": 2143.485,
                "delta_nwc": 7.4556
              },
              {
                "year": 3,
                "revenue": 3200.9376,
                "ebit_margin": -0.14,
                "tax_rate": 0.0,
                "da": 960.28128,
                "capex": 1920.56256,
                "delta_nwc": 6.859152
              },
              {
                "year": 4,
                "revenue": 3521.03136,
                "ebit_margin": -0.1,
                "tax_rate": 0.0,
                "da": 1161.940349,
                "capex": 1760.51568,
                "delta_nwc": 6.401875
              },
              {
                "year": 5,
                "revenue": 3802.713869,
                "ebit_margin": -0.06,
                "tax_rate": 0.0,
                "da": 1254.895577,
                "capex": 1521.085548,
                "delta_nwc": 5.63365
              },
              {
                "year": 6,
                "revenue": 4030.876701,
                "ebit_margin": -0.02,
                "tax_rate": 0.0,
                "da": 1209.26301,
                "capex": 1330.189311,
                "delta_nwc": 4.563257
              },
              {
                "year": 7,
                "revenue": 4192.111769,
                "ebit_margin": 0.01,
                "tax_rate": 0.25,
                "da": 1131.870178,
                "capex": 1173.791295,
                "delta_nwc": 3.224701
              },
              {
                "year": 8,
                "revenue": 4317.875122,
                "ebit_margin": 0.025,
                "tax_rate": 0.25,
                "da": 1036.290029,
                "capex": 1079.468781,
                "delta_nwc": 2.515267
              },
              {
                "year": 9,
                "revenue": 4404.232624,
                "ebit_margin": 0.035,
                "tax_rate": 0.25,
                "da": 968.931177,
                "capex": 1012.973504,
                "delta_nwc": 1.72715
              },
              {
                "year": 10,
                "revenue": 4448.274951,
                "ebit_margin": 0.04,
                "tax_rate": 0.25,
                "da": 889.65499,
                "capex": 905.455175,
                "delta_nwc": 0.880847
              }
            ],
            "terminal": {
              "growth": 0.01,
              "roic": 0.08,
              "margin": 0.04,
              "tax_rate": 0.25
            }
          },
          {
            "id": "other_corporate_eliminations",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-8. Residual is All Others + Unallocated + intersegment eliminations, not a reported standalone business. Q1 net revenue 113.16 and adjusted EBITA -41.87. This preserves group totals and keeps elimination costs. A more negative initial margin than the old group estimate and later loss reduction are assumptions; segment-internal sales mix is unknown. Margin interpretation is accounting-residual only, not industry comparison.",
            "discount_rate": 0.13,
            "years": [
              {
                "year": 1,
                "revenue": 450,
                "ebit_margin": -0.45,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": -0.0528
              },
              {
                "year": 2,
                "revenue": 450,
                "ebit_margin": -0.42,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 3,
                "revenue": 450,
                "ebit_margin": -0.38,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 4,
                "revenue": 450,
                "ebit_margin": -0.32,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 5,
                "revenue": 450,
                "ebit_margin": -0.25,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 6,
                "revenue": 450,
                "ebit_margin": -0.18,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 7,
                "revenue": 450,
                "ebit_margin": -0.12,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 8,
                "revenue": 450,
                "ebit_margin": -0.08,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 9,
                "revenue": 450,
                "ebit_margin": -0.04,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 15.75,
                "delta_nwc": 0.0
              },
              {
                "year": 10,
                "revenue": 450,
                "ebit_margin": 0,
                "tax_rate": 0.0,
                "da": 13.5,
                "capex": 13.5,
                "delta_nwc": 0.0
              }
            ],
            "terminal": {
              "growth": 0,
              "roic": 0.08,
              "margin": 0,
              "tax_rate": 0.25
            }
          }
        ],
        "equity_adjustments": [
          {
            "id": "june_unrestricted_cash_treasury",
            "amount": 4745.05,
            "reason": "6/30 unrestricted cash plus treasury, already includes long-dated deposits/securities; excludes 425.85 restricted cash",
            "source": "S1 pp15,20"
          },
          {
            "id": "post_june_completed_placement",
            "amount": 682.18418,
            "reason": "Completed 8/26; translate approximate HKD79.7 billion net amount (797亿元HKD) at common cutoff fixing; actual settlement FX unavailable, capital purpose is AI capex not discretionary dividend",
            "source": "S2 p2; S9"
          },
          {
            "id": "post_june_cash_burn_estimate",
            "amount": -893.4,
            "reason": "Unverified Jul-Oct cash-burn assumption = June company FCF outflow 446.70 x 4/3 x 1.5; excludes separately listed dividend and fines. Not the September reported result. Future years start 11/1 so no period overlap.",
            "source": "S1 p26 plus research assumption"
          },
          {
            "id": "post_june_declared_dividend",
            "amount": -167.845,
            "reason": "FY2026 dividend expected in July, after June cash date. Reserve approximate USD2.5bn regardless of settlement timing; exact payment/FX not verified. Do not also deduct dividend payable.",
            "source": "S4 pp5-6; S9"
          },
          {
            "id": "regulatory_cash_obligation_range_reserve",
            "amount": -63,
            "reason": "Conservative conditional reserve63 for own USD325m and EUR550m (cutoff translation62.95545). Actual payment or any overlap withJune30 cash/estimated burn unknown. Range0-63 means amount still absent from the starting cash/burn ledger, not uncertainty about the legal amounts. Deduct once as post-June use OR outstanding obligation, never both.",
            "source": "S10/S11 original official releases; S1 p13 EC provision"
          },
          {
            "id": "unreconstructed_post_june_changes_X",
            "amount": 0,
            "reason": "Conditional algebra uses X=0 solely to make unresolved cash change explicit; actual X is unknown and not asserted zero. Includes un-reconstructed buybacks, FX, acquisitions and net debt changes. Subtract actual net outflow X from resulting equity value; no unsupported fixed allowance substituted for missing records.",
            "source": "research assumption; S7 titles show July buybacks not fully reconstructed"
          },
          {
            "id": "operating_cash_retention",
            "amount": -500,
            "reason": "Permanent operating liquidity reserve; low/base/high 500/400/300 (~3%-5% of current sales), not reported restricted cash; future NWC excludes cash. Must not be confused with deducting future capex again.",
            "source": "research assumption supported by S1 cash-burn risk"
          },
          {
            "id": "june_interest_bearing_debt",
            "amount": -2665.3,
            "reason": "Five balance-sheet debt lines; use debt treatment for convertibles. No extra if-converted shares. Subsequent net debt changes unresolved.",
            "source": "S1 pp20-21"
          },
          {
            "id": "noncash_financial_investments",
            "amount": 1829.668,
            "reason": "Noncash financial investment book 4574.17 = equities/other 4311.48 - liquid treasury already included 1769.38 + equity method2032.07; recoverability 40%. Includes Ant, so do not add separate Ant NAV. Haircut is an assumption, not observed market value.",
            "source": "S1 pp20-21; S5 p215"
          },
          {
            "id": "noncontrolling_and_mezzanine",
            "amount": -648.56,
            "reason": "Group FCFF includes NCI; deduct NCI572.72 plus mezzanine75.84 at book proxy. Fair-value NCI not independently estimated, +/-20% sensitivity necessary; no NCI earnings deduction inside consolidated EBIT.",
            "source": "S1 p21"
          }
        ],
        "equity_value": 6237.435190419634
      },
      "base": {
        "segments": [
          {
            "id": "ecommerce",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-10. E-commerce combines domestic, quick commerce, international and wholesale; Q1 annualized revenue 8234.48. Year1 sales 8200/8500/8800 are assumptions around this run-rate, not an annual forecast from management. EBIT margins include economic SBC, ordinary intangible amortization and lease expense; later margin/growth changes are research forecasts. DA 1.8% revenue and capex 2.5%-3.4% are allocation assumptions; no segment capex disclosure.",
            "discount_rate": 0.1,
            "years": [
              {
                "year": 1,
                "revenue": 8500,
                "ebit_margin": 0.17,
                "tax_rate": 0.25,
                "da": 153.0,
                "capex": 212.5,
                "delta_nwc": 5.3104
              },
              {
                "year": 2,
                "revenue": 8840.0,
                "ebit_margin": 0.175,
                "tax_rate": 0.25,
                "da": 159.12,
                "capex": 247.52,
                "delta_nwc": 6.8
              },
              {
                "year": 3,
                "revenue": 9193.6,
                "ebit_margin": 0.18,
                "tax_rate": 0.25,
                "da": 165.4848,
                "capex": 275.808,
                "delta_nwc": 7.072
              },
              {
                "year": 4,
                "revenue": 9515.376,
                "ebit_margin": 0.185,
                "tax_rate": 0.25,
                "da": 171.276768,
                "capex": 294.976656,
                "delta_nwc": 6.43552
              },
              {
                "year": 5,
                "revenue": 9800.83728,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 176.415071,
                "capex": 313.626793,
                "delta_nwc": 5.709226
              },
              {
                "year": 6,
                "revenue": 10094.862398,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 181.707523,
                "capex": 323.035597,
                "delta_nwc": 5.880502
              },
              {
                "year": 7,
                "revenue": 10347.233958,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 186.250211,
                "capex": 331.111487,
                "delta_nwc": 5.047431
              },
              {
                "year": 8,
                "revenue": 10554.178638,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 189.975215,
                "capex": 337.733716,
                "delta_nwc": 4.138894
              },
              {
                "year": 9,
                "revenue": 10765.26221,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 193.77472,
                "capex": 344.488391,
                "delta_nwc": 4.221671
              },
              {
                "year": 10,
                "revenue": 10980.567454,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 197.650214,
                "capex": 349.817196,
                "delta_nwc": 4.306105
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.2,
              "margin": 0.19,
              "tax_rate": 0.25
            }
          },
          {
            "id": "ai_cloud_labs",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-10. Cloud plus AI Labs eliminates an unsupported separation between AI infrastructure benefit and model/app cost. Q1 combined revenue 517.75 and EBITA -82.33; annualized revenue 2071.00. Year1 +20/30/40% and decelerating growth are below or near the latest 45% cloud growth; recovery margins require utilization/pricing and Labs cost absorption. DA and capex are explicit allocation assumptions constrained by S1 group capex and S5 computer lives 3-5 years; no company ten-year plan is claimed.",
            "discount_rate": 0.12,
            "years": [
              {
                "year": 1,
                "revenue": 2692.3,
                "ebit_margin": -0.15,
                "tax_rate": 0.0,
                "da": 457.691,
                "capex": 2153.84,
                "delta_nwc": 12.426
              },
              {
                "year": 2,
                "revenue": 3365.375,
                "ebit_margin": -0.1,
                "tax_rate": 0.0,
                "da": 774.03625,
                "capex": 2187.49375,
                "delta_nwc": 13.4615
              },
              {
                "year": 3,
                "revenue": 4038.45,
                "ebit_margin": -0.04,
                "tax_rate": 0.0,
                "da": 1130.766,
                "capex": 2019.225,
                "delta_nwc": 13.4615
              },
              {
                "year": 4,
                "revenue": 4684.602,
                "ebit_margin": 0.02,
                "tax_rate": 0.25,
                "da": 1405.3806,
                "capex": 1873.8408,
                "delta_nwc": 12.92304
              },
              {
                "year": 5,
                "revenue": 5246.75424,
                "ebit_margin": 0.06,
                "tax_rate": 0.25,
                "da": 1521.55873,
                "capex": 1678.961357,
                "delta_nwc": 11.243045
              },
              {
                "year": 6,
                "revenue": 5718.962122,
                "ebit_margin": 0.09,
                "tax_rate": 0.25,
                "da": 1544.119773,
                "capex": 1544.119773,
                "delta_nwc": 9.444158
              },
              {
                "year": 7,
                "revenue": 6119.28947,
                "ebit_margin": 0.11,
                "tax_rate": 0.25,
                "da": 1468.629473,
                "capex": 1407.436578,
                "delta_nwc": 8.006547
              },
              {
                "year": 8,
                "revenue": 6425.253944,
                "ebit_margin": 0.12,
                "tax_rate": 0.25,
                "da": 1349.303328,
                "capex": 1349.303328,
                "delta_nwc": 6.119289
              },
              {
                "year": 9,
                "revenue": 6650.137832,
                "ebit_margin": 0.12,
                "tax_rate": 0.25,
                "da": 1263.526188,
                "capex": 1330.027566,
                "delta_nwc": 4.497678
              },
              {
                "year": 10,
                "revenue": 6783.140588,
                "ebit_margin": 0.12,
                "tax_rate": 0.25,
                "da": 1220.965306,
                "capex": 1320.05236,
                "delta_nwc": 2.660055
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.12,
              "margin": 0.12,
              "tax_rate": 0.25
            }
          },
          {
            "id": "other_corporate_eliminations",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-8. Residual is All Others + Unallocated + intersegment eliminations, not a reported standalone business. Q1 net revenue 113.16 and adjusted EBITA -41.87. This preserves group totals and keeps elimination costs. A more negative initial margin than the old group estimate and later loss reduction are assumptions; segment-internal sales mix is unknown. Margin interpretation is accounting-residual only, not industry comparison.",
            "discount_rate": 0.12,
            "years": [
              {
                "year": 1,
                "revenue": 460,
                "ebit_margin": -0.35,
                "tax_rate": 0.0,
                "da": 13.8,
                "capex": 16.1,
                "delta_nwc": 0.1472
              },
              {
                "year": 2,
                "revenue": 469.2,
                "ebit_margin": -0.3,
                "tax_rate": 0.0,
                "da": 14.076,
                "capex": 16.422,
                "delta_nwc": 0.184
              },
              {
                "year": 3,
                "revenue": 478.584,
                "ebit_margin": -0.24,
                "tax_rate": 0.0,
                "da": 14.35752,
                "capex": 16.75044,
                "delta_nwc": 0.18768
              },
              {
                "year": 4,
                "revenue": 488.15568,
                "ebit_margin": -0.18,
                "tax_rate": 0.0,
                "da": 14.64467,
                "capex": 17.085449,
                "delta_nwc": 0.191434
              },
              {
                "year": 5,
                "revenue": 497.918794,
                "ebit_margin": -0.12,
                "tax_rate": 0.0,
                "da": 14.937564,
                "capex": 17.427158,
                "delta_nwc": 0.195262
              },
              {
                "year": 6,
                "revenue": 507.877169,
                "ebit_margin": -0.06,
                "tax_rate": 0.0,
                "da": 15.236315,
                "capex": 17.775701,
                "delta_nwc": 0.199168
              },
              {
                "year": 7,
                "revenue": 518.034713,
                "ebit_margin": 0,
                "tax_rate": 0.0,
                "da": 15.541041,
                "capex": 18.131215,
                "delta_nwc": 0.203151
              },
              {
                "year": 8,
                "revenue": 528.395407,
                "ebit_margin": 0.03,
                "tax_rate": 0.25,
                "da": 15.851862,
                "capex": 18.493839,
                "delta_nwc": 0.207214
              },
              {
                "year": 9,
                "revenue": 538.963315,
                "ebit_margin": 0.05,
                "tax_rate": 0.25,
                "da": 16.168899,
                "capex": 18.863716,
                "delta_nwc": 0.211358
              },
              {
                "year": 10,
                "revenue": 549.742582,
                "ebit_margin": 0.06,
                "tax_rate": 0.25,
                "da": 16.492277,
                "capex": 21.224375,
                "delta_nwc": 0.215585
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.1,
              "margin": 0.06,
              "tax_rate": 0.25
            }
          }
        ],
        "equity_adjustments": [
          {
            "id": "june_unrestricted_cash_treasury",
            "amount": 4745.05,
            "reason": "6/30 unrestricted cash plus treasury, already includes long-dated deposits/securities; excludes 425.85 restricted cash",
            "source": "S1 pp15,20"
          },
          {
            "id": "post_june_completed_placement",
            "amount": 682.18418,
            "reason": "Completed 8/26; translate approximate HKD79.7 billion net amount (797亿元HKD) at common cutoff fixing; actual settlement FX unavailable, capital purpose is AI capex not discretionary dividend",
            "source": "S2 p2; S9"
          },
          {
            "id": "post_june_cash_burn_estimate",
            "amount": -595.6,
            "reason": "Unverified Jul-Oct cash-burn assumption = June company FCF outflow 446.70 x 4/3 x 1.0; excludes separately listed dividend and fines. Not the September reported result. Future years start 11/1 so no period overlap.",
            "source": "S1 p26 plus research assumption"
          },
          {
            "id": "post_june_declared_dividend",
            "amount": -167.845,
            "reason": "FY2026 dividend expected in July, after June cash date. Reserve approximate USD2.5bn regardless of settlement timing; exact payment/FX not verified. Do not also deduct dividend payable.",
            "source": "S4 pp5-6; S9"
          },
          {
            "id": "regulatory_cash_obligation_range_reserve",
            "amount": -63,
            "reason": "Conservative conditional reserve63 for own USD325m and EUR550m (cutoff translation62.95545). Actual payment or any overlap withJune30 cash/estimated burn unknown. Range0-63 means amount still absent from the starting cash/burn ledger, not uncertainty about the legal amounts. Deduct once as post-June use OR outstanding obligation, never both.",
            "source": "S10/S11 original official releases; S1 p13 EC provision"
          },
          {
            "id": "unreconstructed_post_june_changes_X",
            "amount": 0,
            "reason": "Conditional algebra uses X=0 solely to make unresolved cash change explicit; actual X is unknown and not asserted zero. Includes un-reconstructed buybacks, FX, acquisitions and net debt changes. Subtract actual net outflow X from resulting equity value; no unsupported fixed allowance substituted for missing records.",
            "source": "research assumption; S7 titles show July buybacks not fully reconstructed"
          },
          {
            "id": "operating_cash_retention",
            "amount": -400,
            "reason": "Permanent operating liquidity reserve; low/base/high 500/400/300 (~3%-5% of current sales), not reported restricted cash; future NWC excludes cash. Must not be confused with deducting future capex again.",
            "source": "research assumption supported by S1 cash-burn risk"
          },
          {
            "id": "june_interest_bearing_debt",
            "amount": -2665.3,
            "reason": "Five balance-sheet debt lines; use debt treatment for convertibles. No extra if-converted shares. Subsequent net debt changes unresolved.",
            "source": "S1 pp20-21"
          },
          {
            "id": "noncash_financial_investments",
            "amount": 2744.502,
            "reason": "Noncash financial investment book 4574.17 = equities/other 4311.48 - liquid treasury already included 1769.38 + equity method2032.07; recoverability 60%. Includes Ant, so do not add separate Ant NAV. Haircut is an assumption, not observed market value.",
            "source": "S1 pp20-21; S5 p215"
          },
          {
            "id": "noncontrolling_and_mezzanine",
            "amount": -648.56,
            "reason": "Group FCFF includes NCI; deduct NCI572.72 plus mezzanine75.84 at book proxy. Fair-value NCI not independently estimated, +/-20% sensitivity necessary; no NCI earnings deduction inside consolidated EBIT.",
            "source": "S1 p21"
          }
        ],
        "equity_value": 16016.986472890081
      },
      "high": {
        "segments": [
          {
            "id": "ecommerce",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-10. E-commerce combines domestic, quick commerce, international and wholesale; Q1 annualized revenue 8234.48. Year1 sales 8200/8500/8800 are assumptions around this run-rate, not an annual forecast from management. EBIT margins include economic SBC, ordinary intangible amortization and lease expense; later margin/growth changes are research forecasts. DA 1.8% revenue and capex 2.5%-3.4% are allocation assumptions; no segment capex disclosure.",
            "discount_rate": 0.09,
            "years": [
              {
                "year": 1,
                "revenue": 8800,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 158.4,
                "capex": 220.0,
                "delta_nwc": 11.3104
              },
              {
                "year": 2,
                "revenue": 9328.0,
                "ebit_margin": 0.195,
                "tax_rate": 0.25,
                "da": 167.904,
                "capex": 261.184,
                "delta_nwc": 10.56
              },
              {
                "year": 3,
                "revenue": 9887.68,
                "ebit_margin": 0.2,
                "tax_rate": 0.25,
                "da": 177.97824,
                "capex": 296.6304,
                "delta_nwc": 11.1936
              },
              {
                "year": 4,
                "revenue": 10382.064,
                "ebit_margin": 0.205,
                "tax_rate": 0.25,
                "da": 186.877152,
                "capex": 321.843984,
                "delta_nwc": 9.88768
              },
              {
                "year": 5,
                "revenue": 10849.25688,
                "ebit_margin": 0.21,
                "tax_rate": 0.25,
                "da": 195.286624,
                "capex": 347.17622,
                "delta_nwc": 9.343858
              },
              {
                "year": 6,
                "revenue": 11283.227155,
                "ebit_margin": 0.215,
                "tax_rate": 0.25,
                "da": 203.098089,
                "capex": 361.063269,
                "delta_nwc": 8.679406
              },
              {
                "year": 7,
                "revenue": 11678.140106,
                "ebit_margin": 0.22,
                "tax_rate": 0.25,
                "da": 210.206522,
                "capex": 373.700483,
                "delta_nwc": 7.898259
              },
              {
                "year": 8,
                "revenue": 12028.484309,
                "ebit_margin": 0.22,
                "tax_rate": 0.25,
                "da": 216.512718,
                "capex": 384.911498,
                "delta_nwc": 7.006884
              },
              {
                "year": 9,
                "revenue": 12329.196417,
                "ebit_margin": 0.22,
                "tax_rate": 0.25,
                "da": 221.925535,
                "capex": 394.534285,
                "delta_nwc": 6.014242
              },
              {
                "year": 10,
                "revenue": 12637.426327,
                "ebit_margin": 0.22,
                "tax_rate": 0.25,
                "da": 227.473674,
                "capex": 429.82661,
                "delta_nwc": 6.164598
              }
            ],
            "terminal": {
              "growth": 0.025,
              "roic": 0.25,
              "margin": 0.22,
              "tax_rate": 0.25
            }
          },
          {
            "id": "ai_cloud_labs",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-10. Cloud plus AI Labs eliminates an unsupported separation between AI infrastructure benefit and model/app cost. Q1 combined revenue 517.75 and EBITA -82.33; annualized revenue 2071.00. Year1 +20/30/40% and decelerating growth are below or near the latest 45% cloud growth; recovery margins require utilization/pricing and Labs cost absorption. DA and capex are explicit allocation assumptions constrained by S1 group capex and S5 computer lives 3-5 years; no company ten-year plan is claimed.",
            "discount_rate": 0.11,
            "years": [
              {
                "year": 1,
                "revenue": 2899.4,
                "ebit_margin": -0.1,
                "tax_rate": 0.0,
                "da": 463.904,
                "capex": 2174.55,
                "delta_nwc": 16.568
              },
              {
                "year": 2,
                "revenue": 3769.22,
                "ebit_margin": -0.03,
                "tax_rate": 0.0,
                "da": 791.5362,
                "capex": 2261.532,
                "delta_nwc": 17.3964
              },
              {
                "year": 3,
                "revenue": 4711.525,
                "ebit_margin": 0.05,
                "tax_rate": 0.25,
                "da": 1177.88125,
                "capex": 2261.532,
                "delta_nwc": 18.8461
              },
              {
                "year": 4,
                "revenue": 5653.83,
                "ebit_margin": 0.1,
                "tax_rate": 0.25,
                "da": 1526.5341,
                "capex": 2148.4554,
                "delta_nwc": 18.8461
              },
              {
                "year": 5,
                "revenue": 6558.4428,
                "ebit_margin": 0.14,
                "tax_rate": 0.25,
                "da": 1705.195128,
                "capex": 2033.117268,
                "delta_nwc": 18.092256
              },
              {
                "year": 6,
                "revenue": 7345.455936,
                "ebit_margin": 0.17,
                "tax_rate": 0.25,
                "da": 1762.909425,
                "capex": 1983.273103,
                "delta_nwc": 15.740263
              },
              {
                "year": 7,
                "revenue": 8006.54697,
                "ebit_margin": 0.19,
                "tax_rate": 0.25,
                "da": 1761.440333,
                "capex": 1921.571273,
                "delta_nwc": 13.221821
              },
              {
                "year": 8,
                "revenue": 8486.939788,
                "ebit_margin": 0.2,
                "tax_rate": 0.25,
                "da": 1697.387958,
                "capex": 1867.126753,
                "delta_nwc": 9.607856
              },
              {
                "year": 9,
                "revenue": 8826.41738,
                "ebit_margin": 0.2,
                "tax_rate": 0.25,
                "da": 1588.755128,
                "capex": 1765.283476,
                "delta_nwc": 6.789552
              },
              {
                "year": 10,
                "revenue": 9047.077814,
                "ebit_margin": 0.2,
                "tax_rate": 0.25,
                "da": 1538.003228,
                "capex": 1722.070808,
                "delta_nwc": 4.413209
              }
            ],
            "terminal": {
              "growth": 0.025,
              "roic": 0.18,
              "margin": 0.2,
              "tax_rate": 0.25
            }
          },
          {
            "id": "other_corporate_eliminations",
            "source": "S1 pp7-10,23; S5 pp206,218-220; assumptions in evidence.md",
            "assumptions": "S1 pp7-8. Residual is All Others + Unallocated + intersegment eliminations, not a reported standalone business. Q1 net revenue 113.16 and adjusted EBITA -41.87. This preserves group totals and keeps elimination costs. A more negative initial margin than the old group estimate and later loss reduction are assumptions; segment-internal sales mix is unknown. Margin interpretation is accounting-residual only, not industry comparison.",
            "discount_rate": 0.11,
            "years": [
              {
                "year": 1,
                "revenue": 470,
                "ebit_margin": -0.25,
                "tax_rate": 0.0,
                "da": 14.1,
                "capex": 16.45,
                "delta_nwc": 0.3472
              },
              {
                "year": 2,
                "revenue": 488.8,
                "ebit_margin": -0.15,
                "tax_rate": 0.0,
                "da": 14.664,
                "capex": 17.108,
                "delta_nwc": 0.376
              },
              {
                "year": 3,
                "revenue": 508.352,
                "ebit_margin": -0.05,
                "tax_rate": 0.0,
                "da": 15.25056,
                "capex": 17.79232,
                "delta_nwc": 0.39104
              },
              {
                "year": 4,
                "revenue": 528.68608,
                "ebit_margin": 0.02,
                "tax_rate": 0.25,
                "da": 15.860582,
                "capex": 18.504013,
                "delta_nwc": 0.406682
              },
              {
                "year": 5,
                "revenue": 547.190093,
                "ebit_margin": 0.06,
                "tax_rate": 0.25,
                "da": 16.415703,
                "capex": 19.151653,
                "delta_nwc": 0.37008
              },
              {
                "year": 6,
                "revenue": 563.605796,
                "ebit_margin": 0.08,
                "tax_rate": 0.25,
                "da": 16.908174,
                "capex": 19.726203,
                "delta_nwc": 0.328314
              },
              {
                "year": 7,
                "revenue": 577.69594,
                "ebit_margin": 0.1,
                "tax_rate": 0.25,
                "da": 17.330878,
                "capex": 20.219358,
                "delta_nwc": 0.281803
              },
              {
                "year": 8,
                "revenue": 589.249859,
                "ebit_margin": 0.1,
                "tax_rate": 0.25,
                "da": 17.677496,
                "capex": 20.623745,
                "delta_nwc": 0.231078
              },
              {
                "year": 9,
                "revenue": 601.034856,
                "ebit_margin": 0.1,
                "tax_rate": 0.25,
                "da": 18.031046,
                "capex": 21.03622,
                "delta_nwc": 0.2357
              },
              {
                "year": 10,
                "revenue": 613.055554,
                "ebit_margin": 0.1,
                "tax_rate": 0.25,
                "da": 18.391667,
                "capex": 25.814447,
                "delta_nwc": 0.240414
              }
            ],
            "terminal": {
              "growth": 0.02,
              "roic": 0.12,
              "margin": 0.1,
              "tax_rate": 0.25
            }
          }
        ],
        "equity_adjustments": [
          {
            "id": "june_unrestricted_cash_treasury",
            "amount": 4745.05,
            "reason": "6/30 unrestricted cash plus treasury, already includes long-dated deposits/securities; excludes 425.85 restricted cash",
            "source": "S1 pp15,20"
          },
          {
            "id": "post_june_completed_placement",
            "amount": 682.18418,
            "reason": "Completed 8/26; translate approximate HKD79.7 billion net amount (797亿元HKD) at common cutoff fixing; actual settlement FX unavailable, capital purpose is AI capex not discretionary dividend",
            "source": "S2 p2; S9"
          },
          {
            "id": "post_june_cash_burn_estimate",
            "amount": -297.8,
            "reason": "Unverified Jul-Oct cash-burn assumption = June company FCF outflow 446.70 x 4/3 x 0.5; excludes separately listed dividend and fines. Not the September reported result. Future years start 11/1 so no period overlap.",
            "source": "S1 p26 plus research assumption"
          },
          {
            "id": "post_june_declared_dividend",
            "amount": -167.845,
            "reason": "FY2026 dividend expected in July, after June cash date. Reserve approximate USD2.5bn regardless of settlement timing; exact payment/FX not verified. Do not also deduct dividend payable.",
            "source": "S4 pp5-6; S9"
          },
          {
            "id": "regulatory_cash_obligation_range_reserve",
            "amount": -63,
            "reason": "Conservative conditional reserve63 for own USD325m and EUR550m (cutoff translation62.95545). Actual payment or any overlap withJune30 cash/estimated burn unknown. Range0-63 means amount still absent from the starting cash/burn ledger, not uncertainty about the legal amounts. Deduct once as post-June use OR outstanding obligation, never both.",
            "source": "S10/S11 original official releases; S1 p13 EC provision"
          },
          {
            "id": "unreconstructed_post_june_changes_X",
            "amount": 0,
            "reason": "Conditional algebra uses X=0 solely to make unresolved cash change explicit; actual X is unknown and not asserted zero. Includes un-reconstructed buybacks, FX, acquisitions and net debt changes. Subtract actual net outflow X from resulting equity value; no unsupported fixed allowance substituted for missing records.",
            "source": "research assumption; S7 titles show July buybacks not fully reconstructed"
          },
          {
            "id": "operating_cash_retention",
            "amount": -300,
            "reason": "Permanent operating liquidity reserve; low/base/high 500/400/300 (~3%-5% of current sales), not reported restricted cash; future NWC excludes cash. Must not be confused with deducting future capex again.",
            "source": "research assumption supported by S1 cash-burn risk"
          },
          {
            "id": "june_interest_bearing_debt",
            "amount": -2665.3,
            "reason": "Five balance-sheet debt lines; use debt treatment for convertibles. No extra if-converted shares. Subsequent net debt changes unresolved.",
            "source": "S1 pp20-21"
          },
          {
            "id": "noncash_financial_investments",
            "amount": 3659.336,
            "reason": "Noncash financial investment book 4574.17 = equities/other 4311.48 - liquid treasury already included 1769.38 + equity method2032.07; recoverability 80%. Includes Ant, so do not add separate Ant NAV. Haircut is an assumption, not observed market value.",
            "source": "S1 pp20-21; S5 p215"
          },
          {
            "id": "noncontrolling_and_mezzanine",
            "amount": -648.56,
            "reason": "Group FCFF includes NCI; deduct NCI572.72 plus mezzanine75.84 at book proxy. Fair-value NCI not independently estimated, +/-20% sensitivity necessary; no NCI earnings deduction inside consolidated EBIT.",
            "source": "S1 p21"
          }
        ],
        "equity_value": 30633.35322013709
      }
    }
  },
  "baseline": null,
  "valuation_review": {
    "base_case": "同包条件截面；经营假设见inputs/evidence与assumptions；非概率中位数，资产归属仍未闭合",
    "method_choice": "这是模型实验，不是完整生产研究；本组严格采用valuation.kind所声明的资本化法或分业务FCFF，新增假设分拆披露。",
    "pe_crosscheck": "旧阿里普通股利润PE为12/15/18倍；旧小米是EV/NOPAT资本化16/18/20倍再除1.10，不得标为归母PE。本DCF基准经营EV=12385.5553亿元、Y1 NOPAT=518.9050亿元，隐含EV/NOPAT=23.8686倍；含恢复预期，非同业事实或正当性证明。",
    "market_check": {
      "price": 97.05,
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
          "segment_id": "ai_cloud_labs",
          "variable": "terminal_margin",
          "target_price": 97.05,
          "lower": 0,
          "upper": 0.5,
          "parameter": 0.1570157381282522,
          "modeled_price": 97.05,
          "residual": 2e-48
        }
      ]
    }
  },
  "discounts": {
    "d_base": {
      "value": 0.25,
      "range": [
        0.25,
        0.25
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
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_v5": {
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_gov": {
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
      "reason": "固定历史折扣仅为控制实验，非本轮重新认可其经济有效性",
      "change": {
        "kind": "initial",
        "reason": "实验基线原文另在inputs；不是正式增量研究交付",
        "evidence": []
      }
    },
    "r_terminal": {
      "value": 0.0,
      "range": [
        0.0,
        0.0
      ],
      "risk_ids": [],
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
