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
savings_value = 2E5    # starting value of savings account
ira_value     = 2E6    # starting value of traditional IRA
roth_value    = 2E6    # starting value of Roth IRA
spending      = 200000 # starting amount of planned spending to be increased with inflation
start         = 2025   # start year for evaluation; need to include 2 years of income before start for medicare cost
marr          = 0.07   # minimum acceptable rate of return
roi           = marr   # return on investment used to increase IRA value with time
inflation     = 0.0215
heir_yob      = 1996   # heir year of birth; used to determine RMDs
heir_income   = 150000 # income of heir; used to determine RMDs
heir_factor   = 'min'  # factor to use for RMD calculation; 'min' uses IRS single life expectancy table
heir_factor   = 5      # or some #<10 to withdraw a more even amount each year to deplete by required 10 years to minimize taxes

# %%
# run scenario with different maximum taxable income limits
scenario_out = []
summary = []
#max_taxables = [1E9, 500000, 395000, 350000, 300000, 250000, 207000, 150000, 97000]
max_taxables = [395000, 350000, 300000, 250000, 97000]
for max_taxable in max_taxables:
    df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
                     income, ira_value, roth_value, savings_value,
                     heir_yob, heir_income, heir_factor)
    df.to_csv(os.path.join('output', 'ira_out_'+str(max_taxable)+'.csv'))
    scenario_out.append(df)
    summary.append({'spending':spending, 'max_taxable':max_taxable, 'marr':marr, 'roi':roi, 'inflation':inflation, 'totalexpenses':df.expenses.sum(), 'pv':df.pv[len(df.pv)-1]})
dfsum = pd.DataFrame(summary)
dfsum.to_csv(os.path.join('output', 'ira_out.csv'))
dfsum

#%%
# Cumulative taxes, medicare, and spending expenses
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.cumexpenses, label=str(i)+'. limit: '+str(round(df.max_taxable[0]/1000))+'; PV='+str(round(dfsum.pv[i]/1000)))
plt.xlabel('age')
plt.ylabel('cumultive Expenses')
plt.title('Taxes, Medicare, and Spending; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
plt.legend
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
# Taxable income (not counting Roth withdrawals)
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.taxable, label=str(i)+'. limit: '+str(round(df.max_taxable[0]/1000))+'; PV='+str(round(dfsum.pv[i]/1000)))
plt.ylim(100000, 600000)
plt.xlabel('age')
plt.ylabel('Taxable Income')
plt.title('Taxable Income; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
# PV
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.pv, label=str(i)+'. limit: '+str(round(df.max_taxable[0]/1000))+'; PV='+str(round(dfsum.pv[i]/1000)))
#plt.ylim(100000, 600000)
plt.xlabel('age')
plt.ylabel('PV')
plt.title('Present Value; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
scenario_out[2]   # printout selected scenario #
#%%