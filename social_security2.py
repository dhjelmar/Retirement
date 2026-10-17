#%%
'''
This is from Gemini and is still being checked
'''

import pandas as pd
import matplotlib.pyplot as plt
import math
import os

home_dir = os.path.expanduser("~")
os.chdir(os.path.join(home_dir, 'Documents', 'GitHub', 'Retirement'))
import modules as my

def find_break_even(df_early, df_delay):
    # Calculate cumulative sums for both strategies
    early_cum = df_early['Total_Net_Cash'].cumsum()
    delay_cum = df_delay['Total_Net_Cash'].cumsum()
    
    # Find the first year where Delay overtakes Early
    for i in range(len(early_cum)):
        if delay_cum.iloc[i] > early_cum.iloc[i]:
            return df_early.iloc[i]['Year'], df_early.iloc[i]['P1_Age']
    return None, None

import numpy_financial as npf
def calculate_claiming_irr(df_early, df_delay):
    # Difference in cash flow: (Delay Check - Early Check)
    # This will be negative during the waiting period and positive after
    cash_flow_diff = df_delay['Total_Net_Cash'] - df_early['Total_Net_Cash']
    
    # Calculate IRR (Annualized)
    irr = npf.irr(cash_flow_diff.tolist())
    return irr


# Example: Husband (1964) claims at 70, Wife (1968) claims at 62

df = pd.read_excel('input/config_test.xlsx')
df = pd.read_excel('input/config.xlsx')
earnings1 = df.set_index('Year')['SSEarnings1'].to_dict()
earnings2 = df.set_index('Year')['SSEarnings2'].to_dict()

p1_birth = 1965
p2_birth = 1964

sim = my.HouseholdSimulator(p1_birth=p1_birth     , p2_birth=p2_birth,
                            p1_earnings=earnings1 , p2_earnings=earnings2,
                            p1_claim_age=67       , p2_claim_age=67, 
                            p1_death=100          , p2_death=100,
                            cola_future=0.03, ss_bend_point_growth_rate=0.02)

#%%
df = sim.calculate_for_years(2026, 2066)
plt.plot(df.Age_p1, df.invested, label='Invested SS')
plt.plot(df.Age_p1, df.cumulative, label='Cumulative SS')
plt.plot(df.Age_p1, df.Net_Cash, label='Net Cash')
plt.legend()

df.head(10)

#%%
results = []
scenarios = []
for claim_age1 in [70]:
    for claim_age2 in [70, 67, 62]:
        scenarios.append({'p1_claim_age':claim_age1, 'p2_claim_age':claim_age2})
        sim = my.HouseholdSimulator(p1_birth=p1_birth       , p2_birth=p2_birth,
                                    p1_earnings=earnings1   , p2_earnings=earnings2,
                                    p1_claim_age=claim_age1 , p2_claim_age=claim_age2, 
                                    p1_death=76             , p2_death=90,
                                    cola_future=0.03, ss_bend_point_growth_rate=0.02)
        if not sim: break
        df = sim.calculate_for_years(start=2026, end=2066, roi=0.05,
                                    p1_income=0, p2_income=0, spend=0,
                                    p1_ira=0, p2_ira=0)
        print(f"Claim Ages: {claim_age1}, {claim_age2}; Invested: ${df['invested'].iloc[-1]:,.2f}")
        results.append(df)
results[0].head(5)

#%%

for i,scenario in enumerate(scenarios):
    plt.plot(results[i].Age_p1, results[i].Net_Cash,
             label='Claim Ages: ' + str(scenario['p1_claim_age']) + ', ' + str(scenario['p2_claim_age']))
plt.legend()
plt.ylabel('Actual Dollars')
plt.xlabel('Age of Person 1')
plt.title('Net Cash Each Year (Work + SS + RMDs)')

#%%
for i,scenario in enumerate(scenarios):
    plt.plot(results[i].Age_p1, results[i].cumulative, 
             label='Claim Ages: ' + str(scenario['p1_claim_age']) + ', ' + str(scenario['p2_claim_age']))
plt.legend()
plt.ylabel('Actual Dollars')
plt.xlabel('Age of Person 1')
plt.title('Cumulative')

#%%
for i,scenario in enumerate(scenarios):
    plt.plot(results[i].Age_p1, results[i].invested, 
             label='Claim Ages: ' + str(scenario['p1_claim_age']) + ', ' + str(scenario['p2_claim_age']))
plt.legend()
plt.ylabel('Actual Dollars')
plt.xlabel('Age of Person 1')
plt.title('Invested')



########################################################################################
########################################################################################
########################################################################################
########################################################################################

#%%
roi = 0.05
df = pd.DataFrame(results)

#%%

for year in df
        invested_cumsum = (invested_cumsum * (1 + roi)) + annual_cash_flow



