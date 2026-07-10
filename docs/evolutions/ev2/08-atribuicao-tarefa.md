# Atribuicao da Tarefa

## Objetivo

Registrar com clareza de dominio quem atribuiu a tarefa e quem realizou a ultima atualizacao operacional.

## Contexto

No modelo legado, a Tarefa possuia apenas `criada_em` e `atualizado_em`. Nao havia registro de quem atribuiu nem de quem atualizou.

A EV2 distingue dois papeis distintos:

- Quem atribui a tarefa (papel gerencial — define responsavel e descricao).
- Quem atualizou por ultimo (pode ser gestor atualizando a atribuicao ou tecnico atualizando o status).

## Campos

### Atribuicao

- `atribuido_em`: DateTimeField com `auto_now_add=True`, registrado pelo sistema no momento da criacao.
- `atribuido_por`: ForeignKey ao usuario que criou e atribuiu a tarefa.

O nome `atribuido_por` e preferido a `criado_por` porque a criacao e a atribuicao sao sempre uma acao atomica no fluxo atual do sistema. O nome de dominio reflete a intencao da acao, nao apenas o fato tecnico de ter criado o registro.

Caso o sistema evolua para suportar tarefas criadas sem responsavel definido, um campo `criado_por` separado pode ser introduzido. Por ora, uma unica FK e suficiente.

### Atualizacao

- `atualizado_em`: DateTimeField com `auto_now=True`.
- `atualizado_por`: ForeignKey ao ultimo usuario que salvou qualquer campo da tarefa.

`atualizado_por` registra o ultimo update independente do que foi alterado — atribuicao, descricao ou status. A distincao entre "gestor atualizou a atribuicao" e "tecnico atualizou o status" nao e capturada em campos da model; ela pertence ao log de auditoria (`RegistroAuditoria`), que registra antes/depois por campo.

## Migracao inicial

- `atribuido_em`: populado com `criada_em` existente.
- `atribuido_por`: nulo para todas as tarefas existentes.
- `atualizado_por`: nulo para todas as tarefas existentes.
