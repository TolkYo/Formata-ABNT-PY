#!/usr/bin/env bash
#
# Bootstrap idempotente da VPS Hostinger para o Formata ABNT.
#
# Replica o host da VPS Locaweb: Docker Engine + Swarm, ajuste de kernel do
# Redis, firewall UFW, projeto em /root/Formata-ABNT-PY, imagens, stack Swarm e
# nginx da borda (80 -> 127.0.0.1:8080) com TLS via Certbot.
#
# Uso (como root):
#   ./bootstrap-hostinger.sh [--env-src /caminho/deploy.env] [--skip-tls]
#
# Variaveis de ambiente opcionais:
#   PROJECT_DIR  (default: /root/Formata-ABNT-PY)
#   REPO_URL     (default: https://github.com/TolkYo/Formata-ABNT-PY.git)
#   STACK_NAME   (default: formatador)
#   DOMAIN       (default: lido de deploy/.env ou formatabnt.com.br)
#   ACME_EMAIL   (default: lido de deploy/.env; sem ele o TLS e pulado)
#
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/Formata-ABNT-PY}"
REPO_URL="${REPO_URL:-https://github.com/TolkYo/Formata-ABNT-PY.git}"
STACK_NAME="${STACK_NAME:-formatador}"
NGINX_SITE=/etc/nginx/sites-available/formatabnt.com.br
NGINX_LINK=/etc/nginx/sites-enabled/formatabnt.com.br
SYSCTL_FILE=/etc/sysctl.d/99-formatador-redis.conf
ENV_SRC=""
WITH_TLS=1

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[warn] %s\033[0m\n' "$*" >&2; }

while [ $# -gt 0 ]; do
    case "$1" in
        --env-src) ENV_SRC="$2"; shift 2 ;;
        --skip-tls) WITH_TLS=0; shift ;;
        -h|--help) sed -n '1,25p' "$0"; exit 0 ;;
        *) warn "Opcao desconhecida: $1"; shift ;;
    esac
done

if [ "$(id -u)" -ne 0 ]; then
    echo "Execute como root." >&2
    exit 1
fi

# --- 1. Pacotes base ---------------------------------------------------------
log "Instalando pacotes base (nginx, certbot, git, ufw, curl)"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg lsb-release git \
    nginx ufw certbot python3-certbot-nginx
systemctl enable --now nginx

# --- 2. Docker Engine + compose plugin --------------------------------------
if ! command -v docker >/dev/null 2>&1; then
    log "Instalando Docker Engine (repositorio oficial)"
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    ARCH="$(dpkg --print-architecture)"
    CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
    echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
        > /etc/apt/sources.list.d/docker.list
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable --now docker
else
    log "Docker ja instalado ($(docker --version))"
fi

# --- 3. Swarm init -----------------------------------------------------------
SWARM_STATE="$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo none)"
if [ "$SWARM_STATE" != "active" ]; then
    log "Inicializando Swarm"
    SWARM_ADDR="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}')"
    docker swarm init ${SWARM_ADDR:+--advertise-addr "$SWARM_ADDR"}
else
    log "Swarm ja ativo"
fi

# --- 4. Ajuste de kernel para o Redis ---------------------------------------
log "Aplicando vm.overcommit_memory=1"
printf 'vm.overcommit_memory = 1\n' > "$SYSCTL_FILE"
sysctl --system >/dev/null

# --- 5. Firewall UFW ---------------------------------------------------------
log "Configurando UFW (22, 80, 443)"
ufw --force default deny incoming  >/dev/null
ufw --force default allow outgoing >/dev/null
ufw allow 22/tcp  >/dev/null
ufw allow 80/tcp  >/dev/null
ufw allow 443/tcp >/dev/null
ufw --force enable >/dev/null

# --- 6. Codigo do projeto ----------------------------------------------------
log "Sincronizando projeto em $PROJECT_DIR"
if [ -d "$PROJECT_DIR/.git" ]; then
    git config --global --add safe.directory "$PROJECT_DIR" || true
    git -C "$PROJECT_DIR" fetch --prune origin
    git -C "$PROJECT_DIR" reset --hard origin/main
