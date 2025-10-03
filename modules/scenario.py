#%%
import pandas as pd
import modules as my

#%%
def scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
             income, ira_initial, roth_initial, savings_initial,
             heir_yob, heir_income, heir_factor):
    '''
    spending    = starting planned spending to be increased with inflation
    max_taxable = value to keep income below
    roi         = return on investment used to increase ira_initial following start year
    start       = first year for evaluation
    year        = list of years for income;
                  need to include 2 years before start for medicare cost
    age         = list of ages corresponding to year list of individual to be used in evaluation for IRA RMDs
    income      = list of income corresponding to year list
    ira_initial   = value of traditional IRA in start year
    rmd         = list of RMDs
    ira_convert = list of planned conversions from regular IRA to Roth
    heir_yob   = year of birth of heir
    heir_income = income of heir
    heir_factor = factor to use for RMD calculation; 'min' uses IRS single life expectancy table
    '''
    
    # conversion to pandas series is not really necessary but provides consistency 
    # depending on how they were defined and supposed efficiency vs. lists
    year = pd.Series(year)
    age = pd.Series(age)
    income = pd.Series(income)

    marr_real = (1 + marr) / (1 + inflation) - 1  # real rate of return after inflation
    heir_age = year[0] - heir_yob
    rmd = []
    ira_convert = []
    mylist = []
    ira = ira_initial
    roth = roth_initial
    savings = savings_initial
    cumexpenses = 0
    pvcum = 0
    print_broke = True
    for i,yr in enumerate(year):
        if yr < start:
            rmd.append(0.)
            ira_convert.append(0.)
        else:

            # medicare cost based on two years prior
            agi_medicare = income[i-2] + rmd[i-2] + ira_convert[i-2]
            if age[i] < 65:
                med = 0
            else:
                med = my.medicare(agi_medicare)
                
            # total taxable income and associated taxes baesd on prior year
            taxable = income[i-1] + rmd[i-1] + ira_convert[i-1]
            federal, state, fedrate, fedrate_lcg, staterate = my.tax(yr, inflation, taxable)

            # determine RMD based on prior EOY IRA value for current year age
            rmd.append(my.rmd(ira, age[i]))
            
            # initialize how much to take out of various assets
            savings_out = 0
            roth_out = 0
            ira_out = rmd[i]

            # determine how much of traditional IRA to convert to Roth or use for expenses to keep total income below max_taxable
            ira_out_extra = max_taxable - (income[i] + rmd[i])
            if ira_out_extra < 0:
                # already above max_taxable so no withdrawal
                ira_out_extra = 0
            elif ira_out_extra > ira:
                # amount to take is more than balance so take balance
                ira_out_extra = ira
            ira_out = ira_out + ira_out_extra

            # increase account remaining values for income and growth move any IRA withdrawals to savings
            ira = max((1 + roi)*ira - ira_out, 0)
            roth = (1 + roi)*roth
            # assume large fraction of savings is cash so no roi on that fraction
            cash_fraction = 0.5
            savings = cash_fraction * savings + (1 + roi)*(1-cash_fraction)*savings + income[i] + ira_out
            
            # total expenses of federal tax, state tax, and medicare and planned spending
            spendingi = spending * (1 + inflation)**(yr-start)
            expenses = federal + state + med + spendingi
            cumexpenses = cumexpenses + expenses

            # pay expenses from savings
            savings = savings - expenses
            savings_out = savings_out + expenses

            # if no more savings, then need to take funds from Roth or IRA
            if savings > 0:
                # have sufficient savings to cover expenses so convert ira_out_extra to Roth if possible
                if ira_out_extra <= 0:
                    # nothing to convert
                    convert = 0
                elif ira_out_extra > savings:
                    # sufficient savings so convert entire amount
                    convert = ira_out_extra
                else:
                    # insufficient savings to convert entire amount
                    # could change this to keep a minimum savings amount
                    minimum_savings = 0.
                    convert = max(savings - minimum_savings, 0)
                ira_convert.append(convert)
                savings = savings - convert
                savings_out = savings_out + convert
                roth = roth + convert
                roth_out = roth_out - convert

            else:
                # insufficient savings to cover expenses so take from Roth IRA first
                ira_convert.append(0)  # if insufficient savings, then will not convert anything to Roth
                take = - savings
                savings = 0
                if roth > take:
                    roth = roth - take
                    roth_out = roth_out + take
                else:
                    # not enough left in Roth to cover expenses, so take remainder from IRA and refigure taxes
                    roth_out = roth_out + roth
                    take = take - roth
                    roth = 0
                    if ira > take:
                        ira = ira - take
                    else:
                        if print_broke == True:
                            print('## BROKE: year=',yr,' initial spending',spending,'; max taxable',max_taxable)
                            print_broke = False
                        take = ira
                        ira = 0
                    ira_out = ira_out + take

                    taxable = income[i-1] + ira_out
                    federal, state, fedrate, fedrate_lcg, staterate = my.tax(yr, inflation, taxable)               
                    cumexpenses = cumexpenses - expenses
                    expenses = federal + state + med + spending * (1 + inflation)**(yr-start)
                    cumexpenses = cumexpenses + expenses   # updated with new expenses

            # assets in year i; ira discounted for 24% taxes
            assets = savings + roth + (1-0.24)*ira
            assets_constant_dollars = assets /( 1 + inflation )**(yr-start)

            # present value of cash flow (i.e., expenses) and remaining assets
            pvcum = pvcum + expenses / ( 1 + marr_real )**(yr-start)
            PV = pvcum + assets / ( 1 + marr_real )**(yr-start)

            # pv if add 10 year withdrawal of remaining IRA after taxes
            distributions, PVestate = my.pv_estate(yr, inflation, ira, roth, savings,
                                                  heir_income, heir_age, roi, marr, heir_factor=heir_factor)
            PVestate = pvcum + PVestate / ( 1 + marr_real )**(yr-start)

            # save results
            #if yr == 2037:
            #    breakpoint()
            mylist.append({'max_taxable':max_taxable,
                           'marr':marr,
                           'roi':roi,
                           'inflation':inflation,

                           'year':year[i],
                           'age':age[i],
                           'income':income[i],
                           'rmd':round(rmd[i]),
                           'ira_convert':round(ira_convert[i]),

                           'savings_out':round(savings_out),
                           'roth_out':round(roth_out),
                           'ira_out':round(ira_out),

                           'savings':round(savings),
                           'roth':round(roth),
                           'ira':round(ira),

                           'assets':round(assets),
                           'assets_constant_dollars':round(assets_constant_dollars), 
                           'PV':round(PV),
                           'PVestate':round(PVestate),

                           'taxable':round(taxable),
                           'federal':round(federal),
                           'state':round(state),
                           'medicare':round(med),
                           'tax':round(federal+state),

                           'agi_medicare':round(agi_medicare),
                           'expenses':round(expenses),
                           'cumexpenses':round(cumexpenses),
                           'spending':round(spendingi), 

                           'fedrate':fedrate,
                           'fedrate_lcg':fedrate_lcg,
                           'staterate':staterate})

    df = pd.DataFrame(mylist)

    return df

# %%
