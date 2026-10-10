# Decisões de arquitetura e de domínio (ADR)

Cada ADR registra uma decisão, o contexto em que foi tomada, as alternativas descartadas e as consequências. Decisões substituídas continuam aqui, marcadas como tal, para preservar o histórico.

| ADR | Decisão | Status |
|---|---|---|
| [0001](0001-catalogo-sem-atributos-de-hora-estimada.md) | Catálogo sem atributos de horas estimadas/complexidade | Substituído pelos ADRs 0004 e 0005 |
| [0002](0002-bloqueio-de-exclusao-em-cascata.md) | Bloqueio de exclusão em cascata | Aceito e implementado |
| [0003](0003-setores-funcoes-e-permissoes-configuraveis.md) | Setores, funções e permissões configuráveis | Aceito; backend implementado |
| [0004](0004-setor-responsavel-pela-execucao.md) | Setor responsável pela execução e catálogo | Aceito e implementado |
| [0005](0005-prazo-como-unico-parametro-de-planejamento.md) | Prazo como único parâmetro de planejamento | Aceito; implementação pendente |
| [0006](0006-fluxo-de-execucao-nos-setores.md) | Fluxo de execução nos setores | Parcialmente aceito (visões e telas a definir); implementação pendente |
| [0007](0007-papel-do-sistema-no-faturamento.md) | Papel do sistema no faturamento | Parcialmente aceito; mudanças no modelo em proposta, sem implementar |

Documentos relacionados:
- `docs/conceitos-de-dominio.md` — glossário do domínio.
- `docs/telas-blocos-e-endpoints.md` — telas, blocos de informação, quem vê o quê (permissões) e endpoints candidatos.
- `docs/mapa-de-permissoes.md` — o que cada permissão libera e as regras do frontend.
- `docs/plano-setores-e-permissoes.md` — plano de implementação por fases.
- `docs/briefing-sprint-setores.md` e `docs/as-is/` — o problema original e o sistema antes da sprint.
- `docs/faturamento/01-condicoes-de-pagamento-as-is.md` — condições de pagamento: o que o sistema faz hoje e como o negócio realmente cobra.
