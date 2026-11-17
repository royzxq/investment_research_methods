from pathlib import Path
from datetime import date, timedelta
import json
import re
import shutil
import tempfile
import unittest

from scripts.investment_framework_governance import check, FILES, ROOT, STRATEGY_SCOPE
from scripts.stock_framework_bundle import BUNDLE, sync


class InvestmentGovernanceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "framework").mkdir()
        for name in BUNDLE:
            shutil.copyfile(ROOT / "framework" / name, self.root / "framework" / name)

    def replace(self, name, old, new):
        path = self.root / "framework" / name
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def test_current_pair_has_complete_structure(self):
        self.assertEqual(check(self.root)["status"], "passed")

    def test_missing_and_duplicate_rule_definition_are_rejected(self):
        self.replace(FILES[1], "- **R21 ", "- **R20 ")
        with self.assertRaisesRegex(ValueError, "definitions"):
            check(self.root)

    def test_undefined_reference_is_rejected(self):
        path = self.root / "framework" / FILES[1]
        path.write_text(path.read_text() + "\n[R99]\n")
        with self.assertRaisesRegex(ValueError, "Undefined"):
            check(self.root)

    def test_new_rule_cannot_be_missing_duplicated_or_renumbered(self):
        path = self.root / "framework" / FILES[1]
        original = path.read_text()
        for replacement in ("- **ETF ", "- **R21 ", "- **R23 "):
            with self.subTest(replacement=replacement):
                path.write_text(original.replace("- **R22 ", replacement, 1))
                with self.assertRaisesRegex(ValueError, "definitions"):
                    check(self.root)
        path.write_text(original + "\n- **R22 duplicate**\n")
        with self.assertRaisesRegex(ValueError, "definitions"):
            check(self.root)

    def test_only_one_copy_refreshing_state_is_rejected(self):
        text = (self.root / "framework" / FILES[0]).read_text()
        block = re.search(r"<!-- investment-state:start -->\s*```json\s*(.*?)\s*```", text, re.S)
        old_day = json.loads(block[1])["as_of"]
        new_day = (date.fromisoformat(old_day) + timedelta(days=1)).isoformat()
        self.replace(FILES[0], f'"as_of": "{old_day}"', f'"as_of": "{new_day}"')
        with self.assertRaisesRegex(ValueError, "observation snapshots differ"):
            check(self.root)

    def test_state_block_cannot_hide_a_rule_field(self):
        self.replace(FILES[0], '"schema": "investment-state/v1"',
                     '"schema": "investment-state/v1", "threshold": 123')
        with self.assertRaises(ValueError):
            check(self.root)

    def test_migrated_rule_cannot_be_reactivated_by_a_compact_reference(self):
        path = self.root / "framework" / FILES[1]
        path.write_text(path.read_text() + "\n稳态现金流依赖[R9]放行。\n")
        with self.assertRaisesRegex(ValueError, "active compact reference"):
            check(self.root)

    def test_scope_and_migration_destination_cannot_silently_disappear(self):
        self.replace(FILES[0], STRATEGY_SCOPE, "")
        with self.assertRaisesRegex(ValueError, "Strategy scope"):
            check(self.root)

    def test_missing_migrated_model_is_rejected_even_after_hash_sync(self):
        self.replace("dividend_framework.md", "### HD4A ", "### Archived model ")
        sync(self.root)
        with self.assertRaisesRegex(ValueError, "HD4A"):
            check(self.root)

    def test_legacy_six_file_bundle_keeps_its_original_scope(self):
        # snapshot/v2 already existed before R9's full migration.
        frozen = ROOT / "research/investment/weekly/2026-11-17/evidence/investment-2026-11-17-handoff-methods"
        for name in BUNDLE:
            shutil.copyfile(frozen / name, self.root / "framework" / name)
        self.assertEqual(check(self.root)["strategy_scope"], "legacy")


if __name__ == "__main__":
    unittest.main()
