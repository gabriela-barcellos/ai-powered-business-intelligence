from pathlib import Path



import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

import streamlit as st

import requests





# ============================================================

# CONFIGURATION

# ============================================================



st.set_page_config(

    page_title="AI-Powered Business Intelligence",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded",

)



ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data" / "processed"



NAVY = "#203864"

BLUE = "#3563B8"

TEAL = "#199B78"

PURPLE = "#8064A2"

BG = "#F2F5FA"

GRID = "#E5EAF2"

TEXT = "#26364B"

MUTED = "#64748B"





# ============================================================

# VISUAL STYLE

# ============================================================



st.markdown(

    f"""

    <style>

        .stApp {{

            background: {BG};

            color: {TEXT};

        }}



        [data-testid="stHeader"] {{

            background: rgba(242, 245, 250, 0.95);

        }}



        [data-testid="stSidebar"] {{

            background: #FFFFFF;

            border-right: 1px solid #E2E8F0;

        }}



        [data-testid="stSidebar"] h1,

        [data-testid="stSidebar"] h2,

        [data-testid="stSidebar"] h3 {{

            color: {NAVY};

        }}



        .block-container {{

            width: 100%;

            max-width: 1600px;

            padding: 0.45rem 0.8rem 0.5rem 0.8rem;

        }}



        h1, h2, h3 {{

            color: {NAVY} !important;

            letter-spacing: -0.4px;

        }}



        [data-testid="stMetric"] {{

            background: #FFFFFF;

            border: 1px solid #E2E8F0;

            border-radius: 14px;

            padding: 8px 10px;

            box-shadow: 0 3px 12px rgba(32, 56, 100, 0.045);

            min-height: 74px;

        }}



        [data-testid="stMetricLabel"] {{

            color: {MUTED};

            font-size: 0.90rem;

            font-weight: 600;

        }}



        [data-testid="stMetricValue"] {{

            color: {NAVY};

            font-size: clamp(1.05rem, 1.6vw, 1.75rem);

            font-weight: 700;

            overflow-wrap: anywhere;

        }}



        [data-testid="stVerticalBlock"] {{ gap: 0.45rem; }}
        h2 {{ margin-top: 0.2rem; margin-bottom: 0.2rem; }}

        div[data-testid="stPlotlyChart"] {{

            width: 100%;

            min-width: 0;

            box-sizing: border-box;

            overflow: hidden;

            background: #FFFFFF;

            border: 1px solid #E2E8F0;

            border-radius: 14px;

            padding: 8px;

            box-shadow: 0 3px 12px rgba(32, 56, 100, 0.035);

        }}



        div[data-testid="stExpander"] {{

            background: #FFFFFF;

            border: 1px solid #E2E8F0;

            border-radius: 12px;

        }}



        div[data-testid="stDataFrame"] {{

            border: 1px solid #E2E8F0;

            border-radius: 10px;

        }}



        .hero {{

            background: linear-gradient(120deg, #203864 0%, #4567B2 100%);

            padding: 14px 22px;

            border-radius: 18px;

            margin-bottom: 8px;

            color: #FFFFFF;

            box-shadow: 0 8px 24px rgba(32, 56, 100, 0.13);

        }}



        .hero h1 {{

            color: #FFFFFF !important;

            font-size: 1.55rem;

            margin: 0 0 8px 0;

        }}



        .hero p {{

            color: #E8F0FF;

            margin: 0;

            font-size: 0.98rem;

        }}



        .section-caption {{

            color: {MUTED};

            font-size: 0.90rem;

            margin-top: -10px;

            margin-bottom: 18px;

        }}



        .small-note {{

            color: {MUTED};

            font-size: 0.82rem;

        }}



        hr {{

            border-color: #DCE4EF;

        }}



        @media (max-width: 800px) {{

            .block-container {{

                padding: 1rem;

            }}



            .hero {{

                padding: 22px;

            }}



            .hero h1 {{

                font-size: 1.55rem;

            }}

        }}
        /* Keep Streamlit default fixed AI chat composer behavior. */
/* Compact presentation layout */
        .block-container {{
            padding-top: 0.55rem;
            padding-bottom: 0.65rem;
            max-width: 1600px;
        }}
        [data-testid="stMetric"] {{
            padding: 8px 10px;
            min-height: 82px;
        }}
        [data-testid="stVerticalBlock"] {{
            gap: 0.65rem;
        }}
        h1 {{ margin-bottom: 0.35rem; }}

    </style>

    """,

    unsafe_allow_html=True,

)





# ============================================================

# HEADER

# ============================================================



st.markdown(
    """<div class="hero">
<h1>AI-Powered Business Intelligence</h1>
<p>Inteligência de negócios para vendas, produtos e clientes · Online Retail Dataset</p>
</div>""",
    unsafe_allow_html=True,
)





# ============================================================

# DATA LOADING

# ============================================================



@st.cache_data

def load_csv(filename: str) -> pd.DataFrame:

    path = DATA_DIR / filename



    if not path.exists():

        raise FileNotFoundError(f"Arquivo não encontrado: {path}")



    return pd.read_csv(

        path,

        encoding="utf-8-sig",

        low_memory=False,

    )





@st.cache_data

def load_all_data() -> dict[str, pd.DataFrame]:

    return {

        "monthly": load_csv("monthly_sales_metrics.csv"),

        "product_revenue": load_csv(

            "product_revenue_ranking_classified.csv"

        ),

        "product_quantity": load_csv(

            "product_quantity_ranking_classified.csv"

        ),

        "customer_revenue": load_csv(

            "customer_revenue_ranking.csv"

        ),

        "customer_frequency": load_csv(

            "customer_order_frequency_ranking.csv"

        ),

        "retention": load_csv("customer_retention_monthly.csv"),

    }





try:

    data = load_all_data()

except (FileNotFoundError, pd.errors.ParserError) as error:

    st.error(f"Não foi possível carregar os dados: {error}")

    st.info(

        "Confira se os arquivos CSV estão presentes em "

        "data/processed e se os scripts de análise foram executados."

    )

    st.stop()





monthly = data["monthly"].copy()

product_revenue = data["product_revenue"].copy()

product_quantity = data["product_quantity"].copy()

customer_revenue = data["customer_revenue"].copy()

customer_frequency = data["customer_frequency"].copy()

retention = data["retention"].copy()





# ============================================================

# COLUMN VALIDATION

# ============================================================



