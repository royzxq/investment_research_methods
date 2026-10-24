"""Execution profiles and frozen plans, without packs, CLIs or model APIs."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import research_runtime as runtime


class ResearchRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.request = dict(batch_id='a' * 32, generators=['codex', 'claude'])
        self.raw = runtime.canonical_bytes(self.request)

    def config(self):
        return runtime.load_config()

    def save_plan(self, plan=None, raw=None):
        if raw is None:
            raw = runtime.canonical_bytes(plan if plan is not None else runtime.build_plan(self.request, self.raw))
        folder = self.root / 'framework-snapshot'
        folder.mkdir(exist_ok=True)
        path = folder / runtime.PLAN_FILENAME
        path.write_bytes(raw)
        snapshot = dict(execution_plan=dict(path=runtime.PLAN_FILENAME,
                                            sha256=hashlib.sha256(raw).hexdigest()))
        return path, snapshot

    def test_default_profiles_inherit_all_supported_roles_and_are_new_objects(self):
        for producer, harness in (('codex', 'codex-cli'), ('claude', 'claude-code-cli')):
            with self.subTest(producer=producer):
                profile = runtime.default_profile(producer)
                self.assertEqual(profile, dict(
                    profile_id=producer + '-inherited', revision=1, producer=producer, harness=harness,
                    models=dict(main=dict(model=None, effort=None), subagent=dict(model=None))))
                profile['models']['main']['model'] = 'mutated'
                self.assertIsNone(runtime.default_profile(producer)['models']['main']['model'])

    def test_builtin_config_never_reads_user_configuration_or_environment(self):
        with patch.dict(os.environ, {'RESEARCH_RUNTIME_CONFIG': '/missing/private-config.json',
                                     'OPENAI_API_KEY': 'secret', 'ANTHROPIC_API_KEY': 'secret'}), \
                patch.object(Path, 'read_bytes', side_effect=AssertionError('must use builtins')):
            config = runtime.load_config()
        self.assertEqual(config['schema_version'], runtime.CONFIG_SCHEMA)
        self.assertEqual(config['active'], {'codex': 'codex-inherited', 'claude': 'claude-inherited'})
        self.assertNotIn('secret', runtime.canonical_bytes(config).decode())

    def test_explicit_config_load_and_deepcopy(self):
        config = self.config()
        config['profiles'][0]['models']['main']['model'] = 'requested-model'
        path = self.root / 'runtime.json'
        path.write_bytes(runtime.canonical_bytes(config))
        self.assertEqual(runtime.load_config(path), config)
        validated = runtime.validate_config(config)
        config['profiles'][0]['models']['main']['model'] = 'later-value'
        self.assertEqual(validated['profiles'][0]['models']['main']['model'], 'requested-model')
        validated['active']['codex'] = 'mutated'
        self.assertEqual(runtime.load_config(path)['active']['codex'], 'codex-inherited')

    def test_unknown_missing_and_secret_config_fields_are_rejected_without_values(self):
        for level in ('root', 'profile', 'models', 'main', 'subagent'):
            for key in ('api_key', 'env', 'base_url', 'argv', 'executable', 'token'):
                with self.subTest(level=level, key=key):
                    config = self.config()
                    profile = config['profiles'][0]
                    target = {'root': config, 'profile': profile, 'models': profile['models'],
                              'main': profile['models']['main'], 'subagent': profile['models']['subagent']}[level]
                    target[key + '-PRIVATE-INPUT'] = 'PRIVATE-SECRET-VALUE'
                    with self.assertRaises(ValueError) as caught:
                        runtime.validate_config(config)
                    self.assertNotIn('PRIVATE', str(caught.exception))
        for key in ('schema_version', 'profiles', 'active'):
            config = self.config()
            del config[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                runtime.validate_config(config)

    def test_profile_missing_fields_and_incorrect_types_are_rejected(self):
        for field in runtime.PROFILE_KEYS:
            config = self.config()
            del config['profiles'][0][field]
            with self.subTest(missing=field), self.assertRaises(ValueError):
                runtime.validate_config(config)
        for revision in (True, False, 0, -1, 1.0, '1', None, float('nan')):
            config = self.config()
            config['profiles'][0]['revision'] = revision
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                runtime.validate_config(config)
        for invalid in ([], None, '', {'schema_version': runtime.CONFIG_SCHEMA, 'profiles': [], 'active': {}}):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                runtime.validate_config(invalid)

    def test_profile_identifiers_are_safe_unique_and_bounded(self):
        for name in ('', '../secret', '/absolute', 'a/b', 'a\\b', '.', 'a b', 'x' * 65, 'UPPER'):
            config = self.config()
            config['profiles'][0]['profile_id'] = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                runtime.validate_config(config)
        config = self.config()
        config['profiles'].append(deepcopy(config['profiles'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            runtime.validate_config(config)

    def test_invalid_active_profiles_and_production_identity_are_rejected(self):
        for active in ({}, [], {'dsh': 'codex-inherited'}, {'codex': 'missing'},
                       {'codex': 'claude-inherited'}, {'codex': None}):
            config = self.config()
            config['active'] = active
            with self.subTest(active=active), self.assertRaises(ValueError):
                runtime.validate_config(config)
        for producer, harness in (('dsh', 'codex-cli'), ('codex', 'claude-code-cli'),
                                  ('claude', 'codex-cli'), ('codex', 'unknown-harness')):
            config = self.config()
            config['profiles'][0].update(producer=producer, harness=harness)
            with self.subTest(producer=producer, harness=harness), self.assertRaises(ValueError):
                runtime.validate_config(config)

    def test_only_supported_model_roles_can_be_declared(self):
        profile = runtime.default_profile('claude')
        profile['models'] = dict(main=dict(model='requested-main', effort='high'),
                                 subagent=dict(model='requested-subagent'))
        config = dict(schema_version=runtime.CONFIG_SCHEMA, profiles=[profile],
                      active={'claude': profile['profile_id']})
        self.assertEqual(runtime.validate_config(config)['profiles'][0], profile)
        profile['producer'] = 'codex'
        profile['harness'] = 'codex-cli'
        config['active'] = {'codex': profile['profile_id']}
        with self.assertRaises(ValueError):
            runtime.validate_config(config)
        for model in ('', '   ', ' model', 'model\n', 1, True, {}, []):
            config = self.config()
            config['profiles'][0]['models']['main']['model'] = model
            with self.subTest(model=model), self.assertRaises(ValueError):
                runtime.validate_config(config)
        for change in ('role', 'subagent-effort'):
            config = self.config()
            models = config['profiles'][0]['models']
            if change == 'role':
                models['reviewer'] = dict(model='pretend-effective')
            else:
                models['subagent']['effort'] = 'high'
            with self.subTest(change=change), self.assertRaises(ValueError):
                runtime.validate_config(config)

    def test_strict_config_json_rejects_duplicate_keys_and_nonfinite_values(self):
        valid = runtime.canonical_bytes(self.config()).decode()
        cases = [
            valid.replace('"schema_version":', '"schema_version": "wrong", "schema_version":', 1),
            valid.replace('"revision": 1', '"revision": 1, "revision": 2', 1),
            valid.replace('"model": null', '"model": NaN', 1),
            valid.replace('"model": null', '"model": Infinity', 1),
            valid.replace('"model": null', '"model": -Infinity', 1),
            valid.replace('"model": null', '"model": 1e999', 1),
            '{"private-key": "PRIVATE-SECRET-VALUE", invalid',
        ]
        path = self.root / 'runtime.json'
        for raw in cases:
            path.write_text(raw)
            with self.subTest(raw=raw[:25]), self.assertRaises(ValueError) as caught:
                runtime.load_config(path)
            self.assertNotIn('PRIVATE', str(caught.exception))
        path.write_bytes(b'\xff')
        with self.assertRaises(ValueError):
            runtime.load_config(path)
        with self.assertRaises(ValueError):
            runtime.load_config(self.root / 'missing.json')

    def test_build_plan_binds_request_bytes_and_exact_selected_producers(self):
        request = dict(self.request, generators=['codex'])
        raw = runtime.canonical_bytes(request)
        plan = runtime.build_plan(request, raw)
        self.assertEqual(plan['schema_version'], runtime.PLAN_SCHEMA)
        self.assertEqual(plan['batch_id'], request['batch_id'])
        self.assertEqual(plan['request_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(set(plan['profiles']), {'codex'})
        self.assertEqual(plan['profiles']['codex'], runtime.default_profile('codex'))
        for changed_request, changed_raw in ((dict(request, batch_id='b' * 32), raw),
                                             (request, raw + b'\n'), (self.request, raw)):
            with self.subTest(changed_request=changed_request), self.assertRaises(ValueError):
                runtime.validate_plan(plan, changed_request, changed_raw)

    def test_plan_is_frozen_across_profile_and_active_configuration_changes(self):
        config = self.config()
        alternative = runtime.default_profile('codex')
        alternative.update(profile_id='codex-alternative', revision=2)
        alternative['models']['main'].update(model='requested-at-prepare', effort='high')
        config['profiles'].append(alternative)
        config['active']['codex'] = alternative['profile_id']
        plan = runtime.build_plan(self.request, self.raw, config)
        frozen = deepcopy(plan)
        alternative['models']['main']['model'] = 'changed-after-prepare'
        config['active']['codex'] = 'codex-inherited'
        self.assertEqual(plan, frozen)
        with patch.object(runtime, 'load_config', side_effect=AssertionError('must not consult config')):
            validated = runtime.validate_plan(plan, self.request, self.raw)
            profile = runtime.profile_for_plan(validated, 'codex')
        self.assertEqual(profile['models']['main']['model'], 'requested-at-prepare')
        profile['models']['main']['model'] = 'caller-mutation'
        validated['profiles']['claude']['revision'] = 9
        self.assertEqual(plan, frozen)
        self.assertNotIn('observed_model', plan['profiles']['codex'])

    def test_build_plan_rejects_config_path_and_missing_selected_active_profile(self):
        with self.assertRaises(ValueError):
            runtime.build_plan(self.request, self.raw, self.root / 'runtime.json')
        config = self.config()
        del config['active']['claude']
        with self.assertRaisesRegex(ValueError, 'no active profile'):
            runtime.build_plan(self.request, self.raw, config)
        request = dict(self.request, generators=['codex'])
        self.assertEqual(set(runtime.build_plan(request, self.raw, config)['profiles']), {'codex'})

    def test_plan_rejects_missing_extra_or_mismatched_profiles_and_unknown_fields(self):
        for mutation in ('missing', 'extra', 'producer', 'harness', 'field', 'schema', 'revision'):
            plan = runtime.build_plan(self.request, self.raw)
            if mutation == 'missing':
                del plan['profiles']['codex']
            elif mutation == 'extra':
                plan['profiles']['dsh'] = runtime.default_profile('codex')
            elif mutation == 'producer':
                plan['profiles']['codex'] = runtime.default_profile('claude')
            elif mutation == 'harness':
                plan['profiles']['codex']['harness'] = 'untrusted'
            elif mutation == 'field':
                plan['api_key'] = 'PRIVATE-SECRET-VALUE'
            elif mutation == 'schema':
                plan['schema_version'] = 'research-execution-plan/v99'
            else:
                plan['profiles']['codex']['revision'] = 0
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                runtime.validate_plan(plan, self.request, self.raw)

    def test_minimal_request_validation_does_not_read_data_packs(self):
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('no data packs')):
            self.assertEqual(set(runtime.build_plan(self.request, self.raw)['profiles']), {'codex', 'claude'})
        for generators in ([], ['codex', 'codex'], ['dsh'], 'codex', [None]):
            request = dict(self.request, generators=generators)
            with self.subTest(generators=generators), self.assertRaises(ValueError):
                runtime.build_plan(request, self.raw)
        with self.assertRaises(ValueError):
            runtime.build_plan(self.request, self.raw.decode())

    def test_marked_plan_roundtrip_and_legacy_without_marker(self):
        self.assertIsNone(runtime.load_plan(self.root, self.request, self.raw, {}))
        plan = runtime.build_plan(self.request, self.raw)
        _, snapshot = self.save_plan(plan)
        self.assertEqual(runtime.load_plan(self.root, self.request, self.raw, snapshot), plan)
        with patch.object(runtime, 'load_config', side_effect=AssertionError('must inherit legacy defaults')):
            legacy = runtime.profile_for_plan(None, 'codex')
        self.assertEqual(legacy, runtime.default_profile('codex'))
        with self.assertRaises(ValueError):
            runtime.profile_for_plan(plan, 'dsh')
        with self.assertRaises(ValueError):
            runtime.profile_for_plan({'profiles': {}}, 'codex')

    def test_plan_marker_cannot_be_removed_injected_or_downgraded(self):
        path, snapshot = self.save_plan()
        with self.assertRaisesRegex(ValueError, 'unmarked'):
            runtime.load_plan(self.root, self.request, self.raw, {})
        path.unlink()
        with self.assertRaises(ValueError):
            runtime.load_plan(self.root, self.request, self.raw, snapshot)
        self.assertIsNone(runtime.load_plan(self.root, self.request, self.raw, {}))
        for descriptor in (None, {}, {'path': runtime.PLAN_FILENAME},
                           dict(path=runtime.PLAN_FILENAME, sha256='z' * 64),
                           dict(path=runtime.PLAN_FILENAME, sha256='0' * 64, secret='PRIVATE'),
                           dict(path='../execution-plan.json', sha256='0' * 64),
                           dict(path='/tmp/execution-plan.json', sha256='0' * 64)):
            with self.subTest(descriptor=descriptor), self.assertRaises(ValueError):
                runtime.load_plan(self.root, self.request, self.raw, {'execution_plan': descriptor})

    def test_plan_tampering_wrong_request_duplicate_json_and_nonfinite_are_rejected(self):
        path, snapshot = self.save_plan()
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            runtime.load_plan(self.root, self.request, self.raw, snapshot)
        _, snapshot = self.save_plan()
        with self.assertRaisesRegex(ValueError, 'request bytes mismatch'):
            runtime.load_plan(self.root, self.request, self.raw + b'\n', snapshot)
        valid = runtime.canonical_bytes(runtime.build_plan(self.request, self.raw)).decode()
        for raw in (valid.replace('"revision": 1', '"revision": 1, "revision": 2', 1),
                    valid.replace('"model": null', '"model": NaN', 1),
                    valid.replace('"model": null', '"model": 1e999', 1)):
            _, snapshot = self.save_plan(raw=raw.encode())
            with self.subTest(raw=raw[:25]), self.assertRaises(ValueError):
                runtime.load_plan(self.root, self.request, self.raw, snapshot)

    def test_plan_file_and_snapshot_symlinks_are_rejected_even_when_hash_matches(self):
        path, snapshot = self.save_plan()
        real = self.root / 'outside-plan.json'
        path.rename(real)
        path.symlink_to(real)
        with self.assertRaisesRegex(ValueError, 'symbolic'):
            runtime.load_plan(self.root, self.request, self.raw, snapshot)
        path.unlink()
        path.symlink_to(self.root / 'missing-plan.json')
        with self.assertRaisesRegex(ValueError, 'symbolic'):
            runtime.load_plan(self.root, self.request, self.raw, {})
        path.unlink()
        real.rename(path)
        folder = path.parent
        outside_folder = self.root / 'other-snapshot'
        folder.rename(outside_folder)
        folder.symlink_to(outside_folder, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symbolic'):
            runtime.load_plan(self.root, self.request, self.raw, snapshot)

    def test_plan_path_must_be_regular_file(self):
        path, snapshot = self.save_plan()
        path.unlink()
        path.mkdir()
        with self.assertRaises(ValueError):
            runtime.load_plan(self.root, self.request, self.raw, snapshot)
        with self.assertRaises(ValueError):
            runtime.load_plan(self.root, self.request, self.raw, {})

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'named pipes require POSIX')
    def test_named_pipe_plan_is_rejected_without_waiting_for_a_writer(self):
        path, snapshot = self.save_plan()
        path.unlink()
        os.mkfifo(path)
        with self.assertRaisesRegex(ValueError, 'regular plan file'):
            runtime.load_plan(self.root, self.request, self.raw, snapshot)

    def test_canonical_encoding_matches_runner_format(self):
        value = {'中文': ['value', None], 'count': 2}
        expected = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
        self.assertEqual(runtime.canonical_bytes(value), expected)
        with self.assertRaises(ValueError):
            runtime.canonical_bytes({'value': float('nan')})


if __name__ == '__main__':
    unittest.main()
