ARG BASE_IMAGE_URL
FROM ${BASE_IMAGE_URL}python:3.10-slim-bullseye AS build-image

WORKDIR /dk

# Based on https://docs.docker.com/engine/install/debian/#install-using-the-repository

RUN \
  apt-get update; \
  apt-get install -y ca-certificates curl git; \
  install -m 0755 -d /etc/apt/keyrings; \
  curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc; \
  chmod a+r /etc/apt/keyrings/docker.asc

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list

# Installing the docker CLI without the compose plugin
RUN apt-get update; apt-get install -y docker-ce-cli docker-compose-plugin-

RUN apt-get clean; rm -rf /var/lib/apt/lists/*

WORKDIR /dk

COPY ./pyproject.toml /dk
RUN pip install .[build,dev]
RUN rm -rf pyproject.toml build *.egg-info

CMD ["bash"]