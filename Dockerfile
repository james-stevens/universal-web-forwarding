FROM jamesstevens/gunicorn-flask

RUN apk update
RUN apk upgrade
RUN apk add py3-dnspython
RUN apk add bind

RUN mkdir -p /usr/local/etc /usr/local/bin /etc/inittab.d
COPY inittab_bind /etc/inittab.d

COPY named.conf /usr/local/etc
COPY start_bind /usr/local/bin

COPY python /opt/python/
RUN python3 -m compileall /opt/python
