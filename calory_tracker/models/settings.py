"""Domain model for user settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AppSettings:
    """Editable application settings."""

    unit_system: str = "metric"
    daily_goal: int = 2200
    rest_day_goal: int = 2200
    workout_day_goal: int = 2500
    active_day_type: str = "daily"

    def active_goal(self) -> int:
        if self.active_day_type == "daily":
            return self.daily_goal
        if self.active_day_type == "workout":
            return self.workout_day_goal
        if self.active_day_type == "rest":
            return self.rest_day_goal
        return self.daily_goal

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_system": self.unit_system,
            "daily_goal": self.daily_goal,
            "rest_day_goal": self.rest_day_goal,
            "workout_day_goal": self.workout_day_goal,
            "active_day_type": self.active_day_type,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AppSettings":
        return cls(
            unit_system=str(payload.get("unit_system", "metric")),
            daily_goal=int(payload.get("daily_goal", payload.get("rest_day_goal", 2200))),
            rest_day_goal=int(payload.get("rest_day_goal", payload.get("daily_goal", 2200))),
            workout_day_goal=int(payload.get("workout_day_goal", 2500)),
            active_day_type=str(payload.get("active_day_type", "daily")),
        )
