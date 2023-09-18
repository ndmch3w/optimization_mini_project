import copy
import time

def rando():
    m, m2 = 2147483647, 2145483479
    a12, a13, a21, a23 = 63308, -183326, 86098, -539608
    q12, q13, q21, q23 = 33921, 11714, 24919, 3976
    r12, r13, r21, r23 = 12979, 2883, 7417, 2071
    invm = 4.656612873077393e-10
    h = rando.x10 // q13
    p13 = -a13 * (rando.x10 - h * q13) - h * r13
    h = rando.x11 // q12
    p12 = a12 * (rando.x11 - h * q12) - h * r12
    if p13 < 0: p13 = p13 + m
    if p12 < 0: p12 = p12 + m
    rando.x10, rando.x11, rando.x12 = rando.x11, rando.x12, p12 - p13
    if rando.x12 < 0: rando.x12 = rando.x12 + m
    h = rando.x20 // q23
    p23 = -a23 * (rando.x20 - h * q23) - h * r23
    h = rando.x22 // q21
    p21 = a21 * (rando.x22 - h * q21) - h * r21
    if p23 < 0: p23 = p23 + m2
    if p21 < 0: p21 = p21 + m2
    rando.x20, rando.x21, rando.x22 = rando.x21, rando.x22, p21 - p23
    if rando.x22 < 0: rando.x22 = rando.x22 + m2
    if rando.x12 < rando.x22: h = rando.x12 - rando.x22 + m
    else: h = rando.x12 - rando.x22
    if h == 0: return 0.5
    else: return h * invm

rando.x10, rando.x11, rando.x12 = 12345, 67890, 13579
rando.x20, rando.x21, rando.x22 = 24680, 98765, 43210

