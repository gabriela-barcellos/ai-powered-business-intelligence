
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "online_retail_processed.csv"
)

AUDIT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "transaction_classification_audit.csv"
)

SUMMARY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "transaction_classification_audit_summary.md"
)

COMBINATIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "transaction_classification_overlaps.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig",
        dtype={"InvoiceNo": "string"},
    )

    required_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "InvoiceDate",
        "Quantity",
        "UnitPrice",
        "CustomerID",
        "TransactionCategory",
        "LineValue",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    df["InvoiceNo"] = df["InvoiceNo"].str.strip()
    df["Description"] = df["Description"].astype("string")

    for column in ["Quantity", "UnitPrice", "LineValue"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


# ============================================================
# CLASSIFICATION OVERLAP AUDIT
# ============================================================

def audit_classification(df):
    invoice = df["InvoiceNo"].str.upper()

    description = (
        df["Description"]
        .str.strip()
        .str.lower()
    )

    quantity = df["Quantity"]
    price = df["UnitPrice"]
    category = df["TransactionCategory"]

    is_c_invoice = invoice.str.startswith("C", na=False)
    is_bad_debt = description.eq("adjust bad debt").fillna(False)
    is_negative_price = price < 0
    is_negative_quantity = quantity < 0
    is_zero_price = price == 0
    is_positive_quantity_and_price = (
        (quantity > 0) & (price > 0)
    )

    missing_customer = (
        df["CustomerID"].isna()
        | df["CustomerID"].astype("string").str.strip().eq("")
    )

    # Keep each condition separate to reveal exact overlaps.
    conditions = pd.DataFrame(
        {
            "cancellation_invoice": is_c_invoice,
            "bad_debt_description": is_bad_debt,
            "negative_price": is_negative_price,
            "negative_quantity": is_negative_quantity,
            "zero_price": is_zero_price,
            "positive_quantity_and_price": (
                is_positive_quantity_and_price
            ),
        },
        index=df.index,
    )

    df["MatchingConditionCount"] = conditions.sum(axis=1)

    df["MatchingConditions"] = conditions.apply(
        lambda row: " | ".join(
            row.index[row].tolist()
        ),
        axis=1,
    )

    df["MissingCustomerID"] = missing_customer

    # Diagnose category mismatches without changing categories.
    reasons = pd.Series("", index=df.index, dtype="string")

    def add_reason(mask, reason):
        nonlocal reasons
        mask = mask.fillna(False)
        reasons.loc[mask] = reasons.loc[mask].where(
            reasons.loc[mask].eq(""),
            reasons.loc[mask] + "; ",
        ) + reason

    add_reason(
        is_c_invoice & (quantity > 0),
        "C_invoice_with_positive_quantity",
    )

    add_reason(
        is_bad_debt
        & (category != "financial_adjustment_or_negative_price"),
        "Bad_debt_category_mismatch",
    )

    add_reason(
        is_negative_price
        & (category != "financial_adjustment_or_negative_price"),
        "Negative_price_category_mismatch",
    )

    add_reason(
        is_negative_quantity
        & ~is_c_invoice
        & (category != "negative_quantity_review"),
        "Negative_quantity_category_mismatch",
    )

    add_reason(
        is_zero_price
        & ~is_c_invoice
        & ~is_bad_debt
        & ~is_negative_price
        & ~is_negative_quantity
        & (category != "zero_price_review"),
        "Zero_price_category_mismatch",
    )

    add_reason(
        (category == "standard_sales_candidate")
        & (quantity <= 0),
        "Candidate_with_nonpositive_quantity",
    )

    add_reason(
        (category == "standard_sales_candidate")
        & (price <= 0),
        "Candidate_with_nonpositive_price",
    )

    add_reason(
        (category == "standard_sales_candidate")
        & missing_customer,
        "Candidate_without_customer_id",
    )

    add_reason(
        category == "other_review",
        "Unclassified_record",
    )

    df["AuditReasons"] = reasons
    df["RequiresReview"] = reasons.ne("")

    audit_df = df.loc[df["RequiresReview"]].copy()

    # Export exact combinations where multiple conditions apply.
    overlaps = df.loc[
        df["MatchingConditionCount"] > 1
    ].copy()

    combination_counts = (
        overlaps.groupby(
            ["MatchingConditions", "TransactionCategory"],
            dropna=False,
        )
        .agg(
            Records=("InvoiceNo", "size"),
            DistinctInvoices=("InvoiceNo", "nunique"),
            DistinctStockCodes=("StockCode", "nunique"),
            TotalQuantity=("Quantity", "sum"),
            TotalLineValue=("LineValue", "sum"),
        )
        .reset_index()
        .sort_values("Records", ascending=False)
    )

    audit_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "InvoiceDate",
        "Quantity",
        "UnitPrice",
        "LineValue",
        "CustomerID",
        "TransactionCategory",
        "MatchingConditionCount",
        "MatchingConditions",
        "AuditReasons",
    ]

    audit_df = audit_df[
        [column for column in audit_columns if column in audit_df.columns]
    ]

    return df, audit_df, combination_counts


