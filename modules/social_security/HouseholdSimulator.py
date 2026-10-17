# --- Household Simulation ---
import math
import pandas as pd
import modules as my

# COLA for year X is usually announced in Oct and applied to Dec/Jan benefits
cola_data = {
        2021: 5.9,
        2022: 8.7,
        2023: 3.2,
        2024: 2.5,  # 2025 per Gemini but 2024 per social security example
        2025: 2.8,  # Projected/Future
            } 

class HouseholdSimulator:
    def __init__(self, p1_birth, p2_birth, p1_earnings, p2_earnings, 
                 p1_claim_age=67, p2_claim_age=67, p1_death=90, p2_death=90,
                 cola_future=0.03, ss_bend_point_growth_rate=0.02):
        
        self.p1_birth, self.p2_birth = p1_birth, p2_birth
        self.p1_claim_year = p1_birth + p1_claim_age
        self.p2_claim_year = p2_birth + p2_claim_age
        self.p1_death, self.p2_death = p1_death, p2_death
        self.cola_future = cola_future
        
        # 1. Pre-calculate the "Base PIA" at age 62
        self.aime1 =my.calculate_aime(p1_earnings, p1_birth)
        self.aime2 =my.calculate_aime(p2_earnings, p2_birth)
        self.pia_base1 = my.calculate_base_pia(self.aime1, 
                                          p1_birth, 
                                          growth_rate=ss_bend_point_growth_rate)
        self.pia_base2 = my.calculate_base_pia(self.aime2, 
                                          p2_birth,
                                          growth_rate=ss_bend_point_growth_rate)

        # 2. Determine High/Low for Spousal Logic
        if self.pia_base1 >= self.pia_base2:
            self.pia_h, self.pia_l = self.pia_base1, self.pia_base2
            self.birth_high, self.birth_low = p1_birth, p2_birth
            self.c_age_h, self.c_age_l = p1_claim_age, p2_claim_age
            self.d_age_h, self.d_age_l = p1_death, p2_death
        else:
            self.pia_h, self.pia_l = self.pia_base2, self.pia_base1
            self.birth_high, self.birth_low = p2_birth, p1_birth
            self.c_age_h, self.c_age_l = p2_claim_age, p1_claim_age
            self.d_age_h, self.d_age_l = p2_death, p1_death


    def calculate_for_year(self, year, p1_income=0, p2_income=0, spend=0, p1_ira=0, p2_ira=0):
        """
        Calculates the complete household financial picture for a specific year,
        accounting for Social Security, Work, RMDs, and Taxes.
        """
        # 1. Vitality Checks
        p1_alive = year <= (self.p1_birth + self.p1_death)
        p2_alive = year <= (self.p2_birth + self.p2_death)
        
        if not p1_alive and not p2_alive:
            return None # End of simulation if both have passed

        # 2. Determine current ages
        age_h = year - self.birth_high
        age_l = year - self.birth_low
        is_joint = p1_alive and p2_alive

        # 3. Benefit Logic (with Deemed Filing & Survivor Step-ups)
        check_h, check_l = 0.0, 0.0
        
        if p1_alive and p2_alive:
            # --- STANDARD JOINT LOGIC ---
            # High Earner
            if age_h >= self.c_age_h:
                base_h = my.pia_adjusted(self.pia_h, self.c_age_h)
                check_h = self.get_cola_adjusted_check(base_h, self.birth_high, year)
            
            # Low Earner (Your logic + Deemed Filing gate)
            if age_l >= self.c_age_l:
                own_at_claim = my.pia_adjusted(self.pia_l, self.c_age_l, fra=67)
                
                # Spousal top-up ONLY if high earner has filed
                if age_h >= self.c_age_h:
                    spousal_limit = self.pia_h * 0.50
                    excess_base = max(0, spousal_limit - self.pia_l)
                    topup_at_claim = my.pia_adjusted(excess_base, self.c_age_l, fra=67, is_spousal=True)
                else:
                    topup_at_claim = 0
                    
                check_l = self.get_cola_adjusted_check(own_at_claim + topup_at_claim, self.birth_low, year)

        else:
            # --- SURVIVOR LOGIC ---
            # If one is dead, the survivor gets the higher of the two checks
            # Based on the High Earner's PIA (including any credits they earned)
            survivor_base = my.pia_adjusted(self.pia_h, self.c_age_h)
            # Use the survivor's birth year for COLA tracking
            living_birth = self.birth_high if p1_alive else self.birth_low
            
            if p1_alive: check_h = self.get_cola_adjusted_check(survivor_base, living_birth, year)
            if p2_alive: check_l = self.get_cola_adjusted_check(survivor_base, living_birth, year)

        # 4. Earnings Test (Withholding for work before FRA 67)
        # 2026 Estimated Limit
        limit = 24000
        if p1_alive and age_h < 67 and p1_income > limit:
            check_h = max(0, check_h - ((p1_income - limit) / 2) / 12)
        if p2_alive and age_l < 67 and p2_income > limit:
            check_l = max(0, check_l - ((p2_income - limit) / 2) / 12)

        # 5. RMDs and Other Income
        rmd_h = self.calculate_rmd(p1_ira, age_h) if p1_alive else 0
        rmd_l = self.calculate_rmd(p2_ira, age_l) if p2_alive else 0
        
        # round down to the dollar for social security check
        check_h = math.floor(check_h)
        check_l = math.floor(check_l)

        total_ss = (check_h + check_l) * 12.
        total_other_income = p1_income + p2_income + rmd_h + rmd_l

        # 6. Tax Torpedo (Calculates taxable portion of SS)
        taxable_ss = self.calculate_taxable_benefits(total_ss, total_other_income, is_joint)
        
        # 7. Final Net Calculation
        # Simple estimate: (Total Income - Standard Deduction) * Blended Rate
        deduction = 30000 if is_joint else 15000
        est_tax = max(0, (total_other_income + taxable_ss - deduction) * 0.18)

        return {
            "Year": year,
            'Age_p1': year - self.p1_birth,
            'Age_p2': year - self.p2_birth,
            'Check_high': round(check_h, 2),
            'Check_low': round(check_l, 2),
            "Total_SS": round(total_ss, 2),
            "Other_Income": round(total_other_income, 2),
            "Taxable_SS": round(taxable_ss, 2),
            "Net_Cash": round(total_ss + total_other_income - est_tax - spend, 2),
            "Status": "Joint" if is_joint else "Survivor",
            "RMD1": rmd_h,
            "RMD2": rmd_l
        }


    def calculate_for_years(self, start, end, roi=0.05,
                            p1_income=0, p2_income=0, spend=0,
                            p1_ira=0, p2_ira=0):
        results = []
        cumulative =0
        invested = 0
        for year in range(start, end):
            row = self.calculate_for_year(year, 
                                        p1_income, p2_income, spend,
                                        p1_ira, p2_ira)
            if not row: break       
            # Update balances for next year (Growth - RMD - Fees)
            p1_ira = (p1_ira - row.get('RMD', 0)) * 1.05
            p1_ira = (p1_ira - row.get('RMD', 0)) * 1.05
            row['p1_ira'] = p1_ira
            row['p2_ira'] = p2_ira
            cumulative = cumulative + row['Net_Cash']
            row['cumulative'] = cumulative
            invested = invested * ( 1 + roi ) + row['Net_Cash']
            row['invested'] = invested
            results.append(row)
        df = pd.DataFrame(results)
        return df


    def get_cola_adjusted_check(self, check, birth, current_year):
        """
        Adjusts the PIA for COLA annually, using historical data where available
        and the simulation's COLA rate for future/missing years.
        """
        eligibility_year = birth + 62 
        adjusted_pia = check
        
        # Iterate from age 62 up to the year before the current simulation year
        # COLA for year N affects the benefit paid in year N+1
        for year in range(eligibility_year, current_year):
            # 1. Determine which COLA rate to use
            if year in cola_data:
                # Use historical data from aime_pia.py (converted to decimal)
                cola_rate = cola_data[year] / 100
            else:
                # Use the 'cola' rate defined in the Simulator instance
                cola_rate = self.cola_future
                
            # 2. Apply COLA
            adjusted_pia = adjusted_pia * (1 + cola_rate)
            
            # 3. SSA Rounding Rule: Round down to the lower dime ($0.10)
            adjusted_pia = math.floor(adjusted_pia * 10) / 10
            
        return adjusted_pia

    def calculate_taxable_benefits(self, ss_total, other_income, is_joint):
        combined = other_income + (0.5 * ss_total)
        
        # Thresholds: Joint ($32k/$44k) vs Single ($25k/$34k)
        base = 32000 if is_joint else 25000
        upper = 44000 if is_joint else 34000
        
        if combined > upper:
            taxable = (combined - upper) * 0.85 + (upper - base) * 0.5
        elif combined > base:
            taxable = (combined - base) * 0.5
        else:
            taxable = 0
            
        return min(taxable, ss_total * 0.85)


    def get_joint_cash_flow(self, year, p1_work, p2_work, p1_balance, p2_balance):
        # 1. Ages for each person
        age1 = year - self.p1_birth
        age2 = year - self.p2_birth
        
        # 2. Individual SS Benefits (from your calculate_for_year logic)
        ss_results = self.calculate_for_year(year)
        gross_ss_total = ss_results['Total']
        
        # 3. Individual RMDs
        p1_rmd = self.calculate_rmd(p1_balance, age1)
        p2_rmd = self.calculate_rmd(p2_balance, age2)
        
        # 4. Combined Household Income (excluding SS)
        # This is what determines how much of the SS is taxable
        total_other_income = p1_work + p2_work + p1_rmd + p2_rmd
        
        # 5. Taxation (Married Filing Jointly)
        taxable_ss = self.calculate_taxable_benefits(gross_ss_total, total_other_income)
        
        # 6. Final Combined Picture
        total_household_income = gross_ss_total + total_other_income
        
        # Simplified Federal Tax calculation on (Other Income + Taxable SS)
        # Using a 2026 standard deduction for a couple (~$30,000)
        adjusted_gross_income = total_other_income + taxable_ss
        taxable_income_base = max(0, adjusted_gross_income - 30000)
        
        # Applying a simple blended tax bracket
        estimated_tax = self.estimate_federal_tax(taxable_income_base)

        return {
            "Year": year,
            "P1_Age": age1,
            "P2_Age": age2,
            "Total_SS": round(gross_ss_total, 2),
            "Total_RMD": round(p1_rmd + p2_rmd, 2),
            "Taxable_SS": round(taxable_ss, 2),
            "Net_Household_Cash": round(total_household_income - estimated_tax, 2)
        }
    

    def calculate_rmd(self, balance, age):
        """
        Calculates the Required Minimum Distribution based on IRS Uniform Lifetime Table.
        """
        # 1. Determine the RMD Start Age based on birth year (SECURE Act 2.0)
        # This assumes p1_birth is a 4-digit year (e.g., 1965)
        start_age = 75 if self.p1_birth >= 1960 else 73
        
        if age < start_age or balance <= 0:
            return 0.0

        # 2. IRS Uniform Lifetime Table Factors (Selected ages for mapping)
        # The factor is the "Distribution Period" (expected remaining years)
        irs_table = {
            73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
            80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 90: 12.2,
            95: 8.9, 100: 6.4, 110: 3.5, 120: 2.0
        }

        # 3. Find the factor for the specific age
        # If age is between keys, we find the closest lower key
        if age in irs_table:
            factor = irs_table[age]
        else:
            # Fallback for very old age or gaps: get the value for the highest key <= age
            sorted_keys = sorted(irs_table.keys())
            closest_age = max([k for k in sorted_keys if k <= age])
            factor = irs_table[closest_age]

        # RMD Formula: Year-end Balance / Distribution Period
        return round(balance / factor, 2)
