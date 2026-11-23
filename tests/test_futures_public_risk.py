from datetime import datetime, timedelta
import json
from pathlib import Path
import tempfile
import unittest

from scripts import futures_public_risk as risk


def calendar(endpoint, params, fields):
    first, last = [datetime.strptime(params[key], '%Y%m%d').date() for key in ('start_date', 'end_date')]
    return [dict(exchange=params['exchange'], cal_date=d.strftime('%Y%m%d'), is_open=int(d.weekday() < 5))
            for n in range((last-first).days+1) for d in [first+timedelta(days=n)]]


def tables():
    return {
        'ft_limit': {'20261120': {'down_limit': 2883, 'up_limit': 3249, 'm_ratio': 7}},
        'fut_daily': {'20261119': {'settle': 3066}, '20261120': {'pre_settle': 3066, 'settle': 3083, 'low': 3060, 'high': 3108}},
        'fut_settle': {'20261120': {'settle': 3083, **dict.fromkeys(risk.MARGIN_FIELDS, .07)}},
        'fut_trade_param_dce': {
            '20261119': dict(trade_type='期货', rise_limit=3249, fall_limit=2883, client_buy_posi_quota=93503),
            '20261120': dict(trade_type='期货', rise_limit=3267, fall_limit=2899, client_buy_posi_quota=93199)},
    }


def summarize(t, exchange='DCE'):
    return risk.summarize('M2701.DCE' if exchange == 'DCE' else 'MA2701.ZCE', exchange, '20261120', '20261119', t)


