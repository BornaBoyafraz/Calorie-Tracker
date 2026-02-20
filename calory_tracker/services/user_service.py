"""Application service coordinating validation and persistence."""

from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from calory_tracker.models import AppSettings, MealEntry, UserData
from calory_tracker.services.calorie_service import CalorieService, DashboardSummary
from calory_tracker.services.storage_service import StorageService


class UserService:
    """Coordinates CRUD operations while keeping the UI layer thin."""

    def __init__(self, storage: StorageService, calories: CalorieService):
        self.storage = storage
        self.calories = calories

    def load_user(self, username: str) -> UserData:
        return self.storage.load_user(username)

    def save_settings(self, user_data: UserData, updates: dict[str, str]) -> UserData:
        unit_system = updates.get("unit_system", user_data.settings.unit_system).strip().lower()
        if unit_system not in {"metric", "imperial"}:
            raise ValueError("Unit system must be either metric or imperial.")

        daily_goal = self._to_positive_int(updates.get("daily_goal", user_data.settings.daily_goal), "Daily goal")
        rest_goal = self._to_positive_int(updates.get("rest_day_goal", user_data.settings.rest_day_goal), "Rest day goal")
        workout_goal = self._to_positive_int(
            updates.get("workout_day_goal", user_data.settings.workout_day_goal),
            "Workout day goal",
        )

        active_day_type = updates.get("active_day_type", user_data.settings.active_day_type).strip().lower()
        if active_day_type not in {"daily", "rest", "workout"}:
            raise ValueError("Active day type must be daily, rest, or workout.")

        user_data.settings = AppSettings(
            unit_system=unit_system,
            daily_goal=daily_goal,
            rest_day_goal=rest_goal,
            workout_day_goal=workout_goal,
            active_day_type=active_day_type,
        )
        self.storage.save_user(user_data)
        return user_data

    def add_entry(self, user_data: UserData, entry_input: dict[str, str]) -> MealEntry:
        entry = self._build_entry(entry_input, entry_id=str(uuid4()))
        user_data.entries.append(entry)
        self.storage.save_user(user_data)
        return entry

    def update_entry(self, user_data: UserData, entry_id: str, entry_input: dict[str, str]) -> MealEntry:
        updated = self._build_entry(entry_input, entry_id=entry_id)
        for index, entry in enumerate(user_data.entries):
            if entry.entry_id == entry_id:
                user_data.entries[index] = updated
                self.storage.save_user(user_data)
                return updated

        raise ValueError("The selected entry no longer exists.")

    def delete_entry(self, user_data: UserData, entry_id: str, persist: bool = True) -> None:
        before = len(user_data.entries)
        user_data.entries = [entry for entry in user_data.entries if entry.entry_id != entry_id]
        if len(user_data.entries) == before:
            raise ValueError("The selected entry no longer exists.")
        if persist:
            self.storage.save_user(user_data)

    def build_dashboard(self, user_data: UserData) -> DashboardSummary:
        return self.calories.build_dashboard_summary(user_data)

    def filter_history(
        self,
        user_data: UserData,
        query: str = "",
        start_date: str = "",
        end_date: str = "",
    ) -> list[MealEntry]:
        return self.calories.filter_entries(user_data.entries, query, start_date, end_date)

    def seed_sample_data(self, user_data: UserData, overwrite: bool) -> UserData:
        if user_data.entries and not overwrite:
            raise ValueError("Entries already exist. Choose overwrite to replace them with sample data.")

        if overwrite:
            user_data.entries = []

        base = date.today()
        sample_entries: list[MealEntry] = []
        sample_rows = [
            ("Protein Oats", 420, 30, 52, 10, "Breakfast"),
            ("Chicken Bowl", 610, 46, 58, 18, "Lunch"),
            ("Greek Yogurt", 180, 16, 14, 6, "Snack"),
            ("Salmon Rice", 540, 38, 45, 21, "Dinner"),
        ]

        for day_offset in range(0, 7):
            day_iso = (base - timedelta(days=day_offset)).isoformat()
            for row_index, row in enumerate(sample_rows):
                if (day_offset + row_index) % 2 == 0:
                    sample_entries.append(
                        MealEntry(
                            entry_id=str(uuid4()),
                            meal_name=row[0],
                            calories=row[1],
                            protein=float(row[2]),
                            carbs=float(row[3]),
                            fat=float(row[4]),
                            meal_type=row[5],
                            consumed_on=day_iso,
                            notes="Sample data",
                        )
                    )

        user_data.entries.extend(sample_entries)
        self.storage.save_user(user_data)
        return user_data

    def export_user(self, user_data: UserData, export_path: str) -> None:
        self.storage.export_user_json(user_data, export_path)

    def meal_calories_from_catalog(self, meal_name: str) -> int | None:
        normalized = meal_name.strip().lower().replace(" ", "_")
        if not normalized:
            return None
        return self.storage.load_food_catalog().get(normalized)

    def save_meal_to_catalog(self, meal_name: str, calories_per_100g: int) -> None:
        if not meal_name.strip():
            raise ValueError("Meal name cannot be empty.")
        if calories_per_100g <= 0:
            raise ValueError("Calories per 100g must be a positive number.")
        self.storage.save_food_item(meal_name, calories_per_100g)

    def _build_entry(self, entry_input: dict[str, str], entry_id: str) -> MealEntry:
        meal_name = entry_input.get("meal_name", "").strip()
        if not meal_name:
            raise ValueError("Meal name is required.")

        consumed_on = entry_input.get("consumed_on", date.today().isoformat()).strip()
        self.calories.parse_iso_date(consumed_on, "Date")

        calories = self._to_positive_int(entry_input.get("calories", "0"), "Calories")

        protein = self._to_non_negative_float(entry_input.get("protein", "0"), "Protein")
        carbs = self._to_non_negative_float(entry_input.get("carbs", "0"), "Carbs")
        fat = self._to_non_negative_float(entry_input.get("fat", "0"), "Fat")

        meal_type = entry_input.get("meal_type", "Meal").strip() or "Meal"
        notes = entry_input.get("notes", "").strip()

        return MealEntry(
            entry_id=entry_id,
            meal_name=meal_name,
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            meal_type=meal_type,
            notes=notes,
            consumed_on=consumed_on,
        )

    @staticmethod
    def _to_positive_int(value: str | int, label: str) -> int:
        try:
            number = int(str(value).strip())
        except ValueError as exc:
            raise ValueError(f"{label} must be a whole number.") from exc
        if number <= 0:
            raise ValueError(f"{label} must be greater than zero.")
        return number

    @staticmethod
    def _to_non_negative_float(value: str | float, label: str) -> float:
        text = str(value).strip()
        if not text:
            return 0.0
        try:
            number = float(text)
        except ValueError as exc:
            raise ValueError(f"{label} must be a valid number.") from exc
        if number < 0:
            raise ValueError(f"{label} cannot be negative.")
        return number
