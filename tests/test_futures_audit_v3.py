"""Report A regressions: ownership, honest status, withdrawn evidence reuse."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_validate_futures_audit import audit, checks, verified_account, validate_audit


def current():
    doc = audit()
    doc.update(audit_schema_version=3, evidence_corrections=[])
    doc["framework"]["version"] = "v2.24"
    doc["candidates"][0].update(candidate_id="MA-plan", plan={})
    doc["candidates"][0]["evaluated_checks"][0]["gap"] = dict(kind="account", owner="user", next_action="核实账户快照", due_at="before_execution")
    return doc


class CurrentAuditTests(unittest.TestCase):
    def test_new_version_requires_current_schema(self):
        doc = current(); self.assertEqual(validate_audit(doc), [])
        doc["audit_schema_version"] = 2
        self.assertTrue(any("v2.24+" in e for e in validate_audit(doc)))

    def test_unfinished_plan_is_owned_by_research_not_user(self):
        doc = current(); gap = doc["candidates"][0]["evaluated_checks"][0]["gap"]
        gap.update(kind="definition", owner="user")
        self.assertTrue(any("requires research" in e for e in validate_audit(doc)))
        gap["owner"] = "research"
        self.assertEqual(validate_audit(doc), [])

    def test_unknown_requires_specific_next_action_and_owner(self):
        doc = current(); del doc["candidates"][0]["evaluated_checks"][0]["gap"]
        self.assertTrue(any("gap" in e for e in validate_audit(doc)))

    def test_governance_deadline_is_not_a_release_schedule(self):
        doc = current(); gap = doc["candidates"][0]["evaluated_checks"][0]["gap"]
        gap.update(kind="not_published", owner="publisher", due_at="2026-09-14")
        self.assertTrue(any("publication schedule" in e for e in validate_audit(doc)))
        gap.update(expected_release_at="2026-09-11T20:30:00+08:00", release_evidence_refs=["inventory"])
        # Structural only: the validator cannot prove this fixture's content is a schedule.
        self.assertEqual(validate_audit(doc), [])

    def test_single_failure_is_not_proven_only_blocker_with_unknown_account(self):
        doc = current(); c = checks(doc, [("#1", True, "fail")]); c["only_blocker"] = True
        self.assertTrue(any("true requires a verified account" in e for e in validate_audit(doc)))
        c["only_blocker"] = None
        self.assertEqual(validate_audit(doc), [])

    def test_no_signal_needs_direct_proof_but_not_account_or_plan(self):
        doc = current(); c = doc["candidates"][0]
        c.update(signal="not_triggered", status="no_signal", evaluated_checks=[], unknown_checks=[])
        self.assertTrue(any("direct trigger evidence" in e for e in validate_audit(doc)))
        c["signal_evidence_refs"] = ["inventory"]
        self.assertEqual(validate_audit(doc), [])

    def test_old_year_evidence_cannot_remain_a_d14_failure(self):
        doc = current(); verified_account(doc)
        doc["evidence"][0].update(quality="invalid", observation_date="2025-09-05", published_at="2025-09-06", time_scope="historical")
        c = checks(doc, [("D14-water", True, "fail")]); c["status"] = "blocked"
        self.assertTrue(any("fail requires verified" in e for e in validate_audit(doc)))
        c["evaluated_checks"][0]["evidence_refs"] = []
        c["evaluated_checks"][0]["diagnostic_evidence_refs"] = ["inventory"]
        doc["evidence_corrections"] = [dict(withdrawn_evidence_id="inventory", reason="原文为2025，撤回旧触发",
                                           affected_checks=[dict(candidate_id="MA-plan", rule_id="D14-water")], recalculation="pending")]
        self.assertTrue(any("pending correction cannot preserve" in e for e in validate_audit(doc)))
        c.update(status="incomplete", all_blockers=[], first_blocker=None, unknown_checks=["D14-water"])
        c["evaluated_checks"][0].update(result="unknown", gap=dict(kind="acquisition", owner="research", next_action="核实替代周度247家样本", due_at="next_report"))
        self.assertEqual(validate_audit(doc), [])
        doc["evidence_corrections"][0]["affected_checks"][0]["rule_id"] = "D14-other"
        self.assertTrue(any("unresolved candidate/check" in e for e in validate_audit(doc)))

    def test_known_fail_plus_account_unknown_stays_incomplete(self):
        doc = current()
        doc["candidates"][0]["evaluated_checks"].append(dict(rule_id="#1", applicable=True, result="fail", evidence_refs=["inventory"]))
        doc["candidates"][0].update(all_blockers=["#1"], first_blocker="#1", status="blocked")
        self.assertTrue(any("unresolved checks/account" in e for e in validate_audit(doc)))
        doc["candidates"][0]["status"] = "incomplete"
        self.assertEqual(validate_audit(doc), [])


if __name__ == "__main__": unittest.main()
