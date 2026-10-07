import io
import json
import subprocess
import sys
import unittest
from nameproof.cli import report
from nameproof.mcp import handle, serve
class IntegrationTests(unittest.TestCase):
    def test_cli_report(self):
        proc=subprocess.run([sys.executable,'-m','nameproof','report','--brief','examples/brief.json','--candidates','examples/candidates.json'],capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        result=json.loads(proc.stdout)
        self.assertEqual(len(result['candidates']),3)
        self.assertFalse(result['candidates'][0]['trademark_screen']['legal_clearance'])
        self.assertEqual(result['candidates'][0]['domains'][0]['purchase_status'],'unknown')
    def test_cli_input_error(self):
        proc=subprocess.run([sys.executable,'-m','nameproof','domain','http://local'],capture_output=True,text=True)
        self.assertEqual(proc.returncode,2)
        self.assertNotIn('Traceback',proc.stderr)
    def test_mcp_handshake_and_tools(self):
        for method in ['initialize','tools/list','ping']:
            self.assertIn('result',handle({'jsonrpc':'2.0','id':1,'method':method}))
    def test_notification_silent(self):
        self.assertIsNone(handle({'jsonrpc':'2.0','method':'notifications/initialized'}))
    def test_mcp_offline_domain(self):
        result=handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'check_domain','arguments':{'domain':'example.com'}}})['result']
        self.assertFalse(result['isError'])
        self.assertEqual(json.loads(result['content'][0]['text'])['reason'],'not_checked')
    def test_mcp_bad_live_type(self):
        result=handle({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'check_domain','arguments':{'domain':'example.com','live':'false'}}})['result']
        self.assertTrue(result['isError'])
    def test_stdio_bad_json_continues(self):
        out=io.StringIO()
        serve(io.StringIO('bad\n{"jsonrpc":"2.0","id":2,"method":"ping"}\n'),out)
        lines=out.getvalue().splitlines()
        self.assertEqual(json.loads(lines[0])['error']['code'],-32700)
        self.assertEqual(json.loads(lines[1])['result'],{})
