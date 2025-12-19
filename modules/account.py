#%%
import pandas as pd
class account():
    '''
    
    '''
    def __init__(self, name, year, deposit=0, rate=0):
        self.name = name
        self.balance = deposit
        self.rate = rate     # interest rate
        self.warning = 'none'
        self.history_dict = {'year':[year],
                        'balance':[self.balance],
                        'amount':[self.balance],
                        'description':['starting balance'],
                        'note':['']}
        self.eoy = {'year':[year],
                    'balance':[self.balance]}
        
    def deposit(self, year, amount, note=''):
        self.balance = self.balance + amount
        self.history_update(year,amount,description='deposit', note=note)
        if self.balance < 0:
            self.warning = 'overdrawn'
            self.history_update(year,amount,description='deposit', note='OVERDRAWN')

    def withdraw(self, year, amount, note=''):
        self.balance = self.balance - amount
        self.history_update(year,amount,description='withdrawal', note=note)
        if self.balance < 0:
            self.warning = 'overdrawn'
            self.history_update(year,amount,description='withdrawal', note='OVERDRAWN')

    def growth(self, year, rate, note=''):
        name = self.name
        balance = self.balance
        amount = rate * self.balance
        self.balance = self.balance + amount
        if name=='savings':
            # year 2026 balance coming into function is not right
            new_balance = self.balance
            breakpoint()
        self.history_update(year, amount=amount, description='growth', note='rate='+str(rate))

    def history_update(self, year, amount, description, note=''):
        # updates self.history and self.eoy
        self.history_dict['year'].append(year)
        self.history_dict['balance'].append(self.balance)
        self.history_dict['amount'].append(amount)
        self.history_dict['description'].append(description)
        self.history_dict['note'].append(note)
        # update any value in eoy with current balance
        if year in self.eoy['year']:
            # already an entry for current year so overwrite balance
            i = self.eoy['year'].index(year)
            self.eoy['balance'][i] = self.balance
        else:
            # 1st entry for year so append
            self.eoy['year'].append(year)
            self.eoy['balance'].append(self.balance)

    def history(self):
        df = pd.DataFrame(self.history_dict)
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
