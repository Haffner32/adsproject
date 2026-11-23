"""Instance generators from the standard knapsack literature (Kellerer, Pferschy, Pisinger).

Weights are uniform in [1, R]. All generators are deterministic given a seed.
"""
import random

TYPES = ["uncorrelated", "weakly", "strongly", "subset_sum", "inverse_strongly"]


def generate(kind, n, R=100, seed=0):
    """Return (weights, profits) with n items of the given correlation type."""
    rng = random.Random(seed)
    d = max(1, R // 10)
    w, p = [], []
    for _ in range(n):
        if kind == "uncorrelated":
            wj, pj = rng.randint(1, R), rng.randint(1, R)
        elif kind == "weakly":
            wj = rng.randint(1, R)
            pj = rng.randint(max(1, wj - d), wj + d)
        elif kind == "strongly":
            wj = rng.randint(1, R)
            pj = wj + d
        elif kind == "subset_sum":
            wj = rng.randint(1, R)
            pj = wj
        elif kind == "inverse_strongly":
            pj = rng.randint(1, R)
            wj = pj + d
        else:
            raise ValueError(f"unknown instance type: {kind}")
        w.append(wj)
        p.append(pj)
    return w, p


def capacity_from_fraction(weights, fraction):
    """Capacity as a fraction of total weight (at least 1)."""
    return max(1, int(fraction * sum(weights)))
