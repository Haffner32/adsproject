import random
from knapsack_test import test_solver, benchmark_sizes, example_solver
from dp_lists import dp_lists


def solver(weights, profits, capacity):
    return dp_lists(weights, profits, capacity)[1]   # profit of the largest state


if __name__ == "__main__":
    # 1. Textbook-style single case (expected profit: 12 -> items 2 and 4... check printed output)
    print(test_solver(solver, [2, 3, 4, 5], [3, 4, 5, 8], 8))

    # 2. Edge cases
    for w, p, c in [([], [], 10), ([5], [10], 0), ([5], [10], 4), ([5], [10], 5), ([1, 1, 1], [0, 0, 0], 2)]:
        test_solver(solver, w, p, c, repeats=1, warmups=0)

    # 3. Randomized stress test against the reference (small, many cases)
    rng = random.Random(0)
    for _ in range(2000):
        n = rng.randint(0, 12)
        w = [rng.randint(1, 20) for _ in range(n)]
        p = [rng.randint(0, 30) for _ in range(n)]
        c = rng.randint(0, 60)
        test_solver(solver, w, p, c, repeats=1, warmups=0)
    print("random tests passed")

    # 4. Scaling benchmark
    for row in benchmark_sizes(solver, [50, 100, 200, 400]):
        print(row)

    # 5. Compare with example knapsack
    for n in [50, 100, 200, 400]:
        rng = random.Random(n)
        w = [rng.randint(1, 100) for _ in range(n)]
        p = [rng.randint(0, 100) for _ in range(n)]
        a = test_solver(solver, w, p, 1000, repeats=3)["median_seconds"]
        b = test_solver(example_solver, w, p, 1000, repeats=3)["median_seconds"]
        print(n, f"lists={a:.4f}s  array={b:.4f}s")