# ============================================================
# SUMMARY REPORT
# ============================================================

def build_summary(df, audit_df, combination_counts):
    category_counts = (
        df["TransactionCategory"]
        .value_counts(dropna=False)
        .sort_index()
    )

    reason_counts = (
        audit_df.loc[audit_df["AuditReasons"].ne(""), "AuditReasons"]
        .str.split("; ")
        .explode()
        .value_counts()
        .sort_values(ascending=False)
    )

    total_rows = len(df)
    audited_rows = len(audit_df)
    overlap_rows = int((df["MatchingConditionCount"] > 1).sum())

    report_lines = [
        "# Transaction Classification Audit",
        "",
        "## 1. Scope",
        "",
        f"- Processed dataset rows: {total_rows:,}",
        f"- Rows flagged for review: {audited_rows:,}",
        f"- Rows matching multiple classification conditions: {overlap_rows:,}",
        (
            f"- Share of rows flagged: {audited_rows / total_rows * 100:.2f}%"
            if total_rows
            else "- Share of rows flagged: N/A"
        ),
        "",
        "The audit identifies patterns for investigation. It does not "
        "automatically correct categories, remove records, or prove the "
        "definitive commercial meaning of transactions.",
        "",
        "## 2. Existing Category Counts",
        "",
        "| Category | Records |",
        "|---|---:|",
    ]

    for category, count in category_counts.items():
        report_lines.append(f"| {category} | {count:,} |")

    report_lines.extend([
        "",
        "## 3. Review Reasons",
        "",
        "| Reason | Records |",
        "|---|---:|",
    ])

    for reason, count in reason_counts.items():
        report_lines.append(f"| {reason} | {count:,} |")

    report_lines.extend([
        "",
        "## 4. Most Frequent Condition Combinations",
        "",
        "| Matching conditions | Existing category | Records | Distinct invoices |",
        "|---|---|---:|---:|",
    ])

    for _, row in combination_counts.head(20).iterrows():
        report_lines.append(
            f"| {row['MatchingConditions']} "
            f"| {row['TransactionCategory']} "
            f"| {int(row['Records']):,} "
            f"| {int(row['DistinctInvoices']):,} |"
        )

    report_lines.extend([
        "",
        "## 5. Interpretation and Limitations",
        "",
        "- A review flag is not proof of an error.",
        "- A C-prefixed invoice with positive quantity is flagged for "
        "inspection; the prefix alone does not establish commercial meaning.",
        "- Multiple matching conditions may be expected because the current "
        "classification uses an explicit priority order.",
        "- Missing CustomerID limits customer attribution but does not, by "
        "itself, invalidate a sales line.",
        "- Existing transaction categories were not modified.",
        "- The audit does not validate net revenue, refunds, or definitive "
        "order counts.",
        "",
        "## 6. Recommended Next Steps",
        "",
        "- Inspect examples from the most frequent condition combinations.",
        "- Compare flagged invoices with the original Excel source.",
        "- Document evidence before changing classification rules.",
        "- Revalidate metrics after any approved business-rule changes.",
        "",
    ])

    return "\n".join(report_lines)


# ============================================================
# EXECUTION
# ============================================================

def main():
    print("=" * 65)
    print("TRANSACTION CLASSIFICATION AUDIT")
    print("=" * 65)

    df = load_data()
    df, audit_df, combination_counts = audit_classification(df)

    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)

    audit_df.to_csv(
        AUDIT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    combination_counts.to_csv(
        COMBINATIONS_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    summary = build_summary(
        df,
        audit_df,
        combination_counts,
    )

    SUMMARY_FILE.write_text(
        summary,
        encoding="utf-8",
    )

    print(f"Processed dataset rows: {len(df):,}")
    print(f"Rows flagged for review: {len(audit_df):,}")
    print(
        "Rows matching multiple conditions: "
        f"{int((df['MatchingConditionCount'] > 1).sum()):,}"
    )

    print("\nMost frequent condition combinations:")
    if combination_counts.empty:
        print("No overlapping conditions found.")
    else:
        print(
            combination_counts[
                [
                    "MatchingConditions",
                    "TransactionCategory",
                    "Records",
                    "DistinctInvoices",
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

    print("\nGenerated files:")
    print(f"- {AUDIT_FILE}")
    print(f"- {COMBINATIONS_FILE}")
    print(f"- {SUMMARY_FILE}")

    print("\nAudit completed. Existing categories were not changed.")


if __name__ == "__main__":
    main()
