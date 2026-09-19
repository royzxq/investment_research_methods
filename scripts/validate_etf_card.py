"""Offline checks for ETF decision card schema 1 (reference: framework/etf_card_schema.md).

CLI: python scripts/validate_etf_card.py research/etf-cards/<card_id>-<as_of_date>.md [...]

A card is a Markdown file with exactly one fenced ``json`` block. Duplicate
keys, non-finite numbers and unknown keys are rejected. Every number sits in a
sourced-number object {"value", "source"} except a few structural integers;
``ai_estimate`` is accepted only on scenario assumptions. Where the inputs are
on the card, calculator outputs are recomputed with etf_calc; numbers citing
``snapshot§N`` must appear in that section of the referenced snapshot. No
network, no market data refresh: a valid card is internally consistent and
traceable, which does not make its thesis right.
"""

import argparse
from datetime import date
import inspect
import json
import math
from pathlib import Path
import re
import sys

try:
    from . import etf_calc
except ImportError:  # direct script invocation
    import etf_calc

SCHEMA_VERSION = 1
REPO_ROOT = Path(__file__).resolve().parents[1]

TASKS = {"core", "tactical", "defensive"}
STATUSES = {"active", "watch", "no_buy", "closed"}
NO_BUY_REASONS = {"thesis", "price", "tool", "portfolio", "data"}
CLOSE_REASONS = {"thesis_realized", "thesis_invalidated", "budget", "tool", "expired"}
ASSET_TYPES = {"broad_equity", "dividend_value", "growth_theme", "sector", "cyclical", "bond",
               "gold_commodity", "cross_border_equity"}
METHODS = {"return_decomposition", "reverse_valuation", "mid_cycle", "ytm_duration", "scenario_only"}
MULTIPLE_METHODS = {"return_decomposition", "reverse_valuation", "mid_cycle"}
VALUATION_METRICS = {"erp_spread", "pe_ttm", "pb"}
INSTRUMENT_TYPES = {"otc_fund", "exchange_etf"}
ROLES = {"primary", "backup", "held_other", "rejected"}
INSTRUMENT_ACTIONS = {"buy", "hold", "stop_dca", "switch_out", "none"}
DCA_ACTIONS = {"continue", "pause"}
REDUCE_MODES = {"to_target_ratio", "exit_all"}
TRIGGER_KINDS = {"auto", "manual"}
AUTO_METRICS = {"index_level", "index_vs_sma200_pct", "index_vs_sma10m_pct", "index_drawdown_from_ref_pct",
                "instrument_premium_pct", "bet_group_value_cny", "bet_group_weight_pct"}
OPERATORS = {"<", "<=", ">", ">="}
FREQUENCIES = {"daily", "weekly", "monthly", "quarterly", "event"}
MONITOR_ACTIONS = {"alert", "review", "pause_dca", "reduce", "close", "swap_tool"}
EXIT_ACTIONS = {"close", "reduce", "swap_tool"}
SCENARIOS = ("bear", "base", "bull")
SCENARIO_INPUTS = ("eps_growth_pct", "dividend_yield_pct", "current_multiple", "terminal_multiple", "years", "drag_pct")
ASSUMPTION_INPUTS = {"eps_growth_pct", "dividend_yield_pct", "years", "drag_pct"}

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SNAPSHOT_REF = re.compile(r"research/etf-\d{4}-\d{2}-\d{2}-data-snapshot\.txt")
SOURCE = re.compile(r"snapshot§[0-8]|calc:([a-z_]+)|framework:A\d{1,2}|user:\d{4}-\d{2}-\d{2}|ai_estimate")
NUMBER_TOKEN = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")
CALCULATORS = {name for name, member in vars(etf_calc).items() if not name.startswith("_")
               and inspect.isfunction(member) and member.__module__ == etf_calc.__name__}


