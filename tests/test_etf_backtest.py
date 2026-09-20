"""Synthetic paths with hand-computable outcomes; nothing here is market data or a backtest result."""
from datetime import date, timedelta
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.etf_backtest import (BUY_COST, annualized, by_month, consecutive_tail, downside_capture, drawdown_state, evaluate_dca_pause,
                                  evaluate_ladder, fold_slices, judge, ladder_target, lagged, max_drawdown,
                                  money_weighted, percentile_series, rule_verdict, run_constant_mix, run_dca,
                                  run_ladder, time_weighted, trend_gate)

FLAT = [0.0] * 6


class LadderTests(unittest.TestCase):
    def test_target_is_one_way_in_each_zone(self):
        self.assertEqual(ladder_target(5, 0.0), 1.0)
        self.assertEqual(ladder_target(10, 0.5), 1.0)
        self.assertEqual(ladder_target(20, 0.0), 0.5)
        self.assertIsNone(ladder_target(20, 0.8))      # back up from the deeper rung: the extra is not sold
        self.assertIsNone(ladder_target(50, 0.0))      # middle zone: nothing
        self.assertIsNone(ladder_target(50, 1.0))
        self.assertEqual(ladder_target(75, 1.0), 0.3)
        self.assertIsNone(ladder_target(90, 0.1))      # reduce zone never buys
        self.assertIsNone(ladder_target(None, 0.5))

    def test_ratchet_buys_on_the_way_down_and_holds_on_the_way_back(self):
        values, weights = run_ladder(FLAT, FLAT, [50, 20, 5, 20, 50, 80])
        half = 0.5 * (1 - BUY_COST)
        self.assertEqual(weights[0], 0.0)
        self.assertAlmostEqual(values[1], 0.5 + half)                      # bought half, paid the fee on it
        self.assertAlmostEqual(weights[1], half / (0.5 + half))
        self.assertAlmostEqual(weights[2], 1.0)                            # all in at the deep rung
        self.assertEqual(weights[3], weights[2])                           # back in the shallow rung: no sale
        self.assertEqual(weights[4], weights[2])
        self.assertAlmostEqual(weights[5], 0.3)                            # expensive: sold down, sales are free
        self.assertAlmostEqual(values[5], values[4])

    def test_gate_blocks_purchases_but_never_sales(self):
        gate = [False, False, True, True, True, False]
        _, weights = run_ladder(FLAT, FLAT, [5, 5, 5, 50, 50, 80], gate)
        self.assertEqual(weights[:2], [0.0, 0.0])
        self.assertAlmostEqual(weights[2], 1.0)
        self.assertAlmostEqual(weights[5], 0.3)          # gate closed, the reduction still happens

    def test_returns_accrue_on_the_position_carried_into_the_month(self):
        values, _ = run_ladder([0.0, 0.10, -0.50], [0.0, 0.01, 0.01], [5, 50, 50])
        invested = 1 - BUY_COST
        self.assertAlmostEqual(values[1], invested * 1.10)
        self.assertAlmostEqual(values[2], invested * 1.10 * 0.50)
        cash_only, _ = run_ladder([0.0, 0.10, -0.50], [0.0, 0.01, 0.01], [50, 50, 50])
        self.assertAlmostEqual(cash_only[2], 1.01 ** 2)

    def test_constant_mix_full_weight_is_buy_and_hold(self):
        values = run_constant_mix([0.0, 0.2, -0.1], FLAT[:3], 1.0)
        self.assertAlmostEqual(values[2], (1 - BUY_COST) * 1.2 * 0.9)
        half = run_constant_mix([0.0, 1.0], [0.0, 0.0], 0.5)
        self.assertAlmostEqual(half[1], 0.5 * (1 - BUY_COST) * 2 + 0.5)   # rebalancing here is a sale: free


