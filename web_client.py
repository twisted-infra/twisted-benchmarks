
"""
This benchmark runs a trivial Twisted Web server and client and makes as many
requests as it can in a fixed period of time.

A significant problem with this benchmark is the lack of persistent connections
in the HTTP client.  Lots of TCP connections means lots of overhead in the
kernel that's not really what we're trying to benchmark.  Plus lots of sockets
end up in TIME_WAIT which has a (briefly) persistent effect on system-wide
performance and makes consecutive runs of the benchmark vary wildly in their
results.
"""

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.defer import Deferred
from twisted.web.client import Agent
from twisted.python.compat import networkString
from twisted.web.client import ResponseDone

from benchlib import Client, driver


class BodyConsumer(Protocol):
    def __init__(self, finished):
        self.finished = finished


    def connectionLost(self, reason):
        if reason.check(ResponseDone):
            self.finished.callback(None)
        else:
            self.finished.errback(reason)



class Client(Client):
    def __init__(self, reactor, host, portNumber, agent):
        self._requestLocation = networkString('http://%s:%d/' % (host, portNumber,))
        self._agent = agent
        super(Client, self).__init__(reactor)


    def _request(self):
        d = self._agent.request(b'GET', self._requestLocation)
        d.addCallback(self._read)
        d.addCallback(self._continue)
        d.addErrback(self._stop)


    def _read(self, response):
        finished = Deferred()
        response.deliverBody(BodyConsumer(finished))
        return finished


class FakeServerProtocol(Protocol):

    def __init__(self):
        self._data = b""


    def dataReceived(self, data):
        self._data += data

        if self._data[-4:] == b"\r\n\r\n":
            self.transport.write(self.factory.response)

        self.transport.loseConnection()



interface = 0
def main(reactor, duration):
    global interface
    concurrency = 10

    protoFactory = Factory.forProtocol(FakeServerProtocol)
    protoFactory.response = b"\r\n".join(b"""HTTP/1.1 200 OK
Date: Sat, 31 Dec 2016 07:48:22 GMT
Connection: close
Content-Type: text/plain
Content-Length: 12
Server: FakeTwistedWeb

Hello, world""".split(b"\n"))

    interface += 1
    interface %= 255
    port = reactor.listenTCP(
        0, protoFactory, backlog=128, interface='127.0.0.%d' % (interface,))
    agent = Agent(reactor)
    client = Client(reactor, port.getHost().host, port.getHost().port, agent)
    d = client.run(concurrency, duration)
    def cleanup(passthrough):
        d = port.stopListening()
        d.addCallback(lambda ignored: passthrough)
        return d
    d.addBoth(cleanup)
    return d



if __name__ == '__main__':
    import sys
    import web_client
    driver(web_client.main, sys.argv)
