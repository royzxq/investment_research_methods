import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import research_consistency as audit, stock_price_map as prices
from test_two_price_contract import sample
from research_audit_fixture import audit_for


class ControlsSemanticsTests(unittest.TestCase):
    def test_check_cli_requires_lifecycle_baseline_coverage_before_accepting_release(self):
        value=sample();value['research_controls']['add']=dict(status='blocked',refs=['X'])
        old_doc=prices.build_document(value);old=audit_for(old_doc)
        rule=dict(id='X',scope=['add'],status='blocking',action='eligibility',reason='baseline fact',
                  release_conditions=['company review'],lifecycle='persistent')
        old['constraints']=[rule];old['release_all_of']['add']=['X']
        doc=prices.build_document(sample());current=audit_for(doc)
        release=dict(rule,status='clear',clearance=dict(evidence=['reviewed company facts']))
        current['constraints']=[release]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);baseline=root/'baseline.md'
            baseline.write_text(audit.render_report_block(old,old_doc))
            baseline_before=baseline.read_bytes()
            current['baseline']=dict(report_path='baseline.md',sha256=hashlib.sha256(baseline_before).hexdigest(),
                discounts={key:dict(value=entry['value'],quote=entry['reason'])
                           for key,entry in old['discounts'].items()})
            for entry in current['discounts'].values():
                entry['change']['kind']='unchanged'
            price_map=root/'price.json';price_map.write_text(json.dumps(doc))
            report=root/'release.md'
            for covers in (None, [], [audit.constraint_claim_sha256(rule)]):
                with self.subTest(covers=covers):
                    if covers is not None:
                        release['clearance']['covers']=covers
                    # Model an untrusted report rather than pre-validating with render.
                    report.write_text(audit.render_checks(current,doc)+'\n'+audit.START+'\n```json\n'
                                      +json.dumps(current)+'\n```\n'+audit.END)
                    result=subprocess.run([sys.executable,str(Path(audit.__file__)), 'check',
                        '--root',str(root),'--price-map',str(price_map),'--report',str(report),
                        '--require-lifecycle'],capture_output=True,text=True)
                    if covers:
                        self.assertEqual(result.returncode,0,result.stderr)
                        self.assertEqual(json.loads(result.stdout)['status'],'passed')
                    else:
                        self.assertEqual(result.returncode,2,result.stderr)
                        self.assertIn('coverage',result.stderr)
                    self.assertEqual(baseline.read_bytes(),baseline_before)

    def test_explicit_release_coverage_must_match_the_unresolved_baseline_claim(self):
        value=sample();value['research_controls']['add']=dict(status='blocked',refs=['X'])
        old_doc=prices.build_document(value);old=audit_for(old_doc)
        rule=dict(id='X',scope=['add'],status='blocking',action='eligibility',reason='baseline fact',
                  release_conditions=['company review'],lifecycle='persistent')
        old['constraints']=[rule];old['release_all_of']['add']=['X']
        current_doc=prices.build_document(sample());current=audit_for(current_doc)
        release=dict(rule,status='clear',clearance=dict(evidence=['reviewed'],covers=['0'*64]))
        current['constraints']=[release]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'baseline.md').write_text(audit.render_report_block(old,old_doc))
            current['baseline']=dict(report_path='baseline.md')
            with self.assertRaisesRegex(ValueError,'coverage'):
                audit.validate_scoped_controls(current,current_doc,root=root)
            release['clearance']['covers']=[audit.constraint_claim_sha256(rule)]
            audit.validate_scoped_controls(current,current_doc,root=root)
            del release['clearance']['covers']
            with self.assertRaisesRegex(ValueError,'coverage'):
                audit.validate_scoped_controls(current,current_doc,root=root)
            # Dropping the new report's lifecycle cannot downgrade its baseline.
            del release['lifecycle']
            with self.assertRaisesRegex(ValueError,'coverage'):
                audit.validate_scoped_controls(current,current_doc,root=root)

    def test_coverage_omission_is_reserved_for_genuinely_legacy_baseline_rules(self):
        for lifecycle in (None, 'persistent'):
            for status in ('clear', 'not_applicable'):
                with self.subTest(baseline_lifecycle=lifecycle, release_status=status):
                    value=sample();value['research_controls']['add']=dict(status='blocked',refs=['X'])
                    old_doc=prices.build_document(value);old=audit_for(old_doc)
                    rule=dict(id='X',scope=['add'],status='blocking',action='eligibility',
                              reason='baseline fact',release_conditions=['company review'])
                    if lifecycle is not None:
                        rule['lifecycle']=lifecycle
                    old['constraints']=[rule];old['release_all_of']['add']=['X']
                    current_doc=prices.build_document(sample());current=audit_for(current_doc)
                    # Reclassification as runtime still needs proof
                    # that the old persistent research restriction was released.
                    release=dict(rule,status=status,lifecycle='runtime',
                                 clearance=dict(evidence=['reviewed company facts']))
                    current['constraints']=[release]
                    with tempfile.TemporaryDirectory() as folder:
                        root=Path(folder);(root/'baseline.md').write_text(audit.render_report_block(old,old_doc))
                        current['baseline']=dict(report_path='baseline.md')
                        if lifecycle is None:
                            audit.validate_scoped_controls(current,current_doc,root=root)
                        else:
                            with self.assertRaisesRegex(ValueError,'coverage'):
                                audit.validate_scoped_controls(current,current_doc,root=root)
                        for covers in ([], ['0'*64]):
                            release['clearance']['covers']=covers
                            with self.assertRaisesRegex(ValueError,'coverage'):
                                audit.validate_scoped_controls(current,current_doc,root=root)
                        release['clearance']['covers']=[audit.constraint_claim_sha256(rule)]
                        audit.validate_scoped_controls(current,current_doc,root=root)

    def test_runtime_and_observation_do_not_enter_unresolved_research_set(self):
        for lifecycle in ('runtime', 'observation'):
            value = sample()
            value['research_controls']['add'] = dict(status='blocked', refs=['X'])
            doc = prices.build_document(value)
            check = audit_for(doc)
            check['constraints'] = [dict(id='X', scope=['add'], action='eligibility', status='blocking',
                reason='not a persistent research restriction', release_conditions=['price changes'], lifecycle=lifecycle)]
            check['release_all_of']['add'] = ['X']
            with self.assertRaisesRegex(ValueError, 'persistent'):
                audit.validate_audit(check, doc)

    def test_persistent_restriction_and_holding_unknown_are_scoped(self):
        value = sample()
        value['research_controls']['holding'] = dict(status='unknown', refs=['H'])
        doc = prices.build_document(value)
        check = audit_for(doc)
        check['constraints'] = [dict(id='H', scope=['holding'], action='review_holding', status='unknown',
            reason='approved deadline unknown', release_conditions=['official evidence and review'], lifecycle='persistent')]
        check['release_all_of']['holding'] = ['H']
        audit.validate_audit(check, doc)
        self.assertEqual(doc['research_controls']['entry']['status'], 'eligible')

    def test_watch_condition_has_no_unresolved_research_debt(self):
        doc = prices.build_document(sample())
        check = audit_for(doc)
        doc['monitoring'][0].update(id='FUTURE',kind='thesis_invalidation',state='watching')
        self.assertEqual(audit.validate_audit(check,doc)['unresolved_constraints'],dict(entry=[],add=[],holding=[]))

    def test_new_report_requires_lifecycle_but_legacy_v4_remains_readable(self):
        value=sample(); value['research_controls']['add']=dict(status='blocked',refs=['X'])
        doc=prices.build_document(value); check=audit_for(doc)
        rule=dict(id='X',scope=['add'],action='eligibility',status='blocking',
                  reason='required evidence missing',release_conditions=['company review'])
        check['constraints']=[rule]; check['release_all_of']['add']=['X']
        def report():
            return audit.render_checks(check,doc)+'\n'+audit.START+'\n```json\n'+json.dumps(check)+'\n```\n'+audit.END
        audit.validate_report(report(),doc)
        with self.assertRaisesRegex(ValueError,'explicit lifecycle'):
            audit.validate_report(report(),doc,require_lifecycle=True)
        rule['lifecycle']='persistent'
        audit.validate_report(report(),doc,require_lifecycle=True)
