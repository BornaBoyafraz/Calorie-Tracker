"""Main Tkinter application window."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, simpledialog, ttk

from calory_tracker.models import MealEntry
from calory_tracker.services import CalorieService, StorageService, UserService, sanitize_username
from calory_tracker.ui.theme import configure_theme
from calory_tracker.ui.views.dashboard_view import DashboardView
from calory_tracker.ui.views.history_view import HistoryView
from calory_tracker.ui.views.log_view import LogView
from calory_tracker.ui.views.settings_view import SettingsView


class CaloryTrackerApp(tk.Tk):
    """Desktop application shell containing navigation and all views."""

    def __init__(self):
        super().__init__()
        self.title("Calory Tracker")
        self.geometry("1220x760")
        self.minsize(980, 640)

        configure_theme(self)

        self.storage = StorageService()
        self.service = UserService(self.storage, CalorieService())

        self.user_data = self._load_user_context()
        if self.user_data is None:
            self.destroy()
            return

        self.views: dict[str, ttk.Frame] = {}
        self.nav_buttons: dict[str, ttk.Button] = {}
        self.active_view = "Dashboard"

        self._build_shell()
        self._bind_shortcuts()
        self.refresh_all_views()

    def _load_user_context(self):
        while True:
            username = simpledialog.askstring(
                "Welcome to Calory Tracker",
                "Enter your first and last name:",
                parent=self,
            )
            if username is None:
                return None

            normalized = sanitize_username(username)
            if not normalized:
                messagebox.showerror("Invalid name", "Please provide a valid name.")
                continue

            return self.service.load_user(normalized)

    def _build_shell(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ttk.Label(header, text="Calory Tracker", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text=f"User: {self.user_data.username.replace('_', ' ').title()}",
            style="Subheading.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=220)
        sidebar.grid(row=1, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(10, weight=1)

        nav_items = [
            ("Dashboard", "Overview"),
            ("Log Entries", "Meals"),
            ("History", "Timeline"),
            ("Settings", "Preferences"),
        ]

        ttk.Label(
            sidebar,
            text="Sections",
            foreground="#9FB4D9",
            background="#0B1C3A",
            font=("Segoe UI Semibold", 10),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(18, 8))

        for idx, (name, subtitle) in enumerate(nav_items, start=1):
            button = ttk.Button(
                sidebar,
                text=f"{name}\n{subtitle}",
                style="Sidebar.TButton",
                command=lambda key=name: self.show_view(key),
            )
            button.grid(row=idx, column=0, sticky="ew", padx=10, pady=4)
            self.nav_buttons[name] = button

        content = ttk.Frame(self, style="App.TFrame")
        content.grid(row=1, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.views = {
            "Dashboard": DashboardView(content, self),
            "Log Entries": LogView(content, self),
            "History": HistoryView(content, self),
            "Settings": SettingsView(content, self),
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        self.show_view("Dashboard")

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-1>", lambda _event: self.show_view("Dashboard"))
        self.bind("<Control-2>", lambda _event: self.show_view("Log Entries"))
        self.bind("<Control-3>", lambda _event: self.show_view("History"))
        self.bind("<Control-4>", lambda _event: self.show_view("Settings"))
        self.bind("<Control-n>", lambda _event: self.open_add_entry())
        self.bind("<Control-r>", lambda _event: self.refresh_all_views())

    def show_view(self, view_name: str) -> None:
        self.active_view = view_name
        self.views[view_name].tkraise()
        for name, button in self.nav_buttons.items():
            button.configure(style="SidebarActive.TButton" if name == view_name else "Sidebar.TButton")

        refresh = getattr(self.views[view_name], "refresh", None)
        if callable(refresh):
            refresh()

    def refresh_all_views(self) -> None:
        for view in self.views.values():
            refresh = getattr(view, "refresh", None)
            if callable(refresh):
                refresh()

    def refresh_dashboard_and_history(self) -> None:
        for key in ("Dashboard", "History"):
            refresh = getattr(self.views[key], "refresh", None)
            if callable(refresh):
                refresh()

    def today_iso(self) -> str:
        return date.today().isoformat()

    def get_dashboard_summary(self):
        return self.service.build_dashboard(self.user_data)

    def get_log_entries(self) -> list[MealEntry]:
        return sorted(
            self.user_data.entries,
            key=lambda entry: (entry.consumed_on, entry.entry_id),
            reverse=True,
        )

    def get_history_entries(self, query: str = "", start_date: str = "", end_date: str = "") -> list[MealEntry]:
        return self.service.filter_history(self.user_data, query, start_date, end_date)

    def add_entry(self, payload: dict[str, str]) -> None:
        self.service.add_entry(self.user_data, payload)

    def update_entry(self, entry_id: str, payload: dict[str, str]) -> None:
        self.service.update_entry(self.user_data, entry_id, payload)

    def delete_entry(self, entry_id: str) -> None:
        self.service.delete_entry(self.user_data, entry_id)

    def find_entry(self, entry_id: str) -> MealEntry | None:
        for entry in self.user_data.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def update_settings(self, payload: dict[str, str]) -> None:
        self.service.save_settings(self.user_data, payload)

    def export_data(self, path: str) -> None:
        self.service.export_user(self.user_data, path)

    def load_sample_data(self, overwrite: bool) -> None:
        self.service.seed_sample_data(self.user_data, overwrite=overwrite)

    def lookup_meal_calories(self, meal_name: str) -> int | None:
        return self.service.meal_calories_from_catalog(meal_name)

    def save_meal_to_catalog(self, meal_name: str, calories: int) -> None:
        self.service.save_meal_to_catalog(meal_name, calories)

    def open_add_entry(self) -> None:
        self.show_view("Log Entries")
        log_view = self.views["Log Entries"]
        focus_add = getattr(log_view, "focus_add_shortcut", None)
        if callable(focus_add):
            focus_add()


def run_app() -> None:
    app = CaloryTrackerApp()
    if app.user_data is not None:
        app.mainloop()
