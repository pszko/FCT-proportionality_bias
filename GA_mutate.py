from __init__ import *

# ---Loading data
tz_fct = pd.read_csv (path + 'FCT_prop.csv', index_col = 'Unnamed: 0')
tz_fct = tz_fct.values

VDFM_igjh = pd.read_csv (path + 'VDFM_igjh.csv', index_col = 'Unnamed: 0')
VDFM_igjh = VDFM_igjh.values

VFM = pd.read_csv (path + 'VFM_fjh.csv', index_col = 'Unnamed: 0')
VFM = VFM.values

VXMD_igj = pd.read_csv (path + 'VXMD_igj.csv', index_col = 'Unnamed: 0')
VXMD_igj = VXMD_igj.values

VIFM_gjh = pd.read_csv (path + 'VIFM_gjh.csv', index_col = 'Unnamed: 0')
VIFM_gjh = VIFM_gjh.values

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


# ---Performing GA with mutations-----------------------------------------------
# ------------------------------------------------------------------------------

# ---Defining the Leontief inverse with {F_i  = D〖(I-B)〗^(-1) T_i}
def leontief(VFM, box, trade):
    c = VFM.sum(axis = 0) + box.sum(axis = 0)
    io_mx = np.divide(1, c, out=np.zeros_like(c), where=c!=0)
    factors = VFM * io_mx
    io = box * io_mx
    I = np.identity(io.shape[0], dtype = float)
    B = I - io
    return np.matmul(factors, np.linalg.solve(B,trade))

# ---Defining the mean absolute percent error
def MAPE(tz_fct, sim_fct):
    tz_fct, sim_fct = np.array(tz_fct), np.array(sim_fct)
    return (np.abs((tz_fct - sim_fct) / tz_fct)) * 100

# ---Defining the column mean absolute percent error
def CMAPE(tz_fct, sim_fct):
    tz_fct, sim_fct = np.array(tz_fct), np.array(sim_fct)
    return (np.mean(np.abs((tz_fct - sim_fct) / tz_fct), axis = 0)) * 100

# ---Defining mean of the mean absolute percent error
def MMAPE(tz_fct, sim_fct):
    tz_fct, sim_fct = np.array(tz_fct), np.array(sim_fct)
    return (np.mean(np.abs((tz_fct - sim_fct) / tz_fct))) * 100

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


# ---Loading parent
parent = pd.read_csv (path + 'box_1.csv', index_col = 'Unnamed: 0')
parent = parent.values

# ---Parent fit
trade = trade_mx(parent, VXMD_igj, list_j)
B = VDFM_igjh + parent
fct = leontief(VFM,  B, trade)
col_fit_p = CMAPE(tz_fct, fct)
fit_p = MAPE(tz_fct, fct)
bias_p = MMAPE(tz_fct, fct)

# ---Mutating
count = 0
while count < 3300:
    print("Runtime", stopwatch.elapsed())
    stopwatch.start()
    print(count)
    child = shaking(list_ig, list_jh, VXMD_igj, VIFM_gjh, VDFM_igjh)
    trade = trade_mx(child, VXMD_igj, list_j)
    B = VDFM_igjh + child
    fct = leontief(VFM,  B, trade)
    col_fit_c = CMAPE(tz_fct, fct)
    fit_c = MAPE(tz_fct, fct)
    parent = np.empty((8,0))
    for z in range(140):
        if col_fit_p[z] > col_fit_c[z]:
            parent = np.concatenate((parent, fit_p[:,z].reshape((-1, 1))), axis=1)
        else:
            parent = np.concatenate((parent, fit_c[:,z].reshape((-1, 1))), axis=1)

    col_fit_p = np.mean(parent, axis = 0)
    fit_p = parent
    bias_c = np.mean(parent)
    print("bias_p: ", bias_p, "bias_c: ", bias_c)
    if bias_p == bias_c:
        count += 1
    else:
        bias_p = bias_c
        count = 0

# ---Outputting GA score
pop = pd.DataFrame(data = fit_p, index = list_f, columns = list_j)
pop.to_csv(path + 'GA_mutate_scores.csv')
