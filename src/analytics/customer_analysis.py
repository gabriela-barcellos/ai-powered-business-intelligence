
from pathlib import Path

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

REVENUE_RANKING_FILE = OUTPUT_DIR / "customer_revenue_ranking.csv"
FREQUENCY_RANKING_FILE = OUTPUT_DIR / "customer_order_frequency_ranking.csv"
QUANTITY_RANKING_FILE = OUTPUT_DIR / "customer_quantity_ranking.csv"
SUMMARY_FILE = OUTPUT_DIR / "customer_analysis_summary.md"


# ============================================================
# PREPARAÇÃO DOS DADOS
# ============================================================

def load_and_prepare_data() -> pd.DataFrame:
    """Carrega os dados processados e seleciona vendas candidatas."""

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
        "Quantity",
        "UnitPrice",
        "LineValue",
        "InvoiceYearMonth",
        "TransactionCategory",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {sorted(missing_columns)}"
        )

    # Seleciona somente as vendas classificadas como candidatas.
    sales = df.loc[
        df["TransactionCategory"].eq("standard_sales_candidate")
    ].copy()

    # Padroniza os identificadores.
    sales["CustomerID"] = sales["CustomerID"].str.strip()
    sales["InvoiceNo"] = sales["InvoiceNo"].astype("string").str.strip()

    # Exclui registros sem identificação de cliente ou pedido.
    sales = sales.loc[
        sales["CustomerID"].notna()
        & sales["CustomerID"].ne("")
        & sales["InvoiceNo"].notna()
        & sales["InvoiceNo"].ne("")
    ].copy()

    # Converte os indicadores numéricos.
    numeric_columns = ["Quantity", "UnitPrice", "LineValue"]

    for column in numeric_columns:
        sales[column] = pd.to_numeric(
            sales[column],
            errors="coerce",
        )

    sales = sales.dropna(subset=numeric_columns)

    # Proteção adicional para considerar apenas vendas positivas.
    sales = sales.loc[
        (sales["Quantity"] > 0)
        & (sales["UnitPrice"] > 0)
    ].copy()

    if sales.empty:
        raise ValueError(
            "Nenhuma venda candidata válida foi encontrada."
        )

    print(f"Linhas de venda válidas: {len(sales):,}")
    print(f"Clientes identificados: {sales['CustomerID'].nunique():,}")

    return sales


# ============================================================
# ANÁLISE DE CLIENTES
# ============================================================

