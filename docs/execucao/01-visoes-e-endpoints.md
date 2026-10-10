# Visões de trabalho e endpoints da operação

> **Status (10/10/2026): proposta, a confirmar.** Nada aqui foi aprovado nem implementado. O documento detalha a seção 10 do ADR 0006 (blocos de informação) em endpoints concretos e propõe as visões de cada pessoa (seção 8, ainda não decidida). O que já está **aceito** nos ADRs aparece marcado como tal.
>
> **Fora de escopo:** organização, setores, funções, usuários e catálogo (já prontos) e a OS operacional.

## 1. Princípios

| # | Princípio | Origem |
|---|---|---|
| 1 | **Um bloco de informação = um endpoint.** O frontend compõe as páginas livremente; cada bloco carrega e atualiza sozinho. | ADR 0006, seção 10 (proposta) |
| 2 | **Cada endpoint declara a permissão que exige.** Nunca testa nome de função, de setor ou de cargo. | ADR 0003 (aceito) |
| 3 | **Nada depende de um setor específico.** Os endpoints de execução recebem o setor como parâmetro. Um setor novo (ex.: Ergonomia) passa a ter fila, painel e equipe assim que um catálogo apontar para ele e alguém tiver uma função com as permissões nele. Nenhuma linha de código muda. | ADRs 0004 e 0006, seção 2 (aceito) |
| 4 | **A unidade de trabalho do setor é o serviço;** a OS é a visão do Comercial e do Financeiro. | ADR 0006, seção 3 (aceito) |
| 5 | **As listagens atuais continuam** (`/ordens/`, `/servicos/`, `/tarefas/`). Os endpoints novos são leituras orientadas à tela, com os campos já calculados. | ADR 0006, consequências |
| 6 | **Lógica em `services/`.** Cálculos de etapa, prazo, carga e parado ficam em `apps/ordens_servico/services/execucao.py`, reaproveitados pelos endpoints e pelos e-mails. | Regra do projeto |
| 7 | **Sem horas nem complexidade.** Só prazo, status e datas. | ADR 0005 (aceito) |

## 2. Conceitos calculados (usados em todos os blocos)

### 2.1 Etapa do serviço (ADR 0006, seção 1 — aceito)

| Etapa | Regra |
|---|---|
| `na_fila` | status `aberto` e **sem tarefas** |
| `distribuido` | status `aberto` e com tarefas (ninguém começou) |
| `em_execucao` | status `em_andamento` |
| `concluido` | status `concluida` |
| `cancelado` | status `cancelado` |

Calculada por `annotate`, sem campo novo.

### 2.2 Situação de prazo de uma tarefa ativa

| Valor | Regra | Situação |
|---|---|---|
| `atrasado` | `prazo < hoje` | aceito (carga, seção 7) |
| `vence_7_dias` | `hoje <= prazo <= hoje + 7` | aceito (carga, seção 7) |
| `depois` | `prazo > hoje + 7` | aceito |
| `sem_prazo` | `prazo` vazio (alerta) | aceito (seção 5.1) |
| `vence_hoje`, `vence_semana` | faixas mais finas | **proposta** (seção 5.2) |

**Prazo do serviço** = maior prazo entre as tarefas (aceito, seção 5.1). Hoje `Servico.prazo` é um campo editável; passaria a ser preenchido pela sincronização do serviço, como já acontece com status e datas.

### 2.3 Parado e aguardando (ADR 0006, seção 6 — aceito)

- **`parado_ha_dias`** = hoje − data da última movimentação da tarefa. *Proposta:* novo campo `Tarefa.movimentada_em`, atualizado só quando muda status, responsável ou prazo. Usar `atualizado_em` contaria qualquer edição (ex.: corrigir a descrição) como movimento.
- **Aguardando:** dois campos novos na tarefa:
  - `aguardando_motivo`: `cliente`, `documentacao`, `agendamento`, `terceiro` ou `outro`, opcional;
  - `aguardando_desde`: data e hora.

  Limpos automaticamente quando o status da tarefa muda. Não congelam o prazo.

