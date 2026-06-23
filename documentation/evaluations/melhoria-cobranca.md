# Melhoria no Sistema de Cobrança

## Objetivo

Registrar na Ordem de Serviço quando e por quem ela foi liberada para faturamento.

Esses dados são marcos históricos de cobrança e devem ser gerenciados pelo sistema.

## Campos

Campos da Ordem de Serviço:

* `liberada_para_faturamento`
* `liberada_para_faturamento_em`
* `liberada_para_faturamento_por`
* `faturada_por`

## Cobrança imediata

Quando a OS nasce com `cobranca_imediata = True`, a liberação deve ser preenchida na criação:

* `liberada_para_faturamento = True`
* `liberada_para_faturamento_em = data/hora da criação`
* `liberada_para_faturamento_por = usuário criador`

Após isso, esses campos não devem ser alterados automaticamente.

## Cobrança não imediata

Quando a OS não tem cobrança imediata, ela deve ser liberada quando chegar ao status concluída por propagação.

Regras:

* Todos os serviços da OS precisam estar concluídos.
* A data de liberação vem da conclusão da última tarefa do último serviço concluído.
* O usuário da liberação vem do responsável pela última tarefa concluída do último serviço concluído.

## Serviço terminado por

O Serviço deve registrar `terminado_por`, porque agrega várias tarefas e vários responsáveis possíveis.

Regra:

* `terminado_por` recebe o responsável da última tarefa concluída do serviço.

## Imutabilidade do marco de liberação

Depois que uma OS for liberada para faturamento, os campos de liberação não devem ser sobrescritos automaticamente.

Caso exista futuramente uma regra de reabertura ou estorno operacional, ela deve ser tratada como fluxo explícito.

## Faturamento

Quando uma OS for faturada pela API, o sistema deve registrar:

* `faturada = True`
* `numero_nf`
* `data_faturamento`
* `faturada_por = usuário da requisição`

Na primeira migração de dados, OS já faturadas devem receber `faturada_por` com o usuário de id 3.

## MiniOS / OS Operacional

A MiniOS / OS Operacional também precisa registrar rastreabilidade de cobrança.

Campos:

* `gera_cobranca`
* `data_liberacao_cobranca`
* `liberada_cobranca_por`
* `faturada`
* `numero_nf`
* `faturada_por`

Regra:

* Se `revisao_cliente = True`, então `gera_cobranca = True`.
* Se `revisao_cliente = False`, então `gera_cobranca = False`.
* `gera_cobranca` é gerenciado pelo sistema a partir de `revisao_cliente`.

Quando a MiniOS gera cobrança e é finalizada:

* `data_liberacao_cobranca` recebe a data/hora de liberação.
* `liberada_cobranca_por` recebe o responsável da MiniOS.

Como a MiniOS possui um único responsável, não há necessidade de um campo separado `concluida_por`.

Quando uma MiniOS for faturada pela API:

* `faturada = True`
* `numero_nf`
* `faturada_por = usuário da requisição`

Na primeira migração de dados, MiniOS já faturadas devem receber `faturada_por` com o usuário de id 3.

## Contratos

A Ordem de Serviço pode representar um contrato.

Campos:

* `contrato`
* `objeto_contrato`
* `contrato_data_inicio`
* `contrato_data_fim`
* `gestor_contrato_nome`
* `gestor_contrato_email`
* `gestor_contrato_telefone`

Quando `contrato = True`, o usuário deve preencher:

* Objeto do contrato
* Data de início
* Data de fim

Os dados do gestor do contrato são opcionais.

Ao criar uma OS com `contrato = True`, todos os usuários ativos do sistema devem receber um e-mail informando a criação do contrato.

Em ambiente de desenvolvimento, o backend de e-mail do Django deve usar console para evitar disparos reais.
