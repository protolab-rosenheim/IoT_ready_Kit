FROM alpine:3.8

WORKDIR /usr/src/app
COPY ./requirements.txt /usr/src/app/requirements.txt

RUN apk --no-cache add \
        python3 \
        postgresql-libs \
        libstdc++ \
        lapack \
        git \
        libxml2 \
        libxslt \
        libffi \
        && \
    pip3 install --no-cache-dir --upgrade pip setuptools && \
    apk add --no-cache --virtual .build-deps \
        build-base \
        postgresql-dev \
        python3-dev \
        lapack-dev \
        gfortran \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
         && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-dependencies git+https://github.com/protolab-rosenheim/IoT_ready_Kit_Webservice && \
    rm -fr /root/.cache && \
    rm /usr/include/xlocale.h && \
    apk del .build-deps

COPY . .
ENV PYTHONPATH `pwd`/..

CMD [ "python3", "iot_ready_kit/" ]
