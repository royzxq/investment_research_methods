import test from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {inspect, precheck, Coverage, apply, isoDay} from '../scripts/research_data_health.mjs';

const AK = 'mcp__aktools__get_data';
const args = {name: 'stock_financial_hk_report_em', params: {stock: '01211', symbol: '利润表'}, max_rows: 2, offset: 0};
const row = i => ({SECUCODE: '01211.HK', SECURITY_CODE: '01211', REPORT_DATE: '2026-09-30 00:00:00',
  STD_ITEM_CODE: String(i), AMOUNT: i});
const page = (offset = 0, count = 2, total = 3) => ({name: args.name, total_rows: total, offset,
  returned_rows: count, truncated: true, columns: Object.keys(row(1)), rows: Array.from({length: count}, (_, i) => row(offset + i))});
const result = data => ({isError: false, value: {content: [{type: 'text', text: JSON.stringify(data)}],
  structuredContent: {result: data}}, content: [{type: 'text', text: 'original presentation'}]});
const web = (content, extra = {}) => ({isError: false,
  value: {url: 'https://example.com/report', statusCode: 200, body: {kind: 'html', content}, truncated: false, ...extra},
  content: [{type: 'text', text: content}]});
const codes = report => report.issues.map(x => x.code);
const check = (r, a = args, options = {}) => inspect(AK, a, r, {asOf: '2026-11-08', ...options});

test('preflight refuses ambiguous identities, lossy numeric tickers and invalid pagination before retrieval', () => {
  assert.deepEqual(precheck(AK, args), []);
  for (const changed of [{params: {stock: 1211}}, {params: {stock: '1211'}}, {offset: '1'}, {offset: 0.5}, {max_rows: 1001}])
    assert.ok(precheck(AK, {...args, ...changed}).some(x => x.severity === 'reject'));
  assert.ok(precheck(AK, {name: 'stock_profit_sheet_by_report_em', params: {symbol: '000001'}}).length);
  assert.deepEqual(precheck(AK, {name: 'stock_profit_sheet_by_report_em', params: {symbol: 'SZ000001'}}), []);
  for (const url of ['file:///tmp/report', 'https://user:secret@example.com', 'invalid'])
    assert.ok(precheck('web_fetch', {url}).length);
});

test('nonempty HTTP 200 with a truncated script shell is not a body verification', () => {
  const r = inspect('web_fetch', {url: 'https://example.com'}, web('<head>Title</head><nav>Links</nav><script>' + 'x'.repeat(10000), {truncated: true}));
  assert.ok(codes(r).includes('body_truncated'));
  assert.ok(codes(r).includes('html_no_visible_body'));
  assert.equal(r.status, 'review_required');
  assert.equal(r.fact_verification, 'not_performed');
});

test('short genuine text is usable for review, while empty and failed HTTP cannot masquerade as success', () => {
  const short = inspect('web_fetch', {url: 'https://example.com'}, web('<p>2026-11-08 停牌公告</p>'));
  assert.equal(short.status, 'review_required');
  assert.notEqual(short.status, 'rejected');
  for (const r of [web(''), web('Not found', {statusCode: 404}), {isError: true}])
    assert.equal(inspect('web_fetch', {url: 'https://example.com'}, r).status, 'rejected');
  assert.equal(inspect('web_fetch', {url: 'https://example.com'}, web('valid', {body: {kind: 'text', content: 'valid'}})).status, 'mechanical_checks_only');
});

test('empty table never means no announcement or zero business activity', () => {
  const r = check(result(page(0, 0, 0)));
  assert.ok(codes(r).includes('empty_result_not_absence'));
  assert.equal(r.observed.coverage, 'empty');
  assert.equal(check(result(page(0, 0, 3))).status, 'rejected');
});

test('complete pagination is the union of returned offsets; truncated tail does not erase completion', () => {
  const coverage = new Coverage();
  assert.equal(check(result(page()), args, {coverage}).observed.coverage, 'partial');
  const tail = {...args, offset: 2};
  assert.equal(check(result(page(2, 1)), tail, {coverage}).observed.coverage, 'complete_observed');
  assert.equal(check(result(page()), args, {coverage}).observed.coverage, 'complete_observed');
  assert.equal(check(result(page(2, 1)), tail).observed.coverage, 'partial');
  assert.equal(check(result(page(2, 1)), {...args, offset: -1}).observed.coverage, 'partial');
  assert.notEqual(check(result(page(3, 0)), {...args, offset: 999}).status, 'rejected');
  assert.equal(check(result(page(0, 2)), {...args, offset: -999}).observed.coverage, 'partial');
});

