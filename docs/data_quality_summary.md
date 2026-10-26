# Data Quality Summary — Online Retail

## 1. Files

- Original file: `data\raw\Online Retail.xlsx`
- Processed file: `data\processed\online_retail_processed.csv`
- The original file was preserved.

## 2. Record Counts

- Original rows: 541,909
- Original columns: 8
- Exact duplicate rows removed: 5,268
- Processed rows: 536,641
- Exact duplicate rows remaining: 0

## 3. Missing Values Before Deduplication

| Column | Missing records |
|---|---:|
| InvoiceNo | 0 |
| StockCode | 0 |
| Description | 1,454 |
| Quantity | 0 |
| InvoiceDate | 0 |
| UnitPrice | 0 |
| CustomerID | 135,080 |
| Country | 0 |

## 4. Missing Values After Deduplication

| Column | Missing records |
|---|---:|
| InvoiceNo | 0 |
| StockCode | 0 |
| Description | 1,454 |
| Quantity | 0 |
| InvoiceDate | 0 |
| UnitPrice | 0 |
| CustomerID | 135,037 |
| Country | 0 |
| TransactionCategory | 0 |
| LineValue | 0 |
| InvoiceYearMonth | 0 |

## 5. Transaction Classification

Categories are mutually exclusive and follow a priority order. Classification is preliminary and does not establish the definitive commercial meaning of each record.

| Category | Records |
|---|---:|
| cancellation_invoice | 9,251 |
| financial_adjustment_or_negative_price | 3 |
| negative_quantity_review | 1,336 |
| standard_sales_candidate | 524,877 |
| zero_price_review | 1,174 |

## 6. Additional Data Checks

- Invalid invoice dates: 0
- Negative quantities: 10,587
- Negative unit prices: 2
- Zero unit prices: 2,510
- Records without CustomerID: 135,037

## 7. Preparation Validation

| Check | Result |
|---|---|
| Original and processed row counts reconcile | PASS |
| Category counts reconcile to processed rows | PASS |
| No exact duplicate rows remain | PASS |
| LineValue matches Quantity x UnitPrice | PASS |
| No invalid invoice dates detected | PASS |

- Overall preparation validation: **PASSED**
- Transaction category records counted: 536,641

These checks verify structural and arithmetic consistency. They do not independently validate the business meaning of the transaction categories or prove that candidate revenue is net revenue.

## 8. Definitions and Limitations

- `LineValue` is `Quantity x UnitPrice`; it is not, by itself, validated net revenue.
- `standard_sales_candidate` identifies rows with positive quantity and positive unit price that were not assigned to a higher-priority category. These are candidates, not definitively validated sales.
- Invoices beginning with `C` are classified separately according to the current rule.
- Negative quantities on invoices not beginning with `C` remain under review.
- Financial adjustments and negative prices are separated from sales candidates according to the current priority order.
- Zero-price records remain under review.
- Unclassified records remain in `other_review`.
- Rows are not removed solely because of missing values, zero prices, or negative quantities.
- Net revenue and definitive order counts have not yet been validated.
- Classification priority is a technical rule and does not, by itself, confirm the commercial nature of a transaction.

## 9. Next Validation Steps

- Audit transaction categories against invoice, quantity, price, and description patterns.
- Validate the business rules for revenue, orders, and returns.
- Compare samples from the processed CSV with the original Excel file.
- Confirm results before treating the metrics as definitive.
