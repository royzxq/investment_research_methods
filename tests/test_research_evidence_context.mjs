import test from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {spawn, spawnSync} from 'node:child_process';
import {EvidenceStore, apply} from '../scripts/research_evidence_context.mjs';

const digest = x => createHash('sha256').update(x).digest('hex');
const middle = '主体甲，2025年度；人民币万元；受限现金 -1,234.50，不能作为可用净现金；披露日2026-03-31。';
const longText = '前文背景。'.repeat(5000) + middle + '后文背景。'.repeat(3000);
const body = (content = longText, truncated = false) => ({statusCode: 200, body: {kind: 'text', content}, truncated});
const pin = (id, extra = {}) => ({evidence_id: id, label: '受限现金附注', subject: '主体甲', period: '2025年度',
  currency: 'CNY', unit: '万元', disclosed_at: '2026-03-31', stance: 'counterevidence', note: '不可计入可用净现金', ...extra});
async function setup(t) {
  const temp = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'evidence-context-')));
  t.after(() => fs.rm(temp, {recursive: true, force: true}));
  const config = {directory: path.join(temp, 'evidence-context'), recoveryDirectory: path.join(temp, 'evidence-recovery'), asOf: '2026-11-08'};
  await fs.mkdir(config.directory); await fs.mkdir(config.recoveryDirectory);
  return {temp, config, store: await new EvidenceStore(config).init()};
}
async function web(store, content = longText, url = 'https://example.org/report') {
  return store.registerWeb({url}, body(content));
}
async function reading(store) {
  const source = await web(store);
  const located = await store.find({source_id: source.id, query: '受限现金'});
  return store.open({source_id: source.id, ...located.matches[0], limit: 400});
}

test('source search, bounded exact read and IDs survive process/store reload', async t => {
  const s = await setup(t), read = await reading(s.store);
  assert.ok(read.content.includes(middle)); assert.ok(read.content.length <= 400);
  await s.store.pin(pin(read.evidence_id));
  const fresh = await new EvidenceStore(s.config).init();
  assert.equal(fresh.catalog({query: '受限现金'}).entries[0].evidence[0].evidence_id, read.evidence_id);
  assert.deepEqual((await fresh.open({evidence_id: read.evidence_id})).content, read.content);
  assert.match(fresh.context(), /2025年度/); assert.match(fresh.context(), /counterevidence/);
  assert.match(fresh.context(), /万元/); assert.equal(fresh.pins.size, 1);
  assert.equal((await fresh.open({source_id: read.source_id, offset: read.locator.start, limit: read.content.length})).evidence_id, read.evidence_id);
  const measured = spawnSync(process.env.RECOVERY_TEST_PYTHON ?? 'python3', ['-c',
    'import json,sys;from scripts.research_dsh_metrics import context_metrics;print(json.dumps(context_metrics(sys.argv[1])))', s.temp], {encoding: 'utf8'});
  assert.equal(measured.status, 0, measured.stderr);
  const effects = JSON.parse(measured.stdout);
  assert.equal(effects.sources, 1); assert.equal(effects.pins, 1); assert.equal(effects.events.reopened, 1);
  assert.equal(effects.events.pin_source_checked, 1); assert.equal(effects.sources_reverified, false);
  assert.deepEqual(effects.issues, []); assert.ok(!measured.stdout.includes('example.org'));
  assert.ok(!measured.stdout.includes('受限现金'));
});

test('exact citations catch changed amounts, locator, source, missing markers and unknown IDs', async t => {
  const {store} = await setup(t), read = await reading(store);
  await store.pin(pin(read.evidence_id));
  const cite = await store.cite({evidence_id: read.evidence_id, quote: middle});
  const report = '# 研究报告\n\n' + cite.markdown;
  assert.equal((await store.checkCitations(report)).status, 'mechanical_pass');
  for (const changed of [report.replace('-1,234.50', '1,234.50'), report.replace('定位', '错误位置'),
    report.replace('example.org', 'wrong.example'), report.replace(/<!--.*?-->/, ''), report.replace(cite.citation_id, 'c-' + '0'.repeat(64))]) {
    assert.equal((await store.checkCitations(changed)).status, 'failed');
  }
  await assert.rejects(store.cite({evidence_id: read.evidence_id, quote: '受限现金为零'}), /quote_not_in/);
  const empty = await setup(t); assert.equal((await empty.store.checkCitations('无登记证据')).status, 'not_exercised');
});

