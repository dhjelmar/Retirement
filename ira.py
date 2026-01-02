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
    from input.config_test import roi_savings
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
    from input.config import roi_savings
    from input.config import roi
    from input.config import inflation
    from input.config import heir_factor
    from input.config import heir_income
    from input.config import heir_yob

# %%
# run scenario with different maximum taxable income limits
scenario = []
summary = []
#max_taxables = [1E9, 500000, 395000, 350000, 300000, 250000, 207000, 150000, 97000]
max_taxables = [395000, 350000, 323200, 300000, 250000, 207000, 97000]
# 395k is federal max for 24%; 323.2k is max for 6.85% 
#max_taxables = [300000]
os.makedirs('output', exist_ok=True)
for i,max_taxable in enumerate(max_taxables):
    scenario.append(my.scenario('scenario'+str(i), spending, max_taxable, marr, roi, roi_savings, inflation, 
                                start, year, age,
                                income, ira_initial, roth_initial, savings_initial,
                                heir_yob, heir_income, heir_factor, 
                                taxes=True, medicare=True))
    scenario[i].df.to_csv(os.path.join('output', 'ira_out_'+str(max_taxable)+'.csv'))
    summary.append({'spending':scenario[i].spending, 'max_taxable':scenario[i].max_taxable, 
                    'marr':scenario[i].marr, 'roi':scenario[i].roi, 'inflation':scenario[i].inflation, 
                    'assets':scenario[i].df.assets.iloc[-1], 'assets_cd':scenario[i].df.assets_cd.iloc[-1]})
    
dfsum = pd.DataFrame(summary)
dfsum.to_csv(os.path.join('output', 'ira_out.csv'))

# divisor for dollars
d2m = 1/1E6
dfsum

#%%
my.plotout(scenario, yvar='assets')
my.plotout(scenario, yvar='assets_cd')
my.plotout(scenario, yvar='assets_cd', xlim=[80,100], ylim=[4.5,7.5])

#%%
yvar = 'fedrate'
yvar = 'effective_rate'
my.plotout(scenario, yvar=yvar)
my.plotout(scenario, yvar=yvar, legend_below=True)
my.plotout([scenario[i] for i in [0,1,2,3]], yvar=yvar, legend_below=True)

#%% plot subset
my.plotout([scenario[i] for i in [0,2,3,4,5]], yvar='assets_cd')

#%%
for obj in scenario:
    obj.plot(yvar=['fedrate', 'fedrate_lcg', 'staterate'])

#%%
i = 0
print('max_taxable     =',scenario[i].max_taxable)
print('inflation       =',scenario[i].inflation)
print('roi             =',scenario[i].roi)
print('marr            =',scenario[i].marr)
print('spending        =',scenario[i].spending)
print('savings_initial =',round(scenario[i].savings_initial))
print('roth_initial    =',round(scenario[i].roth_initial))
print('ira_initial     =',round(scenario[i].ira_initial))
cols = ['year','age','income','ira_out','ira_convert','rmd',
        'savings','roth','ira','assets','assets_cd',
        'taxable','federal','state','medicare','fedrate']
df = scenario[i].df.copy()
df[cols]

#%%
my.printall(scenario[3].savings.history())

# %%
scenario[3].df[cols].head(10)
#%%
scenario[3].check_tax.head(10)
#%%
