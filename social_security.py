#%%
import math
import pandas as pd
import matplotlib.pyplot as plt

def calculate_aime(earnings_history, birth_year):
    """
    Calculates AIME by indexing historical earnings to the age-60 year.
    
    Input:
        earnings_history: Dict of {year: amount} or List of nominal annual earnings.
        birth_year:      The year the worker was born.
    """
    # 1. Define the Indexing Year (the year the worker turns 60)
    indexing_year = birth_year + 60
    
    # 2. National Average Wage Index (AWI) Table
    awi_table = {
        2026: 72700.00,
        2025: 71200.00,
        2024: 69846.57,
        2023: 66621.80,
        2022: 63795.13,
        2021: 60575.07,
        2020: 55628.60,
        2019: 54099.99,
        2018: 52145.80,
        2017: 50321.89,
        2016: 48642.15,
        2015: 48098.63,
        2014: 46481.52,
        2013: 44888.16,
        2012: 44321.67,
        2011: 42979.61,
        2010: 41673.83,
        2009: 40711.61,
        2008: 41334.97,
        2007: 40405.48,
        2006: 38651.41,
        2005: 36952.94,
        2004: 35648.55,
        2003: 34064.95,
        2002: 33252.09,
        2001: 32921.92,
        2000: 32154.82,
        1999: 30469.84,
        1998: 28861.44,
        1997: 27426.00,
        1996: 25913.90,
        1995: 24705.66,
        1994: 23753.53,
        1993: 23132.67,
        1992: 22935.42,
        1991: 21811.60,
        1990: 21027.98,
        1989: 20099.55,
        1988: 19334.04,
        1987: 18426.51,
        1986: 17321.82,
        1985: 16822.51,
        1984: 16135.07,
        1983: 15239.24,
        1982: 14531.34,
        1981: 13773.10,
        1980: 12513.46
    }    
    # Get the AWI for the indexing year (fallback to 2024 if future year missing)
    base_awi = awi_table.get(indexing_year, 69846.57)
    
    indexed_earnings = []

    # 3. Handle Dictionary or List inputs
    if isinstance(earnings_history, dict):
        for year, amount in earnings_history.items():
            if year < indexing_year:
                # Use a nearby year if the exact year isn't in our simplified table
                closest_year = min(awi_table.keys(), key=lambda x: abs(x - year))
                factor = base_awi / awi_table[closest_year]
                indexed_earnings.append(amount * factor)
            else:
                # No indexing for earnings at age 60, 61, or 62+
                indexed_earnings.append(amount)
    else:
        # Fallback: if user just provides a list, assume they are already indexed
        indexed_earnings = earnings_history

    # 4. Select top 35 years and pad with zeros if necessary
    top_35 = sorted(indexed_earnings, reverse=True)[:35]
    while len(top_35) < 35:
        top_35.append(0)
        
    # 5. Divide by 420 (number of months in 35 years)
    aime = sum(top_35) / 420
    
    return round(aime, 2)

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


def calculate_pia(aime):
    # current breakpoints in earnings
    b1, b2 = 1286, 7749   

    if aime <= b1:
        pia = aime * 0.9
    elif aime <= b2:
        pia = (b1 * 0.9) + ((aime - b1) * 0.32)
    else:
        pia = (b1 * 0.9) + ((b2 - b1) * 0.32) + ((aime - b2) * 0.15)

    return pia


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
        aime = calculate_aime(earnings_history, birth_year)
    
    elif isinstance(earnings_history, list):
        # this is a simplification of the above that will understimate benefit
        top_35_years = sorted(earnings_history, reverse=True)[:35]
        aime = sum(top_35_years) / 420

    else:
        # also a simplification
        aime = earnings_history * 35 / 420
    
    pia = calculate_pia(aime)
        
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
birth_year = 1964
worker_earnings = {1990: 50000, 2010: 80000, 2024: 100000} # Simplified
spouse_earnings = {1995: 20000, 2005: 25000} # Lower earner

# 1. Calculate PIAs for both
worker_aime = calculate_aime(worker_earnings, birth_year)
worker_pia = calculate_pia(worker_aime) # Using your bend point logic

spouse_aime = calculate_aime(spouse_earnings, birth_year)
spouse_pia = calculate_pia(spouse_aime)

# 2. Calculate Final Spouse Check
# Let's say the spouse claims at 62
excess_spousal = calculate_spousal_benefit(spouse_pia, worker_pia, spouse_claim_age=62)

# Spouse's check = (Their reduced retirement benefit) + (Their reduced excess spousal)
# Note: You'd use your existing reduction logic for the spouse_pia part!
reduced_spouse_retirement = spouse_pia * 0.70 # Simplified reduction for age 62
total_spouse_check = reduced_spouse_retirement + excess_spousal

print(f"Spouse's Own Reduced Benefit: ${reduced_spouse_retirement:,.2f}")
print(f"Spouse's Top-up from Worker:  ${excess_spousal:,.2f}")
print(f"Total Monthly Spouse Check:   ${total_spouse_check:,.2f}")




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
