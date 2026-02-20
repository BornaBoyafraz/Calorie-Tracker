"""Domain model for persisted user data."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .meal_entry import MealEntry
from .settings import AppSettings


@dataclass
class UserData:
    """Container for all user-facing data."""

    username: str
    settings: AppSettings = field(default_factory=AppSettings)
    entries: list[MealEntry] = field(default_factory=list)
    legacy_state: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, username: str, payload: dict[str, Any]) -> "UserData":
        settings_payload = payload.get("settings", {})
        rest_day = int(payload.get("Rest Day Calories", settings_payload.get("rest_day_goal", 2200)))
        workout_day = int(payload.get("Workout Day Calories", settings_payload.get("workout_day_goal", 2500)))
        settings_payload = {
            "unit_system": settings_payload.get("unit_system", "metric"),
            "daily_goal": settings_payload.get("daily_goal", rest_day),
            "rest_day_goal": rest_day,
            "workout_day_goal": workout_day,
            "active_day_type": settings_payload.get("active_day_type", "daily"),
        }

        raw_entries = payload.get("entries", [])
        entries: list[MealEntry] = []
        if isinstance(raw_entries, list):
            for entry_payload in raw_entries:
                if isinstance(entry_payload, dict):
                    entry = MealEntry.from_dict(entry_payload)
                    if entry.entry_id:
                        entries.append(entry)

        return cls(
            username=username,
            settings=AppSettings.from_dict(settings_payload),
            entries=entries,
            legacy_state=payload,
        )

    def to_payload(self) -> dict[str, Any]:
        payload = dict(self.legacy_state)
        payload.update(
            {
                "user_name": self.username,
                "Rest Day Calories": self.settings.rest_day_goal,
                "Workout Day Calories": self.settings.workout_day_goal,
                "settings": self.settings.to_dict(),
                "entries": [entry.to_dict() for entry in self.entries],
                "version": 2,
            }
        )

        today_total = sum(
            entry.calories for entry in self.entries if entry.consumed_on == date.today().isoformat()
        )
        payload["Calories Left Rest Day"] = self.settings.rest_day_goal - today_total
        payload["Calories Left Workout Day"] = self.settings.workout_day_goal - today_total

        return payload
