#! /usr/bin/python3
# (c) Copyright 2023-2023, James Stevens ... see LICENSE for details
# Alternative license arrangements possible, contact me for more information

import os
import random
import flask
from dns import rdatatype

import resolver

RR_URI = rdatatype.from_text("URI")
RR_TXT = rdatatype.from_text("TXT")


def abort(err_no, message):
    return flask.make_response(message+"\n", err_no)


application = flask.Flask("Universal Web Redirect")
qry = resolver.Query(os.environ["PYTHON_NAME_SERVERS"].split(" ")
                     if "PYTHON_NAME_SERVERS" in os.environ else ["127.0.0.1"])


def strip_uri(uri):
    if (pos := uri.find('"')) >= 0:
        return uri[pos + 1:].strip('"')
    return uri.strip('"')


def get_uris(msg):
    return [strip_uri(i.to_text()) for rr in msg.answer for i in rr]


def redirect_user(request, text):
    host = None
    if "X-Host" in request.headers:
        host = request.headers["X-Host"]
    elif "Host" in request.headers:
        host = request.headers["Host"]
    else:
        return abort(499, "No host name header record found")

    if host.find(":") > 0:
        host = host.split(":")[0]

    uris = None
    qry.query("_http._tcp." + host, RR_URI)
    msg = qry.resolv()
    if msg.rcode() == 0:
        if len(msg.answer) > 0:
            uris = get_uris(msg)
        else:
            qry.query("_http._tcp." + host, RR_TXT)
            msg = qry.resolv()
            if msg.rcode() == 0 and len(msg.answer) > 0:
                uris = get_uris(msg)

    if uris is None or len(uris) <= 0:
        return abort(499, f"No URI or TXT record found for host '{host}'")

    redirect_code = 301
    if len(uris) > 1:
        redirect_code = 302
        random.shuffle(uris)

    send_them_to = uris[0]

    if send_them_to[-3:] == "/$$":
        send_them_to = send_them_to[:-2] + text
        if len(request.query_string) > 0:
            send_them_to = send_them_to + "?" + request.query_string.decode(
                "utf-8")

    ttl = max([rr.ttl for rr in msg.answer])

    response = flask.redirect(send_them_to, code=redirect_code)
    response.headers['Cache-Control'] = f"max-age={ttl}"
    return response


@application.route('/<path:text>', methods=['GET', 'POST'])
def redirect_text(text):
    return redirect_user(flask.request, text)


@application.route('/', methods=['GET', 'POST'])
def redirect_none():
    return redirect_user(flask.request, "")


if __name__ == "__main__":
    application.run()
