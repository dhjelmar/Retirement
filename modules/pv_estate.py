#%%
import pandas as pd
import os
import modules as my

rmd_single_life_expectancy = pd.read_csv(os.path.join('input', 'rmd_single_life_expectancy.csv'))
rmd_single_life_expectancy.columns = rmd_single_life_expectancy.columns.str.strip()   # remove leading and trailing spaces

def pv_estate(value, heir_income, heir_age, roi, marr_real, heir_factor='min', rmd_single_life_table=rmd_single_life_expectancy):
    '''
    input: factor = 'min' (default) uses IRS single life expectacy table which removes most in last year
                  = 10 (or maybe a bit lower) would withdraw a more even amount each year over 10 years to minimize taxes
    '''
    # read factor from single life table
    df = rmd_single_life_table
    # determine total PV for 10 years of distributions to deplete value
    distributions = []
    pv = 0
    for i in range(0,10):
        if i == 0:
            if heir_factor == 'min':
                # determine initial year witdrawal based on heir age
                heir_factor = df.loc[df.age==heir_age,'factor'].iloc[0]
            rmd = []
            rmd = value / heir_factor
            value = value * (1+roi) - rmd
        elif i < 9:
            if heir_factor == 'min':
                heir_factor = heir_factor - 1
            rmd =  value / heir_factor
            value = value * (1+roi) - rmd
        else:
            # distribute any remaining assets
            rmd =  value * (1+roi)
            value = value - rmd

        # rmd after taxes based on heir_income
        federal_after_rmd, state_after_rmd = my.tax(heir_income + rmd, lcg=0)
        federal_before_rmd, state_before_rmd = my.tax(heir_income, lcg=0)
        rmd_after_tax = rmd - (federal_after_rmd-federal_before_rmd) - (state_after_rmd-state_before_rmd)

        # PV
        pvi = rmd / (1+marr_real)**i     # pv of rmd in year i
        pv = pv + pvi

        distributions.append({'heir_age':heir_age, 'heir_income':heir_income, 'roi':roi, 'marr_real':marr_real,
                              'value':round(value), 'factor':round(heir_factor), 
                              'rmd':round(rmd), 'rmd_after_tax':round(rmd_after_tax),
                              'pvi':round(pvi), 'pv':round(pv)})

    distributions = pd.DataFrame(distributions)
    return distributions, round(pv)

#%%
#distributions, pv = pv_estate(100000, 150000, 50, 0.07)
#print('pv=',pv)
#distributions
#%%
#distributions, pv = pv_estate(100000, 150000, 50, 0.07, factor=5)
#print('pv=',pv)
#distributions



# %%
