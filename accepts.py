
from __future__ import division

from twisted.python.log import err
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol
from twisted.internet.error import ConnectionClosed
from twisted.internet.defer import Deferred

from benchlib import Client, driver


class Client(Client):
    def __init__(self, reactor, portNumber):
        super(Client, self).__init__(reactor)
        self._portNumber = portNumber
        self._factory = ClientFactory()


    def _request(self):
        finished = Deferred()
        factory = ClientFactory()
        factory.protocol = Protocol
        factory.clientConnectionLost = factory.clientConnectionFailed = lambda connector, reason: finished.errback(reason)
        finished.addErrback(self._filterFinished)
        self._reactor.connectTCP('127.0.0.1', self._portNumber, factory)
        finished.addCallback(self._continue)
        finished.addErrback(self._stop)


    def _filterFinished(self, reason):
        reason.trap(ConnectionClosed)



def report(acceptCount, duration):
    print '%s accepts/sec (%s connections in %s seconds)' % (
        acceptCount / duration, acceptCount, duration)



class CloseConnection(Protocol):
    def makeConnection(self, transport):
        transport.loseConnection()



def main(reactor):
    duration = 5
    concurrency = 50

    factory = ServerFactory()
    factory.protocol = CloseConnection
    port = reactor.listenTCP(0, factory)

    client = Client(reactor, port.getHost().port)
    d = client.run(concurrency, duration)
    d.addCallbacks(report, err, callbackArgs=(duration,))
    return d



if __name__ == '__main__':
    driver(main)
