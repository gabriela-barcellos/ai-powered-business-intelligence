# Customer Retention & Behavior Analysis

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

- Clientes únicos: 4,338
- Soma de clientes ativos por mês (cliente-mês): 13,054
- Receita da base: £8,887,208.89
- Receita mensal agregada: £8,887,208.89
- Diferença de receita: £-0.00
- Quantidade da base: 5,152,002
- Quantidade mensal agregada: 5,152,002
- Diferença de quantidade: 0.000000
- Novos + recorrentes = ativos em todos os meses: True
- Taxas de retenção conferem com a fórmula: True
- Valores ausentes de retenção são válidos: True
- Validação de retenção aprovada: True
- Status geral: APROVADA

## Indicadores mensais

```text
InvoiceMonth  ActiveCustomers  NewCustomers  ReturningCustomers  ReturningCustomerRate  NextMonthRetainedCustomers  NextMonthRetentionRate  Orders  Quantity     Revenue
     2010-12              885           885                   0               0.000000                         324               36.610169    1400    311048  570422.730
     2011-01              741           417                 324              43.724696                         262               35.357625     987    348473  568101.310
     2011-02              758           380                 378              49.868074                         290               38.258575     997    265027  446084.920
     2011-03              974           452                 522              53.593429                         304               31.211499    1321    347582  594081.760
     2011-04              856           300                 556              64.953271                         368               42.990654    1149    291366  468374.331
     2011-05             1056           284                 772              73.106061                         410               38.825758    1555    372864  677355.150
     2011-06              991           242                 749              75.580222                         365               36.831483    1393    363014  660046.050
     2011-07              949           188                 761              80.189673                         388               40.885142    1331    367360  598962.901
     2011-08              935           169                 766              81.925134                         425               45.454545    1280    397373  644051.040
     2011-09             1266           299                 967              76.382306                         489               38.625592    1755    543652  950690.202
     2011-10             1364           358                1006              73.753666                         622               45.601173    1929    591543 1035642.450
     2011-11             1664           323                1341              80.588942                         371               22.295673    2657    665923 1156205.610
     2011-12              615            41                 574              93.333333                           0                     NaN     778    286777  517190.440
```

## Primeiras 20 linhas da análise de coortes

```text
CohortMonth  CohortAge  CohortSize  ActiveCustomers  RetentionRate
    2010-12          0         885              885     100.000000
    2010-12          1         885              324      36.610169
    2010-12          2         885              286      32.316384
    2010-12          3         885              340      38.418079
    2010-12          4         885              321      36.271186
    2010-12          5         885              352      39.774011
    2010-12          6         885              321      36.271186
    2010-12          7         885              309      34.915254
    2010-12          8         885              313      35.367232
    2010-12          9         885              350      39.548023
    2010-12         10         885              331      37.401130
    2010-12         11         885              445      50.282486
    2010-12         12         885              235      26.553672
    2011-01          0         417              417     100.000000
    2011-01          1         417               92      22.062350
    2011-01          2         417              111      26.618705
    2011-01          3         417               96      23.021583
    2011-01          4         417              134      32.134293
    2011-01          5         417              120      28.776978
    2011-01          6         417              103      24.700240
```

## Limitações

A primeira compra representa a primeira ocorrência do cliente dentro do período
disponível na base, não necessariamente sua primeira compra real na empresa.

O último mês disponível não possui um mês seguinte completo para calcular
retenção. Além disso, clientes ativos em meses diferentes podem se repetir;
por isso, a soma de clientes ativos por mês não representa clientes únicos
no período inteiro.
