# Cobranca — Data Acordada de Pagamento

## Objetivo

Registrar a data acordada com o cliente para o pagamento da OS.

## Contexto

A Ordem de Servico ja possui dois marcos temporais de cobranca:

- `liberada_para_cobranca_em`: quando a OS ficou liberada para emissao de nota.
- `data_cobranca`: quando a cobranca foi efetivamente realizada (nota emitida).

O campo `data_acordada_pagamento` e distinto dos dois anteriores. Representa o prazo combinado com o cliente para que o pagamento seja efetuado — informacao comercial de controle de recebimento.

## Campo

- `data_acordada_pagamento`: DateField, data de vencimento acordada com o cliente para pagamento.

## Regras

- Preenchimento manual e opcional.
- Nao e gerenciado pelo sistema — representa uma combinacao comercial.
- Nao confundir com `data_cobranca` (quando a nota foi emitida) nem com `data_prevista_conclusao` (quando o servico deve ser entregue).

## Migracao inicial

Nulo para todas as OS existentes — dado nao disponivel no legado.
