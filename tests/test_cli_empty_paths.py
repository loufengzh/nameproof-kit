import contextlib
import io
import unittest
from unittest.mock import patch

from nameproof.cli import main


class EmptyInputPaths(unittest.TestCase):
    def test_explicit_empty_optional_paths_fail_before_dispatch(self):
        cases = [
            (['domain', 'example.com', '--live'], '--receipt'),
            (['screen', '--name', 'Example', '--countries', 'US', '--classes', '9'], '--records'),
            (['propose', '--brief', 'examples/brief.json'], '--candidates'),
            (['report', '--brief', 'examples/brief.json', '--live'], '--candidates'),
            (['report', '--brief', 'examples/brief.json', '--live'], '--records'),
        ]
        for args, option in cases:
            for suffix in ([option, ''], [option + '=']):
                with self.subTest(args=args, suffix=suffix):
                    out, err = io.StringIO(), io.StringIO()
                    with patch('nameproof.cli.check_domain') as domain, patch('nameproof.cli.load_json') as load:
                        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                            code = main(args + suffix)
                    self.assertEqual(code, 2)
                    self.assertEqual(out.getvalue(), '')
                    self.assertIn(option, err.getvalue())
                    self.assertNotIn('Traceback', err.getvalue())
                    domain.assert_not_called()
                    load.assert_not_called()

    def test_omitted_optional_paths_still_work(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(['screen', '--name', 'Example', '--countries', 'US', '--classes', '9'])
        self.assertEqual(code, 0)
        self.assertIn('not-searched', out.getvalue())
        self.assertEqual(err.getvalue(), '')

    def test_whitespace_is_a_literal_path_not_empty(self):
        with patch('nameproof.cli.load_json', return_value=[]) as load:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = main(['screen', '--name', 'Example', '--countries', 'US', '--classes', '9', '--records', ' '])
        self.assertEqual(code, 0)
        load.assert_called_once_with(' ')
