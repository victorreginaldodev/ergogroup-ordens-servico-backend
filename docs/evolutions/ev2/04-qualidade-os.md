# Qualidade e Pos-servico

## Objetivo

Registrar indicadores de qualidade percebida e de retrabalho para compor analytics de satisfacao e de eficiencia operacional.

## Campos

### Avaliacao do cliente

- `avaliacao_cliente`: inteiro de 1 a 10, preenchido apos a conclusao da OS.

Representa o CSAT (Customer Satisfaction Score) coletado apos a entrega. E o unico indicador que fecha o ciclo de qualidade percebida pelo cliente.

Habilita:
- Media de satisfacao por cliente, tecnico, tipo de servico e periodo.
- Identificacao de padroes de insatisfacao.

Regras:
- Valor valido entre 1 e 10.
- Preenchimento opcional e manual — nao e gerado pelo sistema.
- Pode ser preenchido apenas quando a OS estiver concluida.

### Retrabalho

- `retrabalho`: BooleanField, indica que esta OS foi originada por falha em uma OS anterior.
- `os_origem`: ForeignKey para outra OS, identifica de qual OS a falha se originou.

`os_origem` e opcional mesmo quando `retrabalho = True`. Nem sempre e possivel rastrear a OS original.

Habilita:
- Taxa de retrabalho por periodo, cliente, tecnico e tipo de servico.
- Custo de retrabalho (soma de valores de OS com `retrabalho = True`).
- Identificacao de tecnicos com maior indice de retrabalho.

Regras:
- `retrabalho = False` por padrao para todas as novas OS.
- `os_origem` so faz sentido quando `retrabalho = True`. Se `retrabalho = False`, `os_origem` deve ser nulo.

## Migracao inicial

- `avaliacao_cliente`: nulo para todas as OS existentes.
- `retrabalho`: `False` para todas as OS existentes.
- `os_origem`: nulo para todas as OS existentes.