test('citation audit distinguishes nested list content from code blocks', async t => {
  const {store} = await setup(t), read = await reading(store);
  await store.pin(pin(read.evidence_id));
  const {markdown} = await store.cite({evidence_id: read.evidence_id, quote: middle});
  for (const report of [
    `1. Valuation inputs\n    - ${markdown}`,
    `1. Valuation inputs\n    - Restricted cash\n      ${markdown}`,
    `1. Valuation inputs\n\n    ${markdown}`,
    `1. Valuation inputs\n\t- ${markdown}`,
    `1. Valuation inputs\n\n   \`\`\`md\n   example\n   \`\`\`\n\n   ${markdown}`,
    `1. Valuation inputs\n\n   \`\`\`md\n   example\n\n${markdown}`,
  ]) {
    assert.equal((await store.checkCitations(report)).status, 'mechanical_pass', report);
  }
  for (const report of [
    `    - ${markdown}`,
    `1. Valuation inputs\n\n       - ${markdown}`,
    `1. Valuation inputs\n\n    - Example\n\n          ${markdown}`,
    `1. Valuation inputs\n\n    \`\`\`md\n    ${markdown}\n    \`\`\``,
    `1. Valuation inputs\n    - \`\`\`md\n      ${markdown}\n      \`\`\``,
    `1. Valuation inputs\n\nOut of the list.\n\n    - ${markdown}`,
  ]) {
    const audit = await store.checkCitations(report);
    assert.equal(audit.citation_markers, 0, report);
    assert.deepEqual(audit.issues.map(issue => issue.code), ['required_evidence_not_cited']);
  }
});

test('search continuation crosses dense keyword matches and later document parts without losing hits', async t => {
  const {store} = await setup(t);
  const a = await web(store, 'cash 1\n'.repeat(25));
  const b = await web(store, 'cash 2\n'.repeat(5), 'https://example.org/appendix');
  const source = await store.put('sources', 's', {...a.data, parts: [...a.data.parts, {...b.data.parts[0], part: 2}], bindings: [...a.data.bindings, ...b.data.bindings]});
  let cursor = {}, all = [];
  do {
    const result = await store.find({source_id: source.id, query: 'cash', ...cursor});
    all.push(...result.matches); cursor = result.next_search;
  } while (cursor);
  assert.equal(all.length, 30); assert.equal(all.filter(x => x.part === 2).length, 5);
  assert.equal(new Set(all.map(x => `${x.part}:${x.match_offset}`)).size, 30);
});

test('citation audit preserves UTF-8 characters split between stdin chunks', async t => {
  const {store, config} = await setup(t), read = await reading(store);
  await store.pin(pin(read.evidence_id));
  const citation = await store.cite({evidence_id: read.evidence_id, quote: middle});
  const report = '# 投研报告\n' + '中文长正文。'.repeat(20000) + '\n\n' + citation.markdown;
  const raw = Buffer.from(JSON.stringify({config, report})), split = raw.indexOf(Buffer.from('投')) + 1;
  assert.ok(split > 0);
  const child = spawn(process.execPath, ['scripts/research_evidence_context.mjs', '--check-citations'], {stdio: ['pipe', 'pipe', 'pipe']});
  t.after(() => child.kill());
  let output = '', error = '';
  child.stdout.setEncoding('utf8'); child.stdout.on('data', chunk => { output += chunk; });
  child.stderr.setEncoding('utf8'); child.stderr.on('data', chunk => { error += chunk; });
  const closed = new Promise((resolve, reject) => { child.on('error', reject); child.on('close', resolve); });
  child.stdin.write(raw.subarray(0, split));
  await new Promise(resolve => setTimeout(resolve, 150));
  child.stdin.end(raw.subarray(split));
  assert.equal(await closed, 0, error);
  const audit = JSON.parse(output);
  assert.equal(audit.report_sha256, digest(report));
  assert.equal(audit.status, 'mechanical_pass');
});

test('all anchors remain discoverable when one source exceeds the catalog display budget', async t => {
  const {store} = await setup(t), source = await web(store);
  const ids = [];
  for (let i = 0; i < 25; i++) {
    const read = await store.open({source_id: source.id, offset: i * 10, limit: 10});
    await store.pin(pin(read.evidence_id, {label: '同名关键附注'})); ids.push(read.evidence_id);
  }
  const first = store.catalog();
  assert.equal(first.entries[0].evidence_next_offset, 12);
  let offset = 0, found = [];
  do {
    const page = store.catalog({source_id: source.id, evidence_offset: offset}).entries[0];
    found.push(...page.evidence.map(x => x.evidence_id)); offset = page.evidence_next_offset;
  } while (offset !== null);
  assert.deepEqual(found, ids);
  assert.throws(() => store.catalog({evidence_offset: 12}), /requires_source/);
});

