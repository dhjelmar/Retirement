#%%
'''
This is from Gemini and is still being checked
'''

import pandas as pd
import matplotlib.pyplot as plt
import math
import modules as my

# --- 0. Settings

debug = True


# --- 2. THE LOGIC: Individual Calculations ---


if debug:
    # example from https://www.ssa.gov/oact/progdata/retirebenefit1.html
    df = pd.read_excel('input/config_test.xlsx', skiprows=1)
    #df = df[1:len(df)]   # drop 2026 year since not in SS database yet

    # NominalEarnings1 is for person born in 1964; aime = $5825
    earnings1 = df.set_index('Year')['NominalEarnings1'].to_dict()
    birth_year1 = 1964
    aime1 = my.calculate_aime(earnings1, birth_year1)
    print('aime1             =', f'${aime1:,.0f}', '; answer from website = $5825')
    print('aime1 not indexed =', f'${my.calculate_aime(earnings1, birth_year1, index=False):,.0f}')

    # NominalEarnings2 is for person born in 1959; aime = $11,463
    earnings2 = df.set_index('Year')['NominalEarnings2'].to_dict()
    birth_year2 = 1959
    aime2 = my.calculate_aime(earnings2, birth_year2)
    print('aime2             =', f'${aime2:,.0f}', '; answer from website = $11,463')
    print('aime2 not indexed =', f'${my.calculate_aime(earnings2, birth_year2, index=False):,.0f}')


#%%
def get_bend_points(birth_year):
    # National Average Wage Index (AWI) Series
    # Source: SSA.gov (AWI for 1977 is the base year for the formula)
    awi_1977 = 9779.44
    
    # 1. Determine Eligibility Year (Age 62)
    eligibility_year = birth_year + 62
    
    # 2. Determine Indexing Year (Eligibility - 2)
    indexing_year = eligibility_year - 2
    
    if indexing_year not in AWI_TABLE:
        return f"Data for indexing year {indexing_year} (Birth year {birth_year}) not available."
    
    current_awi = AWI_TABLE.get(indexing_year, 69846.57) # default 69846.57 for future
    
    # 3. Calculate Points using 1979 base figures ($180, $1085)
    ratio = current_awi / awi_1977
    
    bp1 = round(180 * ratio)
    bp2 = round(1085 * ratio)
    
    return bp1, bp2

if debug:
    print('bend points for', str(birth_year1), 'birth year used in website example =', get_bend_points(birth_year1))
    print('bend points for', str(birth_year2), 'birth year used in website example =', get_bend_points(birth_year2))


#%%
def calculate_pia(aime, birth_year, claim_year, cola=0.03):
    '''
    Primary Insurance Amount (PIA) is the base monthly benefit a worker receives 
    from Social Security if they start collecting at their Full Retirement Age (FRA)
    Calculates the Base Benefit using Bend Points based on year person turns 62.
    Adjusts pia based on claiming year.
    '''

    # 1. Get the base PIA at age 62
    b1, b2 = get_bend_points(birth_year)
    if aime <= b1:
        pia = aime * 0.9
    elif aime <= b2:
        pia = (b1 * 0.9) + ((aime - b1) * 0.32)
    else:
        pia = (b1 * 0.9) + ((b2 - b1) * 0.32) + ((aime - b2) * 0.15)

# 2. Apply COLA starting from the year the user turns 62
    # COLA for year X is usually announced in Oct and applied to Dec/Jan benefits
    cola_data = {
        2021: 5.9,
        2022: 8.7,
        2023: 3.2,
        2024: 2.5,  # 2025 per Gemini but 2024 per social security example
        2025: 2.8,  # Projected/Future
    }
    
    eligibility_year = birth_year + 62
    
    # Iterate from eligibility year up to the year before claiming
    # (Since COLA is applied to the previous year's benefit)
    current_year = eligibility_year
    while current_year < claim_year:
        breakpoint()
        cola_rate = cola_data.get(current_year, cola) / 100 # Default input "cola" for future
        print('year=',current_year,'; cola=',cola_rate)
        pia = pia * (1 + cola_rate)
        
        # SSA Rule: After each COLA increase, the new PIA is rounded to the lower dime
        pia = math.floor(pia * 10) / 10
        current_year += 1

    return math.floor(pia * 10) / 10 # SSA rounds to the dime

