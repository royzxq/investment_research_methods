from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts import quarterly_peers as q


def batch(period='20260930', observed='20261122'):
    rows = {key: [] for key in q.FIELDS}
    for i, code in enumerate(['600001.SH', '600002.SH', '600003.SH', '600004.SH']):
        for endpoint, fields in q.STATEMENTS.items():
            row = dict(ts_code=code, f_ann_date='20261025', ann_date='20261025', end_date=period,
                       report_type='1', comp_type='1' if i < 3 else '2')
            row.update({key: (i+1)*1e8 for key in fields})
            rows[endpoint].append(row)
        rows['disclosure_date'].append(dict(ts_code=code, actual_date='20261025', end_date=period))
        rows['index_member_all'].append(dict(ts_code=code, l3_code='X', name=code,
            l3_name='示例行业', in_date='20250101', out_date=None, is_new='Y'))
    return dict(schema=q.SCHEMA, observed=observed, period=period, rows=rows)


class PeerTests(unittest.TestCase):
    def test_ex_self_missing_fields_and_separate_company_types(self):
        doc = batch()
        for row, profit in zip(doc['rows']['income_vip'], [90e6, 20e6, 120e6, 400e6]):
            row['n_income_attr_p'] = profit
        doc['rows']['cashflow_vip'][1]['n_cashflow_act'] = None
        doc['rows']['income_vip'].append(dict(doc['rows']['income_vip'][0], report_type='6', total_revenue=7))
        doc['rows']['income_vip'].append(dict(doc['rows']['income_vip'][0], f_ann_date='20261201', total_revenue=9))
        doc['rows']['fina_mainbz_vip'] = [dict(ts_code='600001.SH',bz_item='A',bz_sales=20,curr_type='CNY')]
        with TemporaryDirectory() as tmp:
            weekly = Path(tmp)/'research/investment/weekly'
            path = q.path_for(weekly, doc['observed'], doc['period'])
            q.publish(path, doc)
            with self.assertRaises(FileExistsError):
                q.publish(path, doc)
            self.assertIn('gap', q.for_pack('600001.SH', '20261121', weekly))
            s = q.for_pack('600001.SH', '20261122', weekly)
            self.assertEqual(s['amounts']['total_revenue'], 1e8)
            self.assertIsNone(s['report_currency'])
            self.assertEqual(s['metrics']['parent_margin']['own'], 90)
            self.assertEqual(s['metrics']['parent_margin']['peer_median'], 25)
            self.assertEqual(s['metrics']['operating_cash_margin']['n'], 1)
            self.assertEqual(s['group_size'], 3)
            self.assertIn('A 20.00 CNY', q.render(s))
            self.assertIn('gap', q.for_pack('999999.SH', '20261122', weekly))
            self.assertNotIn('operating_cash_margin', q.for_pack('600004.SH','20261122',weekly)['metrics'])
            check = path.with_name('investment-2026-11-22-peer-validation-20260930.json')
            original = dict(source_unit='人民币百万元', report='https://example.com/filing.pdf', pages='2',
                            reported_amounts={k:str(v/1e6) for k,v in s['amounts'].items()})
            inspected = dict(period=s['period'], observed=s['observed'], sha256=s['sha256'],
                             samples={s['code']:original})
            check.write_text(json.dumps(inspected))
            verified = q.for_pack(s['code'], '20261122', weekly)
            self.assertIn('亿元人民币', q.render(verified))
            self.assertEqual(verified['report_currency'], 'CNY')
            original['reported_amounts']['total_revenue'] = '2'
            check.write_text(json.dumps(inspected))
            self.assertIsNone(q.for_pack(s['code'], '20261122', weekly)['report_currency'])
            damaged = q.path_for(weekly, '20261123', doc['period'])
            damaged.parent.mkdir(parents=True)
            damaged.write_bytes(b'incomplete')
            self.assertIn('读取失败', q.for_pack('600001.SH', '20261123', weekly)['gap'])

    def test_disclosure_missing_and_same_day_conflicting_fields(self):
        doc = batch()
        rows = doc['rows']
        rows['disclosure_date'][1]['actual_date'] = None
        rows['income_vip'].append(dict(rows['income_vip'][0], n_income_attr_p=-42))
        rows['balancesheet_vip'].append(dict(rows['balancesheet_vip'][2], comp_type='4'))
        for endpoint in q.STATEMENTS:
            rows[endpoint][3]['comp_type'] = None
        stocks = q.companies(doc)
        self.assertIsNone(stocks['600001.SH']['n_income_attr_p'])
        self.assertEqual(stocks['600001.SH']['total_revenue'], 1e8)
        self.assertNotIn('total_revenue', stocks['600002.SH'])
        self.assertIsNone(stocks['600003.SH']['comp_type'])
        self.assertIsNone(stocks['600004.SH']['comp_type'])

    def test_pagination_continues_until_empty_and_rejects_repeated_page(self):
        doc = batch()
        def call(endpoint, params, fields):
            source = doc['rows'][endpoint]
            for r in source:
                if 'end_date' in r:
                    self.assertEqual(r['end_date'], '20260930')
            return source[params['offset']:params['offset'] + 2]
        result = q.fetch_snapshot('20261122','20260930', call)
        self.assertEqual(result['requests']['income_vip']['page_sizes'], [2,2,0])
        with self.assertRaisesRegex(ValueError,'repeated page'):
            q.fetch_snapshot('20261122','20260930', lambda endpoint, params, fields: doc['rows'][endpoint][:1])

    def test_not_yet_disclosed_at_quarter_rollover(self):
        doc = batch()
        with TemporaryDirectory() as tmp:
            weekly = Path(tmp)/'research/investment/weekly'
            q.publish(q.path_for(weekly,doc['observed'],doc['period']), doc)
            new = deepcopy(doc)
            new.update(period='20261231', observed='20270115', rows={k:[] for k in q.FIELDS})
            new['rows']['disclosure_date'].append(dict(ts_code='600001.SH', actual_date='20270114'))
            q.publish(q.path_for(weekly,new['observed'],new['period']),new)
            s = q.for_pack('600001.SH','20270115',weekly)
            self.assertEqual(s['period'],'20260930')
            self.assertTrue(any('20261231' in x for x in s['gaps']))

    def test_optional_product_failure_keeps_complete_statements_and_records_gap(self):
        source = batch()['rows']
        def call(endpoint, params, fields):
            if endpoint == 'fina_mainbz_vip':
                if params['offset']:
                    raise PermissionError
                return [dict(ts_code='600001.SH', end_date='20260930', bz_item='A', bz_sales=1, curr_type='CNY')]
            return [] if params['offset'] else source[endpoint]
        frozen = q.fetch_snapshot('20261122', '20260930', call)
        stock = q.companies(frozen)['600001.SH']
        self.assertEqual(stock['total_revenue'], 1e8)
        self.assertFalse(frozen['rows']['fina_mainbz_vip'])
        self.assertTrue(any('覆盖未知' in gap for gap in stock['gaps']))