class _Card:
    """Error list plus the sourced numbers seen, so snapshot citations can be checked afterwards."""

    def __init__(self):
        self.errors = []
        self.sourced = []

    def error(self, path, message):
        self.errors.append(f"{path}: {message}")

    def errors_at(self, path):
        return any(error.startswith(path) for error in self.errors)

    def obj(self, value, path, keys):
        if not isinstance(value, dict):
            self.error(path, "expected object")
            return None
        for key in keys:
            if key not in value:
                self.error(f"{path}.{key}", "missing field")
        for key in value:
            if key not in keys:
                self.error(f"{path}.{key}", "unknown field")
        return value if all(key in value for key in keys) else None

    def text(self, value, path, *, nullable=False, allow_empty=False):
        if value is None and nullable:
            return None
        if not isinstance(value, str) or not (allow_empty or value.strip()):
            self.error(path, "expected nonempty string" + (" or null" if nullable else ""))
            return None
        return value

    def enum(self, value, path, allowed, *, nullable=False):
        if value is None and nullable:
            return None
        if not isinstance(value, str) or value not in allowed:
            self.error(path, "expected one of " + ", ".join(sorted(allowed)) + (" or null" if nullable else ""))
            return None
        return value

    def boolean(self, value, path):
        if not isinstance(value, bool):
            self.error(path, "expected true or false")

    def day(self, value, path, *, nullable=False):
        if value is None and nullable:
            return None
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            self.error(path, "expected ISO date YYYY-MM-DD" + (" or null" if nullable else ""))
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            self.error(path, "invalid calendar date")
            return None

    def integer(self, value, path, *, minimum=0, nullable=False):
        if value is None and nullable:
            return None
        if type(value) is not int or value < minimum:
            self.error(path, f"expected integer >= {minimum}" + (" or null" if nullable else ""))
            return None
        return value

    def texts(self, value, path, *, exactly=None):
        if not isinstance(value, list):
            self.error(path, "expected array")
            return
        for index, item in enumerate(value):
            self.text(item, f"{path}[{index}]")
        if exactly is not None and len(value) != exactly:
            self.error(path, f"expected exactly {exactly} items")

    def number(self, value, path, *, assumption=False, required=False, minimum=None, maximum=None):
        """Sourced number {"value", "source"[, "note"]}; returns the value or None when unknown."""
        if not isinstance(value, dict) or "value" not in value or "source" not in value:
            self.error(path, 'expected sourced number {"value", "source"}')
            return None
        for key in value:
            if key not in ("value", "source", "note"):
                self.error(f"{path}.{key}", "unknown field")
        if "note" in value:
            self.text(value["note"], f"{path}.note", nullable=True)
        amount, source = value["value"], value["source"]
        if amount is None:
            if source is not None:
                self.error(f"{path}.source", "must be null while value is null")
            if required:
                self.error(f"{path}.value", "required here, null is not accepted")
            return None
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount):
            self.error(f"{path}.value", "expected finite number or null")
            return None
        match = SOURCE.fullmatch(source) if isinstance(source, str) else None
        if match is None:
            self.error(f"{path}.source", "expected snapshot§0-8, calc:<etf_calc function>, framework:A<n>, "
                                         "user:<ISO date> or ai_estimate")
        elif source == "ai_estimate" and not assumption:
            self.error(f"{path}.source", "ai_estimate is accepted only on scenario assumptions")
        elif match.group(1) is not None and match.group(1) not in CALCULATORS:
            self.error(f"{path}.source", f"etf_calc has no function {match.group(1)}")
        else:
            self.sourced.append((path, amount, source))
        if minimum is not None and amount < minimum or maximum is not None and amount > maximum:
            self.error(f"{path}.value", f"outside [{minimum}, {maximum}]")
        return amount


