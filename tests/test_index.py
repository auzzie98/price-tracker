"""Index test, from the worked example in METHODOLOGY.md.

Days 1 to 4, indexes 100.00, 99.00, 97.35, and 95.65.
Do not change these numbers. They are the source of truth for the test.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_tracker.index import compute_index


class TestIndexWorkedExample(unittest.TestCase):
    def test_worked_example(self):
        """Worked example from METHODOLOGY.md, Days 1 to 4.

        Median price per SKU per day (dollars):
            SKU | Day 1 | Day 2 | Day 3 | Day 4
            A   | 500   | 490   | 490   | 480.20
            B   | 600   | 600   | 570   | 570
            C   | 700   | 693   | 693   | 693
            D   | none  | none  | 900   | 855

        Expected indexes: 100.00, 99.00, 97.35, 95.65.
        SKU D is new on Day 3 (skipped), counts on Day 4.
        """
        period_prices = {
            "Day 1": {"A": 500.0, "B": 600.0, "C": 700.0},
            "Day 2": {"A": 490.0, "B": 600.0, "C": 693.0},
            "Day 3": {"A": 490.0, "B": 570.0, "C": 693.0, "D": 900.0},
            "Day 4": {"A": 480.20, "B": 570.0, "C": 693.0, "D": 855.0},
        }
        results = compute_index(period_prices)

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0], ("Day 1", 100.0, 3))
        self.assertEqual(results[1], ("Day 2", 99.0, 3))
        self.assertEqual(results[2], ("Day 3", 97.35, 3))
        self.assertEqual(results[3], ("Day 4", 95.65, 4))


if __name__ == "__main__":
    unittest.main()
