#values = the value of each item
def dp_lists(weights: list, profits: list, capacity: int):
    n = len(weights)
    list_current = [(0,0)]
    for i in range(n):
        list_prime = []
        #add the value of the current to each element in the previous list
        for w, p in list_current:
            new_w = w + weights[i]
            new_p = p + profits[i]
            if new_w <= capacity:
                list_prime.append((new_w, new_p))
        list_current = merge_lists(list_current, list_prime)
    return list_current[-1]

def merge_lists(l1: list, l2: list):
    l1 = l1 + [(float('inf'), 0)]
    l2 = l2 + [(float('inf'), 0)]
    result = [(0,0)]
    #pointers to the current element of l1 and l2
    p1 = p2 = 0 
    while True:
        if l1[p1][0] < l2[p2][0]:
            w, p = l1[p1]
            p1 += 1
        else:
            w, p = l2[p2]
            p2 += 1

        if w == float('inf'):
            break

        w_m, p_m = result[-1]

        if p > p_m:
            if w == w_m:
                result[-1] = (w, p)
            else:
                result.append((w, p))
    return result
        
    
 
            

