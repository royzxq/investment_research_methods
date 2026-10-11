"""Refresh v3 price research from complete, dated inputs; never grant trade permission.

Default is offline reuse. --fetch explicitly permits the existing data collector
to run in an isolated directory. --check-only is always offline and writes nothing.
The real-date calendar is inherited from future_data v1.18 (Tushare SSE calendar),
not reconstructed from weekdays; night-session/execution calendars remain unverified.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, time, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

try:
    from .futures_strategy import RULE_VERSION, TREND_PRODUCTS, REVERSION_PRODUCTS, trend_inputs, reversion_inputs
    from .price_evidence import completed_day_cutoff
    from .research_paths import ROOT, iso_date, snapshot_complete, artifact_path
except ImportError:
    from futures_strategy import RULE_VERSION, TREND_PRODUCTS, REVERSION_PRODUCTS, trend_inputs, reversion_inputs
    from price_evidence import completed_day_cutoff
    from research_paths import ROOT, iso_date, snapshot_complete, artifact_path

CHINA = ZoneInfo("Asia/Shanghai")
VERSION = "1.1"
CALENDAR_SOURCE = "future_data v1.18: Tushare Pro trade_cal(exchange=SSE); actual dated sessions"


def stamp(value):
    return iso_date(value).replace("-", "")


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp_missing")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp_requires_timezone")
    return parsed.astimezone(CHINA)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_json(path, *, with_digest=False):
    """Reject duplicate keys/NaN, including in user-supplied plans and anchors."""
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError(f"duplicate_json_key:{key}")
            out[key] = value
        return out

    def invalid(value):
        raise ValueError(f"invalid_json_number:{value}")

    raw = Path(path).read_bytes()
    text = raw.decode("utf-8")
    if Path(path).suffix == ".md":
        blocks = re.findall(r"```json\s*\n(.*?)\n```", text, re.S)
        if len(blocks) != 1:
            raise ValueError("require_one_json_block")
        text = blocks[0]
    result = json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    return (result, digest(raw)) if with_digest else result


def calendar_days(market, as_of):
    if not isinstance(market, dict):
        raise ValueError("market_inputs_must_be_object")
    raw = market.get("trading_dates")
    if not isinstance(raw, list) or not raw:
        raise ValueError("real_calendar_missing")
    days = [stamp(day) for day in raw]
    if days != sorted(set(days)):
        raise ValueError("calendar_not_sorted_unique")
    if days[0] > as_of or days[-1] < as_of:
        raise ValueError("calendar_does_not_cover_as_of")
    return days


def latest_completed(days, as_of, now):
    """18:00 protection plus actual sessions; no weekday approximation."""
    cutoff = min(stamp(as_of), completed_day_cutoff(now))
    eligible = [day for day in days if day <= cutoff]
    if not eligible:
        raise ValueError("calendar_has_no_completed_session")
    return eligible[-1]


def unknown(contract, issue, expected=None):
    return dict(contract=contract, status="incomplete", signal="unknown", side=None,
                expected_market_trade_date=expected, freshness="unknown",
                missing_fields=[issue], execution_permission="not_evaluated")


def checked_market(market, as_of, now, *, spread=False):
    days = calendar_days(market, as_of)
    expected = latest_completed(days, as_of, now)
    if spread and not isinstance(market.get("sources"), dict):
        raise ValueError("price_provenance_missing")
    provenance = (list(market["sources"].values()) if spread else [market])
    if not provenance or (spread and len(provenance) != 2):
        raise ValueError("price_provenance_missing")
    for source in provenance:
        if not isinstance(source, dict):
            raise ValueError("price_provenance_must_be_object")
        if source.get("source") != "Tushare Pro fut_daily":
            raise ValueError("price_source_missing_or_unsupported")
        fetched = timestamp(source.get("fetched_at"))
        if fetched > now:
            raise ValueError("fetched_at_is_in_future")
        if completed_day_cutoff(fetched) < expected:
            raise ValueError("source_fetched_before_completed_session_cutoff")
    if not market.get("exchange"):
        raise ValueError("exchange_missing")
    rows = market.get("records")
    if not isinstance(rows, list):
        raise ValueError("raw_records_missing")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("raw_rows_must_be_objects")
    eligible = [stamp(row["trade_date"]) for row in rows
                if stamp(row["trade_date"]) <= expected and row.get("is_complete") is not False]
    if not eligible or max(eligible) != expected:
        raise ValueError(f"stale_or_missing_completed_bar:{expected}")
    checked = copy.deepcopy(market)
    checked["as_of_date"] = expected
    return checked, days, expected


def entry_window(days, signal_day):
    index = days.index(stamp(signal_day))
    window = days[index + 1:index + 3]
    if len(window) != 2:
        raise ValueError("calendar_missing_two_entry_sessions")
    return [iso_date(day) for day in window]


def contract_exchange(contract):
    match = re.fullmatch(r"([A-Z]+)\d{2}(0[1-9]|1[0-2])", contract) if isinstance(contract, str) else None
    if not match or match[1] not in TREND_PRODUCTS:
        raise ValueError("unsupported_or_invalid_contract")
    return {"RB": "SHFE", "M": "DCE"}.get(match[1], "CZCE")


def source_identity(source, contract, exchange):
    if not isinstance(source, dict):
        raise ValueError("price_provenance_must_be_object")
    if source.get("contract", contract) != contract:
        raise ValueError("price_source_contract_identity_mismatch")
    expected_code = contract + "." + {"CZCE": "ZCE", "SHFE": "SHF", "DCE": "DCE"}[exchange]
    if source.get("ts_code", expected_code) != expected_code:
        raise ValueError("price_source_contract_identity_mismatch")


def spread_identity(item):
    """Bind outer pair, raw pair, each row and each provenance leg before use."""
    pair = (item.get("near_contract"), item.get("far_contract"))
    exchange = contract_exchange(pair[0])
    if contract_exchange(pair[1]) != exchange or pair[0][:-4] != pair[1][:-4]:
        raise ValueError("raw_pair_identity_mismatch")
    if pair[0][:-4] not in REVERSION_PRODUCTS or pair[0][-4:] >= pair[1][-4:]:
        raise ValueError("require_same_product_near_before_far")
    market = item.get("market_inputs")
    if not isinstance(market, dict) or (market.get("near_contract"), market.get("far_contract")) != pair:
        raise ValueError("raw_pair_identity_mismatch")
    if market.get("exchange") != exchange:
        raise ValueError("raw_pair_exchange_mismatch")
    sources = market.get("sources")
    if not isinstance(sources, dict) or set(sources) != set(pair):
        raise ValueError("raw_pair_source_keys_mismatch")
    for contract in pair:
        source_identity(sources[contract], contract, exchange)
        if sources[contract].get("exchange", exchange) != exchange:
            raise ValueError("raw_pair_leg_exchange_mismatch")
        if sources[contract].get("trading_dates", market.get("trading_dates")) != market.get("trading_dates"):
            raise ValueError("raw_pair_leg_calendar_mismatch")
    rows = market.get("records")
    if not isinstance(rows, list) or any(not isinstance(row, dict) or
            (row.get("near_contract"), row.get("far_contract")) != pair for row in rows):
        raise ValueError("raw_pair_record_identity_mismatch")
    return pair, market


def signal_observation(observations, pair, signal_day, now, *, fetched_at=None):
    matching = [row for row in observations if
                (row.get("near_contract"), row.get("far_contract")) == pair and
                stamp(row.get("signal_date")) == stamp(signal_day)]
    if len(matching) > 1:
        raise ValueError("duplicate_signal_completion_observation")
    if not matching:
        return None
    row = matching[0]
    refs = row.get("source_refs")
    if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ValueError("signal_completion_source_refs_missing")
    completed = timestamp(row.get("signal_completed_at"))
    if stamp(completed.date()) != stamp(signal_day):
        raise ValueError("signal_completion_date_mismatch")
    if completed > now:
        raise ValueError("signal_completion_is_in_future")
    if fetched_at is not None and completed > min(timestamp(value) for value in fetched_at):
        raise ValueError("signal_completed_after_source_fetch")
    return completed


def applicable_withdrawal(withdrawals, pair, as_of, now, *, frozen_at=None):
    """Respect an explicit withdrawal without projecting future evidence backward."""
    if not isinstance(withdrawals, list):
        raise ValueError("anchor_withdrawals_must_be_array")
    cutoff = min(now, datetime.combine(datetime.strptime(as_of, "%Y%m%d").date(), time.max, CHINA))
    matches = []
    for row in withdrawals:
        if not isinstance(row, dict):
            raise ValueError("anchor_withdrawal_must_be_object")
        row_pair = (row.get("near_contract"), row.get("far_contract"))
        # Invalid identity cannot be silently treated as a withdrawal of another pair.
        if (contract_exchange(row_pair[0]) != contract_exchange(row_pair[1]) or
                row_pair[0][:-4] != row_pair[1][:-4] or row_pair[0][-4:] >= row_pair[1][-4:]):
            raise ValueError("anchor_withdrawal_pair_invalid")
        invalidated = timestamp(row.get("invalidated_at"))
        refs, reason = row.get("source_refs"), row.get("reason")
        if (not isinstance(reason, str) or not reason.strip() or not isinstance(refs, list) or not refs or
                any(not isinstance(ref, str) or not ref.strip() for ref in refs)):
            raise ValueError("anchor_withdrawal_requires_reason_and_source_refs")
        if row_pair == pair and invalidated <= cutoff and (frozen_at is None or invalidated >= frozen_at):
            matches.append((invalidated, row))
    return max(matches, key=lambda item: item[0])[1] if matches else None


def calendar_entry(market, contract, source, *, origin, price_status):
    """Keep independently usable calendar evidence without claiming old prices refreshed."""
    return dict(contract=contract, trading_dates=market.get("trading_dates"), exchange=market.get("exchange"),
                source=source.get("source"), fetched_at=source.get("fetched_at"),
                calendar_origin=origin, price_refresh_status=price_status)


def plan_calendar(contract, markets, as_of, now, signal_day):
    exchange = contract_exchange(contract)
    entries = [row for rows in markets.values() for row in (rows if isinstance(rows, list) else [rows])]
    exact = [row for row in entries if row.get("contract") == contract]
    eligible = exact or [row for row in entries if row.get("exchange") == exchange]
    if not eligible:
        raise ValueError(f"calendar_missing_for_contract:{contract}")
    verified = []
    for market in eligible:
        if market.get("calendar_issue"):
            raise ValueError(f"calendar_input_invalid:{contract}:{market['calendar_issue']}")
        if market.get("exchange") != exchange or market.get("source") != "Tushare Pro fut_daily":
            raise ValueError(f"calendar_provenance_invalid:{contract}")
        if timestamp(market.get("fetched_at")) > now:
            raise ValueError("calendar_source_fetched_in_future")
        verified.append((calendar_days(market, as_of), market))
    # Calendar files may cover different history/horizon lengths; compare their
    # overlapping dates rather than treating harmless range extensions as conflict.
    for index, (days, _) in enumerate(verified):
        for other, _ in verified[index + 1:]:
            begin, end = max(days[0], other[0]), min(days[-1], other[-1])
            if [day for day in days if begin <= day <= end] != [day for day in other if begin <= day <= end]:
                raise ValueError(f"calendar_conflict_for_contract:{contract}")
    sufficient = []
    for days, market in verified:
        try:
            entry_window(days, signal_day)
        except ValueError:
            continue
        sufficient.append((days, market))
    if not sufficient:
        raise ValueError(f"calendar_missing_original_signal_or_two_entry_sessions:{contract}")
    first = max(sufficient, key=lambda entry: (entry[0][-1], len(entry[0])))[0]
    price_states = sorted({market.get("price_refresh_status", "not_evaluated") for _, market in verified})
    return first, dict(contract=contract,
                      basis="exact_contract_inputs" if exact else "same_exchange_calendar_only",
                      exchange=exchange,
                      source_contracts=sorted({market["contract"] for _, market in verified}),
                      calendar_source=CALENDAR_SOURCE,
                      price_refresh_status=((price_states[0] if len(price_states) == 1 else "mixed_raw_input_status")
                                            if exact else "missing_original_contract_prices"),
                      price_input_checks=[dict(source_contract=market["contract"],
                          input_kind=market.get("calendar_origin", "external_market_input"),
                          status=market.get("price_refresh_status", "not_evaluated"))
                          for _, market in verified] if exact else [])


def check_plans(plans, markets, as_of, now, *, observations=()):
    """Check the original clock independently of the current selected T contract."""
    results = []
    candidates = plans.get("candidates", plans.get("plans", [])) if isinstance(plans, dict) else plans
    if not isinstance(candidates, list):
        return [dict(status="incomplete", issue="plans_must_be_array")]
    for candidate in candidates:
        if not isinstance(candidate, dict):
            results.append(dict(status="incomplete", issue="plan_must_be_object"))
            continue
        plan = candidate.get("plan", candidate)
        if not isinstance(plan, dict) or not plan.get("signal_date"):
            continue
        result = dict(opportunity_id=candidate.get("opportunity_id"),
                      signal_date=plan.get("signal_date"), valid_until=plan.get("valid_until"),
                      registered_at=plan.get("registered_at", candidate.get("registered_at")),
                      status="incomplete", execution_permission="not_evaluated",
                      signal_clock_reset=False)
        try:
            signal_day = stamp(plan["signal_date"])
            if signal_day > min(as_of, stamp(now.date())):
                raise ValueError("signal_date_is_in_future")
            contracts = candidate.get("contracts") or [candidate.get("contract", plan.get("contract"))]
            if not isinstance(contracts, list) or len(contracts) not in (1, 2) or len(set(contracts)) != len(contracts):
                raise ValueError("plan_contracts_require_one_contract_or_two_distinct_legs")
            if len(contracts) == 2 and (contracts[0][:-4] != contracts[1][:-4] or contracts[0][-4:] >= contracts[1][-4:]):
                raise ValueError("plan_requires_same_product_near_before_far")
            calendars = [plan_calendar(contract, markets, as_of, now, signal_day) for contract in contracts]
            valid_windows = [entry_window(days, signal_day) for days, _ in calendars]
            if any(window != valid_windows[0] for window in valid_windows[1:]):
                raise ValueError("plan_leg_entry_calendar_mismatch")
            valid_days = valid_windows[0]
            result["calendar_checks"] = [basis for _, basis in calendars]
            if iso_date(plan["valid_until"]) != valid_days[-1]:
                raise ValueError("original_valid_until_conflicts_with_two_session_window")
            registered = timestamp(result["registered_at"])
            if registered > now:
                raise ValueError("registration_is_in_future")
            if stamp(registered.date()) < signal_day:
                raise ValueError("registration_before_signal_date")
            completion = None
            if plan.get("signal_completed_at") is not None:
                completion = signal_observation([dict(near_contract=contracts[0], far_contract=contracts[-1],
                    signal_date=signal_day, signal_completed_at=plan["signal_completed_at"],
                    source_refs=plan.get("signal_completed_source_refs"))],
                    (contracts[0], contracts[-1]), signal_day, now)
            elif len(contracts) == 2:
                completion = signal_observation(observations, tuple(contracts), signal_day, now)
            if completion is not None and registered < completion:
                raise ValueError("registration_before_signal_completion")
            result["registration_order_status"] = ("verified_timestamp" if completion is not None else
                "verified_date_order" if stamp(registered.date()) > signal_day else
                "unknown_same_day_signal_completion_time")
            # A date-level calendar cannot establish intraday/night execution availability.
            evaluation = now if stamp(now.date()) == as_of else datetime.combine(
                datetime.strptime(as_of, "%Y%m%d").date(), time(23, 59), CHINA)
            evaluation_day = stamp(evaluation.date())
            remaining = [day for day in valid_days if stamp(day) > evaluation_day]
            unresolved = [day for day in valid_days if stamp(day) == evaluation_day]
            result.update(status="remaining_window" if remaining else "session_check_required" if unresolved else "expired",
                          original_valid_entry_dates=valid_days, remaining_entry_dates=remaining,
                          entry_session_checks_required_dates=unresolved,
                          allowed_execution_session="not_evaluated_require_after_registration")
        except (KeyError, ValueError, TypeError, IndexError) as exc:
            result["issue"] = str(exc)
        results.append(result)
    return results


def evaluate(payload, snapshot, as_of, now, *, anchors=None, plans=None):
    """Pure calculation except reading the paired snapshot. No network or writes."""
    as_of = stamp(as_of)
    report = dict(schema_version=1, refresh_version=VERSION, rule_version=RULE_VERSION,
                  as_of_date=iso_date(as_of), evaluated_at=now.isoformat(), generator="codex",
                  scope="mechanical_refresh_only", refresh_status="failed", issues=[], trend=[],
                  economic_reversion=[], registered_plan_windows=[],
                  calendar_source=CALENDAR_SOURCE,
                  publication_note="18:00 cutoff is a guard, not verified final-settlement publication",
                  execution_permission="not_evaluated", readiness="not_evaluated", final_lots=None,
                  performance_status="not_automated", source_inputs=None,
                  method=dict(canonical="framework/futures_framework.md",
                              canonical_sha256=digest((ROOT / "framework/futures_framework.md").read_bytes()),
                              helper="scripts/futures_strategy.py",
                              helper_sha256=digest((ROOT / "scripts/futures_strategy.py").read_bytes()),
                              refresh_sha256=digest(Path(__file__).read_bytes())))
    try:
        if as_of > stamp(now.date()):
            raise ValueError("future_as_of_not_allowed")
        if not isinstance(payload, dict) or (payload.get("rule_version"), payload.get("script_version"),
                payload.get("scope")) != (RULE_VERSION, "v1.18", "v3_research_inputs_only"):
            raise ValueError("require_v1.18_v3_raw_input_package")
        source_day = stamp(payload["as_of_date"])
        if source_day > as_of:
            raise ValueError("source_as_of_after_requested_date")
        if snapshot is None or Path(snapshot).suffix == ".partial":
            raise ValueError("paired_snapshot_missing_or_incomplete")
        snapshot_raw = Path(snapshot).read_bytes()
        snapshot_text = snapshot_raw.decode("utf-8")
        lines = snapshot_text.rstrip().splitlines()
        pattern = rf"\bAS_OF={source_day}(?!\d)"
        if (not lines or not lines[-1].startswith("== 快照完成 |")
                or not re.search(pattern, lines[-1]) or not re.search(pattern, lines[0])):
            raise ValueError("paired_snapshot_missing_or_incomplete")
        report["evaluated_snapshot_sha256"] = digest(snapshot_raw)
        if "脚本 v1.18" not in lines[-1] or "v1.18" not in lines[0]:
            raise ValueError("snapshot_version_mismatch")
        if "busday近似·口径已降级" in snapshot_text:
            raise ValueError("calendar_degraded_to_weekdays")
        items = payload.get("trend")
        if not isinstance(items, list):
            raise ValueError("trend_inputs_missing")
    except (KeyError, ValueError, TypeError, OSError, UnicodeError) as exc:
        report["issues"].append(str(exc))
        return report

    markets, by_product = {}, {}
    for item in items:
        if not isinstance(item, dict):
            report["issues"].append("trend_item_must_be_object")
            continue
        contract = item.get("contract", "")
        match = re.fullmatch(r"([A-Z]+)\d{4}", contract) if isinstance(contract, str) else None
        product = match[1] if match else None
        if product not in TREND_PRODUCTS:
            continue
        by_product.setdefault(product, []).append(item)
        market = item.get("market_inputs")
        if isinstance(market, dict) and market.get("contract") == contract:
            try:
                if market.get("exchange") != contract_exchange(contract):
                    raise ValueError("raw_contract_exchange_mismatch")
                source_identity(market, contract, market["exchange"])
                markets.setdefault(contract, []).append(calendar_entry(market, contract, market,
                    origin="trend_raw_inputs", price_status="raw_inputs_present_not_reassessed"))
            except (KeyError, ValueError, TypeError) as exc:
                markets.setdefault(contract, []).append(dict(contract=contract,
                    exchange=market.get("exchange"), calendar_issue=str(exc)))
        elif isinstance(market, dict) and market:
            markets.setdefault(contract, []).append(dict(contract=contract,
                exchange=market.get("exchange"), calendar_issue="raw_contract_identity_mismatch"))
    for product in sorted(TREND_PRODUCTS):
        candidates = by_product.get(product, [])
        if len(candidates) != 1:
            report["trend"].append(unknown(product, "require_one_selected_contract_per_product"))
            continue
        item = candidates[0]
        contract, market = item["contract"], item.get("market_inputs", {})
        try:
            expected_line = f"T {contract}: {item['status']} / {item['signal']} /"
            if expected_line not in snapshot_text:
                raise ValueError("snapshot_and_raw_package_disagree")
            if not isinstance(market, dict) or market.get("contract") != contract:
                raise ValueError("raw_contract_identity_mismatch")
            if market.get("exchange") != contract_exchange(contract):
                raise ValueError("raw_contract_exchange_mismatch")
            source_identity(market, contract, market["exchange"])
            checked, days, expected = checked_market(market, as_of, now)
            result = trend_inputs(checked)
            result.update(freshness="fresh", expected_market_trade_date=expected)
            for entry in markets.get(contract, []):
                entry["price_refresh_status"] = "fresh" if result["status"] == "valid" else "incomplete"
            if result["signal"] == "triggered":
                result.update(signal_date=iso_date(expected),
                              valid_entry_dates=entry_window(days, expected),
                              valid_until=entry_window(days, expected)[-1],
                              registered_at=None)
        except (KeyError, ValueError, TypeError, IndexError) as exc:
            result = unknown(contract, str(exc))
            # Calendar provenance remains separate when an old/current bar is absent.
            for entry in markets.get(contract, []):
                entry["price_refresh_status"] = "incomplete"
        report["trend"].append(result)

    anchor_rows = anchors.get("anchors", []) if isinstance(anchors, dict) else (anchors or [])
    if not isinstance(anchor_rows, list):
        report["issues"].append("anchors_must_be_array")
        anchor_rows = []
    if any(not isinstance(anchor, dict) for anchor in anchor_rows):
        report["issues"].append("economic_anchor_must_be_object")
        anchor_rows = [anchor for anchor in anchor_rows if isinstance(anchor, dict)]
    withdrawals = anchors.get("withdrawals", []) if isinstance(anchors, dict) else []
    observations = anchors.get("signal_observations", []) if isinstance(anchors, dict) else []
    if not isinstance(observations, list) or any(not isinstance(row, dict) for row in observations):
        report["issues"].append("signal_observations_must_be_object_array")
        observations = []
    spreads = payload.get("economic_reversion", [])
    if not isinstance(spreads, list):
        report["issues"].append("economic_reversion_must_be_array")
        spreads = []
    supplied_pairs = [(item.get("near_contract"), item.get("far_contract"))
                      for item in spreads if isinstance(item, dict)]
    for anchor in anchor_rows:
        if (anchor.get("near_contract"), anchor.get("far_contract")) not in supplied_pairs:
            report["issues"].append("economic_anchor_pair_has_no_raw_inputs")
    for item in spreads:
        if not isinstance(item, dict):
            report["issues"].append("economic_reversion_item_must_be_object")
            continue
        pair = (item.get("near_contract"), item.get("far_contract"))
        result = dict(near_contract=pair[0], far_contract=pair[1],
                      research_stage=item.get("research_stage"), status="not_evaluated",
                      signal="unknown", reason="frozen_economic_anchor_not_supplied",
                      execution_permission="not_evaluated")
        try:
            pair, market = spread_identity(item)
            for contract in pair:
                markets.setdefault(contract, []).append(calendar_entry(market, contract, market["sources"][contract],
                    origin="spread_leg_raw_inputs", price_status="raw_inputs_present_not_reassessed"))
            matching = [anchor for anchor in anchor_rows if
                        (anchor.get("near_contract"), anchor.get("far_contract")) == pair]
            if len(matching) > 1:
                raise ValueError("duplicate_economic_anchor")
            anchor = matching[0] if matching else None
            frozen = timestamp(anchor["frozen_at"]) if anchor is not None else None
            withdrawn = applicable_withdrawal(withdrawals, pair, as_of, now, frozen_at=frozen)
            if withdrawn is not None:
                result["anchor_withdrawal"] = withdrawn
                raise ValueError("anchor_withdrawn")
            if anchor is not None:
                market, days, expected = checked_market(market, as_of, now, spread=True)
                if frozen > now:
                    raise ValueError("economic_anchor_frozen_in_future")
                if stamp(frozen.date()) > expected:
                    raise ValueError("economic_anchor_frozen_after_signal_date")
                completed = signal_observation(observations, pair, expected, now,
                    fetched_at=[source["fetched_at"] for source in market["sources"].values()])
                if stamp(frozen.date()) == expected:
                    if completed is None:
                        raise ValueError("same_day_anchor_requires_signal_completion_evidence")
                    if frozen >= completed:
                        raise ValueError("economic_anchor_not_frozen_before_signal_completion")
                if stamp(anchor["valid_until"]) < expected:
                    raise ValueError("economic_anchor_expired")
                for key in ("source_refs", "economic_anchor_basis", "convergence_mechanism", "invalidation_basis"):
                    if not anchor.get(key):
                        raise ValueError(f"economic_anchor_missing:{key}")
                market.update(anchor_low=anchor["anchor_low"], anchor_high=anchor["anchor_high"])
                result = reversion_inputs(market)
                result.update(freshness="fresh", expected_market_trade_date=expected,
                              anchor=anchor, economic_validity="requires_research_review",
                              anchor_timing_basis="verified_timestamp" if completed else "prior_date_freeze",
                              signal_completed_at=completed.isoformat() if completed else None)
                if result["signal"] == "triggered":
                    result.update(signal_date=iso_date(expected), valid_entry_dates=entry_window(days, expected),
                                  valid_until=entry_window(days, expected)[-1], registered_at=None)
        except (KeyError, ValueError, TypeError, IndexError) as exc:
            result.update(status="incomplete", reason=str(exc))
            # A known malformed exact input cannot be hidden by a T-calendar fallback.
            if str(exc).startswith(("raw_pair_", "price_source_contract_identity", "require_same_product")):
                for contract in pair:
                    try:
                        exchange = contract_exchange(contract)
                    except ValueError:
                        continue
                    markets.setdefault(contract, []).append(dict(contract=contract, exchange=exchange,
                        calendar_issue=str(exc)))
        report["economic_reversion"].append(result)
    if plans is not None:
        report["registered_plan_windows"] = check_plans(plans, markets, as_of, now, observations=observations)
    full = all(row["status"] == "valid" for row in report["trend"])
    partial = any(row.get("freshness") == "fresh" for row in report["trend"])
    failed_v = any(row["status"] == "incomplete" for row in report["economic_reversion"])
    failed_plan = any(row["status"] == "incomplete" for row in report["registered_plan_windows"])
    report["refresh_status"] = ("fresh" if full and not failed_v and not failed_plan and not report["issues"]
                                else "partial" if partial else "failed")
    return report


def discover_inputs(root, as_of):
    """Newest source day first; absence never creates a pretend empty signal set."""
    paths = list((root / "output/cache/futures").glob("v3_research_inputs_*.json"))
    paths += list((root / "output/futures-refresh-fetch").glob("*/*/v3_research_inputs_*.json"))
    found = []
    for path in paths:
        match = re.fullmatch(r"v3_research_inputs_(\d{8})\.json", path.name)
        if not match or match[1] > as_of:
            continue
        snapshot = (root / "research/futures/snapshots" / f"{iso_date(match[1])}-data-snapshot.txt"
                    if path.parent == root / "output/cache/futures" else path.parent / "data-snapshot.txt")
        if snapshot_complete(snapshot, match[1]):
            found.append((match[1], path.stat().st_mtime_ns, path, snapshot))
    return [(path, snapshot) for _, _, path, snapshot in sorted(found, reverse=True)]


def fetch_isolated(root, as_of, python):
    """Run the unchanged collector with isolated output and atomic snapshot writer."""
    directory = root / "output/futures-refresh-fetch" / iso_date(as_of)
    directory.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="run-", dir=directory))
    snapshot = run / "data-snapshot.txt"
    code = ("import sys\nfrom pathlib import Path\nfrom scripts import future_data as data\n"
            "from scripts.research_paths import snapshot_output\n"
            "data.AS_OF = sys.argv[1]\ndata.OUTDIR = Path(sys.argv[2])\n"
            "target = Path(sys.argv[3])\n"
            "with snapshot_output(target, data.AS_OF):\n    data.run(target)\n")
    # Credentials stay in the inherited environment, never command arguments.
    # API output is held in the isolated log, not echoed into an error summary.
    with (run / "collector.log").open("w", encoding="utf-8") as log:
        try:
            process = subprocess.run([python, "-c", code, as_of, str(run), str(snapshot)],
                                     cwd=root, stdout=log, stderr=log, timeout=900, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, None, f"collector_failed:{type(exc).__name__}"
    if process.returncode or not snapshot_complete(snapshot, as_of):
        return None, None, f"collector_failed:exit_{process.returncode}:isolated_partial_preserved"
    return run / f"v3_research_inputs_{as_of}.json", snapshot, None


def save_report(report, root, source_files):
    """Stage evidence first; the final exclusive JSON link is the commit marker.

    A failed publish leaves an isolated .partial staging directory, never an
    empty/truncated formal JSON. Prior revisions are never replaced. Each source
    is read once and checked against its digest from the evaluation, when given.
    """
    day = report["as_of_date"]
    base = artifact_path("futures", "signal-refresh", day, root=root)
    directory = base.parent
    directory.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        stem = base.stem + (f"-r{index}" if index > 1 else "")
        target = directory / f"{stem}.json"
        markdown = directory / f"{stem}.md"
        evidence = directory / "evidence" / stem
        lock = directory / f".{stem}.lock"
        if target.exists() or markdown.exists() or evidence.exists():
            index += 1
            continue
        try:
            lock.mkdir()
            break
        except FileExistsError:
            index += 1
    published = []
    try:
        staging_parent = root / "output/futures-refresh-staging" / day
        staging_parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=stem + "-", suffix=".partial", dir=staging_parent))
        raw_directory = staging / "evidence"
        raw_directory.mkdir()
        manifest = []
        for source_item in source_files:
            label, source = source_item[:2]
            expected_hash = source_item[2] if len(source_item) == 3 else None
            if source is None or not Path(source).is_file():
                if expected_hash:
                    raise ValueError(f"evaluated_source_disappeared:{label}")
                continue
            raw = Path(source).read_bytes()
            if expected_hash and digest(raw) != expected_hash:
                raise ValueError(f"evaluated_source_changed:{label}")
            frozen = evidence / f"{label}{Path(source).suffix}"
            (raw_directory / frozen.name).write_bytes(raw)
            manifest.append(dict(role=label, original_path=str(Path(source).resolve()),
                                 path=str(frozen.relative_to(root)), sha256=digest(raw), bytes=len(raw)))
        report["source_inputs"] = manifest
        report["complete"] = True
        staged_json = staging / target.name
        staged_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                               encoding="utf-8")
        staged_markdown = staging / markdown.name
        staged_markdown.write_text(render_markdown(report, target), encoding="utf-8")
        evidence.parent.mkdir(parents=True, exist_ok=True)
        raw_directory.rename(evidence)
        # link() fails if a destination exists; no accidental concurrent overwrite.
        os.link(staged_markdown, markdown)
        published.append(markdown)
        os.link(staged_json, target)
        published.append(target)
    except Exception:
        for path in reversed(published):
            path.unlink(missing_ok=True)
        raise
    finally:
        lock.rmdir()
    # Successful evidence is in research; staging files are disposable only now.
    shutil.rmtree(staging, ignore_errors=True)
    return target, markdown


def render_markdown(report, target):
    day = report["as_of_date"]
    lines = [f"# 期货轻量行情刷新 · {day}", "", f"刷新状态：**{report['refresh_status']}**。",
             "仅检查行情与原信号时钟；不更新产业观点、方法参数或账户风险，不授予交易许可。",
             f"实际评估：{report['evaluated_at']}；日历：{report['calendar_source']}。",
             "18:00 为完整日线保护，不能证明最终结算已发布。夜盘归属、当前报价和 G1–G6 另核。", "",
             "| 合约 | 输入状态 | 价格信号 | 行情日 | 原信号截止 |", "|---|---|---|---|---|"]
    for row in report["trend"]:
        lines.append(f"| {row['contract']} | {row['status']} | {row['signal']} / {row.get('side')} | "
                     f"{row.get('market_trade_date', 'unknown')} | {row.get('valid_until', '—')} |")
    lines += ["", "V 仅使用显式提交且提前冻结的经济锚；未提供锚为 not_evaluated。",
              "既有计划检查保留原 signal_date / registered_at / valid_until，不重置两交易日窗口。",
              "本报告没有登记新交易计划；经济依据、执行规则及账户条件需单独复核。", "",
              f"详细结果及缺项：[JSON]({target.name})。精确原料和 SHA-256 见 source_inputs。"]
    selection = report.get("input_selection", {})
    if selection:
        lines += ["", f"所用输入：`{selection.get('selected')}`。来源选择与跳过记录见 input_selection。"]
        skipped = [row for row in selection.get("attempted", [])
                   if row["path"] != selection.get("selected")]
        if skipped:
            lines += [f"本次另检查了 {len(skipped)} 份未采纳输入；不将其缺失或失败记录抹去。"]
    if report["issues"]:
        lines += ["", "缺项：" + "；".join(report["issues"])]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default=datetime.now(CHINA).date().isoformat())
    parser.add_argument("--input", type=Path, help="Exact v1.18 raw JSON package")
    parser.add_argument("--snapshot", type=Path, help="Paired complete v1.18 text snapshot")
    parser.add_argument("--anchors", type=Path, help="JSON anchors[]; optional signal_observations[] timing evidence and withdrawals[] invalidation evidence")
    parser.add_argument("--plans", type=Path, help="JSON or one-JSON-block audit Markdown with candidates[].plan")
    parser.add_argument("--fetch", action="store_true", help="Allow missing/stale data fetch into an isolated run")
    parser.add_argument("--check-only", action="store_true", help="Offline validation; no network and no files written")
    parser.add_argument("--python", default=sys.executable, help="Collector interpreter, normally environment.md's Python")
    args = parser.parse_args(argv)
    if args.check_only and args.fetch:
        parser.error("--check-only cannot be combined with --fetch")
    if args.snapshot and not args.input:
        parser.error("--snapshot requires --input")
    now = datetime.now(CHINA)
    try:
        as_of = stamp(args.as_of)
        if as_of > stamp(now.date()):
            parser.error("--as-of cannot be in the future")
        anchors, anchors_hash = load_json(args.anchors, with_digest=True) if args.anchors else (None, None)
        plans, plans_hash = load_json(args.plans, with_digest=True) if args.plans else (None, None)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    candidates = [(args.input, args.snapshot)] if args.input else discover_inputs(ROOT, as_of)
    selected, snapshot, selected_hash = None, None, None
    attempted = []
    report = evaluate({}, None, as_of, now)
    report["issues"] = ["no_complete_v1.18_input_found"]
    for path, snap in candidates:
        try:
            payload, source_hash = load_json(path, with_digest=True)
            result = evaluate(payload, snap, as_of, now, anchors=anchors, plans=plans)
        except (ValueError, OSError, UnicodeError) as exc:
            source_hash = None
            result = evaluate({}, None, as_of, now)
            result["issues"] = [f"input_read_failed:{type(exc).__name__}"]
        attempted.append(dict(path=str(path), snapshot=str(snap), refresh_status=result["refresh_status"],
                              issues=result["issues"], raw_sha256=source_hash,
                              price_gaps=[dict(contract=row.get("contract"),
                                               missing_fields=row.get("missing_fields", []))
                                          for row in result["trend"] if row["status"] != "valid"]))
        ranks = {"failed": 0, "partial": 1, "fresh": 2}
        if selected is None or ranks[result["refresh_status"]] > ranks[report["refresh_status"]]:
            report, selected, snapshot, selected_hash = result, path, snap, source_hash
        if result["refresh_status"] == "fresh":
            break
    needs_fetch = not report["trend"] or any(row.get("freshness") != "fresh" or row["status"] != "valid"
                                             for row in report["trend"])
    if args.fetch and needs_fetch:
        path, snap, error = fetch_isolated(ROOT, as_of, args.python)
        if error:
            report["issues"].append(error)
            if report["refresh_status"] == "fresh":
                report["refresh_status"] = "partial"
        else:
            try:
                payload, source_hash = load_json(path, with_digest=True)
                report = evaluate(payload, snap, as_of, datetime.now(CHINA), anchors=anchors, plans=plans)
                selected, snapshot, selected_hash = path, snap, source_hash
            except (OSError, ValueError, UnicodeError) as exc:
                report["issues"].append(f"collector_package_invalid:{type(exc).__name__}")
    report["input_selection"] = dict(selected=str(selected) if selected else None,
                                    selected_sha256=selected_hash, attempted=attempted,
                                    selected_snapshot=str(snapshot) if snapshot else None)
    if args.check_only:
        print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        source_files = [("market-inputs", selected, selected_hash),
                        ("data-snapshot", snapshot, report.get("evaluated_snapshot_sha256")),
                        ("frozen-anchors", args.anchors, anchors_hash), ("registered-plans", args.plans, plans_hash)]
        try:
            target, markdown = save_report(report, ROOT, source_files)
        except (OSError, ValueError) as exc:
            print(json.dumps(dict(refresh_status="failed", issue=f"publish_failed:{type(exc).__name__}",
                                  report=None, execution_permission="not_evaluated")))
            return 2
        print(json.dumps(dict(refresh_status=report["refresh_status"], json=str(target),
                              report=str(markdown), execution_permission="not_evaluated"), ensure_ascii=False))
    return 0 if report["refresh_status"] == "fresh" else 2


if __name__ == "__main__":
    raise SystemExit(main())