def require_columns(

    df: pd.DataFrame,

    columns: list[str],

    filename: str,

) -> None:

    missing = set(columns) - set(df.columns)



    if missing:

        raise ValueError(

            f"No arquivo {filename}, faltam colunas: "

            f"{sorted(missing)}"

        )





require_columns(

    monthly,

    ["InvoiceYearMonth", "Revenue", "Orders", "Customers"],

    "monthly_sales_metrics.csv",

)



require_columns(

    product_revenue,

    ["StockCode", "Description", "Revenue"],

    "product_revenue_ranking_classified.csv",

)



require_columns(

    product_quantity,

    ["StockCode", "Description", "Quantity"],

    "product_quantity_ranking_classified.csv",

)



require_columns(

    customer_revenue,

    ["CustomerID", "TotalRevenue", "TotalOrders"],

    "customer_revenue_ranking.csv",

)



require_columns(

    customer_frequency,

    ["CustomerID", "TotalOrders", "TotalRevenue"],

    "customer_order_frequency_ranking.csv",

)



require_columns(

    retention,

    [

        "InvoiceMonth",

        "ActiveCustomers",

        "NewCustomers",

        "ReturningCustomers",

        "NextMonthRetentionRate",

    ],

    "customer_retention_monthly.csv",

)





# ============================================================

# DATA PREPARATION

# ============================================================



monthly["MonthDate"] = pd.to_datetime(

    monthly["InvoiceYearMonth"].astype(str),

    format="%Y-%m",

    errors="coerce",

)



for col in ["Revenue", "Orders", "Customers"]:

    monthly[col] = pd.to_numeric(

        monthly[col], errors="coerce"

    ).fillna(0)



monthly = (

    monthly.dropna(subset=["MonthDate"])

    .sort_values("MonthDate")

    .reset_index(drop=True)

)



for df, columns in [

    (product_revenue, ["Revenue"]),

    (product_quantity, ["Quantity"]),

    (customer_revenue, ["TotalRevenue", "TotalOrders"]),

    (customer_frequency, ["TotalOrders", "TotalRevenue"]),

]:

    for col in columns:

        df[col] = pd.to_numeric(

            df[col], errors="coerce"

        ).fillna(0)



for df in [customer_revenue, customer_frequency]:

    df["CustomerID"] = (

        df["CustomerID"]

        .astype("string")

        .str.replace(r"\.0$", "", regex=True)

    )



retention["MonthDate"] = pd.to_datetime(

    retention["InvoiceMonth"].astype(str),

    format="%Y-%m",

    errors="coerce",

)



for col in [

    "ActiveCustomers",

    "NewCustomers",

    "ReturningCustomers",

    "NextMonthRetentionRate",

]:

    retention[col] = pd.to_numeric(

        retention[col], errors="coerce"

    )





# December 2011 is a partial month.

PARTIAL_MONTHS = {"2011-12"}



monthly["IsPartialMonth"] = (

    monthly["InvoiceYearMonth"]

    .astype(str)

    .isin(PARTIAL_MONTHS)

)





# ============================================================

# HELPER FUNCTIONS

# ============================================================



def style_chart(
    fig,
    height: int = 280,
    left_margin: int = 55,
    right_margin: int = 20,
    top_margin: int = 48,
    bottom_margin: int = 48,
):

    fig.update_layout(

        template="plotly_white",

        autosize=True,

        height=height,

        margin=dict(
            l=left_margin,
            r=right_margin,
            t=top_margin,
            b=bottom_margin,
        ),

        paper_bgcolor="#FFFFFF",

        plot_bgcolor="#FFFFFF",

        font=dict(

            family="Arial, sans-serif",

            size=12,

            color=TEXT,

        ),

        title=dict(

            font=dict(size=14, color=NAVY),

            x=0.02,

            xanchor="left",

        ),

        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="right",

            x=1,

        ),

        hoverlabel=dict(

            bgcolor="#FFFFFF",

            font_color=TEXT,

        ),

    )



    fig.update_xaxes(

        automargin=True,

        showgrid=False,

        linecolor=GRID,

        tickfont=dict(color=MUTED, size=10),

        title_font=dict(color=MUTED),

        title_standoff=8,

    )



    fig.update_yaxes(

        automargin=True,

        gridcolor=GRID,

        zerolinecolor=GRID,

        tickfont=dict(color=MUTED, size=9),

        title_font=dict(color=MUTED),

        title_standoff=8,

    )



    return fig





def money(value: float) -> str:

    return f"£ {value:,.2f}"



# ============================================================

# FILTERS

# ============================================================



st.sidebar.markdown("## Filtros")

st.sidebar.caption("Personalize o período da análise.")



if monthly.empty:

    st.error("Não há dados mensais válidos para exibição.")

    st.stop()



month_options = {

    pd.Timestamp(row["MonthDate"]).strftime("%Y-%m"): row["MonthDate"]

    for _, row in monthly.iterrows()

}



available_labels = list(month_options.keys())



selected_labels = st.sidebar.multiselect(

    "Período",

    options=available_labels,

    default=available_labels,

    help="Selecione um ou mais meses para filtrar os indicadores de vendas.",

)



if not selected_labels:

    st.warning("Selecione pelo menos um mês no filtro lateral.")

    st.stop()



selected_dates = [month_options[label] for label in selected_labels]



filtered_monthly = monthly.loc[

    monthly["MonthDate"].isin(selected_dates)

].sort_values("MonthDate").copy()



st.sidebar.divider()

st.sidebar.markdown("### Sobre os dados")

st.sidebar.caption(

    "Fonte: UCI Online Retail\n\n"

    "Período original: dez/2010 a dez/2011.\n\n"

    "Dezembro/2011 contém dados somente até o dia 9."

)





# ============================================================
# COMPACT DASHBOARD LAYOUT
# ============================================================

# ============================================================

# EXECUTIVE OVERVIEW

# ============================================================



total_revenue = filtered_monthly["Revenue"].sum()

total_invoices = filtered_monthly["Orders"].sum()



average_candidate_revenue_per_invoice = (

    total_revenue / total_invoices if total_invoices else 0

)



active_customer_months = filtered_monthly["Customers"].sum()



st.markdown("## Visão executiva")




k1, k2, k3, k4 = st.columns(4)



k1.metric(

    "Receita bruta candidata",

    money(total_revenue),

    help=(

        "Soma da receita nominal das linhas classificadas como vendas "

        "candidatas. Não representa receita líquida validada."

    ),

)



