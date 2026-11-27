"""Instrumented copy of dp_lists.py (same algorithm, plus counters) and a brute-force reference.

Timing is always done on the ORIGINAL dp_lists; this module is used only for
machine-independent measurements (|L|, candidates processed) and invariant checks.
"""
from itertools import combinations


def merge_lists_stats(l1, l2):
    """Identical logic to dp_lists.merge_lists; also returns #candidates consumed."""
    l1 = l1 + [(float("inf"), 0)]
    l2 = l2 + [(float("inf"), 0)]
    result = [(0, 0)]
    p1 = p2 = 0
    candidates = 0
    while True:
        if l1[p1][0] < l2[p2][0]:
            w, p = l1[p1]
            p1 += 1
        else:
            w, p = l2[p2]
            p2 += 1
        if w == float("inf"):
            break
        candidates += 1
        w_m, p_m = result[-1]
        if p > p_m:
            if w == w_m:
                result[-1] = (w, p)
            else:
                result.append((w, p))
    return result, candidates


def check_invariant(lst, capacity):
    """Weights and profits strictly increasing, all weights <= capacity, starts at (0,0)."""
    assert lst[0] == (0, 0), "list must start with (0,0)"
    for (w1, p1), (w2, p2) in zip(lst, lst[1:]):
        assert w1 < w2 and p1 < p2, f"order violated: {(w1, p1)} then {(w2, p2)}"
    assert all(w <= capacity for w, _ in lst), "weight exceeds capacity"


def dp_lists_stats(weights, profits, capacity, check=False):
    """Run DP-with-Lists. Returns (best_state, stats dict)."""
    cur = [(0, 0)]
    sizes, candidates = [], 0
    for wi, pi in zip(weights, profits):
        shifted = [(w + wi, p + pi) for w, p in cur if w + wi <= capacity]
        cur, k = merge_lists_stats(cur, shifted)
        candidates += k
        sizes.append(len(cur))
        if check:
            check_invariant(cur, capacity)
    return cur[-1], {
        "max_list": max(sizes, default=1),
        "avg_list": sum(sizes) / len(sizes) if sizes else 1.0,
        "final_list": len(cur),
        "candidates": candidates,
    }


def array_updates(weights, capacity):
    """Number of inner-loop updates the 1D array DP performs."""
    return sum(max(0, capacity - w + 1) for w in weights)


def brute_force(weights, profits, capacity):
    """Exhaustive optimum; only for n <= ~15."""
    n = len(weights)
    best = 0
    for r in range(n + 1):
        for idx in combinations(range(n), r):
            if sum(weights[i] for i in idx) <= capacity:
                best = max(best, sum(profits[i] for i in idx))
    return best
