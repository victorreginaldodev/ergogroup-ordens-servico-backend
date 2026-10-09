# Plano — setores, funções e permissões

Plano de 09/10/2026 para implementar no backend a modelagem discutida (organização → setores → funções → vínculos) e corrigir as falhas A1–A8 de [mapa-de-permissoes.md](mapa-de-permissoes.md).

## Princípios

1. **O backend é a barreira de segurança.** O frontend já esconde as ações proibidas, mas qualquer usuário logado pode chamar a API direto com o próprio token. As regras precisam valer no servidor.
2. **Regras por código de permissão desde o primeiro passo.** As views passam a perguntar "o usuário tem `financeiro.registrar_cobranca`?" e nunca "o usuário é `gestor_financeiro`?". No começo, a resposta vem do `tipo_usuario`; depois, dos vínculos com setores. A troca acontece num lugar só.
3. **Nenhuma mudança de comportamento para quem usa a tela.** As regras novas reproduzem o que o frontend já trava. Restringir mais é decisão da gestora, feita depois, na configuração das funções.
4. **Migrações pequenas.** Uma alteração de schema por migração, separada da migração de dados, porque o MySQL não desfaz DDL em transação.
5. **Lógica em `services`**, não em serializers ou views.

## Visão geral

| Fase | Entrega | Muda comportamento? | Depende de |
|---|---|---|---|
| 0 | Fechar o trabalho em aberto | não | — |
| 1 | Catálogo de permissões + correção de A1–A8 | só para chamadas diretas à API que o front já bloqueia | regras do front (passo 1.1) |
| 2 | Estrutura: funções, permissões das funções, vínculos | não | fase 1 |
| 3 | Permissões passam a vir dos vínculos | não (com a migração dos usuários) | fase 2 + setores e funções iniciais |
| 4 | Remover `tipo_usuario` e a flag `ativo` duplicada | não | fase 3 + front adaptado |
| 5 | Painel do setor | nova funcionalidade | fase 3 + catálogos classificados |

Cada fase vira uma branch a partir de `main`, com um commit por item e testes para cada regra.

---

## Fase 0 — Fechar o que está aberto

- [ ] Separar da branch `feat/organizacao-catalogo` os modelos ainda sem migração (`Funcao`, `MembroSetor`, `Setor.organizacao`). Eles voltam na fase 2.
- [ ] Commit da branch: remoção de horas e complexidade do catálogo e entidade `Organizacao` (migrações já aplicadas no dev).
- [ ] Commit da documentação (`docs/as-is/`, briefing, mapa e este plano).
- [ ] Em paralelo: levar as 8 perguntas da seção 4 do mapa para a gestora. Elas não bloqueiam as fases 1 e 2.

## Fase 1 — Catálogo de permissões e correção das falhas

**1.1 Levantar as regras do frontend.** Ler as travas de tela no projeto React: quais tipos veem cada menu, botão e campo. Isso fecha a tabela de equivalência *tipo de usuário → permissões* e garante que o backend bloqueie exatamente o que a tela já bloqueia. Divergências entre o front e o mapa voltam para você decidir.

**1.2 Catálogo de permissões no código.** Em `apps/organizacoes/permissoes.py`:
- enum `Permissao` com os códigos da seção 3 do mapa e o escopo de cada um (global ou por setor);
- `permissoes_do_usuario(usuario)`: por enquanto calculada a partir do `tipo_usuario` pela tabela de equivalência; superusuário tem todas;
- `tem_permissao(usuario, codigo, setor=None)`;
- uma permissão DRF reutilizável, por exemplo `TemPermissao('clientes.gerenciar')`, para as views.

**1.3 Aplicar e corrigir.** Uma regra por commit, cada uma com teste:

| Falha | Correção |
|---|---|
| A1 | Sem `usuarios.gerenciar`, `tipo_usuario`, `ativo`, `is_staff` e `is_superuser` ficam somente leitura, inclusive no próprio cadastro |
| A8 | Só quem é diretor (ou superusuário) cria, edita, desativa ou exclui diretores |
| A3 | Campos de cobrança somente leitura na edição genérica de OS e OSO; os endpoints de cobrança exigem `financeiro.registrar_cobranca` |
| A2 | Sem `financeiro.ver_valores`, valor e condições de pagamento saem da resposta das OS (lista, detalhe e liberação para cobrança) |
| A4 | Auditoria exige `auditoria.ver` |
| A5 | Serviços passam a ter o mesmo filtro de visibilidade de OS e tarefas |
| A6 | Criar, reatribuir e excluir tarefa exige `tarefas.distribuir`; o responsável continua atualizando a própria tarefa |
| A7 | Escrita em clientes, catálogos, OS e serviços exige `clientes.gerenciar`, `catalogo.gerenciar`, `os.gerenciar` e `os.excluir` |