def _exposure(card, exposure):
    path = "exposure"
    exposure = card.obj(exposure, path, ("index_code", "index_name", "asset_type", "currency", "counts_toward_sector_cap",
                                         "china_equity", "view_mismatch_note", "structure"))
    if exposure is None:
        return None
    card.text(exposure["index_code"], f"{path}.index_code")
    card.text(exposure["index_name"], f"{path}.index_name")
    card.enum(exposure["asset_type"], f"{path}.asset_type", ASSET_TYPES)
    if not isinstance(exposure["currency"], str) or not re.fullmatch(r"[A-Z]{3}", exposure["currency"]):
        card.error(f"{path}.currency", "expected ISO 4217 code such as CNY")
    card.boolean(exposure["counts_toward_sector_cap"], f"{path}.counts_toward_sector_cap")
    card.boolean(exposure["china_equity"], f"{path}.china_equity")
    card.text(exposure["view_mismatch_note"], f"{path}.view_mismatch_note", allow_empty=True)
    path = "exposure.structure"
    structure = card.obj(exposure["structure"], path, ("weights_as_of", "constituent_count", "max_constituent_weight_pct",
                                                       "top10_weight_pct", "research_coverage_pct", "top_constituents"))
    if structure is not None:
        card.day(structure["weights_as_of"], f"{path}.weights_as_of", nullable=True)
        card.number(structure["constituent_count"], f"{path}.constituent_count", minimum=1)
        for key in ("max_constituent_weight_pct", "top10_weight_pct", "research_coverage_pct"):
            card.number(structure[key], f"{path}.{key}", minimum=0, maximum=100)
        rows = structure["top_constituents"]
        if not isinstance(rows, list):
            card.error(f"{path}.top_constituents", "expected array")
            rows = []
        for index, row in enumerate(rows):
            row_path = f"{path}.top_constituents[{index}]"
            row = card.obj(row, row_path, ("code", "name", "weight_pct"))
            if row is not None:
                card.text(row["code"], f"{row_path}.code")
                card.text(row["name"], f"{row_path}.name")
                card.number(row["weight_pct"], f"{row_path}.weight_pct", required=True, minimum=0, maximum=100)
    return exposure


def _expectation(card, expectation):
    path = "expectation"
    expectation = card.obj(expectation, path, ("method", "scenarios", "valuation_state"))
    if expectation is None:
        return
    method = card.enum(expectation["method"], f"{path}.method", METHODS)
    scenarios = card.obj(expectation["scenarios"], f"{path}.scenarios", SCENARIOS)
    returns = {}
    for name in SCENARIOS if scenarios is not None else ():
        scenario_path = f"{path}.scenarios.{name}"
        scenario = card.obj(scenarios[name], scenario_path, ("inputs", "valuation_change_pct", "annual_return_pct"))
        if scenario is None:
            continue
        change = card.number(scenario["valuation_change_pct"], f"{scenario_path}.valuation_change_pct")
        returns[name] = card.number(scenario["annual_return_pct"], f"{scenario_path}.annual_return_pct",
                                    assumption=method == "scenario_only")
        if name == "base" and (change != 0 if method in MULTIPLE_METHODS else change not in (None, 0)):
            card.error(f"{scenario_path}.valuation_change_pct.value", "base scenario must assume zero valuation change")
        if scenario["inputs"] is None:
            continue
        inputs = card.obj(scenario["inputs"], f"{scenario_path}.inputs", SCENARIO_INPUTS)
        if inputs is None:
            continue
        values = {key: card.number(inputs[key], f"{scenario_path}.inputs.{key}", assumption=key in ASSUMPTION_INPUTS)
                  for key in SCENARIO_INPUTS}
        if None in values.values():
            continue
        expected = etf_calc.scenario_annual_return(**values)
        for key, actual in (("valuation_change_pct", change), ("annual_return_pct", returns[name])):
            if expected["status"] != "complete" or actual is None or abs(actual - expected[key]) > 0.01:
                card.error(f"{scenario_path}.{key}.value",
                           f"does not match calc:scenario_annual_return of the inputs ({expected[key]})")
    if all(returns.get(name) is not None for name in SCENARIOS) and not (
            returns["bear"] <= returns["base"] <= returns["bull"]):
        card.error(f"{path}.scenarios", "expected bear <= base <= bull annual_return_pct")
    path = "expectation.valuation_state"
    state = card.obj(expectation["valuation_state"], path, ("index_code", "metric", "value", "percentile_expanding",
                                                            "percentile_10y", "sample_n", "as_of"))
    if state is not None:
        quoted = card.text(state["index_code"], f"{path}.index_code", nullable=True)
        metric = card.enum(state["metric"], f"{path}.metric", VALUATION_METRICS, nullable=True)
        value = card.number(state["value"], f"{path}.value")
        for key in ("percentile_expanding", "percentile_10y"):
            card.number(state[key], f"{path}.{key}", minimum=0, maximum=100)
        card.number(state["sample_n"], f"{path}.sample_n", minimum=1)
        as_of = card.day(state["as_of"], f"{path}.as_of", nullable=True)
        if len({quoted is None, metric is None, value is None, as_of is None}) != 1:
            card.error(path, "index_code, metric, value and as_of are all present or all null")


