# Fluxos de UX

## Fluxo 1: Formatacao anonima (F1 - MVP)

```mermaid
graph TD
    A[Landing / Ferramenta] -->|Arrasta ou seleciona .docx| B[Arquivo carregado]
    B --> C{Quer capa/sumario?}
    C -->|Sim| D[Preenche dados da capa]
    C -->|Nao| E[Clique em Formatar]
    D --> E
    E --> F{Cota por IP OK?}
    F -->|Nao| G[429: aviso de cota + CTA criar conta]
    F -->|Sim| H[Processando...]
    H --> I{Sucesso?}
    I -->|Sim| J[ResultadoCard: download + resumo]
    I -->|422| K[Erro: secoes ausentes listadas]
    I -->|500| L[Erro amigavel + tentar novamente]
```

### Estados da Tela (F1)
| Estado | Gatilho | Comportamento |
|--------|---------|---------------|
| Vazio | Nenhum arquivo | Dropzone em destaque, botao desabilitado |
| Arquivo carregado | Selecao valida | Mostrar nome/tamanho, habilitar opcoes |
| Arquivo invalido | Extensao/tamanho | Alerta de erro, remover arquivo |
| Enviando | Clique em Formatar | Barra de progresso de upload |
| Processando | Upload concluido | Spinner + texto "Aplicando normas ABNT" |
| Sucesso | 200 | Download automatico + resumo do que foi aplicado |
| Erro de estrutura | 422 | Lista de secoes ausentes + opcao "baixar mesmo assim" (sem validar) |
| Cota excedida | 429 | Aviso com CTA "Criar conta" / "Comprar creditos" |
| Erro interno | 5xx | Mensagem amigavel + botao "Tentar novamente" |

## Fluxo 2: Criacao de conta (F2)

```mermaid
graph TD
    A[Clicou em Criar conta] --> B[Formulario e-mail + senha]
    B --> C{Validacao}
    C -->|Erro| B
    C -->|OK| D[Conta criada]
    D --> E[E-mail de verificacao]
    E -->|Clique no link| F[E-mail confirmado]
    F --> G[Login]
```

## Fluxo 3: Compra de creditos (F2)

```mermaid
graph TD
    A[Painel: saldo baixo] --> B[Escolhe pacote]
    B --> C[Seleciona metodo: Pix/cartao/boleto]
    C --> D[Cria pedido pendente]
    D --> E[Checkout Mercado Pago]
    E --> F{Pagamento aprovado?}
    F -->|Sim| G[Webhook confirma]
    G --> H[Credita saldo + e-mail]
    F -->|Nao| I[Pedido expira em 24h]
```

### Estados da Tela (F2 - Checkout)
| Estado | Gatilho | Comportamento |
|--------|---------|---------------|
| Selecao | Entrou em /pacotes | Cards com preco e creditos |
| Aguardando pagamento | Pix gerado | QR Code + copia-e-cola + polling de status |
| Processando | Cartao em analise | Mensagem "Aguardando confirmacao" |
| Aprovado | Webhook `approved` | Saldo atualizado + toast de sucesso |
| Rejeitado | Webhook `rejected` | Mensagem + opcao de tentar outro metodo |
| Expirado | 24h sem pagamento | Pedido cancelado, CTA refazer compra |

## Fluxo 4: Formatacao autenticada com debito (F2)

```mermaid
graph TD
    A[Usuario logado envia arquivo] --> B{Saldo >= 1?}
    B -->|Nao| C[402: CTA comprar creditos]
    B -->|Sim| D[Debita 1 credito - atomico]
    D --> E[Processa formatacao]
    E -->|Sucesso| F[Entrega arquivo + registra documento]
    E -->|Erro do sistema| G[Estorna credito automaticamente]
    E -->|Erro do usuario| H[Retorna erro sem estorno]
```

## Fluxo 5: Recuperacao de senha (F2)

```mermaid
graph TD
    A[Esqueci minha senha] --> B[Informa e-mail]
    B --> C[E-mail com link token 1h]
    C --> D[Define nova senha]
    D --> E[Token invalidado, login]
```

## Fluxo 6: Acesso ao painel admin (F2)

```mermaid
graph TD
    A[/admin/login] --> B{Credenciais validas?}
    B -->|Nao| A
    B -->|Sim| C{papel == admin?}
    C -->|Nao| D[403 - volta ao site]
    C -->|Sim| E[Dashboard: uso + faturamento]
    E --> F[Aba Tokens]
    E --> G[Aba Usuarios]
```

### Estados da Tela (admin)
| Estado | Gatilho | Comportamento |
|--------|---------|---------------|
| Sem permissao | papel != admin | 403 + link para o site |
| Carregando | Busca metricas | Skeleton nos KPI cards |
| Sem dados | Periodo sem uso | Cards zerados + mensagem |
| Erro | Falha na API | Alerta + botao "Tentar novamente" |

## Fluxo 7: Criacao de tokens (F2 - admin)

```mermaid
graph TD
    A[Aba Tokens] --> B[Define quantidade, lote, validade, observacao]
    B --> C[POST /admin/tokens]
    C --> D[Codigos exibidos UMA unica vez]
    D --> E[Admin copia/exporta CSV]
    E --> F[Tokens ficam 'disponivel' na lista]
```

## Fluxo 8: Resgate de token e uso gratuito (F2)

```mermaid
graph TD
    A[Usuario/visitante informa codigo] --> B[POST /tokens/resgatar]
    B --> C{Valido e nao usado?}
    C -->|Nao| D[422: motivo - ja usado/expirado/revogado]
    C -->|Sim| E[Marca token como usado]
    E --> F[Passe de 1 documento gratis]
    F --> G[Formata proximo documento sem consumir cota/credito]
    G --> H[Passe consumido]
```

### Estados do Resgate
| Estado | Gatilho | Comportamento |
|--------|---------|---------------|
| Vazio | Nenhum codigo | Campo desabilitado para envio |
| Validando | Clique em Resgatar | Spinner curto |
| Sucesso | 200 | Mensagem "1 documento gratis liberado" |
| Erro | 422 | Motivo claro e campo limpo |
| Passe ativo | Apos sucesso | Badge persistente ate usar ou expirar |
