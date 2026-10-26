# Auditoria da Classificação de Produtos

## Escopo

- Linhas consideradas: 524,877
- Linhas excluídas desta análise: 0
- Combinações de código, descrição e categoria: 4,157
- Códigos presentes em mais de uma categoria: 0

## Distribuição por categoria

| Categoria | Linhas | Códigos distintos | Receita | Quantidade |
|---|---:|---:|---:|---:|
| merchandise_candidate | 522,571 | 3,913 | £10,247,905.13 | 5,561,420 |
| service_postage | 1,973 | 3 | £291,401.65 | 3,998 |
| special_item_review | 333 | 5 | £91,741.96 | 7,001 |

## Validação dos totais

- Receita original da seleção: £10,631,048.74
- Receita auditada: £10,631,048.74
- Diferença de receita: £0.00
- Quantidade original da seleção: 5,572,419
- Quantidade auditada: 5,572,419
- Diferença de quantidade: 0
- Totais preservados: Sim

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
