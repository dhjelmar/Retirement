# IRA Retirement Analysis Documentation

## Overview

The `ira.py` script performs a comprehensive retirement planning analysis focused on optimizing Traditional IRA to Roth IRA conversions to minimize lifetime tax burden while managing Required Minimum Distributions (RMDs) and Medicare costs.

## What the Analysis Does

### Core Objective
The analysis evaluates different annual taxable income limits to determine the optimal strategy for converting Traditional IRA funds to Roth IRA while minimizing the present value of total costs (taxes + Medicare).

### Key Parameters
- **Analysis Period**: 42 years (2023-2064)
- **Starting Age**: 59 years old (born 1964)
- **Initial IRA Value**: $2,000,000
- **Investment Return Rate (ROI)**: 7%
- **Minimum Acceptable Rate of Return (MARR)**: 7%
- **Heir Information**: Born 1996, $150,000 annual income

### Income Profile
- 2023-2025: $300,000 annually
- 2026: $218,000 
- 2027+: $135,000 base income
- Social Security: $44,000 starting at age 72, increasing to $98,000 ($44k + $54k)

## How the Analysis Works

### 1. Scenario Evaluation (`scenario.py`)
The analysis tests 9 different maximum taxable income limits:
- $1,000,000,000 (essentially no limit)
- $500,000, $395,000, $350,000, $300,000, $250,000, $207,000, $150,000, $97,000

For each scenario, the model:

#### Annual Calculations:
1. **RMD Calculation**: Uses IRS Uniform Lifetime Table to calculate required distributions starting at age 73
2. **IRA Growth**: Applies 7% growth to remaining IRA balance
3. **Conversion Strategy**: Converts Traditional IRA to Roth up to the maximum taxable income limit
4. **Tax Calculation**: Computes federal and state taxes on total taxable income
5. **Medicare Costs**: Calculates Medicare premiums based on Modified Adjusted Gross Income (MAGI) from 2 years prior
6. **Present Value**: Computes present value of spending power and estate value

#### Estate Planning Component:
- Models 10-year distribution of remaining IRA to heir
- Uses heir's income tax bracket to calculate after-tax inheritance value
- Applies present value discounting to estate distributions

### 2. Tax Calculations (`tax.py`)
#### Federal Tax Brackets (2024):
- 0%: $0 - $24,000
- 12%: $24,000 - $97,000
- 22%: $97,000 - $207,000
- 24%: $207,000 - $395,000
- 32%: $395,000 - $501,000
- 35%: $501,000 - $752,000
- 37%: $752,000+

#### New York State Tax:
- Progressive rates from 4% to 10.9%
- Treats capital gains as ordinary income

### 3. Medicare Cost Modeling (`medicare.py`)
Medicare premiums based on MAGI (2 years prior):
- Base premium: $185/month (Part B) + $37/month (Part D)
- Income-Related Monthly Adjustment Amount (IRMAA) surcharges apply at higher income levels
- Maximum surcharge: $628.9/month (Part B) + $85.8/month (Part D)

### 4. Required Minimum Distributions (`rmd.py`)
- Uses IRS Uniform Lifetime Table
- Distributions mandatory starting at age 73
- Factor decreases with age (higher required distributions)

### 5. Estate Valuation (`pv_estate.py`)
- Models heir's 10-year withdrawal strategy
- Uses IRS Single Life Expectancy Table for distribution factors
- Calculates present value of after-tax distributions to heir

## Analysis Outputs

### 1. Data Files
- Individual scenario results: `ira_out_[max_taxable].csv`
- Summary comparison: `ira_out.csv`

### 2. Visualizations
- **Cumulative Cost Plot**: Shows total taxes and Medicare costs over time
- **Taxable Income Plot**: Displays annual taxable income by scenario
- **Present Value Plot**: Shows cumulative present value of benefits

### 3. Key Metrics
- **Cumulative Cost**: Total lifetime taxes and Medicare payments
- **Present Value**: Net present value of spending power plus estate value
- **Optimal Strategy**: Scenario with highest present value

## Analysis Gaps and Potential Improvements

### 1. Inflation Modeling
**Current Gap**: No inflation adjustment for income, tax brackets, or Medicare costs
**Improvement**: Incorporate 2-3% annual inflation rate for:
- Social Security benefits
- Tax bracket thresholds
- Medicare premium increases
- Living expenses

### 2. Investment Risk Analysis
**Current Gap**: Assumes constant 7% return
**Improvement**: 
- Monte Carlo simulation with return volatility
- Sequence of returns risk analysis
- Different asset allocation scenarios
- Market crash scenarios during critical conversion years

### 3. Tax Law Changes
**Current Gap**: Assumes current tax structure remains constant
**Improvement**:
- Scenario analysis for potential tax law changes
- Sunset of Tax Cuts and Jobs Act (2025)
- State tax relocation strategies

### 4. Health Care Cost Modeling
**Current Gap**: Only includes Medicare premiums
**Improvement**:
- Long-term care insurance costs
- Out-of-pocket medical expenses
- Medigap insurance premiums
- Health Savings Account (HSA) integration

### 5. Social Security Optimization
**Current Gap**: Fixed Social Security claiming strategy
**Improvement**:
- Delayed retirement credits analysis
- Spousal benefit optimization
- Tax torpedo analysis (provisional income thresholds)

### 6. Roth Conversion Timing
**Current Gap**: Linear conversion strategy
**Improvement**:
- Market timing for conversions (convert more in down markets)
- Tax bracket management across multiple years
- Bunching conversions in low-income years

### 7. Estate Planning Enhancements
**Current Gap**: Simple 10-year distribution model
**Improvement**:
- Multiple beneficiary scenarios
- Charitable giving strategies
- Trust structures
- Step-up basis considerations

### 8. Additional Income Sources
**Current Gap**: Limited income diversification
**Improvement**:
- Pension income modeling
- Part-time work scenarios
- Rental property income
- Annuity payments

### 9. Sensitivity Analysis
**Current Gap**: Limited parameter sensitivity testing
**Improvement**:
- Sensitivity to MARR assumptions
- Impact of different conversion limits
- Break-even analysis for key parameters

### 10. Advanced Optimization
**Current Gap**: Grid search over discrete income limits
**Improvement**:
- Dynamic programming for optimal year-by-year conversion amounts
- Machine learning optimization
- Multi-objective optimization (minimize taxes vs. maximize liquidity)

## Recommendations for Enhancement

1. **Priority 1**: Add inflation modeling and investment return volatility
2. **Priority 2**: Enhance health care cost projections and Social Security optimization
3. **Priority 3**: Implement dynamic conversion optimization algorithm
4. **Priority 4**: Add comprehensive sensitivity analysis and scenario planning tools

The current analysis provides a solid foundation for IRA conversion planning but would benefit significantly from incorporating uncertainty, inflation, and more sophisticated optimization techniques.