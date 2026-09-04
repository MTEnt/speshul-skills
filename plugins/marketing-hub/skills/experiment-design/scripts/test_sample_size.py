from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sample_size.py"


class SampleSizeTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)

    def test_proportions_estimate_is_in_the_textbook_range(self) -> None:
        completed = self.run_script("proportions", "--baseline", "0.10", "--mde", "0.02", "--power", "0.80", "--alpha", "0.05")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(3000 <= int(payload["per_group"]) <= 4500, payload)
        self.assertEqual(payload["total"], payload["per_group"] * 2)

    def test_invalid_probability_is_rejected(self) -> None:
        completed = self.run_script("proportions", "--baseline", "1.5", "--mde", "0.02")
        self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
