import json, threading, unittest, socket


class Connection(object):
    def __init__(self, socket):
        self.socket = socket
        self.dispatcher_thread = self.DispatcherThread(self)
        self.dispatcher_thread.start()
        
    class DispatcherThread(threading.Thread):
        def __init__(self, conn, *arg, **kw):
            self.conn = conn
            self.reader = json.ParserReader(self.conn.socket)
            threading.Thread.__init__(self, *arg, **kw)
          
        def run(self):
            for value in self.reader.read_values():
                self.conn.dispatch(value)

    def dispatch(self, value):
        pass

class ServerConnection(object):
    ClientConnection = Connection

    def __init__(self, socket):
        self.socket = socket
        self.dispatcher_thread = self.DispatcherThread(self)
        self.dispatcher_thread.start()

    class DispatcherThread(threading.Thread):
        def __init__(self, conn, *arg, **kw):
            self.conn = conn
            threading.Thread.__init__(self, *arg, **kw)

        def run(self):
            while True:
                socket, address = self.conn.socket.accept()
                self.dispatch_snd(socket, address)

        def dispatch(self, socket, address):
            self.conn.dispatch(self.ClientConnection(socket))

    def dispatch(self, conn):
        pass

class ThreadDispatcherMixin(object):
    def dispatch(self, *arg, **kw):
        thread = self.DispatchedThread(self, *arg, **kw)
        thread.start()

    class DispatchedThread(threading.Thread):
        def __init__(self, conn, *arg, **kw):
            self.conn = conn
            threading.Thread.__init__(self, args=arg, kwargs=kw)
            
        def run(self, *arg, **kw):
            return self.dispatch(*arg, **kw)

        def dispatch(self, *arg, **kw):
            pass


class TestConnection(unittest.TestCase):
    def test_read_value(self):
        class EchoServer(Connection):
            def dispatch(self, value):
                json.json(value, self.socket)

        sockets = [s.makefile('r+') for s in socket.socketpair()]
        reader = json.ParserReader(sockets[0])
        echo_server = EchoServer(sockets[1])

        obj = {'foo':1, 'bar':[1, 2]}
        json.json(obj, sockets[0])
        return_obj = reader.read_value()
        
        self.assertEqual(obj, return_obj)

if __name__ == "__main__":
    unittest.main()
