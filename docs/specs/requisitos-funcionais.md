# Requisitos Funcionais

> Prioridades (MoSCoW): **Must** (obrigatorio), **Should** (importante),
> **Could** (desejavel), **Won't** (fora de escopo agora).
> Fase indicada entre parenteses: F1 = MVP open source, F2 = observabilidade/admin, F3 = escala.

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
| RF012 | Como visitante, quero usar a ferramenta livremente, **sem cota, sem pagamento e sem login** | Must | RF010 |
| RF013 | Como visitante, quero uma secao de perguntas frequentes e o que a norma exige | Could | Nenhuma |
| RF014 | Como visitante, quero usar a ferramenta no celular (responsivo) | Should | RF010 |

**Criterios de Aceitacao**:
- [ ] Dado qualquer numero de documentos, quando envio em sequencia normal, entao todas as requisicoes sao processadas (sem limite de negocio).
- [ ] Dado um arquivo grande, quando envio, entao vejo estado de progresso e nao um travamento silencioso.

## Modulo: Uso Ilimitado e Anti-abuso (F1)
**Descricao**: Uso livre sem cota de negocio, protegido apenas contra abuso automatizado.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF020 | Como sistema, quero permitir uso **ilimitado** da formatacao, sem contagem por IP | Must | RF001 |
| RF021 | Como sistema, quero aplicar um **rate limit tecnico generoso** na borda apenas contra flood | Should | RF020 |
| RF022 | Como visitante legitimo, quero receber mensagem clara e temporaria se eu exceder o limite tecnico | Should | RF021 |
| RF023 | Como sistema, quero manter o limite de tamanho de upload e a validacao de arquivo | Must | RF001 |

**Criterios de Aceitacao**:
- [ ] Dado uso humano normal, quando envio varios documentos, entao nenhum bloqueio por cota ocorre.
- [ ] Dado um flood automatizado, quando excede o limite tecnico, entao recebo 429 temporario com `Retry-After`, sem afetar o uso normal.
- [ ] Dado um arquivo acima do limite de tamanho, quando envio, entao recebo 413.

## Modulo: Doacoes (F1)
**Descricao**: Unica forma de arrecadacao, voluntaria e sem contraprestacao.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF040 | Como visitante, quero um botao "Apoiar o projeto" visivel na pagina | Should | RF010 |
| RF041 | Como visitante, quero ser levado a um canal de doacao (plataforma externa ou chave Pix) | Should | RF040 |
| RF042 | Como mantenedor, quero que a doacao nao afete funcionalidade alguma (sem contraprestacao) | Must | RF040 |

**Criterios de Aceitacao**:
- [ ] Dado o botao de apoio, quando clico, entao sou direcionado ao canal de doacao configurado.
- [ ] Dado que doei, quando volto a ferramenta, entao nada muda no uso (ja e ilimitado).

## Modulo: Admin Minimo (F2)
**Descricao**: Painel administrativo (somente leitura) protegido por chave de ambiente.

| ID | Historia de Usuario | Prioridade | Dependencias |
|----|-------------------|------------|--------------|
| RF050 | Como admin, quero acessar o painel com uma chave secreta para ver metricas de uso | Must | RF001 |
| RF051 | Como admin, quero ver documentos processados por dia e taxa de erro | Should | RF050 |
| RF052 | Como admin, quero uma trilha de auditoria das minhas acoes administrativas | Could | RF050 |

**Criterios de Aceitacao**:
- [ ] Dada uma chave invalida/ausente, quando acesso `/admin`, entao recebo 401 sem detalhes internos.
- [ ] Dado o painel, quando abro, entao vejo documentos processados e taxa de erro do periodo.

> **Fora de escopo:** nao ha cadastro/login de usuario, perfis, creditos pay-per-use,
> cota de requisicoes, pagamentos nem API publica para terceiros. O acesso ocorre
> exclusivamente pelo site, sustentado por doacoes.
