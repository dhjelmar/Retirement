#%%
import math
import os
import pandas as pd

#%%
# --- Official National Average Wage Index (AWI) ---
AWI_TABLE = {
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

#%%
def calculate_aime(earnings_history, birth_year, index=True):
    """Indexes earnings to age 60 and averages the top 35 years."""

    if index:
        indexing_year = birth_year + 60
        # Anchor is the AWI from the year the worker turned 60
        anchor_awi = AWI_TABLE.get(indexing_year, 69846.57) 
        
        indexed_earnings = []
        for year, amount in earnings_history.items():
            if year < indexing_year:
                # Multiplier: (AWI at age 60) / (AWI of work year)
                # Using 1980 as a fallback for very old records
                factor = anchor_awi / AWI_TABLE.get(year, AWI_TABLE[1980])
                indexed_earnings.append(amount * factor)
            else:
                indexed_earnings.append(amount) # No indexing for Age 60+
                
        top_35 = sorted(indexed_earnings, reverse=True)[:35]
        while len(top_35) < 35: top_35.append(0)

    else:
        top_35 = sorted(earnings_history.values(), reverse=True)[:35]
    
    aime = math.floor( sum(top_35) / 420 )
    return aime


#%%
def get_bend_points(birth_year, growth_rate=0.035):
    # National Average Wage Index (AWI) Series
    # Source: SSA.gov (AWI for 1977 is the base year for the formula)
    awi_1977 = 9779.44
    
    # 1. Determine Eligibility Year (Age 62)
    eligibility_year = birth_year + 62
    
    # 2. Determine Indexing Year (Eligibility - 2)
    indexing_year = eligibility_year - 2
    
    if indexing_year not in AWI_TABLE:
        """
        Calculates estimated SS bend points based on AWI growth.
        
        :param target_year: The year the individual turns 62.
        :param growth_rate: Assumed annual increase in Average Wage Index (decimal).
        :return: Dictionary with First and Second bend points.
        """
        # Known 2026 Bend Points (Official)
        base_year = 2026
        bp1_2026 = 1286
        bp2_2026 = 7749
        
        if indexing_year <= base_year:
            # In a real app, you'd use a lookup table for historicals.
            # For this example, we return 2026 values as the floor.
            return {"year": indexing_year, "bp1": bp1_2026, "bp2": bp2_2026}
        
        # Calculate years of growth from the 2026 base
        years_diff = indexing_year - base_year
        
        # Apply compounding growth
        # SSA rounds to the nearest dollar
        bp1 = round(bp1_2026 * (1 + growth_rate) ** years_diff)
        bp2 = round(bp2_2026 * (1 + growth_rate) ** years_diff)
        
    else:
        current_awi = AWI_TABLE.get(indexing_year, 69846.57) # default 69846.57 for future
        
        # 3. Calculate Points using 1979 base figures ($180, $1085)
        ratio = current_awi / awi_1977
        
        bp1 = round(180 * ratio)
        bp2 = round(1085 * ratio)
    
    return bp1, bp2


#%%
def calculate_base_pia(aime, birth_year, growth_rate=0.035):
    '''
    Calculates the Base PIA at age 62.
    growth_rate is only used for Wage Indexing (Bend Points).
    Post-62 COLA is handled by the HouseholdSimulator.
    '''

    b1, b2 = get_bend_points(birth_year, growth_rate)
    if aime <= b1:
        pia = aime * 0.9
    elif aime <= b2:
        pia = (b1 * 0.9) + ((aime - b1) * 0.32)
    else:
        pia = (b1 * 0.9) + ((b2 - b1) * 0.32) + ((aime - b2) * 0.15)

    pia = math.floor(pia * 10) / 10 # SSA rounds to the dime
    return pia

#%%

def pia_adjusted(pia, claim_age, fra=67, is_spousal=False):
    """
    Calculates the benefit amount based on age relative to FRA.
    Returns: The dollar amount (PIA * reduction/credit factor).
    """
    # Calculate months of difference from Full Retirement Age (FRA)
    m_diff = (claim_age - fra) * 12

    # 1. DELAYED RETIREMENT (After age 67)
    if m_diff > 0:
        if is_spousal:
            # Spousal benefits do NOT earn delayed credits
            return pia
        # Individual benefits earn 2/3 of 1% per month (8% per year)
        # Maxes out at age 70 (36 months past FRA)
        months_of_credit = min(m_diff, 36)
        factor = 1 + (months_of_credit * (2/300))
        return pia * factor

    # 2. EARLY RETIREMENT (Before age 67)
    m_early = abs(m_diff)
    
    if is_spousal:
        # Spousal Reduction: 25/36 of 1% for first 36mo, 5/12 of 1% thereafter
        reduction = (min(36, m_early) * (25/3600)) + (max(0, m_early - 36) * (5/1200))
    else:
        # Individual Reduction: 5/9 of 1% for first 36mo, 5/12 of 1% thereafter
        reduction = (min(36, m_early) * (5/900)) + (max(0, m_early - 36) * (5/1200))
    
    factor = 1 - reduction
    return pia * factor