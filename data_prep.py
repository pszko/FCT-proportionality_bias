from __init__ import *

# ---Seperating final demand from VDFM------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start() 

# ---Loading data
VDFM = pd.read_excel (path + 'VDFM.xlsx')

# ---Creating output dataframes
VDFM__c = pd.DataFrame(columns = ['dim1', 'dim2', 'dim3', 'Value'])
VDFM_FD = pd.DataFrame(columns = ['dim1', 'dim2', 'dim3', 'Value'])

# ---Iterating over VDFM rows and outputting to given dataframe
for index, row in VDFM.iterrows():
    if row['dim2'] == 'c':
        VDFM_FD = VDFM_FD.append({'dim1': row['dim1'], 'dim2': row['dim2'], 'dim3': row['dim3'], 'Value': row['Value']}, ignore_index=True)

    elif row['dim2'] == 'g':
        VDFM_FD = VDFM_FD.append({'dim1': row['dim1'], 'dim2': row['dim2'], 'dim3': row['dim3'], 'Value': row['Value']}, ignore_index=True)

    elif row['dim2'] == 'i':
        VDFM_FD = VDFM_FD.append({'dim1': row['dim1'], 'dim2': row['dim2'], 'dim3': row['dim3'], 'Value': row['Value']}, ignore_index=True)

    else:
        VDFM__c = VDFM__c.append({'dim1': row['dim1'], 'dim2': row['dim2'], 'dim3': row['dim3'], 'Value': row['Value']}, ignore_index=True)

# ---Outputting clean and final demand VDFM
# VDFM__c.to_csv(path + 'VDFM__c.csv', index=False)
# VDFM_FD.to_csv(path + 'VDFM_FD.csv', index=False)

print("\n Seperating final demand from VDFM", stopwatch.elapsed())
# ---Time: 1817.798


# ---Extracting and outputting i, g, j, h values and combinations---------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
# VDFM__c = pd.read_csv (path + 'VDFM__c.csv')

# ---Identifying table columns
# dim1 = output sector (g)
# dim2 = input sector (h)
# dim3 = output/input country (i/j)

# ---Lowercasing and outputting output sector (g) values
VDFM__c['dim1'] = VDFM__c['dim1'].str.lower()
VDFM__c_dim1 = VDFM__c['dim1'].unique()
VDFM__c_dim1.sort()

output_sector = VDFM__c_dim1.tolist()
with open(path + 'list_g.txt', 'w') as filehandle:
    json.dump(output_sector, filehandle)

# ---Lowercasing and outputting input sector (h) values
VDFM__c['dim2'] = VDFM__c['dim2'].str.lower()
VDFM__c_dim2 = VDFM__c['dim2'].unique()
VDFM__c_dim2.sort()

input_sector = VDFM__c_dim2.tolist()
with open(path + 'list_h.txt', 'w') as filehandle:
    json.dump(input_sector, filehandle)

# ---Uppercasing and outputting output/input country (i/j) values
VDFM__c['dim3'] = VDFM__c['dim3'].str.upper()
VDFM__c_dim3 = VDFM__c['dim3'].unique()
VDFM__c_dim3.sort()

output_input_country = VDFM__c_dim3.tolist()
with open(path + 'list_i.txt', 'w') as filehandle:
    json.dump(output_input_country, filehandle)
with open(path + 'list_j.txt', 'w') as filehandle:
    json.dump(output_input_country, filehandle)

# ---Creating all combinations of ouput country (i) / output sector (g)
ig = []
for i in VDFM__c_dim3:
    for g in VDFM__c_dim1:
        x = i + '-'+ g
        ig.append(x)
with open(path + 'list_ig.txt', 'w') as filehandle:
    json.dump(ig, filehandle)

# ---Creating all combinations of input country (j) / input sector (h)
jh = []
for j in VDFM__c_dim3:
    for h in VDFM__c_dim2:
        x = j + '-'+ h
        jh.append(x)
with open(path + 'list_jh.txt', 'w') as filehandle:
    json.dump(jh, filehandle)

print("\n Extracting and outputting i, g, j, h values", stopwatch.elapsed())
# ---Time: 0.455


# ---Reshaping VDFM to VDFM_igjh------------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
# VDFM__c = pd.read_csv (path + 'VDFM__c.csv')
#
# with open(path + 'list_ig.txt', 'r') as filehandle:
#     list_ig = json.load(filehandle)
#
# with open(path + 'list_jh.txt', 'r') as filehandle:
#     list_jh = json.load(filehandle)