### 2.4 Idade

- **`com_a_pessoa_ha_dias`** = hoje − `Tarefa.criada_em` (ou a data da última reatribuição, se houver; *proposta*: guardar `atribuida_em`).

### 2.5 Setores que a pessoa acompanha

- **Organiza o setor X:** tem `servicos.ver_setor` **e** `tarefas.distribuir` em X (ADR 0006, seção 8 — proposta).
- **Acompanha o setor X:** tem `servicos.ver_setor` em X.
- Com `setores.todos`: todos os **setores de execução** (setores com ao menos um catálogo), sem lista fixa.

`os.ver_todas` **não** coloca ninguém no painel de setor: ela dá acesso de leitura às listagens, mas não torna a pessoa organizadora de um setor.

## 3. Visões de trabalho por pessoa (proposta)

A visão é montada pelas permissões, não pelo nome da função. Abaixo, como ficam as 10 funções iniciais (permissões da migração `organizacoes/0013`):

| Função inicial | Permissões relevantes | Visões que recebe |
|---|---|---|
| Técnico | nenhuma de execução | **Minhas tarefas** |
| Sub-Gestor Técnico | `servicos.ver_setor`, `tarefas.distribuir`, `tarefas.editar_setor` (Seg. do Trabalho) | **Painel do setor** (Seg. do Trabalho) + Minhas tarefas |
| Gestor Técnico | as do Sub-Gestor + `os.gerenciar`, `financeiro.ver_valores` | Painel do setor + Minhas tarefas + Vendas |
| Comercial | `os.gerenciar`, `financeiro.ver_valores` | **Vendas** |
| Gestor Comercial | tudo, com `setores.todos` | Vendas + **Visão consolidada** + Cobranças |
| Diretor | tudo, com `setores.todos` | Visão consolidada + Vendas + Cobranças |
| Financeiro / Gestor Financeiro | `financeiro.registrar_cobranca`, `financeiro.ver_valores` | **Cobranças** + Vendas |
| Administrativo / Gestor Administrativo | `os.gerenciar` (sem valores) | Vendas (sem valores) |

Qualquer pessoa com tarefa atribuída também vê **Minhas tarefas**, inclusive gestores.

Para o frontend saber quais visões mostrar, o `/auth/me/` já devolve `permissoes` (globais, por setor e `todos_os_setores`). O endpoint 4.1 devolve os setores com nome, para montar o menu do painel.

## 4. Endpoints

Legenda de situação: **existe** (sem mudança), **ajustar** (existe e muda), **novo**.

Prefixo comum: `/api/ordens-servico/`.

### 4.1 Execução — painel do setor

| # | Bloco (ADR 0006) | Endpoint | Permissão | Situação |
|---|---|---|---|---|
| E1 | (menu do painel) | `GET execucao/setores/` | `servicos.ver_setor` em algum setor | novo |
| E2 | Fila de triagem | `GET execucao/setores/{setor_id}/fila/` | `servicos.ver_setor` no setor | novo |
| E3 | Ação de distribuir | `POST execucao/servicos/{id}/distribuir/` | `tarefas.distribuir` no setor do serviço | novo |
| E4 | Em andamento por responsável | `GET execucao/setores/{setor_id}/andamento/` | `servicos.ver_setor` no setor | novo |
| E5 | Atrasados, aguardando e parados | `GET execucao/setores/{setor_id}/atencao/` | `servicos.ver_setor` no setor | novo |
| E6 | Concluídos no período | `GET execucao/setores/{setor_id}/concluidos/?de=&ate=` | `servicos.ver_setor` no setor | novo |
| E7 | Carga da equipe | `GET execucao/setores/{setor_id}/equipe/` | `servicos.ver_setor` no setor | novo |

