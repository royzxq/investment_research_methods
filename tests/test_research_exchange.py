"""Offline acceptance of batch requests and exact research artifact pairs."""

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.research_exchange import load_request, load_results


class ResearchExchangeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.request_root = self.root / "exchange"
        self.request_root.mkdir()
        self.artifact_root = self.root / "methods"
        self.artifact_root.mkdir()
        self.request_path = self.request_root / "request.json"
        self.result_path = self.root / "result.json"
        self.pack = self.request_root / "packs/SH-600066.md"
        self.pack.parent.mkdir()
        self.pack.write_text("量价数据包\n", encoding="utf-8")
        self.request = {
            "schema_version": "stock-research-request/v1", "batch_id": "1" * 32,
            "created_at": "2026-10-06T08:00:00+08:00", "valuation_date": "2026-10-06",
            "generators": ["codex", "claude"], "tasks": [{
                "task_id": "SH-600066", "code": "600066.SH", "name": "宇通客车",
                "sources": ["candidate_review"],
                "data_pack": {"path": "packs/SH-600066.md", "sha256": self.sha(self.pack)},
                "data_pack_meta": {"missing": ["shares"], "close": 25.3},
            }],
        }
        self.write_request()
        self.report_relative = (
            "research/investment/companies/2026-10-06/SH-600066/"
            "investment-600066-2026-10-06-research-codex-r2.md"
        )
        self.price_relative = self.report_relative.replace("research-codex", "price-map-codex").replace(".md", ".json")
        self.report_path = self.artifact_root / self.report_relative
        self.report_path.parent.mkdir(parents=True)
        self.report_path.write_text("# 研究报告\n\n" + "\n\n".join(
            f"## {i}. 研究章节\n\n本节的离线验收内容。" for i in range(9)
        ), encoding="utf-8")
        self.price_path = self.artifact_root / self.price_relative
        self.document = {
            "meta": {"schema_version": "stock-research/v2", "code": "600066.SH", "name": "宇通客车",
                     "valuation_date": "2026-10-06", "currency": "CNY", "generator": "codex",
                     "report_path": self.report_relative},
            "price_map": {"mode": "tracking", "reason": "离线样例，仅跟踪",
                          "v50": {"low": 20, "base": 25, "high": 30},
                          "p1": {"low": 10, "base": 12, "high": 15},
                          "p2": {"status": "cancelled", "price": None, "reason": "取消加仓"},
                          "t1": {"price_condition": "达到 V50 区间复核", "events": ["利润率下降"]},
                          "t2": {"price_condition": "价格不适用", "events": ["逻辑证伪"]}},
            "monitoring": [{"variable": "收入", "current": None, "as_of": None, "trigger": "同比下降",
                            "action": "重算估值", "source": "离线样例", "next_check": "下次财报"}],
        }
        self.price_path.write_text(json.dumps(self.document, ensure_ascii=False), encoding="utf-8")
        self.result = {
            "schema_version": "stock-research-result/v1", "batch_id": self.request["batch_id"],
            "request_sha256": self.sha(self.request_path), "created_at": "2026-10-06T10:00:00+08:00",
            "results": [{"task_id": "SH-600066", "generator": "codex", "status": "completed", "reason": None,
                         "started_at": "2026-10-06T08:01:00+08:00", "completed_at": "2026-10-06T09:00:00+08:00",
                         "report": {"path": self.report_relative, "sha256": self.sha(self.report_path)},
                         "price_map": {"path": self.price_relative, "sha256": self.sha(self.price_path)}}],
        }
        self.write_result()

    @staticmethod
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_request(self):
        self.request_path.write_text(json.dumps(self.request, ensure_ascii=False), encoding="utf-8")

    def write_result(self):
        self.result_path.write_text(json.dumps(self.result, ensure_ascii=False), encoding="utf-8")

    def rewrite_document(self):
        self.price_path.write_text(json.dumps(self.document, ensure_ascii=False), encoding="utf-8")
        self.result["results"][0]["price_map"]["sha256"] = self.sha(self.price_path)
        self.write_result()

    def check_result(self):
        return load_results(self.result_path, self.request_path, self.artifact_root)

    def test_accepts_data_gaps_partial_sources_and_revision_without_writes(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(load_request(self.request_path), self.request)
        self.assertEqual(self.check_result(), self.result)
        self.assertEqual({p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}, before)

    def test_accepts_empty_result_manifest_and_failed_provider(self):
        self.result["results"] = []
        self.write_result()
        self.assertEqual(self.check_result()["results"], [])
        self.result["results"] = [{"task_id": "SH-600066", "generator": "claude", "status": "failed",
                                  "reason": "账号不可用", "started_at": "2026-10-06T08:01:00+08:00",
                                  "completed_at": "2026-10-06T08:02:00+08:00", "report": None, "price_map": None}]
        self.write_result()
        self.assertEqual(self.check_result()["results"][0]["status"], "failed")

    def test_accepts_hong_kong_and_shenzhen_requests(self):
        for market, code in [("HK", "01952"), ("SZ", "000001")]:
            with self.subTest(market=market):
                task = self.request["tasks"][0]
                task.update(task_id=f"{market}-{code}", code=f"{code}.{market}")
                self.write_request()
                self.assertEqual(load_request(self.request_path)["tasks"][0]["task_id"], f"{market}-{code}")

    def test_request_valuation_cutoff_uses_shanghai_date_not_wall_clock_or_timestamp_zone(self):
        self.request["created_at"] = "2026-10-05T16:01:00Z"
        self.write_request()
        self.assertEqual(load_request(self.request_path)["valuation_date"], "2026-10-06")
        self.request["created_at"] = "2026-10-05T15:59:00Z"
        self.write_request()
        with self.assertRaisesRegex(ValueError, "valuation_date"):
            load_request(self.request_path)

    def test_results_compare_actual_instants_across_timezones(self):
        self.result["created_at"] = "2026-10-06T02:00:00Z"
        entry = self.result["results"][0]
        entry["started_at"] = "2026-10-06T00:01:00Z"
        entry["completed_at"] = "2026-10-06T01:00:00Z"
        self.write_result()
        self.assertEqual(self.check_result(), self.result)
        entry["started_at"] = "2026-10-05T23:59:59Z"
        self.write_result()
        with self.assertRaisesRegex(ValueError, "time order"):
            self.check_result()

    def test_rejects_request_structure_identity_duplicates_and_naive_time(self):
        cases = [
            lambda r: r.update(extra=True), lambda r: r.update(batch_id="G" * 32),
            lambda r: r.update(batch_id="a" * 31), lambda r: r.update(created_at="2026-10-06T08:00:00"),
            lambda r: r.update(valuation_date="2026-02-30"), lambda r: r.update(valuation_date="2026-10-07"),
            lambda r: r.update(generators=[]),
            lambda r: r.update(generators=["codex", "codex"]), lambda r: r.update(generators=["gemini"]),
            lambda r: r.update(tasks=[]), lambda r: r["tasks"].append(deepcopy(r["tasks"][0])),
            lambda r: r["tasks"][0].update(task_id="SZ-600066"),
            lambda r: r["tasks"][0].update(task_id="BJ-830001", code="830001.BJ"),
            lambda r: r["tasks"][0].update(name=" "), lambda r: r["tasks"][0].update(sources=[]),
            lambda r: r["tasks"][0].update(sources=["candidate_review", "candidate_review"]),
            lambda r: r["tasks"][0].update(data_pack_meta=[]),
            lambda r: r["tasks"][0]["data_pack"].update(sha256="not-sha256"),
            lambda r: r["tasks"][0]["data_pack"].update(extra=True),
        ]
        original = deepcopy(self.request)
        for mutate in cases:
            with self.subTest(mutate=mutate):
                self.request = deepcopy(original)
                mutate(self.request)
                self.write_request()
                with self.assertRaises(ValueError):
                    load_request(self.request_path)

    def test_rejects_absolute_parent_missing_empty_and_symlink_pack_paths(self):
        original = deepcopy(self.request)
        outside = self.root / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        (self.request_root / "escape.md").symlink_to(outside)
        for path in [str(outside), "../outside.md", "missing.md", "escape.md"]:
            with self.subTest(path=path):
                self.request = deepcopy(original)
                self.request["tasks"][0]["data_pack"]["path"] = path
                self.write_request()
                with self.assertRaises((ValueError, OSError)):
                    load_request(self.request_path)
        self.request = original
        self.pack.write_bytes(b"")
        self.request["tasks"][0]["data_pack"]["sha256"] = self.sha(self.pack)
        self.write_request()
        with self.assertRaisesRegex(ValueError, "empty"):
            load_request(self.request_path)

    def test_rejects_tampered_data_pack_and_request_bytes(self):
        self.pack.write_text("modified", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sha256"):
            load_request(self.request_path)
        self.request["tasks"][0]["data_pack"]["sha256"] = self.sha(self.pack)
        self.write_request()
        with self.assertRaisesRegex(ValueError, "request_sha256"):
            self.check_result()

    def test_rejects_duplicate_keys_nonfinite_and_overflow_in_metadata(self):
        valid = self.request_path.read_text(encoding="utf-8")
        for changed in [valid.replace('"close": 25.3', '"close": 25.3, "close": 24'),
                        valid.replace('"close": 25.3', '"close": NaN'),
                        valid.replace('"close": 25.3', '"close": Infinity'),
                        valid.replace('"close": 25.3', '"close": 1e9999')]:
            with self.subTest(changed=changed):
                self.request_path.write_text(changed, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_request(self.request_path)

    def test_rejects_result_batch_task_generator_duplicates_and_extra_fields(self):
        cases = [lambda r: r.update(batch_id="2" * 32), lambda r: r.update(extra=1),
                 lambda r: r["results"][0].update(task_id="HK-01952"),
                 lambda r: r["results"][0].update(generator="gemini"),
                 lambda r: r["results"].append(deepcopy(r["results"][0]))]
        original = deepcopy(self.result)
        for mutate in cases:
            with self.subTest(mutate=mutate):
                self.result = deepcopy(original)
                mutate(self.result)
                self.write_result()
                with self.assertRaises(ValueError):
                    self.check_result()

    def test_rejects_invalid_status_reason_artifacts_and_time_order(self):
        cases = [lambda r: r["results"][0].update(status="pending"),
                 lambda r: r["results"][0].update(reason="unexpected"),
                 lambda r: r["results"][0].update(report=None),
                 lambda r: r["results"][0].update(status="failed", reason=" ", report=None, price_map=None),
                 lambda r: r["results"][0].update(status="failed", reason="failed"),
                 lambda r: r["results"][0].update(completed_at="2026-10-06T08:00:01+08:00"),
                 lambda r: r["results"][0].update(started_at="2026-10-06T07:00:00+08:00", completed_at="2026-10-06T07:30:00+08:00"),
                 lambda r: r.update(created_at="2026-10-06T08:30:00+08:00"),
                 lambda r: r["results"][0].update(started_at="2026-10-06T08:01:00")]
        original = deepcopy(self.result)
        for mutate in cases:
            with self.subTest(mutate=mutate):
                self.result = deepcopy(original)
                mutate(self.result)
                self.write_result()
                with self.assertRaises(ValueError):
                    self.check_result()

    def test_rejects_price_metadata_mismatches_and_missing_generator(self):
        original = deepcopy(self.document)
        for field, value in [("code", "600067.SH"), ("name", "另一公司"), ("valuation_date", "2026-10-07"),
                             ("generator", "claude"), ("currency", "HKD"), ("report_path", "output/old.md")]:
            with self.subTest(field=field):
                self.document = deepcopy(original)
                self.document["meta"][field] = value
                self.rewrite_document()
                with self.assertRaises(ValueError):
                    self.check_result()
        self.document = deepcopy(original)
        del self.document["meta"]["generator"]
        self.rewrite_document()
        with self.assertRaises(ValueError):
            self.check_result()

    def test_rejects_mismatched_revision_latest_and_artifact_escape(self):
        for path in [self.report_relative.replace("-r2", "-r3"), "output/indexes/investment/latest.json",
                     "../outside.md", str(self.report_path)]:
            with self.subTest(path=path):
                self.result["results"][0]["report"]["path"] = path
                self.write_result()
                with self.assertRaises((ValueError, OSError)):
                    self.check_result()

    def test_rejects_formal_artifact_symlink_escape_and_unplanned_valid_provider(self):
        outside = self.root / "outside-report.md"
        outside.write_bytes(self.report_path.read_bytes())
        self.report_path.unlink()
        self.report_path.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "escapes root"):
            self.check_result()
        self.request["generators"] = ["claude"]
        self.write_request()
        self.result["request_sha256"] = self.sha(self.request_path)
        self.write_result()
        with self.assertRaisesRegex(ValueError, "not planned"):
            self.check_result()

    def test_rejects_report_hash_missing_sections_and_empty_section_body(self):
        self.report_path.write_text("modified", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sha256"):
            self.check_result()
        for report in ["# Short report\n## 0. Introduction\ntext", "\n".join(f"## {i}. Section" for i in range(9)),
                       "```\n" + "\n".join(f"## {i}. Section\ntext" for i in range(9)) + "\n```"]:
            with self.subTest(report=report):
                self.report_path.write_text(report, encoding="utf-8")
                self.result["results"][0]["report"]["sha256"] = self.sha(self.report_path)
                self.write_result()
                with self.assertRaises(ValueError):
                    self.check_result()

    def test_rejects_sections_hidden_in_html_comments(self):
        sections = "\n\n".join(f"## {i}. Section\nbody" for i in range(9))
        for report in [f"<!--\n{sections}\n-->", f"<!--\n{sections}",
                       "\n".join(f"<!--\n## {i}. Section\nbody\n-->" for i in range(9))]:
            with self.subTest(report=report):
                self.report_path.write_text(report, encoding="utf-8")
                self.result["results"][0]["report"]["sha256"] = self.sha(self.report_path)
                self.write_result()
                with self.assertRaisesRegex(ValueError, "sections 0-8"):
                    self.check_result()

    def test_fence_with_trailing_info_does_not_close_code_block(self):
        sections = "\n\n".join(f"## {i}. Section\nbody" for i in range(9))
        for start, false_close in [("```python", "```still-code"), ("~~~python", "~~~~still-code"),
                                   ("````python", "~~~"), ("````python", "```")]:
            with self.subTest(start=start, false_close=false_close):
                self.report_path.write_text(f"{start}\n{false_close}\n{sections}\n", encoding="utf-8")
                self.result["results"][0]["report"]["sha256"] = self.sha(self.report_path)
                self.write_result()
                with self.assertRaisesRegex(ValueError, "sections 0-8"):
                    self.check_result()

    def test_valid_fence_closing_and_comments_inside_code_leave_real_sections_visible(self):
        sections = "\n\n".join(f"## {i}. Section\nbody <!-- omitted --> still visible" for i in range(9))
        self.report_path.write_text("```python\n<!-- unclosed comment inside code\n```` \t\n" + sections,
                                    encoding="utf-8")
        self.result["results"][0]["report"]["sha256"] = self.sha(self.report_path)
        self.write_result()
        self.assertEqual(self.check_result(), self.result)

    def test_strict_price_json_and_result_manifest_loading(self):
        original = self.price_path.read_text(encoding="utf-8")
        self.price_path.write_text(original.replace('"base": 25', '"base": 25, "base": 26'), encoding="utf-8")
        self.result["results"][0]["price_map"]["sha256"] = self.sha(self.price_path)
        self.write_result()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check_result()
        self.result_path.write_text('{"schema_version":"x","schema_version":"y"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check_result()

    def test_cli_only_returns_counts_and_never_changes_artifacts(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        commands = [["check-request", str(self.request_path)],
                    ["check-results", str(self.result_path), "--request", str(self.request_path),
                     "--artifact-root", str(self.artifact_root)]]
        for args in commands:
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(ROOT / "scripts/research_exchange.py"), *args],
                                        capture_output=True, text=True, env=env)
                self.assertEqual(result.returncode, 0, result.stderr)
                reply = json.loads(result.stdout)
                self.assertEqual(reply["batch_id"], self.request["batch_id"])
                self.assertNotIn("documents", reply)
        self.assertEqual({p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}, before)


if __name__ == "__main__":
    unittest.main()
