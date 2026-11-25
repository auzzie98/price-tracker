from pathlib import Path
import unittest

from scripts.serve import cpus_page, gpus_page, ram_page


class TestGpuPage(unittest.TestCase):
    def test_gpu_route_uses_a_dedicated_page(self):
        response = gpus_page()

        self.assertEqual(Path(response.path).name, "gpus.html")

    def test_cpu_and_ram_routes_keep_the_shared_category_page(self):
        self.assertEqual(Path(cpus_page().path).name, "category.html")
        self.assertEqual(Path(ram_page().path).name, "category.html")

    def test_gpu_page_contains_requested_sections_and_controls(self):
        page_path = Path(__file__).resolve().parents[1] / "web" / "gpus.html"
        page = page_path.read_text(encoding="utf-8")

        for expected in (
            "Graphics cards",
            "GPU price index",
            "Lowest price",
            "Highest price",
            "Median of models",
            "Observations",
            "data-maker=\"NVIDIA\"",
            "data-maker=\"AMD\"",
            "data-maker=\"Intel\"",
            "Biggest 30-day drop",
            "30-day trend",
            "src=\"/static/js/gpus.js\"",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, page)


if __name__ == "__main__":
    unittest.main()
