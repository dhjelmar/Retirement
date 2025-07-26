#%%
def taxcalc(income, start, rate):
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
            return tax

def tax(income, lcg=0):
    '''
    lcg    = long term capital gains
    income = all other taxable income
    '''

    ###############################
    # federal taxes

    # income and short term capital gains
    start = [0, 24000, 97000, 207000, 395000, 501000, 752000,   1E9]
    rate  = [0,  0.12,  0.22,   0.24,   0.32,   0.35,   0.37,  0.37]
    federal_income = taxcalc(income, start, rate)

    # long term capital gains
    start = [0, 48351, 533401,   1E6]
    rate  = [0,  0.15,   0.20,  0.20]
    federal_lcg = taxcalc(lcg, start, rate)

    # total federal tax
    federal = federal_income + federal_lcg

    ###############################
    # state taxes (NY treats capital gains as income)
    start = [   0, 17151,  23601, 27901, 161551, 323201, 2155351, 5000001, 25000001,   1E9]
    rate  = [0.04, 0.045, 0.0525, 0.055,   0.06, 0.0685,  0.0965,   0.103,    0.109, 0.109]
    state = taxcalc(income+lcg, start, rate)

    return federal, state
#%%

def tax_test():
    import pandas as pd
    mylist = []
    for income in [24000, 97000, 197000, 207000, 208000, 1E6]:
        federal, state = tax(income)
        mylist.append({'income':income, 'federal':federal, 'state':state, 'total':federal+state})
    example = pd.DataFrame(mylist)
    return example

tax_test()
#%%