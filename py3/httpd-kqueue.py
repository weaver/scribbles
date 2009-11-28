"""httpd-kqueue -- A "hello world" web server implemented using kqueue.

Copyright (c) 2009, Ben Weaver.  All rights reserved.
This software is issued "as is" under a BSD license
<http://orangesoda.net/license.html>.  All warranties disclaimed.

http://scotdoyle.com/python-epoll-howto.html
http://wiki.netbsd.se/kqueue_tutorial
"""
import sys, io, socket, select, errno

def handle(conn, hint):
    print('%d bytes:' % hint, conn.read(hint))
    conn.write(b'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\nContent-Length:13\r\n\r\nHello, world!')

class server(object):

    def __init__(self, handle):
        self.handle = handle

    def __call__(self, addr='127.0.0.1', port=8080, backlog=None, nevents=None):
        sock = self.listen(addr, port, backlog)
        try:
            self.serve(sock, nevents)
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
        mgr = manager()
        nevents = socket.SOMAXCONN if nevents is None else nevents

        with kqueue() as kq:

            sockno = mgr.add(kq.event(sock), sock).fileno()
            while True:

                events = kq(nevents)
                if not events:
                    raise RuntimeError('serve: kqueue returned an empty list of events.')

                for event in events:
                    if event.flags & kq.ERROR:
                        self.error(mgr.get(event), kq.error(event))
                    elif event.ident == sockno:
                        conn = self.start(sock)
                        mgr.add(kq.event(conn), conn)
                    else:
                        if event.flags & kq.READ and event.data > 0:
                            self.handle(mgr.get(event), event.data)
                        if event.flags & kq.EOF:
                            self.finish(mgr.pop(event))

    def error(self, conn, message):
        print('ERROR', conn and conn.getsockname(), message)

    def start(self, sock):
        conn, addr = sock.accept()
        conn.setblocking(0)
        return conn

    def finish(self, conn):
        ## Closing the socket deletes any associated events.
        conn.close()

class kqueue(object):
    ADD = select.KQ_EV_ADD
    ENABLE = select.KQ_EV_ENABLE
    ERROR = select.KQ_EV_ERROR
    EOF = select.KQ_EV_EOF

    READ = select.KQ_FILTER_READ
    WRITE = select.KQ_FILTER_WRITE

    def __init__(self):
        self._kq = select.kqueue()
        self._changes = []

    def __call__(self, nevents):
        events = self._kq.control(self._changes, nevents)
        del self._changes[:]
        return events

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def event(self, sock, filters=READ, flags=(ADD | ENABLE)):
        event = select.kevent(sock.fileno(), filters, flags)
        self._changes.append(event)
        return event

    def close(self):
        return self._kq.close()

    def error(self, event):
        return errno.errorcode[event.data]

class manager(object):

    def __init__(self):
        self._conn = {}

    def add(self, event, sock):
        self._conn[event.ident] = conn = connection(sock, 'rwb')
        return conn

    def get(self, event):
        return self._conn.get(event.ident)

    def pop(self, event):
        return self._conn.pop(event.ident)

class connection(socket.SocketIO):

    def close(self):
        return self._sock.close()

if __name__ == '__main__':
    server(handle)()
