
"""
Benchmark for Twisted Spread.
"""

from __future__ import division

from twisted.spread.pb import PBServerFactory, PBClientFactory, Root
from twisted.python.log import err

from benchlib import Client, driver


class BenchRoot(Root):
    def remote_discard(self, argument):
        pass



class Client(Client):
    _structure = [
        'hello' * 100,
        {'foo': 'bar',
         'baz': 100,
         u'these are bytes': (1, 2, 3)}]

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


    def _request(self):
        d = self._reference.callRemote('discard', self._structure)
        d.addCallback(self._continue)
        d.addErrback(self._stop)



def report(requestCount, duration):
    print '%s requests/second (%s requests in %s seconds)' % (
        requestCount / duration, requestCount, duration)



def main(reactor):
    concurrency = 15
    duration = 5

    server = PBServerFactory(BenchRoot())
    port = reactor.listenTCP(0, server)
    client = Client(reactor, port.getHost().port)
    d = client.run(concurrency, duration)
    d.addCallbacks(report, err, callbackArgs=(duration,))
    return d


if __name__ == '__main__':
    driver(main)
