#! /usr/bin/python3
# (c) Copyright 2023-2023, James Stevens ... see LICENSE for details
# Alternative license arrangements possible, contact me for more information

import os
import socket
import random
import flask
import resolv
import dns.rdatatype

RR_URI = dns.rdatatype.from_text("URI")
RR_TXT = dns.rdatatype.from_text("TXT")

def abort(err_no, message):
    response = flask.jsonify({'error': message})
    response.status_code = err_no
    return response



application = flask.Flask("Universal Web Redirect")
qry = resolv.Query()
qry.servers = os.environ["NAME_SERVERS"].split(",") if "NAME_SERVERS" in os.environ else ["8.8.8.8","8.8.4.4"]
qry.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def redirect_user(header,text):
    host = "_http._tcp."+ (header["X-Host"] if "X-Host" in header else header["Host"])
    if host.find(":") > 0:
        host = host.split(":")[0]

    qry.name = host
    qry.rdtype = RR_URI
    msg = qry.resolv()
    if msg.rcode() == 0 and len(msg.answer) == 0:
        qry.rdtype = RR_TXT
        msg = qry.resolv()

    redirect_code = 301
    if msg.rcode() == 0 and len(msg.answer) > 0:
        uris = [ i.to_text() for rr in msg.answer for i in rr]
        if len(uris) > 1:
            redirect_code = 302
            random.shuffle(uris)
        send_them_to = uris[0].strip('"') + "/$$"
        if send_them_to[-3:] == "/$$":
            send_them_to = send_them_to[:-2] + text
        ttl = max([ rr.ttl for rr in msg.answer])
        response = flask.redirect(send_them_to,code=redirect_code)
        response.headers={'Cache-Control': f"max-age={ttl}"}
        return response

    return abort(499,"what")


@application.route('/<path:text>', methods=['GET','POST'])
def redirect_text(text):
    return redirect_user(flask.request.headers,text)

@application.route('/', methods=['GET','POST'])
def redirect_none():
    return redirect_user(flask.request.headers,"")


if __name__ == "__main__":
    application.run()
