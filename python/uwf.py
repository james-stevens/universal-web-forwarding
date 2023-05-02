#! /usr/bin/python3
# (c) Copyright 2023-2023, James Stevens ... see LICENSE for details
# Alternative license arrangements possible, contact me for more information

import os
import flask
import resolv

def abort(err_no, message):
    response = flask.jsonify({'error': message})
    response.status_code = err_no
    return response


application = flask.Flask("UWF")

name_servers = os.environ["NAME_SERVERS"].split(",") if "NAME_SERVERS" in os.environ else ["8.8.8.8","8.8.4.4"]

@application.route('/<string:text>', methods=['GET'])
def redirect_user(text):

    print(flask.request.headers)
    host = "__webfwd."+flask.request.headers["Host"]
    if host.find(":") > 0:
        host = host.split(":")[0]

    qry = resolv.Query(host, "txt")
    qry.servers = name_servers
    msg = qry.resolv()

    print("RC:",msg.rcode(),msg.flags)
    print("QR:",msg.question)
    print("AN:",msg.answer)
    print("AT:",msg.authority)

    print(">>> http://"+host+"/"+text)
    return abort(499,"what")

if __name__ == "__main__":
    application.run()
