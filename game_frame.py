"""
game_frame.py
=============
Step-by-step two-player game screen.
"""

import tkinter as tk
from tkinter import scrolledtext

from theme  import (BG, PANEL, BORDER, ACCENT,
                    V_COLOR, F_COLOR,
                    WIN_BG, WIN_FG, LOSE_BG, LOSE_FG, TREE_BG,
                    MONO, SANS, SANS_B, SANS_SM, SANS_LG)
from formula import filter_rows, all_rows
from engine  import build_turn_order, eval_move


class GameFrame(tk.Frame):
    """
    Main game screen.

    Parameters:
      master      — parent widget
      N           — number of variables
      V_vars      — list of Verificator's variables
      F_vars      — list of Falsificator's variables
      formula_fn  — callable(x: dict) -> bool
      formula_raw — original formula string (for display)
      on_restart  — callback to return to SetupFrame
    """

    def __init__(self, master, N, V_vars, F_vars,
                 formula_fn, formula_raw, on_restart):
        super().__init__(master, bg=BG)

        self.N           = N
        self.V_vars      = V_vars
        self.F_vars      = F_vars
        self.formula     = formula_fn
        self.formula_raw = formula_raw
        self.on_restart  = on_restart

        self.turn_order  = build_turn_order(V_vars, F_vars)
        self.all_data    = all_rows(N, formula_fn)

        self.v_remaining = list(V_vars)
        self.f_remaining = list(F_vars)
        self.assigned    = {}    # {var_idx: bool}
        self.history     = []    # [(player, var, val), ...]
        self.turn_idx    = 0
        self.game_over   = False

        self._build()
        self._refresh()

    # ══════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════

    def _build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    # ── Left panel ─────────────────────────────────────────

    def _build_left_panel(self):
        left = tk.Frame(self, bg=PANEL,
                        highlightbackground=BORDER,
                        highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew",
                  padx=(12, 6), pady=12)
        left.columnconfigure(0, weight=1)

        # Header
        tk.Label(left, text="Verificator vs Falsificator",
                 bg=PANEL, font=("Segoe UI", 11, "bold"),
                 fg="#2c2c2a").pack(
            anchor="w", padx=14, pady=(14, 0))
        tk.Label(left, text=f"Formula: {self.formula_raw}",
                 bg=PANEL, font=("Courier New", 9),
                 fg="#888780", wraplength=230).pack(
            anchor="w", padx=14, pady=(2, 6))

        tk.Frame(left, bg=BORDER, height=1).pack(
            fill="x", padx=14, pady=4)

        # Player labels
        tk.Label(left, text="PLAYERS", bg=PANEL,
                 font=("Segoe UI", 8, "bold"),
                 fg="#888780").pack(
            anchor="w", padx=14, pady=(8, 2))
        self.lbl_V = tk.Label(left, bg=PANEL, font=SANS, anchor="w")
        self.lbl_V.pack(fill="x", padx=14, pady=1)
        self.lbl_F = tk.Label(left, bg=PANEL, font=SANS, anchor="w")
        self.lbl_F.pack(fill="x", padx=14, pady=1)

        tk.Frame(left, bg=BORDER, height=1).pack(
            fill="x", padx=14, pady=(8, 4))

        # Whose turn
        tk.Label(left, text="TURN", bg=PANEL,
                 font=("Segoe UI", 8, "bold"),
                 fg="#888780").pack(
            anchor="w", padx=14, pady=(4, 2))
        self.lbl_whose_turn = tk.Label(
            left, bg=PANEL, font=SANS_LG, wraplength=220)
        self.lbl_whose_turn.pack(
            anchor="w", padx=14, pady=(0, 10))

        # Variable selection
        tk.Label(left, text="Choose a variable:", bg=PANEL,
                 font=SANS_SM, fg="#444441").pack(
            anchor="w", padx=14)
        self.var_buttons_frame = tk.Frame(left, bg=PANEL)
        self.var_buttons_frame.pack(
            fill="x", padx=14, pady=(4, 10))
        self.selected_var = tk.IntVar(value=-1)

        # Value selection
        tk.Label(left, text="Value:", bg=PANEL,
                 font=SANS_SM, fg="#444441").pack(
            anchor="w", padx=14)
        self.val_var = tk.StringVar(value="True")
        val_frame = tk.Frame(left, bg=PANEL)
        val_frame.pack(fill="x", padx=14, pady=(4, 12))

        self.rb_true = tk.Radiobutton(
            val_frame, text="True",
            variable=self.val_var, value="True",
            bg=PANEL, font=SANS, fg="#27500a",
            activebackground=PANEL, selectcolor=WIN_BG)
        self.rb_true.pack(side="left", padx=(0, 16))

        self.rb_false = tk.Radiobutton(
            val_frame, text="False",
            variable=self.val_var, value="False",
            bg=PANEL, font=SANS, fg="#791f1f",
            activebackground=PANEL, selectcolor=LOSE_BG)
        self.rb_false.pack(side="left")

        self.btn_move = tk.Button(
            left, text="Make move →",
            font=SANS_B, bg=ACCENT, fg="white",
            activebackground="#2555a0", activeforeground="white",
            relief="flat", cursor="hand2", padx=10, pady=8,
            command=self._make_move)
        self.btn_move.pack(fill="x", padx=14, pady=(0, 4))

        self.lbl_move_err = tk.Label(
            left, text="", bg=PANEL,
            font=SANS_SM, fg="#791f1f", wraplength=220)
        self.lbl_move_err.pack(padx=14)

        tk.Frame(left, bg=BORDER, height=1).pack(
            fill="x", padx=14, pady=(8, 4))

        # Move history
        tk.Label(left, text="MOVE HISTORY", bg=PANEL,
                 font=("Segoe UI", 8, "bold"),
                 fg="#888780").pack(
            anchor="w", padx=14, pady=(4, 2))

        self.txt_history = scrolledtext.ScrolledText(
            left, font=("Courier New", 9), bg=TREE_BG,
            fg="#2c2c2a", relief="flat", bd=0,
            wrap="none", state="disabled",
            height=10, width=26)
        self.txt_history.pack(
            fill="both", expand=True, padx=10, pady=(0, 4))
        self.txt_history.tag_config(
            "v", foreground=V_COLOR,
            font=("Courier New", 9, "bold"))
        self.txt_history.tag_config(
            "f", foreground=F_COLOR,
            font=("Courier New", 9, "bold"))

        tk.Button(
            left, text="↩ New game",
            font=SANS_SM, bg="#f1efe8", fg="#444441",
            activebackground=BORDER, relief="flat",
            cursor="hand2", padx=8, pady=5,
            command=self.on_restart
        ).pack(fill="x", padx=14, pady=(4, 14))

    # ── Right panel ────────────────────────────────────────

    def _build_right_panel(self):
        right = tk.Frame(self, bg=BG)
        right.grid(row=0, column=1, sticky="nsew",
                   padx=(0, 12), pady=12)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=3)
        right.rowconfigure(4, weight=2)

        # Info bar
        self.info_frame = tk.Frame(
            right, bg=PANEL,
            highlightbackground=BORDER, highlightthickness=1)
        self.info_frame.grid(
            row=0, column=0, sticky="ew", pady=(0, 8))
        self.lbl_info = tk.Label(
            self.info_frame, bg=PANEL, font=SANS,
            fg="#2c2c2a", wraplength=520,
            justify="left", padx=14, pady=10)
        self.lbl_info.pack(anchor="w")

        tk.Label(right, text="Compatible assignments",
                 bg=BG, font=SANS_B,
                 fg="#444441").grid(
            row=1, column=0, sticky="sw",
            padx=0, pady=(0, 2))

        # Main table
        table_wrap = tk.Frame(
            right, bg=PANEL,
            highlightbackground=BORDER, highlightthickness=1)
        table_wrap.grid(
            row=2, column=0, sticky="nsew", pady=(0, 8))
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        self.txt_table = scrolledtext.ScrolledText(
            table_wrap, font=MONO, bg=PANEL, fg="#2c2c2a",
            relief="flat", bd=0, wrap="none", state="disabled")
        self.txt_table.pack(
            fill="both", expand=True, padx=2, pady=2)

        # Preview
        self.lbl_preview_title = tk.Label(
            right, text="", bg=BG, font=SANS_B, fg="#444441")
        self.lbl_preview_title.grid(
            row=3, column=0, sticky="sw",
            padx=0, pady=(0, 2))

        preview_wrap = tk.Frame(
            right, bg=PANEL,
            highlightbackground=BORDER, highlightthickness=1)
        preview_wrap.grid(row=4, column=0, sticky="nsew")
        preview_wrap.columnconfigure(0, weight=1)
        preview_wrap.rowconfigure(0, weight=1)

        self.txt_preview = scrolledtext.ScrolledText(
            preview_wrap, font=("Courier New", 9), bg=PANEL,
            fg="#2c2c2a", relief="flat", bd=0,
            wrap="none", state="disabled")
        self.txt_preview.pack(
            fill="both", expand=True, padx=2, pady=2)

        # Tags for both text widgets
        for w in (self.txt_table, self.txt_preview):
            self._add_tags(w)

    @staticmethod
    def _add_tags(widget):
        """Registers all color tags for a ScrolledText widget."""
        widget.tag_config("win",
                           foreground=WIN_FG, background=WIN_BG)
        widget.tag_config("lose",
                           foreground=LOSE_FG, background=LOSE_BG)
        widget.tag_config("v", foreground=V_COLOR,
                           font=("Courier New", 9, "bold"))
        widget.tag_config("f", foreground=F_COLOR,
                           font=("Courier New", 9, "bold"))
        widget.tag_config("head",
                           font=("Courier New", 9, "bold"),
                           foreground="#444441")
        widget.tag_config("assigned", background="#fff8e1")
        widget.tag_config("dim",      foreground="#b0aea8")
        widget.tag_config("result_win",
                           foreground=WIN_FG,
                           font=("Courier New", 9, "bold"))
        widget.tag_config("result_lose",
                           foreground=LOSE_FG,
                           font=("Courier New", 9, "bold"))
        widget.tag_config("preview_true",  background="#eaf3f8")
        widget.tag_config("preview_false", background="#fff3e8")
        widget.tag_config("section_true",
                           foreground=V_COLOR,
                           font=("Courier New", 9, "bold"),
                           background="#dceeff")
        widget.tag_config("section_false",
                           foreground=F_COLOR,
                           font=("Courier New", 9, "bold"),
                           background="#ffeedd")

    # ══════════════════════════════════════════════════════════
    #  VARIABLE BUTTONS WITH HINTS
    # ══════════════════════════════════════════════════════════

    def _rebuild_var_buttons(self):
        for w in self.var_buttons_frame.winfo_children():
            w.destroy()

        if self.game_over or self.turn_idx >= len(self.turn_order):
            return

        player = self.turn_order[self.turn_idx]
        pool   = (self.v_remaining if player == 'V'
                  else self.f_remaining)

        if not pool:
            tk.Label(self.var_buttons_frame,
                     text="no variables available",
                     bg=PANEL, font=SANS_SM,
                     fg="#888780").pack()
            return

        # Evaluate each move via minimax (alpha-beta)
        hint_map = {}
        for var in pool:
            t_wins = eval_move(
                var, True,
                list(self.v_remaining), list(self.f_remaining),
                dict(self.assigned), self.turn_order,
                self.turn_idx, self.N, self.formula)
            f_wins = eval_move(
                var, False,
                list(self.v_remaining), list(self.f_remaining),
                dict(self.assigned), self.turn_order,
                self.turn_idx, self.N, self.formula)
            hint_map[var] = (t_wins, f_wins)

        self.selected_var.set(pool[0])
        self._var_btns = {}
        self._hint_map = hint_map
        cols = 3

        for i, var in enumerate(pool):
            t_wins, f_wins = hint_map[var]
            any_win  = t_wins or f_wins
            star     = " *" if any_win else ""

            if t_wins and f_wins:   hint_txt = "T* F*"
            elif t_wins:            hint_txt = "T*  F"
            elif f_wins:            hint_txt = "T   F*"
            else:                   hint_txt = "T   F"

            cell = tk.Frame(self.var_buttons_frame, bg=PANEL)
            cell.grid(row=i // cols, column=i % cols,
                      padx=3, pady=3, sticky="ew")

            btn = tk.Button(
                cell, text=f"x{var}{star}",
                font=("Segoe UI", 10, "bold"),
                relief="flat", cursor="hand2",
                padx=8, pady=5,
                command=lambda v=var: self._select_var(v))
            btn.pack(fill="x")

            lbl_hint = tk.Label(
                cell, text=hint_txt,
                font=("Courier New", 8), bg=PANEL,
                fg="#27500a" if any_win else "#888780")
            lbl_hint.pack()

            self._var_btns[var] = (btn, lbl_hint, cell)

        for c in range(min(cols, len(pool))):
            self.var_buttons_frame.columnconfigure(c, weight=1)

        self._hint_legend = tk.Label(
            self.var_buttons_frame,
            text="* = winning move",
            font=("Segoe UI", 7), bg=PANEL, fg="#b0aea8")
        self._hint_legend.grid(
            row=(len(pool) - 1) // cols + 1,
            column=0, columnspan=cols,
            sticky="w", padx=4, pady=(2, 0))

        self._highlight_var_buttons()
        self._update_preview(pool[0])

    def _select_var(self, var: int):
        self.selected_var.set(var)
        self._highlight_var_buttons()
        self._update_preview(var)

    def _highlight_var_buttons(self):
        if not hasattr(self, '_var_btns'):
            return
        player  = (self.turn_order[self.turn_idx]
                   if self.turn_idx < len(self.turn_order) else 'V')
        sel_bg  = "#dceeff" if player == 'V' else "#ffeedd"
        sel_fg  = V_COLOR   if player == 'V' else F_COLOR
        norm_bg = "#f1efe8"
        norm_fg = "#444441"

        for var, (btn, lbl_hint, cell) in self._var_btns.items():
            t_wins, f_wins = self._hint_map.get(var, (False, False))
            any_win = t_wins or f_wins

            if var == self.selected_var.get():
                btn.config(bg=sel_bg, fg=sel_fg,
                           relief="solid", bd=1)
                cell.config(bg=sel_bg)
                lbl_hint.config(bg=sel_bg)
            else:
                btn.config(bg=norm_bg, fg=norm_fg,
                           relief="flat", bd=0)
                cell.config(bg=PANEL)
                lbl_hint.config(bg=PANEL)

            lbl_hint.config(
                fg="#27500a" if any_win else "#888780")

    # ══════════════════════════════════════════════════════════
    #  SCREEN REFRESH
    # ══════════════════════════════════════════════════════════

    def _refresh(self):
        self._update_labels()
        self._rebuild_var_buttons()
        self._update_table()

    def _update_labels(self):
        v_rem = ', '.join(f'x{v}' for v in self.v_remaining) or '—'
        f_rem = ', '.join(f'x{v}' for v in self.f_remaining) or '—'
        self.lbl_V.config(
            text=f"V  (Verificator): {v_rem}", fg=V_COLOR)
        self.lbl_F.config(
            text=f"F  (Falsificator): {f_rem}", fg=F_COLOR)

        if self.game_over:
            remaining = filter_rows(self.all_data, self.assigned)
            true_c  = sum(1 for _, r in remaining if r)
            false_c = sum(1 for _, r in remaining if not r)

            if true_c > 0 and false_c == 0:
                msg, fg, bg = ("Verificator wins! ✓",
                               WIN_FG, WIN_BG)
            elif false_c > 0 and true_c == 0:
                msg, fg, bg = ("Falsificator wins! ✗",
                               LOSE_FG, LOSE_BG)
            else:
                msg, fg, bg = ("Draw / ambiguous",
                               "#444441", "#f1efe8")

            self.lbl_whose_turn.config(text=msg, fg=fg, bg=bg)
            self.info_frame.config(bg=bg)
            self.lbl_info.config(
                text=(f"Game over!  {msg}  |  "
                      f"Assignments: {len(remaining)}  "
                      f"(True: {true_c}, False: {false_c})"),
                bg=bg, fg=fg)
            self.btn_move.config(state="disabled")
            self.rb_true.config(state="disabled")
            self.rb_false.config(state="disabled")
            return

        player    = self.turn_order[self.turn_idx]
        remaining = filter_rows(self.all_data, self.assigned)
        true_c    = sum(1 for _, r in remaining if r)
        false_c   = sum(1 for _, r in remaining if not r)
        pool      = (self.v_remaining if player == 'V'
                     else self.f_remaining)
        vars_str  = ', '.join(f'x{v}' for v in pool)

        if player == 'V':
            self.lbl_whose_turn.config(
                text="Verificator's turn", fg=V_COLOR, bg=PANEL)
            self.info_frame.config(bg="#eaf3f8")
            self.lbl_info.config(
                text=(f"Verificator (blue) to move. "
                      f"Available variables: {vars_str}.  "
                      f"Compatible assignments: {len(remaining)}  "
                      f"(True: {true_c}, False: {false_c})"),
                bg="#eaf3f8", fg=V_COLOR)
            self.btn_move.config(bg=V_COLOR)
        else:
            self.lbl_whose_turn.config(
                text="Falsificator's turn", fg=F_COLOR, bg=PANEL)
            self.info_frame.config(bg="#fff3e8")
            self.lbl_info.config(
                text=(f"Falsificator (orange) to move. "
                      f"Available variables: {vars_str}.  "
                      f"Compatible assignments: {len(remaining)}  "
                      f"(True: {true_c}, False: {false_c})"),
                bg="#fff3e8", fg=F_COLOR)
            self.btn_move.config(bg=F_COLOR)

    # ══════════════════════════════════════════════════════════
    #  PREVIEW
    # ══════════════════════════════════════════════════════════

    def _update_preview(self, var: int):
        w = self.txt_preview
        w.configure(state="normal")
        w.delete("1.0", "end")

        if self.game_over or self.turn_idx >= len(self.turn_order):
            self.lbl_preview_title.config(text="")
            w.configure(state="disabled")
            return

        player = self.turn_order[self.turn_idx]
        color  = V_COLOR if player == 'V' else F_COLOR
        self.lbl_preview_title.config(
            text=f"Preview: x{var} = ?", fg=color)

        COL = 6
        future_vars = sorted(
            v for v in range(1, self.N + 1)
            if v not in self.assigned and v != var)
        col_order = [var] + future_vars

        def write_section(val_choice, section_tag, val_label):
            w.insert("end", f"  x{var} = {val_label}  ",
                     section_tag)
            trial = {**self.assigned, var: val_choice}
            rows  = filter_rows(self.all_data, trial)
            tc    = sum(1 for _, r in rows if r)
            fc    = sum(1 for _, r in rows if not r)
            w.insert("end",
                     f"  ({len(rows)} assignments: "
                     f"True={tc}, False={fc})\n")

            w.insert("end", "  ")
            for v in col_order:
                p = "V" if v in self.V_vars else "F"
                w.insert("end", f"x{v}".center(COL),
                         "v" if p == "V" else "f")
            w.insert("end", "  Result\n", "head")

            pt = "preview_true" if val_choice else "preview_false"
            for (x, res) in rows:
                w.insert("end", "  ")
                for v in col_order:
                    cell = ("T" if x[v] else "F").center(COL)
                    w.insert("end", cell,
                             pt if v == var else "")
                w.insert("end",
                         f"  {'✓  True ' if res else '✗  False'}\n",
                         "result_win" if res else "result_lose")
            w.insert("end", "\n")

        write_section(True,  "section_true",  "True ")
        write_section(False, "section_false", "False")
        w.configure(state="disabled")

    # ══════════════════════════════════════════════════════════
    #  MOVE
    # ══════════════════════════════════════════════════════════

    def _make_move(self):
        if self.game_over or self.turn_idx >= len(self.turn_order):
            return

        self.lbl_move_err.config(text="")
        player = self.turn_order[self.turn_idx]
        pool   = (self.v_remaining if player == 'V'
                  else self.f_remaining)

        var = self.selected_var.get()
        if var == -1 or var not in pool:
            self.lbl_move_err.config(
                text="Choose a variable from the available ones")
            return

        val = self.val_var.get() == "True"

        self.assigned[var] = val
        self.history.append((player, var, val))

        if player == 'V':
            self.v_remaining.remove(var)
        else:
            self.f_remaining.remove(var)

        # Append move to history immediately
        self.txt_history.configure(state="normal")
        val_str = "True " if val else "False"
        self.txt_history.insert(
            "end",
            f"  {len(self.history)}. [{player}] x{var} = {val_str}\n",
            "v" if player == "V" else "f")
        self.txt_history.see("end")
        self.txt_history.configure(state="disabled")

        self.turn_idx += 1
        if self.turn_idx >= len(self.turn_order):
            self.game_over = True

        self._refresh()

        if self.game_over:
            self.lbl_preview_title.config(text="")
            self.txt_preview.configure(state="normal")
            self.txt_preview.delete("1.0", "end")
            self.txt_preview.configure(state="disabled")

    # ══════════════════════════════════════════════════════════
    #  ASSIGNMENT TABLE
    # ══════════════════════════════════════════════════════════

    def _update_table(self):
        self.txt_table.configure(state="normal")
        self.txt_table.delete("1.0", "end")

        COL = 7
        assigned_vars   = [var for (_, var, _) in self.history]
        remaining_vars  = sorted(
            [v for v in self.V_vars if v not in self.assigned] +
            [v for v in self.F_vars if v not in self.assigned])
        col_order = assigned_vars + remaining_vars

        # Header
        self.txt_table.insert("end", "  ", "head")
        for var in col_order:
            p   = "V" if var in self.V_vars else "F"
            tag = "v" if p == "V" else "f"
            self.txt_table.insert(
                "end", f"x{var}[{p}]".center(COL), tag)
        self.txt_table.insert("end", "  Result\n", "head")
        self.txt_table.insert(
            "end",
            "  " + ("─" * COL) * len(col_order) + "  " + "─" * 10
            + "\n")

        # Rows
        visible = filter_rows(self.all_data, self.assigned)
        hidden  = len(self.all_data) - len(visible)

        for (x, res) in visible:
            self.txt_table.insert("end", "  ")
            for var in col_order:
                cell = ("T" if x[var] else "F").center(COL)
                self.txt_table.insert(
                    "end", cell,
                    "assigned" if var in self.assigned else "")
            self.txt_table.insert(
                "end",
                f"  {'✓  True ' if res else '✗  False'}\n",
                "result_win" if res else "result_lose")

        if hidden > 0:
            self.txt_table.insert(
                "end",
                f"\n  ... {hidden} more rows excluded by moves\n",
                "dim")

        true_c  = sum(1 for _, r in visible if r)
        false_c = sum(1 for _, r in visible if not r)
        self.txt_table.insert(
            "end",
            f"\n  Assignments: {len(visible)}  |  "
            f"True: {true_c}  |  False: {false_c}\n",
            "head")

        self.txt_table.configure(state="disabled")