def _instruments(card, instruments, status):
    path = "instruments"
    instruments = card.obj(instruments, path, ("list", "merge_note"))
    if instruments is None:
        return None
    card.text(instruments["merge_note"], f"{path}.merge_note", allow_empty=True)
    rows = instruments["list"]
    if not isinstance(rows, list):
        card.error(f"{path}.list", "expected array")
        return None
    primary, codes = None, set()
    for index, row in enumerate(rows):
        row_path = f"{path}.list[{index}]"
        row = card.obj(row, row_path, ("code", "name", "instrument_type", "share_class", "platform_account",
                                       "role", "action", "reason"))
        if row is None:
            continue
        code = card.text(row["code"], f"{row_path}.code")
        if code in codes:
            card.error(f"{row_path}.code", f"duplicate instrument {code}")
        codes.add(code)
        card.text(row["name"], f"{row_path}.name")
        card.enum(row["instrument_type"], f"{row_path}.instrument_type", INSTRUMENT_TYPES)
        card.text(row["share_class"], f"{row_path}.share_class", nullable=True)
        card.text(row["platform_account"], f"{row_path}.platform_account")
        role = card.enum(row["role"], f"{row_path}.role", ROLES)
        action = card.enum(row["action"], f"{row_path}.action", INSTRUMENT_ACTIONS)
        card.text(row["reason"], f"{row_path}.reason")
        if role == "primary":
            if primary is not None:
                card.error(f"{row_path}.role", "only one primary instrument")
            primary = row
        if role == "rejected" and action != "none":
            card.error(f"{row_path}.action", "a rejected instrument takes action none")
        if action == "buy" and status != "active":
            card.error(f"{row_path}.action", "buy requires card status active")
    if primary is None and status in ("active", "watch"):
        card.error(f"{path}.list", "an active or watch card names exactly one primary instrument")
    return primary


def _trigger(card, trigger, path, actions):
    trigger = card.obj(trigger, path, ("name", "kind", "metric", "operator", "threshold", "condition_text",
                                       "data_source", "current_text", "frequency", "action", "action_note"))
    if trigger is None:
        return
    card.text(trigger["name"], f"{path}.name")
    kind = card.enum(trigger["kind"], f"{path}.kind", TRIGGER_KINDS)
    metric = card.enum(trigger["metric"], f"{path}.metric", AUTO_METRICS, nullable=True)
    operator = card.enum(trigger["operator"], f"{path}.operator", OPERATORS, nullable=True)
    threshold = card.number(trigger["threshold"], f"{path}.threshold")
    card.text(trigger["condition_text"], f"{path}.condition_text")
    card.text(trigger["data_source"], f"{path}.data_source")
    card.text(trigger["current_text"], f"{path}.current_text", nullable=True)
    card.enum(trigger["frequency"], f"{path}.frequency", FREQUENCIES)
    card.enum(trigger["action"], f"{path}.action", actions)
    card.text(trigger["action_note"], f"{path}.action_note", allow_empty=True)
    if kind == "auto" and None in (metric, operator, threshold):
        card.error(path, "an auto trigger needs metric, operator and threshold.value")
    if kind == "manual" and (metric, operator, threshold) != (None, None, None):
        card.error(path, "a manual trigger keeps metric, operator and threshold.value null; say it in condition_text")


