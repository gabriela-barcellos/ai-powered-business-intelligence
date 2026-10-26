
from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURAÇÃO DOS CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "online_retail_processed.csv"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Novos arquivos: preservamos os rankings preliminares anteriores.
REVENUE_FILE = (
    PROCESSED_DIR / "product_revenue_ranking_classified.csv"
)
QUANTITY_FILE = (
    PROCESSED_DIR / "product_quantity_ranking_classified.csv"
)
CLASSIFICATION_FILE = (
    PROCESSED_DIR / "product_classification_summary.csv"
)
SUMMARY_FILE = (
    PROCESSED_DIR / "product_classification_report.md"
)


# ============================================================
# 2. REGRAS DE CLASSIFICAÇÃO
# ============================================================

# Códigos conhecidos que exigem uma classificação específica.
POSTAGE_CODES = {"DOT", "POST"}

MANUAL_CODES = {"M"}

# Descrições indicativas de serviços de postagem.
POSTAGE_DESCRIPTIONS = {
    "DOTCOM POSTAGE",
    "POSTAGE",
    "CARRIAGE",
}

# Descrições que exigem revisão, pois podem representar
# ajustes, taxas ou outros lançamentos não comerciais.
REVIEW_DESCRIPTIONS = {
    "MANUAL",
    "BANK CHARGES",
    "AMAZON FEE",
    "CRUK COMMISSION",
    "ADJUST BAD DEBT",
    "POSTAGE CHARGE",
    "SAMPLES",
    "PADS",
}


# ============================================================
# 3. CARREGAMENTO DOS DADOS
# ============================================================

