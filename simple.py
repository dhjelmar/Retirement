#%%
import pandas as pd
import modules as my
import numpy as np

# %%
# read IRA, pension, and SS PIA data

# drop any rows with missing 'Value' and only keep rows with D or E in 'Owner'
df_orig = pd.read_excel('../../retirement.xlsx', sheet_name='accounts')
df = df_orig.dropna(subset=['Value']).copy()
df = df[df.Owner.str.contains("D|E", na=False)]

# pull out pension and SS PIA
pension_d = df.Value[(df.Owner=='D')&(df.Type=='Pension')].item()
pension_e = df.Value[(df.Owner=='E')&(df.Type=='Pension')].item()
pia_d = df.Value[(df.Owner=='D')&(df.Type=='SS_PIA')].item()
pia_e = df.Value[(df.Owner=='E')&(df.Type=='SS_PIA')].item()

# drop pension and SS PIA rows
df = df[~(df.Type=='Pension')]
df = df[~(df.Type=='SS_PIA')]
accounts = df.copy()

# Modify account types for IRAs to include D or E
mask = (accounts.Owner=='D')&(accounts.Type=='IRA')
accounts.loc[mask,'Type'] = 'IRA_D'
mask = (accounts.Owner=='E')&(accounts.Type=='IRA')
accounts.loc[mask, 'Type'] = 'IRA_E'

#pd.pivot_table(df, values='Value', index='Type', columns='Owner')
#df = pd.pivot_table(df, values='Value', index=['Owner','Type'])
accounts = pd.pivot_table(accounts, values='Value', index='Type')
# flatten index
accounts = accounts.reset_index()

print('Income')
print('pension: D=',pension_d,' ; D=',pension_e)
print('SS PIA : D=',pia_d    ,' ; E=',pia_e)
print()
print('Accounts')
accounts


#%%
# # Starting DataFrame

# accounts = pd.DataFrame({
#    'Type': ['HYS', 'IRA_D', 'IRA_E', 'InherIRA', 'Invest', 'Roth'],
#    'Value': [5000, 15000, 2000, 80000, 25000, 45000]
# })

#%%
# Reshape into a 1-row DataFrame with a 'year' column
# Pivot sets 'Type' as columns and 'Value' as values
df = accounts
single_row_df = df.set_index('Type').T.reset_index(drop=True)
single_row_df.insert(0, 'Year', 2026)
single_row_df.insert(1, 'Age_D', 62)
single_row_df.insert(2, 'Age_E', 63)
single_row_df['Age_D'] = 62
single_row_df['Age_E'] = 63

print("Single-row DataFrame:")
print(single_row_df)

#%%
# Convert to a dictionary for easy multi-year manipulation
# Taking the first row as a standard Python dict
# Using the following, it maintains real as real and integer as integer
#status = single_row_df.iloc[0].to_dict()
status = single_row_df.to_dict(orient='records')[0]
print(status)

#############################################################
#%%
# scenario

