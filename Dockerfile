FROM jamesstevens/gunicorn-flask

COPY uwf/*.py /usr/local/uwf/
RUN python3 -m compileall /usr/local/uwf

CMD [ "/sbin/init" ]
