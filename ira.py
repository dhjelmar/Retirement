#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import modules as my

#%%
def scenario(start, year, age, income, ira_value, rmd, ira_convert):
    '''
    start       = first year for evaluation
    year        = list of years for income;
                  need to include 2 years before evaluation starts for medicare cost
    age         = list of ages corresponding to year list of individual to be used in evaluation for IRA RMDs
    income      = list of income corresponding to year list
    ira_value   = value of traditional IRA in start year
    rmd         = list of RMDs
    ira_convert = list of planned conversions from regular IRA to Roth
    '''
    mylist = []
    cumcost = 0
    ira_remaining = ira_value
    for i,agei in enumerate(age):
        if year[i] >= start:
            # start scenario with 3rd year in income list
            taxable = income[i] + rmd[i] + ira_convert[i]
            federal, state = my.tax(taxable)
            agi_medicare = income[i-2] + ira_convert[i-2]
            if agei < 65:
                med = 0
            else:
                med = my.medicare(agi_medicare)
            cost = federal + state + med
            cumcost = cumcost + cost
            ira_remaining = ira_remaining - ira_convert[i]
            mylist.append({'year':year[i], 'age':agei, 'income':income[i], 'rmd':rmd[i],
                           'ira_convert':ira_convert[i], 'taxable':taxable, 'ira_remaining':ira_remaining,
                           'federal':round(federal), 'state':round(state), 'tax':round(federal+state),
                           'agi medicare':agi_medicare, 'medicare':round(med),
                           'cost':round(cost), 'cumcost':round(cumcost)})
        df = pd.DataFrame(mylist)
    return df

def limit_taxable(max_taxable, start, year, age, income, ira_value, ira_convert):
    '''
    max_taxable = value to keep income below
    remaining input is same as for scenario()
    '''
    ira_convert = []
    rmd = []
    ira_remaining = ira_value
    for i, inc in enumerate(income):
        if year[i] < start:
            ira_convert.append(0.)
            rmd.append(0.)
        else:
            # determine RMD
            #       not done yet; need to write rmd.py            dlh
            rmd.append(0.)
            # rmd = rmd_calc(ira_remaining, age[i])
            
            # subtract RMD from ira_remaining
            ira_remaining = ira_remaining - rmd[i]
            
            # determine how much of traditional IRA to convert
            convert = max_taxable - inc
            if convert > 0.:
                if ira_remaining > convert:
                    ira_convert.append(convert)
                    # subtract conversion from remaining RMD
                    ira_remaining = max(ira_remaining - convert, 0)
                else:
                    ira_convert.append(ira_remaining)
                    ira_remaining = 0.
            else:
                ira_convert.append(0.)
    runit = scenario(start, year, age, income, ira_value, rmd, ira_convert)
    return runit

#%%
# commone to all scenarios
years = 25
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
ira_value = 1E6
start = 2025

#%%
# scenario 1
ira_convert = [     0,      0,    1E6,      0] + (years-4)*[0]
#scenario1 = scenario(start, year, age, income, ira_value, rmd, ira_convert)
max_taxable = 1E9
scenario1 = limit_taxable(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario1
# %%

#%%
# scenario 2 to keep taxable income below $395k
max_taxable = 395000
scenario2 = limit_taxable(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario2

#%%
# scenario 3
max_taxable = 207000
scenario3 = limit_taxable(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario3

#%%
plt.plot(scenario1.year, scenario1.cumcost, label='convert all in 2025')
plt.plot(scenario2.year, scenario2.cumcost, label='convert to keep taxable < $395k')
plt.plot(scenario3.year, scenario3.cumcost, label='convert to keep taxable < $207k')
plt.xlabel('year')
plt.ylabel('cumultive cost')
plt.title('IRA Conversion and Medicare Costs')
plt.legend() # Displays the labels for each line

# Display the plot
plt.show()
#%%