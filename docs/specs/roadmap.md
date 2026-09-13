# Roadmap

## Fase 1 — MVP: ferramenta web publica (sem login)
Objetivo: validar demanda e usabilidade antes de investir em cobranca.

- [ ] RF001 — Upload drag-and-drop de `.docx`/`.doc`
- [ ] RF002 — Opcoes: capa, sumario, validacao
- [ ] RF003 — Formulario de dados da capa
- [ ] RF004 — Download do arquivo formatado
- [ ] RF005 — Resumo do que foi aplicado
- [ ] RF006 — Aviso de estrutura minima (secoes ausentes)
- [ ] RF010 — Pagina unica com Vue 3 CDN + Bootstrap
- [ ] RF011 — Estados de upload/processamento/erro
- [ ] RF012 — Cota anonima por IP (Redis)
- [ ] RF014 — Layout responsivo
- [ ] Corrigir dividas do nucleo: margens em `Cm(3)`/`Cm(2)`, suporte/aviso para `.doc`
- [ ] Deploy Docker Swarm + Traefik + nginx
- [ ] Analytics basico (documentos/dia, taxa de erro)

## Fase 2 — Conta, creditos, cobranca e administracao
Objetivo: monetizar com pacotes de creditos e operar o negocio.

- [ ] RF020-RF024 — Cadastro, login JWT, refresh, logout, recuperacao de senha
- [ ] RF030-RF034 — Saldo, debito por documento, extrato, bloqueio por saldo, estorno
- [ ] RF040-RF044 — Pacotes, checkout Mercado Pago (Pix/cartao/boleto), webhook idempotente
- [ ] RF050-RF052 — Painel: documentos, perfil
- [ ] RF060-RF065 — Admin: login por papel, metricas de uso, faturamento e usuarios
- [ ] RF080-RF086 — Tokens de acesso: gerar em lote, listar, revogar e resgatar
- [ ] Migracoes Alembic + PostgreSQL
- [ ] E-mails transacionais (verificacao, compra, senha)
- [ ] Testes de regras de credito (concorrencia/ledger)

## Fase 3 — Escala e distribuicao
Objetivo: melhorar desempenho e reduzir custo de suporte.

- [ ] Fila (Redis + workers) para arquivos grandes
- [ ] Observabilidade: Sentry, metricas, dashboards
- [ ] Landing page de SEO + conteudo academico
- [ ] Politica de privacidade e termos de uso (LGPD)

## Decisoes em Aberto
| Tema | Ponto a decidir |
|------|-----------------|
| Custo por documento | 1 credito fixo (F2) vs. por pagina/tamanho (F3) |
| Canal de acesso | **Definido**: somente pelo site; sem API publica para terceiros |
| Precos dos pacotes | **Definido**: avulso R$ 7,00; pacotes a R$ 3,00/credito (5=R$15, 15=R$45, 40=R$120) |
| Expiração de creditos | Sem expiracao na F2; revisar |
| Limite anonimo | 3/dia e o ponto de partida; calibrar com dados |
| Provedor de e-mail | Resend vs. AWS SES |

## Estado das Specs
| Arquivo | Status | Revisado em |
|---------|--------|-------------|
| visao-geral.md | Em revisao | - |
| requisitos-funcionais.md | Em revisao | - |
| regras-negocio.md | Em revisao | - |
| requisitos-nao-funcionais.md | Em revisao | - |
| modelo-dados.md | Em revisao | - |
| api-spec.md | Em revisao | - |
| componentes-frontend.md | Em revisao | - |
| fluxos-ux.md | Em revisao | - |
| roadmap.md | Em revisao | - |
