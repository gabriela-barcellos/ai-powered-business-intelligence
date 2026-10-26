
from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURAÇÃO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "online_retail_processed.csv"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DETAIL_FILE = (
    PROCESSED_DIR / "product_classification_audit.csv"
)

OVERLAP_FILE = (
    PROCESSED_DIR / "product_classification_overlaps.csv"
)

SUMMARY_FILE = (
    PROCESSED_DIR / "product_classification_audit_summary.md"
)


# ============================================================
# 2. CARREGAMENTO E PREPARAÇÃO
# ============================================================

def load_data():
    """Carrega a base processada e verifica as colunas."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Base processada não encontrada: {DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig",
        dtype={"StockCode": "string"},
    )

    required = [
        "StockCode",
        "Description",
        "Quantity",
        "UnitPrice",
        "LineValue",
        "TransactionCategory",
    ]

    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Colunas ausentes: {missing}")

    print(f"Base carregada: {len(df):,} linhas")

    return df


def prepare_data(df):
    """Seleciona as vendas candidatas e aplica as regras atuais."""

    data = df.loc[
        df["TransactionCategory"] == "standard_sales_candidate"
    ].copy()

    for column in ["Quantity", "UnitPrice", "LineValue"]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data["StockCode"] = (
        data["StockCode"].astype("string").str.strip()
    )

    data["Description"] = (
        data["Description"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    valid = (
        data["StockCode"].notna()
        & data["StockCode"].ne("")
        & data["Quantity"].gt(0)
        & data["UnitPrice"].gt(0)
        & data["LineValue"].notna()
    )

    excluded = int((~valid).sum())
    data = data.loc[valid].copy()

    data["Description"] = data["Description"].replace(
        "",
        "DESCRIÇÃO NÃO INFORMADA",
    )

    return data, excluded


# ============================================================
# 3. REGRAS DE CLASSIFICAÇÃO
# ============================================================

POSTAGE_CODES = {"DOT", "POST"}
MANUAL_CODES = {"M"}

POSTAGE_DESCRIPTIONS = {
    "DOTCOM POSTAGE",
    "POSTAGE",
    "CARRIAGE",
}

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


def classify_product(row):
    """Reproduz as regras atuais para permitir a auditoria."""

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

    return "merchandise_candidate"


# ============================================================
# 4. AUDITORIA POR CÓDIGO E DESCRIÇÃO
# ============================================================

def build_product_audit(data):
    """Resume os códigos, descrições e categorias observadas."""

    data = data.copy()

    data["ProductClassification"] = data.apply(
        classify_product,
        axis=1,
    )

    audit = (
        data.groupby(
            ["StockCode", "Description", "ProductClassification"],
            as_index=False,
            dropna=False,
        )
        .agg(
            TransactionLines=("StockCode", "size"),
            Revenue=("LineValue", "sum"),
            Quantity=("Quantity", "sum"),
            MinUnitPrice=("UnitPrice", "min"),
            MaxUnitPrice=("UnitPrice", "max"),
        )
        .sort_values(
            ["ProductClassification", "StockCode", "Description"]
        )
        .reset_index(drop=True)
    )

    audit.to_csv(
        DETAIL_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    return data, audit


# ============================================================
# 5. CÓDIGOS PRESENTES EM MAIS DE UMA CATEGORIA
# ============================================================

def find_category_overlaps(audit):
    """Identifica códigos associados a múltiplas categorias."""

    category_counts = (
        audit.groupby("StockCode")["ProductClassification"]
        .nunique()
        .rename("CategoryCount")
    )

    overlapping_codes = category_counts.loc[
        category_counts > 1
    ].index

    overlaps = audit.loc[
        audit["StockCode"].isin(overlapping_codes)
    ].copy()

    overlaps.to_csv(
        OVERLAP_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    return overlaps


# ============================================================
# 6. RESUMO DAS CATEGORIAS E VALIDAÇÃO
# ============================================================

def summarize_and_validate(data, audit, excluded):
    """Confere totais e cria um resumo auditável."""

    category_summary = (
        data.groupby("ProductClassification")
        .agg(
            TransactionLines=("StockCode", "size"),
            DistinctCodes=("StockCode", "nunique"),
            Revenue=("LineValue", "sum"),
            Quantity=("Quantity", "sum"),
        )
        .sort_values("Revenue", ascending=False)
    )

    source_revenue = data["LineValue"].sum()
    audit_revenue = audit["Revenue"].sum()

    source_quantity = data["Quantity"].sum()
    audit_quantity = audit["Quantity"].sum()

    revenue_difference = audit_revenue - source_revenue
    quantity_difference = audit_quantity - source_quantity

    revenue_ok = abs(revenue_difference) < 0.01
    quantity_ok = abs(quantity_difference) < 1e-9

    print("\n" + "=" * 65)
    print("DISTRIBUIÇÃO POR CATEGORIA")
    print("=" * 65)
    print(category_summary.to_string())

    print("\n" + "=" * 65)
    print("VALIDAÇÃO DA AUDITORIA")
    print("=" * 65)
    print(f"Linhas consideradas: {len(data):,}")
    print(f"Linhas excluídas desta análise: {excluded:,}")
    print(f"Receita da base: £{source_revenue:,.2f}")
    print(f"Receita auditada: £{audit_revenue:,.2f}")
    print(f"Diferença de receita: £{revenue_difference:,.2f}")
    print(f"Quantidade da base: {source_quantity:,.0f}")
    print(f"Quantidade auditada: {audit_quantity:,.0f}")
    print(f"Diferença de quantidade: {quantity_difference:,.0f}")

    print(
        "\nValidação: "
        + ("APROVADA" if revenue_ok and quantity_ok else "REPROVADA")
    )

    return category_summary, {
        "source_revenue": source_revenue,
        "audit_revenue": audit_revenue,
        "revenue_difference": revenue_difference,
        "source_quantity": source_quantity,
        "audit_quantity": audit_quantity,
        "quantity_difference": quantity_difference,
        "passed": revenue_ok and quantity_ok,
    }


# ============================================================
# 7. RELATÓRIO
# ============================================================

def create_report(data, audit, overlaps, summary, validation, excluded):
    """Gera um relatório com os resultados da auditoria."""

    category_rows = []

    for category, row in summary.iterrows():
        category_rows.append(
            f"| {category} | {int(row['TransactionLines']):,} "
            f"| {int(row['DistinctCodes']):,} "
            f"| £{row['Revenue']:,.2f} "
            f"| {row['Quantity']:,.0f} |"
        )

    category_table = "\n".join(category_rows)

    report = f"""# Auditoria da Classificação de Produtos

