import test from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {apply, documentWorker} from '../scripts/research_evidence_recovery.mjs';
import {apply as healthApply} from '../scripts/research_data_health.mjs';

const AK = 'mcp__aktools__get_data';
const python = process.env.RECOVERY_TEST_PYTHON ?? 'python3';
const workerFixture = `import sys,json,pathlib,hashlib,time,os
r=json.load(sys.stdin);p=pathlib.Path(r['directory'])
if 'slow' in r.get('url',''): time.sleep(60)
if 'fail' in r.get('url',''): print(json.dumps(dict(ok=False,error='http_status_403')));sys.exit(1)
def save(name,raw):
 (p/name).write_bytes(raw);return dict(file=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
body='' if 'blank' in r['url'] else 'Revenue 1234\\nRestricted cash -50\\n'+'evidence '*1000
raw=save('source.txt',body.encode());part=dict(index=1,chars=len(body),lines=len(body.splitlines()),**save('document.txt',body.encode()))
d=dict(schema_version='research-document-recovery/v1',kind='pdf' if '.pdf' in r['url'] else 'html',transport_complete=True,text_available=bool(body),semantic_verification='pending',raw=raw,parts=[part],warnings=[] if body else ['pages_without_text_require_visual_review'],requested_url=r['url'],final_url=r['url'])
save('document.json',(json.dumps(d,ensure_ascii=False,indent=2)+'\\n').encode())
print(json.dumps(dict(ok=True,result=d)))
`;

async function setup(t, native = false) {
  const directory = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'evidence-recovery-')));
  t.after(() => fs.rm(directory, {recursive: true, force: true}));
  const store = path.join(directory, 'evidence-recovery'); await fs.mkdir(store);
  const worker = path.join(directory, 'worker.py'); await fs.writeFile(worker, workerFixture);
  // Resolve only a test interpreter; production always freezes an absolute path.
  const {spawnSync} = await import('node:child_process');
  const py = spawnSync(python, ['-c', 'import sys;print(sys.executable)'], {encoding: 'utf8'}).stdout.trim();
  const config = {directory: store, worker, python: py, asOf: '2026-11-08',
    healthModule: path.resolve('scripts/research_data_health.mjs')};
  let ctx, call;
  if (native) {
    const root = path.resolve(process.env.DSH_PACKAGE_ROOT);
    const load = pkg => import(pathToFileURL(path.join(root, 'node_modules/@deepseek-ai', pkg, 'lib/index.js')).href);
    const [{Context}, {SystemPrompt}, {ToolRuntime}] = await Promise.all([load('cordis'), load('dsh-system-prompt'), load('dsh-tools')]);
    ctx = new Context();
    const prompt = await ctx.plugin(SystemPrompt, {}).await();
    const tools = await ctx.plugin(ToolRuntime, {}).await();
    const healthDir = path.join(directory, 'data-health'); await fs.mkdir(healthDir);
    const health = await ctx.plugin({name: 'health-test', inject: ['tools'], apply: healthApply}, {directory: healthDir, asOf: config.asOf}).await();
    const recovery = await ctx.plugin({name: 'recovery-test', inject: ['tools'], apply}, config).await();
    t.after(async () => { await recovery.dispose(); await health.dispose(); await tools.dispose(); await prompt.dispose(); });
    call = (name, args, extra = {}) => ctx.tools.execute({name, arguments: args, callId: `test-${Math.random()}`, signal: new AbortController().signal, ...extra});
  } else {
    const hooks = {}, definitions = new Map();
    ctx = {on: (event, fn) => { hooks[event] = fn; }, tools: {
      register: def => { definitions.set(def.name, def); },
      execute: async input => {
        const exec = {token: Symbol(), deferContext: () => {}, ...input};
        let result;
        try {
          const def = definitions.get(exec.name); if (!def) throw new Error('unknown tool');
          const value = await hooks['tools/execute'](exec, () => def.execute(exec.arguments, exec));
          result = {isError: false, value, content: def.output.render(exec.arguments, value)};
        } catch (e) { result = {isError: true, content: [{type: 'text', text: e.message}]}; }
        const decision = await hooks['tools/post-execute'](exec, result, async () => ({kind: 'accept'}));
        return decision.kind === 'accept' ? {...result, ...decision, kind: undefined} : {isError: true, content: decision.feedback};
      }}};
    await apply(ctx, config);
    call = (name, args, extra = {}) => ctx.tools.execute({name, arguments: args, callId: `test-${Math.random()}`, signal: new AbortController().signal, ...extra});
  }
  const register = (name, fn) => ctx.tools.register({name, description: 'offline fixture', parameters: {type: 'object', additionalProperties: true},
    output: {schema: {}, render: () => [{type: 'text', text: 'original presentation'}]}, execute: fn});
  const states = async () => {
    const out = [];
    for (const id of await fs.readdir(store)) {
      const files = (await fs.readdir(path.join(store, id))).filter(x => /^event-\d+\.json$/.test(x)).sort();
      if (files.length) out.push(JSON.parse(await fs.readFile(path.join(store, id, files.at(-1)))));
    }
    return out;
  };
  return {directory, store, config, ctx, call, register, states};
}

