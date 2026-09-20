"""CSI 300 anchors are the 2026-09-18 legulegu monthly readings quoted in the task spec; the rest is synthetic."""
from datetime import date, timedelta
from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etf_calc import (aggregate_valuation, erp_spread, expanding_percentile, history_quantiles, joint_stress_loss, level_at_multiple,
                              lookthrough_weights, loss_budget_cap, month_end_levels, premium_pct, return_decomposition,
                              scenario_annual_return, sma_state, tracking_difference, tracking_error)

END = dict(date="20260918", level=4507.39, pe=12.68)
BASES = dict(fund_basis="adj_nav", index_basis="total_return", fund_currency="CNY", index_currency="CNY")


def monthly(values, start=date(2010, 1, 31)):
    return [(start + timedelta(days=30 * i), value) for i, value in enumerate(values)]


def daily(levels, start=date(2025, 1, 1)):
    return [(start + timedelta(days=i), level) for i, level in enumerate(levels)]


class ReturnDecompositionTests(unittest.TestCase):
    def test_csi300_since_2007_peak_matches_spec(self):
        result = return_decomposition(dict(date="20071031", level=5688.54, pe=47.84), END)
        self.assertEqual(result["status"], "complete")
        self.assertAlmostEqual(result["years"], 18.9, places=1)
        self.assertEqual([round(result[k], 2) for k in ("price_annual_pct", "eps_annual_pct", "valuation_annual_pct")],
                         [-1.22, 5.97, -6.79])

    def test_csi300_since_2005_start_matches_spec(self):
        result = return_decomposition(dict(date="20050429", level=932.40, pe=13.99), END)
        self.assertAlmostEqual(result["years"], 21.4, places=1)
        self.assertEqual([round(result[k], 2) for k in ("price_annual_pct", "eps_annual_pct", "valuation_annual_pct")],
                         [7.65, 8.14, -0.46])

    def test_parts_compound_rather_than_add(self):
        result = return_decomposition(dict(date="20071031", level=5688.54, pe=47.84), END)
        compounded = (1 + result["eps_annual_pct"] / 100) * (1 + result["valuation_annual_pct"] / 100) - 1
        self.assertAlmostEqual(compounded * 100, result["price_annual_pct"], places=9)

    def test_non_positive_or_missing_pe_is_a_gap_not_a_number(self):
        for bad in (0, -8.5, None, float("nan"), "n/a"):
            result = return_decomposition(dict(date="20071031", level=5688.54, pe=bad), END)
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(result["missing_fields"], ["start_pe"])
            self.assertIsNone(result["price_annual_pct"])

    def test_sub_year_window_is_not_annualized(self):
        result = return_decomposition(dict(date="20260318", level=4000, pe=12), END)
        self.assertEqual(result["missing_fields"], ["window_shorter_than_one_year"])
        self.assertIsNone(result["eps_annual_pct"])

    def test_reversed_dates_raise(self):
        with self.assertRaises(ValueError):
            return_decomposition(END, dict(date="20071031", level=5688.54, pe=47.84))