## Escopo

- Linhas consideradas: {len(data):,}
- Linhas excluídas desta análise: {excluded:,}
- Combinações de código, descrição e categoria: {len(audit):,}
- Códigos presentes em mais de uma categoria: {overlaps['StockCode'].nunique():,}

## Distribuição por categoria

| Categoria | Linhas | Códigos distintos | Receita | Quantidade |
|---|---:|---:|---:|---:|
{category_table}

## Validação dos totais

- Receita original da seleção: £{validation['source_revenue']:,.2f}
- Receita auditada: £{validation['audit_revenue']:,.2f}
- Diferença de receita: £{validation['revenue_difference']:,.2f}
- Quantidade original da seleção: {validation['source_quantity']:,.0f}
- Quantidade auditada: {validation['audit_quantity']:,.0f}
- Diferença de quantidade: {validation['quantity_difference']:,.0f}
- Totais preservados: {"Sim" if validation['passed'] else "Não"}

## Interpretação

Esta auditoria reproduz as regras atuais de classificação.
Ela identifica códigos que aparecem em mais de uma categoria e
preserva a receita e a quantidade na agregação.

A presença de um código em mais de uma categoria não significa
automaticamente que a classificação esteja errada: descrições
diferentes podem exigir revisão. Os resultados devem ser analisados
antes de alterar qualquer regra de negócio.

## Arquivos gerados

- `product_classification_audit.csv`: detalhe por código, descrição e categoria.
- `product_classification_overlaps.csv`: códigos presentes em múltiplas categorias.
"""

    SUMMARY_FILE.write_text(
        report,
        encoding="utf-8",
    )

    print(f"\nDetalhamento salvo em: {DETAIL_FILE}")
    print(f"Códigos sobrepostos salvos em: {OVERLAP_FILE}")
    print(f"Relatório salvo em: {SUMMARY_FILE}")


# ============================================================
# 8. EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    """Executa a auditoria da classificação."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_data()

    data, excluded = prepare_data(df)

    classified, audit = build_product_audit(data)

    overlaps = find_category_overlaps(audit)

    print("\n" + "=" * 65)
    print("CÓDIGOS EM MAIS DE UMA CATEGORIA")
    print("=" * 65)

    if overlaps.empty:
        print("Nenhum código foi encontrado em múltiplas categorias.")
    else:
        print(
            overlaps[
                [
                    "StockCode",
                    "Description",
                    "ProductClassification",
                    "TransactionLines",
                    "Revenue",
                ]
            ].to_string(index=False)
        )

    summary, validation = summarize_and_validate(
        classified,
        audit,
        excluded,
    )

    create_report(
        classified,
        audit,
        overlaps,
        summary,
        validation,
        excluded,
    )

    print("\n" + "=" * 65)
    print("AUDITORIA CONCLUÍDA")
    print("=" * 65)


if __name__ == "__main__":
    main()
