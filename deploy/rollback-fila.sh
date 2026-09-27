#!/bin/sh
set -eu

STAMP=${1:?Uso: rollback-fila.sh AAAAmmddHHMMSS}
case "$STAMP" in
    *[!0-9]*|'') echo "STAMP invalido" >&2; exit 2 ;;
esac
test "${#STAMP}" -eq 14

ROOT=/root/Formata-ABNT-PY
BACKUP="$ROOT/.deploy-backups/${STAMP}-fila"
test -d "$BACKUP"
test -f "$BACKUP/ROLLBACK.txt"
test -f "$BACKUP/deploy/stack.yml"

cd "$ROOT"
cp -a "$BACKUP/Dockerfile" Dockerfile
cp -a "$BACKUP/requirements.txt" requirements.txt
cp -a "$BACKUP/docker-compose.yml" docker-compose.yml
cp -a "$BACKUP/README.md" README.md
cp -a "$BACKUP/app/." app/
cp -a "$BACKUP/frontend/." frontend/
cp -a "$BACKUP/docs/." docs/
cp -a "$BACKUP/deploy/stack.yml" deploy/stack.yml

docker image tag "formatador-api:rollback-$STAMP" formatador-api:latest
docker image tag "formatador-web:rollback-$STAMP" formatador-web:latest

ORIGINAL=$(sed -n 's/^OVERCOMMIT_ORIGINAL=//p' "$BACKUP/ROLLBACK.txt" | tail -n 1)
EXISTED=$(sed -n 's/^OVERCOMMIT_FILE_EXISTED=//p' "$BACKUP/ROLLBACK.txt" | tail -n 1)
if [ "$EXISTED" = "yes" ]; then
    cp -a "$BACKUP/99-formatador-redis.conf.before" /etc/sysctl.d/99-formatador-redis.conf
else
    rm -f /etc/sysctl.d/99-formatador-redis.conf
fi
if [ -n "$ORIGINAL" ]; then
    sysctl -w "vm.overcommit_memory=$ORIGINAL"
fi

set -a
. "$BACKUP/deploy/.env"
set +a
docker stack deploy --prune --resolve-image never -c "$BACKUP/deploy/stack.yml" formatador
docker service update --force --no-resolve-image formatador_api >/dev/null
docker service update --force --no-resolve-image formatador_web >/dev/null

ready=0
for _ in $(seq 1 60); do
    if curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 2
done
test "$ready" = 1

echo "Rollback $STAMP concluido. Volumes redis-data/jobs-data foram preservados."
