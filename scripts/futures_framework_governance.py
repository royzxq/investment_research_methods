"""Read-only structural checks for the full and compact futures frameworks.

CLI: python3 scripts/futures_framework_governance.py --check
Without --check, report file sizes only. Neither mode writes or generates files.
The compact version is independently condensed, not copied from a marked block.
Checks do not establish semantic equivalence, rule validity, or evidence truth.
"""

import argparse
from collections import Counter
from html import unescape
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = Path("framework/futures_framework.md")
COMPACT = Path("framework/futures_framework_compact.md")
FRAMEWORK_FILES = (CANONICAL, COMPACT, Path("framework/FUTURES_DATA_PROTOCOL.md"))
# Stable compact rule IDs at the v2.27 baseline. Additional IDs are allowed;
# deleting/renaming an existing ID requires an explicit migration here.
# This manifest checks identities only, not the meaning behind each identity.
EXPECTED_COMPACT_ANCHORS = frozenset("""
r-pool-core r-pool-backup r-pool-signal r-pool-scan r-pool-sleep
r-route-near r-route-far r-route-structure r-data-authority r-pool-independent
r-cal-lookahead r-cal-cross r-cal-day r-reg-trigger r-reg-tail
r-reg-correlation r-reg-exchange r-cal-timestamp r-state-density r-reg-set
r-reg-geop r-roll-days r-roll-direction r-roll-structure r-roll-plan
r-roll-target r-roll-timing r-roll-reset r-roll-sc r-pre-preview
r-input-price r-input-spread r-input-status r-input-scope r-input-manual
r-input-state r-data-feasibility r-data-snapshot r-data-reference r-data-fields
r-data-lineage r-data-quality r-input-preparation r-gate-1 r-gate-2
r-gate-3 r-gate-4 r-gate-5 r-gate-6 r-gate-7
r-gate-8 r-gate-9 r-gate-10 r-gate-11 r-gate-12
r-gate-13 r-gate-14 r-gate-15 r-gate-16 r-gate-17
r-gate-18 r-gate-19 r-gate-20 r-gate-21 r-gate-22
r-gate-23 r-gate-24 r-gate-25 r-gate-26 r-gate-27
r-gate-28 r-gate-29 r-gate-30 r-gate-31 r-soft-d12
r-soft-ma r-soft-chain r-soft-lowadx r-soft-beta r-gate-calm
r-gate-resume r-gate-long r-gate-equity r-gate-policy r-gate-capacity
r-gate-carry r-gate-cu r-trigger-b r-trigger-c r-trigger-d
r-trigger-e r-trigger-fg r-param-d r-param-a r-param-f
r-param-e r-param-g r-param-c r-param-b r-param-overnight
r-param-caps r-trigger-b-window r-weight-a r-weight-d r-weight-f
r-weight-g r-weight-c r-weight-b r-weight-evidence r-d9-levels
r-d10-score r-d8-definition r-d8-fin-long r-d8-fin-short r-d8-commodity
r-d11-bands r-d12-trigger r-d12-bands r-d12-diverge r-d13-cost
r-d13-freeze r-d14-restart r-d14-water r-d14-stock r-d14-pass
r-d15 r-pen-narrative r-pen-fixed r-factor-groups r-factor-nearhigh
r-factor-correlation r-factor-policy r-score-normalize r-conf-definition r-conf-prospective
r-score-d1 r-score-d2 r-score-d3 r-score-d4 r-score-d5
r-conf-owner r-latent-h r-latent-jmrb r-latent-curve r-latent-ps
r-latent-lh r-latent-spread-screen r-a-definition r-a-screen r-a-reversion
r-a-continuation r-a-fields r-a-median r-a-stop r-a-cost
r-a-r r-a-fill r-a-legs r-a-stress r-a-expiry
r-a-overrides r-plan-style r-plan-d-time r-plan-d-exit r-plan-e
r-plan-f r-plan-g r-plan-c r-plan-b r-risk-caps
r-risk-regime r-risk-unit r-risk-factor r-risk-used r-risk-add
r-risk-round r-risk-final r-risk-dedup r-risk-tool r-risk-snapshot
r-risk-net r-risk-profit r-risk-margin r-risk-limit r-risk-reserve
r-risk-null r-risk-recal r-risk-structure-recal r-risk-stock-regime r-plan-f-validation
r-plan-h-params r-plan-au-break r-plan-b-time r-plan-b-version r-plan-b-history
r-plan-b-economics r-plan-b-trail r-manage-stop r-manage-profit r-manage-driver
r-manage-f r-manage-d9 r-manage-event r-manage-geop r-manage-exchange
r-manage-au r-manage-top r-manage-policy r-manage-rb r-manage-ma
r-manage-agri r-swap-same r-swap-cross r-swap-d8 r-manage-no-account
r-manage-tail r-manage-dormant r-manage-cu r-gap-active r-gap-latent
r-gap-definition r-gap-action r-audit-weekly r-audit-unit r-audit-coverage
r-audit-no r-audit-incomplete r-audit-block r-audit-awaiting r-audit-ready
r-audit-only r-audit-account r-audit-wording r-audit-pending r-audit-fields
r-audit-shadow r-audit-rule-review r-audit-gap-owner r-audit-retraction r-card-ma
r-card-ma-week r-card-ma-month r-card-ma-inventory r-card-ma-price r-card-rb
r-card-rb-manage r-card-m r-card-sr r-card-cf r-card-au
r-card-sc r-revive-commod r-revive-lc r-revive-finance r-revive-structures
r-revive-si r-dynamic-version r-dynamic-caps r-dynamic-pool r-dynamic-frequency
r-dynamic-mult r-dynamic-roll-ma r-dynamic-roll-rb r-dynamic-roll-agri r-dynamic-roll-signal
r-dynamic-roll-table r-dynamic-regime r-dynamic-cpi r-dynamic-iron-sample r-dynamic-events
r-dynamic-gap r-dynamic-freezes r-dynamic-deadline r-dynamic-pv-date r-dynamic-pending
r-dynamic-overreact r-dynamic-narratives
""".split())
HTML_ID = re.compile(r"\bid\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
INLINE_LINK = re.compile(
    r"!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)(?:\s+[\"'][^\n]*?[\"'])?\s*\)"
)
UPDATE_NOTE = re.compile(r"【(?:本次更新|v\d+\.\d+)[^】\r\n]*】", re.IGNORECASE)


def without_fenced_code(source):
    """Exclude common Markdown fences, retaining line breaks for readable checks."""
    lines = []
    fence = None
    for line in source.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence is None:
            if match:
                fence = match.group(1)
            else:
                lines.append(line)
        elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
            fence = None
    return "\n".join(lines)


def anchors_in(source):
    """Return explicit IDs and common ATX-heading IDs for local Markdown links.

    Heading slugs follow the usual lowercase/punctuation-stripping convention.
    This is not a complete renderer for every Markdown extension.
    """
    text = without_fenced_code(source)
    explicit = HTML_ID.findall(text)
    anchors = set(explicit)
    heading_counts = Counter()
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]*>", "", match.group(1))
        heading = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", unescape(heading).lower())
        slug = re.sub(r"\s", "-", slug)
        duplicate = heading_counts[slug]
        heading_counts[slug] += 1
        anchors.add(f"{slug}-{duplicate}" if duplicate else slug)
    return explicit, anchors


