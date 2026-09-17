# Componentes Frontend

> Stack: Vue 3 via CDN + Bootstrap 5.3, paginas estaticas servidas por nginx.
> Sem pipeline de build, **sem login** e **sem perfis**. Estado via `reactive`/`ref`, sem Vuex/Pinia.
> A pagina publica (`index.html`) concentra ferramenta + doacao; `admin.html` e o
> painel minimo (somente leitura) protegido por chave.

## Arvore de Arquivos
```
frontend/
├── index.html                 # ferramenta publica (Vue CDN)
├── admin.html                 # painel admin minimo (chave)
├── nginx.conf.template
└── assets/
    ├── css/app.css            # estilos proprios sobre o Bootstrap
    ├── js/
    │   ├── app.js             # instancia Vue, estado e chamadas a API
    │   ├── api.js             # wrapper fetch (baseURL, erros)
    │   ├── admin.js           # logica do painel admin minimo
    │   └── components/        # componentes registrados globalmente
    │       ├── UploadDropzone.js
    │       ├── OpcoesForm.js
    │       ├── DadosCapaForm.js
    │       ├── ResultadoCard.js
    │       └── ApoiarProjeto.js
    └── img/logo.svg
```

## Componentes (publico)
```
#app (root)
├── AppNavbar          # logo, links "Como funciona" e "Apoiar o projeto"
├── HeroSection        # proposta de valor + UploadDropzone
├── UploadDropzone     # drag-and-drop / seletor de arquivo
├── OpcoesForm         # toggles: incluir_capa, incluir_sumario, validar
├── DadosCapaForm      # campos da capa (condicional a incluir_capa)
├── ProgressoBar       # estado de upload/processamento
├── ResultadoCard      # sucesso: download + resumo das alteracoes
├── ErroAlerta         # 400/413/422 com mensagem amigavel
├── ApoiarProjeto      # botao de doacao -> canal externo (sem contraprestacao)
├── ComoFunciona       # passos 1-2-3
├── FaqSection         # duvidas frequentes
└── AppFooter
```

## Componentes (admin minimo)
```
AdminPanel
├── AdminLogin         # campo da chave (X-Admin-Key) guardada em memoria
├── KpiCards           # documentos, taxa de erro
└── GraficoUso         # documentos/dia (linha)
```

## Rotas
| Path | Pagina | Auth | Guard |
|------|--------|------|-------|
| / | index.html (ferramenta) | Nao | - |
| /como-funciona | index.html#como-funciona | Nao | - |
| /apoiar | index.html#apoiar | Nao | - |
| /admin | admin.html | Chave | exige `X-Admin-Key` valido (senao 401) |

## Estado Global (publico)
```js
const state = reactive({
  arquivo: null,          // File selecionado
  opcoes: {
    incluir_capa: false,
    incluir_sumario: false,
    validar: false,
  },
  capa: {                 // dados do formulario de capa
    instituicao: '', curso: '', autor: '',
    titulo: '', subtitulo: '', cidade: '', ano: '',
  },
  status: 'idle',         // idle | enviando | processando | sucesso | erro
  progresso: 0,
  erro: null,             // { codigo, mensagem, secoes_ausentes?, retry_em? }
  resultado: null,        // { blobUrl, nomeArquivo, resumo }
})
```

## Convencoes de UI
- Upload aceito: `.docx` (preferencial) e `.doc`, com aviso de conversao.
- Desabilitar "Formatar" sem arquivo; spinner durante o processamento.
- Deixar claro que **o uso e ilimitado e gratuito** — nao ha cota, passe ou pagamento.
- Apresentar o botao **Apoiar o projeto** como doacao voluntaria, sem prometer vantagem.
- Se a borda retornar 429 tecnico anti-flood, mostrar aviso temporario com "tentar novamente".
- Bootstrap 5.3 para grid/cards/modais; CSS proprio apenas para identidade visual.
- Nao ha referencias a login, perfis, creditos, tokens ou painel de usuario.
