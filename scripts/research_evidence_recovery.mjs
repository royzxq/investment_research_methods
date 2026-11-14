/** Bounded recovery through native DSH tools; source, reading and use stay separate. */
import {createHash, randomUUID} from 'node:crypto';
import {constants} from 'node:fs';
import * as fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawn} from 'node:child_process';

export const name = 'research-evidence-recovery';
export const inject = ['tools'];
export const VERSION = 'evidence-recovery-v1';
const AK = 'mcp__aktools__get_data';
const SCHEMA = 'research-evidence-recovery/v1';
const MAX_FILE = 32 * 1024 * 1024;
const MAX_GAPS = 64, MAX_ROUNDS = 3, PAGES_PER_ROUND = 3;
const canonical = x => JSON.stringify(x, (k, v) => v && typeof v === 'object' && !Array.isArray(v)
  ? Object.fromEntries(Object.keys(v).sort().map(key => [key, v[key]])) : v);
const hash = x => createHash('sha256').update(x).digest('hex');
const text = x => [{type: 'text', text: typeof x === 'string' ? x : JSON.stringify(x)}];
const table = value => value.structuredContent?.result ?? value.structuredContent ?? JSON.parse(value.content[0].text);
const aborted = signal => { if (signal?.aborted) throw new Error('cancelled'); };
const normalizedURL = value => { const url = new URL(value); url.hash = ''; return url.href; };

async function safeDirectory(directory) {
  const st = await fs.lstat(directory);
  if (!st.isDirectory() || st.isSymbolicLink() || await fs.realpath(directory) !== directory)
    throw new Error('unsafe_evidence_directory');
}
async function writeNew(directory, file, value) {
  await safeDirectory(directory);
  if (path.basename(file) !== file) throw new Error('unsafe_evidence_path');
  const raw = typeof value === 'string' ? value : JSON.stringify(value, null, 2) + '\n';
  if (Buffer.byteLength(raw) > MAX_FILE) throw new Error('evidence_size_limit');
  const fd = await fs.open(path.join(directory, file), constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW, 0o600);
  try { await fd.writeFile(raw); } finally { await fd.close(); }
  return {file, sha256: hash(raw), bytes: Buffer.byteLength(raw)};
}
async function readFile(directory, record) {
  await safeDirectory(directory);
  if (path.basename(record.file) !== record.file) throw new Error('unsafe_evidence_path');
  const fd = await fs.open(path.join(directory, record.file), constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const st = await fd.stat();
    if (!st.isFile() || st.size > MAX_FILE) throw new Error('invalid_evidence_file');
    const raw = await fd.readFile();
    if (record.sha256 && hash(raw) !== record.sha256) throw new Error('evidence_changed');
    return raw;
  } finally { await fd.close(); }
}

/** No shell, inherited credentials or unbounded stdout; terminate and reap on abort. */
export function documentWorker(config, request, signal) {
  return new Promise((resolve, reject) => {
    aborted(signal);
    const env = Object.fromEntries(['PATH', 'LANG', 'LC_ALL', 'TMPDIR', 'SYSTEMROOT']
      .filter(k => process.env[k]).map(k => [k, process.env[k]]));
    const child = spawn(config.python, ['-I', '-B', config.worker], {env, cwd: request.directory, stdio: ['pipe', 'pipe', 'pipe']});
    const output = [];
    let bytes = 0, failed;
    const stop = reason => { failed ??= reason; child.kill('SIGKILL'); };
    const cancel = () => stop('cancelled');
    const timer = setTimeout(() => stop('document_timeout'), 90000);
    signal?.addEventListener('abort', cancel, {once: true});
    if (signal?.aborted) cancel();
    child.stdout.on('data', chunk => {
      bytes += chunk.length;
      if (bytes > 2 * 1024 * 1024) stop('worker_output_limit'); else output.push(chunk);
    });
    child.stderr.on('data', () => {}); // Parser diagnostics can contain source text/URLs.
    child.stdin.on('error', () => {});
    child.on('error', () => { failed = 'worker_start_failed'; });
    child.on('close', code => {
      clearTimeout(timer); signal?.removeEventListener('abort', cancel);
      if (failed) return reject(new Error(failed));
      try {
        const value = JSON.parse(Buffer.concat(output).toString('utf8'));
        if (code !== 0 || value.ok !== true) throw new Error(value.error || 'document_worker_failed');
        resolve(value.result);
      } catch (error) { reject(error); }
    });
    child.stdin.end(JSON.stringify(request));
  });
}

