#install openssl
#sudo aptitude install python-openssl

#modified from http://xiaoxia.org/2011/03/29/written-by-python-socks5-server/ 
#copyring by original author

#todo fix "Unexpected EOF"

from OpenSSL import SSL
import socket, SocketServer, select

class SSlSocketServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        SocketServer.BaseServer.__init__(self, server_address,
            RequestHandlerClass)
        ctx = SSL.Context(SSL.TLSv1_METHOD)
        cert = 'cacert.pem'
        key = 'privkey.pem'
        ctx.use_privatekey_file(key)
        ctx.use_certificate_file(cert)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
            self.socket_type))
        if bind_and_activate:
            self.server_bind()
            self.server_activate()
    def shutdown_request(self,request):
        request.shutdown()

class Decoder(SocketServer.StreamRequestHandler):
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

    def handle_tcp(self, sock, remote):
        fdset = [sock, remote]
        while True:
            r, w, e = select.select(fdset, [], [])
            if sock in r:
                if remote.send((sock.recv(4096))) <= 0:
                    break
            if remote in r:     
                if sock.send((remote.recv(4096))) <= 0:
                    break 

    def handle(self):
        try:
            socket1 = self.connection
            data = socket1.recv(4096)
            pos = data.find(',')
            if(pos != -1):
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((data[:pos], int(data[pos+1:])))
                socket1.send('success')
                self.handle_tcp(socket1,remote)
                remote.close()
        except Exception, e:
            print 'socket error',e
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

