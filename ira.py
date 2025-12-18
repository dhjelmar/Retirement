#%% [markdown]
# Description
# ===========
# This script evaluates different scenarios for IRA withdrawals, taxes, and Medicare costs over a period of 42 years, starting from 2023. It calculates the cumulative costs of taxes and Medicare,
# taxable income, and present value (PV) of contributions based on various maximum taxable income limits. The results are visualized using matplotlib.
# The scenarios are saved to CSV files, and a summary DataFrame is created to store the results of each scenario.

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import modules as my

#%%
# import data needed for scenarios

# following works, but then need to use as config.years instead of just years
#import input.config as config
#print(f"years = {config.years}")

import_file = 'user'
if import_file == 'test':
    # test variables defined in input/config_test.py
    from input.config_test import year
    from input.config_test import age
    from input.config_test import income
    from input.config_test import savings_initial
    from input.config_test import ira_initial
    from input.config_test import roth_initial
    from input.config_test import spending
    from input.config_test import start
    from input.config_test import marr
    from input.config_test import roi
    from input.config_test import inflation
    from input.config_test import heir_factor
    from input.config_test import heir_income
    from input.config_test import heir_yob
else:
    # user can define variables in input/config.py
    from input.config import year
    from input.config import age
    from input.config import income
    from input.config import savings_initial
    from input.config import ira_initial
    from input.config import roth_initial
    from input.config import spending
    from input.config import start
    from input.config import marr
    from input.config import roi
    from input.config import inflation
    from input.config import heir_factor
    from input.config import heir_income
    from input.config import heir_yob

# %%
# run scenario with different maximum taxable income limits
scenario_out = []
summary = []
#max_taxables = [1E9, 500000, 395000, 350000, 300000, 250000, 207000, 150000, 97000]
max_taxables = [395000, 350000, 300000, 250000, 207000, 97000]
max_taxables = [300000]
os.makedirs('output', exist_ok=True)
for max_taxable in max_taxables:
    df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
                     income, ira_initial, roth_initial, savings_initial,
                     heir_yob, heir_income, heir_factor)
    df.to_csv(os.path.join('output', 'ira_out_'+str(max_taxable)+'.csv'))
    scenario_out.append(df)
    summary.append({'spending':spending, 'max_taxable':max_taxable, 'marr':marr, 'roi':roi, 'inflation':inflation, 'totalexpenses':df.expenses.sum(), 'PVestate':df.PVestate[len(df.PVestate)-1]})
dfsum = pd.DataFrame(summary)
dfsum.to_csv(os.path.join('output', 'ira_out.csv'))

# divisor for dollars
d2m = 1/1E6
dfsum

#%%
#plotout(yvar='cumexpenses')   # Taxes, Medicare, and Spending
#plotout(yvar='taxable')       # taxable income
#plotout(yvar='assets')        # savings + Roth + discoutned IRA for 24% taxes
#plotout(yvar='assets_constant_dollars') # assets adjusted to today's dollars (w/ 24% tax assumption)
#plotout(yvar='PV')            # present value of distributions + assets (w/ 24% tax assumption)
plotout(yvar='PVestate')       # present value of estate (uses heir income for tax assumption)
plotout(yvar='PVestate', xlim=(85,100), ylim=(9, 11))

#%%
i = 3
print('max_taxable     =',scenario_out[i]['max_taxable'].iloc[0])
print('inflation       =',scenario_out[i]['inflation'].iloc[0])
print('roi             =',scenario_out[i]['roi'].iloc[0])
print('marr            =',scenario_out[i]['marr'].iloc[0])
print('spending        =',scenario_out[i]['spending'].iloc[0])
print('savings_initial =',round(savings_initial))
print('roth_initial    =',round(roth_initial))
print('ira_initial     =',round(ira_initial))
cols = ['year','age','income','savings_out','roth_out','ira_out','rmd','ira_convert',
        'taxable','federal','state','medicare','savings','roth','ira','assets','PV','PVestate']
cols = ['year','age','income','rmd','ira_convert','taxable','federal','state','medicare','savings','roth','ira','assets','PV','PVestate']
cols = ['year','age','income','rmd','savings_out','roth_out','ira_out','ira_convert',
        'savings','roth','ira','assets','PV','PVestate',
        'taxable','federal','state','medicare','fedrate']
df = scenario_out[i].copy()
df[cols]
#%%