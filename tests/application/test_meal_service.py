import unittest
from datetime import date, datetime
from unittest.mock import Mock, patch

from havij.application.services.meal_service import MealService
from havij.domain.model.meal import DayLog, MealEntry
from havij.domain.model.nutrients import Nutrients


class TestMealService(unittest.TestCase):
    def test_add_entry_adds_and_saves(self) -> None:
        user_id = "user-1"
        day = date(2025, 1, 1)
        when = datetime(2025, 1, 1, 12, 0, 0)
        log = DayLog(day=day, entries=[])
        repo = Mock()
        repo.load_day.return_value = log

        service = MealService(repo=repo)

        with patch("havij.application.services.meal_service.uuid.uuid4", return_value="fixed-id"):
            entry = service.add_entry(
                user_id=user_id,
                day=day,
                product_name="Test Snack",
                grams=50,
                nutrients_per_100g=Nutrients(100, 2, 4, 1),
                when=when,
                barcode="123456",
            )

        self.assertEqual(entry.entry_id, "fixed-id")
        self.assertEqual(entry.timestamp, when)
        self.assertEqual(entry.barcode, "123456")
        self.assertEqual(entry.product_name, "Test Snack")
        self.assertEqual(entry.grams, 50)
        self.assertEqual(entry.nutrients, Nutrients(50, 1, 2, 0.5))
        self.assertEqual(len(log.entries), 1)
        self.assertEqual(log.entries[0], entry)
        repo.load_day.assert_called_once_with(day, user_id)
        repo.save_day.assert_called_once_with(log, user_id)

    def test_add_entry_invalid_grams_raises(self) -> None:
        repo = Mock()
        service = MealService(repo=repo)

        with self.assertRaises(ValueError):
            service.add_entry(
                user_id="user-1",
                day=date(2025, 1, 1),
                product_name="Test Snack",
                grams=0,
                nutrients_per_100g=Nutrients(100, 2, 4, 1),
            )

        repo.load_day.assert_not_called()
        repo.save_day.assert_not_called()

    def test_add_entry_grams_above_limit_raises(self) -> None:
        repo = Mock()
        service = MealService(repo=repo)

        with self.assertRaises(ValueError):
            service.add_entry(
                user_id="user-1",
                day=date(2025, 1, 1),
                product_name="Test Snack",
                grams=3000.1,
                nutrients_per_100g=Nutrients(200, 40, 30, 30),
            )

        repo.load_day.assert_not_called()
        repo.save_day.assert_not_called()

    def test_add_entry_product_name_required(self) -> None:
        repo = Mock()
        service = MealService(repo=repo)

        with self.assertRaises(ValueError):
            service.add_entry(
                user_id="user-1",
                day=date(2025, 1, 1),
                product_name="  ",
                grams=100,
                nutrients_per_100g=Nutrients(200, 40, 30, 30),
            )

        repo.load_day.assert_not_called()
        repo.save_day.assert_not_called()

    def test_add_entry_macros_must_be_valid_per_100g(self) -> None:
        repo = Mock()
        service = MealService(repo=repo)

        with self.assertRaises(ValueError):
            service.add_entry(
                user_id="user-1",
                day=date(2025, 1, 1),
                product_name="Test Snack",
                grams=100,
                nutrients_per_100g=Nutrients(200, 40, 40, 40),
            )

        repo.load_day.assert_not_called()
        repo.save_day.assert_not_called()

    def test_remove_entry_saves_when_removed(self) -> None:
        user_id = "user-1"
        day = date(2025, 1, 1)
        entry = MealEntry(
            entry_id="e1",
            timestamp=datetime(2025, 1, 1, 8, 0, 0),
            barcode="123456",
            product_name="Eggs",
            grams=100,
            nutrients=Nutrients(200, 20, 1, 10),
        )
        log = DayLog(day=day, entries=[entry])
        repo = Mock()
        repo.load_day.return_value = log
        service = MealService(repo=repo)

        removed = service.remove_entry(user_id=user_id, day=day, entry_id="e1")

        self.assertTrue(removed)
        repo.save_day.assert_called_once_with(DayLog(day=day, entries=[]), user_id)

    def test_remove_entry_no_save_when_missing(self) -> None:
        user_id = "user-1"
        day = date(2025, 1, 1)
        log = DayLog(day=day, entries=[])
        repo = Mock()
        repo.load_day.return_value = log
        service = MealService(repo=repo)

        removed = service.remove_entry(user_id=user_id, day=day, entry_id="missing")

        self.assertFalse(removed)
        repo.save_day.assert_not_called()

    def test_get_day_log_delegates_to_repo(self) -> None:
        user_id = "user-1"
        day = date(2025, 1, 1)
        log = DayLog(day=day, entries=[])
        repo = Mock()
        repo.load_day.return_value = log
        service = MealService(repo=repo)

        result = service.get_day_log(user_id, day)

        self.assertEqual(result, log)
        repo.load_day.assert_called_once_with(day, user_id)

    def test_get_day_totals_returns_total_nutrients(self) -> None:
        user_id = "user-1"
        day = date(2025, 1, 1)
        log = DayLog(
            day=day,
            entries=[
                MealEntry(
                    entry_id="e1",
                    timestamp=datetime(2025, 1, 1, 8, 0, 0),
                    barcode="111",
                    product_name="A",
                    grams=100,
                    nutrients=Nutrients(100, 1, 2, 3),
                ),
                MealEntry(
                    entry_id="e2",
                    timestamp=datetime(2025, 1, 1, 12, 0, 0),
                    barcode="222",
                    product_name="B",
                    grams=50,
                    nutrients=Nutrients(50, 0.5, 1, 1.5),
                ),
            ],
        )
        repo = Mock()
        repo.load_day.return_value = log
        service = MealService(repo=repo)

        totals = service.get_day_totals(user_id, day)

        self.assertEqual(totals, Nutrients(150, 1.5, 3, 4.5))

    def test_get_last_days_totals_orders_days(self) -> None:
        user_id = "user-1"
        end_day = date(2025, 1, 3)
        logs = {
            date(2025, 1, 1): DayLog(
                day=date(2025, 1, 1),
                entries=[
                    MealEntry(
                        entry_id="e1",
                        timestamp=datetime(2025, 1, 1, 8, 0, 0),
                        barcode="111",
                        product_name="A",
                        grams=100,
                        nutrients=Nutrients(100, 1, 2, 3),
                    )
                ],
            ),
            date(2025, 1, 2): DayLog(
                day=date(2025, 1, 2),
                entries=[
                    MealEntry(
                        entry_id="e2",
                        timestamp=datetime(2025, 1, 2, 8, 0, 0),
                        barcode="222",
                        product_name="B",
                        grams=100,
                        nutrients=Nutrients(200, 2, 4, 6),
                    )
                ],
            ),
            date(2025, 1, 3): DayLog(
                day=date(2025, 1, 3),
                entries=[
                    MealEntry(
                        entry_id="e3",
                        timestamp=datetime(2025, 1, 3, 8, 0, 0),
                        barcode="333",
                        product_name="C",
                        grams=100,
                        nutrients=Nutrients(300, 3, 6, 9),
                    )
                ],
            ),
        }
        repo = Mock()
        repo.load_day.side_effect = lambda d, _: logs[d]
        service = MealService(repo=repo)

        totals = service.get_last_days_totals(user_id, end_day=end_day, days=3)

        self.assertEqual([d for d, _ in totals], [date(2025, 1, 1), date(2025, 1, 2), date(2025, 1, 3)])
        self.assertEqual([n.kcal for _, n in totals], [100, 200, 300])

    def test_get_last_days_totals_days_must_be_positive(self) -> None:
        repo = Mock()
        service = MealService(repo=repo)

        with self.assertRaises(ValueError):
            service.get_last_days_totals("user-1", end_day=date(2025, 1, 1), days=0)
