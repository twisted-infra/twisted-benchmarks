"""
Benchmark for Twisted Spread.
"""

from twisted.python.compat import _PY3
from twisted.spread.pb import PBClientFactory, PBServerFactory, Root

from benchlib import Client, driver


_structure = [
    b'hello' * 100,
    {
        b'bytestring key': b'val',
        'nativestr': 100,
        u'these are bytes': (1, 2, 3),
    },
]


class BenchRoot(Root):
    def remote_discard(self, argument):
        assert argument == _structure


class Client(Client):
    def __init__(self, reactor, port):
        super(Client, self).__init__(reactor)
        self._port = port

    def run(self, *args, **kwargs):
        def connected(reference):
            self._reference = reference
            return super(Client, self).run(*args, **kwargs)

        client = PBClientFactory()
        d = client.getRootObject()
        d.addCallback(connected)
        self._reactor.connectTCP('127.0.0.1', self._port, client)
        return d

    def cleanup(self):
        self._reference.broker.transport.loseConnection()

    def _request(self):
        d = self._reference.callRemote('discard', _structure)
        d.addCallback(self._continue)
        d.addErrback(self._stop)


def main(reactor, duration):
    concurrency = 15

    server = PBServerFactory(BenchRoot())
    port = reactor.listenTCP(0, server)
    client = Client(reactor, port.getHost().port)
    d = client.run(concurrency, duration)

    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d

    d.addCallback(cleanup)
    return d


if __name__ == '__main__':
    import sys
    import pb

    driver(pb.main, sys.argv)
