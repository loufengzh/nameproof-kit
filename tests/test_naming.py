import unittest
from nameproof.naming import propose, logo_brief, validate_brief
class NamingTests(unittest.TestCase):
    def test_idea_changes_names(self):
        a=propose({'idea':'writing editor'})['candidates']
        b=propose({'idea':'code test developer'})['candidates']
        self.assertNotEqual([x['name'] for x in a],[x['name'] for x in b])
    def test_repeatable(self):
        self.assertEqual(propose({'idea':'research'}),propose({'idea':'research'}))
    def test_host_candidates(self):
        result=propose({'idea':'writing'},[{'name':'Folio','rationale':'documents'}])
        self.assertEqual(result['method'],'host_candidates_ranked')
        self.assertEqual(result['candidates'][0]['screening_status'],'not_checked')
    def test_dedupe_and_avoid(self):
        result=propose({'idea':'writing','avoid':['nest']},[{'name':x,'rationale':'x'} for x in ['Quill','QUILL','QuillNest']])
        self.assertEqual(len(result['candidates']),1)
    def test_bad_inputs(self):
        for brief in [{},{'idea':''},{'idea':2},{'idea':'ok','max_length':True},{'idea':'ok','tlds':['com/path']},{'idea':'ok','keywords':'thing'}]:
            with self.subTest(brief=brief),self.assertRaises(ValueError): validate_brief(brief)
    def test_logo_never_fabricates_image(self):
        result=logo_brief('Folio',{'idea':'editor'})
        self.assertEqual(result['status'],'brief_only_no_image_generated')
        self.assertTrue(result['approval_required_before'])
