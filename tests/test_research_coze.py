"""Conditional third opinion: strict threshold, independent failure and provenance."""
import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone
from scripts import research_coze as coze


class CozeTests(unittest.TestCase):
    def timeout_fixture(self, root, status='pending', replies=None):
        methods, mail = Path(root)/'methods', Path(root)/'mail'
        intent = methods/'output/research_queue/coze/batch-stock/intent.json'
        sent = datetime(2026, 10, 15, 0, tzinfo=timezone.utc)
        coze.atomic(intent, dict(status='pending', request_id='request-1'))
        coze.atomic(mail/'requests.json', dict(version=1, requests={'request-1': dict(
            status=status, sent_at=sent.isoformat(), sending_at=(sent-timedelta(seconds=20)).isoformat(),
            replies=replies or ([{'received_at':sent.isoformat()}] if status=='complete' else []), history=[])}))
        coze.atomic(mail/'request-1/monitor.json', dict(notified=['previous_block'],
            candidate_report_message_id='unmatched-evidence', attachment_blocked=True))
        return methods, mail, intent, sent

    def test_timeout_uses_actual_send_and_exact_fifteen_minutes(self):
        with tempfile.TemporaryDirectory() as root:
            methods, mail, intent, sent = self.timeout_fixture(root)
            self.assertEqual(coze.expire(methods, mail, sent+timedelta(minutes=14, seconds=59))['failed'], [])
            result = coze.expire(methods, mail, sent+timedelta(minutes=15))
            self.assertTrue(result['failed'][0]['notification_needed'])
            self.assertEqual(coze.read(intent)['status'], 'failed')
            self.assertFalse(coze.read(intent)['retry_allowed'])
            monitor = coze.read(mail/'request-1/monitor.json')
            self.assertEqual(monitor['notified'], ['previous_block'])
            self.assertEqual(monitor['candidate_report_message_id'], 'unmatched-evidence')
            history = coze.read(mail/'requests.json')['requests']['request-1']['history']
            coze.expire(methods, mail, sent+timedelta(hours=2))
            self.assertEqual(coze.read(mail/'requests.json')['requests']['request-1']['history'], history)
            with self.assertRaisesRegex(ValueError, 'terminal'):
                coze.bind(intent, 'request-1')
            with self.assertRaises(ValueError):
                coze.hold(intent, 'try again')
            with self.assertRaisesRegex(ValueError, 'terminal'):
                coze.publish(intent, Path(root)/'missing-extraction.json', methods, Path(root)/'exchange')

    def test_timely_reply_survives_delayed_poll_but_late_reply_does_not(self):
        for seconds, expired in [(900, False), (901, True)]:
            with self.subTest(seconds=seconds), tempfile.TemporaryDirectory() as root:
                methods, mail, intent, sent = self.timeout_fixture(root)
                db = coze.read(mail/'requests.json')
                db['requests']['request-1']['replies'] = [{'received_at':(sent+timedelta(seconds=seconds)).isoformat()}]
                coze.atomic(mail/'requests.json', db)
                result = coze.expire(methods, mail, sent+timedelta(hours=1))
                self.assertEqual(bool(result['failed']), expired)

    def test_completed_request_is_not_downgraded_and_failure_crash_recovers(self):
        for status in ['complete', 'failed']:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as root:
                methods, mail, intent, sent = self.timeout_fixture(root, status=status)
                coze.expire(methods, mail, sent+timedelta(hours=1))
                self.assertEqual(coze.read(intent)['status'], 'failed' if status=='failed' else 'pending')
                self.assertEqual(coze.read(mail/'requests.json')['requests']['request-1']['status'], status)

    def test_expiry_does_not_close_other_automations_request(self):
        with tempfile.TemporaryDirectory() as root:
            methods, mail, _, sent = self.timeout_fixture(root)
            db = coze.read(mail/'requests.json')
            db['requests']['other-request'] = dict(status='pending', sending_at=sent.isoformat(), replies=[])
            coze.atomic(mail/'requests.json', db)
            coze.atomic(mail/'other-request/monitor.json', dict(automation_id='another-monitor', status='ACTIVE'))
            coze.expire(methods, mail, sent+timedelta(hours=1))
            self.assertEqual(coze.read(mail/'requests.json')['requests']['other-request']['status'], 'pending')
            self.assertEqual(coze.read(mail/'other-request/monitor.json')['status'], 'ACTIVE')

    def test_strict_ten_percent_boundary_and_symmetry(self):
        self.assertFalse(coze.divergent(10, 11))
        self.assertTrue(coze.divergent(10, 11.01))
        self.assertTrue(coze.divergent(11.01, 10))
        self.assertFalse(coze.divergent(.1, .11))

    def test_missing_nonfinite_or_nonpositive_is_not_comparable(self):
        for value in (None, True, 0, -1, float('nan'), float('inf'), '12'):
            with self.subTest(value=value):
                self.assertFalse(coze.divergent(10, value))

    def test_prices_must_be_exact_explicit_quotes_from_returned_research(self):
        text = 'P1建仓价：10.20元/股；T1卖出价：18.30元/股。'
        extracted = dict(p1={'base': 10.2}, t1=18.3, monitoring=[],
                         evidence={'p1': 'P1建仓价：10.20元/股', 't1': 'T1卖出价：18.30元/股'})
        coze.validate_extraction(extracted, text)
        for key in ('p1', 't1'):
            broken = dict(extracted, **{key: None})
            with self.assertRaises(ValueError):
                coze.validate_extraction(broken, text)
        for quotes in ({'p1': 'not returned', 't1': extracted['evidence']['t1']},
                       {'p1': 'T1卖出价：18.30元/股', 't1': extracted['evidence']['t1']}):
            with self.assertRaises(ValueError):
                coze.validate_extraction(dict(extracted, evidence=quotes), text)
        with self.assertRaises(ValueError):
            coze.validate_extraction(dict(extracted, t1=18.4), text)

    def test_v2_has_no_retired_fields_and_v1_stays_readable(self):
        text = 'P1：10.20元/股；T1：18.30元/股。'
        extracted = dict(p1={'base':10.2}, t1=18.3, monitoring=[], evidence={'p1':'P1：10.20元/股', 't1':'T1：18.30元/股'})
        doc = dict(meta=dict(schema_version=coze.SCHEMA, generator='coze', code='600066.SH', name='offline',
            valuation_date='2026-10-18', currency='CNY', report_path='report.md'),
            price_map=dict(mode='observation', reason='supplement', v50=None, p1=extracted['p1'],
                t1=dict(price_condition='股价≥18.3元/股')), monitoring=[], extraction=extracted)
        coze.validate_document(doc); coze.validate_extraction(extracted, text)
        extracted['p2'] = None
        with self.assertRaises(ValueError): coze.validate_extraction(extracted, text)
        doc['meta']['schema_version'] = coze.LEGACY_SCHEMA
        doc['price_map']['p2'] = dict(status='unavailable', price=None, reason='Coze未提供P2')
        doc['price_map']['t1']['events'] = []
        coze.validate_document(doc); coze.validate_extraction(extracted, text, schema=coze.LEGACY_SCHEMA)

    def test_p2_state_cannot_publish_cancelled_price_or_active_null(self):
        for value in (dict(status='cancelled', price=9, reason='取消'),
                      dict(status='unavailable', price=9, reason='未提供'),
                      dict(status='active', price=None, reason=None),
                      dict(status='suspended', price=None, reason='暂停')):
            with self.assertRaises(ValueError):
                coze.validate_coze_p2(value)
        coze.validate_coze_p2(dict(status='cancelled', price=None, reason='取消'))


if __name__ == '__main__':
    unittest.main()
