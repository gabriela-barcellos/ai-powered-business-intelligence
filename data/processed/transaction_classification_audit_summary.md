# Transaction Classification Audit

## 1. Scope

- Processed dataset rows: 536,641
- Rows flagged for review: 132,185
- Rows matching multiple classification conditions: 10,590
- Share of rows flagged: 24.63%

The audit identifies patterns for investigation. It does not automatically correct categories, remove records, or prove the definitive commercial meaning of transactions.

## 2. Existing Category Counts

| Category | Records |
|---|---:|
| cancellation_invoice | 9,251 |
| financial_adjustment_or_negative_price | 3 |
| negative_quantity_review | 1,336 |
| standard_sales_candidate | 524,877 |
| zero_price_review | 1,174 |

## 3. Review Reasons

| Reason | Records |
|---|---:|
| Candidate_without_customer_id | 132,185 |

## 4. Most Frequent Condition Combinations

| Matching conditions | Existing category | Records | Distinct invoices |
|---|---|---:|---:|
| cancellation_invoice | negative_quantity | cancellation_invoice | 9,251 | 3,836 |
| negative_quantity | zero_price | negative_quantity_review | 1,336 | 1,336 |
| bad_debt_description | negative_price | financial_adjustment_or_negative_price | 2 | 2 |
| bad_debt_description | positive_quantity_and_price | financial_adjustment_or_negative_price | 1 | 1 |

## 5. Interpretation and Limitations

- A review flag is not proof of an error.
- A C-prefixed invoice with positive quantity is flagged for inspection; the prefix alone does not establish commercial meaning.
- Multiple matching conditions may be expected because the current classification uses an explicit priority order.
- Missing CustomerID limits customer attribution but does not, by itself, invalidate a sales line.
- Existing transaction categories were not modified.
- The audit does not validate net revenue, refunds, or definitive order counts.

## 6. Recommended Next Steps

- Inspect examples from the most frequent condition combinations.
- Compare flagged invoices with the original Excel source.
- Document evidence before changing classification rules.
- Revalidate metrics after any approved business-rule changes.