if debug:
    claim_year1 = 2026
    claim_year2 = 2026
    claim_age1 = claim_year1 - birth_year1
    claim_age2 = claim_year2 - birth_year2
    pia1 = calculate_pia(aime1, birth_year1, claim_year1)
    pia2 = calculate_pia(aime2, birth_year2, claim_year2)
    print('pia1 =', pia1, '; website example is $2609.8')
    print('pia2 =', pia2, '; website example is $4152.4 which is nearly identical')

#%%
# --- 3. THE ENGINE: Household Simulation ---

class HouseholdSimulator:
    def __init__(self, p1, p2, cola):
        self.p1 = p1
        self.p2 = p2
        self.p1['claim_year'] = p1['birth_year'] + p1['claim_age']
        self.p2['claim_year'] = p2['birth_year'] + p2['claim_age']
        self.cola = cola

    def run(self):
        """Simulates household benefits for two different people."""
        # Calculate AIME & PIA for each
        aime1 = calculate_aime(self.p1['earnings'], self.p1['birth_year'])
        aime2 = calculate_aime(self.p2['earnings'], self.p2['birth_year'])

        # set aime to 0 if claim age does not make sense (meaning no claim)
        if ( self.p1['claim_age'] <= 0 ) | ( self.p1['claim_age'] > 1000 ):
            aime1 = 0.
        if ( self.p2['claim_age'] <= 0 ) | ( self.p2['claim_age'] > 1000 ):
            aime2 = 0.

        pia1 = calculate_pia(aime1, self.p1['birth_year'], self.p1['claim_year'], self.cola)
        pia2 = calculate_pia(aime2, self.p2['birth_year'], self.p2['claim_year'], self.cola)
        
        # Identify high vs low earner for spousal logic
        if pia1 >= pia2:
            pia_high, pia_low = pia1, pia2
            claim_age_high, claim_age_low = self.p1['claim_age'], self.p2['claim_age']
        else:
            pia_high, pia_low = pia2, pia1
            claim_age_high, claim_age_low = self.p2['claim_age'], self.p1['claim_age']

        # Calculate checks
        check_high = pia_high * self.get_reduction(claim_age_high)
        
        # Low earner: Own Reduced + Reduced Spousal Top-up
        l_own_reduced = pia_low * self.get_reduction(claim_age_low)
        spousal_limit = pia_high * 0.50
        excess_base = max(0, spousal_limit - pia_low)
        topup = excess_base * self.get_reduction(claim_age_low, is_spousal=True)
        check_low = l_own_reduced + topup

        return {
            "Total Monthly": round(check_high + check_low, 2),
            "High Earner Check": round(check_high, 2),
            "Low Earner Check": round(check_low, 2)
        }
 
    def get_reduction(self, claim_age, fra=67, is_spousal=False):
        """Standard SSA reduction for early claiming."""
        m_early = max(0, (fra - claim_age) * 12)
        if m_early == 0: return 1.0
        if is_spousal:
            # Spousal reduction is steeper
            red = min(36, m_early) * (25/3600) + max(0, m_early - 36) * (5/1200)
        else:
            red = min(36, m_early) * (5/900) + max(0, m_early - 36) * (5/1200)
        return 1 - red


#%%
husband = {'birth_year' : birth_year1, 
           'claim_age'  : claim_age1, 
           'earnings'   : earnings1}
claim_age2_use = 3000
wife    = {'birth_year' : birth_year2, 
           'claim_age'  : claim_age2_use, 
           'earnings'   : earnings2}

cola = 0.02   # future cola                      change above to use as decimal instead of % and check usage
sim = HouseholdSimulator(husband, wife, cola)
results = sim.run()

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
aime = calculate_aime(earnings, 1965)

pia = calculate_pia(aime)

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