def load_data():
    """Carrega a base processada e valida as colunas necessárias."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Base processada não encontrada: {DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig",
        dtype={"StockCode": "string"},
    )

    required_columns = [
        "StockCode",
        "Description",
        "Quantity",
        "UnitPrice",
        "LineValue",
        "TransactionCategory",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {missing_columns}"
        )

    print(f"Base carregada: {len(df):,} linhas")

    return df


# ============================================================
# 4. SELEÇÃO DAS VENDAS CANDIDATAS
# ============================================================

def prepare_product_data(df):
    """
    Seleciona as vendas candidatas e prepara os campos.

    Registros com problemas são contabilizados e documentados.
    A base original e a base processada não são modificadas.
    """

    products = df.loc[
        df["TransactionCategory"] == "standard_sales_candidate"
    ].copy()

    for column in ["Quantity", "UnitPrice", "LineValue"]:
        products[column] = pd.to_numeric(
            products[column],
            errors="coerce",
        )

    products["StockCode"] = (
        products["StockCode"]
        .astype("string")
        .str.strip()
    )

    products["Description"] = (
        products["Description"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Para esta análise, uma linha precisa ter código e métricas
    # válidas. A exclusão é apenas desta análise derivada.
    valid_mask = (
        products["StockCode"].notna()
        & products["StockCode"].ne("")
        & products["Quantity"].gt(0)
        & products["UnitPrice"].gt(0)
        & products["LineValue"].notna()
    )

    excluded_rows = int((~valid_mask).sum())
    products = products.loc[valid_mask].copy()

    products["Description"] = products["Description"].replace(
        "",
        "DESCRIÇÃO NÃO INFORMADA",
    )

    print("\n" + "=" * 65)
    print("PREPARAÇÃO DOS DADOS")
    print("=" * 65)
    print(f"Linhas candidatas na base: {int((df['TransactionCategory'] == 'standard_sales_candidate').sum()):,}")
    print(f"Linhas consideradas: {len(products):,}")
    print(f"Linhas excluídas desta análise: {excluded_rows:,}")
    print(f"Códigos de produto identificados: {products['StockCode'].nunique():,}")

    return products, excluded_rows


# ============================================================
# 5. CLASSIFICAÇÃO DOS CÓDIGOS
# ============================================================

def classify_product(row):
    """
    Classifica cada linha com base em regras explícitas.

    A classificação é indicativa e pode exigir revisão humana.
    Não representa uma confirmação contábil ou comercial.
    """

    code = str(row["StockCode"]).strip().upper()
    description = str(row["Description"]).strip().upper()

    if (
        code in POSTAGE_CODES
        or description in POSTAGE_DESCRIPTIONS
        or "POSTAGE" in description
    ):
        return "service_postage"

    if (
        code in MANUAL_CODES
        or description in REVIEW_DESCRIPTIONS
        or "ADJUST BAD DEBT" in description
        or "BANK CHARGES" in description
        or "COMMISSION" in description
        or "AMAZON FEE" in description
    ):
        return "special_item_review"

    # Mantemos estes registros como candidatos a mercadoria.
    # Isso não garante que sejam produtos comerciais.
    return "merchandise_candidate"


def classify_products(products):
    """Aplica as regras e apresenta a distribuição das categorias."""

    classified = products.copy()

    classified["ProductClassification"] = classified.apply(
        classify_product,
        axis=1,
    )

    print("\n" + "=" * 65)
    print("CLASSIFICAÇÃO DOS PRODUTOS")
    print("=" * 65)

    classification_counts = (
        classified.groupby("ProductClassification")
        .agg(
            TransactionLines=("StockCode", "size"),
            DistinctCodes=("StockCode", "nunique"),
            Revenue=("LineValue", "sum"),
            Quantity=("Quantity", "sum"),
        )
        .sort_values("Revenue", ascending=False)
    )

    print(classification_counts.to_string())

    classification_counts.to_csv(
        CLASSIFICATION_FILE,
        encoding="utf-8-sig",
    )

    print(
        "\nResumo da classificação salvo em: "
        f"{CLASSIFICATION_FILE}"
    )

    return classified, classification_counts


# ============================================================
# 6. AGREGAÇÃO POR PRODUTO
# ============================================================

def aggregate_products(products):
    """
    Agrega por código e classificação.

    Se um código aparecer em mais de uma categoria, ele será
    mantido separado por categoria para preservar a rastreabilidade.
    """

    product_summary = (
        products.groupby(
            ["StockCode", "ProductClassification"],
            as_index=False,
        )
        .agg(
            Description=(
                "Description",
                lambda values: (
                    values.mode().iloc[0]
                    if not values.mode().empty
                    else "DESCRIÇÃO NÃO INFORMADA"
                ),
            ),
            Revenue=("LineValue", "sum"),
            Quantity=("Quantity", "sum"),
            TransactionLines=("StockCode", "size"),
            AverageUnitPrice=("UnitPrice", "mean"),
        )
    )

    return product_summary


# ============================================================
# 7. RANKINGS
# ============================================================

def create_rankings(product_summary):
    """
    Gera rankings gerais e rankings de candidatos a mercadoria.

    Os rankings gerais incluem todas as categorias.
    Os rankings de mercadorias excluem postagem e itens em revisão.
    """

    all_products = product_summary.copy()

    merchandise = product_summary.loc[
        product_summary["ProductClassification"]
        == "merchandise_candidate"
    ].copy()

    revenue_all = (
        all_products.sort_values(
            ["Revenue", "StockCode"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )
    revenue_all.insert(
        0,
        "RevenueRank",
        range(1, len(revenue_all) + 1),
    )

    quantity_all = (
        all_products.sort_values(
            ["Quantity", "StockCode"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )
    quantity_all.insert(
        0,
        "QuantityRank",
        range(1, len(quantity_all) + 1),
    )

    # Rankings separados para candidatos a mercadoria.
    revenue_merchandise = (
        merchandise.sort_values(
            ["Revenue", "StockCode"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )
    revenue_merchandise.insert(
        0,
        "RevenueRank",
        range(1, len(revenue_merchandise) + 1),
    )

    quantity_merchandise = (
        merchandise.sort_values(
            ["Quantity", "StockCode"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )
    quantity_merchandise.insert(
        0,
        "QuantityRank",
        range(1, len(quantity_merchandise) + 1),
    )

    # Os arquivos principais agora representam rankings
    # de candidatos a mercadoria, mais adequados à análise comercial.
    revenue_merchandise.to_csv(
        REVENUE_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    quantity_merchandise.to_csv(
        QUANTITY_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n" + "=" * 65)
    print("TOP 10 CANDIDATOS A MERCADORIA POR RECEITA")
    print("=" * 65)

    print(
        revenue_merchandise[
            [
                "RevenueRank",
                "StockCode",
                "Description",
                "Revenue",
                "Quantity",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\n" + "=" * 65)
    print("TOP 10 CANDIDATOS A MERCADORIA POR QUANTIDADE")
    print("=" * 65)

    print(
        quantity_merchandise[
            [
                "QuantityRank",
                "StockCode",
                "Description",
                "Quantity",
                "Revenue",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print(f"\nRanking por receita salvo em: {REVENUE_FILE}")
    print(f"Ranking por quantidade salvo em: {QUANTITY_FILE}")

    return (
        all_products,
        revenue_all,
        quantity_all,
        revenue_merchandise,
        quantity_merchandise,
    )


# ============================================================
# 8. VALIDAÇÃO DOS TOTAIS
# ============================================================

def validate_results(products, product_summary):
    """Confere se a agregação preserva receita e quantidade."""

    source_revenue = products["LineValue"].sum()
    aggregated_revenue = product_summary["Revenue"].sum()

    source_quantity = products["Quantity"].sum()
    aggregated_quantity = product_summary["Quantity"].sum()

    revenue_difference = aggregated_revenue - source_revenue
    quantity_difference = aggregated_quantity - source_quantity

    revenue_ok = abs(revenue_difference) < 0.01
    quantity_ok = abs(quantity_difference) < 1e-9

    print("\n" + "=" * 65)
    print("VALIDAÇÃO DOS TOTAIS")
    print("=" * 65)

    print(f"Receita de origem: £{source_revenue:,.2f}")
    print(f"Receita agregada: £{aggregated_revenue:,.2f}")
    print(f"Diferença de receita: £{revenue_difference:,.2f}")
    print(f"Quantidade de origem: {source_quantity:,.0f}")
    print(f"Quantidade agregada: {aggregated_quantity:,.0f}")
    print(f"Diferença de quantidade: {quantity_difference:,.0f}")

    if revenue_ok and quantity_ok:
        print("\nValidação aprovada: os totais foram preservados.")
    else:
        print(
            "\nATENÇÃO: os totais não foram preservados. "
            "Investigue antes de usar os rankings."
        )

    return {
        "source_revenue": source_revenue,
        "aggregated_revenue": aggregated_revenue,
        "revenue_difference": revenue_difference,
        "source_quantity": source_quantity,
        "aggregated_quantity": aggregated_quantity,
        "quantity_difference": quantity_difference,
        "passed": revenue_ok and quantity_ok,
    }


# ============================================================
# 9. RELATÓRIO DA CLASSIFICAÇÃO
# ============================================================

def create_report(
    products,
    product_summary,
    classification_counts,
    validation,
    excluded_rows,
    revenue_merchandise,
    quantity_merchandise,
):
    """Documenta as regras, os resultados e as limitações."""

    total_revenue = products["LineValue"].sum()
    total_quantity = products["Quantity"].sum()

    merchandise = products.loc[
        products["ProductClassification"]
        == "merchandise_candidate"
    ]

    postage = products.loc[
        products["ProductClassification"] == "service_postage"
    ]

    review = products.loc[
        products["ProductClassification"] == "special_item_review"
    ]

    report = f"""# Classificação e Análise de Produtos

