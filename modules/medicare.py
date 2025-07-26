#%%
import numpy as np

def medicare(magi, paid_deductible=1676):
    '''
    input:  magi = modified adjusted gross income (2 years before current year)
            paid_deductible = total deductible payments (default = 1676 which is max)
    
    output: total medicare cost (without plan C)
    '''
    # medicare based on MAGI of 2 yeras prior so use income+lcg
    start        = [  0, 212001, 266001, 334001, 400001, 750001,   1E9]
    monthlyB     = [185,    259,    370,  480.9,  591.9,  628.9, 628.9]
    monthlyD_add = [  0,   13.7,   35.3,     57,   78.6,   85.8,  85.8]
    monthlyD     = [x + 37 for x in monthlyD_add]
    yearlyB      = [x * 12 for x in monthlyB]
    yearlyD      = np.array(monthlyD) * 12   # could also convert back to list with yearlyD.tolist()
    medicare = 0
    for i,value in enumerate(start):
        if magi < value:
            medicare = yearlyB[i-1] + yearlyD[i-1]
            return medicare + paid_deductible
#%%

def medicare_test():
    import pandas as pd
    example = []
    for magi in [212000, 212001, 334000, 334001, 750000, 750001, 1E6]:
        example.append({'magi':magi, 'medicare':medicare(magi)})
    example = pd.DataFrame(example)
    return example
medicare_test()
#%%