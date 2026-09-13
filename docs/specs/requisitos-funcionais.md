# Requisitos Funcionais

> Prioridades (MoSCoW): **Must** (obrigatorio), **Should** (importante),
> **Could** (desejavel), **Won't** (fora de escopo agora).
> Fase indicada entre parenteses: F1 = MVP anonimo, F2 = conta + creditos, F3 = escala.

## Modulo: Formatacao ABNT (F1)
**Descricao**: Nucleo do produto — recebe um `.docx`, aplica a norma e devolve o arquivo.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF001 | Como visitante, quero enviar um `.docx` por upload (drag-and-drop) para formata-lo | Must | Nenhuma |
| RF002 | Como visitante, quero escolher se havera capa, sumario e validacao estrutural | Must | RF001 |
| RF003 | Como visitante, quero preencher os dados da capa (instituicao, curso, autor, titulo, subtitulo, cidade, ano) | Should | RF002 |
| RF004 | Como visitante, quero baixar o documento formatado | Must | RF001 |
| RF005 | Como visitante, quero ver um resumo do que foi alterado (margens, fonte, espacamento, titulos) | Should | RF001 |
| RF006 | Como visitante, quero ser avisado quando o documento nao atender a estrutura minima, com a lista de secoes ausentes | Should | RF002 |

**Criterios de Aceitacao**:
- [ ] Dado um `.docx` valido, quando eu envio com opcoes padrao, entao recebo o arquivo formatado para download.
- [ ] Dado um arquivo `.doc` legado, quando eu envio, entao o sistema converte ou informa que preciso enviar `.docx`.
- [ ] Dado `validar=true` e um documento sem "abstract", quando envio, entao recebo a lista de secoes ausentes sem perder o arquivo.
- [ ] Dado um arquivo acima do limite de tamanho, quando envio, entao recebo erro claro de limite.

## Modulo: Ferramenta Web Publica (F1)
**Descricao**: Interface Vue 3 CDN que torna o nucleo acessivel a usuarios leigos.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF010 | Como visitante, quero uma pagina unica com upload, opcoes e botao "Formatar" | Must | RF001 |
| RF011 | Como visitante, quero acompanhar o progresso enquanto o arquivo e processado | Must | RF010 |
| RF012 | Como visitante, quero cota gratuita anonima (ex.: 3 documentos/dia) controlada por IP | Should | RF010 |
| RF013 | Como visitante, quero uma secao de perguntas frequentes e o que a norma exige | Could | Nenhuma |
| RF014 | Como visitante, quero usar a ferramenta no celular (responsivo) | Should | RF010 |

**Criterios de Aceitacao**:
- [ ] Dado que excedi a cota anonima, quando tento enviar, entao vejo aviso com CTA para criar conta/créditos.
- [ ] Dado um arquivo grande, quando envio, entao vejo estado de progresso e nao um travamento silencioso.

## Modulo: Conta e Autenticacao (F2)
**Descricao**: Cadastro e login proprios via JWT.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF020 | Como visitante, quero criar conta com e-mail e senha para ter saldo de creditos | Must | Nenhuma |
| RF021 | Como usuario, quero fazer login e manter a sessao com refresh token | Must | RF020 |
| RF022 | Como usuario, quero recuperar minha senha por e-mail | Should | RF020 |
| RF023 | Como usuario, quero confirmar meu e-mail antes de comprar creditos | Should | RF020 |
| RF024 | Como usuario, quero sair (logout) invalidando meu refresh token | Must | RF021 |

## Modulo: Creditos (F2)
**Descricao**: Saldo pay-per-use e consumo por documento.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF030 | Como usuario, quero ver meu saldo de creditos no painel | Must | RF020 |
| RF031 | Como usuario, quero que cada formatacao debitе o custo correspondente | Must | RF030 |
| RF032 | Como usuario, quero ver o historico de creditos (compras e consumos) | Must | RF030 |
| RF033 | Como usuario, quero ser impedido de formatar quando o saldo for insuficiente | Must | RF031 |
| RF034 | Como usuario, quero reembolso automatico de credito quando a formatacao falhar por erro do sistema | Should | RF031 |

