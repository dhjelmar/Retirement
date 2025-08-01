#%%
import pandas as pd
import os
rmd_uniform_life_table = pd.read_csv(os.path.join('input', 'rmd_uniform_life.csv'))

def rmd(value, age, out='rmd', rmd_uniform_life_table=rmd_uniform_life_table):
    if age < 73:
        factor = 1E9
        rmd = 0
    else:
        df = rmd_uniform_life_table
        df.columns = df.columns.str.strip()   # remove leading and trailing spaces
        factor = df.loc[df.age==age,'factor'].iloc[0]
    if out == 'factor':
        return factor
    else:
        rmd = round(value / factor, 2)
        return rmd

#%%
def rmd_test():
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