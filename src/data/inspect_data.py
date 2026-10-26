
from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"


# ============================================================
# ETAPA 1 — INSPEÇÃO INICIAL DOS DADOS
# ============================================================

def inspect_data():
    print("=" * 60)
    print("INSPEÇÃO INICIAL — ONLINE RETAIL")
    print("=" * 60)

    if not FILE_PATH.exists():
        print(f"ERRO: arquivo não encontrado:\n{FILE_PATH}")
        return None

    df = pd.read_excel(FILE_PATH, engine="openpyxl")

    print(f"\nArquivo: {FILE_PATH.name}")
    print(f"Quantidade de linhas: {df.shape[0]:,}")
    print(f"Quantidade de colunas: {df.shape[1]}")

    print("\n--- COLUNAS ---")
    print(df.columns.tolist())

    print("\n--- TIPOS DE DADOS ---")
    print(df.dtypes.to_string())

    print("\n--- VALORES AUSENTES ---")
    missing = df.isna().sum()
    print(missing[missing > 0].to_string() or "Nenhum valor ausente.")

    print("\n--- REGISTROS DUPLICADOS ---")
    print(
        "Linhas duplicadas além da primeira: "
        f"{df.duplicated().sum():,}"
    )

    print("\n--- ESTATÍSTICAS DESCRITIVAS ---")
    print(df.describe().to_string())

    print("\n--- PERÍODO DAS TRANSAÇÕES ---")
    dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    print(f"Data mínima: {dates.min()}")
    print(f"Data máxima: {dates.max()}")
    print(f"Datas inválidas: {dates.isna().sum():,}")

    print("\n--- QUANTIDADES E PREÇOS ---")
    print(f"Quantidade negativa: {(df['Quantity'] < 0).sum():,}")
    print(f"Preço unitário negativo: {(df['UnitPrice'] < 0).sum():,}")
    print(f"Preço unitário igual a zero: {(df['UnitPrice'] == 0).sum():,}")

    print("\n--- AMOSTRA DOS DADOS ---")
    print(df.head(5).to_string(index=False))

    return df


# ============================================================
# ETAPA 2 — INVESTIGAÇÃO DE CANCELAMENTOS
# ============================================================

def inspect_cancellations(df):
    invoice_text = df["InvoiceNo"].astype("string").str.strip()

    is_cancellation = invoice_text.str.upper().str.startswith(
        "C", na=False
    )
    negative_quantity = df["Quantity"] < 0
    negative_price = df["UnitPrice"] < 0

    print("\n" + "=" * 60)
    print("INVESTIGAÇÃO DE CANCELAMENTOS")
    print("=" * 60)

    print(f"Faturas iniciadas por C: {is_cancellation.sum():,}")
    print(f"Quantidades negativas: {negative_quantity.sum():,}")
    print(
        "Quantidade negativa e fatura C: "
        f"{(negative_quantity & is_cancellation).sum():,}"
    )
    print(
        "Quantidade negativa sem fatura C: "
        f"{(negative_quantity & ~is_cancellation).sum():,}"
    )
    print(f"Preços negativos: {negative_price.sum():,}")

    columns = [
        "InvoiceNo", "StockCode", "Description",
        "Quantity", "InvoiceDate", "UnitPrice"
    ]

    print("\n--- EXEMPLOS DE FATURAS C ---")
    if is_cancellation.any():
        print(
            df.loc[is_cancellation, columns]
            .head(10)
            .to_string(index=False)
        )
    else:
        print("Nenhuma fatura C encontrada.")

    print("\n--- QUANTIDADES NEGATIVAS SEM FATURA C ---")
    mask = negative_quantity & ~is_cancellation
    if mask.any():
        print(df.loc[mask, columns].head(10).to_string(index=False))
    else:
        print("Nenhum registro encontrado.")

    print("\n--- PREÇOS NEGATIVOS ---")
    if negative_price.any():
        print(df.loc[negative_price, columns].to_string(index=False))
    else:
        print("Nenhum preço negativo encontrado.")


# ============================================================
# ETAPA 3 — INVESTIGAÇÃO DE REGISTROS ATÍPICOS
# ============================================================