**E1 — Setores que acompanho.** Um item por setor (regra 2.5), com contadores para o menu e os cards:

```json
[{
  "id": 3, "nome": "Segurança do Trabalho",
  "organiza": true,
  "na_fila": 12, "em_andamento": 48, "atrasados": 9, "aguardando": 4, "sem_prazo": 6
}]
```

`organiza` indica se a pessoa pode distribuir no setor (mostra ou esconde o botão).

**E2 — Fila.** Serviços do setor na etapa `na_fila`, mais antigos primeiro.

- Campos:
  - `servico_id`, `catalogo_nome`, `descricao`, `prioridade`;
  - `ordem_servico_id`, `cliente_id`, `cliente_nome`, `data_venda`;
  - `na_fila_ha_dias`, calculado desde `Servico.criado_em`;
  - `outros_servicos_da_os`: lista de `{catalogo_nome, setor_nome, etapa}`. Mostra os pacotes: PGR, PCMSO e LTCAT da mesma OS.
- Filtros: `cliente`, `ordem_servico`, `prioridade`.
- Agrupar por cliente ou por OS é decisão da tela: o frontend agrupa pelos campos que já recebe.

**E3 — Distribuir.** Cria as tarefas do serviço numa transação.

```json
{ "tarefas": [ { "responsavel": 17, "prazo": "2026-10-30", "descricao": "" } ] }
```

- Uma tarefa = distribuição comum. Mais de uma = "dividir entre técnicos" (aceito, seção 4).
- Também serve para acrescentar tarefas a um serviço já distribuído.
- O prazo é opcional; sem prazo, a tarefa aparece como alerta (aceito).
- Responde com o serviço atualizado (etapa `distribuido`).
- **Proposta, a confirmar:** o responsável precisa ter vínculo ativo no setor do serviço. Hoje qualquer usuário ativo pode ser responsável. Com a regra, a lista de técnicos da tela vem de E7 e um setor novo só distribui para os seus membros.

**E4 — Em andamento.** Tarefas ativas (`aberta` e `em_andamento`) do setor.

- Campos:
  - `tarefa_id`, `status`;
  - `responsavel_id`, `responsavel_nome`;
  - `servico_id`, `catalogo_nome`, `cliente_nome`, `ordem_servico_id`;
  - `prazo`, `situacao_prazo`;
  - `com_a_pessoa_ha_dias`, `parado_ha_dias`;
  - `aguardando_motivo`, `aguardando_desde`.
- Filtro: `responsavel`. O frontend agrupa por responsável.

**E5 — Atenção.** Mesmo formato de E4, só com as tarefas ativas que estão:

- atrasadas;
- aguardando;
- paradas há `N` dias ou mais. **Proposta:** `?parado_dias=`, padrão 7.

Cada item traz `motivos: ["atrasada", "aguardando", "parada"]`.

**E6 — Concluídos.** Serviços concluídos no período (por `data_termino`).

- Campos:
  - `catalogo_nome`, `cliente_nome`, `ordem_servico_id`;
  - `terminado_por_nome`;
  - `prazo`, `data_termino`, `no_prazo` (verdadeiro, falso ou vazio quando não havia prazo).
- Padrão do período: mês atual.

**E7 — Equipe e carga.** Um item por pessoa com vínculo ativo no setor, mais quem tem tarefa ativa no setor sem ter vínculo (ex.: alguém que mudou de setor):

```json
{
  "usuario_id": 17, "nome": "Nome Completo", "funcao": "Técnico", "membro_do_setor": true,
  "ativos": 9, "atrasados": 2, "vence_7_dias": 3, "sem_prazo": 1, "aguardando": 1,
  "mais_antigo_dias": 41, "parado_mais_antigo_dias": 18
}
```

- `ativos` não conta os aguardando (aceito, seção 7).
- Serve também como lista de responsáveis na distribuição.

