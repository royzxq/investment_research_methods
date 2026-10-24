"""Recovery must remain a finite supplement, never a new vote or original retry."""
import copy
import unittest
from scripts import research_recovery as recovery


class RecoveryContractTests(unittest.TestCase):
    def test_wrapper_preserves_every_original_field(self):
        base = dict(schema_version='research-sealed/v2', task_id='HK-09988',
                    batch_id='a'*32, event_key='b'*64, request='/request.json',
                    request_sha256='c'*64, budget_date='2026-10-24', results=[])
        descriptor = dict(path='output/example.json', sha256='d'*64)
        wrapper = dict(base, schema_version=recovery.SEAL_SCHEMA,
                       base_seal=descriptor, recovery_seal=descriptor,
                       recovery_intent=descriptor, recovered_generators=['dsh'])
        recovery.validate_wrapper(wrapper, base)
        for key in base.keys()-{'schema_version'}:
            changed = copy.deepcopy(wrapper)
            changed[key] = None
            with self.subTest(key=key), self.assertRaises(ValueError):
                recovery.validate_wrapper(changed, base)

    def test_no_extra_vote_or_arbitrary_schema_fields(self):
        base = {key: None for key in recovery.BASE_KEYS}
        wrapper = dict(base, schema_version=recovery.SEAL_SCHEMA,
                       base_seal={}, recovery_seal={}, recovery_intent={},
                       recovered_generators=['dsh', 'claude'])
        with self.assertRaises(ValueError):
            recovery.validate_wrapper(wrapper, base)
        wrapper['recovered_generators'] = ['dsh']
        wrapper['extra'] = True
        with self.assertRaises(ValueError):
            recovery.validate_wrapper(wrapper, base)

    def test_completed_refusal_is_not_a_failed_seat(self):
        entry = dict(status='completed', report=None, price_map=None)
        with self.assertRaisesRegex(ValueError, 'failed'):
            recovery.require_failed(entry)
        for artifact in ('report', 'price_map'):
            changed = dict(status='failed', report=None, price_map=None)
            changed[artifact] = {'path': 'draft'}
            with self.assertRaises(ValueError):
                recovery.require_failed(changed)
        recovery.require_failed(dict(status='failed', report=None, price_map=None))
