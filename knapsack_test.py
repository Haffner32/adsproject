"""Correctness and runtime harness for 0/1 knapsack solvers.

A solver passed to this module must have the signature:
    solver(weights: list[int], profits: list[int], capacity: int) -> int

The solver should return the maximum total profit. Items may be skipped; each
item can be selected at most once. This harness uses only the Python standard
library.
"""

from __future__ import annotations

from statistics import median
from time import perf_counter
from typing import Callable, Sequence
import random

Solver = Callable[[Sequence[int], Sequence[int], int], int]


def reference_knapsack(
    weights: Sequence[int], profits: Sequence[int], capacity: int
) -> int:
    """Return the optimal 0/1 knapsack profit using a 1D DP reference."""
    _validate_input(weights, profits, capacity)
    dp = [0] * (capacity + 1)
    for weight, profit in zip(weights, profits):
        # Descending order ensures each item is used at most once.
        for room in range(capacity, weight - 1, -1):
            dp[room] = max(dp[room], dp[room - weight] + profit)
    return dp[capacity]


def _validate_input(
    weights: Sequence[int], profits: Sequence[int], capacity: int
) -> None:
    if len(weights) != len(profits):
        raise ValueError("weights and profits must have the same length")
    if not isinstance(capacity, int) or capacity < 0:
        raise ValueError("capacity must be a non-negative integer")
    if any(not isinstance(w, int) or w <= 0 for w in weights):
        raise ValueError("every weight must be a positive integer")
    if any(not isinstance(p, int) for p in profits):
        raise ValueError("every profit must be an integer")


def test_solver(
    solver: Solver,
    weights: Sequence[int],
    profits: Sequence[int],
    capacity: int,
    *,
    repeats: int = 5,
    warmups: int = 1,
) -> dict[str, int | float | bool]:
    """Check a solver against the reference answer and time repeated calls.

    Returns a dictionary with correctness, expected/actual profit, and runtime
    statistics in seconds. Raises AssertionError if the answer is incorrect.
    """
    _validate_input(weights, profits, capacity)
    if repeats < 1 or warmups < 0:
        raise ValueError("repeats must be >= 1 and warmups must be >= 0")

    expected = reference_knapsack(weights, profits, capacity)
    w, p = list(weights), list(profits)
    for _ in range(warmups):
        solver(w, p, capacity)

    durations = []
    actual = None
    for _ in range(repeats):
        start = perf_counter()
        actual = solver(w, p, capacity)
        durations.append(perf_counter() - start)

    correct = actual == expected
    result: dict[str, int | float | bool] = {
        "correct": correct,
        "expected_profit": expected,
        "actual_profit": actual,
        "median_seconds": median(durations),
        "min_seconds": min(durations),
        "repeats": repeats,
    }
    if not correct:
        raise AssertionError(
            f"Incorrect result: solver returned {actual}, expected {expected}"
        )
    return result


def benchmark_sizes(
    solver: Solver,
    sizes: Sequence[int],
    *,
    capacity: int = 1000,
    max_weight: int = 100,
    max_profit: int = 100,
    seed: int = 2026,
    repeats: int = 3,
) -> list[dict[str, int | float | bool]]:
    """Benchmark increasing item counts on deterministic random instances."""
    if any(n < 0 for n in sizes):
        raise ValueError("all sizes must be non-negative")
    if max_weight < 1 or max_profit < 0:
        raise ValueError("max_weight must be >= 1 and max_profit must be >= 0")

    rng = random.Random(seed)
    rows = []
    for n in sizes:
        weights = [rng.randint(1, max_weight) for _ in range(n)]
        profits = [rng.randint(0, max_profit) for _ in range(n)]
        row = test_solver(
            solver, weights, profits, capacity, repeats=repeats, warmups=1
        )
        row["items"] = n
        rows.append(row)
    return rows


def example_solver(
    weights: Sequence[int], profits: Sequence[int], capacity: int
) -> int:
    """Example 1D dynamic-programming implementation."""
    dp = [0] * (capacity + 1)
    for weight, profit in zip(weights, profits):
        for room in range(capacity, weight - 1, -1):
            dp[room] = max(dp[room], dp[room - weight] + profit)
    return dp[capacity]


if __name__ == "__main__":
    weights = [2, 3, 4, 5]
    profits = [3, 4, 5, 8]
    capacity = 8
    print("Single case:", test_solver(example_solver, weights, profits, capacity))
    print("Scaling benchmark:")
    for result in benchmark_sizes(example_solver, [50, 100, 200, 400]):
        print(result)
