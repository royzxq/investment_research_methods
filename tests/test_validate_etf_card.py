"""Synthetic card and snapshot; none of these numbers is market data."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etf_calc import level_at_multiple, scenario_annual_return
from scripts.validate_etf_card import (cross_card_errors, current_cards, export_drift, export_payload, load_card,
                                       validate_card, validate_file)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = """== ETF 框架 v0.1 数据快照 | AS_OF=20260918 ==
---- §0 自检 ----
---- §1 估值 ----
  PE_TTM: 当前 12.68 | 扩张窗分位 52.7 (n=258, 自20050429) | 10年窗分位 62.8 (n=121)
    历史分位点(扩张窗): P10 9.50 / P25 11.00 / P50 12.50 / P75 15.00 / P90 20.00
---- §3 指数结构 ----
[某指数] 成分数 50 | 最大单一成分 13.45% | 前十大合计 47.91%
  前十大: 甲公司(600001.SH) 13.45、乙公司(600002.SH) 8.37
  研究覆盖率: 8.4% (1 只在个股研究池内)
---- §5 工具池 ----
  费率: 管理 0.50% + 托管 0.05% + 销售服务 0.10% = 年费合计 0.65%
---- §6 趋势 ----
 某指数 931152.CSI 20260918 1,880.55 1,888.98
