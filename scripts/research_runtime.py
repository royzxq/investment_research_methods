"""Nonsecret execution profiles and immutable per-batch execution plans.

The request's existing generator remains the production identity. A profile
only declares the harness and supported model options used for that identity;
it is not evidence of the model observed at runtime. Historical batches have
no execution-plan marker and use a fresh inherited profile on every lookup.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
from typing import Any, TypedDict

try:
    from .research_exchange import GENERATORS, DEFAULT_GENERATORS, REQUEST_SCHEMA, REQUEST_SCHEMA_V2, validate_generators
    from .research_harness import default_harness, get_adapter
except ImportError:
    from research_exchange import GENERATORS, DEFAULT_GENERATORS, REQUEST_SCHEMA, REQUEST_SCHEMA_V2, validate_generators
    from research_harness import default_harness, get_adapter


CONFIG_SCHEMA = 'research-runtime-config/v1'
PLAN_SCHEMA = 'research-execution-plan/v1'
PLAN_FILENAME = 'execution-plan.json'
PROFILE_KEYS = {'profile_id', 'revision', 'producer', 'harness', 'models'}
CONFIG_KEYS = {'schema_version', 'profiles', 'active'}
PLAN_KEYS = {'schema_version', 'batch_id', 'request_sha256', 'profiles'}
_SLUG = re.compile(r'[a-z0-9][a-z0-9_-]{0,63}')
_SHA256 = re.compile(r'[0-9a-f]{64}')


class MainModel(TypedDict):
    model: str | None
    effort: str | None


class SubagentModel(TypedDict):
    model: str | None


class Models(TypedDict):
    main: MainModel
    subagent: SubagentModel


class Profile(TypedDict):
    profile_id: str
    revision: int
    producer: str
    harness: str
    models: Models


class RuntimeConfig(TypedDict):
    schema_version: str
    profiles: list[Profile]
    active: dict[str, str]


class ExecutionPlan(TypedDict):
    schema_version: str
    batch_id: str
    request_sha256: str
    profiles: dict[str, Profile]


def _require(condition: Any, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _fields(value: Any, expected: set[str], label: str) -> None:
    # Deliberately do not include supplied keys or values in validation errors:
    # rejected configurations may contain a mistakenly pasted secret.
    _require(type(value) is dict and set(value) == expected,
             label + ': expected exact object fields')


def _producer(value: Any, label: str) -> None:
    _require(isinstance(value, str) and value in GENERATORS,
             label + ': unsupported production identity')


def _slug(value: Any, label: str) -> None:
    _require(isinstance(value, str) and _SLUG.fullmatch(value) is not None,
             label + ': expected safe profile identifier of at most 64 characters')


def _model_option(value: Any, label: str) -> None:
    _require(value is None or (isinstance(value, str) and bool(value.strip())
                             and value == value.strip()
                             and not any(ord(char) < 32 or ord(char) == 127 for char in value)),
             label + ': expected null or nonempty option string')


def _validate_profile(value: Any) -> Profile:
    _fields(value, PROFILE_KEYS, 'profile')
    _slug(value['profile_id'], 'profile.profile_id')
    _require(type(value['revision']) is int and value['revision'] > 0,
             'profile.revision: expected positive integer')
    _producer(value['producer'], 'profile.producer')
    _require(isinstance(value['harness'], str), 'profile.harness: expected harness identifier')
    _fields(value['models'], {'main', 'subagent'}, 'profile.models')
    _fields(value['models']['main'], {'model', 'effort'}, 'profile.models.main')
    _fields(value['models']['subagent'], {'model'}, 'profile.models.subagent')
    _model_option(value['models']['main']['model'], 'profile.models.main.model')
    _model_option(value['models']['main']['effort'], 'profile.models.main.effort')
    _model_option(value['models']['subagent']['model'], 'profile.models.subagent.model')
    result = deepcopy(value)
    try:
        # Harness-specific capability and producer rules have a single owner.
        get_adapter(result['harness']).validate_profile(result)
    except (KeyError, TypeError, ValueError):
        raise ValueError('profile: unsupported harness or model role configuration') from None
    return result


def default_profile(producer: str) -> Profile:
    """Keep legacy inheritance; new DSH calls declare the evaluated model intent."""
    _producer(producer, 'profile.producer')
    models = dict(main=dict(model=None, effort=None), subagent=dict(model=None))
    if producer == 'dsh':
        # A newly supported DSH identity has no marker-free legacy batches.
        # Keep its provider/model intent explicit even for trusted API callers.
        models = dict(main=dict(model='deepseek-flash', effort='high'),
                      subagent=dict(model='deepseek-flash'))
    return _validate_profile(dict(
        profile_id=('dsh-deepseek-flash-high' if producer == 'dsh' else producer + '-inherited'),
        revision=1, producer=producer,
        harness=default_harness(producer),
        models=models,
    ))


def validate_config(value: Any) -> RuntimeConfig:
    """Validate and copy a configuration; no arbitrary CLI/environment options."""
    _fields(value, CONFIG_KEYS, 'runtime config')
    _require(value['schema_version'] == CONFIG_SCHEMA, 'runtime config: unsupported schema')
    _require(type(value['profiles']) is list and bool(value['profiles']),
             'runtime config.profiles: expected nonempty list')
    profiles = [_validate_profile(item) for item in value['profiles']]
    by_id = {item['profile_id']: item for item in profiles}
    _require(len(by_id) == len(profiles), 'runtime config.profiles: duplicate profile identifier')
    active = value['active']
    _require(type(active) is dict and bool(active), 'runtime config.active: expected nonempty object')
    for producer, profile_id in active.items():
        _producer(producer, 'runtime config.active')
        _slug(profile_id, 'runtime config.active.profile_id')
        _require(profile_id in by_id, 'runtime config.active: unknown profile identifier')
        _require(by_id[profile_id]['producer'] == producer,
                 'runtime config.active: profile production identity mismatch')
    return dict(schema_version=CONFIG_SCHEMA, profiles=profiles, active=deepcopy(active))


def _strict_json(raw: bytes, label: str) -> Any:
    def no_duplicates(pairs):
        document = {}
        for key, value in pairs:
            _require(key not in document, label + ': duplicate JSON object key')
            document[key] = value
        return document

    def reject_constant(_constant):
        raise ValueError(label + ': nonfinite JSON number')

    def finite(value):
        if isinstance(value, float):
            _require(math.isfinite(value), label + ': nonfinite JSON number')
        elif isinstance(value, dict):
            for nested in value.values():
                finite(nested)
        elif isinstance(value, list):
            for nested in value:
                finite(nested)

    try:
        document = json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicates,
                              parse_constant=reject_constant)
        finite(document)
    except (UnicodeError, ValueError, RecursionError):
        raise ValueError(label + ': invalid strict JSON') from None
    return document


def load_config(path: str | os.PathLike[str] | None = None) -> RuntimeConfig:
    """Read an explicit config path, or builtins; never inspect the environment."""
    if path is None:
        profiles = [default_profile(producer) for producer in sorted(DEFAULT_GENERATORS)]
        return validate_config(dict(schema_version=CONFIG_SCHEMA, profiles=profiles,
                                    active={item['producer']: item['profile_id'] for item in profiles}))
    try:
        raw = Path(path).read_bytes()
    except (OSError, TypeError, ValueError):
        raise ValueError('runtime config: cannot read explicit configuration file') from None
    return validate_config(_strict_json(raw, 'runtime config'))


def _request_binding(request: Any, request_raw: bytes) -> tuple[str, list[str], str]:
    _require(type(request) is dict, 'execution plan: expected validated request object')
    _require(isinstance(request.get('batch_id'), str) and bool(request['batch_id']),
             'execution plan: request batch identifier required')
    generators = request.get('generators')
    _require(type(generators) is list and bool(generators),
             'execution plan: request generators must be nonempty list')
    for producer in generators:
        _producer(producer, 'execution plan request.generators')
    _require(len(set(generators)) == len(generators), 'execution plan: duplicate request generators')
    validate_generators(generators, request.get('schema_version', REQUEST_SCHEMA))
    _require(isinstance(request_raw, bytes), 'execution plan: request raw bytes required')
    return request['batch_id'], generators, hashlib.sha256(request_raw).hexdigest()


def build_plan(request: dict, request_raw: bytes,
               config: dict | None = None) -> ExecutionPlan:
    """Freeze only selected producer profiles against the exact request bytes."""
    batch_id, generators, request_hash = _request_binding(request, request_raw)
    current = load_config() if config is None else validate_config(config)
    by_id = {item['profile_id']: item for item in current['profiles']}
    selected = {}
    for producer in generators:
        _require(producer in current['active'], 'execution plan: requested producer has no active profile')
        selected[producer] = deepcopy(by_id[current['active'][producer]])
    return validate_plan(dict(schema_version=PLAN_SCHEMA, batch_id=batch_id,
                              request_sha256=request_hash, profiles=selected), request, request_raw)


def validate_plan(plan: Any, request: dict, request_raw: bytes) -> ExecutionPlan:
    """Verify a frozen plan without consulting today's runtime configuration."""
    batch_id, generators, request_hash = _request_binding(request, request_raw)
    _fields(plan, PLAN_KEYS, 'execution plan')
    _require(plan['schema_version'] == PLAN_SCHEMA, 'execution plan: unsupported schema')
    _require(plan['batch_id'] == batch_id, 'execution plan: request batch identifier mismatch')
    _require(isinstance(plan['request_sha256'], str)
             and _SHA256.fullmatch(plan['request_sha256']) is not None
             and plan['request_sha256'] == request_hash,
             'execution plan: request bytes mismatch')
    _require(type(plan['profiles']) is dict and set(plan['profiles']) == set(generators),
             'execution plan.profiles: selected producer set mismatch')
    profiles = {}
    for producer in generators:
        profile = _validate_profile(plan['profiles'][producer])
        _require(profile['producer'] == producer, 'execution plan.profiles: production identity mismatch')
        profiles[producer] = profile
    _require(len({profile['profile_id'] for profile in profiles.values()}) == len(profiles),
             'execution plan.profiles: duplicate profile identifier')
    return dict(schema_version=PLAN_SCHEMA, batch_id=batch_id,
                request_sha256=request_hash, profiles=profiles)


