"""Download integrity, public URL boundaries and real local PDF extraction."""
import contextlib
import http.server
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from scripts import research_document_recovery as recovery
from scripts.research_dsh import _pdf_python


class DocumentRecoveryTests(unittest.TestCase):
    def test_network_targets_reject_credentials_local_redirects_and_nonweb_urls(self):
        for url in ['file:///etc/passwd', 'https://user:pass@example.org', 'http://example.org:22',
                    'https://example.org\n/secret']:
            with self.subTest(url=url), self.assertRaises((recovery.RecoveryError, ValueError)):
                recovery.public_target(url)
        with patch.object(recovery.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('127.0.0.1', 80))]):
            with self.assertRaisesRegex(recovery.RecoveryError, 'non_public'):
                recovery.public_target('http://example.org')
        with patch.object(recovery.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.216.34', 443))]):
            self.assertEqual(recovery.public_target('https://example.org')[2], '93.184.216.34')

    def test_long_html_preserves_body_after_script_and_numbers_without_inventing_semantics(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp).resolve()
            raw = ('<html><head><script>' + 'x' * 120000 + '</script></head><body><h1>报告</h1>'
                   '<table><tr><th>利润</th><td>-100</td><td>0</td><td>--</td></tr></table>'
                   '<p>受限现金 1,234 万元</p></body></html>').encode()
            value = recovery.extract(raw, dict(content_type='text/html; charset=utf-8', final_url='https://example.org/a'), p)
            text = recovery.read_checked(p, value['parts'][0]).decode()
            self.assertIn('受限现金 1,234 万元', text)
            self.assertIn('-100\t0\t--', text)
            self.assertNotIn('xxxx', text)
            self.assertEqual(recovery.read_checked(p, value['raw']), raw)
            self.assertEqual(value['semantic_verification'], 'pending')

    def test_empty_html_and_pdf_disguised_as_login_page_are_not_usable_proof(self):
        with tempfile.TemporaryDirectory() as temp:
            value = recovery.extract(b'<html><script>loading</script></html>',
                dict(content_type='text/html', final_url='https://example.org/a'), Path(temp).resolve())
            self.assertFalse(value['text_available'])
            self.assertIn('short_or_empty_text_requires_review', value['warnings'])
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(recovery.RecoveryError, 'pdf_signature'):
            recovery.extract(b'<html>Login</html>', dict(content_type='text/html', final_url='https://example.org/a.pdf'), Path(temp).resolve())

    def test_tampered_files_and_symlink_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp).resolve()
            record = recovery.write_new(p, 'source.txt', b'original')
            (p / 'source.txt').write_bytes(b'changed')
            with self.assertRaisesRegex(recovery.RecoveryError, 'artifact_changed'):
                recovery.read_checked(p, record)
            (p / 'link').symlink_to(p, target_is_directory=True)
            with self.assertRaises(recovery.RecoveryError):
                recovery.directory(str(p / 'link'))
            with self.assertRaises(recovery.RecoveryError):
                recovery.write_new(p, '../escape', b'x')

    def test_http_size_truncation_status_and_redirect_validation(self):
        class Response:
            status = 200
            def __init__(self, body, headers): self.body, self.headers = body, headers
            def getheader(self, name, default=None): return self.headers.get(name, default)
            def read(self, count):
                value, self.body = self.body[:count], self.body[count:]
                return value
        class Connection:
            def __init__(self, response): self.response = response
            def request(self, *args, **kw): pass
            def getresponse(self): return self.response
            def close(self): pass
        responses = [(Response(b'abc', {'Content-Length': '5'}), 'incomplete_download'),
            (Response(b'abc', {'Content-Length': str(recovery.MAX_BYTES + 1)}), 'size_limit'),
            (Response(b'abc', {'Content-Encoding': 'gzip'}), 'unsupported_content_encoding')]
        for response, expected in responses:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temp, \
                 patch.object(recovery, 'public_target', return_value=(urlsplit('https://example.org'), 443, '93.184.216.34')), \
                 patch.object(recovery.http.client, 'HTTPSConnection', return_value=Connection(response)), \
                 self.assertRaisesRegex(recovery.RecoveryError, expected):
                recovery.download('https://example.org', Path(temp))
        redirect = Response(b'', {'Location': 'http://127.0.0.1/private'}); redirect.status = 302
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(recovery, 'public_target', return_value=(urlsplit('https://example.org'), 443, '93.184.216.34')), \
             patch.object(recovery.http.client, 'HTTPSConnection', return_value=Connection(redirect)), \
             self.assertRaisesRegex(recovery.RecoveryError, 'https_downgrade'):
            recovery.download('https://example.org', Path(temp))

    def test_real_local_http_download_keeps_all_bytes_and_extracts_late_body(self):
        raw = ('<html><script>' + 'x' * 110000 + '</script><body><p>late evidence</p></body></html>').encode()
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
            def log_message(self, *args): pass
        with http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            try:
                url = f'http://127.0.0.1:{server.server_port}/report'
                # Only the test replaces public-target validation for its loopback fixture.
                with tempfile.TemporaryDirectory() as temp, patch.object(recovery, 'public_target',
                        return_value=(urlsplit(url), server.server_port, '127.0.0.1')):
                    data, meta = recovery.download(url, Path(temp))
                    self.assertEqual(data, raw)
                    result = recovery.extract(data, meta, Path(temp).resolve())
                    self.assertIn('late evidence', recovery.read_checked(Path(temp).resolve(), result['parts'][0]).decode())
            finally:
                server.shutdown(); thread.join(timeout=3)

    def test_installed_pymupdf_preserves_pages_marks_blank_and_renders_original(self):
        root = Path(__file__).resolve().parents[1]
        code = '''import importlib.util,json,pathlib,sys,tempfile,pymupdf
spec=importlib.util.spec_from_file_location('recovery',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as temp:
 p=pathlib.Path(temp).resolve();d=pymupdf.open();d.new_page().insert_text((50,50),'Revenue 1234; cash -50');d.new_page()
 raw=d.tobytes();d.close();r=m.extract(raw,dict(content_type='application/pdf',final_url='https://example.org/report.pdf'),p)
 assert len(r['parts'])==2 and r['parts'][1]['chars']==0
 assert 'pages_without_text_require_visual_review' in r['warnings']
 assert b'Revenue 1234' in m.read_checked(p,r['parts'][0])
 image=m.render(p,r,2);assert m.read_checked(p,image).startswith(b'\\x89PNG')
 assert r['semantic_verification']=='pending'
 print(json.dumps(dict(pages=2,rendered=True,semantic_verification=r['semantic_verification'])))
'''
        result = subprocess.run([_pdf_python(), '-I', '-c', code, str(root / 'scripts/research_document_recovery.py')],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['rendered'])


if __name__ == '__main__':
    unittest.main()
