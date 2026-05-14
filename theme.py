"""
theme.py
========
Colors and fonts for the entire application.
Import in any UI module:

  from theme import BG, PANEL, V_COLOR, MONO, ...
"""

# ── Backgrounds ────────────────────────────────────────────
BG      = "#f8f7f4"   # window background
PANEL   = "#ffffff"   # panel background
BORDER  = "#e0ddd6"   # border
ACCENT  = "#3266ad"   # accent blue (Start button)

# ── Players ────────────────────────────────────────────────
V_COLOR = "#1a6fa8"   # Verificator  — blue
F_COLOR = "#b85c00"   # Falsificator — orange

# ── Result ─────────────────────────────────────────────────
WIN_BG  = "#eaf3de"
WIN_FG  = "#27500a"
LOSE_BG = "#fcebeb"
LOSE_FG = "#791f1f"

# ── Additional backgrounds ─────────────────────────────────
TREE_BG = "#f1efe8"   # strategy tree / move history background

# ── Fonts ──────────────────────────────────────────────────
MONO   = ("Courier New", 10)
SANS   = ("Segoe UI",    10)
SANS_B = ("Segoe UI",    10, "bold")
SANS_SM= ("Segoe UI",     9)
SANS_LG= ("Segoe UI",    13, "bold")