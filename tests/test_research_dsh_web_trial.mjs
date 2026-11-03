import test from 'node:test';
import assert from 'node:assert/strict';
import {validateManifest, nonemptyResult} from '../scripts/research_dsh_web_trial.mjs';

test('HTTP error pages and empty responses do not count as successful retrieval', () => {
  assert.equal(nonemptyResult('fetch', {statusCode: 404, body: {kind: 'text', content: 'Not Found'}}), false);
  assert.equal(nonemptyResult('fetch', {statusCode: 200, body: {kind: 'text', content: '  '}}), false);
  assert.equal(nonemptyResult('fetch', {statusCode: 200, body: {kind: 'text', content: 'article'}}), true);
  assert.equal(nonemptyResult('fetch', {statusCode: 200, body: {kind: 'html', content: '<article>body</article>'}}), true);
  assert.equal(nonemptyResult('search', {sources: []}), false);
  assert.equal(nonemptyResult('search', {sources: [{url: 'https://example.com'}]}), true);
});

test('manifest cannot escape its output directory or reuse a case filename', () => {
  for (const id of ['../outside', '/absolute', 'a/b', undefined]) {
    assert.throws(() => validateManifest({repeats: 1, cases: [{id, kind: 'search', query: 'test'}]}));
  }
  assert.throws(() => validateManifest({repeats: 1, cases: [1, 2].map(() => ({id: 'same', kind: 'search', query: 'test'}))}));
});

test('invalid requests are rejected before any provider request', () => {
  for (const repeats of [0, -1, 11, 1.5]) assert.throws(() => validateManifest({repeats, cases: []}));
  for (const item of [{id: 'empty', kind: 'search', query: ''}, {id: 'file', kind: 'fetch', url: 'file:///tmp/local'}]) {
    assert.throws(() => validateManifest({repeats: 1, cases: [item]}));
  }
  validateManifest({repeats: 2, cases: [{id: 'fetch', kind: 'fetch', url: 'https://example.com'}]});
});