test('code and comments cannot satisfy required citations, including unclosed fences', async t => {
  const {store} = await setup(t), read = await reading(store);
  await store.pin(pin(read.evidence_id)); const c = (await store.cite({evidence_id: read.evidence_id})).markdown;
  for (const report of ['```markdown\n' + c + '\n```', '~~~\n' + c, '    ' + c, '`' + c + '`', '<!-- hidden\n' + c + '\n-->'])
    assert.equal((await store.checkCitations(report)).status, 'failed', report);
  const source = await web(store, 'cash `net` < 5 * USD');
  const r = await store.open({source_id: source.id});
  await store.pin(pin(read.evidence_id, {required_citation: false, note: '该段未采用'}));
  const c2 = await store.cite({evidence_id: r.evidence_id, quote: 'cash `net` < 5 * USD'});
  assert.equal((await store.checkCitations(c2.markdown)).status, 'mechanical_pass');
});

test('raw source, extracted text and anchor changes fail rather than falling back to summaries', async t => {
  for (const target of ['raw', 'text', 'anchor']) {
    const {store, config} = await setup(t), r = await reading(store), source = store.sources.get(r.source_id);
    await store.pin(pin(r.evidence_id)); const c = await store.cite({evidence_id: r.evidence_id});
    const file = target === 'anchor' ? `anchors/${r.evidence_id}.json` :
      target === 'raw' ? source.data.bindings[0].file : source.data.parts[0].file;
    await fs.appendFile(path.join(config.directory, file), 'changed');
    if (target === 'anchor') await assert.rejects(new EvidenceStore(config).init());
    else {
      await assert.rejects(store.open({evidence_id: r.evidence_id}), /source_changed/);
      assert.equal((await store.checkCitations(c.markdown)).status, 'failed');
    }
  }
});

test('unknowns, conflicts and explicit non-use survive bounded context and pin revisions', async t => {
  const {store, config} = await setup(t), source = await web(store);
  for (let i = 0; i < 9; i++) {
    const r = await store.open({source_id: source.id, offset: i * 10, limit: 10});
    await store.pin(pin(r.evidence_id, {label: '待复核' + i, stance: 'unresolved', currency: null}));
  }
  assert.ok(store.context().length < 3500); assert.match(store.context(), /另有[3-9]个/);
  assert.match(store.context(), /"currency":null/);
  const first = [...store.pins.keys()][0];
  await store.pin(pin(first, {stance: 'rejected', required_citation: false, note: '主体不符，明确不采用'}));
  const fresh = await new EvidenceStore(config).init();
  assert.equal(fresh.pins.get(first).data.revision, 2);
  await assert.rejects(fresh.cite({evidence_id: first}), /rejected/);
  assert.equal((await fresh.checkCitations('未引用其它未决证据')).required_evidence, 8);
});

test('symlinks, out-of-range reads, cancellation, and duplicate source limits are explicit', async t => {
  const {store, config} = await setup(t), source = await web(store);
  await assert.rejects(store.open({source_id: source.id, limit: 4001}), /invalid_read_range/);
  await assert.rejects(store.open({source_id: source.id, offset: longText.length}), /empty/);
  const abort = new AbortController(); abort.abort();
  await assert.rejects(store.open({source_id: source.id}, abort.signal), /cancelled/);
  for (let i = 1; i < 128; i++) await web(store, 'text', 'https://example.org/' + i);
  assert.equal((await web(store)).id, source.id);
  await assert.rejects(web(store, 'text', 'https://example.org/overflow'), /context_record_limit/);
  const record = source.data.parts[0]; await fs.unlink(path.join(config.directory, record.file));
  await fs.symlink(path.join(config.directory, source.data.bindings[0].file), path.join(config.directory, record.file));
  await assert.rejects(store.open({source_id: source.id}));
});

