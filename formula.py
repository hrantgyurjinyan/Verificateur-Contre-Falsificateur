"""
formula.py
==========
Parsing and preprocessing of boolean formulas.

Supported operations:
  and  or  not  ( )
  xor             — exclusive or            (a != b)
  iff  <->        — equivalence             (a == b)
  implies  ->     — implication             (a <= b)

Usage:
  from formula import make_formula, all_rows, filter_rows

  formula, processed = make_formula("(x1 or x2) and (x3 xor x4)")
  rows = all_rows(4, formula)
  compatible = filter_rows(rows, {1: True})
"""

import re
import itertools


# ============================================================
#  PREPROCESSOR
# ============================================================

def preprocess_formula(s: str) -> str:
    """
    Converts extended syntax into a Python expression.

    xor       → !=
    iff / <-> → ==
    implies / -> → <=   (for bool: p<=q is equivalent to not p or q)
    x1..xN    → x[1]..x[N]  for subsequent eval()
    """
    # Protect xN tokens — temporarily replace with placeholders
    s = re.sub(r'x(\d+)', r'__V\1__', s)

    def replace_binop(src: str, keywords: list, replacement: str) -> str:
        pat = '|'.join(re.escape(k) for k in keywords)
        # var op var
        src = re.sub(
            rf'__V(\d+)__\s*(?:{pat})\s*__V(\d+)__',
            rf'__V\1__ {replacement} __V\2__', src)
        # ) op (
        src = re.sub(
            rf'\)\s*(?:{pat})\s*\(',
            f') {replacement} (', src)
        # var op (
        src = re.sub(
            rf'__V(\d+)__\s*(?:{pat})\s*\(',
            rf'__V\1__ {replacement} (', src)
        # ) op var
        src = re.sub(
            rf'\)\s*(?:{pat})\s*__V(\d+)__',
            rf') {replacement} __V\1__', src)
        return src

    s = replace_binop(s, ['xor'],           '!=')
    s = replace_binop(s, ['iff', '<->'],    '==')
    s = replace_binop(s, ['implies', '->'], '<=')

    # Restore variables → x[N]
    s = re.sub(r'__V(\d+)__', r'x[\1]', s)
    return s


def make_formula(formula_str_raw: str):
    """
    Accepts a formula as a string, returns:
      (formula_fn, processed_str)

    formula_fn(x: dict) -> bool
      where x = {1: True/False, 2: True/False, ...}
    """
    processed = preprocess_formula(formula_str_raw)

    def formula_fn(x: dict) -> bool:
        return bool(eval(processed))

    return formula_fn, processed


# ============================================================
#  TRUTH TABLE
# ============================================================

def all_rows(N: int, formula_fn) -> list:
    """
    Returns a list of all 2^N rows of the truth table:
      [(assignment_dict, result_bool), ...]

    assignment_dict = {1: bool, 2: bool, ..., N: bool}
    """
    rows = []
    for vals in itertools.product([False, True], repeat=N):
        x = {i + 1: v for i, v in enumerate(vals)}
        rows.append((x, formula_fn(x)))
    return rows


def filter_rows(rows: list, assigned: dict) -> list:
    """
    Keeps only the rows compatible with the current assignments.

    rows     — output of all_rows()
    assigned — {var_idx: bool, ...} already assigned variables
    """
    return [
        (x, r) for (x, r) in rows
        if all(x[var] == val for var, val in assigned.items())
    ]