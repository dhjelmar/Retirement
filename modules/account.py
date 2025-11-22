#%%
class account():
    '''
    
    '''
    def __init__(self, year, deposit=0, rate=0):
        self.balance = deposit
        self.rate = rate     # interest rate
        self.warning = 'none'
        #self.history = [{'year':year, 'balance':self.balance}]
        self.history = {'year':[year],
                        'balance':[self.balance]}

    def deposit(self, year, amount):
        self.balance = self.balance + amount
        #self.history.append({'year':year, 'balance':self.balance})
        if year in self.history['year']:
            # already an entry for current year so overwrite balance
            i = savings.history['year'].index(year)
            self.history['balance'][i] = self.balance
        else:
            # 1st entry for year so append
            self.history['year'].append(year)
            self.history['balance'].append(self.balance)
        if self.balance < 0:
            self.warning = 'overdrawn'

    def withdraw(self, year, amount):
        self.deposit(year, -amount)

    def growth(self, rate):
        self.balance = (1+rate)*self.balance


#%%
savings = account(2025, deposit=10)
savings.withdraw(2026, 100)
savings.balance
#savings.history[0]['year']
savings.history['year']
#%%
savings.withdraw(2026, 5)
# %%
savings.deposit(2027, 5)
savings.history
#%%
