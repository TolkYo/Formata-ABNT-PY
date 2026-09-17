# Roadmap

## Fase 1 — MVP open source: ferramenta publica (sem login)
Objetivo: publicar o projeto aberto com uso gratuito e ilimitado, sustentado por doacoes.

- [ ] RF001 — Upload drag-and-drop de `.docx`/`.doc`
- [ ] RF002 — Opcoes: capa, sumario, validacao
- [ ] RF003 — Formulario de dados da capa
- [ ] RF004 — Download do arquivo formatado
- [ ] RF005 — Resumo do que foi aplicado
- [ ] RF006 — Aviso de estrutura minima (secoes ausentes)
- [ ] RF010 — Pagina unica com Vue 3 CDN + Bootstrap
- [ ] RF011 — Estados de upload/processamento/erro
- [ ] RF012/RF020 — Uso **gratuito e ilimitado**, sem cota e sem login
- [ ] RF021/RF022 — Rate limit tecnico anti-flood na borda (ex.: 60 req/min por IP)
- [ ] RF040-RF042 — Botao "Apoiar o projeto" com link externo de doacao
- [ ] RF014 — Layout responsivo
- [ ] Publicacao open source: `LICENSE`, `README`, `CONTRIBUTING`, `CODE_OF_CONDUCT`
- [ ] Corrigir dividas do nucleo: margens em `Cm(3)`/`Cm(2)`, suporte/aviso para `.doc`
- [ ] Deploy Docker Swarm + Traefik + nginx
- [ ] Analytics basico (documentos/dia, taxa de erro)

## Fase 2 — Observabilidade e admin minimo
Objetivo: acompanhar uso e manter o projeto saudavel, sem contas de usuario.

- [ ] RF050-RF052 — Admin minimo (somente leitura): metricas de uso e auditoria
- [ ] PostgreSQL minimo para eventos de uso e auditoria (migracoes Alembic)
- [ ] Dashboards de uso e taxa de erro
- [ ] Alertas de erro e de consumo anomalo
- [ ] Testes de formatacao e anti-abuso

## Fase 3 — Escala e sustentabilidade
Objetivo: melhorar desempenho, reduzir custo e ampliar a comunidade.

- [ ] Fila (Redis + workers) para arquivos grandes
- [ ] Observabilidade: Sentry, metricas, dashboards avancados
- [ ] Landing page de SEO + conteudo academico
- [ ] Politica de privacidade e termos de uso (LGPD)
- [ ] Automacao do reconhecimento de doacoes (metas, agradecimentos)

## Decisoes em Aberto
| Tema | Ponto a decidir |
|------|-----------------|
| Licenca | MIT vs. AGPL-3.0 (copyleft forte para servico) |
| Plataforma de doacoes | GitHub Sponsors vs. Ko-fi vs. Pix proprio |
| Rate limit tecnico | Limite exato na borda (ex.: 60 req/min por IP) |
| Retencao de logs/eventos | Prazo e anonimizacao |

## Estado das Specs
| Arquivo | Status | Revisado em |
|---------|--------|-------------|
| visao-geral.md | Revisado (open source, uso ilimitado, doacoes) | 2026-09-16 |
| requisitos-funcionais.md | Revisado | 2026-09-16 |
| regras-negocio.md | Revisado | 2026-09-16 |
| requisitos-nao-funcionais.md | Revisado | 2026-09-16 |
| modelo-dados.md | Revisado | 2026-09-16 |
| api-spec.md | Revisado | 2026-09-16 |
| componentes-frontend.md | Revisado | 2026-09-16 |
| fluxos-ux.md | Revisado | 2026-09-16 |
| roadmap.md | Revisado | 2026-09-16 |
