import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from nameproof.logo import retrieve_logo_source
class LogoTests(unittest.TestCase):
    def test_manifest_offline(self):
        result=retrieve_logo_source('/not-created',getter=lambda _:self.fail('network'))
        self.assertEqual(result['status'],'not_fetched')
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError): retrieve_logo_source(root,True)
    def test_hash_mismatch_no_output(self):
        with tempfile.TemporaryDirectory() as root:
            target=Path(root)/'new'
            with self.assertRaises(ValueError): retrieve_logo_source(target,True,getter=lambda _:b'changed')
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(root).iterdir()),[])
    def test_exact_bytes_saved_without_execution(self):
        import hashlib
        data=b'# instructions\n'
        with tempfile.TemporaryDirectory() as root, patch('nameproof.logo.MANIFEST',{'SKILL.md':('UPSTREAM_SKILL.md',hashlib.sha256(data).hexdigest())}):
            target=Path(root)/'new'
            result=retrieve_logo_source(target,True,getter=lambda _:data)
            self.assertEqual((target/'UPSTREAM_SKILL.md').read_bytes(),data)
            self.assertTrue((target/'provenance.json').exists())
            self.assertNotIn('SKILL.md',[p.name for p in target.iterdir()])
            self.assertEqual(result['status'],'retrieved_hash_verified_instructions_only')
