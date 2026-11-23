"""Correctness suite for DP-with-Lists. Run: python run_tests.py"""
import random
from knapsack_test import test_solver, reference_knapsack, example_solver
from dp_lists import dp_lists
from instrumented import dp_lists_stats, brute_force
from generators import generate, TYPES, capacity_from_fraction


def solver(weights, profits, capacity):
    return dp_lists(weights, profits, capacity)[1]   # profit of the last (largest) state


def check_all(w, p, c):
    """Compare solver with array DP, brute force (small n), and the instrumented copy."""
    expected = reference_knapsack(w, p, c)
    assert solver(w, p, c) == expected, f"solver mismatch on {w},{p},{c}"
    if len(w) <= 15:
        assert brute_force(w, p, c) == expected, f"reference mismatch on {w},{p},{c}"
    # instrumented copy must agree with the original and keep the sorted/non-dominated invariant
    best, _ = dp_lists_stats(w, p, c, check=True)
    assert best == dp_lists(w, p, c), "instrumented copy differs from dp_lists"


if __name__ == "__main__":
    # 1. Textbook case, asserted (items 2 and 4: weight 3+5=8, profit 4+8=12)
    assert solver([2, 3, 4, 5], [3, 4, 5, 8], 8) == 12
    print("textbook case:", test_solver(solver, [2, 3, 4, 5], [3, 4, 5, 8], 8))

    # 2. Hand-written edge cases
    edge = [
        ([], [], 10),                    # no items
        ([5], [10], 0),                  # c = 0
        ([5], [10], 4),                  # item too heavy
        ([5], [10], 5),                  # exact fit
        ([1, 1, 1], [0, 0, 0], 2),       # zero profits
        ([3, 3, 3], [5, 5, 5], 6),       # duplicate items
        ([2, 3, 4], [1, 2, 3], 100),     # everything fits
        ([4, 4], [7, 9], 4),             # same weight, different profit (replace branch)
        ([50, 60], [5, 9], 10),          # all items heavier than c
    ]
    for w, p, c in edge:
        check_all(w, p, c)
    print("edge cases passed:", len(edge))

    # 3. Random small instances (brute-force checked), incl. heavy items and zero profits
    rng = random.Random(0)
    for _ in range(3000):
        n = rng.randint(0, 12)
        wmax = rng.choice([3, 10, 20, 80])
        w = [rng.randint(1, wmax) for _ in range(n)]
        p = [rng.randint(0, rng.choice([0, 5, 30])) for _ in range(n)]
        c = rng.randint(0, 60)
        check_all(w, p, c)
    print("random small tests passed: 3000")

    # 4. Every generator type x capacity fraction (small n: brute force + invariant)
    count = 0
    for kind in TYPES:
        for frac in (0.1, 0.25, 0.5, 1.0):
            for seed in range(20):
                w, p = generate(kind, 12, R=30, seed=seed)
                check_all(w, p, capacity_from_fraction(w, frac))
                count += 1
    print("generator-type tests passed:", count)

    # 5. Larger instances vs the array DP (no brute force), invariant checked
    count = 0
    for kind in TYPES:
        for n in (100, 300):
            w, p = generate(kind, n, R=100, seed=n)
            c = capacity_from_fraction(w, 0.25)
            check_all(w, p, c)
            count += 1
    print("large-instance tests passed:", count)
    print("ALL CORRECTNESS TESTS PASSED")