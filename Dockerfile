FROM python:3.8-alpine

ARG AUTOMATIC_MIGRATIONS=FALSE
ENV AUTOMATIC_MIGRATIONS=$AUTOMATIC_MIGRATIONS
RUN mkdir -p /opt/blogd
WORKDIR /opt/blogd
COPY requirements.txt /opt/blogd/requirements.txt
RUN addgroup -g 101 blogd                                        &&  \
    adduser -G blogd -u 101 -h /opt/blogd -s /bin/sh -D blogd    &&  \
    chown -R 101:101 /opt/blogd && \
    apk add --no-cache --virtual .build-deps zlib-dev gcc libc-dev libffi-dev postgresql-dev g++ && \
    apk add memcached libssl1.1 libcrypto1.1 libpq && \
    pip install -U pip django==2.2.8 && \
    pip install -Ur requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*
USER blogd
CMD [ "/bin/sh", "-c", "test $(echo $AUTOMATIC_MIGRATIONS | tr [A-Z] [a-z]) = true && ./manage.py makemigrations && ./manage.py migrate && ./manage.py silent_config ; ./manage.py collectstatic --noinput ; ./manage.py compress --force ; memcached -d ; uwsgi --ini ./blogd.ini" ]
