#values = the value of each item
from dp_lists import merge_lists  # same merge as DP-with-Lists, so the comparison is fair


def solve_knapsack_branch_and_bound(weights: list, profits: list, capacity: int):
    """DP-with-Upper-Bounds (Section 3.5): DP-with-Lists where a state (w, p) is
    fathomed when its LP-relaxation bound U(p, w) does not exceed the incumbent z.
    Returns the best state (weight, profit) found."""
    n = len(weights)
    list_current = [(0,0)]

    order = sorted(range(n), key=lambda i: profits[i] / weights[i], reverse=True)
    ws = [weights[i] for i in order]
    ps = [profits[i] for i in order]

    # incumbent: best state seen so far and its profit z (the lower bound)
    best_state = (0, 0)
    z = 0

    for i in range(n):
        wi, pi = ws[i], ps[i]
        list_prime = []
        # add the value of the current to each element in the previous list
        for w, p in list_current:
            new_w = w + wi
            if new_w <= capacity:
                list_prime.append((new_w, p + pi))
        list_current = merge_lists(list_current, list_prime)

        # lists are sorted by weight with strictly increasing profit,
        # so the most profitable state of the level is the last one
        if list_current[-1][1] > z:
            best_state = list_current[-1]
            z = best_state[1]

        # fathom every state with U(p, w) <= z. U is the LP relaxation over the
        # items i+1..n-1 (greedy in ratio order, O(n) per state as in the book),
        # inlined to avoid a function call per state
        new_list = []
        for w, p in list_current:
            remaining_capacity = capacity - w
            upper_bound = p
            idx = i + 1
            while remaining_capacity > 0 and idx < n:
                w_idx = ws[idx]
                if w_idx <= remaining_capacity:
                    upper_bound += ps[idx]
                    remaining_capacity -= w_idx
                else:
                    upper_bound += ps[idx] * remaining_capacity / w_idx
                    break
                idx += 1
            if upper_bound > z:
                new_list.append((w, p))

        list_current = new_list

    return best_state
