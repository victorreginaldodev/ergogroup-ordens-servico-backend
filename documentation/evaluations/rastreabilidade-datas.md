# Rastreabilidade de Datas

## Objetivo

As models principais precisam registrar datas operacionais criadas pelo sistema, sem depender de preenchimento manual pelo usuário.

Models cobertas:

* Ordem de Serviço
* Serviço
* Tarefa
* MiniOS / OS Operacional

## Ordem de Serviço

Campos:

* `data_criacao`: data comercial/operacional da OS, mantida por compatibilidade.
* `criada_em`: data e hora real de criação no sistema.
* `data_atualizacao`: data e hora da última atualização.

Migração inicial:

* `criada_em` deve ser populada com `data_criacao`.
* Quando não houver referência confiável, usar a data/hora da migração como fallback.

## Serviço

Campos:

* `data_inicio`: primeira data de início entre as tarefas relacionadas.
* `data_termino`: data de conclusão da última tarefa concluída quando todas as tarefas estiverem concluídas.
* `data_conclusao`: mantida por compatibilidade, sincronizada com `data_termino`.
* `criado_em`: data e hora estimada da criação do serviço.
* `atualizado_em`: data e hora da última atualização.

Migração inicial:

* `data_inicio` vem da menor `data_inicio` das tarefas.
* `data_termino` vem da `data_conclusao` existente ou da última `data_termino` das tarefas concluídas.
* `criado_em` vem da primeira data conhecida do serviço, com fallback para a data da OS.

## Tarefa

Campos:

* `data_inicio`: preenchida automaticamente quando a tarefa entra em andamento.
* `data_termino`: preenchida automaticamente quando a tarefa é concluída.
* `criada_em`: data e hora estimada da criação da tarefa.
* `atualizado_em`: data e hora da última atualização.

Não há campo `concluida_por`, porque a tarefa pertence a um único responsável e somente ele deve concluir a tarefa.

Migração inicial:

* `criada_em` vem de `data_inicio`, depois `data_termino`, depois `data_criacao` da OS relacionada.
* Quando não houver referência confiável, usar a data/hora da migração como fallback.

## MiniOS / OS Operacional

Campos:

* `data_recebimento`: data operacional recebida do processo atual.
* `data_inicio`: preenchida automaticamente quando a OS Operacional entra em andamento.
* `data_termino`: preenchida automaticamente quando a OS Operacional é finalizada.
* `criada_em`: data e hora estimada da criação no sistema.
* `atualizado_em`: data e hora da última atualização.

Não há campo `concluida_por`, porque a MiniOS / OS Operacional possui um único responsável.

Migração inicial:

* `criada_em` vem de `data_recebimento`, depois `data_inicio`, depois `data_termino`.
* Quando não houver referência confiável, usar a data/hora da migração como fallback.

