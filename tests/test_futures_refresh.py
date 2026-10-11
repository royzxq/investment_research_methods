"""Synthetic offline refresh boundaries; no API, trade or profitability assertions."""
from contextlib import redirect_stdout
import copy
from datetime import date, datetime, timedelta
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import futures_refresh as refresh
from scripts.futures_strategy import trend_inputs


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Explicit synthetic exchange sessions include a weekday closure.
        start = date(2026, 1, 1)
        self.days = [(start + timedelta(days=i)).strftime("%Y%m%d") for i in range(220)
                     if (start + timedelta(days=i)).weekday() < 5 and i != 5]
        self.day = self.days[60]
        self.now = datetime.fromisoformat(refresh.iso_date(self.day) + "T19:30:00+08:00")
        self.payload = dict(rule_version="v3.0", script_version="v1.18", scope="v3_research_inputs_only",
                            as_of_date=self.day, trend=[], economic_reversion=[])
        for product in ("MA", "RB", "M", "SR", "CF"):
            contract = product + "2701"
            rows = [dict(trade_date=day, close=3000 + i % 7, high=3002 + i % 7, low=2998 + i % 7)
                    for i, day in enumerate(self.days[:61])]
            rows[-1].update(close=3030, high=3032, low=3028)
            market = dict(contract=contract, records=rows, trading_dates=self.days, as_of_date=self.day,
                          exchange="SHFE" if product == "RB" else "DCE" if product == "M" else "CZCE",
                          source="Tushare Pro fut_daily", fetched_at=self.now.isoformat(),
                          identity_basis="fut_daily_response_ts_code",
                          ts_code=contract + (".SHF" if product == "RB" else ".DCE" if product == "M" else ".ZCE"))
            item = trend_inputs(market)
            item["market_inputs"] = market
            self.payload["trend"].append(item)
        self.snapshot = self.root / "snapshot.txt"
        self.write_snapshot()

    def write_snapshot(self):
        lines = [f"== v3.0 框架数据脚本 {self.payload['script_version']} | AS_OF={self.day} |"]
        lines += [f"T {row['contract']}: {row['status']} / {row['signal']} / {row['side']}"
                  for row in self.payload["trend"]]
        lines += [f"== 快照完成 | AS_OF={self.day} | 脚本 {self.payload['script_version']} | 本行存在即输出完整 =="]
        self.snapshot.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def evaluate(self, **kwargs):
        return refresh.evaluate(self.payload, self.snapshot, kwargs.pop("as_of", self.day),
                                kwargs.pop("now", self.now), **kwargs)

    def test_all_five_recomputed_from_raw_without_trade_permission(self):
        # Cached result values are not consumed as numerical evidence.
        self.payload["trend"][0]["signal_close"] = 1
        result = self.evaluate()
        self.assertEqual(result["refresh_status"], "fresh")
        self.assertEqual(len(result["trend"]), 5)
        self.assertTrue(all(row["signal_close"] == 3030 for row in result["trend"]))
        self.assertEqual(result["scope"], "mechanical_refresh_only")
        self.assertEqual(result["execution_permission"], "not_evaluated")
        self.assertIsNone(result["final_lots"])
        self.assertEqual(result["trend"][0]["valid_until"], refresh.iso_date(self.days[62]))

    def test_incomplete_or_legacy_snapshot_rejected(self):
        for replacement in ("", "== 快照完成 | AS_OF=20200101 | 脚本 v1.18 |", "legacy v1.16"):
            self.snapshot.write_text(replacement, encoding="utf-8")
            result = self.evaluate()
            self.assertEqual(result["refresh_status"], "failed")
            self.assertEqual(result["trend"], [])
            self.assertIn("canonical_sha256", result["method"])

    def test_partial_file_never_counted_as_complete(self):
        partial = self.snapshot.with_suffix(".partial")
        partial.write_bytes(self.snapshot.read_bytes())
        result = refresh.evaluate(self.payload, partial, self.day, self.now)
        self.assertEqual(result["refresh_status"], "failed")

    def test_stale_data_is_unknown_not_no_signal(self):
        self.payload["trend"][0]["market_inputs"]["records"].pop()
        result = self.evaluate()
        row = next(row for row in result["trend"] if row["contract"] == "MA2701")
        self.assertEqual(result["refresh_status"], "partial")
        self.assertEqual((row["status"], row["signal"]), ("incomplete", "unknown"))
        self.assertTrue(any("stale_or_missing" in gap for gap in row["missing_fields"]))

    def test_all_stale_failed_and_calendar_missing_unknown(self):
        for row in self.payload["trend"]:
            row["market_inputs"]["trading_dates"] = []
        result = self.evaluate()
        self.assertEqual(result["refresh_status"], "failed")
        self.assertTrue(all(row["signal"] == "unknown" for row in result["trend"]))

    def test_short_calendar_does_not_guess_future_entry_days(self):
        for row in self.payload["trend"]:
            row["market_inputs"]["trading_dates"] = self.days[:61]
        result = self.evaluate()
        self.assertEqual(result["refresh_status"], "failed")
        self.assertTrue(all(row["signal"] == "unknown" for row in result["trend"]))

    def test_holiday_and_weekend_use_real_calendar_not_weekdays(self):
        days = ["20260930", "20261008", "20261009", "20261012", "20261013"]
        for day in ("20261001", "20261006", "20261007"):
            now = datetime.fromisoformat(refresh.iso_date(day) + "T19:30:00+08:00")
            self.assertEqual(refresh.latest_completed(days, day, now), "20260930")
        now = datetime.fromisoformat("2026-10-11T19:30:00+08:00")
        self.assertEqual(refresh.latest_completed(days, "20261011", now), "20261009")

    def test_before_18_does_not_require_intraday_bar(self):
        day = self.days[61]
        now = datetime.fromisoformat(refresh.iso_date(day) + "T17:59:00+08:00")
        result = self.evaluate(as_of=day, now=now)
        self.assertEqual(result["refresh_status"], "fresh")
        self.assertTrue(all(row["market_trade_date"] == self.day for row in result["trend"]))
        result = self.evaluate(as_of=day, now=now.replace(hour=18))
        self.assertEqual(result["refresh_status"], "failed")

    def test_future_fetch_and_preclose_fetch_rejected(self):
        market = self.payload["trend"][0]["market_inputs"]
        for value in ((self.now + timedelta(minutes=1)).isoformat(), self.now.replace(hour=17).isoformat()):
            market["fetched_at"] = value
            result = self.evaluate()
            row = next(row for row in result["trend"] if row["contract"] == "MA2701")
            self.assertEqual(row["signal"], "unknown")

    def test_missing_product_or_duplicate_contract_is_partial(self):
        for mutate in (lambda: self.payload["trend"].pop(),
                       lambda: self.payload["trend"].append(copy.deepcopy(self.payload["trend"][0]))):
            original = copy.deepcopy(self.payload)
            mutate()
            result = self.evaluate()
            self.assertEqual(result["refresh_status"], "partial")
            self.payload = original

    def test_declared_source_calendar_degradation_fails(self):
        content = self.snapshot.read_text(encoding="utf-8")
        self.snapshot.write_text(content.replace("T MA", "busday近似·口径已降级\nT MA"), encoding="utf-8")
        self.assertEqual(self.evaluate()["refresh_status"], "failed")

    def plans(self):
        return dict(candidates=[dict(opportunity_id="original-id", contracts=["MA2701"],
                   plan=dict(signal_date=refresh.iso_date(self.day), valid_until=refresh.iso_date(self.days[62]),
                             registered_at=self.now.isoformat()))])

    def test_registered_plan_original_clock_retained_and_expires(self):
        plans = self.plans()
        original = copy.deepcopy(plans)
        result = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(result["status"], "remaining_window")
        self.assertEqual(result["remaining_entry_dates"], list(map(refresh.iso_date, self.days[61:63])))
        expiry = datetime.fromisoformat(refresh.iso_date(self.days[62]) + "T15:00:00+08:00")
        result = self.evaluate(plans=plans, as_of=self.days[62], now=expiry)["registered_plan_windows"][0]
        self.assertEqual(result["status"], "session_check_required")
        self.assertEqual(result["entry_session_checks_required_dates"], [refresh.iso_date(self.days[62])])
        expiry += timedelta(days=1)
        result = self.evaluate(plans=plans, as_of=refresh.stamp(expiry.date()), now=expiry)["registered_plan_windows"][0]
        self.assertEqual(result["status"], "expired")
        self.assertEqual(result["remaining_entry_dates"], [])
        self.assertFalse(result["signal_clock_reset"])
        self.assertEqual(plans, original)

    def test_extended_expiry_or_naive_registration_rejected(self):
        for key, value in (("valid_until", self.days[63]), ("registered_at", self.now.date().isoformat())):
            plans = self.plans()
            plans["candidates"][0]["plan"][key] = value
            row = self.evaluate(plans=plans)["registered_plan_windows"][0]
            self.assertEqual(row["status"], "incomplete")

    def add_reversion(self):
        records = [dict(trade_date=day, near_contract="MA2701", far_contract="MA2705",
                        near_settle=3000 + value, far_settle=3000)
                   for day, value in zip(self.days, [200 + i % 7 for i in range(58)] + [320, 310, 300])]
        provenance = dict(source="Tushare Pro fut_daily", fetched_at=self.now.isoformat(),
                          identity_basis="fut_daily_response_ts_code")
        self.payload["economic_reversion"] = [dict(near_contract="MA2701", far_contract="MA2705",
            research_stage="current", market_inputs=dict(near_contract="MA2701", far_contract="MA2705",
            records=records, trading_dates=self.days, as_of_date=self.day, exchange="CZCE",
            sources={"MA2701": dict(provenance, ts_code="MA2701.ZCE"),
                     "MA2705": dict(provenance, ts_code="MA2705.ZCE")}))]
        return dict(anchors=[dict(near_contract="MA2701", far_contract="MA2705", anchor_low=-100,
            anchor_high=100, frozen_at=(self.now - timedelta(days=3)).isoformat(), valid_until=self.days[70],
            source_refs=["synthetic-source"], economic_anchor_basis="synthetic-storage-band",
            convergence_mechanism="synthetic-arrival", invalidation_basis="synthetic-delay")])

    def test_reversion_without_frozen_anchor_not_evaluated(self):
        self.add_reversion()
        result = self.evaluate()
        self.assertEqual(result["economic_reversion"][0]["status"], "not_evaluated")
        self.assertEqual(result["refresh_status"], "fresh")

    def test_explicit_anchor_passes_only_frozen_before_signal(self):
        anchors = self.add_reversion()
        result = self.evaluate(anchors=anchors)
        self.assertEqual(result["economic_reversion"][0]["signal"], "triggered")
        self.assertEqual(result["economic_reversion"][0]["economic_validity"], "requires_research_review")
        anchors["anchors"][0]["frozen_at"] = self.now.isoformat()
        result = self.evaluate(anchors=anchors)
        self.assertEqual(result["economic_reversion"][0]["status"], "incomplete")
        self.assertEqual(result["refresh_status"], "partial")

    def add_signal_observation(self, anchors):
        anchors["signal_observations"] = [dict(near_contract="MA2701", far_contract="MA2705",
            signal_date=refresh.iso_date(self.day), signal_completed_at=self.now.replace(hour=15, minute=15).isoformat(),
            source_refs=["synthetic exchange settlement publication at 15:15"])]
        return anchors["signal_observations"][0]

    def test_same_day_economic_anchor_before_verified_completion_is_eligible(self):
        anchors = self.add_reversion()
        anchors["anchors"][0]["frozen_at"] = self.now.replace(hour=9).isoformat()
        self.add_signal_observation(anchors)
        original = copy.deepcopy(anchors)
        row = self.evaluate(anchors=anchors)["economic_reversion"][0]
        self.assertEqual((row["status"], row["signal"]), ("valid", "triggered"))
        self.assertEqual(row["anchor_timing_basis"], "verified_timestamp")
        self.assertEqual(row["execution_permission"], "not_evaluated")
        self.assertEqual(anchors, original)

    def test_same_day_anchor_missing_or_late_completion_never_guesses_close(self):
        anchors = self.add_reversion()
        anchors["anchors"][0]["frozen_at"] = self.now.replace(hour=9).isoformat()
        row = self.evaluate(anchors=anchors)["economic_reversion"][0]
        self.assertEqual(row["reason"], "same_day_anchor_requires_signal_completion_evidence")
        observation = self.add_signal_observation(anchors)
        for value in (observation["signal_completed_at"], self.now.replace(hour=16).isoformat()):
            with self.subTest(frozen=value):
                anchors["anchors"][0]["frozen_at"] = value
                row = self.evaluate(anchors=anchors)["economic_reversion"][0]
                self.assertEqual(row["reason"], "economic_anchor_not_frozen_before_signal_completion")

    def test_signal_completion_provenance_and_time_boundaries(self):
        anchors = self.add_reversion()
        anchors["anchors"][0]["frozen_at"] = self.now.replace(hour=9).isoformat()
        observation = self.add_signal_observation(anchors)
        original = copy.deepcopy(observation)
        cases = [("source_refs", []), ("source_refs", "not an array"),
                 ("signal_completed_at", self.now.replace(tzinfo=None).isoformat()),
                 ("signal_completed_at", (self.now + timedelta(minutes=1)).isoformat()),
                 ("signal_completed_at", (self.now - timedelta(days=1)).isoformat())]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                observation.clear()
                observation.update(original)
                observation[key] = value
                row = self.evaluate(anchors=anchors)["economic_reversion"][0]
                self.assertEqual(row["status"], "incomplete")
        observation.clear()
        observation.update(original)
        observation["signal_completed_at"] = self.now.replace(hour=19, minute=0).isoformat()
        for source in self.payload["economic_reversion"][0]["market_inputs"]["sources"].values():
            source["fetched_at"] = self.now.replace(hour=18, minute=30).isoformat()
        row = self.evaluate(anchors=anchors)["economic_reversion"][0]
        self.assertEqual(row["reason"], "signal_completed_after_source_fetch")

    def test_completion_from_different_pair_or_day_does_not_authorize_anchor(self):
        anchors = self.add_reversion()
        anchors["anchors"][0]["frozen_at"] = self.now.replace(hour=9).isoformat()
        observation = self.add_signal_observation(anchors)
        for field, value in (("far_contract", "MA2709"), ("signal_date", self.days[59])):
            original = copy.deepcopy(observation)
            observation[field] = value
            row = self.evaluate(anchors=anchors)["economic_reversion"][0]
            self.assertEqual(row["reason"], "same_day_anchor_requires_signal_completion_evidence")
            observation.clear()
            observation.update(original)
        anchors["signal_observations"].append(copy.deepcopy(observation))
        row = self.evaluate(anchors=anchors)["economic_reversion"][0]
        self.assertEqual(row["reason"], "duplicate_signal_completion_observation")

    def test_pair_binding_rejects_outer_ma_with_underlying_rb(self):
        anchors = self.add_reversion()
        market = self.payload["economic_reversion"][0]["market_inputs"]
        market.update(near_contract="RB2701", far_contract="RB2705", exchange="SHFE")
        market["sources"] = {key.replace("MA", "RB"): value for key, value in market["sources"].items()}
        for record in market["records"]:
            record.update(near_contract="RB2701", far_contract="RB2705")
        row = self.evaluate(anchors=anchors)["economic_reversion"][0]
        self.assertEqual(row["status"], "incomplete")
        self.assertEqual(row["reason"], "raw_pair_identity_mismatch")
        self.assertEqual(row["near_contract"], "MA2701")

    def test_pair_source_keys_row_identity_and_leg_provenance_are_bound(self):
        anchors = self.add_reversion()
        item = self.payload["economic_reversion"][0]
        original = copy.deepcopy(item)
        mutations = [
            lambda m: m["sources"].update(RB2701=m["sources"].pop("MA2701")),
            lambda m: m["records"][-1].update(far_contract="MA2709"),
            lambda m: m["sources"]["MA2705"].update(ts_code="RB2705.SHF"),
            lambda m: m["sources"]["MA2705"].update(contract="MA2709"),
            lambda m: m["sources"]["MA2705"].update(exchange="SHFE"),
            lambda m: m.update(exchange="SHFE"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                item.clear()
                item.update(copy.deepcopy(original))
                mutate(item["market_inputs"])
                row = self.evaluate(anchors=anchors)["economic_reversion"][0]
                self.assertEqual(row["status"], "incomplete")
                self.assertNotEqual(row.get("signal"), "triggered")

    def old_pair_plans(self):
        plans = self.plans()
        plans["candidates"][0]["contracts"] = ["MA2705", "MA2709"]
        self.add_reversion()
        item = self.payload["economic_reversion"][0]
        item.update(near_contract="MA2705", far_contract="MA2709")
        market = item["market_inputs"]
        market.update(near_contract="MA2705", far_contract="MA2709")
        market["sources"] = {"MA2705": copy.deepcopy(market["sources"]["MA2701"]),
                             "MA2709": copy.deepcopy(market["sources"]["MA2705"])}
        for contract, source in market["sources"].items():
            source["ts_code"] = contract + ".ZCE"
        for record in market["records"]:
            record.update(near_contract="MA2705", far_contract="MA2709")
        return plans

    def test_old_v_pair_uses_both_exact_raw_calendars_without_current_t_leg(self):
        plans = self.old_pair_plans()
        original = copy.deepcopy(plans)
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "remaining_window")
        self.assertEqual([entry["contract"] for entry in row["calendar_checks"]], ["MA2705", "MA2709"])
        self.assertTrue(all(entry["basis"] == "exact_contract_inputs" for entry in row["calendar_checks"]))
        self.assertEqual(plans, original)
        self.assertEqual(row["opportunity_id"], "original-id")

    def test_old_t_contract_uses_same_exchange_calendar_without_claiming_prices(self):
        plans = self.plans()
        plans["candidates"][0]["contracts"] = ["MA2609"]
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "remaining_window")
        check = row["calendar_checks"][0]
        self.assertEqual(check["basis"], "same_exchange_calendar_only")
        self.assertEqual(check["price_refresh_status"], "missing_original_contract_prices")
        self.assertTrue(all(contract.startswith(("MA", "SR", "CF")) for contract in check["source_contracts"]))
        self.assertEqual(row["execution_permission"], "not_evaluated")

    def test_stale_original_price_does_not_erase_its_valid_calendar(self):
        self.payload["trend"][0]["market_inputs"]["records"].pop()
        row = self.evaluate(plans=self.plans())["registered_plan_windows"][0]
        self.assertEqual(row["status"], "remaining_window")
        self.assertEqual(row["calendar_checks"][0]["price_refresh_status"], "incomplete")

    def test_old_plan_calendar_requires_sourced_consistent_same_exchange(self):
        plans = self.plans()
        plans["candidates"][0]["contracts"] = ["MA2609"]
        for item in self.payload["trend"]:
            if item["contract"].startswith(("MA", "SR", "CF")):
                item["market_inputs"]["source"] = None
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "incomplete")
        self.assertIn("calendar_provenance_invalid", row["issue"])
        for item in self.payload["trend"]:
            item["market_inputs"]["source"] = "Tushare Pro fut_daily"
        self.payload["trend"][-1]["market_inputs"]["trading_dates"] = [day for day in self.days if day != self.days[61]]
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "incomplete")
        self.assertIn("calendar_conflict", row["issue"])

    def test_pair_leg_calendar_disagreement_is_not_repaired_from_current_t(self):
        plans = self.old_pair_plans()
        market = self.payload["economic_reversion"][0]["market_inputs"]
        market["sources"]["MA2709"]["trading_dates"] = [day for day in self.days if day != self.days[61]]
        result = self.evaluate(plans=plans)
        self.assertEqual(result["economic_reversion"][0]["reason"], "raw_pair_leg_calendar_mismatch")
        # A malformed exact-leg input must not silently become a same-exchange success.
        self.assertEqual(result["registered_plan_windows"][0]["status"], "incomplete")

    def test_calendar_range_extensions_do_not_create_a_new_clock_barrier(self):
        plans = self.plans()
        plans["candidates"][0]["contracts"] = ["MA2609"]
        self.payload["trend"][0]["market_inputs"]["trading_dates"] = self.days[5:100]
        self.payload["trend"][-1]["market_inputs"]["trading_dates"] = self.days[:80]
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "remaining_window")
        self.assertEqual(row["original_valid_entry_dates"], list(map(refresh.iso_date, self.days[61:63])))

    def test_old_contract_missing_calendar_is_distinct_from_missing_price(self):
        plans = self.plans()
        plans["candidates"][0]["contracts"] = ["MA2609"]
        self.payload["trend"] = [item for item in self.payload["trend"] if item["contract"].startswith(("M2", "RB"))]
        self.write_snapshot()
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "incomplete")
        self.assertEqual(row["issue"], "calendar_missing_for_contract:MA2609")

    def test_invalid_contract_month_does_not_crash_refresh(self):
        self.payload["trend"][0]["contract"] = "MA2799"
        self.payload["trend"][0]["market_inputs"]["contract"] = "MA2799"
        self.write_snapshot()
        result = self.evaluate()
        self.assertEqual(result["refresh_status"], "partial")
        row = next(row for row in result["trend"] if row["contract"] == "MA2799")
        self.assertIn("unsupported_or_invalid_contract", row["missing_fields"])

    def test_future_signal_and_registration_before_signal_are_rejected(self):
        for fields, issue in ((dict(signal_date=self.days[61], valid_until=self.days[63]), "signal_date_is_in_future"),
                              (dict(registered_at=(self.now - timedelta(days=1)).isoformat()), "registration_before_signal_date")):
            plans = self.plans()
            plans["candidates"][0]["plan"].update(fields)
            row = self.evaluate(plans=plans)["registered_plan_windows"][0]
            self.assertEqual(row["status"], "incomplete")
            self.assertEqual(row["issue"], issue)

    def test_registration_order_uses_sourced_completion_or_reports_unknown(self):
        plans = self.plans()
        plan = plans["candidates"][0]["plan"]
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["registration_order_status"], "unknown_same_day_signal_completion_time")
        plan.update(signal_completed_at=self.now.replace(hour=16).isoformat(),
                    signal_completed_source_refs=["synthetic publication source"],
                    registered_at=self.now.replace(hour=15).isoformat())
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["issue"], "registration_before_signal_completion")
        plan["registered_at"] = self.now.isoformat()
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "remaining_window")
        self.assertEqual(row["registration_order_status"], "verified_timestamp")
        plan["signal_completed_source_refs"] = []
        row = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(row["status"], "incomplete")

    def add_withdrawal(self, anchors, invalidated_at=None):
        row = dict(near_contract="MA2701", far_contract="MA2705",
                   invalidated_at=invalidated_at or (self.now - timedelta(hours=1)).isoformat(),
                   reason="synthetic supply evidence invalidates anchor", source_refs=["synthetic correction source"])
        anchors["withdrawals"] = [row]
        return row

    def test_direct_anchor_package_with_effective_withdrawal_never_computes_signal(self):
        anchors = self.add_reversion()
        withdrawal = self.add_withdrawal(anchors)
        original = copy.deepcopy(anchors)
        result = self.evaluate(anchors=anchors)
        row = result["economic_reversion"][0]
        self.assertEqual((row["status"], row["signal"], row["reason"]), ("incomplete", "unknown", "anchor_withdrawn"))
        self.assertEqual(row["anchor_withdrawal"], withdrawal)
        self.assertEqual(result["refresh_status"], "partial")
        self.assertEqual(row["execution_permission"], "not_evaluated")
        self.assertEqual(anchors, original)
        # Continuity collect may already have removed the anchor, retaining its withdrawal.
        anchors["anchors"] = []
        self.assertEqual(self.evaluate(anchors=anchors)["economic_reversion"][0]["reason"], "anchor_withdrawn")

    def test_anchor_frozen_strictly_after_withdrawal_can_be_evaluated(self):
        anchors = self.add_reversion()
        withdrawn_at = self.now - timedelta(days=2)
        self.add_withdrawal(anchors, withdrawn_at.isoformat())
        anchors["anchors"][0]["frozen_at"] = withdrawn_at.isoformat()
        self.assertEqual(self.evaluate(anchors=anchors)["economic_reversion"][0]["reason"], "anchor_withdrawn")
        anchors["anchors"][0]["frozen_at"] = (withdrawn_at + timedelta(hours=1)).isoformat()
        row = self.evaluate(anchors=anchors)["economic_reversion"][0]
        self.assertEqual((row["status"], row["signal"]), ("valid", "triggered"))

    def test_future_withdrawal_is_not_applied_to_current_or_historical_evaluation(self):
        anchors = self.add_reversion()
        self.add_withdrawal(anchors, (self.now + timedelta(hours=1)).isoformat())
        self.assertEqual(self.evaluate(anchors=anchors)["economic_reversion"][0]["status"], "valid")
        # An event known now but after the requested historical day must not rewrite that day's result.
        self.add_withdrawal(anchors, (self.now + timedelta(days=1)).isoformat())
        row = self.evaluate(anchors=anchors, now=self.now + timedelta(days=3))["economic_reversion"][0]
        self.assertEqual((row["status"], row["signal"]), ("valid", "triggered"))

    def test_withdrawal_is_bound_to_pair_and_latest_effective_date(self):
        anchors = self.add_reversion()
        row = self.add_withdrawal(anchors)
        row.update(near_contract="MA2705", far_contract="MA2709")
        self.assertEqual(self.evaluate(anchors=anchors)["economic_reversion"][0]["status"], "valid")
        first = self.add_withdrawal(anchors, (self.now - timedelta(hours=2)).isoformat())
        second = dict(first, invalidated_at=(self.now - timedelta(hours=1)).isoformat(), reason="latest correction")
        future = dict(first, invalidated_at=(self.now + timedelta(hours=1)).isoformat(), reason="future correction")
        anchors["withdrawals"] = [future, first, second]
        result = self.evaluate(anchors=anchors)["economic_reversion"][0]
        self.assertEqual(result["reason"], "anchor_withdrawn")
        self.assertEqual(result["anchor_withdrawal"]["reason"], "latest correction")

    def test_malformed_withdrawal_is_not_silently_ignored(self):
        anchors = self.add_reversion()
        original = copy.deepcopy(self.add_withdrawal(anchors))
        cases = [None, [None], [dict(original, source_refs=[])], [dict(original, reason="")],
                 [dict(original, invalidated_at="2026-01-01")],
                 [dict(original, near_contract="MA2701", far_contract="RB2705")]]
        for malformed in cases:
            with self.subTest(malformed=malformed):
                anchors["withdrawals"] = malformed
                row = self.evaluate(anchors=anchors)["economic_reversion"][0]
                self.assertEqual((row["status"], row["signal"]), ("incomplete", "unknown"))
                self.assertNotEqual(row["reason"], "frozen_economic_anchor_not_supplied")

    def test_source_identity_requires_explicit_provider_code_not_outer_or_request_label(self):
        for contract, exchange, code in (("MA2701", "CZCE", "MA2701.ZCE"),
                                          ("RB2701", "SHFE", "RB2701.SHF"),
                                          ("M2701", "DCE", "M2701.DCE")):
            with self.subTest(contract=contract):
                refresh.source_identity(dict(ts_code=code, identity_basis="fut_daily_response_ts_code"), contract, exchange)
                refresh.source_identity(dict(ts_code=code, contract=contract, exchange=exchange,
                                             requested_ts_code=code, identity_basis="fut_daily_response_ts_code"), contract, exchange)
                for missing in ({}, {"contract": contract, "exchange": exchange},
                                {"requested_ts_code": code}, {"ts_code": None},
                                {"ts_code": ""}, {"ts_code": " "}, {"ts_code": 2701}):
                    with self.assertRaisesRegex(ValueError, "price_source_contract_identity_missing"):
                        refresh.source_identity(missing, contract, exchange)

    def test_source_identity_rejects_conflicting_contract_exchange_and_request(self):
        for fields in ({"ts_code": "MA2705.ZCE"}, {"ts_code": "MA2701.SHF"},
                       {"ts_code": "MA2701.ZCE "}, {"ts_code": "MA2701.ZCE", "contract": "MA2705"},
                       {"ts_code": "MA2701.ZCE", "contract": None},
                       {"ts_code": "MA2701.ZCE", "exchange": "SHFE"},
                       {"ts_code": "MA2701.ZCE", "exchange": None},
                       {"ts_code": "MA2701.ZCE", "requested_ts_code": "MA2705.ZCE"}):
            with self.subTest(fields=fields), self.assertRaisesRegex(ValueError, "price_source_contract_identity"):
                refresh.source_identity(dict(fields, identity_basis="fut_daily_response_ts_code"), "MA2701", "CZCE")

    def test_trend_missing_provider_identity_is_unknown_even_with_matching_labels(self):
        market = self.payload["trend"][0]["market_inputs"]
        market.pop("ts_code")
        market["requested_ts_code"] = "MA2701.ZCE"
        result = self.evaluate(plans=self.plans())
        row = next(row for row in result["trend"] if row["contract"] == "MA2701")
        self.assertEqual((row["status"], row["signal"]), ("incomplete", "unknown"))
        self.assertIn("price_source_contract_identity_missing", row["missing_fields"])
        self.assertEqual(result["registered_plan_windows"][0]["status"], "incomplete")

    def test_optional_trend_row_provider_identity_must_match_provenance(self):
        market = self.payload["trend"][0]["market_inputs"]
        for row in market["records"]:
            row["ts_code"] = "MA2701.ZCE"
        self.assertEqual(self.evaluate()["refresh_status"], "fresh")
        for value in ("MA2705.ZCE", "MA2701.SHF", None, ""):
            with self.subTest(ts_code=value):
                market["records"][0]["ts_code"] = value
                row = next(row for row in self.evaluate()["trend"] if row["contract"] == "MA2701")
                self.assertEqual((row["status"], row["signal"]), ("incomplete", "unknown"))
                self.assertTrue(any(issue.startswith("price_source_contract_identity") for issue in row["missing_fields"]))

    def test_v_missing_provider_identity_cannot_hide_behind_current_t_calendar(self):
        plans = self.old_pair_plans()
        market = self.payload["economic_reversion"][0]["market_inputs"]
        for leg in ("MA2705", "MA2709"):
            original = market["sources"][leg].pop("ts_code")
            with self.subTest(leg=leg):
                result = self.evaluate(plans=plans)
                self.assertEqual(result["economic_reversion"][0]["reason"], "price_source_contract_identity_missing")
                clock = result["registered_plan_windows"][0]
                self.assertEqual(clock["status"], "incomplete")
                self.assertIn("calendar_input_invalid", clock["issue"])
            market["sources"][leg]["ts_code"] = original

    def test_v_nonobject_provenance_cannot_fall_back_to_same_exchange_calendar(self):
        plans = self.old_pair_plans()
        market = self.payload["economic_reversion"][0]["market_inputs"]
        for invalid in (None, "MA2709.ZCE", ["MA2709.ZCE"]):
            with self.subTest(source=invalid):
                market["sources"]["MA2709"] = invalid
                result = self.evaluate(plans=plans)
                self.assertEqual(result["economic_reversion"][0]["reason"],
                                 "price_source_contract_identity_requires_object")
                self.assertEqual(result["registered_plan_windows"][0]["status"], "incomplete")
                self.assertIn("calendar_input_invalid", result["registered_plan_windows"][0]["issue"])

    def test_old_v_request_code_without_response_verification_is_not_accepted(self):
        anchors = self.add_reversion()
        self.assertEqual(self.evaluate(anchors=anchors)["economic_reversion"][0]["status"], "valid")
        source = self.payload["economic_reversion"][0]["market_inputs"]["sources"]["MA2705"]
        source.pop("identity_basis")
        result = self.evaluate(anchors=anchors)
        self.assertEqual(result["economic_reversion"][0]["reason"],
                         "price_source_contract_identity_response_unverified")
        self.assertEqual((result["economic_reversion"][0]["status"], result["economic_reversion"][0]["signal"]),
                         ("incomplete", "unknown"))
        plans = self.old_pair_plans()
        self.payload["economic_reversion"][0]["market_inputs"]["sources"]["MA2709"].pop("identity_basis")
        clock = self.evaluate(plans=plans)["registered_plan_windows"][0]
        self.assertEqual(clock["status"], "incomplete")
        self.assertIn("calendar_input_invalid", clock["issue"])

    def test_trend_response_verification_is_required_but_not_repeated_on_each_bar(self):
        market = self.payload["trend"][0]["market_inputs"]
        for row in market["records"]:
            row["ts_code"] = "MA2701.ZCE"
        self.assertEqual(self.evaluate()["refresh_status"], "fresh")
        for marker in (None, "", "requested_ts_code", True):
            with self.subTest(identity_basis=marker):
                market["identity_basis"] = marker
                row = next(row for row in self.evaluate()["trend"] if row["contract"] == "MA2701")
                self.assertEqual((row["status"], row["signal"]), ("incomplete", "unknown"))
                self.assertIn("price_source_contract_identity_response_unverified", row["missing_fields"])
        market.pop("identity_basis")
        row = next(row for row in self.evaluate()["trend"] if row["contract"] == "MA2701")
        self.assertIn("price_source_contract_identity_response_unverified", row["missing_fields"])

    def test_optional_spread_row_provider_identities_are_bound_to_their_legs(self):
        anchors = self.add_reversion()
        row = self.payload["economic_reversion"][0]["market_inputs"]["records"][0]
        row.update(near_ts_code="MA2701.ZCE", far_ts_code="MA2705.ZCE")
        self.assertEqual(self.evaluate(anchors=anchors)["economic_reversion"][0]["status"], "valid")
        for field, value in (("near_ts_code", "MA2705.ZCE"), ("far_ts_code", "MA2705.SHF"),
                             ("far_ts_code", None), ("ts_code", "MA2701.ZCE")):
            original = copy.deepcopy(row)
            row[field] = value
            result = self.evaluate(anchors=anchors)["economic_reversion"][0]
            self.assertEqual((result["status"], result["signal"]), ("incomplete", "unknown"))
            row.clear()
            row.update(original)

    def test_optional_raw_response_and_request_ids_are_normalized_and_bound(self):
        market = self.payload["trend"][0]["market_inputs"]
        original = copy.deepcopy(market)
        market.update(response_ts_code_values=[" ma2701.zce ", "MA2701.ZCE"], requested_ts_code_raw=" ma2701.zce ")
        self.assertEqual(self.evaluate()["refresh_status"], "fresh")
        for key, value in (("response_ts_code_values", []), ("response_ts_code_values", "MA2701.ZCE"),
                           ("response_ts_code_values", ["MA2701.ZCE", "RB2701.SHF"]),
                           ("response_ts_code_values", [None]), ("response_ts_code_values", [""]),
                           ("requested_ts_code_raw", "RB2701.SHF"), ("requested_ts_code_raw", None)):
            with self.subTest(key=key, value=value):
                market.clear()
                market.update(copy.deepcopy(original))
                market[key] = value
                row = next(row for row in self.evaluate()["trend"] if row["contract"] == "MA2701")
                self.assertEqual((row["status"], row["signal"]), ("incomplete", "unknown"))
                self.assertTrue(any(issue.startswith("price_source_contract_identity_raw") for issue in row["missing_fields"]))

    def test_raw_bar_identity_is_checked_with_or_without_repeated_canonical_id(self):
        market = self.payload["trend"][0]["market_inputs"]
        record = market["records"][-1]
        for repeat_canonical_id in (False, True):
            if repeat_canonical_id:
                record["ts_code"] = "MA2701.ZCE"
            record["response_ts_code"] = " ma2701.zce "
            self.assertEqual(self.evaluate()["refresh_status"], "fresh")
            for value in ("RB2701.SHF", "MA2705.ZCE", None, ""):
                with self.subTest(repeated=repeat_canonical_id, raw=value):
                    record["response_ts_code"] = value
                    row = next(row for row in self.evaluate()["trend"] if row["contract"] == "MA2701")
                    self.assertEqual((row["status"], row["signal"]), ("incomplete", "unknown"))
                    self.assertTrue(any(issue.startswith("price_source_contract_identity_raw") for issue in row["missing_fields"]))

    def test_v_conflicting_raw_source_identity_cannot_use_calendar_fallback(self):
        plans = self.old_pair_plans()
        source = self.payload["economic_reversion"][0]["market_inputs"]["sources"]["MA2709"]
        source["response_ts_code_values"] = [" ma2709.zce "]
        self.assertEqual(self.evaluate(plans=plans)["registered_plan_windows"][0]["status"], "remaining_window")
        source["response_ts_code_values"] = ["RB2709.SHF"]
        result = self.evaluate(plans=plans)
        self.assertEqual(result["economic_reversion"][0]["reason"], "price_source_contract_identity_raw_mismatch")
        self.assertEqual(result["registered_plan_windows"][0]["status"], "incomplete")
        self.assertIn("calendar_input_invalid", result["registered_plan_windows"][0]["issue"])

    def test_patch_collector_versions_require_matching_snapshot_and_identity(self):
        for version in ("v1.18", "v1.18.1", "v1.18.2"):
            with self.subTest(version=version):
                self.payload["script_version"] = version
                self.write_snapshot()
                result = self.evaluate()
                self.assertEqual(result["refresh_status"], "fresh")
                self.assertEqual(result["input_script_version"], version)
        self.snapshot.write_text(self.snapshot.read_text().replace("脚本 v1.18.2", "脚本 v1.18.1", 1))
        result = self.evaluate()
        self.assertEqual(result["refresh_status"], "failed")
        self.assertIn("snapshot_version_mismatch", result["issues"])
        self.payload["script_version"] = "v1.18.1"
        self.write_snapshot()
        self.payload["trend"][0]["market_inputs"].pop("ts_code")
        result = self.evaluate()
        self.assertEqual(result["refresh_status"], "partial")
        self.assertIn("price_source_contract_identity_missing", next(
            row for row in result["trend"] if row["contract"] == "MA2701")["missing_fields"])

    def test_invalid_json_duplicate_keys_or_nan_rejected(self):
        for content in ('{"x":1,"x":2}', '{"x":NaN}'):
            source = self.root / "invalid.json"
            source.write_text(content)
            with self.assertRaises(ValueError):
                refresh.load_json(source)

    def test_preserve_exact_raw_evidence_and_isolate_repeated_reports(self):
        source = self.root / "inputs.json"
        raw = json.dumps(self.payload, ensure_ascii=False, indent=1).encode()
        source.write_bytes(raw)
        sources = [("market-inputs", source), ("data-snapshot", self.snapshot)]
        first, first_md = refresh.save_report(self.evaluate(), self.root, sources)
        old = first.read_bytes()
        second, _ = refresh.save_report(self.evaluate(), self.root, sources)
        self.assertIn("-r2.json", second.name)
        self.assertEqual(first.read_bytes(), old)
        manifest = json.loads(old)["source_inputs"][0]
        self.assertEqual((self.root / manifest["path"]).read_bytes(), raw)
        self.assertEqual(manifest["sha256"], refresh.digest(raw))
        self.assertTrue(first_md.exists())

    def test_fetch_failure_preserves_formal_and_cache_files(self):
        formal = self.root / "research/futures/snapshots" / f"{refresh.iso_date(self.day)}-data-snapshot.txt"
        cache = self.root / "output/cache/futures" / f"v3_research_inputs_{self.day}.json"
        for path in (formal, cache):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("original")
        with patch.object(refresh.subprocess, "run", return_value=subprocess.CompletedProcess([], 3)) as call:
            source, snapshot, error = refresh.fetch_isolated(self.root, self.day, sys.executable)
        self.assertIsNone(source)
        self.assertIsNone(snapshot)
        self.assertIn("exit_3", error)
        self.assertTrue(all(path.read_text() == "original" for path in (formal, cache)))
        command = call.call_args.args[0]
        self.assertNotIn("--overwrite", command)
        self.assertIn("futures-refresh-fetch", command[-1])
        self.assertNotIn("TUSHARE_TOKEN", " ".join(command))

    def test_check_only_never_writes_or_fetches(self):
        source = self.root / "inputs.json"
        source.write_text(json.dumps(self.payload))
        with patch.object(refresh, "save_report") as save, patch.object(refresh, "fetch_isolated") as fetch:
            with redirect_stdout(io.StringIO()) as out:
                code = refresh.main(["--as-of", self.day, "--input", str(source),
                                     "--snapshot", str(self.snapshot), "--check-only"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["refresh_status"], "fresh")
        save.assert_not_called()
        fetch.assert_not_called()

    def test_check_only_rejects_fetch_flag(self):
        with patch("sys.stderr", io.StringIO()), self.assertRaises(SystemExit) as error:
            refresh.main(["--check-only", "--fetch"])
        self.assertEqual(error.exception.code, 2)

    def test_malformed_items_are_incomplete_without_crashing(self):
        self.payload["trend"].append(None)
        self.payload["economic_reversion"] = [7]
        result = self.evaluate(anchors={"anchors": [None]}, plans={"candidates": [None]})
        self.assertEqual(result["refresh_status"], "partial")
        self.assertIn("trend_item_must_be_object", result["issues"])
        self.assertIn("economic_anchor_must_be_object", result["issues"])
        self.assertEqual(result["registered_plan_windows"][0]["status"], "incomplete")

    def test_source_changed_after_evaluation_prevents_publication(self):
        source = self.root / "market.json"
        source.write_text("first evaluated bytes")
        evaluated_hash = refresh.digest(source.read_bytes())
        source.write_text("different bytes before publishing")
        with self.assertRaisesRegex(ValueError, "evaluated_source_changed"):
            refresh.save_report(self.evaluate(), self.root, [("market-inputs", source, evaluated_hash)])
        formal = self.root / "research/futures/refresh" / refresh.iso_date(self.day)
        self.assertEqual(list(formal.glob("*.json")), [])
        self.assertEqual(list(formal.glob("*.md")), [])
        self.assertTrue(list((self.root / "output/futures-refresh-staging").glob("*/*.partial")))

    def test_json_publish_failure_removes_new_markdown_preserves_old_revision(self):
        first, first_md = refresh.save_report(self.evaluate(), self.root, [("data-snapshot", self.snapshot)])
        old = first.read_bytes()
        actual_link = refresh.os.link

        def fail_json(source, destination):
            if str(destination).endswith(".json"):
                raise OSError("synthetic publication failure")
            return actual_link(source, destination)

        with patch.object(refresh.os, "link", side_effect=fail_json), self.assertRaises(OSError):
            refresh.save_report(self.evaluate(), self.root, [("data-snapshot", self.snapshot)])
        self.assertEqual(first.read_bytes(), old)
        self.assertTrue(first_md.exists())
        self.assertEqual(sorted(path.name for path in first.parent.glob("*.json")), [first.name])
        self.assertEqual(sorted(path.name for path in first.parent.glob("*.md")), [first_md.name])

    def test_skipped_bad_source_is_reported_with_older_fresh_selection(self):
        bad, good = self.root / "bad.json", self.root / "good.json"
        bad.write_text("{not-json}")
        good.write_text(json.dumps(self.payload))
        with patch.object(refresh, "discover_inputs", return_value=[(bad, self.snapshot), (good, self.snapshot)]):
            with redirect_stdout(io.StringIO()) as out:
                code = refresh.main(["--as-of", self.day, "--check-only"])
        result = json.loads(out.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(result["input_selection"]["selected"], str(good))
        self.assertEqual(result["input_selection"]["attempted"][0]["refresh_status"], "failed")
        self.assertEqual(len(result["input_selection"]["attempted"]), 2)


if __name__ == "__main__":
    unittest.main()
