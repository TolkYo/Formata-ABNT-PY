FROM nginx:1.27-alpine

ENV API_HOST=api \
    API_PORT=8000

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY index.html /usr/share/nginx/html/index.html
COPY admin.html /usr/share/nginx/html/admin.html
COPY assets /usr/share/nginx/html/assets

EXPOSE 80