## Objetivo

Separar candidatos a mercadoria de serviços de postagem e
itens que precisam de revisão, mantendo a rastreabilidade dos dados.

## Escopo da análise

- Linhas selecionadas como vendas candidatas: {len(products) + excluded_rows:,}
- Linhas consideradas nesta análise: {len(products):,}
- Linhas excluídas por dados inválidos: {excluded_rows:,}
- Códigos de produto distintos: {products['StockCode'].nunique():,}

## Totais de origem considerados

- Receita candidata: £{total_revenue:,.2f}
- Quantidade candidata: {total_quantity:,.0f}

## Categorias

- Candidatos a mercadoria: {len(merchandise):,} linhas
- Serviços de postagem: {len(postage):,} linhas
- Itens especiais para revisão: {len(review):,} linhas

## Regras de classificação

1. `service_postage`: códigos DOT e POST, descrições conhecidas de postagem ou descrições contendo POSTAGE.
2. `special_item_review`: código M e descrições conhecidas de taxas, comissões, ajustes ou itens que precisam de revisão.
3. `merchandise_candidate`: demais registros, mantidos como candidatos a mercadoria.

## Principais resultados

### Maior receita entre candidatos a mercadoria

{revenue_merchandise.iloc[0]['StockCode']} — {revenue_merchandise.iloc[0]['Description']}

Receita candidata: £{revenue_merchandise.iloc[0]['Revenue']:,.2f}

### Maior quantidade entre candidatos a mercadoria

{quantity_merchandise.iloc[0]['StockCode']} — {quantity_merchandise.iloc[0]['Description']}

Quantidade candidata: {quantity_merchandise.iloc[0]['Quantity']:,.0f}

## Validação

- Diferença de receita após agregação: £{validation['revenue_difference']:,.2f}
- Diferença de quantidade após agregação: {validation['quantity_difference']:,.0f}
- Totais preservados: {"Sim" if validation['passed'] else "Não"}

## Limitações

- A classificação é baseada em regras explícitas e não substitui a validação de negócio.
- Os códigos M, DOT e POST foram tratados por regras específicas que devem ser revisadas.
- A categoria `merchandise_candidate` não garante que cada registro seja uma mercadoria comercial.
- Os rankings são preliminares e não devem ser tratados como indicadores oficiais sem validação adicional.
- A base original e a base processada não são alteradas por este script.
"""

    SUMMARY_FILE.write_text(
        report,
        encoding="utf-8",
    )

    print(f"\nRelatório salvo em: {SUMMARY_FILE}")


# ============================================================
# 10. EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    """Executa a classificação e a análise dos produtos."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_data()

    products, excluded_rows = prepare_product_data(df)

    classified, classification_counts = classify_products(products)

    product_summary = aggregate_products(classified)

    (
        all_products,
        revenue_all,
        quantity_all,
        revenue_merchandise,
        quantity_merchandise,
    ) = create_rankings(product_summary)

    validation = validate_results(
        classified,
        product_summary,
    )

    create_report(
        classified,
        product_summary,
        classification_counts,
        validation,
        excluded_rows,
        revenue_merchandise,
        quantity_merchandise,
    )

    print("\n" + "=" * 65)
    print("CLASSIFICAÇÃO E ANÁLISE DE PRODUTOS CONCLUÍDAS")
    print("=" * 65)

    print("Os rankings gerais foram calculados para auditoria.")
    print("Os arquivos principais contêm candidatos a mercadoria.")
    print("Revise as regras de classificação antes de divulgar conclusões.")


if __name__ == "__main__":
    main()