export async function apply(ctx, config) {
  if (!config || !path.isAbsolute(config.directory) || !path.isAbsolute(config.python)
      || !path.isAbsolute(config.worker) || !path.isAbsolute(config.healthModule)) throw new Error('invalid_recovery_config');
  const {inspect, Coverage, precheck, isoDay} = await import(pathToFileURL(config.healthModule).href);
  if (isoDay(config.asOf) !== config.asOf) throw new Error('invalid_recovery_cutoff');
  await safeDirectory(config.directory);
  const gaps = new Map(), locks = new Map(), internal = new Set(), dispatched = new Set();
  // A denied pre-dispatch call also reaches post-execute in DSH. Only recover
  // failures from calls that actually entered the authorized dispatch pipeline.
  ctx.on('tools/execute', async (exec, next) => {
    if (['web_fetch', AK].includes(exec.name)) dispatched.add(exec.callId);
    return next();
  });
  ctx.on('tools/result', exec => { dispatched.delete(exec.callId); });
  const locked = async (id, task) => {
    const previous = locks.get(id) ?? Promise.resolve();
    const current = previous.catch(() => {}).then(task);
    locks.set(id, current);
    try { return await current; } finally { if (locks.get(id) === current) locks.delete(id); }
  };
  const folder = id => path.join(config.directory, id);
  const save = async (g, event) => {
    const revision = g.state.revision + 1;
    await writeNew(folder(g.state.gap_id), `event-${String(revision).padStart(6, '0')}.json`,
      {...g.state, revision, event, updated_at: new Date().toISOString()});
    g.state.revision = revision;
  };
  const get = async (id, category, args) => {
    if (!/^[a-f0-9]{64}$/.test(id)) throw new Error('invalid_gap_id');
    if (gaps.has(id)) return gaps.get(id);
    if (gaps.size >= MAX_GAPS) throw new Error('gap_tracking_limit');
    const location = folder(id);
    if (category) await fs.mkdir(location, {recursive: false}).catch(e => { if (e.code !== 'EEXIST') throw e; });
    await safeDirectory(location);
    const files = (await fs.readdir(location)).filter(x => /^event-\d{6}\.json$/.test(x)).sort();
    let state;
    if (files.length) {
      state = JSON.parse(await readFile(location, {file: files.at(-1)}));
      if (state.schema_version !== SCHEMA || state.gap_id !== id || state.valuation_cutoff !== config.asOf)
        throw new Error('incompatible_recovery_state');
    } else {
      if (!category) throw new Error('unknown_gap');
      state = {schema_version: SCHEMA, gap_id: id, category, request: args, valuation_cutoff: config.asOf,
        revision: 0, retrieval_status: 'detected', attempts: 0, auto_scheduled: false, observations: 0,
        deduplicated_requests: 0, supplemental_tool_calls: 0, document_download_attempts: 0,
        recovery_wall_ms: 0, triggers: [], pages: [], reads: [], reviews: [], fact_verification: 'not_performed'};
    }
    const g = {state, coverage: new Coverage()};
    for (const p of state.pages) {
      const value = JSON.parse(await readFile(location, p.raw));
      inspect(AK, p.args, {isError: false, value}, {asOf: config.asOf, coverage: g.coverage});
    }
    gaps.set(id, g);
    if (state.retrieval_status === 'running') {
      state.retrieval_status = state.pages.length ? 'partial' : 'failed';
      state.remaining_issue = 'interrupted_recovery_not_complete';
      await save(g, 'interrupted_recovery_observed');
    }
    return g;
  };
  const snapshot = g => ({gap_id: g.state.gap_id, category: g.state.category, retrieval_status: g.state.retrieval_status,
    attempts: g.state.attempts, coverage: g.state.coverage ?? null, total_rows: g.state.total_rows ?? null,
    document_kind: g.state.document?.kind ?? null, parts: g.state.document?.parts.length ?? null,
    warnings: g.state.warnings ?? [], remaining_issue: g.state.remaining_issue ?? null,
    reads_recorded: g.state.reads.length, use_assessments: g.state.reviews.length,
    fact_verification: 'not_performed', evidence_directory: folder(g.state.gap_id),
    next: '用 research_read_evidence 定位/读取原文；用 research_record_evidence_use 记录采用范围或未解决原因。机械收齐不等于事实核验。'});
  const ingest = async (g, args, result) => {
    const report = inspect(AK, args, result, {asOf: config.asOf, coverage: g.coverage});
    g.state.warnings = report.issues.map(x => x.code);
    if (report.status === 'rejected' || report.observed.coverage === 'conflict') {
      g.state.retrieval_status = report.issues.some(x => x.code === 'upstream_tool_failed') ? 'partial' : 'conflict';
      g.state.remaining_issue = report.issues.some(x => x.code === 'upstream_tool_failed') ? 'page_request_failed' : 'page_failed_validation';
      await save(g, 'page_rejected'); return false;
    }
    const raw = JSON.stringify(result.value) + '\n';
    if (!g.state.pages.some(p => p.raw.sha256 === hash(raw) && canonical(p.args) === canonical(args))) {
      const record = await writeNew(folder(g.state.gap_id), `page-${randomUUID()}.json`, raw);
      g.state.pages.push({args, raw: record});
    }
    g.state.coverage = report.observed.coverage;
    g.state.total_rows = report.observed.total_rows;
    g.state.retrieval_status = report.observed.coverage === 'complete_observed' ? 'retrieved' : 'partial';
    g.state.remaining_issue = g.state.retrieval_status === 'retrieved' ? null : 'pagination_incomplete';
    await save(g, 'page_observed'); return true;
  };
  const dispatch = async (name, args, exec, signal = exec.signal) => {
    aborted(signal);
    const callId = `recovery-${randomUUID()}`;
    internal.add(callId);
    try {
      const result = await ctx.tools.execute({name, arguments: args, callId,
        rootCallId: exec.rootCallId ?? exec.callId, agent: exec.agent, parent: exec.token, signal});
      for (const context of result.additionalContexts ?? []) exec.deferContext?.(context);
      return result;
    } finally { internal.delete(callId); }
  };
  const recover = async (args, exec) => {
    if (!!args.gap_id === !!args.url) throw new Error('provide_gap_id_or_url');
    if (args.url && precheck('web_fetch', {url: args.url}).length) throw new Error('invalid_url');
    const url = args.url ? normalizedURL(args.url) : null;
    const id = args.gap_id ?? hash(canonical({category: 'document', url}));
    return locked(id, async () => {
      const g = await get(id, url ? 'document' : null, url ? {url} : null);
      if (url && !(g.state.triggers ?? []).length)
        g.state.triggers = [/\.pdf$/i.test(new URL(url).pathname) ? 'pdf' : 'explicit_document'];
      if (g.state.retrieval_status === 'retrieved' || g.state.retrieval_status === 'conflict'
          || (g.state.category !== 'pagination' && g.state.attempts > 0)) {
        g.state.deduplicated_requests++; await save(g, 'reused_recovery'); return snapshot(g);
      }
      if (g.state.attempts >= MAX_ROUNDS) {
        g.state.remaining_issue = 'recovery_budget_exhausted'; await save(g, 'budget_exhausted'); return snapshot(g);
      }
      aborted(exec.signal);
      const started = Date.now();
      g.state.attempts++; g.state.retrieval_status = 'running'; await save(g, 'recovery_started');
      try {
        if (g.state.category === 'pagination') {
          for (let n = 0; n < PAGES_PER_ROUND; n++) {
            aborted(exec.signal);
            const group = g.coverage.groups.get(canonical({name: g.state.request.name, params: g.state.request.params ?? {}}));
            if (!group || group.conflict) throw new Error('coverage_unavailable');
            let offset = 0;
            while (group.rows.has(offset) && offset < group.total) offset++;
            if (offset === group.total) break;
            const nextArgs = {...g.state.request, offset, max_rows: Math.min(1000, group.total - offset)};
            g.state.supplemental_tool_calls = (g.state.supplemental_tool_calls ?? 0) + 1;
            await save(g, 'page_requested');
            const result = await dispatch(AK, nextArgs, exec);
            if (!await ingest(g, nextArgs, result) || g.state.retrieval_status === 'retrieved') break;
          }
        } else {
          const docFolder = path.join(folder(id), `document-${g.state.attempts}`);
          await fs.mkdir(docFolder);
          g.state.document_download_attempts = (g.state.document_download_attempts ?? 0) + 1;
          await save(g, 'document_requested');
          const document = await documentWorker(config, {operation: 'download', url: g.state.request.url, directory: docFolder}, exec.signal);
          const manifestRaw = await readFile(docFolder, {file: 'document.json'});
          if (canonical(JSON.parse(manifestRaw)) !== canonical(document)) throw new Error('document_manifest_mismatch');
          g.state.document = document; g.state.document_directory = path.basename(docFolder);
          g.state.document_manifest = {file: 'document.json', sha256: hash(manifestRaw)};
          g.state.warnings = document.warnings;
          g.state.retrieval_status = document.text_available ? 'retrieved' : 'partial';
          g.state.remaining_issue = document.text_available ? null : 'visual_or_alternate_source_required';
        }
      } catch (error) {
        g.state.retrieval_status = exec.signal?.aborted ? 'cancelled' : 'failed';
        g.state.remaining_issue = /^[\w_-]{1,100}$/.test(error.message) ? error.message : 'recovery_failed';
      }
      g.state.recovery_wall_ms = (g.state.recovery_wall_ms ?? 0) + Math.max(0, Date.now() - started);
      await save(g, 'recovery_finished');
      return snapshot(g);
    });
  };
  const read = async (args, exec) => locked(args.gap_id, async () => {
    const g = await get(args.gap_id), s = g.state;
    aborted(exec.signal);
    if (s.reads.length >= 100) throw new Error('read_record_limit');
    if (s.retrieval_status === 'conflict') throw new Error('conflicting_pages_not_usable');
    const start = args.offset ?? 0, count = args.limit ?? (s.category === 'pagination' ? 20 : 6000);
    if (!Number.isSafeInteger(start) || start < 0 || !Number.isSafeInteger(count) || count < 1
        || count > (s.category === 'pagination' ? 100 : 12000)) throw new Error('invalid_read_range');
    let content, locator, source;
    if (s.category === 'pagination') {
      const rows = new Map();
      for (const p of s.pages) {
        const data = table(JSON.parse(await readFile(folder(s.gap_id), p.raw)));
        data.rows.forEach((r, i) => { if (data.offset + i >= start && data.offset + i < start + count) rows.set(data.offset + i, r); });
      }
      const selected = [...rows].sort((a, b) => a[0] - b[0]);
      if (!selected.length) throw new Error('requested_rows_not_observed');
      content = JSON.stringify(selected.map(([offset, row]) => ({offset, row})));
      if (content.length > 24000) throw new Error('reduce_row_count');
      locator = {kind: 'rows', offsets: selected.map(x => x[0])};
      source = s.pages.map(p => p.raw.sha256);
    } else {
      if (!s.document) throw new Error('document_not_available');
      const dir = path.join(folder(s.gap_id), s.document_directory);
      await readFile(dir, s.document_manifest);
      await readFile(dir, s.document.raw);
      if (args.render_page !== undefined) {
        const rendered = await documentWorker(config, {operation: 'render', directory: dir,
          manifest: s.document_manifest, page: args.render_page}, exec.signal);
        await save(g, 'page_rendered');
        return {gap_id: s.gap_id, ...rendered, path: path.join(dir, rendered.file),
          warning: '仅生成原页图片，尚未证明模型已查看。用已有图片读取工具核页；扫描页提取缺口继续保留。'};
      }
      if (args.query !== undefined) {
        if (typeof args.query !== 'string' || !args.query.trim() || args.query.length > 200) throw new Error('invalid_query');
        const matches = [];
        for (const p of s.document.parts) {
          aborted(exec.signal);
          const value = (await readFile(dir, p)).toString('utf8');
          let offset = value.indexOf(args.query);
          while (offset >= 0 && matches.length < 20) {
            matches.push({part: p.index, offset, snippet: value.slice(Math.max(0, offset - 80), offset + args.query.length + 160)});
            offset = value.indexOf(args.query, offset + args.query.length);
          }
          if (matches.length >= 20) break;
        }
        return {gap_id: s.gap_id, matches, capped: matches.length >= 20, warning: '搜索只定位；继续读取所需章节及相邻附注。'};
      }
      const part = s.document.parts.find(p => p.index === (args.part ?? 1));
      if (!part) throw new Error('invalid_document_part');
      const value = (await readFile(dir, part)).toString('utf8');
      if (start >= value.length) throw new Error('empty_range_or_scanned_page');
      content = value.slice(start, start + count);
      locator = {kind: 'text', part: part.index, pdf_page: s.document.kind === 'pdf' ? part.index : null,
        character_start: start, character_end: start + content.length, next_offset: start + content.length < value.length ? start + content.length : null,
        line_start: value.slice(0, start).split('\n').length};
      source = [part.sha256, s.document.raw.sha256];
    }
    const receipt = {receipt_id: randomUUID(), locator, source_sha256: source, excerpt_sha256: hash(content),
      content_chars: content.length, delivered_to_tool: true};
    s.reads.push(receipt); await save(g, 'evidence_read');
    return {gap_id: s.gap_id, receipt, content, warning: '这是原始材料片段；读取不等于事实核验或报告已经引用。'};
  });
  const review = async args => locked(args.gap_id, async () => {
    const g = await get(args.gap_id), s = g.state;
    const receipt = s.reads.find(x => x.receipt_id === args.receipt_id);
    if (!receipt || s.reviews.length >= 100 || !['used_for_scope', 'used_partial', 'unresolved', 'rejected', 'not_used'].includes(args.disposition))
      throw new Error('invalid_review');
    for (const key of ['affected_input', 'scope', 'reason'])
      if (typeof args[key] !== 'string' || !args[key].trim() || args[key].length > 2000) throw new Error('review_requires_scope_and_reason');
    if (args.disposition.startsWith('used_') && (typeof args.report_section !== 'string' || !args.report_section.trim() || args.report_section.length > 300))
      throw new Error('used_evidence_requires_report_section');
    const assessment = {...args, report_section: args.report_section ?? null, assessment_id: randomUUID(),
      actor: 'research_agent', independently_verified: false, final_citation_verified: false};
    s.reviews.push(assessment); await save(g, 'use_assessment_recorded');
    return {gap_id: s.gap_id, assessment, note: '已记录研究者判断及声明用途；未把它升级为程序验证的事实或最终引用。'};
  });
  const register = (toolName, description, properties, required, execute) => ctx.tools.register({
    name: toolName, description, parameters: {type: 'object', properties, required, additionalProperties: false},
    timeoutMs: toolName === 'research_recover_evidence' ? 300000 : 100000,
    output: {schema: {}, render: (args, value) => text(value)}, execute});
  const str = {type: 'string'}, integer = {type: 'integer'};
  register('research_recover_evidence', '补证：提供已提示的 gap_id 续补分页，或 url 下载 PDF/完整网页。每来源去重、有界，不修改原工具返回。',
    {gap_id: str, url: str}, [], recover);
  register('research_read_evidence', '读取补证原文：PDF part 为从1起的页序；文本 offset/limit 为字符，表格为行偏移/行数。query 只定位，render_page 仅生成图片。',
    {gap_id: str, part: integer, offset: integer, limit: integer, query: str, render_page: integer}, ['gap_id'], read);
  register('research_record_evidence_use', '根据实际读取的 receipt_id 记录采用范围、相关输入、报告章节或未解决原因。此记录是研究者判断，不是事实验证通过。',
    {gap_id: str, receipt_id: str, disposition: {type: 'string', enum: ['used_for_scope', 'used_partial', 'unresolved', 'rejected', 'not_used']},
      affected_input: str, scope: str, reason: str, report_section: str},
    ['gap_id', 'receipt_id', 'disposition', 'affected_input', 'scope', 'reason'], review);
  ctx.on('tools/post-execute', async (exec, result, next) => {
    const wasDispatched = dispatched.delete(exec.callId);
    const downstream = await next();
    if (!wasDispatched || internal.has(exec.callId) || !['web_fetch', AK].includes(exec.name) || downstream.kind !== 'accept'
        || Object.hasOwn(downstream, 'value') || exec.signal?.aborted || precheck(exec.name, exec.arguments).length) return downstream;
    let id, category, args, trigger, auto = false, g;
    if (exec.name === 'web_fetch') {
      const report = inspect(exec.name, exec.arguments, result, {asOf: config.asOf});
      const pdf = /\.pdf$/i.test(new URL(exec.arguments.url).pathname)
        || (result.isError && /application\/pdf|PDF/.test(JSON.stringify(result.content ?? [])));
      if (!pdf && !report.issues.some(x => ['body_truncated', 'html_no_visible_body'].includes(x.code))) return downstream;
      trigger = pdf ? 'pdf' : 'web_truncated_or_empty';
      category = 'document'; args = {url: normalizedURL(exec.arguments.url)}; id = hash(canonical({category, ...args}));
    } else {
      const report = inspect(exec.name, exec.arguments, result, {asOf: config.asOf});
      if (report.status === 'rejected' || !['partial', 'complete_observed'].includes(report.observed.coverage)) return downstream;
      category = 'pagination'; args = {name: exec.arguments.name, params: exec.arguments.params ?? {}};
      trigger = 'pagination_incomplete';
      id = hash(canonical({category, ...args}));
      if (report.observed.coverage === 'complete_observed' && !gaps.has(id)) return downstream;
    }
    try {
      await locked(id, async () => {
        g = await get(id, category, args); g.state.observations++;
        g.state.triggers = [...new Set([...(g.state.triggers ?? []), trigger])];
        if (category === 'pagination') await ingest(g, exec.arguments, result);
        if (!g.state.auto_scheduled && !['retrieved', 'conflict'].includes(g.state.retrieval_status)) {
          g.state.auto_scheduled = true; auto = true;
        } else if (g.state.auto_scheduled) g.state.deduplicated_requests++;
        await save(g, 'gap_observed');
      });
      let nested;
      if (auto) nested = await dispatch('research_recover_evidence', {gap_id: id}, exec);
      if (nested?.isError && g.state.retrieval_status === 'detected') await locked(id, async () => {
        g.state.retrieval_status = 'blocked'; g.state.remaining_issue = 'recovery_dispatch_failed';
        await save(g, 'recovery_dispatch_failed');
      });
      const note = text({recovery: snapshot(g), dispatch_failed: nested?.isError === true})[0];
      const contexts = [...downstream.additionalContexts ?? [], ...nested?.additionalContexts ?? []];
      if (exec.parent !== undefined) contexts.push({id: randomUUID(), role: 'user', source: {kind: 'tool', callId: exec.callId}, content: [note]});
      return {...downstream, content: [note, ...(downstream.content ?? result.content)], additionalContexts: contexts};
    } catch {
      const note = text('补证状态保存或执行失败；原始体检仍有效，缺口保持未解决。')[0];
      const contexts = [...downstream.additionalContexts ?? []];
      if (exec.parent !== undefined) contexts.push({id: randomUUID(), role: 'user', source: {kind: 'tool', callId: exec.callId}, content: [note]});
      return {...downstream, content: [note, ...(downstream.content ?? result.content)], additionalContexts: contexts};
    }
  });
}