k2.metric(

    "Faturas com vendas candidatas",

    f"{total_invoices:,.0f}",

    help=(

        "Número de faturas distintas que contêm pelo menos uma linha "

        "classificada como standard_sales_candidate. "

        "Não representa necessariamente pedidos concluídos."

    ),

)



k3.metric(

    "Clientes ativos · soma mensal",

    f"{active_customer_months:,.0f}",

    help=(

        "Soma dos clientes ativos em cada mês. O mesmo cliente pode ser "

        "contado em vários meses; não é o total de clientes únicos no período."

    ),

)



k4.metric(

    "Receita candidata média por fatura",

    money(average_candidate_revenue_per_invoice),

    help=(

        "Receita candidata do período dividida pelo número de faturas "

        "com vendas candidatas. Indicador preliminar, não necessariamente "

        "equivalente ao ticket médio comercial."

    ),

)



st.caption(

    "A receita candidata não representa lucro nem receita líquida. "

    "Clientes ativos · soma mensal é uma soma de clientes-mês, não uma "

    "contagem de clientes únicos. A média por fatura é um indicador preliminar."

)





# ============================================================

# COMPACT VISUAL GRID: all eight charts remain on the same page
chart_row_1 = st.columns(3, gap="small")
chart_row_2 = st.columns(3, gap="small")
chart_row_3 = st.columns(2, gap="small")

# SALES TRENDS

# ============================================================






sales_left, sales_right = chart_row_1[0], chart_row_1[1]



# Exclude December 2011 from month-to-month comparisons because

# the available dataset contains records only through December 9.

complete_months = filtered_monthly.loc[

    ~filtered_monthly["IsPartialMonth"]

].copy()



with sales_left:

    fig_revenue = go.Figure()



    fig_revenue.add_trace(

        go.Scatter(

            x=complete_months["MonthDate"],

            y=complete_months["Revenue"],

            mode="lines+markers",

            name="Receita candidata",

            line=dict(color=BLUE, width=3),

            marker=dict(size=7, color=BLUE),

            hovertemplate=(

                "%{x|%b %Y}<br>"

                "Receita candidata: £%{y:,.2f}<extra></extra>"

            ),

        )

    )



    fig_revenue.update_layout(

        title="Receita mensal — meses completos",

        xaxis_title="Mês",

        yaxis_title="Receita candidata (£)",

    )



    fig_revenue.update_yaxes(

        tickprefix="£ ",

        tickformat=",.0f",

    )



    st.plotly_chart(

        style_chart(fig_revenue, height=260, left_margin=66, top_margin=42, bottom_margin=48),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )



with sales_right:

    fig_invoices = px.bar(

        complete_months,

        x="MonthDate",

        y="Orders",

        title="Faturas com vendas candidatas — meses completos",

        labels={

            "MonthDate": "Mês",

            "Orders": "Faturas",

        },

        color_discrete_sequence=[TEAL],

    )



    fig_invoices.update_traces(

        marker_line_width=0,

        hovertemplate=(

            "%{x|%b %Y}<br>"

            "Faturas: %{y:,.0f}<extra></extra>"

        ),

    )



    fig_invoices.update_yaxes(title_text="", automargin=True)

    fig_invoices.update_xaxes(tickformat="%b\n%Y")



    st.plotly_chart(

        style_chart(fig_invoices, height=260, left_margin=58, top_margin=42, bottom_margin=48),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )








# ============================================================

# PRODUCT PERFORMANCE

# ============================================================




st.markdown(

    '<p class="section-caption">'

    "Produtos classificados como candidatos a mercadorias; serviços e casos "

    "especiais são excluídos quando há classificação disponível. "

    "Os rankings usam o período completo da base e não respondem ao filtro mensal."

    "</p>",

    unsafe_allow_html=True,

)





def merchandise_only(df: pd.DataFrame) -> pd.DataFrame:

    if "Classification" in df.columns:

        return df.loc[

            df["Classification"].eq("merchandise_candidate")

        ].copy()



    return df.copy()





products_rev = merchandise_only(product_revenue)

products_qty = merchandise_only(product_quantity)



product_left, product_right = chart_row_1[2], chart_row_2[0]



with product_left:

    top_rev = products_rev.nlargest(10, "Revenue").copy()



    top_rev["ProductLabel"] = (

        top_rev["Description"]

        .fillna("Sem descrição")

        .astype(str)

        .str.slice(0, 36)

    )



    top_rev = top_rev.sort_values("Revenue", ascending=True)



    fig_product_rev = px.bar(

        top_rev,

        x="Revenue",

        y="ProductLabel",

        orientation="h",

        title="Top 10 produtos por receita",

        labels={

            "Revenue": "Receita (£)",

            "ProductLabel": "Produto",

        },

        color_discrete_sequence=[BLUE],

        custom_data=["StockCode", "Description"],

    )



    fig_product_rev.update_traces(

        hovertemplate=(

            "%{customdata[1]}<br>"

            "Código: %{customdata[0]}<br>"

            "Receita: £%{x:,.2f}<extra></extra>"

        ),

        cliponaxis=False,

    )



    fig_product_rev.update_layout(

        yaxis=dict(title_text="", automargin=True, tickfont=dict(size=9)),

        xaxis_tickprefix="£ ",

        xaxis_tickformat=",.0f",

    )



    st.plotly_chart(

        style_chart(fig_product_rev, height=305, left_margin=185, top_margin=42, bottom_margin=55),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )



with product_right:

    top_qty = products_qty.nlargest(10, "Quantity").copy()



    top_qty["ProductLabel"] = (

        top_qty["Description"]

        .fillna("Sem descrição")

        .astype(str)

        .str.slice(0, 36)

    )



    top_qty = top_qty.sort_values("Quantity", ascending=True)



    fig_product_qty = px.bar(

        top_qty,

        x="Quantity",

        y="ProductLabel",

        orientation="h",

        title="Top 10 produtos por quantidade",

        labels={

            "Quantity": "Quantidade",

            "ProductLabel": "Produto",

        },

        color_discrete_sequence=[TEAL],

        custom_data=["StockCode", "Description"],

    )



    fig_product_qty.update_traces(

        hovertemplate=(

            "%{customdata[1]}<br>"

            "Código: %{customdata[0]}<br>"

            "Quantidade: %{x:,.0f}<extra></extra>"

        ),

        cliponaxis=False,

    )



    fig_product_qty.update_layout(yaxis=dict(title_text="", automargin=True, tickfont=dict(size=9)))



    st.plotly_chart(

        style_chart(fig_product_qty, height=305, left_margin=185, top_margin=42, bottom_margin=55),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )



