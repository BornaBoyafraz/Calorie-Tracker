"""Dashboard screen showing today's summary and weekly trend."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from calory_tracker.ui.theme import ACCENT, DANGER, SURFACE, TEXT_MUTED, TEXT_PRIMARY


class DashboardView(ttk.Frame):
    """Home screen with KPI cards and weekly calorie chart."""

    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent, style="Surface.TFrame", padding=20)
        self.controller = controller

        self.today_value = tk.StringVar(value="0 kcal")
        self.remaining_value = tk.StringVar(value="0 kcal")
        self.macros_value = tk.StringVar(value="P 0g | C 0g | F 0g")
        self.goal_value = tk.StringVar(value="Goal: 0 kcal")

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ttk.Frame(self, style="Surface.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)
        ttk.Label(header, text="Dashboard", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Track calories, macros, and trends from one place.",
            style="Subheading.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        cards = ttk.Frame(self, style="Surface.TFrame")
        cards.grid(row=1, column=0, sticky="ew")
        for idx in range(3):
            cards.grid_columnconfigure(idx, weight=1)

        self._build_card(cards, 0, "Today's Calories", self.today_value, self.goal_value)
        self._build_card(cards, 1, "Remaining", self.remaining_value, tk.StringVar(value=""))
        self._build_card(cards, 2, "Macros", self.macros_value, tk.StringVar(value=""))

        chart_card = ttk.Frame(self, style="Surface.TFrame", padding=16)
        chart_card.grid(row=2, column=0, sticky="nsew", pady=(16, 0))
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(1, weight=1)

        ttk.Label(chart_card, text="Weekly Calories", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.chart_canvas = tk.Canvas(
            chart_card,
            background=SURFACE,
            highlightthickness=0,
            relief="flat",
            height=260,
        )
        self.chart_canvas.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.empty_state = ttk.Label(
            chart_card,
            text="No entries yet. Add your first meal in Log Entries.",
            style="Subheading.TLabel",
        )
        self.empty_state.grid(row=1, column=0)

        self.chart_canvas.bind("<Configure>", lambda _event: self.refresh())

    def _build_card(self, parent: ttk.Frame, column: int, title: str, value_var: tk.StringVar, sub_var: tk.StringVar) -> None:
        card = ttk.Frame(parent, style="Surface.TFrame", padding=16)
        card.grid(row=0, column=column, sticky="nsew", padx=(0, 12 if column < 2 else 0))
        ttk.Label(card, text=title, style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(card, textvariable=value_var, style="CardValue.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 4))
        ttk.Label(card, textvariable=sub_var, style="Subheading.TLabel").grid(row=2, column=0, sticky="w")

    def refresh(self) -> None:
        summary = self.controller.get_dashboard_summary()

        self.today_value.set(f"{summary.today_total} kcal")
        self.goal_value.set(f"Goal: {summary.goal} kcal")

        remaining_prefix = "Remaining"
        if summary.remaining < 0:
            remaining_prefix = "Over"

        self.remaining_value.set(f"{remaining_prefix}: {abs(summary.remaining)} kcal")
        self.macros_value.set(f"P {summary.protein}g | C {summary.carbs}g | F {summary.fat}g")

        self._draw_chart(summary.weekly_totals, summary.goal)

    def _draw_chart(self, points: list[tuple[str, int]], goal: int) -> None:
        canvas = self.chart_canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 300)
        height = max(canvas.winfo_height(), 220)

        non_zero = any(total > 0 for _, total in points)
        if not points or not non_zero:
            self.empty_state.lift()
            return

        self.empty_state.lower()

        left = 40
        right = width - 20
        top = 20
        bottom = height - 40

        max_total = max(max(total for _, total in points), goal, 1)
        bar_width = max(18, int((right - left) / (len(points) * 1.5)))
        step = (right - left) / max(len(points), 1)

        canvas.create_line(left, bottom, right, bottom, fill="#CBD5E1", width=2)

        if goal > 0:
            y_goal = bottom - ((goal / max_total) * (bottom - top))
            canvas.create_line(left, y_goal, right, y_goal, fill="#94A3B8", dash=(4, 4))
            canvas.create_text(right - 2, y_goal - 8, text=f"goal {goal}", fill=TEXT_MUTED, anchor="e", font=("Segoe UI", 9))

        for idx, (day_iso, total) in enumerate(points):
            x_center = left + step * (idx + 0.5)
            x0 = x_center - bar_width / 2
            x1 = x_center + bar_width / 2
            bar_height = (total / max_total) * (bottom - top)
            y0 = bottom - bar_height

            bar_color = ACCENT if total <= goal else DANGER
            canvas.create_rectangle(x0, y0, x1, bottom, fill=bar_color, outline="")
            canvas.create_text(x_center, y0 - 10, text=str(total), fill=TEXT_PRIMARY, font=("Segoe UI", 9))
            canvas.create_text(
                x_center,
                bottom + 14,
                text=day_iso[5:],
                fill=TEXT_MUTED,
                font=("Segoe UI", 9),
            )