### 4.2 Execução — quem executa

| # | Bloco | Endpoint | Permissão | Situação |
|---|---|---|---|---|
| X1 | Meus serviços | `GET execucao/minhas-tarefas/` | base (só as próprias) | novo |
| X2 | Marcar aguardando | `POST tarefas/{id}/aguardando/` `{ "motivo": "cliente" }` | responsável ou `tarefas.editar_setor` | novo |
| X3 | Retirar aguardando | `DELETE tarefas/{id}/aguardando/` | idem | novo |
| X4 | Mudar status | `PATCH tarefas/{id}/` `{ "status": ... }` | responsável ou `tarefas.editar_setor` | existe |
| X5 | Detalhe do serviço | `GET execucao/servicos/{id}/` | quem vê o serviço (`servicos_visiveis`) | novo |

**X1 — Minhas tarefas.**

- Mesmo formato de E4, filtrado pelo usuário logado, ordenado por situação de prazo (atrasadas primeiro).
- `?status=concluida&de=&ate=` mostra o histórico.
- Não exige permissão: qualquer pessoa vê as próprias tarefas.

**X5 — Detalhe do serviço:**

- dados do serviço;
- etapa e prazo;
- tarefas, com responsável, prazo, status, parado e aguardando;
- contexto da OS: cliente, data da venda e observação. **Sem** valor e condições;
- **os outros serviços da mesma OS**, com setor, etapa e responsáveis (aceito, seção 3);
- `pode_distribuir` e `pode_editar`, para a tela mostrar os botões certos.

### 4.3 Comercial

| # | Bloco | Endpoint | Permissão | Situação |
|---|---|---|---|---|
| C1 | Lista de vendas com etapa da execução | `GET ordens/` | leitura: regras atuais de visibilidade | ajustar |
| C2 | Criação e edição da venda | `POST/PATCH ordens/` e `servicos/` | `os.gerenciar` | ajustar |
| C3 | Andamento dos serviços de uma OS | `GET ordens/{id}/andamento/` | quem vê a OS | novo |

**C1:**

- Acrescentar a cada OS `resumo_execucao`:

  ```json
  { "total": 4, "na_fila": 1, "distribuido": 1, "em_execucao": 1, "concluido": 1, "cancelado": 0 }
  ```

  Assim a lista mostra "1 de 4 concluídos".
- Filtro novo `?minhas=true` (OS com `criado_por` = usuário) para "Minhas vendas".
- Filtro novo `?etapa=` para "em execução" ou "concluídas".

**C2:**

- **Proposta:** aceitar `servicos` aninhados na criação da OS, numa transação. Hoje a OS é criada e cada serviço vai num `POST` separado. Isso impede saber quando a venda terminou de ser lançada, e o aviso de chegada (seção 5) precisa desse momento.
- Os campos de condição de pagamento já seguem o ADR 0007 (seção 4b).
- O catálogo para a criação já existe: `GET /api/catalogo/catalogos/?ativo=true`.

**C3:** um item por serviço da OS com:

- `catalogo_nome`, `setor_nome`, `etapa`;
- `responsaveis` (nomes completos);
- `prazo`, `data_termino`.

Serve à tela do Comercial e ao detalhe da OS.

### 4.4 Financeiro

A camada de dados do ADR 0007 (seção 4b) já está implementada; os nomes abaixo são os do modelo.

| # | Bloco | Endpoint | Permissão | Situação |
|---|---|---|---|---|
| F1 | Cobranças (liberadas, lançadas, não liberadas) | `GET cobrancas/?situacao=liberada\|lancada\|nao_liberada` | `financeiro.registrar_cobranca` | novo (hoje: `ordens/?liberada=&cobranca_realizada=`) |
| F2 | Registrar o lançamento | `PATCH ordens/{id}/cobranca/` `{ "referencia_lancamento", "data_cobranca" }` | `financeiro.registrar_cobranca` | existe |
| F3 | Situação financeira de uma OS | `GET ordens/{id}/financeiro/` | `financeiro.ver_valores` | ajustar (substitui `liberada-cobranca/`) |
| F4 | Indicadores financeiros | `GET /api/analise/financeiro/` | `financeiro.ver_valores` | ajustar ("a cobrar" = liberado e não lançado) |

