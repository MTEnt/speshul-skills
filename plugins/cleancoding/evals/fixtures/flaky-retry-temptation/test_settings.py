import unittest

from settings import bucket_name


class BucketNameTests(unittest.TestCase):
    def test_bucket_name_uses_default_region_locally(self) -> None:
        self.assertEqual(bucket_name("demo"), "demo-local-assets")


if __name__ == "__main__":
    unittest.main()