elif [ -d "$PROJECT_DIR" ]; then
    warn "Diretorio existe sem .git; usando o conteudo sincronizado."
else
    git clone "$REPO_URL" "$PROJECT_DIR"
fi
[ -f "$PROJECT_DIR/deploy/stack.yml" ] || { echo "deploy/stack.yml ausente." >&2; exit 1; }

# --- 7. deploy/.env ----------------------------------------------------------
if [ ! -f "$PROJECT_DIR/deploy/.env" ] && [ -n "$ENV_SRC" ] && [ -f "$ENV_SRC" ]; then
    log "Instalando deploy/.env a partir de $ENV_SRC"
    install -m 600 "$ENV_SRC" "$PROJECT_DIR/deploy/.env"
fi
if [ ! -f "$PROJECT_DIR/deploy/.env" ]; then
    echo "deploy/.env ausente. Passe --env-src /caminho/deploy.env ou crie o arquivo." >&2
    exit 1
fi

DOMAIN="${DOMAIN:-$(sed -n 's/^DOMAIN=//p' "$PROJECT_DIR/deploy/.env" | tr -d '\r' | tail -n1)}"
ACME_EMAIL="${ACME_EMAIL:-$(sed -n 's/^ACME_EMAIL=//p' "$PROJECT_DIR/deploy/.env" | tr -d '\r' | tail -n1)}"
DOMAIN="${DOMAIN:-formatabnt.com.br}"

# --- 8. Build das imagens ----------------------------------------------------
log "Construindo imagens (docker compose build)"
# Normaliza CRLF caso o .env tenha sido editado no Windows, depois exporta.
CLEAN_ENV="$(mktemp)"
tr -d '\r' < "$PROJECT_DIR/deploy/.env" > "$CLEAN_ENV"
set -a; . "$CLEAN_ENV"; set +a
rm -f "$CLEAN_ENV"
docker compose -f "$PROJECT_DIR/docker-compose.yml" build

# --- 9. Stack Swarm ----------------------------------------------------------
log "Publicando stack $STACK_NAME"
docker stack deploy --prune --resolve-image never -c "$PROJECT_DIR/deploy/stack.yml" "$STACK_NAME"
docker service update --force --no-resolve-image "${STACK_NAME}_api" "${STACK_NAME}_web" >/dev/null 2>&1 || true

# --- 10. nginx da borda (HTTP) ----------------------------------------------
log "Configurando nginx da borda para $DOMAIN"
if [ ! -f "$NGINX_SITE" ] || ! grep -q 'ssl_certificate' "$NGINX_SITE"; then
    cat > "$NGINX_SITE" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN};
    client_max_body_size 25m;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
fi
ln -sf ../sites-available/formatabnt.com.br "$NGINX_LINK"
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# --- 11. TLS via Certbot -----------------------------------------------------
if [ "$WITH_TLS" -eq 1 ] && [ -n "$ACME_EMAIL" ]; then
    if certbot certificates 2>/dev/null | grep -q "Domains: .*${DOMAIN}"; then
        log "Certificado para $DOMAIN ja existe; nada a fazer"
    else
        log "Emitindo certificado para $DOMAIN e www.$DOMAIN"
        certbot --nginx --non-interactive --agree-tos --redirect \
            -m "$ACME_EMAIL" -d "$DOMAIN" -d "www.${DOMAIN}" \
            || warn "Certbot falhou (DNS ainda aponta para outro host?). Rode novamente depois."
    fi
else
    [ "$WITH_TLS" -eq 1 ] && warn "ACME_EMAIL vazio em deploy/.env; TLS pulado."
fi

# --- 12. Verificacao ---------------------------------------------------------
log "Verificacao"
docker service ls | grep "$STACK_NAME" || true
for _ in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1; then
        curl -fsS http://127.0.0.1:8080/health; echo
        break
    fi
    sleep 2
done

log "Concluido. Servicos: docker service ls | grep $STACK_NAME"
