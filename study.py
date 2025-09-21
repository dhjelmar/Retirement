#%%
import pandas as pd

# study
income = 100000
roi = 0.10
tax_income = 0.24
tax_cg = 0.15 # capital gains rate
nc = 10 # years to conversion
n = 20 # years to withdrawal
marr = roi # minimum acceptable rate of return

all = []

for tax_income in [0.24, 0.32, 0.34]:
    # savings / invest
    S = income * (1-tax_income)
    Fs = S * (1+roi)**n
    Ts = (Fs - S) * tax_cg
    PV_savings = (Fs - Ts) / (1+marr)**n
    print('Savings PV    =', round(PV_savings))

    # Roth
    PV_Roth = Fs / (1+marr)**n
    print('Roth PV       =', round(PV_Roth))

    # IRA
    Fi = income * (1+roi)**n
    Ti = Fi * tax_income
    PV_IRA = (Fi - Ti) / (1+marr)**n
    #PV_IRA = income * ((1+roi)**n - tax_income) / (1+marr)**n
    print('IRA PV        =', round(PV_IRA))

    # Conversion
    Fc = income * (1+roi)**nc
    Tc = Fc * tax_income
    Fr = (Fc - Tc)*(1+roi)**(n-nc)
    PV_convert = Fr / (1+marr)**n
    print('Conversion PV =', round(PV_convert))
    
    all.append({'income':income, 'roi':roi, 'tax_income':tax_income, 'tax_cg':tax_cg,
                'nc':nc, 'n':n, 'marr':marr,
                'PV_savings':round(PV_savings), 'PV_Roth':round(PV_Roth), 
                'PV_IRA':round(PV_IRA), 'PV_convert':round(PV_convert)})

df = pd.DataFrame(all)
df    

# %%
