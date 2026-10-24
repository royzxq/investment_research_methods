"""Isolated CC/DSH comparison arms; deliberately unrelated to publication APIs.

The caller supplies a frozen workspace and a credential-free local proxy route.
No production runner, queue, registry, result contract, or consensus entry is used.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import signal
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import time
from urllib.parse import urlsplit
import uuid


ROOT = Path(__file__).resolve().parents[1]
USER_HOME = Path('/Users/xinquanzhou')
SANDBOX_EXEC = '/usr/bin/sandbox-exec'
DEFAULT_CC = Path('/Users/xinquanzhou/.local/bin/claude')
DEFAULT_DSH = Path('/Users/xinquanzhou/.local/bin/dsh')
INHERITED_ENV = frozenset(('PATH', 'LANG', 'LC_ALL', 'LC_CTYPE', 'LC_MESSAGES', 'TZ', 'TERM'))
MODEL = 'deepseek-flash'
DUMMY_KEY = 'isolated-trial-proxy-placeholder'
PYTHON_LIBS_SOURCE = USER_HOME / 'Library/Python/3.10/lib/python/site-packages'


# This deliberately limited compatibility layer uses the same frozen PyMuPDF
# installation in both arms. It does not claim to be a Poppler installation and
# refuses unimplemented options rather than silently changing their meaning.
_PDF_TOOL = r'''
import json, math, os, pathlib, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'python-libs'))
import pymupdf
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
if args == ['-v'] or args == ['--version']:
    print(name + ' isolated PyMuPDF compatibility layer ' + pymupdf.VersionBind)
    raise SystemExit(0)
values = {'-f': 'first', '-l': 'last', '-r': 'dpi', '-rx': 'dpi_x', '-ry': 'dpi_y',
          '-scale-to': 'scale', '-scale-to-x': 'scale_x', '-scale-to-y': 'scale_y',
          '-upw': 'password', '-opw': 'password', '-enc': 'encoding'}
flags = {'-png', '-jpeg', '-singlefile', '-gray', '-mono', '-cropbox', '-layout',
         '-raw', '-nopgbrk', '-q'}
options, positional = {}, []
index = 0
try:
    while index < len(args):
        item = args[index]
        if item in values:
            index += 1
            if index == len(args):
                raise ValueError('missing value for ' + item)
            options[values[item]] = args[index]
        elif item in flags:
            options[item[1:]] = True
        elif item.startswith('-') and item != '-':
            raise ValueError('unsupported compatibility option ' + item)
        else:
            positional.append(item)
        index += 1
    allowed = {
        'pdfinfo': {'first', 'last', 'password'},
        'pdftotext': {'first', 'last', 'password', 'encoding', 'layout', 'raw', 'nopgbrk', 'q'},
        'pdftoppm': {'first', 'last', 'password', 'dpi', 'dpi_x', 'dpi_y', 'scale', 'scale_x',
                    'scale_y', 'png', 'jpeg', 'singlefile', 'gray', 'mono', 'cropbox', 'q'},
    }
    unsupported = set(options) - allowed.get(name, set())
    if unsupported:
        raise ValueError('unsupported compatibility option for ' + name + ': ' + ','.join(sorted(unsupported)))
    if options.get('png') and options.get('jpeg'):
        raise ValueError('choose exactly one output image format')
    if not positional or len(positional) > (1 if name == 'pdfinfo' else 2):
        raise ValueError('expected PDF path and optional output path/prefix')
    if positional[0] == '-':
        pdf_bytes = sys.stdin.buffer.read(104857601)
        if len(pdf_bytes) > 104857600:
            raise ValueError('stdin PDF exceeds 100 MiB')
        doc = pymupdf.open(stream=pdf_bytes, filetype='pdf')
        file_size = len(pdf_bytes)
    else:
        doc = pymupdf.open(positional[0])
        file_size = pathlib.Path(positional[0]).stat().st_size
    if doc.needs_pass and not doc.authenticate(options.get('password', '')):
        raise ValueError('PDF password required or incorrect')
    first = int(options.get('first', 1))
    last = int(options.get('last', len(doc)))
    if first < 1 or last < first or first > len(doc):
        raise ValueError('invalid page range')
    last = min(last, len(doc))
    if name == 'pdfinfo':
        metadata = doc.metadata or {}
        for key, label in [('title', 'Title'), ('author', 'Author'), ('creator', 'Creator'),
                           ('producer', 'Producer'), ('creationDate', 'CreationDate'),
                           ('modDate', 'ModDate')]:
            if metadata.get(key):
                print(label + ': ' + metadata[key])
        print('Pages: ' + str(len(doc)))
        print('Encrypted: ' + ('yes' if doc.is_encrypted else 'no'))
        page = doc[first - 1]
        print('Page size: ' + str(page.rect.width) + ' x ' + str(page.rect.height) + ' pts')
        print('File size: ' + str(file_size) + ' bytes')
        print('PDF version: ' + str(metadata.get('format', 'PDF')).removeprefix('PDF '))
    elif name == 'pdftotext':
        if options.get('encoding', 'UTF-8').lower().replace('-', '') != 'utf8':
            raise ValueError('compatibility layer supports only UTF-8')
        # PyMuPDF's sorted text is an explicit text-extraction fallback. It is
        # not byte-equivalent to Poppler -layout and must not prove visual QA.
        pages = [doc[n].get_text(sort=not options.get('raw', False)) for n in range(first - 1, last)]
        text = ('\n' if options.get('nopgbrk') else '\f').join(pages)
        target = positional[1] if len(positional) == 2 else str(pathlib.Path(positional[0]).with_suffix('.txt'))
        if target == '-':
            sys.stdout.write(text)
        else:
            pathlib.Path(target).write_text(text, encoding='utf-8')
    elif name == 'pdftoppm':
        dpi_x = float(options.get('dpi_x', options.get('dpi', 150)))
        dpi_y = float(options.get('dpi_y', options.get('dpi', 150)))
        if not all(math.isfinite(v) and 0 < v <= 1200 for v in (dpi_x, dpi_y)):
            raise ValueError('render DPI must be finite and in (0,1200]')
        if options.get('mono'):
            raise ValueError('monochrome rendering is not implemented')
        prefix = positional[1] if len(positional) == 2 else None
        if prefix is None and not options.get('singlefile') and first != last:
            raise ValueError('multiple-page rendering requires an output prefix')
        extension = 'png' if options.get('png') else 'jpg' if options.get('jpeg') else 'ppm'
        for number in range(first - 1, min(first, last) if options.get('singlefile') else last):
            page = doc[number]
            sx, sy = dpi_x / 72, dpi_y / 72
            if 'scale' in options:
                size = int(options['scale'])
                if size <= 0 or size > 16384:
                    raise ValueError('scale-to must be in [1,16384]')
                sx = sy = size / max(page.rect.width, page.rect.height)
            for option, dimension, axis in [('scale_x', page.rect.width, 'x'), ('scale_y', page.rect.height, 'y')]:
                if option in options:
                    size = int(options[option])
                    if size != -1 and not 0 < size <= 16384:
                        raise ValueError('scale dimension must be -1 or in [1,16384]')
                    if size != -1:
                        if axis == 'x': sx = size / dimension
                        else: sy = size / dimension
            if options.get('scale_x') == '-1': sx = sy
            if options.get('scale_y') == '-1': sy = sx
            if page.rect.width * sx * page.rect.height * sy > 64000000:
                raise ValueError('render exceeds 64 million pixels')
            pix = page.get_pixmap(matrix=pymupdf.Matrix(sx, sy),
                  colorspace=pymupdf.csGRAY if options.get('gray') else pymupdf.csRGB, alpha=False)
            if prefix is None or prefix == '-':
                sys.stdout.buffer.write(pix.tobytes(extension))
            else:
                suffix = '' if options.get('singlefile') else '-' + str(number + 1).zfill(len(str(len(doc))))
                pix.save(prefix + suffix + '.' + extension)
    else:
        raise ValueError('unknown PDF compatibility tool')
except (ValueError, OSError, RuntimeError) as exc:
    print(name + ': isolated PyMuPDF compatibility layer: ' + str(exc), file=sys.stderr)
    raise SystemExit(2)
'''


def _write_json(path: Path, value: dict) -> None:
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode()
    temporary = path.parent / ('.process-' + uuid.uuid4().hex + '.tmp')
    try:
        fd = os.open(str(temporary), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        # Replacing the directory entry cannot follow a CLI-created symlink.
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _path(value, *, directory=False) -> Path:
    original = Path(value).expanduser().absolute()
    for part in (original, *original.parents):
        if part.is_symlink():
            raise ValueError('trial paths must not contain symlinks')
    result = original.resolve()
    if directory and not result.is_dir():
        raise ValueError('trial directory does not exist')
    return result


def _proxy(proxy_url: str) -> tuple[str, int]:
    parsed = urlsplit(proxy_url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError('proxy requires a loopback HTTP endpoint with an explicit port') from exc
    if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or port is None
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or not parsed.path.startswith('/') or '..' in parsed.path.split('/')):
        raise ValueError('proxy requires a loopback HTTP endpoint with an explicit port')
    return proxy_url.rstrip('/'), port


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def trial_environment(run_dir: Path, proxy_url: str, *, harness: str,
                      max_output_tokens=16384, stream_idle_timeout=120, inherited=None) -> dict:
    """Build a new allow-listed environment; never copy provider credentials."""
    proxy_url, _ = _proxy(proxy_url)
    source = os.environ if inherited is None else inherited
    env = {key: source[key] for key in INHERITED_ENV if key in source}
    env.setdefault('PATH', '/usr/bin:/bin:/usr/sbin:/sbin')
    # The shared PDF tools are installed here on this host; provide the same
    # executable search path to both arms, including shell subprocesses.
    if '/usr/local/bin' not in env['PATH'].split(os.pathsep):
        env['PATH'] = '/usr/local/bin' + os.pathsep + env['PATH']
    env['PATH'] = str(run_dir / 'runtime-bin') + os.pathsep + env['PATH']
    env.setdefault('LANG', 'en_US.UTF-8')
    for name in ('home', 'claude-config', 'dsh-home', 'agents-home', 'tmp'):
        (run_dir / name).mkdir(mode=0o700, exist_ok=True)
    env.update({
        'HOME': str(run_dir / 'home'),
        'CLAUDE_CONFIG_DIR': str(run_dir / 'claude-config'),
        'DSH_HOME': str(run_dir / 'dsh-home'),
        'DSH_AGENTS_HOME': str(run_dir / 'agents-home'),
        'TMPDIR': str(run_dir / 'tmp'),
        'ANTHROPIC_API_KEY': DUMMY_KEY,
        'ANTHROPIC_BASE_URL': proxy_url,
        'DEEPSEEK_API_KEY': DUMMY_KEY,
        'DEEPSEEK_BASE_URL': proxy_url,
        'DEEPSEEK_SEARCH_BASE_URL': proxy_url + '/v1',
        'DSH_TELEMETRY_DISABLED': '1',
        # The native loader's default TMPDIR cache lives under the protected
        # repository. Node realpaths its ancestors even when the leaf is allowed;
        # load the installed read-only native binary instead of broadening reads.
        'NARB_DISABLE_NATIVE_CACHE': '1',
        'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1',
        'DISABLE_TELEMETRY': '1',
        'DISABLE_ERROR_REPORTING': '1',
        'CLAUDE_CODE_SUBAGENT_MODEL': MODEL,
        'CLAUDE_CODE_MAX_OUTPUT_TOKENS': str(max_output_tokens),
        'CLAUDE_CODE_TMPDIR': str(run_dir / 'tmp'),
        # zsh/bash here-doc temporary files use these shell-specific roots;
        # TMPDIR alone does not stop a model shell from selecting /tmp.
        'TMPPREFIX': str(run_dir / 'tmp' / 'zsh'),
        'API_TIMEOUT_MS': str(round(stream_idle_timeout * 1000)),
        'PYTHONPATH': str(run_dir / 'python-libs'),
        'PYTHONDONTWRITEBYTECODE': '1',
        'ANTHROPIC_DEFAULT_HAIKU_MODEL': MODEL,
        'ANTHROPIC_DEFAULT_SONNET_MODEL': MODEL,
        'ANTHROPIC_DEFAULT_OPUS_MODEL': MODEL,
        'ANTHROPIC_DEFAULT_FABLE_MODEL': MODEL,
    })
    if harness not in ('cc', 'dsh'):
        raise ValueError('harness must be cc or dsh')
    return env


def freeze_python_libraries(run_dir: Path) -> dict:
    """Copy only the two existing PDF code packages into this arm, with hashes.

    The child never receives read access to the real user site-packages tree.
    No package manager or network is used; an absent installation fails closed.
    """
    destination = run_dir / 'python-libs'
    destination.mkdir(mode=0o700, exist_ok=False)
    files = {}
    for name in ('pymupdf', 'fitz'):
        source = PYTHON_LIBS_SOURCE / name
        if not source.is_dir() or source.is_symlink():
            raise ValueError('installed PDF dependency package unavailable')
        for original in sorted(source.rglob('*')):
            if '__pycache__' in original.parts:
                continue
            if original.is_symlink():
                raise ValueError('PDF dependency package contains a symlink')
            if original.is_dir():
                continue
            if not original.is_file():
                raise ValueError('PDF dependency package contains a nonregular file')
            relative = Path(name) / original.relative_to(source)
            target = destination / relative
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            shutil.copyfile(original, target)
            target.chmod(0o500 if original.stat().st_mode & 0o111 else 0o400)
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest != hashlib.sha256(original.read_bytes()).hexdigest():
                raise ValueError('installed PDF dependency changed while freezing')
            files[relative.as_posix()] = {'sha256': digest, 'bytes': target.stat().st_size}
    executables = {}
    binaries = run_dir / 'runtime-bin'
    binaries.mkdir(mode=0o700, exist_ok=False)
    wrapper = '#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' -B "$@"\n'
    for name in ('python', 'python3', 'pdfinfo', 'pdftoppm', 'pdftotext'):
        target = binaries / name
        source_text = wrapper if name in ('python', 'python3') else (
            '#!' + sys.executable + ' -B\n' + _PDF_TOOL)
        target.write_text(source_text, encoding='utf-8')
        target.chmod(0o500)
        executables[name] = {'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                             'bytes': target.stat().st_size}
    manifest = {'schema_version': 'research-trial-runtime-dependencies/v2',
                'source': 'existing-local-installation-copy', 'source_root': str(PYTHON_LIBS_SOURCE),
                'python_version': sys.version.split()[0], 'packages': ['pymupdf', 'fitz'], 'files': files,
                'executables': executables,
                'pdf_tools': 'limited PyMuPDF compatibility layer; not Poppler; unsupported options fail',
                'bytecode_policy': 'python wrapper -B plus OS-denied runtime writes; strict file set'}
    _write_json(run_dir / 'runtime-deps.json', manifest)
    return manifest


def runtime_libraries_intact(run_dir: Path, manifest: dict) -> bool:
    for dirname, key in (('python-libs', 'files'), ('runtime-bin', 'executables')):
        if key not in manifest:
            # Older fixtures/manifests have only the copied Python packages.
            if key == 'executables':
                continue
            return False
        root = run_dir / dirname
        if root.is_symlink() or not root.is_dir():
            return False
        actual = {}
        for path in root.rglob('*'):
            if path.is_symlink():
                return False
            if path.is_dir():
                continue
            if not path.is_file():
                return False
            actual[path.relative_to(root).as_posix()] = {
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
        if actual != manifest[key]:
            return False
    return True


def sandbox_profile(run_dir, proxy_url, *, online=True, protected_roots=None) -> str:
    """Seatbelt policy using JSON string escaping, never shell interpolation."""
    if not isinstance(online, bool):
        raise ValueError('online must be a boolean')
    run = _path(run_dir, directory=True)
    _, port = _proxy(proxy_url)
    roots = [USER_HOME, ROOT, ROOT.parent / 'ai_investment', run.parent]
    if protected_roots:
        roots.extend(Path(path).absolute().resolve() for path in protected_roots)
    roots = sorted(set(str(path.resolve()) for path in roots))
    deny_reads = ' '.join('(subpath ' + json.dumps(path) + ')' for path in roots)
    # These are installed code/runtime roots, not user configuration roots.
    # Never allow ~/.local or ~/.nvm as a whole: both can contain credentials.
    code_roots = [USER_HOME / '.local/lib/node_modules/@deepseek-ai/dsh',
                  USER_HOME / '.local/share/dsh-runtime/node_modules/node']
    code_files = [DEFAULT_DSH.resolve(), DEFAULT_CC.resolve()]
    node_candidate = USER_HOME / '.nvm/versions/node/v22.14.0/bin/node'
    if node_candidate.is_file():
        code_files.append(node_candidate.resolve())
    read_grants = ['(subpath ' + json.dumps(str(run)) + ')']
    # DSH's durable attachment store opens/fsyncs every ancestor of DSH_HOME.
    # Literal directory grants permit those directory handles (and directory
    # entry names), not sibling or home-file contents. All negative file-read
    # probes below remain mandatory for both arms.
    read_grants.extend('(literal ' + json.dumps(str(path)) + ')' for path in run.parents)
    read_grants.extend('(subpath ' + json.dumps(str(path.resolve())) + ')' for path in code_roots)
    read_grants.extend('(literal ' + json.dumps(str(path)) + ')' for path in code_files)
    lines = ['(version 1)', '(allow default)', '(deny file-write*)',
             '(allow file-write* (subpath ' + json.dumps(str(run)) + ') (literal "/dev/null"))',
             '(deny file-write* (subpath ' + json.dumps(str(run / 'python-libs')) + ') '
             '(subpath ' + json.dumps(str(run / 'runtime-bin')) + '))',
             # Metadata stays available for Node realpath/lstat of ancestors;
             # file/directory content under the real home remains inaccessible.
             '(deny file-read-data ' + deny_reads + ')',
             '(allow file-read-data ' + ' '.join(read_grants) + ')']
    if not online:
        lines.extend(['(deny network-outbound)',
                      # Seatbelt's network parser accepts localhost, not a
                      # numeric host. The proxy URL still requires 127.0.0.1;
                      # this policy also permits IPv6 loopback at the same port.
                      '(allow network-outbound (remote ip "localhost:' + str(port) + '"))'])
    return '\n'.join(lines) + '\n'


_PROBE = r'''
import errno,json,pathlib,socket,sys
inside,outside,secret,other,private,host,port,blocked_port=sys.argv[1:]
facts={}
try:
    pathlib.Path(inside).write_text('allowed')
    facts['inside_write']=True
except OSError:
    facts['inside_write']=False
try:
    pathlib.Path(outside).write_text('must be denied')
    facts['outside_write_denied']=False
except OSError as e:
    facts['outside_write_denied']=e.errno in (errno.EPERM,errno.EACCES)
for label,folder in [('runtime_library_write_denied','python-libs'),
                     ('runtime_executable_write_denied','runtime-bin')]:
    try:
        (pathlib.Path(inside).parent/folder/pathlib.Path(inside).name).write_text('must be denied')
        facts[label]=False
    except OSError as e:
        facts[label]=e.errno in (errno.EPERM,errno.EACCES)
for label,path in [('project_read_denied',secret),('other_arm_read_denied',other),
                   ('private_home_read_denied',private)]:
    try:
        pathlib.Path(path).read_bytes()
        facts[label]=False
    except OSError as e:
        facts[label]=e.errno in (errno.EPERM,errno.EACCES)
if blocked_port!='0':
    try:
        with socket.create_connection((host,int(port)),timeout=2): pass
        facts['proxy_connect']=True
    except OSError:
        facts['proxy_connect']=False
    try:
        with socket.create_connection((host,int(blocked_port)),timeout=2): pass
        facts['other_network_denied']=False
    except OSError as e:
        facts['other_network_denied']=e.errno in (errno.EPERM,errno.EACCES)
print(json.dumps(facts))
'''


def _home_private_probe():
    """Select an existing private home file by metadata only, never its content."""
    for name in ('.zshrc', '.zprofile', '.bash_profile', '.gitconfig'):
        candidate = USER_HOME / name
        if candidate.is_file():
            return candidate
    return None


def verify_isolation(run_dir, proxy_url, *, online=True, profile_path=None,
                     sandbox_exec=SANDBOX_EXEC, runner=None) -> dict:
    """Fail closed before a model process starts, using file and local TCP probes.

    Offline uses a second loopback listener to prove the exact-port exception;
    no external host receives a validation request. ``runner`` is a test seam.
    """
    run = _path(run_dir, directory=True)
    _, proxy_port = _proxy(proxy_url)
    profile = Path(profile_path) if profile_path else run / 'isolation-check.sb'
    if profile_path is None:
        profile.write_text(sandbox_profile(run, proxy_url, online=online))
        profile.chmod(0o600)
    runner = subprocess.run if runner is None else runner
    nonce = uuid.uuid4().hex
    inside = run / ('.sandbox-inside-' + nonce)
    outside = run.parent / ('.sandbox-write-outside-' + nonce)
    other = run.parent / ('.sandbox-other-arm-' + nonce)
    other.write_text('existing outside canary')
    other.chmod(0o600)
    listener = None
    try:
        private_probe = _home_private_probe()
        if private_probe is None:
            return {'success': False, 'checks': {}, 'error': 'no_existing_private_home_probe'}
        blocked_port = 0
        if not online:
            listener = socket.socket()
            listener.bind(('127.0.0.1', 0))
            listener.listen(2)
            blocked_port = listener.getsockname()[1]
        args = [str(sandbox_exec), '-f', str(profile), sys.executable, '-I', '-c', _PROBE,
                str(inside), str(outside), str(ROOT / 'AGENTS.md'), str(other), str(private_probe),
                '127.0.0.1', str(proxy_port), str(blocked_port)]
        env = {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'HOME': str(run / 'home'),
               'TMPDIR': str(run / 'tmp'), 'LANG': 'en_US.UTF-8'}
        completed = runner(args, cwd=str(run), env=env, capture_output=True, timeout=15)
        raw = completed.stdout
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8', errors='strict')
        try:
            facts = json.loads(raw)
        except (ValueError, UnicodeError):
            facts = {}
        expected = ['inside_write', 'outside_write_denied', 'project_read_denied',
                    'other_arm_read_denied', 'private_home_read_denied',
                    'runtime_library_write_denied', 'runtime_executable_write_denied']
        if not online:
            expected += ['proxy_connect', 'other_network_denied']
        good = completed.returncode == 0 and all(facts.get(key) is True for key in expected)
        good = good and not outside.exists()
        stderr = completed.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode('utf-8', errors='replace')
        return {'success': good, 'checks': facts, 'exit_code': completed.returncode,
                'diagnostic': stderr[:4096],
                'offline_network_probe': 'local exact-port allow and other-port denial' if not online else None}
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        return {'success': False, 'checks': {}, 'error': type(exc).__name__}
    finally:
        if listener is not None:
            listener.close()
        for path in (inside, outside, other, run / 'python-libs' / inside.name,
                     run / 'runtime-bin' / inside.name):
            path.unlink(missing_ok=True)


def _dsh_patch(workspace: Path, run: Path, proxy_url: str, tokens: int,
               stream_idle_timeout=120) -> str:
    # JSON strings are valid YAML scalars and keep configured paths as data.
    rows = [
        {'id': 'agent-default-model', 'config': {'provider': 'deepseek-official', 'model': MODEL,
                                               'reasoningEffort': 'high'}},
        {'id': 'llm-deepseek', 'config': {'apiKeyEnv': 'DEEPSEEK_API_KEY', 'baseURL': proxy_url,
                                        'reasoningEffort': 'high', 'maxTokens': tokens,
                                        'streamIdleTimeoutMs': round(stream_idle_timeout * 1000)}},
        {'id': 'subagent', 'config': {'maxActiveSubagents': 2}},
        {'id': 'tool-subagent', 'config': {'provider': 'spawn', 'toolName': 'subagent',
          'agentOptions': {'provider': 'deepseek-official',
          'model': MODEL, 'reasoningEffort': 'high', 'maxTokens': tokens}, 'maxDepth': 1}},
        {'id': 'session-persistence-jsonl', 'config': {'root': str(run / 'dsh-sessions'),
                                                      'compression': 'none'}},
        # The outer Seatbelt policy already confines every descendant. macOS
        # rejects nested sandbox_apply; this documented inner mode bypasses only
        # DSH's second OS wrapper while keeping the outer policy in force.
        {'id': 'sandbox-policy', 'config': {'mode': 'danger-full-access', 'workspaceRoot': str(workspace)}},
        {'id': 'approval', 'config': {'policy': 'never'}},
        {'id': 'permission', 'config': {'presets': {
          'trial': {'sandbox': 'danger-full-access', 'approval': 'never'}}, 'defaultPreset': 'trial'}},
        {'id': 'web-search-deepseek', 'config': {'apiKeyEnv': 'DEEPSEEK_API_KEY',
          'baseURL': proxy_url + '/v1', 'model': MODEL, 'maxTokens': 4096, 'maxUses': 5}},
    ]
    return json.dumps(rows, ensure_ascii=False, indent=2) + '\n'


def _kill_group(process, *, grace=3):
    """Reap the leader and terminate descendants, even after leader exit."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        if sig == signal.SIGTERM:
            try:
                process.wait(timeout=grace)
            except subprocess.TimeoutExpired:
                pass
    process.wait(timeout=grace)


