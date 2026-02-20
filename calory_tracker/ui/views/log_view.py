"""Meal logging screen with add, edit, and delete flows."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from calory_tracker.models import MealEntry


class LogView(ttk.Frame):
    """Shows entry table and CRUD actions."""

    COLUMNS = ("date", "meal", "calories", "protein", "carbs", "fat", "type")

    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent, style="Surface.TFrame", padding=20)
        self.controller = controller

        self.empty_state = ttk.Label(
            self,
            text="No meals logged yet. Click 'Add Meal' to start your first entry.",
            style="Subheading.TLabel",
        )

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ttk.Frame(self, style="Surface.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ttk.Label(header, text="Log Entries", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Add, edit, and remove meals for each day.", style="Subheading.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 0),
        )

        button_row = ttk.Frame(self, style="Surface.TFrame")
        button_row.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        ttk.Button(button_row, text="+ Add Meal", style="Primary.TButton", command=self.open_add_dialog).pack(
            side="left"
        )
        ttk.Button(button_row, text="Edit Selected", style="Ghost.TButton", command=self.open_edit_dialog).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(button_row, text="Delete Selected", style="Ghost.TButton", command=self.delete_selected).pack(
            side="left", padx=(8, 0)
        )

        table_wrap = ttk.Frame(self, style="Surface.TFrame")
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_wrap, columns=self.COLUMNS, show="headings", style="App.Treeview")
        headings = {
            "date": "Date",
            "meal": "Meal",
            "calories": "Calories",
            "protein": "Protein",
            "carbs": "Carbs",
            "fat": "Fat",
            "type": "Type",
        }
        widths = {
            "date": 110,
            "meal": 180,
            "calories": 90,
            "protein": 90,
            "carbs": 90,
            "fat": 90,
            "type": 110,
        }

        for column in self.COLUMNS:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], stretch=column == "meal")

        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)

        self.empty_state.grid(row=2, column=0)
        self.tree.bind("<Double-1>", lambda _event: self.open_edit_dialog())

    def refresh(self) -> None:
        entries = self.controller.get_log_entries()
        self.tree.delete(*self.tree.get_children())

        for entry in entries:
            self.tree.insert(
                "",
                "end",
                iid=entry.entry_id,
                values=(
                    entry.consumed_on,
                    entry.meal_name,
                    entry.calories,
                    entry.protein,
                    entry.carbs,
                    entry.fat,
                    entry.meal_type,
                ),
            )

        if entries:
            self.empty_state.lower()
        else:
            self.empty_state.lift()

    def focus_add_shortcut(self) -> None:
        self.open_add_dialog()

    def open_add_dialog(self) -> None:
        EntryDialog(self, self.controller, title="Add Meal", on_submit=self.controller.add_entry)

    def open_edit_dialog(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select a meal entry to edit.")
            return

        entry = self.controller.find_entry(selected[0])
        if entry is None:
            messagebox.showerror("Not found", "The selected entry could not be found.")
            self.refresh()
            return

        EntryDialog(
            self,
            self.controller,
            title="Edit Meal",
            existing_entry=entry,
            on_submit=lambda payload: self.controller.update_entry(entry.entry_id, payload),
        )

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select a meal entry to delete.")
            return

        entry = self.controller.find_entry(selected[0])
        if entry is None:
            self.refresh()
            return

        confirmed = messagebox.askyesno(
            "Delete entry",
            f"Delete '{entry.meal_name}' from {entry.consumed_on}? This action cannot be undone.",
        )
        if not confirmed:
            return

        try:
            self.controller.delete_entry(entry.entry_id)
            self.refresh()
        except ValueError as exc:
            messagebox.showerror("Delete failed", str(exc))


class EntryDialog(tk.Toplevel):
    """Modal dialog for adding or editing one meal entry."""

    def __init__(
        self,
        parent: LogView,
        controller,
        title: str,
        on_submit,
        existing_entry: MealEntry | None = None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.on_submit = on_submit
        self.existing_entry = existing_entry

        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.meal_var = tk.StringVar(value=existing_entry.meal_name if existing_entry else "")
        self.calories_var = tk.StringVar(value=str(existing_entry.calories) if existing_entry else "")
        self.protein_var = tk.StringVar(value=str(existing_entry.protein) if existing_entry else "0")
        self.carbs_var = tk.StringVar(value=str(existing_entry.carbs) if existing_entry else "0")
        self.fat_var = tk.StringVar(value=str(existing_entry.fat) if existing_entry else "0")
        self.date_var = tk.StringVar(value=existing_entry.consumed_on if existing_entry else self.controller.today_iso())
        self.meal_type_var = tk.StringVar(value=existing_entry.meal_type if existing_entry else "Meal")

        self.notes_text = tk.Text(self, height=4, width=30, wrap="word", font=("Segoe UI", 10))

        self._build_ui()

        if existing_entry:
            self.notes_text.insert("1.0", existing_entry.notes)

        self.bind("<Return>", lambda _event: self._submit())
        self.bind("<Escape>", lambda _event: self.destroy())

    def _build_ui(self) -> None:
        shell = ttk.Frame(self, style="Surface.TFrame", padding=16)
        shell.grid(row=0, column=0, sticky="nsew")

        labels = [
            ("Date (YYYY-MM-DD)", self.date_var),
            ("Meal Name", self.meal_var),
            ("Calories", self.calories_var),
            ("Protein (g)", self.protein_var),
            ("Carbs (g)", self.carbs_var),
            ("Fat (g)", self.fat_var),
        ]

        for row_idx, (label, variable) in enumerate(labels):
            ttk.Label(shell, text=label, style="Surface.TLabel").grid(row=row_idx, column=0, sticky="w", pady=(0, 2))
            ttk.Entry(shell, textvariable=variable, style="App.TEntry", width=34).grid(
                row=row_idx,
                column=1,
                sticky="ew",
                pady=(0, 10),
            )

        type_row = len(labels)
        ttk.Label(shell, text="Meal Type", style="Surface.TLabel").grid(row=type_row, column=0, sticky="w", pady=(0, 2))
        ttk.Combobox(
            shell,
            textvariable=self.meal_type_var,
            values=("Breakfast", "Lunch", "Dinner", "Snack", "Meal"),
            state="readonly",
            style="App.TCombobox",
            width=31,
        ).grid(row=type_row, column=1, sticky="ew", pady=(0, 10))

        notes_row = type_row + 1
        ttk.Label(shell, text="Notes", style="Surface.TLabel").grid(row=notes_row, column=0, sticky="nw", pady=(0, 2))
        self.notes_text.grid(row=notes_row, column=1, sticky="ew", pady=(0, 10))

        helper_row = notes_row + 1
        ttk.Button(
            shell,
            text="Lookup calories from foods.txt",
            style="Ghost.TButton",
            command=self._lookup_calories,
        ).grid(row=helper_row, column=1, sticky="w", pady=(0, 10))

        button_row = helper_row + 1
        actions = ttk.Frame(shell, style="Surface.TFrame")
        actions.grid(row=button_row, column=0, columnspan=2, sticky="e")
        ttk.Button(actions, text="Cancel", style="Ghost.TButton", command=self.destroy).pack(side="left")
        ttk.Button(actions, text="Save", style="Primary.TButton", command=self._submit).pack(side="left", padx=(8, 0))

        shell.grid_columnconfigure(1, weight=1)

    def _lookup_calories(self) -> None:
        meal = self.meal_var.get().strip()
        if not meal:
            messagebox.showinfo("Meal required", "Enter a meal name first.")
            return

        calories = self.controller.lookup_meal_calories(meal)
        if calories is None:
            messagebox.showinfo(
                "Not found",
                "Meal was not found in foods.txt. You can save it from this dialog after entering calories.",
            )
            return

        self.calories_var.set(str(calories))

    def _submit(self) -> None:
        payload = {
            "consumed_on": self.date_var.get(),
            "meal_name": self.meal_var.get(),
            "calories": self.calories_var.get(),
            "protein": self.protein_var.get(),
            "carbs": self.carbs_var.get(),
            "fat": self.fat_var.get(),
            "meal_type": self.meal_type_var.get(),
            "notes": self.notes_text.get("1.0", "end").strip(),
        }

        try:
            self.on_submit(payload)
            calories = int(payload["calories"])
            meal_name = payload["meal_name"]
            should_save = messagebox.askyesno(
                "Save to foods database",
                "Save this meal and calories to foods.txt for quick lookup next time?",
            )
            if should_save:
                self.controller.save_meal_to_catalog(meal_name, calories)
        except ValueError as exc:
            messagebox.showerror("Validation error", str(exc))
            return

        self.parent.refresh()
        self.controller.refresh_dashboard_and_history()
        self.destroy()