# ---Lowercasing and outputting output sector (g) values
VDFM__c['dim1'] = VDFM__c['dim1'].str.lower()

# ---Lowercasing input sector (h) values
VDFM__c['dim2'] = VDFM__c['dim2'].str.lower()

# ---Uppercasing country (i/j) values
VDFM__c['dim3'] = VDFM__c['dim3'].str.upper()

# ---Reshaping VDFM__c
VDFM__c['ig'] = VDFM__c['dim3'] + "-" + VDFM__c['dim1']
VDFM__c['jh'] = VDFM__c['dim3'] + "-" + VDFM__c['dim2']

VDFM__c = VDFM__c[['ig', 'jh', 'Value']]
VDFM__c = VDFM__c.sort_values(by=['ig', 'jh'])

# ---Creating null matrix of size ig*jh
blank_VDFM_igjh = np.zeros((len(list_ig), len(list_jh)))

# ---Creating null dataframe VDFM_igjh
VDFM_igjh = pd.DataFrame(data=blank_VDFM_igjh, index=list_ig, columns=list_jh)
VDFM_igjh.apply(pd.to_numeric)

# ---Populating VDFM_igjh matrix with VDFM__c table values
for index, row in VDFM__c.iterrows():
    VDFM_igjh.loc[row['ig'], row['jh']] = row['Value']

# ---Outputting VDFM_igjh
VDFM_igjh.to_csv(path + 'VDFM_igjh.csv')

print("\n Reshaping VDFM to VDFM_igjh", stopwatch.elapsed())
# ---Time: 153.397


# ---Reshaping VXMD to VXMD_igj-------------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
VXMD = pd.read_excel (path + 'VXMD.xlsx')

# with open(path + 'list_ig.txt', 'r') as filehandle:
#     list_ig = json.load(filehandle)
#
# with open(path + 'list_j.txt', 'r') as filehandle:
#     list_j = json.load(filehandle)

# ---Identifying table columns
# dim1 = output sector (g)
# dim2 = output country (i)
# dim3 = input country (j)

# ---Lowercasing output sector values
VXMD['dim1'] = VXMD['dim1'].str.lower()

# ---Uppercasing country values
VXMD['dim2'] = VXMD['dim2'].str.upper()
VXMD['dim3'] = VXMD['dim3'].str.upper()

# ---Renaming Values in dim1 - dim2 and dim 3
VXMD['ig'] = VXMD['dim2'] + "-" + VXMD['dim1']
VXMD['j'] = VXMD['dim3']

VXMD = VXMD[['ig', 'j', 'Value']]
VXMD = VXMD.sort_values(by=['ig', 'j'])

# ---Creating null matrix of size ig*jh
blank_VXMD_igj = np.zeros((len(list_ig), len(list_j)))

# ---Creating null dataframe VXMD_igj
VXMD_igj = pd.DataFrame(data=blank_VXMD_igj, index=list_ig, columns=list_j)
VXMD_igj.apply(pd.to_numeric)

# ---Populating VXMD_igj matrix with VXMD table values
for index, row in VXMD.iterrows():
    VXMD_igj.loc[row['ig'], row['j']] = row['Value']

# ---Outputting VXMD_igj
VXMD_igj.to_csv(path + 'VXMD_igj.csv')

print("\n Reshaping VXMD to VXMD_igj", stopwatch.elapsed())
# ---Time: 182.318


# ---Reshaping VIFM to VIFM_2d-------------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
VIFM = pd.read_excel (path + 'VIFM.xlsx')

# ---Identifying table columns
# dim1 = output sector (g)
# dim2 = input sector (h)
# dim3 = input country (j)

# ---Lowercasing sector values
VIFM['dim1'] = VIFM['dim1'].str.lower()
VIFM['dim2'] = VIFM['dim2'].str.lower()

# ---Upercasing country values
VIFM['dim3'] = VIFM['dim3'].str.upper()

# ---Renaming Values in dim1 and dim3 - dim 2
VIFM['g'] = VIFM['dim1']
VIFM['jh'] = VIFM['dim3'] + "-" + VIFM['dim2']

VIFM = VIFM[['g', 'jh', 'Value']]
VIFM = VIFM.sort_values(by=['g', 'jh'])

# ---Outputting VIFM_2d
VIFM.to_csv(path + 'VIFM_2d.csv', index = False)

print("\n Reshaping VIFM to VIFM_2d", stopwatch.elapsed())
# ---Time: 16.236