def _triggers(card, rows, path, actions):
    if not isinstance(rows, list):
        card.error(path, "expected array")
        return 0
    for index, row in enumerate(rows):
        _trigger(card, row, f"{path}[{index}]", actions)
    return len(rows)


def _anchor(card, anchor, path):
    """One price anchor: index level from a named calculator, plus the position it calls for."""
    anchor = card.obj(anchor, path, ("level", "target_ratio_pct", "inputs", "rationale"))
    if anchor is None:
        return None, None
    level = card.number(anchor["level"], f"{path}.level", minimum=1e-9)
    ratio = card.number(anchor["target_ratio_pct"], f"{path}.target_ratio_pct", minimum=0, maximum=100)
    card.text(anchor["rationale"], f"{path}.rationale", nullable=level is None)
    if (level is None) != (ratio is None):
        card.error(path, "level and target_ratio_pct are both present or both null")
    source = anchor["level"]["source"] if level is not None else None
    function = SOURCE.fullmatch(source).group(1) if isinstance(source, str) and SOURCE.fullmatch(source) else None
    if level is not None and function is None:
        card.error(f"{path}.level.source", "an anchor level names the calculator that derived it (calc:<function>)")
    if anchor["inputs"] is None:
        return level, ratio
    if not isinstance(anchor["inputs"], dict):
        card.error(f"{path}.inputs", "expected object of sourced numbers or null")
        return level, ratio
    values = {key: card.number(value, f"{path}.inputs.{key}") for key, value in anchor["inputs"].items()}
    if function in CALCULATORS and None not in values.values():
        try:
            expected = getattr(etf_calc, function)(**values)
        except (TypeError, ValueError) as exc:
            card.error(f"{path}.inputs", f"etf_calc.{function} rejects these inputs: {exc}")
        else:
            if not isinstance(expected, float):
                card.error(f"{path}.inputs", f"etf_calc.{function} does not yield a level from these inputs ({expected!r})")
            elif abs(level - expected) > max(0.01, 1e-4 * expected):
                card.error(f"{path}.level.value", f"does not match {source} of the inputs ({expected})")
    return level, ratio


def _decision(card, decision, exposure):
    path = "decision"
    decision = card.obj(decision, path, ("rule_refs", "anchors", "dca_action"))
    if decision is None:
        return
    card.texts(decision["rule_refs"], f"{path}.rule_refs")
    card.enum(decision["dca_action"], f"{path}.dca_action", DCA_ACTIONS)
    path = "decision.anchors"
    anchors = card.obj(decision["anchors"], path, ("basis", "index_code", "add_below", "buy_below", "reduce_above",
                                                   "reduce_mode", "no_anchor_reason", "valid_until"))
    if anchors is None:
        return
    if anchors["basis"] != "index_level":
        card.error(f"{path}.basis", "conditions hang on index_level, never on fund NAV or ETF price")
    if exposure is not None and anchors["index_code"] != exposure["index_code"]:
        card.error(f"{path}.index_code", "must equal exposure.index_code")
    (add, add_ratio), (buy, buy_ratio), (reduce, reduce_ratio) = (
        _anchor(card, anchors[key], f"{path}.{key}") for key in ("add_below", "buy_below", "reduce_above"))
    mode = card.enum(anchors["reduce_mode"], f"{path}.reduce_mode", REDUCE_MODES)
    reason = card.text(anchors["no_anchor_reason"], f"{path}.no_anchor_reason", nullable=True)
    present = [level is not None for level in (add, buy, reduce)]
    card.day(anchors["valid_until"], f"{path}.valid_until", nullable=not any(present))
    if any(present) != all(present):
        card.error(path, "the three anchors are all present or all null: a partial ladder cannot be read statelessly")
    if any(present) == (reason is not None):
        card.error(f"{path}.no_anchor_reason", "present exactly when the card carries no anchors")
    if all(present) and not card.errors_at(path):
        if not add < buy < reduce:
            card.error(path, "expected add_below.level < buy_below.level < reduce_above.level, strictly")
        if not add_ratio >= buy_ratio > reduce_ratio:
            card.error(path, "expected add_below ratio >= buy_below ratio > reduce_above ratio")
        if (mode == "exit_all") != (reduce_ratio == 0):
            card.error(f"{path}.reduce_mode", "exit_all goes with a reduce_above target_ratio_pct of 0, and only then")


