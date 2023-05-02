FROM jamesstevens/gunicorn-flask

RUN apk update
RUN apk upgrade
RUN apk add py3-dnspython

COPY python /opt/python/
RUN python3 -m compileall /opt/python
