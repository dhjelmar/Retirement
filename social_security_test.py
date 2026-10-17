#%%
import os
import pandas as pd
import modules as my

#%%
# example from https://www.ssa.gov/oact/progdata/retirebenefit1.html
home_dir = os.path.expanduser("~")
path = os.path.join(home_dir, 'Documents', 'GitHub', 'Retirement', 'input', 'config_test.xlsx')
df = pd.read_excel(path)
#df = df[1:len(df)]   # drop 2026 year since not in SS database yet
df.head()

#%%
# check aime

# NominalEarnings1 is for person born in 1964; aime = $5825
earnings1 = df.set_index('Year')['SSEarnings1'].to_dict()
birth_year1 = 1959
aime1 = my.calculate_aime(earnings1, birth_year1)
print('aime1             =', f'${aime1:,.0f}', '; answer from website = $11,463')
print('aime1 not indexed =', f'${my.calculate_aime(earnings1, birth_year1, index=False):,.0f}')

# NominalEarnings2 is for person born in 1959; aime = $11,463
earnings2 = df.set_index('Year')['SSEarnings2'].to_dict()
birth_year2 = 1964
aime2 = my.calculate_aime(earnings2, birth_year2)
print('aime2             =', f'${aime2:,.0f}', '; answer from website = $5825')
print('aime2 not indexed =', f'${my.calculate_aime(earnings2, birth_year2, index=False):,.0f}')

#%%
# check bend points
print('bend points for', str(birth_year1), 'birth year used in website example =', my.get_bend_points(birth_year1))
print('bend points for', str(birth_year2), 'birth year used in website example =', my.get_bend_points(birth_year2))

#%%
# check checks
claim_year1 = 2026
claim_year2 = 2026
claim_age1 = claim_year1 - birth_year1
claim_age2 = claim_year2 - birth_year2
base_pia1 = my.calculate_base_pia(aime1, birth_year1)
base_pia2 = my.calculate_base_pia(aime2, birth_year2)
print('base_pia1 =', base_pia1)
print('base_pia2 =', base_pia2)

sim = my.HouseholdSimulator(p1_birth=birth_year1    , p2_birth=birth_year2,
                            p1_earnings=earnings1   , p2_earnings=earnings2,
                            p1_claim_age=claim_age1 , p2_claim_age=claim_age2, 
                            p1_death=100       , p2_death=100,
                            cola_future=0.03, ss_bend_point_growth_rate=0.03)

out = sim.calculate_for_year(2026, p1_income=0, p2_income=0, p1_ira=0, p2_ira=0)

print('Check_high =', out['Check_high'], '; website example is $4152')
print('Check_low  =', out['Check_low'],  '; website example is $1826')


#%%
# report checks over time
print('birth years:', birth_year1, ',', birth_year2)

claim_age1 = 67
claim_age2 = 62
p1_death = 100
p2_death = 100
cola = 0.03
cola_missing = 0.03
ss_bend_point_growth_rate = 0.02
sim = my.HouseholdSimulator(p1_birth=birth_year1    , p2_birth=birth_year2,
                            p1_earnings=earnings1   , p2_earnings=earnings2,
                            p1_claim_age=claim_age1 , p2_claim_age=claim_age2, 
                            p1_death=p1_death       , p2_death=p2_death,
                            cola_future=cola, ss_bend_point_growth_rate=ss_bend_point_growth_rate)

print(f"aime       : ${sim.aime1:,.2f}, ${sim.aime2:,.2f}")
print(f"base pia   : ${sim.pia_base1:,.2f}, ${sim.pia_base2:,.2f}")
print('claim age  :', claim_age1, ',', claim_age2)
print('death age  :', p1_death, ',', p2_death)
print('cola:', cola, '; bend point growth:', ss_bend_point_growth_rate)

df = sim.calculate_for_years()
print(f"Invested   : ${df['invested'].iloc[-1]:,.2f}")
df.head(10)
# %%
