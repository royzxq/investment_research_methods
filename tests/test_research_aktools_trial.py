import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from scripts.research_aktools_trial import run


class AKToolsTrialFailureTests(unittest.TestCase):
    def probe(self, mode):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        fake = root/'fake-mcp'
        fake.write_text(f'''#!{sys.executable}
import json,os,sys
from pathlib import Path
Path('server.pid').write_text(str(os.getpid()))
for line in sys.stdin:
 r=json.loads(line); method=r['method']
 with Path('methods.jsonl').open('a') as f:f.write(json.dumps(method)+'\\n')
 if 'id' not in r:continue
 if method=='initialize':
  response={{'error':{{'code':-32600,'message':'initialization rejected'}}}} if {mode!r}=='initialize' else {{'result':{{'protocolVersion':'2025-03-26'}}}}
 elif method=='tools/list':
  names=['search_interfaces','describe_interface']+([] if {mode!r}=='discovery' else ['get_data'])
  response={{'result':{{'tools':[{{'name':n}} for n in names]}}}}
 else:response={{'result':{{'isError':True,'content':[{{'type':'text','text':'upstream error'}}]}}}}
 print(json.dumps(dict(jsonrpc='2.0',id=r['id'],**response)),flush=True)
''')
        fake.chmod(0o700)
        output = root/'output'
        manifest = {'calls': [dict(name='get_data', arguments={'name': 'example'})]}
        return fake, manifest, output

    def test_rejected_initialize_stops_before_discovery_and_reaps_server(self):
        fake, manifest, output = self.probe('initialize')
        with self.assertRaisesRegex(RuntimeError, 'invalid result envelope'):
            run(fake, manifest, output)
        self.assertEqual((output/'methods.jsonl').read_text().strip(), '"initialize"')
        with self.assertRaises(ProcessLookupError):
            os.kill(int((output/'server.pid').read_text()), 0)

    def test_incomplete_tool_discovery_cannot_be_counted_as_ready(self):
        fake, manifest, output = self.probe('discovery')
        with self.assertRaisesRegex(RuntimeError, 'expected AKTools capabilities'):
            run(fake, manifest, output)
        self.assertNotIn('tools/call', (output/'methods.jsonl').read_text())

    def test_tool_error_preserves_evidence_and_cannot_pass(self):
        fake, manifest, output = self.probe('call')
        run(fake, manifest, output)
        self.assertFalse(json.loads((output/'call-00.json').read_text())['ok'])
        self.assertEqual(json.loads((output/'manifest.json').read_text()), manifest)
        self.assertEqual(len(json.loads((output/'driver.json').read_text())['driver_sha256']), 64)


if __name__ == '__main__':
    unittest.main()
