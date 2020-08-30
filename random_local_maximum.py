from __init__ import *

# ---Loading data
VDFM_igjh = pd.read_csv (path + 'VDFM_igjh.csv', index_col = 'Unnamed: 0')
VDFM_igjh = VDFM_igjh.values

VXMD_igj = pd.read_csv (path + 'VXMD_igj.csv', index_col = 'Unnamed: 0')

VIFM_2d = pd.read_csv (path + 'VIFM_2d.csv')

VIFM_gjh = pd.read_csv (path + 'VIFM_gjh.csv', index_col = 'Unnamed: 0')
VIFM_gjh = VIFM_gjh.values

tz_fct = pd.read_csv (path + 'FCT_prop.csv', index_col = 'Unnamed: 0')
tz_fct = tz_fct.values

VFM = pd.read_csv (path + 'VFM_fjh.csv', index_col = 'Unnamed: 0')
VFM = VFM.values

with open(path + 'list_i.txt', 'r') as filehandle:
    list_i = json.load(filehandle)

with open(path + 'list_g.txt', 'r') as filehandle:
    list_g = json.load(filehandle)

with open(path + 'list_j.txt', 'r') as filehandle:
    list_j = json.load(filehandle)

with open(path + 'list_h.txt', 'r') as filehandle:
    list_h = json.load(filehandle)

with open(path + 'list_ig.txt', 'r') as filehandle:
    list_ig = json.load(filehandle)

with open(path + 'list_jh.txt', 'r') as filehandle:
    list_jh = json.load(filehandle)

with open(path + 'list_f.txt', 'r') as filehandle:
    list_f = json.load(filehandle)

# ---Preparing imported input-output constraints--------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Creating null matrix of size ig*jh
blank_VIFM_igjh_constraints  = np.zeros((len(list_ig), len(list_jh)))

# ---Creating null dataframe VIFM_igjh_constraints
VIFM_igjh_constraints = pd.DataFrame(data=blank_VIFM_igjh_constraints, index=list_ig, columns=list_jh)
VIFM_igjh_constraints.apply(pd.to_numeric)

# ---Setting imported input-output constraints
for index, row in VIFM_2d.iterrows():
    for i in list_i:
        VIFM_igjh_constraints.loc[i + "-" + row['g'], row['jh']] = row['Value']

# ---Removing final demand c, g, i constraints
VIFM_igjh_constraints = VIFM_igjh_constraints[list_jh]

# ---Outputting imported input-output constraints
# VIFM_igjh_constraints.to_csv(path + 'VIFM_igjh_constraints.csv')


# ---Preparing bilateral trade constraints--------------------------------------
# ------------------------------------------------------------------------------
# ---Creating null matrix of size ig*jh
blank_VXMD_igjh_constraints  = np.zeros((len(list_ig), len(list_jh)))

# ---Creating null dataframe VXMD_igjh_constraints
VXMD_igjh_constraints = pd.DataFrame(data=blank_VXMD_igjh_constraints, index=list_ig, columns=list_jh)
VXMD_igjh_constraints.apply(pd.to_numeric)

# ---Setting bilateral trade constraints
VXMD_igjh_constraints = pd.DataFrame()
for column in VXMD_igj:
    for h in list_h:
        df = VXMD_igj[column]
        df.rename(columns={column : column + "-" + h})
        VXMD_igjh_constraints[column + "-" + h] = df

# ---Outputting max_constraints
# VXMD_igjh_constraints.to_csv(path + 'VXMD_igjh_constraints.csv')


# ---Calculating Min from max contraints for each igjh--------------------------
# ------------------------------------------------------------------------------
# ---Extracting values from dataframes
VXMD_igjh_constraints = VXMD_igjh_constraints.values
VIFM_igjh_constraints = VIFM_igjh_constraints.values

# ---Calculating Min per igjh
max_constraint = np.fmin(VXMD_igjh_constraints, VIFM_igjh_constraints)