class ExpandingPercentileTests(unittest.TestCase):
    def test_share_strictly_below_with_current_in_sample(self):
        result = expanding_percentile(monthly(list(range(1, 101))))
        self.assertEqual((result["status"], result["percentile"], result["sample_n"]), ("complete", 99.0, 100))
        lowest = expanding_percentile(monthly(list(range(100, 0, -1))))
        self.assertEqual(lowest["percentile"], 0.0)

    def test_ties_do_not_count_as_below(self):
        self.assertEqual(expanding_percentile(monthly([5.0] * 80))["percentile"], 0.0)

    def test_short_history_gives_no_percentile(self):
        result = expanding_percentile(monthly(list(range(59))))  # 58 * 30 days < 5 years
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["percentile"])
        self.assertTrue(result["missing_fields"][0].startswith("history_shorter_than_min_years"))
        self.assertEqual(expanding_percentile([])["missing_fields"], ["current_value"])

    def test_window_uses_trailing_years_only_and_must_be_covered(self):
        values = [1000.0] * 100 + list(range(1, 131))  # old highs fall out of the 10-year window
        full = expanding_percentile(monthly(values))
        windowed = expanding_percentile(monthly(values), window_years=10)
        self.assertAlmostEqual(full["percentile"], 100 * 129 / 230)
        self.assertEqual(windowed["sample_n"], 122)  # 3652.5 days / 30-day spacing
        self.assertAlmostEqual(windowed["percentile"], 100 * 121 / 122)
        uncovered = expanding_percentile(monthly(list(range(100))), window_years=10)
        self.assertIsNone(uncovered["percentile"])
        self.assertTrue(uncovered["missing_fields"][0].startswith("window_not_covered"))

    def test_missing_history_is_dropped_but_missing_current_is_a_gap(self):
        values = list(range(1, 81))
        values[10] = None
        values[20] = float("nan")
        self.assertEqual(expanding_percentile(monthly(values))["sample_n"], 78)
        self.assertEqual(expanding_percentile(monthly(values[:-1] + [None]))["missing_fields"], ["current_value"])

    def test_unsorted_or_duplicate_dates_raise(self):
        series = monthly([1, 2, 3])
        for bad in (series[::-1], series + [series[-1]]):
            with self.assertRaises(ValueError):
                expanding_percentile(bad)

    def test_history_quantiles_share_the_sample_and_guards(self):
        result = history_quantiles(monthly(list(range(1, 102))))
        self.assertEqual((result["status"], result["sample_n"]), ("complete", 101))
        self.assertEqual(result["levels"], {10: 11.0, 25: 26.0, 50: 51.0, 75: 76.0, 90: 91.0})
        windowed = history_quantiles(monthly([1000.0] * 100 + list(range(1, 131))), (50,), window_years=10)
        self.assertEqual((windowed["sample_n"], windowed["levels"]), (122, {50: 69.5}))
        short = history_quantiles(monthly(list(range(59))))
        self.assertEqual((short["status"], short["levels"]), ("incomplete", None))
        self.assertEqual(history_quantiles([(date(2026, 1, 1), 5)], min_years=0)["missing_fields"], ["sample_n:1/2"])
        for bad in ((0,), (100,), (12.5,)):
            with self.assertRaises(ValueError):
                history_quantiles(monthly(list(range(80))), bad)


class AggregateValuationTests(unittest.TestCase):
    def test_weight_harmonic_multiples_and_weighted_yield(self):
        weights = {"A": 50, "B": 30, "C": 20}
        rows = {"A": dict(pe_ttm=10, pb=1.0, dv_ttm=4.0), "B": dict(pe_ttm=20, pb=2.0, dv_ttm=2.0), "C": dict(pe_ttm=40, pb=4.0, dv_ttm=0.0)}
        result = aggregate_valuation(weights, rows)
        self.assertEqual(result["status"], "complete")
        self.assertAlmostEqual(result["pe_ttm"], 100 / (50 / 10 + 30 / 20 + 20 / 40))   # 14.29: earnings-weighted, not mean of PEs
        self.assertAlmostEqual(result["pb"], 100 / (50 / 1 + 30 / 2 + 20 / 4))
        self.assertAlmostEqual(result["dividend_yield_pct"], (50 * 4 + 30 * 2) / 100)
        self.assertEqual((result["loss_weight_pct"], result["coverage_pct"], result["total_weight_pct"]), (0.0, 100.0, 100.0))

    def test_loss_makers_are_counted_not_guessed(self):
        rows = {"A": dict(pe_ttm=10, pb=1.0, dv_ttm=None), "B": dict(pe_ttm=None, pb=0.8, dv_ttm=1.0), "C": dict(pe_ttm=-5, pb=None, dv_ttm=None)}
        result = aggregate_valuation({"A": 60, "B": 25, "C": 15}, rows)
        self.assertAlmostEqual(result["pe_ttm"], 100 / (60 / 10))   # B and C excluded from earnings
        self.assertAlmostEqual(result["loss_weight_pct"], 40.0)
        self.assertAlmostEqual(result["pb"], 100 / (60 / 1 + 25 / 0.8))   # C's book treated as zero, like a loss-maker's earnings
        self.assertAlmostEqual(result["dividend_yield_pct"], 25 * 1.0 / 100)

    def test_thin_coverage_gives_no_multiple(self):
        result = aggregate_valuation({"A": 50, "B": 50}, {"A": dict(pe_ttm=10, pb=1, dv_ttm=1)})
        self.assertEqual((result["status"], result["pe_ttm"], result["pb"]), ("incomplete", None, None))
        self.assertEqual(result["missing_fields"], ["coverage_pct:50.0/90"])
        self.assertEqual(result["coverage_pct"], 50.0)
        self.assertEqual(aggregate_valuation({}, {})["missing_fields"], ["weights"])
        with self.assertRaises(ValueError):
            aggregate_valuation({"A": -1}, {})
        all_losses = aggregate_valuation({"A": 100}, {"A": dict(pe_ttm=None, pb=None, dv_ttm=None)})
        self.assertEqual((all_losses["status"], all_losses["pe_ttm"], all_losses["loss_weight_pct"]), ("complete", None, 100.0))


