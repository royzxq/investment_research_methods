"""Audited, conditional Jev routing for public disclosure candidates.

Only ranking/location: all candidates survive. Original text goes from this
program to the installed Jev MCP, never through the host model's tool arguments.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

SCHEMA = 'research-jev/v1'
MANIFEST_SCHEMA = 'research-jev-candidates/v1'
POLICY = {'version': 1, 'announcement_min_candidates': 8, 'annual_min_candidates': 6,
          'min_characters': 12000, 'max_items': 50, 'max_batch_characters': 500000,
          'backend_timeout_seconds': 40}
MODES = ('auto', 'off', 'force')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def parse(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('nonfinite JSON number')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def new(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.jev-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.link(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def contained(root, path):
    path = Path(path)
    target = (path if path.is_absolute() else root / path).resolve()
    require(target.is_relative_to(root), 'path outside the research root')
    return target


def backend_command():
    """Resolve argv only. Do not copy config env or read credential contents."""
    override = os.environ.get('RESEARCH_JEV_COMMAND')
    if override:
        argv = parse(override)
        require(isinstance(argv, list) and argv and all(isinstance(x, str) and x for x in argv),
                'RESEARCH_JEV_COMMAND must be a JSON argv array')
        require(not any(x.lower().startswith(('--api-key','--token','bearer ')) for x in argv),
                'credentials must not be passed in backend argv')
        return argv
    try:
        import tomllib
        cfg = tomllib.loads((Path.home()/'.codex/config.toml').read_text())
        server = cfg.get('mcp_servers', {}).get('jev', {})
        argv = [server['command'], *server.get('args', [])]
        if all(isinstance(x, str) and x for x in argv):
            return argv
    except (ImportError, OSError, ValueError, KeyError, TypeError):
        pass
    script = Path.home()/'.local/share/jev-mcp/node_modules/jev-mcp/dist/index.js'
    node = shutil.which('node')
    return [node, str(script)] if node and script.is_file() else None


def prepare(folder, root, *, task_id, day, generator, mode=None):
    root, folder = Path(root).resolve(), Path(folder).resolve()
    require(folder.is_relative_to(root/'output'), 'Jev execution must be under output/')
    mode = os.environ.get('RESEARCH_JEV_MODE', 'auto') if mode is None else mode
    require(mode in MODES, 'Jev mode must be auto/off/force')
    directory = folder/'jev'
    materials = directory/'materials'
    materials.mkdir(parents=True, exist_ok=False)
    config = {'schema_version': SCHEMA, 'root': str(root), 'execution_dir': str(folder),
              'materials_dir': str(materials), 'mode': mode, 'policy': POLICY,
              'backend_command': backend_command(), 'task_id': task_id, 'generator': generator,
              'valuation_date': day, 'model_override': os.environ.get('JEV_MODEL'),
              'max_response_bytes': 9000}
    raw = (encode(config)+'\n').encode()
    new(directory/'config.json', raw)
    service = Service(config)
    service.log('registered', mode=mode, backend_available=bool(config['backend_command']))
    return {'jev_config_sha256': sha(raw), 'jev_mode': mode}


def registration(folder):
    path = Path(folder).resolve()/'jev/config.json'
    if not path.exists() or parse(path.read_bytes())['mode'] == 'off':
        return {}
    return {'jev_research': {'command': sys.executable,
            'args': [str(Path(__file__).resolve()), 'serve', '--config', str(path)]}}


def instructions(folder):
    path = Path(folder).resolve()/'jev/config.json'
    cfg = parse(path.read_bytes())
    if cfg['mode'] == 'off':
        return '\n本次 Jev=off；仅普通程序定位和当前宿主主模型核验。未调用原因会记录。\n'
    return (f'\n<jev_research_route>\nJev模式={cfg["mode"]}；材料目录：{cfg["materials_dir"]}。'
            '每次批量公告分流或年报候选章节定位，先用普通程序将公开原文存到此目录，建立候选manifest，'
            '然后调用 research_jev_route(manifest_path)。程序判定是否触发，不由主模型口头决定跳过。'
            f'manifest格式：schema_version="{MANIFEST_SCHEMA}", purpose="announcements"或"annual_sections", '
            'query=本轮待定位主题, selection_complete=已确定全部必要范围时true（否则false）, '
            'candidates=[{id,path,sha256,start,end,public_url,title}]。'
            'start/end是UTF-8解码后从0开始的字符半开区间；public_url标明公开资料出处，不能交账户或凭据材料。'
            'auto阈值为公告至少8候选或年报至少6候选，且原文合计至少12000字符；这是待校准的开销参数，不是投资规则。'
            '小批量、selection_complete精确位置等也走route记录未调用原因。一次最多50候选，超限明确回退或拆成完整批次，不静默丢弃。'
            '程序直接转交原文给Jev，主模型不转抄全文；结果只作排序定位，所有候选和不确定/失败项保留。'
            'query只问相关性；事实、金额、主体、现金、Gate和估值仍由当前宿主主模型查原文核验。'
            '结果有next_offset时继续翻页；不把负面相关性判断当证据不存在。'
            '调用记录在本次jev/calls.jsonl，状态在jev/summary.json。'
            f'MCP不可用时：{sys.executable} scripts/research_jev.py route --config {path} --manifest <文件>。'
            '未提交候选会标为not_requested，不能声称程序已判断无需Jev。\n</jev_research_route>\n')


class Backend:
    """Private stdio MCP child; installed server owns credential loading."""
    def __init__(self, argv, timeout=40, *, required_tool='jev_triage'):
        require(argv, 'Jev backend is unavailable')
        self.timeout, self.seq = timeout, 0
        env = dict(os.environ, JEV_FILE_ROOTS='off')
        self.proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, env=env, bufsize=0)
        os.set_blocking(self.proc.stdin.fileno(), False)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ)
        self.buffer = b''
        try:
            self.request('initialize', {'protocolVersion':'2024-11-05', 'capabilities':{},
                         'clientInfo':{'name':'research-jev-router','version':'1'}})
            self.send({'jsonrpc':'2.0','method':'notifications/initialized'})
            listed = self.request('tools/list', {})
            require(required_tool in {t['name'] for t in listed.get('tools', [])}, 'requested MCP tool is not advertised')
        except BaseException:
            self.close(); raise

    def send(self, value, deadline=None):
        data=memoryview((encode(value)+'\n').encode())
        deadline=deadline or time.monotonic()+self.timeout
        with selectors.DefaultSelector() as selector:
            selector.register(self.proc.stdin,selectors.EVENT_WRITE)
            while data:
                remaining=deadline-time.monotonic()
                if remaining <= 0 or not selector.select(remaining):
                    raise TimeoutError('Jev backend write timeout')
                try:
                    count=os.write(self.proc.stdin.fileno(),data)
                except BlockingIOError:
                    continue
                require(count > 0, 'Jev backend closed its input')
                data=data[count:]

    def request(self, method, params):
        self.seq += 1; id_ = self.seq
        deadline = time.monotonic()+self.timeout
        self.send({'jsonrpc':'2.0', 'id':id_, 'method':method, 'params':params},deadline)
        while True:
            while b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                value = parse(line)
                if value.get('id') == id_:
                    require('error' not in value, 'backend protocol error')
                    return value['result']
            remaining = deadline-time.monotonic()
            if remaining <= 0 or not self.selector.select(remaining):
                raise TimeoutError('Jev backend timeout')
            data = os.read(self.proc.stdout.fileno(), 65536)
            require(data, 'Jev backend closed its output')
            self.buffer += data
            require(len(self.buffer) <= 4000000, 'Jev backend response exceeded transport limit')

    def triage(self, items, query):
        reply = self.request('tools/call', {'name':'jev_triage','arguments':{'items':items,'query':query}})
        value = reply.get('structuredContent')
        if value is None:
            texts = [c['text'] for c in reply.get('content', []) if c.get('type') == 'text']
            require(len(texts) == 1, 'Jev returned no single typed result')
            value = parse(texts[0])
        require(isinstance(value, dict), 'Jev result must be an object')
        return value

    def close(self):
        self.selector.close()
        if self.proc.poll() is None:
            self.proc.terminate()
            try:self.proc.wait(timeout=1)
            except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
        for stream in (self.proc.stdin, self.proc.stdout):
            stream.close()


def safe_error(error):
    if not isinstance(error, dict):
        return {'kind':'unknown', 'retryable':False}
    kind = error.get('kind','unknown')
    if 'No API key' in str(error.get('message','')):
        kind = 'authentication_configuration'
    terminal = {'authentication','authentication_configuration','permission_denied','invalid_request',
                'invalid_arguments','file_access','not_found','cancelled'}
    retryable = error.get('retryable') is True and kind not in terminal
    return {k:v for k,v in {'kind':kind,'status':error.get('status'),
                            'retryable':retryable}.items() if v is not None}


class Service:
    def __init__(self, config, backend_factory=Backend):
        require(config.get('schema_version') == SCHEMA, 'unsupported Jev config')
        self.config = config
        self.root = Path(config['root']).resolve()
        self.execution = contained(self.root, config['execution_dir'])
        require(self.execution.is_relative_to(self.root/'output'), 'execution outside output/')
        self.directory = self.execution/'jev'
        self.materials = contained(self.root, config['materials_dir'])
        require(self.materials.is_relative_to(self.directory), 'materials outside this execution')
        require(config['mode'] in MODES and config['policy'] == POLICY, 'unsupported mode or policy')
        self.directory.mkdir(parents=True, exist_ok=True)
        self.backend_factory = backend_factory

    @contextmanager
    def lock(self):
        with (self.directory/'route.lock').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX);yield

    def log(self, event, **fields):
        with (self.directory/'calls.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(encode({'schema_version':SCHEMA,'timestamp':datetime.now(timezone.utc).isoformat(),
                                'event':event,**fields})+'\n');stream.flush();os.fsync(stream.fileno())

    def load(self, path):
        path = contained(self.root, path)
        require(path.is_relative_to(self.execution), 'manifest must be inside this execution')
        raw = path.read_bytes()
        require(len(raw) <= 1000000, 'candidate manifest too large')
        manifest = parse(raw)
        require(manifest.get('schema_version') == MANIFEST_SCHEMA, 'unsupported candidate manifest')
        require(manifest.get('purpose') in ('announcements','annual_sections'), 'ranking purpose must be discovery/location')
        query = manifest.get('query')
        require(isinstance(query,str) and 0 < len(query) <= 2000, 'query must be 1..2000 characters')
        rows = manifest.get('candidates')
        require(type(manifest.get('selection_complete', False)) is bool, 'selection_complete must be boolean')
        require(isinstance(rows,list) and len(rows) <= 1000, 'candidates must be an array of at most 1000 entries')
        items, positions, ids, total = [], [], set(), 0
        for row in rows:
            id_ = row.get('id')
            require(isinstance(id_,str) and 0 < len(id_) <= 100 and id_ not in ids, 'candidate IDs must be unique')
            ids.add(id_)
            source = contained(self.root,row['path'])
            require(source.is_relative_to(self.materials), 'candidate source outside authorised materials')
            require(source.suffix.lower() in ('.txt','.md'), 'only extracted public text is accepted')
            require(not any(x in source.name.lower() for x in ('credential','secret','token','config','password','key.')),
                    'credential/configuration files cannot be submitted')
            url = row.get('public_url')
            require(isinstance(url,str) and url.startswith(('https://','http://')) and len(url) <= 2000,
                    'candidate needs a public source URL')
            body = source.read_bytes()
            require(sha(body) == row['sha256'], 'candidate source hash changed')
            text = body.decode('utf-8')
            a,b = row['start'],row['end']
            require(type(a) is int and type(b) is int and 0 <= a < b <= len(text), 'invalid candidate character range')
            selected = text[a:b];total += len(selected)
            require(total <= 4000000, 'candidate corpus exceeds local reading limit')
            items.append({'id':id_,'text':selected})
            positions.append({'id':id_,'path':str(source),'sha256':row['sha256'],'start':a,'end':b})
        key = sha(encode({'purpose':manifest['purpose'],'query':query,
                          'selection_complete':manifest.get('selection_complete',False),
                          'config':self.config,'positions':positions}).encode())
        return manifest,items,positions,total,key

    def decision(self, manifest, n, size):
        mode = self.config['mode']
        if mode == 'off':return False,'disabled'
        if not n:return False,'no_candidates'
        if n > POLICY['max_items'] or size > POLICY['max_batch_characters']:
            return False,'batch_limit_exceeded_split_or_read_originals'
        if any((u['end']-u['start']) > 200000 for u in manifest['candidates']):
            return False,'candidate_too_large_no_truncation'
        if mode == 'force':return True,'explicit_force'
        if manifest.get('selection_complete',False):return False,'declared_precise_location'
        minimum = POLICY['announcement_min_candidates'] if manifest['purpose']=='announcements' else POLICY['annual_min_candidates']
        if n < minimum:return False,'candidate_count_below_threshold'
        if size < POLICY['min_characters']:return False,'candidate_text_below_threshold'
        return True,'large_unresolved_candidate_batch'

    def route(self, path, *, offset=0, limit=20):
        require(type(offset) is int and offset >= 0 and type(limit) is int and 1 <= limit <= 50, 'invalid result pagination')
        with self.lock():
            route_id = uuid.uuid4().hex
            started = time.monotonic()
            submitted = False
            try:
                self.log('route_requested',route_id=route_id,manifest_path=str(path),offset=offset,limit=limit)
                manifest,items,positions,size,key = self.load(path)
                cache = self.directory/('result-'+key+'.json')
                if cache.exists():
                    result = parse(cache.read_bytes())
                    self.log('cache_reused', route_id=route_id, result_path=str(cache), source_key=key, api_submitted=False)
                else:
                    trigger,reason = self.decision(manifest,len(items),size)
                    self.log('decision',route_id=route_id,mode=self.config['mode'],purpose=manifest['purpose'],
                             candidate_count=len(items),candidate_characters=size,triggered=trigger,reason=reason,source_key=key,
                             manifest_path=str(contained(self.root,path)))
                    scores,usage,errors,attempts,models = {},[],{},0,[]
                    if trigger and not self.config['backend_command']:
                        trigger=False;reason='backend_unavailable'
                        self.log('skipped',route_id=route_id,reason=reason,api_submitted=False)
                    if trigger:
                        self.log('call_started',route_id=route_id,requested_items=len(items),tool='jev_triage')
                        backend = None
                        try:
                            backend=self.backend_factory(self.config['backend_command'],POLICY['backend_timeout_seconds'])
                            pending=items
                            for attempt in (1,2):
                                attempts+=1
                                submitted = True
                                self.log('backend_tool_submitted',route_id=route_id,attempt=attempt,
                                         tool='jev_triage',requested_items=len(pending),
                                         candidate_ids=[x['id'] for x in pending],
                                         candidate_characters=sum(len(x['text']) for x in pending))
                                response=backend.triage(pending,manifest['query'])
                                if response.get('model'):models.append(response['model'])
                                if isinstance(response.get('usage'),dict):usage.append(response['usage'])
                                rows=response.get('results')
                                if not isinstance(rows,list):
                                    error=safe_error(response.get('error'))
                                    errors.update({x['id']:error for x in pending})
                                    if attempt==1 and error['retryable']:continue
                                    break
                                require(len(rows)==len(pending) and {r.get('id') for r in rows}=={x['id'] for x in pending},
                                        'Jev result IDs mismatch; retain original candidates')
                                again=[]
                                for row in rows:
                                    id_=row['id']
                                    if 'error' in row:
                                        error=safe_error(row['error']);errors[id_]=error
                                        if attempt==1 and error['retryable']:again.append(next(x for x in pending if x['id']==id_))
                                    else:
                                        answer=row.get('answers',{}).get('relevant',{})
                                        value=answer.get('noul')
                                        require(type(value) in (int,float) and math.isfinite(value) and 0 <= value <= 1,
                                                'Jev relevance probability malformed')
                                        scores[id_]={'score':value,'verdict':answer.get('verdict','uncertain')}
                                        errors.pop(id_,None)
                                if not again:break
                                pending=again
                        except Exception as exc:
                            kind='timeout' if isinstance(exc,TimeoutError) else 'backend_failure'
                            errors.update({x['id']:{'kind':kind,'retryable':False} for x in items if x['id'] not in scores})
                        finally:
                            if backend is not None:backend.close()
                        status='ranked' if len(scores)==len(items) else 'partial_fallback' if scores else 'fallback'
                        self.log('call_finished',route_id=route_id,status=status,mcp_calls=attempts,
                                 successful_items=len(scores),errors=errors,usage=usage,
                                 backend_tool_submitted=submitted,
                                 usage_scope='successful_items_only; failed_requests_unknown',cost=None,
                                 sdk_internal_retry_count=None,models=models,latency_seconds=time.monotonic()-started)
                    else:
                        status='skipped'
                    ranked=[dict(row,**scores.get(row['id'],{'score':None,'verdict':'unrated'})) for row in positions]
                    ranked.sort(key=lambda row:-(row['score'] if row['score'] is not None else 0.5))
                    result={'schema_version':SCHEMA,'status':status,'mode':self.config['mode'],'reason':reason,
                            'candidate_count':len(items),'candidate_characters':size,'ranked':ranked,'errors':errors,
                            'usage':usage,'usage_scope':'successful_items_only; failed_requests_unknown',
                            'models':models,'mcp_calls':attempts,'cost':None,'no_candidates_dropped':True,
                            'research_complete':False,'evidence_status':'unverified','source_key':key,
                            'fallback_required':bool(errors) or reason in ('backend_unavailable','batch_limit_exceeded_split_or_read_originals','candidate_too_large_no_truncation')}
                    new(cache,(encode(result)+'\n').encode())
                page=self.page(result,cache,offset,limit)
                self.log('tool_response',route_id=route_id,result_path=str(cache),status=result['status'],
                         response_bytes=len(encode(page).encode()),returned_items=len(page['items']),
                         offset=offset,next_offset=page['next_offset'],latency_seconds=time.monotonic()-started)
                return page
            except Exception as exc:
                self.log('route_failed',route_id=route_id,kind='validation_or_io_failure',backend_tool_submitted=submitted,
                         latency_seconds=time.monotonic()-started)
                raise ValueError('Jev route failed input validation; read original materials and inspect local record') from exc

    def page(self, result, path, offset, limit):
        require(offset <= len(result['ranked']), 'offset past result end')
        summary={k:result[k] for k in ('status','mode','reason','candidate_count','fallback_required','no_candidates_dropped',
                                     'research_complete','evidence_status','models')}
        summary.update(result_path=str(path),offset=offset,items=result['ranked'][offset:offset+limit],
                       error_ids=list(result['errors']),
                       error_kinds=sorted({row.get('kind','unknown') for row in result['errors'].values()}),next_offset=None)
        budget=self.config.get('max_response_bytes',9000)
        while len(encode(summary).encode())+600 > budget and summary['items']:
            summary['items'].pop()
        if offset < len(result['ranked']):require(summary['items'],'one result row exceeds response budget')
        next_=offset+len(summary['items'])
        summary['next_offset']=next_ if next_<len(result['ranked']) else None
        return summary


def summarize(folder, *, persist=True):
    directory=Path(folder)/'jev'
    if not (directory/'config.json').exists():return {'status':'not_registered'}
    config=parse((directory/'config.json').read_bytes())
    events=[parse(line) for line in (directory/'calls.jsonl').read_bytes().splitlines()]
    decisions=[e for e in events if e['event']=='decision']
    finished=[e for e in events if e['event']=='call_finished']
    started=[e for e in events if e['event']=='call_started']
    requested=[e for e in events if e['event']=='route_requested']
    submitted=[e for e in events if e['event']=='backend_tool_submitted']
    failed=[e for e in events if e['event']=='route_failed']
    responses=[e for e in events if e['event']=='tool_response']
    # Starting the local server is not a Jev inference request. Older journals
    # without route_requested remain readable without claiming API activity.
    has_request=bool(requested or decisions or failed)
    tool_calls=len(submitted) if submitted else sum(e.get('mcp_calls',0) for e in finished)
    status=('disabled' if config['mode']=='off' else 'not_requested' if not has_request
            else 'invoked' if tool_calls else 'fallback' if failed or finished else 'skipped')
    result={'schema_version':SCHEMA,'mode':config['mode'],'status':status,
            'reason':'no_candidate_batch_submitted' if status=='not_requested' else 'disabled' if status=='disabled' else None,
            'route_requests':len(requested),'backend_tool_submissions':tool_calls,
            'submitted_candidate_requests':sum(e['requested_items'] for e in submitted) if submitted else None,
            'decisions':len(decisions),'jev_batches_started':len(started),'jev_batches_finished':len(finished),
            'decision_reasons':[e['reason'] for e in events if e['event'] in ('decision','skipped')],
            'unfinished_route_ids':[e['route_id'] for e in started if e['route_id'] not in {f['route_id'] for f in finished}],
            'failed_route_requests':len(failed),
            'fallback_batches':sum(e['status'] in ('fallback','partial_fallback') for e in finished),
            'usage_records':[u for e in finished for u in e['usage']], 'cost':None,
            'tool_response_bytes':sum(e['response_bytes'] for e in responses),
            'tool_response_seconds':sum(e['latency_seconds'] for e in responses),
            'cache_returns':sum(e['event']=='cache_reused' for e in events),
            'usage_scope':'successful_items_only; unreported and failed usage unknown',
            'backend_available':bool(config['backend_command']),'calls_path':str(directory/'calls.jsonl')}
    if persist:new(directory/'summary.json',(encode(result)+'\n').encode())
    return result


def serve(service):
    for line in sys.stdin:
        id_=None
        try:
            request=parse(line);id_=request.get('id');method=request.get('method');params=request.get('params',{})
            if method.startswith('notifications/'):continue
            if method=='initialize':
                result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'jev-research','version':'1'}}
            elif method=='tools/list':
                result={'tools':[{'name':'research_jev_route', 'description':'Route a public candidate manifest through deterministic auto/off/force policy. Program sends original text privately to Jev; ranks all candidates without excluding evidence. Also paginate cached results; off/small/unavailable/error reasons are audited.',
                    'inputSchema':{'type':'object','properties':{'manifest_path':{'type':'string'},'offset':{'type':'integer'},'limit':{'type':'integer'}},'required':['manifest_path'],'additionalProperties':False}}]}
            elif method=='tools/call':
                require(params.get('name')=='research_jev_route','unknown research Jev tool')
                args=params.get('arguments',{});require(not(set(args)-{'manifest_path','offset','limit'}),'unknown tool arguments')
                value=service.route(args['manifest_path'],offset=args.get('offset',0),limit=args.get('limit',20))
                result={'content':[{'type':'text','text':encode(value)}]}
            else:raise ValueError('unsupported MCP method')
            reply={'jsonrpc':'2.0','id':id_,'result':result}
        except Exception:
            reply={'jsonrpc':'2.0','id':id_,'error':{'code':-32000,'message':'Jev route failed; preserve candidates, use ordinary locating, and inspect jev/calls.jsonl'}}
        print(encode(reply),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('serve','route','summary'))
    p.add_argument('--config',required=True);p.add_argument('--manifest');p.add_argument('--offset',type=int,default=0);p.add_argument('--limit',type=int,default=20)
    args=p.parse_args();config=parse(Path(args.config).read_bytes())
    service=Service(config)
    if args.action=='serve':serve(service);return 0
    if args.action=='summary':result=summarize(config['execution_dir'],persist=False)
    else:result=service.route(args.manifest,offset=args.offset,limit=args.limit)
    print(encode(result));return 0


if __name__=='__main__':
    sys.exit(main())