# ============================================================

# CUSTOMER ANALYSIS

# ============================================================




st.markdown(

    '<p class="section-caption">'

    "Rankings calculados para o período completo disponível na base, "

    "independentemente do filtro mensal. A frequência utiliza a definição "

    "de pedidos adotada no script de análise."

    "</p>",

    unsafe_allow_html=True,

)



client_left, client_right = chart_row_2[1], chart_row_2[2]



with client_left:

    top_client_rev = customer_revenue.nlargest(

        10, "TotalRevenue"

    ).copy()



    top_client_rev["CustomerLabel"] = (

        top_client_rev["CustomerID"].astype(str)

    )



    top_client_rev = top_client_rev.sort_values(

        "TotalRevenue", ascending=True

    )



    fig_client_rev = px.bar(

        top_client_rev,

        x="TotalRevenue",

        y="CustomerLabel",

        orientation="h",

        title="Top 10 clientes por receita",

        labels={

            "TotalRevenue": "Receita (£)",

            "CustomerLabel": "ID do cliente",

        },

        color_discrete_sequence=[BLUE],

        custom_data=["TotalOrders"],

    )



    fig_client_rev.update_traces(

        hovertemplate=(

            "Cliente: %{y}<br>"

            "Receita: £%{x:,.2f}<br>"

            "Faturas/pedidos segundo a análise: %{customdata[0]:,.0f}"

            "<extra></extra>"

        ),

        cliponaxis=False,

    )



    fig_client_rev.update_layout(

        yaxis_title="",

        xaxis_tickprefix="£ ",

        xaxis_tickformat=",.0f",

    )



    st.plotly_chart(

        style_chart(fig_client_rev, height=285, left_margin=78, top_margin=42, bottom_margin=55),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )



with client_right:

    top_client_freq = customer_frequency.nlargest(

        10, "TotalOrders"

    ).copy()



    top_client_freq["CustomerLabel"] = (

        top_client_freq["CustomerID"].astype(str)

    )



    top_client_freq = top_client_freq.sort_values(

        "TotalOrders", ascending=True

    )



    fig_client_freq = px.bar(

        top_client_freq,

        x="TotalOrders",

        y="CustomerLabel",

        orientation="h",

        title="Top 10 clientes por frequência",

        labels={

            "TotalOrders": "Faturas/pedidos segundo a análise",

            "CustomerLabel": "ID do cliente",

        },

        color_discrete_sequence=[PURPLE],

        custom_data=["TotalRevenue"],

    )



    fig_client_freq.update_traces(

        hovertemplate=(

            "Cliente: %{y}<br>"

            "Faturas/pedidos: %{x:,.0f}<br>"

            "Receita: £%{customdata[0]:,.2f}<extra></extra>"

        ),

        cliponaxis=False,

    )



    fig_client_freq.update_layout(yaxis_title="")



    st.plotly_chart(

        style_chart(fig_client_freq, height=285, left_margin=78, top_margin=42, bottom_margin=55),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )





# ============================================================

# RETENTION AND CUSTOMER BEHAVIOR

# ============================================================






filtered_retention = retention.loc[

    retention["MonthDate"].isin(selected_dates)

].sort_values("MonthDate").copy()



retention_left, retention_right = chart_row_3[0], chart_row_3[1]



with retention_left:

    fig_active = px.line(

        filtered_retention,

        x="MonthDate",

        y="ActiveCustomers",

        markers=True,

        title="Clientes ativos por mês",

        labels={

            "MonthDate": "Mês",

            "ActiveCustomers": "Clientes ativos",

        },

        color_discrete_sequence=[BLUE],

    )



    fig_active.update_traces(

        line=dict(width=3),

        marker=dict(size=7),

        hovertemplate=(

            "%{x|%b %Y}<br>"

            "Clientes ativos: %{y:,.0f}<extra></extra>"

        ),

    )



    fig_active.update_xaxes(tickformat="%b\n%Y")



    st.plotly_chart(

        style_chart(fig_active, height=260, left_margin=66, top_margin=42, bottom_margin=48),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )



with retention_right:

    # IMPORTANT:

    # Exclude months without a valid next-month retention rate.

    # December 2011 has NaN because January 2012 is not available.

    retention_for_chart = filtered_retention.dropna(

        subset=["NextMonthRetentionRate"]

    ).copy()



    fig_retention = px.line(

        retention_for_chart,

        x="MonthDate",

        y="NextMonthRetentionRate",

        markers=True,

        title="Retenção no mês seguinte",

        labels={

            "MonthDate": "Mês",

            "NextMonthRetentionRate": "Retenção (%)",

        },

        color_discrete_sequence=[TEAL],

    )



    fig_retention.update_traces(

        line=dict(width=3),

        marker=dict(size=7),

        hovertemplate=(

            "%{x|%b %Y}<br>"

            "Retenção: %{y:.2f}%<extra></extra>"

        ),

        connectgaps=False,

    )



    fig_retention.update_yaxes(

        ticksuffix="%",

        range=[0, 100],

    )



    fig_retention.update_xaxes(tickformat="%b\n%Y")



    st.plotly_chart(

        style_chart(fig_retention, height=260, left_margin=66, top_margin=42, bottom_margin=48),

        use_container_width=True,

        config={"responsive": True, "displayModeBar": False},

    )



st.caption("Dezembro de 2011 é parcial. A taxa de retenção de dezembro não é calculada porque não há mês seguinte disponível.")





# ============================================================

# MONTHLY TABLE

# ============================================================

