#%%
import pandas as pd
import modules as my
import numpy as np

def checkit(df, expected_savings, expected_roth, expected_ira):
    actual_savings = df.savings.iloc[-1]
    actual_roth    = df.roth.iloc[-1]
    actual_ira   = df.ira.iloc[-1]
    print('expected savings =', expected_savings)
    print('actual   savings =', actual_savings)
    print('expected roth    =', expected_roth)
    print('actual   roth    =', actual_roth)
    print('expected ira     =', expected_ira)
    print('actual   ira     =', actual_ira)
    if expected_savings < 0.01:
        pass1 = abs(actual_savings - expected_savings) < 0.01
    else:
        pass1 = abs(actual_savings/expected_savings-1)<0.001
    if expected_roth < 0.01:
        pass2 = abs(actual_roth - expected_roth) < 0.01
    else:
        pass2 = abs(actual_roth/expected_roth-1)<0.001
    if expected_ira < 0.01:
        pass3 = abs(actual_ira - expected_ira) < 0.01
    else:
        pass3 = abs(actual_ira/expected_ira-1)<0.001
    check = all([pass1, pass2, pass3])
    print('pass?:', check)
    return check

##################################################################
#%% [markdown]
# VERIFICATION TESTS

#%%
# setup
check = []
scenario = []
cols = ['year','age','income','rmd','ira_convert','taxable','federal','state','medicare','savings','roth','ira','assets','PV','PVestate']
cols = ['year','age','income','savings_out','roth_out','ira_out','taxable','federal','state','medicare','savings','roth','ira','assets','PV','PVestate']
cols = ['year','age','income','rmd','ira_convert','savings','roth','ira','taxable','federal','state','medicare','assets','PV','PVestate']

#%%
# test
i = 0
title = 'income, no savings/ira/roth, no marr/roi/inflation, max_taxable=0, no taxes or medicare'
print('test', i, '; title:', title)
years = 12
year  = range(2023, 2023+years, 1)
age = np.array(year) - 1960
income      = years * [10000]
social_security = 0
savings_initial = 0    # starting value of savings account
ira_initial     = 0    # starting value of traditional IRA
roth_initial    = 0    # starting value of Roth IRA
spending      = 0 # starting amount of planned spending to be increased with inflation
start         = 2025   # start year for evaluation; need to include 2 years of income before start for medicare cost
marr          = 0.0   # minimum acceptable rate of return
roi           = marr   # return on investment used to increase IRA value with time
inflation     = 0.0
heir_yob      = 2000   # heir year of birth; used to determine RMDs
heir_income   = 150000 # income of heir; used to determine RMDs
heir_factor   = 'min'  # factor to use for RMD calculation; 'min' uses IRS single life expectancy table
heir_factor   = 5      # or some #<10 to withdraw a more even amount each year to deplete by required 10 years to minimize taxes
max_taxable   = 0
taxes = False
medicare = False
#df, savings, ira, roth = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
#            income, ira_initial, roth_initial, savings_initial,
#            heir_yob, heir_income, heir_factor, savings_rate=0, taxes=taxes, medicare=medicare)
scenario.append(my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor, savings_rate=0, taxes=taxes, medicare=medicare))

#%%
#                                                                       state tax   medicare
#                                                                       ---------   ----
expected_savings = savings_initial + sum(income[2:12]) # - 10*(spending + 400       + 4340)
expected_roth    = roth_initial 
expected_ira     = ira_initial
checki = checkit(scenario[i].df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki, 'title':title})
scenario[i].df[cols]

#%%
# test
i = 1
print()
title = 'same but $500k initial savings'
print('test', i, '; title:', title)
savings_initial = 0.5E6
scenario.append(my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor, savings_rate=0, taxes=taxes, medicare=medicare))
savings = savings_initial*(1+roi)**10 + sum(income[2:12]) #- 10*(spending + 400       + 4340)
expected_savings = max(0, savings) 
if savings > 0:
    expected_roth = roth_initial
else:
    expected_roth = roth_initial + savings
expected_ira     = ira_initial
checki = checkit(scenario[i].df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki, 'title':title})
scenario[i].df[cols]

#%%
# test
i = 2
print()
title = 'same plus initial $500k roth + $1M ira'
print('test', i, '; title:', title)
savings_initial = 0.5E6
roth_initial = 0.5E6
ira_initial = 1.E6
scenario.append(my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor, savings_rate=0, taxes=taxes, medicare=medicare))
#rmd = scenario[i].df.iloc[-1].rmd    # grabs last rmd value
# hand calculate the 2 RMDs
ira_age_72 = scenario[i].df.loc[scenario[i].df.age==72,'ira'].iloc[0]
rmd_73 = ira_age_72 / 26.5
rmd_74 = (ira_age_72 - rmd_73) / 25.5
rmds = rmd_73 + rmd_74
savings = savings_initial*(1+roi)**10 + sum(income[2:12]) + rmds #- 10*(spending + 400       + 4340)
expected_savings = max(0, savings) 
expected_roth = roth_initial
expected_ira     = ira_initial - rmds
checki = checkit(scenario[i].df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki, 'title':title})
scenario[i].df[cols]

#%%
# test
i = 3
print()
title = 'same but max_taxable=$250k to exercise ira conversions adding to Roth'
print('test', i, '; title:', title)
savings_initial = 0.5E6
roth_initial = 0.5E6
ira_initial = 1.E6
max_taxable = 250000
scenario.append(my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor, savings_rate=0, taxes=taxes, medicare=medicare))
# expectation
expected_savings = savings_initial + sum(income[2:12])
expected_roth    = roth_initial + ira_initial
expected_ira     = 0
checki = checkit(scenario[i].df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki, 'title':title})
scenario[i].df[cols]

#%% [markdown]
# create summary table
dfcheck = pd.DataFrame(check)
dfcheck

#%%
# print results from test 1
scenario[0].df[cols]

#%%
# plot results
scenario[3].plot()
#%%