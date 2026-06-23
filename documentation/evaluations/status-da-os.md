# Status da Ordem de Serviço

## Objetivo

O status da Ordem de Serviço deve representar automaticamente a situação real da execução operacional.

A atualização segue o fluxo documentado em `documentation/flows/propagacao-de-status.md`:

```txt
Tarefa -> Serviço -> Ordem de Serviço
```

## Regra da Ordem de Serviço

O status da Ordem de Serviço é gerenciado pelo sistema e calculado a partir dos status dos serviços relacionados.

Estados previstos:

```txt
Aberta
Em Andamento
Concluída
Cancelada
```

Regras:

* Se a OS estiver cancelada, o status não deve ser alterado automaticamente pela propagação.
* Se todos os serviços estiverem concluídos, a OS deve ficar concluída.
* Se houver ao menos um serviço em andamento ou concluído, mas nem todos estiverem concluídos, a OS deve ficar em andamento.
* Se não houver execução iniciada, a OS deve ficar aberta.

## Cancelamento

O cancelamento não é propagado automaticamente.

Cancelar tarefa não cancela serviço.
Cancelar serviço não cancela OS.
Cancelar OS deve ser ação explícita de usuário autorizado.

## Campo legado de conclusão

O campo `concluida` continua existindo como compatibilidade operacional e deve ser sincronizado com o status:

* `concluida = True` quando `status = concluida`
* `concluida = False` nos demais status

## Campos gerenciados pelo sistema

Os seguintes campos não devem ser editados manualmente pelo usuário:

* `status`
* `concluida`

