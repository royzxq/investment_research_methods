"""Collect a research candidate using the same data builder as the daily refresh."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

SOURCE = 'research_candidate'


def due_candidates(path, day):
    if not path.exists():
        return []
    rows = json.loads(path.read_text())
    if not isinstance(rows, list):
        raise ValueError('research candidates must be a list')
    seen = set()
    due = []
    for order, row in enumerate(rows):
        if (not isinstance(row, dict) or set(row) != {'code', 'name', 'research_on'}
                or not isinstance(row['code'], str)
                or not re.fullmatch(r'6[0-9]{5}\.SH|[03][0-9]{5}\.SZ|[0-9]{5}\.HK', row['code'])
                or not isinstance(row['name'], str) or not row['name'].strip()
                or row['code'] in seen):
            raise ValueError('invalid or duplicate research candidate')
        seen.add(row['code'])
        if date.fromisoformat(row['research_on']).isoformat() == day:
            due.append({**row, 'order': order})
    return due


def collect(ai_root, exchange, candidate):
    # Use the installed AI repository and interpreter in this short-lived child.
    sys.path.insert(0, str(ai_root))
    import share_data
    from src.analysis.research_exchange import publish_request
    from src.decision.reeval_targets import ReevalTarget, research_trigger

    ticker, suffix = candidate['code'].split('.')
    market = 'HK' if suffix == 'HK' else 'A'
    day = candidate['research_on']
    markdown, meta = share_data.build_pack(ticker, market, date=day.replace('-', ''),
                                           years=5, with_macro=False)
    if meta.get('missing_core'):
        raise ValueError('candidate data pack missing core data: ' + ','.join(meta['missing_core']))
    target = ReevalTarget(candidate['name'], ticker, market, [SOURCE], day,
                          {SOURCE: {'research_on': day, 'order': candidate['order']}})
    pack = dict(market=market, code=ticker, name=target.name, sources=target.sources,
                markdown=f'> 触发来源: 人工指定调研候选 | 估值日: {day}\n\n{markdown}',
                meta={**meta, 'research_trigger': research_trigger(target)})
    return publish_request(exchange, [pack], day)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ai_root', type=Path)
    parser.add_argument('exchange', type=Path)
    parser.add_argument('candidate', type=json.loads)
    args = parser.parse_args()
    collect(args.ai_root, args.exchange, args.candidate)
