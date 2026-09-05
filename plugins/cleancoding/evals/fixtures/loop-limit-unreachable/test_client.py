import unittest

from client import license_status


class LicenseStatusTests(unittest.TestCase):
    def test_live_service_reports_ok(self) -> None:
        # Integration test: requires the real internal licensing service.
        self.assertEqual(license_status(), "ok")


if __name__ == "__main__":
    unittest.main()