def analyze_customers(
    sales: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Gera indicadores e rankings por cliente."""

    customers = (
        sales.groupby("CustomerID", as_index=False)
        .agg(
            TotalRevenue=("LineValue", "sum"),
            TotalQuantity=("Quantity", "sum"),
            TotalOrders=("InvoiceNo", "nunique"),
            TotalLines=("InvoiceNo", "size"),
            FirstPurchase=("InvoiceDate", "min"),
            LastPurchase=("InvoiceDate", "max"),
        )
    )

    customers["AverageRevenuePerOrder"] = (
        customers["TotalRevenue"] / customers["TotalOrders"]
    )

    customers["AverageItemsPerOrder"] = (
        customers["TotalQuantity"] / customers["TotalOrders"]
    )

    # Ranking por receita.
    revenue_ranking = customers.sort_values(
        ["TotalRevenue", "CustomerID"],
        ascending=[False, True],
    ).reset_index(drop=True)

    revenue_ranking.insert(
        0,
        "RevenueRank",
        range(1, len(revenue_ranking) + 1),
    )

    # Ranking por frequência de pedidos.
    frequency_ranking = customers.sort_values(
        ["TotalOrders", "TotalRevenue", "CustomerID"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    frequency_ranking.insert(
        0,
        "FrequencyRank",
        range(1, len(frequency_ranking) + 1),
    )

    # Ranking por quantidade de itens.
    quantity_ranking = customers.sort_values(
        ["TotalQuantity", "TotalRevenue", "CustomerID"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    quantity_ranking.insert(
        0,
        "QuantityRank",
        range(1, len(quantity_ranking) + 1),
    )

    return {
        "customers": customers,
        "revenue": revenue_ranking,
        "frequency": frequency_ranking,
        "quantity": quantity_ranking,
    }


# ============================================================
# VALIDAÇÃO DOS RESULTADOS
# ============================================================

def validate_results(
    sales: pd.DataFrame,
    results: dict[str, pd.DataFrame],
) -> dict:
    """Compara os totais da base filtrada com os totais agregados."""

    customers = results["customers"]

    base_revenue = sales["LineValue"].sum()
    analyzed_revenue = customers["TotalRevenue"].sum()

    base_quantity = sales["Quantity"].sum()
    analyzed_quantity = customers["TotalQuantity"].sum()

    base_customers = sales["CustomerID"].nunique()
    analyzed_customers = customers["CustomerID"].nunique()

    revenue_difference = analyzed_revenue - base_revenue
    quantity_difference = analyzed_quantity - base_quantity

    return {
        "base_revenue": base_revenue,
        "analyzed_revenue": analyzed_revenue,
        "revenue_difference": revenue_difference,
        "base_quantity": base_quantity,
        "analyzed_quantity": analyzed_quantity,
        "quantity_difference": quantity_difference,
        "base_customers": base_customers,
        "analyzed_customers": analyzed_customers,
        "validation_passed": (
            abs(revenue_difference) < 0.01
            and abs(quantity_difference) < 0.000001
            and base_customers == analyzed_customers
        ),
    }


# ============================================================
# EXPORTAÇÃO DOS RESULTADOS
# ============================================================

def export_results(
    results: dict[str, pd.DataFrame],
    validation: dict,
) -> None:
    """Exporta rankings e relatório em Markdown."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results["revenue"].to_csv(
        REVENUE_RANKING_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    results["frequency"].to_csv(
        FREQUENCY_RANKING_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    results["quantity"].to_csv(
        QUANTITY_RANKING_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    customers = results["customers"]

    top_revenue = results["revenue"].head(10)
    top_frequency = results["frequency"].head(10)
    top_quantity = results["quantity"].head(10)

    total_orders = customers["TotalOrders"].sum()

    average_revenue_per_order = (
        validation["analyzed_revenue"] / total_orders
        if total_orders > 0
        else 0
    )

    report = f"""# Customer Analysis Summary

## Objetivo

Analisar o comportamento de compra dos clientes identificados,
considerando receita, frequência de pedidos e quantidade de itens.

## Escopo e regras

- Fonte: `data/processed/online_retail_processed.csv`
- Categoria considerada: `standard_sales_candidate`
- Clientes e pedidos sem identificação foram excluídos.
- Foram mantidas somente linhas com quantidade e preço unitário positivos.
- A receita utiliza a coluna `LineValue`.
- A frequência considera pedidos distintos por `InvoiceNo`.
- Os indicadores representam receita bruta candidata, não lucro ou receita líquida.

## Indicadores gerais

- Clientes identificados: {validation["analyzed_customers"]:,}
- Receita bruta candidata: £{validation["analyzed_revenue"]:,.2f}
- Quantidade total de itens: {validation["analyzed_quantity"]:,.0f}
- Receita média por cliente: £{customers["TotalRevenue"].mean():,.2f}
- Pedidos médios por cliente: {customers["TotalOrders"].mean():,.2f}
- Receita média por pedido: £{average_revenue_per_order:,.2f}

## Top 10 clientes por receita

{top_revenue[["RevenueRank", "CustomerID", "TotalRevenue", "TotalOrders", "TotalQuantity"]].to_markdown(index=False)}

## Top 10 clientes por frequência de pedidos

{top_frequency[["FrequencyRank", "CustomerID", "TotalOrders", "TotalRevenue", "TotalQuantity"]].to_markdown(index=False)}

## Top 10 clientes por quantidade de itens

{top_quantity[["QuantityRank", "CustomerID", "TotalQuantity", "TotalOrders", "TotalRevenue"]].to_markdown(index=False)}

## Validação dos resultados

- Receita da base filtrada: £{validation["base_revenue"]:,.2f}
- Receita agregada por cliente: £{validation["analyzed_revenue"]:,.2f}
- Diferença de receita: £{validation["revenue_difference"]:,.2f}
- Quantidade da base filtrada: {validation["base_quantity"]:,.0f}
- Quantidade agregada: {validation["analyzed_quantity"]:,.0f}
- Diferença de quantidade: {validation["quantity_difference"]:,.6f}
- Clientes únicos na base filtrada: {validation["base_customers"]:,}
- Clientes únicos no resultado: {validation["analyzed_customers"]:,}
- Status: {"APROVADA" if validation["validation_passed"] else "REVISAR"}

## Limitações

A análise considera somente vendas candidatas com cliente identificado.
Pedidos sem identificação de cliente não entram nos rankings. Os resultados
dependem das regras de classificação adotadas nas etapas anteriores.
"""

    SUMMARY_FILE.write_text(report, encoding="utf-8")

    print("\nARQUIVOS GERADOS")

    for file_path in [
        REVENUE_RANKING_FILE,
        FREQUENCY_RANKING_FILE,
        QUANTITY_RANKING_FILE,
        SUMMARY_FILE,
    ]:
        print(f"- {file_path}")


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main() -> None:
    print("=" * 60)
    print("ANÁLISE DE CLIENTES")
    print("=" * 60)

    sales = load_and_prepare_data()
    results = analyze_customers(sales)
    validation = validate_results(sales, results)

    print("\nINDICADORES GERAIS")
    print(f"Clientes identificados: {validation['analyzed_customers']:,}")
    print(f"Receita bruta candidata: £{validation['analyzed_revenue']:,.2f}")
    print(f"Quantidade de itens: {validation['analyzed_quantity']:,.0f}")

    print("\nTOP 10 CLIENTES POR RECEITA")

    print(
        results["revenue"][
            ["RevenueRank", "CustomerID", "TotalRevenue", "TotalOrders"]
        ].head(10).to_string(index=False)
    )

    print("\nTOP 10 CLIENTES POR FREQUÊNCIA")

    print(
        results["frequency"][
            ["FrequencyRank", "CustomerID", "TotalOrders", "TotalRevenue"]
        ].head(10).to_string(index=False)
    )

    print("\nVALIDAÇÃO")
    print(f"Receita da base: £{validation['base_revenue']:,.2f}")
    print(f"Receita agregada: £{validation['analyzed_revenue']:,.2f}")
    print(f"Diferença de receita: £{validation['revenue_difference']:,.2f}")
    print(f"Diferença de quantidade: {validation['quantity_difference']:,.6f}")

    status = "APROVADA" if validation["validation_passed"] else "REVISAR"
    print(f"Status: {status}")

    if not validation["validation_passed"]:
        raise ValueError(
            "A validação falhou. Confira os totais antes de continuar."
        )

    export_results(results, validation)

    print("\nANÁLISE DE CLIENTES CONCLUÍDA COM SUCESSO!")


if __name__ == "__main__":
    main()