def load_plan(run: str | os.PathLike[str], request: dict, request_raw: bytes,
              snapshot: dict) -> ExecutionPlan | None:
    """Load the manifest-bound plan, preserving marker-free legacy batches.

    An unmarked plan is an injection into a historical batch and is rejected.
    A marked batch can never silently fall back after loss or tampering.
    """
    _require(type(snapshot) is dict, 'execution plan: snapshot object required')
    run_path = Path(run)
    folder = run_path / 'framework-snapshot'
    path = folder / PLAN_FILENAME
    _require(not run_path.is_symlink() and not folder.is_symlink() and not path.is_symlink(),
             'execution plan: symbolic links are not permitted')
    marked = 'execution_plan' in snapshot
    if not marked:
        _require(not path.exists(), 'execution plan: unmarked plan file is not permitted')
        _require(request.get('schema_version') != REQUEST_SCHEMA_V2,
                 'execution plan: v2 request requires a frozen plan')
        return None
    descriptor = snapshot['execution_plan']
    _fields(descriptor, {'path', 'sha256'}, 'execution plan descriptor')
    _require(descriptor['path'] == PLAN_FILENAME, 'execution plan descriptor: fixed path required')
    _require(isinstance(descriptor['sha256'], str)
             and _SHA256.fullmatch(descriptor['sha256']) is not None,
             'execution plan descriptor: expected SHA-256')
    try:
        root = run_path.resolve(strict=True)
        resolved_folder = folder.resolve(strict=True)
        resolved = path.resolve(strict=True)
        _require(resolved_folder.parent == root and resolved.parent == resolved_folder,
                 'execution plan: path escapes frozen batch')
        # Open each owned component without following links. Directory-relative
        # reads keep a replaced snapshot symlink from redirecting the final open.
        no_follow = getattr(os, 'O_NOFOLLOW', 0)
        directory_flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) | no_follow
        run_fd = os.open(run_path, directory_flags)
        try:
            folder_fd = os.open('framework-snapshot', directory_flags, dir_fd=run_fd)
            try:
                file_flags = os.O_RDONLY | no_follow | getattr(os, 'O_NONBLOCK', 0)
                descriptor_fd = os.open(PLAN_FILENAME, file_flags, dir_fd=folder_fd)
                with os.fdopen(descriptor_fd, 'rb') as source:
                    _require(stat.S_ISREG(os.fstat(source.fileno()).st_mode),
                             'execution plan: regular plan file required')
                    raw = source.read()
            finally:
                os.close(folder_fd)
        finally:
            os.close(run_fd)
    except OSError:
        raise ValueError('execution plan: cannot read frozen plan file') from None
    _require(hashlib.sha256(raw).hexdigest() == descriptor['sha256'],
             'execution plan: frozen plan hash mismatch')
    return validate_plan(_strict_json(raw, 'execution plan'), request, request_raw)


def profile_for_plan(plan: dict | None, producer: str) -> Profile:
    """Use a frozen profile, or inherited defaults for a legacy batch only."""
    _producer(producer, 'execution profile.producer')
    if plan is None:
        return default_profile(producer)
    _require(type(plan) is dict and type(plan.get('profiles')) is dict
             and producer in plan['profiles'], 'execution profile: missing frozen producer profile')
    profile = _validate_profile(plan['profiles'][producer])
    _require(profile['producer'] == producer, 'execution profile: production identity mismatch')
    return profile


def canonical_bytes(value: Any) -> bytes:
    """Match the runner's existing JSON encoding exactly."""
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