class WeeklyRiskTests(unittest.TestCase):
    def test_rule_transition_keeps_the_affected_session_indeterminate(self):
        from scripts.verify_futures_public_risk import rebar_position_rule
        for previous, closing in ((899999, 900000), (900000, 899999)):
            rule = rebar_position_rule(2, previous, closing)
            self.assertIsNone(rule['fixed_branch_lots'])
            self.assertIsNone(rule['fraction'])
        self.assertEqual(rebar_position_rule(2, 900000, 900000)['fraction'], .1)
        self.assertEqual(rebar_position_rule(1, 899999, 900000)['fixed_branch_lots'], 4500)

    def test_verifier_rejects_modified_summary_before_reading_exchange_sources(self):
        from scripts.verify_futures_public_risk import verify
        code, day, prior = 'M2701.DCE', '20261120', '20261119'
        t = tables()
        row = summarize(t)
        row['up_limit'] += 1
        doc = dict(schema=risk.SCHEMA, codes=[code], rows=[row], raw={code: t},
                   calendars={'DCE': dict(prior=prior, sessions=[day])})
        doc['input_sha256'] = risk.evidence_key(doc)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pack = root/'pack.json'
            pack.write_text(json.dumps(dict(public_risk=doc, trend=[dict(market_inputs=dict(ts_code=code))],
                                            economic_reversion=[])))
            with self.assertRaisesRegex(ValueError, 'differs from raw response'):
                verify(pack, pack, root/'cache', root/'checks.json')
            self.assertFalse((root/'cache').exists())

    def test_cutoff_and_full_holiday(self):
        def holiday(endpoint, params, fields):
            rows = calendar(endpoint, params, fields)
            for item in rows:
                if item['cal_date'] >= '20261116':
                    item['is_open'] = 0
            return rows
        self.assertEqual(risk.window('20261119', 'DCE', calendar)['friday'], '2026-11-13')
        self.assertEqual(risk.window('20261122', 'DCE', holiday)['sessions'][-1], '20261113')
        with self.assertRaises(ValueError):
            risk.window('20261122', 'DCE', lambda *args: calendar(*args)[:-1])

    def test_dce_close_and_session_are_separate(self):
        t = tables()
        row = summarize(t)
        self.assertEqual((row['position_source_date'], row['session_position_limit_lots'], row['closing_table_position_limit_lots']),
                         ('20261119', 93503, 93199))
        self.assertEqual(row['settlement_margin_pct']['long_margin_rate'], 7.0)
        for field in ('rise_limit', 'fall_limit', 'trade_type'):
            t = tables()
            t['fut_trade_param_dce']['20261119'][field] = 0
            self.assertIsNone(summarize(t)['session_position_limit_lots'])
        t = tables()
        t['fut_daily']['20261119'] = {}
        self.assertIsNone(summarize(t)['session_position_limit_lots'])

    def test_czce_percent_and_distinct_open_cap(self):
        t = tables()
        t['fut_settle']['20261120'].update(dict.fromkeys(risk.MARGIN_FIELDS, 9))
        t['fut_trade_param'] = {'20261120': dict(
            position_limit='85272', trade_limit='25000', pre_settle_price='3066')}
        row = summarize(t, 'CZCE')
        self.assertEqual((row['session_position_limit_lots'], row['session_open_limit_lots']), (85272, 25000))
        self.assertEqual(row['settlement_margin_pct']['short_margin_rate'], 9.0)
        t['fut_settle']['20261120']['long_margin_rate'] = .07
        self.assertIsNone(summarize(t, 'CZCE')['settlement_margin_pct']['long_margin_rate'])
        t['fut_trade_param']['20261120']['pre_settle_price'] = None
        self.assertIsNone(summarize(t, 'CZCE')['session_position_limit_lots'])

    def test_no_settlement_no_margin_and_conflicting_board(self):
        t = tables()
        del t['fut_settle']['20261120']['settle'], t['fut_daily']['20261120']['settle']
        t['fut_daily']['20261120']['low'] = 2800
        row = summarize(t)
        self.assertTrue(all(v is None for v in row['settlement_margin_pct'].values()))
        self.assertIsNone(row['down_limit'])
        self.assertIsNone(row['session_position_limit_lots'])

    def test_identity_and_gaps(self):
        row = dict(ts_code='M2701.DCE', trade_date='20261120', exchange='DCE')
        for bad in ([row, row], [dict(row, exchange='CZCE')], [dict(row, ts_code='M2705.DCE')], [dict(row, trade_date='20261123')]):
            with self.assertRaises(ValueError):
                risk.dated(bad, 'M2701.DCE', 'DCE', ['20261120'])

        def limited(endpoint, params, fields):
            if endpoint == 'trade_cal':
                return calendar(endpoint, params, fields)
            raise PermissionError
        with tempfile.TemporaryDirectory() as root:
            doc = risk.collect('20261123', '20261122', ['M2701.DCE'], limited, Path(root))
            self.assertEqual(len(doc['rows']), 5)
            self.assertTrue(doc['issues'])
            self.assertIsNone(doc['final_lots'])
            self.assertTrue(all(r['up_limit'] is None for r in doc['rows']))

    def test_exchange_attachment_scoped_to_input_and_availability(self):
        doc = dict(calendars={'DCE': {'friday': '2026-11-20'}}, input_sha256='source', issues=[],
                   observed_at='2026-11-23T09:05:00+08:00', as_of_date='20261123',
                   rows=[dict(ts_code='M2701.DCE', trade_date='20261120')])
        with tempfile.TemporaryDirectory() as root:
            path = risk.week_directory('2026-11-20', Path(root))/'evidence'/risk.CHECK_FILE
            path.parent.mkdir(parents=True)
            check = dict(input_sha256='other', observed_at='2026-11-23T08:00:00+08:00',
                         contracts={'M2701.DCE': {'20261120': {'status': 'source checked', 'board': 'provider crosscheck'}}})
            path.write_text(json.dumps(check))
            risk.attach_checks(doc, Path(root))
            self.assertNotIn('exchange_checks', doc)
            check['input_sha256'] = 'source'
            path.write_text(json.dumps(check))
            doc['as_of_date'] = '20261122'
            risk.attach_checks(doc, Path(root))
            self.assertNotIn('exchange_checks', doc)
            doc['as_of_date'] = '20261123'
            risk.attach_checks(doc, Path(root))
            self.assertEqual(doc['rows'][0]['board_check'], 'provider crosscheck')


if __name__ == '__main__':
    unittest.main()
