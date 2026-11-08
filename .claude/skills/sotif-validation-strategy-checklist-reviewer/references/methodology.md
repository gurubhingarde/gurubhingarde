# SOTIF Validation Strategy Checklist Methodology

## Scoring Conventions

| Rating | Meaning |
|--------|---------|
| FC | Fully Compliant |
| LC | Largely Compliant |
| PC | Partially Compliant |
| NO | Not Compliant |
| NA | Not Applicable |
| — | Pending |

## Four Mandatory Validation Methods (ISO 21448 §10)

1. **Real-World Driving**: Fleet accumulates target mileage with geographic, weather, temporal distribution
2. **Simulation**: Scenario library (NHTSA/EuroNCAP/custom) with correlation to real-world validated
3. **Proving Ground**: Test cases with pass/fail criteria on controlled facility
4. **Field Monitoring**: Telemetry plan for anomaly detection and validation evidence collection

## Key Checks

**Check 1**: Acceptance criterion referenced from SOTIF Analysis  
**Check 2**: All four validation methods covered  
**Check 3**: Real-world mileage target quantified (e.g., "100k miles")  
**Check 4**: Fleet coverage defined (geographic, weather, time-of-day distribution)  
**Check 5**: Simulation scenario library cited (NHTSA/EuroNCAP or custom)  
**Check 6**: Simulation correlation with real-world validated  
**Check 7**: Proving ground test catalog with >=10 test cases + pass/fail criteria  
**Check 8**: Field monitoring telemetry plan defined  
**Check 9**: Acceptance criterion tracking shows current vs. target status  
**Check 10**: Coverage gaps explicitly noted and justified  
**Check 11**: Statistical significance of validation evidence justified (confidence intervals, sample size)  
**Check 12**: ISO 21448 §10-11 referenced throughout  

## Common Gaps

- Only 2-3 validation methods covered instead of all 4
- Real-world mileage target not quantified
- Fleet geographic/weather/temporal distribution not specified
- Simulation correlation with real-world not validated
- Proving ground test cases lack pass/fail criteria
- Field monitoring plan vague or missing
- No explicit coverage gap documentation
- Statistical significance not justified
