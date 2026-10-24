"""Trusted CLI adapters for the local research execution harness.

Profiles select an adapter and model options; they cannot supply executable
commands or load code. Requested model options stay separate from identifiers
actually observed in the runtime event stream.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import threading
from types import MappingProxyType


@dataclass(frozen=True)
class LaunchContext:
    folder: Path
    root: Path
    producer: str
    mcp_servers: dict
    delivery_instruction: str | None = None


def check_codex_cli(cli, root):
    """Reject incompatible CLIs before claiming any single-use batch tasks.

    Automatic approval review and standalone process cleanup are required by
    this runner. Older CLIs must not silently fall back to bypassing approvals
    or to a shared daemon whose children outlive our process group.
    """
    for args, required in (
        (['--help'], ('--no-daemon',)),
        (['exec', '--help'], ('--approve-for-me', '--ephemeral', '--json',
                            '--color', '--output-schema', '--output-last-message',
                            '--cd', '--config')),
    ):
        try:
            result = subprocess.run([cli, *args], cwd=root, stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError(f'Codex CLI capability check failed: {cli}: {exc}') from exc
        if result.returncode:
            raise ValueError(f'Codex CLI capability check failed: {cli} {" ".join(args)} '
                             f'exited {result.returncode}')
        # Match option declarations, not incidental mentions in prose.
        options = set(re.findall(r'^\s+(?:-\w, )?(--[\w-]+)\b', result.stdout, re.M))
        missing = [flag for flag in required if flag not in options]
        if missing:
            raise ValueError(f'Incompatible Codex CLI {cli}: {" ".join(args)} lacks '
                             f'{", ".join(missing)}; select a compatible CLI with --cli '
                             '(verified: Codex CLI 0.160.1). No research tasks launched.')


def _check_options(cli, root, args, required, label):
    """Verify explicitly requested options against declared CLI help flags."""
    try:
        result = subprocess.run([cli, *args], cwd=root, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f'{label} CLI capability check failed: {cli}: {exc}') from exc
    if result.returncode:
        raise ValueError(f'{label} CLI capability check failed: {cli} {" ".join(args)} '
                         f'exited {result.returncode}')
    options = set(re.findall(r'^\s+(?:-\w, )?(--[\w-]+)\b', result.stdout, re.M))
    missing = [flag for flag in required if flag not in options]
    if missing:
        raise ValueError(f'Incompatible {label} CLI {cli}: {" ".join(args)} lacks '
                         f'{", ".join(missing)}; no research tasks launched.')


class CLIAdapter:
    """Interface implemented and registered only by trusted Python code."""

    harness_id = None
    producer = None
    executable = None
    supports_subagent_model = False
    requires_delivery_instruction = False

    @property
    def metadata(self):
        return MappingProxyType(dict(harness_id=self.harness_id,
                                     producer=self.producer,
                                     executable=self.executable))

    def validate_profile(self, profile):
        if not isinstance(profile, dict):
            raise ValueError('execution profile must be an object')
        if profile.get('harness') != self.harness_id:
            raise ValueError('execution profile harness does not match adapter')
        if profile.get('producer') != self.producer:
            raise ValueError('execution profile producer does not match adapter')
        models = profile.get('models')
        if not isinstance(models, dict) or set(models) != {'main', 'subagent'}:
            raise ValueError('execution profile models require only main and subagent roles')
        for role, required in (('main', {'model', 'effort'}), ('subagent', {'model'})):
            spec = models[role]
            if not isinstance(spec, dict) or set(spec) != required:
                raise ValueError(f'execution profile {role} model fields mismatch')
            for key, value in spec.items():
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    raise ValueError(f'execution profile {role}.{key} must be null or nonempty text')
        if models['subagent']['model'] is not None and not self.supports_subagent_model:
            raise ValueError(f'{self.harness_id} does not support a subagent model override')

    def preflight(self, cli, root, profile, codex_check=None):
        self.validate_profile(profile)
        if not cli or not Path(cli).is_file() or not os.access(cli, os.X_OK):
            raise ValueError(f'{self.producer} CLI executable unavailable')

    def _validate_context(self, context, profile):
        self.validate_profile(profile)
        if context.producer != self.producer:
            raise ValueError('launch context producer does not match adapter')

    def command(self, cli, context, profile):
        raise NotImplementedError

    def environment(self, env, profile):
        self.validate_profile(profile)
        return dict(env)

    def launch_environment(self, env, profile, context):
        """Keep legacy environment adapters compatible with per-run hooks."""
        self._validate_context(context, profile)
        return self.environment(env, profile)

    def instruction_from_command(self, args):
        return None

    def receipt(self, folder, strict_json, write_new, encode):
        raise NotImplementedError

    def observed_model(self, folder, strict_json):
        """Record only identifiers emitted by the runtime, never infer a model."""
        path = Path(folder) / 'events.jsonl'
        if not path.exists():
            return None
        for line in path.read_bytes().splitlines():
            try:
                event = strict_json(line, 'event')
            except (ValueError, UnicodeError):
                continue
            if not isinstance(event, dict):
                continue
            if self._model_event(event) and isinstance(event.get('model'), str) and event['model'].strip():
                return event['model']
        return None

    def _model_event(self, event):
        raise NotImplementedError


class CodexCLIAdapter(CLIAdapter):
    harness_id = 'codex-cli'
    producer = 'codex'
    executable = 'codex'

    def preflight(self, cli, root, profile, codex_check=None):
        super().preflight(cli, root, profile, codex_check=codex_check)
        (check_codex_cli if codex_check is None else codex_check)(cli, root)
        main = profile['models']['main']
        required = []
        if main['model'] is not None:
            required.append('--model')
        if main['effort'] is not None:
            required.append('--config')
        if required:
            _check_options(cli, root, ['exec', '--help'], required, 'Codex')

    def command(self, cli, context, profile):
        self._validate_context(context, profile)
        folder = Path(context.folder)
        args = [cli, '--no-daemon', 'exec', '--approve-for-me', '-c', 'web_search="live"',
                '-c', 'mcp_servers.jev.enabled=false',
                '--ephemeral', '--json', '--color', 'never', '--output-schema',
                str(folder / 'receipt-schema.json'), '-o', str(folder / 'cli-receipt.json'),
                '-C', str(Path(context.root).resolve()), '-']
        main = profile['models']['main']
        options = []
        if main['model'] is not None:
            options += ['--model', main['model']]
        if main['effort'] is not None:
            options += ['-c', 'model_reasoning_effort=' + json.dumps(main['effort'])]
        args[3:3] = options
        for name, server in context.mcp_servers.items():
            args[1:1] = ['-c', f'mcp_servers.{name}.command=' + json.dumps(server['command']),
                         '-c', f'mcp_servers.{name}.args=' + json.dumps(server['args'])]
        return args

    def receipt(self, folder, strict_json, write_new, encode):
        return strict_json((Path(folder) / 'cli-receipt.json').read_bytes(), 'CLI receipt')

    def _model_event(self, event):
        return event.get('type') == 'turn.started'


class ClaudeCodeCLIAdapter(CLIAdapter):
    harness_id = 'claude-code-cli'
    producer = 'claude'
    executable = 'claude'
    supports_subagent_model = True
    requires_delivery_instruction = True

    def preflight(self, cli, root, profile, codex_check=None):
        super().preflight(cli, root, profile, codex_check=codex_check)
        main = profile['models']['main']
        required = []
        if main['model'] is not None:
            required.append('--model')
        if main['effort'] is not None:
            required.append('--effort')
        if required:
            _check_options(cli, root, ['--help'], required, 'Claude')

    def command(self, cli, context, profile):
        self._validate_context(context, profile)
        if not isinstance(context.delivery_instruction, str) or not context.delivery_instruction:
            raise ValueError('Claude launch requires a delivery instruction')
        folder = Path(context.folder)
        args = [cli, '-p', '--permission-mode', 'auto', '--permission-prompts', 'none',
                '--append-system-prompt', context.delivery_instruction,
                '--output-format', 'stream-json', '--verbose', '--no-session-persistence',
                '--strict-mcp-config', '--mcp-config', json.dumps({'mcpServers': context.mcp_servers}),
                '--json-schema', (folder / 'receipt-schema.json').read_text()]
        main = profile['models']['main']
        options = []
        if main['model'] is not None:
            options += ['--model', main['model']]
        if main['effort'] is not None:
            options += ['--effort', main['effort']]
        args[2:2] = options
        return args

    def environment(self, env, profile):
        result = super().environment(env, profile)
        model = profile['models']['subagent']['model']
        if model is not None:
            result['CLAUDE_CODE_SUBAGENT_MODEL'] = model
        return result

    def instruction_from_command(self, args):
        try:
            return args[args.index('--append-system-prompt') + 1]
        except (ValueError, IndexError) as exc:
            raise ValueError('Claude command missing delivery instruction') from exc

    def receipt(self, folder, strict_json, write_new, encode):
        folder = Path(folder)
        final = None
        for line in (folder / 'events.jsonl').read_bytes().splitlines():
            try:
                event = strict_json(line, 'CLI event')
            except ValueError:
                continue
            if isinstance(event, dict) and event.get('type') == 'result':
                final = event
        if not final or final.get('is_error') is not False or final.get('subtype') != 'success':
            raise ValueError('Claude returned no successful result; inspect local events/stderr')
        receipt = final.get('structured_output')
        if not isinstance(receipt, dict):
            raise ValueError('Claude returned no structured research receipt')
        write_new(folder / 'cli-receipt.json', encode(receipt))
        return receipt

    def _model_event(self, event):
        return event.get('type') == 'system' and event.get('subtype') == 'init'


_ADAPTERS = {}
_ADAPTER_LOCK = threading.RLock()
_DEFAULT_HARNESSES = MappingProxyType({'codex': 'codex-cli', 'claude': 'claude-code-cli',
                                     'dsh': 'dsh-cli'})


def register_adapter(adapter):
    """Register an already constructed adapter from trusted application code."""
    for field in ('harness_id', 'producer', 'executable'):
        value = getattr(adapter, field, None)
        if not isinstance(value, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', value):
            raise ValueError(f'adapter {field} must be a simple nonempty identifier')
    for name in ('validate_profile', 'preflight', 'command', 'environment',
                 'instruction_from_command', 'receipt', 'observed_model'):
        if not callable(getattr(adapter, name, None)):
            raise ValueError(f'adapter {name} must be callable')
    if type(getattr(adapter, 'requires_delivery_instruction', None)) is not bool:
        raise ValueError('adapter requires_delivery_instruction must be boolean')
    if adapter.harness_id in _ADAPTERS:
        raise ValueError(f'harness adapter already registered: {adapter.harness_id}')
    _ADAPTERS[adapter.harness_id] = adapter


def get_adapter(harness_id):
    if harness_id == 'dsh-cli' and harness_id not in _ADAPTERS:
        _register_dsh()
    if not isinstance(harness_id, str) or harness_id not in _ADAPTERS:
        raise ValueError(f'unknown research harness: {harness_id!r}')
    return _ADAPTERS[harness_id]


def default_harness(producer):
    if not isinstance(producer, str) or producer not in _DEFAULT_HARNESSES:
        raise ValueError(f'unknown research producer: {producer!r}')
    return _DEFAULT_HARNESSES[producer]


def adapter_metadata():
    """Return an immutable snapshot of the registered adapter identities."""
    _register_dsh()
    return MappingProxyType({name: MappingProxyType(dict(harness_id=adapter.harness_id,
                                                        producer=adapter.producer,
                                                        executable=adapter.executable))
                             for name, adapter in _ADAPTERS.items()})


register_adapter(CodexCLIAdapter())
register_adapter(ClaudeCodeCLIAdapter())

def _register_dsh():
    """Load only the fixed trusted module, also permitting direct helper imports."""
    with _ADAPTER_LOCK:
        if 'dsh-cli' not in _ADAPTERS:
            if __package__:
                from .research_dsh import DSHCLIAdapter
            else:
                from research_dsh import DSHCLIAdapter
            register_adapter(DSHCLIAdapter())
