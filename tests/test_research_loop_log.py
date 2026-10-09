import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.research_loop_log import record
from scripts.research_scheduler import journal


class ResearchLoopLogTests(unittest.TestCase):
    def test_scheduler_journal_uses_local_writer_and_preserves_event_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'logs/events.jsonl'
            with patch('scripts.research_loop_log.os.fsync', wraps=os.fsync) as sync:
                journal(path, 'provider_finished', run_id='research-test',
                        details={'attempt': 2, 'actual_model': None})
            sync.assert_called_once()
            row = json.loads(path.read_text())
            self.assertEqual(row['schema_version'], 'research-loop-event/v1')
            self.assertEqual(row['repository'], 'investment_research_methods')
            self.assertEqual(row['stage'], 'research')
            self.assertEqual(row['event'], 'provider_finished')
            self.assertEqual(row['run_id'], 'research-test')
            self.assertEqual(row['details'], {'attempt': 2, 'actual_model': None})
            self.assertEqual(datetime.fromisoformat(row['ts']).utcoffset(), timedelta(hours=8))
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_nested_credentials_are_redacted_in_shared_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'events.jsonl'
            journal(path, 'failed', details={
                'api_key': 'private-key',
                'nested': [{'authorization': 'private-header',
                            'reason': 'Bearer private-value; password=private-password'}],
                'attempt': 1,
            })
            raw = path.read_text()
            self.assertNotIn('private-', raw)
            details = json.loads(raw)['details']
            self.assertEqual(details['api_key'], '[redacted]')
            self.assertEqual(details['nested'][0]['authorization'], '[redacted]')
            self.assertEqual(details['attempt'], 1)

    def test_multiple_processes_append_complete_json_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'events.jsonl'
            code = (
                'from scripts.research_loop_log import record; import sys; '
                '[record(sys.argv[1], repository=sys.argv[2], stage="research", '
                'event="provider_finished", index=i, details={"summary": "测试" * 5000}) '
                'for i in range(12)]'
            )
            processes = [subprocess.Popen([sys.executable, '-c', code, str(path), repository],
                                          cwd=Path(__file__).resolve().parents[1],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                         for repository in ('investment_research_methods', 'ai_investment')]
            try:
                for process in processes:
                    _, error = process.communicate(timeout=15)
                    self.assertEqual(process.returncode, 0, error.decode())
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.kill()
                    process.communicate()
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 24)
            self.assertEqual({(row['repository'], row['index']) for row in rows},
                             {(repo, i) for repo in ('investment_research_methods', 'ai_investment')
                              for i in range(12)})
            self.assertTrue(all(row['details']['summary'] == '测试' * 5000 for row in rows))

    def test_journal_io_errors_are_visible_and_none_is_disabled(self):
        with patch('scripts.research_scheduler.record', side_effect=OSError('journal unavailable')):
            journal(None, 'check_started')
            with self.assertRaisesRegex(OSError, 'journal unavailable'):
                journal(Path('unused.jsonl'), 'check_started')
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(OSError):
                record(Path(temp), repository='investment_research_methods',
                       stage='research', event='check_started')

    def test_invalid_numeric_metadata_does_not_append_a_partial_event(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'events.jsonl'
            with self.assertRaises(ValueError):
                journal(path, 'provider_finished', details={'duration': float('nan')})
            self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
