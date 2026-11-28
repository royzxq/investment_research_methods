"""Collect dated research inputs with the two CLI backends used by stock_analysis MCP."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from datetime import date, datetime, timedelta
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = 'output/runtime/stock-analysis-0.2.11'
SHANGHAI = ZoneInfo('Asia/Shanghai')


def query(root, args, timeout, cancelled=None):
    """Run the pinned plugin's command directly so cancellation also stops nested CLIs."""
    runtime = root / RUNTIME
    scripts = list(runtime.glob('lib/python*/site-packages/hermes/_payload/tools/value_data.py'))
    if len(scripts) != 1:
        raise ValueError('plugin_runtime_unavailable')
    env = {k: v for k, v in os.environ.items() if k.upper() in {
        'PATH', 'HOME', 'TMPDIR', 'LANG', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY',
        'REQUESTS_CA_BUNDLE', 'SSL_CERT_FILE', 'SSL_CERT_DIR'}}
    env['STOCK_CACHE_DIR'] = str(root / 'output/cache/stock-analysis')
    deadline = time.monotonic() + timeout
    with subprocess.Popen([runtime / 'bin/python', '-I', scripts[0], *args], env=env,
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          start_new_session=True) as proc:
        try:
            while True:
                if cancelled is not None and cancelled.is_set():
                    raise InterruptedError('research runner cancelled during disclosure lookup')
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ValueError('provider_timeout')
                try:
                    stdout, _ = proc.communicate(timeout=min(remaining, 0.25) if cancelled is not None else remaining)
                    break
                except subprocess.TimeoutExpired:
                    continue
        finally:
            if proc.returncode is None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.communicate()
        if proc.returncode:
            raise ValueError('provider_call_failed')
    try:
        raw = json.loads(stdout)
    except (UnicodeError, ValueError):
        raise ValueError('invalid_provider_response') from None
    if not isinstance(raw, dict) or 'error' in raw:
        raise ValueError('invalid_provider_response')
    return raw


def stock_symbol(code):
    if re.fullmatch(r'[0-9]{6}\.(SH|SZ)', code):
        if code[0] in '036' and code.endswith('.SH') != code.startswith('6'):
            raise ValueError('stock_exchange_mismatch')
        return code[:6]
    if re.fullmatch(r'[0-9]{5}\.HK', code):
        return code
    raise ValueError('expected_market_qualified_stock_code')


