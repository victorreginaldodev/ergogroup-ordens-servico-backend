# EV2 - Evolucoes do sistema de OS

## Escopo global

A EV2 expande o modelo de dados de Ordem de Servico, Servico e Tarefa com novos atributos operacionais, de controle e de analytics que nao existiam no sistema legado.

Esta evolucao e independente da refatoracao estrutural que unifica os apps legados (`ordem_servico`, `servicos`, `tarefas`) em `apps/ordens_servico`. A ev2 trata exclusivamente dos novos campos e regras de dominio.

## Premissas

- Novos campos de rastreabilidade de datas sao gerenciados pelo sistema, nunca preenchidos manualmente pelo usuario.
- O tecnico nao pode declarar quando iniciou ou concluiu uma demanda — o sistema registra o momento exato da transicao de status.
- Campos de qualidade e controle operacional ampliam a capacidade de analytics sem alterar o fluxo principal de execucao.
- Campos de auditoria sao expandidos em todas as entidades.

## Evolucoes detalhadas em arquivos

1. [Numero da OS](01-numero-os.md)
2. [Datas gerenciadas pelo sistema](02-datas-sistema.md)
3. [Controle operacional da OS](03-controle-os.md)
4. [Qualidade e pos-servico](04-qualidade-os.md)
5. [Cobranca — data acordada de pagamento](05-cobranca-data-acordada.md)
6. [Evolucao do Servico](06-evolucao-servico.md)
7. [Evolucao da Tarefa](07-evolucao-tarefa.md)
8. [Atribuicao da Tarefa](08-atribuicao-tarefa.md)
