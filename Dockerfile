FROM jamesstevens/gunicorn-flask

RUN apk update
RUN apk upgrade
RUN apk add py3-dnspython

COPY python /opt/python/
RUN python3 -m compileall /opt/python


RUN apk add bind
RUN mkdir -p /opt /opt/named /opt/named /opt/named/etc
RUN mkdir -p /opt/named/etc/bind /opt/named/zones /opt/named/var /opt/named/var/run
RUN cp -a /etc/bind/rndc.key /opt/named/etc/bind
RUN chown -R named: /opt/named/zones /opt/named/var
COPY named.conf /opt/named/etc/bind

RUN mkdir /etc/inittab.d
COPY inittab_bind /etc/inittab.d
