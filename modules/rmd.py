#%%
import pandas as pd
import os

uniform_life_table = pd.read_csv(os.path.join('input', 'rmd_uniform_life.csv'))
uniform_life_table.columns = uniform_life_table.columns.str.strip()   # remove leading and trailing spaces

single_life_table = pd.read_csv(os.path.join('input', 'rmd_single_life_expectancy.csv'))
single_life_table.columns = single_life_table.columns.str.strip()   # remove leading and trailing spaces

def rmd(value, age, out='rmd', option=1):
    # option = 1 = individual's own IRA (default)
    #        = 2 = inherited IRA by an eligible dependent
    #        = 3+ not programmed
    if option == 1:
        # this is the individual's IRA
        if age < 75:
            factor = 1E9
            rmd = 0
        else:
            df = uniform_life_table
            factor = df.loc[df.age==age,'factor'].iloc[0]

    elif option == 2:
        # This is an inherited IRA by an eligible dependent for RMDs started prior to xxxxx.
        # Distributions spread over single life expectancy of dependent based on age
        # of dependent in calendar year following year of death.
        df = single_life_table
        factor = df.loc[df.age==age,'factor'].iloc[0]
        
    else:
        # not programmed
        return 'Error: Selected option not programmed'

    if out == 'factor':
        return factor
    else:
        rmd = round(value / factor, 2)
        return rmd
    
    
#%%
def rmd_test():

    rmd_uniform_life_table = pd.read_csv(os.path.join('input', 'rmd_uniform_life_verification.csv'))
    rmd_uniform_life_table.columns = rmd_uniform_life_table.columns.str.strip()   # remove leading and trailing spaces

    test = []
    value = 1E6

    answer = rmd(value, 69, out='rmd')
    test.append({'test':1, 'answer':answer, 'correct=0':round(answer - 0, 2)})

    answer = rmd(value, 73, out='factor')
    test.append({'test':2, 'answer':answer, 'correct=0':round(answer - 26.5, 2)})

    answer = rmd(value, 76, out='factor')
    test.append({'test':3, 'answer':answer, 'correct=0':round(answer - 23.7, 2)})

    answer = rmd(value, 76, out='rmd')
    test.append({'test':4, 'answer':answer, 'correct=0':round(answer - value / 23.7, 2)})

    df = pd.DataFrame(test)

    return df

#rmd_test()
#%%