class DcaTests(unittest.TestCase):
    def test_paused_contributions_stay_in_cash_for_good(self):
        values, flows = run_dca([0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [True, False, True])
        self.assertEqual(flows, [1.0, 1.0, 1.0])
        self.assertAlmostEqual(values[2], (1 - BUY_COST) * 2 + 1 + (1 - BUY_COST))
        fixed, _ = run_dca([0.0, 0.0, 1.0], [0.0, 0.0, 0.0])
        self.assertAlmostEqual(fixed[2], (1 - BUY_COST) * 2 * 2 + (1 - BUY_COST))

    def test_time_weighting_removes_the_contributions(self):
        values, flows = run_dca([0.0, 0.1, -0.2], FLAT[:3])
        index = time_weighted(values, flows)
        unit = 1 - BUY_COST                                              # each contribution pays its purchase fee on arrival
        self.assertAlmostEqual(index[1], (unit * 1.1 + unit - 1) / unit)   # 10% less the fee on the new money
        self.assertAlmostEqual(index[2] / index[1], ((unit * 1.1 + unit) * 0.8 + unit - 1) / (unit * 1.1 + unit))

    def test_money_weighted_return_solves_the_cash_flows(self):
        monthly = 0.01
        flows = [1.0] * 24
        terminal = sum((1 + monthly) ** (23 - t) for t in range(24))
        self.assertAlmostEqual(money_weighted([0.0] * 23 + [terminal], flows), 1.01 ** 12 - 1, places=6)
        self.assertIsNone(money_weighted([0.0] * 23 + [1e9], flows))


class MetricTests(unittest.TestCase):
    def test_drawdown_annualized_and_capture(self):
        self.assertAlmostEqual(max_drawdown([1, 1.2, 0.6, 0.9, 1.5, 1.2]), -0.5)
        self.assertEqual(max_drawdown([1, 2, 3]), 0.0)
        self.assertAlmostEqual(annualized([1.0] + [1.21] * 24), 0.1)
        self.assertIsNone(annualized([1.0]))
        held = run_constant_mix([0.0] * 13, [0.0] * 13, 1.0)               # flat market: the only thing that happens is the entry fee
        self.assertEqual(annualized(held), 0.0)                           # measured from after the purchase the fee vanishes
        self.assertAlmostEqual(annualized(held, 1.0), -BUY_COST)          # measured from the capital put in, it is charged
        self.assertAlmostEqual(downside_capture([1, 0.95, 1.0, 0.98], [1, 0.9, 1.0, 0.95]), (0.05 + 0.02) / (0.1 + 0.05))
        self.assertIsNone(downside_capture([1, 1.1], [1, 1.2]))

    def test_judge_follows_the_preregistered_thresholds(self):
        def fold(dd, ann, mix=None):
            row = dict(drawdown=dd, annual=ann)
            if mix:
                row["annual_mix"] = mix
            return row
        good = [fold((-0.2, -0.4), (0.06, 0.07), (0.06, 0.05))] * 2 + [fold((-0.1, -0.3), (0.08, 0.05), (0.08, 0.06))]
        self.assertEqual(judge(good, skill=True)["verdict"], "pass")
        self.assertEqual(judge(good[:2])["verdict"], "insufficient_data")
        worse_risk = good[:2] + [fold((-0.5, -0.3), (0.08, 0.05), (0.08, 0.06))]
        self.assertEqual(judge(worse_risk, skill=True)["verdict"], "fail")            # drawdown better in only 2 folds
        costly = [fold((-0.2, -0.4), (0.02, 0.07)), fold((-0.2, -0.4), (0.03, 0.07)), fold((-0.2, -0.4), (0.01, 0.07))]
        self.assertFalse(judge(costly)["cost_ok"])                                     # lag of 5pp +- 1pp is not noise
        noisy = [fold((-0.2, -0.4), (0.02, 0.07)), fold((-0.2, -0.4), (0.12, 0.07)), fold((-0.2, -0.4), (0.04, 0.07))]
        self.assertTrue(judge(noisy)["cost_ok"])                                       # mean -1pp, sigma 5.3pp
        unskilled = [fold((-0.2, -0.4), (0.07, 0.07), (0.07, 0.08))] * 3           # safer than holding, no worse, but a plain mix does better
        self.assertEqual(judge(unskilled, skill=True)["verdict"], "no_timing_skill")
        tied_but_behind = [fold((-0.2, -0.4), (0.06, 0.07))] * 3                       # sigma 0 and mean < 0
        self.assertEqual(judge(tied_but_behind)["verdict"], "fail")
        with_a_hole = good + [fold((-0.2, -0.4), (None, 0.07), (None, 0.05))]          # an uncomputable fold does not vote or crash
        self.assertEqual((judge(with_a_hole, skill=True)["folds"], judge(with_a_hole, skill=True)["verdict"]), (3, "pass"))

    def test_rule_verdict_needs_the_primary_index_and_a_majority(self):
        ok, bad, thin = dict(verdict="pass"), dict(verdict="fail"), dict(verdict="insufficient_data")
        self.assertEqual(rule_verdict(ok, [ok, ok, bad, thin]), "validated")
        self.assertEqual(rule_verdict(ok, [ok, bad, thin]), "validated(primary_index_only)")
        self.assertEqual(rule_verdict(ok, []), "validated(primary_index_only)")
        self.assertEqual(rule_verdict(bad, [ok, ok]), "rejected")
        self.assertEqual(rule_verdict(dict(verdict="no_timing_skill"), [ok]), "rejected(no_timing_skill)")
        self.assertEqual(rule_verdict(thin, [ok]), "data_insufficient")


class SignalTests(unittest.TestCase):
    def test_percentiles_use_only_the_past(self):
        days = [date(2000, 1, 31) + timedelta(days=30 * t) for t in range(80)]
        rising = percentile_series(days, [float(t) for t in range(80)])
        self.assertTrue(all(value is None for value in rising[:60]))      # under five years of history
        self.assertAlmostEqual(rising[-1], 100 * 79 / 80)
        with_spike = percentile_series(days, [float(t) for t in range(79)] + [-1.0])
        self.assertEqual(with_spike[-1], 0.0)
        self.assertEqual(with_spike[:-1], rising[:-1])                    # the future never rewrites the past

    def test_month_keys_and_unbroken_runs(self):
        table = by_month(["20260130", "20260227", "20260302", "20260331"], [1.0, 2.0, 3.0, 4.0])
        self.assertEqual({month: value for month, (_, value) in table.items()}, {"202601": 1.0, "202602": 2.0, "202603": 4.0})
        self.assertEqual(consecutive_tail(["202510", "202512", "202601", "202602"]), ["202512", "202601", "202602"])
        self.assertEqual(consecutive_tail(["202601"]), ["202601"])

    def test_drawdown_state_and_gate_and_lag(self):
        self.assertEqual(drawdown_state([10, 20, 10, 5, 5], window=3), [1.0, 1.0, 0.5, 0.25, 0.5])
        gate = trend_gate([1.0] * 9 + [2.0, 0.5])
        self.assertEqual(gate[:9], [None] * 9)                            # no ten-month average yet: unknown, treated as closed
        self.assertEqual(gate[9:], [True, False])
        self.assertEqual(lagged([1, 2, 3]), [None, 1, 2])


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.months = [f"{year}{month:02d}" for year in range(2005, 2027) for month in range(1, 13)][:260]
        cycle = [0.03] * 18 + [-0.04] * 18                                # long swings the ladder can exploit
        self.returns = [cycle[t % 36] for t in range(260)]
        self.cash = [0.002] * 260
        level, self.closes = 100.0, []
        for change in self.returns:
            level *= 1 + change
            self.closes.append(level)

    def test_fold_slices_follow_the_preregistered_calendar(self):
        self.assertEqual([(name, end - start + 1, length) for name, start, end, length in fold_slices(self.months)],
                         [("F1", 72, 72), ("F2", 72, 72), ("F3", 72, 72), ("F4", 44, 44)])
        late = fold_slices(self.months[100:])                                   # a series that starts in 2013-05
        self.assertEqual(late[0][0], "F2")
        self.assertEqual((late[0][2] - late[0][1] + 1, late[0][3]), (44, 72))   # 44 months present, judged against 72

    def test_a_series_that_starts_mid_fold_does_not_get_a_shorter_fold(self):
        start = 100
        rows, _ = evaluate_ladder(self.months[start:], self.returns[start:], self.cash[start:], [20.0] * 160)
        self.assertEqual([row["fold"] for row in rows], ["F3", "F4"])          # F2: 44 of 72 calendar months
        rows, _ = evaluate_dca_pause(self.months[start:], self.returns[start:], self.cash[start:], self.closes[start:])
        self.assertEqual([row["fold"] for row in rows], ["F3", "F4"])

    def test_folds_without_a_signal_do_not_count(self):
        quantiles = [None] * 100 + [20.0] * 160
        rows, verdict = evaluate_ladder(self.months, self.returns, self.cash, quantiles)
        self.assertEqual([row["fold"] for row in rows], ["F3", "F4"])     # F2 has the signal in 44 of 72 months: under 80%
        borderline, _ = evaluate_ladder(self.months, self.returns, self.cash, [None] * 86 + [20.0] * 174)
        self.assertEqual(borderline[0]["fold"], "F2")                     # 58 of 72 months is 80.6%
        self.assertEqual(verdict["verdict"], "insufficient_data")

    def test_a_ladder_on_a_mean_reverting_path_is_scored_against_hold_and_mix(self):
        state = drawdown_state(self.closes)
        days = [date(int(month[:4]), int(month[4:]), 28) for month in self.months]
        quantiles = percentile_series(days, state)
        rows, verdict = evaluate_ladder(self.months, self.returns, self.cash, quantiles)
        self.assertEqual([row["fold"] for row in rows], ["F2", "F3", "F4"])
        for row in rows:
            self.assertLessEqual(row["average_weight"], 1.0)
            self.assertIn("annual_mix", row)
        self.assertIn(verdict["verdict"], ("pass", "fail", "no_timing_skill"))
        gated_rows, gated = evaluate_ladder(self.months, self.returns, self.cash, quantiles,
                                            gate=trend_gate(self.closes), baseline="ungated")
        self.assertNotIn("annual_mix", gated_rows[0])
        self.assertNotIn("skill_ok", gated)

    def test_dca_pause_skips_the_fold_that_predates_the_average(self):
        rows, _ = evaluate_dca_pause(self.months, self.returns, self.cash, self.closes)
        self.assertEqual([row["fold"] for row in rows], ["F2", "F3", "F4"])     # F1 opens before a ten-month average exists
        self.assertTrue(all(0 < row["paused_months"] < row["months"] for row in rows))
        long_history = [True] * len(self.months)                                 # a gate computed on older prices covers F1 too
        rows, _ = evaluate_dca_pause(self.months, self.returns, self.cash, self.closes, long_history)
        self.assertEqual([row["fold"] for row in rows], ["F1", "F2", "F3", "F4"])
        self.assertTrue(all(row["paused_months"] == 0 and row["annual"][0] == row["annual"][1] for row in rows))


if __name__ == "__main__":
    unittest.main()
