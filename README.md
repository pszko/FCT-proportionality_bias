# Genetic Algorithms Measuring Bias in the Proportionality Assumption of Factor Content of Trade

## Introduction
The following scripts have been developed with the purpose of estimating the maximum potential bias of the proportionality assumption of factor content of trade.

Code submitted in fulfilment of requirements for degree of Master of Science in Business Analytics at HEC Montréal.


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

## Running the scripts

1. _data_prep_
required datasets: 
- VXMD.xlsx
- VDFM.xlsx
- VIFM.xlsx
- VFM.xlsx

Sections:
- Seperating final demand from VDFM
- Extracting and outputting i, g, j, h values
- Reshaping VDFM to VDFM_igjh
- Reshaping VXMD to VXMD_igj
- Reshaping VIFM to VIFM_re
- Reshaping VIFM_re to VIFM_gjh
- Reshaping VFM to VFM_fjh

Output datasets: 
- VDFM__c.csv
- VDFM_FD.csv
- VDFM_igjh.csv
- VXMD_igj.csv
- VIFM_re.csv
- VIFM_gjh.csv
- VFM_fjh.csv 

- 2_prop_b
required datasets: VDFM_igjh.csv, VXMD_igj.csv, VIFM_re.csv
section: Building proportionally imputed I/O
output dataset: tz_b.csv

- 3_trade
required datasets: VXMD_igj.csv, VIFM_re.csv
section: Building trade vector
output dataset: trade.csv

- 4_prop_fct
required datasets: VFM.csv, tz_b.csv, trade.csv
section: Calculating factor content of trade using the proportionality assumption
output dataset: fct_prop.csv

- 5_constraints
required datasets: VXMD_igj.csv, VIFM_re.csv
sections:
	Building Maximum contraints per igjh entry
	Preparing imported input-output constraints
	Preparing bilateral trade constraints
	Calculating Min from max contraints for each igjh
output datasets: VIFM_igjh_constraints.csv, VXMD_igjh_constraints.csv, max_constraints.csv

- 6_random_local_optimum
required datasets: max_constraints.csv, tz_b.csv, VDFM_igjh.csv, VFM.csv, trade.csv, VXMD_igj.csv, VIFM_gjh.csv
section: Building random local optimum
output datasets: igjh_max.csv, igjh_max_sorted.csv, rlo_B.csv, MC_rlo.csv, MAPE_rlo.csv

- 7_MC_max
required datasets: tz_b.csv, VDFM_igjh.csv, VFM.csv, trade.csv, VXMD_igj.csv, VIFM_gjh.csv
section: Simulating maximum factor content of trade
output datasets: MCs_max.csv, MAPE_max.csv, *box_(x).csv*
**Script runs Monte Carlo simulation based on MC_count**
**Script can be reused to run additional simulations - merging datasets not in scope**

- 8_MC_likely
required datasets: tz_b.csv, VDFM_igjh.csv, VFM.csv, trade.csv, VXMD_igj.csv, VIFM_gjh.csv
section: Simulating likely factor content of trade
output datasets: MCs_likely.csv, MAPE_likely.csv.csv
**Script runs Monte Carlo simulation based on MC_count**
**Script can be reused to run additional simulations - merging datasets not in scope**

- 9_MC_reqs
required datasets: MCs_max.csv, MCs_likely.csv
section: Simulating maximum factor content of trade
	**Script can either calculate required simulations for maximization framework or likely framework**

- 10_GA
required datasets: tz_b.csv, VDFM_igjh.csv, VFM.csv, trade.csv, VXMD_igj.csv, VIFM_gjh.csv
section: GA for estimating maximum factor content of trade
output dataset: GA_scores_2_1m.csv
**To load initial population (lines 131-136), box_df.to_csv from 7_MC_max (lines 122-123) needs to be uncommented**