As permissões atuais (`IsGestor`, `PodeModificarTarefa`, `PodeVerValoresFinanceiros`, `TIPOS_*`) passam a usar `tem_permissao` e depois são removidas.

**Saída:** todas as regras da API em códigos de permissão, as falhas A1–A8 fechadas e nenhuma diferença para quem usa a tela.

## Fase 2 — Estrutura de setores, funções e vínculos

Só schema e API de cadastro; nenhuma regra ainda lê isso.

| Item | Detalhe |
|---|---|
| `Setor.organizacao` | Três migrações: coluna opcional → preencher com a organização existente → obrigatória. Nome único por organização. |
| `Funcao` | `organizacao`, `nome` (livre, único por organização), `descricao`, `ativo` |
| `FuncaoPermissao` | `funcao`, `permissao` (código do enum), único por par |
| `MembroSetor` | `usuario`, `setor`, `funcao`, único por usuário + setor; função e setor da mesma organização |
| API | CRUD de funções (com lista de permissões) e de vínculos; `GET` do catálogo de permissões com descrição e escopo, para a tela de configurações; tudo exige `organizacao.configurar` ou `usuarios.gerenciar` |
| Proteções | Excluir setor ou função em uso responde 409 (handler já existente) |

## Fase 3 — Permissões vindas dos vínculos

1. **`permissoes_do_usuario` passa a ler os vínculos.** Junta as permissões das funções em todos os setores do usuário; as de escopo por setor valem só naquele setor.
2. **Período de transição:** usuário sem nenhum vínculo continua com as permissões do `tipo_usuario`. Nada quebra enquanto os vínculos são cadastrados.
3. **Regras por setor de fato:** `tarefas.distribuir`, `tarefas.editar_setor`, `servicos.ver_setor` e `servicos.gerenciar` passam a considerar `Servico.setor`. Os filtros de visibilidade passam a ser "próprio + setores com permissão + tudo, se tiver `os.ver_todas`".
4. **Migração dos usuários atuais**, no momento que vocês escolherem. É preciso definir os setores e funções iniciais; a tabela de equivalência do mapa é o ponto de partida. A migração é um comando que cria funções equivalentes aos tipos e os vínculos. Testado primeiro no dev com os dados reais, e você confere a lista antes de rodar.
5. **Fim do fallback:** depois de todos os usuários vinculados, o `tipo_usuario` deixa de ser consultado.

## Fase 4 — Limpeza

- Remover `tipo_usuario`, o endpoint `/usuarios/tipos/` e as permissões antigas. O diretor vira uma função com todas as permissões no setor "Diretoria".
- Unificar `ativo` e `is_active` (INC-06), com levantamento prévio de onde divergem no banco.
- Frontend: trocar as travas por tipo pelas permissões que o backend devolve no `/auth/me/`, com a lista de permissões do usuário e por setor.

## Fase 5 — Painel do setor

Retoma o item original da sprint:
- fila de serviços aguardando triagem (sem tarefas);
- em andamento agrupado por responsável;
- atrasados e concluídos no período;
- criação e atribuição de tarefas a partir do painel.

**Depende de:**
- **Fase 3**, para o painel mostrar só os setores de cada gestor;
- **Catálogos classificados por setor**, com um comando para copiar o setor do catálogo para os serviços existentes.

---

## Decisões pendentes

| Quando | Decisão |
|---|---|
| Antes da fase 1 | Divergências entre as travas do front e a tabela de equivalência (resultado do passo 1.1) |
| Antes da fase 3 | As 8 perguntas da seção 4 do mapa |
| Antes da fase 3, passo 4 | Setores e funções iniciais e o vínculo de cada usuário atual |
| Antes da fase 5 | Classificação dos catálogos por setor |
