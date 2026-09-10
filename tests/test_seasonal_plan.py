"""Synthetic calendars/quotes only; these fixtures are not historical performance."""
from datetime import date, timedelta
from pathlib import Path
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.seasonal_plan import boundaries, calculate, calendar


def synthetic_calendar(year):
    days = [date(year, 1, 1) + timedelta(days=i) for i in range(365)]
    # Deliberately omit one weekday to exercise exchange holidays, not weekday subtraction.
    return [d.isoformat() for d in days if d.weekday() < 5 and d != date(year, 10, 1)]


def fixture():
    days = synthetic_calendar(2026)
    b = boundaries("CF-autumn", 2026, calendar(days))
    entry = date(2026, 9, 11)
    history = []
    for year, end in zip((2023, 2024, 2025), (110, 95, 125)):
        hdays = calendar(synthetic_calendar(year))
        e = next(d for d in hdays if d >= entry.replace(year=year))
        x = max(d for d in hdays if d <= b["planned_exit"].replace(year=year))
        history.append(dict(year=year, contract=f"CF{(year+1)%100:02d}01", trading_dates=[d.isoformat() for d in hdays],
                            entry_date=e.isoformat(), exit_date=x.isoformat(), entry_settle=100, exit_settle=end,
                            listed_on=f"{year}-01-01", last_trade_date=f"{year+1}-01-15",
                            price_basis="settle", source="synthetic fixture"))
    return dict(window_id="CF-autumn", as_of_date="2026-09-10", trading_dates=days,
                plan=dict(contract="CF2701", entry_date=entry.isoformat(), contract_latest_exit="2026-12-17",
                          ma20=15001, pre_window_low5=14500, atr20=300, tick=5, history=history))


class SeasonalPlanTests(unittest.TestCase):
    def test_remaining_interval_and_signed_mean_convert_to_tick_prices(self):
        result = calculate(fixture())
        self.assertAlmostEqual(result["mean_return"], .1)  # losses included: (10%-5%+25%)/3
        self.assertEqual((result["entry"], result["stop"], result["tp1"]), (15005, 14555, 16055))
        self.assertEqual(result["execution_permission"], "not_evaluated")
        self.assertIn("net_R_and_costs", result["pending_checks"])

    def test_outside_window_short_circuits_without_history_or_account(self):
        data = dict(window_id="SR-summer", as_of_date="2026-03-02", trading_dates=synthetic_calendar(2026))
        self.assertEqual(calculate(data)["screening"], "not_triggered")
        self.assertNotIn("entry", calculate(data))

    def test_pre20_is_preparation_not_entry_permission(self):
        data = fixture()
        data["as_of_date"] = "2026-08-20"
        data["plan"]["entry_date"] = "2026-08-21"
        self.assertEqual(calculate(data)["plan_result"], "fails_time_window")

    def test_exit_buffer_and_earlier_contract_boundary(self):
        data = fixture()
        data["plan"]["contract_latest_exit"] = "2026-09-11"
        self.assertEqual(calculate(data)["plan_result"], "fails_time_window")
        data = fixture()
        data["plan"]["entry_date"] = boundaries("CF-autumn", 2026, calendar(data["trading_dates"]))["planned_exit"].isoformat()
        self.assertEqual(calculate(data)["plan_result"], "fails_time_window")

    def test_no_cherry_picking_years_or_whole_window_returns_or_main_splicing(self):
        for change in (dict(year=2022), dict(entry_date="2023-09-01"), dict(contract="CF2405"),
                       dict(price_basis="close"), dict(listed_on="2023-12-01")):
            data = fixture(); data["plan"]["history"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                calculate(data)
        data = fixture(); data["plan"]["history"].pop()
        with self.assertRaises(ValueError):
            calculate(data)

    def test_negative_returns_are_a_known_plan_failure(self):
        data = fixture()
        for h in data["plan"]["history"]: h["exit_settle"] = 90
        self.assertEqual(calculate(data)["plan_result"], "fails_nonpositive_target")

    def test_reject_bad_calendar_tick_and_nonfinite_inputs(self):
        data = fixture(); data["trading_dates"].append(data["trading_dates"][-1])
        with self.assertRaises(ValueError): calculate(data)
        for value in (float("nan"), float("inf"), True, -1):
            data = fixture(); data["plan"]["atr20"] = value
            with self.subTest(value=value), self.assertRaises(ValueError): calculate(data)
        data = fixture(); data["plan"]["tick"] = 1
        with self.assertRaises(ValueError): calculate(data)


if __name__ == "__main__": unittest.main()
