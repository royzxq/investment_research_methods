"""Actual frozen Alibaba/Xiaomi regressions, including deliberate failure paths."""
from copy import deepcopy
from decimal import Decimal as D
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r5_replay',HERE/'replay.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def test_original_pack_bytes_dates_and_legacy_r4_immutable():
    out,_=r.build()
    for code,name in [('09988','09988/frozen/inputs/batch/packs/HK-09988.md'),('01810','01810/sources/pack.md')]:
        assert hashlib.sha256((HERE/'frozen'/name).read_bytes()).hexdigest()==out['stocks'][code]['pack_sha256']
    assert out['stocks']['09988']['valuation_date']=='2026-11-09'
    assert out['stocks']['01810']['valuation_date']=='2026-11-08'


def test_no_price_increase_from_equivalent_contract_migration():
    out,models=r.build()
    assert abs(out['stocks']['09988']['equivalent_migration_delta'])<D('1e-20')
    for case in out['stocks']['01810']['expense_cases']:
        assert abs(case['equivalent_migration_delta'])<D('1e-10')
    for m in models.values():
        encoded=json.dumps(m,default=r.json_number)
        r.calc.evaluate_dcf(json.loads(encoded,parse_float=D),input_bridges=True)


def test_ali_tax_cash_correction_and_assumptions_are_separate():
    a=r.build()[0]['stocks']['09988'];s=a['stages']
    assert float(s[0]['conditional_v50'])==pytest.approx(128.4403031846925)
    assert float(s[0]['delta_v50'])==pytest.approx(-1.8671976004832)
    assert float(s[2]['conditional_v50'])==pytest.approx(120.37412306779515)
    assert abs(sum(x['delta_v50'] for x in s)-(s[-1]['conditional_v50']-a['old_r2_conditional_v50']))<D('1e-20')
    reinvest=[x['commerce_reinvestment'] for x in a['pure_tax_sensitivity']]
    assert max(reinvest)-min(reinvest)<D('1e-12')


def test_xiaomi_cost_bridge_does_not_release_unknown_capital_or_discount():
    x=r.build()[0]['stocks']['01810']
    assert float(x['expense_assumption_delta'])==pytest.approx(-1.60303825624)
    assert x['adopted_residual_discounts']=={k:None for k in r.checks.DISCOUNTS}
    _,models=r.build()
    caps=[m['scenarios']['base']['equity_adjustments'] for k,m in models.items() if k.startswith('01810')]
    assert all(c==caps[0] for c in caps)


def test_gap_documents_cannot_become_prices_or_weekly_completion():
    out,_=r.build()
    assert out['production_eligible'] is False
    for code in out['stocks']:
        d=json.loads((HERE/f'{code}-price-map-isolated.json').read_text())
        text=(HERE/f'{code}-audit.md').read_text()
        receipt=r.checks.validate_report(text,d,expected_schema='stock-research-audit/v5',require_lifecycle=True)
        assert receipt['discount_factor'] is None
        assert d['price_map']['v50'] is d['price_map']['p1'] is None
        with pytest.raises(ValueError,match='acceptance'):
            r.checks.validate_report(text,d,require_lifecycle=True,require_acceptance=True)
        a=r.checks.extract_audit(text)
        d['price_map']['v50']={'low':1,'base':2,'high':3}
        with pytest.raises(ValueError,match='V50'):r.checks.validate_audit(a,d)


def test_ali_explicit_cash_tax_does_not_vanish_on_net_loss():
    models=r.build()[1];m=models['09988-tax_no_cross_entity_offset']
    ys=m['scenarios']['base']['segments'][1]['years']
    assert any(y['ebit_margin']<0 and y['cash_tax']>0 for y in ys)
    changed=deepcopy(m)
    for row in changed['scenarios'].values():
        for y in row['segments'][1]['years']:
            if y['ebit_margin']<0:y['cash_tax']=0
    with pytest.raises(ValueError,match='equity_value'):r.calc.evaluate_dcf(changed,input_bridges=True)
