# Data Quality Report — Online Retail

## 1. Dataset

- **Source:** UCI Machine Learning Repository — Online Retail
- **Original file:** `data/raw/Online Retail.xlsx`
- **Original records:** 541,909
- **Columns:** 8
- **Observed period:** December 1, 2010 to December 9, 2011
- **Currency:** GBP (£)

## 2. Data Integrity and Structure

- All eight expected columns were identified.
- No invalid dates were found during the initial inspection.
- A total of 5,268 duplicate rows beyond the first occurrence were identified.
- A total of 10,147 rows belong to groups containing exact duplicates.

## 3. Missing Values

| Column | Missing Records |
|---|---:|
| `CustomerID` | 135,080 |
| `Description` | 1,454 |

Records will not be automatically excluded due to missing values. Treatment decisions will depend on the analytical objective and impact assessment.

## 4. Quantities and Prices

| Occurrence | Records |
|---|---:|
| Negative quantity | 10,624 |
| Negative unit price | 2 |
| Zero unit price | 2,515 |

Negative quantities will be investigated before defining revenue and order calculation rules.

The two negative unit prices are associated with the description `Adjust bad debt` and product code `B`.

Zero-price records appear under various descriptions, including `check`, `damages`, `damaged`, `found`, and missing descriptions. These records will not be automatically classified as normal sales.

## 5. Cancellations

A total of 9,288 rows with invoice numbers beginning with `C` were identified. All have negative quantities.

Another 1,336 rows have negative quantities without the `C` prefix. In the inspected examples, these rows have zero prices, missing descriptions, and missing customer IDs.

These patterns will be considered when defining data treatment rules, without assuming that all records have the same origin.

## 6. Potential Impact of Duplicates

- Excess rows: 5,268.
- Quantity summed across excess rows: 13,948.
- Nominal value of excess rows: £21,740.98.
- Excess rows with positive quantities: 5,231.
- Excess rows with negative quantities: 37.

The nominal value represents the sum of `Quantity × UnitPrice` across excess rows. It does not necessarily represent the final impact on net revenue.

## 7. Preliminary Rules

1. Preserve the original file without modifications.
2. Investigate and document duplicates before applying deduplication.
3. Do not automatically exclude records with missing values.
4. Do not automatically remove negative quantities or zero prices.
5. Identify cancellations using the invoice prefix, documenting the limitations of this rule.
6. Define revenue and order metrics before calculating KPIs.
7. Validate and record the number of records before and after each transformation.

## 8. Next Steps

- Finalize business rules.
- Implement a reproducible data preparation script.
- Generate the processed dataset without overwriting the original file.
- Produce a data quality report before and after treatment.
- Validate the results and document limitations.
