# Customer Analysis Summary

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

- Clientes identificados: 4,338
- Receita bruta candidata: £8,887,208.89
- Quantidade total de itens: 5,152,002
- Receita média por cliente: £2,048.69
- Pedidos médios por cliente: 4.27
- Receita média por pedido: £479.56

## Top 10 clientes por receita

|   RevenueRank |   CustomerID |   TotalRevenue |   TotalOrders |   TotalQuantity |
|--------------:|-------------:|---------------:|--------------:|----------------:|
|             1 |        14646 |       280206   |            73 |          196915 |
|             2 |        18102 |       259657   |            60 |           64124 |
|             3 |        17450 |       194391   |            46 |           69973 |
|             4 |        16446 |       168472   |             2 |           80997 |
|             5 |        14911 |       143711   |           201 |           80240 |
|             6 |        12415 |       124915   |            21 |           77374 |
|             7 |        14156 |       117210   |            55 |           57768 |
|             8 |        17511 |        91062.4 |            31 |           64549 |
|             9 |        16029 |        80850.8 |            63 |           40108 |
|            10 |        12346 |        77183.6 |             1 |           74215 |

## Top 10 clientes por frequência de pedidos

|   FrequencyRank |   CustomerID |   TotalOrders |   TotalRevenue |   TotalQuantity |
|----------------:|-------------:|--------------:|---------------:|----------------:|
|               1 |        12748 |           209 |        33053.2 |           25287 |
|               2 |        14911 |           201 |       143711   |           80240 |
|               3 |        17841 |           124 |        40519.8 |           22834 |
|               4 |        13089 |            97 |        58762.1 |           31025 |
|               5 |        14606 |            93 |        12076.1 |            6187 |
|               6 |        15311 |            91 |        60632.8 |           38147 |
|               7 |        12971 |            86 |        11189.9 |            9289 |
|               8 |        14646 |            73 |       280206   |          196915 |
|               9 |        16029 |            63 |        80850.8 |           40108 |
|              10 |        13408 |            62 |        28117   |           16232 |

## Top 10 clientes por quantidade de itens

|   QuantityRank |   CustomerID |   TotalQuantity |   TotalOrders |   TotalRevenue |
|---------------:|-------------:|----------------:|--------------:|---------------:|
|              1 |        14646 |          196915 |            73 |       280206   |
|              2 |        16446 |           80997 |             2 |       168472   |
|              3 |        14911 |           80240 |           201 |       143711   |
|              4 |        12415 |           77374 |            21 |       124915   |
|              5 |        12346 |           74215 |             1 |        77183.6 |
|              6 |        17450 |           69973 |            46 |       194391   |
|              7 |        17511 |           64549 |            31 |        91062.4 |
|              8 |        18102 |           64124 |            60 |       259657   |
|              9 |        13694 |           63312 |            50 |        65039.6 |
|             10 |        14298 |           58343 |            44 |        51527.3 |

## Validação dos resultados

- Receita da base filtrada: £8,887,208.89
- Receita agregada por cliente: £8,887,208.89
- Diferença de receita: £-0.00
- Quantidade da base filtrada: 5,152,002
- Quantidade agregada: 5,152,002
- Diferença de quantidade: 0.000000
- Clientes únicos na base filtrada: 4,338
- Clientes únicos no resultado: 4,338
- Status: APROVADA

## Limitações

A análise considera somente vendas candidatas com cliente identificado.
Pedidos sem identificação de cliente não entram nos rankings. Os resultados
dependem das regras de classificação adotadas nas etapas anteriores.
