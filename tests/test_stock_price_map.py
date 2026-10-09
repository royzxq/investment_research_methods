"""Offline price-map regressions using explicit, non-investment assumptions."""

from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.stock_price_map as price_map_module
from scripts.stock_price_map import build_document, load_json, quote_value, validate_document


def yutong_example():
    """The old report's arithmetic example, not adopted investment parameters."""
    return {
        "meta": {
            "code": "600066.SH", "name": "宇通客车", "valuation_date": "2026-10-05",
            "currency": "CNY", "report_path": "research/example.md",
        },
        "mode": "tracking", "reason": "公募持仓分位缺失，仅跟踪",
        "valuation": {
            "kind": "equity_value", "values": {"low": 486, "base": 630, "high": 792},
            "currency": "CNY", "unit": "100_million", "fx_to_quote": 1,
            "shares": 2_214_000_000,
        },
        "discounts": {"d_base": 0.10, "r_chip": 0.03, "r_v5": 0.05,
                      "r_gov": 0, "r_terminal": 0.05},
        "step_down": 0.075,
        "p2": {"status": "active", "reason": None},
        "t1": {"price_condition": "价格达到观察区间时复核", "events": ["出口毛利率下降"]},
        "t2": {"price_condition": "不设机械卖出价", "events": ["盈利假设被证伪"]},
        "monitoring": [{
            "variable": "PB三年分位", "current": 45.9, "as_of": "2026-09-30",
            "trigger": "达到80%时复核", "action": "复核拥挤度", "source": "离线样例数据包",
            "next_check": "下次复评",
        }],
    }


