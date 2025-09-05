#%%
import pandas as pd
import modules as my

import numpy as np
years = 12
year  = range(2023, 2023+years, 1)
age = np.array(year) - 1960
income      = years * [10000]
social_security = 0
for i,a in enumerate(age):
    if a >= 72:
        social_security = 10000
    income[i] = income[i] + social_security
savings_initial = 1E6    # starting value of savings account
ira_initial     = 0    # starting value of traditional IRA
roth_initial    = 0    # starting value of Roth IRA
spending      = 20000 # starting amount of planned spending to be increased with inflation
start         = 2025   # start year for evaluation; need to include 2 years of income before start for medicare cost
marr          = 0.0   # minimum acceptable rate of return
roi           = marr   # return on investment used to increase IRA value with time
inflation     = 0.0
heir_yob      = 2000   # heir year of birth; used to determine RMDs
heir_income   = 150000 # income of heir; used to determine RMDs
heir_factor   = 'min'  # factor to use for RMD calculation; 'min' uses IRS single life expectancy table
heir_factor   = 5      # or some #<10 to withdraw a more even amount each year to deplete by required 10 years to minimize taxes

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
    check = {'test':i, 'pass':all([pass1, pass2, pass3])}
    return check

##################################################################
# VERIFICATION TESTS

check = []
dfout = []
cols = ['income','age','rmd','federal','state','medicare','savings','roth','ira']

# test
i = 0
print('test', i)
max_taxable = 20000
df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor)
dfout.append(df)
#                                                                      state tax       medicare
#                                                                      -------------   --------
expected_savings = savings_initial + sum(income[2:12]) - 10*spending - 8*400 - 2*814 - 10*4340
expected_roth    = roth_initial
expected_ira     = ira_initial
checki = checkit(df, expected_savings, expected_roth, expected_ira)
check.append(checki)

# test
i = 1
print()
print('test', i)
max_taxable = 20000
roth_initial = 0
roi = 0.10
df = my.scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
            income, ira_initial, roth_initial, savings_initial,
            heir_yob, heir_income, heir_factor)
dfout.append(df)
# estimated but this will be a bit high because interest on savings should be decremented each year for expenses
expected_savings = savings_initial*(1+roi)**10 + \
                   sum(income[2:12]) - 10*spending - 8*400 - 2*814 - 10*4340
# above yields 2475514.460100002 vs. calculated actual of 2391055 which 84k smaller than estimate
# need to do verification in a spreadsheet then put better value below for expected
expected_savings = -100
expected_roth    = roth_initial
expected_ira     = ira_initial
checki = checkit(df, expected_savings, expected_roth, expected_ira)
check.append(checki)

# create summary table
check = pd.DataFrame(check)
check

#%%
dfout[1][cols]
#%%