"""Real-file/Git boundary tests for explicit futures report adoption."""
from contextlib import redirect_stdout
from datetime import datetime
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import futures_handoff as handoff


class HandoffTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.now = datetime(2026, 10, 11, 20, 0, tzinfo=handoff.CHINA)
        clock = patch.object(handoff, "_now", return_value=self.now)
        clock.start()
        self.addCleanup(clock.stop)
        chunks = ["# 期货框架 v3.0\n"]
        for name in handoff.RULE_ANCHORS:
            body = "Rules: 20/10; 2ATR; 0.5ATR; 3.5%."
            if name == "r-v3-state":
                body = "state A"
            elif name == "r-v3-retirement":
                body = "Retired rules."
            chunks.append(f'<a id="{name}"></a>\n## Display heading\n{body}\n')
        self.canonical = self.write(handoff.CANONICAL, "\n".join(chunks))
        for path in handoff.SOURCE_DEPENDENCIES:
            self.write(path, '"""Fixture helper."""\nVALUE = 2\n')


    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
        return path

    def report(self, kind="market_research", day="2026-10-11", revision=None):
        suffix = f"-r{revision}" if revision else ""
        relative = f"research/futures/weekly/{day}/{day}-{kind.replace('_', '-')}{suffix}.md"
        if kind == "execution_audit":
            audit = {"audit_schema_version": 3, "as_of_date": day,
                     "framework": {"version": "v3.0"},
                     "snapshot": {"market_trade_date": "2026-10-09"},
                     "candidates": [{"strategy": "trend", "status": "incomplete",
                                     "trade_date": "2026-10-09", "plan": {"signal_date": "2026-10-09"}}]}
            text = "# Current audit\n```json\n" + json.dumps(audit) + "\n```\n"
        else:
            text = f"# {day} {kind} {revision}\nFacts and source dates.\n"
        self.write(relative, text)
        return relative

    def register(self, day="2026-10-11", **kwargs):
        options = {"scope": "local", "method_version": "v3.0", "method_revision": "HEAD+local",
                   "artifacts": {"market_research": self.report(day=day)}}
        options.update(kwargs)
        return handoff.register(self.root, day, "2026-10-09", **options)

    def manifest(self, day="2026-10-11"):
        return self.root / handoff.manifest_relative(day)

    def mutate_manifest(self, change, day="2026-10-11"):
        path = self.manifest(day)
        document = json.loads(path.read_text())
        change(document)
        path.write_text(json.dumps(document), encoding="utf-8")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def init_git(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")

    def commit(self):
        self.git("add", "framework", "research", "scripts")
        self.git("commit", "--quiet", "-m", "fixture")

    def test_exact_revision_adoption_and_null_slots(self):
        report = self.report(revision=2)
        self.report(revision=99)
        result = self.register(artifacts={"market_research": report})
        loaded = handoff.resolve(self.root, "2026-10-11")
        self.assertEqual(loaded["handoff"]["artifacts"]["market_research"]["path"], report)
        self.assertIsNone(loaded["handoff"]["artifacts"]["change_decision"])
        self.assertEqual(result["handoff"]["status"], "adopted")
        self.assertTrue(loaded["method_compatible"])
        self.assertFalse(loaded["execution_reuse"])
        self.assertFalse(loaded["candidate_continuity_compatible"])
        self.assertTrue(loaded["requires_fresh_evaluation"])

    def test_unregistered_revision_does_not_become_latest(self):
        self.report(revision=3)
        relative = handoff.manifest_relative("2026-10-11").replace("-handoff.json", "-handoff-r3.json")
        self.write(relative, '{"status":"adopted"}')
        result = handoff.resolve(self.root, "2026-10-11")
        self.assertEqual(result["status"], "missing")
        self.assertTrue(result["legacy_fallback_allowed"])

    def test_asof_before_and_no_mtime_selection(self):
        self.register("2026-10-10")
        self.register()
        before = handoff.resolve(self.root, "2026-10-11", before=True)
        self.assertEqual(before["handoff"]["as_of_date"], "2026-10-10")
        current = handoff.resolve(self.root, "2026-10-11")
        self.assertEqual(current["handoff"]["as_of_date"], "2026-10-11")

    def test_same_day_registration_never_overwrites_implicitly(self):
        self.register()
        original = self.manifest().read_bytes()
        with self.assertRaisesRegex(ValueError, "replace"):
            self.register()
        self.assertEqual(self.manifest().read_bytes(), original)

    def test_replace_preserves_manifest_and_original_report_hash(self):
        first = self.register()
        original = self.manifest().read_bytes()
        old_report = first["handoff"]["artifacts"]["market_research"]
        revision = self.report(revision=2)
        self.register(artifacts={"market_research": revision}, replace=True,
                      correction_scope=["Correct source date only"], supersedes=[old_report["path"]])
        result = handoff.resolve(self.root, "2026-10-11")
        old = result["handoff"]["previous_handoff"]
        self.assertEqual((self.root / old["path"]).read_bytes(), original)
        self.assertEqual(old["sha256"], handoff.digest(original))
        self.assertEqual(result["handoff"]["corrections"]["supersedes"][0], old_report)

    def test_replace_cannot_launder_changed_original(self):
        first = self.register()
        old = first["handoff"]["artifacts"]["market_research"]["path"]
        self.write(old, "mutated original")
        original_manifest = self.manifest().read_bytes()
        revision = self.report(revision=2)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            handoff.register(self.root, "2026-10-11", "2026-10-09", scope="local",
                             method_version="v3.0", method_revision="local",
                             artifacts={"market_research": revision}, replace=True)
        self.assertEqual(self.manifest().read_bytes(), original_manifest)

    def test_invalid_new_registration_does_not_create_formal_or_archive(self):
        self.register()
        original = self.manifest().read_bytes()
        with self.assertRaisesRegex(ValueError, "method version"):
            self.register(method_version="v2.28", replace=True)
        self.assertEqual(self.manifest().read_bytes(), original)
        self.assertFalse((self.manifest().parent / "evidence/handoff-history").exists())

    def test_changed_archived_manifest_is_rejected(self):
        self.register()
        self.register(artifacts={"market_research": self.report(revision=2)}, replace=True)
        document = json.loads(self.manifest().read_text())
        self.write(document["previous_handoff"]["path"], "corrupted")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            handoff.resolve(self.root, "2026-10-11")

    def test_state_only_refresh_is_compatible_but_rule_edit_is_not(self):
        result = self.register()
        original_sha = result["handoff"]["method"]["canonical_full_sha256"]
        self.canonical.write_text(self.canonical.read_text().replace("state A", "state B"))
        resolved = handoff.resolve(self.root, "2026-10-11")
        self.assertTrue(resolved["method_compatible"])
        self.assertNotEqual(handoff.method_fingerprint(self.root)["canonical_full_sha256"], original_sha)
        self.canonical.write_text(self.canonical.read_text().replace("2ATR", "3ATR"))
        with self.assertRaisesRegex(ValueError, "incompatible"):
            handoff.resolve(self.root, "2026-10-11")
        historical = handoff.resolve(self.root, "2026-10-11", allow_historical=True)
        self.assertFalse(historical["method_compatible"])
        self.assertFalse(historical["execution_reuse"])
        self.assertFalse(historical["candidate_continuity_compatible"])
        self.assertTrue(historical["requires_fresh_evaluation"])

    def test_retirement_text_is_not_excluded_from_method_fingerprint(self):
        before = handoff.method_fingerprint(self.root)
        self.canonical.write_text(self.canonical.read_text().replace("Retired", "Reactivated"))
        self.assertNotEqual(before["sha256"], handoff.method_fingerprint(self.root)["sha256"])

    def test_duplicate_or_missing_state_anchors_rejected(self):
        original = self.canonical.read_text()
        for changed in [original.replace(handoff.STATE_START, ""), original + handoff.STATE_START,
                        original.replace(handoff.STATE_START, handoff.STATE_END)]:
            with self.subTest(changed=changed):
                self.canonical.write_text(changed)
                with self.assertRaises(ValueError):
                    handoff.method_fingerprint(self.root)

    def test_newest_incompatible_record_never_falls_back(self):
        self.register("2026-10-10")
        self.register()
        self.mutate_manifest(lambda data: data["method"].update(sha256="0" * 64))
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            handoff.resolve(self.root, "2026-10-11")

    def test_newest_corrupt_record_never_falls_back(self):
        self.register("2026-10-10")
        self.register()
        self.manifest().write_text("broken json")
        with self.assertRaises(ValueError):
            handoff.resolve(self.root, "2026-10-11")

    def test_unknown_status_scope_and_schema_are_not_skipped(self):
        self.register("2026-10-10")
        self.register()
        original = self.manifest().read_bytes()
        for key, value in [("status", "draft"), ("scope", "unreviewed"), ("schema", "v42")]:
            with self.subTest(key=key):
                self.manifest().write_bytes(original)
                self.mutate_manifest(lambda data: data.update({key: value}))
                with self.assertRaises(ValueError):
                    handoff.resolve(self.root, "2026-10-11")

    def test_hash_damage_is_not_legacy_fallback(self):
        self.register()
        self.write(self.report(), "changed after adoption")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            handoff.resolve(self.root, "2026-10-11")

    def test_corrected_original_hash_is_checked(self):
        original = self.report(revision=2)
        current = self.report(revision=3)
        self.register(artifacts={"market_research": current},
                      correction_scope=["Source date"], supersedes=[original])
        self.write(original, "changed historical record")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            handoff.resolve(self.root, "2026-10-11")

    def test_correction_requires_both_scope_and_original(self):
        original = self.report(revision=2)
        for kwargs in [{"correction_scope": ["correct date"]}, {"supersedes": [original]}]:
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, "both"):
                self.register(**kwargs)
        self.assertFalse(self.manifest().exists())

    def test_future_registration_market_and_research_dates_rejected(self):
        with self.assertRaises(ValueError):
            self.register("2026-10-12")
        with self.assertRaises(ValueError):
            handoff.register(self.root, "2026-10-11", "2026-10-12", scope="local",
                             method_version="v3.0", method_revision="local",
                             artifacts={"market_research": self.report()})
        self.register()
        self.mutate_manifest(lambda data: data.update(registered_at="2026-10-11T21:00:00+08:00"))
        with self.assertRaisesRegex(ValueError, "Future"):
            handoff.resolve(self.root, "2026-10-11")
        with self.assertRaisesRegex(ValueError, "future"):
            handoff.resolve(self.root, "2026-10-12")

    def test_timestamp_requires_shanghai_offset(self):
        self.register()
        self.mutate_manifest(lambda data: data.update(registered_at="2026-10-11T10:00:00"))
        with self.assertRaisesRegex(ValueError, "timezone"):
            handoff.resolve(self.root, "2026-10-11")

    def test_wrong_track_type_period_and_revision_rejected(self):
        good = self.report()
        bad_paths = [good.replace("futures", "investment"), good.replace("market-research", "execution-audit"),
                     good.replace("2026-10-11-market", "2026-10-10-market"),
                     good.replace(".md", "-r1.md"), good.replace(".md", ".md.partial")]
        for relative in bad_paths:
            self.write(relative, "# report")
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                self.register(artifacts={"market_research": relative})
        with self.assertRaises(ValueError):
            self.register(artifacts={"market_research": self.report(day="2026-10-10")})

    def test_unsafe_paths_and_symlink_escape_rejected(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        external = Path(outside.name) / "source.md"
        external.write_text("external")
        good = self.report()
        (self.root / good).unlink()
        (self.root / good).symlink_to(external)
        for relative in [good, str(external), "../source.md", "research//futures/a.md", "./research/a.md"]:
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                self.register(artifacts={"market_research": relative})
        self.assertFalse(self.manifest().exists())

    def test_output_directory_symlink_escape_rejected(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        directory = self.root / "research/futures/weekly/2026-10-11"
        directory.parent.mkdir(parents=True)
        directory.symlink_to(Path(outside.name), target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.register(artifacts={})
        self.assertFalse((Path(outside.name) / "2026-10-11-handoff.json").exists())

    def test_nonfinite_and_duplicate_json_rejected(self):
        for text in ['{"x":NaN}', '{"x":Infinity}', '{"x":1e999}', '{"x":1,"x":2}']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                handoff.read_json(text)

    def test_empty_and_nonutf8_reports_rejected(self):
        relative = self.report()
        for data in [b" ", b"\xff"]:
            self.write(relative, data)
            with self.subTest(data=data), self.assertRaises((ValueError, UnicodeError)):
                handoff.register(self.root, "2026-10-11", "2026-10-09", scope="local",
                                 method_version="v3.0", method_revision="local",
                                 artifacts={"market_research": relative})

    def test_audit_compatibility_and_market_anchor(self):
        audit = self.report("execution_audit", revision=3)
        self.register(artifacts={"execution_audit": audit})
        resolved = handoff.resolve(self.root, "2026-10-11")
        self.assertFalse(resolved["execution_reuse"])
        self.assertTrue(resolved["candidate_continuity_compatible"])
        self.assertTrue(resolved["requires_fresh_evaluation"])

    def test_bad_audit_version_status_strategy_date_rejected(self):
        audit = self.report("execution_audit", revision=3)
        original = (self.root / audit).read_text()
        substitutions = [('"v3.0"', '"v2.28"'), ('"incomplete"', '"accepted"'),
                         ('"trend"', '"A"'), ('"2026-10-09"', '"2026-10-12"'),
                         ('"audit_schema_version": 3', '"audit_schema_version": 2')]
        for old, new in substitutions:
            self.write(audit, original.replace(old, new))
            with self.subTest(new=new), self.assertRaises(ValueError):
                self.register(artifacts={"execution_audit": audit})
        self.assertFalse(self.manifest().exists())

    def test_future_candidate_signal_rejected(self):
        audit = self.report("execution_audit")
        path = self.root / audit
        path.write_text(path.read_text().replace('"signal_date": "2026-10-09"', '"signal_date": "2026-10-12"'))
        with self.assertRaisesRegex(ValueError, "signal"):
            self.register(artifacts={"execution_audit": audit})

    def test_published_requires_manifest_and_sources_in_head(self):
        self.init_git()
        self.register()
        with self.assertRaisesRegex(ValueError, "HEAD"):
            handoff.resolve(self.root, "2026-10-11", scope="published")
        self.commit()
        resolved = handoff.resolve(self.root, "2026-10-11", scope="published")
        self.assertEqual(resolved["stored_scope"], "local")
        self.assertEqual(resolved["consumption_scope"], "published")
        self.assertTrue(resolved["publication_verified"])
        self.mutate_manifest(lambda data: data["method"].update(revision="modified working tree"))
        self.git("add", "research")
        with self.assertRaisesRegex(ValueError, "HEAD"):
            handoff.resolve(self.root, "2026-10-11", scope="published")

    def test_published_does_not_skip_newer_local_adoption(self):
        self.init_git()
        self.register("2026-10-10")
        self.commit()
        self.register()
        with self.assertRaisesRegex(ValueError, "HEAD"):
            handoff.resolve(self.root, "2026-10-11", scope="published")

    def test_published_rejects_uncommitted_state_only_change(self):
        self.init_git()
        self.register()
        self.commit()
        self.canonical.write_text(self.canonical.read_text().replace("state A", "state B"))
        self.assertTrue(handoff.resolve(self.root, "2026-10-11")["method_compatible"])
        with self.assertRaisesRegex(ValueError, "HEAD"):
            handoff.resolve(self.root, "2026-10-11", scope="published")

    def test_published_registration_is_not_consumable_until_manifest_commit(self):
        self.init_git()
        report = self.report()
        self.commit()
        result = self.register(scope="published", artifacts={"market_research": report})
        self.assertFalse(result["published_consumable"])
        with self.assertRaisesRegex(ValueError, "HEAD"):
            handoff.resolve(self.root, "2026-10-11", scope="published")
        self.commit()
        self.assertTrue(handoff.resolve(self.root, "2026-10-11", scope="published")["publication_verified"])

    def test_published_checks_superseded_files_and_archive_in_head(self):
        self.init_git()
        first = self.register()
        self.commit()
        original = first["handoff"]["artifacts"]["market_research"]["path"]
        self.register(artifacts={"market_research": self.report(revision=2)}, replace=True,
                      correction_scope=["date"], supersedes=[original])
        self.commit()
        self.assertTrue(handoff.resolve(self.root, "2026-10-11", scope="published")["publication_verified"])
        self.git("rm", "--cached", original)
        self.git("commit", "--quiet", "-m", "remove historical source")
        with self.assertRaisesRegex(ValueError, "HEAD"):
            handoff.resolve(self.root, "2026-10-11", scope="published")

    def test_changed_source_during_registration_fails_before_formal_write(self):
        report = self.report()
        original_ref = handoff._ref

        def changing_ref(root, relative):
            result = original_ref(root, relative)
            self.write(relative, "changed concurrently")
            return result

        with patch.object(handoff, "_ref", side_effect=changing_ref):
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.register(artifacts={"market_research": report})
        self.assertFalse(self.manifest().exists())

    def legacy(self):
        self.register(artifacts={"market_research": self.report(), "execution_audit": self.report("execution_audit")})
        data = json.loads(self.manifest().read_text())
        data["schema"] = handoff.LEGACY_SCHEMA
        data.pop("legacy_migration")
        data["method"] = {key: value for key, value in data["method"].items()
                          if key in {"path", "version", "revision", "sha256", "canonical_full_sha256"}}
        data["method"]["sha256"] = handoff._legacy_fingerprint(self.canonical.read_bytes())
        self.manifest().write_text(json.dumps(data))
        baseline = self.root / "output/baseline"
        for relative in (handoff.CANONICAL, *handoff.SOURCE_DEPENDENCIES):
            path = baseline / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((self.root / relative).read_bytes())
        return baseline

    def test_heading_workflow_maintenance_and_tools_edits_remain_compatible(self):
        self.canonical.write_text(self.canonical.read_text().replace(
            '<a id="r-v3-workflow"></a>', '<a id="r-v3-workflow"></a>\n'
            + handoff.MAINTENANCE_START + '\n维护分为状态刷新、证据纠错、方法变更，可同时发生。全市场主要矛盾只作背景，不形成共同方向许可。\n' + handoff.MAINTENANCE_END))
        self.register()
        original = self.canonical.read_text()
        self.canonical.write_text(original.replace("Display heading", "Display heading（维护）").replace("维护分为状态刷新、证据纠错、方法变更，可同时发生。", "维护分为状态刷新、证据纠错、方法变更，分别完成。").replace(
            '<a id="r-v3-tools"></a>\n## Display heading（维护）\nRules: 20/10; 2ATR; 0.5ATR; 3.5%.',
            '<a id="r-v3-tools"></a>\nTool workflow clarification'))
        self.assertTrue(handoff.resolve(self.root, "2026-10-11")["method_compatible"])
        self.canonical.write_text(self.canonical.read_text().replace("不形成共同方向许可", "形成共同方向许可"))
        with self.assertRaisesRegex(ValueError, "incompatible"):
            handoff.resolve(self.root, "2026-10-11")

    def test_actual_prose_rule_scope_and_gate_changes_are_incompatible(self):
        self.register()
        original = self.canonical.read_text()
        for anchor in ("scope", "pool", "workflow", "data", "calendar", "economics", "quality", "status"):
            with self.subTest(anchor=anchor):
                self.canonical.write_text(original.replace(f'<a id="r-v3-{anchor}"></a>',
                    f'<a id="r-v3-{anchor}"></a>\nNow allow a previously forbidden behavior.'))
                with self.assertRaisesRegex(ValueError, "incompatible"):
                    handoff.resolve(self.root, "2026-10-11")
        self.canonical.write_text(original)

    def test_semantic_helper_edit_rejected_but_comments_docstrings_and_collector_provenance_are_not_rules(self):
        self.register()
        original = handoff.method_fingerprint(self.root)
        for path in handoff.METHOD_DEPENDENCIES:
            self.write(path, '# comment\n"""Different docstring."""\nVALUE=2\n')
        self.write("scripts/future_data.py", '"""Logging-only collector revision."""\nVALUE=2\n')
        changed = handoff.method_fingerprint(self.root)
        self.assertNotEqual(original["source_dependencies"], changed["source_dependencies"])
        self.assertTrue(handoff.resolve(self.root, "2026-10-11")["method_compatible"])
        self.write(handoff.METHOD_DEPENDENCIES[0], "VALUE=3\n")
        with self.assertRaisesRegex(ValueError, "incompatible"):
            handoff.resolve(self.root, "2026-10-11")

    def test_legacy_requires_explicit_migration_and_keeps_original_evidence(self):
        baseline = self.legacy()
        old = self.manifest().read_bytes()
        with self.assertRaisesRegex(ValueError, "Legacy v1"):
            handoff.resolve(self.root, "2026-10-11")
        historical = handoff.resolve(self.root, "2026-10-11", allow_historical=True)
        self.assertFalse(historical["candidate_continuity_compatible"])
        result = handoff.migrate(self.root, handoff.manifest_relative("2026-10-11"), baseline_root=baseline,
                                 baseline_provenance="Frozen original fixture sources reviewed", method_revision="reviewed migration")
        loaded = handoff.resolve(self.root, "2026-10-11")
        self.assertTrue(loaded["candidate_continuity_compatible"])
        self.assertFalse(loaded["execution_reuse"])
        prior = result["handoff"]["previous_handoff"]
        self.assertEqual((self.root / prior["path"]).read_bytes(), old)
        self.assertEqual(result["handoff"]["artifacts"], historical["handoff"]["artifacts"])

    def test_migration_allows_legacy_maintenance_markers_without_dropping_direction_rule(self):
        # The original explicit maintenance paragraph predates the markers.
        old_text = self.canonical.read_text().replace('<a id="r-v3-workflow"></a>',
            '<a id="r-v3-workflow"></a>\n维护分为状态刷新、证据纠错、方法变更，可同时发生。全市场主要矛盾只作背景，不形成共同方向许可。\n')
        self.canonical.write_text(old_text)
        baseline = self.legacy()
        self.canonical.write_text(old_text.replace(
            '维护分为状态刷新、证据纠错、方法变更，可同时发生。全市场主要矛盾只作背景，不形成共同方向许可。',
            handoff.MAINTENANCE_START + '\n维护分为状态刷新、证据纠错、方法变更，分别完成。全市场主要矛盾只作背景，不形成共同方向许可。\n' + handoff.MAINTENANCE_END))
        handoff.migrate(self.root, handoff.manifest_relative("2026-10-11"), baseline_root=baseline,
                        baseline_provenance="reviewed old sources", method_revision="identity migration")
        self.assertTrue(handoff.resolve(self.root, "2026-10-11")["method_compatible"])

    def test_legacy_migration_cannot_approve_changed_rules_or_helper(self):
        baseline = self.legacy()
        original = self.canonical.read_text()
        self.canonical.write_text(original.replace("2ATR", "3ATR"))
        with self.assertRaisesRegex(ValueError, "changed effective"):
            handoff.migrate(self.root, handoff.manifest_relative("2026-10-11"), baseline_root=baseline,
                            baseline_provenance="originals", method_revision="attempt")
        self.canonical.write_text(original)
        self.write(handoff.METHOD_DEPENDENCIES[0], "VALUE=3\n")
        with self.assertRaisesRegex(ValueError, "changed effective"):
            handoff.migrate(self.root, handoff.manifest_relative("2026-10-11"), baseline_root=baseline,
                            baseline_provenance="originals", method_revision="attempt")

    def test_bad_legacy_canonical_or_missing_provenance_rejected(self):
        baseline = self.legacy()
        with self.assertRaisesRegex(ValueError, "provenance"):
            handoff.migrate(self.root, handoff.manifest_relative("2026-10-11"), baseline_root=baseline,
                            baseline_provenance="", method_revision="attempt")
        (baseline / handoff.CANONICAL).write_text(self.canonical.read_text() + "changed")
        with self.assertRaisesRegex(ValueError, "source hashes"):
            handoff.migrate(self.root, handoff.manifest_relative("2026-10-11"), baseline_root=baseline,
                            baseline_provenance="originals", method_revision="attempt")

    def test_corrupted_frozen_migration_helper_is_not_silently_accepted(self):
        baseline = self.legacy()
        result = handoff.migrate(self.root, handoff.manifest_relative("2026-10-11"), baseline_root=baseline,
                                 baseline_provenance="originals", method_revision="identity migration")
        ref = result["handoff"]["legacy_migration"]["baseline_sources"][handoff.METHOD_DEPENDENCIES[0]]
        self.write(ref["path"], "VALUE=3\n")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            handoff.resolve(self.root, "2026-10-11")

    def test_typed_market_and_execution_resolve_different_adoptions(self):
        market = self.report(day="2026-10-09")
        self.register("2026-10-09", artifacts={"market_research": market})
        audit = self.report("execution_audit", day="2026-10-10")
        self.register("2026-10-10", artifacts={"execution_audit": audit})
        market_result = handoff.resolve(self.root, "2026-10-11", before=True, kind="market-research")
        audit_result = handoff.resolve(self.root, "2026-10-11", kind="execution_audit")
        self.assertEqual(market_result["artifact"]["path"], market)
        self.assertEqual(audit_result["artifact"]["path"], audit)
        self.assertEqual(handoff.resolve(self.root, "2026-10-11", kind="change-decision")["status"], "missing")

    def test_typed_same_kind_corruption_never_falls_back(self):
        self.register("2026-10-09")
        recent = self.register("2026-10-10")
        self.write(recent["handoff"]["artifacts"]["market_research"]["path"], "corrupt")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            handoff.resolve(self.root, "2026-10-11", kind="market-research")

    def test_typed_query_does_not_hide_malformed_unrelated_record(self):
        self.register("2026-10-09")
        self.register("2026-10-10", artifacts={"execution_audit": self.report("execution_audit", day="2026-10-10")})
        self.mutate_manifest(lambda data: data.update(status="draft"), day="2026-10-10")
        with self.assertRaises(ValueError):
            handoff.resolve(self.root, "2026-10-11", kind="market-research")

    def test_typed_published_market_not_hidden_by_unpublished_audit_only(self):
        self.init_git()
        market = self.register("2026-10-09")
        self.commit()
        self.register("2026-10-10", artifacts={"execution_audit": self.report("execution_audit", day="2026-10-10")})
        result = handoff.resolve(self.root, "2026-10-11", kind="market-research", scope="published")
        self.assertEqual(result["artifact"], market["handoff"]["artifacts"]["market_research"])


    def test_published_heading_change_after_commit_keeps_plan_compatibility(self):
        self.init_git()
        self.register(artifacts={"execution_audit": self.report("execution_audit")})
        self.commit()
        self.canonical.write_text(self.canonical.read_text().replace("Display heading", "New title"))
        self.commit()
        result = handoff.resolve(self.root, "2026-10-11", scope="published")
        self.assertTrue(result["candidate_continuity_compatible"])
        self.assertNotEqual(result["handoff"]["method"]["canonical_full_sha256"], handoff.method_fingerprint(self.root)["canonical_full_sha256"])

    def test_markers_cannot_hide_workflow_gate_or_effective_section(self):
        original = self.canonical.read_text()
        baseline = handoff.method_fingerprint(self.root)
        self.canonical.write_text(original.replace('<a id="r-v3-workflow"></a>',
            f'<a id="r-v3-workflow"></a>\n{handoff.MAINTENANCE_START}\nG4 execution checks\n{handoff.MAINTENANCE_END}'))
        self.assertNotEqual(handoff.method_fingerprint(self.root)["sha256"], baseline["sha256"])
        self.canonical.write_text(original.replace('<a id="r-v3-signal-t"></a>',
            f'<a id="r-v3-signal-t"></a>\n{handoff.MAINTENANCE_START}\nlower threshold\n{handoff.MAINTENANCE_END}'))
        with self.assertRaises(ValueError):
            handoff.method_fingerprint(self.root)

    def test_unknown_gate_inside_maintenance_block_is_effective_not_keyword_filtered(self):
        self.canonical.write_text(self.canonical.read_text().replace('<a id="r-v3-workflow"></a>',
            '<a id="r-v3-workflow"></a>\n' + handoff.MAINTENANCE_START + '\n'
            + handoff.REVIEWED_MAINTENANCE_SENTENCES[0] + '\n' + handoff.MAINTENANCE_END))
        self.register(artifacts={"execution_audit": self.report("execution_audit")})
        original = self.canonical.read_text()
        for new_rule in (
            "T 必须等待框架生效后的再次突破才可研究，历史信号不得接续。",
            "V 只允许做多。",
            "风险金额上限改为原来的两倍。",
            "New wording without any previously blacklisted token.",
        ):
            with self.subTest(new_rule=new_rule):
                self.canonical.write_text(original.replace(handoff.MAINTENANCE_END, new_rule + '\n' + handoff.MAINTENANCE_END))
                with self.assertRaisesRegex(ValueError, "incompatible"):
                    handoff.resolve(self.root, "2026-10-11")
        self.canonical.write_text(original)

    def test_reviewed_maintenance_presentation_and_link_changes_stay_compatible(self):
        approved = handoff.REVIEWED_MAINTENANCE_SENTENCES[-1]
        self.canonical.write_text(self.canonical.read_text().replace('<a id="r-v3-workflow"></a>',
            '<a id="r-v3-workflow"></a>\n' + handoff.MAINTENANCE_START + '\n'
            + approved.replace("维护入口", "[维护入口](old-link.md)") + '\n' + handoff.MAINTENANCE_END))
        self.register()
        self.canonical.write_text(self.canonical.read_text().replace(
            "采纳版本、取数、刷新与发布按[维护入口](old-link.md)执行，本文只在末节保留有日期的当期摘要与引用。",
            "### 维护入口（说明）\n- **采纳版本、取数、刷新与发布**按[维护入口](new-link.md)执行，\n本文只在末节保留有日期的当期摘要与引用。"))
        self.assertTrue(handoff.resolve(self.root, "2026-10-11")["method_compatible"])

    def test_register_cannot_bypass_legacy_migration_by_readopting_identical_old_audit(self):
        self.legacy()
        with self.assertRaisesRegex(ValueError, "Cannot re-adopt"):
            self.register(replace=True, artifacts={"execution_audit": self.report("execution_audit")})

    def test_cli_typed_resolve_returns_requested_source(self):
        report = self.report(day="2026-10-09")
        self.register("2026-10-09", artifacts={"market_research": report})
        self.register("2026-10-10", artifacts={"execution_audit": self.report("execution_audit", day="2026-10-10")})
        output = io.StringIO()
        with redirect_stdout(output):
            code = handoff.main(["--root", str(self.root), "resolve", "--as-of", "2026-10-11", "--before", "--kind", "market-research"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["artifact"]["path"], report)


    def test_cli_missing_and_error_are_distinct(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = handoff.main(["--root", str(self.root), "resolve", "--as-of", "2026-10-11"])
        self.assertEqual(result, 2)
        self.assertTrue(json.loads(output.getvalue())["legacy_fallback_allowed"])
        self.register()
        self.manifest().write_text("invalid")
        output = io.StringIO()
        with redirect_stdout(output):
            result = handoff.main(["--root", str(self.root), "resolve", "--as-of", "2026-10-11"])
        self.assertEqual(result, 1)
        self.assertFalse(json.loads(output.getvalue())["legacy_fallback_allowed"])


if __name__ == "__main__":
    unittest.main()
