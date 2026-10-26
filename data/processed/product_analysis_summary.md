# Análise de Produtos

## Escopo

A análise considera registros classificados como
`standard_sales_candidate` na base processada.

Os resultados são preliminares e dependem da validação
das regras de negócio.

## Cobertura

- Linhas consideradas: 524,877
- Produtos identificados: 3,921
- Receita candidata agregada: £10,631,048.74
- Quantidade candidata agregada: 5,572,419

## Destaques

- Produto com maior receita candidata: DOT — DOTCOM POSTAGE
- Receita candidata desse produto: £206,248.77
- Produto com maior quantidade candidata: 23843 — PAPER CRAFT , LITTLE BIRDIE
- Quantidade candidata desse produto: 80,995

## Validação

- Totais agregados preservados: Sim

## Limitações

- Os resultados dependem da classificação das transações na etapa de preparação.
- O código do produto (`StockCode`) é usado como identificador principal.
- Descrições podem variar entre registros do mesmo código.
- Quantidade vendida e receita candidata são métricas diferentes.
- Os resultados não devem ser interpretados como indicadores oficiais
  sem validação das regras de negócio.
