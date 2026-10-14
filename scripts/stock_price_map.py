"""Export report quotes as stock-research/v3; read historical v2 documents.

P1/P2 are explicit report quotes, never derived from V50 during export.
This checks units, precision and states, not report semantics or Gate decisions.
"""

import argparse
from copy import deepcopy
from datetime import date
from decimal import Decimal, DecimalException, ROUND_HALF_UP, localcontext
import json
from pathlib import Path
import re
import sys


SCHEMA = "stock-research/v3"
SUPPORTED_SCHEMAS = {"stock-research/v2", SCHEMA}
RANGE_KEYS = {"low", "base", "high"}
PRICED_MODES = {"buy_candidate", "tracking", "observation"}
MODES = PRICED_MODES | {"frozen", "rejected", "unavailable"}
P2_STATES = {"active", "cancelled", "suspended", "unavailable"}
META_KEYS = {"code", "name", "valuation_date", "currency", "report_path"}
MONITOR_KEYS = {"variable", "current", "as_of", "trigger", "action", "source", "next_check"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(value, required, label, optional=frozenset()):
    require(isinstance(value, dict), f"{label}: expected object")
    require(required <= value.keys() <= required | optional,
            f"{label}: missing {sorted(required - value.keys())}; "
            f"unexpected {sorted(value.keys() - required - optional)}")


def string(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: expected nonempty string")
    return value


def number(value, label, positive=False):
    require(isinstance(value, (int, float, Decimal)) and not isinstance(value, bool),
            f"{label}: expected number, not boolean/string/null")
    result = Decimal(str(value))
    require(result.is_finite(), f"{label}: nonfinite number")
    if positive:
        require(result > 0, f"{label}: must be positive")
    return result


def iso_date(value, label):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value),
            f"{label}: expected YYYY-MM-DD")
    return date.fromisoformat(value)


def numeric_range(value, label):
    fields(value, RANGE_KEYS, label)
    result = {k: number(value[k], f"{label}.{k}", positive=True) for k in ("low", "base", "high")}
    require(result["low"] <= result["base"] <= result["high"], f"{label}: unordered range")
    return result


def p1_quotes(value):
    """A report's explicit point and/or interval; never invent missing quotes."""
    fields(value, {"base"}, "p1", optional={"low", "high"})
    has_range = "low" in value or "high" in value
    require(not has_range or {"low", "high"} <= value.keys(), "p1: interval requires both low and high")
    result = {}
    if value["base"] is not None:
        result["base"] = number(value["base"], "p1.base", positive=True)
    require(result or has_range, "p1: explicit base quote or interval required")
    if has_range:
        result.update({k: number(value[k], f"p1.{k}", positive=True) for k in ("low", "high")})
        require(result["low"] <= result["high"], "p1: unordered interval")
        if "base" in result:
            require(result["low"] <= result["base"] <= result["high"], "p1: base outside interval")
    return result


def validate_meta(meta, exported=False):
    fields(meta, META_KEYS | ({"schema_version"} if exported else set()), "meta",
           optional={"generator"} if exported else {"schema_version", "generator"})
    if "generator" in meta:
        require(meta["generator"] in ("codex", "claude"), "meta.generator: expected codex or claude")
    for k in META_KEYS:
        string(meta[k], f"meta.{k}")
    require(re.fullmatch(r"(?:\d{6}\.(?:SH|SZ|BJ)|\d{5}\.HK)", meta["code"]), "meta.code: unsupported code")
    expected = "HKD" if meta["code"].endswith(".HK") else "CNY"
    require(meta["currency"] == expected, "meta.currency: inconsistent with listing market")
    iso_date(meta["valuation_date"], "meta.valuation_date")
    if "schema_version" in meta:
        require(isinstance(meta["schema_version"], str)
                and meta["schema_version"] in (SUPPORTED_SCHEMAS if exported else {SCHEMA}),
                "meta.schema_version: unsupported version")


