# EV1 - Evolucoes do sistema de OS

## Escopo global

A EV1 organiza melhorias operacionais do sistema interno da Ergogroup para Ordem de Servico, Servico, Tarefa e MiniOS / OS Operacional.

O objetivo desta evolucao e melhorar rastreabilidade, cobranca, auditoria, contratos e catalogo sem propor uma refatoracao estrutural ampla do backend ou do frontend.

## Premissas

- O sistema e interno da Ergogroup e deve atender as necessidades operacionais atuais.
- Campos derivados de execucao devem ser gerenciados pelo sistema, nao preenchidos manualmente pelo usuario.
- A evolucao deve preservar compatibilidade com dados legados sempre que possivel.
- Quando nao houver historico completo no legado, a primeira migracao deve criar uma base inicial util a partir dos dados existentes.

## Evolucoes detalhadas em arquivos

1. [Status da OS](01-status-da-os.md)
2. [Prioridade da OS](02-prioridade-da-os.md)
3. [Rastreabilidade de datas](03-rastreabilidade-datas.md)
4. [Melhoria no sistema de cobranca](04-melhoria-cobranca.md)
5. [Contratos e notificacoes](05-contratos-notificacoes.md)
6. [Auditoria operacional](06-auditoria.md)
7. [Subitens do catalogo comum](07-subitens-catalogo.md)

## Evolucoes no escopo global

As melhorias abaixo tambem fazem parte da EV1, mas permanecem documentadas neste README ate receberem detalhamento proprio para implementacao.

### Indicadores e BI

Criar um modulo inteligente de indicadores para acompanhar a operacao, apoiar decisoes internas e dar visibilidade sobre produtividade, tempos medios e volume de visitas tecnicas.

Indicadores pedidos explicitamente:

- Analise individual de cada tecnico.
- Tempo medio entre a criacao e o encerramento de uma Ordem de Servico.
- Tempo medio entre o inicio e o fim de um Servico especifico.
- Quantidade de visitas tecnicas por mes em OS ou OS Operacional.
- Analise tecnica dos indicadores.

### Pagina consolidada de OS, Servicos e Tarefas

Unir as informacoes de Ordem de Servico, Servicos e Tarefas em uma unica pagina operacional, de forma organizada e adequada ao fluxo de trabalho do time.

A pagina deve permitir visualizar:

- Dados principais da Ordem de Servico.
- Servicos relacionados.
- Tarefas de cada servico.
- Status propagado da execucao.
- Datas de rastreabilidade.
- Informacoes de cobranca permitidas ao perfil do usuario.

Restricoes de acesso:

- Usuarios nao autorizados nao devem atualizar tarefas que nao sao deles.
- Usuarios sem permissao nao devem criar novas tarefas.
- Usuarios sem permissao nao devem visualizar dados financeiros.

### MiniOS como OS Operacional

Alterar a nomenclatura de negocio exibida ao usuario para que MiniOS / OS Rapida seja tratada como OS Operacional.

Escopo:

- Exibir `MiniOS` como `OS Operacional`.
- Evitar o termo `OS Rapida` na interface.
- Manter compatibilidade tecnica com models e endpoints existentes enquanto nao houver refatoracao estrutural.
