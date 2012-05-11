#install openssl
#sudo aptitude install python-openssl

#modified from http://xiaoxia.org/2011/03/29/written-by-python-socks5-server/ 
#copyring by original author

import ssl, socket, SocketServer, select

class SSlSocketServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def get_request(self):#overwritten
        newsocket, fromaddr = self.socket.accept()
        connstream = ssl.wrap_socket(newsocket,
            server_side=True,
            certfile="cacert.pem",
            keyfile="privkey.pem",
            ssl_version=ssl.PROTOCOL_TLSv1)
        return connstream, fromaddr

class Decoder(SocketServer.StreamRequestHandler):
    def handle_tcp(self, sock, remote):
        fdset = [sock, remote]
        while True:
            r, w, e = select.select(fdset, [], [])
            try:
                if sock in r:
                    if remote.send(sock.recv(4096)) <= 0:
                        break
                if remote in r:
                    if sock.send(remote.recv(4096)) <= 0:
                        break 
            except socket.sslerror, x:
                if x.args[0] == socket.SSL_ERROR_EOF:
                    break
                else:
                    raise

    def handle(self):
        socket1 = self.connection
        data = socket1.recv(4096)
        pos = data.find(',')
        if(pos != -1):
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                remote.connect((data[:pos], int(data[pos+1:])))
            except:
                print data[:pos],int(data[pos+1:])
                return
            socket1.send('success')
            try:
                self.handle_tcp(socket1,remote)
            finally:
                remote.close()

def main():
    server = SSlSocketServer(('0.0.0.0', 9999), Decoder)
    server.serve_forever()
if __name__ == '__main__':
    main()



#now test server

#import socket
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('localhost', 9999))
#sslSocket = socket.ssl(s)
#print repr(sslSocket.server())
#print repr(sslSocket.issuer())
#sslSocket.write('Hello secure socket\n')
#s.close()

