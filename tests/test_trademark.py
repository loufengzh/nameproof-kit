import unittest
from nameproof.trademark import catalog, screening


def record(**changes):
    value = dict(mark='Náme Proof', jurisdiction='US', classes=[9],
                 source_url='https://example.org/official-record/123',
                 observed_at='2025-01-01T00:00:00Z', record_id='123', status='live')
    value.update(changes)
    return value


class TrademarkTests(unittest.TestCase):
    def test_manual_default_all_jurisdictions(self):
        result = screening('Nova', list(catalog()), [9, 42])
        self.assertEqual(len(result['jurisdictions']), 8)
        self.assertFalse(result['legal_clearance'])
        self.assertTrue(all(j['status'] == 'unreviewed' for j in result['jurisdictions']))

    def test_unicode_normalization(self):
        result = screening('NA\u0301ME-PROOF', ['US'], [9], [record()])
        hit = result['jurisdictions'][0]['matches'][0]
        self.assertEqual(hit['match_type'], 'normalized-exact')
        self.assertFalse(hit['evidence_verified'])
        self.assertEqual(hit['source_url'], record()['source_url'])

    def test_non_latin_marks_and_non_latin_no_match(self):
        for mark, country in [('星光', 'CN'), ('Звезда', 'RU')]:
            result = screening(mark, [country], [9], [record(mark=mark, jurisdiction=country)])
            self.assertEqual(result['jurisdictions'][0]['matches'][0]['match_type'], 'normalized-exact')
        with self.assertRaises(ValueError):
            screening('\u0301', ['US'], [9])

    def test_fuzzy(self):
        result = screening('Náme Proov', ['US'], [9], [record()])
        self.assertEqual(result['jurisdictions'][0]['matches'][0]['match_type'], 'fuzzy')

    def test_class_mismatch_and_dead_retained(self):
        result = screening('Náme Proof', ['US'], [42], [record(status='dead')])
        hit = result['jurisdictions'][0]['matches'][0]
        self.assertEqual(hit['class_relation'], 'different-classes-review-required')
        self.assertEqual(hit['status'], 'dead')

    def test_no_match_and_no_coverage_distinct(self):
        result = screening('Zzzzzzzzzzzz', ['US', 'SG'], [9], [record()])
        self.assertEqual(result['jurisdictions'][0]['status'], 'no-match-in-imported-records')
        self.assertEqual(result['jurisdictions'][1]['status'], 'unreviewed')
        self.assertEqual(screening('Nova', ['US'], [9], [])['jurisdictions'][0]['status'], 'unreviewed')

    def test_eu_de_territory(self):
        result = screening('Náme Proof', ['DE'], [9], [record(jurisdiction='EU')])
        self.assertEqual(result['jurisdictions'][0]['records_reviewed'], 1)
        self.assertEqual(result['jurisdictions'][0]['matches'][0]['jurisdiction'], 'EU')

    def test_uk_alias(self):
        self.assertEqual(screening('Nova', ['UK', 'GB'], [9])['countries'], ['GB'])

    def test_validation(self):
        for kwargs in [dict(countries=['ZZ']), dict(classes=[0]), dict(classes=[46]),
                       dict(classes=[True]), dict(classes=[]), dict(name='---'),
                       dict(countries='US')]:
            args = dict(name='Nova', countries=['US'], classes=[9])
            args.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                screening(**args)

    def test_record_validation(self):
        bad = [record(source_url='http://example.org'), record(source_url='https://x:y@example.org'),
               record(observed_at='2025-01-01'), record(observed_at='2999-01-01T00:00:00Z'),
               record(classes=[True]), record(jurisdiction='ZZ'), record(record_id=''),
               record(extra='field')]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                screening('Nova', ['US'], [9], [value])
        with self.assertRaises(ValueError):
            screening('Nova', ['US'], [9], [record(), record()])

    def test_input_not_mutated(self):
        value = record(jurisdiction='UK', classes=[42, 9])
        screening('Náme Proof', ['GB'], [9], [value])
        self.assertEqual(value['jurisdiction'], 'UK')
        self.assertEqual(value['classes'], [42, 9])

if __name__ == '__main__':
    unittest.main()