def scenario(ss_start_e, ss_start_d, max_income, 
             spend, status, inflation=0.02, num_years=10):
    # Iterate across multiple years and modify account values
    history = []
    # Append starting values to history list
    history.append(status.copy())

    for i in range(num_years):

        # update year
        status['Year'] += 1
        year = status['Year']

        # ages of D + E
        status['Age_D'] = status['Age_D'] + 1
        status['Age_E'] = status['Age_E'] + 1
        
        # pension
        status['Pension_D'] = 12 * pension_d
        status['Pension_E'] = 12 * pension_e * 1.02**(year - 2026)

        def ss_mult(start_age):
            if start_age == 62:
                mult = 1 - 0.24
            elif start_age == 67:
                mult = 1.
            elif start_age == 70:
                mult = 1.30
            return mult

        # social security
        if status['Age_D'] >= ss_start_d:
            status['SS_D'] = 12 * pia_d * ss_mult(ss_start_d)
        else:
            status['SS_D'] = 0.
        if status['Age_E'] >= ss_start_e:
            status['SS_E'] = 12 * pia_e * ss_mult(ss_start_e)
        else:
            status['SS_E'] = 0.

        # RMD
        IRAout_D = my.rmd(status['IRA_D'], status['Age_D'], out='rmd')
        IRAout_E = my.rmd(status['IRA_E'], status['Age_E'], out='rmd')
        # need to fix inherIRA RMD
        IRAout_Einher = my.rmd(status['InherIRA'], status['Age_E'], out='rmd')
        status['IRA_D'] -= IRAout_D
        status['IRA_E'] -= IRAout_E
        status['InherIRA'] -= IRAout_Einher
        status['RMD'] = IRAout_D + IRAout_E + IRAout_Einher

        # income
        pension_ss_rmd = status['Pension_D'] + status['Pension_E'] + \
                         status['SS_D'] + status['SS_E'] +           \
                         status['RMD']
                
        # Additional income to hit max then convert to Roth.
        # Can not convert InherIRA so only inconsidering traditional IRA for source.
        # Convert Elsa's first beause she would need to take RMD first.
        IRAout_extra = 0.
        if pension_ss_rmd < max_income:

            need = max_income - pension_ss_rmd
            take = 0.
            if ( need > 0 )&( status['IRA_E']>0 ):
                take = min( need, status['IRA_E'])
                need = need - take
                status['IRA_E'] = status['IRA_E'] - take
                IRAout_extra = take

            take = 0.
            if ( need > 0 )&( status['IRA_D']>0 ):
                take = min( need, status['IRA_D'])
                need = need - take
                status['IRA_D'] = status['IRA_D'] - take
                IRAout_extra = IRAout_extra + take

        status['IRAout'] = status['RMD'] + IRAout_extra
        income = pension_ss_rmd + IRAout_extra
        status['Income'] = income

        # deposit into savings
        # use this to pay taxes and potentially convert Roth
        status['HYS'] = status['HYS'] + income

        # taxes
        federal, state, fedrate, fedrate_lcg, staterate = my.tax(year, inflation, income, lcg=0, printit=False)

        # subtract taxes + spending for the year
        spend = spend * (1+inflation)
        status['HYS'] = status['HYS'] - (federal + state + spend)

        # If took out extra from IRA, decide whether can convert.
        # Keep 5 years expense needs in savings if income not sufficient.
        extra = pension_ss_rmd - (federal + state + spend)
        if extra > 0:
            min_savings = 0.
        else:
            min_savings = 5 * abs(extra)
        if ( IRAout_extra>0 )&( status['HYS'] > min_savings ):
                # Convert entire amount to Roth from what was put into savings.
                # Do not worry about whose Roth because it does not matter for this purpose.
                status['Roth'] =  status['Roth'] + IRAout_extra
                status['HYS'] = status['HYS'] - IRAout_extra

        # Update year-end account
        for account, rate in growth_rates.items():
            status[account] = round(status[account] * (1 + rate), 2)

        # Append a copy of the current state to history list
        history.append(status.copy())

    # Convert back to a multi-year DataFrame and change NaN in starting year to 0
    df = pd.DataFrame(history)
    #df = df.fillna(0)
    return df

#%%
inflation = 0.
marr = 0.

# Example growth rates per account type
growth_rates = {
    'HYS': 0.0,
    'IRA_D': 0.07,
    'IRA_E': 0.07,
    'InherIRA': 0.07,
    'Invest': 0.07,
    'Roth': 0.07
}

#%%
df = scenario(ss_start_e=62, ss_start_d=70, max_income=300000., 
              spend=200000., status=status, inflation=0.02, num_years=20)
print(df)

#%%
df2 = scenario(ss_start_e=67, ss_start_d=70, max_income=300000., 
               spend=200000., status=status, inflation=0.02, num_years=10)
df3 = scenario(ss_start_e=70, ss_start_d=70, max_income=300000., 
               spend=200000., status=status, inflation=0.02, num_years=10)
#%%