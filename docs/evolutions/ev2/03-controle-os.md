# Controle Operacional da OS

## Objetivo

Adicionar campos que ampliam o controle interno de entrega e o ciclo de vida operacional da Ordem de Servico.

## Campos

### Responsavel interno

- `responsavel_interno`: ForeignKey ao usuario interno responsavel pela entrega da OS.

Diferente de `criado_por`, que registra quem abriu a OS, o `responsavel_interno` e o gestor ou lider tecnico que responde pela execucao perante o cliente.

Permite analytics de carga de trabalho por gestor e accountability de entrega.

### Data prevista de conclusao

- `data_prevista_conclusao`: DateField, prazo acordado internamente para conclusao da OS.

Habilita:
- Calculo de aderencia a prazo (SLA).
- Identificacao de OS atrasadas (data atual > data_prevista_conclusao e status != concluida).
- Alertas operacionais de vencimento.

Nao confundir com `data_acordada_pagamento`, que e o prazo de pagamento com o cliente.

### Data e responsavel de conclusao

- `data_conclusao`: DateField, preenchido pelo sistema quando a OS atinge o status `concluida`.
- `concluida_por`: ForeignKey ao usuario responsavel pela conclusao (derivado do responsavel da ultima tarefa do ultimo servico concluido).

Esses campos sao gerenciados pelo sistema, nao editaveis pelo usuario.

### Motivo de cancelamento

- `motivo_cancelamento`: TextField, obrigatorio quando o status da OS e alterado para `cancelada`.

Sem esse campo, cancelamentos sao estados finais sem contexto. O campo e essencial para analytics de qualidade e para entender padroes de perda.

## Regras

- `data_prevista_conclusao` pode ser alterada pelo usuario enquanto a OS nao estiver concluida ou cancelada.
- `data_conclusao` e `concluida_por` sao preenchidos automaticamente e nao podem ser editados.
- `motivo_cancelamento` e nulo enquanto a OS nao for cancelada.

## Migracao inicial

- `responsavel_interno`: nulo para todas as OS existentes.
- `data_prevista_conclusao`: nulo para todas as OS existentes.
- `data_conclusao`: populado com `Max(Servico.concluido_em).date()` para OS com `status = concluida`.
- `concluida_por`: nulo para OS existentes (dado nao disponivel no legado).
- `motivo_cancelamento`: nulo para todas as OS existentes.
