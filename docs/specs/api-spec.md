openapi: 3.1.0
info:
  title: Formata ABNT API
  version: 1.0.0
  description: >
    API interna do SaaS de formatacao ABNT, consumida exclusivamente pelo site.
    Endpoints publicos (F1) e autenticados por JWT (F2). Nao ha API publica para
    terceiros.
servers:
  - url: https://api.formataabnt.com/api/v1
    description: Producao
  - url: http://localhost:8000/api/v1
    description: Desenvolvimento
tags:
  - name: Publico
  - name: Auth
  - name: Creditos
  - name: Pagamentos
  - name: Documentos
  - name: Admin

paths:
  /health:
    get:
      tags: [Publico]
      summary: Healthcheck
      responses:
        "200":
          description: Servico no ar
          content:
            application/json:
              schema:
                type: object
                properties:
                  status: { type: string, example: ok }
                  version: { type: string, example: 1.0.0 }

  /formatar:
    post:
      tags: [Publico]
      summary: Formatar documento .docx (F1 anonimo / F2 autenticado)
      description: >
        Recebe multipart/form-data e devolve o arquivo formatado.
        Anonimo: sujeito a cota por IP (429). Autenticado: debita 1 credito.
      security:
        - {}
        - BearerAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file:
                  type: string
                  format: binary
                dados:
                  type: string
                  description: JSON string com os dados da capa
                incluir_capa:
                  type: boolean
                  default: false
                incluir_sumario:
                  type: boolean
                  default: false
                validar:
                  type: boolean
                  default: false
      responses:
        "200":
          description: Arquivo formatado
          headers:
            Content-Disposition:
              schema: { type: string }
          content:
            application/vnd.openxmlformats-officedocument.wordprocessingml.document:
              schema: { type: string, format: binary }
        "400":
          description: Documento ou dados invalidos
        "401":
          description: Token invalido (F2)
        "402":
          description: Creditos insuficientes (F2)
        "413":
          description: Arquivo acima do limite
        "422":
          description: Documento fora da estrutura minima
        "429":
          description: Cota anonima excedida (F1) ou rate limit (F3)

  /formatar/validar:
    post:
      tags: [Publico]
      summary: Validar estrutura sem formatar (nao consome credito)
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file: { type: string, format: binary }
      responses:
        "200":
          description: Resultado da validacao
          content:
            application/json:
              schema:
                type: object
                properties:
                  valido: { type: boolean }
                  secoes_ausentes:
                    type: array
                    items: { type: string }
        "400":
          description: Documento invalido

  /auth/registrar:
    post:
      tags: [Auth]
      summary: Criar conta
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, senha]
              properties:
                email: { type: string, format: email }
                senha: { type: string, minLength: 8 }
                nome: { type: string }
      responses:
        "201":
          description: Conta criada
        "409":
          description: E-mail ja cadastrado

  /auth/login:
    post:
      tags: [Auth]
      summary: Login (retorna access + refresh)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, senha]
              properties:
                email: { type: string, format: email }
                senha: { type: string }
      responses:
        "200":
          description: Autenticado
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token: { type: string }
                  refresh_token: { type: string }
                  token_type: { type: string, example: bearer }
                  papel: { type: string, enum: [usuario, admin] }
        "401":
          description: Credenciais invalidas

  /auth/refresh:
    post:
      tags: [Auth]
      summary: Renovar access token
      security:
        - BearerAuth: []
      responses:
        "200":
          description: Novo access token
        "401":
          description: Refresh invalido/expirado

  /auth/logout:
    post:
      tags: [Auth]
      summary: Revogar refresh token da sessao
      security:
        - BearerAuth: []
      responses:
        "204":
          description: Sessao encerrada

  /auth/esqueci-senha:
    post:
      tags: [Auth]
      summary: Solicitar recuperacao de senha
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email]
              properties:
                email: { type: string, format: email }
      responses:
        "202":
          description: E-mail enviado se a conta existir
        "429":
          description: Muitas solicitacoes

  /creditos/saldo:
    get:
      tags: [Creditos]
      summary: Consultar saldo
      security:
        - BearerAuth: []
      responses:
        "200":
          description: Saldo atual
          content:
            application/json:
              schema:
                type: object
                properties:
                  saldo: { type: integer, example: 7 }
        "401":
          description: Nao autenticado

  /creditos/extrato:
    get:
      tags: [Creditos]
      summary: Extrato de creditos
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: per_page
          in: query
          schema: { type: integer, default: 20 }
      responses:
        "200":
          description: Lista de transacoes
        "401":
          description: Nao autenticado

  /pacotes:
    get:
      tags: [Pagamentos]
      summary: Listar pacotes de creditos disponiveis
      responses:
        "200":
          description: Catalogo de pacotes

  /pagamentos/checkout:
    post:
      tags: [Pagamentos]
      summary: Criar pedido e preferencia de pagamento no Mercado Pago
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [pacote_id, metodo]
              properties:
                pacote_id: { type: string, format: uuid }
                metodo: { type: string, enum: [pix, cartao, boleto] }
      responses:
        "201":
          description: Pedido criado
          content:
            application/json:
              schema:
                type: object
                properties:
                  pedido_id: { type: string, format: uuid }
                  checkout_url: { type: string, format: uri }
                  pix_qr_code: { type: string, nullable: true }
        "401":
          description: Nao autenticado

  /pagamentos/webhook:
    post:
      tags: [Pagamentos]
      summary: Webhook de notificacao do Mercado Pago (idempotente)
      description: Valida a origem, reconsulta a API do MP e credita em caso de aprovacao.
      responses:
        "200":
          description: Notificacao processada ou ignorada
        "400":
          description: Notificacao invalida

  /documentos:
    get:
      tags: [Documentos]
      summary: Listar metadados dos documentos formatados
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: per_page
          in: query
          schema: { type: integer, default: 20 }
      responses:
        "200":
          description: Lista de documentos (sem conteudo)
        "401":
          description: Nao autenticado

  /tokens/resgatar:
    post:
      tags: [Publico]
      summary: Resgatar token de acesso (1 documento gratuito)
      description: >
        Publico (visitante) ou autenticado. Valida o codigo, marca como usado e
        cria um passe de 1 formatacao gratuita.
      security:
        - {}
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [codigo]
              properties:
                codigo: { type: string, example: "AB12-CD34-EF56" }
      responses:
        "200":
          description: Token resgatado
          content:
            application/json:
              schema:
                type: object
                properties:
                  beneficio: { type: string, example: documento }
                  expira_em: { type: string, format: date-time }
        "422":
          description: Token invalido, expirado, revogado ou ja usado

  /admin/metricas/uso:
    get:
      tags: [Admin]
      summary: Metricas de uso (documentos, erros, usuarios)
      security:
        - BearerAuth: []
      parameters:
        - name: de
          in: query
          schema: { type: string, format: date }
        - name: ate
          in: query
          schema: { type: string, format: date }
      responses:
        "200":
          description: Agregados de uso
        "403":
          description: Requer papel admin

  /admin/metricas/faturamento:
    get:
      tags: [Admin]
      summary: Metricas de faturamento (receita, pedidos, ticket medio)
      security:
        - BearerAuth: []
      parameters:
        - name: de
          in: query
          schema: { type: string, format: date }
        - name: ate
          in: query
          schema: { type: string, format: date }
      responses:
        "200":
          description: Agregados financeiros
        "403":
          description: Requer papel admin

  /admin/tokens:
    get:
      tags: [Admin]
      summary: Listar tokens de acesso (filtros por status/lote)
      security:
        - BearerAuth: []
      parameters:
        - name: status
          in: query
          schema: { type: string, enum: [disponivel, usado, expirado, revogado] }
        - name: lote
          in: query
          schema: { type: string }
      responses:
        "200":
          description: Lista de tokens (sem o codigo puro)
        "403":
          description: Requer papel admin
    post:
      tags: [Admin]
      summary: Criar token(s) de acesso de uso unico
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                quantidade: { type: integer, default: 1, minimum: 1, maximum: 500 }
                lote: { type: string }
                observacao: { type: string }
                validade_dias: { type: integer, default: 90 }
      responses:
        "201":
          description: Token(s) criado(s) — codigos exibidos uma unica vez
        "403":
          description: Requer papel admin

  /admin/tokens/{id}:
    delete:
      tags: [Admin]
      summary: Revogar token nao usado
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        "204":
          description: Token revogado
        "403":
          description: Requer papel admin
        "404":
          description: Token nao encontrado

  /admin/usuarios:
    get:
      tags: [Admin]
      summary: Listar usuarios
      security:
        - BearerAuth: []
      responses:
        "200":
          description: Lista de usuarios
        "403":
          description: Requer papel admin

  /admin/usuarios/{id}/saldo:
    patch:
      tags: [Admin]
      summary: Ajustar saldo de creditos manualmente (gera lancamento)
      security:
        - BearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [quantidade, motivo]
              properties:
                quantidade: { type: integer, description: Positivo credita, negativo debita }
                motivo: { type: string }
      responses:
        "200":
          description: Saldo ajustado
        "403":
          description: Requer papel admin

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
