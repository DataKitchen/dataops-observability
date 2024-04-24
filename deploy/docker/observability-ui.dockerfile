ARG BASE_IMAGE_URL

FROM --platform=${BUILDPLATFORM} ${BASE_IMAGE_URL}debian:bookworm-slim AS build-image

WORKDIR /observability_ui
COPY observability_ui/ /observability_ui

SHELL ["/bin/bash", "--login", "-c"]

RUN apt-get update -y && \
  apt-get upgrade -y && \
  apt-get install curl -y && \
  apt-get install jq -y
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
RUN nvm install $(jq -r .engines.node package.json)
RUN npm install --global yarn
RUN yarn
RUN yarn build:ci


FROM ${BASE_IMAGE_URL}nginxinc/nginx-unprivileged:1.25

WORKDIR /observability_ui

COPY --from=build-image --chown=nginx:nginx /observability_ui/dist /observability_ui
COPY --from=build-image --chown=nginx:nginx /observability_ui/nginx.conf /etc/nginx/nginx.conf

RUN mv /observability_ui/auth /observability_ui/shell/
