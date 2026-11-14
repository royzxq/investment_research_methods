"""Bounded public-document recovery for DSH; no model calls or financial inference.

The caller owns a fresh directory. Complete downloads and page/line locators are
hashed; extraction warnings never become factual verification. stdin/stdout JSON.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import http.client
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import ssl
import stat
import sys
import time
from urllib.parse import urljoin, urlsplit

MAX_BYTES = 32 * 1024 * 1024
MAX_PAGES = 1000
SCHEMA = 'research-document-recovery/v1'


class RecoveryError(Exception):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def directory(value):
    p = Path(value)
    if not p.is_absolute() or p.is_symlink() or not p.is_dir() or str(p.resolve()) != str(p):
        raise RecoveryError('unsafe_directory')
    return p


def write_new(folder, name, raw):
    directory(str(folder))
    if Path(name).name != name:
        raise RecoveryError('unsafe_filename')
    fd = os.open(folder / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(raw)
    return dict(file=name, sha256=digest(raw), bytes=len(raw))


def read_checked(folder, record):
    directory(str(folder))
    name = record['file']
    if Path(name).name != name:
        raise RecoveryError('unsafe_filename')
    fd = os.open(folder / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise RecoveryError('not_regular_file')
        raw = f.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES or digest(raw) != record['sha256']:
        raise RecoveryError('artifact_changed')
    return raw


def public_target(url):
    p = urlsplit(url)
    if (p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password
            or p.port not in (None, 80 if p.scheme == 'http' else 443)
            or any(ord(c) < 32 for c in url)):
        raise RecoveryError('public_http_url_required')
    port = p.port or (443 if p.scheme == 'https' else 80)
    addresses = sorted({x[4][0] for x in socket.getaddrinfo(p.hostname, port, type=socket.SOCK_STREAM)})
    if not addresses or any(not ipaddress.ip_address(x).is_global for x in addresses):
        raise RecoveryError('non_public_address')
    return p, port, addresses[0]


def download(url, folder):
    """Pin each validated DNS answer, retaining TLS hostname/SNI; recheck redirects."""
    deadline = time.monotonic() + 60
    initial = url
    for redirect in range(6):
        p, port, ip = public_target(url)
        timeout = min(15, deadline - time.monotonic())
        if timeout <= 0:
            raise RecoveryError('download_timeout')
        conn = (http.client.HTTPSConnection(p.hostname, port, timeout=timeout, context=ssl.create_default_context())
                if p.scheme == 'https' else http.client.HTTPConnection(p.hostname, port, timeout=timeout))
        # The connection still uses the original hostname for Host and TLS SNI.
        conn._create_connection = lambda address, timeout=None, source_address=None: socket.create_connection(
            (ip, port), timeout, source_address)
        try:
            conn.request('GET', (p.path or '/') + ('?' + p.query if p.query else ''), headers={
                'User-Agent': 'InvestmentResearchDocumentRecovery/1.0', 'Accept-Encoding': 'identity',
                'Accept': 'application/pdf,text/html,application/xhtml+xml,text/plain;q=0.9'})
            response = conn.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader('Location')
                if not location:
                    raise RecoveryError('redirect_missing_location')
                target = urljoin(url, location)
                if p.scheme == 'https' and urlsplit(target).scheme != 'https':
                    raise RecoveryError('https_downgrade')
                url = target
                continue
            if response.status != 200:
                raise RecoveryError('http_status_' + str(response.status))
            if response.getheader('Content-Encoding', 'identity').lower() not in ('', 'identity'):
                raise RecoveryError('unsupported_content_encoding')
            length = response.getheader('Content-Length')
            expected = int(length) if length is not None else None
            if expected is not None and (expected < 0 or expected > MAX_BYTES):
                raise RecoveryError('download_size_limit')
            chunks, total = [], 0
            while True:
                if time.monotonic() > deadline:
                    raise RecoveryError('download_timeout')
                chunk = response.read(min(65536, MAX_BYTES + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_BYTES:
                    raise RecoveryError('download_size_limit')
                chunks.append(chunk)
            raw = b''.join(chunks)
            if not raw or (expected is not None and len(raw) != expected):
                raise RecoveryError('incomplete_download')
            return raw, dict(requested_url=initial, final_url=url, http_status=response.status,
                             content_type=response.getheader('Content-Type', ''), redirects=redirect)
        finally:
            conn.close()
    raise RecoveryError('redirect_limit')


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = []
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag in ('head', 'script', 'style', 'nav', 'header', 'footer'):
            self.hidden.append(tag)
        elif not self.hidden and tag in ('p', 'div', 'br', 'tr', 'li', 'h1', 'h2', 'h3', 'section'):
            self.out.append('\n')
        elif not self.hidden and tag in ('td', 'th'):
            self.out.append('\t')

    def handle_endtag(self, tag):
        if tag in self.hidden:
            self.hidden = self.hidden[:self.hidden.index(tag)]
        elif not self.hidden and tag in ('p', 'div', 'tr', 'li', 'section'):
            self.out.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.out.append(data)


def extract(raw, meta, folder):
    warnings, parts = [], []
    is_pdf = raw[:1024].lstrip().startswith(b'%PDF-')
    if is_pdf:
        import pymupdf
        source = write_new(folder, 'source.pdf', raw)
        doc = pymupdf.open(stream=raw, filetype='pdf')
        try:
            if doc.needs_pass:
                raise RecoveryError('encrypted_pdf')
            if not 0 < len(doc) <= MAX_PAGES:
                raise RecoveryError('pdf_page_limit')
            if doc.is_repaired:
                warnings.append('pdf_repaired_review_original')
            size = 0
            for i, page in enumerate(doc):
                text = page.get_text('text', sort=False)
                encoded = text.encode('utf-8')
                size += len(encoded)
                if size > MAX_BYTES:
                    raise RecoveryError('extracted_text_limit')
                parts.append(dict(index=i + 1, chars=len(text), lines=len(text.splitlines()),
                                  **write_new(folder, f'page-{i+1:05d}.txt', encoded)))
            if any(p['chars'] == 0 for p in parts):
                warnings.append('pages_without_text_require_visual_review')
        finally:
            doc.close()
        kind = 'pdf'
    else:
        if 'pdf' in meta['content_type'].lower() or urlsplit(meta['final_url']).path.lower().endswith('.pdf'):
            raise RecoveryError('pdf_signature_mismatch')
        mime = meta['content_type'].split(';')[0].strip().lower()
        if mime not in ('text/html', 'application/xhtml+xml', 'text/plain', ''):
            raise RecoveryError('unsupported_document_type')
        source = write_new(folder, 'source.html' if 'html' in mime else 'source.txt', raw)
        charset = re.search(r'charset\s*=\s*[\"\']?([\w.-]+)', meta['content_type'], re.I)
        if not charset:
            charset = re.search(r'charset\s*=\s*[\"\']?([\w.-]+)', raw[:8192].decode('ascii', 'ignore'), re.I)
        try:
            text = raw.decode(charset.group(1) if charset else 'utf-8')
        except (LookupError, UnicodeError):
            text = raw.decode('utf-8', 'replace')
            warnings.append('encoding_requires_review')
        kind = 'html' if 'html' in mime or re.search(r'<(?:html|body|!doctype)\b', text[:1000], re.I) else 'text'
        if kind == 'html':
            parser = VisibleHTML()
            parser.feed(text)
            text = '\n'.join(line.strip() for line in ''.join(parser.out).splitlines() if line.strip())
        if len(text.strip()) < 120:
            warnings.append('short_or_empty_text_requires_review')
        parts.append(dict(index=1, chars=len(text), lines=len(text.splitlines()),
                          **write_new(folder, 'document.txt', text.encode('utf-8'))))
    record = dict(schema_version=SCHEMA, kind=kind, transport_complete=True,
                  text_available=any(p['chars'] > 0 for p in parts), semantic_verification='pending',
                  raw=source, parts=parts, warnings=warnings, **meta)
    write_new(folder, 'document.json', (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode())
    return record


def render(folder, manifest, page):
    import pymupdf
    if type(page) is not int or not 1 <= page <= len(manifest['parts']) or manifest['kind'] != 'pdf':
        raise RecoveryError('invalid_pdf_page')
    raw = read_checked(folder, manifest['raw'])
    doc = pymupdf.open(stream=raw, filetype='pdf')
    try:
        p = doc[page - 1]
        scale = min(1.5, 1600 / max(p.rect.width, p.rect.height))
        image = p.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False).tobytes('png')
        return dict(page=page, rendered_only=True, **write_new(folder, f'render-{page:05d}-{os.urandom(4).hex()}.png', image))
    finally:
        doc.close()


def main():
    request = json.loads(sys.stdin.buffer.read(65537))
    folder = directory(request['directory'])
    if request['operation'] == 'download':
        raw, meta = download(request['url'], folder)
        return extract(raw, meta, folder)
    if request['operation'] == 'render':
        manifest = json.loads(read_checked(folder, request['manifest']))
        return render(folder, manifest, request['page'])
    raise RecoveryError('unknown_operation')


if __name__ == '__main__':
    try:
        print(json.dumps(dict(ok=True, result=main()), ensure_ascii=False))
    except Exception as exc:
        # Do not print URLs, headers, environment or parser exception payloads.
        code = str(exc) if isinstance(exc, RecoveryError) else type(exc).__name__
        print(json.dumps(dict(ok=False, error=code)))
        sys.exit(1)
