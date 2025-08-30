import pandas as pd
import modules as my

def scenario(spending, max_taxable, marr, roi, inflation, start, year, age,
             income, ira_value, roth_value, savings_value,
             heir_yob, heir_income, heir_factor):
    '''
    spending    = starting planned spending to be increased with inflation
    max_taxable = value to keep income below
    roi         = return on investment used to increase ira_value following start year
    start       = first year for evaluation
    year        = list of years for income;
                  need to include 2 years before start for medicare cost
    age         = list of ages corresponding to year list of individual to be used in evaluation for IRA RMDs
    income      = list of income corresponding to year list
    ira_value   = value of traditional IRA in start year
    rmd         = list of RMDs
    ira_convert = list of planned conversions from regular IRA to Roth
    heir_yob   = year of birth of heir
    heir_income = income of heir
    heir_factor = factor to use for RMD calculation; 'min' uses IRS single life expectancy table
    '''
    year = pd.Series(year)
    age = pd.Series(age)
    income = pd.Series(income)

    marr_real = (1 + marr) / (1 + inflation) - 1  # real rate of return after inflation
    heir_age = year[0] - heir_yob
    rmd = []
    ira_convert = []
    mylist = []
    ira_remaining = ira_value
    roth_remaining = roth_value
    savings_remaining = savings_value
    cumexpenses = 0
    cumpv = 0       # present value (pv = fv / (1+r)^n)
    print_broke = True
    for i,yr in enumerate(year):
        if yr < start:
            rmd.append(0.)
            ira_convert.append(0.)
        else:
            # determine RMD based on prior EOY IRA value for current year age
            rmd.append(my.rmd(ira_remaining, age[i]))
            
            # increase IRA remaining value for growth then subtract RMD
            ira_remaining = (1+roi)*ira_remaining - rmd[i]
            
            # determine how much of traditional IRA to convert to keep total income below max_taxable
            convert = max_taxable - (income[i] + rmd[i])
            if convert > 0.:
                if ira_remaining > convert:
                    ira_convert.append(convert)
                    # subtract conversion from remaining RMD
                    ira_remaining = max(ira_remaining - convert, 0)
                else:
                    ira_convert.append(ira_remaining)
                    ira_remaining = 0.
            else:
                ira_convert.append(0.)

            # total taxable income and associated taxes
            taxable = income[i] + rmd[i] + ira_convert[i]
            federal, state, rate_federal_income, rate_federal_lcg, rate_state = my.tax(yr, inflation, taxable)

            # medicare cost
            agi_medicare = income[i-2] + rmd[i-2] + ira_convert[i-2]
            if age[i] < 65:
                med = 0
            else:
                med = my.medicare(agi_medicare)

            # total expenses of federal tax, state tax, and medicare and planned spending
            spendingi = spending * (1 + inflation)**(yr-start)
            expenses = federal + state + med + spendingi
            cumexpenses = cumexpenses + expenses

            # add extra income to savings
            income_extra = taxable - expenses
            savings_remaining = savings_remaining + income_extra
            income_extra = 0

            # if no more savings, then need to take funds from Roth or IRA
            if savings_remaining < 0:
                # insufficient savings to cover expenses so take from Roth IRA first
                take = - savings_remaining
                savings_remaining = 0
                roth_remaining = roth_remaining - take
                if roth_remaining < 0:
                    # not enough left in Roth to cover expenses, so take remainder from IRA and refigure taxes
                    take = - roth_remaining
                    roth_remaining = 0
                    ira_remaining = ira_remaining - take
                    if ira_remaining < 0:
                        if print_broke == True:
                            print('## BROKE: year=',yr,' initial spending',spending,'; max taxable',max_taxable)
                            print_broke = False
                        ira_remaining = ira_remaining + take
                        federal, state, rate_federal_income, rate_federal_lcg, rate_state = my.tax(yr, inflation, taxable + ira_remaining)
                        ira_remaining = 0
                        expenses = federal + state + med + spending * (1 + inflation)**(yr-start)
                        cumexpenses = cumexpenses + expenses
                    else:
                        federal, state, rate_federal_income, rate_federal_lcg, rate_state = my.tax(yr, inflation, taxable + take)
                        cumexpenses = cumexpenses - expenses
                        expenses = federal + state + med + spending * (1 + inflation)**(yr-start)
                        cumexpenses = cumexpenses + expenses   # updated with new expenses

            # PV contribution from year i, cumulative pv from contributions
            pvi = income_extra /( 1 + marr_real )**(yr-start)
            cumpv = cumpv + pvi

            # pv if add 10 year withdrawal of remaining IRA after taxes
            distributions, pvcalc = my.pv_estate(yr, inflation, ira_remaining, roth_remaining, savings_remaining,
                                                  heir_income, heir_age, roi, marr, heir_factor=heir_factor)
            pv = cumpv + pvcalc

            # save results
            mylist.append({'max_taxable':max_taxable, 'marr':marr, 'roi':roi, 'inflation':inflation,
                           'year':year[i], 'age':age[i], 'income':income[i], 'rmd':round(rmd[i]),
                           'ira_convert':round(ira_convert[i]), 'taxable':round(taxable), 
                           'ira_remaining':round(ira_remaining), 'roth_remaining':round(roth_remaining),
			               'savings_remaining':round(savings_remaining),
                           'federal':round(federal), 'state':round(state), 'tax':round(federal+state),
                           'agi medicare':round(agi_medicare), 'medicare':round(med),
                           'expenses':round(expenses), 'cumexpenses':round(cumexpenses), 'spending':round(spendingi), 
                           'pvi':round(pvi), 'pv':round(pv), 
                           'rate_federal_income':rate_federal_income, 'rate_federal_lcg':rate_federal_lcg, 'rate_state':rate_state})

    df = pd.DataFrame(mylist)
    return df
