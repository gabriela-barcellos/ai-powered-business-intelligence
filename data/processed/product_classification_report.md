# Classificação e Análise de Produtos

## Objetivo

Separar candidatos a mercadoria de serviços de postagem e
itens que precisam de revisão, mantendo a rastreabilidade dos dados.

## Escopo da análise

- Linhas selecionadas como vendas candidatas: 524,877
- Linhas consideradas nesta análise: 524,877
- Linhas excluídas por dados inválidos: 0
- Códigos de produto distintos: 3,921

## Totais de origem considerados

- Receita candidata: £10,631,048.74
- Quantidade candidata: 5,572,419

## Categorias

- Candidatos a mercadoria: 522,571 linhas
- Serviços de postagem: 1,973 linhas
- Itens especiais para revisão: 333 linhas

## Regras de classificação

1. `service_postage`: códigos DOT e POST, descrições conhecidas de postagem ou descrições contendo POSTAGE.
2. `special_item_review`: código M e descrições conhecidas de taxas, comissões, ajustes ou itens que precisam de revisão.
3. `merchandise_candidate`: demais registros, mantidos como candidatos a mercadoria.

## Principais resultados

### Maior receita entre candidatos a mercadoria

22423 — REGENCY CAKESTAND 3 TIER

Receita candidata: £174,156.54

### Maior quantidade entre candidatos a mercadoria

23843 — PAPER CRAFT , LITTLE BIRDIE

Quantidade candidata: 80,995

## Validação

- Diferença de receita após agregação: £0.00
- Diferença de quantidade após agregação: 0
- Totais preservados: Sim

## Limitações

- A classificação é baseada em regras explícitas e não substitui a validação de negócio.
- Os códigos M, DOT e POST foram tratados por regras específicas que devem ser revisadas.
- A categoria `merchandise_candidate` não garante que cada registro seja uma mercadoria comercial.
- Os rankings são preliminares e não devem ser tratados como indicadores oficiais sem validação adicional.
- A base original e a base processada não são alteradas por este script.