## Modulo: Pagamentos (F2)
**Descricao**: Compra de pacotes de creditos via Mercado Pago.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF040 | Como usuario, quero escolher um pacote de creditos | Must | RF020 |
| RF041 | Como usuario, quero pagar por Pix, cartao ou boleto | Must | RF040 |
| RF042 | Como usuario, quero que meus creditos sejam liberados automaticamente apos a confirmacao | Must | RF041 |
| RF043 | Como usuario, quero receber e-mail de confirmacao da compra | Should | RF042 |
| RF044 | Como admin, quero reprocessar um pagamento cujo webhook falhou | Should | RF042 |

## Modulo: Painel do Usuario (F2)
**Descricao**: Area logada com historico e consumo.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF050 | Como usuario, quero ver os documentos que formatei (metadados, sem conteudo) | Should | RF020 |
| RF051 | Como usuario, quero refazer o download de um documento recente | Could | RF050 |
| RF052 | Como usuario, quero gerenciar meus dados cadastrais e senha | Should | RF020 |

## Modulo: Admin (F2)
**Descricao**: Painel administrativo protegido por papel (`admin`), com visao de
uso, faturamento e gestao.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF060 | Como admin, quero entrar pelo mesmo login e acessar a area `/admin` | Must | RF021 |
| RF061 | Como admin, quero gerenciar o catalogo de pacotes de creditos | Should | RF040 |
| RF062 | Como admin, quero ver metricas de uso (documentos/dia, taxa de erro, usuarios ativos) | Must | RF042 |
| RF063 | Como admin, quero ver faturamento (receita total, por pacote, pedidos pagos/pendentes, ticket medio) | Must | RF042 |
| RF064 | Como admin, quero gerenciar usuarios e ajustar saldos manualmente | Could | RF020 |
| RF065 | Como admin, quero uma trilha de auditoria das minhas acoes administrativas | Could | RF060 |

**Criterios de Aceitacao**:
- [ ] Dado um usuario sem papel `admin`, quando acessa `/admin`, entao recebe 403.
- [ ] Dado o painel, quando abro, entao vejo documentos processados, taxa de erro e receita do periodo.
- [ ] Dado um ajuste manual de saldo, quando confirmo, entao gero lancamento no ledger com `tipo=ajuste`.

## Modulo: Tokens de Acesso (F2)
**Descricao**: Codigos de uso unico gerados pelo admin que liberam **1 documento
gratuito** para quem os resgatar (visitante ou usuario logado).

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF080 | Como admin, quero gerar um token de uso unico com observacao e validade | Must | RF060 |
| RF081 | Como admin, quero gerar tokens em lote (ex.: 50 codigos) para distribuir | Should | RF080 |
| RF082 | Como admin, quero listar e filtrar tokens por status (disponivel, usado, expirado, revogado) | Must | RF080 |
| RF083 | Como admin, quero revogar um token ainda nao usado | Should | RF080 |
| RF084 | Como visitante, quero resgatar um codigo e ganhar 1 formatacao gratuita sem login | Must | RF001 |
| RF085 | Como usuario logado, quero resgatar um codigo e ter 1 formatacao sem debitar credito | Should | RF030 |
| RF086 | Como admin, quero exportar os tokens de um lote em CSV | Could | RF082 |

**Criterios de Aceitacao**:
- [ ] Dado um token valido, quando resgato, entao a proxima formatacao e gratuita e o token fica `usado`.
- [ ] Dado um token ja usado/expirado/revogado, quando resgato, entao recebo erro claro.
- [ ] Dado um token resgatado por visitante, quando ele formata, entao a cota anonima nao e consumida.
- [ ] Dado um token resgatado por usuario logado, quando ele formata, entao nenhum credito e debitado.

> **Fora de escopo:** nao havera API publica para terceiros. O acesso ao servico
> ocorre exclusivamente pelo site (interface web).
