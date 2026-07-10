# Datas Gerenciadas pelo Sistema

## Objetivo

Eliminar a possibilidade de o usuario declarar manualmente quando iniciou ou concluiu uma demanda.

No modelo legado, `data_inicio` e `data_termino` eram DateFields que podiam ser preenchidos ou alterados livremente, criando um vetor de fraude: um tecnico podia registrar conclusao com data retroativa.

A EV2 substitui esses campos por DateTimeFields preenchidos automaticamente pelo sistema no momento exato da transicao de status.

## Servico

Campos removidos:
- `data_inicio` (DateField derivado das tarefas)
- `data_termino` (DateField derivado das tarefas)
- `data_conclusao` (DateField, compatibilidade com data_termino)

Campos introduzidos:
- `iniciado_em`: DateTimeField, preenchido pelo sistema quando o status transita para `em_andamento`.
- `iniciado_por`: ForeignKey ao usuario que realizou a transicao.
- `concluido_em`: DateTimeField, preenchido pelo sistema quando todos os servicos ficam concluidos.
- `concluido_por`: ForeignKey ao usuario responsavel pela conclusao (herdado da ultima tarefa concluida).

## Tarefa

Campos removidos:
- `data_inicio` (DateField, auto-setado na transicao de status)
- `data_termino` (DateField, auto-setado na conclusao)

Campos introduzidos:
- `iniciado_em`: DateTimeField, preenchido pelo sistema quando o status transita para `em_andamento`.
- `concluido_em`: DateTimeField, preenchido pelo sistema quando o status transita para `concluida`.

Regras de automacao (Tarefa):
- `iniciado_em` e preenchido no primeiro save com status `em_andamento` ou `concluida`, quando ainda for nulo.
- `concluido_em` e preenchido no primeiro save com status `concluida`, quando ainda for nulo.
- `concluido_em` e zerado automaticamente quando o status sai de `concluida`.

## Impacto em analytics

Campos de analytics que dependiam de `data_inicio` e `data_termino` no Servico devem ser atualizados para usar `iniciado_em` e `concluido_em`.

Para calculos que necessitam apenas da data (sem hora), usar `.date()` sobre o DateTimeField.

## Migracao inicial

- `iniciado_em` do Servico: populado com `data_inicio` existente convertida para datetime com hora `00:00:00` no fuso local.
- `concluido_em` do Servico: populado com `data_termino` existente convertida da mesma forma.
- `iniciado_em` da Tarefa: populado com `data_inicio` existente.
- `concluido_em` da Tarefa: populado com `data_termino` existente.
- Quando o campo legado for nulo, o campo novo permanece nulo.
