"""Archive auditable public-source evidence; gzip preserves exact CLI bytes."""
from pathlib import Path
import gzip
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[2]
sha = lambda raw: hashlib.sha256(raw).hexdigest()

if __name__ == '__main__':
    parent = ROOT / 'research/investment/maintenance/2026-10-12/evidence'
    target = parent / 'hengrui-claude-end-to-end'
    suffix = 2
    while target.exists():
        target = parent / f'hengrui-claude-end-to-end-r{suffix}'
        suffix += 1
    target.mkdir(parents=True)
    entries = {}
    for source in sorted(BASE.rglob('*')):
        if not source.is_file() or source.name in ['stderr.log'] or source.suffix == '.lock' or '__pycache__' in source.parts:
            continue
        relative = source.relative_to(BASE)
        raw = source.read_bytes()
        dest = target / relative
        compressed = source.name == 'events.jsonl'
        if compressed: dest = dest.with_name(dest.name + '.gz')
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = gzip.compress(raw, mtime=0) if compressed else raw
        dest.write_bytes(data)
        entries[str(dest.relative_to(target))] = dict(sha256=sha(data), bytes=len(data),
            original_relative_path=str(relative), original_sha256=sha(raw),
            original_bytes=len(raw), gzip=compressed)
    (target / 'archive-manifest.json').write_text(json.dumps(dict(
        generator='codex', measured_generator='claude', source_scratch=str(BASE),
        entries=entries, exclusions='private stderr and inactive lock copies; no usage/tool payloads omitted',
        reconstruction='For events.jsonl.gz, gzip decompression reproduces original events.jsonl exactly, including line offsets referenced by usage.json.'),
        ensure_ascii=False, indent=2))
    for relative, entry in entries.items():
        data = (target / relative).read_bytes()
        assert sha(data) == entry['sha256']
        decoded = gzip.decompress(data) if entry['gzip'] else data
        assert sha(decoded) == entry['original_sha256']
    fingerprint = json.loads((target / 'implementation-fingerprints.json').read_text())
    for path, expected in fingerprint.items(): assert sha((ROOT / path).read_bytes()) == expected
    (target / 'validation.json').write_text(json.dumps(dict(
        archived_files=len(entries), archived_hashes_valid=True, decompressed_event_hashes_valid=True,
        implementation_fingerprints=len(fingerprint), implementation_hashes_valid=True), indent=2))
    print(json.dumps({'archive': str(target), 'files': len(entries),
        'bytes': sum(e['bytes'] for e in entries.values())}))
