/** Durable source locators and exact citations, independent of conversation summaries. */
import * as fs from 'node:fs/promises';
import {constants} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash, randomUUID} from 'node:crypto';

export const name = 'research-evidence-context';
export const inject = ['tools', 'systemPrompt'];
export const VERSION = 'evidence-context-v1';
const MAX_BYTES = 32 * 1024 * 1024;
const canonical = v => JSON.stringify(v, (k, x) => x && typeof x === 'object' && !Array.isArray(x)
  ? Object.fromEntries(Object.keys(x).sort().map(key => [key, x[key]])) : x);
const hash = value => createHash('sha256').update(value).digest('hex');
const validId = (id, prefix) => typeof id === 'string' && new RegExp(`^${prefix}-[a-f0-9]{64}$`).test(id);
const blocks = value => [{type: 'text', text: typeof value === 'string' ? value : JSON.stringify(value)}];
const urlOf = value => {
  const url = new URL(value);
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) throw new Error('invalid_source_url');
  url.hash = ''; return url.href;
};
const checkAbort = signal => { if (signal?.aborted) throw new Error('cancelled'); };

function indentColumn(whitespace, column = 0) {
  for (const char of whitespace) column += char === '\t' ? 4 - column % 4 : 1;
  return column;
}

// Preserve offsets while excluding code examples and non-citation comments.
function narrativeOnly(report) {
  const listIndents = [];
  let fence = null;
  let visible = report.split(/(?<=\n)/).map(line => {
    if (!line.trim()) return line;
    const leading = /^[ \t]*/.exec(line)[0];
    let column = indentColumn(leading);
    let content = line.slice(leading.length);
    while (listIndents.length && column < listIndents.at(-1)) listIndents.pop();
    if (fence && listIndents.length < fence.depth) fence = null;

    if (fence) {
      const marker = column - (listIndents.at(-1) ?? 0) < 4 && /^(`{3,}|~{3,})(.*)/.exec(content);
      if (marker && marker[1][0] === fence.char && marker[1].length >= fence.length && !marker[2].trim()) fence = null;
      return ' '.repeat(line.length);
    }

    // List markers establish content columns. Four columns beyond the active
    // item still introduce indented code, even when the sample starts with '-'.
    while (column - (listIndents.at(-1) ?? 0) < 4) {
      if (/^(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})\r?$/.test(content.trimEnd())) break;
      const item = /^([-+*]|\d{1,9}[.)])([ \t]+|(?=\r?\n?$))/.exec(content);
      if (!item) break;
      const markerEnd = column + item[1].length;
      column = indentColumn(item[2], markerEnd);
      const padding = column - markerEnd;
      listIndents.push(markerEnd + (padding >= 1 && padding <= 4 ? padding : 1));
      content = content.slice(item[0].length);
      if (!content.trim()) return line;
    }
    const relativeIndent = column - (listIndents.at(-1) ?? 0);
    if (relativeIndent >= 4) return ' '.repeat(line.length);
    const marker = /^(`{3,}|~{3,})(.*)/.exec(content);
    if (!marker) return line;
    fence = {char: marker[1][0], length: marker[1].length, depth: listIndents.length};
    return ' '.repeat(line.length);
  }).join('');
  visible = visible.replace(/(?<!\\)(`+)([\s\S]*?)\1(?!`)/g, m => ' '.repeat(m.length));
  return visible.replace(/(?<!\\)<!--(?!\s*evidence-cite:)[\s\S]*?(?:-->|$)/g, m => ' '.repeat(m.length));
}

async function safeDir(directory) {
  const stat = await fs.lstat(directory);
  if (!stat.isDirectory() || stat.isSymbolicLink() || await fs.realpath(directory) !== directory) throw new Error('unsafe_evidence_directory');
}
async function readBounded(root, file, expected) {
  await safeDir(root);
  if (typeof file !== 'string' || path.isAbsolute(file) || file.split('/').some(x => !x || ['..', '.'].includes(x))) throw new Error('unsafe_evidence_path');
  const target = path.join(root, file);
  await safeDir(path.dirname(target));
  const fd = await fs.open(target, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const st = await fd.stat();
    if (!st.isFile() || st.size > MAX_BYTES) throw new Error('invalid_evidence_file');
    const raw = await fd.readFile();
    if (expected && hash(raw) !== expected) throw new Error('source_changed');
    return raw;
  } finally { await fd.close(); }
}
async function immutable(root, file, raw) {
  await safeDir(root); await safeDir(path.dirname(path.join(root, file)));
  let fd;
  try { fd = await fs.open(path.join(root, file), constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW, 0o600); }
  catch (error) {
    if (error.code !== 'EEXIST') throw error;
    if (!(await readBounded(root, file)).equals(Buffer.from(raw))) throw new Error('immutable_record_conflict');
    return;
  }
  try { await fd.writeFile(raw); } finally { await fd.close(); }
}

export class EvidenceStore {
  constructor(config) {
    this.config = config;
    this.sources = new Map(); this.anchors = new Map(); this.pins = new Map(); this.citations = new Map();
    this.errors = []; this.pinRecords = 0;
  }
  async init() {
    for (const key of ['directory', 'recoveryDirectory']) if (!path.isAbsolute(this.config[key])) throw new Error('invalid_context_directory');
    if (!/^\d{4}-\d{2}-\d{2}$/.test(this.config.asOf)) throw new Error('invalid_context_cutoff');
    await safeDir(this.config.directory); await safeDir(this.config.recoveryDirectory);
    for (const category of ['sources', 'anchors', 'pins', 'citations', 'blobs', 'events']) {
      const dir = path.join(this.config.directory, category);
      await fs.mkdir(dir, {recursive: true}); await safeDir(dir);
      if (category === 'blobs') continue;
      const files = (await fs.readdir(dir)).filter(x => x.endsWith('.json')).sort();
      if (category === 'events') {
        if (files.length > 8192) throw new Error('context_event_limit');
        for (const file of files) {
          const event = JSON.parse(await readBounded(this.config.directory, `${category}/${file}`));
          if (event.kind === 'indexing_failed') this.errors.push('source_indexing_failed');
        }
        this.errors = this.errors.slice(-20); continue;
      }
      if (files.length > (category === 'pins' ? 512 : 1024)) throw new Error('context_record_limit');
      for (const file of files) {
        const record = JSON.parse(await readBounded(this.config.directory, `${category}/${file}`));
        const prefix = {sources: 's', anchors: 'e', pins: 'p', citations: 'c'}[category];
        if (file !== `${record.id}.json` || record.id !== `${prefix}-${hash(canonical(record.data))}`
            || record.data.as_of !== this.config.asOf) throw new Error('context_record_changed');
        if (category === 'pins') {
          this.pinRecords++;
          if (!validId(record.data.evidence_id, 'e') || !Number.isSafeInteger(record.data.revision) || record.data.revision < 1) throw new Error('invalid_pin_revision');
          const previous = this.pins.get(record.data.evidence_id);
          if (!previous || record.data.revision > previous.data.revision) this.pins.set(record.data.evidence_id, record);
          else if (record.data.revision === previous.data.revision && record.id !== previous.id) throw new Error('conflicting_pin_revision');
        } else this[category].set(record.id, record);
      }
    }
    return this;
  }
  async put(category, prefix, data) {
    data = {...data, as_of: this.config.asOf};
    const id = `${prefix}-${hash(canonical(data))}`;
    const limit = {sources: 128, anchors: 512, citations: 512}[category];
    if (limit && !this[category].has(id) && this[category].size >= limit) throw new Error('context_record_limit');
    const record = {id, data};
    if (category === 'pins' && this.pinRecords >= 512) throw new Error('pin_revision_limit');
    await immutable(this.config.directory, `${category}/${id}.json`, JSON.stringify(record, null, 2) + '\n');
    if (category === 'pins') this.pinRecords++;
    if (category !== 'pins') this[category].set(id, record);
    return record;
  }
  async event(kind, details = {}) {
    const record = {schema_version: 'research-evidence-context-event/v1', kind, at: new Date().toISOString(), ...details};
    await immutable(this.config.directory, `events/${randomUUID()}.json`, JSON.stringify(record) + '\n');
  }
  async verify(source) {
    if (!source || source.id !== `s-${hash(canonical(source.data))}`) throw new Error('unknown_source');
    const root = source.data.area === 'recovery' ? this.config.recoveryDirectory : this.config.directory;
    for (const record of source.data.bindings) await readBounded(root, record.file, record.sha256);
    return root;
  }
  async registerWeb(args, value) {
    if (!value || value.statusCode < 200 || value.statusCode >= 300 || typeof value.truncated !== 'boolean'
        || !['html', 'text'].includes(value.body?.kind) || typeof value.body.content !== 'string' || !value.body.content.trim()) return;
    const content = value.body.content, raw = canonical(value) + '\n';
    if (Buffer.byteLength(content) > MAX_BYTES || Buffer.byteLength(raw) > MAX_BYTES) throw new Error('source_size_limit');
    const rawFile = `blobs/${hash(raw)}.json`, textFile = `blobs/${hash(content)}.txt`;
    await immutable(this.config.directory, rawFile, raw); await immutable(this.config.directory, textFile, content);
    return this.put('sources', 's', {area: 'context', kind: value.body.kind === 'html' ? 'raw_html' : 'text',
      url: urlOf(args.url), gap_id: null, transport_truncated: value.truncated,
      warnings: value.truncated ? ['source_response_truncated'] : [],
      bindings: [{file: rawFile, sha256: hash(raw)}], parts: [{part: 1, file: textFile, sha256: hash(content)}]});
  }
  async registerRecovery(gapId) {
    if (!/^[a-f0-9]{64}$/.test(gapId)) throw new Error('invalid_gap_id');
    const dir = path.join(this.config.recoveryDirectory, gapId); await safeDir(dir);
    const files = (await fs.readdir(dir)).filter(x => /^event-\d{6}\.json$/.test(x)).sort();
    if (!files.length) return;
    const state = JSON.parse(await readBounded(this.config.recoveryDirectory, `${gapId}/${files.at(-1)}`));
    if (state.gap_id !== gapId || state.valuation_cutoff !== this.config.asOf || state.category !== 'document' || !state.document) return;
    if (!/^document-[1-3]$/.test(state.document_directory)) throw new Error('invalid_document_directory');
    const base = `${gapId}/${state.document_directory}/`;
    const manifestRaw = await readBounded(this.config.recoveryDirectory, base + state.document_manifest.file, state.document_manifest.sha256);
    const doc = JSON.parse(manifestRaw);
    if (canonical(doc) !== canonical(state.document) || !Array.isArray(doc.parts)) throw new Error('document_manifest_changed');
    const data = {area: 'recovery', kind: doc.kind, url: urlOf(doc.requested_url ?? state.request.url),
      gap_id: gapId, transport_truncated: false, warnings: doc.warnings,
      bindings: [{file: base + state.document_manifest.file, sha256: hash(manifestRaw)}, {file: base + doc.raw.file, sha256: doc.raw.sha256}],
      parts: doc.parts.map(p => ({part: p.index, file: base + p.file, sha256: p.sha256})), as_of: this.config.asOf};
    await this.verify({id: `s-${hash(canonical(data))}`, data});
    return this.put('sources', 's', data);
  }
  async syncRecovery() {
    const gaps = (await fs.readdir(this.config.recoveryDirectory)).filter(x => /^[a-f0-9]{64}$/.test(x));
    if (gaps.length > 128) throw new Error('recovery_index_limit');
    for (const gap of gaps) await this.registerRecovery(gap);
  }
  async text(source, part) {
    const root = await this.verify(source);
    const record = source.data.parts.find(p => p.part === part);
    if (!record) throw new Error('unknown_source_part');
    return (await readBounded(root, record.file, record.sha256)).toString('utf8');
  }
  catalog({source_id, query = '', offset = 0, limit = 10, evidence_offset = 0} = {}) {
    if (!Number.isInteger(offset) || offset < 0 || !Number.isInteger(limit) || limit < 1 || limit > 30
        || !Number.isInteger(evidence_offset) || evidence_offset < 0
        || typeof query !== 'string' || query.length > 200) throw new Error('invalid_catalog_query');
    if (evidence_offset && !source_id) throw new Error('evidence_offset_requires_source');
    if (source_id && !this.sources.has(source_id)) throw new Error('unknown_source');
    const sources = source_id ? [this.sources.get(source_id)] : [...this.sources.values()];
    const entries = sources.map(s => ({source_id: s.id, kind: s.data.kind, url: s.data.url,
      parts: s.data.parts.length, truncated: s.data.transport_truncated, warnings: s.data.warnings,
      evidence: [...this.anchors.values()].filter(a => a.data.source_id === s.id).map(a => ({evidence_id: a.id,
        locator: a.data.locator, pin: this.pins.get(a.id)?.data ?? null}))}));
    const matches = query ? entries.filter(x => canonical(x).toLowerCase().includes(query.toLowerCase())) : entries;
    let shownEvidence = 0;
    const selected = matches.slice(offset, offset + limit).map(x => {
      const evidence = query ? x.evidence.filter(a => canonical(a).toLowerCase().includes(query.toLowerCase())) : x.evidence;
      const selected = evidence.slice(evidence_offset, evidence_offset + Math.max(0, 12 - shownEvidence)); shownEvidence += selected.length;
      return {...x, url: x.url.slice(0, 300), url_shortened: x.url.length > 300,
        evidence: selected.map(a => ({evidence_id: a.evidence_id, locator: a.locator,
          label: a.pin?.annotations.label ?? null, stance: a.pin?.stance ?? null, required_citation: a.pin?.required_citation ?? null})),
        evidence_total: x.evidence.length, evidence_matches: evidence.length, evidence_omitted: evidence.length - selected.length,
        evidence_offset, evidence_next_offset: evidence_offset + selected.length < evidence.length ? evidence_offset + selected.length : null};
    });
    return {total: matches.length, entries: selected, next_offset: offset + limit < matches.length ? offset + limit : null,
      index_errors: this.errors, fact_verification: 'not_performed'};
  }
  async find({source_id, query, part = 1, offset = 0}, signal) {
    if (typeof query !== 'string' || !query.trim() || query.length > 200 || !Number.isInteger(offset) || offset < 0
        || !Number.isInteger(part) || part < 1) throw new Error('invalid_source_query');
    const source = this.sources.get(source_id), matches = [];
    if (!source) throw new Error('unknown_source');
    const root = await this.verify(source);
    if (!source.data.parts.some(p => p.part === part)) throw new Error('unknown_source_part');
    const parts = source.data.parts.filter(p => p.part >= part);
    let next_search = null;
    for (let i = 0; i < parts.length; i++) {
      const p = parts[i];
      checkAbort(signal);
      const text = (await readBounded(root, p.file, p.sha256)).toString('utf8');
      let pos = text.indexOf(query, p.part === part ? offset : 0);
      while (pos >= 0 && matches.length < 20) {
        matches.push({part: p.part, offset: Math.max(0, pos - 160), match_offset: pos, snippet: text.slice(Math.max(0, pos - 80), pos + query.length + 120)});
        pos = text.indexOf(query, pos + query.length);
      }
      if (matches.length >= 20) {
        next_search = pos >= 0 ? {part: p.part, offset: pos} : parts[i + 1] ? {part: parts[i + 1].part, offset: 0} : null;
        break;
      }
    }
    return {source_id, matches, capped: next_search !== null, next_search,
      note: '搜索只定位；用next_search续查后续页/片段，用research_open_evidence读取原文及相邻附注。'};
  }
  async open(args, signal, eventKind) {
    checkAbort(signal);
    let source, locator, anchor;
    if (args.evidence_id) {
      anchor = this.anchors.get(args.evidence_id); if (!anchor) throw new Error('unknown_evidence');
      source = this.sources.get(anchor.data.source_id); locator = anchor.data.locator;
    } else {
      source = this.sources.get(args.source_id);
      const start = args.offset ?? 0, length = args.limit ?? 2400;
      if (!Number.isSafeInteger(start) || start < 0 || !Number.isSafeInteger(length) || length < 1 || length > 4000) throw new Error('invalid_read_range');
      locator = {part: args.part ?? 1, start, end: start + length};
    }
    const original = await this.text(source, locator.part);
    const content = original.slice(locator.start, locator.end);
    if (!content) throw new Error('empty_or_scanned_source_range');
    locator = {...locator, end: locator.start + content.length};
    if (anchor && (hash(content) !== anchor.data.excerpt_sha256 || canonical(locator) !== canonical(anchor.data.locator))) throw new Error('evidence_changed');
    if (!anchor) {
      anchor = await this.put('anchors', 'e', {source_id: source.id, locator, excerpt_sha256: hash(content)});
    }
    await this.event(eventKind ?? (args.evidence_id ? 'reopened' : 'opened'), {evidence_id: anchor.id});
    return {evidence_id: anchor.id, source_id: source.id, url: source.data.url, kind: source.data.kind, locator,
      pdf_page: source.data.kind === 'pdf' ? locator.part : null, next_offset: locator.end < original.length ? locator.end : null,
      warnings: source.data.warnings, content, pin: this.pins.get(anchor.id)?.data ?? null, fact_verification: 'not_performed'};
  }
  async pin(args) {
    const anchor = this.anchors.get(args.evidence_id);
    if (!anchor) throw new Error('read_evidence_before_pinning');
    for (const key of ['label', 'subject', 'period', 'currency', 'unit', 'disclosed_at', 'note']) {
      if (args[key] !== undefined && args[key] !== null && (typeof args[key] !== 'string' || args[key].length > (key === 'note' ? 400 : 120))) throw new Error('invalid_pin_annotation');
    }
    if (!args.label?.trim() || !args.note?.trim() || !['support', 'counterevidence', 'unresolved', 'rejected'].includes(args.stance)) throw new Error('pin_requires_scope_and_stance');
    if (!this.pins.has(anchor.id) && this.pins.size >= 32) throw new Error('pin_limit');
    await this.open({evidence_id: anchor.id}, undefined, 'pin_source_checked');
    const previous = this.pins.get(anchor.id);
    const data = {evidence_id: anchor.id, revision: (previous?.data.revision ?? 0) + 1,
      required_citation: args.required_citation !== false, stance: args.stance,
      annotations: Object.fromEntries(['label', 'subject', 'period', 'currency', 'unit', 'disclosed_at', 'note'].map(k => [k, args[k] ?? null])),
      annotation_author: 'research_agent', fact_verification: 'not_performed'};
    const record = await this.put('pins', 'p', data); this.pins.set(anchor.id, record);
    return record;
  }
  context() {
    let output = `投研证据定位簿（估值截止 ${this.config.asOf}）：${this.sources.size}个来源，${this.anchors.size}个读取锚点，${this.pins.size}个关键标记。\n`
      + '原文保存在对话之外；裁剪或摘要不能替代原文。忘记ID时调用 research_find_evidence；有ID时 research_open_evidence(evidence_id) 重读，research_cite_evidence 生成原文引用。单位、期间、主体和披露日未知仍为未知。以下标注来自研究者，不是已验证事实。\n';
    const pins = [...this.pins.values()].sort((a, b) => Number(['unresolved', 'rejected'].includes(b.data.stance)) - Number(['unresolved', 'rejected'].includes(a.data.stance)) || a.id.localeCompare(b.id));
    let shown = 0;
    for (const pin of pins) {
      const {note, ...annotations} = pin.data.annotations;
      const line = canonical({evidence_id: pin.data.evidence_id, stance: pin.data.stance, required_citation: pin.data.required_citation, annotations}) + '\n';
      if (output.length + line.length > 3300 || shown >= 6) break;
      output += line; shown++;
    }
    output += `已显示${shown}个，另有${pins.length - shown}个在完整索引中；未显示不表示已解决。索引异常：${this.errors.length}。`;
    return output;
  }
  async cite({evidence_id, quote = ''}) {
    if (typeof quote !== 'string' || quote.length > 500 || /[\r\n]/.test(quote)) throw new Error('quote_must_be_one_short_exact_span');
    if (this.pins.get(evidence_id)?.data.stance === 'rejected') throw new Error('rejected_evidence_cannot_support_citation');
    const read = await this.open({evidence_id}, undefined, 'citation_source_checked');
    if (quote && !read.content.includes(quote)) throw new Error('quote_not_in_original_span');
    const url = new URL(read.url); if (read.pdf_page) url.hash = `page=${read.pdf_page}`;
    const label = read.pdf_page ? `原文，第${read.pdf_page}页` : `原文，定位${read.locator.start}–${read.locator.end}`;
    const record = await this.put('citations', 'c', {evidence_id, url: url.href, label, quote});
    return {citation_id: record.id, evidence_id, markdown: this.markdown(record), locator: read.locator,
      note: '引用核验仅证明链接、位置及所引文字对应保存的原文；不能证明推论或原始披露真实。'};
  }
  markdown(record) {
    const q = record.data.quote.replace(/[\\`*_{}\[\]<>]/g, '\\$&');
    return `${q ? `“${q}” ` : ''}[${record.data.label}](<${record.data.url}>)<!-- evidence-cite:${record.id} -->`;
  }
  async checkCitations(report) {
    if (typeof report !== 'string' || Buffer.byteLength(report) > 8 * 1024 * 1024) throw new Error('invalid_report_text');
    // Code samples are not citations in the report's narrative.
    const visible = narrativeOnly(report);
    const markers = [...visible.matchAll(/<!--\s*evidence-cite:([^\s>]+)\s*-->/g)];
    if (markers.length > 512) throw new Error('citation_limit');
    const issues = [], cited = new Set();
    for (const match of markers) {
      const record = this.citations.get(match[1]);
      if (!record) { issues.push({code: 'unknown_citation', citation_id: match[1].slice(0, 100)}); continue; }
      const expected = this.markdown(record), end = match.index + match[0].length;
      if (visible.slice(end - expected.length, end) !== expected) { issues.push({code: 'citation_text_or_locator_changed', citation_id: record.id}); continue; }
      try {
        if (this.pins.get(record.data.evidence_id)?.data.stance === 'rejected') throw new Error('rejected_evidence');
        const source = await this.open({evidence_id: record.data.evidence_id}, undefined, 'audit_source_checked');
        if (record.data.quote && !source.content.includes(record.data.quote)) throw new Error('quote_changed');
        cited.add(record.data.evidence_id);
      } catch { issues.push({code: 'citation_source_unavailable_or_changed', citation_id: record.id}); }
    }
    for (const pin of this.pins.values()) if (pin.data.required_citation && pin.data.stance !== 'rejected' && !cited.has(pin.data.evidence_id))
      issues.push({code: 'required_evidence_not_cited', evidence_id: pin.data.evidence_id});
    return {schema_version: 'research-evidence-citations/v1', status: issues.length ? 'failed' : markers.length ? 'mechanical_pass' : 'not_exercised',
      report_sha256: hash(report), citation_markers: markers.length, verified_evidence: cited.size,
      required_evidence: [...this.pins.values()].filter(p => p.data.required_citation && p.data.stance !== 'rejected').length,
      issues, semantic_verification: 'not_performed'};
  }
}

export async function apply(ctx, config) {
  const store = await new EvidenceStore(config).init();
  let pending = Promise.resolve();
  const serial = task => {
    const current = pending.then(task);
    pending = current.then(() => undefined, () => undefined);
    return current;
  };
  const enqueue = task => {
    pending = serial(task).catch(async () => {
      store.errors.push('source_indexing_failed'); store.errors = store.errors.slice(-20);
      try { await store.event('indexing_failed'); } catch { /* Runtime context retains the explicit error. */ }
    });
  };
  // Final outcomes only: pre-policy denial and post-policy blocking/replacement
  // must not be reconstructed from an earlier unapproved result.
  ctx.on('tools/result', (exec, result) => {
    if (exec.name === 'web_fetch') enqueue(async () => {
      if (result.isError === false) await store.registerWeb(exec.arguments, result.value);
      // An independently authorized recovery may have succeeded even though
      // native web_fetch could not read a PDF. Never copy its failed value.
      await store.syncRecovery();
    });
    if (result.isError !== false) return;
    if (['research_recover_evidence', 'research_read_evidence'].includes(exec.name) && /^[a-f0-9]{64}$/.test(result.value?.gap_id))
      enqueue(() => store.registerRecovery(result.value.gap_id));
  });
  ctx.systemPrompt.context({name: 'research-evidence-locators', order: 9500, required: true, interpolate: false, text: () => store.context()});
  ctx.on('system-prompt/assemble', async (assembly, context, next) => {
    await pending;
    return ctx.systemPrompt.refreshContext(await next(), context);
  });
  const register = (toolName, description, properties, required, handler) => ctx.tools.register({name: toolName, description,
    parameters: {type: 'object', properties, required, additionalProperties: false},
    output: {schema: {}, render: (args, value) => blocks(value)}, execute: async (args, exec) => {
      return serial(() => { checkAbort(exec.signal); return handler(args, exec); });
    }});
  const str = {type: 'string'}, int = {type: 'integer'};
  register('research_find_evidence', '压缩后从持久索引找来源/关键证据；仅给source_id可列该来源的锚点，按evidence_next_offset传evidence_offset续查；给source_id和query时搜索原文，搜索不代表已读。',
    {source_id: str, query: str, part: int, offset: int, limit: int, evidence_offset: int}, [],
    (args, exec) => args.source_id && args.query ? store.find(args, exec.signal) : store.catalog(args));
  register('research_open_evidence', '按source_id及页/字符范围读取原文并创建稳定evidence_id，或用evidence_id核哈希重读原片段。最长4000字符。',
    {source_id: str, evidence_id: str, part: int, offset: int, limit: int}, [], (args, exec) => store.open(args, exec.signal));
  register('research_pin_evidence', '标记关键投研证据，保留主体/期间/币种/单位/披露日及支持、反证、未决、拒绝状态。未知字段留空。默认要求最终报告引用；不采用时明确说明并设required_citation=false。',
    {evidence_id: str, label: str, subject: str, period: str, currency: str, unit: str, disclosed_at: str, note: str,
      stance: {type: 'string', enum: ['support', 'counterevidence', 'unresolved', 'rejected']}, required_citation: {type: 'boolean'}},
    ['evidence_id', 'label', 'stance', 'note'], args => store.pin(args));
  register('research_cite_evidence', '重读并生成可验的原文引用。可附一段不超过500字符的单行逐字quote；须照用返回的markdown（含隐藏标记）。',
    {evidence_id: str, quote: str}, ['evidence_id'], args => store.cite(args));
  register('research_check_citations', '检查报告文本中的证据引用、原文哈希及关键证据漏引；不检验经济推论。',
    {report: str}, ['report'], args => store.checkCitations(args.report));
}

// The production adapter runs this same frozen implementation against the final
// staged report. No DSH services, provider credentials or network are involved.
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href && process.argv[2] === '--check-citations') {
  try {
    // A pipe can split a Chinese character between buffers; decode as a stream.
    process.stdin.setEncoding('utf8');
    let raw = ''; for await (const chunk of process.stdin) { raw += chunk; if (Buffer.byteLength(raw) > 10 * 1024 * 1024) throw new Error('audit_input_limit'); }
    const request = JSON.parse(raw);
    const result = await (await new EvidenceStore(request.config).init()).checkCitations(request.report);
    process.stdout.write(JSON.stringify(result) + '\n');
  } catch { process.stderr.write('Evidence citation audit unavailable or evidence changed.\n'); process.exitCode = 1; }
}