// Real PyMuPDF extraction, with no network: the fixture is a synthetic disclosure.
async function pdfFixture(s) {
  const py = process.env.CONTEXT_TEST_PDF_PYTHON;
  const gap = digest('offline-pdf'), dir = path.join(s.config.recoveryDirectory, gap, 'document-1');
  await fs.mkdir(dir, {recursive: true});
  const code = `import sys,json,pathlib,pymupdf\nfrom scripts.research_document_recovery import extract\np=pathlib.Path(sys.argv[1]);d=pymupdf.open()\nfor text in ['Cover 2025 annual report', 'Restricted cash -1234.50 CNY ten-thousand; excludes free cash', '']:\n page=d.new_page();page.insert_text((72,72),text)\nraw=d.tobytes();d.close()\nextract(raw,dict(content_type='application/pdf',requested_url='https://example.org/annual.pdf',final_url='https://example.org/annual.pdf'),p)\n`;
  const result = spawnSync(py, ['-c', code, dir], {encoding: 'utf8'}); assert.equal(result.status, 0, result.stderr);
  const raw = await fs.readFile(path.join(dir, 'document.json')), doc = JSON.parse(raw);
  const event = {gap_id: gap, valuation_cutoff: s.config.asOf, category: 'document', document: doc,
    document_directory: 'document-1', document_manifest: {file: 'document.json', sha256: digest(raw)}, request: {url: doc.requested_url}};
  await fs.writeFile(path.join(dir, '..', 'event-000001.json'), JSON.stringify(event));
  return {gap, dir, source: await s.store.registerRecovery(gap)};
}
test('real three-page PDF: correct page survives reload, blank page stays unread, bad page fails audit',
  {skip: !process.env.CONTEXT_TEST_PDF_PYTHON}, async t => {
    const s = await setup(t), fixture = await pdfFixture(s);
    assert.equal(fixture.source.data.kind, 'pdf');
    const match = (await s.store.find({source_id: fixture.source.id, query: 'Restricted cash'})).matches[0];
    assert.equal(match.part, 2);
    const r = await s.store.open({source_id: fixture.source.id, ...match});
    assert.equal(r.pdf_page, 2); await s.store.pin(pin(r.evidence_id));
    const c = await s.store.cite({evidence_id: r.evidence_id, quote: 'Restricted cash -1234.50'});
    assert.match(c.markdown, /#page=2/);
    const fresh = await new EvidenceStore(s.config).init();
    assert.equal((await fresh.checkCitations(c.markdown)).status, 'mechanical_pass');
    assert.equal((await fresh.checkCitations(c.markdown.replace('#page=2', '#page=1'))).status, 'failed');
    await assert.rejects(fresh.open({source_id: fixture.source.id, part: 3}), /empty_or_scanned/);
    await fs.appendFile(path.join(fixture.dir, 'source.pdf'), 'changed');
    await assert.rejects(fresh.open({evidence_id: r.evidence_id}), /source_changed/);
  });

async function native(t, s, beforeContext) {
  const load = p => import(pathToFileURL(path.join(process.env.DSH_PACKAGE_ROOT, 'node_modules/@deepseek-ai', p, 'lib/index.js')).href);
  const {Context} = await load('cordis'), {SystemPrompt} = await load('dsh-system-prompt'), {ToolRuntime} = await load('dsh-tools');
  const ctx = new Context(), handles = [];
  const mount = async (plugin, config = {}) => { const h = await ctx.plugin(plugin, config).await(); handles.push(h); return h; };
  await mount(SystemPrompt); await mount(ToolRuntime);
  if (beforeContext) await beforeContext(mount);
  await mount({name: 'context-test', inject: ['tools', 'systemPrompt'], apply}, s.config);
  t.after(async () => { for (const h of handles.reverse()) await h.dispose(); });
  const call = async (name, args) => {
    const r = await ctx.tools.execute({name, arguments: args, callId: 'test-' + Math.random(), signal: new AbortController().signal});
    assert.equal(r.isError, false, JSON.stringify(r)); return r.value;
  };
  return {ctx, load, mount, call};
}
test('real DSH native pruning then lossy compaction still locates, rereads and cites middle evidence',
  {skip: !process.env.DSH_PACKAGE_ROOT}, async t => {
    const s = await setup(t), n = await native(t, s);
    const {SessionStore} = await n.load('dsh-session'), {SessionProjectionRegistry} = await n.load('dsh-session-projection');
    const {TokenMeter} = await n.load('dsh-token-meter'), llm = await n.load('dsh-llm');
    const {ToolResultPruner} = await n.load('dsh-compaction-tool-result-pruner');
    const {BasicCompactionEngine} = await n.load('dsh-compaction-basic');
    let summaries = 0;
    class Offline extends BasicCompactionEngine {
      async summarize() { summaries++; return {summary: [{type: 'text', text: '继续投研；摘要刻意不保留原文数字、页码和证据ID。'}], provider: 'offline', model: 'fixture'}; }
    }
    for (const p of [SessionStore, SessionProjectionRegistry, TokenMeter, llm.LlmRuntime, ToolResultPruner]) await n.mount(p);
    await n.mount(Offline, {auto: false});
    n.ctx.tools.register({name: 'web_fetch', description: 'offline', parameters: {type: 'object', properties: {url: {type: 'string'}}},
      output: {schema: {}, render: () => [{type: 'text', text: longText}]}, execute: async () => body()});
    await n.call('web_fetch', {url: 'https://example.org/report'});
    const catalog = await n.call('research_find_evidence', {}), source = catalog.entries[0].source_id;
    const match = (await n.call('research_find_evidence', {source_id: source, query: '受限现金'})).matches[0];
    const read = await n.call('research_open_evidence', {source_id: source, part: match.part, offset: match.offset, limit: 400});
    await n.call('research_pin_evidence', pin(read.evidence_id));
    const sourceCatalog = await n.call('research_find_evidence', {source_id: source, evidence_offset: 0});
    assert.equal(sourceCatalog.entries[0].evidence[0].evidence_id, read.evidence_id);
    const session = n.ctx.sessions.create('session-context-fixture');
    session.append('turn/start', {turn: 1});
    session.append('user/message', llm.createUserMessage({content: [{type: 'text', text: '请核现金口径'}], source: {kind: 'user'}}), {surfaceOp: 'append'});
    session.append('step/start', {turn: 1, step: 1});
    session.append('assistant/message', {turn: 1, step: 1, stream: [], message: llm.createAssistantMessage({source: {provider: 'offline', model: 'fixture'},
      content: [{type: 'tool-call', id: 'call-1', name: 'web_fetch', arguments: '{"url":"https://example.org/report"}'}]})}, {surfaceOp: 'append'});
    session.append('tool/result', {turn: 1, step: 1, message: llm.createToolResultMessage({callId: 'call-1', content: [{type: 'text', text: longText}], isError: false})}, {surfaceOp: 'append'});
    session.append('step/end', {turn: 1, step: 1});
    const before = JSON.stringify(session.deriveMessages()); assert.ok(before.includes(middle));
    const pruned = n.ctx.toolResultPruner.pruneSession(session);
    assert.equal(pruned.pruned.length, 1); assert.ok(!JSON.stringify(session.deriveMessages()).includes(middle));
    const compacted = await n.ctx.compaction.compactRegion(session.surface.nodes[0], session.surface.nodes.at(-1), {session, options: {}});
    assert.equal(summaries, 1); assert.equal(session.surface.nodes.length, 1); assert.ok(compacted.shadowedSeqs.length > 1);
    assert.ok(!JSON.stringify(session.deriveMessages()).includes(read.evidence_id));
    n.ctx.systemPrompt.suppressRuntimeContext();
    const assembly = await n.ctx.systemPrompt.assemble();
    const context = assembly.contexts.find(c => c.name === 'research-evidence-locators');
    assert.ok(context); assert.ok(context.text.includes(read.evidence_id)); assert.ok(context.text.includes('万元'));
    const found = await n.call('research_find_evidence', {query: '受限现金'});
    assert.equal(found.entries[0].evidence[0].evidence_id, read.evidence_id);
    const reread = await n.call('research_open_evidence', {evidence_id: read.evidence_id});
    assert.equal(reread.content, read.content);
    const citation = await n.call('research_cite_evidence', {evidence_id: read.evidence_id, quote: middle});
    assert.equal((await n.call('research_check_citations', {report: citation.markdown})).status, 'mechanical_pass');
    assert.equal((await new EvidenceStore(s.config).init()).sources.size, 1);
    t.diagnostic(JSON.stringify({native_prune_chars_removed: pruned.charsRemoved, native_compactions: summaries,
      critical_text_missing_after_prune: true, summary_omitted_evidence: true, reread_exact: true, citation_status: 'mechanical_pass', model_calls: 0}));
  });

test('real DSH health, automatic recovery and context indexing share the recovered document without a second fetch',
  {skip: !process.env.DSH_PACKAGE_ROOT}, async t => {
    const s = await setup(t);
    const worker = path.join(s.temp, 'worker.py');
    await fs.writeFile(worker, `import sys,json,pathlib,hashlib\nr=json.load(sys.stdin);p=pathlib.Path(r['directory'])\ndef save(n,b):\n (p/n).write_bytes(b);return dict(file=n,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))\nb=b'Restricted cash -1234.50 CNY; source fixture'\nraw=save('source.txt',b);part=dict(index=1,chars=len(b),lines=1,**save('document.txt',b))\nd=dict(schema_version='research-document-recovery/v1',kind='pdf',transport_complete=True,text_available=True,semantic_verification='pending',raw=raw,parts=[part],warnings=[],requested_url=r['url'],final_url=r['url'])\nsave('document.json',(json.dumps(d)+'\\n').encode());print(json.dumps(dict(ok=True,result=d)))\n`);
    const py = spawnSync(process.env.RECOVERY_TEST_PYTHON ?? 'python3', ['-c', 'import sys;print(sys.executable)'], {encoding: 'utf8'}).stdout.trim();
    const n = await native(t, s, async mount => {
      const {apply: health} = await import('../scripts/research_data_health.mjs');
      const {apply: recovery} = await import('../scripts/research_evidence_recovery.mjs');
      const healthDir = path.join(s.temp, 'data-health'); await fs.mkdir(healthDir);
      await mount({name: 'health-context-test', inject: ['tools'], apply: health}, {directory: healthDir, asOf: s.config.asOf});
      await mount({name: 'recovery-context-test', inject: ['tools'], apply: recovery}, {directory: s.config.recoveryDirectory,
        asOf: s.config.asOf, python: py, worker, healthModule: path.resolve('scripts/research_data_health.mjs')});
    });
    let fetches = 0;
    n.ctx.tools.register({name: 'web_fetch', description: 'offline PDF', parameters: {type: 'object', additionalProperties: true},
      output: {schema: {}, render: () => []}, execute: async () => {fetches++; throw new Error('Unsupported content type application/pdf');}});
    const failed = await n.ctx.tools.execute({name: 'web_fetch', arguments: {url: 'https://example.org/a.pdf'}, callId: 'pdf', signal: new AbortController().signal});
    assert.equal(failed.isError, true);
    const catalog = await n.call('research_find_evidence', {});
    assert.equal(catalog.total, 1); assert.equal(catalog.entries[0].kind, 'pdf');
    const read = await n.call('research_open_evidence', {source_id: catalog.entries[0].source_id});
    assert.match(read.content, /-1234.50/); assert.equal(read.pdf_page, 1);
    assert.equal(fetches, 1);
    const stateDir = path.join(s.config.recoveryDirectory, (await fs.readdir(s.config.recoveryDirectory))[0]);
    const events = (await fs.readdir(stateDir)).filter(x => x.startsWith('event-')).sort();
    assert.equal(JSON.parse(await fs.readFile(path.join(stateDir, events.at(-1)))).document_download_attempts, 1);
  });

test('real DSH final-result denial is not indexed; concurrent reads and prompt refresh see committed sources',
  {skip: !process.env.DSH_PACKAGE_ROOT}, async t => {
    const s = await setup(t), n = await native(t, s);
    n.ctx.tools.register({name: 'web_fetch', description: 'offline', parameters: {type: 'object', additionalProperties: true},
      output: {schema: {}, render: () => [{type: 'text', text: 'original'}]}, execute: async () => body()});
    n.ctx.on('tools/pre-execute', async (exec, next) => exec.name === 'web_fetch' && exec.arguments.url.includes('deny')
      ? {kind: 'deny', reason: 'fixture denied'} : next());
    n.ctx.on('tools/post-execute', async (exec, result, next) => exec.name === 'web_fetch' && exec.arguments.url.includes('blocked')
      ? {kind: 'block', feedback: [{type: 'text', text: 'offline policy block'}]} : next());
    await n.ctx.tools.execute({name: 'web_fetch', arguments: {url: 'https://example.org/deny'}, callId: 'deny', signal: new AbortController().signal});
    await n.ctx.tools.execute({name: 'web_fetch', arguments: {url: 'https://example.org/blocked'}, callId: 'blocked', signal: new AbortController().signal});
    assert.equal((await n.call('research_find_evidence', {})).total, 0);
    await Promise.all([n.call('web_fetch', {url: 'https://example.org/a'}), n.call('web_fetch', {url: 'https://example.org/b'})]);
    const assembly = await n.ctx.systemPrompt.assemble();
    assert.match(assembly.contexts.find(c => c.name === 'research-evidence-locators').text, /2个来源/);
    assert.equal((await n.call('research_find_evidence', {})).total, 2);
  });