def summarize_events(path: Path, harness: str) -> dict:
    final = False
    completed = False
    count = 0
    invalid = 0
    truncated = 0
    last_result = None
    last_reason = None
    last_type = None
    errors = 0
    active_turn = False
    active_turn_id = None
    seen_turn_start = False
    seen_turn_end = False
    turn_sequence_valid = True
    # A CLI can replace a pathname it may write. Refuse both symlinks and a
    # named pipe without blocking the supervisor outside the task timeout.
    descriptor = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('trial event log must be a regular file')
        for line in stream:
            if not line.strip():
                continue
            count += 1
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError('not an object')
            except (ValueError, UnicodeError):
                invalid += 1
                continue
            if event.get('truncated'):
                truncated += 1
            last_type = event.get('type')
            if last_type == 'error':
                errors += 1
            if harness == 'cc' and event.get('type') == 'result':
                last_result = event
            if harness == 'dsh' and event.get('type') == 'final':
                final = True
            if harness == 'dsh' and event.get('type') == 'status' and event.get('phase') == 'turn_start':
                if active_turn:
                    turn_sequence_valid = False
                seen_turn_start = True
                active_turn = True
                active_turn_id = event.get('turn')
                last_reason = None
                final = False
            if harness == 'dsh' and event.get('type') == 'status' and event.get('phase') == 'turn_end':
                ending_id = event.get('turn')
                if active_turn:
                    if active_turn_id is not None and ending_id is not None and active_turn_id != ending_id:
                        turn_sequence_valid = False
                        last_reason = None
                    else:
                        active_turn = False
                        active_turn_id = None
                        last_reason = event.get('reason')
                elif not seen_turn_start and not seen_turn_end:
                    # Older captured traces can contain only a terminal end.
                    # This compatibility never closes a newer observed start.
                    last_reason = event.get('reason')
                else:
                    turn_sequence_valid = False
                    last_reason = None
                seen_turn_end = True
                final = False
    if harness == 'cc':
        completed = bool(last_type == 'result' and last_result and last_result.get('subtype') == 'success'
                         and last_result.get('is_error') is False)
    else:
        # Current DSH uses the discriminated reason object {kind: ...}; retain
        # string support for older traces without treating an arbitrary object
        # or unknown/failed/aborted kind as completion.
        reason_kind = last_reason.get('kind') if isinstance(last_reason, dict) else last_reason
        completed = (last_type == 'final' and final and reason_kind == 'completed' and errors == 0
                     and not active_turn and turn_sequence_valid)
    return {'terminal_success': completed, 'events': count, 'invalid_event_lines': invalid,
            'truncated_events': truncated, 'last_turn_reason': last_reason,
            'unended_turn': active_turn if harness == 'dsh' else None,
            'turn_sequence_valid': turn_sequence_valid if harness == 'dsh' else None}


