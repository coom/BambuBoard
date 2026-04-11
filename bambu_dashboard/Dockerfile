ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache \
        python3 \
        py3-pip \
        py3-wheel \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev \
        openssl-dev

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

COPY backend /app/backend
COPY frontend /app/frontend
COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]
