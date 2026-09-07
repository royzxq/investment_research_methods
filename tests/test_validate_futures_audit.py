"""Offline report-schema regressions; no data refresh or source verification."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate_futures_audit import load_audit, validate_audit


def evidence():
    return dict(evidence_id="inventory", metric="registered_warehouse_inventory",
                value=1200, unit="tonne", observation_date="2026-09-04",
                published_at="2026-09-04T16:00:00+08:00", source_url_or_file="user-export.csv",
                original_source="exchange export supplied by user", price_basis=None,
                comparison_basis="level only", role="required_model", quality="verified",
                time_scope="current")


def audit():
    return dict(
        audit_schema_version=2, as_of_date="2026-09-07", research_mode="public_data",
        framework={"path": "framework/futures_framework.md", "version": "v2.22"},
        snapshot={"market_trade_date": "2026-09-04", "market_captured_at": None,
                  "account": dict(actual_position_status="unknown", verified_at=None,
                                  evidence=None, equity=None, open_positions=None,
                                  pending_orders=None, existing_risk=None, reserved_order_risk=None,
                                  margin_available=None, configured_equity=150000)},
        coverage={"completeness": "partial"}, evidence=[evidence()], unresolved_items=[],
        candidates=[dict(data_feasibility="available", signal="triggered", status="incomplete",
                         evaluated_checks=[dict(rule_id="#31", applicable=True, result="unknown",
                                                evidence_refs=[])], all_blockers=[], unknown_checks=["#31"],
                         first_blocker=None, only_blocker=None, final_lots=None)])


def verified_account(document, *, positions=False):
    document["snapshot"]["account"].update(
        actual_position_status="verified_positions" if positions else "verified_flat",
        verified_at="2026-09-07T08:00:00+08:00", evidence="account-snapshot.csv", equity=150000,
        open_positions=[{"contract": "MA2701", "lots": 1}] if positions else [],
        pending_orders=[], existing_risk=1000 if positions else 0, reserved_order_risk=0,
        margin_available=100000)


def checks(document, results):
    candidate = document["candidates"][0]
    candidate["evaluated_checks"] = [dict(rule_id=rule, applicable=applicable, result=result,
                                          evidence_refs=["inventory"])
                                     for rule, applicable, result in results]
    candidate["all_blockers"] = [rule for rule, applicable, result in results
                                 if applicable and result == "fail"]
    candidate["unknown_checks"] = [rule for rule, applicable, result in results
                                   if applicable and result == "unknown"]
    candidate["first_blocker"] = next(iter(candidate["all_blockers"]), None)
    return candidate


class AuditStructureTests(unittest.TestCase):
    def assert_error(self, document, fragment):
        errors = validate_audit(document)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_unknown_account_does_not_prevent_valid_incomplete_research(self):
        self.assertEqual(validate_audit(audit()), [])

    def test_inapplicable_structure_exemption_cannot_be_failed_or_unknown(self):
        for result in ("fail", "unknown"):
            with self.subTest(result=result):
                document = audit()
                checks(document, [("#16", False, result)])
                self.assert_error(document, "inapplicable check")
        document = audit()
        checks(document, [("#16", False, "not_applicable"), ("#31", True, "unknown")])
        self.assertEqual(validate_audit(document), [])

    def test_unknown_and_known_blockers_are_not_interchangeable(self):
        document = audit()
        candidate = checks(document, [("#1", True, "fail"), ("#31", True, "unknown")])
        candidate["first_blocker"] = "#1"
        self.assertEqual(validate_audit(document), [])
        candidate["all_blockers"].append("#31")
        self.assert_error(document, "all_blockers: must equal")
        candidate["all_blockers"] = ["#1"]
        candidate["unknown_checks"] = []
        self.assert_error(document, "unknown_checks: must equal")

    def test_only_blocker_tristate_preserves_unfinished_checks(self):
        cases = [([], True, False), ([("#1", True, "fail")], True, True),
                 ([("#1", True, "fail"), ("#31", True, "unknown")], True, False),
                 ([("#1", True, "fail")], False, False),
                 ([("#1", True, "fail"), ("#2", True, "fail")], False, True),
                 ([("#1", True, "fail"), ("#31", True, "unknown")], None, True)]
        for results, only, valid in cases:
            with self.subTest(results=results, only=only):
                document = audit()
                candidate = checks(document, results)
                candidate["only_blocker"] = only
                matching = [error for error in validate_audit(document) if ".only_blocker:" in error]
                self.assertEqual(not matching, valid, matching)

    def test_first_blocker_must_reference_a_known_applicable_failure(self):
        document = audit()
        document["candidates"][0]["first_blocker"] = "#31"
        self.assert_error(document, "first_blocker: must reference")
        document["candidates"][0]["first_blocker"] = ["#31"]
        self.assert_error(document, "first_blocker: expected")

    def test_first_blocker_follows_explicit_or_default_evaluation_order(self):
        document = audit()
        candidate = checks(document, [("#1", True, "fail"), ("#2", True, "fail"),
                                      ("#31", True, "unknown")])
        self.assertEqual(validate_audit(document), [])
        candidate["first_blocker"] = "#2"
        self.assert_error(document, "first fail in evaluation order")
        candidate["evaluation_order"] = ["#31", "#2", "#1"]
        self.assertEqual(validate_audit(document), [])
        for order in (["#1", "#2"], ["#1", "#2", "#31", "#31"],
                      ["#1", "#2", "#31", "#99"], {"#1": 1}, ["#1", []]):
            with self.subTest(order=order):
                candidate["evaluation_order"] = order
                self.assert_error(document, "evaluation_order")
        candidate["evaluation_order"] = ["#31", "#2", "#1"]
        candidate["first_blocker"] = None
        self.assert_error(document, "first fail in evaluation order")

    def test_unknown_account_cannot_be_zero_filled(self):
        for field, value in (("equity", 0), ("open_positions", []), ("pending_orders", []),
                             ("existing_risk", 0), ("reserved_order_risk", 0),
                             ("margin_available", 0)):
            with self.subTest(field=field):
                document = audit()
                document["snapshot"]["account"][field] = value
                self.assert_error(document, f"snapshot.account.{field}: must be null")
        document = audit()
        document["candidates"][0]["final_lots"] = 0
        self.assert_error(document, "final_lots: must be null")

    def test_ready_requires_verified_account_and_consistent_passes(self):
        for positions in (False, True):
            document = audit()
            verified_account(document, positions=positions)
            candidate = checks(document, [("#31", True, "pass"), ("#16", False, "not_applicable")])
            candidate.update(status="ready", final_lots=1)
            self.assertEqual(validate_audit(document), [])
        for change in ({"signal": "unknown"}, {"signal": "not_triggered"},
                       {"data_feasibility": "research_only"}, {"data_feasibility": "temporary_gap"},
                       {"final_lots": 0}, {"final_lots": None}):
            with self.subTest(change=change):
                changed = copy.deepcopy(document)
                changed["candidates"][0].update(change)
                self.assert_error(changed, "ready requires")

    def test_ready_rejects_unknown_or_failed_checks_and_unverified_snapshot(self):
        for result in ("unknown", "fail"):
            document = audit()
            verified_account(document)
            candidate = checks(document, [("#1", True, result)])
            candidate.update(status="ready", final_lots=1)
            self.assert_error(document, "ready requires")
        document = audit()
        candidate = checks(document, [("#1", True, "pass")])
        candidate.update(status="ready", final_lots=1)
        self.assert_error(document, "ready requires")

    def test_lots_are_integers_not_boolean_or_numeric_strings(self):
        for lots in (True, False, 1.5, -1, "1", {}):
            with self.subTest(lots=lots):
                document = audit()
                document["candidates"][0]["final_lots"] = lots
                self.assert_error(document, "expected nonnegative integer or null")

    def test_invalid_signal_or_no_signal_label_is_rejected(self):
        for signal in ("incomplete", "no_signal", True, [], None):
            document = audit()
            document["candidates"][0]["signal"] = signal
            self.assert_error(document, ".signal: expected")
        document = audit()
        document["candidates"][0].update(signal="not_triggered", status="no_signal")
        self.assertEqual(validate_audit(document), [])
        document["candidates"][0]["signal"] = "triggered"
        self.assert_error(document, "no_signal requires")

    def test_blocked_does_not_hide_account_or_gate_gaps(self):
        document = audit()
        candidate = checks(document, [("#1", True, "fail"), ("#31", True, "unknown")])
        candidate["status"] = "blocked"
        self.assert_error(document, "unresolved checks/account require incomplete")
        verified_account(document)
        candidate = checks(document, [("#1", True, "fail")])
        self.assertEqual(validate_audit(document), [])
        candidate = checks(document, [("#1", True, "pass")])
        candidate["final_lots"] = 0
        self.assertEqual(validate_audit(document), [])

    def test_required_verified_evidence_needs_value_dates_units_and_sources(self):
        for field in ("value", "unit", "observation_date", "published_at",
                      "source_url_or_file", "original_source"):
            with self.subTest(field=field):
                document = audit()
                document["evidence"][0][field] = None
                self.assert_error(document, f"evidence[0].{field}:")

    def test_optional_missing_context_and_explicit_history_are_not_auto_blockers(self):
        document = audit()
        optional = evidence()
        optional.update(evidence_id="shipping_context", role="optional_context", quality="missing",
                        value=None, unit=None, observation_date=None, published_at=None,
                        original_source=None, source_url_or_file=None)
        document["evidence"].append(optional)
        historical = evidence()
        historical.update(evidence_id="old_inventory", time_scope="historical",
                          observation_date="2025-08-27", published_at="2025-08-29")
        document["evidence"].append(historical)
        self.assertEqual(validate_audit(document), [])

    def test_future_dates_are_rejected_including_timezone_day_boundary(self):
        for field, value in (("observation_date", "2026-09-08"),
                             ("published_at", "2026-09-07T17:00:00Z")):
            document = audit()
            document["evidence"][0][field] = value
            self.assert_error(document, "later than as_of_date")
        document = audit()
        document["snapshot"]["market_trade_date"] = "2026-09-08"
        self.assert_error(document, "snapshot.market_trade_date: later")

    def test_dates_require_a_year_and_valid_calendar_date(self):
        for value in ("8/27", "2026-02-30", 20260827):
            document = audit()
            document["evidence"][0]["observation_date"] = value
            self.assert_error(document, "evidence[0].observation_date:")
        document = audit()
        document["evidence"][0]["published_at"] = "2026-09-04T10:00:00"
        self.assert_error(document, "timezone-qualified")

    def test_evidence_references_and_duplicate_rule_ids_are_checked(self):
        document = audit()
        candidate = checks(document, [("#1", True, "pass"), ("#1", True, "pass")])
        self.assert_error(document, "duplicate rule ID")
        candidate["evaluated_checks"] = candidate["evaluated_checks"][:1]
        candidate["evaluated_checks"][0]["evidence_refs"] = ["invented_source"]
        self.assert_error(document, "unresolved evidence ID")
        document["evidence"].append(evidence())
        self.assert_error(document, "duplicate ID inventory")

    def test_malformed_nested_structures_return_errors_not_exceptions(self):
        for value in (None, [], "report", 0):
            self.assertTrue(validate_audit(value))
        for field, value in (("snapshot", []), ("framework", None), ("coverage", []),
                             ("candidates", {}), ("candidates", [None]), ("evidence", [True]),
                             ("unresolved_items", ["missing"])):
            with self.subTest(field=field, value=value):
                document = audit()
                document[field] = value
                self.assertTrue(validate_audit(document))
        document = audit()
        document["candidates"][0].update(evaluated_checks=[None, {"rule_id": [], "applicable": 1,
                                                               "result": {}, "evidence_refs": [False]}],
                                          all_blockers=[{}], unknown_checks="unknown")
        self.assertTrue(validate_audit(document))

    def test_schema_version_and_direct_nonfinite_values_are_rejected(self):
        for version in (1, True, 2.0, "2"):
            document = audit()
            document["audit_schema_version"] = version
            self.assert_error(document, "audit_schema_version")
        document = audit()
        document["evidence"][0]["value"] = float("nan")
        self.assert_error(document, "non-finite number")

    def test_container_values_for_status_and_only_blocker_do_not_crash(self):
        for field in ("status", "signal", "data_feasibility", "only_blocker", "first_blocker"):
            for value in ([], {}):
                with self.subTest(field=field, value=value):
                    document = audit()
                    document["candidates"][0][field] = value
                    self.assertTrue(validate_audit(document))


class AuditInputTests(unittest.TestCase):
    def run_cli(self, args, source=None):
        process = subprocess.run([sys.executable, str(ROOT / "scripts/validate_futures_audit.py")] + args,
                                 input=source, text=True, capture_output=True)
        self.assertNotIn("Traceback", process.stderr)
        output = json.loads(process.stdout)
        self.assertEqual(output["scope"], "structure_validation_only")
        self.assertEqual(output["execution_permission"], "not_evaluated")
        return process.returncode, output

    def test_json_and_single_markdown_audit_block(self):
        source = json.dumps(audit())
        self.assertEqual(load_audit(source), audit())
        markdown = "# Audit\n\n```yaml\nold: not_the_audit\n```\n\n```json\n" + source + "\n```\n"
        self.assertEqual(load_audit(markdown, markdown=True), audit())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.md"
            path.write_text(markdown, encoding="utf-8")
            self.assertEqual(self.run_cli([str(path)])[0], 0)
            path = Path(directory) / "report.json"
            path.write_text(source, encoding="utf-8")
            self.assertEqual(self.run_cli(["--input", str(path)])[0], 0)

    def test_invalid_json_duplicate_keys_and_nonfinite_numbers(self):
        for source in ('{"audit_schema_version":', '{"a":1,"a":2}', '{"a":{"b":1,"b":2}}',
                       '{"a":NaN}', '{"a":Infinity}', "[]"):
            with self.subTest(source=source):
                code, output = self.run_cli(["--input", "-"], source)
                self.assertEqual(code, 2)
                self.assertTrue(output["errors"])

    def test_missing_or_multiple_json_blocks_are_ambiguous(self):
        block = "```json\n" + json.dumps(audit()) + "\n```\n"
        for source in ("# Audit\nNo JSON", "# Audit\n" + block * 2,
                       "# Audit\n```json\n{}"):
            code, output = self.run_cli(["--input", "-"], source)
            self.assertEqual(code, 2)
            self.assertIn("exactly one", output["errors"][0])

    def test_input_errors_and_boolean_lots_have_structured_output(self):
        self.assertEqual(self.run_cli(["--input", "/nonexistent/futures-report.json"])[0], 2)
        self.assertEqual(self.run_cli([])[0], 2)
        document = audit()
        document["candidates"][0]["final_lots"] = True
        code, output = self.run_cli(["--input", "-"], json.dumps(document))
        self.assertEqual(code, 2)
        self.assertTrue(any("never boolean" in error for error in output["errors"]))


if __name__ == "__main__":
    unittest.main()
