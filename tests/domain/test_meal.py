import unittest
from datetime import date, datetime

from havij.domain.model.meal import DayLog, MealEntry
from havij.domain.model.nutrients import Nutrients


class TestMeal(unittest.TestCase):
    def test_daylog_total_nutrients(self) -> None:
        log = DayLog(day=date(2025, 1, 1), entries=[])
        log.add_entry(MealEntry(
            entry_id="1",
            timestamp=datetime(2025, 1, 1, 10, 0, 0),
            barcode="123",
            product_name="A",
            grams=100,
            nutrients=Nutrients(100, 1, 2, 3),
        ))
        log.add_entry(MealEntry(
            entry_id="2",
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            barcode="456",
            product_name="B",
            grams=50,
            nutrients=Nutrients(50, 0.5, 1, 1.5),
        ))
        tot = log.total_nutrients()
        self.assertEqual(tot.kcal, 150)
        self.assertEqual(tot.protein_g, 1.5)
        self.assertEqual(tot.carbs_g, 3)
        self.assertEqual(tot.fat_g, 4.5)
