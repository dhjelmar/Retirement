import math

# --- 1. THE DATA: Official National Average Wage Index (AWI) ---
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
    return math.floor( sum(top_35) / 420 )