def validate_monitoring(items, valuation_date):
    require(isinstance(items, list) and 1 <= len(items) <= 10, "monitoring: expected 1-10 items")
    seen = set()
    for i, item in enumerate(items):
        label = f"monitoring[{i}]"
        fields(item, MONITOR_KEYS, label)
        for k in MONITOR_KEYS - {"current", "as_of"}:
            string(item[k], f"{label}.{k}")
        name = item["variable"].strip()
        require(name not in seen, f"{label}: duplicate variable")
        seen.add(name)
        current = item["current"]
        if current is not None:
            if isinstance(current, str):
                string(current, f"{label}.current")
            else:
                number(current, f"{label}.current")
            require(item["as_of"] is not None, f"{label}: observed current requires as_of")
        if item["as_of"] is not None:
            require(iso_date(item["as_of"], f"{label}.as_of") <= date.fromisoformat(valuation_date),
                    f"{label}: future observation")


def validate_triggers(value, label):
    fields(value, {"price_condition", "events"}, label)
    string(value["price_condition"], f"{label}.price_condition")
    require(isinstance(value["events"], list) and value["events"], f"{label}.events: empty")
    for event in value["events"]:
        string(event, f"{label}.events")


def validate_mode(mode, reason):
    require(isinstance(mode, str) and mode in MODES, "price_map.mode: unsupported mode")
    if mode != "buy_candidate" or reason is not None:
        string(reason, "price_map.reason")


def validate_p2(value, exported=False):
    fields(value, {"status", "reason"} | ({"price"} if exported else set()), "p2")
    require(isinstance(value["status"], str) and value["status"] in P2_STATES, "p2.status: unsupported state")
    if value["status"] != "active" or value["reason"] is not None:
        string(value["reason"], "p2.reason")


def quote_value(amount, fx_to_quote):
    """Multiply source-currency amount by quote currency per source unit."""
    return number(amount, "amount") * number(fx_to_quote, "fx_to_quote", positive=True)


def per_share_values(valuation, quote_currency):
    base_keys = {"kind", "values", "currency", "unit", "fx_to_quote"}
    fields(valuation, base_keys, "valuation", optional={"shares", "fx_source"})
    require(valuation["currency"] in ("CNY", "HKD"), "valuation.currency: expected CNY/HKD")
    values = numeric_range(valuation["values"], "valuation.values")
    fx = number(valuation["fx_to_quote"], "valuation.fx_to_quote", positive=True)
    if valuation["currency"] == quote_currency:
        require(fx == 1, "valuation.fx_to_quote: same currency must use 1")
    else:
        string(valuation.get("fx_source"), "valuation.fx_source")
    if valuation["kind"] == "equity_value":
        units = {"currency": Decimal(1), "million": Decimal(10) ** 6, "100_million": Decimal(10) ** 8}
        require(isinstance(valuation["unit"], str) and valuation["unit"] in units, "valuation.unit: expected equity value unit")
        shares = number(valuation.get("shares"), "valuation.shares", positive=True)
        require(shares == shares.to_integral_value(), "valuation.shares: use actual whole shares")
        scale = units[valuation["unit"]] / shares
    else:
        require(valuation["kind"] == "per_share", "valuation.kind: expected equity_value/per_share")
        require(valuation["unit"] == "per_share" and "shares" not in valuation,
                "valuation: per_share requires per_share unit and no shares")
        scale = Decimal(1)
    return {k: quote_value(v, fx) * scale for k, v in values.items()}


def quantum(currency):
    return Decimal("0.001" if currency == "HKD" else "0.01")


def round_price(value, currency):
    return float(value.quantize(quantum(currency), rounding=ROUND_HALF_UP))


def build_document(data):
    fields(data, {"meta", "mode", "reason", "valuation", "p1", "p2", "t1", "t2", "monitoring"}, "input")
    validate_meta(data["meta"])
    validate_mode(data["mode"], data["reason"])
    validate_p2(data["p2"], exported=True)
    currency = data["meta"]["currency"]
    with localcontext() as ctx:
        ctx.prec = 40
        v50 = per_share_values(data["valuation"], currency) if data["valuation"] is not None else None
        result = {
            "meta": dict(data["meta"], schema_version=SCHEMA),
            "price_map": {
                "mode": data["mode"], "reason": data["reason"],
                "v50": None if v50 is None else {k: round_price(v, currency) for k, v in v50.items()},
                "p1": deepcopy(data["p1"]), "p2": deepcopy(data["p2"]),
                "t1": deepcopy(data["t1"]), "t2": deepcopy(data["t2"]),
            },
            "monitoring": deepcopy(data["monitoring"]),
        }
    validate_document(result)
    validate_price_references(result)
    validate_t1_delivery(result)
    return result


