"""Calorie and history calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from calory_tracker.models import MealEntry, UserData


@dataclass
class DashboardSummary:
    today_total: int
    remaining: int
    goal: int
    protein: float
    carbs: float
    fat: float
    weekly_totals: list[tuple[str, int]]


class CalorieService:
    """Business logic for totals, filters, and chart data."""

    @staticmethod
    def parse_iso_date(raw_value: str, field_name: str) -> date:
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc

    def build_dashboard_summary(self, user_data: UserData, today: date | None = None) -> DashboardSummary:
        current_day = today or date.today()
        today_iso = current_day.isoformat()
        today_entries = [entry for entry in user_data.entries if entry.consumed_on == today_iso]

        today_total = sum(entry.calories for entry in today_entries)
        protein_total = sum(entry.protein for entry in today_entries)
        carbs_total = sum(entry.carbs for entry in today_entries)
        fat_total = sum(entry.fat for entry in today_entries)

        goal = user_data.settings.active_goal()
        remaining = goal - today_total
        weekly_totals = self.build_weekly_totals(user_data.entries, current_day, 7)

        return DashboardSummary(
            today_total=today_total,
            remaining=remaining,
            goal=goal,
            protein=round(protein_total, 1),
            carbs=round(carbs_total, 1),
            fat=round(fat_total, 1),
            weekly_totals=weekly_totals,
        )

    def build_weekly_totals(
        self,
        entries: list[MealEntry],
        end_date: date,
        window_days: int,
    ) -> list[tuple[str, int]]:
        results: list[tuple[str, int]] = []
        for offset in range(window_days - 1, -1, -1):
            day = end_date - timedelta(days=offset)
            day_iso = day.isoformat()
            total = sum(entry.calories for entry in entries if entry.consumed_on == day_iso)
            results.append((day_iso, total))
        return results

    def filter_entries(
        self,
        entries: list[MealEntry],
        query: str = "",
        start_date: str = "",
        end_date: str = "",
    ) -> list[MealEntry]:
        filtered_entries = list(entries)

        def entry_date(entry: MealEntry) -> date | None:
            try:
                return self.parse_iso_date(entry.consumed_on, "Entry date")
            except ValueError:
                return None

        if start_date:
            start = self.parse_iso_date(start_date, "Start date")
            filtered_entries = [
                entry
                for entry in filtered_entries
                if (entry_day := entry_date(entry)) is not None and entry_day >= start
            ]

        if end_date:
            end = self.parse_iso_date(end_date, "End date")
            filtered_entries = [
                entry
                for entry in filtered_entries
                if (entry_day := entry_date(entry)) is not None and entry_day <= end
            ]

        if query:
            lowered = query.strip().lower()
            filtered_entries = [
                entry
                for entry in filtered_entries
                if lowered in entry.meal_name.lower() or lowered in entry.notes.lower()
            ]

        return sorted(
            filtered_entries,
            key=lambda entry: (entry.consumed_on, entry.entry_id),
            reverse=True,
        )
