"""Minimal service smoke checks for Calory Tracker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from calory_tracker.services import CalorieService, StorageService, UserService


class ServiceSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        root = Path(self.tmpdir.name)
        self.storage = StorageService(data_dir=root / "Users_Data", food_database=root / "foods.txt")
        self.service = UserService(self.storage, CalorieService())

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_load_user_creates_legacy_file(self) -> None:
        user_data = self.service.load_user("Jane Doe")

        self.assertEqual(user_data.username, "jane_doe")
        self.assertTrue((Path(self.tmpdir.name) / "Users_Data" / "jane_doe.txt").exists())

    def test_add_entry_persists_and_can_be_reloaded(self) -> None:
        user_data = self.service.load_user("Jane Doe")
        self.service.add_entry(
            user_data,
            {
                "consumed_on": "2026-02-20",
                "meal_name": "Chicken bowl",
                "calories": "650",
                "protein": "45",
                "carbs": "55",
                "fat": "20",
                "meal_type": "Lunch",
                "notes": "post-workout",
            },
        )

        reloaded = self.service.load_user("Jane Doe")
        self.assertEqual(len(reloaded.entries), 1)
        self.assertEqual(reloaded.entries[0].meal_name, "Chicken bowl")

    def test_history_filter_returns_expected_entries(self) -> None:
        user_data = self.service.load_user("Jane Doe")
        self.service.add_entry(
            user_data,
            {
                "consumed_on": "2026-02-19",
                "meal_name": "Oats",
                "calories": "410",
                "protein": "24",
                "carbs": "50",
                "fat": "11",
                "meal_type": "Breakfast",
                "notes": "",
            },
        )
        self.service.add_entry(
            user_data,
            {
                "consumed_on": "2026-02-20",
                "meal_name": "Pasta",
                "calories": "700",
                "protein": "26",
                "carbs": "95",
                "fat": "22",
                "meal_type": "Dinner",
                "notes": "family dinner",
            },
        )

        results = self.service.filter_history(
            user_data,
            query="pasta",
            start_date="2026-02-20",
            end_date="2026-02-20",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].meal_name, "Pasta")

    def test_sample_data_generation(self) -> None:
        user_data = self.service.load_user("Jane Doe")
        self.service.seed_sample_data(user_data, overwrite=False)
        self.assertGreater(len(user_data.entries), 0)


if __name__ == "__main__":
    unittest.main()
