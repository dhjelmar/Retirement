#%%
import numpy as np

def tax(year, inflation, income, lcg=0, printit=False):
    '''
    lcg    = long term capital gains
    income = all other taxable income
    '''

    # tax table year
    tax_table_year = 2026

    ###############################
    # federal taxes

    # income and short term capital gains
    start = [0, 24000, 97000, 207000, 395000, 501000, 752000,   1E9]  # 2026 tax table
    start = np.array(start) * (1 + inflation)**(year - tax_table_year)
    rate  = [0,  0.12,  0.22,   0.24,   0.32,   0.35,   0.37,  0.37]
    federal_income, fedrate = taxcalc(income, start, rate)

    # long term capital gains
    if income + lcg <= 94050 * (1 + inflation)**(year - tax_table_year):
        fedrate_lcg = 0.0
    elif income + lcg < 583750 * (1 + inflation)**(year - tax_table_year):
        fedrate_lcg = 0.15
    else:
        fedrate_lcg = 0.20
    federal_lcg = lcg * fedrate_lcg

    # total federal tax
    federal = federal_income + federal_lcg

    ###############################
    # state taxes (NY treats capital gains as income)
    start = [   0, 17151,  23601, 27901, 161551, 323201, 2155351, 5000001, 25000001,   1E9]
    start = np.array(start) * (1 + inflation)**(year - tax_table_year)
    rate  = [0.04, 0.045, 0.0525, 0.055,   0.06, 0.0685,  0.0965,   0.103,    0.109, 0.109]
    state, staterate = taxcalc(income+lcg, start, rate)

    if printit:
        print('Year:', year)
        print(' Income:         $', round(income))
        print(' LCG:            $', round(lcg))
        print(' Federal tax:    $', round(federal), 
              '  (rate:', round(100* (federal/(income+lcg)) if income>0 else 0,2), '%)')
        print('   - income tax: $', round(federal_income), '  (marginal rate:', round(100*fedrate,2), '%)')
        print('   - LCG tax:    $', round(federal_lcg), '  (marginal rate:', round(100*fedrate_lcg,2), '% )')
        print(' State tax:      $', round(state), 
              '  (rate:', round(100* (state/(income+lcg)) if income>0 else 0,2), '%; ',
               ' marginal rate:', round(100*staterate,2), '%)')
        print('-------------------------------------')
        print(' Total tax:      $', round(federal+state))

    return federal, state, fedrate, fedrate_lcg, staterate

#%%
def taxcalc(income, start, rate):
    '''
    input:  income = income value
            start  = array of tax bin starting values
            rate   = array of tax rates starting at start values
    output: tax    = tax based on income
            rate   = marginal tax rate
    '''
    tax = 0
    remaining = income
    for i in range(0,len(start)):
        bin = start[i+1] - start[i]
        if remaining > bin:
            tax = tax + bin * rate[i]
            remaining = remaining - bin
        else:
            tax = tax + remaining * rate[i]
            remaining = 0
            return tax, rate[i]

#%%
def tax_test(year=2030, inflation=0.025):
    import pandas as pd
    mylist = []
    for income in [24000, 97000, 197000, 207000, 208000, 1E6]:
        federal, state, fedrate, fedrate_lcg, staterate = tax(year, inflation, income)
        mylist.append({'income':round(income), 
                       'federal':round(federal),
                       'state':round(state), 
                       'total':round(federal+state),
                       'fedrate':fedrate,
                       'fedrate_lcg':fedrate_lcg, 
                       'staterate':staterate})
    example = pd.DataFrame(mylist)
    return example

#tax_test()
#%%
federal, state, fedrate, fedrate_lcg, staterate = tax(2026, inflation=0.025, income=133000, lcg=0, printit=True)
#federal, state, fedrate, fedrate_lcg, staterate = tax(2026, inflation=0.025, income=0, lcg=10000, printit=True)
#federal, state, fedrate, fedrate_lcg, staterate = tax(2026, inflation=0.025, income=100000, lcg=10000, printit=True)
#%%