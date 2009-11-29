"""httpd-pyev -- A "hello world" web server implemented using pyev.

Copyright (c) 2009, Ben Weaver.  All rights reserved.
This software is issued "as is" under a BSD license
<http://orangesoda.net/license.html>.  All warranties disclaimed.

"""

import sys, io, socket, pyev, signal

def handle(conn):
    data = conn.read(io.DEFAULT_BUFFER_SIZE)
    print('%d bytes:' % len(data), data)
    conn.write(b'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\nContent-Length:13\r\n\r\nHello, world!')

class server(object):

    def __init__(self, handle):
        self.handle = handle

    def __call__(self, addr='127.0.0.1', port=8080, backlog=None):
        sock = self.listen(addr, port, backlog)
        try:
            self.serve(sock)
        finally:
            sock.close()

    def listen(self, addr, port, backlog=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((addr, port))
        sock.listen(socket.SOMAXCONN if backlog is None else backlog)
        sock.setblocking(0)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        return sock

    def serve(self, sock, nevents=None):
        loop = pyev.default_loop()

        self.clients = {}
        main = pyev.Io(sock, pyev.EV_READ, loop, self.accept, data=sock)
        main.start()

        sigint = pyev.Signal(signal.SIGINT, loop, self.sigint, data=[main])
        sigint.start()

        loop.loop()

    def sigint(self, watcher, events):
        try:
            for w in self.clients.keys():
                self.finish(w)
            for w in watcher.data:
                w.stop()
        finally:
            watcher.loop.unloop()

    def accept(self, watcher, events):
        sock, addr = watcher.data.accept()
        sock.setblocking(0)

        conn = connection(sock)
        wc = pyev.Io(sock, pyev.EV_READ, watcher.loop, self.read)
        self.clients[wc] = conn
        wc.start()

    def read(self, watcher, events):
        conn = self.clients[watcher]
        if conn._fill_buffer():
            self.handle(conn)
        else:
            self.finish(watcher)

    def finish(self, watcher):
        watcher.stop()
        self.clients.pop(watcher).close()

class connection(socket.SocketIO):

    def __init__(self, sock):
        super(connection, self).__init__(sock, 'rwb')

        self._rpos = self._rlen = 0
        self._rbuf = bytearray(io.DEFAULT_BUFFER_SIZE)

    def readinto(self, b):
        self._checkClosed()
        self._checkReadable()
        return self._readinto_from_buffer(b)

    def _readinto_from_buffer(self, b):
        size = min(self._rlen, len(b)); end = self._rpos + size
        b[0:size] = self._rbuf[self._rpos:end]
        self._rpos = end; self._rlen -= size
        return size

    def _fill_buffer(self):
        self._rpos = 0
        self._rlen = self._sock.recv_into(self._rbuf)
        return self._rlen

    def close(self):
        return self._sock.close()

if __name__ == '__main__':
    server(handle)()