class ScalarTests(unittest.TestCase):
    def test_erp_spread_is_in_percentage_points(self):
        self.assertAlmostEqual(erp_spread(12.68, 1.682), 100 / 12.68 - 1.682)
        self.assertAlmostEqual(erp_spread(20, -0.5), 5.5)
        for pe, bond in ((0, 1.7), (-5, 1.7), (None, 1.7), (12, None), (12, float("inf"))):
            self.assertIsNone(erp_spread(pe, bond))

    def test_level_at_multiple_scales_the_level_with_earnings_held_constant(self):
        self.assertAlmostEqual(level_at_multiple(4507.39, 12.68, 10.08), 4507.39 * 10.08 / 12.68)
        self.assertAlmostEqual(level_at_multiple(4507.39, 12.68, 12.68), 4507.39)
        for args in ((None, 12, 10), (4500, 0, 10), (4500, -3, 10), (4500, 12, None), (0, 12, 10)):
            self.assertIsNone(level_at_multiple(*args))

    def test_premium_pct_and_the_ten_percent_collapse(self):
        self.assertAlmostEqual(premium_pct(1.10, 1.00), 10.0)
        self.assertAlmostEqual(premium_pct(1.00, 1.10), -100 / 11)  # premium gone: -9.09%
        for price, nav in ((1, 0), (None, 1), (0, 1), ("x", 1)):
            self.assertIsNone(premium_pct(price, nav))

    def test_loss_budget_cap_matches_user_budget(self):
        self.assertAlmostEqual(loss_budget_cap(35000, -70), 50000)
        self.assertAlmostEqual(loss_budget_cap(35000, -75), 46666.6667, places=3)
        self.assertIsNone(loss_budget_cap(None, -70))
        self.assertIsNone(loss_budget_cap(35000, None))
        for bad in (70, 0, -101):  # sign or unit mistakes must not yield a cap
            with self.assertRaises(ValueError):
                loss_budget_cap(35000, bad)


class ScenarioTests(unittest.TestCase):
    def test_base_scenario_has_zero_valuation_change(self):
        result = scenario_annual_return(6, 2.5, 12.68, 12.68, 5, 0.6)
        self.assertEqual(result["valuation_change_pct"], 0)
        self.assertAlmostEqual(result["annual_return_pct"], 7.9)

    def test_multiple_compression_is_annualized(self):
        result = scenario_annual_return(6, 2.5, 20, 10, 5, 0)
        self.assertAlmostEqual(result["valuation_change_pct"], (0.5 ** 0.2 - 1) * 100)
        self.assertAlmostEqual(result["annual_return_pct"], 8.5 + (0.5 ** 0.2 - 1) * 100)

    def test_any_unknown_input_blocks_the_result(self):
        result = scenario_annual_return(None, 2.5, 0, 10, 5, 0.6)
        self.assertEqual(result["missing_fields"], ["eps_growth_pct", "current_multiple"])
        self.assertIsNone(result["annual_return_pct"])
        self.assertIsNone(result["valuation_change_pct"])


