# DEV NOTE:  YOU MUST RUN `docker build` FROM THE TOP-LEVEL OF `observability-be` AND POINT TO THIS FILE.
ARG BASE_IMAGE_URL
FROM ${BASE_IMAGE_URL}python:3.10-slim-bullseye AS build-image
LABEL maintainer="DataKitchen"

COPY pyproject.toml /tmp/dk/
#           -O: Strips asserts from the code which removes some unnecessary codepaths resulting in a small
#               performance improvement
#      /tmp/dk: The package source folder
# --prefix=/dk: The destination installation environment folder
RUN python3 -O -m pip install /tmp/dk --prefix=/dk

# Copy and build the actual application
COPY . /tmp/dk/
ENV PYTHONPATH ${PYTHONPATH}:/dk/lib/python3.10/site-packages
#    --no-deps: The previous pip layer will have already installed the dependencies. This
#               will disable doing a second dependency resolution check.
#           -O: Strips asserts from the code which removes some unnecessary codepaths resulting in a small
#               performance improvement
#      /tmp/dk: The package source folder
# --prefix=/dk: The destination installation environment folder
RUN python3 -O -m pip install --no-deps /tmp/dk --prefix=/dk

FROM ${BASE_IMAGE_URL}python:3.10-slim-bullseye AS runtime-image

# Grab the pre-built app from the build-image. This way we don't have
# excess laying around in the final image.
COPY --from=build-image /dk /dk
COPY --from=build-image /tmp/dk/deploy/conf/gunicorn.conf.py /dk/

ENV PYTHONPATH ${PYTHONPATH}:/dk/lib/python3.10/site-packages
ENV PATH ${PATH}:/dk/bin
