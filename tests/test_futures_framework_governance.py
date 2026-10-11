"""Read-only structural regressions use temporary framework trees."""

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.futures_framework_governance import (
    CANONICAL, COMPACT, EXPECTED_COMPACT_ANCHORS, FRAMEWORK_FILES, LEGACY_COMPACT_ANCHORS, MIGRATION,
    anchors_in, check, inspect,
)


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        anchors = '\n'.join(f'<a id="{anchor}"></a>\nRule content.\n'
                            for anchor in sorted(EXPECTED_COMPACT_ANCHORS))
        self.write(CANONICAL, '# 完整框架 v3.0\n\n[摘要规则](futures_framework_compact.md#r-v3-budget)\n' + anchors)
        self.write(COMPACT, '# 精简版 v3.0\n\n[完整版](futures_framework.md#r-v3-scope)\n\n' + anchors)
        self.write(FRAMEWORK_FILES[2], '# 数据协议\n')
        self.write(MIGRATION, (ROOT / MIGRATION).read_text(encoding='utf-8'))

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')

    def assert_error(self, fragment):
        errors = check(self.root)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def command(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts/futures_framework_governance.py'),
             '--root', str(self.root), *args], capture_output=True, text=True)

    def test_v3_rules_have_30_ids_with_explicit_277_id_migration(self):
        self.assertEqual(len(EXPECTED_COMPACT_ANCHORS), 30)
        self.assertEqual(len(LEGACY_COMPACT_ANCHORS), 277)
        self.assertEqual(check(self.root), [])

    def test_same_anchor_count_does_not_hide_a_renamed_rule(self):
        source = (self.root / COMPACT).read_text(encoding='utf-8')
        self.write(COMPACT, source.replace('id="r-v3-budget"', 'id="r-renamed-cost"'))
        self.assert_error('missing stable rule anchors: r-v3-budget')

    def test_duplicate_anchor_is_rejected(self):
        source = (self.root / COMPACT).read_text(encoding='utf-8')
        self.write(COMPACT, source + '\n<a id="r-v3-budget"></a>\n')
        self.assert_error('duplicate anchor IDs: r-v3-budget')

    def test_compact_can_have_independent_wording_and_files_have_no_size_ceiling(self):
        source = (self.root / COMPACT).read_text(encoding='utf-8')
        self.write(COMPACT, source + '\n独立维护的精简表述。\n')
        source = (self.root / CANONICAL).read_text(encoding='utf-8')
        self.write(CANONICAL, source + '完整方法说明。\n' * 2500)
        self.assertEqual(check(self.root), [])

    def test_size_report_counts_utf8_bytes_and_lines(self):
        path = FRAMEWORK_FILES[2]
        self.write(path, '汉字\n')
        reports, errors = inspect(self.root)
        self.assertEqual(errors, [])
        report = next(row for row in reports if row['path'] == str(path))
        self.assertEqual(report['bytes'], 7)
        self.assertEqual(report['lines'], 1)

    def test_cli_check_is_read_only_and_does_not_claim_semantic_verification(self):
        before = {path: ((self.root / path).read_bytes(), (self.root / path).stat().st_mtime_ns)
                  for path in FRAMEWORK_FILES}
        result = self.command('--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('semantic equivalence and investment validity are not verified', result.stdout)
        self.assertIn('30 explicit anchors', result.stdout)
        self.assertEqual(before, {path: ((self.root / path).read_bytes(),
                                       (self.root / path).stat().st_mtime_ns)
                                  for path in FRAMEWORK_FILES})

    def test_unsupported_write_option_is_rejected_without_writing(self):
        before = (self.root / COMPACT).read_bytes()
        result = self.command('--write-compact', '--check')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unrecognized arguments: --write-compact', result.stderr)
        self.assertEqual((self.root / COMPACT).read_bytes(), before)

    def test_plain_report_is_available_without_check(self):
        result = self.command()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('UTF-8 bytes', result.stdout)
        self.assertNotIn('checks passed', result.stdout)

    def test_inline_file_and_anchor_links_are_checked_in_all_three_files(self):
        for path in FRAMEWORK_FILES:
            with self.subTest(path=path):
                source = (self.root / path).read_text(encoding='utf-8')
                self.write(path, source + '\n[missing](missing.md)\n[anchor](#missing-rule)\n')
                self.assert_error(f"{path}: missing local link target 'missing.md'")
                self.assert_error(f"{path}: missing local anchor '#missing-rule'")
                self.write(path, source)
        self.assertEqual(check(self.root), [])

    def test_urls_fences_encoded_paths_titles_and_heading_anchors(self):
        self.write(Path('framework/with space.md'), '# A Heading\n\n## 重复标题\n\n## 重复标题\n')
        source = (self.root / CANONICAL).read_text(encoding='utf-8')
        self.write(CANONICAL, source + '\n'.join([
            '[file](with%20space.md#a-heading)',
            '[file title](<with space.md> "title")',
            '[duplicate heading](with%20space.md#重复标题-1)',
            '[external](https://example.invalid/missing.md#anything)',
            '```md', '[example](missing-example.md#missing)', '<a id="example"></a>', '```',
        ]))
        self.assertEqual(check(self.root), [])
        explicit, _ = anchors_in((self.root / CANONICAL).read_text(encoding='utf-8'))
        self.assertNotIn('example', explicit)

    def test_historical_notes_fail_but_active_rule_version_values_remain_valid(self):
        source = (self.root / CANONICAL).read_text(encoding='utf-8')
        for note in ('【本次更新】', '【本次更新 v2.27】', '【本次更新 v2.27:修订】', '【v2.26】'):
            with self.subTest(note=note):
                self.write(CANONICAL, source + f'\n{note}\n')
                self.assert_error('remove inline historical update notes')
        self.write(CANONICAL, source + '\nrule_version=B-v2.24；方法版本 v2.27。\n')
        self.assertEqual(check(self.root), [])

    def test_missing_file_and_invalid_utf8_fail_cli(self):
        (self.root / FRAMEWORK_FILES[2]).unlink()
        self.assert_error('FUTURES_DATA_PROTOCOL.md: cannot read UTF-8 file')
        (self.root / CANONICAL).write_bytes(b'\xff')
        result = self.command('--check')
        self.assertEqual(result.returncode, 1)
        self.assertIn('futures_framework.md: cannot read UTF-8 file', result.stderr)

    def test_v3_canonical_and_compact_versions_must_match(self):
        source = (self.root / CANONICAL).read_text(encoding='utf-8')
        self.write(CANONICAL, source.replace('v3.0', 'v3.1'))
        self.assert_error('canonical and compact versions must match')

    def test_v3_checks_canonical_rule_ids_too(self):
        source = (self.root / CANONICAL).read_text(encoding='utf-8')
        self.write(CANONICAL, source.replace('id="r-v3-stop"', 'id="omitted-stop"'))
        self.assert_error('futures_framework.md: missing stable rule anchors: r-v3-stop')

    def test_migration_cannot_omit_or_invent_old_rules(self):
        migration = json.loads((self.root / MIGRATION).read_text(encoding='utf-8'))
        migration['rules']['invented-old-rule'] = migration['rules'].pop('r-gate-31')
        self.write(MIGRATION, json.dumps(migration))
        self.assert_error('missing historical rule dispositions: r-gate-31')
        self.assert_error('unknown historical rule IDs: invented-old-rule')

    def test_migration_requires_reason_and_current_target_or_explicit_retirement(self):
        migration = json.loads((self.root / MIGRATION).read_text(encoding='utf-8'))
        migration['rules']['r-gate-31'] = dict(disposition='mapped', target='r-gate-31', reason='')
        self.write(MIGRATION, json.dumps(migration))
        self.assert_error('target must be a current v3 rule ID')
        self.assert_error('migration reason is required')
        migration['rules']['r-gate-31'] = dict(disposition='retired', target=None, reason='Historical-only rule.')
        self.write(MIGRATION, json.dumps(migration))
        self.assertEqual(check(self.root), [])

    def test_historical_v2_frameworks_keep_original_anchor_contract(self):
        self.write(CANONICAL, '# 完整框架 v2.29\n')
        self.write(COMPACT, '# 精简版 v2.29\n' + '\n'.join(f'<a id="{a}"></a>' for a in LEGACY_COMPACT_ANCHORS))
        (self.root / MIGRATION).unlink()
        self.assertEqual(check(self.root), [])


if __name__ == '__main__':
    unittest.main()
