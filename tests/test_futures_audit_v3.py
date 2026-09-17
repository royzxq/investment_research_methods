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


def research_complete(doc):
    candidate = doc["candidates"][0]
    candidate.update(signal="triggered", plan=dict(entry=3050, stop=2960, targets=[3230], latest_exit_date="2026-10-09"))
    return candidate


def shadow(**changes):
    plan = dict(shadow_id="MA-plan-shadow-1", candidate_id="MA-plan", registered_at="2026-09-07T20:00:00+08:00",
                instrument=dict(type="single", contracts=["MA2701"]), side="long", entry_type="limit",
                entry=3050, stop=2960, target=3230, entry_expiry="2026-09-11", latest_exit_date="2026-10-09",
                multiplier=10, round_trip_cost=40)
    plan.update(changes)
    return plan


class FeedbackLoopAuditTests(unittest.TestCase):
    def test_research_complete_except_account_cannot_hide_as_incomplete(self):
        doc = current(); candidate = research_complete(doc)
        self.assertTrue(any("requires awaiting_account" in e for e in validate_audit(doc)))
        candidate["status"] = "awaiting_account"
        self.assertEqual(validate_audit(doc), [])

    def test_all_listed_checks_passing_with_unverified_account_is_awaiting_account(self):
        doc = current(); candidate = research_complete(doc)
        candidate.update(evaluated_checks=[dict(rule_id="#1", applicable=True, result="pass", evidence_refs=["inventory"])],
                         unknown_checks=[])
        self.assertTrue(any("requires awaiting_account" in e for e in validate_audit(doc)))
        candidate["status"] = "awaiting_account"
        self.assertEqual(validate_audit(doc), [])

    def test_awaiting_account_rejects_research_gaps_failures_verified_accounts_and_schema_2(self):
        def plan_unfinished(doc, c): c["plan"]["stop"] = None
        def research_gap(doc, c): c["evaluated_checks"][0]["gap"].update(kind="plan", owner="research")
        def known_failure(doc, c):
            c["evaluated_checks"].append(dict(rule_id="#16", applicable=True, result="fail", evidence_refs=["inventory"]))
            c.update(all_blockers=["#16"], first_blocker="#16")
        def account_verified(doc, c): verified_account(doc)
        def old_schema(doc, c): doc.update(audit_schema_version=2, framework=dict(doc["framework"], version="v2.22"))
        for change in (plan_unfinished, research_gap, known_failure, account_verified, old_schema):
            with self.subTest(change=change.__name__):
                doc = current(); candidate = research_complete(doc); candidate["status"] = "awaiting_account"
                change(doc, candidate)
                self.assertTrue(any("awaiting_account requires" in e for e in validate_audit(doc)), validate_audit(doc))

    def test_backdated_shadow_registration_is_rejected(self):
        doc = current(); doc["shadow_plans"] = [shadow(registered_at="2026-08-29T20:00:00+08:00")]  # 9 days before as_of
        self.assertTrue(any("backdated" in e for e in validate_audit(doc)))
        doc["shadow_plans"] = [shadow(registered_at="2026-09-02T20:00:00+08:00")]  # inside the report week
        self.assertEqual(validate_audit(doc), [])

    def test_research_complete_needs_an_evaluated_rule_and_a_numeric_plan(self):
        doc = current(); candidate = research_complete(doc)
        candidate.update(evaluated_checks=[], unknown_checks=[])
        self.assertEqual(validate_audit(doc), [])  # nothing evaluated: incomplete is right
        candidate["status"] = "awaiting_account"
        self.assertTrue(any("awaiting_account requires" in e for e in validate_audit(doc)))
        for plan_change in (dict(entry="tbd"), dict(targets=[]), dict(targets=["3230"]), dict(latest_exit_date="20261009")):
            with self.subTest(plan_change=plan_change):
                doc = current(); candidate = research_complete(doc); candidate["plan"].update(plan_change)
                self.assertEqual(validate_audit(doc), [])
                candidate["status"] = "awaiting_account"
                self.assertTrue(any("awaiting_account requires" in e for e in validate_audit(doc)))

    def test_shadow_plans_are_frozen_ordered_and_linked(self):
        doc = current(); doc["shadow_plans"] = [shadow()]
        self.assertEqual(validate_audit(doc), [])
        doc["shadow_plans"] = [shadow(instrument=dict(type="spread", contracts=["MA2701", "MA2705"]), entry=-20, stop=-40, target=10)]
        self.assertEqual(validate_audit(doc), [])
        bad = {
            "later than as_of_date": dict(registered_at="2026-09-08T09:00:00+08:00"),
            "timezone-qualified timestamp": dict(registered_at="2026-09-07"),
            "stop and target on opposite sides": dict(stop=3100),
            "must reference an audited candidate": dict(candidate_id="other"),
            "requires 2 distinct contracts": dict(instrument=dict(type="spread", contracts=["MA2701"])),
            "cannot precede registration": dict(entry_expiry="2026-09-06"),
            "cannot precede entry_expiry": dict(latest_exit_date="2026-09-10"),
            "expected finite positive number": dict(multiplier=True),
            "expected finite nonnegative number": dict(round_trip_cost=-1),
        }
        for fragment, changes in bad.items():
            with self.subTest(fragment=fragment):
                doc = current(); doc["shadow_plans"] = [shadow(**changes)]
                self.assertTrue(any(fragment in e for e in validate_audit(doc)), validate_audit(doc))
        doc = current(); doc["shadow_plans"] = [shadow(), shadow()]
        self.assertTrue(any("unique nonempty ID" in e for e in validate_audit(doc)))


if __name__ == "__main__": unittest.main()
