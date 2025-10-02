FROM python:3.10-alpine

WORKDIR /rustdesk-api-server

# Copy requirements first for better build caching
COPY requirements.txt .

# Install runtime dependencies, build dependencies, then clean up build deps
RUN apk add --no-cache \
    zlib \
    jpeg \
    libpng \
    freetype \
    mariadb-connector-c \
    && apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    linux-headers \
    mariadb-connector-c-dev \
    pkgconfig \
    zlib-dev \
    jpeg-dev \
    libpng-dev \
    freetype-dev \
    && pip install --no-cache-dir --disable-pip-version-check -r requirements.txt \
    && apk del .build-deps

# Copy the rest of the application
COPY . .

# Backup database directory
RUN cp -r ./db ./db_bak

ENV HOST="0.0.0.0"
ENV TZ="Asia/Shanghai"

EXPOSE 21114/tcp
EXPOSE 21114/udp

ENTRYPOINT ["sh", "run.sh"]
