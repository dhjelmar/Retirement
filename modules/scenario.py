#%%
import pandas as pd
import matplotlib.pyplot as plt
import modules as my

#%%
class scenario():
    '''
    spending    = starting planned spending to be increased with inflation
    max_taxable = value to keep income below
    roi         = return on investment used to increase ira_initial following start year
    start       = first year for evaluation
    year        = list of years for income;
                  need to include 2 years before start for medicare cost
    age         = list of ages corresponding to year list of individual to be used in evaluation for IRA RMDs
    income      = list of income corresponding to year list
                  should include work, pension, and social security
    ira_initial   = value of traditional IRA in start year
    rmd         = list of RMDs
    ira_convert = list of planned conversions from regular IRA to Roth
    heir_yob   = year of birth of heir
    heir_income = income of heir
    heir_factor = factor to use for RMD calculation; 'min' uses IRS single life expectancy table
    '''
    
    def __init__(self, spending, max_taxable, marr, roi, inflation, start, year, age,
                 income, ira_initial, roth_initial, savings_initial,
                 heir_yob, heir_income, heir_factor, savings_rate=0.02, taxes=True, medicare=True):

        # expose input to self
        self.spending=spending
        self.max_taxable=max_taxable
        self.marr=marr
        self.roi=roi
        self.inflation=inflation
        self.start=start
        self.year=year
        self.age=age
        self.income=income
        self.ira_initial=ira_initial
        self.roth_initial=roth_initial
        self.savings_initial=savings_initial
        self.heir_yob=heir_yob
        self.heir_income=heir_income
        self.heir_factor=heir_factor
        self.savings_rate=savings_rate
        self.taxes=taxes
        self.medicare=medicare

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

        # initialize account objects
        savings = my.account(year[0], deposit=savings_initial, rate=marr_real)
        ira     = my.account(year[0], deposit=ira_initial    , rate=marr_real)
        roth    = my.account(year[0], deposit=roth_initial   , rate=marr_real)

        # initialize last year estimated tax payment
        federal_est_last = 0
        state_est_last = 0

        cumexpenses = 0
        pvcum = 0

        for i,yr in enumerate(year):
            if yr < start:
                rmd.append(0.)
                ira_convert.append(0.)
            else:

                #if age[i] > 72:
                #    breakpoint()

                # cash on hand and expenses start at 0 each year then distributed as needed
                cash = income[i]

                # medicare cost based on two years prior
                agi_medicare = income[i-2] + rmd[i-2] + ira_convert[i-2]
                if (age[i] < 65) | (medicare == False):
                    med = 0
                else:
                    med = my.medicare(agi_medicare)

                # total taxable income and associated taxes based on prior year
                taxable = income[i-1] + rmd[i-1] + ira_convert[i-1]
                if taxes:    
                    federal, state, fedrate, fedrate_lcg, staterate = my.tax(yr-1, inflation, taxable)
                else:
                    federal = state = fedrate = fedrate_lcg = staterate = 0

                # determine RMD based on prior EOY IRA value for current year age
                rmd.append(my.rmd(ira.balance, age[i]))
                cash = cash + rmd[i]
                ira.withdraw(yr, rmd[i])

                # determine how much of traditional IRA to convert to Roth or use for expenses to keep total income below max_taxable
                if cash < max_taxable:
                    # withdraw enough above RMD to reach max_taxable
                    ira_out = min(max_taxable - cash, ira.balance)
                    ira.withdraw(yr, ira_out)
                    cash = cash + ira_out
                else:
                    # withdraw nothing above RMD
                    ira_out = 0 
                
                # estimate taxes based on current year
                taxable = cash
                if taxes:
                    federal_est, state_est, fedrate_est, fedrate_lcg_est, staterate_est = my.tax(yr, inflation, taxable)
                else:
                    federal_est = state_est = fedrate_est = fedrate_lcg_est = staterate_est = 0

                # total expenses of federal tax, state tax, and medicare and planned spending
                spendingi = spending * (1 + inflation)**(yr-start)
                expenses = federal + state + med + spendingi - federal_est_last - state_est_last + federal_est + state_est
                cumexpenses = cumexpenses + expenses

                # pay taxes and put remaining into savings or Roth possible
                if cash >= expenses:
                    # sufficient cash to cover expenses
                    cash = cash - expenses

                    if (ira_out > 0):
                        # put available remaining cash up to value of ira_out into roth
                        convert = min(cash, ira_out)
                        ira_convert.append(convert)
                        roth.deposit(yr, convert)
                        
                    else:
                        ira_convert.append(0.)

                    # put remaining cash into savings
                    cash = cash - ira_out
                    savings.deposit(yr, cash)

                else:
                    # use available cash
                    expenses = expenses - cash
                    cash = 0
                    if savings.balance >= expenses:
                        # pay remaining expenses from savings
                        savings.withdraw(yr, expenses)
                    else:
                        # use any remainng savings
                        expenses = expenses - savings.balance
                        savings.withdraw(yr, savings.balance)   # sets savings to $0

                        if roth.balance >= expenses:
                            # take rest from Roth
                            roth.withdraw(yr, expenses)
                        else:
                            # use remaining Roth
                            expenses = expenses - roth.balance
                            roth.withdraw(yr, roth.balance)

                            if ira.balance >= expenses:
                                # take rest from IRA
                                ira.withdraw(yr, expenses)

                                # refigure estimated taxes
                                cumexpenses = cumexpenses - federal_est - state_est
                                taxable = taxable + expenses
                                federal_est, state_est, fedrate_est, fedrate_lcg_est, staterate_est = my.tax(yr, inflation, taxable)               
                                cumexpenses = cumexpenses + federal_est + state_est 

                            else:
                                # insufficient funds to cover expenses
                                ira.withdraw(yr, ira.balance)
                                print('## BROKE: year=',yr,' initial spending',spending,'; max taxable',max_taxable)

                # store estiamted tax payments
                federal_est_last = federal_est
                state_est_last = state_est

                # increase value of accounts
                savings.growth(yr, rate=savings_rate)
                ira.growth(yr, rate=roi)
                roth.growth(yr, rate=roi)

                # assets in year i; ira discounted for 24% taxes
                assets = savings.balance + roth.balance + (1-0.24)*ira.balance
                assets_constant_dollars = assets /( 1 + inflation )**(yr-start)

                # present value of cash flow (i.e., expenses) and remaining assets
                pvcum = pvcum + expenses / ( 1 + marr_real )**(yr-start)
                PV = pvcum + assets / ( 1 + marr_real )**(yr-start)

                # pv if add 10 year withdrawal of remaining IRA after taxes
                distributions, PVestate = my.pv_estate(yr, inflation, ira.balance, roth.balance, savings.balance,
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

                            'savings':round(savings.balance),
                            'roth':round(roth.balance),
                            'ira':round(ira.balance),

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

        # expose results to self
        self.df = pd.DataFrame(mylist)
        self.savings = savings
        self.ira = ira
        self.roth = roth

    def plot(self, yvar=['PVestate','savings','roth','ira'], xvar='age', xlim='auto', ylim='auto'):
        # dollars converted to M$
        d2m = 1/1E6
        #label=str('limit: '+str(round(self.max_taxable*d2m,3))+'; PVestate='+str(round(self.df.PVestate[len(self.df.PVestate)-1]*d2m,3)))
        #plt.plot(self.df[xvar], self.df[yvar]*d2m, label=label)
        for yvari in yvar:
            label = yvari
            plt.plot(self.df[xvar], self.df[yvari]*d2m, label=label)
        plt.xlabel(xvar)
        plt.ylabel('Million Dollars')
        if xlim != 'auto':
            plt.xlim(xlim)
        if ylim != 'auto':
            plt.ylim(ylim)
        plt.title('MARR='+str(self.marr)+'; ROI='+str(self.roi)+'; Inflation='+str(self.inflation)+'; Max Taxable='+str(self.max_taxable))
        plt.legend
        plt.legend(fontsize=8) # Displays the labels for each line
        plt.grid(True)
        plt.show()


# %%
