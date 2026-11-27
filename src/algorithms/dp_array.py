#values = the value of each item
def dp_array(weights: list, profits: list, capacity: int):
    """DP-1: the one-dimensional array DP from class. Returns the optimal profit."""
    z = [0] * (capacity + 1)
    for w, p in zip(weights, profits):
        # go down from c so each item is used at most once
        for d in range(capacity, w - 1, -1):
            z[d] = max(z[d], z[d - w] + p)
    return z[capacity]
