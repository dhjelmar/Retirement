#%%
import pandas as pd # Optional, for a clean table layout
import modules as my

def compare_claiming_scenarios(earnings_history, twr, death_age=95):
    scenarios = [62, 67, 70]
    comparison = []

    for age in scenarios:
        data = my.social_security(earnings_history, claim_age=age, twr=twr, death_age=death_age)
        
        # Calculate cumulative totals at specific milestones
        total_at_75 = my.social_security(earnings_history, age, twr, 75)["Lifetime Total"]
        total_at_80 = my.social_security(earnings_history, age, twr, 80)["Lifetime Total"]
        total_at_85 = my.social_security(earnings_history, age, twr, 85)["Lifetime Total"]
        total_at_90 = my.social_security(earnings_history, age, twr, 90)["Lifetime Total"]
        total_at_95 = my.social_security(earnings_history, age, twr, 95)["Lifetime Total"]
        
        comparison.append({
            "Claim Age": age,
            'TWR': twr,
            "Monthly": f"${data['Monthly Benefit']:,}",
            "Total @ 75": f"${total_at_75:,.0f}",
            "Total @ 80": f"${total_at_80:,.0f}",
            "Total @ 85": f"${total_at_85:,.0f}",
            "Total @ 90": f"${total_at_90:,.0f}",
            "Total @ 95": f"${total_at_95:,.0f}"
        })
    
    return pd.DataFrame(comparison)

# Using the previous logic:
max_history = [184500] * 35
df = compare_claiming_scenarios(max_history, 0.05)
print(df.to_string(index=False))

# %%
my.social_security(max_history, 62, 0.05, 100)
# %%
