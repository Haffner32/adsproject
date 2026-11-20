#values = the value of each item
def dp_lists(weights: list, profits: list):
    n = len(weights)
    list_current = [(0,0)]
    for i in range(n):
        list_prime = []
        #add the value of the current to each element in the previous list
        for w, p in list_current:
            new_w = w + weights[i]
            new_p = p + profits[i]
            list_prime.append((new_w, new_p))
        list_current = merge_lists(list_current, list_prime)
    return list_current(len(list_current) - 1)

def merge_lists(l1: list, l2: list):
    current_max = (float('inf'), 0)
    l1.append((float('inf'), 0))
    l2.append((float('inf'), 0))
    result = []
    #pointers to the current element of l1 and l2
    p1, p2 = 0, 0
    w, p = -1, -1 
    n = len(l1)
    while (w != float('inf')):
        if l1[p1][0] < l2[p2][0]:
            current_smallest = l1[p1]
            p1 += 1
        else:
            current_smallest = l2[p2]
            p2 += 1

        w, p = current_smallest
        w_m, p_m = current_max
        if w >= w_m:
            #w > w_m and p > p_m
            #no dominance between current and max
             
            current_max = current_smallest
            result.append(current_smallest)

            # w = w_m and p > p_m
            if w == w_m and p > p_m:
                current_length = len(result)
                result[current_length] = current_smallest
                current_max = current_smallest

            #else w >= m and p <= p_m, dominated by current max -> skip
    return result
        
    
 
            