def _sizing(card, sizing):
    path = "sizing"
    sizing = card.obj(sizing, path, ("bet_group", "stress_drawdown_pct", "loss_budget_cny", "standalone_cap_cny"))
    if sizing is None:
        return
    if not isinstance(sizing["bet_group"], str) or not SLUG.fullmatch(sizing["bet_group"]):
        card.error(f"{path}.bet_group", "expected lowercase slug shared by every card of the same bet")
    drawdown = card.number(sizing["stress_drawdown_pct"], f"{path}.stress_drawdown_pct", minimum=-100, maximum=-1e-9)
    budget = card.number(sizing["loss_budget_cny"], f"{path}.loss_budget_cny", minimum=0)
    cap = card.number(sizing["standalone_cap_cny"], f"{path}.standalone_cap_cny", minimum=0)
    if cap is not None and not card.errors_at(path):
        expected = etf_calc.loss_budget_cap(budget, drawdown)
        if expected is None or abs(cap - expected) > 1:
            card.error(f"{path}.standalone_cap_cny.value", f"does not match calc:loss_budget_cap ({expected})")


def _bare_numbers(card, value, path):
    """Any number outside a sourced-number object or a declared structural integer is an unsourced claim."""
    if isinstance(value, dict):
        if set(value) >= {"value", "source"}:
            return
        for key, item in value.items():
            _bare_numbers(card, item, f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _bare_numbers(card, item, f"{path}[{index}]")
    elif isinstance(value, (int, float)) and not isinstance(value, bool) and path not in (
            "card_schema_version", "thesis.horizon_months", "trade_rules.min_holding_days", "scorecard.confidence_pct"):
        card.error(path, 'bare number; wrap it as {"value", "source"}')


def _snapshot_citations(card, snapshot_text):
    """A number citing snapshot§N must equal a number printed in that section: copied, never rounded further."""
    sections = {}
    for block in re.split(r"(?m)^(?=---- §\d)", snapshot_text):
        match = re.match(r"---- §(\d)", block)
        if match:
            sections[match.group(1)] = {float(token.replace(",", "")) for token in NUMBER_TOKEN.findall(block)}
    for path, amount, source in card.sourced:
        if not source.startswith("snapshot§"):
            continue
        printed = sections.get(source[-1])
        if printed is None:
            card.error(f"{path}.source", f"{source} is not a section of the referenced snapshot")
        elif not any(math.isclose(amount, number, rel_tol=0, abs_tol=1e-9) for number in printed):
            card.error(f"{path}.value", f"{amount} is not printed in {source} of the referenced snapshot")


def validate_card(document, *, snapshot_text=None, filename=None):
    """Return a list of error strings; empty means the card is structurally valid."""
    card = _Card()
    keys = ("card_schema_version", "card_id", "as_of_date", "supersedes", "framework", "snapshot_ref", "task", "status",
            "no_buy_reason", "close_reason", "exposure", "thesis", "expectation", "instruments", "trade_rules",
            "decision", "sizing", "monitor_variables", "exit", "scorecard")
    if card.obj(document, "card", keys) is None:
        return card.errors
    if document["card_schema_version"] != SCHEMA_VERSION or type(document["card_schema_version"]) is not int:
        card.error("card_schema_version", f"expected {SCHEMA_VERSION}")
    card_id = document["card_id"]
    if not isinstance(card_id, str) or not SLUG.fullmatch(card_id):
        card.error("card_id", "expected lowercase slug such as cn-hk-pharma-tactical")
    as_of = card.day(document["as_of_date"], "as_of_date")
    if filename is not None and filename != f"{card_id}-{document['as_of_date']}.md":
        card.error("card_id", f"file must be named <card_id>-<as_of_date>.md, got {filename}")
    card.text(document["supersedes"], "supersedes", nullable=True)
    framework = card.obj(document["framework"], "framework", ("path", "version"))
    if framework is not None:
        if framework["path"] != "framework/etf_framework.md":
            card.error("framework.path", "expected framework/etf_framework.md")
        if not isinstance(framework["version"], str) or not re.fullmatch(r"v\d+\.\d+", framework["version"]):
            card.error("framework.version", "expected vMAJOR.MINOR")
    if not isinstance(document["snapshot_ref"], str) or not SNAPSHOT_REF.fullmatch(document["snapshot_ref"]):
        card.error("snapshot_ref", "expected research/etf-YYYY-MM-DD-data-snapshot.txt")

    task = card.enum(document["task"], "task", TASKS)
    status = card.enum(document["status"], "status", STATUSES)
    no_buy = card.enum(document["no_buy_reason"], "no_buy_reason", NO_BUY_REASONS, nullable=True)
    closed = card.enum(document["close_reason"], "close_reason", CLOSE_REASONS, nullable=True)
    if (status == "no_buy") != (no_buy is not None):
        card.error("no_buy_reason", "present exactly when status is no_buy")
    if (status == "closed") != (closed is not None):
        card.error("close_reason", "present exactly when status is closed")
    live = status in ("active", "watch")

    exposure = _exposure(card, document["exposure"])
    thesis = card.obj(document["thesis"], "thesis", ("statement", "evidence", "counter_evidence", "horizon_months"))
    if thesis is not None:
        card.text(thesis["statement"], "thesis.statement")
        card.texts(thesis["evidence"], "thesis.evidence", exactly=3)
        card.texts(thesis["counter_evidence"], "thesis.counter_evidence", exactly=2)
        card.integer(thesis["horizon_months"], "thesis.horizon_months", minimum=1 if task == "tactical" else 0)
    _expectation(card, document["expectation"])
    primary = _instruments(card, document["instruments"], status)

    rules = card.obj(document["trade_rules"], "trade_rules", ("min_holding_days", "purchase_limit_note",
                                                              "max_premium_pct", "sell_if_premium_above_pct"))
    if rules is not None:
        card.integer(rules["min_holding_days"], "trade_rules.min_holding_days", nullable=True)
        card.text(rules["purchase_limit_note"], "trade_rules.purchase_limit_note", nullable=True)
        premiums = [card.number(rules[key], f"trade_rules.{key}", minimum=0)
                    for key in ("max_premium_pct", "sell_if_premium_above_pct")]
        if primary is not None and primary["instrument_type"] == "otc_fund" and premiums != [None, None]:
            card.error("trade_rules", "an OTC fund trades at NAV: premium fields must be null")

    _decision(card, document["decision"], exposure)
    _sizing(card, document["sizing"])
    monitors = _triggers(card, document["monitor_variables"], "monitor_variables", MONITOR_ACTIONS)
    if live and not 3 <= monitors <= 5:
        card.error("monitor_variables", "an active or watch card carries 3 to 5 monitor variables")

    exits = card.obj(document["exit"], "exit", ("invalidation", "latest_review_date"))
    if exits is not None:
        invalidations = _triggers(card, exits["invalidation"], "exit.invalidation", EXIT_ACTIONS)
        if task == "tactical" and live and invalidations == 0:
            card.error("exit.invalidation", "a live tactical card preregisters at least one invalidation")
        review = card.day(exits["latest_review_date"], "exit.latest_review_date", nullable=status == "closed")
        if review is not None and as_of is not None and review <= as_of and status != "closed":
            card.error("exit.latest_review_date", "must be later than as_of_date")

    score = card.obj(document["scorecard"], "scorecard", ("benchmark", "preregistered_at", "confidence_pct",
                                                          "entry_ref_index_level"))
    if score is not None:
        card.text(score["benchmark"], "scorecard.benchmark")
        registered = card.day(score["preregistered_at"], "scorecard.preregistered_at")
        if registered is not None and as_of is not None and registered > as_of:
            card.error("scorecard.preregistered_at", "later than as_of_date")
        confidence = score["confidence_pct"]
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 100:
            card.error("scorecard.confidence_pct", "expected number in [0, 100]")
        card.number(score["entry_ref_index_level"], "scorecard.entry_ref_index_level", minimum=0)

    _bare_numbers(card, document, "")
    if snapshot_text is not None:
        _snapshot_citations(card, snapshot_text)
    return card.errors


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"non-finite JSON number: {value}")


