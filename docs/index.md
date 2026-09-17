# Documentacao — Formata ABNT (Open Source)

Indice geral da documentacao do produto.

## Planejamento (Specs) — `/docs/specs/`
Contratos de **o que construir** (visao, requisitos, regras, dados, API, UX, roadmap).

| Arquivo | Conteudo |
|---------|----------|
| [visao-geral.md](specs/visao-geral.md) | Proposito, stack, arquitetura, fases |
| [requisitos-funcionais.md](specs/requisitos-funcionais.md) | Historias de usuario por modulo (MoSCoW) |
| [regras-negocio.md](specs/regras-negocio.md) | Regras de formatacao, uso ilimitado, doacoes e admin |
| [requisitos-nao-funcionais.md](specs/requisitos-nao-funcionais.md) | Performance, seguranca, LGPD, operacao |
| [modelo-dados.md](specs/modelo-dados.md) | ER e tabelas PostgreSQL (eventos de uso e auditoria) |
| [api-spec.md](specs/api-spec.md) | Contrato OpenAPI 3.1 |
| [componentes-frontend.md](specs/componentes-frontend.md) | Vue 3 CDN: arquivos, componentes e estado |
| [fluxos-ux.md](specs/fluxos-ux.md) | Fluxos e estados de tela |
| [roadmap.md](specs/roadmap.md) | Fases, decisoes em aberto e status |

## Guias do projeto
| Arquivo | Conteudo |
|---------|----------|
| [../README.md](../README.md) | Como usar a API (estado atual do codigo) |

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
- **Modelo**: projeto **open source** com **uso gratuito e ilimitado**, sem login e sem perfis.
- **Arrecadacao**: somente **doacoes voluntarias** (canal externo), sem contraprestacao.
- **Sem pagamentos**: nao ha passe, token, checkout, gateway nem faturas.
- **Anti-abuso**: apenas rate limit tecnico na borda (contra floods), sem limite de negocio.
- **Fase 1 (MVP)**: ferramenta web publica open source, uso ilimitado e link de doacao.
- **Fase 2**: admin minimo (metricas/auditoria) e observabilidade.
- **Fase 3**: fila, SEO e automacao de doacoes.
- **Canal**: acesso somente pelo site; sem API publica para terceiros.
- **Privacidade**: documentos nunca sao persistidos; apenas metadados anonimos.
