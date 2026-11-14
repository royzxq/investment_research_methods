"""Include deterministic JS retrieval checks in the standard offline regression."""
from pathlib import Path
import shutil
import subprocess
import unittest


class DataHealthTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is required for the DSH plugin checks')
    def test_retrieval_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(['node', '--test', 'tests/test_research_data_health.mjs',
                                 'tests/test_research_evidence_recovery.mjs',
                                 'tests/test_research_evidence_context.mjs'],
                                cwd=root, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
