# Regras de Negocio

## Entidade: Formatação

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN001 | Formatos aceitos | Validacao | Apenas `.docx` e `.doc`. `.doc` legado e convertido internamente ou rejeitado com aviso. |
| RN002 | Limite de tamanho | Validacao | Upload maximo configuravel (ex.: 20 MB). Acima disso, HTTP 413. |
| RN003 | Processamento em memoria | Fluxo | Nenhum documento e gravado em disco ou banco (LGPD/privacidade). |
| RN004 | Norma ABNT aplicada | Calculo | Margens 3/2 cm, Arial 12, espacamento 1,5, justificado e titulos conforme nivel. |
| RN005 | Sumario automatico | Fluxo | O TOC e inserido como campo do Word; exige atualizacao (F9) para renderizar. |

### Detalhamento

**RN002 - Limite de tamanho**
- **Condicao**: arquivo enviado excede `MAX_UPLOAD_MB`.
- **Comportamento**: rejeitar antes do processamento e retornar 413 com mensagem clara.
- **Excecao**: usuarios autenticados podem ter limite maior conforme plano/creditos.

**RN005 - Sumario automatico**
- **Condicao**: `incluir_sumario=true`.
- **Comportamento**: inserir campo `TOC \o "1-3"` antes da capa.
- **Excecao**: se o usuario nao atualizar o campo no Word, o sumario aparece com texto de instrucao — avisar na UI.

## Entidade: Cota Anonima (F1)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN010 | Cota por IP | Fluxo | Visitante pode formatar N documentos por janela de tempo (ex.: 3/dia), contado por IP. |
| RN011 | Contagem por IP+UA | Fluxo | Contagem considera IP; UA serve apenas como heuristica antifraude. |
| RN012 | Reset da cota | Fluxo | Janela deslizante de 24h controlada no Redis (TTL). |
| RN013 | Cota excedida | Validacao | Retorna 429 com CTA para criar conta e comprar creditos. |

## Entidade: Usuario (F2)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN020 | E-mail unico | Validacao | Nao permitir dois cadastros com o mesmo e-mail (case-insensitive). |
| RN021 | Forca da senha | Validacao | Minimo 8 caracteres, com letra e numero. Hash com bcrypt/argon2. |
| RN022 | Verificacao de e-mail | Fluxo | Comprar creditos exige e-mail verificado. |
| RN023 | Bloqueio por tentativas | Seguranca | Bloquear login apos 5 tentativas invalidas por 15 min. |

## Entidade: Credito (F2)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN030 | Custo por documento | Calculo | 1 credito por documento formatado (independe do tamanho na F2). |
| RN031 | Saldo nao negativo | Validacao | Nao permitir consumir mais creditos do que o saldo disponivel. |
| RN032 | Ledger imutavel | Fluxo | Todo credito/debito gera lancamento imutavel em `transacoes_credito`. |
| RN033 | Debito antes do processamento | Fluxo | Reservar/debitar o credito antes de processar; reembolsar se falhar por erro do sistema. |
| RN034 | Sem reembolso por resultado | Fluxo | Nao reembolsar quando a formatacao ocorreu, ainda que o usuario nao goste do resultado. |
| RN035 | Creditos nao expiram | Fluxo | Creditos comprados nao expiram na F2 (revisar em fases futuras). |

### Detalhamento

**RN033 - Debito e reembolso**
- **Condicao**: usuario autenticado inicia uma formatacao.
- **Comportamento**: debitar 1 credito atomicamente; em caso de erro 5xx do sistema, registrar estorno.
- **Excecao**: erro causado por documento invalido do usuario (RN001) nao garante estorno automatico.

## Entidade: Pagamento (F2)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN040 | Catalogo de pacotes | Validacao | Pacotes definidos em banco, com preco em BRL e quantidade de creditos. Avulso R$ 7,00; pacotes a R$ 3,00 por credito. |
| RN041 | Idempotencia de webhook | Fluxo | Processar cada notificacao do Mercado Pago uma unica vez (chave = id do pagamento). |
| RN042 | Liberacao de creditos | Fluxo | Creditar somente apos status `approved` confirmado pela API/webhook. |
| RN043 | Pedido pendente | Fluxo | Pedido criado como `pending`; expira se nao pago em 24h. |
| RN044 | Preco do pacote | Calculo | Preco vem do pedido no momento da criacao (nao reler do catalogo na confirmacao). |
| RN045 | Conciliacao | Fluxo | Job periodico reconcilia pedidos pendentes com a API do Mercado Pago. |

