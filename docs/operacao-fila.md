# Operacao da fila de documentos

## Objetivo

A fila protege a VPS contra picos de memoria. A API recebe o upload, grava o
DOCX em um volume privado, cria um job no Redis e responde `202`. Um worker RQ
processa um documento por vez em um processo filho isolado. O frontend consulta
o status e baixa o resultado quando estiver pronto.

O Redis guarda apenas metadados e estado. O conteudo do documento nao e salvo
no Redis nem no PostgreSQL.

## Componentes

- `api`: upload, consulta de status e download.
- `redis`: fila persistida com AOF; limite de 128 MB e politica `noeviction`.
- `worker`: um worker RQ; cada job roda em processo filho e libera memoria ao terminar.
- `jobs-data`: volume privado compartilhado somente por API e worker.
- `web`: exibe posicao, estado do processamento e inicia o download.

## Limites e retencao

| Configuracao | Padrao | Funcao |
|---|---:|---|
| `FILA_MAX_JOBS` | 20 | Maximo de documentos aguardando |
| `JOB_TIMEOUT_SEGUNDOS` | 180 | Tempo maximo de processamento |
| `JOB_TTL_SEGUNDOS` | 900 | Disponibilidade do resultado: 15 min |
| `JOB_FILA_TTL_SEGUNDOS` | 1800 | Tempo maximo na fila/volume: 30 min |
| `MAX_UPLOAD_MB` | 20 | Tamanho maximo por documento |

O arquivo de entrada e apagado pelo worker assim que o processamento termina,
inclusive em caso de erro. O resultado e apagado depois do download. Uma rotina
da API remove diretorios abandonados a cada cinco minutos quando atingem o TTL.

## API

`POST /jobs/formatar` recebe `multipart/form-data`: `file`, `modo` (`abnt` ou
`fametro`), as opcoes booleanas e o JSON opcional `dados`.

Resposta `202`:

```json
{
  "id": "uuid-sem-hifens",
  "status": "na_fila",
  "posicao": 1,
  "nome_saida": "artigo_formatado.docx",
  "status_url": "/jobs/uuid-sem-hifens"
}
```

- `GET /jobs/{id}`: consulta estado e posicao.
- `GET /jobs/{id}/download`: baixa o resultado e agenda sua exclusao.
- `DELETE /jobs/{id}`: cancela um job que ainda nao iniciou.

Fila cheia responde `429` com `Retry-After: 30`. Redis indisponivel responde
`503` com `Retry-After: 15`.

## Verificacao de producao

```bash
docker service ls | grep formatador
docker service logs --since 10m formatador_worker
docker exec "$(docker ps --filter name=formatador_redis -q | head -n 1)" redis-cli ping
curl -fsS http://127.0.0.1:8080/health
```

O health deve informar `fila.habilitada=true` e `fila.disponivel=true`.

### Ajuste do host para Redis

O host usa `vm.overcommit_memory=1` para permitir fork/rewrite do AOF mesmo sob
pressao de memoria. O deploy grava `/etc/sysctl.d/99-formatador-redis.conf` e
registra o valor anterior no `ROLLBACK.txt`.

```bash
sysctl vm.overcommit_memory
cat /etc/sysctl.d/99-formatador-redis.conf
```

## Deploy seguro

Antes de cada deploy:

1. crie `.deploy-backups/AAAAmmddHHMMSS-fila`;
2. copie `Dockerfile`, requirements, arquivos de stack, `app/` e `frontend/`;
3. marque as imagens atuais como `formatador-api:rollback-STAMP` e
   `formatador-web:rollback-STAMP`;
4. registre IDs e comandos no `ROLLBACK.txt` do backup;
5. somente depois construa e implante as novas imagens.

Nao remova `redis-data` nem `jobs-data` durante atualizacoes normais.

## Rollback

Use o `STAMP` informado no relatorio do deploy:

```bash
cd /root/Formata-ABNT-PY
sh deploy/rollback-fila.sh SUBSTITUA_PELO_STAMP
```

O script valida o identificador, restaura codigo, imagens, stack e o ajuste de
kernel. A sequencia manual equivalente e mantida abaixo para recuperacao mesmo
que a copia corrente do script nao esteja disponivel.

```bash
cd /root/Formata-ABNT-PY
STAMP=SUBSTITUA_PELO_STAMP
BACKUP=".deploy-backups/${STAMP}-fila"

cp -a "$BACKUP/Dockerfile" Dockerfile
cp -a "$BACKUP/requirements.txt" requirements.txt
cp -a "$BACKUP/docker-compose.yml" docker-compose.yml
cp -a "$BACKUP/deploy/stack.yml" deploy/stack.yml
rm -rf app frontend
cp -a "$BACKUP/app" app
cp -a "$BACKUP/frontend" frontend

docker image tag "formatador-api:rollback-${STAMP}" formatador-api:latest
docker image tag "formatador-web:rollback-${STAMP}" formatador-web:latest

set -a
. deploy/.env
set +a
docker stack deploy --prune --resolve-image never -c deploy/stack.yml formatador
```

Para reverter tambem o ajuste de kernel, consulte `OVERCOMMIT_ORIGINAL` e
`OVERCOMMIT_FILE_EXISTED` no `ROLLBACK.txt`. Se o arquivo nao existia antes:

```bash
rm -f /etc/sysctl.d/99-formatador-redis.conf
sysctl -w vm.overcommit_memory=VALOR_DE_OVERCOMMIT_ORIGINAL
```

Se ele existia, restaure
`$BACKUP/99-formatador-redis.conf.before` e aplique o valor original com
`sysctl -w`.

O `--prune` remove `worker` e `redis` se eles nao existirem no stack anterior.
Os volumes novos permanecem preservados. Depois de confirmar o rollback e de
garantir que nenhum documento precisa ser recuperado, eles podem ser removidos
manualmente. Nunca remova volumes durante uma resposta a incidente.

Depois do rollback:

```bash
docker service ls | grep formatador
curl -fsS http://127.0.0.1:8080/health
```

## Recuperacao sem rollback total

- Redis indisponivel: reinicie apenas `formatador_redis`.
- Worker parado: `docker service update --force formatador_worker`.
- Fila presa: preserve primeiro `jobs-data`, examine os logs e so depois cancele jobs.
- API com memoria elevada: `docker service update --force formatador_api`.

Os endpoints sincronizados antigos `/formatar` e `/formatar/fametro` foram
mantidos para compatibilidade. O frontend publico usa exclusivamente `/jobs`.
