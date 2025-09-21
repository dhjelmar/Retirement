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
# set data common to all scenarios
years = 42
year        = range(2023, 2023+years, 1)
age = np.array(year) - 1964
#                2023,   2024,   2025,   2026]
income      = [300000, 300000, 300000, 218000] + (years-4)*[135000]
social_security = 0
for i,a in enumerate(age):
    if a == 72:
        social_security = 44000
    elif a > 72:
        social_security = 44000 + 54000
    income[i] = income[i] + social_security
savings_initial = 4E5    # starting value of savings account
ira_initial     = 3.5E6    # starting value of traditional IRA
roth_initial    = 5E5    # starting value of Roth IRA
spending      = 200000 # starting amount of planned spending to be increased with inflation
start         = 2025   # start year for evaluation; need to include 2 years of income before start for medicare cost
marr          = 0.07   # minimum acceptable rate of return
roi           = marr   # return on investment used to increase IRA value with time
inflation     = 0.0215
heir_yob      = 1996   # heir year of birth; used to determine RMDs
heir_income   = 150000 # income of heir; used to determine RMDs
heir_income   = 200000 # income of heir; used to determine RMDs
heir_factor   = 'min'  # factor to use for RMD calculation; 'min' uses IRS single life expectancy table
heir_factor   = 5      # or some #<10 to withdraw a more even amount each year to deplete by required 10 years to minimize taxes

# %%
# run scenario with different maximum taxable income limits
scenario_out = []
summary = []
#max_taxables = [1E9, 500000, 395000, 350000, 300000, 250000, 207000, 150000, 97000]
max_taxables = [395000, 350000, 300000, 250000, 97000]
os.makedirs('output', exist_ok=True)
for max_taxable in max_taxables:
    print('max_taxable=',max_taxable)
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
def plotout(yvar='PVestate', xvar='age', scenario_list=scenario_out):
    # plot function for list of max_taxable scenarios for given marr, roi, and inflation
    # dollars converted to M$
    d2m = 1/1E6
    for i in range(0,len(scenario_list)):
        df = scenario_list[i]
        label=str(i)+'. limit: '+str(round(df.max_taxable[0]*d2m,3))+'; PVestate='+str(round(df.PVestate[len(df.PVestate)-1]*d2m,3))
        plt.plot(df[xvar], df[yvar]*d2m, label=label)
    plt.xlabel(xvar)
    plt.ylabel(yvar)
    marr = scenario_out[i]['marr'][0]
    roi = scenario_out[i]['roi'][0]
    inflation = scenario_out[i]['inflation'][0]
    plt.title(yvar+': MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
    plt.legend
    plt.legend(fontsize=8) # Displays the labels for each line
    plt.show()

#plotout(yvar='cumexpenses')   # Taxes, Medicare, and Spending
#plotout(yvar='taxable')       # taxable income
#plotout(yvar='assets')        # savings + Roth + discoutned IRA for 24% taxes
#plotout(yvar='assets_constant_dollars') # assets adjusted to today's dollars (w/ 24% tax assumption)
#plotout(yvar='PV')            # present value of distributions + assets (w/ 24% tax assumption)
plotout(yvar='PVestate')       # present value of estate (uses heir income for tax assumption)

#%%
i = 0
print('max_taxable=',scenario_out[i]['max_taxable'].iloc[0])
print('inflation  =',scenario_out[i]['inflation'].iloc[0])
print('roi        =',scenario_out[i]['roi'].iloc[0])
print('marr       =',scenario_out[i]['marr'].iloc[0])
print('spending   =',scenario_out[i]['spending'].iloc[0])
cols = ['year','age','income','savings_out','roth_out','ira_out','rmd','ira_convert',
        'taxable','federal','state','medicare','savings','roth','ira','assets','PV','PVestate']
scenario_out[i][cols].round().astype(int)   # printout selected scenario #
#%%