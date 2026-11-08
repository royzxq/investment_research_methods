import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts import research_dsh_metrics as metrics


def event(kind, data, **kwargs):
    return dict(type=kind, data=data, **kwargs)


def usage_record(**usage):
    return dict(type='chunk', time=100, chunk=dict(type='usage', usage=usage))


class DSHMetricsTests(unittest.TestCase):
    def test_context_metrics_report_unexercised_and_changed_records_without_source_text(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            self.assertIsNone(metrics.context_metrics(root))
            folder = root/'evidence-context'
            for name in ('sources', 'anchors', 'pins', 'citations', 'events'):
                (folder/name).mkdir(parents=True)
            self.assertEqual(metrics.context_metrics(root)['sources'], 0)
            self.assertIsNone(metrics.context_metrics(root)['final_report_audit'])
            (folder/'sources/invalid.json').write_text(json.dumps({'id': 'bad', 'data': {'excerpt': 'PRIVATE SOURCE'}}))
            value = metrics.context_metrics(root)
            self.assertIn('invalid_or_changed_context_store', value['issues'])
            self.assertNotIn('PRIVATE SOURCE', json.dumps(value))

    def test_recovery_effects_keep_reading_use_claims_and_final_citations_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            self.assertIsNone(metrics.recovery_metrics(root))
            folder = root / 'evidence-recovery' / ('a' * 64); folder.mkdir(parents=True)
            raw = b'{"source":"PRIVATE SOURCE TEXT"}\n'
            (folder / 'page.json').write_bytes(raw)
            state = dict(schema_version='research-evidence-recovery/v1', gap_id=folder.name,
                revision=1, category='pagination', retrieval_status='retrieved', attempts=1,
                deduplicated_requests=2, request={'url': 'SECRET-URL'},
                pages=[{'raw': {'file': 'page.json', 'sha256': hashlib.sha256(raw).hexdigest()}}],
                reads=[{'receipt_id': 'r1'}], reviews=[dict(receipt_id='r1', disposition='used_partial', reason='PRIVATE REASON')])
            (folder / 'event-000001.json').write_text(json.dumps(state))
            value = metrics.recovery_metrics(root)
            self.assertEqual(value['cases'], 1)
            self.assertEqual(value['cases_read'], 1)
            self.assertEqual(value['cases_with_declared_use'], 1)
            self.assertIsNone(value['final_citations_verified'])
            self.assertIsNone(value['facts_independently_verified'])
            self.assertNotIn('PRIVATE', json.dumps(value))
            self.assertNotIn('SECRET-URL', json.dumps(value))
            state['revision'] = 2
            state['reviews'].append(dict(receipt_id='r1', disposition='rejected'))
            (folder / 'event-000002.json').write_text(json.dumps(state))
            self.assertEqual(metrics.recovery_metrics(root)['cases_with_declared_use'], 0)
            (folder / 'page.json').write_text('tampered')
            value = metrics.recovery_metrics(root)
            self.assertEqual(value['cases'], 0)
            self.assertIn('invalid_or_changed_recovery_case', value['issues'])

    def test_recovery_missing_events_unread_cases_and_symlinks_are_not_silent_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            folder = root / 'evidence-recovery' / ('b' * 64); folder.mkdir(parents=True)
            self.assertIn('invalid_or_changed_recovery_case', metrics.recovery_metrics(root)['issues'])
            state = dict(schema_version='research-evidence-recovery/v1', gap_id=folder.name,
                revision=1, category='document', retrieval_status='failed', attempts=1,
                deduplicated_requests=0, pages=[], reads=[], reviews=[])
            (folder / 'event-000001.json').write_text(json.dumps(state))
            value = metrics.recovery_metrics(root)
            self.assertEqual(value['retrieval_statuses'], {'failed': 1})
            self.assertEqual(value['cases_awaiting_assessment'], 1)
            self.assertEqual(value['cases_read'], 0)
            self.assertIn('evidence_recovery', metrics.summarize(root, process={}))
            (root / 'evidence-recovery' / ('c' * 64)).symlink_to(folder, target_is_directory=True)
            self.assertIn('invalid_or_changed_recovery_case', metrics.recovery_metrics(root)['issues'])

    def test_usage_replaces_same_step_and_counts_actual_retry(self):
        rows = [event('assistant/attempt', dict(turn=1, step=1, stream=[usage_record(inputTokens=10, outputTokens=1)])),
                event('assistant/message', dict(turn=1, step=1, usage={'inputTokens': 10, 'outputTokens': 2})),
                event('llm/retry-started', dict(turn=1, step=1)),
                event('assistant/attempt', dict(turn=1, step=1, stream=[usage_record(inputTokens=3)]))]
        result = metrics.session_metrics(rows)
        self.assertEqual(result['usage_samples'], 2)
        self.assertEqual(result['tokens']['inputTokens']['known_sum'], 13)
        self.assertEqual(result['tokens']['outputTokens'], dict(known_sum=2, known_samples=1, missing_samples=1))
        self.assertEqual(result['tokens']['cacheReadTokens']['missing_samples'], 2)

    def test_native_compact_stream_last_usage_and_message_precedence(self):
        stream = [usage_record(inputTokens=10, outputTokens=1),
                  {'type': 'text-chunks', 'texts': ['private text'], 'time0': 1, 'dt': []},
                  usage_record(inputTokens=10, outputTokens=4)]
        result = metrics.session_metrics([
            event('assistant/attempt', dict(turn=1, step=1, stream=stream)),
            event('assistant/message', dict(turn=1, step=2, stream=stream)),
            event('assistant/message', dict(turn=1, step=3, stream=stream, usage={'inputTokens': 20, 'outputTokens': 6}))])
        self.assertEqual(result['usage_samples'], 3)
        self.assertEqual(result['tokens']['inputTokens']['known_sum'], 40)
        self.assertEqual(result['tokens']['outputTokens']['known_sum'], 14)
        self.assertEqual(result['assistant_records_without_usage'], 0)

    def test_compaction_lifecycle_is_one_operation_and_failures_are_separate(self):
        rows = [event('compaction/start', {}), event('compaction/summary', {}),
                event('compaction/end', {}), event('compaction/start', {}),
                event('compaction/end', {'error': 'upstream failed'}), event('compaction/start', {})]
        result = metrics.session_metrics(rows)
        self.assertEqual(result['compactions'], 1)
        self.assertEqual(result['compaction_attempts'], dict(started=3, failed=1, incomplete=1))

    def test_invalid_records_do_not_erase_the_rest_of_the_attempt(self):
        rows = [event([], {}), event('assistant/attempt', {'turn': [], 'step': 1}),
                event('assistant/message', dict(turn=1, step=1, usage={'inputTokens': 2}))]
        result = metrics.session_metrics(rows)
        self.assertEqual(result['invalid_records'], 2)
        self.assertEqual(result['tokens']['inputTokens']['known_sum'], 2)

    def test_wrapper_success_does_not_hide_shell_failure_or_missing_result(self):
        rows = [event('tool/call', dict(callId='a', name='bash'), time=10, seq=1),
                event('tool/result', dict(message={'toolCallId': 'a', 'isError': False}), time=30, seq=2),
                event('job/settled', dict(kind='bash', jobId='b', detail='exit code: 2'), seq=3),
                event('tool/call', dict(callId='c', name='fetch'), time=40, seq=4)]
        result = metrics.session_metrics(rows + [rows[0]])
        self.assertEqual(result['tools']['bash']['errors'], 0)
        self.assertEqual(result['tools']['bash']['duration_ms'], 20)
        self.assertEqual(result['bash_jobs']['nonzero_exit'], 1)
        self.assertEqual(result['tools']['fetch']['missing_results'], 1)
        self.assertEqual(result['duplicate_sequences'], 1)

    def test_missing_logs_stay_unknown_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            other = root / 'outside'; other.mkdir()
            (root / 'dsh-sessions').symlink_to(other, target_is_directory=True)
            result = metrics.summarize(root, process={'status': 'failed', 'attempt': 2})
            self.assertIn('symlink_session_root_rejected', result['issues'])
            self.assertIsNone(result['cost_usd'])
            self.assertIsNone(result['wall_seconds'])
            self.assertEqual(metrics.aggregate([result])['retries'], 1)

    def test_cli_projection_not_double_counted_and_content_not_exposed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rows = [dict(type='session', version=4, id='session-test'),
                    event('tool/call', dict(callId='c', name='fetch', arguments='SECRET-PROMPT'), seq=1)]
            p = root / 'dsh-sessions/ns/session-test/session.v4.jsonl'; p.parent.mkdir(parents=True)
            p.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
            (root / 'events.jsonl').write_text(json.dumps(dict(type='session', sessionId='session-test')) + '\n' +
                                              json.dumps(rows[1]) + '\n')
            result = metrics.summarize(root, process={})
            self.assertEqual(result['sessions'][0]['tools']['fetch']['calls'], 1)
            self.assertEqual(result['sessions'][0]['role'], 'main')
            self.assertNotIn('SECRET-PROMPT', json.dumps(result))

    def test_child_uuid_sessions_and_failed_attempts_are_included(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for session_id in ('session-main', '1234-child-uuid'):
                p = root / 'dsh-sessions/ns' / session_id / 'session.v4.jsonl'
                p.parent.mkdir(parents=True)
                p.write_text(json.dumps(dict(type='session', version=4, id=session_id)) + '\n' +
                             json.dumps(event('tool/call', dict(callId='same-id-different-session', name='bash'))) + '\n')
            (root / 'events.jsonl').write_text(json.dumps(dict(type='session', sessionId='session-main')) + '\n')
            result = metrics.summarize(root, process={'status': 'failed', 'attempt': 2})
            summary = metrics.aggregate([result])
            self.assertEqual(len(result['sessions']), 2)
            self.assertEqual(summary['tools']['bash']['calls'], 2)
            self.assertEqual(summary['statuses'], {'failed': 1})


if __name__ == '__main__':
    unittest.main()