def filings(root, code, cutoff, start=None, *, timeout=60, cancelled=None):
    end = date.fromisoformat(cutoff)
    start = (end - timedelta(days=89)).isoformat() if start is None else start
    if date.fromisoformat(start) > end:
        raise ValueError('start_after_cutoff')
    hk = code.endswith('.HK')
    host = 'www1.hkexnews.hk' if hk else 'static.cninfo.com.cn'
    source = 'hkexnews' if hk else 'cninfo'
    result = dict(tool='get_announcements', code=code, source=source,
                  directory='HKEXnews English' if hk else 'CNInfo A-share', start_date=start,
                  end_date=cutoff, queried_at=datetime.now(SHANGHAI).isoformat(), category='all',
                  status='unavailable', filings=[])
    try:
        symbol = stock_symbol(code)
        raw = query(root, ['announcements', symbol, '--category', 'all', '--start-date', start,
                           '--end-date', cutoff, '--top', '500'], timeout, cancelled)
        if (raw.get('symbol') != symbol or raw.get('market') != ('HK' if hk else 'A')
                or raw.get('source') != source or raw.get('requested_category') != 'all'
                or (raw.get('start_date'), raw.get('end_date')) != (start, cutoff)
                or not isinstance(raw.get('announcements'), list) or type(raw.get('truncated')) is not bool
                or type(raw.get('total')) is not int or raw['total'] < 0):
            raise ValueError('response_identity_or_coverage_mismatch')
        records = {}
        rejected = 0
        for row in raw['announcements']:
            if not isinstance(row, dict):
                rejected += 1
                continue
            url, title, day = (row.get(k) for k in ('pdf_url', 'title', 'date'))
            if (not isinstance(url, str) or not url.startswith('https://' + host + '/')
                    or not isinstance(title, str) or not title.strip() or not isinstance(day, str)
                    or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', day) or not start <= day <= cutoff):
                rejected += 1
                continue
            try:
                date.fromisoformat(day)
            except ValueError:
                rejected += 1
                continue
            records[url] = dict(date=day, title=title, document_url=url)
        rows = sorted(records.values(), key=lambda row: (row['date'], row['title']), reverse=True)
        partial = raw['truncated'] or rejected or raw['total'] != len(raw['announcements'])
        result.update(status='partial' if partial else 'indexed' if rows else 'empty_unconfirmed',
                      provider_total=raw['total'], truncated=raw['truncated'], rejected_rows=rejected,
                      filings=rows)
    except InterruptedError:
        raise
    except (ValueError, OSError) as exc:
        result['reason'] = str(exc) if isinstance(exc, ValueError) else 'plugin_launch_failed'
    return result


def etf_holdings(root, fund, cutoff, stock=None, *, period=None, published=None, original=None,
                 original_position_count=None):
    """Only release rows from a report the researcher has dated to the decision window."""
    end = date.fromisoformat(cutoff)
    if not re.fullmatch(r'[0-9]{6}\.(SH|SZ)', fund):
        raise ValueError('expected_domestic_listed_fund_code')
    if (fund.startswith('5') and not fund.endswith('.SH')) or (fund.startswith('1') and not fund.endswith('.SZ')):
        raise ValueError('fund_exchange_mismatch')
    if stock:
        stock_symbol(stock)
    if any((period, published, original)):
        if not all((period, published, original)) or not (
                urlsplit(original).scheme == 'https' and urlsplit(original).hostname):
            raise ValueError('supply_report_period_publication_date_and_original_https_url_together')
        if date.fromisoformat(published) < date.fromisoformat(period):
            raise ValueError('publication_precedes_report_period')
    if original_position_count is not None and (
            not published or type(original_position_count) is not int or original_position_count < 1):
        raise ValueError('original_position_count_requires_dated_report_and_positive_count')
    result = dict(tool='get_etf_details', fund=fund, cutoff=cutoff, stock=stock,
                  queried_at=datetime.now(SHANGHAI).isoformat(), status='unavailable',
                  weight_pct=None, published_on=published, original_url=original, original_period=period,
                  original_position_count=original_position_count, coverage_status='unverified')
    try:
        raw = query(root, ['etf_details', fund[:6], '--days', '10', '--include-full-holdings'], 480)
        report = raw.get('disclosed_equity_report')
        if raw.get('symbol') != fund[:6] or raw.get('market') != 'A' or not isinstance(report, dict):
            raise ValueError('disclosed_equity_table_unavailable')
        actual = date.fromisoformat(report['as_of'])
        rows = report.get('equity_positions')
        result.update(report_period=actual.isoformat(), requested_report_period=report.get('requested_report_date'),
                      holdings_source=report.get('source_url'), coverage=report.get('coverage'),
                      warnings=raw.get('warnings', []))
        if (not isinstance(rows, list) or not rows or report.get('position_count') != len(rows)
                or not all(isinstance(row, dict) and isinstance(row.get('code'), str) for row in rows)):
            raise ValueError('incomplete_equity_table')
        if actual > end or (published and date.fromisoformat(published) > end):
            result['status'] = 'unavailable_at_cutoff'
        elif period and period != actual.isoformat():
            result['status'] = 'different_report_period'
        elif not published:
            result['status'] = 'verify_original_publication'
        else:
            if original_position_count is not None:
                result['coverage_status'] = (
                    'verified_against_original' if len(rows) == original_position_count else 'count_mismatch')
            # Keep the listed code and leading zeroes. Truncated codes remain unknown.
            selected = rows if not stock else [r for r in rows if r['code'] == stock.split('.')[0]]
            if stock and len(selected) != 1:
                result['status'] = 'stock_exposure_unknown'
            else:
                positions = []
                for row in selected:
                    weight = row.get('weight_pct')
                    if type(weight) not in (float, int) or not math.isfinite(weight) or not 0 <= weight <= 100:
                        raise ValueError('missing_or_invalid_weight')
                    positions.append(dict(code=row['code'], name=row.get('name'), weight_pct=weight))
                result.update(status='disclosed_holdings', position_count=len(rows), positions=positions)
                if stock:
                    result['weight_pct'] = positions[0]['weight_pct']
    except (KeyError, TypeError, ValueError, OSError) as exc:
        result['reason'] = str(exc) if type(exc) is ValueError else 'invalid_or_unavailable_response'
    return result


def compare_funds(left, right):
    """Sum common disclosed NAV weights only within the same decision and reporting dates."""
    for table in (left, right):
        if (table.get('status') != 'disclosed_holdings' or table.get('stock') is not None
                or table.get('coverage_status') != 'verified_against_original'
                or not table.get('positions')
                or len(table['positions']) != table.get('position_count')
                or len(table['positions']) != table.get('original_position_count')):
            raise ValueError('comparison_requires_two_tables_verified_against_original_reports')
    if (left['fund'] == right['fund'] or left['report_period'] != right['report_period']
            or left['cutoff'] != right['cutoff']):
        raise ValueError('comparison_requires_distinct_funds_and_aligned_dates')

    def by_code(rows):
        indexed = {}
        for row in rows:
            code = row['code']
            # Different report sections can repeat a security. Reconcile those in the originals.
            indexed[code] = None if code in indexed else row
        return indexed

    a, b = (by_code(table['positions']) for table in (left, right))
    common, unresolved = [], []
    for code in sorted(a.keys() & b.keys()):
        first, second = a[code], b[code]
        if not first or not second or not first.get('name') or first['name'] != second.get('name'):
            unresolved.append(code)
            continue
        common.append(dict(code=code, name=first['name'], left_pct=first['weight_pct'],
                           right_pct=second['weight_pct'], common_pct=min(first['weight_pct'], second['weight_pct'])))
    common.sort(key=lambda row: -row['common_pct'])
    return dict(status='partial' if unresolved else 'compared',
                funds=[left['fund'], right['fund']], cutoff=left['cutoff'], report_period=left['report_period'],
                originals=[left['original_url'], right['original_url']], common_positions=common,
                unresolved_common_codes=unresolved,
                observed_common_nav_pct=round(sum(row['common_pct'] for row in common), 4))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    commands = ap.add_subparsers(dest='mode', required=True)
    ann = commands.add_parser('announcements')
    ann.add_argument('code')
    ann.add_argument('--start')
    etf = commands.add_parser('etf')
    etf.add_argument('fund')
    etf.add_argument('--stock')
    etf.add_argument('--report-period')
    etf.add_argument('--published-on')
    etf.add_argument('--original-url')
    etf.add_argument('--original-position-count', type=int,
                     help='equity row count from the original report after checking every row')
    for cmd in (ann, etf):
        cmd.add_argument('--as-of', required=True)
    overlap = commands.add_parser('overlap', help='compare two saved whole-fund etf results')
    overlap.add_argument('left', type=Path)
    overlap.add_argument('right', type=Path)
    args = ap.parse_args()
    if args.mode == 'announcements':
        result = filings(ROOT, args.code, args.as_of, args.start)
    elif args.mode == 'etf':
        result = etf_holdings(ROOT, args.fund, args.as_of, args.stock, period=args.report_period,
                              published=args.published_on, original=args.original_url,
                              original_position_count=args.original_position_count)
    else:
        result = compare_funds(json.loads(args.left.read_text()), json.loads(args.right.read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