const web = () => ({statusCode: 200, body: {kind: 'html', content: '<script>' + 'x'.repeat(10000)}, truncated: true});
function provider(total, calls, change = x => x) {
  return async args => {
    calls.push(args);
    const count = Math.min(args.max_rows ?? 100, total - (args.offset ?? 0));
    const data = change({name: args.name, offset: args.offset ?? 0, total_rows: total, returned_rows: count,
      columns: ['id', 'amount'], rows: Array.from({length: count}, (_, i) => ({id: (args.offset ?? 0) + i, amount: -i})), truncated: true});
    // Values at overlapping positions must be identical in the stable fixture.
    data.rows.forEach(r => { r.amount = r.id === 0 ? 0 : -r.id; });
    return {structuredContent: {result: data}, content: [{type: 'text', text: JSON.stringify(data)}]};
  };
}
const args = {name: 'example_financial_table', params: {symbol: 'SH600000'}, offset: 0, max_rows: 1000};

test('truncated web is recovered once; raw native value, reading and declared use remain distinct', async t => {
  const s = await setup(t), original = web();
  s.register('web_fetch', async () => original);
  const result = await s.call('web_fetch', {url: 'https://example.org/report'});
  assert.deepEqual(result.value, original);
  let [state] = await s.states();
  assert.equal(state.retrieval_status, 'retrieved'); assert.equal(state.attempts, 1);
  assert.equal(state.reads.length, 0); assert.equal(state.reviews.length, 0);
  const repeat = await s.call('research_recover_evidence', {gap_id: state.gap_id});
  assert.equal(repeat.value.attempts, 1);
  const located = await s.call('research_read_evidence', {gap_id: state.gap_id, query: 'Restricted'});
  assert.equal(located.value.matches[0].part, 1);
  const read = await s.call('research_read_evidence', {gap_id: state.gap_id, offset: 0, limit: 100});
  assert.match(read.value.content, /Restricted cash -50/);
  assert.ok(read.value.receipt.locator.next_offset);
  const invalid = await s.call('research_record_evidence_use', {gap_id: state.gap_id, receipt_id: 'invented', disposition: 'used_for_scope'});
  assert.equal(invalid.isError, true);
  const used = await s.call('research_record_evidence_use', {gap_id: state.gap_id, receipt_id: read.value.receipt.receipt_id,
    disposition: 'used_partial', affected_input: 'restricted cash', scope: 'this excerpt only', reason: 'currency still needs original note', report_section: 'cash bridge'});
  assert.equal(used.value.assessment.final_citation_verified, false);
  [state] = await s.states(); assert.equal(state.reads.length, 1); assert.equal(state.reviews.length, 1);
  assert.equal(state.fact_verification, 'not_performed');
  const {spawnSync} = await import('node:child_process');
  const effects = spawnSync(python, ['-c', 'import json,sys;from scripts.research_dsh_metrics import recovery_metrics;print(json.dumps(recovery_metrics(sys.argv[1])))', s.directory], {encoding: 'utf8'});
  assert.equal(effects.status, 0, effects.stderr);
  const measured = JSON.parse(effects.stdout);
  assert.equal(measured.cases, 1); assert.equal(measured.artifacts_checked_cases, 1);
  assert.equal(measured.cases_read, 1); assert.equal(measured.cases_with_declared_use, 1);
  assert.equal(measured.final_citations_verified, null);
  assert.ok(!effects.stdout.includes('Restricted cash'));
});

