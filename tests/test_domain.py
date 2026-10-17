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
    def test_all_supplied_rdap_names_must_match(self):
        for fields in [
            {'ldhName': 'example.com', 'unicodeName': 'other.com'},
            {'ldhName': 'other.com', 'unicodeName': 'example.com'},
            {},
        ] + [{good: 'example.com', bad: value}
             for good, bad in [('ldhName', 'unicodeName'), ('unicodeName', 'ldhName')]
             for value in ['', None, False, 0, [], {}, ' example.com', 'example.com..', 'xn--example-.com',
                           'example.xn--com-', 'xn--example-.xn--com-', 'xn--.com']]:
            with self.subTest(fields=fields):
                result = check_domain('example.com', True, self.response(200, {'objectClassName': 'domain', **fields}))
                self.assertEqual(result['registration_status'], 'unknown')
                self.assertEqual(result['purchase_status'], 'unknown')
                self.assertEqual(result['reason'], 'rdap_domain_mismatch')

    def test_rdap_equivalent_names(self):
        for query, fields in [
            ('example.com', {'ldhName': 'EXAMPLE.COM.', 'unicodeName': 'Example.Com'}),
            ('example.com', {'unicodeName': 'EXAMPLE.COM.'}),
            ('xn--bcher-kva.com', {'ldhName': 'XN--BCHER-KVA.COM', 'unicodeName': 'bu\u0308cher.com'}),
            ('xn--bcher-kva.com', {'unicodeName': 'bücher.com'}),
            ('xn--fa-hia.com', {'ldhName': 'xn--fa-hia.com', 'unicodeName': 'faß.com'}),
            ('xn--fa-hia.com', {'unicodeName': 'faß.com'}),
            ('xn--3xa.com', {'ldhName': 'xn--3xa.com', 'unicodeName': 'ς.com'}),
            ('xn--bcher-kva.com', {'unicodeName': 'xn--bcher-kva.com'}),
        ]:
            with self.subTest(query=query, fields=fields):
                result = check_domain(query, True, self.response(200, {'objectClassName': 'domain', **fields}))
                self.assertEqual(result['registration_status'], 'registered')

    def test_rdap_does_not_map_distinct_unicode_spellings(self):
        for query, name in [('fass.com', 'faß.com'), ('xn--fa-hia.com', 'fass.com'),
                            ('xn--3xa.com', 'σ.com'), ('xn--bcher-kva.com', 'bucher.com')]:
            with self.subTest(query=query, name=name):
                result = check_domain(query, True, self.response(200, {'objectClassName': 'domain', 'ldhName': query, 'unicodeName': name}))
                self.assertEqual(result['registration_status'], 'unknown')
                self.assertEqual(result['reason'], 'rdap_domain_mismatch')

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
