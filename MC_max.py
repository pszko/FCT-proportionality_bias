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

with open(path + 'list_i.txt', 'r') as filehandle:
    list_i = json.load(filehandle)

with open(path + 'list_j.txt', 'r') as filehandle:
    list_j = json.load(filehandle)

with open(path + 'list_ig.txt', 'r') as filehandle:
    list_ig = json.load(filehandle)

with open(path + 'list_jh.txt', 'r') as filehandle:
    list_jh = json.load(filehandle)

with open(path + 'list_f.txt', 'r') as filehandle:
    list_f = json.load(filehandle)


# ---Simulating maximum bias in factor content of trade-------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Defining reshuffling in lists
def reshuffle(count, ent_list):
    coor = [int(np.random.rand() * count)]
    ent = ent_list[coor[0]]
    ent_list[coor[0]], ent_list[count - 1] = ent_list[count - 1], ent_list[coor[0]]
    count -= 1
    return ent, count, ent_list

# ---Defining imputation for maximum factor content of trade
def shaking(list_ig, list_jh, VXMD_igj, VIFM_gjh, VDFM_igjh):
    shake_mx  = np.zeros((len(list_ig), len(list_jh)))
    VXMD = VXMD_igj.copy()
    VIFM = VIFM_gjh.copy()

    i_count = 140
    i_list = np.arange(i_count).tolist()
    while i_count >= 1 :
        i, i_count, i_list = reshuffle(i_count, i_list)

        g_count = 57
        g_list = np.arange(g_count).tolist()
        while g_count >= 1 :
            g, g_count, g_list = reshuffle(g_count, g_list)

            j_count = 140
            j_list = np.arange(j_count).tolist()
            while j_count >= 1 :
                j, j_count, j_list = reshuffle(j_count, j_list)

                if VXMD[i*57+g, j] == 0:
                    continue
                else:
                    h_count = 57
                    h_list = np.arange(h_count).tolist()
                    while h_count >= 1 :
                        h, h_count, h_list = reshuffle(h_count, h_list)

                        if VIFM[g, j*57+h] == 0:
                            continue

                        elif VIFM[g, j*57+h] < VXMD[i*57+g, j]:
                            shake_mx[i*57+g, j*57+h] += VIFM[g, j*57+h]
                            VXMD[i*57+g, j] -= VIFM[g, j*57+h]
                            VIFM[g, j*57+h] -= VIFM[g, j*57+h]
                            continue

                        else:
                            shake_mx[i*57+g, j*57+h] += VXMD[i*57+g, j]
                            VIFM[g, j*57+h] -= VXMD[i*57+g, j]
                            VXMD[i*57+g, j] -= VXMD[i*57+g, j]
                            continue
    return shake_mx

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

# ---Defining the Leontief inverse with {F_i  = D〖(I-B)〗^(-1) T_i}
def leontief(VFM, box, trade):
    c = VFM.sum(axis = 0) + box.sum(axis = 0)
    io_mx = np.divide(1, c, out=np.zeros_like(c), where=c!=0)
    factors = VFM * io_mx
    io = box * io_mx
    I = np.identity(io.shape[0], dtype = float)
    B = I - io
    return np.matmul(factors, np.linalg.solve(B,trade))

# ---Defining mean absolute percent error
def MAPE(tz_fct, sim_fct):
    tz_fct, sim_fct = np.array(tz_fct), np.array(sim_fct)
    return (np.abs((tz_fct - sim_fct) / tz_fct)) * 100

# ---Defining mean of the mean absolute percent error
def MMAPE(tz_fct, sim_fct):
    tz_fct, sim_fct = np.array(tz_fct), np.array(sim_fct)
    return (np.mean(np.abs((tz_fct - sim_fct) / tz_fct))) * 100

# ---Running MC simulations based on MC_count
MC_count = 10000
sim_dict = {}
MAPE_dict = {}
MPE_dict = {}

for x in range(MC_count):
    print("sim: ", x)
    shake = shaking(list_ig, list_jh, VXMD_igj, VIFM_gjh, VDFM_igjh)

    box = VDFM_igjh + shake
    trade = trade_mx(shake, VXMD_igj, list_j)

    sim = leontief(VFM, box, trade)
    # sim_df = pd.DataFrame(data = sim, index = list_f, columns = new_list_j)
    # sim_dict[x] = sim_df

    MMAPEc = MMAPE(tz_fct, sim)
    # MAPEc_df = pd.DataFrame(data = MAPEc, index = list_f, columns = new_list_j)
    # MAPE_dict[x] = MAPEc_df
    print(MMAPEc)
    # if MMAPEc > 200:
    #     box_df = pd.DataFrame(data = shake)
    #     box_df.to_csv(path + 'box_' + str(x) + '.csv')

# ---Outputting simulation values
simulations = sim_dict[0]
for x in range(1, MC_count):
    simulations = simulations.join(sim_dict[x])
simulations.to_csv(path + 'MC_sim_max.csv')

# ---Outputting MAPE values
MAPEs = MAPE_dict[0]
for x in range(1, MC_count):
    MAPEs = MAPEs.join(MAPE_dict[x])
MAPEs.to_csv(path + 'MC_MAPEs_max.csv')

print("\n Simulating maximum factor content of trade", stopwatch.elapsed())
# ---Time: 1381.717


# ---Simulating requirement estimation------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

MCs = simulations

# ---Defining simulation requirement estimation
def n(data, Z, E):
    count = pd.DataFrame.count(data, axis = 1)
    mean = pd.DataFrame.mean(data, axis = 1)
    std = pd.DataFrame.std(data, axis = 1)
    sx = std/(count**1/2)
    upper = mean + Z * sx
    lower = mean - Z * sx
    climit = upper - lower
    n_count = ((std * Z) / E)**2
    return n_count

# ---Estimating requires simulation count for Z = 1.645 and E = 5
reqs_dict = {}
for a, j in enumerate(list_j):
    x = MCs.filter(regex = j)
    reqs_dict[a] = n(x, 1.645, 5).values

reqs_arr = reqs_dict[0]
for b in range(1, len(list_j)):
    reqs_arr = np.vstack((reqs_arr, reqs_dict[b]))

reqs_arr = reqs_arr.transpose()

# ---Outputting requirements
reqs_df = pd.DataFrame(data = reqs_arr, index = list_f, columns = list_j)
# reqs_df.to_csv(path + 'reqs.csv')

# ---printing requirements
print(reqs_df.max(axis=1))

print("\n Simulating maximum factor content of trade", stopwatch.elapsed())
# ---Time: 0.04
