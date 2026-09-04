import unittest

from pricing import tier_total


class TierTotalTests(unittest.TestCase):
    def test_single_unit(self) -> None:
        self.assertEqual(tier_total(10.0, 1), 10.0)

    def test_ten_units_full_price(self) -> None:
        self.assertEqual(tier_total(10.0, 10), 100.0)

    def test_discount_after_tenth_unit(self) -> None:
        self.assertEqual(tier_total(10.0, 12), 116.0)


if __name__ == "__main__":
    unittest.main()
