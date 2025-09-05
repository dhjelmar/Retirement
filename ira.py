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
spending      = 250000 # starting amount of planned spending to be increased with inflation
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
dfsum

# divisor for dollars
d2m = 1/1E6

#%%
# Cumulative taxes, medicare, and spending expenses
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.cumexpenses*d2m, label=str(i)+'. limit: '+str(round(df.max_taxable[0]*d2m,3))+'; PVestate='+str(round(df.PVestate[len(df.PVestate)-1]*d2m,3)))
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
    plt.plot(df.age, df.taxable*d2m, label=str(i)+'. limit: '+str(round(df.max_taxable[0]*d2m,3))+'; PVestate='+str(round(df.PVestate[len(df.PVestate)-1]*d2m,3)))
plt.xlabel('age')
plt.ylabel('Taxable Income')
plt.title('Taxable Income; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
# assets
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.assets*d2m, label=str(i)+'. limit: '+str(round(df.max_taxable[0]*d2m,3))+'; PVestate='+str(round(df.PVestate[len(df.PVestate)-1]*d2m,3)))
plt.xlabel('age')
plt.ylabel('Assets = Savings + Roth + discoutned IRA for 24% taxes')
plt.title('Assets; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
# PV of assets
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.PVassets*d2m, label=str(i)+'. limit: '+str(round(df.max_taxable[0]*d2m,3))+'; PVestate='+str(round(df.PVestate[len(df.PVestate)-1]*d2m,3)))
plt.xlabel('age')
plt.ylabel('PVassets = Present Value of Savings + Roth + discoutned IRA for 24% taxes')
plt.title('PVassets; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
# PV of estate
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.PVestate*d2m, label=str(i)+'. limit: '+str(round(df.max_taxable[0]*d2m,3))+'; PVestate='+str(round(df.PVestate[len(df.PVestate)-1]*d2m,3)))
#plt.ylim(100000, 600000)
plt.xlabel('age')
plt.ylabel('PV')
plt.title('PVestate; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
scenario_out[2]   # printout selected scenario #
#%%