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
        pass1 = abs(actual_savings/expected_savings-1)<0.01
    if expected_roth < 0.01:
        pass2 = abs(actual_roth - expected_roth) < 0.01
    else:
        pass2 = abs(actual_roth/expected_roth-1)<0.01
    if expected_ira < 0.01:
        pass3 = abs(actual_ira - expected_ira) < 0.01
    else:
        pass3 = abs(actual_ira/expected_ira-1)<0.01
    check = all([pass1, pass2, pass3])
    print('pass?:', check)
    return check

##################################################################
#%% [markdown]
# VERIFICATION TESTS
check = []
dfout = []
cols = ['year','age','income','rmd','ira_convert','taxable','federal','state','medicare','savings','roth','ira','assets','PV','PVestate']
cols = ['year','age','income','savings_out','roth_out','ira_out','taxable','federal','state','medicare','savings','roth','ira','assets','PV','PVestate']

#%%
# test
i = 0
print('test', i)
years = 12
year  = range(2023, 2023+years, 1)
age = np.array(year) - 1960
income      = years * [10000]
social_security = 0
savings_initial = 1E6    # starting value of savings account
ira_initial     = 0    # starting value of traditional IRA
roth_initial    = 0    # starting value of Roth IRA
spending      = 1E5 # starting amount of planned spending to be increased with inflation
start         = 2025   # start year for evaluation; need to include 2 years of income before start for medicare cost
marr          = 0.0   # minimum acceptable rate of return
roi           = marr   # return on investment used to increase IRA value with time
inflation     = 0.0
heir_yob      = 2000   # heir year of birth; used to determine RMDs
heir_income   = 150000 # income of heir; used to determine RMDs
heir_factor   = 'min'  # factor to use for RMD calculation; 'min' uses IRS single life expectancy table
heir_factor   = 5      # or some #<10 to withdraw a more even amount each year to deplete by required 10 years to minimize taxes
max_taxable = 20000
df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor)
dfout.append(df)
#                                                                       state tax   medicare
#                                                                       ---------   ----
expected_savings = savings_initial + sum(income[2:12]) - 10*(spending + 400       + 4340)
expected_roth    = roth_initial 
expected_ira     = ira_initial
checki = checkit(df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki})
df[cols]

#%%
# test
i = 1
print()
print('test', i)
savings_initial = 0.5E6
roth_initial    = 0.5E6
df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor)
dfout.append(df)
savings = savings_initial*(1+roi)**10 + sum(income[2:12]) - 10*(spending + 400       + 4340)
expected_savings = max(0, savings) 
# above yields 2475514.460100002 vs. calculated actual of 2391055 which 84k smaller than estimate
# need to do verification in a spreadsheet then put better value below for expected
#expected_savings = -100
if savings > 0:
    expected_roth = roth_initial
else:
    expected_roth = roth_initial + savings
expected_ira     = ira_initial
checki = checkit(df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki})
df[cols]

#%%
# test
i = 2
print()
print('test', i)
print('max_taxable =', max_taxable)
savings_initial = 0.5E6
roth_initial    = 0.0
ira_initial     = 0.5E6
df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor)
dfout.append(df)
# expected based on inspecting results from df[cols]
expected_savings = 0
expected_roth = 0
expected_ira = 48872
checki = checkit(df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki})
df[cols]

#%%
# test
i = 3
print()
print('test', i)
print('max_taxable =', max_taxable)
savings_initial = 0.5E6
roth_initial    = 0.0
ira_initial     = 0.5E6
roi             = 0.10
df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor)
dfout.append(df)
# expected based on inspecting results from df[cols]
expected_savings = 0
expected_roth = 0
expected_ira = 1074160
checki = checkit(df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki})
df[cols]

#%%
# test not finalized yet
i = 4
print()
print('test', i)
print('max_taxable =', max_taxable)
income      = years * [0]
spending = 0
max_taxable = 0
savings_initial = 100000 / (1-0.24)
roth_initial    = 0.0
ira_initial     = 0.0
roi             = 0.05
marr            = roi
inflation       = 0.0
df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor)
dfout.append(df)

# expected based on inspecting results from df[cols]
expected_savings = 0
expected_roth = 0
expected_ira = 1074160
checki = checkit(df, expected_savings, expected_roth, expected_ira)
check.append({'test':i, 'pass':checki})
df[cols]

#%% [markdown]
# create summary table
dfcheck = pd.DataFrame(check)
dfcheck

#%%
dfout[1][cols]
#%%