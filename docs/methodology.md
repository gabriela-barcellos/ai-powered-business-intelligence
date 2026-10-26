# Business Rules and Data Preparation Methodology

## 1. Objective

Define transparent, reproducible rules for preparing the UCI Online Retail dataset and calculating sales metrics.

## 2. Source data

- Original file: `data/raw/Online Retail.xlsx`
- Original records: 541,909
- Currency: GBP (£)
- Original file must remain unchanged.

## 3. Transaction classification

### Standard sales candidates
Rows with positive quantities, positive unit prices, and invoice numbers not beginning with `C`.

These rows are candidates for sales KPIs. Their validity must be checked during preparation.

### Cancellation invoices
Rows whose invoice number begins with `C`. These will be identified and reported separately.

### Negative quantities without cancellation prefix
Retain and classify separately until their meaning is better understood.

### Zero unit prices
Preserve and investigate. Do not automatically classify these records as ordinary sales or errors.

### Negative unit prices
The two observed `Adjust bad debt` records must be separated from ordinary product sales.

## 4. Revenue definitions

- Line value: `Quantity × UnitPrice`.
- Gross sales candidate value: sum of line values for classified standard sales candidates.
- Cancellation and return values: report separately by transaction category.
- Net revenue: do not publish until the treatment of cancellations, returns, and financial adjustments is validated.

All financial values must remain in GBP.

## 5. Order and customer metrics

- Order count: distinct invoice numbers for the defined sales population, excluding cancellation invoices.
- Quantity sold: sum of positive quantities for the defined sales population.
- Identified customers: distinct non-missing `CustomerID` values.
- Missing customer identifiers must not automatically cause transaction deletion.

## 6. Duplicate handling

- Identify exact duplicate rows across all original columns.
- Remove exact duplicates only in the processed copy, after validating the impact.
- Preserve the original file.
- Record the number of rows removed and the number of rows remaining.
- Do not remove rows merely because the same invoice and product appear more than once.

## 7. Data-quality controls

The preparation process must report:

- Row counts before and after processing.
- Missing values by column.
- Exact duplicates.
- Cancellation invoices.
- Negative quantities and prices.
- Zero-price records.
- Invalid dates and relevant data-type issues.

## 8. Validation and limitations

All rules must be implemented reproducibly and tested against the observed dataset.

Unusual records must be classified transparently. Do not infer that an unexplained transaction is an error without supporting evidence.

Net revenue remains undefined until transaction categories and their financial treatment have been validated.