def input_(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        [N, K] = [int(x) for x in lines[0].split()]
        distances = []
        for i in range(1, N+2):
            distances.append([int(x) for x in lines[i].split()])
    return N, K, distances


def writeSolution(filename, tour):
    with open(filename, "w") as f:
        f.write(str(K))
        f.write("\n")
        result = ''
        for k in range(1, K+1):
            s = str(len(tour[k])) + '\n'
            for i in tour[k]:
                s = s + str(i) + ' '
            s = s + '\n'
            result += s
        f.write(result)


def printSolution(tour):
    print(K)
    for k in range(1, K+1):
        print(len(tour[k]))
        print(' '.join(tour[k]))



######## Returns a random integer in [low; high]
def unif(low, high):
    return low + int((high - low + 1) * rando())

######## Returns a random permutation of the elements 0...n-1
def rand_permutation(n):
    p = [i for i in range(n)]
    for i in range(n - 1):
        random_index = unif(i, n - 1)
        p[i], p[random_index] = p[random_index], p[i]
    return p



##### compute the length of each route in tour
def vrp_route_length(d, tour):

    route_length = [[]]
    for k in range(1, K+1):
        #print('k=',k)
        #print(len(tour))
        n = len(tour[k])
        s = d[tour[k][n-1]][0]
        for i in range(n-1):
            s += d[tour[k][i]][tour[k][i+1]]
        route_length.append(s)
    return route_length

#### compute the total length of tour
def vrp_tour_length(d, tour):
    return sum(vrp_route_length(d, tour)[1:]) #type: ignore







# compute the length of a tsp tour
def tsp_length(d, tour):
    n = len(tour)
    length = d[tour[n-1]][tour[0]]
    for i in range(n-1):
        length += d[tour[i]][tour[i+1]]
    return length

# build solution representation by successors
def tsp_tour_to_succ(tour):
    n = len(tour)
    succ = [-1] * n
    for i in range(n):
        succ[tour[i]] = tour[(i+1)%n]
    return succ

# build solution representation by predeccessors
def tsp_succ_to_pred(succ):
    n = len(succ)
    pred = [-1]*n
    for i in range(n):
        pred[succ[i]] = i
    return pred

# convert solution from successor of each city to city order
def tsp_succ_to_tour(succ):
    n = len(succ)
    tour = [-1]*n
    j = 0
    for i in range(n):
        tour[i] = j
        j = succ[j]
    return tour

# convert a solution given by 2-opt data structure to a standard tour
def tsp_2opt_data_structure_to_tour(t):
    n = int(len(t)/2 + 0.5)
    tour = [-1]*n
    j = 0
    for i in range(n):
        tour[i] = j >> 1
        j = t[j]
        #print('tour =', tour)
        #print('t =', t)
        #print('j = ', j)
    return tour

# compare 2 directed tours; returns the number of different arcs
def tsp_compare(succ_a, succ_b):
    n = len(succ_a)
    count = 0
    for i in range(n):
        if succ_a[i] != succ_b[i]:
            count += 1
    return count


# data structure building for performing 2-opt move in constant time
def build_2opt_data_structure(tour): # order of visit of the cities
    n = len(tour)
    t = [-1]*2*n
    for i in range(n-1):
        t[2*tour[i]] = 2*tour[i+1]
    t[2*tour[n-1]] = 2* tour[0]
    for i in range(1, n):
        t[2*tour[i]+1] = 2*tour[i-1] + 1
    t[2*tour[0] + 1] = 2 * tour[n-1] + 1
    return t

# local search with 2-opt neighborhood and first improvement policy
def tsp_2opt_first(d, tour, length):
    n = len(tour)
    t = build_2opt_data_structure(tour)
    i = last_i = 0 # i = starting city || last_i = i - a complete tour
    while t[t[i]] >> 1 != last_i: # index i has made 1 turn without improvement
        j = t[t[i]]
        while j >> 1 != last_i and (t[j] >> 1 != last_i or i >> 1 != last_i):
            delta = d[i>>1][j>>1] + d[t[i]>>1][t[j]>>1] \
                - d[i>>1][t[i]>>1] - d[j>>1][t[j]>>1]
            if delta < 0: # An improving move is found
                next_i, next_j = t[i], t[j] # Perform move
                t[i], t[j] = j ^ 1, i ^ 1
                t[next_i ^ 1], t[next_j ^ 1] = next_j, next_i

                length += delta # Update solution cost
                #print('delta =', delta)
                #print('length =', length)
                last_i = i >> 1 # Solution improved: i must make another turn
                j = t[i]
            j = t[j]
        i = t[i]
        #print('length =', length)
    return tsp_2opt_data_structure_to_tour(t), length


### POPMUSIC (Partial Optimization Metaheuristic Under Special Intensification Condition)
def tsp_3opt_limited(d, # Distance matrix
    r, # Subproblem size
    succ, # Tour provided and returned
    length): # Tour length
    n = len(succ)
    if r > n - 2: # Subproblem size must not exceed n - 2
        r=n-2
    i = last_i = 0 # starting city is index 0
    while True:
        j = succ[i]
        t=0
        # do not exceed subproblem and the limits of the neighborhood
        while t<r and succ[succ[j]] != last_i:
            k = succ[j]
            u=0
            while u<r and succ[k] != last_i:
                delta = d[i][succ[j]] + d[j][succ[k]] + d[k][succ[i]] \
                        -d[i][succ[i]] - d[j][succ[j]] - d[k][succ[k]]
                if delta < 0: # Is there an improvement?
                    length += delta # Perform move
                    succ[i], succ[j], succ[k] = succ[j], succ[k], succ[i]
                    j, k = k, j # Replace j between i and k
                    last_i = i
                u += 1
                k = succ[k] # Next k
            t += 1
            j = succ[j] # Next j
        i = succ[i] # Next i

        if i == last_i: # A complete tour scanned without improvement
            break

    return succ, length







######### Local search with 3-opt neighborhood and first improvement policy
def tsp_3opt_first(d, succ, length):
    last_i, last_j, last_k = 0, succ[0], succ[succ[0]]
    i, j, k = last_i, last_j, last_k
    while True:
        delta = d[i][succ[j]] + d[j][succ[k]] + d[k][succ[i]] \
            -d[i][succ[i]] - d[j][succ[j]] - d[k][succ[k]] # Move cost
        if delta < 0: # is there an improvement?
            length += delta # Update solution cost
            succ[i], succ[j], succ[k] = succ[j], succ[k], succ[i]# Perform move
            j, k = k, j      # Replace j between i and k
            last_i, last_j, last_k = i, j, k
        k = succ[k]    #next k
        if k == i: # k at its last value, next j
            j = succ[j]; k = succ[j]
        if k == i: # j at its last value, next i
            i = succ[i]; j = succ[i]; k = succ[j]
        if i == last_i and j == last_j and k == last_k:
            break
        
        #print('length =', length)
    return succ, length


def greedy_optimalTSPtoVRP(solution, length):
    solution, length = tsp_2opt_first(distances, solution, length)
    print('Cost of solution found with 2-opt first: {:d}'.format(length))

    
    succ = tsp_tour_to_succ(solution)
    succ, length = tsp_3opt_limited(distances, 25, succ, length)


    solution = tsp_succ_to_tour(succ)
    print('Cost of solution found with 2-opt first and 3-opt limited: {:d}'.format(length))
    


    '''
    successors = tsp_tour_to_succ(solution)
    
    successors, length = tsp_3opt_first(distances, successors, length)
    solution = tsp_succ_to_tour(successors)
    print('Solution improved with 3-opt first: {:d}'.format(length))
    '''
    
    
    ####### transform TSP tour to VRP tour (greedy)
    tour = [[]]
    for i in range(K):
        tour.append([0])
    route_length = [0]
    for i in range(K):
        route_length.append(0)
    #print(route_length)
    k = 1
    i = 1
    while k < K:
        route_length[k] = route_length[k] + distances[tour[k][len(tour[k])-1]][solution[i]]
        tour[k].append(solution[i])
        i = i + 1
        while route_length[k] + distances[tour[k][len(tour[k])-1]][solution[i]] - distances[0][tour[k][1]]<= length/K:
            #print(route_length)
            #tour[k].append(solution[i])
            route_length[k] = route_length[k] + distances[tour[k][len(tour[k])-1]][solution[i]]
            tour[k].append(solution[i])
            i += 1
            if i > N:
                break
            #print(i)
            if route_length[k] + distances[tour[k][len(tour[k])-1]][solution[i]] - distances[0][tour[k][1]]> length/K:
                k += 1
                break
            if k > K-1:
                break

    for j in range(i, N+1):
        tour[k].append(solution[j])
    
    route_length = vrp_route_length(distances, tour)
    tour_length = vrp_tour_length(distances, tour)
    print('route_length = ', route_length)
    print('length =', tour_length)

    return tour, route_length, tour_length

###########################################################

###weight 2-opt move

##### calculate delta
def weight_pseudo_move_2opt_first(d, tour, k, i, j):
    a = copy.deepcopy(tour)
    m = copy.deepcopy(i)
    n = copy.deepcopy(j)
    ka = copy.deepcopy(k)
    m = m+1
    while m<n:
        #print('i = ', i, ', j =', j)
        #print('k =', k)
        a[ka][m], a[ka][n] = a[ka][n], a[ka][m]
        m, n = m+1, n-1
    return w1*(vrp_tour_length(d, a) - vrp_tour_length(d, tour)) + w2*(max(vrp_route_length(d, a)[1:]) - max(vrp_route_length(d, tour)[1:])) # type: ignore



##### find delta
def weight_delta_of_2opt_first(d, tour):
    k = 1
    delta = float('inf')
    while k < K+1:
        n = len(tour[k])
        max_len_seq = n-2

        i = 0
        while max_len_seq >= n-2:
            j = i+max_len_seq
            if j<n and (i>0 or j<n-1) and i != j:
                #print('k =', k)
                #a = max(vrp_route_length(d, tour)[1:])
                #b = pseudo_move_2opt_first(d, tour, k, i, j)
                delta = weight_pseudo_move_2opt_first(d, tour, k, i, j)
                #print('delta = ', delta)
                #print('delta = ', delta)
                if delta < 0:
                    #print('delta = ', delta)
                    return delta, k, i, j

            i += 1
            if i == n-max_len_seq:   #next max_len_seq
                max_len_seq -= 1
        k+=1
    i = -1
    j = -1
    return delta, k, i, j


def weight_perform_2opt_first(d, tour, route_length, length, delta, k, i, j):
    #delta, k, i, j = delta_of_2opt_first(d, tour)
    #print('tour =', tour)
    if delta < 0:
        #print('O')
        i = i+1
        while i<j:
            tour[k][i], tour[k][j] = tour[k][j], tour[k][i]
            i, j = i+1, j-1
    #print('tour =', tour)
    #print('check =', route_length)
    route_length = vrp_route_length(d, tour)
    #print('check =', route_length)
    length = sum(route_length[1:]) # type: ignore
    return tour, route_length, length
####




###weight swap

##### calculate delta
def weight_pseudo_swap(d, tour, k1, k2, i, j):
    Tour = copy.deepcopy(tour)
    K1 = copy.deepcopy(k1)
    K2 = copy.deepcopy(k2)
    I = copy.deepcopy(i)
    J = copy.deepcopy(j)
   
    Tour[K1][I], Tour[K2][J] = Tour[K2][J], Tour[K1][I]

    return w1*(vrp_tour_length(d, Tour) - vrp_tour_length(d, tour)) + w2*(max(vrp_route_length(d, Tour)[1:]) - max(vrp_route_length(d, tour)[1:])) # type: ignore



##### find delta
def weight_delta_of_swap(d, tour):
    k1 = 1
    i = 1
    while k1 < K:
        k2 = k1 + 1
        n1 = len(tour[k1])
        n2 = len(tour[k2])
        j = 1
        while j < n2 and i < n1:
            n1 = len(tour[k1])
            n2 = len(tour[k2])
            '''
            print('k1 = ', k1)
            print('k2 =', k2)
            print('i =', i)
            print('j =', j)
            print('len(tour[k1] =', len(tour[k1]))
            print('len(tour[k2] = ', len(tour[k2]))
            print(' ')
            '''
            delta = weight_pseudo_swap(d, tour, k1, k2, i, j)
            if delta < 0:
                return delta, k1, k2, i, j
            
            j += 1
            if j == n2:
                k2 += 1
                j = 1
            if k2 == K+1:
                i += 1
                j = 1
                k2 = k1 + 1

            if i == n1:
                i = 1
                break
        k1 += 1
    return float('inf'), -1, -1, -1, -1

def weight_perform_swap(d, tour, route_length, length, delta, k1, k2, i, j):
    if delta < 0:
        tour[k1][i], tour[k2][j] = tour[k2][j], tour[k1][i]
        route_length = vrp_route_length(d, tour)
        length = vrp_tour_length(d, tour)
    return tour, route_length, length
####



###weight relocate


##### calculate delta
def weight_pseudo_relocate(d, tour, k1, k2, i, j):
    Tour = copy.deepcopy(tour)
    K1 = copy.deepcopy(k1)
    K2 = copy.deepcopy(k2)
    I = copy.deepcopy(i)
    J = copy.deepcopy(j)
    
    temp = Tour[K1].pop(I)
    Tour[K2].insert(J+1, temp)
    return w1*(vrp_tour_length(d, Tour) - vrp_tour_length(d, tour)) + w2*(max(vrp_route_length(d, Tour)[1:]) - max(vrp_route_length(d, tour)[1:])) # type: ignore



##### find delta
def weight_delta_of_relocate(d, tour):
    delta = [float('inf'), float('inf')]
    k1 = 1
    while k1 < K+1:
        for i in range(1, len(tour[k1])-1):    
            for k2 in range(1, K+1):
                #print('k2 =', k2)
                if k1 == k2:
                    continue
                if k1 == k2 == K:
                    return False
                for j in range(len(tour[k2])-1):
                    n1 = len(tour[k1])
                    n2 = len(tour[k2])

                    delta = weight_pseudo_relocate(d, tour, k1, k2, i, j)
                    if delta < 0 and len(tour[k1]) > 2:
                        return delta, k1, k2, i, j
        k1 += 1
    return delta, -1, -1, -1, -1

def weight_perform_relocate(d, tour, route_length, length, delta, k1, k2, i, j):
    if delta < 0:
        temp = tour[k1].pop(i)
        tour[k2].insert(j+1, temp)

        length = vrp_tour_length(d, tour)
        route_length = vrp_route_length(d, tour)
    return tour, route_length, length
####



###weighted inter2opt


##### calculate delta
def weight_pseudo_inter2opt(d, tour, k1, k2, i, j):
    Tour = copy.deepcopy(tour)
    K1 = copy.deepcopy(k1)
    K2 = copy.deepcopy(k2)
    I = copy.deepcopy(i)
    J = copy.deepcopy(j)
    Tour[K1][I:], Tour[K2][J:] = Tour[K2][J:], Tour[K1][I:]

    return w1*(vrp_tour_length(d, Tour) - vrp_tour_length(d, tour)) + w2*(max(vrp_route_length(d, Tour)[1:]) - max(vrp_route_length(d, tour)[1:])) # type: ignore


##### find delta
def weight_delta_of_inter2opt(d, tour):
    #return 1e9, -1, -1, -1, -1
    delta = 1e9
    k1 = 1
    while k1 < K+1:
        #print('k1 =', k1)
        if k1 == K:
            break
        for i in range(1, len(tour[k1])):
            for k2 in range(k1+1, K+1):
                for j in range(1, len(tour[k2])):
                    if (i==1 and j==1) or (i == len(tour[k1])-1 and j == len(tour[k2])-1):
                        continue
                    delta = weight_pseudo_inter2opt(d, tour, k1, k2, i, j)
                    #print('delta =', delta)
                    #print('i =', i)
                    #print('k1=', k1, ', k2=', k2)
                    if delta < 0:
                        return delta, k1, k2, i, j
        k1 = k1 + 1
    return 1e9, -1, -1, -1, -1

def weight_perform_inter2opt(d, tour, route_length, length, delta, k1, k2, i, j):
    if delta < 0:
        tour[k1][i:], tour[k2][j:] = tour[k2][j:], tour[k1][i:]
        route_length = vrp_route_length(d, tour)
        length = vrp_tour_length(d, tour)
    return tour, route_length, length




def weightedCPU():
    x =  weight_delta_of_2opt_first(distances, tour)
    y =  weight_delta_of_swap(distances, tour)
    z = weight_delta_of_relocate(distances, tour)
    t = weight_delta_of_inter2opt(distances, tour)


    #### list of delta (potential moves)
    lst = [x[0], y[0], z[0], t[0]] # type: ignore
    if min(lst) < 0:
        mini = lst.index(min(lst))
        a = None
        if mini == 0:
            a = x
        elif mini == 1:
            a = y
        elif mini == 2:
            a = z
        elif mini == 3:
            a = t
        return True, mini, a
    return False, None, None

def weight_perform(d, tour, route_length, length, mini, a):
    if mini == 0:
        delta, k, i, j = a
        tour, route_length, length = weight_perform_2opt_first(d, tour, route_length, length, delta, k, i, j)
    elif mini == 1:
        delta, k1, k2, i, j = a
        tour, route_length, length = weight_perform_swap(d, tour, route_length, length, delta, k1, k2, i, j)
    elif mini == 2:
        delta, k1, k2, i, j = a
        tour, route_length, length = weight_perform_relocate(d, tour, route_length, length, delta, k1, k2, i, j)
    elif mini == 3:
        delta, k1, k2, i, j = a
        tour, route_length, length = weight_perform_inter2opt(d, tour, route_length, length, delta, k1, k2, i, j)
    return tour, route_length, length



def weight_improvement_heuristics(d, tour, route_length, length):
    global execution_time
    iterations = 1
    while True:
        if execution_time > 200:
            ######time limit
            break

        st = time.time()
        bo, mini, a = weightedCPU()
        if bo:
            tour, route_length, length = weight_perform(d, tour, route_length, length, mini, a)       
            
            delta_time = time.time() - st
            execution_time += delta_time

            print('iteration ', iterations)
            print('max route_length=', max(route_length[1:]))
            print('length =', length)
            print(' ')
            #writeSolution("FINALsol.txt", tour)

        else:
            break
        
        iterations += 1
    return tour, route_length, length







########## input_(filename)
N, K, distances = input_("C:\\Users\\admin\\OneDrive\\Máy tính\\Mini-project\\input\\1000_20.txt")
n = N+1

w1 = 0.00005
w2 = 1 - w1

solution = rand_permutation(n)
length = tsp_length(distances, solution)

start_time = time.time()
tour, route_length, tour_length = greedy_optimalTSPtoVRP(solution, length)
execution_time = time.time() - start_time



##### Use this line if you want to improve solution even more with local search for VRP(time limit = 200 seconds)
#tour, route_length, tour_length = weight_improvement_heuristics(distances, tour, route_length, length)




print(max(route_length[1:]))

####### writeSolution(filename, tour)
writeSolution("FINALsol.txt", tour)

print("Execution time: ", execution_time)


