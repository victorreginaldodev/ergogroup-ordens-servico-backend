# Evolucao da Tarefa

## Objetivo

Ampliar a Tarefa com controle de prazo, prioridade, tempo e motivo de cancelamento.

## Novos campos

### Prioridade

- `prioridade`: TextChoices com quatro niveis — `baixa`, `media`, `alta`, `urgente`.

A OS ja possui prioridade. A prioridade da Tarefa e independente e representa a urgencia de execucao individual dentro de um servico.

Padrao: `baixa`.

### Prazo

- `prazo`: DateField, deadline individual da tarefa.

A OS tem `data_prevista_conclusao`. Tarefas dentro de um mesmo servico podem ter prazos distintos — entregas parciais, dependencias externas ou fases da execucao.

Preenchimento manual e opcional.

### Horas

- `horas_estimadas`: DecimalField, estimativa de horas para a tarefa.
- `horas_realizadas`: DecimalField, horas efetivamente trabalhadas.

No nivel mais granular da execucao. Permitem calculo de produtividade por tecnico e precisao de estimativas por tipo de tarefa.

Preenchimento manual pelo tecnico responsavel.

### Motivo de cancelamento

- `motivo_cancelamento`: TextField, contexto do cancelamento da tarefa.

Consistente com OS e Servico. Complementa a taxa de cancelamento de tarefas com a causa raiz.

## Migracao inicial

- `prioridade`: `baixa` para todas as tarefas existentes.
- `prazo`: nulo para todas as tarefas existentes.
- `horas_estimadas`, `horas_realizadas`: nulo para todas.
- `motivo_cancelamento`: nulo para todas.