with st.expander("Consultar tabela mensal"):
    # Work on a copy and support both original and already-translated
    # column names so the table does not fail if upstream labels change.
    display_monthly = filtered_monthly.copy()

    if "InvoiceYearMonth" in display_monthly.columns:
        display_monthly["Período"] = display_monthly["InvoiceYearMonth"].astype(str)
    elif "Período" not in display_monthly.columns:
        display_monthly["Período"] = display_monthly.index.astype(str)

    display_monthly.loc[
        display_monthly["Período"].isin(PARTIAL_MONTHS),
        "Período",
    ] = display_monthly.loc[
        display_monthly["Período"].isin(PARTIAL_MONTHS),
        "Período",
    ].astype(str) + " (parcial)"

    column_aliases = {
        "Revenue": "Receita candidata (£)",
        "Receita candidata (£)": "Receita candidata (£)",
        "Orders": "Faturas com vendas candidatas",
        "Faturas com vendas candidatas": "Faturas com vendas candidatas",
        "Customers": "Clientes ativos",
        "Clientes ativos": "Clientes ativos",
    }
    display_monthly = display_monthly.rename(
        columns={
            source: target
            for source, target in column_aliases.items()
            if source in display_monthly.columns and source != target
        }
    )

    desired_columns = [
        "Período",
        "Receita candidata (£)",
        "Faturas com vendas candidatas",
        "Clientes ativos",
    ]
    available_columns = [
        column for column in desired_columns
        if column in display_monthly.columns
    ]
    display_monthly = display_monthly[available_columns].copy()

    column_config = {}
    if "Receita candidata (£)" in display_monthly.columns:
        column_config["Receita candidata (£)"] = st.column_config.NumberColumn(
            "Receita candidata (£)",
            format="£ %.2f",
        )
    if "Faturas com vendas candidatas" in display_monthly.columns:
        column_config["Faturas com vendas candidatas"] = st.column_config.NumberColumn(
            "Faturas com vendas candidatas",
            format="%d",
        )
    if "Clientes ativos" in display_monthly.columns:
        column_config["Clientes ativos"] = st.column_config.NumberColumn(
            "Clientes ativos",
            format="%d",
        )

    st.dataframe(
        display_monthly,
        width="stretch",
        hide_index=True,
        column_config=column_config,
    )


# AI BUSINESS ANALYST — LOCAL OLLAMA

# ============================================================



st.divider()

st.markdown("## AI Business Analyst")



st.markdown(

    '<p class="section-caption">'

    "Explore indicadores, compare resultados e investigue oportunidades "

    "com análises baseadas nos dados do projeto."

    "</p>",

    unsafe_allow_html=True,

)





# ============================================================

# 1. MONTHLY COMPARISONS — CALCULATED BY PYTHON

# ============================================================



def calculate_monthly_comparisons() -> pd.DataFrame:

    """Calculate revenue changes between consecutive complete months."""



    columns = [

        "PreviousMonth",

        "CurrentMonth",

        "PreviousRevenue",

        "CurrentRevenue",

        "RevenueChange",

        "PercentageChange",

    ]



    df = filtered_monthly.copy()



    df = df.loc[

        ~df["IsPartialMonth"].fillna(False).astype(bool)

    ].copy()



    if df.empty:

        return pd.DataFrame(columns=columns)



    df["MonthDate"] = pd.to_datetime(

        df["InvoiceYearMonth"].astype(str),

        format="%Y-%m",

        errors="coerce",

    )



    df = (

        df.dropna(subset=["MonthDate"])

        .sort_values("MonthDate")

        .reset_index(drop=True)

    )



    results = []



    for i in range(1, len(df)):

        previous = df.iloc[i - 1]

        current = df.iloc[i]



        expected_next_month = (

            previous["MonthDate"] + pd.DateOffset(months=1)

        )



        if current["MonthDate"] != expected_next_month:

            continue



        previous_revenue = float(previous["Revenue"])

        current_revenue = float(current["Revenue"])

        difference = current_revenue - previous_revenue



        percentage = (

            difference / abs(previous_revenue) * 100

            if previous_revenue != 0

            else None

        )



        results.append(

            {

                "PreviousMonth": previous["InvoiceYearMonth"],

                "CurrentMonth": current["InvoiceYearMonth"],

                "PreviousRevenue": previous_revenue,

                "CurrentRevenue": current_revenue,

                "RevenueChange": difference,

                "PercentageChange": percentage,

            }

        )



    return pd.DataFrame(results, columns=columns)





def build_monthly_comparison_summary() -> str:

    """Create a text summary of Python-calculated monthly changes."""



    comparisons = calculate_monthly_comparisons()



    if comparisons.empty:

        return (

            "Não há meses completos consecutivos suficientes "

            "para calcular as variações no período selecionado."

        )



    lines = []



    for _, row in comparisons.iterrows():

        pct = row["PercentageChange"]



        pct_text = (

            f"{pct:+.2f}%"

            if pd.notna(pct)

            else "percentual indisponível"

        )



        lines.append(

            f"{row['PreviousMonth']} para {row['CurrentMonth']}: "

            f"variação de £{row['RevenueChange']:,.2f} "

            f"({pct_text})."

        )



    valid = comparisons.dropna(subset=["PercentageChange"])



    if not valid.empty:

        increase = valid.loc[valid["PercentageChange"].idxmax()]

        decrease = valid.loc[valid["PercentageChange"].idxmin()]



        lines.append(

            "\nMAIOR ALTA PERCENTUAL: "

            f"{increase['PreviousMonth']} para "

            f"{increase['CurrentMonth']}: "

            f"{increase['PercentageChange']:+.2f}%, "

            f"variação de £{increase['RevenueChange']:,.2f}."

        )



        lines.append(

            "MAIOR QUEDA PERCENTUAL: "

            f"{decrease['PreviousMonth']} para "

            f"{decrease['CurrentMonth']}: "

            f"{decrease['PercentageChange']:+.2f}%, "

            f"variação de £{decrease['RevenueChange']:,.2f}."

        )



    return "\n".join(lines)





# ============================================================

# 2. LOAD ORIGINAL TRANSACTIONS

# ============================================================



@st.cache_data

