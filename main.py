"""
main.py
=======
Entry point. Run: python main.py

Project structure:
  main.py          — root window, navigation between screens
  setup_frame.py   — game setup screen
  game_frame.py    — step-by-step game screen
  engine.py        — game engine (minimax, alpha-beta, turn order)
  formula.py       — formula parsing, truth table
  theme.py         — colors and fonts
"""

import tkinter as tk
from tkinter import ttk

from theme       import BG
from setup_frame import SetupFrame
from game_frame  import GameFrame


class App(tk.Tk):
    """
    Root application window.
    Manages switching between SetupFrame and GameFrame.
    """

    def __init__(self):
        super().__init__()
        self.title("Verificator vs Falsificator")
        self.minsize(920, 620)
        self.configure(bg=BG)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)

        self._current = None
        self._show_setup()

    def _show_setup(self):
        """Shows the setup screen."""
        if self._current:
            self._current.destroy()
        frame = SetupFrame(self, on_start=self._start_game)
        frame.pack(fill="both", expand=True)
        self._current = frame

    def _start_game(self, N, V_vars, F_vars, formula_fn, formula_raw):
        """Launches the game screen with the given parameters."""
        if self._current:
            self._current.destroy()
        frame = GameFrame(
            self, N, V_vars, F_vars,
            formula_fn, formula_raw,
            on_restart=self._show_setup)
        frame.pack(fill="both", expand=True)
        self._current = frame


if __name__ == "__main__":
    app = App()
    app.mainloop()