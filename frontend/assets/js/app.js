/* Aplicação Vue 3 (CDN) da ferramenta pública de formatação ABNT. */
(function () {
  'use strict';

  var LIMITE_PADRAO_MB = 20;

  Vue.createApp({
    data: function () {
      return {
        arquivo: null,
        arrastando: false,
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
        progresso: 0,
        erro: null,
        resultado: null,
        doacaoUrl: null,
        limiteMb: LIMITE_PADRAO_MB,
        ano: new Date().getFullYear(),
        regrasAplicadas: [
          'Margens: 3 cm (superior/esquerda) e 2 cm (inferior/direita)',
          'Fonte Arial 12 em todo o texto',
          'Espaçamento entre linhas de 1,5',
          'Texto justificado',
          'Títulos formatados conforme a ABNT',
        ],
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
    },

    mounted: function () {
      var self = this;
      ApiABNT.info().then(function (dados) {
        if (dados && dados.doacoes_url) {
          self.doacaoUrl = dados.doacoes_url;
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
      },

      formatar: function () {
        if (!this.arquivo || this.status === 'enviando') return;
        var self = this;
        this.status = 'enviando';
        this.progresso = 0;
        this.erro = null;
        this.resultado = null;

        var form = new FormData();
        form.append('file', this.arquivo);
        form.append('incluir_capa', this.opcoes.incluir_capa);
        form.append('incluir_sumario', this.opcoes.incluir_sumario);
        form.append('validar', this.opcoes.validar);
        if (this.opcoes.incluir_capa) {
          form.append('dados', JSON.stringify(this.capa));
        }

        ApiABNT.formatar(form, function (percentual) {
          self.progresso = percentual;
        }).then(function (resposta) {
          var url = URL.createObjectURL(resposta.blob);
          self.resultado = { nome: resposta.nome, url: url };
          self.status = 'idle';
          self.baixar();
        }).catch(function (falha) {
          self.status = 'idle';
          self.erro = falha.mensagem || 'Não foi possível formatar o documento.';
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
    },
  }).mount('#app');
})();
