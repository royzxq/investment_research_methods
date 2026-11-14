/** Deterministic retrieval checks for the pinned DSH tool protocol.
 * No network, data correction, investment decisions, or semantic pass claims.
 * Raw canonical results are retained separately from model-facing feedback.
 */
import {createHash, randomUUID} from 'node:crypto';
import {constants} from 'node:fs';
import * as fs from 'node:fs/promises';
import path from 'node:path';

export const name = 'research-data-health';
export const inject = ['tools'];
export const VERSION = 'data-health-v1';
const AK = 'mcp__aktools__get_data';
const FINANCIAL = new Set(['stock_profit_sheet_by_report_em', 'stock_financial_hk_report_em']);
const PLACEHOLDERS = new Set(['', '--', '—', 'N/A', 'null', 'NULL', 'None', 'NaN', 'nan', '未知企业', '暂无公司详细介绍']);
const MAX_RAW_BYTES = 16 * 1024 * 1024;
const MAX_TRACKED_ROWS = 100000;
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const missing = x => x === null || x === undefined || (typeof x === 'string' && PLACEHOLDERS.has(x.trim()));
const hash = x => createHash('sha256').update(x).digest('hex');
const canonical = x => JSON.stringify(x, function(k, v) {
  return object(v) ? Object.fromEntries(Object.keys(v).sort().map(key => [key, v[key]])) : v;
});
const relevant = exec => exec.name === 'web_fetch' || exec.name === AK;
const issue = (list, code, severity = 'review') => list.push({code, severity});

export function isoDay(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}(?:$|[ T])/.test(value)) return null;
  const day = value.slice(0, 10);
  const date = new Date(day + 'T00:00:00Z');
  return Number.isNaN(date.valueOf()) || date.toISOString().slice(0, 10) !== day ? null : day;
}

function security(value) {
  if (typeof value !== 'string') return null; // Never repair lost leading zeroes.
  const v = value.toUpperCase();
  let m = /^(SH|SZ)(\d{6})$/.exec(v);
  if (m) return {code: m[2], market: m[1]};
  m = /^(\d{6})\.(SH|SZ)$/.exec(v) || /^(\d{5})\.(HK)$/.exec(v);
  if (m) return {code: m[1], market: m[2]};
  if (/^\d{5,6}$/.test(v)) return {code: v, market: v.length === 5 ? 'HK' : null};
  return null;
}

export function precheck(tool, args) {
  const issues = [];
  if (!object(args)) { issue(issues, 'arguments_invalid', 'reject'); return issues; }
  if (tool === 'web_fetch') {
    try {
      const url = new URL(args.url);
      if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password) throw new Error();
    } catch { issue(issues, 'url_invalid', 'reject'); }
  } else if (tool === AK) {
    if (typeof args.name !== 'string' || !args.name.trim() || !object(args.params ?? {}))
      issue(issues, 'interface_or_params_invalid', 'reject');
    for (const [key, low, high] of [['offset', Number.MIN_SAFE_INTEGER, Number.MAX_SAFE_INTEGER], ['max_rows', 1, 1000]]) {
      if (args[key] !== undefined && (!Number.isSafeInteger(args[key]) || args[key] < low || args[key] > high))
        issue(issues, key + '_invalid', 'reject');
    }
    if (FINANCIAL.has(args.name)) {
      const input = args.name === 'stock_financial_hk_report_em' ? args.params?.stock : args.params?.symbol;
      const parsed = security(input);
      if (!parsed || (args.name === 'stock_financial_hk_report_em'
        ? parsed.market !== 'HK' : !['SH', 'SZ'].includes(parsed.market)))
        issue(issues, 'security_identity_ambiguous', 'reject');
    }
  }
  return issues;
}