# ---Reshaping VIFM_2d to VIFM_gjh----------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
# VIFM_2d = pd.read_csv (path + 'VIFM_2d.csv')
#
# with open(path + 'list_g.txt', 'r') as filehandle:
#     list_g = json.load(filehandle)
#
# with open(path + 'list_jh.txt', 'r') as filehandle:
#     list_jh = json.load(filehandle)

# ---Creating null matrix of size g*jh
blank_VIFM_gjh  = np.zeros((len(list_g), len(list_jh)))

# ---Creating null dataframe VXMD_igj
VIFM_gjh = pd.DataFrame(data=blank_VIFM_gjh, index=list_g, columns=list_jh)
VIFM_gjh.apply(pd.to_numeric)

# ---Populating VIFM_gjh matrix with VIFM_2d table values
for index, row in VIFM_2d.iterrows():
    VIFM_gjh.loc[row['g'], row['jh']] = row['Value']
VIFM_gjh = VIFM_gjh[list_jh]

# ---Outputting VIFM_gjh
VIFM_gjh.to_csv(path + 'VIFM_gjh.csv')

print("\n Reshaping VIFM_2d to VIFM_gjh", stopwatch.elapsed())
# ---Time: 82.811


# ---Reshaping VIFM_2d to VIFM_gj------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
# VIFM_2d = pd.read_csv (path + 'VIFM_2d.csv')
#
# with open(path + 'list_g.txt', 'r') as filehandle:
#     list_g = json.load(filehandle)
#
# with open(path + 'list_j.txt', 'r') as filehandle:
#     list_j = json.load(filehandle)

# ---Creating null matrix of size g*jh
blank_VIFM_gj  = np.zeros((len(list_g), len(list_j)))

# ---Creating null dataframe VXMD_igj
VIFM_gj = pd.DataFrame(data=blank_VIFM_gj, index=list_g, columns=list_j)
VIFM_gj.apply(pd.to_numeric)

gj = {}
gj_sum = {}
for g in list_g:
    print("g", g)
    for j in list_j:
        output_sector = VIFM_2d.loc[np.where(VIFM_2d['g'].str.contains(g))]
        output_sector = output_sector.reset_index(drop=True)

        a = g + j
        gj[a] = output_sector.loc[np.where(output_sector['jh'].str.contains(j))]
        gj_sum[a] = sum(gj[a]["Value"])
        VIFM_gj.loc[g, j] = gj_sum[a]

# ---Outputting VIFM_gjh
VIFM_gj.to_csv(path + 'VIFM_gj.csv')

print("\n Reshaping VIFM_2d to VIFM_gj", stopwatch.elapsed())
# ---Time: 1354.338


# ---Reshaping VFM to VFM_fjh---------------------------------------------------
# ------------------------------------------------------------------------------
stopwatch.start()

# ---Loading data
VFM = pd.read_excel (path + 'VFM.xlsx')

# with open(path + 'list_jh.txt', 'r') as filehandle:
#     list_jh = json.load(filehandle)

# ---Identifying table columns
# dim1 = factors (f)
# dim2 = input sector (h)
# dim3 = input country (j)

# ---Outputting unique factor (f) values
VFM['dim1'] = VFM['dim1'].str.upper()
VFM_dim1 = VFM['dim1'].unique()
VFM_dim1.sort()

f = VFM_dim1.tolist()
with open(path + 'list_f.txt', 'w') as filehandle:
    json.dump(f, filehandle)

# ---Lowercasing sector values
VFM['dim2'] = VFM['dim2'].str.lower()

# ---Upercasing country values
VFM['dim3'] = VFM['dim3'].str.upper()

# ---Renaming Values in dim1 and dim3 - dim 2
VFM['f'] = VFM['dim1']
VFM['jh'] = VFM['dim3'] + "-" + VFM['dim2']

VFM = VFM[['f', 'jh', 'Value']]
VFM = VFM.sort_values(by=['f', 'jh'])

# ---Creating null matrix of size f*jh
blank_VFM_fjh = np.zeros((len(f), len(list_jh)))

# ---Creating null dataframe VFM_fjh
VFM_fjh = pd.DataFrame(data=blank_VFM_fjh, index=f, columns=jh)
VFM_fjh.apply(pd.to_numeric)

# ---Populating VFM_fjh matrix with VFM table values
for index, row in VFM.iterrows():
    VFM_fjh.loc[row['f'], row['jh']] = row['Value']

# ---Outputting VFM_fjh
VFM_fjh.to_csv(path + 'VFM_fjh.csv')

print("\n Reshaping VFM to VFM_fjh", stopwatch.elapsed())
# ---Time: 18.66
