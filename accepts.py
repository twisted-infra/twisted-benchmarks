
from twisted.internet.protocol import ServerFactory, ClientFactory, Protocol
from twisted.internet.error import ConnectionClosed
from twisted.internet.defer import Deferred

from benchlib import Client, driver


class Client(Client):
    def __init__(self, reactor, address, portNumber):
        super(Client, self).__init__(reactor)
        self._address = address
        self._portNumber = portNumber
        self._factory = ClientFactory()


    def _request(self):
        finished = Deferred()
        factory = ClientFactory()
        factory.protocol = Protocol
        factory.clientConnectionLost = factory.clientConnectionFailed = lambda connector, reason: finished.errback(reason)
        finished.addErrback(self._filterFinished)
        self._reactor.connectTCP(self._address, self._portNumber, factory, bindAddress=(self._address, 0))
        finished.addCallback(self._continue)
        finished.addErrback(self._stop)


    def _filterFinished(self, reason):
        reason.trap(ConnectionClosed)


class CloseConnection(Protocol):
    def makeConnection(self, transport):
        transport.loseConnection()


interface = 0
def main(reactor, duration):
    global interface
    concurrency = 50

    factory = ServerFactory()
    factory.protocol = CloseConnection

    interface += 1
    interface %= 255
    port = reactor.listenTCP(0, factory, interface='127.0.0.%d' % (interface,))

    client = Client(reactor, port.getHost().host, port.getHost().port)
    d = client.run(concurrency, duration)
    return d



if __name__ == '__main__':
    import sys
    import accepts
    driver(accepts.main, sys.argv)
