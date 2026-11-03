/** Isolated, billable A/B of the exact installed providers. No production writes.
 * DEEPSEEK_API_KEY is inherited only; results never contain request headers.
 * Usage: node script.mjs <dsh-package-root> <manifest.json> <new-output-dir>
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
export function validateManifest(manifest) {
  if (!Number.isInteger(manifest?.repeats) || manifest.repeats < 1 || manifest.repeats > 10 ||
      !Array.isArray(manifest.cases) || !manifest.cases.length) throw new Error('invalid trial manifest');
  const ids = new Set();
  for (const item of manifest.cases) {
    if (!item || typeof item.id !== 'string' || !/^[a-z][a-z0-9-]{0,63}$/.test(item.id) || ids.has(item.id)) throw new Error('invalid or duplicate case id');
    ids.add(item.id);
    if (item.kind === 'search' && typeof item.query === 'string' && item.query.trim()) continue;
    if (item.kind === 'fetch' && typeof item.url === 'string') {
      try { if (/^https?:$/.test(new URL(item.url).protocol)) continue; } catch {}
    }
    throw new Error('invalid trial case');
  }
}

export function nonemptyResult(kind, result) {
  if (kind === 'search') return Array.isArray(result?.sources) && result.sources.length > 0;
  return Number.isInteger(result?.statusCode) && result.statusCode >= 200 && result.statusCode < 300 &&
    ['html', 'text'].includes(result.body?.kind) && typeof result.body.content === 'string' && result.body.content.trim().length > 0;
}

export async function runTrial(args) {
  const [root, manifestPath, output] = args;
  if (!root || !manifestPath || !output || !process.env.DEEPSEEK_API_KEY) throw new Error('explicit inputs and inherited credential required');
  const manifestBytes = await fs.readFile(manifestPath);
  const manifest = JSON.parse(manifestBytes);
  validateManifest(manifest);
  await fs.mkdir(output, {recursive: false});
  await fs.writeFile(path.join(output, 'manifest.json'), manifestBytes, {flag: 'wx'});
  const load = name => import(pathToFileURL(path.join(root, 'node_modules/@deepseek-ai', name, 'lib/index.js')));
  const direct = await load('dsh-web-deepseek-api');
  const legacy = await load('dsh-web-search-deepseek');
  const http = await load('dsh-web-fetch-http');
  const credential = async () => process.env.DEEPSEEK_API_KEY;
  const directOptions = () => ({resolveApiKey: credential, baseURL: direct.DEEPSEEK_WEB_API_BASE_URL, count: 10});
  const providers = {
    search_baseline: new legacy.DeepSeekSearchProvider(() => ({resolveApiKey: credential,
      baseURL: 'https://api.deepseek.com/anthropic/v1', apiVersion: legacy.DEEPSEEK_DEFAULT_API_VERSION,
      model: 'deepseek-flash', maxTokens: 4096, maxUses: 5})),
    search_candidate: new direct.DeepSeekSearchApiProvider(directOptions),
    fetch_baseline: new http.HttpFetchProvider({maxResponseBytes: 5000000, maxBodyChars: 100000,
      timeoutMs: 30000, maxRedirects: 5, userAgent: http.DEFAULT_USER_AGENT}),
    fetch_candidate: new direct.DeepSeekFetchApiProvider(directOptions),
  };
  const records = [];
  for (let repeat = 0; repeat < manifest.repeats; repeat++) {
    for (const item of manifest.cases) {
      // Alternation reduces ordering bias. Serial requests avoid load confounding.
      for (const arm of repeat % 2 ? ['candidate', 'baseline'] : ['baseline', 'candidate']) {
        const start = performance.now();
        const row = {id: item.id, kind: item.kind, arm, repeat, started_at: new Date().toISOString()};
        try {
          const provider = providers[`${item.kind}_${arm}`];
          const result = await provider[item.kind](item.kind === 'search' ? {query: item.query, maxResults: 10} : {url: item.url}, AbortSignal.timeout(60000));
          row.transport_ok = true;
          row.ok = nonemptyResult(item.kind, result);
          if (!row.ok) row.failure_reason = 'empty_or_unsuccessful_result';
          row.result = result;
        } catch (error) {
          row.ok = false;
          row.transport_ok = false;
          row.error_code = error.code ?? error.name;
          row.http_status = /HTTP (\d+)/.exec(error.message)?.[1] ?? null;
          // Provider messages may contain upstream content: deliberately omit them.
        }
        row.duration_ms = Math.round(performance.now() - start);
        records.push(row);
        await fs.writeFile(path.join(output, `${item.id}-${repeat}-${arm}.json`), JSON.stringify(row, null, 2) + '\n', {flag: 'wx'});
        console.log(JSON.stringify({id: row.id, repeat, arm, ok: row.ok, ms: row.duration_ms, error: row.error_code, status: row.http_status}));
      }
    }
  }
  const pkg = JSON.parse(await fs.readFile(path.join(root, 'package.json')));
  await fs.writeFile(path.join(output, 'summary.json'), JSON.stringify({schema_version: 'dsh-web-trial/v1',
    success_definition: 'nonempty response; fetch must be 2xx; substantive content requires separate review',
    driver_sha256: createHash('sha256').update(await fs.readFile(new URL(import.meta.url))).digest('hex'),
    installed_dsh_version: pkg.version, manifest_sha256: createHash('sha256').update(manifestBytes).digest('hex'),
    records: records.map(({result, ...row}) => ({...row, sources: result?.sources?.length ?? null,
      body_kind: result?.body?.kind ?? null, content_length: result?.body?.content?.length ?? null,
      truncated: result?.truncated ?? null, target_status: result?.statusCode ?? null}))}, null, 2) + '\n', {flag: 'wx'});
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await runTrial(process.argv.slice(2));
}
