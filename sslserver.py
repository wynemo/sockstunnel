import socket
import tornado.ioloop
import tornado.netutil
import ssl

def write_to(stream):
    def on_data(data):
        if len(data):
            if not stream.closed():
                stream.write(data)
    return on_data

def pipe(stream_a, stream_b):
    def on_a_close():
        print 'client close'
        stream_b.close()
    def on_b_close():
        print 'remote close'
        stream_a.close()
    def re_read(data):
        if len(data):
            if not stream_b.closed():
                stream_b.write(data)
        if not stream_a.closed() and not stream_b.closed():
            stream_a.read_bytes(4096,re_read,write_to(stream_b))
    writer_a = write_to(stream_a)
    writer_b = write_to(stream_b)
    stream_a.set_close_callback(on_a_close)
    stream_b.set_close_callback(on_b_close)
    if stream_a.closed():
        stream_b.close()
    if stream_b.closed():
        stream_a.close()
    #stream_a.read_until_close(writer_b,writer_b)
    if not stream_a.closed() and not stream_b.closed():
        stream_a.read_bytes(4096,re_read,writer_b)
        stream_b.read_until_close(writer_a,writer_a)

class DirectConnector():

    def connect(self, host, port, callback):

        def on_close():
            callback(None)

        def on_connected():
            stream.set_close_callback(None)
            callback(stream)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(s)
        stream.set_close_callback(on_close)
        stream.connect((host, port), on_connected)
        print host,port

class ProxyHandler:

    def on_self_header(self,remote_info):
        data = remote_info[:-2]
        pos = data.find(',')
        addr = data[:pos]
        port = int(data[pos+1:])
        self.outgoing = self.connector.connect(addr, port, self.on_connected)

    def on_connected(self, outgoing):
        if outgoing is not None:
            pipe(self.incoming, outgoing)
        else:
            self.incoming.close()

    def __init__(self, stream, connector):
        self.connector = connector

        self.incoming = stream
        self.incoming.read_until(b'\r\n', self.on_self_header)

class ProxyServer(tornado.netutil.TCPServer):

    def __init__(self, connector = None):
        d1 = {"certfile": "cacert.pem","keyfile": "privkey.pem",
            "ssl_version": ssl.PROTOCOL_TLSv1}
        tornado.netutil.TCPServer.__init__(self,ssl_options=d1)
        self.connector = DirectConnector()

    def handle_stream(self, stream, address):
        ProxyHandler(stream, self.connector)

def main():
    port = 59999
    host = '0.0.0.0'
    connector = DirectConnector()
    server = ProxyServer(connector)
    server.listen(port, host)
    tornado.ioloop.IOLoop.instance().start() 

if __name__ == '__main__': main()
