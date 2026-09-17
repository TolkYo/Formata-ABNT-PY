openapi: 3.1.0
info:
  title: Formata ABNT API
  version: 3.0.0
  description: >
    API interna da ferramenta open source de formatacao ABNT, consumida
    exclusivamente pelo site. Sem login e sem perfis: o uso e gratuito e ilimitado,
    protegido apenas por um rate limit tecnico na borda. Nao ha pagamentos, passes
    nem tokens de acesso; a sustentacao vem de doacoes externas ao sistema.
    Nao ha API publica para terceiros.
servers:
  - url: https://api.formataabnt.com/api/v1
    description: Producao
  - url: http://localhost:8000/api/v1
    description: Desenvolvimento
tags:
  - name: Publico
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
                  version: { type: string, example: 3.0.0 }

  /formatar:
    post:
      tags: [Publico]
      summary: Formatar documento .docx (uso ilimitado)
      description: >
        Recebe multipart/form-data e devolve o arquivo formatado. Sem cota de
        negocio. O rate limit tecnico anti-flood fica na borda e pode responder
        429 temporario com Retry-After.
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
        "413":
          description: Arquivo acima do limite
        "422":
          description: Documento fora da estrutura minima
        "429":
          description: Rate limit tecnico (nao e cota de negocio)

  /formatar/validar:
    post:
      tags: [Publico]
      summary: Validar estrutura sem formatar
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

  /admin/metricas/uso:
    get:
      tags: [Admin]
      summary: Metricas de uso (documentos, erros)
      security:
        - AdminKey: []
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
        "401":
          description: Chave admin ausente ou invalida

  /admin/auditoria:
    get:
      tags: [Admin]
      summary: Trilha de auditoria administrativa
      security:
        - AdminKey: []
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: per_page
          in: query
          schema: { type: integer, default: 20 }
      responses:
        "200":
          description: Lista de registros de auditoria
        "401":
          description: Chave admin ausente ou invalida

components:
  securitySchemes:
    AdminKey:
      type: apiKey
      in: header
      name: X-Admin-Key