import matplotlib.pyplot as plt

def plot_retirement_strategies(strategies_data):
    plt.figure(figsize=(12, 6))
    
    for label, df in strategies_data.items():
        # Calculate cumulative sum of net household cash
        cumulative_cash = df['Net_Household_Cash'].cumsum()
        plt.plot(df['Year'], cumulative_cash, label=label, linewidth=2)

    plt.title('Social Security Break-Even Analysis: Cumulative Household Net Cash', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Cumulative Dollars (Net of Tax)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Optional: Format Y-axis as currency
    from matplotlib.ticker import StrMethodFormatter
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}'))
    
    plt.show()

# Usage Example:
# strategies = {
#    "Early (62/62)": df_62,
#    "FRA (67/67)": df_67,
#    "High-Delay (70/62)": df_70
# }
# plot_retirement_strategies(strategies)

#%%

# Create the loop
data = [sim.calculate_for_year(y) for y in range(2026, 2026 + 40)]

# Convert to DataFrame
df = pd.DataFrame(data)

# Calculate Cumulative Wealth
df['Cumulative_Wealth'] = df['Total'].cumsum()

df


#%%
print(f"Household Monthly: ${results['Total Monthly']:,}")


##################################################################################3
##################################################################################3
##################################################################################3


#%%
def simulate_household_wealth(p1_data, p2_data, p1_death=85, p2_death=95, roi=0.05, inflation=0.03):
    """
    p1: Higher earner, p2: Lower earner
    p1_death: Age when worker passes
    p2_death: Age when spouse passes
    """

    sim = HouseholdSimulator()
    res = sim.run(p1_data, p2_data)
    
    # These are the fixed monthly amounts determined by the SSA rules
    h_check = res["High Earner Check"]
    l_check = res["Low Earner Check"]
    
    timeline = []
    invested_cumsum = 0
    start_age = min(p1_data['claim_age'], p2_data['claim_age'])
    
    for age in range(start_age, p2_death + 1):
        # 1. SURVIVOR LOGIC: This is where the 'kink' comes from
        if age <= p1_death:
            # Both are alive (assuming p1 is the first to die for this example)
            # We check if the spouse has reached their claim age yet
            current_l = l_check if age >= p2_data['claim_age'] else 0
            current_h = h_check if age >= p1_data['claim_age'] else 0
            monthly_income = current_h + current_l
        else:
            # P1 has died. P2 is the survivor. 
            # Survivor gets the HIGHER of the two checks.
            monthly_income = max(h_check, l_check)

        # 2. WEALTH GROWTH
        annual_cash_flow = monthly_income * 12
        # Previous balance grows by ROI, then we add the new year's checks
        invested_cumsum = (invested_cumsum * (1 + roi)) + annual_cash_flow
        
        # 3. INFLATION ADJUSTMENT (Today's Dollars)
        years_out = age - start_age
        buying_power = invested_cumsum / ((1 + inflation) ** years_out)
        
        timeline.append({
            'age': age,
            'monthly_income': monthly_income,
            'cum_wealth': invested_cumsum,
            'buying_power': buying_power
        })
        
    return pd.DataFrame(timeline)

#%%
# Example: Husband (1964) claims at 70, Wife (1968) claims at 62

df = pd.read_excel('input/config.xlsx')
earnings = df.set_index('Work Year')['Taxed Medicare Earnings'].to_dict()
aime = my.calculate_aime(earnings, 1965)

pia = my.calculate_base_pia(aime)

#%%
husband = {'birth_year': 1964, 
           'claim_age' : 70, 
           'earnings'  : {2020: 100000, 2024: 110000}}
wife    = {'birth_year': 1968, 
           'claim_age' : 62, 
           'earnings'  : {2020: 30000, 2024: 35000}}

sim = HouseholdSimulator()
results = sim.run(husband, wife)

print(f"Household Monthly: ${results['Total Monthly']:,}")

#%%
# Create the DataFrame
df_lifecycle = simulate_household_wealth(husband, wife, p1_death=85, p2_death=85)

# Plotting
plt.figure(figsize=(10, 5))
plt.fill_between(df_lifecycle['age'], df_lifecycle['cum_wealth'], color="skyblue", alpha=0.4)
plt.plot(df_lifecycle['age'], df_lifecycle['cum_wealth'], color="Slateblue", alpha=0.6, linewidth=2)

plt.title("Total Household Social Security Wealth (Including Survivor Phase)")
plt.xlabel("Age (Primary Worker)")
plt.ylabel("Total Wealth ($)")
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

df_lifecycle.head(10).style.format({
    'monthly_income': "${:,.2f}",
    'cum_wealth'    : "${:,.2f}",
    'buying_power'  : "${:,.2f}"
})
#%%
