
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


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

MONTHLY_FILE = PROCESSED_DIR / "monthly_sales_metrics.csv"
TRENDS_FILE = PROCESSED_DIR / "monthly_sales_trends.csv"
CHART_FILE = PROCESSED_DIR / "monthly_revenue_candidates.png"

# Dezembro de 2011 contém dados somente até o dia 9.
# O mês será preservado nos CSVs, mas não será comparado
# visualmente com meses completos.
PARTIAL_MONTHS = {"2011-12"}


# ============================================================
# 2. CARREGAMENTO DOS DADOS
# ============================================================

def load_data():
    """Carrega a base processada."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Base processada não encontrada: {DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig",
        parse_dates=["InvoiceDate"],
    )

    print(f"Base carregada: {len(df):,} linhas")

    return df


# ============================================================
# 3. MÉTRICAS GERAIS DE VENDAS
# ============================================================

def calculate_sales_metrics(df):
    """Calcula métricas gerais das vendas candidatas."""

    sales = df.loc[
        df["TransactionCategory"] == "standard_sales_candidate"
    ].copy()

    total_revenue = sales["LineValue"].sum()
    total_quantity = sales["Quantity"].sum()
    total_orders = sales["InvoiceNo"].nunique()
    total_customers = sales["CustomerID"].nunique()

    metrics = {
        "Receita bruta candidata (£)": total_revenue,
        "Unidades vendidas candidatas": total_quantity,
        "Pedidos distintos candidatos": total_orders,
        "Clientes identificados": total_customers,
    }

    print("\n" + "=" * 65)
    print("MÉTRICAS GERAIS DE VENDAS")
    print("=" * 65)

    for name, value in metrics.items():
        if "Receita" in name:
            print(f"{name}: £{value:,.2f}")
        else:
            print(f"{name}: {value:,.0f}")

    return sales, metrics


# ============================================================
# 4. MÉTRICAS MENSAIS
# ============================================================

def calculate_monthly_sales(sales):
    """Calcula métricas mensais e preserva todos os meses."""

    monthly = (
        sales.groupby("InvoiceYearMonth", as_index=False)
        .agg(
            Revenue=("LineValue", "sum"),
            Quantity=("Quantity", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique"),
        )
        .sort_values("InvoiceYearMonth")
        .reset_index(drop=True)
    )

    print("\n" + "=" * 65)
    print("MÉTRICAS MENSAIS")
    print("=" * 65)

    display_monthly = monthly.copy()
    display_monthly["Revenue"] = display_monthly["Revenue"].map(
        lambda value: f"£{value:,.2f}"
    )

    print(display_monthly.to_string(index=False))

    monthly.to_csv(
        MONTHLY_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nMétricas mensais salvas em: {MONTHLY_FILE}")

    return monthly


# ============================================================
# 5. VALIDAÇÃO DAS MÉTRICAS
# ============================================================

def validate_metrics(sales, metrics, monthly):
    """Compara os totais gerais com os totais mensais."""

    monthly_revenue = monthly["Revenue"].sum()
    monthly_quantity = monthly["Quantity"].sum()

    revenue_difference = (
        monthly_revenue
        - metrics["Receita bruta candidata (£)"]
    )

    quantity_difference = (
        monthly_quantity
        - metrics["Unidades vendidas candidatas"]
    )

    print("\n" + "=" * 65)
    print("VALIDAÇÃO DAS MÉTRICAS")
    print("=" * 65)

    print(f"Receita mensal acumulada: £{monthly_revenue:,.2f}")
    print(f"Diferença de receita: £{revenue_difference:,.2f}")
    print(f"Diferença de quantidade: {quantity_difference:,.0f}")
    print(f"Meses analisados: {len(monthly)}")

    revenue_ok = abs(revenue_difference) < 0.01
    quantity_ok = quantity_difference == 0

    if revenue_ok and quantity_ok:
        print("Validação de receita e quantidade aprovada.")
    else:
        print(
            "ATENÇÃO: existem diferenças que precisam "
            "ser investigadas."
        )

    monthly_orders = monthly["Orders"].sum()
    overall_orders = metrics["Pedidos distintos candidatos"]

    if monthly_orders != overall_orders:
        print(
            "Observação: a soma dos pedidos mensais difere "
            "do total de pedidos distintos. Um mesmo pedido "
            "pode aparecer em meses diferentes."
        )


# ============================================================
# 6. ANÁLISE DAS TENDÊNCIAS MENSAIS
# ============================================================

def analyze_monthly_trends(monthly):
    """Calcula variações mensais sem comparar o mês parcial."""

    trends = (
        monthly.sort_values("InvoiceYearMonth")
        .copy()
        .reset_index(drop=True)
    )

    trends["RevenueChangePct"] = (
        trends["Revenue"].pct_change() * 100
    )

    # A variação de dezembro de 2011 não é comparável:
    # o mês contém dados somente até 09/12.
    partial_mask = (
        trends["InvoiceYearMonth"]
        .astype(str)
        .isin(PARTIAL_MONTHS)
    )

    trends.loc[partial_mask, "RevenueChangePct"] = float("nan")

    complete_months = trends.loc[~partial_mask]

    print("\n" + "=" * 65)
    print("ANÁLISE DAS TENDÊNCIAS MENSAIS")
    print("=" * 65)

    if not complete_months.empty:
        highest_month = complete_months.loc[
            complete_months["Revenue"].idxmax()
        ]

        lowest_month = complete_months.loc[
            complete_months["Revenue"].idxmin()
        ]

        print(
            f"Maior receita entre os meses completos: "
            f"{highest_month['InvoiceYearMonth']} "
            f"— £{highest_month['Revenue']:,.2f}"
        )

        print(
            f"Menor receita entre os meses completos: "
            f"{lowest_month['InvoiceYearMonth']} "
            f"— £{lowest_month['Revenue']:,.2f}"
        )

    print("\nVariação percentual mensal:")

    for _, row in trends.iterrows():
        month = str(row["InvoiceYearMonth"])
        change = row["RevenueChangePct"]

        if month in PARTIAL_MONTHS:
            print(
                f"{month}: não comparável "
                "(mês parcial)"
            )
        elif pd.isna(change):
            print(f"{month}: sem mês anterior para comparar")
        else:
            print(f"{month}: {change:+.2f}%")

    trends.to_csv(
        TRENDS_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nTendências mensais salvas em: {TRENDS_FILE}")

    return trends


# ============================================================
# 7. GRÁFICO PROFISSIONAL DA RECEITA MENSAL
# ============================================================

def plot_monthly_revenue(monthly):
    """Gera um gráfico de linha usando somente meses completos."""

    plot_data = (
        monthly.loc[
            ~monthly["InvoiceYearMonth"]
            .astype(str)
            .isin(PARTIAL_MONTHS)
        ]
        .sort_values("InvoiceYearMonth")
        .copy()
        .reset_index(drop=True)
    )

    if plot_data.empty:
        print("Não há meses completos disponíveis para o gráfico.")
        return

    month_names = {
        1: "Jan",
        2: "Fev",
        3: "Mar",
        4: "Abr",
        5: "Mai",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Set",
        10: "Out",
        11: "Nov",
        12: "Dez",
    }

    dates = pd.to_datetime(
        plot_data["InvoiceYearMonth"].astype(str),
        format="%Y-%m",
        errors="raise",
    )

    labels = [
        f"{month_names[date.month]}/{date.year}"
        for date in dates
    ]

    revenue = plot_data["Revenue"].astype(float).tolist()
    positions = list(range(len(plot_data)))

    # Paleta e estilo visual.
    background = "#FFFFFF"
    primary = "#2563EB"
    text_color = "#0F172A"
    secondary_text = "#64748B"
    grid_color = "#E2E8F0"

    fig, ax = plt.subplots(figsize=(13, 7))

    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)

    # Linha principal.
    ax.plot(
        positions,
        revenue,
        color=primary,
        linewidth=2.8,
        marker="o",
        markersize=6,
        markerfacecolor=background,
        markeredgecolor=primary,
        markeredgewidth=2,
        zorder=3,
    )

    # Destaca somente o menor e o maior valor.
    min_index = revenue.index(min(revenue))
    max_index = revenue.index(max(revenue))

    for index, color in (
        (min_index, "#EA580C"),
        (max_index, "#16A34A"),
    ):
        ax.scatter(
            positions[index],
            revenue[index],
            s=90,
            color=color,
            edgecolors=background,
            linewidths=1.5,
            zorder=5,
        )

    def format_currency(value, position):
        if value == 0:
            return "£0"

        if abs(value) >= 1_000_000:
            return f"£{value / 1_000_000:.1f} mi"

        return f"£{value / 1_000:.0f} mil"

    ax.yaxis.set_major_formatter(
        FuncFormatter(format_currency)
    )

    # Identifica os extremos sem sobrecarregar a visualização.
    def format_value(value):
        if value >= 1_000_000:
            return f"£{value / 1_000_000:.2f} mi"
        return f"£{value / 1_000:.0f} mil"

    for index in (min_index, max_index):
        value = revenue[index]

        # Coloca os rótulos em posições que reduzem colisões.
        offset = 14 if index != max_index else -24

        if index == min_index:
            offset = -24

        ax.annotate(
            format_value(value),
            (positions[index], value),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center",
            va="bottom" if offset > 0 else "top",
            fontsize=9,
            fontweight="bold",
            color=text_color,
        )

    # Título e subtítulo.
    fig.suptitle(
        "Evolução Mensal da Receita Bruta Candidata",
        x=0.08,
        y=0.965,
        ha="left",
        fontsize=17,
        fontweight="bold",
        color=text_color,
    )

    ax.set_title(
        "Online Retail | Dez/2010 a Nov/2011 | Valores em GBP (£)",
        loc="left",
        fontsize=10,
        color=secondary_text,
        pad=18,
    )

    ax.set_xlabel(
        "Mês da emissão da fatura",
        fontsize=10,
        color=secondary_text,
        labelpad=12,
    )

    ax.set_ylabel(
        "Receita candidata",
        fontsize=10,
        color=secondary_text,
        labelpad=12,
    )

    ax.set_xticks(positions)
    ax.set_xticklabels(
        labels,
        rotation=0,
        ha="center",
        fontsize=9,
        color=secondary_text,
    )

    # O eixo começa em zero para evitar exagerar as variações.
    ax.set_ylim(bottom=0, top=max(revenue) * 1.15)

    ax.grid(
        axis="y",
        linestyle="-",
        linewidth=0.7,
        alpha=1,
        color=grid_color,
    )

    ax.grid(axis="x", visible=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(grid_color)

    ax.tick_params(axis="both", length=0, pad=9)

    # Nota metodológica e interpretação.
    fig.text(
        0.08,
        0.055,
        "Dez/2011 foi excluído do gráfico por conter dados "
        "somente até 09/12. O mês permanece nos arquivos CSV.",
        fontsize=9,
        color=secondary_text,
        ha="left",
    )

    fig.text(
        0.08,
        0.025,
        "Indicadores preliminares; receita candidata sujeita "
        "à validação das regras de negócio.",
        fontsize=8.5,
        color=secondary_text,
        ha="left",
    )

    fig.subplots_adjust(
        left=0.10,
        right=0.97,
        top=0.82,
        bottom=0.19,
    )

    plt.savefig(
        CHART_FILE,
        dpi=300,
        bbox_inches="tight",
        facecolor=background,
    )

    plt.close(fig)

    print("\n" + "=" * 65)
    print("GRÁFICO GERADO COM SUCESSO")
    print("=" * 65)
    print(f"Arquivo: {CHART_FILE}")
    print("Formato: PNG | Resolução: 300 DPI")
    print("Período visualizado: Dez/2010 a Nov/2011")
    print("Dez/2011 permanece nos CSVs, mas foi excluído do gráfico.")


# ============================================================
# 8. EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    """Executa o fluxo completo da análise de vendas."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_data()

    sales, metrics = calculate_sales_metrics(df)

    monthly = calculate_monthly_sales(sales)

    validate_metrics(
        sales,
        metrics,
        monthly,
    )

    analyze_monthly_trends(monthly)

    plot_monthly_revenue(monthly)

    print("\n" + "=" * 65)
    print("ANÁLISE CONCLUÍDA")
    print("=" * 65)

    print(
        "Os resultados representam vendas candidatas e "
        "dependem da validação das regras de negócio."
    )


if __name__ == "__main__":
    main()
