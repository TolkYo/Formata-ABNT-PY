/* Cliente HTTP da API do Formatador ABNT (Fase 1). */
(function (global) {
  'use strict';

  // Padrão: mesma origem (o nginx faz proxy de /formatar e /health para o
  // backend). Em dev, com o front servido fora do nginx, defina antes:
  //   <script>window.API_BASE = 'http://127.0.0.1:8000'</script>
  var API_BASE = typeof global.API_BASE === 'string' ? global.API_BASE : '';

  function extrairErro(xhr) {
    return new Promise(function (resolve) {
      if (!xhr.response) {
        resolve('Falha ao processar o arquivo.');
        return;
      }
      var reader = new FileReader();
      reader.onload = function () {
        var mensagem = 'Falha ao processar o arquivo.';
        try {
          var corpo = JSON.parse(reader.result);
          var detail = corpo.detail;
          if (Array.isArray(detail)) {
            mensagem = detail.map(function (item) { return item.msg; }).join('; ');
          } else if (typeof detail === 'string') {
            mensagem = detail;
          }
        } catch (e) { /* resposta não-JSON */ }
        resolve(mensagem);
      };
      reader.onerror = function () { resolve('Falha ao processar o arquivo.'); };
      reader.readAsText(xhr.response);
    });
  }

  function enviarDocumento(rota, payload, nomePadrao, onProgress) {
    return new Promise(function (resolve, reject) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', API_BASE + rota);
      xhr.responseType = 'blob';

      xhr.upload.onprogress = function (evento) {
        if (evento.lengthComputable && typeof onProgress === 'function') {
          onProgress(Math.round((evento.loaded / evento.total) * 100));
        }
      };

      xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
          var disposicao = xhr.getResponseHeader('Content-Disposition') || '';
          var achado = /filename="?([^"]+)"?/.exec(disposicao);
          resolve({
            blob: xhr.response,
            nome: achado ? achado[1] : nomePadrao,
          });
          return;
        }

        extrairErro(xhr).then(function (mensagem) {
          reject({ status: xhr.status, mensagem: mensagem });
        });
      };

      xhr.onerror = function () {
        reject({ status: 0, mensagem: 'Não foi possível conectar ao servidor.' });
      };

      xhr.send(payload);
    });
  }

  function enfileirar(payload, onProgress) {
    return new Promise(function (resolve, reject) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', API_BASE + '/jobs/formatar');
      xhr.responseType = 'json';
      xhr.upload.onprogress = function (evento) {
        if (evento.lengthComputable && typeof onProgress === 'function') {
          onProgress(Math.min(95, Math.round((evento.loaded / evento.total) * 95)));
        }
      };
      xhr.onload = function () {
        if (xhr.status === 202) {
          resolve(xhr.response || {});
          return;
        }
        var corpo = xhr.response || {};
        reject({ status: xhr.status, mensagem: corpo.detail || 'Falha ao entrar na fila.' });
      };
      xhr.onerror = function () {
        reject({ status: 0, mensagem: 'Nao foi possivel conectar ao servidor.' });
      };
      xhr.send(payload);
    });
  }

  function consultarJob(id) {
    return fetch(API_BASE + '/jobs/' + encodeURIComponent(id)).then(function (resposta) {
      return resposta.json().then(function (corpo) {
        if (!resposta.ok) throw { status: resposta.status, mensagem: corpo.detail };
        return corpo;
      });
    });
  }

  function baixarJob(url, nomePadrao) {
    return fetch(API_BASE + url).then(function (resposta) {
      if (!resposta.ok) {
        return resposta.json().then(function (corpo) {
          throw { status: resposta.status, mensagem: corpo.detail || 'Falha no download.' };
        });
      }
      var disposicao = resposta.headers.get('Content-Disposition') || '';
      var achado = /filename="?([^";]+)"?/.exec(disposicao);
      return resposta.blob().then(function (blob) {
        return { blob: blob, nome: achado ? achado[1] : nomePadrao };
      });
    });
  }

  function formatar(payload, onProgress) {
    return enviarDocumento('/formatar', payload, 'documento_formatado.docx', onProgress);
  }

  function validar(file) {
    var form = new FormData();
    form.append('file', file);
    return fetch(API_BASE + '/formatar/validar', { method: 'POST', body: form })
      .then(function (resposta) {
        return resposta.json().then(function (corpo) {
          if (!resposta.ok) {
            throw new Error((corpo && corpo.detail) || 'Falha na validação.');
          }
          return corpo;
        });
      });
  }

  function info() {
    return fetch(API_BASE + '/health').then(function (resposta) {
      return resposta.ok ? resposta.json() : {};
    }).catch(function () { return {}; });
  }

  global.ApiABNT = {
    base: API_BASE,
    formatar: formatar,
    enfileirar: enfileirar,
    consultarJob: consultarJob,
    baixarJob: baixarJob,
    validar: validar,
    info: info,
  };
})(window);