class StockPriceMapTests(unittest.TestCase):
    def test_t1_t2_v50_reference_checks_only_the_referenced_amount(self):
        for field in ('t1', 't2'):
            with self.subTest(field=field):
                data = yutong_example()
                data['valuation'] = dict(kind='per_share', values=dict(low=20, base=30, high=40),
                                         currency='CNY', unit='per_share', fx_to_quote=1)
                data[field]['price_condition'] = '接近 V50 上沿 40 元；当前价格 25 元'
                document = build_document(data)
                document['price_map'][field]['price_condition'] = '接近V50上沿41元；现价25元'
                # Historical sealed results retain structure-only loading;
                # an independent buy refusal must survive a T1 semantic error.
                validate_document(document)
                with self.assertRaisesRegex(ValueError, field + '.*V50.high'):
                    price_map_module.validate_price_references(document)
                data[field]['price_condition'] = '接近V50上沿41元；现价25元'
                with self.assertRaisesRegex(ValueError, field + '.*V50.high'):
                    build_document(data)

    def test_symbolic_v50_and_independent_threshold_remain_valid(self):
        data = yutong_example()
        data['t1']['price_condition'] = '接近V50上沿时复核；当前25元'
        data['t2']['price_condition'] = '股价达到50元时复核'
        build_document(data)
        data['t2']['price_condition'] = '高于V50上沿20%即42.93元/股，研究假设'
        build_document(data)

    def test_yutong_p2_uses_lower_bound_and_tracking_needs_no_account_cap(self):
        result = build_document(yutong_example())
        prices = result["price_map"]
        self.assertEqual(prices["mode"], "tracking")
        self.assertEqual(prices["p1"], {"low": 17.29, "base": 22.42, "high": 28.18})
        # Independently checked: 15.997858... rounds to 16.00. The old 20.7 used base.
        self.assertEqual(prices["p2"]["price"], 16.00)
        self.assertEqual(set(result), {"meta", "price_map", "monitoring"})
        self.assertNotIn("cap", prices)
        prices["p2"]["price"] = 20.7
        with self.assertRaisesRegex(ValueError, "P1_low"):
            validate_document(result)

    def test_hk_profit_valuation_and_reverse_currency_direction(self):
        data = yutong_example()
        data["meta"].update(code="01952.HK", name="云顶新耀", currency="HKD")
        data["valuation"] = {
            "kind": "equity_value",
            # RMB earnings 3.2/4.34/5.5 hundred million at 18/22/28 times.
            "values": {"low": 57.6, "base": 95.48, "high": 154},
            "currency": "CNY", "unit": "100_million", "shares": 354_467_063,
            "fx_to_quote": Decimal(200) / Decimal(173),
            "fx_source": "离线假设：每港元0.865人民币，即每人民币200/173港元",
        }
        v50 = build_document(data)["price_map"]["v50"]
        self.assertEqual(v50, {"low": 18.786, "base": 31.14, "high": 50.226})
        self.assertEqual([round(v50[key]) for key in ("low", "base", "high")], [19, 31, 50])
        # 16.24 hundred-million HKD -> 14.0476 in the same CNY unit, not 18.8.
        self.assertEqual(quote_value(Decimal("16.24"), Decimal("0.865")), Decimal("14.04760"))

    def test_per_share_input_and_total_equity_units_are_not_interchangeable(self):
        per_share = {
            "kind": "per_share", "values": {"low": 20, "base": 30, "high": 40},
            "currency": "CNY", "unit": "per_share", "fx_to_quote": 1,
        }
        data = yutong_example()
        data["valuation"] = per_share
        self.assertEqual(build_document(data)["price_map"]["v50"],
                         {"low": 20, "base": 30, "high": 40})
        invalid = [
            dict(per_share, unit="100_million"),
            dict(per_share, shares=100_000_000),
            dict(yutong_example()["valuation"], unit="per_share"),
            dict(yutong_example()["valuation"], shares=Decimal("22.14")),
            dict(per_share, fx_to_quote=0.865),
        ]
        for valuation in invalid:
            with self.subTest(valuation=valuation):
                data["valuation"] = valuation
                with self.assertRaises(ValueError):
                    build_document(data)

    def test_missing_discounts_are_not_silently_assumed(self):
        for discounts in (None, {"d_base": 0.1}):
            with self.subTest(discounts=discounts):
                data = yutong_example()
                data["discounts"] = discounts
                with self.assertRaises(ValueError):
                    build_document(data)

    def test_round_once_after_p2_calculation_and_reject_excess_precision(self):
        data = yutong_example()
        data["valuation"] = {
            "kind": "per_share", "values": {"low": Decimal("10.005"), "base": 20, "high": 30},
            "currency": "CNY", "unit": "per_share", "fx_to_quote": 1,
        }
        data["discounts"] = dict.fromkeys(data["discounts"], 0)
        data["step_down"] = 0.05
        result = build_document(data)
        self.assertEqual(result["price_map"]["p1"]["low"], 10.01)
        self.assertEqual(result["price_map"]["p2"]["price"], 9.50)
        result["price_map"]["p1"]["low"] = Decimal("10.001")
        with self.assertRaisesRegex(ValueError, "precision"):
            validate_document(result)

    def test_step_boundaries_and_suspended_p2(self):
        for step in (0.049, 0.101):
            with self.subTest(step=step):
                data = yutong_example()
                data["step_down"] = step
                with self.assertRaises(ValueError):
                    build_document(data)
        data = yutong_example()
        data["p2"] = {"status": "suspended", "reason": "在册事件窗口，完成复评后才恢复"}
        result = build_document(data)
        self.assertEqual(result["price_map"]["p2"]["status"], "suspended")
        self.assertEqual(result["price_map"]["p2"]["price"], 16)

    def test_invalid_numeric_values_and_listing_currency_are_rejected(self):
        for value in (True, float("nan"), float("inf"), -0.01, 1, "0.1"):
            with self.subTest(discount=value):
                data = yutong_example()
                data["discounts"]["r_chip"] = value
                with self.assertRaises(ValueError):
                    build_document(data)
        for code, currency in (("600066.SH", "HKD"), ("01952.HK", "CNY")):
            with self.subTest(code=code, currency=currency):
                data = yutong_example()
                data["meta"].update(code=code, currency=currency)
                with self.assertRaisesRegex(ValueError, "listing market"):
                    build_document(data)

    def test_cancelled_p2_has_reason_but_no_price_or_allocation(self):
        data = yutong_example()
        data["p2"] = {"status": "cancelled", "reason": "现金流修复证据弱"}
        result = build_document(data)
        self.assertEqual(result["price_map"]["p2"],
                         {"status": "cancelled", "reason": "现金流修复证据弱", "price": None})
        self.assertNotIn("p2_share", result["price_map"])
        for mutation in ({"price": 16}, {"share": 0.4}, {"reason": None}):
            with self.subTest(mutation=mutation):
                bad = deepcopy(result)
                bad["price_map"]["p2"].update(mutation)
                with self.assertRaises(ValueError):
                    validate_document(bad)

    def test_frozen_and_unavailable_modes_cannot_publish_entry_prices(self):
        for mode in ("frozen", "unavailable"):
            with self.subTest(mode=mode):
                data = yutong_example()
                data.update(mode=mode, reason="关键条件未满足", discounts=None, step_down=None)
                data["p2"] = {"status": "unavailable", "reason": "等待复核"}
                if mode == "unavailable":
                    data["valuation"] = None
                result = build_document(data)
                self.assertIsNone(result["price_map"]["p1"])
                self.assertIsNone(result["price_map"]["p2"]["price"])
                result["price_map"]["p1"] = {"low": 10, "base": 15, "high": 20}
                with self.assertRaises(ValueError):
                    validate_document(result)

    def test_monitoring_preserves_baseline_and_rejects_forward_observations(self):
        data = yutong_example()
        self.assertEqual(build_document(data)["monitoring"][0]["current"], 45.9)
        for as_of in ("2026-10-06", None):
            with self.subTest(as_of=as_of):
                data["monitoring"][0]["as_of"] = as_of
                with self.assertRaises(ValueError):
                    build_document(data)
        data["monitoring"][0].update(current=None, as_of=None)
        self.assertIsNone(build_document(data)["monitoring"][0]["current"])

    def test_json_loader_rejects_duplicates_and_nonfinite_constants(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for payload in ('{"a":{"price":1,"price":2}}', '{"price":NaN}',
                            '{"price":Infinity}', '{"price":-Infinity}'):
                with self.subTest(payload=payload):
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_json(path)

    def test_cli_build_check_and_refusal_to_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            destination = Path(directory) / "investment-600066-2026-10-05-price-map-codex.json"
            data = yutong_example()
            data['meta']['report_path'] = "research/investment-600066-2026-10-05-research-codex.md"
            source.write_text(json.dumps(data), encoding="utf-8")
            command = [sys.executable, str(ROOT / "scripts/stock_price_map.py")]
            args = ["build", "--generator", "codex", "--input", str(source), "--output", str(destination)]
            built = subprocess.run(command + args, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            original = destination.read_bytes()
            self.assertEqual(set(json.loads(original)), {"meta", "price_map", "monitoring"})
            self.assertEqual(json.loads(original)['meta']['generator'], 'codex')
            checked = subprocess.run(command + ["check", str(destination)], capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            refused = subprocess.run(command + args, capture_output=True, text=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(destination.read_bytes(), original)

    def test_generator_metadata_is_optional_only_for_historical_compatibility(self):
        data = yutong_example()
        self.assertNotIn('generator', build_document(data)['meta'])
        for generator in ('codex', 'claude'):
            data['meta']['generator'] = generator
            self.assertEqual(build_document(data)['meta']['generator'], generator)
        for generator in ('unknown', '', None, ['codex']):
            data['meta']['generator'] = generator
            with self.assertRaisesRegex(ValueError, 'generator'):
                build_document(data)

    def test_cli_generator_conflicts_and_mismatched_filenames_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.json'
            command = [sys.executable, str(ROOT / 'scripts/stock_price_map.py'), 'build',
                       '--generator', 'codex', '--input', str(source)]
            for generator, output_name, report_name in [
                ('claude', 'price-map-codex.json', 'research-codex.md'),
                ('codex', 'price-map-claude.json', 'research-codex.md'),
                ('codex', 'price-map-codex.json', 'research-claude.md'),
                ('codex', 'price-map-codex-r2.json', 'research-codex.md'),
            ]:
                with self.subTest(generator=generator, output=output_name, report=report_name):
                    stem = 'investment-600066-2026-10-05-'
                    data = yutong_example()
                    data['meta'].update(generator=generator, report_path='research/' + stem + report_name)
                    source.write_text(json.dumps(data))
                    destination = Path(directory) / (stem + output_name)
                    result = subprocess.run(command + ['--output', str(destination)], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(destination.exists())

    def test_cli_claude_revision_and_required_generator(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.json'
            destination = Path(directory) / 'investment-600066-2026-10-05-price-map-claude-r12.json'
            data = yutong_example()
            data['meta']['report_path'] = 'research/investment-600066-2026-10-05-research-claude-r12.md'
            source.write_text(json.dumps(data))
            command = [sys.executable, str(ROOT / 'scripts/stock_price_map.py'), 'build',
                       '--input', str(source), '--output', str(destination)]
            missing = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(missing.returncode, 0)
            self.assertFalse(destination.exists())
            result = subprocess.run(command + ['--generator', 'claude'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(destination.read_text())['meta']['generator'], 'claude')


if __name__ == "__main__":
    unittest.main()
