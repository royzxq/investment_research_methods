from datetime import datetime, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import weekly_etf_shares as e

DAYS = ['20261113','20261116','20261117']
CODE = '510300.SH'


def tables():
    data = {k:[] for k in e.FIELDS}
    for i, day in enumerate(DAYS):
        data['fund_share'].append(dict(ts_code=CODE, trade_date=day, fd_share=[10000,20000,15000][i]))
        data['fund_adj'].append(dict(ts_code=CODE, trade_date=day, adj_factor=1))
        data['fund_nav'].append(dict(ts_code=CODE, nav_date=day, ann_date=day, unit_nav=2+i))
        data['fund_daily'].append(dict(ts_code=CODE, trade_date=day, close=2+i, amount=100000))
    return data


class WeeklySharesTests(unittest.TestCase):
    def test_weekly_identity_units_and_no_baseline_volume(self):
        s = e.summarize(CODE, DAYS, DAYS[-1], tables())
        self.assertEqual(s['delta_yi_shares'],.5)
        self.assertEqual(s['share_change_at_nav_yi_cny'],1)
        self.assertEqual(s['nav_effect_yi_cny'],3)
        self.assertEqual(s['weekly_turnover_yi_cny'],2)
        self.assertEqual(s['price_change_pct'],100)

    def test_split_missing_session_and_conflicting_nav(self):
        for case in ('split','missing','conflict'):
            raw = tables()
            if case == 'split':
                raw['fund_adj'][1]['adj_factor'] = 2
            elif case == 'missing':
                raw['fund_share'].pop(1)
            else:
                raw['fund_nav'].append(dict(raw['fund_nav'][1], unit_nav=9))
            s = e.summarize(CODE, DAYS, DAYS[-1], raw)
            self.assertIsNone(s['share_change_at_nav_yi_cny'])
            self.assertEqual(s['delta_yi_shares'],.5)

    def test_future_revision_not_visible_and_foreign_code_invalid(self):
        raw = tables()
        original = raw['fund_nav'][1].pop('ann_date')
        self.assertIsNone(e.summarize(CODE, DAYS, DAYS[-1], raw)['unit_nav_cny'][1])
        raw['fund_nav'][1]['ann_date'] = original
        raw['fund_nav'].append(dict(raw['fund_nav'][1], ann_date='20261118', unit_nav=9))
        self.assertEqual(e.summarize(CODE,DAYS,DAYS[-1],raw)['share_change_at_nav_yi_cny'],1)
        raw['fund_daily'][0]['ts_code'] = 'OTHER'
        with self.assertRaises(ValueError):
            e.summarize(CODE,DAYS,DAYS[-1],raw)

    def test_partial_fund_is_retryable_and_historical_reads_respect_observation_week(self):
        raw = tables()
        raw['fund_nav'].pop(1)
        summary = e.summarize(CODE, DAYS, '20261122', raw)
        doc = dict(schema=e.SCHEMA, cutoff='20261122', sessions=DAYS,
                   funds={CODE: dict(name='sample', inputs=raw, summary=summary)})
        self.assertEqual(e.missing_observations(doc), {CODE: ['20261116 unit_nav_cny']})
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/'2026-11-22/evidence/investment-2026-11-22-etf-shares.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(doc))
            self.assertIsNone(e.snapshot_section('20261121', root))
            self.assertIn('sample', e.snapshot_section('20261122', root, market_cutoff='20261121'))
            self.assertIn('sample', e.snapshot_section('20261125', root))
            self.assertIsNone(e.snapshot_section('20261129', root))

    def test_snapshot_can_fetch_this_morning_with_last_completed_market_day(self):
        from scripts import etf_data
        observed = datetime.now(e.ZoneInfo('Asia/Shanghai')).date()
        today = observed.strftime('%Y%m%d')
        prior = (observed - timedelta(days=1)).strftime('%Y%m%d')
        doc = dict(funds={})
        with patch.object(etf_data, 'AS_OF', today), patch.object(etf_data, 'CUTOFF', prior), \
                patch.object(e, 'snapshot_section', return_value=None), \
                patch.object(e, 'collect', return_value=doc) as collect, patch.object(e, 'render', return_value='本周份额'):
            self.assertIn('本周份额', etf_data.section_weekly_shares())
            self.assertEqual(collect.call_args.args[0], today)
            self.assertEqual(collect.call_args.kwargs['market_cutoff'], prior)

    def test_holiday_and_midweek_anchor(self):
        def calendar(endpoint, params, fields):
            d = datetime.strptime(params['start_date'], '%Y%m%d').date()
            end = datetime.strptime(params['end_date'], '%Y%m%d').date()
            rows = []
            while d <= end:
                day = d.strftime('%Y%m%d')
                rows.append(dict(exchange='SSE', cal_date=day, is_open=int(d.weekday()<5 and day!='20261120')))
                d += timedelta(days=1)
            return rows
        self.assertEqual(e.calendar_window('20261122',calendar), ['20261113','20261116','20261117','20261118','20261119'])
        self.assertEqual(e.calendar_window('20261119',calendar)[-1],'20261113')
        with self.assertRaises(ValueError):
            e.calendar_window('20261122',lambda *args: calendar(*args)[1:])
