# define parameters needed for scenario
import numpy as np
years = 10
year  = range(2023, 2023+years, 1)
age   = np.array(year) - 1960
#                2023,   2024,   2025]
income      = [100000, 100000, 100000] + (years-3)*[50000]
social_security = 0
for i,a in enumerate(age):
    if a == 72:
        social_security = 10000
    elif a > 72:
        social_security = 20000
    income[i] = income[i] + social_security
savings_initial = 1E5    # starting value of savings account
ira_initial     = 1E6    # starting value of traditional IRA
roth_initial    = 5E5    # starting value of Roth IRA
spending        = 1E5    # starting amount of planned spending to be increased with inflation
start           = 2025   # start year for evaluation; need to include 2 years of income before start for medicare cost
marr            = 0.07   # minimum acceptable rate of return
roi_savings     = 0.
roi             = marr   # return on investment used to increase IRA value with time
inflation       = 0.0215
heir_yob        = 1996   # heir year of birth; used to determine RMDs
heir_income     = 150000 # income of heir; used to determine RMDs
heir_factor     = 'min'  # factor to use for RMD calculation; 'min' uses IRS single life expectancy table
heir_factor     = 5      # or some #<10 to withdraw a more even amount each year to deplete by required 10 years to minimize taxes
