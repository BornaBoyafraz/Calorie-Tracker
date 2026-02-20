"""Centralized visual theme configuration for Tkinter widgets."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

APP_BACKGROUND = "#F1F5F9"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#E2E8F0"
TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#475569"
ACCENT = "#2563EB"
ACCENT_DARK = "#1D4ED8"
SUCCESS = "#059669"
DANGER = "#DC2626"


def configure_theme(root: tk.Tk) -> None:
    """Configures ttk styles so views share one visual language."""

    root.configure(bg=APP_BACKGROUND)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("App.TFrame", background=APP_BACKGROUND)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure("Sidebar.TFrame", background="#0B1C3A")
    style.configure("Header.TFrame", background=SURFACE)

    style.configure(
        "App.TLabel",
        background=APP_BACKGROUND,
        foreground=TEXT_PRIMARY,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Surface.TLabel",
        background=SURFACE,
        foreground=TEXT_PRIMARY,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Heading.TLabel",
        background=SURFACE,
        foreground=TEXT_PRIMARY,
        font=("Segoe UI Semibold", 18),
    )
    style.configure(
        "Subheading.TLabel",
        background=SURFACE,
        foreground=TEXT_MUTED,
        font=("Segoe UI", 10),
    )
    style.configure(
        "CardTitle.TLabel",
        background=SURFACE,
        foreground=TEXT_MUTED,
        font=("Segoe UI Semibold", 10),
    )
    style.configure(
        "CardValue.TLabel",
        background=SURFACE,
        foreground=TEXT_PRIMARY,
        font=("Segoe UI Semibold", 24),
    )

    style.configure(
        "Primary.TButton",
        font=("Segoe UI Semibold", 10),
        background=ACCENT,
        foreground="#FFFFFF",
        borderwidth=0,
        focusthickness=3,
        focuscolor=ACCENT_DARK,
        padding=(12, 8),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
        foreground=[("disabled", "#CBD5E1")],
    )

    style.configure(
        "Ghost.TButton",
        font=("Segoe UI", 10),
        background=SURFACE,
        foreground=TEXT_PRIMARY,
        bordercolor=SURFACE_ALT,
        borderwidth=1,
        padding=(10, 8),
    )
    style.map(
        "Ghost.TButton",
        background=[("active", "#EEF2FF")],
        bordercolor=[("active", ACCENT)],
    )

    style.configure(
        "Sidebar.TButton",
        font=("Segoe UI Semibold", 10),
        background="#0B1C3A",
        foreground="#D1D9EA",
        borderwidth=0,
        padding=(16, 10),
        anchor="w",
    )
    style.map(
        "Sidebar.TButton",
        background=[("active", "#123166"), ("pressed", "#123166")],
        foreground=[("active", "#FFFFFF")],
    )

    style.configure(
        "SidebarActive.TButton",
        font=("Segoe UI Semibold", 10),
        background="#123166",
        foreground="#FFFFFF",
        borderwidth=0,
        padding=(16, 10),
        anchor="w",
    )

    style.configure(
        "App.Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=TEXT_PRIMARY,
        bordercolor="#D7DEE9",
        borderwidth=1,
        rowheight=28,
        font=("Segoe UI", 10),
    )
    style.configure(
        "App.Treeview.Heading",
        background="#EEF2FF",
        foreground=TEXT_PRIMARY,
        font=("Segoe UI Semibold", 10),
        bordercolor="#D7DEE9",
    )

    style.configure(
        "App.TEntry",
        fieldbackground="#FFFFFF",
        foreground=TEXT_PRIMARY,
        bordercolor="#CBD5E1",
        lightcolor="#CBD5E1",
        darkcolor="#CBD5E1",
        padding=(8, 7),
    )
    style.configure(
        "App.TCombobox",
        fieldbackground="#FFFFFF",
        foreground=TEXT_PRIMARY,
        bordercolor="#CBD5E1",
        lightcolor="#CBD5E1",
        darkcolor="#CBD5E1",
        padding=(6, 5),
    )
