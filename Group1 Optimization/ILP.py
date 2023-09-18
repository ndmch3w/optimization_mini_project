import time
import sys
from ortools.linear_solver import pywraplp


class SubSetGenerator:
    def __init__(self, N):
        self.N = N
        self.x = [0 for i in range(N+1)]
    

    def __CollectSubset__(self):
        #print(self.x)
        S = []
        for i in range(1, self.N+1):
            if self.x[i] == 1:
                S.append(i)
        return S

    def GenerateFirstSubset(self):
        '''
        S = []
        for i in range(1, self.N + 1):
            if self.x[i] == 1:
                S.append(i)
        return S
        '''
        return self.__CollectSubset__()

    def GenerateNextSubset(self):
        N = self.N
        x = self.x
        i = N
        while i>= 1 and x[i] == 1:
            i -= 1
        if i == 0:
            return None
        x[i] = 1
        for j in range(i+1, N + 1):
            x[j] = 0
        return self.__CollectSubset__()

def input_():
    [N, K] = [int(x) for x in sys.stdin.readline().split()]
    d = []
    for i in range(N+1):
        r = [int(x) for x in sys.stdin.readline().split()]
        d.append(r)
    return N, K, d

#N, K, d = input_()
with open("1.txt", "r") as f:
    lines = f.readlines()
    [N, K] = [int(x) for x in lines[0].split()]
    d = []
    for i in range(1, N+2):
        d.append([int(x) for x in lines[i].split()])


#solver = pywraplp.Solver.CreateSolver('CBC')
solver = pywraplp.Solver.CreateSolver('SCIP')
X = [[[solver.IntVar(0,1,'X( ' + str(i) + ',' + str(j) + ',' + str(b) + ')') for b in range(K+1)]for j in range(N+1)] for i in range(N+1)]
z = solver.IntVar(0, 1e9, 'z')


m = K

############################






########################



start_time = time.time()
#Constraint 1:

for i in range(1, N+1):
    c = solver.Constraint(1,1)
    for k in range(1, K+1):
        for j in range(0, N+1):
            if i != j:
                c.SetCoefficient(X[i][j][k], 1)



#Constraint 2:
for k in range(1, m+1):
    c = solver.Constraint(1,1)
    for j in range(1, N+1):
        if j != 0:
            c.SetCoefficient(X[0][j][k], 1)

#Constraint 3:
for h in range(1, N+1):
    for k in range(1, m+1):
        c = solver.Constraint(0, 0)
        for i in range(N+1):
            if i != h:
                c.SetCoefficient(X[i][h][k], 1)
        for j in range(N+1):
            if j != h:
                c.SetCoefficient(X[h][j][k], -1)

'''
#Constraint 4:
for h in range(1, N+1):
    for k in range(1, m+1):
        c = solver.Constraint(1, 1)
        for i in range(N+1):
            if i != h:
                c.SetCoefficient(X[h][i][k], 1)
'''


#Constraint 5:
SG = SubSetGenerator(N)
S = SG.GenerateFirstSubset()

while True:
    #print(S)
    if len(S) >= 2 and len(S)<N:        
        for k in range(1, m+1):
            c = solver.Constraint(0, len(S) - 1)
            for i in S:
                for j in S:
                    if i != j:
                        c.SetCoefficient(X[i][j][k], 1)
        
    S = SG.GenerateNextSubset()
    if S == None:
        break









#Constraint 6:

for k in range(1, m+1):
    c = solver.Constraint(1, 1)
    for i in range(1, N+1):
        if i != 0:
            c.SetCoefficient(X[i][0][k], 1)
#####

##### Find Z

for k in range(1, K+1):
        c = solver.Constraint(0, 15)
        for i in range(N+1):
            for j in range(N+1):
                if i != j:
                    c.SetCoefficient(X[i][j][k], -d[i][j])
        c.SetCoefficient(z, 1)



Z = 99
objective = solver.Objective()
objective.SetCoefficient(z, 1)
result_status = solver.Solve()
if result_status != pywraplp.Solver.OPTIMAL:
    print('cannot find optimal solution')
else:
    Z = solver.Objective().Value()
#############



#FOR Z1 objective function - constraint
for k in range(1, K+1):
    c = solver.Constraint(0, Z)
    for i in range(N+1):
        for j in range(N+1):
            if i != j:
                c.SetCoefficient(X[i][j][k], d[i][j])

##### Resolve 
#objective = solver.Objective()
for i in range(N+1):
    for j in range(N+1):
        for k in range(m+1):
            if i != j:
                objective.SetCoefficient(X[i][j][k], d[i][j])
#######









result_status = solver.Solve()
if result_status != pywraplp.Solver.OPTIMAL:
    print('cannot find optimal solution')
else:
    print('optimal objective value = ', solver.Objective().Value()-Z)
    print()
    for k in range(1, K+1):
        sum = 0
        for i in range(N+1):
            for j in range(N+1):
                if X[i][j][k].solution_value() != 0:
                    print('x(' + str(i) + ',' + str(j) + ','+str(k)+')', X[i][j][k].solution_value())
                    sum += X[i][j][k].solution_value() * d[i][j]
        print('Total distance taken of ' + str(k) + ': ', sum)



print("Execution time: %s seconds ---" % (time.time() - start_time))


#print(Z)