test('failed PDF fetch triggers recovery but retains the original error; direct PDFs use same deduplication', async t => {
  const s = await setup(t);
  s.register('web_fetch', async () => { throw new Error('Unsupported content type application/pdf'); });
  const result = await s.call('web_fetch', {url: 'https://example.org/report.pdf'}, {parent: Symbol('ptc')});
  assert.equal(result.isError, true);
  assert.ok(result.content.some(x => x.text.includes('Unsupported content')));
  assert.ok(result.additionalContexts.length);
  const direct = await s.call('research_recover_evidence', {url: 'https://example.org/report.pdf'});
  assert.equal(direct.value.attempts, 1); assert.equal(direct.value.document_kind, 'pdf');
});

test('blank/scanned PDF stays partial and cannot supply a fabricated reading receipt', async t => {
  const s = await setup(t);
  const recovered = await s.call('research_recover_evidence', {url: 'https://example.org/blank.pdf'});
  assert.equal(recovered.value.retrieval_status, 'partial');
  const read = await s.call('research_read_evidence', {gap_id: recovered.value.gap_id});
  assert.equal(read.isError, true);
  assert.equal((await s.states())[0].reads.length, 0);
});

test('partial table fills missing initial and tail ranges; truncated=true is not a retry condition', async t => {
  const s = await setup(t), calls = [];
  s.register(AK, provider(2061, calls));
  const first = await s.call(AK, {...args, offset: 1000});
  assert.equal(first.value.structuredContent.result.offset, 1000);
  const [state] = await s.states();
  assert.equal(state.coverage, 'complete_observed'); assert.equal(state.retrieval_status, 'retrieved');
  assert.deepEqual(calls.map(x => x.offset), [1000, 0, 2000]);
  const read = await s.call('research_read_evidence', {gap_id: state.gap_id, offset: 2059, limit: 2});
  assert.deepEqual(read.value.receipt.locator.offsets, [2059, 2060]);
  await s.call('research_recover_evidence', {gap_id: state.gap_id}); assert.equal(calls.length, 3);
});

test('pagination budgets leave explicit gaps and do not loop forever', async t => {
  const s = await setup(t), calls = [];
  s.register(AK, provider(10000, calls));
  await s.call(AK, {...args, max_rows: 100});
  let [state] = await s.states(); assert.equal(calls.length, 4); assert.equal(state.retrieval_status, 'partial');
  for (let i = 0; i < 3; i++) await s.call('research_recover_evidence', {gap_id: state.gap_id});
  [state] = await s.states(); assert.equal(calls.length, 10); assert.equal(state.attempts, 3);
  assert.equal(state.remaining_issue, 'recovery_budget_exhausted'); assert.notEqual(state.coverage, 'complete_observed');
});

test('changed totals stop supplementation and are never marked complete', async t => {
  const s = await setup(t), calls = [];
  s.register(AK, provider(2061, calls, data => ({...data, total_rows: calls.length > 1 ? 2062 : 2061})));
  await s.call(AK, args);
  const [state] = await s.states(); assert.equal(calls.length, 2); assert.equal(state.retrieval_status, 'conflict');
  assert.equal((await s.call('research_read_evidence', {gap_id: state.gap_id})).isError, true);
});

test('an upstream pagination failure preserves readable earlier evidence and remains unresolved', async t => {
  const s = await setup(t), calls = [];
  const fn = provider(2061, calls);
  s.register(AK, async a => { if (a.offset > 0) throw new Error('source unavailable'); return fn(a); });
  await s.call(AK, args);
  const [state] = await s.states(); assert.equal(state.retrieval_status, 'partial');
  assert.equal(state.remaining_issue, 'page_request_failed');
  assert.equal((await s.call('research_read_evidence', {gap_id: state.gap_id, limit: 1})).isError, false);
});

test('concurrent same-source observations share a single recovery and keep both native responses', async t => {
  const s = await setup(t); s.register('web_fetch', async () => web());
  const responses = await Promise.all([s.call('web_fetch', {url: 'https://example.org/report'}), s.call('web_fetch', {url: 'https://example.org/report'})]);
  assert.ok(responses.every(x => x.value.truncated));
  const [state] = await s.states(); assert.equal(state.attempts, 1); assert.equal(state.observations, 2);
  assert.ok(state.deduplicated_requests >= 1);
});

