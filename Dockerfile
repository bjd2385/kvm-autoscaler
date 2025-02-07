ARG IMAGE=python
ARG TAG=3.13.2

FROM ${IMAGE}:${TAG} AS base

SHELL [ "/bin/bash", "-c" ]

ENV PREMISCALE_TOKEN="" \
    PREMISCALE_CONFIG_PATH=/opt/premiscale/config.yaml \
    PREMISCALE_PID_FILE=/opt/premiscale/premiscale.pid \
    PREMISCALE_LOG_LEVEL=info \
    PREMISCALE_PLATFORM=app.premiscale.com \
    PREMISCALE_CACERT="" \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

# https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys
LABEL org.opencontainers.image.description "© PremiScale, Inc. 2024"
LABEL org.opencontainers.image.licenses "BSL 1.1"
LABEL org.opencontainers.image.authors "Emma Doyle <emma@premiscale.com>"
LABEL org.opencontainers.image.documentation "https://premiscale.com"

USER root

# https://github.com/krallin/tini
ARG TINI_VERSION=v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ARG LIBVIRT_DEV_VERSION=9.0.0-4
RUN apt update && apt list -a libvirt-dev && apt install -y libvirt-dev=${LIBVIRT_DEV_VERSION} \
    && rm -rf /var/apt/lists/* \
    && groupadd premiscale --gid 1001 \
    && useradd -rm -d /opt/premiscale -s /bin/bash -g premiscale -u 1001 premiscale

ENV PATH=/opt/premiscale/.local/bin:/opt/premiscale/bin:${PATH}
WORKDIR /opt/premiscale

RUN chown -R premiscale:premiscale .

USER premiscale

RUN mkdir -p "$HOME"/.ssh/ "$HOME"/.local/bin \
    && touch "$HOME"/.ssh/config

## Production image

FROM base AS production

ARG PYTHON_USERNAME
ARG PYTHON_PASSWORD
ARG PYTHON_REPOSITORY
ARG PYTHON_INDEX=https://${PYTHON_USERNAME}:${PYTHON_PASSWORD}@repo.ops.premiscale.com/repository/${PYTHON_REPOSITORY}/simple
ARG PYTHON_PACKAGE_VERSION=0.0.1

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --no-input --extra-index-url="${PYTHON_INDEX}" premiscale=="${PYTHON_PACKAGE_VERSION}" \
    && premiscale --version

ENTRYPOINT [ "/tini", "--" ]
CMD [ "bash", "-c", "premiscale --log-stdout" ]

## Development image

FROM base AS develop

ENV POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VERSION=1.8.3 \
    POETRY_CACHE_DIR=/opt/premiscale/poetry-cache

COPY --chown=premiscale:premiscale src/ ./src/
COPY --chown=premiscale:premiscale README.md LICENSE poetry.lock pyproject.toml requirements.txt ./

RUN mkdir -p ${POETRY_CACHE_DIR}

ADD --chown=premiscale:premiscale https://install.python-poetry.org ./install-poetry.py
RUN --mount=type=cache,target=${HOME}/.local/bin,uid=1001,gid=1001 python install-poetry.py \
    && rm install-poetry.py
RUN --mount=type=cache,target=${POETRY_CACHE_DIR},uid=1001,gid=1001 poetry install --without=dev --with=profile \
    && poetry run premiscale --version
RUN poetry install --without=dev

ENTRYPOINT [ "/tini", "--" ]
CMD [ "bash", "-c", "poetry run premiscale --log-stdout --log-level=${PREMISCALE_LOG_LEVEL}" ]