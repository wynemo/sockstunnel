#!/usr/bin/env python
#coding:utf-8
# please use tornado 3

import socket
import tornado.ioloop
import tornado.tcpserver
import ssl
import sys

flush = sys.stdout.flush

def pipe(stream_a, stream_b, addr):

    def write_to(stream):
        def on_data(data):
            if data:
                if not stream.closed():
                    stream.write(data)
        return on_data

    def remote_close(stream):
        def on_data(data):
            if not stream.writing():
                stream.close()
            else:
                print addr, 'remote close client writing', stream.writing()
                flush()
                
        return on_data

    def on_a_close():
        stream_b.close()

    writer_a = write_to(stream_a)
    writer_b = write_to(stream_b)
    stream_a.set_close_callback(on_a_close)
    if stream_a.closed():
        stream_b.close()
    if stream_b.closed():
        stream_a.close()
    if not stream_a.closed() and not stream_b.closed():
        stream_a.read_until_close(writer_b, writer_b)
        stream_b.read_until_close(remote_close(stream_a), writer_a)


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


class ProxyHandler:

    def on_self_header(self, remote_info):
        data = remote_info[:-2]
        pos = data.find(':')
        addr = data[:pos]
        port = int(data[pos + 1:])
        print addr, port
        flush()
        self.addr = addr
        self.connector.connect(addr, port, self.on_connected)

    def on_connected(self, outgoing):
        if outgoing is not None:
            pipe(self.incoming, outgoing, self.addr)
        else:
            self.incoming.close()

    def __init__(self, stream, connector):
        self.connector = connector

        self.incoming = stream
        self.incoming.read_until(b'\r\n', self.on_self_header)


class ProxyServer(tornado.tcpserver.TCPServer):

    def __init__(self, connector=None):
        d1 = {"certfile": "cacert.pem", "keyfile": "privkey.pem",
              "ssl_version": ssl.PROTOCOL_TLSv1}
        tornado.tcpserver.TCPServer.__init__(self, ssl_options=d1)
        if connector is None:
            self.connector = DirectConnector()
        else:
            self.connector = connector

    def handle_stream(self, stream, address):
        ProxyHandler(stream, self.connector)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 51888
    host = '0.0.0.0'
    connector = DirectConnector()
    server = ProxyServer(connector)
    server.listen(port, host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
