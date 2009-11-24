
from __future__ import division

from twisted.python.log import err
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.names.dns import DNSDatagramProtocol
from twisted.names.server import DNSServerFactory
from twisted.names import hosts, client


class Client(object):
    _requestCount = 0

    def __init__(self, reactor, portNumber):
        self._reactor = reactor
        self._resolver = client.Resolver(servers=[('127.0.0.1', portNumber)])


    def run(self, duration):
        self._reactor.callLater(duration, self._stop, None)
        self._request()
        self._finished = Deferred()
        return self._finished


    def _request(self):
        d = self._resolver.lookupAddress('localhost')
        d.addCallback(self._continue)
        d.addErrback(self._stop)


    def _continue(self, ignored):
        self._requestCount += 1
        self._request()


    def _stop(self, reason):
        if self._finished is not None:
            finished = self._finished
            self._finished = None
            if reason is not None:
                finished.errback(reason)
            else:
                finished.callback(self._requestCount)



def report(requestCount, duration):
    print '%s req/sec (%s requests in %s seconds)' % (
        requestCount / duration, requestCount, duration)



def main():
    duration = 5
    controller = DNSServerFactory([hosts.Resolver()])
    port = reactor.listenUDP(0, DNSDatagramProtocol(controller))
    client = Client(reactor, port.getHost().port)
    d = client.run(duration)
    d.addCallbacks(report, err, callbackArgs=(duration,))
    d.addCallback(lambda ign: reactor.stop())
    reactor.run()


if __name__ == '__main__':
    main()