class TrackingTests(unittest.TestCase):
    def setUp(self):
        self.index = daily([100 * 1.0004 ** i for i in range(400)])
        self.fund = daily([1.0 * 1.0004 ** i * (1 - 0.00002 * i) for i in range(400)])

    def test_difference_is_fund_minus_index(self):
        result = tracking_difference(self.fund, self.index, **BASES)
        expected = ((1 - 0.00002 * 399) - 1) * 1.0004 ** 399 * 100
        self.assertEqual(result["status"], "complete")
        self.assertAlmostEqual(result["period_td_pct"], expected)
        self.assertLess(result["annual_td_pct"], 0)
        self.assertEqual((result["window_start"], result["observations"]), (date(2025, 1, 1), 400))

    def test_short_window_reports_period_only(self):
        result = tracking_difference(self.fund[:200], self.index[:200], **BASES)
        self.assertEqual(result["status"], "complete")
        self.assertIsNone(result["annual_td_pct"])
        self.assertIsNotNone(result["period_td_pct"])

    def test_identical_paths_have_zero_error_and_noise_is_annualized(self):
        same = tracking_error(daily([1.0 * 1.0004 ** i for i in range(400)]), self.index, **BASES)
        self.assertAlmostEqual(same["annual_te_pct"], 0, places=9)
        noisy = daily([level * (1.001 if i % 2 else 1.0) for i, (_, level) in enumerate(self.index)])
        result = tracking_error(noisy, self.index, **BASES)
        self.assertAlmostEqual(result["annual_te_pct"], 0.1 * math.sqrt(250), delta=0.05)

    def test_only_common_dates_are_used(self):
        sparse = [point for i, point in enumerate(self.fund) if i % 2 == 0]
        result = tracking_difference(sparse, self.index, **BASES)
        self.assertEqual(result["observations"], 200)
        self.assertEqual(result["window_end"], sparse[-1][0])

    def test_undeclared_basis_or_currency_is_a_gap(self):
        for override, expected in ((dict(fund_basis=None), "fund_basis"), (dict(index_basis="close"), "index_basis"),
                                   (dict(index_currency=None), "currency"),
                                   (dict(index_currency="HKD"), "currency_mismatch:CNY/HKD")):
            for function, key in ((tracking_difference, "period_td_pct"), (tracking_error, "annual_te_pct")):
                result = function(self.fund, self.index, **{**BASES, **override})
                self.assertEqual((result["status"], result["missing_fields"], result[key]),
                                 ("incomplete", [expected], None))

    def test_price_index_is_computed_with_a_dividend_warning(self):
        result = tracking_difference(self.fund, self.index, **{**BASES, "index_basis": "price"})
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["warnings"], ["index_price_basis_excludes_dividends"])

    def test_too_few_aligned_observations_is_a_gap(self):
        result = tracking_error(self.fund[:119], self.index, **BASES)
        self.assertEqual(result["missing_fields"], ["aligned_observations:119/120"])
        self.assertIsNone(result["annual_te_pct"])
        bad_levels = tracking_difference(daily([0, None] * 200), self.index, **BASES)
        self.assertEqual(bad_levels["missing_fields"], ["aligned_observations:0/120"])


