"""Check a proposed AI watchlist against ai_investment's current active research pool."""
import argparse
import json
from pathlib import Path
import sys

from stock_ai_watchlist import CODE, read_release


def active_listings(pool):
    active = {}
    for row in pool['stocks']:
        if row['state'] != 'active':
            continue
        ticker = row['code']
        if len(ticker) == 5:
            market = 'HK'
        elif ticker.startswith('6'):
            market = 'SH'
        elif ticker.startswith(('0', '3')):
            market = 'SZ'
        else:
            continue  # The watchlist covers SH/SZ/HK listings.
        code = f'{ticker}.{market}'
        if not CODE.fullmatch(code):
            raise ValueError(f'Invalid active security: {code}')
        active[code] = row['name']
    return active


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pool-root', required=True, type=Path)
    parser.add_argument('--release', type=Path, help='Check all proposed entries. Omit to show active candidates.')
    args = parser.parse_args()
    pool_root = args.pool_root.resolve(strict=True)
    sys.path.insert(0, str(pool_root))
    from scripts.review_stock_pool import build_inputs

    pool = build_inputs(pool_root, {'codes': []})
    for name in ('investment_prediction.csv', 'paused_stocks.csv'):
        if not pool['sources'].get(name):
            raise SystemExit(f'Missing stock pool source: {name}')
    active = active_listings(pool)
    result = dict(checked_at=pool['created_at'], active_count=len(active), sources=pool['sources'])
    if args.release:
        _, _, digest, entries = read_release(args.release)
        outside = sorted(entries.keys() - active.keys())
        if outside:
            raise SystemExit('Outside the active stock pool: ' + ', '.join(outside))
        result['release_sha256'] = digest
        result['matched_count'] = len(entries)
    else:
        result['active'] = active
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
