"""Select dated AI business verification leads for Shanghai, Shenzhen and Hong Kong research."""
import argparse
from datetime import date, datetime, time
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

try:
    from .research_exchange import _strict_json, _timestamp
    from .research_paths import AI_WATCHLIST_DIR
except ImportError:
    from research_exchange import _strict_json, _timestamp
    from research_paths import AI_WATCHLIST_DIR

ROOT = Path(__file__).resolve().parents[1]
ZONE = ZoneInfo('Asia/Shanghai')
FILENAME = re.compile(r'investment-(\d{4}-\d\d-\d\d)-ai-watchlist(?:-r([1-9]\d*))?\.json')
CODE = re.compile(r'[0-9]{6}\.(?:SH|SZ)|[0-9]{5}\.HK')
FIELDS = {'name', 'business', 'evidence', 'check', 'source_date', 'source_title', 'source_url'}


def cutoff(value):
    if len(value) == 10:
        return datetime.combine(date.fromisoformat(value), time.max, ZONE)
    return _timestamp(value, 'AI watchlist cutoff').astimezone(ZONE)


def releases(root, until):
    """Read eligible releases once per batch, newest availability first."""
    versions = []
    for path in (Path(root) / AI_WATCHLIST_DIR).glob('investment-*-ai-watchlist*.json'):
        match = FILENAME.fullmatch(path.name)
        if not match or match[2] == '1':
            raise ValueError(f'invalid AI watchlist filename: {path.name}')
        if date.fromisoformat(match[1]) > until.astimezone(ZONE).date():
            continue
        raw = path.read_bytes()
        doc = _strict_json(raw, 'AI watchlist')
        if not isinstance(doc, dict) or set(doc) != {'available_at', 'entries'}:
            raise ValueError(f'invalid AI watchlist fields: {path}')
        available = _timestamp(doc['available_at'], 'AI watchlist available_at').astimezone(ZONE)
        if available.date().isoformat() != match[1]:
            raise ValueError(f'AI watchlist availability differs from filename: {path}')
        if available > until:
            continue
        entries = doc['entries']
        if not isinstance(entries, dict):
            raise ValueError(f'invalid AI watchlist entries: {path}')
        for code, row in entries.items():
            if (not CODE.fullmatch(code) or not isinstance(row, dict) or set(row) != FIELDS
                    or not all(isinstance(v, str) and v.strip() for v in row.values())):
                raise ValueError(f'invalid AI watchlist entry: {code}')
            url = urlsplit(row['source_url'])
            if (url.scheme != 'https' or not url.hostname
                    or date.fromisoformat(row['source_date']) > available.date()):
                raise ValueError(f'invalid AI watchlist source: {code}')
        versions.append((available, path.name, hashlib.sha256(raw).hexdigest(), entries))
    if len({v[0] for v in versions}) != len(versions):
        raise ValueError('ambiguous AI watchlist availability')
    return sorted(versions, reverse=True)


def lookup(versions, code, until):
    if not CODE.fullmatch(code):
        raise ValueError(f'invalid AI watchlist security code: {code}')
    for available, name, digest, entries in versions:
        if available <= until:
            return dict(version=name, sha256=digest, code=code, entry=entries.get(code))
    return None


def freeze(root, request):
    until = min(cutoff(request['valuation_date']), cutoff(request['created_at']))
    versions = releases(root, until)
    if not versions:
        return {}
    result = {}
    for task in request['tasks']:
        meta = task['data_pack_meta']
        revision = meta.get('historical_valuation_revision') or {}
        if not isinstance(revision, dict):
            raise ValueError('invalid historical valuation revision')
        limits = [until]
        for field in (meta, revision):
            if field.get('evidence_cutoff'):
                limits.append(cutoff(field['evidence_cutoff']))
        record = lookup(versions, task['code'], min(limits))
        if record:
            result[task['task_id']] = record
    return result


def instructions(record, strategy):
    if record is None:
        return ''
    header = f"AI 业务重点核验名单 {record['version']}（sha256 {record['sha256']}），证券 {record['code']}。"
    if record['entry'] is None:
        if strategy == 'dividend':
            return header + '未列入，按本批红利主策略研究。\n\n'
        return (header + '未列入。普通策略发现有实质影响的 AI 业务仍可启用本批 ai_business_supplement.md 的适用业务行，'
                '将依据和建议纳入名单的线索写入报告；无实质影响可直接略过。\n\n')
    row = record['entry']
    source = f"{row['source_title']}，{row['source_date']}，{row['source_url']}"
    text = (f"{header}名单内。{row['name']}｜{row['business']}。已有线索：{row['evidence']}（{source}）。"
            f"本次核验：{row['check']} 核对截止时点可得原始披露。报告 §0 单列一行"
            '“AI专项：启用｜理由：具体业务、证据及价值影响”或“AI专项：跳过｜理由：具体原因”。')
    if strategy == 'dividend':
        return text + '本次为红利主策略，选跳过并说明红利策略及相关投入对可分配现金的影响。\n\n'
    return (text + '普通策略按利润、现金流或现价隐含预期的重要性作结论，启用时把本批 '
            'ai_business_supplement.md 的适用业务行并入原报告；手工选定红利主策略时选跳过。\n\n')


def validate_decision(section_zero, record, strategy):
    if record is None or record['entry'] is None:
        return
    # The prompt asks for one visible line so ambiguous or empty decisions are caught.
    plain = section_zero.replace('**', '')
    decisions = re.findall(r'(?m)^[ \t]*(?:[-*] )?AI专项[：:][ \t]*(启用|跳过)[ \t]*[｜|][ \t]*理由[：:]([^\n]*)$', plain)
    if (len(decisions) != 1 or not decisions[0][1].strip()
            or (strategy == 'dividend' and decisions[0][0] != '跳过')):
        raise ValueError('AI watchlist: section 0 requires one applicable decision and reason')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', help='Shanghai date or ISO timestamp with timezone')
    parser.add_argument('--code', help='e.g. 00700.HK; omit to list the entire effective release')
    args = parser.parse_args()
    until = cutoff(args.as_of) if args.as_of else datetime.now(ZONE)
    versions = releases(ROOT, until)
    if args.code:
        result = lookup(versions, args.code, until)
    elif versions:
        _, version, digest, entries = versions[0]
        result = dict(version=version, sha256=digest, entries=entries)
    else:
        result = None
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
