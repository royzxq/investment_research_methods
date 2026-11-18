"""Bind the shared/dividend method closure without changing legacy pair snapshots."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

CORE = ('investment_framework.md', 'investment_framework_compact.md')
DEPENDENCIES = ('stock_research_common.md', 'dividend_framework.md',
                'dividend_framework_compact.md', 'dividend_report_template.md')
BUNDLE = CORE + DEPENDENCIES
MARKER = re.compile(r'<!-- stock-framework-dependencies: (.*?) -->')
ROOT = Path(__file__).resolve().parents[1]


def dependency_map(raw):
    found = MARKER.findall(raw.decode('utf-8'))
    if not found:
        return None
    if len(found) != 1:
        raise ValueError('require one stock framework dependency marker')
    pairs = json.loads(found[0], object_pairs_hook=list)
    if (not isinstance(pairs, list) or any(not isinstance(p, tuple) or len(p) != 2 for p in pairs)
            or len(pairs) != len(DEPENDENCIES)):
        raise ValueError('invalid stock framework dependencies')
    result = dict(pairs)
    if (set(result) != set(DEPENDENCIES) or any(not isinstance(v, str) or
            not re.fullmatch('[0-9a-f]{64}', v) for v in result.values())):
        raise ValueError('invalid stock framework dependencies')
    return result


def validate(contents):
    maps = [dependency_map(contents[name]) for name in CORE]
    if maps == [None, None]:
        if set(contents) != set(CORE):
            raise ValueError('legacy framework must contain the exact original pair')
        return CORE
    if maps[0] is None or maps[0] != maps[1] or set(contents) != set(BUNDLE):
        raise ValueError('stock framework dependency closure missing or inconsistent')
    for name, digest in maps[0].items():
        if hashlib.sha256(contents[name]).hexdigest() != digest:
            raise ValueError('stock framework dependency hash mismatch: ' + name)
    return BUNDLE


def capture(folder):
    folder = Path(folder)
    contents = {name: (folder / name).read_bytes() for name in CORE}
    if any(dependency_map(raw) is not None for raw in contents.values()):
        contents.update({name: (folder / name).read_bytes() for name in DEPENDENCIES})
    validate(contents)
    if contents != {name: (folder / name).read_bytes() for name in contents}:
        raise ValueError('framework changed while preparing snapshot; retry preparation')
    return contents


def sync(root=ROOT):
    """Explicit maintainer action, never called by capture/prepare/validation."""
    folder = Path(root) / 'framework'
    mapping = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in DEPENDENCIES}
    marker = '<!-- stock-framework-dependencies: ' + json.dumps(mapping, sort_keys=True) + ' -->'
    for name in CORE:
        path = folder / name
        raw = path.read_text()
        if len(MARKER.findall(raw)) > 1:
            raise ValueError('duplicate dependency marker')
        path.write_text(MARKER.sub(marker, raw) if MARKER.search(raw) else marker + '\n' + raw)
    capture(folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--sync', action='store_true', help='Explicitly bind reviewed method dependency bytes')
    args = parser.parse_args()
    if args.sync:
        sync(args.root)
    print(json.dumps({'files': list(capture(args.root / 'framework'))}))
