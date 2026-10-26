
# Metrics Validation — Online Retail

## 1. Objective

This document records the arithmetic and consistency checks performed on the sales metrics generated from the processed Online Retail dataset.

The checks help establish reproducibility and internal consistency. They do not independently validate the commercial meaning of transactions or establish accounting-grade net revenue.

## 2. Dataset and Scope

- Source dataset: `data/raw/Online Retail.xlsx`
- Processed dataset: `data/processed/online_retail_processed.csv`
- Original records: 541,909
- Exact duplicate rows removed: 5,268
- Processed records: 536,641
- Analysis period: December 2010 to December 2011
- Currency: GBP (£)

December 2011 contains data only through December 9 and is excluded from the monthly revenue comparison chart.

## 3. Sales Candidate Metrics

Metrics are calculated using records classified as `standard_sales_candidate`.

| Metric | Validated result |
|---|---:|
| Candidate records | 524,877 |
| Candidate revenue (`LineValue`) | £10,631,048.74 |
| Candidate quantity | 5,572,419 |
| Distinct invoices containing candidate sales | 19,959 |
| Identified customers | 4,338 |

### Metric definitions

- **Candidate revenue:** Sum of `LineValue` for records classified as `standard_sales_candidate`.
- **Candidate quantity:** Sum of `Quantity` for the same records.
- **Distinct invoices containing candidate sales:** Number of unique `InvoiceNo` values among candidate records.
- **Identified customers:** Number of unique `CustomerID` values among candidate records.

These are preliminary analytical metrics, not definitive accounting or commercial measures.

## 4. Arithmetic Validation Results

The following checks were executed against the processed dataset.

| Check | Result |
|---|---|
| General revenue reconciles with monthly revenue totals | PASS |
| General quantity reconciles with monthly quantity totals | PASS |
| `LineValue` matches `Quantity × UnitPrice` for candidate records | PASS |
| Missing or non-numeric `LineValue` values in candidate records | 0 |
| Missing or non-numeric `Quantity` values in candidate records | 0 |
| Missing or non-numeric `UnitPrice` values in candidate records | 0 |
| Candidate records with negative `LineValue` | 0 |
| Candidate records with zero `LineValue` | 0 |
| Candidate invoices associated with multiple months | 0 |

The general and monthly totals reconciled with no observed difference in revenue or quantity.

## 5. Invoice Classification Findings

The invoice-level review identified:

- 19,906 invoices containing only `standard_sales_candidate` records.
- 53 invoices containing candidate records alongside records assigned to other categories.
- 5,941 invoices without any `standard_sales_candidate` records.

The 53 mixed-category invoices contain candidate records alongside zero-price review and/or negative-quantity review records.

For this reason, the current invoice metric is best described as **Distinct Invoices Containing Candidate Sales**, rather than a definitive count of completed orders.

## 6. Transaction Classification Limitations

The transaction classification remains preliminary.

- `standard_sales_candidate` identifies records with positive quantity and positive unit price that were not assigned to a higher-priority category.
- Invoices beginning with `C` are classified separately under the current rules.
- Negative quantities, zero-price records, and financial adjustments are handled through separate review categories.
- A single invoice may contain records assigned to different categories.
- Missing customer identifiers prevent attribution to an identified customer but do not automatically invalidate a transaction.

The arithmetic checks do not independently confirm the commercial meaning of these categories.

## 7. Revenue Limitations

`LineValue` is calculated as:

`Quantity × UnitPrice`

This value is a nominal line amount. It has not been independently reconciled against accounting records, validated net revenue, or a complete business definition of returns and refunds.

The candidate revenue figure must therefore not be presented as definitively validated net revenue.

## 8. Conclusion

The current sales metrics passed the arithmetic consistency checks performed against the processed dataset.

The results are reproducible and internally consistent within the current classification rules. Further business-rule validation is required before the metrics can be considered definitive commercial or accounting measures.