**F1** traz cada OS com:

- `cliente_nome` e `valor`;
- a condição já organizada: `tipo_condicao`, `quantidade_parcelas`, `data_acordada_cobranca` (primeiro vencimento), `intervalo_parcelas_dias`, `dia_fechamento`, `dia_vencimento`, `forma_pagamento`;
- `liberada_em` e `liberada_por_nome`;
- `referencia_lancamento`, `origem_lancamento`, `data_cobranca` e `cobranca_realizada_por_nome`.

### 4.5 Visão consolidada (diretoria)

Nenhum endpoint próprio:

- E1 com `setores.todos` devolve todos os setores de execução com os contadores;
- E2 a E7 funcionam para qualquer setor;
- C1 e F1 já cobrem venda e faturamento.

## 5. Aviso de chegada por e-mail (aceito em princípio; formato a definir)

- **Quando:** ao concluir a criação da OS. Com C2 aninhado, é no fim da transação (`on_commit`). Serviço acrescentado depois a uma OS existente avisa só o setor dele.
- **Para quem:** usuários ativos com `tarefas.distribuir` **no setor do serviço**. É a mesma função `tem_permissao(usuario, permissao, setor)` usada na API, então funciona para qualquer setor novo.
- **Conteúdo:** um e-mail por setor, listando os serviços que chegaram (catálogo, cliente, OS) e um link para a fila (E2).
- O interruptor `EMAIL_NOTIFICATIONS_ENABLED` continua valendo.

## 6. Mudanças de modelo que os endpoints exigem

Todas em `Tarefa` e `Servico`; nenhum app novo.

| Mudança | Para quê | Situação |
|---|---|---|
| Remover `horas_estimadas` e `complexidade` de `Servico` e `Tarefa` | ADR 0005 | aceito |
| `Servico.prazo` passa a ser calculado (maior prazo das tarefas) | seção 2.2 | aceito (ADR 0006, 5.1) |
| `Tarefa.aguardando_motivo`, `Tarefa.aguardando_desde` | X2, X3, E5, E7 | aceito (ADR 0006, 6) |
| `Tarefa.movimentada_em` | `parado_ha_dias` | proposta |
| `Tarefa.atribuida_em` | idade com a pessoa após reatribuição | proposta |

## 7. Pontos para decidir

| # | Ponto | Recomendação |
|---|---|---|
| 1 | Aprovar as visões da seção 3 (organizador = `servicos.ver_setor` + `tarefas.distribuir`) | aprovar |
| 2 | Um endpoint por bloco (seção 4) | aprovar |
| 3 | Responsável precisa ter vínculo no setor do serviço (E3) | aprovar: mantém cada setor isolado e funciona para setores novos |
| 4 | Serviços aninhados na criação da OS (C2) | aprovar: dá o momento certo para o aviso de chegada |
| 5 | "Parado" a partir de `movimentada_em` e padrão de 7 dias em E5 | aprovar |
| 6 | Faixas `vence_hoje` / `vence_semana` e histórico de replanejamento | deixar para depois; a carga aceita já cobre atrasado, 7 dias e sem prazo |
| 7 | "Novos desde a sua última triagem" (ADR 0006, seção 9) | deixar para depois; exige guardar a última visita por pessoa e setor |
| 8 | Ordem de implementação | ADR 0005 → modelo da tarefa (aguardando, movimentação) → E1 a E7 e X1 a X5 → C1 a C3 → aviso de chegada → F1, F3 e F4 (a camada de dados do faturamento já existe) |
