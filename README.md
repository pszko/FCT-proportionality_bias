# Genetic Algorithms Measuring Bias in the Proportionality Assumption of Factor Content of Trade

## Introduction
The following scripts have been developed with the purpose of estimating the maximum potential bias in the proportionality assumption of factor content of trade.

Submitted in fulfilment of requirements for degree of Master of Science in Business Analytics at HEC Montréal.


## Requirements
- `Python 3.6+`
- Python packages can be installed via `pip install -r requirements.txt`

## Data
The following paper uses the [GTAP 9 database](https://www.gtap.agecon.purdue.edu/databases/v9/) gathered by the Global Trade Analysis Project at Purdue University.

Datasets required to run scripts:
1. _VDFM_ – Domestic input-output matrices
2. _VXMD_ – Bilateral trade flow vectors
3. _VIFM_ – Imported input-output vectors
4. _VFM_ – Factor demand matrices

## Running scripts

### 1. `data_prep.py`Prepares data for all further scripts.
* Section(s):
  * Seperating final demand from VDFM
  * Extracting and outputting i, g, j, h values and combinations
  * Reshaping VDFM to VDFM_igjh
  * Reshaping VXMD to VXMD_igj
  * Reshaping VIFM to VIFM_2d
  * Reshaping VIFM_2d to VIFM_gjh
  * Reshaping VFM to VFM_fjh
* Required dataset(s): VXMD.xlsx, VDFM.xlsx, VIFM.xlsx, VFM.xlsx
* Output dataset(s): list_i.txt, list_g.txt, list_j.txt, list_h.txt, list_ig.txt, list_jh.txt, VDFM_igjh.csv, VXMD_igj.csv, VIFM_2d.csv, VIFM_gjh.csv, VFM_fjh.csv

### 2. `prop_fct.py`
* Section(s):
  * Building proportionally imputed I/O
  * Building trade matrix
  * Calculating factor content of trade using the proportionality assumption
* Required dataset(s): VDFM_igjh.csv, VXMD_igj.csv, VIFM_2d.csv, VFM_fjh.csv
* Output dataset(s): fct_prop.csv

### 3. `random_local_maximum.py`
* Section(s):
  * Preparing imported input-output constraints
  * Preparing bilateral trade constraints
  * Calculating Min from max contraints for each igjh
  * Building random local maximum
* Required dataset(s): VDFM_igjh.csv, VXMD_igj.csv, VIFM_2d.csv, VIFM_gjh.csv, FCT_prop.csv, VFM_fjh.csv
* Output dataset(s): MC_rlo.csv, MAPE_rlo.csv

### 4. `MC_max.py`
* Section(s):
  * Simulating maximum bias in factor content of trade
    * _Runs number of Monte Carlo simulation based on MC_count (line 126)_
    * _Outputs B matrix for MMAPEs greater than 200 (lines 146-148) for later use in Genetic Algorithms_    
  * Simulating requirement estimation
* Required dataset(s): VDFM_igjh.csv, VFM_fjh.csv, VXMD_igj.csv, VIFM_gjh.csv, FCT_prop.csv
* Output dataset(s): MCs_max.csv, MAPE_max.csv, *box_(x).csv*

### 5. `GA_cross_mutate.py`
* Section(s):
  * GA with crossovers and mutations
* Required dataset(s): VDFM_igjh.csv, VFM_fjh.csv, VXMD_igj.csv, VIFM_gjh.csv, FCT_prop.csv, *box_(x).csv*
* Output dataset(s): GA_cross_mutate_scores.csv

### 6. `GA_cross_mutate.py`
* Section(s):
  * GA with only mutations
* Required dataset(s): VDFM_igjh.csv, VFM_fjh.csv, VXMD_igj.csv, VIFM_gjh.csv, FCT_prop.csv, *box_(x).csv*
* Output dataset(s): GA_cross_mutate_scores.csv