def inspect_unusual_records(df):
    zero_price = df["UnitPrice"] == 0
    negative_quantity = df["Quantity"] < 0
    missing_description = df["Description"].isna()

    invoice_text = df["InvoiceNo"].astype("string").str.strip()
    is_cancellation = invoice_text.str.upper().str.startswith(
        "C", na=False
    )

    print("\n" + "=" * 60)
    print("INVESTIGAÇÃO DE REGISTROS ATÍPICOS")
    print("=" * 60)

    print("\n--- PREÇOS IGUAIS A ZERO ---")
    print(f"Total: {zero_price.sum():,}")
    print(
        "Com quantidade negativa: "
        f"{(zero_price & negative_quantity).sum():,}"
    )
    print(
        "Com descrição ausente: "
        f"{(zero_price & missing_description).sum():,}"
    )
    print(
        "Com fatura iniciada por C: "
        f"{(zero_price & is_cancellation).sum():,}"
    )

    columns = [
        "InvoiceNo", "StockCode", "Description",
        "Quantity", "InvoiceDate", "CustomerID", "Country"
    ]

    print("\n--- QUANTIDADE NEGATIVA E PREÇO ZERO ---")
    mask = negative_quantity & zero_price
    if mask.any():
        print(df.loc[mask, columns].head(15).to_string(index=False))
    else:
        print("Nenhum registro encontrado.")

    print("\n--- QUANTIDADE NEGATIVA POR PREFIXO DA FATURA ---")
    prefix = invoice_text.str[:1].fillna("(ausente)")
    print(prefix[negative_quantity].value_counts().to_string())

    print("\n--- PREÇOS ZERO POR DESCRIÇÃO ---")
    print(
        df.loc[zero_price, "Description"]
        .fillna("(descrição ausente)")
        .value_counts()
        .head(15)
        .to_string()
    )


# ============================================================
# ETAPA 4 — INVESTIGAÇÃO DE DUPLICATAS
# ============================================================

def inspect_duplicates(df):
    print("\n" + "=" * 60)
    print("INVESTIGAÇÃO DE DUPLICATAS")
    print("=" * 60)

    duplicated_mask = df.duplicated(keep=False)
    duplicated_rows = df.loc[duplicated_mask].copy()

    extra_duplicates = int(df.duplicated().sum())

    print(
        "Linhas envolvidas em grupos duplicados: "
        f"{duplicated_mask.sum():,}"
    )
    print(
        "Linhas duplicadas além da primeira ocorrência: "
        f"{extra_duplicates:,}"
    )

    print("\n--- EXEMPLOS DE DUPLICATAS ---")
    if duplicated_rows.empty:
        print("Nenhuma duplicata encontrada.")
        return

    duplicated_rows = duplicated_rows.sort_values(
        by=["InvoiceNo", "StockCode", "InvoiceDate"],
        kind="stable"
    )

    print(duplicated_rows.head(20).to_string(index=False))

    print("\n--- FATURAS COM MAIS LINHAS EM GRUPOS DUPLICADOS ---")
    print(
        duplicated_rows["InvoiceNo"]
        .value_counts()
        .head(10)
        .to_string()
    )


# ============================================================
# ETAPA 5 — IMPACTO POTENCIAL DAS DUPLICATAS
# ============================================================

def inspect_duplicate_impact(df):
    print("\n" + "=" * 60)
    print("IMPACTO POTENCIAL DAS DUPLICATAS")
    print("=" * 60)

    # Mantém apenas as ocorrências excedentes para medir o impacto
    duplicate_mask = df.duplicated(keep="first")
    duplicates = df.loc[duplicate_mask].copy()

    # Valor nominal de cada linha: quantidade x preço unitário
    duplicates["LineValue"] = (
        duplicates["Quantity"] * duplicates["UnitPrice"]
    )

    print(f"\nLinhas excedentes: {len(duplicates):,}")
    print(
        "Quantidade total nas linhas excedentes: "
        f"{duplicates['Quantity'].sum():,}"
    )
    print(
        "Valor nominal das linhas excedentes: "
        f"£{duplicates['LineValue'].sum():,.2f}"
    )

    print("\n--- IMPACTO POR TIPO DE QUANTIDADE ---")
    print(
        "Linhas com quantidade positiva: "
        f"{(duplicates['Quantity'] > 0).sum():,}"
    )
    print(
        "Linhas com quantidade negativa: "
        f"{(duplicates['Quantity'] < 0).sum():,}"
    )
    print(
        "Linhas com quantidade zero: "
        f"{(duplicates['Quantity'] == 0).sum():,}"
    )

    print("\n--- VALOR NOMINAL POR PAÍS ---")
    country_impact = (
        duplicates.groupby("Country", dropna=False)["LineValue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    print(country_impact.to_string())


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    df = inspect_data()

    if df is not None:
        inspect_cancellations(df)
        inspect_unusual_records(df)
        inspect_duplicates(df)
        inspect_duplicate_impact(df)