test('repeated pages, changed totals and conflicting overlaps are never complete histories', () => {
  const coverage = new Coverage();
  check(result(page()), args, {coverage});
  const repeat = page(2, 1); repeat.rows = [row(0)];
  assert.equal(check(result(repeat), {...args, offset: 2}, {coverage}).observed.coverage, 'conflict');
  const fresh = new Coverage();
  check(result(page()), args, {coverage: fresh});
  assert.ok(codes(check(result(page(2, 1, 4)), {...args, offset: 2}, {coverage: fresh})).includes('pagination_conflict'));
});

test('pagination metadata, interface or company mismatches reject the response', () => {
  for (const mutate of [d => { d.offset = 1; }, d => { d.returned_rows = 1; }, d => { d.name = 'other'; },
    d => { d.rows[0].SECURITY_CODE = '00700'; }, d => { d.rows[0].SECUCODE = '01211.SH'; },
    d => { delete d.rows[0].AMOUNT; }]) {
    const d = page(); mutate(d);
    assert.equal(check(result(d)).status, 'rejected');
  }
});

test('zero and negative profit are valid values; nulls and placeholders remain missing, never repaired', () => {
  const d = page(); d.rows[0].AMOUNT = 0; d.rows[1].AMOUNT = -100;
  const original = JSON.stringify(d);
  assert.equal(check(result(d)).observed.missing_financial_cells, 0);
  assert.equal(JSON.stringify(d), original);
  d.rows[0].AMOUNT = null; d.rows[1].AMOUNT = '--';
  assert.equal(check(result(d)).observed.missing_financial_cells, 2);
  assert.equal(d.rows[0].AMOUNT, null);
  assert.ok(codes(check(result(d))).includes('currency_or_unit_unverified'));
});

test('report period and publication date are distinct; future rows are identified without fabricating disclosure', () => {
  const d = page(); d.rows[0].REPORT_DATE = '2026-12-31';
  d.rows[1].NOTICE_DATE = '2026-11-09 00:00:00';
  const r = check(result(d));
  assert.equal(r.observed.future_report_period_rows, 1);
  assert.equal(r.observed.future_disclosure_rows, 1);
  assert.equal(r.observed.disclosure_unknown_rows, 1);
  assert.ok(codes(r).includes('rows_after_valuation_cutoff'));
  assert.equal(isoDay('2026-02-30'), null);
  assert.equal(isoDay('2026-02-28T10:00:00'), '2026-02-28');
});

test('unknown interface semantics are not guessed; malformed envelopes fail', () => {
  const a = {...args, name: 'another_interface'}, d = page(); d.name = a.name;
  assert.ok(codes(check(result(d), a)).includes('interface_semantics_unchecked'));
  for (const value of [{}, {structuredContent: {}}, {content: [{type: 'text', text: 'not JSON'}]}])
    assert.equal(check({isError: false, value}).status, 'rejected');
  const d2 = page();
  assert.equal(check({isError: false, value: {content: [{type: 'text', text: JSON.stringify(d2)}]}}).observed.returned_rows, 2);
  const conflict = result(page()); conflict.value.content[0].text = JSON.stringify(page(1, 1));
  assert.equal(check(conflict).status, 'rejected');
});

async function hooks(t) {
  const directory = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'data-health-')));
  t.after(() => fs.rm(directory, {recursive: true, force: true}));
  const handlers = {};
  apply({on: (event, handler) => { handlers[event] = handler; }}, {directory, asOf: '2026-11-08'});
  return {directory, handlers};
}
const exec = a => ({name: AK, arguments: a, callId: 'test-call'});

test('hooks preserve original value, persist hashed raw response, and expose partial coverage before analysis', async t => {
  const {directory, handlers} = await hooks(t), r = result(page()), original = JSON.stringify(r);
  const decision = await handlers['tools/post-execute'](exec(args), r, async () => ({kind: 'accept'}));
  assert.equal(decision.kind, 'accept');
  assert.match(decision.content[0].text, /pagination_incomplete/);
  assert.deepEqual(decision.content.slice(1), r.content);
  assert.equal(JSON.stringify(r), original);
  const file = (await fs.readdir(directory)).find(x => x.endsWith('.check.json'));
  const audit = JSON.parse(await fs.readFile(path.join(directory, file)));
  const raw = await fs.readFile(path.join(directory, audit.raw_path));
  assert.equal(createHash('sha256').update(raw).digest('hex'), audit.raw_sha256);
  assert.deepEqual(JSON.parse(raw), r.value);
});

