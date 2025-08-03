#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import modules as my

#%%
def scenario(max_taxable, marr, roi, start, year, age, income, ira_value, heir_yob, heir_income):
    '''
    max_taxable = value to keep income below
    roi         = return on investment used to increase ira_value following start year
    start       = first year for evaluation
    year        = list of years for income;
                  need to include 2 years before start for medicare cost
    age         = list of ages corresponding to year list of individual to be used in evaluation for IRA RMDs
    income      = list of income corresponding to year list
    ira_value   = value of traditional IRA in start year
    rmd         = list of RMDs
    ira_convert = list of planned conversions from regular IRA to Roth
    '''
    heir_age = year[0] - heir_yob
    rmd = []
    ira_convert = []
    mylist = []
    ira_remaining = ira_value
    cumcost = 0
    cumpv = 0       # present value (pv = fv / (1+r)^n)
    for i,yr in enumerate(year):
        if yr < start:
            rmd.append(0.)
            ira_convert.append(0.)
        else:
            # determine RMD based on prior EOY IRA value for current year age
            rmd.append(my.rmd(ira_remaining, age[i]))
            
            # increase IRA remaining value for growth then subtract RMD
            ira_remaining = (1+roi)*ira_remaining - rmd[i]
            
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
            agi_medicare = income[i-2] + rmd[i-2] + ira_convert[i-2]
            if age[i] < 65:
                med = 0
            else:
                med = my.medicare(agi_medicare)

            # total cost of federal tax, state tax, and medicare
            cost = federal + state + med
            cumcost = cumcost + cost

            # spending money, PV contribution from year i, cumulative pv from contributions
            spending = taxable - cost
            pvi = spending /( 1 + marr )**(yr-start)
            cumpv = cumpv + pvi

            # pv if add 10 year withdrawal of remaining IRA after taxes
            distributions, pvcalc = my.pv_estate(ira_remaining, heir_income, heir_age, marr, factor='min')
            pv = cumpv + pvcalc

            # save results
            mylist.append({'max_taxable':max_taxable, 'marr':marr, 'roi':roi, 
                           'year':year[i], 'age':age[i], 'income':income[i], 'rmd':rmd[i],
                            'ira_convert':ira_convert[i], 'taxable':taxable, 'ira_remaining':ira_remaining,
                            'federal':round(federal), 'state':round(state), 'tax':round(federal+state),
                            'agi medicare':agi_medicare, 'medicare':round(med),
                            'cost':round(cost), 'cumcost':round(cumcost), 'spending':round(spending), 
                            'pvi':pvi, 'pv':pv})
        
    df = pd.DataFrame(mylist)
    return df

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
schwab = 900 + 149 + 64
chemung = 437
kapl = 190 + 180 + 145
trowe = 109
ira_value = (schwab + chemung + kapl + trowe) * 1000
start = 2025
marr = 0.07  # minimum acceptable rate of return
roi = marr    # return on investment used to increase IRA value with time
heir_yob = 1996
heir_income = 150000

# %%
myscenario = []
summary = []
for max_taxable in [1E9, 500000, 395000, 350000, 300000, 250000, 207000, 150000, 97000]:
    df = scenario(max_taxable, marr, roi, start, year, age, income, ira_value, heir_yob, heir_income)
    myscenario.append(df)
    summary.append({'max_taxable':max_taxable, 'marr':marr, 'roi':roi, 'cumcost':df.cost.sum(), 'pv':df.pv.sum()})
dfsum = pd.DataFrame(summary)
dfsum

#%%
# Cumulative cost of taxes and medicare
for i in range(0,len(myscenario)):
    df = myscenario[i]
    plt.plot(df.age, df.cumcost, label=str(i)+'. limit: '+str(round(df.max_taxable[0]/1000))+'; PV='+str(round(dfsum.pv[i]/1000)))
plt.xlabel('age')
plt.ylabel('cumultive cost')
plt.title('Taxes and Medicare Costs; MARR='+str(marr)+'; ROI='+str(roi))
plt.legend
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
# Taxable income (not counting Roth withdrawals)
for i in range(0,len(myscenario)):
    df = myscenario[i]
    plt.plot(df.age, df.taxable, label=str(i)+'. limit: '+str(round(df.max_taxable[0]/1000))+'; PV='+str(round(dfsum.pv[i]/1000)))
plt.ylim(100000, 600000)
plt.xlabel('age')
plt.ylabel('Taxable Income')
plt.title('Taxable Income; MARR='+str(marr)+'; ROI='+str(roi))
plt.legend(fontsize=8) # Displays the labels for each line
plt.show()

#%%
myscenario[1]   # printout selected scenario #
#%%