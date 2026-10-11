"""Read-only stock framework structure checks; not evidence or method validation."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

try:
    from .investment_maintenance import method_fingerprint
except ImportError:
    from investment_maintenance import method_fingerprint


ROOT = Path(__file__).resolve().parents[1]
FILES = ("investment_framework.md", "investment_framework_compact.md")


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
    for prefix, total in (("R", 21), ("D", 8)):
        definitions = Counter(re.findall(rf"(?m)^- \*\*({prefix}\d+)\s", compact))
        expected = {f"{prefix}{i}" for i in range(1, total + 1)}
        if set(definitions) != expected or any(n != 1 for n in definitions.values()):
            raise ValueError(f"{prefix} definitions missing, duplicated or unexpectedly renumbered")
        references = set(re.findall(rf"\[({prefix}\d+)\]", compact))
        if references - expected:
            raise ValueError(f"Undefined {prefix} references: {sorted(references - expected)}")
    return {"status": "passed", "method_version": versions[0],
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
