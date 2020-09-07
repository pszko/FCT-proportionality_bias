from __init__ import *

# ---Building proportionally imputed I/O----------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
VDFM_igjh = pd.read_csv (path + 'VDFM_igjh.csv', index_col = 'Unnamed: 0')

VXMD_igj = pd.read_csv (path + 'VXMD_igj.csv')

VIFM_2d = pd.read_csv (path + 'VIFM_2d.csv')

VFM = pd.read_csv (path + 'VFM_fjh.csv', index_col = 'Unnamed: 0')
VFM = VFM.values

with open(path + 'list_g.txt', 'r') as filehandle:
    list_g = json.load(filehandle)

with open(path + 'list_j.txt', 'r') as filehandle:
    list_j = json.load(filehandle)

with open(path + 'list_jh.txt', 'r') as filehandle:
    list_jh = json.load(filehandle)

with open(path + 'list_ig.txt', 'r') as filehandle:
    list_ig = json.load(filehandle)

with open(path + 'list_f.txt', 'r') as filehandle:
    list_f = json.load(filehandle)

# ---Setting sets of bilateral trade constraints
VXMD_dict = {}
VXMD = {}
for sector in list_g:
    VXMD_dict[sector] = VXMD_igj.loc[np.where(VXMD_igj['Unnamed: 0'].str.contains(sector))]
    VXMD_dict[sector] = VXMD_dict[sector].set_index('Unnamed: 0')

    for country in list_j:
        a = sector + "-" + country
        VXMD[a] = VXMD_dict[sector].filter(regex=country)

# ---Setting sets of imported input-output constraints
VIFM = {}
VIFM_sum = {}
for sector in list_g:
    VIFM_sec = VIFM_2d.loc[np.where(VIFM_2d['g'].str.contains(sector))]
    VIFM_sec = VIFM_sec.reset_index(drop=True)

    for country in list_j:
        a = sector + "-" + country
        VIFM[a] = VIFM_sec.loc[np.where(VIFM_sec['jh'].str.contains(country))]
        VIFM_sum[a] = sum(VIFM[a]["Value"])

# ---Imputing values based on constraints
for sector in list_g:
    for country in list_j:
        a = sector + "-" + country
        try:
            for index_io, row_io in VIFM[a].iterrows():
                calc = row_io[2] / VIFM_sum[a]
                if calc == 0:
                    continue
                else:
                    try:
                        y = VXMD[a]
                        for index_trade, row_trade in VXMD[a].iterrows():
                            if row_trade[0] == 0:
                                continue
                            else:
                                val = calc * row_trade[0]
                                VDFM_igjh.loc[index_trade, row_io[1]] = val
                    except:
                            print("VXMD[",a,"] not in scope")
        except:
            print("VIFM[",a,"] not in scope")

# ---Outputting tz_b
VDFM_igjh = VDFM_igjh[list_jh]
VDFM_igjh.to_csv(path + 'tz_b.csv')

print("\n Building proportionally imputed I/O", stopwatch.elapsed())
# ---Time: 8243.973


# ---Building trade matrix------------------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
tz_b = VDFM_igjh.values

VDFM_igjh = VDFM_igjh.values

VXMD_igj = VXMD_igj.set_index('Unnamed: 0')
VXMD_igj = VXMD_igj.values

# ---Removing domestic input-outputs
prop_tech = tz_b - VDFM_igjh

# ---Summing imports over j
imports_dict = {}
for j in range(len(list_j)):
    imports_dict[j] = prop_tech[j*57: j*57+56, :].sum(0)

imports = imports_dict[0]

for x in range(1, len(list_j)):
    imports = np.vstack((imports, imports_dict[x]))

# ---Transposing imports
imports = imports.transpose()

# ---Removing imports from exports
trade = VXMD_igj - imports

# ---Outputting trade
# trade_df = pd.DataFrame(data = trade, index = list_ig, columns = list_j)
# trade_df.to_csv(path + 'prop_trade.csv')

print("\n Building trade vector", stopwatch.elapsed())
# ---Time: 1294.039

# ---Calculating factor content of trade using the proportionality assumption---
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Defining the Leontief inverse with {F_i  = D〖(I-B)〗^(-1) T_i}
def leontief(VFM, box, trade):
    c = VFM.sum(axis = 0) + box.sum(axis = 0)
    io_mx = np.divide(1, c, out=np.zeros_like(c), where=c!=0)
    factors = VFM * io_mx
    io = box * io_mx
    I = np.identity(io.shape[0], dtype = float)
    B = I - io
    return np.matmul(factors, np.linalg.solve(B,trade))

# ---Calculating proportionality factor content of trade
fct = leontief(VFM, tz_b, trade)

# ---Outputting trade
fct_prop = pd.DataFrame(data=fct, index = list_f, columns = list_j)
fct_prop.to_csv(path + 'FCT_prop.csv')

print("\n Calculating factor content of trade using the proportionality assumption", stopwatch.elapsed())
# ---Time: 54.998