test('blocked documents are recorded once; cancellation kills the worker and records incomplete recovery', async t => {
  const s = await setup(t);
  const failed = await s.call('research_recover_evidence', {url: 'https://example.org/fail.pdf'});
  assert.equal(failed.value.retrieval_status, 'failed');
  const repeat = await s.call('research_recover_evidence', {gap_id: failed.value.gap_id}); assert.equal(repeat.value.attempts, 1);
  const controller = new AbortController();
  const pending = s.call('research_recover_evidence', {url: 'https://example.org/slow.pdf'}, {signal: controller.signal});
  setTimeout(() => controller.abort(), 200);
  const cancelled = await pending; assert.equal(cancelled.value.retrieval_status, 'cancelled');
  assert.equal((await s.states()).find(x => x.request.url.includes('slow')).remaining_issue, 'cancelled');
});

test('source tampering and path traversal cannot masquerade as evidence reads', async t => {
  const s = await setup(t);
  assert.equal((await s.call('research_read_evidence', {gap_id: '../outside'})).isError, true);
  const r = await s.call('research_recover_evidence', {url: 'https://example.org/report'});
  const [state] = await s.states();
  await fs.writeFile(path.join(s.store, state.gap_id, state.document_directory, state.document.parts[0].file), 'tampered');
  assert.equal((await s.call('research_read_evidence', {gap_id: r.value.gap_id})).isError, true);
});

test('changed raw PDF prevents text reads and searches even if extracted text is intact', async t => {
  const s = await setup(t);
  const recovered = await s.call('research_recover_evidence', {url: 'https://example.org/report.pdf'});
  const [state] = await s.states();
  await fs.appendFile(path.join(s.store, state.gap_id, state.document_directory, state.document.raw.file), 'changed');
  assert.equal((await s.call('research_read_evidence', {gap_id: recovered.value.gap_id})).isError, true);
  assert.equal((await s.call('research_read_evidence', {gap_id: recovered.value.gap_id, query: 'Revenue'})).isError, true);
  assert.equal((await s.states())[0].reads.length, 0);
});

test('document worker preserves multibyte metadata across stdout chunks', async t => {
  const s = await setup(t);
  await fs.writeFile(s.config.worker, `import sys,json,time\nraw=json.dumps(dict(ok=True,result=dict(title='中文财报')),ensure_ascii=False).encode()\npos=raw.index('中'.encode())+1\nsys.stdout.buffer.write(raw[:pos]);sys.stdout.buffer.flush();time.sleep(0.15)\nsys.stdout.buffer.write(raw[pos:]);sys.stdout.buffer.flush()\n`);
  const result = await documentWorker(s.config, {directory: s.directory}, new AbortController().signal);
  assert.equal(result.title, '中文财报');
});

test('installed ToolRuntime composes health, recovery, nested policy and PTC context without replacing source',
  {skip: !process.env.DSH_PACKAGE_ROOT}, async t => {
    const s = await setup(t, true), calls = [];
    s.register(AK, provider(2061, calls));
    const result = await s.call(AK, args, {parent: Symbol('ptc')});
    assert.equal(result.isError, false, JSON.stringify(result));
    assert.equal(result.value.structuredContent.result.returned_rows, 1000);
    assert.equal((await s.states())[0].retrieval_status, 'retrieved');
    assert.ok(result.additionalContexts.some(x => x.content.some(c => c.text?.includes('recovery'))));
    // Native pre-policy denial must block the recovery tool's underlying fetch.
    s.ctx.on('tools/pre-execute', async (exec, next) => exec.name === AK && exec.arguments.offset > 0
      ? {kind: 'deny', reason: 'fixture policy'} : next());
    await s.call(AK, {...args, params: {symbol: 'other'}});
    const blocked = (await s.states()).find(x => x.request.params.symbol === 'other');
    assert.equal(blocked.retrieval_status, 'partial'); assert.equal(blocked.remaining_issue, 'page_request_failed');
    s.register('web_fetch', async () => { throw new Error('PDF unsupported'); });
    s.ctx.on('tools/pre-execute', async (exec, next) => exec.name === 'web_fetch'
      ? {kind: 'deny', reason: 'fixture denies this PDF source'} : next());
    const denied = await s.call('web_fetch', {url: 'https://example.org/denied.pdf'});
    assert.equal(denied.isError, true);
    assert.equal((await s.states()).filter(x => x.category === 'document').length, 0);
  });
