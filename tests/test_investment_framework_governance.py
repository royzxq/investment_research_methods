from pathlib import Path
from datetime import date, timedelta
import json
import re
import shutil
import tempfile
import unittest

from scripts.investment_framework_governance import check, FILES, ROOT


class InvestmentGovernanceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "framework").mkdir()
        for name in FILES:
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


if __name__ == "__main__":
    unittest.main()
