#%%
import pandas as pd
class account():
    '''
    
    '''
    def __init__(self, year, deposit=0, rate=0):
        self.balance = deposit
        self.rate = rate     # interest rate
        self.warning = 'none'
        self.history = {'year':[year],
                        'balance':[self.balance],
                        'amount':[self.balance],
                        'description':['starting balance']}
        self.eoy = {'year':[year],
                    'balance':[self.balance]}
        
    def deposit(self, year, amount):
        self.balance = self.balance + amount
        self.history_update(year,amount,description='deposit')
        if self.balance < 0:
            self.warning = 'overdrawn'

    def withdraw(self, year, amount):
        self.deposit(year, -amount)
        self.history_update(year,amount,description='withdrawal')

    def growth(self, year, rate):
        self.balance = (1+rate)*self.balance
        self.history_update(year, amount=rate*self.balance, description='growth')

    def history_update(self, year, amount, description):
        # updates self.history and self.eoy
        self.history['year'].append(year)
        self.history['balance'].append(self.balance)
        self.history['amount'].append(amount)
        self.history['description'].append(description)
        # update any value in eoy with current balance
        if year in self.eoy['year']:
            # already an entry for current year so overwrite balance
            i = self.eoy['year'].index(year)
            self.eoy['balance'][i] = self.balance
        else:
            # 1st entry for year so append
            self.eoy['year'].append(year)
            self.eoy['balance'].append(self.balance)

    def history_df(self):
        df = pd.DataFrame(self.history)
        return df

#%%
#savings = account(2025, deposit=10)
#savings.withdraw(2026, 100)
#savings.balance
#%%
#savings.withdraw(2026, 5)
#savings.deposit(2027, 5)
#savings.history
#%%
#savings.history_df()
# %%
