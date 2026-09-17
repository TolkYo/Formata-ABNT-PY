# Regras de Negocio

## Entidade: Formatacao

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
- **Excecao**: limite ajustavel por configuracao.

**RN005 - Sumario automatico**
- **Condicao**: `incluir_sumario=true`.
- **Comportamento**: inserir campo `TOC \o "1-3"` antes da capa.
- **Excecao**: se o usuario nao atualizar o campo no Word, o sumario aparece com texto de instrucao — avisar na UI.

## Entidade: Uso Ilimitado e Anti-abuso (F1)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN010 | Sem cota de negocio | Fluxo | Nao existe limite de requisicoes por IP, dia ou hora. Uso livre. |
| RN011 | Sem cobranca | Fluxo | Nao ha passe, credito, token de acesso nem qualquer transacao paga. |
| RN012 | Rate limit tecnico | Fluxo | Aplicar apenas um limite generico anti-flood na borda (ex.: 60 req/min por IP). |
| RN013 | Excesso tecnico | Validacao | Exceder o limite tecnico retorna 429 temporario com `Retry-After`; nao e bloqueio de negocio. |
| RN014 | Validacao de arquivo | Validacao | Limite de tamanho e extensao continuam valendo para todo upload. |

### Detalhamento

**RN010 - Sem cota de negocio**
- **Condicao**: qualquer requisicao a `POST /formatar`.
- **Comportamento**: processar sem contagem por IP; sem bloqueio por volume.
- **Excecao**: indisponibilidade de infraestrutura pode levar a 503, que nao e cota.

**RN012 - Rate limit tecnico**
- **Condicao**: rajada anormal de requisicoes do mesmo IP.
- **Comportamento**: aplicar limite generoso na borda (nginx); uso humano normal nunca e afetado.
- **Excecao**: IPs de monitoracao/teste podem ser isentos por configuracao.

## Entidade: Doacoes (F1)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN040 | Unica arrecadacao | Fluxo | A arrecadacao do projeto vem exclusivamente de doacoes voluntarias. |
| RN041 | Sem contraprestacao | Fluxo | Doacao **nao** concede vantagem, prioridade ou funcionalidade (o uso ja e ilimitado). |
| RN042 | Canal configuravel | Fluxo | O destino (plataforma externa ou chave Pix) vem de variavel de ambiente. |
| RN043 | Sem dados financeiros | Privacidade | O sistema nao processa nem armazena dados financeiros do doador. |

### Detalhamento

**RN041 - Sem contraprestacao**
- **Condicao**: visitante realiza uma doacao.
- **Comportamento**: apenas exibir agradecimento; nenhuma alteracao funcional. A doacao ocorre fora do sistema.
- **Excecao**: nenhuma; qualquer beneficio futuro exigiria decisao de produto propria.

## Entidade: Administracao (F2)

| ID | Regra | Tipo | Descricao |
|----|-------|------|-----------|
| RN050 | Acesso por chave | Seguranca | Rotas `/admin` exigem a chave secreta de ambiente `ADMIN_API_KEY` no cabecalho `X-Admin-Key`. |
| RN051 | Somente leitura | Fluxo | O painel admin e apenas de consulta (metricas e auditoria); nao altera dados de negocio. |
| RN052 | Sem acesso a conteudo | Seguranca | Admin ve metadados e metricas, nunca o conteudo dos documentos (LGPD). |
| RN053 | Auditoria | Fluxo | Registrar acao, alvo e data de cada operacao administrativa sensivel. |