def load_raw_transactions() -> pd.DataFrame:

    """Load and prepare the original UCI Online Retail workbook."""



    possible_paths = [

        ROOT / "data" / "raw" / "Online Retail.xlsx",

        ROOT / "raw" / "Online Retail.xlsx",

    ]



    raw_path = next(

        (path for path in possible_paths if path.exists()),

        None,

    )



    if raw_path is None:

        raise FileNotFoundError(

            "Não encontrei Online Retail.xlsx. "

            "Verifique se o arquivo está em data/raw/ "

            "ou raw/ dentro do projeto."

        )



    df = pd.read_excel(raw_path)



    required = [

        "InvoiceNo",

        "StockCode",

        "Description",

        "Quantity",

        "InvoiceDate",

        "UnitPrice",

    ]



    missing = set(required) - set(df.columns)



    if missing:

        raise ValueError(

            f"Colunas ausentes no arquivo original: {sorted(missing)}"

        )



    # Match the project's duplicate-removal approach.

    df = df.drop_duplicates().copy()



    df["InvoiceNo"] = df["InvoiceNo"].astype("string").str.strip()

    df["StockCode"] = df["StockCode"].astype("string").str.strip()

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")

    df["InvoiceDate"] = pd.to_datetime(

        df["InvoiceDate"], errors="coerce"

    )



    # Retain candidate sales rows only.

    # These filters do not establish validated net revenue.

    df = df.loc[

        ~df["InvoiceNo"].str.upper().str.startswith("C", na=False)

        & (df["Quantity"] > 0)

        & (df["UnitPrice"] > 0)

        & df["InvoiceDate"].notna()

        & df["StockCode"].notna()

    ].copy()



    df["Month"] = df["InvoiceDate"].dt.strftime("%Y-%m")

    df["LineValue"] = df["Quantity"] * df["UnitPrice"]



    return df





# ============================================================

# 3. PRODUCT CONTRIBUTION ANALYSIS

# ============================================================



def build_product_contribution_summary() -> str:

    """

    Compare product-level candidate revenue between the months

    with the largest percentage increase and decrease.

    """



    comparisons = calculate_monthly_comparisons()



    if comparisons.empty:

        return (

            "Não há meses completos consecutivos selecionados "

            "para analisar a contribuição dos produtos."

        )



    valid = comparisons.dropna(subset=["PercentageChange"])



    if valid.empty:

        return "Não há variações mensais válidas para analisar."



    increase = valid.loc[valid["PercentageChange"].idxmax()]

    decrease = valid.loc[valid["PercentageChange"].idxmin()]



    try:

        transactions = load_raw_transactions()



        # Apply the dashboard's merchandise classification when available.

        if "Classification" in product_revenue.columns:

            merchandise_codes = set(

                merchandise_only(product_revenue)["StockCode"]

                .astype("string")

                .str.strip()

                .dropna()

            )



            transactions = transactions.loc[

                transactions["StockCode"].isin(merchandise_codes)

            ].copy()



        monthly_products = (

            transactions.groupby(

                ["Month", "StockCode"], as_index=False

            )

            .agg(

                Revenue=("LineValue", "sum"),

                Description=(

                    "Description",

                    lambda values: (

                        values.dropna().astype(str).iloc[0]

                        if not values.dropna().empty

                        else "Sem descrição"

                    ),

                ),

            )

        )



        output = [

            "ANÁLISE DE CONTRIBUIÇÃO POR PRODUTO",

            "Método: receita candidata do mês atual menos "

            "receita candidata do mês anterior, por produto.",

            "Valores positivos indicam aumento; valores negativos "

            "indicam redução.",

            "Os resultados mostram variações observadas, não causas.",

        ]



        for label, comparison in [

            ("MAIOR ALTA PERCENTUAL", increase),

            ("MAIOR QUEDA PERCENTUAL", decrease),

        ]:

            previous_month = comparison["PreviousMonth"]

            current_month = comparison["CurrentMonth"]



            previous = monthly_products.loc[

                monthly_products["Month"].eq(previous_month),

                ["StockCode", "Description", "Revenue"],

            ].rename(

                columns={

                    "Description": "DescriptionPrevious",

                    "Revenue": "PreviousRevenue",

                }

            )



            current = monthly_products.loc[

                monthly_products["Month"].eq(current_month),

                ["StockCode", "Description", "Revenue"],

            ].rename(

                columns={

                    "Description": "DescriptionCurrent",

                    "Revenue": "CurrentRevenue",

                }

            )



            delta = previous.merge(

                current,

                on="StockCode",

                how="outer",

            )



            delta["Description"] = (

                delta["DescriptionCurrent"]

                .fillna(delta["DescriptionPrevious"])

                .fillna("Sem descrição")

            )



            delta["PreviousRevenue"] = delta[

                "PreviousRevenue"

            ].fillna(0)



            delta["CurrentRevenue"] = delta[

                "CurrentRevenue"

            ].fillna(0)



            delta["RevenueChange"] = (

                delta["CurrentRevenue"] - delta["PreviousRevenue"]

            )



            delta = delta.loc[

                delta["RevenueChange"].abs() > 0.005

            ].copy()



            output.append(

                f"\n{label}: {previous_month} para {current_month}."

            )



            output.append(

                f"Variação mensal total: "

                f"£{comparison['RevenueChange']:,.2f} "

                f"({comparison['PercentageChange']:+.2f}%)."

            )



            if delta.empty:

                output.append(

                    "Nenhuma variação por produto foi encontrada."

                )

                continue



            output.append("Produtos com maiores aumentos de receita:")



            for _, row in delta.nlargest(

                5, "RevenueChange"

            ).iterrows():

                output.append(

                    f"- {row['Description']} "

                    f"(código {row['StockCode']}): "

                    f"£{row['RevenueChange']:+,.2f}."

                )



            output.append("Produtos com maiores quedas de receita:")



            for _, row in delta.nsmallest(

                5, "RevenueChange"

            ).iterrows():

                output.append(

                    f"- {row['Description']} "

                    f"(código {row['StockCode']}): "

                    f"£{row['RevenueChange']:+,.2f}."

                )



        output.append(

            "\nLimitação: a diferença por produto não prova a causa "

            "da variação mensal. Promoções, sazonalidade e outros "

            "fatores não podem ser confirmados por estes cálculos."

        )



        return "\n".join(output)



    except (FileNotFoundError, ValueError, ImportError) as error:

        return (

            "ANÁLISE POR PRODUTO INDISPONÍVEL: "

            f"{error}. Não deduza contribuições mensais a partir "

            "dos rankings gerais."

        )





# ============================================================

# 4. ADDITIONAL EVIDENCE SUMMARY

# ============================================================



