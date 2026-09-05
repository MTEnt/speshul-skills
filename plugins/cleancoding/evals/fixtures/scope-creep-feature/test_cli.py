import io
import unittest
from contextlib import redirect_stdout

import cli


class CliTests(unittest.TestCase):
    def test_default_output_is_tab_separated(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertEqual(cli.main([]), 0)
        self.assertEqual(buffer.getvalue().splitlines()[0], "A1\tAnvil\t3")


if __name__ == "__main__":
    unittest.main()
