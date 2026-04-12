#%%
import math
import pandas as pd
import matplotlib.pyplot as plt

def social_security(earnings_history, claim_age, roi=0.05, inflation=0.03, cola=0.026, fra=67, death_age=95):
    """
    Returns a pandas DataFrame tracking benefits over time.
    
    Input:
        earning_history: List of highest 35 years of earning history 
                         (can be average input 35 times)
        claim_age:       Age that social security benefits are frist taken
        roi:             Annual investment return (nominal)
        inflation:       Annual inflation rate (for discounting to Today's Dollars)
        cola:            Annual SSA Cost of Living Adjustment
        fra:             Full retirement age
        death_age:       Ending age for simulation

    Notes:
        age: The current year in the projection.

        check_constdol:  The buying power of the check. If cola is lower than inflation, 
                         you will see this number slowly decrease over time.

        check_actual:    The "sticker price" of the check you receive. This will increase 
                         every year as long as cola > 0.

        cumulative_sum:  Your total "Social Security Wealth" if you took every check and 
                         put it into an account earning your specified ROI. This is the 
                         best metric for comparing whether it is mathematically better to
                         claim early or late.

    """
    
    # 1. Calculate AIME & Base PIA
    top_35_years = sorted(earnings_history, reverse=True)[:35]
    aime = sum(top_35_years) / 420
    b1, b2 = 1286, 7749
    
    if aime <= b1:
        pia = aime * 0.9
    elif aime <= b2:
        pia = (b1 * 0.9) + ((aime - b1) * 0.32)
    else:
        pia = (b1 * 0.9) + ((b2 - b1) * 0.32) + ((aime - b2) * 0.15)
        
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

    return timeline

# --- Example Usage ---
# Max taxable earnings for 35 years
max_history = [184500] * 35 
df = social_security(max_history, claim_age=62, roi=0.07, inflation=0.03, cola=0.026)

# Display first few years
print(df.head(10))

#%%
for roi in [0., 0.05, 0.07]:
    out = []
    fig, ax = plt.subplots()
    for claim_age in [62,65,67,70,72]:
        df = social_security(max_history, 
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
