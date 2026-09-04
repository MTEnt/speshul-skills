import unittest

from pages import page_path, page_paths


class PageTests(unittest.TestCase):
    def test_single(self) -> None:
        self.assertEqual(page_path("  Hello, World!  "), "/hello-world")

    def test_many(self) -> None:
        self.assertEqual(page_paths(["A B", "C--D"]), ["/a-b", "/c-d"])

    def test_empty(self) -> None:
        self.assertEqual(page_path("!!!"), "/")


if __name__ == "__main__":
    unittest.main()
