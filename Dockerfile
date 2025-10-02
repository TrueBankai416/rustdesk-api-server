FROM python:3.10-alpine

WORKDIR /rustdesk-api-server
ADD . /rustdesk-api-server

# Install build dependencies and Python packages, then clean up
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    linux-headers \
    mariadb-connector-c-dev \
    pkgconfig \
    zlib-dev \
    jpeg-dev \
    freetype-dev \
    && pip install --no-cache-dir --disable-pip-version-check -r requirements.txt \
    && apk del .build-deps \
    && cp -r ./db ./db_bak

ENV HOST="0.0.0.0"
ENV TZ="Asia/Shanghai"

EXPOSE 21114/tcp
EXPOSE 21114/udp

ENTRYPOINT ["sh", "run.sh"]
