ARG BASE_IMAGE_URL

FROM --platform=${BUILDPLATFORM} ${BASE_IMAGE_URL}node:23.11.1-alpine3.22 AS build-image

WORKDIR /observability_ui
COPY observability_ui/ /observability_ui

RUN yarn
RUN yarn build:ci

FROM ${BASE_IMAGE_URL}nginxinc/nginx-unprivileged:alpine3.22

WORKDIR /observability_ui

ENV OBSERVABILITY_API_HOSTNAME=
ENV OBSERVABILITY_CSP_EXTRA=
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx

COPY --from=build-image --chown=nginx:nginx /observability_ui/dist /observability_ui
COPY --from=build-image --chown=nginx:nginx /observability_ui/nginx.conf /etc/nginx/templates/nginx.conf.template

RUN mv /observability_ui/auth /observability_ui/shell/