def load_card(markdown):
    """Parse the single fenced json block of a card."""
    blocks = re.findall(r"(?ms)^```json[ \t]*\n(.*?)^```[ \t]*$", markdown)
    if len(blocks) != 1:
        raise ValueError(f"a card must contain exactly one fenced json block, found {len(blocks)}")
    return json.loads(blocks[0], object_pairs_hook=_unique_object, parse_constant=_reject_constant)


def validate_file(path):
    path = Path(path)
    try:
        document = load_card(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"{path}: {exc}"]
    snapshot_text, errors = None, []
    reference = document.get("snapshot_ref") if isinstance(document, dict) else None
    if isinstance(reference, str) and SNAPSHOT_REF.fullmatch(reference):
        try:
            snapshot_text = (REPO_ROOT / reference).read_text(encoding="utf-8")
        except OSError:
            errors.append(f"snapshot_ref: {reference} not found under {REPO_ROOT}")
        else:
            if "快照完成" not in snapshot_text:
                errors.append(f"snapshot_ref: {reference} is incomplete (no 快照完成 line)")
    return errors + validate_card(document, snapshot_text=snapshot_text, filename=path.name)


def bet_group_conflicts(paths):
    """One bet, one card: a bet_group carries one cap and one ladder, so two card_ids may not share it."""
    owners = {}
    for path in paths:
        try:
            document = load_card(Path(path).read_text(encoding="utf-8"))
            owners.setdefault(document["sizing"]["bet_group"], set()).add(document["card_id"])
        except (OSError, ValueError, KeyError, TypeError):
            continue  # already reported by validate_file
    return [f"sizing.bet_group: {group} is shared by cards {', '.join(sorted(ids))}; merge them into one card"
            for group, ids in sorted(owners.items()) if len(ids) > 1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=f"Validate ETF decision cards (schema {SCHEMA_VERSION})")
    parser.add_argument("cards", nargs="+", metavar="CARD.md")
    cards = parser.parse_args(argv).cards
    failed = False
    for card in cards:
        errors = validate_file(card)
        failed = failed or bool(errors)
        print(f"{card}: " + ("valid" if not errors else f"{len(errors)} error(s)"))
        for error in errors:
            print(f"  - {error}")
    for conflict in bet_group_conflicts(cards):
        failed = True
        print(f"  - {conflict}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