test('preflight blocks before next; unrelated calls and downstream denials retain their original behavior', async t => {
  const {handlers} = await hooks(t);
  const never = async () => { throw new Error('must not run'); };
  assert.equal((await handlers['tools/pre-execute'](exec({...args, offset: 0.5}), never)).kind, 'deny');
  const denial = {kind: 'block', feedback: [{type: 'text', text: 'other policy'}]};
  assert.deepEqual(await handlers['tools/post-execute'](exec(args), result(page()), async () => denial), denial);
  const marker = {kind: 'accept', content: [{type: 'text', text: 'another projection'}]};
  const projected = await handlers['tools/post-execute'](exec(args), result(page()), async () => marker);
  assert.deepEqual(projected.content.slice(1), marker.content);
  assert.match(projected.content[0].text, /pagination_incomplete/);
  assert.equal(await handlers['tools/post-execute']({...exec(args), name: 'bash'}, {}, async () => marker), marker);
  const nested = await handlers['tools/post-execute']({...exec(args), parent: Symbol('ptc')}, result(page()), async () => ({kind: 'accept'}));
  assert.match(nested.additionalContexts[0].content[0].text, /pagination_incomplete/);
  assert.equal(nested.additionalContexts[0].source.kind, 'tool');
});

test('a rejected page cannot contaminate later correct coverage, and failed tools retain their diagnostics', async t => {
  const coverage = new Coverage(), bad = page(); bad.rows[0].SECURITY_CODE = '00700';
  assert.equal(check(result(bad), args, {coverage}).observed.coverage, 'rejected_page');
  assert.equal(check(result(page()), args, {coverage}).observed.coverage, 'partial');
  const {handlers} = await hooks(t);
  const error = {isError: true, content: [{type: 'text', text: 'PDF unsupported'}]};
  const decision = await handlers['tools/post-execute'](exec(args), error, async () => ({kind: 'accept'}));
  assert.equal(decision.kind, 'accept'); // Retains the native failed outcome.
  assert.deepEqual(decision.content.slice(1), error.content);
});

test('failed persistence never reports a successful check and cannot follow a replaced output directory', async t => {
  const {directory, handlers} = await hooks(t);
  await fs.rmdir(directory);
  const elsewhere = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'health-target-')));
  t.after(() => fs.rm(elsewhere, {recursive: true, force: true}));
  await fs.symlink(elsewhere, directory);
  const outcome = await handlers['tools/post-execute'](exec(args), result(page()), async () => ({kind: 'accept'}));
  assert.equal(outcome.kind, 'block');
  assert.deepEqual(await fs.readdir(elsewhere), []);
});

test('installed DSH ToolRuntime dispatches real pre/post policies and preserves canonical values',
  {skip: !process.env.DSH_PACKAGE_ROOT}, async t => {
    const root = path.resolve(process.env.DSH_PACKAGE_ROOT);
    const load = pkg => import(pathToFileURL(path.join(root, 'node_modules/@deepseek-ai', pkg, 'lib/index.js')).href);
    const [{Context}, {SystemPrompt}, {ToolRuntime}] = await Promise.all([load('cordis'), load('dsh-system-prompt'), load('dsh-tools')]);
    const directory = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'health-native-')));
    t.after(() => fs.rm(directory, {recursive: true, force: true}));
    const ctx = new Context();
    const prompt = await ctx.plugin(SystemPrompt, {}).await();
    const tools = await ctx.plugin(ToolRuntime, {}).await();
    const health = await ctx.plugin({name: 'data-health-test', inject: ['tools'], apply}, {directory, asOf: '2026-11-08'}).await();
    t.after(async () => { await health.dispose(); await tools.dispose(); await prompt.dispose(); });
    let called = 0;
    const original = web('<script>no body', {truncated: true}).value;
    ctx.tools.register({name: 'web_fetch', description: 'offline fixture', parameters: {type: 'object', properties: {url: {type: 'string'}}},
      output: {schema: {}, render: () => [{type: 'text', text: 'original'}]}, execute: async () => {called++; return original;}});
    const call = (url, id) => ctx.tools.execute({name: 'web_fetch', callId: id, arguments: {url}, signal: new AbortController().signal});
    const rejected = await call('file:///tmp/test', 'pre');
    assert.equal(rejected.isError, true); assert.equal(called, 0);
    const accepted = await call('https://example.com', 'post');
    assert.equal(accepted.isError, false); assert.equal(called, 1);
    assert.deepEqual(accepted.value, original);
    assert.match(accepted.content[0].text, /body_truncated/);
    assert.equal((await fs.readdir(directory)).filter(x => x.endsWith('.check.json')).length, 2);
  });
