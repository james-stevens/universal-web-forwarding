FROM jamesstevens/gunicorn-flask

COPY python/*.py /usr/local/python/
RUN python3 -m compileall /usr/local/python

CMD [ "/sbin/init" ]