# ---Outputting max_constraints
# max_constrain_df = pd.DataFrame(data=max_constraint, index=list_ig, columns=list_jh)
# max_constrain_df.to_csv(path + 'max_constraints.csv')

print("\n Building Maximum contraints per igjh entry", stopwatch.elapsed())
# ---Time: 8627.236


# ---Building random local maximum----------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

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

# ---Building list of ig/jh values
igjh_list = []
for ig in list_ig:
    for jh in list_jh:
        igjh = ig + "/" + jh
        igjh_list.append(igjh)

# ---Creating null matrix of size igjh*1
igjh_df = np.zeros((len(igjh_list), 1))

# ---Building list of max constraints
for row in igjh_list:
    i_val = row.split('/')[0].split('-')[0]
    i = list_i.index(i_val)
    g_val = row.split('/')[0].split('-')[1]
    g = list_g.index(g_val)
    j_val = row.split('/')[1].split('-')[0]
    j = list_j.index(j_val)
    h_val = row.split('/')[1].split('-')[1]
    h = list_h.index(h_val)

    value = max_constraints[i*57+g, j*57+h]
    igjh_df[i*454860 + g*7980 + j*57 + h] = value

# ---Outputting list of max constraints
igjh_df = pd.DataFrame(data=igjh_df, index=igjh_list, columns=['Value'])
# igjh_df.to_csv(path + 'igjh_max.csv')

# ---Sorting list of max constraints
igjh_df_sorted = igjh_df.sort_values(by='Value', ascending=False)

# ---Outputting sorted list of max constraints
# igjh_df_sorted.to_csv(path + 'igjh_max_sorted.csv')

# ---Sorting constraints
igjh_list_sorted = igjh_df_sorted.index.tolist()
max_local = np.zeros((len(list_ig), len(list_jh)))

# ---Imputing values based on sorted constraints
for row in igjh_list_sorted:
    i_val = row.split('/')[0].split('-')[0]
    i = list_i.index(i_val)
    g_val = row.split('/')[0].split('-')[1]
    g = list_g.index(g_val)
    j_val = row.split('/')[1].split('-')[0]
    j = list_j.index(j_val)
    h_val = row.split('/')[1].split('-')[1]
    h = list_h.index(h_val)

    if VXMD_igj[i*57+g, j] < VIFM_gjh[g, j*57+h]:
        max_local[i*57+g, j*57+h] += VXMD_igj[i*57+g, j]
        VIFM_gjh[g, j*57+h] = VIFM_gjh[g, j*57+h] - VXMD_igj[i*57+g, j]
        VXMD_igj[i*57+g, j] = 0

    else:
        max_local[i*57+g, j*57+h] += VIFM_gjh[g, j*57+h]
        VXMD_igj[i*57+g, j] = VXMD_igj[i*57+g, j] - VIFM_gjh[g, j*57+h]
        VIFM_gjh[g, j*57+h] = 0

# ---Outputting random local optimum matrix B
max_local = VDFM_igjh + max_local
# max_local_df = pd.DataFrame(data = max_local, index = list_ig, columns = list_jh)
# max_local_df.to_csv(path + 'RLO.csv')

B = max_local - VDFM_igjh

trade = trade_mx(B, VXMD_igj, list_j)

# ---Calculating random local optimum factor content of trade
sim = leontief(VFM, max_local, trade)

# ---Outputting random local optimum
sim_df = pd.DataFrame(data = sim, index = list_f, columns = list_j)
sim_df.to_csv(path + 'MC_rlo.csv')

# ---Outputting random local optimum MAPE
MAPEc = MAPE(tz_fct, sim)
# print("MAPEc", MAPEc)
# MAPEM = MMAPE(tz_fct, sim)
# print("MAPEM", MAPEM)
MAPEc_df = pd.DataFrame(data = MAPEc, index = list_f, columns = list_j)
MAPEc_df.to_csv(path + 'MAPE_rlo.csv')

print("\n Building random local maximum", stopwatch.elapsed())
# ---Time: 1456.864
