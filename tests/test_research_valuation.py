"""Auditable FCFF arithmetic and bounded reverse DCF, without external data."""
from copy import deepcopy
from decimal import Decimal, ROUND_UP, localcontext
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import research_valuation as valuation


def example():
    scenarios = {}
    for label, margin, equity in [('low', .1, 85), ('base', .2, 160), ('high', .3, 235)]:
        scenarios[label] = dict(segments=[dict(
            id='core', source='audited filing, page 20', assumptions='Stable revenue and margins',
            discount_rate=.1,
            years=[dict(year=1, revenue=100, ebit_margin=margin, tax_rate=.25,
                        da=0, capex=0, delta_nwc=0)],
            terminal=dict(growth=0, roic=.1, margin=margin, tax_rate=.25))],
            equity_adjustments=[dict(id='cash', amount=10, reason='Excess cash', source='balance sheet')],
            equity_value=equity)
    return dict(kind='dcf_fcff', currency='CNY', amount_unit='100_million',
                shares=100_000_000, fx_to_quote=1, scenarios=scenarios)


def flat_scenarios(model, scenario):
    model['scenarios'] = {label: deepcopy(scenario) for label in ('low', 'base', 'high')}


class ResearchValuationTests(unittest.TestCase):
    def test_loss_year_does_not_automatically_receive_cash_tax_refund(self):
        model = example()
        model['scenarios']['base']['segments'][0]['years'][0]['ebit_margin'] = -.1
        with self.assertRaisesRegex(ValueError, 'loss.*tax'):
            valuation.evaluate_dcf(model)

    def test_explicit_zero_terminal_for_residual_business_does_not_invent_profit(self):
        model = example()
        row = model['scenarios']['base']
        row['segments'][0]['terminal'].update(growth=0, margin=0)
        row['equity_value'] = Decimal(15) / Decimal('1.1') + 10
        flat_scenarios(model, row)
        detail = valuation.evaluate_dcf(model)['details']['base']['segments'][0]
        self.assertEqual(detail['terminal_pv'], 0)
        model['scenarios']['base']['segments'][0]['terminal']['growth'] = .01
        with self.assertRaisesRegex(ValueError, 'terminal.*NOPAT'):
            valuation.evaluate_dcf(model)

    def test_full_cash_bridge_units_and_unrounded_values(self):
        model = example()
        original = deepcopy(model)
        result = valuation.evaluate_dcf(model)
        self.assertEqual(result['values'], dict(low=Decimal(85), base=Decimal(160), high=Decimal(235)))
        detail = result['details']['base']
        self.assertEqual(detail['enterprise_value'], Decimal(150))
        self.assertEqual(detail['equity_adjustments'], Decimal(10))
        self.assertEqual(detail['equity_value'], Decimal(160))
        self.assertEqual(detail['segments'][0]['years'][0]['fcff'], Decimal(15))
        self.assertEqual(model, original)
        model['shares'] = 300_000_000
        model['fx_to_quote'] = Decimal('1.1')
        model['currency'] = 'USD'
        self.assertAlmostEqual(valuation.evaluate_dcf(model)['values']['base'], Decimal(160) / 3 * Decimal('1.1'))

    def test_negative_early_fcff_signed_nwc_and_multiple_segments(self):
        model = example()
        row = model['scenarios']['base']
        core = row['segments'][0]
        core['years'][0].update(da=2, capex=40, delta_nwc=-3)
        # FCFF=-20; PV explicit=-20/1.1, PV terminal=150/1.1.
        core['terminal']['margin'] = Decimal('.2')
        loss = deepcopy(core)
        loss.update(id='runoff')
        loss['years'][0]['capex'] = 200
        row['segments'].append(loss)
        row['equity_adjustments'].append(dict(id='debt', amount=-5, reason='Gross debt', source='debt note'))
        row['equity_value'] = Decimal(130) / Decimal('1.1') - Decimal(30) / Decimal('1.1') + 5
        flat_scenarios(model, row)
        detail = valuation.evaluate_dcf(model)['details']['base']
        self.assertEqual(detail['segments'][0]['years'][0]['fcff'], -20)
        self.assertLess(detail['segments'][1]['enterprise_value'], 0)
        self.assertEqual(detail['equity_adjustments'], 5)
        self.assertGreater(detail['equity_value'], 0)

    def test_terminal_growth_requires_reinvestment_and_correct_discount_period(self):
        model = example()
        row = model['scenarios']['base']
        segment = row['segments'][0]
        segment['years'].append(dict(year=2, revenue=110, ebit_margin=.2, tax_rate=.25,
                                     da=2, capex=3, delta_nwc=1))
        segment['terminal'].update(growth=.02, roic=.2)
        # Year 2 FCFF = 14.5; NOPAT_(N+1)=16.83; reinvestment=1.683.
        expected_ev = Decimal(15) / Decimal('1.1') + (Decimal('14.5') + Decimal('15.147') / Decimal('.08')) / Decimal('1.21')
        row['equity_value'] = expected_ev + 10
        flat_scenarios(model, row)
        detail = valuation.evaluate_dcf(model)['details']['base']['segments'][0]
        self.assertEqual(detail['terminal_nopat'], Decimal('16.83'))
        self.assertEqual(detail['terminal_reinvestment'], Decimal('1.683'))
        self.assertEqual(detail['terminal_fcff'], Decimal('15.147'))
        self.assertAlmostEqual(detail['enterprise_value'], expected_ev)
        self.assertAlmostEqual(detail['terminal_pv'], Decimal('15.147') / Decimal('.08') / Decimal('1.21'))

    def test_growth_neutral_at_roic_equal_wacc_holding_first_terminal_nopat_fixed(self):
        baseline = valuation.evaluate_dcf(example())['values']['base']
        model = example()
        row = model['scenarios']['base']
        # At ROIC=WACC, TV=terminal-year NOPAT/WACC. Freeze that NOPAT,
        # rather than accidentally changing its base by also growing revenue.
        row['segments'][0]['terminal'].update(growth=.05, margin=Decimal('.2') / Decimal('1.05'))
        flat_scenarios(model, row)
        self.assertAlmostEqual(valuation.evaluate_dcf(model)['values']['base'], baseline)

    def test_declared_equity_is_checked_but_never_used_as_calculation_input(self):
        model = example()
        model['scenarios']['base']['equity_value'] = Decimal('160.004')
        self.assertEqual(valuation.evaluate_dcf(model)['values']['base'], 160)
        model['scenarios']['base']['equity_value'] = Decimal('160.006')
        with self.assertRaisesRegex(ValueError, 'equity_value'):
            valuation.evaluate_dcf(model)

    def test_invalid_financial_inputs_fail_independently_of_claimed_equity(self):
        cases = [
            (('shares',), True, 'shares'), (('shares',), 0, 'shares'),
            (('shares',), 1.5, 'whole shares'), (('fx_to_quote',), 0, 'fx_to_quote'),
            (('fx_to_quote',), float('nan'), 'nonfinite'),
            (('segments', 0, 'discount_rate'), .0, 'discount_rate'),
            (('segments', 0, 'discount_rate'), .02, 'discount_rate.*growth'),
            (('segments', 0, 'terminal', 'growth'), -.01, 'growth'),
            (('segments', 0, 'terminal', 'roic'), .02, 'ROIC'),
            (('segments', 0, 'terminal', 'margin'), -.1, 'terminal.*NOPAT'),
            (('segments', 0, 'terminal', 'tax_rate'), 1, 'terminal.*NOPAT'),
            (('segments', 0, 'years', 0, 'tax_rate'), 1.1, 'tax_rate'),
            (('segments', 0, 'years', 0, 'ebit_margin'), -1.1, 'ebit_margin'),
            (('segments', 0, 'years', 0, 'revenue'), -1, 'revenue'),
            (('segments', 0, 'years', 0, 'da'), -1, 'da'),
            (('segments', 0, 'years', 0, 'capex'), -1, 'capex'),
            (('segments', 0, 'years', 0, 'delta_nwc'), Decimal('Infinity'), 'nonfinite'),
            (('segments', 0, 'years', 0, 'revenue'), '100', 'number'),
            (('segments', 0, 'years', 0, 'year'), True, 'continuous'),
            (('segments', 0, 'source'), ' ', 'source'),
            (('segments', 0, 'assumptions'), '', 'assumptions'),
        ]
        for path, value, error in cases:
            with self.subTest(path=path, value=value):
                model = example()
                row = model if path[0] in ('shares', 'fx_to_quote') else model['scenarios']['base']
                if path[0] == 'segments':
                    row['segments'][0]['terminal']['growth'] = .02
                for key in path[:-1]:
                    row = row[key]
                row[path[-1]] = value
                with self.assertRaisesRegex(ValueError, error):
                    valuation.evaluate_dcf(model)

    def test_strict_fields_order_duplicate_ids_lengths_and_positive_equity(self):
        for mutation, error in [
            (lambda m: m.update(extra=1), 'unexpected'),
            (lambda m: m['scenarios']['base']['segments'][0]['terminal'].update(extra=1), 'unexpected'),
            (lambda m: m['scenarios']['base']['segments'][0]['years'][0].update(year=2), 'continuous'),
            (lambda m: m['scenarios']['base']['segments'].append(deepcopy(m['scenarios']['base']['segments'][0])), 'duplicate segment'),
            (lambda m: m['scenarios']['base']['equity_adjustments'].append(deepcopy(m['scenarios']['base']['equity_adjustments'][0])), 'duplicate equity'),
            (lambda m: m['scenarios']['base']['equity_adjustments'][0].update(source=''), 'source'),
            (lambda m: m['scenarios']['base'].update(segments=[]), 'nonempty'),
            (lambda m: m['scenarios']['base']['segments'][0].update(years=[]), 'nonempty'),
            (lambda m: m['scenarios']['base']['equity_adjustments'][0].update(amount=-1000), 'positive equity'),
        ]:
            with self.subTest(error=error):
                model = example()
                mutation(model)
                with self.assertRaisesRegex(ValueError, error):
                    valuation.evaluate_dcf(model)
        model = example()
        model['scenarios']['low'], model['scenarios']['high'] = model['scenarios']['high'], model['scenarios']['low']
        with self.assertRaisesRegex(ValueError, 'unordered'):
            valuation.evaluate_dcf(model)
        model = example()
        segment = deepcopy(model['scenarios']['base']['segments'][0])
        segment['id'] = 'new'
        segment['years'].append(dict(segment['years'][0], year=2))
        model['scenarios']['base']['segments'].append(segment)
        with self.assertRaisesRegex(ValueError, 'same forecast length'):
            valuation.evaluate_dcf(model)

    def test_reverse_margin_round_trip_cross_currency_does_not_mutate_input(self):
        model = example()
        model['currency'], model['fx_to_quote'] = 'USD', Decimal('1.1')
        original = deepcopy(model)
        # Explicit FCFF remains 15; terminal margin .3 produces TV=225.
        target = (Decimal(240) / Decimal('1.1') + 10) * Decimal('1.1')
        result = valuation.solve_reverse_dcf(model, scenario='base', segment_id='core',
            variable='terminal_margin', target_price=target, lower=0, upper=.5)
        self.assertAlmostEqual(result['parameter'], Decimal('.3'))
        self.assertAlmostEqual(result['modeled_price'], target)
        self.assertLess(abs(result['residual']), Decimal('1e-20'))
        case = dict(scenario='base', segment_id='core', variable='terminal_margin',
                    target_price=target, lower=0, upper=.5, **result)
        self.assertEqual(valuation.validate_reverse_dcf(model, case), result)
        self.assertEqual(model, original)
        for key in ('parameter', 'modeled_price', 'residual'):
            tampered = deepcopy(case)
            tampered[key] += Decimal('.01')
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                valuation.validate_reverse_dcf(model, tampered)

    def test_reverse_handles_negative_boundary_equity_and_rejects_no_root(self):
        model = example()
        row = model['scenarios']['base']
        row['segments'][0]['years'][0]['capex'] = 100
        row['equity_value'] = Decimal(65) / Decimal('1.1') + 10
        flat_scenarios(model, row)
        # Zero-margin boundary equity is negative, but .3 gives a positive root.
        result = valuation.solve_reverse_dcf(model, scenario='base', segment_id='core',
            variable='terminal_margin', target_price=100, lower=0, upper=.5)
        self.assertAlmostEqual(result['parameter'], Decimal(184) / 750)
        kwargs = dict(scenario='base', segment_id='core', variable='terminal_margin',
                      target_price=100, lower=0, upper=.5)
        for replacement, error in [({'target_price': 10000}, 'no root'),
                                    ({'scenario': 'unknown'}, 'scenario'),
                                    ({'segment_id': 'unknown'}, 'segment'),
                                    ({'variable': 'revenue_growth'}, 'terminal_margin'),
                                    ({'lower': -.1}, 'bounds'),
                                    ({'lower': .5}, 'bounds'),
                                    ({'target_price': float('inf')}, 'nonfinite'),
                                    ({'target_price': True}, 'number')]:
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, error):
                valuation.solve_reverse_dcf(model, **(kwargs | replacement))

    def test_decimal_context_does_not_change_results_or_leak(self):
        with localcontext() as context:
            context.prec = 6
            context.rounding = ROUND_UP
            result = valuation.evaluate_dcf(example())
            self.assertEqual(context.prec, 6)
            self.assertEqual(context.rounding, ROUND_UP)
        self.assertEqual(result['values']['base'], 160)

    def test_underflow_is_an_error_instead_of_silent_zero_price(self):
        model = example()
        model['shares'] = Decimal('1e2000000')
        with self.assertRaisesRegex(ValueError, 'calculable precision'):
            valuation.evaluate_dcf(model)

    def test_no_solution_exception_never_masks_invalid_models(self):
        model = example()
        kwargs = dict(scenario='base', segment_id='core', variable='terminal_margin',
                      target_price=10000, lower=0, upper=.5)
        with self.assertRaises(valuation.ReverseNoSolutionError):
            valuation.solve_reverse_dcf(model, **kwargs)
        model['scenarios']['base']['segments'][0]['terminal']['roic'] = 0
        with self.assertRaises(ValueError) as failure:
            valuation.solve_reverse_dcf(model, **kwargs)
        self.assertNotIsInstance(failure.exception, valuation.ReverseNoSolutionError)

    def test_zero_terminal_margin_is_not_an_admissible_final_solution(self):
        model = example()
        row = model['scenarios']['base']
        row['segments'][0]['discount_rate'] = 1
        row['equity_value'] = 25
        flat_scenarios(model, row)
        with self.assertRaises(valuation.ReverseNoSolutionError):
            valuation.solve_reverse_dcf(model, scenario='base', segment_id='core',
                variable='terminal_margin', target_price=Decimal('17.5'), lower=0, upper=.5)


if __name__ == '__main__':
    unittest.main()
