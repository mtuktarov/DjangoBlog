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
    apk add memcached libssl1.1 libcrypto1.1 libpq postgresql-client && \
    pip install -U pip django==2.2.8 && \
    pip install -Ur requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*
USER blogd
CMD [ "/bin/sh", "-c", "\
    test $(echo $WAIT_FOR_POSTGRES | tr [A-Z] [a-z]) = true ; \
    while true ; do psql -c \"SELECT datname FROM pg_database WHERE datistemplate = false;\" && sleep 10 && break || sleep 10 ; done ; ; \
    test $(echo $ADD_SUPERUSER | tr [A-Z] [a-z]) = true && ./manage.py createsuperuser ; \
    test $(echo $CONFIGURE_GROUPS | tr [A-Z] [a-z]) = true && ./manage.py configure_groups  ; \
    test $(echo $RENAME_SITE | tr [A-Z] [a-z]) = true && ./manage.py rename_site  ; \
    test $(echo $MAKEMIGRATIONS | tr [A-Z] [a-z]) = true && ./manage.py makemigrations ; \
    test $(echo $MIGRATE | tr [A-Z] [a-z]) = true && ./manage.py migrate ; \
    test $(echo $COLLECT_STATIC | tr [A-Z] [a-z]) = true && ./manage.py collectstatic --noinput ; \
    test $(echo $COMPRESS_STATIC | tr [A-Z] [a-z]) = true && ./manage.py compress --force ; \
    test $(echo $DJANGO_DISABLE_CACHE | tr [A-Z] [a-z]) = true ||  memcached -d ; \
    uwsgi $UWSGI_PARAMS"]
