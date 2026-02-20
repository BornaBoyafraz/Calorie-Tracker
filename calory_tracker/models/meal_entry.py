"""Domain model for meal entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


def _today_iso() -> str:
    return date.today().isoformat()


@dataclass
class MealEntry:
    """Represents one logged meal entry."""

    entry_id: str
    meal_name: str
    calories: int
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    meal_type: str = "Meal"
    notes: str = ""
    consumed_on: str = field(default_factory=_today_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "meal_name": self.meal_name,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "meal_type": self.meal_type,
            "notes": self.notes,
            "consumed_on": self.consumed_on,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MealEntry":
        return cls(
            entry_id=str(payload.get("entry_id", "")),
            meal_name=str(payload.get("meal_name", "")).strip(),
            calories=int(payload.get("calories", 0)),
            protein=float(payload.get("protein", 0.0)),
            carbs=float(payload.get("carbs", 0.0)),
            fat=float(payload.get("fat", 0.0)),
            meal_type=str(payload.get("meal_type", "Meal")),
            notes=str(payload.get("notes", "")),
            consumed_on=str(payload.get("consumed_on", _today_iso())),
        )