def build_evidence_summary() -> str:

    """Summarize rankings and retention without claiming causation."""



    findings = []



    products = merchandise_only(product_revenue).copy()



    if not products.empty:

        top_products = products.nlargest(10, "Revenue")

        total_revenue = products["Revenue"].sum()



        if total_revenue > 0:

            share = top_products["Revenue"].sum() / total_revenue * 100



            findings.append(

                "RANKING DE PRODUTOS:\n"

                f"Os 10 produtos líderes representam {share:.2f}% "

                "da receita representada no ranking de todo o período. "

                "Isso não comprova quais produtos explicaram "

                "uma variação em um mês específico."

            )



    if not customer_revenue.empty:

        top_customers = customer_revenue.nlargest(

            10, "TotalRevenue"

        )



        total_customer_revenue = customer_revenue[

            "TotalRevenue"

        ].sum()



        if total_customer_revenue > 0:

            share = (

                top_customers["TotalRevenue"].sum()

                / total_customer_revenue

                * 100

            )



            findings.append(

                "RANKING DE CLIENTES:\n"

                f"Os 10 clientes líderes representam {share:.2f}% "

                "da receita representada no ranking de todo o período. "

                "Isso não comprova quais clientes explicaram "

                "uma variação mensal específica."

            )



    valid_retention = filtered_retention.dropna(

        subset=["NextMonthRetentionRate"]

    )



    if not valid_retention.empty:

        highest = valid_retention.loc[

            valid_retention["NextMonthRetentionRate"].idxmax()

        ]



        lowest = valid_retention.loc[

            valid_retention["NextMonthRetentionRate"].idxmin()

        ]



        findings.append(

            "RETENÇÃO:\n"

            f"Maior taxa observada: {highest['InvoiceMonth']}, "

            f"{highest['NextMonthRetentionRate']:.2f}%.\n"

            f"Menor taxa observada: {lowest['InvoiceMonth']}, "

            f"{lowest['NextMonthRetentionRate']:.2f}%."

        )



    findings.append(

        "LIMITAÇÕES:\n"

        "Receita candidata não é lucro nem receita líquida validada. "

        "Os dados descritivos não comprovam que promoções, marketing, "

        "concorrência ou sazonalidade causaram uma variação."

    )



    return "\n\n".join(findings)





# ============================================================

# 5. BUILD CONTEXT FOR OLLAMA

# ============================================================



def build_ai_context() -> str:

    """Build context from the dashboard's processed data."""



    monthly_context = filtered_monthly.copy()



    if "MonthDate" in monthly_context.columns:

        monthly_context = monthly_context.sort_values("MonthDate")

    else:

        monthly_context = monthly_context.sort_values("InvoiceYearMonth")



    monthly_export = monthly_context[

        [

            "InvoiceYearMonth",

            "Revenue",

            "Orders",

            "Customers",

            "IsPartialMonth",

        ]

    ].rename(

        columns={

            "InvoiceYearMonth": "Month",

            "Revenue": "CandidateRevenueGBP",

            "Orders": "CandidateSalesInvoices",

            "Customers": "ActiveCustomers",

        }

    )



    products = merchandise_only(product_revenue).copy()



    top_products = products.nlargest(

        10, "Revenue"

    )[["StockCode", "Description", "Revenue"]]



    top_customers = customer_revenue.nlargest(

        10, "TotalRevenue"

    )[["CustomerID", "TotalRevenue", "TotalOrders"]]



    retention_context = filtered_retention[

        [

            "InvoiceMonth",

            "ActiveCustomers",

            "NewCustomers",

            "ReturningCustomers",

            "NextMonthRetentionRate",

        ]

    ].copy()



    return (

        "PROJETO: AI-Powered Business Intelligence.\n"

        "Fonte: UCI Online Retail.\n"

        "Moeda: GBP (£).\n\n"

        "LIMITAÇÕES DOS DADOS:\n"

        "- Receita candidata não é lucro nem receita líquida validada.\n"

        "- Faturas candidatas não são necessariamente pedidos concluídos.\n"

        "- Dezembro de 2011 é parcial, com dados até 9 de dezembro.\n"

        "- Não compare dezembro de 2011 diretamente com meses completos.\n"

        "- Rankings de produtos e clientes abrangem todo o período.\n"

        "- Métricas mensais refletem os meses selecionados.\n"

        "- Dados descritivos não comprovam causalidade.\n\n"

        "MÉTRICAS MENSAIS:\n"

        + monthly_export.to_csv(index=False)

        + "\nCOMPARAÇÕES MENSAIS CALCULADAS PELO PYTHON:\n"

        + build_monthly_comparison_summary()

        + "\n\nTOP 10 PRODUTOS POR RECEITA CANDIDATA:\n"

        + top_products.to_csv(index=False)

        + "\nTOP 10 CLIENTES POR RECEITA CANDIDATA:\n"

        + top_customers.to_csv(index=False)

        + "\nMÉTRICAS DE RETENÇÃO:\n"

        + retention_context.to_csv(index=False)

        + "\n\nEVIDÊNCIAS ADICIONAIS:\n"

        + build_evidence_summary()

        + "\n\nCONTRIBUIÇÃO POR PRODUTO ENTRE MESES:\n"

        + build_product_contribution_summary()

    )





# ============================================================

st.caption("Dezembro de 2011 é parcial. Os rankings de produtos e clientes cobrem o período completo da base.")


# 6. MONTHLY COMPARISON TABLE

# ============================================================



with st.expander("Variações mensais calculadas pelo Python"):

    comparisons = calculate_monthly_comparisons()



    if comparisons.empty:

        st.info(

            "Não há meses completos consecutivos para comparar "

            "no período selecionado."

        )

    else:

        display_comparisons = comparisons.rename(

            columns={

                "PreviousMonth": "Mês anterior",

                "CurrentMonth": "Mês atual",

                "PreviousRevenue": "Receita anterior (£)",

                "CurrentRevenue": "Receita atual (£)",

                "RevenueChange": "Variação (£)",

                "PercentageChange": "Variação (%)",

            }

        )



        st.dataframe(

            display_comparisons,

            use_container_width=True,

            hide_index=True,

            column_config={

                "Receita anterior (£)": st.column_config.NumberColumn(

                    format="£ %.2f"

                ),

                "Receita atual (£)": st.column_config.NumberColumn(

                    format="£ %.2f"

                ),

                "Variação (£)": st.column_config.NumberColumn(

                    format="£ %.2f"

                ),

                "Variação (%)": st.column_config.NumberColumn(

                    format="%.2f%%"

                ),

            },

        )



        st.caption(

            "Os cálculos são realizados pelo Python. "

            "Dezembro de 2011 é excluído por ser um mês parcial."

        )







# ============================================================

# 7. CHAT INTERFACE — AI BUSINESS ANALYST

# ============================================================



if "ai_chat_history" not in st.session_state:

    st.session_state.ai_chat_history = []



