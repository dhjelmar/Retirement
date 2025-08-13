#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import modules as my

#%%
# commone to all scenarios
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
ira_value = 2E6
roth_value = 2E6
spending = 300000 # starting spending value to be increased with inflation
start = 2025
marr = 0.07  # minimum acceptable rate of return
roi = marr    # return on investment used to increase IRA value with time
inflation = 0.0215
heir_yob = 1996
heir_income = 150000
heir_factor = 'min'  # factor to use for RMD calculation; 'min' uses IRS single life expectancy table
heir_factor = 5  # or maybe a bit lower would withdraw a more even amount each year over 10 years to minimize taxes

# %%
scenario_out = []
summary = []
for max_taxable in [1E9, 500000, 395000, 350000, 300000, 250000, 207000, 150000, 97000]:
    df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age, income, ira_value, heir_yob, heir_income, heir_factor)
    df.to_csv(os.path.join('output', 'ira_out_'+str(max_taxable)+'.csv'))
    scenario_out.append(df)
    summary.append({'spending':spending, 'max_taxable':max_taxable, 'marr':marr, 'roi':roi, 'inflation':inflation, 'cumcost':df.cost.sum(), 'pv':df.pv.sum()})
dfsum = pd.DataFrame(summary)
dfsum.to_csv(os.path.join('output', 'ira_out.csv'))

#%%
# Cumulative cost of taxes and medicare
for i in range(0,len(scenario_out)):
    df = scenario_out[i]
    plt.plot(df.age, df.cumcost, label=str(i)+'. limit: '+str(round(df.max_taxable[0]/1000))+'; PV='+str(round(dfsum.pv[i]/1000)))
plt.xlabel('age')
plt.ylabel('cumultive cost')
plt.title('Taxes and Medicare Costs; MARR='+str(marr)+'; ROI='+str(roi)+'; Inflation='+str(inflation))
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