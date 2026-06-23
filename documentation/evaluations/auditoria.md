# Auditoria

## Objetivo

Registrar os eventos críticos das principais entidades operacionais:

* Ordem de Serviço
* Serviço
* Tarefa
* MiniOS / OS Operacional

A auditoria deve permitir rastrear ações humanas, efeitos automáticos do sistema e uma linha base inicial criada a partir dos dados existentes.

## Entidades auditadas

### Ordem de Serviço

Eventos críticos:

* Criação
* Atualização de dados comerciais
* Alteração de prioridade
* Mudança e propagação de status
* Liberação para faturamento
* Faturamento
* Dados de contrato
* Exclusão

### Serviço

Eventos críticos:

* Criação
* Atualização de descrição/repositório
* Mudança e propagação de status a partir das tarefas
* Início e término inferidos pelas tarefas
* Usuário que terminou o serviço
* Exclusão

### Tarefa

Eventos críticos:

* Criação
* Alteração de responsável, descrição ou serviço
* Mudança de status
* Início e término automáticos
* Exclusão

### MiniOS / OS Operacional

Eventos críticos:

* Criação
* Alteração de cliente, serviço, responsável, quantidade ou descrição
* Mudança de status
* Início e término automáticos
* Revisão do cliente e geração de cobrança
* Liberação de cobrança
* Faturamento
* Exclusão

## Modelo

A auditoria usa uma model genérica `RegistroAuditoria`, com:

* Entidade auditada
* ID do objeto
* Representação textual do objeto
* Ação
* Origem
* Motivo
* Usuário
* Alterações antes/depois em JSON
* Snapshot do objeto em JSON
* IDs auxiliares para timeline de OS, Serviço, Tarefa e MiniOS
* Dados da requisição, quando disponíveis

## Backfill inicial

Como o sistema não possuía auditoria completa, a população inicial é parcial e inferida.

Os registros criados pela migration de backfill usam:

```txt
origem = migracao
acao = backfill ou ação inferida
motivo = Evento inferido a partir do estado atual do sistema. Histórico detalhado anterior indisponível.
```

Esse backfill cria:

* Um snapshot inicial de cada OS, Serviço, Tarefa e MiniOS.
* Eventos inferidos de conclusão/status quando há status ou datas compatíveis.
* Eventos inferidos de liberação de faturamento.
* Eventos inferidos de faturamento.
* Eventos inferidos de contrato.
* Eventos inferidos de liberação de cobrança da MiniOS.

## Limitação conhecida

O backfill não reconstrói o histórico real anterior.

Ele cria uma linha base útil para consulta e BI, e a partir da implantação da auditoria os novos eventos passam a ser registrados com antes/depois real.

