# Componentes Frontend

> Stack: Vue 3 via CDN + Bootstrap 5.3, paginas estaticas servidas por nginx.
> Sem pipeline de build. Estado via `reactive`/`ref`, sem Vuex/Pinia.
> Fase 1 = ferramenta publica (`index.html`); F2+ adiciona `painel/` e `admin/`.

## Arvore de Arquivos
```
frontend/
├── index.html                 # F1: ferramenta publica (SPA leve via Vue CDN)
├── assets/
│   ├── css/app.css            # estilos proprios sobre o Bootstrap
│   ├── js/
│   │   ├── app.js             # instancia Vue, estado e chamadas a API
│   │   ├── api.js             # wrapper fetch (baseURL, erros, auth header)
│   │   └── components/        # componentes registrados globalmente
│   │       ├── UploadDropzone.js
│   │       ├── OpcoesForm.js
│   │       ├── DadosCapaForm.js
│   │       ├── ResultadoCard.js
│   │       ├── ResgatarToken.js
│   │       └── CotaAviso.js
│   └── img/logo.svg
├── painel/                    # F2: area logada
│   ├── index.html             # dashboard (saldo, documentos)
│   ├── login.html
│   ├── cadastro.html
│   ├── pacotes.html
│   └── assets/js/dashboard.js
└── admin/                     # F2: area administrativa (papel admin)
    ├── index.html             # dashboard: uso + faturamento
    ├── tokens.html            # gerar/listar/revogar tokens
    ├── usuarios.html          # usuarios e ajuste de saldo
    ├── login.html
    └── assets/js/admin.js
```

## Componentes (F1)
```
#app (root)
├── AppNavbar          # logo, link "Como funciona", CTA "Criar conta" (F2)
├── HeroSection        # proposta de valor + UploadDropzone
├── UploadDropzone     # drag-and-drop / seletor de arquivo
├── OpcoesForm         # toggles: incluir_capa, incluir_sumario, validar
├── DadosCapaForm      # campos da capa (condicional a incluir_capa)
├── ResultadoCard      # sucesso: download + resumo das alteracoes
├── ErroAlerta         # 400/413/422/429 com mensagem amigavel
├── ProgressoBar       # estado de upload/processamento
├── ResgatarToken      # campo "Tenho um codigo de acesso" -> POST /tokens/resgatar
├── ComoFunciona       # passos 1-2-3
├── FaqSection         # duvidas frequentes
└── AppFooter
```

## Componentes (F2 - painel)
```
Dashboard
├── SaldoCard          # saldo atual + CTA "Comprar creditos"
├── ListaDocumentos    # metadados, status, data
├── ExtratoCreditos    # ledger paginado
├── PacotesGrid        # cards de pacote -> checkout
├── CheckoutModal      # metodo (Pix/cartao/boleto) + QR/redirect
└── PerfilForm         # dados cadastrais e troca de senha
```

## Componentes (F2 - admin)
```
AdminDashboard
├── AdminNavbar        # logo, usuario admin, sair
├── KpiCards           # documentos, taxa de erro, usuarios, receita
├── GraficoUso         # documentos/dia (linha)
├── GraficoFaturamento # receita/dia e por pacote (barras)
├── TabelaPedidos      # pedidos pagos/pendentes, ticket medio
├── TokenForm          # quantidade, lote, observacao, validade
├── TokenLista         # status, lote, resgate; acao revogar
└── UsuarioTabela      # busca, papel, ajuste de saldo
```

## Rotas
| Path | Pagina | Auth | Guard |
|------|--------|------|-------|
| / | index.html (ferramenta) | Nao | - |
| /como-funciona | index.html#como-funciona | Nao | - |
| /painel | painel/index.html | Sim | redirect -> /login |
| /login | painel/login.html | Nao | redirect -> /painel se logado |
| /cadastro | painel/cadastro.html | Nao | - |
| /pacotes | painel/pacotes.html | Sim | redirect -> /login |
| /admin/login | admin/login.html | Nao | redirect -> /admin se logado |
| /admin | admin/index.html | Sim | guard papel `admin` (403 -> /admin/login) |
| /admin/tokens | admin/tokens.html | Sim | guard papel `admin` |
| /admin/usuarios | admin/usuarios.html | Sim | guard papel `admin` |

## Estado Global (F1)
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
  erro: null,             // { codigo, mensagem, secoes_ausentes? }
  resultado: null,        // { blobUrl, nomeArquivo, resumo }
})
```

## Estado Global (F2)
- **useAuth**: `{ usuario, accessToken, login(), logout(), refresh(), isAuthenticated() }`
  - access token em memoria; refresh via cookie HttpOnly/`localStorage` com cautela.
- **useCreditos**: `{ saldo, extrato, fetchSaldo(), fetchExtrato() }`
- **useDocumentos**: `{ items, page, loading, fetch() }`
- **usePacotes**: `{ items, checkout(pacoteId, metodo) }`
- **useToken**: `{ resgatar(codigo), passeAtivo, expiraEm }` (visitante ou logado)
- **useAdmin**: `{ metricasUso, metricasFaturamento, tokens, usuarios, criarTokens(), revogarToken(), ajustarSaldo() }` (exige papel `admin`)

## Convencoes de UI
- Upload aceito: `.docx` (preferencial) e `.doc`, com aviso de conversao.
- Desabilitar "Formatar" sem arquivo; spinner durante o processamento.
- Exibir cota restante para o visitante (F1) e saldo para o usuario (F2).
- Indisponivel com `403`, o guard redireciona usuario sem papel `admin` para `/admin/login`.
- Apos resgatar um token, exibir o passe ativo ("1 documento gratis liberado") ate o uso.
- Mensagens de erro sempre com acao de recuperacao (reenviar, criar conta, comprar creditos).
- Bootstrap 5.3 para grid/cards/modais; CSS proprio apenas para identidade visual.
