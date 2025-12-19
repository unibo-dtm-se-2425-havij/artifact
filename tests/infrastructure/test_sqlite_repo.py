import sqlite3
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from havij.infrastructure.persistence.sqlite_db import init_schema
from havij.infrastructure.persistence.meal_repository import SqliteDayLogRepository
from havij.domain.model.meal import DayLog, MealEntry
from havij.domain.model.nutrients import Nutrients


class TestSqliteRepository(unittest.TestCase):
    def test_sqlite_repository_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            db = Path(tmp_dir) / "t.sqlite"
            conn = sqlite3.connect(str(db))
            conn.row_factory = sqlite3.Row
            init_schema(conn)
            repo = SqliteDayLogRepository(conn)

            d = date(2025, 1, 1)
            log = DayLog(day=d, entries=[
                MealEntry(
                    entry_id="e1",
                    timestamp=datetime(2025, 1, 1, 9, 0, 0),
                    barcode="111",
                    product_name="X",
                    grams=100.0,
                    nutrients=Nutrients(100, 1, 2, 3),
                )
            ])
            repo.save_day(log)
            loaded = repo.load_day(d)
            self.assertEqual(len(loaded.entries), 1)
            self.assertEqual(loaded.entries[0].barcode, "111")
            self.assertEqual(loaded.total_nutrients().kcal, 100)
