# Requisitos Nao Funcionais

## Performance
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF001 | Tempo de formatacao de documento tipico (< 5 MB) | < 3s (p95) |
| RNF002 | Resposta de endpoints de leitura (saldo, historico) | < 300ms (p95) |
| RNF003 | Upload + inicio de processamento | < 1s para confirmar recebimento |
| RNF004 | Arquivos grandes (> 5 MB) | Processados em fila, sem bloquear a requisicao |

## Escalabilidade
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF005 | Backend stateless | Escala horizontal no Docker Swarm |
| RNF006 | Fila de jobs | Redis + worker, no maximo 1 doc concorrente por worker configuravel |
| RNF007 | Cota anonima | Controle em Redis, sem estado local |

## Seguranca
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF010 | Senhas | Hash bcrypt/argon2, nunca em texto puro |
| RNF011 | Comunicacao | HTTPS/TLS via Traefik |
| RNF012 | Tokens | JWT access de curta duracao (ex.: 15 min) + refresh revogavel |
| RNF013 | Autorizacao | Usuario so acessa seus proprios recursos |
| RNF014 | Upload | Validar extensao real e tamanho; sanitizar nome de arquivo |
| RNF015 | Webhooks | Validar assinatura/origem e reconsultar a API do Mercado Pago |
| RNF016 | Segredos | Somente via variaveis de ambiente / secrets do Swarm |

## Privacidade e LGPD
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF020 | Conteudo de documentos | Nunca persistir; processamento 100% em memoria |
| RNF021 | Metadados | Guardar apenas nome do arquivo, data, status e usuario |
| RNF022 | Retencao | Metadados removiveis a pedido do usuario |
| RNF023 | Base legal | Consentimento explicito no cadastro e politica de privacidade |

## Disponibilidade e Resiliencia
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF030 | Uptime | 99.5% (F2) evolui para 99.9% (F3) |
| RNF031 | Healthcheck | Endpoint `/health` monitorado pelo Traefik/Swarm |
| RNF032 | Falha no pagamento | Webhook reenviado/reconciliado, sem perder credito |
| RNF033 | Deploy | Rolling update sem downtime perceptivel |

## Observabilidade
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF040 | Logs estruturados | JSON com request_id, sem dados sensiveis |
| RNF041 | Metricas | Documentos/dia, tempo de processamento, erros, receita |
| RNF042 | Erros | Integracao com Sentry ou equivalente |

## Manutenibilidade
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF050 | Testes | Suite pytest para formatter e regras de credito; cobertura > 70% nos modulos criticos |
| RNF051 | Qualidade | Lint (ruff) e formatacao (black) no CI |
| RNF052 | Migracoes | Alembic versionado (F2+) |
| RNF053 | Config | `.env.example` documentado; nenhum segredo no repositorio |

## Acessibilidade e UX
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF060 | Responsividade | Funcional de 360px a desktop |
| RNF061 | Acessibilidade | Contraste AA, labels, navegacao por teclado (WCAG 2.1 basico) |
| RNF062 | Feedback | Estados de carregando/erro/sucesso visiveis em toda acao |
| RNF063 | Idiomas | Portugues (Brasil) na F1/F2 |

## Custos e Operacao
| ID | Requisito | Metrica/Alvo |
|----|-----------|--------------|
| RNF070 | Custo por documento | CPU/memoria previsiveis; alerta de consumo anômalo |
| RNF071 | Mercado Pago | Taxa por transacao considerada no preco dos pacotes |
| RNF072 | E-mail | Servico transacional (Resend/SES) com limites de envio |
