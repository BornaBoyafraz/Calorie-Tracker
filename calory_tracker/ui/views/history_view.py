"""History screen with date-range and text filters."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class HistoryView(ttk.Frame):
    """Lists historical entries with filters."""

    COLUMNS = ("date", "meal", "calories", "protein", "carbs", "fat", "type", "notes")

    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent, style="Surface.TFrame", padding=20)
        self.controller = controller

        self.search_var = tk.StringVar(value="")
        self.start_var = tk.StringVar(value="")
        self.end_var = tk.StringVar(value="")

        self.empty_state = ttk.Label(
            self,
            text="No history entries match this filter.",
            style="Subheading.TLabel",
        )

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ttk.Frame(self, style="Surface.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="History", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Filter entries by date range and search term.",
            style="Subheading.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        controls = ttk.Frame(self, style="Surface.TFrame")
        controls.grid(row=1, column=0, sticky="ew", pady=(12, 12))
        controls.grid_columnconfigure(8, weight=1)

        ttk.Label(controls, text="From", style="Surface.TLabel").grid(row=0, column=0, padx=(0, 6))
        ttk.Entry(controls, textvariable=self.start_var, width=12, style="App.TEntry").grid(row=0, column=1)

        ttk.Label(controls, text="To", style="Surface.TLabel").grid(row=0, column=2, padx=(12, 6))
        ttk.Entry(controls, textvariable=self.end_var, width=12, style="App.TEntry").grid(row=0, column=3)

        ttk.Label(controls, text="Search", style="Surface.TLabel").grid(row=0, column=4, padx=(12, 6))
        search_entry = ttk.Entry(controls, textvariable=self.search_var, width=24, style="App.TEntry")
        search_entry.grid(row=0, column=5)

        ttk.Button(controls, text="Apply", style="Primary.TButton", command=self.apply_filters).grid(
            row=0,
            column=6,
            padx=(12, 6),
        )
        ttk.Button(controls, text="Clear", style="Ghost.TButton", command=self.clear_filters).grid(row=0, column=7)

        self.result_label = ttk.Label(controls, text="", style="Subheading.TLabel")
        self.result_label.grid(row=0, column=8, sticky="e")

        table_wrap = ttk.Frame(self, style="Surface.TFrame")
        table_wrap.grid(row=2, column=0, sticky="nsew")
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_wrap, columns=self.COLUMNS, show="headings", style="App.Treeview")
        widths = {
            "date": 110,
            "meal": 140,
            "calories": 80,
            "protein": 70,
            "carbs": 70,
            "fat": 70,
            "type": 110,
            "notes": 280,
        }

        for column in self.COLUMNS:
            self.tree.heading(column, text=column.title())
            self.tree.column(column, width=widths[column], stretch=column in {"meal", "notes"})

        self.tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)

        self.empty_state.grid(row=2, column=0)
        search_entry.bind("<Return>", lambda _event: self.apply_filters())

    def refresh(self) -> None:
        self.apply_filters(show_errors=False)

    def apply_filters(self, show_errors: bool = True) -> None:
        try:
            entries = self.controller.get_history_entries(
                query=self.search_var.get(),
                start_date=self.start_var.get(),
                end_date=self.end_var.get(),
            )
        except ValueError as exc:
            if show_errors:
                messagebox.showerror("Invalid filter", str(exc))
            return

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
                    entry.notes,
                ),
            )

        self.result_label.config(text=f"{len(entries)} result(s)")
        if entries:
            self.empty_state.lower()
        else:
            self.empty_state.lift()

    def clear_filters(self) -> None:
        self.search_var.set("")
        self.start_var.set("")
        self.end_var.set("")
        self.apply_filters(show_errors=False)
