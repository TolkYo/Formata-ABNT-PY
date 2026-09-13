# Documentacao — Formata ABNT (SaaS)

Indice geral da documentacao do produto.

## Planejamento (Specs) — `/docs/specs/`
Contratos de **o que construir** (visao, requisitos, regras, dados, API, UX, roadmap).

| Arquivo | Conteudo |
|---------|----------|
| [visao-geral.md](specs/visao-geral.md) | Proposito, stack, arquitetura, fases |
| [requisitos-funcionais.md](specs/requisitos-funcionais.md) | Historias de usuario por modulo (MoSCoW) |
| [regras-negocio.md](specs/regras-negocio.md) | Regras de formatacao, cota, credito e pagamento |
| [requisitos-nao-funcionais.md](specs/requisitos-nao-funcionais.md) | Performance, seguranca, LGPD, operacao |
| [modelo-dados.md](specs/modelo-dados.md) | ER e tabelas PostgreSQL (F2+) |
| [api-spec.md](specs/api-spec.md) | Contrato OpenAPI 3.1 |
| [componentes-frontend.md](specs/componentes-frontend.md) | Vue 3 CDN: arquivos, componentes e estado |
| [fluxos-ux.md](specs/fluxos-ux.md) | Fluxos e estados de tela |
| [roadmap.md](specs/roadmap.md) | Fases, decisoes em aberto e status |

## Guias do projeto
| Arquivo | Conteudo |
|---------|----------|
| [../COMO_USAR.md](../COMO_USAR.md) | Como usar a API atual (F1) |

## Documentacao de implementacao — `/docs/` (a gerar)
A skill `gerador-documentacao` consome estas specs e produz a documentacao de
**como** foi construido (arquitetura tecnologica, deploy, erros, DDL fisico).

| Artefato | Origem (spec) | Destino (implementacao) |
|----------|---------------|-------------------------|
| API | `api-spec.md` (contrato) | `/docs/api.md` (implementacao + erros) |
| Dados | `modelo-dados.md` (ER logico) | `/docs/banco.md` (DDL fisico) |
| Arquitetura | `visao-geral.md` (conceitual) | `/docs/arquitetura.md` (tecnologica) |
| Deploy | — | `/docs/deploy.md` |

## Resumo do Produto
- **Modelo**: creditos pay-per-use.
- **Fase 1 (MVP)**: ferramenta web publica, sem login.
- **Fase 2**: conta JWT + creditos + Mercado Pago + painel admin + tokens de acesso.
- **Fase 3**: fila, observabilidade e SEO.
- **Canal**: acesso somente pelo site; sem API publica para terceiros.
- **Privacidade**: documentos nunca sao persistidos; apenas metadados.
