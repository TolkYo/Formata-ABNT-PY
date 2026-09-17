# Como Usar a API de Formatação ABNT

## 1. Iniciar o servidor

```bash
uvicorn app.main:app --reload
```

A API fica disponível em `http://127.0.0.1:8000`.

---

## 2. Endpoints

| Método | Rota                | Descrição                                   |
|--------|---------------------|---------------------------------------------|
| GET    | `/`                 | Verifica se a API está no ar                |
| GET    | `/health`           | Saúde da API e link de doações              |
| POST   | `/formatar`         | Formata um `.docx` e devolve o arquivo      |
| POST   | `/formatar/validar` | Valida a estrutura mínima sem formatar      |
| GET    | `/admin/metricas/uso` | Métricas de uso (requer `X-Admin-Key`, F2) |
| GET    | `/admin/auditoria`  | Trilha de auditoria (requer `X-Admin-Key`, F2) |
| GET    | `/docs`             | Documentação interativa (Swagger UI)        |
| GET    | `/redoc`            | Documentação alternativa (ReDoc)            |

---

## 3. Endpoint `POST /formatar`

Recebe um arquivo `.docx` (multipart/form-data) e devolve o documento formatado para download.

### Parâmetros

| Campo             | Tipo    | Obrigatório | Descrição                                                                    |
|-------------------|---------|-------------|------------------------------------------------------------------------------|
| `file`            | arquivo | Sim         | Documento `.docx` a ser formatado.                                           |
| `dados`           | texto   | Não         | JSON (string) com os dados da capa.                                          |
| `incluir_capa`    | bool    | Não         | Se `true`, insere uma capa formatada no início do documento.                 |
| `incluir_sumario` | bool    | Não         | Se `true`, insere um sumário automático (TOC) no início do documento.        |
| `validar`         | bool    | Não         | Se `true`, valida a estrutura mínima antes de formatar.                      |

> Valores booleanos devem ser enviados como `"true"` ou `"false"`.
>
> **Uso gratuito e ilimitado:** não há cota nem login. Um *rate limit* técnico
> contra abuso é aplicado na borda (nginx), podendo responder `429` de forma
> temporária em rajadas anormais — o uso humano normal não é afetado.

### O que a formatação faz (sempre aplicada)

- Margens: superior/esquerda 3 cm, inferior/direita 2 cm.
- Alinhamento justificado.
- Espaçamento entre linhas: 1,5.
- Fonte Arial, tamanho 12.
- Títulos (Heading/Título 1, 2 e 3): negrito, cor preta, tamanhos e alinhamentos ABNT.

---

## 4. JSON do campo `dados` (capa)

Todos os campos são opcionais. Campos omitidos não aparecem na capa.

```json
{
  "instituicao": "Universidade Federal",
  "curso": "Direito",
  "autor": "Fulano de Tal",
  "titulo": "Título do Trabalho",
  "subtitulo": "Subtítulo (se houver)",
  "cidade": "São Paulo",
  "ano": "2026"
}
```

Exemplo mínimo:

```json
{
  "autor": "Fulano de Tal",
  "titulo": "Título do Trabalho"
}
```

---

## 5. Validação estrutural

Com `validar=true`, a API retorna erro `422` se alguma destas seções estiver ausente:

resumo, abstract, sumário, introdução, conclusão e referências.

Exemplo de resposta de erro:

```json
{
  "detail": "Documento fora da estrutura mínima. Seções ausentes: abstract, sumário."
}
```

---

## 6. Exemplos

### 6.1. Apenas formatar (sem capa nem sumário)

```powershell
curl.exe -X POST "http://127.0.0.1:8000/formatar" `
  -F "file=@tcc.docx" `
  -o tcc_formatado.docx
```

### 6.2. Formatar com capa

```powershell
curl.exe -X POST "http://127.0.0.1:8000/formatar" `
  -F "file=@tcc.docx" `
  -F "incluir_capa=true" `
  -F "dados={\"instituicao\":\"UNI\",\"autor\":\"Fulano\",\"titulo\":\"TCC\",\"cidade\":\"São Paulo\",\"ano\":\"2026\"}" `
  -o tcc_formatado.docx
```

### 6.3. Formatar com capa, sumário e validação

```powershell
curl.exe -X POST "http://127.0.0.1:8000/formatar" `
  -F "file=@tcc.docx" `
  -F "incluir_capa=true" `
  -F "incluir_sumario=true" `
  -F "validar=true" `
  -F "dados={\"instituicao\":\"UNI\",\"curso\":\"Direito\",\"autor\":\"Fulano\",\"titulo\":\"TCC\"}" `
  -o tcc_formatado.docx
```

