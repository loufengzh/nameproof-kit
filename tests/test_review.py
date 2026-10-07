"""Independent review regressions; no network requests or provider accounts."""
import io
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from nameproof.domain import check_domain, normalize_domain, apply_registrar_receipt
from nameproof.mcp import handle, serve
from nameproof.naming import propose
from nameproof.cli import report, markdown

BOOT = {'services': [[['com'], ['https://rdap.example.org/']]]}


class DomainEvidenceReviewTests(unittest.TestCase):
    def check(self, status, record):
        calls = []
        def fetch(url):
            calls.append(url)
            return (200, BOOT) if len(calls) == 1 else (status, record)
        result = check_domain('brand.com', live=True, fetch=fetch)
        self.assertEqual(len(calls), 2)
        return result

    def test_offline_does_not_fetch(self):
        def fetch(url):
            self.fail('offline lookup must not use network')
        self.assertEqual(check_domain('brand.com', fetch=fetch)['purchase_status'], 'unknown')

    def test_rdap_absence_never_means_available(self):
        result = self.check(404, {'errorCode': 404})
        self.assertEqual(result['registration_status'], 'no_record')
        self.assertEqual(result['purchase_status'], 'unknown')

    def test_unstructured_404_is_unknown(self):
        self.assertEqual(self.check(404, {})['registration_status'], 'unknown')

    def test_wrong_domain_record_is_unknown(self):
        self.assertEqual(self.check(200, {'objectClassName': 'domain', 'ldhName': 'other.com'})['registration_status'], 'unknown')

    def test_rate_limit_is_unknown(self):
        self.assertEqual(self.check(429, {'errorCode': 429})['purchase_status'], 'unknown')

    def test_idna_deviation_never_silently_queries_another_domain(self):
        # IDNA2008 sharp-s A-label is xn--fa-hia.de; IDNA2003 changes it to fass.de.
        # Explicit rejection also satisfies the dependency-free fail-closed contract.
        try:
            value = normalize_domain('faß.de')
        except ValueError:
            return
        self.assertEqual(value, 'xn--fa-hia.de')

    def test_invalid_receipt_url_type_is_validation_error(self):
        receipt = dict(domain='brand.com', registrar='Example', status='available',
                       source_url=123, observed_at='2026-01-01T00:00:00Z')
        with self.assertRaises(ValueError):
            apply_registrar_receipt(check_domain('brand.com'), receipt)

    def test_conflicting_registrar_evidence_is_visible(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        receipt = dict(domain='brand.com', registrar='Example', status='available',
                       source_url='https://example.org/check', observed_at=now.isoformat())
        observation = self.check(200, {'objectClassName': 'domain', 'ldhName': 'brand.com'})
        result = apply_registrar_receipt(observation, receipt, now=now)
        self.assertEqual(result['purchase_status'], 'conflicting_evidence')
        self.assertEqual(result['receipt_verification'], 'user_supplied_not_independently_authenticated')


class NamingAndReportReviewTests(unittest.TestCase):
    def test_preserve_accents_in_domain_suggestions(self):
        result = propose({'idea':'a cafe'}, [{'name':'Café','rationale':'Coffee'}])
        self.assertIn('café.com', result['candidates'][0]['domain_labels'])

    def test_shared_brief_rejects_invalid_classes_and_jurisdictions(self):
        for fields in ({'nice_classes':['foo']}, {'nice_classes':[True]},
                       {'nice_classes':[]}, {'countries':['ZZ']}, {'countries':[]}):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                propose(dict(idea='bakery', **fields))

    def test_markdown_preserves_evidence_provenance(self):
        record = dict(mark='Nova', jurisdiction='US', classes=[9],
                      source_url='https://example.org/record/123',
                      observed_at='2025-01-01T00:00:00Z', record_id='123', status='live')
        result = report({'idea':'software'}, [{'name':'Nova','rationale':'A bright start'}], [record])
        rendered = markdown(result)
        self.assertIn(record['source_url'], rendered)
        self.assertIn(record['observed_at'], rendered)


class ProtocolAndSkillReviewTests(unittest.TestCase):
    def test_malformed_json_rpc_id_rejected(self):
        for invalid_id in ({}, [], True):
            with self.subTest(id=invalid_id):
                result = handle({'jsonrpc':'2.0', 'id':invalid_id, 'method':'ping'})
                self.assertEqual(result.get('error', {}).get('code'), -32600)

    def test_invalid_tool_boolean_returns_error(self):
        result = handle({'jsonrpc':'2.0', 'id':1, 'method':'tools/call',
                         'params':{'name':'check_domain','arguments':{'domain':'brand.com','live':'false'}}})
        self.assertTrue(result['result']['isError'])

    def test_invalid_input_does_not_kill_stdio(self):
        src = io.StringIO('{bad json}\n' + json.dumps({'jsonrpc':'2.0','id':2,'method':'ping'}) + '\n')
        dst = io.StringIO()
        self.assertEqual(serve(src, dst), 0)
        responses = [json.loads(line) for line in dst.getvalue().splitlines()]
        self.assertEqual(responses[0]['error']['code'], -32700)
        self.assertEqual(responses[1]['result'], {})

    def test_documented_skill_commands_execute(self):
        commands = [
            ['--help'], ['domain', 'brand.com'],
            ['screen', '--name', 'Nova', '--countries', 'US,EU,VN', '--classes', '9,42'],
            ['propose', '--brief', 'examples/brief.json'],
            ['report', '--brief', 'examples/brief.json', '--candidates', 'examples/candidates.json'],
            ['logo-brief', '--name', 'Nova', '--brief', 'examples/brief.json'],
        ]
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, '-m', 'nameproof', *command],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                if command != ['--help']:
                    json.loads(result.stdout)

if __name__ == '__main__':
    unittest.main()
