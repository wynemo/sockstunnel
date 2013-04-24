#!/usr/bin/env python
#coding:utf-8
import socket
import sys
import select
import SocketServer
import struct
import logging
import ssl

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class Encoder(SocketServer.StreamRequestHandler):

    def handle_tcp(self, sock, ssl_socket, addr1, port1):
        fdset = [sock, ssl_socket]

        data = addr1 + ':' + str(port1) + '\r\n'
        rv = ssl_socket.send(data)
        logging.info('connecting to ' + addr1 + ':' + str(port1))

        while True:
            r, w, e = select.select(fdset, [], [])
            try:
                if sock in r:
                    if ssl_socket.send(sock.recv(64*1024)) <= 0:
                        break
                if ssl_socket in r:
                    if sock.send(ssl_socket.recv(64*1024)) <= 0:
                        break
            except socket.sslerror as e:
                if e.args[0] == socket.SSL_ERROR_EOF:
                    break
                else:
                    raise

    def handle(self):
        try:
            logging.info('socks connection from ' + str(self.client_address))
            sock = self.connection
            # 1. Version
            sock.recv(262)
            sock.send(b"\x05\x00");
            # 2. Request
            data = self.rfile.read(4)
            mode = ord(data[1])
            addrtype = ord(data[3])
            if addrtype == 1:       # IPv4
                addr = socket.inet_ntoa(self.rfile.read(4))
            elif addrtype == 3:     # Domain name
                addr = self.rfile.read(ord(sock.recv(1)[0]))
            port = struct.unpack('>H', self.rfile.read(2))
            reply = b"\x05\x00\x00\x01"
            try:
                if mode == 1:  # 1. Tcp connect
                    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ssl_socket = ssl.wrap_socket(remote, ssl_version=ssl.PROTOCOL_TLSv1)
                    i = 0
                    l = [('server_ip', 51888)]
                    ssl_socket.connect(l[i])
                else:
                    reply = b"\x05\x07\x00\x01" # Command not supported
                local = remote.getsockname()
                reply += socket.inet_aton(local[0]) + struct.pack(">H", local[1])
            except socket.error:
                # Connection refused
                reply = '\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00'
            sock.send(reply)
            # 3. Transfering
            if reply[1] == '\x00':  # Success
                if mode == 1:    # 1. Tcp connect
                    self.handle_tcp(sock, ssl_socket, addr, port[0])
        finally:
            try:
                ssl_socket.close()
            except:
                pass

def main():
    level = logging.INFO
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=level)
    server = ThreadingTCPServer(('127.0.0.1', 7000), Encoder)
    server.serve_forever()
if __name__ == '__main__':
    main()