### Detalhamento

**RN041 - Idempotencia de webhook**
- **Condicao**: chega notificacao repetida do Mercado Pago.
- **Comportamento**: verificar `mp_payment_id` ja processado; se sim, retornar 200 sem novo credito.
- **Excecao**: nunca confiar apenas no corpo do webhook; sempre consultar a API do MP.

### Tabela de Precos (definida)

| Pacote | Creditos | Preco | Por credito |
|--------|----------|-------|-------------|
| Avulso | 1 | R$ 7,00 | R$ 7,00 |
| Pacote 5 | 5 | R$ 15,00 | R$ 3,00 |
| Pacote 15 | 15 | R$ 45,00 | R$ 3,00 |
| Pacote 40 | 40 | R$ 120,00 | R$ 3,00 |

- Precos em BRL; valores em centavos no banco (`preco_centavos`).
- 1 credito = 1 documento formatado (RN030).
- O avulso (R$ 7,00) e o ponto de entrada; os pacotes cobram R$ 3,00 por credito para incentivar volume.
- Taxa do Mercado Pago e absorvida no preco; revisar margem liquida apos os primeiros dados reais.

## Entidade: Token de Acesso (F2)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN060 | Uso unico | Fluxo | Cada token libera exatamente **1 documento gratuito** e so pode ser resgatado uma vez. |
| RN061 | Resgate atomico | Fluxo | Marcar o token como usado com `UPDATE ... WHERE usado = false`; se 0 linhas, negar (corrida). |
| RN062 | Validade | Validacao | Token expira em data configuravel na criacao (padrao 90 dias). |
| RN063 | Revogacao | Fluxo | Admin pode revogar um token ainda nao usado. |
| RN064 | Vinculo do resgate | Fluxo | Registrar quem resgatou (usuario ou IP/sessao anonima) e quando. |
| RN065 | Beneficio | Fluxo | Visitante: libera a proxima formatacao ignorando a cota por IP. Usuario logado: libera a proximidade formatacao sem debitar credito. |
| RN066 | Codigo seguro | Seguranca | Codigo aleatorio de alta entropia; guardar apenas o hash, exibir o codigo uma unica vez. |
| RN067 | Nao transferivel apos uso | Validacao | Token usado nao pode ser reutilizado, remarcado ou reembolsado como credito. |
| RN068 | Origem | Validacao | Somente admin cria/revoga tokens; toda criacao registra o admin autor. |

### Detalhamento

**RN061 - Resgate atomico**
- **Condicao**: usuario ou visitante informa um codigo.
- **Comportamento**: validar existencia, status e validade; marcar `usado=true`, `usado_por`/`usado_em` na mesma transacao.
- **Excecao**: token inexistente, expirado, revogado ou ja usado retornam erro 422 com motivo.

**RN065 - Beneficio e sem login**
- **Condicao**: token valido resgatado.
- **Comportamento**: criar um passe de 1 uso no Redis (visitante) ou flag de 1 formatacao gratuita na sessao/conta; o passe e consumido na formatacao seguinte.
- **Excecao**: se o passe nao for usado dentro da janela definida (ex.: 30 min), expira e o token permanece consumido.

## Entidade: Administracao (F2)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN070 | Papel | Validacao | `usuario.papel` em {`usuario`, `admin`}; rotas `/admin` exigem `admin`. |
| RN071 | Criacao de admin | Seguranca | Nao existe auto-promocao; admin e criado por seed/CLI ou por outro admin. |
| RN072 | Sem acesso a conteudo | Seguranca | Admin ve metadados e metricas, nunca o conteudo dos documentos (LGPD). |
| RN073 | Ajuste de saldo | Fluxo | Ajuste manual gera lancamento no ledger com `tipo=ajuste` e motivo obrigatorio. |
| RN074 | Auditoria | Fluxo | Registrar admin, acao, alvo e data de cada operacao administrativa sensivel. |
| RN075 | Faturamento | Calculo | Receita considera apenas pagamentos `approved`; pedidos pendentes nao entram no total. |

