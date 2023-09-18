from ortools.sat.python import cp_model
import sys
import time

def input_():
    [N, K] = [int(x) for x in sys.stdin.readline().split()]
    d = []
    for i in range(N+1):
        r = [int(x) for x in sys.stdin.readline().split()]
        d.append(r)
    return N, K, d

def inputFromFile(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
        [N, K] = [int(x) for x in lines[0].split()]
        d = []
        for i in range(1, N+2):
            d.append([int(x) for x in lines[i].split()])
    return N, K, d

def writeToFile(filename, tour):
    with open("ILPsolution.txt", "w") as f:
        f.write(str(K))
        f.write("\n")
        result = ''
        for k in range(1, K+1):
            s = ''
            s += str(len(tour[k]))
            s += '\n'
            for i in tour[k]:
                s = s + str(i) + ' '
            s = s + '\n'
            result += s
        f.write(result)



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





def findZcp(X, z, model):
    for k in range(1, K+1):
        model.Add(z>=sum(X[i][j][k]*d[i][j] for i in range(N+1) for j in range(N+1))) # type: ignore
    model.Minimize(z)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver.ObjectiveValue()




def CreateVariables(model):
    X = [[[model.NewBoolVar('X( ' + str(i) + ',' + str(j) + ',' + str(b) + ')') for b in range(K+1)]for j in range(N+1)] for i in range(N+1)]
    z = model.NewIntVar(0, 100000000, 'z')
    return X, z

def VRP_SEC(SECs):
    model = cp_model.CpModel()
    X, z = CreateVariables(model)

    for S in SECs:
        for k in range(1, K+1):        
            model.Add(sum([X[i][j][k] for i in S for j in S]) <= len(S)-1)
        

    for k in range(1, K+1):
        for i in range(N+1):
            model.Add(X[i][i][k] == 0)
    
    for i in range(1, N+1):
        model.AddExactlyOne([X[i][j][k] for k in range(1, K+1) for j in range(N+1)])
    for k in range(1, K+1):
        model.AddExactlyOne([X[0][j][k] for j in range(N+1)])

    for k in range(1, K+1):
        for h in range(1, N+1):
            model.Add(sum([X[i][h][k] for i in range(N+1)]) == sum([X[h][i][k] for i in range(N+1)]))

    for k in range(1, K+1):
        model.AddExactlyOne([X[i][0][k] for i in range(N+1)])
    
    Z = int(findZcp(X, z, model))
    for k in range(1, K+1):
        model.Add(sum(X[i][j][k]*d[i][j] for i in range(N+1) for j in range(N+1))<=Z)
    
    model.Minimize(sum(X[i][j][k]*d[i][j] for i in range(N+1) for j in range(N+1) for k in range(1, K+1)))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status != cp_model.OPTIMAL:
        #print('cannot find optimal solution')
        return None
    else:
        #print('optimal value sub-problem = ', solver.ObjectiveValue())
        result = solver.ObjectiveValue()
    s = [[[solver.Value(X[i][j][k]) for k in range(K+1)] for j in range(N+1)] for i in range(N+1)]
    return s, result


def findNext(X, current, cand, k):
    for i in cand:
        if X[current][i][k] > 0:
            return i
    return -1

def getFirst(X, cand, k):
    for i in cand:
        for j in cand:
            if X[i][j][k] > 0:
                return i
    return -1

def getSpecial(X, cand, k):
    for i in cand:
        if X[0][i][k] > 0:
            return i
    return -1


def belongTo(X, i):
    for k in range(1, K+1):
        for j in range(N+1):
            if X[i][j][k] > 0:
                return k


def getFirstNode(X, cand, k):
    for j in cand:
        if X[0][j][k] > 0:
            return j
    return -1



def checkGlobalTour(X):
    cand = set()
    for i in range(1, N+1):
        cand.add(i)
    visited = set()
    visited.add(0)
    c = set()
    for i in range(1, N+1):
        c.add(i)
    for k in range(1, K+1):
        current = getFirstNode(X, cand, k)
        
        visited.add(current)
        #print('visited =', visited)
        #print('Before diaster k =', k)
        #print('Before disaster current =', current)
        c.remove(current)
        #print('c=', c)
        while True:
            next = findNext(X, current, c, k)
            if next == -1:
                break
            visited.add(next)
            c.remove(next)
            current = next
    #print('visited =', visited)
    if len(visited) == N+1:
        return True
    return False   

        


def ExtractSubTour(X):
    if checkGlobalTour(X):
        return None


    #extract all the subtour in S of X'''


    S = []
    cand = set()
    for i in range(1, N+1):
        cand.add(i)
    
    for k in range(1, K+1):
        T = [set() for i in range(10)]
        #T[0].add(0)
        #consider the path that includes depot 0
        current = getSpecial(X, cand, k)
        while True:
            if current == -1:
                break
            T[0].add(current)
            cand.remove(current)
            next = findNext(X, current, cand, k)
            current = next

            #print('T =', T)
        cnt = 1
        while len(cand) > 0:
        #if len(cand) != 0:
            current = getFirst(X, cand, k)
            if current == -1:
                break
            #print('debug 1 current',)
            while True:
                if current == -1:
                    break
                T[cnt].add(current)
                #print('debug current =', current)
                #print('debug next =', next)
                #print('debug cand =', cand)
                cand.remove(current)
                next = findNext(X, current, cand, k)
                current = next
                
                #print('0 T =', T)
            #print('done')
            cnt += 1
        #print('S =', S)
        '''
        for Ti in T:
            if Ti != set() and Ti not in S:
                S.append(Ti)
        '''


        
        #FIXED
        if T[0] != set():
            for i in range(1, 10):
                if T[i] != set():
                    S.append(T[i])
                    S.append(T[0])
                    #print('S =', S)
        
            
        
        #print('S =', S)
    #if checkGlobalTour(X):
        #return None
    return S

def printSolution(solution):
    tour = [[]]
    #optimalValue = 0
    print(K)
    for k in range(1, K+1):
        
        '''
        for i in range(N+1):
            for j in range(N+1):
                if solution[i][j][k] > 0:
                    print('X(' + str(i) + ',' +str(j)+','+str(k) + ') = 1')
                    sum += solution[i][j][k] * d[i][j]
        '''

        #optimalValue += sum
        res = extractSolution(solution, k)
        res = [int(x) for x in res.split()]
        tour.append(res)
        #print('Total distance taken of ' + str(k) + ': ', sum)
        #print('    ')
    #print('---------------')
    #print(' optimal value: ', optimalValue)
    return tour
def extractSolution(solution, k):
    res = ''
    #print(str(0) + '', end=' ')
    res = res + str(0) + ' '
    visited = set()
    for i in range(1, N+1):
        visited.add(i)
    current = getFirstNode(solution, visited, k)
    visited.remove(current)
    #print(str(current)+'', end=' ')
    res = res + str(current) + ' '
    count = 2
    while True:
            next = findNext(solution, current, visited, k)
            if next == -1:
                break
            visited.remove(next)
            #print(str(next)+'', end=' ')
            res = res + str(next) +' '
            count += 1
            current = next
    print(count)
    print(res)
    return res
    






def VRP():
    global tour
    SECs = []
    while True:
        solution = VRP_SEC(SECs)[0] #type: ignore
        #printSolution(solution)


        if solution == None:
            #print('Not feasible')
            break
        S = ExtractSubTour(solution)
        if S == None:
            #print(VRP_SEC(SECs)[1]) #type: ignore
            #print('found optimal solution')
            #print()
            tour = printSolution(solution)
            
            break
        for Si in S:
            if Si not in SECs:
                SECs.append(Si)
        #print(SECs)




N, K, d = input_()
#N, K, d = inputFromFile("6_2.txt")


start_time = time.time()
VRP()



print('max route_length =', max(vrp_route_length(d, tour)[1:]))
print('total length =', vrp_tour_length(d, tour))

print("Execution time: %s seconds ---" % (time.time() - start_time))

#print(tour)


###### write solution to file
writeToFile("CPsolution.txt", tour)