def validate_document(document):
    """Validate quotes/states; research assumptions and extraction need review."""
    fields(document, {"meta", "price_map", "monitoring"}, "document")
    validate_meta(document["meta"], exported=True)
    p = document["price_map"]
    fields(p, {"mode", "reason", "v50", "p1", "p2", "t1", "t2"}, "price_map")
    validate_mode(p["mode"], p["reason"])
    validate_p2(p["p2"], exported=True)
    v50 = numeric_range(p["v50"], "v50") if p["v50"] is not None else None
    legacy = document["meta"]["schema_version"] == "stock-research/v2"
    p1 = None
    if p["p1"] is not None:
        p1 = numeric_range(p["p1"], "p1") if legacy else p1_quotes(p["p1"])
    tick = quantum(document["meta"]["currency"])
    prices = [v for values in (v50, p1) if values is not None for v in values.values()]
    if p["p2"]["price"] is not None:
        prices.append(number(p["p2"]["price"], "p2.price", positive=True))
    for price in prices:
        require(price % tick == 0, "exported price exceeds currency precision")
        if not legacy:
            require(number(float(price), "exported price", positive=True) == price,
                    "exported price cannot be serialized without changing quote")
    frozen_priced = p["mode"] == "frozen" and p1 is not None
    if frozen_priced:
        require(p["p2"]["status"] in {"suspended", "cancelled"},
                "frozen observation prices: p2 must be suspended or cancelled")
    if p["mode"] in PRICED_MODES or frozen_priced:
        require(v50 is not None and p1 is not None, "priced mode requires v50 and p1")
        if legacy:
            require(all(p1[k] <= v50[k] for k in RANGE_KEYS), "p1 exceeds v50")
        if p["p2"]["status"] in {"active", "suspended"}:
            price = number(p["p2"]["price"], "p2.price", positive=True)
            tolerance = quantum(document["meta"]["currency"])
            if "low" in p1:
                require(p1["low"] * Decimal("0.90") - tolerance <= price <= p1["low"] * Decimal("0.95") + tolerance,
                        "p2.price inconsistent with explicit P1_low and 5%-10% step")
            else:
                require(price < p1["base"], "p2.price must be below P1 quote; missing low is not base")
        else:
            require(p["p2"]["price"] is None, "cancelled/unavailable p2 must have null price")
    else:
        require(p1 is None and p["p2"]["status"] in {"cancelled", "unavailable"}
                and p["p2"]["price"] is None, "unpriced mode must not publish entry prices")
    validate_triggers(p["t1"], "t1")
    validate_triggers(p["t2"], "t2")
    validate_monitoring(document["monitoring"], document["meta"]["valuation_date"])


def validate_t1_delivery(document):
    """New-delivery grammar only; never applied to historical sealed loading."""
    p = document['price_map']
    condition = re.sub(r'\s+', '', string(p['t1']['price_condition'], 't1 delivery'))
    if condition in {'当前不适用', '本轮不提供T1报价'}:
        return None
    reference = re.fullmatch(r'接近V50(上沿|下沿|基准)时复核', condition)
    if reference:
        require(p['v50'] is not None, 't1 delivery: referenced V50 is absent')
        edge = {'上沿': 'high', '下沿': 'low', '基准': 'base'}[reference[1]]
        value = number(p['v50'][edge], 't1 delivery: V50 quote', positive=True)
    else:
        explicit = re.fullmatch(r'股价≥([0-9]+(?:\.[0-9]+)?)(港元|元|HKD|CNY)/股',
                                condition, re.I)
        require(explicit is not None,
                't1 delivery: use 股价≥金额元/股, 接近V50上沿/下沿/基准时复核, '
                '当前不适用 or 本轮不提供T1报价; put explanations in report')
        currency = document['meta']['currency']
        allowed = {'CNY': {'元', 'CNY'}, 'HKD': {'港元', 'HKD'}}[currency]
        require(explicit[2].upper() in allowed, 't1 delivery: quote currency mismatch')
        value = number(Decimal(explicit[1]), 't1 delivery: explicit quote', positive=True)
        digits = len(explicit[1].partition('.')[2].rstrip('0'))
        require(digits <= (3 if currency == 'HKD' else 2),
                't1 delivery: quote exceeds currency precision; do not silently round')
    # AI business quotes are floats. Overflow/underflow must not become an
    # accepted Infinity/zero even when the literal Decimal is a positive number.
    number(float(value), 't1 delivery: business quote', positive=True)
    return value


