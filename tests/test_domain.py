import unittest
from datetime import datetime, timezone, timedelta
from nameproof.domain import normalize_domain, check_domain, apply_registrar_receipt, rdap_url

BOOT = {'services': [[['com'], ['https://rdap.verisign.com/com/v1/']]]}
class DomainTests(unittest.TestCase):
    def response(self, code, value):
        return lambda url: (200, BOOT) if url.endswith('dns.json') else (code, value)
    def test_normalization(self):
        self.assertEqual(normalize_domain('EXAMPLE.COM.'), 'example.com')
        self.assertEqual(normalize_domain('bücher.de'), 'xn--bcher-kva.de')
    def test_invalid(self):
        for value in ['localhost','x.local','https://x.com','user@x.com','x.com/a','127.0.0.1','x..com','-x.com','x.com:443',' x.com',None]:
            with self.subTest(value=value), self.assertRaises(ValueError): normalize_domain(value)
    def test_offline_never_calls_network(self):
        result = check_domain('example.com', fetch=lambda _: self.fail('network'))
        self.assertEqual(result['reason'], 'not_checked')
    def test_registered(self):
        result = check_domain('example.com', True, self.response(200, {'objectClassName':'domain','ldhName':'EXAMPLE.COM'}))
        self.assertEqual(result['registration_status'], 'registered')
    def test_no_record_not_available(self):
        result = check_domain('example.com', True, self.response(404, {'errorCode':404}))
        self.assertEqual(result['registration_status'],'no_record')
        self.assertEqual(result['purchase_status'],'unknown')
    def test_failures_unknown(self):
        for code, obj in [(404, {}),(200, {}),(429, {}),(200, {'objectClassName':'domain','ldhName':'other.com'})]:
            with self.subTest(code=code,obj=obj):
                self.assertEqual(check_domain('example.com', True, self.response(code,obj))['registration_status'],'unknown')
    def test_unregistered_suffix(self):
        self.assertIsNone(rdap_url('thing.zzzzz',BOOT))
    def receipt(self, status='available'):
        return {'domain':'example.com','registrar':'Example registrar','status':status,'source_url':'https://example.com/quote','observed_at':datetime.now(timezone.utc).isoformat()}
    def test_receipt_provenance(self):
        result=apply_registrar_receipt(check_domain('example.com'),self.receipt())
        self.assertEqual(result['purchase_status'],'registrar_reported_available')
        self.assertIn('not_independently',result['receipt_verification'])
    def test_stale_quote(self):
        receipt=self.receipt(); receipt['observed_at']=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()
        self.assertEqual(apply_registrar_receipt(check_domain('example.com'),receipt)['purchase_status'],'unknown')
    def test_registered_quote_conflict(self):
        observation=check_domain('example.com',True,self.response(200,{'objectClassName':'domain','ldhName':'example.com'}))
        self.assertEqual(apply_registrar_receipt(observation,self.receipt())['purchase_status'],'conflicting_evidence')
    def test_reserved_and_premium(self):
        for status in ['reserved','premium','unavailable']:
            self.assertEqual(apply_registrar_receipt(check_domain('example.com'),self.receipt(status))['purchase_status'],'registrar_reported_'+status)
    def test_receipt_mismatch(self):
        receipt=self.receipt(); receipt['domain']='other.com'
        with self.assertRaises(ValueError): apply_registrar_receipt(check_domain('example.com'),receipt)
