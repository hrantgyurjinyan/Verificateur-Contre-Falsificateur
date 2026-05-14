"""
setup_frame.py
==============
Game setup screen — enter formula, variables, N.
"""

import tkinter as tk

from formula import make_formula
from theme import (BG, PANEL, BORDER, ACCENT,
                   SANS, SANS_B, SANS_SM)


class SetupFrame(tk.Frame):
    """
    Start screen: the user enters game parameters.
    On clicking "Start", calls on_start(N, V_vars, F_vars,
                                        formula_fn, formula_raw).
    """

    def __init__(self, master, on_start):
        super().__init__(master, bg=BG)
        self.on_start = on_start
        self._build()

    def _build(self):
        wrap = tk.Frame(self, bg=PANEL,
                        highlightbackground=BORDER,
                        highlightthickness=1)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(wrap, text="Verificator vs Falsificator",
                 bg=PANEL, font=("Segoe UI", 16, "bold"),
                 fg="#2c2c2a").pack(padx=40, pady=(28, 2))
        tk.Label(wrap, text="Two-player turn-based game",
                 bg=PANEL, font=SANS_SM,
                 fg="#888780").pack(pady=(0, 16))

        def row(label, default):
            tk.Label(wrap, text=label, bg=PANEL,
                     font=SANS_SM, fg="#444441",
                     anchor="w").pack(fill="x", padx=30, pady=(0, 2))
            e = tk.Entry(wrap, font=SANS, relief="flat",
                         bg="#f1efe8", fg="#2c2c2a",
                         highlightbackground=BORDER,
                         highlightthickness=1)
            e.insert(0, default)
            e.pack(fill="x", padx=30, pady=(0, 10))
            return e

        self.e_N       = row("Number of variables N", "4")
        self.e_V       = row("Verificator variables (space-separated)", "1 3")
        self.e_formula = row("Formula  (x1, x2, …, xN)",
                             "(x1 or x2) and (x3 or x4)")

        # Quick operator insertion buttons
        tk.Label(wrap, text="Operators:", bg=PANEL,
                 font=("Segoe UI", 8),
                 fg="#888780").pack(padx=30, anchor="w")

        ops_f = tk.Frame(wrap, bg=PANEL)
        ops_f.pack(padx=30, fill="x", pady=(0, 14))

        for i, (lbl, ins) in enumerate([
            ("and",  " and "),
            ("or",   " or "),
            ("not",  " not "),
            ("xor",  " xor "),
            ("→",    " implies "),
            ("↔",    " iff "),
        ]):
            tk.Button(
                ops_f, text=lbl, font=("Segoe UI", 9),
                relief="flat", bg="#e8e6e0", fg="#2c2c2a",
                cursor="hand2", padx=6, pady=3,
                command=lambda t=ins: self._insert_op(t)
            ).grid(row=i // 3, column=i % 3,
                   padx=2, pady=2, sticky="ew")

        ops_f.columnconfigure(0, weight=1)
        ops_f.columnconfigure(1, weight=1)
        ops_f.columnconfigure(2, weight=1)

        self.lbl_err = tk.Label(
            wrap, text="", bg=PANEL,
            font=SANS_SM, fg="#791f1f", wraplength=320)
        self.lbl_err.pack(padx=30)

        tk.Button(
            wrap, text="Start game →",
            font=SANS_B, bg=ACCENT, fg="white",
            activebackground="#2555a0", activeforeground="white",
            relief="flat", cursor="hand2", padx=10, pady=10,
            command=self._start
        ).pack(fill="x", padx=30, pady=(8, 30))

    def _insert_op(self, text: str):
        self.e_formula.focus_set()
        self.e_formula.insert(tk.INSERT, text)

    def _start(self):
        # ── Validate N ─────────────────────────────────────
        try:
            N = int(self.e_N.get().strip())
            if N < 1:
                raise ValueError
        except ValueError:
            self.lbl_err.config(text="N must be an integer ≥ 1")
            return

        # ── Validate formula ───────────────────────────────
        formula_raw = self.e_formula.get().strip()
        if not formula_raw:
            self.lbl_err.config(text="Please enter a formula")
            return

        try:
            formula_fn, _ = make_formula(formula_raw)
            formula_fn({i: False for i in range(1, N + 1)})
        except Exception as e:
            self.lbl_err.config(text=f"Formula error: {e}")
            return

        # ── Validate V variables ───────────────────────────
        try:
            V_vars = sorted(map(int, self.e_V.get().strip().split()))
        except ValueError:
            self.lbl_err.config(
                text="V variables must be space-separated numbers")
            return

        if any(v < 1 or v > N for v in V_vars):
            self.lbl_err.config(
                text=f"V variables must be between 1 and {N}")
            return

        F_vars = sorted(i for i in range(1, N + 1)
                        if i not in V_vars)
        self.on_start(N, V_vars, F_vars, formula_fn, formula_raw)