def _read(path, cache):
    key = path.resolve()
    if key not in cache:
        cache[key] = path.read_bytes().decode("utf-8")
    return cache[key]


def _link_errors(root, relative_path, source, cache):
    errors = []
    for match in INLINE_LINK.finditer(without_fenced_code(source)):
        destination = match.group(1).strip("<>")
        try:
            parsed = urlsplit(destination)
        except ValueError:
            errors.append(f"{relative_path}: malformed link {destination!r}")
            continue
        if parsed.scheme or parsed.netloc:
            continue
        target = (root / relative_path.parent / unquote(parsed.path)
                  if parsed.path else root / relative_path)
        if not target.exists():
            errors.append(f"{relative_path}: missing local link target {destination!r}")
            continue
        if parsed.fragment and target.suffix.lower() == ".md":
            try:
                _, target_anchors = anchors_in(_read(target, cache))
            except (OSError, UnicodeError) as exc:
                errors.append(f"{relative_path}: cannot read linked Markdown {destination!r}: {exc}")
                continue
            if unquote(parsed.fragment) not in target_anchors:
                errors.append(f"{relative_path}: missing local anchor {destination!r}")
    return errors


def inspect(root=ROOT):
    """Return (size reports, structural errors) without modifying any files."""
    root = Path(root)
    reports = []
    errors = []
    cache = {}
    for relative_path in FRAMEWORK_FILES:
        try:
            source = _read(root / relative_path, cache)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative_path}: cannot read UTF-8 file: {exc}")
            continue
        explicit, _ = anchors_in(source)
        reports.append({"path": str(relative_path), "bytes": len(source.encode("utf-8")),
                        "lines": len(source.splitlines()), "explicit_anchors": len(explicit)})
        duplicates = sorted(anchor for anchor, count in Counter(explicit).items() if count > 1)
        if duplicates:
            errors.append(f"{relative_path}: duplicate anchor IDs: {', '.join(duplicates)}")
        if relative_path == COMPACT:
            missing = sorted(EXPECTED_COMPACT_ANCHORS - set(explicit))
            if missing:
                errors.append(f"{relative_path}: missing stable rule anchors: {', '.join(missing)}")
        if relative_path in (CANONICAL, COMPACT) and UPDATE_NOTE.search(source):
            errors.append(f"{relative_path}: remove inline historical update notes; preserve effective rules")
        errors.extend(_link_errors(root, relative_path, source, cache))
    return reports, errors


def check(root=ROOT):
    """Return structural errors only; no generation or size ceilings."""
    return inspect(root)[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: script's repository)")
    parser.add_argument("--check", action="store_true", help="validate rule anchors, local links, and historical notes")
    args = parser.parse_args(argv)
    reports, errors = inspect(args.root)
    for report in reports:
        print(f"{report['path']}: {report['bytes']:,} UTF-8 bytes, "
              f"{report['lines']:,} lines, {report['explicit_anchors']} explicit anchors")
    if args.check:
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("Structural checks passed; semantic equivalence and investment validity are not verified.")
    elif len(reports) != len(FRAMEWORK_FILES):
        for error in errors:
            if "cannot read UTF-8 file" in error:
                print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
