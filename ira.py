#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import modules as my

#%%
def scenario(max_taxable, start, year, age, income, ira_value, ira_convert):
    '''
    max_taxable = value to keep income below
    start       = first year for evaluation
    year        = list of years for income;
                  need to include 2 years before start for medicare cost
    age         = list of ages corresponding to year list of individual to be used in evaluation for IRA RMDs
    income      = list of income corresponding to year list
    ira_value   = value of traditional IRA in start year
    rmd         = list of RMDs
    ira_convert = list of planned conversions from regular IRA to Roth
    '''
    rmd = []
    ira_convert = []
    mylist = []
    ira_remaining = ira_value
    cumcost = 0
    for i,yr in enumerate(year):
        if yr < start:
            rmd.append(0.)
            ira_convert.append(0.)
        else:
            # determine RMD based on prior EOY IRA value for current year age
            rmd.append(my.rmd(ira_remaining, age[i]))
            
            # subtract RMD from ira_remaining
            ira_remaining = ira_remaining - rmd[i]
            
            # determine how much of traditional IRA to convert to keep total income below max_taxable
            convert = max_taxable - (income[i] + rmd[i])
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

            # total taxable income in current year
            taxable = income[i] + rmd[i] + ira_convert[i]
            federal, state = my.tax(taxable)

            # medicare cost
            agi_medicare = income[i-2] + ira_convert[i-2]
            if age[i] < 65:
                med = 0
            else:
                med = my.medicare(agi_medicare)

            # total cost of federal tax, state tax, and medicare
            cost = federal + state + med
            cumcost = cumcost + cost

            # save results
            mylist.append({'year':year[i], 'age':age[i], 'income':income[i], 'rmd':rmd[i],
                            'ira_convert':ira_convert[i], 'taxable':taxable, 'ira_remaining':ira_remaining,
                            'federal':round(federal), 'state':round(state), 'tax':round(federal+state),
                            'agi medicare':agi_medicare, 'medicare':round(med),
                            'cost':round(cost), 'cumcost':round(cumcost)})
        
    df = pd.DataFrame(mylist)
    return df

#%%
# commone to all scenarios
years = 40
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
# scenario 1: convert entire IRA in start year
ira_convert = [     0,      0,    1E6,      0] + (years-4)*[0]
max_taxable = 1E9
scenario1 = scenario(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario1
# %%

#%%
# scenario 2: keep taxable income below $395k
max_taxable = 395000
scenario2 = scenario(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario2

#%%
# scenario 3: keep taxable income below $207k
max_taxable = 207000
scenario3 = scenario(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario3

#%%
# scenario 4: keep taxable income below $150k
max_taxable = 150000
scenario4 = scenario(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario4

#%%
# scenario 5: keep taxable income below $97k
max_taxable = 97000
scenario5 = scenario(max_taxable, start, year, age, income, ira_value, ira_convert)
scenario5

#%%
plt.plot(scenario1.year, scenario1.cumcost, label='convert all in 2025')
plt.plot(scenario2.year, scenario2.cumcost, label='convert to keep taxable < $395k')
plt.plot(scenario3.year, scenario3.cumcost, label='convert to keep taxable < $207k')
plt.plot(scenario4.year, scenario4.cumcost, label='convert to keep taxable < $150k')
plt.plot(scenario5.year, scenario5.cumcost, label='convert to keep taxable <  $97k')
plt.xlabel('year')
plt.ylabel('cumultive cost')
plt.title('IRA Conversion and Medicare Costs')
plt.legend() # Displays the labels for each line

# Display the plot
plt.show()
#%%