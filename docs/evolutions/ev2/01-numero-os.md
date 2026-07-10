# Numero da OS

## Objetivo

Criar um identificador de negocio legivel para a Ordem de Servico, separado do ID tecnico do banco de dados.

O ID tecnico (PK) identifica o registro internamente. O numero da OS identifica a demanda externamente — em emails, reunioes, contratos e notas fiscais.

## Campo

- `numero_os`: identificador unico de negocio, gerado automaticamente pelo sistema no momento da criacao.

## Formato

```txt
OS-YYYY-NNNN
```

Onde:
- `YYYY` e o ano de criacao da OS.
- `NNNN` e o ID tecnico com padding de 4 digitos.

Exemplos: `OS-2025-0001`, `OS-2025-0042`, `OS-2026-0100`.

O padding e de 4 digitos. IDs acima de 9999 continuam corretos sem truncamento (`OS-2026-10000`).

## Regras

- O campo e gerado automaticamente no primeiro `save()` da OS.
- Nao pode ser alterado pelo usuario apos a criacao.
- E unico no banco de dados.
- Nao e nulo apos a criacao — o sistema sempre preenche.

## Migracao inicial

OS existentes devem receber `numero_os` gerado retroativamente com base em seu `pk` e no ano de `criada_em`.

A migration de backfill percorre todas as OS sem `numero_os` e aplica o padrao `OS-{ano}-{pk:04d}`.
