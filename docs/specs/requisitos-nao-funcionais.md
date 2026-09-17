# Requisitos Nao Funcionais

## Performance
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF001 | Tempo de formatacao de documento tipico (< 5 MB) | < 3s (p95) |
| RNF002 | Resposta de endpoints leves (health, metricas) | < 300ms (p95) |
| RNF003 | Upload + inicio de processamento | < 1s para confirmar recebimento |
| RNF004 | Arquivos grandes (> 5 MB) | Processados em fila, sem bloquear a requisicao |

## Escalabilidade
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF005 | Backend stateless | Escala horizontal no Docker Swarm |
| RNF006 | Fila de jobs | Redis + worker, no maximo 1 doc concorrente por worker configuravel |
| RNF007 | Anti-abuso | Rate limit tecnico na borda; Redis opcional para metricas |

## Seguranca
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF010 | Admin | Rotas `/admin` protegidas por chave secreta de ambiente (`X-Admin-Key`) |
| RNF011 | Comunicacao | HTTPS/TLS via Traefik |
| RNF012 | Upload | Validar extensao real e tamanho; sanitizar nome de arquivo |
| RNF013 | Segredos | Somente via variaveis de ambiente / secrets do Swarm |
| RNF014 | Abuso | Rate limit generico por IP na borda (nginx/Traefik) contra floods |
| RNF015 | Sem transacoes | Nenhum dado financeiro/cartao trafega ou e armazenado no sistema |

## Privacidade e LGPD
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF020 | Conteudo de documentos | Nunca persistir; processamento 100% em memoria |
| RNF021 | Metadados | Minimos e anonimizados (IP apenas em hash) |
| RNF022 | Retencao | Logs e eventos com retencao curta e configuravel |
| RNF023 | Base legal | Aviso de privacidade e transparencia (projeto open source) |

## Disponibilidade e Resiliencia
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF030 | Uptime | 99.5% evolui para 99.9% (F3) |
| RNF031 | Healthcheck | Endpoint `/health` monitorado pelo Traefik/Swarm |
| RNF032 | Falhas | Erros tratados sem perda de dados; jobs reprocessaveis |
| RNF033 | Deploy | Rolling update sem downtime perceptivel |

## Observabilidade
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF040 | Logs estruturados | JSON com request_id, sem dados sensiveis |
| RNF041 | Metricas | Documentos/dia, tempo de processamento, taxa de erro |
| RNF042 | Erros | Integracao com Sentry ou equivalente |

## Manutenibilidade
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF050 | Testes | Suite pytest para formatter e anti-abuso; cobertura > 70% nos modulos criticos |
| RNF051 | Qualidade | Lint (ruff) e formatacao (black) no CI |
| RNF052 | Migracoes | Alembic versionado |
| RNF053 | Config | `.env.example` documentado; nenhum segredo no repositorio |
| RNF054 | Comunidade | Licenca open source, README, CONTRIBUTING e CODE_OF_CONDUCT |

## Acessibilidade e UX
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF060 | Responsividade | Funcional de 360px a desktop |
| RNF061 | Acessibilidade | Contraste AA, labels, navegacao por teclado (WCAG 2.1 basico) |
| RNF062 | Feedback | Estados de carregando/erro/sucesso visiveis em toda acao |
| RNF063 | Idiomas | Portugues (Brasil) |

## Custos e Operacao
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF070 | Custo por documento | CPU/memoria previsiveis; alerta de consumo anomalo |
| RNF071 | Sustento | Doacoes voluntarias ajudam a cobrir custos de infraestrutura |
| RNF072 | Rate limit | Limite tecnico calibrado para nao afetar uso humano normal |
