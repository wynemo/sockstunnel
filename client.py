#!/usr/bin/env python
#coding:utf-8
import socket, sys, select, SocketServer, struct, time, ssl

  
class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass
class Encoder(SocketServer.StreamRequestHandler):
    def log1(self,str1):
        print(time.asctime(time.localtime(time.time()))),' ',str1
    def handle_tcp(self, sock,sslsocket,addr1,port1):
        init = 0
        fdset = [sock, sslsocket]

        while True:
            r, w, e = select.select(fdset, [], [])
            if 0 == init:
                data = addr1 + ',' + str(port1)
                rv = sslsocket.send(data)
                rt = sslsocket.recv(10)
                if rt == 'success':
                    init = 1
                continue
            try:
                if sock in r:
                    if sslsocket.send(sock.recv(4096)) <= 0:
                        break
                if sslsocket in r:
                    if sock.send(sslsocket.recv(4096)) <= 0:
                        break
            except socket.sslerror, x:
                if x.args[0] == socket.SSL_ERROR_EOF:
                    break
                else:
                    raise

    def handle(self):
        try:
            self.log1('socks connection from '+str(self.client_address))
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
                    sslSocket = ssl.wrap_socket(remote,ssl_version=ssl.PROTOCOL_TLSv1)
                    sslSocket.connect(('server_ip', 9999))
                    #self.log1(' Tcp connect to '+addr+' '+str(port[0]))
                else:
                    reply = b"\x05\x07\x00\x01" # Command not supported
                local = remote.getsockname()
                #print 'local is ',local
                reply += socket.inet_aton(local[0]) + struct.pack(">H", local[1])
            except socket.error:
                # Connection refused
                reply = '\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00'
            sock.send(reply)
            # 3. Transfering
            if reply[1] == '\x00':  # Success
                if mode == 1:    # 1. Tcp connect
                    self.handle_tcp(sock,sslSocket,addr,port[0])
        finally:
            try:
                sslSocket.close()
            except:
                pass

def main():
    server = ThreadingTCPServer(('127.0.0.1', 7000), Encoder)
    server.serve_forever()
if __name__ == '__main__':
    main()
