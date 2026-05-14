"""
engine.py
=========
Game engine: turn order, minimax with alpha-beta pruning
and memoization, single-move evaluation.

Usage:
  from engine import build_turn_order, minimax_hint, eval_move
"""


# ============================================================
#  TURN ORDER
# ============================================================

def build_turn_order(v_vars: list, f_vars: list) -> list:
    """
    Strict alternation V → F → V → F ...
    If one player runs out of variables, the other finishes alone.

    Returns a list of 'V' | 'F' of length len(v_vars) + len(f_vars).

    Examples:
      build_turn_order([1,3], [2,4]) → ['V','F','V','F']
      build_turn_order([1,2,3], [4]) → ['V','F','V','V']
    """
    turns = []
    vi, fi = 0, 0
    whose_turn = 'V'

    while vi < len(v_vars) or fi < len(f_vars):
        if whose_turn == 'V':
            if vi < len(v_vars):
                turns.append('V'); vi += 1
            elif fi < len(f_vars):
                turns.append('F'); fi += 1
            whose_turn = 'F'
        else:
            if fi < len(f_vars):
                turns.append('F'); fi += 1
            elif vi < len(v_vars):
                turns.append('V'); vi += 1
            whose_turn = 'V'

    return turns


# ============================================================
#  MINIMAX WITH ALPHA-BETA PRUNING + MEMOIZATION
# ============================================================
#
#  For boolean minimax, alpha-beta reduces to:
#    V moves → found True  → return True  immediately (β-cutoff)
#    F moves → found False → return False immediately (α-cutoff)
#
#  Classic principle: once a guaranteed result is found,
#  the rest of the subtree is skipped.
#
#  Memoization: the same position can be reached via different
#  paths — cache results to avoid recomputation.
# ============================================================

def minimax_hint(v_remaining: list,
                 f_remaining: list,
                 assigned: dict,
                 turn_order: list,
                 turn_idx: int,
                 N: int,
                 formula_fn,
                 _cache: dict = None) -> bool:
    """
    Returns True if V can guarantee a win from the current position
    with optimal play from both sides.

    Parameters:
      v_remaining — list of V's variables not yet assigned
      f_remaining — list of F's variables not yet assigned
      assigned    — {var_idx: bool} already assigned variables
      turn_order  — list of 'V'|'F', the move sequence
      turn_idx    — current step in turn_order
      N           — total number of variables
      formula_fn  — formula from make_formula()
      _cache      — internal memoization cache (do not pass manually)

    Optimizations:
      1. Alpha-beta pruning — early exit on determined result
      2. Memoization        — cache keyed by (assigned, v_rem, f_rem, turn_idx)
      3. Move ordering      — True first for V, False first for F
    """
    if _cache is None:
        _cache = {}

    # ── Cache key ──────────────────────────────────────────
    cache_key = (
        frozenset(assigned.items()),
        tuple(sorted(v_remaining)),
        tuple(sorted(f_remaining)),
        turn_idx
    )
    if cache_key in _cache:
        return _cache[cache_key]

    # ── Leaf node — all variables assigned ─────────────────
    if turn_idx == len(turn_order):
        x = {i: assigned[i] for i in range(1, N + 1)}
        result = formula_fn(x)
        _cache[cache_key] = result
        return result

    player = turn_order[turn_idx]

    if player == 'V':
        # V maximizes: looks for at least one winning move
        # True first — β-cutoff triggers as early as possible
        for var in v_remaining:
            for val in [True, False]:
                new_a = {**assigned, var: val}
                new_v = [v for v in v_remaining if v != var]
                if minimax_hint(new_v, f_remaining, new_a,
                                turn_order, turn_idx + 1, N,
                                formula_fn, _cache):
                    # Win found — stop looking (β-cutoff)
                    _cache[cache_key] = True
                    return True
        _cache[cache_key] = False
        return False

    else:  # F moves
        # F minimizes: looks for at least one refuting move
        # False first — α-cutoff triggers as early as possible
        for var in f_remaining:
            for val in [False, True]:
                new_a = {**assigned, var: val}
                new_f = [f for f in f_remaining if f != var]
                if not minimax_hint(v_remaining, new_f, new_a,
                                    turn_order, turn_idx + 1, N,
                                    formula_fn, _cache):
                    # Refutation found — stop looking (α-cutoff)
                    _cache[cache_key] = False
                    return False
        _cache[cache_key] = True
        return True


def eval_move(var: int,
              val: bool,
              v_remaining: list,
              f_remaining: list,
              assigned: dict,
              turn_order: list,
              turn_idx: int,
              N: int,
              formula_fn) -> bool:
    """
    Evaluates a single specific move (var = val) for the current player.

    Returns True if this move leads to a win for the current player
    with optimal play from both sides afterward.

    Each call uses its own cache — positions are independent across calls.
    """
    player = turn_order[turn_idx]
    new_a  = {**assigned, var: val}
    cache  = {}

    if player == 'V':
        new_v = [v for v in v_remaining if v != var]
        return minimax_hint(new_v, f_remaining, new_a,
                            turn_order, turn_idx + 1, N,
                            formula_fn, cache)
    else:
        new_f = [f for f in f_remaining if f != var]
        # F wins if V does NOT win
        return not minimax_hint(v_remaining, new_f, new_a,
                                turn_order, turn_idx + 1, N,
                                formula_fn, cache)