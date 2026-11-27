"""Experiment harness. Writes results/results.csv and results/env.json.

Usage: python run_experiments.py [--quick] [--seeds N]
"""
import argparse, csv, gc, json, os, platform, sys
from statistics import median
from time import perf_counter

# make src/algorithms and tests (for knapsack_test) importable no matter where the script is run from
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "algorithms"))
sys.path.insert(0, os.path.join(_HERE, "..", "..", "tests"))

from dp_lists import dp_lists
from knapsack_test import example_solver, reference_knapsack
from instrumented import dp_lists_stats, array_updates
from generators import generate, capacity_from_fraction, TYPES


def lists_solver(w, p, c):
    return dp_lists(w, p, c)[1]


def time_once(solver, w, p, c, repeats):
    """Min of `repeats` runs, GC disabled, perf_counter. Returns (seconds, result)."""
    best, result = float("inf"), None
    for _ in range(repeats):
        gc.collect()
        gc.disable()
        t0 = perf_counter()
        result = solver(w, p, c)
        dt = perf_counter() - t0
        gc.enable()
        best = min(best, dt)
    return best, result


def run_instance(exp, kind, n, R, w, p, c, seed, repeats, rows, extra=None):
    t_lists, r1 = time_once(lists_solver, w, p, c, repeats)
    t_array, r2 = time_once(example_solver, w, p, c, repeats)
    assert r1 == r2, f"solvers disagree ({exp}, {kind}, n={n}, c={c}, seed={seed})"
    _, st = dp_lists_stats(w, p, c)
    row = {
        "experiment": exp, "kind": kind, "n": n, "R": R, "capacity": c, "seed": seed,
        "cap_fraction": round(c / sum(w), 4) if sum(w) else 0,
        "t_lists": t_lists, "t_array": t_array,
        "max_list": st["max_list"], "avg_list": st["avg_list"], "final_list": st["final_list"],
        "candidates": st["candidates"], "array_updates": array_updates(w, c),
        "opt": r1,
    }
    if extra:
        row.update(extra)
    rows.append(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="small sizes for a smoke test")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--repeats", type=int, default=3)
    a = ap.parse_args()
    S, rep = a.seeds, a.repeats
    R = 100
    rows = []

    if a.quick:
        ns, cs, n_fix, c_fix, n_type = [50, 100], [200, 400], 50, 400, 100
    else:
        ns, cs, n_fix, c_fix, n_type = [100, 200, 400, 800, 1600], [500, 1000, 2000, 4000, 8000], 200, 5000, 400

    # E1: fixed capacity, vary n (uncorrelated)
    for n in ns:
        for s in range(S):
            w, p = generate("uncorrelated", n, R, seed=1000 * n + s)
            run_instance("E1_vary_n", "uncorrelated", n, R, w, p, c_fix, s, rep, rows)
        print("E1 n =", n, flush=True)

    # E2: fixed n, vary capacity (uncorrelated)
    for c in cs:
        for s in range(S):
            w, p = generate("uncorrelated", n_fix, R, seed=7000 + c + s)
            run_instance("E2_vary_c", "uncorrelated", n_fix, R, w, p, c, s, rep, rows)
        print("E2 c =", c, flush=True)

    # E3/E4: instance type x capacity fraction
    for kind in TYPES:
        for frac in (0.10, 0.25, 0.50):
            for s in range(S):
                w, p = generate(kind, n_type, R, seed=31 * s + 5)
                c = capacity_from_fraction(w, frac)
                run_instance("E3_type_frac", kind, n_type, R, w, p, c, s, rep, rows,
                             extra={"frac_target": frac})
            print("E3", kind, frac, flush=True)

    # E5: adversarial for the list DP: subset sum, where distinct sums never dominate each other
    # (|L| approaches c+1), versus the best case for dominance (strongly correlated, small capacity).
    for kind, frac in (("subset_sum", 0.5), ("strongly", 0.05)):
        for n in ns:
            for s in range(S):
                w, p = generate(kind, n, R, seed=9000 + n + s)
                c = capacity_from_fraction(w, frac)
                run_instance("E5_extremes", kind, n, R, w, p, c, s, rep, rows,
                             extra={"frac_target": frac})
        print("E5", kind, flush=True)

    os.makedirs("results", exist_ok=True)
    fields = sorted({k for r in rows for k in r})
    with open("results/results.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)
    with open("results/env.json", "w") as f:
        json.dump({"python": sys.version, "platform": platform.platform(),
                   "processor": platform.processor(), "seeds": S, "repeats": rep,
                   "timing": "min of repeats, perf_counter, GC disabled",
                   "R": R, "quick": a.quick}, f, indent=2)
    print("wrote", len(rows), "rows")


if __name__ == "__main__":
    main()
