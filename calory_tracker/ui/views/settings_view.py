"""Settings screen with unit/goal controls and data actions."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class SettingsView(ttk.Frame):
    """Shows editable settings and utility actions."""

    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent, style="Surface.TFrame", padding=20)
        self.controller = controller

        self.unit_var = tk.StringVar(value="metric")
        self.daily_goal_var = tk.StringVar(value="2200")
        self.rest_goal_var = tk.StringVar(value="2200")
        self.workout_goal_var = tk.StringVar(value="2500")
        self.active_day_var = tk.StringVar(value="daily")

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Settings", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self,
            text="Customize goals, units, and data tools.",
            style="Subheading.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 16))

        form = ttk.Frame(self, style="Surface.TFrame")
        form.grid(row=2, column=0, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        self._row(form, 0, "Unit system", self.unit_var, widget="combo", values=("metric", "imperial"))
        self._row(form, 1, "Daily goal (kcal)", self.daily_goal_var)
        self._row(form, 2, "Rest day goal (kcal)", self.rest_goal_var)
        self._row(form, 3, "Workout day goal (kcal)", self.workout_goal_var)
        self._row(
            form,
            4,
            "Active day type",
            self.active_day_var,
            widget="combo",
            values=("daily", "rest", "workout"),
        )

        actions = ttk.Frame(self, style="Surface.TFrame")
        actions.grid(row=3, column=0, sticky="w", pady=(16, 0))

        ttk.Button(actions, text="Save Settings", style="Primary.TButton", command=self.save_settings).pack(side="left")
        ttk.Button(actions, text="Export Data", style="Ghost.TButton", command=self.export_data).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(actions, text="Load Sample Data", style="Ghost.TButton", command=self.load_sample_data).pack(
            side="left", padx=(8, 0)
        )

        self.status_label = ttk.Label(self, text="", style="Subheading.TLabel")
        self.status_label.grid(row=4, column=0, sticky="w", pady=(14, 0))

    def _row(self, parent: ttk.Frame, row: int, label: str, variable, widget: str = "entry", values=()) -> None:
        ttk.Label(parent, text=label, style="Surface.TLabel").grid(row=row, column=0, sticky="w", pady=(0, 10), padx=(0, 12))
        if widget == "combo":
            ttk.Combobox(
                parent,
                textvariable=variable,
                values=values,
                style="App.TCombobox",
                width=28,
                state="readonly",
            ).grid(row=row, column=1, sticky="w", pady=(0, 10))
            return

        ttk.Entry(parent, textvariable=variable, style="App.TEntry", width=30).grid(row=row, column=1, sticky="w", pady=(0, 10))

    def refresh(self) -> None:
        settings = self.controller.user_data.settings
        self.unit_var.set(settings.unit_system)
        self.daily_goal_var.set(str(settings.daily_goal))
        self.rest_goal_var.set(str(settings.rest_day_goal))
        self.workout_goal_var.set(str(settings.workout_day_goal))
        self.active_day_var.set(settings.active_day_type)

    def save_settings(self) -> None:
        payload = {
            "unit_system": self.unit_var.get(),
            "daily_goal": self.daily_goal_var.get(),
            "rest_day_goal": self.rest_goal_var.get(),
            "workout_day_goal": self.workout_goal_var.get(),
            "active_day_type": self.active_day_var.get(),
        }

        try:
            self.controller.update_settings(payload)
        except ValueError as exc:
            messagebox.showerror("Validation error", str(exc))
            return

        self.status_label.config(text="Settings saved.")
        self.controller.refresh_dashboard_and_history()

    def export_data(self) -> None:
        initial = f"{self.controller.user_data.username}_export.json"
        path = filedialog.asksaveasfilename(
            title="Export Data",
            initialfile=initial,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return

        self.controller.export_data(path)
        self.status_label.config(text=f"Data exported to {path}")

    def load_sample_data(self) -> None:
        overwrite = messagebox.askyesno(
            "Sample data",
            "Overwrite existing entries with sample data?\nChoose 'No' to append sample data.",
        )

        try:
            self.controller.load_sample_data(overwrite=overwrite)
        except ValueError as exc:
            messagebox.showerror("Sample data", str(exc))
            return

        self.status_label.config(text="Sample data loaded.")
        self.controller.refresh_dashboard_and_history()
