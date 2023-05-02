#! /usr/bin/python3
# (c) Copyright 2019-2022, James Stevens ... see LICENSE for details
# Alternative license arrangements possible, contact me for more information
""" module to resolve DNS queries into DoH JSON objects """

from syslog import syslog
import socket
import select
import argparse
import dns
import dns.name
import dns.message
import dns.rdatatype
import random

import validation

DNS_MAX_RESP = 4096
MAX_TRIES = 10

id_list = [ (int(x/255),x%255) for x in range(1,65535) ]
random.shuffle(id_list)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class ResolvError(Exception):
    """ custom error """


class Query:  # pylint: disable=too-few-public-methods
    """ build a DNS query & resolve it """
    def __init__(self):
        self.name = None
        self.rdtype = None
        self.servers = ["8.8.8.8", "1.1.1.1"]
        self.sock = None
        self.next_id_item = 0

    def resolv(self):
        """ resolve the query we hold """
        res = Resolver(self)
        res.sock = self.sock
        return res.recv()


class Resolver:
    """ resolve a DNS <Query> """
    def __init__(self, qry):
        self.qry_id = None
        self.reply = None
        self.sock = None
        self.qry = qry

        if isinstance(self.qry.rdtype, int):
            self.qry.rdtype = int(self.qry.rdtype)
        else:
            try:
                self.qry.rdtype = dns.rdatatype.from_text(self.qry.rdtype)
            except dns.rdatatype.UnknownRdatatype:
                raise ResolvError("Invalid RD type")


        for each_svr in self.qry.servers:
            if not validation.is_valid_ipv4(each_svr):
                raise ResolvError("Invalid IP v4 Address for a Server")

        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if self.sock is None:
            raise ResolvError("Failed to open UDP client socket")

        self.expiry = 1
        self.tries = 0
        self.name = qry.name

    def send_all(self):
        """ send the query to all servers """
        ret = False
        for each_svr in self.qry.servers:
            try:
                sent_len = self.sock.sendto(self.question, (each_svr, 53))
                ret = ret or (sent_len == len(self.question))
            except Exception as err:
                syslog(str(err))

        return ret  # True if at least one worked

    def send(self):
        """ send the DNS query out """
        if self.question is None:
            return None

        self.qry_id = id_list[self.qry.next_id_item]
        self.qry.next_id_item = self.qry.next_id_item+1 if self.qry.next_id_item < len(id_list) else 0
        self.question[0] = self.qry_id[0]
        self.question[1] = self.qry_id[1]
        return self.send_all()

    def match_id(self):
        """ check the DNS quiery Id field matches what we asked """
        return (self.qry_id is not None and self.reply[0] == self.qry_id[0]
                and self.reply[1] == self.qry_id[1])

    def recv(self, binary_format=False):
        """ look for dns UDP response and read it """

        msg = dns.message.make_query(self.qry.name, self.qry.rdtype)
        self.question = bytearray(msg.to_wire())

        while self.tries < MAX_TRIES:
            if not self.send():
                return None

            while True:
                rlist, _, _ = select.select([self.sock], [], [], self.expiry)
                if len(rlist) <= 0:
                    break

                self.reply, (addr, _) = self.sock.recvfrom(DNS_MAX_RESP)
                if self.match_id():
                    return dns.message.from_wire(self.reply)

            self.expiry += int(self.expiry / 2) if self.expiry > 2 else 1
            self.tries += 1

        return None


def main():
    """ main """
    parser = argparse.ArgumentParser(
        description='This is a wrapper to test the resolver code')
    parser.add_argument("-s",
                        "--servers",
                        default="8.8.8.8,1.1.1.1",
                        help="Resolvers to query")
    parser.add_argument("-n",
                        "--name",
                        default="jrcs.net",
                        help="Name to query for")
    parser.add_argument("-t",
                        "--rdtype",
                        default="txt",
                        help="RR Type to query for")
    args = parser.parse_args()

    qry = Query()
    qry.name = args.name
    qry.rdtype = args.rdtype
    qry.sock = sock
    qry.servers = args.servers.split(",")
    msg = qry.resolv()
    print("RC:",msg.rcode(),msg.flags)
    print("QR:",msg.question)
    print("AN:",msg.answer)
    print("AT:",msg.authority)
 
    print("")
    qry.name="_http._tcp.twt.jrcs.net"
    msg = qry.resolv()
    print("RC:",msg.rcode(),msg.flags)
    print("QR:",msg.question)
    print("AN:",msg.answer)
    print("AT:",msg.authority)
    sock.close()


if __name__ == "__main__":
    main()