def validate_price_references(document):
    """New-delivery check; never retroactively invalidate sealed input loading."""
    p = document["price_map"]
    v50 = numeric_range(p["v50"], "v50") if p["v50"] is not None else None
    # Only check literal references to a named V50 boundary. Other amounts
    # (current quotes, independent thresholds) need not equal that boundary.
    if v50 is not None:
        for label in ("t1", "t2"):
            condition = re.sub(r"[\s*`]+", "", p[label]["price_condition"])
            for match in re.finditer(
                    r"V50(?:估值|区间|合理价值|价值)?(?:的)?(上沿|上限|高位|upper|下沿|下限|lower|中枢|基准|base)"
                    r"(?:为|[:：=（(])?(\d+(?:\.\d+)?)(?:港元|元|HKD|CNY)", condition, re.I):
                word = match[1].lower()
                edge = ("high" if word in ("上沿", "上限", "高位", "upper") else
                        "low" if word in ("下沿", "下限", "lower") else "base")
                require(abs(Decimal(match[2]) - v50[edge]) <= Decimal("0.011"),
                        f"{label}: quoted V50.{edge} {match[2]} disagrees with {v50[edge]}")


def no_duplicates(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, f"duplicate JSON key: {k}")
        result[k] = v
    return result


def reject_constant(value):
    raise ValueError(f"nonfinite JSON number: {value}")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=Decimal,
                      object_pairs_hook=no_duplicates, parse_constant=reject_constant)


def json_number(value):
    if isinstance(value, Decimal) and value.is_finite():
        return float(value)
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="export explicit report P1/P2 quotes; never derive or overwrite")
    build.add_argument("--input", required=True)
    build.add_argument("--output", required=True)
    build.add_argument("--generator", required=True, choices=["codex", "claude"],
                       help="Actual host producing the research, not the source of cited material")
    check = sub.add_parser("check", help="validate v3/v2 quotes and states, not report semantics")
    check.add_argument("file")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            data = load_json(args.input)
            require(isinstance(data, dict) and isinstance(data.get("meta"), dict), "input.meta: expected object")
            require(data["meta"].get("generator", args.generator) == args.generator,
                    "meta.generator conflicts with --generator")
            data["meta"]["generator"] = args.generator
            result = build_document(data)
            meta = result["meta"]
            stem = f"investment-{meta['code'].split('.')[0]}-{meta['valuation_date']}"
            pattern = rf"{re.escape(stem)}-price-map-{args.generator}(-r[2-9]\d*|-r1\d+)?\.json"
            match = re.fullmatch(pattern, Path(args.output).name)
            require(match, "output filename must include code/date and -price-map-<generator>[-rN].json")
            report_name = f"{stem}-research-{args.generator}{match[1] or ''}.md"
            require(Path(meta["report_path"]).name == report_name,
                    "meta.report_path must match output code/date/generator/revision")
            payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False, default=json_number) + "\n"
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(payload)
            print(f"Built {args.output}; report P1/P2 quotes preserved; structure/state checked, report semantics not checked")
        else:
            document = load_json(args.file)
            validate_document(document)
            validate_price_references(document)
            validate_t1_delivery(document)
            print(f"Valid {document['meta']['schema_version']}; structure/state/V50 references/T1 delivery checked; report extraction and research assumptions not checked")
    except (ValueError, TypeError, OSError, DecimalException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
