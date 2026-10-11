"""Local persistence and cross-worktree regression tests; no market/network calls."""
from copy import deepcopy
from datetime import datetime, timedelta
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import futures_continuity as continuity
from scripts import futures_handoff as handoff


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "main"
        self.root.mkdir()
        self.now = datetime(2026, 10, 11, 20, 0, tzinfo=handoff.CHINA)
        owner = self

        class Clock(datetime):
            @classmethod
            def now(cls, tz=None):
                return owner.now if tz else owner.now.replace(tzinfo=None)

        for patcher in (patch.object(continuity, "datetime", Clock),
                        patch.object(handoff, "_now", side_effect=lambda: self.now)):
            patcher.start()
            self.addCleanup(patcher.stop)
        chunks = ["# Futures v3.0\n"]
        for name in handoff.RULE_ANCHORS:
            chunks.append(f'<a id="{name}"></a>\n## Label\nEffective rule for {name}: 20/10; 2ATR.\n')
        self.write(self.root, handoff.CANONICAL, "\n".join(chunks))
        for path in handoff.SOURCE_DEPENDENCIES:
            self.write(self.root, path, '"""Fixture calculation source."""\nVALUE=2\n')
        self.git(self.root, "init", "--quiet")
        self.git(self.root, "config", "user.email", "fixture@example.invalid")
        self.git(self.root, "config", "user.name", "Fixture")
        self.git(self.root, "add", "framework", "scripts")
        self.git(self.root, "commit", "--quiet", "-m", "fixture")
        self.store = continuity.default_store(self.root)

    def git(self, root, *args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def write(self, root, relative, data):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode())
        return path

    def json_file(self, root, relative, value):
        return self.write(root, relative, json.dumps(value, ensure_ascii=False, indent=2) + "\n")

    def worktree(self, name):
        destination = self.base / name
        self.git(self.root, "worktree", "add", "--quiet", "--detach", str(destination), "HEAD")
        return destination

    def candidate(self, **changes):
        result = dict(opportunity_id="MA2701-trend-20261008", candidate_id="original-candidate",
                      strategy="trend", contracts=["MA2701"], direction="long", trade_date="2026-10-09",
                      status="ready", final_lots=2, execution_permission="allowed",
                      evaluated_checks=[dict(rule_id=rule, applicable=True, result="pass") for rule in ("G1", "G2", "G3", "G4", "G5", "G6")],
                      risk_evaluation=dict(result=dict(status="valid", final_lots=2, execution_permission="allowed")),
                      plan=dict(signal_date="2026-10-08", registered_at="2026-10-08T17:00:00+08:00",
                                valid_until="2026-10-12", entry=3300, stop=3100, entry_range=[3290, 3310],
                                targets=None, latest_exit_date="2026-11-04",
                                exit_rule="initial_2atr_and_prior10_channel_tighten_only_max20_sessions"))
        result.update(changes)
        return result

    def register(self, root=None, *, day="2026-10-11", revision=None, candidate=None,
                 correction=None, evidence_corrections=None):
        root = root or self.root
        suffix = f"-r{revision}" if revision else ""
        relative = f"research/futures/weekly/{day}/{day}-execution-audit{suffix}.md"
        audit = dict(audit_schema_version=3, as_of_date=day, framework=dict(version="v3.0"),
                     snapshot=dict(market_trade_date="2026-10-09"),
                     candidates=[candidate if candidate is not None else self.candidate()])
        if evidence_corrections:
            audit["evidence_corrections"] = evidence_corrections
        self.write(root, relative, "# Adopted audit\n```json\n" + json.dumps(audit) + "\n```\n")
        scopes, supersedes = [], []
        if correction:
            original = "research/futures/weekly/2026-10-09/2026-10-09-market-research.md"
            self.write(root, original, "# Original market observations\nSources from original day.\n")
            scopes, supersedes = [correction], [original]
        result = handoff.register(root, day, "2026-10-09", scope="local", method_version="v3.0",
                                 method_revision="fixture reviewed current rules", artifacts={"execution_audit": relative},
                                 correction_scope=scopes, supersedes=supersedes,
                                 replace=(root / handoff.manifest_relative(day)).exists())
        return result["manifest"]

    def publish(self, root=None, *, manifest=None, anchors=None, producer="daily"):
        root = root or self.root
        return continuity.publish(root, continuity.default_store(root), manifest=manifest, anchors=anchors, producer=producer)

    def collect(self, root=None, *, as_of="2026-10-11", name="collected"):
        root = root or self.root
        result = continuity.collect(root, continuity.default_store(root), as_of, root / "output" / name)
        folder = Path(result["output"])
        return result, {key: json.loads((folder / f"{key}.json").read_text()) for key in ("continuity", "plans", "anchors")}

    def anchor(self, **changes):
        anchor = dict(near_contract="MA2701", far_contract="MA2705", anchor_low=-100, anchor_high=100,
                      frozen_at="2026-10-08T09:00:00+08:00", valid_until="2026-10-20",
                      source_refs=["https://example.invalid/original-evidence"],
                      economic_anchor_basis="synthetic-storage-band", convergence_mechanism="synthetic-arrival",
                      invalidation_basis="synthetic-delay")
        anchor.update(changes)
        return anchor

    def anchor_package(self, name="anchors", *, rows=None, withdrawals=None, observations=None):
        relative = f"research/futures/weekly/2026-10-11/evidence/{name}.json"
        package = dict(anchors=rows if rows is not None else [self.anchor()])
        if withdrawals is not None:
            package["withdrawals"] = withdrawals
        if observations is not None:
            package["signal_observations"] = observations
        self.json_file(self.root, relative, package)
        return relative

    def withdrawal(self, **changes):
        item = dict(near_contract="MA2701", far_contract="MA2705", invalidated_at="2026-10-10T10:00:00+08:00",
                    reason="Independent supply evidence invalidated frozen mechanism",
                    source_refs=["https://example.invalid/correction-source"])
        item.update(changes)
        return item

    def test_real_worktrees_share_store_and_survive_producer_removal(self):
        daily = self.worktree("daily")
        weekly = self.worktree("weekly")
        self.assertEqual(continuity.default_store(daily), self.store)
        self.assertEqual(continuity.default_store(weekly), self.store)
        manifest = self.register(daily)
        stored = self.publish(daily, manifest=manifest)
        self.git(self.root, "worktree", "remove", "--force", str(daily))
        self.assertFalse(daily.exists())
        result, exported = self.collect(weekly)
        self.assertEqual(result["candidates"], 1)
        candidate = exported["plans"]["candidates"][0]
        self.assertEqual(candidate["opportunity_id"], self.candidate()["opportunity_id"])
        self.assertEqual(candidate["plan"], self.candidate()["plan"])
        self.assertTrue((Path(result["output"]) / "sources" / stored["entry_id"] / manifest).is_file())
        self.assertFalse(exported["continuity"]["publication_verified"])

    def test_original_clock_and_id_survive_daily_weekly_updates_without_readiness(self):
        daily = self.register(day="2026-10-10")
        self.publish(manifest=daily)
        self.now += timedelta(minutes=10)
        weekly = self.register(candidate=self.candidate(candidate_id="weekly-review-id"))
        self.publish(manifest=weekly, producer="weekly")
        _, exported = self.collect()
        self.assertEqual(len(exported["plans"]["candidates"]), 1)
        row = exported["plans"]["candidates"][0]
        self.assertEqual(row["opportunity_id"], self.candidate()["opportunity_id"])
        self.assertEqual(row["plan"]["signal_date"], "2026-10-08")
        self.assertEqual(row["plan"]["registered_at"], "2026-10-08T17:00:00+08:00")
        self.assertEqual(row["plan"]["valid_until"], "2026-10-12")
        self.assertEqual(row["status"], "incomplete")
        self.assertIsNone(row["final_lots"])
        self.assertEqual(row["execution_permission"], "not_evaluated")
        self.assertFalse(exported["continuity"]["execution_reuse"])

    def test_changed_method_is_reassessment_only(self):
        manifest = self.register()
        self.publish(manifest=manifest)
        canonical = self.root / handoff.CANONICAL
        canonical.write_text(canonical.read_text().replace("2ATR", "3ATR"))
        _, exported = self.collect()
        self.assertEqual(exported["plans"]["candidates"], [])
        pending = exported["continuity"]["requires_method_reassessment"]
        self.assertEqual(pending[0]["opportunity_id"], self.candidate()["opportunity_id"])
        self.assertEqual(pending[0]["original"]["plan"], self.candidate()["plan"])

    def test_explicit_and_audit_corrections_accumulate(self):
        first = self.register(day="2026-10-10", correction="Source period corrected", evidence_corrections=[{"id": "C1"}])
        self.publish(manifest=first)
        second = self.register(correction="Signal applicability corrected", evidence_corrections=[{"id": "C2"}])
        self.publish(manifest=second, producer="weekly")
        _, exported = self.collect()
        corrections = exported["continuity"]["corrections"]
        self.assertEqual(len(corrections), 4)
        text = json.dumps(corrections)
        self.assertIn("Source period corrected", text)
        self.assertIn("Signal applicability corrected", text)
        self.assertIn("C1", text)
        self.assertIn("C2", text)

    def test_clock_conflict_is_not_overwritten_or_resurrected(self):
        self.publish(manifest=self.register(day="2026-10-09"))
        changed = self.candidate()
        changed["plan"]["valid_until"] = "2026-10-13"
        self.publish(manifest=self.register(day="2026-10-10", candidate=changed))
        self.publish(manifest=self.register(candidate=self.candidate()))
        result, exported = self.collect()
        self.assertEqual(result["status"], "needs_reconciliation")
        self.assertEqual(exported["plans"]["candidates"], [])
        self.assertTrue(exported["continuity"]["conflicts"])

    def test_same_opportunity_different_ids_is_not_chosen(self):
        self.publish(manifest=self.register(day="2026-10-10"))
        self.publish(manifest=self.register(candidate=self.candidate(opportunity_id="different-id")))
        result, exported = self.collect()
        self.assertEqual(result["status"], "needs_reconciliation")
        self.assertEqual(exported["plans"]["candidates"], [])

    def test_equal_effective_time_different_frozen_plans_require_reconciliation(self):
        first = self.register()
        self.publish(manifest=first)
        changed = self.candidate()
        changed["plan"]["stop"] = 3000
        second = self.register(revision=2, candidate=changed)
        self.publish(manifest=second)
        result, exported = self.collect()
        self.assertEqual(result["status"], "needs_reconciliation")
        self.assertEqual(exported["plans"]["candidates"], [])

    def test_latest_damaged_object_is_not_silently_skipped(self):
        self.publish(manifest=self.register(day="2026-10-10"))
        latest = self.publish(manifest=self.register())
        entry = json.loads((self.store / "entries" / f"{latest['entry_id']}.json").read_text())
        reference = entry["files"][handoff.manifest_relative("2026-10-11")]
        (self.store / reference["object"]).write_text("corrupted newest source")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.collect()
        self.assertFalse((self.root / "output/collected").exists())

    def test_latest_damaged_entry_and_index_do_not_fall_back(self):
        self.publish(manifest=self.register(day="2026-10-10"))
        latest = self.publish(manifest=self.register())
        entry_path = self.store / "entries" / f"{latest['entry_id']}.json"
        entry_path.write_text("corrupt")
        with self.assertRaises(ValueError):
            self.collect()
        self.assertFalse((self.root / "output/collected").exists())
        (self.store / "index.json").write_text('{"schema":"wrong","entries":[]}')
        with self.assertRaises(ValueError):
            self.collect()

    def test_identical_manifest_publish_is_idempotent(self):
        manifest = self.register()
        first = self.publish(manifest=manifest)
        self.now += timedelta(minutes=1)
        second = self.publish(manifest=manifest, producer="weekly")
        self.assertEqual(first["entry_id"], second["entry_id"])
        self.assertEqual(len(continuity.index_read(self.store)["entries"]), 1)

    def test_identical_anchors_only_publish_is_idempotent(self):
        anchors = self.anchor_package()
        first = self.publish(anchors=anchors)
        self.now += timedelta(minutes=1)
        second = self.publish(anchors=anchors)
        self.assertEqual(first["entry_id"], second["entry_id"])
        self.assertEqual(len(continuity.index_read(self.store)["entries"]), 1)

    def test_existing_export_is_never_overwritten(self):
        self.publish(manifest=self.register())
        result, _ = self.collect()
        sentinel = Path(result["output"]) / "continuity.json"
        before = sentinel.read_bytes()
        with self.assertRaisesRegex(ValueError, "fresh output"):
            self.collect()
        self.assertEqual(sentinel.read_bytes(), before)

    def test_collect_empty_store_direct_api_creates_output_parent(self):
        self.assertFalse((self.root / "output").exists())
        result, exported = self.collect()
        self.assertEqual(result["candidates"], 0)
        self.assertEqual(exported["continuity"]["consumed"], [])

    def test_anchor_conflict_cannot_be_resurrected_by_third_record(self):
        first = self.anchor_package("a1")
        second = self.anchor_package("a2", rows=[self.anchor(anchor_high=120)])
        third = self.anchor_package("a3")
        for relative in (first, second, third):
            self.publish(anchors=relative)
            self.now += timedelta(minutes=1)
        result, exported = self.collect()
        self.assertEqual(result["status"], "needs_reconciliation")
        self.assertEqual(exported["anchors"]["anchors"], [])

    def test_signal_observation_conflict_cannot_be_resurrected(self):
        observation = dict(near_contract="MA2701", far_contract="MA2705", signal_date="2026-10-09",
                           signal_completed_at="2026-10-09T15:10:00+08:00", source_refs=["https://example.invalid/settlement"])
        changed = dict(observation, signal_completed_at="2026-10-09T15:20:00+08:00")
        for i, row in enumerate((observation, changed, observation)):
            relative = self.anchor_package(f"observation-{i}", observations=[row])
            self.publish(anchors=relative)
            self.now += timedelta(minutes=1)
        result, exported = self.collect()
        self.assertEqual(result["status"], "needs_reconciliation")
        self.assertEqual(exported["anchors"]["signal_observations"], [])

    def test_withdrawal_removes_old_anchor_and_retains_audit(self):
        self.publish(anchors=self.anchor_package("frozen"))
        self.publish(anchors=self.anchor_package("withdrawn", rows=[], withdrawals=[self.withdrawal()]))
        _, exported = self.collect()
        self.assertEqual(exported["anchors"]["anchors"], [])
        self.assertEqual(exported["anchors"]["withdrawals"][0]["invalidated_at"], "2026-10-10T10:00:00+08:00")
        self.assertIn("Independent supply", json.dumps(exported["anchors"]["withdrawals"]))

    def test_new_anchor_after_withdrawal_can_be_used_without_erasing_withdrawal(self):
        self.publish(anchors=self.anchor_package("old"))
        self.publish(anchors=self.anchor_package("withdraw", rows=[], withdrawals=[self.withdrawal()]))
        self.publish(anchors=self.anchor_package("renewed", rows=[self.anchor(frozen_at="2026-10-11T09:00:00+08:00")]))
        _, exported = self.collect()
        self.assertEqual(len(exported["anchors"]["anchors"]), 1)
        self.assertEqual(exported["anchors"]["anchors"][0]["frozen_at"], "2026-10-11T09:00:00+08:00")
        self.assertEqual(len(exported["anchors"]["withdrawals"]), 1)

    def test_method_change_keeps_withdrawal_and_prevents_old_anchor_resurrection(self):
        self.publish(anchors=self.anchor_package("old"))
        self.publish(anchors=self.anchor_package("withdrawn", rows=[], withdrawals=[self.withdrawal()]))
        canonical = self.root / handoff.CANONICAL
        canonical.write_text(canonical.read_text().replace("2ATR", "3ATR"))
        self.publish(anchors=self.anchor_package("new-method-import", rows=[self.anchor()]))
        _, exported = self.collect()
        self.assertEqual(exported["anchors"]["anchors"], [])
        withdrawal = exported["anchors"]["withdrawals"][0]
        self.assertEqual(withdrawal["invalidated_at"], self.withdrawal()["invalidated_at"])
        self.assertFalse(withdrawal["continuity_source"]["method_compatible"])

    def test_latest_no_plan_disposition_blocks_old_candidate_until_later_reassessment(self):
        original = self.candidate(evaluated_at="2026-10-09T17:00:00+08:00")
        self.publish(manifest=self.register(day="2026-10-09", candidate=original))
        withdrawn = self.candidate(status="blocked", plan=None, final_lots=None,
                                  evaluated_at="2026-10-10T17:00:00+08:00",
                                  all_blockers=["economic_basis_invalidated"])
        self.publish(manifest=self.register(day="2026-10-10", candidate=withdrawn))
        result, exported = self.collect(name="after-withdrawal")
        self.assertEqual(result["status"], "needs_reassessment")
        self.assertEqual(exported["plans"]["candidates"], [])
        pending = exported["continuity"]["requires_plan_reassessment"][0]
        self.assertEqual(pending["latest_observation"]["status"], "blocked")
        self.assertEqual(pending["original_plan"], original["plan"])
        self.assertEqual(len(exported["continuity"]["review_scope"]), 2)
        # A fresh, explicitly adopted reassessment can restore the same clock;
        # a later capture of the older disposition cannot remove it again.
        newer = self.candidate(evaluated_at="2026-10-11T17:00:00+08:00")
        self.publish(manifest=self.register(candidate=newer))
        self.publish(manifest=self.register(revision=2, candidate=withdrawn))
        result, exported = self.collect(name="after-reassessment")
        self.assertEqual(result["status"], "collected")
        self.assertEqual(exported["continuity"]["requires_plan_reassessment"], [])
        self.assertEqual(exported["plans"]["candidates"][0]["plan"], original["plan"])
        self.assertEqual(exported["plans"]["candidates"][0]["evaluated_at"], newer["evaluated_at"])
        shifted = self.candidate(evaluated_at="2026-10-11T18:00:00+08:00")
        shifted["plan"]["valid_until"] = "2026-10-13"
        self.publish(manifest=self.register(revision=3, candidate=shifted))
        result, exported = self.collect(name="after-illegal-clock-change")
        self.assertEqual(result["status"], "needs_reconciliation")
        self.assertEqual(exported["plans"]["candidates"], [])
        self.assertTrue(any(x["reason"] == "original_clock_or_identity_changed"
                            for x in exported["continuity"]["conflicts"]))

    def test_asof_does_not_apply_later_withdrawal_or_observation(self):
        manifest = self.register(day="2026-10-09")
        anchors = self.anchor_package("future-withdrawal", withdrawals=[self.withdrawal()], observations=[dict(
            near_contract="MA2701", far_contract="MA2705", signal_date="2026-10-10",
            signal_completed_at="2026-10-10T15:10:00+08:00", source_refs=["https://example.invalid/settlement"])])
        self.publish(manifest=manifest, anchors=anchors)
        _, exported = self.collect(as_of="2026-10-09")
        self.assertEqual(len(exported["anchors"]["anchors"]), 1)
        self.assertEqual(exported["anchors"]["withdrawals"], [])
        self.assertEqual(exported["anchors"]["signal_observations"], [])

    def test_invalid_withdrawals_are_not_persisted(self):
        for i, item in enumerate((self.withdrawal(invalidated_at="2026-10-12T10:00:00+08:00"),
                                  self.withdrawal(invalidated_at="2026-10-10T10:00:00"),
                                  self.withdrawal(reason=""), self.withdrawal(source_refs=[]),
                                  self.withdrawal(far_contract="RB2705"))):
            relative = self.anchor_package(f"invalid-withdrawal-{i}", rows=[], withdrawals=[item])
            with self.subTest(item=item), self.assertRaises(ValueError):
                self.publish(anchors=relative)
        self.assertEqual(continuity.index_read(self.store)["entries"], [])

    def test_account_gates_and_nested_capacity_do_not_survive_as_current_approval(self):
        self.publish(manifest=self.register())
        _, exported = self.collect()
        candidate = exported["plans"]["candidates"][0]
        self.assertFalse(any(check.get("rule_id") in {"G5", "G6"} and check.get("result") == "pass"
                             for check in candidate.get("evaluated_checks", [])))
        self.assertIsNone((candidate.get("risk_evaluation") or {}).get("result"))
        history = exported["continuity"]["review_scope"]
        self.assertEqual(history[0]["candidates"][0]["status"], "ready")
        self.assertFalse(history[0]["current_account_verified"])

    def test_explicit_historical_import_retains_original_method_identity(self):
        manifest = self.register()
        old = json.loads((self.root / manifest).read_text())["method"]
        canonical = self.root / handoff.CANONICAL
        canonical.write_text(canonical.read_text().replace("2ATR", "3ATR"))
        with self.assertRaisesRegex(ValueError, "incompatible"):
            self.publish(manifest=manifest)
        stored = continuity.publish(self.root, self.store, manifest=manifest, allow_historical=True)
        entry, _ = continuity.load_entry(self.store, stored["entry_id"])
        self.assertEqual(entry["method"], old)
        _, exported = self.collect()
        self.assertEqual(exported["plans"]["candidates"], [])
        self.assertEqual(len(exported["continuity"]["requires_method_reassessment"]), 1)

    def test_earlier_evaluation_registered_later_does_not_replace_current_observation(self):
        current = self.candidate(evaluated_at="2026-10-10T17:00:00+08:00", observation="newer evidence")
        self.publish(manifest=self.register(day="2026-10-10", candidate=current))
        older = self.candidate(evaluated_at="2026-10-09T17:00:00+08:00", observation="older evidence")
        self.publish(manifest=self.register(candidate=older))
        _, exported = self.collect()
        self.assertEqual(exported["plans"]["candidates"][0]["observation"], "newer evidence")

    def test_future_evaluation_never_supersedes_valid_current_candidate(self):
        self.publish(manifest=self.register(day="2026-10-10"))
        future = self.candidate(evaluated_at="2026-10-12T17:00:00+08:00")
        self.publish(manifest=self.register(candidate=future))
        result, exported = self.collect()
        self.assertEqual(result["status"], "needs_reconciliation")
        self.assertEqual(exported["plans"]["candidates"], [])
        self.assertTrue(exported["continuity"]["conflicts"])


    def test_publish_missing_link_or_changed_adopted_source_fails_without_index(self):
        manifest = self.register()
        document = json.loads((self.root / manifest).read_text())
        audit_path = document["artifacts"]["execution_audit"]["path"]
        self.write(self.root, audit_path, "changed original evidence")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.publish(manifest=manifest)
        self.assertEqual(continuity.index_read(self.store)["entries"], [])

    def refresh_evidence(self, *, declared_hash=None, omit_hash=False):
        frozen = "research/futures/refresh/2026-10-11/evidence/frozen/market-inputs.json"
        raw = b'{"frozen": true}\n'
        self.write(self.root, frozen, raw)
        old_cache = "output/futures-refresh-fetch/2026-10-11/removed-run/market-inputs.json"
        source = dict(role="market-inputs", original_path=str(self.root / old_cache), path=frozen,
                      sha256=declared_hash or continuity.digest(raw), bytes=len(raw))
        if omit_hash:
            source.pop("sha256")
        report = "research/futures/refresh/2026-10-11/2026-10-11-signal-refresh.json"
        self.json_file(self.root, report, dict(source_inputs=[source], input_selection=dict(
            selected=old_cache, attempted=[dict(path=old_cache, snapshot="output/removed/snapshot.txt")],
            selected_snapshot="output/removed/snapshot.txt")))
        return report, frozen, raw

    def test_refresh_frozen_source_metadata_survives_deleted_original_cache(self):
        report, frozen, raw = self.refresh_evidence()
        snapshot = "research/futures/refresh/2026-10-11/evidence/frozen/data-snapshot.txt"
        snapshot_raw = b"Raw snapshot; old cache=output/removed/data-snapshot.txt\n"
        self.write(self.root, snapshot, snapshot_raw)
        document = json.loads((self.root / report).read_text())
        document["source_inputs"].append(dict(role="data-snapshot", original_path="output/removed/data-snapshot.txt",
                                              path=snapshot, sha256=continuity.digest(snapshot_raw), bytes=len(snapshot_raw)))
        self.json_file(self.root, report, document)
        markdown = report.replace(".json", ".md")
        self.write(self.root, markdown, "# Refresh\n所用输入：`output/removed/market-inputs.json`。来源选择与跳过记录见 input_selection。\n"
                   + f"[JSON]({Path(report).name})\n")
        stored = continuity.publish(self.root, self.store, manifest=self.register(), evidence=[markdown])
        entry, files = continuity.load_entry(self.store, stored["entry_id"])
        self.assertEqual(files[frozen], raw)
        self.assertEqual(entry["files"][frozen]["sha256"], continuity.digest(raw))
        self.assertEqual(files[snapshot], snapshot_raw)
        self.assertFalse(any("removed" in path for path in files))

    def test_refresh_declared_frozen_hash_mismatch_is_rejected(self):
        report, _, _ = self.refresh_evidence(declared_hash="0" * 64)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            continuity.publish(self.root, self.store, manifest=self.register(), evidence=[report])
        self.assertEqual(continuity.index_read(self.store)["entries"], [])

    def test_refresh_source_missing_declared_hash_is_not_guessed(self):
        report, _, _ = self.refresh_evidence(omit_hash=True)
        with self.assertRaisesRegex(ValueError, "source_inputs require"):
            continuity.publish(self.root, self.store, manifest=self.register(), evidence=[report])
        self.assertEqual(continuity.index_read(self.store)["entries"], [])


if __name__ == "__main__":
    unittest.main()
