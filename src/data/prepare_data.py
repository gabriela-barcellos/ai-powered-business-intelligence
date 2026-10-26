
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "online_retail_processed.csv"
REPORT_FILE = PROJECT_ROOT / "docs" / "data_quality_summary.md"

REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def classify_transactions(df):
    """
    Classify rows without deleting transactions by category.
    The classification follows an explicit priority order.

    These categories are preliminary and do not establish
    the definitive commercial meaning of each record.
    """

    invoice = df["InvoiceNo"].astype("string").str.strip()

    description = (
        df["Description"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    is_cancellation = invoice.str.upper().str.startswith(
        "C", na=False
    )

    is_bad_debt = description.eq("adjust bad debt").fillna(False)
    is_negative_price = df["UnitPrice"] < 0
    is_negative_quantity = df["Quantity"] < 0
    is_zero_price = df["UnitPrice"] == 0

    # The first matching condition determines the category.
    # This priority is technical, not proof of business meaning.
    conditions = [
        is_cancellation,
        is_bad_debt | is_negative_price,
        is_negative_quantity,
        is_zero_price,
        (df["Quantity"] > 0) & (df["UnitPrice"] > 0),
    ]

    categories = [
        "cancellation_invoice",
        "financial_adjustment_or_negative_price",
        "negative_quantity_review",
        "zero_price_review",
        "standard_sales_candidate",
    ]

    df["TransactionCategory"] = pd.Series(
        "other_review",
        index=df.index,
        dtype="string",
    )

    for condition, category in zip(conditions, categories):
        mask = (
            condition
            & df["TransactionCategory"].eq("other_review")
        )

        df.loc[mask, "TransactionCategory"] = category

    return df


# ============================================================
# PREPARATION VALIDATION
# ============================================================

def validate_preparation(
    df,
    original_rows,
    duplicate_count,
    rows_after_deduplication,
    date_invalid_count,
):
    """Validate structural and arithmetic consistency."""

    category_total = int(
        df["TransactionCategory"].value_counts(dropna=False).sum()
    )

    exact_duplicates_remaining = int(df.duplicated().sum())

    expected_line_value = df["Quantity"] * df["UnitPrice"]

    line_value_matches = bool(
        (
            df["LineValue"].fillna(0)
            - expected_line_value.fillna(0)
        )
        .abs()
        .lt(1e-9)
        .all()
    )

    row_counts_reconcile = (
        original_rows - duplicate_count
        == rows_after_deduplication
    )

    categories_reconcile = category_total == len(df)
    no_exact_duplicates_remain = exact_duplicates_remaining == 0
    dates_valid = date_invalid_count == 0

    checks = {
        "Original and processed row counts reconcile":
            row_counts_reconcile,
        "Category counts reconcile to processed rows":
            categories_reconcile,
        "No exact duplicate rows remain":
            no_exact_duplicates_remain,
        "LineValue matches Quantity x UnitPrice":
            line_value_matches,
        "No invalid invoice dates detected":
            dates_valid,
    }

    return (
        checks,
        exact_duplicates_remaining,
        category_total,
    )


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_data():
    print_section("ONLINE RETAIL — DATA PREPARATION")

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Original file not found: {RAW_FILE}"
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 1. Load the original file.
    df = pd.read_excel(RAW_FILE, engine="openpyxl")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The source file is missing required columns: "
            + ", ".join(missing_columns)
        )

    original_rows = len(df)
    original_columns = len(df.columns)
    original_missing = df.isna().sum()

    print(f"Original rows: {original_rows:,}")
    print(f"Original columns: {original_columns}")

    # 2. Remove only exact duplicate rows.
    duplicate_count = int(df.duplicated().sum())

    df = df.drop_duplicates().copy()

    rows_after_deduplication = len(df)

    print(f"Exact duplicate rows removed: {duplicate_count:,}")
    print(f"Rows after deduplication: {rows_after_deduplication:,}")

    # 3. Classify transactions without deleting categories.
    # Existing classification rules and priority are preserved.
    df = classify_transactions(df)

    # 4. Calculate nominal line value.
    # This is not validated net revenue.
    df["LineValue"] = df["Quantity"] * df["UnitPrice"]

    # 5. Create a time-analysis field.
    parsed_dates = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce",
    )

    df["InvoiceYearMonth"] = (
        parsed_dates.dt.to_period("M").astype("string")
    )

    # 6. Save the processed copy.
    # The original Excel file is not modified.
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    # 7. Calculate data-quality indicators.
    missing_after = df.isna().sum()

    category_counts = (
        df["TransactionCategory"]
        .value_counts(dropna=False)
        .sort_index()
    )

    date_invalid_count = int(parsed_dates.isna().sum())
    negative_quantity_count = int((df["Quantity"] < 0).sum())
    negative_price_count = int((df["UnitPrice"] < 0).sum())
    zero_price_count = int((df["UnitPrice"] == 0).sum())
    missing_customer_count = int(df["CustomerID"].isna().sum())

    (
        checks,
        exact_duplicates_remaining,
        category_total,
    ) = validate_preparation(
        df=df,
        original_rows=original_rows,
        duplicate_count=duplicate_count,
        rows_after_deduplication=rows_after_deduplication,
        date_invalid_count=date_invalid_count,
    )

    overall_validation_passed = all(checks.values())

    # 8. Generate the report in English.
    report_lines = [
        "# Data Quality Summary — Online Retail",
        "",
        "## 1. Files",
        "",
        f"- Original file: `{RAW_FILE.relative_to(PROJECT_ROOT)}`",
        f"- Processed file: `{OUTPUT_FILE.relative_to(PROJECT_ROOT)}`",
        "- The original file was preserved.",
        "",
        "## 2. Record Counts",
        "",
        f"- Original rows: {original_rows:,}",
        f"- Original columns: {original_columns}",
        f"- Exact duplicate rows removed: {duplicate_count:,}",
        f"- Processed rows: {len(df):,}",
        f"- Exact duplicate rows remaining: {exact_duplicates_remaining:,}",
        "",
        "## 3. Missing Values Before Deduplication",
        "",
        "| Column | Missing records |",
        "|---|---:|",
    ]

    for column, count in original_missing.items():
        report_lines.append(f"| {column} | {count:,} |")

    report_lines.extend([
        "",
        "## 4. Missing Values After Deduplication",
        "",
        "| Column | Missing records |",
        "|---|---:|",
    ])

    for column, count in missing_after.items():
        report_lines.append(f"| {column} | {count:,} |")

    report_lines.extend([
        "",
        "## 5. Transaction Classification",
        "",
        "Categories are mutually exclusive and follow a priority "
        "order. Classification is preliminary and does not establish "
        "the definitive commercial meaning of each record.",
        "",
        "| Category | Records |",
        "|---|---:|",
    ])

    for category, count in category_counts.items():
        report_lines.append(f"| {category} | {count:,} |")

    report_lines.extend([
        "",
        "## 6. Additional Data Checks",
        "",
        f"- Invalid invoice dates: {date_invalid_count:,}",
        f"- Negative quantities: {negative_quantity_count:,}",
        f"- Negative unit prices: {negative_price_count:,}",
        f"- Zero unit prices: {zero_price_count:,}",
        f"- Records without CustomerID: {missing_customer_count:,}",
        "",
        "## 7. Preparation Validation",
        "",
        "| Check | Result |",
        "|---|---|",
    ])

    for check_name, passed in checks.items():
        result = "PASS" if passed else "REVIEW"
        report_lines.append(f"| {check_name} | {result} |")

    overall_status = (
        "PASSED"
        if overall_validation_passed
        else "REVIEW REQUIRED"
    )

    report_lines.extend([
        "",
        f"- Overall preparation validation: **{overall_status}**",
        f"- Transaction category records counted: {category_total:,}",
        "",
        "These checks verify structural and arithmetic consistency. "
        "They do not independently validate the business meaning of "
        "the transaction categories or prove that candidate revenue "
        "is net revenue.",
        "",
        "## 8. Definitions and Limitations",
        "",
        "- `LineValue` is `Quantity x UnitPrice`; it is not, by itself, "
        "validated net revenue.",
        "- `standard_sales_candidate` identifies rows with positive "
        "quantity and positive unit price that were not assigned to "
        "a higher-priority category. These are candidates, not "
        "definitively validated sales.",
        "- Invoices beginning with `C` are classified separately "
        "according to the current rule.",
        "- Negative quantities on invoices not beginning with `C` "
        "remain under review.",
        "- Financial adjustments and negative prices are separated "
        "from sales candidates according to the current priority order.",
        "- Zero-price records remain under review.",
        "- Unclassified records remain in `other_review`.",
        "- Rows are not removed solely because of missing values, "
        "zero prices, or negative quantities.",
        "- Net revenue and definitive order counts have not yet "
        "been validated.",
        "- Classification priority is a technical rule and does not, "
        "by itself, confirm the commercial nature of a transaction.",
        "",
        "## 9. Next Validation Steps",
        "",
        "- Audit transaction categories against invoice, quantity, "
        "price, and description patterns.",
        "- Validate the business rules for revenue, orders, and returns.",
        "- Compare samples from the processed CSV with the original Excel file.",
        "- Confirm results before treating the metrics as definitive.",
        "",
    ])

    REPORT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print_section("TRANSACTION CLASSIFICATION")
    print(category_counts.to_string())

    print_section("PREPARATION VALIDATION")

    for check_name, passed in checks.items():
        result = "PASS" if passed else "REVIEW"
        print(f"{result} — {check_name}")

    print(f"Overall preparation validation: {overall_status}")

    print_section("GENERATED FILES")
    print(f"Processed dataset: {OUTPUT_FILE}")
    print(f"Data quality report: {REPORT_FILE}")

    print("\nPreparation completed. Review the report before proceeding.")


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    prepare_data()
