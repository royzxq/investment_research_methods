"""Trusted DeepSeek Harness headless integration; no provider calls here.

Credentials remain in the child environment. The per-attempt profile and
session roots contain only non-secret execution configuration and research.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

try:
    from .research_harness import CLIAdapter
except ImportError:
    from research_harness import CLIAdapter


MODEL = 'deepseek-flash'
EFFORT = 'high'
MAX_TOKENS = 32768
STREAM_IDLE_MS = 180000
BASE_URL = 'https://api.deepseek.com/anthropic'
SEARCH_URL = BASE_URL + '/v1'
MAX_EVENT_LINE = 16 * 1024 * 1024
RECEIPT_ENCODING = 'strict-json-or-single-json-fence/v1'
DATA_HEALTH_VERSION = 'data-health-v1'
EVIDENCE_RECOVERY_VERSION = 'evidence-recovery-v1'
EVIDENCE_CONTEXT_VERSION = 'evidence-context-v1'


def _data_health_source():
    return _regular_bytes(Path(__file__).with_name('research_data_health.mjs'))


def _evidence_recovery_sources():
    return {target: _regular_bytes(Path(__file__).with_name(source)) for target, source in (
        ('dsh-evidence-recovery.mjs', 'research_evidence_recovery.mjs'),
        ('dsh-document-recovery.py', 'research_document_recovery.py'))}


def _evidence_context_source():
    return _regular_bytes(Path(__file__).with_name('research_evidence_context.mjs'))


def _context_audit_node():
    node = shutil.which('node')
    if not node:
        raise ValueError('Evidence context citation audit requires installed Node.js')
    node = str(Path(node).resolve())
    probe = subprocess.run([node, '-e', 'process.exit(Number(process.versions.node.split(".")[0]) >= 20 ? 0 : 1)'],
                           capture_output=True, timeout=10)
    if probe.returncode:
        raise ValueError('Evidence context citation audit requires Node.js 20 or newer')
    return node

# DSH deliberately scrubs credential-shaped ambient environment names from
# tool children. This fixed trusted plugin restores only the data credential
# required by the existing research scripts; model API credentials stay out.
DATA_ENV_BRIDGE = '''export const name = 'research-data-environment';
export const inject = ['subprocess'];
export function apply(ctx) {
  const runtime = ctx.subprocess;
  const original = runtime.spawn;
  const replacement = function(spec) {
    const token = process.env.TUSHARE_TOKEN;
    const env = {...(spec.env ?? {})};
    if (typeof token === 'string' && token.length) env.TUSHARE_TOKEN = token;
    return original.call(runtime, {...spec, env});
  };
  runtime.spawn = replacement;
  ctx.on('dispose', () => {
    if (runtime.spawn === replacement) runtime.spawn = original;
  });
}
'''


def _new(path, raw):
    """Only create a regular file, allowing exact idempotent preparation."""
    path = Path(path)
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != raw:
            raise ValueError('DSH runtime preparation conflicts with existing files')
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)


def _encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode()


@lru_cache(maxsize=1)
def _pdf_python():
    """Require the already installed, architecture-compatible PDF fallback."""
    candidates = [Path(sys.executable), Path(sys.base_prefix) / 'bin/python3']
    if shutil.which('python3'):
        candidates.append(Path(shutil.which('python3')))
    # This local macOS deployment already has independent framework/conda
    # interpreters. Probe them in place; never copy libraries across versions.
    versions = Path('/Library/Frameworks/Python.framework/Versions')
    candidates.extend(sorted(versions.glob('3.*/bin/python3'), reverse=True))
    candidates.append(Path.home() / 'miniconda3/bin/python3')
    checked = set()
    probe = ('import pymupdf; d=pymupdf.open(); p=d.new_page(width=8,height=8); '
             'pix=p.get_pixmap(); assert pix.width==8 and pix.height==8')
    for candidate in candidates:
        # A venv launcher may be a symlink to a base interpreter: resolving it
        # before execution loses its pyvenv.cfg and installed site-packages.
        candidate = candidate.absolute()
        if candidate in checked or not candidate.is_file() or not os.access(candidate, os.X_OK):
            continue
        checked.add(candidate)
        try:
            result = subprocess.run([str(candidate), '-c', probe], stdin=subprocess.DEVNULL,
                                    capture_output=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0:
            return str(candidate)
    raise ValueError('DSH requires an installed architecture-compatible Python with PyMuPDF for PDF fallback')


def _regular_lines(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('DSH runtime log must be a regular file')
        while True:
            line = stream.readline(MAX_EVENT_LINE + 1)
            if not line:
                return
            if len(line) > MAX_EVENT_LINE:
                raise ValueError('DSH runtime event exceeds the supported bound')
            if line.strip():
                yield line


def _regular_bytes(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('DSH runtime input must be a regular file')
        raw = stream.read(MAX_EVENT_LINE + 1)
        if len(raw) > MAX_EVENT_LINE:
            raise ValueError('DSH runtime input exceeds the supported bound')
        return raw


def _key(env):
    direct = env.get('DEEPSEEK_API_KEY')
    if isinstance(direct, str) and direct.strip():
        return direct
    # This migration reuses the same, explicitly authorized official DeepSeek
    # credential. A variable name alone never proves its provider identity.
    settings = Path.home() / '.claude/settings.json'
    try:
        raw = _regular_bytes(settings)
        document = json.loads(raw)
        configured = document['env']
        if not isinstance(configured, dict) or configured.get('ANTHROPIC_BASE_URL') != BASE_URL:
            raise ValueError
        override = env.get('ANTHROPIC_BASE_URL')
        if override is not None and override != BASE_URL:
            raise ValueError
        for name in ('ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY'):
            value = configured.get(name)
            if isinstance(value, str) and value.strip():
                return value
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        pass
    raise ValueError('DSH requires an available credential for the verified official DeepSeek route')


def _events(folder, strict_json):
    """Require a fresh, ordered completed headless run, then its exact answer."""
    active = None
    last_turn = 0
    ended = False
    final = None
    session = None
    count = 0
    for raw in _regular_lines(Path(folder) / 'events.jsonl'):
        event = strict_json(raw, 'DSH CLI event')
        if not isinstance(event, dict):
            raise ValueError('DSH CLI event must be an object')
        kind = event.get('type')
        if final is not None:
            raise ValueError('DSH event follows its final answer')
        if count == 0 and kind != 'session':
            raise ValueError('DSH run missing opening session event')
        count += 1
        if kind == 'error':
            raise ValueError('DSH returned an error event')
        if kind == 'session':
            value = event.get('sessionId')
            if session is not None or not isinstance(value, str) or not re.fullmatch(r'session-[A-Za-z0-9-]+', value):
                raise ValueError('DSH opening session identity is invalid')
            session = value
        elif kind == 'status' and event.get('phase') in ('turn_start', 'turn_end'):
            turn = event.get('turn')
            if event.get('truncated') or type(turn) is not int or turn < 1:
                raise ValueError('DSH terminal turn event is invalid')
            if event['phase'] == 'turn_start':
                if active is not None or turn <= last_turn:
                    raise ValueError('DSH turn sequence is invalid')
                active = turn
                ended = False
            else:
                reason = event.get('reason')
                if active != turn or not isinstance(reason, dict) or reason.get('kind') != 'completed':
                    raise ValueError('DSH turn did not complete successfully in order')
                last_turn = turn
                active = None
                ended = True
        elif kind == 'final':
            if active is not None or not ended or event.get('truncated') or not isinstance(event.get('text'), str):
                raise ValueError('DSH final answer lacks an ordered completed turn')
            final = event['text']
    if final is None:
        raise ValueError('DSH returned no terminal final answer')
    return final, session


def _aktools_runtime(root):
    """Resolve one trusted, version-locked local sidecar; never install on a run."""
    root = Path(root).resolve()
    lock = root / 'config/dsh_aktools-0.1.4-r1.lock.json'
    python = root / 'output/runtime/aktools-0.1.4/bin/python'
    try:
        expected = json.loads(lock.read_bytes())
        probe = '''import hashlib,importlib.metadata as m,json,sys,sysconfig
from pathlib import Path
site=Path(sysconfig.get_paths()['purelib'])
spec=json.load(sys.stdin)
packages={d.metadata['Name'].lower().replace('_','-'):d.version for d in m.distributions() if d.metadata['Name'].lower() not in ('pip','setuptools')}
files={p:hashlib.sha256((site/p).read_bytes()).hexdigest() for p in spec['source_sha256']}
print(json.dumps(dict(python=f'{sys.version_info.major}.{sys.version_info.minor}',packages=packages,source_sha256=files)))
'''
        result = subprocess.run([str(python), '-I', '-c', probe], input=json.dumps(expected),
                                capture_output=True, text=True, timeout=10)
        observed = json.loads(result.stdout)
        if result.returncode or any(observed[key] != expected[key] for key in ('python', 'packages', 'source_sha256')):
            raise ValueError()
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        raise ValueError('AKTools isolated runtime is missing or differs from its tested lock') from None
    return str(python), hashlib.sha256(lock.read_bytes()).hexdigest()


class DSHCLIAdapter(CLIAdapter):
    harness_id = 'dsh-cli'
    producer = 'dsh'
    executable = 'dsh'
    supports_subagent_model = True
    requires_delivery_instruction = True

    def validate_profile(self, profile):
        super().validate_profile(profile)
        if 'tools' in profile:
            tools = profile['tools']
            if (type(tools) is not dict or not {'search', 'fetch'}.issubset(tools)
                    or set(tools) - {'search', 'fetch', 'aktools', 'data_health', 'evidence_recovery', 'evidence_context'}
                    or tools['search'] not in ('deepseek-official', 'deepseek-search-api')
                    or tools['fetch'] not in ('http', 'deepseek-fetch-api')
                    or tools.get('aktools') not in (None, 'aktools-0.1.4-r1')
                    or ('data_health' in tools and tools['data_health'] != DATA_HEALTH_VERSION)
                    or ('evidence_recovery' in tools and (tools['evidence_recovery'] != EVIDENCE_RECOVERY_VERSION
                        or tools.get('data_health') != DATA_HEALTH_VERSION))
                    or ('evidence_context' in tools and (tools['evidence_context'] != EVIDENCE_CONTEXT_VERSION
                        or tools.get('evidence_recovery') != EVIDENCE_RECOVERY_VERSION))):
                raise ValueError('DSH tools require the supported nonsecret provider selections')
        models = profile['models']
        if models['main']['model'] is None or models['subagent']['model'] is None:
            raise ValueError('DSH requires explicit main and subagent model selections')
        if models['main']['effort'] not in ('off', 'low', 'high', 'max'):
            raise ValueError('DSH requires a supported explicit reasoning effort')

    def preflight(self, cli, root, profile, codex_check=None):
        super().preflight(cli, root, profile, codex_check=codex_check)
        _key(os.environ)
        _pdf_python()
        if profile.get('tools', {}).get('aktools'):
            _aktools_runtime(root)
        if profile.get('tools', {}).get('data_health'):
            _data_health_source()
        if profile.get('tools', {}).get('evidence_recovery'):
            _evidence_recovery_sources()
        if profile.get('tools', {}).get('evidence_context'):
            _evidence_context_source()
            _context_audit_node()
        with tempfile.TemporaryDirectory(prefix='research-dsh-preflight-') as temp:
            env = dict(os.environ, DSH_HOME=str(Path(temp) / 'dsh-home'),
                       HOME=str(Path(temp) / 'home'), DSH_TELEMETRY_DISABLED='1')
            Path(env['HOME']).mkdir()
            for args, required in ((['--help'], {'--profile', '--patch'}),
                                   (['--profile', 'headless', '--help'], {'--json'})):
                try:
                    result = subprocess.run([cli, *args], cwd=root, env=env, stdin=subprocess.DEVNULL,
                                            capture_output=True, text=True, timeout=15)
                except (OSError, subprocess.TimeoutExpired):
                    raise ValueError('DSH CLI capability check could not complete') from None
                options = set(re.findall(r'^\s+(?:-\w, )?(--[\w-]+)\b', result.stdout, re.M))
                if result.returncode != 0 or not required.issubset(options):
                    raise ValueError('DSH CLI lacks required headless JSON/profile/patch capabilities')

    def environment(self, env, profile):
        result = super().environment(env, profile)
        result['DEEPSEEK_API_KEY'] = _key(result)
        # The official route is deliberate, independent of shell/project .env.
        result['DEEPSEEK_BASE_URL'] = BASE_URL
        result['DEEPSEEK_SEARCH_BASE_URL'] = SEARCH_URL
        result['DSH_TELEMETRY_DISABLED'] = '1'
        for key in ('DSH_PERMISSION_MODE', 'DSH_TOOLS_MODE'):
            result.pop(key, None)
        return result

    def launch_environment(self, env, profile, context):
        self._validate_context(context, profile)
        result = self.environment(env, profile)
        folder = Path(context.folder).resolve()
        for key, relative in (('HOME', 'dsh-private-home'), ('DSH_HOME', 'dsh-home'),
                              ('DSH_AGENTS_HOME', 'dsh-agents-home'),
                              ('XDG_CONFIG_HOME', 'dsh-config'), ('XDG_CACHE_HOME', 'dsh-cache'),
                              ('XDG_DATA_HOME', 'dsh-data')):
            target = folder / relative
            if target.is_symlink():
                raise ValueError('DSH private home cannot be a symbolic link')
            target.mkdir(mode=0o700, parents=False, exist_ok=True)
            result[key] = str(target)
        return result

    def command(self, cli, context, profile):
        self._validate_context(context, profile)
        if not isinstance(context.delivery_instruction, str) or not context.delivery_instruction:
            raise ValueError('DSH launch requires a delivery instruction')
        folder = Path(context.folder).resolve()
        main = profile['models']['main']
        model, effort = main['model'], main['effort']
        subagent_model = profile['models']['subagent']['model']
        receipt_instruction = ('最终答复必须仅为一个严格JSON对象，完全符合本次回执schema；'
                               '不得使用Markdown围栏或额外文字。schema：'
                               + (folder / 'receipt-schema.json').read_text())
        pdf_python = _pdf_python()
        pdf_instruction = ('原始PDF读取仍按原研究方法核原页。若pdftotext/pdfinfo不可用或报架构错误，'
                           f'使用已验证的 {pdf_python} 与 import pymupdf 按页读取或渲染原PDF；'
                           '程序例：doc=pymupdf.open(path); doc[page-1].get_text()；'
                           '图表/扫描页用get_pixmap()渲染核对，不凭抽取失败判证据不存在。')
        delivery = context.delivery_instruction + '\n' + pdf_instruction + '\n' + receipt_instruction
        health_source = None
        health_config = None
        recovery_sources = None
        recovery_config = None
        context_source = None
        evidence_context = None
        context_node = None
        if profile.get('tools', {}).get('data_health'):
            # The existing frozen receipt schema owns the valuation cutoff.
            schema = json.loads(_regular_bytes(folder / 'receipt-schema.json'))
            dates = schema.get('properties', {}).get('valuation_date', {}).get('enum')
            if (not isinstance(dates, list) or len(dates) != 1 or not isinstance(dates[0], str)
                    or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', dates[0])):
                raise ValueError('Data health requires the frozen receipt valuation date')
            from datetime import date
            date.fromisoformat(dates[0])
            health_dir = folder / 'data-health'
            if health_dir.is_symlink():
                raise ValueError('DSH data health directory cannot be a symbolic link')
            health_dir.mkdir(mode=0o700, exist_ok=True)
            health_source = _data_health_source()
            _new(folder / 'dsh-data-health.mjs', health_source)
            health_config = {'directory': str(health_dir), 'asOf': dates[0]}
            delivery += ('\n本次 web_fetch 与 AKTools get_data 已启用取数前后机械体检，'
                         '原响应与体检记录在本次 data-health/。rejected 只拒绝该次响应，'
                         'review_required 须按所需输入处理分页、截断、身份/单位/日期缺口；'
                         'mechanical_checks_only 也不表示事实核验通过。不得自动修值或补零。'
                         '只用已核片段时明确范围；记录原值、换算依据与采用值，缺口只限制受影响判断。'
                         'bash/curl、PDF 和其它取数路径不被此插件拦截，继续按 data-acquisition.md 核验。')
        if profile.get('tools', {}).get('evidence_recovery'):
            recovery_dir = folder / 'evidence-recovery'
            if recovery_dir.is_symlink():
                raise ValueError('DSH evidence recovery directory cannot be a symbolic link')
            recovery_dir.mkdir(mode=0o700, exist_ok=True)
            recovery_sources = _evidence_recovery_sources()
            for name, raw in recovery_sources.items():
                _new(folder / name, raw)
            recovery_config = dict(directory=str(recovery_dir), asOf=health_config['asOf'],
                python=pdf_python, worker=str(folder / 'dsh-document-recovery.py'),
                healthModule=str(folder / 'dsh-data-health.mjs'))
            delivery += ('\n本次启用补证闭环：网页截断/空壳、PDF取数失败和AKTools分页不足会触发一次有界补证。'
                         '直接PDF链接可用 research_recover_evidence(url)，分页仍不足可按gap_id续补。'
                         '每轮最多3页、每数据集最多3轮，单来源下载去重；失败不得循环重试。'
                         'research_read_evidence 可搜索/按页读取正文或生成原页图片；图片生成不等于已查看。'
                         '对实际读取的receipt_id，用 research_record_evidence_use 记录采用范围、相关输入、'
                         '报告章节或未解决原因；程序记录读取和研究者判断，不自动确认事实或最终引用。'
                         '完整下载、分页收齐和事实核验分开；按原方法核主体、披露日、单位和所需附注。'
                         '最终正文保留来源URL和页码/章节；本次 evidence-recovery/ 留存原件和补证过程。')
        if profile.get('tools', {}).get('evidence_context'):
            context_dir = folder / 'evidence-context'
            if context_dir.is_symlink():
                raise ValueError('DSH evidence context directory cannot be a symbolic link')
            context_dir.mkdir(mode=0o700, exist_ok=True)
            context_source = _evidence_context_source()
            _new(folder / 'dsh-evidence-context.mjs', context_source)
            context_node = _context_audit_node()
            evidence_context = dict(directory=str(context_dir), recoveryDirectory=recovery_config['directory'],
                                    asOf=health_config['asOf'])
            delivery += ('\n本次有独立于对话压缩的证据定位簿。已允许的web_fetch与补证文档进入持久索引；'
                         '其他bash/本地文件路径不自动登记。用research_find_evidence找来源或在原文定位，'
                         '用research_open_evidence按页/范围读原文，获得稳定evidence_id。'
                         '关键估值输入及反证用research_pin_evidence保留主体、期间、单位、币种、披露日与未决状态，未知留空。'
                         '压缩或裁剪后通过evidence_id核哈希重读，不把摘要当原文。'
                         '引用用research_cite_evidence生成markdown并原样放入报告，包括隐藏的evidence-cite标记；'
                         '引用中的quote必须逐字对应。关键标记默认要求最终引用；不采用时明确理由并设required_citation=false。'
                         '交付前research_check_citations检查文本；runner还会核最终暂存报告的引用和已标记的关键漏引。'
                         '机械核验不证明事实或经济推论；不改变投资方法或最终JSON字段。')
        aktools_runtime = None
        if profile.get('tools', {}).get('aktools'):
            aktools_runtime = _aktools_runtime(context.root)
            delivery += ('\n可按需用 AKTools MCP 获取结构化历史财务、补已有数据缺口：先 search_interfaces，'
                         '再 describe_interface，最后 get_data。它是第三方数据线索，沿用现有一手证据及财务口径验收；'
                         '不得替代原公告/PDF核页或覆盖已验证共享事实。记录接口、参数、报告期、抓取时点和来源；'
                         '检查 total_rows/offset/returned_rows/truncated，默认100行、最多1000行并非完整历史，'
                         '按所需报告期分页；分页终止按 offset+returned_rows>=total_rows，'
                         'truncated只表示本页非整表，尾页也可能为true。港股币种/单位可能缺失，'
                         '须从原公告确认，缺失保持未知。'
                         '冷调用可能数十秒，同进程缓存60秒，缓存命中不代表数据更新。失败时继续现有取数路径。')
        _new(folder / 'dsh-delivery-instruction.txt', delivery.encode())
        _new(folder / 'dsh-data-environment.mjs', DATA_ENV_BRIDGE.encode())
        rows = [
            {'id': 'agent-default-model', 'config': {'provider': 'deepseek-official', 'model': model,
                                                    'reasoningEffort': effort}},
            {'id': 'llm-deepseek', 'config': {'apiKeyEnv': 'DEEPSEEK_API_KEY', 'baseURL': BASE_URL,
                                             'reasoningEffort': effort, 'maxTokens': MAX_TOKENS,
                                             'streamIdleTimeoutMs': STREAM_IDLE_MS}},
            {'id': 'tool-subagent', 'config': {'provider': 'spawn', 'toolName': 'subagent', 'maxDepth': 1,
              'agentOptions': {'provider': 'deepseek-official', 'model': subagent_model,
                               'reasoningEffort': effort, 'maxTokens': MAX_TOKENS}}},
            {'id': 'tool-subagent-fork', 'config': {'provider': 'fork', 'toolName': 'subagent_fork', 'maxDepth': 1,
              'agentOptions': {'provider': 'deepseek-official', 'model': subagent_model,
                               'reasoningEffort': effort, 'maxTokens': MAX_TOKENS}}},
            {'id': 'subagent', 'config': {'maxActiveSubagents': 2}},
            {'id': 'session-persistence-jsonl', 'config': {'root': str(folder / 'dsh-sessions'), 'compression': 'none'}},
            {'id': 'storage-json', 'config': {'root': str(folder / 'dsh-storage')}},
            {'id': 'system-prompt', 'config': {'personaPrefix': delivery}},
            {'id': 'sandbox-policy', 'config': {'mode': 'workspace-write', 'workspaceRoot': str(Path(context.root).resolve())}},
            {'id': 'approval', 'config': {'policy': 'never'}},
            {'id': 'permission', 'config': {'presets': {'research': {'sandbox': 'workspace-write', 'approval': 'never'}},
                                             'defaultPreset': 'research'}},
            {'id': 'web-search-deepseek', 'config': {'apiKeyEnv': 'DEEPSEEK_API_KEY', 'baseURL': SEARCH_URL,
                                                     'model': model, 'maxTokens': 4096, 'maxUses': 5}},
            {'insert': [{'id': 'research-data-environment', 'name': str(folder / 'dsh-data-environment.mjs')}]},
        ]
        if 'tools' in profile:
            rows.extend([
                {'id': 'web', 'config': {'searchProvider': profile['tools']['search'],
                                         'fetchProvider': profile['tools']['fetch']}},
                {'id': 'web-deepseek-api', 'config': {'apiKeyEnv': 'DEEPSEEK_API_KEY',
                    'baseURL': 'https://api.deepseek.com/v1/tools', 'count': 10}},
            ])
        if health_config:
            rows.append({'insert': [{'id': 'research-data-health',
                'name': str(folder / 'dsh-data-health.mjs'), 'config': health_config}]})
        if recovery_config:
            rows.append({'insert': [{'id': 'research-evidence-recovery',
                'name': str(folder / 'dsh-evidence-recovery.mjs'), 'config': recovery_config}]})
        if evidence_context:
            rows.append({'insert': [{'id': 'research-evidence-context',
                'name': str(folder / 'dsh-evidence-context.mjs'), 'config': evidence_context}]})
        mcp_rows = []
        if aktools_runtime:
            # AKTools writes a local log in cwd; keep it inside this attempt.
            aktools_cwd = folder / 'dsh-aktools'
            if aktools_cwd.is_symlink():
                raise ValueError('DSH AKTools working directory cannot be a symbolic link')
            aktools_cwd.mkdir(mode=0o700, exist_ok=True)
            mcp_rows.append({'id': 'research-mcp-aktools', 'name': '@deepseek-ai/dsh-mcp-client',
                'config': {'serverName': 'aktools', 'transport': 'stdio', 'command': aktools_runtime[0],
                    'args': ['-I', '-B', '-m', 'aktools.mcp_server'], 'cwd': str(aktools_cwd),
                    'env': {'AKTOOLS_TIMEOUT': '20', 'AKTOOLS_CACHE_TTL': '60', 'PYTHONUNBUFFERED': '1'},
                    'toolCallTimeoutMs': 90000, 'failOnStartupError': False}})
        for name, server in context.mcp_servers.items():
            if name == 'aktools' and aktools_runtime:
                raise ValueError('DSH MCP AKTools namespace is reserved by the frozen tool profile')
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,32}', name):
                raise ValueError('DSH MCP server namespace is invalid')
            config = {'serverName': name, 'transport': 'stdio', 'command': server['command'],
                      'args': server.get('args', []), 'cwd': str(Path(context.root).resolve()),
                      'failOnStartupError': True}
            if name == 'jev_research':
                config['env'] = {'JEV_KEY_FILE': str(Path.home() / '.config/typesafe/key')}
            mcp_rows.append({'id': 'research-mcp-' + name, 'name': '@deepseek-ai/dsh-mcp-client', 'config': config})
        if mcp_rows:
            rows.append({'insert': mcp_rows})
        patch = folder / 'dsh-runtime.patch.json'
        _new(patch, _encode(rows))
        _new(folder / 'dsh-runtime.json', _encode({'schema_version': 'research-dsh-runtime/v2',
            'receipt_encoding': RECEIPT_ENCODING,
            'harness': self.harness_id, 'producer': self.producer, 'model': model, 'effort': effort,
            'subagent_model': subagent_model, 'subagent_effort': effort,
            **({'aktools_runtime': profile['tools']['aktools'], 'aktools_lock_sha256': aktools_runtime[1]}
               if aktools_runtime else {}),
            **({'data_health_version': DATA_HEALTH_VERSION,
                'data_health_sha256': hashlib.sha256(health_source).hexdigest()} if health_source else {}),
            **({'evidence_recovery_version': EVIDENCE_RECOVERY_VERSION,
                'evidence_recovery_sources': {name: hashlib.sha256(raw).hexdigest()
                    for name, raw in recovery_sources.items()}} if recovery_sources else {}),
            **({'evidence_context_version': EVIDENCE_CONTEXT_VERSION,
                'evidence_context_sha256': hashlib.sha256(context_source).hexdigest(),
                'evidence_context_config': evidence_context, 'evidence_context_node': context_node}
               if context_source else {}),
            'pdf_fallback_python': pdf_python,
            'pdf_fallback_python_realpath': str(Path(pdf_python).resolve()),
            'max_tokens': MAX_TOKENS, 'stream_idle_ms': STREAM_IDLE_MS,
            'sandbox': 'workspace-write', 'approval': 'never', 'auto_review': False,
            'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(),
            'data_environment_sha256': hashlib.sha256(DATA_ENV_BRIDGE.encode()).hexdigest()}))
        return [cli, '--profile', 'headless', '--patch', str(patch), '--json', '-']

    def instruction_from_command(self, args):
        try:
            patch = Path(args[args.index('--patch') + 1])
            return (patch.parent / 'dsh-delivery-instruction.txt').read_text()
        except (ValueError, IndexError, OSError):
            raise ValueError('DSH command missing its frozen delivery instruction') from None

    def receipt(self, folder, strict_json, write_new, encode):
        folder = Path(folder)
        metadata = strict_json(_regular_bytes(folder / 'dsh-runtime.json'), 'DSH runtime binding')
        version = metadata.get('schema_version')
        if version == 'research-dsh-runtime/v1':
            if 'receipt_encoding' in metadata:
                raise ValueError('DSH legacy runtime cannot override receipt encoding')
        elif version != 'research-dsh-runtime/v2' or metadata.get('receipt_encoding') != RECEIPT_ENCODING:
            raise ValueError('DSH runtime has unsupported receipt encoding/version')
        if 'data_health_version' in metadata or 'data_health_sha256' in metadata:
            if (version != 'research-dsh-runtime/v2' or metadata.get('data_health_version') != DATA_HEALTH_VERSION
                    or hashlib.sha256(_regular_bytes(folder / 'dsh-data-health.mjs')).hexdigest()
                    != metadata.get('data_health_sha256')):
                raise ValueError('DSH data health runtime changed or is unsupported')
        if 'evidence_recovery_version' in metadata or 'evidence_recovery_sources' in metadata:
            sources = metadata.get('evidence_recovery_sources')
            if (version != 'research-dsh-runtime/v2'
                    or metadata.get('evidence_recovery_version') != EVIDENCE_RECOVERY_VERSION
                    or metadata.get('data_health_version') != DATA_HEALTH_VERSION
                    or not isinstance(sources, dict)
                    or set(sources) != {'dsh-evidence-recovery.mjs', 'dsh-document-recovery.py'}
                    or any(hashlib.sha256(_regular_bytes(folder / name)).hexdigest() != expected
                           for name, expected in sources.items())):
                raise ValueError('DSH evidence recovery runtime changed or is unsupported')
        if 'evidence_context_version' in metadata or 'evidence_context_sha256' in metadata:
            self._validate_evidence_context(folder, metadata)
        for name, field in (('dsh-runtime.patch.json', 'patch_sha256'),
                            ('dsh-data-environment.mjs', 'data_environment_sha256')):
            raw = _regular_bytes(folder / name)
            if hashlib.sha256(raw).hexdigest() != metadata.get(field):
                raise ValueError('DSH prepared runtime changed during research')
        final, _ = _events(folder, strict_json)
        if version == 'research-dsh-runtime/v2':
            # One whole transport envelope only. The payload still goes through
            # the same strict JSON parser and every shared acceptance gate.
            wrapped = re.fullmatch(r'```json\r?\n([\s\S]*)\r?\n```', final.strip(' \t\r\n'))
            if wrapped is not None:
                final = wrapped[1]
        receipt = strict_json(final.encode(), 'DSH final research receipt')
        if not isinstance(receipt, dict):
            raise ValueError('DSH final research receipt must be an object')
        write_new(folder / 'cli-receipt.json', encode(receipt))
        return receipt

    def _validate_evidence_context(self, folder, metadata):
        config = metadata.get('evidence_context_config')
        dates = json.loads(_regular_bytes(Path(folder) / 'receipt-schema.json')).get('properties', {}).get('valuation_date', {}).get('enum')
        if (metadata.get('evidence_context_version') != EVIDENCE_CONTEXT_VERSION
                or metadata.get('evidence_recovery_version') != EVIDENCE_RECOVERY_VERSION
                or hashlib.sha256(_regular_bytes(Path(folder) / 'dsh-evidence-context.mjs')).hexdigest()
                    != metadata.get('evidence_context_sha256')
                or not isinstance(config, dict) or set(config) != {'directory', 'recoveryDirectory', 'asOf'}
                or config['directory'] != str(Path(folder).resolve() / 'evidence-context')
                or config['recoveryDirectory'] != str(Path(folder).resolve() / 'evidence-recovery')
                or dates != [config['asOf']]
                or not isinstance(metadata.get('evidence_context_node'), str)
                or not Path(metadata['evidence_context_node']).is_absolute()):
            raise ValueError('DSH evidence context runtime changed or is unsupported')

    def evidence_citation_audit(self, folder, report_raw):
        """Check only opted-in frozen evidence references against the final report."""
        folder = Path(folder).resolve()
        metadata = json.loads(_regular_bytes(folder / 'dsh-runtime.json'))
        self._validate_evidence_context(folder, metadata)
        request = dict(config=metadata['evidence_context_config'], report=report_raw.decode('utf-8'))
        try:
            result = subprocess.run([metadata['evidence_context_node'], str(folder / 'dsh-evidence-context.mjs'), '--check-citations'],
                input=json.dumps(request, ensure_ascii=False), text=True, capture_output=True, timeout=45,
                env={key: value for key, value in os.environ.items() if key in ('PATH', 'LANG', 'LC_ALL', 'TMPDIR', 'SYSTEMROOT')})
            if result.returncode or len(result.stdout) > 2 * 1024 * 1024:
                raise ValueError()
            audit = json.loads(result.stdout)
            if (not isinstance(audit, dict) or audit.get('schema_version') != 'research-evidence-citations/v1'
                    or audit.get('report_sha256') != hashlib.sha256(report_raw).hexdigest()
                    or audit.get('status') not in ('failed', 'mechanical_pass', 'not_exercised')
                    or not isinstance(audit.get('issues'), list)
                    or any(not isinstance(x, dict) or not isinstance(x.get('code'), str) for x in audit['issues'])
                    or bool(audit['issues']) != (audit['status'] == 'failed')):
                raise ValueError()
            return audit
        except (OSError, ValueError, subprocess.TimeoutExpired):
            raise ValueError('DSH evidence citation audit unavailable or evidence changed') from None

    def observed_model(self, folder, strict_json):
        """Only use the main persisted runtime header, never the chosen profile."""
        folder = Path(folder)
        try:
            session = None
            cwd = None
            for raw in _regular_lines(folder / 'events.jsonl'):
                event = strict_json(raw, 'DSH observed event')
                if isinstance(event, dict) and event.get('type') == 'session':
                    session = event.get('sessionId')
                    cwd = event.get('cwd')
                    break
            if not isinstance(session, str) or not re.fullmatch(r'session-[A-Za-z0-9-]+', session):
                return None
            # The native v4 store namespaces sessions by encoded workspace.
            root = folder / 'dsh-sessions'
            paths = [root / session / 'session.v4.jsonl',
                     *root.glob('*/' + session + '/session.v4.jsonl')]
            paths = [path for path in paths if path.exists()]
            if len(paths) != 1:
                return None
            path = paths[0]
            if any(parent.is_symlink() for parent in (path, *path.parents)
                   if parent == root or root in parent.parents):
                return None
            first = True
            for raw in _regular_lines(path):
                event = strict_json(raw, 'DSH persisted runtime event')
                if first:
                    first = False
                    if (not isinstance(event, dict) or event.get('type') != 'session'
                            or event.get('id') != session or event.get('cwd') != cwd):
                        return None
                if isinstance(event, dict) and event.get('type') == 'request/header':
                    config = event.get('data', {}).get('header', {}).get('config', {})
                    model = config.get('model')
                    return model if isinstance(model, str) and model.strip() else None
        except (OSError, ValueError, TypeError, AttributeError, UnicodeError):
            return None
        return None
