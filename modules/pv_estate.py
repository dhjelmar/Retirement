#%%
import pandas as pd
import os
import modules as my

rmd_single_life_expectancy = pd.read_csv(os.path.join('input', 'rmd_single_life_expectancy.csv'))
rmd_single_life_expectancy.columns = rmd_single_life_expectancy.columns.str.strip()   # remove leading and trailing spaces


#%%
def rmd_estate(i, ira_value, heir_age, roi, heir_factor='min', rmd_single_life_table=rmd_single_life_expectancy):
    '''
    i = 0 to 9; 0 is first year after death of individual
    ira_value = value of IRA at end of prior year
    heir_age = age of heir at time of death
    roi = return on investment used to increase IRA value following death
    heir_factor = factor to use for RMD calculation; 'min' uses IRS single life expectancy table
                  5 (or maybe a bit lower) would withdraw a more even amount each year over 10 years to minimize taxes
    rmd_single_life_table = table with single life expectancy factors    
    '''

    if heir_factor == 'min':
        # determine initial year witdrawal based on heir age
        df = rmd_single_life_table
        if i == 0:
            # first year after death of individual
            factor = df.loc[df.age==heir_age,'factor'].iloc[0]
        elif i < 9:
            # subsequent years use prior year factor minus 1
            factor = df.loc[df.age==heir_age,'factor'].iloc[0] - i
    else:
        # use provided factor
        if isinstance(heir_factor, str):
            raise ValueError("heir_factor must be 'min' or a numeric value")
        if heir_factor <= 0:
            raise ValueError("heir_factor must be greater than 0")
        factor = float(heir_factor)

    if i < 9:
        # not last year, so withdraw based on factor
        rmd = ira_value / factor
        ira_remaining = ira_value * (1 + roi) - rmd
    else:
        # last year, so distribute all remaining assets
        factor = 1  # set factor to 1 to withdraw all remaining assets
        rmd = ira_value
        ira_remaining = 0
        
    # return RMD, remaining value, and factor used for next year
    if rmd < 0:
        rmd = 0  # avoid negative RMD

    return rmd, ira_remaining, factor

#%%
def rmd_estate_test():
    ira_value = 1E6
    heir_age = 50
    roi = 0.07
    print('Testing rmd_estate with value=',ira_value, 'heir_age=',heir_age, 'roi=',roi)
    test = []
    for i in range(0, 10):
        rmd, ira_remaining, factor = rmd_estate(i, ira_value, heir_age, roi)
        test.append({'test':i+1, 'rmd':rmd, 'ira_remaining':ira_remaining, 'factor':factor})
    df = pd.DataFrame(test)
    return df

#rmd_estate_test()
#%%
def pv_estate(ira_remaining, roth_remaining, savings_remaining,
              heir_income, heir_age, roi, marr_real=0.07, heir_factor='min', rmd_single_life_table=rmd_single_life_expectancy):
    '''
    input: heir_factor = 'min' (default) uses IRS single life expectacy table which removes most in last year
                       = 10 (or maybe a bit lower) would withdraw a more even amount each year over 10 years to minimize taxes
    '''

    # determine present value of Roth IRA and savings
    pv = roth_remaining + savings_remaining
    
    # determine total PV for 10 years of distributions from IRA to deplete value
    distributions = []
    for i in range(0,10):

        # rmd_estate
        rmd, ira_remaining, factor = rmd_estate(i, ira_remaining, heir_age, roi, heir_factor, rmd_single_life_table)

        # rmd after taxes based on heir_income
        federal_after_rmd, state_after_rmd = my.tax(heir_income + rmd, lcg=0)
        federal_before_rmd, state_before_rmd = my.tax(heir_income, lcg=0)
        rmd_after_tax = rmd - (federal_after_rmd-federal_before_rmd) - (state_after_rmd-state_before_rmd)

        # PV
        pvi = rmd / (1+marr_real)**i
        pv = pv + pvi

        distributions.append({'heir_age':heir_age, 'heir_income':heir_income, 'roi':roi, 'marr_real':marr_real,
                              'ira_remaining':round(ira_remaining), 'factor':round(factor), 
                              'rmd':round(rmd), 'rmd_after_tax':round(rmd_after_tax),
                              'pvi':round(pvi), 'pv':round(pv)})

    distributions = pd.DataFrame(distributions)
    return distributions, round(pv)

#%%
def pv_estate_test():
    test = []
    ira_remaining = 1E6
    heir_income = 150000
    heir_age = 50
    roi = 0.07

    # Test with heir_factor as 'min' and a factor of min
    answer, answer_pv = pv_estate(ira_remaining, 0, 0, heir_income, heir_age, roi, heir_factor='min')
    test.append({'test':0, 'answer':answer, 'correct=0':round(answer_pv - 1016395)})  # still need to check all 3 answers

    # Test with heir_factor as 'min' and a factor of 5
    answer, answer_pv = pv_estate(ira_remaining, 0, 0, heir_income, heir_age, roi, heir_factor=5)
    test.append({'test':0, 'answer':answer, 'correct=0':round(answer_pv - 1059128)})

    # Test with heir_factor as 'min' and a factor of 10
    answer, answer_pv = pv_estate(ira_remaining, 0, 0, heir_income, heir_age, roi, heir_factor=10)
    test.append({'test':0, 'answer':answer, 'correct=0':round(answer_pv - 1041054)})

    df = pd.DataFrame(test)

    return df
#pv_estate_test()

# %%