function webCheck(value, issues, observed) {
  if (!object(value) || !Number.isInteger(value.statusCode) || !object(value.body)
      || !['html', 'text'].includes(value.body.kind) || typeof value.body.content !== 'string'
      || typeof value.truncated !== 'boolean') {
    issue(issues, 'web_envelope_invalid', 'reject'); return;
  }
  observed.http_status = value.statusCode;
  observed.body_chars = value.body.content.length;
  observed.truncated = value.truncated;
  if (value.statusCode < 200 || value.statusCode >= 300) issue(issues, 'http_unsuccessful', 'reject');
  if (!value.body.content.trim()) issue(issues, 'body_empty', 'reject');
  if (value.truncated) issue(issues, 'body_truncated');
  if (value.body.kind === 'html') {
    // A conservative diagnostic only: this is not a general HTML extractor.
    const visible = value.body.content
      .replace(/<!--(?:[\s\S]*?-->|[\s\S]*$)/g, '')
      .replace(/<(script|style|nav|header|footer|head)\b[^>]*>[\s\S]*?(?:<\/\1\s*>|$)/gi, '')
      .replace(/<[^>]*(?:>|$)/g, ' ').replace(/&(?:nbsp|#160);/gi, ' ').trim();
    observed.visible_chars_estimate = visible.length;
    if (!visible) issue(issues, 'html_no_visible_body');
    else if (visible.length < 120) issue(issues, 'html_short_body_review');
  }
  // Subject, disclosure date, relevance and substantive completeness are semantic checks.
  observed.semantic_verification = 'pending';
}

function payload(value) {
  if (!object(value)) return null;
  const structured = value.structuredContent?.result ?? value.structuredContent;
  const text = Array.isArray(value.content) ? value.content.filter(x => x?.type === 'text') : null;
  if (!Array.isArray(text) || text.length !== 1) return null;
  try {
    const parsed = JSON.parse(text[0].text);
    if (structured !== undefined && canonical(structured) !== canonical(parsed)) return null;
    return structured !== undefined ? structured : parsed;
  } catch { return null; }
}

/** Per-process, per-interface+parameters coverage. It is not a freshness guarantee. */
export class Coverage {
  groups = new Map();
  check(args, data, issues) {
    const key = canonical({name: args.name, params: args.params ?? {}});
    if (!this.groups.has(key)) {
      if (this.groups.size >= 256) { issue(issues, 'coverage_tracking_limit'); return 'unknown'; }
      this.groups.set(key, {total: data.total_rows, rows: new Map(), fingerprints: new Map(), conflict: false});
    }
    const group = this.groups.get(key);
    if (group.total !== data.total_rows) group.conflict = true;
    if (group.rows.size + data.rows.length > MAX_TRACKED_ROWS) {
      issue(issues, 'coverage_tracking_limit'); return 'unknown';
    }
    for (let i = 0; i < data.rows.length; i++) {
      const pos = data.offset + i, fingerprint = hash(canonical(data.rows[i]));
      if (group.rows.has(pos) && group.rows.get(pos) !== fingerprint) group.conflict = true;
      if (group.fingerprints.has(fingerprint) && group.fingerprints.get(fingerprint) !== pos) group.conflict = true;
      group.rows.set(pos, fingerprint);
      group.fingerprints.set(fingerprint, pos);
    }
    if (group.conflict) { issue(issues, 'pagination_conflict'); return 'conflict'; }
    if (group.rows.size === group.total && group.total > 0) return 'complete_observed';
    issue(issues, group.total === 0 ? 'empty_result_not_absence' : 'pagination_incomplete');
    return group.total === 0 ? 'empty' : 'partial';
  }
}

function tableCheck(args, value, asOf, coverage, issues, observed) {
  const data = payload(value);
  if (!object(data) || !Array.isArray(data.rows) || !Array.isArray(data.columns)
      || data.columns.some(x => typeof x !== 'string') || new Set(data.columns).size !== data.columns.length
      || data.rows.some(x => !object(x)) || typeof data.truncated !== 'boolean'
      || !['total_rows', 'offset', 'returned_rows'].every(k => Number.isSafeInteger(data[k]) && data[k] >= 0)) {
    issue(issues, 'table_envelope_invalid', 'reject'); return;
  }
  observed.total_rows = data.total_rows;
  observed.returned_rows = data.returned_rows;
  observed.offset = data.offset;
  if (data.name !== args.name) issue(issues, 'interface_mismatch', 'reject');
  const requestedOffset = args.offset ?? 0;
  const expectedOffset = requestedOffset < 0 ? Math.max(data.total_rows + requestedOffset, 0)
    : Math.min(requestedOffset, data.total_rows);
  if (data.offset !== expectedOffset || data.returned_rows !== data.rows.length
      || data.returned_rows > (args.max_rows ?? 100) || data.offset + data.returned_rows > data.total_rows
      || data.rows.some(row => data.columns.some(col => !Object.hasOwn(row, col))))
    issue(issues, 'pagination_or_columns_invalid', 'reject');
  if (!data.rows.length && data.total_rows > data.offset) issue(issues, 'pagination_no_progress', 'reject');
  if (data.rows.some(row => Object.values(row).some(x => typeof x === 'number' && !Number.isFinite(x))))
    issue(issues, 'numeric_nonfinite', 'reject');
  if (issues.some(x => x.severity === 'reject')) return;
  observed.provider_truncated = data.truncated; // Tail pages may truthfully retain true.
  if (!FINANCIAL.has(args.name)) {
    observed.coverage = coverage.check(args, data, issues);
    issue(issues, 'interface_semantics_unchecked'); return;
  }
  const expected = security(args.name === 'stock_financial_hk_report_em' ? args.params.stock : args.params.symbol);
  let unknownIdentity = 0, futurePeriod = 0, futureDisclosure = 0, unknownDisclosure = 0, invalidDate = 0;
  let missingCells = 0, financialMissing = 0;
  const required = args.name === 'stock_financial_hk_report_em' ? ['AMOUNT'] : ['TOTAL_OPERATE_INCOME', 'PARENT_NETPROFIT'];
  for (const row of data.rows) {
    const identities = ['SECUCODE', 'SECURITY_CODE'].filter(k => !missing(row[k])).map(k => security(row[k]));
    if (!identities.length || identities.some(x => !x)) unknownIdentity++;
    if (identities.some(x => !x)) issue(issues, 'identity_format_invalid', 'reject');
    if (identities.some(x => x && (x.code !== expected.code || (x.market && x.market !== expected.market))))
      issue(issues, 'security_identity_mismatch', 'reject');
    if (Object.values(row).some(x => x === '未知企业')) issue(issues, 'company_placeholder');
    missingCells += Object.values(row).filter(missing).length;
    financialMissing += required.filter(k => missing(row[k])).length;
    const period = isoDay(row.REPORT_DATE);
    if (!period) invalidDate++;
    else if (period > asOf) futurePeriod++;
    const disclosed = isoDay(row.NOTICE_DATE);
    if (!disclosed) unknownDisclosure++;
    else if (disclosed > asOf) futureDisclosure++;
  }
  Object.assign(observed, {identity_unknown_rows: unknownIdentity, future_report_period_rows: futurePeriod,
    future_disclosure_rows: futureDisclosure, disclosure_unknown_rows: unknownDisclosure,
    invalid_report_date_rows: invalidDate, missing_cells: missingCells, missing_financial_cells: financialMissing});
  if (unknownIdentity) issue(issues, 'identity_unverified');
  if (futurePeriod || futureDisclosure) issue(issues, 'rows_after_valuation_cutoff');
  if (invalidDate) issue(issues, 'report_date_invalid');
  if (unknownDisclosure) issue(issues, 'disclosure_date_unverified');
  if (financialMissing) issue(issues, 'financial_fields_missing');
  // No currency or scale is inferred from an exchange, language or ticker.
  if (missing(data.currency) || missing(data.unit)) issue(issues, 'currency_or_unit_unverified');
  observed.coverage = issues.some(x => x.severity === 'reject') ? 'rejected_page' : coverage.check(args, data, issues);
}

export function inspect(tool, args, result, {asOf, coverage = new Coverage()} = {}) {
  const issues = precheck(tool, args), observed = {valuation_cutoff: asOf ?? null};
  if (!issues.length) {
    if (!result || result.isError !== false) issue(issues, 'upstream_tool_failed', 'reject');
    else if (tool === 'web_fetch') webCheck(result.value, issues, observed);
    else if (tool === AK) tableCheck(args, result.value, asOf, coverage, issues, observed);
  }
  const unique = [...new Map(issues.map(x => [x.code, x])).values()];
  return {schema_version: 'research-data-health/v1', tool,
    status: unique.some(x => x.severity === 'reject') ? 'rejected' : unique.length ? 'review_required' : 'mechanical_checks_only',
    issues: unique, observed, fact_verification: 'not_performed'};
}

const GUIDANCE = '取数体检仅检查机械一致性，不证明事实正确。缺失保持未知；禁止自动补零、改单位或判无公告。'
  + '部分分页/正文截断须按所需范围补取，已核验片段可局部使用，不能声称完整。'
  + '主体冲突或格式错误须另取来源；估值日之后的披露/期间不得用于本轮历史判断；单位、币种和披露日回原公告核验。';

async function persist(directory, exec, report, result) {
  const stat = await fs.lstat(directory);
  if (!stat.isDirectory() || stat.isSymbolicLink() || await fs.realpath(directory) !== directory)
    throw new Error('health directory changed');
  const id = randomUUID(), raw = result?.isError === false ? JSON.stringify(result.value) + '\n' : null;
  const write = async (file, text) => {
    const fd = await fs.open(file, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW, 0o600);
    try { await fd.writeFile(text); } finally { await fd.close(); }
  };
  if (raw && Buffer.byteLength(raw) > MAX_RAW_BYTES) throw new Error('health response too large');
  const record = {...report, fetched_at: new Date().toISOString(), request_sha256: hash(canonical(exec.arguments)),
    call_sha256: hash(String(exec.callId)), raw_path: raw ? `${id}.raw.json` : null, raw_sha256: raw ? hash(raw) : null};
  if (raw) await write(path.join(directory, record.raw_path), raw);
  const file = path.join(directory, `${id}.check.json`);
  await write(file, JSON.stringify(record, null, 2) + '\n');
  return file;
}

/** Global hooks cover root and child agents; original values are never rewritten. */
export function apply(ctx, config) {
  if (!object(config) || !path.isAbsolute(config.directory) || isoDay(config.asOf) !== config.asOf)
    throw new Error('Invalid frozen data health configuration');
  const coverage = new Coverage();
  ctx.on('tools/pre-execute', async (exec, next) => {
    if (!relevant(exec)) return next();
    const issues = precheck(exec.name, exec.arguments);
    if (!issues.length) return next();
    const report = {schema_version: 'research-data-health/v1', tool: exec.name, stage: 'preflight',
      valuation_cutoff: config.asOf, status: 'rejected', issues};
    let file;
    try { file = await persist(config.directory, exec, report); }
    catch { return {kind: 'deny', reason: '取数体检记录失败；检查本次运行目录，不得宣称取数通过。'}; }
    return {kind: 'deny', reason: `${GUIDANCE}\n${JSON.stringify(report)}\n体检记录：${file}`};
  });
  ctx.on('tools/post-execute', async (exec, result, next) => {
    if (!relevant(exec)) return next();
    if (precheck(exec.name, exec.arguments).length) return next(); // Already recorded by preflight.
    const downstream = await next();
    if (downstream.kind !== 'accept' || Object.hasOwn(downstream, 'value'))
      return downstream; // Never bypass another policy or inspect a replaced result as the original.
    let report, file;
    try {
      report = inspect(exec.name, exec.arguments, result, {asOf: config.asOf, coverage});
      file = await persist(config.directory, exec, report, result);
    } catch {
      coverage.groups.clear(); // Unsaved checks must not support later completeness claims.
      return {kind: 'block', feedback: [{type: 'text', text: '取数体检或原始响应保存失败；此次响应尚未通过机械检查，请保留缺口并改用可核验来源。'}]};
    }
    const note = {type: 'text', text: `${GUIDANCE}\n${JSON.stringify(report)}\n体检及原始响应索引：${file}`};
    const contexts = [...downstream.additionalContexts ?? []];
    // PTC subcalls consume the canonical value, not its presentation. Ferry the
    // same diagnostic to the model after the enclosing run_code completes.
    if (exec.parent !== undefined) contexts.push(Object.freeze({id: randomUUID(), role: 'user',
      source: Object.freeze({kind: 'tool', callId: exec.callId}), content: Object.freeze([Object.freeze(note)])}));
    const content = downstream.content ?? result.content;
    if (report.status === 'rejected' && result.isError === false)
      return {kind: 'block', feedback: [note], additionalContexts: contexts};
    return {...downstream, content: [note, ...content], additionalContexts: contexts};
  });
}
