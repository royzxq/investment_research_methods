"""Bind each generation of the stock framework to its exact method files."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

CORE = ('investment_framework.md', 'investment_framework_compact.md')
STRATEGY_DEPENDENCIES = ('stock_research_common.md', 'dividend_framework.md',
                         'dividend_framework_compact.md', 'dividend_report_template.md')
AI_SUPPLEMENT = 'ai_business_supplement.md'
PIPELINE_SUPPLEMENT = 'drug_pipeline_supplement.md'
AI_DEPENDENCIES = STRATEGY_DEPENDENCIES + (AI_SUPPLEMENT,)
DEPENDENCIES = AI_DEPENDENCIES + (PIPELINE_SUPPLEMENT,)
DEPENDENCY_VERSIONS = (STRATEGY_DEPENDENCIES, AI_DEPENDENCIES, DEPENDENCIES)
STRATEGY_BUNDLE = CORE + STRATEGY_DEPENDENCIES
AI_BUNDLE = CORE + AI_DEPENDENCIES
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
    if not isinstance(pairs, list) or any(not isinstance(p, tuple) or len(p) != 2 for p in pairs):
        raise ValueError('invalid stock framework dependencies')
    result = dict(pairs)
    if (len(result) != len(pairs) or not any(result.keys() == set(names) for names in DEPENDENCY_VERSIONS)
            or any(not isinstance(v, str) or
            not re.fullmatch('[0-9a-f]{64}', v) for v in result.values())):
        raise ValueError('invalid stock framework dependencies')
    return result


def validate(contents):
    maps = [dependency_map(contents[name]) for name in CORE]
    if maps == [None, None]:
        if set(contents) != set(CORE):
            raise ValueError('legacy framework must contain the exact original pair')
        return CORE
    if maps[0] is None or maps[0] != maps[1] or set(contents) != set(CORE).union(maps[0]):
        raise ValueError('stock framework dependency closure missing or inconsistent')
    for name, digest in maps[0].items():
        if hashlib.sha256(contents[name]).hexdigest() != digest:
            raise ValueError('stock framework dependency hash mismatch: ' + name)
    return CORE + next(names for names in DEPENDENCY_VERSIONS if maps[0].keys() == set(names))


def capture(folder):
    folder = Path(folder)
    contents = {name: (folder / name).read_bytes() for name in CORE}
    declared = dependency_map(contents[CORE[0]]) or {}
    # Historical prompt hashes also bind the file order.
    contents.update({name: (folder / name).read_bytes() for name in DEPENDENCIES if name in declared})
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