def run_trial(harness, workspace, run_dir, prompt, proxy_url, *, timeout=1800,
              online=True, max_output_tokens=16384, claude_cli=None, dsh_cli=None,
              cancelled=None, stream_idle_timeout=120) -> dict:
    """Run exactly one private comparison arm and return its local process facts.

    ``prompt`` is bytes or UTF-8 text, sent byte-for-byte on stdin. ``workspace``
    must be an existing directory beneath this arm's fresh ``run_dir``. A failed
    sandbox preflight records process.json and refuses to invoke a model CLI.
    """
    if harness not in ('cc', 'dsh'):
        raise ValueError('harness must be cc or dsh')
    if not isinstance(online, bool):
        raise ValueError('online must be a boolean')
    if cancelled is not None and not callable(getattr(cancelled, 'is_set', None)):
        raise ValueError('cancelled must provide is_set() or be None')
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout) or timeout <= 0):
        raise ValueError('timeout must be finite and positive')
    if isinstance(max_output_tokens, bool) or not isinstance(max_output_tokens, int) or max_output_tokens < 1:
        raise ValueError('max_output_tokens must be a positive integer')
    if (isinstance(stream_idle_timeout, bool) or not isinstance(stream_idle_timeout, (int, float))
            or not math.isfinite(stream_idle_timeout) or stream_idle_timeout <= 0):
        raise ValueError('stream_idle_timeout must be finite and positive')
    if not isinstance(prompt, (bytes, str)):
        raise ValueError('prompt must be bytes or text')
    raw_prompt = prompt.encode('utf-8') if isinstance(prompt, str) else prompt
    if not raw_prompt.strip():
        raise ValueError('prompt must not be blank')
    proxy_url, _ = _proxy(proxy_url)
    run = _path(run_dir, directory=True)
    workspace = _path(workspace, directory=True)
    if workspace == run or not _within(workspace, run):
        raise ValueError('workspace must be a separate directory inside the arm run_dir')
    forbidden_project_config = ('.claude/settings.json', '.claude/settings.local.json',
                                '.claude/hooks', '.claude/plugins')
    if any((workspace / name).exists() or (workspace / name).is_symlink()
           for name in forbidden_project_config):
        raise ValueError('trial workspace must exclude project settings, hooks, and plugins')
    for name in ('process.json', 'events.jsonl', 'stderr.log', 'sandbox.sb',
                 'dsh-isolation.patch.yml', 'runtime-deps.json', 'python-libs', 'runtime-bin'):
        if (run / name).exists():
            raise ValueError('trial output already exists; use a fresh arm directory')
    run.chmod(0o700)
    cli_input = Path((claude_cli or DEFAULT_CC) if harness == 'cc' else (dsh_cli or DEFAULT_DSH)).expanduser()
    if not cli_input.is_absolute():
        raise ValueError('trial CLI path must be absolute')
    cli = cli_input.resolve()
    if not cli.is_file() or not os.access(cli, os.X_OK):
        raise ValueError('trial CLI executable is unavailable')
    env = trial_environment(run, proxy_url, harness=harness, max_output_tokens=max_output_tokens,
                            stream_idle_timeout=stream_idle_timeout)
    runtime_dependencies = freeze_python_libraries(run)
    profile = run / 'sandbox.sb'
    profile.write_text(sandbox_profile(run, proxy_url, online=online))
    profile.chmod(0o600)
    if harness == 'cc':
        args = [str(cli), '-p', '--setting-sources', 'project', '--tools', 'default',
                '--model', MODEL + '[1m]', '--effort', 'high',
                '--permission-mode', 'auto', '--permission-prompts', 'none', '--output-format',
                'stream-json', '--verbose', '--no-session-persistence', '--strict-mcp-config',
                '--mcp-config', json.dumps({'mcpServers': {}})]
    else:
        patch = run / 'dsh-isolation.patch.yml'
        patch.write_text(_dsh_patch(workspace, run, proxy_url, max_output_tokens, stream_idle_timeout))
        patch.chmod(0o600)
        args = [str(cli), '--profile', 'headless', '--patch', str(patch), '--json', '-']
    command = [SANDBOX_EXEC, '-f', str(profile), *args]
    process_data = {'schema_version': 'research-harness-trial/v1', 'harness': harness,
                    'success': False, 'consensus_eligible': False, 'production': False,
                    'workspace': str(workspace), 'run_dir': str(run), 'command': command,
                    'prompt_sha256': hashlib.sha256(raw_prompt).hexdigest(),
                    'model': MODEL, 'effort': 'high', 'max_output_tokens': max_output_tokens,
                    'main_child_output_limit_shared': True,
                    'stream_idle_timeout_seconds': stream_idle_timeout,
                    'ancestor_directory_read_grants': [str(path) for path in run.parents],
                    'outer_sandbox': 'seatbelt',
                    'dsh_inner_sandbox': 'disabled-outer-seatbelt-enforced' if harness == 'dsh' else None,
                    'runtime_dependencies_sha256': hashlib.sha256(
                        json.dumps(runtime_dependencies, sort_keys=True).encode()).hexdigest(),
                    'online': bool(online), 'timeout_seconds': timeout,
                    'project_settings_hooks_plugins_excluded': True,
                    'environment_keys': sorted(env), 'timed_out': False, 'cancelled': False,
                    'exit_code': None}
    _write_json(run / 'process.json', process_data)
    for name in ('events.jsonl', 'stderr.log'):
        with (run / name).open('xb'):
            pass
        (run / name).chmod(0o600)
    if cancelled is not None and cancelled.is_set():
        process_data['cancelled'] = True
        _write_json(run / 'process.json', process_data)
        return process_data
    isolation = verify_isolation(run, proxy_url, online=online, profile_path=profile)
    process_data['isolation'] = isolation
    if not isolation.get('success'):
        process_data['error'] = 'isolation_preflight_failed'
        _write_json(run / 'process.json', process_data)
        return process_data
    started = time.monotonic()
    child = None
    try:
        with (run / 'events.jsonl').open('ab') as events, (run / 'stderr.log').open('ab') as errors:
            child = subprocess.Popen(command, cwd=str(workspace), env=env, stdin=subprocess.PIPE,
                                     stdout=events, stderr=errors, start_new_session=True, umask=0o077)
            process_data['pid'] = child.pid
            # Supervisors can inspect/stop the live process before it finishes.
            _write_json(run / 'process.json', process_data)
            try:
                deadline = started + timeout
                pending_input = raw_prompt
                while True:
                    if cancelled is not None and cancelled.is_set():
                        process_data['cancelled'] = True
                        break
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        process_data['timed_out'] = True
                        break
                    try:
                        child.communicate(input=pending_input, timeout=min(0.25, remaining))
                        break
                    except subprocess.TimeoutExpired:
                        # communicate retains its unwritten input after timeout;
                        # providing it again would duplicate/reject the prompt.
                        pending_input = None
            finally:
                _kill_group(child)
            process_data['exit_code'] = child.returncode
        process_data.update(summarize_events(run / 'events.jsonl', harness))
        process_data['runtime_dependencies_intact'] = runtime_libraries_intact(run, runtime_dependencies)
        process_data['success'] = (not process_data['timed_out'] and not process_data['cancelled']
                                   and child.returncode == 0
                                   and process_data['terminal_success']
                                   and process_data['runtime_dependencies_intact']
                                   and process_data['invalid_event_lines'] == 0)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        process_data['error'] = type(exc).__name__
    finally:
        if child is not None and child.poll() is None:
            _kill_group(child)
            process_data['exit_code'] = child.returncode
        process_data['elapsed_seconds'] = round(time.monotonic() - started, 3)
        _write_json(run / 'process.json', process_data)
    return process_data
