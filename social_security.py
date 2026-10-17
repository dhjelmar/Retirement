#%%
import math
import pandas as pd
import matplotlib.pyplot as plt
import modules as my

def calculate_spousal_benefit(spouse_pia, worker_pia, spouse_claim_age, spouse_fra=67):
    """
    Calculates the final monthly check for a spouse.
    """
    # 1. Calculate the 'Base Spousal Benefit' (50% of worker's PIA)
    base_spousal_limit = worker_pia * 0.50
    
    # 2. Determine if there is an 'Excess Spousal' amount
    # If your own PIA is already higher than half of your spouse's, you get $0 extra.
    excess_spousal_base = max(0, base_spousal_limit - spouse_pia)
    
    # 3. Apply Reduction if claiming the Spousal Benefit early
    # Spousal benefits are reduced more aggressively than regular retirement.
    # Reduction: 25/36 of 1% for first 36 months, then 5/12 of 1% after.
    if spouse_claim_age >= spouse_fra:
        reduction_factor = 1.0
    else:
        m_early = (spouse_fra - spouse_claim_age) * 12
        reduction = min(36, m_early) * (25/3600) + max(0, m_early - 36) * (5/1200)
        reduction_factor = 1 - reduction
        
    final_excess_spousal = excess_spousal_base * reduction_factor
    
    return round(final_excess_spousal, 2)

def social_security(earnings_history, claim_age, claim_month=1, roi=0.05, inflation=0.03, cola=0.026, fra=67, death_age=95):
    """
    Returns a pandas DataFrame tracking benefits over time.
    
    Input:
        earning_history: List of highest 35 years of earning history or average of highest 35 years
        claim_age:       Age that social security benefits are frist taken
        claim_month:     1 (default) = January so assume 12 checks the 1st year
                         2 = February so assume 11 checks the 1st year, etc.
        roi:             Annual investment return (nominal)
        inflation:       Annual inflation rate (for discounting to Today's Dollars)
        cola:            Annual SSA Cost of Living Adjustment
        fra:             Full retirement age
        death_age:       Ending age for simulation

    Notes:
        age:             The current year in the simulation

        check_constdol:  The buying power of the check in today's dollars. If cola is lower
                         than inflation, you will see this number slowly decrease over time.

        check_actual:    The "sticker price" of the check you receive. This will increase 
                         every year as long as cola > 0.

        cumulative_sum:  Your total "Social Security Wealth" if you took every check and 
                         put it into an account earning your specified ROI. This is the 
                         best metric for comparing whether it is mathematically better to
                         claim early or late.

    """
        
    # 1. Calculate AIME & Base PIA
    if isinstance(earnings_history, dict):
        aime = my.calculate_aime(earnings_history, birth_year)
    
    elif isinstance(earnings_history, list):
        # this is a simplification of the above that will understimate benefit
        top_35_years = sorted(earnings_history, reverse=True)[:35]
        aime = sum(top_35_years) / 420

    else:
        # also a simplification
        aime = earnings_history * 35 / 420
    
    pia = my.calculate_base_pia(aime)
        
    # 2. Age Adjustments
    if claim_age == fra:
        multiplier = 1.0
    elif claim_age < fra:
        m_early = (fra - claim_age) * 12
        reduction = min(36, m_early) * (5/900) + max(0, m_early - 36) * (5/1200)
        multiplier = 1 - reduction
    else:
        m_late = (claim_age - fra) * 12
        multiplier = 1 + (m_late * (2/300))
        
    initial_monthly = math.floor(pia * multiplier)

    # 3. Build Timeline
    timeline = []
    invested_cumsum = 0
    
    for age in range(claim_age, death_age + 1):
        years_from_now = age - claim_age
        
        # Monthly Check Actual: The nominal dollar amount with COLA applied
        check_actual = initial_monthly * ((1 + cola) ** years_from_now)
        
        # Monthly Check Today's Dollars: Buying power discounted by inflation
        check_constdol = check_actual / ((1 + inflation) ** years_from_now)
        
        # Cumulative Sum: Benefits reinvested at the assumed ROI
        # (Assuming annual compounding for the purpose of the summary)
        if invested_cumsum == 0:
            # this is the 1st year so there will likely be fewer than 12 checks
            annual_cash_flow = check_actual * (13 - claim_month)
        else:
            annual_cash_flow = check_actual * 12
        invested_cumsum = (invested_cumsum * (1 + roi)) + annual_cash_flow
        
        timeline.append({
            'claim_age' : claim_age,
            'age': age,
            'check_constdol': round(check_constdol, 2),
            'check_actual': round(check_actual, 2),
            'invested_cumsum': round(invested_cumsum, 2)
        })
        
    timeline = pd.DataFrame(timeline)

    return timeline, initial_monthly, aime, pia




#%%

# --- Setup ---
p1_birth = 1965
p2_birth = 1964
p1_earnings = {1990: 50000, 2010: 80000, 2024: 100000} # Simplified
p2_earnings = {1995: 20000, 2005: 25000} # Lower earner

