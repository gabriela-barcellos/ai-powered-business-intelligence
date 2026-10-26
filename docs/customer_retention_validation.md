# Customer Retention — Validation Report

## 1. Objective

Document the validation procedures applied to the customer retention and behavior analysis, ensuring consistency between the processed sales data and the generated monthly metrics.

## 2. Validation Results

| Validation | Result |
|---|---|
| Unique identified customers | 4,338 |
| Revenue reconciliation | Difference below £0.01 |
| Quantity reconciliation | 0.000000 difference |
| New + returning customers = active customers | Passed |
| Monthly retention rate formula | Passed |
| Missing retention rate for the final month | Passed |
| Overall validation status | **APPROVED** |

## 3. Retention Rate Calculation

Monthly retention is calculated as:

**Next-month retention rate = (Customers active in both consecutive months / Customers active in the current month) × 100**

The script independently recalculates the rate from the monthly output values and compares it with the stored rate, using a tolerance of 0.000001 percentage points.

## 4. Final Month Handling

The final month has no calculated next-month retention rate because the dataset does not contain a subsequent month for comparison. This is represented as a missing value rather than zero, avoiding a misleading interpretation of customer retention.

## 5. Generated Artifacts

- `data/processed/customer_retention_monthly.csv`
- `data/processed/customer_retention_cohorts.csv`
- `data/processed/customer_retention_summary.md`

## 6. Limitations

- Customer identification and retention metrics are limited to records with an identified customer and qualifying sales transactions.
- The first observed purchase in the available dataset may not represent the customer's first purchase in the company's actual history.
- Passing mathematical validation confirms consistency of the checked metrics, but does not independently prove that every business classification or interpretation is correct.

## 7. Conclusion

All implemented validation checks passed. Revenue and quantity reconcile with the qualifying sales base, customer counts are internally consistent, and the monthly retention rate calculations match the defined formula.

**Status: APPROVED**