== 快照完成 ==
"""


def number(value, source=None):
    return {"value": value, "source": source if value is not None else None}


def scenario(growth, terminal):
    inputs = dict(eps_growth_pct=growth, dividend_yield_pct=1.0, current_multiple=12.68, terminal_multiple=terminal,
                  years=5, drag_pct=0.65)
    result = scenario_annual_return(**inputs)
    sources = dict(eps_growth_pct="ai_estimate", dividend_yield_pct="ai_estimate", current_multiple="snapshot§1",
                   terminal_multiple="snapshot§1", years="ai_estimate", drag_pct="snapshot§5")
    return {"inputs": {key: number(value, sources[key]) for key, value in inputs.items()},
            "valuation_change_pct": number(round(result["valuation_change_pct"], 4), "calc:scenario_annual_return"),
            "annual_return_pct": number(round(result["annual_return_pct"], 4), "calc:scenario_annual_return")}


def anchor(target_multiple, ratio):
    inputs = dict(current_level=1880.55, current_multiple=12.68, target_multiple=target_multiple)
    sources = dict(current_level="snapshot§6", current_multiple="snapshot§1", target_multiple="snapshot§1")
    return {"level": number(round(level_at_multiple(**inputs), 2), "calc:level_at_multiple"),
            "target_ratio_pct": number(ratio, "framework:A9"),
            "inputs": {key: number(value, sources[key]) for key, value in inputs.items()},
            "rationale": f"PE 回到 {target_multiple} 倍对应的点位"}


def no_anchor():
    return {"level": number(None), "target_ratio_pct": number(None), "inputs": None, "rationale": None}


def trigger(kind="manual", action="review"):
    auto = kind == "auto"
    return {"name": "指数跌破10月线" if auto else "集采续约降价幅度", "kind": kind,
            "metric": "index_vs_sma10m_pct" if auto else None, "operator": "<" if auto else None,
            "threshold": number(0 if auto else None, "framework:A9"),
            "condition_text": "月末收盘低于10月均线" if auto else "续约平均降幅超过上一轮",
            "data_source": "ai_investment 日频计算" if auto else "国家医保局公告", "current_text": None,
            "frequency": "monthly" if auto else "event", "action": action, "action_note": ""}


def card():
    return {
        "card_schema_version": 1, "card_id": "cn-pharma-tactical", "as_of_date": "2026-09-19", "supersedes": None,
        "framework": {"path": "framework/etf_framework.md", "version": "v0.1"},
        "snapshot_ref": "research/etf-2026-09-18-data-snapshot.txt",
        "task": "tactical", "status": "active", "no_buy_reason": None, "close_reason": None,
        "exposure": {"index_code": "931152.CSI", "index_name": "中证创新药产业", "asset_type": "sector", "currency": "CNY",
                     "counts_toward_sector_cap": True, "china_equity": True, "view_mismatch_note": "CXO 占比高于创新药本身",
                     "structure": {"weights_as_of": "2026-08-31", "constituent_count": number(50, "snapshot§3"),
                                   "max_constituent_weight_pct": number(13.45, "snapshot§3"),
                                   "top10_weight_pct": number(47.91, "snapshot§3"),
                                   "research_coverage_pct": number(8.4, "snapshot§3"),
                                   "top_constituents": [{"code": "600001.SH", "name": "甲公司",
                                                         "weight_pct": number(13.45, "snapshot§3")}]}},
        "thesis": {"statement": "出海授权收入开始兑现而估值仍在中位以下", "evidence": ["证据一", "证据二", "证据三"],
                   "counter_evidence": ["反证一", "反证二"], "horizon_months": 18},
        "expectation": {"method": "return_decomposition",
                        "scenarios": {"bear": scenario(2, 9.5), "base": scenario(8, 12.68), "bull": scenario(12, 15.0)},
                        "valuation_state": {"index_code": "931152.CSI", "metric": "pe_ttm", "value": number(12.68, "snapshot§1"),
                                            "percentile_expanding": number(52.7, "snapshot§1"),
                                            "percentile_10y": number(62.8, "snapshot§1"),
                                            "sample_n": number(258, "snapshot§1"), "as_of": "2026-09-18"}},
        "instruments": {"merge_note": "四只医药基金穿透后是同一笔押注，合并为一只",
                        "list": [{"code": "012781.OF", "name": "银华中证创新药产业ETF联接-A", "instrument_type": "otc_fund",
                                  "share_class": "A", "currency": "CNY", "platform_account": "支付宝", "role": "primary", "action": "buy",
                                  "reason": "同指数 A 类无销售服务费"},
                                 {"code": "012782.OF", "name": "银华中证创新药产业ETF联接-C", "instrument_type": "otc_fund",
                                  "share_class": "C", "currency": "CNY", "platform_account": "支付宝", "role": "held_other",
                                  "action": "stop_dca", "reason": "长期持有 C 类更贵"}]},
        "trade_rules": {"min_holding_days": 7, "purchase_limit_note": None},
        "decision": {"rule_refs": ["A8", "A9", "A10"],
                     "anchors": {"basis": "index_level", "index_code": "931152.CSI", "reduce_mode": "to_target_ratio",
                                 "no_anchor_reason": None, "valid_until": "2026-12-31",
                                 "add_below": anchor(9.5, 100), "buy_below": anchor(11.0, 50),
                                 "reduce_above": anchor(15.0, 30)}},
        "sizing": {"bet_group": "cn-hk-pharma", "stress_drawdown_pct": number(-70, "framework:A8"),
                   "loss_budget_cny": number(35000, "user:2026-09-18"),
                   "standalone_cap_cny": number(50000, "calc:loss_budget_cap")},
        "monitor_variables": [trigger("auto", "alert"), trigger(), trigger()],
        "exit": {"invalidation": [trigger(action="close")], "latest_review_date": "2026-12-19"},
        "scorecard": {"benchmark": {"code": "000510.SH", "name": "同一笔钱放在中证A500联接"}, "preregistered_at": "2026-09-19", "confidence_pct": 55,
                      "entry_ref_index_level": number(1880.55, "snapshot§6")},
    }


def errors_of(mutate, **kwargs):
    document = card()
    mutate(document)
    return validate_card(document, snapshot_text=SNAPSHOT, **kwargs)


class ValidCardTests(unittest.TestCase):
    def test_fixture_is_valid(self):
        self.assertEqual(validate_card(card(), snapshot_text=SNAPSHOT,
                                       filename="cn-pharma-tactical-2026-09-19.md"), [])

    def test_schema_reference_example_is_valid_against_its_committed_snapshot(self):
        document = load_card((ROOT / "framework" / "etf_card_schema.md").read_text(encoding="utf-8"))
        snapshot = (ROOT / document["snapshot_ref"]).read_text(encoding="utf-8")
        self.assertEqual(validate_card(document, snapshot_text=snapshot), [])

    def test_no_buy_card_needs_no_primary_zones_or_monitors(self):
        def mutate(document):
            document.update(status="no_buy", no_buy_reason="portfolio", monitor_variables=[])
            document["instruments"]["list"] = []
            document["exit"]["invalidation"] = []
            document["decision"]["anchors"].update(add_below=no_anchor(), buy_below=no_anchor(), reduce_above=no_anchor(),
                                                   no_anchor_reason="已超单笔上限，不设买入点位", valid_until=None)
        self.assertEqual(errors_of(mutate), [])


class RejectionTests(unittest.TestCase):
    def assert_error(self, mutate, fragment, **kwargs):
        errors = errors_of(mutate, **kwargs)
        self.assertTrue(any(fragment in error for error in errors), f"{fragment!r} not in {errors}")

    def test_status_reason_combinations(self):
        self.assert_error(lambda d: d.update(status="no_buy"), "no_buy_reason: present exactly when")
        self.assert_error(lambda d: d.update(no_buy_reason="price"), "no_buy_reason: present exactly when")
        self.assert_error(lambda d: d.update(status="closed"), "close_reason: present exactly when")
        self.assert_error(lambda d: d.update(status="paused"), "status: expected one of")

    def test_ai_estimate_is_rejected_on_levels_weights_amounts_and_valuations(self):
        for path in (("decision", "anchors", "buy_below", "inputs", "current_level"),
                     ("decision", "anchors", "reduce_above", "target_ratio_pct"), ("sizing", "loss_budget_cny"),
                     ("exposure", "structure", "top10_weight_pct"), ("expectation", "valuation_state", "value"),
                     ("expectation", "scenarios", "bear", "inputs", "terminal_multiple"),
                     ("scorecard", "entry_ref_index_level")):
            def mutate(document, path=path):
                target = document
                for key in path:
                    target = target[key]
                target["source"] = "ai_estimate"
            self.assert_error(mutate, "ai_estimate is accepted only on scenario assumptions")

    def test_numbers_need_a_wrapper_and_a_known_source(self):
        self.assert_error(lambda d: d["sizing"].update(loss_budget_cny=35000), "sizing.loss_budget_cny: expected sourced number")
        self.assert_error(lambda d: d["thesis"].update(target_price=12.5), "thesis.target_price: bare number")
        self.assert_error(lambda d: d["sizing"]["loss_budget_cny"].update(source="wind"), "sizing.loss_budget_cny.source")
        self.assert_error(lambda d: d["sizing"]["standalone_cap_cny"].update(source="calc:kelly"), "etf_calc has no function kelly")
        self.assert_error(lambda d: d["sizing"]["loss_budget_cny"].update(value=None), "source: must be null while value is null")
        self.assert_error(lambda d: d["sizing"]["loss_budget_cny"].update(value=True), "expected finite number or null")
        self.assert_error(lambda d: d["sizing"]["loss_budget_cny"].update(value=float("inf")), "expected finite number or null")

    def test_calculator_outputs_are_recomputed(self):
        self.assert_error(lambda d: d["sizing"]["standalone_cap_cny"].update(value=60000), "does not match calc:loss_budget_cap")
        self.assert_error(lambda d: d["expectation"]["scenarios"]["bull"]["annual_return_pct"].update(value=25.0),
                          "does not match calc:scenario_annual_return")
        self.assert_error(lambda d: d["sizing"]["stress_drawdown_pct"].update(value=70), "sizing.stress_drawdown_pct.value: outside")

    def test_base_scenario_assumes_zero_valuation_change(self):
        def mutate(document):
            document["expectation"]["scenarios"]["base"] = scenario(8, 15.0)
        self.assert_error(mutate, "base scenario must assume zero valuation change")
        self.assert_error(lambda d: d["expectation"]["scenarios"].update(bear=scenario(20, 20.0)), "expected bear <= base <= bull")

    def test_snapshot_citations_must_be_printed_in_the_cited_section(self):
        self.assert_error(lambda d: d["expectation"]["valuation_state"]["value"].update(value=11.9),
                          "11.9 is not printed in snapshot§1")
        self.assert_error(lambda d: d["expectation"]["valuation_state"]["value"].update(source="snapshot§6"),
                          "12.68 is not printed in snapshot§6")
        self.assert_error(lambda d: d["expectation"]["valuation_state"]["value"].update(source="snapshot§7"),
                          "snapshot§7 is not a section of the referenced snapshot")
        for miscopied in (13.4496, 13.4, 13):   # copied as printed, never rounded further
            self.assert_error(lambda d, v=miscopied: d["exposure"]["structure"]["max_constituent_weight_pct"].update(value=v),
                              f"{miscopied} is not printed in snapshot§3")
        for near_an_integer_token in (9.6, 0.7, 75.3):   # "10年窗", "§1", "P75" must not vouch for these
            self.assert_error(lambda d, v=near_an_integer_token: d["expectation"]["valuation_state"]["value"].update(value=v),
                              f"{near_an_integer_token} is not printed in snapshot§1")

    def test_tactical_and_live_card_obligations(self):
        self.assert_error(lambda d: d["exit"].update(invalidation=[]), "preregisters at least one invalidation")
        self.assert_error(lambda d: d["exit"].update(latest_review_date="2026-09-19"), "must be later than as_of_date")
        self.assert_error(lambda d: d["exit"].update(latest_review_date=None), "exit.latest_review_date: expected ISO date")
        self.assert_error(lambda d: d.update(monitor_variables=[trigger()] * 2), "3 to 5 monitor variables")
        self.assert_error(lambda d: d["thesis"].update(evidence=["只有一条"]), "thesis.evidence: expected exactly 3")
        self.assert_error(lambda d: d["thesis"].update(horizon_months=0), "thesis.horizon_months: expected integer >= 1")
        self.assert_error(lambda d: d["instruments"].update(list=d["instruments"]["list"][1:]), "exactly one primary")
        self.assert_error(lambda d: d["scorecard"].update(preregistered_at="2026-09-20"), "later than as_of_date")

    def test_conditions_hang_on_the_index_and_otc_funds_have_no_premium(self):
        self.assert_error(lambda d: d["decision"]["anchors"].update(basis="fund_nav"), "conditions hang on index_level")
        self.assert_error(lambda d: d["decision"]["anchors"].update(index_code="000300.SH"), "must equal exposure.index_code")
        self.assert_error(lambda d: d["trade_rules"].update(max_premium_pct=number(3, "framework:A7")), "trade_rules.max_premium_pct: unknown field")
        self.assert_error(lambda d: d["decision"].update(dca_action="pause"), "decision.dca_action: unknown field")
        self.assert_error(lambda d: d["monitor_variables"][0].update(metric="bet_group_weight_pct"), "monitor_variables[0].metric")

    def test_anchors_are_a_strict_stateless_three_point_ladder(self):
        anchors = lambda d: d["decision"]["anchors"]
        self.assert_error(lambda d: anchors(d).update(buy_below=anchor(9.5, 50)), "add_below.level < buy_below.level < reduce_above.level")
        self.assert_error(lambda d: anchors(d).update(reduce_above=anchor(11.0, 30)), "add_below.level < buy_below.level < reduce_above.level")
        self.assert_error(lambda d: anchors(d).update(buy_below=anchor(11.0, 20)), "add_below ratio >= buy_below ratio > reduce_above ratio")
        self.assert_error(lambda d: anchors(d).update(reduce_mode="exit_all"), "exit_all goes with a reduce_above target_ratio_pct of 0")
        self.assert_error(lambda d: anchors(d).update(reduce_above=anchor(15.0, 0)), "exit_all goes with a reduce_above target_ratio_pct of 0")
        self.assert_error(lambda d: anchors(d).update(add_below=no_anchor()), "all present or all null")
        self.assert_error(lambda d: anchors(d).update(no_anchor_reason="无估值源"), "present exactly when the card carries no anchors")
        self.assert_error(lambda d: anchors(d).update(valid_until=None), "decision.anchors.valid_until: expected ISO date")

    def test_anchor_levels_come_from_a_named_calculator_and_are_recomputed(self):
        buy = lambda d: d["decision"]["anchors"]["buy_below"]
        self.assert_error(lambda d: buy(d)["level"].update(source="snapshot§6"), "names the calculator that derived it")
        self.assert_error(lambda d: buy(d)["level"].update(value=1500.0), "does not match calc:level_at_multiple of the inputs")
        self.assert_error(lambda d: buy(d)["inputs"].update(pe=number(11.0, "snapshot§1")), "etf_calc.level_at_multiple rejects these inputs")
        self.assert_error(lambda d: buy(d)["inputs"]["target_multiple"].update(value=11.7), "11.7 is not printed in snapshot§1")
        self.assertEqual(errors_of(lambda d: buy(d).update(inputs=None)), [])

    def test_anchor_recompute_never_crashes_or_passes_unverified(self):
        buy = lambda d: d["decision"]["anchors"]["buy_below"]
        self.assert_error(lambda d: buy(d)["level"].update(source=5), "decision.anchors.buy_below.level.source")
        self.assert_error(lambda d: buy(d)["inputs"]["current_multiple"].update(value=-12.68, source="user:2026-09-19"),
                          "etf_calc.level_at_multiple does not yield a level from these inputs (None)")

        def misuse(document):
            buy(document)["level"]["source"] = "calc:loss_budget_cap"
            buy(document)["inputs"] = {"loss_budget": number(1000, "user:2026-09-19"),
                                       "stress_drawdown_pct": number(30, "user:2026-09-19")}
        self.assert_error(misuse, "etf_calc.loss_budget_cap rejects these inputs: stress_drawdown_pct_must_be_in")
        self.assert_error(lambda d: buy(d)["level"].update(source="calc:timedelta"), "etf_calc has no function timedelta")

    def test_a_card_that_governs_money_carries_a_cap_monitors_and_a_price_source(self):
        def no_buy_holding(document):   # held but not added to: still claimed, so still governed
            document.update(status="no_buy", no_buy_reason="price", monitor_variables=[])
            document["instruments"]["list"][0]["action"] = "hold"
        self.assert_error(no_buy_holding, "a card that claims a holding carries at least one monitor variable")
        self.assert_error(lambda d: d["sizing"].update(loss_budget_cny=number(None), standalone_cap_cny=number(None)),
                          "sizing.standalone_cap_cny.value: required when the card claims a holding or carries anchors")

        def buy_without_anchors(document):
            document["decision"]["anchors"].update(add_below=no_anchor(), buy_below=no_anchor(), reduce_above=no_anchor(),
                                                   no_anchor_reason="无估值源", valid_until=None)
        self.assert_error(buy_without_anchors, "an instrument with action buy needs the three anchors")

        def unsourced_index(document):
            document["exposure"]["index_code"] = document["decision"]["anchors"]["index_code"] = "HSHYLV"
        self.assert_error(unsourced_index, "this index has no price source: the card must be no_buy/data without anchors")

    def test_identifiers_are_unambiguous(self):
        first = lambda d: d["instruments"]["list"][0]
        for bare in ("012781", "02800", "012781.of", "HSI"):
            self.assert_error(lambda d, v=bare: first(d).update(code=v), "instruments.list[0].code: expected ts_code with suffix")
        self.assert_error(lambda d: d["exposure"]["structure"]["top_constituents"][0].update(code="600001"),
                          "top_constituents[0].code: expected ts_code with suffix")
        self.assert_error(lambda d: first(d).update(currency="人民币"), "instruments.list[0].currency")
        self.assert_error(lambda d: first(d).pop("currency"), "instruments.list[0].currency: missing field")
        self.assert_error(lambda d: d["exposure"].update(index_code="HSTECH"), "exposure.index_code: expected an index key registered")
        self.assert_error(lambda d: d["scorecard"]["benchmark"].update(code="货币基金"), "scorecard.benchmark.code")
        self.assertEqual(errors_of(lambda d: d["scorecard"]["benchmark"].update(code=None)), [])
        self.assert_error(lambda d: d.update(as_of_date="2999-01-01"), "as_of_date: later than today")
        self.assert_error(lambda d: d["exposure"].update(currency="USD"), "the registry lists 931152.CSI in CNY")
        for path in (("expectation", "valuation_state"), ("scorecard", "benchmark")):
            def unpriced(document, path=path):
                target = document
                for key in path:
                    target = target[key]
                target["index_code" if path[0] == "expectation" else "code"] = "HSHYLV"
            self.assert_error(unpriced, "HSHYLV has no price source in the registry")
        self.assert_error(lambda d: d["decision"]["anchors"].update(valid_until="2026-09-18"),
                          "valid_until: earlier than as_of_date")
        self.assert_error(lambda d: d["monitor_variables"][0].update(action="pause_dca"), "monitor_variables[0].action")
        self.assert_error(lambda d: d["exposure"]["structure"]["top_constituents"][0].update(code="022448.OF"),
                          "top_constituents[0].code")   # a fund is not a constituent

    def test_a_committed_export_must_match_the_cards(self):
        document = card()
        with tempfile.TemporaryDirectory() as folder, unittest.mock.patch("scripts.validate_etf_card.EXPORT",
                                                                          Path(folder) / "current.json") as export:
            self.assertEqual(export_drift([document]), [])   # nothing committed yet
            export.write_text(json.dumps(export_payload([document], "2026-09-19T00:00:00+08:00"), ensure_ascii=False),
                              encoding="utf-8")
            self.assertEqual(export_drift([document]), [])   # generated_at is not compared
            changed = card()
            changed["status"], changed["close_reason"] = "closed", "expired"
            self.assertEqual(export_drift([changed]), [f"{export}: out of date (cards); rerun with --export and commit the result"])
            export.write_text("{", encoding="utf-8")
            self.assertTrue(export_drift([document])[0].startswith(f"{export}: "))

    def test_triggers(self):
        def auto_without_threshold(document):
            document["monitor_variables"][0]["threshold"] = number(None)
        self.assert_error(auto_without_threshold, "an auto trigger needs metric, operator and threshold.value")
        self.assert_error(lambda d: d["monitor_variables"][1].update(metric="index_level"), "a manual trigger keeps metric")
        self.assert_error(lambda d: d["exit"]["invalidation"][0].update(action="alert"), "exit.invalidation[0].action")
        self.assert_error(lambda d: d["monitor_variables"][0].update(metric="fund_nav"), "monitor_variables[0].metric")

    def test_unknown_missing_and_misnamed(self):
        self.assert_error(lambda d: d.update(price_target=1), "card.price_target: unknown field")
        self.assert_error(lambda d: d.pop("sizing"), "card.sizing: missing field")
        self.assert_error(lambda d: d.update(card_schema_version=2), "card_schema_version: expected 1")
        self.assert_error(lambda d: d.update(card_schema_version=1.0), "card_schema_version: expected 1")
        self.assert_error(lambda d: d.update(as_of_date="2026-02-30"), "as_of_date: invalid calendar date")
        self.assert_error(lambda d: None, "file must be named", filename="pharma.md")
        self.assertTrue(validate_card([]))


class LoadTests(unittest.TestCase):
    def wrap(self, *blocks):
        return "# 卡\n\n" + "\n\n".join(f"```json\n{block}\n```" for block in blocks) + "\n"

    def test_exactly_one_json_block(self):
        self.assertEqual(load_card(self.wrap(json.dumps(card())))["card_id"], "cn-pharma-tactical")
        for text in (self.wrap(), self.wrap("{}", "{}")):
            with self.assertRaises(ValueError):
                load_card(text)

    def test_duplicate_keys_and_non_finite_numbers_are_rejected(self):
        for block in ('{"a": 1, "a": 2}', '{"a": NaN}', '{"a": Infinity}'):
            with self.assertRaises(ValueError):
                load_card(self.wrap(block))

    def test_cross_card_invariants_look_at_current_versions_only(self):
        def version(card_id, as_of, **sizing):
            document = card()
            document.update(card_id=card_id, as_of_date=as_of)
            document["sizing"].update(sizing)
            return document
        old, new = version("cn-pharma-tactical", "2026-08-19"), version("cn-pharma-tactical", "2026-09-19")
        self.assertEqual(current_cards([new, old]), [new])
        self.assertEqual(cross_card_errors([old, new]), [])   # two versions of one card share group and holdings
        other = version("hk-pharma-tactical", "2026-09-19")
        self.assertEqual(cross_card_errors([old, new, other]), [
            "sizing.bet_group: cn-hk-pharma is shared by cards cn-pharma-tactical, hk-pharma-tactical; merge them into one card",
            "instruments: 012781.OF is claimed by cards cn-pharma-tactical, hk-pharma-tactical; every other card lists it as rejected",
            "instruments: 012782.OF is claimed by cards cn-pharma-tactical, hk-pharma-tactical; every other card lists it as rejected"])
        other.update(status="closed", close_reason="budget")   # a closed card releases its bet and its instruments
        self.assertEqual(cross_card_errors([new, other]), [])

    def test_export_carries_current_cards_and_derived_portfolio_params(self):
        old, new = card(), card()
        old["as_of_date"] = "2026-08-19"
        payload = export_payload([old, new], "2026-09-19T20:00:00+08:00")
        self.assertEqual((payload["card_schema_version"], payload["cards"]), (1, [new]))
        params = payload["portfolio_params"]
        self.assertEqual((params["sector_etf_cap_cny"], params["single_bet_cap_cny"], params["china_equity_cap_pct"]),
                         (210000, 50000, 90))
        self.assertNotIn("_doc", params)
        self.assertIn({"key": "HKTECH", "name": "恒生科技", "source": "index_global", "code": "HKTECH", "currency": "HKD"},
                      payload["index_registry"])

    def test_missing_snapshot_file_is_an_error(self):
        document = copy.deepcopy(card())
        document["snapshot_ref"] = "research/etf-1999-01-01-data-snapshot.txt"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cn-pharma-tactical-2026-09-19.md"
            path.write_text(self.wrap(json.dumps(document, ensure_ascii=False)), encoding="utf-8")
            errors = validate_file(path)
            self.assertEqual([error for error in errors if "snapshot" in error],
                             ["snapshot_ref: research/etf-1999-01-01-data-snapshot.txt not found under " + str(ROOT)])
            self.assertTrue(validate_file(Path(folder) / "no-such-card.md"))


if __name__ == "__main__":
    unittest.main()