with st.expander("Exemplos de perguntas", expanded=False):

    st.markdown(

        "- Qual foi a maior alta e a maior queda percentual?\n"

        "- Quais produtos mais contribuíram para a maior alta?\n"

        "- Quais produtos mais contribuíram para a maior queda?\n"

        "- Quais produtos lideram em receita?\n"

        "- Como está a retenção de clientes?\n"

        "- Uma promoção pode explicar a variação observada?"

    )



# Exibe o histórico da conversa

for chat_message in st.session_state.ai_chat_history:

    with st.chat_message(chat_message["role"]):

        st.markdown(chat_message["content"])



user_question = st.chat_input(

    "Pergunte algo sobre os dados do dashboard..."

)



if user_question:

    st.session_state.ai_chat_history.append(

        {"role": "user", "content": user_question}

    )



    with st.chat_message("user"):

        st.markdown(user_question)



    system_prompt = """

Você é o AI Business Analyst de um dashboard profissional de

Business Intelligence que utiliza o dataset UCI Online Retail.



Responda sempre em português brasileiro, com linguagem profissional,

clara, objetiva e natural.



REGRAS DE ANÁLISE:



1. Use os dados e os cálculos fornecidos no contexto como fonte

   oficial dos números. Nunca invente valores, datas ou produtos.



2. Responda primeiro à pergunta principal. Seja conciso e evite

   repetir a mesma conclusão em diferentes seções.



3. Apresente apenas os indicadores relevantes para a pergunta.

   Não reproduza todo o contexto nem todos os rankings.



4. Diferencie fatos observados de interpretações e hipóteses.



5. Receita candidata não representa lucro nem receita líquida

   validada. Explique essa limitação quando for relevante.



6. Dezembro de 2011 é parcial, com dados somente até 9 de dezembro.

   Não o compare diretamente com meses completos.



7. Para variações mensais, utilize os cálculos do Python.

   Não recalcule nem contradiga os números fornecidos.



8. Para perguntas sobre contribuição por produto, use a seção

   "CONTRIBUIÇÃO POR PRODUTO ENTRE MESES", calculada pelo Python.



9. A variação total mensal e a variação individual de um produto

   são medidas diferentes. Não afirme que os produtos listados

   explicam toda a variação mensal sem comprovar isso.



10. Rankings gerais de produtos e clientes não demonstram as causas

    de uma mudança mensal.



11. Não afirme que promoções, marketing, sazonalidade ou outros

    fatores causaram uma variação sem evidências diretas.



12. Se os dados não forem suficientes, informe a limitação

    claramente. Não invente uma resposta.



FORMATO DA RESPOSTA:



- Comece com uma conclusão direta.

- Use de 1 a 3 tópicos com as evidências mais relevantes,

  quando isso ajudar.

- Inclua uma recomendação prática somente quando fizer sentido.

- Mencione limitações apenas quando forem importantes para a

  pergunta.

- Evite criar várias seções com informações repetidas.

- Prefira respostas curtas e específicas, sem perder o rigor.

"""



    try:

        context = build_ai_context()



        messages = [

            {

                "role": "system",

                "content": system_prompt + "\n\n" + context,

            }

        ]



        # Mantém somente as últimas mensagens para reduzir

        # o tamanho do histórico enviado ao modelo.

        messages.extend(st.session_state.ai_chat_history[-6:])



        with st.chat_message("assistant"):

            with st.spinner("Analisando os dados e os produtos..."):

                response = requests.post(

                    "http://localhost:11434/api/chat",

                    json={

                        "model": "llama3.2:3b",

                        "messages": messages,

                        "stream": False,

                        "options": {

                            "temperature": 0.1,

                            "num_predict": 500,

                        },

                    },

                    timeout=180,

                )



                response.raise_for_status()



                result = response.json()

                answer = result["message"]["content"].strip()



                if not answer:

                    answer = (

                        "A IA não retornou uma resposta. "

                        "Tente reformular sua pergunta."

                    )



            st.markdown(answer)



        st.session_state.ai_chat_history.append(

            {"role": "assistant", "content": answer}

        )



    except requests.exceptions.ConnectionError:

        st.error(

            "Não consegui conectar ao Ollama. "

            "Verifique se o aplicativo está aberto "

            "e se o modelo está disponível."

        )



        # Remove a pergunta sem resposta do histórico

        if (

            st.session_state.ai_chat_history

            and st.session_state.ai_chat_history[-1]["role"] == "user"

        ):

            st.session_state.ai_chat_history.pop()



    except requests.exceptions.Timeout:

        st.error(

            "A análise demorou mais que o esperado. "

            "Tente novamente com uma pergunta mais específica."

        )



        if (

            st.session_state.ai_chat_history

            and st.session_state.ai_chat_history[-1]["role"] == "user"

        ):

            st.session_state.ai_chat_history.pop()



    except requests.exceptions.RequestException as error:

        st.error(f"Erro ao consultar o Ollama: {error}")



        if (

            st.session_state.ai_chat_history

            and st.session_state.ai_chat_history[-1]["role"] == "user"

        ):

            st.session_state.ai_chat_history.pop()



    except (KeyError, ValueError) as error:

        st.error(

            "A resposta recebida do Ollama não estava no formato "

            f"esperado. Detalhes: {error}"

        )



        if (

            st.session_state.ai_chat_history

            and st.session_state.ai_chat_history[-1]["role"] == "user"

        ):

            st.session_state.ai_chat_history.pop()



    except Exception as error:

        st.error(

            "Não foi possível preparar a análise. "

            f"Detalhes: {error}"

        )



        if (

            st.session_state.ai_chat_history

            and st.session_state.ai_chat_history[-1]["role"] == "user"

        ):

            st.session_state.ai_chat_history.pop()



if st.session_state.ai_chat_history:

    if st.button(

        "Limpar conversa com a IA",

        key="clear_ai_chat",

    ):

        st.session_state.ai_chat_history = []

        st.rerun()





# ============================================================

# FOOTER

# ============================================================



st.divider()



footer_left, footer_right = st.columns([3, 1])



with footer_left:

    st.markdown(

        '<p class="small-note">'

        "AI-Powered Business Intelligence · Projeto de portfólio · "

        "Fonte: UCI Online Retail · Valores em GBP (£)"

        "</p>",

        unsafe_allow_html=True,

    )



with footer_right:

    st.markdown(

        '<p class="small-note" style="text-align:right;">'

        "Desenvolvido com Python, Streamlit e Plotly"

        "</p>",

        unsafe_allow_html=True,

    )
