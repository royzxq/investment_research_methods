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
    """Explicit offline report quotes, not adopted investment parameters."""
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
        "p1": {"base": 22.42},
        "p2": {"status": "active", "price": 16, "reason": None},
        "t1": {"price_condition": "股价≥30元/股", "events": ["出口毛利率下降"]},
        "t2": {"price_condition": "不设机械卖出价", "events": ["盈利假设被证伪"]},
        "monitoring": [{
            "variable": "PB三年分位", "current": 45.9, "as_of": "2026-09-30",
            "trigger": "达到80%时复核", "action": "复核拥挤度", "source": "离线样例数据包",
            "next_check": "下次复评",
        }],
    }


class StockPriceMapTests(unittest.TestCase):
    def test_new_t1_delivery_rejects_prose_but_historical_structure_still_loads(self):
        complex_text = ('接近V50上沿：≥30.85元/股（＝V50上沿34.28元×90%）。'
                        '注：现价22.80元（2026-10-12收盘）低于V50基准27.90元。')
        for condition in (complex_text, '接近V50上沿时复核；当前25元',
                          '股价≥30元/股；另一卖出价35', '盈利恶化时复核'):
            with self.subTest(condition=condition):
                data = yutong_example()
                data['valuation'] = dict(kind='per_share', values=dict(low=22.59, base=27.9, high=34.28),
                                         currency='CNY', unit='per_share', fx_to_quote=1)
                data['t1']['price_condition'] = condition
                with self.assertRaisesRegex(ValueError, 't1 delivery'):
                    build_document(data)
        document = build_document(yutong_example())
        document['price_map']['t1']['price_condition'] = complex_text
        validate_document(document)  # Loading old sealed bytes stays structural.

    def test_canonical_t1_delivery_values_and_currency(self):
        for currency, condition, expected in (
            ('CNY', '股价≥30.85元/股', Decimal('30.85')),
            ('CNY', ' 股价 ≥ 30.8500 CNY /股 ', Decimal('30.85')),
            ('HKD', '股价≥37.337港元/股', Decimal('37.337')),
            ('HKD', '股价≥37.337HKD/股', Decimal('37.337')),
            ('CNY', '接近V50上沿时复核', Decimal('40')),
            ('CNY', '接近V50下沿时复核', Decimal('20')),
            ('CNY', '接近V50基准时复核', Decimal('30')),
            ('CNY', '当前不适用', None),
            ('CNY', '本轮不提供T1报价', None),
        ):
            with self.subTest(condition=condition):
                data = yutong_example()
                data['meta']['currency'] = currency
                data['meta']['code'] = '01952.HK' if currency == 'HKD' else '600066.SH'
                data['valuation'] = dict(kind='per_share', values=dict(low=20, base=30, high=40),
                                         currency=currency, unit='per_share', fx_to_quote=1)
                data['t1']['price_condition'] = condition
                document = build_document(data)
                self.assertEqual(price_map_module.validate_t1_delivery(document), expected)

    def test_canonical_t1_delivery_rejects_invalid_or_ambiguous_values(self):
        bad = ['股价≥0元/股', '股价≥-30元/股', '股价≥30.851元/股',
               '股价≥30.85港元/股', '股价≥30.85HKD/股', '股价≥30元',
               '股价≥30至35元/股', '股价≥30元/股或35元/股',
               '股价≥30元/股；现价25元', '接近V50上沿40元时复核',
               '接近V50上沿×90%时复核', '当前不适用：现价25元',
               '本轮不提供T1报价；T1为30元', '股价≥NaN元/股',
               '股价≥Inf元/股', '股价≥1e2元/股',
               '股价≥' + '9'*400 + '元/股']
        for condition in bad:
            with self.subTest(condition=condition):
                data = yutong_example()
                data['valuation'] = dict(kind='per_share', values=dict(low=20, base=30, high=40),
                                         currency='CNY', unit='per_share', fx_to_quote=1)
                data['t1']['price_condition'] = condition
                with self.assertRaisesRegex(ValueError, 't1 delivery'):
                    build_document(data)

    def test_new_t1_delivery_requires_an_existing_symbolic_anchor(self):
        data = yutong_example()
        data.update(mode='unavailable', reason='missing financials', valuation=None,
                    p1=None, p2=dict(status='unavailable', price=None, reason='missing'))
        data['t1']['price_condition'] = '接近V50上沿时复核'
        with self.assertRaisesRegex(ValueError, 't1 delivery'):
            build_document(data)
        data['t1']['price_condition'] = '股价≥30元/股'
        build_document(data)  # An independent T1 does not require V50.

    def test_t1_t2_v50_reference_checks_only_the_referenced_amount(self):
        for field in ('t1', 't2'):
            with self.subTest(field=field):
                data = yutong_example()
                data['valuation'] = dict(kind='per_share', values=dict(low=20, base=30, high=40),
                                         currency='CNY', unit='per_share', fx_to_quote=1)
                document = build_document(data)
                document['price_map'][field]['price_condition'] = '接近 V50 上沿 40 元；当前价格 25 元'
                validate_document(document)
                price_map_module.validate_price_references(document)
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
        data['t1']['price_condition'] = '接近V50上沿时复核'
        data['t2']['price_condition'] = '股价达到50元时复核'
        build_document(data)
        data['t2']['price_condition'] = '高于V50上沿20%即42.93元/股，研究假设'
        build_document(data)

    def test_report_point_is_preserved_without_inventing_bounds_or_account_cap(self):
        result = build_document(yutong_example())
        prices = result["price_map"]
        self.assertEqual(prices["mode"], "tracking")
        self.assertEqual(prices["p1"], {"base": 22.42})
        self.assertEqual(prices["p2"]["price"], 16.00)
        self.assertEqual(set(result), {"meta", "price_map", "monitoring"})
        self.assertNotIn("cap", prices)

    def test_v50_changes_never_recalculate_explicit_p1_or_p2(self):
        data = yutong_example()
        for values in ({"low": 100, "base": 200, "high": 300},
                       {"low": 10, "base": 15, "high": 20}):
            data['valuation'] = dict(kind='per_share', values=values, currency='CNY',
                                     unit='per_share', fx_to_quote=1)
            result = build_document(data)
            self.assertEqual(result['price_map']['p1'], data['p1'])
            self.assertEqual(result['price_map']['p2'], data['p2'])

    def test_explicit_interval_keeps_only_reported_quotes_and_checks_p2_if_low_exists(self):
        data = yutong_example()
        for base in (22.42, None):
            data['p1'] = dict(base=base, low=17.29, high=28.18)
            result = build_document(data)
            self.assertEqual(result['price_map']['p1'], data['p1'])
            result['price_map']['p2']['price'] = 20.7
            with self.assertRaisesRegex(ValueError, 'P1_low'):
                validate_document(result)

    def test_interval_must_be_explicit_complete_positive_and_ordered(self):
        for quote in ({}, {'base': None}, {'base': 20, 'low': 18},
                      {'base': 20, 'low': None, 'high': None},
                      {'base': 20, 'low': 21, 'high': 25},
                      {'base': None, 'low': 25, 'high': 21},
                      {'base': True}, {'base': '22.42'}, {'base': 0},
                      {'base': float('nan')}, {'base': float('inf')}):
            with self.subTest(quote=quote):
                data = yutong_example()
                data['p1'] = quote
                with self.assertRaises(ValueError):
                    build_document(data)

    def test_legacy_v2_reader_preserves_old_ranges_and_arithmetic_validation(self):
        document = build_document(yutong_example())
        document['meta']['schema_version'] = 'stock-research/v2'
        document['price_map']['p1'] = dict(low=17.29, base=22.42, high=28.18)
        before = deepcopy(document)
        validate_document(document)
        self.assertEqual(document, before)
        document['price_map']['p2']['price'] = 20.7
        with self.assertRaisesRegex(ValueError, 'P1_low'):
            validate_document(document)
        document = deepcopy(before)
        document['price_map']['p1'] = {'base': 22.42}
        with self.assertRaises(ValueError):
            validate_document(document)
        data = yutong_example()
        data['meta']['schema_version'] = 'stock-research/v2'
        with self.assertRaisesRegex(ValueError, 'unsupported version'):
            build_document(data)

    def test_hk_profit_valuation_and_reverse_currency_direction(self):
        data = yutong_example()
        data["meta"].update(code="01952.HK", name="云顶新耀", currency="HKD")
        data["t1"]["price_condition"] = "股价≥30港元/股"
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

    def test_old_formula_inputs_are_rejected_instead_of_recalculating(self):
        for extra in ({'discounts': {'d_base': 0.1}}, {'step_down': 0.075}):
            with self.subTest(extra=extra):
                data = yutong_example()
                data.update(extra)
                with self.assertRaises(ValueError):
                    build_document(data)

    def test_missing_quotes_are_not_backfilled_from_valuation(self):
        for field in ('p1', 'p2'):
            data = yutong_example()
            del data[field]
            with self.assertRaises(ValueError):
                build_document(data)
        data = yutong_example()
        del data['p2']['price']
        with self.assertRaises(ValueError):
            build_document(data)

    def test_quotes_are_not_silently_rounded(self):
        data = yutong_example()
        for field in ('p1', 'p2'):
            bad = deepcopy(data)
            bad[field]['base' if field == 'p1' else 'price'] = Decimal('10.005')
            with self.assertRaisesRegex(ValueError, 'precision'):
                build_document(bad)
        data['p1'] = {'base': Decimal('22.4200')}
        self.assertEqual(build_document(data)['price_map']['p1'], data['p1'])

    def test_quote_serialization_refuses_loss_and_preserves_hkd_precision(self):
        data = yutong_example()
        data['p1'] = {'base': Decimal('999999999999999.99')}
        with self.assertRaisesRegex(ValueError, 'without changing quote'):
            build_document(data)
        data = yutong_example()
        data['meta'].update(code='01952.HK', currency='HKD')
        data['valuation'] = dict(kind='per_share', values=dict(low=20, base=30, high=40),
                                 currency='HKD', unit='per_share', fx_to_quote=1)
        data['p1'] = {'base': Decimal('22.421')}
        data['p2']['price'] = Decimal('16.001')
        data['t1']['price_condition'] = '股价≥30港元/股'
        original = deepcopy(data)
        document = build_document(data)
        self.assertEqual(document['price_map']['p1'], data['p1'])
        self.assertEqual(document['price_map']['p2'], data['p2'])
        self.assertEqual(data, original)
        document['price_map']['p1']['base'] = 25
        self.assertEqual(data, original)

    def test_single_quote_does_not_become_p2_lower_anchor(self):
        data = yutong_example()
        # This report's explicit P2 is outside 5%-10% of its single P1. No
        # lower-bound assumption is made during export.
        data["p2"] = {"status": "suspended", "price": 16, "reason": "在册事件窗口，完成复评后才恢复"}
        result = build_document(data)
        self.assertEqual(result["price_map"]["p2"]["status"], "suspended")
        self.assertEqual(result["price_map"]["p2"]["price"], 16)
        data['p2']['price'] = data['p1']['base']
        with self.assertRaisesRegex(ValueError, 'below P1'):
            build_document(data)

    def test_invalid_numeric_values_and_listing_currency_are_rejected(self):
        for value in (True, float("nan"), float("inf"), -0.01, 0, "0.1"):
            with self.subTest(price=value):
                data = yutong_example()
                data["p2"]["price"] = value
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
        data["p2"] = {"status": "cancelled", "price": None, "reason": "现金流修复证据弱"}
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

    def test_legacy_frozen_and_unavailable_without_calculation_remain_unpriced(self):
        for mode in ("frozen", "unavailable"):
            with self.subTest(mode=mode):
                data = yutong_example()
                data.update(mode=mode, reason="关键条件未满足", p1=None)
                data["p2"] = {"status": "unavailable", "price": None, "reason": "等待复核"}
                if mode == "unavailable":
                    data["valuation"] = None
                result = build_document(data)
                self.assertIsNone(result["price_map"]["p1"])
                self.assertIsNone(result["price_map"]["p2"]["price"])
                result["price_map"]["p2"]["price"] = 10
                with self.assertRaises(ValueError):
                    validate_document(result)

    def test_temporary_freeze_preserves_valuation_and_observation_prices(self):
        data = yutong_example()
        data.update(mode="frozen", reason="D5市场状态限制买入；仅用于研究观察")
        data["p2"] = {"status": "suspended", "price": 16, "reason": "原重建条件满足且逐股复评后才可恢复"}
        result = build_document(data)
        self.assertEqual(result["meta"]["schema_version"], "stock-research/v3")
        self.assertEqual(result["price_map"]["mode"], "frozen")
        self.assertEqual(result["price_map"]["p1"], {"base": 22.42})
        self.assertEqual(result["price_map"]["p2"], dict(data["p2"], price=16.00))
        validate_document(result)
        data["p2"] = {"status": "cancelled", "price": None, "reason": "本轮取消P2，不转移仓位"}
        cancelled = build_document(data)
        self.assertIsNotNone(cancelled["price_map"]["p1"])
        self.assertIsNone(cancelled["price_map"]["p2"]["price"])

    def test_frozen_observation_prices_never_have_active_p2(self):
        for status in ("active", "unavailable"):
            with self.subTest(status=status):
                data = yutong_example()
                data.update(mode="frozen", reason="窗口冻结")
                data["p2"] = {"status": status, "price": 16 if status == 'active' else None, "reason": "窗口未完成复核"}
                with self.assertRaisesRegex(ValueError, "suspended or cancelled"):
                    build_document(data)
                result = build_document(yutong_example())
                result["price_map"].update(mode="frozen", reason="窗口冻结")
                result["price_map"]["p2"] = dict(data["p2"], price=16 if status == "active" else None)
                with self.assertRaisesRegex(ValueError, "suspended or cancelled"):
                    validate_document(result)

    def test_frozen_quotes_require_valuation_and_valid_explicit_prices(self):
        for updates in ({"valuation": None}, {"p1": {}}, {'p1': {'base': True}}):
            with self.subTest(updates=updates):
                data = yutong_example()
                data.update(mode="frozen", reason="暂时市场限制，事实可靠")
                data["p2"] = {"status": "suspended", "price": 16, "reason": "等待复核"}
                data.update(updates)
                with self.assertRaises(ValueError):
                    build_document(data)

    def test_frozen_p1_still_requires_valuation_and_valid_price_order(self):
        data = yutong_example()
        data.update(mode="frozen", reason="公司可估，事件窗口暂停")
        data["p2"] = {"status": "suspended", "price": 16, "reason": "等窗口实际结果复评"}
        result = build_document(data)
        for mutation in (lambda p: p.update(v50=None),
                         lambda p: p.update(p1={"low": 30, "base": 40, "high": 35}),
                         lambda p: p["p2"].update(price=23)):
            with self.subTest(mutation=mutation):
                invalid = deepcopy(result)
                mutation(invalid["price_map"])
                with self.assertRaises(ValueError):
                    validate_document(invalid)

    def test_rejection_or_unavailable_cannot_use_frozen_price_exception(self):
        data = yutong_example()
        for mode in ("rejected", "unavailable"):
            with self.subTest(mode=mode):
                data.update(mode=mode, reason="治理红线或核心证据不可得")
                data["p2"] = {"status": "cancelled", "price": None, "reason": "不具备估值基础"}
                with self.assertRaisesRegex(ValueError, "unpriced mode"):
                    build_document(data)

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

    def test_cli_check_legacy_t1_prose_without_relaxing_v3_or_structural_checks(self):
        document = build_document(yutong_example())
        document['meta']['schema_version'] = 'stock-research/v2'
        document['price_map']['p1'] = dict(low=17.29, base=22.42, high=28.18)
        document['price_map']['t1']['price_condition'] = '价格达到观察区间时复核'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'historical.json'
            command = [sys.executable, str(ROOT / 'scripts/stock_price_map.py'), 'check', str(path)]
            path.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
            original = path.read_bytes()
            checked = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertNotIn('T1 delivery checked', checked.stdout)
            self.assertEqual(path.read_bytes(), original)
            document['meta']['schema_version'] = 'stock-research/v3'
            path.write_text(json.dumps(document), encoding='utf-8')
            checked = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(checked.returncode, 0)
            self.assertIn('t1 delivery', checked.stderr)
            document['meta']['schema_version'] = 'stock-research/v2'
            document['price_map']['p2']['price'] = 20.7
            path.write_text(json.dumps(document), encoding='utf-8')
            checked = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(checked.returncode, 0)
            self.assertIn('P1_low', checked.stderr)

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
