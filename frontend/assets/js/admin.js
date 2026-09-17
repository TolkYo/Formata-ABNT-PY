/* Painel admin mínimo (F2): métricas de uso e auditoria.
 * Acesso via chave administrativa (header X-Admin-Key), mantida apenas em memória.
 */
(function () {
  'use strict';

  var API_BASE = typeof window.API_BASE === 'string' ? window.API_BASE : '';

  Vue.createApp({
    data: function () {
      return {
        chave: '',
        carregado: false,
        carregando: false,
        erro: null,
        de: '',
        ate: '',
        resumo: null,
        porDia: [],
        auditoria: [],
        auditoriaPage: 1,
        auditoriaTotal: 0,
      };
    },

    methods: {
      req: function (url) {
        var chave = this.chave;
        return fetch(url, { headers: { 'X-Admin-Key': chave } }).then(function (resposta) {
          if (!resposta.ok) {
            return resposta.json().catch(function () { return {}; }).then(function (corpo) {
              throw new Error((corpo && corpo.detail) || ('Erro ' + resposta.status));
            });
          }
          return resposta.json();
        });
      },

      montarUrlMetricas: function () {
        var params = [];
        if (this.de) params.push('de=' + encodeURIComponent(this.de));
        if (this.ate) params.push('ate=' + encodeURIComponent(this.ate));
        return API_BASE + '/admin/metricas/uso' + (params.length ? '?' + params.join('&') : '');
      },

      entrar: function () {
        if (!this.chave) {
          this.erro = 'Informe a chave administrativa.';
          return;
        }
        var self = this;
        this.carregando = true;
        this.erro = null;
        this.carregarMetricas()
          .then(function () {
            self.carregado = true;
            return self.carregarAuditoria(1);
          })
          .catch(function (falha) {
            self.erro = falha.message || 'Falha ao consultar o painel.';
          })
          .then(function () { self.carregando = false; });
      },

      carregar: function () {
        var self = this;
        this.carregando = true;
        this.erro = null;
        this.carregarMetricas()
          .catch(function (falha) { self.erro = falha.message; })
          .then(function () { self.carregando = false; });
      },

      carregarMetricas: function () {
        var self = this;
        return this.req(this.montarUrlMetricas()).then(function (dados) {
          self.resumo = dados.resumo;
          self.porDia = dados.por_dia;
        });
      },

      carregarAuditoria: function (page) {
        var self = this;
        var alvo = page || this.auditoriaPage;
        return this.req(API_BASE + '/admin/auditoria?page=' + alvo).then(function (dados) {
          self.auditoria = dados.itens;
          self.auditoriaTotal = dados.total;
          self.auditoriaPage = dados.page;
        });
      },

      sair: function () {
        this.carregado = false;
        this.chave = '';
        this.resumo = null;
        this.porDia = [];
        this.auditoria = [];
      },

      taxa: function (valor) {
        return (Number(valor || 0) * 100).toFixed(1) + '%';
      },

      formatarData: function (iso) {
        if (!iso) return '';
        try {
          return new Date(iso).toLocaleString('pt-BR');
        } catch (e) {
          return iso;
        }
      },
    },
  }).mount('#admin');
})();
