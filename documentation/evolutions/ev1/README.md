# EV1 - Evolucoes do sistema de OS

## Escopo global

A EV1 organiza melhorias operacionais do sistema interno da Ergogroup para Ordem de Servico, Servico, Tarefa e MiniOS / OS Operacional.

O objetivo desta evolucao e melhorar rastreabilidade, cobranca, auditoria, contratos e catalogo sem propor uma refatoracao estrutural ampla do backend ou do frontend.

## Premissas

- O sistema e interno da Ergogroup e deve atender as necessidades operacionais atuais.
- Campos derivados de execucao devem ser gerenciados pelo sistema, nao preenchidos manualmente pelo usuario.
- A evolucao deve preservar compatibilidade com dados legados sempre que possivel.
- Quando nao houver historico completo no legado, a primeira migracao deve criar uma base inicial util a partir dos dados existentes.

## Evolucoes documentadas

1. [Status da OS](01-status-da-os.md)
2. [Prioridade da OS](02-prioridade-da-os.md)
3. [Rastreabilidade de datas](03-rastreabilidade-datas.md)
4. [Melhoria no sistema de cobranca](04-melhoria-cobranca.md)
5. [Contratos e notificacoes](05-contratos-notificacoes.md)
6. [Auditoria operacional](06-auditoria.md)
7. [Subitens do catalogo comum](07-subitens-catalogo.md)

## Evolucoes mapeadas para a EV1

Tambem fazem parte do escopo funcional mapeado para a EV1:

- Indicadores e BI.
- Visualizacao consolidada de Ordem de Servico, Servicos e Tarefas em uma pagina.
- MiniOS exibida no frontend como OS Operacional.

Esses itens devem receber documentos numerados proprios quando forem detalhados para implementacao.
