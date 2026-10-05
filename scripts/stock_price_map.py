"""Offline arithmetic and compact export for stock-research/v2.

This checks units, arithmetic and output states, not evidence or Gate decisions.
Research assumptions belong in the report; build inputs stay in scratch output/.
"""

import argparse
from datetime import date
from decimal import Decimal, DecimalException, ROUND_HALF_UP, localcontext
import json
from pathlib import Path
import re
import sys


SCHEMA = "stock-research/v2"
RANGE_KEYS = {"low", "base", "high"}
DISCOUNT_KEYS = {"d_base", "r_chip", "r_v5", "r_gov", "r_terminal"}
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


def validate_meta(meta, exported=False):
    fields(meta, META_KEYS | ({"schema_version"} if exported else set()), "meta",
           optional=set() if exported else {"schema_version"})
    for k in META_KEYS:
        string(meta[k], f"meta.{k}")
    require(re.fullmatch(r"(?:\d{6}\.(?:SH|SZ|BJ)|\d{5}\.HK)", meta["code"]), "meta.code: unsupported code")
    expected = "HKD" if meta["code"].endswith(".HK") else "CNY"
    require(meta["currency"] == expected, "meta.currency: inconsistent with listing market")
    iso_date(meta["valuation_date"], "meta.valuation_date")
    if "schema_version" in meta:
        require(meta["schema_version"] == SCHEMA, "meta.schema_version: unsupported version")


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
    fields(data, {"meta", "mode", "reason", "valuation", "discounts", "step_down", "p2", "t1", "t2", "monitoring"}, "input")
    validate_meta(data["meta"])
    validate_mode(data["mode"], data["reason"])
    validate_p2(data["p2"])
    priced = data["mode"] in PRICED_MODES
    currency = data["meta"]["currency"]
    with localcontext() as ctx:
        ctx.prec = 40
        v50 = per_share_values(data["valuation"], currency) if data["valuation"] is not None else None
        p1 = p2_price = None
        if priced:
            require(v50 is not None, "priced mode requires valuation; use unavailable with a reason")
            fields(data["discounts"], DISCOUNT_KEYS, "discounts")
            factor = Decimal(1)
            for k in sorted(DISCOUNT_KEYS):
                discount = number(data["discounts"][k], f"discounts.{k}")
                require(0 <= discount < 1, f"discounts.{k}: expected [0,1)")
                factor *= 1 - discount
            step = number(data["step_down"], "step_down")
            require(Decimal("0.05") <= step <= Decimal("0.10"), "step_down: expected 0.05-0.10")
            raw_p1 = {k: v * factor for k, v in v50.items()}
            p1 = {k: round_price(v, currency) for k, v in raw_p1.items()}
            if data["p2"]["status"] in {"active", "suspended"}:
                p2_price = round_price(raw_p1["low"] * (1 - step), currency)
        else:
            require(data["discounts"] is None and data["step_down"] is None,
                    "unpriced mode: discounts and step_down must be null")
            require(data["p2"]["status"] in {"cancelled", "unavailable"},
                    "unpriced mode: p2 must be cancelled or unavailable")
        result = {
            "meta": dict(data["meta"], schema_version=SCHEMA),
            "price_map": {
                "mode": data["mode"], "reason": data["reason"],
                "v50": None if v50 is None else {k: round_price(v, currency) for k, v in v50.items()},
                "p1": p1, "p2": dict(data["p2"], price=p2_price),
                "t1": data["t1"], "t2": data["t2"],
            },
            "monitoring": data["monitoring"],
        }
    validate_document(result)
    return result


def validate_document(document):
    """Validate exported state/types; discounts and evidence require build/report."""
    fields(document, {"meta", "price_map", "monitoring"}, "document")
    validate_meta(document["meta"], exported=True)
    p = document["price_map"]
    fields(p, {"mode", "reason", "v50", "p1", "p2", "t1", "t2"}, "price_map")
    validate_mode(p["mode"], p["reason"])
    validate_p2(p["p2"], exported=True)
    v50 = numeric_range(p["v50"], "v50") if p["v50"] is not None else None
    p1 = numeric_range(p["p1"], "p1") if p["p1"] is not None else None
    tick = quantum(document["meta"]["currency"])
    prices = [v for values in (v50, p1) if values is not None for v in values.values()]
    if p["p2"]["price"] is not None:
        prices.append(number(p["p2"]["price"], "p2.price", positive=True))
    for price in prices:
        require(price % tick == 0, "exported price exceeds currency precision")
    if p["mode"] in PRICED_MODES:
        require(v50 is not None and p1 is not None, "priced mode requires v50 and p1")
        require(all(p1[k] <= v50[k] for k in RANGE_KEYS), "p1 exceeds v50")
        if p["p2"]["status"] in {"active", "suspended"}:
            price = number(p["p2"]["price"], "p2.price", positive=True)
            tolerance = quantum(document["meta"]["currency"])
            require(p1["low"] * Decimal("0.90") - tolerance <= price <= p1["low"] * Decimal("0.95") + tolerance,
                    "p2.price inconsistent with P1_low and 5%-10% step")
        else:
            require(p["p2"]["price"] is None, "cancelled/unavailable p2 must have null price")
    else:
        require(p1 is None and p["p2"]["status"] in {"cancelled", "unavailable"}
                and p["p2"]["price"] is None, "unpriced mode must not publish entry prices")
    validate_triggers(p["t1"], "t1")
    validate_triggers(p["t2"], "t2")
    validate_monitoring(document["monitoring"], document["meta"]["valuation_date"])


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
    build = sub.add_parser("build", help="calculate from researched scratch assumptions; never overwrite")
    build.add_argument("--input", required=True)
    build.add_argument("--output", required=True)
    check = sub.add_parser("check", help="validate v2 structure/state, not facts or full arithmetic")
    check.add_argument("file")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = build_document(load_json(args.input))
            payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False, default=json_number) + "\n"
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(payload)
            print(f"Built {args.output}; arithmetic/state checked, research evidence not checked")
        else:
            validate_document(load_json(args.file))
            print(f"Valid {SCHEMA}; structure/state only, evidence and discount assumptions not checked")
    except (ValueError, TypeError, OSError, DecimalException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