### 6.4. Pelo Swagger (`/docs`)

1. Acesse `http://127.0.0.1:8000/docs`.
2. Em `POST /formatar`, clique em **Try it out**.
3. Selecione o arquivo em `file`.
4. Preencha os demais campos (`dados`, `incluir_capa`, etc.).
5. Clique em **Execute**. O navegador baixa o arquivo formatado.

---

## 7. Observações

- **Sumário automático:** o campo TOC precisa ser atualizado no Word (selecione o campo e pressione `F9`, ou clique com o botão direito → "Atualizar campo") para que o sumário seja gerado.
- **Sem gravação em disco:** todo o processamento ocorre em memória.
- **Formatos aceitos:** apenas `.docx`. Arquivos `.doc` antigos são recusados com erro `400` — salve o documento como `.docx` no Word.

---

## 8. Frontend (ferramenta web)

A página única fica em `frontend/index.html` e usa Vue 3 via CDN + Bootstrap 5.3
(sem build). Para rodar localmente:

1. Suba a API: `uvicorn app.main:app --reload` (porta 8000).
2. Sirva o frontend, por exemplo: `python -m http.server 5500 --directory frontend`.
3. Acesse `http://127.0.0.1:5500`.

O endereço da API pode ser trocado definindo `window.API_BASE` antes de carregar
`assets/js/api.js`. O padrão é **mesma origem** (o nginx faz proxy de `/formatar`
e `/health` para o backend). No dev com o front servido fora do nginx, defina
`window.API_BASE = 'http://127.0.0.1:8000'`.

---

## 9. Apoiar o projeto (doações)

Este é um projeto **open source**, de **uso gratuito e ilimitado**, sustentado por
**doações voluntárias**. Para exibir o botão de doação no site, defina a variável
de ambiente `DOACOES_URL` (ex.: `https://github.com/sponsors/seu-usuario`); o valor
é exposto em `GET /health` e lido pelo frontend. Doações são **voluntárias** e **não**
concedem nenhum benefício funcional.

---

## 10. Painel admin e métricas (Fase 2)

A Fase 2 adiciona métricas de uso e trilha de auditoria (admin mínimo, somente leitura).
É **opcional**: sem `DATABASE_URL`, o núcleo continua funcionando e nada é persistido.

### Configuração

- `DATABASE_URL` — conexão PostgreSQL (ex.: `postgresql+psycopg://...`).
- `ADMIN_API_KEY` — chave do painel (enviada no header `X-Admin-Key`).
- `IP_HASH_SALT` — sal para anonimizar o IP (hash SHA-256).
- `AUTO_CRIAR_TABELAS` — `true` cria as tabelas no start (dev). Em produção use Alembic.

### Migrações (Alembic)

```bash
alembic upgrade head
```

### Endpoints

| Método | Rota                  | Descrição                                   |
|--------|-----------------------|---------------------------------------------|
| GET    | `/admin/metricas/uso` | Totais, taxa de erro e série diária (`de`/`ate`) |
| GET    | `/admin/auditoria`    | Trilha de auditoria paginada                |

Ambos exigem `X-Admin-Key`; sem a chave/chave errada respondem `401`, e sem banco `503`.

### Painel web

O painel fica em `/admin` (`frontend/admin.html`); informe a chave para consultar as
métricas e a auditoria. O nginx serve a página e faz proxy de `/admin/...` para a API.

### Observabilidade e alertas

- `SENTRY_DSN` — ativa o Sentry (erros + release); sem DSN, fica desligado.
- `SENTRY_ENVIRONMENT` (padrão `production`) e `SENTRY_TRACES_SAMPLE_RATE` (padrão `0.0`).
- `ALERTA_WEBHOOK_URL` — webhook compatível com Slack/Discord (opcional; sem ele os
  alertas saem no log e no Sentry).
- Alertas verificam a janela recente a cada `ALERTA_INTERVALO_MIN` (padrão 15) minutos,
  disparando quando a taxa de erro passa de `ALERTA_TAXA_ERRO` (padrão 0.3) ou o volume
  passa de `ALERTA_VOLUME_MAX` (> 0), respeitando `ALERTA_MIN_DOCUMENTOS` e um cooldown
  (`ALERTA_COOLDOWN_MIN`). Exigem `DATABASE_URL` (usam os eventos de uso).
