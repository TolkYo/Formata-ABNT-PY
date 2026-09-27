/* Aplicação Vue 3 (CDN) da ferramenta pública de formatação ABNT. */
(function () {
  'use strict';

  var LIMITE_PADRAO_MB = 20;

  Vue.createApp({
    data: function () {
      return {
        arquivo: null,
        arrastando: false,
        modoFormatacao: 'abnt',
        opcoes: {
          incluir_capa: false,
          incluir_sumario: false,
          validar: false,
        },
        capa: {
          instituicao: '',
          curso: '',
          autor: '',
          titulo: '',
          subtitulo: '',
          cidade: '',
          ano: '',
        },
        status: 'idle',
        jobId: null,
        mensagemFila: '',
        posicaoFila: null,
        progresso: 0,
        erro: null,
        resultado: null,
        doacaoUrl: null,
        pix: null,
        copiado: false,
        limiteMb: LIMITE_PADRAO_MB,
        ano: new Date().getFullYear(),
      };
    },

    computed: {
      nomeArquivo: function () {
        return this.arquivo ? this.arquivo.name : '';
      },
      tamanhoLegivel: function () {
        if (!this.arquivo) return '';
        var mb = this.arquivo.size / (1024 * 1024);
        return mb >= 1 ? mb.toFixed(2) + ' MB' : Math.ceil(this.arquivo.size / 1024) + ' KB';
      },
      limiteBytes: function () {
        return this.limiteMb * 1024 * 1024;
      },
      fametroSelecionado: function () {
        return this.modoFormatacao === 'fametro';
      },
      textoBotao: function () {
        return this.fametroSelecionado ? 'Normalizar artigo FAMETRO' : 'Formatar documento';
      },
      ocupado: function () {
        return ['enviando', 'na_fila', 'processando', 'baixando'].indexOf(this.status) !== -1;
      },
      textoStatus: function () {
        if (this.status === 'enviando') return 'Enviando documento...';
        if (this.status === 'na_fila') {
          return this.posicaoFila ? 'Posicao na fila: ' + this.posicaoFila : 'Aguardando na fila...';
        }
        if (this.status === 'processando') return 'Formatando documento...';
        if (this.status === 'baixando') return 'Preparando download...';
        return '';
      },
      mensagemSucesso: function () {
        return this.fametroSelecionado
          ? 'Artigo normalizado no padrão FAMETRO com sucesso!'
          : 'Documento formatado com sucesso!';
      },
      regrasAplicadas: function () {
        if (this.fametroSelecionado) {
          return [
            'Identificação automática de título, autores e resumo',
            'Estilos próprios para seções, subseções e referências',
            'Arial 10 no resumo e Arial 12 nos demais elementos',
            'Margens: 3 cm (superior/esquerda) e 2 cm (inferior/direita)',
            'Preservação de notas de rodapé e destaques do conteúdo',
          ];
        }
        return [
          'Margens: 3 cm (superior/esquerda) e 2 cm (inferior/direita)',
          'Fonte Arial 12 em todo o texto',
          'Espaçamento entre linhas de 1,5',
          'Texto justificado',
          'Títulos formatados conforme a ABNT',
        ];
      },
    },

    mounted: function () {
      var self = this;
      ApiABNT.info().then(function (dados) {
        if (dados && dados.doacoes_url) {
          self.doacaoUrl = dados.doacoes_url;
        }
        if (dados && dados.pix && dados.pix.payload) {
          self.pix = dados.pix;
        }
      });
    },

    methods: {
      onFileChange: function (evento) {
        var escolhido = evento.target.files && evento.target.files[0];
        if (escolhido) this.selecionarArquivo(escolhido);
        evento.target.value = '';
      },

      onDrop: function (evento) {
        this.arrastando = false;
        var solto = evento.dataTransfer.files && evento.dataTransfer.files[0];
        if (solto) this.selecionarArquivo(solto);
      },

      selecionarArquivo: function (file) {
        this.erro = null;
        this.resultado = null;
        var nome = file.name.toLowerCase();

        if (nome.endsWith('.doc') && !nome.endsWith('.docx')) {
          this.erro = 'Arquivos .doc antigos não são suportados. Salve como .docx e tente novamente.';
          this.arquivo = null;
          return;
        }
        if (!nome.endsWith('.docx')) {
          this.erro = 'Envie um arquivo no formato .docx.';
          this.arquivo = null;
          return;
        }
        if (file.size > this.limiteBytes) {
          this.erro = 'Arquivo acima do limite de ' + this.limiteMb + ' MB.';
          this.arquivo = null;
          return;
        }
        this.arquivo = file;
      },

      limparArquivo: function () {
        this.arquivo = null;
        this.resultado = null;
        this.erro = null;
        this.status = 'idle';
        this.jobId = null;
        this.mensagemFila = '';
        this.posicaoFila = null;
      },

      formatar: function () {
        if (!this.arquivo || this.ocupado) return;
        var self = this;
        this.status = 'enviando';
        this.progresso = 0;
        this.erro = null;
        this.resultado = null;
        this.mensagemFila = '';
        this.posicaoFila = null;

        var atualizarProgresso = function (percentual) {
          self.progresso = percentual;
        };

        var form = new FormData();
        form.append('file', this.arquivo);
        form.append('modo', this.fametroSelecionado ? 'fametro' : 'abnt');
        form.append('incluir_capa', this.opcoes.incluir_capa);
        form.append('incluir_sumario', this.opcoes.incluir_sumario);
        form.append('validar', this.opcoes.validar);
        if (this.opcoes.incluir_capa) form.append('dados', JSON.stringify(this.capa));

        ApiABNT.enfileirar(form, atualizarProgresso).then(function (job) {
          self.jobId = job.id;
          self.status = 'na_fila';
          self.progresso = 100;
          self.posicaoFila = job.posicao;
          self.mensagemFila = 'Documento recebido. Aguarde o processamento.';
          self.acompanharJob();
        }).catch(function (falha) {
          self.status = 'idle';
          self.erro = falha.mensagem || 'Não foi possível entrar na fila.';
        });
      },

      acompanharJob: function () {
        var self = this;
        if (!this.jobId) return;
        ApiABNT.consultarJob(this.jobId).then(function (job) {
          self.status = job.status;
          self.posicaoFila = job.posicao;
          self.mensagemFila = job.mensagem || '';
          if (job.status === 'concluido') {
            self.status = 'baixando';
            return ApiABNT.baixarJob(job.download_url, job.nome_saida).then(function (resposta) {
              self.resultado = {
                nome: resposta.nome,
                url: URL.createObjectURL(resposta.blob),
              };
              self.status = 'idle';
              self.jobId = null;
              self.baixar();
            });
          }
          if (job.status === 'erro' || job.status === 'cancelado') {
            self.status = 'idle';
            self.erro = job.mensagem || 'Não foi possível processar o documento.';
            return;
          }
          setTimeout(function () { self.acompanharJob(); }, 1000);
        }).catch(function (falha) {
          if (falha.status === 0 || falha.status === 429 || falha.status === 503) {
            self.mensagemFila = 'Servidor ocupado. Tentando consultar novamente...';
            setTimeout(function () { self.acompanharJob(); }, 2000);
            return;
          }
          self.status = 'idle';
          self.erro = falha.mensagem || 'Não foi possível consultar a fila.';
        });
      },

      baixar: function () {
        if (!this.resultado) return;
        var link = document.createElement('a');
        link.href = this.resultado.url;
        link.download = this.resultado.nome;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      },

      copiarPix: function () {
        if (!this.pix) return;
        var self = this;
        var texto = this.pix.payload;

        function marcarCopiado() {
          self.copiado = true;
          setTimeout(function () { self.copiado = false; }, 2000);
        }

        function copiarFallback() {
          var campo = self.$refs.pixInput;
          if (!campo) return;
          campo.focus();
          campo.select();
          try {
            document.execCommand('copy');
            marcarCopiado();
          } catch (e) { /* copia manual pelo usuario */ }
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(texto).then(marcarCopiado, copiarFallback);
        } else {
          copiarFallback();
        }
      },
    },
  }).mount('#app');
})();