# 1. Calculate PIAs for both
p1_aime = my.calculate_aime(p1_earnings, p1_birth)
p1_pia = my.calculate_base_pia(p1_aime, p1_birth) # Using your bend point logic

p2_aime = my.calculate_aime(p2_earnings, p2_birth)
p2_pia = my.calculate_base_pia(p2_aime, p2_birth)

# 2. Calculate Final Spouse Check
# Let's say the spouse claims at 62
excess_spousal = calculate_spousal_benefit(p2_pia, p1_pia, spouse_claim_age=62)

# Spouse's check = (Their reduced retirement benefit) + (Their reduced excess spousal)
# Note: You'd use your existing reduction logic for the spouse_pia part!
reduced_spouse_retirement = p2_pia * 0.70 # Simplified reduction for age 62
total_spouse_check = reduced_spouse_retirement + excess_spousal

print('person 1')
print('aime:', p1_aime)
print('pai :', p1_pia)
print()
print('person 2')
print('aime:', p2_aime)
print('pai :', p2_pia)
print(f"Reduced Benefit: ${reduced_spouse_retirement:,.2f}")
print(f"Top-up from person 1:  ${excess_spousal:,.2f}")
print(f"Total Monthly Check for person 2:   ${total_spouse_check:,.2f}")

#%%
p1_claim_age = 62
p2_claim_age = 62
p1_death = 100
p2_death = 100
cola_future = 0.03
ss_bend_point_growth_rate = 0.02
sim = my.HouseholdSimulator(p1_birth, p2_birth, p1_earnings, p2_earnings, 
                            p1_claim_age, p2_claim_age, p1_death, p2_death,
                            cola_future, ss_bend_point_growth_rate)
print('person 1')
print('aime    :', sim.aime1)
print('pia base:', sim.pia_base1)
print()
print('person 2')
print('aime    :', sim.aime2)
print('pia base:', sim.pia_base2)

print()
out = sim.calculate_for_year(1964+p2_claim_age, p1_income=0, p2_income=0, spend=0, p1_ira=0, p2_ira=0)
print(f"check_high:   ${out['Check_high']:,.2f}")
print(f"check_low :   ${out['Check_low']:,.2f}")

print()
out = sim.calculate_for_year(1965+p1_claim_age, p1_income=0, p2_income=0, spend=0, p1_ira=0, p2_ira=0)
print(f"check_high:   ${out['Check_high']:,.2f}")
print(f"check_low :   ${out['Check_low']:,.2f}")

out=[]
for year in range(2026,2041):
    out.append(sim.calculate_for_year(year, p1_income=0, p2_income=0, spend=0, p1_ira=0, p2_ira=0))
df = pd.DataFrame(out)
df

#%%
#print(f"Total Monthly Check for person 2:   ${sim.get_cola_adjusted_check():,.2f}")


#%%
# Max taxable earnings for 35 years
earnings_history = 99172.  # monthly benefit: early (5/2027)=$2905; full (4/3032)=$4188; delayed (4/2035)=$5230 
print('average of highest 35 years of earnings =', earnings_history)
df, initial_monthly, aime, pia = social_security(earnings_history, claim_age=62, roi=0.07, inflation=0.03, cola=0.026)
print('initial monthly check = ', f"${initial_monthly:,.2f}")
df.head(10).style.format({'check_constdol'  : "${:,.2f}",
                          'check_actual'    : "${:,.2f}",
                          'invested_cumsum' : "${:,.2f}",})

#%%

# --- Example Usage ---
# Max taxable earnings for 35 years
earnings_history = 100000.
print('average of highest 35 years of earnings =', earnings_history)
df, initial_monthly, aime, pia = social_security(earnings_history, claim_age=62, roi=0.07, inflation=0.03, cola=0.026)

# Display first few years
print(df.head(10))

df.style.format({'check_constdol'  : "${:,.2f}",
                 'check_actual'    : "${:,.2f}",
                 'invested_cumsum' : "${:,.2f}",})


#%%
for roi in [0., 0.025, 0.05, 0.07]:
    out = []
    fig, ax = plt.subplots()
    for claim_age in [62,65,67,70,72]:
        df, initial_monthly, aime, pia = social_security(earnings_history, 
                                    claim_age=claim_age,
                                    roi=roi, 
                                    inflation=0.03, 
                                    cola=0.026)
        df.plot('age', 'invested_cumsum', label=str(claim_age), ax=ax)
        out.append(df)
    ax.set_title("Financial Projections for "+str(round(roi*100,0))+"% ROI")
    ax.set_ylabel("USD")
    plt.show()
    out = pd.concat(out, ignore_index=True)


#%%
# print(f"{'Age':<5} | {'Actual Check':<15} | {'In Today\'s Dollars':<20}")
# print("-" * 45)
# for age, data in results.items():
#     if age % 5 == 0 or age == 62:
#         print(f"{age:<5} | ${data['Actual_Dollars']:<14,.2f} | ${data['check_constdol']:<19,.2f}")



# %%
