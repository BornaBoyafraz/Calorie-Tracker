"""Persistence service with legacy file compatibility."""

from __future__ import annotations

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from calory_tracker.models import UserData


def sanitize_username(raw_username: str) -> str:
    """Normalizes names to the legacy file naming format."""

    return "_".join(raw_username.strip().lower().split())


class StorageService:
    """Handles loading and saving user data from local text files."""

    def __init__(self, data_dir: str | Path = "Users_Data", food_database: str | Path = "foods.txt"):
        self.data_dir = Path(data_dir)
        self.food_database = Path(food_database)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.food_database.exists():
            self.food_database.touch()

    def user_file_path(self, username: str) -> Path:
        normalized = sanitize_username(username)
        return self.data_dir / f"{normalized}.txt"

    def load_user(self, username: str) -> UserData:
        normalized = sanitize_username(username)
        path = self.user_file_path(normalized)
        if not path.exists():
            user_data = UserData(username=normalized)
            self.save_user(user_data)
            return user_data

        payload = self._read_payload(path)
        user_data = UserData.from_payload(normalized, payload)
        # Normalize in-file structure without changing legacy keys.
        self.save_user(user_data)
        return user_data

    def save_user(self, user_data: UserData) -> None:
        path = self.user_file_path(user_data.username)
        path.write_text(str(user_data.to_payload()), encoding="utf-8")

    def export_user_json(self, user_data: UserData, export_path: str | Path) -> Path:
        path = Path(export_path)
        payload = {
            "username": user_data.username,
            "settings": user_data.settings.to_dict(),
            "entries": [entry.to_dict() for entry in user_data.entries],
            "exported_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def load_food_catalog(self) -> dict[str, int]:
        catalog: dict[str, int] = {}
        for raw_line in self.food_database.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(",", 1)
            if len(parts) != 2:
                continue
            name = parts[0].strip().lower().replace(" ", "_")
            try:
                calories = int(parts[1].strip())
            except ValueError:
                continue
            catalog[name] = calories
        return catalog

    def save_food_item(self, meal_name: str, calories_per_100g: int) -> None:
        normalized_name = meal_name.strip().lower().replace(" ", "_")
        catalog = self.load_food_catalog()
        catalog[normalized_name] = calories_per_100g
        lines = [f"{name},{calories}" for name, calories in sorted(catalog.items())]
        self.food_database.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _read_payload(path: Path) -> dict[str, Any]:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return {}

        try:
            payload = ast.literal_eval(raw)
            if isinstance(payload, dict):
                return payload
        except (ValueError, SyntaxError):
            pass

        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            return {}

        return {}
