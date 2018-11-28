import io
import os
import sys
import unittest

import env  # noqa pylint: disable=unused-import
from interpreter.c_lexer import Lexer
from interpreter.c_parser import Parser

PATH = os.path.dirname(os.path.abspath(__file__))


def _run_code(filename, args=None, input_=None):
    parser = Parser(Lexer(f'{PATH}/minic/{filename}'))
    backup = [v for v in (sys.argv, sys.stdin, sys.stdout)]

    if args is not None:
        sys.argv = (None, None, *args)
    if input_ is not None:
        sys.stdin = io.StringIO(input_)
    sys.stdout = io.StringIO()

    parser.parse()
    result = sys.stdout.getvalue()

    sys.argv, sys.stdin, sys.stdout = backup
    return result


class TestParser(unittest.TestCase):

    def test_ex(self):
        result = _run_code('ex.c', None, '1000\n')
        self.assertIn('= 2 * 2 * 2 * 5 * 5 * 5', result)
        result = _run_code('ex.c', None, f'{2 * 3 * 5 * 7}\n')
        self.assertIn('= 2 * 3 * 5 * 7', result)

    def test_cafunfo(self):
        result = _run_code('cafunfo.c', (100, 1))
        self.assertNotIn('7', result)
        self.assertIn('cafunfo', result)


if __name__ == "__main__":
    unittest.main()