class LookthroughTests(unittest.TestCase):
    def test_direct_plus_fund_times_constituent(self):
        result = lookthrough_weights({"600519.SH": 5}, {"A500": 20, "DRUG": 10},
                                     {"A500": {"600519.SH": 3, "300750.SZ": 4},
                                      "DRUG": {"01093.HK": 10, "300750.SZ": 0}})
        self.assertEqual(result["status"], "complete")
        self.assertAlmostEqual(result["weights_pct"]["600519.SH"], 5.6)
        self.assertAlmostEqual(result["weights_pct"]["300750.SZ"], 0.8)
        self.assertAlmostEqual(result["weights_pct"]["01093.HK"], 1.0)
        self.assertAlmostEqual(result["unresolved_pct"], 20 * 0.93 + 10 * 0.9)
        self.assertAlmostEqual(sum(result["weights_pct"].values()) + result["unresolved_pct"], 35)

    def test_fund_without_constituents_stays_unresolved(self):
        result = lookthrough_weights({}, {"GOLD": 8, "HSTECH": 12}, {"HSTECH": {}})
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["missing_fields"], ["constituents:GOLD", "constituents:HSTECH"])
        self.assertEqual((result["weights_pct"], result["unresolved_pct"]), ({}, 20.0))

    def test_invalid_weights_raise(self):
        for args in (({"X": -1}, {}, {}), ({}, {"F": None}, {}), ({}, {"F": 10}, {"F": {"X": 60, "Y": 60}}),
                     ({}, {"F": 10}, {"F": {"X": float("nan")}})):
            with self.assertRaises(ValueError):
                lookthrough_weights(*args)


class StressTests(unittest.TestCase):
    def test_sector_book_at_minus_seventy(self):
        result = joint_stress_loss([(94349, -70), (49024, -70), (11774, -70), (11570, -70), (8845, -70)])
        self.assertAlmostEqual(result["loss"], 175562 * 0.7)

    def test_empty_book_is_zero_and_unknown_drawdown_blocks_the_total(self):
        self.assertEqual(joint_stress_loss([])["loss"], 0.0)
        result = joint_stress_loss([(50000, -70), (10000, None), (-5, -60)])
        self.assertEqual(result["missing_fields"], ["position_1:stress_drawdown_pct", "position_2:amount"])
        self.assertIsNone(result["loss"])
        with self.assertRaises(ValueError):
            joint_stress_loss([(50000, 70)])


class TrendTests(unittest.TestCase):
    def test_month_end_levels_keeps_last_observation_per_month(self):
        series = [(date(2026, 7, 30), 1), (date(2026, 7, 31), 2), (date(2026, 8, 28), 3), (date(2026, 9, 18), 4)]
        self.assertEqual(month_end_levels(series),
                         [(date(2026, 7, 31), 2.0), (date(2026, 8, 28), 3.0), (date(2026, 9, 18), 4.0)])
        self.assertEqual(month_end_levels([]), [])

    def test_sma_state(self):
        above = sma_state([1] * 9 + [2], 10)
        self.assertEqual((above["state"], above["sma"]), ("above", 1.1))
        self.assertAlmostEqual(above["distance_pct"], (2 / 1.1 - 1) * 100)
        self.assertEqual(sma_state([3, 3, 3, 2], 3)["state"], "below")
        self.assertEqual(sma_state([5, 5], 2)["state"], "at")
        self.assertEqual(sma_state([9, 9, 1, 2, 3], 3)["sma"], 2)  # only the trailing window counts

    def test_insufficient_or_invalid_levels_are_gaps(self):
        short = sma_state([1] * 9, 10)
        self.assertEqual((short["status"], short["missing_fields"], short["state"]), ("incomplete", ["levels:9/10"], None))
        self.assertEqual(sma_state([1, None, 3], 3)["missing_fields"], ["invalid_level_in_window"])
        self.assertEqual(sma_state([], 1)["missing_fields"], ["levels:0/1"])
        for bad in (0, -1, 2.5):
            with self.assertRaises(ValueError):
                sma_state([1, 2, 3], bad)


if __name__ == "__main__":
    unittest.main()
