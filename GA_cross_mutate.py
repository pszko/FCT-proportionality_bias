from __init__ import *

# ---Loading data
VDFM_igjh = pd.read_csv (path + 'VDFM_igjh.csv', index_col = 'Unnamed: 0')
VDFM_igjh = VDFM_igjh.values

VFM = pd.read_csv (path + 'VFM_fjh.csv', index_col = 'Unnamed: 0')
VFM = VFM.values

VXMD_igj = pd.read_csv (path + 'VXMD_igj.csv', index_col = 'Unnamed: 0')
VXMD_igj = VXMD_igj.values

VIFM_gjh = pd.read_csv (path + 'VIFM_gjh.csv', index_col = 'Unnamed: 0')
VIFM_gjh = VIFM_gjh.values

tz_fct = pd.read_csv (path + 'FCT_prop.csv', index_col = 'Unnamed: 0')
tz_fct = tz_fct.values

with open(path + 'list_j.txt', 'r') as filehandle:
    list_j = json.load(filehandle)

# ---Performing GA with crossovers and mutations--------------------------------
# ------------------------------------------------------------------------------

# ---Defining bubble sorting
def bubbleSort(arr, x):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] < arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                x[j], x[j+1] = x[j+1], x[j]
    return arr, x

# ---Defining reverse bubble sorting single iteration for child
def reverseBubble(arr, x):
    i = len(arr)
    for j in range(i-1,0,-1):
        if arr[j-1] < arr[j] :
            arr[j-1], arr[j] = arr[j], arr[j-1]
            x[j-1], x[j] = x[j], x[j-1]
    return arr

# ---Defining the Leontief inverse with {F_i  = D〖(I-B)〗^(-1) T_i}
def leontief(VFM, box, trade):
    c = VFM.sum(axis = 0) + box.sum(axis = 0)
    io_mx = np.divide(1, c, out=np.zeros_like(c), where=c!=0)
    factors = VFM * io_mx
    io = box * io_mx
    I = np.identity(io.shape[0], dtype = float)
    B = I - io
    return np.matmul(factors, np.linalg.solve(B,trade))

# ---Defining mean of the mean absolute percent error
def MMAPE(tz_fct, sim_fct):
    tz_fct, sim_fct = np.array(tz_fct), np.array(sim_fct)
    return (np.mean(np.abs((tz_fct - sim_fct) / tz_fct))) * 100

# ---Defining mutation of segment
def mutate(n, VXMD_igj, VIFM_gjh):
    mutant = np.zeros((7980, 57))
    VXMD = VXMD_igj.copy()
    VIFM = VIFM_gjh.copy()

    j = n
    for h in range(57):
        g_count = 57
        g_list = np.arange(g_count)
        g_list = g_list.tolist()

        while g_count >= 1:
            g_coor = [int(np.random.rand() * g_count)]
            g = g_list[g_coor[0]]
            g_list[g_coor[0]], g_list[g_count - 1] = g_list[g_count - 1], g_list[g_coor[0]]
            g_count -= 1

            if VIFM[g, j*57+h] == 0:
                continue

            else:
                i_count = 140
                i_list = np.arange(i_count)
                i_list = i_list.tolist()

                while i_count >= 1 :
                    i_coor = [int(np.random.rand() * i_count)]
                    i = i_list[i_coor[0]]
                    i_list[i_coor[0]], i_list[i_count - 1] = i_list[i_count - 1], i_list[i_coor[0]]
                    i_count -= 1

                    if VXMD[i*57+g, j] == 0:
                        continue

                    else:
                        if VIFM[g, j*57+h] < VXMD[i*57+g, j]:
                            mutant[i*57+g, h] += VIFM[g, j*57+h]
                            VXMD[i*57+g, j] = VXMD[i*57+g, j] - VIFM[g, j*57+h]
                            VIFM[g, j*57+h] = 0
                            break

                        else:
                            mutant[i*57+g, h] += VXMD[i*57+g, j]
                            VIFM[g, j*57+h] = VIFM[g, j*57+h] - VXMD[i*57+g, j]
                            VXMD[i*57+g, j] = 0
    return mutant

# ---Defining crossover with mutation
def crossNmutate():
    cross = np.empty((7980, 0))
    order = []
    arr = np.arange(2)
    for x in range(70):
        order.append(arr[0])
        order.append(arr[1])
    order[-1] = 2
    np.random.shuffle(order)

    for n, group in enumerate(order):
        if group == 2:
            mutant = mutate(n, VXMD_igj, VIFM_gjh)
            cross = np.concatenate((cross, mutant), axis=1)
        else:
            parent = pop[group]
            parent_select = parent[:, n*57 : n*57 + 57]
            cross = np.concatenate((cross, parent_select), axis=1)
    return cross

# ---Defining trade vectors
def trade_mx(shake, VXMD_igj, list_j):
    exports = VXMD_igj.copy()
    imports_dict = {}
    for j in range(len(list_j)):
        imports_dict[j] = shake[j*57: j*57+56, :].sum(0)
    imports = imports_dict[0]
    for x in range(1, len(list_j)):
        imports = np.vstack((imports, imports_dict[x]))

    imports = imports.transpose()
    return exports - imports

# ---Loading initial population
pop = {}
for x in range(2):
    pop[x] = pd.read_csv (path + 'box_' + str(x) + '.csv', index_col = 'Unnamed: 0')
    pop[x] = pop[x].values

# ---Calculating parent factor content of trade
scores = []
for p in range(2):
    B = pop[p] + VDFM_igjh
    trade = trade_mx(pop[p], VXMD_igj, list_j)
    pop_leon = leontief(VFM,  B, trade)
    fit = MMAPE(tz_fct, pop_leon)
    scores = np.append(scores,fit)

# ---Sorting parents and matrix B's
scores, pop = bubbleSort(scores, pop)

# ---Crossing and mutating population
count = 0
while count < 3300 and np.allclose(scores, scores[1], rtol=1e-09, atol=1e-09) == False:
    print("Runtime", stopwatch.elapsed())
    stopwatch.start()
    child = crossNmutate()
    B = child + VDFM_igjh
    trade = trade_mx(child, VXMD_igj, list_j)
    child_fct = leontief(VFM, B, trade)
    fit = MMAPE(tz_fct, child_fct)
    if fit > scores[-1]:
        scores[-1] = fit
        pop[1] = child
        scores = reverseBubble(scores, pop)
        count = 0
        print('scores', scores)
    else:
        count += 1
        print('count', count)

# ---Outputting GA score
scores_GA = pd.DataFrame(data = scores)
scores_GA.to_csv(path + 'GA_cross_mutate_scores.csv', index = False, header = False)
