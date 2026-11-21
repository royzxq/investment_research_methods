"""Read-only stock framework structure checks; not evidence or method validation."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

try:
    from .investment_maintenance import method_fingerprint
    from . import stock_framework_bundle
except ImportError:
    from investment_maintenance import method_fingerprint
    import stock_framework_bundle


ROOT = Path(__file__).resolve().parents[1]
FILES = ("investment_framework.md", "investment_framework_compact.md")
STRATEGY_SCOPE = "<!-- stock-strategy-scope: non_dividend; migrated-rules: R9=dividend-HD6 -->"


def check(root=ROOT):
    texts, versions, states, fingerprints = {}, [], [], {}
    for name in FILES:
        raw = (Path(root) / "framework" / name).read_bytes()
        text = raw.decode("utf-8")
        texts[name] = text
        versions_here = re.findall(r"<!-- investment-method-version: ([\w.-]+) -->", text)
        if len(versions_here) != 1:
            raise ValueError(f"{name}: require one method version")
        versions += versions_here
        fingerprints[name] = method_fingerprint(raw)
        match = re.search(r"<!-- investment-state:start -->\s*```json\s*\n(.*?)\n```\s*<!-- investment-state:end -->", text, re.S)
        if match is None:
            raise ValueError(f"{name}: missing validated observations block")
        states.append(json.loads(match[1]))
        for placeholder in ("COMPANY_NAME", "TICKER_OR_CODE", "VALUATION_DATE"):
            if "{{" + placeholder + "}}" not in text:
                raise ValueError(f"{name}: missing {placeholder} placeholder")
    if len(set(versions)) != 1:
        raise ValueError("Canonical and compact method versions differ")
    if states[0] != states[1]:
        raise ValueError("Canonical and compact observation snapshots differ")
    compact = texts[FILES[1]]
    for prefix, total in (("R", 22), ("D", 8)):
        definitions = Counter(re.findall(rf"(?m)^- \*\*({prefix}\d+)\s", compact))
        expected = {f"{prefix}{i}" for i in range(1, total + 1)}
        if set(definitions) != expected or any(n != 1 for n in definitions.values()):
            raise ValueError(f"{prefix} definitions missing, duplicated or unexpectedly renumbered")
        references = set(re.findall(rf"\[({prefix}\d+)\]", compact))
        if references - expected:
            raise ValueError(f"Undefined {prefix} references: {sorted(references - expected)}")
    contents = stock_framework_bundle.capture(Path(root) / "framework")
    scoped = any("stock-strategy-scope:" in texts[name] for name in FILES)
    if scoped or versions[0].startswith("stock-strategy-split-v2-"):
        if any(texts[name].count(STRATEGY_SCOPE) != 1 for name in FILES):
            raise ValueError("Strategy scope must agree in canonical and compact")
        if not set(stock_framework_bundle.STRATEGY_BUNDLE).issubset(contents):
            raise ValueError("Migrated rules require the full strategy bundle")
        # R9 is a migration index, not a live dependency of non-dividend rules.
        if "[R9]" in compact:
            raise ValueError("Migrated R9 cannot remain an active compact reference")
        r9 = next(line for line in compact.splitlines() if line.startswith("- **R9 "))
        if "已迁出" not in r9 or "dividend_framework.md#hd6" not in r9:
            raise ValueError("R9 must retain its migration destination")
        if any("### HD4A " not in contents[name].decode()
               for name in ("dividend_framework.md", "dividend_framework_compact.md")):
            raise ValueError("Migrated dividend model needs canonical and compact HD4A")
    for supplement in (stock_framework_bundle.AI_SUPPLEMENT, stock_framework_bundle.PIPELINE_SUPPLEMENT):
        link = f"]({supplement})"
        expected_count = int(supplement in contents)
        entries = [[line for line in texts[name].splitlines() if link in line] for name in FILES]
        if any(texts[name].count(link) != expected_count for name in FILES) or entries[0] != entries[1]:
            raise ValueError(f"{supplement} entry must match the signed bundle and agree in both editions")
    if set(stock_framework_bundle.STRATEGY_BUNDLE).issubset(contents):
        dividend_versions = []
        for name in ("dividend_framework.md", "dividend_framework_compact.md"):
            body = contents[name].decode()
            version = re.findall(r"<!-- dividend-method-version: ([\w.-]+) -->", body)
            if len(version) != 1:
                raise ValueError("require one dividend method version")
            dividend_versions += version
            pattern = r"(?m)^## (HD\d+) " if name == "dividend_framework.md" else r"(?m)^- \*\*(HD\d+) "
            found = Counter(re.findall(pattern, body))
            if found != Counter({f"HD{i}": 1 for i in range(1, 9)}):
                raise ValueError("dividend definitions missing or duplicated")
        if len(set(dividend_versions)) != 1:
            raise ValueError("dividend method versions differ")
        for name in stock_framework_bundle.DEPENDENCIES:
            if name not in contents:
                continue
            texts[name] = contents[name].decode()
            fingerprints[name] = method_fingerprint(contents[name])
        template = texts['dividend_report_template.md']
        if re.findall(r'(?m)^## ([0-8])\.', template) != list('012345678'):
            raise ValueError('dividend report must retain nine sections')
    return {"status": "passed", "method_version": versions[0],
            "strategy_scope": "non_dividend; R9 -> dividend-HD6" if scoped else "legacy",
            "state_as_of": states[0]["as_of"], "method_fingerprints": fingerprints,
            "sizes": {name: {"bytes": len(text.encode("utf-8")), "lines": len(text.splitlines())}
                      for name, text in texts.items()},
            "limits": "Structure only; not complete semantic equivalence, evidence truth or investment effectiveness"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Run read-only structure checks")
    args = parser.parse_args()
    try:
        result = check(args.root)
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(1, f"Stock framework check failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
