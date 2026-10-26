
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "online_retail_processed.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

MONTHLY_FILE = OUTPUT_DIR / "customer_retention_monthly.csv"
COHORT_FILE = OUTPUT_DIR / "customer_retention_cohorts.csv"
SUMMARY_FILE = OUTPUT_DIR / "customer_retention_summary.md"


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

def load_data() -> pd.DataFrame:
    """Carrega e prepara as vendas candidatas com cliente identificado."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8",
        low_memory=False,
        dtype={"CustomerID": "string"},
    )

    required_columns = {
        "CustomerID",
        "InvoiceNo",
        "InvoiceDate",
        "Quantity",
        "UnitPrice",
        "LineValue",
        "TransactionCategory",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {sorted(missing_columns)}"
        )

    sales = df.loc[
        df["TransactionCategory"].eq("standard_sales_candidate")
    ].copy()

    sales["CustomerID"] = sales["CustomerID"].str.strip()
    sales["InvoiceNo"] = sales["InvoiceNo"].astype("string").str.strip()

    sales["InvoiceDate"] = pd.to_datetime(
        sales["InvoiceDate"],
        errors="coerce",
    )

    for column in ["Quantity", "UnitPrice", "LineValue"]:
        sales[column] = pd.to_numeric(
            sales[column],
            errors="coerce",
        )

    sales = sales.dropna(
        subset=[
            "CustomerID",
            "InvoiceNo",
            "InvoiceDate",
            "Quantity",
            "UnitPrice",
            "LineValue",
        ]
    )

    sales = sales.loc[
        sales["CustomerID"].ne("")
        & sales["InvoiceNo"].ne("")
        & (sales["Quantity"] > 0)
        & (sales["UnitPrice"] > 0)
    ].copy()

    if sales.empty:
        raise ValueError("Nenhuma venda válida foi encontrada.")

    sales["InvoiceMonth"] = sales["InvoiceDate"].dt.to_period("M")

    print(f"Linhas válidas: {len(sales):,}")
    print(f"Clientes identificados: {sales['CustomerID'].nunique():,}")
    print(
        f"Período: {sales['InvoiceDate'].min():%Y-%m-%d}"
        f" a {sales['InvoiceDate'].max():%Y-%m-%d}"
    )

    return sales


# ============================================================
# ANÁLISE MENSAL
# ============================================================

def analyze_monthly(sales: pd.DataFrame) -> pd.DataFrame:
    """Calcula clientes novos, recorrentes e ativos por mês."""

    # Primeiro mês em que cada cliente aparece na base.
    first_purchase = (
        sales.groupby("CustomerID")["InvoiceMonth"]
        .min()
        .rename("FirstPurchaseMonth")
    )

    sales = sales.join(first_purchase, on="CustomerID")

    sales["IsNewCustomer"] = (
        sales["InvoiceMonth"] == sales["FirstPurchaseMonth"]
    )

    monthly = (
        sales.groupby("InvoiceMonth")
        .agg(
            ActiveCustomers=("CustomerID", "nunique"),
            NewCustomers=("CustomerID", lambda x: 0),
            Revenue=("LineValue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Quantity=("Quantity", "sum"),
        )
        .reset_index()
    )

    # Clientes novos: primeira compra observada naquele mês.
    new_customers = (
        sales.loc[sales["IsNewCustomer"]]
        .groupby("InvoiceMonth")["CustomerID"]
        .nunique()
        .rename("NewCustomers")
    )

    monthly = monthly.drop(columns=["NewCustomers"]).merge(
        new_customers,
        left_on="InvoiceMonth",
        right_index=True,
        how="left",
    )

    monthly["NewCustomers"] = (
        monthly["NewCustomers"].fillna(0).astype(int)
    )

    monthly["ReturningCustomers"] = (
        monthly["ActiveCustomers"] - monthly["NewCustomers"]
    )

    monthly["ReturningCustomerRate"] = (
        monthly["ReturningCustomers"]
        / monthly["ActiveCustomers"]
        * 100
    )

    # Retenção: clientes ativos no mês atual que voltaram
    # a comprar no mês seguinte.
    customer_months = (
        sales[["CustomerID", "InvoiceMonth"]]
        .drop_duplicates()
    )

    month_sets = {
        month: set(group["CustomerID"])
        for month, group in customer_months.groupby("InvoiceMonth")
    }

    monthly["NextMonthRetainedCustomers"] = 0
    monthly["NextMonthRetentionRate"] = float("nan")

    for i in range(len(monthly) - 1):
        current_month = monthly.iloc[i]["InvoiceMonth"]
        next_month = monthly.iloc[i + 1]["InvoiceMonth"]

        # Só compara meses consecutivos do calendário.
        if next_month == current_month + 1:
            current_customers = month_sets[current_month]
            next_customers = month_sets[next_month]

            retained = len(current_customers & next_customers)
            current_active = len(current_customers)

            monthly.loc[i, "NextMonthRetainedCustomers"] = retained
            monthly.loc[i, "NextMonthRetentionRate"] = (
                retained / current_active * 100
                if current_active
                else 0
            )

    monthly["InvoiceMonth"] = monthly["InvoiceMonth"].astype(str)

    monthly = monthly[
        [
            "InvoiceMonth",
            "ActiveCustomers",
            "NewCustomers",
            "ReturningCustomers",
            "ReturningCustomerRate",
            "NextMonthRetainedCustomers",
            "NextMonthRetentionRate",
            "Orders",
            "Quantity",
            "Revenue",
        ]
    ]

    return monthly


# ============================================================
# ANÁLISE DE COORTES
# ============================================================

def analyze_cohorts(sales: pd.DataFrame) -> pd.DataFrame:
    """Calcula a retenção por mês da primeira compra (coorte)."""

    customer_first_month = (
        sales.groupby("CustomerID")["InvoiceMonth"]
        .min()
        .rename("CohortMonth")
    )

    customer_months = (
        sales[["CustomerID", "InvoiceMonth"]]
        .drop_duplicates()
        .join(customer_first_month, on="CustomerID")
    )

    customer_months["CohortAge"] = (
        (
            customer_months["InvoiceMonth"].dt.year
            - customer_months["CohortMonth"].dt.year
        ) * 12
        + customer_months["InvoiceMonth"].dt.month
        - customer_months["CohortMonth"].dt.month
    )

    cohorts = (
        customer_months.groupby(
            ["CohortMonth", "CohortAge"]
        )["CustomerID"]
        .nunique()
        .reset_index(name="ActiveCustomers")
    )

    cohort_sizes = (
        cohorts.loc[cohorts["CohortAge"] == 0]
        .set_index("CohortMonth")["ActiveCustomers"]
        .rename("CohortSize")
    )

    cohorts = cohorts.join(cohort_sizes, on="CohortMonth")

    cohorts["RetentionRate"] = (
        cohorts["ActiveCustomers"]
        / cohorts["CohortSize"]
        * 100
    )

    cohorts["CohortMonth"] = cohorts["CohortMonth"].astype(str)

    return cohorts[
        [
            "CohortMonth",
            "CohortAge",
            "CohortSize",
            "ActiveCustomers",
            "RetentionRate",
        ]
    ].sort_values(
        ["CohortMonth", "CohortAge"]
    ).reset_index(drop=True)


# ============================================================
# VALIDAÇÕES
# ============================================================

def validate_results(
    sales: pd.DataFrame,
    monthly: pd.DataFrame,
) -> dict:
    """Confere totais, categorias de clientes e taxa de retenção."""

    total_active_customer_months = monthly["ActiveCustomers"].sum()
    total_unique_customers = sales["CustomerID"].nunique()

    total_revenue_base = sales["LineValue"].sum()
    total_revenue_monthly = monthly["Revenue"].sum()

    total_quantity_base = sales["Quantity"].sum()
    total_quantity_monthly = monthly["Quantity"].sum()

    # Validação: novos + recorrentes = ativos.
    category_counts_valid = (
        (
            monthly["NewCustomers"]
            + monthly["ReturningCustomers"]
        )
        == monthly["ActiveCustomers"]
    ).all()

    # Nova validação: recalcula a taxa de retenção de forma independente
    # usando os números já exportados na tabela mensal.
    has_retention_rate = monthly["NextMonthRetentionRate"].notna()

    expected_retention_rate = (
        monthly["NextMonthRetainedCustomers"]
        / monthly["ActiveCustomers"].replace(0, np.nan)
        * 100
    )

    retention_rates_valid = np.isclose(
        monthly.loc[
            has_retention_rate, "NextMonthRetentionRate"
        ].to_numpy(dtype=float),
        expected_retention_rate.loc[has_retention_rate].to_numpy(
            dtype=float
        ),
        rtol=0,
        atol=0.000001,
    ).all()

    # Quando a taxa não existe, não deve haver uma taxa numérica
    # para validar. Isso é esperado no último mês sem mês seguinte.
    retention_missing_values_valid = (
        monthly.loc[
            ~has_retention_rate, "NextMonthRetentionRate"
        ].isna()
    ).all()

    retention_validation_passed = bool(
        retention_rates_valid and retention_missing_values_valid
    )

    validation_passed = bool(
        abs(total_revenue_monthly - total_revenue_base) < 0.01
        and abs(total_quantity_monthly - total_quantity_base) < 0.000001
        and category_counts_valid
        and retention_validation_passed
    )

    return {
        "total_unique_customers": total_unique_customers,
        "total_active_customer_months": total_active_customer_months,
        "total_revenue_base": total_revenue_base,
        "total_revenue_monthly": total_revenue_monthly,
        "revenue_difference": total_revenue_monthly - total_revenue_base,
        "total_quantity_base": total_quantity_base,
        "total_quantity_monthly": total_quantity_monthly,
        "quantity_difference": total_quantity_monthly - total_quantity_base,
        "customer_counts_valid": bool(category_counts_valid),
        "retention_rates_valid": bool(retention_rates_valid),
        "retention_missing_values_valid": bool(
            retention_missing_values_valid
        ),
        "retention_validation_passed": retention_validation_passed,
        "validation_passed": validation_passed,
    }


# ============================================================
# EXPORTAÇÃO
# ============================================================

def export_results(
    monthly: pd.DataFrame,
    cohorts: pd.DataFrame,
    validation: dict,
) -> None:
    """Salva as análises em CSV e gera relatório Markdown."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    monthly.to_csv(
        MONTHLY_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    cohorts.to_csv(
        COHORT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    monthly_table = monthly.to_string(index=False)
    cohort_preview = cohorts.head(20).to_string(index=False)

    report = f"""# Customer Retention & Behavior Analysis

## Objetivo

Analisar a evolução mensal dos clientes, distinguindo clientes novos e
recorrentes, além de medir a retenção entre meses e por coorte.

## Regras de análise

- Considera somente vendas classificadas como `standard_sales_candidate`.
- Exclui registros sem identificação de cliente, pedido ou data válida.
- Considera quantidade e preço unitário positivos.
- Cliente novo é aquele cuja primeira compra observada na base ocorreu naquele mês.
- Cliente recorrente já havia comprado em um mês anterior da base.
- Retenção mensal considera clientes ativos em um mês que voltaram no mês seguinte.
- A análise de coortes usa o mês da primeira compra observada como referência.

## Validações

- Clientes únicos: {validation["total_unique_customers"]:,}
- Soma de clientes ativos por mês (cliente-mês): {validation["total_active_customer_months"]:,}
- Receita da base: £{validation["total_revenue_base"]:,.2f}
- Receita mensal agregada: £{validation["total_revenue_monthly"]:,.2f}
- Diferença de receita: £{validation["revenue_difference"]:,.2f}
- Quantidade da base: {validation["total_quantity_base"]:,.0f}
- Quantidade mensal agregada: {validation["total_quantity_monthly"]:,.0f}
- Diferença de quantidade: {validation["quantity_difference"]:,.6f}
- Novos + recorrentes = ativos em todos os meses: {validation["customer_counts_valid"]}
- Taxas de retenção conferem com a fórmula: {validation["retention_rates_valid"]}
- Valores ausentes de retenção são válidos: {validation["retention_missing_values_valid"]}
- Validação de retenção aprovada: {validation["retention_validation_passed"]}
- Status geral: {"APROVADA" if validation["validation_passed"] else "REVISAR"}

## Indicadores mensais

```text
{monthly_table}
```

## Primeiras 20 linhas da análise de coortes

```text
{cohort_preview}
```

## Limitações

A primeira compra representa a primeira ocorrência do cliente dentro do período
disponível na base, não necessariamente sua primeira compra real na empresa.

O último mês disponível não possui um mês seguinte completo para calcular
retenção. Além disso, clientes ativos em meses diferentes podem se repetir;
por isso, a soma de clientes ativos por mês não representa clientes únicos
no período inteiro.
"""

    SUMMARY_FILE.write_text(report, encoding="utf-8")

    print("\nARQUIVOS GERADOS")
    print(f"- {MONTHLY_FILE}")
    print(f"- {COHORT_FILE}")
    print(f"- {SUMMARY_FILE}")


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main() -> None:
    print("=" * 60)
    print("CUSTOMER RETENTION & BEHAVIOR ANALYSIS")
    print("=" * 60)

    sales = load_data()

    monthly = analyze_monthly(sales)
    cohorts = analyze_cohorts(sales)

    validation = validate_results(sales, monthly)

    print("\nRESUMO MENSAL")
    print(monthly.to_string(index=False))

    print("\nVALIDAÇÃO")
    print(f"Clientes únicos: {validation['total_unique_customers']:,}")
    print(
        f"Diferença de receita: "
        f"£{validation['revenue_difference']:,.2f}"
    )
    print(
        f"Diferença de quantidade: "
        f"{validation['quantity_difference']:,.6f}"
    )
    print(
        "Novos + recorrentes = ativos:",
        validation["customer_counts_valid"],
    )
    print(
        "Taxas de retenção conferem:",
        validation["retention_rates_valid"],
    )
    print(
        "Último mês sem taxa tratado corretamente:",
        validation["retention_missing_values_valid"],
    )
    print(
        "Validação de retenção:",
        "APROVADA"
        if validation["retention_validation_passed"]
        else "REVISAR",
    )
    print(
        "Status geral:",
        "APROVADA" if validation["validation_passed"] else "REVISAR",
    )

    if not validation["validation_passed"]:
        raise ValueError(
            "A validação falhou. Confira os resultados antes de continuar."
        )

    export_results(monthly, cohorts, validation)

    print("\nANÁLISE DE RETENÇÃO CONCLUÍDA COM SUCESSO!")


if __name__ == "__main__":
    main()
