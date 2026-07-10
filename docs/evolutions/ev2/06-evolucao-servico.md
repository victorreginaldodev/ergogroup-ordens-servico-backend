# Evolucao do Servico

## Objetivo

Ampliar o Servico com campos de controle de tempo, progresso, contexto tecnico e rastreabilidade de quem iniciou a execucao.

## Novos campos

### Horas

- `horas_estimadas`: DecimalField, estimativa de horas necessarias para executar o servico.
- `horas_realizadas`: DecimalField, horas efetivamente trabalhadas no servico.

Habilitam:
- Comparativo estimado vs realizado por tipo de servico.
- Calculo de produtividade e margem operacional.
- Identificacao de servicos sistematicamente subestimados.

Preenchimento manual pelo usuario responsavel.

### Percentual de conclusao

- `percentual_conclusao`: inteiro de 0 a 100, progresso atual do servico.

Permite reporting de andamento sem depender de conclusao de tarefas. Util para servicos longos onde o cliente acompanha o progresso.

Preenchimento manual. Nao e derivado do progresso das tarefas.

### Equipamento

- `equipamento`: CharField, identificador do ativo ou equipamento atendido pelo servico.

Exemplos: numero de patrimonio, numero de serie, nome do equipamento.

Permite historico de atendimentos por ativo ao longo do tempo.

### Observacoes tecnicas

- `observacoes_tecnicas`: TextField, registro interno de diagnostico, condicoes encontradas e decisoes tecnicas.

Campo exclusivamente interno. Nao deve ser exibido ao cliente.

### Motivo de cancelamento

- `motivo_cancelamento`: TextField, contexto do cancelamento do servico.

Analogamente ao cancelamento da OS, registrar o motivo e essencial para analytics de qualidade.

### Iniciado por

- `iniciado_por`: ForeignKey ao usuario que transitou o servico para `em_andamento`.

Complementa `iniciado_em` com a identidade de quem iniciou a execucao. No modelo legado, apenas `terminado_por` existia — a EV2 simetriza o rastreio com `iniciado_por`.

### Auditoria expandida

- `criado_por`: ForeignKey ao usuario que criou o servico. Ausente no modelo legado.
- `atualizado_por`: ForeignKey ao ultimo usuario que atualizou o servico.

## Migracao inicial

- `horas_estimadas`, `horas_realizadas`: nulo para todos os servicos existentes.
- `percentual_conclusao`: 0 para servicos em aberto ou em andamento; 100 para servicos concluidos.
- `equipamento`, `observacoes_tecnicas`, `motivo_cancelamento`: nulo para todos.
- `iniciado_por`: nulo para todos os servicos existentes.
- `criado_por`, `atualizado_por`: nulo para todos os servicos existentes.
