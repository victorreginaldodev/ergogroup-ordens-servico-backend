# Prioridade da Ordem de Serviço

## Objetivo

A prioridade é um atributo de negócio da Ordem de Serviço usado para organização operacional.

## Estados

Estados previstos:

```txt
Baixa
Média
Alta
```

## Regra inicial

Como o sistema não possuía esse atributo antes, todas as Ordens de Serviço existentes devem ser migradas com prioridade baixa.

Novas Ordens de Serviço também devem nascer com prioridade baixa quando nenhum valor for informado.

## Edição

Diferente dos campos derivados de execução, a prioridade pode ser alterada pelo usuário.

Ela representa uma decisão operacional humana, não uma consequência automática das tarefas ou serviços.

